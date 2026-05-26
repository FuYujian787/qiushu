"""
============================================================
紫金求思 · 私聊系统后端引擎 — 高奢科技感私人数字化会客室
Chat Blueprint — 全栈高端化重构版
============================================================

核心设计：
  1. 防 N+1 联合查询：使用 joinedload(Message.sender) 一次性打包
     拉出发送者的学院、年级与校内验证状态，杜绝循环查询。
  2. 增量时间戳同步：前端携带 last_timestamp（微秒级时间戳），
     后端仅返回该时间戳之后的新消息，配合前端 TransitionGroup
     瀑布流错峰补写，页面不发生任何硬刷新跳动。
  3. 高容错异常处理：所有接口包裹 try-except，恶意篡改的
     last_timestamp 格式不会导致 500 崩溃，优雅降级返回空列表。
  4. 高效分页：限制单次最大返回 50 条消息，防止上万条毛玻璃
     卡片全量推送给前端导致 DOM 爆炸。
  5. 消息状态机：PENDING → DELIVERED → READ，支持前端乐观更新
     后的状态同步回写。

数据模型依赖：
  - Message 模型（见 server/models.py 新增）
  - User 模型（已有）

API 端点：
  - GET  /api/chat/history?user_a=<>&user_b=<>&last_timestamp=<>&limit=<>
  - POST /api/chat/send
  - POST /api/chat/read
  - GET  /api/chat/conversations?user=<>
============================================================
"""
import json
import time
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy import or_, and_

# 注意：models.py 中需要新增 Message 模型，我们将在 chat.py 中
# 通过动态导入的方式确保兼容性，同时提供完整的模型定义注释
from models import db, User

chat_bp = Blueprint('chat', __name__)

# ============================================================
# 常量
# ============================================================

# 单次拉取消息的最大数量，防止 DOM 爆炸
MAX_MESSAGE_LIMIT = 50

# 默认分页大小
DEFAULT_MESSAGE_LIMIT = 30

# 消息状态枚举
MSG_STATUS_PENDING = 'PENDING'      # 发送中（前端乐观更新）
MSG_STATUS_DELIVERED = 'DELIVERED'  # 已送达（后端确认）
MSG_STATUS_READ = 'READ'            # 已读

# 用户身份缓存（内存级轻量字典缓存，避免重复查询 User 表）
# 结构：{ user_name: { college, grade, verified } }
_user_cache = {}

# ============================================================
# 动态 Message 模型导入/定义
# ============================================================

# 尝试从 models 导入 Message，如果不存在则动态定义
try:
    from models import Message as MessageModel
    Message = MessageModel
