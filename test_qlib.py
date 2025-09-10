#!/usr/bin/env python3
"""
测试qlib包是否正常工作
"""
import os
import sys

# 设置环境变量
os.environ['SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYQLIB'] = '0.9.8'

try:
    import qlib
    print("✅ qlib导入成功，版本:", qlib.__version__)

    # 测试基本功能
    print("✅ qlib配置导入成功")

    # 初始化qlib（不依赖数据源）
    qlib.init(default_conf="client")
    print("✅ qlib初始化成功")

    print("\n🎉 qlib包工作正常！")

except Exception as e:
    print(f"❌ qlib测试失败: {e}")
    sys.exit(1)
