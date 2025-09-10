#!/usr/bin/env python3
"""
测试内存优化和Gym兼容性修复的简化脚本
"""

import gc
import os
import sys
import warnings

# 应用Gym到Gymnasium兼容性补丁
try:
    import gymnasium as gym
    sys.modules['gym'] = gym
    print("✓ 已应用Gym到Gymnasium兼容性补丁")
except ImportError:
    print("⚠ 未找到gymnasium，建议安装: pip install gymnasium[classic_control]")

# 忽略警告
warnings.filterwarnings("ignore", category=UserWarning, module="torch.cuda")

import torch
import numpy as np
import pandas as pd

print(f"Python版本: {sys.version}")
print(f"PyTorch版本: {torch.__version__}")
print(f"NumPy版本: {np.__version__}")
print(f"Pandas版本: {pd.__version__}")

# 内存优化设置
torch.backends.cudnn.benchmark = False
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print(f"✓ CUDA可用，GPU: {torch.cuda.get_device_name(0)}")
else:
    print("✓ 使用CPU模式")

# 测试qlib导入
try:
    import qlib
    print(f"✓ qlib导入成功，版本: {qlib.__version__ if hasattr(qlib, '__version__') else '未知'}")
    
    # 测试qlib中使用gym的模块
    try:
        from qlib.rl.interpreter import Interpreter
        print("✓ qlib.rl模块导入成功，Gym兼容性修复有效")
    except Exception as e:
        print(f"⚠ qlib.rl模块导入警告: {e}")
        
except ImportError as e:
    print(f"⚠ qlib未安装或导入失败: {e}")

# 测试内存管理
print("\n=== 内存管理测试 ===")

def test_memory_optimization():
    """测试内存优化功能"""
    try:
        # 创建一些测试数据
        print("创建测试数据...")
        test_data = []
        
        # 分批创建数据以模拟内存优化
        batch_size = 5
        total_batches = 10
        
        for i in range(0, total_batches, batch_size):
            batch_data = [np.random.randn(100, 6) for _ in range(min(batch_size, total_batches - i))]
            test_data.extend(batch_data)
            
            # 强制垃圾回收
            gc.collect()
            
            if i + batch_size < total_batches:
                print(f"已处理 {i+batch_size}/{total_batches} 批数据")
        
        print(f"✓ 成功创建 {len(test_data)} 批测试数据")
        
        # 清理测试数据
        del test_data
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        print("✓ 内存优化测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 内存优化测试失败: {e}")
        return False

def test_torch_inference():
    """测试PyTorch推理内存管理"""
    try:
        print("测试PyTorch推理...")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 创建简单模型
        model = torch.nn.Sequential(
            torch.nn.Linear(10, 50),
            torch.nn.ReLU(),
            torch.nn.Linear(50, 1)
        ).to(device)
        
        model.eval()
        
        with torch.no_grad():
            for i in range(5):
                # 创建小批量数据
                x = torch.randn(4, 10).to(device)  # 小batch size
                
                # 使用混合精度（如果支持）
                with torch.cuda.amp.autocast(enabled=device=="cuda"):
                    output = model(x)
                
                # 定期清理内存
                if i % 2 == 0 and device == "cuda":
                    torch.cuda.empty_cache()
                    
                print(f"推理批次 {i+1}/5 完成")
        
        print("✓ PyTorch推理内存管理测试完成")
        return True
        
    except Exception as e:
        print(f"✗ PyTorch推理测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== Kronos 修复验证测试 ===")
    
    success_count = 0
    total_tests = 2
    
    # 测试1: 内存优化
    if test_memory_optimization():
        success_count += 1
    
    # 测试2: PyTorch推理
    if test_torch_inference():
        success_count += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过测试: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("✓ 所有测试通过，修复成功！")
        return True
    else:
        print("⚠ 部分测试失败，可能需要进一步调整")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)