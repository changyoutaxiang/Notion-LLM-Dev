# Notion-LLM 异步工作流助手

一个高度可配置的自动化工具，旨在连接Notion数据库、本地知识库和大型语言模型（LLM），实现复杂的异步工作流。

## 🌟 核心功能

- **自动化Notion工作流**: 自动监听Notion数据库，当满足特定条件时触发处理流程。
- **动态模型选择**: 在Notion中通过"类型"标签，为每个任务动态选择不同的LLM。
- **本地知识库 (RAG)**: 通过在Notion中选择"背景"标签，自动从本地Markdown文件中读取上下文，并注入到LLM的提示词中。
- **模板化提示工程**: 使用"模版"标签来应用预设的系统提示词，以适应不同的任务场景。
- **自动生成标题**: 对无标题的条目，能够根据内容自动生成简洁的标题。
- **图形化操作界面**: 提供一个简单的GUI来启动、停止和监控程序的运行状态及日志。
- **高度可配置**: 所有关键参数，包括API密钥、数据库ID、Notion属性名等，都通过 `config.json` 文件进行统一管理。

## ⚙️ 配置与安装

### 1. 准备工作

#### a. API 密钥
- **Notion**: 访问 [Notion Developers](https://www.notion.so/my-integrations) 创建一个新的集成，并获取API密钥。
- **OpenRouter**: 访问 [OpenRouter.ai](https://openrouter.ai/) 注册并获取API密钥。

#### b. Notion 数据库
在你的Notion工作区中创建一个数据库，并确保它包含以下属性：

| 属性名 (可配置) | 类型         | 说明                                               |
|:----------------|:-------------|:---------------------------------------------------|
| `标题`          | `Title`      | 任务的标题，如果留空，程序会自动生成。             |
| `输入`          | `Rich Text`  | 你想让LLM处理的核心内容。                          |
| `回复`          | `Rich Text`  | LLM的生成结果将自动写回这里。                      |
| `类型`          | `Select`     | **（触发条件）** 用于选择本次任务使用的LLM。           |
| `模版`          | `Select`     | **（触发条件）** 用于选择本次任务使用的提示词模板。   |
| `背景`          | `Multi-select`| **（触发条件）** 用于关联本地知识库中的 `.md` 文件。|
| `状态`          | `Status`     | （可选）用于追踪任务状态。                         |

**重要**:
1.  确保你创建的Notion集成有权限访问这个数据库。
2.  复制数据库的ID。它通常是浏览器URL中 `notion.so/` 之后、`?v=` 之前的那串长字符。

#### c. 本地知识库
1.  在项目根目录下，有一个 `knowledge_base` 文件夹。
2.  你可以在这里创建任意数量的 Markdown 文件 (`.md`)。
3.  每个文件的**文件名（不含扩展名）**应与你在Notion数据库"背景"属性中设置的标签名完全一致。
    -   例如，如果你的背景标签是 `AI效率中心`，那么你应该在 `knowledge_base` 文件夹中创建一个名为 `AI效率中心.md` 的文件。

### 2. 安装与配置

#### a. 安装依赖
```bash
# 进入项目目录
cd 你的项目文件夹

# 安装依赖
pip install -r requirements.txt
```

#### b. 创建配置文件
1.  将 `config.example.json` 文件复制一份，并重命名为 `config.json`。
2.  打开 `config.json` 并填入你的信息。

#### c. `config.json` 文件详解
```json
{
  "notion": {
    "api_key": "你的Notion API密钥",
    "database_id": "你的Notion数据库ID",
    "input_property_name": "输入",
    "output_property_name": "回复",
    "template_property_name": "模版",
    "knowledge_base_property_name": "背景",
    "model_property_name": "类型",
    "title_property_name": "标题",
    "knowledge_base_path": "knowledge_base"
  },
  "openrouter": {
    "api_key": "你的OpenRouter API密钥"
  },
  "settings": {
    "check_interval": 30, // 检查Notion的频率（秒）
    "auto_generate_title": true, // 是否自动生成标题
    "model_mapping": {
      // 在Notion"类型"中看到的名字 -> OpenRouter的模型ID
      "Gemini 2.5 pro": "google/gemini-pro-2.5",
      "Claude 4 sonnet": "anthropic/claude-sonnet-4",
      // ...其他模型
    }
  }
}
```

## 🚀 运行与使用

### 1. 启动程序
```bash
python main.py
```
程序启动后会显示一个小的GUI窗口。

### 2. 开始/停止
- 点击 **"启动"** 按钮，程序将开始按照 `check_interval` 设定的频率监控Notion数据库。
- 点击 **"停止"** 按钮，程序将安全地完成当前任务并停止监听。

### 3. 工作流触发
程序会自动处理满足以下 **所有** 条件的数据库条目：
1.  **`回复`** 字段为空。
2.  **`类型`** 字段已选择。
3.  **`模版`** 字段已选择。
4.  **`背景`** 字段已选择（至少一个）。

### 4. 查看日志
所有的操作、错误和状态信息都会实时显示在GUI的日志区域，方便你监控和调试。

## 🤝 技术支持

如果遇到问题，请首先检查GUI中的日志输出。常见的错误原因包括：
- API密钥或数据库ID不正确。
- `config.json` 中的属性名与你Notion数据库中的实际属性名不匹配。
- 网络连接问题。

---

**祝你使用愉快！** 🎉 