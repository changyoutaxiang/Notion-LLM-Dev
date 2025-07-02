# 本地RAG服务公网访问配置指南

> **目标**: 让云端服务能够访问本地RAG服务  
> **当前状态**: ✅ 本地服务已就绪 (0.0.0.0:8001)  
> **公网IP**: 1.203.80.194  
> **内网IP**: 172.16.228.45  

---

## 🎯 配置总览

### ✅ 已完成
- [x] 本地RAG服务运行正常
- [x] 服务绑定到所有网络接口 (0.0.0.0:8001)
- [x] 健康检查通过，RAG引擎就绪

### 🔧 待配置
- [ ] 路由器端口转发配置
- [ ] 防火墙设置检查
- [ ] 公网访问测试
- [ ] 云端服务配置

---

## 🌐 方案一：固定公网IP访问（推荐⭐⭐⭐⭐⭐）

### 优势
- ✅ 最稳定可靠
- ✅ 性能最佳
- ✅ 配置简单
- ✅ 无需第三方服务

### 配置步骤

#### 1. 路由器端口转发配置
```
访问路由器管理界面 (通常是 192.168.1.1 或 192.168.0.1)
→ 高级设置 / 端口转发 / 虚拟服务器
→ 添加新规则：
   - 服务名称: RAG-Service
   - 外部端口: 8001
   - 内部IP: 172.16.228.45
   - 内部端口: 8001
   - 协议: TCP
   - 状态: 启用
→ 保存设置
```

#### 2. macOS防火墙配置
```bash
# 检查防火墙状态
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 如果防火墙开启，允许8001端口
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3
```

#### 3. 测试外网访问
```bash
# 方法1: 使用手机热点测试
# 断开WiFi，连接手机热点，然后访问：
curl http://1.203.80.194:8001/health

# 方法2: 使用在线测试工具
# 访问: https://www.yougetsignal.com/tools/open-ports/
# 输入: 1.203.80.194:8001
```

#### 4. 云端服务配置
```env
# Zeabur环境变量
LOCAL_RAG_SERVICE_URL=http://1.203.80.194:8001
ENABLE_RAG_FALLBACK=true
RAG_REQUEST_TIMEOUT=10
```

---

## 🌐 方案二：动态域名服务（DDNS）（推荐⭐⭐⭐⭐）

### 优势
- ✅ 适合动态IP
- ✅ 域名访问更稳定
- ✅ 支持HTTPS

### 配置步骤

#### 1. 申请DDNS服务
**选项A: 花生壳（国内推荐）**
```
1. 注册账号: https://console.hsk.oray.com
2. 下载客户端安装
3. 添加域名映射: your-name.gicp.net → 8001端口
4. 获得访问地址: http://your-name.gicp.net:8001
```

**选项B: No-IP（国际）**
```
1. 注册账号: https://www.noip.com
2. 创建域名: your-name.ddns.net
3. 下载DUC客户端
4. 配置域名解析
```

#### 2. 路由器DDNS设置
```
路由器管理界面
→ 高级设置 / 动态DNS
→ 服务提供商: 选择对应服务
→ 域名: 填入申请的域名
→ 用户名/密码: DDNS服务账号
→ 启用DDNS服务
```

#### 3. 云端配置
```env
LOCAL_RAG_SERVICE_URL=http://your-name.gicp.net:8001
```

---

## 🌐 方案三：内网穿透（快速测试⭐⭐⭐）

### 优势
- ✅ 配置最简单
- ✅ 无需路由器配置
- ✅ 支持HTTPS

### 缺点
- ❌ 依赖第三方服务
- ❌ 有流量限制
- ❌ 延迟较高

### ngrok配置
```bash
# 1. 安装ngrok
brew install ngrok

# 2. 注册并获取token
# 访问 https://ngrok.com/signup
# 获取认证token

# 3. 设置token
ngrok authtoken YOUR_TOKEN

# 4. 启动隧道
ngrok http 8001

# 5. 获得公网地址（示例）
# https://abc123.ngrok.io
```

### frp配置（自建推荐）
```bash
# 1. 准备云服务器
# 2. 下载frp: https://github.com/fatedier/frp
# 3. 服务端配置 (frps.ini)
[common]
bind_port = 7000
dashboard_port = 7500

# 4. 客户端配置 (frpc.ini)
[common]
server_addr = YOUR_VPS_IP
server_port = 7000

[rag-service]
type = tcp
local_ip = 127.0.0.1
local_port = 8001
remote_port = 8001

# 5. 启动服务
./frps -c frps.ini  # 服务端
./frpc -c frpc.ini  # 客户端

# 6. 访问地址
# http://YOUR_VPS_IP:8001
```

---

## 🔍 配置验证与测试

