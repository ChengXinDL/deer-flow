# DeerFlow 前端组件目录

## 组件概览

本文档列出 DeerFlow 前端的所有组件，包括来源、用途和使用方式。

---

## 一、UI 基础组件 (components/ui/)

这些组件来自 **Shadcn UI**，提供基础 UI 元素。

### 布局组件

| 组件 | 说明 | 来源 |
|------|------|------|
| `sidebar.tsx` | 侧边栏布局 | Shadcn |
| `resizable.tsx` | 可调整大小面板 | Shadcn |
| `scroll-area.tsx` | 滚动区域 | Shadcn |
| `separator.tsx` | 分隔线 | Shadcn |
| `card.tsx` | 卡片容器 | Shadcn |

### 表单组件

| 组件 | 说明 | 来源 |
|------|------|------|
| `button.tsx` | 按钮 | Shadcn |
| `button-group.tsx` | 按钮组 | Shadcn |
| `input.tsx` | 输入框 | Shadcn |
| `textarea.tsx` | 文本域 | Shadcn |
| `select.tsx` | 下拉选择 | Shadcn |
| `switch.tsx` | 开关 | Shadcn |
| `toggle.tsx` | 切换按钮 | Shadcn |
| `toggle-group.tsx` | 切换按钮组 | Shadcn |
| `checkbox.tsx` | 复选框 | Shadcn |
| `radio-group.tsx` | 单选组 | Shadcn |
| `slider.tsx` | 滑块 | Shadcn |
| `command.tsx` | 命令面板 | Shadcn |

### 反馈组件

| 组件 | 说明 | 来源 |
|------|------|------|
| `alert.tsx` | 警告提示 | Shadcn |
| `dialog.tsx` | 对话框 | Shadcn |
| `sheet.tsx` | 侧边抽屉 | Shadcn |
| `toast.tsx` | 轻提示 | Shadcn |
| `sonner.tsx` | 通知 | Shadcn |
| `skeleton.tsx` | 骨架屏 | Shadcn |
| `progress.tsx` | 进度条 | Shadcn |
| `tooltip.tsx` | 工具提示 | Shadcn |
| `hover-card.tsx` | 悬停卡片 | Shadcn |
| `popover.tsx` | 弹出层 | Shadcn |

### 导航组件

| 组件 | 说明 | 来源 |
|------|------|------|
| `breadcrumb.tsx` | 面包屑 | Shadcn |
| `tabs.tsx` | 标签页 | Shadcn |
| `dropdown-menu.tsx` | 下拉菜单 | Shadcn |
| `navigation-menu.tsx` | 导航菜单 | Shadcn |
| `pagination.tsx` | 分页 | Shadcn |

### 数据展示

| 组件 | 说明 | 来源 |
|------|------|------|
| `avatar.tsx` | 头像 | Shadcn |
| `badge.tsx` | 徽章 | Shadcn |
| `table.tsx` | 表格 | Shadcn |
| `collapsible.tsx` | 可折叠 | Shadcn |
| `accordion.tsx` | 手风琴 | Shadcn |
| `carousel.tsx` | 轮播 | Shadcn |
| `calendar.tsx` | 日历 | Shadcn |

---

## 二、AI 元素组件 (components/ai-elements/)

这些组件来自 **Vercel AI SDK Elements**，专门用于 AI 对话界面。

### 核心对话组件

| 组件 | 说明 | 用途 |
|------|------|------|
| `conversation.tsx` | 对话容器 | 整体对话布局 |
| `message.tsx` | 消息项 | 单条消息展示 |
| `prompt-input.tsx` | 输入框 | 用户输入区域 |
| `suggestion.tsx` | 建议提示 | 输入建议 |
| `sources.tsx` | 来源引用 | 消息来源展示 |

### 推理与思考组件

| 组件 | 说明 | 用途 |
|------|------|------|
| `reasoning.tsx` | 推理过程 | 展示 AI 推理 |
| `chain-of-thought.tsx` | 思维链 | 步骤化思考 |
| `plan.tsx` | 计划展示 | 任务计划 |
| `context.tsx` | 上下文 | 对话上下文 |

### 工件与代码组件

| 组件 | 说明 | 用途 |
|------|------|------|
| `artifact.tsx` | 工件展示 | 文件/代码展示 |
| `code-block.tsx` | 代码块 | 代码高亮 |
| `canvas.tsx` | 画布 | 可视化编辑 |
| `web-preview.tsx` | 网页预览 | 预览生成的网页 |

### 流程与节点组件

| 组件 | 说明 | 用途 |
|------|------|------|
| `node.tsx` | 节点 | 流程图节点 |
| `edge.tsx` | 边 | 流程图连线 |
| `connection.tsx` | 连接 | 节点连接 |
| `panel.tsx` | 面板 | 属性面板 |
| `controls.tsx` | 控制 | 画布控制 |

### 任务与状态组件

