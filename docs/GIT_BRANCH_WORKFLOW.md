# Git 分支工作流指南

## 分支说明

- **main**: 上游主分支，跟踪官方仓库的更新
- **local-integrate**: 本地集成分支，包含您的自定义修改和文档

## 将 main 更新合并到 local-integrate

当 main 分支有新的更新时，您可以将这些更新合并到 local-integrate 分支。

### 方法 1：使用 merge（推荐）

```bash
# 1. 确保您在 local-integrate 分支
git checkout local-integrate

# 2. 获取远程最新更新
git fetch origin

# 3. 将 main 的更新合并到当前分支
git merge origin/main

# 4. 如果有冲突，解决冲突后提交
# 编辑冲突文件...
git add -A
git commit -m "merge: 将 main 分支更新合并到 local-integrate"
```

### 方法 2：使用 rebase（历史更整洁）

```bash
# 1. 确保您在 local-integrate 分支
git checkout local-integrate

# 2. 获取远程最新更新
git fetch origin

# 3. 将当前分支变基到最新的 main
git rebase origin/main

# 4. 如果有冲突，解决冲突后继续
# 编辑冲突文件...
git add -A
git rebase --continue
```

**注意**: Rebase 会重写提交历史，如果已将 local-integrate 推送到远程，不建议使用 rebase。

## 完整工作流示例

### 场景：main 有更新，需要同步到 local-integrate

```bash
# 步骤 1: 切换到 local-integrate 分支
git checkout local-integrate

# 步骤 2: 查看当前状态
git status

# 步骤 3: 获取远程更新
git fetch origin

# 步骤 4: 查看 main 分支的新提交
git log local-integrate..origin/main --oneline

# 步骤 5: 合并更新
git merge origin/main

# 步骤 6: 解决冲突（如果有）
# - 打开冲突文件
# - 查找 <<<<<<< HEAD 标记
# - 保留需要的更改
# - 删除冲突标记

# 步骤 7: 提交合并
git add -A
git commit -m "merge: 同步 main 分支更新"

# 步骤 8: 验证
git log --oneline --graph -10
```

## 冲突解决指南

### 常见冲突场景

#### 1. 文档文件冲突
如果官方也修改了文档，您需要决定：
- 保留官方版本
- 保留您的版本
- 合并两者

```bash
# 查看冲突文件
git status

# 编辑冲突文件，解决冲突
# 然后标记为已解决
git add <冲突文件>

# 完成合并
git commit -m "merge: 解决文档冲突"
```

#### 2. 代码文件冲突
如果官方修改了您也修改过的代码：

```bash
# 查看冲突详情
git diff

# 编辑文件解决冲突
# 确保功能正常

# 测试更改
# ...

# 提交
git add -A
git commit -m "merge: 解决代码冲突并测试"
```

## 自动化脚本

您可以创建一个脚本来简化更新流程：

```bash
#!/bin/bash
# update-from-main.sh

echo "🔄 更新 local-integrate 分支..."

# 保存当前更改
git stash

# 切换到 local-integrate
git checkout local-integrate

# 获取远程更新
git fetch origin

# 合并 main 更新
git merge origin/main

# 恢复保存的更改
git stash pop

echo "✅ 更新完成！"
```

## 最佳实践

### 1. 定期同步
- 建议每天或每周同步一次 main 分支
- 避免积累太多冲突

### 2. 小步提交
- 将大更改拆分为多个小提交
- 便于冲突解决和回滚

### 3. 清晰的提交信息
```bash
# 好的提交信息
git commit -m "docs: 添加 Demo 模式故障排除指南"
git commit -m "fix: 修复 Mock API 路由的 HTTP 方法支持"
git commit -m "merge: 同步 main 分支更新"

# 避免的提交信息
git commit -m "update"
git commit -m "fix bug"
```

### 4. 测试合并结果
```bash
# 合并后运行测试
pnpm typecheck
pnpm lint

# 启动服务验证
pnpm dev
```

## 常见问题

### Q: 合并后出现错误怎么办？

```bash
# 查看合并提交
git log --oneline -5

# 如果需要回滚
git reset --hard HEAD~1

# 或者使用 reflog 找到之前的提交
git reflog
git reset --hard <提交哈希>
```

### Q: 如何处理二进制文件冲突？

```bash
# 保留您的版本
git checkout --ours <文件>
git add <文件>

# 或保留 main 版本
git checkout --theirs <文件>
git add <文件>
```

### Q: 不想立即解决冲突？

```bash
# 中止合并
git merge --abort

# 或中止 rebase
git rebase --abort
```

## 可视化分支状态

```bash
# 查看分支图
git log --oneline --graph --all -20

# 查看分支差异
git diff local-integrate..origin/main --stat

# 查看哪些提交在 main 但不在 local-integrate
git log local-integrate..origin/main --oneline
```

## 推送分支到远程（可选）

如果您想备份 local-integrate 分支：

```bash
# 首次推送
git push -u origin local-integrate

# 后续推送
git push
```

---

**提示**: 保持分支同步是一个好习惯，可以避免后期大量的合并冲突。
