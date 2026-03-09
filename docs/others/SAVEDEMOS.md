# save-demo.js 使用文档

## 1. 脚本概述

`save-demo.js` 是一个用于保存对话线程演示的 Node.js 脚本，主要用于将特定的对话线程及其相关数据导出为演示案例。该脚本可以完整地保存对话历史、用户上传的文件和生成的输出结果�?
### 1.1 主要功能

- **获取对话历史**：从 API 获取指定线程的对话历�?- **保存线程数据**：将线程数据保存�?JSON 文件
- **复制用户数据**：复制用户上传的文件和生成的输出
- **创建演示目录**：在 `public/demo/threads/` 下创建演示目�?
### 1.2 技术栈

- **运行环境**：Node.js
- **依赖模块**：`dotenv`, `fs`, `path`, `process`
- **数据格式**：JSON
- **文件操作**：同步文件系统操�?
## 2. 使用场景

### 2.1 创建产品演示

**场景描述**：当需要展示特定的对话案例时，用于产品演示或功能展示�?
**使用时机**�?- 为客户或演示准备真实的对话示�?- 创建产品功能演示
- 展示特定功能的实际应�?- 准备营销材料

**示例**�?```bash
# 保存一个成功的对话案例作为产品演示
node save-demo.js http://localhost:3000/thread/success-case-001
```

### 2.2 保存重要对话

**场景描述**：保存有价值的对话线程，建立对话案例库�?
**使用时机**�?- 记录成功的案例或解决方案
- 保存重要的技术讨�?- 建立知识库案�?- 备份关键对话数据

**示例**�?```bash
# 保存技术讨论作为知识库案例
node save-demo.js http://localhost:3000/thread/tech-discussion-123
```

### 2.3 数据导出

**场景描述**：导出用户上传的文件和生成的输出结果�?
**使用时机**�?- 导出用户上传的文�?- 导出生成的输出结�?- 备份重要的对话数�?- 数据迁移或归�?
**示例**�?```bash
# 导出包含文件上传的对�?node save-demo.js http://localhost:3000/thread/file-upload-456
```

### 2.4 测试和验�?
**场景描述**：验证对话线程的完整性和功能正确性�?
**使用时机**�?- 验证对话线程的完整�?- 测试数据复制功能
- 检查前端演示效�?- 功能回归测试

**示例**�?```bash
# 保存测试线程验证功能
node save-demo.js http://localhost:3000/thread/test-thread-789
```

## 3. 使用方法

### 3.1 基本语法

```bash
node save-demo.js <thread_url>
```

### 3.2 参数说明

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|--------|------|------|
| `thread_url` | string | �?| 线程的完�?URL | `http://localhost:3000/thread/abc123` |

### 3.3 URL 格式要求

**本地 URL**�?```
http://localhost:3000/thread/{threadId}
http://127.0.0.1:3000/thread/{threadId}
```

**远程 URL**�?```
https://app.magicflow.com/thread/{threadId}
https://example.com/thread/{threadId}
```

### 3.4 使用示例

#### 示例 1：保存本地线�?```bash
node save-demo.js http://localhost:3000/thread/abc123
```

#### 示例 2：保存远程线�?```bash
node save-demo.js https://app.magicflow.com/thread/xyz789
```

#### 示例 3：保存带端口的线�?```bash
node save-demo.js http://localhost:8080/thread/test-thread-001
```

## 4. 生成的目录结�?
### 4.1 目录结构

执行脚本后，会创建以下目录结构：

```
public/demo/threads/{threadId}/
├── thread.json              # 线程历史数据
└── user-data/
    ├── outputs/            # 生成的输出文�?    �?  ├── file1.pdf
    �?  ├── report.docx
    �?  └── ...
    └── uploads/           # 用户上传的文�?        ├── image1.png
        ├── data.csv
        └── ...