### 本地网络测试
```bash
# 1. 本地测试
curl http://127.0.0.1:8001/health
curl http://172.16.228.45:8001/health

# 2. 内网其他设备测试
curl http://172.16.228.45:8001/health
```

### 外网访问测试
```bash
# 使用公网IP测试
curl http://1.203.80.194:8001/health

# 使用域名测试（如果配置了DDNS）
curl http://your-domain.ddns.net:8001/health

# 功能测试
curl -X POST http://1.203.80.194:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "测试查询", "tags": [], "max_results": 3}'
```

### 在线端口检测
```
工具1: https://www.yougetsignal.com/tools/open-ports/
工具2: https://canyouseeme.org/
工具3: https://www.portchecktool.com/

输入: 1.203.80.194:8001
检查端口是否开放
```

---

## ⚠️ 安全注意事项

### 防火墙配置
```bash
# macOS防火墙管理
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3
```

### 访问控制建议
```python
# 在RAG服务中可添加IP白名单（可选）
ALLOWED_IPS = [
    "你的云端服务器IP",
    "127.0.0.1",
    "::1"
]
```

### 网络安全
- 🔐 考虑使用VPN连接
- 🔐 定期更换端口号
- 🔐 监控访问日志
- 🔐 使用HTTPS（推荐）

---

## 🛠️ 故障排除

### 无法访问时检查
```bash
# 1. 本地服务状态
python3 start_local_rag_service.py status
curl http://127.0.0.1:8001/health

# 2. 端口监听状态
netstat -an | grep 8001
lsof -i :8001

# 3. 路由器设置
ping 192.168.1.1  # 确认路由器可访问
# 检查端口转发规则

# 4. 防火墙状态
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 5. 网络连通性
ping 1.203.80.194  # 从外网ping公网IP
```

### 常见问题解决
```
问题1: 端口转发不生效
解决: 重启路由器，检查内网IP是否变化

问题2: 防火墙阻止连接
解决: 添加Python应用到防火墙白名单

问题3: 运营商封锁端口
解决: 更换端口号（如8080、3000等）

问题4: 动态IP变化
解决: 使用DDNS服务自动更新
```

---

## 📋 云端服务配置模板

### Zeabur环境变量
```env
# 基础配置
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
OPENROUTER_API_KEY=your_openrouter_key

# 混合架构配置（关键）
LOCAL_RAG_SERVICE_URL=http://1.203.80.194:8001
ENABLE_RAG_FALLBACK=true
RAG_FALLBACK_MESSAGE=本地知识库暂时不可用，已采用基础模式处理

# 性能调优
RAG_REQUEST_TIMEOUT=10
RAG_MAX_RETRIES=2
RAG_HEALTH_CHECK_INTERVAL=300

# 系统配置
AUTO_START=true
CHECK_INTERVAL=120
LOG_LEVEL=INFO
```

### 测试命令
```bash
# 云端服务测试本地RAG连接
curl -X POST https://your-app.zeabur.app/rag/test \
  -H "Content-Type: application/json" \
  -d '{"test_query": "测试连接"}'
```

---

## 🎯 推荐配置方案

### 🏠 家庭用户（推荐方案一）
```
✅ 固定公网IP + 路由器端口转发
- 配置简单，性能最佳
- 成本低，稳定性高
```

### 🏢 企业用户（推荐方案二）
```
✅ DDNS + 企业域名
- 专业性强，易于管理
- 支持HTTPS，安全性高
```

### 🧪 测试环境（推荐方案三）
```
✅ ngrok内网穿透
- 快速部署，即开即用
- 适合开发测试阶段
```

---

## 📞 获取帮助

### 验证配置成功
```bash
# 运行完整测试
python3 test_hybrid_cloud_service.py

# 检查所有连接
curl http://127.0.0.1:8001/health           # 本地
curl http://172.16.228.45:8001/health       # 内网
curl http://1.203.80.194:8001/health        # 公网
```

### 下一步
配置完成后，请继续：
1. 🚀 Zeabur云端部署
2. 🔗 端到端功能测试
3. 📊 性能监控配置

---

**🎉 配置完成后，您将拥有一个完整的混合架构AI系统！** 

## 🎉 配置完成状态

### ✅ **已完成项目**
- [x] **ngrok安装**: 版本 3.23.3 ✅ 正常运行
- [x] **认证令牌**: 已配置到 `/Users/wangdong/Library/Application Support/ngrok/ngrok.yml`
- [x] **隧道启动**: 8001端口 → 公网HTTPS地址
- [x] **公网测试**: 健康检查响应正常
- [x] **本地RAG**: 服务版本1.0.0，RAG引擎就绪

