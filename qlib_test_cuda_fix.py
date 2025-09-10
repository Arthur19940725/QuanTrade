#!/usr/bin/env python
"""
qlib_test.py CUDA修复版本
专门解决CUDA运行时的模型路径和兼容性问题
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

def check_cuda_compatibility():
    """检查CUDA兼容性"""
    print("🔍 检查CUDA兼容性...")
    
    if not torch.cuda.is_available():
        print("❌ CUDA不可用")
        return False, "cpu"
    
    print(f"✅ CUDA可用，版本: {torch.version.cuda}")
    print(f"🖥️  GPU数量: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        gpu_name = torch.cuda.get_device_name(i)
        gpu_capability = torch.cuda.get_device_capability(i)
        print(f"   GPU {i}: {gpu_name} (计算能力: sm_{gpu_capability[0]}{gpu_capability[1]})")
    
    # 检查是否有兼容性警告
    try:
        test_tensor = torch.zeros(1).cuda()
        print("✅ CUDA张量创建成功")
        return True, "cuda:0"
    except Exception as e:
        print(f"⚠️  CUDA兼容性问题: {e}")
        print("💡 建议使用CPU模式")
        return False, "cpu"

def fix_model_paths_for_cuda(config):
    """为CUDA运行修复模型路径"""
    print("🔧 修复CUDA模式下的模型路径...")
    
    # 检查并修复分词器路径
    tokenizer_path = config.get('tokenizer_path', config.get('finetuned_tokenizer_path'))
    if not tokenizer_path or not os.path.exists(tokenizer_path):
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
        else:
            print(f"❌ 预训练分词器路径也不存在: {pretrained_tokenizer}")
            return None
    
    # 检查并修复预测器路径
    model_path = config.get('model_path', config.get('finetuned_predictor_path'))
    if not model_path or not os.path.exists(model_path):
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
        else:
            print(f"❌ 预训练预测器路径也不存在: {pretrained_predictor}")
            return None
    
    return config

def load_models_cuda_safe(config, device):
    """CUDA安全的模型加载"""
    print(f"🔄 在设备 {device} 上安全加载模型...")
    
    try:
        # 加载分词器
        print(f"📁 分词器路径: {config['tokenizer_path']}")
        tokenizer = KronosTokenizer.from_pretrained(config['tokenizer_path'])
        
        # 安全地移动到设备
        if device.startswith('cuda'):
            try:
                tokenizer = tokenizer.cuda()
                print("✅ 分词器成功移动到CUDA")
            except Exception as e:
                print(f"⚠️  分词器CUDA移动失败: {e}")
                print("🔄 回退到CPU")
                tokenizer = tokenizer.cpu()
                device = 'cpu'
        else:
            tokenizer = tokenizer.cpu()
        
        tokenizer = tokenizer.eval()
        print("✅ 分词器加载成功")
        
        # 加载预测器
        print(f"📁 预测器路径: {config['model_path']}")
        model = Kronos.from_pretrained(config['model_path'])
        
        # 安全地移动到设备
        if device.startswith('cuda'):
            try:
                model = model.cuda()
                print("✅ 预测器成功移动到CUDA")
            except Exception as e:
                print(f"⚠️  预测器CUDA移动失败: {e}")
                print("🔄 回退到CPU")
                model = model.cpu()
                device = 'cpu'
                tokenizer = tokenizer.cpu()  # 确保两个模型在同一设备上
        else:
            model = model.cpu()
        
        model = model.eval()
        print("✅ 预测器加载成功")
        
        return tokenizer, model, device
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        raise

class QlibInferenceDataset(Dataset):
    """CUDA优化的推理数据集"""
    
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
                df_values = df.values.astype(np.float32)  # 使用float32以节省GPU内存
                df_normalized = np.clip(df_values, -clip, clip)
                
                # 创建滑动窗口样本（减少样本数量以节省内存）
                step = max(1, (len(df_normalized) - lookback_window - predict_window + 1) // 10)  # 每10个取1个
                for i in range(0, len(df_normalized) - lookback_window - predict_window + 1, step):
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

def generate_predictions_cuda(config, test_data, device):
    """CUDA优化的预测生成"""
    print("🔄 开始CUDA优化预测...")
    
    # 加载模型
    tokenizer, model, actual_device = load_models_cuda_safe(config, device)
    
    # 创建数据集（减少数据量以适应GPU内存）
    print("📊 创建优化数据集...")
    dataset = QlibInferenceDataset(
        test_data, 
        config['lookback_window'], 
        config['predict_window'],
        config['clip']
    )
    
    print(f"📊 数据集大小: {len(dataset)}")
    
    # 创建数据加载器（小批次以节省GPU内存）
    batch_size = 2 if actual_device.startswith('cuda') else 10  # CUDA使用更小的批次
    dataloader = DataLoader(
        dataset, 
        batch_size=batch_size,
        shuffle=False,
        pin_memory=(actual_device.startswith('cuda'))
    )
    
    predictions = {}
    successful_predictions = 0
    
    print(f"🚀 开始推理（批次大小: {batch_size}，设备: {actual_device}）...")
    
    with torch.no_grad():
        for batch_idx, batch in enumerate(tqdm(dataloader, desc="CUDA推理")):
            try:
                inputs = batch['input'].to(actual_device)
                targets = batch['target']
                symbols = batch['symbol']
                
                # 创建时间戳（简化处理）
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
                    
                    # 处理预测输出
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
                
                # 每处理10个批次清理一次GPU内存
                if batch_idx % 10 == 0 and actual_device.startswith('cuda'):
                    torch.cuda.empty_cache()
                    
            except Exception as e:
                print(f"⚠️  批次 {batch_idx} 推理失败: {e}")
                # CUDA内存不足时的处理
                if "out of memory" in str(e).lower() and actual_device.startswith('cuda'):
                    print("🔄 GPU内存不足，清理缓存...")
                    torch.cuda.empty_cache()
                continue
    
    print(f"✅ 推理完成，成功处理 {successful_predictions} 个样本，涉及 {len(predictions)} 个股票")
    
    # 最终清理GPU内存
    if actual_device.startswith('cuda'):
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
    parser = argparse.ArgumentParser(description="Qlib测试脚本CUDA修复版本")
    parser.add_argument("--device", type=str, default="cuda:0", help="设备类型")
    parser.add_argument("--force-cpu", action="store_true", help="强制使用CPU")
    
    args = parser.parse_args()
    
    print("🚀 Qlib测试脚本CUDA修复版本")
    print(f"💻 请求设备: {args.device}")
    
    # 检查CUDA兼容性
    if args.force_cpu:
        print("⚠️  强制使用CPU模式")
        device = torch.device('cpu')
    else:
        cuda_ok, recommended_device = check_cuda_compatibility()
        if cuda_ok and args.device.startswith('cuda'):
            device = torch.device(args.device)
            print(f"✅ 使用CUDA设备: {device}")
        else:
            device = torch.device('cpu')
            print(f"⚠️  回退到CPU设备: {device}")
    
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
            'predict_window': config['predict_window'],
            'clip': config['clip'],
            'T': config.get('inference_T', 0.6),
            'top_k': config.get('inference_top_k', 0),
            'top_p': config.get('inference_top_p', 0.9),
            'sample_count': config.get('inference_sample_count', 1),
            'batch_size': config.get('backtest_batch_size', 1000),
            'lookback_window': config['lookback_window'],
            'pretrained_tokenizer_path': config['pretrained_tokenizer_path'],
            'pretrained_predictor_path': config['pretrained_predictor_path']
        }
        
        print("✅ 配置加载成功")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 修复模型路径
    run_config = fix_model_paths_for_cuda(run_config)
    if run_config is None:
        print("❌ 模型路径修复失败")
        return 1
    
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
        predictions = generate_predictions_cuda(run_config, test_data, str(device))
        
        if predictions:
            # 评估结果
            eval_results = evaluate_predictions(predictions)
            
            if eval_results:
                print("🎉 CUDA测试完成!")
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
        
        # 如果是CUDA相关错误，建议使用CPU
        if "cuda" in str(e).lower() or "gpu" in str(e).lower():
            print("\n💡 检测到CUDA相关错误，建议尝试:")
            print("   python qlib_test_cuda_fix.py --force-cpu")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)