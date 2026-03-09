# magicflow 后端配置指南

## 配置文件位置

magicflow 使用两个主要配置文件，都应放�?*项目根目�?*�?
1. **`config.yaml`** - 主应用配�?2. **`extensions_config.json`** - MCP 服务器和技能配�?
```
magic-flow/
├── config.yaml              # 主配置（推荐位置�?├── extensions_config.json   # 扩展配置
├── backend/
└── frontend/
```

## 配置优先�?
### config.yaml 搜索顺序

1. `MAGIC_FLOW_CONFIG_PATH` 环境变量
2. `backend/config.yaml`（当前目录）
3. `config.yaml`（父目录 - **推荐**�?
### extensions_config.json 搜索顺序

1. `MAGIC_FLOW_EXTENSIONS_CONFIG_PATH` 环境变量
2. `backend/extensions_config.json`（当前目录）
3. `extensions_config.json`（父目录 - **推荐**�?
## 配置模板

### config.yaml 模板

```yaml
# ============================================
# magicflow 主配置文�?# ============================================

# --------------------------------------------
# 模型配置
# --------------------------------------------
models:
  # OpenAI GPT-4o
  - name: gpt-4o
    display_name: GPT-4o
    use: langchain_openai:ChatOpenAI
    model: gpt-4o
    api_key: $OPENAI_API_KEY
    max_tokens: 4096
    temperature: 0.7
    supports_thinking: false
    supports_vision: true

  # Anthropic Claude 3 Opus
  - name: claude-3-opus
    display_name: Claude 3 Opus
    use: langchain_anthropic:ChatAnthropic
    model: claude-3-opus-20240229
    api_key: $ANTHROPIC_API_KEY
    max_tokens: 4096
    temperature: 0.7
    supports_thinking: false
    supports_vision: true

  # DeepSeek V3
  - name: deepseek-v3
    display_name: DeepSeek V3
    use: langchain_deepseek:ChatDeepSeek
    model: deepseek-chat
    api_key: $DEEPSEEK_API_KEY
    max_tokens: 4096
    temperature: 0.7
    supports_thinking: true
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled

  # OpenAI 兼容端点示例 (Novita)
  - name: novita-deepseek
    display_name: Novita DeepSeek
    use: langchain_openai:ChatOpenAI
    model: deepseek/deepseek-v3.2
    api_key: $NOVITA_API_KEY
    base_url: https://api.novita.ai/openai
    supports_thinking: true
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled

# --------------------------------------------
# 工具分组
# --------------------------------------------
tool_groups:
  - name: web          # 网页浏览和搜�?  - name: file:read    # 只读文件操作
  - name: file:write   # 写入文件操作
  - name: bash         # Shell 命令执行

# --------------------------------------------
# 工具配置
# --------------------------------------------
tools:
  # 网页搜索 (Tavily)
  - name: web_search
    group: web
    use: src.community.tavily.tools:web_search_tool
    max_results: 5
    # api_key: $TAVILY_API_KEY  # 可选，默认使用环境变量

  # 网页获取 (Jina AI)
  - name: web_fetch
    group: web
    use: src.community.jina_ai.tools:web_fetch_tool

  # 图片搜索 (DuckDuckGo)
  - name: image_search
    group: web
    use: src.community.image_search.tools:image_search_tool
    max_results: 5

  # 文件操作
  - name: ls
    group: file:read
    use: src.sandbox.tools:list_dir_tool

  - name: read_file
    group: file:read
    use: src.sandbox.tools:read_file_tool

  - name: write_file
    group: file:write
    use: src.sandbox.tools:write_file_tool

  - name: str_replace
    group: file:write
    use: src.sandbox.tools:str_replace_tool

  # Bash 执行
  - name: bash
    group: bash
    use: src.sandbox.tools:bash_tool

# --------------------------------------------
# 沙箱配置
# --------------------------------------------
sandbox:
  # 选项 1: 本地沙箱（开发，默认�?  use: src.sandbox.local:LocalSandboxProvider

  # 选项 2: Docker 沙箱（生产）
  # use: src.community.aio_sandbox:AioSandboxProvider
  # port: 8080
  # auto_start: true
  # container_prefix: magic-flow-sandbox

  # 选项 3: Kubernetes 沙箱
  # use: src.community.aio_sandbox:AioSandboxProvider
  # provisioner_url: http://provisioner:8002

# --------------------------------------------
# 技能配�?# --------------------------------------------
skills:
  # 主机路径（可选，默认: ../skills�?  path: /custom/path/to/skills

  # 容器挂载路径（默�? /mnt/skills�?  container_path: /mnt/skills

# --------------------------------------------
# 标题生成配置
# --------------------------------------------
title:
  enabled: true
  max_words: 6
  max_chars: 60
  model_name: null  # null 表示使用第一个模�?
# --------------------------------------------
# 记忆系统配置
# --------------------------------------------
memory:
  enabled: true
  max_tokens: 2000
  similarity_weight: 0.6  # TF-IDF 相似度权�?  confidence_weight: 0.4  # 置信度权�?
# --------------------------------------------
# 摘要配置（可选）
# --------------------------------------------
summarization:
  enabled: false
  max_tokens: 8000
  threshold: 0.8

# --------------------------------------------
# �?Agent 配置
# --------------------------------------------
subagents:
  enabled: true
  max_concurrent: 3
  timeout: 900  # 15 分钟
```

