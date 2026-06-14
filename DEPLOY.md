# 求书·書緣 部署指南

## Render 平台部署

### 前提条件
1. 注册 Render 账号：https://render.com
2. 连接你的 GitHub/Gitee 仓库

### 部署步骤

#### 1. 推送代码到仓库
```bash
git add .
git commit -m "feat: 添加 Render 部署配置"
git push origin master
```

#### 2. 在 Render 创建服务
1. 登录 Render 控制台
2. 点击 "New" → "Blueprint"
3. 选择你的仓库
4. Render 会自动检测 `render.yaml` 配置文件

#### 3. 配置环境变量
Render 会自动创建以下环境变量：
- `SECRET_KEY` - 自动生成的密钥
- `DATABASE_URL` - PostgreSQL 连接字符串

#### 4. 部署完成
- 前端地址：`https://qiushu-frontend.onrender.com`
- 后端地址：`https://qiushu-backend.onrender.com`

### 注意事项

#### 数据库
- Render 使用 PostgreSQL 数据库
- 首次部署后需要初始化数据库：
  ```bash
  # 在 Render Shell 中执行
  cd server
  python init_db.py
  ```

#### 跨域配置
后端已配置 CORS，允许前端域名访问。

#### 文件上传
- 上传文件存储在服务器内存中
- 重启服务后文件会丢失
- 建议使用云存储（如阿里云 OSS）替代

### 本地开发

#### 前端
```bash
cd client
npm install
npm run dev
```

#### 后端
```bash
cd server
pip install -r requirements.txt
python app.py
```

### 常见问题

#### Q: 部署后无法访问 API
A: 检查后端服务是否正常运行，查看 Render 日志。

#### Q: 数据库连接失败
A: 确认 `DATABASE_URL` 环境变量已正确设置。

#### Q: 文件上传失败
A: 检查 `UPLOAD_FOLDER` 目录权限，确保目录存在。