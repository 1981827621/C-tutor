@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   Starting C++ Tutor (Chainlit Frontend)
echo ========================================
echo.

REM Change to script directory
cd /d %~dp0

REM Activate virtual environment
if exist "%~dp0.venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Please run install.bat first
    pause
    exit /b 1
)

REM Set environment variable
set API_BASE_URL=http://localhost:8000

echo [INFO] Frontend URL: http://localhost:8080
echo [INFO] Backend URL: http://localhost:8000
echo [INFO] Press Ctrl+C to stop
echo.

REM Start Chainlit in background
start "Chainlit" /B cmd /c "cd cpp_tutor_bot\frontend && chainlit run chainlit_app.py --host 0.0.0.0 --port 8080 --watch"

REM Wait for server to start
echo [INFO] Waiting for Chainlit to start...
timeout /t 3 /nobreak >nul

REM Open browser
echo [INFO] Opening browser...
start http://localhost:8080

pause

