@echo off
echo ========================================
echo    Kronos 项目启动脚本
echo ========================================
echo.

echo 1. 激活Python 3.10虚拟环境...
call venv_py310\Scripts\activate.bat

echo 2. 设置环境变量...
set SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYQLIB=0.9.8
set PYTHONPATH=D:\code\Kronos

echo 3. 检查Python版本...
python --version

echo.
echo 4. 环境设置完成！
echo.
echo 可用的命令：
echo   - python examples/prediction_example.py     (运行预测示例)
echo   - python webui/app.py                      (启动Web界面)
echo   - python finetune/qlib_data_preprocess.py  (数据预处理)
echo.
echo 按任意键继续...
pause >nul

cmd /k