# 使用官方 Python 3.11 基于 x86 架构的镜像作为基础
FROM python:3.11-slim-buster

# 设置工作目录为 /app
WORKDIR /app

# 将 yt_dlp_server.py、start.sh 和 requirements.txt 复制到工作目录
COPY yt_dlp_server.py .
COPY start.sh .
COPY requirements.txt .

# 设置start.sh执行权限
RUN chmod +x start.sh

# 更新包列表并安装 nano
RUN apt-get update && \
    apt-get install -y nano && \
    # 清理缓存，减小镜像体积
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置默认环境变量
ENV HOST=0.0.0.0
ENV DIR=/downloads
ENV PORT=7777

# 设置启动脚本为 entrypoint
ENTRYPOINT ["./start.sh"]
