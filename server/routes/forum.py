"""论坛 API（帖子/回帖）"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Post, Reply, Course, Book
from services.auth import login_required

forum_bp = Blueprint('forum', __name__)


@forum_bp.route('/posts', methods=['GET'])
def list_posts():
    """获取帖子列表"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    course_id = request.args.get('course_id', '')
    post_type = request.args.get('type', '')

    query = Post.query
    if course_id:
        query = query.filter(Post.course_id == course_id)
    if post_type:
        query = query.filter(Post.type == post_type)

    # 置顶优先 + 时间倒序
    query = query.order_by(Post.is_pinned.desc(), Post.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'status': 'success',
        'data': {
            'posts': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        },
    })


@forum_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """获取帖子详情"""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'status': 'error', 'code': 'POST_NOT_FOUND', 'message': '帖子不存在'}), 404

    # 增加浏览数
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()

    result = post.to_dict()
    replies = Reply.query.filter_by(post_id=post_id).order_by(Reply.created_at.asc()).all()
    result['replies'] = [r.to_dict() for r in replies]

    return jsonify({'status': 'success', 'data': result})


@forum_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    """发帖"""
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'status': 'error', 'message': '请输入帖子标题'}), 400

    post = Post(
        user_id=request.current_user_id,
        course_id=data.get('course_id'),
        book_id=data.get('book_id'),
        type=data.get('type', '其他'),
        title=title,
        content=data.get('content', '').strip(),
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({'status': 'success', 'data': post.to_dict(), 'message': '发布成功'}), 201


@forum_bp.route('/posts/<post_id>/reply', methods=['POST'])
@login_required
def reply_post(post_id):
    """回帖"""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'status': 'error', 'code': 'POST_NOT_FOUND', 'message': '帖子不存在'}), 404

    data = request.get_json() or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'status': 'error', 'message': '请输入回复内容'}), 400

    reply = Reply(
        post_id=post_id,
        user_id=request.current_user_id,
        content=content,
    )
    post.reply_count = (post.reply_count or 0) + 1
    db.session.add(reply)
    db.session.commit()

    return jsonify({'status': 'success', 'data': reply.to_dict(), 'message': '回复成功'}), 201


@forum_bp.route('/courses', methods=['GET'])
def list_courses():
    """获取课程列表（供论坛分区使用）"""
    courses = Course.query.order_by(Course.name).all()
    return jsonify({
        'status': 'success',
        'data': [c.to_dict() for c in courses],
    })


@forum_bp.route('/posts/<post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """删除帖子"""
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'status': 'error', 'code': 'POST_NOT_FOUND', 'message': '帖子不存在'}), 404
    if post.user_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '只能删除自己的帖子'}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({'status': 'success', 'message': '已删除'})
