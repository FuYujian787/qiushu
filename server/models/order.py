"""
订单模型
"""
from db import db


class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(64), unique=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    title = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(32), default='待收货')
    buyer = db.Column(db.String(64), nullable=False, index=True)
    address = db.Column(db.String(256), default='')
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True)

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