| 组件 | 说明 | 用途 |
|------|------|------|
| `task.tsx` | 任务项 | 任务展示 |
| `queue.tsx` | 队列 | 任务队列 |
| `checkpoint.tsx` | 检查点 | 状态检查点 |
| `loader.tsx` | 加载器 | 加载状态 |
| `shimmer.tsx` | 闪烁效果 | 加载动画 |

### 工具组件

| 组件 | 说明 | 用途 |
|------|------|------|
| `toolbar.tsx` | 工具栏 | 操作工具栏 |
| `model-selector.tsx` | 模型选择 | 切换 AI 模型 |
| `image.tsx` | 图片 | 图片展示 |
| `open-in-chat.tsx` | 在聊天中打开 | 跳转链接 |

---

## 三、工作区组件 (components/workspace/)

这些组件是 DeerFlow 自定义的业务组件。

### 布局组件

| 组件 | 说明 | 文件 |
|------|------|------|
| `workspace-container.tsx` | 工作区容器 | workspace-container.tsx |
| `workspace-header.tsx` | 顶部导航 | workspace-header.tsx |
| `workspace-sidebar.tsx` | 侧边栏 | workspace-sidebar.tsx |
| `workspace-nav-menu.tsx` | 导航菜单 | workspace-nav-menu.tsx |
| `workspace-nav-chat-list.tsx` | 聊天列表导航 | workspace-nav-chat-list.tsx |
| `overscroll.tsx` | 滚动处理 | overscroll.tsx |

### 消息组件

| 组件 | 说明 | 文件 |
|------|------|------|
| `message-list.tsx` | 消息列表 | messages/message-list.tsx |
| `message-list-item.tsx` | 消息项 | messages/message-list-item.tsx |
| `message-group.tsx` | 消息组 | messages/message-group.tsx |
| `markdown-content.tsx` | Markdown 内容 | messages/markdown-content.tsx |
| `subtask-card.tsx` | 子任务卡片 | messages/subtask-card.tsx |
| `skeleton.tsx` | 消息骨架屏 | messages/skeleton.tsx |
| `streaming-indicator.tsx` | 流式指示器 | streaming-indicator.tsx |

### 工件组件

| 组件 | 说明 | 文件 |
|------|------|------|
| `artifact-file-list.tsx` | 工件文件列表 | artifacts/artifact-file-list.tsx |
| `artifact-file-detail.tsx` | 工件详情 | artifacts/artifact-file-detail.tsx |
| `context.tsx` | 工件上下文 | artifacts/context.tsx |
| `code-editor.tsx` | 代码编辑器 | code-editor.tsx |

### 设置组件

| 组件 | 说明 | 文件 |
|------|------|------|
| `settings-dialog.tsx` | 设置对话框 | settings/settings-dialog.tsx |
| `settings-section.tsx` | 设置区块 | settings/settings-section.tsx |
| `about-settings-page.tsx` | 关于页面 | settings/about-settings-page.tsx |
| `appearance-settings-page.tsx` | 外观设置 | settings/appearance-settings-page.tsx |
| `memory-settings-page.tsx` | 记忆设置 | settings/memory-settings-page.tsx |
| `notification-settings-page.tsx` | 通知设置 | settings/notification-settings-page.tsx |
| `skill-settings-page.tsx` | 技能设置 | settings/skill-settings-page.tsx |
| `tool-settings-page.tsx` | 工具设置 | settings/tool-settings-page.tsx |

### 输入组件

| 组件 | 说明 | 文件 |
|------|------|------|
| `input-box.tsx` | 输入框 | input-box.tsx |
| `copy-button.tsx` | 复制按钮 | copy-button.tsx |
| `flip-display.tsx` | 翻转显示 | flip-display.tsx |
| `mode-hover-guide.tsx` | 模式悬停引导 | mode-hover-guide.tsx |

### 其他组件

| 组件 | 说明 | 文件 |
|------|------|------|
| `recent-chat-list.tsx` | 最近聊天列表 | recent-chat-list.tsx |
| `thread-title.tsx` | 线程标题 | thread-title.tsx |
| `todo-list.tsx` | 待办列表 | todo-list.tsx |
| `welcome.tsx` | 欢迎页 | welcome.tsx |
| `citation-link.tsx` | 引用链接 | citations/citation-link.tsx |
| `github-icon.tsx` | GitHub 图标 | github-icon.tsx |

---

## 四、落地页组件 (components/landing/)

这些组件用于项目落地页展示。

### 页面区块

| 组件 | 说明 | 文件 |
|------|------|------|
| `hero.tsx` | 主视觉区 | hero.tsx |
| `header.tsx` | 页头 | header.tsx |
| `footer.tsx` | 页脚 | footer.tsx |
| `section.tsx` | 通用区块 | section.tsx |

### 特色区块

