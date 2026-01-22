"""
主入口文件 - 命令行接口
"""

import click
import sys
from rich.console import Console
from loguru import logger
from pathlib import Path

from src.core.subscription_manager import SubscriptionManager
from src.core.github_client import GitHubClient
from src.core.scheduler import Scheduler
from src.ai.report_generator import ReportGenerator
from src.storage.database import Database
from src.config_loader import ConfigLoader
from src.cli.interactive_shell import SentinelShell
from src.cli.subscription_commands import SubscriptionCommands

console = Console()


class GitHubSentinel:
    """GitHub Sentinel 主类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = ConfigLoader(config_path)
        self.db = Database(self.config.get("database.path", "data/sentinel.json"))
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
            self.update_single_repository(sub['repo_name'], sub['id'])

    def update_single_repository(self, repo_name: str, sub_id: int = None):
        """更新单个仓库
        
        Args:
            repo_name: 仓库名称
            sub_id: 订阅ID（可选），如果没有提供，尝试查找
        """
        try:
            logger.info(f"正在更新仓库: {repo_name}")
            
            if sub_id is None:
                sub = self.subscription_manager.get_subscription(repo_name)
                if sub:
                    sub_id = sub['id']
                else:
                    # 如果未订阅，仅生成临时报告，不保存记录？
                    # 或者我们可以允许更新未订阅的仓库作为一次性检查
                    pass

            updates = self.github_client.fetch_repository_updates(
                repo_name,
                days=self.config.get("report.max_days", 7)
            )
            
            # 生成报告
            report = self.report_generator.generate_report(repo_name, updates)
            
            # 打印报告到控制台
            console.print(f"\n[bold cyan]=== {repo_name} 更新报告 ===[/bold cyan]")
            console.print(report)
            console.print(f"[bold cyan]===========================[/bold cyan]\n")

            # 如果是已订阅的仓库，保存记录并发送通知
            if sub_id:
                # 保存更新记录
                self.subscription_manager.save_update_record(sub_id, updates)
                
                # 发送通知
                self._send_notification(repo_name, report)
                console.print(f"[green]✓[/green] 已记录并通知: {repo_name}")
            else:
                console.print(f"[yellow]ℹ[/yellow] 这是一个未订阅的仓库，仅显示报告。")
            
        except Exception as e:
            logger.error(f"更新仓库 {repo_name} 失败: {e}")
            console.print(f"[red]✗[/red] 更新失败: {repo_name}")
    
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
    
    def generate_daily_reports(self):
        """为所有订阅的仓库生成每日报告"""
        logger.info("开始生成每日报告...")
        subscriptions = self.subscription_manager.list_subscriptions()
        
        if not subscriptions:
            logger.warning("没有订阅的仓库")
            return
        
        success_count = 0
        fail_count = 0
        
        for sub in subscriptions:
            repo_name = sub['repo_name']
            try:
                logger.info(f"正在生成 {repo_name} 的每日报告...")
                
                # 获取今日的 Issues 和 PRs
                issues = self.github_client.get_daily_issues(repo_name)
                pull_requests = self.github_client.get_daily_pull_requests(repo_name)
                
                # 导出每日进展
                progress_file = self.github_client.export_daily_progress(
                    repo_name, issues, pull_requests
                )
                
                # 生成 AI 报告
                report_file = self.report_generator.generate_daily_report(
                    repo_name, progress_file
                )
                
                logger.info(f"✓ {repo_name} 每日报告已生成: {report_file}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"✗ 生成 {repo_name} 的每日报告失败: {e}")
                fail_count += 1
        
        logger.info(f"每日报告生成完成 - 成功: {success_count}, 失败: {fail_count}")
        return success_count, fail_count


@click.group()
@click.version_option(version="0.1")
def cli():
    """GitHub Sentinel - AI驱动的GitHub仓库监控工具"""
    pass

@cli.command()
def interactive():
    """启动交互式命令行界面"""
    try:
        SentinelShell().cmdloop()
    except KeyboardInterrupt:
        console.print("\n[yellow]退出...[/yellow]")

@cli.group()
def subscribe():
    """管理仓库订阅"""
    pass

@subscribe.command("add")
@click.argument("repo_name")
@click.option("--tags", "-t", help="标签（逗号分隔）", default="")
def subscribe_add(repo_name: str, tags: str):
    """添加仓库订阅"""
    try:
        sentinel = GitHubSentinel()
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        sentinel.subscription_manager.add_subscription(repo_name, tag_list)
        console.print(f"[green]✓[/green] 已添加订阅: {repo_name}")
    except Exception as e:
        console.print(f"[red]✗[/red] 添加订阅失败: {e}")

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

@cli.command()
def interactive():
    """启动交互式命令行界面"""
    try:
        sentinel = GitHubSentinel()
        SentinelShell(sentinel).cmdloop()
    except KeyboardInterrupt:
        console.print("\n[yellow]退出...[/yellow]")

@cli.group()
def subscribe():
    """管理仓库订阅"""
    pass

@subscribe.command("add")
@click.argument("repo_name")
@click.option("--tags", "-t", help="标签（逗号分隔）", default="")
def subscribe_add(repo_name: str, tags: str):
    """添加仓库订阅"""
    sentinel = GitHubSentinel()
    commands = SubscriptionCommands(sentinel)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    commands.add_subscription(repo_name, tag_list)

@subscribe.command("remove")
@click.argument("repo_name")
def subscribe_remove(repo_name: str):
    """移除仓库订阅"""
    sentinel = GitHubSentinel()
    commands = SubscriptionCommands(sentinel)
    commands.remove_subscription(repo_name)

@subscribe.command("list")
def subscribe_list():
    """列出所有订阅"""
    sentinel = GitHubSentinel()
    commands = SubscriptionCommands(sentinel)
    commands.list_subscriptions()

@cli.command()
def update():
    """手动触发更新所有订阅的仓库"""
    try:
        sentinel = GitHubSentinel()
        sentinel.update_repositories()
    except Exception as e:
        console.print(f"[red]✗[/red] 更新失败: {e}")

@cli.command("check")
@click.argument("repo_name")
def check_repo(repo_name: str):
    """检查单个仓库更新并生成报告（无论是否订阅）"""
    sentinel = GitHubSentinel()
    commands = SubscriptionCommands(sentinel)
    commands.check_repository(repo_name)

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

@cli.command()
def init():
    """初始化配置和数据库"""
    try:
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        sentinel = GitHubSentinel()
        console.print("[green]✓[/green] 数据库初始化完成")
        if not Path("config/config.yaml").exists():
            console.print("[yellow]⚠[/yellow] 配置文件不存在，请复制 config/config.yaml.example 并修改")
        else:
            console.print("[green]✓[/green] 配置文件已存在")
        console.print("\n[green]GitHub Sentinel 初始化完成！[/green]")
    except Exception as e:
        console.print(f"[red]✗[/red] 初始化失败: {e}")

if __name__ == "__main__":
    cli()