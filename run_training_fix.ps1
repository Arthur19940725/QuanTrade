# Kronos训练启动脚本 - Windows libuv问题修复版本
# 使用方法: .\run_training_fix.ps1

Write-Host "🚀 启动Kronos预测器训练..." -ForegroundColor Green
Write-Host "📋 修复Windows下torchrun libuv问题" -ForegroundColor Yellow

# 设置环境变量以禁用libuv
$env:USE_LIBUV = "0"
$env:WORLD_SIZE = "1"
$env:RANK = "0"
$env:LOCAL_RANK = "0"
$env:MASTER_ADDR = "localhost"
$env:MASTER_PORT = "12355"

Write-Host "✅ 环境变量设置完成:" -ForegroundColor Green
Write-Host "   USE_LIBUV: $env:USE_LIBUV"
Write-Host "   WORLD_SIZE: $env:WORLD_SIZE"
Write-Host "   RANK: $env:RANK"
Write-Host "   LOCAL_RANK: $env:LOCAL_RANK"

# 激活虚拟环境（如果存在）
if (Test-Path ".\venv_py311\Scripts\activate.ps1") {
    Write-Host "🔧 激活虚拟环境..." -ForegroundColor Blue
    & .\venv_py311\Scripts\activate.ps1
}

# 运行修复版本的训练脚本
Write-Host "🏃‍♂️ 开始训练..." -ForegroundColor Green
python run_training_fix.py

Write-Host "🎉 训练脚本执行完成!" -ForegroundColor Green