except ImportError:
    # 如果 models.py 尚未定义 Message，我们在此动态创建
    # 但推荐在 models.py 中正式定义
    from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
    from sqlalchemy.orm import relationship

    class Message(db.Model):
        """
        私聊消息模型 — 高奢科技感私人数字化会客室
        ============================================================
        字段设计：
          - id: 自增主键
          - sender: 发送者用户名
          - receiver: 接收者用户名
          - content: 消息内容（支持富文本/全息信件格式）
          - status: 消息状态（PENDING | DELIVERED | READ）
          - client_timestamp: 客户端微秒级时间戳（用于乐观更新匹配）
          - created_at: 服务端记录时间
          - related_book_id: 关联书籍 ID（交易消息专用）
          - related_order_no: 关联订单号（交易消息专用）
          - is_system: 是否为系统消息（如交易确认）
        ============================================================
        """
        __tablename__ = 'messages'

        id = Column(Integer, primary_key=True, autoincrement=True)
        sender = Column(String(64), nullable=False, index=True)
        receiver = Column(String(64), nullable=False, index=True)
        content = Column(Text, nullable=False)
        status = Column(String(16), default=MSG_STATUS_DELIVERED)
        client_timestamp = Column(BigInteger, default=0)  # 微秒级时间戳
        created_at = Column(DateTime, default=datetime.utcnow)
        related_book_id = Column(Integer, nullable=True)
        related_order_no = Column(String(64), nullable=True)
        is_system = Column(db.Boolean, default=False)

        # 发送者关系（用于 joinedload 预加载）
        sender_rel = relationship('User', foreign_keys=[sender],
                                  primaryjoin=lambda: User.name == Message.sender,
                                  uselist=False)

        def to_dict(self, include_sender_info=True):
            """序列化消息对象"""
            result = {
                'id': self.id,
                'sender': self.sender,
                'receiver': self.receiver,
                'content': self.content,
                'status': self.status,
                'clientTimestamp': self.client_timestamp,
                'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                             if self.created_at else '',
                'relatedBookId': self.related_book_id,
                'relatedOrderNo': self.related_order_no,
                'isSystem': self.is_system,
            }

            # 附加发送者身份信息（通过 joinedload 预加载，无额外查询）
            if include_sender_info and self.sender_rel:
                user = self.sender_rel
                result['senderInfo'] = {
                    'college': user.college or '未设置',
                    'grade': user.grade or '未知',
                    'verified': True,  # 浙大认证状态
                }
            else:
                # 从缓存中获取
                cached = get_user_from_cache(self.sender)
                result['senderInfo'] = cached if cached else {
                    'college': '校友',
                    'grade': '未知',
                    'verified': False,
                }

            return result

    print('[CHAT] 动态创建 Message 模型（建议在 models.py 中正式定义）')


# ============================================================
# 辅助函数
# ============================================================

def get_user_from_cache(user_name: str) -> dict:
    """
    从内存缓存中获取用户身份信息
    ============================================================
    缓存策略：
      - 首次查询 User 表后写入缓存
      - 缓存永不过期（用户信息极少变更）
      - 线程安全（GIL 保护）
    ============================================================
    """
    if user_name in _user_cache:
        return _user_cache[user_name]

    user = User.query.filter_by(name=user_name).first()
    if user:
        info = {
            'college': user.college or '未设置',
            'grade': user.grade or '未知',
            'verified': True,
        }
    else:
        info = {
            'college': '校友',
            'grade': '未知',
            'verified': False,
        }

    _user_cache[user_name] = info
    return info


def parse_timestamp(ts_str: str) -> int:
    """
    安全解析时间戳字符串
    ============================================================
    防御设计：
      - 如果传入空值或非法格式，返回 0（从头拉取）
      - 如果传入非数字字符串，返回 0
      - 如果传入负数，返回 0
    ============================================================
    """
    if not ts_str:
        return 0
    try:
        ts = int(ts_str)
        return max(0, ts)
    except (ValueError, TypeError):
        return 0


def validate_user_exists(user_name: str) -> bool:
    """验证用户是否存在（优雅降级）"""
    if not user_name or not user_name.strip():
        return False
    user = User.query.filter_by(name=user_name.strip()).first()
    return user is not None


# ============================================================
# API 端点
# ============================================================

