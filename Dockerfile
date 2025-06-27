FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 只复制必需的文件
COPY cloud_main.py .
COPY notion_handler.py .
COPY llm_handler.py .
COPY template_manager.py .
COPY templates.json .
COPY requirements_cloud.txt .
COPY knowledge_base/ ./knowledge_base/

# 安装依赖
RUN pip install --no-cache-dir -r requirements_cloud.txt

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PORT=8080

# 启动应用
CMD ["python", "cloud_main.py"] 