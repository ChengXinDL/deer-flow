# DeerFlow 后端 API 参考文档

## 概述

DeerFlow 后端暴露两组 API：

1. **LangGraph API** - Agent 交互、线程和流式传输 (`/api/langgraph/*`)
2. **Gateway API** - 模型、MCP、技能、上传和工件 (`/api/*`)

所有 API 通过 Nginx 反向代理在端口 2026 访问。

---

## LangGraph API

**Base URL**: `/api/langgraph`

由 LangGraph 服务器提供，遵循 LangGraph SDK 规范。

### 线程管理

#### 创建线程

```http
POST /api/langgraph/threads
Content-Type: application/json
```

**请求体**:
```json
{
  "metadata": {
    "title": "新对话"
  }
}
```

**响应**:
```json
{
  "thread_id": "abc123",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {
    "title": "新对话"
  }
}
```

#### 获取线程状态

```http
GET /api/langgraph/threads/{thread_id}/state
```

**响应**:
```json
{
  "values": {
    "messages": [...],
    "sandbox": {...},
    "artifacts": [...],
    "thread_data": {...},
    "title": "对话标题"
  },
  "next": [],
  "config": {...}
}
```

#### 获取线程历史

```http
GET /api/langgraph/threads/{thread_id}/history
```

**响应**:
```json
{
  "history": [
    {
      "values": {...},
      "next": [...],
      "config": {...}
    }
  ]
}
```

#### 删除线程

```http
DELETE /api/langgraph/threads/{thread_id}
```

**响应**: `204 No Content`

### 运行管理

#### 创建运行

执行 Agent 并传入输入。

```http
POST /api/langgraph/threads/{thread_id}/runs
Content-Type: application/json
```

**请求体**:
```json
{
  "input": {
    "messages": [
      {
        "role": "user",
        "content": "你好，能帮我吗？"
      }
    ]
  },
  "config": {
    "configurable": {
      "model_name": "gpt-4",
      "thinking_enabled": false,
      "is_plan_mode": false
    }
  },
  "stream_mode": ["values", "messages"]
}
```

**Configurable 选项**:
- `model_name` (string): 覆盖默认模型
- `thinking_enabled` (boolean): 启用扩展思考模式
- `is_plan_mode` (boolean): 启用任务跟踪模式

**响应**: Server-Sent Events (SSE) 流

```
event: values
data: {"messages": [...], "title": "..."}

event: messages
data: {"content": "你好！我很乐意帮忙。", "role": "assistant"}

event: end
data: {}
```

#### 流式运行

实时流式响应。

```http
POST /api/langgraph/threads/{thread_id}/runs/stream
Content-Type: application/json
```

请求体与创建运行相同。返回 SSE 流。

#### 获取运行列表

```http
GET /api/langgraph/threads/{thread_id}/runs
```

**响应**:
```json
{
  "runs": [
    {
      "run_id": "run123",
      "status": "success",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### SSE 事件类型

| 事件 | 说明 |
|------|------|
| `values` | 完整状态值 |
| `values/partial` | 部分状态更新 |
| `messages` | 完整消息 |
| `messages/partial` | 部分消息内容 |
| `updates` | 状态更新 |
| `error` | 错误信息 |
| `end` | 流结束 |

---

## Gateway API

**Base URL**: `/api`

由 FastAPI 应用提供，处理非 Agent 操作。

### 模型 API

#### 列出模型

获取配置中所有可用的 LLM 模型。

```http
GET /api/models
```

**响应**:
```json
{
  "models": [
    {
      "name": "gpt-4o",
      "display_name": "GPT-4o",
      "supports_thinking": false,
      "supports_vision": true
    },
    {
      "name": "claude-3-opus",
      "display_name": "Claude 3 Opus",
      "supports_thinking": false,
      "supports_vision": true
    },
    {
      "name": "deepseek-v3",
      "display_name": "DeepSeek V3",
      "supports_thinking": true,
      "supports_vision": false
    }
  ]
}
```

#### 获取模型详情

```http
GET /api/models/{model_name}
```

**响应**:
```json
{
  "name": "gpt-4o",
  "display_name": "GPT-4o",
  "model": "gpt-4o",
  "provider": "openai",
  "supports_thinking": false,
  "supports_vision": true,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

### MCP API

#### 获取 MCP 配置

```http
GET /api/mcp/config
```

**响应**:
```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

#### 更新 MCP 配置

```http
PUT /api/mcp/config
Content-Type: application/json
```

**请求体**:
```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN"
      }
    }
  }
}
```

**响应**: `200 OK`

### 技能 API

#### 列出技能

```http
GET /api/skills
```

**响应**:
```json
{
  "skills": [
    {
      "name": "research",
      "display_name": "Research",
      "description": "Deep research on any topic",
      "version": "1.0.0",
      "enabled": true
    }
  ]
}
```

#### 获取技能详情

```http
GET /api/skills/{skill_name}
```

**响应**:
```json
{
  "name": "research",
  "display_name": "Research",
  "description": "Deep research on any topic",
  "version": "1.0.0",
  "author": "DeerFlow Team",
  "content": "# Research Skill\n\n...",
  "enabled": true
}
```

#### 更新技能状态

```http
PUT /api/skills/{skill_name}
Content-Type: application/json
```

**请求体**:
```json
{
  "enabled": false
}
```

#### 安装技能

```http
POST /api/skills/install
Content-Type: multipart/form-data
```

**请求体**:
- `file`: `.skill` 归档文件

**响应**:
```json
{
  "success": true,
  "skill": {
    "name": "my-skill",
    "version": "1.0.0"
  }
}
```

### 记忆 API

#### 获取记忆数据

```http
GET /api/memory
```

**响应**:
```json
{
  "context": {
    "work": "Software engineer",
    "personal": "Lives in Beijing"
  },
  "facts": [
    {
      "content": "Prefers Python over JavaScript",
      "confidence": 0.95,
      "category": "preference"
    }
  ],
  "history": [
    {
      "date": "2024-01-15",
      "summary": "Discussed project architecture"
    }
  ]
}
```

#### 强制重新加载记忆

```http
POST /api/memory/reload
```

**响应**: `200 OK`

#### 获取记忆配置

```http
GET /api/memory/config
```

**响应**:
```json
{
  "enabled": true,
  "max_tokens": 2000,
  "similarity_weight": 0.6,
  "confidence_weight": 0.4
}
```

#### 获取记忆状态和配置

```http
GET /api/memory/status
```

**响应**:
```json
{
  "config": {...},
  "data": {...}
}
```

### 文件上传 API

#### 上传文件

```http
POST /api/threads/{thread_id}/uploads
Content-Type: multipart/form-data
```

**请求体**:
- `files`: 一个或多个文件

**响应**:
```json
{
  "success": true,
  "files": [
    {
      "filename": "document.pdf",
      "size": 1234567,
      "path": ".deer-flow/threads/{thread_id}/user-data/uploads/document.pdf",
      "virtual_path": "/mnt/user-data/uploads/document.pdf",
      "artifact_url": "/api/threads/{thread_id}/artifacts/mnt/user-data/uploads/document.pdf",
      "markdown_file": "document.md",
      "markdown_path": ".deer-flow/threads/{thread_id}/user-data/uploads/document.md",
      "markdown_virtual_path": "/mnt/user-data/uploads/document.md"
    }
  ],
  "message": "Successfully uploaded 1 file(s)"
}
```

**支持的自动转换格式**:
- PDF (`.pdf`)
- PowerPoint (`.ppt`, `.pptx`)
- Excel (`.xls`, `.xlsx`)
- Word (`.doc`, `.docx`)

#### 列出已上传文件

```http
GET /api/threads/{thread_id}/uploads/list
```

**响应**:
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "size": 1234567,
      "path": ".deer-flow/threads/{thread_id}/user-data/uploads/document.pdf",
      "virtual_path": "/mnt/user-data/uploads/document.pdf",
      "artifact_url": "/api/threads/{thread_id}/artifacts/mnt/user-data/uploads/document.pdf",
      "extension": ".pdf",
      "modified": 1705997600.0
    }
  ],
  "count": 1
}
```

