"""用户信息 API"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import User, Book, Favorite, Order
from services.auth import login_required
from services.validators import validate_phone, validate_email
from services.__init__ import ERROR_CODES

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户完整信息"""
    user = User.query.get(request.current_user_id)
    if not user:
        return jsonify({'status': 'error', 'code': 'USER_NOT_FOUND', 'message': ERROR_CODES['USER_NOT_FOUND']}), 404

    # 统计数据
    my_books = Book.query.filter_by(user_id=user.id).count()
    my_sold = Book.query.filter_by(user_id=user.id, status='已售').count()
    fav_count = Favorite.query.filter_by(user_id=user.id).count()

    result = user.to_dict()
    result.update({
        'stats': {
            'books_count': my_books,
            'sold_count': my_sold,
            'favorites_count': fav_count,
        },
    })
    return jsonify({'status': 'success', 'data': result})


@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户信息"""
    user = User.query.get(request.current_user_id)
    if not user:
        return jsonify({'status': 'error', 'code': 'USER_NOT_FOUND', 'message': ERROR_CODES['USER_NOT_FOUND']}), 404

    data = request.get_json() or {}
    for field in ['nickname', 'college', 'major', 'grade']:
        if field in data:
            setattr(user, field, data[field])

    # 手机号更新：验证格式 + 检查唯一性
    if 'phone' in data:
        new_phone = data['phone'].strip()
        valid, msg = validate_phone(new_phone)
        if not valid:
            return jsonify({'status': 'error', 'code': 'AUTH_PHONE_INVALID', 'message': msg}), 400
        if new_phone != user.phone and User.query.filter_by(phone=new_phone).first():
            return jsonify({'status': 'error', 'code': 'AUTH_DUPLICATE_USER', 'message': '该手机号已被其他用户使用'}), 409
        user.phone = new_phone

    # 邮箱更新：验证格式 + 检查唯一性
    if 'email' in data:
        new_email = data['email'].strip()
        if new_email:
            valid, msg = validate_email(new_email)
            if not valid:
                return jsonify({'status': 'error', 'code': 'AUTH_EMAIL_INVALID', 'message': msg}), 400
            if new_email != user.email and User.query.filter_by(email=new_email).first():
                return jsonify({'status': 'error', 'code': 'AUTH_DUPLICATE_USER', 'message': '该邮箱已被其他用户使用'}), 409
        user.email = new_email if new_email else None

    db.session.commit()
    return jsonify({'status': 'success', 'data': user.to_dict(), 'message': '已更新'})


@user_bp.route('/books', methods=['GET'])
@login_required
def get_my_books():
    """获取当前用户发布的书籍"""
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    query = Book.query.filter_by(user_id=request.current_user_id)
    if status:
        query = query.filter(Book.status == status)

    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'status': 'success',
        'data': {
            'books': [b.to_dict() for b in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
        },
    })


@user_bp.route('/orders', methods=['GET'])
@login_required
def get_my_orders():
    """获取当前用户的订单列表（买入+卖出）"""
    role = request.args.get('role', 'all')  # buy/sell/all
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    if role == 'buy':
        query = Order.query.filter(Order.buyer_id == request.current_user_id)
    elif role == 'sell':
        query = Order.query.filter(Order.seller_id == request.current_user_id)
    else:
        from sqlalchemy import or_
        query = Order.query.filter(or_(
            Order.buyer_id == request.current_user_id,
            Order.seller_id == request.current_user_id,
        ))

    if status_filter:
        query = query.filter(Order.status == status_filter)

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'status': 'success',
        'data': {
            'orders': [o.to_dict() for o in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
        },
    })
