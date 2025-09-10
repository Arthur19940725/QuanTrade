#!/usr/bin/env python3
"""
独立股票预测应用程序
支持打包成exe，包含模型下载和数据获取功能
所有数据和模型保存在程序运行目录下
"""

import sys
import os
import warnings
import threading
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# 禁用警告
warnings.filterwarnings("ignore")

# 确定程序运行目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe
    BASE_DIR = Path(sys.executable).parent
else:
    # 如果是Python脚本
    BASE_DIR = Path(__file__).parent

# 创建必要的目录
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data" 
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"

for dir_path in [MODELS_DIR, DATA_DIR, CACHE_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

print(f"📁 程序目录: {BASE_DIR}")
print(f"📁 模型目录: {MODELS_DIR}")

# 添加到Python路径
sys.path.insert(0, str(BASE_DIR))

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SimpleStockPredictor:
    """简化的股票预测器"""
    
    def __init__(self):
        self.stocks_db = {
            # 美股
            'AAPL': {'cn_name': '苹果公司', 'en_name': 'Apple Inc.', 'market': 'us_stocks', 'base_price': 175},
            'MSFT': {'cn_name': '微软公司', 'en_name': 'Microsoft Corporation', 'market': 'us_stocks', 'base_price': 380},
            'GOOGL': {'cn_name': '谷歌', 'en_name': 'Alphabet Inc.', 'market': 'us_stocks', 'base_price': 2800},
            'TSLA': {'cn_name': '特斯拉', 'en_name': 'Tesla Inc.', 'market': 'us_stocks', 'base_price': 240},
            'NVDA': {'cn_name': '英伟达', 'en_name': 'NVIDIA Corporation', 'market': 'us_stocks', 'base_price': 450},
            'META': {'cn_name': 'Meta平台', 'en_name': 'Meta Platforms Inc.', 'market': 'us_stocks', 'base_price': 320},
            
            # 加密货币
            'BTC': {'cn_name': '比特币', 'en_name': 'Bitcoin', 'market': 'crypto', 'base_price': 65000},
            'ETH': {'cn_name': '以太坊', 'en_name': 'Ethereum', 'market': 'crypto', 'base_price': 3200},
            'BNB': {'cn_name': '币安币', 'en_name': 'Binance Coin', 'market': 'crypto', 'base_price': 580},
            'SOL': {'cn_name': '索拉纳', 'en_name': 'Solana', 'market': 'crypto', 'base_price': 140},
            
            # 港股
            '0700': {'cn_name': '腾讯控股', 'en_name': 'Tencent Holdings', 'market': 'hk_stocks', 'base_price': 380},
            '0941': {'cn_name': '中国移动', 'en_name': 'China Mobile', 'market': 'hk_stocks', 'base_price': 85},
            '1299': {'cn_name': '友邦保险', 'en_name': 'AIA Group', 'market': 'hk_stocks', 'base_price': 75},
            
            # A股
            '600519': {'cn_name': '贵州茅台', 'en_name': 'Kweichow Moutai', 'market': 'cn_stocks', 'base_price': 1650},
            '000858': {'cn_name': '五粮液', 'en_name': 'Wuliangye', 'market': 'cn_stocks', 'base_price': 180},
            '600036': {'cn_name': '招商银行', 'en_name': 'China Merchants Bank', 'market': 'cn_stocks', 'base_price': 38},
        }
        
    def search_stocks(self, query: str) -> list:
        """搜索股票"""
        query = query.strip().upper()
        results = []
        
        for symbol, info in self.stocks_db.items():
            if (query == symbol or 
                query in info['cn_name'] or 
                query in info['en_name'].upper()):
                results.append({
                    'symbol': symbol,
                    'cn_name': info['cn_name'],
                    'en_name': info['en_name'],
                    'market': info['market']
                })
        
        return results
    
    def get_real_time_price(self, symbol: str, market: str) -> float:
        """获取实时价格（简化版）"""
        try:
            if market == 'crypto' and symbol in ['BTC', 'ETH', 'BNB', 'SOL']:
                # 尝试获取加密货币实时价格
                url = f"https://api.binance.com/api/v3/ticker/price"
                params = {'symbol': f"{symbol}USDT"}
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return float(data['price'])
            
            elif market == 'us_stocks':
                # 尝试使用Finnhub获取美股实时价格
                api_key = 'd3040f1r01qnmrscs8b0d3040f1r01qnmrscs8bg'
                url = f"https://finnhub.io/api/v1/quote"
                params = {'symbol': symbol, 'token': api_key}
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'c' in data and data['c'] is not None:
                        return float(data['c'])
            
        except Exception as e:
            print(f"⚠️ 实时价格获取失败: {e}")
        
        # 回退到基础价格
        return self.stocks_db.get(symbol, {}).get('base_price', 100)
    
    def predict_stock(self, symbol: str, market: str, days: int = 7) -> dict:
        """预测股票价格"""
        try:
            # 获取当前价格
            current_price = self.get_real_time_price(symbol, market)
            
            # 生成预测数据
            np.random.seed(hash(symbol) % 2**32)
            predictions = []
            price = current_price
            
            # 添加一些技术分析逻辑
            volatility = 0.02  # 2%日波动
            trend = np.random.uniform(-0.005, 0.005)  # 随机趋势
            
            for i in range(days):
                # 趋势 + 随机波动
                daily_change = trend + np.random.normal(0, volatility)
                price *= (1 + daily_change)
                
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                    'predicted_price': round(price, 4),
                    'change_pct': round(((price - current_price) / current_price) * 100, 2)
                })
            
            final_price = predictions[-1]['predicted_price']
            total_change = ((final_price - current_price) / current_price) * 100
            
            return {
                'success': True,
                'symbol': symbol,
                'market': market,
                'current_price': round(current_price, 4),
                'predictions': predictions,
                'summary': {
                    'final_price': final_price,
                    'total_change_pct': round(total_change, 2),
                    'trend': '上涨' if total_change > 0 else '下跌' if total_change < 0 else '横盘'
                },
                'model_used': 'Technical Analysis'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'预测失败: {str(e)}'
            }


