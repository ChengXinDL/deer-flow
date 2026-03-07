# DeerFlow 后端核心组件详解

## 组件概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DeerFlow Backend                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    Agent     │  │   Sandbox    │  │   Memory     │  │    MCP       │ │
│  │   System     │  │   System     │  │   System     │  │  Integration │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Subagent    │  │    Skill     │  │    Tool      │  │   Gateway    │ │
│  │   System     │  │   System     │  │   System     │  │     API      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Agent 系统

### Lead Agent

**位置**: `src/agents/lead_agent/agent.py`

**核心函数**:

```python
def make_lead_agent(config: RunnableConfig) -> CompiledGraph:
    """创建主 Agent"""
    # 1. 加载模型
    model = create_chat_model(config)
    
    # 2. 加载工具
    tools = get_available_tools(config)
    
    # 3. 创建 Agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        state_schema=ThreadState,
        prompt=apply_prompt_template,
    )
    
    # 4. 添加中间件
    agent = apply_middlewares(agent, config)
    
    return agent
```

### 中间件链

中间件按严格顺序执行：

| 顺序 | 中间件 | 阶段 | 功能 |
|------|--------|------|------|
| 1 | ThreadDataMiddleware | before_model | 创建线程目录 |
| 2 | UploadsMiddleware | before_model | 处理上传文件 |
| 3 | SandboxMiddleware | before_model | 获取沙箱环境 |
| 4 | DanglingToolCallMiddleware | after_model | 修复工具调用响应 |
| 5 | SummarizationMiddleware | before_model | 上下文摘要 |
| 6 | TodoListMiddleware | before_model | 任务跟踪 |
| 7 | TitleMiddleware | after_model | 自动生成标题 |
| 8 | MemoryMiddleware | before_model | 记忆注入 |
| 9 | ViewImageMiddleware | before_model | 图像处理 |
| 10 | SubagentLimitMiddleware | after_model | 限制并发子 Agent |
| 11 | ClarificationMiddleware | after_model | 处理澄清请求 |

**中间件接口**:

```python
class Middleware:
    def before_model(
        self,
        state: ThreadState,
        config: RunnableConfig
    ) -> ThreadState:
        """在调用 LLM 之前执行"""
        return state
    
    def after_model(
        self,
        state: ThreadState,
        config: RunnableConfig
    ) -> ThreadState:
        """在调用 LLM 之后执行"""
        return state
```

### ThreadState

**位置**: `src/agents/thread_state.py`

```python
class ThreadState(AgentState):
    """扩展的线程状态"""
    
    # 核心消息
    messages: Annotated[list[BaseMessage], add_messages]
    
    # 沙箱信息
    sandbox: dict = {}  # {sandbox_id, type, provider}
    
    # 文件和工件
    artifacts: Annotated[list[str], merge_artifacts]  # 生成的文件
    uploaded_files: list = []  # 上传的文件
    viewed_images: Annotated[dict, merge_viewed_images]  # 查看的图像
    
    # 线程数据
    thread_data: dict = {}  # {workspace, uploads, outputs} 路径
    
    # 元数据
    title: str | None = None  # 对话标题
    todos: list = []  # 待办事项
```

---

## 2. 沙箱系统

### 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Sandbox System                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │ SandboxProvider  │◄────────│  Provider Impl   │                     │
│  │  (Abstract)      │         │                  │                     │
│  │  - acquire()     │         │  LocalSandbox    │                     │
│  │  - get()         │         │  AioSandbox      │                     │
│  │  - release()     │         │                  │                     │
│  └────────┬─────────┘         └──────────────────┘                     │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────┐                                                   │
│  │     Sandbox      │                                                   │
│  │  (Abstract)      │                                                   │
│  │  - execute_cmd() │                                                   │
│  │  - read_file()   │                                                   │
│  │  - write_file()  │                                                   │
│  │  - list_dir()    │                                                   │
│  └──────────────────┘                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 虚拟路径系统

| 虚拟路径 | 物理路径 | 说明 |
|----------|----------|------|
| `/mnt/user-data/workspace` | `.deer-flow/threads/{id}/user-data/workspace` | 工作目录 |
| `/mnt/user-data/uploads` | `.deer-flow/threads/{id}/user-data/uploads` | 上传目录 |
| `/mnt/user-data/outputs` | `.deer-flow/threads/{id}/user-data/outputs` | 输出目录 |
| `/mnt/skills` | `deer-flow/skills/` | 技能目录 |

### 沙箱工具

**位置**: `src/sandbox/tools.py`

| 工具 | 功能 | 示例 |
|------|------|------|
| `bash` | 执行命令 | `bash -c "ls -la"` |
| `ls` | 列出目录 | `ls /mnt/user-data/workspace` |
| `read_file` | 读取文件 | `read_file /path/to/file` |
| `write_file` | 写入文件 | `write_file /path/to/file "content"` |
| `str_replace` | 字符串替换 | `str_replace /path/to/file "old" "new"` |

---

## 3. 记忆系统

