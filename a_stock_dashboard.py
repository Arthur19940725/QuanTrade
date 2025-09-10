#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据仪表板
展示A股实时价格和买卖量分解
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import pandas as pd

class AStockDashboard:
    """A股数据仪表板"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("A股数据仪表板 - 实时价格与买卖量分析")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f2f2f7')
        
        # 数据获取器
        try:
            from enhanced_a_stock_fetcher import EnhancedAStockFetcher
            self.fetcher = EnhancedAStockFetcher()
        except ImportError:
            messagebox.showerror("错误", "增强型A股数据获取器未找到")
            return
        
        # 当前显示的股票
        self.current_symbol = None
        self.update_thread = None
        self.is_updating = False
        
        self.setup_ui()
        self.start_auto_update()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="A股数据仪表板", 
                               font=('SF Pro Text', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 股票选择区域
        selection_frame = ttk.LabelFrame(main_frame, text="股票选择", padding="10")
        selection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 股票代码输入
        ttk.Label(selection_frame, text="股票代码:").grid(row=0, column=0, padx=(0, 10))
        self.symbol_var = tk.StringVar()
        self.symbol_entry = ttk.Entry(selection_frame, textvariable=self.symbol_var, width=15)
        self.symbol_entry.grid(row=0, column=1, padx=(0, 10))
        
        # 预设股票按钮
        preset_stocks = [
            ('600519', '贵州茅台'),
            ('000858', '五粮液'),
            ('000001', '平安银行'),
            ('000002', '万科A'),
            ('600036', '招商银行'),
            ('601318', '中国平安')
        ]
        
        for i, (code, name) in enumerate(preset_stocks):
            btn = ttk.Button(selection_frame, text=f"{code}\n{name}", 
                           command=lambda c=code: self.select_stock(c),
                           width=12)
            btn.grid(row=0, column=2+i, padx=5)
        
        # 查询按钮
        query_btn = ttk.Button(selection_frame, text="查询", command=self.query_stock)
        query_btn.grid(row=0, column=8, padx=(10, 0))
        
        # 数据展示区域
        data_frame = ttk.LabelFrame(main_frame, text="实时数据", padding="10")
        data_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        data_frame.columnconfigure(1, weight=1)
        
        # 价格信息
        self.price_label = ttk.Label(data_frame, text="请选择股票", 
                                   font=('SF Pro Text', 16))
        self.price_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 详细信息表格
        self.create_info_table(data_frame)
        
        # 买卖量分解图表区域
        volume_frame = ttk.LabelFrame(main_frame, text="买卖量分解", padding="10")
        volume_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        volume_frame.columnconfigure(0, weight=1)
        
        # 买卖量信息
        self.volume_info_label = ttk.Label(volume_frame, text="买卖量信息将在此显示", 
                                         font=('SF Pro Text', 14))
        self.volume_info_label.grid(row=0, column=0, pady=(0, 10))
        
        # 买卖量进度条
        self.buy_progress = ttk.Progressbar(volume_frame, length=400, mode='determinate')
        self.buy_progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.sell_progress = ttk.Progressbar(volume_frame, length=400, mode='determinate')
        self.sell_progress.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 买卖量标签
        self.buy_label = ttk.Label(volume_frame, text="买入量: 0 股 (0%)")
        self.buy_label.grid(row=3, column=0, sticky=tk.W)
        
        self.sell_label = ttk.Label(volume_frame, text="卖出量: 0 股 (0%)")
        self.sell_label.grid(row=4, column=0, sticky=tk.W)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_info_table(self, parent):
        """创建信息表格"""
        # 创建Treeview
        columns = ('指标', '数值', '单位')
        self.info_tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)
        
        # 设置列标题
        for col in columns:
            self.info_tree.heading(col, text=col)
            self.info_tree.column(col, width=150, anchor='center')
        
        self.info_tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.info_tree.yview)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.info_tree.configure(yscrollcommand=scrollbar.set)
    
    def select_stock(self, symbol):
        """选择预设股票"""
        self.symbol_var.set(symbol)
        self.query_stock()
    
    def query_stock(self):
        """查询股票数据"""
        symbol = self.symbol_var.get().strip()
        if not symbol:
            messagebox.showwarning("警告", "请输入股票代码")
            return
        
        self.current_symbol = symbol
        self.update_data()
    
    def update_data(self):
        """更新股票数据"""
        if not self.current_symbol:
            return
        
        try:
            self.status_var.set(f"正在获取 {self.current_symbol} 数据...")
            
            # 获取实时数据
            realtime_data = self.fetcher.get_real_time_price(self.current_symbol)
            
            if realtime_data and realtime_data.get('price', 0) > 0:
                # 更新价格显示
                price = realtime_data['price']
                change = realtime_data.get('change', 0)
                change_pct = realtime_data.get('change_pct', 0)
                
                price_text = f"{self.current_symbol} - {price:.2f} 元"
                if change != 0:
                    price_text += f" ({change:+.2f}, {change_pct:+.2f}%)"
                
                self.price_label.config(text=price_text)
                
                # 更新详细信息表格
                self.update_info_table(realtime_data)
                
                # 更新买卖量分解
                self.update_volume_breakdown(realtime_data)
                
                self.status_var.set(f"数据更新成功 - {datetime.now().strftime('%H:%M:%S')}")
            else:
                self.status_var.set("数据获取失败")
                messagebox.showerror("错误", f"无法获取股票 {self.current_symbol} 的数据")
        
        except Exception as e:
            self.status_var.set(f"更新失败: {str(e)}")
            messagebox.showerror("错误", f"更新数据时发生错误: {str(e)}")
    
    def update_info_table(self, data):
        """更新信息表格"""
        # 清空现有数据
        for item in self.info_tree.get_children():
            self.info_tree.delete(item)
        
        # 添加数据行
        info_data = [
            ('最新价', f"{data.get('price', 0):.2f}", '元'),
            ('涨跌额', f"{data.get('change', 0):+.2f}", '元'),
            ('涨跌幅', f"{data.get('change_pct', 0):+.2f}", '%'),
            ('成交量', f"{data.get('volume', 0):,.0f}", '股'),
            ('成交额', f"{data.get('turnover', 0):,.0f}", '元'),
            ('最高价', f"{data.get('high', 0):.2f}", '元'),
            ('最低价', f"{data.get('low', 0):.2f}", '元'),
            ('开盘价', f"{data.get('open', 0):.2f}", '元'),
            ('数据源', data.get('source', '未知'), ''),
            ('更新时间', data.get('timestamp', ''), '')
        ]
        
        for info in info_data:
            self.info_tree.insert('', 'end', values=info)
    
    def update_volume_breakdown(self, data):
        """更新买卖量分解显示"""
        try:
            # 获取买卖量分解数据
            volume_data = self.fetcher.get_volume_breakdown(self.current_symbol)
            
            if volume_data:
                total_volume = volume_data['total_volume']
                buy_volume = volume_data['buy_volume']
                sell_volume = volume_data['sell_volume']
                buy_ratio = volume_data['buy_ratio']
                sell_ratio = volume_data['sell_ratio']
                
                # 更新进度条
                self.buy_progress['value'] = buy_ratio * 100
                self.sell_progress['value'] = sell_ratio * 100
                
                # 更新标签
                self.buy_label.config(text=f"买入量: {buy_volume:,.0f} 股 ({buy_ratio:.1%})")
                self.sell_label.config(text=f"卖出量: {sell_volume:,.0f} 股 ({sell_ratio:.1%})")
                
                # 更新买卖量信息
                volume_info = f"总成交量: {total_volume:,.0f} 股 | 买入: {buy_ratio:.1%} | 卖出: {sell_ratio:.1%}"
                self.volume_info_label.config(text=volume_info)
            else:
                self.volume_info_label.config(text="无法获取买卖量分解数据")
                self.buy_label.config(text="买入量: 未知")
                self.sell_label.config(text="卖出量: 未知")
        
        except Exception as e:
            self.volume_info_label.config(text=f"买卖量分解获取失败: {str(e)}")
    
    def start_auto_update(self):
        """开始自动更新"""
        def update_loop():
            while True:
                if self.current_symbol and not self.is_updating:
                    self.is_updating = True
                    try:
                        self.update_data()
                    finally:
                        self.is_updating = False
                time.sleep(30)  # 每30秒更新一次
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def on_closing(self):
        """关闭窗口时的处理"""
        self.root.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = AStockDashboard(root)
    
    # 设置关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 启动GUI
    root.mainloop()

if __name__ == "__main__":
    main()