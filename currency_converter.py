#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多货币实时汇率转换接口
支持多种货币之间的实时转换
"""

import requests
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import json

class CurrencyConverter:
    """多货币汇率转换器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 缓存配置
        self.cache = {}
        self.cache_duration = 60  # 1分钟缓存
        
        # 支持的货币列表
        self.supported_currencies = {
            'USD': {'name': '美元', 'symbol': '$', 'flag': '🇺🇸'},
            'CNY': {'name': '人民币', 'symbol': '¥', 'flag': '🇨🇳'},
            'EUR': {'name': '欧元', 'symbol': '€', 'flag': '🇪🇺'},
            'GBP': {'name': '英镑', 'symbol': '£', 'flag': '🇬🇧'},
            'JPY': {'name': '日元', 'symbol': '¥', 'flag': '🇯🇵'},
            'HKD': {'name': '港币', 'symbol': 'HK$', 'flag': '🇭🇰'},
            'SGD': {'name': '新加坡元', 'symbol': 'S$', 'flag': '🇸🇬'},
            'AUD': {'name': '澳元', 'symbol': 'A$', 'flag': '🇦🇺'},
            'CAD': {'name': '加元', 'symbol': 'C$', 'flag': '🇨🇦'},
            'CHF': {'name': '瑞士法郎', 'symbol': 'CHF', 'flag': '🇨🇭'},
            'KRW': {'name': '韩元', 'symbol': '₩', 'flag': '🇰🇷'},
            'THB': {'name': '泰铢', 'symbol': '฿', 'flag': '🇹🇭'},
            'INR': {'name': '印度卢比', 'symbol': '₹', 'flag': '🇮🇳'},
            'RUB': {'name': '俄罗斯卢布', 'symbol': '₽', 'flag': '🇷🇺'},
            'BRL': {'name': '巴西雷亚尔', 'symbol': 'R$', 'flag': '🇧🇷'},
        }
        
        # 数据源配置（去除exchangerate_api）
        self.data_sources = {
            'yahoo_finance': {
                'url': 'https://query1.finance.yahoo.com/v8/finance/chart/{pair}=X',
                'priority': 1,
                'description': 'Yahoo Finance'
            },
            'fixer_io': {
                'url': 'https://api.fixer.io/latest',
                'priority': 2,
                'description': 'Fixer.io',
                'api_key_required': True
            },
            'currencylayer': {
                'url': 'http://api.currencylayer.com/live',
                'priority': 3,
                'description': 'CurrencyLayer',
                'api_key_required': True
            }
        }
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict:
        """获取任意两种货币之间的汇率"""
        if from_currency == to_currency:
            return {
                'rate': 1.0,
                'source': 'same_currency',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        cache_key = f"{from_currency}_{to_currency}_rate"
        
        # 检查缓存
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # 尝试多个数据源
        for source_name, source_config in self.data_sources.items():
            try:
                if source_name == 'yahoo_finance':
                    data = self._get_yahoo_finance_rate(from_currency, to_currency)
                elif source_name == 'fixer_io':
                    data = self._get_fixer_io_rate(from_currency, to_currency)
                elif source_name == 'currencylayer':
                    data = self._get_currencylayer_rate(from_currency, to_currency)
                
                if data and data.get('rate', 0) > 0:
                    # 更新缓存
                    self.cache[cache_key] = {
                        'data': data,
                        'timestamp': time.time()
                    }
                    return data
                    
            except Exception as e:
                print(f"⚠️ {source_name} 汇率获取失败: {e}")
                continue
        
        # 所有数据源都失败，返回默认汇率
        print("⚠️ 所有汇率数据源失败，使用默认汇率")
        default_rate = self._get_default_rate(from_currency, to_currency)
        default_data = {
            'rate': default_rate,
            'source': 'default',
            'timestamp': datetime.now().isoformat(),
            'status': 'fallback'
        }
        
        self.cache[cache_key] = {
            'data': default_data,
            'timestamp': time.time()
        }
        return default_data
    
    def get_usd_cny_rate(self) -> Dict:
        """获取美元/人民币汇率（保持向后兼容）"""
        return self.get_exchange_rate('USD', 'CNY')
    
    def _get_yahoo_finance_rate(self, from_currency: str, to_currency: str) -> Dict:
        """从Yahoo Finance获取汇率"""
        pair = f"{from_currency}{to_currency}"
        url = self.data_sources['yahoo_finance']['url'].format(pair=pair)
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                rate = result['meta']['regularMarketPrice']
                return {
                    'rate': rate,
                    'source': 'yahoo_finance',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
        return None
    
    def _get_fixer_io_rate(self, from_currency: str, to_currency: str) -> Dict:
        """从Fixer.io获取汇率（需要API密钥）"""
        # 这里需要API密钥，暂时跳过
        return None
    
    def _get_currencylayer_rate(self, from_currency: str, to_currency: str) -> Dict:
        """从CurrencyLayer获取汇率（需要API密钥）"""
        # 这里需要API密钥，暂时跳过
        return None
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Tuple[float, Dict]:
        """通用货币转换"""
        if from_currency == to_currency:
            return amount, {'rate': 1.0, 'source': 'same_currency', 'status': 'success'}
        
        rate_data = self.get_exchange_rate(from_currency, to_currency)
        rate = rate_data['rate']
        converted_amount = amount * rate
        
        return converted_amount, rate_data
    
    def convert_usd_to_cny(self, usd_amount: float) -> Tuple[float, Dict]:
        """将美元转换为人民币（保持向后兼容）"""
        return self.convert_currency(usd_amount, 'USD', 'CNY')
    
    def convert_cny_to_usd(self, cny_amount: float) -> Tuple[float, Dict]:
        """将人民币转换为美元（保持向后兼容）"""
        return self.convert_currency(cny_amount, 'CNY', 'USD')
    
    def get_rate_info(self) -> Dict:
        """获取汇率信息（保持向后兼容）"""
        return self.get_usd_cny_rate()
    
    def get_supported_currencies(self) -> Dict:
        """获取支持的货币列表"""
        return self.supported_currencies
    
    def _get_default_rate(self, from_currency: str, to_currency: str) -> float:
        """获取默认汇率"""
        # 一些常用的默认汇率
        default_rates = {
            ('USD', 'CNY'): 7.25,
            ('CNY', 'USD'): 0.138,
            ('USD', 'EUR'): 0.85,
            ('EUR', 'USD'): 1.18,
            ('USD', 'GBP'): 0.73,
            ('GBP', 'USD'): 1.37,
            ('USD', 'JPY'): 110.0,
            ('JPY', 'USD'): 0.0091,
            ('USD', 'HKD'): 7.8,
            ('HKD', 'USD'): 0.128,
        }
        
        # 直接汇率
        if (from_currency, to_currency) in default_rates:
            return default_rates[(from_currency, to_currency)]
        
        # 通过USD中转
        if from_currency != 'USD' and to_currency != 'USD':
            usd_from = default_rates.get((from_currency, 'USD'), 1.0)
            usd_to = default_rates.get(('USD', to_currency), 1.0)
            return usd_from * usd_to
        
        return 1.0
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        item = self.cache.get(key)
        return bool(item and (time.time() - item['timestamp'] < self.cache_duration))


# 测试函数
def test_currency_converter():
    """测试汇率转换器"""
    converter = CurrencyConverter()
    
    print("🔄 测试美元/人民币汇率转换器")
    
    # 获取汇率信息
    rate_info = converter.get_rate_info()
    print(f"📊 当前汇率: 1 USD = {rate_info['rate']:.4f} CNY")
    print(f"📡 数据源: {rate_info['source']}")
    print(f"⏰ 时间: {rate_info['timestamp']}")
    
    # 测试转换
    usd_amount = 100
    cny_amount, _ = converter.convert_usd_to_cny(usd_amount)
    print(f"💵 {usd_amount} USD = {cny_amount:.2f} CNY")
    
    cny_amount = 1000
    usd_amount, _ = converter.convert_cny_to_usd(cny_amount)
    print(f"💴 {cny_amount} CNY = {usd_amount:.2f} USD")


if __name__ == "__main__":
    test_currency_converter()
    test_currency_converter()