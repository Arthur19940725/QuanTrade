#!/usr/bin/env python
"""
torchrun CPU版本修复方案
解决Windows下的libuv问题，并强制使用CPU训练
"""
import os
import sys
import argparse

def setup_environment():
    """设置环境"""
    # 禁用libuv
    os.environ["USE_LIBUV"] = "0"
    os.environ["WORLD_SIZE"] = "1"
    os.environ["RANK"] = "0"
    os.environ["LOCAL_RANK"] = "0"
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    
    # 强制使用CPU
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    
    # 添加路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finetune'))

def fix_model_paths():
    """修复模型路径"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查并修复分词器路径
    tokenizer_path = os.path.join(base_dir, "models", "models--NeoQuasar--Kronos-Tokenizer-base")
    snapshot_dirs = []
    if os.path.exists(os.path.join(tokenizer_path, "snapshots")):
        snapshots_dir = os.path.join(tokenizer_path, "snapshots")
        snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
    
    if snapshot_dirs:
        actual_tokenizer_path = os.path.join(tokenizer_path, "snapshots", snapshot_dirs[0])
        print(f"✅ 找到分词器路径: {actual_tokenizer_path}")
    else:
        actual_tokenizer_path = tokenizer_path
        print(f"⚠️  使用默认分词器路径: {actual_tokenizer_path}")
    
    # 检查预测器路径
    predictor_path = os.path.join(base_dir, "models", "models--NeoQuasar--Kronos-small")
    snapshot_dirs = []
    if os.path.exists(os.path.join(predictor_path, "snapshots")):
        snapshots_dir = os.path.join(predictor_path, "snapshots")
        snapshot_dirs = [d for d in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, d))]
    
    if snapshot_dirs:
        actual_predictor_path = os.path.join(predictor_path, "snapshots", snapshot_dirs[0])
        print(f"✅ 找到预测器路径: {actual_predictor_path}")
    else:
        actual_predictor_path = predictor_path
        print(f"⚠️  使用默认预测器路径: {actual_predictor_path}")
    
    return actual_tokenizer_path, actual_predictor_path

def modify_training_script_for_cpu():
    """修改训练脚本以支持CPU训练"""
    # 修改setup_ddp函数强制使用CPU
    training_utils_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finetune', 'utils', 'training_utils.py')
    
    try:
        with open(training_utils_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换CUDA相关代码
        if 'torch.cuda.set_device' in content:
            content = content.replace('torch.cuda.set_device(local_rank)', '# torch.cuda.set_device(local_rank)  # Disabled for CPU')
            content = content.replace('torch.cuda.set_device(0)', '# torch.cuda.set_device(0)  # Disabled for CPU')
        
        with open(training_utils_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 训练脚本已修改为CPU模式")
    except Exception as e:
        print(f"⚠️  无法修改训练脚本: {e}")

def train_predictor_cpu():
    """使用CPU训练预测器"""
    try:
        # 修改训练脚本
        modify_training_script_for_cpu()
        
        from train_predictor import main as train_predictor_main
        from config import Config
        
        # 获取修复的路径
        tokenizer_path, predictor_path = fix_model_paths()
        
        # 创建配置并修复路径
        config_instance = Config()
        config = config_instance.__dict__
        
        # 使用正确的路径
        config['pretrained_tokenizer_path'] = tokenizer_path
        config['pretrained_predictor_path'] = predictor_path
        config['finetuned_tokenizer_path'] = tokenizer_path
        
        # 减少批次大小以适应CPU
        config['batch_size'] = 10  # 减少批次大小
        config['epochs'] = 5       # 减少训练轮数用于测试
        
        print("✅ 配置修复完成，开始CPU训练预测器...")
        print("💻 使用CPU模式，训练速度会较慢")
        train_predictor_main(config)
        print("✅ 预测器训练完成")
        return True
    except Exception as e:
        print(f"❌ 预测器训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Kronos CPU训练修复方案")
    parser.add_argument("--standalone", action="store_true", help="单机模式")
    parser.add_argument("--nproc_per_node", type=int, default=1, help="每个节点的进程数")
    parser.add_argument("--train-predictor", action="store_true", help="训练预测器")
    parser.add_argument("--cpu", action="store_true", help="强制使用CPU")
    parser.add_argument("script", nargs="?", help="脚本路径")
    
    args = parser.parse_args()
    
    print("🚀 Kronos CPU训练修复方案")
    print("📋 解决Windows下torchrun libuv + CUDA兼容性问题")
    print("💻 强制使用CPU训练")
    
    # 设置环境
    setup_environment()
    
    success = False
    
    if args.train_predictor or (args.script and "train_predictor" in args.script):
        success = train_predictor_cpu()
    else:
        print("❌ 请指定训练任务:")
        print("   --train-predictor: 训练预测器")
        print("   或指定脚本路径")
        return 1
    
    if success:
        print("🎉 CPU训练成功完成!")
        return 0
    else:
        print("❌ 训练失败!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)