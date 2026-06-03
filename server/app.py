"""
Flask 应用主入口
启动方式: python app.py
"""
from flask import Flask, jsonify

from config import Config
from extensions import db, bcrypt, jwt, cors
from models import User, RevokedToken, cleanup_expired_tokens


def create_app():
    """应用工厂：创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── 初始化扩展 ──
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/auth/*": {"origins": "*"}})

    # ── 注册蓝图 ──
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    # ── 创建数据库表 ──
    with app.app_context():
        db.create_all()

    # ── JWT 回调处理 ──

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """检查 token 的 jti 是否在黑名单中。
        每次受保护请求都会调用此函数。先清理过期条目再查询。"""
        cleanup_expired_tokens()
        jti = jwt_payload['jti']
        return RevokedToken.query.filter_by(jti=jti).first() is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """token 已被吊销时的响应。
        区分 access 和 refresh token 返回不同的错误信息。"""
        if jwt_payload['type'] == 'refresh':
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        return jsonify({'error': 'Token has been revoked'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """token 已过期时的响应。
        区分 access 和 refresh token 返回不同的错误信息。"""
        if jwt_payload['type'] == 'refresh':
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        return jsonify({'error': 'Invalid or expired access token'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """token 格式无效时的响应（如被篡改、算法错误等）。"""
        return jsonify({'error': 'Invalid or expired access token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """请求头缺少 Authorization 时的响应。"""
        return jsonify({'error': 'Missing authorization header'}), 401

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)