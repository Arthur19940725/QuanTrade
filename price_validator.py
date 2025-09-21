#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格数据验证和修复模块
解决历史价格不准确、不符合历史规律的问题
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings

class PriceValidator:
    """价格数据验证和修复器"""
    
    def __init__(self):
        # 价格异常检测阈值
        self.price_change_threshold = 0.2  # 20%的日涨跌幅阈值
        self.volume_spike_threshold = 5.0  # 5倍成交量异常阈值
        self.price_gap_threshold = 0.1     # 10%的价格跳空阈值
        
        # 不同市场的价格范围限制
        self.price_limits = {
            'crypto': {'min': 0.000001, 'max': 1000000},
            'us_stocks': {'min': 0.01, 'max': 10000},
            'hk_stocks': {'min': 0.01, 'max': 10000},
            'cn_stocks': {'min': 0.01, 'max': 10000}
        }
        
    def validate_and_fix_prices(self, df: pd.DataFrame, symbol: str, market: str) -> pd.DataFrame:
        """验证和修复价格数据"""
        if df.empty:
            return df
            
        print(f"🔍 开始验证 {symbol} ({market}) 价格数据...")
        
        # 1. 基础数据验证
        df = self._validate_basic_data(df)
        
        # 2. OHLC关系验证和修复
        df = self._validate_ohlc_relationships(df)
        
        # 3. 价格连续性验证
        df = self._validate_price_continuity(df, market)
        
        # 4. 异常值检测和修复
        df = self._detect_and_fix_outliers(df, market)
        
        # 5. 成交量异常检测
        df = self._validate_volume_data(df)
        
        # 6. 价格范围验证
        df = self._validate_price_ranges(df, market)
        
        # 7. 时间序列完整性检查
        df = self._validate_time_series(df)
        
        print(f"✅ {symbol} 价格数据验证完成")
        return df
    
    def _validate_basic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """基础数据验证"""
        # 确保必需列存在
        required_cols = ['timestamps', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必需列: {col}")
        
        # 移除完全空的行
        df = df.dropna(how='all')
        
        # 数据类型转换
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 移除包含NaN的行
        df = df.dropna(subset=['timestamps', 'open', 'high', 'low', 'close'])
        
        return df
    
    def _validate_ohlc_relationships(self, df: pd.DataFrame) -> pd.DataFrame:
        """验证和修复OHLC关系"""
        print("  📊 验证OHLC关系...")
        
        # 检查High >= Low
        invalid_high_low = df['high'] < df['low']
        if invalid_high_low.any():
            print(f"    ⚠️ 发现 {invalid_high_low.sum()} 条High < Low的记录，正在修复...")
            df.loc[invalid_high_low, 'high'] = df.loc[invalid_high_low, 'low']
        
        # 检查High >= Open
        invalid_high_open = df['high'] < df['open']
        if invalid_high_open.any():
            print(f"    ⚠️ 发现 {invalid_high_open.sum()} 条High < Open的记录，正在修复...")
            df.loc[invalid_high_open, 'high'] = df.loc[invalid_high_open, 'open']
        
        # 检查High >= Close
        invalid_high_close = df['high'] < df['close']
        if invalid_high_close.any():
            print(f"    ⚠️ 发现 {invalid_high_close.sum()} 条High < Close的记录，正在修复...")
            df.loc[invalid_high_close, 'high'] = df.loc[invalid_high_close, 'close']
        
        # 检查Low <= Open
        invalid_low_open = df['low'] > df['open']
        if invalid_low_open.any():
            print(f"    ⚠️ 发现 {invalid_low_open.sum()} 条Low > Open的记录，正在修复...")
            df.loc[invalid_low_open, 'low'] = df.loc[invalid_low_open, 'open']
        
        # 检查Low <= Close
        invalid_low_close = df['low'] > df['close']
        if invalid_low_close.any():
            print(f"    ⚠️ 发现 {invalid_low_close.sum()} 条Low > Close的记录，正在修复...")
            df.loc[invalid_low_close, 'low'] = df.loc[invalid_low_close, 'close']
        
        return df
    
    def _validate_price_continuity(self, df: pd.DataFrame, market: str) -> pd.DataFrame:
        """验证价格连续性，检测异常跳空"""
        print("  🔗 验证价格连续性...")
        
        if len(df) < 2:
            return df
        
        # 计算价格变化率
        df['price_change'] = df['close'].pct_change()
        
        # 检测异常跳空（超过阈值的变化）
        extreme_changes = abs(df['price_change']) > self.price_change_threshold
        
        if extreme_changes.any():
            print(f"    ⚠️ 发现 {extreme_changes.sum()} 条异常价格变化记录")
            
            # 对于异常变化，使用前一日价格进行平滑处理
            for idx in df[extreme_changes].index:
                if idx > 0:
                    prev_close = df.loc[idx - 1, 'close']
                    change_factor = 1 + np.random.normal(0, 0.02)  # 添加小幅随机变化
                    new_close = prev_close * change_factor
                    
                    # 更新OHLC，保持一致性
                    df.loc[idx, 'close'] = new_close
                    df.loc[idx, 'high'] = max(df.loc[idx, 'high'], new_close)
                    df.loc[idx, 'low'] = min(df.loc[idx, 'low'], new_close)
        
        return df
    
    def _detect_and_fix_outliers(self, df: pd.DataFrame, market: str) -> pd.DataFrame:
        """检测和修复异常值"""
        print("  🎯 检测异常值...")
        
        if len(df) < 10:  # 数据太少，跳过异常值检测
            return df
        
        # 使用Z-score检测异常值
        for col in ['open', 'high', 'low', 'close']:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = z_scores > 3  # 3个标准差外的值
            
            if outliers.any():
                print(f"    ⚠️ 在 {col} 列发现 {outliers.sum()} 个异常值")
                
                # 使用中位数替换异常值
                median_value = df[col].median()
                df.loc[outliers, col] = median_value
        
        # 重新验证OHLC关系
        df = self._validate_ohlc_relationships(df)
        
        return df
    
    def _validate_volume_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """验证成交量数据"""
        print("  📈 验证成交量数据...")
        
        if 'volume' not in df.columns:
            return df
        
        # 检查负成交量
        negative_volume = df['volume'] < 0
        if negative_volume.any():
            print(f"    ⚠️ 发现 {negative_volume.sum()} 条负成交量记录，正在修复...")
            df.loc[negative_volume, 'volume'] = 0
        
        # 检测成交量异常峰值
        if len(df) > 5:
            volume_median = df['volume'].median()
            volume_std = df['volume'].std()
            
            # 成交量超过中位数+3倍标准差的值视为异常
            volume_outliers = df['volume'] > (volume_median + 3 * volume_std)
            
            if volume_outliers.any():
                print(f"    ⚠️ 发现 {volume_outliers.sum()} 条成交量异常记录")
                # 将异常成交量限制在合理范围内
                max_reasonable_volume = volume_median * 3
                df.loc[volume_outliers, 'volume'] = max_reasonable_volume
        
        return df
    
    def _validate_price_ranges(self, df: pd.DataFrame, market: str) -> pd.DataFrame:
        """验证价格范围"""
        print("  💰 验证价格范围...")
        
        if market not in self.price_limits:
            return df
        
        price_limits = self.price_limits[market]
        
        for col in ['open', 'high', 'low', 'close']:
            # 检查价格是否在合理范围内
            too_low = df[col] < price_limits['min']
            too_high = df[col] > price_limits['max']
            
            if too_low.any():
                print(f"    ⚠️ 发现 {too_low.sum()} 条 {col} 价格过低记录")
                df.loc[too_low, col] = price_limits['min']
            
            if too_high.any():
                print(f"    ⚠️ 发现 {too_high.sum()} 条 {col} 价格过高记录")
                df.loc[too_high, col] = price_limits['max']
        
        return df
    
    def _validate_time_series(self, df: pd.DataFrame) -> pd.DataFrame:
        """验证时间序列完整性"""
        print("  ⏰ 验证时间序列...")
        
        # 确保时间列是datetime类型
        df['timestamps'] = pd.to_datetime(df['timestamps'], errors='coerce')
        
        # 按时间排序
        df = df.sort_values('timestamps').reset_index(drop=True)
        
        # 检查时间序列是否单调递增
        if not df['timestamps'].is_monotonic_increasing:
            print("    ⚠️ 时间序列不单调，正在重新排序...")
            df = df.sort_values('timestamps').reset_index(drop=True)
        
        # 检查重复时间戳
        duplicate_times = df['timestamps'].duplicated()
        if duplicate_times.any():
            print(f"    ⚠️ 发现 {duplicate_times.sum()} 条重复时间戳，正在去重...")
            df = df.drop_duplicates(subset=['timestamps'], keep='last')
        
        return df
    
    def generate_price_report(self, df: pd.DataFrame, symbol: str) -> Dict:
        """生成价格数据质量报告"""
        if df.empty:
            return {"error": "数据为空"}
        
        report = {
            "symbol": symbol,
            "total_records": len(df),
            "date_range": {
                "start": df['timestamps'].min().strftime('%Y-%m-%d'),
                "end": df['timestamps'].max().strftime('%Y-%m-%d')
            },
            "price_stats": {
                "min_close": float(df['close'].min()),
                "max_close": float(df['close'].max()),
                "avg_close": float(df['close'].mean()),
                "price_volatility": float(df['close'].std())
            },
            "volume_stats": {
                "min_volume": float(df['volume'].min()),
                "max_volume": float(df['volume'].max()),
                "avg_volume": float(df['volume'].mean())
            },
            "data_quality": {
                "ohlc_consistent": self._check_ohlc_consistency(df),
                "no_outliers": self._check_outliers(df),
                "time_series_valid": df['timestamps'].is_monotonic_increasing
            }
        }
        
        return report
    
    def _check_ohlc_consistency(self, df: pd.DataFrame) -> bool:
        """检查OHLC一致性"""
        return all([
            (df['high'] >= df['low']).all(),
            (df['high'] >= df['open']).all(),
            (df['high'] >= df['close']).all(),
            (df['low'] <= df['open']).all(),
            (df['low'] <= df['close']).all()
        ])
    
    def _check_outliers(self, df: pd.DataFrame) -> bool:
        """检查是否有异常值"""
        if len(df) < 10:
            return True
        
        for col in ['open', 'high', 'low', 'close']:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            if (z_scores > 3).any():
                return False
        return True


def test_price_validator():
    """测试价格验证器"""
    print("🧪 测试价格验证器")
    print("=" * 50)
    
    # 创建测试数据
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    
    # 正常数据
    normal_prices = 100 + np.cumsum(np.random.normal(0, 2, 30))
    
    # 添加一些异常数据
    test_data = {
        'timestamps': dates,
        'open': normal_prices + np.random.normal(0, 1, 30),
        'high': normal_prices + np.random.uniform(0, 3, 30),
        'low': normal_prices - np.random.uniform(0, 3, 30),
        'close': normal_prices,
        'volume': np.random.uniform(1000, 10000, 30)
    }
    
    # 故意添加一些异常值
    test_data['high'][5] = test_data['low'][5] - 10  # High < Low
    test_data['close'][10] = test_data['close'][9] * 1.5  # 异常跳空
    test_data['volume'][15] = -1000  # 负成交量
    
    df = pd.DataFrame(test_data)
    
    # 使用验证器
    validator = PriceValidator()
    fixed_df = validator.validate_and_fix_prices(df, "TEST", "us_stocks")
    
    # 生成报告
    report = validator.generate_price_report(fixed_df, "TEST")
    
    print("📊 验证报告:")
    print(f"  总记录数: {report['total_records']}")
    print(f"  价格范围: ${report['price_stats']['min_close']:.2f} - ${report['price_stats']['max_close']:.2f}")
    print(f"  OHLC一致性: {report['data_quality']['ohlc_consistent']}")
    print(f"  无异常值: {report['data_quality']['no_outliers']}")
    print(f"  时间序列有效: {report['data_quality']['time_series_valid']}")


if __name__ == "__main__":
    test_price_validator()