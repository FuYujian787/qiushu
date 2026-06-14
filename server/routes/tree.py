"""知识传承树 API（买卖关系图谱可视化）"""
from flask import Blueprint, request, jsonify
from extensions import db
from models import Order, User, Book
from services.auth import login_required

tree_bp = Blueprint('tree', __name__)


@tree_bp.route('', methods=['GET'])
@login_required
def get_my_tree():
    """获取当前登录用户的知识传承树（默认）"""
    return _build_tree(request.current_user_id)


@tree_bp.route('/<user_id>', methods=['GET'])
def get_user_tree(user_id):
    """获取指定用户的知识传承树（公开查看）"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404
    return _build_tree(user_id)


def _build_tree(user_id, max_depth=4):
    """构建知识传承树 — 递归遍历买卖关系

    使用批量查询优化，避免 N+1 问题。
    以当前用户为根节点，沿买卖关系展开传承图谱。
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': '用户不存在'}), 404

    # 批量预加载所有已完成订单
    all_orders = Order.query.filter_by(status='已完成').order_by(Order.created_at.desc()).all()

    # 按卖家分组
    orders_by_seller = {}
    for order in all_orders:
        orders_by_seller.setdefault(order.seller_id, []).append(order)

    # BFS 构建树
    user_ids = {user_id}
    edges = []
    node_depths = {user_id: 0}
    seen_edges = set()
    queue = [(user_id, 0)]

    while queue:
        seller_id, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        for order in orders_by_seller.get(seller_id, []):
            buyer_id = order.buyer_id
            # 防止自环
            if buyer_id == seller_id:
                continue
            edge_key = (seller_id, buyer_id)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            user_ids.add(buyer_id)

            new_depth = depth + 1
            if buyer_id not in node_depths or node_depths[buyer_id] > new_depth:
                node_depths[buyer_id] = new_depth

            edges.append({
                'from': seller_id,
                'to': buyer_id,
                'book_title': order.book.title if order.book else '',
                'book_id': order.book_id if order.book else None,
                'order_date': order.created_at.isoformat() if order.created_at else None,
            })
            queue.append((buyer_id, new_depth))

    # 批量查询用户信息
    users_map = {u.id: u for u in User.query.filter(User.id.in_(list(user_ids))).all()}

    # 构建节点列表
    nodes = []
    for uid in user_ids:
        u = users_map.get(uid)
        if u:
            nodes.append({
                'id': uid,
                'name': u.nickname or '书友',
                'college': u.college or '',
                'depth': node_depths.get(uid, 0),
            })

    # 统计信息
    stats = {
        'total_nodes': len(nodes),
        'total_edges': len(edges),
        'max_depth': max(node_depths.values()) if node_depths else 0,
        'root_name': users_map.get(user_id).nickname if users_map.get(user_id) else '书友',
    }

    return jsonify({
        'status': 'success',
        'data': {
            'nodes': nodes,
            'edges': edges,
            'stats': stats,
        },
    })
