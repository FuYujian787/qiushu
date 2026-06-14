from flask import Blueprint, request, jsonify
import requests

isbn_bp = Blueprint('isbn', __name__)

# 模拟图书数据（用于测试）
mock_books = {
    "9787040444560": {
        "title": "高等数学（第七版）上册",
        "author": "同济大学数学系",
        "publisher": "高等教育出版社",
        "price": "49.80",
        "image": "https://img1.doubanio.com/lpic/s27269103.jpg"
    },
    "9787040453558": {
        "title": "线性代数（第六版）",
        "author": "同济大学数学系",
        "publisher": "高等教育出版社",
        "price": "31.50",
        "image": "https://img1.doubanio.com/lpic/s27733723.jpg"
    },
    "9787111529447": {
        "title": "Python编程：从入门到实践",
        "author": "[美] 埃里克·马瑟斯",
        "publisher": "人民邮电出版社",
        "price": "89.00",
        "image": "https://img1.doubanio.com/lpic/s28297175.jpg"
    },
    "9787111407010": {
        "title": "深入理解计算机系统",
        "author": "[美] Randal E.Bryant / [美] David O'Hallaron",
        "publisher": "机械工业出版社",
        "price": "129.00",
        "image": "https://img1.doubanio.com/lpic/s26912133.jpg"
    },
    "9787115335679": {
        "title": "数据结构与算法分析（C语言描述）",
        "author": "[美] Mark Allen Weiss",
        "publisher": "人民邮电出版社",
        "price": "69.00",
        "image": "https://img1.doubanio.com/lpic/s27242088.jpg"
    }
}


def clean_isbn(isbn):
    """清理 ISBN 码，去除连字符和空格"""
    return isbn.replace('-', '').replace(' ', '').strip()


def is_valid_isbn(isbn):
    """验证 ISBN 码的有效性"""
    isbn = clean_isbn(isbn)
    
    if len(isbn) == 13:
        # ISBN-13 校验
        try:
            digits = [int(c) for c in isbn]
            total = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
            check_digit = (10 - (total % 10)) % 10
            return check_digit == digits[12]
        except ValueError:
            return False
    elif len(isbn) == 10:
        # ISBN-10 校验
        try:
            total = 0
            for i in range(9):
                total += int(isbn[i]) * (10 - i)
            last_char = isbn[9].upper()
            check_digit = 10 if last_char == 'X' else int(last_char)
            return (total + check_digit) % 11 == 0
        except ValueError:
            return False
    else:
        return False


def search_book_by_isbn(isbn):
    """通过 ISBN 查询图书信息"""
    isbn_clean = clean_isbn(isbn)
    
    # 优先从模拟数据中查找
    if isbn_clean in mock_books:
        return mock_books[isbn_clean]
    
    # 尝试调用豆瓣图书 API
    try:
        url = f"https://api.douban.com/v2/book/isbn/{isbn_clean}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title", ""),
                "author": "/".join(data.get("author", [])),
                "publisher": data.get("publisher", ""),
                "price": data.get("price", ""),
                "image": data.get("image", "")
            }
    except Exception as e:
        print(f"Error fetching from Douban API: {e}")
    
    return None


@isbn_bp.route('/api/isbn/search', methods=['GET'])
def search_isbn():
    """ISBN 查询接口"""
    isbn = request.args.get('code', '')
    
    if not isbn:
        return jsonify({"success": False, "message": "请提供 ISBN 码"})
    
    if not is_valid_isbn(isbn):
        return jsonify({"success": False, "message": "请输入有效的 ISBN 码"})
    
    book_info = search_book_by_isbn(isbn)
    
    if book_info:
        return jsonify({"success": True, "data": book_info})
    else:
        return jsonify({"success": False, "message": "未找到该图书信息"})


@isbn_bp.route('/api/isbn/validate', methods=['GET'])
def validate_isbn():
    """ISBN 验证接口"""
    isbn = request.args.get('code', '')
    
    if not isbn:
        return jsonify({"success": False, "message": "请提供 ISBN 码"})
    
    is_valid = is_valid_isbn(isbn)
    return jsonify({"success": True, "data": {"is_valid": is_valid}})
