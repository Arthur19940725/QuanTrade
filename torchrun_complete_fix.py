#!/usr/bin/env python
"""
torchrun完整修复方案
解决Windows下的libuv问题，并处理训练流程
"""
import os
import sys
import argparse

def setup_training_environment():
    """设置训练环境"""
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

def train_tokenizer_first():
    """先训练分词器"""
    print("🔧 步骤1: 训练分词器")
    try:
        from train_tokenizer import main as train_tokenizer_main
        from config import Config
        
        config_instance = Config()
        config = config_instance.__dict__
        
        print("✅ 开始训练分词器...")
        train_tokenizer_main(config)
        print("✅ 分词器训练完成")
        return True
    except Exception as e:
        print(f"❌ 分词器训练失败: {e}")
        return False

def train_predictor():
    """训练预测器"""
    print("🔧 步骤2: 训练预测器")
    try:
        from train_predictor import main as train_predictor_main
        from config import Config
        
        config_instance = Config()
        config = config_instance.__dict__
        
        # 修改配置，使用预训练的分词器而不是微调的
        if not os.path.exists(config['finetuned_tokenizer_path']):
            print("⚠️  微调分词器不存在，使用预训练分词器")
            config['finetuned_tokenizer_path'] = config['pretrained_tokenizer_path']
        
        print("✅ 开始训练预测器...")
        train_predictor_main(config)
        print("✅ 预测器训练完成")
        return True
    except Exception as e:
        print(f"❌ 预测器训练失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Kronos训练完整方案")
    parser.add_argument("--standalone", action="store_true", help="单机模式")
    parser.add_argument("--nproc_per_node", type=int, default=1, help="每个节点的进程数")
    parser.add_argument("--train-tokenizer", action="store_true", help="先训练分词器")
    parser.add_argument("--train-predictor", action="store_true", help="训练预测器")
    parser.add_argument("--train-all", action="store_true", help="训练所有组件")
    parser.add_argument("script", nargs="?", help="要执行的脚本")
    
    args = parser.parse_args()
    
    print("🚀 Kronos训练完整方案")
    print("📋 解决Windows下torchrun libuv问题")
    
    # 设置环境
    setup_training_environment()
    
    success = True
    
    if args.train_all:
        print("🏃‍♂️ 完整训练流程 (分词器 + 预测器)")
        success &= train_tokenizer_first()
        if success:
            success &= train_predictor()
    elif args.train_tokenizer:
        success &= train_tokenizer_first()
    elif args.train_predictor or (args.script and "train_predictor" in args.script):
        success &= train_predictor()
    elif args.script and "train_tokenizer" in args.script:
        success &= train_tokenizer_first()
    else:
        print("❌ 请指定训练任务:")
        print("   --train-all: 训练分词器和预测器")
        print("   --train-tokenizer: 只训练分词器") 
        print("   --train-predictor: 只训练预测器")
        print("   或者直接指定脚本路径")
        return 1
    
    if success:
        print("🎉 训练完成!")
        return 0
    else:
        print("❌ 训练失败!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)