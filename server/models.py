"""求书 · 書緣 — SQLAlchemy 数据模型（15张表）"""
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


def gen_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), default='书友')
    avatar = db.Column(db.String(200), nullable=True)
    college = db.Column(db.String(100), nullable=True)
    major = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(10), nullable=True)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    books = db.relationship('Book', backref='seller', lazy=True)
    orders_as_buyer = db.relationship('Order', foreign_keys='Order.buyer_id', backref='buyer', lazy=True)
    orders_as_seller = db.relationship('Order', foreign_keys='Order.seller_id', backref='seller_rel', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    replies = db.relationship('Reply', backref='author', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    wants = db.relationship('WantedBook', backref='requester', lazy=True)
    courses = db.relationship('UserCourse', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'email': self.email,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'college': self.college,
            'major': self.major,
            'grade': self.grade,
            'student_id': self.student_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    category = db.Column(db.String(20), nullable=True)
    original_price = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(10), default='良好')  # 全新/良好/有笔记/旧
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(10), default='在售')  # 在售/已售/下架
    accept_exchange = db.Column(db.Boolean, default=False)  # 是否接受以书换书
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('BookImage', backref='book', lazy=True)
    orders = db.relationship('Order', backref='book', lazy=True)
    reviews = db.relationship('Review', backref='book', lazy=True)
    favorites = db.relationship('Favorite', backref='book', lazy=True)
    journeys = db.relationship('BookJourney', backref='book', lazy=True)

    def to_dict(self):
        # 获取封面图片 URL
        cover_url = None
        if self.images:
            cover = next((img for img in self.images if img.is_cover), self.images[0])
            cover_url = cover.url
        else:
            # 无上传图片时，使用默认封面图
            cover_url = '/mock/images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'original_price': self.original_price,
            'price': self.price,
            'condition': self.condition,
            'description': self.description,
            'status': self.status,
            'accept_exchange': bool(self.accept_exchange) if self.accept_exchange is not None else False,
            'image': cover_url,  # 封面图片（BookCard 前端使用此字段）
            'images': [img.to_dict() for img in self.images] if self.images else [],
            'seller_name': self.seller.nickname if self.seller else None,
            'seller_college': self.seller.college if self.seller else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class BookImage(db.Model):
    __tablename__ = 'book_image'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    book_id = db.Column(db.String(36), db.ForeignKey('book.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    is_cover = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {'id': self.id, 'url': self.url, 'is_cover': self.is_cover, 'sort_order': self.sort_order}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    book_id = db.Column(db.String(36), db.ForeignKey('book.id'), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(10), default='待确认')  # 待确认/已确认/已完成/已取消
    contact_phone = db.Column(db.String(20), nullable=True)
    contact_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = db.relationship('Review', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'status': self.status,
            'contact_phone': self.contact_phone,
            'contact_note': self.contact_note,
            'book_title': self.book.title if self.book else None,
            'book_price': self.book.price if self.book else None,
            'buyer_name': self.buyer.nickname if self.buyer else None,
            'seller_name': self.seller_rel.nickname if self.seller_rel else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    book_id = db.Column(db.String(36), db.ForeignKey('book.id'), nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('order.id'), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'user_name': self.author.nickname if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.String(36), db.ForeignKey('book.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='uq_user_book_fav'),)


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), nullable=True)
    college = db.Column(db.String(100), nullable=True)
    credits = db.Column(db.Float, nullable=True)
    semester = db.Column(db.String(10), nullable=True)

    books = db.relationship('CourseBook', backref='course', lazy=True)
    posts = db.relationship('Post', backref='course', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'college': self.college,
            'credits': self.credits,
            'semester': self.semester,
        }


class CourseBook(db.Model):
    __tablename__ = 'course_book'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    course_id = db.Column(db.String(36), db.ForeignKey('course.id'), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)
    book_author = db.Column(db.String(100), nullable=True)
    book_isbn = db.Column(db.String(13), nullable=True)
    is_required = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'book_title': self.book_title,
            'book_author': self.book_author,
            'book_isbn': self.book_isbn,
            'is_required': self.is_required,
        }


class UserCourse(db.Model):
    __tablename__ = 'user_course'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.String(36), db.ForeignKey('course.id'), nullable=False)
    semester = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='uq_user_course'),)

    def to_dict(self):
        course = Course.query.get(self.course_id) if self.course_id else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'semester': self.semester,
            'course_name': course.name if course else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.String(36), db.ForeignKey('course.id'), nullable=True)
    book_id = db.Column(db.String(36), db.ForeignKey('book.id'), nullable=True)
    type = db.Column(db.String(20), default='其他')  # 选课求助/老师评价/考试资料/学习笔记/书评/求书/其他
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    is_pinned = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    replies = db.relationship('Reply', backref='post', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'book_id': self.book_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'view_count': self.view_count,
            'reply_count': self.reply_count,
            'user_name': self.author.nickname if self.author else None,
            'course_name': self.course.name if self.course else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    post_id = db.Column(db.String(36), db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'user_name': self.author.nickname if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class WantedBook(db.Model):
    __tablename__ = 'wanted_book'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    isbn = db.Column(db.String(13), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(10), default='求购中')  # 求购中/已匹配/已关闭
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'reason': self.reason,
            'status': self.status,
            'user_name': self.requester.nickname if self.requester else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class BookJourney(db.Model):
    __tablename__ = 'book_journey'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    book_id = db.Column(db.String(36), db.ForeignKey('book.id'), nullable=False)
    from_user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    to_user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    event_type = db.Column(db.String(20))  # 初次上架/售出/再次上架
    note = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 双外键指向同一表，需显式指定 foreign_keys 消除歧义
    from_user = db.relationship('User', foreign_keys=[from_user_id], lazy=True)
    to_user = db.relationship('User', foreign_keys=[to_user_id], lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'from_user_id': self.from_user_id,
            'to_user_id': self.to_user_id,
            'from_user_name': self.from_user.nickname if self.from_user else None,
            'to_user_name': self.to_user.nickname if self.to_user else None,
            'event_type': self.event_type,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Conversation(db.Model):
    """私信会话 — 两个用户之间的聊天通道"""
    __tablename__ = 'conversation'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user1_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.String(36), db.ForeignKey('order.id'), nullable=True)  # 关联订单（可选）
    book_id = db.Column(db.String(36), db.ForeignKey('book.id'), nullable=True)    # 关联书籍（可选）
    last_message = db.Column(db.String(500), nullable=True)   # 最后一条消息预览
    last_message_at = db.Column(db.DateTime, nullable=True)    # 最后消息时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 双外键
    user1 = db.relationship('User', foreign_keys=[user1_id], lazy=True)
    user2 = db.relationship('User', foreign_keys=[user2_id], lazy=True)
    order = db.relationship('Order', foreign_keys=[order_id], lazy=True)
    book = db.relationship('Book', foreign_keys=[book_id], lazy=True)
    messages = db.relationship('Message', backref='conversation', lazy=True,
                               order_by='Message.created_at.asc()')

    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id',
                           name='uq_conversation_pair'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'order_id': self.order_id,
            'book_id': self.book_id,
            'last_message': self.last_message,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'user1_name': self.user1.nickname if self.user1 else None,
            'user2_name': self.user2.nickname if self.user2 else None,
            'book_title': self.book.title if self.book else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    """私信消息"""
    __tablename__ = 'message'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)  # 文本内容（image/order_card 类型时可为空）
    message_type = db.Column(db.String(20), default='text')  # text / image / order_card
    image_url = db.Column(db.String(300), nullable=True)     # 图片消息的图片 URL
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'content': self.content,
            'message_type': self.message_type or 'text',
            'image_url': self.image_url,
            'is_read': self.is_read,
            'sender_name': self.sender.nickname if self.sender else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AILog(db.Model):
    __tablename__ = 'ai_log'
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    type = db.Column(db.String(30))  # 对话/定价/推荐/摘要/搜索
    input_data = db.Column(db.Text, nullable=True)
    output_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
