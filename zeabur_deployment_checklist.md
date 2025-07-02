# 🚀 Zeabur 部署问题诊断清单

## 📊 当前状态分析
- ✅ 应用已部署并启动运行
- ❓ 可能存在环境变量配置不完整
- 🎯 需要验证核心功能是否正常

## 🔧 必需环境变量补充

### 第一步：验证核心变量
确认以下变量已正确设置：
```
NOTION_API_KEY=secret_****************
NOTION_DATABASE_ID=****************  
OPENROUTER_API_KEY=sk-or-v1-****************
```

### 第二步：添加模板库支持（重要）
```
NOTION_TEMPLATE_DATABASE_ID=your_template_db_id
AUTO_SYNC_TEMPLATES=true
```

### 第三步：启用智能知识系统（推荐）
```
NOTION_KNOWLEDGE_DATABASE_ID=your_knowledge_db_id
NOTION_CATEGORY_DATABASE_ID=your_category_db_id
ENABLE_NEW_KNOWLEDGE_SYSTEM=true
```

### 第四步：混合架构配置（可选）
如果您有本地RAG服务：
```
LOCAL_RAG_SERVICE_URL=http://your-local-ip:8001
ENABLE_RAG_FALLBACK=true
```

## 🎯 快速诊断步骤

### 1. 健康检查
访问：`https://your-app.zeabur.app/health`
预期响应：`{"status": "healthy"}`

### 2. 系统状态检查  
访问：`https://your-app.zeabur.app/status`
检查：
- 调度器状态
- 模板库状态
- RAG服务状态（如果配置）

### 3. 启动调度器
POST请求：`https://your-app.zeabur.app/start`

### 4. 测试处理功能
POST请求：`https://your-app.zeabur.app/process-once`

## 🚨 常见问题解决

### 问题1：无法连接Notion
- 检查 NOTION_API_KEY 是否正确
- 确认API密钥权限包含目标数据库

### 问题2：模板功能异常
- 确认 NOTION_TEMPLATE_DATABASE_ID 已设置
- 检查模板库数据库权限

### 问题3：RAG功能不可用
- 如果不使用本地RAG，可忽略相关错误
- 如果使用，确认本地服务可从公网访问

## 📱 下一步行动

1. **补充环境变量**：按照上述清单补充缺失变量
2. **重新部署**：保存环境变量后重新部署
3. **功能测试**：使用API端点验证各项功能
4. **Notion测试**：在Notion数据库中添加测试条目 