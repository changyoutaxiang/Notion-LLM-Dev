#!/bin/bash

# RAG服务状态检查脚本
# 双击运行即可快速检查服务状态

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "=========================================="
echo "       🔍 RAG服务状态检查器"
echo "=========================================="
echo -e "${NC}"

# 检查服务状态
echo -e "${YELLOW}正在检查RAG服务状态...${NC}"
echo

# 执行状态检查
python3 start_local_rag_service.py status

echo
echo -e "${BLUE}💡 其他验证方法：${NC}"
echo "1. 浏览器访问：http://127.0.0.1:8001/health"
echo "2. 查看进程：ps aux | grep 'uvicorn'"
echo "3. 查看端口：lsof -i :8001"

# 快速网络测试
echo
echo -e "${YELLOW}🌐 快速网络测试...${NC}"
if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 网络测试通过 - 服务可访问${NC}"
else
    echo -e "${RED}❌ 网络测试失败 - 服务不可访问${NC}"
fi

echo
echo -e "${BLUE}📋 快速操作：${NC}"
echo "启动服务：bash 启动RAG后台服务.sh"
echo "停止服务：python3 start_local_rag_service.py stop"

# 在macOS上，如果是双击运行，保持窗口打开
if [ "$TERM_PROGRAM" = "Apple_Terminal" ] && [ -z "$SSH_CLIENT" ]; then
    echo
    read -p "按回车键关闭窗口..."
fi 