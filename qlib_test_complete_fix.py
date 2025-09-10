#!/usr/bin/env python
"""
qlib_test.py 完整修复版本
解决模块导入和模型路径问题
"""
import argparse
from collections import defaultdict
import os
import pickle
import sys

# 修复Python路径问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if 'finetune' in current_dir else current_dir
finetune_dir = os.path.join(project_root, 'finetune')

sys.path.insert(0, project_root)
sys.path.insert(0, finetune_dir)

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

from config import Config
from model.kronos import Kronos, KronosTokenizer, auto_regressive_inference

def fix_model_paths(config):
    """修复模型路径"""
    print("🔧 修复模型路径...")
    
    # 检查并修复分词器路径
    tokenizer_path = config['tokenizer_path']
    if not os.path.exists(tokenizer_path):
        print(f"⚠️  分词器路径不存在: {tokenizer_path}")
        
        # 尝试使用预训练分词器
        pretrained_tokenizer = config.get('pretrained_tokenizer_path', './models/models--NeoQuasar--Kronos-Tokenizer-base')
        
        # 检查snapshot路径
        if os.path.exists(pretrained_tokenizer):
            snapshots_dir = os.path.join(pretrained_tokenizer, 'snapshots')
            if os.path.exists(snapshots_dir):
                snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
                if snapshot_dirs:
                    actual_tokenizer_path = os.path.join(snapshots_dir, snapshot_dirs[0])
                    config['tokenizer_path'] = actual_tokenizer_path
                    print(f"✅ 使用预训练分词器: {actual_tokenizer_path}")
                else:
                    config['tokenizer_path'] = pretrained_tokenizer
                    print(f"✅ 使用预训练分词器: {pretrained_tokenizer}")
            else:
                config['tokenizer_path'] = pretrained_tokenizer
                print(f"✅ 使用预训练分词器: {pretrained_tokenizer}")
    
    # 检查并修复预测器路径
    model_path = config['model_path']
    if not os.path.exists(model_path):
        print(f"⚠️  预测器路径不存在: {model_path}")
        
        # 尝试使用预训练预测器
        pretrained_predictor = config.get('pretrained_predictor_path', './models/models--NeoQuasar--Kronos-small')
        
        # 检查snapshot路径
        if os.path.exists(pretrained_predictor):
            snapshots_dir = os.path.join(pretrained_predictor, 'snapshots')
            if os.path.exists(snapshots_dir):
                snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
                if snapshot_dirs:
                    actual_predictor_path = os.path.join(snapshots_dir, snapshot_dirs[0])
                    config['model_path'] = actual_predictor_path
                    print(f"✅ 使用预训练预测器: {actual_predictor_path}")
                else:
                    config['model_path'] = pretrained_predictor
                    print(f"✅ 使用预训练预测器: {pretrained_predictor}")
            else:
                config['model_path'] = pretrained_predictor
                print(f"✅ 使用预训练预测器: {pretrained_predictor}")
    
    return config

class QlibInferenceDataset(Dataset):
    """用于Qlib数据推理的数据集类"""
    
    def __init__(self, data_dict, lookback_window, predict_window, clip=5.0):
        self.data_dict = data_dict
        self.lookback_window = lookback_window
        self.predict_window = predict_window
        self.clip = clip
        
        # 准备样本
        self.samples = []
        for symbol, df in data_dict.items():
            if len(df) >= lookback_window + predict_window:
                # 标准化数据
                df_values = df.values
                df_normalized = np.clip(df_values, -clip, clip)
                
                # 创建滑动窗口样本
                for i in range(len(df_normalized) - lookback_window - predict_window + 1):
                    sample = {
                        'input': df_normalized[i:i+lookback_window],
                        'target': df_normalized[i+lookback_window:i+lookback_window+predict_window],
                        'symbol': symbol,
                        'index': i
                    }
                    self.samples.append(sample)
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        return {
            'input': torch.FloatTensor(sample['input']),
            'target': torch.FloatTensor(sample['target']),
            'symbol': sample['symbol'],
            'index': sample['index']
        }

def load_models(config, device):
    """加载模型"""
    print(f"🔄 加载模型到设备: {device}")
    
    try:
        # 加载分词器
        print(f"📁 分词器路径: {config['tokenizer_path']}")
        tokenizer = KronosTokenizer.from_pretrained(config['tokenizer_path'])
        tokenizer = tokenizer.to(device).eval()
        print("✅ 分词器加载成功")
        
        # 加载预测器
        print(f"📁 预测器路径: {config['model_path']}")
        model = Kronos.from_pretrained(config['model_path'])
        model = model.to(device).eval()
        print("✅ 预测器加载成功")
        
        return tokenizer, model
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        raise

