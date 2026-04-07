@echo off
echo ========================================
echo   C++竞赛助教Bot - 启动后端服务
echo ========================================
echo.

REM 检查.env文件
if not exist ".env" (
    echo [警告] .env文件不存在
    echo [提示] 请复制.env.example为.env并配置API密钥
    echo.
    pause
    exit /b 1
)

echo [1/2] 正在启动FastAPI后端服务...
echo [提示] 后端服务将在 http://localhost:8000 运行
echo [提示] API文档: http://localhost:8000/docs
echo.

REM 启动FastAPI
uvicorn cpp_tutor_bot.api.main:app --host 0.0.0.0 --port 8000 --reload

pause
