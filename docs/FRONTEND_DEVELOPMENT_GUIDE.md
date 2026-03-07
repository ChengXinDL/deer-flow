# DeerFlow 前端开发指南

## 开发环境准备

### 前置要求

- **Node.js**: 22+
- **pnpm**: 10.26.2+
- **操作系统**: Windows 11 / macOS / Linux

### 安装依赖

```bash
cd frontend
pnpm install
```

### 环境配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件（可选）：
```bash
# 如需直接连接后端服务，取消注释以下行
# NEXT_PUBLIC_BACKEND_BASE_URL="http://localhost:8001"
# NEXT_PUBLIC_LANGGRAPH_BASE_URL="http://localhost:2024"
```

> 默认使用 nginx 代理，无需配置后端 URL

## 启动开发服务器

### 方式一：Docker 开发（推荐）

在项目根目录执行：

```bash
# 初始化（首次运行）
make docker-init

# 启动服务
make docker-start
```

访问：http://localhost:2026

### 方式二：本地开发

```bash
# 检查环境
make check

# 安装所有依赖
make install

# 启动开发服务
make dev
```

访问：http://localhost:2026

### 方式三：仅前端开发

```bash
cd frontend
pnpm dev
```

访问：http://localhost:3000

## 项目结构详解

### App Router 结构

```
src/app/
├── layout.tsx          # 根布局（主题、字体、全局样式）
├── page.tsx            # 落地页
├── api/                # API 路由
│   └── auth/           # Better Auth 认证
├── workspace/          # 工作区
│   ├── layout.tsx      # 工作区布局
│   ├── page.tsx        # 工作区首页
│   └── chats/          # 聊天模块
│       ├── page.tsx    # 聊天列表
│       └── [thread_id]/
│           ├── layout.tsx
│           └── page.tsx
└── mock/               # Mock API（开发用）
```

### 组件组织

```
src/components/
├── ui/                 # Shadcn UI 基础组件（自动生成）
├── ai-elements/        # AI 相关组件（自动生成）
├── landing/            # 落地页组件
└── workspace/          # 工作区组件
```

**注意**: `ui/` 和 `ai-elements/` 是通过 registry 生成的，不要手动修改。

## 核心开发模式

### 1. 线程管理

```typescript
import { useThreadStream, useSubmitThread } from '@/core/threads';

function ChatComponent() {
  const { messages, isStreaming } = useThreadStream(threadId);
  const { submit } = useSubmitThread();

  const handleSend = async (content: string) => {
    await submit({
      threadId,
      messages: [{ role: 'user', content }]
    });
  };

  return (
    <div>
      {messages.map(msg => <Message key={msg.id} data={msg} />)}
      {isStreaming && <StreamingIndicator />}
    </div>
  );
}
```

### 2. 使用 API Client

```typescript
import { getAPIClient } from '@/core/api';

const client = getAPIClient();

// 创建线程
const thread = await client.threads.create({
  metadata: { title: 'New Chat' }
});

// 发送消息
const stream = await client.runs.stream(
  thread.thread_id,
  'lead_agent',
  {
    input: { messages: [{ role: 'user', content: 'Hello' }] }
  }
);
```

### 3. 工件处理

```typescript
import { useArtifacts } from '@/core/artifacts';

function ArtifactViewer() {
  const { artifacts, loadArtifact } = useArtifacts(threadId);

  return (
    <div>
      {artifacts.map(artifact => (
        <ArtifactCard key={artifact.id} data={artifact} />
      ))}
    </div>
  );
}
```

### 4. 国际化

```typescript
import { useI18n } from '@/core/i18n';

function MyComponent() {
  const { t, locale, setLocale } = useI18n();

  return (
    <div>
      <h1>{t('welcome.title')}</h1>
      <button onClick={() => setLocale('zh-CN')}>
        {t('language.switch')}
      </button>
    </div>
  );
}
```

## 组件开发规范

