import os
import pickle

from config import Config
import numpy as np
import pandas as pd
from tqdm import trange

import qlib
from qlib.config import REG_CN
from qlib.data import D
from qlib.data.dataset.loader import QlibDataLoader


class QlibDataPreprocessor:
    """
    A class to handle the loading, processing, and splitting of Qlib financial data.
    This is a memory-safe version that loads data in smaller chunks.
    """

    def __init__(self):
        """Initializes the preprocessor with configuration and data fields."""
        self.config = Config()
        self.data_fields = ['open', 'close', 'high', 'low', 'volume', 'vwap']
        self.data = {}  # A dictionary to store processed data for each symbol.

    def initialize_qlib(self):
        """Initializes the Qlib environment with memory-safe settings."""
        print("Initializing Qlib...")
        # 确保使用绝对路径 - 从 finetune 目录回到项目根目录
        import os
        abs_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", self.config.qlib_data_path))
        print(f"Using data path: {abs_data_path}")

        # 初始化 qlib 并指定频率
        qlib.init(
            provider_uri=abs_data_path,
            region=REG_CN,
            freq='day',  # 明确指定频率
            # 减少并行处理以避免内存问题
            joblib_backend='threading',  # 使用线程而不是进程
            n_jobs=1  # 限制并行作业数量
        )

    def load_qlib_data_safe(self, max_symbols=50):
        """
        安全地加载数据，限制处理的股票数量以避免内存问题
        """
        print("Loading and processing data from Qlib (safe mode)...")
        data_fields_qlib = ['$' + f for f in self.data_fields]

        try:
            # 尝试获取日历数据
            cal: np.ndarray = D.calendar()
            print(f"Successfully loaded calendar with {len(cal)} trading days")
        except Exception as e:
            print(f"Error loading calendar: {e}")
            print("Trying to load calendar with explicit frequency...")
            try:
                cal: np.ndarray = D.calendar(freq='day')
                print(f"Successfully loaded calendar with explicit frequency: {len(cal)} trading days")
            except Exception as e2:
                print(f"Failed to load calendar even with explicit frequency: {e2}")
                raise e2

        # 使用更短的时间范围来减少内存使用
        start_time = "2024-01-01"  # 只加载最近几年的数据
        end_time = "2024-12-31"

        print(f"Loading data from {start_time} to {end_time} (reduced time range for safety)")
        print(f"Using instrument: {self.config.instrument}")

        try:
            # 加载数据
            data_df = QlibDataLoader(config=data_fields_qlib).load(
                self.config.instrument, start_time, end_time
            )
            data_df = data_df.stack().unstack(level=1)  # Reshape for easier access.

            symbol_list = list(data_df.columns)
            print(f"Found {len(symbol_list)} symbols")

            # 限制处理的股票数量
            if len(symbol_list) > max_symbols:
                print(f"Limiting to first {max_symbols} symbols for memory safety")
                symbol_list = symbol_list[:max_symbols]

            for i in trange(len(symbol_list), desc="Processing Symbols"):
                symbol = symbol_list[i]
                symbol_df = data_df[symbol]

                # Pivot the table to have features as columns and datetime as index.
                symbol_df = symbol_df.reset_index().rename(columns={'level_1': 'field'})
                symbol_df = pd.pivot(symbol_df, index='datetime', columns='field', values=symbol)
                symbol_df = symbol_df.rename(columns={f'${field}': field for field in self.data_fields})

                # Calculate amount and select final features.
                symbol_df['vol'] = symbol_df['volume']
                symbol_df['amt'] = (symbol_df['open'] + symbol_df['high'] + symbol_df['low'] + symbol_df['close']) / 4 * symbol_df['vol']
                symbol_df = symbol_df[self.config.feature_list]

                # Filter out symbols with insufficient data.
                symbol_df = symbol_df.dropna()
                if len(symbol_df) < self.config.lookback_window + self.config.predict_window + 1:
                    continue

                self.data[symbol] = symbol_df
                print(f"Processed {symbol}: {len(symbol_df)} rows")

            print(f"Successfully processed {len(self.data)} symbols")

        except Exception as e:
            print(f"Error loading data: {e}")
            print("This might be due to memory limitations. Try reducing max_symbols or time range.")
            raise e

    def prepare_dataset(self):
        """
        Splits the loaded data into train, validation, and test sets and saves them to disk.
        """
        print("Splitting data into train, validation, and test sets...")
        train_data, val_data, test_data = {}, {}, {}

        symbol_list = list(self.data.keys())
        for i in trange(len(symbol_list), desc="Preparing Datasets"):
            symbol = symbol_list[i]
            symbol_df = self.data[symbol]

            # Define time ranges from config.
            train_start, train_end = self.config.train_time_range
            val_start, val_end = self.config.val_time_range
            test_start, test_end = self.config.test_time_range

            # Create boolean masks for each dataset split.
            train_mask = (symbol_df.index >= train_start) & (symbol_df.index <= train_end)
            val_mask = (symbol_df.index >= val_start) & (symbol_df.index <= val_end)
            test_mask = (symbol_df.index >= test_start) & (symbol_df.index <= test_end)

            # Apply masks to create the final datasets.
            train_data[symbol] = symbol_df[train_mask]
            val_data[symbol] = symbol_df[val_mask]
            test_data[symbol] = symbol_df[test_mask]

        # Save the datasets using pickle.
        os.makedirs(self.config.dataset_path, exist_ok=True)
        with open(f"{self.config.dataset_path}/train_data.pkl", 'wb') as f:
            pickle.dump(train_data, f)
        with open(f"{self.config.dataset_path}/val_data.pkl", 'wb') as f:
            pickle.dump(val_data, f)
        with open(f"{self.config.dataset_path}/test_data.pkl", 'wb') as f:
            pickle.dump(test_data, f)

        print("Datasets prepared and saved successfully.")


if __name__ == '__main__':
    # This block allows the script to be run directly to perform data preprocessing.
    print("Starting safe data preprocessing...")
    preprocessor = QlibDataPreprocessor()
    preprocessor.initialize_qlib()
    preprocessor.load_qlib_data_safe(max_symbols=20)  # 只处理20个股票
    preprocessor.prepare_dataset()
    print("Data preprocessing completed successfully!")
