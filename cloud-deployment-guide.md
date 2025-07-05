# 云端部署指南

## 🚀 Zeabur 平台部署步骤

### 1. 准备工作
- 确保你已经有 Zeabur 账户
- 准备好 Notion API 密钥和数据库 ID
- 准备好 OpenRouter API 密钥

### 2. 部署配置

#### 使用 Dockerfile 部署（推荐）
在 Zeabur 项目设置中：
1. 选择 **Docker** 部署方式
2. 确保使用项目根目录的 `Dockerfile`
3. 设置以下环境变量：

```bash
# 必需的环境变量
NOTION_API_KEY=secret_your_notion_api_key
NOTION_DATABASE_ID=your_database_id
OPENROUTER_API_KEY=sk-or-your_openrouter_api_key

# 可选的环境变量
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
CHECK_INTERVAL=120
AUTO_START=true
PORT=8000
```

#### 使用 Python 部署
如果不使用 Docker，确保：
1. 启动命令设置为：`python cloud_main.py`
2. 或者使用：`python app.py`
3. 使用 `requirements-cloud.txt` 作为依赖文件

### 3. 环境变量详细说明

#### 必需变量
- `NOTION_API_KEY`: Notion 集成密钥
- `NOTION_DATABASE_ID`: 主数据库 ID
- `OPENROUTER_API_KEY`: OpenRouter API 密钥

#### 可选变量
- `OPENROUTER_MODEL`: LLM 模型（默认：anthropic/claude-3.5-sonnet）
- `CHECK_INTERVAL`: 检查间隔秒数（默认：120）
- `AUTO_START`: 是否自动启动调度器（默认：true）
- `PORT`: 服务端口（默认：8000）
- `NOTION_TEMPLATE_DATABASE_ID`: 模板库数据库 ID（可选）

### 4. 部署后验证

#### 健康检查
访问：`https://your-domain.zeabur.app/health`

期望返回：
```json
{
  "status": "healthy",
  "service": "notion-llm-cloud-simplified",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

#### 启动调度器
发送 POST 请求到：`https://your-domain.zeabur.app/start`

期望返回：
```json
{
  "success": true,
  "message": "云端调度器启动成功"
}
```

#### 检查状态
访问：`https://your-domain.zeabur.app/status`

期望返回：
```json
{
  "is_running": true,
  "message_count": 0,
  "last_check": "2024-01-01T00:00:00.000000",
  "last_template_sync": null
}
```

### 5. 常见问题解决

#### 问题1：tkinter 导入错误
**错误信息**：`ImportError: libtkb.so: cannot open shared object file`

**解决方案**：
1. 确保使用 `cloud_main.py` 而不是 `main.py`
2. 检查 Dockerfile 中的 CMD 命令
3. 使用 `requirements-cloud.txt` 依赖文件

#### 问题2：端口绑定失败
**错误信息**：`Address already in use`

**解决方案**：
1. 确保使用环境变量 `PORT`
2. 在 cloud_main.py 中使用 `port = int(os.getenv("PORT", 5000))`

#### 问题3：环境变量未读取
**错误信息**：`Missing required environment variables`

**解决方案**：
1. 检查 Zeabur 环境变量设置
2. 确保变量名称完全匹配
3. 重新部署服务

### 6. 其他云平台部署

#### Railway
1. 连接 GitHub 仓库
2. 设置环境变量
3. 确保启动命令为：`python cloud_main.py`

#### Render
1. 选择 Web Service
2. 设置构建命令：`pip install -r requirements-cloud.txt`
3. 设置启动命令：`python cloud_main.py`

#### Heroku
1. 创建 `Procfile`：`web: python cloud_main.py`
2. 使用 `requirements-cloud.txt`
3. 设置环境变量

---

## 🔧 本地测试云端版本

如果需要在本地测试云端版本：

```bash
# 设置环境变量
export NOTION_API_KEY="your_key"
export NOTION_DATABASE_ID="your_id"
export OPENROUTER_API_KEY="your_key"

# 启动云端版本
python cloud_main.py
```

---

## 📞 技术支持

如果遇到部署问题，请提供：
1. 错误日志截图
2. 环境变量配置
3. 使用的云平台名称
4. 部署方式（Docker/Python） 