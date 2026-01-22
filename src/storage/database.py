"""
数据存储管理（JSON 文件）
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger


class Database:
    """JSON 文件数据存储"""
    
    def __init__(self, db_path: str = "data/sentinel.json"):
        self.db_path = Path(db_path)
        self._ensure_directory()
        self.data = self._load_data()
        logger.info(f"数据存储初始化成功: {self.db_path}")
    
    def _ensure_directory(self):
        """确保数据目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self) -> Dict:
        """从 JSON 文件加载数据"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载数据文件失败: {e}，创建新文件")
                return self._init_data_structure()
        else:
            return self._init_data_structure()
    
    def _init_data_structure(self) -> Dict:
        """初始化数据结构"""
        return {
            'subscriptions': [],
            'update_records': [],
            'settings': {},
            'next_subscription_id': 1,
            'next_record_id': 1
        }
    
    def _save_data(self):
        """保存数据到 JSON 文件"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise
    
    def add_subscription(self, repo_name: str, tags: str = '') -> int:
        """添加订阅"""
        # 检查是否已存在
        for sub in self.data['subscriptions']:
            if sub['repo_name'] == repo_name:
                raise ValueError(f"仓库已订阅: {repo_name}")
        
        subscription_id = self.data['next_subscription_id']
        self.data['next_subscription_id'] += 1
        
        subscription = {
            'id': subscription_id,
            'repo_name': repo_name,
            'tags': tags,
            'created_at': datetime.now().isoformat(),
            'last_updated': None
        }
        
        self.data['subscriptions'].append(subscription)
        self._save_data()
        
        logger.info(f"添加订阅成功: {repo_name} (ID: {subscription_id})")
        return subscription_id
    
    def remove_subscription(self, repo_name: str) -> int:
        """移除订阅"""
        original_length = len(self.data['subscriptions'])
        
        # 找到订阅 ID
        subscription_id = None
        for sub in self.data['subscriptions']:
            if sub['repo_name'] == repo_name:
                subscription_id = sub['id']
                break
        
        # 移除订阅
        self.data['subscriptions'] = [
            sub for sub in self.data['subscriptions'] 
            if sub['repo_name'] != repo_name
        ]
        
        # 移除相关的更新记录
        if subscription_id:
            self.data['update_records'] = [
                record for record in self.data['update_records']
                if record['subscription_id'] != subscription_id
            ]
        
        affected = original_length - len(self.data['subscriptions'])
        if affected > 0:
            self._save_data()
            logger.info(f"移除订阅成功: {repo_name}")
        
        return affected
    
    def get_subscriptions(self) -> List[Dict]:
        """获取所有订阅"""
        return self.data['subscriptions']
    
    def get_subscription_by_name(self, repo_name: str) -> Optional[Dict]:
        """根据仓库名获取订阅"""
        for sub in self.data['subscriptions']:
            if sub['repo_name'] == repo_name:
                return sub
        return None
    
    def update_subscription_last_updated(self, subscription_id: int):
        """更新订阅的最后更新时间"""
        for sub in self.data['subscriptions']:
            if sub['id'] == subscription_id:
                sub['last_updated'] = datetime.now().isoformat()
                self._save_data()
                break
    
    def add_update_record(self, subscription_id: int, update_data: Dict) -> int:
        """添加更新记录"""
        record_id = self.data['next_record_id']
        self.data['next_record_id'] += 1
        
        record = {
            'id': record_id,
            'subscription_id': subscription_id,
            'update_data': update_data,
            'created_at': datetime.now().isoformat()
        }
        
        self.data['update_records'].append(record)
        self._save_data()
        
        logger.info(f"添加更新记录成功: 记录 ID {record_id}")
        return record_id
    
    def get_update_records(self, subscription_id: int, limit: int = 10) -> List[Dict]:
        """获取订阅的更新记录"""
        records = [
            record for record in self.data['update_records']
            if record['subscription_id'] == subscription_id
        ]
        
        # 按创建时间倒序排序
        records.sort(key=lambda x: x['created_at'], reverse=True)
        
        return records[:limit]
    
    def get_setting(self, key: str, default: Any = None) -> Optional[str]:
        """获取配置值"""
        return self.data['settings'].get(key, default)
    
    def set_setting(self, key: str, value: str):
        """设置配置值"""
        self.data['settings'][key] = {
            'value': value,
            'updated_at': datetime.now().isoformat()
        }
        self._save_data()
    
    def close(self):
        """关闭数据存储（JSON 不需要关闭连接）"""
        logger.info("数据存储已关闭")
    
    def __del__(self):
        """析构函数"""
        pass
