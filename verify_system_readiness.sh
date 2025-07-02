#!/bin/bash
echo "🔍 系统就绪状态检查"
echo "=========================="

# 1. 检查本地RAG服务
echo ""
echo "📍 本地RAG服务状态:"
if curl -s http://127.0.0.1:8001/health >/dev/null 2>&1; then
    echo "✅ RAG服务正常运行"
    RAG_RESPONSE=$(curl -s http://127.0.0.1:8001/health)
    echo "   响应: $RAG_RESPONSE"
else
    echo "❌ RAG服务未运行"
    echo "🚀 正在启动RAG服务..."
    python3 start_local_rag_service.py start
    sleep 10
    if curl -s http://127.0.0.1:8001/health >/dev/null 2>&1; then
        echo "✅ RAG服务启动成功"
    else
        echo "❌ RAG服务启动失败"
    fi
fi

# 2. 检查云端部署准备
echo ""
echo "🌐 云端部署准备检查:"
if [ -d "zeabur_hybrid_deploy" ]; then
    echo "✅ 云端部署目录存在"
    if [ -f "zeabur_hybrid_deploy/app.py" ]; then
        echo "✅ Zeabur入口文件准备就绪"
    fi
    if [ -f "zeabur_hybrid_deploy/requirements.txt" ]; then
        echo "✅ 依赖配置文件准备就绪"
    fi
else
    echo "❌ 云端部署目录缺失"
fi

# 3. 检查测试脚本
echo ""
echo "🧪 测试脚本状态:"
if [ -f "test_hybrid_cloud_service.py" ]; then
    echo "✅ 云端服务测试脚本存在"
    echo "🔄 运行测试..."
    python3 test_hybrid_cloud_service.py | head -20
else
    echo "❌ 测试脚本缺失"
fi

echo ""
echo "💡 下一步建议:"
echo "=========================="
if curl -s http://127.0.0.1:8001/health >/dev/null 2>&1; then
    echo "1. ✅ 本地RAG服务已就绪"
    echo "2. 🔧 需要解决ngrok安装问题"
    echo "3. 🌐 然后可以进行云端部署"
    echo ""
    echo "📋 ngrok安装选项:"
    echo "   - 官网下载: https://ngrok.com/download"
    echo "   - 查看详细指南: cat install_ngrok_manual.md"
else
    echo "1. ❌ 需要先启动本地RAG服务"
    echo "2. 🔧 然后解决ngrok安装问题"
fi
