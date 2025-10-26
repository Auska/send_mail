#!/usr/bin/env python3
# webhook_server.py - Webhook接收端，用于接收邮件发送请求

from flask import Flask, request, jsonify
import os
import sys
import logging
import argparse
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
import smtplib
import markdown

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Webhook服务，用于接收邮件发送请求")
    parser.add_argument('--log-level', default=os.getenv('LOG_LEVEL', 'INFO'), choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='设置日志等级 (默认: INFO)')
    parser.add_argument('--host', default=os.getenv('HOST', '0.0.0.0'), help='服务监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=int(os.getenv('PORT', '5000')), help='服务端口 (默认: 5000)')
    parser.add_argument('--api-key', default=os.getenv('API_KEY'), help='API密钥，用于验证客户端身份')
    return parser.parse_args()

# 解析命令行参数
args = parse_arguments()

# 设置日志等级
log_level = getattr(logging, args.log_level.upper(), logging.INFO)
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
DEFAULT_SENDER = os.getenv("EMAIL_SENDER", "luodan0709@foxmail.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

app = Flask(__name__)

# 全局变量存储命令行参数
global_args = args

# API密钥验证装饰器
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 如果没有设置API密钥，则跳过验证
        if not global_args.api_key:
            return f(*args, **kwargs)
        
        # 检查请求头中的API密钥
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == global_args.api_key:
            return f(*args, **kwargs)
        else:
            logger.warning(f"API key authentication failed, IP address: {request.remote_addr}")
            return jsonify({"error": "Unauthorized: Invalid or missing API key"}), 401
    return decorated_function

def send_email(sender, password, recipient, subject, text_body, html_body=None):
    """
    发送单封邮件给一个收件人
    :param recipient: 单个收件人邮箱字符串
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

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(0)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        logger.info(f"邮件已发送给：{recipient}")
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error(f"认证失败：检查邮箱 '{sender}' 和授权码")
        return False
    except smtplib.SMTPConnectError:
        logger.error("连接失败：无法连接到 SMTP 服务器")
        return False
    except Exception as e:
        logger.error(f"发送失败给 {recipient}：{str(e)}")
        return False

@app.route('/send_email', methods=['POST'])
@require_api_key
def send_email_webhook():
    """
    Webhook端点，接收JSON格式的邮件发送请求
    """
    # 访问全局参数
    global global_args
    
    try:
        # 记录请求信息
        logger.info(f"收到邮件发送请求，IP地址：{request.remote_addr}")
        logger.info(f"请求头：{dict(request.headers)}")
        
        # 获取JSON数据
        data = request.get_json()
        
        # 记录请求数据（敏感信息已过滤）
        if data:
            filtered_data = data.copy()
            if 'password' in filtered_data:
                filtered_data['password'] = '***'
            logger.info(f"请求数据：{filtered_data}")
        else:
            logger.warning("请求体中没有JSON数据")
        
        # 检查必需字段
        if not data:
            logger.warning("请求中缺少JSON数据")
            logger.warning("Request missing JSON data")
            return jsonify({"error": "Missing JSON data"}), 400
            
        # 从环境变量获取授权码
        password = os.getenv("EMAIL_PASS")
        if not password:
            logger.error("未设置EMAIL_PASS环境变量")
            logger.error("EMAIL_PASS environment variable not set")
            return jsonify({"error": "Server not configured correctly: EMAIL_PASS environment variable missing"}), 500
            
        # 解析请求数据
        recipients = data.get('to', [])
        subject = data.get('subject', '无主题')
        text_body = data.get('message', '这是一封测试邮件。')
        html_body = data.get('html')
        markdown_file = data.get('markdown_file')
        
        # 记录将要执行的操作
        logger.info(f"准备发送邮件：收件人数量={len(recipients)}, 主题='{subject}'")
        
        # 处理Markdown文件
        if markdown_file:
            if os.path.isfile(markdown_file):
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                    html_body = markdown.markdown(md_content)
                    # 如果没有提供纯文本内容，则使用 Markdown 内容作为纯文本
                    if not text_body or text_body == '这是一封测试邮件。':
                        text_body = md_content
                logger.info(f"Markdown文件已处理：{markdown_file}")
            else:
                logger.warning(f"Markdown 文件不存在：{markdown_file}")
        
        # 检查收件人
        if not recipients or not isinstance(recipients, list):
            logger.warning(f"收件人列表格式不正确：{type(recipients)}, 值：{recipients}")
            logger.warning(f"Recipient list is empty or incorrectly formatted: {type(recipients)}, value: {recipients}")
            return jsonify({"error": "Recipient list is empty or incorrectly formatted"}), 400
            
        # 发送邮件
        success_count = 0
        for recipient in recipients:
            logger.info(f"正在发送邮件给：{recipient}")
            if send_email(
                sender=DEFAULT_SENDER,
                password=password,
                recipient=recipient,
                subject=subject,
                text_body=text_body,
                html_body=html_body
            ):
                success_count += 1
                logger.info(f"成功发送邮件给：{recipient}")
            else:
                logger.error(f"发送邮件失败给：{recipient}")
                
        # 记录发送结果
        logger.info(f"邮件发送完成：成功={success_count}, 总数={len(recipients)}")
        
        # 返回结果
        return jsonify({
            "message": f"Email(s) sent successfully! Successfully sent {success_count}/{len(recipients)} email(s).",
            "success_count": success_count,
            "total_count": len(recipients)
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook request: {str(e)}")
        logger.exception("Detailed error information:")  # 记录完整的异常堆栈
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
@require_api_key
def health_check():
    """
    健康检查端点
    """
    # 访问全局参数
    global global_args
    
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    # 启动服务
    app.run(host=args.host, port=args.port, debug=False)