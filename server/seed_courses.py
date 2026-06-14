"""课程预置数据导入脚本

Usage: python seed_courses.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models import Course, CourseBook
from seed_data import SEED_COURSES


def seed_courses():
    """导入预置课程数据"""
    app = create_app()
    with app.app_context():
        # 检查是否已有数据
        if Course.query.first():
            print('[WARN] 课程数据已存在，跳过导入')
            return

        for course_data in SEED_COURSES:
            course = Course(
                name=course_data['name'],
                code=course_data['code'],
                college=course_data['college'],
                credits=course_data['credits'],
                semester='2025-2026-2',
            )
            db.session.add(course)
            db.session.flush()

            for book_data in course_data['books']:
                cb = CourseBook(
                    course_id=course.id,
                    book_title=book_data['title'],
                    book_author=book_data['author'],
                    book_isbn=book_data.get('isbn', ''),
                    is_required=book_data.get('required', True),
                )
                db.session.add(cb)

        db.session.commit()
        print(f'[OK] 已导入 {len(SEED_COURSES)} 门课程及对应教材')


if __name__ == '__main__':
    seed_courses()