### 📊 **实际配置信息**
```bash
# 本地RAG服务
本地地址: http://127.0.0.1:8001
服务状态: {"status":"healthy","service":"Local RAG Service","version":"1.0.0","rag_engine_ready":true}

# ngrok隧道
公网地址: https://cf26-1-203-80-194.ngrok-free.app  
隧道状态: ✅ 活跃
认证状态: ✅ 已验证

# 公网访问测试
curl https://cf26-1-203-80-194.ngrok-free.app/health
响应: {"status":"healthy","service":"Local RAG Service","version":"1.0.0","rag_engine_ready":true}
```

## 🔧 配置完成过程回顾

### **第1阶段：ngrok安装** ✅
```bash
# 下载和解压
unzip ngrok-v3-stable-darwin-arm64.zip

# 清除隔离标记
xattr -cr ./ngrok

# 验证安装
./ngrok version  # 输出: ngrok version 3.23.3
```

### **第2阶段：认证配置** ✅  
```bash
# 配置认证令牌
./ngrok config add-authtoken 2zJsdMchT5Isz0o3HDH671CDjsc_3XBQn1CmmAG8CGpKrpsHb

# 验证配置
./ngrok config check  # 输出: Valid configuration file
```

### **第3阶段：隧道启动** ✅
```bash
# 启动隧道 (后台运行)
./ngrok http 8001 --log=stdout &

# 获取公网地址
curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['tunnels'][0]['public_url'])"
# 输出: https://cf26-1-203-80-194.ngrok-free.app
```

## 🌐 网络架构图

```
┌─────────────────┐    ngrok隧道    ┌──────────────────┐
│   Zeabur云端    │ ←────────────→ │    用户本地      │
│                 │                │                  │
│ 混合架构调度器  │   HTTPS安全   │ 本地RAG服务      │
│ cloud_hybrid    │   加密传输     │ 127.0.0.1:8001  │  
│ _main.py        │                │ (0.0.0.0监听)   │
└─────────────────┘                └──────────────────┘
         │                                   │
         ↓                                   ↓
  公网访问地址:                          本地访问地址:
  https://cf26-1-203-80-194.             http://127.0.0.1:8001
  ngrok-free.app
```

## 📋 Zeabur部署环境变量

```env
# 🎯 关键配置 - 直接使用
LOCAL_RAG_SERVICE_URL=https://cf26-1-203-80-194.ngrok-free.app

# 其他必需配置
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id  
OPENROUTER_API_KEY=your_openrouter_key
DEPLOYMENT_MODE=hybrid
LOCAL_RAG_ENABLED=true
```

## 🛠️ 维护说明

### **ngrok隧道管理**
```bash
# 检查隧道状态
curl -s http://127.0.0.1:4040/api/tunnels

# 重启隧道 (如果需要)
pkill ngrok
./ngrok http 8001 --log=stdout &

# 查看隧道日志
curl -s http://127.0.0.1:4040/api/tunnels | jq
```

### **本地RAG服务管理**
```bash
# 检查服务状态
bash 检查RAG服务.sh

# 重启服务 (如果需要)
python3 start_local_rag_service.py restart

# 查看服务日志
tail -f logs/rag_service.log
```

## ⚠️ 注意事项

### **ngrok免费版限制**
- ✅ **HTTPS加密**: 自动提供SSL证书
- ✅ **稳定连接**: 连接会话期间保持
- ⚠️ **地址变化**: 重启ngrok会更换URL
- ⚠️ **流量限制**: 免费版有月流量限制

### **生产环境建议**
1. **ngrok Pro版**: 固定域名，无限流量
2. **固定公网IP**: 企业宽带 + 端口转发
3. **VPS代理**: 云服务器作为代理转发
4. **专线连接**: 企业专线 + VPN

## 🎯 下一步操作

### ✅ **系统已就绪** - 立即可用
1. **本地RAG服务**: ✅ 正常运行
2. **公网隧道**: ✅ 已建立并测试通过
3. **环境变量**: ✅ 已生成配置文件
4. **部署文件**: ✅ zeabur_hybrid_deploy/ 准备完毕

### 🚀 **立即部署Zeabur**
1. 上传 `zeabur_hybrid_deploy/` 目录到Git仓库
2. 在Zeabur中导入仓库
3. 复制 `zeabur_env_ready.txt` 中的环境变量
4. 填入真实的API密钥并部署

**预计部署时间**: 3-5分钟  
**预计总耗时**: 从开始到完全可用 < 10分钟  

## 📞 技术支持

如遇问题，按优先级检查：
1. **本地RAG**: `curl http://127.0.0.1:8001/health`
2. **ngrok隧道**: `curl http://127.0.0.1:4040/api/tunnels`  
3. **公网访问**: `curl https://cf26-1-203-80-194.ngrok-free.app/health`
4. **云端服务**: 查看Zeabur部署日志

---

**✅ 配置完成！** 您现在拥有了完整的本地RAG公网访问能力，可以立即进行Zeabur云端部署！ 