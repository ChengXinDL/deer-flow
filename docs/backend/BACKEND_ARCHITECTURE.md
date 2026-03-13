# magicflow 后端架构文档

## 系统架构概览

```
┌──────────────────────────────────────────────────────────────────────────�?�?                             Client (Browser)                             �?└─────────────────────────────────┬────────────────────────────────────────�?                                  �?                                  �?┌──────────────────────────────────────────────────────────────────────────�?�?                         Nginx (Port 2026)                               �?�?                   Unified Reverse Proxy Entry Point                      �?�? ┌────────────────────────────────────────────────────────────────────�? �?�? �? /api/langgraph/*  �? LangGraph Server (2024)                      �? �?�? �? /api/*            �? Gateway API (8001)                           �? �?�? �? /*                �? Frontend (3000)                               �? �?�? └────────────────────────────────────────────────────────────────────�? �?└─────────────────────────────────┬────────────────────────────────────────�?                                  �?          ┌───────────────────────┼───────────────────────�?          �?                      �?                      �?          �?                      �?                      �?┌─────────────────────�?┌─────────────────────�?┌─────────────────────�?�?  LangGraph Server  �?�?   Gateway API      �?�?    Frontend        �?�?    (Port 2024)     �?�?   (Port 8001)      �?�?   (Port 3000)      �?�?                    �?�?                    �?�?                    �?�? - Agent Runtime    �?�? - Models API       �?�? - Next.js App      �?�? - Thread Mgmt      �?�? - MCP Config       �?�? - React UI         �?�? - SSE Streaming    �?�? - Skills Mgmt      �?�? - Chat Interface   �?�? - Checkpointing    �?�? - File Uploads     �?�?                    �?�?                    �?�? - Artifacts        �?�?                    �?└─────────────────────�?└─────────────────────�?└─────────────────────�?          �?                      �?          �?    ┌─────────────────�?          �?    �?          �?    �?┌──────────────────────────────────────────────────────────────────────────�?�?                        Shared Configuration                              �?�? ┌─────────────────────────�? ┌────────────────────────────────────────�?�?�? �?     config.yaml        �? �?     extensions_config.json            �?�?�? �? - Models               �? �? - MCP Servers                         �?�?�? �? - Tools                �? �? - Skills State                        �?�?�? �? - Sandbox              �? �?                                       �?�?�? �? - Summarization        �? �?                                       �?�?�? └─────────────────────────�? └────────────────────────────────────────�?�?└──────────────────────────────────────────────────────────────────────────�?```

## 核心组件

### 1. LangGraph Server (端口 2024)

**职责**:
- Agent 运行时和工作流执�?- 线程状态管�?- 中间件链执行
- 工具执行编排
- SSE 流式响应

**入口**: `src/agents/lead_agent/agent.py:make_lead_agent`

**配置**: `langgraph.json`

```json
{
  "graphs": {
    "lead_agent": "src.agents:make_lead_agent"
  }
}
```

### 2. Gateway API (端口 8001)

基于 FastAPI �?REST API，提供非 Agent 操作的端点�?
**入口**: `src/gateway/app.py`

**路由模块**:

| 路由 | 端点 | 功能 |
|------|------|------|
| models.py | `/api/models` | 模型列表和详�?|
| mcp.py | `/api/mcp` | MCP 服务器配�?|
| skills.py | `/api/skills` | 技能管�?|
| memory.py | `/api/memory` | 记忆数据管理 |
| uploads.py | `/api/threads/{id}/uploads` | 文件上传 |
| artifacts.py | `/api/threads/{id}/artifacts` | 工件服务 |

### 3. Lead Agent 架构

```
┌─────────────────────────────────────────────────────────────────────────�?�?                          make_lead_agent(config)                        �?└────────────────────────────────────┬────────────────────────────────────�?                                     �?                                     �?┌─────────────────────────────────────────────────────────────────────────�?�?                           Middleware Chain                              �?�? ┌──────────────────────────────────────────────────────────────────�?  �?�? �?1. ThreadDataMiddleware  - Initialize workspace/uploads/outputs  �?  �?�? �?2. UploadsMiddleware     - Process uploaded files               �?  �?�? �?3. SandboxMiddleware     - Acquire sandbox environment          �?  �?�? �?4. DanglingToolCallMiddleware - Fix tool call responses         �?  �?�? �?5. SummarizationMiddleware - Context reduction (optional)       �?  �?�? �?6. TodoListMiddleware    - Task tracking (plan mode)            �?  �?�? �?7. TitleMiddleware       - Auto-generate titles                 �?  �?�? �?8. MemoryMiddleware      - Async memory update                  �?  �?�? �?9. ViewImageMiddleware   - Vision model support                 �?  �?�? �?10. SubagentLimitMiddleware - Limit concurrent subagents        �?  �?�? �?11. ClarificationMiddleware - Handle clarifications (last)      �?  �?�? └──────────────────────────────────────────────────────────────────�?  �?└────────────────────────────────────┬────────────────────────────────────�?                                     �?                                     �?┌─────────────────────────────────────────────────────────────────────────�?�?                             Agent Core                                  �?�? ┌──────────────────�? ┌──────────────────�? ┌──────────────────────�?  �?�? �?     Model       �? �?     Tools       �? �?   System Prompt     �?  �?�? �? (from factory)  �? �? (configured +   �? �? (with skills)       �?  �?�? �?                 �? �?  MCP + builtin) �? �?                     �?  �?�? └──────────────────�? └──────────────────�? └──────────────────────�?  �?└─────────────────────────────────────────────────────────────────────────�?```

