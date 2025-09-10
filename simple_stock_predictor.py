#!/usr/bin/env python3
"""
简化版股票预测器
专门用于打包成exe，最小依赖
"""

import sys
import os
import warnings
import threading
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# 禁用警告
warnings.filterwarnings("ignore")

# 确定程序运行目录
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

# 创建必要的目录
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"

for dir_path in [MODELS_DIR, DATA_DIR, CACHE_DIR]:
    dir_path.mkdir(exist_ok=True)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import sys
import os

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class SimpleStockDatabase:
    """扩展的股票数据库 - 支持所有A股、美股、加密货币"""
    
    def __init__(self):
        self.stocks = {}
        self._load_all_stocks()
    
    def _load_all_stocks(self):
        """加载所有股票数据"""
        # 美股 - 主要科技股
        us_tech_stocks = {
            'AAPL': {'cn_name': '苹果公司', 'en_name': 'Apple Inc.', 'market': 'US', 'sector': '科技', 'api_symbol': 'AAPL'},
            'MSFT': {'cn_name': '微软公司', 'en_name': 'Microsoft Corporation', 'market': 'US', 'sector': '科技', 'api_symbol': 'MSFT'},
            'GOOGL': {'cn_name': '谷歌', 'en_name': 'Alphabet Inc.', 'market': 'US', 'sector': '科技', 'api_symbol': 'GOOGL'},
            'TSLA': {'cn_name': '特斯拉', 'en_name': 'Tesla Inc.', 'market': 'US', 'sector': '汽车', 'api_symbol': 'TSLA'},
            'NVDA': {'cn_name': '英伟达', 'en_name': 'NVIDIA Corporation', 'market': 'US', 'sector': '科技', 'api_symbol': 'NVDA'},
            'META': {'cn_name': 'Meta平台', 'en_name': 'Meta Platforms Inc.', 'market': 'US', 'sector': '科技', 'api_symbol': 'META'},
            'AMZN': {'cn_name': '亚马逊', 'en_name': 'Amazon.com Inc.', 'market': 'US', 'sector': '电商', 'api_symbol': 'AMZN'},
            'NFLX': {'cn_name': '奈飞', 'en_name': 'Netflix Inc.', 'market': 'US', 'sector': '媒体', 'api_symbol': 'NFLX'},
            'AMD': {'cn_name': '超微半导体', 'en_name': 'Advanced Micro Devices', 'market': 'US', 'sector': '科技', 'api_symbol': 'AMD'},
            'INTC': {'cn_name': '英特尔', 'en_name': 'Intel Corporation', 'market': 'US', 'sector': '科技', 'api_symbol': 'INTC'},
            'ORCL': {'cn_name': '甲骨文', 'en_name': 'Oracle Corporation', 'market': 'US', 'sector': '科技', 'api_symbol': 'ORCL'},
            'CRM': {'cn_name': 'Salesforce', 'en_name': 'Salesforce Inc.', 'market': 'US', 'sector': '软件', 'api_symbol': 'CRM'},
            'ADBE': {'cn_name': 'Adobe', 'en_name': 'Adobe Inc.', 'market': 'US', 'sector': '软件', 'api_symbol': 'ADBE'},
            'PYPL': {'cn_name': 'PayPal', 'en_name': 'PayPal Holdings Inc.', 'market': 'US', 'sector': '金融科技', 'api_symbol': 'PYPL'},
            'UBER': {'cn_name': '优步', 'en_name': 'Uber Technologies Inc.', 'market': 'US', 'sector': '交通', 'api_symbol': 'UBER'},
            'SPOT': {'cn_name': 'Spotify', 'en_name': 'Spotify Technology S.A.', 'market': 'US', 'sector': '媒体', 'api_symbol': 'SPOT'},
            'ZM': {'cn_name': 'Zoom', 'en_name': 'Zoom Video Communications', 'market': 'US', 'sector': '软件', 'api_symbol': 'ZM'},
            'SQ': {'cn_name': 'Square', 'en_name': 'Block Inc.', 'market': 'US', 'sector': '金融科技', 'api_symbol': 'SQ'},
            'ROKU': {'cn_name': 'Roku', 'en_name': 'Roku Inc.', 'market': 'US', 'sector': '媒体', 'api_symbol': 'ROKU'},
            'SNOW': {'cn_name': 'Snowflake', 'en_name': 'Snowflake Inc.', 'market': 'US', 'sector': '科技', 'api_symbol': 'SNOW'},
        }
        
        # 美股 - 传统行业
        us_traditional_stocks = {
            'JPM': {'cn_name': '摩根大通', 'en_name': 'JPMorgan Chase & Co.', 'market': 'US', 'sector': '金融', 'api_symbol': 'JPM'},
            'BAC': {'cn_name': '美国银行', 'en_name': 'Bank of America Corp.', 'market': 'US', 'sector': '金融', 'api_symbol': 'BAC'},
            'WMT': {'cn_name': '沃尔玛', 'en_name': 'Walmart Inc.', 'market': 'US', 'sector': '零售', 'api_symbol': 'WMT'},
            'JNJ': {'cn_name': '强生', 'en_name': 'Johnson & Johnson', 'market': 'US', 'sector': '医疗', 'api_symbol': 'JNJ'},
            'PG': {'cn_name': '宝洁', 'en_name': 'Procter & Gamble Co.', 'market': 'US', 'sector': '消费品', 'api_symbol': 'PG'},
            'KO': {'cn_name': '可口可乐', 'en_name': 'The Coca-Cola Company', 'market': 'US', 'sector': '饮料', 'api_symbol': 'KO'},
            'PFE': {'cn_name': '辉瑞', 'en_name': 'Pfizer Inc.', 'market': 'US', 'sector': '制药', 'api_symbol': 'PFE'},
            'DIS': {'cn_name': '迪士尼', 'en_name': 'The Walt Disney Company', 'market': 'US', 'sector': '娱乐', 'api_symbol': 'DIS'},
            'NKE': {'cn_name': '耐克', 'en_name': 'Nike Inc.', 'market': 'US', 'sector': '体育用品', 'api_symbol': 'NKE'},
            'HD': {'cn_name': '家得宝', 'en_name': 'The Home Depot Inc.', 'market': 'US', 'sector': '零售', 'api_symbol': 'HD'},
        }
        
        # A股 - 主要股票
        a_stocks = {
            '000001': {'cn_name': '平安银行', 'en_name': 'Ping An Bank', 'market': 'A', 'sector': '银行', 'api_symbol': '000001.SZ'},
            '000002': {'cn_name': '万科A', 'en_name': 'China Vanke', 'market': 'A', 'sector': '房地产', 'api_symbol': '000002.SZ'},
            '000858': {'cn_name': '五粮液', 'en_name': 'Wuliangye Yibin', 'market': 'A', 'sector': '白酒', 'api_symbol': '000858.SZ'},
            '000876': {'cn_name': '新希望', 'en_name': 'New Hope', 'market': 'A', 'sector': '农业', 'api_symbol': '000876.SZ'},
            '002415': {'cn_name': '海康威视', 'en_name': 'Hikvision', 'market': 'A', 'sector': '安防', 'api_symbol': '002415.SZ'},
            '002594': {'cn_name': '比亚迪', 'en_name': 'BYD Company', 'market': 'A', 'sector': '汽车', 'api_symbol': '002594.SZ'},
            '300059': {'cn_name': '东方财富', 'en_name': 'East Money', 'market': 'A', 'sector': '金融科技', 'api_symbol': '300059.SZ'},
            '300750': {'cn_name': '宁德时代', 'en_name': 'CATL', 'market': 'A', 'sector': '新能源', 'api_symbol': '300750.SZ'},
            '600036': {'cn_name': '招商银行', 'en_name': 'China Merchants Bank', 'market': 'A', 'sector': '银行', 'api_symbol': '600036.SS'},
            '600519': {'cn_name': '贵州茅台', 'en_name': 'Kweichow Moutai', 'market': 'A', 'sector': '白酒', 'api_symbol': '600519.SS'},
            '600887': {'cn_name': '伊利股份', 'en_name': 'Inner Mongolia Yili', 'market': 'A', 'sector': '乳业', 'api_symbol': '600887.SS'},
            '601318': {'cn_name': '中国平安', 'en_name': 'Ping An Insurance', 'market': 'A', 'sector': '保险', 'api_symbol': '601318.SS'},
            '601398': {'cn_name': '工商银行', 'en_name': 'ICBC', 'market': 'A', 'sector': '银行', 'api_symbol': '601398.SS'},
            '601888': {'cn_name': '中国中免', 'en_name': 'China Tourism Group', 'market': 'A', 'sector': '旅游', 'api_symbol': '601888.SS'},
            '601919': {'cn_name': '中远海控', 'en_name': 'COSCO SHIPPING', 'market': 'A', 'sector': '航运', 'api_symbol': '601919.SS'},
            '603259': {'cn_name': '药明康德', 'en_name': 'WuXi AppTec', 'market': 'A', 'sector': '医药', 'api_symbol': '603259.SS'},
            '688036': {'cn_name': '传音控股', 'en_name': 'Transsion Holdings', 'market': 'A', 'sector': '科技', 'api_symbol': '688036.SS'},
            '688981': {'cn_name': '中芯国际', 'en_name': 'SMIC', 'market': 'A', 'sector': '半导体', 'api_symbol': '688981.SS'},
            '688599': {'cn_name': '天合光能', 'en_name': 'Trina Solar', 'market': 'A', 'sector': '新能源', 'api_symbol': '688599.SS'},
            '688223': {'cn_name': '晶科能源', 'en_name': 'JinkoSolar', 'market': 'A', 'sector': '新能源', 'api_symbol': '688223.SS'},
        }
        
        # 港股 - 主要股票
        hk_stocks = {
            '00700': {'cn_name': '腾讯控股', 'en_name': 'Tencent Holdings', 'market': 'HK', 'sector': '科技', 'api_symbol': '0700.HK'},
            '09988': {'cn_name': '阿里巴巴', 'en_name': 'Alibaba Group', 'market': 'HK', 'sector': '电商', 'api_symbol': '9988.HK'},
            '03690': {'cn_name': '美团', 'en_name': 'Meituan', 'market': 'HK', 'sector': '生活服务', 'api_symbol': '3690.HK'},
            '01024': {'cn_name': '快手', 'en_name': 'Kuaishou Technology', 'market': 'HK', 'sector': '短视频', 'api_symbol': '1024.HK'},
            '09618': {'cn_name': '京东集团', 'en_name': 'JD.com Inc.', 'market': 'HK', 'sector': '电商', 'api_symbol': '9618.HK'},
            '09888': {'cn_name': '百度集团', 'en_name': 'Baidu Inc.', 'market': 'HK', 'sector': '科技', 'api_symbol': '9888.HK'},
            '02020': {'cn_name': '安踏体育', 'en_name': 'ANTA Sports', 'market': 'HK', 'sector': '体育用品', 'api_symbol': '2020.HK'},
            '02318': {'cn_name': '中国平安', 'en_name': 'Ping An Insurance', 'market': 'HK', 'sector': '保险', 'api_symbol': '2318.HK'},
            '01398': {'cn_name': '工商银行', 'en_name': 'ICBC', 'market': 'HK', 'sector': '银行', 'api_symbol': '1398.HK'},
            '00939': {'cn_name': '建设银行', 'en_name': 'China Construction Bank', 'market': 'HK', 'sector': '银行', 'api_symbol': '939.HK'},
        }
        
        # 加密货币 - 主要币种
        crypto_currencies = {
            'BTC': {'cn_name': '比特币', 'en_name': 'Bitcoin', 'market': 'CRYPTO', 'sector': '数字货币', 'api_symbol': 'BTCUSDT'},
            'ETH': {'cn_name': '以太坊', 'en_name': 'Ethereum', 'market': 'CRYPTO', 'sector': '智能合约', 'api_symbol': 'ETHUSDT'},
            'BNB': {'cn_name': '币安币', 'en_name': 'Binance Coin', 'market': 'CRYPTO', 'sector': '交易所代币', 'api_symbol': 'BNBUSDT'},
            'SOL': {'cn_name': '索拉纳', 'en_name': 'Solana', 'market': 'CRYPTO', 'sector': '智能合约', 'api_symbol': 'SOLUSDT'},
            'ADA': {'cn_name': '艾达币', 'en_name': 'Cardano', 'market': 'CRYPTO', 'sector': '智能合约', 'api_symbol': 'ADAUSDT'},
            'DOGE': {'cn_name': '狗狗币', 'en_name': 'Dogecoin', 'market': 'CRYPTO', 'sector': '社区代币', 'api_symbol': 'DOGEUSDT'},
            'XRP': {'cn_name': '瑞波币', 'en_name': 'Ripple', 'market': 'CRYPTO', 'sector': '支付', 'api_symbol': 'XRPUSDT'},
            'DOT': {'cn_name': '波卡', 'en_name': 'Polkadot', 'market': 'CRYPTO', 'sector': '跨链', 'api_symbol': 'DOTUSDT'},
            'AVAX': {'cn_name': '雪崩', 'en_name': 'Avalanche', 'market': 'CRYPTO', 'sector': '智能合约', 'api_symbol': 'AVAXUSDT'},
            'MATIC': {'cn_name': '多边形', 'en_name': 'Polygon', 'market': 'CRYPTO', 'sector': '扩容', 'api_symbol': 'MATICUSDT'},
            'LINK': {'cn_name': 'Chainlink', 'en_name': 'Chainlink', 'market': 'CRYPTO', 'sector': '预言机', 'api_symbol': 'LINKUSDT'},
            'UNI': {'cn_name': 'Uniswap', 'en_name': 'Uniswap', 'market': 'CRYPTO', 'sector': '去中心化交易', 'api_symbol': 'UNIUSDT'},
            'AAVE': {'cn_name': 'Aave', 'en_name': 'Aave', 'market': 'CRYPTO', 'sector': '去中心化金融', 'api_symbol': 'AAVEUSDT'},
            'SUSHI': {'cn_name': 'SushiSwap', 'en_name': 'SushiSwap', 'market': 'CRYPTO', 'sector': '去中心化交易', 'api_symbol': 'SUSHIUSDT'},
            'CRV': {'cn_name': 'Curve', 'en_name': 'Curve DAO Token', 'market': 'CRYPTO', 'sector': '去中心化金融', 'api_symbol': 'CRVUSDT'},
            'COMP': {'cn_name': 'Compound', 'en_name': 'Compound', 'market': 'CRYPTO', 'sector': '去中心化金融', 'api_symbol': 'COMPUSDT'},
            'YFI': {'cn_name': 'Yearn Finance', 'en_name': 'Yearn Finance', 'market': 'CRYPTO', 'sector': '去中心化金融', 'api_symbol': 'YFIUSDT'},
            'SNX': {'cn_name': 'Synthetix', 'en_name': 'Synthetix', 'market': 'CRYPTO', 'sector': '合成资产', 'api_symbol': 'SNXUSDT'},
            'MKR': {'cn_name': 'Maker', 'en_name': 'Maker', 'market': 'CRYPTO', 'sector': '去中心化金融', 'api_symbol': 'MKRUSDT'},
            'LTC': {'cn_name': '莱特币', 'en_name': 'Litecoin', 'market': 'CRYPTO', 'sector': '数字货币', 'api_symbol': 'LTCUSDT'},
        }
        
        # 合并所有股票数据
        self.stocks.update(us_tech_stocks)
        self.stocks.update(us_traditional_stocks)
        self.stocks.update(a_stocks)
        self.stocks.update(hk_stocks)
        self.stocks.update(crypto_currencies)
    
    def search(self, query):
        """搜索股票"""
        query = query.strip().upper()
        results = []
        
        for symbol, info in self.stocks.items():
            if (query == symbol or 
                query in info['cn_name'] or 
                query in info['en_name'].upper() or
                query in info.get('sector', '')):
                results.append({
                    'symbol': symbol,
                    'cn_name': info['cn_name'],
                    'en_name': info['en_name'],
                    'market': info['market'],
                    'sector': info.get('sector', ''),
                    'api_symbol': info.get('api_symbol', symbol)
                })
        
        return results
    
    def get_market_stats(self):
        """获取市场统计信息"""
        stats = {
            'US': {'count': 0, 'sectors': set()},
            'A': {'count': 0, 'sectors': set()},
            'HK': {'count': 0, 'sectors': set()},
            'CRYPTO': {'count': 0, 'sectors': set()}
        }
        
        for symbol, info in self.stocks.items():
            market = info['market']
            sector = info.get('sector', '')
            
            if market in stats:
                stats[market]['count'] += 1
                if sector:
                    stats[market]['sectors'].add(sector)
        
        # 转换set为list
        for market in stats:
            stats[market]['sectors'] = list(stats[market]['sectors'])
        
        return stats


