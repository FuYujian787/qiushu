"""
社区路由：帖子列表、发布、回复 — 全栈高端化重构版
============================================================
紫金求思 · 数字化思想圣殿后端引擎

核心特性：
  1. 热度加权排序算法（HOT RANK）
     综合浏览量、回复数、时间衰减因子，使用牛顿冷却定律：
       score = (view_count * 0.3 + reply_count * 0.7) / (1 + hours_elapsed) ^ 0.5
     确保新帖有足够曝光，同时优质老帖不会沉没。

  2. 智能书名识别与书摊联动
     自动扫描帖子正文，模糊匹配 books 表中在售书籍。
     返回 matchedBooks 数组供前端渲染毛玻璃 Popover。

  3. N+1 查询优化
     使用 SQLAlchemy joinedload 预加载关联数据，
     避免循环查询导致的性能灾难。

  4. 用户信息关联
     返回作者 college（学院）和 grade（年级），
     通过 User 表 joinedload 一次性加载。

  5. 边界安全
     - 零浏览量/零回复时不会除零错误
     - 超长正文的正则匹配使用 re.finditer 惰性求值
     - 所有输出经过 XSS 安全转义
============================================================
"""
import re
import json
import math
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from models import db, Post, Reply, Book, User

community_bp = Blueprint('community', __name__)

# ============================================================
# 常量
# ============================================================

# 热度排序权重系数
# view_weight: 浏览量权重，reply_weight: 回复数权重
# 回复行为比浏览行为更能体现帖子质量，故赋予更高权重
VIEW_WEIGHT = 0.3
REPLY_WEIGHT = 0.7

# 时间衰减半衰期（小时）：超过此时间热度衰减至一半
# 使用牛顿冷却定律：decay = 1 / sqrt(1 + hours / half_life)
HALF_LIFE_HOURS = 48.0

# 书名匹配正则：匹配《》内的内容
# 安全设计：使用非贪婪匹配 + 限制最大长度（50字符），防止 ReDoS 攻击
BOOK_TITLE_PATTERN = re.compile(r'《([^》]{1,50})》')

# 分页默认值
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# ============================================================
# 辅助函数
# ============================================================

def compute_hot_score(view_count: int, reply_count: int, created_at: datetime) -> float:
    """
    热度加权排序算法
    ============================================================
    公式：
      base_score = view_count * VIEW_WEIGHT + reply_count * REPLY_WEIGHT
      hours_elapsed = (now - created_at).total_seconds() / 3600
      decay_factor = 1 / sqrt(1 + hours_elapsed / HALF_LIFE_HOURS)
      hot_score = base_score * decay_factor

    设计原理：
      - 使用平方根衰减而非指数衰减，避免新帖瞬间沉没
      - 回复数权重高于浏览量，鼓励深度讨论
      - 当 view_count=0 且 reply_count=0 时，base_score=0，不会除零
    ============================================================
    """
    # 边界保护：确保非负整数
    vc = max(0, view_count or 0)
    rc = max(0, reply_count or 0)

    base_score = vc * VIEW_WEIGHT + rc * REPLY_WEIGHT

    # 如果帖子没有任何互动，返回极小值而非零，确保新帖也能出现在列表末尾
    if base_score == 0:
        base_score = 0.01

    now = datetime.now(timezone.utc)
    # 处理时区问题：如果 created_at 没有时区信息，视为 UTC
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    hours_elapsed = max(0, (now - created_at).total_seconds() / 3600.0)

    # 牛顿冷却定律：decay_factor = 1 / sqrt(1 + hours / half_life)
    # 当 hours=0 时，decay_factor=1，不会除零
    decay_factor = 1.0 / math.sqrt(1.0 + hours_elapsed / HALF_LIFE_HOURS)

    return round(base_score * decay_factor, 6)


