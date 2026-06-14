# Flask JWT 认证与授权系统

基于 Flask + JWT 的后端认证系统，支持用户注册、登录、免登录刷新、登出与受保护资源访问。

## 技术栈

- Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-Bcrypt + Flask-CORS
- SQLite 数据库
- JWT (JSON Web Token) 无状态认证

## 项目结构

```
server/
├── app.py              # 应用入口，JWT 回调配置
├── config.py           # 配置（密钥、JWT 有效期、数据库）
├── extensions.py       # Flask 扩展统一初始化
├── models.py           # 数据库模型（User、RevokedToken）
├── auth.py             # 认证蓝图（注册/登录/刷新/登出/Profile）
├── requirements.txt    # Python 依赖
└── readme.md           # 本文件
```

## 启动方式

```bash
cd server

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 启动
python app.py
```

服务默认运行在 `http://localhost:5000`。

## API 端点

所有端点前缀为 `/auth`，请求和响应均为 JSON 格式。

| 方法 | 路径               | 说明                     | 是否需要 access_token |
|------|--------------------|--------------------------|-----------------------|
| POST | `/auth/register`   | 用户注册                 | 否                    |
| POST | `/auth/login`      | 用户登录                 | 否                    |
| POST | `/auth/refresh`    | 刷新 access_token        | 否（需 refresh_token）|
| POST | `/auth/logout`     | 登出（吊销 token）       | 是                    |
| GET  | `/auth/profile`    | 获取当前用户信息         | 是                    |

### POST /auth/register

请求体：

```json
{
  "email": "user@example.com",
  "password": "Abc@1234"
}
```

成功响应 (`201`)：

```json
{
  "message": "User registered successfully"
}
```

### POST /auth/login

请求体：

```json
{
  "email": "user@example.com",
  "password": "Abc@1234",
  "remember_me": true
}
```

`remember_me` 为可选字段，默认 `false`。

- `remember_me = true` → refresh_token 有效期 **30 天**
- `remember_me = false` → refresh_token 有效期 **7 天**

成功响应 (`200`)：

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### POST /auth/refresh

请求体：

```json
{
  "refresh_token": "eyJ..."
}
```

成功响应 (`200`)：

```json
{
  "access_token": "eyJ..."
}
```

### POST /auth/logout

**Header:** `Authorization: Bearer <access_token>`

请求体（可选，可同时吊销 refresh_token）：

```json
{
  "refresh_token": "eyJ..."
}
```

成功响应 (`200`)：

```json
{
  "message": "Successfully logged out"
}
```

### GET /auth/profile

**Header:** `Authorization: Bearer <access_token>`

成功响应 (`200`)：

```json
{
  "email": "user@example.com",
  "created_at": "2026-06-03T12:00:00"
}
```

## 错误码说明

| HTTP 状态码 | 说明         |
|-------------|--------------|
| 400         | 请求格式错误 |
| 401         | 认证失败     |
| 404         | 资源未找到   |
| 409         | 资源冲突     |

## 错误响应示例

所有错误均返回结构化的 JSON：

```json
// 邮箱格式不合法
{ "error": "Invalid email format" }

// 密码强度不足
{ "error": "Password must be at least 8 characters and include uppercase, lowercase, digit, and special character" }

// 邮箱已注册
{ "error": "Email already registered" }

// 邮箱未注册
{ "error": "Email not found" }

// 密码错误
{ "error": "Incorrect password" }

// 令牌缺少
{ "error": "Missing authorization header" }

// 令牌无效或过期
{ "error": "Invalid or expired access token" }

// 令牌已被吊销
{ "error": "Token has been revoked" }

// refresh_token 无效/过期/被销毁
{ "error": "Invalid or expired refresh token" }
```