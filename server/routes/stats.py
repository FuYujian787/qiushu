"""
卖家统计路由：仪表盘数据聚合
"""
from flask import Blueprint, request, jsonify
from db import db
from models import Order, Book

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/api/orders/seller-stats', methods=['GET'])
def seller_stats():
    """
    卖家统计面板数据
    - 零数据时优雅返回 0，不会崩溃
    """
    seller_name = request.args.get('seller', '').strip()
    if not seller_name:
        return jsonify({'success': False, 'message': 'seller 参数不能为空'}), 400

    seller_books = Book.query.filter(Book.seller == seller_name).all()
    seller_book_ids = [b.id for b in seller_books]

    if not seller_book_ids:
        return jsonify({
            'success': True,
            'total_books_sold': 0,
            'total_earnings': 0.00,
        }), 200

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