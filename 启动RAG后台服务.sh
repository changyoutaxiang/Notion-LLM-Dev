#!/bin/bash

# RAG后台服务一键启动脚本
# 双击运行或在终端执行：bash 启动RAG后台服务.sh

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
echo "      🤖 RAG后台服务一键启动器"
echo "=========================================="
echo -e "${NC}"

# 启动RAG后台服务
echo -e "${YELLOW}🚀 正在启动RAG后台服务...${NC}"
python3 start_local_rag_service.py start

# 检查启动结果
if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}✅ RAG后台服务启动成功！${NC}"
    echo
    echo -e "${BLUE}💡 重要提示：${NC}"
    echo "  ✓ RAG服务已在后台运行，无需保持此窗口打开"
    echo "  ✓ 电脑重启后需要重新启动此服务"
    echo "  ✓ 服务地址：http://127.0.0.1:8001"
    echo
    echo -e "${BLUE}📋 管理命令：${NC}"
    echo "  查看状态：python3 start_local_rag_service.py status"
    echo "  停止服务：python3 start_local_rag_service.py stop"
    echo "  重启服务：python3 start_local_rag_service.py restart"
    echo
    echo -e "${GREEN}🎉 你现在可以关闭这个窗口了！${NC}"
else
    echo
    echo -e "${RED}❌ RAG服务启动失败${NC}"
    echo "请检查错误信息并重试"
fi

# 在macOS上，如果是双击运行，保持窗口打开
if [ "$TERM_PROGRAM" = "Apple_Terminal" ] && [ -z "$SSH_CLIENT" ]; then
    echo
    read -p "按回车键关闭窗口..."
fi 