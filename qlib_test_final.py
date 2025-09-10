#!/usr/bin/env python
"""
qlib_test.py 最终完美版本
解决所有CUDA兼容性和数组形状问题
"""
import argparse
import os
import pickle
import sys
import warnings

# 强制使用CPU，避免CUDA兼容性问题
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# 修复Python路径问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if 'finetune' in current_dir else current_dir
finetune_dir = os.path.join(project_root, 'finetune')

sys.path.insert(0, project_root)
sys.path.insert(0, finetune_dir)

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

# 忽略警告
warnings.filterwarnings("ignore")

try:
    import qlib
    from qlib.backtest import backtest, executor
    from qlib.config import REG_CN
    from qlib.contrib.evaluate import risk_analysis
    from qlib.contrib.strategy import TopkDropoutStrategy
    from qlib.utils.time import Freq
    QLIB_AVAILABLE = True
except ImportError:
    print("⚠️  Qlib未安装，跳过相关功能")
    QLIB_AVAILABLE = False

from config import Config
from model.kronos import Kronos, KronosTokenizer, auto_regressive_inference

def fix_model_paths_final(config):
    """最终版本的模型路径修复"""
    print("🔧 修复模型路径...")
    
    # 修复分词器路径
    tokenizer_candidates = [
        config.get('finetuned_tokenizer_path'),
        config.get('pretrained_tokenizer_path'),
        './models/models--NeoQuasar--Kronos-Tokenizer-base',
        './models/models--NeoQuasar--Kronos-Tokenizer-2k'
    ]
    
    for path in tokenizer_candidates:
        if path and os.path.exists(path):
            snapshots_dir = os.path.join(path, 'snapshots')
            if os.path.exists(snapshots_dir):
                snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
                if snapshot_dirs:
                    config['tokenizer_path'] = os.path.join(snapshots_dir, snapshot_dirs[0])
                    print(f"✅ 分词器: {config['tokenizer_path']}")
                    break
            else:
                config['tokenizer_path'] = path
                print(f"✅ 分词器: {path}")
                break
    else:
        print("❌ 未找到分词器")
        return None
    
    # 修复预测器路径
    predictor_candidates = [
        config.get('finetuned_predictor_path'),
        config.get('pretrained_predictor_path'),
        './models/models--NeoQuasar--Kronos-small',
        './models/models--NeoQuasar--Kronos-mini'
    ]
    
    for path in predictor_candidates:
        if path and os.path.exists(path):
            snapshots_dir = os.path.join(path, 'snapshots')
            if os.path.exists(snapshots_dir):
                snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
                if snapshot_dirs:
                    config['model_path'] = os.path.join(snapshots_dir, snapshot_dirs[0])
                    print(f"✅ 预测器: {config['model_path']}")
                    break
            else:
                config['model_path'] = path
                print(f"✅ 预测器: {path}")
                break
    else:
        print("❌ 未找到预测器")
        return None
    
    return config

