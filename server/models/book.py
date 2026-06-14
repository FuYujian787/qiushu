"""
书籍模型（用户发布） + 虚拟书籍表（JSON导入）
"""
from db import db


class Book(db.Model):
    """书籍模型（用户发布）"""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False, index=True)
    author = db.Column(db.String(128), default='', index=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, default=0.0)
    condition = db.Column(db.String(32), default='九成新')
    seller = db.Column(db.String(64), default='系统', index=True)
    img = db.Column(db.String(512), default='R-C.jpg')
    category = db.Column(db.String(32), default='教材', index=True)
    is_user_published = db.Column(db.Boolean, default=False, index=True)
    alipay_qr = db.Column(db.Text, nullable=True)
    wechat_qr = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)

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


class BookJson(db.Model):
    """虚拟书籍表（从 books.json 导入）"""
    __tablename__ = 'books_json'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False, index=True)
    author = db.Column(db.String(128), default='', index=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, default=0.0)
    condition = db.Column(db.String(32), default='九成新')
    seller = db.Column(db.String(64), default='系统', index=True)
    img = db.Column(db.String(512), default='R-C.jpg')
    category = db.Column(db.String(32), default='教材', index=True)
    is_user_published = db.Column(db.Boolean, default=False)

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
            'isUserPublished': False,
        }