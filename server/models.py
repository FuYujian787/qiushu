"""
数据模型定义 — SQLAlchemy ORM
============================================================
紫金求思 · 社区模块增强版

变更记录：
  - Post 模型新增: like_count, view_count, book_mentions (JSON)
  - Reply 模型新增: like_count
  - User 模型保持 college / grade 字段，to_dict() 完整返回
  - 新增热度加权排序支持（后端 community.py 实现）
============================================================
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(16), default='buyer')
    college = db.Column(db.String(64), default='未设置')
    grade = db.Column(db.String(16), default='大一')
    address = db.Column(db.String(256), default='')
    avatar = db.Column(db.String(256), default='5492ec47e5014900a8690086552604d9.jpg')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'college': self.college,
            'grade': self.grade,
            'address': self.address,
            'avatar': self.avatar,
        }


class Book(db.Model):
    """书籍模型（系统商品 + 用户发布）"""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False, index=True)  # 【索引优化】常用于搜索
    author = db.Column(db.String(128), default='', index=True)     # 【索引优化】常用于搜索
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, default=0.0)
    condition = db.Column(db.String(32), default='九成新')
    seller = db.Column(db.String(64), default='系统', index=True)  # 【索引优化】常用于 filter_by 和关联查询
    img = db.Column(db.String(512), default='R-C.jpg')
    category = db.Column(db.String(32), default='教材', index=True) # 【索引优化】常用于筛选
    is_user_published = db.Column(db.Boolean, default=False, index=True)  # 【索引优化】常用于筛选
    alipay_qr = db.Column(db.Text, nullable=True)
    wechat_qr = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 【索引优化】常用于排序

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'price': round(self.price, 1),
            'oldPrice': round(self.old_price, 1),
            'condition': self.condition,
            'seller': self.seller,
            'img': self.img,
            'category': self.category,
            'isUserPublished': self.is_user_published,
            'alipayQr': self.alipay_qr,
            'wechatQr': self.wechat_qr,
        }


class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(64), unique=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)  # 【索引优化】常用于关联查询
    title = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(32), default='待收货')
    buyer = db.Column(db.String(64), nullable=False, index=True)  # 【索引优化】常用于 filter_by
    address = db.Column(db.String(256), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 【索引优化】常用于排序

    book = db.relationship('Book', backref='orders')

    def to_dict(self):
        return {
            'id': self.order_no,
            'title': self.title,
            'price': round(self.price, 1),
            'status': self.status,
            'date': self.created_at.strftime('%Y-%m-%d') if self.created_at else '',
            'buyer': self.buyer,
        }


class Post(db.Model):
    """
    社区帖子模型（增强版）
    ============================================================
    新增字段：
      - like_count:  点赞数，用于热度排序
      - view_count:  浏览数，用于热度排序
      - book_mentions: JSON 数组，存储帖子中自动识别的书名列表
                       格式: [{"title": "曼昆宏观经济学", "matched": true}, ...]
    ============================================================
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(64), nullable=False)
    is_preset = db.Column(db.Boolean, default=False)
    like_count = db.Column(db.Integer, default=0)       # 点赞数
    view_count = db.Column(db.Integer, default=0)       # 浏览数
    book_mentions = db.Column(db.Text, default='[]')    # JSON 字符串，存储识别的书名
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id if not self.is_preset else 'preset_' + str(self.id),
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'likeCount': self.like_count or 0,
            'viewCount': self.view_count or 0,
            'bookMentions': json.loads(self.book_mentions) if self.book_mentions else [],
            'matchedBooks': json.loads(self.book_mentions) if self.book_mentions else [],
        }



class Reply(db.Model):
    """
    帖子回复模型（增强版）
    ============================================================
    新增字段：
      - like_count: 点赞数
    ============================================================
    """
    __tablename__ = 'replies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, default=0)       # 点赞数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship('Post', backref='replies')

    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.post_id,
            'author': self.author,
            'content': self.content,
            'likeCount': self.like_count or 0,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
        }


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

    索引设计：
      - (sender, receiver) 联合索引加速私聊查询
      - client_timestamp 索引加速增量同步
    ============================================================
    """
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.String(64), nullable=False, index=True)
    receiver = db.Column(db.String(64), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), default='DELIVERED')
    client_timestamp = db.Column(db.BigInteger, default=0)  # 微秒级时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_book_id = db.Column(db.Integer, nullable=True)
    related_order_no = db.Column(db.String(64), nullable=True)
    is_system = db.Column(db.Boolean, default=False)

    # 发送者关系（用于 joinedload 预加载）
    sender_rel = db.relationship(
        'User',
        foreign_keys=[sender],
        primaryjoin='User.name == Message.sender',
        uselist=False,
        lazy='joined',
    )

    __table_args__ = (
        db.Index('idx_messages_pair', 'sender', 'receiver'),
        db.Index('idx_messages_timestamp', 'client_timestamp'),
    )

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
                'verified': True,
            }
        else:
            result['senderInfo'] = {
                'college': '校友',
                'grade': '未知',
                'verified': False,
            }

        return result


class Notification(db.Model):
    """通知消息模型"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(64), nullable=False, index=True)
    title = db.Column(db.String(256), nullable=False)
    desc = db.Column(db.Text, default='')
    unread = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'title': self.title,
            'desc': self.desc,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'unread': self.unread,
        }
