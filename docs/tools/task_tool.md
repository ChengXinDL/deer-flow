# task Tool 使用说明

## 概述

`task` 工具用于将任务委派给专门的子代理（Subagent）。子代理在独立的上下文中运行，可以处理复杂的多步骤任务，同时保持主对话的上下文清晰。

---

## 能干什么

### 1. 委派复杂任务
将复杂的多步骤任务委派给子代理：
- 需要多步骤推理的任务
- 需要探索和行动的任务
- 需要隔离上下文的任务
- 产生详细输出的任务

### 2. 并行执行任务
同时启动多个子代理，提高效率：
- 并行研究多个主题
- 并行分析多个文件
- 并行执行多个独立任务
- 并行生成多个输出

### 3. 使用专门的子代理类型
根据任务特点选择合适的子代理：
- **general-purpose**：通用的能力代理
- **bash**：命令执行专家

### 4. 限制子代理轮次
控制子代理的执行时间：
- 设置最大轮次数
- 防止无限循环
- 控制资源使用

### 5. 实时进度跟踪
通过事件流跟踪子代理进度：
- 任务开始事件
- 任务运行事件（AI 消息）
- 任务完成事件
- 任务失败事件
- 任务超时事件

---

## 不能干什么

### 1. 不能用于简单任务
- ❌ 不能用于单步骤操作
- ❌ 不能用于简单的文件读取
- ❌ 不能用于简单的命令执行
- ❌ 不能用于不需要推理的任务

### 2. 不能用于需要用户交互的任务
- ❌ 不能用于需要用户澄清的任务
- ❌ 不能用于需要用户确认的任务
- ❌ 不能用于需要用户输入的任务
- ❌ 不能用于需要用户决策的任务

### 3. 不能嵌套调用
- ❌ 不能在子代理中使用此工具
- ❌ 不能递归委派任务
- ❌ 不能创建子代理链
- ❌ 不能无限嵌套

### 4. 不能绕过并发限制
- ❌ 不能超过每轮最大并发数（默认 3）
- ❌ 不能绕过 SubagentLimitMiddleware
- ❌ 不能同时启动过多子代理
- ❌ 不能忽略并发限制

### 5. 不能使用不存在的子代理类型
- ❌ 不能使用未定义的子代理类型
- ❌ 不能使用自定义子代理类型
- ❌ 不能修改子代理配置
- ❌ 不能绕过子代理限制

---

## 使用条件

### 必须满足的条件

1. **任务复杂**
   - 需要多步骤推理
   - 需要探索和行动
   - 需要隔离上下文
   - 产生详细输出

2. **任务独立**
   - 可以独立完成
   - 不需要用户交互
   - 不需要用户确认
   - 不需要用户决策

3. **子代理类型可用**
   - 子代理类型已定义
   - 子代理配置正确
   - 子代理工具可用
   - 子代理超时设置合理

4. **并发限制未超**
   - 当前并发数 < 最大并发数
   - 有足够的资源执行
   - 不会造成资源竞争

### 不应该使用的条件

1. **任务简单**
   - ❌ 单步骤操作
   - ❌ 简单的文件读取
   - ❌ 简单的命令执行
   - ❌ 不需要推理的任务

2. **需要用户交互**
   - ❌ 需要用户澄清
   - ❌ 需要用户确认
   - ❌ 需要用户输入
   - ❌ 需要用户决策

3. **子代理类型不可用**
   - ❌ 子代理类型未定义
   - ❌ 子代理配置错误
   - ❌ 子代理工具不可用
   - ❌ 子代理超时设置不合理

4. **并发限制已超**
   - ❌ 当前并发数 >= 最大并发数
   - ❌ 资源不足
   - ❌ 可能造成资源竞争

---

## 参数说明

### runtime（必需，自动注入）
- **类型**: `ToolRuntime[ContextT, ThreadState]`
- **说明**: LangChain 工具运行时上下文
- **作用**: 提供状态和配置信息
- **注入**: 由 LangChain 自动注入

### description（必需）
- **类型**: `str`
- **说明**: 任务简短描述（3-5 个词）
- **要求**:
  - 简短明了
  - 描述任务本质
  - 用于日志和显示
- **示例**:
  ```python
  description="分析腾讯股价"
  description="运行测试套件"
  description="生成数据报告"
  description="代码审查"
  ```

