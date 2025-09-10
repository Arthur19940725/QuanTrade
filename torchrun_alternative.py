#!/usr/bin/env python
"""
torchrun替代方案
完全绕过torchrun的libuv问题，直接启动分布式训练
"""
import os
import sys
import multiprocessing as mp
from multiprocessing import Process
import argparse

def worker_process(rank, world_size, script_path, args):
    """工作进程函数"""
    # 设置环境变量
    os.environ["USE_LIBUV"] = "0"
    os.environ["WORLD_SIZE"] = str(world_size)
    os.environ["RANK"] = str(rank)
    os.environ["LOCAL_RANK"] = str(rank)
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    
    print(f"🚀 启动进程 {rank}/{world_size}")
    
    # 添加项目路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 导入并运行训练脚本
        if script_path == "finetune/train_predictor.py":
            sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finetune'))
            from train_predictor import main as train_main
            from config import Config
            
            config_instance = Config()
            train_main(config_instance.__dict__)
        else:
            # 对于其他脚本，直接执行
            import subprocess
            subprocess.run([sys.executable, script_path] + args, check=True)
            
    except Exception as e:
        print(f"❌ 进程 {rank} 执行失败: {e}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="torchrun替代方案")
    parser.add_argument("--standalone", action="store_true", help="单机模式")
    parser.add_argument("--nproc_per_node", type=int, default=1, help="每个节点的进程数")
    parser.add_argument("script", help="要执行的脚本")
    parser.add_argument("script_args", nargs="*", help="脚本参数")
    
    args = parser.parse_args()
    
    print("🔧 torchrun替代方案启动器")
    print(f"📋 脚本: {args.script}")
    print(f"🖥️  进程数: {args.nproc_per_node}")
    
    if args.nproc_per_node == 1:
        # 单进程模式，直接在当前进程运行
        print("🏃‍♂️ 单进程模式")
        worker_process(0, 1, args.script, args.script_args)
    else:
        # 多进程模式
        print(f"🏃‍♂️ 多进程模式 ({args.nproc_per_node} 进程)")
        processes = []
        
        try:
            for rank in range(args.nproc_per_node):
                p = Process(
                    target=worker_process, 
                    args=(rank, args.nproc_per_node, args.script, args.script_args)
                )
                p.start()
                processes.append(p)
            
            # 等待所有进程完成
            for p in processes:
                p.join()
                
            print("🎉 所有进程完成")
            
        except KeyboardInterrupt:
            print("\n⚠️  用户中断，终止所有进程")
            for p in processes:
                p.terminate()
                p.join()
            return 130

if __name__ == "__main__":
    main()