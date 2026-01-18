# 变更日志

## [0.1] - 2026-01-18

### 新增
- 🎮 交互式命令行界面 (Interactive Shell)
  - 使用 `python -m src.main interactive` 进入
  - 支持 `add`, `list`, `update`, `remove` 等命令
- ⚡ 即时检查功能
  - 使用 `check` 命令无需订阅即可检查任意仓库
  - 支持单仓库更新 `update [repo]`
- 🛡️ 增强的 GitHub 客户端
  - 支持匿名访问（无 Token 模式）
  - 自动处理 Rate Limit 警告
- 🔧 依赖优化
  - 移除不必要的 `smtplib-ssl` 依赖

### Release Notes (English)

**New Features**
- 🎮 **Interactive CLI**: New `interactive` command for REPL environment
- ⚡ **Instant Check**: Check any repo without subscription using `check` command
- 🛡️ **Enhanced Client**: Support anonymous access (no token)
- 🔧 **Optimization**: Dependencies cleanup

## [0.0.1] - 2026-01-18

### 新增
- ✨ 项目初始化和基础框架搭建
- 🔧 GitHub API 客户端实现，支持获取仓库更新
  - 提交记录 (Commits)
  - Pull Requests
  - Issues
  - Releases
- 📝 订阅管理系统
  - 添加/移除/列出订阅
  - 订阅数据持久化
  - 更新记录保存
- 🤖 AI 驱动的报告生成
  - 支持 OpenAI GPT-4
  - 支持 Anthropic Claude
  - 基础 Markdown 报告模板
- 📬 通知系统
  - 邮件通知（SMTP）
  - Webhook 通知
- ⏰ 任务调度器
  - 每日定时更新
  - 每周定时更新
- 💾 SQLite 数据库存储
- 🎨 命令行界面（CLI）
  - `subscribe add/remove/list` - 订阅管理
  - `update` - 手动触发更新
  - `start` - 启动定时任务
  - `init` - 初始化项目
- 🧪 单元测试框架
- 📚 完整的项目文档

### 技术栈
- Python 3.8+
- PyGithub - GitHub API 封装
- OpenAI/Anthropic - AI 报告生成
- APScheduler - 任务调度
- SQLite - 数据存储
- Click - CLI 框架
- Rich - 终端美化
- Loguru - 日志管理

### 文档
- README.md - 项目介绍和使用指南
- LICENSE - MIT 许可证
- config/config.yaml.example - 配置文件示例
