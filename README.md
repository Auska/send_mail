# send_email_cli.py

一个支持多收件人逐个发送的命令行邮件工具，基于 Python3 和 QQ 邮箱 SMTP 服务。

## 功能

- 通过命令行发送邮件
- 支持多个收件人（逐个发送）
- 支持纯文本和 HTML 格式正文
- 支持通过环境变量设置授权码

## 使用方法

```bash
# 发送普通文本邮件
python3 send_email_cli.py -t "recipient@example.com" -s "邮件主题" -m "邮件正文"

# 发送 Markdown 文件作为邮件正文
python3 send_email_cli.py -t "recipient@example.com" -s "邮件主题" --md "邮件内容.md"
```

### 参数说明

- `-t`, `--to`: 收件人邮箱，多个用英文逗号分隔
- `-s`, `--subject`: 邮件主题（默认：无主题）
- `-m`, `--message`: 纯文本正文内容（默认：这是一封测试邮件。）
- `--html`: HTML 格式正文内容（可选）
- `--md`: Markdown 格式正文文件路径（可选）
- `--from`: 发件人邮箱（默认：luodan0709@foxmail.com）
- `--auth`: 授权码（推荐通过环境变量 EMAIL_PASS 设置）

### 授权码设置

推荐通过环境变量 `EMAIL_PASS` 设置授权码，避免在命令行中暴露密码。

```bash
export EMAIL_PASS="your_email_password"
```