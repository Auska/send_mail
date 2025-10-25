# send_mail

一个支持多收件人逐个发送的邮件工具集，包含命令行工具和Webhook服务，基于 Python3 和 QQ 邮箱 SMTP 服务。

## 功能特性

- 通过命令行发送邮件
- 通过Webhook服务发送邮件
- 支持多个收件人（逐个发送）
- 支持纯文本、HTML和Markdown格式正文
- 支持邮件附件
- 支持通过环境变量设置授权码
- 完整的日志记录功能

## 命令行工具使用方法

```bash
# 发送普通文本邮件
python3 send_email_cli.py -t "recipient@example.com" -s "邮件主题" -m "邮件正文"

# 发送 Markdown 文件作为邮件正文
python3 send_email_cli.py -t "recipient@example.com" -s "邮件主题" --md "邮件内容.md"

# 发送带附件的邮件
python3 send_email_cli.py -t "recipient@example.com" -s "邮件主题" -m "邮件正文" -f "file1.txt,file2.pdf"
```

### 命令行参数说明

- `-t`, `--to`: 收件人邮箱，多个用英文逗号分隔
- `-s`, `--subject`: 邮件主题（默认：无主题）
- `-m`, `--message`: 纯文本正文内容（默认：这是一封测试邮件。）
- `--html`: HTML 格式正文内容（可选）
- `--md`: Markdown 格式正文文件路径（可选）
- `--from`: 发件人邮箱（默认：luodan0709@foxmail.com）
- `--auth`: 授权码（推荐通过环境变量 EMAIL_PASS 设置）
- `-f`, `--files`: 附件文件路径，多个用英文逗号分隔

### 授权码设置

推荐通过环境变量 `EMAIL_PASS` 设置授权码，避免在命令行中暴露密码。

```bash
export EMAIL_PASS="your_email_password"
```

## Webhook服务

除了命令行工具，本项目还提供了一个基于Flask的Webhook服务，允许通过HTTP请求发送邮件。

### 启动Webhook服务

```bash
# 设置环境变量
export EMAIL_PASS=your_email_password  # 必需：邮箱授权码

# 安装依赖
pip install flask markdown

# 启动服务（默认配置）
python3 webhook_server.py
```

### Webhook API端点

#### 发送邮件 `/send_email`

- **方法**: POST
- **内容类型**: application/json

##### 请求参数

- `to` (必需): 收件人邮箱地址列表
- `subject` (可选): 邮件主题，默认为"无主题"
- `message` (可选): 纯文本正文内容，默认为"这是一封测试邮件。"
- `html` (可选): HTML格式正文内容
- `markdown_file` (可选): Markdown文件路径，将被转换为HTML
- `attachments` (可选): 附件文件路径列表

##### 请求示例

```bash
curl -X POST http://localhost:5000/send_email \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient1@example.com", "recipient2@example.com"],
    "subject": "测试邮件",
    "message": "这是一封测试邮件。",
    "html": "<h1>测试邮件</h1><p>这是一封测试邮件。</p>",
    "attachments": ["test_attachment.txt"]
  }'
```

#### 健康检查 `/health`

- **方法**: GET
- **用途**: 检查服务运行状态

##### 请求示例

```bash
curl http://localhost:5000/health
```

### Webhook服务配置

Webhook服务支持以下命令行参数：

```bash
python3 webhook_server.py --help
```

- `--log-level`: 设置日志等级 (默认: INFO)
- `--host`: 服务监听地址 (默认: 0.0.0.0)
- `--port`: 服务端口 (默认: 5000)
- `--api-key`: API密钥，用于验证客户端身份

### 安全注意事项

- 请确保通过HTTPS访问Webhook端点
- 妥善保管邮箱授权码，不要在代码中硬编码
- 考虑设置API密钥以增强安全性
- 详细的安全配置请参考 [WEBHOOK.md](WEBHOOK.md)