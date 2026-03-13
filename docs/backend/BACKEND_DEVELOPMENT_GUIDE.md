# magicflow 后端开发指�?
## 开发环境准�?
### 前置要求

- **Python**: 3.12+
- **包管理器**: [uv](https://docs.astral.sh/uv/)
- **API Keys**: OpenAI / Anthropic / DeepSeek �?
### 安装 uv

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 项目设置

```bash
# 1. 进入项目根目�?cdmagic-floww

# 2. 复制配置文件
cp config.example.yaml config.yaml

# 3. 编辑配置，添加你�?API keys
# vim config.yaml

# 4. 进入后端目录
cd backend

# 5. 安装依赖
make install
```

## 开发工作流

### 常用命令

```bash
# 安装依赖
make install

# 启动 LangGraph 服务器（端口 2024�?make dev

# 启动 Gateway API（端�?8001�?make gateway

# 运行测试
make test

# 代码检�?make lint

# 代码格式�?make format
```

### 完整应用开�?
在项目根目录�?
```bash
# 检查环�?make check

# 安装所有依赖（前端 + 后端�?make install

# 启动完整应用
make dev
```

访问：http://localhost:2026

## 项目结构详解

### 源代码组�?
```
src/
├── agents/                 # LangGraph Agent 系统
�?  ├── lead_agent/         # �?Agent 实现
�?  �?  ├── agent.py        # Agent 工厂函数
�?  �?  └── prompt.py       # 系统提示模板
�?  ├── middlewares/        # 中间件链
�?  �?  ├── thread_data_middleware.py
�?  �?  ├── sandbox_middleware.py
�?  �?  ├── memory_middleware.py
�?  �?  └── ...
�?  ├── memory/             # 记忆系统
�?  �?  ├── queue.py        # 记忆队列
�?  �?  ├── updater.py      # 记忆更新�?�?  �?  └── prompt.py       # 记忆提取提示
�?  └── thread_state.py     # 线程状态定�?�?├── gateway/                # FastAPI Gateway
�?  ├── app.py              # FastAPI 应用
�?  └── routers/            # API 路由
�?      ├── models.py       # 模型 API
�?      ├── skills.py       # 技�?API
�?      ├── memory.py       # 记忆 API
�?      └── ...
�?├── sandbox/                # 沙箱执行系统
�?  ├── local/              # 本地沙箱实现
�?  ├── sandbox.py          # 抽象接口
�?  ├── sandbox_provider.py # 提供者接�?�?  ├── tools.py            # 沙箱工具
�?  └── middleware.py       # 沙箱中间�?�?├── subagents/              # �?Agent 系统
�?  ├── builtins/           # 内置�?Agent
�?  ├── executor.py         # 执行引擎
�?  └── registry.py         # 注册�?�?├── tools/                  # 工具系统
�?  └── builtins/           # 内置工具
�?├── mcp/                    # MCP 集成
�?  ├── client.py           # MCP 客户�?�?  ├── tools.py            # MCP 工具适配
�?  └── oauth.py            # OAuth 支持
�?├── skills/                 # 技能系�?�?  ├── loader.py           # 技能加载器
�?  └── parser.py           # 技能解析器
�?├── models/                 # 模型工厂
�?  └── factory.py          # 模型创建
�?├── config/                 # 配置系统
�?  ├── app_config.py       # 应用配置
�?  ├── model_config.py     # 模型配置
�?  └── ...
�?└── community/              # 社区工具
    ├── aio_sandbox/        # Docker 沙箱
    ├── tavily/             # 搜索工具
    ├── jina_ai/            # 网页获取
    └── ...
```

## 核心开发模�?
### 1. 创建中间�?
```python
# src/agents/middlewares/my_middleware.py
from langchain_core.runnables import RunnableConfig
from src.agents.thread_state import ThreadState

class MyMiddleware:
    """自定义中间件示例"""

    def before_model(
        self,
        state: ThreadState,
        config: RunnableConfig
    ) -> ThreadState:
        """在调�?LLM 之前执行"""
        # 修改状�?        state["my_field"] = "value"
        return state

    def after_model(
        self,
        state: ThreadState,
        config: RunnableConfig
    ) -> ThreadState:
        """在调�?LLM 之后执行"""
        return state
```

### 2. 创建工具

```python
# src/tools/my_tool.py
from langchain_core.tools import tool
from src.agents.thread_state import ThreadState

@tool
def my_tool(
    arg1: str,
    state: ThreadState  # 注入状�?) -> str:
    """工具描述，会�?LLM 看到"""
    # 工具逻辑
    result = f"Processed: {arg1}"
    return result
```

### 3. 创建 Gateway API 端点

```python
# src/gateway/routers/my_router.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/my-feature")

class MyRequest(BaseModel):
    data: str

class MyResponse(BaseModel):
    result: str

@router.post("/process", response_model=MyResponse)
async def process_data(request: MyRequest):
    """处理数据"""
    result = await do_something(request.data)
    return MyResponse(result=result)
```

### 4. 添加模型支持

```python
# src/models/factory.py
from langchain_openai import ChatOpenAI

def create_chat_model(config: ModelConfig):
    """创建聊天模型"""
    if config.provider == "openai":
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
        )
    # 添加其他提供�?..
```

## 调试技�?
### 1. 日志调试

```python
import logging

logger = logging.getLogger(__name__)

# 在代码中添加日志
logger.debug("Debug message: %s", variable)
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 2. LangSmith 追踪

```bash
# 设置环境变量
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-key
export LANGCHAIN_PROJECT=magic-flow
```

### 3. 断点调试

```python
# 在代码中插入断点
import pdb; pdb.set_trace()

# 或使�?VS Code 调试配置
```

**VS Code 配置** (`.vscode/launch.json`):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: LangGraph",
      "type": "debugpy",
      "request": "launch",
      "module": "langgraph",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

### 4. 检查线程状�?
```python
# 在中间件中打印状�?print("Current state:", state)
print("Messages:", state.get("messages", []))
print("Sandbox:", state.get("sandbox", {}))
```

## 测试

### 运行测试

```bash
# 运行所有测�?make test

# 运行特定测试
uv run pytest tests/test_specific.py -v

# 运行带覆盖率
uv run pytest --cov=src tests/
```

### 编写测试

```python
# tests/test_my_feature.py
import pytest
from src.my_module import my_function

def test_my_function():
    """测试我的功能"""
    result = my_function("input")
    assert result == "expected_output"

@pytest.mark.asyncio
async def test_async_function():
    """测试异步功能"""
    result = await my_async_function()
    assert result is not None
```

## 代码质量

### 代码风格

项目使用 **ruff** 进行代码检查和格式化：

```bash
# 检查代�?make lint

# 自动修复
make format
```

### 类型注解

```python
from typing import Optional, List, Dict, Any

def process_data(
    input_data: str,
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """处理数据并返回结果列�?""
    results: List[str] = []
    # 处理逻辑
    return results
```

## 配置开�?
### 本地配置

```yaml
# config.yaml (项目根目�?
models:
  - name: gpt-4o
    display_name: GPT-4o
    use: langchain_openai:ChatOpenAI
    model: gpt-4o
    api_key: $OPENAI_API_KEY
    supports_vision: true

tools:
  - name: web_search
    use: src.community.tavily.tools:web_search_tool

sandbox:
  use: src.sandbox.local:LocalSandboxProvider
```

### 环境变量

```bash
# .env (项目根目�?
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

## 常见问题

### Q: 配置文件找不到？

A: 确保 `config.yaml` 在项目根目录，而不�?backend 目录�?
```bash
# 检查配置位�?python -c "from src.config import get_app_config; print(get_app_config())"
```

### Q: 依赖安装失败�?
A: 确保使用 uv 安装�?
```bash
# 清除缓存
uv cache clean

# 重新安装
make install
```

### Q: 端口被占用？

A: 查找并关闭占用端口的进程�?
```bash
# Windows
netstat -ano | findstr :2024
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :2024
kill -9 <PID>
```

### Q: 沙箱执行失败�?
A: 检查沙箱配置：

```yaml
# 使用本地沙箱（开发）
sandbox:
  use: src.sandbox.local:LocalSandboxProvider

# 或使�?Docker 沙箱
sandbox:
  use: src.community.aio_sandbox:AioSandboxProvider
```

## 性能优化

### 1. 异步操作

```python
import asyncio

# 并行执行多个任务
results = await asyncio.gather(
    task1(),
    task2(),
    task3(),
)
```

### 2. 缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(key: str) -> str:
    """缓存 expensive 操作的结�?""
    return compute_result(key)
```

### 3. 连接�?
```python
import httpx

# 使用连接�?async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

## 部署准备

### Docker 构建

```bash
# 构建镜像
docker build -t magic-flow-backend .

# 运行容器
docker run -p 2024:2024 -p 8001:8001 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  magic-flow-backend
```

### 生产环境检查清�?
- [ ] 配置生产环境 API keys
- [ ] 启用 Docker 沙箱（更安全�?- [ ] 配置日志级别�?INFO
- [ ] 设置监控和告�?- [ ] 配置备份策略

## 相关资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangChain 文档](https://python.langchain.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [uv 文档](https://docs.astral.sh/uv/)

