"""AI 教材推荐引擎 — 基于课程名 + ZDBK 数据，使用 DeepSeek 推荐教材

将学生当前学期课程映射到推荐教材，并与平台在售二手书进行匹配。
"""
import json
import logging
import os
from services.ai_client import call_deepseek

logger = logging.getLogger(__name__)

# 预置的浙大课程-教材映射库（无需 API 调用的快速匹配）
PRESET_COURSE_BOOKS = {
    '微积分': [
        {'title': '微积分（上册）', 'author': '同济大学数学系', 'isbn': '9787040392913', 'publisher': '高等教育出版社'},
        {'title': '微积分（下册）', 'author': '同济大学数学系', 'isbn': '9787040445155', 'publisher': '高等教育出版社'},
    ],
    '线性代数': [
        {'title': '线性代数（第七版）', 'author': '同济大学数学系', 'isbn': '9787040524424', 'publisher': '高等教育出版社'},
    ],
    '普通物理学': [
        {'title': '普通物理学（第七版）', 'author': '程守洙', 'isbn': '9787040458594', 'publisher': '高等教育出版社'},
    ],
    '有机化学': [
        {'title': '有机化学（第六版）', 'author': '邢其毅', 'isbn': '9787301279248', 'publisher': '北京大学出版社'},
    ],
    '概率论': [
        {'title': '概率论与数理统计（第五版）', 'author': '盛骤', 'isbn': '9787040514721', 'publisher': '高等教育出版社'},
    ],
    '英语口语': [
        {'title': '大学英语口语教程', 'author': '浙江大学外语学院', 'isbn': '', 'publisher': '浙江大学出版社'},
    ],
    '管理统计': [
        {'title': '管理统计学', 'author': '马世罕', 'isbn': '', 'publisher': '浙江大学出版社'},
        {'title': '商务与经济统计（第14版）', 'author': 'Anderson', 'isbn': '9787111642586', 'publisher': '机械工业出版社'},
    ],
    '组织行为学': [
        {'title': '组织行为学（第18版）', 'author': 'Stephen P. Robbins', 'isbn': '9787300283271', 'publisher': '中国人民大学出版社'},
    ],
    '运作管理': [
        {'title': '运作管理（第12版）', 'author': 'Jay Heizer', 'isbn': '9787300289122', 'publisher': '中国人民大学出版社'},
    ],
    '微观经济学': [
        {'title': '微观经济学（第九版）', 'author': '曼昆', 'isbn': '9787301283691', 'publisher': '北京大学出版社'},
    ],
    '宏观经济学': [
        {'title': '宏观经济学（第十版）', 'author': '曼昆', 'isbn': '9787301283684', 'publisher': '北京大学出版社'},
    ],
    '管理学': [
        {'title': '管理学（第15版）', 'author': 'Stephen P. Robbins', 'isbn': '9787300322651', 'publisher': '中国人民大学出版社'},
    ],
    '社会学': [
        {'title': '社会学概论新修（第五版）', 'author': '郑杭生', 'isbn': '9787300274346', 'publisher': '中国人民大学出版社'},
    ],
    'C语言': [
        {'title': 'C程序设计（第五版）', 'author': '谭浩强', 'isbn': '9787302481440', 'publisher': '清华大学出版社'},
    ],
    'Python': [
        {'title': 'Python编程：从入门到实践（第3版）', 'author': 'Eric Matthes', 'isbn': '9787115546081', 'publisher': '人民邮电出版社'},
    ],
    '数据结构': [
        {'title': '数据结构（C语言版）', 'author': '严蔚敏', 'isbn': '9787302147510', 'publisher': '清华大学出版社'},
    ],
    '马克思主义基本原理': [
        {'title': '马克思主义基本原理（2023年版）', 'author': '本书编写组', 'isbn': '9787040599019', 'publisher': '高等教育出版社'},
    ],
    '毛泽东': [
        {'title': '毛泽东思想和中国特色社会主义理论体系概论（2023年版）', 'author': '本书编写组', 'isbn': '9787040599033', 'publisher': '高等教育出版社'},
    ],
    '习近平': [
        {'title': '习近平新时代中国特色社会主义思想概论', 'author': '本书编写组', 'isbn': '9787040615985', 'publisher': '高等教育出版社'},
    ],
    '中国近现代史': [
        {'title': '中国近现代史纲要（2023年版）', 'author': '本书编写组', 'isbn': '9787040599057', 'publisher': '高等教育出版社'},
    ],
    '思想道德': [
        {'title': '思想道德与法治（2023年版）', 'author': '本书编写组', 'isbn': '9787040599040', 'publisher': '高等教育出版社'},
    ],
    '计算机': [
        {'title': '计算机组成原理（第3版）', 'author': '唐朔飞', 'isbn': '9787040572113', 'publisher': '高等教育出版社'},
    ],
    '数据库': [
        {'title': '数据库系统概论（第5版）', 'author': '王珊', 'isbn': '9787040406641', 'publisher': '高等教育出版社'},
    ],
    '经济学': [
        {'title': '经济学原理（第8版）', 'author': '曼昆', 'isbn': '9787301483678', 'publisher': '北京大学出版社'},
    ],
}


def _match_preset(course_name: str) -> list:
    """从预置库匹配教材（关键词模糊匹配，毫秒级）"""
    results = []
    for key, books in PRESET_COURSE_BOOKS.items():
        if key in course_name:
            results.extend(books)
    return results[:3]  # 最多返回 3 本


