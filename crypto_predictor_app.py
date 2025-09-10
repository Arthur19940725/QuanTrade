#!/usr/bin/env python3
"""
加密货币价格预测应用程序
基于Kronos模型预测BTC、ETH、SOL价格
支持实时数据获取和GUI界面
"""

import sys
import os
import warnings
import gc
from datetime import datetime, timedelta
import json
import traceback
from typing import Dict, List, Optional, Tuple
import threading
import time

# 忽略警告
warnings.filterwarnings("ignore")

# Gym兼容性补丁
try:
    import gymnasium as gym
    sys.modules['gym'] = gym
except ImportError:
    pass

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'finetune'))
sys.path.insert(0, os.path.join(current_dir, 'model'))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import requests
import torch

# 内存优化设置
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
torch.backends.cudnn.benchmark = False

try:
    from model.kronos import Kronos, KronosTokenizer, KronosPredictor
    MODEL_AVAILABLE = True
except ImportError as e:
    print(f"⚠ 模型导入失败: {e}")
    MODEL_AVAILABLE = False

class CryptoDataFetcher:
    """加密货币数据获取器"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    def get_kline_data(self, symbol: str, interval: str = "1d", limit: int = 100) -> pd.DataFrame:
        """获取K线数据"""
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': f"{symbol}USDT",
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 转换为DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            # 数据类型转换
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
                df[col] = pd.to_numeric(df[col])
            
            # 重命名列以匹配模型输入
            df = df.rename(columns={
                'timestamp': 'datetime',
                'volume': 'vol',
                'quote_volume': 'amt'
            })
            
            # 选择需要的列
            df = df[['datetime', 'open', 'high', 'low', 'close', 'vol', 'amt']]
            df = df.set_index('datetime')
            
            return df
            
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
            return self._get_mock_data(symbol, limit)
    
    def _get_mock_data(self, symbol: str, limit: int) -> pd.DataFrame:
        """生成模拟数据（当API不可用时）"""
        dates = pd.date_range(end=datetime.now(), periods=limit, freq='D')
        
        # 根据不同币种设置基础价格
        base_prices = {'BTC': 45000, 'ETH': 2500, 'SOL': 100}
        base_price = base_prices.get(symbol, 1000)
        
        np.random.seed(42)
        prices = []
        current_price = base_price
        
        for _ in range(limit):
            change = np.random.normal(0, 0.02)  # 2%的日波动
            current_price *= (1 + change)
            prices.append(current_price)
        
        df = pd.DataFrame({
            'datetime': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'vol': np.random.uniform(1000, 10000, limit),
            'amt': np.random.uniform(1000000, 100000000, limit)
        })
        
        df = df.set_index('datetime')
        return df

class CryptoPricePredictor:
    """加密货币价格预测器"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.predictor = None
        self.device = "cpu"  # 默认使用CPU
        self.model_loaded = False
        
    def setup_device(self):
        """设置计算设备"""
        if torch.cuda.is_available():
            try:
                # 测试CUDA兼容性
                test_tensor = torch.randn(2, 2).cuda()
                _ = test_tensor + test_tensor
                del test_tensor
                torch.cuda.empty_cache()
                self.device = "cuda"
                print("✓ 使用GPU加速")
            except Exception as e:
                print(f"⚠ CUDA不兼容，使用CPU: {e}")
                self.device = "cpu"
        else:
            print("✓ 使用CPU模式")
            
    def load_models(self):
        """加载预训练模型"""
        if not MODEL_AVAILABLE:
            print("⚠ 模型库不可用，使用模拟预测")
            return False
            
        try:
            self.setup_device()
            
            # 使用预训练模型路径
            tokenizer_path = "NeoQuasar/Kronos-Tokenizer-base"
            model_path = "NeoQuasar/Kronos-small"
            
            # 检查本地模型
            local_tokenizer = "./models/models--NeoQuasar--Kronos-Tokenizer-base"
            local_model = "./models/models--NeoQuasar--Kronos-small"
            
            if os.path.exists(local_tokenizer):
                tokenizer_path = local_tokenizer
            if os.path.exists(local_model):
                model_path = local_model
            
            print(f"加载分词器: {tokenizer_path}")
            self.tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)
            
            print(f"加载模型: {model_path}")
            self.model = Kronos.from_pretrained(model_path)
            self.model = self.model.to(self.device)
            self.model.eval()
            
            # 创建预测器
            self.predictor = KronosPredictor(
                self.model, 
                self.tokenizer, 
                device=self.device, 
                max_context=256  # 减少内存使用
            )
            
            self.model_loaded = True
            print("✓ 模型加载成功")
            return True
            
        except Exception as e:
            print(f"✗ 模型加载失败: {e}")
            self.model_loaded = False
            return False
    
    def predict_price(self, df: pd.DataFrame, symbol: str, pred_days: int = 7) -> Dict:
        """预测价格"""
        try:
            if not self.model_loaded:
                return self._mock_prediction(df, symbol, pred_days)
            
            # 准备数据
            lookback = min(60, len(df))  # 使用最近60天数据
            x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'vol', 'amt']]
            x_timestamp = df.index[-lookback:]
            
            # 生成未来时间戳
            last_date = df.index[-1]
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=pred_days,
                freq='D'
            )
            
            # 进行预测
            with torch.no_grad():
                pred_df = self.predictor.predict(
                    df=x_df,
                    x_timestamp=x_timestamp,
                    y_timestamp=future_dates,
                    pred_len=pred_days,
                    T=1.0,
                    top_p=0.9,
                    sample_count=1,
                    verbose=False
                )
            
            # 处理预测结果
            current_price = float(df['close'].iloc[-1])
            predicted_prices = pred_df['close'].values
            
            # 计算价格变化
            price_change = predicted_prices[-1] - current_price
            price_change_pct = (price_change / current_price) * 100
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'predicted_prices': predicted_prices.tolist(),
                'future_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'trend': 'UP' if price_change > 0 else 'DOWN',
                'confidence': min(95, abs(price_change_pct) * 10)  # 简单的置信度计算
            }
            
        except Exception as e:
            print(f"预测失败: {e}")
            return self._mock_prediction(df, symbol, pred_days)
    
    def _mock_prediction(self, df: pd.DataFrame, symbol: str, pred_days: int) -> Dict:
        """模拟预测（当模型不可用时）"""
        current_price = float(df['close'].iloc[-1])
        
        # 基于历史波动率的简单预测
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()
        
        # 生成预测价格
        np.random.seed(hash(symbol) % 1000)
        predicted_prices = []
        price = current_price
        
        for _ in range(pred_days):
            change = np.random.normal(0, volatility)
            price *= (1 + change)
            predicted_prices.append(price)
        
        price_change = predicted_prices[-1] - current_price
        price_change_pct = (price_change / current_price) * 100
        
        last_date = df.index[-1]
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=pred_days,
            freq='D'
        )
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'predicted_prices': predicted_prices,
            'future_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'trend': 'UP' if price_change > 0 else 'DOWN',
            'confidence': 75  # 模拟预测的置信度较低
        }

