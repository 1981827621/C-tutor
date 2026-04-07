@echo off
echo ========================================
echo   C++竞赛助教Bot - 安装依赖
echo ========================================
echo.

echo [1/3] 正在安装Python依赖...
pip install -r requirements.txt

echo.
echo [2/3] 创建必要的目录...
if not exist "chroma_db" mkdir chroma_db
if not exist "temp_uploads" mkdir temp_uploads
if not exist "uploads" mkdir uploads

echo.
echo [3/3] 初始化环境变量配置...
if not exist ".env" (
    copy .env.example .env
    echo [提示] 已创建.env文件，请编辑并填入你的DeepSeek API密钥
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 编辑 .env 文件，填入 DeepSeek API 密钥
echo 2. 运行 start_backend.bat 启动后端服务
echo 3. 运行 start_frontend.bat 启动前端界面
echo.
pause
