@echo off
chcp 65001 >nul
echo ===============================================
echo            WGARP Web 版本启动器
echo        世界观生成与角色扮演程序
echo ===============================================
echo.

echo 正在启动后端服务器...
start "WGARP Backend" cmd /k "%~dp0start-backend.bat"

echo 等待后端启动...
timeout /t 5 /nobreak >nul

echo 正在启动前端应用...
start "WGARP Frontend" cmd /k "%~dp0start-frontend.bat"

echo.
echo ===============================================
echo 启动完成！
echo.
echo 后端服务器: http://localhost:8000
echo 前端应用:   http://localhost:3000
echo API 文档:   http://localhost:8000/docs
echo.
echo 请等待服务完全启动后访问前端应用
echo ===============================================
echo.
pause
