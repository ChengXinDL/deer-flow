# ask_clarification Tool 使用说明

## 概述

`ask_clarification` 是一个中断型工具，用于在 Agent 需要更多信息才能继续执行时，向用户询问澄清。调用后会暂停执行，等待用户响应。

---

## 能干什么

### 1. 询问缺少的信息
当用户请求中缺少必要的详细信息时使用：
- 缺少文件路径或 URL
- 缺少具体的技术要求
- 缺少目标环境或配置
- 缺少必要的参数或选项

### 2. 澄清模糊的需求
当需求可以有多种解释时使用：
- 优化代码（性能、可读性、内存？）
- 添加功能（具体什么功能？）
- 改进系统（哪个方面？）

### 3. 询问实现方法
当存在多种有效实现方法时使用：
- 认证方式（JWT、OAuth、Session？）
- 数据库选择（MySQL、PostgreSQL、MongoDB？）
- 部署方式（Docker、Kubernetes、传统部署？）

### 4. 确认危险操作
当执行可能造成破坏的操作时使用：
- 删除文件或目录
- 修改生产环境配置
- 数据库操作（删除、修改）
- 覆盖现有代码或数据

### 5. 提供建议并征求同意
当 Agent 有推荐方案但需要用户批准时使用：
- 建议重构某个模块
- 建议使用某种技术栈
- 建议某种实现方式

---

## 不能干什么

### 1. 不能用于信息收集
- ❌ 不能用于收集用户偏好或反馈
- ❌ 不能用于市场调研或问卷调查
- ❌ 不能用于获取非必要信息

### 2. 不能用于非阻塞场景
- ❌ 不能在执行过程中途询问（应该在开始前询问）
- ❌ 不能用于简单的确认（应该直接执行）
- ❌ 不能用于非关键决策

### 3. 不能嵌套调用
- ❌ 不能在子代理中使用此工具
- ❌ 不能在工具链中多次调用
- ❌ 不能与其他中断型工具混用

### 4. 不能用于展示信息
- ❌ 不能用于展示结果或报告
- ❌ 不能用于提供帮助或教程
- ❌ 不能用于解释概念或技术

### 5. 不能绕过用户同意
- ❌ 不能假设用户同意
- ❌ 不能跳过确认步骤
- ❌ 不能在没有用户输入的情况下继续

---

## 使用条件

### 必须满足的条件

1. **缺少必要信息**
   - 用户请求中缺少关键信息
   - 无法从上下文中推断出信息
   - 信息对任务执行至关重要

2. **需求模糊不清**
   - 存在多种有效解释
   - 无法确定用户真实意图
   - 需要明确具体要求

3. **存在多种方法**
   - 有多个可行的实现方案
   - 需要用户选择偏好
   - 不同方案有不同权衡

4. **操作具有风险**
   - 可能造成数据丢失
   - 可能影响生产环境
   - 可能产生不可逆的后果

5. **需要用户批准**
   - Agent 有推荐方案
   - 需要用户确认才能继续
   - 涉及重要决策

### 不应该使用的条件

1. **信息已充分**
   - ✅ 用户提供了所有必要信息
   - ✅ 可以从上下文中推断出信息
   - ✅ 信息对任务执行非关键

2. **需求明确**
   - ✅ 只有一种合理解释
   - ✅ 用户意图清晰
   - ✅ 具体要求明确

3. **方法唯一**
   - ✅ 只有一种可行方案
   - ✅ 标准做法明确
   - ✅ 没有选择余地

4. **操作安全**
   - ✅ 只影响临时文件
   - ✅ 可以轻松回滚
   - ✅ 不涉及生产环境

5. **无需批准**
   - ✅ 标准操作流程
   - ✅ 用户已明确指示
   - ✅ 不涉及重要决策

---

## 参数说明

### question（必需）
- **类型**: `str`
- **说明**: 向用户提出的问题
- **要求**: 必须具体明确
- **示例**:
  ```python
  question="您想要抓取哪个网站的内容？"
  question="您希望优化代码的哪个方面？"
  question="确认要删除生产数据库吗？此操作不可逆！"
  ```

### clarification_type（必需）
- **类型**: `Literal["missing_info", "ambiguous_requirement", "approach_choice", "risk_confirmation", "suggestion"]`
- **说明**: 澄清类型
- **选项**:
  - `missing_info` - 缺少信息
  - `ambiguous_requirement` - 需求模糊
  - `approach_choice` - 方法选择
  - `risk_confirmation` - 风险确认
  - `suggestion` - 建议

### context（可选）
- **类型**: `str | None`
- **说明**: 解释为什么需要澄清的上下文信息
- **作用**: 帮助用户理解情况
- **示例**:
  ```python
  context="我需要知道目标网站的 URL 才能创建 scraper"
  context="优化可以指性能、可读性、内存使用等多个方面"
  context="删除备份文件可能导致数据无法恢复"
  ```

### options（可选）
- **类型**: `list[str] | None`
- **说明**: 供用户选择的选项列表
- **适用类型**: `approach_choice` 和 `suggestion`
- **示例**:
  ```python
  options=["性能优化", "代码可读性", "内存使用", "安全性"]
  options=["JWT Token", "OAuth 2.0", "Session-based", "API Keys"]
  options=["继续重构", "保持现状", "稍后再说"]
  ```

---

## 使用示例

### 示例 1：缺少信息

```python
# 场景：用户说"创建一个 web scraper"，但没有指定目标网站

ask_clarification(
    question="您想要抓取哪个网站的内容？",
    clarification_type="missing_info",
    context="我需要知道目标网站的 URL 才能创建 scraper"
)
```

