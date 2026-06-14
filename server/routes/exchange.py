"""以书换书 API（零现金交易模式）"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Book, WantedBook
from services.auth import login_required

exchange_bp = Blueprint('exchange', __name__)


@exchange_bp.route('', methods=['GET'])
def list_exchange_books():
    """获取可换书列表（支持分页、搜索、类型筛选）

    查询参数:
        - page: 页码（默认 1）
        - per_page: 每页条数（默认 20，最大 100）
        - q: 搜索关键词（匹配书名/作者）
        - category: 分类筛选
        - condition: 书况筛选
        - min_price / max_price: 价格区间
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    condition = request.args.get('condition', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    book_query = Book.query.filter(
        Book.status == '在售',
        Book.accept_exchange == True,
    )

    if query:
        like_q = f'%{query}%'
        book_query = book_query.filter(
            db.or_(Book.title.like(like_q), Book.author.like(like_q))
        )
    if category:
        book_query = book_query.filter(Book.category == category)
    if condition:
        book_query = book_query.filter(Book.condition == condition)
    if min_price is not None:
        book_query = book_query.filter(Book.price >= min_price)
    if max_price is not None:
        book_query = book_query.filter(Book.price <= max_price)

    book_query = book_query.order_by(Book.created_at.desc())
    pagination = book_query.paginate(page=page, per_page=per_page, error_out=False)

    # 获取所有求购帖，用于匹配标记
    wanted_books = WantedBook.query.filter_by(status='求购中').all()
    wanted_titles = {wb.title.lower() for wb in wanted_books}

    books_with_match = []
    for book in pagination.items:
        book_dict = book.to_dict()
        # 标记是否与求购帖匹配
        book_dict['has_wanted_match'] = book.title.lower() in wanted_titles
        books_with_match.append(book_dict)

    return jsonify({
        'status': 'success',
        'data': {
            'books': books_with_match,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
        },
    })


@exchange_bp.route('/toggle/<book_id>', methods=['POST'])
@login_required
def toggle_exchange(book_id):
    """切换书籍的「接受交换」状态"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'status': 'error', 'message': '书籍不存在'}), 404
    if book.user_id != request.current_user_id:
        return jsonify({'status': 'error', 'message': '只能操作自己发布的书籍'}), 403

    book.accept_exchange = not book.accept_exchange
    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': {
            'book_id': book.id,
            'accept_exchange': book.accept_exchange,
        },
        'message': f'已{"开启" if book.accept_exchange else "关闭"}以书换书',
    })


@exchange_bp.route('/matches', methods=['GET'])
def get_matches():
    """获取换书匹配列表（在售换书 vs 求购帖的交集）"""
    # 所有接受交换的在售书
    exchange_books = Book.query.filter(
        Book.status == '在售',
        Book.accept_exchange == True,
    ).all()

    # 所有求购中的帖子
    wanted_books = WantedBook.query.filter_by(status='求购中').all()

    matches = []
    seen_pairs = set()

    for book in exchange_books:
        for wanted in wanted_books:
            # 模糊匹配：书名包含关键词
            if (wanted.title.lower() in book.title.lower() or
                    book.title.lower() in wanted.title.lower()):
                pair_key = (book.id, wanted.id)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    matches.append({
                        'book': book.to_dict(),
                        'wanted': wanted.to_dict(),
                        'match_score': 'exact' if book.title.lower() == wanted.title.lower() else 'partial',
                    })

    # 按匹配度排序（精确匹配优先）
    matches.sort(key=lambda m: 0 if m['match_score'] == 'exact' else 1)

    return jsonify({
        'status': 'success',
        'data': {
            'matches': matches,
            'total': len(matches),
        },
    })


@exchange_bp.route('/my', methods=['GET'])
@login_required
def my_exchange_books():
    """获取当前用户接受交换的书籍列表"""
    books = Book.query.filter_by(
        user_id=request.current_user_id,
        status='在售',
    ).order_by(Book.created_at.desc()).all()

    return jsonify({
        'status': 'success',
        'data': {
            'books': [b.to_dict() for b in books],
            'exchange_enabled': [b.to_dict() for b in books if b.accept_exchange],
        },
    })
