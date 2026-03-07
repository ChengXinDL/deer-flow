# DeerFlow 前端架构文档

## 项目概述

DeerFlow 前端是一个基于 Next.js 16 构建的现代化 AI 对话界面，用于与 LangGraph 后端进行交互。它提供了线程式的 AI 对话、流式响应、工件管理和技能系统等功能。

## 技术栈

| 类别 | 技术 |
|------|------|
| **框架** | Next.js 16 (App Router) |
| **UI 库** | React 19, Tailwind CSS 4 |
| **组件库** | Shadcn UI, MagicUI, React Bits |
| **AI 集成** | LangGraph SDK 1.5.3, Vercel AI Elements |
| **状态管理** | TanStack Query 5.90.17 |
| **代码编辑器** | CodeMirror 6 |
| **流程图** | React Flow (xyflow) |
| **构建工具** | pnpm 10.26.2+, Turbopack |

## 项目结构

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router 页面
│   │   ├── api/                # API 路由
│   │   │   └── auth/           # 认证路由
│   │   ├── workspace/          # 主工作区页面
│   │   │   └── chats/          # 聊天页面
│   │   │       ├── [thread_id]/# 特定聊天线程
│   │   │       └── page.tsx    # 聊天列表
│   │   ├── mock/               # Mock/Demo 页面
│   │   ├── layout.tsx          # 根布局
│   │   └── page.tsx            # 落地页
│   │
│   ├── components/             # React 组件
│   │   ├── ui/                 # Shadcn UI 基础组件
│   │   ├── ai-elements/        # AI 相关 UI 元素
│   │   │   ├── artifact.tsx    # 工件展示
│   │   │   ├── canvas.tsx      # 画布组件
│   │   │   ├── chain-of-thought.tsx  # 思维链
│   │   │   ├── conversation.tsx # 对话组件
│   │   │   ├── message.tsx     # 消息组件
│   │   │   ├── plan.tsx        # 计划展示
│   │   │   ├── reasoning.tsx   # 推理展示
│   │   │   └── ...
│   │   ├── landing/            # 落地页组件
│   │   │   ├── sections/       # 页面区块
│   │   │   ├── hero.tsx        # 主视觉
│   │   │   └── ...
│   │   └── workspace/          # 工作区组件
│   │       ├── artifacts/      # 工件管理
│   │       ├── messages/       # 消息列表
│   │       ├── settings/       # 设置页面
│   │       └── ...
│   │
│   ├── core/                   # 核心业务逻辑
│   │   ├── api/                # API 客户端
│   │   │   └── api-client.ts   # LangGraph SDK 封装
│   │   ├── artifacts/          # 工件管理
│   │   ├── config/             # 应用配置
│   │   ├── i18n/               # 国际化 (en-US, zh-CN)
│   │   ├── mcp/                # MCP 集成
│   │   ├── memory/             # 持久化记忆系统
│   │   ├── messages/           # 消息处理
│   │   ├── models/             # 数据模型
│   │   ├── settings/           # 用户设置
│   │   ├── skills/             # 技能系统
│   │   ├── threads/            # 线程管理
│   │   │   ├── hooks.ts        # 线程相关 Hooks
│   │   │   ├── types.ts        # 类型定义
│   │   │   └── utils.ts        # 工具函数
│   │   ├── todos/              # 待办事项系统
│   │   └── utils/              # 工具函数
│   │
│   ├── hooks/                  # 自定义 React Hooks
│   ├── lib/                    # 共享库和工具
│   ├── server/                 # 服务端代码 (better-auth)
│   └── styles/                 # 全局样式
│
├── public/                     # 静态资源
├── scripts/                    # 构建脚本
└── docs/                       # 文档

