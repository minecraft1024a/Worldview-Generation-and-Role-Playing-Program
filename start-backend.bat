@echo off
chcp 65001 >nul
echo 启动 WGARP 后端服务器...
echo.

cd /d "%~dp0backend"

echo 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请确保已安装 Python 3.8+
    pause
    exit /b 1
)

echo 检查虚拟环境...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate

echo 安装依赖...
pip install -r requirements.txt

echo.
echo 启动后端服务器...
echo 服务器地址: http://localhost:8000
echo API 文档地址: http://localhost:8000/docs
echo.

python main.py
