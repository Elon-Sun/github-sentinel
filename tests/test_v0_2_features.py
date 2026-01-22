"""
v0.2 功能测试

测试每日进展和报告生成功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import os
import tempfile

from src.core.github_client import GitHubClient
from src.ai.report_generator import ReportGenerator


class TestDailyProgress(unittest.TestCase):
    """测试每日进展功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.repo_name = "test/repo"
        self.test_date = datetime(2026, 1, 18)
        
    @patch('src.core.github_client.Github')
    def test_get_daily_issues(self, mock_github):
        """测试获取每日 Issues"""
        # Mock GitHub Search API 响应
        mock_issue = MagicMock()
        mock_issue.created_at = datetime(2026, 1, 18, 10, 0, tzinfo=timezone.utc)
        mock_issue.updated_at = datetime(2026, 1, 18, 10, 0, tzinfo=timezone.utc)
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.state = "open"
        mock_issue.user.login = "testuser"
        mock_issue.comments = 0
        mock_issue.labels = []
        mock_issue.body = "Test body"
        mock_issue.html_url = "https://github.com/test/repo/issues/1"
        
        # Mock search_issues to return issues only for created query (not updated)
        def mock_search_issues(query, **kwargs):
            if "created:" in query and "is:issue" in query and "-created:" not in query:
                return [mock_issue]  # Return for created query
            else:
                return []  # Return empty for updated query
        
        mock_github.return_value.search_issues.side_effect = mock_search_issues
        
        # 创建客户端并测试
        client = GitHubClient("test_token")
        issues = client.get_daily_issues(self.repo_name, self.test_date)
        
        # 验证结果
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['number'], 1)
        self.assertEqual(issues[0]['title'], "Test Issue")
        self.assertTrue(issues[0]['is_new'])
    
    @patch('src.core.github_client.Github')
    def test_get_daily_pull_requests(self, mock_github):
        """测试获取每日 Pull Requests"""
        # Mock GitHub Search API 响应
        mock_pr = MagicMock()
        mock_pr.created_at = datetime(2026, 1, 18, 10, 0, tzinfo=timezone.utc)
        mock_pr.updated_at = datetime(2026, 1, 18, 10, 0, tzinfo=timezone.utc)
        mock_pr.number = 1
        mock_pr.title = "Test PR"
        mock_pr.state = "open"
        mock_pr.user.login = "testuser"
        mock_pr.body = "Test body"
        mock_pr.html_url = "https://github.com/test/repo/pull/1"
        
        # Mock the as_pull_request() method
        mock_full_pr = MagicMock()
        mock_full_pr.merged = False
        mock_full_pr.merged_at = None
        mock_full_pr.additions = 10
        mock_full_pr.deletions = 5
        mock_full_pr.changed_files = 2
        mock_pr.as_pull_request.return_value = mock_full_pr
        
        # Mock search_issues to return PRs only for created query (not updated)
        def mock_search_issues(query, **kwargs):
            if "created:" in query and "is:pr" in query and "-created:" not in query:
                return [mock_pr]  # Return for created query
            else:
                return []  # Return empty for updated query
        
        mock_github.return_value.search_issues.side_effect = mock_search_issues
        
        # 创建客户端并测试
        client = GitHubClient("test_token")
        prs = client.get_daily_pull_requests(self.repo_name, self.test_date)
        
        # 验证结果
        self.assertEqual(len(prs), 1)
        self.assertEqual(prs[0]['number'], 1)
        self.assertEqual(prs[0]['title'], "Test PR")
        self.assertTrue(prs[0]['is_new'])
        self.assertEqual(prs[0]['additions'], 10)
    
    @patch('src.core.github_client.Github')
    def test_export_daily_progress(self, mock_github):
        """测试导出每日进展"""
        client = GitHubClient("test_token")
        
        # 准备测试数据
        issues = [
            {
                'number': 1,
                'title': 'Test Issue',
                'state': 'open',
                'author': 'testuser',
                'is_new': True,
                'labels': ['bug'],
                'url': 'https://github.com/test/repo/issues/1',
                'body': 'Test description',
                'comments': 0
            }
        ]
        
        prs = [
            {
                'number': 1,
                'title': 'Test PR',
                'state': 'open',
                'author': 'testuser',
                'is_new': True,
                'merged': False,
                'additions': 10,
                'deletions': 5,
                'changed_files': 2,
                'url': 'https://github.com/test/repo/pull/1',
                'body': 'Test PR description'
            }
        ]
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = client.export_daily_progress(
                self.repo_name,
                issues,
                prs,
                self.test_date,
                output_dir=tmpdir
            )
            
            # 验证文件已创建
            self.assertTrue(os.path.exists(filepath))
            
            # 验证文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('test/repo', content)
                self.assertIn('Test Issue', content)
                self.assertIn('Test PR', content)
                self.assertIn('2026-01-18', content)


