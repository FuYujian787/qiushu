"""用户认证 API（注册/登录/登出/CAS）"""
from flask import Blueprint, request, jsonify
from extensions import db, limiter
from models import User, Book
from services.auth import create_access_token, revoke_token, verify_token, login_required, extract_token_from_request
from services.validators import validate_password_strength, validate_email, validate_phone
from services.zju_cas import ZjuCASClient
from services.__init__ import ERROR_CODES

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit('10 per minute')
def register():
    """用户注册"""
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    nickname = data.get('nickname', '').strip() or '书友'

    # 验证手机号
    valid, msg = validate_phone(phone)
    if not valid:
        return jsonify({'status': 'error', 'code': 'AUTH_PHONE_INVALID', 'message': msg}), 400

    # 验证邮箱（可选）
    if email:
        valid, msg = validate_email(email)
        if not valid:
            return jsonify({'status': 'error', 'code': 'AUTH_EMAIL_INVALID', 'message': msg}), 400

    # 验证密码强度
    valid, msg = validate_password_strength(password)
    if not valid:
        return jsonify({'status': 'error', 'code': 'AUTH_WEAK_PASSWORD', 'message': msg}), 400

    # 检查重复注册（统一错误信息防枚举）
    duplicate = False
    if User.query.filter_by(phone=phone).first():
        duplicate = True
    if email and User.query.filter_by(email=email).first():
        duplicate = True
    if duplicate:
        return jsonify({'status': 'error', 'code': 'AUTH_DUPLICATE_USER', 'message': ERROR_CODES['AUTH_DUPLICATE_USER']}), 409

    # 创建用户
    user = User(
        phone=phone,
        email=email if email else None,
        nickname=nickname,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(user.id)

    return jsonify({
        'status': 'success',
        'data': {
            'token': token,
            'user': user.to_dict(),
        },
        'message': '注册成功',
    }), 201


@auth_bp.route('/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    """用户登录（手机号+密码）"""
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)

    if not phone or not password:
        return jsonify({'status': 'error', 'code': 'AUTH_INVALID_CREDENTIALS', 'message': ERROR_CODES['AUTH_INVALID_CREDENTIALS']}), 401

    user = User.query.filter_by(phone=phone).first()
    if not user or not user.check_password(password):
        return jsonify({'status': 'error', 'code': 'AUTH_INVALID_CREDENTIALS', 'message': ERROR_CODES['AUTH_INVALID_CREDENTIALS']}), 401

    token = create_access_token(user.id, remember_me=remember_me)

    return jsonify({
        'status': 'success',
        'data': {
            'token': token,
            'user': user.to_dict(),
        },
        'message': '登录成功',
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    token = extract_token_from_request()
    if not token:
        data = request.get_json() or {}
        token = data.get('token', '')

    if token:
        revoke_token(token)

    return jsonify({'status': 'success', 'message': '已安全登出'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_me():
    """获取当前登录用户信息"""
    user = User.query.get(request.current_user_id)
    if not user:
        return jsonify({'status': 'error', 'code': 'USER_NOT_FOUND', 'message': ERROR_CODES['USER_NOT_FOUND']}), 404
    return jsonify({'status': 'success', 'data': user.to_dict()})


@auth_bp.route('/cas/login', methods=['POST'])
@limiter.limit('5 per minute')
def cas_login():
    """浙大通行证 CAS 登录"""
    data = request.get_json() or {}
    student_id = data.get('student_id', '').strip()
    password = data.get('password', '')

    if not student_id or not password:
        return jsonify({'status': 'error', 'code': 'AUTH_INVALID_CREDENTIALS', 'message': '请输入学号和密码'}), 400

    try:
        client = ZjuCASClient()
        cas_result = client.login(student_id, password)

        # 获取学籍信息
        student_info = client.get_student_info()

        # 获取课程数据（courses.zju.edu.cn todos）
        course_data = client.get_course_data()

        # 获取完整课程表（ZDBK 课表 API，含教师/时间/地点）
        course_schedule = client.get_course_schedule()

        # 教材推荐（预置库快速匹配，不阻塞；AI 推荐由前端按需调用 /api/ai/textbooks）
        textbook_recommendations = []
        if course_schedule:
            try:
                from services.ai_textbook import recommend_textbooks_for_courses, match_platform_books
                textbook_recommendations = recommend_textbooks_for_courses(
                    course_schedule, use_ai=False  # CAS 登录时不调 AI，快速返回预置库结果
                )
                # 匹配平台在售二手书
                available_books = Book.query.filter_by(status='在售').all()
                available_list = [b.to_dict() for b in available_books]
                textbook_recommendations = match_platform_books(textbook_recommendations, available_list)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning('教材推荐失败（非致命）: %s', e)

        # 查找或创建用户（CAS 用户不存储密码，安全性要求）
        user = User.query.filter_by(student_id=student_id).first()
        if not user:
            # 生成一个随机安全密码哈希（用户通过 CAS 登录，不使用密码登录）
            import secrets
            random_pw = secrets.token_urlsafe(32)
            user = User(
                student_id=student_id,
                nickname=student_info.get('name', f'浙大{student_id[-4:]}'),
                college=student_info.get('college', ''),
                major=student_info.get('major', ''),
                grade=student_info.get('grade', ''),
                phone=None,
            )
            user.set_password(random_pw)  # 使用随机哈希占位，避免空密码安全风险
            db.session.add(user)
            db.session.commit()
        else:
            # 更新学籍信息（同步最新数据）
            if student_info.get('college'):
                user.college = student_info['college']
            if student_info.get('major'):
                user.major = student_info['major']
            if student_info.get('name'):
                user.nickname = student_info['name']
            if student_info.get('grade'):
                user.grade = student_info['grade']
            db.session.commit()

        token = create_access_token(user.id)

        return jsonify({
            'status': 'success',
            'data': {
                'token': token,
                'user': user.to_dict(),
                'courses': course_data,
                'schedule': course_schedule,               # 完整课程表（ZDBK，50门）
                'textbooks': textbook_recommendations,      # 教材推荐（预置库快速匹配）
            },
            'message': 'CAS 登录成功',
        })

    except ValueError as e:
        error_msg = str(e)
        if error_msg == 'AUTH_INVALID_CREDENTIALS':
            return jsonify({'status': 'error', 'code': 'AUTH_INVALID_CREDENTIALS', 'message': '学号或密码错误，请重试'}), 401
        if error_msg == 'AUTH_CAS_CAPTCHA':
            return jsonify({
                'status': 'error',
                'code': 'AUTH_CAS_CAPTCHA',
                'message': 'CAS 登录需要验证码，请在浏览器中登录一次浙大通行证后再试，或使用手机号登录',
            }), 400
        if error_msg == 'AUTH_CAS_LOCKED':
            return jsonify({
                'status': 'error',
                'code': 'AUTH_CAS_LOCKED',
                'message': '账号已被临时锁定，请稍后重试或使用手机号登录',
            }), 423
        if 'CAS_AUTH_UNAVAILABLE' in error_msg:
            return jsonify({
                'status': 'error',
                'code': 'AUTH_CAS_UNAVAILABLE',
                'message': 'CAS 认证服务暂时不可用，请使用手机号登录',
            }), 503
        # 不暴露内部错误详情
        return jsonify({'status': 'error', 'code': 'AUTH_CAS_ERROR', 'message': 'CAS 认证失败，请检查学号密码或稍后重试'}), 500
    except Exception:
        return jsonify({'status': 'error', 'code': 'AUTH_CAS_ERROR', 'message': 'CAS 认证异常，请稍后重试'}), 500


@auth_bp.route('/verify', methods=['GET'])
def verify():
    """验证 token 是否有效（供前端自动登录使用）"""
    token = request.args.get('token', '') or extract_token_from_request()

    if not token:
        return jsonify({'status': 'error', 'code': 'AUTH_TOKEN_MISSING', 'message': '请先登录'}), 401

    payload = verify_token(token)
    if not payload:
        return jsonify({'status': 'error', 'code': 'AUTH_TOKEN_EXPIRED', 'message': '登录已过期'}), 401

    user = User.query.get(payload.get('user_id'))
    if not user:
        return jsonify({'status': 'error', 'code': 'USER_NOT_FOUND', 'message': '用户不存在'}), 404

    return jsonify({
        'status': 'success',
        'data': {
            'token': token,
            'user': user.to_dict(),
        },
    })
