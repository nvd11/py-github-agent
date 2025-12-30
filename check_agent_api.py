#!/usr/bin/env python3
"""
检查 LangChain agents 模块中可用的函数
"""

import sys
from langchain.agents import *

# 获取所有可用的函数
available_functions = [name for name in dir() if 'agent' in name.lower()]
print("Available agent functions:", available_functions)

# 检查 create_agent 的签名
if 'create_agent' in dir():
    import inspect
    sig = inspect.signature(create_agent)
    print(f"\ncreate_agent signature: {sig}")
    
    # 获取参数信息
    print("\nParameters:")
    for param_name, param in sig.parameters.items():
        print(f"  {param_name}: {param.annotation} = {param.default}")
