#!/usr/bin/env python3
"""
测试股票预测器功能
"""

import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from stock_predictor import MultiMarketStockPredictor

def test_stock_search():
    """测试股票搜索功能"""
    print("=== 测试股票搜索功能 ===")
    predictor = MultiMarketStockPredictor()
    
    # 测试不同类型的搜索
    test_queries = ["苹果", "AAPL", "腾讯", "0700", "BTC", "比特币", "贵州茅台", "600519"]
    
    for query in test_queries:
        print(f"\n搜索: {query}")
        results = predictor.search_stocks(query)
        for result in results[:3]:  # 只显示前3个结果
            print(f"  {result['symbol']} - {result['cn_name']} ({result['en_name']}) - {result['market']}")

def test_stock_prediction():
    """测试股票预测功能"""
    print("\n=== 测试股票预测功能 ===")
    predictor = MultiMarketStockPredictor()
    
    # 测试不同市场的股票预测
    test_stocks = [
        ("AAPL", "us_stocks", "苹果公司"),
        ("BTC", "crypto", "比特币"),
        ("0700", "hk_stocks", "腾讯控股"),
        ("600519", "cn_stocks", "贵州茅台")
    ]
    
    for symbol, market, name in test_stocks:
        print(f"\n预测 {name} ({symbol}) - {market}")
        try:
            result = predictor.predict_stock(symbol, market, pred_days=5, lookback_days=60)
            if result['success']:
                print(f"  当前价格: ${result['current_price']}")
                print(f"  预测价格: ${result['summary']['final_price']}")
                print(f"  涨跌幅: {result['summary']['total_change_pct']}%")
                print(f"  趋势: {result['summary']['trend']}")
                print(f"  使用模型: {result['model_used']}")
            else:
                print(f"  预测失败: {result['error']}")
        except Exception as e:
            print(f"  预测异常: {e}")

def test_market_info():
    """测试市场信息"""
    print("\n=== 支持的市场信息 ===")
    predictor = MultiMarketStockPredictor()
    
    markets = {
        'cn_stocks': 'A股市场',
        'hk_stocks': '港股市场', 
        'us_stocks': '美股市场',
        'crypto': '加密货币市场'
    }
    
    for market_key, market_name in markets.items():
        print(f"{market_name}: {market_key}")
        
        # 显示该市场的示例股票
        sample_stocks = []
        for symbol, info in predictor.symbol_resolver.stock_databases[market_key].items():
            sample_stocks.append(f"{symbol} ({info[0]})")
            if len(sample_stocks) >= 3:
                break
        
        print(f"  示例股票: {', '.join(sample_stocks)}")

if __name__ == "__main__":
    print("🚀 开始测试股票预测器...")
    
    try:
        # 测试股票搜索
        test_stock_search()
        
        # 测试市场信息
        test_market_info()
        
        # 测试股票预测
        test_stock_prediction()
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()