### 服务端组件（默认）

```typescript
// 直接访问后端数据
async function ServerComponent() {
  const data = await fetchData();

  return <div>{data.title}</div>;
}
```

### 客户端组件

```typescript
'use client';

import { useState } from 'react';

function ClientComponent() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### 样式规范

使用 `cn()` 工具函数组合 Tailwind 类：

```typescript
import { cn } from '@/lib/utils';

function Button({ className, variant, ...props }) {
  return (
    <button
      className={cn(
        'px-4 py-2 rounded-md',
        variant === 'primary' && 'bg-blue-500 text-white',
        variant === 'secondary' && 'bg-gray-200 text-gray-800',
        className
      )}
      {...props}
    />
  );
}
```

## 状态管理

### 服务端状态 - TanStack Query

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';

// 查询
const { data, isLoading } = useQuery({
  queryKey: ['threads'],
  queryFn: fetchThreads
});

// 修改
const mutation = useMutation({
  mutationFn: createThread,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['threads'] });
  }
});
```

### 客户端状态 - React Hooks

```typescript
import { useState, useCallback } from 'react';

function useLocalState() {
  const [state, setState] = useState(initialValue);

  const updateState = useCallback((newValue) => {
    setState(newValue);
  }, []);

  return { state, updateState };
}
```

### 持久化状态 - localStorage

```typescript
import { useSettings } from '@/core/settings';

function SettingsComponent() {
  const { settings, updateSettings } = useSettings();

  return (
    <div>
      <input
        value={settings.theme}
        onChange={(e) => updateSettings({ theme: e.target.value })}
      />
    </div>
  );
}
```

## API 集成

### LangGraph SDK 使用

```typescript
import { getAPIClient } from '@/core/api';

const client = getAPIClient();

// 流式对话
const stream = await client.runs.stream(
  threadId,
  assistantId,
  {
    input: { messages },
    streamMode: 'messages'
  }
);

// 处理流式响应
for await (const chunk of stream) {
  if (chunk.event === 'messages/partial') {
    console.log(chunk.data);
  }
}
```

### 自定义 API 调用

```typescript
// app/api/custom/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const data = await fetchExternalData();
  return NextResponse.json(data);
}
```

## 调试技巧

### 1. 环境变量调试

```bash
# 跳过环境验证（Docker 构建时有用）
SKIP_ENV_VALIDATION=1 pnpm build
```

### 2. 日志输出

```typescript
// 开发环境日志
if (process.env.NODE_ENV === 'development') {
  console.log('Debug:', data);
}
```

### 3. React DevTools

安装 React DevTools 浏览器扩展，检查组件树和状态。

### 4. 网络调试

- 打开浏览器开发者工具
- 查看 Network 标签
- 过滤 XHR/Fetch 请求

## 常见问题

### Q: 热更新不生效？

A: Turbopack 已启用，如果仍有问题：
```bash
# 清除缓存
rm -rf .next
pnpm dev
```

### Q: 类型错误？

A: 运行类型检查：
```bash
pnpm typecheck
```

### Q: 环境变量不生效？

A: 确保变量名以 `NEXT_PUBLIC_` 开头（客户端需要），并重启开发服务器。

### Q: API 请求失败？

A: 检查：
1. 后端服务是否运行
2. nginx 配置是否正确
3. 环境变量是否设置

## 性能优化建议

1. **使用 React Server Components** 减少客户端 JS
2. **图片优化** 使用 Next.js Image 组件
3. **代码分割** 动态导入大组件
4. **缓存策略** 合理配置 TanStack Query
5. **虚拟列表** 长列表使用虚拟化

## 提交代码前检查

```bash
# 运行所有检查
pnpm check

# 或分别运行
pnpm lint
pnpm typecheck
```

## 相关资源

- [Next.js 文档](https://nextjs.org/docs)
- [React 文档](https://react.dev/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [TanStack Query 文档](https://tanstack.com/query/latest)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
