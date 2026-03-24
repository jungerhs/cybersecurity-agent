@echo off
echo ========================================
echo 网络安全知识问答助手 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查Python依赖...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo [2/3] 检查Node.js依赖...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo [3/3] 启动服务...
echo.
echo 正在启动Flask后端服务 (端口 5000)...
start "Flask Backend" cmd /k "python app.py"

echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo 正在启动React前端服务 (端口 5173)...
start "React Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 后端API: http://localhost:5000
echo 前端界面: http://localhost:5173
echo.
echo 按任意键关闭此窗口...
pause >nul