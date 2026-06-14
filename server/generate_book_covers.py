"""生成 20 张真实质感的书籍封面图片

Usage: python generate_book_covers.py
输出: client/public/mock/images/book_1.jpg ~ book_20.jpg
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'client', 'public', 'mock', 'images')

# 20 本书的信息（真实图书数据，用于封面生成）
BOOKS = [
    # === 数学 ===
    {'title': '高等数学', 'subtitle': '第七版·上册', 'author': '同济大学数学系', 'publisher': '高等教育出版社', 'color': '#1A5276'},
    {'title': '线性代数', 'subtitle': '第七版', 'author': '同济大学数学系', 'publisher': '高等教育出版社', 'color': '#2471A3'},
    {'title': '概率论与数理统计', 'subtitle': '第五版', 'author': '盛骤 等', 'publisher': '高等教育出版社', 'color': '#2E86C1'},
    # === 计算机 ===
    {'title': '数据结构', 'subtitle': 'C语言版', 'author': '严蔚敏 吴伟民', 'publisher': '清华大学出版社', 'color': '#1E8449'},
    {'title': '计算机组成原理', 'subtitle': '第3版', 'author': '唐朔飞', 'publisher': '高等教育出版社', 'color': '#27AE60'},
    {'title': '操作系统概论', 'subtitle': '第10版', 'author': 'Abraham Silberschatz', 'publisher': '机械工业出版社', 'color': '#229954'},
    {'title': '计算机网络', 'subtitle': '第8版', 'author': 'James F. Kurose', 'publisher': '机械工业出版社', 'color': '#1D8348'},
    {'title': '数据库系统概论', 'subtitle': '第5版', 'author': '王珊 萨师煊', 'publisher': '高等教育出版社', 'color': '#196F3D'},
    {'title': 'Python编程', 'subtitle': '从入门到实践·第3版', 'author': 'Eric Matthes', 'publisher': '人民邮电出版社', 'color': '#0E6655'},
    {'title': 'C++ Primer', 'subtitle': '第5版·中文版', 'author': 'Stanley B. Lippman', 'publisher': '电子工业出版社', 'color': '#148F77'},
    # === 经管 ===
    {'title': '微观经济学', 'subtitle': '第九版', 'author': '曼昆', 'publisher': '北京大学出版社', 'color': '#7D3C98'},
    {'title': '宏观经济学', 'subtitle': '第十版', 'author': '曼昆', 'publisher': '北京大学出版社', 'color': '#8E44AD'},
    {'title': '管理学', 'subtitle': '第15版', 'author': 'Stephen P. Robbins', 'publisher': '中国人民大学出版社', 'color': '#6C3483'},
    # === 理化 ===
    {'title': '大学物理', 'subtitle': '第七版·上册', 'author': '张三慧', 'publisher': '清华大学出版社', 'color': '#D35400'},
    {'title': '有机化学', 'subtitle': '第六版', 'author': '邢其毅 裴伟伟', 'publisher': '北京大学出版社', 'color': '#E67E22'},
    # === 人文社科 ===
    {'title': '马克思主义基本原理', 'subtitle': '2023年版', 'author': '本书编写组', 'publisher': '高等教育出版社', 'color': '#922B21'},
    {'title': '中国近现代史纲要', 'subtitle': '2023年版', 'author': '本书编写组', 'publisher': '高等教育出版社', 'color': '#C0392B'},
    {'title': '大学英语', 'subtitle': '综合教程·4', 'author': '浙江大学外语学院', 'publisher': '浙江大学出版社', 'color': '#2C3E50'},
    {'title': '英语口语教程', 'subtitle': '第2版', 'author': 'Dominic Graham', 'publisher': '浙江大学出版社', 'color': '#34495E'},
    {'title': '社会学概论', 'subtitle': '新修·第五版', 'author': '郑杭生', 'publisher': '中国人民大学出版社', 'color': '#5B2C6F'},
]


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_font(size, bold=False):
    """尝试加载中文字体，降级到默认"""
    font_paths = [
        # Windows
        'C:\\Windows\\Fonts\\msyh.ttc',        # 微软雅黑
        'C:\\Windows\\Fonts\\msyhbd.ttc',       # 微软雅黑粗体
        'C:\\Windows\\Fonts\\simhei.ttf',        # 黑体
        'C:\\Windows\\Fonts\\simsun.ttc',        # 宋体
        'C:\\Windows\\Fonts\\simkai.ttf',        # 楷体
        'C:\\Windows\\Fonts\\STSONG.TTF',        # 华文宋体
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    # 降级到默认
    return ImageFont.load_default()


def generate_cover(book_info, output_path, width=400, height=560):
    """生成一张书籍封面图片"""
    color_rgb = hex_to_rgb(book_info['color'])

    # 创建图像
    img = Image.new('RGB', (width, height), color_rgb)
    draw = ImageDraw.Draw(img)

    # === 1. 顶部深色区域（书名区） ===
    top_height = height * 2 // 3
    # 渐变效果（通过多个矩形模拟）
    for i in range(top_height):
        ratio = i / top_height
        r = int(color_rgb[0] * (0.55 + 0.45 * ratio))
        g = int(color_rgb[1] * (0.55 + 0.45 * ratio))
        b = int(color_rgb[2] * (0.55 + 0.45 * ratio))
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # 装饰条纹
    accent = (
        min(255, color_rgb[0] + 60),
        min(255, color_rgb[1] + 60),
        min(255, color_rgb[2] + 60),
    )
    for i in range(8):
        y = top_height - 80 + i * 7
        alpha = 0.3 - i * 0.03
        r = int(color_rgb[0] + (accent[0] - color_rgb[0]) * alpha)
        g = int(color_rgb[1] + (accent[1] - color_rgb[1]) * alpha)
        b = int(color_rgb[2] + (accent[2] - color_rgb[2]) * alpha)
        draw.line([(20, y), (width - 20, y)], fill=(r, g, b), width=1)

    # === 2. 书名 ===
    title_font = get_font(48, bold=True)
    title = book_info['title']
    # 计算居中
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = len(title) * 48
    tx = (width - tw) // 2
    ty = top_height // 2 - 80
    # 白色文字 + 微阴影
    draw.text((tx + 2, ty + 2), title, fill=(0, 0, 0, 40), font=title_font)
    draw.text((tx, ty), title, fill=(255, 255, 250), font=title_font)

    # === 3. 副标题 ===
    subtitle_font = get_font(22)
    subtitle = book_info.get('subtitle', '')
    if subtitle:
        try:
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            sw = bbox[2] - bbox[0]
        except Exception:
            sw = len(subtitle) * 22
        sx = (width - sw) // 2
        sy = ty + 60
        draw.text((sx, sy), subtitle, fill=(255, 255, 255, 200), font=subtitle_font)

    # === 4. 底部白色区域 ===
    bottom_top = top_height
    draw.rectangle([(0, bottom_top), (width, height)], fill=(250, 250, 248))

    # === 5. 分隔线 ===
    draw.line([(30, bottom_top + 2), (width - 30, bottom_top + 2)], fill=(220, 220, 215), width=1)

    # === 6. 作者 ===
    author_font = get_font(24)
    author = book_info.get('author', '')
    if author:
        try:
            bbox = draw.textbbox((0, 0), author, font=author_font)
            aw = bbox[2] - bbox[0]
        except Exception:
            aw = len(author) * 24
        ax = (width - aw) // 2
        ay = bottom_top + 30
        draw.text((ax, ay), author, fill=(60, 60, 55), font=author_font)

    # === 7. 出版社 ===
    pub_font = get_font(20)
    publisher = book_info.get('publisher', '')
    if publisher:
        try:
            bbox = draw.textbbox((0, 0), publisher, font=pub_font)
            pw = bbox[2] - bbox[0]
        except Exception:
            pw = len(publisher) * 20
        px = (width - pw) // 2
        py = ay + 50
        draw.text((px, py), publisher, fill=(140, 140, 135), font=pub_font)

    # === 8. 底部装饰条 ===
    bar_height = 8
    draw.rectangle([(0, height - bar_height), (width, height)], fill=color_rgb)
    # 小装饰三角
    for x in range(30, width - 30, 25):
        draw.rectangle([(x, height - bar_height), (x + 12, height)], fill=accent)

    # === 9. 角落装饰 ===
    corner_size = 30
    corner_color = (255, 255, 255, 60)
    # 左下角
    draw.rectangle([(0, top_height - corner_size), (3, top_height)], fill=(255, 255, 255, 80))
    # 右下角
    draw.rectangle([(width - 3, top_height - corner_size), (width, top_height)], fill=(255, 255, 255, 80))

    # 保存
    img.save(output_path, 'JPEG', quality=85)
    print(f'  [OK] {output_path.split("/")[-1]:20s} — {book_info["title"]}')


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f'Generating {len(BOOKS)} book cover images...')
    print(f'Output: {OUTPUT_DIR}\n')

    for i, book in enumerate(BOOKS, 1):
        output_path = os.path.join(OUTPUT_DIR, f'book_{i}.jpg')
        generate_cover(book, output_path)

    # 列出生成的文件大小
    print(f'\nDone! Generated {len(BOOKS)} covers:')
    total_size = 0
    for i in range(1, len(BOOKS) + 1):
        path = os.path.join(OUTPUT_DIR, f'book_{i}.jpg')
        size = os.path.getsize(path)
        total_size += size
        print(f'  book_{i:02d}.jpg — {size//1024} KB')
    print(f'  Total: {total_size//1024} KB (~{total_size//1024//1024} MB)')


if __name__ == '__main__':
    main()
