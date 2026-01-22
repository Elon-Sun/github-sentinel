# 变更日志

## [0.3.0] - 2026-01-22

### 重大变更
- 🔍 **GitHub API 优化**: 从仓库方法切换到搜索 API
  - 使用 `github.search_issues()` 替代 `repo.get_issues()`
  - 支持高效的日期范围过滤查询
  - 解决大仓库查询性能问题和卡死问题

### 新增
- 📅 **自定义日期范围查询**
  - `get_daily_issues()` 和 `get_daily_pull_requests()` 支持 `start_date` 和 `end_date` 参数
  - 向后兼容：仍支持单个日期参数
  - 自动区分新建和更新的 Issues/PRs

- 📁 **项目文件夹组织**
  - 报告按项目分组：`data/reports/{project_name}/`
  - 进展文件按项目分组：`data/daily_progress/{project_name}/`
  - 更清晰的文件管理结构

- 🖥️ **新 CLI 命令**
  - `python -m src.main report REPO_NAME --start-date YYYY-MM-DD --end-date YYYY-MM-DD`
  - 支持自定义日期范围报告生成
  - 完整的参数验证和错误处理

### 改进
- ⚡ **性能提升**: 大幅改善大仓库查询速度
  - 避免遍历所有 Issues/PRs
  - 使用 GitHub 搜索 API 的日期过滤
  - 从可能卡死到秒级响应

- 📝 **文件名包含日期范围**
  - 导出文件格式：`{repo}_{start_date}_to_{end_date}.md`
  - 报告文件格式：`{repo}_report_{start_date}_to_{end_date}.md`
  - 更直观的文件命名

- 🧪 **测试完善**
  - 更新所有测试用例以匹配新的 Search API
  - 8/8 测试通过，包括新的日期范围功能
  - 改进的 Mock 设置和断言

### 技术细节
- 使用 GitHub Search API 查询语法：
  - 新建：`repo:{repo} is:issue created:{start}..{end}`
  - 更新：`repo:{repo} is:issue updated:{start}..{end} -created:{start}..{end}`
- 限制查询结果为 100 个条目以保证性能
- 自动处理时区转换（UTC）

## [0.2.1] - 2026-01-22

### 重大变更
- 🔄 **存储系统迁移**: 从 SQLite 迁移到 JSON 文件存储
  - 移除 `sqlalchemy` 依赖，使用轻量级 JSON 文件
  - 数据文件：`data/sentinel.json`
  - 提供迁移脚本：`migrate_to_json.py`
  - 更简单、更易于备份和版本控制

### 新增
- 📅 **定时报告生成任务**
  - 调度器自动生成每日/每周报告
  - 在更新仓库后 30 分钟自动执行
  - 支持批量处理所有订阅的仓库
  
- 🛠️ **迁移工具**
  - `migrate_to_json.py`: SQLite 到 JSON 的数据迁移脚本
  - `MIGRATION.md`: 完整的迁移指南和文档
  
- 🎨 **CLI 模块化**
  - 新增 `src/cli/` 模块
  - `subscription_commands.py`: 订阅管理命令
  - `interactive_shell.py`: 交互式 Shell 界面

### 改进
- ⚡ 简化依赖：移除重量级数据库依赖
- 📦 更小的安装包体积
- 🔍 更易于调试和数据检查
- 📝 完善的测试覆盖（8/8 测试通过）

### 配置变更
```yaml
database:
  type: "json"  # 之前: "sqlite"
  path: "data/sentinel.json"  # 之前: "data/sentinel.db"
```

### 迁移说明
如果您从 v0.2 升级，请运行：
```bash
python migrate_to_json.py
```

## [0.2] - 2026-01-18

### 新增
- 📊 **每日进展模块**
  - `get_daily_issues()`: 获取指定日期的 Issues 列表
  - `get_daily_pull_requests()`: 获取指定日期的 Pull Requests 列表
  - `export_daily_progress()`: 将每日进展导出为结构化的 Markdown 文件
  - 文件命名格式：`{项目名称}_{日期}.md`
  - 包含完整的元信息：状态、作者、标签、代码变更统计等
  - 自动区分新增和更新的内容
  
- 🤖 **AI 报告生成模块**
  - `generate_daily_report()`: 读取每日进展，使用 AI 生成正式报告
  - `batch_generate_reports()`: 批量生成多个仓库的报告
  - 支持 GPT-4 和 Claude 进行智能分析
  - 生成正式、专业的项目报告
  - 包含项目概览、核心进展、Issues/PR 分析、活跃度评估等
  
- 📁 **新增目录结构**
  - `data/daily_progress/`: 存储每日进展 Markdown 文件
  - `data/reports/`: 存储 AI 生成的报告
  - `examples/daily_report_example.py`: 功能使用示例
  - `docs/v0.2-features.md`: 详细功能文档
  
- 🧪 **测试覆盖**
  - 添加 v0.2 功能的单元测试
  - 添加集成测试验证完整工作流程

### 改进
- 📝 优化 Markdown 输出格式，增强可读性
- 🎯 AI 提示词优化，生成更专业的报告内容
- 📈 增加统计信息和数据分析
- 🔍 改进错误处理和日志记录

### Release Notes (English)

**New Features**
- 📊 **Daily Progress Module**: Track and export daily Issues and PRs to Markdown
- 🤖 **AI Report Generation**: Generate professional reports using GPT-4/Claude
- 📁 **Data Organization**: New directory structure for progress and reports
- 🧪 **Test Coverage**: Unit and integration tests for v0.2 features

**Improvements**
- Enhanced Markdown output formatting
- Optimized AI prompts for better report quality
- Added comprehensive statistics and analysis
- Improved error handling and logging

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
