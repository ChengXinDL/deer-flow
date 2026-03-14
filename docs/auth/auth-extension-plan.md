# 认证系统扩展开发计划

## 开发日期
2026-03-14

## 开发目标

基于已完成的认证系统，扩展以下功能：
1. 密码找回功能完善
2. 第三方登录（微信、GitHub、Google）
3. 用户设置页面

## 技术方案

### 可复用资源

从 `G:\AI_works\05_archi_skills` 项目复用：

| 模块 | 文件 | 复用程度 |
|------|------|----------|
| OAuth 路由 | `app/api/v1/endpoints/oauth.py` | 高 - 直接复用 |
| OAuth 工具 | `app/core/oauth.py` | 高 - 直接复用 |
| OAuth 模型 | `app/models/oauth_account.py` | 高 - 直接复用 |
| 微信登录状态 | `app/models/wechat_login_state.py` | 高 - 直接复用 |
| OAuth 模式 | `app/schemas/oauth.py` | 高 - 直接复用 |

### 当前项目设置页面

- **位置**: `frontend/src/components/workspace/settings/`
- **组件**: SettingsDialog (Dialog 形式)
- **已有页面**: 外观设置、通知设置、关于

---

## 开发任务计划

### 阶段一：密码找回功能 ✅ 已完成

#### 1.1 后端开发 ✅

| 任务 | 文件 | 状态 |
|------|------|------|
| 创建邮件服务 | `backend/src/gateway/routers/email_service.py` | ✅ 已完成 |
| 完善密码重置接口 | `backend/src/gateway/routers/auth.py` | ✅ 已完成 |

**后端任务清单**:
- [x] 创建邮件服务模块 (SMTP 配置)
- [x] 实现邮件发送功能
- [x] 创建密码重置邮件模板（内嵌 HTML）
- [x] 完善 `/forgot-password` 接口
- [x] 完善 `/reset-password` 接口
- [x] 添加邮件配置到环境变量

#### 1.2 前端开发 ✅

| 任务 | 文件 | 状态 |
|------|------|------|
| 忘记密码页面 | `frontend/src/app/auth/forgot-password/page.tsx` | ✅ 已完成 |
| 重置密码页面 | `frontend/src/app/auth/reset-password/page.tsx` | ✅ 已完成 |

**前端任务清单**:
- [x] 创建忘记密码页面
- [x] 创建重置密码页面
- [x] 添加 API 调用函数
- [x] 添加成功/错误提示

---

### 阶段二：第三方登录功能 ✅ 已完成

#### 2.1 后端开发 ✅

| 任务 | 文件 | 状态 |
|------|------|------|
| OAuth 路由 | `backend/src/gateway/routers/oauth.py` | ✅ 已完成 |
| OAuth 工具函数 | `backend/src/gateway/routers/oauth_utils.py` | ✅ 已完成 |
| OAuth 账号模型 | `backend/src/gateway/routers/auth_models.py` | ✅ 已完成 |
| 微信登录状态模型 | `backend/src/gateway/routers/auth_models.py` | ✅ 已完成 |
| OAuth 数据模式 | `backend/src/gateway/routers/auth_schemas.py` | ✅ 已完成 |

**后端任务清单**:
- [x] 添加 OAuth 相关字段到 User 模型
- [x] 创建 OAuthAccount 模型
- [x] 创建 WechatLoginState 模型
- [x] 创建 OAuth 工具函数
- [x] 创建 OAuth 路由 (GitHub/Google/微信)
- [x] 注册 OAuth 路由到 app.py
- [x] 添加 OAuth 配置到环境变量

**环境变量配置**:
```env
# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8001/api/oauth/github/callback

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8001/api/oauth/google/callback

# 微信 OAuth
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
WECHAT_REDIRECT_URI=http://localhost:8001/api/oauth/wechat/callback

# 邮件服务
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_email_password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=MagicFlow

# 前端 URL
FRONTEND_URL=http://localhost:3000
```

