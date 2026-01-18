"""
订阅管理器
"""

from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import json

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
        
        # 检查是否已订阅
        existing = self.db.execute_query(
            "SELECT id FROM subscriptions WHERE repo_name = ?",
            (repo_name,)
        )
        
        if existing:
            raise ValueError(f"仓库已订阅: {repo_name}")
        
        # 添加订阅
        tags_str = ','.join(tags) if tags else ''
        subscription_id = self.db.execute_update(
            """
            INSERT INTO subscriptions (repo_name, tags, created_at)
            VALUES (?, ?, ?)
            """,
            (repo_name, tags_str, datetime.now().isoformat())
        )
        
        logger.info(f"添加订阅成功: {repo_name} (ID: {subscription_id})")
        return subscription_id
    
    def remove_subscription(self, repo_name: str):
        """移除仓库订阅"""
        result = self.db.execute_update(
            "DELETE FROM subscriptions WHERE repo_name = ?",
            (repo_name,)
        )
        
        if result > 0:
            logger.info(f"移除订阅成功: {repo_name}")
        else:
            raise ValueError(f"订阅不存在: {repo_name}")
    
    def list_subscriptions(self) -> List[Dict]:
        """列出所有订阅"""
        rows = self.db.execute_query(
            """
            SELECT id, repo_name, tags, created_at, last_updated
            FROM subscriptions
            ORDER BY created_at DESC
            """
        )
        
        subscriptions = []
        for row in rows:
            subscriptions.append({
                'id': row[0],
                'repo_name': row[1],
                'tags': row[2] or '',
                'created_at': row[3],
                'last_updated': row[4] or 'Never'
            })
        
        return subscriptions
    
    def get_subscription(self, repo_name: str) -> Optional[Dict]:
        """获取订阅信息"""
        rows = self.db.execute_query(
            "SELECT id, repo_name, tags, created_at, last_updated FROM subscriptions WHERE repo_name = ?",
            (repo_name,)
        )
        
        if not rows:
            return None
        
        row = rows[0]
        return {
            'id': row[0],
            'repo_name': row[1],
            'tags': row[2] or '',
            'created_at': row[3],
            'last_updated': row[4] or 'Never'
        }
    
    def save_update_record(self, subscription_id: int, updates: Dict):
        """保存更新记录
        
        Args:
            subscription_id: 订阅 ID
            updates: 更新数据
        """
        # 保存到更新记录表
        self.db.execute_update(
            """
            INSERT INTO update_records (subscription_id, update_data, created_at)
            VALUES (?, ?, ?)
            """,
            (subscription_id, json.dumps(updates, ensure_ascii=False), datetime.now().isoformat())
        )
        
        # 更新订阅的最后更新时间
        self.db.execute_update(
            "UPDATE subscriptions SET last_updated = ? WHERE id = ?",
            (datetime.now().isoformat(), subscription_id)
        )
        
        logger.info(f"保存更新记录成功: 订阅 ID {subscription_id}")
    
    def get_update_history(self, repo_name: str, limit: int = 10) -> List[Dict]:
        """获取更新历史
        
        Args:
            repo_name: 仓库名称
            limit: 返回记录数量
        
        Returns:
            更新历史列表
        """
        rows = self.db.execute_query(
            """
            SELECT ur.id, ur.update_data, ur.created_at
            FROM update_records ur
            JOIN subscriptions s ON ur.subscription_id = s.id
            WHERE s.repo_name = ?
            ORDER BY ur.created_at DESC
            LIMIT ?
            """,
            (repo_name, limit)
        )
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'update_data': json.loads(row[1]),
                'created_at': row[2]
            })
        
        return history