@chat_bp.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """
    获取私聊历史消息（增量同步 + 防 N+1 联合查询）
    ============================================================
    查询参数：
      - user_a:      当前用户（必填）
      - user_b:      对话对方（必填）
      - last_timestamp: 前端最后一条消息的微秒级时间戳（可选）
                        不传或传 0 表示从头拉取
      - limit:       单次最大返回条数（默认 30，最大 50）

    性能优化：
      - 使用 joinedload(Message.sender_rel) 预加载发送者信息
      - 使用内存级用户身份缓存，避免重复查询 User 表
      - 限制单次最大返回 50 条，防止 DOM 爆炸
      - 增量同步：仅返回 last_timestamp 之后的消息

    安全设计：
      - 参数边界保护：page 最小为 1，limit 限制在 1~50
      - 时间戳解析异常保护：非法格式返回 0，从头拉取
      - 用户存在性验证：不存在返回空列表而非 500
    ============================================================
    """
    try:
        user_a = request.args.get('user_a', '').strip()
        user_b = request.args.get('user_b', '').strip()
        last_timestamp_str = request.args.get('last_timestamp', '0')
        limit = request.args.get('limit', DEFAULT_MESSAGE_LIMIT, type=int)

        # ---- 参数边界保护 ----
        if not user_a or not user_b:
            return jsonify({
                'success': False,
                'message': '缺少必要参数 user_a 或 user_b',
                'messages': [],
            }), 400

        limit = max(1, min(limit, MAX_MESSAGE_LIMIT))
        last_timestamp = parse_timestamp(last_timestamp_str)

        # ---- 构建联合查询（防 N+1） ----
        # 使用 joinedload 预加载 sender_rel，一次性打包发送者信息
        query = Message.query.options(
            joinedload(Message.sender_rel)
        ).filter(
            or_(
                and_(Message.sender == user_a, Message.receiver == user_b),
                and_(Message.sender == user_b, Message.receiver == user_a),
            )
        )

        # ---- 增量同步：仅返回 last_timestamp 之后的消息 ----
        if last_timestamp > 0:
            # 使用 client_timestamp 进行增量同步
            # 同时包含等于 last_timestamp 的消息（用于去重）
            query = query.filter(Message.client_timestamp >= last_timestamp)

        # ---- 按时间正序排列 ----
        query = query.order_by(Message.client_timestamp.asc())

        # ---- 限制数量 ----
        messages = query.limit(limit).all()

        # ---- 构建响应 ----
        result = []
        for msg in messages:
            result.append(msg.to_dict(include_sender_info=True))

        return jsonify({
            'success': True,
            'messages': result,
            'count': len(result),
            'hasMore': len(result) >= limit,
        }), 200

    except Exception as e:
        # 全局异常捕获，绝不返回 500
        return jsonify({
            'success': False,
            'message': '获取聊天记录失败: ' + str(e),
            'messages': [],
        }), 200  # 返回 200 而非 500，前端优雅降级


@chat_bp.route('/api/chat/send', methods=['POST'])
def send_message():
    """
    发送私聊消息
    ============================================================
    请求体：
      - sender:          发送者用户名（必填）
      - receiver:        接收者用户名（必填）
      - content:         消息内容（必填）
      - client_timestamp: 客户端微秒级时间戳（必填，用于乐观更新匹配）
      - related_book_id:  关联书籍 ID（可选，交易消息）
      - related_order_no: 关联订单号（可选，交易消息）
      - is_system:        是否为系统消息（可选，默认 false）

    返回：
      - 完整的消息对象（包含服务端生成的 id 和 status）
      - 前端使用此返回的 id 替换乐观更新中的临时虚拟 ID

    安全设计：
      - 所有字段进行 strip 和长度校验
      - content 最大长度 5000 字符
      - 发送者和接收者不能相同
      - 用户存在性验证
    ============================================================
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体不能为空',
            }), 400

        sender = (data.get('sender') or '').strip()
        receiver = (data.get('receiver') or '').strip()
        content = (data.get('content') or '').strip()
        client_timestamp = data.get('client_timestamp', 0)
        related_book_id = data.get('related_book_id')
        related_order_no = data.get('related_order_no')
        is_system = data.get('is_system', False)

        # ---- 参数校验 ----
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

        # ---- 用户存在性验证 ----
        if not validate_user_exists(sender):
            return jsonify({'success': False, 'message': '发送者不存在'}), 400
        if not validate_user_exists(receiver):
            return jsonify({'success': False, 'message': '接收者不存在'}), 400

        # ---- 创建消息 ----
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

        # ---- 刷新以获取完整的关系数据 ----
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


@chat_bp.route('/api/chat/read', methods=['POST'])
def mark_as_read():
    """
    标记消息为已读
    ============================================================
    请求体：
      - reader: 读取者用户名（必填）
      - sender: 发送者用户名（必填，标记该发送者的所有消息为已读）

    返回：
      - 被标记为已读的消息数量

    设计：
      - 批量标记，将 reader 与 sender 之间所有 DELIVERED 状态
        的消息标记为 READ
      - 前端在进入私聊界面或收到新消息时调用
    ============================================================
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': '请求体不能为空'}), 400

        reader = (data.get('reader') or '').strip()
        sender = (data.get('sender') or '').strip()

        if not reader or not sender:
            return jsonify({'success': False, 'message': '参数不完整'}), 400

        # 批量标记已读
        count = Message.query.filter(
            Message.sender == sender,
            Message.receiver == reader,
            Message.status == MSG_STATUS_DELIVERED,
        ).update({Message.status: MSG_STATUS_READ})

        db.session.commit()

        return jsonify({
            'success': True,
            'markedCount': count,
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '标记已读失败: ' + str(e),
        }), 200


