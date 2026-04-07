@echo off
echo ========================================
echo   C++竞赛助教Bot - 启动前端界面
echo ========================================
echo.

echo [1/2] 正在启动Streamlit前端界面...
echo [提示] 前端界面将在 http://localhost:8501 运行
echo [提示] 请确保后端服务已启动（端口8000）
echo.

REM 启动Streamlit
streamlit run cpp_tutor_bot/frontend/app.py

pause
