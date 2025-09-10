@echo off
echo 启动Python 3.10环境...
echo 设置环境变量...

set SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYQLIB=0.9.8

echo 激活虚拟环境...
call venv_py310\Scripts\activate.bat

echo 环境变量已设置，虚拟环境已激活
echo Python版本:
python --version
echo.
echo 现在可以运行项目脚本了
echo 例如: python finetune/qlib_data_preprocess.py
echo.
cmd /k 