### 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Memory System                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   Extract    │───▶│    Queue     │───▶│   Updater    │              │
│  │              │    │              │    │              │              │
│  │ 从对话提取   │    │ 批量处理     │    │ LLM 分析     │              │
│  │ 上下文和事实 │    │ 防抖         │    │ 更新记忆     │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                                            │                  │
│         │                                            ▼                  │
│         │                                   ┌──────────────┐            │
│         │                                   │   Storage    │            │
│         │                                   │  (JSON file) │            │
│         │                                   └──────────────┘            │
│         │                                            │                  │
│         └────────────────────────────────────────────┘                  │
│                                                      ▼                  │
│                                            ┌──────────────┐            │
│                                            │   Inject     │            │
│                                            │  到系统提示  │            │
│                                            └──────────────┘            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 记忆结构

```python
{
  "context": {
    "work": "软件工程师",
    "personal": "住在北京",
    "top_of_mind": "正在学习 LangGraph"
  },
  "facts": [
    {
      "content": "更喜欢 Python 而不是 JavaScript",
      "confidence": 0.95,
      "category": "preference",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "history": [
    {
      "date": "2024-01-15",
      "summary": "讨论了项目架构"
    }
  ]
}
```

### 相似度计算

使用 TF-IDF + 余弦相似度：

```python
final_score = (similarity × 0.6) + (confidence × 0.4)
```

- **相似度 (60%)**: 与当前对话的相关性
- **置信度 (40%)**: LLM 分配的置信度

---

## 4. MCP 集成

### 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MCP Integration                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   Config     │───▶│   Client     │───▶│    Tools     │              │
│  │              │    │              │    │              │              │
│  │ extensions   │    │ 连接服务器   │    │ 转换为       │              │
│  │ _config.json │    │ 管理会话     │    │ LangChain    │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                                            │                  │
│         │                                            ▼                  │
│         │                                   ┌──────────────┐            │
│         │                                   │   Agent      │            │
│         │                                   │  使用工具    │            │
│         │                                   └──────────────┘            │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────┐                                                       │
│  │   OAuth      │                                                       │
│  │              │                                                       │
│  │ Token 管理   │                                                       │
│  │ 自动刷新     │                                                       │
│  └──────────────┘                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 支持的传输类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `stdio` | 标准输入输出 | 本地命令 |
| `sse` | Server-Sent Events | HTTP 流 |
| `http` | HTTP 请求 | REST API |

### OAuth 支持

```json
{
  "mcpServers": {
    "secure-api": {
      "type": "http",
      "oauth": {
        "enabled": true,
        "token_url": "https://auth.example.com/token",
        "grant_type": "client_credentials",
        "client_id": "$CLIENT_ID",
        "client_secret": "$CLIENT_SECRET",
        "scope": "api.read",
        "refresh_skew_seconds": 60
      }
    }
  }
}
```

---

## 5. 子 Agent 系统

### 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Subagent System                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐                                                       │
│  │  Lead Agent  │                                                       │
│  │              │                                                       │
│  │ 调用 task()  │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   Executor   │───▶│   Thread     │───▶│  Subagent    │              │
│  │              │    │   Pool       │    │  Instance    │              │
│  │ 调度执行     │    │  (3 workers) │    │              │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│         │                                            │                  │
│         │                                            │                  │
│         │                    ┌───────────────────────┘                  │
│         │                    │                                          │
│         │                    ▼                                          │
│         │         ┌──────────────┐                                     │
│         │         │   Status     │                                     │
│         │         │   Poll       │                                     │
│         │         │  (5s interval)│                                    │
│         │         └──────────────┘                                     │
│         │                    │                                          │
│         └────────────────────┘                                          │
│                              ▼                                          │
│                   ┌──────────────┐                                     │
│                   │   Result     │                                     │
│                   │   Return     │                                     │
│                   └──────────────┘                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 内置子 Agent

| Agent | 描述 | 工具 |
|-------|------|------|
| `general-purpose` | 通用目的 | 除 task 外的所有工具 |
| `bash` | 命令行专家 | bash, ls, read_file |

### 并发限制

- **最大并发**: 3 个子 Agent
- **超时**: 15 分钟
- **轮询间隔**: 5 秒

---

## 6. 技能系统

### 技能结构

```
skills/
├── public/              # 公共技能
│   ├── research/
│   │   └── SKILL.md
│   ├── report-generation/
│   │   └── SKILL.md
│   └── slide-creation/
│       └── SKILL.md
└── custom/              # 自定义技能
    └── my-skill/
        └── SKILL.md
```

### SKILL.md 格式

```markdown
# Skill Name

## Description
技能描述

## When to Use
使用场景

## Workflow
1. 步骤 1
2. 步骤 2

## Examples
示例代码

## Best Practices
最佳实践
```

### 技能加载

```python
# src/skills/loader.py
def load_skills(skills_path: str) -> list[Skill]:
    """递归加载所有技能"""
    skills = []
    for skill_file in Path(skills_path).rglob("SKILL.md"):
        skill = parse_skill(skill_file)
        skills.append(skill)
    return skills
```

