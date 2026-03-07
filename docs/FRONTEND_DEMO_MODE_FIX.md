# Demo 模式配置问题修复记录

## 问题概述

在配置 DeerFlow 前端 Demo 模式时，遇到了 Demo 数据和文件产物无法加载的问题。

## 问题表现

1. **Demo 线程列表无法加载**
   - 前端请求 `/api/langgraph/threads/search` 返回 404
   - 应该请求 `/mock/api/threads/search`

2. **文件产物无法显示**
   - 图片、文档等文件请求返回 404
   - 请求路径：`/api/threads/{thread_id}/artifacts/...`
   - 应该请求：`/mock/api/threads/{thread_id}/artifacts/...`

## 根本原因分析

### 原因 1：API 路径配置不完整

**文件**：`frontend/src/core/config/index.ts`

**问题**：`getLangGraphBaseURL()` 函数没有处理 `NEXT_PUBLIC_STATIC_WEBSITE_ONLY` 环境变量。

**影响**：API 客户端使用了错误的 Base URL，导致请求路径不正确。

### 原因 2：文件产物 URL 构建错误

**文件**：`frontend/src/core/artifacts/utils.ts`

**问题**：`urlOfArtifact()` 函数总是使用 `getBackendBaseURL()`，没有考虑 Demo 模式。

**影响**：文件产物 URL 指向了不存在的后端 API，而不是 Mock API。

### 原因 3：Mock API 路由方法不完整

**文件**：`frontend/src/app/mock/api/threads/search/route.ts`

**问题**：只实现了 POST 方法，没有实现 GET 方法。

**影响**：LangGraph SDK 使用 GET 方法请求时返回 405 错误。

## 解决方案

### 修改 1：完善 API 路径配置

**文件**：`frontend/src/core/config/index.ts`

```typescript
export function getLangGraphBaseURL() {
  // 新增：优先检查 Demo 模式
  if (env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true") {
    if (typeof window !== "undefined") {
      return `${window.location.origin}/mock/api`;
    }
    return "http://localhost:3002/mock/api";
  }
  
  // 原有逻辑...
}
```

**关键点**：
- Demo 模式优先级最高
- 返回 `/mock/api` 路径（不包含 `/api` 前缀）
- 同时处理客户端和服务端环境

### 修改 2：修复文件产物 URL 构建

**文件**：`frontend/src/core/artifacts/utils.ts`

```typescript
export function urlOfArtifact({ filepath, threadId, download = false }) {
  // 关键修改：根据模式选择正确的 Base URL
  const baseURL = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true" 
    ? getLangGraphBaseURL()    // Demo 模式：返回 /mock/api
    : getBackendBaseURL();      // 正常模式：返回后端 URL
  
  return `${baseURL}/threads/${threadId}/artifacts${filepath}${download ? "?download=true" : ""}`;
}
```

**关键点**：
- Demo 模式下使用 `getLangGraphBaseURL()`
- 正常模式下使用 `getBackendBaseURL()`
- 路径格式统一：`{baseURL}/threads/{threadId}/artifacts{filepath}`

### 修改 3：完善 Mock API 路由

**文件**：`frontend/src/app/mock/api/threads/search/route.ts`

```typescript
// 重构：提取公共逻辑
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

// 新增：支持 GET 方法
export function GET() {
  return Response.json(getThreadData());
}

// 保留：支持 POST 方法
export function POST() {
  return Response.json(getThreadData());
}
```

**关键点**：
- 同时支持 GET 和 POST 方法
- 提取公共逻辑，避免代码重复
- 返回格式与真实 API 保持一致

### 修改 4：优化 API 客户端

**文件**：`frontend/src/core/api/api-client.ts`

```typescript
let _singleton: LangGraphClient | null = null;

export function getAPIClient(): LangGraphClient {
  const currentUrl = getLangGraphBaseURL();
  
  // 新增：Demo 模式下每次都创建新客户端
  if (!_singleton || env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true") {
    _singleton = new LangGraphClient({
      apiUrl: currentUrl,
    });
  }
  
  return _singleton;
}
```

**关键点**：
- 保持单例模式，避免重复创建
- Demo 模式下特殊处理，确保使用正确的 URL
- 环境变量改变时重新创建客户端

