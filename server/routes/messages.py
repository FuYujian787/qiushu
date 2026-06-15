"""私信 API（会话列表 → 聊天窗口 → 消息收发 → 图片上传 → 订单卡片）"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db, limiter
from models import Conversation, Message, User, Order
from services.auth import login_required
from services.__init__ import ERROR_CODES

messages_bp = Blueprint('messages', __name__)

# 图片上传配置
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
ALLOWED_IMAGE_MIME = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def _validate_image(file_bytes):
    """通过 magic bytes 验证图片真实类型"""
    if not file_bytes or len(file_bytes) < 4:
        return False
    if file_bytes[:3] == b'\xff\xd8\xff':
        return True  # JPEG
    if file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return True  # PNG
    if file_bytes[:4] == b'RIFF' and len(file_bytes) >= 12 and file_bytes[8:12] == b'WEBP':
        return True  # WebP
    if file_bytes[:6] in (b'GIF89a', b'GIF87a'):
        return True  # GIF
    return False


@messages_bp.route('/conversations', methods=['GET'])
@login_required
@limiter.limit('120 per minute')
def list_conversations():
    """获取当前用户的所有会话（按最后消息时间倒序）"""
    user_id = request.current_user_id

    conversations = Conversation.query.filter(
        db.or_(
            Conversation.user1_id == user_id,
            Conversation.user2_id == user_id,
        )
    ).order_by(
        Conversation.last_message_at.desc().nullslast(),
        Conversation.created_at.desc(),
    ).all()

    # 为每个会话附加对方用户信息和未读数
    result = []
    for conv in conversations:
        data = conv.to_dict()
        # 对方用户信息
        if conv.user1_id == user_id:
            data['peer_id'] = conv.user2_id
            data['peer_name'] = conv.user2.nickname if conv.user2 else '书友'
            data['peer_avatar'] = conv.user2.avatar if conv.user2 else None
        else:
            data['peer_id'] = conv.user1_id
            data['peer_name'] = conv.user1.nickname if conv.user1 else '书友'
            data['peer_avatar'] = conv.user1.avatar if conv.user1 else None

        # 未读消息数
        unread = Message.query.filter_by(
            conversation_id=conv.id,
            sender_id=data['peer_id'],  # 对方发的
            is_read=False,
        ).count()
        data['unread_count'] = unread
        result.append(data)

    return jsonify({
        'status': 'success',
        'data': result,
    })


@messages_bp.route('/conversations', methods=['POST'])
@login_required
@limiter.limit('30 per minute')
def create_conversation():
    """创建或获取已有会话"""
    data = request.get_json() or {}
    peer_id = data.get('user_id', '').strip()
    order_id = data.get('order_id', '').strip() or None
    book_id = data.get('book_id', '').strip() or None

    if not peer_id:
        return jsonify({'status': 'error', 'code': 'USER_NOT_FOUND', 'message': '请指定对方用户'}), 400

    if peer_id == request.current_user_id:
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '不能和自己聊天'}), 400

    # 验证对方用户存在
    peer = User.query.get(peer_id)
    if not peer:
        return jsonify({'status': 'error', 'code': 'USER_NOT_FOUND', 'message': '用户不存在'}), 404

    user_id = request.current_user_id
    u1, u2 = sorted([user_id, peer_id])

    # 🔧 同一对用户只保留一个会话，不按 order_id 分裂
    # 先查找两人之间是否已有会话（忽略 order_id/book_id）
    conv = Conversation.query.filter(
        db.or_(
            db.and_(Conversation.user1_id == u1, Conversation.user2_id == u2),
            db.and_(Conversation.user1_id == u2, Conversation.user2_id == u1),
        )
    ).first()

    if conv:
        # 已有会话：如果提供了新的上下文信息，更新之
        updated = False
        if order_id and not conv.order_id:
            conv.order_id = order_id
            updated = True
        if book_id and not conv.book_id:
            conv.book_id = book_id
            updated = True
        if updated:
            db.session.commit()
        return jsonify({'status': 'success', 'data': conv.to_dict(), 'message': '会话已存在'})

    # 创建新会话
    conv = Conversation(
        user1_id=u1,
        user2_id=u2,
        order_id=order_id,
        book_id=book_id,
    )
    db.session.add(conv)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': conv.to_dict(),
        'message': '会话已创建',
    }), 201


@messages_bp.route('/conversations/<conv_id>', methods=['GET'])
@login_required
@limiter.limit('120 per minute')
def get_messages(conv_id):
    """获取某个会话的消息列表（分页）"""
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': '会话不存在'}), 404

    # 权限检查
    if request.current_user_id not in (conv.user1_id, conv.user2_id):
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权查看此会话'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)

    pagination = Message.query.filter_by(conversation_id=conv_id).order_by(
        Message.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    messages_list = [m.to_dict() for m in reversed(pagination.items)]

    return jsonify({
        'status': 'success',
        'data': {
            'conversation': conv.to_dict(),
            'messages': messages_list,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        },
    })


@messages_bp.route('', methods=['POST'])
@login_required
@limiter.limit('60 per minute')
def send_message():
    """发送消息（支持 text / image / order_card 三种类型）"""
    data = request.get_json() or {}
    conversation_id = data.get('conversation_id', '').strip()
    msg_type = data.get('message_type', 'text').strip()
    content = (data.get('content') or '').strip()
    image_url = (data.get('image_url') or '').strip()

    # 验证会话
    if not conversation_id:
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '请指定会话'}), 400

    conv = Conversation.query.get(conversation_id)
    if not conv:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': '会话不存在'}), 404

    if request.current_user_id not in (conv.user1_id, conv.user2_id):
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权在此会话发送消息'}), 403

    # 按类型验证
    if msg_type == 'text':
        if not content:
            return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '请输入消息内容'}), 400
        if len(content) > 2000:
            return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '消息内容过长（最多2000字）'}), 400
        preview = content[:200]
    elif msg_type == 'image':
        if not image_url:
            return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '请上传图片'}), 400
        content = content or ''  # 可选图片说明
        preview = '[图片]'
    elif msg_type == 'order_card':
        if not content:
            return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '缺少订单数据'}), 400
        preview = '[订单卡片]'
    else:
        return jsonify({'status': 'error', 'code': 'ORDER_STATUS_INVALID', 'message': '不支持的消息类型'}), 400

    msg = Message(
        conversation_id=conversation_id,
        sender_id=request.current_user_id,
        content=content,
        message_type=msg_type,
        image_url=image_url or None,
    )
    db.session.add(msg)

    # 更新会话最后消息预览
    conv.last_message = preview
    conv.last_message_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': msg.to_dict(),
        'message': '发送成功',
    }), 201


@messages_bp.route('/upload-image', methods=['POST'])
@login_required
@limiter.limit('30 per minute')
def upload_image():
    """上传聊天图片"""
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'code': 'UPLOAD_FORMAT_INVALID', 'message': '请选择图片'}), 400

    file = request.files['image']
    if not file or not file.filename:
        return jsonify({'status': 'error', 'code': 'UPLOAD_FORMAT_INVALID', 'message': '请选择图片'}), 400

    # 检查扩展名
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return jsonify({'status': 'error', 'code': 'UPLOAD_FORMAT_INVALID', 'message': '仅支持 JPG、PNG、WebP、GIF 格式'}), 400

    # 检查大小
    file_bytes = file.read()
    file.seek(0)
    if len(file_bytes) > MAX_IMAGE_SIZE:
        return jsonify({'status': 'error', 'code': 'UPLOAD_SIZE_EXCEEDED', 'message': '图片大小不能超过 5MB'}), 400

    # Magic bytes 验证
    if not _validate_image(file_bytes):
        return jsonify({'status': 'error', 'code': 'UPLOAD_FORMAT_INVALID', 'message': '文件不是有效的图片'}), 400

    # 保存到 chat 子目录
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chat')
    os.makedirs(upload_folder, exist_ok=True)

    filename = f"{uuid.uuid4()}.{ext}"
    file.save(os.path.join(upload_folder, filename))

    url = f'/static/uploads/chat/{filename}'
    return jsonify({
        'status': 'success',
        'data': {'url': url},
        'message': '上传成功',
    }), 201


@messages_bp.route('/order-card/<order_id>', methods=['GET'])
@login_required
@limiter.limit('30 per minute')
def get_order_card(order_id):
    """获取订单卡片数据（用于发送订单卡片消息）"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': '订单不存在'}), 404

    if request.current_user_id not in (order.buyer_id, order.seller_id):
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权查看此订单'}), 403

    return jsonify({
        'status': 'success',
        'data': {
            'order_id': order.id,
            'book_title': order.book.title if order.book else None,
            'book_price': order.book.price if order.book else None,
            'status': order.status,
            'buyer_name': order.buyer.nickname if order.buyer else None,
            'seller_name': order.seller_rel.nickname if order.seller_rel else None,
            'created_at': order.created_at.isoformat() if order.created_at else None,
        },
    })


