#!/usr/bin/env python3
"""
创建虚拟数据文件，避免内存问题
"""

from datetime import datetime
import os
import pickle

import numpy as np
import pandas as pd


def create_dummy_data():
    """创建虚拟的股票数据用于测试"""
    print("Creating dummy data for testing...")

    # 创建时间序列
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2020, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # 创建一些虚拟股票数据
    symbols = ['sz000001', 'sz000002', 'sz000858', 'sz002415', 'sz300001']

    data = {}

    for symbol in symbols:
        print(f"Creating data for {symbol}...")

        # 生成随机价格数据
        np.random.seed(hash(symbol) % 2**32)  # 确保每个股票的数据是固定的

        n_days = len(dates)
        base_price = 10.0 + np.random.random() * 50  # 基础价格

        # 生成价格序列（随机游走）
        returns = np.random.normal(0, 0.02, n_days)  # 2% 日波动率
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        # 创建 OHLCV 数据
        df = pd.DataFrame(index=dates)
        df['open'] = prices
        df['high'] = [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices]
        df['low'] = [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices]
        df['close'] = [p * (1 + np.random.normal(0, 0.005)) for p in prices]
        df['volume'] = np.random.randint(1000000, 10000000, n_days)
        df['vwap'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

        # 添加 Kronos 需要的字段
        df['vol'] = df['volume']
        df['amt'] = df['vwap'] * df['vol']

        # 选择最终特征
        feature_list = ['open', 'high', 'low', 'close', 'vol', 'amt']
        df = df[feature_list]

        # 添加时间戳
        df['timestamps'] = df.index

        data[symbol] = df

    return data

def split_data(data):
    """将数据分割为训练、验证和测试集"""
    print("Splitting data into train/val/test sets...")

    train_data, val_data, test_data = {}, {}, {}

    # 定义时间范围
    train_start = "2020-01-01"
    train_end = "2020-08-31"
    val_start = "2020-09-01"
    val_end = "2020-10-31"
    test_start = "2020-11-01"
    test_end = "2020-12-31"

    for symbol, df in data.items():
        # 创建时间掩码
        train_mask = (df.index >= train_start) & (df.index <= train_end)
        val_mask = (df.index >= val_start) & (df.index <= val_end)
        test_mask = (df.index >= test_start) & (df.index <= test_end)

        # 分割数据
        train_data[symbol] = df[train_mask]
        val_data[symbol] = df[val_mask]
        test_data[symbol] = df[test_mask]

    return train_data, val_data, test_data

def main():
    """主函数"""
    print("=== 创建虚拟数据文件 ===")

    # 创建数据
    data = create_dummy_data()
    print(f"Created data for {len(data)} symbols")

    # 分割数据
    train_data, val_data, test_data = split_data(data)

    # 保存数据
    dataset_path = "../data/processed_datasets"
    os.makedirs(dataset_path, exist_ok=True)

    print(f"Saving data to {dataset_path}...")

    with open(f"{dataset_path}/train_data.pkl", 'wb') as f:
        pickle.dump(train_data, f)
    print(f"Saved train data: {len(train_data)} symbols")

    with open(f"{dataset_path}/val_data.pkl", 'wb') as f:
        pickle.dump(val_data, f)
    print(f"Saved validation data: {len(val_data)} symbols")

    with open(f"{dataset_path}/test_data.pkl", 'wb') as f:
        pickle.dump(test_data, f)
    print(f"Saved test data: {len(test_data)} symbols")

    print("✅ Data creation completed successfully!")
    print("\nYou can now use these data files for training without memory issues.")

if __name__ == "__main__":
    main()