```

### 4.2 文件说明

| 文件/目录 | 说明 | 来源 |
|-----------|------|------|
| `thread.json` | 线程的完整对话历史和元数�?| API 响应 |
| `user-data/outputs/` | Agent 生成的输出文�?| 后端线程目录 |
| `user-data/uploads/` | 用户上传的文�?| 后端线程目录 |

### 4.3 thread.json 结构

```json
{
  "values": {
    "title": "线程标题",
    "messages": [
      {
        "type": "human",
        "content": "用户消息"
      },
      {
        "type": "ai",
        "content": "AI 响应"
      }
    ]
  }
}
```

## 5. 工作流程

### 5.1 执行流程

```
1. URL 解析
   ├─ 提取 threadId
   ├─ 提取主机信息
   └─ 构建协议和端�?
2. API 调用
   ├─ 构建 API URL
   ├─ 发�?POST 请求
   └─ 接收响应数据

3. 数据保存
   ├─ 创建演示目录
   ├─ 保存 thread.json
   └─ 复制用户数据

4. 完成提示
   └─ 输出保存成功消息
```

### 5.2 详细步骤

#### 步骤 1：URL 解析
```javascript
const url = new URL(process.argv[2]);
const threadId = url.pathname.split("/").pop();
const host = url.host;
```

**功能**�?- 从命令行参数解析 URL
- 提取线程 ID（URL 路径的最后一部分�?- 提取主机信息（域名或 IP�?
#### 步骤 2：API 调用
```javascript
const apiURL = new URL(
  `/api/langgraph/threads/${threadId}/history`,
  `${url.protocol}//${host}`,
);

const response = await fetch(apiURL, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    limit: 10,
  }),
});
```

**功能**�?- 构建 API 端点 URL
- 发�?POST 请求获取线程历史
- 设置请求参数（限制获�?10 条消息）

#### 步骤 3：数据保�?```javascript
const rootPath = path.resolve(process.cwd(), "public/demo/threads", threadId);
if (fs.existsSync(rootPath)) {
  fs.rmSync(rootPath, { recursive: true });
}
fs.mkdirSync(rootPath, { recursive: true });
fs.writeFileSync(
  path.resolve(rootPath, "thread.json"),
  JSON.stringify(data, null, 2),
);
```

**功能**�?- 创建演示目录（如果已存在则删除重建）
- 保存线程数据�?JSON 文件
- 使用缩进格式�?JSON，便于阅�?
#### 步骤 4：数据复�?```javascript
const backendRootPath = path.resolve(
  process.cwd(),
  "../backend/.magic-flow/threads",
  threadId,
);
copyFolder("user-data/outputs", rootPath, backendRootPath);
copyFolder("user-data/uploads", rootPath, backendRootPath);
```

**功能**�?- 从后端线程目录复制用户数�?- 复制输出文件和上传文�?- 保持目录结构一�?
## 6. 数据来源

### 6.1 线程数据

| 属�?| �?|
|------|-----|
| **API 端点** | `/api/langgraph/threads/{threadId}/history` |
| **请求方法** | POST |
| **请求参数** | `{ limit: 10 }` |
| **返回数据** | 线程的对话历史和元数�?|
| **数据格式** | JSON |

### 6.2 用户数据

| 目录 | 后端路径 | 前端路径 |
|------|-----------|-----------|
| **输出目录** | `../backend/.magic-flow/threads/{threadId}/user-data/outputs/` | `public/demo/threads/{threadId}/user-data/outputs/` |
| **上传目录** | `../backend/.magic-flow/threads/{threadId}/user-data/uploads/` | `public/demo/threads/{threadId}/user-data/uploads/` |

## 7. 实际应用场景

### 7.1 场景 1：产品演示准�?
**需�?*：为即将到来的产品演示准备真实的对话案例�?
**步骤**�?```bash
# 1. 识别有价值的对话线程
# 2. 执行保存脚本
node save-demo.js http://localhost:3000/thread/success-case-001

# 3. 验证保存结果
ls -la public/demo/threads/success-case-001/

