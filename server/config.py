"""
应用配置模块
"""
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite 数据库路径
DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')

# Flask 密钥（用于 session 签名等，当前无 session 但需要）
SECRET_KEY = 'qushu-platform-secret-key-2026'

# 分页默认值
DEFAULT_PAGE_SIZE = 20