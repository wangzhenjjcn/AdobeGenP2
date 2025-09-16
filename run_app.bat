@echo off
echo Adobe GenP Downloads 主程序
echo ====================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

:: 安装依赖
echo 正在安装依赖包...
pip install -r src\requirements.txt

:: 运行主程序
echo 正在运行主程序...
cd src
python app.py

if errorlevel 1 (
    echo.
    echo 程序运行出错
    pause
) 