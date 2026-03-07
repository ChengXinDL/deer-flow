# DeerFlow 前端开发文档

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) | 前端架构 overview，技术栈和项目结构 |
| [FRONTEND_DEVELOPMENT_GUIDE.md](./FRONTEND_DEVELOPMENT_GUIDE.md) | 开发环境搭建和开发流程 |
| [FRONTEND_COMPONENT_CATALOG.md](./FRONTEND_COMPONENT_CATALOG.md) | 组件目录，包含所有可用组件 |
| [FRONTEND_API_INTEGRATION.md](./FRONTEND_API_INTEGRATION.md) | API 集成指南，LangGraph SDK 使用 |
| [FRONTEND_TROUBLESHOOTING.md](./FRONTEND_TROUBLESHOOTING.md) | 常见问题排查和解决方案 |

---

## 🚀 快速开始

### 环境要求

- Node.js 22+
- pnpm 10.26.2+

### 安装和启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 复制环境变量
cp .env.example .env

# 启动开发服务器
pnpm dev
```

访问 http://localhost:3000

---

## 🏗️ 技术栈

| 类别 | 技术 |
|------|------|
| **框架** | Next.js 16 + React 19 |
| **样式** | Tailwind CSS 4 |
| **组件库** | Shadcn UI + MagicUI + React Bits |
| **AI SDK** | LangGraph SDK 1.5.3 |
| **状态管理** | TanStack Query |
| **构建工具** | pnpm + Turbopack |

---

## 📁 项目结构

```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   ├── components/       # React 组件
│   │   ├── ui/          # Shadcn UI 组件
│   │   ├── ai-elements/ # AI 相关组件
│   │   ├── workspace/   # 工作区组件
│   │   └── landing/     # 落地页组件
│   ├── core/            # 核心业务逻辑
│   ├── hooks/           # 自定义 Hooks
│   ├── lib/             # 工具函数
│   └── styles/          # 全局样式
├── public/              # 静态资源
└── docs/                # 文档
```

---

## 📝 开发规范

### 代码风格

- 使用 `pnpm check` 检查代码
- 使用 `cn()` 组合 Tailwind 类
- 优先使用服务端组件
- 路径别名 `@/*` 映射到 `src/*`

### 提交前检查

```bash
pnpm check    # 运行 lint + typecheck
pnpm lint     # ESLint 检查
pnpm typecheck # TypeScript 检查
```

---

## 🔗 相关链接

- [项目 README](../frontend/README.md)
- [CLAUDE.md](../frontend/CLAUDE.md) - Claude Code 指南
- [AGENTS.md](../frontend/AGENTS.md) - Agent 架构文档
- [Next.js 文档](https://nextjs.org/docs)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Shadcn UI](https://ui.shadcn.com/)

---

## 💡 提示

- Docker 开发是推荐方式，使用 `make docker-start`
- 后端 API URL 是可选的，默认使用 nginx 代理
- 环境验证可以用 `SKIP_ENV_VALIDATION=1` 跳过
- `components/ui/` 和 `components/ai-elements/` 是自动生成的，不要手动修改
