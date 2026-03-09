# present_files Tool 使用说明

## 概述

`present_files` 工具用于将文件呈现给用户，使其在前端界面中可见、可下载或可交互。这是将工作成果交付给用户的主要方式。

---

## 能干什么

### 1. 展示单个文件
将一个文件呈现给用户查看或下载：
- 文档文件（.md, .txt, .pdf）
- 代码文件（.py, .js, .ts 等）
- 数据文件（.csv, .json, .xml）
- 图像文件（.png, .jpg, .svg）

### 2. 展示多个相关文件
一次性展示多个相关文件：
- 一个项目的多个输出文件
- 报告及其附件
- 代码文件和文档
- 数据文件和可视化图表

### 3. 并行展示文件
与其他工具并行调用，提高效率：
- 在生成文件的同时展示其他文件
- 在执行任务的同时展示结果
- 批量处理多个文件

### 4. 更新状态
将文件路径添加到 `ThreadState.artifacts` 状态：
- 前端从状态中读取文件列表
- 自动去重和合并
- 支持增量更新

---

## 不能干什么

### 1. 不能用于内部处理
- ❌ 不能用于 Agent 自己读取文件内容
- ❌ 不能用于临时或中间文件
- ❌ 不能用于不需要用户查看的文件

### 2. 不能处理非 outputs 目录的文件
- ❌ 不能展示 `/mnt/user-data/uploads` 中的文件
- ❌ 不能展示 `/mnt/user-data/workspace` 中的文件
- ❌ 不能展示系统其他位置的文件

### 3. 不能修改文件内容
- ❌ 不能编辑文件内容
- ❌ 不能转换文件格式
- ❌ 不能压缩或解压文件

### 4. 不能直接展示文件内容
- ❌ 不能在响应中直接显示文件内容
- ❌ 不能预览文件内容
- ❌ 不能渲染文件内容

### 5. 不能处理不存在的文件
- ❌ 不能展示不存在的文件
- ❌ 不能自动创建文件
- ❌ 不能处理路径错误

---

## 使用条件

### 必须满足的条件

1. **文件存在**
   - 文件必须已经创建
   - 文件路径必须正确
   - 文件内容必须完整

2. **文件在 outputs 目录**
   - 文件必须在 `/mnt/user-data/outputs` 目录中
   - 必须使用绝对路径
   - 虚拟路径会被映射到实际路径

3. **文件需要用户查看**
   - 文件是最终交付物
   - 用户需要查看或下载文件
   - 文件是任务结果的一部分

4. **文件路径正确**
   - 必须使用绝对路径
   - 路径格式必须正确
   - 路径分隔符必须正确

### 不应该使用的条件

1. **文件不存在**
   - ❌ 文件还未创建
   - ❌ 文件路径错误
   - ❌ 文件内容不完整

2. **文件不在 outputs 目录**
   - ❌ 文件在 uploads 目录
   - ❌ 文件在 workspace 目录
   - ❌ 文件在系统其他位置

3. **不需要用户查看**
   - ❌ 临时文件
   - ❌ 中间文件
   - ❌ Agent 内部使用的文件

4. **只需要读取内容**
   - ❌ Agent 只需要读取文件内容
   - ❌ 不需要展示给用户
   - ❌ 只用于数据处理

---

## 参数说明

### runtime（必需，自动注入）
- **类型**: `ToolRuntime[ContextT, ThreadState]`
- **说明**: LangChain 工具运行时上下文
- **作用**: 提供状态和配置信息
- **注入**: 由 LangChain 自动注入

### filepaths（必需）
- **类型**: `list[str]`
- **说明**: 要展示的文件绝对路径列表
- **要求**:
  - 必须是绝对路径
  - 必须在 `/mnt/user-data/outputs` 目录中
  - 文件必须存在
