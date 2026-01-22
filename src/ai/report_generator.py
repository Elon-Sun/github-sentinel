"""
AI 驱动的报告生成器
"""

from typing import Dict, List
from loguru import logger
import json
import os
from datetime import datetime

from src.ai.ai_client import AIClient
from src.ai.prompts import PromptTemplates


class ReportGenerator:
    """AI 报告生成器"""
    
    def __init__(self, config):
        self.config = config
        self.language = config.get("ai.language", "zh-CN")
        
        # 初始化 AI 客户端
        provider = config.get("ai.provider", "openai")
        api_key = config.get("ai.api_key")
        model = config.get("ai.model", "gpt-4-turbo-preview")
        base_url = config.get("ai.base_url")
        
        self.ai_client = AIClient(provider, api_key, model, base_url)
        
        if self.ai_client.is_available():
            logger.info(f"{provider} AI 客户端初始化成功")
        else:
            logger.warning("AI 客户端不可用，将使用基础报告模板")
    
    def generate_report(self, repo_name: str, updates: Dict) -> str:
        """生成报告
        
        Args:
            repo_name: 仓库名称
            updates: 更新数据
        
        Returns:
            生成的报告文本
        """
        if self.ai_client.is_available() and self.config.get("report.generate_summary", True):
            return self._generate_ai_report(repo_name, updates)
        else:
            return self._generate_basic_report(repo_name, updates)
    
    def _generate_ai_report(self, repo_name: str, updates: Dict) -> str:
        """使用 AI 生成报告"""
        try:
            # 构建提示词
            system_prompt = PromptTemplates.SYSTEM_REPORT_WRITER.format(language=self.language)
            user_prompt = self._build_update_report_prompt(repo_name, updates)
            
            # 调用 AI 生成
            report = self.ai_client.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=self.config.get("ai.max_tokens", 2000),
                temperature=0.7
            )
            
            if report:
                logger.info(f"AI 报告生成成功: {repo_name}")
                return report
            else:
                logger.warning("AI 生成失败，使用基础模板")
                return self._generate_basic_report(repo_name, updates)
                
        except Exception as e:
            logger.error(f"AI 报告生成失败: {e}，使用基础模板")
            return self._generate_basic_report(repo_name, updates)
    
    def _build_update_report_prompt(self, repo_name: str, updates: Dict) -> str:
        """构建更新报告的 AI 提示词"""
        return PromptTemplates.UPDATE_REPORT_TEMPLATE.format(
            repo_name=repo_name,
            repo_description=updates.get('repo_description', 'N/A'),
            stars=updates.get('stars', 0),
            forks=updates.get('forks', 0),
            language=updates.get('language', 'N/A'),
            commits_count=len(updates.get('commits', [])),
            commits_content=PromptTemplates.format_commits(updates.get('commits', [])),
            prs_count=len(updates.get('pull_requests', [])),
            prs_content=PromptTemplates.format_prs(updates.get('pull_requests', [])),
            issues_count=len(updates.get('issues', [])),
            issues_content=PromptTemplates.format_issues(updates.get('issues', [])),
            releases_count=len(updates.get('releases', [])),
            releases_content=PromptTemplates.format_releases(updates.get('releases', []))
        )
    
    def _generate_basic_report(self, repo_name: str, updates: Dict) -> str:
        """生成基础报告（不使用 AI）"""
        report_lines = [
            f"# 📊 {repo_name} 更新报告",
            "",
            f"**仓库**: [{repo_name}](https://github.com/{repo_name})",
            f"**描述**: {updates.get('repo_description', 'N/A')}",
            f"**Stars**: ⭐ {updates.get('stars', 0)} | **Forks**: 🍴 {updates.get('forks', 0)} | **语言**: {updates.get('language', 'N/A')}",
            "",
            "---",
            ""
        ]
        
        # 提交
        commits = updates.get('commits', [])
        if commits:
            report_lines.extend([
                f"## 📝 提交记录 ({len(commits)} 个)",
                ""
            ])
            for commit in commits[:15]:
                report_lines.append(
                    f"- **{commit['sha']}**: {commit['message']} - *{commit['author']}* - {commit['date'][:10]}"
                )
            if len(commits) > 15:
                report_lines.append(f"\n*... 还有 {len(commits) - 15} 个提交*")
            report_lines.append("")
        
        # Pull Requests
        prs = updates.get('pull_requests', [])
        if prs:
            report_lines.extend([
                f"## 🔀 Pull Requests ({len(prs)} 个)",
                ""
            ])
            for pr in prs[:10]:
                status_icon = "✅" if pr.get('merged') else ("🟢" if pr['state'] == 'open' else "🔴")
                report_lines.append(
                    f"- {status_icon} **#{pr['number']}**: {pr['title']} - *{pr['author']}*"
                )
            if len(prs) > 10:
                report_lines.append(f"\n*... 还有 {len(prs) - 10} 个 PR*")
            report_lines.append("")
        
        # Issues
        issues = updates.get('issues', [])
        if issues:
            report_lines.extend([
                f"## 🐛 Issues ({len(issues)} 个)",
                ""
            ])
            for issue in issues[:10]:
                status_icon = "🟢" if issue['state'] == 'open' else "🔴"
                labels = f" [{', '.join(issue['labels'])}]" if issue['labels'] else ""
                report_lines.append(
                    f"- {status_icon} **#{issue['number']}**: {issue['title']}{labels} - *{issue['author']}*"
                )
            if len(issues) > 10:
                report_lines.append(f"\n*... 还有 {len(issues) - 10} 个 Issue*")
            report_lines.append("")
        
        # Releases
        releases = updates.get('releases', [])
        if releases:
            report_lines.extend([
                f"## 🚀 发布版本 ({len(releases)} 个)",
                ""
            ])
            for release in releases:
                prerelease_tag = " (预发布)" if release.get('prerelease') else ""
                report_lines.append(
                    f"- **{release['tag']}**: {release['name']}{prerelease_tag} - *{release['author']}*"
                )
                if release.get('body'):
                    # 只取前两行描述
                    body_lines = release['body'].split('\n')[:2]
                    for line in body_lines:
                        if line.strip():
                            report_lines.append(f"  {line.strip()}")
                report_lines.append("")
        
        # 摘要统计
        report_lines.extend([
            "---",
            "",
            "## 📈 活跃度统计",
            "",
            f"- 📝 提交: {len(commits)}",
            f"- 🔀 Pull Requests: {len(prs)}",
            f"- 🐛 Issues: {len(issues)}",
            f"- 🚀 版本发布: {len(releases)}",
            "",
            f"*报告生成时间: {updates.get('updated_at', 'N/A')}*"
        ])
        
        return '\n'.join(report_lines)
    
    def generate_daily_report(self, repo_name: str, progress_file: str, 
                             output_dir: str = "data/reports", 
                             start_date: datetime = None, end_date: datetime = None) -> str:
        """读取每日进展文件，生成正式的项目每日报告
        
        Args:
            repo_name: 仓库名称
            progress_file: 每日进展的 markdown 文件路径
            output_dir: 报告输出目录
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            生成的报告文件路径
        """
        logger.info(f"开始生成 {repo_name} 的每日报告...")
        
        # 读取每日进展文件
        if not os.path.exists(progress_file):
            raise FileNotFoundError(f"每日进展文件不存在: {progress_file}")
        
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_content = f.read()
        
        # 使用 AI 生成报告
        if self.ai_client.is_available():
            report_content = self._generate_ai_daily_report(repo_name, progress_content)
        else:
            logger.warning("未配置 AI，将使用原始进展文件作为报告")
            report_content = progress_content
        
        # 创建项目特定的输出目录
        repo_safe_name = repo_name.replace('/', '_')
        project_dir = os.path.join(output_dir, repo_safe_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 生成报告文件名（包含日期范围）
        if start_date and end_date:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            if start_str == end_str:
                date_suffix = start_str
            else:
                date_suffix = f"{start_str}_to_{end_str}"
        else:
            # 默认使用当前日期
            date_suffix = datetime.now().strftime('%Y-%m-%d')
        
        report_filename = f"{repo_safe_name}_report_{date_suffix}.md"
        report_filepath = os.path.join(project_dir, report_filename)
        
        # 写入报告
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"每日报告已生成: {report_filepath}")
        return report_filepath
    
    def _generate_ai_daily_report(self, repo_name: str, progress_content: str) -> str:
        """使用 AI 生成正式的每日报告
        
        Args:
            repo_name: 仓库名称
            progress_content: 每日进展的原始内容
        
        Returns:
            生成的正式报告内容
        """
        try:
            # 构建提示词
            system_prompt = PromptTemplates.SYSTEM_ANALYST.format(language=self.language)
            user_prompt = PromptTemplates.DAILY_REPORT_TEMPLATE.format(
                repo_name=repo_name,
                progress_content=progress_content
            )
            
            # 调用 AI 生成
            report = self.ai_client.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=self.config.get("ai.max_tokens", 3000),
                temperature=0.5  # 降低温度以获得更稳定、正式的输出
            )
            
            if not report:
                logger.warning("AI 生成失败，使用原始进展文件")
                return progress_content
            
            # 添加报告元信息
            metadata = f"""---
**项目**: {repo_name}  
**报告日期**: {datetime.now().strftime('%Y-%m-%d')}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**生成方式**: AI 分析（{self.ai_client.provider} - {self.ai_client.model}）

---

"""
            
            full_report = metadata + report + "\n\n---\n\n*本报告由 GitHub Sentinel 基于 AI 技术自动生成*\n"
            
            logger.info(f"AI 每日报告生成成功: {repo_name}")
            return full_report
            
        except Exception as e:
            logger.error(f"AI 每日报告生成失败: {e}，使用原始进展文件")
            return progress_content
    
    def batch_generate_reports(self, repo_names: List[str], date: datetime = None,
                               progress_dir: str = "data/daily_progress",
                               output_dir: str = "data/reports") -> List[str]:
        """批量生成多个仓库的每日报告
        
        Args:
            repo_names: 仓库名称列表
            date: 目标日期，默认为当天
            progress_dir: 每日进展文件目录
            output_dir: 报告输出目录
        
        Returns:
            生成的报告文件路径列表
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        report_files = []
        
        for repo_name in repo_names:
            try:
                # 构建进展文件路径
                repo_safe_name = repo_name.replace('/', '_')
                progress_file = os.path.join(progress_dir, f"{repo_safe_name}_{date_str}.md")
                
                # 生成报告
                report_file = self.generate_daily_report(repo_name, progress_file, output_dir)
                report_files.append(report_file)
                
            except Exception as e:
                logger.error(f"生成 {repo_name} 的报告失败: {e}")
                continue
        
        logger.info(f"批量报告生成完成，成功: {len(report_files)}/{len(repo_names)}")
        return report_files

