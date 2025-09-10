@echo off
chcp 65001 >nul
echo 🚀 开始安装Kronos依赖...

echo 📦 安装核心依赖...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install numpy>=1.26.0
pip install pandas>=2.3.0
pip install einops>=0.8.0
pip install huggingface_hub>=0.33.0
pip install matplotlib>=3.9.0

echo 🌐 安装Web界面依赖...
pip install flask>=3.0.0
pip install flask-cors>=6.0.0
pip install plotly>=6.0.0

echo 🔧 安装开发依赖...
pip install tqdm>=4.42.0
pip install requests>=2.25.0

echo 🧪 测试安装...
python -c "import torch; import pandas; import matplotlib; import flask; print('✅ 所有依赖安装成功！')"

echo 🧪 测试Kronos模型...
python -c "from model import Kronos, KronosTokenizer, KronosPredictor; print('✅ Kronos模型导入成功！')"

echo 🎉 安装完成！
echo 现在可以运行以下命令启动Web界面：
echo cd webui
echo python app.py
echo 然后在浏览器中访问: http://localhost:5000

pause 