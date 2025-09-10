@echo off
chcp 65001
title Kronos 加密货币预测器
color 0A

echo.
echo ================================================
echo    🚀 Kronos 加密货币预测器
echo ================================================
echo.
echo 正在启动应用...
echo.

REM 激活虚拟环境 (如果存在)
if exist "venv_py311\Scripts\activate.bat" (
    echo ✓ 激活Python虚拟环境
    call venv_py311\Scripts\activate.bat
)

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo ✓ 检查依赖包...
python -c "import tkinter, matplotlib, pandas, numpy, requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠ 正在安装必要依赖...
    pip install matplotlib pandas numpy requests >nul 2>&1
)

REM 选择版本
echo.
echo 选择要运行的版本:
echo.
echo [1] 💎 完整版 - 基于Kronos深度学习模型
echo [2] ⚡ 轻量版 - 基于技术分析 (推荐)
echo [3] 🔧 打包成exe文件
echo.
set /p choice=请输入选择 (1/2/3): 

if "%choice%"=="1" (
    echo.
    echo 🚀 启动完整版...
    python crypto_predictor_app.py
) else if "%choice%"=="2" (
    echo.
    echo ⚡ 启动轻量版...
    python crypto_predictor_lite.py
) else if "%choice%"=="3" (
    echo.
    echo 🔧 开始打包...
    call build_exe_final.bat
) else (
    echo.
    echo 默认启动轻量版...
    python crypto_predictor_lite.py
)

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，请检查错误信息
    echo.
    echo 常见解决方案:
    echo 1. 确保Python已正确安装
    echo 2. 运行: pip install matplotlib pandas numpy requests
    echo 3. 检查网络连接
    echo.
)

pause