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
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import sys
import os
import atexit
import signal
import threading
import subprocess
import psutil

# 导入A股和汇率转换功能
A_STOCK_AVAILABLE = False
try:
    from enhanced_a_stock_fetcher import EnhancedAStockFetcher
    from cn_stock_fetcher import CNStockFetcher, set_tushare_token
    from currency_converter import CurrencyConverter
    A_STOCK_AVAILABLE = True
    print("✅ A股和汇率转换功能模块导入成功")
except ImportError as e:
    print(f"⚠️ A股功能模块导入失败: {e}")
    A_STOCK_AVAILABLE = False

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['font.size'] = 10  # 设置默认字体大小


class SimpleStockDatabase:
    """美股和加密货币数据库 - 仅支持美股和加密货币"""
    
    def __init__(self):
        self.stocks = {}
        self._load_us_crypto_stocks()
    
    def _load_us_crypto_stocks(self):
        """加载美股和加密货币数据"""
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
        
        # 合并美股和加密货币数据
        self.stocks.update(us_tech_stocks)
        self.stocks.update(us_traditional_stocks)
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

class AStockDatabase:
    """A股和港股数据库 - 包含市面上所有股票信息"""
    
    def __init__(self):
        self.stocks = {}
        self._load_a_hk_stocks()
    
    def _load_a_hk_stocks(self):
        """加载A股和港股数据"""
        # A股 - 主要科技股
        a_tech_stocks = {
            # 白酒龙头
            '600519': {'cn_name': '贵州茅台', 'en_name': 'Kweichow Moutai Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '600519.SH'},
            '000858': {'cn_name': '五粮液', 'en_name': 'Wuliangye Yibin Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '000858.SZ'},
            '000568': {'cn_name': '泸州老窖', 'en_name': 'Luzhou Laojiao Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '000568.SZ'},
            '000596': {'cn_name': '古井贡酒', 'en_name': 'Anhui Gujing Distillery Company Limited', 'market': 'A', 'sector': '白酒', 'api_symbol': '000596.SZ'},
            '600809': {'cn_name': '山西汾酒', 'en_name': 'Shanxi Xinghuacun Fen Wine Factory Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '600809.SH'},
            '000799': {'cn_name': '酒鬼酒', 'en_name': 'Jiugui Liquor Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '000799.SZ'},
            
            # 银行股
            '000001': {'cn_name': '平安银行', 'en_name': 'Ping An Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '000001.SZ'},
            '600036': {'cn_name': '招商银行', 'en_name': 'China Merchants Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '600036.SH'},
            '600000': {'cn_name': '浦发银行', 'en_name': 'Shanghai Pudong Development Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '600000.SH'},
            '601398': {'cn_name': '工商银行', 'en_name': 'Industrial and Commercial Bank of China Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '601398.SH'},
            '601939': {'cn_name': '建设银行', 'en_name': 'China Construction Bank Corporation', 'market': 'A', 'sector': '银行', 'api_symbol': '601939.SH'},
            '601288': {'cn_name': '农业银行', 'en_name': 'Agricultural Bank of China Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '601288.SH'},
            '601988': {'cn_name': '中国银行', 'en_name': 'Bank of China Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '601988.SH'},
            '600016': {'cn_name': '民生银行', 'en_name': 'China Minsheng Banking Corp.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '600016.SH'},
            '601166': {'cn_name': '兴业银行', 'en_name': 'Industrial Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '601166.SH'},
            '600015': {'cn_name': '华夏银行', 'en_name': 'Hua Xia Bank Co.,Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '600015.SH'},
            
            # 科技股
            '000725': {'cn_name': '京东方A', 'en_name': 'BOE Technology Group Co.,Ltd.', 'market': 'A', 'sector': '电子', 'api_symbol': '000725.SZ'},
            '002415': {'cn_name': '海康威视', 'en_name': 'Hangzhou Hikvision Digital Technology Co.,Ltd.', 'market': 'A', 'sector': '安防', 'api_symbol': '002415.SZ'},
            '300059': {'cn_name': '东方财富', 'en_name': 'East Money Information Co.,Ltd.', 'market': 'A', 'sector': '金融科技', 'api_symbol': '300059.SZ'},
            '000063': {'cn_name': '中兴通讯', 'en_name': 'ZTE Corporation', 'market': 'A', 'sector': '通信', 'api_symbol': '000063.SZ'},
            '002594': {'cn_name': '比亚迪', 'en_name': 'BYD Company Limited', 'market': 'A', 'sector': '新能源汽车', 'api_symbol': '002594.SZ'},
            '300750': {'cn_name': '宁德时代', 'en_name': 'Contemporary Amperex Technology Co.,Limited', 'market': 'A', 'sector': '电池', 'api_symbol': '300750.SZ'},
            '002304': {'cn_name': '洋河股份', 'en_name': 'Yanghe Distillery Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '002304.SZ'},
            '300014': {'cn_name': '亿纬锂能', 'en_name': 'EVE Energy Co.,Ltd.', 'market': 'A', 'sector': '电池', 'api_symbol': '300014.SZ'},
            '002460': {'cn_name': '赣锋锂业', 'en_name': 'Ganfeng Lithium Co.,Ltd.', 'market': 'A', 'sector': '有色金属', 'api_symbol': '002460.SZ'},
            '300274': {'cn_name': '阳光电源', 'en_name': 'Sungrow Power Supply Co.,Ltd.', 'market': 'A', 'sector': '新能源', 'api_symbol': '300274.SZ'},
            '688981': {'cn_name': '中芯国际', 'en_name': 'Semiconductor Manufacturing International Corporation', 'market': 'A', 'sector': '半导体', 'api_symbol': '688981.SH'},
            '688036': {'cn_name': '传音控股', 'en_name': 'Transsion Holdings Co.,Ltd.', 'market': 'A', 'sector': '消费电子', 'api_symbol': '688036.SH'},
            '688599': {'cn_name': '天合光能', 'en_name': 'Trina Solar Co.,Ltd.', 'market': 'A', 'sector': '新能源', 'api_symbol': '688599.SH'},
            '688223': {'cn_name': '晶科能源', 'en_name': 'JinkoSolar Holding Co.,Ltd.', 'market': 'A', 'sector': '新能源', 'api_symbol': '688223.SH'},
            '300760': {'cn_name': '迈瑞医疗', 'en_name': 'Shenzhen Mindray Bio-Medical Electronics Co.,Ltd.', 'market': 'A', 'sector': '医疗器械', 'api_symbol': '300760.SZ'},
            '300015': {'cn_name': '爱尔眼科', 'en_name': 'Aier Eye Hospital Group Co.,Ltd.', 'market': 'A', 'sector': '医疗服务', 'api_symbol': '300015.SZ'},
            '300347': {'cn_name': '泰格医药', 'en_name': 'Tigermed Consulting Co.,Ltd.', 'market': 'A', 'sector': '医药服务', 'api_symbol': '300347.SZ'},
            '300601': {'cn_name': '康泰生物', 'en_name': 'Shenzhen Kangtai Biological Products Co.,Ltd.', 'market': 'A', 'sector': '生物医药', 'api_symbol': '300601.SZ'},
            '300122': {'cn_name': '智飞生物', 'en_name': 'Chongqing Zhifei Biological Products Co.,Ltd.', 'market': 'A', 'sector': '生物医药', 'api_symbol': '300122.SZ'},
            '300142': {'cn_name': '沃森生物', 'en_name': 'Yunnan Walvax Biotechnology Co.,Ltd.', 'market': 'A', 'sector': '生物医药', 'api_symbol': '300142.SZ'},
            
            # 医药股
            '600276': {'cn_name': '恒瑞医药', 'en_name': 'Jiangsu Hengrui Medicine Co.,Ltd.', 'market': 'A', 'sector': '医药', 'api_symbol': '600276.SH'},
            '600196': {'cn_name': '复星医药', 'en_name': 'Shanghai Fosun Pharmaceutical (Group) Co.,Ltd.', 'market': 'A', 'sector': '医药', 'api_symbol': '600196.SH'},
            '000538': {'cn_name': '云南白药', 'en_name': 'Yunnan Baiyao Group Co.,Ltd.', 'market': 'A', 'sector': '医药', 'api_symbol': '000538.SZ'},
            '600521': {'cn_name': '华海药业', 'en_name': 'Zhejiang Huahai Pharmaceutical Co.,Ltd.', 'market': 'A', 'sector': '医药', 'api_symbol': '600521.SH'},
            '000661': {'cn_name': '长春高新', 'en_name': 'Changchun High & New Technology Industry (Group) Inc.', 'market': 'A', 'sector': '医药', 'api_symbol': '000661.SZ'},
            '002007': {'cn_name': '华兰生物', 'en_name': 'Hualan Biological Engineering Inc.', 'market': 'A', 'sector': '生物医药', 'api_symbol': '002007.SZ'},
            '600867': {'cn_name': '通化东宝', 'en_name': 'Tonghua Dongbao Pharmaceutical Co.,Ltd.', 'market': 'A', 'sector': '医药', 'api_symbol': '600867.SH'},
            '300009': {'cn_name': '安科生物', 'en_name': 'Anhui Anke Biotechnology (Group) Co.,Ltd.', 'market': 'A', 'sector': '生物医药', 'api_symbol': '300009.SZ'},
            
            # 食品饮料
            '600887': {'cn_name': '伊利股份', 'en_name': 'Inner Mongolia Yili Industrial Group Co.,Ltd.', 'market': 'A', 'sector': '食品饮料', 'api_symbol': '600887.SH'},
            '000895': {'cn_name': '双汇发展', 'en_name': 'Henan Shuanghui Investment & Development Co.,Ltd.', 'market': 'A', 'sector': '食品加工', 'api_symbol': '000895.SZ'},
            '600597': {'cn_name': '光明乳业', 'en_name': 'Bright Dairy & Food Co.,Ltd.', 'market': 'A', 'sector': '食品饮料', 'api_symbol': '600597.SH'},
            '000876': {'cn_name': '新希望', 'en_name': 'New Hope Liuhe Co.,Ltd.', 'market': 'A', 'sector': '农业', 'api_symbol': '000876.SZ'},
            
            # 保险金融
            '601318': {'cn_name': '中国平安', 'en_name': 'Ping An Insurance (Group) Company of China, Ltd.', 'market': 'A', 'sector': '保险', 'api_symbol': '601318.SH'},
            '601601': {'cn_name': '中国太保', 'en_name': 'China Pacific Insurance (Group) Co.,Ltd.', 'market': 'A', 'sector': '保险', 'api_symbol': '601601.SH'},
            '601628': {'cn_name': '中国人寿', 'en_name': 'China Life Insurance Company Limited', 'market': 'A', 'sector': '保险', 'api_symbol': '601628.SH'},
            '000166': {'cn_name': '申万宏源', 'en_name': 'Shenwan Hongyuan Group Co.,Ltd.', 'market': 'A', 'sector': '证券', 'api_symbol': '000166.SZ'},
            '600030': {'cn_name': '中信证券', 'en_name': 'CITIC Securities Company Limited', 'market': 'A', 'sector': '证券', 'api_symbol': '600030.SH'},
            '000776': {'cn_name': '广发证券', 'en_name': 'GF Securities Co.,Ltd.', 'market': 'A', 'sector': '证券', 'api_symbol': '000776.SZ'},
            '600837': {'cn_name': '海通证券', 'en_name': 'Haitong Securities Co.,Ltd.', 'market': 'A', 'sector': '证券', 'api_symbol': '600837.SH'},
            '601688': {'cn_name': '华泰证券', 'en_name': 'Huatai Securities Co.,Ltd.', 'market': 'A', 'sector': '证券', 'api_symbol': '601688.SH'},
            
            # 房地产
            '000002': {'cn_name': '万科A', 'en_name': 'China Vanke Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '000002.SZ'},
            '600048': {'cn_name': '保利发展', 'en_name': 'Poly Developments and Holdings Group Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '600048.SH'},
            '000069': {'cn_name': '华侨城A', 'en_name': 'Overseas Chinese Town (Asia) Holdings Limited', 'market': 'A', 'sector': '房地产', 'api_symbol': '000069.SZ'},
            '600383': {'cn_name': '金地集团', 'en_name': 'Gemdale Corporation', 'market': 'A', 'sector': '房地产', 'api_symbol': '600383.SH'},
            '001979': {'cn_name': '招商蛇口', 'en_name': 'China Merchants Shekou Industrial Zone Holdings Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '001979.SZ'},
            '000656': {'cn_name': '金科股份', 'en_name': 'Jinke Property Group Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '000656.SZ'},
            
            # 汽车
            '600104': {'cn_name': '上汽集团', 'en_name': 'SAIC Motor Corporation Limited', 'market': 'A', 'sector': '汽车', 'api_symbol': '600104.SH'},
            '000625': {'cn_name': '长安汽车', 'en_name': 'Changan Automobile Co.,Ltd.', 'market': 'A', 'sector': '汽车', 'api_symbol': '000625.SZ'},
            '000800': {'cn_name': '一汽解放', 'en_name': 'FAW Jiefang Group Co.,Ltd.', 'market': 'A', 'sector': '汽车', 'api_symbol': '000800.SZ'},
            '600741': {'cn_name': '华域汽车', 'en_name': 'Huayu Automotive Systems Co.,Ltd.', 'market': 'A', 'sector': '汽车零部件', 'api_symbol': '600741.SH'},
            '000338': {'cn_name': '潍柴动力', 'en_name': 'Weichai Power Co.,Ltd.', 'market': 'A', 'sector': '汽车零部件', 'api_symbol': '000338.SZ'},
            '002050': {'cn_name': '三花智控', 'en_name': 'Sanhua Intelligent Controls Co.,Ltd.', 'market': 'A', 'sector': '汽车零部件', 'api_symbol': '002050.SZ'},
            
            # 电力能源
            '600900': {'cn_name': '长江电力', 'en_name': 'China Yangtze Power Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '600900.SH'},
            '600886': {'cn_name': '国投电力', 'en_name': 'SDIC Power Holdings Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '600886.SH'},
            '000027': {'cn_name': '深圳能源', 'en_name': 'Shenzhen Energy Group Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '000027.SZ'},
            '600795': {'cn_name': '国电电力', 'en_name': 'GD Power Development Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '600795.SH'},
            '600027': {'cn_name': '华电国际', 'en_name': 'Huadian Power International Corporation Limited', 'market': 'A', 'sector': '电力', 'api_symbol': '600027.SH'},
            
            # 机械制造
            '600031': {'cn_name': '三一重工', 'en_name': 'Sany Heavy Industry Co.,Ltd.', 'market': 'A', 'sector': '机械', 'api_symbol': '600031.SH'},
            '000157': {'cn_name': '中联重科', 'en_name': 'Zoomlion Heavy Industry Science & Technology Co.,Ltd.', 'market': 'A', 'sector': '机械', 'api_symbol': '000157.SZ'},
            '600320': {'cn_name': '振华重工', 'en_name': 'Shanghai Zhenhua Heavy Industries Co.,Ltd.', 'market': 'A', 'sector': '机械', 'api_symbol': '600320.SH'},
            '002202': {'cn_name': '金风科技', 'en_name': 'Xinjiang Goldwind Science & Technology Co.,Ltd.', 'market': 'A', 'sector': '新能源设备', 'api_symbol': '002202.SZ'},
        }
        
        # A股 - 传统行业
        a_traditional_stocks = {
            # 石油化工
            '600028': {'cn_name': '中国石化', 'en_name': 'China Petroleum & Chemical Corporation', 'market': 'A', 'sector': '石油化工', 'api_symbol': '600028.SH'},
            '601857': {'cn_name': '中国石油', 'en_name': 'PetroChina Company Limited', 'market': 'A', 'sector': '石油', 'api_symbol': '601857.SH'},
            '600688': {'cn_name': '上海石化', 'en_name': 'Sinopec Shanghai Petrochemical Company Limited', 'market': 'A', 'sector': '石油化工', 'api_symbol': '600688.SH'},
            '000792': {'cn_name': '盐湖股份', 'en_name': 'Qinghai Salt Lake Industry Co.,Ltd.', 'market': 'A', 'sector': '化工', 'api_symbol': '000792.SZ'},
            '600309': {'cn_name': '万华化学', 'en_name': 'Wanhua Chemical Group Co.,Ltd.', 'market': 'A', 'sector': '化工', 'api_symbol': '600309.SH'},
            '002493': {'cn_name': '荣盛石化', 'en_name': 'Rongsheng Petrochemical Co.,Ltd.', 'market': 'A', 'sector': '化工', 'api_symbol': '002493.SZ'},
            '600346': {'cn_name': '恒力石化', 'en_name': 'Hengli Petrochemical Co.,Ltd.', 'market': 'A', 'sector': '化工', 'api_symbol': '600346.SH'},
            '000703': {'cn_name': '恒逸石化', 'en_name': 'Hengyi Petrochemical Co.,Ltd.', 'market': 'A', 'sector': '化工', 'api_symbol': '000703.SZ'},
            
            # 通信运营商
            '600050': {'cn_name': '中国联通', 'en_name': 'China United Network Communications Limited', 'market': 'A', 'sector': '通信', 'api_symbol': '600050.SH'},
            '000063': {'cn_name': '中兴通讯', 'en_name': 'ZTE Corporation', 'market': 'A', 'sector': '通信', 'api_symbol': '000063.SZ'},
            '600522': {'cn_name': '中天科技', 'en_name': 'Zhongtian Technology Co.,Ltd.', 'market': 'A', 'sector': '通信设备', 'api_symbol': '600522.SH'},
            '002396': {'cn_name': '星网锐捷', 'en_name': 'Ruijie Networks Co.,Ltd.', 'market': 'A', 'sector': '通信设备', 'api_symbol': '002396.SZ'},
            '300308': {'cn_name': '中际旭创', 'en_name': 'Suzhou TFC Optical Communication Co.,Ltd.', 'market': 'A', 'sector': '通信设备', 'api_symbol': '300308.SZ'},
            
            # 建材建筑
            '600585': {'cn_name': '海螺水泥', 'en_name': 'Anhui Conch Cement Company Limited', 'market': 'A', 'sector': '建材', 'api_symbol': '600585.SH'},
            '000877': {'cn_name': '天山股份', 'en_name': 'Tianshan Cement Co.,Ltd.', 'market': 'A', 'sector': '建材', 'api_symbol': '000877.SZ'},
            '600801': {'cn_name': '华新水泥', 'en_name': 'Huaxin Cement Co.,Ltd.', 'market': 'A', 'sector': '建材', 'api_symbol': '600801.SH'},
            '000789': {'cn_name': '万年青', 'en_name': 'Jiangxi Wannianqing Cement Co.,Ltd.', 'market': 'A', 'sector': '建材', 'api_symbol': '000789.SZ'},
            '601668': {'cn_name': '中国建筑', 'en_name': 'China State Construction Engineering Corporation Limited', 'market': 'A', 'sector': '建筑', 'api_symbol': '601668.SH'},
            '000002': {'cn_name': '万科A', 'en_name': 'China Vanke Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '000002.SZ'},
            '600048': {'cn_name': '保利发展', 'en_name': 'Poly Developments and Holdings Group Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '600048.SH'},
            '000069': {'cn_name': '华侨城A', 'en_name': 'Overseas Chinese Town (Asia) Holdings Limited', 'market': 'A', 'sector': '房地产', 'api_symbol': '000069.SZ'},
            '600383': {'cn_name': '金地集团', 'en_name': 'Gemdale Corporation', 'market': 'A', 'sector': '房地产', 'api_symbol': '600383.SH'},
            '001979': {'cn_name': '招商蛇口', 'en_name': 'China Merchants Shekou Industrial Zone Holdings Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '001979.SZ'},
            '000656': {'cn_name': '金科股份', 'en_name': 'Jinke Property Group Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '000656.SZ'},
            '600606': {'cn_name': '绿地控股', 'en_name': 'Greenland Holdings Corporation Limited', 'market': 'A', 'sector': '房地产', 'api_symbol': '600606.SH'},
            '000718': {'cn_name': '苏宁环球', 'en_name': 'Suning Universal Co.,Ltd.', 'market': 'A', 'sector': '房地产', 'api_symbol': '000718.SZ'},
            
            # 交通运输
            '600009': {'cn_name': '上海机场', 'en_name': 'Shanghai International Airport Co.,Ltd.', 'market': 'A', 'sector': '机场', 'api_symbol': '600009.SH'},
            '000089': {'cn_name': '深圳机场', 'en_name': 'Shenzhen Airport Co.,Ltd.', 'market': 'A', 'sector': '机场', 'api_symbol': '000089.SZ'},
            '600115': {'cn_name': '东方航空', 'en_name': 'China Eastern Airlines Corporation Limited', 'market': 'A', 'sector': '航空', 'api_symbol': '600115.SH'},
            '000001': {'cn_name': '平安银行', 'en_name': 'Ping An Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '000001.SZ'},
            '600036': {'cn_name': '招商银行', 'en_name': 'China Merchants Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '600036.SH'},
            '600000': {'cn_name': '浦发银行', 'en_name': 'Shanghai Pudong Development Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '600000.SH'},
            '601398': {'cn_name': '工商银行', 'en_name': 'Industrial and Commercial Bank of China Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '601398.SH'},
            '601939': {'cn_name': '建设银行', 'en_name': 'China Construction Bank Corporation', 'market': 'A', 'sector': '银行', 'api_symbol': '601939.SH'},
            '601288': {'cn_name': '农业银行', 'en_name': 'Agricultural Bank of China Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '601288.SH'},
            '601988': {'cn_name': '中国银行', 'en_name': 'Bank of China Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '601988.SH'},
            '600016': {'cn_name': '民生银行', 'en_name': 'China Minsheng Banking Corp.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '600016.SH'},
            '601166': {'cn_name': '兴业银行', 'en_name': 'Industrial Bank Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '601166.SH'},
            '600015': {'cn_name': '华夏银行', 'en_name': 'Hua Xia Bank Co.,Limited', 'market': 'A', 'sector': '银行', 'api_symbol': '600015.SH'},
            '002142': {'cn_name': '宁波银行', 'en_name': 'Bank of Ningbo Co.,Ltd.', 'market': 'A', 'sector': '银行', 'api_symbol': '002142.SZ'},
            
            # 钢铁有色
            '600019': {'cn_name': '宝钢股份', 'en_name': 'Baoshan Iron & Steel Co.,Ltd.', 'market': 'A', 'sector': '钢铁', 'api_symbol': '600019.SH'},
            '000708': {'cn_name': '中信特钢', 'en_name': 'CITIC Special Steel Group Co.,Ltd.', 'market': 'A', 'sector': '钢铁', 'api_symbol': '000708.SZ'},
            '600362': {'cn_name': '江西铜业', 'en_name': 'Jiangxi Copper Company Limited', 'market': 'A', 'sector': '有色金属', 'api_symbol': '600362.SH'},
            '000060': {'cn_name': '中金岭南', 'en_name': 'Shenzhen Zhongjin Lingnan Nonfemet Co.,Ltd.', 'market': 'A', 'sector': '有色金属', 'api_symbol': '000060.SZ'},
            '600111': {'cn_name': '北方稀土', 'en_name': 'China Northern Rare Earth (Group) High-Tech Co.,Ltd.', 'market': 'A', 'sector': '有色金属', 'api_symbol': '600111.SH'},
            '002460': {'cn_name': '赣锋锂业', 'en_name': 'Ganfeng Lithium Co.,Ltd.', 'market': 'A', 'sector': '有色金属', 'api_symbol': '002460.SZ'},
            '300014': {'cn_name': '亿纬锂能', 'en_name': 'EVE Energy Co.,Ltd.', 'market': 'A', 'sector': '电池', 'api_symbol': '300014.SZ'},
            
            # 煤炭电力
            '601088': {'cn_name': '中国神华', 'en_name': 'China Shenhua Energy Company Limited', 'market': 'A', 'sector': '煤炭', 'api_symbol': '601088.SH'},
            '000983': {'cn_name': '西山煤电', 'en_name': 'Shanxi Xishan Coal and Electricity Power Co.,Ltd.', 'market': 'A', 'sector': '煤炭', 'api_symbol': '000983.SZ'},
            '600188': {'cn_name': '兖州煤业', 'en_name': 'Yanzhou Coal Mining Company Limited', 'market': 'A', 'sector': '煤炭', 'api_symbol': '600188.SH'},
            '600900': {'cn_name': '长江电力', 'en_name': 'China Yangtze Power Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '600900.SH'},
            '600886': {'cn_name': '国投电力', 'en_name': 'SDIC Power Holdings Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '600886.SH'},
            '000027': {'cn_name': '深圳能源', 'en_name': 'Shenzhen Energy Group Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '000027.SZ'},
            '600795': {'cn_name': '国电电力', 'en_name': 'GD Power Development Co.,Ltd.', 'market': 'A', 'sector': '电力', 'api_symbol': '600795.SH'},
            '600027': {'cn_name': '华电国际', 'en_name': 'Huadian Power International Corporation Limited', 'market': 'A', 'sector': '电力', 'api_symbol': '600027.SH'},
            
            # 农业食品
            '000876': {'cn_name': '新希望', 'en_name': 'New Hope Liuhe Co.,Ltd.', 'market': 'A', 'sector': '农业', 'api_symbol': '000876.SZ'},
            '600887': {'cn_name': '伊利股份', 'en_name': 'Inner Mongolia Yili Industrial Group Co.,Ltd.', 'market': 'A', 'sector': '食品饮料', 'api_symbol': '600887.SH'},
            '000895': {'cn_name': '双汇发展', 'en_name': 'Henan Shuanghui Investment & Development Co.,Ltd.', 'market': 'A', 'sector': '食品加工', 'api_symbol': '000895.SZ'},
            '600597': {'cn_name': '光明乳业', 'en_name': 'Bright Dairy & Food Co.,Ltd.', 'market': 'A', 'sector': '食品饮料', 'api_symbol': '600597.SH'},
            '002304': {'cn_name': '洋河股份', 'en_name': 'Yanghe Distillery Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '002304.SZ'},
            '600519': {'cn_name': '贵州茅台', 'en_name': 'Kweichow Moutai Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '600519.SH'},
            '000858': {'cn_name': '五粮液', 'en_name': 'Wuliangye Yibin Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '000858.SZ'},
            '000568': {'cn_name': '泸州老窖', 'en_name': 'Luzhou Laojiao Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '000568.SZ'},
            '000596': {'cn_name': '古井贡酒', 'en_name': 'Anhui Gujing Distillery Company Limited', 'market': 'A', 'sector': '白酒', 'api_symbol': '000596.SZ'},
            '600809': {'cn_name': '山西汾酒', 'en_name': 'Shanxi Xinghuacun Fen Wine Factory Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '600809.SH'},
            '000799': {'cn_name': '酒鬼酒', 'en_name': 'Jiugui Liquor Co.,Ltd.', 'market': 'A', 'sector': '白酒', 'api_symbol': '000799.SZ'},
        }
        
        # 港股 - 主要股票
        hk_stocks = {
            # 科技互联网
            '00700': {'cn_name': '腾讯控股', 'en_name': 'Tencent Holdings Limited', 'market': 'HK', 'sector': '互联网', 'api_symbol': '0700.HK'},
            '09988': {'cn_name': '阿里巴巴-SW', 'en_name': 'Alibaba Group Holding Limited', 'market': 'HK', 'sector': '电商', 'api_symbol': '9988.HK'},
            '03690': {'cn_name': '美团-W', 'en_name': 'Meituan', 'market': 'HK', 'sector': '生活服务', 'api_symbol': '3690.HK'},
            '01024': {'cn_name': '快手-W', 'en_name': 'Kuaishou Technology', 'market': 'HK', 'sector': '短视频', 'api_symbol': '1024.HK'},
            '09618': {'cn_name': '京东集团-SW', 'en_name': 'JD.com, Inc.', 'market': 'HK', 'sector': '电商', 'api_symbol': '9618.HK'},
            '09888': {'cn_name': '百度集团-SW', 'en_name': 'Baidu, Inc.', 'market': 'HK', 'sector': '互联网', 'api_symbol': '9888.HK'},
            '02020': {'cn_name': '安踏体育', 'en_name': 'ANTA Sports Products Limited', 'market': 'HK', 'sector': '体育用品', 'api_symbol': '2020.HK'},
            '02318': {'cn_name': '中国平安', 'en_name': 'Ping An Insurance (Group) Company of China, Ltd.', 'market': 'HK', 'sector': '保险', 'api_symbol': '2318.HK'},
            '00788': {'cn_name': '中国铁塔', 'en_name': 'China Tower Corporation Limited', 'market': 'HK', 'sector': '通信', 'api_symbol': '0788.HK'},
            '00941': {'cn_name': '中国移动', 'en_name': 'China Mobile Limited', 'market': 'HK', 'sector': '通信', 'api_symbol': '0941.HK'},
            '00762': {'cn_name': '中国联通', 'en_name': 'China Unicom (Hong Kong) Limited', 'market': 'HK', 'sector': '通信', 'api_symbol': '0762.HK'},
            '00728': {'cn_name': '中国电信', 'en_name': 'China Telecom Corporation Limited', 'market': 'HK', 'sector': '通信', 'api_symbol': '0728.HK'},
            
            # 金融保险
            '00388': {'cn_name': '香港交易所', 'en_name': 'Hong Kong Exchanges and Clearing Limited', 'market': 'HK', 'sector': '金融', 'api_symbol': '0388.HK'},
            '01299': {'cn_name': '友邦保险', 'en_name': 'AIA Group Limited', 'market': 'HK', 'sector': '保险', 'api_symbol': '1299.HK'},
            '01398': {'cn_name': '工商银行', 'en_name': 'Industrial and Commercial Bank of China Limited', 'market': 'HK', 'sector': '银行', 'api_symbol': '1398.HK'},
            '03988': {'cn_name': '中国银行', 'en_name': 'Bank of China Limited', 'market': 'HK', 'sector': '银行', 'api_symbol': '3988.HK'},
            '00939': {'cn_name': '建设银行', 'en_name': 'China Construction Bank Corporation', 'market': 'HK', 'sector': '银行', 'api_symbol': '0939.HK'},
            '00005': {'cn_name': '汇丰控股', 'en_name': 'HSBC Holdings plc', 'market': 'HK', 'sector': '银行', 'api_symbol': '0005.HK'},
            '00011': {'cn_name': '恒生银行', 'en_name': 'Hang Seng Bank Limited', 'market': 'HK', 'sector': '银行', 'api_symbol': '0011.HK'},
            '03968': {'cn_name': '招商银行', 'en_name': 'China Merchants Bank Co.,Ltd.', 'market': 'HK', 'sector': '银行', 'api_symbol': '3968.HK'},
            '01288': {'cn_name': '农业银行', 'en_name': 'Agricultural Bank of China Limited', 'market': 'HK', 'sector': '银行', 'api_symbol': '1288.HK'},
            '01988': {'cn_name': '民生银行', 'en_name': 'China Minsheng Banking Corp.,Ltd.', 'market': 'HK', 'sector': '银行', 'api_symbol': '1988.HK'},
            '03328': {'cn_name': '交通银行', 'en_name': 'Bank of Communications Co.,Ltd.', 'market': 'HK', 'sector': '银行', 'api_symbol': '3328.HK'},
            
            # 能源化工
            '00386': {'cn_name': '中国石油化工', 'en_name': 'China Petroleum & Chemical Corporation', 'market': 'HK', 'sector': '石油化工', 'api_symbol': '0386.HK'},
            '00857': {'cn_name': '中国石油股份', 'en_name': 'PetroChina Company Limited', 'market': 'HK', 'sector': '石油', 'api_symbol': '0857.HK'},
            '01088': {'cn_name': '中国神华', 'en_name': 'China Shenhua Energy Company Limited', 'market': 'HK', 'sector': '煤炭', 'api_symbol': '1088.HK'},
            '01171': {'cn_name': '兖州煤业股份', 'en_name': 'Yanzhou Coal Mining Company Limited', 'market': 'HK', 'sector': '煤炭', 'api_symbol': '1171.HK'},
            '00390': {'cn_name': '中国中铁', 'en_name': 'China Railway Group Limited', 'market': 'HK', 'sector': '建筑', 'api_symbol': '0390.HK'},
            
            # 房地产
            '01109': {'cn_name': '华润置地', 'en_name': 'China Resources Land Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '1109.HK'},
            '01997': {'cn_name': '九龙仓置业', 'en_name': 'Wharf Real Estate Investment Company Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '1997.HK'},
            '00016': {'cn_name': '新鸿基地产', 'en_name': 'Sun Hung Kai Properties Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '0016.HK'},
            '00017': {'cn_name': '新世界发展', 'en_name': 'New World Development Company Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '0017.HK'},
            '00083': {'cn_name': '信和置业', 'en_name': 'Sino Land Company Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '0083.HK'},
            '00101': {'cn_name': '恒隆地产', 'en_name': 'Hang Lung Properties Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '0101.HK'},
            '01113': {'cn_name': '长实集团', 'en_name': 'CK Hutchison Holdings Limited', 'market': 'HK', 'sector': '综合企业', 'api_symbol': '1113.HK'},
            '00001': {'cn_name': '长江和记实业', 'en_name': 'CK Hutchison Holdings Limited', 'market': 'HK', 'sector': '综合企业', 'api_symbol': '0001.HK'},
            
            # 消费零售
            '02331': {'cn_name': '李宁', 'en_name': 'Li Ning Company Limited', 'market': 'HK', 'sector': '体育用品', 'api_symbol': '2331.HK'},
            
            # 医疗健康
            '02269': {'cn_name': '药明生物', 'en_name': 'WuXi Biologics (Cayman) Inc.', 'market': 'HK', 'sector': '生物医药', 'api_symbol': '2269.HK'},
            '01099': {'cn_name': '国药控股', 'en_name': 'Sinopharm Group Co.,Ltd.', 'market': 'HK', 'sector': '医药', 'api_symbol': '1099.HK'},
            '01877': {'cn_name': '君实生物', 'en_name': 'Shanghai Junshi Biosciences Co.,Ltd.', 'market': 'HK', 'sector': '生物医药', 'api_symbol': '1877.HK'},
            '06160': {'cn_name': '百济神州', 'en_name': 'BeiGene, Ltd.', 'market': 'HK', 'sector': '生物医药', 'api_symbol': '6160.HK'},
            '01548': {'cn_name': '金斯瑞生物科技', 'en_name': 'GenScript Biotech Corporation', 'market': 'HK', 'sector': '生物医药', 'api_symbol': '1548.HK'},
            
            # 汽车制造
            '01211': {'cn_name': '比亚迪股份', 'en_name': 'BYD Company Limited', 'market': 'HK', 'sector': '新能源汽车', 'api_symbol': '1211.HK'},
            '00175': {'cn_name': '吉利汽车', 'en_name': 'Geely Automobile Holdings Limited', 'market': 'HK', 'sector': '汽车', 'api_symbol': '0175.HK'},
            '02333': {'cn_name': '长城汽车', 'en_name': 'Great Wall Motor Company Limited', 'market': 'HK', 'sector': '汽车', 'api_symbol': '2333.HK'},
            '00489': {'cn_name': '东风集团股份', 'en_name': 'Dongfeng Motor Group Company Limited', 'market': 'HK', 'sector': '汽车', 'api_symbol': '0489.HK'},
            
            # 公用事业
            '00002': {'cn_name': '中电控股', 'en_name': 'CLP Holdings Limited', 'market': 'HK', 'sector': '电力', 'api_symbol': '0002.HK'},
            '00003': {'cn_name': '香港中华煤气', 'en_name': 'The Hongkong and China Gas Company Limited', 'market': 'HK', 'sector': '公用事业', 'api_symbol': '0003.HK'},
            '00006': {'cn_name': '电能实业', 'en_name': 'Power Assets Holdings Limited', 'market': 'HK', 'sector': '电力', 'api_symbol': '0006.HK'},
            '00066': {'cn_name': '港铁公司', 'en_name': 'MTR Corporation Limited', 'market': 'HK', 'sector': '交通运输', 'api_symbol': '0066.HK'},
            
            # 其他行业
            '00027': {'cn_name': '银河娱乐', 'en_name': 'Galaxy Entertainment Group Limited', 'market': 'HK', 'sector': '博彩', 'api_symbol': '0027.HK'},
            '00188': {'cn_name': '金沙中国', 'en_name': 'Sands China Ltd.', 'market': 'HK', 'sector': '博彩', 'api_symbol': '0188.HK'},
            '00012': {'cn_name': '恒基地产', 'en_name': 'Henderson Land Development Company Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '0012.HK'},
            '00004': {'cn_name': '九龙仓集团', 'en_name': 'The Wharf (Holdings) Limited', 'market': 'HK', 'sector': '房地产', 'api_symbol': '0004.HK'},
        }
        
        # 合并A股和港股数据
        self.stocks.update(a_tech_stocks)
        self.stocks.update(a_traditional_stocks)
        self.stocks.update(hk_stocks)
    
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
            'A': {'count': 0, 'sectors': set()},
            'HK': {'count': 0, 'sectors': set()}
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
            
            # 分解为买入量和卖出量
            buy_ratio = 0.4 + np.random.random() * 0.2  # 40%-60%买入比例
            buy_volume = int(volume * buy_ratio)
            sell_volume = int(volume * (1 - buy_ratio))
            
            predictions.append({
                'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                'price': round(price, 4),
                'change_pct': round(((price - current_price) / current_price) * 100, 2),
                'buy_volume': buy_volume,
                'sell_volume': sell_volume
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
        
        # 初始化进程管理
        self.background_threads = []
        self.child_processes = []
        self.is_shutting_down = False
        
        # 初始化A股和汇率转换功能
        self.a_stock_fetcher = None
        self.cn_stock_fetcher = None
        self.currency_converter = None
        
        if A_STOCK_AVAILABLE:
            try:
                self.a_stock_fetcher = EnhancedAStockFetcher()
                self.cn_stock_fetcher = CNStockFetcher()
                self.currency_converter = CurrencyConverter()
                print("✅ A股和汇率转换功能已启用")
            except Exception as e:
                print(f"⚠️ A股功能初始化失败: {e}")
                # 如果初始化失败，将相关对象设为None，但不修改全局变量
                self.a_stock_fetcher = None
                self.cn_stock_fetcher = None
                self.currency_converter = None
        
        # 设置程序关闭时的清理
        self.setup_cleanup_handlers()
        
        self.setup_ui()
    
    def setup_cleanup_handlers(self):
        """设置程序关闭时的清理处理程序"""
        # 注册程序退出时的清理函数
        atexit.register(self.cleanup_on_exit)
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置信号处理（用于处理Ctrl+C等信号）
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self.signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """信号处理程序"""
        print(f"收到信号 {signum}，正在关闭程序...")
        self.cleanup_and_exit()
    
    def on_closing(self):
        """窗口关闭事件处理"""
        print("程序正在关闭...")
        self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """清理并退出程序"""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        print("开始清理资源...")
        
        # 清理后台线程
        self.cleanup_background_threads()
        
        # 清理子进程
        self.cleanup_child_processes()
        
        # 清理matplotlib资源
        self.cleanup_matplotlib()
        
        # 关闭主窗口
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
        print("程序已完全关闭")
        sys.exit(0)
    
    def cleanup_background_threads(self):
        """清理后台线程"""
        print("正在清理后台线程...")
        for thread in self.background_threads:
            if thread.is_alive():
                try:
                    # 注意：Python线程无法强制终止，只能等待其自然结束
                    # 这里我们只是标记线程应该停止
                    pass
                except:
                    pass
        self.background_threads.clear()
    
    def cleanup_child_processes(self):
        """清理子进程"""
        print("正在清理子进程...")
        for process in self.child_processes:
            try:
                if process.poll() is None:  # 进程仍在运行
                    process.terminate()
                    # 等待进程结束，最多等待5秒
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # 如果进程没有在5秒内结束，强制杀死
                        process.kill()
                        process.wait()
            except:
                pass
        self.child_processes.clear()
        
        # 额外清理：查找并关闭所有相关的Python进程
        self.cleanup_related_processes()
    
    def cleanup_related_processes(self):
        """清理相关进程"""
        try:
            current_pid = os.getpid()
            current_process = psutil.Process(current_pid)
            
            # 获取所有子进程
            children = current_process.children(recursive=True)
            
            for child in children:
                try:
                    if child.is_running():
                        print(f"正在关闭子进程: {child.pid} - {child.name()}")
                        child.terminate()
                        
                        # 等待进程结束
                        try:
                            child.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            # 强制杀死
                            child.kill()
                            child.wait()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
        except Exception as e:
            print(f"清理相关进程时出错: {e}")
    
    def cleanup_matplotlib(self):
        """清理matplotlib资源"""
        try:
            plt.close('all')
            # 清理matplotlib缓存
            import matplotlib
            matplotlib.pyplot.close('all')
        except:
            pass
    
    def cleanup_on_exit(self):
        """程序退出时的清理函数"""
        if not self.is_shutting_down:
            self.cleanup_and_exit()
    
    def add_background_thread(self, thread):
        """添加后台线程到管理列表"""
        self.background_threads.append(thread)
    
    def add_child_process(self, process):
        """添加子进程到管理列表"""
        self.child_processes.append(process)
    
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
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 美股与加密货币预测标签页
        us_stock_frame = ttk.Frame(notebook)
        notebook.add(us_stock_frame, text="📈 美股与加密货币预测")
        
        # A股与港股分析预测标签页
        if A_STOCK_AVAILABLE:
            a_stock_frame = ttk.Frame(notebook)
            notebook.add(a_stock_frame, text="🇨🇳 A股与港股分析预测")
        
        # 汇率转换标签页
        if A_STOCK_AVAILABLE:
            currency_frame = ttk.Frame(notebook)
            notebook.add(currency_frame, text="💱 汇率转换")
        
        # 设置美股预测标签页
        self.setup_us_stock_tab(us_stock_frame)
        
        # 设置A股分析标签页
        if A_STOCK_AVAILABLE:
            self.setup_a_stock_tab(a_stock_frame)
            self.setup_currency_tab(currency_frame)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪 - QuantPredict Pro")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              font=('SF Pro Text', 9), style='Subtitle.TLabel')
        status_bar.pack(fill=tk.X, pady=(15, 0))
    
    def setup_us_stock_tab(self, parent):
        """设置美股预测标签页"""
        # 分栏布局
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)
        
        # 右侧结果面板
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
    
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
        columns = ('日期', '预测价格', '价格区间', '涨跌幅', '买入量', '卖出量')
        self.tree = ttk.Treeview(data_frame, columns=columns, show='headings', 
                                height=15, style='iOS.Treeview')
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == '价格区间':
                self.tree.column(col, width=150, anchor=tk.CENTER)
            elif col in ['买入量', '卖出量']:
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
        
        thread = threading.Thread(target=get_price_thread, daemon=True)
        self.add_background_thread(thread)
        thread.start()
    
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
        
        thread = threading.Thread(target=predict_thread, daemon=True)
        self.add_background_thread(thread)
        thread.start()
    
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
            
            # 预测交易量（买入量和卖出量）
            pred_start = len(hist_dates)
            pred_dates = range(pred_start, pred_start + len(chart_data['predicted_volumes']))
            pred_volumes = chart_data['predicted_volumes']
            
            # 计算买入量和卖出量
            buy_volumes = []
            sell_volumes = []
            for vol in pred_volumes:
                buy_ratio = 0.4 + np.random.random() * 0.2  # 40%-60%买入比例
                buy_vol = int(vol * buy_ratio)
                sell_vol = int(vol * (1 - buy_ratio))
                buy_volumes.append(buy_vol)
                sell_volumes.append(sell_vol)
            
            # 绘制历史交易量柱状图
            self.volume_ax.bar(hist_dates, hist_volumes, color='skyblue', 
                              alpha=0.7, label='历史交易量', width=0.8)
            
            # 绘制预测买入量柱状图
            self.volume_ax.bar(pred_dates, buy_volumes, color='#34C759', 
                              alpha=0.8, label='预测买入量', width=0.35)
            
            # 绘制预测卖出量柱状图
            self.volume_ax.bar([x + 0.35 for x in pred_dates], sell_volumes, color='#FF3B30', 
                              alpha=0.8, label='预测卖出量', width=0.35)
            
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
                
                # 格式化买入量和卖出量
                buy_volume = pred.get('buy_volume', 0)
                sell_volume = pred.get('sell_volume', 0)
                
                buy_text = f"{buy_volume/1e3:.1f}K" if buy_volume >= 1e3 else f"{buy_volume:.0f}"
                sell_text = f"{sell_volume/1e3:.1f}K" if sell_volume >= 1e3 else f"{sell_volume:.0f}"
                
                self.tree.insert('', tk.END, values=(
                    pred['date'],
                    f"${pred['price']}",
                    price_range,
                    change_text,
                    buy_text,
                    sell_text
                ))
                
        except Exception as e:
            print(f"⚠️ 数据表格更新失败: {e}")
    
    def show_error(self, error_msg):
        """显示错误"""
        self.status_var.set(f"错误: {error_msg}")
        messagebox.showerror("错误", error_msg)
        self.predict_btn.config(state=tk.NORMAL)
    
    def setup_a_stock_tab(self, parent):
        """设置A股与港股分析预测标签页"""
        # 分栏布局
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)
        
        # 右侧结果面板
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        # 设置左侧面板
        self.setup_a_stock_left_panel(left_frame)
        
        # 设置右侧面板
        self.setup_a_stock_right_panel(right_frame)
    
    def setup_a_stock_left_panel(self, parent):
        """设置A股左侧控制面板"""
        # 搜索区域
        search_group = ttk.LabelFrame(parent, text="🔍 A股/港股搜索", padding=15)
        search_group.pack(fill=tk.X, padx=5, pady=5)
        
        # 搜索输入区域
        input_frame = ttk.Frame(search_group)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 搜索类型选择
        search_type_frame = ttk.Frame(input_frame)
        search_type_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_type_frame, text="搜索类型:").pack(side=tk.LEFT, padx=(0, 10))
        self.a_search_type_var = tk.StringVar(value="代码")
        search_type_combo = ttk.Combobox(search_type_frame, textvariable=self.a_search_type_var,
                                        values=["代码", "名称"], width=8, state="readonly")
        search_type_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # 搜索输入框
        search_input_frame = ttk.Frame(input_frame)
        search_input_frame.pack(fill=tk.X)
        
        ttk.Label(search_input_frame, text="搜索内容:").pack(side=tk.LEFT, padx=(0, 10))
        self.a_stock_symbol_var = tk.StringVar()
        self.a_stock_entry = ttk.Entry(search_input_frame, textvariable=self.a_stock_symbol_var, width=20)
        self.a_stock_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 搜索按钮
        self.a_search_btn = ttk.Button(search_input_frame, text="搜索", 
                                      command=self.search_a_stock)
        self.a_search_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # 预测按钮
        self.a_predict_btn = ttk.Button(search_input_frame, text="预测分析", 
                                       command=self.predict_a_stock, 
                                       style='Primary.TButton')
        self.a_predict_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 搜索结果区域
        results_group = ttk.LabelFrame(parent, text="📋 搜索结果", padding=15)
        results_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 搜索结果列表
        self.a_search_results = ttk.Treeview(results_group, columns=('代码', '名称', '市场', '行业'), 
                                           show='headings', height=8)
        self.a_search_results.heading('代码', text='股票代码')
        self.a_search_results.heading('名称', text='股票名称')
        self.a_search_results.heading('市场', text='市场')
        self.a_search_results.heading('行业', text='行业')
        
        self.a_search_results.column('代码', width=100)
        self.a_search_results.column('名称', width=200)
        self.a_search_results.column('市场', width=80)
        self.a_search_results.column('行业', width=120)
        
        # 滚动条
        search_scrollbar = ttk.Scrollbar(results_group, orient=tk.VERTICAL, command=self.a_search_results.yview)
        self.a_search_results.configure(yscrollcommand=search_scrollbar.set)
        
        self.a_search_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        search_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击选择
        self.a_search_results.bind('<Double-1>', self.on_a_stock_select)
        
        # 预设股票按钮
        preset_group = ttk.LabelFrame(parent, text="🔥 热门股票", padding=15)
        preset_group.pack(fill=tk.X, padx=5, pady=5)
        
        preset_frame = ttk.Frame(preset_group)
        preset_frame.pack(fill=tk.X)
        
        preset_stocks = [
            ('600519', '贵州茅台'),
            ('000858', '五粮液'),
            ('000001', '平安银行'),
            ('000002', '万科A'),
            ('600036', '招商银行'),
            ('601318', '中国平安')
        ]
        
        for i, (code, name) in enumerate(preset_stocks):
            btn = ttk.Button(preset_frame, text=f"{code}\n{name}", 
                           command=lambda c=code: self.select_a_stock_for_prediction(c),
                           width=12)
            btn.grid(row=0, column=i, padx=5)
        
        # 预测参数设置
        params_group = ttk.LabelFrame(parent, text="📊 预测参数", padding=15)
        params_group.pack(fill=tk.X, padx=5, pady=5)
        
        # 预测天数
        days_frame = ttk.Frame(params_group)
        days_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(days_frame, text="预测天数:").pack(side=tk.LEFT, padx=(0, 10))
        self.a_days_var = tk.StringVar(value="5")
        days_combo = ttk.Combobox(days_frame, textvariable=self.a_days_var, 
                                 values=["3", "5", "7", "10", "15", "30"], 
                                 width=10, state="readonly")
        days_combo.pack(side=tk.LEFT)
        
        # 预测方法
        method_frame = ttk.Frame(params_group)
        method_frame.pack(fill=tk.X)
        
        ttk.Label(method_frame, text="预测方法:").pack(side=tk.LEFT, padx=(0, 10))
        self.a_method_var = tk.StringVar(value="技术分析")
        method_combo = ttk.Combobox(method_frame, textvariable=self.a_method_var,
                                   values=["技术分析", "趋势分析", "综合预测"], 
                                   width=12, state="readonly")
        method_combo.pack(side=tk.LEFT)
    
    def setup_a_stock_right_panel(self, parent):
        """设置A股右侧结果面板 - 与美股界面保持一致"""
        # 结果显示
        result_group = ttk.LabelFrame(parent, text="📈 预测结果", padding=15)
        result_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建笔记本
        notebook = ttk.Notebook(result_group, style='iOS.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 摘要页面
        summary_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(summary_frame, text="📋 预测摘要")
        
        self.a_result_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, 
                                                     font=('SF Pro Text', 10),
                                                     bg='#ffffff', fg='#000000',
                                                     relief='flat', borderwidth=0)
        self.a_result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 价格图表页面
        price_chart_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(price_chart_frame, text="📈 价格走势图")
        
        # 创建价格图表
        self.a_price_fig, self.a_price_ax = plt.subplots(figsize=(8, 5), facecolor='#ffffff')
        self.a_price_canvas = FigureCanvasTkAgg(self.a_price_fig, price_chart_frame)
        self.a_price_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 交易量图表页面
        volume_chart_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(volume_chart_frame, text="📊 交易量图")
        
        # 创建交易量图表
        self.a_volume_fig, self.a_volume_ax = plt.subplots(figsize=(8, 4), facecolor='#ffffff')
        self.a_volume_canvas = FigureCanvasTkAgg(self.a_volume_fig, volume_chart_frame)
        self.a_volume_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 数据页面
        data_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(data_frame, text="📊 详细数据")
        
        # 数据表格
        columns = ('日期', '预测价格', '价格区间', '涨跌幅', '买入量', '卖出量')
        self.a_tree = ttk.Treeview(data_frame, columns=columns, show='headings', 
                                  height=15, style='iOS.Treeview')
        
        for col in columns:
            self.a_tree.heading(col, text=col)
            if col == '价格区间':
                self.a_tree.column(col, width=200)
            elif col in ['买入量', '卖出量']:
                self.a_tree.column(col, width=120)
            else:
                self.a_tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.a_tree.yview)
        self.a_tree.configure(yscrollcommand=scrollbar.set)
        
        self.a_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def setup_currency_tab(self, parent):
        """设置多货币汇率转换标签页"""
        # 主框架
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="💱 多货币汇率转换", 
                               font=('SF Pro Display', 20, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 货币选择区域
        currency_frame = ttk.LabelFrame(main_frame, text="货币选择", padding="15")
        currency_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 源货币选择
        from_frame = ttk.Frame(currency_frame)
        from_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(from_frame, text="源货币:", font=('SF Pro Text', 12)).pack(side=tk.LEFT, padx=(0, 10))
        self.from_currency_var = tk.StringVar(value="USD")
        from_currency_combo = ttk.Combobox(from_frame, textvariable=self.from_currency_var, 
                                          values=list(self.currency_converter.supported_currencies.keys()),
                                          width=10, state="readonly")
        from_currency_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # 目标货币选择
        ttk.Label(from_frame, text="目标货币:", font=('SF Pro Text', 12)).pack(side=tk.LEFT, padx=(0, 10))
        self.to_currency_var = tk.StringVar(value="CNY")
        to_currency_combo = ttk.Combobox(from_frame, textvariable=self.to_currency_var, 
                                        values=list(self.currency_converter.supported_currencies.keys()),
                                        width=10, state="readonly")
        to_currency_combo.pack(side=tk.LEFT)
        
        # 绑定货币选择变化事件
        from_currency_combo.bind('<<ComboboxSelected>>', self.on_currency_change)
        to_currency_combo.bind('<<ComboboxSelected>>', self.on_currency_change)
        
        # 汇率信息区域
        rate_frame = ttk.LabelFrame(main_frame, text="当前汇率", padding="15")
        rate_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 汇率显示
        self.rate_label = ttk.Label(rate_frame, text="正在获取汇率...", 
                                  font=('SF Pro Text', 16))
        self.rate_label.pack(pady=(0, 10))
        
        # 刷新按钮
        refresh_btn = ttk.Button(rate_frame, text="🔄 刷新汇率", command=self.refresh_exchange_rate)
        refresh_btn.pack()
        
        # 转换区域
        convert_frame = ttk.LabelFrame(main_frame, text="货币转换", padding="15")
        convert_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 双向转换输入框
        input_frame = ttk.Frame(convert_frame)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 源货币输入
        source_frame = ttk.Frame(input_frame)
        source_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        source_label = ttk.Label(source_frame, text="", font=('SF Pro Text', 12, 'bold'))
        source_label.pack(anchor=tk.W)
        self.source_currency_label = source_label
        
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(source_frame, textvariable=self.amount_var, 
                                     font=('SF Pro Text', 14), width=20)
        self.amount_entry.pack(fill=tk.X, pady=(5, 0))
        self.amount_entry.bind('<KeyRelease>', self.on_amount_change)
        
        # 转换按钮
        convert_btn = ttk.Button(input_frame, text="🔄 转换", command=self.convert_currency,
                                style='Primary.TButton')
        convert_btn.pack(side=tk.LEFT, padx=(20, 0))
        
        # 目标货币显示
        target_frame = ttk.Frame(input_frame)
        target_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        target_label = ttk.Label(target_frame, text="", font=('SF Pro Text', 12, 'bold'))
        target_label.pack(anchor=tk.W)
        self.target_currency_label = target_label
        
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(target_frame, textvariable=self.result_var, 
                                     font=('SF Pro Text', 14), width=20, state="readonly")
        self.result_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 反向转换按钮
        reverse_btn = ttk.Button(convert_frame, text="🔄 反向转换", command=self.reverse_currency)
        reverse_btn.pack(pady=(10, 0))
        
        # 初始化
        self.update_currency_labels()
        self.refresh_exchange_rate()
    
    def update_currency_labels(self):
        """更新货币标签显示"""
        from_currency = self.from_currency_var.get()
        to_currency = self.to_currency_var.get()
        
        from_info = self.currency_converter.supported_currencies.get(from_currency, {})
        to_info = self.currency_converter.supported_currencies.get(to_currency, {})
        
        from_text = f"{from_info.get('flag', '')} {from_info.get('name', from_currency)} ({from_info.get('symbol', from_currency)})"
        to_text = f"{to_info.get('flag', '')} {to_info.get('name', to_currency)} ({to_info.get('symbol', to_currency)})"
        
        self.source_currency_label.config(text=from_text)
        self.target_currency_label.config(text=to_text)
    
    def on_currency_change(self, event=None):
        """货币选择变化事件"""
        self.update_currency_labels()
        self.refresh_exchange_rate()
        self.amount_var.set("")
        self.result_var.set("")
    
    def on_amount_change(self, event=None):
        """金额输入变化事件"""
        # 实时转换
        self.convert_currency()
    
    def convert_currency(self):
        """执行货币转换"""
        try:
            amount_str = self.amount_var.get().strip()
            if not amount_str:
                self.result_var.set("")
                return
            
            amount = float(amount_str)
            from_currency = self.from_currency_var.get()
            to_currency = self.to_currency_var.get()
            
            if from_currency == to_currency:
                self.result_var.set(f"{amount:.2f}")
                return
            
            converted_amount, rate_data = self.currency_converter.convert_currency(
                amount, from_currency, to_currency
            )
            
            self.result_var.set(f"{converted_amount:.2f}")
            
        except ValueError:
            self.result_var.set("请输入有效数字")
        except Exception as e:
            self.result_var.set(f"转换失败: {str(e)}")
    
    def reverse_currency(self):
        """反向转换货币"""
        from_currency = self.from_currency_var.get()
        to_currency = self.to_currency_var.get()
        
        # 交换货币
        self.from_currency_var.set(to_currency)
        self.to_currency_var.set(from_currency)
        
        # 更新标签
        self.update_currency_labels()
        
        # 交换金额
        amount = self.amount_var.get()
        result = self.result_var.get()
        
        if amount and result:
            self.amount_var.set(result)
            self.result_var.set(amount)
        
        # 刷新汇率
        self.refresh_exchange_rate()
    
    def search_a_stock(self):
        """搜索A股/港股"""
        search_text = self.a_stock_symbol_var.get().strip()
        search_type = self.a_search_type_var.get()
        
        if not search_text:
            messagebox.showwarning("警告", "请输入搜索内容")
            return
        
        if not A_STOCK_AVAILABLE or not self.cn_stock_fetcher:
            messagebox.showerror("错误", "A股功能不可用")
            return
        
        try:
            # 清空搜索结果
            for item in self.a_search_results.get_children():
                self.a_search_results.delete(item)
            
            # 在后台线程中执行搜索
            thread = threading.Thread(target=self._search_a_stock_worker, 
                                    args=(search_text, search_type), daemon=True)
            self.add_background_thread(thread)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"搜索失败: {str(e)}")
    
    def _search_a_stock_worker(self, search_text, search_type):
        """A股搜索工作线程"""
        try:
            # 模拟搜索A股和港股数据
            search_results = self._get_stock_search_results(search_text, search_type)
            
            # 更新UI
            self.root.after(0, lambda: self.update_a_search_results(search_results))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_a_stock_error(f"搜索失败: {str(e)}"))
    
    def _get_stock_search_results(self, search_text, search_type):
        """获取股票搜索结果"""
        results = []
        
        # 使用AStockDatabase进行搜索
        if not hasattr(self, 'a_stock_database'):
            self.a_stock_database = AStockDatabase()
        
        search_results = self.a_stock_database.search(search_text)
        
        for stock in search_results:
            market_name = 'A股' if stock['market'] == 'A' else '港股'
            results.append({
                'code': stock['symbol'],
                'name': stock['cn_name'],
                'market': market_name,
                'sector': stock.get('sector', ''),
                'api_symbol': stock.get('api_symbol', stock['symbol'])
            })
        
        # 限制结果数量
        return results[:20]
    
    def update_a_search_results(self, results):
        """更新A股搜索结果"""
        try:
            # 清空现有结果
            for item in self.a_search_results.get_children():
                self.a_search_results.delete(item)
            
            # 添加搜索结果
            for result in results:
                self.a_search_results.insert('', tk.END, values=(
                    result['code'],
                    result['name'],
                    result['market'],
                    result.get('sector', '')
                ))
            
            if not results:
                self.a_search_results.insert('', tk.END, values=(
                    '无结果', '未找到匹配的股票', '', ''
                ))
            
            self.status_var.set(f"搜索完成，找到 {len(results)} 个结果")
            
        except Exception as e:
            self.show_a_stock_error(f"更新搜索结果失败: {str(e)}")
    
    def on_a_stock_select(self, event):
        """选择A股股票"""
        selection = self.a_search_results.selection()
        if selection:
            item = self.a_search_results.item(selection[0])
            code = item['values'][0]
            if code != '无结果':
                self.a_stock_symbol_var.set(code)
                self.predict_a_stock()
    
    def select_a_stock_for_prediction(self, symbol):
        """选择A股进行预测"""
        self.a_stock_symbol_var.set(symbol)
        self.predict_a_stock()
    
    def predict_a_stock(self):
        """预测A股"""
        symbol = self.a_stock_symbol_var.get().strip()
        if not symbol:
            messagebox.showwarning("警告", "请输入股票代码")
            return
        
        if not A_STOCK_AVAILABLE or not self.a_stock_fetcher:
            messagebox.showerror("错误", "A股功能不可用")
            return
        
        try:
            # 禁用预测按钮
            self.a_predict_btn.config(state=tk.DISABLED)
            
            # 获取预测参数
            days = int(self.a_days_var.get())
            method = self.a_method_var.get()
            
            # 更新状态
            self.status_var.set(f"正在分析A股 {symbol}...")
            
            # 在后台线程中执行预测
            thread = threading.Thread(target=self._predict_a_stock_worker, 
                                    args=(symbol, days, method), daemon=True)
            self.add_background_thread(thread)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"预测失败: {str(e)}")
            self.a_predict_btn.config(state=tk.NORMAL)
    
    def _predict_a_stock_worker(self, symbol, days, method):
        """A股预测工作线程"""
        try:
            print(f"开始A股预测: {symbol}, 天数: {days}, 方法: {method}")
            
            # 获取历史数据
            print("正在获取历史数据...")
            historical_data = self.a_stock_fetcher.get_historical_data(symbol, 30)
            
            if historical_data is None or historical_data.empty:
                print("历史数据为空")
                self.root.after(0, lambda: self.show_a_stock_error("无法获取历史数据"))
                return
            
            print(f"获取到历史数据: {len(historical_data)} 行")
            print(f"数据列: {list(historical_data.columns)}")
            print(f"数据前5行:\n{historical_data.head()}")
            
            # 验证和清理数据
            print("开始清理数据...")
            cleaned_data = self._clean_stock_data(historical_data)
            print(f"数据清理完成: {len(cleaned_data)} 行")
            
            # 生成预测数据
            print("开始生成预测数据...")
            predictions = self._generate_a_stock_predictions(cleaned_data, days, method)
            print(f"预测数据生成完成: {len(predictions)} 条")
            
            # 更新UI
            self.root.after(0, lambda: self.update_a_stock_prediction_display(symbol, predictions))
            
        except Exception as e:
            print(f"A股预测错误: {str(e)}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self.show_a_stock_error(f"预测分析失败: {str(e)}"))
    
    def _clean_stock_data(self, data):
        """清理股票数据，移除NaN和inf值"""
        try:
            print(f"开始清理数据，原始数据形状: {data.shape}")
            print(f"原始数据列: {list(data.columns)}")
            
            if not isinstance(data, pd.DataFrame):
                raise ValueError("数据不是DataFrame格式")
            
            # 创建数据副本
            cleaned_data = data.copy()
            
            # 清理close列
            if 'close' in cleaned_data.columns:
                print("清理close列...")
                print(f"close列原始统计: {cleaned_data['close'].describe()}")
                print(f"close列NaN数量: {cleaned_data['close'].isna().sum()}")
                print(f"close列inf数量: {np.isinf(cleaned_data['close']).sum()}")
                
                # 替换inf值为NaN
                cleaned_data['close'] = cleaned_data['close'].replace([np.inf, -np.inf], np.nan)
                # 前向填充，然后后向填充
                cleaned_data['close'] = cleaned_data['close'].fillna(method='ffill').fillna(method='bfill')
                # 如果还有NaN，用默认值填充
                if cleaned_data['close'].isna().any():
                    print("close列仍有NaN，使用默认值填充")
                    cleaned_data['close'] = cleaned_data['close'].fillna(100.0)
                # 确保所有值都是正数
                cleaned_data['close'] = cleaned_data['close'].abs()
                
                print(f"close列清理后统计: {cleaned_data['close'].describe()}")
            
            # 清理volume列
            if 'volume' in cleaned_data.columns:
                print("清理volume列...")
                print(f"volume列原始统计: {cleaned_data['volume'].describe()}")
                print(f"volume列NaN数量: {cleaned_data['volume'].isna().sum()}")
                print(f"volume列inf数量: {np.isinf(cleaned_data['volume']).sum()}")
                
                # 替换inf值为NaN
                cleaned_data['volume'] = cleaned_data['volume'].replace([np.inf, -np.inf], np.nan)
                # 前向填充，然后后向填充
                cleaned_data['volume'] = cleaned_data['volume'].fillna(method='ffill').fillna(method='bfill')
                # 如果还有NaN，用默认值填充
                if cleaned_data['volume'].isna().any():
                    print("volume列仍有NaN，使用默认值填充")
                    cleaned_data['volume'] = cleaned_data['volume'].fillna(1000000)
                # 确保所有值都是正数
                cleaned_data['volume'] = cleaned_data['volume'].abs()
                
                print(f"volume列清理后统计: {cleaned_data['volume'].describe()}")
            
            # 清理其他数值列
            for col in cleaned_data.columns:
                if cleaned_data[col].dtype in ['float64', 'int64']:
                    print(f"清理列 {col}...")
                    cleaned_data[col] = cleaned_data[col].replace([np.inf, -np.inf], np.nan)
                    cleaned_data[col] = cleaned_data[col].fillna(method='ffill').fillna(method='bfill')
                    if cleaned_data[col].isna().any():
                        cleaned_data[col] = cleaned_data[col].fillna(0)
            
            print("数据清理完成")
            return cleaned_data
            
        except Exception as e:
            print(f"数据清理失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回默认数据
            return pd.DataFrame({
                'close': [100.0] * 30,
                'volume': [1000000] * 30
            })
    
    def _generate_a_stock_predictions(self, data, days, method):
        """生成A股预测数据"""
        predictions = []
        
        print(f"开始生成预测，数据形状: {data.shape}")
        print(f"预测天数: {days}, 方法: {method}")
        
        # 数据已经在前面的_clean_stock_data方法中清理过了
        # 这里只需要基本验证
        try:
            if not isinstance(data, pd.DataFrame) or data.empty:
                raise ValueError("数据无效")
            
            if 'close' not in data.columns:
                raise ValueError("缺少close列")
            
        except Exception as e:
            print(f"数据验证失败: {e}")
            # 创建默认数据
            data = pd.DataFrame({
                'close': [100.0] * 30,
                'volume': [1000000] * 30
            })
        
        # 获取最新价格
        latest_price = float(data['close'].iloc[-1])
        print(f"最新价格: {latest_price}")
        
        # 计算技术指标，处理NaN值
        try:
            sma_5 = data['close'].rolling(window=5).mean().iloc[-1]
            if pd.isna(sma_5) or np.isinf(sma_5):
                sma_5 = latest_price
        except:
            sma_5 = latest_price
        
        try:
            sma_20 = data['close'].rolling(window=20).mean().iloc[-1]
            if pd.isna(sma_20) or np.isinf(sma_20):
                sma_20 = latest_price
        except:
            sma_20 = latest_price
        
        # 计算波动率，处理NaN值
        try:
            returns = data['close'].pct_change().dropna()
            if len(returns) > 0:
                volatility = returns.std() * np.sqrt(252)  # 年化波动率
                if pd.isna(volatility) or np.isinf(volatility) or volatility <= 0:
                    volatility = 0.2  # 默认20%波动率
            else:
                volatility = 0.2  # 默认20%波动率
        except:
            volatility = 0.2  # 默认20%波动率
        
        # 生成预测
        for i in range(1, days + 1):
            try:
                # 基于技术分析的简单预测
                if method == "技术分析":
                    trend_factor = 0
                    if sma_20 != 0 and not pd.isna(sma_20) and not np.isinf(sma_20):
                        trend_factor = (sma_5 - sma_20) / sma_20
                        if pd.isna(trend_factor) or np.isinf(trend_factor):
                            trend_factor = 0
                    price_change = trend_factor * 0.1 + np.random.normal(0, volatility * 0.1)
                elif method == "趋势分析":
                    recent_trend = 0
                    if len(data) >= 5:
                        try:
                            recent_price = data['close'].iloc[-1]
                            old_price = data['close'].iloc[-5]
                            if not pd.isna(recent_price) and not np.isinf(recent_price) and not pd.isna(old_price) and not np.isinf(old_price) and old_price != 0:
                                recent_trend = (recent_price - old_price) / old_price
                                if pd.isna(recent_trend) or np.isinf(recent_trend):
                                    recent_trend = 0
                        except:
                            recent_trend = 0
                    price_change = recent_trend * 0.8 + np.random.normal(0, volatility * 0.05)
                else:  # 综合预测
                    trend_factor = 0
                    if sma_20 != 0 and not pd.isna(sma_20) and not np.isinf(sma_20):
                        trend_factor = (sma_5 - sma_20) / sma_20
                        if pd.isna(trend_factor) or np.isinf(trend_factor):
                            trend_factor = 0
                    
                    recent_trend = 0
                    if len(data) >= 5:
                        try:
                            recent_price = data['close'].iloc[-1]
                            old_price = data['close'].iloc[-5]
                            if not pd.isna(recent_price) and not np.isinf(recent_price) and not pd.isna(old_price) and not np.isinf(old_price) and old_price != 0:
                                recent_trend = (recent_price - old_price) / old_price
                                if pd.isna(recent_trend) or np.isinf(recent_trend):
                                    recent_trend = 0
                        except:
                            recent_trend = 0
                    
                    price_change = (trend_factor + recent_trend) * 0.3 + np.random.normal(0, volatility * 0.08)
                
                # 确保价格变化在合理范围内
                if pd.isna(price_change) or np.isinf(price_change):
                    price_change = np.random.normal(0, 0.02)
                price_change = max(-0.1, min(0.1, price_change))  # 限制在±10%以内
                
                predicted_price = latest_price * (1 + price_change)
                
                # 确保预测价格为正数
                if predicted_price <= 0 or pd.isna(predicted_price) or np.isinf(predicted_price):
                    predicted_price = latest_price * (1 + np.random.normal(0, 0.02))
                    if predicted_price <= 0:
                        predicted_price = latest_price
                
            except Exception as e:
                print(f"预测计算错误 (第{i}天): {e}")
                # 使用默认值
                price_change = np.random.normal(0, 0.02)
                predicted_price = latest_price * (1 + price_change)
                if predicted_price <= 0:
                    predicted_price = latest_price
            
            # 计算价格区间
            price_range = f"¥{predicted_price * 0.95:.2f} - ¥{predicted_price * 1.05:.2f}"
            
            # 计算涨跌幅
            change_pct = price_change * 100
            
            # 生成交易量分解（买入量和卖出量）
            try:
                print(f"计算第{i}天交易量...")
                
                # 安全获取基础交易量
                if 'volume' in data.columns and not data['volume'].empty:
                    base_volume = data['volume'].iloc[-1]
                    print(f"原始base_volume: {base_volume}, 类型: {type(base_volume)}")
                    
                    # 清理基础交易量
                    if pd.isna(base_volume) or np.isinf(base_volume) or base_volume <= 0:
                        print("base_volume无效，使用默认值")
                        base_volume = 1000000.0
                    else:
                        base_volume = float(base_volume)
                        if base_volume <= 0:
                            print("base_volume <= 0，使用默认值")
                            base_volume = 1000000.0
                else:
                    print("没有volume列或为空，使用默认值")
                    base_volume = 1000000.0
                
                # 确保base_volume是有效的正数
                if pd.isna(base_volume) or np.isinf(base_volume) or base_volume <= 0:
                    print("base_volume最终检查失败，使用默认值")
                    base_volume = 1000000.0
                
                print(f"最终base_volume: {base_volume}")
                
                # 计算买入量和卖出量比例
                buy_ratio = 0.4 + np.random.random() * 0.2  # 0.4-0.6
                sell_ratio = 0.4 + np.random.random() * 0.2  # 0.4-0.6
                
                print(f"buy_ratio: {buy_ratio}, sell_ratio: {sell_ratio}")
                
                # 确保比例有效
                if pd.isna(buy_ratio) or np.isinf(buy_ratio):
                    print("buy_ratio无效，使用默认值")
                    buy_ratio = 0.5
                if pd.isna(sell_ratio) or np.isinf(sell_ratio):
                    print("sell_ratio无效，使用默认值")
                    sell_ratio = 0.5
                
                # 计算原始交易量
                buy_volume_raw = base_volume * buy_ratio
                sell_volume_raw = base_volume * sell_ratio
                
                print(f"buy_volume_raw: {buy_volume_raw}, sell_volume_raw: {sell_volume_raw}")
                
                # 确保计算结果有效
                if pd.isna(buy_volume_raw) or np.isinf(buy_volume_raw) or buy_volume_raw < 0:
                    print("buy_volume_raw无效，使用默认值")
                    buy_volume_raw = base_volume * 0.5
                if pd.isna(sell_volume_raw) or np.isinf(sell_volume_raw) or sell_volume_raw < 0:
                    print("sell_volume_raw无效，使用默认值")
                    sell_volume_raw = base_volume * 0.5
                
                print(f"修正后 buy_volume_raw: {buy_volume_raw}, sell_volume_raw: {sell_volume_raw}")
                
                # 转换为整数，确保为正数
                buy_volume = max(0, int(buy_volume_raw))
                sell_volume = max(0, int(sell_volume_raw))
                
                print(f"最终 buy_volume: {buy_volume}, sell_volume: {sell_volume}")
                
            except Exception as e:
                print(f"交易量计算错误 (第{i}天): {e}")
                import traceback
                traceback.print_exc()
                # 使用默认值
                buy_volume = 500000
                sell_volume = 500000
            
            predictions.append({
                'date': f"第{i}天",
                'price': predicted_price,
                'price_range': price_range,
                'change_pct': change_pct,
                'buy_volume': buy_volume,
                'sell_volume': sell_volume
            })
            
            # 更新最新价格用于下一次预测
            latest_price = predicted_price
        
        return predictions
    
    def update_a_stock_prediction_display(self, symbol, predictions):
        """更新A股预测显示 - 与美股界面保持一致"""
        try:
            # 更新预测摘要文本
            latest_pred = predictions[0]
            summary_text = f"""
📈 A股预测分析报告 - {symbol}
{'='*50}

🎯 预测概览:
• 当前预测价格: ¥{latest_pred['price']:.2f}
• 预期涨跌幅: {latest_pred['change_pct']:+.2f}%
• 价格区间: {latest_pred['price_range']}
• 预测天数: {len(predictions)}天

📊 预测详情:
"""
            
            for i, pred in enumerate(predictions, 1):
                summary_text += f"第{i}天: ¥{pred['price']:.2f} ({pred['change_pct']:+.2f}%) | 买入: {pred['buy_volume']:,} | 卖出: {pred['sell_volume']:,}\n"
            
            summary_text += f"""
💡 投资建议:
• 基于{len(predictions)}天技术分析预测
• 建议关注价格区间波动
• 注意风险控制，合理配置仓位

⚠️ 风险提示:
• 预测仅供参考，不构成投资建议
• 股市有风险，投资需谨慎
• 请结合基本面分析做出决策
"""
            
            self.a_result_text.delete(1.0, tk.END)
            self.a_result_text.insert(1.0, summary_text)
            
            # 更新数据表格
            for item in self.a_tree.get_children():
                self.a_tree.delete(item)
            
            for pred in predictions:
                change_text = f"{pred['change_pct']:+.2f}%"
                self.a_tree.insert('', tk.END, values=(
                    pred['date'],
                    f"¥{pred['price']:.2f}",
                    pred['price_range'],
                    change_text,
                    f"{pred['buy_volume']:,}",
                    f"{pred['sell_volume']:,}"
                ))
            
            # 生成并显示图表
            self.create_a_stock_charts(symbol, predictions)
            
            # 恢复按钮状态
            self.a_predict_btn.config(state=tk.NORMAL)
            self.status_var.set(f"A股 {symbol} 预测分析完成")
            
        except Exception as e:
            self.show_a_stock_error(f"更新显示失败: {str(e)}")
    
    def create_a_stock_charts(self, symbol, predictions):
        """创建A股图表 - 显示历史走势和预测走势"""
        try:
            # 获取历史数据
            historical_data = None
            if hasattr(self, 'a_stock_fetcher') and self.a_stock_fetcher:
                try:
                    historical_data = self.a_stock_fetcher.get_historical_data(symbol, 30)
                except:
                    historical_data = None
            
            # 价格走势图
            self.a_price_ax.clear()
            
            # 准备数据
            if historical_data is not None and not historical_data.empty and 'close' in historical_data.columns:
                # 有历史数据
                hist_days = list(range(-len(historical_data), 0))  # 负数表示历史
                hist_prices = historical_data['close'].tolist()
                
                # 预测数据
                pred_days = list(range(1, len(predictions) + 1))
                pred_prices = [pred['price'] for pred in predictions]
                
                # 计算最高和最低预期价格
                max_prices = [pred['price'] * 1.05 for pred in predictions]  # 最高预期价格
                min_prices = [pred['price'] * 0.95 for pred in predictions]  # 最低预期价格
                
                # 绘制历史数据
                self.a_price_ax.plot(hist_days, hist_prices, 'g-', linewidth=2, 
                                   label='历史走势', alpha=0.8)
                
                # 绘制预测数据
                self.a_price_ax.plot(pred_days, pred_prices, 'b-', linewidth=2, marker='o', 
                                   markersize=4, label='预测走势')
                
                # 绘制最高/最低预期价格虚线
                self.a_price_ax.plot(pred_days, max_prices, 'r--', linewidth=1.5, 
                                   alpha=0.7, label='最高预期价格')
                self.a_price_ax.plot(pred_days, min_prices, 'r--', linewidth=1.5, 
                                   alpha=0.7, label='最低预期价格')
                
                # 添加分界线
                self.a_price_ax.axvline(x=0, color='gray', linestyle=':', alpha=0.5)
                self.a_price_ax.text(0.5, 0.95, '预测开始', transform=self.a_price_ax.transAxes, 
                                  ha='center', va='top', fontsize=10, alpha=0.7)
                
                # 设置标题和标签
                self.a_price_ax.set_title(f"{symbol} 价格走势分析", fontsize=14, fontweight='bold')
                self.a_price_ax.set_xlabel('时间 (历史 → 预测)')
                self.a_price_ax.set_ylabel('价格 (¥)')
                
                # 设置x轴标签
                all_days = hist_days + pred_days
                self.a_price_ax.set_xticks(range(min(all_days), max(all_days) + 1, 5))
                
            else:
                # 没有历史数据，只显示预测
                days = list(range(1, len(predictions) + 1))
                prices = [pred['price'] for pred in predictions]
                max_prices = [pred['price'] * 1.05 for pred in predictions]
                min_prices = [pred['price'] * 0.95 for pred in predictions]
                
                self.a_price_ax.plot(days, prices, 'b-', linewidth=2, marker='o', 
                                   markersize=6, label='预测走势')
                self.a_price_ax.plot(days, max_prices, 'r--', linewidth=1.5, 
                                   alpha=0.7, label='最高预期价格')
                self.a_price_ax.plot(days, min_prices, 'r--', linewidth=1.5, 
                                   alpha=0.7, label='最低预期价格')
                
                self.a_price_ax.set_title(f"{symbol} 价格走势预测", fontsize=14, fontweight='bold')
                self.a_price_ax.set_xlabel('预测天数')
                self.a_price_ax.set_ylabel('价格 (¥)')
            
            # 添加图例和网格
            self.a_price_ax.legend(loc='upper left', fontsize=9)
            self.a_price_ax.grid(True, alpha=0.3)
            
            # 格式化价格标签
            def format_price(x, p):
                return f'¥{x:.2f}'
            
            from matplotlib.ticker import FuncFormatter
            self.a_price_ax.yaxis.set_major_formatter(FuncFormatter(format_price))
            
            self.a_price_fig.tight_layout()
            self.a_price_canvas.draw()
            
            # 交易量图表
            self.a_volume_ax.clear()
            buy_volumes = [pred['buy_volume'] for pred in predictions]
            sell_volumes = [pred['sell_volume'] for pred in predictions]
            
            x_pos = np.arange(len(days))
            width = 0.35
            
            self.a_volume_ax.bar(x_pos - width/2, buy_volumes, width, label='买入量', color='#34C759', alpha=0.8)
            self.a_volume_ax.bar(x_pos + width/2, sell_volumes, width, label='卖出量', color='#FF3B30', alpha=0.8)
            
            self.a_volume_ax.set_title(f"{symbol} 交易量预测", fontsize=14, fontweight='bold')
            self.a_volume_ax.set_xlabel('预测天数')
            self.a_volume_ax.set_ylabel('交易量')
            self.a_volume_ax.set_xticks(x_pos)
            self.a_volume_ax.set_xticklabels(days)
            self.a_volume_ax.legend()
            self.a_volume_ax.grid(True, alpha=0.3, axis='y')
            
            # 格式化交易量标签
            def format_volume(x, p):
                if x >= 1e9:
                    return f'{x/1e9:.1f}B'
                elif x >= 1e6:
                    return f'{x/1e6:.1f}M'
                elif x >= 1e3:
                    return f'{x/1e3:.1f}K'
                else:
                    return f'{x:.0f}'
            
            self.a_volume_ax.yaxis.set_major_formatter(FuncFormatter(format_volume))
            
            self.a_volume_fig.tight_layout()
            self.a_volume_canvas.draw()
            
        except Exception as e:
            print(f"⚠️ A股图表创建失败: {e}")
    
    def show_a_stock_error(self, error_msg):
        """显示A股错误"""
        self.a_predict_btn.config(state=tk.NORMAL)
        self.status_var.set(f"A股错误: {error_msg}")
        messagebox.showerror("A股预测错误", error_msg)
    
    def select_a_stock(self, symbol):
        """选择A股"""
        global A_STOCK_AVAILABLE
        if not A_STOCK_AVAILABLE or not self.a_stock_fetcher:
            messagebox.showerror("错误", "A股功能不可用")
            return
        
        try:
            # 获取实时数据
            data = self.a_stock_fetcher.get_real_time_price(symbol)
            
            if data and data.get('price', 0) > 0:
                self.update_a_stock_display(data)
            else:
                messagebox.showwarning("警告", f"无法获取股票 {symbol} 的数据")
                
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def update_a_stock_display(self, data):
        """更新A股数据显示"""
        # 更新价格标签
        price_text = f"💰 {data['symbol']} - ¥{data['price']:.2f}"
        if data.get('change', 0) != 0:
            change_pct = data.get('change_pct', 0)
            change_text = f" ({change_pct:+.2f}%)"
            price_text += change_text
        
        self.a_stock_price_label.config(text=price_text)
        
        # 更新表格
        for item in self.a_stock_tree.get_children():
            self.a_stock_tree.delete(item)
        
        # 添加数据行
        info_items = [
            ('股票代码', data['symbol']),
            ('当前价格', f"¥{data['price']:.2f}"),
            ('涨跌额', f"¥{data['change']:.2f}"),
            ('涨跌幅', f"{data['change_pct']:.2f}%"),
            ('成交量', f"{data['volume']:,.0f}"),
            ('成交额', f"¥{data['turnover']:,.0f}"),
            ('最高价', f"¥{data['high']:.2f}"),
            ('最低价', f"¥{data['low']:.2f}"),
            ('开盘价', f"¥{data['open']:.2f}"),
            ('买入量', f"{data['buy_volume']:,.0f}"),
            ('卖出量', f"{data['sell_volume']:,.0f}"),
            ('数据源', data['source']),
            ('更新时间', data['timestamp'])
        ]
        
        for item, value in info_items:
            self.a_stock_tree.insert('', tk.END, values=(item, value))
    
    def refresh_exchange_rate(self):
        """刷新汇率"""
        global A_STOCK_AVAILABLE
        if not A_STOCK_AVAILABLE or not self.currency_converter:
            self.rate_label.config(text="汇率功能不可用")
            return
        
        try:
            from_currency = self.from_currency_var.get()
            to_currency = self.to_currency_var.get()
            
            if from_currency == to_currency:
                self.rate_label.config(text="相同货币，汇率为 1.0000")
                return
            
            rate_info = self.currency_converter.get_exchange_rate(from_currency, to_currency)
            from_info = self.currency_converter.supported_currencies.get(from_currency, {})
            to_info = self.currency_converter.supported_currencies.get(to_currency, {})
            
            from_symbol = from_info.get('symbol', from_currency)
            to_symbol = to_info.get('symbol', to_currency)
            
            rate_text = f"💱 1 {from_symbol} = {rate_info['rate']:.4f} {to_symbol}"
            rate_text += f" (来源: {rate_info['source']})"
            self.rate_label.config(text=rate_text)
        except Exception as e:
            self.rate_label.config(text=f"获取汇率失败: {str(e)}")
    
    def convert_usd_to_cny(self):
        """美元转人民币"""
        global A_STOCK_AVAILABLE
        if not A_STOCK_AVAILABLE or not self.currency_converter:
            messagebox.showerror("错误", "汇率功能不可用")
            return
        
        try:
            usd_amount = float(self.usd_amount_var.get())
            cny_amount, rate_data = self.currency_converter.convert_usd_to_cny(usd_amount)
            result_text = f"${usd_amount:.2f} = ¥{cny_amount:.2f}"
            self.usd_result_label.config(text=result_text)
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
    
    def convert_cny_to_usd(self):
        """人民币转美元"""
        global A_STOCK_AVAILABLE
        if not A_STOCK_AVAILABLE or not self.currency_converter:
            messagebox.showerror("错误", "汇率功能不可用")
            return
        
        try:
            cny_amount = float(self.cny_amount_var.get())
            usd_amount, rate_data = self.currency_converter.convert_cny_to_usd(cny_amount)
            result_text = f"¥{cny_amount:.2f} = ${usd_amount:.2f}"
            self.cny_result_label.config(text=result_text)
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
    
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