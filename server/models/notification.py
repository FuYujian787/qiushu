"""
通知模型
"""
from db import db


class Notification(db.Model):
    """通知消息模型"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(64), nullable=False, index=True)
    title = db.Column(db.String(256), nullable=False)
    desc = db.Column(db.Text, default='')
    unread = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'title': self.title,
            'desc': self.desc,
            'time': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'unread': self.unread,
        }