"""
书籍路由：列表、详情、发布、分类信息
支持从本地 JSON 文件加载 10 万级虚拟商品数据（Promise 方式）
"""
import json
import os
import uuid
from flask import Blueprint, request, jsonify
from models import db, Book

books_bp = Blueprint('books', __name__)

# 用户发布书籍的 ID 偏移量，避免与 JSON 书籍 ID 冲突
USER_BOOK_ID_OFFSET = 100000000

# JSON 数据文件路径（位于 client/public/data/books.json）
JSON_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'client', 'public', 'data', 'books.json'
)

# 缓存：首次加载后驻留内存，避免重复磁盘 I/O
_json_books_cache = None
_json_books_total = 0


def _load_json_books():
    """加载 JSON 文件中的书籍数据（惰性加载 + 缓存）"""
    global _json_books_cache, _json_books_total
    if _json_books_cache is not None:
        return _json_books_cache
    if not os.path.exists(JSON_DATA_PATH):
        _json_books_cache = []
        _json_books_total = 0
        return _json_books_cache
    with open(JSON_DATA_PATH, 'r', encoding='utf-8') as f:
        _json_books_cache = json.load(f)
    _json_books_total = len(_json_books_cache)
    return _json_books_cache


@books_bp.route('/api/books/categories', methods=['GET'])
def get_categories():
    """获取分类、筛选条件、首页展示数据等配置信息"""
    subjects = ['微积分', '线性代数', '大学英语', '有机化学', '数据结构',
                '概率论', '计算机网络', '操作系统', '高等数学', '考研政治',
                '微观经济学', '宏观经济学']
    conditions = ['九成新', '八成新', '全新未拆', '有笔记', '七成新']
    category_map = {
        '微积分': '教材', '线性代数': '教材', '大学英语': '教材', '有机化学': '教材',
        '数据结构': '选修', '概率论': '选修', '计算机网络': '选修', '操作系统': '选修',
        '高等数学': '教材', '考研政治': '考研', '微观经济学': '选修', '宏观经济学': '选修',
    }
    smart_books = [
        {'name': '微积分（上册）', 'matchCount': 20000},
        {'name': '线性代数（上册）', 'matchCount': 16666},
        {'name': '有机化学（上册）', 'matchCount': 8333},
    ]
    home_publishers = [
        {'name': '高教社', 'icon': 'mdi:school', 'color': 'purple'},
        {'name': '科学社', 'icon': 'mdi:microscope', 'color': 'blue'},
        {'name': '浙大出版社', 'icon': 'mdi:university', 'color': 'red'},
        {'name': '更多', 'icon': 'mdi:dots-horizontal', 'color': 'gray'},
    ]

    return jsonify({
        'subjects': subjects,
        'conditions': conditions,
        'categoryMap': category_map,
        'filterChips': ['全部', '教材', '考研', '选修'],
        'smartBooks': smart_books,
        'homePublishers': home_publishers,
    }), 200


@books_bp.route('/api/books', methods=['GET'])
def get_books():
    """获取书籍列表（支持分页、筛选、搜索）—— 从 JSON 文件 + 数据库（用户发布）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    category = request.args.get('category', '').strip()
    query = request.args.get('query', '').strip().lower()

    # 1. 从 JSON 文件加载系统书籍
    json_books = _load_json_books()

    # 2. 从数据库加载用户发布的书籍
    db_query = Book.query.filter_by(is_user_published=True)
    if category and category != '全部':
        db_query = db_query.filter_by(category=category)
    if query:
        db_query = db_query.filter(
            db.or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%')
            )
        )
    db_books = [b.to_dict() for b in db_query.all()]

    # 3. 对用户发布的书籍 ID 进行偏移，避免与 JSON 书籍 ID 冲突
    for b in db_books:
        b['id'] = b['id'] + USER_BOOK_ID_OFFSET

    # 4. 合并
    all_books = json_books + db_books

    # 筛选（JSON 部分需要筛选）
    filtered = all_books
    if category and category != '全部':
        filtered = [b for b in filtered if b.get('category') == category]
    if query:
        filtered = [
            b for b in filtered
            if query in b.get('title', '').lower() or query in b.get('author', '').lower()
        ]

    total = len(filtered)
    # 分页
    start = (page - 1) * page_size
    paged = filtered[start:start + page_size]

    return jsonify({
        'books': paged,
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': max(1, (total + page_size - 1) // page_size),
    }), 200


@books_bp.route('/api/books/user-books', methods=['GET'])
def get_user_books():
    """获取指定卖家发布的书籍（从数据库）"""
    seller = request.args.get('seller', '').strip()
    if not seller:
        return jsonify({'success': False, 'message': '缺少卖家参数'}), 400
    books = Book.query.filter_by(is_user_published=True, seller=seller).all()
    return jsonify({'books': [b.to_dict() for b in books]}), 200


@books_bp.route('/api/books/random', methods=['GET'])
def get_random_books():
    """获取随机推荐书籍（从 JSON 文件）"""
    import random
    count = request.args.get('count', 4, type=int)
    all_books = _load_json_books()
    if not all_books:
        return jsonify({'books': []}), 200
    selected = random.sample(all_books, min(count, len(all_books)))
    return jsonify({'books': selected}), 200


@books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取单本书籍详情（先查数据库用户发布，再查 JSON 文件）"""
    # 先查数据库（用户发布的书籍）
    if book_id >= USER_BOOK_ID_OFFSET:
        # 带偏移量的 ID：从数据库查找
        real_id = book_id - USER_BOOK_ID_OFFSET
        book = Book.query.get(real_id)
        if book:
            return jsonify({'book': book.to_dict()}), 200
        return jsonify({'success': False, 'message': '书籍不存在'}), 404

    # 查 JSON 文件
    all_books = _load_json_books()
    for b in all_books:
        if b.get('id') == book_id:
            return jsonify({'book': b}), 200

    # 也查一下数据库（用户发布的书籍，无偏移量）
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'message': '书籍不存在'}), 404
    return jsonify({'book': book.to_dict()}), 200


@books_bp.route('/api/books', methods=['POST'])
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


