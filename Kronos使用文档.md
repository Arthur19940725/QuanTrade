# Kronos ʹ���ĵ�

## ?? ���ٿ�ʼ

### 1. ��װ����

#### Windows�������Ƽ���
```bash
# ����1��ʹ��PowerShell�ű�
.\install_windows.ps1

# ����2��ʹ���������ļ�
install_windows.bat

# ����3���ֶ���װ
git clone https://github.com/shiyu-coder/Kronos.git
cd Kronos
pip install -r requirements_updated.txt
```

#### Linux/Mac����
```bash
git clone https://github.com/shiyu-coder/Kronos.git
cd Kronos
pip install -r requirements.txt
```

### 2. ����ʹ��
```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# ����ģ��
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, device="cuda:0", max_context=512)

# ׼������
df = pd.read_csv("./data/your_data.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# Ԥ�����
lookback = 400
pred_len = 120

# ִ��Ԥ��
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

## ? Web����

### ����
```bash
cd webui
python app.py
```

### ����
- ��������ʣ�`http://localhost:5000`
- ѡ��ģ�� �� �ϴ����� �� ���ò��� �� ��ʼԤ��

## ? ģ��΢��

### 1. ����Ԥ����
```bash
cd finetune
# �༭config.py����·��
python qlib_data_preprocess.py
```

### 2. ѵ��ģ��
```bash
# ΢���ִ���
torchrun --standalone --nproc_per_node=2 train_tokenizer.py

# ΢��Ԥ����
torchrun --standalone --nproc_per_node=2 train_predictor.py
```

### 3. �ز�����
```bash
python qlib_test.py --device cuda:0
```

## ? ���ݸ�ʽҪ��

### ������
- `open`: ���̼�
- `high`: ��߼�
- `low`: ��ͼ�
- `close`: ���̼�

### ��ѡ��
- `volume`: �ɽ���
- `amount`: �ɽ���

### ʱ���
- ������`timestamps`��`timestamp`��`date`
- ��ʽ��֧��pandas�ɽ�����ʱ���ʽ

## ?? ���ò���

### ģ��ѡ��
- **Kronos-mini**: 4.1M������2048�����ĳ���
- **Kronos-small**: 24.7M������512�����ĳ��ȣ��Ƽ���
- **Kronos-base**: 102.3M������512�����ĳ���

### Ԥ�����
- `T`: �¶Ȳ�������������ԣ�0.1-2.0��
- `top_p`: �˲������ʣ�0.1-1.0��
- `sample_count`: ����������1-10��

## ?? �����ų�

### Python 3.13����������
�����ʹ��Python 3.13����ʹ�����½��������

```bash
# 1. ʹ�ø��µ�requirements�ļ�
pip install -r requirements_updated.txt

# 2. �����ֶ���װ���ݰ汾
pip install pandas>=2.3.0  # ֧��Python 3.13
pip install matplotlib>=3.9.0  # ֧��Python 3.13
pip install torch>=2.8.0  # ֧��Python 3.13
```

### CUDA�ڴ治��
```python
# ���������ĳ���
predictor = KronosPredictor(model, tokenizer, device="cuda:0", max_context=256)

# ��ʹ��CPU
predictor = KronosPredictor(model, tokenizer, device="cpu", max_context=512)
```

### ���ݸ�ʽ����
```python
# �������
print("����:", df.columns.tolist())

# ��������
df = df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'})
```

## ? ʾ������

### ����Ԥ��ʾ��
```bash
cd examples
python prediction_example.py
```

### �޳ɽ���Ԥ��
```bash
python prediction_wo_vol_example.py
```

## ? ��Դ����

- **GitHub**: https://github.com/shiyu-coder/Kronos
- **Hugging Face**: https://huggingface.co/NeoQuasar
- **������ʾ**: https://shiyu-coder.github.io/Kronos-demo/
- **����**: https://arxiv.org/abs/2508.02739

## ? ���ʵ��

1. **��������**: ȷ�����������Ժ�һ����
2. **ģ��ѡ��**: ���ݼ�����Դѡ����ʵ�ģ�͹�ģ
3. **��������**: ���ݾ�����������¶ȺͲ�������
4. **���ܼ��**: ���GPU�ڴ�ʹ�ú�Ԥ������
5. **�����֤**: �������֪ʶ��֤Ԥ�����ĺ�����

## ? ����֧��

- **Issues**: https://github.com/shiyu-coder/Kronos/issues
- **Discussions**: https://github.com/shiyu-coder/Kronos/discussions

---

*������ϸ��Ϣ��ο���ĿREADME.md��Kronosѧϰ�ĵ�.md* 