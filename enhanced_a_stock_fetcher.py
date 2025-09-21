#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型A股数据获取器
使用多个数据源和更好的错误处理机制
"""

import pandas as pd
import numpy as np
import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
urllib3.disable_warnings(InsecureRequestWarning)

class EnhancedAStockFetcher:
    """增强型A股数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 配置SSL上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 数据源配置（按优先级排序，腾讯最准确）
        self.data_sources = {
            'tencent': {
                'base_url': 'http://qt.gtimg.cn',
                'realtime_url': '/q=',
                'priority': 1
            },
            'eastmoney': {
                'base_url': 'https://push2.eastmoney.com',
                'realtime_url': '/api/qt/clist/get',
                'history_url': '/api/qt/stock/kline/get',
                'priority': 2
            },
            'sina': {
                'base_url': 'https://hq.sinajs.cn',
                'realtime_url': '/list=',
                'priority': 3
            }
        }
        
        # 缓存配置
        self.cache = {}
        self.cache_duration = 30  # 30秒缓存
        
    def get_real_time_price(self, symbol: str) -> Dict:
        """获取A股实时价格和交易量信息"""
        cache_key = f"realtime_{symbol}"
        
        # 检查缓存
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # 尝试多个数据源
        for source_name, source_config in self.data_sources.items():
            try:
                if source_name == 'eastmoney':
                    data = self._get_eastmoney_realtime(symbol)
                elif source_name == 'sina':
                    data = self._get_sina_realtime(symbol)
                elif source_name == 'tencent':
                    data = self._get_tencent_realtime(symbol)
                
                if data and data.get('price', 0) > 0:
                    # 更新缓存
                    self.cache[cache_key] = {
                        'data': data,
                        'timestamp': time.time()
                    }
                    return data
                    
            except Exception as e:
                print(f"⚠️ {source_name} 数据源失败: {e}")
                continue
        
        # 所有数据源都失败，返回模拟数据
        print(f"⚠️ 所有数据源失败，使用模拟数据: {symbol}")
        mock_data = self._get_mock_data(symbol)
        self.cache[cache_key] = {
            'data': mock_data,
            'timestamp': time.time()
        }
        return mock_data
    
    def _get_eastmoney_realtime(self, symbol: str) -> Dict:
        """从东方财富获取实时数据"""
        url = f"{self.data_sources['eastmoney']['base_url']}{self.data_sources['eastmoney']['realtime_url']}"
        
        # 修复查询参数，使用正确的市场分类
        if symbol.startswith(('600', '601', '603', '688')):
            # 上海证券交易所
            market_filter = 'm:1+t:2,m:1+t:23'
        elif symbol.startswith(('000', '002', '300')):
            # 深圳证券交易所
            market_filter = 'm:0+t:6,m:0+t:80'
        else:
            # 默认全市场
            market_filter = 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23'
        
        params = {
            'pn': '1',
            'pz': '1',
            'po': '1',
            'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2',
            'invt': '2',
            'fid': 'f12',
            'fs': f'{market_filter}+s:{symbol}',
            'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
        }
        
        response = self.session.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' in data and 'diff' in data['data'] and data['data']['diff']:
            # 查找匹配的股票代码
            stock_data = None
            for item in data['data']['diff']:
                if item.get('f12') == symbol:
                    stock_data = item
                    break
            
            if not stock_data:
                # 如果没找到匹配的股票，使用第一个结果
                stock_data = data['data']['diff'][0]
                print(f"⚠️ 未找到精确匹配的股票代码 {symbol}，使用 {stock_data.get('f12', 'unknown')}")
            
            # 确保价格数据不为0
            price = float(stock_data.get('f2', 0))
            if price == 0:
                price = float(stock_data.get('f3', 0))  # 尝试其他字段
            
            # 验证股票名称是否合理（避免获取到错误的股票）
            stock_name = stock_data.get('f14', '')
            if '茅台' not in stock_name and symbol == '600519':
                print(f"⚠️ 获取的股票名称不匹配: {stock_name}，期望茅台")
                return None
            
            return {
                'symbol': symbol,
                'price': price,  # 最新价
                'change': float(stock_data.get('f4', 0)),  # 涨跌额
                'change_pct': float(stock_data.get('f3', 0)),  # 涨跌幅
                'volume': float(stock_data.get('f5', 0)) * 100,  # 成交量(手) -> 股
                'turnover': float(stock_data.get('f6', 0)),  # 成交额(元)
                'high': float(stock_data.get('f15', 0)),  # 最高价
                'low': float(stock_data.get('f16', 0)),  # 最低价
                'open': float(stock_data.get('f17', 0)),  # 开盘价
                'close': price,  # 收盘价
                'buy_volume': float(stock_data.get('f8', 0)) * 100,  # 买入量
                'sell_volume': float(stock_data.get('f9', 0)) * 100,  # 卖出量
                'source': 'eastmoney',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _get_sina_realtime(self, symbol: str) -> Dict:
        """从新浪获取实时数据"""
        # 转换股票代码格式
        if symbol.startswith(('000', '002', '300')):
            sina_symbol = f'sz{symbol}'
        elif symbol.startswith(('600', '601', '603', '688')):
            sina_symbol = f'sh{symbol}'
        else:
            return None
        
        url = f"{self.data_sources['sina']['base_url']}{self.data_sources['sina']['realtime_url']}{sina_symbol}"
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        if 'var hq_str_' in content:
            data_str = content.split('"')[1]
            data_list = data_str.split(',')
            
            if len(data_list) >= 32:
                return {
                    'symbol': symbol,
                    'price': float(data_list[3]) if data_list[3] else 0,
                    'change': float(data_list[4]) if data_list[4] else 0,
                    'change_pct': float(data_list[5]) if data_list[5] else 0,
                    'volume': float(data_list[8]) if data_list[8] else 0,
                    'turnover': float(data_list[9]) if data_list[9] else 0,
                    'high': float(data_list[4]) if data_list[4] else 0,
                    'low': float(data_list[5]) if data_list[5] else 0,
                    'open': float(data_list[1]) if data_list[1] else 0,
                    'close': float(data_list[3]) if data_list[3] else 0,
                    'buy_volume': 0,  # 新浪不提供买卖量分解
                    'sell_volume': 0,
                    'source': 'sina',
                    'timestamp': datetime.now().isoformat()
                }
        
        return None
    
    def _get_tencent_realtime(self, symbol: str) -> Dict:
        """从腾讯获取实时数据"""
        # 转换股票代码格式
        if symbol.startswith(('000', '002', '300')):
            tencent_symbol = f'sz{symbol}'
        elif symbol.startswith(('600', '601', '603', '688')):
            tencent_symbol = f'sh{symbol}'
        else:
            return None
        
        url = f"{self.data_sources['tencent']['base_url']}{self.data_sources['tencent']['realtime_url']}{tencent_symbol}"
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        if 'v_' in content:
            data_str = content.split('"')[1]
            data_list = data_str.split('~')
            
            if len(data_list) >= 10:
                # 腾讯数据格式: 1~股票名称~股票代码~当前价~昨收~今开~成交量~成交额~买一~买一量~卖一~卖一量~...
                # 索引: 0~1~2~3~4~5~6~7~8~9~10~11~...
                current_price = float(data_list[3]) if data_list[3] else 0
                prev_close = float(data_list[4]) if data_list[4] else 0
                open_price = float(data_list[5]) if data_list[5] else 0
                volume = float(data_list[6]) if data_list[6] else 0
                turnover = float(data_list[7]) if data_list[7] else 0
                
                # 计算涨跌额和涨跌幅
                change = current_price - prev_close if prev_close > 0 else 0
                change_pct = (change / prev_close * 100) if prev_close > 0 else 0
                
                return {
                    'symbol': symbol,
                    'price': current_price,
                    'change': change,
                    'change_pct': change_pct,
                    'volume': volume,
                    'turnover': turnover,
                    'high': current_price,  # 腾讯不直接提供最高价，使用当前价
                    'low': current_price,   # 腾讯不直接提供最低价，使用当前价
                    'open': open_price,
                    'close': current_price,
                    'buy_volume': 0,  # 腾讯不提供买卖量分解
                    'sell_volume': 0,
                    'source': 'tencent',
                    'timestamp': datetime.now().isoformat()
                }
        
        return None
    
    def get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """获取A股历史数据"""
        cache_key = f"history_{symbol}_{days}"
        
        # 检查缓存
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            import akshare as ak
            
            # 使用akshare获取历史数据
            stock_zh_a_hist_df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
                adjust="qfq"  # 前复权
            )
            
            if not stock_zh_a_hist_df.empty:
                # 重命名列以匹配标准格式
                stock_zh_a_hist_df = stock_zh_a_hist_df.rename(columns={
                    '日期': 'timestamps',
                    '开盘': 'open',
                    '最高': 'high',
                    '最低': 'low',
                    '收盘': 'close',
                    '成交量': 'volume',
                    '成交额': 'turnover'
                })
                
                # 确保数据类型正确
                for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                    stock_zh_a_hist_df[col] = pd.to_numeric(stock_zh_a_hist_df[col], errors='coerce')
                
                # 统一时间列为datetime，去重并排序
                stock_zh_a_hist_df['timestamps'] = pd.to_datetime(stock_zh_a_hist_df['timestamps'], errors='coerce')
                stock_zh_a_hist_df = stock_zh_a_hist_df.dropna(subset=['timestamps', 'open', 'high', 'low', 'close'])
                stock_zh_a_hist_df = stock_zh_a_hist_df.drop_duplicates(subset=['timestamps']).sort_values('timestamps').reset_index(drop=True)
                
                # 使用价格验证器进行深度验证和修复
                try:
                    from price_validator import PriceValidator
                    validator = PriceValidator()
                    stock_zh_a_hist_df = validator.validate_and_fix_prices(stock_zh_a_hist_df, symbol, 'cn_stocks')
                except ImportError:
                    print("⚠️ 价格验证器未找到，使用基础验证")
                
                # 添加买卖量分解（基于历史数据估算）
                stock_zh_a_hist_df = self._add_volume_breakdown(stock_zh_a_hist_df)
                
                # 更新缓存
                self.cache[cache_key] = {
                    'data': stock_zh_a_hist_df,
                    'timestamp': time.time()
                }
                
                print(f"✅ 成功获取A股 {symbol} 历史数据: {len(stock_zh_a_hist_df)} 条记录")
                return stock_zh_a_hist_df
            else:
                print(f"⚠️ A股 {symbol} 历史数据为空，使用模拟数据")
                mock_df = self._generate_mock_historical_data(symbol, days)
                self.cache[cache_key] = {
                    'data': mock_df,
                    'timestamp': time.time()
                }
                return mock_df
                
        except Exception as e:
            print(f"⚠️ 获取A股 {symbol} 历史数据失败: {e}")
            mock_df = self._generate_mock_historical_data(symbol, days)
            self.cache[cache_key] = {
                'data': mock_df,
                'timestamp': time.time()
            }
            return mock_df
    
    def _add_volume_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加买卖量分解"""
        try:
            # 基于价格变化趋势估算买卖量
            df['price_change'] = df['close'].pct_change().fillna(0)
            
            # 清理数据，确保没有NaN或inf值
            df['volume'] = df['volume'].replace([np.inf, -np.inf], np.nan).fillna(100000)
            df['close'] = df['close'].replace([np.inf, -np.inf], np.nan).fillna(25.0)
            df['price_change'] = df['price_change'].replace([np.inf, -np.inf], np.nan).fillna(0)
            
            # 改进的买卖量估算逻辑
            df['buy_volume'] = df['volume'] * (0.5 + df['price_change'].clip(0, 0.1) * 5)
            df['sell_volume'] = df['volume'] - df['buy_volume']
            
            # 确保买卖量不为负数
            df['buy_volume'] = df['buy_volume'].clip(0, df['volume'])
            df['sell_volume'] = df['sell_volume'].clip(0, df['volume'])
            
            # 重新计算确保买卖量总和等于总成交量
            total_volume = df['buy_volume'] + df['sell_volume']
            volume_ratio = df['volume'] / total_volume
            volume_ratio = volume_ratio.fillna(1)  # 处理除零情况
            
            # 清理volume_ratio中的NaN和inf值
            volume_ratio = volume_ratio.replace([np.inf, -np.inf], np.nan).fillna(1)
            
            # 计算买入量，确保没有NaN值
            buy_volume_calc = df['buy_volume'] * volume_ratio
            buy_volume_calc = buy_volume_calc.replace([np.inf, -np.inf], np.nan).fillna(df['volume'] * 0.5)
            df['buy_volume'] = buy_volume_calc.round().astype(int)
            df['sell_volume'] = df['volume'] - df['buy_volume']
            
            # 处理特殊情况：如果买卖量都为0，平均分配
            zero_volume_mask = (df['buy_volume'] == 0) & (df['sell_volume'] == 0) & (df['volume'] > 0)
            if zero_volume_mask.any():
                half_volume = df.loc[zero_volume_mask, 'volume'] * 0.5
                half_volume = half_volume.replace([np.inf, -np.inf], np.nan).fillna(50000)
                df.loc[zero_volume_mask, 'buy_volume'] = half_volume.round().astype(int)
                df.loc[zero_volume_mask, 'sell_volume'] = df.loc[zero_volume_mask, 'volume'] - df.loc[zero_volume_mask, 'buy_volume']
            
            # 最终检查：确保所有值都是有效的
            df['buy_volume'] = df['buy_volume'].replace([np.inf, -np.inf], np.nan).fillna(50000).astype(int)
            df['sell_volume'] = df['sell_volume'].replace([np.inf, -np.inf], np.nan).fillna(50000).astype(int)
            
            return df
            
        except Exception as e:
            print(f"买卖量分解计算失败: {e}")
            # 返回简单的平均分配
            df['buy_volume'] = (df['volume'] * 0.5).round().astype(int)
            df['sell_volume'] = df['volume'] - df['buy_volume']
            return df
    
    def _generate_mock_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """生成模拟历史数据"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # 基础价格设置
        base_prices = {
            '600519': 1600, '000858': 180, '000001': 12, '000002': 18,
            'default': 25
        }
        
        base_price = base_prices.get(symbol, base_prices['default'])
        
        np.random.seed(hash(symbol) % 2**32)
        prices = []
        volumes = []
        current_price = base_price
        
        for _ in range(days):
            change = np.random.normal(0, 0.02)
            current_price *= (1 + change)
            prices.append(current_price)
            volumes.append(np.random.uniform(10000, 100000))
        
        df = pd.DataFrame({
            'timestamps': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': volumes,
            'turnover': [v * p for v, p in zip(volumes, prices)]
        })
        
        # 添加买卖量分解
        df = self._add_volume_breakdown(df)
        
        return df
    
    def _get_mock_data(self, symbol: str) -> Dict:
        """获取模拟数据"""
        base_prices = {
            '600519': 1600, '000858': 180, '000001': 12, '000002': 18,
            'default': 25
        }
        
        base_price = base_prices.get(symbol, base_prices['default'])
        
        # 添加随机波动
        change = np.random.normal(0, 0.01)
        current_price = base_price * (1 + change)
        
        return {
            'symbol': symbol,
            'price': current_price,
            'change': current_price - base_price,
            'change_pct': change * 100,
            'volume': np.random.uniform(10000, 100000),
            'turnover': current_price * np.random.uniform(10000, 100000),
            'high': current_price * 1.02,
            'low': current_price * 0.98,
            'open': current_price * (1 + np.random.normal(0, 0.005)),
            'close': current_price,
            'buy_volume': np.random.uniform(5000, 50000),
            'sell_volume': np.random.uniform(5000, 50000),
            'source': 'mock',
            'timestamp': datetime.now().isoformat()
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        entry = self.cache[cache_key]
        # 历史实现中可能直接存了DataFrame，这里直接视为无效以避免异常
        if not isinstance(entry, dict):
            return False
        cache_time = entry.get('timestamp', 0)
        if isinstance(cache_time, str):
            try:
                cache_time = datetime.fromisoformat(cache_time).timestamp()
            except Exception:
                cache_time = 0
        try:
            return (time.time() - float(cache_time)) < self.cache_duration
        except Exception:
            return False
    
    def get_volume_breakdown(self, symbol: str) -> Dict:
        """获取详细的交易量分解信息"""
        realtime_data = self.get_real_time_price(symbol)
        
        if realtime_data and realtime_data.get('volume', 0) > 0:
            total_volume = realtime_data['volume']
            buy_volume = realtime_data.get('buy_volume', 0)
            sell_volume = realtime_data.get('sell_volume', 0)
            
            # 如果没有买卖量分解，基于价格变化估算
            if buy_volume == 0 and sell_volume == 0:
                change_pct = realtime_data.get('change_pct', 0)
                if change_pct > 0:
                    buy_ratio = min(0.7, 0.5 + abs(change_pct) / 100)
                else:
                    buy_ratio = max(0.3, 0.5 - abs(change_pct) / 100)
                
                buy_volume = total_volume * buy_ratio
                sell_volume = total_volume - buy_volume
            
            return {
                'symbol': symbol,
                'total_volume': total_volume,
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'buy_ratio': buy_volume / total_volume if total_volume > 0 else 0.5,
                'sell_ratio': sell_volume / total_volume if total_volume > 0 else 0.5,
                'timestamp': realtime_data.get('timestamp', datetime.now().isoformat())
            }
        
        return None

def main():
    """测试函数"""
    fetcher = EnhancedAStockFetcher()
    
    # 测试实时价格
    test_symbols = ['600519', '000858', '000001', '000002']
    
    print("🚀 增强型A股数据获取器测试")
    print("=" * 60)
    
    for symbol in test_symbols:
        print(f"\n📊 测试 {symbol}:")
        
        # 获取实时价格
        realtime_data = fetcher.get_real_time_price(symbol)
        if realtime_data:
            print(f"  价格: {realtime_data['price']:.2f} 元")
            print(f"  涨跌: {realtime_data['change']:+.2f} ({realtime_data['change_pct']:+.2f}%)")
            print(f"  成交量: {realtime_data['volume']:,.0f} 手")
            print(f"  成交额: {realtime_data['turnover']:,.0f} 元")
            print(f"  数据源: {realtime_data['source']}")
        
        # 获取交易量分解
        volume_data = fetcher.get_volume_breakdown(symbol)
        if volume_data:
            print(f"  买入量: {volume_data['buy_volume']:,.0f} 手 ({volume_data['buy_ratio']:.1%})")
            print(f"  卖出量: {volume_data['sell_volume']:,.0f} 手 ({volume_data['sell_ratio']:.1%})")

if __name__ == "__main__":
    main()