"""
私聊消息模型
"""
from db import db


class Message(db.Model):
    """私聊消息模型"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.String(64), nullable=False, index=True)
    receiver = db.Column(db.String(64), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(16), default='DELIVERED')
    client_timestamp = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    related_book_id = db.Column(db.Integer, nullable=True)
    related_order_no = db.Column(db.String(64), nullable=True)
    is_system = db.Column(db.Boolean, default=False)

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