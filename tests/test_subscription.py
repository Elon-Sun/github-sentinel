"""
订阅管理测试
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.storage.database import Database
from src.core.subscription_manager import SubscriptionManager
from src.core.github_client import GitHubClient


@pytest.fixture
def mock_db():
    """模拟数据库"""
    db = Mock(spec=Database)
    return db


@pytest.fixture
def mock_github_client():
    """模拟 GitHub 客户端"""
    client = Mock(spec=GitHubClient)
    client.validate_repository = Mock(return_value=True)
    return client


@pytest.fixture
def subscription_manager(mock_db, mock_github_client):
    """创建订阅管理器实例"""
    return SubscriptionManager(mock_db, mock_github_client)


def test_add_subscription_success(subscription_manager, mock_db, mock_github_client):
    """测试成功添加订阅"""
    # 设置模拟返回值
    mock_db.add_subscription.return_value = 1  # 插入成功
    
    # 执行测试
    result = subscription_manager.add_subscription("python/cpython", ["python", "core"])
    
    # 验证
    assert result == 1
    mock_github_client.validate_repository.assert_called_once_with("python/cpython")
    mock_db.add_subscription.assert_called_once()


def test_add_subscription_already_exists(subscription_manager, mock_db, mock_github_client):
    """测试添加已存在的订阅"""
    # 设置模拟返回值 - add_subscription 抛出 ValueError
    mock_db.add_subscription.side_effect = ValueError("仓库已订阅: python/cpython")
    
    # 执行测试并验证异常
    with pytest.raises(ValueError, match="仓库已订阅"):
        subscription_manager.add_subscription("python/cpython")


def test_add_subscription_invalid_repo(subscription_manager, mock_github_client):
    """测试添加无效仓库"""
    # 设置模拟返回值
    mock_github_client.validate_repository.return_value = False
    
    # 执行测试并验证异常
    with pytest.raises(ValueError, match="仓库不存在或无法访问"):
        subscription_manager.add_subscription("invalid/repo")


def test_remove_subscription_success(subscription_manager, mock_db):
    """测试成功移除订阅"""
    # 设置模拟返回值
    mock_db.remove_subscription.return_value = 1  # 删除成功
    
    # 执行测试
    subscription_manager.remove_subscription("python/cpython")
    
    # 验证
    mock_db.remove_subscription.assert_called_once()


def test_remove_subscription_not_exists(subscription_manager, mock_db):
    """测试移除不存在的订阅"""
    # 设置模拟返回值
    mock_db.remove_subscription.return_value = 0  # 没有删除任何记录
    
    # 执行测试并验证异常
    with pytest.raises(ValueError, match="订阅不存在"):
        subscription_manager.remove_subscription("python/cpython")


def test_list_subscriptions(subscription_manager, mock_db):
    """测试列出订阅"""
    # 设置模拟返回值
    mock_db.get_subscriptions.return_value = [
        {'id': 1, 'repo_name': "python/cpython", 'tags': "python,core", 'created_at': "2024-01-01", 'last_updated': "2024-01-02"},
        {'id': 2, 'repo_name': "django/django", 'tags': "python,web", 'created_at': "2024-01-01", 'last_updated': None}
    ]
    
    # 执行测试
    result = subscription_manager.list_subscriptions()
    
    # 验证
    assert len(result) == 2
    assert result[0]['repo_name'] == "python/cpython"
    assert result[1]['repo_name'] == "django/django"
    assert result[1]['last_updated'] == "Never"


def test_get_subscription(subscription_manager, mock_db):
    """测试获取订阅"""
    # 设置模拟返回值
    mock_db.get_subscription_by_name.return_value = {
        'id': 1,
        'repo_name': "python/cpython",
        'tags': "python,core",
        'created_at': "2024-01-01",
        'last_updated': "2024-01-02"
    }
    
    # 执行测试
    result = subscription_manager.get_subscription("python/cpython")
    
    # 验证
    assert result is not None
    assert result['repo_name'] == "python/cpython"
    assert result['tags'] == "python,core"


def test_save_update_record(subscription_manager, mock_db):
    """测试保存更新记录"""
    updates = {
        'commits': [],
        'pull_requests': [],
        'issues': []
    }
    
    # 执行测试
    subscription_manager.save_update_record(1, updates)
    
    # 验证调用了 add_update_record 和 update_subscription_last_updated
    mock_db.add_update_record.assert_called_once_with(1, updates)
    mock_db.update_subscription_last_updated.assert_called_once_with(1)
