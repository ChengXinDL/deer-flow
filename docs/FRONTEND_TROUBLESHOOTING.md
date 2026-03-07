# DeerFlow 前端故障排除指南

## 开发环境问题

### 1. 安装依赖失败

**问题**: `pnpm install` 报错

**解决方案**:
```bash
# 清除缓存
pnpm store prune

# 删除 node_modules
rm -rf node_modules

# 重新安装
pnpm install
```

### 2. 端口被占用

**问题**: `Error: Port 3000 is already in use`

**解决方案**:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# 或使用其他端口
pnpm dev -- -p 3001
```

### 3. 热更新不生效

**问题**: 代码修改后页面不刷新

**解决方案**:
```bash
# 清除 Next.js 缓存
rm -rf .next

# 重启开发服务器
pnpm dev
```

### 4. 内存不足

**问题**: `JavaScript heap out of memory`

**解决方案**:
```bash
# Windows PowerShell
$env:NODE_OPTIONS="--max-old-space-size=4096"
pnpm dev
```

## 构建问题

### 1. TypeScript 类型错误

**问题**: `pnpm build` 报错类型错误

**解决方案**:
```bash
# 运行类型检查
pnpm typecheck

# 查看详细错误
pnpm typecheck 2>&1 | head -50
```

**常见类型错误**:
- 缺少类型定义: `npm install -D @types/package-name`
- 类型不兼容: 检查接口定义
- 隐式 any: 添加类型注解

### 2. ESLint 错误

**问题**: 代码风格检查失败

**解决方案**:
```bash
# 自动修复
pnpm lint:fix

# 查看错误
pnpm lint
```

### 3. 环境变量错误

**问题**: `Missing environment variable`

**解决方案**:
```bash
# 复制环境变量模板
cp .env.example .env

# 或跳过验证（Docker 构建）
SKIP_ENV_VALIDATION=1 pnpm build
```

### 4. 静态导出失败

**问题**: `Image optimization failed`

**解决方案**:
```typescript
// next.config.js
const config = {
  images: {
    unoptimized: true, // 静态导出时禁用优化
  },
};
```

## Demo 模式问题

### 1. Demo 数据无法加载

**问题**: 前端页面空白，无法显示 Demo 线程

**排查步骤**:
1. 检查环境变量配置
   ```bash
   # 查看 .env 文件
   cat frontend/.env | grep STATIC_WEBSITE_ONLY
   # 应该显示: NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true"
   ```

2. 检查前端日志
   ```bash
   # 查看请求路径
   # 应该看到: GET /mock/api/threads/search 200
   # 不应该看到: GET /api/langgraph/threads/search
   ```

3. 测试 Mock API
   ```bash
   curl http://localhost:3002/mock/api/threads/search
   # 应该返回 JSON 数组
   ```

**解决方案**:
```bash
# 1. 设置环境变量
echo 'NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true"' >> frontend/.env

# 2. 注释掉后端 URL
# NEXT_PUBLIC_BACKEND_BASE_URL="http://localhost:8001"

# 3. 重启前端服务
pnpm dev
```

### 2. 文件产物无法显示

**问题**: 图片、文档等文件无法显示，请求返回 404

**排查步骤**:
1. 检查请求路径
   ```bash
   # 错误路径（指向后端 API）
   GET /api/threads/{thread_id}/artifacts/...
   
   # 正确路径（指向 Mock API）
   GET /mock/api/threads/{thread_id}/artifacts/...
   ```

2. 测试文件产物 API
   ```bash
   curl http://localhost:3002/mock/api/threads/{thread_id}/artifacts/mnt/user-data/outputs/{filename}
   # 应该返回 200 状态码和文件内容
   ```

3. 检查文件是否存在
   ```bash
   ls frontend/public/demo/threads/{thread_id}/user-data/outputs/
   ```

**解决方案**:

修改 `frontend/src/core/artifacts/utils.ts`：

```typescript
export function urlOfArtifact({ filepath, threadId, download = false }) {
  // 关键：Demo 模式下使用 getLangGraphBaseURL()
  const baseURL = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true" 
    ? getLangGraphBaseURL()
    : getBackendBaseURL();
  
  return `${baseURL}/threads/${threadId}/artifacts${filepath}${download ? "?download=true" : ""}`;
}
```

### 3. Mock API 返回 405 错误

**问题**: 请求返回 `405 Method Not Allowed`

**原因**: Mock API 路由只实现了 POST 方法，但 LangGraph SDK 使用 GET 方法

**解决方案**:

修改 `frontend/src/app/mock/api/threads/search/route.ts`：

```typescript
// 同时支持 GET 和 POST 方法
export function GET() {
  return Response.json(getThreadData());
}

