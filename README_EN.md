# GitHub Sentinel 🔍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[简体中文](README.md) | **English**

An intelligent, open-source AI Agent tool designed for developers and project managers to automatically track and summarize the latest updates from GitHub repositories.

## ✨ Features

- 🔔 **Smart Subscription Management**: Easily subscribe to and manage multiple GitHub repositories.
- 📊 **AI-Powered Reporting**: Automatically generate readable summaries and reports using AI.
- ⏰ **Scheduled Updates**: Support daily or weekly automatic updates.
- 📬 **Multi-Channel Notifications**: Support Email, Webhooks, and more.
- 📈 **Trend Analysis**: Track project activity and development trends.
- 🎯 **Smart Filtering**: Filter important updates to reduce information noise.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Elon-Sun/github-sentinel.git
cd github-sentinel

# Install dependencies
pip install -r requirements.txt

# Or use setup.py
pip install -e .
```

### Configuration

1. Copy the configuration template:
```bash
cp config/config.yaml.example config/config.yaml
```

2. Edit `config/config.yaml` with your settings:
```yaml
github:
  token: "your_github_token"
  
ai:
  provider: "openai"  # or anthropic
  api_key: "your_api_key"
  
notification:
  email:
    enabled: true
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    
schedule:
  interval: "daily"  # daily or weekly
```

### Usage

**Interactive Mode (Recommended)**

```bash
# Enter interactive shell
python -m src.main interactive

# In interactive mode:
(sentinel) check langchain-ai/langchain  # Instant check
(sentinel) add microsoft/vscode          # Subscribe
(sentinel) list                          # List subscriptions
```

**Command Line Usage**

```bash
# Add subscription
python -m src.main subscribe add owner/repo

# List all subscriptions
python -m src.main subscribe list

# Manual update
python -m src.main update

# Start scheduled task
python -m src.main start
```

## 📁 Project Structure

```
github-sentinel/
├── config/              # Configuration files
├── src/                 # Source code
│   ├── core/           # Core modules
│   ├── ai/             # AI report generation
│   ├── notifier/       # Notification system
│   └── storage/        # Database storage
├── data/               # Data files
├── logs/               # Log files
└── tests/              # Test cases
```

## 🛠️ Tech Stack

- **Python 3.8+**: Core language
- **PyGithub**: GitHub API interaction
- **OpenAI/Anthropic**: AI report generation
- **APScheduler**: Task scheduling
- **SQLite**: Lightweight storage
- **Jinja2**: Template engine

## 📝 Roadmap

- [x] v0.0.1: Basic framework and core features
- [x] v0.1.0: Interactive CLI & Instant Check
- [ ] v0.2.0: Web Console Interface
- [ ] v0.3.0: More notification channels (Slack, Discord)
- [ ] v1.0.0: Production ready

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Thanks to all developers contributing to the open source community!

---

**Made with ❤️ for the Developer Community**
