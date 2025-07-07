@echo off
chcp 65001 >nul
echo 启动 WGARP 前端应用...
echo.

cd /d "%~dp0frontend"

echo 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Node.js，请确保已安装 Node.js 16+
    pause
    exit /b 1
)

echo 检查 npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 npm
    pause
    exit /b 1
)

echo 安装依赖...
if not exist "node_modules" (
    npm install
) else (
    echo 依赖已安装，跳过...
)

echo.
echo 启动前端开发服务器...
echo 应用地址: http://localhost:3000
echo.

npm start
