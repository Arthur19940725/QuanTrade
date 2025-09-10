@echo off
echo ========================================
echo 🚀 Kronos 股票预测器 EXE 打包工具
echo ========================================

:: 激活虚拟环境
call venv_py311\Scripts\activate.bat

:: 清理之前的构建
echo 🧹 清理之前的构建...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

:: 开始打包
echo 📦 开始打包程序...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="KronosStockPredictor" ^
    --distpath="dist" ^
    --workpath="build" ^
    --clean ^
    --noconfirm ^
    standalone_stock_predictor.py

:: 检查打包结果
if exist "dist\KronosStockPredictor.exe" (
    echo.
    echo ✅ 打包成功！
    echo 📁 程序位置: dist\KronosStockPredictor.exe
    echo 📊 程序大小: 
    dir "dist\KronosStockPredictor.exe" | findstr "KronosStockPredictor.exe"
    
    :: 创建目录结构
    echo.
    echo 📁 创建程序目录结构...
    mkdir "dist\models" 2>nul
    mkdir "dist\data" 2>nul
    mkdir "dist\cache" 2>nul
    mkdir "dist\logs" 2>nul
    
    :: 创建使用说明
    echo 📝 创建使用说明...
    echo 🚀 Kronos股票预测器 - 独立版 > "dist\使用说明.txt"
    echo. >> "dist\使用说明.txt"
    echo 📋 使用方法: >> "dist\使用说明.txt"
    echo 1. 双击 KronosStockPredictor.exe 启动程序 >> "dist\使用说明.txt"
    echo 2. 在搜索框输入股票代码或名称 >> "dist\使用说明.txt"
    echo 3. 双击选择股票 >> "dist\使用说明.txt"
    echo 4. 设置预测天数并点击预测 >> "dist\使用说明.txt"
    echo 5. 查看预测结果和图表 >> "dist\使用说明.txt"
    echo. >> "dist\使用说明.txt"
    echo 🌍 支持市场: >> "dist\使用说明.txt"
    echo • 美股: AAPL(苹果)、MSFT(微软)、GOOGL(谷歌)、TSLA(特斯拉) >> "dist\使用说明.txt"
    echo • 加密货币: BTC(比特币)、ETH(以太坊)、SOL(索拉纳) >> "dist\使用说明.txt"
    echo • 港股: 0700(腾讯)、0941(中国移动) >> "dist\使用说明.txt"
    echo • A股: 600519(贵州茅台)、000858(五粮液) >> "dist\使用说明.txt"
    echo. >> "dist\使用说明.txt"
    echo ⚡ 特色功能: >> "dist\使用说明.txt"
    echo • 实时价格获取 (Finnhub + Binance API) >> "dist\使用说明.txt"
    echo • 智能预测算法 >> "dist\使用说明.txt"
    echo • 图形化结果展示 >> "dist\使用说明.txt"
    echo • 本地数据存储 >> "dist\使用说明.txt"
    echo. >> "dist\使用说明.txt"
    echo 💡 注意: 预测结果仅供参考，投资有风险！ >> "dist\使用说明.txt"
    
    echo.
    echo ========================================
    echo ✅ 打包完成！
    echo 📦 程序包位置: dist\
    echo 🎯 主程序: KronosStockPredictor.exe
    echo 📚 使用说明: 使用说明.txt
    echo.
    echo 🚀 现在可以运行: dist\KronosStockPredictor.exe
    echo ========================================
) else (
    echo.
    echo ❌ 打包失败！
    echo 请检查错误信息并重试
)

pause