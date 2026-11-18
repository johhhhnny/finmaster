# FinMaster（价值投资大师工作站）Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统基础工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖并安装
COPY requirements-lock.txt .
RUN pip install --no-cache-dir -r requirements-lock.txt

# 复制应用代码
COPY . .

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 健康检查
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 启动命令
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
