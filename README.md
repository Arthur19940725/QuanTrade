# QuantPredict Pro - 量化预测专业版

一个基于Kronos模型的多市场股票预测系统，支持A股、港股、美股和加密货币的智能预测。

## 🚀 主要功能

- **多市场支持**: A股、港股、美股、加密货币
- **智能预测**: 基于Kronos时间序列模型
- **实时数据**: 多数据源fallback机制
- **技术分析**: 高级技术指标分析
- **可视化**: 交互式图表展示
- **用户界面**: 现代化GUI界面

## 📋 系统要求

- Python 3.8+
- Windows 10/11
- 8GB+ RAM (推荐16GB)
- 2GB+ 可用磁盘空间

## 🛠️ 安装指南

### 1. 克隆仓库
```bash
git clone https://github.com/Arthur19940725/QuanTrade.git
cd QuanTrade
```

### 2. 创建虚拟环境
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 下载模型文件
由于模型文件较大，需要单独下载：

```bash
# 下载Kronos模型
python download_models.py
```

或者手动下载模型到 `models/` 目录：
- Kronos-small: https://huggingface.co/NeoQuasar/Kronos-small
- Kronos-base: https://huggingface.co/NeoQuasar/Kronos-base
- Kronos-mini: https://huggingface.co/NeoQuasar/Kronos-mini

## 🎯 快速开始

### 启动主程序
```bash
python stock_predictor.py
```

### 启动加密货币预测器
```bash
python crypto_predictor_app.py
```

### 启动A股仪表板
```bash
python a_stock_dashboard.py
```

## 📊 支持的市场

| 市场 | 代码示例 | 数据源 |
|------|----------|--------|
| A股 | 600519, 000858 | akshare, 东方财富 |
| 港股 | 0700, 0941 | Yahoo Finance |
| 美股 | AAPL, MSFT | Yahoo Finance, Finnhub |
| 加密货币 | BTC, ETH | Binance, CoinGecko |

## 🔧 配置说明

### API密钥配置
在 `data_source_manager.py` 中配置您的API密钥：

```python
# Finnhub API (美股实时数据)
FINNHUB_API_KEY = "your_api_key_here"

# 其他数据源配置
```

### 数据源优先级
1. **A股**: akshare > 东方财富 > 模拟数据
2. **美股**: Yahoo Finance > Alpha Vantage > Finnhub
3. **港股**: Yahoo Finance > 模拟数据
4. **加密货币**: Binance > CoinGecko > 模拟数据

## 📈 使用示例

```python
from stock_predictor import MultiMarketStockPredictor

# 创建预测器
predictor = MultiMarketStockPredictor()

# 搜索股票
results = predictor.search_stocks("苹果")
print(results)

# 预测股票价格
prediction = predictor.predict_stock("AAPL", "us_stocks", pred_days=7)
if prediction['success']:
    print(f"预测结果: {prediction['summary']}")
```

## 🏗️ 项目结构

```
QuantPredictPro/
├── stock_predictor.py          # 主预测器
├── data_source_manager.py      # 数据源管理
├── enhanced_a_stock_fetcher.py # A股数据获取
├── crypto_predictor_app.py     # 加密货币预测器
├── a_stock_dashboard.py        # A股仪表板
├── simple_stock_predictor.py   # 简化版预测器
├── standalone_stock_predictor.py # 独立版预测器
├── models/                     # 模型文件目录
├── cache/                      # 缓存目录
├── data/                       # 数据目录
└── requirements.txt            # 依赖文件
```

## 🔄 数据修复

最新版本已修复以下问题：
- ✅ 加密货币历史数据时间排序
- ✅ A股历史数据去重和清洗
- ✅ 数据源fallback机制优化
- ✅ 缓存结构统一化
- ✅ 时间列格式标准化

## 📝 更新日志

### v2.0.0 (2024-09-06)
- 新增多市场支持
- 优化数据获取机制
- 修复历史数据准确性问题
- 改进用户界面

### v1.0.0 (2024-08-31)
- 初始版本发布
- 基础预测功能
- Kronos模型集成

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式
Email: 1945673686@qq.com

如有问题，请提交Issue或联系开发者。

---

**注意**: 本项目仅供学习和研究使用，不构成投资建议。投资有风险，请谨慎决策。
