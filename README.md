# 求书 · 書緣 — 浙江大学校内二手书交易平台

> **Course**: 大数据信息系统分析与设计（黄鹂强老师）  
> **Student**: 单人开发  
> **Tech**: Vue 3 + Element Plus / Flask + SQLAlchemy / DeepSeek AI  

---

## 🎯 项目简介

「求书 · 書緣」是一个面向浙江大学在校学生的校内二手书交易平台。平台以"知识传承"为核心理念，提供完整的二手书买卖流程，并集成了浙大通行证 (CAS) 单点登录、AI 智能对话助手、课程-教材自动匹配、以书换书等特色功能。

### 核心功能

| 优先级 | 功能 | 说明 |
|:---:|---|---|
| P0 | 用户注册/登录 | 手机号+密码 + 浙大通行证 CAS SSO 双模式 |
| P0 | 书籍浏览/搜索 | 首页推荐 + 关键词搜索 + 分类筛选 + 分页 |
| P0 | 书籍详情 | 完整信息 + 卖家信息 + 图片画廊 + AI 评价摘要 |
| P0 | 发布书籍 | 表单 + ISBN 查询 + 图片上传 + AI 定价建议 |
| P0 | 下单交易 | 买家发起 → 卖家确认 → 完成 → 评价 |
| P0 | JWT 权限控制 | 路由守卫 + API 中间件 |
| P1 | 课程论坛 | 按课程分区、发帖/回帖、书↔帖关联 |
| P1 | 求书许愿墙 | 发布求购帖、自动匹配通知 |
| P1 | AI 对话助手 | 平台内嵌"求书小助手" Chat Widget |
| P1 | AI 个性化推荐 | DeepSeek 驱动的首页推荐 |
| P1 | 个人中心 | 信息编辑、我的发布、订单、收藏 |
| P1 | 课程-教材匹配 | 用户关联课程 → 自动匹配在售二手书 |
| P2 | 书籍旅程时间线 | 每本书的流转历史 |
| P2 | 知识传承树 | 用户买卖关系可视化 |
| P2 | 以书换书 | 零现金交易模式 |
| P2 | AI 评价摘要 | 评论 >10 条时 AI 自动生成摘要 |

---

## 🚀 快速启动

### 环境要求

- **Python** 3.10+
- **Node.js** 18+
- **Git** (用于版本控制)

### 1. 克隆项目

```bash
git clone <gitee-repo-url>
cd 001_page
```

### 2. 后端启动

```bash
cd server

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DEEPSEEK_API_KEY 和 JWT_SECRET_KEY

# 生成虚拟数据（可选，首次运行）
python seed_data.py

# 启动 Flask 服务
python app.py
```

后端运行在 `http://localhost:5000`

### 3. 前端启动

```bash
cd client

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 `http://localhost:5173`

### 4. 生成书籍封面（可选）

```bash
cd server
pip install Pillow
python generate_book_covers.py
```

---

## 🔐 测试账号

### CAS 认证测试

| 项目 | 值 |
|---|---|
| 学号 | `3240104192` |
| 密码 | `zju20240157` |
| 姓名 | 傅昱坚 |
| 学院 | 竺可桢学院 |

### 手机号注册

支持任意手机号 + 密码注册（密码需满足强度要求：8位+大小写+数字+特殊字符）。

---

## 📁 项目结构

