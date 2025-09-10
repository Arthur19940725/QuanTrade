#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型下载脚本
下载Kronos模型到本地
"""

import os
import sys
from pathlib import Path

def download_models():
    """下载Kronos模型"""
    try:
        from transformers import AutoModel, AutoTokenizer
        
        # 创建模型目录
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        # 模型配置
        models = {
            "NeoQuasar/Kronos-small": "Kronos-small",
            "NeoQuasar/Kronos-base": "Kronos-base", 
            "NeoQuasar/Kronos-mini": "Kronos-mini",
            "NeoQuasar/Kronos-Tokenizer-base": "Kronos-Tokenizer-base",
            "NeoQuasar/Kronos-Tokenizer-2k": "Kronos-Tokenizer-2k"
        }
        
        print("🚀 开始下载Kronos模型...")
        print("=" * 50)
        
        for model_name, local_name in models.items():
            print(f"\n📥 下载 {model_name}...")
            
            try:
                if "Tokenizer" in model_name:
                    # 下载tokenizer
                    tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        cache_dir=str(models_dir)
                    )
                    print(f"✅ {local_name} 下载完成")
                else:
                    # 下载模型
                    model = AutoModel.from_pretrained(
                        model_name,
                        cache_dir=str(models_dir)
                    )
                    print(f"✅ {local_name} 下载完成")
                    
            except Exception as e:
                print(f"❌ {local_name} 下载失败: {e}")
                continue
        
        print("\n🎉 模型下载完成！")
        print("📁 模型文件保存在 models/ 目录中")
        
    except ImportError:
        print("❌ 请先安装transformers库:")
        print("pip install transformers")
        return False
    
    except Exception as e:
        print(f"❌ 下载过程中出现错误: {e}")
        return False
    
    return True

def check_models():
    """检查模型是否已下载"""
    models_dir = Path("models")
    if not models_dir.exists():
        return False
    
    # 检查关键模型文件
    required_dirs = [
        "models--NeoQuasar--Kronos-small",
        "models--NeoQuasar--Kronos-base",
        "models--NeoQuasar--Kronos-mini"
    ]
    
    for dir_name in required_dirs:
        if not (models_dir / dir_name).exists():
            return False
    
    return True

def main():
    """主函数"""
    print("🔍 检查模型文件...")
    
    if check_models():
        print("✅ 模型文件已存在，无需下载")
        return
    
    print("📥 开始下载模型文件...")
    success = download_models()
    
    if success:
        print("\n🎉 所有模型下载完成！")
        print("现在可以运行预测程序了:")
        print("python stock_predictor.py")
    else:
        print("\n❌ 模型下载失败，请检查网络连接或手动下载")

if __name__ == "__main__":
    main()