#!/usr/bin/env python
"""
torchrun最终修复方案
完全解决Windows下的所有问题
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

def train_predictor_with_fixed_paths():
    """使用修复的路径训练预测器"""
    try:
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
        config['finetuned_tokenizer_path'] = tokenizer_path  # 暂时使用预训练的
        
        print("✅ 配置修复完成，开始训练预测器...")
        train_predictor_main(config)
        print("✅ 预测器训练完成")
        return True
    except Exception as e:
        print(f"❌ 预测器训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def train_tokenizer_with_fixed_paths():
    """使用修复的路径训练分词器"""
    try:
        from train_tokenizer import main as train_tokenizer_main
        from config import Config
        
        # 获取修复的路径
        tokenizer_path, predictor_path = fix_model_paths()
        
        # 创建配置并修复路径
        config_instance = Config()
        config = config_instance.__dict__
        
        # 使用正确的路径
        config['pretrained_tokenizer_path'] = tokenizer_path
        
        print("✅ 配置修复完成，开始训练分词器...")
        train_tokenizer_main(config)
        print("✅ 分词器训练完成")
        return True
    except Exception as e:
        print(f"❌ 分词器训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Kronos训练最终修复方案")
    parser.add_argument("--standalone", action="store_true", help="单机模式")
    parser.add_argument("--nproc_per_node", type=int, default=1, help="每个节点的进程数")
    parser.add_argument("--train-tokenizer", action="store_true", help="训练分词器")
    parser.add_argument("--train-predictor", action="store_true", help="训练预测器")
    parser.add_argument("script", nargs="?", help="脚本路径")
    
    args = parser.parse_args()
    
    print("🚀 Kronos训练最终修复方案")
    print("📋 解决Windows下所有torchrun问题")
    
    # 设置环境
    setup_environment()
    
    success = False
    
    if args.train_predictor or (args.script and "train_predictor" in args.script):
        success = train_predictor_with_fixed_paths()
    elif args.train_tokenizer or (args.script and "train_tokenizer" in args.script):
        success = train_tokenizer_with_fixed_paths()
    else:
        print("❌ 请指定训练任务:")
        print("   --train-predictor: 训练预测器")
        print("   --train-tokenizer: 训练分词器")
        print("   或指定脚本路径")
        return 1
    
    if success:
        print("🎉 训练成功完成!")
        return 0
    else:
        print("❌ 训练失败!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)