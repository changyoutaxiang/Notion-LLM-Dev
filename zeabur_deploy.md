# 🚀 Zeabur云端部署指南

## 📋 部署准备

### 1. 环境变量配置
在Zeabur项目中设置以下环境变量：

**必需变量：**
```
NOTION_API_KEY=你的Notion_API密钥
NOTION_DATABASE_ID=你的Notion数据库ID
OPENROUTER_API_KEY=你的OpenRouter_API密钥
```

**可选变量：**
```
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
CHECK_INTERVAL=120
AUTO_START=true
AUTO_TITLE=true
TITLE_MAX_LENGTH=20
TITLE_MIN_LENGTH=10

# Notion属性名称（如果与默认不同）
NOTION_INPUT_PROP=输入
NOTION_OUTPUT_PROP=回复
NOTION_TEMPLATE_PROP=模板选择
NOTION_KNOWLEDGE_PROP=背景
NOTION_MODEL_PROP=模型
NOTION_TITLE_PROP=标题

# 模型映射（JSON格式）
MODEL_MAPPING={"Gemini 2.5 pro": "google/gemini-2.5-pro"}
```

### 2. 部署文件
将以下文件上传到Zeabur：
- `cloud_main.py` (主程序)
- `notion_handler.py`
- `llm_handler.py` 
- `template_manager.py`
- `templates.json`
- `requirements_cloud.txt`
- `knowledge_base/` 文件夹

## 🔧 部署步骤

### 1. 创建Zeabur项目
1. 登录 [Zeabur](https://zeabur.com)
2. 创建新项目
3. 选择Git仓库部署或文件上传

### 2. 配置运行环境
1. 选择Python运行时
2. 设置启动命令：`python cloud_main.py`
3. 依赖文件：`requirements_cloud.txt`

### 3. 设置环境变量
在Zeabur控制台的Environment页面添加所有必需的环境变量

### 4. 部署应用
点击部署，Zeabur会自动：
- 安装依赖
- 启动应用
- 提供访问域名

## 🌐 API接口

部署成功后，你可以通过以下API控制程序：

### 健康检查
```bash
GET https://你的域名/health
```

### 启动调度器
```bash
POST https://你的域名/start
```

### 停止调度器  
```bash
POST https://你的域名/stop
```

### 查看状态
```bash
GET https://你的域名/status
```

### 手动处理一次
```bash
POST https://你的域名/process-once
```

## ✨ 优势

### 🆔 vs 本地运行：
- ✅ 24/7不间断运行
- ✅ 无需本地环境
- ✅ 自动重启和恢复
- ✅ 可通过API远程控制
- ✅ 多地区部署可选

### 📊 监控与日志：
- 实时日志查看
- 运行状态监控
- 错误自动重试
- 健康检查接口

## 🛠️ 故障排除

### 常见问题：

1. **启动失败**
   - 检查环境变量是否正确设置
   - 查看日志中的错误信息

2. **无法处理消息**
   - 验证Notion API密钥和数据库ID
   - 检查OpenRouter API密钥

3. **知识库文件缺失**
   - 确保上传了完整的`knowledge_base`文件夹

### 查看日志：
```bash
# 在Zeabur控制台查看实时日志
# 或通过API获取状态信息
curl https://你的域名/status
```

## 💡 最佳实践

1. **定期检查**：设置合理的CHECK_INTERVAL（建议120秒）
2. **监控健康**：设置外部监控访问/health接口
3. **备份配置**：保存好所有环境变量配置
4. **日志监控**：定期查看应用日志确保正常运行

## 🔄 更新部署

1. 修改代码后提交到Git仓库
2. Zeabur会自动检测变更并重新部署
3. 或者直接上传新文件覆盖 