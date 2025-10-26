# Webhook服务使用说明

## 功能特性

- 通过HTTP请求发送邮件
- 支持多收件人（逐个发送）
- 支持纯文本、HTML和Markdown格式邮件内容

- 完整的请求日志记录
- 健康检查端点

## 启动服务

```bash
# 设置环境变量
export EMAIL_PASS=your_email_password  # 必需：邮箱授权码
export EMAIL_SENDER=your_email@example.com  # 可选：发件人邮箱，默认为luodan0709@foxmail.com

# 安装依赖
pip install flask markdown

# 启动服务（默认配置）
python3 webhook_server.py
```

### 命令行参数

Webhook服务支持以下命令行参数：

```bash
python3 webhook_server.py --help
```

```
usage: webhook_server.py [-h]
                         [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [--host HOST] [--port PORT] [--api-key API_KEY]

Webhook服务，用于接收邮件发送请求

options:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        设置日志等级 (默认: INFO)
  --host HOST           服务监听地址 (默认: 0.0.0.0)
  --port PORT           服务端口 (默认: 5000)
  --api-key API_KEY     API密钥，用于验证客户端身份
```

### 使用示例

```bash
# 以DEBUG等级启动服务
python3 webhook_server.py --log-level DEBUG

# 在特定端口启动服务
python3 webhook_server.py --port 8080

# 在特定地址和端口启动服务
python3 webhook_server.py --host 127.0.0.1 --port 8080

# 设置API密钥
python3 webhook_server.py --api-key your_secret_api_key
```

### 环境变量说明

- `EMAIL_PASS`: 邮箱授权码（必需）
- `EMAIL_SENDER`: 发件人邮箱地址（可选，默认为luodan0709@foxmail.com）

## API端点

### 发送邮件 `/send_email`

- **方法**: POST
- **内容类型**: application/json

#### 参数说明

- `to` (必需): 收件人邮箱地址列表
- `subject` (可选): 邮件主题，默认为"无主题"
- `message` (可选): 纯文本正文内容，默认为"这是一封测试邮件。"
- `html` (可选): HTML格式正文内容
- `markdown_file` (可选): Markdown文件路径，将被转换为HTML
#### 请求示例

```bash
curl -X POST http://localhost:5000/send_email \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "to": ["recipient1@example.com", "recipient2@example.com"],
    "subject": "测试邮件",
    "message": "这是一封测试邮件。",
    "html": "<h1>测试邮件</h1><p>这是一封测试邮件。</p>"
  }'
```

#### Markdown文件发送示例

```bash
curl -X POST http://localhost:5000/send_email \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Markdown测试邮件",
    "markdown_file": "test_email.md"
  }'
```

#### 响应示例

成功响应：
```json
{
  "message": "Email(s) sent successfully! Successfully sent 2/2 email(s).",
  "success_count": 2,
  "total_count": 2
}
```

错误响应：
```json
{
  "error": "Recipient list is empty or incorrectly formatted"
}
```

### 健康检查 `/health`

- **方法**: GET
- **用途**: 检查服务运行状态

#### 请求示例

```bash
curl -H "X-API-Key: your_api_key" http://localhost:5000/health
```

#### 响应示例

```json
{
  "status": "healthy"
}
```

## 日志说明

Webhook服务会记录以下日志信息：

- 请求IP地址
- 请求头信息
- 请求数据（敏感信息已过滤）
- 邮件发送操作的详细步骤
- 发送结果统计
- 错误信息和异常堆栈

### 日志等级

可以通过`--log-level`参数设置日志等级：

- `DEBUG`: 最详细的日志信息，用于调试
- `INFO`: 一般信息，默认等级
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误信息

使用示例：
```bash
# 以DEBUG等级启动服务，输出详细日志
python3 webhook_server.py --log-level DEBUG
```

## 错误处理

常见错误类型：
- 400: 请求格式错误（缺少必需字段、数据类型不正确等）
- 401: 认证失败（邮箱或授权码错误）
- 500: 服务器内部错误

## Docker部署

本项目支持通过Docker容器化部署，提供了Dockerfile和docker-compose.yml文件。

### 使用Docker直接构建

```bash
# 构建镜像
docker build -t send-mail-webhook .

# 运行容器
docker run -d \
  --name send-mail-webhook \
  -p 5000:5000 \
  -e EMAIL_PASS=your_email_password \
  -e API_KEY=your_api_key \
  send-mail-webhook
```

### 使用Docker Compose部署（推荐）

```bash
# 设置环境变量
export EMAIL_PASS=your_email_password
export API_KEY=your_api_key

# 启动服务
docker-compose up -d
```

### 环境变量说明

Docker容器支持以下环境变量：

- `EMAIL_PASS`: 邮箱授权码（必需）
- `EMAIL_SENDER`: 发件人邮箱地址（可选，默认为luodan0709@foxmail.com）
- `SMTP_SERVER`: SMTP服务器地址（可选，默认为smtp.qq.com）
- `SMTP_PORT`: SMTP服务器端口（可选，默认为587）
- `LOG_LEVEL`: 日志等级（可选，默认为INFO）
- `API_KEY`: API密钥，用于验证客户端身份（可选）
- `HOST`: 服务监听地址（可选，默认为0.0.0.0）
- `PORT`: 服务端口（可选，默认为5000）

## 安全注意事项

- 请确保通过HTTPS访问Webhook端点
- 合理限制请求频率，防止滥用
- 妥善保管邮箱授权码，不要在代码中硬编码
- 妥善保管API密钥，避免泄露
- 考虑添加IP白名单或请求认证机制