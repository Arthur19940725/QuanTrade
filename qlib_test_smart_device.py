#!/usr/bin/env python
"""
qlib_test.py 智能设备选择版本
自动检测CUDA兼容性，智能选择最佳设备
"""
import argparse
from collections import defaultdict
import os
import pickle
import sys
import warnings

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

def smart_device_selection(requested_device="cuda:0"):
    """智能设备选择，自动检测CUDA兼容性"""
    print("🔍 智能设备选择中...")
    
    # 检查是否有CUDA
    if not torch.cuda.is_available():
        print("❌ CUDA不可用，使用CPU")
        return torch.device('cpu'), "CUDA不可用"
    
    print(f"✅ CUDA可用，版本: {torch.version.cuda}")
    print(f"🖥️  GPU数量: {torch.cuda.device_count()}")
    
    # 检查GPU兼容性
    for i in range(torch.cuda.device_count()):
        gpu_name = torch.cuda.get_device_name(i)
        gpu_capability = torch.cuda.get_device_capability(i)
        sm_version = f"sm_{gpu_capability[0]}{gpu_capability[1]}"
        print(f"   GPU {i}: {gpu_name} (计算能力: {sm_version})")
        
        # 检查是否是RTX 5060 Ti或其他新GPU
        if "5060" in gpu_name or gpu_capability[0] >= 12:  # sm_120及以上
            print(f"⚠️  检测到新GPU架构 {sm_version}，可能与当前PyTorch不兼容")
    
    # 尝试创建CUDA张量测试兼容性
    print("🧪 测试CUDA兼容性...")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            test_tensor = torch.zeros(10, 10).cuda()
            result = torch.matmul(test_tensor, test_tensor.t())  # 简单的矩阵运算
            print("✅ CUDA基本运算测试通过")
        
        # 尝试更复杂的操作
        try:
            test_model = torch.nn.Linear(10, 5).cuda()
            output = test_model(test_tensor)
            print("✅ CUDA神经网络测试通过")
            
            # 清理测试张量
            del test_tensor, result, test_model, output
            torch.cuda.empty_cache()
            
            return torch.device(requested_device), "CUDA兼容性测试通过"
            
        except Exception as e:
            print(f"⚠️  CUDA神经网络测试失败: {e}")
            print("🔄 回退到CPU模式")
            return torch.device('cpu'), f"CUDA神经网络不兼容: {e}"
            
    except Exception as e:
        print(f"⚠️  CUDA基本测试失败: {e}")
        print("🔄 回退到CPU模式")
        return torch.device('cpu'), f"CUDA基本运算不兼容: {e}"

