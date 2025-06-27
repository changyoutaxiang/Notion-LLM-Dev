@echo off
title Notion-LLM 异步通信助手
color 0A

echo.
echo ===============================================
echo          🤖 Notion-LLM 异步通信助手
echo ===============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python！
    echo    请先安装Python 3.7+
    echo    下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装
echo.

REM 检查依赖包
echo 🔍 检查依赖包...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ❌ 缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败！
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ✅ 依赖包已安装
)

echo.

REM 检查配置文件
if not exist "config.json" (
    echo ❌ 警告：配置文件config.json不存在！
    echo    程序将创建默认配置文件，请记得配置API密钥
    echo.
)

echo 🚀 正在启动程序...
echo.
echo 💡 提示：关闭此窗口将停止程序

REM 启动程序
python 启动器.py

if errorlevel 1 (
    echo.
    echo ❌ 程序启动失败！
    echo    请检查错误信息并重试
) else (
    echo.
    echo ✅ 程序已正常退出
)

echo.
echo 按任意键关闭窗口...
pause >nul 