# Kronos训练 - torchrun libuv问题修复版本
# 用法: .\torchrun_fix.ps1 --standalone --nproc_per_node=1 finetune/train_predictor.py
# 或者: .\torchrun_fix.ps1 --train-predictor

param(
    [string]$standalone,
    [string]$nproc_per_node,
    [string]$script,
    [switch]$train_predictor,
    [switch]$train_tokenizer,
    [switch]$train_all,
    [switch]$help
)

Write-Host "🚀 Kronos训练 - torchrun修复版本" -ForegroundColor Green
Write-Host "📋 解决Windows下PyTorch libuv支持问题" -ForegroundColor Yellow

if ($help) {
    Write-Host "使用方法:" -ForegroundColor Cyan
    Write-Host "  .\torchrun_fix.ps1 --standalone --nproc_per_node=1 finetune/train_predictor.py"
    Write-Host "  .\torchrun_fix.ps1 -train_predictor"
    Write-Host "  .\torchrun_fix.ps1 -train_tokenizer" 
    Write-Host "  .\torchrun_fix.ps1 -train_all"
    exit 0
}

# 激活虚拟环境（如果存在）
if (Test-Path ".\venv_py311\Scripts\activate.ps1") {
    Write-Host "🔧 激活虚拟环境..." -ForegroundColor Blue
    & .\venv_py311\Scripts\activate.ps1
}

# 构建Python命令
$pythonArgs = @("torchrun_complete_fix.py")

if ($standalone) {
    $pythonArgs += "--standalone"
}

if ($nproc_per_node) {
    $pythonArgs += "--nproc_per_node=$nproc_per_node"
}

if ($train_all) {
    $pythonArgs += "--train-all"
} elseif ($train_tokenizer) {
    $pythonArgs += "--train-tokenizer"
} elseif ($train_predictor) {
    $pythonArgs += "--train-predictor"
} elseif ($script) {
    $pythonArgs += $script
}

Write-Host "🏃‍♂️ 执行命令: python $($pythonArgs -join ' ')" -ForegroundColor Green

# 运行Python脚本
& python @pythonArgs

Write-Host "🎉 脚本执行完成!" -ForegroundColor Green