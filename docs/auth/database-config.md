# 认证数据库配置

## PostgreSQL 配置

### 环境变量

认证系统支持通过以下环境变量配置数据库连接：

```bash
# PostgreSQL 连接字符串（推荐）
POSTGRES_URL=postgresql://app_user:Sykj_1234P@192.168.9.180:5432/pg_db

# 或者使用独立的环境变量
POSTGRES_USER=app_user
POSTGRES_PASSWORD=Sykj_1234P
POSTGRES_HOST=192.168.9.174
POSTGRES_PORT=5432
POSTGRES_DB=pg_db

# 可选：指定数据表所在的 schema
SCHEMA_APP_DATA=document_data
```

### 优先级

数据库连接字符串的优先级如下：

1. `POSTGRES_URL` - 完整的 PostgreSQL 连接字符串
2. `AUTH_DATABASE_URL` - 认证数据库专用连接字符串
3. SQLite（默认）- 本地开发使用

### 当前配置

```bash
POSTGRES_URL=postgresql://app_user:Sykj_1234P@192.168.9.180:5432/pg_db
```

### 数据库表

认证系统会创建以下数据表：

- `users` - 用户表
- `refresh_tokens` - 刷新令牌表
- `password_reset_tokens` - 密码重置令牌表

### 初始化数据库

```bash
cd backend
uv run python scripts/init_auth_db.py
```

### 依赖安装

```bash
uv run pip install psycopg2-binary
```

## SQLite 配置（本地开发）

如果不配置 PostgreSQL，系统会自动使用 SQLite：

```bash
# 数据库文件位置
{MAGIC_FLOW_HOME}/.magic-flow/auth.db
```

## 注意事项

1. 生产环境必须使用 PostgreSQL
2. 确保数据库用户有创建表的权限
3. 建议为认证数据库创建独立的 schema
4. 定期备份数据库
