"""
邮件通知器
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from loguru import logger


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self, config):
        self.config = config
        self.smtp_host = config.get("notification.email.smtp_host")
        self.smtp_port = config.get("notification.email.smtp_port", 587)
        self.username = config.get("notification.email.username")
        self.password = config.get("notification.email.password")
        self.from_addr = config.get("notification.email.from_addr")
        self.to_addrs = config.get("notification.email.to_addrs", [])
        
        if not self.smtp_host or not self.username or not self.password:
            logger.warning("邮件通知未完全配置")
    
    def send(self, subject: str, content: str, to_addrs: List[str] = None):
        """发送邮件
        
        Args:
            subject: 邮件主题
            content: 邮件内容（支持 Markdown/HTML）
            to_addrs: 收件人列表，如果为 None 则使用配置中的默认值
        """
        if not to_addrs:
            to_addrs = self.to_addrs
        
        if not to_addrs:
            logger.warning("没有配置收件人，跳过邮件发送")
            return
        
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(to_addrs)
            
            # 尝试将 Markdown 转换为 HTML
            html_content = self._markdown_to_html(content)
            
            # 添加纯文本和 HTML 版本
            part1 = MIMEText(content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"邮件发送成功: {subject} -> {', '.join(to_addrs)}")
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """将 Markdown 转换为 HTML
        
        简单的转换，可以根据需要使用 markdown 库进行更复杂的转换
        """
        try:
            import markdown
            html = markdown.markdown(
                markdown_text,
                extensions=['extra', 'codehilite', 'tables']
            )
            
            # 添加基本的 CSS 样式
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-family: 'Monaco', 'Courier New', monospace;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    a {{ color: #3498db; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    ul, ol {{ padding-left: 20px; }}
                    hr {{ border: none; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    {html}
                </div>
            </body>
            </html>
            """
            return styled_html
            
        except ImportError:
            # 如果没有安装 markdown 库，返回基本的 HTML
            html = markdown_text.replace('\n', '<br>')
            return f"<html><body><pre>{html}</pre></body></html>"