def generate_predictions(config, test_data, device):
    """生成预测"""
    print("🔄 开始生成预测...")
    
    # 加载模型
    tokenizer, model = load_models(config, device)
    
    # 创建数据集
    dataset = QlibInferenceDataset(
        test_data, 
        config['lookback_window'], 
        config['predict_window'],
        config['clip']
    )
    
    print(f"📊 数据集大小: {len(dataset)}")
    
    # 创建数据加载器
    dataloader = DataLoader(
        dataset, 
        batch_size=min(config['batch_size'], 10),  # 限制批次大小
        shuffle=False
    )
    
    predictions = {}
    
    with torch.no_grad():
        for batch_idx, batch in enumerate(tqdm(dataloader, desc="生成预测")):
            try:
                inputs = batch['input'].to(device)
                targets = batch['target']
                symbols = batch['symbol']
                
                # 执行推理
                # 需要创建时间戳（这里简化处理）
                batch_size, seq_len, feature_dim = inputs.shape
                x_stamp = torch.zeros(batch_size, seq_len, 5)  # 5个时间特征
                y_stamp = torch.zeros(batch_size, config['pred_len'], 5)
                
                pred_outputs = auto_regressive_inference(
                    tokenizer, model, inputs,
                    x_stamp, y_stamp,
                    config['max_context'],
                    config['pred_len'],
                    clip=config['clip'],
                    T=config['T'],
                    top_k=config['top_k'],
                    top_p=config['top_p'],
                    sample_count=1,
                    verbose=False
                )
                
                # 存储预测结果
                for i, symbol in enumerate(symbols):
                    if symbol not in predictions:
                        predictions[symbol] = []
                    
                    # 处理预测输出（可能是numpy数组或tensor）
                    if hasattr(pred_outputs[i], 'cpu'):
                        pred_array = pred_outputs[i].cpu().numpy()
                    else:
                        pred_array = pred_outputs[i]
                    
                    predictions[symbol].append({
                        'prediction': pred_array,
                        'target': targets[i].numpy(),
                        'index': batch['index'][i].item()
                    })
                    
            except Exception as e:
                print(f"⚠️  批次 {batch_idx} 推理失败: {e}")
                continue
    
    print(f"✅ 预测完成，处理了 {len(predictions)} 个股票")
    return predictions

def evaluate_predictions(predictions):
    """评估预测结果"""
    print("📈 评估预测结果...")
    
    all_predictions = []
    all_targets = []
    
    for symbol, preds in predictions.items():
        for pred_data in preds:
            all_predictions.append(pred_data['prediction'])
            all_targets.append(pred_data['target'])
    
    if all_predictions:
        all_predictions = np.array(all_predictions)
        all_targets = np.array(all_targets)
        
        # 计算评估指标
        mse = np.mean((all_predictions - all_targets) ** 2)
        mae = np.mean(np.abs(all_predictions - all_targets))
        
        print(f"📊 评估结果:")
        print(f"   均方误差 (MSE): {mse:.6f}")
        print(f"   平均绝对误差 (MAE): {mae:.6f}")
        print(f"   预测样本数: {len(all_predictions)}")
        
        return {
            'mse': mse,
            'mae': mae,
            'num_samples': len(all_predictions)
        }
    else:
        print("❌ 没有有效的预测结果")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Qlib测试脚本完整修复版本")
    parser.add_argument("--device", type=str, default="cpu", help="设备类型")
    
    args = parser.parse_args()
    
    print("🚀 Qlib测试脚本完整修复版本")
    print(f"💻 使用设备: {args.device}")
    
    # 检查设备可用性
    if args.device.startswith('cuda'):
        if not torch.cuda.is_available():
            print("⚠️  CUDA不可用，切换到CPU")
            device = torch.device('cpu')
        else:
            try:
                device = torch.device(args.device)
                # 测试设备是否可用
                torch.zeros(1).to(device)
                print(f"✅ 使用设备: {device}")
            except Exception as e:
                print(f"⚠️  设备 {args.device} 不可用: {e}")
                print("切换到CPU")
                device = torch.device('cpu')
    else:
        device = torch.device('cpu')
    
    # 加载配置
    try:
        config_instance = Config()
        config = config_instance.__dict__
        
        # 设置运行配置
        run_config = {
            'device': str(device),
            'data_path': config['dataset_path'],
            'result_save_path': config['backtest_result_path'],
            'result_name': config['backtest_save_folder_name'],
            'tokenizer_path': config.get('finetuned_tokenizer_path', config['pretrained_tokenizer_path']),
            'model_path': config.get('finetuned_predictor_path', config['pretrained_predictor_path']),
            'max_context': config['max_context'],
            'pred_len': config['predict_window'],
            'clip': config['clip'],
            'T': config['inference_T'],
            'top_k': config['inference_top_k'],
            'top_p': config['inference_top_p'],
            'sample_count': config['inference_sample_count'],
            'batch_size': config['backtest_batch_size'],
            'lookback_window': config['lookback_window'],
            'predict_window': config['predict_window'],
            'pretrained_tokenizer_path': config['pretrained_tokenizer_path'],
            'pretrained_predictor_path': config['pretrained_predictor_path']
        }
        
        print("✅ 配置加载成功")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 修复模型路径
    run_config = fix_model_paths(run_config)
    
    # 加载测试数据
    test_data_path = os.path.join(run_config['data_path'], 'test_data.pkl')
    if not os.path.exists(test_data_path):
        print(f"❌ 测试数据文件不存在: {test_data_path}")
        print("💡 请先运行数据预处理脚本生成测试数据")
        return 1
    
    try:
        print(f"🔄 加载测试数据: {test_data_path}")
        with open(test_data_path, 'rb') as f:
            test_data = pickle.load(f)
        print(f"✅ 测试数据加载成功，包含 {len(test_data)} 个股票")
        
        # 显示部分数据信息
        for i, (symbol, df) in enumerate(test_data.items()):
            print(f"   {symbol}: {df.shape}")
            if i >= 5:  # 只显示前5个
                break
                
    except Exception as e:
        print(f"❌ 测试数据加载失败: {e}")
        return 1
    
    # 生成预测
    try:
        predictions = generate_predictions(run_config, test_data, device)
        
        if predictions:
            # 评估结果
            eval_results = evaluate_predictions(predictions)
            
            if eval_results:
                print("🎉 测试完成!")
                return 0
            else:
                print("❌ 评估失败")
                return 1
        else:
            print("❌ 没有生成任何预测")
            return 1
            
    except Exception as e:
        print(f"❌ 预测生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)