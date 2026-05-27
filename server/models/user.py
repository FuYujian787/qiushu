"""
用户模型
"""
from db import db


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