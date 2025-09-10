#!/usr/bin/env python3
"""
简单的 qlib 测试脚本，用于诊断问题
"""

import os
import sys
import traceback


def test_qlib_basic():
    """测试 qlib 基本功能"""
    try:
        print("=== 测试 qlib 基本导入 ===")
        import qlib
        from qlib.config import REG_CN
        from qlib.data import D
        print("✅ qlib 导入成功")

        print(f"qlib 版本: {qlib.__version__}")

        # 设置数据路径 - 从 finetune 目录回到项目根目录
        data_path = os.path.abspath("../qlib/qlib_data/cn_data")
        print(f"数据路径: {data_path}")

        # 检查数据路径是否存在
        if not os.path.exists(data_path):
            print(f"❌ 数据路径不存在: {data_path}")
            return False

        print("✅ 数据路径存在")

        # 检查关键目录
        calendars_dir = os.path.join(data_path, "calendars")
        features_dir = os.path.join(data_path, "features")

        if not os.path.exists(calendars_dir):
            print(f"❌ 日历目录不存在: {calendars_dir}")
            return False

        if not os.path.exists(features_dir):
            print(f"❌ 特征目录不存在: {features_dir}")
            return False

        print("✅ 关键目录存在")

        # 检查日历文件
        calendar_file = os.path.join(calendars_dir, "day.txt")
        if not os.path.exists(calendar_file):
            print(f"❌ 日历文件不存在: {calendar_file}")
            return False

        print("✅ 日历文件存在")

        # 尝试初始化 qlib
        print("\n=== 测试 qlib 初始化 ===")
        try:
            qlib.init(provider_uri=data_path, region=REG_CN)
            print("✅ qlib 初始化成功")
        except Exception as e:
            print(f"❌ qlib 初始化失败: {e}")
            print("尝试使用不同的初始化方式...")

            # 尝试不同的初始化方式
            try:
                qlib.init(provider_uri=data_path, region=REG_CN, freq='day')
                print("✅ qlib 初始化成功 (带频率)")
            except Exception as e2:
                print(f"❌ qlib 初始化仍然失败: {e2}")
                return False

        # 尝试获取日历
        print("\n=== 测试获取日历 ===")
        try:
            cal = D.calendar()
            print(f"✅ 成功获取日历，包含 {len(cal)} 个交易日")
            print(f"日历范围: {cal[0]} 到 {cal[-1]}")
        except Exception as e:
            print(f"❌ 获取日历失败: {e}")
            print("尝试使用显式频率...")
            try:
                cal = D.calendar(freq='day')
                print(f"✅ 成功获取日历 (显式频率)，包含 {len(cal)} 个交易日")
            except Exception as e2:
                print(f"❌ 获取日历仍然失败: {e2}")
                return False

        return True

    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        traceback.print_exc()
        return False

def test_data_loading():
    """测试数据加载"""
    try:
        print("\n=== 测试数据加载 ===")
        from qlib.data.dataset.loader import QlibDataLoader

        # 测试加载少量数据
        data_fields = ['$open', '$close', '$high', '$low', '$volume']

        # 使用较小的日期范围进行测试
        start_time = "2024-01-01"
        end_time = "2024-01-31"

        print(f"尝试加载数据: {start_time} 到 {end_time}")

        data_df = QlibDataLoader(config=data_fields).load(
            'csi300', start_time, end_time
        )

        print(f"✅ 成功加载数据，形状: {data_df.shape}")
        print(f"数据列: {list(data_df.columns)}")

        return True

    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始 qlib 诊断测试...")
    print("=" * 50)

    # 基本测试
    if not test_qlib_basic():
        print("\n❌ 基本测试失败，停止后续测试")
        sys.exit(1)

    # 数据加载测试
    if not test_data_loading():
        print("\n❌ 数据加载测试失败")
        sys.exit(1)

    print("\n✅ 所有测试通过！")
