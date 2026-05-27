"""
社区辅助函数：热度算法、书名提取、XSS转义、用户信息
"""
import re
import math
from datetime import datetime, timezone
from db import db
from models import Book, User

VIEW_WEIGHT = 0.3
REPLY_WEIGHT = 0.7
HALF_LIFE_HOURS = 48.0
BOOK_TITLE_PATTERN = re.compile(r'《([^》]{1,50})》')


def compute_hot_score(view_count: int, reply_count: int, created_at: datetime) -> float:
    """热度加权排序算法（牛顿冷却定律）"""
    vc = max(0, view_count or 0)
    rc = max(0, reply_count or 0)
    base_score = vc * VIEW_WEIGHT + rc * REPLY_WEIGHT
    if base_score == 0:
        base_score = 0.01
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    hours_elapsed = max(0, (now - created_at).total_seconds() / 3600.0)
    decay_factor = 1.0 / math.sqrt(1.0 + hours_elapsed / HALF_LIFE_HOURS)
    return round(base_score * decay_factor, 6)


def extract_book_titles(text: str) -> list:
    """从文本中提取《》内的书名"""
    if not text or len(text) > 100000:
        return []
    seen = set()
    titles = []
    for match in BOOK_TITLE_PATTERN.finditer(text):
        title = match.group(1).strip()
        if title and title not in seen:
            seen.add(title)
            titles.append(title)
            if len(titles) >= 20:
                break
    return titles


def match_books_with_titles(titles: list) -> list:
    """将书名与在售书籍模糊匹配"""
    if not titles:
        return []
    from sqlalchemy import or_
    filters = [Book.title.ilike(f'%{t}%') for t in titles]
    all_matched = Book.query.filter(or_(*filters)).all()
    title_to_books = {}
    for book in all_matched:
        for t in titles:
            if t.lower() in book.title.lower():
                if t not in title_to_books:
                    title_to_books[t] = []
                title_to_books[t].append(book)
    matched_books = []
    for title in titles:
        books = title_to_books.get(title, [])
        if books:
            min_price = min(b.price for b in books)
            matched_books.append({
                'title': title, 'matched': True,
                'availableCount': len(books),
                'minPrice': round(min_price, 1),
            })
        else:
            matched_books.append({
                'title': title, 'matched': False,
                'availableCount': 0, 'minPrice': None,
            })
    return matched_books


def sanitize_html(text: str) -> str:
    """基础 XSS 安全转义"""
    if not text:
        return ''
    text = text.replace('&', '&')
    text = text.replace('<', '<')
    text = text.replace('>', '>')
    text = text.replace('"', '"')
    text = text.replace("'", '&#x27;')
    return text


def get_user_info(author_name: str) -> dict:
    """获取作者信息"""
    user = User.query.filter_by(name=author_name).first()
    if user:
        return {'college': user.college or '未设置', 'grade': user.grade or '未知'}
    return {'college': '校友', 'grade': '未知'}