### prompt（必需）
- **类型**: `str`
- **说明**: 子代理的任务描述
- **要求**:
  - 具体明确
  - 说明需要做什么
  - 包含必要的上下文
  - 提供清晰的指令
- **示例**:
  ```python
  prompt="研究腾讯股价近期下跌的原因，包括财务报告、负面新闻、行业趋势等"
  prompt="执行项目的完整测试套件，包括单元测试和集成测试"
  prompt="分析销售数据并生成可视化报告，保存到 /mnt/user-data/outputs/"
  ```

### subagent_type（必需）
- **类型**: `Literal["general-purpose", "bash"]`
- **说明**: 子代理类型
- **选项**:
  - `general-purpose` - 通用的能力代理
  - `bash` - 命令执行专家
- **选择原则**:
  - 复杂推理 → general-purpose
  - 命令执行 → bash
  - 两者都适用 → general-purpose

### max_turns（可选）
- **类型**: `int | None`
- **说明**: 子代理最大轮次数
- **默认**: 子代理配置的默认值
- **作用**: 控制子代理执行时间
- **示例**:
  ```python
  max_turns=5  # 最多 5 轮
  max_turns=10  # 最多 10 轮
  max_turns=None  # 使用默认值
  ```

### tool_call_id（必需，自动注入）
- **类型**: `str`
- **说明**: 工具调用 ID
- **作用**: 用于跟踪工具调用
- **注入**: 由 LangChain 自动注入

---

## 子代理类型

### general-purpose

**用途**：通用的能力代理，适用于复杂、多步骤的任务

**特点**：
- 支持复杂的推理和规划
- 可以使用多种工具
- 适合需要探索和行动的任务
- 具有独立的上下文空间

**适用场景**：
- 复杂的研究任务
- 代码探索和分析
- 多步骤的文件操作
- 需要综合分析的任务

**示例**：
```python
task_tool(
    runtime=runtime,
    description="代码审查",
    prompt="审查 /mnt/user-data/workspace/app.py 文件的代码质量，包括：\n1. 代码结构和可读性\n2. 潜在的 bug 和安全问题\n3. 性能优化建议\n4. 最佳实践建议",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

### bash

**用途**：命令执行专家，专门用于运行 bash 命令

**特点**：
- 专注于命令执行
- 适合 git 操作、构建过程
- 处理会产生大量输出的命令
- 更高效的命令执行

**适用场景**：
- Git 操作（clone, commit, push 等）
- 构建和测试（npm test, make build 等）
- 部署操作
- 系统管理命令

**示例**：
```python
task_tool(
    runtime=runtime,
    description="运行测试",
    prompt="执行项目的完整测试套件：\n1. 拉取最新代码\n2. 安装依赖\n3. 运行单元测试\n4. 运行集成测试\n5. 生成测试报告",
    subagent_type="bash",
    tool_call_id=tool_call_id
)
```

---

## 使用示例

### 示例 1：复杂研究任务

```python
# 场景：研究某个技术主题

