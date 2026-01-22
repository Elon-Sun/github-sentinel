"""
订阅管理器
"""

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

from src.storage.database import Database
from src.core.github_client import GitHubClient


class SubscriptionManager:
    """订阅管理器"""
    
    def __init__(self, db: Database, github_client: GitHubClient):
        self.db = db
        self.github_client = github_client
    
    def add_subscription(self, repo_name: str, tags: List[str] = None) -> int:
        """添加仓库订阅
        
        Args:
            repo_name: 仓库名称，格式为 owner/repo
            tags: 标签列表
        
        Returns:
            订阅 ID
        """
        # 验证仓库是否存在
        if not self.github_client.validate_repository(repo_name):
            raise ValueError(f"仓库不存在或无法访问: {repo_name}")
        
        # 添加订阅
        tags_str = ','.join(tags) if tags else ''
        subscription_id = self.db.add_subscription(repo_name, tags_str)
        
        logger.info(f"添加订阅成功: {repo_name} (ID: {subscription_id})")
        return subscription_id
    
    def remove_subscription(self, repo_name: str):
        """移除仓库订阅"""
        result = self.db.remove_subscription(repo_name)
        
        if result > 0:
            logger.info(f"移除订阅成功: {repo_name}")
        else:
            raise ValueError(f"订阅不存在: {repo_name}")
    
    def list_subscriptions(self) -> List[Dict]:
        """列出所有订阅"""
        subscriptions = self.db.get_subscriptions()
        
        # 格式化输出
        result = []
        for sub in subscriptions:
            result.append({
                'id': sub['id'],
                'repo_name': sub['repo_name'],
                'tags': sub.get('tags', ''),
                'created_at': sub['created_at'],
                'last_updated': sub.get('last_updated') or 'Never'
            })
        
        # 按创建时间倒序排序
        result.sort(key=lambda x: x['created_at'], reverse=True)
        
        return result
    
    def get_subscription(self, repo_name: str) -> Optional[Dict]:
        """获取订阅信息"""
        sub = self.db.get_subscription_by_name(repo_name)
        
        if not sub:
            return None
        
        return {
            'id': sub['id'],
            'repo_name': sub['repo_name'],
            'tags': sub.get('tags', ''),
            'created_at': sub['created_at'],
            'last_updated': sub.get('last_updated') or 'Never'
        }
    
    def save_update_record(self, subscription_id: int, updates: Dict):
        """保存更新记录
        
        Args:
            subscription_id: 订阅 ID
            updates: 更新数据
        """
        # 保存更新记录
        self.db.add_update_record(subscription_id, updates)
        
        # 更新订阅的最后更新时间
        self.db.update_subscription_last_updated(subscription_id)
        
        logger.info(f"保存更新记录成功: 订阅 ID {subscription_id}")
    
    def get_update_history(self, repo_name: str, limit: int = 10) -> List[Dict]:
        """获取更新历史
        
        Args:
            repo_name: 仓库名称
            limit: 返回记录数量
        
        Returns:
            更新历史列表
        """
        # 获取订阅信息
        sub = self.db.get_subscription_by_name(repo_name)
        if not sub:
            return []
        
        # 获取更新记录
        records = self.db.get_update_records(sub['id'], limit)
        
        history = []
        for record in records:
            history.append({
                'id': record['id'],
                'update_data': record['update_data'],
                'created_at': record['created_at']
            })
        
        return history
