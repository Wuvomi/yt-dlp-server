@echo off
setlocal

:: 检查 Python 版本
python --version 2>&1 | findstr /R "Python 3\.[6-9]" >nul
if errorlevel 1 (
    echo 请安装 Python 3.6 及以上版本。
    goto end
)

:: 安装依赖库
echo 正在安装依赖库...
python -m pip install --upgrade pip

:: 添加需要安装的依赖库
python -m pip install Flask Flask-SocketIO eventlet requests yt-dlp

:end
endlocal