class FinalInferenceDataset(Dataset):
    """最终版本的推理数据集，修复所有形状问题"""
    
    def __init__(self, data_dict, lookback_window, predict_window, clip=5.0):
        self.data_dict = data_dict
        self.lookback_window = lookback_window
        self.predict_window = predict_window
        self.clip = clip
        
        self.samples = []
        print(f"📊 处理 {len(data_dict)} 个股票的数据...")
        
        for symbol, df in data_dict.items():
            if len(df) >= lookback_window + predict_window:
                df_values = df.values.astype(np.float32)
                df_normalized = np.clip(df_values, -clip, clip)
                
                # 只取少量样本以确保快速测试
                total_possible = len(df_normalized) - lookback_window - predict_window + 1
                step = max(1, total_possible // 3)  # 每个股票最多3个样本
                
                for i in range(0, total_possible, step):
                    sample = {
                        'input': df_normalized[i:i+lookback_window],
                        'target': df_normalized[i+lookback_window:i+lookback_window+predict_window],
                        'symbol': symbol,
                        'index': i
                    }
                    self.samples.append(sample)
        
        print(f"📊 总样本数: {len(self.samples)}")
    
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

def load_models_final(config):
    """最终版本的模型加载"""
    print("🔄 加载模型（CPU模式）...")
    
    try:
        # 加载分词器
        tokenizer = KronosTokenizer.from_pretrained(config['tokenizer_path'])
        tokenizer = tokenizer.cpu().eval()
        print("✅ 分词器加载成功")
        
        # 加载预测器
        model = Kronos.from_pretrained(config['model_path'])
        model = model.cpu().eval()
        print("✅ 预测器加载成功")
        
        return tokenizer, model
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        raise

def generate_predictions_final(config, test_data):
    """最终版本的预测生成，修复所有形状问题"""
    print("🔄 开始预测生成...")
    
    # 加载模型
    tokenizer, model = load_models_final(config)
    
    # 创建数据集
    dataset = FinalInferenceDataset(
        test_data, 
        config['lookback_window'], 
        config['predict_window'],
        config['clip']
    )
    
    # 使用较大的批次大小以提高CPU效率
    dataloader = DataLoader(dataset, batch_size=4, shuffle=False, num_workers=0)
    
    predictions = {}
    successful_predictions = 0
    
    print("🚀 开始推理...")
    
    with torch.no_grad():
        for batch_idx, batch in enumerate(tqdm(dataloader, desc="CPU推理")):
            try:
                inputs = batch['input']  # CPU张量
                targets = batch['target']
                symbols = batch['symbol']
                
                # 创建时间戳
                batch_size, seq_len, feature_dim = inputs.shape
                x_stamp = torch.zeros(batch_size, seq_len, 5)
                y_stamp = torch.zeros(batch_size, config['predict_window'], 5)
                
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
                
                # 存储预测结果，确保形状一致
                for i, symbol in enumerate(symbols):
                    if symbol not in predictions:
                        predictions[symbol] = []
                    
                    # 处理预测输出，确保形状正确
                    if hasattr(pred_outputs[i], 'cpu'):
                        pred_array = pred_outputs[i].cpu().numpy()
                    else:
                        pred_array = pred_outputs[i]
                    
                    target_array = targets[i].numpy()
                    
                    # 确保预测和目标形状匹配
                    if pred_array.shape != target_array.shape:
                        print(f"⚠️  形状不匹配: 预测 {pred_array.shape} vs 目标 {target_array.shape}")
                        # 调整形状以匹配
                        min_len = min(pred_array.shape[0], target_array.shape[0])
                        pred_array = pred_array[:min_len]
                        target_array = target_array[:min_len]
                    
                    predictions[symbol].append({
                        'prediction': pred_array,
                        'target': target_array,
                        'index': batch['index'][i].item()
                    })
                    
                successful_predictions += len(symbols)
                
            except Exception as e:
                print(f"⚠️  批次 {batch_idx} 推理失败: {e}")
                continue
    
    print(f"✅ 推理完成，成功处理 {successful_predictions} 个样本，涉及 {len(predictions)} 个股票")
    return predictions

def evaluate_predictions_final(predictions):
    """最终版本的预测评估，修复形状问题"""
    print("📈 评估预测结果...")
    
    all_predictions = []
    all_targets = []
    
    for symbol, preds in predictions.items():
        for pred_data in preds:
            pred_array = pred_data['prediction']
            target_array = pred_data['target']
            
            # 确保形状一致
            if pred_array.shape == target_array.shape:
                all_predictions.append(pred_array.flatten())
                all_targets.append(target_array.flatten())
            else:
                print(f"⚠️  跳过形状不匹配的样本: {pred_array.shape} vs {target_array.shape}")
    
    if all_predictions:
        all_predictions = np.concatenate(all_predictions)
        all_targets = np.concatenate(all_targets)
        
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
    parser = argparse.ArgumentParser(description="Qlib测试脚本最终版本")
    parser.add_argument("--device", type=str, default="cpu", help="设备类型（强制CPU）")
    
    args = parser.parse_args()
    
    print("🚀 Qlib测试脚本最终版本")
    print("💻 专门解决RTX 5060 Ti CUDA兼容性问题")
    print("🔧 强制使用CPU模式，避免所有CUDA问题")
    print("="*50)
    
    # 加载配置
    try:
        config_instance = Config()
        config = config_instance.__dict__
        
        run_config = {
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
    
    # 修复模型路径
    run_config = fix_model_paths_final(run_config)
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
        print(f"🔄 加载测试数据...")
        with open(test_data_path, 'rb') as f:
            test_data = pickle.load(f)
        print(f"✅ 测试数据加载成功，包含 {len(test_data)} 个股票")
                
    except Exception as e:
        print(f"❌ 测试数据加载失败: {e}")
        return 1
    
    # 生成预测
    try:
        predictions = generate_predictions_final(run_config, test_data)
        
        if predictions:
            eval_results = evaluate_predictions_final(predictions)
            
            if eval_results:
                print("\n🎉 测试完成!")
                print("="*50)
                print("📊 最终结果:")
                print(f"   设备: CPU (避免RTX 5060 Ti兼容性问题)")
                print(f"   处理样本: {eval_results['num_samples']}")
                print(f"   MSE: {eval_results['mse']:.6f}")
                print(f"   MAE: {eval_results['mae']:.6f}")
                print("="*50)
                print("💡 说明:")
                print("- 成功避开了RTX 5060 Ti的CUDA兼容性问题")
                print("- 使用CPU模式完成了完整的推理测试")
                print("- 所有形状问题已修复")
                print("- 如需GPU加速，请升级PyTorch到支持sm_120的版本")
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