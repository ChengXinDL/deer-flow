# 多 Agent 实例配置重构方案

基于当前项目架构，设计一个支持多 agent 实例配置的重构方案。

## 1. 新的 Agent 配置模型

```python
# backend/src/config/agent_config.py

from typing import Optional
from pydantic import BaseModel


class AgentToolConfig(BaseModel):
    """Agent 工具配置"""
    name: str  # 工具名称
    enabled: bool = True
    config: dict = {}  # 工具特定配置


class AgentMcpConfig(BaseModel):
    """Agent MCP 服务器配置"""
    server_name: str
    enabled: bool = True


class AgentSkillConfig(BaseModel):
    """Agent 技能配置"""
    name: str
    enabled: bool = True


class AgentMemoryConfig(BaseModel):
    """Agent 记忆配置"""
    enabled: bool = True
    summary_enabled: bool = True


class AgentConfig(BaseModel):
    """单个 Agent 实例配置"""
    id: str  # agent_id，如 "research-agent", "sql-agent"
    name: str
    description: str = ""
    
    # 模型配置
    model_name: str  # 使用的模型
    thinking_enabled: bool = True
    reasoning_effort: str | None = None
    
    # 工具配置
    tools: list[AgentToolConfig] = []
    tool_groups: list[str] = []  # 工具组
    include_builtin_tools: bool = True
    include_mcp_tools: bool = True
    mcp_servers: list[AgentMcpConfig] = []
    
    # 技能配置
    skills: list[AgentSkillConfig] = []
    
    # 记忆配置
    memory: AgentMemoryConfig = AgentMemoryConfig()
    
    # Middleware 配置
    summarization_enabled: bool = True
    plan_mode_enabled: bool = False
    subagent_enabled: bool = False
    max_concurrent_subagents: int = 3
    
    # Prompt 覆盖
    system_prompt: str | None = None


class AgentsAppConfig(BaseModel):
    """多 Agent 应用配置"""
    agents: list[AgentConfig] = []
    default_agent_id: str | None = None  # 默认 Agent
```

## 2. Agent 工厂类

```python
# backend/src/agents/factory.py

from typing import Optional, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool

from src.config.agent_config import AgentConfig, AgentsAppConfig, AgentToolConfig
from src.config.app_config import get_app_config
from src.models import create_chat_model
from src.tools import get_available_tools
from src.mcp.cache import get_cached_mcp_tools
from src.skills import load_skills
from src.agents.thread_state import ThreadState
from src.agents.middlewares.thread_data_middleware import ThreadDataMiddleware
from src.agents.middlewares.memory_middleware import MemoryMiddleware


def create_summarization_middleware():
    """创建摘要中间件"""
    from src.agents.lead_agent.agent import _create_summarization_middleware
    return _create_summarization_middleware()


def create_todo_list_middleware():
    """创建待办事项中间件"""
    from src.agents.lead_agent.agent import _create_todo_list_middleware
    return _create_todo_list_middleware(is_plan_mode=True)


class AgentFactory:
    """Agent 工厂类 - 支持创建不同配置的 Agent 实例"""
    
    def __init__(self, agents_config: AgentsAppConfig):
        self.agents_config = agents_config
        self._agent_cache: dict[str, Any] = {}
    
    def get_agent_config(self, agent_id: str) -> AgentConfig | None:
        """获取 Agent 配置"""
        for agent in self.agents_config.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def create_agent(
        self,
        agent_id: str,
        runtime_config: Optional[RunnableConfig] = None,
    ) -> "Agent":
        """创建 Agent 实例"""
        config = self.get_agent_config(agent_id)
        if not config:
            raise ValueError(f"Agent '{agent_id}' not found in configuration")
        
        return self._build_agent(config, runtime_config or {})
    
    def _build_agent(self, config: AgentConfig, runtime_config: dict) -> "Agent":
        """构建 Agent"""
        # 1. 获取工具
        tools = self._load_tools(config)
        
        # 2. 创建模型
        model = create_chat_model(
            name=config.model_name,
            thinking_enabled=config.thinking_enabled,
            reasoning_effort=config.reasoning_effort,
        )
        
        # 3. 构建 Middleware
        middlewares = self._build_middlewares(config, runtime_config)
        
        # 4. 创建 Agent
        from langchain.agents import create_agent
        
        prompt = config.system_prompt or self._get_default_prompt(config)
        
        return create_agent(
            model=model,
            tools=tools,
            middleware=middlewares,
            system_prompt=prompt,
            state_schema=ThreadState,
        )
    
    def _load_tools(self, config: AgentConfig) -> list[BaseTool]:
        """加载 Agent 特定的工具"""
        tools = []
        
        # 内置工具
        if config.include_builtin_tools:
            from src.tools.tools import BUILTIN_TOOLS
            tools.extend(BUILTIN_TOOLS)
        
        # MCP 工具 - 只加载指定的服务器
        if config.include_mcp_tools:
            mcp_tools = get_cached_mcp_tools()
            enabled_servers = {s.server_name for s in config.mcp_servers if s.enabled}
            # 过滤只包含启用的 MCP 服务器
            filtered_mcp = [
                t for t in mcp_tools 
                if getattr(t, "server_name", None) in enabled_servers
            ]
            tools.extend(filtered_mcp)
        
        # 按配置过滤工具
        if config.tools:
            enabled_tools = {t.name for t in config.tools if t.enabled}
            tools = [t for t in tools if t.name in enabled_tools]
        
        return tools
    
    def _build_middlewares(self, config: AgentConfig, runtime_config: dict) -> list:
        """构建 Agent 特定的 Middleware"""
        middlewares = []
        
        # ThreadDataMiddleware
        middlewares.append(ThreadDataMiddleware())
        
        # 根据配置添加 Middleware
        if config.summarization_enabled:
            summarization_mw = create_summarization_middleware()
            if summarization_mw:
                middlewares.append(summarization_mw)
        
        if config.plan_mode_enabled:
            todo_list_mw = create_todo_list_middleware()
            if todo_list_mw:
                middlewares.append(todo_list_mw)
        
        if config.memory.enabled:
            middlewares.append(MemoryMiddleware())
        
        return middlewares
    
    def _get_default_prompt(self, config: AgentConfig) -> str:
        """获取默认 Prompt"""
        # 可以根据 agent 类型返回不同的默认 prompt
        return "You are a helpful AI assistant."


# 全局工厂实例
_agent_factory: Optional[AgentFactory] = None


def get_agent_factory() -> AgentFactory:
    """获取全局 Agent 工厂"""
    global _agent_factory
    if _agent_factory is None:
        # 从配置加载
        from src.config.agent_config import AgentsAppConfig
        # 暂时使用空配置，后续从文件加载
        _agent_factory = AgentFactory(AgentsAppConfig(agents=[]))
    return _agent_factory
```

