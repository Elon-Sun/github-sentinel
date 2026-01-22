"""
订阅管理命令模块
"""

import click
from rich.console import Console
from rich.table import Table
from loguru import logger

console = Console()


class SubscriptionCommands:
    """订阅管理命令集合"""
    
    def __init__(self, sentinel):
        """初始化订阅命令
        
        Args:
            sentinel: GitHubSentinel 实例
        """
        self.sentinel = sentinel
    
    def add_subscription(self, repo_name: str, tags: list = None):
        """添加仓库订阅
        
        Args:
            repo_name: 仓库名称 (owner/repo)
            tags: 标签列表
        """
        try:
            self.sentinel.subscription_manager.add_subscription(repo_name, tags or [])
            console.print(f"[green]✓[/green] 已添加订阅: {repo_name}")
            logger.info(f"添加订阅成功: {repo_name}")
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] 添加订阅失败: {e}")
            logger.error(f"添加订阅失败: {repo_name} - {e}")
            return False
    
    def remove_subscription(self, repo_name: str):
        """移除仓库订阅
        
        Args:
            repo_name: 仓库名称
        """
        try:
            self.sentinel.subscription_manager.remove_subscription(repo_name)
            console.print(f"[green]✓[/green] 已移除订阅: {repo_name}")
            logger.info(f"移除订阅成功: {repo_name}")
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] 移除订阅失败: {e}")
            logger.error(f"移除订阅失败: {repo_name} - {e}")
            return False
    
    def list_subscriptions(self):
        """列出所有订阅"""
        try:
            subscriptions = self.sentinel.subscription_manager.list_subscriptions()
            
            if not subscriptions:
                console.print("[yellow]没有订阅的仓库[/yellow]")
                return []
            
            table = Table(title="订阅列表")
            table.add_column("ID", style="cyan")
            table.add_column("仓库", style="magenta")
            table.add_column("标签", style="green")
            table.add_column("订阅时间", style="yellow")
            table.add_column("最后更新", style="blue")
            
            for sub in subscriptions:
                table.add_row(
                    str(sub['id']),
                    sub['repo_name'],
                    sub.get('tags', ''),
                    sub['created_at'],
                    sub.get('last_updated', 'Never')
                )
            console.print(table)
            return subscriptions
        except Exception as e:
            console.print(f"[red]✗[/red] 获取订阅列表失败: {e}")
            logger.error(f"获取订阅列表失败: {e}")
            return []
    
    def update_repository(self, repo_name: str = None):
        """更新仓库
        
        Args:
            repo_name: 仓库名称，如果为None则更新所有订阅
        """
        if repo_name:
            self.sentinel.update_single_repository(repo_name)
        else:
            self.sentinel.update_repositories()
    
    def check_repository(self, repo_name: str):
        """检查单个仓库（无论是否订阅）
        
        Args:
            repo_name: 仓库名称
        """
        try:
            self.sentinel.update_single_repository(repo_name)
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] 检查失败: {e}")
            logger.error(f"检查仓库失败: {repo_name} - {e}")
            return False


def create_subscription_cli_commands(sentinel):
    """创建订阅相关的 Click 命令
    
    Args:
        sentinel: GitHubSentinel 实例
    
    Returns:
        Click 命令组
    """
    commands = SubscriptionCommands(sentinel)
    
    @click.group()
    def subscribe():
        """管理仓库订阅"""
        pass
    
    @subscribe.command("add")
    @click.argument("repo_name")
    @click.option("--tags", "-t", help="标签（逗号分隔）", default="")
    def add(repo_name: str, tags: str):
        """添加仓库订阅"""
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        commands.add_subscription(repo_name, tag_list)
    
    @subscribe.command("remove")
    @click.argument("repo_name")
    def remove(repo_name: str):
        """移除仓库订阅"""
        commands.remove_subscription(repo_name)
    
    @subscribe.command("list")
    def list_cmd():
        """列出所有订阅"""
        commands.list_subscriptions()
    
    return subscribe
