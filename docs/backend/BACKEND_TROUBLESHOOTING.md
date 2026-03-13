# magicflow 后端故障排除指南

## 环境配置问题

### 1. Python 版本不兼�?
**问题**: `requires-python: >=3.12`

**解决方案**:
```bash
# 检�?Python 版本
python --version  # 需�?3.12+

# 使用 pyenv 安装 Python 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# 或使�?uv 管理 Python
uv python install 3.12
uv python use 3.12
```

### 2. uv 安装失败

**问题**: `command not found: uv`

**解决方案**:
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

### 3. 依赖安装失败

**问题**: `make install` 报错

**解决方案**:
```bash
# 清除 uv 缓存
uv cache clean

# 删除虚拟环境
rm -rf .venv

# 重新安装
make install

# 或使�?uv 直接安装
uv sync
```

### 4. 配置文件未找�?
**问题**: `Config file not found`

**解决方案**:
```bash
# 1. 确保在项目根目录
cd magic-flow

# 2. 复制配置模板
cp config.example.yaml config.yaml

# 3. 验证配置位置
ls -la config.yaml

# 4. 检查配置加�?python -c "from src.config import get_app_config; print(get_app_config())"
```

### 5. 环境变量未解�?
**问题**: API key 未生�?
**解决方案**:
```bash
# 检查环境变�?env | grep OPENAI

# 确保变量已导�?export OPENAI_API_KEY="sk-..."

# 验证配置中的变量替换
python -c "
import os
from src.config import get_app_config
config = get_app_config()
print(config.models[0].api_key)  # 应该显示实际 key，不�?$OPENAI_API_KEY
"
```

## 启动问题

### 1. LangGraph 服务器启动失�?
**问题**: `make dev` 报错

**排查步骤**:
```bash
# 检查端口占�?lsof -i :2024  # macOS/Linux
netstat -ano | findstr :2024  # Windows

# 检查配置文�?python -c "from src.config import get_app_config; print('Config OK')"

# 检�?langgraph.json
cat langgraph.json

# 手动启动查看详细错误
uv run langgraph dev --no-browser
```

**常见错误**:
- `ModuleNotFoundError`: 依赖未安装，运行 `make install`
- `ImportError`: 检�?Python 路径
- `Address already in use`: 端口被占用，关闭其他实例

### 2. Gateway API 启动失败

**问题**: `make gateway` 报错

**排查步骤**:
```bash
# 检查端口占�?lsof -i :8001

# 手动启动
uv run uvicorn src.gateway.app:app --host 0.0.0.0 --port 8001 --reload

# 查看详细错误
```

### 3. 端口冲突

**解决方案**:
```bash
# 查找占用进程
# macOS/Linux
lsof -i :2024
kill -9 <PID>

# Windows
netstat -ano | findstr :2024
taskkill /PID <PID> /F

# 或使用不同端�?# 修改 Makefile 或手动指�?uv run langgraph dev --port 2025
```

## 运行时问�?
### 1. Agent 执行失败

**问题**: Agent 不响应或报错

**排查步骤**:

1. **检查模型配�?*:
```bash
python -c "
from src.config import get_app_config
config = get_app_config()
print('Models:', [m.name for m in config.models])
print('First model:', config.models[0])
"
```

2. **检�?API Key**:
```bash
# 测试 API 连接
python -c "
from src.models.factory import create_chat_model
from src.config import get_app_config
config = get_app_config()
model = create_chat_model(config.models[0])
response = model.invoke('Hello')
print(response)
"
```

3. **检查日�?*:
```bash
# 查看详细日志
export LOG_LEVEL=DEBUG
make dev
```

### 2. 沙箱执行失败

**问题**: `bash` 或文件操作报�?
**排查步骤**:

1. **检查沙箱配�?*:
```yaml
# config.yaml
sandbox:
  use: src.sandbox.local:LocalSandboxProvider  # 开发环�?  # use: src.community.aio_sandbox:AioSandboxProvider  # Docker
```

