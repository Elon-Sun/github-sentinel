# GitHub Sentinel Web UI 使用指南

## 🌐 启动 Web 界面

### 方式 1: 使用命令行
```bash
python -m src.main web
```

### 方式 2: 使用快速启动脚本
```bash
python run_web.py
```

### 自定义配置
```bash
# 指定端口
python -m src.main web --port 8080

# 指定主机地址
python -m src.main web --host 127.0.0.1

# 创建公共分享链接（用于远程访问）
python -m src.main web --share
```

## 📋 功能说明

### 1. 订阅管理 📚

**添加订阅**
- 输入仓库名称（格式：owner/repo）
- 选择更新频率（daily 或 weekly）
- 点击"添加订阅"按钮

**移除订阅**
- 输入要移除的仓库名称
- 点击"移除订阅"按钮

**查看订阅列表**
- 点击"刷新列表"查看当前所有订阅
- 显示订阅状态、订阅时间、最后检查时间

### 2. 即时检查 🔎

快速检查任意 GitHub 仓库的最新动态：

1. 输入仓库名称（例如：langchain-ai/langchain）
2. 选择查询天数（1-30天）
3. 点击"检查更新"
4. 查看 AI 生成的更新报告

**适用场景**：
- 快速了解某个项目的最新进展
- 临时查看不想订阅的仓库
- 评估是否值得订阅某个项目

### 3. 自定义报告 📅

生成指定日期范围的详细 AI 分析报告：

1. 输入仓库名称
2. 设置开始日期（YYYY-MM-DD）
3. 设置结束日期（YYYY-MM-DD）
4. 点击"生成报告"

**报告内容包括**：
- Issues 新增和更新情况
- Pull Requests 提交和合并情况
- AI 智能分析和总结
- 项目活跃度评估

**文件保存位置**：
- 进展文件：`data/daily_progress/{project_name}/`
- 报告文件：`data/reports/{project_name}/`

### 4. 仓库信息 ℹ️

查看 GitHub 仓库的基本统计信息：

1. 输入仓库名称
2. 点击"获取信息"

**显示内容**：
- ⭐ Stars 数量
- 🍴 Forks 数量
- 🐛 Open Issues 数量
- 💻 主要编程语言
- 🔄 最后更新时间
- 📝 仓库描述

## 💡 使用技巧

### 常见操作流程

**初次使用**：
1. 在"订阅管理"页面添加感兴趣的仓库
2. 定期查看订阅列表中的仓库更新
3. 使用"自定义报告"生成详细分析

**临时查询**：
1. 使用"即时检查"快速查看任意仓库
2. 无需订阅，立即获得 AI 报告

**深度分析**：
1. 使用"自定义报告"选择具体时间段
2. 生成包含完整 Issues 和 PRs 的详细报告
3. AI 会自动分析并总结关键信息

### 快捷键

- `Tab`: 在输入框间切换
- `Enter`: 在输入框中按回车触发按钮
- `Ctrl+C`: 在终端中停止 Web 服务

## 🔧 配置说明

Web 界面使用与命令行相同的配置文件：`config/config.yaml`

**关键配置项**：
```yaml
github:
  token: "your_github_token_here"  # GitHub API Token

ai:
  provider: "deepseek"  # openai, anthropic, deepseek
  api_key: "your_api_key"
  model: "deepseek-chat"
  language: "zh-CN"
```

## ⚠️ 注意事项

1. **GitHub Token**: 必须配置有效的 GitHub Token 才能使用
2. **AI 功能**: 需要配置 AI API Key 才能生成智能报告，否则只能生成基础报告
3. **访问权限**: 默认监听 0.0.0.0，可从局域网访问，注意安全性
4. **端口占用**: 默认使用 7860 端口，如被占用可使用 `--port` 参数修改

## 🐛 常见问题

**Q: 页面无法访问？**
A: 检查防火墙设置，确保端口未被占用

**Q: GitHub API Rate Limit?**
A: 使用有效的 GitHub Token 可提高限额到 5000 次/小时

**Q: AI 报告生成失败？**
A: 检查 AI API Key 配置是否正确，网络是否可访问 AI 服务

**Q: 报告保存在哪里？**
A: 
- 进展文件：`data/daily_progress/{project_name}/`
- 报告文件：`data/reports/{project_name}/`

## 📚 更多信息

- [完整文档](../README.md)
- [命令行使用](../README.md#命令使用)
- [配置说明](../README.md#配置)

---

Made with ❤️ by GitHub Sentinel
