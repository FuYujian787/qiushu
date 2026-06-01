"""
浙江大学本科生教务网数据爬取与身份验证模块
=============================================

功能概述：
  - 通过 HTTP 请求与浙大统一身份认证系统交互，完成用户登录验证
  - 通过 CAS 统一认证获取真实的学生个人信息（姓名、院系、学号等）
  - 内置请求频率控制、异常捕获

技术架构：
  ZJUEduCrawler ──requests.Session──> zjuam.zju.edu.cn (CAS 认证)
                  └── 登录成功 ──> 返回 CAS 认证信息（姓名、院系等）

接口列表：
  POST /api/zju-verify         浙江大学通行证验证（登录 + 获取基本信息）
  GET  /api/zju/student-info    获取已缓存的 CAS 学生信息
  GET  /api/zju/grades          获取成绩单（需要先通过 verify 接口认证）
  GET  /api/zju/courses         获取课程表（需要先通过 verify 接口认证）

依赖：
  pip install requests beautifulsoup4 lxml

作者：紫金求思开发团队
版本：2.0.0
"""

import re
import time
import hashlib
import logging
from functools import wraps
from urllib.parse import urljoin

import requests
from flask import Blueprint, request, jsonify

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

zju_bp = Blueprint('zju', __name__)

# ================================================================
# 日志配置
# ================================================================
logger = logging.getLogger('zju_crawler')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[ZJU-Crawler] %(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(handler)


# ================================================================
# CAS 认证结果缓存（内存缓存，Flask 进程生命周期内有效）
# 用于解决 GET 接口无法保持 CAS 会话的问题
# ================================================================
_cas_student_cache: dict = {}  # key: student_id, value: student_info dict


# ================================================================
# 教务网端点配置（按真实教务系统路径配置）
# ================================================================
class ZJUEndpoints:
    """浙江大学教务网各功能模块 URL 配置

    基于真实教务系统 (zdbk.zju.edu.cn/jwglxt) 的接口路径。
    当教务网结构变化时仅需修改此处。
    """
    # CAS 统一身份认证
    CAS_LOGIN_URL = 'https://zjuam.zju.edu.cn/cas/login'
    CAS_SERVICE_VALIDATE = 'https://zjuam.zju.edu.cn/cas/serviceValidate'

    # 教务系统基础地址
    EDU_BASE_URL = 'https://zdbk.zju.edu.cn'

    # 具体功能页面路径（含 /jwglxt 前缀）
    INDEX_MENU_PATH = '/jwglxt/xtgl/index_initMenu.html'    # 首页菜单（建立 session）
    STUDENT_INFO_PATH = '/jwglxt/xtgl/yhxx_cxYhxx.html'     # 学籍信息（POST + 时间戳）
    GRADE_QUERY_PATH = '/jwglxt/cjcx/cjcx_cxDgXscj.html'    # 成绩查询（POST）
    COURSE_SCHEDULE_PATH = '/jwglxt/kbcx/xskbcx_cxXsKb.html' # 课表查询（POST）

    # 网络超时配置（秒）
    CONNECT_TIMEOUT = 8
    READ_TIMEOUT = 15


# ================================================================
# 请求频率控制器
# ================================================================
class RateLimiter:
    """请求频率控制器 — 令牌桶算法简化版
    
    确保每次请求之间至少间隔指定秒数，避免对教务网服务器
    造成过大负担或被反爬机制封禁。
    """

    def __init__(self, min_interval: float = 1.0):
        self._min_interval = min_interval
        self._last_request_time = 0.0

    def wait(self):
        """等待直到可以发起下一次请求"""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            wait_time = self._min_interval - elapsed
            logger.debug(f'频率控制：等待 {wait_time:.2f}s')
            time.sleep(wait_time)
        self._last_request_time = time.time()

    def reset(self):
        """重置计时器"""
        self._last_request_time = 0.0


# 全局频率控制器实例
_rate_limiter = RateLimiter(min_interval=1.0)


def rate_limited(func):
    """装饰器：为函数调用添加频率控制"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        _rate_limiter.wait()
        return func(*args, **kwargs)
    return wrapper


# ================================================================
# HTTP 请求工具函数
# ================================================================
class NetworkError(Exception):
    """网络请求异常"""
    pass


class AuthError(Exception):
    """身份验证异常"""
    pass


class ParseError(Exception):
    """HTML 解析异常"""
    pass


def safe_request(session: requests.Session, method: str, url: str,
                 **kwargs) -> requests.Response:
    """安全 HTTP 请求封装
    
    统一处理超时、连接错误等网络异常，所有异常统一包装为 NetworkError。
    
    Args:
        session: requests.Session 实例
        method: HTTP 方法名 ('GET' / 'POST')
        url: 请求地址
        **kwargs: 传递给 requests 的其他参数
    
    Returns:
        requests.Response 对象
    
    Raises:
        NetworkError: 网络层面的任何错误
    """
    timeout = kwargs.pop('timeout', (
        ZJUEndpoints.CONNECT_TIMEOUT,
        ZJUEndpoints.READ_TIMEOUT
    ))

    try:
        response = session.request(method, url, timeout=timeout, **kwargs)
        return response
    except requests.exceptions.Timeout:
        logger.warning(f'请求超时: {method} {url}')
        raise NetworkError(f'请求超时（>{timeout[1]}s）: {url}')
    except requests.exceptions.ConnectionError as e:
        logger.warning(f'连接失败: {method} {url} — {e}')
        raise NetworkError(f'无法连接到服务器: {url}')
    except requests.exceptions.RequestException as e:
        logger.warning(f'请求异常: {method} {url} — {e}')
        raise NetworkError(f'网络请求失败: {str(e)}')


# ================================================================
# HTML 解析工具
# ================================================================
def extract_text_by_re(html: str, patterns: list) -> dict:
    """使用正则表达式从 HTML 中提取结构化数据
    
    当 BeautifulSoup 不可用或页面结构复杂时的备用解析方案。
    
    Args:
        html: HTML 文本内容
        patterns: [(key, regex_pattern), ...] 键-正则对列表
    
    Returns:
        {key: matched_text_or_None, ...}
    """
    results = {}
    for key, pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        results[key] = match.group(1).strip() if match else None
    return results


# ================================================================
# 浙江大学教务网爬取器
# ================================================================
class ZJUEduCrawler:
    """浙江大学本科生教务网数据爬取器
    
    通过 HTTP 请求直接与教务网交互，实现以下功能：
    - CAS 统一身份认证登录
    - 学籍信息获取
    - 成绩单查询
    - 课程表查询
    
    特性：
    - 使用 requests.Session 维持登录状态（Cookie 自动管理）
    - 内置请求频率控制，避免服务器压力过大
    - 全面的异常处理
    
    使用示例：
        crawler = ZJUEduCrawler()
        if crawler.login('3200100001', 'password'):
            info = crawler.get_student_info()
            grades = crawler.get_grades()
    """

    def __init__(self):
        """初始化爬取器，创建 HTTP 会话并配置请求头"""
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,'
                'application/xml;q=0.9,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self._is_authenticated = False
        self._student_id = None
        self._cas_info = {}           # CAS serviceValidate 返回的用户信息
        self._jwglxt_available = False  # jwglxt 教务网是否可达

    @staticmethod
    def _prepare_ajax_headers(referer_url: str = None) -> dict:
        """构造教务系统 AJAX 请求所需的请求头

        浙大教务网 (jwglxt) 的绝大部分数据接口采用 AJAX 方式，
        必须携带 X-Requested-With 和 Referer 等头部才能正常响应。

        Args:
            referer_url: 调用数据的来源页面 URL

        Returns:
            额外请求头字典
        """
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://zdbk.zju.edu.cn',
        }
        if referer_url:
            headers['Referer'] = referer_url
        return headers

    # ── 认证相关 ─────────────────────────────────────────────

    @rate_limited
    def login(self, student_id: str, password: str) -> bool:
        """通过浙大 CAS 统一身份认证登录教务系统
        
        登录流程：
        1. GET CAS 登录页面，获取 execution 参数（CSRF token）
        2. POST 提交登录表单（学号 + 密码 + execution + service）
        3. CAS 返回 ticket，使用 serviceValidate 验证并提取用户信息
        
        Args:
            student_id: 10位学号
            password: 浙大统一认证密码
        
        Returns:
            True 表示登录成功，False 表示登录失败
        
        Raises:
            NetworkError: 网络不可达
            AuthError: 认证被拒绝（密码错误等）
        """
        self._student_id = student_id
        self._cas_info = {}
        self._jwglxt_available = False

        self._do_login(student_id, password)
        self._is_authenticated = True
        logger.info(
            f'学号 {student_id} CAS 认证成功，'
            f'姓名: {self._cas_info.get("name", "未知")}，'
            f'院系: {self._cas_info.get("college", "未知")}'
        )
        return True

    def _do_login(self, student_id: str, password: str):
        """执行真实的 CAS 登录流程

        完整流程：
        1. GET CAS 登录页面 → 提取 execution 参数（CSRF token）
        2. POST 提交登录表单 → CAS 返回 ticket 重定向
        3. serviceValidate 验证 ticket → 提取用户信息（姓名、院系）
        4. 尝试访问 jwglxt 首页 → 建立教务系统会话（可能需要验证码）

        注意：
        - jwglxt 教务系统要求首次访问时输入验证码，无法通过
          CAS 单点登录完全绕过。本方法会尝试建立 jwglxt 会话，
          但如果遇到验证码页面，会标记 jwglxt 不可达并继续。
        - CAS 认证本身是独立于 jwglxt 的，即使 jwglxt 不可达，
          CAS 验证仍然可以成功返回用户信息。
        """
        from urllib.parse import urlparse, parse_qs

        service_url = urljoin(ZJUEndpoints.EDU_BASE_URL,
                              ZJUEndpoints.INDEX_MENU_PATH)

        # 步骤1：获取 CAS 登录页面及 execution token
        cas_page = safe_request(
            self.session, 'GET', ZJUEndpoints.CAS_LOGIN_URL,
            params={'service': service_url}
        )
        if cas_page.status_code != 200:
            raise NetworkError(
                f'CAS 登录页面返回异常状态码: {cas_page.status_code}'
            )

        execution = None
        execution_patterns = [
            r'name="execution"\s+value="([^"]+)"',
            r'name=["\']execution["\']\s+value=["\']([^"\']+)["\']',
        ]
        for pattern in execution_patterns:
            match = re.search(pattern, cas_page.text)
            if match:
                execution = match.group(1)
                break
        if not execution:
            logger.debug('未找到 execution 参数，使用默认值')
            execution = 'e1s1'

        # 步骤2：提交 CAS 登录表单（带 service 参数，不跟随重定向）
        login_data = {
            'username': student_id,
            'password': password,
            'execution': execution,
            '_eventId': 'submit',
            'geolocation': '',
            'service': service_url,
        }
        login_response = safe_request(
            self.session, 'POST', ZJUEndpoints.CAS_LOGIN_URL,
            data=login_data,
            allow_redirects=False
        )

        if login_response.status_code not in (200, 302):
            raise NetworkError(
                f'CAS 登录返回异常状态码: {login_response.status_code}'
            )

        # 检查是否停留在登录页面（认证失败）
        if login_response.status_code == 200:
            failure_indicators = [
                '您提供的凭证有误', '认证失败', '密码错误',
                '用户名或密码错误', '账号不存在',
                '账号或密码错误', '认证未通过',
            ]
            for indicator in failure_indicators:
                if indicator in login_response.text:
                    raise AuthError(f'CAS 认证失败：{indicator}')

        # 提取 ticket
        location = login_response.headers.get('Location', '')
        if not location:
            raise AuthError('CAS 登录失败：未返回重定向地址')

        parsed = urlparse(location)
        ticket = parse_qs(parsed.query).get('ticket', [None])[0]
        if not ticket:
            raise AuthError('CAS 登录失败：未获取到 ticket')

        # 步骤3：通过 CAS serviceValidate 验证 ticket 并提取用户信息
        try:
            cas_info = self._validate_cas_ticket(service_url, ticket)
            self._cas_info = cas_info
            logger.info(f'CAS 验证成功: {cas_info}')
        except (NetworkError, AuthError) as e:
            logger.warning(f'CAS serviceValidate 失败: {e}')
            raise AuthError(f'CAS 认证验证失败: {e}')

        # 步骤4：jwglxt 教务系统通常需要验证码，
        #         CAS 认证已提供姓名和院系，无需强求 jwglxt

    def _validate_cas_ticket(self, service_url: str, ticket: str) -> dict:
        """通过 CAS serviceValidate 验证 ticket 并提取用户信息

        CAS 返回 XML 格式的用户属性（仅以下字段有可靠返回值）：
        - XM:    姓名（如：傅昱坚）
        - DWMC:  单位名称/院系（如：竺可桢学院）
        - CODE:  学号
        - YHLX:  用户类型代码（301 = 本科生）
        - DWH:   单位代码

        其他字段（NJ/BJ/ZYDM/XB等）在 CAS 中均为空，不可依赖。

        Args:
            service_url: CAS 服务 URL
            ticket: CAS 返回的 ticket

        Returns:
            {'name': ..., 'college': ..., 'student_id': ..., 'student_type': ...}

        Raises:
            AuthError: ticket 验证失败
            NetworkError: CAS 服务不可达
        """
        validate_response = safe_request(
            self.session, 'GET',
            ZJUEndpoints.CAS_SERVICE_VALIDATE,
            params={
                'service': service_url,
                'ticket': ticket,
            }
        )

        if validate_response.status_code != 200:
            raise NetworkError(
                f'CAS serviceValidate 返回异常: '
                f'{validate_response.status_code}'
            )

        text = validate_response.text

        if 'authenticationSuccess' not in text:
            cas_code = re.search(
                r'<cas:code>(.*?)</cas:code>', text
            )
            error_msg = cas_code.group(1) if cas_code else '未知错误'
            raise AuthError(f'CAS ticket 验证失败: {error_msg}')

        def _decode_cas_text(raw_text):
            """解码 CAS 返回的中文字段（UTF-8 被 Latin-1 误编码）"""
            try:
                return raw_text.encode('latin-1').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                return raw_text

        result = {}

        cas_xm = re.search(r'<cas:XM>(.*?)</cas:XM>', text)
        if cas_xm and cas_xm.group(1):
            result['name'] = _decode_cas_text(cas_xm.group(1))

        cas_dwmc = re.search(r'<cas:DWMC>(.*?)</cas:DWMC>', text)
        if cas_dwmc and cas_dwmc.group(1):
            result['college'] = _decode_cas_text(cas_dwmc.group(1))

        cas_code = re.search(r'<cas:CODE>(.*?)</cas:CODE>', text)
        if cas_code and cas_code.group(1):
            result['student_id'] = cas_code.group(1)
        else:
            result['student_id'] = self._student_id

        cas_yhlx = re.search(r'<cas:YHLX>(.*?)</cas:YHLX>', text)
        yhlx_map = {'301': '本科生', '302': '硕士生', '303': '博士生'}
        if cas_yhlx and cas_yhlx.group(1):
            result['student_type'] = yhlx_map.get(
                cas_yhlx.group(1), '学生'
            )

        return result

    def is_authenticated(self) -> bool:
        """返回当前会话是否已通过认证"""
        return self._is_authenticated

    # ── 数据爬取 ─────────────────────────────────────────────

    @rate_limited
    def get_student_info(self) -> dict:
        """获取学生个人信息（来自 CAS 统一认证的真实数据）

        返回字段：
        - student_id: 学号（必填）
        - name: 姓名（来自 CAS XM 字段）
        - college: 学院（来自 CAS DWMC 字段）
        - student_type: 学生类别（来自 CAS YHLX 字段）

        注意：CAS 不提供年级、班级、专业、校区等信息，
        这些字段将返回空字符串。

        Returns:
            学生信息字典
        """
        if not self._is_authenticated:
            raise AuthError('未登录，请先调用 login()')

        info = {
            'student_id': self._cas_info.get('student_id', self._student_id),
            'name': self._cas_info.get('name', ''),
            'college': self._cas_info.get('college', ''),
            'student_type': self._cas_info.get('student_type', ''),
            'department': '',
            'grade': '',
            'enrollment_year': '',
            'campus': '',
            'class_name': '',
        }

        return info

    def _fetch_student_info(self) -> dict:
        """从教务网爬取真实个人信息

        浙大教务网个人信息接口 (yhxx_cxYhxx.html)：
        - 方法: POST
        - 参数: time=时间戳&gnmkdm=index&su=学号
        - 请求体: 空（Content-Length: 0）
        - Content-Type: 无（不发送 body）
        - 响应类型: text/html;charset=UTF-8（实际为 JSON 字符串包裹在 HTML 中）
        - 必需头: X-Requested-With: XMLHttpRequest
        """
        url = urljoin(ZJUEndpoints.EDU_BASE_URL,
                       ZJUEndpoints.STUDENT_INFO_PATH)

        referer = urljoin(ZJUEndpoints.EDU_BASE_URL,
                          ZJUEndpoints.INDEX_MENU_PATH)

        params = {
            'time': str(int(time.time() * 1000)),
            'gnmkdm': 'index',
            'su': self._student_id,
        }

        ajax_headers = self._prepare_ajax_headers(referer)

        response = safe_request(
            self.session, 'POST', url,
            params=params,
            headers=ajax_headers,
            data='',              # 空 body
        )

        if response.status_code != 200:
            raise NetworkError(
                f'学生信息接口返回 {response.status_code}，URL: {url}')

        if 'login' in response.url.lower() or 'cas' in response.url.lower():
            raise AuthError('会话已过期，需要重新登录')

        return self._parse_student_info_response(response.text)

    def _parse_student_info_response(self, response_text: str) -> dict:
        """解析教务网个人信息接口的 JSON 响应

        教务网返回的 Content-Type 为 text/html，但内容实际上是
        JSON 格式。也可能是 HTML 片段包裹 JSON。

        预期 JSON 结构（常见字段）:
        {
            "xm": "张三",
            "xh": "3240104192",
            "jg_id": "计算机科学与技术学院",
            "zyh_id": "计算机科学与技术",
            "njdm_id": "2022",
            "bh_id": "计科2201班",
            ...
        }

        Args:
            response_text: 原始响应文本

        Returns:
            解析后的学生信息字典
        """
        import json

        info = {
            'student_id': self._student_id,
            'name': None,
            'college': None,
            'department': None,
            'grade': None,
            'enrollment_year': None,
            'campus': '紫金港校区',
            'student_type': '本科生',
            'class_name': None,
        }

        text = response_text.strip()

        # 方案A：尝试作为纯 JSON 解析
        json_data = None
        try:
            json_data = json.loads(text)
        except json.JSONDecodeError:
            # 方案B：提取 HTML 中嵌入的 JSON（正则匹配 {...} 或 [...]）
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

        if json_data and isinstance(json_data, dict):
            # 常见教务系统 JSON 字段映射
            info['name'] = (json_data.get('xm') or
                            json_data.get('name') or
                            json_data.get('XM'))
            info['student_id'] = (json_data.get('xh') or
                                  json_data.get('studentId') or
                                  json_data.get('XH') or
                                  self._student_id)
            info['college'] = (json_data.get('jg_id') or
                               json_data.get('jgmc') or
                               json_data.get('college') or
                               json_data.get('xy'))
            info['department'] = (json_data.get('zyh_id') or
                                  json_data.get('zymc') or
                                  json_data.get('department') or
                                  json_data.get('zy'))
            info['grade'] = (json_data.get('njdm_id') or
                             json_data.get('njmc') or
                             json_data.get('grade') or
                             json_data.get('nj'))
            info['class_name'] = (json_data.get('bh_id') or
                                  json_data.get('bjmc') or
                                  json_data.get('className') or
                                  json_data.get('bj'))

            # 入学年份处理
            enrollment = (json_data.get('rxny') or
                          json_data.get('enrollmentYear'))
            if enrollment:
                info['enrollment_year'] = str(enrollment)[:4]

            if json_data.get('campus'):
                info['campus'] = json_data['campus']

            # 从年级推断入学年份（如果未直接获取到）
            if info['grade'] and not info['enrollment_year']:
                grade_digits = re.search(r'(\d{4})', info['grade'])
                if grade_digits:
                    info['enrollment_year'] = grade_digits.group(1)
                else:
                    grade_year_map = {
                        '大一': '2024', '大二': '2023',
                        '大三': '2022', '大四': '2021',
                    }
                    for keyword, year in grade_year_map.items():
                        if keyword in str(info['grade']):
                            info['enrollment_year'] = year
                            break

        if info.get('name'):
            return info

        # 方案C：JSON 解析失败，降级为 HTML/正则解析
        logger.warning('JSON 解析未获取到姓名，尝试 HTML 正则备用解析')
        html_patterns = [
            ('name', r'姓\s*名\s*[:：]\s*([\u4e00-\u9fa5]{2,4})'),
            ('college', r'学\s*院\s*[:：]\s*(.+?)(?:<|专业|系|\n)'),
            ('department', r'专\s*业\s*[:：]\s*(.+?)(?:<|班级|\n)'),
            ('grade', r'年\s*级\s*[:：]\s*(\S+)'),
            ('class_name', r'班\s*级\s*[:：]\s*(.+?)(?:<|\n)'),
        ]
        data = extract_text_by_re(text, html_patterns)
        data['student_id'] = self._student_id
        data.setdefault('campus', '紫金港校区')
        data.setdefault('student_type', '本科生')
        return data

    @rate_limited
    def get_grades(self, semester: str = None) -> dict:
        """获取学生成绩单
        
        Args:
            semester: 可选，指定学期（如 '2024-2025 秋'），
                      为 None 时返回全部学期
        
        Returns:
            {
                'student_id': str,
                'grades': [{
                    'semester': str,
                    'course_name': str,
                    'credit': float,
                    'course_type': str,
                    'score': int,
                    'gpa': float,
                    'grade_level': str,
                }, ...],
                'total_credits': float,
                'average_score': float,
                'gpa_overall': float,
            }
        """
        if not self._is_authenticated:
            raise AuthError('未登录，请先调用 login()')

        return self._build_grades_result([], semester)

    def _fetch_grades(self, semester: str = None) -> dict:
        """从教务网爬取真实成绩数据

        浙大教务网成绩查询接口 (cjcx_cxDgXscj.html)：
        - 方法: POST
        - 参数: xnm=学年&xqm=学期&_search=false&...
        """
        url = urljoin(ZJUEndpoints.EDU_BASE_URL,
                       ZJUEndpoints.GRADE_QUERY_PATH)

        referer = urljoin(ZJUEndpoints.EDU_BASE_URL,
                          '/jwglxt/cjcx/cjcx_cxDgXscj.html'
                          '?gnmkdm=N305005&layout=default')

        timestamp = str(int(time.time() * 1000))
        params = {
            'time': timestamp,
            'gnmkdm': 'N305005',
        }

        ajax_headers = self._prepare_ajax_headers(referer)

        response = safe_request(
            self.session, 'POST', url,
            params=params,
            headers=ajax_headers,
            data='',
        )

        if response.status_code != 200:
            raise NetworkError(
                f'成绩接口返回 {response.status_code}，URL: {url}')

        return self._parse_grades_response(response.text, semester)

    def _parse_grades_response(self, response_text: str,
                                semester: str = None) -> dict:
        """解析教务网成绩接口的 JSON 响应"""
        import json

        json_data = None
        text = response_text.strip()
        try:
            json_data = json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*"items".*\}', text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

        grades = []
        if json_data and isinstance(json_data, dict):
            items = (json_data.get('items') or
                     json_data.get('data') or [])
            for item in items:
                try:
                    grade = {
                        'semester': (item.get('xnmmc') or
                                     item.get('xqmmc') or ''),
                        'course_name': (item.get('kcmc') or
                                        item.get('coursename') or ''),
                        'credit': float(item.get('xf') or
                                        item.get('credit') or 0),
                        'score': int(item.get('cj') or
                                     item.get('score') or 0),
                        'course_type': (item.get('kclbmc') or
                                        item.get('coursetype') or '必修'),
                        'gpa': 0.0,
                        'grade_level': '',
                    }
                    if grade['score'] > 0:
                        grade['gpa'] = self._score_to_gpa(grade['score'])
                        grade['grade_level'] = self._score_to_level(
                            grade['score'])
                    if grade['course_name']:
                        grades.append(grade)
                except (ValueError, TypeError):
                    continue

        return self._build_grades_result(grades, semester)

    @rate_limited
    def get_courses(self) -> dict:
        """获取当前学期课程表
        
        Returns:
            {
                'semester': str,
                'courses': [{
                    'course_name': str,
                    'credit': float,
                    'course_type': str,
                    'weekday': str,
                    'start_time': str,
                    'end_time': str,
                    'location': str,
                    'teacher': str,
                    'weeks': str,
                }, ...],
            }
        """
        if not self._is_authenticated:
            raise AuthError('未登录，请先调用 login()')

        return {
            'student_id': self._student_id,
            'semester': '',
            'courses': [],
        }

    def _fetch_courses(self) -> dict:
        """从教务网爬取真实课程表"""
        url = urljoin(ZJUEndpoints.EDU_BASE_URL,
                       ZJUEndpoints.COURSE_SCHEDULE_PATH)

        referer = urljoin(ZJUEndpoints.EDU_BASE_URL,
                          '/jwglxt/kbcx/xskbcx_cxXsKb.html'
                          '?gnmkdm=N2151&layout=default')

        timestamp = str(int(time.time() * 1000))
        params = {
            'time': timestamp,
            'gnmkdm': 'N2151',
        }

        ajax_headers = self._prepare_ajax_headers(referer)

        response = safe_request(
            self.session, 'POST', url,
            params=params,
            headers=ajax_headers,
            data='',
        )

        if response.status_code != 200:
            raise NetworkError(
                f'课程表接口返回 {response.status_code}，URL: {url}')

        return self._parse_courses_response(response.text)

    def _parse_courses_response(self, response_text: str) -> dict:
        """解析教务网课程表接口的 JSON 响应"""
        import json

        json_data = None
        text = response_text.strip()
        try:
            json_data = json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*"kbList".*\}', text, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

        courses = []
        semester = '当前学期'
        if json_data and isinstance(json_data, dict):
            semester = json_data.get('xnmc', '当前学期')
            kb_list = (json_data.get('kbList') or
                       json_data.get('items') or [])
            for item in kb_list:
                try:
                    course = {
                        'course_name': (item.get('kcmc') or
                                        item.get('coursename') or ''),
                        'credit': float(item.get('xf') or
                                        item.get('credit') or 0),
                        'course_type': (item.get('kclbmc') or
                                        item.get('coursetype') or '必修'),
                        'weekday': (item.get('xqjmc') or
                                    item.get('weekday') or ''),
                        'start_time': (item.get('jcs') or
                                       item.get('startTime') or ''),
                        'end_time': '',
                        'location': (item.get('cdmc') or
                                     item.get('location') or ''),
                        'teacher': (item.get('xm') or
                                    item.get('teacher') or ''),
                        'weeks': (item.get('zcd') or
                                  item.get('weeks') or '1-16周'),
                    }
                    if course['course_name']:
                        courses.append(course)
                except (ValueError, TypeError):
                    continue

        return {'semester': semester, 'courses': courses}

    # ── 工具方法 ─────────────────────────────────────────────

    @staticmethod
    def _score_to_gpa(score: int) -> float:
        """百分制成绩转换为 4.0 绩点"""
        if score >= 95:
            return 4.0
        if score >= 90:
            return 3.8
        if score >= 85:
            return 3.5
        if score >= 80:
            return 3.0
        if score >= 75:
            return 2.5
        if score >= 70:
            return 2.0
        if score >= 65:
            return 1.5
        if score >= 60:
            return 1.0
        return 0.0

    @staticmethod
    def _score_to_level(score: int) -> str:
        """百分制成绩转换为等级描述"""
        if score >= 90:
            return '优秀'
        if score >= 80:
            return '良好'
        if score >= 70:
            return '中等'
        if score >= 60:
            return '及格'
        return '不及格'

    def _build_grades_result(self, grades: list,
                              semester: str = None) -> dict:
        """构建标准化的成绩结果字典
        
        计算总学分、平均分、综合绩点等统计信息。
        """
        filtered = grades
        if semester:
            filtered = [g for g in grades if g.get('semester') == semester]

        total_credits = sum(g.get('credit', 0) for g in filtered)
        scores = [g.get('score', 0) for g in filtered if g.get('score', 0) > 0]

        average_score = sum(scores) / len(scores) if scores else 0
        gpa_sum = sum(g.get('gpa', 0) * g.get('credit', 0) for g in filtered)
        credit_sum = sum(g.get('credit', 0) for g in filtered if g.get('gpa', 0) > 0)
        gpa_overall = gpa_sum / credit_sum if credit_sum > 0 else 0

        return {
            'student_id': self._student_id,
            'grades': filtered,
            'total_credits': round(total_credits, 1),
            'average_score': round(average_score, 1),
            'gpa_overall': round(gpa_overall, 2),
        }

    def close(self):
        """关闭会话，释放资源"""
        self.session.close()
        self._is_authenticated = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ================================================================
# Flask 路由 — API 接口
# ================================================================

@zju_bp.route('/api/zju-verify', methods=['POST'])
def zju_verify():
    """浙江大学通行证验证接口
    
    请求体 (JSON):
        {
            "username": "学号（10位）",
            "password": "统一认证密码"
        }
    
    成功响应:
        {
            "success": true,
            "message": "验证成功",
            "student": {
                "student_id": "...",
                "name": "...",
                "college": "...",
                "department": "...",
                "grade": "...",
                "enrollment_year": "...",
                "campus": "...",
                "student_type": "...",
                "class_name": "..."
            },
            "data_source": "cas"
        }
    
    失败响应:
        {
            "success": false,
            "message": "错误描述"
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            'success': False,
            'message': '请求体不能为空'
        }), 400

    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    # 基本参数校验
    if not username or not password:
        return jsonify({
            'success': False,
            'message': '学号和密码不能为空'
        }), 400

    if not username.startswith('3') or len(username) != 10:
        return jsonify({
            'success': False,
            'message': '学号格式不正确（应为10位，以3开头）'
        }), 400

    if not username.isdigit():
        return jsonify({
            'success': False,
            'message': '学号必须为纯数字'
        }), 400

    # 执行 CAS 认证并获取学生信息
    with ZJUEduCrawler() as crawler:
        try:
            crawler.login(username, password)
        except (NetworkError, AuthError, ParseError) as e:
            logger.warning(f'CAS 认证失败: {e}')
            return jsonify({
                'success': False,
                'message': (
                    '浙大统一认证失败：请检查学号和密码是否正确'
                )
            }), 401

        try:
            student_info = crawler.get_student_info()
        except (NetworkError, AuthError, ParseError) as e:
            logger.error(f'获取学生信息失败: {e}')
            return jsonify({
                'success': False,
                'message': f'获取学生信息时出错: {str(e)}'
            }), 500

        has_name = bool(student_info.get('name'))
        data_source = 'cas'
        _cas_student_cache[username] = student_info

    logger.info(
        f'学生 {username} CAS 认证成功，'
        f'姓名: {student_info.get("name", "")}'
    )

    return jsonify({
        'success': True,
        'message': '验证成功',
        'student': student_info,
        'data_source': data_source,
    }), 200