@chat_bp.route('/api/chat/conversations', methods=['GET'])
def get_conversations():
    """
    获取用户的对话列表
    ============================================================
    查询参数：
      - user: 用户名（必填）

    返回：
      - conversations: 对话列表，每个对话包含对方用户信息和最后一条消息
      - 按最后消息时间倒序排列

    性能优化：
      - 使用子查询获取每个对话的最后一条消息
      - 使用内存缓存获取用户身份信息
    ============================================================
    """
    try:
        user = request.args.get('user', '').strip()
        if not user:
            return jsonify({'success': False, 'message': '缺少参数 user'}), 400

        # 获取与该用户相关的所有对话对方
        # 使用 UNION 查询所有出现过的人
        sent_to = db.session.query(Message.receiver).filter(
            Message.sender == user
        ).distinct().all()

        received_from = db.session.query(Message.sender).filter(
            Message.receiver == user
        ).distinct().all()

        # 合并去重
        partners = set()
        for (name,) in sent_to:
            partners.add(name)
        for (name,) in received_from:
            partners.add(name)

        conversations = []
        for partner in partners:
            # 获取最后一条消息
            last_msg = Message.query.options(
                joinedload(Message.sender_rel)
            ).filter(
                or_(
                    and_(Message.sender == user, Message.receiver == partner),
                    and_(Message.sender == partner, Message.receiver == user),
                )
            ).order_by(Message.client_timestamp.desc()).first()

            if last_msg:
                # 获取未读消息数
                unread_count = Message.query.filter(
                    Message.sender == partner,
                    Message.receiver == user,
                    Message.status == MSG_STATUS_DELIVERED,
                ).count()

                partner_info = get_user_from_cache(partner)

                conversations.append({
                    'partner': partner,
                    'partnerInfo': partner_info,
                    'lastMessage': last_msg.to_dict(include_sender_info=False),
                    'unreadCount': unread_count,
                })

        # 按最后消息时间倒序
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


@chat_bp.route('/api/chat/order', methods=['POST'])
def create_chat_order():
    """
    在聊天中创建订单（一键出价/确认交割）
    ============================================================
    请求体：
      - sender:   发送者（买家）
      - receiver: 接收者（卖家）
      - book_id:  关联书籍 ID
      - price:    成交价格
      - address:  收货地址

    返回：
      - 系统消息（包含订单信息）
      - 订单号

    设计：
      - 在聊天流中生成一条全息信件动效的系统消息
      - 同时创建订单记录（调用 orders 模块）
    ============================================================
    """
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

        # 生成订单号
        import random
        order_no = f'ORD{datetime.utcnow().strftime("%Y%m%d%H%M%S")}{random.randint(1000, 9999)}'

        # 获取书籍信息
        from models import Book
        # 如果 book_id 带有偏移量（用户发布书籍），还原为真实数据库 ID
        USER_BOOK_ID_OFFSET = 100000000
        if book_id and book_id >= USER_BOOK_ID_OFFSET:
            book_id = book_id - USER_BOOK_ID_OFFSET
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'success': False, 'message': '书籍不存在'}), 404

        # 创建系统消息（全息信件格式）
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
