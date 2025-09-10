@echo off
echo Building Kronos Crypto Predictor...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Install PyInstaller if needed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean old builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Choose version to build:
echo 1. Full version (with Kronos model)
echo 2. Lite version (technical analysis)
echo.
set /p choice=Enter choice (1 or 2): 

if "%choice%"=="1" (
    set APP_FILE=crypto_predictor_app.py
    set APP_NAME=KronosCryptoPredictor
) else (
    set APP_FILE=crypto_predictor_lite.py
    set APP_NAME=KronosCryptoPredictorLite
)

echo.
echo Building %APP_NAME%...
echo Please wait...

pyinstaller --onefile --windowed --name=%APP_NAME% ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=PIL._tkinter_finder ^
    --exclude-module=test ^
    --exclude-module=tests ^
    --exclude-module=pytest ^
    %APP_FILE%

if exist "dist\%APP_NAME%.exe" (
    echo.
    echo SUCCESS: Built dist\%APP_NAME%.exe
    echo.
    set /p run_test=Run test now? (y/n): 
    if /i "%run_test%"=="y" (
        echo Starting application...
        start "" "dist\%APP_NAME%.exe"
    )
) else (
    echo.
    echo ERROR: Build failed
    echo Check error messages above
)

echo.
pause