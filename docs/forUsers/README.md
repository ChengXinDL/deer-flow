# 🦌 magicflow - 2.0 用户使用指南

magicflow（**D**eep **E**xploration and **E**fficient **R**esearch **Flow，深度探索与高效研究流）是一个开源的**超级智能体框架**，它通过**可扩展的技能**来编排**子智能体**、**记忆**和**沙盒**，几乎可以完成任何任务。

> [!NOTE]
> **magicflow 2.0 是完全重写的版本**。它与 v1 版本没有任何代码共享。如果您在寻找原始的 Deep Research 框架，它仍在 [`1.x` 分支](https://github.com/bytedance/magic-flow/tree/main-1.x)上维护——欢迎继续贡献。活跃开发已转移到 2.0 版本。

---

## 目录

- [快速开始](#快速开始)
  - [配置](#配置)
  - [运行应用](#运行应用)
    - [方式一：Docker（推荐）](#方式一docker推荐)
    - [方式二：本地开发](#方式二本地开发)
  - [高级设置](#高级设置)
    - [沙盒模式](#沙盒模式)
    - [MCP 服务器](#mcp-服务器)
- [核心功能](#核心功能)
  - [技能与工具](#技能与工具)
  - [子智能体](#子智能体)
  - [沙盒与文件系统](#沙盒与文件系统)
  - [上下文工程](#上下文工程)
  - [长期记忆](#长期记忆)
- [推荐的模型](#推荐的模型)
- [常见问题](#常见问题)

---

## 快速开始

### 配置

1. **克隆 magicflow 仓库**

   ```bash
   git clone https://github.com/bytedance/magic-flow.git
   cd magic-flow
   ```

2. **生成本地配置文件**

   在项目根目录（`magic-flow/`）下运行：

   ```bash
   make config
   ```

   此命令会根据提供的示例模板创建本地配置文件。

3. **配置您偏好的模型**

   编辑 `config.yaml` 并定义至少一个模型：

   ```yaml
   models:
     - name: gpt-4                       # 内部标识符
       display_name: GPT-4               # 人类可读的名称
       use: langchain_openai:ChatOpenAI  # LangChain 类路径
       model: gpt-4                      # API 的模型标识符
       api_key: $OPENAI_API_KEY          # API 密钥（推荐：使用环境变量）
       max_tokens: 4096                  # 每次请求的最大令牌数
       temperature: 0.7                  # 采样温度
   ```

4. **为配置的模型设置 API 密钥**

   选择以下方法之一：

   - **方法 A：编辑项目根目录下的 `.env` 文件（推荐）**

     ```bash
     TAVILY_API_KEY=your-tavily-api-key
     OPENAI_API_KEY=your-openai-api-key
     # 根据需要添加其他提供商的密钥
     ```

   - **方法 B：在 shell 中导出环境变量**

     ```bash
     export OPENAI_API_KEY=your-openai-api-key
     ```

   - **方法 C：直接编辑 `config.yaml`（不推荐用于生产环境）**

     ```yaml
     models:
       - name: gpt-4
         api_key: your-actual-api-key-here  # 替换占位符
     ```

### 运行应用

#### 方式一：Docker（推荐）

这是以一致环境快速开始的最快方式：

1. **初始化并启动**：
   ```bash
   make docker-init    # 拉取沙盒镜像（仅需一次或镜像更新时）
   make docker-start   # 启动服务（从 config.yaml 自动检测沙盒模式）
   ```

   `make docker-start` 现在仅在 `config.yaml` 使用 provisioner 模式（`sandbox.use: src.community.aio_sandbox:AioSandboxProvider` 配合 `provisioner_url`）时启动 `provisioner`。

2. **访问**：http://localhost:2026

#### 方式二：本地开发

如果您更喜欢在本地运行服务：

1. **检查先决条件**：
   ```bash
   make check  # 验证 Node.js 22+、pnpm、uv、nginx
   ```

2. **（可选）预拉取沙盒镜像**：
   ```bash
   # 如果使用 Docker/容器化沙盒，推荐此步骤
   make setup-sandbox
   ```

3. **启动服务**：
   ```bash
   make dev
   ```

4. **访问**：http://localhost:2026

### 高级设置

#### 沙盒模式

magicflow 支持多种沙盒执行模式：
- **本地执行**（直接在主机上运行沙盒代码）
- **Docker 执行**（在隔离的 Docker 容器中运行沙盒代码）
- **Kubernetes Docker 执行**（通过 provisioner 服务在 Kubernetes Pod 中运行沙盒代码）

对于 Docker 开发，服务启动遵循 `config.yaml` 中的沙盒模式。在本地/Docker 模式下，不会启动 `provisioner`。

#### MCP 服务器

magicflow 支持可配置的 MCP 服务器和技能来扩展其能力。
对于 HTTP/SSE MCP 服务器，支持 OAuth 令牌流（`client_credentials`、`refresh_token`）。

---

## 核心功能

### 技能与工具

技能是让 magicflow 能够完成**几乎任何事情**的关键。

标准的智能体技能是一个结构化的能力模块——一个定义工作流程、最佳实践和支持资源引用的 Markdown 文件。magicflow 内置了研究、报告生成、幻灯片制作、网页制作、图像和视频生成等技能。但真正的力量在于可扩展性：您可以添加自己的技能，替换内置技能，或将它们组合成复合工作流程。

技能是渐进式加载的——仅在任务需要时加载，而不是一次性全部加载。这保持了上下文窗口的精简，使 magicflow 即使在令牌敏感的模型上也能良好运行。

工具遵循相同的理念。magicflow 配备了核心工具集——网络搜索、网络获取、文件操作、bash 执行——并通过 MCP 服务器和 Python 函数支持自定义工具。可以交换任何工具。添加任何工具。

```
# 沙盒容器内的路径
/mnt/skills/public
├── research/SKILL.md
├── report-generation/SKILL.md
├── slide-creation/SKILL.md
├── web-page/SKILL.md
└── image-generation/SKILL.md

/mnt/skills/custom
└── your-custom-skill/SKILL.md      -- 您的技能
```

### 子智能体

复杂的任务很少能一次性完成。magicflow 会将它们分解。

主导智能体可以即时生成子智能体——每个子智能体都有自己的作用域上下文、工具和终止条件。子智能体尽可能并行运行，报告结构化结果，主导智能体将所有内容合成为连贯的输出。

这就是 magicflow 处理需要数分钟到数小时任务的方式：一个研究任务可能会分散到十几个子智能体，每个探索不同的角度，然后汇聚成一份单一的报告——或者一个网站——或者一个带有生成视觉效果的幻灯片。一个框架，多双手。

### 沙盒与文件系统

magicflow 不仅仅是*谈论*做事情。它有自己的计算机。

每个任务都在一个隔离的 Docker 容器中运行，具有完整的文件系统——技能、工作区、上传、输出。智能体读取、写入和编辑文件。它执行 bash 命令和代码。它查看图像。全部沙盒化，全部可审计，会话之间零污染。

这就是具有工具访问权限的聊天机器人与具有实际执行环境的智能体之间的区别。

```
# 沙盒容器内的路径
/mnt/user-data/
├── uploads/          -- 您的文件
├── workspace/        -- 智能体的工作目录
└── outputs/          -- 最终交付物
```

### 上下文工程

**隔离的子智能体上下文**：每个子智能体在自己的隔离上下文中运行。这意味着子智能体将无法看到主导智能体或其他子智能体的上下文。这很重要，可以确保子智能体能够专注于手头的任务，而不会被主导智能体或其他子智能体的上下文分散注意力。

**摘要**：在一个会话中，magicflow 积极地管理上下文——总结已完成的子任务，将中间结果卸载到文件系统，压缩不再立即相关的内容。这使它能够在长时间、多步骤的任务中保持敏锐，而不会耗尽上下文窗口。

### 长期记忆

大多数智能体在对话结束的那一刻就会忘记一切。magicflow 会记住。

跨会话，magicflow 会建立您的个人资料、偏好和积累知识的持久记忆。您使用得越多，它就越了解您——您的写作风格、您的技术栈、您重复的工作流程。记忆存储在本地，并保持在您的控制之下。

---

## 推荐的模型

magicflow 是模型无关的——它适用于任何实现 OpenAI 兼容 API 的 LLM。也就是说，它在支持以下功能的模型上表现最佳：

- **长上下文窗口**（100k+ 令牌）用于深度研究和多步骤任务
- **推理能力**用于自适应规划和复杂分解
- **多模态输入**用于图像理解和视频理解
- **强大的工具使用**用于可靠的函数调用和结构化输出

---

## 常见问题

### Q: magicflow 与其他 AI 助手有什么不同？

A: magicflow 不仅仅是一个聊天机器人。它是一个完整的智能体框架，具有：
- 真正的执行环境（沙盒）
- 多智能体协作
- 持久记忆
- 可扩展的技能系统
- 文件系统和代码执行能力

### Q: 我需要什么技术背景才能使用 magicflow？

A: magicflow 设计为对普通用户友好。您不需要编程知识即可使用基本功能。但是，如果您想自定义技能或进行高级配置，一些技术背景会有所帮助。

### Q: magicflow 支持哪些语言模型？

A: magicflow 支持任何实现 OpenAI 兼容 API 的模型，包括 GPT-4、Claude、Llama 等。您可以在 `config.yaml` 中配置多个模型。

### Q: 我的数据安全吗？

A: 是的。magicflow 在本地运行，您的数据存储在本地。如果您使用云 API，请确保您信任该服务提供商。

### Q: 如何添加自定义技能？

A: 您可以在 `skills/custom/` 目录中创建自己的技能。每个技能是一个 Markdown 文件，定义了工作流程和最佳实践。有关详细信息，请参阅技能开发文档。

### Q: magicflow 可以离线使用吗？

A: 部分功能可以离线使用，但大多数功能需要互联网连接来访问 LLM API 和网络搜索工具。

### Q: 如何获取帮助？

A: 您可以：
- 查看项目文档：[backend/docs/](backend/docs/)
- 提交问题：[GitHub Issues](https://github.com/bytedance/magic-flow/issues)
- 加入社区讨论

---

## 许可证

本项目是开源的，使用 [MIT 许可证](./LICENSE)。

## 致谢

magicflow 建立在开源社区令人难以置信的工作之上。我们要深深感谢所有使 magicflow 成为可能的项目和贡献者。真的，我们站在巨人的肩膀上。

我们要特别感谢以下项目的宝贵贡献：

- **[LangChain](https://github.com/langchain-ai/langchain)**：他们卓越的框架为我们的 LLM 交互和链提供动力，实现了无缝集成和功能。
- **[LangGraph](https://github.com/langchain-ai/langgraph)**：他们创新的多智能体编排方法对于实现 magicflow 复杂的工作流程至关重要。

### 核心贡献者

我们要衷心感谢 `magicflow` 的核心作者，他们的愿景、热情和奉献精神使这个项目得以实现：

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

您坚定不移的承诺和专业知识一直是 magicflow 成功的推动力。我们很荣幸能在这次旅程中由您掌舵。

---

**[返回项目主页](https://magicflow.tech/)** | **[GitHub 仓库](https://github.com/bytedance/magic-flow)**
