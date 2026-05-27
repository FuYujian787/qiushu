"""
书籍路由：列表、详情、分类、推荐 — 从 BookJson 表 + Book 表查询
"""
from flask import Blueprint, request, jsonify
from db import db
from models import Book, BookJson

books_bp = Blueprint('books', __name__)

USER_BOOK_ID_OFFSET = 100000000


@books_bp.route('/api/books/categories', methods=['GET'])
def get_categories():
    """获取分类、筛选条件等配置信息"""
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
    """
    获取书籍列表（分页 + 筛选 + 搜索）
    从 BookJson 表 + Book 表（用户发布）联合查询
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 20, type=int)
    category = request.args.get('category', '').strip()
    query = request.args.get('query', '').strip().lower()

    # 从 BookJson 查询
    json_query = BookJson.query
    if category and category != '全部':
        json_query = json_query.filter(BookJson.category == category)
    if query:
        json_query = json_query.filter(
            db.or_(
                BookJson.title.ilike(f'%{query}%'),
                BookJson.author.ilike(f'%{query}%'),
            )
        )
    total_json = json_query.count()
    json_books = [b.to_dict() for b in json_query.all()]

    # 从 Book 表查询用户发布的书籍
    db_query = Book.query.filter_by(is_user_published=True)
    if category and category != '全部':
        db_query = db_query.filter_by(category=category)
    if query:
        db_query = db_query.filter(
            db.or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
            )
        )
    db_books = [b.to_dict() for b in db_query.all()]
    for b in db_books:
        b['id'] = b['id'] + USER_BOOK_ID_OFFSET

    total = total_json + len(db_books)
    all_books = json_books + db_books

    start = (page - 1) * page_size
    paged = all_books[start:start + page_size]

    return jsonify({
        'books': paged,
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': max(1, (total + page_size - 1) // page_size),
    }), 200


@books_bp.route('/api/books/random', methods=['GET'])
def get_random_books():
    """获取随机推荐书籍（从 BookJson 表）"""
    import random
    count = request.args.get('count', 4, type=int)
    all_ids = [b.id for b in BookJson.query.with_entities(BookJson.id).all()]
    if not all_ids:
        return jsonify({'books': []}), 200
    selected_ids = random.sample(all_ids, min(count, len(all_ids)))
    books = BookJson.query.filter(BookJson.id.in_(selected_ids)).all()
    return jsonify({'books': [b.to_dict() for b in books]}), 200


@books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取单本书籍详情"""
    # 先查数据库（用户发布）
    if book_id >= USER_BOOK_ID_OFFSET:
        real_id = book_id - USER_BOOK_ID_OFFSET
        book = Book.query.get(real_id)
        if book:
            return jsonify({'book': book.to_dict()}), 200
        return jsonify({'success': False, 'message': '书籍不存在'}), 404

    # 查 BookJson 表
    book = BookJson.query.get(book_id)
    if book:
        return jsonify({'book': book.to_dict()}), 200

    # 再查 Book 表（无偏移量）
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'message': '书籍不存在'}), 404
    return jsonify({'book': book.to_dict()}), 200