```

## 路由结构

| 路由 | 说明 |
|------|------|
| `/` | 落地页 |
| `/workspace/chats` | 聊天列表 |
| `/workspace/chats/[thread_id]` | 特定聊天线程 |
| `/api/auth/*` | 认证 API |
| `/mock/*` | Mock API (开发用) |

## 数据流

```
用户输入 → Thread Hooks → LangGraph SDK → LangGraph 后端
                                              ↓
组件订阅 ← 线程状态 ← 流事件更新 ← 主 Agent/子 Agent
```

### 核心数据流说明

1. **用户输入** → `core/threads/hooks.ts` 中的线程 Hooks
2. **LangGraph SDK 流式传输** → 接收实时响应
3. **流事件更新线程状态** → 消息、工件、待办事项
4. **TanStack Query** 管理服务端状态
5. **localStorage** 存储用户设置
6. **组件订阅线程状态** 并渲染更新

## 核心模块

### 1. 线程管理 (core/threads/)

- **`useThreadStream`** - 线程流式传输
- **`useSubmitThread`** - 提交线程消息
- **`useThreads`** - 线程列表管理
- **线程状态管理** - 消息、工件、待办事项

### 2. 工件系统 (core/artifacts/)

- 工件加载和缓存
- 支持代码、图片、文档等多种类型
- 文件系统操作

### 3. 技能系统 (core/skills/)

- 技能安装和管理
- 动态技能加载
- 技能配置

### 4. 记忆系统 (core/memory/)

- 持久化用户记忆
- 跨会话记忆保持

### 5. MCP 集成 (core/mcp/)

- Model Context Protocol 集成
- 外部工具扩展

## 环境变量

```bash
# 服务端
BETTER_AUTH_SECRET=              # 认证密钥
BETTER_AUTH_GITHUB_CLIENT_ID=    # GitHub OAuth
BETTER_AUTH_GITHUB_CLIENT_SECRET=# GitHub OAuth
GITHUB_OAUTH_TOKEN=              # GitHub Token
NODE_ENV=development|production  # 环境模式

# 客户端
NEXT_PUBLIC_BACKEND_BASE_URL=    # 后端 API URL (可选)
NEXT_PUBLIC_LANGGRAPH_BASE_URL=  # LangGraph API URL (可选)
NEXT_PUBLIC_STATIC_WEBSITE_ONLY= # 静态网站模式
```

> **注意**: 后端 API URL 是可选的，默认使用 nginx 代理

## 开发规范

### 代码风格

- **默认服务端组件**，交互组件使用 `"use client"`
- **导入排序**: 内置 → 外部 → 内部 → 父级 → 同级
- **类型导入**: 使用内联类型导入 `import { type Foo }`
- **未使用变量**: 前缀 `_`
- **类名**: 使用 `cn()` 函数处理条件 Tailwind 类
- **路径别名**: `@/*` 映射到 `src/*`

### 组件规范

- `ui/` 和 `ai-elements/` 是从 registry 生成的，不要手动编辑
- 使用 Shadcn UI、MagicUI、React Bits、Vercel AI SDK 的组件

## 常用命令

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 启动开发服务器 (Turbopack) |
| `pnpm build` | 生产构建 |
| `pnpm start` | 启动生产服务器 |
| `pnpm check` | 运行 lint + typecheck |
| `pnpm lint` | ESLint 检查 |
| `pnpm lint:fix` | 自动修复 ESLint 问题 |
| `pnpm typecheck` | TypeScript 类型检查 |

## 依赖说明

### 核心依赖

- `next`: ^16.1.4 - Next.js 框架
- `react`: ^19.0.0 - React 库
- `@langchain/langgraph-sdk`: ^1.5.3 - LangGraph SDK
- `@tanstack/react-query`: ^5.90.17 - 状态管理
- `tailwindcss`: ^4.0.15 - CSS 框架

### UI 依赖

- `@radix-ui/*`: Radix UI 基础组件
- `lucide-react`: 图标库
- `@uiw/react-codemirror`: 代码编辑器
- `@xyflow/react`: 流程图组件
- `motion`: 动画库

### AI 相关

- `ai`: ^6.0.33 - Vercel AI SDK
- `streamdown`: 1.4.0 - 流式 Markdown 渲染
- `shiki`: 3.15.0 - 代码高亮

## 与后端集成

### API 架构

```
Frontend (Next.js) ──▶ LangGraph SDK ──▶ LangGraph Backend (lead_agent)
                                              ├── Sub-Agents
                                              └── Tools & Skills
```

### 关键集成点

1. **LangGraph Client** - 单例模式，通过 `getAPIClient()` 获取
2. **流式响应** - 使用 SSE 接收实时 AI 响应
3. **线程管理** - 创建、继续、删除对话线程
4. **工件处理** - 上传、下载、预览生成的文件

## 性能优化

- **Turbopack** - 开发时快速编译
- **React Server Components** - 减少客户端 JavaScript
- **TanStack Query** - 智能缓存和后台更新
- **代码分割** - 按需加载组件

## 浏览器支持

- Chrome/Edge (最新版)
- Firefox (最新版)
- Safari (最新版)

## 相关文档

- [Next.js 文档](https://nextjs.org/docs)
- [LangGraph SDK 文档](https://www.npmjs.com/package/@langchain/langgraph-sdk)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Shadcn UI 文档](https://ui.shadcn.com/)
