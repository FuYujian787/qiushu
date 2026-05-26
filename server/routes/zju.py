"""
浙大通行证验证路由（模拟端点）
注意：这是一个模拟实现，用于演示前端与后端交互流程。
实际部署需要接入学校统一认证系统。
"""
from flask import Blueprint, request, jsonify

zju_bp = Blueprint('zju', __name__)


@zju_bp.route('/api/zju-verify', methods=['POST'])
def zju_verify():
    """模拟浙大通行证验证"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': '学号和密码不能为空'}), 400

    # 模拟验证逻辑：学号以 3 开头视为有效
    if not username.startswith('3') or len(username) != 10:
        return jsonify({
            'success': False,
            'message': '学号格式不正确或验证失败',
        }), 401

    # 模拟返回学生信息
    colleges = ['计算机科学与技术学院', '管理学院', '数学科学学院',
                '外国语学院', '化学系', '经济学院']
    grades = ['大一', '大二', '大三', '大四', '研究生']

    student = {
        'name': f'同学{username[-4:]}',
        'college': colleges[hash(username) % len(colleges)],
        'grade': grades[hash(username + 'g') % len(grades)],
    }

    return jsonify({
        'success': True,
        'message': '验证成功',
        'student': student,
    }), 200