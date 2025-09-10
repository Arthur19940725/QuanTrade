# Kronos 使用文档

## ?? 快速开始

### 1. 安装依赖

#### Windows环境（推荐）
```bash
# 方法1：使用PowerShell脚本
.\install_windows.ps1

# 方法2：使用批处理文件
install_windows.bat

# 方法3：手动安装
git clone https://github.com/shiyu-coder/Kronos.git
cd Kronos
pip install -r requirements_updated.txt
```

#### Linux/Mac环境
```bash
git clone https://github.com/shiyu-coder/Kronos.git
cd Kronos
pip install -r requirements.txt
```

### 2. 基础使用
```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# 加载模型
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, device="cuda:0", max_context=512)

# 准备数据
df = pd.read_csv("./data/your_data.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 预测参数
lookback = 400
pred_len = 120

# 执行预测
x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']

pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9,
    sample_count=1
)
```

## ? Web界面

### 启动
```bash
cd webui
python app.py
```

### 访问
- 浏览器访问：`http://localhost:5000`
- 选择模型 → 上传数据 → 配置参数 → 开始预测

## ? 模型微调

### 1. 数据预处理
```bash
cd finetune
# 编辑config.py配置路径
python qlib_data_preprocess.py
```

### 2. 训练模型
```bash
# 微调分词器
torchrun --standalone --nproc_per_node=2 train_tokenizer.py

# 微调预测器
torchrun --standalone --nproc_per_node=2 train_predictor.py
```

### 3. 回测评估
```bash
python qlib_test.py --device cuda:0
```

## ? 数据格式要求

### 必需列
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价

### 可选列
- `volume`: 成交量
- `amount`: 成交额

### 时间戳
- 列名：`timestamps`、`timestamp`或`date`
- 格式：支持pandas可解析的时间格式

## ?? 配置参数

### 模型选择
- **Kronos-mini**: 4.1M参数，2048上下文长度
- **Kronos-small**: 24.7M参数，512上下文长度（推荐）
- **Kronos-base**: 102.3M参数，512上下文长度

### 预测参数
- `T`: 温度参数，控制随机性（0.1-2.0）
- `top_p`: 核采样概率（0.1-1.0）
- `sample_count`: 采样次数（1-10）

## ?? 故障排除

### Python 3.13兼容性问题
如果您使用Python 3.13，请使用以下解决方案：

```bash
# 1. 使用更新的requirements文件
pip install -r requirements_updated.txt

# 2. 或者手动安装兼容版本
pip install pandas>=2.3.0  # 支持Python 3.13
pip install matplotlib>=3.9.0  # 支持Python 3.13
pip install torch>=2.8.0  # 支持Python 3.13
```

### CUDA内存不足
```python
# 减少上下文长度
predictor = KronosPredictor(model, tokenizer, device="cuda:0", max_context=256)

# 或使用CPU
predictor = KronosPredictor(model, tokenizer, device="cpu", max_context=512)
```

### 数据格式错误
```python
# 检查列名
print("列名:", df.columns.tolist())

# 重命名列
df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
```

## ? 示例代码

### 完整预测示例
```bash
cd examples
python prediction_example.py
```

### 无成交量预测
```bash
python prediction_wo_vol_example.py
```

## ? 资源链接

- **GitHub**: https://github.com/shiyu-coder/Kronos
- **Hugging Face**: https://huggingface.co/NeoQuasar
- **在线演示**: https://shiyu-coder.github.io/Kronos-demo/
- **论文**: https://arxiv.org/abs/2508.02739

## ? 最佳实践

1. **数据质量**: 确保数据完整性和一致性
2. **模型选择**: 根据计算资源选择合适的模型规模
3. **参数调优**: 根据具体任务调整温度和采样参数
4. **性能监控**: 监控GPU内存使用和预测质量
5. **结果验证**: 结合领域知识验证预测结果的合理性

## ? 技术支持

- **Issues**: https://github.com/shiyu-coder/Kronos/issues
- **Discussions**: https://github.com/shiyu-coder/Kronos/discussions

---

*更多详细信息请参考项目README.md和Kronos学习文档.md* 