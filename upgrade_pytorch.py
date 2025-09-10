#!/usr/bin/env python
import subprocess
import sys

def upgrade_pytorch():
    print("🚀 开始升级PyTorch以支持RTX 5060 Ti...")
    
    commands = [
        # 卸载旧版本
        [sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"],
        # 安装新版本
        [sys.executable, "-m", "pip", "install", "torch>=2.2.0", "torchvision", "torchaudio", 
         "--index-url", "https://download.pytorch.org/whl/cu121"]
    ]
    
    for cmd in commands:
        print(f"执行: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e}")
            return False
    
    print("✅ PyTorch升级完成!")
    return True

if __name__ == "__main__":
    upgrade_pytorch()
