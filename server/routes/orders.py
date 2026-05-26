"""
订单路由：下单、查询
"""
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import db, Order, Book, Notification

orders_bp = Blueprint('orders', __name__)

# 用户发布书籍的 ID 偏移量，必须与 books.py 保持一致
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
        # 如果 book_id 带有偏移量（用户发布书籍），还原为真实数据库 ID
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

        # 如果卖家不是自己，发送通知
        if book.seller and book.seller != buyer:
            notif = Notification(
                user_name=book.seller,
                title='书籍售出通知',
                desc=f'买家 {buyer} 已购买您的书籍《{book.title}》，收货地址：{address}',
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


@orders_bp.route('/api/orders/seller-stats', methods=['GET'])
def seller_stats():
    """
    卖家统计面板数据：
    - total_books_sold: 累计卖出图书总数
    - total_earnings: 累计赚取金额
    根据书籍的 seller 字段聚合已售订单。如果数据为 0 则返回 0。
    """
    seller_name = request.args.get('seller', '').strip()
    if not seller_name:
        return jsonify({'success': False, 'message': 'seller 参数不能为空'}), 400

    # 查找该卖家发布的所有已售订单
    from models import Book
    # 找出 seller 名下的所有书籍
    seller_books = Book.query.filter(Book.seller == seller_name).all()
    seller_book_ids = [b.id for b in seller_books]

    if not seller_book_ids:
        return jsonify({
            'success': True,
            'total_books_sold': 0,
            'total_earnings': 0.00,
        }), 200

    # 统计这些 book_id 的订单（已售 = 订单存在即视为已售）
    from sqlalchemy import func
    stats = db.session.query(
        func.count(Order.id).label('total_sold'),
        func.sum(Order.price).label('total_earnings')
    ).filter(
        Order.book_id.in_(seller_book_ids)
    ).first()

    total_books_sold = stats.total_sold or 0
    total_earnings = round(float(stats.total_earnings or 0), 2)

    return jsonify({
        'success': True,
        'total_books_sold': total_books_sold,
        'total_earnings': total_earnings,
    }), 200