@messages_bp.route('/conversations/<conv_id>/read', methods=['PUT'])
@login_required
@limiter.limit('120 per minute')
def mark_read(conv_id):
    """将会话中所有对方发来的消息标记为已读"""
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({'status': 'error', 'code': 'ORDER_NOT_FOUND', 'message': '会话不存在'}), 404

    if request.current_user_id not in (conv.user1_id, conv.user2_id):
        return jsonify({'status': 'error', 'code': 'AUTH_PERMISSION_DENIED', 'message': '无权操作此会话'}), 403

    # Mark all messages from the other person as read
    updated = Message.query.filter_by(
        conversation_id=conv_id,
        is_read=False,
    ).filter(
        Message.sender_id != request.current_user_id
    ).update({'is_read': True})

    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': {'updated': updated},
        'message': f'已标记 {updated} 条消息为已读',
    })


@messages_bp.route('/unread-count', methods=['GET'])
@login_required
@limiter.limit('60 per minute')
def unread_count():
    """获取当前用户的总未读消息数"""
    user_id = request.current_user_id

    # 找到用户参与的所有会话
    conv_ids = db.session.query(Conversation.id).filter(
        db.or_(
            Conversation.user1_id == user_id,
            Conversation.user2_id == user_id,
        )
    ).all()
    conv_ids = [c[0] for c in conv_ids]

    if not conv_ids:
        return jsonify({'status': 'success', 'data': {'count': 0}})

    count = Message.query.filter(
        Message.conversation_id.in_(conv_ids),
        Message.sender_id != user_id,
        Message.is_read == False,  # noqa: E712
    ).count()

    return jsonify({'status': 'success', 'data': {'count': count}})
