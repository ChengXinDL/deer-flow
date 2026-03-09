import sys
import os

# 打印 Python 版本和路径
print('Python executable:', sys.executable)
print('Python version:', sys.version)
print('Python path:', sys.path)

# 尝试导入 langchain_community
try:
    from langchain_community.utilities import SQLDatabase
    print('Successfully imported SQLDatabase from langchain_community')
except ImportError as e:
    print(f'Import error: {e}')

# 尝试导入 magicflowClient
try:
    from src.client import magicflowClient
    print('Successfully imported magicflowClient')
    
    # 尝试初始化 SQL Agent
    client = magicflowClient(agent_type='sql')
    print('SQL Agent initialized successfully')
except ImportError as e:
    print(f'Import error: {e}')
except Exception as e:
    print(f'Error: {e}')
