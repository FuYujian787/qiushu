"""
Flask 应用主入口
启动方式：python app.py
"""
import os
import sys

# 确保 server/ 目录在 sys.path 中
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from flask import Flask, jsonify
from flask_cors import CORS
from config import DATABASE_URI, SECRET_KEY
from db import db


def create_app():
    """应用工厂"""
    # 确保路径在 reloader 子进程中也能生效
    if _SERVER_DIR not in sys.path:
        sys.path.insert(0, _SERVER_DIR)

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.books_publish import books_publish_bp
    from routes.orders import orders_bp
    from routes.stats import stats_bp
    from routes.community import community_bp
    from routes.community_actions import community_actions_bp
    from routes.notifications import notifications_bp
    from routes.zju import zju_bp
    from routes.chat_send_read import chat_send_read_bp
    from routes.chat_history import chat_history_bp
    from routes.chat_order import chat_order_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(books_publish_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(community_actions_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(zju_bp)
    app.register_blueprint(chat_send_read_bp)
    app.register_blueprint(chat_history_bp)
    app.register_blueprint(chat_order_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'message': '请求的资源不存在'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500

    @app.route('/')
    def index():
        return jsonify({'message': '紫金求思 API 服务运行中', 'status': 'ok'}), 200

    return app


if __name__ == '__main__':
    app = create_app()
    from init_db import init_database
    init_database(app)
    print('[INFO] Flask 后端启动于 http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=False)