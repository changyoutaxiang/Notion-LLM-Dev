#!/bin/bash

# LLM上下文调试工具启动脚本

echo "🛠️  启动LLM上下文调试工具..."
echo "用于检查背景文件是否正确加载到LLM上下文中"
echo

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装或不在PATH中"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "❌ 配置文件 config.json 未找到"
    echo "请确保在项目根目录下运行此脚本"
    exit 1
fi

# 检查依赖文件
if [ ! -f "notion_handler.py" ] || [ ! -f "template_manager.py" ]; then
    echo "❌ 缺少必要的依赖文件"
    echo "请确保在项目根目录下运行此脚本"
    exit 1
fi

# 运行调试工具
python3 debug_context.py

echo
echo "调试工具已退出" 