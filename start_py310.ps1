# PowerShell启动脚本 - Python 3.10环境
Write-Host "Starting Python 3.10 Environment..." -ForegroundColor Green
Write-Host "Setting environment variables..." -ForegroundColor Yellow

# 设置环境变量
$env:SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYQLIB = "0.9.8"

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
# 激活虚拟环境
.\venv_py310\Scripts\Activate.ps1

Write-Host "Environment variables set, virtual environment activated" -ForegroundColor Green
Write-Host "Python version:" -ForegroundColor Cyan
python --version
Write-Host ""
Write-Host "Now you can run project scripts" -ForegroundColor Green
Write-Host "Example: python finetune/qlib_data_preprocess.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
Read-Host 