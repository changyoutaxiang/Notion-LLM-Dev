FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

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

# 🧠 复制RAG智能检索系统文件 (v3.0)
COPY notion_knowledge_db.py .
COPY semantic_search.py .
COPY hybrid_retrieval.py .
COPY migrate_knowledge_to_notion.py .
COPY test_knowledge_connection.py .
COPY test_smart_search.py .
COPY debug_notion_fields.py .

# 复制RAG系统依赖文件
COPY requirements_rag.txt .

# 复制知识库目录（从根目录）
COPY knowledge_base/ ./knowledge_base/

# 安装Python依赖（包括RAG系统）
RUN pip install --no-cache-dir -r requirements_cloud.txt
RUN pip install --no-cache-dir -r requirements_rag.txt

# 🤖 创建模型缓存目录（模型将在首次启动时自动下载）
RUN mkdir -p /app/model_cache

# 创建必要的目录
RUN mkdir -p vector_cache logs cache

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PORT=8080
ENV ENABLE_RAG_SYSTEM=true
ENV RAG_MODE=hybrid
ENV MODEL_CACHE_DIR=/app/model_cache
ENV VECTOR_CACHE_DIR=/app/vector_cache

# 启动应用
CMD ["python", "cloud_main.py"] 