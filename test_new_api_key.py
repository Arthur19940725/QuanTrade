#!/usr/bin/env python3
"""
测试新的Finnhub API Key
"""

import requests
import json

def test_new_api_key():
    """测试新的API Key"""
    api_key = 'd303jc9r01qnmrscqjdgd303jc9r01qnmrscqje0'
    print(f'🔑 测试新API Key: {api_key[:10]}...{api_key[-10:]}')
    
    url = 'https://finnhub.io/api/v1/quote'
    params = {'symbol': 'AAPL', 'token': api_key}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f'📡 HTTP状态码: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ 新API Key验证成功!')
            print(f'   AAPL当前价格: ${data.get("c", "N/A")}')
            print(f'   开盘价: ${data.get("o", "N/A")}')
            print(f'   最高价: ${data.get("h", "N/A")}')
            print(f'   最低价: ${data.get("l", "N/A")}')
            print(f'   昨收: ${data.get("pc", "N/A")}')
            print(f'   完整响应: {json.dumps(data, indent=2)}')
            return True
        else:
            print(f'❌ API请求失败: {response.status_code}')
            print(f'响应内容: {response.text}')
            return False
    except Exception as e:
        print(f'❌ 测试异常: {str(e)}')
        return False

def test_multiple_stocks():
    """测试多个股票的实时价格"""
    api_key = 'd303jc9r01qnmrscqjdgd303jc9r01qnmrscqje0'
    
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    print(f'\n📊 测试多个股票实时价格:')
    print('-' * 40)
    
    for symbol in stocks:
        try:
            url = 'https://finnhub.io/api/v1/quote'
            params = {'symbol': symbol, 'token': api_key}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price = data.get('c', 0)
                print(f'✅ {symbol:6} | ${price:8.2f}')
            else:
                print(f'❌ {symbol:6} | 获取失败 ({response.status_code})')
                
        except Exception as e:
            print(f'❌ {symbol:6} | 异常: {str(e)}')

if __name__ == "__main__":
    print("🚀 测试新的Finnhub API Key")
    print("=" * 50)
    
    # 测试API Key
    if test_new_api_key():
        # 测试多个股票
        test_multiple_stocks()
        
        print(f'\n✅ API Key配置成功!')
        print(f'💡 现在可以享受Finnhub提供的高质量实时价格数据')
    else:
        print(f'\n❌ API Key配置失败，请检查密钥是否正确')