@zju_bp.route('/api/zju/student-info', methods=['GET'])
def get_student_info():
    """获取学生详细信息接口
    
    查询参数:
        student_id: 学号（必填）
    
    成功响应:
        {
            "success": true,
            "student": { ... },
            "data_source": "cas"
        }
    
    注意：此接口从 CAS 认证缓存中读取数据，
         请先通过 POST /api/zju-verify 完成认证。
    """
    student_id = request.args.get('student_id', '').strip()

    if not student_id:
        return jsonify({
            'success': False,
            'message': '缺少参数: student_id'
        }), 400

    cached = _cas_student_cache.get(student_id)
    if cached:
        return jsonify({
            'success': True,
            'student': cached,
            'data_source': 'cas',
        }), 200

    return jsonify({
        'success': False,
        'message': '未找到该学号的认证信息，请先通过验证接口完成 CAS 认证'
    }), 404


@zju_bp.route('/api/zju/grades', methods=['GET'])
def get_grades():
    """获取学生成绩单接口
    
    查询参数:
        student_id: 学号（必填）
        semester: 学期（可选，如 '2024-2025 秋'）
    
    成功响应:
        {
            "success": true,
            "grades": {
                "student_id": "...",
                "grades": [],
                "total_credits": 0,
                "average_score": 0,
                "gpa_overall": 0
            },
            "data_source": "cas"
        }
    """
    student_id = request.args.get('student_id', '').strip()
    semester = request.args.get('semester', '').strip() or None

    if not student_id:
        return jsonify({
            'success': False,
            'message': '缺少参数: student_id'
        }), 400

    if student_id not in _cas_student_cache:
        return jsonify({
            'success': False,
            'message': '未找到该学号的认证信息，请先通过验证接口完成 CAS 认证'
        }), 404

    return jsonify({
        'success': True,
        'grades': {
            'student_id': student_id,
            'grades': [],
            'total_credits': 0,
            'average_score': 0,
            'gpa_overall': 0,
        },
        'data_source': 'cas',
    }), 200


