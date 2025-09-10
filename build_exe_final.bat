@echo off
chcp 65001 >nul
echo ================================================
echo    Kronos 加密货币预测器打包工具
echo ================================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)

echo ✓ Python环境检查通过

REM 检查必要的包
echo 正在检查依赖包...
python -c "import tkinter, matplotlib, pandas, numpy, requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠ 缺少必要的包，正在安装...
    pip install matplotlib pandas numpy requests
)

echo ✓ 依赖包检查完成

REM 检查PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo ✓ PyInstaller已准备就绪

REM 选择要打包的版本
echo.
echo 选择要打包的版本:
echo 1. 完整版 (需要Kronos模型)
echo 2. 轻量版 (基于技术分析)
echo.
set /p choice=请输入选择 (1或2): 

if "%choice%"=="1" (
    set APP_FILE=crypto_predictor_app.py
    set APP_NAME=KronosCryptoPredictor
    set APP_DESC=完整版
) else if "%choice%"=="2" (
    set APP_FILE=crypto_predictor_lite.py
    set APP_NAME=KronosCryptoPredictorLite
    set APP_DESC=轻量版
) else (
    echo 无效选择，默认使用轻量版
    set APP_FILE=crypto_predictor_lite.py
    set APP_NAME=KronosCryptoPredictorLite
    set APP_DESC=轻量版
)

echo.
echo 正在打包 %APP_DESC% (%APP_FILE%)...
echo 这可能需要几分钟时间，请耐心等待...
echo.

REM 清理旧文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 执行打包
pyinstaller --onefile --windowed --name=%APP_NAME% --icon=NONE ^
    --add-data "models;models" ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=requests ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --exclude-module=test ^
    --exclude-module=tests ^
    --exclude-module=pytest ^
    --exclude-module=jupyter ^
    %APP_FILE%

REM 检查结果
if exist "dist\%APP_NAME%.exe" (
    echo.
    echo ================================================
    echo    🎉 打包成功！
    echo ================================================
    echo.
    echo 可执行文件: dist\%APP_NAME%.exe
    
    REM 获取文件大小
    for %%I in ("dist\%APP_NAME%.exe") do set SIZE=%%~zI
    set /a SIZE_MB=%SIZE%/1024/1024
    echo File size: %SIZE_MB% MB
    echo.
    echo Instructions:
    echo 1. Double click dist\%APP_NAME%.exe to run
    echo 2. Select crypto currencies to predict
    echo 3. Set prediction days
    echo 4. Click Start Prediction button
    echo 5. View results and charts
    echo.
    echo Notes:
    echo - First run may take a few seconds
    echo - Network connection required
    echo - Results are for reference only
    echo.
    
    REM 询问是否立即运行
    set /p run_now=是否立即运行程序测试? (y/n): 
    if /i "%run_now%"=="y" (
        echo 正在启动程序...
        start "" "dist\%APP_NAME%.exe"
    )
    
) else (
    echo.
    echo ================================================
    echo    ❌ 打包失败
    echo ================================================
    echo.
    echo Please check error messages above
    echo Common issues:
    echo 1. Ensure all dependencies are installed
    echo 2. Check Python version compatibility  
    echo 3. Ensure sufficient disk space
)

echo.
pause