@echo off
echo ================================================
echo   Kronos Enhanced Crypto Predictor Builder
echo ================================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed
    pause
    exit /b 1
)

echo Python environment: OK
echo.

REM Install dependencies if needed
echo Checking dependencies...
python -c "import tkinter, matplotlib, pandas, numpy, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install matplotlib pandas numpy requests
)

REM Install PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo Dependencies: OK
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Choose version to build:
echo.
echo [1] Enhanced Lite Version (Recommended)
echo     - DOGE and WLFI support
echo     - Historical + Prediction charts  
echo     - High/Low curves
echo     - Chinese font support
echo.
echo [2] Enhanced Full Version
echo     - All lite features
echo     - Kronos AI model
echo     - Larger file size
echo.
set /p choice=Enter choice (1 or 2): 

if "%choice%"=="1" (
    set APP_FILE=crypto_predictor_lite.py
    set APP_NAME=KronosEnhancedLite
    set APP_DESC=Enhanced Lite Version
    echo.
    echo Building Enhanced Lite Version...
) else if "%choice%"=="2" (
    set APP_FILE=crypto_predictor_app.py  
    set APP_NAME=KronosEnhancedFull
    set APP_DESC=Enhanced Full Version
    echo.
    echo Building Enhanced Full Version...
) else (
    echo Invalid choice, using Enhanced Lite Version
    set APP_FILE=crypto_predictor_lite.py
    set APP_NAME=KronosEnhancedLite
    set APP_DESC=Enhanced Lite Version
)

echo.
echo Building %APP_DESC%...
echo This may take several minutes...
echo.

REM Build with PyInstaller
pyinstaller --onefile --windowed --name=%APP_NAME% ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=requests ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --collect-data matplotlib ^
    --exclude-module=test ^
    --exclude-module=tests ^
    --exclude-module=pytest ^
    --exclude-module=jupyter ^
    --exclude-module=notebook ^
    %APP_FILE%

REM Check result
if exist "dist\%APP_NAME%.exe" (
    echo.
    echo ================================================
    echo   SUCCESS: Build Complete!
    echo ================================================
    echo.
    echo Executable: dist\%APP_NAME%.exe
    
    REM Get file size
    for %%I in ("dist\%APP_NAME%.exe") do set SIZE=%%~zI
    set /a SIZE_MB=%SIZE%/1024/1024
    echo File size: %SIZE_MB% MB
    echo.
    echo New Features:
    echo - DOGE and WLFI token support
    echo - Historical + Prediction price charts
    echo - High/Low price curves  
    echo - Improved Chinese font support
    echo - Enhanced visual interface
    echo.
    echo Ready to use! Double-click the exe to start.
    echo.
    
    set /p test=Test the application now? (y/n): 
    if /i "%test%"=="y" (
        echo Starting application...
        start "" "dist\%APP_NAME%.exe"
    )
    
) else (
    echo.
    echo ================================================  
    echo   ERROR: Build Failed
    echo ================================================
    echo.
    echo Please check the error messages above
    echo.
    echo Common solutions:
    echo 1. Ensure all dependencies are installed
    echo 2. Check available disk space
    echo 3. Try building the lite version instead
)

echo.
pause