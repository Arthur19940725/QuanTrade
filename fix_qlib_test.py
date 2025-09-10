#!/usr/bin/env python
"""
修复qlib_test.py的路径问题
"""
import os
import sys

def fix_qlib_test_imports():
    """修复qlib_test.py的导入路径问题"""
    
    # 获取路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    finetune_dir = os.path.join(current_dir, 'finetune')
    qlib_test_path = os.path.join(finetune_dir, 'qlib_test.py')
    
    print(f"🔧 修复qlib_test.py的导入问题")
    print(f"📁 文件路径: {qlib_test_path}")
    
    if not os.path.exists(qlib_test_path):
        print(f"❌ 文件不存在: {qlib_test_path}")
        return False
    
    try:
        # 读取原文件
        with open(qlib_test_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复导入路径
        old_imports = '''# Ensure project root is in the Python path
sys.path.append("../")
from config import Config

from model.kronos import Kronos, KronosTokenizer, auto_regressive_inference'''

        new_imports = '''# Ensure project root is in the Python path - FIXED
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)

from config import Config
from model.kronos import Kronos, KronosTokenizer, auto_regressive_inference'''
        
        # 替换内容
        if old_imports in content:
            content = content.replace(old_imports, new_imports)
            print("✅ 路径导入已修复")
        else:
            print("⚠️  未找到预期的导入模式，手动添加路径修复")
            # 在sys.path.append("../")之前添加路径修复
            if 'sys.path.append("../")\n' in content:
                content = content.replace(
                    'sys.path.append("../")\n',
                    '''# 路径修复 - 添加项目根目录和当前目录到Python路径
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)
sys.path.append("../")
'''
                )
        
        # 写回文件
        with open(qlib_test_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ qlib_test.py已修复")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def run_fixed_qlib_test(device="cpu"):
    """运行修复后的qlib测试"""
    
    # 设置环境
    current_dir = os.path.dirname(os.path.abspath(__file__))
    finetune_dir = os.path.join(current_dir, 'finetune')
    
    # 切换到finetune目录
    os.chdir(finetune_dir)
    
    print(f"🏃‍♂️ 运行修复后的qlib测试")
    print(f"📁 工作目录: {finetune_dir}")
    print(f"💻 设备: {device}")
    
    try:
        # 运行测试
        import subprocess
        result = subprocess.run([
            sys.executable, 'qlib_test.py', '--device', device
        ], capture_output=True, text=True)
        
        print("📤 输出:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        return False
    finally:
        # 切换回原目录
        os.chdir(current_dir)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="修复并运行qlib_test.py")
    parser.add_argument("--device", type=str, default="cpu", help="设备类型")
    parser.add_argument("--fix-only", action="store_true", help="只修复不运行")
    
    args = parser.parse_args()
    
    print("🚀 qlib_test.py修复工具")
    
    # 修复文件
    if fix_qlib_test_imports():
        print("✅ 文件修复成功")
        
        if not args.fix_only:
            # 运行测试
            if run_fixed_qlib_test(args.device):
                print("🎉 测试运行成功!")
                return 0
            else:
                print("❌ 测试运行失败")
                return 1
        else:
            print("📝 仅修复模式，跳过运行")
            return 0
    else:
        print("❌ 文件修复失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)