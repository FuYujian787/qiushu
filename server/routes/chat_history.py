"""
私聊路由：历史消息、对话列表
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_
from db import db
from models import User, Message

chat_history_bp = Blueprint('chat_history', __name__)

MAX_MESSAGE_LIMIT = 50
DEFAULT_MESSAGE_LIMIT = 30


def _get_user_info(user_name):
    """从数据库实时查询用户信息（无缓存）"""
    user = User.query.filter_by(name=user_name).first()
    if user:
        return {
            'college': user.college or '未设置',
            'grade': user.grade or '未知',
            'verified': True,
        }
    return {
        'college': '校友',
        'grade': '未知',
        'verified': False,
    }


@chat_history_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """获取私聊历史消息（增量同步）"""
    try:
        user_a = request.args.get('user_a', '').strip()
        user_b = request.args.get('user_b', '').strip()
        last_timestamp_str = request.args.get('last_timestamp', '0')
        limit = request.args.get('limit', DEFAULT_MESSAGE_LIMIT, type=int)

        if not user_a or not user_b:
            return jsonify({
                'success': False, 'message': '缺少必要参数',
                'messages': [],
            }), 400

        limit = max(1, min(limit, MAX_MESSAGE_LIMIT))

        try:
            last_timestamp = max(0, int(last_timestamp_str))
        except (ValueError, TypeError):
            last_timestamp = 0

        query = Message.query.options(
            joinedload(Message.sender_rel)
        ).filter(
            or_(
                and_(Message.sender == user_a, Message.receiver == user_b),
                and_(Message.sender == user_b, Message.receiver == user_a),
            )
        )

        if last_timestamp > 0:
            query = query.filter(Message.client_timestamp >= last_timestamp)

        query = query.order_by(Message.client_timestamp.asc())
        messages = query.limit(limit).all()

        result = [msg.to_dict(include_sender_info=True) for msg in messages]

        return jsonify({
            'success': True,
            'messages': result,
            'count': len(result),
            'hasMore': len(result) >= limit,
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': '获取聊天记录失败: ' + str(e),
            'messages': [],
        }), 200


@chat_history_bp.route('/api/chat/conversations', methods=['GET'])
def get_conversations():
    """获取用户的对话列表"""
    try:
        user = request.args.get('user', '').strip()
        if not user:
            return jsonify({'success': False, 'message': '缺少参数 user'}), 400

        sent_to = db.session.query(Message.receiver).filter(
            Message.sender == user
        ).distinct().all()

        received_from = db.session.query(Message.sender).filter(
            Message.receiver == user
        ).distinct().all()

        partners = set()
        for (name,) in sent_to:
            partners.add(name)
        for (name,) in received_from:
            partners.add(name)

        conversations = []
        for partner in partners:
            last_msg = Message.query.options(
                joinedload(Message.sender_rel)
            ).filter(
                or_(
                    and_(Message.sender == user, Message.receiver == partner),
                    and_(Message.sender == partner, Message.receiver == user),
                )
            ).order_by(Message.client_timestamp.desc()).first()

            if last_msg:
                unread_count = Message.query.filter(
                    Message.sender == partner,
                    Message.receiver == user,
                    Message.status == 'DELIVERED',
                ).count()

                partner_info = _get_user_info(partner)

                conversations.append({
                    'partner': partner,
                    'partnerInfo': partner_info,
                    'lastMessage': last_msg.to_dict(include_sender_info=False),
                    'unreadCount': unread_count,
                })

        conversations.sort(
            key=lambda c: c['lastMessage'].get('clientTimestamp', 0),
            reverse=True,
        )

        return jsonify({
            'success': True,
            'conversations': conversations,
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': '获取对话列表失败: ' + str(e),
            'conversations': [],
        }), 200