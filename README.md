# GitHub Sentinel 🔍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个智能的开源 AI Agent 工具，专为开发者和项目管理人员设计，能够自动跟踪和汇总 GitHub 仓库的最新动态。

## ✨ 特性

- 🔔 **智能订阅管理**: 轻松订阅和管理多个 GitHub 仓库
- 📊 **AI 驱动报告**: 使用 AI 自动生成易读的更新摘要和报告
- ⏰ **定时获取**: 支持每日/每周自动获取仓库更新
- 📬 **多渠道通知**: 支持邮件、Webhook 等多种通知方式
- 📈 **趋势分析**: 跟踪项目活跃度和发展趋势
- 🎯 **智能过滤**: 过滤重要更新，减少信息噪音

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

### 使用

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

## 📁 项目结构

```
github-sentinel/
├── config/              # 配置文件
├── src/                 # 源代码
│   ├── core/           # 核心功能模块
│   ├── ai/             # AI 报告生成
│   ├── notifier/       # 通知系统
│   └── storage/        # 数据存储
├── data/               # 数据文件
├── logs/               # 日志文件
└── tests/              # 测试用例
```

## 🛠️ 技术栈

- **Python 3.8+**: 核心开发语言
- **PyGithub**: GitHub API 交互
- **OpenAI/Anthropic**: AI 报告生成
- **APScheduler**: 任务调度
- **SQLite**: 轻量级数据存储
- **Jinja2**: 报告模板生成

## 📝 开发计划

- [x] v0.0.1: 基础框架和核心功能
- [ ] v0.1.0: AI 报告生成优化
- [ ] v0.2.0: Web 控制台界面
- [ ] v0.3.0: 更多通知渠道（Slack, Discord）
- [ ] v1.0.0: 生产就绪版本

## 🤝 贡献

欢迎贡献代码、报告问题或提出新功能建议！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢所有为开源社区做出贡献的开发者们！

---

**Made with ❤️ for the Developer Community**
