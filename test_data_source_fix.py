#!/usr/bin/env python3
"""
测试数据源修复功能
验证是否能获取最新的股票价格数据
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_enhanced_data_manager():
    """测试增强型数据源管理器"""
    print("🔬 测试增强型数据源管理器")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        # 测试不同市场的数据获取
        test_cases = [
            ("BTC", "crypto", "比特币"),
            ("AAPL", "us_stocks", "苹果公司"),
            ("0700", "hk_stocks", "腾讯控股")
        ]
        
        for symbol, market, name in test_cases:
            print(f"\n📊 测试 {name} ({symbol}) - {market}")
            print("-" * 30)
            
            try:
                # 获取历史数据
                df = manager.get_latest_data(symbol, market, days=30)
                
                if not df.empty:
                    latest_price = df['close'].iloc[-1]
                    latest_time = df['timestamps'].iloc[-1]
                    data_age = datetime.now() - latest_time.to_pydatetime()
                    
                    print(f"✅ 数据获取成功")
                    print(f"   数据行数: {len(df)}")
                    print(f"   最新价格: ${latest_price:.4f}")
                    print(f"   最新时间: {latest_time}")
                    print(f"   数据新鲜度: {data_age.days}天 {data_age.seconds//3600}小时前")
                    
                    # 验证数据质量
                    if data_age.days <= 7:
                        print(f"   ✅ 数据新鲜度良好")
                    else:
                        print(f"   ⚠️ 数据可能不是最新的")
                    
                    # 测试实时价格获取
                    real_time_price = manager.get_real_time_price(symbol, market)
                    if real_time_price:
                        print(f"   实时价格: ${real_time_price:.4f}")
                        price_diff = abs(real_time_price - latest_price)
                        print(f"   价格差异: ${price_diff:.4f}")
                    else:
                        print(f"   ⚠️ 无法获取实时价格")
                        
                else:
                    print(f"❌ 获取到空数据")
                    
            except Exception as e:
                print(f"❌ 测试失败: {str(e)}")
                
            time.sleep(1)  # 避免API限制
            
    except ImportError as e:
        print(f"❌ 无法导入增强型数据源管理器: {e}")

def test_stock_predictor_integration():
    """测试股票预测器集成"""
    print(f"\n🤖 测试股票预测器集成")
    print("=" * 50)
    
    try:
        from stock_predictor import MultiMarketStockPredictor
        
        predictor = MultiMarketStockPredictor()
        
        # 测试数据获取
        print("测试数据获取功能...")
        df = predictor.data_fetcher.fetch_data("BTC", "crypto", days=10)
        
        if not df.empty:
            print(f"✅ 集成测试成功")
            print(f"   获取数据: {len(df)}行")
            print(f"   最新价格: ${df['close'].iloc[-1]:.4f}")
            print(f"   最新时间: {df['timestamps'].iloc[-1]}")
            
            # 测试实时价格
            real_time_price = predictor.data_fetcher.get_real_time_price("BTC", "crypto")
            if real_time_price:
                print(f"   实时价格: ${real_time_price:.4f}")
            
        else:
            print(f"❌ 集成测试失败：数据为空")
            
    except Exception as e:
        print(f"❌ 集成测试异常: {str(e)}")

def test_api_fallback():
    """测试API回退机制"""
    print(f"\n🔄 测试API回退机制")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        # 测试加密货币数据（多源fallback）
        print("测试加密货币数据获取...")
        df = manager._fetch_crypto_with_fallback("BTC", 7)
        
        if not df.empty:
            print(f"✅ 加密货币数据获取成功")
            print(f"   数据源: Binance/CoinGecko/Mock")
            print(f"   数据行数: {len(df)}")
            print(f"   价格范围: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        
        # 测试美股数据
        print(f"\n测试美股数据获取...")
        df = manager._fetch_us_stock_with_fallback("AAPL", 7)
        
        if not df.empty:
            print(f"✅ 美股数据获取成功")
            print(f"   数据源: Yahoo/AlphaVantage/Mock")
            print(f"   数据行数: {len(df)}")
            print(f"   价格范围: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            
    except Exception as e:
        print(f"❌ 回退机制测试失败: {str(e)}")

def test_data_quality():
    """测试数据质量验证"""
    print(f"\n🔍 测试数据质量验证")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        # 测试数据验证功能
        test_symbols = ["BTC", "AAPL", "0700"]
        test_markets = ["crypto", "us_stocks", "hk_stocks"]
        
        for symbol, market in zip(test_symbols, test_markets):
            print(f"\n验证 {symbol} ({market}) 数据质量...")
            
            try:
                df = manager.get_latest_data(symbol, market, days=5)
                
                # 检查数据完整性
                required_cols = ['timestamps', 'open', 'high', 'low', 'close', 'volume']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if not missing_cols:
                    print(f"✅ 数据结构完整")
                else:
                    print(f"⚠️ 缺少列: {missing_cols}")
                
                # 检查数据有效性
                if df['close'].min() > 0 and df['volume'].min() >= 0:
                    print(f"✅ 数据值有效")
                else:
                    print(f"⚠️ 发现无效数据值")
                
                # 检查OHLC关系
                ohlc_valid = all([
                    (df['high'] >= df['low']).all(),
                    (df['high'] >= df['open']).all(),
                    (df['high'] >= df['close']).all(),
                    (df['low'] <= df['open']).all(),
                    (df['low'] <= df['close']).all()
                ])
                
                if ohlc_valid:
                    print(f"✅ OHLC关系正确")
                else:
                    print(f"⚠️ OHLC关系异常")
                    
            except Exception as e:
                print(f"❌ 数据质量验证失败: {str(e)}")
                
    except Exception as e:
        print(f"❌ 数据质量测试异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 股票价格数据源修复测试")
    print("=" * 60)
    print("测试内容:")
    print("1. 增强型数据源管理器功能")
    print("2. 股票预测器集成")
    print("3. API回退机制")
    print("4. 数据质量验证")
    print("=" * 60)
    
    try:
        # 测试增强型数据源管理器
        test_enhanced_data_manager()
        
        # 测试股票预测器集成
        test_stock_predictor_integration()
        
        # 测试API回退机制
        test_api_fallback()
        
        # 测试数据质量
        test_data_quality()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("💡 数据源修复要点:")
        print("   1. 多数据源fallback机制")
        print("   2. 请求重试和频率限制处理")
        print("   3. 数据缓存和质量验证")
        print("   4. 实时价格更新功能")
        print("   5. 更真实的模拟数据生成")
        print("\n🌐 启动Web界面测试:")
        print("   cd webui && python app.py")
        print("   查看实时价格更新功能")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()