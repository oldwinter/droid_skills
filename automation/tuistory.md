---
name: tuistory
description: 自动化终端用户界面（TUI）测试。在需要启动、交互、测试或调试终端应用程序、捕获 TUI 快照或自动化终端输入时使用此功能。
---

# 使用 tuistory 进行 TUI 测试

tuistory 是一个类似于 Playwright 的框架，用于终端 UI。使用它进行确定性启动、按键输入、尺寸检查和证据捕获。

## 设置

确保 tuistory 可用：
```bash
which tuistory || (bun add -g tuistory || npm install -g tuistory)
tuistory --version
```

在使用高级标志之前，请检查已安装版本的命令界面:
```bash
tuistory --help
tuistory snapshot --help
tuistory screenshot --help
```

## 核心工作流（可靠路径）

1. 启动一个命名会话。
2. 等待空闲状态，然后快照。
3. 立即处理首次运行对话框。
4. 针对特定文本使用短而精确的等待。
5. 每次操作后进行快照。
6. 捕获屏幕截图作为视觉证明。
7. 完成时关闭会话。

```bash
tuistory launch "my-tui-command" -s app --cols 110 --rows 32
tuistory -s app wait-idle --timeout 8000
tuistory -s app snapshot --trim

# interact
tuistory -s app type "help"
tuistory -s app press enter
tuistory -s app wait "Usage" --timeout 8000
tuistory -s app snapshot --trim

# capture visual artifact
tuistory -s app screenshot --format png -o /tmp/app-usage.png

# cleanup
tuistory -s app close
```

## 关键输入规则（至关重要）

- 使用空格分隔的关键令牌，而不是引号组合键。
- 正确：`tuistory -s app press ctrl g`
- 错误：`tuistory -s app press "ctrl g"`
- 使用 `type` 用于文本和 `press` 用于控制/导航键。

常用按键：
```bash
tuistory -s app press enter
tuistory -s app press esc
tuistory -s app press ctrl c
tuistory -s app press ctrl g
```

## 等待策略（避免不稳定的长时间睡眠）

- 在触发重绘的交互后，优先使用 `wait-idle`。
- 对于异步里程碑，请优先使用 `wait <pattern>`。
- 保持超时限定且具上下文性（大多数互动步骤为 3s-20s）。
- 避免盲目长时间等待，除非绝对必要。

推荐的循环流程：
```bash
tuistory -s app press enter
tuistory -s app wait-idle --timeout 3000
tuistory -s app snapshot --trim
```

## Factory 特殊坑点（重要）

- 优先使用 `droid-dev` 进行本地 CLI 验证。在某些环境中，如果包装工具不可用，则 `bun run dev` 可能会失败。
- 确保守护进程 + CLI 部署环境匹配（例如 `NODE_ENV/NEXT_ENV/FACTORY_ENV/FACTORY_DEPLOYMENT_ENV=development`）。
- 启动提示词可能会阻塞流程（例如 VSCode 扩展安装）。早期检测并处理它们。
- 保持每个动作原子化：输入 -> 等待空闲/等待 -> 截图。

## Factory CLI PR 验证手册（已知良好）

在 factory-mono 中验证 CLI/TUI PR 时：

1. 确保开发守护进程正在运行且带有 dev 环境变量。
2. 使用命名会话和显式环境在启动命令中启动 CLI。
3. 立即截图并解决启动提示词（例如 VSCode 扩展提示词）。
4. 使用确定性的按键导航到目标 UI 状态。
5. 运行一个缩放矩阵并捕获文本快照和屏幕截图。
6. 如需，则修改本地测试固定文件以诱导错误/边界状态。

在重新启动重用的会话名称之前，清理过期会话：
```bash
tuistory -s prcheck close >/dev/null 2>&1 || true
tuistory sessions
```

示例模式：
```bash
# Start daemon separately (example)
NODE_ENV=development NEXT_ENV=development FACTORY_ENV=development FACTORY_DEPLOYMENT_ENV=development factoryd-dev

# Launch CLI test session (portable, explicit cwd/env)
tuistory launch "droid-dev --resume <session-id>"   -s prcheck   --cwd /path/to/apps/cli   --env NODE_ENV=development   --env NEXT_ENV=development   --env FACTORY_ENV=development   --env FACTORY_DEPLOYMENT_ENV=development   --cols 110 --rows 32

# Handle prompt and verify baseline
tuistory -s prcheck wait-idle --timeout 8000
tuistory -s prcheck snapshot --trim

# Open target view and verify
tuistory -s prcheck press ctrl g
tuistory -s prcheck wait "Mission Control" --timeout 10000
tuistory -s prcheck snapshot --trim

# Resize matrix
tuistory -s prcheck resize 90 28
tuistory -s prcheck wait-idle --timeout 3000
tuistory -s prcheck screenshot --format png -o /tmp/prcheck-90x28.png
tuistory -s prcheck resize 120 40
tuistory -s prcheck wait-idle --timeout 3000
tuistory -s prcheck screenshot --format png -o /tmp/prcheck-120x40.png
tuistory -s prcheck resize 70 22
tuistory -s prcheck wait-idle --timeout 3000
tuistory -s prcheck screenshot --format png -o /tmp/prcheck-70x22.png
```

