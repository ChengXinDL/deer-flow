# DeerFlow 前端 API 集成文档

## 概述

DeerFlow 前端通过 **LangGraph SDK** 与后端进行通信，支持流式响应、线程管理和工件处理。

## 架构

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend      │────▶│  LangGraph   │────▶│   Backend       │
│   (Next.js)     │     │   SDK        │     │   (LangGraph)   │
└─────────────────┘     └──────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Thread      │
                        │  State       │
                        └──────────────┘
```

## API Client

### 获取 Client 实例

```typescript
import { getAPIClient } from '@/core/api';

const client = getAPIClient();
```

Client 使用单例模式，确保整个应用使用同一个实例。

### Client 配置

```typescript
// core/api/api-client.ts
const client = new Client({
  apiUrl: process.env.NEXT_PUBLIC_LANGGRAPH_BASE_URL || '/api/langgraph',
});
```

## 线程管理 API

### 创建线程

```typescript
const thread = await client.threads.create({
  metadata: {
    title: '新对话',
    created_at: new Date().toISOString(),
  },
});

console.log(thread.thread_id); // 线程 ID
```

### 获取线程列表

```typescript
const threads = await client.threads.search({
  limit: 20,
  offset: 0,
});
```

### 获取线程详情

```typescript
const thread = await client.threads.get(threadId);
```

### 删除线程

```typescript
await client.threads.delete(threadId);
```

### 更新线程元数据

```typescript
await client.threads.update(threadId, {
  metadata: {
    title: '新标题',
  },
});
```

## 消息流 API

### 发送消息（流式）

```typescript
const stream = await client.runs.stream(
  threadId,
  'lead_agent',  // Assistant ID
  {
    input: {
      messages: [
        { role: 'user', content: '你好' }
      ]
    },
    streamMode: 'messages',
  }
);

// 处理流式响应
for await (const chunk of stream) {
  switch (chunk.event) {
    case 'messages/partial':
      // 部分消息更新
      console.log(chunk.data);
      break;
    case 'messages/complete':
      // 完整消息
      console.log(chunk.data);
      break;
    case 'error':
      // 错误处理
      console.error(chunk.data);
      break;
  }
}
```

### 流式事件类型

| 事件 | 说明 |
|------|------|
| `messages/partial` | 消息部分内容 |
| `messages/complete` | 完整消息 |
| `values/partial` | 状态值部分更新 |
| `values/complete` | 完整状态值 |
| `updates` | 状态更新 |
| `error` | 错误 |
| `end` | 流结束 |

## 线程状态 API

### 获取线程状态

```typescript
const state = await client.threads.getState(threadId);
console.log(state.values); // 当前状态值
```

### 获取状态历史

```typescript
const history = await client.threads.getHistory(threadId);
```

### 更新线程状态

```typescript
await client.threads.updateState(threadId, {
  values: {
    messages: [...],
  },
});
```

## 工件（Artifacts）API

### 获取工件列表

```typescript
import { useArtifacts } from '@/core/artifacts';

function ArtifactsViewer({ threadId }: { threadId: string }) {
  const { artifacts, isLoading } = useArtifacts(threadId);

  if (isLoading) return <Skeleton />;

  return (
    <div>
      {artifacts.map(artifact => (
        <ArtifactCard key={artifact.id} data={artifact} />
      ))}
    </div>
  );
}
```

### 加载工件内容

```typescript
import { loadArtifact } from '@/core/artifacts/loader';

const content = await loadArtifact(threadId, artifactId);
```

### 工件类型

| 类型 | 说明 | 扩展名 |
|------|------|--------|
| `code` | 代码文件 | .js, .ts, .py, etc. |
| `image` | 图片 | .png, .jpg, .svg |
| `document` | 文档 | .md, .txt, .pdf |
| `webpage` | 网页 | .html |
| `data` | 数据 | .json, .csv |

## 技能（Skills）API

### 获取技能列表

```typescript
import { useSkills } from '@/core/skills';

function SkillsPage() {
  const { skills, isLoading } = useSkills();

  return (
    <div>
      {skills.map(skill => (
        <SkillCard key={skill.id} data={skill} />
      ))}
    </div>
  );
}
```

### 安装技能

```typescript
import { installSkill } from '@/core/skills/api';

await installSkill({
  name: 'my-skill',
  source: 'https://github.com/user/skill-repo',
});
```

### 技能配置

```typescript
interface Skill {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  config: Record<string, unknown>;
}
```

## MCP（Model Context Protocol）API

### 获取 MCP 配置

```typescript
import { useMCP } from '@/core/mcp';

function MCPSettings() {
  const { config, updateConfig } = useMCP();

  return (
    <div>
      {config.servers.map(server => (
        <MCPServerCard key={server.id} data={server} />
      ))}
    </div>
  );
}
```

### MCP 服务器类型

| 类型 | 说明 |
|------|------|
| `stdio` | 标准输入输出 |
| `sse` | Server-Sent Events |
| `http` | HTTP 请求 |

## 记忆（Memory）API

### 获取用户记忆

```typescript
import { useMemory } from '@/core/memory';

