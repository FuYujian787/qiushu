"""求书许愿墙 API"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import WantedBook
from services.auth import login_required
from services.wish_matcher import find_matches_for_wish

wishes_bp = Blueprint('wishes', __name__)


@wishes_bp.route('', methods=['GET'])
def list_wishes():
    """获取许愿列表"""
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = WantedBook.query
    if status:
        query = query.filter(WantedBook.status == status)

    query = query.order_by(WantedBook.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 为每条许愿检查是否有匹配的书籍
    wishes = []
    for w in pagination.items:
        w_dict = w.to_dict()
        matched = find_matches_for_wish(w, limit=3)
        w_dict['matched_books'] = [b.to_dict() for b in matched] if matched else []
        wishes.append(w_dict)

    return jsonify({
        'status': 'success',
        'data': {
            'wishes': wishes,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        },
    })


@wishes_bp.route('', methods=['POST'])
@login_required
def create_wish():
    """发布求书帖"""
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'status': 'error', 'message': '请输入书名'}), 400

    # 检查是否已有相同求书帖
    existing = WantedBook.query.filter_by(
        user_id=request.current_user_id,
        title=title,
        status='求购中',
    ).first()
    if existing:
        return jsonify({'status': 'error', 'message': '您已发布过相同书籍的求购帖'}), 400

    wish = WantedBook(
        user_id=request.current_user_id,
        title=title,
        author=data.get('author', '').strip(),
        isbn=data.get('isbn', '').strip(),
        reason=data.get('reason', '').strip(),
    )
    db.session.add(wish)
    db.session.commit()

    return jsonify({'status': 'success', 'data': wish.to_dict(), 'message': '求书帖已发布'}), 201


@wishes_bp.route('/<wish_id>', methods=['PUT'])
@login_required
def update_wish(wish_id):
    """更新求书帖状态"""
    wish = WantedBook.query.get(wish_id)
    if not wish:
        return jsonify({'status': 'error', 'code': 'WISH_NOT_FOUND', 'message': '求书帖不存在'}), 404
    if wish.user_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权操作'}), 403

    data = request.get_json() or {}
    if 'status' in data:
        wish.status = data['status']
    db.session.commit()

    return jsonify({'status': 'success', 'data': wish.to_dict()})


@wishes_bp.route('/<wish_id>', methods=['DELETE'])
@login_required
def delete_wish(wish_id):
    """删除求书帖"""
    wish = WantedBook.query.get(wish_id)
    if not wish:
        return jsonify({'status': 'error', 'code': 'WISH_NOT_FOUND', 'message': '求书帖不存在'}), 404
    if wish.user_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权操作'}), 403

    db.session.delete(wish)
    db.session.commit()
    return jsonify({'status': 'success', 'message': '已删除'})
