"""
书籍发布路由：上架书籍、查询卖家发布
"""
from flask import Blueprint, request, jsonify
from db import db
from models import Book

books_publish_bp = Blueprint('books_publish', __name__)


@books_publish_bp.route('/api/books/user-books', methods=['GET'])
def get_user_books():
    """获取指定卖家发布的书籍"""
    seller = request.args.get('seller', '').strip()
    if not seller:
        return jsonify({'success': False, 'message': '缺少卖家参数'}), 400
    books = Book.query.filter_by(is_user_published=True, seller=seller).all()
    return jsonify({'books': [b.to_dict() for b in books]}), 200


@books_publish_bp.route('/api/books', methods=['POST'])
def publish_book():
    """用户发布闲置书籍"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    title = (data.get('title') or '').strip()
    price = data.get('price')
    publisher = (data.get('publisher') or '').strip()
    condition = (data.get('condition') or '').strip()
    seller = (data.get('seller') or '').strip()

    if not title:
        return jsonify({'success': False, 'message': '书名不能为空'}), 400
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        return jsonify({'success': False, 'message': '价格必须为正数'}), 400
    if not publisher:
        return jsonify({'success': False, 'message': '出版社不能为空'}), 400
    if not condition:
        return jsonify({'success': False, 'message': '成色不能为空'}), 400

    old_price = data.get('oldPrice')
    if old_price is None:
        old_price = round(float(price) * 1.5, 1)
    else:
        old_price = round(float(old_price), 1)

    book = Book(
        title=title,
        author=publisher,
        price=round(float(price), 1),
        old_price=old_price,
        condition=condition,
        seller=seller or '匿名',
        img=str(data.get('img') or 'R-C.jpg'),
        category=str(data.get('category') or '教材'),
        is_user_published=True,
        alipay_qr=data.get('alipayQr'),
        wechat_qr=data.get('wechatQr'),
    )
    db.session.add(book)
    db.session.commit()

    return jsonify({'success': True, 'book': book.to_dict()}), 201