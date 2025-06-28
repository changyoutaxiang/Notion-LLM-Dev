FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制云端主程序和调试工具（从 zeabur_deploy 目录）
COPY zeabur_deploy/cloud_main.py .
COPY zeabur_deploy/emergency_debug.py .
COPY zeabur_deploy/requirements_cloud.txt .

# 复制共享的核心文件（从根目录）
COPY notion_handler.py .
COPY llm_handler.py .
COPY template_manager.py .
COPY templates.json .

# 🧠 复制智能知识库系统文件 (v3.0新增)
COPY notion_knowledge_db.py .
COPY migrate_knowledge_to_notion.py .
COPY test_knowledge_connection.py .
COPY test_smart_search.py .
COPY debug_notion_fields.py .

# 复制知识库目录（从根目录）
COPY knowledge_base/ ./knowledge_base/

# 安装依赖
RUN pip install --no-cache-dir -r requirements_cloud.txt

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PORT=8080

# 启动应用
CMD ["python", "cloud_main.py"] 