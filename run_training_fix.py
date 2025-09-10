#!/usr/bin/env python
"""
修复版本的训练启动脚本
解决Windows下torchrun的libuv问题
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_environment():
    """设置训练环境变量"""
    # 禁用libuv以避免Windows兼容性问题
    os.environ["USE_LIBUV"] = "0"
    
    # 设置单GPU分布式训练环境变量
    os.environ["WORLD_SIZE"] = "1"
    os.environ["RANK"] = "0"
    os.environ["LOCAL_RANK"] = "0"
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    
    print("✅ 环境变量设置完成:")
    print(f"   USE_LIBUV: {os.environ.get('USE_LIBUV')}")
    print(f"   WORLD_SIZE: {os.environ.get('WORLD_SIZE')}")
    print(f"   RANK: {os.environ.get('RANK')}")
    print(f"   LOCAL_RANK: {os.environ.get('LOCAL_RANK')}")

def main():
    """主函数"""
    print("🚀 启动Kronos预测器训练...")
    print("📋 修复Windows下torchrun libuv问题")
    
    # 设置环境
    setup_environment()
    
    # 导入训练模块
    try:
        # 添加finetune目录到路径
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finetune'))
        
        from train_predictor import main as train_main
        from config import Config
        
        print("✅ 成功导入训练模块")
        
        # 创建配置
        config_instance = Config()
        config = config_instance.__dict__
        
        print("✅ 配置加载完成")
        print("🏃‍♂️ 开始训练...")
        
        # 启动训练
        train_main(config)
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("💡 请确保已正确安装所有依赖")
        return 1
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        return 1
    
    print("🎉 训练完成!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)