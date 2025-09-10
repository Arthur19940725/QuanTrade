#!/usr/bin/env python3
"""
修复版本的训练脚本，解决Windows上的libuv问题
"""
import os
import sys

# 在导入任何PyTorch相关模块之前设置环境变量
os.environ.setdefault("USE_LIBUV", "0")
os.environ.setdefault("WORLD_SIZE", "1") 
os.environ.setdefault("RANK", "0")
os.environ.setdefault("LOCAL_RANK", "0")

# 设置项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'finetune'))

# 现在可以安全导入训练脚本
try:
    # 导入并运行原始训练脚本
    from finetune.config import Config
    from finetune.train_predictor import main
    
    print("=" * 60)
    print("Kronos Predictor Training - Windows Fixed Version")
    print("=" * 60)
    print(f"USE_LIBUV: {os.environ.get('USE_LIBUV', 'not set')}")
    print(f"WORLD_SIZE: {os.environ.get('WORLD_SIZE', 'not set')}")
    print(f"RANK: {os.environ.get('RANK', 'not set')}")
    print(f"LOCAL_RANK: {os.environ.get('LOCAL_RANK', 'not set')}")
    print("=" * 60)
    
    # 加载配置并运行
    config_instance = Config()
    main(config_instance.__dict__)
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保您在正确的目录中运行此脚本")
    sys.exit(1)
except Exception as e:
    print(f"运行错误: {e}")
    sys.exit(1)