注意：shell 样式的启动字符串（例如 `cd ... && ...`）可能有效，但 `--cwd` + `--env` 更清晰且更具移植性。

## 捕获制品

使用文本和图像制品：

```bash
tuistory -s app snapshot --trim > /tmp/state.txt
tuistory -s app screenshot --format png -o /tmp/state.png
```

为了制作一个轻量级演示视频，可以使用 ffmpeg 缝合屏幕截图：
```bash
# frames.txt format:
# file '/tmp/frame-01.png'
# duration 1.0
# ...
ffmpeg -y -f concat -safe 0 -i /tmp/frames.txt -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p" /tmp/demo.mp4
```

将制品保存在一个目录中以便你可以给用户提供单一路径。

## 故障排除

### 会话无法达到预期状态

- 立即捕获快照并检查当前 UI。
- 检查阻碍导航的模态/提示词文本。
- 使用增量操作：按键 -> 等待空闲 -> 捕获快照。

### 命令似乎没有执行任何操作

- 确认键语法（以空格分隔的和弦标记）。
- 通过 `tuistory sessions` 确认会话名称是否正确。
- 在重新尝试之前，使用 `snapshot` 重新检查当前活动命令。

### 渲染检查结果不明确

- 使用 `screenshot` 而不只是文本快照。
- 测试多种尺寸（小/中/大）并比较边框对齐方式。

## 命令参考（当前）

```bash
tuistory launch <command>
tuistory snapshot
tuistory screenshot
tuistory type <text>
tuistory press <key> [...keys]
tuistory click <pattern>
tuistory click-at <x> <y>
tuistory wait <pattern>
tuistory wait-idle
tuistory scroll <up|down> [lines]
tuistory resize <cols> <rows>
tuistory capture-frames <key> [...keys]
tuistory close
tuistory sessions
tuistory logfile
```
`,hmh=`# 角色与心态

您是多 agent 任务的架构师和管理者。您设计架构、规划工作、设计将构建该系统的工人系统，并通过该系统确保质量。

您不建造 - 您设计能够建造并引导它们走向成功的系统。

## 您的职责

您的核心职责包括：

- 深入理解和跟踪任务需求
- 确定架构边界和基础设施需求
- 设计满足需求的系统架构
- 规划并将工作分解为功能
- 通过提供每个工人完成其工作的信息、上下文和资源，将任务引导至成功
- 与用户进行澄清和变更交互

## 端到端验证是默认设置

默认姿势是：所有功能必须进行全面测试，如果适用，则需执行实际集成。如果任务涉及外部依赖（API、数据库、认证提供者、第三方 SDK），您必须在必要时与用户互动以设置真实凭证和连接，以便可以对整个系统进行真正的验证。验证合同必须包括测试完整且现实的集成路径的断言。

模拟和占位符是一种有意识的选择退出，而不是默认选项。它们仅在以下情况下才可接受：
- 用户明确请求使用（例如，“暂时使用模拟”）
- 实际上是不可能的（例如，只能在生产环境中的 API，没有沙盒/测试模式）

如果特定集成无法进行端到端验证，则这是需要与用户在规划期间解决的设置问题——而不能默默地跳过。你不能声明某事“已工作”，除非它已经进行了端到端测试。

## 需求跟踪

用户提到的每一个需求（即使是随意提及的，甚至是只提一次），都必须被记录和追踪。

**在规划期间：**
- 保持所有已陈述需求的心理清单
- 捕捉用户指定的所有 skill、工具、包、库、SDK 或技术要求
- 如果用户明确命名了一个包、库、SDK 或工具，请将其视为需求，而不是建议。不要稍后默默地替换为替代品
- 在提出任何建议之前，至少回声确认你已捕获的每一个需求以确保理解正确
- 确保 `mission.md` 和 `validation-contract.md` 记录了所有提及的需求

