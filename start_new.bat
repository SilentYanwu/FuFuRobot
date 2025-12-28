@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM =======================================================
echo.
echo =======================================================
echo 启动脚本：全栈应用启动器
echo =======================================================

set "BASE_DIR=%~dp0"

echo.
echo [1/5] 检查环境...
python --version >nul 2>&1 || (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

node --version >nul 2>&1 || (
    echo ❌ 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

echo ✅ 环境检查通过

echo.
echo [2/5] 激活虚拟环境...
if exist "%BASE_DIR%.venv\Scripts\activate.bat" (
    call "%BASE_DIR%.venv\Scripts\activate.bat"
    echo ✅ 虚拟环境激活成功
    
    REM 检查Python依赖
    echo 📦 检查Python依赖...
    python -c "import fastapi, uvicorn" 2>nul
    if ERRORLEVEL 1 (
        echo ⚠️ 正在安装Python依赖...
        pip install fastapi uvicorn python-dotenv pandas aiofiles --quiet
        echo ✅ Python依赖安装完成
    )
) else (
    echo ⚠️ 使用系统Python
    echo ⚠️ 注意：建议使用虚拟环境 (.venv)
)

echo.
echo [3/5] 清理端口占用...
netstat -ano | findstr ":8000 " >nul && (
    echo ⚠️ 端口8000被占用，尝试清理...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 "') do taskkill /F /PID %%a >nul 2>&1
)

netstat -ano | findstr ":5173 " >nul && (
    echo ⚠️ 端口5173被占用，尝试清理...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173 "') do taskkill /F /PID %%a >nul 2>&1
)

echo.
echo [4/5] 启动后端API服务 (端口 8000)...
REM 在新窗口中激活虚拟环境并启动后端
start "AI学生管理系统 - 后端API" cmd /k "chcp 65001 > nul && title 后端API && echo [后端API] 正在启动... && cd /d "%BASE_DIR%" && (if exist ".venv\Scripts\activate.bat" (call ".venv\Scripts\activate.bat") && python main.py)"

echo ⏳ 等待后端启动 (2秒)...
timeout /t 2 /nobreak > nul

echo.
echo [5/5] 启动Vue前端开发服务器...
echo 📦 正在启动前端...

REM 检查前端目录
if not exist "%BASE_DIR%frontend_vue\package.json" (
    echo ❌ 错误: 未找到Vue前端项目
    echo 请确保Vue项目位于 frontend_vue 目录中
    pause
    exit /b 1
)

REM 关键：在新窗口中启动前端，使用 /k 保持窗口打开
start "Vue前端开发" cmd /c "chcp 65001 > nul && title Vue前端 && cd /d "%BASE_DIR%frontend_vue" && echo [Vue前端] 正在安装依赖... && npm install --silent && echo [Vue前端] 正在格式化代码... && npm run format --silent && echo [Vue前端] 正在启动开发服务器... && echo 🌐 访问地址: http://localhost:5173 && echo 🔥 支持热重载 && echo. && npm run dev --host"

echo ⏳ 等待前端启动 (2秒)...
timeout /t 2 /nobreak > nul

echo.
echo 🌐 正在打开浏览器...
start "" "http://localhost:5173/"

echo.
echo =======================================================
echo ✅ 系统启动完成！
echo =======================================================
echo.
echo 📡 服务信息:
echo    • Vue前端: http://127.0.0.1:5173/
echo    • 后端API: http://127.0.0.1:8000/
echo    • API文档: http://127.0.0.1:8000/docs
echo.
echo 💡 提示:
echo    • 前端调用后端API地址: http://127.0.0.1:8000/api
echo    • 按 Ctrl+C 停止各服务
echo =======================================================
echo.
echo 按任意键退出此窗口...
pause >nul