---

## 7. 工具系统

### 工具分类

| 类别 | 工具 | 位置 |
|------|------|------|
| **沙箱** | bash, ls, read_file, write_file, str_replace | `src/sandbox/tools.py` |
| **内置** | present_file, ask_clarification, view_image, task | `src/tools/builtins/` |
| **社区** | web_search, web_fetch, image_search | `src/community/` |
| **MCP** | 动态加载 | `src/mcp/tools.py` |

### 工具定义

```python
from langchain_core.tools import tool
from src.agents.thread_state import ThreadState

@tool
def my_tool(
    arg1: str,
    arg2: int,
    state: ThreadState  # 自动注入
) -> str:
    """工具描述
    
    Args:
        arg1: 参数 1 说明
        arg2: 参数 2 说明
    
    Returns:
        结果说明
    """
    # 工具逻辑
    result = process(arg1, arg2)
    
    # 更新状态（可选）
    state["artifacts"].append(result)
    
    return result
```

---

## 8. Gateway API

### 路由结构

```
src/gateway/
├── app.py              # FastAPI 应用
├── config.py           # 配置
├── path_utils.py       # 路径工具
└── routers/
    ├── models.py       # /api/models
    ├── mcp.py          # /api/mcp
    ├── skills.py       # /api/skills
    ├── memory.py       # /api/memory
    ├── uploads.py      # /api/threads/{id}/uploads
    └── artifacts.py    # /api/threads/{id}/artifacts
```

### 路由示例

```python
# src/gateway/routers/models.py
from fastapi import APIRouter
from src.config import get_app_config

router = APIRouter(prefix="/models")

@router.get("/")
async def list_models():
    """列出所有可用模型"""
    config = get_app_config()
    return {
        "models": [
            {
                "name": m.name,
                "display_name": m.display_name,
                "supports_vision": m.supports_vision,
            }
            for m in config.models
        ]
    }

@router.get("/{model_name}")
async def get_model(model_name: str):
    """获取模型详情"""
    config = get_app_config()
    model = next((m for m in config.models if m.name == model_name), None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model
```

---

## 9. 配置系统

### 配置类层次

```
AppConfig
├── models: list[ModelConfig]
├── tools: list[ToolConfig]
├── tool_groups: list[ToolGroupConfig]
├── sandbox: SandboxConfig
├── skills: SkillsConfig
├── memory: MemoryConfig
├── title: TitleConfig
└── summarization: SummarizationConfig
```

### 配置加载

```python
# src/config/app_config.py
class AppConfig(BaseModel):
    """应用配置"""
    
    models: list[ModelConfig]
    tools: list[ToolConfig] = []
    tool_groups: list[ToolGroupConfig] = []
    sandbox: SandboxConfig
    skills: SkillsConfig = SkillsConfig()
    memory: MemoryConfig = MemoryConfig()
    title: TitleConfig = TitleConfig()
    summarization: SummarizationConfig = SummarizationConfig()
    
    @classmethod
    def load(cls, path: str | None = None) -> "AppConfig":
        """加载配置"""
        path = path or cls.resolve_config_path()
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

---

## 组件交互图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Component Interactions                              │
└─────────────────────────────────────────────────────────────────────────┘

    User Request
        │
        ▼
┌───────────────┐
│     Nginx     │
└───────┬───────┘
        │
    ┌───┴───┐
    │       │
    ▼       ▼
┌───────┐ ┌───────┐
│LangGraph│ │Gateway│
│ Server │ │  API  │
└───┬───┘ └───────┘
    │
    ▼
┌───────────────┐
│  Middleware   │
│    Chain      │
└───────┬───────┘
    │
    ▼
┌───────────────┐
│  Lead Agent   │
└───────┬───────┘
    │
    ├───▶ Model ──▶ LLM API
    │
    ├───▶ Tools ──┬──▶ Sandbox ──▶ File System
    │             ├──▶ MCP ──────▶ External API
    │             └──▶ Subagent ─▶ Thread Pool
    │
    ├───▶ Memory ───▶ Storage
    │
    └───▶ Skills ───▶ Skills Dir
```

---

## 开发指南

### 添加新中间件

1. 创建文件 `src/agents/middlewares/my_middleware.py`
2. 实现中间件类
3. 在 `agent.py` 中注册

### 添加新工具

1. 在 `src/tools/` 或 `src/community/` 创建工具
2. 使用 `@tool` 装饰器
3. 在 `config.yaml` 中配置

### 添加新 API 端点

1. 在 `src/gateway/routers/` 创建路由文件
2. 在 `app.py` 中注册路由

---

## 相关文档

- [后端架构](./BACKEND_ARCHITECTURE.md)
- [后端开发指南](./BACKEND_DEVELOPMENT_GUIDE.md)
- [API 参考](./BACKEND_API_REFERENCE.md)
- [配置指南](./BACKEND_CONFIGURATION.md)
