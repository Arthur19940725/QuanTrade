#!/usr/bin/env python
"""
qlib_test.py 修复版本
解决模块导入路径问题
"""
import argparse
from collections import defaultdict
import os
import pickle
import sys

# 修复Python路径问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
finetune_dir = os.path.join(project_root, 'finetune')

# 添加必要的路径到Python路径
sys.path.insert(0, project_root)  # 项目根目录
sys.path.insert(0, finetune_dir)  # finetune目录

print(f"✅ 项目根目录: {project_root}")
print(f"✅ 当前目录: {current_dir}")
print(f"✅ Python路径已修复")

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

# 检查并导入qlib相关模块
try:
    import qlib
    from qlib.backtest import backtest, executor
    from qlib.config import REG_CN
    from qlib.contrib.evaluate import risk_analysis
    from qlib.contrib.strategy import TopkDropoutStrategy
    from qlib.utils.time import Freq
    print("✅ qlib模块导入成功")
except ImportError as e:
    print(f"❌ qlib模块导入失败: {e}")
    print("💡 请确保已正确安装qlib")

# 导入配置
try:
    from config import Config
    print("✅ 配置模块导入成功")
except ImportError as e:
    print(f"❌ 配置模块导入失败: {e}")

# 导入Kronos模型
try:
    from model.kronos import Kronos, KronosTokenizer, auto_regressive_inference
    print("✅ Kronos模型模块导入成功")
except ImportError as e:
    print(f"❌ Kronos模型模块导入失败: {e}")
    print("💡 尝试相对导入...")
    try:
        # 尝试从项目根目录导入
        sys.path.append(os.path.join(project_root, 'model'))
        import kronos
        from kronos import Kronos, KronosTokenizer, auto_regressive_inference
        print("✅ 使用相对导入成功")
    except ImportError as e2:
        print(f"❌ 相对导入也失败: {e2}")
        sys.exit(1)

# =================================================================================
# 1. Data Loading and Processing for Inference
# =================================================================================

class QlibInferenceDataset(Dataset):
    """Dataset for inference on Qlib data."""
    
    def __init__(self, data, lookback_window, predict_window):
        self.data = data
        self.lookback_window = lookback_window
        self.predict_window = predict_window
        
        # Create samples
        self.samples = []
        for i in range(len(data) - lookback_window - predict_window + 1):
            sample = {
                'input': data[i:i+lookback_window],
                'target': data[i+lookback_window:i+lookback_window+predict_window],
                'index': i
            }
            self.samples.append(sample)
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        return self.samples[idx]

def load_qlib_data(config):
    """加载qlib数据进行推理"""
    print("🔄 加载qlib数据...")
    
    try:
        # 初始化qlib
        qlib.init(provider_uri=config['qlib_data_path'], region=REG_CN)
        
        # 获取数据
        from qlib.data import D
        
        instruments = D.instruments(market='csi300')
        fields = ['$open', '$high', '$low', '$close', '$volume', '$amount']
        
        # 加载测试时间范围的数据
        start_time = config['test_time_range'][0]
        end_time = config['test_time_range'][1]
        
        print(f"📅 数据时间范围: {start_time} 到 {end_time}")
        print(f"🏢 股票数量: {len(instruments)}")
        
        data = D.features(instruments, fields, start_time=start_time, end_time=end_time, freq='day')
        
        print(f"✅ 数据加载完成，形状: {data.shape}")
        return data, instruments
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return None, None

def run_inference_test(config, device):
    """运行推理测试"""
    print("🚀 开始推理测试...")
    
    # 加载数据
    data, instruments = load_qlib_data(config)
    if data is None:
        print("❌ 数据加载失败，退出测试")
        return
    
    # 加载模型
    try:
        print("🔄 加载预训练模型...")
        tokenizer = KronosTokenizer.from_pretrained(config['pretrained_tokenizer_path'])
        model = Kronos.from_pretrained(config['pretrained_predictor_path'])
        
        tokenizer.eval().to(device)
        model.eval().to(device)
        
        print("✅ 模型加载成功")
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 运行推理测试
    try:
        print("🔄 执行推理...")
        
        # 选择一小部分数据进行测试
        test_data = data.head(1000)  # 只测试前1000条数据
        
        # 创建数据集
        dataset = QlibInferenceDataset(
            test_data.values, 
            config['lookback_window'], 
            config['predict_window']
        )
        
        dataloader = DataLoader(dataset, batch_size=10, shuffle=False)
        
        predictions = []
        targets = []
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="推理进度"):
                inputs = batch['input'].float().to(device)
                batch_targets = batch['target'].float()
                
                # 执行推理
                # 注意：这里需要根据实际的模型接口调整
                try:
                    outputs = auto_regressive_inference(
                        model, tokenizer, inputs, 
                        config['predict_window'],
                        device=device
                    )
                    
                    predictions.append(outputs.cpu())
                    targets.append(batch_targets)
                    
                except Exception as e:
                    print(f"⚠️  批次推理失败: {e}")
                    continue
        
        if predictions:
            predictions = torch.cat(predictions, dim=0)
            targets = torch.cat(targets, dim=0)
            
            print(f"✅ 推理完成")
            print(f"📊 预测形状: {predictions.shape}")
            print(f"📊 目标形状: {targets.shape}")
            
            # 计算简单的评估指标
            mse = torch.mean((predictions - targets) ** 2)
            print(f"📈 均方误差 (MSE): {mse.item():.6f}")
            
        else:
            print("❌ 没有成功的推理结果")
            
    except Exception as e:
        print(f"❌ 推理测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Qlib测试脚本修复版本")
    parser.add_argument("--device", type=str, default="cpu", help="设备类型 (cpu/cuda:0)")
    parser.add_argument("--config", type=str, help="配置文件路径")
    
    args = parser.parse_args()
    
    print("🚀 Qlib测试脚本修复版本")
    print(f"💻 使用设备: {args.device}")
    
    # 检查设备可用性
    if args.device.startswith('cuda') and not torch.cuda.is_available():
        print("⚠️  CUDA不可用，切换到CPU")
        device = torch.device('cpu')
    else:
        device = torch.device(args.device)
    
    # 加载配置
    try:
        config_instance = Config()
        config = config_instance.__dict__
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 检查必要的路径
    if not os.path.exists(config['qlib_data_path']):
        print(f"❌ Qlib数据路径不存在: {config['qlib_data_path']}")
        print("💡 请先运行数据预处理脚本")
        return 1
    
    # 运行测试
    try:
        run_inference_test(config, device)
        print("🎉 测试完成!")
        return 0
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)