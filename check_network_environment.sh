#!/bin/bash
# 网络环境检测脚本

echo "🌐 网络环境检测报告"
echo "时间: $(date)"
echo "================================"

# 检查本地IP
echo ""
echo "📍 本地网络信息:"
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)
echo "   内网IP: $LOCAL_IP"

# 检查公网IP
echo ""
echo "🌍 公网信息:"
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null)
if [ -n "$PUBLIC_IP" ]; then
    echo "   公网IP: $PUBLIC_IP"
    
    # 检查IP归属地
    LOCATION=$(curl -s "ipinfo.io/$PUBLIC_IP/city" 2>/dev/null)
    COUNTRY=$(curl -s "ipinfo.io/$PUBLIC_IP/country" 2>/dev/null)
    if [ -n "$LOCATION" ] && [ -n "$COUNTRY" ]; then
        echo "   IP归属: $LOCATION, $COUNTRY"
    fi
else
    echo "   ❌ 无法获取公网IP"
fi

# 检查VPN状态
echo ""
echo "🔒 VPN状态分析:"
if [ "$LOCAL_IP" != "$PUBLIC_IP" ]; then
    echo "   ✅ 检测到VPN连接"
    echo "   本地IP与公网IP不同，可能使用VPN"
else
    echo "   ❓ 未明确检测到VPN"
fi

# 检查网络类型
echo ""
echo "�� 网络环境判断:"
if [[ $LOCAL_IP == 10.* ]] || [[ $LOCAL_IP == 172.16.* ]] || [[ $LOCAL_IP == 192.168.* ]]; then
    echo "   📶 内网环境 (NAT网络)"
    echo "   需要内网穿透或端口转发才能公网访问"
    
    if [[ $LOCAL_IP == 172.16.* ]]; then
        echo "   🏢 疑似公司网络 (172.16.x.x网段)"
        echo "   通常无法配置路由器端口转发"
    fi
else
    echo "   🌐 公网环境"
    echo "   可能支持直接端口映射"
fi

# 检查端口占用
echo ""
echo "🔌 本地服务检查:"
if lsof -i :8001 > /dev/null 2>&1; then
    echo "   ✅ 端口8001已被占用 (RAG服务可能在运行)"
    PROCESS=$(lsof -i :8001 | tail -1 | awk '{print $1}')
    echo "   进程: $PROCESS"
else
    echo "   ❌ 端口8001空闲 (RAG服务未运行)"
fi

# 测试网络连通性
echo ""
echo "🌐 网络连通性测试:"
if ping -c 1 ngrok.com > /dev/null 2>&1; then
    echo "   ✅ ngrok.com 可访问"
else
    echo "   ❌ ngrok.com 不可访问"
fi

if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo "   ✅ DNS解析正常"
else
    echo "   ❌ DNS解析异常"
fi

# 建议方案
echo ""
echo "💡 配置建议:"
echo "================================"

if [[ $LOCAL_IP == 172.16.* ]]; then
    echo "🎯 推荐方案: ngrok内网穿透"
    echo "   原因:"
    echo "   - 您使用公司WiFi (172.16.x.x网段)"
    echo "   - 无法配置路由器端口转发"
    echo "   - VPN环境不支持入站连接"
    echo ""
    echo "📋 操作步骤:"
    echo "   1. 安装ngrok: brew install ngrok/ngrok/ngrok"
    echo "   2. 注册账户: https://ngrok.com/signup"
    echo "   3. 配置认证: ngrok config add-authtoken YOUR_TOKEN"
    echo "   4. 启动隧道: ./start_ngrok_tunnel.sh"
else
    echo "🎯 可考虑方案: 端口转发或内网穿透"
    echo "   - 如果可以配置路由器，尝试端口转发"
    echo "   - 否则使用ngrok内网穿透"
fi

echo ""
echo "⚠️  注意事项:"
echo "   - ngrok免费版每次重启会更换域名"
echo "   - 建议在stable环境中考虑付费版"
echo "   - 保持ngrok进程持续运行"
