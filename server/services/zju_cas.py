"""浙大通行证 CAS SSO 认证客户端 (v2.0 - 2026-06-13 重写)

基于实际 API 探测结果重写，使用已验证可用的端点。

CAS 认证流程:
1. GET /cas/login → 提取 execution token + JSESSIONID
2. GET /cas/v2/getPubKey → 获取 RSA 公钥 (modulus, exponent) + _pv0 cookie
3. RSA 加密密码（无 padding，密码→UTF-8→hex→int→pow(m,e,n)→hex）
4. POST /cas/login → 获取 iPlanetDirectoryPro SSO Cookie

数据获取 (CAS 认证后):
5. courses.zju.edu.cn/api/profile → 学生信息 (name, user_no, department, org, program, grade, klass, email)
6. courses.zju.edu.cn/api/todos → 课程列表 (course_name, course_code, course_id)
7. zdbk 课表 API → 学籍信息补充 (xh, xm, xy, zy, xzb)

参考:
- Celechron: https://github.com/Celechron/Celechron (Dart, GPL-3.0)
- login-ZJU: https://github.com/5dbwat4/login-ZJU (TypeScript, MIT)
- 诊断脚本: server/test_cas_diagnostic.py
"""
import re
import ssl
import logging
import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib.parse import unquote

logger = logging.getLogger(__name__)

# 确保 CAS 模块日志始终可见
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S',
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False


class _EduTLSSAdapter(HTTPAdapter):
    """自定义 TLS 适配器，兼容浙大老旧服务器的弱 DH 密钥（DH_KEY_TOO_SMALL）"""

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