- **示例**:
  ```python
  filepaths=["/mnt/user-data/outputs/report.md"]
  filepaths=["/mnt/user-data/outputs/report.md", "/mnt/user-data/outputs/chart.png"]
  filepaths=[
      "/mnt/user-data/outputs/analysis.md",
      "/mnt/user-data/outputs/data.csv",
      "/mnt/user-data/outputs/visualization.png"
  ]
  ```

### tool_call_id（必需，自动注入）
- **类型**: `str`
- **说明**: 工具调用 ID
- **作用**: 用于跟踪工具调用
- **注入**: 由 LangChain 自动注入

---

## 使用示例

### 示例 1：展示单个文件

```python
# 场景：创建报告后展示给用户

# 1. 创建报告文件
write_file(
    path="/mnt/user-data/outputs/report.md",
    content="# Analysis Report\n\nThis is the analysis result."
)

# 2. 展示报告
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

### 示例 2：展示多个相关文件

```python
# 场景：数据分析项目，展示报告和数据文件

# 1. 创建分析报告
write_file(
    path="/mnt/user-data/outputs/analysis_report.md",
    content="# Data Analysis Report\n\n..."
)

# 2. 创建数据文件
write_file(
    path="/mnt/user-data/outputs/processed_data.csv",
    content="name,value\nItem 1,100\nItem 2,200"
)

# 3. 创建可视化图表
# (假设已经生成了图表)

# 4. 展示所有文件
present_file_tool(
    runtime=runtime,
    filepaths=[
        "/mnt/user-data/outputs/analysis_report.md",
        "/mnt/user-data/outputs/processed_data.csv",
        "/mnt/user-data/outputs/chart.png"
    ],
    tool_call_id=tool_call_id
)
```

### 示例 3：并行展示文件

```python
# 场景：在生成新文件的同时展示其他文件

# 1. 展示已完成的文件
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/part1.md"],
    tool_call_id=tool_call_id_1
)

# 2. 同时生成新文件
task_tool(
    runtime=runtime,
    description="生成第二部分",
    prompt="生成报告的第二部分",
    subagent_type="general-purpose",
    tool_call_id=tool_call_id_2
)

# 3. 展示新生成的文件
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/part2.md"],
    tool_call_id=tool_call_id_3
)
```

### 示例 4：批量展示代码文件

```python
# 场景：展示一个项目的多个代码文件

present_file_tool(
    runtime=runtime,
    filepaths=[
        "/mnt/user-data/outputs/app.py",
        "/mnt/user-data/outputs/models.py",
        "/mnt/user-data/outputs/utils.py",
        "/mnt/user-data/outputs/README.md"
    ],
    tool_call_id=tool_call_id
)
```

---

## 最佳实践

### 1. 先创建后展示
```python
# ❌ 错误：文件还未创建就展示
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)

# ✅ 正确：先创建文件，再展示
write_file(
    path="/mnt/user-data/outputs/report.md",
    content="# Report\n\nContent"
)
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

### 2. 使用绝对路径
```python
# ❌ 错误：使用相对路径
present_file_tool(
    runtime=runtime,
    filepaths=["outputs/report.md"],
    tool_call_id=tool_call_id
)

# ✅ 正确：使用绝对路径
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

### 3. 批量展示相关文件
```python
# ❌ 错误：多次调用展示相关文件
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id_1
)
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/chart.png"],
    tool_call_id=tool_call_id_2
)
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/data.csv"],
    tool_call_id=tool_call_id_3
)

# ✅ 正确：一次调用展示所有相关文件
present_file_tool(
    runtime=runtime,
    filepaths=[
        "/mnt/user-data/outputs/report.md",
        "/mnt/user-data/outputs/chart.png",
        "/mnt/user-data/outputs/data.csv"
    ],
    tool_call_id=tool_call_id
)
```

### 4. 只展示最终成果
```python
# ❌ 错误：展示临时文件
write_file(
    path="/mnt/user-data/outputs/temp.txt",
    content="Temporary data"
)
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/temp.txt"],
    tool_call_id=tool_call_id
)