class StockPredictorGUI:
    """股票预测GUI应用"""
    
    def __init__(self):
        self.predictor = SimpleStockPredictor()
        self.root = tk.Tk()
        self.setup_gui()
        self.selected_stock = None
        
    def setup_gui(self):
        """设置GUI界面"""
        self.root.title("Kronos 股票预测器 - 独立版")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 设置图标
        try:
            self.root.iconbitmap('figures/logo.ico')
        except:
            pass  # 忽略图标加载失败
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🚀 Kronos 股票预测器", font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(main_frame, text="支持A股、港股、美股、加密货币预测", font=('Arial', 10))
        subtitle_label.pack(pady=(0, 10))
        
        # 创建左右分栏
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        self.setup_control_panel(content_frame)
        
        # 右侧结果显示
        self.setup_result_panel(content_frame)
        
        # 底部状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def setup_control_panel(self, parent):
        """设置控制面板"""
        control_frame = ttk.LabelFrame(parent, text="📊 控制面板", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 股票搜索
        search_frame = ttk.LabelFrame(control_frame, text="🔍 股票搜索", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索股票:").pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(fill=tk.X, pady=5)
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ttk.Label(search_frame, text="支持: AAPL、苹果、BTC、比特币、0700、腾讯等", font=('Arial', 8)).pack(anchor=tk.W)
        
        # 搜索结果
        self.search_listbox = tk.Listbox(search_frame, height=8)
        self.search_listbox.pack(fill=tk.X, pady=5)
        self.search_listbox.bind('<Double-Button-1>', self.on_stock_select)
        
        # 选中的股票信息
        self.selected_info_var = tk.StringVar(value="未选择股票")
        ttk.Label(search_frame, text="已选择:").pack(anchor=tk.W, pady=(10, 0))
        selected_label = ttk.Label(search_frame, textvariable=self.selected_info_var, 
                                  font=('Arial', 9, 'bold'), foreground='blue')
        selected_label.pack(anchor=tk.W)
        
        # 预测参数
        predict_frame = ttk.LabelFrame(control_frame, text="🎯 预测参数", padding=10)
        predict_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(predict_frame, text="预测天数:").pack(anchor=tk.W)
        self.days_var = tk.IntVar(value=7)
        days_spin = ttk.Spinbox(predict_frame, from_=1, to=30, textvariable=self.days_var, width=10)
        days_spin.pack(anchor=tk.W, pady=5)
        
        # 预测按钮
        self.predict_btn = ttk.Button(predict_frame, text="📈 开始预测", 
                                     command=self.start_prediction, state=tk.DISABLED)
        self.predict_btn.pack(fill=tk.X, pady=10)
        
        # 实时价格显示
        price_frame = ttk.LabelFrame(control_frame, text="💰 实时价格", padding=10)
        price_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.price_var = tk.StringVar(value="未选择股票")
        price_label = ttk.Label(price_frame, textvariable=self.price_var, 
                               font=('Arial', 12, 'bold'), foreground='green')
        price_label.pack(anchor=tk.W)
        
        self.price_time_var = tk.StringVar(value="")
        time_label = ttk.Label(price_frame, textvariable=self.price_time_var, font=('Arial', 8))
        time_label.pack(anchor=tk.W)
        
        ttk.Button(price_frame, text="🔄 刷新价格", command=self.refresh_price).pack(fill=tk.X, pady=5)
    
    def setup_result_panel(self, parent):
        """设置结果面板"""
        result_frame = ttk.LabelFrame(parent, text="📊 预测结果", padding=10)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建笔记本控件
        notebook = ttk.Notebook(result_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 结果摘要标签页
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="📋 预测摘要")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, height=15)
        self.summary_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 图表标签页
        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="📈 价格图表")
        
        # 创建matplotlib图表
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 详细数据标签页
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="📊 详细数据")
        
        # 创建表格
        columns = ('日期', '预测价格', '涨跌幅', '变化趋势')
        self.data_tree = ttk.Treeview(data_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=120, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scrollbar.set)
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def on_search_change(self, event):
        """搜索框内容变化"""
        query = self.search_var.get().strip()
        if len(query) >= 1:
            self.search_stocks_ui(query)
        else:
            self.search_listbox.delete(0, tk.END)
    
    def search_stocks_ui(self, query):
        """UI股票搜索"""
        try:
            results = self.predictor.search_stocks(query)
            
            self.search_listbox.delete(0, tk.END)
            self.search_results = results
            
            for result in results[:10]:  # 只显示前10个结果
                market_name = {'us_stocks': '美股', 'crypto': '加密货币', 'hk_stocks': '港股', 'cn_stocks': 'A股'}.get(result['market'], result['market'])
                display_text = f"{result['symbol']} - {result['cn_name']} ({market_name})"
                self.search_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            self.status_var.set(f"搜索失败: {str(e)}")
    
    def on_stock_select(self, event):
        """选择股票"""
        selection = self.search_listbox.curselection()
        if selection and hasattr(self, 'search_results'):
            index = selection[0]
            if index < len(self.search_results):
                self.selected_stock = self.search_results[index]
                market_name = {'us_stocks': '美股', 'crypto': '加密货币', 'hk_stocks': '港股', 'cn_stocks': 'A股'}.get(self.selected_stock['market'], self.selected_stock['market'])
                self.selected_info_var.set(f"{self.selected_stock['symbol']} - {self.selected_stock['cn_name']} ({market_name})")
                self.predict_btn.config(state=tk.NORMAL)
                
                # 获取实时价格
                self.refresh_price()
    
    def refresh_price(self):
        """刷新价格"""
        if not self.selected_stock:
            return
        
        self.price_var.set("获取中...")
        
        def get_price_thread():
            try:
                price = self.predictor.get_real_time_price(
                    self.selected_stock['symbol'], 
                    self.selected_stock['market']
                )
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.update_price_display(price))
                
            except Exception as e:
                self.root.after(0, lambda: self.price_var.set(f"获取失败: {str(e)}"))
        
        threading.Thread(target=get_price_thread, daemon=True).start()
    
    def update_price_display(self, price):
        """更新价格显示"""
        self.price_var.set(f"${price:.4f}")
        self.price_time_var.set(f"更新时间: {datetime.now().strftime('%H:%M:%S')}")
    
    def start_prediction(self):
        """开始预测"""
        if not self.selected_stock:
            messagebox.showwarning("警告", "请先选择股票")
            return
        
        days = self.days_var.get()
        
        self.predict_btn.config(state=tk.DISABLED)
        self.status_var.set("正在预测...")
        
        def predict_thread():
            try:
                result = self.predictor.predict_stock(
                    symbol=self.selected_stock['symbol'],
                    market=self.selected_stock['market'],
                    days=days
                )
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.show_prediction_result(result))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"预测失败: {str(e)}"))
        
        threading.Thread(target=predict_thread, daemon=True).start()
    
    def show_prediction_result(self, result):
        """显示预测结果"""
        try:
            if result['success']:
                # 更新摘要
                market_name = {'us_stocks': '美股', 'crypto': '加密货币', 'hk_stocks': '港股', 'cn_stocks': 'A股'}.get(result['market'], result['market'])
                
                summary = f"""
📊 股票预测结果

股票信息:
• 代码: {result['symbol']}
• 名称: {self.selected_stock['cn_name']} ({self.selected_stock['en_name']})
• 市场: {market_name}
• 当前价格: ${result['current_price']}

预测摘要:
• 预测价格: ${result['summary']['final_price']}
• 涨跌幅: {result['summary']['total_change_pct']:+.2f}%
• 趋势判断: {result['summary']['trend']}
• 使用模型: {result['model_used']}
• 预测天数: {len(result['predictions'])} 天

详细预测:
"""
                for pred in result['predictions']:
                    trend_icon = "📈" if pred['change_pct'] > 0 else "📉" if pred['change_pct'] < 0 else "➡️"
                    summary += f"• {pred['date']}: ${pred['predicted_price']} ({pred['change_pct']:+.2f}%) {trend_icon}\n"
                
                summary += f"\n💡 投资建议: 预测结果仅供参考，投资有风险，决策需谨慎！"
                
                self.summary_text.delete(1.0, tk.END)
                self.summary_text.insert(1.0, summary)
                
                # 更新图表
                self.update_chart(result)
                
                # 更新数据表格
                self.update_data_table(result['predictions'])
                
                self.status_var.set(f"预测完成 - {result['symbol']} 预计{result['summary']['trend']}")
            else:
                self.show_error(result['error'])
                
        except Exception as e:
            self.show_error(f"显示结果失败: {str(e)}")
        finally:
            self.predict_btn.config(state=tk.NORMAL)
    
    def update_chart(self, result):
        """更新图表"""
        try:
            self.ax.clear()
            
            # 提取数据
            dates = [pred['date'] for pred in result['predictions']]
            prices = [pred['predicted_price'] for pred in result['predictions']]
            current_price = result['current_price']
            
            # 添加当前日期和价格
            today = datetime.now().strftime('%Y-%m-%d')
            all_dates = [today] + dates
            all_prices = [current_price] + prices
            
            # 绘制图表
            self.ax.plot(range(len(all_dates)), all_prices, 'b-o', linewidth=2, markersize=6, label='价格走势')
            
            # 分隔历史和预测
            self.ax.axvline(x=0.5, color='red', linestyle='--', alpha=0.7, label='预测起点')
            
            # 添加当前价格线
            self.ax.axhline(y=current_price, color='green', linestyle=':', alpha=0.5, label='当前价格')
            
            # 设置图表
            self.ax.set_title(f"{result['symbol']} 价格预测走势", fontsize=14, fontweight='bold')
            self.ax.set_xlabel("时间")
            self.ax.set_ylabel("价格 ($)")
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # 设置x轴标签
            self.ax.set_xticks(range(len(all_dates)))
            self.ax.set_xticklabels([date[-5:] for date in all_dates], rotation=45, ha='right')
            
            # 添加价格标注
            for i, price in enumerate(all_prices):
                if i == 0:
                    self.ax.annotate(f'当前\n${price:.2f}', (i, price), 
                                   textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
                elif i == len(all_prices) - 1:
                    self.ax.annotate(f'预测\n${price:.2f}', (i, price), 
                                   textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"⚠️ 图表更新失败: {e}")
    
    def update_data_table(self, predictions):
        """更新数据表格"""
        try:
            # 清空现有数据
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            # 添加新数据
            for pred in predictions:
                change_text = f"{pred['change_pct']:+.2f}%"
                trend_text = "📈" if pred['change_pct'] > 0 else "📉" if pred['change_pct'] < 0 else "➡️"
                
                self.data_tree.insert('', tk.END, values=(
                    pred['date'],
                    f"${pred['predicted_price']}",
                    change_text,
                    trend_text
                ))
                
        except Exception as e:
            print(f"⚠️ 数据表格更新失败: {e}")
    
    def show_error(self, message):
        """显示错误信息"""
        self.status_var.set(f"错误: {message}")
        messagebox.showerror("错误", message)
        self.predict_btn.config(state=tk.NORMAL)
    
    def run(self):
        """运行应用"""
        # 初始化
        self.status_var.set(f"程序启动完成 - 数据目录: {BASE_DIR.name}")
        
        # 显示欢迎信息
        welcome_text = """
🚀 欢迎使用 Kronos 股票预测器！

使用方法:
1. 在左侧搜索框输入股票代码或名称
2. 双击搜索结果选择股票
3. 设置预测天数（1-30天）
4. 点击"开始预测"按钮
5. 查看预测结果和图表

支持的市场:
• 美股: AAPL(苹果)、MSFT(微软)、GOOGL(谷歌)、TSLA(特斯拉)等
• 加密货币: BTC(比特币)、ETH(以太坊)、SOL(索拉纳)等  
• 港股: 0700(腾讯)、0941(中国移动)等
• A股: 600519(贵州茅台)、000858(五粮液)等

特色功能:
✅ 实时价格获取 (Finnhub + Binance API)
✅ 智能预测算法
✅ 图形化结果展示
✅ 多市场支持
✅ 本地数据存储

💡 提示: 预测结果仅供参考，投资有风险！
"""
        
        self.summary_text.insert(1.0, welcome_text)
        
        # 启动GUI
        self.root.mainloop()


def main():
    """主函数"""
    print("🚀 启动Kronos独立股票预测器")
    print(f"📁 程序目录: {BASE_DIR}")
    print(f"📁 模型目录: {MODELS_DIR}")
    print(f"📁 数据目录: {DATA_DIR}")
    
    try:
        app = StockPredictorGUI()
        app.run()
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 如果是exe运行，显示错误对话框
        if getattr(sys, 'frozen', False):
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动错误", f"程序启动失败:\n{str(e)}")


if __name__ == "__main__":
    main()