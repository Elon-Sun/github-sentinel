"""
GitHub API 客户端
"""

from github import Github, GithubException
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger


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