### 4. 线程状�?(ThreadState)

扩展 LangGraph �?`AgentState`，添�?magicflow 特有字段�?
```python
class ThreadState(AgentState):
    messages: list[BaseMessage]      # 核心状�?    sandbox: dict                    # 沙箱环境信息
    artifacts: list[str]             # 生成的文件路�?    thread_data: dict                # {workspace, uploads, outputs} 路径
    title: str | None                # 自动生成的对话标�?    todos: list[dict]                # 任务跟踪（计划模式）
    uploaded_files: list             # 上传的文�?    viewed_images: dict              # 视觉模型图像数据
```

### 5. 沙箱系统

```
┌─────────────────────────────────────────────────────────────────────────�?�?                          Sandbox Architecture                           �?└─────────────────────────────────────────────────────────────────────────�?
                      ┌─────────────────────────�?                      �?   SandboxProvider      �?(Abstract)
                      �? - acquire()            �?                      �? - get()                �?                      �? - release()            �?                      └────────────┬────────────�?                                   �?              ┌────────────────────┼────────────────────�?              �?                                        �?              �?                                        �?┌─────────────────────────�?             ┌─────────────────────────�?�? LocalSandboxProvider   �?             �? AioSandboxProvider     �?�? (src/sandbox/local.py) �?             �? (src/community/)       �?�?                        �?             �?                        �?�? - Singleton instance   �?             �? - Docker-based         �?�? - Direct execution     �?             �? - Isolated containers  �?�? - Development use      �?             �? - Production use       �?└─────────────────────────�?             └─────────────────────────�?
                      ┌─────────────────────────�?                      �?       Sandbox          �?(Abstract)
                      �? - execute_command()    �?                      �? - read_file()          �?                      �? - write_file()         �?                      �? - list_dir()           �?                      └─────────────────────────�?```

**虚拟路径映射**:

| 虚拟路径 | 物理路径 |
|-------------|---------------|
| `/mnt/user-data/workspace` | `backend/.magic-flow/threads/{thread_id}/user-data/workspace` |
| `/mnt/user-data/uploads` | `backend/.magic-flow/threads/{thread_id}/user-data/uploads` |
| `/mnt/user-data/outputs` | `backend/.magic-flow/threads/{thread_id}/user-data/outputs` |
| `/mnt/skills` | `magic-flow/skills/` |

### 6. 工具系统

```
┌─────────────────────────────────────────────────────────────────────────�?�?                           Tool Sources                                  �?└─────────────────────────────────────────────────────────────────────────�?
┌─────────────────────�? ┌─────────────────────�? ┌─────────────────────�?�?  Built-in Tools    �? �? Configured Tools   �? �?    MCP Tools       �?�? (src/tools/)       �? �? (config.yaml)      �? �? (extensions.json)  �?├─────────────────────�? ├─────────────────────�? ├─────────────────────�?�?- present_file      �? �?- web_search        �? �?- github            �?�?- ask_clarification �? �?- web_fetch         �? �?- filesystem        �?�?- view_image        �? �?- bash              �? �?- postgres          �?�?- task (subagent)   �? �?- read_file         �? �?- brave-search      �?�?                    �? �?- write_file        �? �?                    �?�?                    �? �?- str_replace       �? �?                    �?└─────────────────────�? └─────────────────────�? └─────────────────────�?```

**沙箱工具**:
- `bash` - 执行命令
- `ls` - 目录列表
- `read_file` - 读取文件
- `write_file` - 写入文件
- `str_replace` - 字符串替�?
**内置工具**:
- `present_file` - 展示文件给用�?- `ask_clarification` - 请求澄清
- `view_image` - 查看图像
- `task` - �?Agent 委派

**社区工具**:
- `web_search` (Tavily) - 网页搜索
- `web_fetch` (Jina AI) - 网页获取
- `firecrawl` - 网页抓取
- `image_search` (DuckDuckGo) - 图片搜索

### 7. �?Agent 系统

**内置 Agent**:
- `general-purpose` - 全工具集
- `bash` - 命令行专�?
**执行流程**:
```
task() tool �?SubagentExecutor �?background thread �?poll 5s �?SSE events �?result
```

**并发限制**:
- 最大并�? 3 个子 Agent
- 超时: 15 分钟

### 8. 记忆系统

LLM 驱动的持久化上下文保持：

- **自动提取**: 分析对话获取用户上下文、事实和偏好
- **结构化存�?*: 用户上下文、历史、置信度评分的事�?- **防抖更新**: 批处理更新以最小化 LLM 调用
- **系统提示注入**: 将顶级事�?+ 上下文注�?Agent 提示