```
project-root/
├── client/                    # 前端 Vue 3 项目
│   ├── src/
│   │   ├── components/        # 业务组件 (16+ 个)
│   │   │   ├── NavBar.vue         # 导航栏
│   │   │   ├── BookCard.vue       # 书籍卡片
│   │   │   ├── BookGrid.vue       # 书籍网格布局
│   │   │   ├── BookJourney.vue    # 书籍旅程时间线
│   │   │   ├── CyberBackground.vue # 暗色模式大气背景
│   │   │   ├── AIChat.vue         # AI 对话助手组件
│   │   │   ├── RecommendSection.vue # AI 推荐区域
│   │   │   ├── SearchBar.vue      # 搜索栏
│   │   │   ├── FilterPanel.vue    # 筛选面板
│   │   │   ├── HeroSection.vue    # 首页 Hero
│   │   │   ├── ThemeToggle.vue    # 主题切换按钮
│   │   │   ├── CasLoginForm.vue   # CAS 登录表单
│   │   │   ├── LoginForm.vue      # 手机号登录表单
│   │   │   ├── RegisterForm.vue   # 注册表单
│   │   │   ├── EmptyState.vue     # 空状态组件
│   │   │   ├── PostCard.vue       # 帖子卡片
│   │   │   ├── WishCard.vue       # 许愿卡片
│   │   │   └── ... (论坛/个人中心相关组件)
│   │   ├── views/             # 页面级组件 (12 个)
│   │   │   ├── HomeView.vue       # 首页
│   │   │   ├── AuthView.vue       # 登录/注册
│   │   │   ├── BrowseView.vue     # 浏览/搜索
│   │   │   ├── BookDetailView.vue # 书籍详情
│   │   │   ├── PublishView.vue    # 发布书籍
│   │   │   ├── OrdersView.vue     # 订单管理
│   │   │   ├── ProfileView.vue    # 个人中心
│   │   │   ├── ForumView.vue      # 课程论坛
│   │   │   ├── PostDetailView.vue # 帖子详情
│   │   │   ├── WishesView.vue     # 求书许愿墙
│   │   │   ├── ExchangeView.vue   # 以书换书
│   │   │   └── TreeView.vue       # 知识传承树
│   │   ├── router/            # Vue Router 配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/               # Axios HTTP 封装
│   │   ├── composables/       # 组合式函数
│   │   │   ├── useTheme.js        # 主题管理
│   │   │   ├── useVirtualData.js  # 10w 虚拟数据管理
│   │   │   └── useChat.js         # AI 对话状态
│   │   ├── assets/            # 第三方 CSS
│   │   └── App.vue            # 根组件
│   ├── public/
│   │   └── mock/              # 10w 虚拟数据 JSON + 封面图片
│   └── package.json
├── server/                    # 后端 Flask 项目
│   ├── app.py                 # Flask 入口
│   ├── models.py              # 15 张表 SQLAlchemy 模型
│   ├── extensions.py          # db/limiter 扩展
│   ├── routes/                # API 蓝图 (10 个)
│   │   ├── auth.py            # 认证 (注册/登录/CAS/JWT)
│   │   ├── books.py           # 书籍 CRUD + 搜索
│   │   ├── orders.py          # 订单管理
│   │   ├── favorites.py       # 收藏管理
│   │   ├── forum.py           # 课程论坛
│   │   ├── wishes.py          # 求书许愿墙
│   │   ├── courses.py         # 课程匹配
│   │   ├── user.py            # 用户信息
│   │   ├── ai.py              # AI (对话/定价/推荐/摘要/教材)
│   │   ├── exchange.py        # 以书换书
│   │   └── tree.py            # 知识传承树
│   ├── services/              # 业务逻辑层
│   │   ├── auth.py            # JWT 签发/验证/黑名单
│   │   ├── validators.py      # 密码/邮箱/手机验证
│   │   ├── zju_cas.py         # CAS SSO 客户端 (v2.1)
│   │   ├── ai_client.py       # DeepSeek API 封装
│   │   ├── ai_chat.py         # AI 对话 System Prompt
│   │   ├── ai_recommend.py    # AI 个性化推荐
│   │   ├── ai_textbook.py     # AI 教材推荐引擎
│   │   ├── course_matcher.py  # 课程-教材匹配
│   │   ├── wish_matcher.py    # 求购自动匹配
│   │   └── isbn_lookup.py     # ISBN 查询
│   ├── seed_data.py           # 10w 虚拟数据生成
│   ├── seed_courses.py        # 课程数据预置
│   ├── generate_book_covers.py # 书籍封面生成
│   └── requirements.txt
├── prototype/                 # 原型设计（前期产出）
├── docs/                      # 文档与设计规范
├── CLAUDE.md                  # 项目规范 (AI 助手用)
├── tasks.md                   # 任务清单
├── README.md                  # 本文件
└── url.txt                    # 部署 URL（如已上线）
```

---

## 🎨 双主题设计

平台支持两套视觉主题，通过右上角按钮一键切换：

| 属性 | 🌞 书韵模式 (默认) | 🌙 赛博模式 (暗色) |
|------|-------------------|-------------------|
| 底色 | 暖米纸 `#F5F0E8` | 深紫黑 `#09051A` |
| 主强调色 | 朱砂 `#C41E3A` | 霓虹蓝 `#00D4FF` |
| 卡片 | 纯白 `#FFFFFF` | 半透玻璃 `rgba(255,255,255,0.03)` |
| 质感 | 纸纹、印章、墨色 | 毛玻璃、发光边框、粒子背景 |
| 标题字体 | 衬线 Serif | 无衬线等宽 |

暗色模式包含四层大气背景：
1. 氛围背景图（screen 混合模式 + 微模糊）
2. 渐变遮罩（仅边缘，中部透明保证文字清晰）
3. Canvas 粒子画布（50 粒子 + 近距离发光连线）
4. CRT 扫描线质感

---

## 🔧 技术栈

