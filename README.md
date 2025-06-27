# Notion-LLM 异步工作流助手

🤖 一个高度可配置的自动化工具，旨在连接Notion数据库、本地知识库和大型语言模型（LLM），实现复杂的异步工作流。

## 🌟 核心功能

### 基础功能
- **🔄 自动化Notion工作流**: 自动监听Notion数据库，当满足特定条件时触发处理流程
- **🤖 智能模型选择**: 支持多种LLM模型，包括标准模式和推理模式
- **📚 本地知识库 (RAG)**: 通过标签自动从本地Markdown文件中读取上下文
- **📋 模板化提示工程**: 使用模板标签应用预设的系统提示词
- **🖥️ 现代化GUI界面**: 简洁美观的图形界面，实时监控和日志

### 高级功能
- **🎯 双异步模式**: 需选择模板才执行处理，避免意外触发
- **🧠 AI自动生成标题**: 对无标题条目自动生成10-20字的自然标题
- **📊 智能统计**: 实时显示等待和处理状态
- **🔄 自动模板同步**: 自动同步模板选项到Notion数据库
- **⚡ 混合推理支持**: 完美支持Gemini 2.5 Pro等推理模型
- **📝 内容智能处理**: 自动长度限制、内容清洗和错误恢复

## 🎯 最新更新 (v2.0)

### ✅ 重大修复
1. **配置文件问题修复**: 修复了GUI配置生成不完整的问题
2. **Notion API错误修复**: 解决了属性名称不匹配导致的400错误
3. **模型ID修复**: 更正了Gemini 2.5 Pro的模型映射
4. **推理模式支持**: 新增对Gemini 2.5 Pro推理模式的完整支持

### 🚀 性能优化
- **智能内容截断**: Notion Rich Text 2000字符限制保护
- **增强错误处理**: 详细的错误日志和自动恢复机制
- **内容清洗改进**: 更温和的内容处理，保留格式完整性

### 🎨 用户体验提升
- **现代化UI设计**: 全新的卡片式界面设计
- **实时状态显示**: 详细的处理进度和统计信息
- **完整的模板管理**: 内置模板编辑器和导入导出功能

## 🤖 支持的模型

### Google Gemini 系列
- ✅ **Gemini 2.5 Flash** (`google/gemini-2.5-flash`) - 快速响应
- ✅ **Gemini 2.5 Pro** (`google/gemini-2.5-pro`) - 推理模式支持

### Anthropic Claude 系列  
- ✅ **Claude 4 Sonnet** (`anthropic/claude-sonnet-4`) - 高质量分析

### OpenAI ChatGPT 系列
- ✅ **ChatGPT 4.1** (`openai/gpt-4.1`) 
- ✅ **ChatGPT O3** (`openai/o3`)

### DeepSeek 系列
- ✅ **DeepSeek R1** (`deepseek/deepseek-r1-0528`) - 推理模型
- ✅ **DeepSeek V3** (`deepseek/deepseek-chat-v3-0324`) - 对话模型