function MemorySettings() {
  const { memories, addMemory, deleteMemory } = useMemory();

  return (
    <div>
      {memories.map(memory => (
        <MemoryItem
          key={memory.id}
          data={memory}
          onDelete={() => deleteMemory(memory.id)}
        />
      ))}
    </div>
  );
}
```

### 添加记忆

```typescript
await addMemory({
  content: '用户偏好使用中文',
  category: 'preference',
});
```

## 模型（Models）API

### 获取可用模型

```typescript
import { useModels } from '@/core/models';

function ModelSelector() {
  const { models, selectedModel, setSelectedModel } = useModels();

  return (
    <Select value={selectedModel} onValueChange={setSelectedModel}>
      {models.map(model => (
        <SelectItem key={model.id} value={model.id}>
          {model.displayName}
        </SelectItem>
      ))}
    </Select>
  );
}
```

### 模型配置

```typescript
interface Model {
  id: string;
  displayName: string;
  provider: 'openai' | 'anthropic' | 'deepseek' | string;
  config: {
    temperature?: number;
    maxTokens?: number;
    topP?: number;
  };
}
```

## 文件上传 API

### 上传文件

```typescript
import { useUploads } from '@/core/uploads';

function FileUploader() {
  const { upload, isUploading } = useUploads();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const result = await upload(file, {
      threadId,
      metadata: { type: 'attachment' },
    });

    console.log(result.url); // 文件 URL
  };

  return <input type="file" onChange={handleFileChange} disabled={isUploading} />;
}
```

## 错误处理

### 常见错误类型

```typescript
try {
  const stream = await client.runs.stream(threadId, assistantId, input);
} catch (error) {
  if (error instanceof LangGraphError) {
    switch (error.code) {
      case 'THREAD_NOT_FOUND':
        // 线程不存在
        break;
      case 'ASSISTANT_NOT_FOUND':
        // Assistant 不存在
        break;
      case 'RATE_LIMITED':
        // 请求频率限制
        break;
      default:
        // 其他错误
    }
  }
}
```

### 全局错误处理

```typescript
// core/api/api-client.ts
client.on('error', (error) => {
  console.error('API Error:', error);
  // 发送错误到监控系统
});
```

## 类型定义

### 核心类型

```typescript
// core/threads/types.ts
interface Thread {
  thread_id: string;
  metadata: ThreadMetadata;
  created_at: string;
  updated_at: string;
}

interface ThreadMetadata {
  title?: string;
  description?: string;
  [key: string]: unknown;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

// core/artifacts/types.ts
interface Artifact {
  id: string;
  name: string;
  type: 'code' | 'image' | 'document' | 'webpage' | 'data';
  mimeType: string;
  size: number;
  createdAt: string;
  metadata?: Record<string, unknown>;
}
```

## 最佳实践

### 1. 使用 Hooks 封装 API 调用

```typescript
// 推荐
const { data, isLoading } = useThread(threadId);

// 不推荐
const [data, setData] = useState();
useEffect(() => {
  fetchThread(threadId).then(setData);
}, [threadId]);
```

### 2. 处理加载状态

```typescript
function Component() {
  const { data, isLoading, error } = useData();

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return <EmptyState />;

  return <DataView data={data} />;
}
```

### 3. 流式响应处理

```typescript
const [messages, setMessages] = useState<Message[]>([]);

useEffect(() => {
  const stream = client.runs.stream(threadId, assistantId, input);

  (async () => {
    for await (const chunk of stream) {
      if (chunk.event === 'messages/partial') {
        setMessages(prev => updateMessages(prev, chunk.data));
      }
    }
  })();

  return () => {
    // 清理流
    stream.cancel();
  };
}, [threadId]);
```

### 4. 错误重试

```typescript
const { data, error, refetch } = useQuery({
  queryKey: ['thread', threadId],
  queryFn: () => fetchThread(threadId),
  retry: 3,
  retryDelay: 1000,
});
```

## 调试技巧

### 1. 启用调试日志

```typescript
// .env
NEXT_PUBLIC_DEBUG_API=true
```

### 2. 使用浏览器开发者工具

- Network 标签查看 API 请求
- Console 查看日志输出
- React DevTools 检查组件状态

### 3. API 请求日志

```typescript
// core/api/api-client.ts
if (process.env.NODE_ENV === 'development') {
  client.interceptors.request.use((request) => {
    console.log('API Request:', request);
    return request;
  });
}
```

## 相关文档

- [LangGraph SDK 文档](https://www.npmjs.com/package/@langchain/langgraph-sdk)
- [LangGraph 概念](https://langchain-ai.github.io/langgraph/concepts/)
- [TanStack Query 文档](https://tanstack.com/query/latest)
