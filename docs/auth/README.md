# 认证系统使用指南

## 概述

本认证系统提供完整的用户注册、登录、令牌管理功能，支持 JWT 认证和刷新令牌机制。

## 功能特性

- ✅ 用户注册（邮箱/密码）
- ✅ 用户登录（邮箱/密码）
- ✅ JWT 令牌认证
- ✅ 刷新令牌机制
- ✅ 用户登出
- ✅ 获取当前用户信息
- ✅ 密码重置
- ✅ 密码修改

## 快速开始

### 1. 启动服务

```bash
# 启动后端服务
cd backend
uv run uvicorn src.gateway.app:app --host 0.0.0.0 --port 8001

# 启动前端服务
cd frontend
pnpm dev
```

### 2. 访问认证页面

- **注册页面**：http://localhost:3000/auth/register
- **登录页面**：http://localhost:3000/auth/login

### 3. 运行测试

```bash
# 后端测试
cd backend
python tests/test_auth.py

# 前端测试
cd frontend
pnpm test
```

## API 文档

### 认证接口

#### 1. 用户注册

**请求**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "用户名"
}
```

**响应**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "用户名",
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-03-13T13:45:24.260749"
}
```

#### 2. 用户登录

**请求**
```http
POST /api/auth/login
Content-Type: application/json

{
  "login_type": "email",
  "identifier": "user@example.com",
  "password": "password123",
  "remember_me": true
}
```

**响应**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "VTwzJOdYgs1OcV8g5fOOduJjzLmiWsxZ",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_name": "用户名",
  "user_avatar": null
}
```

#### 3. 刷新令牌

**请求**
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "refresh-token-string"
}
```

**响应**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "new-refresh-token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### 4. 获取当前用户

**请求**
```http
GET /api/auth/me
Authorization: Bearer access-token
```

**响应**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "用户名",
  "avatar_url": null,
  "is_active": true,
  "is_verified": false,
  "created_at": "2026-03-13T13:45:24.260749",
  "last_login_at": "2026-03-13T13:45:29.376511"
}
```

#### 5. 用户登出

**请求**
```http
POST /api/auth/logout
Authorization: Bearer access-token
Content-Type: application/json

{
  "refresh_token": "refresh-token-string"
}
```

**响应**
```json
{
  "message": "登出成功"
}
```

## 前端使用

### 使用认证 Hook

```typescript
import { useAuth } from '@/core/auth/hooks';

function MyComponent() {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    error,
    login, 
    register, 
    logout 
  } = useAuth();

  // 登录
  const handleLogin = async () => {
    try {
      await login({
        login_type: 'email',
        identifier: 'user@example.com',
        password: 'password123',
        remember_me: true
      });
    } catch (err) {
      console.error('登录失败:', err);
    }
  };

  // 注册
  const handleRegister = async () => {
    try {
      await register({
        email: 'user@example.com',
        password: 'password123',
        name: '用户名'
      });
    } catch (err) {
      console.error('注册失败:', err);
    }
  };

  // 登出
  const handleLogout = async () => {
    await logout();
  };

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <p>欢迎, {user?.name}</p>
          <button onClick={handleLogout}>登出</button>
        </div>
      ) : (
        <div>
          <button onClick={handleLogin}>登录</button>
          <button onClick={handleRegister}>注册</button>
        </div>
      )}
    </div>
  );
}
```

### 使用认证 API

```typescript
import { 
  login, 
  register, 
  logout, 
  getCurrentUser,
  checkIsAuthenticated 
} from '@/core/auth/api';

// 登录
const response = await login({
  login_type: 'email',
  identifier: 'user@example.com',
  password: 'password123',
  remember_me: true
});

// 注册
const user = await register({
  email: 'user@example.com',
  password: 'password123',
  name: '用户名'
});

// 获取当前用户
const currentUser = await getCurrentUser();

// 检查认证状态
const isAuth = checkIsAuthenticated();
```

## 数据库配置

### PostgreSQL 连接信息

```
Host: 192.168.9.174
Port: 5432
Database: pg_db
User: app_user
Password: Sykj_1234P
```

### 数据表

- **users** - 用户表
- **refresh_tokens** - 刷新令牌表
- **password_reset_tokens** - 密码重置令牌表

## 安全说明

1. **密码加密**：使用 bcrypt 算法进行密码加密
2. **JWT 令牌**：使用 HS256 算法签名
3. **令牌过期**：访问令牌 1 小时过期，刷新令牌 7 天过期
4. **HTTPS**：生产环境建议使用 HTTPS

## 故障排除

### 数据库连接失败

检查 `backend/.env` 文件中的数据库配置：
```
POSTGRES_URL=postgresql://app_user:Sykj_1234P@192.168.9.174:5432/pg_db
```

### 令牌验证失败

- 检查令牌是否过期
- 检查 Authorization 头格式是否正确：`Bearer token`

### 注册失败

- 检查邮箱格式是否正确
- 检查密码长度是否至少 8 位
- 检查邮箱是否已存在

## 相关文档

- [开发总结](./development-summary.md)
- [变更日志](./CHANGELOG.md)
- [后端开发进度](./backend-development-progress.md)
- [前端开发进度](./frontend-development-progress.md)
- [数据库配置](./database-config.md)
- [复用评估](./reuse-assessment.md)
