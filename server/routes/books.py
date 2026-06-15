"""书籍 API（CRUD + 图片上传 + 评论 + 旅程）"""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db, limiter
from models import Book, BookImage, Review, BookJourney
from services.auth import login_required

from services.__init__ import ERROR_CODES

books_bp = Blueprint('books', __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/webp',
}
# Magic bytes for image type detection
IMAGE_MAGIC_BYTES = {
    b'\xff\xd8\xff': 'image/jpeg',  # JPEG
    b'\x89PNG\r\n\x1a\n': 'image/png',  # PNG
    b'RIFF': 'image/webp',  # WebP (needs further check for WEBP)
}


def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image_content(file_bytes):
    """通过 magic bytes 验证文件真实类型"""
    if not file_bytes:
        return False
    if file_bytes[:3] == b'\xff\xd8\xff':
        return True  # JPEG
    if file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return True  # PNG
    # WebP: RIFF....WEBP
    if file_bytes[:4] == b'RIFF' and len(file_bytes) >= 12 and file_bytes[8:12] == b'WEBP':
        return True
    return False


@books_bp.route('', methods=['GET'])
def list_books():
    """获取书籍列表（支持分页、搜索、筛选）"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    condition = request.args.get('condition', '').strip()
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')

    # 排序字段白名单校验
    ALLOWED_SORT_FIELDS = {'created_at', 'price', 'original_price', 'title', 'condition'}
    if sort not in ALLOWED_SORT_FIELDS:
        sort = 'created_at'

    # 展示「在售」和「预定了」的书籍，「已售」和「下架」的不出现
    book_query = Book.query.filter(Book.status.in_(['在售', '预定了']))

    if query:
        like_q = f'%{query}%'
        book_query = book_query.filter(
            db.or_(Book.title.like(like_q), Book.author.like(like_q))
        )
    if category:
        book_query = book_query.filter(Book.category == category)
    if condition:
        book_query = book_query.filter(Book.condition == condition)
    if price_min is not None:
        book_query = book_query.filter(Book.price >= price_min)
    if price_max is not None:
        book_query = book_query.filter(Book.price <= price_max)

    # 排序
    sort_column = getattr(Book, sort, Book.created_at)
    if order == 'asc':
        book_query = book_query.order_by(sort_column.asc())
    else:
        book_query = book_query.order_by(sort_column.desc())

    pagination = book_query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'status': 'success',
        'data': {
            'books': [book.to_dict() for book in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        },
    })


@books_bp.route('/<book_id>', methods=['GET'])
def get_book(book_id):
    """获取书籍详情"""
    book = Book.query.get(book_id)
    if not book or book.status in ('下架', '已售'):
        return jsonify({'status': 'error', 'code': 'BOOK_NOT_FOUND', 'message': ERROR_CODES['BOOK_NOT_FOUND']}), 404

    result = book.to_dict()

    # 卖家其他在售书籍
    other_books = Book.query.filter(
        Book.user_id == book.user_id,
        Book.id != book.id,
        Book.status == '在售',
    ).limit(5).all()
    result['seller_other_books'] = [b.to_dict() for b in other_books]

    # 评价
    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
    result['reviews'] = [r.to_dict() for r in reviews]

    # 旅程
    journeys = BookJourney.query.filter_by(book_id=book_id).order_by(BookJourney.created_at.asc()).all()
    result['journeys'] = [j.to_dict() for j in journeys]

    return jsonify({'status': 'success', 'data': result})


@books_bp.route('', methods=['POST'])
@login_required
def create_book():
    """发布书籍"""
    data = request.form.to_dict() if request.form else request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'status': 'error', 'code': 'BOOK_NOT_FOUND', 'message': '请输入书名'}), 400

    book = Book(
        user_id=request.current_user_id,
        title=title,
        author=data.get('author', '').strip(),
        isbn=data.get('isbn', '').strip(),
        category=data.get('category', '').strip(),
        original_price=float(data['original_price']) if data.get('original_price') else None,
        price=float(data['price']) if data.get('price') else 0,
        condition=data.get('condition', '良好'),
        description=data.get('description', '').strip(),
        accept_exchange=data.get('accept_exchange', 'false') in ('true', '1', True, 1),
    )
    db.session.add(book)
    db.session.flush()

    # 处理图片上传（含真实 MIME 类型验证）
    if request.files:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        files = request.files.getlist('images')
        for idx, file in enumerate(files[:5]):  # 最多 5 张
            if file and allowed_file(file.filename):
                # 读取文件内容进行 magic bytes 验证
                file_bytes = file.read()
                file.seek(0)  # 重置指针
                if not validate_image_content(file_bytes):
                    continue  # 跳过非图片文件
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4()}.{ext}"
                file.save(os.path.join(upload_folder, filename))
                img = BookImage(
                    book_id=book.id,
                    url=f'/static/uploads/{filename}',
                    is_cover=(idx == 0),
                    sort_order=idx,
                )
                db.session.add(img)

    # 记录旅程
    journey = BookJourney(
        book_id=book.id,
        from_user_id=request.current_user_id,
        event_type='初次上架',
        note='书籍首次发布',
    )
    db.session.add(journey)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': book.to_dict(),
        'message': '发布成功',
    }), 201


@books_bp.route('/<book_id>', methods=['PUT'])
@login_required
def update_book(book_id):
    """更新书籍"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'status': 'error', 'code': 'BOOK_NOT_FOUND', 'message': ERROR_CODES['BOOK_NOT_FOUND']}), 404
    if book.user_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'BOOK_PERMISSION_DENIED', 'message': ERROR_CODES['BOOK_PERMISSION_DENIED']}), 403

    data = request.get_json() or {}
    old_status = book.status
    for field in ['title', 'author', 'isbn', 'category', 'condition', 'description', 'status']:
        if field in data:
            setattr(book, field, data[field])
    if 'accept_exchange' in data:
        book.accept_exchange = data['accept_exchange'] in (True, 'true', '1', 1)
    if 'price' in data:
        book.price = float(data['price'])
    if 'original_price' in data and data['original_price']:
        book.original_price = float(data['original_price'])

    # 当状态从「已售」改为「在售」时，记录再次上架事件
    if old_status == '已售' and book.status == '在售':
        journey = BookJourney(
            book_id=book.id,
            from_user_id=request.current_user_id,
            event_type='再次上架',
            note='书籍重新上架出售',
        )
        db.session.add(journey)

    db.session.commit()
    return jsonify({'status': 'success', 'data': book.to_dict(), 'message': '更新成功'})


