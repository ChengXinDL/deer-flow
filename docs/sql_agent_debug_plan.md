# SQL Agent 调试计划文档

## 1. 问题分析

### 1.1 调用方式不匹配
**位置**: `backend/src/client.py` 第 206-221 行

**问题描述**:
当 `agent_type == "sql"` 时，代码尝试调用 `make_sql_agent(**kwargs)`，但 `make_sql_agent` 函数在 `agent.py` 中定义的签名是:
```python
def make_sql_agent(config: RunnableConfig):
```

它期望接收一个 `RunnableConfig` 对象，而不是分散的 kwargs。

**当前代码**:
```python
if agent_type == "sql":
    from src.agents.sql_agent.agent import make_sql_agent
    
    kwargs: dict[str, Any] = {
        "model": create_chat_model(...),
        "tools": self._get_tools(...),
        "middleware": _build_sql_middlewares(config, model_name=model_name),
        "system_prompt": apply_sql_prompt_template(...),
        "state_schema": ThreadState,
    }
    self._agent = make_sql_agent(**kwargs)  # 错误：参数不匹配
```

**期望的调用方式**:
```python
config = RunnableConfig(
    configurable={
        "db_url": db_url,
        "building_id": building_id,
        "model_name": model_name,
        "thinking_enabled": thinking_enabled,
        "is_plan_mode": is_plan_mode,
    }
)
self._agent = make_sql_agent(config)
```

### 1.2 缺少 `read_file` 工具
**位置**: `backend/src/tools/builtins/`

**问题描述**:
Skill 系统（query-writing）需要 `read_file` 工具来读取技能文档（如 `references/bim_query_examples.md`）。

在 `prompt.py` 中，技能系统提示词明确说明:
```
1. 当用户查询与技能的用例匹配时，立即使用下面技能标签中提供的路径属性对技能的主文件调用 `read_file`
```

但当前工具集中没有提供这个工具，导致 Agent 无法读取 skill 文档。

### 1.3 db_url 和 building_id 传递问题
**位置**: `backend/src/client.py` 和 `backend/src/agents/sql_agent/agent.py`

**问题描述**:
`make_sql_agent` 需要从 `config.configurable` 中提取 `db_url` 和 `building_id`:
```python
db_url = config.get("configurable", {}).get("db_url")
building_id = config.get("configurable", {}).get("building_id")
```

但 `client.py` 的 `_get_runnable_config` 方法中没有包含这些参数，导致 sql_agent 无法获取数据库连接信息。

## 2. 修复方案

### 2.1 修复 sql_agent 调用方式
修改 `client.py` 中的 `_ensure_agent` 方法，使其正确调用 `make_sql_agent`。

有两种方案:

**方案 A**: 修改 `client.py` 以正确构建 `RunnableConfig` 并传递给 `make_sql_agent`

**方案 B**: 修改 `make_sql_agent` 的签名以接受分散的参数（与 `create_agent` 保持一致）

推荐采用 **方案 A**，因为 `make_sql_agent` 的设计就是通过 `RunnableConfig` 接收配置。

### 2.2 添加 `read_file` 工具
在 `backend/src/tools/builtins/` 目录下创建 `read_file_tool.py`，提供读取文件内容的功能。

### 2.3 添加 db_url 和 building_id 配置
修改 `client.py` 的初始化方法和 `_get_runnable_config` 方法，支持传递 `db_url` 和 `building_id`。

## 3. 实施步骤

1. 创建 `read_file_tool.py` 工具
2. 修改 `client.py` 以支持 sql_agent 的正确调用
3. 更新 `magicflowClient` 类以支持 `db_url` 和 `building_id` 参数
4. 测试 sql_agent 是否能正确读取 skill 文档并执行查询

## 4. 测试验证

测试用例:
1. 前端发送消息: "一层有哪些房间"
2. Agent 应该:
   - 识别需要使用 query-writing skill
   - 使用 `read_file` 工具读取 `SKILL.md` 和 `references/bim_query_examples.md`
   - 根据示例构建 SQL 查询
   - 使用 `sql_db_query` 工具执行查询
   - 返回正确的房间列表
