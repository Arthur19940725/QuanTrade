#!/usr/bin/env python3
"""
多市场股票预测器
支持A股、港股、美股、虚拟货币的股票名称/代码搜索和价格预测
基于Kronos模型进行时间序列预测
"""

import sys
import os
import warnings
from datetime import datetime, timedelta
import json
import traceback
from typing import Dict, List, Optional, Tuple
import re

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import requests
import time

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'model'))

try:
    from model.kronos import Kronos, KronosTokenizer, KronosPredictor
    MODEL_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Kronos模型导入失败: {e}")
    MODEL_AVAILABLE = False


class StockSymbolResolver:
    """股票代码/名称解析器"""
    
    def __init__(self):
        self.stock_databases = {
            'cn_stocks': {},  # A股数据库
            'hk_stocks': {},  # 港股数据库  
            'us_stocks': {},  # 美股数据库
            'crypto': {}      # 加密货币数据库
        }
        self._load_stock_databases()
    
    def _load_stock_databases(self):
        """加载股票数据库"""
        # A股常见股票（示例数据）
        self.stock_databases['cn_stocks'] = {
            # 股票代码: [股票名称, 英文名称, 市场]
            '000001': ['平安银行', 'Ping An Bank', 'SZ'],
            '000002': ['万科A', 'China Vanke', 'SZ'],
            '000858': ['五粮液', 'Wuliangye', 'SZ'],
            '600000': ['浦发银行', 'Shanghai Pudong Development Bank', 'SH'],
            '600036': ['招商银行', 'China Merchants Bank', 'SH'],
            '600519': ['贵州茅台', 'Kweichow Moutai', 'SH'],
            '600887': ['伊利股份', 'Inner Mongolia Yili', 'SH'],
            '000858': ['五粮液', 'Wuliangye Yibin', 'SZ'],
            '002415': ['海康威视', 'Hikvision', 'SZ'],
            '300059': ['东方财富', 'East Money', 'SZ'],
        }
        
        # 港股常见股票
        self.stock_databases['hk_stocks'] = {
            '0700': ['腾讯控股', 'Tencent Holdings', 'HK'],
            '0941': ['中国移动', 'China Mobile', 'HK'],
            '0939': ['建设银行', 'China Construction Bank', 'HK'],
            '1299': ['友邦保险', 'AIA Group', 'HK'],
            '2318': ['中国平安', 'Ping An Insurance', 'HK'],
            '0005': ['汇丰控股', 'HSBC Holdings', 'HK'],
            '1398': ['工商银行', 'Industrial and Commercial Bank of China', 'HK'],
            '2388': ['中银香港', 'BOC Hong Kong', 'HK'],
            '0883': ['中国海洋石油', 'CNOOC', 'HK'],
            '1211': ['比亚迪', 'BYD Company', 'HK'],
        }
        
        # 美股常见股票  
        self.stock_databases['us_stocks'] = {
            'AAPL': ['苹果公司', 'Apple Inc.', 'NASDAQ'],
            'MSFT': ['微软公司', 'Microsoft Corporation', 'NASDAQ'],
            'GOOGL': ['谷歌', 'Alphabet Inc.', 'NASDAQ'],
            'AMZN': ['亚马逊', 'Amazon.com Inc.', 'NASDAQ'],
            'TSLA': ['特斯拉', 'Tesla Inc.', 'NASDAQ'],
            'META': ['Meta平台', 'Meta Platforms Inc.', 'NASDAQ'],
            'NVDA': ['英伟达', 'NVIDIA Corporation', 'NASDAQ'],
            'JPM': ['摩根大通', 'JPMorgan Chase & Co.', 'NYSE'],
            'JNJ': ['强生公司', 'Johnson & Johnson', 'NYSE'],
            'V': ['维萨', 'Visa Inc.', 'NYSE'],
            'PG': ['宝洁公司', 'Procter & Gamble', 'NYSE'],
            'UNH': ['联合健康', 'UnitedHealth Group', 'NYSE'],
            'HD': ['家得宝', 'The Home Depot', 'NYSE'],
            'MA': ['万事达', 'Mastercard Inc.', 'NYSE'],
            'BAC': ['美国银行', 'Bank of America', 'NYSE'],
        }
        
        # 加密货币
        self.stock_databases['crypto'] = {
            'BTC': ['比特币', 'Bitcoin', 'Crypto'],
            'ETH': ['以太坊', 'Ethereum', 'Crypto'],
            'BNB': ['币安币', 'Binance Coin', 'Crypto'],
            'XRP': ['瑞波币', 'Ripple', 'Crypto'],
            'ADA': ['艾达币', 'Cardano', 'Crypto'],
            'DOGE': ['狗狗币', 'Dogecoin', 'Crypto'],
            'SOL': ['索拉纳', 'Solana', 'Crypto'],
            'TRX': ['波场币', 'TRON', 'Crypto'],
            'AVAX': ['雪崩币', 'Avalanche', 'Crypto'],
            'SHIB': ['柴犬币', 'Shiba Inu', 'Crypto'],
        }
    
    def search_symbol(self, query: str) -> List[Dict]:
        """搜索股票代码/名称"""
        query = query.strip().upper()
        results = []
        
        for market, stocks in self.stock_databases.items():
            for code, info in stocks.items():
                cn_name, en_name, exchange = info
                
                # 匹配代码
                if code.upper() == query:
                    results.append({
                        'symbol': code,
                        'cn_name': cn_name,
                        'en_name': en_name,
                        'market': market,
                        'exchange': exchange,
                        'match_type': 'exact_code'
                    })
                # 匹配中文名称
                elif query in cn_name:
                    results.append({
                        'symbol': code,
                        'cn_name': cn_name,
                        'en_name': en_name,
                        'market': market,
                        'exchange': exchange,
                        'match_type': 'cn_name'
                    })
                # 匹配英文名称
                elif query in en_name.upper():
                    results.append({
                        'symbol': code,
                        'cn_name': cn_name,
                        'en_name': en_name,
                        'market': market,
                        'exchange': exchange,
                        'match_type': 'en_name'
                    })
        
        # 按匹配类型排序，精确匹配优先
        sort_order = {'exact_code': 0, 'cn_name': 1, 'en_name': 2}
        results.sort(key=lambda x: sort_order.get(x['match_type'], 3))
        
        return results


