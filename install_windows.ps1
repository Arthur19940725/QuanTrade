# Kronos Windows 安装脚本
# 解决Python 3.13兼容性问题

Write-Host "🚀 开始安装Kronos依赖..." -ForegroundColor Green

# 检查Python版本
$pythonVersion = python --version 2>&1
Write-Host "检测到Python版本: $pythonVersion" -ForegroundColor Yellow

# 检查pip
Write-Host "检查pip..." -ForegroundColor Blue
pip --version

# 安装核心依赖·
Write-Host "📦 安装核心依赖..." -ForegroundColor Green

# 安装PyTorch (CPU版本，兼容Python 3.13)
Write-Host "安装PyTorch..." -ForegroundColor Blue
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
Write-Host "安装其他依赖..." -ForegroundColor Blue
pip install numpy>=1.26.0
pip install pandas>=2.3.0
pip install einops>=0.8.0
pip install huggingface_hub>=0.33.0
pip install matplotlib>=3.9.0

# 安装Web界面依赖
Write-Host "🌐 安装Web界面依赖..." -ForegroundColor Green
pip install flask>=3.0.0
pip install flask-cors>=6.0.0
pip install plotly>=6.0.0

# 安装开发依赖
Write-Host "🔧 安装开发依赖..." -ForegroundColor Green
pip install tqdm>=4.42.0
pip install requests>=2.25.0

# 测试安装
Write-Host "🧪 测试安装..." -ForegroundColor Green
python -c "import torch; import pandas; import matplotlib; import flask; print('✅ 所有依赖安装成功！')"

# 测试Kronos模型
Write-Host "🧪 测试Kronos模型..." -ForegroundColor Green
python -c "from model import Kronos, KronosTokenizer, KronosPredictor; print('✅ Kronos模型导入成功！')"

Write-Host "🎉 安装完成！" -ForegroundColor Green
Write-Host "现在可以运行以下命令启动Web界面：" -ForegroundColor Yellow
Write-Host "cd webui" -ForegroundColor Cyan
Write-Host "python app.py" -ForegroundColor Cyan
Write-Host "然后在浏览器中访问: http://localhost:5000" -ForegroundColor Cyan 