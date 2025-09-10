"""
Gym到Gymnasium兼容性补丁
自动将qlib中的gym导入替换为gymnasium
"""

import sys
import importlib.util
from pathlib import Path

def patch_qlib_gym_imports():
    """修补qlib中的gym导入"""
    try:
        import gymnasium as gym
        
        # 将gymnasium注册为gym模块
        sys.modules['gym'] = gym
        
        print("✓ 成功将gymnasium注册为gym模块")
        return True
        
    except ImportError:
        print("✗ 未找到gymnasium，请先安装: pip install gymnasium[classic_control]")
        return False

def apply_patch():
    """应用补丁"""
    success = patch_qlib_gym_imports()
    
    if success:
        print("✓ Gym兼容性补丁应用成功")
    else:
        print("✗ 补丁应用失败")
    
    return success

if __name__ == "__main__":
    apply_patch()