def fix_model_paths_smart(config):
    """智能修复模型路径"""
    print("🔧 智能修复模型路径...")
    
    # 修复分词器路径
    tokenizer_path = config.get('tokenizer_path', config.get('finetuned_tokenizer_path'))
    if not tokenizer_path or not os.path.exists(tokenizer_path):
        # 查找预训练分词器
        possible_paths = [
            config.get('pretrained_tokenizer_path'),
            './models/models--NeoQuasar--Kronos-Tokenizer-base',
            './models/models--NeoQuasar--Kronos-Tokenizer-2k'
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                # 检查是否有snapshots目录
                snapshots_dir = os.path.join(path, 'snapshots')
                if os.path.exists(snapshots_dir):
                    snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
                    if snapshot_dirs:
                        config['tokenizer_path'] = os.path.join(snapshots_dir, snapshot_dirs[0])
                        print(f"✅ 找到分词器: {config['tokenizer_path']}")
                        break
                else:
                    config['tokenizer_path'] = path
                    print(f"✅ 使用分词器: {path}")
                    break
        else:
            print("❌ 未找到可用的分词器")
            return None
    
    # 修复预测器路径
    model_path = config.get('model_path', config.get('finetuned_predictor_path'))
    if not model_path or not os.path.exists(model_path):
        # 查找预训练预测器
        possible_paths = [
            config.get('pretrained_predictor_path'),
            './models/models--NeoQuasar--Kronos-small',
            './models/models--NeoQuasar--Kronos-mini',
            './models/models--NeoQuasar--Kronos-base'
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                # 检查是否有snapshots目录
                snapshots_dir = os.path.join(path, 'snapshots')
                if os.path.exists(snapshots_dir):
                    snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
                    if snapshot_dirs:
                        config['model_path'] = os.path.join(snapshots_dir, snapshot_dirs[0])
                        print(f"✅ 找到预测器: {config['model_path']}")
                        break
                else:
                    config['model_path'] = path
                    print(f"✅ 使用预测器: {path}")
                    break
        else:
            print("❌ 未找到可用的预测器")
            return None
    
    return config

def load_models_smart(config, device):
    """智能加载模型，处理设备兼容性"""
    print(f"🔄 智能加载模型到设备: {device}")
    
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
        if device.type == 'cuda':
            print("🔄 尝试回退到CPU...")
            try:
                tokenizer = KronosTokenizer.from_pretrained(config['tokenizer_path'])
                tokenizer = tokenizer.cpu().eval()
                model = Kronos.from_pretrained(config['model_path'])
                model = model.cpu().eval()
                print("✅ CPU模式加载成功")
                return tokenizer, model
            except Exception as e2:
                print(f"❌ CPU模式也失败: {e2}")
                raise
        else:
            raise

class SmartInferenceDataset(Dataset):
    """智能推理数据集，根据设备优化"""
    
    def __init__(self, data_dict, lookback_window, predict_window, clip=5.0, device_type='cpu'):
        self.data_dict = data_dict
        self.lookback_window = lookback_window
        self.predict_window = predict_window
        self.clip = clip
        self.device_type = device_type
        
        # 根据设备类型调整采样策略
        sample_ratio = 0.3 if device_type == 'cpu' else 0.1  # CPU取更多样本，GPU取少量样本
        
        self.samples = []
        for symbol, df in data_dict.items():
            if len(df) >= lookback_window + predict_window:
                df_values = df.values.astype(np.float32)
                df_normalized = np.clip(df_values, -clip, clip)
                
                # 智能采样
                total_possible = len(df_normalized) - lookback_window - predict_window + 1
                step = max(1, int(1 / sample_ratio))
                
                for i in range(0, total_possible, step):
                    sample = {
                        'input': df_normalized[i:i+lookback_window],
                        'target': df_normalized[i+lookback_window:i+lookback_window+predict_window],
                        'symbol': symbol,
                        'index': i
                    }
                    self.samples.append(sample)
        
        print(f"📊 智能采样完成，样本数: {len(self.samples)} (设备: {device_type})")
    
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

def generate_predictions_smart(config, test_data, device):
    """智能预测生成"""
    print("🔄 开始智能预测生成...")
    
    # 加载模型
    tokenizer, model = load_models_smart(config, device)
    
    # 根据实际设备类型更新配置
    actual_device = next(model.parameters()).device
    print(f"📍 实际使用设备: {actual_device}")
    
    # 创建智能数据集
    dataset = SmartInferenceDataset(
        test_data, 
        config['lookback_window'], 
        config['predict_window'],
        config['clip'],
        actual_device.type
    )
    
    # 智能批次大小选择
    if actual_device.type == 'cuda':
        batch_size = 1  # CUDA兼容性问题时使用最小批次
    else:
        batch_size = 8   # CPU使用较大批次
    
    dataloader = DataLoader(
        dataset, 
        batch_size=batch_size,
        shuffle=False,
        pin_memory=(actual_device.type == 'cuda'),
        num_workers=0  # 避免多进程问题
    )
    
    predictions = {}
    successful_predictions = 0
    
    print(f"🚀 开始智能推理（批次大小: {batch_size}，设备: {actual_device}）...")
    
    with torch.no_grad():
        for batch_idx, batch in enumerate(tqdm(dataloader, desc="智能推理")):
            try:
                inputs = batch['input'].to(actual_device)
                targets = batch['target']
                symbols = batch['symbol']
                
                # 创建时间戳
                batch_size_actual, seq_len, feature_dim = inputs.shape
                x_stamp = torch.zeros(batch_size_actual, seq_len, 5).to(actual_device)
                y_stamp = torch.zeros(batch_size_actual, config['predict_window'], 5).to(actual_device)
                
                # 执行推理
                pred_outputs = auto_regressive_inference(
                    tokenizer, model, inputs,
                    x_stamp, y_stamp,
                    config['max_context'],
                    config['predict_window'],
                    clip=config['clip'],
                    T=config.get('T', 0.6),
                    top_k=config.get('top_k', 0),
                    top_p=config.get('top_p', 0.9),
                    sample_count=1,
                    verbose=False
                )
                
                # 存储预测结果
                for i, symbol in enumerate(symbols):
                    if symbol not in predictions:
                        predictions[symbol] = []
                    
                    if hasattr(pred_outputs[i], 'cpu'):
                        pred_array = pred_outputs[i].cpu().numpy()
                    else:
                        pred_array = pred_outputs[i]
                    
                    predictions[symbol].append({
                        'prediction': pred_array,
                        'target': targets[i].numpy(),
                        'index': batch['index'][i].item()
                    })
                    
                successful_predictions += len(symbols)
                
                # 定期清理GPU内存
                if batch_idx % 5 == 0 and actual_device.type == 'cuda':
                    torch.cuda.empty_cache()
                    
            except Exception as e:
                print(f"⚠️  批次 {batch_idx} 推理失败: {e}")
                # 如果是CUDA错误，立即停止
                if "cuda" in str(e).lower() and "kernel" in str(e).lower():
                    print("🛑 检测到CUDA内核错误，停止推理")
                    break
                continue
    
    print(f"✅ 智能推理完成，成功处理 {successful_predictions} 个样本，涉及 {len(predictions)} 个股票")
    
    # 清理内存
    if actual_device.type == 'cuda':
        torch.cuda.empty_cache()
    
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
    parser = argparse.ArgumentParser(description="Qlib测试脚本智能设备版本")
    parser.add_argument("--device", type=str, default="cuda:0", help="请求的设备类型")
    
    args = parser.parse_args()
    
    print("🚀 Qlib测试脚本智能设备版本")
    print("🧠 自动检测CUDA兼容性并智能选择最佳设备")
    
    # 智能设备选择
    device, reason = smart_device_selection(args.device)
    print(f"💻 最终选择设备: {device} ({reason})")
    
    # 加载配置
    try:
        config_instance = Config()
        config = config_instance.__dict__
        
        run_config = {
            'device': str(device),
            'data_path': config['dataset_path'],
            'tokenizer_path': config.get('finetuned_tokenizer_path', config['pretrained_tokenizer_path']),
            'model_path': config.get('finetuned_predictor_path', config['pretrained_predictor_path']),
            'max_context': config['max_context'],
            'predict_window': config['predict_window'],
            'clip': config['clip'],
            'T': config.get('inference_T', 0.6),
            'top_k': config.get('inference_top_k', 0),
            'top_p': config.get('inference_top_p', 0.9),
            'lookback_window': config['lookback_window'],
            'pretrained_tokenizer_path': config['pretrained_tokenizer_path'],
            'pretrained_predictor_path': config['pretrained_predictor_path']
        }
        
        print("✅ 配置加载成功")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 智能修复模型路径
    run_config = fix_model_paths_smart(run_config)
    if run_config is None:
        print("❌ 模型路径修复失败")
        return 1
    
    # 加载测试数据
    test_data_path = os.path.join(run_config['data_path'], 'test_data.pkl')
    if not os.path.exists(test_data_path):
        print(f"❌ 测试数据文件不存在: {test_data_path}")
        return 1
    
    try:
        print(f"🔄 加载测试数据: {test_data_path}")
        with open(test_data_path, 'rb') as f:
            test_data = pickle.load(f)
        print(f"✅ 测试数据加载成功，包含 {len(test_data)} 个股票")
                
    except Exception as e:
        print(f"❌ 测试数据加载失败: {e}")
        return 1
    
    # 智能预测生成
    try:
        predictions = generate_predictions_smart(run_config, test_data, device)
        
        if predictions:
            eval_results = evaluate_predictions(predictions)
            
            if eval_results:
                print("🎉 智能测试完成!")
                print(f"🏆 使用设备: {device}")
                print(f"📊 处理样本: {eval_results['num_samples']}")
                return 0
            else:
                print("❌ 评估失败")
                return 1
        else:
            print("❌ 没有生成任何预测")
            return 1
            
    except Exception as e:
        print(f"❌ 智能预测失败: {e}")
        print("\n💡 建议:")
        print("1. 如果是CUDA问题，PyTorch版本可能需要更新")
        print("2. 您的RTX 5060 Ti需要更新的PyTorch版本支持")
        print("3. 当前版本会自动回退到CPU，这是正常的")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)