## 3. 配置文件扩展

```yaml
# backend/config.yaml

# 扩展 agents 配置
agents:
  - id: lead-agent
    name: 主 Agent
    description: 默认的智能助手
    model_name: kimi-k2.5
    thinking_enabled: true
    tools:
      - web_search
      - read_file
      - write_file
      - bash
    mcp_servers:
      - server_name: filesystem
        enabled: true
    skills:
      - query-writing
      - frontend-design
    memory:
      enabled: true
      summary_enabled: true

  - id: sql-agent
    name: SQL Agent
    description: 专门用于数据库查询的 Agent
    model_name: kimi-k2.5
    thinking_enabled: false
    tools:
      - query_db
      - read_file
    mcp_servers:
      - server_name: mysql-tools
        enabled: true
    skills:
      - query-writing

  - id: research-agent
    name: 研究 Agent
    description: 专门用于网络研究和信息收集
    model_name: deepseek-v3
    thinking_enabled: true
    tool_groups:
      - web
    mcp_servers:
      - server_name: brave-search
        enabled: true

# 默认 Agent
default_agent_id: lead-agent
```

## 4. API 层面的支持

```python
# backend/src/gateway/routers/agents.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/agents", tags=["agents"])


class CreateAgentRequest(BaseModel):
    agent_id: str
    # 可选的运行时覆盖配置
    model_name: str | None = None
    thinking_enabled: bool | None = None


class InvokeAgentRequest(BaseModel):
    agent_id: str
    messages: list[dict]
    config: dict = {}  # 运行时配置


@router.get("/")
async def list_agents():
    """列出所有可用 Agent"""
    factory = get_agent_factory()
    return [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "model_name": a.model_name,
        }
        for a in factory.agents_config.agents
    ]


@router.post("/invoke")
async def invoke_agent(request: InvokeAgentRequest):
    """调用指定 Agent"""
    factory = get_agent_factory()
    agent = factory.create_agent(request.agent_id, request.config)
    
    result = await agent.ainvoke(
        {"messages": request.messages},
        config=request.config
    )
    return result
```

## 5. 使用示例

```python
# 前端请求
POST /api/agents/invoke
{
    "agent_id": "sql-agent",
    "messages": [{"role": "user", "content": "查询一层有哪些房间"}],
    "config": {
        "configurable": {
            "db_url": "mysql://...",
            "building_id": "B1"
        }
    }
}
```

## 6. 优势

| 特性 | 说明 |
|------|------|
| **隔离性** | 每个 Agent 有独立的工具、MCP、技能配置 |
| **灵活性** | 支持运行时配置覆盖 |
| **可扩展性** | 易于添加新的 Agent 类型 |
| **兼容性** | 保持与现有 lead-agent 的向后兼容 |
