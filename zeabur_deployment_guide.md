
# 🚀 Zeabur部署指南

## 📊 测试结果总览
测试时间: 2025-07-02 20:59:19
部署就绪: ✅ 是

- ✅ 通过 部署文件检查: 所有7个必需文件都存在
- ✅ 通过 依赖包轻量化: 依赖包配置正确，已移除重型AI依赖
- ✅ 通过 模块导入测试: 导入结果:
   ✅ cloud_hybrid_main.HybridCloudScheduler
   ✅ notion_handler.NotionHandler
   ✅ llm_handler.LLMHandler
   ✅ template_manager.TemplateManager
- ✅ 通过 调度器初始化: 调度器初始化成功，所有组件就绪
- ✅ 通过 本地RAG连接: 本地RAG服务运行正常 (版本: 1.0.0)
- ✅ 通过 Flask应用测试: Flask应用正常，包含11个路由


## 🌐 Zeabur部署步骤

### 1. 准备代码仓库
```bash
# 进入部署目录
cd zeabur_hybrid_deploy

# 初始化Git仓库（如果需要）
git init
git add .
git commit -m "混合架构云端服务部署"

# 推送到GitHub/GitLab
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. 创建Zeabur项目
1. 访问 https://dash.zeabur.com
2. 点击 "New Project"
3. 选择 "Git Repository"
4. 连接你的代码仓库

### 3. 配置环境变量
在Zeabur项目设置中添加：

```env
# 必需配置
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
OPENROUTER_API_KEY=your_openrouter_key

# 混合架构配置
LOCAL_RAG_SERVICE_URL=http://YOUR_LOCAL_IP:8001
ENABLE_RAG_FALLBACK=true
RAG_FALLBACK_MESSAGE=本地知识库暂时不可用，已采用基础模式处理

# 可选配置
AUTO_START=true
CHECK_INTERVAL=120
```

### 4. 本地RAG服务配置
确保你的本地RAG服务：
- 正在运行在端口8001
- 可以从公网访问（使用固定IP或DDNS）
- 防火墙已开放8001端口

### 5. 部署和验证
1. Zeabur会自动检测app.py并开始部署
2. 部署完成后访问健康检查: https://your-app.zeabur.app/health
3. 检查系统状态: https://your-app.zeabur.app/status

## 🔧 故障排除

如果部署失败，检查：
1. 环境变量是否配置完整
2. 代码是否成功推送到仓库
3. requirements.txt格式是否正确
4. 本地RAG服务是否可从公网访问

## 📞 获得帮助

如有问题请检查：
- 部署日志
- 健康检查API响应
- 本地RAG服务状态
