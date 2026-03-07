#!/usr/bin/env pwsh
# 更新 local-integrate 分支的脚本
# 用法: .\scripts\update-from-main.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔄 正在更新 local-integrate 分支..." -ForegroundColor Cyan
Write-Host ""

# 检查是否在 Git 仓库中
if (-not (Test-Path .git)) {
    Write-Host "❌ 错误: 当前目录不是 Git 仓库" -ForegroundColor Red
    exit 1
}

# 获取当前分支
$currentBranch = git branch --show-current
Write-Host "当前分支: $currentBranch" -ForegroundColor Yellow

# 检查是否有未提交的更改
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️  检测到未提交的更改，正在暂存..." -ForegroundColor Yellow
    git stash push -m "自动暂存: update-from-main脚本"
    $stashed = $true
} else {
    $stashed = $false
}

try {
    # 切换到 local-integrate 分支
    Write-Host "📋 切换到 local-integrate 分支..." -ForegroundColor Cyan
    git checkout local-integrate

    # 获取远程更新
    Write-Host "📥 获取远程更新..." -ForegroundColor Cyan
    git fetch origin

    # 查看 main 分支的新提交
    Write-Host ""
    Write-Host "📊 main 分支的新提交:" -ForegroundColor Green
    $newCommits = git log local-integrate..origin/main --oneline
    if ($newCommits) {
        Write-Host $newCommits
    } else {
        Write-Host "(无新提交)" -ForegroundColor Gray
    }
    Write-Host ""

    # 合并更新
    Write-Host "🔀 正在合并 origin/main 到 local-integrate..." -ForegroundColor Cyan
    git merge origin/main --no-edit

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 更新成功完成!" -ForegroundColor Green
        Write-Host ""
        Write-Host "当前分支状态:" -ForegroundColor Yellow
        git log --oneline --graph -5
    } else {
        Write-Host ""
        Write-Host "⚠️  合并出现冲突，请手动解决:" -ForegroundColor Yellow
        Write-Host "   1. 编辑冲突文件" -ForegroundColor White
        Write-Host "   2. git add -A" -ForegroundColor White
        Write-Host "   3. git commit -m 'merge: 同步 main 分支更新'" -ForegroundColor White
        exit 1
    }

} finally {
    # 恢复暂存的更改
    if ($stashed) {
        Write-Host ""
        Write-Host "📤 恢复暂存的更改..." -ForegroundColor Cyan
        git stash pop
    }
}

Write-Host ""
Write-Host "🎉 全部完成!" -ForegroundColor Green
