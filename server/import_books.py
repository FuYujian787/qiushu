"""
将 client/public/data/books.json 导入 SQLite BookJson 表
用法：cd server && python import_books.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import DATABASE_URI, SECRET_KEY
from db import db


def import_json_books(app):
    """将 books.json 数据导入 BookJson 表"""
    from models import BookJson

    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'client', 'public', 'data', 'books.json'
    )

    if not os.path.exists(json_path):
        print(f'[WARN] 未找到 {json_path}，跳过导入')
        return

    with app.app_context():
        # 清空已有数据
        BookJson.query.delete()
        db.session.commit()

        with open(json_path, 'r', encoding='utf-8') as f:
            books_data = json.load(f)

        chunk_size = 5000
        total = len(books_data)
        print(f'[INFO] 正在导入 {total} 条书籍数据到 BookJson 表...')

        for i in range(0, total, chunk_size):
            chunk = books_data[i:i + chunk_size]
            for b in chunk:
                book = BookJson(
                    id=b.get('id'),
                    title=b.get('title', ''),
                    author=b.get('author', ''),
                    price=b.get('price', 0),
                    old_price=b.get('oldPrice', 0),
                    condition=b.get('condition', '九成新'),
                    seller=b.get('seller', '系统'),
                    img=b.get('img', 'R-C.jpg'),
                    category=b.get('category', '教材'),
                )
                db.session.add(book)
            db.session.commit()
            print(f'  已导入 {min(i + chunk_size, total)} / {total} 条')

        print(f'[DONE] 导入完成，共 {total} 条')


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)

    import_json_books(app)
    print('[DONE] 导入完成')