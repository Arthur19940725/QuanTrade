@echo off
echo ========================================
echo 🚀 Kronos 股票预测器 - 最终打包
echo ========================================

:: 激活虚拟环境
call venv_py311\Scripts\activate.bat

:: 安装最小依赖
echo 📦 确保必要依赖已安装...
pip install requests numpy matplotlib pyinstaller

:: 清理之前的构建
echo 🧹 清理构建目录...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

:: 简化打包 - 只包含必要组件
echo 🚀 开始最终打包...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="KronosStockPredictor" ^
    --exclude-module=torch ^
    --exclude-module=transformers ^
    --exclude-module=pandas ^
    --exclude-module=plotly ^
    --exclude-module=qlib ^
    --exclude-module=jupyter ^
    --exclude-module=IPython ^
    --exclude-module=pytest ^
    --exclude-module=scipy ^
    --exclude-module=sklearn ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=numpy ^
    --hidden-import=requests ^
    --hidden-import=tkinter ^
    simple_stock_predictor.py

:: 检查结果
if exist "dist\KronosStockPredictor.exe" (
    echo.
    echo ✅ 打包成功！
    echo 📁 程序位置: dist\KronosStockPredictor.exe
    
    :: 显示文件信息
    for %%I in ("dist\KronosStockPredictor.exe") do (
        set size=%%~zI
        set /a sizeMB=!size!/1024/1024
    )
    echo 📊 程序大小: %sizeMB% MB
    
    :: 创建程序目录
    echo 📁 创建程序目录...
    mkdir "dist\models" 2>nul
    mkdir "dist\data" 2>nul
    mkdir "dist\cache" 2>nul
    
    :: 创建详细说明
    echo 📝 创建使用说明...
    (
        echo 🚀 Kronos股票预测器 - 独立版 v1.0
        echo.
        echo 📋 程序特性:
        echo • 独立运行，无需安装Python环境
        echo • 支持美股、加密货币实时价格预测
        echo • 集成Finnhub和Binance API
        echo • 高级价格走势图表
        echo • 价格区间和交易量预测
        echo • 中文界面，操作简单
        echo.
        echo 🎯 使用方法:
        echo 1. 双击 KronosStockPredictor.exe 启动程序
        echo 2. 在搜索框输入股票代码或名称
        echo    美股示例: AAPL、苹果、MSFT、微软
        echo    加密货币: BTC、比特币、ETH、以太坊
        echo 3. 双击搜索结果选择股票
        echo 4. 点击"刷新价格"获取最新实时价格
        echo 5. 设置预测天数^(1-30天^)
        echo 6. 点击"开始预测"查看结果
        echo 7. 切换标签页查看不同视图:
        echo    • 预测摘要: 详细分析结果
        echo    • 价格走势图: 历史+预测价格曲线
        echo    • 交易量图: 历史+预测交易量
        echo    • 详细数据: 完整预测数据表格
        echo.
        echo 🌍 支持股票:
        echo • 美股: AAPL^(苹果^)、MSFT^(微软^)、GOOGL^(谷歌^)、TSLA^(特斯拉^)、NVDA^(英伟达^)、META^(Meta^)、AMZN^(亚马逊^)
        echo • 加密货币: BTC^(比特币^)、ETH^(以太坊^)、BNB^(币安币^)、SOL^(索拉纳^)、ADA^(艾达币^)、DOGE^(狗狗币^)
        echo.
        echo 📊 图表功能:
        echo • 价格走势图: 前半部分显示历史价格，后半部分显示预测价格
        echo • 价格区间: 显示预测价格的最大最小范围^(绿色阴影区域^)
        echo • 交易量图: 历史交易量^(蓝色^) vs 预测交易量^(红色^)
        echo • 数据表格: 包含价格区间和交易量预测的详细数据
        echo.
        echo 📡 数据源:
        echo • Finnhub API: 美股实时价格
        echo • Binance API: 加密货币实时价格
        echo • 技术分析算法: 基于历史数据的智能预测
        echo.
        echo ⚠️ 重要提示:
        echo • 需要网络连接获取实时数据
        echo • 预测结果仅供参考，不构成投资建议
        echo • 股市有风险，投资需谨慎
        echo • 建议结合多种分析方法做决策
        echo.
        echo 🔧 技术支持:
        echo • 程序会在运行目录下创建models、data、cache文件夹
        echo • 所有数据和配置都保存在程序目录下
        echo • 如遇问题，请检查网络连接和防火墙设置
        echo.
        echo 版本: v1.0
        echo 更新时间: %date% %time%
    ) > "dist\使用说明.txt"
    
    echo.
    echo ========================================
    echo ✅ 最终打包完成！
    echo 📦 程序: KronosStockPredictor.exe
    echo 📚 说明: 使用说明.txt
    echo 🎯 大小: %sizeMB% MB
    echo 💫 功能: 完整的股票预测分析工具
    echo ========================================
    echo.
    echo 🚀 现在可以运行: dist\KronosStockPredictor.exe
    echo 💡 或者分发整个 dist 文件夹给其他用户使用
    echo.
) else (
    echo.
    echo ❌ 打包失败！
    echo 请检查错误信息并重试
    echo.
)

pause