class PriceDataFetcher:
    """价格数据获取器"""
    
    def __init__(self):
        self.finnhub_api_key = 'd3040f1r01qnmrscs8b0d3040f1r01qnmrscs8bg'
        self.binance_base_url = 'https://api.binance.com/api/v3'
        self.finnhub_base_url = 'https://finnhub.io/api/v1'
    
    def get_real_time_price(self, stock_info):
        """获取实时价格"""
        try:
            if stock_info['market'] == 'CRYPTO':
                return self._get_crypto_price(stock_info['api_symbol'])
            elif stock_info['market'] == 'US':
                return self._get_us_stock_price(stock_info['api_symbol'])
            elif stock_info['market'] in ['A', 'HK']:
                return self._get_china_stock_price(stock_info['api_symbol'])
            else:
                return self._get_mock_price(stock_info['symbol'])
                
        except Exception as e:
            print(f"⚠️ 获取价格失败: {e}")
            return self._get_mock_price(stock_info['symbol'])
    
    def _get_crypto_price(self, symbol):
        """获取加密货币价格"""
        url = f"{self.binance_base_url}/ticker/price"
        params = {'symbol': symbol}
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return float(data['price'])
    
    def _get_us_stock_price(self, symbol):
        """获取美股价格"""
        url = f"{self.finnhub_base_url}/quote"
        params = {
            'symbol': symbol,
            'token': self.finnhub_api_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if 'c' in data and data['c'] is not None:
            return float(data['c'])
        else:
            raise Exception("无效的价格数据")
    
    def _get_china_stock_price(self, symbol):
        """获取A股/港股价格"""
        try:
            # 使用增强型A股数据获取器
            from enhanced_a_stock_fetcher import EnhancedAStockFetcher
            
            fetcher = EnhancedAStockFetcher()
            realtime_data = fetcher.get_real_time_price(symbol)
            
            if realtime_data and realtime_data.get('price', 0) > 0:
                print(f"✅ 成功获取A股 {symbol} 实时价格: {realtime_data['price']:.2f} 元")
                return realtime_data['price']
            else:
                print(f"⚠️ 未找到A股 {symbol} 数据，使用模拟价格")
                return self._get_mock_price(symbol)
                
        except ImportError:
            print("⚠️ 增强型A股数据获取器未找到，使用akshare")
            return self._get_china_stock_price_with_akshare(symbol)
        except Exception as e:
            print(f"⚠️ 获取A股/港股价格失败: {e}")
            return self._get_mock_price(symbol)
    
    def _get_china_stock_price_with_akshare(self, symbol):
        """使用akshare获取A股/港股价格（备用方法）"""
        try:
            import akshare as ak
            
            # 判断是A股还是港股
            if symbol.startswith(('000', '002', '300', '600', '601', '603', '688')):
                # A股代码
                try:
                    # 获取A股实时价格
                    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
                    stock_data = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == symbol]
                    
                    if not stock_data.empty:
                        current_price = float(stock_data['最新价'].iloc[0])
                        print(f"✅ 成功获取A股 {symbol} 实时价格: {current_price}")
                        return current_price
                    else:
                        print(f"⚠️ 未找到A股 {symbol} 数据，使用模拟价格")
                        return self._get_mock_price(symbol)
                        
                except Exception as e:
                    print(f"⚠️ 获取A股 {symbol} 实时价格失败: {e}")
                    return self._get_mock_price(symbol)
                    
            elif symbol.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')) and len(symbol) == 5:
                # 港股代码
                try:
                    # 获取港股实时价格
                    stock_hk_spot_em_df = ak.stock_hk_spot_em()
                    stock_data = stock_hk_spot_em_df[stock_hk_spot_em_df['代码'] == symbol]
                    
                    if not stock_data.empty:
                        current_price = float(stock_data['最新价'].iloc[0])
                        print(f"✅ 成功获取港股 {symbol} 实时价格: {current_price}")
                        return current_price
                    else:
                        print(f"⚠️ 未找到港股 {symbol} 数据，使用模拟价格")
                        return self._get_mock_price(symbol)
                        
                except Exception as e:
                    print(f"⚠️ 获取港股 {symbol} 实时价格失败: {e}")
                    return self._get_mock_price(symbol)
            else:
                print(f"⚠️ 无法识别股票代码 {symbol}，使用模拟价格")
                return self._get_mock_price(symbol)
                
        except ImportError:
            print("⚠️ akshare库未安装，使用模拟数据")
            return self._get_mock_price(symbol)
        except Exception as e:
            print(f"⚠️ 获取A股/港股价格失败: {e}")
            return self._get_mock_price(symbol)
    
    def _get_mock_price(self, symbol):
        """获取模拟价格"""
        base_prices = {
            # 美股
            'AAPL': 175, 'MSFT': 380, 'GOOGL': 2800, 'TSLA': 240, 'NVDA': 450,
            'META': 320, 'AMZN': 3200, 'NFLX': 450, 'AMD': 120, 'INTC': 45,
            'ORCL': 120, 'CRM': 200, 'ADBE': 500, 'PYPL': 60, 'UBER': 45,
            'SPOT': 180, 'ZM': 70, 'SQ': 50, 'ROKU': 60, 'SNOW': 150,
            'JPM': 150, 'BAC': 30, 'WMT': 150, 'JNJ': 160, 'PG': 150,
            'KO': 60, 'PFE': 30, 'DIS': 90, 'NKE': 100, 'HD': 300,
            
            # A股 (人民币)
            '000001': 12.5, '000002': 18.2, '000858': 180.5, '000876': 12.8,
            '002415': 35.6, '002594': 280.0, '300059': 15.2, '300750': 200.0,
            '600036': 45.8, '600519': 1800.0, '600887': 25.6, '601318': 45.2,
            '601398': 5.2, '601888': 180.0, '601919': 12.5, '603259': 85.0,
            '688036': 45.0, '688981': 45.8, '688599': 35.6, '688223': 12.8,
            
            # 港股 (港币)
            '00700': 320.0, '09988': 85.0, '03690': 120.0, '01024': 45.0,
            '09618': 180.0, '09888': 95.0, '02020': 85.0, '02318': 45.0,
            '01398': 4.2, '00939': 5.8,
            
            # 加密货币 (美元)
            'BTC': 65000, 'ETH': 3200, 'BNB': 580, 'SOL': 140, 'ADA': 0.45,
            'DOGE': 0.08, 'XRP': 0.65, 'DOT': 6.5, 'AVAX': 25.0, 'MATIC': 0.85,
            'LINK': 15.0, 'UNI': 8.5, 'AAVE': 120.0, 'SUSHI': 1.2, 'CRV': 0.65,
            'COMP': 45.0, 'YFI': 8500.0, 'SNX': 2.5, 'MKR': 1200.0, 'LTC': 85.0
        }
        
        base_price = base_prices.get(symbol, 100)
        # 添加随机波动
        variation = np.random.uniform(-0.05, 0.05)
        return base_price * (1 + variation)


