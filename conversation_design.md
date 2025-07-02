# 连续对话功能设计文档（方案一：会话状态扩展模式）

## 🎯 设计目标

在现有Notion-LLM系统基础上，以最小侵入的方式添加连续对话功能，保持用户操作习惯不变。

## 📊 现有架构分析

### 当前数据库字段
```
主数据库字段：
├── 标题 (title_property_name)           - Text
├── 输入 (input_property_name)           - Rich Text  
├── 回复 (output_property_name)          - Rich Text
├── 模版 (template_property_name)        - Select
├── 背景 (knowledge_base_property_name)  - Select
└── 类型 (model_property_name)           - Select
```

### 当前处理流程
```
1. 用户在Notion创建条目，填写：输入内容 + 选择模版/背景/类型
2. 系统检测到待处理条目（回复为空且三个选择字段已填）
3. 根据模版获取系统提示词 + 根据背景获取RAG上下文
4. 发送给LLM处理，获得回复
5. 将回复写入Notion页面内容，标记处理完成
```

## 🏗️ 连续对话扩展设计

### 新增数据库字段（必需）

#### 方案A：最小扩展（推荐）
```
新增字段：
├── 会话ID (session_id)          - Rich Text    - 用于标识对话会话
├── 父消息ID (parent_id)         - Rich Text    - 指向上一条消息的页面ID
└── 会话状态 (session_status)    - Select       - active/closed/archived
```

#### 方案B：完整扩展（可选）
```
额外字段：
├── 对话轮次 (conversation_turn) - Number      - 当前对话的轮次序号
├── 会话标题 (session_title)     - Rich Text   - 整个会话的主题标题
└── 上下文长度 (context_length)  - Number      - 当前累积的上下文长度
```

### 新增组件设计

#### 1. ConversationManager（会话管理器）
```python
class ConversationManager:
    """管理连续对话的会话状态"""
    
    def __init__(self, notion_handler):
        self.notion_handler = notion_handler
    
    def get_session_id(self, page_id):
        """获取或生成会话ID"""
        
    def get_conversation_history(self, session_id, max_turns=5):
        """获取对话历史"""
        
    def build_conversation_context(self, session_id, current_content):
        """构建包含历史的对话上下文"""
        
    def update_session_status(self, session_id, status):
        """更新会话状态"""
```

#### 2. ContextBuilder（上下文构建器）
```python
class ContextBuilder:
    """智能构建对话上下文"""
    
    def build_continuous_context(self, history, current_msg, rag_context, template):
        """构建连续对话的完整上下文"""
        
    def summarize_long_history(self, history):
        """总结过长的对话历史"""
        
    def extract_key_information(self, conversation):
        """从对话中提取关键信息"""
```

### 工作流程设计

#### 新的处理流程
```
1. 用户创建新条目
   ├── 如果填写了parent_id -> 继续已有对话
   └── 如果未填写parent_id -> 开始新对话
   
2. 系统检测处理条件
   ├── 基本条件：回复为空 && 模版/背景/类型已选择
   └── 新增条件：检查会话状态和父消息关系
   
3. 上下文构建（新增）
   ├── 获取对话历史（如果是连续对话）
   ├── 构建RAG知识上下文
   ├── 整合模版系统提示词
   └── 组合成完整上下文
   
4. LLM处理
   ├── 发送完整上下文给LLM
   └── 获取回复
   
5. 结果更新
   ├── 更新回复内容到当前页面
   ├── 更新会话状态和轮次信息
   └── 记录对话历史关系
```

## 🛠️ 实施计划

### 阶段一：基础字段和数据结构（1周）
- [ ] 扩展config.json配置
- [ ] 修改NotionHandler支持新字段
- [ ] 创建ConversationManager基础框架
- [ ] 编写数据库字段创建指南

### 阶段二：会话逻辑实现（1-2周）
- [ ] 实现会话ID生成和管理
- [ ] 实现对话历史获取
- [ ] 实现上下文构建逻辑
- [ ] 修改调度器支持连续对话

### 阶段三：界面和体验优化（1周）
- [ ] GUI界面显示会话信息
- [ ] 会话状态可视化
- [ ] 错误处理和恢复机制
- [ ] 用户指导文档

### 阶段四：测试和优化（1周）
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 用户测试反馈

## 📝 用户使用方式

### 开始新对话
```
1. 在Notion创建新条目
2. 填写"输入"内容
3. 选择"模版"、"背景"、"类型"
4. 不填写"父消息ID"（系统自动开始新会话）
5. 等待AI回复
```

### 继续对话
```
1. 在Notion创建新条目
2. 填写"输入"内容（新的问题或回应）
3. 选择"模版"、"背景"、"类型"
4. 填写"父消息ID"（复制上一条消息的页面ID）
5. 等待AI回复（会包含对话历史上下文）
```

### 管理会话
```
1. 查看"会话状态"了解对话状态
2. 通过"会话ID"查找相关对话
3. 设置"会话状态"为"closed"结束对话
```

## 🔍 技术细节

### 对话历史存储策略
- 使用Notion页面关系链存储对话历史
- parent_id字段建立父子关系
- session_id字段标识会话归属
- 支持树状对话结构（支持分支对话）

### 上下文管理策略
- 最大历史轮次限制（默认5轮）
- 超长历史自动总结
- 智能选择关键历史信息
- 与RAG知识库上下文平衡

### 性能考虑
- 缓存频繁访问的会话历史
- 批量查询优化
- 异步处理长对话历史
- 定期清理过期会话

## 🎯 预期效果

### 用户体验
- ✅ 学习成本为零（仍在Notion中操作）
- ✅ 支持自然的连续对话
- ✅ 保持所有现有功能
- ✅ 可视化会话管理

### 技术优势
- ✅ 最小架构改动
- ✅ 向后兼容性
- ✅ 易于维护和扩展
- ✅ 稳定可靠

## 🚀 后续扩展可能性

1. **会话分支管理**：支持从历史消息分支出新对话
2. **会话模板**：为不同类型的连续对话创建专门模板
3. **会话分析**：统计和分析对话模式
4. **会话导出**：将完整对话导出为文档
5. **多人会话**：支持多用户参与的会话 