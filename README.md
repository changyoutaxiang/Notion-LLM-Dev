# Notion-LLM 异步通信助手

一个帮助你在Notion数据库与LLM之间实现异步通信的Mac端软件。

## 🌟 功能特点

- 📝 **自动监听** Notion数据库中的新消息
- 🧠 **智能处理** 通过OpenRouter调用各种LLM模型
- 🔄 **自动回写** 将LLM回复写回Notion数据库
- 🖥️ **图形界面** 简单易用的操作界面
- 📊 **实时监控** 处理状态和日志记录
- ⚙️ **灵活配置** 支持多种LLM模型选择

## 📋 准备工作

### 1. 获取API密钥

#### Notion API密钥
1. 访问 [Notion Developers](https://www.notion.so/my-integrations)
2. 点击 "New integration" 创建新集成
3. 填写集成信息，获取 API 密钥
4. 将集成添加到你要使用的数据库页面

#### OpenRouter API密钥
1. 访问 [OpenRouter](https://openrouter.ai/)
2. 注册账户并获取API密钥
3. 充值一定金额用于API调用

### 2. 设置Notion数据库

在Notion中创建一个数据库，包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | Title | 消息标题 |
| 输入内容 | Rich Text | 发送给LLM的内容 |
| LLM回复 | Rich Text | LLM的回复（程序自动填写） |

### 3. 获取数据库ID

1. 打开你的Notion数据库页面
2. 复制页面URL，格式类似：
   ```
   https://www.notion.so/your-workspace/xxxxxxxxx?v=yyyyyyyy
   ```
3. 其中 `xxxxxxxxx` 部分就是数据库ID

## 🚀 安装使用

### 1. 安装Python依赖

```bash
# 进入项目目录
cd 异步小项目

# 安装依赖包
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

### 3. 配置API

1. 程序启动后，切换到"配置设置"标签页
2. 填入你的Notion API密钥和数据库ID
3. 填入OpenRouter API密钥
4. 选择要使用的LLM模型
5. 点击"保存配置"
6. 点击"测试连接"确保配置正确

### 4. 开始监听

1. 切换到"运行监控"标签页
2. 点击"开始监听"按钮
3. 程序将每2分钟检查一次Notion数据库
4. 在"运行日志"标签页可以查看详细日志

## 📖 使用方法

1. **发送消息给LLM**：
   - 在Notion数据库中新增一行
   - 填写"标题"和"输入内容"
   - 程序会自动检测并处理

2. **查看LLM回复**：
   - 处理完成后，"LLM回复"字段会自动填入
   - 程序会自动处理所有"LLM回复"字段为空的记录

3. **监控处理状态**：
   - 在程序的"运行监控"页面查看实时状态
   - 在"运行日志"页面查看详细处理记录

## 🔧 高级配置

### 修改检查间隔
在配置页面的"检查间隔(秒)"字段修改，默认120秒（2分钟）。

### 选择不同的LLM模型
支持的模型包括：
- `anthropic/claude-sonnet-4` (最新最强，推荐)
- `anthropic/claude-3.5-sonnet` (平衡性能)
- `anthropic/claude-3-haiku` (更快更便宜)
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`

### 自定义系统提示
可以在`scheduler.py`文件中修改系统提示词：
```python
success, llm_reply = self.llm_handler.send_message(
    content,
    "你是一个智能助手，请认真回答用户的问题。请用中文回复。"  # 修改这里
)
```

## 🛠️ 打包成独立应用

如果你想将程序打包成独立的Mac应用：

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包程序
pyinstaller --onefile --windowed --name "Notion-LLM助手" main.py

# 生成的应用在 dist/ 目录下
```

## ❗ 常见问题

### Q: 程序提示"Notion连接失败"
A: 检查API密钥是否正确，数据库ID是否正确，以及是否已将集成添加到数据库。

### Q: LLM处理失败
A: 检查OpenRouter API密钥是否正确，账户是否有余额。

### Q: 程序无法检测到新消息
A: 确保Notion数据库中的"输入内容"字段有内容，且"LLM回复"字段为空。

### Q: 如何停止程序
A: 在"运行监控"页面点击"停止监听"，或直接关闭程序窗口。

## 📝 注意事项

1. **API费用**：OpenRouter按使用量收费，请注意控制成本
2. **网络连接**：程序需要稳定的网络连接
3. **隐私安全**：API密钥请妥善保管，不要分享给他人
4. **备份重要**：建议定期备份Notion数据库

## 🤝 技术支持

如果遇到问题，可以：
1. 查看"运行日志"页面的错误信息
2. 检查网络连接和API密钥配置
3. 重启程序尝试解决临时问题

---

**祝你使用愉快！** 🎉 