"""
社区帖子 + 回复模型
"""
import json
from db import db


class Post(db.Model):
    """社区帖子模型"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(64), nullable=False)
    is_preset = db.Column(db.Boolean, default=False)
    like_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    book_mentions = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
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
    """帖子回复模型"""
    __tablename__ = 'replies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())

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