| Layer | Technology |
|-------|-----------|
| 前端框架 | Vue 3 + Composition API (`<script setup>`) |
| UI 组件库 | Element Plus (主题覆盖) |
| HTTP 客户端 | Axios |
| 路由 | Vue Router 4.x |
| 状态管理 | Pinia |
| 后端框架 | Flask 3.x |
| ORM | Flask-SQLAlchemy 3.x |
| 认证 | JWT (PyJWT) + ZJU CAS SSO |
| 数据库 | SQLite (dev) → MySQL (final) |
| AI 引擎 | DeepSeek API |
| 版本控制 | Git (Gitee 码云) |

---

## 📊 数据库设计

共 15 张数据表：

**核心**: `user`, `book`, `book_image`, `order`, `favorite`, `review`  
**课程**: `course`, `course_book`, `user_course`  
**论坛**: `post`, `reply`  
**特色**: `wanted_book`, `book_journey`, `ai_log`, `token_blacklist` (内存)

---

## 🔒 安全特性

- 密码强度验证（8位+大小写+数字+特殊字符），前后端双重
- 邮箱格式验证 + 临时邮箱域名黑名单
- JWT 过期：24h（普通）/ 7天（记住我）
- 登出时 JWT 加入黑名单销毁
- 统一错误码体系（`ERROR_CODES` 字典）
- 图片上传 Magic Bytes 验证（防伪造文件类型）
- API 限流（Flask-Limiter，200次/天 + 60次/小时）
- CAS 认证密码不落盘，仅在后端使用 SSO Cookie

---

## 🧪 CAS 认证技术细节

基于 Celechron 项目的逆向实现：

1. GET `/cas/login` → 提取 execution token
2. GET `/cas/v2/getPubKey` → 获取 RSA 公钥 (512-bit)
3. RSA 加密密码（纯模幂，无 padding）
4. POST `/cas/login` → 获取 `iPlanetDirectoryPro` SSO Cookie
5. SSO Cookie → ZDBK 课表 API → 学籍信息 + 课程表 (50门)
6. SSO Cookie → `courses.zju.edu.cn` → 课程数据
7. Flask 签发 JWT（含学号、课程信息）→ 前端存储

数据源优先级:
- **主源**: ZDBK 课表 API（学籍 + 课程表，50门课）
- **降级**: courses.zju.edu.cn（课程待办 + profile）

---

## 🤖 AI 功能矩阵

| 功能 | 端点 | 说明 |
|------|------|------|
| AI 对话 | `POST /api/ai/chat` | 平台内嵌"求书小助手" |
| AI 定价 | `POST /api/ai/price` | 基于书况 + 历史交易建议售价 |
| AI 推荐 | `GET /api/ai/recommend` | 基于用户课程 + 收藏的个性化推荐 |
| AI 摘要 | `GET /api/ai/summarize/:id` | 评论 >10 条时自动生成评价摘要 |
| AI 教材 | `POST /api/ai/textbooks` | 23门预置教材库 + DeepSeek 补充 |

---

## 🎬 演示流程 (15-20 分钟)

1. 主页浏览 → 感受首页推荐和双主题切换
2. 注册/登录 → **演示密码错误**（评分点）
3. CAS 登录 → 浙大通行证认证（自动导入课程+教材推荐）
4. 发布书籍 → ISBN 查询 + AI 定价 + 以书换书选项
5. 浏览搜索 → 分类筛选 + 搜索（API + 10w 虚拟数据）
6. 书籍详情 → 图片画廊 + AI 评价摘要 + 书籍旅程
7. 下单交易 → 买家下单 → 订单管理
8. AI 对话 → 求书小助手回答问题
9. 论坛浏览 → 课程分区 + 发帖/回帖
10. 以书换书 → 开启交换 + 智能匹配
11. 知识传承树 → 买卖关系图谱

---

## 📝 开发心得

- CAS 认证是最复杂的部分 — ZJU 的 CAS 系统有多个数据源，需要通过多个 API 组合才能获得完整的学籍和课程信息
- AI 不只是噱头 — 定价建议、教材推荐、评价摘要都切实解决了二手书交易中的实际问题
- 10w 虚拟数据的 Promise 分片加载是课件硬性要求，使用 `requestIdleCallback` 分片解析，`setTimeout` 推迟搜索到宏任务避免 UI 冻结
- Vue 3 Composition API 的响应式系统让双主题切换非常简单 — CSS 变量 + `<script setup>` 是绝佳组合
- 双主题设计不仅仅是换颜色 — 暗色模式有专门的粒子背景、毛玻璃效果、发光边框，提供了完全不同的视觉体验

---

## 📄 License

本项目仅用于课程作业展示，不用于商业用途。

---

> **最后更新**: 2026-06-14  
> **课程截止**: 2026-06-15 23:59
