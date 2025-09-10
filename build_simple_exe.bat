@echo off
echo ========================================
echo 🚀 Kronos 简化版股票预测器打包工具
echo ========================================

:: 激活虚拟环境
call venv_py311\Scripts\activate.bat

:: 清理之前的构建
echo 🧹 清理之前的构建...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

:: 安装最小依赖
echo 📦 安装必要依赖...
pip install requests numpy pyinstaller

:: 开始简化打包
echo 🚀 开始打包简化版程序...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="KronosStockPredictor" ^
    --exclude-module=torch ^
    --exclude-module=transformers ^
    --exclude-module=pandas ^
    --exclude-module=matplotlib ^
    --exclude-module=plotly ^
    --exclude-module=qlib ^
    simple_stock_predictor.py

:: 检查结果
if exist "dist\KronosStockPredictor.exe" (
    echo.
    echo ✅ 打包成功！
    echo 📁 程序位置: dist\KronosStockPredictor.exe
    
    :: 获取文件大小
    for %%I in ("dist\KronosStockPredictor.exe") do echo 📊 程序大小: %%~zI 字节
    
    :: 创建目录
    mkdir "dist\models" 2>nul
    mkdir "dist\data" 2>nul
    mkdir "dist\cache" 2>nul
    
    :: 创建说明文件
    echo 🚀 Kronos股票预测器 - 简化版 > "dist\README.txt"
    echo. >> "dist\README.txt"
    echo 📋 使用方法: >> "dist\README.txt"
    echo 1. 双击 KronosStockPredictor.exe 启动 >> "dist\README.txt"
    echo 2. 搜索股票(如: AAPL、苹果、BTC) >> "dist\README.txt"
    echo 3. 双击选择股票 >> "dist\README.txt"
    echo 4. 刷新获取实时价格 >> "dist\README.txt"
    echo 5. 设置预测天数并开始预测 >> "dist\README.txt"
    echo. >> "dist\README.txt"
    echo 🌍 支持股票: >> "dist\README.txt"
    echo • 美股: AAPL、MSFT、GOOGL、TSLA、NVDA、META、AMZN >> "dist\README.txt"
    echo • 加密货币: BTC、ETH、BNB、SOL、ADA、DOGE >> "dist\README.txt"
    echo. >> "dist\README.txt"
    echo 📡 数据源: >> "dist\README.txt"
    echo • Finnhub API (美股实时价格) >> "dist\README.txt"
    echo • Binance API (加密货币实时价格) >> "dist\README.txt"
    echo. >> "dist\README.txt"
    echo ⚠️ 注意: 需要网络连接获取实时数据 >> "dist\README.txt"
    echo 💡 提示: 预测结果仅供参考，投资有风险！ >> "dist\README.txt"
    
    echo.
    echo ========================================
    echo ✅ 简化版打包完成！
    echo 📦 程序: dist\KronosStockPredictor.exe
    echo 📚 说明: dist\README.txt
    echo 🎯 特点: 小巧、快速、独立运行
    echo ========================================
) else (
    echo.
    echo ❌ 打包失败！
    echo 请检查错误信息
)

pause