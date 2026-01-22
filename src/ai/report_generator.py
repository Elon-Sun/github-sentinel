"""
AI 驱动的报告生成器
"""

from typing import Dict, List
from loguru import logger
import json
import os
from datetime import datetime


class ReportGenerator:
    """AI 报告生成器"""
    
    def __init__(self, config):
        self.config = config
        self.provider = config.get("ai.provider", "openai")
        self.api_key = config.get("ai.api_key")
        self.model = config.get("ai.model", "gpt-4-turbo-preview")
        self.language = config.get("ai.language", "zh-CN")
        
        # 初始化 AI 客户端
        self._init_client()
    
    def _init_client(self):
        """初始化 AI 客户端"""
        if not self.api_key or self.api_key == "your_ai_api_key_here":
            logger.warning("未配置 AI API Key，将使用基础报告模板")
            self.client = None
            return
        
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI  客户端初始化成功")
            except Exception as e:
                logger.error(f"OpenAI 客户端初始化失败: {e}")
                self.client = None
        
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                logger.info("Anthropic 客户端初始化成功")
            except Exception as e:
                logger.error(f"Anthropic 客户端初始化失败: {e}")
                self.client = None
        elif self.provider == "deepseek":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                logger.info("DeepSeek 客户端初始化成功")
            except Exception as e:
                logger.error(f"DeepSeek 客户端初始化失败: {e}")
                self.client = None
        else:
            logger.warning(f"未知的 AI 提供商: {self.provider}")
            self.client = None
    
    def generate_report(self, repo_name: str, updates: Dict) -> str:
        """生成报告
        
        Args:
            repo_name: 仓库名称
            updates: 更新数据
        
        Returns:
            生成的报告文本
        """
        if self.client and self.config.get("report.generate_summary", True):
            return self._generate_ai_report(repo_name, updates)
        else:
            return self._generate_basic_report(repo_name, updates)
    
    def _generate_ai_report(self, repo_name: str, updates: Dict) -> str:
        """使用 AI 生成报告"""
        try:
            # 构建提示词
            prompt = self._build_prompt(repo_name, updates)
            
            if self.provider == "openai" or self.provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"你是一个专业的技术报告分析师，擅长总结 GitHub 仓库的更新动态。请用{self.language}语言生成报告。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.config.get("ai.max_tokens", 2000),
                    temperature=0.7
                )
                
                report = response.choices[0].message.content
                
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.config.get("ai.max_tokens", 2000),
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                report = response.content[0].text
            
            else:
                return self._generate_basic_report(repo_name, updates)
            
            logger.info(f"AI 报告生成成功: {repo_name}")
            return report
            
        except Exception as e:
            logger.error(f"AI 报告生成失败: {e}，使用基础模板")
            return self._generate_basic_report(repo_name, updates)
    
    def _build_prompt(self, repo_name: str, updates: Dict) -> str:
        """构建 AI 提示词"""
        prompt = f"""
请为 GitHub 仓库 `{repo_name}` 生成一份更新报告。

仓库信息:
- 描述: {updates.get('repo_description', 'N/A')}
- Stars: {updates.get('stars', 0)}
- Forks: {updates.get('forks', 0)}
- 主要语言: {updates.get('language', 'N/A')}

最近更新内容:

## 提交 (Commits)
共 {len(updates.get('commits', []))} 个提交
{self._format_commits_for_prompt(updates.get('commits', []))}

## Pull Requests
共 {len(updates.get('pull_requests', []))} 个 PR
{self._format_prs_for_prompt(updates.get('pull_requests', []))}

## Issues
共 {len(updates.get('issues', []))} 个 Issue
{self._format_issues_for_prompt(updates.get('issues', []))}

## Releases
共 {len(updates.get('releases', []))} 个发布
{self._format_releases_for_prompt(updates.get('releases', []))}

请生成一份结构化的报告，包括:
1. 📊 概览摘要
2. 🔥 重要更新亮点
3. 📝 详细变更说明
4. 📈 活跃度分析
5. 💡 建议与展望

报告应该专业、简洁、易读，使用 Markdown 格式。
"""
        return prompt
    
    def _format_commits_for_prompt(self, commits: List[Dict]) -> str:
        """格式化提交信息用于提示词"""
        if not commits:
            return "无新提交"
        
        lines = []
        for commit in commits[:10]:  # 只取前10个
            lines.append(f"- {commit['sha']}: {commit['message']} by {commit['author']}")
        
        if len(commits) > 10:
            lines.append(f"... 还有 {len(commits) - 10} 个提交")
        
        return '\n'.join(lines)
    
    def _format_prs_for_prompt(self, prs: List[Dict]) -> str:
        """格式化 PR 信息"""
        if not prs:
            return "无新 PR"
        
        lines = []
        for pr in prs[:10]:
            status = "✅ 已合并" if pr.get('merged') else f"📌 {pr['state']}"
            lines.append(f"- #{pr['number']}: {pr['title']} ({status}) by {pr['author']}")
        
        if len(prs) > 10:
            lines.append(f"... 还有 {len(prs) - 10} 个 PR")
        
        return '\n'.join(lines)
    
    def _format_issues_for_prompt(self, issues: List[Dict]) -> str:
        """格式化 Issue 信息"""
        if not issues:
            return "无新 Issue"
        
        lines = []
        for issue in issues[:10]:
            lines.append(f"- #{issue['number']}: {issue['title']} ({issue['state']}) by {issue['author']}")
        
        if len(issues) > 10:
            lines.append(f"... 还有 {len(issues) - 10} 个 Issue")
        
        return '\n'.join(lines)
    
    def _format_releases_for_prompt(self, releases: List[Dict]) -> str:
        """格式化 Release 信息"""
        if not releases:
            return "无新发布"
        
        lines = []
        for release in releases:
            lines.append(f"- {release['tag']}: {release['name']} by {release['author']}")
        
        return '\n'.join(lines)
    
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
                             output_dir: str = "data/reports") -> str:
        """读取每日进展文件，生成正式的项目每日报告
        
        Args:
            repo_name: 仓库名称
            progress_file: 每日进展的 markdown 文件路径
            output_dir: 报告输出目录
        
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
        if self.client:
            report_content = self._generate_ai_daily_report(repo_name, progress_content)
        else:
            logger.warning("未配置 AI，将使用原始进展文件作为报告")
            report_content = progress_content
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成报告文件名
        repo_safe_name = repo_name.replace('/', '_')
        date_str = datetime.now().strftime('%Y-%m-%d')
        report_filename = f"{repo_safe_name}_report_{date_str}.md"
        report_filepath = os.path.join(output_dir, report_filename)
        
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
            prompt = f"""
你是一位专业的技术项目分析师，负责为 GitHub 项目生成正式的每日报告。

以下是 {repo_name} 项目的每日进展记录：

{progress_content}

请基于以上信息，生成一份简短汇总的项目每日报告。报告要求根据功能合并同类项，至少包含：1）新增功能；2）主要改进；3）修复问题；
"""
            
            if self.provider == "openai" or self.provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"你是一位专业的技术项目分析师，擅长分析 GitHub 项目动态并生成正式的项目报告。请用{self.language}语言生成报告。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.config.get("ai.max_tokens", 3000),
                    temperature=0.5  # 降低温度以获得更稳定、正式的输出
                )
                
                report = response.choices[0].message.content
                
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.config.get("ai.max_tokens", 3000),
                    temperature=0.5,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                report = response.content[0].text
            
            else:
                logger.warning(f"未知的 AI 提供商: {self.provider}，使用原始进展")
                return progress_content
            
            # 添加报告元信息
            metadata = f"""---
**项目**: {repo_name}  
**报告日期**: {datetime.now().strftime('%Y-%m-%d')}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**生成方式**: AI 分析（{self.provider} - {self.model}）

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