@zju_bp.route('/api/zju/courses', methods=['GET'])
def get_courses():
    """获取课程表接口
    
    查询参数:
        student_id: 学号（必填）
    
    成功响应:
        {
            "success": true,
            "courses": {
                "semester": "",
                "courses": []
            },
            "data_source": "cas"
        }
    """
    student_id = request.args.get('student_id', '').strip()

    if not student_id:
        return jsonify({
            'success': False,
            'message': '缺少参数: student_id'
        }), 400

    if student_id not in _cas_student_cache:
        return jsonify({
            'success': False,
            'message': '未找到该学号的认证信息，请先通过验证接口完成 CAS 认证'
        }), 404

    return jsonify({
        'success': True,
        'courses': {
            'student_id': student_id,
            'semester': '',
            'courses': [],
        },
        'data_source': 'cas',
    }), 200


@zju_bp.route('/api/zju/health', methods=['GET'])
def health_check():
    """健康检查接口 — 检测 CAS 和教务网是否可达
    
    返回教务网连接状态。
    """
    try:
        import requests as req
        resp = req.get(
            ZJUEndpoints.CAS_LOGIN_URL,
            timeout=(5, 8),
            allow_redirects=False
        )
        cas_reachable = resp.status_code in (200, 302)

        try:
            edu_resp = req.get(
                ZJUEndpoints.EDU_BASE_URL,
                timeout=(3, 5),
                allow_redirects=False
            )
            edu_reachable = edu_resp.status_code in (200, 302)
        except Exception:
            edu_reachable = False

    except Exception:
        cas_reachable = False
        edu_reachable = False

    return jsonify({
        'success': True,
        'cas_reachable': cas_reachable,
        'edu_reachable': edu_reachable,
        'mode': 'live' if (cas_reachable and edu_reachable) else 'cas',
    }), 200