class ZjuCASClient:
    """ZJU CAS 认证客户端

    用法:
        client = ZjuCASClient()
        client.login('学号', '密码')
        student_info = client.get_student_info()   # 姓名/学号/学院/专业/班级/邮箱
        courses = client.get_course_data()          # 课程列表
    """

    CAS_LOGIN_URL = 'https://zjuam.zju.edu.cn/cas/login'
    CAS_PUBKEY_URL = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'

    # 已验证可用的数据源
    COURSES_PROFILE_URL = 'https://courses.zju.edu.cn/api/profile'       # 学生个人信息
    COURSES_TODOS_URL = 'https://courses.zju.edu.cn/api/todos'           # 课程列表
    ZDBK_SCHEDULE_URL = 'https://zdbk.zju.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html'  # 课表+学籍

    def __init__(self):
        self.session = requests.Session()
        # 模拟浏览器，避免被 CAS 防火墙拦截
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        })
        # 挂载 TLS 适配器
        self.session.mount('https://', _EduTLSSAdapter())
        self.sso_cookie = None       # iPlanetDirectoryPro (原始 URL 编码值)
        self.sso_cookie_raw = None   # iPlanetDirectoryPro (解码后)
        self.jsessionid = None       # ZDBK JSESSIONID
        self.route = ''              # ZDBK route cookie

    # ── CAS 登录 ──────────────────────────────────────────

    def login(self, student_id: str, password: str) -> dict:
        """CAS 认证：学号+密码 → SSO Cookie

        返回: {'student_id': str, 'sso_token': str}
        异常: ValueError — AUTH_INVALID_CREDENTIALS / AUTH_CAS_CAPTCHA /
                           AUTH_CAS_LOCKED / CAS_AUTH_UNAVAILABLE
        """
        try:
            # Step 1: 获取 execution token + JSESSIONID
            logger.info('CAS Step 1: GET %s', self.CAS_LOGIN_URL)
            resp = self.session.get(
                self.CAS_LOGIN_URL,
                allow_redirects=False,
                timeout=15,
            )

            if resp.status_code >= 500:
                logger.error('CAS 登录页面返回 HTTP %s', resp.status_code)
                raise ValueError('CAS_AUTH_UNAVAILABLE')

            match = re.search(r'name="execution" value="(.*?)"', resp.text)
            if not match:
                snippet = (resp.text or '')[:300]
                logger.error('无法提取 execution token，响应片段: %s', snippet)
                raise ValueError('CAS_AUTH_UNAVAILABLE')
            execution = match.group(1)
            logger.debug('CAS execution token: %s...', execution[:30])

            # Step 2: 获取 RSA 公钥
            logger.info('CAS Step 2: GET %s', self.CAS_PUBKEY_URL)
            resp = self.session.get(self.CAS_PUBKEY_URL, timeout=15)

            if resp.status_code != 200:
                logger.error('获取公钥失败 HTTP %s', resp.status_code)
                raise ValueError('CAS_AUTH_UNAVAILABLE')

            pubkey_data = resp.json()
            modulus_hex = pubkey_data['modulus']
            exponent_hex = pubkey_data['exponent']
            modulus = int(modulus_hex, 16)
            exponent = int(exponent_hex, 16)
            logger.debug('RSA modulus: %d hex chars, exponent: %s', len(modulus_hex), exponent_hex)

            # Step 3: RSA 加密密码
            encrypted_pwd = self._rsa_encrypt(password, modulus, exponent, len(modulus_hex))

            # Step 4: 提交登录
            logger.info('CAS Step 4: POST %s', self.CAS_LOGIN_URL)
            resp = self.session.post(
                self.CAS_LOGIN_URL,
                data={
                    'username': student_id,
                    'password': encrypted_pwd,
                    'authcode': '',          # 验证码字段（无验证码时为空，但必须存在）
                    'execution': execution,
                    '_eventId': 'submit',
                    'rememberMe': 'true',
                },
                headers={'Referer': self.CAS_LOGIN_URL},
                allow_redirects=False,
                timeout=15,
            )

            # 检查 SSO Cookie
            sso_cookie = resp.cookies.get('iPlanetDirectoryPro')
            if not sso_cookie:
                resp_text = resp.text or ''
                if '密码错误' in resp_text or '账号或密码错误' in resp_text:
                    raise ValueError('AUTH_INVALID_CREDENTIALS')
                if '验证码' in resp_text or 'captcha' in resp_text.lower():
                    logger.warning('CAS 要求验证码')
                    raise ValueError('AUTH_CAS_CAPTCHA')
                if '锁定' in resp_text or 'locked' in resp_text.lower():
                    logger.warning('CAS 账号已锁定')
                    raise ValueError('AUTH_CAS_LOCKED')
                logger.error(
                    'CAS 登录失败: HTTP %s, Location=%s, 响应片段: %s',
                    resp.status_code,
                    resp.headers.get('Location', '无'),
                    resp_text[:300],
                )
                raise ValueError('AUTH_INVALID_CREDENTIALS')

            self.sso_cookie = sso_cookie
            self.sso_cookie_raw = unquote(sso_cookie)  # 解码 URL 编码
            logger.info('CAS 登录成功: student_id=%s', student_id)

            # 分发 SSO Cookie 到同级子域名
            for domain in ['zdbk.zju.edu.cn', 'courses.zju.edu.cn', 'zju.edu.cn']:
                self.session.cookies.set(
                    'iPlanetDirectoryPro', self.sso_cookie_raw,
                    domain=domain, path='/',
                )

            return {'student_id': student_id, 'sso_token': sso_cookie}

        except requests.RequestException as e:
            logger.error('CAS 网络请求异常: %s', e)
            raise ValueError('CAS_AUTH_UNAVAILABLE')

    # ── 学生信息获取 ──────────────────────────────────────

    def get_student_info(self) -> dict:
        """获取学生完整信息

        数据源优先级（重要）:
        1. ZDBK 课表 API → 学籍信息 (xh, xm, xy, zy, xzb) — 数据最完整
        2. courses.zju.edu.cn/api/profile → 补充信息 (email, phone, name)

        返回:
            {
                'student_id': str,  # 学号
                'name': str,        # 姓名
                'college': str,     # 学院
                'major': str,       # 专业
                'grade': str,       # 年级
                'klass': str,       # 班级
                'email': str,       # 邮箱
                'phone': str,       # 手机号
            }
            未获取到的字段为空字符串。
        """
        if not self.sso_cookie:
            logger.warning('无 SSO Cookie，无法获取学生信息')
            return {}

        info = {}

        # —— 方案 1: ZDBK 课表 API（学籍信息最完整：学院/专业/班级）——
        logger.info('获取学生信息: ZDBK 课表 API')
        try:
            zdbk_info = self._fetch_zdbk_schedule_info()
            if zdbk_info:
                info.update(zdbk_info)
                logger.info('ZDBK: xh=%s, xm=%s, xy=%s, zy=%s, xzb=%s',
                            zdbk_info.get('student_id'), zdbk_info.get('name'),
                            zdbk_info.get('college'), zdbk_info.get('major'),
                            zdbk_info.get('klass'))
        except Exception as e:
            logger.warning('ZDBK 课表 API 失败: %s', e)

        # —— 方案 2: courses.zju.edu.cn/api/profile（补充邮箱/手机）——
        logger.info('获取学生信息: courses profile（补充）')
        try:
            courses_info = self._fetch_courses_profile()
            if courses_info:
                # 仅补充 ZDBK 没有的字段
                for key in ['email', 'phone']:
                    if courses_info.get(key) and not info.get(key):
                        info[key] = courses_info[key]
                # 如果 ZDBK 未返回姓名/学号，用 courses 补充
                if not info.get('name') and courses_info.get('name'):
                    info['name'] = courses_info['name']
                if not info.get('student_id') and courses_info.get('student_id'):
                    info['student_id'] = courses_info['student_id']
                logger.info('courses profile 补充: email=%s, phone=%s',
                            courses_info.get('email'), courses_info.get('phone'))
        except Exception as e:
            logger.warning('courses profile 获取失败: %s', e)

        # 确保所有字段都存在
        for field in ['student_id', 'name', 'college', 'major', 'grade', 'klass', 'email', 'phone']:
            info.setdefault(field, '')

        return info

    def _fetch_courses_profile(self) -> dict:
        """从 courses.zju.edu.cn/api/profile 获取个人信息

        返回字段映射:
        - user_no → student_id (学号)
        - name → name (姓名)
        - department → college (部门/学院)
        - program → major (专业)
        - grade → grade (年级)
        - klass → klass (班级)
        - email → email
        - mobile_phone → phone
        """
        try:
            # courses 的 CAS 认证是通过多层 redirect (identity.zju.edu.cn → zjuam → identity → courses)
            # allow_redirects=True 让 requests 自动跟随所有重定向
            resp = self.session.get(
                self.COURSES_PROFILE_URL,
                allow_redirects=True,
                timeout=20,
            )

            if resp.status_code != 200:
                logger.warning('courses profile 返回 HTTP %s', resp.status_code)
                return {}

            data = resp.json()
            if not isinstance(data, dict):
                return {}

            # 辅助函数：安全提取嵌套字段
            def _safe_str(val):
                """如果 val 是 dict，提取 name 字段；否则直接转字符串"""
                if isinstance(val, dict):
                    return str(val.get('name') or '')
                if val is None:
                    return ''
                return str(val)

            # 提取需要的字段
            # department 和 program 可能是嵌套对象 {name: "xxx", ...}
            department_raw = data.get('department', '')
            program_raw = data.get('program', '')
            org_raw = data.get('org', '')

            result = {
                'student_id': str(data.get('user_no', '')),
                'name': data.get('name', ''),
                'college': _safe_str(department_raw) or _safe_str(org_raw),
                'major': _safe_str(program_raw),
                'grade': _safe_str(data.get('grade')),
                'klass': _safe_str(data.get('klass')),
                'email': _safe_str(data.get('email')),
                'phone': _safe_str(data.get('mobile_phone')),
            }

            logger.debug('courses profile 原始数据: user_no=%s, name=%s, department=%s, program=%s, grade=%s',
                         data.get('user_no'), data.get('name'),
                         data.get('department'), data.get('program'), data.get('grade'))

            return result

        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning('courses profile 请求异常: %s', e)
            return {}

    def _fetch_zdbk_schedule_info(self) -> dict:
        """从 ZDBK 课表 API 获取学籍信息（已验证可用）

        返回字段映射:
        - xh → student_id (学号)
        - xm → name (姓名)
        - xy → college (学院)
        - zy → major (专业)
        - xzb → klass (行政班)
        """
        try:
            # Step 1: SSO 重定向到 ZDBK，获取 JSESSIONID
            if not self.jsessionid:
                self._zdbk_sso_login()

            if not self.jsessionid:
                logger.warning('无法获取 ZDBK JSESSIONID')
                return {}

            # Step 2: 请求课表 API（已验证返回包含学籍信息）
            resp = self.session.post(
                self.ZDBK_SCHEDULE_URL + f';jsessionid={self.jsessionid}',
                data={},  # 空参数返回当前学期课表
                cookies={'route': self.route},
                headers={
                    'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                timeout=15,
            )

            if resp.status_code != 200:
                logger.warning('ZDBK 课表 API 返回 HTTP %s', resp.status_code)
                return {}

            data = resp.json()
            if not isinstance(data, dict):
                return {}

            result = {
                'student_id': str(data.get('xh', '')),
                'name': data.get('xm', ''),
                'college': data.get('xy', ''),
                'major': data.get('zy', ''),
                'klass': data.get('xzb', ''),
            }

            logger.debug('ZDBK 课表原始数据: xh=%s, xm=%s, xy=%s, zy=%s, xzb=%s',
                         data.get('xh'), data.get('xm'),
                         data.get('xy'), data.get('zy'), data.get('xzb'))

            return result

        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning('ZDBK 课表 API 异常: %s', e)
            return {}

    def _zdbk_sso_login(self):
        """通过 CAS SSO 登录 ZDBK 教务网，获取 JSESSIONID"""
        service_url = (
            f'{self.CAS_LOGIN_URL}?service='
            f'https%3A%2F%2Fzdbk.zju.edu.cn%2Fjwglxt%2Fxtgl%2Flogin_ssologin.html'
        )
        resp = self.session.get(service_url, allow_redirects=True, timeout=15)
        final_url = resp.url

        # 从多种来源提取 JSESSIONID
        jsessionid = resp.cookies.get('JSESSIONID')
        if not jsessionid:
            # Tomcat URL rewriting: ...;jsessionid=XXX?...
            match = re.search(r';jsessionid=([A-Fa-f0-9]+)', final_url)
            if match:
                jsessionid = match.group(1)
        if not jsessionid:
            # 遍历所有 cookies
            for cookie in self.session.cookies:
                if 'JSESSION' in cookie.name.upper():
                    jsessionid = cookie.value
                    break

        self.jsessionid = jsessionid
        self.route = resp.cookies.get('route', '')
        logger.debug('ZDBK SSO: jsessionid=%s', jsessionid[:20] if jsessionid else 'None')

    # ── 课程数据获取 ──────────────────────────────────────

    def get_course_data(self) -> list:
        """从 courses.zju.edu.cn/api/todos 获取课程列表

        从 todo_list 中提取去重课程信息。

        返回:
            [{'name': str, 'code': str, 'id': int}, ...]
        """
        if not self.sso_cookie:
            logger.warning('无 SSO Cookie，无法获取课程数据')
            return []

        try:
            # allow_redirects=True 自动完成 CAS→identity→courses 的 SSO 跳转链
            resp = self.session.get(
                self.COURSES_TODOS_URL,
                allow_redirects=True,
                timeout=20,
            )

            if resp.status_code != 200:
                logger.warning('courses todos API 返回 HTTP %s', resp.status_code)
                return []

            data = resp.json()
            items = []
            if isinstance(data, dict):
                items = data.get('todo_list', [])
            elif isinstance(data, list):
                items = data

            if not items:
                logger.warning('courses todos 返回空列表（可能当前学期无课程）')
                return []

            # 从 todo_list 提取去重课程
            seen_names = set()
            seen_ids = set()
            courses = []
            for item in items:
                course_name = item.get('course_name', '')
                course_code = item.get('course_code', '')
                course_id = item.get('course_id', '')

                # 按 course_id 去重更加可靠
                dedup_key = str(course_id) if course_id else course_name
                if dedup_key and dedup_key not in seen_ids:
                    seen_ids.add(dedup_key)
                    seen_names.add(course_name)
                    courses.append({
                        'name': course_name,
                        'code': course_code,
                        'id': str(course_id),
                    })

            logger.info('从 todos 提取到 %d 门课程', len(courses))
            return courses

        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning('获取课程数据失败: %s', e)
            return []

    # ── 完整课程表获取（ZDBK 课表 API）─────────────────────

    def get_course_schedule(self, school_year: str = '2025', semester: str = '3') -> list:
        """从 ZDBK 课表 API 获取完整课程表（含课程名/教师/时间/地点）

        相比 courses.zju.edu.cn/api/todos（仅返回有待办作业的课程），
        此方法返回当前学期全部已选课程，数据量更大更完整。

        Args:
            school_year: 学年，如 '2025' 表示 2025-2026 学年
            semester: 学期，'3'=春夏, '12'=秋冬

        返回:
            [{
                'name': str,         # 课程名称
                'teacher_id': str,   # 教师工号
                'teacher_name': str, # 教师姓名（从 kcb 字段解析）
                'schedule': str,     # 上课时间（如"春夏{第1-8周|2节/周}"）
                'location': str,     # 上课地点
                'exam_time': str,    # 考试时间
                'raw_kcb': str,      # 原始 kcb 字段
            }, ...]
        """
        if not self.sso_cookie:
            logger.warning('无 SSO Cookie，无法获取课程表')
            return []

        try:
            # 确保已登录 ZDBK
            if not self.jsessionid:
                self._zdbk_sso_login()
            if not self.jsessionid:
                logger.warning('无 ZDBK JSESSIONID')
                return []

            # 调用课表查询 API（已验证可用，返回 89 条记录）
            resp = self.session.post(
                self.ZDBK_SCHEDULE_URL + f';jsessionid={self.jsessionid}',
                data={'xnm': school_year, 'xqm': semester},
                cookies={'route': self.route},
                headers={
                    'Referer': 'https://zdbk.zju.edu.cn/jwglxt/xtgl/index_initMenu.html',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                timeout=20,
            )

            if resp.status_code != 200:
                logger.warning('ZDBK 课表 API 返回 HTTP %s', resp.status_code)
                return []

            data = resp.json()
            kb_list = data.get('kbList', [])
            if not kb_list:
                logger.warning('课表为空')
                return []

            # 解析 kcb HTML 字段，提取课程名/教师/时间/地点/考试
            courses_seen = set()
            courses = []

            for kb in kb_list:
                kcb_raw = kb.get('kcb', '')
                if not kcb_raw:
                    continue

                # 解析 kcb 格式:
                # "<课程名><br><学期>{<周次>|<节次>}<br><教师><br><教室>zwf<考试时间>zwf<考试地点>"
                parts = kcb_raw.split('<br>')

                name = parts[0].strip() if len(parts) > 0 else ''
                schedule = parts[1].strip() if len(parts) > 1 else ''
                teacher_name = parts[2].strip() if len(parts) > 2 else ''
                location_raw = parts[3].strip() if len(parts) > 3 else ''

                # 跳过重复课程名（同一课程可能有多个时间段）
                if not name:
                    continue

                # 解析考试信息（如果存在）
                exam_time = ''
                exam_location = ''
                if 'zwf' in location_raw:
                    exam_parts = location_raw.split('zwf')
                    location = exam_parts[0].strip()
                    if len(exam_parts) > 1:
                        exam_time = exam_parts[1].strip()
                    if len(exam_parts) > 2:
                        exam_location = exam_parts[2].strip()
                else:
                    location = location_raw

                # 按课程名去重，但合并时间段
                if name not in courses_seen:
                    courses_seen.add(name)
                    courses.append({
                        'name': name,
                        'teacher_id': kb.get('jszgh', ''),
                        'teacher_name': teacher_name,
                        'schedule': schedule,
                        'location': location,
                        'exam_time': exam_time,
                        'exam_location': exam_location,
                        'course_id': kb.get('xkkh', ''),  # 选课课号
                    })

            logger.info('从 ZDBK 课表提取到 %d 门课程', len(courses))
            return courses

        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning('获取课程表失败: %s', e)
            return []

    # ── RSA 加密 ──────────────────────────────────────────

    @staticmethod
    def _rsa_encrypt(plaintext: str, modulus: int, exponent: int, modulus_hex_len: int) -> str:
        """RSA 加密密码（兼容 ZJU CAS 前端加密格式）

        ZJU CAS JS 前端加密流程:
        1. 密码字符串 → UTF-8 字节
        2. UTF-8 字节 → 十六进制字符串
        3. 十六进制字符串 → 大整数 m
        4. 计算 c = m^e mod n（纯模幂运算，无 PKCS#1 padding）
        5. c → 十六进制字符串，填充到与 modulus 相同长度

        Args:
            plaintext: 明文密码
            modulus: RSA 模数 n (int)
            exponent: RSA 公钥指数 e (int, 通常 65537)
            modulus_hex_len: 模数 hex 字符串长度（用于 zfill 填充）
        """
        # 密码 → UTF-8 字节 → 十六进制 → 大整数
        pwd_bytes = plaintext.encode('utf-8')
        pwd_hex = pwd_bytes.hex()
        pwd_int = int(pwd_hex, 16)

        # RSA: c = m^e mod n
        encrypted_int = pow(pwd_int, exponent, modulus)

        # 转十六进制，填充到与 modulus 相等长度
        return hex(encrypted_int)[2:].zfill(modulus_hex_len)
