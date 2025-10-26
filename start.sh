#!/bin/bash

# start.sh - 启动webhook服务的脚本

# 设置默认值
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-5000}
LOG_LEVEL=${LOG_LEVEL:-INFO}

# 构建命令行参数
CMD_ARGS="--host $HOST --port $PORT --log-level $LOG_LEVEL"

# 如果设置了API密钥，则添加到参数中
if [ -n "$API_KEY" ]; then
    CMD_ARGS="$CMD_ARGS --api-key $API_KEY"
fi

# 启动webhook服务
echo "Starting webhook server..."
echo "Host: $HOST"
echo "Port: $PORT"
echo "Log level: $LOG_LEVEL"
if [ -n "$API_KEY" ]; then
    echo "API key: set"
else
    echo "API key: not set"
fi

exec python webhook_server.py $CMD_ARGS