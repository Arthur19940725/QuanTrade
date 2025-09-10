#!/usr/bin/env python3
"""
测试新增的高级图表功能
包括价格走势图、价格区间预测、交易量预测
"""

import sys
import os
import json

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from stock_predictor import MultiMarketStockPredictor

def test_advanced_prediction():
    """测试高级预测功能"""
    print("🚀 测试高级股票预测功能")
    print("=" * 50)
    
    predictor = MultiMarketStockPredictor()
    
    # 测试不同市场的股票
    test_cases = [
        ("AAPL", "us_stocks", "苹果公司"),
        ("BTC", "crypto", "比特币"),
        ("0700", "hk_stocks", "腾讯控股")
    ]
    
    for symbol, market, name in test_cases:
        print(f"\n📈 测试 {name} ({symbol}) - {market}")
        print("-" * 30)
        
        try:
            result = predictor.predict_stock(
                symbol=symbol,
                market=market,
                pred_days=7,
                lookback_days=30
            )
            
            if result['success']:
                # 基本信息
                print(f"✅ 预测成功")
                print(f"   当前价格: ${result['current_price']}")
                print(f"   预测价格: ${result['summary']['final_price']}")
                print(f"   涨跌幅: {result['summary']['total_change_pct']:+.2f}%")
                print(f"   趋势: {result['summary']['trend']}")
                print(f"   使用模型: {result['model_used']}")
                
                # 价格区间信息
                if 'price_range' in result['summary']:
                    price_range = result['summary']['price_range']
                    print(f"   价格区间: ${price_range['min']} - ${price_range['max']}")
                
                # 图表数据验证
                if 'chart_data' in result:
                    chart_data = result['chart_data']
                    print(f"   历史数据点: {len(chart_data.get('historical_prices', []))}")
                    print(f"   预测数据点: {len(chart_data.get('predicted_prices', []))}")
                    print(f"   价格区间数据: {'有' if chart_data.get('upper_band') else '无'}")
                    print(f"   交易量数据: {'有' if chart_data.get('predicted_volumes') else '无'}")
                
                # 详细预测数据示例
                print(f"   前3天预测详情:")
                for i, pred in enumerate(result['predictions'][:3], 1):
                    price_info = f"${pred['predicted_price']}"
                    if 'upper_price' in pred and 'lower_price' in pred:
                        price_info += f" (区间: ${pred['lower_price']}-${pred['upper_price']})"
                    
                    volume_info = ""
                    if 'predicted_volume' in pred:
                        volume = pred['predicted_volume']
                        if volume >= 1000000:
                            volume_info = f", 成交量: {volume/1000000:.1f}M"
                        else:
                            volume_info = f", 成交量: {volume:,.0f}"
                    
                    print(f"     {i}. {pred['date']}: {price_info} ({pred['change_pct']:+.2f}%){volume_info}")
                
            else:
                print(f"❌ 预测失败: {result['error']}")
                
        except Exception as e:
            print(f"⚠️ 测试异常: {str(e)}")

def test_chart_data_structure():
    """测试图表数据结构"""
    print(f"\n📊 测试图表数据结构")
    print("-" * 30)
    
    predictor = MultiMarketStockPredictor()
    
    try:
        result = predictor.predict_stock("AAPL", "us_stocks", pred_days=5, lookback_days=20)
        
        if result['success'] and 'chart_data' in result:
            chart_data = result['chart_data']
            
            print("✅ 图表数据结构验证:")
            print(f"   历史价格数组长度: {len(chart_data.get('historical_prices', []))}")
            print(f"   历史日期数组长度: {len(chart_data.get('historical_dates', []))}")
            print(f"   历史成交量数组长度: {len(chart_data.get('historical_volumes', []))}")
            print(f"   预测价格数组长度: {len(chart_data.get('predicted_prices', []))}")
            print(f"   预测日期数组长度: {len(chart_data.get('prediction_dates', []))}")
            print(f"   价格上限数组长度: {len(chart_data.get('upper_band', []))}")
            print(f"   价格下限数组长度: {len(chart_data.get('lower_band', []))}")
            print(f"   预测成交量数组长度: {len(chart_data.get('predicted_volumes', []))}")
            
            # 数据示例
            if chart_data.get('historical_prices'):
                print(f"   历史价格示例: {chart_data['historical_prices'][:3]}...")
            if chart_data.get('predicted_prices'):
                print(f"   预测价格示例: {chart_data['predicted_prices'][:3]}...")
            if chart_data.get('upper_band'):
                print(f"   价格上限示例: {chart_data['upper_band'][:3]}...")
            if chart_data.get('predicted_volumes'):
                print(f"   预测成交量示例: {chart_data['predicted_volumes'][:3]}...")
                
        else:
            print("❌ 图表数据获取失败")
            
    except Exception as e:
        print(f"⚠️ 图表数据测试异常: {str(e)}")

def save_test_results():
    """保存测试结果到JSON文件"""
    print(f"\n💾 保存测试结果")
    print("-" * 30)
    
    predictor = MultiMarketStockPredictor()
    
    try:
        result = predictor.predict_stock("AAPL", "us_stocks", pred_days=7, lookback_days=30)
        
        if result['success']:
            # 保存完整结果
            with open('test_chart_data.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            
            print("✅ 测试结果已保存到 test_chart_data.json")
            print("   可以用于前端图表功能验证")
            
        else:
            print(f"❌ 无法保存测试结果: {result['error']}")
            
    except Exception as e:
        print(f"⚠️ 保存测试结果异常: {str(e)}")

def main():
    """主测试函数"""
    print("🔬 高级图表功能测试")
    print("=" * 60)
    print("测试内容:")
    print("1. 价格走势预测（历史+预测）")
    print("2. 价格浮动区间计算")
    print("3. 交易量预测")
    print("4. 图表数据结构验证")
    print("=" * 60)
    
    try:
        # 测试高级预测功能
        test_advanced_prediction()
        
        # 测试图表数据结构
        test_chart_data_structure()
        
        # 保存测试结果
        save_test_results()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("💡 启动Web界面测试完整功能:")
        print("   1. cd webui && python app.py")
        print("   2. 访问 http://localhost:7070")
        print("   3. 选择'在线股票数据'")
        print("   4. 搜索并预测股票，查看新的图表功能")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()