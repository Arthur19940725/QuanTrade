#!/usr/bin/env python3
"""
加密货币价格预测应用 - 轻量版
不依赖Kronos模型，使用技术分析方法进行预测
"""

import sys
import os
import warnings
from datetime import datetime, timedelta
import json
import traceback
from typing import Dict, List, Optional
import threading

warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import requests

class CryptoDataFetcher:
    """加密货币数据获取器"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    def get_kline_data(self, symbol: str, interval: str = "1d", limit: int = 100) -> pd.DataFrame:
        """获取K线数据"""
        try:
            # 处理特殊代币映射
            symbol_mapping = {
                'WLFI': 'WLFIUSDT',  # 特殊处理WLFI
                'DOGE': 'DOGEUSDT',  # DOGE映射
            }
            
            # 确定交易对
            if symbol in symbol_mapping:
                trading_pair = symbol_mapping[symbol]
            else:
                trading_pair = f"{symbol}USDT"
            
            url = f"{self.base_url}/klines"
            params = {
                'symbol': trading_pair,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            df = df.rename(columns={'timestamp': 'datetime'})
            df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
            df = df.set_index('datetime')
            
            return df
            
        except Exception as e:
            print(f"获取 {symbol} 数据失败: {e}")
            return self._get_mock_data(symbol, limit)
    
    def _get_mock_data(self, symbol: str, limit: int) -> pd.DataFrame:
        """生成模拟数据"""
        dates = pd.date_range(end=datetime.now(), periods=limit, freq='D')
        base_prices = {
            'BTC': 45000, 
            'ETH': 2500, 
            'SOL': 100,
            'DOGE': 0.08,  # DOGE基础价格
            'WLFI': 0.01   # WLFI基础价格
        }
        base_price = base_prices.get(symbol, 1000)
        
        np.random.seed(42)
        prices = []
        current_price = base_price
        
        for _ in range(limit):
            change = np.random.normal(0, 0.02)
            current_price *= (1 + change)
            prices.append(current_price)
        
        df = pd.DataFrame({
            'datetime': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000, 10000, limit)
        })
        
        df = df.set_index('datetime')
        return df

class TechnicalAnalysisPredictor:
    """基于技术分析的价格预测器"""
    
    def __init__(self):
        pass
    
    def calculate_sma(self, prices: pd.Series, window: int) -> pd.Series:
        """计算简单移动平均线"""
        return prices.rolling(window=window).mean()
    
    def calculate_ema(self, prices: pd.Series, span: int) -> pd.Series:
        """计算指数移动平均线"""
        return prices.ewm(span=span).mean()
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """计算MACD指标"""
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def predict_price(self, df: pd.DataFrame, symbol: str, pred_days: int = 7) -> Dict:
        """基于技术分析预测价格"""
        try:
            prices = df['close']
            
            # 计算技术指标
            sma_20 = self.calculate_sma(prices, 20)
            ema_12 = self.calculate_ema(prices, 12)
            rsi = self.calculate_rsi(prices)
            macd_line, signal_line, histogram = self.calculate_macd(prices)
            
            # 获取最新值
            current_price = float(prices.iloc[-1])
            latest_sma = float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else current_price
            latest_ema = float(ema_12.iloc[-1]) if not pd.isna(ema_12.iloc[-1]) else current_price
            latest_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
            latest_macd = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else 0
            latest_signal = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0
            
            # 计算趋势强度
            price_momentum = (current_price - latest_sma) / latest_sma
            ema_trend = 1 if current_price > latest_ema else -1
            rsi_signal = 1 if latest_rsi < 30 else (-1 if latest_rsi > 70 else 0)
            macd_signal = 1 if latest_macd > latest_signal else -1
            
            # 综合信号
            signals = [price_momentum * 10, ema_trend, rsi_signal, macd_signal]
            trend_score = sum(signals) / len(signals)
            
            # 计算波动率
            returns = prices.pct_change().dropna()
            volatility = float(returns.std())
            
            # 生成预测价格
            predicted_prices = []
            price = current_price
            
            # 基于趋势和波动率预测
            daily_trend = trend_score * 0.01  # 每日趋势强度
            
            for day in range(pred_days):
                # 趋势衰减
                trend_decay = 0.9 ** day
                daily_change = daily_trend * trend_decay + np.random.normal(0, volatility * 0.5)
                price *= (1 + daily_change)
                predicted_prices.append(price)
            
            # 计算预测统计
            final_price = predicted_prices[-1]
            price_change = final_price - current_price
            price_change_pct = (price_change / current_price) * 100
            
            # 计算置信度
            confidence = min(95, max(50, 80 - abs(latest_rsi - 50) + abs(trend_score * 20)))
            
            # 生成未来日期
            last_date = df.index[-1]
            future_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=pred_days,
                freq='D'
            )
            
            # 生成最高最低价格预测曲线
            predicted_highs = []
            predicted_lows = []
            
            for i, base_price in enumerate(predicted_prices):
                # 基于波动率生成高低点
                daily_volatility = volatility * (1 + np.random.uniform(-0.3, 0.3))
                high_factor = 1 + abs(np.random.normal(0, daily_volatility * 0.7))
                low_factor = 1 - abs(np.random.normal(0, daily_volatility * 0.7))
                
                predicted_highs.append(base_price * high_factor)
                predicted_lows.append(base_price * low_factor)
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'predicted_prices': predicted_prices,
                'predicted_highs': predicted_highs,
                'predicted_lows': predicted_lows,
                'future_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'trend': 'UP' if price_change > 0 else 'DOWN',
                'confidence': confidence,
                'technical_indicators': {
                    'sma_20': latest_sma,
                    'ema_12': latest_ema,
                    'rsi': latest_rsi,
                    'macd': latest_macd,
                    'signal': latest_signal,
                    'trend_score': trend_score
                }
            }
            
        except Exception as e:
            print(f"技术分析预测失败: {e}")
            return self._simple_prediction(df, symbol, pred_days)
    
    def _simple_prediction(self, df: pd.DataFrame, symbol: str, pred_days: int) -> Dict:
        """简单预测（备用方法）"""
        current_price = float(df['close'].iloc[-1])
        returns = df['close'].pct_change().dropna()
        avg_return = float(returns.mean())
        volatility = float(returns.std())
        
        predicted_prices = []
        price = current_price
        
        for _ in range(pred_days):
            daily_return = avg_return + np.random.normal(0, volatility * 0.5)
            price *= (1 + daily_return)
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
            'confidence': 70
        }

class CryptoPredictorLiteGUI:
    """轻量版加密货币预测应用GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kronos Lite 加密货币价格预测器")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # 设置中文字体支持
        try:
            import matplotlib
            matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
            matplotlib.rcParams['axes.unicode_minus'] = False
        except:
            pass
        
        self.setup_styles()
        self.data_fetcher = CryptoDataFetcher()
        self.predictor = TechnicalAnalysisPredictor()
        self.predictions = {}
        
        self.create_widgets()
        
    def setup_styles(self):
        """设置GUI样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
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
                               text="📊 Kronos Lite 加密货币价格预测器",
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                  text="基于技术分析的价格预测",
                                  style='Info.TLabel')
        subtitle_label.pack()
        
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
        
        # 技术指标标签页
        self.indicator_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(self.indicator_frame, text="📋 技术指标")
        
        # 初始化结果显示
        self.create_result_display()
        
    def create_result_display(self):
        """创建结果显示区域"""
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        columns = ('币种', '当前价格', '预测价格', '价格变化', '变化百分比', '趋势', '置信度')
        self.result_tree = ttk.Treeview(self.result_frame, columns=columns, show='headings')
        
        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)
    
    def start_prediction(self):
        """开始预测"""
        self.predict_button.config(state='disabled', text='预测中...')
        thread = threading.Thread(target=self.run_prediction, daemon=True)
        thread.start()
    
    def run_prediction(self):
        """运行预测（后台线程）"""
        try:
            selected_cryptos = [crypto for crypto, var in self.crypto_vars.items() if var.get()]
            pred_days = self.pred_days_var.get()
            
            if not selected_cryptos:
                messagebox.showwarning("警告", "请至少选择一种加密货币")
                return
            
            self.predictions = {}
            
            for crypto in selected_cryptos:
                print(f"正在预测 {crypto}...")
                
                # 获取历史数据
                df = self.data_fetcher.get_kline_data(crypto, limit=100)
                
                if df.empty:
                    print(f"{crypto} 数据获取失败")
                    continue
                
                # 进行技术分析预测
                prediction = self.predictor.predict_price(df, crypto, pred_days)
                
                if prediction:
                    self.predictions[crypto] = prediction
                    print(f"{crypto} 预测完成")
            
            # 更新GUI
            self.root.after(0, self.update_results)
            
        except Exception as e:
            print(f"预测过程出错: {e}")
            traceback.print_exc()
        finally:
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
            
            tags = ('up',) if trend == 'UP' else ('down',)
            
            self.result_tree.insert('', tk.END, values=(
                crypto, current_price, predicted_price, 
                price_change, price_change_pct, trend, confidence
            ), tags=tags)
        
        self.result_tree.tag_configure('up', foreground='#4CAF50')
        self.result_tree.tag_configure('down', foreground='#F44336')
        
        self.update_charts()
        self.update_indicators()
    
    def update_charts(self):
        """更新价格图表 - 显示历史价格+预测价格"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not self.predictions:
            return
        
        fig, axes = plt.subplots(len(self.predictions), 1, 
                                figsize=(12, 5*len(self.predictions)),
                                facecolor='#2b2b2b')
        
        if len(self.predictions) == 1:
            axes = [axes]
        
        fig.suptitle('加密货币价格预测 (历史+预测)', color='white', fontsize=16)
        
        for i, (crypto, pred) in enumerate(self.predictions.items()):
            ax = axes[i]
            ax.set_facecolor('#1e1e1e')
            
            # 获取历史数据
            try:
                hist_df = self.data_fetcher.get_kline_data(crypto, limit=30)
                if not hist_df.empty:
                    hist_dates = hist_df.index[-15:]  # 最近15天历史
                    hist_prices = hist_df['close'][-15:]
                    hist_highs = hist_df['high'][-15:]
                    hist_lows = hist_df['low'][-15:]
                    
                    # 绘制历史价格
                    ax.plot(hist_dates, hist_prices, 'b-', linewidth=2, label='历史价格', alpha=0.8)
                    ax.fill_between(hist_dates, hist_lows, hist_highs, alpha=0.2, color='blue', label='历史波动范围')
            except:
                hist_dates = pd.date_range(end=pd.Timestamp.now(), periods=15, freq='D')
                hist_prices = [pred['current_price']] * 15
            
            # 预测数据
            pred_dates = pd.to_datetime(pred['future_dates'])
            pred_prices = pred['predicted_prices']
            pred_highs = pred.get('predicted_highs', pred_prices)
            pred_lows = pred.get('predicted_lows', pred_prices)
            
            # 连接历史和预测数据
            if 'hist_dates' in locals() and len(hist_dates) > 0:
                # 创建连接点
                connection_date = hist_dates[-1]
                connection_price = hist_prices.iloc[-1] if hasattr(hist_prices, 'iloc') else hist_prices[-1]
                
                # 绘制预测价格（与历史连接）
                all_pred_dates = [connection_date] + list(pred_dates)
                all_pred_prices = [connection_price] + pred_prices
                all_pred_highs = [connection_price] + pred_highs
                all_pred_lows = [connection_price] + pred_lows
                
                ax.plot(all_pred_dates, all_pred_prices, 'r-', linewidth=2, label='预测价格', alpha=0.9)
                ax.fill_between(all_pred_dates, all_pred_lows, all_pred_highs, 
                               alpha=0.3, color='red', label='预测波动范围')
                
                # 标记连接点
                ax.plot(connection_date, connection_price, 'go', markersize=8, label='当前价格')
            else:
                # 如果没有历史数据，只显示预测
                ax.plot(pred_dates, pred_prices, 'r-', linewidth=2, label='预测价格')
                ax.fill_between(pred_dates, pred_lows, pred_highs, alpha=0.3, color='red', label='预测波动范围')
            
            # 设置图表样式
            ax.set_title(f'{crypto} 价格走势预测', color='white', fontsize=14, pad=20)
            ax.set_ylabel('价格 (USD)', color='white', fontsize=12)
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper left', framealpha=0.8)
            
            # 格式化价格显示
            current_price = pred['current_price']
            if current_price < 1:
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.4f}'))
            else:
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.2f}'))
            
            # 旋转日期标签
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # 添加趋势信息
            trend_color = '#4CAF50' if pred['trend'] == 'UP' else '#F44336'
            ax.text(0.02, 0.98, f"趋势: {pred['trend']} ({pred['price_change_pct']:.2f}%)", 
                   transform=ax.transAxes, color=trend_color, fontsize=10,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_indicators(self):
        """更新技术指标显示"""
        for widget in self.indicator_frame.winfo_children():
            widget.destroy()
        
        if not self.predictions:
            return
        
        # 创建技术指标表格
        columns = ('币种', 'SMA-20', 'EMA-12', 'RSI', 'MACD', 'Signal', '趋势得分')
        indicator_tree = ttk.Treeview(self.indicator_frame, columns=columns, show='headings')
        
        for col in columns:
            indicator_tree.heading(col, text=col)
            indicator_tree.column(col, width=100)
        
        for crypto, pred in self.predictions.items():
            if 'technical_indicators' in pred:
                indicators = pred['technical_indicators']
                indicator_tree.insert('', tk.END, values=(
                    crypto,
                    f"{indicators.get('sma_20', 0):.2f}",
                    f"{indicators.get('ema_12', 0):.2f}",
                    f"{indicators.get('rsi', 0):.1f}",
                    f"{indicators.get('macd', 0):.4f}",
                    f"{indicators.get('signal', 0):.4f}",
                    f"{indicators.get('trend_score', 0):.2f}"
                ))
        
        indicator_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def save_results(self):
        """保存预测结果"""
        if not self.predictions:
            messagebox.showwarning("警告", "没有可保存的预测结果")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crypto_predictions_lite_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.predictions, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"预测结果已保存到: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        app = CryptoPredictorLiteGUI()
        app.run()
    except Exception as e:
        print(f"应用启动失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()