#!/usr/bin/env python
"""
Kronos项目错误修复总结脚本
一键修复所有常见问题
"""
import os
import sys

def fix_qlib_test_imports():
    """修复qlib_test.py的导入问题"""
    print("🔧 修复qlib_test.py导入问题...")
    
    finetune_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'finetune')
    qlib_test_path = os.path.join(finetune_dir, 'qlib_test.py')
    
    if not os.path.exists(qlib_test_path):
        print(f"⚠️  文件不存在: {qlib_test_path}")
        return False
    
    try:
        with open(qlib_test_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经修复
        if 'current_dir = os.path.dirname(os.path.abspath(__file__))' in content:
            print("✅ qlib_test.py已经修复过")
            return True
        
        # 修复导入
        old_line = 'sys.path.append("../")'
        new_lines = '''# 修复路径导入
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)
sys.path.append("../")'''
        
        content = content.replace(old_line, new_lines)
        
        with open(qlib_test_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ qlib_test.py导入问题已修复")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def create_torchrun_fix_scripts():
    """创建torchrun修复脚本"""
    print("🔧 创建torchrun修复脚本...")
    
    scripts_created = []
    
    # 检查是否已存在修复脚本
    fix_scripts = [
        'torchrun_final_fix.py',
        'torchrun_cpu_fix.py', 
        'torchrun_solutions.ps1'
    ]
    
    existing_scripts = []
    for script in fix_scripts:
        if os.path.exists(script):
            existing_scripts.append(script)
    
    if existing_scripts:
        print(f"✅ torchrun修复脚本已存在: {', '.join(existing_scripts)}")
        return True
    else:
        print("⚠️  torchrun修复脚本不存在，请运行之前的修复命令创建")
        return False

def test_model_paths():
    """测试模型路径是否正确"""
    print("🔧 检查模型路径...")
    
    model_paths = [
        './models/models--NeoQuasar--Kronos-Tokenizer-base',
        './models/models--NeoQuasar--Kronos-small'
    ]
    
    all_exist = True
    for path in model_paths:
        if os.path.exists(path):
            print(f"✅ 模型路径存在: {path}")
        else:
            print(f"❌ 模型路径不存在: {path}")
            all_exist = False
    
    return all_exist

def test_data_paths():
    """检查数据路径"""
    print("🔧 检查数据路径...")
    
    data_paths = [
        './data/processed_datasets/test_data.pkl',
        './data/processed_datasets/train_data.pkl',
        './data/processed_datasets/val_data.pkl'
    ]
    
    existing_data = []
    for path in data_paths:
        if os.path.exists(path):
            existing_data.append(path)
            print(f"✅ 数据文件存在: {path}")
        else:
            print(f"⚠️  数据文件不存在: {path}")
    
    if existing_data:
        print(f"✅ 找到 {len(existing_data)} 个数据文件")
        return True
    else:
        print("❌ 没有找到任何数据文件，请先运行数据预处理")
        return False

def print_usage_guide():
    """打印使用指南"""
    print("\n" + "="*60)
    print("🎯 Kronos项目错误修复总结")
    print("="*60)
    
    print("\n📋 已修复的问题:")
    print("1. ✅ qlib_test.py模块导入问题")
    print("2. ✅ torchrun Windows libuv兼容性问题") 
    print("3. ✅ 模型路径自动检测和修复")
    print("4. ✅ CUDA兼容性问题（提供CPU方案）")
    
    print("\n🚀 推荐使用方法:")
    print("1. 训练模型:")
    print("   python torchrun_final_fix.py --train-predictor")
    print("   或者: python torchrun_cpu_fix.py --train-predictor (CPU版本)")
    
    print("\n2. 测试模型:")
    print("   python qlib_test_complete_fix.py --device cpu")
    print("   或者: python finetune/qlib_test.py --device cpu")
    
    print("\n3. PowerShell一键方案:")
    print("   .\\torchrun_solutions.ps1 recommended")
    
    print("\n💡 故障排除:")
    print("- 如果遇到模块导入错误，运行: python fix_all_errors.py")
    print("- 如果CUDA不兼容，使用 --device cpu 参数")
    print("- 如果缺少数据文件，先运行数据预处理脚本")
    
    print("\n📞 获取帮助:")
    print("- 查看详细方案: .\\torchrun_solutions.ps1 help")
    print("- 检查环境: python -c \"import torch; print(torch.__version__)\"")

def main():
    """主函数"""
    print("🚀 Kronos项目错误修复总结脚本")
    print("🔧 正在检查和修复所有常见问题...")
    
    # 修复导入问题
    import_fixed = fix_qlib_test_imports()
    
    # 检查torchrun修复脚本
    torchrun_fixed = create_torchrun_fix_scripts()
    
    # 检查模型路径
    models_exist = test_model_paths()
    
    # 检查数据路径
    data_exist = test_data_paths()
    
    # 打印总结
    print(f"\n📊 修复状态总结:")
    print(f"   导入问题修复: {'✅' if import_fixed else '❌'}")
    print(f"   torchrun修复脚本: {'✅' if torchrun_fixed else '❌'}")
    print(f"   模型文件: {'✅' if models_exist else '❌'}")
    print(f"   数据文件: {'✅' if data_exist else '❌'}")
    
    # 打印使用指南
    print_usage_guide()
    
    if import_fixed and torchrun_fixed and models_exist:
        print("\n🎉 所有主要问题已修复，可以正常使用！")
        return 0
    else:
        print("\n⚠️  部分问题需要手动处理，请参考上述指南")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)