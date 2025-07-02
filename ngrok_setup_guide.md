# ngrok内网穿透配置指南

> **专为您的网络环境设计**: 公司WiFi + VPN (新加坡节点)  
> **解决问题**: 让云端服务访问本地RAG服务  
> **当前网络**: 172.16.228.45 (公司内网) → VPN → 1.203.80.194 (新加坡)  

---

## 🚨 **为什么需要内网穿透？**

### 您的网络环境限制
```
本地设备 (172.16.228.45)
    ↓
公司WiFi路由器 (无法配置端口转发)
    ↓  
公司防火墙 (禁止入站连接)
    ↓
VPN隧道 (只处理出站流量)
    ↓
新加坡VPN节点 (1.203.80.194)
    ↓
互联网
```

### ❌ **传统方案不可行原因**
- **公司WiFi**: 无法配置路由器端口转发
- **公司防火墙**: 禁止外部直接访问内网设备
- **VPN限制**: 不支持入站端口映射
- **权限限制**: 无法修改公司网络配置

---

## 🌟 **解决方案：ngrok内网穿透**

### ✅ **ngrok优势**
- 🔓 **突破限制**: 无需配置路由器或防火墙
- 🔐 **安全可靠**: HTTPS加密隧道
- 🌍 **全球可访问**: 提供公网域名
- 💰 **免费使用**: 基础功能完全免费
- ⚡ **即时生效**: 几秒钟建立连接

### 🏗️ **工作原理**
```
云端服务
    ↓ HTTPS请求
ngrok公网域名 (https://abc123.ngrok.io)
    ↓ 隧道转发
ngrok客户端 (您的电脑)
    ↓ 本地转发
本地RAG服务 (127.0.0.1:8001)
```

---

## 🚀 **快速配置步骤**

### 第1步：安装ngrok
```bash
# 方法1: 官网下载 (推荐)
# 1. 访问 https://ngrok.com/download
# 2. 注册免费账户  
# 3. 下载macOS版本
# 4. 解压并安装:
sudo mv ngrok /usr/local/bin/

# 方法2: Homebrew
brew install ngrok/ngrok/ngrok

# 验证安装
ngrok version
```

### 第2步：注册和认证
```bash
# 1. 注册账户: https://dashboard.ngrok.com/signup
# 2. 获取认证令牌: https://dashboard.ngrok.com/get-started/your-authtoken
# 3. 配置认证:
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### 第3步：启动本地RAG服务
```bash
# 确保本地RAG服务运行
python3 start_local_rag_service.py start

# 验证服务状态
curl http://127.0.0.1:8001/health
```

### 第4步：建立ngrok隧道
```bash
# 启动隧道 (在新终端窗口)
ngrok http 8001

# 您将看到类似输出:
# Session Status    online
# Account           your@email.com (Plan: Free)
# Version           3.1.0
# Region            United States (us)
# Latency           45ms
# Web Interface     http://127.0.0.1:4040
# Forwarding        https://abc123.ngrok.io -> http://localhost:8001
```

### 第5步：获取公网地址
```bash
# 从ngrok输出中复制HTTPS地址，例如:
# https://abc123.ngrok.io

# 测试公网访问:
curl https://abc123.ngrok.io/health
```