| 组件 | 说明 | 文件 |
|------|------|------|
| `case-study-section.tsx` | 案例展示 | sections/case-study-section.tsx |
| `community-section.tsx` | 社区区块 | sections/community-section.tsx |
| `sandbox-section.tsx` | 沙箱介绍 | sections/sandbox-section.tsx |
| `skills-section.tsx` | 技能展示 | sections/skills-section.tsx |
| `whats-new-section.tsx` | 新功能介绍 | sections/whats-new-section.tsx |

### 动画组件

| 组件 | 说明 | 文件 |
|------|------|------|
| `progressive-skills-animation.tsx` | 技能渐进动画 | progressive-skills-animation.tsx |

---

## 五、MagicUI 特效组件

这些组件来自 **MagicUI**，提供视觉特效。

| 组件 | 说明 | 文件 |
|------|------|------|
| `aurora-text.tsx` | 极光文字效果 | ui/aurora-text.tsx |
| `flickering-grid.tsx` | 闪烁网格 | ui/flickering-grid.tsx |
| `galaxy.tsx` | 星系背景 | ui/galaxy.tsx |
| `magic-bento.tsx` | 魔法 Bento 网格 | ui/magic-bento.tsx |
| `number-ticker.tsx` | 数字滚动 | ui/number-ticker.tsx |
| `shine-border.tsx` | 发光边框 | ui/shine-border.tsx |
| `spotlight-card.tsx` | 聚光灯卡片 | ui/spotlight-card.tsx |
| `terminal.tsx` | 终端模拟 | ui/terminal.tsx |
| `word-rotate.tsx` | 文字旋转 | ui/word-rotate.tsx |
| `confetti-button.tsx` | 彩纸按钮 | ui/confetti-button.tsx |

---

## 六、自定义 Hooks

### 线程相关

| Hook | 说明 | 文件 |
|------|------|------|
| `useThreadStream` | 线程流式传输 | core/threads/hooks.ts |
| `useSubmitThread` | 提交线程消息 | core/threads/hooks.ts |
| `useThreads` | 线程列表管理 | core/threads/hooks.ts |

### 工件相关

| Hook | 说明 | 文件 |
|------|------|------|
| `useArtifacts` | 工件管理 | core/artifacts/hooks.ts |
| `useArtifactLoader` | 工件加载 | core/artifacts/loader.ts |

### 设置相关

| Hook | 说明 | 文件 |
|------|------|------|
| `useSettings` | 用户设置 | core/settings/hooks.ts |
| `useLocalSettings` | 本地设置 | core/settings/local.ts |

### 国际化

| Hook | 说明 | 文件 |
|------|------|------|
| `useI18n` | 国际化 | core/i18n/hooks.ts |

### 其他

| Hook | 说明 | 文件 |
|------|------|------|
| `useModels` | 模型管理 | core/models/hooks.ts |
| `useSkills` | 技能管理 | core/skills/hooks.ts |
| `useMCP` | MCP 集成 | core/mcp/hooks.ts |
| `useMemory` | 记忆系统 | core/memory/hooks.ts |
| `useUploads` | 文件上传 | core/uploads/hooks.ts |
| `useNotification` | 通知 | core/notification/hooks.ts |

---

## 七、使用示例

### 基础 UI 组件

```tsx
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>标题</CardTitle>
      </CardHeader>
      <CardContent>
        <Button>点击我</Button>
      </CardContent>
    </Card>
  );
}
```

### AI 元素组件

```tsx
import { Message } from '@/components/ai-elements/message';
import { Conversation } from '@/components/ai-elements/conversation';

function ChatPage() {
  return (
    <Conversation>
      {messages.map(msg => (
        <Message key={msg.id} content={msg.content} role={msg.role} />
      ))}
    </Conversation>
  );
}
```

### 工作区组件

```tsx
import { WorkspaceContainer } from '@/components/workspace/workspace-container';
import { MessageList } from '@/components/workspace/messages/message-list';

function WorkspacePage() {
  return (
    <WorkspaceContainer>
      <MessageList threadId={threadId} />
    </WorkspaceContainer>
  );
}
```

---

## 八、组件开发指南

### 创建新组件

1. 确定组件类别（ui/ai-elements/workspace/landing）
2. 在对应目录创建文件
3. 遵循命名规范：`kebab-case.tsx`
4. 导出组件：`export function ComponentName() {}`

### 组件模板

```tsx
'use client'; // 如需客户端交互

import { cn } from '@/lib/utils';

interface MyComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export function MyComponent({ className, children }: MyComponentProps) {
  return (
    <div className={cn('base-classes', className)}>
      {children}
    </div>
  );
}
```

### 注意事项

- `components/ui/` 和 `components/ai-elements/` 是自动生成的，不要手动修改
- 业务组件放在 `components/workspace/` 或 `components/landing/`
- 使用 `cn()` 工具函数处理类名
- 优先使用服务端组件，需要交互时添加 `'use client'`