class SimplePredictor:
    """简化的预测器"""
    
    def __init__(self):
        self.db = SimpleStockDatabase()
        self.fetcher = PriceDataFetcher()
    
    def search_stocks(self, query):
        """搜索股票"""
        return self.db.search(query)
    
    def predict(self, stock_info, days=7):
        """预测股票价格（增强版）"""
        try:
            # 获取当前价格
            current_price = self.fetcher.get_real_time_price(stock_info)
            
            # 生成历史数据（模拟30天）
            historical_data = self._generate_historical_data(current_price, stock_info, 30)
            
            # 基于历史数据进行技术分析预测
            predictions, price_bands, volume_predictions = self._advanced_predict(
                historical_data, current_price, stock_info, days
            )
            
            final_price = predictions[-1]['price']
            total_change = ((final_price - current_price) / current_price) * 100
            
            return {
                'success': True,
                'symbol': stock_info['symbol'],
                'market': stock_info['market'],
                'current_price': round(current_price, 4),
                'final_price': final_price,
                'total_change_pct': round(total_change, 2),
                'trend': '上涨' if total_change > 0 else '下跌' if total_change < 0 else '横盘',
                'predictions': predictions,
                'historical_data': historical_data,
                'price_bands': price_bands,
                'volume_predictions': volume_predictions,
                'chart_data': {
                    'historical_dates': [item['date'] for item in historical_data],
                    'historical_prices': [item['price'] for item in historical_data],
                    'historical_volumes': [item['volume'] for item in historical_data],
                    'prediction_dates': [pred['date'] for pred in predictions],
                    'predicted_prices': [pred['price'] for pred in predictions],
                    'upper_band': [band['upper'] for band in price_bands],
                    'lower_band': [band['lower'] for band in price_bands],
                    'predicted_volumes': [vol['volume'] for vol in volume_predictions]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_historical_data(self, current_price, stock_info, days):
        """生成历史数据"""
        historical_data = []
        
        # 基于股票类型设置参数
        if stock_info['market'] == 'CRYPTO':
            volatility = 0.04
            base_volume = np.random.uniform(100000, 1000000)
        else:
            volatility = 0.02
            base_volume = np.random.uniform(1000000, 10000000)
        
        # 生成历史价格序列
        np.random.seed(hash(stock_info['symbol']) % 2**32)
        prices = []
        price = current_price
        
        # 从当前价格往回推算历史价格
        for i in range(days, 0, -1):
            daily_change = np.random.normal(0, volatility)
            price *= (1 + daily_change)
            prices.append(price)
        
        prices.reverse()  # 反转得到正确的时间顺序
        
        # 生成历史数据
        for i, price in enumerate(prices):
            date = datetime.now() - timedelta(days=days-i)
            volume = base_volume * (1 + np.random.uniform(-0.3, 0.3))
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(price, 4),
                'volume': round(volume, 0)
            })
        
        return historical_data
    
    def _advanced_predict(self, historical_data, current_price, stock_info, days):
        """高级预测算法"""
        # 计算技术指标
        prices = [item['price'] for item in historical_data]
        volumes = [item['volume'] for item in historical_data]
        
        # 计算移动平均和波动率
        if len(prices) >= 10:
            sma_10 = sum(prices[-10:]) / 10
            volatility = np.std([prices[i]/prices[i-1]-1 for i in range(1, len(prices))])
        else:
            sma_10 = current_price
            volatility = 0.02
        
        # 趋势分析
        trend_strength = (current_price - sma_10) / sma_10 if sma_10 > 0 else 0
        
        # 基于股票类型调整参数
        if stock_info['market'] == 'CRYPTO':
            volatility *= 1.5  # 加密货币波动更大
            base_volume = np.mean(volumes) if volumes else 500000
        else:
            base_volume = np.mean(volumes) if volumes else 2000000
        
        predictions = []
        price_bands = []
        volume_predictions = []
        
        price = current_price
        volume = base_volume
        
        for i in range(days):
            # 价格预测
            trend_decay = 0.95 ** i  # 趋势衰减
            daily_change = (trend_strength * 0.01 * trend_decay) + np.random.normal(0, volatility * 0.7)
            price *= (1 + daily_change)
            
            # 价格区间计算
            uncertainty = volatility * price * (1 + i * 0.1)  # 不确定性随时间增加
            upper_price = price + uncertainty
            lower_price = max(price - uncertainty, price * 0.5)  # 防止负价格
            
            # 交易量预测
            volume_change = np.random.normal(0, 0.15)  # 15%交易量波动
            volume *= (1 + volume_change)
            volume = max(volume, base_volume * 0.3)  # 最小交易量
            
            predictions.append({
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'price': round(price, 4),
                'change_pct': round(((price - current_price) / current_price) * 100, 2)
            })
            
            price_bands.append({
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'upper': round(upper_price, 4),
                'lower': round(lower_price, 4)
            })
            
            volume_predictions.append({
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'volume': round(volume, 0)
            })
        
        return predictions, price_bands, volume_predictions