# ✅ 正确：只展示最终成果
write_file(
    path="/mnt/user-data/outputs/final_report.md",
    content="# Final Report\n\n..."
)
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/final_report.md"],
    tool_call_id=tool_call_id
)
```

### 5. 使用有意义的文件名
```python
# ❌ 错误：文件名不清晰
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/file1.txt", "/mnt/user-data/outputs/file2.txt"],
    tool_call_id=tool_call_id
)

# ✅ 正确：使用有意义的文件名
present_file_tool(
    runtime=runtime,
    filepaths=[
        "/mnt/user-data/outputs/analysis_report.md",
        "/mnt/user-data/outputs/sales_chart.png",
        "/mnt/user-data/outputs/data_summary.csv"
    ],
    tool_call_id=tool_call_id
)
```

---

## 错误处理

### 常见错误

#### 错误 1：文件不存在
```python
# ❌ 错误：文件还未创建
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

**解决方案**：先创建文件，再展示

```python
# ✅ 正确
write_file(
    path="/mnt/user-data/outputs/report.md",
    content="# Report"
)
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

#### 错误 2：路径不是绝对路径
```python
# ❌ 错误：使用相对路径
present_file_tool(
    runtime=runtime,
    filepaths=["outputs/report.md"],
    tool_call_id=tool_call_id
)
```

**解决方案**：使用绝对路径

```python
# ✅ 正确
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

#### 错误 3：文件不在 outputs 目录
```python
# ❌ 错误：文件在 uploads 目录
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/uploads/data.csv"],
    tool_call_id=tool_call_id
)
```

**解决方案**：先将文件移动到 outputs 目录

```python
# ✅ 正确
bash("cp /mnt/user-data/uploads/data.csv /mnt/user-data/outputs/data.csv")
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/data.csv"],
    tool_call_id=tool_call_id
)
```

#### 错误 4：路径格式错误
```python
# ❌ 错误：路径分隔符错误
present_file_tool(
    runtime=runtime,
    filepaths=["mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

**解决方案**：使用正确的绝对路径格式

```python
# ✅ 正确
present_file_tool(
    runtime=runtime,
    filepaths=["/mnt/user-data/outputs/report.md"],
    tool_call_id=tool_call_id
)
```

---

## 执行流程

```
Agent 创建文件
    ↓
Agent 调用 present_files
    ↓
验证文件路径
    ↓
更新 ThreadState.artifacts
    ↓
前端从状态中读取文件列表
    ↓
前端展示文件给用户
```

---

## 状态管理

### ThreadState.artifacts

`present_files` 工具会更新 `ThreadState.artifacts` 状态：

```python
{
    "artifacts": [
        "/mnt/user-data/outputs/report.md",
        "/mnt/user-data/outputs/chart.png",
        "/mnt/user-data/outputs/data.csv"
    ]
}
```

### merge_artifacts Reducer

状态更新由 `merge_artifacts` reducer 处理：
- 自动去重
- 合并新旧文件列表
- 防止并发冲突

---

## 注意事项

1. **路径限制**：只能展示 `/mnt/user-data/outputs` 目录中的文件
2. **绝对路径**：必须使用绝对路径
3. **文件存在性**：文件必须存在
4. **并行安全**：可以安全地并行调用，状态更新由 reducer 处理
5. **自动去重**：重复的文件路径会被自动去重

---

## 相关文档

- [Built-in Tools Reference](./BUILTIN_TOOLS_REFERENCE.md#present_files) - 内置工具参考
- [Thread State](../BACKEND_COMPONENTS.md#thread-state) - 线程状态
- [File System](../BACKEND_ARCHITECTURE.md#file-system) - 文件系统
- [Sandbox](../BACKEND_COMPONENTS.md#sandbox) - 沙箱系统