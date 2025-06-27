#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "==============================================="
echo "          🤖 Notion-LLM 异步通信助手"
echo "==============================================="
echo -e "${NC}"

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到Python！${NC}"
    echo "   请先安装Python 3.7+"
    echo "   macOS: brew install python3"
    echo "   Ubuntu: sudo apt update && sudo apt install python3"
    read -p "按回车键退出..." 
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo -e "${GREEN}✅ Python已安装${NC}"
echo

# 检查依赖包
echo -e "${YELLOW}🔍 检查依赖包...${NC}"
if ! $PYTHON_CMD -c "import requests" &> /dev/null; then
    echo -e "${YELLOW}❌ 缺少依赖包，正在安装...${NC}"
    $PIP_CMD install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 依赖包安装失败！${NC}"
        read -p "按回车键退出..."
        exit 1
    fi
    echo -e "${GREEN}✅ 依赖包安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖包已安装${NC}"
fi

echo

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo -e "${YELLOW}❌ 警告：配置文件config.json不存在！${NC}"
    echo "   程序将创建默认配置文件，请记得配置API密钥"
    echo
fi

echo -e "${BLUE}🚀 正在启动程序...${NC}"
echo
echo -e "${YELLOW}💡 提示：按Ctrl+C停止程序${NC}"
echo

# 启动程序
$PYTHON_CMD 启动器.py

if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}❌ 程序启动失败！${NC}"
    echo "   请检查错误信息并重试"
else
    echo
    echo -e "${GREEN}✅ 程序已正常退出${NC}"
fi

echo
read -p "按回车键关闭..." 