# 4. 检查数据完整�?cat public/demo/threads/success-case-001/thread.json
```

**预期结果**�?- 完整的对话历�?- 所有相关的输出文件
- 用户上传的所有文�?
### 7.2 场景 2：客户案例展�?
**需�?*：将客户的成功对话作为案例展示�?
**步骤**�?```bash
# 1. 获取客户对话线程 URL
# 2. 保存客户对话
node save-demo.js https://app.magicflow.com/thread/client-demo-123

# 3. 检查生成的目录结构
tree public/demo/threads/client-demo-123/

# 4. 准备展示材料
```

**预期结果**�?- 客户真实对话案例
- 完整的交互记�?- 可用于营销和展�?
### 7.3 场景 3：功能测试验�?
**需�?*：测试新功能的完整性和数据正确性�?
**步骤**�?```bash
# 1. 创建测试对话
# 2. 保存测试线程
node save-demo.js http://localhost:3000/thread/test-thread-456

# 3. 验证数据复制
ls -la public/demo/threads/test-thread-456/user-data/outputs/
ls -la public/demo/threads/test-thread-456/user-data/uploads/

# 4. 检�?JSON 格式
cat public/demo/threads/test-thread-456/thread.json | jq .
```

**预期结果**�?- 验证功能正确�?- 检查数据完整�?- 确认文件复制成功

## 8. 注意事项

### 8.1 API 可用�?
- **检�?API 端点**：确�?`/api/langgraph/threads/{threadId}/history` 可访�?- **网络连接**：确保能够连接到指定的主机和端口
- **认证要求**：如果需要认证，确保提供正确的凭�?
### 8.2 权限要求

- **文件系统权限**：需要有创建和写入目录的权限
- **API 访问权限**：需要有访问线程历史和用户数据的权限
- **跨目录访�?*：确保脚本可以访问后端和前端目录

### 8.3 路径配置

- **相对路径**：脚本使用相对路径，确保从正确的目录运行
- **后端路径**：`../backend/.magic-flow/threads/` 必须存在
- **前端路径**：`public/demo/threads/` 会自动创�?
### 8.4 数据完整�?
- **数据验证**：检查复制的数据是否完整
- **文件检�?*：确保所有文件都已复�?- **JSON 验证**：验�?JSON 格式是否正确

### 8.5 错误处理

- **无数据情�?*：如�?API 返回空数据，脚本会输出错误信�?- **目录冲突**：如果目标目录已存在，会被删除重�?- **文件缺失**：如果后端数据不存在，相应的目录不会被创�?
## 9. 验证步骤

### 9.1 检查目录结�?
```bash
# 检查生成的目录
ls -la public/demo/threads/{threadId}/

# 查看目录树结�?tree public/demo/threads/{threadId}/
```

### 9.2 验证线程数据

```bash
# 查看 JSON 内容
cat public/demo/threads/{threadId}/thread.json

# 使用 jq 格式化输�?cat public/demo/threads/{threadId}/thread.json | jq .

# 检�?JSON 语法
python -m json.tool public/demo/threads/{threadId}/thread.json
```

### 9.3 检查用户数�?
```bash
# 检查输出文�?ls -la public/demo/threads/{threadId}/user-data/outputs/

# 检查上传文�?ls -la public/demo/threads/{threadId}/user-data/uploads/

# 统计文件数量
find public/demo/threads/{threadId}/user-data/ -type f | wc -l
```

### 9.4 验证数据完整�?
```bash
# 比较文件数量
echo "后端输出文件: $(ls ../backend/.magic-flow/threads/{threadId}/user-data/outputs/ | wc -l)"
echo "前端输出文件: $(ls public/demo/threads/{threadId}/user-data/outputs/ | wc -l)"

# 检查文件大�?du -sh public/demo/threads/{threadId}/
```

## 10. 集成到工作流

### 10.1 自动化脚�?
**场景**：在 CI/CD 流程中自动保存演示�?
**实现**�?```bash
# �?CI/CD 流程中添�?- name: Save Demo Threads
  run: |
    node frontend/scripts/save-demo.js $THREAD_URL
  env:
    THREAD_URL: ${{ secrets.THREAD_URL }}
