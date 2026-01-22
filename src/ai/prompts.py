"""
AI Prompt 模板管理
将所有 prompt 内容集中管理，便于维护和优化
"""

from typing import Dict, List


class PromptTemplates:
    """Prompt 模板类"""
    
    # 系统角色提示
    SYSTEM_ANALYST = """你是一位专业的技术项目分析师，擅长分析 GitHub 项目动态并生成正式的项目报告。请用{language}语言生成报告。"""
    
    SYSTEM_REPORT_WRITER = """你是一个专业的技术报告分析师，擅长总结 GitHub 仓库的更新动态。请用{language}语言生成报告。"""
    
    # 更新报告提示模板
    UPDATE_REPORT_TEMPLATE = """
请为 GitHub 仓库 `{repo_name}` 生成一份更新报告。

仓库信息:
- 描述: {repo_description}
- Stars: {stars}
- Forks: {forks}
- 主要语言: {language}

最近更新内容:

## 提交 (Commits)
共 {commits_count} 个提交
{commits_content}

## Pull Requests
共 {prs_count} 个 PR
{prs_content}

## Issues
共 {issues_count} 个 Issue
{issues_content}

## Releases
共 {releases_count} 个发布
{releases_content}

请生成一份结构化的报告，包括:
1. 📊 概览摘要
2. 🔥 重要更新亮点
3. 📝 详细变更说明
4. 📈 活跃度分析
5. 💡 建议与展望

报告应该专业、简洁、易读，使用 Markdown 格式。
"""
    
    # 每日报告提示模板
    DAILY_REPORT_TEMPLATE = """
你是一位专业的技术项目分析师，负责为 GitHub 项目生成正式的每日报告。

以下是 {repo_name} 项目的每日进展记录：

{progress_content}

请基于以上信息，生成一份简短汇总的项目每日报告。报告要求根据功能合并同类项，至少包含：1）新增功能；2）主要改进；3）修复问题；
"""
    
    @staticmethod
    def format_commits(commits: List[Dict], max_count: int = 10) -> str:
        """格式化提交信息"""
        if not commits:
            return "无新提交"
        
        lines = []
        for commit in commits[:max_count]:
            lines.append(f"- {commit['sha']}: {commit['message']} by {commit['author']}")
        
        if len(commits) > max_count:
            lines.append(f"... 还有 {len(commits) - max_count} 个提交")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_prs(prs: List[Dict], max_count: int = 10) -> str:
        """格式化 PR 信息"""
        if not prs:
            return "无新 PR"
        
        lines = []
        for pr in prs[:max_count]:
            status = "✅ 已合并" if pr.get('merged') else f"📌 {pr['state']}"
            lines.append(f"- #{pr['number']}: {pr['title']} ({status}) by {pr['author']}")
        
        if len(prs) > max_count:
            lines.append(f"... 还有 {len(prs) - max_count} 个 PR")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_issues(issues: List[Dict], max_count: int = 10) -> str:
        """格式化 Issue 信息"""
        if not issues:
            return "无新 Issue"
        
        lines = []
        for issue in issues[:max_count]:
            lines.append(f"- #{issue['number']}: {issue['title']} ({issue['state']}) by {issue['author']}")
        
        if len(issues) > max_count:
            lines.append(f"... 还有 {len(issues) - max_count} 个 Issue")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_releases(releases: List[Dict]) -> str:
        """格式化 Release 信息"""
        if not releases:
            return "无新发布"
        
        lines = []
        for release in releases:
            lines.append(f"- {release['tag']}: {release['name']} by {release['author']}")
        
        return '\n'.join(lines)
