@echo off
chcp 65001 >nul
echo 🌐 启动Kronos Web界面...

cd webui
echo 正在启动Web界面...
python app.py

pause 