```

### 10.2 定期备份

**场景**：定期保存重要的对话线程�?
**实现**�?```bash
# 创建定时任务
# crontab 示例（每天凌�?2 点执行）
0 2 * * * cd /path/to/project && node frontend/scripts/save-demo.js http://localhost:3000/thread/backup-thread-$(date +\%Y\%m\%d)
```

### 10.3 案例管理

**场景**：建立对话案例管理系统�?
**实现**�?```bash
# 创建案例管理脚本
#!/bin/bash
CASES=("case-001" "case-002" "case-003")
for case in "${CASES[@]}"; do
  node frontend/scripts/save-demo.js "http://localhost:3000/thread/$case"
done
```

### 10.4 演示更新

**场景**：定期更新前端演示内容�?
**实现**�?```bash
# 创建更新脚本
#!/bin/bash
# 清理旧演�?rm -rf public/demo/threads/*
# 保存新演�?node frontend/scripts/save-demo.js $1
# 通知更新完成
echo "Demo updated: $1"
```

## 11. 故障排除

### 11.1 常见错误

#### 错误 1：No data found
```
No data found
```

**原因**：API 返回空数据或线程不存�?
**解决方案**�?- 检查线�?URL 是否正确
- 验证线程是否存在
- 检�?API 端点是否可用

#### 错误 2：Cannot find module
```
Error: Cannot find module 'dotenv'
```

**原因**：缺少依赖模�?
**解决方案**�?```bash
# 安装依赖
npm install dotenv

# 或使�?yarn
yarn add dotenv
```

#### 错误 3：EACCES: permission denied
```
Error: EACCES: permission denied, mkdir 'public/demo/threads/...'
```

**原因**：文件系统权限不�?
**解决方案**�?```bash
# 修改目录权限
chmod 755 public/demo/threads/

# 或使�?sudo（不推荐�?sudo node frontend/scripts/save-demo.js $URL
```

### 11.2 调试技�?
#### 启用详细日志
```javascript
// 在脚本中添加日志
console.log("URL:", url);
console.log("Thread ID:", threadId);
console.log("API URL:", apiURL);
console.log("Response:", data);
```

#### 检查网络请�?```bash
# 使用 curl 测试 API
curl -X POST http://localhost:3000/api/langgraph/threads/test-thread/history \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

#### 验证文件路径
```bash
# 检查后端路径是否存�?ls -la ../backend/magic-floww/threads/

# 检查前端目录权�?ls -la public/demo/
```

## 12. 最佳实�?
### 12.1 命名规范

- **线程 ID**：使用有意义的命名（�?`success-case-001`�?- **演示目录**：保持一致的命名风格
- **文件组织**：按类别或时间组织演�?
### 12.2 数据管理

- **定期清理**：定期清理过时的演示数据
- **版本控制**：将重要的演示加入版本控�?- **文档记录**：为每个演示创建说明文档

### 12.3 安全考虑

- **敏感数据**：避免保存包含敏感信息的对话
- **访问控制**：限制对演示目录的访问权�?- **数据脱敏**：必要时对数据进行脱敏处�?
### 12.4 性能优化

- **批量处理**：批量保存多个线程以提高效率
- **增量更新**：只更新变化的部�?- **缓存策略**：缓�?API 响应以减少重复请�?
## 13. 总结

`save-demo.js` 是一个强大的工具，用于保存和管理对话线程演示。通过合理使用此脚本，可以�?
- **创建产品演示**：为产品展示准备真实案例
- **保存重要对话**：建立对话案例库
- **导出用户数据**：备份和迁移对话数据
- **验证功能正确�?*：测试和验证系统功能

遵循本文档的指导，可以最大化地发挥此脚本的价值，提高工作效率和数据管理质量�?
---

**版本**�?.0
**更新时间**�?026-03-08
**适用范围**：MAGICFlow 前端演示管理
**维护责任�?*：Frontend Team
