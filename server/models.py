"""
数据库模型
- User: 用户表，email 唯一约束，密码以 bcrypt 哈希存储
- RevokedToken: 已吊销的 JWT 黑名单
"""
from extensions import db
from datetime import datetime


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'


class RevokedToken(db.Model):
    """JWT 黑名单模型
    存储已吊销的 token 的 jti，在对应 token 过期后可由 cleanup 清除。
    """
    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)   # 'access' 或 'refresh'
    expires_at = db.Column(db.DateTime, nullable=False)      # token 的原始过期时间
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RevokedToken {self.jti}>'


def cleanup_expired_tokens():
    """清理黑名单中已过期的条目，防止数据库无限增长。
    在执行黑名单查询前调用此函数，确保已过期的 token 不再占用空间。"""
    now = datetime.utcnow()
    deleted = RevokedToken.query.filter(RevokedToken.expires_at < now).delete()
    if deleted:
        db.session.commit()