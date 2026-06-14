"""求书 · 書緣 — Flask 后端入口"""
import os
import sys
import logging
from dotenv import load_dotenv

# 加载 .env 文件（必须在其他 import 之前）
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 配置日志（CAS 认证调试用，生产环境可降级为 WARNING）
# force=True 确保覆盖 Flask/Werkzeug 已有的日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
    force=True,
)

from flask import Flask, jsonify
from flask_cors import CORS
from extensions import db, limiter


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    # 数据库配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qiushu.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.environ.get('JWT_SECRET_KEY', ''))

    # 上传配置
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

    db.init_app(app)
    limiter.init_app(app)

    # 注册蓝图
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.orders import orders_bp
    from routes.favorites import favorites_bp
    from routes.forum import forum_bp
    from routes.wishes import wishes_bp
    from routes.courses import courses_bp
    from routes.user import user_bp
    from routes.ai import ai_bp
    from routes.exchange import exchange_bp
    from routes.tree import tree_bp
    from routes.messages import messages_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(forum_bp, url_prefix='/api/forum')
    app.register_blueprint(wishes_bp, url_prefix='/api/wishes')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(exchange_bp, url_prefix='/api/exchange')
    app.register_blueprint(tree_bp, url_prefix='/api/tree')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')

    # 健康检查
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'success', 'data': {'message': '求书·書緣 API is running'}})

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'status': 'error', 'message': '接口不存在'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'status': 'error', 'message': '服务器内部错误'}), 500

    # 启动时创建所有表
    with app.app_context():
        import models  # noqa: F401
        db.create_all()

        # 兼容已有数据库：添加新增列（如果不存在）
        import sqlalchemy as sa
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'book' in inspector.get_table_names():
            existing_cols = [c['name'] for c in inspector.get_columns('book')]
            if 'accept_exchange' not in existing_cols:
                with db.engine.connect() as conn:
                    conn.execute(sa.text('ALTER TABLE book ADD COLUMN accept_exchange BOOLEAN DEFAULT 0'))
                    conn.commit()
                print('[OK] 已为 book 表添加 accept_exchange 列')

        # 清理重复会话（旧版按 order_id 分裂的错误数据）
        if 'conversation' in inspector.get_table_names():
            with db.engine.connect() as conn:
                result = conn.execute(sa.text('''
                    DELETE FROM conversation WHERE id NOT IN (
                        SELECT MIN(id) FROM conversation GROUP BY user1_id, user2_id
                    )
                '''))
                deleted = result.rowcount
                if deleted > 0:
                    conn.commit()
                    print(f'[OK] 已清理 {deleted} 条重复会话')

        # 为 message 表添加新增列（图片消息 + 订单卡片支持）
        if 'message' in inspector.get_table_names():
            msg_cols = [c['name'] for c in inspector.get_columns('message')]
            with db.engine.connect() as conn:
                if 'message_type' not in msg_cols:
                    conn.execute(sa.text("ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'text'"))
                    conn.commit()
                    print('[OK] 已为 message 表添加 message_type 列')
                if 'image_url' not in msg_cols:
                    conn.execute(sa.text('ALTER TABLE message ADD COLUMN image_url VARCHAR(300)'))
                    conn.commit()
                    print('[OK] 已为 message 表添加 image_url 列')

        print('[OK] 数据库表已创建')

    return app


if __name__ == '__main__':
    app = create_app()
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, port=5000, use_reloader=False)