export function POST() {
  return Response.json(getThreadData());
}
```

### 4. 环境变量未生效

**问题**: 修改 `.env` 文件后，前端行为未改变

**原因**: Next.js 在启动时读取环境变量，运行时修改不会生效

**解决方案**:
```bash
# 1. 停止开发服务器（Ctrl+C）

# 2. 修改 .env 文件

# 3. 重新启动
pnpm dev
```

### 5. 文件路径映射错误

**问题**: 文件产物请求返回 404，但文件确实存在

**排查步骤**:
1. 检查路径映射逻辑
   ```typescript
   // 在 Mock API 路由中添加日志
   console.log("Original path:", artifactPath);
   console.log("Resolved path:", resolvedPath);
   console.log("File exists:", fs.existsSync(resolvedPath));
   ```

2. 验证路径格式
   ```
   请求路径: mnt/user-data/outputs/image.jpg
   实际路径: public/demo/threads/{thread_id}/user-data/outputs/image.jpg
   ```

**解决方案**:

检查 `frontend/src/app/mock/api/threads/[thread_id]/artifacts/[[...artifact_path]]/route.ts`：

```typescript
// 正确的路径映射
if (artifactPath.startsWith("mnt/")) {
  artifactPath = path.resolve(
    process.cwd(),
    artifactPath.replace("mnt/", `public/demo/threads/${threadId}/`)
  );
}
```

### 6. Demo 模式下输入框应该禁用

**问题**: Demo 模式下用户仍然可以输入内容

**验证**: 检查输入框是否显示禁用提示

```typescript
// 在 InputBox 组件中
disabled={env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true"}

// 显示提示信息
{env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true" && (
  <div className="text-muted-foreground/67 text-center text-xs">
    {t.common.notAvailableInDemoMode}
  </div>
)}
```

### 7. Demo 线程数量过多导致加载慢

**问题**: Demo 线程太多，首次加载时间过长

**解决方案**:
1. 减少线程数量
   ```bash
   # 只保留需要的 Demo 线程
   ls frontend/public/demo/threads/
   ```

2. 优化 thread.json 文件大小
   ```bash
   # 检查文件大小
   du -h frontend/public/demo/threads/*/thread.json
   
   # 如果太大，考虑分页或延迟加载
   ```

### 8. Demo 模式检查清单

在配置 Demo 模式时，按以下顺序检查：

- [ ] `.env` 文件中设置了 `NEXT_PUBLIC_STATIC_WEBSITE_ONLY="true"`
- [ ] 注释掉了 `NEXT_PUBLIC_BACKEND_BASE_URL` 和 `NEXT_PUBLIC_LANGGRAPH_BASE_URL`
- [ ] 重启了前端服务
- [ ] 日志显示请求 `/mock/api/threads/search`
- [ ] 文件产物 URL 使用了 `/mock/api/threads/{thread_id}/artifacts/...`
- [ ] Demo 线程和文件产物可以正常显示
- [ ] 输入框被禁用并显示提示信息

**相关文档**:
- [前端 Demo 模式完整指南](./FRONTEND_DEMO_MODE_GUIDE.md)
- [Demo 模式配置问题修复记录](./FRONTEND_DEMO_MODE_FIX.md)

## 运行时问题

### 1. 白屏/空白页面

**排查步骤**:
1. 检查浏览器控制台错误
2. 检查网络请求是否成功
3. 检查 React 错误边界

**常见原因**:
- 客户端组件缺少 `'use client'`
- 服务端组件使用了浏览器 API
- 无限循环导致页面卡死

### 2. API 请求失败

**问题**: 无法连接到后端

**排查步骤**:
1. 检查后端服务是否运行
   ```bash
   curl http://localhost:8001/health
   ```

2. 检查 nginx 配置
   ```bash
   nginx -t
   ```

3. 检查环境变量
   ```bash
   # 确认 .env 配置
   NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8001
   ```

**解决方案**:
```typescript
// 添加错误处理
const fetchData = async () => {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    // 显示用户友好的错误消息
    throw error;
  }
};
```

### 3. 流式响应中断

**问题**: AI 回复突然停止

**排查步骤**:
1. 检查浏览器控制台网络请求
2. 检查后端日志
3. 检查 nginx 超时配置

**解决方案**:
```nginx
# nginx.conf
proxy_read_timeout 300s;
proxy_send_timeout 300s;
```

### 4. 状态不更新

**问题**: 数据修改后 UI 不更新

**排查步骤**:
1. 检查状态更新逻辑
2. 检查组件重新渲染
3. 检查 TanStack Query 缓存

**解决方案**:
```typescript
// 强制刷新
queryClient.invalidateQueries({ queryKey: ['data'] });

// 或禁用缓存
const { data } = useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  staleTime: 0,
  cacheTime: 0,
});
```

## 性能问题

### 1. 页面加载慢

**排查工具**:
- Lighthouse
- Chrome DevTools Performance
- React DevTools Profiler

**优化方案**:
```typescript
// 1. 使用动态导入
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
});

// 2. 图片优化
import Image from 'next/image';
<Image src="/image.png" width={800} height={600} priority />

// 3. 代码分割
const module = await import('./module');
```

### 2. 内存泄漏

**症状**: 页面长时间运行后变慢

**排查方法**:
1. Chrome DevTools Memory 标签
2. 记录堆快照对比
3. 检查事件监听器

**常见原因**:
- 未清理的 setInterval/setTimeout
- 未取消的事件监听
- 未关闭的 WebSocket 连接

**解决方案**:
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    // 定时任务
  }, 1000);

  return () => {
    clearInterval(interval); // 清理
  };
}, []);
```

### 3. 渲染卡顿

**排查方法**:
- React DevTools Profiler
- Chrome DevTools Performance

**优化方案**:
```typescript
// 1. 使用 useMemo
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// 2. 使用 useCallback
const handleClick = useCallback(() => {
  doSomething();
}, []);

// 3. 虚拟列表
import { VirtualList } from '@/components/ui/virtual-list';
<VirtualList items={items} renderItem={renderItem} />
```

## 样式问题

### 1. Tailwind 类不生效

**排查步骤**:
1. 检查 Tailwind 配置
2. 检查类名拼写
3. 检查 CSS 优先级

**解决方案**:
```typescript
// 使用 cn() 工具函数
import { cn } from '@/lib/utils';

className={cn(
  'base-classes',
  condition && 'conditional-classes',
  className
)}
```

### 2. 主题切换不生效

**排查步骤**:
1. 检查 ThemeProvider 配置
2. 检查 CSS 变量
3. 检查 localStorage

**解决方案**:
```typescript
// 强制刷新主题
const { theme, setTheme } = useTheme();
setTheme('light');
setTimeout(() => setTheme('dark'), 0);
```

### 3. 响应式布局问题

**调试方法**:
```bash
# Chrome DevTools
1. 打开 DevTools
2. 按 Ctrl+Shift+M 切换设备模拟
3. 选择不同设备测试
```

## 浏览器兼容性问题

### 1. 新特性不支持

**问题**: 某些浏览器功能报错

**解决方案**:
```typescript
// 特性检测
if ('IntersectionObserver' in window) {
  // 使用 IntersectionObserver
} else {
  // 降级方案
}

// 或使用 polyfill
import 'intersection-observer';
```

### 2. CSS 兼容性问题

**解决方案**:
```css
/* 使用 autoprefixer */
.example {
  display: flex;
  -webkit-display: flex; /* 自动添加 */
}
```

## 调试技巧

### 1. 控制台调试

```typescript
// 条件断点
console.log('Debug:', data);

