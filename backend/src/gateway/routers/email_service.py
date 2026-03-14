"""邮件服务模块"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# 邮件配置
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@example.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "MagicFlow")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.host = SMTP_HOST
        self.port = SMTP_PORT
        self.user = SMTP_USER
        self.password = SMTP_PASSWORD
        self.from_email = SMTP_FROM_EMAIL
        self.from_name = SMTP_FROM_NAME
    
    def _create_connection(self) -> Optional[smtplib.SMTP]:
        """创建 SMTP 连接"""
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            return server
        except Exception as e:
            print(f"SMTP connection error: {e}")
            return None
    
    def send_password_reset_email(self, to_email: str, token: str, user_name: Optional[str] = None) -> bool:
        """发送密码重置邮件"""
        reset_url = f"{FRONTEND_URL}/auth/reset-password?token={token}"
        
        subject = "密码重置 - MagicFlow"
        
        # HTML 邮件内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>MagicFlow</h1>
                </div>
                <div class="content">
                    <h2>重置您的密码</h2>
                    <p>您好{f", {user_name}" if user_name else ""}，</p>
                    <p>我们收到了重置您账户密码的请求。请点击下面的按钮来设置新密码：</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">重置密码</a>
                    </p>
                    <p>或者，您可以将以下链接复制到浏览器地址栏：</p>
                    <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 5px;">
                        {reset_url}
                    </p>
                    <div class="warning">
                        <p><strong>⚠️ 安全提示：</strong></p>
                        <ul>
                            <li>此链接将在 <strong>15 分钟</strong> 后失效</li>
                            <li>如果您没有请求重置密码，请忽略此邮件</li>
                            <li>请勿将此链接分享给他人</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复。</p>
                    <p>&copy; {2026} MagicFlow. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 纯文本邮件内容
        text_content = f"""
        密码重置 - MagicFlow
        
        您好{f", {user_name}" if user_name else ""}，
        
        我们收到了重置您账户密码的请求。请点击以下链接来设置新密码：
        
        {reset_url}
        
        此链接将在 15 分钟后失效。
        如果您没有请求重置密码，请忽略此邮件。
        
        此邮件由系统自动发送，请勿回复。
        """
        
        return self._send_email(to_email, subject, html_content, text_content)
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """发送邮件"""
        if not self.user or not self.password:
            print("SMTP credentials not configured. Email would have been sent to:", to_email)
            print("Reset link:", subject)
            return True  # 开发模式下返回成功
        
        server = self._create_connection()
        if not server:
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            # 添加纯文本和 HTML 内容
            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            msg.attach(part1)
            msg.attach(part2)
            
            server.sendmail(self.from_email, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
        finally:
            server.quit()


# 全局邮件服务实例
email_service = EmailService()


def send_password_reset_email(to_email: str, token: str, user_name: Optional[str] = None) -> bool:
    """发送密码重置邮件的便捷函数"""
    return email_service.send_password_reset_email(to_email, token, user_name)
