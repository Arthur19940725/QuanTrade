#!/usr/bin/env python3
"""
加密货币预测应用打包脚本
使用PyInstaller将应用打包为Windows exe文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = [
        'pyinstaller', 'numpy', 'pandas', 'torch', 
        'matplotlib', 'requests', 'transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - 未安装")
    
    if missing_packages:
        print(f"\n需要安装以下包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['crypto_predictor_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models', 'models'),  # 包含模型文件
    ],
    hiddenimports=[
        'torch',
        'transformers',
        'huggingface_hub',
        'safetensors',
        'matplotlib.backends.backend_tkagg',
        'PIL._tkinter_finder',
        'numpy',
        'pandas',
        'requests',
        'gymnasium',
        'einops',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'testing',
        'pytest',
        'jupyter',
        'notebook',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KronosCryptoPredictor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False创建窗口应用
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='crypto_icon.ico',  # 如果有图标文件
)
'''
    
    with open('crypto_app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ 创建了 crypto_app.spec 文件")

def create_batch_files():
    """创建批处理文件"""
    
    # 安装依赖的批处理文件
    install_deps_bat = '''@echo off
echo 正在安装加密货币预测应用依赖...
python -m pip install --upgrade pip
pip install -r requirements_crypto_app.txt
echo 依赖安装完成！
pause
'''
    
    with open('install_dependencies.bat', 'w', encoding='utf-8') as f:
        f.write(install_deps_bat)
    
    # 运行应用的批处理文件
    run_app_bat = '''@echo off
echo 启动Kronos加密货币预测器...
python crypto_predictor_app.py
pause
'''
    
    with open('run_crypto_app.bat', 'w', encoding='utf-8') as f:
        f.write(run_app_bat)
    
    # 打包应用的批处理文件
    build_bat = '''@echo off
echo 正在打包Kronos加密货币预测器...
echo 这可能需要几分钟时间...

REM 检查PyInstaller是否安装
python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller未安装，正在安装...
    pip install pyinstaller
)

REM 使用spec文件打包
pyinstaller crypto_app.spec --clean --noconfirm

REM 检查打包结果
if exist "dist\\KronosCryptoPredictor.exe" (
    echo ✓ 打包成功！
    echo 可执行文件位置: dist\\KronosCryptoPredictor.exe
) else (
    echo ✗ 打包失败，请检查错误信息
)

pause
'''
    
    with open('build_crypto_app.bat', 'w', encoding='utf-8') as f:
        f.write(build_bat)
    
    print("✓ 创建了批处理文件")

def build_executable():
    """构建可执行文件"""
    try:
        # 清理旧的构建文件
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        print("开始打包应用...")
        
        # 使用PyInstaller打包
        cmd = [
            'pyinstaller',
            'crypto_app.spec',
            '--clean',
            '--noconfirm'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 打包成功！")
            
            exe_path = Path('dist/KronosCryptoPredictor.exe')
            if exe_path.exists():
                print(f"可执行文件: {exe_path.absolute()}")
                print(f"文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                return True
            else:
                print("✗ 可执行文件未找到")
                return False
        else:
            print("✗ 打包失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ 打包过程出错: {e}")
        return False

def create_installer_info():
    """创建安装说明"""
    info_content = '''# Kronos 加密货币价格预测器

## 应用说明
基于Kronos深度学习模型的加密货币价格预测应用，支持预测BTC、ETH、SOL的未来价格走势。

## 功能特性
- 🚀 基于先进的Kronos Transformer模型
- 📊 支持BTC、ETH、SOL价格预测
- 📈 实时数据获取（Binance API）
- 🎯 可视化预测结果
- 💾 预测结果保存功能
- 🖥️ 友好的图形用户界面

## 系统要求
- Windows 10/11 (64位)
- 至少4GB RAM
- 网络连接（获取实时数据）

## 使用方法

### 方法1: 直接运行exe文件
1. 双击 `KronosCryptoPredictor.exe`
2. 等待应用启动
3. 选择要预测的加密货币
4. 设置预测天数
5. 点击"开始预测"

### 方法2: Python环境运行
1. 确保安装了Python 3.8+
2. 运行 `install_dependencies.bat` 安装依赖
3. 运行 `run_crypto_app.bat` 启动应用

## 注意事项
- 首次运行需要下载模型文件，请确保网络连接
- 预测结果仅供参考，不构成投资建议
- GPU加速需要CUDA兼容的显卡

## 故障排除
1. 如果应用无法启动，请检查是否有杀毒软件阻止
2. 如果预测失败，请检查网络连接
3. 如果模型加载失败，应用会自动切换到模拟模式

## 技术支持
- 基于Kronos模型: https://github.com/NeoQuasar/Kronos
- 问题反馈: 请提交Issue

## 版本信息
版本: 1.0.0
构建日期: {build_date}
Python版本: {python_version}
'''
    
    from datetime import datetime
    info_content = info_content.format(
        build_date=datetime.now().strftime('%Y-%m-%d'),
        python_version=sys.version.split()[0]
    )
    
    with open('README_应用说明.md', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print("✓ 创建了应用说明文档")

def main():
    """主函数"""
    print("=== Kronos 加密货币预测应用打包工具 ===")
    
    # 检查依赖
    print("\n1. 检查依赖...")
    if not check_dependencies():
        print("请先安装必要的依赖包")
        return
    
    # 创建配置文件
    print("\n2. 创建配置文件...")
    create_spec_file()
    create_batch_files()
    create_installer_info()
    
    # 询问是否立即打包
    response = input("\n是否立即开始打包? (y/n): ").lower().strip()
    if response == 'y':
        print("\n3. 开始打包...")
        success = build_executable()
        
        if success:
            print("\n🎉 打包完成！")
            print("\n生成的文件:")
            print("- dist/KronosCryptoPredictor.exe (主程序)")
            print("- build_crypto_app.bat (打包脚本)")
            print("- run_crypto_app.bat (运行脚本)")
            print("- install_dependencies.bat (依赖安装脚本)")
            print("- README_应用说明.md (使用说明)")
        else:
            print("\n❌ 打包失败，请检查错误信息")
    else:
        print("\n配置文件已创建，可以稍后运行 build_crypto_app.bat 进行打包")

if __name__ == "__main__":
    main()