@books_bp.route('/<book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    """下架书籍"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'status': 'error', 'code': 'BOOK_NOT_FOUND', 'message': ERROR_CODES['BOOK_NOT_FOUND']}), 404
    if book.user_id != request.current_user_id:
        return jsonify({'status': 'error', 'code': 'BOOK_PERMISSION_DENIED', 'message': ERROR_CODES['BOOK_PERMISSION_DENIED']}), 403

    book.status = '下架'
    db.session.commit()
    return jsonify({'status': 'success', 'message': '已下架'})


@books_bp.route('/<book_id>/reviews', methods=['POST'])
@login_required
def add_review(book_id):
    """添加评价"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'status': 'error', 'code': 'BOOK_NOT_FOUND', 'message': ERROR_CODES['BOOK_NOT_FOUND']}), 404

    data = request.get_json() or {}
    review = Review(
        book_id=book_id,
        order_id=data.get('order_id'),
        user_id=request.current_user_id,
        rating=data.get('rating', 5),
        comment=data.get('comment', '').strip(),
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({'status': 'success', 'data': review.to_dict(), 'message': '评价成功'}), 201


@books_bp.route('/<book_id>/journey', methods=['GET'])
def get_book_journey(book_id):
    """获取书籍旅程"""
    journeys = BookJourney.query.filter_by(book_id=book_id).order_by(BookJourney.created_at.asc()).all()
    return jsonify({
        'status': 'success',
        'data': [j.to_dict() for j in journeys],
    })
