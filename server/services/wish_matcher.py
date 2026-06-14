"""求书许愿墙匹配服务

当新书籍发布后，检查是否匹配现有的求书帖，生成匹配通知。
"""
from models import WantedBook, Book


def find_matches_for_wish(wish: WantedBook, limit: int = 5) -> list[Book]:
    """根据求书帖查找匹配的在售书籍

    Args:
        wish: WantedBook 实例
        limit: 返回数量上限

    Returns:
        [Book, ...] 匹配的在售书籍列表
    """
    if not wish.title:
        return []

    query = Book.query.filter(
        Book.title.contains(wish.title),
        Book.status == '在售',
    )

    if wish.author:
        query = query.filter(Book.author.contains(wish.author))

    if wish.isbn:
        isbn_match = Book.query.filter(Book.isbn == wish.isbn, Book.status == '在售').first()
        if isbn_match:
            return [isbn_match]

    return query.limit(limit).all()


def find_matches_for_book(book: Book) -> list[WantedBook]:
    """当新书发布时，查找匹配的求书帖

    Args:
        book: 新发布的 Book 实例

    Returns:
        [WantedBook, ...] 匹配的求书帖
    """
    if not book.title:
        return []

    wishes = WantedBook.query.filter(
        WantedBook.title.contains(book.title[:10]),
        WantedBook.status == '求购中',
    ).all()

    return wishes


def get_match_summary(wish_id: str) -> dict:
    """获取某条求书帖的匹配摘要

    Args:
        wish_id: 求书帖 UUID

    Returns:
        {wish, matched_books: [...]}
    """
    wish = WantedBook.query.get(wish_id)
    if not wish:
        return {'wish': None, 'matched_books': []}

    matched = find_matches_for_wish(wish)
    return {
        'wish': wish.to_dict(),
        'matched_books': [b.to_dict() for b in matched],
    }
