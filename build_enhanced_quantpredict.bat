@echo off
echo ========================================
echo 📊 QuantPredict Pro Enhanced - 增强版打包
echo ========================================
echo 🎯 包含功能:
echo • A股数据修复与增强
echo • 买卖量分解显示
echo • 多数据源支持
echo • 增强型数据获取器
echo • A股数据仪表板
echo ========================================

:: 激活虚拟环境
call venv_py311\Scripts\activate.bat

:: 安装必要依赖
echo 📦 安装必要依赖...
pip install requests numpy matplotlib pyinstaller akshare pandas

:: 清理之前的构建
echo 🧹 清理构建目录...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

:: 创建新的spec文件
echo 📝 创建打包配置...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo a = Analysis^(
echo     ['simple_stock_predictor.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=[
echo         'matplotlib.backends.backend_tkagg',
echo         'numpy',
echo         'requests',
echo         'tkinter',
echo         'pandas',
echo         'akshare',
echo         'datetime',
echo         'threading',
echo         'json',
echo         'ssl',
echo         'urllib3'
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[
echo         'torch',
echo         'transformers',
echo         'plotly',
echo         'qlib',
echo         'jupyter',
echo         'IPython',
echo         'pytest',
echo         'scipy',
echo         'sklearn',
echo         'huggingface_hub'
echo     ],
echo     noarchive=False,
echo     optimize=0,
echo ^)
echo pyz = PYZ^(a.pure^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.datas,
echo     [],
echo     name='QuantPredictProEnhanced',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
) > QuantPredictProEnhanced.spec

:: 打包应用程序
echo 🚀 开始打包 QuantPredict Pro Enhanced...
pyinstaller QuantPredictProEnhanced.spec

:: 检查结果
if exist "dist\QuantPredictProEnhanced.exe" (
    echo.
    echo ✅ 打包成功！
    echo 📁 程序位置: dist\QuantPredictProEnhanced.exe
    
    :: 显示文件信息
    for %%I in ("dist\QuantPredictProEnhanced.exe") do (
        set size=%%~zI
        set /a sizeMB=!size!/1024/1024
    )
    echo 📊 程序大小: %sizeMB% MB
    
    :: 创建程序目录
    echo 📁 创建程序目录...
    mkdir "dist\models" 2>nul
    mkdir "dist\data" 2>nul
    mkdir "dist\cache" 2>nul
    
    :: 复制A股数据仪表板
    echo 📊 复制A股数据仪表板...
    copy "a_stock_dashboard.py" "dist\" 2>nul
    copy "enhanced_a_stock_fetcher.py" "dist\" 2>nul
    copy "data_source_manager.py" "dist\" 2>nul
    copy "stock_predictor.py" "dist\" 2>nul
    
    :: 创建启动脚本
    echo 📝 创建启动脚本...
    (
        echo @echo off
        echo echo ========================================
        echo echo 📊 QuantPredict Pro Enhanced 启动器
        echo echo ========================================
        echo echo 选择要启动的程序:
        echo echo 1. 主程序 ^(股票预测器^)
        echo echo 2. A股数据仪表板
        echo echo 3. 退出
        echo echo ========================================
        echo set /p choice=请输入选择 ^(1-3^): 
        echo if "%%choice%%"=="1" ^(
        echo     echo 🚀 启动主程序...
        echo     QuantPredictProEnhanced.exe
        echo ^) else if "%%choice%%"=="2" ^(
        echo     echo 📊 启动A股数据仪表板...
        echo     python a_stock_dashboard.py
        echo ^) else if "%%choice%%"=="3" ^(
        echo     echo 👋 再见！
        echo     exit
        echo ^) else ^(
        echo     echo ❌ 无效选择，请重新运行
        echo     pause
        echo ^)
    ) > "dist\启动器.bat"
    
    :: 创建详细说明
    echo 📝 创建使用说明...
    (
        echo 📊 QuantPredict Pro Enhanced - 增强版量化预测工具 v2.0
        echo.
        echo 🎯 产品特色:
        echo • 专业级量化分析工具
        echo • 智能股票预测算法
        echo • Apple iOS风格界面设计
        echo • 实时数据集成分析
        echo • 多维度数据可视化
        echo • A股数据修复与增强
        echo • 买卖量分解显示
        echo • 多数据源支持
        echo.
        echo 👨‍💻 设计者信息:
        echo • 设计者: Arthur
        echo • 联系方式: 1945673686@qq.com
        echo • 界面风格: Apple iOS设计语言
        echo.
        echo 🚀 启动方式:
        echo 方式1: 双击 启动器.bat 选择程序
        echo 方式2: 直接双击 QuantPredictProEnhanced.exe 启动主程序
        echo 方式3: 运行 python a_stock_dashboard.py 启动A股仪表板
        echo.
        echo 🎯 主程序使用方法:
        echo 1. 在搜索框输入股票代码或名称
        echo    美股示例: AAPL、苹果、MSFT、微软
        echo    加密货币: BTC、比特币、ETH、以太坊
        echo    A股示例: 600519、贵州茅台、000858、五粮液
        echo 2. 双击搜索结果选择股票
        echo 3. 点击"🔄 刷新价格"获取最新实时价格
        echo 4. 设置预测天数^(1-30天^)
        echo 5. 点击"🚀 开始预测"查看结果
        echo 6. 切换标签页查看不同视图
        echo.
        echo 📊 A股数据仪表板使用方法:
        echo 1. 运行 python a_stock_dashboard.py
        echo 2. 在股票代码输入框输入A股代码
        echo 3. 或点击预设股票按钮快速选择
        echo 4. 查看实时价格和买卖量分解
        echo 5. 程序每30秒自动更新数据
        echo.
        echo 🌍 支持股票:
        echo • 美股: AAPL^(苹果^)、MSFT^(微软^)、GOOGL^(谷歌^)、TSLA^(特斯拉^)、NVDA^(英伟达^)
        echo • 加密货币: BTC^(比特币^)、ETH^(以太坊^)、BNB^(币安币^)、SOL^(索拉纳^)、ADA^(艾达币^)
        echo • A股: 600519^(贵州茅台^)、000858^(五粮液^)、000001^(平安银行^)、000002^(万科A^)
        echo.
        echo 📊 核心功能:
        echo • 实时价格获取: Finnhub API ^(美股^) + Binance API ^(加密货币^) + 多源API ^(A股^)
        echo • 历史+预测价格走势图: 前半部分历史，后半部分预测
        echo • 价格区间分析: 显示预测价格的最大最小范围
        echo • 交易量预测: 历史交易量 vs 预测交易量对比
        echo • A股买卖量分解: 显示买入量和卖出量比例
        echo • 多维度数据可视化: 图表、表格、摘要多角度展示
        echo.
        echo 🆕 新增功能:
        echo • A股数据修复: 解决A股价格不准确问题
        echo • 买卖量分解: 显示买入量和卖出量详细信息
        echo • 多数据源支持: 东方财富、新浪、腾讯等
        echo • 智能回退机制: 数据源失败时自动切换
        echo • A股数据仪表板: 专门的A股数据展示界面
        echo • 增强型数据获取器: 更稳定可靠的数据获取
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
        echo • 东方财富API: A股实时价格
        echo • 新浪财经API: A股备用数据源
        echo • 腾讯财经API: A股备用数据源
        echo • akshare库: A股历史数据
        echo.
        echo ⚠️ 重要提示:
        echo • 需要网络连接获取实时数据
        echo • 预测结果仅供参考，不构成投资建议
        echo • 股市有风险，投资需谨慎
        echo • 建议结合多种分析方法做决策
        echo • A股数据可能存在延迟，请以交易所为准
        echo.
        echo 🔧 技术支持:
        echo • 程序会在运行目录下创建models、data、cache文件夹
        echo • 所有数据和配置都保存在程序目录下
        echo • 如遇问题，请联系设计者: 1945673686@qq.com
        echo.
        echo 版本: v2.0 Enhanced
        echo 更新时间: %date% %time%
        echo 设计者: Arthur
    ) > "dist\使用说明.txt"
    
    echo.
    echo ========================================
    echo ✅ QuantPredict Pro Enhanced 打包完成！
    echo 📦 主程序: QuantPredictProEnhanced.exe
    echo 📊 A股仪表板: a_stock_dashboard.py
    echo 🚀 启动器: 启动器.bat
    echo 📚 说明: 使用说明.txt
    echo 🎯 大小: %sizeMB% MB
    echo 💫 特色: Apple iOS风格界面 + A股增强
    echo 👨‍💻 设计者: Arthur
    echo ========================================
    echo.
    echo 🚀 现在可以运行:
    echo • 启动器.bat - 选择程序启动
    echo • QuantPredictProEnhanced.exe - 直接启动主程序
    echo • python a_stock_dashboard.py - 启动A股仪表板
    echo.
    echo 💡 或者分发整个 dist 文件夹给其他用户使用
    echo.
) else (
    echo.
    echo ❌ 打包失败！
    echo 请检查错误信息并重试
    echo.
)

pause