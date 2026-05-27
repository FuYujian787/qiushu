"""
应用配置模块
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite 数据库路径（重命名为 zju_books.db）
DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'zju_books.db')

# Flask 密钥
SECRET_KEY = 'qushu-platform-secret-key-2026'

# 分页默认值
DEFAULT_PAGE_SIZE = 20