### 示例 2：需求模糊

```python
# 场景：用户说"优化代码"，但未明确优化目标

ask_clarification(
    question="您希望优化代码的哪个方面？",
    clarification_type="ambiguous_requirement",
    context="优化可以指性能、可读性、内存使用等多个方面",
    options=[
        "性能优化（提高执行速度）",
        "代码可读性（提高代码质量）",
        "内存使用（减少内存占用）",
        "安全性（修复安全漏洞）"
    ]
)
```

### 示例 3：方法选择

```python
# 场景：用户说"添加认证"，但未指定认证方式

ask_clarification(
    question="您希望使用哪种认证方式？",
    clarification_type="approach_choice",
    context="不同的认证方式适用于不同的场景",
    options=["JWT Token", "OAuth 2.0", "Session-based", "API Keys"]
)
```

### 示例 4：风险确认

```python
# 场景：删除生产环境的文件

ask_clarification(
    question="确认要删除生产环境的数据库备份文件吗？此操作不可逆！",
    clarification_type="risk_confirmation",
    context="删除备份文件可能导致数据无法恢复"
)
```

### 示例 5：建议

```python
# 场景：建议重构某个模块

ask_clarification(
    question="我建议重构认证模块以提高安全性，是否继续？",
    clarification_type="suggestion",
    context="当前实现存在潜在的安全漏洞",
    options=["继续重构", "保持现状", "稍后再说"]
)
```

---

## 最佳实践

### 1. 一次只问一个问题
```python
# ❌ 错误：一次问多个问题
ask_clarification(
    question="您想要抓取哪个网站？使用什么语言？需要处理什么数据？",
    clarification_type="missing_info"
)

# ✅ 正确：一次只问一个问题
ask_clarification(
    question="您想要抓取哪个网站的内容？",
    clarification_type="missing_info"
)
```

### 2. 问题要具体明确
```python
# ❌ 错误：问题模糊
ask_clarification(
    question="您想要什么？",
    clarification_type="ambiguous_requirement"
)

# ✅ 正确：问题具体
ask_clarification(
    question="您希望优化代码的哪个方面？",
    clarification_type="ambiguous_requirement",
    options=["性能优化", "代码可读性", "内存使用", "安全性"]
)
```

### 3. 不要做假设
```python
# ❌ 错误：假设用户意图
# 直接开始创建 web scraper，假设是某个网站

# ✅ 正确：询问用户
ask_clarification(
    question="您想要抓取哪个网站的内容？",
    clarification_type="missing_info"
)
```

### 4. 危险操作必须确认
```python
# ❌ 错误：不确认就执行危险操作
# 直接删除生产数据库

# ✅ 正确：先确认
ask_clarification(
    question="确认要删除生产数据库吗？此操作不可逆！",
    clarification_type="risk_confirmation",
    context="删除数据库会导致所有数据丢失"
)
```

### 5. 提供有用的上下文
```python
# ❌ 错误：没有上下文
ask_clarification(
    question="您想要抓取哪个网站？",
    clarification_type="missing_info"
)

# ✅ 正确：提供上下文
ask_clarification(
    question="您想要抓取哪个网站的内容？",
    clarification_type="missing_info",
    context="我需要知道目标网站的 URL 才能创建 scraper，不同的网站可能需要不同的解析策略"
)
```

---

## 错误处理

### 常见错误

#### 错误 1：在错误的时间调用
```python
# ❌ 错误：在执行中途询问
# 开始执行任务
bash("npm install")
# 执行到一半询问用户
ask_clarification(
    question="您想要安装哪个版本的包？",
    clarification_type="missing_info"
)
```

**解决方案**：在开始执行前就完成所有必要的澄清

#### 错误 2：问题不具体
```python
# ❌ 错误：问题太模糊
ask_clarification(
    question="您想要什么？",
    clarification_type="ambiguous_requirement"
)
```

**解决方案**：提供具体、明确的问题和选项

#### 错误 3：缺少必要的上下文
```python
# ❌ 错误：没有上下文
ask_clarification(
    question="您想要抓取哪个网站？",
    clarification_type="missing_info"
)
```

**解决方案**：使用 `context` 参数解释为什么需要澄清

#### 错误 4：提供太多选项
```python
# ❌ 错误：选项太多
ask_clarification(
    question="您希望使用哪种技术？",
    clarification_type="approach_choice",
    options=["React", "Vue", "Angular", "Svelte", "Solid", "Qwik", "Alpine", "Preact", "Lit", "Stencil", ...]
)
```

**解决方案**：限制选项数量，最多 4-5 个

---

## 执行流程

```
Agent 调用 ask_clarification
    ↓
ClarificationMiddleware 拦截工具调用
    ↓
执行被中断
    ↓
问题呈现给用户
    ↓
等待用户响应
    ↓
用户响应
    ↓
执行继续
```

---

## 注意事项

1. **中断执行**：调用此工具后，Agent 的执行会立即暂停
2. **等待响应**：必须等待用户响应后才能继续
3. **不能嵌套**：不能在子代理中使用此工具
4. **Middleware 处理**：实际逻辑由 ClarificationMiddleware 处理
5. **一次一个**：一次只问一个问题，避免混淆

---

## 相关文档

- [Built-in Tools Reference](./BUILTIN_TOOLS_REFERENCE.md#ask_clarification) - 内置工具参考
- [ClarificationMiddleware](../BACKEND_COMPONENTS.md#clarificationmiddleware) - 澄清中间件
- [Thread State](../BACKEND_COMPONENTS.md#thread-state) - 线程状态
