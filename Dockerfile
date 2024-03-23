# 使用官方 Python 3.11 基于 x86 架构的镜像作为基础
FROM python:3.11-slim-buster

# 设置工作目录为 /app
WORKDIR /app

# 将 yt_dlp_server.py、start.sh 和 requirements.txt 复制到工作目录
COPY yt_dlp_server.py .
COPY start.sh .
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置默认环境变量
ENV HOST=0.0.0.0
ENV DIR=/downloads
ENV PORT=7777

# 设置启动脚本为 entrypoint
ENTRYPOINT ["./start.sh"]
