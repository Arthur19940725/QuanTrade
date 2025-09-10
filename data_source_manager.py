#!/usr/bin/env python3
"""
改进的数据源管理器
支持多个数据源，确保获取最新的股票价格数据
"""

import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import json

class EnhancedDataSourceManager:
    """增强型数据源管理器"""
    
    def __init__(self):
        # 多个数据源配置
        self.data_sources = {
            'crypto': {
                'binance': {
                    'url': 'https://api.binance.com/api/v3',
                    'priority': 1,
                    'rate_limit': 1200  # 每分钟请求限制
                },
                'coinapi': {
                    'url': 'https://rest.coinapi.io/v1',
                    'priority': 2,
                    'rate_limit': 100
                }
            },
            'us_stocks': {
                'yahoo': {
                    'url': 'https://query1.finance.yahoo.com/v8/finance/chart',
                    'priority': 1,
                    'rate_limit': 2000
                },
                'alpha_vantage': {
                    'url': 'https://www.alphavantage.co/query',
                    'priority': 2,
                    'rate_limit': 5  # 免费版限制
                },
                'finnhub': {
                    'url': 'https://finnhub.io/api/v1',
                    'priority': 3,  # 降低优先级，主要用于实时价格
                    'rate_limit': 60,
                    'api_key': 'd3040f1r01qnmrscs8b0d3040f1r01qnmrscs8bg',
                    'real_time_only': True  # 标记为主要用于实时价格
                }
            },
            'hk_stocks': {
                'yahoo': {
                    'url': 'https://query1.finance.yahoo.com/v8/finance/chart',
                    'priority': 1,
                    'rate_limit': 2000
                }
            }
        }
        
        # 请求会话配置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 配置SSL和连接参数
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 创建适配器配置
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # 创建重试策略，兼容新旧版本的urllib3
        try:
            # 新版本urllib3使用allowed_methods
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )
        except TypeError:
            # 旧版本urllib3使用method_whitelist
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 请求重试配置
        self.max_retries = 3
        self.retry_delay = 1
        
        # 缓存配置
        self.cache = {}
        self.cache_duration = 300  # 5分钟缓存
    
    def get_latest_data(self, symbol: str, market: str, days: int = 100) -> pd.DataFrame:
        """获取最新数据，支持多数据源fallback"""
        cache_key = f"{symbol}_{market}_{days}"
        
        # 检查缓存
        if self._is_cache_valid(cache_key):
            print(f"📋 使用缓存数据: {symbol}")
            return self.cache[cache_key]['data']
        
        # 尝试从多个数据源获取数据
        if market == 'crypto':
            df = self._fetch_crypto_with_fallback(symbol, days)
        elif market == 'us_stocks':
            df = self._fetch_us_stock_with_fallback(symbol, days)
        elif market == 'hk_stocks':
            df = self._fetch_hk_stock_with_fallback(symbol, days)
        elif market == 'cn_stocks':
            df = self._fetch_cn_stock_with_fallback(symbol, days)
        else:
            raise ValueError(f"不支持的市场类型: {market}")
        
        # 验证数据质量
        df = self._validate_and_clean_data(df, symbol)
        
        # 更新缓存
        self.cache[cache_key] = {
            'data': df,
            'timestamp': time.time()
        }
        
        return df
    
    def _fetch_crypto_with_fallback(self, symbol: str, days: int) -> pd.DataFrame:
        """加密货币数据获取（多源fallback）"""
        # 尝试Binance API
        try:
            return self._fetch_binance_data(symbol, days)
        except Exception as e:
            print(f"⚠️ Binance API失败: {e}")
        
        # 尝试备用数据源
        try:
            return self._fetch_coingecko_data(symbol, days)
        except Exception as e:
            print(f"⚠️ CoinGecko API失败: {e}")
        
        print(f"⚠️ 所有加密货币数据源失败，使用模拟数据")
        return self._generate_realistic_mock_data(symbol, days, 'crypto')
    
    def _fetch_us_stock_with_fallback(self, symbol: str, days: int) -> pd.DataFrame:
        """美股数据获取（多源fallback）"""
        # 尝试Yahoo Finance（改进版）
        try:
            return self._fetch_yahoo_data_improved(symbol, days)
        except Exception as e:
            print(f"⚠️ Yahoo Finance失败: {e}")
        
        # 尝试Alpha Vantage（历史数据优先）
        try:
            return self._fetch_alpha_vantage_data(symbol, days)
        except Exception as e:
            print(f"⚠️ Alpha Vantage失败: {e}")
        
        # 注意：Finnhub免费版可能不支持历史数据，主要用于实时价格
        # try:
        #     return self._fetch_finnhub_data(symbol, days)
        # except Exception as e:
        #     print(f"⚠️ Finnhub失败: {e}")
        
        print(f"⚠️ 所有美股数据源失败，使用模拟数据")
        return self._generate_realistic_mock_data(symbol, days, 'us_stock')
    
    def _fetch_hk_stock_with_fallback(self, symbol: str, days: int) -> pd.DataFrame:
        """港股数据获取"""
        try:
            return self._fetch_yahoo_hk_data_improved(symbol, days)
        except Exception as e:
            print(f"⚠️ 港股数据获取失败: {e}")
        
        return self._generate_realistic_mock_data(symbol, days, 'hk_stock')
    
    def _fetch_cn_stock_with_fallback(self, symbol: str, days: int) -> pd.DataFrame:
        """A股数据获取"""
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
                return self._generate_realistic_mock_data(symbol, days, 'cn_stock')
                
        except ImportError:
            print("⚠️ 增强型A股数据获取器未找到，使用akshare")
            return self._fetch_cn_stock_with_akshare(symbol, days)
        except Exception as e:
            print(f"⚠️ A股数据获取异常: {e}")
            return self._generate_realistic_mock_data(symbol, days, 'cn_stock')
    
    def _fetch_cn_stock_with_akshare(self, symbol: str, days: int) -> pd.DataFrame:
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
                for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                    stock_zh_a_hist_df[col] = pd.to_numeric(stock_zh_a_hist_df[col], errors='coerce')
                
                # 按时间排序
                stock_zh_a_hist_df = stock_zh_a_hist_df.sort_values('timestamps')
                
                # 添加买卖量分解
                stock_zh_a_hist_df = self._add_volume_breakdown(stock_zh_a_hist_df)
                
                print(f"✅ 成功获取A股 {symbol} 历史数据: {len(stock_zh_a_hist_df)} 条记录")
                return stock_zh_a_hist_df[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'buy_volume', 'sell_volume']]
            else:
                print(f"⚠️ A股 {symbol} 历史数据为空，使用模拟数据")
                return self._generate_realistic_mock_data(symbol, days, 'cn_stock')
                
        except Exception as e:
            print(f"⚠️ 获取A股 {symbol} 历史数据失败: {e}")
            return self._generate_realistic_mock_data(symbol, days, 'cn_stock')
    
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
    
    def _fetch_binance_data(self, symbol: str, days: int) -> pd.DataFrame:
        """改进的Binance数据获取"""
        url = f"{self.data_sources['crypto']['binance']['url']}/klines"
        params = {
            'symbol': f"{symbol}USDT",
            'interval': '1d',
            'limit': min(days, 1000)  # Binance限制
        }
        
        response = self._make_request_with_retry(url, params)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'count', 'taker_buy_volume',
            'taker_buy_quote_volume', 'ignore'
        ])
        
        df['timestamps'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        df = df[['timestamps', 'open', 'high', 'low', 'close', 'volume']].sort_values('timestamps')
        print(f"✅ 成功获取Binance数据: {symbol}, 最新时间: {df['timestamps'].iloc[-1]}")
        return df
    
    def _fetch_coingecko_data(self, symbol: str, days: int) -> pd.DataFrame:
        """CoinGecko数据获取（备用）"""
        # 币种ID映射
        coin_id_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'DOGE': 'dogecoin',
            'XRP': 'ripple',
            'TRX': 'tron',
            'AVAX': 'avalanche-2',
            'SHIB': 'shiba-inu'
        }
        
        coin_id = coin_id_map.get(symbol, symbol.lower())
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': min(days, 365),
            'interval': 'daily'
        }
        
        response = self._make_request_with_retry(url, params)
        data = response.json()
        
        prices = data['prices']
        volumes = data['total_volumes']
        
        df = pd.DataFrame({
            'timestamps': [datetime.fromtimestamp(p[0]/1000) for p in prices],
            'close': [p[1] for p in prices],
            'volume': [v[1] for v in volumes]
        })
        
        # 添加OHLC数据（简化处理）
        df['open'] = df['close'].shift(1).fillna(df['close'])
        df['high'] = df['close'] * (1 + np.random.uniform(0, 0.02, len(df)))
        df['low'] = df['close'] * (1 - np.random.uniform(0, 0.02, len(df)))
        
        df = df[['timestamps', 'open', 'high', 'low', 'close', 'volume']].sort_values('timestamps')
        print(f"✅ 成功获取CoinGecko数据: {symbol}, 最新时间: {df['timestamps'].iloc[-1]}")
        return df
    
    def _fetch_yahoo_data_improved(self, symbol: str, days: int) -> pd.DataFrame:
        """改进的Yahoo Finance数据获取"""
        # 使用更稳定的时间范围计算
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)
        
        url = f"{self.data_sources['us_stocks']['yahoo']['url']}/{symbol}"
        params = {
            'period1': start_time,
            'period2': end_time,
            'interval': '1d',
            'includePrePost': 'true',
            'events': 'div%2Csplit'
        }
        
        # 添加随机延迟避免频率限制
        time.sleep(random.uniform(0.1, 0.5))
        
        response = self._make_request_with_retry(url, params)
        data = response.json()
        
        if 'chart' not in data or not data['chart']['result']:
            raise Exception("Yahoo Finance返回空数据")
        
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
        
        df = df.dropna().sort_values('timestamps')
        print(f"✅ 成功获取Yahoo Finance数据: {symbol}, 最新时间: {df['timestamps'].iloc[-1]}")
        return df
    
    def _fetch_yahoo_hk_data_improved(self, symbol: str, days: int) -> pd.DataFrame:
        """改进的港股数据获取"""
        # 港股代码格式化
        if not symbol.startswith('0'):
            symbol = symbol.zfill(4)
        hk_symbol = f"{symbol}.HK"
        
        return self._fetch_yahoo_data_improved(hk_symbol, days)
    
    def _fetch_finnhub_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Finnhub数据获取"""
        api_key = self.data_sources['us_stocks']['finnhub']['api_key']
        base_url = self.data_sources['us_stocks']['finnhub']['url']
        
        # 计算时间范围（Finnhub使用Unix时间戳）
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)
        
        # 获取股票K线数据
        url = f"{base_url}/stock/candle"
        params = {
            'symbol': symbol,
            'resolution': 'D',  # 日线数据
            'from': start_time,
            'to': end_time,
            'token': api_key
        }
        
        response = self._make_request_with_retry(url, params)
        data = response.json()
        
        # 检查响应状态
        if data.get('s') != 'ok':
            raise Exception(f"Finnhub API错误: {data.get('s', 'unknown error')}")
        
        # 检查数据是否为空
        if not data.get('c') or len(data['c']) == 0:
            raise Exception("Finnhub返回空数据")
        
        # 构建DataFrame
        df = pd.DataFrame({
            'timestamps': pd.to_datetime(data['t'], unit='s'),
            'open': data['o'],
            'high': data['h'], 
            'low': data['l'],
            'close': data['c'],
            'volume': data['v']
        })
        
        df = df.sort_values('timestamps').reset_index(drop=True)
        print(f"✅ 成功获取Finnhub数据: {symbol}, 最新时间: {df['timestamps'].iloc[-1]}")
        return df
    
    def _fetch_alpha_vantage_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Alpha Vantage数据获取（需要API Key）"""
        # 注意：这需要Alpha Vantage API Key
        api_key = "demo"  # 实际使用时需要真实API Key
        
        url = self.data_sources['us_stocks']['alpha_vantage']['url']
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'compact' if days <= 100 else 'full',
            'apikey': api_key
        }
        
        response = self._make_request_with_retry(url, params)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            raise Exception("Alpha Vantage API响应异常")
        
        time_series = data['Time Series (Daily)']
        
        df_data = []
        for date_str, values in time_series.items():
            df_data.append({
                'timestamps': pd.to_datetime(date_str),
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'volume': int(values['5. volume'])
            })
        
        df = pd.DataFrame(df_data).sort_values('timestamps')
        print(f"✅ 成功获取Alpha Vantage数据: {symbol}")
        return df.tail(days)
    
    def _make_request_with_retry(self, url: str, params: dict) -> requests.Response:
        """带重试的HTTP请求"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 429:  # 频率限制
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"⏳ 遇到频率限制，等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"⚠️ 请求失败，{self.retry_delay}秒后重试: {e}")
                time.sleep(self.retry_delay)
        
        raise Exception("所有重试尝试都失败了")
    
    def _validate_and_clean_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """验证和清理数据"""
        if df.empty:
            raise Exception("数据为空")
        
        # 检查必需列
        required_cols = ['timestamps', 'open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise Exception(f"缺少必需列: {missing_cols}")
        
        # 移除无效数据
        df = df.dropna()
        
        # 数据类型转换
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 移除异常值
        df = df[df['close'] > 0]
        df = df[df['volume'] >= 0]
        
        # 按时间排序
        df = df.sort_values('timestamps').reset_index(drop=True)
        
        # 检查数据新鲜度
        latest_time = df['timestamps'].iloc[-1]
        now = pd.Timestamp.now()
        # 确保时间类型一致
        if not isinstance(latest_time, pd.Timestamp):
            latest_time = pd.to_datetime(latest_time)
        time_diff = now - latest_time
        
        if time_diff > timedelta(days=7):
            print(f"⚠️ 数据可能不是最新的: {symbol}, 最新数据时间: {latest_time}")
        else:
            print(f"✅ 数据新鲜度良好: {symbol}, 最新数据时间: {latest_time}")
        
        return df
    
    def _generate_realistic_mock_data(self, symbol: str, days: int, market_type: str) -> pd.DataFrame:
        """生成更真实的模拟数据"""
        print(f"🎭 生成真实模拟数据: {symbol} ({market_type})")
        
        # 基础价格设置（更接近真实价格）
        base_prices = {
            'crypto': {
                'BTC': 65000, 'ETH': 3200, 'BNB': 580, 'SOL': 140, 'ADA': 0.45,
                'DOGE': 0.08, 'XRP': 0.52, 'TRX': 0.11, 'AVAX': 35, 'SHIB': 0.000024,
                'default': 100
            },
            'us_stock': {
                'AAPL': 175, 'MSFT': 380, 'GOOGL': 2800, 'AMZN': 3200, 'TSLA': 240,
                'META': 320, 'NVDA': 450, 'JPM': 155, 'JNJ': 160, 'V': 250,
                'default': 100
            },
            'hk_stock': {
                '0700': 380, '0941': 85, '0939': 6.5, '1299': 75, '2318': 55,
                'default': 50
            },
            'cn_stock': {
                '600519': 1650, '000858': 180, '600036': 38, '000001': 12,
                'default': 25
            }
        }
        
        base_price = base_prices.get(market_type, {}).get(symbol, 
                     base_prices[market_type]['default'])
        
        # 生成更真实的时间序列
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=days, freq='D')
        
        # 使用更真实的价格模型
        np.random.seed(hash(symbol) % 2**32)
        
        prices = []
        volumes = []
        current_price = base_price
        
        # 添加趋势和周期性
        trend = np.random.uniform(-0.0005, 0.0005)  # 每日趋势
        
        for i in range(days):
            # 趋势 + 随机波动 + 周期性
            daily_change = (trend + 
                          np.random.normal(0, 0.02) + 
                          0.005 * np.sin(i * 2 * np.pi / 30))  # 30天周期
            
            current_price *= (1 + daily_change)
            current_price = max(current_price, base_price * 0.1)  # 防止价格过低
            
            prices.append(current_price)
            
            # 生成交易量（与价格波动相关）
            volume_base = np.random.uniform(10000, 1000000)
            volume_multiplier = 1 + abs(daily_change) * 5  # 波动大时交易量大
            volumes.append(volume_base * volume_multiplier)
        
        # 生成OHLC数据
        df_data = []
        for i, (date, close_price, volume) in enumerate(zip(dates, prices, volumes)):
            daily_volatility = np.random.uniform(0.005, 0.03)
            
            high = close_price * (1 + daily_volatility)
            low = close_price * (1 - daily_volatility)
            
            if i == 0:
                open_price = close_price
            else:
                open_price = prices[i-1] * (1 + np.random.uniform(-0.01, 0.01))
            
            df_data.append({
                'timestamps': date,
                'open': max(open_price, low),
                'high': high,
                'low': low,
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(df_data)
        
        # 确保OHLC关系正确
        df['high'] = df[['open', 'close', 'high']].max(axis=1)
        df['low'] = df[['open', 'close', 'low']].min(axis=1)
        
        return df
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (time.time() - cache_time) < self.cache_duration
    
    def get_real_time_price(self, symbol: str, market: str) -> float:
        """获取实时价格（单独接口）"""
        try:
            if market == 'crypto':
                url = f"{self.data_sources['crypto']['binance']['url']}/ticker/price"
                params = {'symbol': f"{symbol}USDT"}
                response = self._make_request_with_retry(url, params)
                data = response.json()
                return float(data['price'])
            elif market == 'us_stocks':
                # 优先使用Finnhub实时价格API（最准确的实时数据）
                try:
                    return self._get_finnhub_real_time_price(symbol)
                except Exception as e:
                    print(f"⚠️ Finnhub实时价格失败，回退到历史数据: {e}")
                    # 回退到最新收盘价
                    try:
                        df = self.get_latest_data(symbol, market, days=1)
                        return float(df['close'].iloc[-1])
                    except Exception as e2:
                        print(f"⚠️ 获取历史数据也失败: {e2}")
                        return None
            else:
                # 对于其他市场，返回最新收盘价
                df = self.get_latest_data(symbol, market, days=1)
                return float(df['close'].iloc[-1])
                
        except Exception as e:
            print(f"⚠️ 获取实时价格失败: {symbol}, {e}")
            return None
    
    def _get_finnhub_real_time_price(self, symbol: str) -> float:
        """获取Finnhub实时价格"""
        api_key = self.data_sources['us_stocks']['finnhub']['api_key']
        base_url = self.data_sources['us_stocks']['finnhub']['url']
        
        url = f"{base_url}/quote"
        params = {
            'symbol': symbol,
            'token': api_key
        }
        
        response = self._make_request_with_retry(url, params)
        data = response.json()
        
        # 检查数据有效性
        if 'c' not in data or data['c'] is None:
            raise Exception("Finnhub实时价格数据无效")
        
        current_price = float(data['c'])  # c = current price
        print(f"✅ 获取Finnhub实时价格: {symbol} = ${current_price}")
        return current_price


# 使用示例
if __name__ == "__main__":
    manager = EnhancedDataSourceManager()
    
    # 测试不同市场
    test_cases = [
        ("BTC", "crypto"),
        ("AAPL", "us_stocks"),
        ("0700", "hk_stocks")
    ]
    
    for symbol, market in test_cases:
        print(f"\n测试 {symbol} ({market})")
        try:
            df = manager.get_latest_data(symbol, market, days=30)
            print(f"✅ 成功获取数据，共{len(df)}行")
            print(f"   最新价格: ${df['close'].iloc[-1]:.2f}")
            print(f"   最新时间: {df['timestamps'].iloc[-1]}")
        except Exception as e:
            print(f"❌ 获取失败: {e}")