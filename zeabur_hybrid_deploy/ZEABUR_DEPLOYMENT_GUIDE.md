# Zeabur 混合架构部署指南 🚀

> **当前状态**: ✅ 系统就绪，准备部署  
> **本地服务**: http://127.0.0.1:8001 ✅ 运行中  
> **公网地址**: https://cf26-1-203-80-194.ngrok-free.app ✅ 已配置  
> **部署时间**: 预计3-5分钟  

## 🎯 **立即开始部署**

### **第1步：访问Zeabur控制台**
1. 打开浏览器访问：**https://zeabur.com**
2. 使用GitHub账户登录（推荐）
3. 创建新项目或进入现有项目

### **第2步：连接GitHub仓库**
1. 在Zeabur项目中点击 **"Add Service"**
2. 选择 **"GitHub"**
3. 选择包含 `zeabur_hybrid_deploy` 目录的仓库
4. 指定部署路径为 `zeabur_hybrid_deploy`

### **第3步：配置环境变量**
在Zeabur控制台的 **Environment Variables** 中添加以下变量：

```bash
# === 必需API配置 ===
NOTION_API_KEY=你的notion_api_key
NOTION_DATABASE_ID=你的database_id  
OPENROUTER_API_KEY=你的openrouter_api_key

# === 混合架构配置 ===
DEPLOYMENT_MODE=hybrid
LOCAL_RAG_ENABLED=true

# === 关键配置：本地RAG服务地址 ===
LOCAL_RAG_SERVICE_URL=https://cf26-1-203-80-194.ngrok-free.app

# === 性能调优 ===
RAG_REQUEST_TIMEOUT=10
RAG_HEALTH_CHECK_INTERVAL=300
RAG_RETRY_ATTEMPTS=3
ENABLE_FALLBACK=true
FALLBACK_TIMEOUT=5

# === 运行环境 ===
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO
```

### **第4步：部署配置**
- **服务名称**: notion-llm-hybrid
- **区域**: 选择离您较近的区域（推荐：Singapore 或 Hong Kong）
- **实例类型**: Basic（免费额度足够）
- **自动部署**: 启用

### **第5步：验证部署**
部署完成后（约2-3分钟）：
1. Zeabur会提供一个公网URL，如：`https://notion-llm-hybrid.zeabur.app`
2. 访问健康检查端点：`https://your-app.zeabur.app/health`
3. 应该看到类似响应：
   ```json
   {
     "status": "healthy",
     "deployment_mode": "hybrid",
     "local_rag_connected": true,
     "version": "2.0"
   }
   ```

## 🎉 **部署完成后的功能**

### **智能调度系统**
- **本地优先**: 高性能RAG查询通过本地服务
- **云端降级**: 本地不可用时自动切换
- **实时监控**: 每5分钟检查本地服务健康状态

### **API端点**
- `/health` - 健康检查
- `/query` - 智能问答
- `/knowledge` - 知识库搜索
- `/rag/search` - RAG语义搜索
- `/chat` - 对话接口

### **性能优势**
- **启动时间**: ~5秒 (vs 完整版60秒)
- **内存占用**: ~100MB (vs 完整版2.2GB)
- **响应速度**: 本地RAG ~200ms，云端降级 ~2s

## 🔧 **故障排除**

### **如果部署失败**
1. 检查环境变量是否正确设置
2. 确认 `LOCAL_RAG_SERVICE_URL` 地址可访问
3. 查看Zeabur部署日志

### **如果ngrok地址变化**
1. 获取新的ngrok URL
2. 在Zeabur环境变量中更新 `LOCAL_RAG_SERVICE_URL`
3. 重新部署服务

### **本地RAG服务重启**
```bash
# 重启本地服务
python start_local_rag_service.py

# 重启ngrok隧道
./ngrok http 8001
```

## 📊 **监控和管理**

### **在Zeabur控制台查看**
- **实时日志**: 查看服务运行状态
- **访问统计**: 监控API调用量
- **资源使用**: 查看CPU/内存使用情况

### **本地监控**
```bash
# 检查本地RAG服务
curl http://127.0.0.1:8001/health

# 检查ngrok状态  
curl http://127.0.0.1:4040/api/tunnels
```

---

## 🎯 **现在就开始部署吧！**

所有配置已准备就绪，整个部署过程只需要3-5分钟！

部署完成后，您将拥有：
- ✅ 高性能本地RAG系统
- ✅ 稳定的云端服务
- ✅ 智能降级机制
- ✅ 完整的API接口
- ✅ 实时监控功能

**立即访问 https://zeabur.com 开始部署！** 🚀 