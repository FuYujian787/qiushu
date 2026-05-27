"""
私聊路由：发送消息、标记已读
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from db import db
from models import User, Message

chat_send_read_bp = Blueprint('chat_send_read', __name__)

MSG_STATUS_DELIVERED = 'DELIVERED'
MSG_STATUS_READ = 'READ'


@chat_send_read_bp.route('/api/chat/send', methods=['POST'])
def send_message():
    """发送私聊消息"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': '请求体不能为空'}), 400

        sender = (data.get('sender') or '').strip()
        receiver = (data.get('receiver') or '').strip()
        content = (data.get('content') or '').strip()
        client_timestamp = data.get('client_timestamp', 0)
        related_book_id = data.get('related_book_id')
        related_order_no = data.get('related_order_no')
        is_system = data.get('is_system', False)

        if not sender:
            return jsonify({'success': False, 'message': '发送者不能为空'}), 400
        if not receiver:
            return jsonify({'success': False, 'message': '接收者不能为空'}), 400
        if not content:
            return jsonify({'success': False, 'message': '消息内容不能为空'}), 400
        if sender == receiver:
            return jsonify({'success': False, 'message': '不能给自己发送消息'}), 400
        if len(content) > 5000:
            return jsonify({'success': False, 'message': '消息内容过长（最大 5000 字符）'}), 400

        if not User.query.filter_by(name=sender).first():
            return jsonify({'success': False, 'message': '发送者不存在'}), 400
        if not User.query.filter_by(name=receiver).first():
            return jsonify({'success': False, 'message': '接收者不存在'}), 400

        msg = Message(
            sender=sender,
            receiver=receiver,
            content=content,
            status=MSG_STATUS_DELIVERED,
            client_timestamp=client_timestamp,
            related_book_id=related_book_id,
            related_order_no=related_order_no,
            is_system=is_system,
        )
        db.session.add(msg)
        db.session.commit()
        db.session.refresh(msg)

        return jsonify({
            'success': True,
            'message': msg.to_dict(include_sender_info=True),
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '发送消息失败: ' + str(e),
        }), 200


@chat_send_read_bp.route('/api/chat/read', methods=['POST'])
def mark_as_read():
    """标记为已读"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': '请求体不能为空'}), 400

        reader = (data.get('reader') or '').strip()
        sender = (data.get('sender') or '').strip()

        if not reader or not sender:
            return jsonify({'success': False, 'message': '参数不完整'}), 400

        count = Message.query.filter(
            Message.sender == sender,
            Message.receiver == reader,
            Message.status == MSG_STATUS_DELIVERED,
        ).update({Message.status: MSG_STATUS_READ})

        db.session.commit()

        return jsonify({'success': True, 'markedCount': count}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '标记已读失败: ' + str(e),
        }), 200