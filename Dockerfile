FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制zeabur_deploy目录下的所有文件
COPY zeabur_deploy/cloud_main.py .
COPY zeabur_deploy/notion_handler.py .
COPY zeabur_deploy/llm_handler.py .
COPY zeabur_deploy/template_manager.py .
COPY zeabur_deploy/templates.json .
COPY zeabur_deploy/requirements_cloud.txt .
COPY zeabur_deploy/emergency_debug.py .

# 复制真实的knowledge_base目录及其内容
COPY zeabur_deploy/knowledge_base/ ./knowledge_base/

# 安装依赖
RUN pip install --no-cache-dir -r requirements_cloud.txt

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV PORT=8080

# 启动应用
CMD ["python", "cloud_main.py"] 