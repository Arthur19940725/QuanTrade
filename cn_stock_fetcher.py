#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据抓取器（移除 OpenBB 依赖）
- 优先使用 TuShare（需 TUSHARE_TOKEN）
- 备用使用 yfinance（通过 Yahoo China 后缀）
- 预留 tkshare/akshare 接口
输出统一为 DataFrame 列: ['timestamps','open','high','low','close','volume','buy_volume','sell_volume']
"""

import time
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

# 全局 TuShare Token（非环境变量）
TUSHARE_TOKEN: Optional[str] = None

def set_tushare_token(token: str) -> None:
    """设置全局 TuShare Token"""
    global TUSHARE_TOKEN
    TUSHARE_TOKEN = token

class CNStockFetcher:
    """A股历史数据抓取，TuShare -> yfinance 回退"""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 秒
        self._tushare = None

        if TUSHARE_TOKEN:
            try:
                import tushare as ts  # type: ignore
                ts.set_token(TUSHARE_TOKEN)
                self._tushare = ts.pro_api()
            except Exception:
                self._tushare = None

    # --------------- public API ---------------
    def get_historical(self, symbol: str, days: int = 100) -> pd.DataFrame:
        key = f"hist:{symbol}:{days}"
        if self._is_cache_valid(key):
            return self.cache[key]['data']

        df = self._fetch_with_fallback(symbol, days)
        df = self._normalize_df(df)
        self.cache[key] = {"data": df, "ts": time.time()}
        return df

    # --------------- internal ---------------
    def _fetch_with_fallback(self, symbol: str, days: int) -> pd.DataFrame:
        # 1) TuShare 优先
        if self._tushare is not None:
            try:
                df = self._fetch_tushare(symbol, days)
                if not df.empty:
                    return df
            except Exception:
                pass
        # 2) yfinance 备用
        try:
            df = self._fetch_yfinance(symbol, days)
            if not df.empty:
                return df
        except Exception:
            pass
        # 3) 预留 akshare/tkshare（未来可补充）
        return pd.DataFrame()

    def _fetch_tushare(self, symbol: str, days: int) -> pd.DataFrame:
        ts_code = self._to_tushare_code(symbol)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
        df = self._tushare.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return pd.DataFrame()
        # TuShare: trade_date desc 排序
        df = df.sort_values('trade_date')
        out = pd.DataFrame({
            'timestamps': pd.to_datetime(df['trade_date']),
            'open': df['open'].astype(float),
            'high': df['high'].astype(float),
            'low': df['low'].astype(float),
            'close': df['close'].astype(float),
            'volume': (df['vol'] * 100).astype(float) if 'vol' in df.columns else df['vol'].astype(float),
        })
        out['buy_volume'] = 0.0
        out['sell_volume'] = 0.0
        # 裁剪至 days
        if len(out) > days:
            out = out.iloc[-days:]
        return out.reset_index(drop=True)

    def _fetch_yfinance(self, symbol: str, days: int) -> pd.DataFrame:
        import yfinance as yf  # type: ignore
        yf_symbol = self._to_yahoo_code(symbol)
        period_days = max(days + 5, 30)
        data = yf.Ticker(yf_symbol).history(period=f"{period_days}d")
        if data is None or data.empty:
            return pd.DataFrame()
        data = data.reset_index()
        data.rename(columns={
            'Date': 'timestamps',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
        }, inplace=True)
        out = data[['timestamps','open','high','low','close','volume']].copy()
        out['buy_volume'] = 0.0
        out['sell_volume'] = 0.0
        if len(out) > days:
            out = out.iloc[-days:]
        return out.reset_index(drop=True)

    def _normalize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = ['timestamps','open','high','low','close','volume','buy_volume','sell_volume']
        if df is None or df.empty:
            return pd.DataFrame(columns=cols)
        # 强制列存在
        for c in cols:
            if c not in df.columns:
                df[c] = 0.0 if c != 'timestamps' else pd.NaT
        df = df[cols].copy()
        # 时间戳统一为 ISO8601 字符串
        df['timestamps'] = pd.to_datetime(df['timestamps']).dt.tz_localize(None)
        return df

    def _is_cache_valid(self, key: str) -> bool:
        item = self.cache.get(key)
        return bool(item and (time.time() - item['ts'] < self.cache_ttl))

    # --------------- code helpers ---------------
    @staticmethod
    def _to_tushare_code(symbol: str) -> str:
        if symbol.startswith(('600','601','603','605','688')):
            return f"{symbol}.SH"
        if symbol.startswith(('000','001','002','300')):
            return f"{symbol}.SZ"
        return symbol

    @staticmethod
    def _to_yahoo_code(symbol: str) -> str:
        if symbol.startswith(('600','601','603','605','688')):
            return f"{symbol}.SS"
        if symbol.startswith(('000','001','002','300')):
            return f"{symbol}.SZ"
        return symbol