class MultiMarketDataFetcher:
    """多市场数据获取器"""
    
    def __init__(self):
        self.crypto_base_url = "https://api.binance.com/api/v3"
        self.us_base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        
        # 导入增强型数据源管理器
        try:
            from data_source_manager import EnhancedDataSourceManager
            self.enhanced_manager = EnhancedDataSourceManager()
            self.use_enhanced_manager = True
            print("✅ 使用增强型数据源管理器")
        except ImportError:
            self.enhanced_manager = None
            self.use_enhanced_manager = False
            print("⚠️ 使用基础数据获取器")
        
    def fetch_crypto_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """获取加密货币数据"""
        try:
            url = f"{self.crypto_base_url}/klines"
            params = {
                'symbol': f"{symbol}USDT",
                'interval': '1d',
                'limit': days
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            # 统一时间与数据类型，去重并排序
            df['timestamps'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna(subset=['timestamps', 'open', 'high', 'low', 'close']).drop_duplicates(subset=['timestamps'])
            df = df[['timestamps', 'open', 'high', 'low', 'close', 'volume']].sort_values('timestamps').reset_index(drop=True)
            return df
            
        except Exception as e:
            print(f"获取加密货币 {symbol} 数据失败: {e}")
            return self._generate_mock_data(symbol, days, 'crypto')
    
    def fetch_us_stock_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """获取美股数据"""
        try:
            # 计算时间范围
            end_date = int(time.time())
            start_date = end_date - (days * 24 * 60 * 60)
            
            url = f"{self.us_base_url}/{symbol}"
            params = {
                'period1': start_date,
                'period2': end_date,
                'interval': '1d',
                'events': 'history'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data['chart']['result'][0]
            
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'timestamps': pd.to_datetime(timestamps, unit='s'),
                'open': quotes['open'],
                'high': quotes['high'],
                'low': quotes['low'],
                'close': quotes['close'],
                'volume': quotes['volume']
            })
            
            df = df.dropna()
            return df
            
        except Exception as e:
            print(f"获取美股 {symbol} 数据失败: {e}")
            return self._generate_mock_data(symbol, days, 'us_stock')
    
    def fetch_hk_stock_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """获取港股数据"""
        try:
            # 港股代码格式化
            if not symbol.startswith('0'):
                symbol = symbol.zfill(4)
            hk_symbol = f"{symbol}.HK"
            
            # 使用Yahoo Finance API
            end_date = int(time.time())
            start_date = end_date - (days * 24 * 60 * 60)
            
            url = f"{self.us_base_url}/{hk_symbol}"
            params = {
                'period1': start_date,
                'period2': end_date,
                'interval': '1d'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data['chart']['result'][0]
            
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'timestamps': pd.to_datetime(timestamps, unit='s'),
                'open': quotes['open'],
                'high': quotes['high'],
                'low': quotes['low'],
                'close': quotes['close'],
                'volume': quotes['volume']
            })
            
            df = df.dropna()
            return df
            
        except Exception as e:
            print(f"获取港股 {symbol} 数据失败: {e}")
            return self._generate_mock_data(symbol, days, 'hk_stock')
    
    def fetch_cn_stock_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """获取A股数据"""
        try:
            # 使用增强型A股数据获取器
            from enhanced_a_stock_fetcher import EnhancedAStockFetcher
            
            fetcher = EnhancedAStockFetcher()
            df = fetcher.get_historical_data(symbol, days)
            
            if not df.empty:
                # 确保包含买卖量分解
                if 'buy_volume' not in df.columns or 'sell_volume' not in df.columns:
                    df = self._add_volume_breakdown(df)
                
                print(f"✅ 成功获取A股 {symbol} 历史数据: {len(df)} 条记录")
                return df[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'buy_volume', 'sell_volume']]
            else:
                print(f"⚠️ A股 {symbol} 历史数据为空，使用模拟数据")
                return self._generate_mock_data(symbol, days, 'cn_stock')
                
        except ImportError:
            print("⚠️ 增强型A股数据获取器未找到，使用akshare")
            return self._fetch_cn_stock_data_with_akshare(symbol, days)
        except Exception as e:
            print(f"获取A股 {symbol} 数据失败: {e}")
            return self._generate_mock_data(symbol, days, 'cn_stock')
    
    def _fetch_cn_stock_data_with_akshare(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """使用akshare获取A股数据（备用方法）"""
        try:
            import akshare as ak
            
            # 使用akshare获取A股历史数据
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
                stock_zh_a_hist_df['timestamps'] = pd.to_datetime(stock_zh_a_hist_df['timestamps'], errors='coerce')
                for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                    stock_zh_a_hist_df[col] = pd.to_numeric(stock_zh_a_hist_df[col], errors='coerce')
                
                # 清洗、去重并排序
                stock_zh_a_hist_df = stock_zh_a_hist_df.dropna(subset=['timestamps', 'open', 'high', 'low', 'close'])
                stock_zh_a_hist_df = stock_zh_a_hist_df.drop_duplicates(subset=['timestamps']).sort_values('timestamps').reset_index(drop=True)
                
                # 添加买卖量分解
                stock_zh_a_hist_df = self._add_volume_breakdown(stock_zh_a_hist_df)
                
                print(f"✅ 成功获取A股 {symbol} 历史数据: {len(stock_zh_a_hist_df)} 条记录")
                return stock_zh_a_hist_df[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'buy_volume', 'sell_volume']]
            else:
                print(f"⚠️ A股 {symbol} 历史数据为空，使用模拟数据")
                return self._generate_mock_data(symbol, days, 'cn_stock')
                
        except Exception as e:
            print(f"⚠️ 获取A股 {symbol} 历史数据失败: {e}")
            return self._generate_mock_data(symbol, days, 'cn_stock')
    
    def _add_volume_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加买卖量分解"""
        # 基于价格变化趋势估算买卖量
        df['price_change'] = df['close'].pct_change()
        
        # 改进的买卖量估算逻辑
        df['buy_volume'] = df['volume'] * (0.5 + df['price_change'].clip(0, 0.1) * 5)
        df['sell_volume'] = df['volume'] - df['buy_volume']
        
        # 确保买卖量不为负数且总和等于总成交量
        df['buy_volume'] = df['buy_volume'].clip(0, df['volume'])
        df['sell_volume'] = df['volume'] - df['buy_volume']  # 重新计算确保一致性
        
        # 处理特殊情况：如果买卖量都为0，平均分配
        zero_volume_mask = (df['buy_volume'] == 0) & (df['sell_volume'] == 0) & (df['volume'] > 0)
        df.loc[zero_volume_mask, 'buy_volume'] = df.loc[zero_volume_mask, 'volume'] * 0.5
        df.loc[zero_volume_mask, 'sell_volume'] = df.loc[zero_volume_mask, 'volume'] * 0.5
        
        return df
    
    def _generate_mock_data(self, symbol: str, days: int, market_type: str) -> pd.DataFrame:
        """生成模拟数据"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # 根据市场类型设置基础价格
        base_prices = {
            'crypto': {'BTC': 45000, 'ETH': 2500, 'SOL': 100, 'default': 1000},
            'us_stock': {'AAPL': 150, 'MSFT': 300, 'GOOGL': 2500, 'default': 100},
            'hk_stock': {'0700': 350, '0941': 80, 'default': 50},
            'cn_stock': {'600519': 1800, '000858': 150, 'default': 20}
        }
        
        base_price = base_prices.get(market_type, {}).get(symbol, base_prices[market_type]['default'])
        
        np.random.seed(hash(symbol) % 2**32)
        prices = []
        current_price = base_price
        
        for _ in range(days):
            change = np.random.normal(0, 0.02)  # 2%的日波动
            current_price *= (1 + change)
            prices.append(current_price)
        
        df = pd.DataFrame({
            'timestamps': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000, 100000, days)
        })
        
        return df
    
    def fetch_data(self, symbol: str, market: str, days: int = 100) -> pd.DataFrame:
        """根据市场类型获取数据"""
        # 优先使用增强型数据源管理器
        if self.use_enhanced_manager:
            try:
                print(f"🔄 使用增强型数据源获取: {symbol} ({market})")
                return self.enhanced_manager.get_latest_data(symbol, market, days)
            except Exception as e:
                print(f"⚠️ 增强型数据源失败，回退到基础方法: {e}")
        
        # 回退到原始方法
        if market == 'crypto':
            return self.fetch_crypto_data(symbol, days)
        elif market == 'us_stocks':
            return self.fetch_us_stock_data(symbol, days)
        elif market == 'hk_stocks':
            return self.fetch_hk_stock_data(symbol, days)
        elif market == 'cn_stocks':
            return self.fetch_cn_stock_data(symbol, days)
        else:
            raise ValueError(f"不支持的市场类型: {market}")
    
    def get_real_time_price(self, symbol: str, market: str) -> Optional[float]:
        """获取实时价格"""
        if self.use_enhanced_manager:
            return self.enhanced_manager.get_real_time_price(symbol, market)
        else:
            try:
                df = self.fetch_data(symbol, market, days=1)
                return float(df['close'].iloc[-1])
            except:
                return None


