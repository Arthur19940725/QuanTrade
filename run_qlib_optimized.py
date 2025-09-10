#!/usr/bin/env python3
"""
优化的qlib_test运行脚本
"""

import gc
import os
import sys
import warnings

# 设置环境变量
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'

# Gym兼容性补丁
try:
    import gymnasium as gym
    sys.modules['gym'] = gym
except ImportError:
    pass

warnings.filterwarnings("ignore")

import torch

# 内存优化设置
torch.backends.cudnn.benchmark = False
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    try:
        torch.cuda.set_per_process_memory_fraction(0.7)  # 限制GPU内存
    except:
        pass

# 强制使用CPU如果CUDA有问题
try:
    test = torch.randn(2, 2).cuda()
    del test
    torch.cuda.empty_cache()
    device = "cuda"
except:
    device = "cpu"
    print("使用CPU模式以避免CUDA兼容性问题")

print(f"设备: {device}")

# 修改原始qlib_test.py中的设备设置
def patch_device_config():
    """修补设备配置"""
    import argparse
    
    # 创建安全的配置
    safe_config = {
        'device': device,
        'batch_size': 4,  # 小批量
        'sample_count': 1,
        'max_context': 256,  # 减少上下文长度
        'pred_len': 10,
        'clip': True,
        'T': 1.0,
        'top_k': 50,
        'top_p': 0.9
    }
    
    return safe_config

if __name__ == "__main__":
    print("=== 优化的Kronos测试运行器 ===")
    
    config = patch_device_config()
    print(f"使用配置: {config}")
    
    try:
        # 这里可以调用原始的qlib_test函数
        # 但使用优化的配置
        print("准备运行qlib_test...")
        print("注意：请确保数据文件存在于 ../data/processed_datasets/test_data.pkl")
        
        # 实际运行需要取消注释以下行
        # from qlib_test import run_inference
        # result = run_inference('../data/processed_datasets/test_data.pkl', config)
        
        print("✓ 脚本准备完成")
        
    except Exception as e:
        print(f"运行时错误: {e}")
        print("建议：")
        print("1. 确保数据文件存在")
        print("2. 检查模型文件是否正确")
        print("3. 考虑使用更小的batch_size")