// 表格输出
console.table(array);

// 分组输出
console.group('Group');
console.log('Item 1');
console.log('Item 2');
console.groupEnd();

// 性能计时
console.time('operation');
// ... 操作
console.timeEnd('operation');
```

### 2. React DevTools

- 检查组件树
- 查看 Props 和 State
- 分析渲染性能
- 检查 Context

### 3. 网络调试

```bash
# 查看所有请求
# Chrome DevTools > Network

# 过滤特定请求
# 使用 Filter: domain:localhost:8001

# 查看请求详情
# 点击请求 > Headers / Payload / Preview
```

### 4. 断点调试

```typescript
// VS Code 调试配置
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "pnpm",
      "runtimeArgs": ["dev"],
      "port": 9229,
      "skipFiles": ["<node_internals>/**"]
    }
  ]
}
```

## 日志收集

### 1. 客户端日志

```typescript
// 全局错误捕获
window.onerror = (message, source, lineno, colno, error) => {
  console.error('Global Error:', { message, source, lineno, error });
  // 发送到监控系统
};

window.onunhandledrejection = (event) => {
  console.error('Unhandled Promise Rejection:', event.reason);
};
```

### 2. 服务端日志

```typescript
// 服务端组件日志
import { logger } from '@/lib/logger';

export default async function ServerComponent() {
  logger.info('Rendering server component');
  // ...
}
```

## 获取帮助

### 1. 检查文档

- [Next.js 文档](https://nextjs.org/docs)
- [React 文档](https://react.dev/)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)

### 2. 查看日志

```bash
# Docker 日志
make docker-logs

# 前端日志
make docker-logs-frontend

# 网关日志
make docker-logs-gateway
```

### 3. 社区支持

- GitHub Issues: https://github.com/bytedance/deer-flow/issues
- 官方文档: https://deerflow.tech/