## 验证方法

### 1. 测试 Mock API 端点

```bash
# 测试线程搜索
curl http://localhost:3002/mock/api/threads/search

# 测试线程历史
curl http://localhost:3002/mock/api/threads/{thread_id}/history

# 测试文件产物
curl http://localhost:3002/mock/api/threads/{thread_id}/artifacts/mnt/user-data/outputs/{filename}
```

### 2. 检查前端日志

启动前端服务后，应该看到：

```
GET /mock/api/threads/search 200
POST /mock/api/threads/search 200
POST /mock/api/threads/{thread_id}/history 200
GET /mock/api/threads/{thread_id}/artifacts/mnt/user-data/outputs/{filename} 200
```

### 3. 浏览器验证

1. 访问 http://localhost:3002
2. 应该自动重定向到第一个 Demo 线程
3. 检查对话历史是否显示
4. 检查文件产物是否可以查看

## 经验教训

### 1. API 路径构建的统一性

**问题**：不同类型的 API 请求使用了不同的 Base URL 构建方法。

**教训**：
- 所有 API 请求应该使用统一的 Base URL 配置
- 文件产物 URL 也应该遵循相同的规则
- 在 Demo 模式下，所有 API 都应该指向 Mock API

### 2. 环境变量的优先级

**问题**：环境变量的处理顺序不明确，导致配置冲突。

**教训**：
- 明确定义环境变量的优先级顺序
- Demo 模式应该具有最高优先级
- 在代码注释中说明优先级逻辑

### 3. Mock API 的完整性

**问题**：Mock API 只实现了部分 HTTP 方法，导致请求失败。

**教训**：
- Mock API 应该支持所有可能使用的 HTTP 方法
- 参考 LangGraph SDK 的实现，了解它使用哪些方法
- 测试时覆盖所有可能的请求方式

### 4. 单例模式的陷阱

**问题**：API 客户端使用单例模式，环境变量改变后不会更新。

**教训**：
- 单例模式需要考虑配置更新的场景
- 在 Demo 模式下需要特殊处理
- 或者考虑不使用单例，每次都创建新客户端

### 5. 路径映射的准确性

**问题**：文件路径映射逻辑错误，导致找不到文件。

**教训**：
- 明确路径映射规则：`mnt/user-data/` → `public/demo/threads/{thread_id}/user-data/`
- 添加路径验证，防止路径遍历攻击
- 在日志中输出解析后的路径，便于调试

## 最佳实践

### 1. 配置集中管理

```typescript
// 所有 API URL 配置集中在 core/config/index.ts
export function getLangGraphBaseURL() { ... }
export function getBackendBaseURL() { ... }
```

### 2. 环境变量验证

```typescript
// 在 env.js 中定义和验证环境变量
client: {
  NEXT_PUBLIC_STATIC_WEBSITE_ONLY: z.string().optional(),
  NEXT_PUBLIC_BACKEND_BASE_URL: z.string().optional(),
  NEXT_PUBLIC_LANGGRAPH_BASE_URL: z.string().optional(),
}
```

### 3. 条件逻辑清晰

```typescript
// 使用清晰的条件判断
const baseURL = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true" 
  ? getLangGraphBaseURL()
  : getBackendBaseURL();
```

### 4. 错误处理完善

```typescript
// 添加错误处理和日志
if (!fs.existsSync(filePath)) {
  console.error("File not found:", filePath);
  return new Response("File not found", { status: 404 });
}
```

### 5. 测试覆盖全面

```bash
# 测试所有 API 端点
curl http://localhost:3002/mock/api/threads/search
curl http://localhost:3002/mock/api/threads/{thread_id}/history
curl http://localhost:3002/mock/api/threads/{thread_id}/artifacts/{path}
curl http://localhost:3002/mock/api/models
curl http://localhost:3002/mock/api/skills
```

## 相关文档

- [前端 Demo 模式完整指南](./FRONTEND_DEMO_MODE_GUIDE.md)
- [前端开发指南](./FRONTEND_DEVELOPMENT_GUIDE.md)
- [前端故障排除](./FRONTEND_TROUBLESHOOTING.md)

---

**文档版本**：1.0  
**创建日期**：2026-03-06  
**最后更新**：2026-03-06
