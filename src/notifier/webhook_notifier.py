"""
Webhook 通知器
"""

import requests
import json
from loguru import logger


class WebhookNotifier:
    """Webhook 通知器"""
    
    def __init__(self, config):
        self.config = config
        self.url = config.get("notification.webhook.url")
        self.headers = config.get("notification.webhook.headers", {})
        
        if not self.url:
            logger.warning("Webhook URL 未配置")
    
    def send(self, repo_name: str, report: str):
        """发送 Webhook 通知
        
        Args:
            repo_name: 仓库名称
            report: 报告内容
        """
        if not self.url:
            logger.warning("Webhook URL 未配置，跳过发送")
            return
        
        try:
            # 构建 payload
            payload = {
                "repo_name": repo_name,
                "report": report,
                "timestamp": self._get_timestamp()
            }
            
            # 发送请求
            response = requests.post(
                self.url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            logger.info(f"Webhook 发送成功: {repo_name}")
            
        except Exception as e:
            logger.error(f"Webhook 发送失败: {e}")
            raise
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
