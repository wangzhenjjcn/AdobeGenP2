@echo off
echo Adobe GenP Downloads 桌面应用程序
echo ====================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

:: 检查依赖是否安装
python -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install pywebview
    if errorlevel 1 (
        echo 错误：依赖安装失败
        pause
        exit /b 1
    )
)

:: 启动应用程序
echo 正在启动应用程序...
python "%~dp0app-gui.py"

if errorlevel 1 (
    echo.
    echo 程序运行出错
    pause
) 