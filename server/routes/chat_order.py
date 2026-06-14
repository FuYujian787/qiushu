"""
私聊路由：聊天内一键出价 / 创建订单
"""
import json
import time
from datetime import datetime
from flask import Blueprint, request, jsonify
from db import db
from models import Book, Message

chat_order_bp = Blueprint('chat_order', __name__)

MSG_STATUS_DELIVERED = 'DELIVERED'
USER_BOOK_ID_OFFSET = 100000000


@chat_order_bp.route('/api/chat/order', methods=['POST'])
def create_chat_order():
    """在聊天中创建订单（一键出价/确认交割）"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': '请求体不能为空'}), 400

        sender = (data.get('sender') or '').strip()
        receiver = (data.get('receiver') or '').strip()
        book_id = data.get('book_id')
        price = data.get('price', 0)
        address = (data.get('address') or '').strip()

        if not sender or not receiver or not book_id:
            return jsonify({'success': False, 'message': '参数不完整'}), 400

        order_no = f'ORD{datetime.utcnow().strftime("%Y%m%d%H%M%S")}{int(time.time()) % 10000}'

        if book_id and book_id >= USER_BOOK_ID_OFFSET:
            book_id = book_id - USER_BOOK_ID_OFFSET
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'success': False, 'message': '书籍不存在'}), 404

        system_content = json.dumps({
            'type': 'order_created',
            'orderNo': order_no,
            'bookTitle': book.title,
            'price': price,
            'address': address,
            'status': '待确认',
        }, ensure_ascii=False)

        client_ts = int(time.time() * 1000000)

        msg = Message(
            sender=sender,
            receiver=receiver,
            content=system_content,
            status=MSG_STATUS_DELIVERED,
            client_timestamp=client_ts,
            related_book_id=book_id,
            related_order_no=order_no,
            is_system=True,
        )
        db.session.add(msg)
        db.session.commit()
        db.session.refresh(msg)

        return jsonify({
            'success': True,
            'orderNo': order_no,
            'message': msg.to_dict(include_sender_info=True),
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '创建订单失败: ' + str(e),
        }), 200