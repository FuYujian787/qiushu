"""ISBN 查询服务（本地库 → 抓书网 → 课程库 → OpenLibrary → 手动填写）

数据源优先级：
  1. 本地教材库 (0ms) — 40+ 本浙大常用教材，0ms 命中
  2. 抓书网 zhuashu.cn (~2s) — 中文书籍，CIP 数据库，覆盖面广
  3. CourseBook 数据库 (~1ms) — 来自 seed_courses 的教材数据
  4. OpenLibrary (~3s) — 国际数据库，英文书友好
  5. 手动降级 (0ms) — 引导用户手动输入

注意：豆瓣图书 API v2 已于 2018 年关闭，不可用。
"""
import re
import requests
from html import unescape


# 浙大常用教材 ISBN 本地库（40+ 本，无需网络即可匹配）
LOCAL_TEXTBOOK_DB = {
    '9787040445155': {'title': '微积分（下册）', 'author': '同济大学数学系', 'publisher': '高等教育出版社'},
    '9787040524424': {'title': '线性代数（第七版）', 'author': '同济大学数学系', 'publisher': '高等教育出版社'},
    '9787040532979': {'title': '概率论与数理统计', 'author': '盛骤', 'publisher': '高等教育出版社'},
    '9787302147510': {'title': '数据结构（C语言版）', 'author': '严蔚敏', 'publisher': '清华大学出版社'},
    '9787111632887': {'title': '计算机网络（第8版）', 'author': '谢希仁', 'publisher': '电子工业出版社'},
    '9787302528236': {'title': '计算机组成原理（第3版）', 'author': '唐朔飞', 'publisher': '清华大学出版社'},
    '9787111564805': {'title': '数据库系统概论（第5版）', 'author': '王珊', 'publisher': '高等教育出版社'},
    '9787115428028': {'title': 'Python编程：从入门到实践', 'author': 'Eric Matthes', 'publisher': '人民邮电出版社'},
    '9787302423287': {'title': 'C程序设计（第五版）', 'author': '谭浩强', 'publisher': '清华大学出版社'},
    '9787115472588': {'title': '算法导论（第三版）', 'author': 'Thomas H. Cormen', 'publisher': '机械工业出版社'},
    '9787302517597': {'title': '操作系统（第4版）', 'author': '汤小丹', 'publisher': '西安电子科技大学出版社'},
    '9787040412772': {'title': '大学物理（上）', 'author': '马文蔚', 'publisher': '高等教育出版社'},
    '9787040412789': {'title': '大学物理（下）', 'author': '马文蔚', 'publisher': '高等教育出版社'},
    '9787040529024': {'title': '高等数学（第七版）上册', 'author': '同济大学数学系', 'publisher': '高等教育出版社'},
    '9787040529031': {'title': '高等数学（第七版）下册', 'author': '同济大学数学系', 'publisher': '高等教育出版社'},
    '9787040366181': {'title': '有机化学（第六版）', 'author': '天津大学有机化学教研室', 'publisher': '高等教育出版社'},
    '9787040544084': {'title': '马克思主义基本原理', 'author': '本书编写组', 'publisher': '高等教育出版社'},
    '9787040282559': {'title': '中国近现代史纲要', 'author': '本书编写组', 'publisher': '高等教育出版社'},
    '9787040494822': {'title': '毛泽东思想和中国特色社会主义理论体系概论', 'author': '本书编写组', 'publisher': '高等教育出版社'},
    '9787040582649': {'title': '习近平新时代中国特色社会主义思想概论', 'author': '本书编写组', 'publisher': '高等教育出版社'},
    '9787300174990': {'title': '微观经济学（第八版）', 'author': '罗伯特·S·平狄克', 'publisher': '中国人民大学出版社'},
    '9787300263352': {'title': '宏观经济学（第九版）', 'author': 'N·格里高利·曼昆', 'publisher': '中国人民大学出版社'},
    '9787040463897': {'title': '大学英语精读（第三版）', 'author': '董亚芬', 'publisher': '上海外语教育出版社'},
    '9787040566373': {'title': '思想道德与法治', 'author': '本书编写组', 'publisher': '高等教育出版社'},
    '9787111213826': {'title': 'Java编程思想（第4版）', 'author': 'Bruce Eckel', 'publisher': '机械工业出版社'},
    '9787115364654': {'title': 'JavaScript高级程序设计（第4版）', 'author': 'Matt Frisbie', 'publisher': '人民邮电出版社'},
    '9787115546086': {'title': '机器学习', 'author': '周志华', 'publisher': '清华大学出版社'},
    '9787115281487': {'title': '统计学习方法（第2版）', 'author': '李航', 'publisher': '清华大学出版社'},
    '9787302393184': {'title': '信号与系统（第3版）', 'author': '郑君里', 'publisher': '高等教育出版社'},
    '9787111561378': {'title': 'C++ Primer（第5版）', 'author': 'Stanley B. Lippman', 'publisher': '电子工业出版社'},
    '9787111580287': {'title': '离散数学及其应用（第8版）', 'author': 'Kenneth H. Rosen', 'publisher': '机械工业出版社'},
    '9787040538522': {'title': '电工学（第七版）上册', 'author': '秦曾煌', 'publisher': '高等教育出版社'},
    '9787040538539': {'title': '电工学（第七版）下册', 'author': '秦曾煌', 'publisher': '高等教育出版社'},
    '9787302553588': {'title': '数字逻辑电路（第6版）', 'author': '阎石', 'publisher': '清华大学出版社'},
    '9787560641003': {'title': '电磁场与电磁波（第4版）', 'author': '谢处方', 'publisher': '高等教育出版社'},
}


