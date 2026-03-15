#!/usr/bin/env python3
"""
测试配置加载脚本
"""

import os
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.memory_config import get_memory_config
from src.config.skills_config import SkillsConfig
from src.config.sandbox_config import SandboxConfig
from src.config.subagents_config import get_subagents_app_config
from src.config.summarization_config import get_summarization_config
from src.config.title_config import get_title_config


def test_config_loading():
    """测试所有配置是否正确加载"""
    print("测试配置加载...\n")
    
    # 测试内存配置
    print("=== 内存配置 ===")
    memory_config = get_memory_config()
    print(f"启用: {memory_config.enabled}")
    print(f"存储路径: {memory_config.storage_path}")
    print(f"防抖秒数: {memory_config.debounce_seconds}")
    print(f"最大事实数: {memory_config.max_facts}")
    print(f"置信度阈值: {memory_config.fact_confidence_threshold}")
    print(f"注入启用: {memory_config.injection_enabled}")
    print(f"最大注入 tokens: {memory_config.max_injection_tokens}")
    print()
    
    # 测试技能配置
    print("=== 技能配置 ===")
    skills_config = SkillsConfig()
    print(f"技能路径: {skills_config.path}")
    print(f"容器路径: {skills_config.container_path}")
    print()
    
    # 测试沙盒配置
    print("=== 沙盒配置 ===")
    sandbox_config = SandboxConfig()
    print(f"使用: {sandbox_config.use}")
    print(f"镜像: {sandbox_config.image}")
    print(f"端口: {sandbox_config.port}")
    print(f"基础 URL: {sandbox_config.base_url}")
    print(f"自动启动: {sandbox_config.auto_start}")
    print(f"容器前缀: {sandbox_config.container_prefix}")
    print(f"空闲超时: {sandbox_config.idle_timeout}")
    print()
    
    # 测试子代理配置
    print("=== 子代理配置 ===")
    subagents_config = get_subagents_app_config()
    print(f"超时秒数: {subagents_config.timeout_seconds}")
    print()
    
    # 测试摘要配置
    print("=== 摘要配置 ===")
    summarization_config = get_summarization_config()
    print(f"启用: {summarization_config.enabled}")
    print(f"模型名称: {summarization_config.model_name}")
    print(f"最大 tokens: {summarization_config.trim_tokens_to_summarize}")
    print()
    
    # 测试标题配置
    print("=== 标题配置 ===")
    title_config = get_title_config()
    print(f"启用: {title_config.enabled}")
    print(f"模型名称: {title_config.model_name}")
    print(f"最大单词数: {title_config.max_words}")
    print(f"最大字符数: {title_config.max_chars}")
    print()
    
    print("配置加载测试完成！")


if __name__ == "__main__":
    test_config_loading()