def recommend_textbooks_for_courses(
    courses: list,
    use_ai: bool = True,
    ai_max_per_call: int = 10,
) -> list:
    """为课程列表推荐教材

    策略:
    1. 先查预置库 → 快速匹配（毫秒级）
    2. 预置库未命中的课程 → 调用 DeepSeek AI 推荐（秒级）

    Args:
        courses: 课程列表，每项至少含 'name' 字段
        use_ai: 是否启用 AI 推荐（False 则仅使用预置库）
        ai_max_per_call: 单次 AI 调用最多处理的课程数

    返回:
        [{
            'course_name': str,
            'textbooks': [{'title', 'author', 'isbn', 'publisher', 'source': 'preset'|'ai'}, ...]
        }, ...]
    """
    results = []
    ai_courses = []

    for course in courses:
        course_name = course.get('name', '')
        if not course_name:
            continue

        # Step 1: 预置库匹配
        preset_books = _match_preset(course_name)
        if preset_books:
            results.append({
                'course_name': course_name,
                'textbooks': [{**b, 'source': 'preset'} for b in preset_books],
            })
        else:
            ai_courses.append(course)

    # Step 2: AI 推荐（未命中预置库的课程）
    if use_ai and ai_courses:
        logger.info('预置库匹配 %d 门，剩余 %d 门调用 AI', len(results), len(ai_courses))

        # 分批调用 AI
        for i in range(0, len(ai_courses), ai_max_per_call):
            batch = ai_courses[i:i + ai_max_per_call]
            try:
                ai_results = _ai_recommend_batch(batch)
                results.extend(ai_results)
            except Exception as e:
                logger.warning('AI 教材推荐失败 (batch %d): %s', i // ai_max_per_call, e)
                # 降级：返回空教材列表
                for course in batch:
                    results.append({
                        'course_name': course.get('name', ''),
                        'textbooks': [],
                    })

    elif ai_courses:
        # AI 未启用，返回空列表
        for course in ai_courses:
            results.append({
                'course_name': course.get('name', ''),
                'textbooks': [],
            })

    return results


def _ai_recommend_batch(courses: list) -> list:
    """使用 DeepSeek AI 为一批课程推荐教材"""
    if not os.environ.get('DEEPSEEK_API_KEY'):
        logger.warning('DEEPSEEK_API_KEY 未设置，跳过 AI 教材推荐')
        return [{'course_name': c.get('name', ''), 'textbooks': []} for c in courses]

    course_names = [c.get('name', '') for c in courses]
    course_list_str = '\n'.join(f'{i+1}. {name}' for i, name in enumerate(course_names))

    prompt = f"""你是浙江大学教务系统的教材推荐专家。以下是浙大学生当前学期所选课程：

{course_list_str}

请为每门课程推荐最常用的教材（通常每门课 1-3 本）。推荐时优先考虑浙江大学实际使用的教材版本。

请严格按照以下 JSON 格式返回（不要包含任何其他内容）：
{{
  "recommendations": [
    {{
      "course_name": "课程名",
      "textbooks": [
        {{"title": "教材名", "author": "作者", "isbn": "ISBN号（如知道）", "publisher": "出版社"}}
      ]
    }}
  ]
}}

注意：
- isbn 字段如果不知道可以留空字符串 ""
- 只推荐该课程在浙江大学最常用的教材
- 优先推荐国内出版社的教材（高教社、清华社、浙大社等）"""

    response = call_deepseek(
        messages=[
            {'role': 'system', 'content': '你是浙大教材推荐专家。请只返回 JSON 格式结果，不要有其他文字。'},
            {'role': 'user', 'content': prompt},
        ],
        temperature=0.2,
        max_tokens=2048,
    )

    # 解析 AI 响应
    try:
        # 尝试提取 JSON 块
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group(0))
        else:
            data = json.loads(response)

        recommendations = data.get('recommendations', [])

        # 标记来源为 AI
        for rec in recommendations:
            for tb in rec.get('textbooks', []):
                tb['source'] = 'ai'

        return recommendations

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning('AI 教材推荐响应解析失败: %s', e)
        logger.debug('AI 原始响应: %s', response[:500])
        return [{'course_name': c.get('name', ''), 'textbooks': []} for c in courses]


def match_platform_books(textbooks: list, available_books: list) -> list:
    """将推荐教材与平台在售二手书进行匹配

    Args:
        textbooks: recommend_textbooks_for_courses() 的返回结果
        available_books: 平台在售书籍列表 [{title, author, price, id, ...}]

    返回:
        在原 textbooks 结构上增加 matched_books 字段
    """
    for course_rec in textbooks:
        for tb in course_rec.get('textbooks', []):
            tb_title = tb.get('title', '').lower().replace('（', '(').replace('）', ')')
            tb_author = tb.get('author', '').lower()
            matched = []

            for book in available_books:
                b_title = (book.get('title', '') or '').lower().replace('（', '(').replace('）', ')')
                b_author = (book.get('author', '') or '').lower()

                # 模糊匹配：书名关键词重叠度 > 50%
                if tb_title and b_title:
                    # 提取关键词（排除版本号/括号内容）
                    import re
                    tb_keywords = set(re.findall(r'[一-鿿\w]+', tb_title))
                    b_keywords = set(re.findall(r'[一-鿿\w]+', b_title))
                    if tb_keywords and b_keywords:
                        overlap = len(tb_keywords & b_keywords) / len(tb_keywords)
                        if overlap >= 0.5:
                            matched.append(book)

            tb['matched_books'] = matched
            tb['match_count'] = len(matched)

    return textbooks
