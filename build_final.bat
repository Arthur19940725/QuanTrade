@echo off
chcp 65001 >nul
echo ========================================
echo QuantPredict Pro Enhanced - Final Build
echo ========================================

:: Activate virtual environment
call venv_py311\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install requests numpy matplotlib pyinstaller akshare pandas tushare yfinance

:: Clean previous builds and all history versions
echo Cleaning all build directories and history files...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec
if exist "__pycache__" rmdir /s /q __pycache__
if exist "*.pyc" del /q *.pyc
if exist "*.pyo" del /q *.pyo
if exist "*.pyd" del /q *.pyd
if exist ".pytest_cache" rmdir /s /q .pytest_cache
if exist ".coverage" del /q .coverage
if exist "htmlcov" rmdir /s /q htmlcov
if exist ".mypy_cache" rmdir /s /q .mypy_cache
if exist ".ruff_cache" rmdir /s /q .ruff_cache
echo All history files cleaned successfully!

:: Build the application
echo Building application...
pyinstaller --onefile --windowed --name="QuantPredictProEnhanced" --exclude-module=torch --exclude-module=transformers --exclude-module=plotly --exclude-module=qlib --exclude-module=jupyter --exclude-module=IPython --exclude-module=pytest --exclude-module=scipy --exclude-module=sklearn --exclude-module=huggingface_hub --hidden-import=matplotlib.backends.backend_tkagg --hidden-import=numpy --hidden-import=requests --hidden-import=tkinter --hidden-import=pandas --hidden-import=akshare --hidden-import=tushare --hidden-import=yfinance --hidden-import=datetime --hidden-import=threading --hidden-import=json --hidden-import=ssl --hidden-import=urllib3 simple_stock_predictor.py

:: Check if build was successful
:: Get file size first
set size=0
set sizeMB=0
if exist "dist\QuantPredictProEnhanced.exe" (
    for %%I in ("dist\QuantPredictProEnhanced.exe") do set size=%%~zI
    set /a sizeMB=!size!/1024/1024
)

if exist "dist\QuantPredictProEnhanced.exe" (
    echo.
    echo Build successful!
    echo Executable: dist\QuantPredictProEnhanced.exe
    echo Size: !sizeMB! MB
    
    :: Create directories
    mkdir "dist\models" 2>nul
    mkdir "dist\data" 2>nul
    mkdir "dist\cache" 2>nul
    
    :: Copy additional files (A股和汇率功能已集成到主程序中)
    copy "enhanced_a_stock_fetcher.py" "dist\" 2>nul
    copy "cn_stock_fetcher.py" "dist\" 2>nul
    copy "currency_converter.py" "dist\" 2>nul
    copy "data_source_manager.py" "dist\" 2>nul
    copy "price_validator.py" "dist\" 2>nul
    
    :: Create launcher
    (
        echo @echo off
        echo chcp 65001 ^>nul
        echo echo ========================================
        echo echo QuantPredict Pro Enhanced Launcher
        echo echo ========================================
        echo echo 1. Main Program [Stock Predictor]
        echo echo 2. A-Stock Dashboard
        echo echo 3. Exit
        echo echo ========================================
        echo set /p choice=Please select [1-3]: 
        echo if "%%choice%%"=="1" ^(
        echo     echo Starting main program...
        echo     QuantPredictProEnhanced.exe
        echo ^) else if "%%choice%%"=="2" ^(
        echo     echo Starting A-Stock Dashboard...
        echo     python a_stock_dashboard.py
        echo ^) else if "%%choice%%"=="3" ^(
        echo     echo Goodbye!
        echo     exit
        echo ^) else ^(
        echo     echo Invalid choice, please try again
        echo     pause
        echo ^)
    ) > "dist\launcher.bat"
    
    :: Create README
    (
        echo QuantPredict Pro Enhanced v2.0
        echo ================================
        echo.
        echo Features:
        echo - Professional quantitative analysis
        echo - Smart stock prediction algorithms
        echo - Apple iOS style interface
        echo - Real-time data integration
        echo - Multi-dimensional data visualization
        echo - A-Stock real-time analysis (integrated)
        echo - USD/CNY exchange rate conversion
        echo - Volume breakdown display
        echo - Multi-data source support (TuShare/yfinance)
        echo.
        echo Supported Markets:
        echo - US Stocks: AAPL, MSFT, GOOGL, TSLA, NVDA
        echo - Cryptocurrency: BTC, ETH, BNB, SOL, ADA
        echo - A-Stocks: 600519, 000858, 000001, 000002
        echo.
        echo How to Use:
        echo 1. Run launcher.bat to select program
        echo 2. Or directly run QuantPredictProEnhanced.exe
        echo 3. Or run python a_stock_dashboard.py for A-Stock dashboard
        echo.
        echo Designer: Arthur
        echo Contact: 1945673686@qq.com
        echo Version: v2.0 Enhanced
        echo Build Date: %date% %time%
    ) > "dist\README.txt"
    
    echo.
    echo ========================================
    echo Build completed successfully!
    echo Main Program: QuantPredictProEnhanced.exe
    echo A-Stock Dashboard: a_stock_dashboard.py
    echo Launcher: launcher.bat
    echo README: README.txt
    echo Size: %sizeMB% MB
    echo ========================================
    echo.
    echo You can now run:
    echo - launcher.bat (select program)
    echo - QuantPredictProEnhanced.exe (main program)
    echo - python a_stock_dashboard.py (A-Stock dashboard)
    echo.
) else (
    echo.
    echo Build failed!
    echo Please check error messages and try again
    echo.
)

pause