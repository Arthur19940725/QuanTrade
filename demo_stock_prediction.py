#!/usr/bin/env python3
"""
Kronos 股票预测功能演示脚本
展示如何使用新增的股票预测功能
"""

import sys
import os
import asyncio
import time

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from stock_predictor import MultiMarketStockPredictor

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🚀 Kronos 多市场股票预测系统演示")
    print("支持A股、港股、美股、加密货币预测")
    print("=" * 60)

def demo_search_functionality():
    """演示搜索功能"""
    print("\n📊 股票搜索功能演示")
    print("-" * 40)
    
    predictor = MultiMarketStockPredictor()
    
    # 演示不同类型的搜索
    demo_searches = [
        ("AAPL", "美股代码搜索"),
        ("苹果", "中文名称搜索"),
        ("腾讯", "港股中文搜索"),
        ("BTC", "加密货币搜索"),
        ("比特币", "加密货币中文搜索")
    ]
    
    for query, description in demo_searches:
        print(f"\n🔍 {description}: '{query}'")
        results = predictor.search_stocks(query)
        
        if results:
            for i, result in enumerate(results[:3], 1):
                market_name = {
                    'cn_stocks': 'A股',
                    'hk_stocks': '港股', 
                    'us_stocks': '美股',
                    'crypto': '加密货币'
                }.get(result['market'], result['market'])
                
                print(f"  {i}. {result['symbol']} - {result['cn_name']}")
                print(f"     {result['en_name']} ({market_name})")
        else:
            print("  未找到匹配结果")

def demo_prediction_functionality():
    """演示预测功能"""
    print("\n📈 股票预测功能演示")
    print("-" * 40)
    
    predictor = MultiMarketStockPredictor()
    
    # 演示不同市场的预测
    demo_predictions = [
        ("AAPL", "us_stocks", "苹果公司", "🍎"),
        ("BTC", "crypto", "比特币", "₿"),
        ("0700", "hk_stocks", "腾讯控股", "🐧"),
        ("600519", "cn_stocks", "贵州茅台", "🍶")
    ]
    
    for symbol, market, name, emoji in demo_predictions:
        print(f"\n{emoji} 预测 {name} ({symbol})")
        print(f"   市场: {market}")
        
        try:
            # 执行预测
            result = predictor.predict_stock(
                symbol=symbol,
                market=market,
                pred_days=5,
                lookback_days=60
            )
            
            if result['success']:
                # 显示预测结果
                print(f"   💰 当前价格: ${result['current_price']:.2f}")
                print(f"   🎯 预测价格: ${result['summary']['final_price']:.2f}")
                
                change_pct = result['summary']['total_change_pct']
                trend_emoji = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
                print(f"   {trend_emoji} 预计涨跌: {change_pct:+.2f}%")
                print(f"   📊 趋势判断: {result['summary']['trend']}")
                print(f"   🤖 预测模型: {result['model_used']}")
                print(f"   🎲 置信度: {result['summary']['confidence']}")
                
                # 显示详细预测
                print(f"   📅 详细预测 (未来{result['prediction_days']}天):")
                for i, pred in enumerate(result['predictions'][:3], 1):
                    change_symbol = "+" if pred['change_pct'] > 0 else ""
                    print(f"      {i}. {pred['date']}: ${pred['predicted_price']:.2f} ({change_symbol}{pred['change_pct']:.2f}%)")
                
                if len(result['predictions']) > 3:
                    print(f"      ... 还有 {len(result['predictions']) - 3} 天的预测数据")
                    
            else:
                print(f"   ❌ 预测失败: {result['error']}")
                
        except Exception as e:
            print(f"   ⚠️ 预测异常: {str(e)}")
        
        # 添加延迟避免API限制
        time.sleep(1)

def demo_market_coverage():
    """演示市场覆盖情况"""
    print("\n🌐 支持的市场和股票")
    print("-" * 40)
    
    predictor = MultiMarketStockPredictor()
    
    market_info = {
        'cn_stocks': ('A股市场', '🇨🇳', ['600519-贵州茅台', '000858-五粮液', '600036-招商银行']),
        'hk_stocks': ('港股市场', '🇭🇰', ['0700-腾讯控股', '0941-中国移动', '1299-友邦保险']),
        'us_stocks': ('美股市场', '🇺🇸', ['AAPL-苹果', 'MSFT-微软', 'GOOGL-谷歌']),
        'crypto': ('加密货币', '₿', ['BTC-比特币', 'ETH-以太坊', 'SOL-索拉纳'])
    }
    
    for market_key, (market_name, emoji, examples) in market_info.items():
        print(f"\n{emoji} {market_name} ({market_key})")
        stock_count = len(predictor.symbol_resolver.stock_databases[market_key])
        print(f"   支持股票数量: {stock_count}")
        print(f"   示例股票: {', '.join(examples)}")

def demo_web_interface_info():
    """演示Web界面信息"""
    print("\n🌐 Web界面使用说明")
    print("-" * 40)
    print("1. 启动Web服务:")
    print("   cd webui && python app.py")
    print("\n2. 访问地址:")
    print("   http://localhost:7070")
    print("\n3. 使用步骤:")
    print("   ① 选择'在线股票数据'作为数据源")
    print("   ② 在搜索框输入股票名称或代码")
    print("   ③ 选择要预测的股票")
    print("   ④ 设置预测参数（天数等）")
    print("   ⑤ 点击'预测股票走势'按钮")
    print("   ⑥ 查看预测结果和图表")

def main():
    """主函数"""
    print_banner()
    
    try:
        # 演示搜索功能
        demo_search_functionality()
        
        # 演示市场覆盖
        demo_market_coverage()
        
        # 演示预测功能
        demo_prediction_functionality()
        
        # Web界面说明
        demo_web_interface_info()
        
        print("\n" + "=" * 60)
        print("✅ 演示完成！")
        print("💡 提示: 运行 'python webui/app.py' 启动Web界面")
        print("📖 详细说明请查看: 股票预测功能使用说明.md")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()