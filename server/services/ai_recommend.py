"""AI 个性化推荐引擎

根据用户课程列表和收藏偏好，使用 DeepSeek 从候选池中推荐最匹配的书籍。
"""
import json
import re
from models import UserCourse, Course, Favorite, Book
from services.ai_client import call_deepseek


def get_user_preferences(user_id: str) -> dict:
    """获取用户偏好信息

    Returns:
        {course_names: [...], fav_categories: [...], candidates: [...]}
    """
    # 获取用户课程
    user_courses = UserCourse.query.filter_by(user_id=user_id).all()
    course_names = []
    for uc in user_courses:
        course = Course.query.get(uc.course_id)
        if course:
            course_names.append(course.name)

    # 获取收藏类别偏好
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    fav_categories = set()
    for fav in favorites:
        book = Book.query.get(fav.book_id)
        if book and book.category:
            fav_categories.add(book.category)

    # 获取候选书籍（在售，排除用户自己的）
    candidates = Book.query.filter(
        Book.status == '在售',
        Book.user_id != user_id,
    ).limit(50).all()

    candidates_info = [
        {
            'id': b.id,
            'title': b.title,
            'author': b.author or '',
            'category': b.category or '',
            'price': b.price,
        }
        for b in candidates
    ]

    return {
        'course_names': course_names,
        'fav_categories': list(fav_categories),
        'candidates': candidates_info,
    }


def recommend_books(user_id: str, count: int = 6) -> list[dict]:
    """AI 个性化推荐

    Args:
        user_id: 用户 UUID
        count: 推荐数量

    Returns:
        [{id, title, author, ...recommend_reason}, ...]
    """
    prefs = get_user_preferences(user_id)

    if not prefs['candidates']:
        return get_hot_recommendations(count)

    prompt = f"""用户课程: {prefs['course_names']}
用户偏好类别: {prefs['fav_categories']}
候选书籍: {json.dumps(prefs['candidates'], ensure_ascii=False)}

请从候选书籍中选择最匹配的 {count} 本推荐给该用户。
推荐时优先考虑：与用户课程相关的教材、与用户偏好类别匹配的书籍。
返回 JSON 数组: [{{"id": "书籍ID", "reason": "简短推荐理由(≤15字)"}}]
只返回 JSON 数组，不要其他文字。"""

    try:
        response = call_deepseek([
            {
                'role': 'system',
                'content': '你是浙江大学二手书推荐引擎。根据用户课程和偏好，推荐最匹配的书籍。只返回 JSON 数组。',
            },
            {'role': 'user', 'content': prompt},
        ], temperature=0.3, max_tokens=1024)

        # 提取 JSON 数组
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            recommended = json.loads(json_match.group())
            result = []
            for r in recommended:
                book = Book.query.get(r['id'])
                if book:
                    b_dict = book.to_dict()
                    b_dict['recommend_reason'] = r.get('reason', '')
                    result.append(b_dict)
            return result[:count]

        return get_hot_recommendations(count)
    except Exception:
        return get_hot_recommendations(count)


def get_hot_recommendations(count: int = 6) -> list[dict]:
    """热门推荐（降级策略）

    当 AI 不可用时，返回最新的在售书籍作为默认推荐。

    Args:
        count: 推荐数量

    Returns:
        [Book.to_dict(), ...]
    """
    books = Book.query.filter(Book.status == '在售').order_by(
        Book.created_at.desc()
    ).limit(count).all()
    result = []
    for b in books:
        b_dict = b.to_dict()
        b_dict['recommend_reason'] = '热门推荐'
        result.append(b_dict)
    return result