#### 2.2 前端开发 ✅

| 任务 | 文件 | 状态 |
|------|------|------|
| OAuth 回调页面 | `frontend/src/app/auth/callback/page.tsx` | ✅ 已完成 |
| OAuth 按钮组件 | `frontend/src/components/auth/oauth-buttons.tsx` | ✅ 已完成 |

**前端任务清单**:
- [x] 创建 OAuth 回调处理页面
- [x] 创建第三方登录按钮组件
- [x] 在登录/注册页面添加第三方登录入口
- [x] 处理 OAuth 登录成功后的跳转

---

### 阶段三：用户设置页面 ✅ 已完成

#### 3.1 后端开发 ✅

| 任务 | 文件 | 状态 |
|------|------|------|
| 用户信息更新接口 | `backend/src/gateway/routers/auth.py` | ✅ 已完成 |
| 密码修改接口 | `backend/src/gateway/routers/auth.py` | ✅ 已有 |

**后端任务清单**:
- [x] 添加用户信息更新接口 (PUT /api/auth/me)
- [x] 完善密码修改接口

#### 3.2 前端开发 ✅

| 任务 | 文件 | 状态 |
|------|------|------|
| 用户设置页面 | `frontend/src/components/workspace/settings/profile-settings-page.tsx` | ✅ 已完成 |
| 安全设置页面 | `frontend/src/components/workspace/settings/security-settings-page.tsx` | ✅ 已完成 |

**前端任务清单**:
- [x] 创建个人信息设置页面
- [x] 创建安全设置页面（密码修改）
- [x] 更新 SettingsDialog 添加新页面
- [x] 添加表单验证

---

## 文件结构

### 后端新增文件

```
backend/
├── src/gateway/
│   └── routers/
│       ├── oauth.py              # OAuth 路由 ✅
│       ├── oauth_utils.py        # OAuth 工具函数 ✅
│       └── email_service.py      # 邮件服务 ✅
└── .env                          # OAuth 和邮件配置 ✅
```

### 前端新增文件

```
frontend/
├── src/
│   ├── app/auth/
│   │   ├── forgot-password/
│   │   │   └── page.tsx          # 忘记密码页面 ✅
│   │   ├── reset-password/
│   │   │   └── page.tsx          # 重置密码页面 ✅
│   │   └── callback/
│   │       └── page.tsx          # OAuth 回调页面 ✅
│   └── components/
│       ├── auth/
│       │   └── oauth-buttons.tsx # OAuth 按钮组件 ✅
│       └── workspace/settings/
│           ├── profile-settings-page.tsx      # 个人信息设置 ✅
│           └── security-settings-page.tsx     # 安全设置 ✅
```

---

## 完成状态

| 阶段 | 状态 | 完成时间 |
|------|------|----------|
| 第三方登录 | ✅ 已完成 | 2026-03-14 |
| 用户设置页面 | ✅ 已完成 | 2026-03-14 |
| 密码找回 | ✅ 已完成 | 2026-03-14 |

---

## 待配置项

在使用第三方登录和邮件服务前，需要在 `.env` 文件中配置：

### GitHub OAuth
1. 访问 https://github.com/settings/developers
2. 创建新的 OAuth App
3. 获取 Client ID 和 Client Secret

### Google OAuth
1. 访问 https://console.cloud.google.com/apis/credentials
2. 创建 OAuth 2.0 客户端 ID
3. 配置授权重定向 URI

### 微信 OAuth（可选）
1. 需要企业认证
2. 访问 https://open.weixin.qq.com/
3. 创建网站应用

### SMTP 邮件服务
1. 配置 SMTP 服务器地址和端口
2. 配置发件邮箱和密码

---

**文档创建日期**: 2026-03-14  
**文档版本**: v2.0  
**最后更新**: 2026-03-14