### extensions_config.json 模板

```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN"
      }
    },
    "postgres": {
      "enabled": false,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "$DATABASE_URL"
      }
    },
    "brave-search": {
      "enabled": false,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "$BRAVE_API_KEY"
      }
    },
    "secure-api": {
      "enabled": false,
      "type": "http",
      "url": "https://api.example.com/mcp",
      "oauth": {
        "enabled": true,
        "token_url": "https://auth.example.com/oauth/token",
        "grant_type": "client_credentials",
        "client_id": "$OAUTH_CLIENT_ID",
        "client_secret": "$OAUTH_CLIENT_SECRET",
        "scope": "mcp.read",
        "refresh_skew_seconds": 60
      }
    }
  },
  "skills": {
    "research": {
      "enabled": true
    },
    "report-generation": {
      "enabled": true
    },
    "slide-creation": {
      "enabled": false
    }
  }
}
```

## 环境变量

### 必需变量

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic (可�?
export ANTHROPIC_API_KEY="sk-..."

# DeepSeek (可�?
export DEEPSEEK_API_KEY="sk-..."
```

### 可选变�?
```bash
# Tavily 搜索
export TAVILY_API_KEY="tvly-..."

# GitHub MCP
export GITHUB_TOKEN="ghp_..."

# 自定义配置路�?export MAGIC_FLOW_CONFIG_PATH="/path/to/config.yaml"
export MAGIC_FLOW_EXTENSIONS_CONFIG_PATH="/path/to/extensions_config.json"

# LangSmith 追踪
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="ls-..."
export LANGCHAIN_PROJECT="magic-flow"
```

## 配置详解

### 模型配置

#### 支持的提供商

| 提供�?| use �?| 说明 |
|--------|--------|------|
| OpenAI | `langchain_openai:ChatOpenAI` | GPT-4, GPT-4o |
| Anthropic | `langchain_anthropic:ChatAnthropic` | Claude 3 系列 |
| DeepSeek | `langchain_deepseek:ChatDeepSeek` | DeepSeek V3 |
| Google | `langchain_google_genai:ChatGoogleGenerativeAI` | Gemini |

#### 思考模�?
某些模型支持"思�?模式�?
```yaml
models:
  - name: deepseek-v3
    supports_thinking: true
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled
```

#### OpenAI 兼容端点

```yaml
models:
  - name: custom-model
    use: langchain_openai:ChatOpenAI
    base_url: https://api.custom.com/openai
    api_key: $CUSTOM_API_KEY
```

### 沙箱配置

#### 本地沙箱

```yaml
sandbox:
  use: src.sandbox.local:LocalSandboxProvider
```

**特点**:
- 单例实例
- 直接执行
- 适合开�?
#### Docker 沙箱

```yaml
sandbox:
  use: src.community.aio_sandbox:AioSandboxProvider
  port: 8080
  auto_start: true
  container_prefix: magic-flow-sandbox
  mounts:
    - host_path: /path/on/host
      container_path: /path/in/container
      read_only: false
```

**特点**:
- 容器隔离
- 更安�?- 适合生产

#### Kubernetes 沙箱

```yaml
sandbox:
  use: src.community.aio_sandbox:AioSandboxProvider
  provisioner_url: http://provisioner:8002
```

**要求**:
- 本地 K8s 集群（Docker Desktop / OrbStack�?- Provisioner 服务

### MCP 配置

#### stdio 类型

```json
{
  "mcpServers": {
    "server-name": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "KEY": "$ENV_VAR"
      }
    }
  }
}
```

#### HTTP/SSE 类型

```json
{
  "mcpServers": {
    "http-server": {
      "enabled": true,
      "type": "http",
      "url": "https://api.example.com/mcp",
      "oauth": {
        "enabled": true,
        "token_url": "https://auth.example.com/oauth/token",
        "grant_type": "client_credentials",
        "client_id": "$CLIENT_ID",
        "client_secret": "$CLIENT_SECRET"
      }
    }
  }
}
```

### 记忆系统配置

```yaml
memory:
  enabled: true
  max_tokens: 2000        # 最大注�?token �?  similarity_weight: 0.6  # 相似度权�?(0-1)
  confidence_weight: 0.4  # 置信度权�?(0-1)
