# 变更日志

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
