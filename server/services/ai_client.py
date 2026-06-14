"""DeepSeek API 封装"""
import json
import os
import requests

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'


def call_deepseek(messages: list, temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """调用 DeepSeek API"""
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': 'deepseek-chat',
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'stream': False,  # 非流式响应，直接返回完整 JSON
    }
    try:
        resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            raise Exception(f'DeepSeek API 调用失败: {resp.text}')
        data = resp.json()
        return data['choices'][0]['message']['content']
    except requests.RequestException:
        raise Exception('AI 服务暂时不可用，请稍后再试')


def _sanitize_prompt_input(text: str, max_len: int = 200) -> str:
    """清理用户输入以防 prompt injection

    仅做最小化安全处理：截断长度 + 转义花括号。
    不过滤正常中文词汇（如"系统""指令"），避免误伤书名。
    """
    if not text:
        return ''
    # 截断长度
    text = text[:max_len]
    # 转义花括号防止 JSON 注入（DeepSeek 可能误解析）
    text = text.replace('{', '｛').replace('}', '｝')
    # 仅过滤明确的 prompt injection 分隔符
    # 不过滤"系统""指令""忽略"等正常中文词 — 它们可能出现在书名中
    return text.strip()


def _get_local_price_history(book_title: str, isbn: str) -> dict:
    """查询本地数据库中同书名/ISBN 的已成交订单，计算历史价格统计"""
    try:
        from models import Order, Book
        from extensions import db as _db

        # 查询已完成订单
        completed_orders = Order.query.filter_by(status='已完成').all()

        # 筛选同书名或同 ISBN 的订单
        matching_prices = []
        for order in completed_orders:
            if order.book:
                title_match = book_title and (
                    book_title.lower() in (order.book.title or '').lower()
                    or (order.book.title or '').lower() in book_title.lower()
                )
                isbn_match = isbn and order.book.isbn == isbn
                if title_match or isbn_match:
                    # 优先使用订单关联书籍的价格
                    if order.book.price:
                        matching_prices.append(order.book.price)

        if not matching_prices:
            return {'count': 0, 'avg_price': None, 'min_price': None, 'max_price': None}

        return {
            'count': len(matching_prices),
            'avg_price': round(sum(matching_prices) / len(matching_prices), 1),
            'min_price': round(min(matching_prices), 1),
            'max_price': round(max(matching_prices), 1),
        }
    except Exception:
        return {'count': 0, 'avg_price': None, 'min_price': None, 'max_price': None}


def ai_suggest_price(book_title: str, author: str, isbn: str, condition: str,
                     original_price: float = None) -> dict:
    """AI 定价建议

    定价策略：
    1. 查询本地历史成交数据（同书名/ISBN 的已完成订单）
    2. 结合原始定价、书况、历史数据构建 prompt
    3. 调用 DeepSeek 获取 AI 建议区间
    4. 如果 DeepSeek 不可用，用本地历史数据 + 书况系数估算

    书况折价系数（参考浙大二手书市场惯例）：
    - 全新: 原价 50%-70%（教材折价快）
    - 良好: 原价 30%-50%
    - 有笔记: 原价 20%-40%
    - 旧: 原价 10%-30%
    """
    clean_title = _sanitize_prompt_input(book_title)
    clean_author = _sanitize_prompt_input(author)
    valid_conditions = {'全新', '良好', '有笔记', '旧'}
    clean_condition = condition if condition in valid_conditions else '良好'

    # 查询本地历史数据
    history = _get_local_price_history(book_title, isbn)

    # 构建 prompt
    history_text = ''
    if history['count'] > 0:
        history_text = f"""
    - 浙大历史成交: {history['count']} 笔
    - 历史均价: ¥{history['avg_price']}
    - 历史最低: ¥{history['min_price']}
    - 历史最高: ¥{history['max_price']}"""

    original_text = f'\n    - 原价: ¥{original_price}' if original_price else ''

    prompt = f"""你是浙大二手书市场的价格分析师。请基于以下信息给出建议售价区间：
    - 书名: {clean_title}
    - 作者: {clean_author}
    - 书况: {clean_condition}{original_text}{history_text}

    请返回 JSON: {{"min": 最低建议价, "max": 最高建议价, "reason": "简短定价理由"}}
    """

    # 尝试 AI 定价
    try:
        response = call_deepseek([
            {'role': 'system', 'content': '你是一位专业的二手书价格分析师。请只返回 JSON 格式结果，不要有其他文字。请严格按 JSON 格式返回，键名用英文双引号。'},
            {'role': 'user', 'content': prompt},
        ], temperature=0.3, max_tokens=256)

        # 从返回文本中提取 JSON（可能包含 markdown 代码块包裹）
        import re
        json_match = re.search(r'\{[^}]+\}', response)
        if json_match:
            result = json.loads(json_match.group())
            # 确保返回的字段存在
            if 'min' in result and 'max' in result:
                result['source'] = 'ai'
                result['history_count'] = history['count']
                return result
    except Exception:
        pass  # AI 失败，降级到本地估算

    # === 降级：本地数据估算 ===
    condition_ratios = {
        '全新': (0.50, 0.70),
        '良好': (0.30, 0.50),
        '有笔记': (0.20, 0.40),
        '旧': (0.10, 0.30),
    }
    ratio_low, ratio_high = condition_ratios.get(clean_condition, (0.20, 0.50))

    # 优先使用历史均价，其次使用原价
    base_price = None
    if history['avg_price']:
        base_price = history['avg_price']
    elif original_price and original_price > 0:
        base_price = original_price

    if base_price:
        min_price = max(1, round(base_price * ratio_low))
        max_price = max(min_price + 1, round(base_price * ratio_high))
        return {
            'min': min_price,
            'max': max_price,
            'reason': f'基于{"历史均价" if history["avg_price"] else "原价"}¥{base_price} 及书况「{clean_condition}」估算',
            'source': 'local_estimate',
            'history_count': history['count'],
        }

    # 完全没有数据 — 返回保守估计
    return {
        'min': 5,
        'max': 30,
        'reason': '暂无该书的历史成交数据，建议参考同类教材定价',
        'source': 'fallback',
        'history_count': 0,
    }
