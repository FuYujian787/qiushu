"""订单 API（下单 → 确认 → 完成）"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Order, Book, BookJourney, Review
from services.auth import login_required
from services.__init__ import ERROR_CODES

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('', methods=['GET'])
@login_required
def list_orders():
    """获取当前用户的订单列表"""
    role = request.args.get('role', 'all')  # buy/sell/all
    status_filter = request.args.get('status', '')

    query = db.or_(
        Order.buyer_id == request.current_user_id,
        Order.seller_id == request.current_user_id,
    )

    if role == 'buy':
        query = Order.buyer_id == request.current_user_id
    elif role == 'sell':
        query = Order.seller_id == request.current_user_id

    orders_query = Order.query.filter(query)
    if status_filter:
        orders_query = orders_query.filter(Order.status == status_filter)

    orders = orders_query.order_by(Order.created_at.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [o.to_dict() for o in orders],
    })


@orders_bp.route('/<order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """获取订单详情"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': ERROR_CODES['ORDER_NOT_FOUND']}), 404

    if order.buyer_id != request.current_user_id and order.seller_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权查看此订单'}), 403

    return jsonify({'status': 'success', 'data': order.to_dict()})


@orders_bp.route('', methods=['POST'])
@login_required
def create_order():
    """买家发起订单"""
    data = request.get_json() or {}
    book_id = data.get('book_id', '')

    book = Book.query.get(book_id)
    if not book or book.status != '在售':
        return jsonify({'status': 'error', 'code': 'BOOK_NOT_FOUND', 'message': ERROR_CODES['BOOK_NOT_FOUND']}), 404

    if book.user_id == request.current_user_id:
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '不能购买自己的书籍'}), 400

    # 检查是否已有待确认订单
    existing = Order.query.filter_by(
        book_id=book_id,
        buyer_id=request.current_user_id,
        status='待确认',
    ).first()
    if existing:
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '您已有待确认的订单'}), 400

    order = Order(
        book_id=book_id,
        buyer_id=request.current_user_id,
        seller_id=book.user_id,
        contact_phone=data.get('contact_phone', ''),
        contact_note=data.get('contact_note', ''),
        status='待确认',
    )
    db.session.add(order)

    # 下单后书籍状态变为「预定了」，其他买家可见但无法再下单
    book.status = '预定了'
    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': order.to_dict(),
        'message': '订单已创建，等待卖家确认',
    }), 201


@orders_bp.route('/<order_id>/confirm', methods=['POST'])
@login_required
def confirm_order(order_id):
    """卖家确认订单"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': ERROR_CODES['ORDER_NOT_FOUND']}), 404

    if order.seller_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权操作此订单'}), 403

    if order.status != '待确认':
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '当前订单状态不允许此操作'}), 400

    order.status = '已确认'
    db.session.commit()

    return jsonify({'status': 'success', 'data': order.to_dict(), 'message': '订单已确认'})


@orders_bp.route('/<order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    """确认交易完成"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': ERROR_CODES['ORDER_NOT_FOUND']}), 404

    if order.buyer_id != request.current_user_id and order.seller_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权操作此订单'}), 403

    if order.status != '已确认':
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '当前订单状态不允许此操作'}), 400

    order.status = '已完成'
    order.book.status = '已售'

    # 取消该书的其他活跃订单（待确认/已确认），通知其他买家该书已售出
    other_orders = Order.query.filter(
        Order.book_id == order.book_id,
        Order.id != order.id,
        Order.status.in_(['待确认', '已确认']),
    ).all()
    for o in other_orders:
        o.status = '已取消'

    # 记录旅程
    journey = BookJourney(
        book_id=order.book_id,
        from_user_id=order.seller_id,
        to_user_id=order.buyer_id,
        event_type='售出',
        note=f'由 {order.buyer.nickname} 购得' if order.buyer else '',
    )
    db.session.add(journey)
    db.session.commit()

    return jsonify({'status': 'success', 'data': order.to_dict(), 'message': '交易已完成'})


@orders_bp.route('/<order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """取消订单"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': ERROR_CODES['ORDER_NOT_FOUND']}), 404

    if order.buyer_id != request.current_user_id and order.seller_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权操作此订单'}), 403

    if order.status in ('已完成', '已取消'):
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '当前订单状态不允许此操作'}), 400

    order.status = '已取消'

    # 检查是否还有其他活跃订单（待确认/已确认），没有则恢复书籍为在售
    active_orders = Order.query.filter(
        Order.book_id == order.book_id,
        Order.id != order.id,
        Order.status.in_(['待确认', '已确认']),
    ).count()
    if active_orders == 0:
        order.book.status = '在售'

    db.session.commit()

    return jsonify({'status': 'success', 'data': order.to_dict(), 'message': '订单已取消'})