### 9. MCP 集成

Model Context Protocol 支持�?
- **传输类型**: stdio, SSE, HTTP
- **OAuth 支持**: client_credentials, refresh_token
- **自动发现**: 运行时自动发现和集成工具

## 数据�?
### 请求处理流程

```
1. 用户请求 �?Nginx (2026)
2. Nginx 路由:
   - /api/langgraph/* �?LangGraph Server (2024)
   - /api/* �?Gateway API (8001)
3. LangGraph Server:
   - 加载 ThreadState
   - 执行中间件链
   - 调用 LLM
   - 执行工具
   - 保存状�?   - 流式返回 SSE
4. Gateway API:
   - 处理 REST 请求
   - 返回 JSON 响应
```

### Agent 执行流程

```
1. 接收用户消息
2. ThreadDataMiddleware 创建线程目录
3. UploadsMiddleware 处理上传文件
4. SandboxMiddleware 获取沙箱
5. MemoryMiddleware 注入记忆
6. ViewImageMiddleware 处理图像
7. 调用 LLM
8. 执行工具调用
   - 沙箱工具: 在隔离环境执�?   - MCP 工具: 调用外部服务
   - �?Agent: 后台执行
9. ClarificationMiddleware 处理澄清请求
10. 返回响应
```

## 配置系统

### 主配�?(config.yaml)

**位置**: 项目根目�?
**配置�?*:
- `models` - LLM 模型配置
- `tools` - 工具配置
- `tool_groups` - 工具分组
- `sandbox` - 沙箱配置
- `skills` - 技能配�?- `memory` - 记忆系统配置
- `title` - 标题生成配置

### 扩展配置 (extensions_config.json)

**位置**: 项目根目�?
**配置�?*:
- `mcpServers` - MCP 服务器配�?- `skills` - 技能状�?
## 技术栈详情

### 核心依赖

| �?| 版本 | 用�?|
|----|------|------|
| langgraph | >=1.0.6 | Agent 框架 |
| langchain | >=1.2.3 | LLM 集成 |
| fastapi | >=0.115.0 | API 框架 |
| uvicorn | >=0.34.0 | ASGI 服务�?|
| pydantic | >=2.12.5 | 数据验证 |
| tiktoken | >=0.8.0 | Token 计数 |

### 开发依�?
| �?| 版本 | 用�?|
|----|------|------|
| pytest | >=8.0.0 | 测试框架 |
| ruff | >=0.14.11 | 代码质量 |

## 部署架构

### 开发环�?
```
┌─────────────────────────────────────────�?�?          Development Host              �?�? ┌─────────�?┌─────────�?┌───────────�?�?�? │LangGraph�?�?Gateway �?�?Frontend  �?�?�? �? 2024   �?�? 8001   �?�?  3000    �?�?�? └────┬────�?└────┬────�?└─────┬─────�?�?�?      └────────────┴────────────�?      �?�?                   �?                   �?�?              ┌────┴────�?              �?�?              �? Nginx  �?              �?�?              �? 2026   �?              �?�?              └────┬────�?              �?�?                   �?                   �?└────────────────────┼────────────────────�?                     �?                  Browser
```

### Docker 环境

```
┌─────────────────────────────────────────�?�?        Docker Compose Network          �?�? ┌─────────�?┌─────────�?┌───────────�?�?�? │LangGraph�?�?Gateway �?�?Frontend  �?�?�? �? 2024   �?�? 8001   �?�?  3000    �?�?�? └────┬────�?└────┬────�?└─────┬─────�?�?�?      └────────────┴────────────�?      �?�?                   �?                   �?�?              ┌────┴────�?              �?�?              �? Nginx  �?              �?�?              �? 2026   �?              �?�?              └────┬────�?              �?�?                   �?                   �?�? ┌─────────────────�?                   �?�? �?                                     �?�? �?                                     �?�?┌──────────────�? ┌──────────────�?    �?�?�?  Sandbox    �? �?Provisioner  �?    �?�?�? (optional)  �? �? (optional)  �?    �?�?└──────────────�? └──────────────�?    �?└─────────────────────────────────────────�?```

## 安全考虑

1. **沙箱隔离**: 代码执行在隔离环境中
2. **路径限制**: 虚拟路径系统限制文件访问
3. **Token 管理**: API keys 通过环境变量注入
4. **CORS 配置**: 通过 Nginx 统一处理
5. **文件上传限制**: 大小和类型检�?
## 性能优化

1. **中间件缓�?*: 避免重复计算
2. **记忆批处�?*: 防抖更新减少 LLM 调用
3. **沙箱复用**: 同一线程复用沙箱实例
4. **SSE 流式**: 实时响应减少等待
5. **连接�?*: HTTP 客户端连接池

## 监控和日�?
- **结构化日�?*: JSON 格式日志
- **性能指标**: 中间件执行时�?- **错误追踪**: 异常捕获和上�?- **Token 使用**: 监控 LLM Token 消�?
