# Droid Built-in Addins 中文翻译档案

## 仓库与基线

- 中文仓库：`oldwinter/droid_skills`
- 上游仓库：无
- 当前英文基线：`c8da2b1`（初始提取版本）
- 内容来源：本机 `droid` CLI 二进制中提取的 23 个内置 skill

这个仓库不是 GitHub upstream 的 fork。后续维护以新的 Droid 二进制提取结果为输入，先对比当前英文基线，再把新增或变化的用户可见内容重新中文化。

## 必须翻译

- 根目录 `README.md` 与 `dependencies.md` 的介绍、分类、依赖和提取说明。
- 23 个 skill 的 frontmatter `description`、标题、步骤、约束、决策说明、提示语和面向用户的输出要求。
- Markdown 表格中的用户可见说明。

## 必须保留

- frontmatter key、`name`、`version`、布尔值和 skill slug。
- 代码围栏及围栏内的命令、模板、配置、schema、脚本和示例。
- 内联代码、命令名、参数、环境变量、配置 key、文件路径、URL、锚点和包名。
- Factory、Droid、GitHub、GitLab、Figma、Slack、Playwright、HyperFrames、Remotion 等产品名。
- API、CLI、TUI、LLM、MCP、RCA、CI/CD、JSON、YAML、TypeScript、JavaScript 等缩写和技术名。
- 数字、版本号、阶段编号、阈值、严重级别和安全边界。

## 术语约定

| 英文 | 中文 | 说明 |
|---|---|---|
| agent | agent | 指 AI 执行单元时保留英文 |
| skill | skill | 指 Droid skill 实体时保留英文 |
| workflow | 工作流 | 命令名和文件名中保留原文 |
| prompt | 提示词 | prompt contract 中保留原文 |
| runtime | runtime | 指实际加载环境时保留英文 |
| upstream | 上游 | 本仓库当前无 upstream |
| fork | fork | GitHub 仓库关系语境保留英文 |
| code review | 代码审查 | 不使用“代码复习” |
| security review | 安全审查 | 保留 STRIDE、OWASP 等框架名 |
| wiki | Wiki | 产品能力或命令语境保留英文 |

## 验证要求

1. 全部 25 个 Markdown 文件包含中文用户入口，23 个 skill 的 frontmatter 可解析。
2. 与英文基线相比，代码围栏内容、frontmatter 非 `description` 字段、链接目标和内联技术契约不变。
3. 不存在翻译占位符、合并冲突标记或异常全角 Markdown 标记。
4. `git diff --check` 通过，Markdown 围栏成对闭合。
5. 对 README、安装/依赖说明、事件响应、安全审查和 Wiki 主流程进行人工抽样复核。