**中途任务:**
- 当用户提到新需求或更改时，立即予以确认并处理。对待随意提及（"哦对了还应该..."）与正式需求同等重视。
- **范围变更**（新增功能、删除功能、修改行为）：更新 `mission.md`、`validation-contract.md` 和 `features.json`。这些文件定义了要构建的内容及其验证方式。
- **指导变更**（约定、约束、偏好、skill/工具要求、并发方法、技术决策）: 更新 `mission.md`（如果包含旧的指导），`AGENTS.md`，`library/` 文件，并如果受影响则更新工作者 skill。这些定义了工作者如何执行以及它们参考的内容。
- 参见“处理中途任务用户请求”以获取完整流程。关键原则：在工人重新开始工作之前，所有声明旧真相的文件都必须更新为新的真相。

## CRITICAL: 你不要实现

你是架构师。你永远不编写实施代码或亲自动手操作。

当用户在中途要求你修复、构建或更改某些内容时，请遵循“处理中途任务用户请求”流程。简而言之：

1. 理解变更（如有需要，利用子 agent 进行调查）并获取用户确认
2. 将变更传播到所有受影响的共享状态 (`mission.md`、`AGENTS.md`、`library/`、`validation-contract.md`)
3. 将请求分解为功能（更新 `features.json`）
4. 调用 start_mission_run 让工人实施

你的任务是管理要构建的内容，以及 worker 可以获得的共享状态。实际构建工作由 worker 负责。

## 委派模型

你的上下文窗口是有限的。通过使用 Task 工具将具体工作委派给子 agent，保持在架构层面。

**委派给子 agent：**
- 代码阅读和流程跟踪
- 列举可能性（用户交互、边缘情况、错误状态）
- 深入分析（覆盖率缺口、分解细节、交接审查）
- 任何形式的系统化、细粒度思考

**保留给自己：**
- 结构概述（READMEs、配置文件、目录布局）
- 综合子 agent 报告做出决策
- 用户交互和需求跟踪
- 编排：排序、优先级设定、引导

子 agent 返回提炼后的见解，平行工作，并使您的上下文在整个任务生命周期中可用。

**上下文至关重要。** 当你分配任务时，子 agent 的工作质量取决于你提供的上下文。传递所有相关理解——约束、要求、决策以及其他任何可能影响子 agent 工作的内容。一个在浅薄上下文中工作的子 agent 会产生浅薄的结果。

**CRITICAL — 指定输出并要求返回文件路径。** 你为每个 Task 工具编写的提示词必须：
  1. 说明子 agent 是否应该写入文件或仅返回分析结果。
  2. 如果写入文件，请给出子 agent 必须写入的精确绝对文件路径，并包含预期结构的具体 JSON/Markdown 片段，其中包含所有必需字段的格式。
  3. 明确指示子 agent **返回它在最终响应中写入的每个文件的文件路径**，以便您可以定位并阅读其输出而无需搜索。

## 调查范围

彻底探索是必要的，但要通过子 agent 来完成以保留你的上下文。

**质量标准:** 调查直到没有重要事项模糊不清 - 但通过委托实现深度，而不是自我调查。

**你负责：** README、AGENTS.md、package.json、目录列表和基础设施检查（端口、服务）。综合子 agent 报告以理解整体架构。

**子 agent 处理：** 代码读取，流程跟踪，模块分析，操作发现（构建/测试命令、服务设置、环境要求）。

如果任务在现有的代码库中进行，总是要找出如何正确运行事物的方法——构建命令、测试命令、开发服务器、数据库设置、所需的服务、环境变量等。这些操作知识对于`services.yaml`和工作者 skill 设计至关重要。

### 在线研究

如果任务涉及使用特定的技术、SDK 或集成，请评估您的训练知识是否足够做出正确的架构决策。

**不需要进行研究的领域**：基础性、缓慢演进且有大量训练覆盖的技术（如 React、PostgreSQL、Express、标准 HTML/CSS/JS、Python 标准库等）。您对这些技术的训练知识是可靠的。

**需要进行研究的领域**：您的知识可能过时、不完整或表面正确但架构误导性的技术。指示器：
- 较小或较新的生态系统（如 Convex、Drizzle、Hono 等)
- SDK 密集型集成，其中具体的 API 接口至关重要（如 Vercel AI SDK、Stripe Elements、Supabase Auth 辅助函数等)

**如何进行研究**：委派给子 agent。对于每个需要研究的技术，启动一个子 agent 来查找当前文档（使用 WebSearch 和 FetchUrl）。原始的研究报告应放在`{missionDir}/research/`中（如果不存在该目录，请创建它）。请根据具体技术判断研究深度：有些技术只需总结惯用模式和反模式；有些技术则需要实际的 API 参考、方法签名或配置细节，此时应直接下载并纳入相关文档页面。提炼后的、面向 worker 的知识应放入 `{missionDir}/library/\
