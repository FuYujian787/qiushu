"""收藏 API"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Favorite, Book
from services.auth import login_required
from services.__init__ import ERROR_CODES

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('', methods=['GET'])
@login_required
def list_favorites():
    """获取当前用户的收藏列表"""
    favorites = Favorite.query.filter_by(user_id=request.current_user_id).all()
    books = []
    for fav in favorites:
        book = Book.query.get(fav.book_id)
        if book:
            books.append(book.to_dict())
    return jsonify({'status': 'success', 'data': books})


@favorites_bp.route('', methods=['POST'])
@login_required
def add_favorite():
    """收藏书籍"""
    data = request.get_json() or {}
    book_id = data.get('book_id', '')

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'status': 'error', 'code': 'BOOK_NOT_FOUND', 'message': ERROR_CODES['BOOK_NOT_FOUND']}), 404

    existing = Favorite.query.filter_by(
        user_id=request.current_user_id,
        book_id=book_id,
    ).first()
    if existing:
        return jsonify({'status': 'success', 'message': '已收藏'})

    fav = Favorite(user_id=request.current_user_id, book_id=book_id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({'status': 'success', 'message': '收藏成功'}), 201


@favorites_bp.route('/<book_id>', methods=['DELETE'])
@login_required
def remove_favorite(book_id):
    """取消收藏"""
    fav = Favorite.query.filter_by(
        user_id=request.current_user_id,
        book_id=book_id,
    ).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()

    return jsonify({'status': 'success', 'message': '已取消收藏'})


@favorites_bp.route('/check/<book_id>', methods=['GET'])
@login_required
def check_favorite(book_id):
    """检查是否已收藏"""
    existing = Favorite.query.filter_by(
        user_id=request.current_user_id,
        book_id=book_id,
    ).first()
    return jsonify({'status': 'success', 'data': {'is_favorited': existing is not None}})
