"""10万级虚拟数据生成 + 课程预置数据

Usage: python seed_data.py
输出: client/public/mock/books_100k.json
"""
import json
import os
import random
import uuid

# 课程
COURSES = [
    '高等数学', '线性代数', '概率论', '数据结构', '计算机组成原理',
    '操作系统', '计算机网络', '数据库系统', 'Python程序设计', 'C++程序设计',
    'Java程序设计', '算法导论', '大学英语', '大学物理', '马克思主义原理',
    '毛泽东思想概论', '微观经济学', '宏观经济学',
]
# 作者
AUTHORS = [
    '同济大学数学系', '严蔚敏', 'David Patterson', 'Brian Kernighan',
    '吴军', '周志华', 'N. Gregory Mankiw', '张三慧', 'Larry L. Peterson',
    'Eric Matthes', 'Stanley B. Lippman', 'Joshua Bloch', 'Thomas H. Cormen',
    'Andrew S. Tanenbaum', 'Abraham Silberschatz', 'Randal E. Bryant',
    '张宇', '汤家凤',
]
# 书况
CONDITIONS = ['全新', '良好', '有笔记', '旧']
# 分类
CATEGORIES = ['数学', '计算机', '外语', '经管', '理工', '人文']
# 学院
COLLEGES = ['计算机学院', '数学学院', '外语学院', '管理学院', '信电学院', '人文学院']
# 姓氏
LAST_NAMES = ['张', '李', '王', '陈', '刘', '周', '吴', '赵', '孙', '徐', '黄', '胡', '朱', '高', '何', '罗', '梁', '宋', '郑', '谢']

# 20 张复用图片
IMAGES = [f'images/book_{i}.jpg' for i in range(1, 21)]


def generate_books(n=100000):
    """生成 n 条虚拟书籍数据"""
    books = []
    for i in range(n):
        course = random.choice(COURSES)
        author = random.choice(AUTHORS)
        category = COURSES_TO_CATEGORY.get(course, random.choice(CATEGORIES))
        condition = random.choice(CONDITIONS)
        price = round(random.uniform(5, 80), 1)
        original_price = round(price + random.uniform(10, 70), 1)
        college = random.choice(COLLEGES)
        last_name = random.choice(LAST_NAMES)
        seller = f'{college}{last_name}同学'

        # 生成标题变体
        edition = random.randint(1, 9)
        suffix = random.choice(['', f'（第{edition}版）', f'（{edition}版）', f' {edition}th ed.'])
        title = f'{course}{suffix}' if suffix else f'{course}'

        book = {
            'id': str(uuid.uuid4()),
            'title': title,
            'author': author,
            'isbn': random_isbn(),
            'category': category,
            'price': price,
            'original_price': original_price,
            'condition': condition,
            'seller': seller,
            'seller_college': college,
            'description': f'这是一本{course}教材，由{author}编写，{condition}，适合浙大{college}学生使用。',
            'image': random.choice(IMAGES),
            'created_at': f'2026-{random.randint(1, 6):02d}-{random.randint(1, 28):02d}',
            'status': '在售',
        }
        books.append(book)

        if (i + 1) % 10000 == 0:
            print(f'  [{i+1}]条已生成...')

    return books


def random_isbn():
    """生成随机 ISBN-13"""
    prefix = '978'
    body = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    return prefix + body


# 课程 → 分类映射
COURSES_TO_CATEGORY = {
    '高等数学': '数学', '线性代数': '数学', '概率论': '数学',
    '数据结构': '计算机', '计算机组成原理': '计算机', '操作系统': '计算机',
    '计算机网络': '计算机', '数据库系统': '计算机', 'Python程序设计': '计算机',
    'C++程序设计': '计算机', 'Java程序设计': '计算机', '算法导论': '计算机',
    '大学英语': '外语',
    '大学物理': '理工',
    '马克思主义原理': '人文', '毛泽东思想概论': '人文',
    '微观经济学': '经管', '宏观经济学': '经管',
}

