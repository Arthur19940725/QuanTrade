@echo off
REM 设置环境变量禁用libuv
set USE_LIBUV=0

REM 激活虚拟环境
call venv_py311\Scripts\activate.bat

REM 运行训练脚本
torchrun --standalone --nproc_per_node=1 finetune/train_predictor.py

pause