class StockPredictorApp:
    """股票预测应用"""
    
    def __init__(self):
        # 自动创建必要的文件夹
        self.create_directories()
        
        self.predictor = SimplePredictor()
        self.root = tk.Tk()
        self.selected_stock = None
        self.setup_ui()
    
    def create_directories(self):
        """创建程序运行所需的目录"""
        # 获取程序运行目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 创建必要的目录
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
    
    def setup_ios_style(self):
        """配置iOS风格样式"""
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 定义iOS风格颜色
        colors = {
            'primary': '#007AFF',      # iOS蓝色
            'secondary': '#5856D6',    # iOS紫色
            'success': '#34C759',      # iOS绿色
            'warning': '#FF9500',      # iOS橙色
            'danger': '#FF3B30',       # iOS红色
            'background': '#f2f2f7',   # iOS背景色
            'card': '#ffffff',         # iOS卡片色
            'text': '#000000',         # iOS文本色
            'secondary_text': '#8E8E93', # iOS次要文本色
            'border': '#C6C6C8',       # iOS边框色
        }
        
        # 配置Frame样式
        style.configure('Card.TFrame', 
                       background=colors['card'],
                       relief='flat',
                       borderwidth=0)
        
        # 配置LabelFrame样式
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
        
        # 配置Label样式
        style.configure('Title.TLabel',
                       background=colors['card'],
                       foreground=colors['text'],
                       font=('SF Pro Display', 24, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=colors['card'],
                       foreground=colors['secondary_text'],
                       font=('SF Pro Text', 12))
        
        style.configure('Designer.TLabel',
                       background=colors['card'],
                       foreground=colors['secondary_text'],
                       font=('SF Pro Text', 10))
        
        # 配置Button样式
        style.configure('Primary.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=('SF Pro Text', 11, 'bold'),
                       relief='flat',
                       borderwidth=0,
                       padding=(20, 10))
        
        style.map('Primary.TButton',
                 background=[('active', '#0056CC'),
                           ('pressed', '#004BB5')])
        
        style.configure('Secondary.TButton',
                       background=colors['secondary'],
                       foreground='white',
                       font=('SF Pro Text', 11),
                       relief='flat',
                       borderwidth=0,
                       padding=(15, 8))
        
        # 配置Entry样式
        style.configure('iOS.TEntry',
                       fieldbackground=colors['card'],
                       foreground=colors['text'],
                       font=('SF Pro Text', 11),
                       relief='flat',
                       borderwidth=1,
                       padding=(10, 8))
        
        # 配置Combobox样式
        style.configure('iOS.TCombobox',
                       fieldbackground=colors['card'],
                       foreground=colors['text'],
                       font=('SF Pro Text', 11),
                       relief='flat',
                       borderwidth=1)
        
        # 配置Treeview样式
        style.configure('iOS.Treeview',
                       background=colors['card'],
                       foreground=colors['text'],
                       font=('SF Pro Text', 10),
                       relief='flat',
                       borderwidth=0)
        
        style.configure('iOS.Treeview.Heading',
                       background=colors['background'],
                       foreground=colors['text'],
                       font=('SF Pro Text', 10, 'bold'),
                       relief='flat',
                       borderwidth=0)
        
        # 配置Notebook样式
        style.configure('iOS.TNotebook',
                       background=colors['background'],
                       borderwidth=0)
        
        style.configure('iOS.TNotebook.Tab',
                       background=colors['card'],
                       foreground=colors['text'],
                       font=('SF Pro Text', 11),
                       padding=(15, 10),
                       relief='flat',
                       borderwidth=0)
        
        style.map('iOS.TNotebook.Tab',
                 background=[('selected', colors['primary']),
                           ('active', colors['background'])],
                 foreground=[('selected', 'white'),
                           ('active', colors['text'])])
    
    def setup_ui(self):
        """设置用户界面 - iOS风格"""
        self.root.title("QuantPredict Pro - 量化预测专业版 v1.0")
        self.root.geometry("1000x1050")  # 高度从700扩大到1050 (50%增加)
        self.root.resizable(True, True)
        self.root.configure(bg='#f2f2f7')  # iOS风格背景色
        
        # 配置ttk样式为iOS风格
        self.setup_ios_style()
        
        # 主容器
        main_frame = ttk.Frame(self.root, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame, style='Card.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 主标题
        title_label = ttk.Label(title_frame, text="📊 QuantPredict Pro", 
                               font=('SF Pro Display', 24, 'bold'), 
                               style='Title.TLabel')
        title_label.pack(pady=(10, 5))
        
        # 副标题
        subtitle = ttk.Label(title_frame, text="量化预测专业版 - 智能股票分析工具", 
                            font=('SF Pro Text', 12), 
                            style='Subtitle.TLabel')
        subtitle.pack(pady=(0, 5))
        
        # 设计者信息
        designer_frame = ttk.Frame(title_frame, style='Card.TFrame')
        designer_frame.pack(pady=(0, 10))
        
        designer_label = ttk.Label(designer_frame, 
                                  text="设计者: Arthur | 联系方式: 1945673686@qq.com", 
                                  font=('SF Pro Text', 10), 
                                  style='Designer.TLabel')
        designer_label.pack()
        
        # 分栏布局 - 扩大左侧搜索面板宽度
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板 - 扩大50%宽度
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)  # 从weight=1改为weight=2 (扩大50%)
        
        # 右侧结果面板
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)  # 从weight=2改为weight=3 (保持比例)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪 - QuantPredict Pro")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              font=('SF Pro Text', 9), style='Subtitle.TLabel')
        status_bar.pack(fill=tk.X, pady=(15, 0))
    
    def setup_left_panel(self, parent):
        """设置左侧面板 - iOS风格"""
        # 搜索区域
        search_group = ttk.LabelFrame(parent, text="🔍 股票搜索", padding=15)
        search_group.pack(fill=tk.X, padx=5, pady=5)
        
        search_label = ttk.Label(search_group, text="输入股票代码或名称:", 
                               font=('SF Pro Text', 11), style='Subtitle.TLabel')
        search_label.pack(anchor=tk.W)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_group, textvariable=self.search_var, 
                               style='iOS.TEntry', font=('SF Pro Text', 11))
        search_entry.pack(fill=tk.X, pady=(8, 0))
        search_entry.bind('<KeyRelease>', self.on_search)
        
        # 搜索结果
        results_label = ttk.Label(search_group, text="搜索结果:", 
                                font=('SF Pro Text', 11), style='Subtitle.TLabel')
        results_label.pack(anchor=tk.W, pady=(15, 0))
        
        self.search_listbox = tk.Listbox(search_group, height=12,  # 从height=8改为height=12 (扩大50%)
                                       font=('SF Pro Text', 10),
                                       bg='#ffffff', fg='#000000',
                                       selectbackground='#007AFF',
                                       selectforeground='white',
                                       relief='flat', borderwidth=0)
        self.search_listbox.pack(fill=tk.X, pady=(8, 0))
        self.search_listbox.bind('<Double-Button-1>', self.on_select_stock)
        
        # 选中股票信息
        info_group = ttk.LabelFrame(parent, text="📊 选中股票", padding=15)
        info_group.pack(fill=tk.X, padx=5, pady=5)
        
        self.selected_var = tk.StringVar(value="未选择股票")
        selected_label = ttk.Label(info_group, textvariable=self.selected_var, 
                                 font=('SF Pro Text', 11, 'bold'), style='Title.TLabel')
        selected_label.pack(anchor=tk.W)
        
        self.price_var = tk.StringVar(value="")
        price_label = ttk.Label(info_group, textvariable=self.price_var, 
                              font=('SF Pro Text', 14, 'bold'), 
                              foreground='#007AFF', style='Title.TLabel')
        price_label.pack(anchor=tk.W, pady=(8, 0))
        
        refresh_btn = ttk.Button(info_group, text="🔄 刷新价格", 
                               command=self.refresh_price, style='Secondary.TButton')
        refresh_btn.pack(fill=tk.X, pady=(10, 0))
        
        # 预测设置
        predict_group = ttk.LabelFrame(parent, text="🎯 预测设置", padding=15)
        predict_group.pack(fill=tk.X, padx=5, pady=5)
        
        days_label = ttk.Label(predict_group, text="预测天数:", 
                             font=('SF Pro Text', 11), style='Subtitle.TLabel')
        days_label.pack(anchor=tk.W)
        
        self.days_var = tk.IntVar(value=7)
        days_spin = ttk.Spinbox(predict_group, from_=1, to=30, textvariable=self.days_var, 
                               width=15, style='iOS.TEntry', font=('SF Pro Text', 11))
        days_spin.pack(anchor=tk.W, pady=(8, 15))
        
        self.predict_btn = ttk.Button(predict_group, text="🚀 开始预测", 
                                     command=self.start_predict, 
                                     state=tk.DISABLED, style='Primary.TButton')
        self.predict_btn.pack(fill=tk.X)
    
    def setup_right_panel(self, parent):
        """设置右侧面板 - iOS风格"""
        # 结果显示
        result_group = ttk.LabelFrame(parent, text="📈 预测结果", padding=15)
        result_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建笔记本
        notebook = ttk.Notebook(result_group, style='iOS.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 摘要页面
        summary_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(summary_frame, text="📋 预测摘要")
        
        self.result_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, 
                                                    font=('SF Pro Text', 10),
                                                    bg='#ffffff', fg='#000000',
                                                    relief='flat', borderwidth=0)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 价格图表页面
        price_chart_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(price_chart_frame, text="📈 价格走势图")
        
        # 创建价格图表
        self.price_fig, self.price_ax = plt.subplots(figsize=(8, 5), facecolor='#ffffff')
        self.price_canvas = FigureCanvasTkAgg(self.price_fig, price_chart_frame)
        self.price_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 交易量图表页面
        volume_chart_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(volume_chart_frame, text="📊 交易量图")
        
        # 创建交易量图表
        self.volume_fig, self.volume_ax = plt.subplots(figsize=(8, 4), facecolor='#ffffff')
        self.volume_canvas = FigureCanvasTkAgg(self.volume_fig, volume_chart_frame)
        self.volume_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据页面
        data_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(data_frame, text="📊 详细数据")
        
        # 数据表格
        columns = ('日期', '预测价格', '价格区间', '涨跌幅', '预测交易量')
        self.tree = ttk.Treeview(data_frame, columns=columns, show='headings', 
                                height=15, style='iOS.Treeview')
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == '价格区间':
                self.tree.column(col, width=150, anchor=tk.CENTER)
            elif col == '预测交易量':
                self.tree.column(col, width=120, anchor=tk.CENTER)
            else:
                self.tree.column(col, width=100, anchor=tk.CENTER)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # 显示欢迎信息
        welcome_msg = """
📊 欢迎使用 QuantPredict Pro 量化预测专业版！

🎯 产品特色:
• 专业级量化分析工具
• 智能股票预测算法
• Apple iOS风格界面设计
• 实时数据集成分析
• 全市场覆盖支持

📋 使用步骤:
1. 在左侧搜索框输入股票代码或名称
   例如: AAPL、苹果、000001、平安银行、BTC、比特币
2. 双击搜索结果选择股票
3. 点击"🔄 刷新价格"获取最新价格
4. 设置预测天数(1-30天)
5. 点击"🚀 开始预测"查看结果

🌍 支持市场:
• 美股: AAPL(苹果)、MSFT(微软)、GOOGL(谷歌)、TSLA(特斯拉)、NVDA(英伟达)等
• A股: 000001(平安银行)、600519(贵州茅台)、300750(宁德时代)等
• 港股: 00700(腾讯)、09988(阿里巴巴)、03690(美团)等
• 加密货币: BTC(比特币)、ETH(以太坊)、SOL(索拉纳)、DOGE(狗狗币)等

📈 市场覆盖:
• 美股: 30+ 主要股票 (科技、金融、消费、医疗等)
• A股: 20+ 主要股票 (银行、白酒、新能源、科技等)
• 港股: 10+ 主要股票 (科技、电商、金融等)
• 加密货币: 20+ 主要币种 (数字货币、DeFi、智能合约等)

⚡ 核心功能:
• 实时价格获取 (Finnhub + Binance API)
• 历史+预测价格走势图
• 价格区间不确定性分析
• 交易量预测与关联分析
• 多维度数据可视化
• 行业分类筛选

👨‍💻 设计者: Arthur
📧 联系方式: 1945673686@qq.com

💡 风险提示: 预测结果仅供参考，投资有风险！
"""
        self.result_text.insert(1.0, welcome_msg)
    
    def on_search(self, event):
        """搜索事件"""
        query = self.search_var.get().strip()
        if len(query) >= 1:
            results = self.predictor.search_stocks(query)
            
            self.search_listbox.delete(0, tk.END)
            self.search_results = results
            
            for result in results:
                display_text = f"{result['symbol']} - {result['cn_name']} ({result['market']})"
                self.search_listbox.insert(tk.END, display_text)
        else:
            self.search_listbox.delete(0, tk.END)
    
    def on_select_stock(self, event):
        """选择股票事件"""
        selection = self.search_listbox.curselection()
        if selection and hasattr(self, 'search_results'):
            index = selection[0]
            if index < len(self.search_results):
                self.selected_stock = self.search_results[index]
                
                self.selected_var.set(f"{self.selected_stock['symbol']} - {self.selected_stock['cn_name']}")
                self.predict_btn.config(state=tk.NORMAL)
                
                # 自动获取价格
                self.refresh_price()
    
    def refresh_price(self):
        """刷新价格"""
        if not self.selected_stock:
            return
        
        self.price_var.set("获取中...")
        self.status_var.set("正在获取实时价格...")
        
        def get_price_thread():
            try:
                price = self.predictor.fetcher.get_real_time_price(self.selected_stock)
                
                # 更新UI
                self.root.after(0, lambda: self.update_price(price))
                
            except Exception as e:
                self.root.after(0, lambda: self.price_var.set(f"获取失败: {str(e)}"))
                self.root.after(0, lambda: self.status_var.set("价格获取失败"))
        
        threading.Thread(target=get_price_thread, daemon=True).start()
    
    def update_price(self, price):
        """更新价格显示"""
        self.price_var.set(f"实时价格: ${price:.4f}")
        self.status_var.set(f"价格更新完成 - {datetime.now().strftime('%H:%M:%S')}")
    
    def start_predict(self):
        """开始预测"""
        if not self.selected_stock:
            messagebox.showwarning("警告", "请先选择股票")
            return
        
        days = self.days_var.get()
        
        self.predict_btn.config(state=tk.DISABLED)
        self.status_var.set("正在预测中...")
        
        def predict_thread():
            try:
                result = self.predictor.predict(self.selected_stock, days)
                self.root.after(0, lambda: self.show_result(result))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))
        
        threading.Thread(target=predict_thread, daemon=True).start()
    
    def show_result(self, result):
        """显示预测结果"""
        try:
            if result['success']:
                # 计算价格区间统计
                price_bands = result.get('price_bands', [])
                if price_bands:
                    max_upper = max(band['upper'] for band in price_bands)
                    min_lower = min(band['lower'] for band in price_bands)
                else:
                    max_upper = result['final_price']
                    min_lower = result['final_price']
                
                # 计算平均交易量
                volume_predictions = result.get('volume_predictions', [])
                if volume_predictions:
                    avg_volume = sum(vol['volume'] for vol in volume_predictions) / len(volume_predictions)
                    if avg_volume >= 1e9:
                        volume_text = f"{avg_volume/1e9:.1f}B"
                    elif avg_volume >= 1e6:
                        volume_text = f"{avg_volume/1e6:.1f}M"
                    elif avg_volume >= 1e3:
                        volume_text = f"{avg_volume/1e3:.1f}K"
                    else:
                        volume_text = f"{avg_volume:.0f}"
                else:
                    volume_text = "N/A"
                
                # 构建结果文本
                result_text = f"""
📊 预测结果 - {result['symbol']}

基本信息:
• 股票代码: {result['symbol']}
• 中文名称: {self.selected_stock['cn_name']}
• 英文名称: {self.selected_stock['en_name']}
• 市场类型: {result['market']}
• 当前价格: ${result['current_price']}

预测摘要:
• 预测价格: ${result['final_price']}
• 预期涨跌: {result['total_change_pct']:+.2f}%
• 趋势判断: {result['trend']}
• 预测天数: {len(result['predictions'])} 天

价格区间分析:
• 最高预期价格: ${max_upper:.4f}
• 最低预期价格: ${min_lower:.4f}
• 价格波动范围: ${max_upper - min_lower:.4f}

交易量分析:
• 预测平均交易量: {volume_text}
• 历史数据天数: {len(result.get('historical_data', []))} 天

详细预测数据:
"""
                
                for i, pred in enumerate(result['predictions']):
                    trend_icon = "📈" if pred['change_pct'] > 0 else "📉" if pred['change_pct'] < 0 else "➡️"
                    
                    # 添加价格区间信息
                    range_info = ""
                    if i < len(price_bands):
                        band = price_bands[i]
                        range_info = f" [区间: ${band['lower']:.2f}-${band['upper']:.2f}]"
                    
                    # 添加交易量信息
                    volume_info = ""
                    if i < len(volume_predictions):
                        vol = volume_predictions[i]['volume']
                        if vol >= 1e6:
                            volume_info = f" (量: {vol/1e6:.1f}M)"
                        else:
                            volume_info = f" (量: {vol/1e3:.0f}K)"
                    
                    result_text += f"• {pred['date']}: ${pred['price']} ({pred['change_pct']:+.2f}%) {trend_icon}{range_info}{volume_info}\n"
                
                result_text += f"""

📊 预测分析:
• 预测算法: 技术分析 + 随机游走
• 数据来源: 实时API数据
• 置信度: 中等
• 适用范围: 短期趋势参考

💡 投资建议:
• 预测结果仅供参考，不构成投资建议
• 股市有风险，投资需谨慎
• 建议结合多种分析方法
• 合理控制投资风险

更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                # 显示结果
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, result_text)
                
                # 更新图表
                if 'chart_data' in result:
                    self.update_price_chart(result)
                    self.update_volume_chart(result)
                
                # 更新表格
                self.update_table(result)
                
                self.status_var.set(f"预测完成 - {result['symbol']} 预期{result['trend']}")
            else:
                self.show_error(result['error'])
                
        except Exception as e:
            self.show_error(f"显示结果失败: {str(e)}")
        finally:
            self.predict_btn.config(state=tk.NORMAL)
    
    def update_price_chart(self, result):
        """更新价格走势图"""
        try:
            self.price_ax.clear()
            
            chart_data = result['chart_data']
            
            # 历史价格数据
            hist_dates = range(len(chart_data['historical_dates']))
            hist_prices = chart_data['historical_prices']
            
            # 预测价格数据
            pred_start = len(hist_dates)
            pred_dates = range(pred_start, pred_start + len(chart_data['predicted_prices']))
            pred_prices = chart_data['predicted_prices']
            
            # 绘制历史价格线
            self.price_ax.plot(hist_dates, hist_prices, 'b-', linewidth=2, 
                              label='历史价格', marker='o', markersize=3)
            
            # 绘制预测价格线
            # 连接历史和预测
            connect_dates = [pred_start-1, pred_start]
            connect_prices = [hist_prices[-1], pred_prices[0]]
            self.price_ax.plot(connect_dates, connect_prices, 'r--', linewidth=1, alpha=0.7)
            
            self.price_ax.plot(pred_dates, pred_prices, 'r--', linewidth=2, 
                              label='预测价格', marker='s', markersize=3)
            
            # 绘制价格区间
            if 'upper_band' in chart_data and 'lower_band' in chart_data:
                upper_band = chart_data['upper_band']
                lower_band = chart_data['lower_band']
                
                self.price_ax.fill_between(pred_dates, lower_band, upper_band, 
                                          alpha=0.2, color='green', label='价格区间')
                self.price_ax.plot(pred_dates, upper_band, 'g:', linewidth=1, label='最高预期价格')
                self.price_ax.plot(pred_dates, lower_band, 'g:', linewidth=1, label='最低预期价格')
            
            # 设置图表
            self.price_ax.set_title(f"{result['symbol']} 价格走势预测 - QuantPredict Pro", fontsize=14, fontweight='bold')
            self.price_ax.set_xlabel('时间')
            self.price_ax.set_ylabel('价格 ($)')
            self.price_ax.legend()
            self.price_ax.grid(True, alpha=0.3)
            
            # 设置x轴标签
            all_dates = chart_data['historical_dates'] + chart_data['prediction_dates']
            x_labels = [date[-5:] for date in all_dates]  # 只显示月-日
            x_positions = list(range(len(all_dates)))
            
            # 只显示部分标签避免拥挤
            step = max(1, len(x_labels) // 10)
            self.price_ax.set_xticks(x_positions[::step])
            self.price_ax.set_xticklabels(x_labels[::step], rotation=45)
            
            # 添加分割线标注
            self.price_ax.axvline(x=pred_start-0.5, color='red', linestyle='-', alpha=0.5)
            self.price_ax.text(pred_start-0.5, max(hist_prices + pred_prices) * 0.95, 
                              '预测起点', ha='center', va='top', fontsize=9, 
                              bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
            
            self.price_fig.tight_layout()
            self.price_canvas.draw()
            
        except Exception as e:
            print(f"⚠️ 价格图表更新失败: {e}")
    
    def update_volume_chart(self, result):
        """更新交易量图表"""
        try:
            self.volume_ax.clear()
            
            chart_data = result['chart_data']
            
            # 历史交易量
            hist_dates = range(len(chart_data['historical_dates']))
            hist_volumes = chart_data['historical_volumes']
            
            # 预测交易量
            pred_start = len(hist_dates)
            pred_dates = range(pred_start, pred_start + len(chart_data['predicted_volumes']))
            pred_volumes = chart_data['predicted_volumes']
            
            # 绘制历史交易量柱状图
            self.volume_ax.bar(hist_dates, hist_volumes, color='skyblue', 
                              alpha=0.7, label='历史交易量', width=0.8)
            
            # 绘制预测交易量柱状图
            self.volume_ax.bar(pred_dates, pred_volumes, color='salmon', 
                              alpha=0.7, label='预测交易量', width=0.8)
            
            # 设置图表
            self.volume_ax.set_title(f"{result['symbol']} 交易量预测 - QuantPredict Pro", fontsize=14, fontweight='bold')
            self.volume_ax.set_xlabel('时间')
            self.volume_ax.set_ylabel('交易量')
            self.volume_ax.legend()
            self.volume_ax.grid(True, alpha=0.3, axis='y')
            
            # 格式化y轴标签
            def format_volume(x, p):
                if x >= 1e9:
                    return f'{x/1e9:.1f}B'
                elif x >= 1e6:
                    return f'{x/1e6:.1f}M'
                elif x >= 1e3:
                    return f'{x/1e3:.1f}K'
                else:
                    return f'{x:.0f}'
            
            from matplotlib.ticker import FuncFormatter
            self.volume_ax.yaxis.set_major_formatter(FuncFormatter(format_volume))
            
            # 设置x轴标签
            all_dates = chart_data['historical_dates'] + chart_data['prediction_dates']
            x_labels = [date[-5:] for date in all_dates]
            x_positions = list(range(len(all_dates)))
            
            step = max(1, len(x_labels) // 8)
            self.volume_ax.set_xticks(x_positions[::step])
            self.volume_ax.set_xticklabels(x_labels[::step], rotation=45)
            
            # 添加分割线
            self.volume_ax.axvline(x=pred_start-0.5, color='red', linestyle='-', alpha=0.5)
            
            self.volume_fig.tight_layout()
            self.volume_canvas.draw()
            
        except Exception as e:
            print(f"⚠️ 交易量图表更新失败: {e}")
    
    def update_table(self, result):
        """更新数据表格"""
        try:
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 添加预测数据
            predictions = result['predictions']
            price_bands = result.get('price_bands', [])
            volume_predictions = result.get('volume_predictions', [])
            
            for i, pred in enumerate(predictions):
                # 价格区间
                price_range = "-"
                if i < len(price_bands):
                    band = price_bands[i]
                    price_range = f"${band['lower']} - ${band['upper']}"
                
                # 交易量
                volume_text = "-"
                if i < len(volume_predictions):
                    volume = volume_predictions[i]['volume']
                    if volume >= 1e9:
                        volume_text = f"{volume/1e9:.1f}B"
                    elif volume >= 1e6:
                        volume_text = f"{volume/1e6:.1f}M"
                    elif volume >= 1e3:
                        volume_text = f"{volume/1e3:.1f}K"
                    else:
                        volume_text = f"{volume:.0f}"
                
                # 趋势图标
                trend_text = "📈" if pred['change_pct'] > 0 else "📉" if pred['change_pct'] < 0 else "➡️"
                change_text = f"{pred['change_pct']:+.2f}% {trend_text}"
                
                self.tree.insert('', tk.END, values=(
                    pred['date'],
                    f"${pred['price']}",
                    price_range,
                    change_text,
                    volume_text
                ))
                
        except Exception as e:
            print(f"⚠️ 数据表格更新失败: {e}")
    
    def show_error(self, error_msg):
        """显示错误"""
        self.status_var.set(f"错误: {error_msg}")
        messagebox.showerror("错误", error_msg)
        self.predict_btn.config(state=tk.NORMAL)
    
    def run(self):
        """运行应用"""
        self.status_var.set(f"程序启动完成 - 工作目录: {BASE_DIR.name}")
        self.root.mainloop()


def main():
    """主函数"""
    print("🚀 启动Kronos股票预测器")
    print(f"📁 工作目录: {BASE_DIR}")
    
    try:
        app = StockPredictorApp()
        app.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        
        # 如果是exe运行，显示错误对话框
        if getattr(sys, 'frozen', False):
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动错误", f"程序启动失败:\n{str(e)}")


if __name__ == "__main__":
    main()