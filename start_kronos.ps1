# Kronos 项目启动脚本 - PowerShell版本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Kronos 项目启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. 激活Python 3.10虚拟环境..." -ForegroundColor Yellow
.\venv_py310\Scripts\Activate.ps1

Write-Host "2. 设置环境变量..." -ForegroundColor Yellow
$env:SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYQLIB = "0.9.8"
$env:PYTHONPATH = "D:\code\Kronos"

Write-Host "3. 检查Python版本..." -ForegroundColor Yellow
python --version

Write-Host ""
Write-Host "4. 环境设置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "可用的命令：" -ForegroundColor Cyan
Write-Host "  - python examples/prediction_example.py     (运行预测示例)" -ForegroundColor White
Write-Host "  - python webui/app.py                      (启动Web界面)" -ForegroundColor White
Write-Host "  - python finetune/qlib_data_preprocess.py  (数据预处理)" -ForegroundColor White
Write-Host ""
Write-Host "按任意键继续..." -ForegroundColor Yellow
Read-Host