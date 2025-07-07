@echo off
chcp 65001 > nul
echo ====================================
echo    WGARP 重构版快速启动器
echo ====================================
echo.

echo 选择启动模式:
echo 1. 终端模式 (传统界面)
echo 2. Web模式 (浏览器界面)
echo 3. 服务模式 (仅API服务)
echo 4. 环境检查
echo 5. 退出
echo.

set /p choice="请选择 (1-5): "

if "%choice%"=="1" (
    echo 正在启动终端模式...
    python launcher.py terminal
) else if "%choice%"=="2" (
    echo 正在启动Web模式...
    echo 浏览器将自动打开 http://localhost:8000
    start "" http://localhost:8000
    python launcher.py web
) else if "%choice%"=="3" (
    echo 正在启动服务模式...
    python launcher.py service
) else if "%choice%"=="4" (
    echo 正在检查环境...
    python launcher.py --check
    pause
) else if "%choice%"=="5" (
    echo 再见!
    exit /b 0
) else (
    echo 无效选择，请重新运行脚本
    pause
    exit /b 1
)

pause
