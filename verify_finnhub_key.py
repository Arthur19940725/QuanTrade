#!/usr/bin/env python3
"""
验证Finnhub API Key
"""

import requests
import ssl
import urllib3

def verify_api_key():
    """验证API Key"""
    api_key = 'd3040f1r01qnmrscs8b0d3040f1r01qnmrscs8bg'
    
    print(f'🔑 验证Finnhub API Key')
    print(f'Key: {api_key[:15]}...{api_key[-15:]}')
    print('-' * 50)
    
    # 禁用SSL警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 创建会话
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    })
    
    # 测试不同的端点
    tests = [
        {
            'name': '实时价格',
            'url': 'https://finnhub.io/api/v1/quote',
            'params': {'symbol': 'AAPL', 'token': api_key}
        },
        {
            'name': '公司信息',
            'url': 'https://finnhub.io/api/v1/stock/profile2', 
            'params': {'symbol': 'AAPL', 'token': api_key}
        }
    ]
    
    for test in tests:
        print(f'\n📡 测试{test["name"]}端点...')
        
        try:
            response = session.get(
                test['url'], 
                params=test['params'], 
                timeout=15,
                verify=False  # 暂时跳过SSL验证
            )
            
            print(f'   状态码: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'   ✅ 请求成功')
                
                if test['name'] == '实时价格':
                    if 'c' in data and data['c'] is not None:
                        print(f'   💰 AAPL价格: ${data["c"]}')
                        print(f'   📊 开盘: ${data.get("o", "N/A")}')
                        print(f'   📊 最高: ${data.get("h", "N/A")}')
                        print(f'   📊 最低: ${data.get("l", "N/A")}')
                        return True
                    else:
                        print(f'   ⚠️ 价格数据无效')
                        
                elif test['name'] == '公司信息':
                    if 'name' in data:
                        print(f'   🏢 公司名称: {data.get("name", "N/A")}')
                        print(f'   🌍 国家: {data.get("country", "N/A")}')
                        print(f'   💼 行业: {data.get("finnhubIndustry", "N/A")}')
                        
            elif response.status_code == 401:
                print(f'   ❌ API Key无效或已过期')
                return False
            elif response.status_code == 403:
                print(f'   ❌ 权限不足或API限制')
                return False
            elif response.status_code == 429:
                print(f'   ⚠️ 请求频率过高')
                return False
            else:
                print(f'   ❌ 请求失败: {response.text}')
                
        except requests.exceptions.SSLError as e:
            print(f'   ⚠️ SSL错误: {str(e)}')
            print(f'   💡 尝试不同的连接方式...')
            
        except requests.exceptions.ConnectionError as e:
            print(f'   ❌ 连接错误: {str(e)}')
            
        except Exception as e:
            print(f'   ❌ 其他错误: {str(e)}')
    
    return False

def test_with_curl():
    """使用curl测试API"""
    print(f'\n🔧 使用curl测试API连接')
    print('-' * 30)
    
    api_key = 'd3040f1r01qnmrscs8b0d3040f1r01qnmrscs8bg'
    
    import subprocess
    
    try:
        # 构建curl命令
        curl_cmd = [
            'curl',
            '-k',  # 跳过SSL验证
            '--connect-timeout', '10',
            '--max-time', '30',
            f'https://finnhub.io/api/v1/quote?symbol=AAPL&token={api_key}'
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f'✅ curl请求成功')
            print(f'响应: {result.stdout}')
            return True
        else:
            print(f'❌ curl请求失败')
            print(f'错误: {result.stderr}')
            return False
            
    except subprocess.TimeoutExpired:
        print(f'❌ curl请求超时')
        return False
    except FileNotFoundError:
        print(f'⚠️ 系统中未找到curl命令')
        return False
    except Exception as e:
        print(f'❌ curl测试异常: {str(e)}')
        return False

if __name__ == "__main__":
    print("🔐 Finnhub API Key验证工具")
    print("=" * 60)
    
    # 测试API Key
    api_valid = verify_api_key()
    
    if not api_valid:
        # 如果普通请求失败，尝试curl
        curl_success = test_with_curl()
        if curl_success:
            print(f'\n💡 curl测试成功，可能是Python SSL配置问题')
        else:
            print(f'\n❌ 所有测试都失败，请检查API Key或网络连接')
    
    print("=" * 60)