2. **检查目录权�?*:
```bash
# 检查线程目�?ls -la backend/magic-floww/threads/

# 修复权限
chmod -R 755 backend/.magic-flow/
```

3. **测试沙箱**:
```python
python -c "
from src.sandbox.local import LocalSandboxProvider
provider = LocalSandboxProvider()
sandbox = provider.acquire('test-thread')
result = sandbox.execute_command('echo hello')
print(result)
"
```

### 3. MCP 连接失败

**问题**: MCP 工具不可�?
**排查步骤**:

1. **检�?MCP 配置**:
```bash
cat extensions_config.json
```

2. **测试 MCP 服务�?*:
```bash
# 手动测试 stdio 类型�?MCP
npx -y @modelcontextprotocol/server-github

# 检查环境变�?echo $GITHUB_TOKEN
```

3. **查看 MCP 日志**:
```bash
# 启用调试日志
export MCP_DEBUG=1
make dev
```

### 4. 记忆系统不工�?
**问题**: 记忆未注入或更新

**排查步骤**:

1. **检查记忆配�?*:
```yaml
# config.yaml
memory:
  enabled: true
  max_tokens: 2000
```

2. **检查记忆文�?*:
```bash
# 查看记忆存储位置
ls -la backend/.magic-flow/memory/

# 查看记忆内容
cat backend/.magic-flow/memory/{user_id}.json
```

3. **测试记忆提取**:
```python
python -c "
from src.agents.memory.updater import extract_memory
memory = extract_memory('User likes Python')
print(memory)
"
```

### 5. �?Agent 执行失败

**问题**: `task()` 工具报错

**排查步骤**:

1. **检查并发限�?*:
```yaml
# config.yaml
subagents:
  enabled: true
  max_concurrent: 3
```

2. **检查子 Agent 日志**:
```bash
# 查看�?Agent 执行日志
tail -f backend/.magic-flow/logs/subagents.log
```

3. **测试�?Agent**:
```python
python -c "
from src.subagents.executor import SubagentExecutor
executor = SubagentExecutor()
result = executor.execute('bash', 'echo hello')
print(result)
"
```

## API 问题

### 1. API 返回 404

**问题**: 端点不存�?
**排查步骤**:

1. **检查路由配�?*:
```python
# 查看注册的路�?python -c "
from src.gateway.app import app
for route in app.routes:
    print(route.path)
"
```

2. **检�?URL 路径**:
```bash
# LangGraph API
curl http://localhost:2026/api/langgraph/threads

# Gateway API
curl http://localhost:2026/api/models
```

### 2. API 返回 500

**问题**: 服务器内部错�?
**排查步骤**:

1. **查看服务器日�?*:
```bash
# LangGraph 日志
make dev  # 查看控制台输�?
# Gateway 日志
make gateway  # 查看控制台输�?```

2. **检查堆栈跟�?*:
```python
# 在代码中添加详细日志
import traceback
try:
    # 你的代码
    pass
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
```

### 3. CORS 错误

**问题**: 跨域请求被阻�?
**解决方案**:
```bash
# 检�?nginx 配置
cat docker/nginx/nginx.local.conf

# 确保 CORS 头正�?# 通常是前端端口不匹配导致�?```

## 性能问题

### 1. 响应缓慢

**排查步骤**:

1. **检查模型响应时�?*:
```bash
# 测试模型 API 延迟
python -c "
import time
from src.models.factory import create_chat_model
model = create_chat_model(...)
start = time.time()
model.invoke('Hello')
print(f'Latency: {time.time() - start}s')
"
```

2. **检查中间件执行时间**:
```python
# 在中间件中添加计�?import time

class TimedMiddleware:
    def before_model(self, state, config):
        start = time.time()
        # ...
        print(f"Middleware took: {time.time() - start}s")
        return state
```

3. **启用 LangSmith 追踪**:
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-key
```

### 2. 内存泄漏

**排查步骤**:

1. **监控内存使用**:
```bash
# macOS
vm_stat

# Linux
free -h

