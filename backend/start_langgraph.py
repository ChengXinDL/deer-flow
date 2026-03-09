import sys
import json
import pathlib
from langgraph_cli.config import validate_config_file
from langgraph_cli.cli import dev

# 修复编码问题：使用 UTF-8 读取配置文件
config_path = pathlib.Path("langgraph.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config_data = json.load(f)

# 将配置数据写入临时文件，使用 UTF-8 编码
temp_config = pathlib.Path("langgraph_utf8.json")
with open(temp_config, 'w', encoding='utf-8') as f:
    json.dump(config_data, f, ensure_ascii=False, indent=2)

# 使用临时配置文件启动 LangGraph
sys.argv = ['langgraph', 'dev', '--no-browser', '--allow-blocking', '--no-reload', '--config', str(temp_config)]
dev()
