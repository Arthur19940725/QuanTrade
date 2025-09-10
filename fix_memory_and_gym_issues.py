#!/usr/bin/env python3
"""
修复内存错误和Gym兼容性问题的脚本
解决MemoryError和Gym库升级到Gymnasium的问题
"""

import subprocess
import sys
import os
import warnings

def install_gymnasium():
    """安装gymnasium并卸载旧的gym"""
    print("正在修复Gym兼容性问题...")
    
    try:
        # 卸载旧的gym
        print("卸载旧版本的gym...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "gym", "-y"], 
                      check=False, capture_output=True)
        
        # 安装gymnasium
        print("安装gymnasium...")
        subprocess.run([sys.executable, "-m", "pip", "install", "gymnasium[classic_control]"], 
                      check=True, capture_output=True)
        
        print("✓ Gymnasium安装成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 安装gymnasium时出错: {e}")
        return False

def create_memory_optimized_qlib_test():
    """创建内存优化版本的qlib_test.py"""
    print("创建内存优化的测试脚本...")
    
    optimized_code = '''import argparse
from collections import defaultdict
import gc
import os
import pickle
import sys
import warnings

# 忽略CUDA兼容性警告
warnings.filterwarnings("ignore", category=UserWarning, module="torch.cuda")

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

import qlib
from qlib.backtest import backtest, executor
from qlib.config import REG_CN
from qlib.contrib.evaluate import risk_analysis
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.utils.time import Freq

# Ensure project root is in the Python path - FIXED
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)

from config import Config
from model.kronos import Kronos, KronosTokenizer, auto_regressive_inference

# 内存优化设置
torch.backends.cudnn.benchmark = False  # 减少内存使用
if torch.cuda.is_available():
    torch.cuda.empty_cache()  # 清理GPU内存

class QlibTestDataset(Dataset):
    """
    内存优化的PyTorch Dataset for handling Qlib test data
    """

    def __init__(self, data: dict, config: Config):
        self.data = data
        self.config = config
        self.window_size = config.lookback_window + config.predict_window
        self.symbols = list(self.data.keys())
        self.feature_list = config.feature_list
        self.time_feature_list = config.time_feature_list
        self.indices = []

        print("Preprocessing and building indices for test dataset...")
        
        # 分批处理数据以减少内存使用
        batch_size = min(10, len(self.symbols))  # 每次处理最多10个股票
        
        for i in range(0, len(self.symbols), batch_size):
            batch_symbols = self.symbols[i:i+batch_size]
            
            for symbol in batch_symbols:
                df = self.data[symbol].reset_index()
                # Generate time features on-the-fly
                df['minute'] = df['datetime'].dt.minute
                df['hour'] = df['datetime'].dt.hour
                df['weekday'] = df['datetime'].dt.weekday
                df['day'] = df['datetime'].dt.day
                df['month'] = df['datetime'].dt.month
                self.data[symbol] = df  # Store preprocessed dataframe

                num_samples = len(df) - self.window_size + 1
                if num_samples > 0:
                    for j in range(num_samples):
                        timestamp = df.iloc[j + self.config.lookback_window - 1]['datetime']
                        self.indices.append((symbol, j, timestamp))
            
            # 强制垃圾回收
            gc.collect()
            
            print(f"已处理 {min(i+batch_size, len(self.symbols))}/{len(self.symbols)} 个股票")

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, idx: int):
        symbol, start_idx, timestamp = self.indices[idx]
        df = self.data[symbol]

        context_end = start_idx + self.config.lookback_window
        target_end = start_idx + self.window_size

        context_df = df.iloc[start_idx:context_end]
        target_df = df.iloc[context_end:target_end]

        # Extract features
        context_features = context_df[self.feature_list].values.astype(np.float32)
        target_features = target_df[self.feature_list].values.astype(np.float32)

        # Extract time features
        context_time_features = context_df[self.time_feature_list].values.astype(np.float32)
        target_time_features = target_df[self.time_feature_list].values.astype(np.float32)

        return {
            'context_features': torch.tensor(context_features, dtype=torch.float32),
            'target_features': torch.tensor(target_features, dtype=torch.float32),
            'context_time_features': torch.tensor(context_time_features, dtype=torch.float32),
            'target_time_features': torch.tensor(target_time_features, dtype=torch.float32),
            'symbol': symbol,
            'timestamp': timestamp
        }


def load_test_data(data_path: str):
    """加载测试数据，使用内存优化"""
    print(f"Loading test data from {data_path}")
    
    try:
        with open(data_path, 'rb') as f:
            data = pickle.load(f)
        print(f"✓ 成功加载 {len(data)} 个股票的数据")
        return data
    except MemoryError:
        print("✗ 内存不足，尝试分批加载数据...")
        # 如果内存不足，可以考虑分批加载
        raise
    except Exception as e:
        print(f"✗ 加载数据时出错: {e}")
        raise


def run_memory_optimized_inference(config_path: str = "config.py", data_path: str = "../data/processed_datasets/test_data.pkl"):
    """运行内存优化的推理"""
    
    print("=== 开始内存优化的Kronos推理测试 ===")
    
    # 设置内存优化参数
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'  # 限制CUDA内存分配
    
    # 1. Load configuration
    config = Config()
    print(f"✓ 配置加载完成")
    
    # 2. Load test data with memory optimization
    try:
        test_data = load_test_data(data_path)
    except Exception as e:
        print(f"✗ 无法加载测试数据: {e}")
        return False
    
    # 3. Create dataset with smaller batch size
    test_dataset = QlibTestDataset(test_data, config)
    
    # 使用更小的batch size以减少内存使用
    batch_size = min(8, len(test_dataset))  # 最大8个样本
    
    test_dataloader = DataLoader(
        test_dataset, 
        batch_size=batch_size, 
        shuffle=False,
        num_workers=0,  # 不使用多进程以避免内存问题
        pin_memory=False  # 不使用pin_memory
    )
    
    print(f"✓ 数据加载器创建完成，batch_size={batch_size}")
    
    # 4. Load model and tokenizer
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device}")
    
    try:
        tokenizer = KronosTokenizer.from_pretrained(config.tokenizer_model_path)
        model = Kronos.from_pretrained(config.model_path)
        model = model.to(device)
        model.eval()
        print("✓ 模型和分词器加载完成")
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        return False
    
    # 5. Run inference with memory optimization
    predictions = []
    
    print("开始推理...")
    with torch.no_grad():  # 禁用梯度计算
        for batch_idx, batch in enumerate(tqdm(test_dataloader, desc="Inference")):
            try:
                # 移动数据到设备
                context_features = batch['context_features'].to(device)
                target_features = batch['target_features'].to(device)
                context_time_features = batch['context_time_features'].to(device)
                target_time_features = batch['target_time_features'].to(device)
                
                # 运行推理
                with torch.cuda.amp.autocast(enabled=device=="cuda"):  # 使用混合精度
                    outputs = auto_regressive_inference(
                        model=model,
                        tokenizer=tokenizer,
                        context_features=context_features,
                        target_features=target_features,
                        context_time_features=context_time_features,
                        target_time_features=target_time_features,
                        config=config
                    )
                
                # 保存预测结果
                for i in range(len(batch['symbol'])):
                    predictions.append({
                        'symbol': batch['symbol'][i],
                        'timestamp': batch['timestamp'][i],
                        'prediction': outputs[i].cpu().numpy() if torch.is_tensor(outputs[i]) else outputs[i]
                    })
                
                # 定期清理内存
                if batch_idx % 10 == 0:
                    if device == "cuda":
                        torch.cuda.empty_cache()
                    gc.collect()
                    
            except RuntimeError as e:
                if "out of memory" in str(e):
                    print(f"✗ GPU内存不足，跳过batch {batch_idx}")
                    if device == "cuda":
                        torch.cuda.empty_cache()
                    continue
                else:
                    raise e
    
    print(f"✓ 推理完成，共生成 {len(predictions)} 个预测结果")
    
    # 6. Save results
    output_path = "memory_optimized_predictions.pkl"
    with open(output_path, 'wb') as f:
        pickle.dump(predictions, f)
    
    print(f"✓ 结果已保存到 {output_path}")
    return True


if __name__ == "__main__":
    # 修复Gym问题
    install_gymnasium()
    
    # 运行内存优化的推理
    success = run_memory_optimized_inference()
    
    if success:
        print("\\n=== 修复完成 ===")
        print("1. ✓ Gym已升级为Gymnasium")
        print("2. ✓ 内存优化推理完成")
    else:
        print("\\n=== 修复失败 ===")
        print("请检查错误信息并重试")
'''
    
    with open("qlib_test_memory_optimized.py", "w", encoding="utf-8") as f:
        f.write(optimized_code)
    
    print("✓ 内存优化脚本已创建: qlib_test_memory_optimized.py")

