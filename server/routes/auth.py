"""
认证路由：登录 / 注册
"""
from flask import Blueprint, request, jsonify
from db import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    name = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not name or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(name=name, password=password).first()
    if not user:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    return jsonify({'success': True, 'user': user.to_dict()}), 200


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    name = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not name or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400

    if User.query.filter_by(name=name).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 409

    user = User(
        name=name,
        password=password,
        college=(data.get('college') or '未设置'),
        grade=(data.get('grade') or '大一'),
        address=(data.get('address') or ''),
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'user': user.to_dict()}), 201