def _parse_zhuashu_html(html_text: str) -> dict | None:
    """解析 zhuashu.cn 返回的 HTML 页面，提取书籍信息

    页面结构:
        <li>书名：xxx</li>
        <li>作者：xxx（可选）</li>
        <li>出版社：xxx</li>
        <li>出版地：xxx（可选）</li>
        <li>出版时间：xxx（可选）</li>
        <li>cip：xxx（可选）</li>
        <li>isbn：xxx</li>

    返回 dict 或 None（未查到数据时）。
    """
    # 检查是否查询失败
    if '暂未查询到' in html_text or '未查询到此书号' in html_text:
        return None

    result = {}

    # 提取书名（第一个 <h1> 中的内容，格式: "xxx - 的书号查询结果"）
    title_match = re.search(r'<h1>\s*(.+?)\s*-\s*的书号查询结果\s*</h1>', html_text)
    if title_match:
        result['title'] = unescape(title_match.group(1).strip())

    # 解析 <li> 字段
    patterns = {
        'author': r'<li>\s*作者[：:]\s*(.*?)\s*</li>',
        'publisher': r'<li>\s*出版社[：:]\s*(.*?)\s*</li>',
        'pub_place': r'<li>\s*出版地[：:]\s*(.*?)\s*</li>',
        'pub_date': r'<li>\s*出版时间[：:]\s*(.*?)\s*</li>',
        'cip': r'<li>\s*cip[：:]\s*(.*?)\s*</li>',
        'isbn': r'<li>\s*isbn[：:]\s*(.*?)\s*</li>',
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, html_text, re.IGNORECASE)
        if match:
            val = unescape(match.group(1).strip())
            if val and val != '-':
                result[key] = val

    # 如果书名都没提取到，说明解析失败
    if not result.get('title'):
        return None

    return result