# 或使�?Python
python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024} MB')
"
```

2. **检查线程状态累�?*:
```bash
# 清理旧线�?rm -rf backend/magic-floww/threads/old-thread-id
```

### 3. Token 消耗过�?
**排查步骤**:

1. **检查消息历史长�?*:
```python
# �?ThreadState 中检�?print(f"Messages: {len(state['messages'])}")
```

2. **启用摘要功能**:
```yaml
# config.yaml
summarization:
  enabled: true
  max_tokens: 8000
```

## 调试技�?
### 1. 启用详细日志

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 启动服务
make dev
```

### 2. 使用 LangSmith 追踪

```bash
# 配置环境变量
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls-...
export LANGCHAIN_PROJECT=magic-flow-debug

# 查看追踪
# 访问 https://smith.langchain.com
```

### 3. 检查线程状�?
```python
# 获取线程状�?python -c "
from langgraph import Client
client = Client(api_url='http://localhost:2024')
state = client.threads.get_state('thread-id')
print(state)
"
```

### 4. 测试单个组件

```python
# 测试模型
python -c "
from src.models.factory import create_chat_model
model = create_chat_model(...)
print(model.invoke('test'))
"

# 测试工具
python -c "
from src.sandbox.tools import bash_tool
print(bash_tool.invoke({'command': 'echo hello'}))
"

# 测试中间�?python -c "
from src.agents.middlewares.memory_middleware import MemoryMiddleware
m = MemoryMiddleware()
print(m.before_model({'messages': []}, {}))
"
```

### 5. 使用 PDB 调试

```python
# 在代码中插入断点
import pdb; pdb.set_trace()

# 常用命令
# n - 下一�?# s - 进入函数
# c - 继续执行
# p variable - 打印变量
# l - 显示代码
```

## 常见问题 FAQ

### Q: 如何重置所有数据？

A:
```bash
# 停止服务
make stop

# 删除数据目录
rm -rf backend/.magic-flow/

# 重新启动
make dev
```

### Q: 如何更新依赖�?
A:
```bash
# 更新 pyproject.toml 中的版本
# 然后运行
make install

# 或更新所有依�?uv sync --upgrade
```

### Q: 如何添加新的 LLM 提供商？

A:
1. 安装提供商的 LangChain �?2. �?`config.yaml` 中添加模型配�?3. �?`src/models/factory.py` 中添加支�?
### Q: 如何备份配置�?
A:
```bash
# 备份配置
cp config.yaml config.yaml.backup
cp extensions_config.json extensions_config.json.backup

# 备份数据
tar -czvf magic-flow-backup.tar.gz backend/.magic-flow/
```

### Q: 如何查看所有可用的工具�?
A:
```python
python -c "
from src.config import get_app_config
config = get_app_config()
for tool in config.tools:
    print(f'{tool.name}: {tool.use}')
"
```

## 获取帮助

### 1. 查看日志

```bash
# LangGraph 日志
make dev 2>&1 | tee langgraph.log

# Gateway 日志
make gateway 2>&1 | tee gateway.log
```

### 2. 检查系统状�?
```bash
# 检查端�?netstat -tuln | grep -E '2024|8001|2026'

# 检查进�?ps aux | grep -E 'langgraph|uvicorn|nginx'

# 检查磁盘空�?df -h
```

### 3. 社区支持

- GitHub Issues: https://github.com/bytedance/magic-flow/issues
- 官方文档: https://magicflow.tech/
- LangGraph 文档: https://langchain-ai.github.io/langgraph/

---

## 快速诊断清�?
遇到问题时，按顺序检查：

1. [ ] Python 版本 >= 3.12
2. [ ] uv 已安�?3. [ ] 依赖已安�?(`make install`)
4. [ ] 配置文件存在 (`config.yaml`)
5. [ ] 环境变量已设�?(`env | grep API_KEY`)
6. [ ] 端口未被占用
7. [ ] 服务已启�?(`make dev` / `make gateway`)
8. [ ] 日志无错�?9. [ ] API 可访�?(`curl http://localhost:2026/api/models`)