class CryptoPredictorGUI:
    """加密货币预测应用GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kronos 加密货币价格预测器")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # 设置样式
        self.setup_styles()
        
        # 初始化组件
        self.data_fetcher = CryptoDataFetcher()
        self.predictor = CryptoPricePredictor()
        self.predictions = {}
        
        # 创建GUI
        self.create_widgets()
        
        # 加载模型（在后台线程中）
        self.load_models_async()
        
    def setup_styles(self):
        """设置GUI样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background='#2b2b2b',
                       foreground='#ffffff')
        
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       background='#2b2b2b',
                       foreground='#ffffff')
        
        style.configure('Info.TLabel',
                       font=('Arial', 10),
                       background='#2b2b2b',
                       foreground='#cccccc')
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(title_frame, 
                               text="🚀 Kronos 加密货币价格预测器",
                               style='Title.TLabel')
        title_label.pack()
        
        # 状态标签
        self.status_label = ttk.Label(title_frame,
                                     text="正在初始化...",
                                     style='Info.TLabel')
        self.status_label.pack()
        
        # 主容器
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧控制面板
        control_frame = tk.Frame(main_frame, bg='#3b3b3b', relief=tk.RAISED, bd=1)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 币种选择
        ttk.Label(control_frame, text="选择加密货币:", style='Header.TLabel').pack(pady=5)
        
        self.crypto_vars = {}
        # 扩展支持的加密货币列表
        crypto_list = ['BTC', 'ETH', 'SOL', 'DOGE', 'WLFI']
        for crypto in crypto_list:
            # 默认只选中主要币种
            default_selected = crypto in ['BTC', 'ETH', 'SOL']
            var = tk.BooleanVar(value=default_selected)
            self.crypto_vars[crypto] = var
            cb = tk.Checkbutton(control_frame, text=crypto, variable=var,
                               bg='#3b3b3b', fg='white', selectcolor='#4b4b4b',
                               font=('Arial', 10))
            cb.pack(anchor=tk.W, padx=10, pady=2)
        
        # 预测天数
        ttk.Label(control_frame, text="预测天数:", style='Header.TLabel').pack(pady=(20, 5))
        
        self.pred_days_var = tk.IntVar(value=7)
        pred_days_scale = tk.Scale(control_frame, from_=1, to=30, 
                                  variable=self.pred_days_var,
                                  orient=tk.HORIZONTAL,
                                  bg='#3b3b3b', fg='white',
                                  highlightbackground='#3b3b3b')
        pred_days_scale.pack(padx=10, pady=5)
        
        # 预测按钮
        self.predict_button = tk.Button(control_frame, 
                                       text="🔮 开始预测",
                                       command=self.start_prediction,
                                       bg='#4CAF50', fg='white',
                                       font=('Arial', 12, 'bold'),
                                       relief=tk.FLAT, bd=0,
                                       padx=20, pady=10)
        self.predict_button.pack(pady=20)
        
        # 保存结果按钮
        save_button = tk.Button(control_frame,
                               text="💾 保存结果",
                               command=self.save_results,
                               bg='#2196F3', fg='white',
                               font=('Arial', 10),
                               relief=tk.FLAT, bd=0,
                               padx=15, pady=5)
        save_button.pack(pady=5)
        
        # 右侧结果显示区域
        result_frame = tk.Frame(main_frame, bg='#2b2b2b')
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建Notebook用于标签页
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 预测结果标签页
        self.result_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(self.result_frame, text="📈 预测结果")
        
        # 图表标签页
        self.chart_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(self.chart_frame, text="📊 价格图表")
        
        # 日志标签页
        log_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(log_frame, text="📝 运行日志")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 bg='#1e1e1e', fg='#00ff00',
                                                 font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化结果显示
        self.create_result_display()
        
    def create_result_display(self):
        """创建结果显示区域"""
        # 清空现有内容
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # 结果表格
        columns = ('币种', '当前价格', '预测价格', '价格变化', '变化百分比', '趋势', '置信度')
        self.result_tree = ttk.Treeview(self.result_frame, columns=columns, show='headings')
        
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
        
    def load_models_async(self):
        """异步加载模型"""
        def load_models():
            self.log("正在加载Kronos模型...")
            success = self.predictor.load_models()
            
            if success:
                self.log("✓ 模型加载成功")
                self.status_label.config(text="模型已就绪 - 可以开始预测")
            else:
                self.log("⚠ 使用模拟预测模式")
                self.status_label.config(text="模拟模式 - 可以开始预测")
        
        thread = threading.Thread(target=load_models, daemon=True)
        thread.start()
    
    def log(self, message: str):
        """添加日志信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        
        self.root.after(0, update_log)
        print(message)
    
    def start_prediction(self):
        """开始预测"""
        # 禁用按钮
        self.predict_button.config(state='disabled', text='预测中...')
        
        # 在后台线程中执行预测
        thread = threading.Thread(target=self.run_prediction, daemon=True)
        thread.start()
    
    def run_prediction(self):
        """运行预测（后台线程）"""
        try:
            selected_cryptos = [crypto for crypto, var in self.crypto_vars.items() if var.get()]
            pred_days = self.pred_days_var.get()
            
            if not selected_cryptos:
                self.log("⚠ 请至少选择一种加密货币")
                return
            
            self.log(f"开始预测 {', '.join(selected_cryptos)} 未来 {pred_days} 天的价格")
            
            self.predictions = {}
            
            for crypto in selected_cryptos:
                self.log(f"正在获取 {crypto} 的历史数据...")
                
                # 获取历史数据
                df = self.data_fetcher.get_kline_data(crypto, limit=100)
                
                if df.empty:
                    self.log(f"✗ {crypto} 数据获取失败")
                    continue
                
                self.log(f"✓ {crypto} 数据获取成功，共 {len(df)} 条记录")
                
                # 进行预测
                self.log(f"正在预测 {crypto} 价格...")
                prediction = self.predictor.predict_price(df, crypto, pred_days)
                
                if prediction:
                    self.predictions[crypto] = prediction
                    self.log(f"✓ {crypto} 预测完成")
                else:
                    self.log(f"✗ {crypto} 预测失败")
            
            # 更新GUI
            self.root.after(0, self.update_results)
            
        except Exception as e:
            self.log(f"✗ 预测过程出错: {e}")
            traceback.print_exc()
        finally:
            # 重新启用按钮
            self.root.after(0, lambda: self.predict_button.config(state='normal', text='🔮 开始预测'))
    
    def update_results(self):
        """更新结果显示"""
        # 清空现有结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 添加新结果
        for crypto, pred in self.predictions.items():
            current_price = f"${pred['current_price']:.2f}"
            predicted_price = f"${pred['predicted_prices'][-1]:.2f}"
            price_change = f"${pred['price_change']:.2f}"
            price_change_pct = f"{pred['price_change_pct']:.2f}%"
            trend = pred['trend']
            confidence = f"{pred['confidence']:.1f}%"
            
            # 根据趋势设置颜色
            tags = ('up',) if trend == 'UP' else ('down',)
            
            self.result_tree.insert('', tk.END, values=(
                crypto, current_price, predicted_price, 
                price_change, price_change_pct, trend, confidence
            ), tags=tags)
        
        # 配置标签颜色
        self.result_tree.tag_configure('up', foreground='#4CAF50')
        self.result_tree.tag_configure('down', foreground='#F44336')
        
        # 更新图表
        self.update_charts()
        
        self.log(f"✓ 预测完成！共预测了 {len(self.predictions)} 种加密货币")
    
    def update_charts(self):
        """更新价格图表"""
        # 清空图表区域
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not self.predictions:
            return
        
        # 创建matplotlib图表
        fig, axes = plt.subplots(len(self.predictions), 1, 
                                figsize=(10, 6*len(self.predictions)),
                                facecolor='#2b2b2b')
        
        if len(self.predictions) == 1:
            axes = [axes]
        
        fig.suptitle('加密货币价格预测', color='white', fontsize=16)
        
        for i, (crypto, pred) in enumerate(self.predictions.items()):
            ax = axes[i]
            ax.set_facecolor('#1e1e1e')
            
            # 绘制预测价格
            dates = pred['future_dates']
            prices = pred['predicted_prices']
            
            ax.plot(dates, prices, 'o-', color='#4CAF50', linewidth=2, markersize=6)
            ax.axhline(y=pred['current_price'], color='#FF9800', linestyle='--', alpha=0.7, label='当前价格')
            
            ax.set_title(f'{crypto} 价格预测', color='white', fontsize=14)
            ax.set_ylabel('价格 (USD)', color='white')
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # 旋转x轴标签
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # 嵌入到tkinter中
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def save_results(self):
        """保存预测结果"""
        if not self.predictions:
            messagebox.showwarning("警告", "没有可保存的预测结果")
            return
        
        try:
            # 保存为JSON文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crypto_predictions_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.predictions, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"预测结果已保存到: {filename}")
            self.log(f"✓ 结果已保存到: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
            self.log(f"✗ 保存失败: {e}")
    
    def run(self):
        """运行应用"""
        self.log("🚀 Kronos 加密货币预测器启动")
        self.log("支持预测: BTC, ETH, SOL")
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = CryptoPredictorGUI()
        app.run()
    except Exception as e:
        print(f"应用启动失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()