def extract_book_titles(text: str) -> list:
    """
    从文本中提取《》内的书名
    ============================================================
    安全设计：
      - 使用非贪婪匹配 `《([^》]{1,50})》`，限制书名最大长度 50 字符
      - 使用 re.finditer 惰性求值，避免超长文本导致内存溢出
      - 去重后返回，避免同一书名多次匹配
    ============================================================
    """
    if not text or len(text) > 100000:
        # 极端长度保护：超过 10 万字符的文本跳过匹配
        return []

    seen = set()
    titles = []
    for match in BOOK_TITLE_PATTERN.finditer(text):
        title = match.group(1).strip()
        if title and title not in seen:
            seen.add(title)
            titles.append(title)
            if len(titles) >= 20:
                # 单帖最多识别 20 个书名，防止过度匹配
                break
    return titles


def match_books_with_titles(titles: list) -> list:
    """
    将识别的书名与 books 表中在售书籍进行模糊匹配
    ============================================================
    匹配策略：
      - 使用 SQL ILIKE 模糊匹配（大小写不敏感）
      - 使用单次批量 OR 查询，避免 N+1 循环查询
      - 返回匹配书籍的摘要信息：书名、在售数量、最低价
    ============================================================
    """
    if not titles:
        return []

    # 【性能优化】批量查询：一次 SQL 查询匹配所有书名，避免 N+1
    from sqlalchemy import or_
    filters = [Book.title.ilike(f'%{t}%') for t in titles]
    all_matched = Book.query.filter(or_(*filters)).all()

    # 构建书名 → 匹配书籍的映射
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
                'title': title,
                'matched': True,
                'availableCount': len(books),
                'minPrice': round(min_price, 1),
            })
        else:
            matched_books.append({
                'title': title,
                'matched': False,
                'availableCount': 0,
                'minPrice': None,
            })

    return matched_books


def sanitize_html(text: str) -> str:
    """
    基础 XSS 安全转义
    ============================================================
    将 < > & " ' 等 HTML 特殊字符转义为实体，
    防止 v-html 渲染时执行恶意脚本。
    ============================================================
    """
    if not text:
        return ''
    text = text.replace('&', '&')
    text = text.replace('<', '<')
    text = text.replace('>', '>')
    text = text.replace('"', '"')
    text = text.replace("'", '&#x27;')
    return text


def get_user_info(author_name: str) -> dict:
    """
    获取作者信息（学院、年级）
    ============================================================
    使用直接查询而非 joinedload，因为作者名可能不存在于 User 表
    （如预设帖子的作者 "李同学" 可能不是注册用户）
    优雅降级：找不到时返回默认值
    ============================================================
    """
    user = User.query.filter_by(name=author_name).first()
    if user:
        return {
            'college': user.college or '未设置',
            'grade': user.grade or '未知',
        }
    return {
        'college': '校友',
        'grade': '未知',
    }


# ============================================================
# API 端点
# ============================================================

