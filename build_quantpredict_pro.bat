@echo off
echo ========================================
echo 📊 QuantPredict Pro - 量化预测专业版打包
echo ========================================

:: 激活虚拟环境
call venv_py311\Scripts\activate.bat

:: 安装必要依赖
echo 📦 确保必要依赖已安装...
pip install requests numpy matplotlib pyinstaller

:: 清理之前的构建
echo 🧹 清理构建目录...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

:: 打包应用程序
echo 🚀 开始打包 QuantPredict Pro...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name="QuantPredictPro" ^
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
if exist "dist\QuantPredictPro.exe" (
    echo.
    echo ✅ 打包成功！
    echo 📁 程序位置: dist\QuantPredictPro.exe
    
    :: 显示文件信息
    for %%I in ("dist\QuantPredictPro.exe") do (
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
        echo 📊 QuantPredict Pro - 量化预测专业版 v1.0
        echo.
        echo 🎯 产品特色:
        echo • 专业级量化分析工具
        echo • 智能股票预测算法
        echo • Apple iOS风格界面设计
        echo • 实时数据集成分析
        echo • 多维度数据可视化
        echo.
        echo 👨‍💻 设计者信息:
        echo • 设计者: Arthur
        echo • 联系方式: 1945673686@qq.com
        echo • 界面风格: Apple iOS设计语言
        echo.
        echo 🎯 使用方法:
        echo 1. 双击 QuantPredictPro.exe 启动程序
        echo 2. 在搜索框输入股票代码或名称
        echo    美股示例: AAPL、苹果、MSFT、微软
        echo    加密货币: BTC、比特币、ETH、以太坊
        echo 3. 双击搜索结果选择股票
        echo 4. 点击"🔄 刷新价格"获取最新实时价格
        echo 5. 设置预测天数^(1-30天^)
        echo 6. 点击"🚀 开始预测"查看结果
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
        echo 📊 核心功能:
        echo • 实时价格获取: Finnhub API ^(美股^) + Binance API ^(加密货币^)
        echo • 历史+预测价格走势图: 前半部分历史，后半部分预测
        echo • 价格区间分析: 显示预测价格的最大最小范围
        echo • 交易量预测: 历史交易量 vs 预测交易量对比
        echo • 多维度数据可视化: 图表、表格、摘要多角度展示
        echo.
        echo 🎨 界面特色:
        echo • Apple iOS风格设计: 简洁、现代、专业
        echo • SF Pro字体: 苹果官方字体，视觉体验佳
        echo • 卡片式布局: 清晰的信息层次结构
        echo • 响应式交互: 流畅的用户操作体验
        echo • 专业配色: iOS标准色彩体系
        echo.
        echo 📡 数据源:
        echo • Finnhub API: 美股专业实时价格
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
        echo • 如遇问题，请联系设计者: 1945673686@qq.com
        echo.
        echo 版本: v1.0
        echo 更新时间: %date% %time%
        echo 设计者: Arthur
    ) > "dist\使用说明.txt"
    
    echo.
    echo ========================================
    echo ✅ QuantPredict Pro 打包完成！
    echo 📦 程序: QuantPredictPro.exe
    echo 📚 说明: 使用说明.txt
    echo 🎯 大小: %sizeMB% MB
    echo 💫 特色: Apple iOS风格界面
    echo 👨‍💻 设计者: Arthur
    echo ========================================
    echo.
    echo 🚀 现在可以运行: dist\QuantPredictPro.exe
    echo 💡 或者分发整个 dist 文件夹给其他用户使用
    echo.
) else (
    echo.
    echo ❌ 打包失败！
    echo 请检查错误信息并重试
    echo.
)

pause