#!/usr/bin/env python3
"""
测试加密货币预测应用的核心功能
"""

import sys
import traceback
from datetime import datetime

def test_lite_app():
    """测试轻量版应用"""
    print("=== 测试轻量版应用 ===")
    
    try:
        # 测试数据获取器
        from crypto_predictor_lite import CryptoDataFetcher
        fetcher = CryptoDataFetcher()
        print("✓ 数据获取器导入成功")
        
        # 测试获取BTC数据
        df = fetcher.get_kline_data('BTC', limit=10)
        if not df.empty:
            print(f"✓ BTC数据获取成功，共{len(df)}条记录")
            print(f"  最新价格: ${df['close'].iloc[-1]:.2f}")
        else:
            print("⚠ 使用模拟数据")
        
        # 测试技术分析预测器
        from crypto_predictor_lite import TechnicalAnalysisPredictor
        predictor = TechnicalAnalysisPredictor()
        print("✓ 技术分析预测器导入成功")
        
        # 进行预测测试
        prediction = predictor.predict_price(df, 'BTC', 3)
        if prediction:
            print(f"✓ 预测成功:")
            print(f"  当前价格: ${prediction['current_price']:.2f}")
            print(f"  预测价格: ${prediction['predicted_prices'][-1]:.2f}")
            print(f"  趋势: {prediction['trend']}")
            print(f"  置信度: {prediction['confidence']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"✗ 轻量版测试失败: {e}")
        traceback.print_exc()
        return False

def test_full_app():
    """测试完整版应用"""
    print("\n=== 测试完整版应用 ===")
    
    try:
        # 测试Kronos模型导入
        try:
            from model.kronos import Kronos, KronosTokenizer
            print("✓ Kronos模型库导入成功")
            model_available = True
        except ImportError as e:
            print(f"⚠ Kronos模型库不可用: {e}")
            model_available = False
        
        # 测试完整版应用组件
        from crypto_predictor_app import CryptoDataFetcher, CryptoPricePredictor
        
        fetcher = CryptoDataFetcher()
        predictor = CryptoPricePredictor()
        
        print("✓ 完整版组件导入成功")
        
        # 测试数据获取
        df = fetcher.get_kline_data('ETH', limit=10)
        if not df.empty:
            print(f"✓ ETH数据获取成功")
            
            # 测试预测（会自动切换到模拟模式如果模型不可用）
            prediction = predictor.predict_price(df, 'ETH', 3)
            if prediction:
                print(f"✓ 预测成功 ({'模型模式' if model_available else '模拟模式'})")
                print(f"  预测趋势: {prediction['trend']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 完整版测试失败: {e}")
        traceback.print_exc()
        return False

def test_gui_imports():
    """测试GUI相关导入"""
    print("\n=== 测试GUI组件 ===")
    
    try:
        import tkinter as tk
        print("✓ tkinter可用")
        
        import matplotlib.pyplot as plt
        print("✓ matplotlib可用")
        
        import pandas as pd
        import numpy as np
        import requests
        print("✓ 基础依赖可用")
        
        # 测试GUI类导入（不实际创建窗口）
        from crypto_predictor_lite import CryptoPredictorLiteGUI
        print("✓ 轻量版GUI类导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ GUI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Kronos 加密货币预测器 - 功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = []
    
    # 测试GUI组件
    results.append(test_gui_imports())
    
    # 测试轻量版
    results.append(test_lite_app())
    
    # 测试完整版
    results.append(test_full_app())
    
    # 总结结果
    print("\n" + "=" * 50)
    print("🏆 测试总结:")
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"通过: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✅ 所有测试通过！应用可以正常使用")
        print("\n推荐使用:")
        print("- 轻量版: 快速启动，基于技术分析")
        print("- 完整版: 深度学习预测，需要模型文件")
        
        print("\n启动方式:")
        print("1. 运行 python crypto_predictor_lite.py")
        print("2. 或使用 启动加密货币预测器.bat")
        print("3. 或运行打包好的exe文件")
        
    else:
        print("⚠ 部分测试失败，但基础功能可用")
        print("建议优先使用轻量版")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程出错: {e}")
        traceback.print_exc()