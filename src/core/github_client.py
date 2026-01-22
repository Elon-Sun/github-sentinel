"""
GitHub API 客户端
"""

from github import Github, GithubException
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from loguru import logger
import os


class GitHubClient:
    """GitHub API 客户端封装"""
    
    def __init__(self, token: str):
        """初始化 GitHub 客户端
        
        Args:
            token: GitHub Personal Access Token
        """
        if not token or token == "your_github_token_here":
            logger.warning("未设置有效的 GitHub Token，将使用匿名访问（受限于更严格的 Rate Limit）")
            self.github = Github()
            self.user = None
        else:
            self.github = Github(token)
            try:
                self.user = self.github.get_user()
                logger.info(f"GitHub 客户端初始化成功，当前用户: {self.user.login}")
            except Exception as e:
                logger.warning(f"GitHub Token 无效或无法获取用户信息: {e}，将尝试匿名访问")
                self.github = Github()
                self.user = None
    
    def validate_repository(self, repo_name: str) -> bool:
        """验证仓库是否存在
        
        Args:
            repo_name: 仓库名称，格式为 owner/repo
        
        Returns:
            是否存在
        """
        try:
            self.github.get_repo(repo_name)
            return True
        except GithubException:
            return False
    
    def fetch_repository_updates(self, repo_name: str, days: int = 7) -> Dict:
        """获取仓库更新信息
        
        Args:
            repo_name: 仓库名称
            days: 获取最近多少天的更新
        
        Returns:
            包含各类更新的字典
        """
        logger.info(f"正在获取仓库 {repo_name} 最近 {days} 天的更新...")
        
        try:
            repo = self.github.get_repo(repo_name)
            since_date = datetime.now() - timedelta(days=days)
            
            updates = {
                'repo_name': repo_name,
                'repo_description': repo.description,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'language': repo.language,
                'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                'commits': self._fetch_commits(repo, since_date),
                'pull_requests': self._fetch_pull_requests(repo, since_date),
                'issues': self._fetch_issues(repo, since_date),
                'releases': self._fetch_releases(repo, since_date),
            }
            
            logger.info(f"仓库 {repo_name} 更新获取成功")
            return updates
            
        except GithubException as e:
            logger.error(f"获取仓库 {repo_name} 更新失败: {e}")
            raise
    
    def _fetch_commits(self, repo, since_date: datetime) -> List[Dict]:
        """获取提交记录"""
        commits = []
        try:
            for commit in repo.get_commits(since=since_date):
                commits.append({
                    'sha': commit.sha[:7],
                    'message': commit.commit.message.split('\n')[0],  # 只取第一行
                    'author': commit.commit.author.name,
                    'date': commit.commit.author.date.isoformat(),
                    'url': commit.html_url
                })
                if len(commits) >= 50:  # 限制数量
                    break
        except Exception as e:
            logger.warning(f"获取提交记录失败: {e}")
        
        return commits
    
    def _fetch_pull_requests(self, repo, since_date: datetime) -> List[Dict]:
        """获取 Pull Requests"""
        prs = []
        try:
            for pr in repo.get_pulls(state='all', sort='updated', direction='desc'):
                if pr.updated_at < since_date:
                    break
                
                prs.append({
                    'number': pr.number,
                    'title': pr.title,
                    'state': pr.state,
                    'author': pr.user.login,
                    'created_at': pr.created_at.isoformat(),
                    'updated_at': pr.updated_at.isoformat(),
                    'merged': pr.merged,
                    'url': pr.html_url
                })
                
                if len(prs) >= 30:
                    break
        except Exception as e:
            logger.warning(f"获取 Pull Requests 失败: {e}")
        
        return prs
    
    def _fetch_issues(self, repo, since_date: datetime) -> List[Dict]:
        """获取 Issues"""
        issues = []
        try:
            for issue in repo.get_issues(state='all', sort='updated', direction='desc'):
                if issue.updated_at < since_date:
                    break
                
                # 跳过 Pull Requests（GitHub API 中 PR 也算 Issue）
                if issue.pull_request:
                    continue
                
                issues.append({
                    'number': issue.number,
                    'title': issue.title,
                    'state': issue.state,
                    'author': issue.user.login,
                    'created_at': issue.created_at.isoformat(),
                    'updated_at': issue.updated_at.isoformat(),
                    'comments': issue.comments,
                    'labels': [label.name for label in issue.labels],
                    'url': issue.html_url
                })
                
                if len(issues) >= 30:
                    break
        except Exception as e:
            logger.warning(f"获取 Issues 失败: {e}")
        
        return issues
    
    def _fetch_releases(self, repo, since_date: datetime) -> List[Dict]:
        """获取发布版本"""
        releases = []
        try:
            for release in repo.get_releases():
                if release.created_at < since_date:
                    break
                
                releases.append({
                    'tag': release.tag_name,
                    'name': release.title or release.tag_name,
                    'body': release.body or '',
                    'author': release.author.login if release.author else 'Unknown',
                    'created_at': release.created_at.isoformat(),
                    'prerelease': release.prerelease,
                    'url': release.html_url
                })
                
                if len(releases) >= 10:
                    break
        except Exception as e:
            logger.warning(f"获取 Releases 失败: {e}")
        
        return releases
    
    def get_rate_limit(self) -> Dict:
        """获取 API 调用限制信息"""
        rate_limit = self.github.get_rate_limit()
        return {
            'core': {
                'limit': rate_limit.core.limit,
                'remaining': rate_limit.core.remaining,
                'reset': rate_limit.core.reset.isoformat()
            }
        }
    
    def get_daily_issues(self, repo_name: str, date: datetime = None) -> List[Dict]:
        """获取指定日期的 Issues 列表
        
        Args:
            repo_name: 仓库名称，格式为 owner/repo
            date: 目标日期，默认为当天
        
        Returns:
            Issues 列表
        """
        if date is None:
            date = datetime.now(timezone.utc)
        
        # 获取指定日期的起始和结束时间（使用 UTC 时区）
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        logger.info(f"正在获取仓库 {repo_name} 在 {date.strftime('%Y-%m-%d')} 的 Issues...")
        
        try:
            repo = self.github.get_repo(repo_name)
            issues = []
            
            # 获取在指定日期更新或创建的 Issues
            for issue in repo.get_issues(state='all', sort='updated', direction='desc'):
                # 跳过 Pull Requests
                if issue.pull_request:
                    continue
                
                # 检查是否在目标日期范围内创建或更新
                created_in_range = start_date <= issue.created_at < end_date
                updated_in_range = start_date <= issue.updated_at < end_date
                
                if created_in_range or updated_in_range:
                    issues.append({
                        'number': issue.number,
                        'title': issue.title,
                        'state': issue.state,
                        'author': issue.user.login if issue.user else 'Unknown',
                        'created_at': issue.created_at.isoformat(),
                        'updated_at': issue.updated_at.isoformat(),
                        'comments': issue.comments,
                        'labels': [label.name for label in issue.labels],
                        'body': issue.body or '',
                        'url': issue.html_url,
                        'is_new': created_in_range  # 标记是否为新创建
                    })
                
                # 如果已经过了目标日期，停止查询
                if issue.updated_at < start_date:
                    break
                    
                # 限制数量
                if len(issues) >= 100:
                    break
            
            logger.info(f"获取到 {len(issues)} 个 Issues")
            return issues
            
        except GithubException as e:
            logger.error(f"获取仓库 {repo_name} 的 Issues 失败: {e}")
            raise
    
    def get_daily_pull_requests(self, repo_name: str, date: datetime = None) -> List[Dict]:
        """获取指定日期的 Pull Requests 列表
        
        Args:
            repo_name: 仓库名称，格式为 owner/repo
            date: 目标日期，默认为当天
        
        Returns:
            Pull Requests 列表
        """
        if date is None:
            date = datetime.now(timezone.utc)
        
        # 获取指定日期的起始和结束时间（使用 UTC 时区）
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        logger.info(f"正在获取仓库 {repo_name} 在 {date.strftime('%Y-%m-%d')} 的 Pull Requests...")
        
        try:
            repo = self.github.get_repo(repo_name)
            prs = []
            
            # 获取在指定日期更新或创建的 PRs
            for pr in repo.get_pulls(state='all', sort='updated', direction='desc'):
                # 检查是否在目标日期范围内创建或更新
                created_in_range = start_date <= pr.created_at < end_date
                updated_in_range = start_date <= pr.updated_at < end_date
                
                if created_in_range or updated_in_range:
                    prs.append({
                        'number': pr.number,
                        'title': pr.title,
                        'state': pr.state,
                        'author': pr.user.login if pr.user else 'Unknown',
                        'created_at': pr.created_at.isoformat(),
                        'updated_at': pr.updated_at.isoformat(),
                        'merged': pr.merged,
                        'merged_at': pr.merged_at.isoformat() if pr.merged_at else None,
                        'body': pr.body or '',
                        'additions': pr.additions,
                        'deletions': pr.deletions,
                        'changed_files': pr.changed_files,
                        'url': pr.html_url,
                        'is_new': created_in_range  # 标记是否为新创建
                    })
                
                # 如果已经过了目标日期，停止查询
                if pr.updated_at < start_date:
                    break
                    
                # 限制数量
                if len(prs) >= 100:
                    break
            
            logger.info(f"获取到 {len(prs)} 个 Pull Requests")
            return prs
            
        except GithubException as e:
            logger.error(f"获取仓库 {repo_name} 的 Pull Requests 失败: {e}")
            raise
    
    def export_daily_progress(self, repo_name: str, issues: List[Dict], 
                             pull_requests: List[Dict], date: datetime = None,
                             output_dir: str = "data/daily_progress") -> str:
        """将每日进展导出为 Markdown 文件
        
        Args:
            repo_name: 仓库名称
            issues: Issues 列表
            pull_requests: Pull Requests 列表
            date: 日期，默认为当天
            output_dir: 输出目录
        
        Returns:
            导出的文件路径
        """
        if date is None:
            date = datetime.now()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名：repo_name_YYYY-MM-DD.md
        repo_safe_name = repo_name.replace('/', '_')
        date_str = date.strftime('%Y-%m-%d')
        filename = f"{repo_safe_name}_{date_str}.md"
        filepath = os.path.join(output_dir, filename)
        
        # 生成 Markdown 内容
        content = self._generate_progress_markdown(repo_name, issues, pull_requests, date)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"每日进展已导出到: {filepath}")
        return filepath
    
    def _generate_progress_markdown(self, repo_name: str, issues: List[Dict], 
                                    pull_requests: List[Dict], date: datetime) -> str:
        """生成每日进展的 Markdown 内容"""
        date_str = date.strftime('%Y-%m-%d')
        
        content = f"""# {repo_name} 每日进展

**日期**: {date_str}  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 概览

- **Issues 总数**: {len(issues)}
  - 新增: {sum(1 for i in issues if i.get('is_new'))}
  - 更新: {sum(1 for i in issues if not i.get('is_new'))}
  - 开放: {sum(1 for i in issues if i.get('state') == 'open')}
  - 关闭: {sum(1 for i in issues if i.get('state') == 'closed')}

- **Pull Requests 总数**: {len(pull_requests)}
  - 新增: {sum(1 for pr in pull_requests if pr.get('is_new'))}
  - 更新: {sum(1 for pr in pull_requests if not pr.get('is_new'))}
  - 开放: {sum(1 for pr in pull_requests if pr.get('state') == 'open')}
  - 已合并: {sum(1 for pr in pull_requests if pr.get('merged'))}
  - 已关闭: {sum(1 for pr in pull_requests if pr.get('state') == 'closed' and not pr.get('merged'))}

---

## 🐛 Issues

"""
        
        if not issues:
            content += "*今日无 Issues 更新*\n\n"
        else:
            # 按照新增和更新分组
            new_issues = [i for i in issues if i.get('is_new')]
            updated_issues = [i for i in issues if not i.get('is_new')]
            
            if new_issues:
                content += "### 🆕 新增 Issues\n\n"
                for issue in new_issues:
                    labels = ', '.join([f"`{label}`" for label in issue.get('labels', [])])
                    content += f"#### #{issue['number']} {issue['title']}\n\n"
                    content += f"- **状态**: {issue['state']}\n"
                    content += f"- **创建者**: @{issue['author']}\n"
                    content += f"- **标签**: {labels if labels else '无'}\n"
                    content += f"- **链接**: {issue['url']}\n"
                    if issue.get('body'):
                        # 限制描述长度
                        body = issue['body'][:300] + '...' if len(issue['body']) > 300 else issue['body']
                        content += f"- **描述**: {body}\n"
                    content += "\n"
            
            if updated_issues:
                content += "### 🔄 更新的 Issues\n\n"
                for issue in updated_issues:
                    labels = ', '.join([f"`{label}`" for label in issue.get('labels', [])])
                    content += f"#### #{issue['number']} {issue['title']}\n\n"
                    content += f"- **状态**: {issue['state']}\n"
                    content += f"- **创建者**: @{issue['author']}\n"
                    content += f"- **标签**: {labels if labels else '无'}\n"
                    content += f"- **评论数**: {issue.get('comments', 0)}\n"
                    content += f"- **链接**: {issue['url']}\n"
                    content += "\n"
        
        content += "---\n\n## 🔀 Pull Requests\n\n"
        
        if not pull_requests:
            content += "*今日无 Pull Requests 更新*\n\n"
        else:
            # 按照新增和更新分组
            new_prs = [pr for pr in pull_requests if pr.get('is_new')]
            updated_prs = [pr for pr in pull_requests if not pr.get('is_new')]
            
            if new_prs:
                content += "### 🆕 新增 Pull Requests\n\n"
                for pr in new_prs:
                    status_emoji = "✅" if pr.get('merged') else "🔄" if pr.get('state') == 'open' else "❌"
                    content += f"#### {status_emoji} #{pr['number']} {pr['title']}\n\n"
                    content += f"- **状态**: {pr['state']}"
                    if pr.get('merged'):
                        content += " (已合并)"
                    content += "\n"
                    content += f"- **创建者**: @{pr['author']}\n"
                    content += f"- **代码变更**: +{pr.get('additions', 0)} -{pr.get('deletions', 0)}\n"
                    content += f"- **改动文件**: {pr.get('changed_files', 0)}\n"
                    content += f"- **链接**: {pr['url']}\n"
                    if pr.get('body'):
                        # 限制描述长度
                        body = pr['body'][:300] + '...' if len(pr['body']) > 300 else pr['body']
                        content += f"- **描述**: {body}\n"
                    content += "\n"
            
            if updated_prs:
                content += "### 🔄 更新的 Pull Requests\n\n"
                for pr in updated_prs:
                    status_emoji = "✅" if pr.get('merged') else "🔄" if pr.get('state') == 'open' else "❌"
                    content += f"#### {status_emoji} #{pr['number']} {pr['title']}\n\n"
                    content += f"- **状态**: {pr['state']}"
                    if pr.get('merged'):
                        content += " (已合并)"
                    content += "\n"
                    content += f"- **创建者**: @{pr['author']}\n"
                    content += f"- **代码变更**: +{pr.get('additions', 0)} -{pr.get('deletions', 0)}\n"
                    content += f"- **改动文件**: {pr.get('changed_files', 0)}\n"
                    content += f"- **链接**: {pr['url']}\n"
                    content += "\n"
        
        content += "---\n\n*本报告由 GitHub Sentinel 自动生成*\n"
        
        return content

