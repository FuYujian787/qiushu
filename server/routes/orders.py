"""
订单路由：下单、查询
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from db import db
from models import Order, Book

orders_bp = Blueprint('orders', __name__)

USER_BOOK_ID_OFFSET = 100000000


@orders_bp.route('/api/orders', methods=['POST'])
def place_order():
    """下单"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    buyer = (data.get('buyer') or '').strip()
    address = (data.get('address') or '未设置地址').strip()
    items = data.get('items', [])

    if not buyer:
        return jsonify({'success': False, 'message': '买家不能为空'}), 400
    if not items:
        return jsonify({'success': False, 'message': '购物车为空'}), 400

    created_orders = []
    for item in items:
        book_id = item.get('id')
        qty = item.get('qty', 1)
        if book_id and book_id >= USER_BOOK_ID_OFFSET:
            book_id = book_id - USER_BOOK_ID_OFFSET
        book = Book.query.get(book_id)
        if not book:
            continue

        order_no = 'ORD-' + datetime.utcnow().strftime('%Y%m%d%H%M%S') + '-' + uuid.uuid4().hex[:6]

        for _ in range(qty):
            order = Order(
                order_no=order_no,
                book_id=book.id,
                title=book.title,
                price=book.price,
                status='待收货',
                buyer=buyer,
                address=address,
            )
            db.session.add(order)
            created_orders.append(order)

        if book.seller and book.seller != buyer:
            from models import Notification
            notif = Notification(
                user_name=book.seller,
                title='书籍售出通知',
                desc=f'买家 {buyer} 已购买您的书籍《{book.title}》',
            )
            db.session.add(notif)

    db.session.commit()
    return jsonify({
        'success': True,
        'orders': [o.to_dict() for o in created_orders],
    }), 201


@orders_bp.route('/api/orders', methods=['GET'])
def get_orders():
    """查询订单（支持按买家过滤）"""
    buyer = request.args.get('buyer', '').strip()
    q = Order.query
    if buyer:
        q = q.filter(Order.buyer == buyer)
    q = q.order_by(Order.created_at.desc())
    orders = q.all()
    return jsonify({'orders': [o.to_dict() for o in orders]}), 200