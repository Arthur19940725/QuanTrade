#!/usr/bin/env python
import os
# 强制使用CPU，禁用CUDA
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# 导入其他模块
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if 'finetune' in current_dir else current_dir
finetune_dir = os.path.join(project_root, 'finetune')
sys.path.insert(0, project_root)
sys.path.insert(0, finetune_dir)

# 运行CPU版本的qlib测试
if __name__ == "__main__":
    print("🚀 强制CPU模式运行")
    print("💻 已禁用CUDA，使用CPU进行推理")
    
    # 导入并运行智能设备版本
    try:
        from qlib_test_smart_device import main
        import argparse
        
        # 模拟命令行参数
        sys.argv = ['qlib_test_cpu_only.py', '--device', 'cpu']
        main()
    except ImportError:
        print("❌ 请确保qlib_test_smart_device.py存在")