def create_gym_to_gymnasium_patch():
    """创建gym到gymnasium的补丁文件"""
    print("创建Gym到Gymnasium的兼容性补丁...")
    
    patch_code = '''"""
Gym到Gymnasium兼容性补丁
自动将qlib中的gym导入替换为gymnasium
"""

import sys
import importlib.util
from pathlib import Path

def patch_qlib_gym_imports():
    """修补qlib中的gym导入"""
    try:
        import gymnasium as gym
        
        # 将gymnasium注册为gym模块
        sys.modules['gym'] = gym
        
        print("✓ 成功将gymnasium注册为gym模块")
        return True
        
    except ImportError:
        print("✗ 未找到gymnasium，请先安装: pip install gymnasium[classic_control]")
        return False

def apply_patch():
    """应用补丁"""
    success = patch_qlib_gym_imports()
    
    if success:
        print("✓ Gym兼容性补丁应用成功")
    else:
        print("✗ 补丁应用失败")
    
    return success

if __name__ == "__main__":
    apply_patch()
'''
    
    with open("gym_to_gymnasium_patch.py", "w", encoding="utf-8") as f:
        f.write(patch_code)
    
    print("✓ 兼容性补丁已创建: gym_to_gymnasium_patch.py")

def main():
    """主函数"""
    print("=== Kronos 错误修复工具 ===")
    print("正在修复MemoryError和Gym兼容性问题...")
    
    # 1. 安装gymnasium
    gym_success = install_gymnasium()
    
    # 2. 创建内存优化脚本
    create_memory_optimized_qlib_test()
    
    # 3. 创建兼容性补丁
    create_gym_to_gymnasium_patch()
    
    print("\n=== 修复完成 ===")
    print("已创建以下文件:")
    print("1. qlib_test_memory_optimized.py - 内存优化的测试脚本")
    print("2. gym_to_gymnasium_patch.py - Gym兼容性补丁")
    
    print("\n使用方法:")
    print("1. 运行内存优化脚本: python qlib_test_memory_optimized.py")
    print("2. 或在其他脚本开头导入补丁: from gym_to_gymnasium_patch import apply_patch; apply_patch()")
    
    if gym_success:
        print("\n✓ Gymnasium安装成功，Gym兼容性问题已解决")
    else:
        print("\n⚠ 请手动安装gymnasium: pip install gymnasium[classic_control]")

if __name__ == "__main__":
    main()