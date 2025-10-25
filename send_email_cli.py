#!/usr/bin/env python3
# send_email_cli.py - 支持多收件人【逐个发送】的邮件工具

import smtplib
import getpass
import argparse
import os
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders

# 默认发件人配置
DEFAULT_SENDER = "luodan0709@foxmail.com"  # ← 修改为你的邮箱
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587


def send_email(sender, password, recipient, subject, text_body, html_body=None, attachments=None):
    """
    发送单封邮件给一个收件人
    :param recipient: 单个收件人邮箱字符串
    :param attachments: 附件文件路径列表
    """
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = Header(subject, 'utf-8')

    # 添加正文
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # 添加附件
    if attachments:
        for file_path in attachments:
            if os.path.isfile(file_path):
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )
                msg.attach(part)
            else:
                print(f"⚠️  警告：附件文件不存在：{file_path}")

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(0)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        print(f"✅ 邮件已发送给：{recipient}")
    except smtplib.SMTPAuthenticationError:
        print(f"❌ 认证失败：检查邮箱 '{sender}' 和授权码")
        exit(1)
    except smtplib.SMTPConnectError:
        print("❌ 连接失败：无法连接到 SMTP 服务器")
        exit(1)
    except Exception as e:
        print(f"❌ 发送失败给 {recipient}：{str(e)}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="通过 QQ 邮箱发送邮件（逐个发送，支持多收件人）")

    parser.add_argument('-t', '--to', required=True,
                        help='收件人邮箱，多个用英文逗号分隔，例如：a@x.com,b@y.com')

    parser.add_argument('-s', '--subject', default='无主题',
                        help='邮件主题（默认：无主题）')

    parser.add_argument('-m', '--message', default='这是一封测试邮件。',
                        help='纯文本正文内容（默认：测试文本）')

    parser.add_argument('--html', help='HTML 格式正文内容（可选）')
    
    parser.add_argument('--md', help='Markdown 格式正文文件路径（可选）')

    parser.add_argument('--from', dest='sender', default=DEFAULT_SENDER,
                        help=f'发件人邮箱（默认：{DEFAULT_SENDER}）')

    parser.add_argument('--auth', help='授权码（推荐通过环境变量 EMAIL_PASS 设置）')

    parser.add_argument('-f', '--files', dest='files',
                        help='附件文件路径，多个用英文逗号分隔，例如：file1.txt,file2.pdf')

    args = parser.parse_args()

    # 解析收件人列表
    recipients = [addr.strip() for addr in args.to.split(',') if addr.strip()]
    if not recipients:
        print("❌ 错误：收件人列表为空，请检查输入。")
        exit(1)

    # 获取授权码：优先环境变量 → 参数 → 交互输入
    password = (
        os.getenv("EMAIL_PASS") or
        args.auth or
        getpass.getpass(f"🔐 请输入邮箱 '{args.sender}' 的授权码: ")
    )

    # 解析附件列表
    attachments = []
    if args.files:
        attachments = [path.strip() for path in args.files.split(',') if path.strip()]

    # 处理 Markdown 文件
    html_body = args.html
    text_body = args.message
    
    if args.md:
        if os.path.isfile(args.md):
            with open(args.md, 'r', encoding='utf-8') as f:
                md_content = f.read()
                html_body = markdown.markdown(md_content)
                # 如果没有提供纯文本内容，则使用 Markdown 内容作为纯文本
                if not args.message or args.message == '这是一封测试邮件。':
                    text_body = md_content
        else:
            print(f"❌ 错误：Markdown 文件不存在：{args.md}")
            exit(1)

    if not password:
        print("❌ 错误：未提供授权码，无法发送邮件。")
        exit(1)

    # 🔁 循环发送：每个收件人单独发送
    success_count = 0
    for recipient in recipients:
        if send_email(
            sender=args.sender,
            password=password,
            recipient=recipient,
            subject=args.subject,
            text_body=text_body,
            html_body=html_body,
            attachments=attachments
        ):
            success_count += 1

    # 最终统计
    print(f"\n📬 发送完成！成功发送 {success_count}/{len(recipients)} 封邮件。")


if __name__ == "__main__":
    main()
