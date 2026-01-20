#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CI环境配置
"""
import os
import sys

# 模拟CI环境
os.environ['CI'] = 'true'
os.environ['GITHUB_ACTIONS'] = 'true'

# 重新导入以应用CI配置
if 'app' in sys.modules:
    del sys.modules['app']

sys.path.insert(0, 'src')
from app import (
    IS_CI, 
    IS_GITHUB_ACTIONS, 
    CONCURRENT_WORKERS, 
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    ENABLE_DETAILED_LOGS
)

print("=" * 60)
print("CI环境配置测试")
print("=" * 60)
print(f"IS_CI: {IS_CI}")
print(f"IS_GITHUB_ACTIONS: {IS_GITHUB_ACTIONS}")
print(f"CONCURRENT_WORKERS: {CONCURRENT_WORKERS}")
print(f"REQUEST_TIMEOUT: {REQUEST_TIMEOUT}s")
print(f"MAX_RETRIES: {MAX_RETRIES}")
print(f"RETRY_DELAY: {RETRY_DELAY}s")
print(f"ENABLE_DETAILED_LOGS: {ENABLE_DETAILED_LOGS}")
print("=" * 60)

# 验证CI配置
assert IS_CI == True, "IS_CI should be True"
assert IS_GITHUB_ACTIONS == True, "IS_GITHUB_ACTIONS should be True"
assert CONCURRENT_WORKERS == 3, f"CONCURRENT_WORKERS should be 3, got {CONCURRENT_WORKERS}"
assert REQUEST_TIMEOUT == 60, f"REQUEST_TIMEOUT should be 60, got {REQUEST_TIMEOUT}"
assert MAX_RETRIES == 5, f"MAX_RETRIES should be 5, got {MAX_RETRIES}"
assert RETRY_DELAY == 2, f"RETRY_DELAY should be 2, got {RETRY_DELAY}"
assert ENABLE_DETAILED_LOGS == True, "ENABLE_DETAILED_LOGS should be True"

print("✅ 所有CI配置验证通过！")