> **注意**: 所有模型都通过 [OpenRouter.ai](https://openrouter.ai/) 访问，支持标准模式和推理模式的自动适配。

## ⚙️ 快速开始

### 1. 环境准备

#### 安装依赖
```bash
# 克隆项目
git clone [你的项目地址]
cd 异步小项目

# 安装依赖
pip install -r requirements.txt
```

#### API 密钥准备
- **Notion API**: 访问 [Notion Developers](https://www.notion.so/my-integrations) 创建集成
- **OpenRouter API**: 访问 [OpenRouter.ai](https://openrouter.ai/) 获取密钥

### 2. Notion 数据库设置

创建数据库并包含以下字段：

| 字段名称 | 字段类型 | 必需 | 说明 |
|---------|---------|------|------|
| **标题** | Title | ✅ | 任务标题，为空时自动生成 |
| **输入** | Rich Text | ✅ | 用户输入的内容 |
| **回复** | Rich Text | ✅ | LLM生成的回复 |
| **模板选择** | Select | ✅ | 选择提示词模板 |
| **模型** | Select | ✅ | 选择LLM模型 |
| **背景** | Multi-select | ✅ | 选择知识库文件 |
| **状态** | Status | ⚪ | 可选的状态跟踪 |

### 3. 配置文件设置

复制 `config.example.json` 为 `config.json` 并配置：

```json
{
  "notion": {
    "api_key": "你的Notion API密钥",
    "database_id": "你的数据库ID",
    "input_property_name": "输入",
    "output_property_name": "回复", 
    "template_property_name": "模板选择",
    "model_property_name": "模型",
    "knowledge_base_property_name": "背景",
    "title_property_name": "标题",
    "knowledge_base_path": "knowledge_base"
  },
  "openrouter": {
    "api_key": "你的OpenRouter API密钥"
  },
  "settings": {
    "check_interval": 60,
    "auto_generate_title": true,
    "title_max_length": 20,
    "title_min_length": 10,
    "auto_sync_templates": true,
    "model_mapping": {
      "Gemini 2.5 pro": "google/gemini-2.5-pro",
      "Gemini 2.5 flash": "google/gemini-2.5-flash",
      "Claude 4 sonnet": "anthropic/claude-sonnet-4"
    }
  }
}
```

### 4. 知识库设置

在 `knowledge_base/` 文件夹中创建Markdown文件：
- 文件名需与Notion中的"背景"标签完全一致
- 支持中文文件名
- 例如：`AI效率中心.md`、`业务理解.md`

## 🚀 使用指南

### 启动程序
```bash
python main.py
```

### 工作流程
1. **在Notion中创建新条目**
2. **填写"输入"内容**
3. **选择"模板选择"、"模型"、"背景"**
4. **程序自动检测并处理**
5. **查看"回复"字段的AI回复**

### 触发条件
程序会处理满足以下**所有**条件的条目：
- ✅ "回复"字段为空
- ✅ "模板选择"已选择
- ✅ "模型"已选择  
- ✅ "背景"已选择（至少一个）

## 🛠️ 功能特性

### 智能适配
- **推理模式自动识别**: 自动识别并处理Gemini 2.5 Pro的推理输出
- **内容长度保护**: 自动截断超长内容，防止API限制
- **错误自动恢复**: 失败时自动记录错误信息到Notion

### 用户体验
- **现代化界面**: 卡片式设计，清晰的状态指示
- **实时监控**: 处理进度、统计信息一目了然
- **详细日志**: 完整的操作记录和错误诊断

### 可扩展性
- **模板管理**: 内置编辑器，支持导入导出
- **模型映射**: 灵活的模型配置系统
- **知识库**: 简单的文件命名规则，易于扩展

## 🔧 故障排除

### 常见问题

**❌ 程序无法启动**
- 检查依赖包是否安装完整
- 确认配置文件格式正确

**❌ 监听功能报错**  
- 验证Notion API密钥和数据库ID
- 确认字段名称与配置文件匹配

**❌ Gemini 2.5 Pro返回空内容**
- 已修复：程序现在自动支持推理模式
- 确保使用最新版本的代码

**❌ Notion更新失败**
- 检查Notion集成权限
- 确认内容长度不超过限制

### 日志分析
程序提供详细的日志输出：
- 🟢 成功操作显示为绿色
- 🔴 错误操作显示为红色  
- 📝 处理信息显示具体步骤

## 📈 开发计划

### 即将推出
- [ ] 更多LLM模型支持
- [ ] 批量处理功能
- [ ] 自定义字段映射
- [ ] 多数据库支持

### 长期规划
- [ ] 插件系统
- [ ] 云端部署支持
- [ ] 工作流可视化编辑器

## 🤝 贡献指南

欢迎提交Issues和Pull Requests！

1. Fork 本项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

感谢所有贡献者和用户的支持！

---

**🎉 开始你的自动化工作流之旅吧！**

> 最后更新: 2025-06-27  
> 版本: v2.0 - 推理模式支持版本 