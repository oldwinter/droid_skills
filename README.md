# Droid 内置扩展

从 `droid` CLI 二进制文件 (`/opt/homebrew/bin/droid`, Mach-O arm64) 中提取。

总计：**23 个提取的 skill**，分布在 9 个类别中。

## 类别分解

### automation/
浏览器、终端和桌面自动化 skill。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `agent-browser.md` | 19 KB | 500 | 通过 Chrome DevTools 协议自动化浏览器和 Electron 应用（VS Code, Slack, Discord, Figma, Notion, Spotify） |
| `tuistory.md` | 14 KB | 293 | 类似于 Playwright 的 TUI 测试框架 —— 确定性启动、键盘输入、尺寸检查、证据捕获 |
| `figma-mcp-helper.md` | 26 KB | 57 | 促进 Figma MCP 集成 —— 检测 Figma URL 和图像并指导安装 |

### documents/
办公文档生成 skill。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `excel.md` | 7 KB | 156 | 生成精美的 Excel 表格 (.xlsx) |
| `pdf-document.md` | 4 KB | 106 | 生成精美的 PDF 文档（报告、发票、简历、信件） |
| `powerpoint.md` | 4 KB | 114 | 生成精美的 PowerPoint 演示文稿（幻灯片、路演幻灯片） |

### incident/
事故响应和根本原因分析 skill。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `incident.md` | 24 KB | 180 | 事件根本原因分析手册 — 识别警报类型，验证工具/认证，逐步进行根本原因分析 |

### installers/
CI/CD 配置和安装 skill。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `install-code-review.md` | 51 KB | 1025 | 在 GitHub/GitLab 上安装自动化代码审查（单个仓库或组织级别） |
| `install-triage.md` | 21 KB | 267 | 构建计划的 Slack 问题处理自动化机器人 |
| `install-wiki.md` | 4 KB | 118 | 安装 CI 行动，每推送一次自动刷新 Wiki |

### missions/
Factory Missions 编排 skill（规划、工人定义、操作手册）。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `mission-planning.md` | 116 KB | 1153 | 引导协调器在与用户规划阶段进行交互 |
| `define-mission-skills.md` | 93 KB | 856 | 引导协调器设计工作类型及其 skill |
| `refactoring-playbook.md` | 37 KB | 351 | 代码现代化、架构迁移、大规模重构的作业指南 |
| `tui-application-playbook.md` | 30 KB | 148 | TUI 应用程序任务的作业指南——具有交互式界面的 CLI 工具 |

### qa/
质量保证设置和自动化。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `install-qa.md` | 43 KB | 771 | 使用模块化子 skill、CI 工作流和报告模板设置自动化 QA 测试 |

### review/
代码审查和分析 skill。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `review.md` | 17 KB | 298 | 审查代码更改并识别高置信度、可操作的错误 |
| `security-review.md` | 27 KB | 365 | 使用 STRIDE、OWASP Top 10、OWASP LLM Top 10 和供应链分析的安全重点代码审查 |
| `deep-security-review.md` | 187 KB | 2754 | 以正确性和深度为先的安全审计，采用异构多模型 jury、3-pass 基础层和条件升级层 |
| `simplify.md` | 4 KB | 53 | 审查已更改的代码以确保重用、质量和效率，然后修复发现的问题 |

### session/
会话管理和导航。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `session-navigation.md` | 4 KB | 122 | 导航、搜索和管理 Droid 会话——列出、搜索历史、恢复、获取详情 |

### wiki/
自动生成、浏览 Wiki 和生成视频的 skill。

| 文件 | 大小 | 行数 | 描述 |
|------|------|-------|-------------|
| `wiki.md` | 79 KB | 1410 | 生成全面的代码库文档（包含子 agent 委派的完整生成流水线） |
| `wiki-video-gen.md` | 22 KB | 430 | 为仓库 Wiki 生成带有 Factory 品牌的 HyperFrames 视频概述 |
| `browse-wiki.md` | 6 KB | 148 | 搜索和阅读 Wiki 文档 — `droid wiki-read` / `droid wiki-search` 命令 |

---

## 外部依赖关系

一些 skill 依赖于外部 CLI 工具。请参阅 **[dependencies.md](dependencies.md)** 以获取完整列表，包括捆绑工具 (`agent-browser`, `ripgrep`) 和按需安装工具 (`tuistory`)。

`tools/` 目录包含 `agent_browser` 的 LLM 函数调用模式 — 唯一内置工具以 Anthropic 风格的 JSON 函数定义格式存储。核心工具（读取、编辑、执行等）在 TypeScript 中程序化定义，而不是嵌入式 JSON。

---

## 不可提取 (程序化 / 背景)

这些 skill 在系统提醒中被提及为可用 skill，但 **未以独立 YAML skill 定义形式存储** 在二进制文件中。它们可能通过程序化定义、捆绑在其他 skill 内或动态生成。

### droid-control 工作流 skill（不会直接调用）

这些是支持 `droid-control` 自动化 skill 的后台 skill：

- `droid-control` — 控制终端 TUI 和 Web/Electron 应用程序进行测试、演示、质量保证和计算机使用任务
- `capture` — 终端和浏览器会话的录制生命周期
- `verify` — 与承诺交付成果的验证
- `droid-cli` — Droid CLI 目标模式、快捷方式和启动助手
- `compose` — 使用 Remotion 进行视频组装 — 标题卡、布局、过渡效果、特效
- `pty-capture` — 从真实终端仿真器捕获基础事实字节序列
- `desktop-control` — 桌面控制驱动机制，通过 trycua cua-driver 对原生 GUI 应用程序进行自动化
- `showcase` — 使用 Remotion 动画和品牌背景增强视频的视觉效果
- `true-input` — 通过无头 Wayland 组合器对真实终端仿真器进行真输入驱动机制

### 其他不可提取 skill

- `handoff` — 将当前对话精简为一份交接文档，供其他 agent 接手
- `grill-with-docs` — 一个挑战你的计划与现有领域模型对比的烤肉会话

### 自定义 droid（子 agent）

这些是存储在 `.factory/droids/` 或 `~/.factory/droids/` 中的自定义 droid 配置，并非内置于二进制文件：

- `worker` — 通用任务分派代理 droid
- `scrutiny-feature-reviewer` — 在任务验证期间对单一功能进行代码审查
- `user-testing-flow-validator` — 通过指定的合约界面测试验证合约断言

---

## 提取方法

这些 skill 通过以下方式从 `droid` 二进制文件中提取：

1. **模板字面量格式**（16 个 skill）：`var <X>=`---\nname: <name>\n...`;var <NEXT>`
   - 通过搜索 `var <X>=`---` 字节模式找到
   - 边界由 JS 打包文件中的下一个变量赋值确定

2. **转义字符串格式**（1 个 skill）：`var _si="---\nname: browse-wiki\n...";var Bsi=...`
   - 通过搜索 `"---\nname: browse-wiki` 找到

3. **JSON 元数据 + 变量引用**（6 个 skill）：`{metadata:{name:"<name>",description:"..."},systemPrompt:<VAR>}`
   - 将 `<VAR>` 引用解析为捆绑包中其他位置的模板字面量赋值