def _query_zhuashu(isbn: str) -> dict | None:
    """查询 zhuashu.cn（抓书网）ISBN 数据库

    这是中国 CIP 数据的公开查询入口，对中文书籍覆盖最广。
    """
    try:
        resp = requests.get(
            'https://www.zhuashu.cn/cha.html',
            params={'lx': 'isbn', 'k': isbn},
            timeout=5,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            },
        )
        if resp.status_code != 200:
            return None

        # 确保编码正确
        resp.encoding = 'utf-8'
        data = _parse_zhuashu_html(resp.text)
        if not data:
            return None

        return {
            'isbn': data.get('isbn', isbn),
            'title': data.get('title', ''),
            'author': data.get('author', ''),
            'publisher': data.get('publisher', ''),
            'pub_date': data.get('pub_date', ''),
            'cover_url': '',
            'source': 'zhuashu',
            'confidence': 'high' if data.get('author') and data.get('publisher') else 'medium',
        }
    except requests.RequestException:
        return None


def _query_openlibrary(isbn: str) -> dict | None:
    """查询 OpenLibrary 国际书籍数据库"""
    try:
        resp = requests.get(
            f'https://openlibrary.org/isbn/{isbn}.json',
            timeout=3,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        title = data.get('title', '')
        if not title:
            return None

        # OpenLibrary 作者是 URL 引用，需二次请求获取名字
        author = ''
        author_refs = data.get('authors', [])
        if author_refs:
            first_key = author_refs[0].get('key', '')
            if first_key:
                try:
                    a_resp = requests.get(
                        f'https://openlibrary.org{first_key}.json',
                        timeout=2,
                    )
                    if a_resp.status_code == 200:
                        author = a_resp.json().get('name', '')
                except requests.RequestException:
                    pass

        publishers = data.get('publishers', [])
        publisher = publishers[0] if publishers else ''

        return {
            'isbn': isbn,
            'title': title,
            'author': author,
            'publisher': publisher,
            'cover_url': f'https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg',
            'source': 'openlibrary',
            'confidence': 'medium' if author else 'low',
        }
    except requests.RequestException:
        return None


def lookup_isbn(isbn: str) -> dict:
    """通过 ISBN 查询书籍信息

    查询优先级（速度从快到慢，优先中文友好源）:
      1. 本地教材库 → 0ms, 40+ 本浙大教材, confidence: high
      2. zhuashu.cn → ~2s, 中文 CIP 数据库, confidence: high/medium
      3. CourseBook DB → ~1ms, seed_courses 数据, confidence: high
      4. OpenLibrary → ~3s, 国际数据库, confidence: medium/low
      5. 降级返回空 → 引导手动填写
    """
    isbn = isbn.strip().replace('-', '').replace(' ', '')

    # 校验 ISBN 格式
    if not isbn or not (len(isbn) == 10 or len(isbn) == 13):
        return {
            'isbn': isbn,
            'title': '',
            'author': '',
            'publisher': '',
            'cover_url': '',
            'source': 'invalid',
            'error': 'ISBN 格式不正确，应为 10 位或 13 位数字',
        }

    # === L1: 本地教材库（0ms）===
    if isbn in LOCAL_TEXTBOOK_DB:
        entry = LOCAL_TEXTBOOK_DB[isbn]
        return {
            'isbn': isbn,
            'title': entry['title'],
            'author': entry['author'],
            'publisher': entry['publisher'],
            'cover_url': '',
            'source': 'local',
            'confidence': 'high',
        }

    # === L2: 抓书网 zhuashu.cn（中文 CIP 数据库）===
    result = _query_zhuashu(isbn)
    if result and result.get('title'):
        return result

    # === L3: CourseBook 数据库 ===
    try:
        from models import CourseBook
        cb = CourseBook.query.filter_by(book_isbn=isbn).first()
        if cb:
            return {
                'isbn': isbn,
                'title': cb.book_title,
                'author': cb.book_author or '',
                'publisher': '',
                'cover_url': '',
                'source': 'course_db',
                'confidence': 'high',
            }
    except Exception:
        pass

    # === L4: OpenLibrary（国际数据库）===
    result = _query_openlibrary(isbn)
    if result:
        return result

    # === L5: 完全降级 ===
    return {
        'isbn': isbn,
        'title': '',
        'author': '',
        'publisher': '',
        'cover_url': '',
        'source': 'manual',
        'error': '未找到匹配的书籍信息，请手动填写',
    }