```

**权重说明**:
- 权重之和应为 1.0
- 相似度：基于 TF-IDF 的上下文相关�?- 置信度：LLM 分配的置信度分数

### 标题生成配置

```yaml
title:
  enabled: true
  max_words: 6      # 最大词�?  max_chars: 60     # 最大字符数
  model_name: null  # null = 使用第一个模�?```

## 配置验证

### 验证配置加载

```bash
cd backend
python -c "from src.config import get_app_config; print('�?Config loaded:', get_app_config().models[0].name)"
```

### 验证 MCP 配置

```bash
python -c "from src.config import get_extensions_config; print(get_extensions_config())"
```

### 调试配置路径

```bash
python -c "
from src.config.app_config import AppConfig
print('Config path:', AppConfig.resolve_config_path())
"
```

## 配置最佳实�?
### 1. 安全存储 Secrets

```bash
# 使用环境变量，不要在配置文件中硬编码
# .env (添加�?.gitignore)
export OPENAI_API_KEY="sk-..."
```

### 2. 不同环境使用不同配置

```bash
# 开发环�?export MAGIC_FLOW_CONFIG_PATH="./config.dev.yaml"

# 生产环境
export MAGIC_FLOW_CONFIG_PATH="/etc/magic-flow/config.yaml"
```

### 3. 版本控制配置模板

```bash
# 提交模板
git add config.example.yaml

# 忽略实际配置
echo "config.yaml" >> .gitignore
```

### 4. 配置文档�?
```yaml
# config.yaml
# ============================================
# magicflow 配置文件
# 
# 环境变量:
#   - OPENAI_API_KEY: OpenAI API key
#   - ANTHROPIC_API_KEY: Anthropic API key (可�?
# 
# 文档: https://magicflow.tech/docs/config
# ============================================
```

## 故障排除

### 配置未找�?
```bash
# 检查文件位�?ls -la ../config.yaml  # 项目根目�?ls -la config.yaml     # backend 目录

# 检查环境变�?echo $MAGIC_FLOW_CONFIG_PATH
```

### 环境变量未解�?
```bash
# 确保变量已导�?export OPENAI_API_KEY="sk-..."

# 验证
env | grep OPENAI
```

### 配置验证失败

```bash
# 查看详细错误
python -c "
from src.config import get_app_config
try:
    config = get_app_config()
    print('Config valid!')
except Exception as e:
    print(f'Error: {e}')
"
```

## 相关文档

- [后端架构](./BACKEND_ARCHITECTURE.md)
- [后端开发指南](./BACKEND_DEVELOPMENT_GUIDE.md)
- [API 参考](./BACKEND_API_REFERENCE.md)
- [MCP 服务器指南](../backend/docs/MCP_SERVER.md)