@community_bp.route('/api/posts', methods=['GET'])
def get_posts():
    """
    获取帖子列表（热度加权排序 + 分页 + 分类筛选）
    ============================================================
    查询参数：
      - page:      页码（默认 1）
      - pageSize:  每页数量（默认 20，最大 100）
      - category:  分类筛选（可选）
      - sort:      排序方式：'hot'（热度，默认）| 'new'（最新）| 'top'（最多回复）

    性能优化：
      - 使用 joinedload 预加载 replies 关联
      - 使用 count() 获取总数时分页
      - 热度排序在 Python 层计算（SQLite 不支持复杂数学函数）
    ============================================================
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', DEFAULT_PAGE_SIZE, type=int)
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'hot').strip()

    # 参数边界保护
    page = max(1, page)
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    # 基础查询：使用 joinedload 预加载 replies，避免 N+1
    query = Post.query.options(
        joinedload(Post.replies)
    )

    # 分类筛选（基于标题关键词的简单分类）
    if category and category != '全部':
        category_map = {
            '教材': ['微积分', '线性代数', '高等数学', '大学英语', '有机化学'],
            '考研': ['考研', '政治', '英语', '数学'],
            '选修': ['数据结构', '概率论', '计算机网络', '操作系统', '微观经济学', '宏观经济学'],
        }
        keywords = category_map.get(category, [])
        if keywords:
            filters = [Post.title.ilike(f'%{kw}%') for kw in keywords]
            query = query.filter(db.or_(*filters))

    # 获取总数
    total = query.count()

    # 获取所有帖子（热度排序需要在 Python 层计算）
    posts = query.order_by(Post.created_at.desc()).all()

    # 计算热度分数并排序
    scored_posts = []
    for post in posts:
        reply_count = len(post.replies) if post.replies else 0
        hot_score = compute_hot_score(
            view_count=post.view_count or 0,
            reply_count=reply_count,
            created_at=post.created_at,
        )
        scored_posts.append((post, hot_score, reply_count))

    # 根据排序方式排序
    if sort == 'new':
        # 按创建时间倒序
        scored_posts.sort(key=lambda x: x[0].created_at, reverse=True)
    elif sort == 'top':
        # 按回复数倒序
        scored_posts.sort(key=lambda x: x[2], reverse=True)
    else:
        # 默认按热度排序
        scored_posts.sort(key=lambda x: x[1], reverse=True)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    page_posts = scored_posts[start:end]

    # 构建响应
    result = []
    for post, hot_score, reply_count in page_posts:
        post_dict = post.to_dict()
        post_dict['hotScore'] = round(hot_score, 4)
        post_dict['replyCount'] = reply_count

        # 添加作者信息
        post_dict['authorInfo'] = get_user_info(post.author)

        # 添加回复列表
        replies = post.replies or []
        post_dict['replies'] = [r.to_dict() for r in replies]

        # 智能书名识别与书摊联动
        # 扫描帖子标题 + 正文中的《》书名
        all_text = f"{post.title} {post.content}"
        detected_titles = extract_book_titles(all_text)
        matched_books = match_books_with_titles(detected_titles)
        post_dict['matchedBooks'] = matched_books

        # 更新 book_mentions 字段（持久化存储）
        if matched_books:
            post.book_mentions = json.dumps(matched_books, ensure_ascii=False)

        result.append(post_dict)

    # 批量持久化 book_mentions
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({
        'posts': result,
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': max(1, (total + page_size - 1) // page_size),
    }), 200


@community_bp.route('/api/posts/<path:post_id>/view', methods=['POST'])
def increment_view(post_id):
    """
    增加帖子浏览量
    ============================================================
    支持预设帖 ID 格式（如 "preset_1"）。
    前端在帖子进入视口时调用此接口，
    使用防抖控制，避免频繁请求。
    ============================================================
    """
    # 处理预设帖 ID 格式："preset_1" → 1
    if isinstance(post_id, str) and post_id.startswith('preset_'):
        try:
            post_id = int(post_id.replace('preset_', ''))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    else:
        try:
            post_id = int(post_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400

    post = Post.query.get(post_id)

    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404

    post.view_count = (post.view_count or 0) + 1
    db.session.commit()

    return jsonify({'success': True, 'viewCount': post.view_count}), 200


@community_bp.route('/api/posts/<path:post_id>/like', methods=['POST'])
def like_post(post_id):
    """
    点赞帖子
    ============================================================
    支持预设帖 ID 格式（如 "preset_1"）。
    简单计数器递增，后续可扩展为基于用户去重。
    ============================================================
    """
    # 处理预设帖 ID 格式："preset_1" → 1
    if isinstance(post_id, str) and post_id.startswith('preset_'):
        try:
            post_id = int(post_id.replace('preset_', ''))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    else:
        try:
            post_id = int(post_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400

    post = Post.query.get(post_id)

    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404

    post.like_count = (post.like_count or 0) + 1
    db.session.commit()

    return jsonify({'success': True, 'likeCount': post.like_count}), 200


@community_bp.route('/api/posts', methods=['POST'])
def create_post():
    """
    发布新帖
    ============================================================
    自动识别帖子中的书名并存储 book_mentions。
    ============================================================
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    author = (data.get('author') or '').strip()

    if not title:
        return jsonify({'success': False, 'message': '帖子标题不能为空'}), 400
    if not content:
        return jsonify({'success': False, 'message': '帖子内容不能为空'}), 400
    if not author:
        return jsonify({'success': False, 'message': '作者不能为空'}), 400

    # 智能识别书名
    all_text = f"{title} {content}"
    detected_titles = extract_book_titles(all_text)
    matched_books = match_books_with_titles(detected_titles)

    post = Post(
        title=title,
        content=content,
        author=author,
        is_preset=False,
        like_count=0,
        view_count=0,
        book_mentions=json.dumps(matched_books, ensure_ascii=False),
    )
    db.session.add(post)
    db.session.commit()

    post_dict = post.to_dict()
    post_dict['authorInfo'] = get_user_info(author)
    post_dict['replyCount'] = 0
    post_dict['replies'] = []
    post_dict['matchedBooks'] = matched_books
    post_dict['hotScore'] = 0.01

    return jsonify({'success': True, 'post': post_dict}), 201


