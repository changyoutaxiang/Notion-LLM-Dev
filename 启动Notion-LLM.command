#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "🤖 Notion-LLM 异步通信助手"
echo "=========================="

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 未找到Python，请先安装Python 3.7+"
    read -p "按回车键退出..."
    exit 1
fi

echo "✅ 使用 $PYTHON_CMD"

# 检查依赖
if ! $PYTHON_CMD -c "import requests" &> /dev/null; then
    echo "🔧 正在安装依赖包..."
    $PYTHON_CMD -m pip install requests
fi

echo "🚀 启动程序..."
echo ""

# 启动程序
$PYTHON_CMD main.py

echo ""
echo "程序已退出"
read -p "按回车键关闭..." 