#### 删除文件

```http
DELETE /api/threads/{thread_id}/uploads/{filename}
```

**响应**:
```json
{
  "success": true,
  "message": "Deleted document.pdf"
}
```

### 工件 API

#### 获取工件

```http
GET /api/threads/{thread_id}/artifacts/{path}
```

**查询参数**:
- `download` (boolean): 是否作为附件下载

**响应**: 文件内容

---

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### 常见错误码

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `BAD_REQUEST` | 请求参数错误 |
| 401 | `UNAUTHORIZED` | 未授权 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` | 资源冲突 |
| 422 | `VALIDATION_ERROR` | 验证错误 |
| 429 | `RATE_LIMITED` | 请求过于频繁 |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 |

### LangGraph 特定错误

| 错误码 | 说明 |
|--------|------|
| `THREAD_NOT_FOUND` | 线程不存在 |
| `ASSISTANT_NOT_FOUND` | Assistant 不存在 |
| `RUN_NOT_FOUND` | 运行不存在 |
| `INVALID_CONFIG` | 配置无效 |

---

## 认证

目前 DeerFlow 使用简单的 API key 认证：

```http
GET /api/models
Authorization: Bearer {api_key}
```

或在请求头中：

```http
GET /api/models
X-API-Key: {api_key}
```

---

## 速率限制

默认速率限制：

| 端点 | 限制 |
|------|------|
| `/api/langgraph/*` | 100 请求/分钟 |
| `/api/*` | 200 请求/分钟 |

响应头：

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705998000
```

---

## SDK 示例

### Python

```python
from langgraph import Client

client = Client(api_url="http://localhost:2026/api/langgraph")

# 创建线程
thread = client.threads.create()

# 发送消息
stream = client.runs.stream(
    thread.thread_id,
    "lead_agent",
    input={"messages": [{"role": "user", "content": "Hello"}]}
)

for chunk in stream:
    print(chunk)
```

### JavaScript/TypeScript

```typescript
import { Client } from '@langchain/langgraph-sdk';

const client = new Client({
  apiUrl: 'http://localhost:2026/api/langgraph'
});

// 创建线程
const thread = await client.threads.create();

// 发送消息
const stream = await client.runs.stream(
  thread.thread_id,
  'lead_agent',
  {
    input: { messages: [{ role: 'user', content: 'Hello' }] }
  }
);

for await (const chunk of stream) {
  console.log(chunk);
}
```

### cURL

```bash
# 创建线程
curl -X POST http://localhost:2026/api/langgraph/threads \
  -H "Content-Type: application/json" \
  -d '{"metadata": {}}'

# 发送消息（流式）
curl -X POST http://localhost:2026/api/langgraph/threads/{thread_id}/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"messages": [{"role": "user", "content": "Hello"}]},
    "stream_mode": ["messages"]
  }'
```
