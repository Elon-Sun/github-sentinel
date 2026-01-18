"""
主入口文件 - 命令行接口
"""

import click
from rich.console import Console
from rich.table import Table
from loguru import logger
import sys
from pathlib import Path

from src.core.subscription_manager import SubscriptionManager
from src.core.github_client import GitHubClient
from src.core.scheduler import Scheduler
from src.ai.report_generator import ReportGenerator
from src.storage.database import Database
from src.config_loader import ConfigLoader

console = Console()


class GitHubSentinel:
    """GitHub Sentinel 主类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = ConfigLoader(config_path)
        self.db = Database(self.config.get("database.path", "data/sentinel.db"))
        self.github_client = GitHubClient(self.config.get("github.token"))
        self.subscription_manager = SubscriptionManager(self.db, self.github_client)
        self.report_generator = ReportGenerator(self.config)
        self.scheduler = Scheduler(self.config, self)
        
        # 配置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志系统"""
        log_level = self.config.get("logging.level", "INFO")
        log_file = self.config.get("logging.file", "logs/sentinel.log")
        
        # 创建日志目录
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 配置 loguru
        logger.remove()  # 移除默认处理器
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        )
        logger.add(
            log_file,
            rotation="10 MB",
            retention="10 days",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
        )
    
    def update_repositories(self):
        """更新所有订阅的仓库"""
        logger.info("开始更新所有订阅的仓库...")
        subscriptions = self.subscription_manager.list_subscriptions()
        
        if not subscriptions:
            console.print("[yellow]没有订阅的仓库[/yellow]")
            return
        
        for sub in subscriptions:
            try:
                logger.info(f"正在更新仓库: {sub['repo_name']}")
                updates = self.github_client.fetch_repository_updates(
                    sub['repo_name'],
                    days=self.config.get("report.max_days", 7)
                )
                
                # 生成报告
                report = self.report_generator.generate_report(sub['repo_name'], updates)
                
                # 保存更新记录
                self.subscription_manager.save_update_record(sub['id'], updates)
                
                # 发送通知
                self._send_notification(sub['repo_name'], report)
                
                console.print(f"[green]✓[/green] 已更新: {sub['repo_name']}")
                
            except Exception as e:
                logger.error(f"更新仓库 {sub['repo_name']} 失败: {e}")
                console.print(f"[red]✗[/red] 更新失败: {sub['repo_name']}")
    
    def _send_notification(self, repo_name: str, report: str):
        """发送通知"""
        # 邮件通知
        if self.config.get("notification.email.enabled"):
            from src.notifier.email_notifier import EmailNotifier
            email_notifier = EmailNotifier(self.config)
            email_notifier.send(
                subject=f"GitHub Sentinel - {repo_name} 更新报告",
                content=report
            )
        
        # Webhook 通知
        if self.config.get("notification.webhook.enabled"):
            from src.notifier.webhook_notifier import WebhookNotifier
            webhook_notifier = WebhookNotifier(self.config)
            webhook_notifier.send(repo_name, report)


@click.group()
@click.version_option(version="0.0.1")
def cli():
    """GitHub Sentinel - AI驱动的GitHub仓库监控工具"""
    pass


@cli.group()
def subscribe():
    """管理仓库订阅"""
    pass


@subscribe.command("add")
@click.argument("repo_name")
@click.option("--tags", "-t", help="标签（逗号分隔）", default="")
def subscribe_add(repo_name: str, tags: str):
    """添加仓库订阅
    
    示例: github-sentinel subscribe add python/cpython
    """
    try:
        sentinel = GitHubSentinel()
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        sentinel.subscription_manager.add_subscription(repo_name, tag_list)
        console.print(f"[green]✓[/green] 已添加订阅: {repo_name}")
    except Exception as e:
        console.print(f"[red]✗[/red] 添加订阅失败: {e}")
        logger.error(f"添加订阅失败: {e}")


@subscribe.command("remove")
@click.argument("repo_name")
def subscribe_remove(repo_name: str):
    """移除仓库订阅"""
    try:
        sentinel = GitHubSentinel()
        sentinel.subscription_manager.remove_subscription(repo_name)
        console.print(f"[green]✓[/green] 已移除订阅: {repo_name}")
    except Exception as e:
        console.print(f"[red]✗[/red] 移除订阅失败: {e}")
        logger.error(f"移除订阅失败: {e}")


@subscribe.command("list")
def subscribe_list():
    """列出所有订阅"""
    try:
        sentinel = GitHubSentinel()
        subscriptions = sentinel.subscription_manager.list_subscriptions()
        
        if not subscriptions:
            console.print("[yellow]没有订阅的仓库[/yellow]")
            return
        
        table = Table(title="订阅列表")
        table.add_column("ID", style="cyan")
        table.add_column("仓库", style="magenta")
        table.add_column("标签", style="green")
        table.add_column("订阅时间", style="yellow")
        
        for sub in subscriptions:
            table.add_row(
                str(sub['id']),
                sub['repo_name'],
                sub.get('tags', ''),
                sub['created_at']
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗[/red] 获取订阅列表失败: {e}")
        logger.error(f"获取订阅列表失败: {e}")


@cli.command()
def update():
    """手动触发更新所有订阅的仓库"""
    try:
        sentinel = GitHubSentinel()
        sentinel.update_repositories()
    except Exception as e:
        console.print(f"[red]✗[/red] 更新失败: {e}")
        logger.error(f"更新失败: {e}")


@cli.command()
def start():
    """启动定时任务"""
    try:
        console.print("[green]GitHub Sentinel 已启动[/green]")
        console.print(f"调度间隔: {ConfigLoader().get('schedule.interval', 'daily')}")
        
        sentinel = GitHubSentinel()
        sentinel.scheduler.start()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]正在停止 GitHub Sentinel...[/yellow]")
    except Exception as e:
        console.print(f"[red]✗[/red] 启动失败: {e}")
        logger.error(f"启动失败: {e}")


@cli.command()
def init():
    """初始化配置和数据库"""
    try:
        # 创建必要的目录
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        # 初始化数据库
        sentinel = GitHubSentinel()
        console.print("[green]✓[/green] 数据库初始化完成")
        
        # 检查配置文件
        if not Path("config/config.yaml").exists():
            console.print("[yellow]⚠[/yellow] 配置文件不存在，请复制 config/config.yaml.example 并修改")
        else:
            console.print("[green]✓[/green] 配置文件已存在")
        
        console.print("\n[green]GitHub Sentinel 初始化完成！[/green]")
        console.print("\n下一步:")
        console.print("1. 编辑 config/config.yaml 配置文件")
        console.print("2. 运行 'github-sentinel subscribe add owner/repo' 添加订阅")
        console.print("3. 运行 'github-sentinel start' 启动监控")
        
    except Exception as e:
        console.print(f"[red]✗[/red] 初始化失败: {e}")
        logger.error(f"初始化失败: {e}")


if __name__ == "__main__":
    cli()
