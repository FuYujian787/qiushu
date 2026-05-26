"""
通知路由：查询、标记已读
"""
from flask import Blueprint, request, jsonify
from models import db, Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """查询用户通知"""
    user_name = request.args.get('userName', '').strip()
    if not user_name:
        return jsonify({'success': False, 'message': 'userName参数不能为空'}), 400

    notifs = Notification.query.filter_by(user_name=user_name) \
        .order_by(Notification.created_at.desc()).all()

    return jsonify({'notifications': [n.to_dict() for n in notifs]}), 200


@notifications_bp.route('/api/notifications/read', methods=['POST'])
def mark_all_read():
    """标记用户所有通知为已读"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    user_name = (data.get('userName') or '').strip()
    if not user_name:
        return jsonify({'success': False, 'message': 'userName不能为空'}), 400

    Notification.query.filter_by(user_name=user_name, unread=True).update(
        {'unread': False}
    )
    db.session.commit()

    return jsonify({'success': True}), 200