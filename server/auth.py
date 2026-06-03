"""
认证与授权蓝图
包含注册、登录、令牌刷新、登出、受保护资源访问。
"""
import re
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    decode_token
)

from extensions import db, bcrypt
from models import User, RevokedToken, cleanup_expired_tokens

# ──────────────────────────────────────────────
# 蓝图定义
# ──────────────────────────────────────────────
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ──────────────────────────────────────────────
# 验证正则
# ──────────────────────────────────────────────
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# 密码规则：至少 8 位，包含大写字母、小写字母、数字、特殊字符
PASSWORD_REGEX = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?`~\\|]).{8,}$'
)


# ──────────────────────────────────────────────
# POST /auth/register — 用户注册
# ──────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    注册新用户。
    请求体: { "email": "...", "password": "..." }
    验证邮箱格式、密码强度、邮箱唯一性，通过后 bcrypt 哈希存储密码。
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    # 检查必填字段
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # 邮箱格式校验
    if not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Invalid email format'}), 400

    # 密码强度校验
    if not PASSWORD_REGEX.match(password):
        return jsonify({
            'error': 'Password must be at least 8 characters and include '
                     'uppercase, lowercase, digit, and special character'
        }), 400

    # 邮箱唯一性校验
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # bcrypt 哈希存储密码
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# ──────────────────────────────────────────────
# POST /auth/login — 用户登录
# ──────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录。
    请求体: { "email": "...", "password": "...", "remember_me": true/false }
    验证邮箱是否存在、密码是否正确，成功后返回 access_token 和 refresh_token。
    refresh_token 的有效期根据 remember_me 动态设置：
      - remember_me=true  → 30 天
      - remember_me=false → 7 天  （默认）
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # 查找用户 — 错误信息区分邮箱未注册
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Email not found'}), 404

    # 验证密码 — 错误信息区分密码错误
    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Incorrect password'}), 401

    # 生成令牌
    access_token = create_access_token(identity=email)

    # remember_me 动态决定 refresh_token 有效期
    refresh_expires = timedelta(days=30) if remember_me else timedelta(days=7)
    refresh_token = create_refresh_token(identity=email, expires_delta=refresh_expires)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


# ──────────────────────────────────────────────
# POST /auth/refresh — 免登录刷新 access_token
# ──────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    使用 refresh_token 换取新的 access_token，实现免登录。
    请求体: { "refresh_token": "..." }
    验证 refresh_token 的有效性、类型是否为 refresh、是否已被吊销。
    任何失败均返回统—错误信息 {"error": "Invalid or expired refresh token"}。
    """
    data = request.get_json(silent=True)
    if not data or 'refresh_token' not in data:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401

    refresh_token_str = data['refresh_token']

    try:
        # 手动解码 refresh_token（不触发全局 JWT 错误处理器）
        decoded = decode_token(refresh_token_str)

        # 确认为 refresh 类型
        if decoded['type'] != 'refresh':
            return jsonify({'error': 'Invalid or expired refresh token'}), 401

        # 清理过期黑名单，然后检查是否已被吊销
        cleanup_expired_tokens()
        if RevokedToken.query.filter_by(jti=decoded['jti']).first():
            return jsonify({'error': 'Invalid or expired refresh token'}), 401

        # 生成新的 access_token
        new_access_token = create_access_token(identity=decoded['sub'])
        return jsonify({'access_token': new_access_token}), 200

    except Exception:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401


# ──────────────────────────────────────────────
# POST /auth/logout — 登出（吊销 token）
# ──────────────────────────────────────────────
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    登出：将当前 access_token 的 jti 加入黑名单，
    同时接收请求体中可选的 refresh_token，将其 jti 也加入黑名单。
    加入黑名单后，这些 token 即使未过期也无法再使用。
    """
    jwt_data = get_jwt()
    access_jti = jwt_data['jti']
    access_exp = jwt_data['exp']  # Unix 时间戳

    # 清理过期条目后，再加入新的黑名单记录
    cleanup_expired_tokens()

    # 将当前 access_token 加入黑名单
    revoked_access = RevokedToken(
        jti=access_jti,
        token_type='access',
        expires_at=datetime.fromtimestamp(access_exp)
    )
    db.session.add(revoked_access)

    # 可选：将请求体中的 refresh_token 也加入黑名单
    data = request.get_json(silent=True)
    if data and 'refresh_token' in data:
        try:
            refresh_decoded = decode_token(data['refresh_token'])
            refresh_jti = refresh_decoded['jti']
            refresh_exp = refresh_decoded['exp']

            # 避免重复添加
            if not RevokedToken.query.filter_by(jti=refresh_jti).first():
                revoked_refresh = RevokedToken(
                    jti=refresh_jti,
                    token_type='refresh',
                    expires_at=datetime.fromtimestamp(refresh_exp)
                )
                db.session.add(revoked_refresh)
        except Exception:
            # refresh_token 无效则静默忽略，不影响 access_token 的登出
            pass

    db.session.commit()
    return jsonify({'message': 'Successfully logged out'}), 200


# ──────────────────────────────────────────────
# GET /auth/profile — 获取当前用户信息（受保护）
# ──────────────────────────────────────────────
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    受保护资源示例。需要有效的 access_token。
    返回当前用户的邮箱和注册时间。
    """
    current_email = get_jwt_identity()
    user = User.query.filter_by(email=current_email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'email': user.email,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }), 200