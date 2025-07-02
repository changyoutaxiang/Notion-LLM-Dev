#!/bin/bash
# ngrok隧道启动脚本 - 专为公司WiFi+VPN环境设计

echo "🌐 ngrok内网穿透启动脚本"
echo "适用环境: 公司WiFi + VPN"
echo "================================"

# 检查ngrok是否安装
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok未安装"
    echo "请访问 https://ngrok.com/download 下载安装"
    echo "或使用: brew install ngrok/ngrok/ngrok"
    exit 1
fi

echo "✅ ngrok已安装: $(ngrok version | head -1)"

# 检查本地RAG服务
echo ""
echo "🔍 检查本地RAG服务..."
if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo "✅ 本地RAG服务运行正常"
    RAG_STATUS=$(curl -s http://127.0.0.1:8001/health | jq -r '.status' 2>/dev/null || echo "running")
    echo "   状态: $RAG_STATUS"
else
    echo "❌ 本地RAG服务未运行"
    echo "🚀 正在启动RAG服务..."
    python3 start_local_rag_service.py start
    echo "⏳ 等待服务启动..."
    sleep 15
    
    if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
        echo "✅ RAG服务启动成功"
    else
        echo "❌ RAG服务启动失败，请检查配置"
        exit 1
    fi
fi

echo ""
echo "🚀 启动ngrok隧道..."
echo "⚠️  重要提醒:"
echo "   - 请保持此终端窗口打开"
echo "   - 复制HTTPS地址用于云端配置"
echo "   - 隧道断开后需要重新运行此脚本"
echo ""
echo "📋 启动中..."
sleep 2

# 启动ngrok隧道
ngrok http 8001
