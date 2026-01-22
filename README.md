# GitHub Sentinel 🔍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
**简体中文** | [English](README_EN.md)

一个智能的开源 AI Agent 工具，专为开发者和项目管理人员设计，能够自动跟踪和汇总 GitHub 仓库的最新动态。

## ✨ 特性

- 🔔 **智能订阅管理**: 轻松订阅和管理多个 GitHub 仓库
- 📊 **每日进展追踪** (v0.2): 自动获取并导出每日 Issues 和 Pull Requests
- 📅 **自定义日期范围查询** (v0.3): 支持任意时间段的数据查询和报告生成
- 📁 **项目文件夹组织** (v0.3): 报告按项目自动分组存放
- 🤖 **AI 驱动报告**: 使用 GPT-4/Claude 自动生成专业的项目报告
- ⏰ **定时获取**: 支持每日/每周自动获取仓库更新
- 📬 **多渠道通知**: 支持邮件、Webhook 等多种通知方式
- 📈 **趋势分析**: 跟踪项目活跃度和发展趋势
- 🎯 **智能过滤**: 过滤重要更新，减少信息噪音
- ⚡ **高性能查询** (v0.3): 优化 GitHub API 调用，支持大仓库快速查询

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/Elon-Sun/github-sentinel.git
cd github-sentinel

# 安装依赖
pip install -r requirements.txt

# 或使用 setup.py
pip install -e .
```

### 配置

1. 复制配置文件模板：
```bash
cp config/config.yaml.example config/config.yaml
```

2. 编辑 `config/config.yaml`，填入你的配置信息：
```yaml
github:
  token: "your_github_token"
  
ai:
  provider: "openai"  # 或其他 AI 提供商
  api_key: "your_api_key"
  
notification:
  email:
    enabled: true
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    
schedule:
  interval: "daily"  # daily 或 weekly
```

### 交互式模式（推荐）

```bash
# 进入交互式终端
python -m src.main interactive

# 在交互模式下:
(sentinel) check langchain-ai/langchain  # 即时检查更新
(sentinel) add microsoft/vscode          # 订阅仓库
(sentinel) list                          # 查看订阅
```

### 命令使用

```bash
# 添加订阅
python -m src.main subscribe add owner/repo

# 列出所有订阅
python -m src.main subscribe list

# 手动触发更新
python -m src.main update

# 启动定时任务
python -m src.main start
```

### v0.2 新功能：每日报告 (推荐)

```bash
# 运行每日报告示例
python examples/daily_report_example.py

# 或在 Python 代码中使用：
from src.core.github_client import GitHubClient
from src.ai.report_generator import ReportGenerator

# 获取每日数据并生成报告
github_client = GitHubClient("your_token")
issues = github_client.get_daily_issues("pytorch/pytorch")
prs = github_client.get_daily_pull_requests("pytorch/pytorch")

# 导出每日进展
progress_file = github_client.export_daily_progress("pytorch/pytorch", issues, prs)

# 生成 AI 报告
report_generator = ReportGenerator(config)
report_file = report_generator.generate_daily_report("pytorch/pytorch", progress_file)
```

### v0.3 新功能：自定义日期范围报告 (推荐)

```bash
# 生成指定日期范围的报告
python -m src.main report microsoft/playwright --start-date 2024-01-15 --end-date 2024-01-16

# 或在 Python 代码中使用：
from src.core.github_client import GitHubClient
from src.ai.report_generator import ReportGenerator

# 获取自定义日期范围的数据
github_client = GitHubClient("your_token")
issues = github_client.get_daily_issues("microsoft/playwright", 
                                       start_date="2024-01-15", 
                                       end_date="2024-01-16")
prs = github_client.get_daily_pull_requests("microsoft/playwright",
                                           start_date="2024-01-15", 
                                           end_date="2024-01-16")

# 导出到项目文件夹
progress_file = github_client.export_daily_progress("microsoft/playwright", issues, prs,
                                                   start_date="2024-01-15", 
                                                   end_date="2024-01-16")

# 生成 AI 报告（自动保存到项目文件夹）
report_generator = ReportGenerator(config)
report_file = report_generator.generate_daily_report("microsoft/playwright", progress_file,
                                                    start_date="2024-01-15", 
                                                    end_date="2024-01-16")
```

📚 **详细文档**: 
- [v0.2 功能说明](docs/v0.2-features.md)
- [v0.2 快速入门](docs/v0.2-quickstart.md)
- [v0.3 日期范围查询](docs/v0.3-date-range.md)

## 📁 项目结构

```
github-sentinel/
├── config/              # 配置文件
├── src/                 # 源代码
│   ├── core/           # 核心功能模块
│   │   └── github_client.py  # GitHub API (v0.3: 优化为搜索 API)
│   ├── ai/             # AI 报告生成
│   │   └── report_generator.py  # (v0.3: 支持项目文件夹组织)
│   ├── notifier/       # 通知系统
│   └── storage/        # 数据存储
├── data/               # 数据文件
│   ├── daily_progress/ # (v0.2/v0.3) 每日进展 Markdown 文件
│   │   └── {project}/  # (v0.3) 按项目分组
│   └── reports/        # (v0.2/v0.3) AI 生成的报告
│       └── {project}/  # (v0.3) 按项目分组
├── examples/           # 使用示例
│   └── daily_report_example.py  # (v0.2) 每日报告示例
├── docs/               # 文档
│   ├── v0.2-features.md       # (v0.2) 功能文档
│   ├── v0.2-quickstart.md     # (v0.2) 快速入门
│   └── v0.3-date-range.md     # (v0.3) 日期范围查询文档
├── logs/               # 日志文件
└── tests/              # 测试用例
```

## 🛠️ 技术栈

- **Python 3.8+**: 核心开发语言
- **PyGithub**: GitHub API 交互 (v0.3: 优化为搜索 API)
- **OpenAI/Anthropic**: AI 报告生成
- **APScheduler**: 任务调度
- **JSON**: 轻量级数据存储 (v0.2: 从 SQLite 迁移)
- **Jinja2**: 报告模板生成

## 📝 开发计划

- [x] v0.0.1: 基础框架和核心功能
- [x] v0.1.0: 交互式命令行与即时检查
- [x] v0.2.0: 每日进展追踪和 AI 报告生成
- [x] v0.3.0: 自定义日期范围查询和项目文件夹组织
- [ ] v0.4.0: Web 控制台界面
- [ ] v0.5.0: 更多通知渠道（Slack, Discord）
- [ ] v1.0.0: 生产就绪版本

## 🤝 贡献

欢迎贡献代码、报告问题或提出新功能建议！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢所有为开源社区做出贡献的开发者们！

---

**Made with ❤️ for the Developer Community**