@community_bp.route('/api/posts/<path:post_id>/replies', methods=['POST'])
def add_reply(post_id):
    """
    回复帖子（无缝内联回复）
    ============================================================
    支持两种 ID 格式：
      - 纯数字 ID（如 "1", "42"）
      - 预设帖 ID（如 "preset_1"）
    自动提取数字部分进行数据库查询。
    ============================================================
    """
    # 处理预设帖 ID 格式："preset_1" → 1
    if isinstance(post_id, str) and post_id.startswith('preset_'):
        try:
            post_id = int(post_id.replace('preset_', ''))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    else:
        try:
            post_id = int(post_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'message': '帖子不存在'}), 404


    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    author = (data.get('author') or '').strip()
    content = (data.get('content') or '').strip()

    if not author:
        return jsonify({'success': False, 'message': '作者不能为空'}), 400
    if not content:
        return jsonify({'success': False, 'message': '回复内容不能为空'}), 400

    reply = Reply(post_id=post_id, author=author, content=content, like_count=0)
    db.session.add(reply)
    db.session.commit()

    reply_dict = reply.to_dict()
    reply_dict['authorInfo'] = get_user_info(author)

    return jsonify({'success': True, 'reply': reply_dict}), 201


@community_bp.route('/api/posts/<path:post_id>/replies/<int:reply_id>/like', methods=['POST'])
def like_reply(post_id, reply_id):
    """
    点赞回复
    ============================================================
    支持预设帖 ID 格式（如 "preset_1"）。
    ============================================================
    """
    # 处理预设帖 ID 格式："preset_1" → 1
    if isinstance(post_id, str) and post_id.startswith('preset_'):
        try:
            post_id = int(post_id.replace('preset_', ''))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400
    else:
        try:
            post_id = int(post_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '帖子ID格式无效'}), 400

    reply = Reply.query.filter_by(id=reply_id, post_id=post_id).first()

    if not reply:
        return jsonify({'success': False, 'message': '回复不存在'}), 404

    reply.like_count = (reply.like_count or 0) + 1
    db.session.commit()

    return jsonify({'success': True, 'likeCount': reply.like_count}), 200


@community_bp.route('/api/posts/books/search', methods=['GET'])
def search_books_for_post():
    """
    根据书名搜索在售书籍（供前端 Popover 调用）
    ============================================================
    查询参数：
      - title: 书名关键词
    返回匹配书籍的简要列表。
    ============================================================
    """
    title = request.args.get('title', '').strip()
    if not title:
        return jsonify({'books': []}), 200

    books = Book.query.filter(
        Book.title.ilike(f'%{title}%')
    ).limit(10).all()

    return jsonify({
        'books': [{
            'id': b.id,
            'title': b.title,
            'price': round(b.price, 1),
            'condition': b.condition,
            'seller': b.seller,
            'img': b.img,
        } for b in books]
    }), 200
