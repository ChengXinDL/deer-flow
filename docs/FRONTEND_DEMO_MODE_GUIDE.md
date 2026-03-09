# magicflow 前端 Demo 模式完整指南

## 概述

本文档记录了 magicflow 前端 Demo 模式的完整配置和使用方法，包括遇到的问题、解决方案以及最佳实践。这份文档的目标是让未来更容易配置和使用 Demo 模式�?
## 目录

1. [Demo 模式简介](#demo-模式简�?
2. [启用 Demo 模式](#启用-demo-模式)
3. [Demo 数据结构](#demo-数据结构)
4. [核心机制详解](#核心机制详解)
5. [常见问题与解决方案](#常见问题与解决方�?
6. [测试验证方法](#测试验证方法)
7. [最佳实践](#最佳实�?

---

## Demo 模式简�?
### 什么是 Demo 模式�?
Demo 模式�?magicflow 前端的一种特殊运行模式，它允许前端应用在没有后端服务的情况下运行，使用预置的 Demo 数据来展示应用功能�?
### Demo 模式的用�?
- **功能演示**：向用户展示 magicflow 的各种功�?- **离线预览**：在没有后端服务的情况下预览前端界面
- **开发测�?*：前端开发时不需要启动完整的后端服务
- **文档截图**：生成文档和演示材料

### Demo 模式的限�?
- �?可以浏览 Demo 线程和对话历�?- �?可以查看文件产物（图片、视频、文档等�?- �?可以查看任务列表和进�?- �?无法创建新的对话
- �?无法上传文件
- �?无法执行实际�?AI 推理

---

## 启用 Demo 模式

### 方法一：环境变量配置（推荐�?
�?`frontend/.env` 文件中设置：

```bash
# 启用静态网站模式，使用 mock 数据
NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true"

# 注释掉后�?API URL（如果之前设置过�?# NEXT_PUBLIC_BACKEND_BASE_URL="http://localhost:8001"
# NEXT_PUBLIC_LANGGRAPH_BASE_URL="http://localhost:2024"
```

### 方法二：启动时指定环境变�?
```bash
NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true" pnpm run dev
```

### 验证 Demo 模式是否启用

启动前端服务后，检查日志中是否有以下请求：

```
GET /mock/api/threads/search 200
```

如果看到 `/mock/api/` 路径的请求，说明 Demo 模式已成功启用�?
---

## Demo 数据结构

### 目录结构

```
frontend/public/demo/threads/
├── {thread_id_1}/
�?  ├── thread.json              # 线程元数据和消息历史
�?  └── user-data/
�?      ├── outputs/             # 生成的文件产�?�?      �?  ├── image.jpg
�?      �?  ├── document.md
�?      �?  └── ...
�?      └── uploads/             # 上传的文件（如果有）
├── {thread_id_2}/
�?  ├── thread.json
�?  └── user-data/
�?      └── outputs/
└── ...
```

### thread.json 文件结构

```json
{
  "values": {
    "messages": [...],           // 消息历史记录
    "artifacts": [               // 文件产物列表
      "mnt/user-data/outputs/image.jpg",
      "mnt/user-data/outputs/document.md"
    ],
    "todos": [...],              // 任务列表
    "title": "线程标题"           // 线程标题
  },
  "history": [...]               // 状态历史（可选）
}
```

### 文件产物路径规则

所有文件产物路径都�?`mnt/user-data/` 开头：

```
mnt/user-data/outputs/{filename}
```

实际文件位置�?
```
public/demo/threads/{thread_id}/user-data/outputs/{filename}
```

---

## 核心机制详解

### 1. API 路径切换机制

#### 配置文件：`frontend/src/core/config/index.ts`

```typescript
export function getLangGraphBaseURL() {
  if (env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true") {
    // Demo 模式：使�?mock API
    if (typeof window !== "undefined") {
      return `${window.location.origin}/mock/api`;
    }
    return "http://localhost:3002/mock/api";
  } else if (env.NEXT_PUBLIC_LANGGRAPH_BASE_URL) {
    // 自定义后�?URL
    return env.NEXT_PUBLIC_LANGGRAPH_BASE_URL;
  } else {
    // 默认：使�?nginx 代理
    if (typeof window !== "undefined") {
      return `${window.location.origin}/api/langgraph`;
    }
    return "http://localhost:2026/api/langgraph";
  }
}
```

**关键�?*�?- Demo 模式优先级最�?- 返回的路径不包含 `/api` 前缀（由 LangGraph SDK 自动添加�?- 需要同时处理客户端和服务端环境

### 2. API 客户端单例模�?
#### 文件：`frontend/src/core/api/api-client.ts`

```typescript
let _singleton: LangGraphClient | null = null;

export function getAPIClient(): LangGraphClient {
  const currentUrl = getLangGraphBaseURL();
  
  // Demo 模式下每次都创建新客户端，确保使用正确的 URL
  if (!_singleton || env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true") {
    _singleton = new LangGraphClient({
      apiUrl: currentUrl,
    });
  }
  
  return _singleton;
}
```

**关键�?*�?- 使用单例模式避免重复创建客户�?- Demo 模式下需要特殊处理，确保使用正确�?API 路径
- 环境变量改变时需要重新创建客户端

### 3. 文件产物 URL 构建

#### 文件：`frontend/src/core/artifacts/utils.ts`

```typescript
export function urlOfArtifact({
  filepath,
  threadId,
  download = false,
}: {
  filepath: string;
  threadId: string;
  download?: boolean;
}) {
  // 关键：Demo 模式下使�?LangGraph Base URL，而不�?Backend Base URL
  const baseURL = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true" 
    ? getLangGraphBaseURL()
    : getBackendBaseURL();
  
  return `${baseURL}/threads/${threadId}/artifacts${filepath}${download ? "?download=true" : ""}`;
}
```

**关键�?*�?- 文件产物 URL 必须使用正确�?Base URL
- Demo 模式下使�?`getLangGraphBaseURL()`（返�?`/mock/api`�?- 正常模式下使�?`getBackendBaseURL()`（返回后�?API 地址�?- 路径格式：`{baseURL}/threads/{threadId}/artifacts{filepath}`

### 4. Mock API 路由

#### 线程搜索：`frontend/src/app/mock/api/threads/search/route.ts`

```typescript
function getThreadData() {
  const threadsDir = fs.readdirSync(
    path.resolve(process.cwd(), "public/demo/threads"),
    { withFileTypes: true }
  );
  
  return threadsDir
    .map((threadId) => {
      if (threadId.isDirectory() && !threadId.name.startsWith(".")) {
        const threadData = fs.readFileSync(
          path.resolve(`public/demo/threads/${threadId.name}/thread.json`),
          "utf8"
        );
        return {
          thread_id: threadId.name,
          values: JSON.parse(threadData).values,
        };
      }
      return false;
    })
    .filter(Boolean);
}

// 支持 GET �?POST 方法
export function GET() {
  return Response.json(getThreadData());
}

export function POST() {
  return Response.json(getThreadData());
}
```

**关键�?*�?- 必须同时支持 GET �?POST 方法（LangGraph SDK 可能使用任一方法�?- 使用文件系统读取 Demo 数据
- 返回格式必须与真�?API 一�?
#### 文件产物：`frontend/src/app/mock/api/threads/[thread_id]/artifacts/[[...artifact_path]]/route.ts`

```typescript
export async function GET(request, { params }) {
  const threadId = (await params).thread_id;
  let artifactPath = (await params).artifact_path?.join("/") ?? "";
  
  // �?mnt/user-data/ 路径映射到实际文件路�?  if (artifactPath.startsWith("mnt/")) {
    artifactPath = path.resolve(
      process.cwd(),
      artifactPath.replace("mnt/", `public/demo/threads/${threadId}/`)
    );
    
    if (fs.existsSync(artifactPath)) {
      // 处理视频文件
      if (artifactPath.endsWith(".mp4")) {
        return new Response(fs.readFileSync(artifactPath), {
          status: 200,
          headers: { "Content-Type": "video/mp4" }
        });
      }
      
      // 处理其他文件
      return new Response(fs.readFileSync(artifactPath), { status: 200 });
    }
  }
  
  return new Response("File not found", { status: 404 });
}
```

**关键�?*�?- 路径映射：`mnt/user-data/` �?`public/demo/threads/{thread_id}/user-data/`
- 需要处理不同的文件类型（设置正确的 Content-Type�?- 支持下载参数（`?download=true`�?
### 5. 工作空间自动重定�?
#### 文件：`frontend/src/app/workspace/page.tsx`

```typescript
export default function WorkspacePage() {
  if (env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true") {
    // Demo 模式：自动重定向到第一�?Demo 线程
    const firstThread = fs
      .readdirSync(path.resolve(process.cwd(), "public/demo/threads"), {
        withFileTypes: true,
      })
      .find((thread) => thread.isDirectory() && !thread.name.startsWith("."));
    
    if (firstThread) {
      return redirect(`/workspace/chats/${firstThread.name}`);
    }
  }
  
  // 正常模式：重定向到新对话页面
  return redirect("/workspace/chats/new");
}
```

**关键�?*�?- Demo 模式下自动展示第一�?Demo 线程
- 提升用户体验，避免显示空白的新对话页�?
---

## 常见问题与解决方�?
### 问题 1：Demo 数据未加�?
**症状**�?- 前端页面显示空白
- 网络请求返回 404 错误
- 日志显示请求 `/api/langgraph/threads/search` 而不�?`/mock/api/threads/search`

**原因**�?- 环境变量未正确设�?- API 客户端缓存了旧的配置

**解决方案**�?
1. 检�?`.env` 文件�?```bash
NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true"
```

2. 重启前端服务�?```bash
# 停止服务（Ctrl+C�?pnpm run dev
```

3. 验证环境变量是否生效�?```bash
# 检查日志中的请求路�?GET /mock/api/threads/search 200
```

### 问题 2：文件产物无法显�?
**症状**�?- 图片、文档等文件无法显示
- 网络请求返回 404 错误
- 日志显示请求 `/api/threads/{thread_id}/artifacts/...` 而不�?`/mock/api/threads/{thread_id}/artifacts/...`

**原因**�?- 文件产物 URL 构建逻辑未正确处�?Demo 模式
- `urlOfArtifact` 函数使用了错误的 Base URL

**解决方案**�?
修改 `frontend/src/core/artifacts/utils.ts`�?
```typescript
export function urlOfArtifact({ filepath, threadId, download = false }) {
  // 关键修改：Demo 模式下使�?getLangGraphBaseURL()
  const baseURL = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true" 
    ? getLangGraphBaseURL()
    : getBackendBaseURL();
  
  return `${baseURL}/threads/${threadId}/artifacts${filepath}${download ? "?download=true" : ""}`;
}
```

**验证方法**�?
```bash
# 测试文件产物 API
curl http://localhost:3002/mock/api/threads/{thread_id}/artifacts/mnt/user-data/outputs/{filename}

# 应该返回 200 状态码和文件内�?```

### 问题 3：Mock API 路由不支�?GET 方法

**症状**�?- 请求返回 405 Method Not Allowed
- LangGraph SDK 使用 GET 方法请求，但路由只支�?POST

**原因**�?- Mock API 路由只实现了 POST 方法

**解决方案**�?
修改 `frontend/src/app/mock/api/threads/search/route.ts`�?
```typescript
// 同时支持 GET �?POST
export function GET() {
  return Response.json(getThreadData());
}

export function POST() {
  return Response.json(getThreadData());
}
```

### 问题 4：环境变量未生效

**症状**�?- 修改 `.env` 文件后，前端行为未改�?- 日志显示环境变量未更�?
**原因**�?- Next.js 缓存了环境变�?- 需要重启开发服务器

**解决方案**�?
1. 停止开发服务器（Ctrl+C�?2. 修改 `.env` 文件
3. 重新启动：`pnpm run dev`

**注意**：环境变量只在启动时读取，运行时修改不会生效�?
### 问题 5：文件路径映射错�?
**症状**�?- 文件产物请求返回 404
- 文件路径不正�?
**原因**�?- Mock API 路由的路径映射逻辑错误

**解决方案**�?
检查路径映射逻辑�?
```typescript
// 错误示例�?artifactPath.replace("mnt/", `public/demo/threads/${threadId}/`)

// 正确示例�?artifactPath.replace("mnt/", `public/demo/threads/${threadId}/user-data/`)
```

**调试方法**�?
```typescript
console.log("Original path:", artifactPath);
console.log("Resolved path:", resolvedPath);
console.log("File exists:", fs.existsSync(resolvedPath));
```

---

## 测试验证方法

### 1. 验证 Demo 模式启用

```bash
# 检查前端日�?GET /mock/api/threads/search 200

# 测试 API 端点
curl http://localhost:3002/mock/api/threads/search
# 应该返回 JSON 数组，包含所�?Demo 线程
```

### 2. 验证线程数据加载

```bash
# 测试线程历史 API
curl http://localhost:3002/mock/api/threads/{thread_id}/history
# 应该返回线程的完整历史记�?```

### 3. 验证文件产物加载

```bash
# 测试图片文件
curl http://localhost:3002/mock/api/threads/{thread_id}/artifacts/mnt/user-data/outputs/image.jpg
# 应该返回 200 状态码和图片数�?
# 测试文档文件
curl http://localhost:3002/mock/api/threads/{thread_id}/artifacts/mnt/user-data/outputs/document.md
# 应该返回 200 状态码和文档内�?```

### 4. 验证前端页面

1. 访问 http://localhost:3002
2. 应该自动重定向到第一�?Demo 线程
3. 检查对话历史是否正确显�?4. 检查文件产物是否可以查�?5. 检查任务列表是否正确显�?
### 5. 验证输入框禁�?
�?Demo 模式下，输入框应该被禁用，并显示提示信息�?
```
"此功能在演示模式下不可用"
```

---

## 最佳实�?
### 1. 环境变量管理

**推荐做法**�?
```bash
# .env 文件示例
# Demo 模式
NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true"

# 开发模式（连接真实后端�?# NEXT_PUBLIC_BACKEND_BASE_URL="http://localhost:8001"
# NEXT_PUBLIC_LANGGRAPH_BASE_URL="http://localhost:2024"
```

**注意事项**�?- 使用注释切换不同模式，而不是删除配�?- 保持 `.env.example` 文件同步更新
- 不要将敏感信息提交到版本控制

### 2. Demo 数据维护

**添加新的 Demo 线程**�?
1. 创建线程目录�?```bash
mkdir -p frontend/public/demo/threads/{thread_id}/user-data/outputs
```

2. 创建 `thread.json` 文件�?```json
{
  "values": {
    "messages": [...],
    "artifacts": [...],
    "title": "Demo 标题"
  }
}
```

3. 添加文件产物�?`user-data/outputs/` 目录

4. 更新 `artifacts` 数组，包含所有文件路�?
**注意事项**�?- `thread_id` 使用 UUID 格式
- 文件路径必须�?`mnt/user-data/outputs/` 开�?- `thread.json` 文件大小不要超过 20MB（Next.js 默认限制�?
### 3. Mock API 扩展

**添加新的 Mock API 端点**�?
1. 创建路由文件�?```
frontend/src/app/mock/api/{endpoint}/route.ts
```

2. 实现 GET �?�?POST 方法�?```typescript
export function GET() {
  return Response.json({ data: "..." });
}
```

3. 确保返回格式与真�?API 一�?
**注意事项**�?- Mock API 应该模拟真实 API 的行�?- 考虑添加适当的延迟，模拟网络请求
- 处理错误情况�?04, 500 等）

### 4. 代码组织

**推荐结构**�?
```
frontend/src/
├── core/
�?  ├── config/
�?  �?  └── index.ts          # API URL 配置
�?  ├── api/
�?  �?  └── api-client.ts     # API 客户�?�?  └── artifacts/
�?      └── utils.ts          # 文件产物 URL 构建
└── app/
    └── mock/
        └── api/              # Mock API 路由
            ├── threads/
            ├── models/
            └── skills/
```

**注意事项**�?- 保持配置集中管理
- Mock API 路由与真�?API 路径保持一�?- 使用 TypeScript 类型确保类型安全

### 5. 调试技�?
**启用详细日志**�?
```typescript
// 在关键位置添加日�?console.log("Demo mode:", env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY);
console.log("API URL:", getLangGraphBaseURL());
console.log("Artifact URL:", urlOfArtifact({ filepath, threadId }));
```

**检查网络请�?*�?
1. 打开浏览器开发者工具（F12�?2. 切换�?Network 标签
3. 筛�?XHR 请求
4. 检查请求路径和响应内容

**检查文件系�?*�?
```bash
# 列出所�?Demo 线程
ls frontend/public/demo/threads/

# 检查特定线程的文件
ls frontend/public/demo/threads/{thread_id}/user-data/outputs/

# 查看线程数据
cat frontend/public/demo/threads/{thread_id}/thread.json | jq .
```

### 6. 性能优化

**减少文件读取**�?
```typescript
// 缓存线程数据
const threadCache = new Map<string, any>();

function getThreadData(threadId: string) {
  if (!threadCache.has(threadId)) {
    const data = fs.readFileSync(`public/demo/threads/${threadId}/thread.json`);
    threadCache.set(threadId, JSON.parse(data));
  }
  return threadCache.get(threadId);
}
```

**使用流式响应**�?
```typescript
// 对于大文件，使用流式响应
export async function GET(request, { params }) {
  const filePath = resolveArtifactPath(params);
  
  if (fs.existsSync(filePath)) {
    const stream = fs.createReadStream(filePath);
    return new Response(stream as any, {
      headers: { "Content-Type": getContentType(filePath) }
    });
  }
  
  return new Response("Not found", { status: 404 });
}
```

### 7. 安全考虑

**文件访问控制**�?
```typescript
// 验证文件路径，防止目录遍历攻�?function resolveArtifactPath(threadId: string, artifactPath: string): string {
  const basePath = path.resolve(process.cwd(), `public/demo/threads/${threadId}`);
  const resolvedPath = path.resolve(basePath, artifactPath);
  
  // 确保解析后的路径在允许的目录�?  if (!resolvedPath.startsWith(basePath)) {
    throw new Error("Invalid path");
  }
  
  return resolvedPath;
}
```

**输入验证**�?
```typescript
// 验证 thread_id 格式
function isValidThreadId(threadId: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(threadId);
}
```

---

## 总结

### 关键知识�?
1. **环境变量优先�?*：`NEXT_PUBLIC_STATIC_WEBSITE_ONLY` > `NEXT_PUBLIC_LANGGRAPH_BASE_URL` > 默认配置
2. **API 路径构建**：Demo 模式使用 `/mock/api`，正常模式使用后�?URL
3. **文件产物 URL**：必须使用正确的 Base URL（Demo 模式下使�?`getLangGraphBaseURL()`�?4. **Mock API 路由**：必须同时支�?GET �?POST 方法
5. **路径映射**：`mnt/user-data/` 映射�?`public/demo/threads/{thread_id}/user-data/`

### 常见错误

1. �?文件产物 URL 使用�?`getBackendBaseURL()` 而不�?`getLangGraphBaseURL()`
2. �?Mock API 路由只实现了 POST 方法
3. �?环境变量修改后未重启服务
4. �?文件路径映射错误（缺�?`user-data/` 目录�?5. �?API 客户端缓存导致使用旧的配�?
### 检查清�?
在配�?Demo 模式时，按以下顺序检查：

- [ ] `.env` 文件中设置了 `NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true"`
- [ ] 注释掉了 `NEXT_PUBLIC_BACKEND_BASE_URL` �?`NEXT_PUBLIC_LANGGRAPH_BASE_URL`
- [ ] 重启了前端服�?- [ ] 日志显示请求 `/mock/api/threads/search`
- [ ] 文件产物 URL 使用�?`/mock/api/threads/{thread_id}/artifacts/...`
- [ ] Demo 线程和文件产物可以正常显�?
---

## 附录

### 相关文件清单

**配置文件**�?- `frontend/.env` - 环境变量配置
- `frontend/src/env.js` - 环境变量验证
- `frontend/src/core/config/index.ts` - API URL 配置

**API 客户�?*�?- `frontend/src/core/api/api-client.ts` - LangGraph 客户�?
**文件产物**�?- `frontend/src/core/artifacts/utils.ts` - URL 构建
- `frontend/src/core/artifacts/loader.ts` - 内容加载

**Mock API 路由**�?- `frontend/src/app/mock/api/threads/search/route.ts` - 线程搜索
- `frontend/src/app/mock/api/threads/[thread_id]/history/route.ts` - 线程历史
- `frontend/src/app/mock/api/threads/[thread_id]/artifacts/[[...artifact_path]]/route.ts` - 文件产物

**页面组件**�?- `frontend/src/app/workspace/page.tsx` - 工作空间主页
- `frontend/src/app/workspace/chats/page.tsx` - 线程列表
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx` - 线程详情

### 参考链�?
- [Next.js 环境变量文档](https://nextjs.org/docs/basic-features/environment-variables)
- [LangGraph SDK 文档](https://langchain-ai.github.io/langgraph/)
- [Next.js API 路由文档](https://nextjs.org/docs/api-routes/introduction)

---

**文档版本**�?.0  
**最后更�?*�?026-03-06  
**维护�?*：MAGICFlow 开发团�?