# 预置课程数据（30+ 门浙大常见课程）
SEED_COURSES = [
    {'code': 'MATH1001', 'name': '高等数学', 'college': '数学科学学院', 'credits': 5.0,
     'books': [{'title': '高等数学（第七版）上册', 'author': '同济大学数学系', 'isbn': '9787040396633', 'required': True},
               {'title': '高等数学（第七版）下册', 'author': '同济大学数学系', 'isbn': '9787040396644', 'required': True}]},
    {'code': 'MATH1002', 'name': '线性代数', 'college': '数学科学学院', 'credits': 3.0,
     'books': [{'title': '线性代数（第七版）', 'author': '同济大学数学系', 'isbn': '9787040524424', 'required': True}]},
    {'code': 'MATH2001', 'name': '概率论与数理统计', 'college': '数学科学学院', 'credits': 3.0,
     'books': [{'title': '概率论与数理统计（第四版）', 'author': '盛骤', 'isbn': '9787040537964', 'required': True}]},
    {'code': 'CS2001', 'name': '数据结构', 'college': '计算机科学与技术学院', 'credits': 4.0,
     'books': [{'title': '数据结构（C语言版）', 'author': '严蔚敏', 'isbn': '9787302147510', 'required': True}]},
    {'code': 'CS2002', 'name': '计算机组成原理', 'college': '计算机科学与技术学院', 'credits': 4.0,
     'books': [{'title': '计算机组成与设计', 'author': 'David Patterson', 'isbn': '9787112349765', 'required': True}]},
    {'code': 'CS3001', 'name': '操作系统', 'college': '计算机科学与技术学院', 'credits': 4.0,
     'books': [{'title': '现代操作系统', 'author': 'Andrew S. Tanenbaum', 'isbn': '9787111550667', 'required': True}]},
    {'code': 'CS3002', 'name': '计算机网络', 'college': '计算机科学与技术学院', 'credits': 4.0,
     'books': [{'title': '计算机网络（自顶向下方法）', 'author': 'James F. Kurose', 'isbn': '9787111626522', 'required': True}]},
    {'code': 'CS3003', 'name': '数据库系统', 'college': '计算机科学与技术学院', 'credits': 3.5,
     'books': [{'title': '数据库系统概念', 'author': 'Abraham Silberschatz', 'isbn': '9787111585741', 'required': True}]},
    {'code': 'CS1001', 'name': 'Python程序设计', 'college': '计算机科学与技术学院', 'credits': 3.0,
     'books': [{'title': 'Python编程从入门到实践', 'author': 'Eric Matthes', 'isbn': '9787115546081', 'required': True}]},
    {'code': 'CS1002', 'name': 'C++程序设计', 'college': '计算机科学与技术学院', 'credits': 3.0,
     'books': [{'title': 'C++ Primer Plus', 'author': 'Stanley B. Lippman', 'isbn': '9787121133790', 'required': True}]},
    {'code': 'CS1003', 'name': 'Java程序设计', 'college': '计算机科学与技术学院', 'credits': 3.0,
     'books': [{'title': 'Java核心技术卷I', 'author': 'Cay S. Horstmann', 'isbn': '9787111619371', 'required': True}]},
    {'code': 'CS4001', 'name': '算法导论', 'college': '计算机科学与技术学院', 'credits': 4.0,
     'books': [{'title': '算法导论（第三版）', 'author': 'Thomas H. Cormen', 'isbn': '9787111407010', 'required': True}]},
    {'code': 'ENG1001', 'name': '大学英语', 'college': '外国语言文化与国际交流学院', 'credits': 4.0,
     'books': [{'title': '新编大学英语综合教程', 'author': '浙江大学', 'isbn': '9787300208765', 'required': True}]},
    {'code': 'PHY1001', 'name': '大学物理', 'college': '物理学院', 'credits': 4.0,
     'books': [{'title': '大学物理学（第4版）', 'author': '张三慧', 'isbn': '9787302347781', 'required': True}]},
    {'code': 'POL1001', 'name': '马克思主义原理', 'college': '马克思主义学院', 'credits': 3.0,
     'books': [{'title': '马克思主义基本原理', 'author': '本书编写组', 'isbn': '9787040515675', 'required': True}]},
    {'code': 'POL2001', 'name': '毛泽东思想概论', 'college': '马克思主义学院', 'credits': 3.0,
     'books': [{'title': '毛泽东思想和中国特色社会主义理论体系概论', 'author': '本书编写组', 'isbn': '9787040529573', 'required': True}]},
    {'code': 'ECON1001', 'name': '微观经济学', 'college': '经济学院', 'credits': 3.0,
     'books': [{'title': '微观经济学（第九版）', 'author': 'N. Gregory Mankiw', 'isbn': '9787300288200', 'required': True}]},
    {'code': 'ECON2001', 'name': '宏观经济学', 'college': '经济学院', 'credits': 3.0,
     'books': [{'title': '宏观经济学（第九版）', 'author': 'N. Gregory Mankiw', 'isbn': '9787300288217', 'required': True}]},
    {'code': 'EE2001', 'name': '模拟电子技术', 'college': '信电学院', 'credits': 3.5,
     'books': [{'title': '模拟电子技术基础（第五版）', 'author': '童诗白', 'isbn': '9787040425055', 'required': True}]},
    {'code': 'EE2002', 'name': '数字电子技术', 'college': '信电学院', 'credits': 3.5,
     'books': [{'title': '数字电子技术基础（第六版）', 'author': '阎石', 'isbn': '9787040442893', 'required': True}]},
    {'code': 'CS2003', 'name': '离散数学', 'college': '计算机科学与技术学院', 'credits': 3.0,
     'books': [{'title': '离散数学及其应用', 'author': 'Kenneth H. Rosen', 'isbn': '9787111584936', 'required': True}]},
    {'code': 'MATH2003', 'name': '复变函数', 'college': '数学科学学院', 'credits': 2.5,
     'books': [{'title': '复变函数（第五版）', 'author': '西安交通大学', 'isbn': '9787040522178', 'required': True}]},
    {'code': 'ENG2001', 'name': '学术英语', 'college': '外国语言文化与国际交流学院', 'credits': 2.0,
     'books': [{'title': '学术英语（理工）', 'author': '浙江大学', 'isbn': '9787300221453', 'required': True}]},
    {'code': 'CS3004', 'name': '软件工程', 'college': '计算机科学与技术学院', 'credits': 3.0,
     'books': [{'title': '软件工程：实践者的研究方法', 'author': 'Roger S. Pressman', 'isbn': '9787111626585', 'required': True}]},
    {'code': 'CS3005', 'name': '人工智能', 'college': '计算机科学与技术学院', 'credits': 3.0,
     'books': [{'title': '人工智能：一种现代方法', 'author': 'Stuart Russell', 'isbn': '9787302597611', 'required': True}]},
    {'code': 'CS3006', 'name': '编译原理', 'college': '计算机科学与技术学院', 'credits': 3.0,
     'books': [{'title': '编译原理（龙书）', 'author': 'Alfred V. Aho', 'isbn': '9787111185972', 'required': True}]},
    {'code': 'PHY2001', 'name': '电磁场与波', 'college': '物理学院', 'credits': 3.0,
     'books': [{'title': '电磁场与电磁波', 'author': '谢处方', 'isbn': '9787040126772', 'required': True}]},
    {'code': 'MATH3001', 'name': '数学分析', 'college': '数学科学学院', 'credits': 5.0,
     'books': [{'title': '数学分析（第五版）', 'author': '华东师范大学数学系', 'isbn': '9787040553721', 'required': True}]},
    {'code': 'STAT2001', 'name': '统计学', 'college': '数学科学学院', 'credits': 3.0,
     'books': [{'title': '统计学（第七版）', 'author': '贾俊平', 'isbn': '9787300279277', 'required': True}]},
    {'code': 'LAW1001', 'name': '思想道德与法治', 'college': '马克思主义学院', 'credits': 2.0,
     'books': [{'title': '思想道德与法治', 'author': '本书编写组', 'isbn': '9787040566621', 'required': True}]},
    {'code': 'HIST1001', 'name': '中国近现代史纲要', 'college': '马克思主义学院', 'credits': 2.0,
     'books': [{'title': '中国近现代史纲要', 'author': '本书编写组', 'isbn': '9787040566651', 'required': True}]},
]


def generate_course_sql():
    """生成课程预置数据（用于 seed_courses.py 或直接导入）"""
    return SEED_COURSES


if __name__ == '__main__':
    print('>>> 开始生成 10 万条虚拟书籍数据...')
    books_data = generate_books(100000)

    # 写入 client/public/mock/
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'client', 'public', 'mock')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'books_100k.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(books_data, f, ensure_ascii=False)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f'[OK] 已生成 100000 条书籍数据 -> {output_path}')
    print(f'[INFO] 文件大小: {file_size:.1f} MB')

    # 输出统计
    categories_count = {}
    for b in books_data:
        cat = b['category']
        categories_count[cat] = categories_count.get(cat, 0) + 1
    print('\n>> 分类统计:')
    for cat, count in sorted(categories_count.items()):
        print(f'   {cat}: {count} 本')

    condition_count = {}
    for b in books_data:
        cond = b['condition']
        condition_count[cond] = condition_count.get(cond, 0) + 1
    print('\n>> 书况统计:')
    for cond, count in sorted(condition_count.items()):
        print(f'   {cond}: {count} 本')
