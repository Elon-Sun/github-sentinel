"""
交互式命令行界面模块
"""

import cmd
from rich.console import Console
from rich.table import Table
from loguru import logger

console = Console()


class SentinelShell(cmd.Cmd):
    """交互式命令行界面"""
    intro = '欢迎使用 GitHub Sentinel 交互式终端。输入 help 或 ? 查看命令列表。\n'
    prompt = '(sentinel) '

    def __init__(self, sentinel):
        """初始化交互式Shell
        
        Args:
            sentinel: GitHubSentinel 实例
        """
        super().__init__()
        self.sentinel = sentinel

    def do_list(self, arg):
        """列出所有订阅: list"""
        subscriptions = self.sentinel.subscription_manager.list_subscriptions()
        if not subscriptions:
            console.print("[yellow]没有订阅的仓库[/yellow]")
            return
        
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

    def do_add(self, arg):
        """添加订阅: add owner/repo [tags]"""
        args = arg.split()
        if not args:
            console.print("[red]错误: 请指定仓库名称 (owner/repo)[/red]")
            return
        
        repo_name = args[0]
        tags = args[1].split(',') if len(args) > 1 else []
        
        try:
            self.sentinel.subscription_manager.add_subscription(repo_name, tags)
            console.print(f"[green]✓[/green] 已添加订阅: {repo_name}")
        except Exception as e:
            console.print(f"[red]✗[/red] 添加订阅失败: {e}")

    def do_remove(self, arg):
        """移除订阅: remove owner/repo"""
        if not arg:
            console.print("[red]错误: 请指定仓库名称[/red]")
            return
            
        try:
            self.sentinel.subscription_manager.remove_subscription(arg)
            console.print(f"[green]✓[/green] 已移除订阅: {arg}")
        except Exception as e:
            console.print(f"[red]✗[/red] 移除订阅失败: {e}")

    def do_update(self, arg):
        """更新仓库: update [owner/repo]
        如果不指定仓库，则更新所有订阅。
        """
        if arg:
            self.sentinel.update_single_repository(arg)
        else:
            self.sentinel.update_repositories()

    def do_check(self, arg):
        """检查仓库: check owner/repo
        检查指定仓库的更新（无需订阅）
        """
        if not arg:
            console.print("[red]错误: 请指定仓库名称[/red]")
            return
        
        try:
            self.sentinel.update_single_repository(arg)
        except Exception as e:
            console.print(f"[red]✗[/red] 检查失败: {e}")

    def do_status(self, arg):
        """显示系统状态"""
        console.print("\n[bold cyan]GitHub Sentinel 状态[/bold cyan]")
        subscriptions = self.sentinel.subscription_manager.list_subscriptions()
        console.print(f"订阅数量: {len(subscriptions)}")
        console.print(f"调度间隔: {self.sentinel.config.get('schedule.interval', 'daily')}")
        console.print(f"AI 提供商: {self.sentinel.config.get('ai.provider', 'N/A')}")
        console.print()

    def do_exit(self, arg):
        """退出交互模式"""
        console.print("再见！")
        return True
    
    def do_quit(self, arg):
        """退出交互模式"""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """处理 Ctrl+D"""
        console.print()
        return self.do_exit(arg)

    def emptyline(self):
        """空行不执行任何操作"""
        pass
    
    def default(self, line):
        """处理未知命令"""
        console.print(f"[yellow]未知命令: {line}[/yellow]")
        console.print("输入 'help' 查看可用命令")
