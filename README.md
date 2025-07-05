# Notion-LLM 简化版

> **专注核心功能的 Notion + LLM 异步对话系统**

## ✨ 项目概述

这是一个简化版的 Notion-LLM 项目，专注于核心功能：
- **本地版本**：GUI界面 + 基础RAG功能 + Notion+LLM异步对话
- **云端版本**：API服务 + Notion+LLM异步对话

## 🎯 核心功能

### ✅ 保留功能
- 📝 **Notion输入处理**：监控Notion数据库中的新输入
- 🤖 **LLM异步对话**：调用OpenRouter API进行智能回复  
- 📚 **基础RAG功能**：本地知识库文件检索（基于标签）
- 🎨 **模板系统**：支持多种提示词模板
- 🖥️ **本地GUI**：简洁的桌面应用界面
- ☁️ **云端API**：轻量级Web服务接口


## 🚀 快速开始

### 本地使用

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境**
```bash
cp config.example.json config.json
# 编辑config.json，填入你的API密钥
```

3. **验证配置**
```bash
python validate_config.py
# 验证配置文件是否正确设置
```

4. **启动本地GUI**
```bash
python main.py
```

### 云端部署

#### 快速部署

1. **设置环境变量**
```bash
export NOTION_API_KEY="your_notion_api_key"
export NOTION_DATABASE_ID="your_database_id"
export OPENROUTER_API_KEY="your_openrouter_api_key"
```

2. **启动云端服务**
```bash
python cloud_main.py
```

#### Zeabur/Railway/Render 部署

1. **使用 Dockerfile 部署（推荐）**
   - 确保使用项目根目录的 `Dockerfile`
   - 设置必需的环境变量
   - 服务会自动使用 `cloud_main.py` 启动

2. **使用 Python 部署**
   ```bash
   # 确保启动命令为以下之一：
   python cloud_main.py
   # 或者
   python app.py
   ```

#### 常见部署问题解决

**问题1：tkinter 导入错误**
```
ImportError: libtkb.so: cannot open shared object file
```
**解决方案**：
- ✅ 确保使用 `cloud_main.py` 而不是 `main.py`
- ✅ 使用 `requirements-cloud.txt` 依赖文件  
- ✅ 检查 Dockerfile 中的 CMD 命令

**问题2：端口绑定失败**
```
Address already in use
```
**解决方案**：
- ✅ 确保代码中使用 `PORT` 环境变量
- ✅ 云端平台会自动设置端口

**详细部署指南**：请参考 `cloud-deployment-guide.md` 文件

## 📁 项目结构

```
简化后的项目结构/
├── gui.py                    # 本地GUI应用
├── main.py                   # 本地主程序入口
├── cloud_main.py             # 云端服务入口
├── scheduler.py              # 基础消息调度器
├── notion_handler.py         # Notion API处理
├── llm_handler.py           # LLM API处理
├── template_manager.py       # 模板管理器
├── knowledge_base/           # 本地知识库文件夹
├── templates.json            # 默认模板库
├── config.example.json       # 配置文件示例
└── requirements.txt          # 依赖文件
```

## ⚙️ 配置说明

### 配置验证工具
使用 `validate_config.py` 来验证配置文件是否正确设置：
```bash
python validate_config.py
```

该工具会检查：
- ✅ Notion API密钥和数据库ID是否填入
- ✅ OpenRouter API密钥是否有效
- ✅ 所有必需的配置项是否存在
- ✅ 配置值是否在有效范围内
- ✅ 项目文件结构是否完整

### 必需配置
- `NOTION_API_KEY`: Notion集成密钥
- `NOTION_DATABASE_ID`: Notion数据库ID
- `OPENROUTER_API_KEY`: OpenRouter API密钥

### 可选配置  
- `CHECK_INTERVAL`: 检查间隔（秒，默认120）
- `AUTO_TITLE`: 自动生成标题（默认true）
- `OPENROUTER_MODEL`: 默认模型（默认claude-3.5-sonnet）

### 配置文件示例
```json
{
  "notion": {
    "api_key": "secret_your_notion_api_key",
    "database_id": "your_database_id",
    "input_property_name": "输入",
    "output_property_name": "回复"
  },
  "openrouter": {
    "api_key": "sk-or-your_openrouter_api_key",
    "model": "anthropic/claude-3.5-sonnet"
  },
  "settings": {
    "check_interval": 120,
    "auto_generate_title": true
  }
}
```

## 📚 使用说明

### 本地RAG功能

在`knowledge_base/`文件夹中放置`.md`文件，在Notion的"背景"字段中输入对应的文件名（无扩展名），系统会自动加载相关知识。

### 模板使用

在Notion的"模板选择"字段中选择预设模板，或在`templates.json`中自定义模板。

## 🔧 API接口

### 云端服务API

- `GET /health` - 健康检查
- `POST /start` - 启动调度器  
- `POST /stop` - 停止调度器
- `GET /status` - 获取运行状态

## 🎨 简化优势

### 🏃‍♂️ 更快启动
- 减少依赖包数量
- 移除复杂初始化逻辑
- 简化配置流程

### 🧠 更易理解
- 清晰的功能边界
- 简化的代码结构  
- 减少学习成本

### 🛠️ 更好维护
- 专注核心功能
- 减少错误点
- 易于扩展

## 📈 版本历史

- **v3.0** - 项目简化版本
  - 移除混合架构、连续对话、内网穿透
  - 保留核心Notion+LLM+基础RAG功能
  - 优化代码结构和依赖

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License 