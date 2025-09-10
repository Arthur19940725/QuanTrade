#!/usr/bin/env python3
"""
测试Finnhub API集成
验证API KEY和数据获取功能
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_finnhub_api_key():
    """测试Finnhub API Key有效性"""
    print("🔑 测试Finnhub API Key")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        api_key = manager.data_sources['us_stocks']['finnhub']['api_key']
        
        print(f"API Key: {api_key[:10]}...{api_key[-10:]}")
        
        # 测试API连接
        import requests
        url = "https://finnhub.io/api/v1/quote"
        params = {
            'symbol': 'AAPL',
            'token': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'c' in data and data['c'] is not None:
                print(f"✅ API Key有效")
                print(f"   测试股票: AAPL")
                print(f"   当前价格: ${data['c']}")
                print(f"   开盘价: ${data['o']}")
                print(f"   最高价: ${data['h']}")
                print(f"   最低价: ${data['l']}")
                print(f"   昨日收盘: ${data['pc']}")
                return True
            else:
                print(f"❌ API返回数据无效: {data}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Key测试异常: {str(e)}")
        return False

def test_finnhub_historical_data():
    """测试Finnhub历史数据获取"""
    print(f"\n📊 测试Finnhub历史数据获取")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        # 测试多个股票的历史数据
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        for symbol in test_symbols:
            print(f"\n📈 测试 {symbol} 历史数据")
            print("-" * 30)
            
            try:
                df = manager._fetch_finnhub_data(symbol, days=30)
                
                if not df.empty:
                    latest_price = df['close'].iloc[-1]
                    latest_time = df['timestamps'].iloc[-1]
                    price_range = f"${df['close'].min():.2f} - ${df['close'].max():.2f}"
                    avg_volume = df['volume'].mean()
                    
                    print(f"✅ 数据获取成功")
                    print(f"   数据行数: {len(df)}")
                    print(f"   最新价格: ${latest_price:.2f}")
                    print(f"   最新时间: {latest_time}")
                    print(f"   价格范围: {price_range}")
                    print(f"   平均成交量: {avg_volume:,.0f}")
                    
                    # 数据质量检查
                    data_age = datetime.now() - latest_time.to_pydatetime()
                    if data_age.days <= 3:
                        print(f"   ✅ 数据新鲜度良好 ({data_age.days}天前)")
                    else:
                        print(f"   ⚠️ 数据可能不够新 ({data_age.days}天前)")
                else:
                    print(f"❌ 获取到空数据")
                    
            except Exception as e:
                print(f"❌ 获取失败: {str(e)}")
            
            time.sleep(0.5)  # 避免API限制
            
    except Exception as e:
        print(f"❌ 历史数据测试异常: {str(e)}")

def test_finnhub_real_time_price():
    """测试Finnhub实时价格获取"""
    print(f"\n💰 测试Finnhub实时价格获取")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        # 测试多个股票的实时价格
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        for symbol in test_symbols:
            print(f"\n💵 测试 {symbol} 实时价格")
            print("-" * 30)
            
            try:
                # 测试专用实时价格API
                real_time_price = manager._get_finnhub_real_time_price(symbol)
                print(f"✅ 实时价格: ${real_time_price:.2f}")
                
                # 测试通用实时价格接口
                general_price = manager.get_real_time_price(symbol, 'us_stocks')
                print(f"✅ 通用接口价格: ${general_price:.2f}")
                
                # 比较价格差异
                if abs(real_time_price - general_price) < 0.01:
                    print(f"✅ 价格一致性良好")
                else:
                    price_diff = abs(real_time_price - general_price)
                    print(f"⚠️ 价格差异: ${price_diff:.2f}")
                    
            except Exception as e:
                print(f"❌ 实时价格获取失败: {str(e)}")
            
            time.sleep(0.5)  # 避免API限制
            
    except Exception as e:
        print(f"❌ 实时价格测试异常: {str(e)}")

def test_finnhub_fallback_mechanism():
    """测试Finnhub在fallback机制中的表现"""
    print(f"\n🔄 测试Finnhub Fallback机制")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        # 测试美股数据获取（会按优先级尝试不同数据源）
        print("测试美股数据获取优先级...")
        
        test_symbols = ['AAPL', 'MSFT']
        
        for symbol in test_symbols:
            print(f"\n🔍 测试 {symbol} 数据源fallback")
            print("-" * 30)
            
            try:
                df = manager.get_latest_data(symbol, 'us_stocks', days=10)
                
                if not df.empty:
                    print(f"✅ 最终获取成功")
                    print(f"   数据行数: {len(df)}")
                    print(f"   最新价格: ${df['close'].iloc[-1]:.2f}")
                    print(f"   数据来源: 多源fallback机制")
                else:
                    print(f"❌ 所有数据源都失败")
                    
            except Exception as e:
                print(f"❌ Fallback测试失败: {str(e)}")
                
    except Exception as e:
        print(f"❌ Fallback机制测试异常: {str(e)}")

def test_finnhub_data_quality():
    """测试Finnhub数据质量"""
    print(f"\n🔍 测试Finnhub数据质量")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        # 获取测试数据
        df = manager._fetch_finnhub_data('AAPL', days=30)
        
        if not df.empty:
            print("✅ 数据质量检查:")
            
            # 检查必需列
            required_cols = ['timestamps', 'open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if not missing_cols:
                print("   ✅ 数据结构完整")
            else:
                print(f"   ❌ 缺少列: {missing_cols}")
            
            # 检查OHLC关系
            ohlc_valid = all([
                (df['high'] >= df['low']).all(),
                (df['high'] >= df['open']).all(),
                (df['high'] >= df['close']).all(),
                (df['low'] <= df['open']).all(),
                (df['low'] <= df['close']).all()
            ])
            
            if ohlc_valid:
                print("   ✅ OHLC关系正确")
            else:
                print("   ❌ OHLC关系异常")
            
            # 检查数据有效性
            if df['close'].min() > 0 and df['volume'].min() >= 0:
                print("   ✅ 数据值有效")
            else:
                print("   ❌ 发现无效数据值")
            
            # 检查时间序列
            if df['timestamps'].is_monotonic_increasing:
                print("   ✅ 时间序列正确")
            else:
                print("   ❌ 时间序列异常")
            
            # 数据统计
            print(f"   📊 数据统计:")
            print(f"      价格范围: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
            print(f"      平均成交量: {df['volume'].mean():,.0f}")
            print(f"      数据时间跨度: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
            
        else:
            print("❌ 无法获取测试数据")
            
    except Exception as e:
        print(f"❌ 数据质量测试异常: {str(e)}")

def test_api_rate_limits():
    """测试API频率限制"""
    print(f"\n⏱️ 测试API频率限制")
    print("=" * 50)
    
    try:
        from data_source_manager import EnhancedDataSourceManager
        
        manager = EnhancedDataSourceManager()
        
        print("测试连续请求（检查频率限制处理）...")
        
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        success_count = 0
        
        start_time = time.time()
        
        for i, symbol in enumerate(symbols, 1):
            try:
                price = manager._get_finnhub_real_time_price(symbol)
                print(f"   {i}. {symbol}: ${price:.2f}")
                success_count += 1
            except Exception as e:
                print(f"   {i}. {symbol}: 失败 - {str(e)}")
            
            time.sleep(0.2)  # 小延迟避免过快请求
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n📊 频率限制测试结果:")
        print(f"   成功请求: {success_count}/{len(symbols)}")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   平均耗时: {total_time/len(symbols):.2f}秒/请求")
        
        if success_count == len(symbols):
            print(f"   ✅ 频率限制处理良好")
        else:
            print(f"   ⚠️ 部分请求失败，可能遇到频率限制")
            
    except Exception as e:
        print(f"❌ 频率限制测试异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 Finnhub API集成测试")
    print("=" * 60)
    print("API Key: d2o730hr01qga5g7u6ggd2o730hr01qga5g7u6h0")
    print("测试内容:")
    print("1. API Key有效性验证")
    print("2. 历史数据获取测试")
    print("3. 实时价格获取测试")
    print("4. Fallback机制测试")
    print("5. 数据质量验证")
    print("6. API频率限制测试")
    print("=" * 60)
    
    try:
        # 测试API Key
        api_valid = test_finnhub_api_key()
        
        if api_valid:
            # 测试历史数据
            test_finnhub_historical_data()
            
            # 测试实时价格
            test_finnhub_real_time_price()
            
            # 测试fallback机制
            test_finnhub_fallback_mechanism()
            
            # 测试数据质量
            test_finnhub_data_quality()
            
            # 测试频率限制
            test_api_rate_limits()
        else:
            print("\n❌ API Key无效，跳过其他测试")
        
        print("\n" + "=" * 60)
        if api_valid:
            print("✅ Finnhub API集成测试完成！")
            print("💡 Finnhub集成优势:")
            print("   1. 专业金融数据API")
            print("   2. 实时价格更新")
            print("   3. 高质量历史数据")
            print("   4. 作为Yahoo Finance的可靠备用源")
            print("\n🌐 现在可以在Web界面中体验:")
            print("   - 更稳定的美股数据获取")
            print("   - 更准确的实时价格")
            print("   - 更可靠的数据源fallback")
        else:
            print("❌ Finnhub API集成测试失败！")
            print("🔧 请检查:")
            print("   1. API Key是否正确")
            print("   2. 网络连接是否正常")
            print("   3. API配额是否充足")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()