"""课程-教材匹配服务

根据用户课程列表，搜索在售二手书，返回匹配结果。
"""
from models import UserCourse, Course, CourseBook, Book


def match_books_for_user(user_id: str) -> list[dict]:
    """为用户匹配所需教材的二手书

    Args:
        user_id: 用户 UUID

    Returns:
        [{course, required_book, available_count, available_books}, ...]
    """
    user_courses = UserCourse.query.filter_by(user_id=user_id).all()
    matched = []

    for uc in user_courses:
        course = Course.query.get(uc.course_id)
        if not course:
            continue

        course_books = CourseBook.query.filter_by(course_id=uc.course_id).all()
        for cb in course_books:
            # 模糊匹配书名（取前10字符避免标点差异）
            keyword = cb.book_title[:10] if len(cb.book_title) >= 4 else cb.book_title
            available = Book.query.filter(
                Book.title.contains(keyword),
                Book.status == '在售',
            ).all()

            if available:
                matched.append({
                    'course': course.to_dict(),
                    'required_book': cb.to_dict(),
                    'available_count': len(available),
                    'available_books': [b.to_dict() for b in available[:5]],
                })

    return matched


def match_course_for_book(book_title: str) -> list[dict]:
    """根据书名反向查找可能需要该书的课程

    Args:
        book_title: 书名

    Returns:
        [{course, course_book}] 匹配的课程-教材关联
    """
    keyword = book_title[:10] if len(book_title) >= 4 else book_title
    course_books = CourseBook.query.filter(
        CourseBook.book_title.contains(keyword)
    ).all()

    result = []
    for cb in course_books:
        course = Course.query.get(cb.course_id)
        if course:
            result.append({
                'course': course.to_dict(),
                'course_book': cb.to_dict(),
            })

    return result
