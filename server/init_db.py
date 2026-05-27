"""
数据库初始化脚本
运行方式：python init_db.py
注意：如果 database.db 已存在，会备份后重建
"""
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')


def init_database(app):
    """初始化数据库并填充种子数据"""
    from models import db, User, Book, Post, Reply, Message

    # 如果数据库已存在，备份
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + '.bak'
        try:
            shutil.copy2(DB_PATH, backup_path)
            print(f'[INFO] 已备份旧数据库至: {backup_path}')
        except Exception as e:
            print(f'[WARN] 备份失败: {e}')

    with app.app_context():
        # 删除旧库
        db.drop_all()
        db.create_all()
        print('[INFO] 数据库表结构创建完成')

        # === 种子用户 ===
        users_data = [
            {'name': '张伟', 'password': '123', 'role': 'buyer', 'college': '管理学院', 'grade': '大三'},
            {'name': '小明', 'password': '321', 'role': 'buyer', 'college': '计算机学院', 'grade': '大二'},
        ]
        for u in users_data:
            user = User(**u)
            db.session.add(user)

        # === 种子书籍（少量示例，10 万级数据由 JSON 文件提供） ===
        # 10 万级虚拟商品数据通过 generate_books_data.py 生成
        # 存储在 client/public/data/books.json，前端通过 Promise(fetch) 加载
        subjects = ['微积分', '线性代数', '大学英语', '有机化学', '数据结构',
                    '概率论', '计算机网络', '操作系统', '高等数学', '考研政治',
                    '微观经济学', '宏观经济学']
        conditions = ['九成新', '八成新', '全新未拆', '有笔记', '七成新']
        authors = ['同济大学', '清华大学', '浙江大学', '外研社']
        category_map = {
            '微积分': '教材', '线性代数': '教材', '大学英语': '教材', '有机化学': '教材',
            '数据结构': '选修', '概率论': '选修', '计算机网络': '选修', '操作系统': '选修',
            '高等数学': '教材', '考研政治': '考研', '微观经济学': '选修', '宏观经济学': '选修',
        }

        import random

        for i in range(20):
            subj = subjects[i % len(subjects)]
            book = Book(
                title=f'{subj} 辅导书 第{i // len(subjects) + 1}版',
                author=authors[i % len(authors)],
                price=round(10 + random.random() * 50, 1),
                old_price=round(30 + random.random() * 80, 1),
                condition=conditions[i % len(conditions)],
                seller=f'同学{100 + (i % 900)}',
                img='R-C.jpg',
                category=category_map.get(subj, '教材'),
            )
            db.session.add(book)

        # === 种子帖子（预设帖，含《》书名用于智能识别联动） ===
        preset_posts = [
            {
                'title': '《微积分》学习心得分享',
                'content': '最近在啃《微积分》辅导书，感觉极限部分最难理解。大家有没有推荐的《微积分》习题集？另外《线性代数》也要开始复习了，求推荐好的教材。',
                'author': '李同学', 'is_preset': True,
                'like_count': 12, 'view_count': 156,
            },
            {
                'title': '四级备考经验：大英这么学',
                'content': '分享一下我的英语四级备考经验，背单词用app，多做真题。《大学英语》教材里的文章一定要精读，对写作帮助很大。',
                'author': '王同学', 'is_preset': True,
                'like_count': 8, 'view_count': 89,
            },
            {
                'title': '《线性代数》几何直观理解法',
                'content': '《线性代数》一定要理解几何意义，推荐3Blue1Brown的视频。配合《高等数学》一起学效果更好，矩阵变换其实就是空间映射。',
                'author': '张伟', 'is_preset': True,
                'like_count': 24, 'view_count': 312,
            },
            {
                'title': '《有机化学》思维导图学习法',
                'content': '《有机化学》需要记忆的内容很多，建议画思维导图，把反应类型归类。推荐《有机化学》第四版配套习题集。',
                'author': '小明', 'is_preset': True,
                'like_count': 5, 'view_count': 67,
            },
            {
                'title': '考研政治复习规划',
                'content': '《考研政治》不用太早开始，暑假开始刷1000题就够了。推荐肖秀荣全套，最后背肖四肖八。',
                'author': '考研学长', 'is_preset': True,
                'like_count': 35, 'view_count': 520,
            },
            {
                'title': '《数据结构》与《计算机网络》学习路线',
                'content': '《数据结构》建议用C语言实现一遍所有算法。《计算机网络》自顶向下方法这本书非常好，配合《操作系统》一起学能建立完整的计算机知识体系。',
                'author': '计科学长', 'is_preset': True,
                'like_count': 18, 'view_count': 203,
            },
        ]
        for pp in preset_posts:
            post = Post(**pp)
            db.session.add(post)
        db.session.flush()  # 获取 post.id

        # === 种子回复 ===
        preset_replies = [
            {'post_id': 1, 'author': '张伟', 'content': '推荐《微积分》同济版，配合吉米多维奇习题集效果很好。', 'like_count': 3},
            {'post_id': 1, 'author': '小明', 'content': '极限部分可以看宋浩老师的视频，讲得很清楚。', 'like_count': 5},
            {'post_id': 2, 'author': '李同学', 'content': '四级单词用墨墨背单词，每天200个，坚持一个月就有效果。', 'like_count': 2},
            {'post_id': 3, 'author': '王同学', 'content': '3Blue1Brown的视频真的是神作，看完豁然开朗。', 'like_count': 7},
            {'post_id': 4, 'author': '张伟', 'content': '有机化学的命名法一定要先搞清楚，不然后面全乱套。', 'like_count': 1},
            {'post_id': 5, 'author': '小明', 'content': '肖秀荣yyds！去年政治考了75分。', 'like_count': 12},
            {'post_id': 6, 'author': '李同学', 'content': '数据结构建议用《算法导论》作为进阶读物。', 'like_count': 4},
        ]
        for rp in preset_replies:
            reply = Reply(**rp)
            db.session.add(reply)

        db.session.commit()
        print(f'[INFO] 种子数据填充完成：')
        print(f'  - 用户: {len(users_data)} 个')
        print(f'  - 书籍: 20 本（示例）+ 10 万级虚拟数据（JSON 文件）')
        print(f'  - 预设帖子: {len(preset_posts)} 个')
        print(f'  - 预设回复: {len(preset_replies)} 个')
        print(f'  - 消息表: 已创建（Message 模型）')


    print(f'[INFO] 数据库位置: {DB_PATH}')


if __name__ == '__main__':
    # 独立运行时创建临时 app 来初始化
    from flask import Flask
    from config import DATABASE_URI, SECRET_KEY

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY

    from models import db
    db.init_app(app)

    init_database(app)
    print('[DONE] 初始化完成')
