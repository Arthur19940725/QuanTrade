#!/usr/bin/env python
"""
torchrun修复包装脚本
解决Windows下PyTorch libuv支持问题
"""
import os
import sys
import subprocess
import argparse

def setup_environment():
    """设置必要的环境变量"""
    # 禁用libuv
    os.environ["USE_LIBUV"] = "0"
    
    # 设置其他可能需要的环境变量
    os.environ.setdefault("MASTER_ADDR", "localhost")
    os.environ.setdefault("MASTER_PORT", "12355")
    
    print("✅ 环境变量设置:")
    print(f"   USE_LIBUV: {os.environ.get('USE_LIBUV')}")
    print(f"   MASTER_ADDR: {os.environ.get('MASTER_ADDR')}")
    print(f"   MASTER_PORT: {os.environ.get('MASTER_PORT')}")

def run_torchrun_with_fix(args):
    """运行修复版本的torchrun命令"""
    setup_environment()
    
    # 构建torchrun命令
    cmd = ["torchrun"] + args
    
    print(f"🚀 执行命令: {' '.join(cmd)}")
    
    try:
        # 运行命令
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  用户中断训练")
        return 130
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="torchrun修复包装脚本",
        add_help=False  # 禁用默认帮助，传递给torchrun
    )
    
    # 解析所有参数并传递给torchrun
    args = sys.argv[1:]
    
    if not args:
        print("❌ 请提供torchrun参数")
        print("使用示例: python torchrun_fix.py --standalone --nproc_per_node=1 finetune/train_predictor.py")
        return 1
    
    print("🔧 torchrun libuv修复包装脚本")
    return run_torchrun_with_fix(args)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)