"""
生成 10 万条虚拟书籍数据 JSON 文件
输出到 client/public/data/books.json
图片可重复引用以节省磁盘空间
"""
import json
import random
import os

# 确保输出目录存在
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'client', 'public', 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

subjects = ['微积分', '线性代数', '大学英语', '有机化学', '数据结构',
            '概率论', '计算机网络', '操作系统', '高等数学', '考研政治',
            '微观经济学', '宏观经济学']
conditions = ['九成新', '八成新', '全新未拆', '有笔记', '七成新']
authors = ['同济大学', '清华大学', '浙江大学', '外研社', '北京大学出版社', '机械工业出版社']
category_map = {
    '微积分': '教材', '线性代数': '教材', '大学英语': '教材', '有机化学': '教材',
    '数据结构': '选修', '概率论': '选修', '计算机网络': '选修', '操作系统': '选修',
    '高等数学': '教材', '考研政治': '考研', '微观经济学': '选修', '宏观经济学': '选修',
}

# 可重复使用的图片列表（节省磁盘空间，全部使用同一张 R-C.jpg）
img_pool = [
    'R-C.jpg',
]


TOTAL = 100000
CHUNK_SIZE = 10000  # 分块写入，避免内存占用过高

print(f'正在生成 {TOTAL} 条虚拟书籍数据...')

all_books = []
for i in range(TOTAL):
    subj = subjects[i % len(subjects)]
    book = {
        'id': i + 1,
        'title': f'{subj} 辅导书 第{i // len(subjects) + 1}版',
        'author': authors[i % len(authors)],
        'price': round(10 + random.random() * 50, 1),
        'oldPrice': round(30 + random.random() * 80, 1),
        'condition': conditions[i % len(conditions)],
        'seller': f'同学{100 + (i % 900)}',
        'img': img_pool[i % len(img_pool)],
        'category': category_map.get(subj, '教材'),
        'isUserPublished': False,
    }
    all_books.append(book)

    if (i + 1) % CHUNK_SIZE == 0:
        print(f'  已生成 {i + 1} 条...')

output_path = os.path.join(OUTPUT_DIR, 'books.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_books, f, ensure_ascii=False, indent=None)

print(f'完成！共生成 {TOTAL} 条书籍数据')
print(f'输出文件: {output_path}')
print(f'文件大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB')
