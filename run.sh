#!/bin/bash

# 云端服务启动脚本
# 适用于所有云平台部署

echo "🌐 启动 Notion-LLM 云端服务..."

# 设置云端环境标识
export CLOUD_DEPLOYMENT=true

# 检查必需的环境变量
required_vars=("NOTION_API_KEY" "NOTION_DATABASE_ID" "OPENROUTER_API_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 缺少必需的环境变量: $var"
        exit 1
    fi
done

echo "✅ 环境变量检查通过"

# 尝试启动服务
if [ -f "startserver.py" ]; then
    echo "🚀 使用 startserver.py 启动服务..."
    python startserver.py
elif [ -f "cloud_main.py" ]; then
    echo "🚀 使用 cloud_main.py 启动服务..."
    python cloud_main.py
elif [ -f "app.py" ]; then
    echo "🚀 使用 app.py 启动服务..."
    python app.py
else
    echo "❌ 找不到启动文件"
    exit 1
fi 