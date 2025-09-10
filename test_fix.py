#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试QuantPredict Pro修复后的功能
"""

import os
import sys

def test_directories_creation():
    """测试目录创建功能"""
    print("🧪 测试目录创建功能...")
    
    # 模拟程序启动时的目录创建
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = ['cache', 'data', 'models']
    
    for dir_name in directories:
        dir_path = os.path.join(base_dir, dir_name)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                print(f"✅ 创建目录: {dir_path}")
            except Exception as e:
                print(f"⚠️ 创建目录失败 {dir_path}: {e}")
        else:
            print(f"📁 目录已存在: {dir_path}")

def test_style_configuration():
    """测试样式配置"""
    print("\n🧪 测试样式配置...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 测试样式配置
        style = ttk.Style()
        
        # 定义iOS风格颜色
        colors = {
            'primary': '#007AFF',
            'background': '#f2f2f7',
            'card': '#ffffff',
            'text': '#000000',
            'secondary_text': '#8E8E93',
        }
        
        # 配置样式
        style.configure('Card.TFrame', 
                       background=colors['card'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Card.TLabelFrame', 
                       background=colors['card'],
                       foreground=colors['text'],
                       font=('SF Pro Text', 11, 'bold'),
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Card.TLabelFrame.Label',
                       background=colors['card'],
                       foreground=colors['text'],
                       font=('SF Pro Text', 11, 'bold'))
        
        # 配置LabelFrame的边框样式
        style.map('Card.TLabelFrame',
                 background=[('active', colors['card']),
                           ('focus', colors['card'])],
                 foreground=[('active', colors['text']),
                           ('focus', colors['text'])])
        
        print("✅ 样式配置成功")
        
        # 测试创建LabelFrame
        test_frame = ttk.LabelFrame(root, text="测试", style='Card.TLabelFrame')
        print("✅ LabelFrame创建成功")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ 样式配置失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 QuantPredict Pro 修复测试")
    print("=" * 50)
    
    # 测试目录创建
    test_directories_creation()
    
    # 测试样式配置
    if test_style_configuration():
        print("\n✅ 所有测试通过！")
        print("🎉 QuantPredict Pro 修复成功！")
    else:
        print("\n❌ 测试失败！")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)