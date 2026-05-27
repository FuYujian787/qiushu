"""
社区操作路由：发布帖子、浏览、点赞、回复
"""
import json
from flask import Blueprint, request, jsonify
from db import db
from models import Post, Reply
from routes.community_helpers import (
    extract_book_titles, match_books_with_titles,
    get_user_info,
)

community_actions_bp = Blueprint('community_actions', __name__)


def _parse_post_id(raw_id):
    """解析帖子ID，支持 'preset_1' 格式"""
    if isinstance(raw_id, str) and raw_id.startswith('preset_'):
        try:
            return int(raw_id.replace('preset_', ''))
        except (ValueError, TypeError):
            return None
    try:
        return int(raw_id)
    except (ValueError, TypeError):
        return None


@community_actions_bp.route('/api/posts/<path:post_id>/view', methods=['POST'])
def increment_view(post_id):
    """增加帖子浏览量"""
    pid = _parse_post_id(post_id)
    if pid is None:
        return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    post = Post.query.get(pid)
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()
    return jsonify({'success': True, 'viewCount': post.view_count}), 200


@community_actions_bp.route('/api/posts/<path:post_id>/like', methods=['POST'])
def like_post(post_id):
    """点赞帖子"""
    pid = _parse_post_id(post_id)
    if pid is None:
        return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    post = Post.query.get(pid)
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404
    post.like_count = (post.like_count or 0) + 1
    db.session.commit()
    return jsonify({'success': True, 'likeCount': post.like_count}), 200


@community_actions_bp.route('/api/posts', methods=['POST'])
def create_post():
    """发布新帖"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    author = (data.get('author') or '').strip()

    if not title:
        return jsonify({'success': False, 'message': '帖子标题不能为空'}), 400
    if not content:
        return jsonify({'success': False, 'message': '帖子内容不能为空'}), 400
    if not author:
        return jsonify({'success': False, 'message': '作者不能为空'}), 400

    all_text = f"{title} {content}"
    detected_titles = extract_book_titles(all_text)
    matched_books = match_books_with_titles(detected_titles)

    post = Post(
        title=title,
        content=content,
        author=author,
        is_preset=False,
        like_count=0,
        view_count=0,
        book_mentions=json.dumps(matched_books, ensure_ascii=False),
    )
    db.session.add(post)
    db.session.commit()

    post_dict = post.to_dict()
    post_dict['authorInfo'] = get_user_info(author)
    post_dict['replyCount'] = 0
    post_dict['replies'] = []
    post_dict['matchedBooks'] = matched_books
    post_dict['hotScore'] = 0.01

    return jsonify({'success': True, 'post': post_dict}), 201


@community_actions_bp.route('/api/posts/<path:post_id>/replies', methods=['POST'])
def add_reply(post_id):
    """回复帖子"""
    pid = _parse_post_id(post_id)
    if pid is None:
        return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    post = Post.query.get(pid)
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    author = (data.get('author') or '').strip()
    content = (data.get('content') or '').strip()

    if not author:
        return jsonify({'success': False, 'message': '作者不能为空'}), 400
    if not content:
        return jsonify({'success': False, 'message': '回复内容不能为空'}), 400

    reply = Reply(post_id=pid, author=author, content=content, like_count=0)
    db.session.add(reply)
    db.session.commit()

    reply_dict = reply.to_dict()
    reply_dict['authorInfo'] = get_user_info(author)
    return jsonify({'success': True, 'reply': reply_dict}), 201


@community_actions_bp.route('/api/posts/<path:post_id>/replies/<int:reply_id>/like', methods=['POST'])
def like_reply(post_id, reply_id):
    """点赞回复"""
    pid = _parse_post_id(post_id)
    if pid is None:
        return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    reply = Reply.query.filter_by(id=reply_id, post_id=pid).first()
    if not reply:
        return jsonify({'success': False, 'message': '回复不存在'}), 404
    reply.like_count = (reply.like_count or 0) + 1
    db.session.commit()
    return jsonify({'success': True, 'likeCount': reply.like_count}), 200