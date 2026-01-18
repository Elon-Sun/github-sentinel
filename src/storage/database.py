"""
数据库管理
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Any, Optional
from loguru import logger


class Database:
    """SQLite 数据库管理"""
    
    def __init__(self, db_path: str = "data/sentinel.db"):
        self.db_path = Path(db_path)
        self._ensure_directory()
        self.connection = None
        self._init_database()
    
    def _ensure_directory(self):
        """确保数据库目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def _init_database(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 创建订阅表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL UNIQUE,
                tags TEXT,
                created_at TEXT NOT NULL,
                last_updated TEXT
            )
        """)
        
        # 创建更新记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS update_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_id INTEGER NOT NULL,
                update_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
            )
        """)
        
        # 创建配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_subscriptions_repo_name 
            ON subscriptions(repo_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_update_records_subscription_id 
            ON update_records(subscription_id)
        """)
        
        conn.commit()
        logger.info(f"数据库初始化成功: {self.db_path}")
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """执行查询语句
        
        Args:
            query: SQL 查询语句
            params: 查询参数
        
        Returns:
            查询结果列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            query: SQL 更新语句
            params: 更新参数
        
        Returns:
            受影响的行数或新插入的 ID
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            # 如果是 INSERT 操作，返回新插入的 ID
            if query.strip().upper().startswith('INSERT'):
                return cursor.lastrowid
            else:
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"更新执行失败: {e}")
            conn.rollback()
            raise
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """批量执行更新语句
        
        Args:
            query: SQL 更新语句
            params_list: 参数列表
        
        Returns:
            受影响的行数
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logger.error(f"批量更新执行失败: {e}")
            conn.rollback()
            raise
    
    def get_setting(self, key: str, default: Any = None) -> Optional[str]:
        """获取配置值"""
        results = self.execute_query(
            "SELECT value FROM settings WHERE key = ?",
            (key,)
        )
        
        if results:
            return results[0][0]
        return default
    
    def set_setting(self, key: str, value: str):
        """设置配置值"""
        from datetime import datetime
        
        # 先尝试更新
        updated = self.execute_update(
            "UPDATE settings SET value = ?, updated_at = ? WHERE key = ?",
            (value, datetime.now().isoformat(), key)
        )
        
        # 如果没有更新任何行，则插入新记录
        if updated == 0:
            self.execute_update(
                "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, datetime.now().isoformat())
            )
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("数据库连接已关闭")
    
    def __del__(self):
        """析构函数，确保连接关闭"""
        self.close()
