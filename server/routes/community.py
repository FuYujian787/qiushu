"""
社区路由：帖子列表（热度加权排序 + 分页 + 智能书名联动）
"""
import json
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from db import db
from models import Post
from models import Book
from routes.community_helpers import (
    compute_hot_score, extract_book_titles,
    match_books_with_titles, get_user_info,
)

community_bp = Blueprint('community', __name__)
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@community_bp.route('/api/posts', methods=['GET'])
def get_posts():
    """
    获取帖子列表（热度加权排序 + 分页 + 分类筛选）
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', DEFAULT_PAGE_SIZE, type=int)
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'hot').strip()

    page = max(1, page)
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    query = Post.query.options(joinedload(Post.replies))

    if category and category != '全部':
        category_map = {
            '教材': ['微积分', '线性代数', '高等数学', '大学英语', '有机化学'],
            '考研': ['考研', '政治', '英语', '数学'],
            '选修': ['数据结构', '概率论', '计算机网络', '操作系统',
                     '微观经济学', '宏观经济学'],
        }
        keywords = category_map.get(category, [])
        if keywords:
            filters = [Post.title.ilike(f'%{kw}%') for kw in keywords]
            query = query.filter(db.or_(*filters))

    total = query.count()
    posts = query.order_by(Post.created_at.desc()).all()

    scored_posts = []
    for post in posts:
        reply_count = len(post.replies) if post.replies else 0
        hot_score = compute_hot_score(
            view_count=post.view_count or 0,
            reply_count=reply_count,
            created_at=post.created_at,
        )
        scored_posts.append((post, hot_score, reply_count))

    if sort == 'new':
        scored_posts.sort(key=lambda x: x[0].created_at, reverse=True)
    elif sort == 'top':
        scored_posts.sort(key=lambda x: x[2], reverse=True)
    else:
        scored_posts.sort(key=lambda x: x[1], reverse=True)

    start = (page - 1) * page_size
    end = start + page_size
    page_posts = scored_posts[start:end]

    result = []
    for post, hot_score, reply_count in page_posts:
        post_dict = post.to_dict()
        post_dict['hotScore'] = round(hot_score, 4)
        post_dict['replyCount'] = reply_count
        post_dict['authorInfo'] = get_user_info(post.author)

        replies = post.replies or []
        post_dict['replies'] = [r.to_dict() for r in replies]

        all_text = f"{post.title} {post.content}"
        detected_titles = extract_book_titles(all_text)
        matched_books = match_books_with_titles(detected_titles)
        post_dict['matchedBooks'] = matched_books

        if matched_books:
            post.book_mentions = json.dumps(matched_books, ensure_ascii=False)
        result.append(post_dict)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({
        'posts': result,
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': max(1, (total + page_size - 1) // page_size),
    }), 200


@community_bp.route('/api/posts/books/search', methods=['GET'])
def search_books_for_post():
    """根据书名搜索在售书籍（供前端 Popover 调用）"""
    title = request.args.get('title', '').strip()
    if not title:
        return jsonify({'books': []}), 200
    books = Book.query.filter(
        Book.title.ilike(f'%{title}%')
    ).limit(10).all()
    return jsonify({
        'books': [{
            'id': b.id, 'title': b.title, 'price': round(b.price, 1),
            'condition': b.condition, 'seller': b.seller, 'img': b.img,
        } for b in books]
    }), 200