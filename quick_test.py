#!/usr/bin/env python3
"""
Kronos项目快速测试脚本
"""
import os
import sys


def test_imports():
    """测试所有必要的包导入"""
    print("🔍 测试包导入...")

    try:
        import torch
        print(f"✅ torch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ torch导入失败: {e}")
        return False

    try:
        import pandas as pd
        print(f"✅ pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ pandas导入失败: {e}")
        return False

    try:
        import numpy as np
        print(f"✅ numpy: {np.__version__}")
    except ImportError as e:
        print(f"❌ numpy导入失败: {e}")
        return False

    try:
        import qlib
        print(f"✅ qlib: {qlib.__version__}")
    except ImportError as e:
        print(f"❌ qlib导入失败: {e}")
        return False

    try:
        from qlib.config import REG_CN
        print("✅ qlib.config导入成功")
    except ImportError as e:
        print(f"❌ qlib.config导入失败: {e}")
        return False

    try:
        from model import Kronos, KronosPredictor, KronosTokenizer
        print("✅ Kronos模型导入成功")
    except ImportError as e:
        print(f"❌ Kronos模型导入失败: {e}")
        return False

    return True

def test_data_file():
    """测试数据文件是否存在"""
    print("\n🔍 测试数据文件...")

    data_file = "examples/data/XSHG_5min_600977.csv"
    if os.path.exists(data_file):
        print(f"✅ 数据文件存在: {data_file}")
        return True
    else:
        print(f"❌ 数据文件不存在: {data_file}")
        return False

def main():
    """主测试函数"""
    print("🚀 Kronos项目快速测试")
    print("=" * 50)

    # 设置环境变量
    os.environ['SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYQLIB'] = '0.9.8'

    # 测试导入
    imports_ok = test_imports()

    # 测试数据文件
    data_ok = test_data_file()

    print("\n" + "=" * 50)
    if imports_ok and data_ok:
        print("🎉 所有测试通过！项目可以正常运行。")
        print("\n建议运行:")
        print("  python examples/prediction_example.py")
        return True
    else:
        print("❌ 部分测试失败，请检查环境配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