class MultiMarketStockPredictor:
    """多市场股票预测器"""
    
    def __init__(self):
        self.symbol_resolver = StockSymbolResolver()
        self.data_fetcher = MultiMarketDataFetcher()
        self.model = None
        self.tokenizer = None
        self.predictor = None
        self.model_loaded = False
    
    def load_kronos_model(self, model_name: str = "NeoQuasar/Kronos-small", device: str = "cpu"):
        """加载Kronos模型"""
        try:
            if not MODEL_AVAILABLE:
                raise ImportError("Kronos模型不可用")
            
            print(f"正在加载Kronos模型: {model_name}")
            
            # 选择对应的tokenizer
            tokenizer_map = {
                "NeoQuasar/Kronos-small": "NeoQuasar/Kronos-Tokenizer-base",
                "NeoQuasar/Kronos-base": "NeoQuasar/Kronos-Tokenizer-base",
                "NeoQuasar/Kronos-mini": "NeoQuasar/Kronos-Tokenizer-2k"
            }
            
            tokenizer_name = tokenizer_map.get(model_name, "NeoQuasar/Kronos-Tokenizer-base")
            
            self.tokenizer = KronosTokenizer.from_pretrained(tokenizer_name)
            self.model = Kronos.from_pretrained(model_name)
            
            context_length = 2048 if "mini" in model_name else 512
            self.predictor = KronosPredictor(
                self.model, 
                self.tokenizer, 
                device=device, 
                max_context=context_length
            )
            
            self.model_loaded = True
            print(f"✅ Kronos模型加载成功")
            return True
            
        except Exception as e:
            print(f"❌ Kronos模型加载失败: {e}")
            self.model_loaded = False
            return False
    
    def search_stocks(self, query: str) -> List[Dict]:
        """搜索股票"""
        return self.symbol_resolver.search_symbol(query)
    
    def predict_stock(self, symbol: str, market: str, pred_days: int = 7, 
                     lookback_days: int = 60) -> Dict:
        """预测股票价格"""
        try:
            # 获取历史数据
            print(f"正在获取 {symbol} ({market}) 的历史数据...")
            df = self.data_fetcher.fetch_data(symbol, market, lookback_days + 30)
            
            if len(df) < lookback_days:
                return {
                    'success': False,
                    'error': f'历史数据不足，需要至少{lookback_days}天数据，当前只有{len(df)}天'
                }
            
            # 准备预测数据
            lookback_df = df.tail(lookback_days).copy()
            current_price = float(lookback_df['close'].iloc[-1])
            
            # 如果模型已加载，使用Kronos预测
            if self.model_loaded and self.predictor is not None:
                prediction_data = self._predict_with_kronos(lookback_df, pred_days)
            else:
                # 使用技术分析预测
                prediction_data = self._predict_with_technical_analysis_advanced(lookback_df, pred_days)
            
            predicted_prices = prediction_data['close_prices']
            
            # 生成预测结果
            prediction_results = []
            for i, price in enumerate(predicted_prices):
                result_item = {
                    'date': prediction_data['timestamps'][i].strftime('%Y-%m-%d') if hasattr(prediction_data['timestamps'][i], 'strftime') else str(prediction_data['timestamps'][i])[:10],
                    'predicted_price': round(price, 4),
                    'change_pct': round(((price - current_price) / current_price) * 100, 2)
                }
                
                # 添加价格区间信息
                if 'upper_band' in prediction_data and 'lower_band' in prediction_data:
                    result_item['upper_price'] = round(prediction_data['upper_band'][i], 4)
                    result_item['lower_price'] = round(prediction_data['lower_band'][i], 4)
                
                # 添加交易量信息
                if 'volumes' in prediction_data and prediction_data['volumes']:
                    result_item['predicted_volume'] = round(prediction_data['volumes'][i], 0)
                
                prediction_results.append(result_item)
            
            # 计算预测摘要
            final_price = predicted_prices[-1]
            total_change = ((final_price - current_price) / current_price) * 100
            trend = "上涨" if total_change > 0 else "下跌" if total_change < 0 else "横盘"
            
            # 准备历史数据用于图表
            historical_data = []
            for i, row in lookback_df.iterrows():
                historical_data.append({
                    'date': row['timestamps'].strftime('%Y-%m-%d') if hasattr(row['timestamps'], 'strftime') else str(row['timestamps'])[:10],
                    'price': round(float(row['close']), 4),
                    'volume': round(float(row['volume']), 0) if 'volume' in row else 0,
                    'high': round(float(row['high']), 4) if 'high' in row else round(float(row['close']), 4),
                    'low': round(float(row['low']), 4) if 'low' in row else round(float(row['close']), 4)
                })
            
            return {
                'success': True,
                'symbol': symbol,
                'market': market,
                'current_price': round(current_price, 4),
                'prediction_days': pred_days,
                'predictions': prediction_results,
                'historical_data': historical_data,
                'chart_data': {
                    'historical_prices': [item['price'] for item in historical_data],
                    'historical_volumes': [item['volume'] for item in historical_data],
                    'historical_dates': [item['date'] for item in historical_data],
                    'predicted_prices': predicted_prices,
                    'predicted_volumes': prediction_data.get('volumes', []),
                    'upper_band': prediction_data.get('upper_band', []),
                    'lower_band': prediction_data.get('lower_band', []),
                    'prediction_dates': [item['date'] for item in prediction_results]
                },
                'summary': {
                    'final_price': round(final_price, 4),
                    'total_change_pct': round(total_change, 2),
                    'trend': trend,
                    'confidence': 'High' if self.model_loaded else 'Medium',
                    'price_range': {
                        'min': round(min(prediction_data.get('lower_band', predicted_prices)), 4),
                        'max': round(max(prediction_data.get('upper_band', predicted_prices)), 4)
                    }
                },
                'model_used': 'Kronos' if self.model_loaded else 'Technical Analysis'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'预测失败: {str(e)}'
            }
    
    def _predict_with_kronos(self, df: pd.DataFrame, pred_days: int) -> Dict:
        """使用Kronos模型预测，返回完整的预测数据"""
        try:
            # 准备数据格式
            required_cols = ['open', 'high', 'low', 'close']
            if 'volume' in df.columns:
                required_cols.append('volume')
            
            x_df = df[required_cols].copy()
            x_timestamp = df['timestamps']
            
            # 生成预测时间戳
            y_timestamp = pd.date_range(
                start=df['timestamps'].iloc[-1] + timedelta(days=1),
                periods=pred_days,
                freq='D'
            )
            
            # 确保时间戳格式正确
            if isinstance(x_timestamp, pd.DatetimeIndex):
                x_timestamp = pd.Series(x_timestamp, name='timestamps')
            if isinstance(y_timestamp, pd.DatetimeIndex):
                y_timestamp = pd.Series(y_timestamp, name='timestamps')
            
            # 调用Kronos预测
            pred_df = self.predictor.predict(
                df=x_df,
                x_timestamp=x_timestamp,
                y_timestamp=y_timestamp,
                pred_len=pred_days,
                T=1.0,
                top_p=0.9,
                sample_count=1,
                verbose=False
            )
            
            # 计算价格区间（基于预测的不确定性）
            close_prices = pred_df['close'].values
            high_prices = pred_df['high'].values if 'high' in pred_df.columns else close_prices * 1.02
            low_prices = pred_df['low'].values if 'low' in pred_df.columns else close_prices * 0.98
            volumes = pred_df['volume'].values if 'volume' in pred_df.columns else None
            
            # 计算价格波动区间
            price_volatility = np.std(close_prices) * 0.5
            upper_band = close_prices + price_volatility
            lower_band = close_prices - price_volatility
            
            return {
                'close_prices': close_prices.tolist(),
                'high_prices': high_prices.tolist(),
                'low_prices': low_prices.tolist(),
                'upper_band': upper_band.tolist(),
                'lower_band': lower_band.tolist(),
                'volumes': volumes.tolist() if volumes is not None else None,
                'timestamps': y_timestamp.tolist()
            }
            
        except Exception as e:
            print(f"Kronos预测失败，回退到技术分析: {e}")
            return self._predict_with_technical_analysis_advanced(df, pred_days)
    
    def _predict_with_technical_analysis(self, df: pd.DataFrame, pred_days: int) -> List[float]:
        """使用技术分析预测"""
        prices = df['close']
        current_price = float(prices.iloc[-1])
        
        # 计算技术指标
        sma_20 = prices.rolling(20).mean().iloc[-1] if len(prices) >= 20 else current_price
        ema_12 = prices.ewm(span=12).mean().iloc[-1]
        
        # 计算RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        latest_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        # 计算趋势强度
        price_momentum = (current_price - sma_20) / sma_20 if not pd.isna(sma_20) else 0
        ema_trend = 1 if current_price > ema_12 else -1
        rsi_signal = 1 if latest_rsi < 30 else (-1 if latest_rsi > 70 else 0)
        
        # 综合信号
        trend_score = (price_momentum * 10 + ema_trend + rsi_signal) / 3
        
        # 计算波动率
        returns = prices.pct_change().dropna()
        volatility = float(returns.std()) if len(returns) > 0 else 0.02
        
        # 生成预测价格
        predicted_prices = []
        price = current_price
        daily_trend = trend_score * 0.005  # 每日趋势强度
        
        for day in range(pred_days):
            # 添加随机波动
            random_factor = np.random.normal(0, volatility * 0.5)
            trend_decay = 0.95 ** day  # 趋势衰减
            
            daily_change = (daily_trend * trend_decay) + random_factor
            price *= (1 + daily_change)
            predicted_prices.append(price)
        
        return predicted_prices
    
    def _predict_with_technical_analysis_advanced(self, df: pd.DataFrame, pred_days: int) -> Dict:
        """使用高级技术分析预测，返回完整的预测数据"""
        prices = df['close']
        volumes = df['volume'] if 'volume' in df.columns else pd.Series([1000] * len(df))
        current_price = float(prices.iloc[-1])
        current_volume = float(volumes.iloc[-1])
        
        # 计算技术指标
        sma_20 = prices.rolling(20).mean().iloc[-1] if len(prices) >= 20 else current_price
        ema_12 = prices.ewm(span=12).mean().iloc[-1]
        
        # 计算RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        latest_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
        
        # 计算趋势强度
        price_momentum = (current_price - sma_20) / sma_20 if not pd.isna(sma_20) else 0
        ema_trend = 1 if current_price > ema_12 else -1
        rsi_signal = 1 if latest_rsi < 30 else (-1 if latest_rsi > 70 else 0)
        
        # 综合信号
        trend_score = (price_momentum * 10 + ema_trend + rsi_signal) / 3
        
        # 计算波动率
        returns = prices.pct_change().dropna()
        volatility = float(returns.std()) if len(returns) > 0 else 0.02
        
        # 生成预测数据
        predicted_prices = []
        predicted_volumes = []
        upper_band = []
        lower_band = []
        
        price = current_price
        volume = current_volume
        daily_trend = trend_score * 0.005  # 每日趋势强度
        
        for day in range(pred_days):
            # 价格预测
            random_factor = np.random.normal(0, volatility * 0.5)
            trend_decay = 0.95 ** day  # 趋势衰减
            
            daily_change = (daily_trend * trend_decay) + random_factor
            price *= (1 + daily_change)
            predicted_prices.append(price)
            
            # 价格区间计算
            price_uncertainty = volatility * price * (1 + day * 0.1)  # 不确定性随时间增加
            upper_band.append(price + price_uncertainty)
            lower_band.append(max(price - price_uncertainty, price * 0.5))  # 防止负价格
            
            # 交易量预测
            volume_change = np.random.normal(0, 0.1)  # 10%的交易量波动
            volume *= (1 + volume_change)
            predicted_volumes.append(max(volume, current_volume * 0.1))  # 最小交易量
        
        # 生成时间戳
        future_dates = pd.date_range(
            start=df['timestamps'].iloc[-1] + timedelta(days=1),
            periods=pred_days,
            freq='D'
        )
        
        return {
            'close_prices': predicted_prices,
            'high_prices': [p * 1.01 for p in predicted_prices],  # 简单的高价估计
            'low_prices': [p * 0.99 for p in predicted_prices],   # 简单的低价估计
            'upper_band': upper_band,
            'lower_band': lower_band,
            'volumes': predicted_volumes,
            'timestamps': future_dates.tolist()
        }


# 使用示例
if __name__ == "__main__":
    predictor = MultiMarketStockPredictor()
    
    # 搜索股票
    print("=== 股票搜索测试 ===")
    results = predictor.search_stocks("苹果")
    for result in results:
        print(f"{result['symbol']} - {result['cn_name']} ({result['en_name']}) - {result['market']}")
    
    print("\n=== 股票预测测试 ===")
    # 预测苹果股票
    prediction = predictor.predict_stock("AAPL", "us_stocks", pred_days=5)
    if prediction['success']:
        print(f"股票: {prediction['symbol']} ({prediction['market']})")
        print(f"当前价格: ${prediction['current_price']}")
        print(f"预测模型: {prediction['model_used']}")
        print(f"趋势: {prediction['summary']['trend']}")
        print(f"预计{prediction['prediction_days']}天后价格: ${prediction['summary']['final_price']}")
        print(f"预计涨跌幅: {prediction['summary']['total_change_pct']}%")
    else:
        print(f"预测失败: {prediction['error']}")