"""
Flask 应用主入口
启动方式：python app.py
"""
import os
import sys

# 确保当前目录在 sys.path 中，以便 routes 模块正确导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from config import DATABASE_URI, SECRET_KEY


def create_app():
    """应用工厂"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    # CORS — 允许前端跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 初始化数据库（必须先于路由注册）
    from models import db
    db.init_app(app)

    # 注册蓝图
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.orders import orders_bp
    from routes.community import community_bp
    from routes.notifications import notifications_bp
    from routes.zju import zju_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(zju_bp)
    app.register_blueprint(chat_bp)

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'message': '请求的资源不存在'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500

    # 根路径
    @app.route('/')
    def index():
        return jsonify({'message': '紫金求思 API 服务运行中', 'status': 'ok'}), 200

    return app


if __name__ == '__main__':
    app = create_app()

    # 确保数据库已初始化
    from init_db import init_database
    init_database(app)

    print('[INFO] Flask 后端启动于 http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=True)