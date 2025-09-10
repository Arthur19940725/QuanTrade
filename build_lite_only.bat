@echo off
echo.
echo Building Lite Version Only...
echo This will create a smaller, faster exe file
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python first.
    pause
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building KronosCryptoPredictorLite.exe...
echo Please wait, this may take several minutes...
echo.

pyinstaller --onefile --windowed --name=KronosCryptoPredictorLite ^
    --hidden-import=matplotlib.backends.backend_tkagg ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=requests ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --exclude-module=torch ^
    --exclude-module=transformers ^
    --exclude-module=huggingface_hub ^
    --exclude-module=test ^
    --exclude-module=tests ^
    crypto_predictor_lite.py

if exist "dist\KronosCryptoPredictorLite.exe" (
    echo.
    echo SUCCESS!
    echo File: dist\KronosCryptoPredictorLite.exe
    echo.
    echo The lite version is ready to use!
    echo Double-click the exe file to start.
    echo.
    set /p test=Test now? (y/n): 
    if /i "%test%"=="y" (
        start "" "dist\KronosCryptoPredictorLite.exe"
    )
) else (
    echo.
    echo Build failed. Check errors above.
)

pause