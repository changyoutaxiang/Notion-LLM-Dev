# 🚀 Zeabur Git一键部署指南

## 📍 Git仓库信息
- **仓库地址**: https://github.com/changyoutaxiang/-notion-NotionHandler
- **分支**: main
- **云端主程序**: `cloud_main.py`

## 🎯 一键部署步骤

### 第1步：登录Zeabur
1. 访问 [Zeabur官网](https://zeabur.com)
2. 使用GitHub账号登录（推荐）

### 第2步：创建项目并连接Git
1. 点击 **"Create Project"**
2. 选择 **"Deploy from Git"** 
3. 授权Zeabur访问你的GitHub账户
4. 选择仓库：**`changyoutaxiang/-notion-NotionHandler`**
5. 选择分支：**`main`**

### 第3步：配置部署设置
在项目配置页面设置：

**Framework Preset**: `Other`
**Root Directory**: `/` (根目录)
**Build Command**: (留空，使用默认)
**Install Command**: `pip install -r requirements_cloud.txt`
**Start Command**: `python cloud_main.py`

### 第4步：设置环境变量
在 **Environment** 页面添加以下变量：

```bash
# 核心API密钥
NOTION_API_KEY=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
NOTION_DATABASE_ID=21e3bbbae6d280b9af5ce49168ccd347
OPENROUTER_API_KEY=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

# 基础配置
OPENROUTER_MODEL=anthropic/claude-sonnet-4
CHECK_INTERVAL=60
AUTO_START=true
AUTO_TITLE=true
TITLE_MAX_LENGTH=20
TITLE_MIN_LENGTH=10

# Notion字段映射
NOTION_INPUT_PROP=输入
NOTION_OUTPUT_PROP=回复
NOTION_TEMPLATE_PROP=模板选择
NOTION_KNOWLEDGE_PROP=背景
NOTION_MODEL_PROP=模型
NOTION_TITLE_PROP=标题

# 模型映射 (JSON格式，一行)
MODEL_MAPPING={"Gemini 2.5 pro": "google/gemini-2.5-pro", "Gemini 2.5 flash": "google/gemini-2.5-flash", "Claude 4 sonnet": "anthropic/claude-sonnet-4", "Chatgpt 4.1": "openai/gpt-4.1", "Chatgpt O3": "openai/o3", "Deepseek R1": "deepseek/deepseek-r1-0528", "Deepseek V3": "deepseek/deepseek-chat-v3-0324"}
```

### 第5步：部署启动
1. 点击 **"Deploy"** 按钮
2. 等待部署完成（通常2-3分钟）
3. 获得访问域名，如：`https://your-project.zeabur.app`

## ✅ 验证部署

### 健康检查
访问：`https://你的域名.zeabur.app/health`

期望返回：
```json
{
  "status": "healthy",
  "timestamp": "2024-06-27T10:20:30.123456",
  "scheduler_status": {
    "is_running": true,
    "message_count": 0,
    "last_check": "2024-06-27T10:20:30.123456",
    "config_loaded": true
  }
}
```

### 查看运行状态
访问：`https://你的域名.zeabur.app/status`

### 手动触发处理
```bash
curl -X POST https://你的域名.zeabur.app/process-once
```

## 🔄 自动更新机制

### Git推送自动部署
当你向GitHub推送新代码时，Zeabur会自动：
1. 检测代码变更
2. 重新构建应用
3. 自动部署新版本
4. 零停机时间更新

### 手动重新部署
在Zeabur控制台点击 **"Redeploy"** 按钮

## 📊 监控与管理

### 实时日志
在Zeabur控制台的 **"Logs"** 页面查看：
- 应用启动日志
- 消息处理日志  
- 错误信息
- API调用记录

### 性能监控
- CPU使用率
- 内存使用量
- 网络流量
- 响应时间

### 远程控制API
```bash
# 启动调度器
curl -X POST https://你的域名.zeabur.app/start

# 停止调度器
curl -X POST https://你的域名.zeabur.app/stop

# 查看状态
curl https://你的域名.zeabur.app/status

# 手动处理一次
curl -X POST https://你的域名.zeabur.app/process-once
```

## 🛠️ 故障排除

### 常见问题

1. **部署失败**
   - 检查环境变量是否正确设置
   - 确认Start Command为: `python cloud_main.py`
   - 查看Build Logs中的错误信息

2. **程序无响应**
   - 访问 `/health` 检查服务状态
   - 查看Logs页面的错误信息
   - 确认API密钥是否有效

3. **无法处理消息**
   - 检查Notion API密钥和数据库ID
   - 确认OpenRouter API密钥有效
   - 验证Notion数据库字段名称

### 调试技巧
```bash
# 查看详细状态
curl https://你的域名.zeabur.app/status | jq

# 测试单次处理
curl -X POST https://你的域名.zeabur.app/process-once

# 重启应用
在Zeabur控制台点击"Restart"
```

## 💡 最佳实践

1. **监控健康状态**
   - 设置外部监控服务定期访问 `/health`
   - 配置告警通知

2. **日志管理**
   - 定期查看应用日志
   - 关注错误模式

3. **版本管理**
   - 在Git中使用有意义的提交信息
   - 重要更新前先在本地测试

4. **安全考虑**
   - 定期更换API密钥
   - 监控异常访问

## 🎉 部署完成！

部署成功后，你的Notion-LLM助手将：
- ✅ 24/7不间断运行
- ✅ 自动处理Notion消息
- ✅ 支持远程API控制
- ✅ 代码更新自动部署
- ✅ 完整的监控和日志 