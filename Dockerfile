FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制必需的文件
COPY cloud_main.py .
COPY notion_handler.py .
COPY llm_handler.py .
COPY template_manager.py .
COPY templates.json .
COPY requirements_cloud.txt .

# 创建knowledge_base目录并添加说明文件
RUN mkdir -p knowledge_base
RUN echo "# 知识库目录\n此目录用于存放知识库文件(.md格式)\n\n在本地使用时，可以在此目录下添加你的知识库文件。" > knowledge_base/README.md

# 安装依赖
RUN pip install --no-cache-dir -r requirements_cloud.txt

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PORT=8080

# 启动应用
CMD ["python", "cloud_main.py"] 