task_tool(
    runtime=runtime,
    description="研究 LangGraph",
    prompt="研究 LangGraph 框架：\n1. 核心概念和架构\n2. 主要功能和特性\n3. 使用场景和最佳实践\n4. 与其他框架的对比\n5. 生成研究报告（保存到 /mnt/user-data/outputs/）",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

### 示例 2：并行研究任务

```python
# 场景：并行研究多个主题

task_tool(
    runtime=runtime,
    description="AWS 研究",
    prompt="研究 AWS 云服务：\n1. 核心服务和特点\n2. 定价策略\n3. 优势和劣势\n4. 适用场景",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_1
)

task_tool(
    runtime=runtime,
    description="Azure 研究",
    prompt="研究 Azure 云服务：\n1. 核心服务和特点\n2. 定价策略\n3. 优势和劣势\n4. 适用场景",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_2
)

task_tool(
    runtime=runtime,
    description="GCP 研究",
    prompt="研究 GCP 云服务：\n1. 核心服务和特点\n2. 定价策略\n3. 优势和劣势\n4. 适用场景",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_3
)

# 等待所有任务完成后，综合结果
```

### 示例 3：命令执行任务

```python
# 场景：执行构建和测试

task_tool(
    runtime=runtime,
    description="构建和测试",
    prompt="执行以下构建和测试流程：\n1. 拉取最新代码：git pull\n2. 安装依赖：npm install\n3. 运行测试：npm test\n4. 构建项目：npm run build\n5. 生成构建报告",
    subagent_type="bash",
    tool_call_id=tool_call_id
)
```

### 示例 4：限制子代理轮次

```python
# 场景：快速代码审查

task_tool(
    runtime=runtime,
    description="快速审查",
    prompt="审查指定文件的代码质量和潜在问题，重点关注：\n1. 主要 bug\n2. 安全问题\n3. 性能问题",
    subagent_type="general-purpose",
    max_turns=5,  # 最多 5 轮
    tool_call_id=tool_call_id
)
```

### 示例 5：数据分析任务

```python
# 场景：分析数据并生成报告

task_tool(
    runtime=runtime,
    description="数据分析",
    prompt="分析 /mnt/user-data/uploads/sales_data.csv 文件：\n1. 统计销售趋势\n2. 识别关键指标\n3. 生成可视化图表（保存到 /mnt/user-data/outputs/）\n4. 创建分析报告（保存到 /mnt/user-data/outputs/analysis_report.md）",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

---

## 最佳实践

### 1. 选择合适的子代理类型
```python
# ❌ 错误：使用 general-purpose 执行简单命令
task_tool(
    runtime=runtime,
    description="运行测试",
    prompt="npm test",
    subagent_type="general-purpose",  # 不必要
    tool_call_id=tool_call_id
)

# ✅ 正确：使用 bash 执行命令
task_tool(
    runtime=runtime,
    description="运行测试",
    prompt="npm test",
    subagent_type="bash",  # 更高效
    tool_call_id=tool_call_id
)
```

### 2. 提供清晰的 prompt
```python
# ❌ 错误：prompt 不清晰
task_tool(
    runtime=runtime,
    description="分析数据",
    prompt="分析数据",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)

# ✅ 正确：prompt 具体明确
task_tool(
    runtime=runtime,
    description="分析销售数据",
    prompt="分析 /mnt/user-data/uploads/sales_data.csv 文件：\n1. 统计销售趋势\n2. 识别关键指标\n3. 生成可视化图表\n4. 创建分析报告",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

### 3. 并行执行独立任务
```python
# ❌ 错误：串行执行独立任务
task_tool(
    runtime=runtime,
    description="研究 A",
    prompt="研究主题 A",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_1
)
# 等待完成
task_tool(
    runtime=runtime,
    description="研究 B",
    prompt="研究主题 B",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_2
)

# ✅ 正确：并行执行独立任务
task_tool(
    runtime=runtime,
    description="研究 A",
    prompt="研究主题 A",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_1
)
task_tool(
    runtime=runtime,
    description="研究 B",
    prompt="研究主题 B",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_2
)
task_tool(
    runtime=runtime,
    description="研究 C",
    prompt="研究主题 C",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_3
)
```

### 4. 设置合理的 max_turns
```python
# ❌ 错误：不限制轮次，可能导致无限循环
task_tool(
    runtime=runtime,
    description="分析代码",
    prompt="分析整个代码库",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)

# ✅ 正确：限制轮次，防止无限循环
task_tool(
    runtime=runtime,
    description="分析核心代码",
    prompt="分析代码库的核心模块，重点关注：\n1. 主要功能\n2. 代码质量\n3. 潜在问题",
    subagent_type="general-purpose",
    max_turns=10,  # 限制轮次
    tool_call_id=tool_call_id
)
```

### 5. description 要简洁
```python
# ❌ 错误：description 太长
task_tool(
    runtime=runtime,
    description="研究腾讯股价下跌的原因，包括财务报告、负面新闻、行业趋势等多个方面",
    prompt="研究腾讯股价",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)

# ✅ 正确：description 简洁
task_tool(
    runtime=runtime,
    description="研究腾讯股价",
    prompt="研究腾讯股价近期下跌的原因，包括财务报告、负面新闻、行业趋势等",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

---

## 错误处理

### 常见错误

#### 错误 1：任务超时
```python
# ❌ 错误：任务太复杂，容易超时
task_tool(
    runtime=runtime,
    description="分析整个代码库",
    prompt="分析整个代码库的所有文件",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

**解决方案**：分解任务，限制轮次

```python
# ✅ 正确：分解任务，限制轮次
task_tool(
    runtime=runtime,
    description="分析核心模块",
    prompt="分析代码库的核心模块，重点关注：\n1. 主要功能\n2. 代码质量\n3. 潜在问题",
    subagent_type="general-purpose",
    max_turns=10,
    tool_call_id=tool_call_id
)
```

#### 错误 2：子代理失败
```python
# ❌ 错误：没有处理子代理失败
task_tool(
    runtime=runtime,
    description="执行任务",
    prompt="执行任务",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

**解决方案**：提供详细的任务描述和错误处理

```python
# ✅ 正确：提供详细的任务描述
task_tool(
    runtime=runtime,
    description="执行任务",
    prompt="执行以下任务：\n1. 读取文件 /mnt/user-data/workspace/data.csv\n2. 分析数据\n3. 生成报告\n\n如果遇到错误，请：\n1. 记录错误信息\n2. 尝试恢复\n3. 提供详细的错误报告",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id
)
```

#### 错误 3：使用了不存在的子代理类型
```python
# ❌ 错误：子代理类型不存在
task_tool(
    runtime=runtime,
    description="执行任务",
    prompt="执行任务",
    subagent_type="custom-agent",  # 不存在
    tool_call_id=tool_call_id
)
```

**解决方案**：使用正确的子代理类型

```python
# ✅ 正确：使用存在的子代理类型
task_tool(
    runtime=runtime,
    description="执行任务",
    prompt="执行任务",
    subagent_type="general-purpose",  # 存在
    tool_call_id=tool_call_id
)
```

#### 错误 4：超过并发限制
```python
# ❌ 错误：同时启动太多子代理
task_tool(
    runtime=runtime,
    description="任务 1",
    prompt="执行任务 1",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_1
)
task_tool(
    runtime=runtime,
    description="任务 2",
    prompt="执行任务 2",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_2
)
task_tool(
    runtime=runtime,
    description="任务 3",
    prompt="执行任务 3",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_3
)
task_tool(
    runtime=runtime,
    description="任务 4",  # 超过限制
    prompt="执行任务 4",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_4
)
```

**解决方案**：分批执行或减少并发数

```python
# ✅ 正确：分批执行
# 第一批
task_tool(
    runtime=runtime,
    description="任务 1",
    prompt="执行任务 1",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_1
)
task_tool(
    runtime=runtime,
    description="任务 2",
    prompt="执行任务 2",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_2
)
task_tool(
    runtime=runtime,
    description="任务 3",
    prompt="执行任务 3",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_3
)
# 等待第一批完成
# 第二批
task_tool(
    runtime=runtime,
    description="任务 4",
    prompt="执行任务 4",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_4
)
```

---

## 执行流程

```
Agent 调用 task 工具
    ↓
创建子代理执行器
    ↓
启动后台执行
    ↓
后台轮询子代理状态
    ↓
发送事件流
    ├─ task_started
    ├─ task_running（AI 消息）
    ├─ task_completed / task_failed / task_timed_out
    └─ ...
    ↓
返回结果给 Agent
```

## 事件流

### task_started
```json
{
    "type": "task_started",
    "task_id": "tool_call_id",
    "description": "任务描述"
}
```

### task_running
```json
{
    "type": "task_running",
    "task_id": "tool_call_id",
    "message": "AI 消息内容",
    "message_index": 1,
    "total_messages": 3
}
```

### task_completed
```json
{
    "type": "task_completed",
    "task_id": "tool_call_id",
    "result": "任务结果"
}
```

### task_failed
```json
{
    "type": "task_failed",
    "task_id": "tool_call_id",
    "error": "错误信息"
}
```

### task_timed_out
```json
{
    "type": "task_timed_out",
    "task_id": "tool_call_id",
    "error": "超时信息"
}
```

---

## 注意事项

1. **超时限制**：每个子代理都有执行超时限制（默认 10 分钟）
2. **轮询限制**：后台轮询有超时保护（执行超时 + 60 秒缓冲）
3. **禁止嵌套**：子代理不能再次调用 `task` 工具（防止递归）
4. **工具限制**：子代理不包含 `task` 工具，防止递归调用
5. **并发限制**：受 `SubagentLimitMiddleware` 限制，每轮最多 N 个并发子代理（默认 3）
6. **状态隔离**：子代理有独立的上下文，不会污染主对话

---

## 相关文档

- [Built-in Tools Reference](./BUILTIN_TOOLS_REFERENCE.md#task) - 内置工具参考
- [Subagents](../BACKEND_COMPONENTS.md#subagents) - 子代理系统
- [SubagentLimitMiddleware](../BACKEND_COMPONENTS.md#subagentlimitmiddleware) - 子代理限制中间件
- [Thread State](../BACKEND_COMPONENTS.md#thread-state) - 线程状态