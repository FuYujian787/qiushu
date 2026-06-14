"""课程 API + 教材匹配"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Course, CourseBook, UserCourse, Book
from services.auth import login_required

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('', methods=['GET'])
def list_courses():
    """获取所有课程列表"""
    courses = Course.query.order_by(Course.name).all()
    return jsonify({
        'status': 'success',
        'data': [c.to_dict() for c in courses],
    })


@courses_bp.route('/<course_id>', methods=['GET'])
def get_course(course_id):
    """获取课程详情（含教材）"""
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'status': 'error', 'message': '课程不存在'}), 404

    result = course.to_dict()
    result['books'] = [cb.to_dict() for cb in course.books]
    return jsonify({'status': 'success', 'data': result})


@courses_bp.route('/user', methods=['GET'])
@login_required
def get_user_courses():
    """获取当前用户的课程列表"""
    user_courses = UserCourse.query.filter_by(user_id=request.current_user_id).all()
    result = []
    for uc in user_courses:
        course = Course.query.get(uc.course_id)
        if course:
            result.append({
                **course.to_dict(),
                'semester': uc.semester,
            })
    return jsonify({'status': 'success', 'data': result})


@courses_bp.route('/user', methods=['POST'])
@login_required
def add_user_course():
    """用户添加课程"""
    data = request.get_json() or {}
    course_id = data.get('course_id', '')
    semester = data.get('semester', '')

    course = Course.query.get(course_id)
    if not course:
        return jsonify({'status': 'error', 'message': '课程不存在'}), 404

    existing = UserCourse.query.filter_by(
        user_id=request.current_user_id,
        course_id=course_id,
    ).first()
    if existing:
        return jsonify({'status': 'success', 'message': '已添加过该课程'})

    uc = UserCourse(user_id=request.current_user_id, course_id=course_id, semester=semester)
    db.session.add(uc)
    db.session.commit()

    return jsonify({'status': 'success', 'data': uc.to_dict(), 'message': '课程已添加'}), 201


@courses_bp.route('/user/<course_id>', methods=['DELETE'])
@login_required
def remove_user_course(course_id):
    """用户删除课程"""
    uc = UserCourse.query.filter_by(
        user_id=request.current_user_id,
        course_id=course_id,
    ).first()
    if uc:
        db.session.delete(uc)
        db.session.commit()
    return jsonify({'status': 'success', 'message': '已删除'})


@courses_bp.route('/match', methods=['GET'])
@login_required
def match_books():
    """为用户匹配所需教材的二手书"""
    from services.course_matcher import match_books_for_user
    matched = match_books_for_user(request.current_user_id)
    return jsonify({'status': 'success', 'data': matched})
