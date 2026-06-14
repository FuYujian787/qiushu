"""JWT 签发、验证、黑名单管理"""
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '')
if not SECRET_KEY:
    raise RuntimeError(
        '环境变量 JWT_SECRET_KEY 未设置。'
        '请运行: python -c "import secrets; print(secrets.token_urlsafe(32))" 生成密钥'
        '并设置到环境变量或 .env 文件中。'
    )

ACCESS_TOKEN_EXPIRE_HOURS = 24
ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER = 7

# Token 黑名单（登出后销毁，生产环境应使用 Redis）
# 存储格式: {token: expiry_timestamp} 以支持自动过期清理
token_blacklist = {}


def create_access_token(user_id: str, remember_me: bool = False) -> str:
    """签发 JWT access token"""
    expire_hours = ACCESS_TOKEN_EXPIRE_DAYS_REMEMBER * 24 if remember_me else ACCESS_TOKEN_EXPIRE_HOURS
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expire_hours),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def _cleanup_expired_blacklist():
    """清理黑名单中已过期的 token（防止内存泄漏）"""
    now = datetime.utcnow()
    expired_keys = [t for t, exp in list(token_blacklist.items()) if exp < now]
    for key in expired_keys:
        del token_blacklist[key]


def revoke_token(token: str):
    """登出时销毁 token（加入黑名单，含过期时间）"""
    try:
        # 尝试解码获取过期时间（即使被黑名单的 token 也可以先解码）
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={'verify_exp': False})
        exp = datetime.utcfromtimestamp(payload.get('exp', 0))
    except jwt.InvalidTokenError:
        # 无法解码，默认 30 天后过期
        exp = datetime.utcnow() + timedelta(days=30)
    token_blacklist[token] = exp
    # 每次加入时顺便清理过期项
    _cleanup_expired_blacklist()


def verify_token(token: str) -> dict | None:
    """验证 JWT token，返回 payload 或 None"""
    if token in token_blacklist:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def extract_token_from_request(req=None):
    """从请求中提取 Bearer token（统一工具函数）

    Args:
        req: Flask request 对象，默认使用全局 request

    Returns:
        str | None: token 字符串或 None
    """
    if req is None:
        req = request
    auth_header = req.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def login_required(f):
    """需要登录的 API 装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = extract_token_from_request()

        if not token:
            return jsonify({'status': 'error', 'code': 'AUTH_TOKEN_MISSING', 'message': '请先登录'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'status': 'error', 'code': 'AUTH_TOKEN_EXPIRED', 'message': '登录已过期，请重新登录'}), 401

        request.current_user_id = payload.get('user_id')
        return f(*args, **kwargs)
    return decorated
