# Kronos训练 - torchrun libuv问题完整解决方案
# Windows下PyTorch torchrun libuv支持问题的多种解决方案

param(
    [Parameter(Position=0)]
    [string]$Solution = "help",
    [string]$nproc_per_node = "1",
    [string]$script = "finetune/train_predictor.py"
)

Write-Host "🚀 Kronos训练 - torchrun libuv问题解决方案" -ForegroundColor Green
Write-Host "📋 Windows下PyTorch分布式训练修复工具" -ForegroundColor Yellow
Write-Host ""

switch ($Solution.ToLower()) {
    "help" {
        Write-Host "可用解决方案:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. 基础修复方案:" -ForegroundColor White
        Write-Host "   .\torchrun_solutions.ps1 basic" -ForegroundColor Gray
        Write-Host "   - 使用环境变量禁用libuv" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. 完整替代方案:" -ForegroundColor White  
        Write-Host "   .\torchrun_solutions.ps1 alternative" -ForegroundColor Gray
        Write-Host "   - 完全绕过torchrun，直接启动训练" -ForegroundColor Gray
        Write-Host ""
        Write-Host "3. 路径修复方案:" -ForegroundColor White
        Write-Host "   .\torchrun_solutions.ps1 pathfix" -ForegroundColor Gray
        Write-Host "   - 修复模型路径 + 绕过torchrun" -ForegroundColor Gray
        Write-Host ""
        Write-Host "4. CPU训练方案:" -ForegroundColor White
        Write-Host "   .\torchrun_solutions.ps1 cpu" -ForegroundColor Gray
        Write-Host "   - 强制CPU训练，解决CUDA兼容性问题" -ForegroundColor Gray
        Write-Host ""
        Write-Host "5. 推荐方案 (自动选择):" -ForegroundColor White
        Write-Host "   .\torchrun_solutions.ps1 recommended" -ForegroundColor Gray
        Write-Host "   - 自动检测并使用最佳方案" -ForegroundColor Gray
        Write-Host ""
        Write-Host "原始torchrun命令等价用法:" -ForegroundColor Yellow
        Write-Host "torchrun --standalone --nproc_per_node=1 finetune/train_predictor.py" -ForegroundColor Red
        Write-Host "↓ 替换为 ↓" -ForegroundColor Yellow  
        Write-Host ".\torchrun_solutions.ps1 recommended" -ForegroundColor Green
    }
    
    "basic" {
        Write-Host "🔧 方案1: 基础环境变量修复" -ForegroundColor Blue
        $env:USE_LIBUV = "0"
        Write-Host "设置 USE_LIBUV=0"
        Write-Host "执行: torchrun --standalone --nproc_per_node=$nproc_per_node $script" -ForegroundColor Gray
        & torchrun --standalone --nproc_per_node=$nproc_per_node $script
    }
    
    "alternative" {
        Write-Host "🔧 方案2: 完整替代方案" -ForegroundColor Blue
        Write-Host "使用自定义启动器替代torchrun" -ForegroundColor Gray
        & python torchrun_alternative.py --standalone --nproc_per_node=$nproc_per_node $script
    }
    
    "pathfix" {
        Write-Host "🔧 方案3: 路径修复方案" -ForegroundColor Blue  
        Write-Host "修复模型路径并启动训练" -ForegroundColor Gray
        & python torchrun_final_fix.py --train-predictor
    }
    
    "cpu" {
        Write-Host "🔧 方案4: CPU训练方案" -ForegroundColor Blue
        Write-Host "强制使用CPU，解决CUDA兼容性问题" -ForegroundColor Gray
        & python torchrun_cpu_fix.py --train-predictor
    }
    
    "recommended" {
        Write-Host "🔧 推荐方案: 自动选择最佳解决方案" -ForegroundColor Blue
        Write-Host ""
        Write-Host "检测系统环境..." -ForegroundColor Yellow
        
        # 检查CUDA是否可用
        $cudaAvailable = & python -c "import torch; print(torch.cuda.is_available())" 2>$null
        
        if ($cudaAvailable -eq "True") {
            Write-Host "✅ 检测到CUDA支持" -ForegroundColor Green
            Write-Host "🏃‍♂️ 使用GPU路径修复方案" -ForegroundColor Green
            & python torchrun_final_fix.py --train-predictor
        } else {
            Write-Host "⚠️  未检测到CUDA支持或存在兼容性问题" -ForegroundColor Yellow
            Write-Host "🏃‍♂️ 使用CPU训练方案" -ForegroundColor Yellow
            & python torchrun_cpu_fix.py --train-predictor
        }
    }
    
    default {
        Write-Host "❌ 未知方案: $Solution" -ForegroundColor Red
        Write-Host "使用 '.\torchrun_solutions.ps1 help' 查看可用方案" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 脚本执行完成!" -ForegroundColor Green