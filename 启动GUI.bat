@echo off
echo Adobe GenP Downloads 桌面应用程序启动器
echo ==========================================
echo.

:: 检查gui目录是否存在
if not exist "gui\" (
    echo 错误：未找到gui目录
    pause
    exit /b 1
)

:: 检查app-gui.py是否存在
if not exist "gui\app-gui.py" (
    echo 错误：未找到gui\app-gui.py文件
    pause
    exit /b 1
)

:: 调用gui目录中的启动脚本
echo 正在调用GUI程序...
cd /d "%~dp0gui"
call run_gui.bat

:: 返回原目录
cd /d "%~dp0" 