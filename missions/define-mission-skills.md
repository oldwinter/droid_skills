---
name: define-mission-skills
description: 引导协调器设计工作类型及其 skill 的过程。
---

# 设计您的工作系统

您的任务是设计一个生产完整高质量工作的工人系统。

## 步骤 1：分析有效的工作边界

问自己:
- 这项任务触及了哪些不同的层次或领域?
- 不同的区域是否需要不同的流程或工具?

每个不同的边界通常对应一种工作类型。

## 步骤 2：设计工作类型

对于每个边界，确定:
- 在这个区域内进行彻底工作的必备 skill/工具是什么?
- 它如何验证其工作？（TDD + 手动验证）
- 详尽的手工移交是什么样子？

## 自动验证 (内置)

系统在里程碑完成时会自动注入两个验证功能：

1. **scrutiny-validator** — 运行验证器，为每个已完成的功能启动审查子 agent，并综合发现结果。如果失败，则在修复后返回待处理状态重新运行。
2. **user-testing-validator** — 从 `fulfills` 中确定可测试断言，设置环境，启动流程验证子 agent，并综合结果。如果失败，则在修复后返回待处理状态重新运行。

你不需要自己创建这些功能——它们由系统自动注入。

## 指导原则

1. **程序清晰性** - 关于做什么、顺序和使用什么不应有任何重要的模糊性。

2. **测试驱动开发** - 测试应在实现之前编写，始终如此。工人应首先编写失败的测试（红色），然后实施使其通过（绿色）。

3. **手工验证** - 自动化测试是必要的但不充分的。工人必须手动验证他们的工作以捕捉测试遗漏的问题。

4. **无孤儿进程** - 工人不应留下任何测试运行器或其他正在运行的过程：
  - 避免在测试中使用 watch/交互模式，除非明确需要。
  - 如果测试命令启动了一个长时间运行的过程（例如，watch 模式、浏览器运行器），工作者必须停止它，并确保它们启动的任何子进程也被终止（通过 PID 而不是名称）。
---

## 创建工作者 skill

为每种工作者类型，在 missionDir 中创建一个 skill：

```
skills/{worker-type}/SKILL.md
```

**重要提示**：skill 应放在 missionDir 中，而不是在任何仓库的 `.factory/` 目录中。任务会话从 `{missionDir}/skills/` 加载 skill。

### 工作者 skill 结构

每个工作者 skill 必须包括：

1. **YAML 前置信息** - 名称和描述
2. **所需 skill 和工具** - 该类型工作者在工作中必须使用的 skill 和工具。包含用户或任务最终确定的任何绑定项。“None”如果不适用。
3. **工作流** - 步骤说明。具体说明所需的 skill/工具。
4. **示例移交** - 完整且现实的移交示例，展示彻底工作的样子
5. **何时返回协调器** - skill 特定条件

```markdown
---
name: { worker-type }
description: { One-line description }
---

# {Worker Type}

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## Required Skills and Tools

{Skills and tools workers of this type must use during their work. Include anything the user or the mission finalized as binding.}

## Work Procedure

{Step-by-step procedure - testing, implementation, verification. Be specific about tools, commands, and what thorough work looks like at each step.}

## Example Handoff

{A complete JSON example showing what a thorough handoff looks like for this worker type}

## When to Return to Orchestrator

{Skill-specific conditions beyond standard cases}
```

**示例交接定义了 worker 投入程度的上限。** worker 会据此匹配模式；示例展示多深的投入，实际执行就会达到相应深度。请按照 worker 职责所需的深度编写示例，覆盖该工作流的全部职责范围，并以真实、详尽的交接内容为基础。

**Handoff 字段**（由 EndFeatureRun 工具使用）:

| 字段                             | 目的                                                |
| --------------------------------- | ------------------------------------------------------ |
| `salientSummary`                  | 会话中发生了什么的一个 1-4 句话总结   |
| `whatWasImplemented`              | 具体描述所构建的内容（至少 50 个字符）  |
| `whatWasLeftUndone`               | 未完成的部分 - 如果真正完成了则为空字符串         |
| `verification.commandsRun`        | Shell 命令带有`{command, exitCode, observation}` |
| `verification.interactiveChecks`  | UI/浏览器检查带有`{action, observed}` |
| `tests.added`                     | 测试文件带有`{file, cases: [{name, description}]}`。`name`匹配测试运行器标识符（例如，`it(...)`中的字符串或测试函数名称）。`description`是对测试检查内容的描述性文字 |
| `discoveredIssues`                | 发现的问题：`{severity, description, suggestedFix?}` |

良好的`salientSummary`示例（具体说明，1-4 句话）:
- 成功: "实现了 GET /api/products/search，并添加了游标分页和最小长度验证；运行了`npm test -- --grep 'product search'`（通过4 个测试），并通过真实的 curl 请求验证了`q=a`返回400 以及实际的200 响应。"
- 失败: "尝试将注销与`SessionStore`关联，但`bun run typecheck`失败（缺少导入）且`bun test auth`有2 个未通过的测试；返回到协调器以决定是否添加会话持久化或更改注销语义。"

## 何时返回到协调器

- 功能依赖于尚未存在的 API 端点或数据模型
- 需求模糊或矛盾
- 现有 bug 影响此功能

---

## 检查清单

在继续创建任务工件之前：

- [ ] 每个工作者 skill 都位于 `{missionDir}/skills/{worker-type}/SKILL.md`
- [ ] 每个 skill 都包含 YAML 前置信息（name、description）
- [ ] 每个 skill 都包含示例移交部分，其中有完整、现实的 JSON 示例
- [ ] 示例移交详尽且明确——它们设定了工作者将遵循的质量标准
- [ ] 每个 skill 的“所需 skill 和工具”部分包含该工作者必须使用的每个 skill 和工具
- [ ] 每个 skill 的“工作流”以一个程序化验证步骤结束，该步骤反映用户批准的程序化验证计划
