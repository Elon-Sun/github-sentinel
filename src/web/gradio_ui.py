"""
Gradio Web 界面
提供友好的图形化界面来使用 GitHub Sentinel 的所有功能
"""

import gradio as gr
from datetime import datetime, timedelta
from loguru import logger
import os
from typing import List, Tuple

from src.core.subscription_manager import SubscriptionManager
from src.core.github_client import GitHubClient
from src.ai.report_generator import ReportGenerator
from src.storage.database import Database
from src.config_loader import ConfigLoader


class GitHubSentinelUI:
    """GitHub Sentinel Web UI"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化 UI"""
        self.config = ConfigLoader(config_path)
        self.db = Database(self.config.get("database.path", "data/sentinel.json"))
        self.github_client = GitHubClient(self.config.get("github.token"))
        self.subscription_manager = SubscriptionManager(self.db, self.github_client)
        self.report_generator = ReportGenerator(self.config)
        
        logger.info("GitHub Sentinel Web UI 初始化成功")
    
    def list_subscriptions(self) -> str:
        """列出所有订阅"""
        try:
            subscriptions = self.subscription_manager.list_subscriptions()
            if not subscriptions:
                return "📭 暂无订阅的仓库"
            
            result = "## 📚 订阅列表\n\n"
            for sub in subscriptions:
                result += f"- **{sub['repo_name']}**\n"
                result += f"  - 订阅时间: {sub['created_at']}\n"
                if sub.get('last_updated'):
                    result += f"  - 最后更新: {sub['last_updated']}\n"
                else:
                    result += f"  - 最后更新: 从未检查\n"
                if sub.get('tags'):
                    result += f"  - 标签: {sub['tags']}\n"
                result += "\n"
            
            return result
        except Exception as e:
            logger.error(f"获取订阅列表失败: {e}")
            return f"❌ 获取订阅列表失败: {str(e)}"
    
    def add_subscription(self, repo_name: str, frequency: str) -> str:
        """添加订阅"""
        try:
            if not repo_name or not repo_name.strip():
                return "❌ 请输入仓库名称（格式: owner/repo）"
            
            repo_name = repo_name.strip()
            
            # 验证仓库格式
            if '/' not in repo_name:
                return "❌ 仓库格式错误，正确格式: owner/repo"
            
            # 检查仓库是否存在
            if not self.github_client.validate_repository(repo_name):
                return f"❌ 仓库 {repo_name} 不存在或无法访问"
            
            # 添加订阅（使用 frequency 作为标签）
            tags = [frequency] if frequency else []
            subscription_id = self.subscription_manager.add_subscription(repo_name, tags)
            return f"✅ 成功订阅仓库: {repo_name} ({frequency}) [ID: {subscription_id}]"
        
        except Exception as e:
            logger.error(f"添加订阅失败: {e}")
            return f"❌ 添加订阅失败: {str(e)}"
    
    def remove_subscription(self, repo_name: str) -> str:
        """移除订阅"""
        try:
            if not repo_name or not repo_name.strip():
                return "❌ 请输入要移除的仓库名称"
            
            repo_name = repo_name.strip()
            success = self.subscription_manager.remove_subscription(repo_name)
            
            if success:
                return f"✅ 成功移除订阅: {repo_name}"
            else:
                return f"⚠️ 未找到订阅: {repo_name}"
        
        except Exception as e:
            logger.error(f"移除订阅失败: {e}")
            return f"❌ 移除订阅失败: {str(e)}"
    
    def generate_all_repos_report(self, start_date: str, end_date: str) -> Tuple[str, str, List[str]]:
        """为所有订阅仓库生成自定义日期范围报告
        
        直接获取 Issues 和 PRs 数据，与日期范围一致
        
        Returns:
            Tuple[status_msg, report_content, report_files]
        """
        try:
            subscriptions = self.subscription_manager.list_subscriptions()
            
            if not subscriptions:
                return "⚠️ 没有订阅任何仓库，请先添加订阅", "", []
            
            # 解析日期
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return "❌ 日期格式错误，请使用 YYYY-MM-DD 格式", "", []
            
            if start > end:
                return "❌ 开始日期不能晚于结束日期", "", []
            
            success_msg = f"# 📝 批量报告生成\n\n"
            success_msg += f"📅 日期范围: {start_date} 至 {end_date}\n"
            success_msg += f"📦 处理仓库: {len(subscriptions)} 个\n\n---\n\n"
            
            all_reports = ""
            report_files = []  # 收集所有生成的报告文件路径
            
            for idx, sub in enumerate(subscriptions, 1):
                repo_name = sub['repo_name']
                success_msg += f"{idx}. **{repo_name}**\n"
                
                try:
                    # 验证仓库
                    if not self.github_client.validate_repository(repo_name):
                        success_msg += f"   - ❌ 仓库不存在或无法访问\n"
                        continue
                    
                    logger.info(f"正在处理仓库 {repo_name} ({start_date} 至 {end_date})...")
                    
                    # 直接获取指定日期范围的 Issues 和 PRs（作为 AI 报告的背景输入）
                    issues = self.github_client.get_daily_issues(repo_name, start_date=start, end_date=end)
                    prs = self.github_client.get_daily_pull_requests(repo_name, start_date=start, end_date=end)
                    
                    logger.info(f"仓库 {repo_name}: 获取到 {len(issues)} 个 Issues, {len(prs)} 个 PRs")
                    
                    # 导出进展数据
                    progress_file = self.github_client.export_daily_progress(
                        repo_name, issues, prs, 
                        start_date=start, end_date=end,
                        output_dir="data/daily_progress"
                    )
                    
                    # 生成 AI 报告（基于获取的 Issues 和 PRs）
                    report_file = self.report_generator.generate_daily_report(
                        repo_name, progress_file,
                        output_dir="data/reports",
                        start_date=start, end_date=end
                    )
                    
                    # 收集报告文件路径
                    report_files.append(report_file)
                    
                    # 读取报告内容
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    success_msg += f"   - ✅ 报告: `{report_file}`\n"
                    success_msg += f"   - 📊 数据: {len(issues)} Issues, {len(prs)} PRs\n"
                    all_reports += f"\n\n---\n\n# 📊 {repo_name}\n\n{report_content}\n\n"
                    
                except Exception as e:
                    logger.error(f"生成 {repo_name} 报告失败: {e}")
                    success_msg += f"   - ❌ 失败: {str(e)}\n"
            
            return success_msg, all_reports, report_files
        
        except Exception as e:
            logger.error(f"批量生成报告失败: {e}")
            return f"❌ 批量生成报告失败: {str(e)}", "", []
    
    def build_interface(self):
        """构建 Gradio 界面"""
        with gr.Blocks(title="GitHub Sentinel", theme=gr.themes.Soft()) as interface:
            gr.Markdown("""
            # 🔍 GitHub Sentinel
            ### 智能 GitHub 仓库监控与 AI 报告系统
            
            订阅你关注的 GitHub 仓库，自动生成详细的 AI 分析报告
            """)
            
            # 订阅管理区域
            gr.Markdown("## 📚 订阅管理")
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### ➕ 添加订阅")
                    add_repo_input = gr.Textbox(
                        label="仓库名称",
                        placeholder="例如: microsoft/vscode",
                        info="格式: owner/repo"
                    )
                    add_frequency = gr.Dropdown(
                        choices=["daily", "weekly"],
                        value="daily",
                        label="更新频率"
                    )
                    add_btn = gr.Button("➕ 添加订阅", variant="primary", size="lg")
                    add_output = gr.Markdown()
                
                with gr.Column(scale=1):
                    gr.Markdown("### ➖ 移除订阅")
                    remove_repo_input = gr.Textbox(
                        label="仓库名称",
                        placeholder="例如: microsoft/vscode"
                    )
                    remove_btn = gr.Button("➖ 移除订阅", variant="stop", size="lg")
                    remove_output = gr.Markdown()
            
            gr.Markdown("---")
            gr.Markdown("### 📋 当前订阅列表")
            list_btn = gr.Button("🔄 刷新列表", size="sm")
            subscriptions_output = gr.Markdown()
            
            gr.Markdown("---")
            
            # 生成 AI 报告区域
            gr.Markdown("## 📝 生成 AI 分析报告")
            gr.Markdown("""
            为所有订阅仓库生成指定日期范围的详细 AI 分析报告
            
            系统会自动获取该时间段内的 Issues 和 Pull Requests，并由 AI 进行深度分析
            """)
            
            with gr.Row():
                start_date_input = gr.Textbox(
                    label="开始日期",
                    placeholder="YYYY-MM-DD",
                    value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    scale=1
                )
                end_date_input = gr.Textbox(
                    label="结束日期",
                    placeholder="YYYY-MM-DD",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    scale=1
                )
            
            generate_btn = gr.Button("🤖 生成 AI 报告", variant="primary", size="lg")
            report_status = gr.Markdown()
            report_content = gr.Markdown()
            
            # 下载区域
            gr.Markdown("### 📥 下载报告")
            download_files = gr.File(
                label="生成的报告文件",
                file_count="multiple",
                type="filepath",
                interactive=False,
                visible=True
            )
            
            # 事件绑定
            add_btn.click(
                fn=self.add_subscription,
                inputs=[add_repo_input, add_frequency],
                outputs=add_output
            )
            remove_btn.click(
                fn=self.remove_subscription,
                inputs=remove_repo_input,
                outputs=remove_output
            )
            list_btn.click(
                fn=self.list_subscriptions,
                outputs=subscriptions_output
            )
            generate_btn.click(
                fn=self.generate_all_repos_report,
                inputs=[start_date_input, end_date_input],
                outputs=[report_status, report_content, download_files]
            )
            
            # 初始加载订阅列表
            interface.load(
                fn=self.list_subscriptions,
                outputs=subscriptions_output
            )
            
            gr.Markdown("""
            ---
            💡 **使用说明**: 
            
            1. **订阅管理**: 添加或移除需要监控的 GitHub 仓库
            2. **生成报告**: 为所有订阅仓库生成指定日期范围的 AI 分析报告
               - 系统会获取该时间段的 Issues 和 PRs 作为分析数据
               - AI 会自动分析项目进展、关键更新和技术趋势
               - 报告会保存到本地文件系统
            
            📁 报告保存位置:
            - 数据文件: `data/daily_progress/{repo_name}/`
            - AI 报告: `data/reports/{repo_name}/`
            
            Made with ❤️ by GitHub Sentinel
            """)
        
        return interface
    
    def launch(self, **kwargs):
        """启动 Web 界面"""
        interface = self.build_interface()
        interface.launch(**kwargs)


def main():
    """主函数"""
    ui = GitHubSentinelUI()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