class TestReportGeneration(unittest.TestCase):
    """测试报告生成功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.repo_name = "test/repo"
        
        # Mock 配置
        self.mock_config = Mock()
        self.mock_config.get = Mock(side_effect=lambda key, default=None: {
            "ai.provider": "openai",
            "ai.api_key": None,  # 不使用真实 API
            "ai.model": "gpt-4",
            "ai.language": "zh-CN",
            "ai.max_tokens": 2000,
        }.get(key, default))
    
    def test_generate_daily_report_without_ai(self):
        """测试不使用 AI 生成报告"""
        generator = ReportGenerator(self.mock_config)
        
        # 创建临时进展文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# test/repo 每日进展\n\n这是测试内容")
            progress_file = f.name
        
        try:
            # 使用临时目录
            with tempfile.TemporaryDirectory() as tmpdir:
                report_file = generator.generate_daily_report(
                    self.repo_name,
                    progress_file,
                    output_dir=tmpdir
                )
                
                # 验证报告已创建
                self.assertTrue(os.path.exists(report_file))
                
                # 验证报告内容
                with open(report_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn('test/repo', content)
        finally:
            # 清理临时文件
            if os.path.exists(progress_file):
                os.unlink(progress_file)
    
    def test_batch_generate_reports(self):
        """测试批量生成报告"""
        generator = ReportGenerator(self.mock_config)
        
        # 创建临时进展文件
        with tempfile.TemporaryDirectory() as progress_dir:
            with tempfile.TemporaryDirectory() as report_dir:
                # 创建测试进展文件
                repos = ["test/repo1", "test/repo2"]
                date = datetime(2026, 1, 18)
                
                for repo in repos:
                    repo_safe = repo.replace('/', '_')
                    progress_file = os.path.join(
                        progress_dir, 
                        f"{repo_safe}_2026-01-18.md"
                    )
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        f.write(f"# {repo} 每日进展\n\n测试内容")
                
                # 批量生成报告
                report_files = generator.batch_generate_reports(
                    repos,
                    date=date,
                    progress_dir=progress_dir,
                    output_dir=report_dir
                )
                
                # 验证结果
                self.assertEqual(len(report_files), 2)
                for report_file in report_files:
                    self.assertTrue(os.path.exists(report_file))


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.repo_name = "test/repo"
        self.test_date = datetime(2026, 1, 18)
    
    @patch('src.core.github_client.Github')
    def test_full_workflow(self, mock_github):
        """测试完整工作流程"""
        # Mock GitHub Search API
        mock_issue = MagicMock()
        mock_issue.created_at = datetime(2026, 1, 18, 10, 0, tzinfo=timezone.utc)
        mock_issue.updated_at = datetime(2026, 1, 18, 10, 0, tzinfo=timezone.utc)
        mock_issue.number = 1
        mock_issue.title = "Integration Test Issue"
        mock_issue.state = "open"
        mock_issue.user.login = "testuser"
        mock_issue.comments = 0
        mock_issue.labels = []
        mock_issue.body = "Test body"
        mock_issue.html_url = "https://github.com/test/repo/issues/1"
        
        # Mock search_issues to return issues for created query and empty for others
        def mock_search_issues(query, **kwargs):
            if "created:" in query and "is:issue" in query and "-created:" not in query:
                return [mock_issue]  # Return issues for created query
            else:
                return []  # Return empty for updated queries and PR queries
        
        mock_github.return_value.search_issues.side_effect = mock_search_issues
        
        # Mock 配置
        mock_config = Mock()
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "ai.provider": "openai",
            "ai.api_key": None,
            "ai.model": "gpt-4",
            "ai.language": "zh-CN",
            "ai.max_tokens": 2000,
        }.get(key, default))
        
        # 创建客户端和生成器
        client = GitHubClient("test_token")
        generator = ReportGenerator(mock_config)
        
        repo_name = "test/repo"
        test_date = datetime(2026, 1, 18)
        
        with tempfile.TemporaryDirectory() as progress_dir:
            with tempfile.TemporaryDirectory() as report_dir:
                # 步骤 1: 获取每日数据
                issues = client.get_daily_issues(repo_name, test_date)
                prs = client.get_daily_pull_requests(repo_name, test_date)
                
                # 步骤 2: 导出进展
                progress_file = client.export_daily_progress(
                    repo_name,
                    issues,
                    prs,
                    test_date,
                    output_dir=progress_dir
                )
                
                # 步骤 3: 生成报告
                report_file = generator.generate_daily_report(
                    repo_name,
                    progress_file,
                    output_dir=report_dir
                )
                
                # 验证所有文件都已创建
                self.assertTrue(os.path.exists(progress_file))
                self.assertTrue(os.path.exists(report_file))
                
                # 验证文件内容
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_content = f.read()
                    self.assertIn("Integration Test Issue", progress_content)
                
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                    self.assertIn("test/repo", report_content)
    
    @patch('src.core.github_client.Github')
    def test_custom_date_range_fetching(self, mock_github):
        """测试自定义日期范围获取功能"""
        # Mock GitHub Search API 响应
        mock_issue = MagicMock()
        mock_issue.created_at = datetime(2026, 1, 13, 10, 0, tzinfo=timezone.utc)  # 不在范围内
        mock_issue.updated_at = datetime(2026, 1, 16, 10, 0, tzinfo=timezone.utc)  # 在范围内
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.state = "open"
        mock_issue.user.login = "testuser"
        mock_issue.comments = 0
        mock_issue.labels = []
        mock_issue.body = "Test body"
        mock_issue.html_url = "https://github.com/test/repo/issues/1"
        
        # Mock search_issues to return issues only for updated query (not created)
        def mock_search_issues(query, **kwargs):
            if "updated:" in query and "is:issue" in query and "-created:" in query:
                return [mock_issue]  # Return for updated query
            else:
                return []  # Return empty for created query
        
        mock_github.return_value.search_issues.side_effect = mock_search_issues
        
        # 创建客户端并测试日期范围
        client = GitHubClient("test_token")
        start_date = datetime(2026, 1, 14)
        end_date = datetime(2026, 1, 17)
        
        issues = client.get_daily_issues(self.repo_name, start_date=start_date, end_date=end_date)
        
        # 验证结果
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['number'], 1)
        self.assertTrue(issues[0]['is_updated'])  # 应该标记为更新
    
    @patch('src.core.github_client.Github')
    def test_export_with_date_range_filename(self, mock_github):
        """测试日期范围文件名导出"""
        client = GitHubClient("test_token")
        
        # 准备测试数据
        issues = []
        prs = []
        start_date = datetime(2026, 1, 14)
        end_date = datetime(2026, 1, 17)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 导出进展
            progress_file = client.export_daily_progress(
                self.repo_name,
                issues,
                prs,
                start_date=start_date,
                end_date=end_date,
                output_dir=temp_dir
            )
            
            # 验证文件名包含日期范围
            expected_filename = "test_repo_2026-01-14_to_2026-01-17.md"
            self.assertTrue(progress_file.endswith(expected_filename))
            
            # 验证项目文件夹结构
            self.assertIn("test_repo", progress_file)
            
            # 验证文件存在
            self.assertTrue(os.path.exists(progress_file))


if __name__ == '__main__':
    unittest.main()
