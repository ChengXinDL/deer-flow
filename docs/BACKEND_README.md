# DeerFlow 后端开发文档

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md) | 后端架构 overview，核心组件和系统架构 |
| [BACKEND_DEVELOPMENT_GUIDE.md](./BACKEND_DEVELOPMENT_GUIDE.md) | 开发环境搭建、开发流程和调试技巧 |
| [BACKEND_API_REFERENCE.md](./BACKEND_API_REFERENCE.md) | 完整的 API 参考文档 |
| [BACKEND_CONFIGURATION.md](./BACKEND_CONFIGURATION.md) | 配置文件详解和环境变量 |
| [BACKEND_COMPONENTS.md](./BACKEND_COMPONENTS.md) | 核心组件详解（Agent、Middleware、Sandbox 等） |
| [BACKEND_TROUBLESHOOTING.md](./BACKEND_TROUBLESHOOTING.md) | 常见问题排查和解决方案 |

---

## 🚀 快速开始

### 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器
- API keys（OpenAI/Anthropic/DeepSeek 等）

### 安装和启动

```bash
# 进入后端目录
cd backend

# 安装依赖
make install

# 启动 LangGraph 服务器（端口 2024）
make dev

# 启动 Gateway API（端口 8001）
make gateway
```

完整应用启动（项目根目录）：
```bash
make dev  # 启动 LangGraph + Gateway + Frontend + Nginx
```

访问：http://localhost:2026

---

## 🏗️ 技术栈

| 类别 | 技术 |
|------|------|
| **Agent 框架** | LangGraph 1.0.6+ |
| **LLM 集成** | LangChain + 多提供商支持 |
| **API 框架** | FastAPI |
| **沙箱执行** | Local / Docker / Kubernetes |
| **包管理** | uv |
| **代码质量** | ruff |

---

## 📁 项目结构

```
backend/
├── src/
│   ├── agents/           # LangGraph Agent 系统
│   │   ├── lead_agent/   # 主 Agent 实现
│   │   ├── middlewares/  # 中间件链
│   │   ├── memory/       # 记忆系统
│   │   └── thread_state.py
│   ├── gateway/          # FastAPI Gateway
│   ├── sandbox/          # 沙箱执行系统
│   ├── subagents/        # 子 Agent 系统
│   ├── tools/            # 工具系统
│   ├── mcp/              # MCP 集成
│   ├── skills/           # 技能系统
│   ├── models/           # 模型工厂
│   ├── config/           # 配置系统
│   └── community/        # 社区工具
├── tests/                # 测试套件
├── docs/                 # 文档
├── Makefile             # 构建脚本
├── pyproject.toml       # Python 依赖
└── langgraph.json       # LangGraph 配置
```

---

## 🔗 相关链接

- [项目 README](../backend/README.md)
- [CLAUDE.md](../backend/CLAUDE.md) - Claude Code 开发指南
- [Architecture](../backend/docs/ARCHITECTURE.md) - 架构文档
- [API Reference](../backend/docs/API.md) - API 文档
- [Configuration](../backend/docs/CONFIGURATION.md) - 配置指南
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

## 💡 提示

- 配置文件 `config.yaml` 放在项目根目录
- 使用 `make dev` 启动完整应用
- 中间件链按严格顺序执行
- 沙箱支持三种模式：Local / Docker / Kubernetes
