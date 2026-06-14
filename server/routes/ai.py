"""AI 功能 API（对话/定价/推荐/摘要）"""
from flask import Blueprint, request, jsonify
import json
import re
from extensions import db, limiter
from models import AILog, Book, Review, UserCourse, Course, Favorite
from services.auth import login_required
from services.ai_client import call_deepseek, ai_suggest_price

ai_bp = Blueprint('ai', __name__)

# System Prompt for AI Chat Assistant
SYSTEM_PROMPT = """你是"求书小助手"，一个服务于浙江大学校内二手书交易平台的AI助手。

你的职责：
1. 解答用户关于二手书交易的疑问（价格咨询、书况评估、书籍推荐）
2. 帮助用户理解平台功能（如何发布、如何购买、如何交换）
3. 提供课程-教材匹配建议（用户说"我选了线性代数，需要什么教材？"）
4. 回答校园生活相关问题（选课建议、学习资源推荐）
5. 始终保持友好、专业、有温度的浙大学长/学姐口吻

限制：
- 不回答与书籍、学习、校园生活无关的问题
- 不确定的事情诚实说"不确定"，不编造信息
- 回复简洁，控制在 200 字以内
- 可以适当使用浙大相关的梗和归属感语言
"""


@ai_bp.route('/chat', methods=['POST'])
@login_required
@limiter.limit('30 per minute')
def chat():
    """AI 对话"""
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    history = data.get('history', [])

    if not user_message:
        return jsonify({'status': 'error', 'message': '请输入消息'}), 400

    # 基本输入校验
    if len(user_message) > 500:
        return jsonify({'status': 'error', 'message': '消息过长，请控制在 500 字以内'}), 400

    # 构建消息
    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    # 添加上下文信息
    try:
        from services.ai_chat import get_user_context
        user_context = get_user_context(request.current_user_id)
        if user_context:
            messages.append({'role': 'system', 'content': f'当前用户信息: {user_context}'})
    except Exception:
        pass

    # 添加历史对话（最近 10 轮）
    if history:
        for msg in history[-10:]:
            # 只保留 role 和 content 字段
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                messages.append({'role': msg['role'], 'content': msg['content']})

    messages.append({'role': 'user', 'content': user_message})

    try:
        reply = call_deepseek(messages, temperature=0.7, max_tokens=512)

        # 记录日志（截断长文本）
        log = AILog(
            user_id=request.current_user_id,
            type='对话',
            input_data=user_message[:500],
            output_data=reply[:500],
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({'status': 'success', 'data': {'reply': reply}})
    except Exception:
        return jsonify({
            'status': 'success',
            'data': {'reply': '抱歉，AI 服务暂时不可用，请稍后再试。'},
        })


@ai_bp.route('/price', methods=['POST'])
@login_required
def price():
    """AI 定价建议"""
    data = request.get_json() or {}
    book_title = data.get('title', '')
    author = data.get('author', '')
    isbn = data.get('isbn', '')
    condition = data.get('condition', '良好')
    original_price = data.get('original_price')

    try:
        result = ai_suggest_price(
            book_title, author, isbn, condition,
            original_price=float(original_price) if original_price else None,
        )

        log = AILog(
            user_id=request.current_user_id,
            type='定价',
            input_data=str(data),
            output_data=str(result),
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@ai_bp.route('/recommend', methods=['GET'])
@login_required
def recommend():
    """AI 个性化推荐"""
    try:
        from services.ai_recommend import recommend_books
        result = recommend_books(request.current_user_id)
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'success', 'data': [], 'message': str(e)})


@ai_bp.route('/summarize/<book_id>', methods=['GET'])
def summarize_reviews(book_id):
    """AI 评价摘要（评论 > 10 条时触发，无需登录即可查看）"""
    reviews = Review.query.filter_by(book_id=book_id).all()
    if len(reviews) < 10:
        return jsonify({'status': 'success', 'data': None, 'message': '评论数不足 10 条'})

    review_text = '\n'.join(f'评分{r.rating}: {r.comment}' for r in reviews if r.comment)

    try:
        summary = call_deepseek([
            {'role': 'system', 'content': '请用 2-3 句话总结以下用户评价的共同观点，语言简练。'},
            {'role': 'user', 'content': review_text[:2000]},
        ], temperature=0.3, max_tokens=200)

        return jsonify({'status': 'success', 'data': {'summary': summary, 'review_count': len(reviews)}})
    except Exception:
        return jsonify({'status': 'success', 'data': None, 'message': '摘要生成失败'})


@ai_bp.route('/textbooks', methods=['POST'])
@login_required
def recommend_textbooks():
    """AI 教材推荐 — 根据课程列表推荐教材并匹配平台二手书

    请求体:
        {
            'courses': [{'name': '微积分Ⅱ（H）', ...}, ...],
            'use_ai': true   // 是否启用 AI（未命中预置库时）
        }

    返回:
        {
            'recommendations': [
                {
                    'course_name': '微积分Ⅱ（H）',
                    'textbooks': [
                        {
                            'title': '微积分（下册）',
                            'author': '同济大学数学系',
                            'isbn': '9787040445155',
                            'publisher': '高等教育出版社',
                            'source': 'preset',          // 'preset' | 'ai'
                            'matched_books': [...],      // 平台在售匹配
                            'match_count': 0
                        }
                    ]
                }
            ]
        }
    """
    data = request.get_json() or {}
    courses = data.get('courses', [])
    use_ai = data.get('use_ai', True)

    if not courses:
        return jsonify({'status': 'error', 'message': '请提供课程列表'}), 400

    try:
        from services.ai_textbook import recommend_textbooks_for_courses, match_platform_books

        # Step 1: 推荐教材（预置库 + AI）
        recommendations = recommend_textbooks_for_courses(courses, use_ai=use_ai)

        # Step 2: 匹配平台在售二手书
        from models import Book as BookModel
        available_books = BookModel.query.filter_by(status='在售').all()
        available_list = [b.to_dict() for b in available_books]

        recommendations = match_platform_books(recommendations, available_list)

        # 统计
        total_matches = sum(
            1 for rec in recommendations
            for tb in rec.get('textbooks', [])
            if tb.get('match_count', 0) > 0
        )

        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': recommendations,
                'total_courses': len(courses),
                'courses_with_textbooks': sum(1 for r in recommendations if r.get('textbooks')),
                'total_platform_matches': total_matches,
            },
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'教材推荐失败: {str(e)}'}), 500
