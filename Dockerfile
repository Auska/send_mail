FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制requirements.txt并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY webhook_server.py ./
COPY start.sh ./
RUN chmod +x start.sh

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["./start.sh"]
