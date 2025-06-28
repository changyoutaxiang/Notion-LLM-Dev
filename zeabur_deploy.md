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

### 2. 自动化部署（推荐）
项目已配置完整的 Dockerfile，支持一键部署：
- ✅ 自动从正确位置复制所有必要文件
- ✅ 自动安装依赖包
- ✅ 自动配置运行环境
- ✅ 支持 Git 推送自动重新部署

**部署的文件包括：**
- `cloud_main.py` (云端主程序，来自 zeabur_deploy/)
- `notion_handler.py` (来自根目录)
- `llm_handler.py` (来自根目录)
- `template_manager.py` (来自根目录)
- `templates.json` (来自根目录)
- `knowledge_base/` (来自根目录)
- `requirements_cloud.txt` (来自 zeabur_deploy/)

## 🔧 部署步骤

### 1. Git部署（推荐）
1. 登录 [Zeabur](https://zeabur.com)
2. 创建新项目 → "Deploy from Git"
3. 连接你的 GitHub 仓库
4. 选择分支：`main`
5. Zeabur 会自动识别 Dockerfile 并构建

### 2. 配置运行环境
Dockerfile 已自动配置：
- ✅ Python 3.9 运行时
- ✅ 启动命令：`python cloud_main.py`
- ✅ 端口：8080
- ✅ 依赖安装：`requirements_cloud.txt`

### 3. 设置环境变量
在Zeabur控制台的Environment页面添加所有必需的环境变量

### 4. 自动部署
Zeabur会自动：
- 📦 构建Docker镜像
- 📋 安装所有依赖
- 🚀 启动应用程序
- 🌐 提供访问域名

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
- ✅ Git推送自动重新部署

### 📊 监控与日志：
- 实时日志查看
- 运行状态监控
- 错误自动重试
- 健康检查接口

## 🛠️ 故障排除

### 常见问题：

1. **构建失败**
   - 检查 Dockerfile 语法是否正确
   - 确认所有必要文件都在仓库中
   - 查看构建日志中的具体错误

2. **启动失败**
   - 检查环境变量是否正确设置
   - 查看日志中的错误信息

3. **无法处理消息**
   - 验证Notion API密钥和数据库ID
   - 检查OpenRouter API密钥

4. **知识库文件缺失**
   - 确保 `knowledge_base/` 目录在根目录下
   - 检查文件是否正确推送到 Git 仓库

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
5. **版本管理**：使用有意义的Git提交信息，便于追踪部署

## 🔄 更新部署

### 自动更新（推荐）
1. 本地修改代码并测试
2. 提交到 Git 仓库：`git push origin main`
3. Zeabur 自动检测变更并重新部署
4. 零停机时间更新

### 手动重新部署
在 Zeabur 控制台点击 "Redeploy" 按钮

---

## 📝 版本更新说明

### v2.3 更新
- ✅ 修复了 Dockerfile 文件路径问题
- ✅ 优化了构建流程，减少重复文件
- ✅ 支持完全自动化的 Git 部署
- ✅ 更好的错误处理和日志记录 