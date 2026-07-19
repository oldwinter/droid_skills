---
name: install-qa
description: >
  为这个项目设置自动化质量测试。执行深入的代码库分析，
  提出针对性的问题，并生成一个模块化的问答 skill，每个应用都有子 skill,
  一个 GitHub 行动工作流，和一个报告模板。这是一项复杂、多阶段的工作。
  过程 —— 质量保证是基础，我们花时间确保其正确无误。
user-invocable: true
---

    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░                                          ░░
    ░░   ╔═╗ ╔╗╔ ╔═╗ ╔╦╗ ╔═╗ ╦   ╦   ╔═╗ ╔═╗  ░░
    ░░   ║ ║ ║║║ ╚═╗  ║  ╠═╣ ║   ║   ║ ║ ╠═╣  ░░
    ░░   ╚═╝ ╝╚╝ ╚═╝  ╩  ╩ ╩ ╩═╝ ╩═╝ ╚═╝ ╩ ╩  ░░
    ░░                                          ░░
    ░░   ▸ Deep codebase analysis               ░░
    ░░   ▸ Interactive questionnaire            ░░
    ░░   ▸ Multi-phase skill generation         ░░
    ░░   ▸ GitHub Actions workflow setup        ░░
    ░░                                          ░░
    ░░   Quality assurance is foundational.     ░░
    ░░   We take the time to get this right.    ░░
    ░░                                          ░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

> **⚠️ 复杂性警告：** 该 skill 执行深度代码库分析，运行多阶段
> 交互式问卷调查，并生成多个文件。这是一个高复杂度的任务。

# 安装 QA

清除所有之前的计划和待办事项。你之前的任务已完成。你的新任务是为这个项目设置自动化质量检查。

**在开始之前，请从以下阶段创建待办事项列表。**

您正在为该项目设置一个模块化的 QA skill。该 skill 将用于根据应用程序类型，通过实际浏览器（agent-browser）、TUI 测试（tuistory）或 API 调用（curl）运行自动化功能测试。

## 输出结构

您将在 `.factory/skills/` 生成具有以下结构的 skill：

```
.factory/skills/qa/
  SKILL.md                  # Orchestrator: reads diff, routes to relevant sub-skills
  config.yaml               # All env/auth/integration config (single source of truth)
  REPORT-TEMPLATE.md        # Standardized report template
  .install-progress.yaml    # Partial questionnaire progress for resume
.factory/skills/qa-<app-name>/
  SKILL.md                  # One sub-skill per testable app (e.g., qa-web, qa-cli, qa-backend)
```

**命名约定：** 子 skill 必须命名为 `qa-<app-name>`（例如，`qa-web`, `qa-cli`, `qa-backend`）。每个都是一个独立的 skill，有自己的 `SKILL.md` 前置信息文件，以便 Factory skill 系统可以发现并独立调用它们。顶级的 `qa` skill 协调它们。

---

# 阶段 1：检查先前进度

检查 `.factory/skills/qa/.install-progress.yaml` 是否存在。如果存在：

1. 读取它并向用户展示之前配置的内容
2. 询问他们是否希望保留之前的答案作为默认值或从头开始
3. 无论哪种方式，重新询问所有类别（在恢复时使用之前的答案作为默认值），并重新生成所有文件。绝不要跳过生成步骤——用户可能会给出不同的答案或者生成规则可能已经改变。
4. 如果从头开始，则删除进度文件并从头开始

---

# 阶段 2：深入代码库分析

彻底扫描仓库。您必须自动检测以下内容而无需询问用户。在提问任何问题之前，以总结的形式呈现您的发现：

## 需要检测的内容:

### 应用结构

- 这是一个单体仓库吗？存在哪些应用？（查看顶层目录、package.json/pnpm-workspace.yaml/turbo.json 中的工作空间配置）
- 对于每个应用：它是什么？（Web 前端、API 后端、命令行工具、移动应用、桌面应用）
- 哪些路径模式映射到每个应用？

### 技术栈

- 每个应用的框架和语言（package.json, Cargo.toml, go.mod, requirements.txt 等）
- 构建命令和开发服务器命令

### 认证

- 用户如何登录？（搜索 OAuth 提供者、认证中间件、登录组件、会话管理）
- 使用哪种认证库？（NextAuth、Passport、WorkOS、Auth0、Clerk、Firebase Auth 等）

### 环境

- 从以下位置查找所有环境 URL：.env 文件、.env.example、配置文件、CI/CD 工作流、部署清单、README
- 查找特定于环境的配置模式

### 特性标志

- 搜索导入：LaunchDarkly、Statsig、Unleash、Split、Flagsmith 或自定义特性标志模式
- 代码中是如何评估标志的？

### 外部集成

- 支付：Stripe、Braintree、PayPal（搜索依赖项 + 导入）
- 邮件：SendGrid、SES、Postmark、Resend、AgentMail、Mailhog
- 短信：Twilio、MessageBird
- 其他：在 package.json 依赖项中搜索已知的 SaaS SDK

### CI/CD

- 使用哪个持续集成提供商？（.github/workflows、.gitlab-ci.yml、Jenkinsfile、.circleci）
- 是否有现有的质量保证或端到端测试工作流？

### 现有测试基础设施

- 使用了哪些测试框架？（Vitest, Playwright, Cypress, pytest 等）
- 是否有现有的端到端或集成测试？

### 关键用户流程

- 分析路由定义、导航和页面组件以识别主要用户流程
- 查看：路由配置、页面/视图组件、API 端点、表单提交

在继续提问之前，向用户提供所有发现的结构化总结

---

# 阶段 3：有针对性的问题调查

仅询问您无法自动检测的内容。使用 AskUser 工具分组问题。在每个小组回答后将答案保存到`.factory/skills/qa/.install-progress.yaml`中

**重要**：始终先呈现您的发现，然后请求确认或补充。围绕您找到的内容来构建问题，而不是从头开始

## 类别 1：默认 QA 目标

- "我找到了这些环境:[列表]。默认情况下，QA 应该运行在哪个环境中？"
- "是否有特定环境的限制？"（例如，"不要在生产环境中创建真实用户"）

保存此类别之前的进度。

## 类别 2：人物与角色

仔细构建这句话："QA 需要以不同类型的用户测试你的应用。这确保了权限正确工作——管理员可以管理设置，普通成员可以完成他们的工作，而只读查看者确实无法编辑任何内容。每个角色代表一种真实用户类型。"

询问：

- "在您的应用中存在哪些用户角色？对于每个角色，我需要：
  (a) 一个简短的名称（例如，admin、member、viewer、guest） (b) 他们能做什么（关键能力） (c) 他们不应该能够做什么（这将成为一个负向测试） (d) 您是否有专门用于此角色的测试账户？如果有，请提供邮箱地址？
- "对于没有测试账号的角色，应该在测试运行期间通过注册创建它们，还是由你提供？"
- "测试凭证存储在哪里？"（环境变量名称、AWS Secrets Manager 密钥、HashiCorp Vault 路径，或者手动输入）

保存此类别之前的进度。

## 类别 3：关键流程 (确认 + 延伸)

- "根据我的分析，这些是我识别的关键用户流程：[列表]。这些正确吗？还需要添加或删除哪些？"
- "对于每个工作流，成功的标准是什么？（例如，'用户登录后看到仪表盘'，'收到支付确认邮件'）"
- "是否有流程需要使用多个用户角色进行测试？（例如，‘验证 viewer 无法访问管理员设置页面’）"
- "任何流程在测试后创建了需要清理的持久化数据吗?"
  保存此类别之前的进度。

## 类别 4：外部服务（仅在检测到集成时）

对于每个检测到的集成：

- "我在你的依赖项中看到了[ServiceName]。它有沙盒/测试模式吗？QA 应该使用哪些测试凭证？"
- 对于邮件："在注册/通知流程中，QA 应该如何接收测试邮件？"（仅在未检测到 AgentMail/Mailhog/测试 SMTP 时询问）

保存此类别之前的进度。

## 类别 5：清理

- "在 QA 创建测试用户或数据之后，应该如何清理？" 选项:
  - 通过 API 端点删除 (哪个？)
  - 管理员面板清理
  - 数据库重置命令
  - 留给手动清理
  - 不适用（测试是只读的）

保存此类别之前的进度。

## 类别 6: ImageMagick

检查是否安装了 ImageMagick:

```bash
command -v magick || command -v convert
```

- 如果已经安装: 在 config.yaml 中设置 `imagemagick: true`，告诉用户 "检测到 ImageMagick -- QA 将生成前后截图的动画 GIF 差异。"
- 如果不安装: 询问 "ImageMagick 可以为视觉回归测试启用前后截图的动画 GIF 差异。您是否希望安装它？"
  - 如果同意: 运行 `brew install imagemagick`（macOS）或 `sudo apt-get install -y imagemagick`（Linux），设置 `imagemagick: true`
  - 如果否: 设置 `imagemagick: false`

## 类别 7: GitHub Action (仅在 .github/ 目录存在时)

- 首先，检查 `.github/workflows/` 中是否已存在现有的 QA 工作流。如果有，请列出它们。
- "您希望我生成一个自动在 PR 上运行 QA 的 GitHub Actions 工作流吗？"
- 如果肯定: 询问 "QA 检查应该是 **必需的**（失败时阻止合并）还是 **可选的**（运行但不阻止合并）？"
  - 如果是必需的: 不需要额外配置 (仓库管理员将其添加到分支保护规则中)
  - 如果是可选的: 在生成的工作流文件中添加一个注释，说明此检查仅是信息性的
- 如果项目使用 Vercel/Netlify 预览部署 PR, 询问 "我检测到 PR 获取了一个 Vercel 预览部署。QA 工作流是否应该在运行测试之前等待预览被部署？" (默认: 是)

## 类别 8: 失败学习

"当 QA 遇到新的失败模式（例如，认证墙、缺少环境变量、不稳定的元素）时，应该如何反馈以便未来的运行能够更好地处理它？"

提供这些选项:

1. **建议在报告中**（默认）-- QA 报告包含一个“建议的 skill 更新”部分，其中包含可以直接复制粘贴到子 skill 已知失败模式部分的 markdown 摘要。摘要位于带有清晰标签如"将此内容粘贴到 qa-web/SKILL.md 的已知失败模式部分中"的折叠 `<details>` 块内。
2. **Auto-commit** -- agent 直接在每次运行后将更新提交到子 skill 文件。需要工作流中的 `contents: write` 权限。
3. **Open a PR** -- agent 打开一个包含失败目录更新的 PR。有人审查并合并它。

将选择保存为 `failure_learning` 在 config.yaml 中 (值: `suggest_in_report`, `auto_commit`, `open_pr`)。

**每种选项的实现:**

对于 `suggest_in_report`: 调度器 SKILL.md 必须指示 agent 在每次运行结果为 BLOCKED 或 FAIL 且揭示了新的失败模式不在子 skill 已知失败模式中时，向报告添加一个“建议的 skill 更新”部分。建议必须包括要添加的确切 markdown、目标文件路径以及插入位置。示例:

```markdown
### Suggested Skill Updates

<details>
<summary>Add to .factory/skills/qa-web/SKILL.md → Known Failure Modes</summary>

```markdown
6. **WorkOS password field not found.** Some WorkOS configurations show OTP-only login without a password field. If the password input is not found, report as BLOCKED and note the WorkOS configuration.
```

</details>
```

For `auto_commit` or `open_pr`: The workflow must have `contents: write` and `pull-requests: write` permissions. The agent writes a `qa-results/skill-updates.json` file with structured edits. A workflow step after the QA run parses this JSON and applies the edits to the actual repo files, then either commits directly (`auto_commit`) or opens a draft PR (`open_pr`). See the workflow template section for the exact implementation.

Save progress after this category.

---

# Phase 4: Generate the QA Skill

Using all gathered information, generate the following files:

## 4a. config.yaml

Generate `.factory/skills/qa/config.yaml` with all configuration as a single source of truth. Follow this structure:

```yaml
project: <ProjectName>
imagemagick: <true|false>
environments:
  <env-name>:
    url: <url>
    restrictions: [<optional list>]

default_target: <env-name>

auth:
  method: <otp|oauth|email-password|magic-link|api-key|saml>
  provider: <WorkOS|Auth0|Clerk|Firebase|custom|etc>

personas:
  - name: <role-name>
    description: '<what this user type does>'
    email: <test-account-email>
    credentials_source: <aws-secrets-manager|env-var|vault|manual>
    secret_name: <secret-key-or-env-var> # if applicable
    test_focus: [<areas to test as this persona>]
    cannot_do: [<things this persona must NOT be able to do>]
  - name: new_user
    description: 'Fresh signup, no existing data'
    email_pattern: 'qa+signup_{RUN_ID}@<domain>'
    test_focus: ['onboarding', 'empty states', 'first-run experience']

apps:
  <app-name>:
    path_patterns: [<glob patterns>]
    skill: qa-<app-name>
    test_tool: <agent-browser|tuistory|curl>
    build_command: '<optional build command>'

feature_flags:
  provider: <provider-name|none>
  dashboard_url: <url>
  how_to_override: '<instructions>'

integrations:
  <integration-type>:
    provider: <provider-name>
    # provider-specific config

cleanup:
  auto_cleanup: <true|false>
  strategy: <delete-test-users|reset-db|api-call|manual|none>
  instructions: '<how to clean up>'

failure_learning: <suggest_in_report|auto_commit|open_pr>
```

**环境行为对于预发布部署:** 如果项目使用 Vercel/Netlify 预发布部署，则配置文档必须说明预览 URL 的行为类似于开发环境（相同的后端，相同的数据库，相同的 API 密钥）。在测试预览 URL 时，调度器和子 skill 应使用开发环境流程 (例如，Stripe 测试卡、开发 API 密钥)。不要生成单独的生产/预生产 QA 流程来针对预发布 URL 运行它们——因为预发布后端没有生产数据（优惠券代码、生产 Stripe 密钥等），它们会失败。

## 4b. SKILL.md（编排器）

生成 `.factory/skills/qa/SKILL.md`。这是主要的调度器，会被加载到上下文中。它必须是轻量级的——不应包含实际的测试流程（这些在单独的 `qa-<app-name>` 子 skill 中）。它应该:

````markdown
---
name: qa
description: >
  Run QA tests for <ProjectName>. Analyzes git diff to determine affected areas,
  runs configured test flows with multiple personas, and generates diff-targeted tests.
  Uses agent-browser for web testing, tuistory for CLI testing.
  Use when testing PRs, releases, or smoke testing environments.
---

# QA Orchestrator

**SCOPE: This skill performs manual/functional QA only -- verifying that the application actually works by interacting with it as a real user would (browser, TUI, API calls). Do NOT run or report on CI checks, linting, ESLint, typecheck, unit tests, or any static analysis. Those are handled by separate workflows.**

## Step 1: Load Configuration

Read `.factory/skills/qa/config.yaml` for environment URLs, credentials, personas, and app definitions.

## Step 2: Determine Target Environment

Use the default_target from config unless the user specifies a different environment.
Respect any environment restrictions (e.g., no user creation in prod).

**CRITICAL: Vercel/Netlify preview deployments are DEV environments.** Preview URLs serve the branch's frontend code but connect to the same backend, database, Stripe keys, and third-party integrations as the dev environment. Therefore:

- Use **dev flows** when testing against a preview URL (e.g., Stripe test cards, dev API keys, dev feature flags)
- Do NOT use prod/preprod flows against a preview URL (e.g., voucher codes, production Stripe, preprod-specific data). These will fail because the preview backend doesn't have prod data.
- The orchestrator must treat preview URLs as equivalent to the `development` environment in config.yaml.

## Step 3: Analyze Git Diff

Run `git diff` to determine what changed. Map changed files to apps using the path_patterns in config.yaml.

Files that don't match ANY app's path_patterns (e.g., `.factory/skills/**`, `docs/**`, `.github/**`, config files) are NOT associated with any app. Do NOT run app test flows for them.

For each affected app:

- Run ONLY that app's flows from its module file
- Generate ADDITIONAL targeted tests based on the specific changes in the diff

For apps NOT affected by the diff:

- Do NOT load or run their module. Do NOT run their flows. Do NOT run their pre-flight checks. They are completely out of scope.
- Do NOT test CLI if only web files changed. Do NOT test backend if only CLI files changed. The diff determines scope, period.

If NO app is affected by the diff (e.g., docs-only, CI-only, or config-only changes), report as INCONCLUSIVE: "No app code changed -- QA not applicable for this diff." Do NOT run any app flows.

## Step 4: Pre-flight Checks (app-specific only)

Run pre-flight checks ONLY for the apps that are affected by the diff. For example:

- AgentMail/email API check → only if a web app with signup/login flows is affected
- CLI binary build → only if the CLI app is affected

**Web app testing in CI:** When testing web/frontend changes on a PR branch, the agent MUST test against the actual branch code, not whatever is deployed to dev/staging. During codebase analysis (Phase 2), detect which strategy the project uses:

**Strategy 1 (preferred): Vercel/Netlify preview deployments.** If the repo has a workflow that deploys preview URLs on PRs (look for Vercel, Netlify, or similar deployment workflows that post preview URLs as PR comments), the QA workflow should:

1. Wait for the deployment workflow to complete (use `workflow_run` trigger or poll for the PR comment with the preview URL)
2. Extract the preview URL from the PR comment (look for markers like `<!-- vercel-deploy-web -->` or similar)
3. Use that URL as the base for all browser tests

**Strategy 2 (fallback): Local dev server.** If no preview deployment is available:

1. Start the dev server from the checked-out branch code in the background
2. Wait for it to be ready (poll localhost until it responds)
3. Test against localhost

The generated qa-web sub-skill MUST document which strategy to use based on what was detected. If the project uses preview deployments, the workflow MUST wait for the deployment to be ready before running QA.

Do NOT run pre-flight checks for apps that are NOT affected. If a pre-flight check fails for an affected app, report it as BLOCKED with the specific error and remediation steps -- but still proceed with other affected apps.

## Step 5: Execute Diff-Relevant Flows Only

For each app that IS affected by the diff, read its sub-skill from `.factory/skills/qa-<app-name>/SKILL.md`.

The sub-skill contains a MENU of available test flows. You must:

1. Read the diff carefully and identify which flows are relevant to the change
2. Run those flows PLUS any adjacent flows that verify the change integrates correctly (e.g., if a new command is added, test that it appears in /help, that the CLI starts, that fuzzy search finds it)
3. Do NOT run completely unrelated flows (e.g., if the diff only adds a CLI command, do NOT test /settings, /model, billing, or chat)
4. If no existing flow covers the change, write a NEW ad-hoc test that directly verifies the changed behavior
5. Do NOT run unit tests, lint, typecheck, or any automated test suite. This is manual/functional QA -- interact with the app as a real user would.

## Step 6: Evidence Capture

After each significant test step, capture evidence. Use **text snapshots as primary evidence** -- they render inline in the PR comment with no image hosting issues.

For CLI/TUI apps (tuistory):

- Use `tuistory -s <session> snapshot --trim` to capture terminal state as text
- Embed the snapshot directly in the report as a fenced code block with a descriptive label
- Each snapshot MUST show something DIFFERENT. Wait for the UI to change before capturing again.

For web apps (agent-browser):

- Use `agent-browser snapshot` to capture the page's accessibility tree as text evidence
- Save screenshot files to `./qa-results/$RUN_ID/` for the artifact upload
- Do NOT embed `![image](url)` markdown in the report -- screenshot images cannot be displayed inline in GitHub PR comments. Instead, mention the filename and note that it's available in the downloadable artifacts.

Evidence quality rules:

- Focus on the RELEVANT content. Trim snapshots to the meaningful part.
- Label each snapshot clearly: what it shows and why it matters for the test.
- NEVER embed broken image links. If you can't verify an image URL will resolve, use text evidence instead.
- The workflow uploads all files in `./qa-results/` as a downloadable artifact -- reference that for visual evidence.

## Step 7: Test Quality Gate

TEST QUALITY REQUIREMENTS:

1. CHANGE-SPECIFIC FIRST. Prioritize tests that directly verify the behavioral change in the diff. At least half your tests should be testing the new/changed feature itself.
2. INTEGRATION TESTS ARE VALID. Tests that verify the change integrates correctly with existing features are good (e.g., new command shows in /help, fuzzy search finds it, CLI starts without errors). These are NOT smoke tests -- they verify the change didn't break integration points.
3. NO UNRELATED FLOWS. Do NOT test features completely unrelated to the diff (e.g., don't test /settings when only /install-qa changed, don't test billing when only CLI changed).
4. NO AUTOMATED TEST SUITES. Do NOT run vitest, npm test, or any CI-style checks. This is manual/functional QA only.
5. NEGATIVE TESTS. Include at least 1 test verifying error handling or boundary conditions related to the change.
6. INTERACTIVE TESTING. Test by actually interacting with the app as a real user would.
7. INCONCLUSIVE IF UNSURE. If you cannot articulate what the PR changes, mark as INCONCLUSIVE rather than PASS.

## Step 8: Handle Failures

**Never silently skip a flow.** If a flow cannot complete, report it as BLOCKED with what was tried and how the user can fix it. Then continue to the next flow -- never abort the entire run for a single failure.

## Step 9: Generate Report

Generate the report at `./qa-results/report.md` using `.factory/skills/qa/REPORT-TEMPLATE.md`.

The report MUST follow the template in `.factory/skills/qa/REPORT-TEMPLATE.md`. Key rules:

- Start with `## QA Report` heading followed by the test results table
- Result column MUST use emojis: :white_check_mark: PASS, :x: FAIL, :no_entry: BLOCKED, :warning: FLAKY, :grey_question: INCONCLUSIVE
- Keep it CONCISE. The table + a short "Action Required" section (if any) + collapsed screenshots = the entire report.
- Do NOT include: "Behavioral Change Summary", "Blocked Flows" prose, "Info" metadata table, or verbose explanations of what the diff does. The reviewer already knows that.
- Do NOT report setup/prerequisite steps (building, startup, launching) as test rows. Those are means to an end, not test cases. Only report rows that verify actual user-facing behavior or the specific behavioral change from the diff.
- Put ALL evidence in a single collapsed `<details>` block
- For TUI evidence: embed text snapshots as labeled fenced code blocks (e.g., `### Snapshot 1: Autocomplete dropdown` followed by a code block with the terminal output).
- For web evidence: embed accessibility tree snapshots as text. Reference screenshot filenames for visual proof (available in downloadable artifacts). Do NOT use `![image](url)` markdown -- the URLs won't resolve and will show broken images.

## Step 10: Suggest Skill Updates (Failure Learning)

After generating the report, check if any BLOCKED or FAIL results revealed a **testing environment insight** that would help future QA runs succeed. This is about learning how the testing environment works, NOT about fixing bad selectors or skill typos.

**Good suggestions** (environment/workflow knowledge):

- "WorkOS renders in Afrikaans locale -- always use `snapshot -i` to discover button labels dynamically"
- "Feature flag X must be enabled in Statsig before testing this flow"
- "Stripe checkout iframe takes 15+ seconds to load -- increase wait to 20s"
- "The dev server requires `npm run dev:web`, not `npm run dev`"

**Bad suggestions** (skill bugs, not environment insights -- do NOT suggest these):

- "Selector data-testid=foo doesn't exist" -- that's a skill bug, fix it directly
- "The button text changed from X to Y" -- that's expected from the PR diff

Format as a table with severity, collapsible fix prompts, and a count in the heading:

## Suggested Skill Updates (N issues found)

| #   | Severity        | File     | Issue               | Fix Prompt                                                                           |
| --- | --------------- | -------- | ------------------- | ------------------------------------------------------------------------------------ |
| 1   | <emoji> <level> | `<file>` | <short description> | <details><summary>Copy</summary><br>`<full droid prompt to fix the issue>`</details> |

**Severity levels:**

- `�� Breaking` -- Causes test failures every run (wrong URL, wrong auth method, missing required step)
- `�� Degraded` -- Causes intermittent failures or suboptimal behavior (timing issues, rate limits, locale assumptions)
- `�� Info` -- New knowledge that improves future runs but doesn't cause failures (new UI pattern, new endpoint)

Each Fix Prompt must be a self-contained instruction that Droid can execute directly when pasted.

Do NOT suggest updates for failures already covered in Known Failure Modes, bad selectors, or expected behavior changes from the PR. If no genuinely new environment insights were discovered, omit this section entirely.

Read the `failure_learning` field from config.yaml to determine the strategy:

- `suggest_in_report` (default): include the table in the PR comment report only. Do NOT write `skill-updates.json`.
- `auto_commit` or `open_pr`: include the table in the report AND write a `qa-results/skill-updates.json` file so the workflow can apply the edits outside the sandbox. The workflow handles committing/PR creation -- the agent just writes the JSON.

**`skill-updates.json` format** (only for `auto_commit` or `open_pr`):

```json
[
  {
    "file": ".factory/skills/qa-web/SKILL.md",
    "section": "Known Failure Modes",
    "action": "append",
    "content": "6. **WorkOS Afrikaans locale.** The login form renders in Afrikaans. Always use `snapshot -i` to discover button labels dynamically."
  }
]
```

Fields:

- `file`: relative path to the skill file to edit
- `section`: the markdown heading to find (e.g., `Known Failure Modes`, `Authentication Method`)
- `action`: `append` (add after the section's last item) or `replace` (replace the entire section content)
- `content`: the exact markdown to insert

The workflow will parse this file and apply the edits to the actual repo files, then commit or open a PR depending on the mode.

## 4c. App Sub-Skills (qa-<app-name>)

For EACH detected app, generate a dedicated sub-skill at `.factory/skills/qa-<app-name>/SKILL.md` (e.g., `qa-web/SKILL.md`, `qa-cli/SKILL.md`, `qa-backend/SKILL.md`).

Each sub-skill MUST have proper frontmatter so the Factory skill system recognizes it:

```markdown
---
name: qa-<app-name>
description: >
  QA tests for the <app-name> app. [brief description of what it tests]
---
```
````

每个子 skill 应包含:

- 特定于应用的配置说明（例如，“chat input 是一个 contenteditable div”）
- 一个 **可用测试流程的菜单** —— 这些不是检查列表。协调器只会选择与当前差异相关的流程。请清晰地标记每个流程，以便协调器能够将其匹配到更改的代码中。
- 每个人的个性测试变体
- 特定于该应用的错误处理
- 已知的 UI 小问题或变通办法

### 在 CI 中进行 Web/前端应用测试（对于 Web 应用是强制性的）

Web 应用子 skill 必须包括一个“测试目标”部分，告诉 agent 如何获取带有分支实际代码的 URL。根据你在阶段 2 检测到的内容：

**如果仓库使用 Vercel/Netlify 预发布部署：** 子 skill 应指示 agent 执行以下操作：

1. 使用工作流传递的预览 URL（通过环境变量或提示词）-- 请勿重新解析它
2. 如果需要 Vercel 跳过密钥，请在第一个请求中应用它
3. 如果没有提供预览 URL，请将所有 Web 测试报告为 BLOCKED: "没有 Vercel 预览 URL 可用——无法验证分支代码。" 不要回退到 dev/staging/prod URLs —— 这些部署运行的是不同于 PR 分支的代码，针对它们进行测试会产生无意义的结果。

**如果仓库不使用预览部署：** 子 skill 应指示 agent 执行以下操作：

1. 在本地启动开发服务器（包括确切的命令，例如 `npm run dev:web`）
2. 直到本地主机就绪时才进行轮询
3. 以 localhost 作为基础 URL

**关键:** 在测试 PR 分支时，子 skill 绝不能回退到远程环境（开发、预发布、生产）。远程环境运行的是不同的代码——与它们进行测试并不能告诉你 PR 的更改情况。要么使用预览 URL，要么启动本地开发服务器。如果两者都不可用，请报告为 BLOCKED.

### CI 中的认证

需要认证的子 skill 必须记录提供认证所需的哪些环境变量以及如何使用这些变量。子 skill 应注明以下内容：

- 此应用所需的所有环境变量（API 密钥、令牌、凭据）
- 这些环境变量通过 GitHub 秘密由 CI 工作流提供——agent 不需要进行交互式登录
- 应用程序如何消费这些凭据（环境变量自动拾取、命令行标志、配置文件等）

具体的 secret 名称来自阶段 2（代码库分析）中发现的内容。使用项目已有的认证机制，不要硬编码 Factory 特定的模式。

每个模块都应像现有的 automated-qa-dev/automated-qa-prod skill 一样结构化——包含详细的、经过实战检验的步骤，以处理边缘情况（区域变体、加载延迟、iframe 问题等）

重要: 每个子 skill 都是独立的。它应该包括测试该应用所需的一切内容，而不引用其他子 skill。协调者 SKILL.md 只加载相关的子 skill.

### 使用 tuistory 进行 CLI/TUI 测试（对于 CLI 应用是强制要求）

对于 CLI/TUI 应用，生成的子 skill 必须要求进行**交互式 TUI 测试**：构建二进制文件，通过 tuistory 启动它，发送真实按键，并验证实际终端输出。仅运行单元测试或 `droid exec` 不足以完成 QA。子 skill 必须指示 agent **使用 `droid-control` skill 完成所有 tuistory 交互**。droid-control skill 包含完整且正确的 tuistory API 参考。不要在子 skill 中编写原始 tuistory 命令，而应写成类似下面的指令：

```
Use the `droid-control` skill for all tuistory interactions.

1. Launch the CLI binary: tuistory launch "$CLI_BINARY" -s qa-test --cols 110 --rows 36
2. Wait for the prompt to appear
3. Type a command and verify the output
4. Take a screenshot for evidence
```

应用模块应描述要测试什么（启动 CLI、输入“/help”、验证输出），而不是如何调用 tuistory。droid-control skill 负责具体方法。

额外的 CI 说明对于应用模块：

- 在 CI 中，使用`env -u CI FACTORY_DISABLE_KEYRING=true`前缀启动以避免 Ink CI 检测
- 使用会话名称`-s qa-test`和`--cols 110 --rows 36`

## 4d. REPORT-TEMPLATE.md

生成`.factory/skills/qa/REPORT-TEMPLATE.md`:

```markdown
## QA Report

| #   | Test Case | App | Persona | Result | Notes |
| --- | --------- | --- | ------- | ------ | ----- |

{{TEST_ROWS}}

Result values: :white_check_mark: PASS, :x: FAIL, :no_entry: BLOCKED, :warning: FLAKY, :grey_question: INCONCLUSIVE

{{#if ACTIONABLE_ITEMS}}

### Action Required

{{ACTIONABLE_ITEMS}}
{{/if}}

<details>
<summary>Screenshots & Evidence</summary>

{{EVIDENCE}}

</details>
```

## 4f. 失败处理

生成的 SKILL.md 必须包含以下规则：**“绝不能静默跳过流程。如果某个流程无法完成，请将其报告为 BLOCKED，并说明已尝试的操作以及用户应如何修复。”**

每个应用模块应在底部包含一个“已知失败模式”部分，其中填充在代码扫描期间发现的应用特定的怪癖。

## 4e. GitHub Actions 工作流（仅当用户在类别7 中回答是时）

### 替换现有的 QA 工作流

首先，在`.github/workflows/`中检查任何现有的与 QA 相关的 工作流（例如，`cli-qa-droid-exec.yml`，`automated-qa-prod.yml`，`automated-qa-dev.yml`）。新的统一的`qa.yml`将取代所有这些。删除或重命名旧的工作流，并在验证总结中记录这一点，以便用户可以审查。

### 生成`.github/workflows/qa.yml`，遵循以下模式：

**触发器：**

- 如果项目使用预览部署并且用户要求等待它们，请使用在部署工作流完成后运行的`workflow_run`触发器。在代码库分析期间，识别所有产生预览 URL 的部署工作流（前端和后端可能独立部署）。QA 工作流必须等待所有这些工作流完成，以便在测试之前所有预览环境都准备好。示例：
  ```yaml
  on:
    workflow_run:
      workflows: ['<deploy-frontend-workflow>', '<deploy-backend-workflow>'] # list ALL deploy workflows found
      types: [completed]
  ```
  如果任何部署失败，QA 仍然应该运行，但报告受影响的应用程序的测试为阻塞状态。该工作流应从 PR 评论中提取预览 URL（查找带有标记模式的部署机器人评论）。
- 还应包含`pull_request`触发器作为备用选项（当`workflow_run`未从非默认分支触发时）
- `workflow_dispatch` — 允许手动触发

**多个预览部署：** 一些项目独立地部署前端和后端，每个都有自己的预览 URL。在代码库分析期间，检查项目是否有在 PR 上运行的多个部署工作流。如果有：

- 确定每个预览 URL 是如何生成的（PR 评论标记、基于分支名的 URL 模式、部署输出）
- QA 工作流必须等待所有部署完成后再进行测试
- 每个应用程序的子 skill 应记录如何解决其预览 URL
- 后端子 skill 应在后端也获得每 PR 部署时，测试其预览 URL（不是共享的开发后端）

**核心步骤（按此确切顺序）：**

1. 使用 `fetch-depth: 0` 进行检出（用于 git diff 分析所需）
2. 如果使用预览部署：从触发的工作流或 PR 评论中提取预览 URL
3. 如果配置文件中说 imagemagick: true，则安装 ImageMagick (`sudo apt-get install -y -qq imagemagick`)
4. 设置 Node.js (`actions/setup-node@v4`，node-version 22) —— 对于 tuistory 和其他基于 Node 的工具所需
5. 根据检测到的应用类型安装测试工具：
   - 如果存在 CLI 应用（test_tool: tuistory）：`npm install -g tuistory`
   - 如果 CLI 应用有需要依赖项的 build_command：在 QA 步骤之前运行 `npm install` (或项目的包管理器 install)，以便可以构建 CLI 二进制文件
   - 如果存在 Web 应用（test_tool: agent-browser）：agent-browser 已内置在 droid 中，无需额外安装
6. 安装 droid CLI：`curl -fsSL https://app.factory.ai/cli | sh`
7. 运行 QA：使用 `droid exec --auto high` 命令并传递这些 CI 模式的指令作为提示词：
   - "你正在运行在一个非交互式持续集成环境中。没有可用的人类用户。"
   - "不要使用 AskUser，不要等待确认，不要暂停以获取输入。"
   - "运行 qaskill。将最终报告写入 qa-results/report.md"
8. **(只有在 `failure_learning` 是 `auto_commit` 或 `open_pr` 时）** 应用来自 JSON 的 skill 更新。添加一个步骤：

   - 从 `apply-qa-skill-updates` 运行 `apps/scripts/` 脚本：
     ```yaml
     - name: Apply skill updates from QA
       if: always() && steps.qa.outcome != 'cancelled'
       run: npx tsx apps/scripts/src/apply-qa-skill-updates/index.ts qa-results/skill-updates.json
     ```
   - 对于 `auto_commit`：提交并推送到 PR 分支
   - 对于 `open_pr`：创建新分支，提交更改，并打开一个针对 PR 分支的草稿 PR。
   - 参见下面 `auto_commit`/`open_pr` 块中的示例

   **`auto_commit` 提交步骤：**

   ```yaml
   - name: Commit skill updates
     if: always() && steps.apply-updates.outcome == 'success'
     run: |
       if git diff --quiet .factory/skills/; then exit 0; fi
       git config user.name "github-actions[bot]"
       git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
       git add .factory/skills/
       git commit -m "chore(qa): update failure catalog from QA run #\${{ github.run_number }}"
       git push origin HEAD:\${{ steps.pr.outputs.ref }}
   ```

   **`open_pr` 提交 + PR 步骤：**

   ```yaml
   - name: Open PR with skill updates
     if: always() && steps.apply-updates.outcome == 'success'
     env:
       GH_TOKEN: \${{ secrets.GITHUB_TOKEN }}
     run: |
       if git diff --quiet .factory/skills/; then exit 0; fi
       BRANCH="qa/catalog-\${{ github.run_number }}"
       git config user.name "github-actions[bot]"
       git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
       git checkout -b "$BRANCH"
       git add .factory/skills/
       git commit -m "chore(qa): update failure catalog from QA run #\${{ github.run_number }}"
       git push origin "$BRANCH"
       gh pr create --base "\${{ steps.pr.outputs.ref }}" --head "$BRANCH" \
         --title "chore(qa): update failure catalog from QA run #\${{ github.run_number }}" \
         --body "Auto-generated from QA run on PR #\${{ steps.pr.outputs.number }}." --draft
   ```

9. 上传制品（屏幕截图、GIF、报告、skill-updates.json）通过 `actions/upload-artifact@v4`，保留期限为14 天
10. 在 PR 备注中发布/更新报告（参见下方的 PR 备注部分）

**工作流必须传递给 QA 步骤的环境变量：**

- 所有从 config.yaml `credentials_source` 字段和认证配置中识别出的秘密
- `CI: true`: 以便 skill 知道自主运行
- 使用代码库分析中发现的秘密名称 -- 不要硬编码项目特定的名称

**PR 评论发布：** 在"发布 QA 报告作为 PR 评论"步骤中:

- 如果存在 `qa-results/report.md`，则读取它；否则将 `qa-output.txt` 包裹在一个 details 块中作为备选
- 确保报告始终以 `## QA Report` 标题开头（如果没有包含该标题，则添加它）
- 报告已经包含了内联文本快照（围栏代码块）作为证据 -- 不需要上传/嵌入图片
- 在评论底部追加一个带有附件下载链接和工作流运行链接的尾注
- 在评论主体顶部插入隐藏 HTML 标记：`<!-- qa-report -->`
- 发布前，在现有 PR 评论中搜索以 `<!-- qa-report -->` 开始的一个。如果找到，则更新该评论（PATCH）而不是创建一个新的。只有在没有现有 QA 评论时才创建新的评论
- 这确保每个 PR 恰好只有一个 QA 评论，并且每次推送都会更新，不会出现大量评论
- 上传任何图像文件（屏幕截图、GIF）仅作为构建产物 -- 不要在 PR 备注中尝试嵌入它们

**可靠性**:

- 使用基于 PR 号的适当并发组（处理 `pull_request` 和 `workflow_run` 事件形状），并启用正在进行中的取消操作
- 设置作业超时时间（20-25 分钟）和 QA 步骤超时时间（15-20 分钟）
- 在 QA 步骤中使用 `continue-on-error: true`，以便即使在失败时报告始终会被发布
- 从现有工作流中使用此仓库中的 runner 类型（检查 `.github/workflows/` 目录以获取 runner 标签）

### 自测试属性

QA skill 会测试应用程序本身。当对 QA skill 文件（`.factory/skills/qa/**`）进行更改但未修改应用代码时，差异分析将检测到这一点并报告 INCONCLUSIVE -- 由于没有受影响的应用程序流程将运行，因此不会执行任何应用流程。

---

# 阶段 5：验证

生成所有文件后:

1. 向用户展示所生成内容的摘要
2. 列出所有创建的文件及其简要描述
3. 建议："你可以通过运行 /qa 来调用 skill 进行测试，或者通过打开一个 PR 触发 GitHub 行动（如果已生成）。"

**重要 -- GitHub 密钥设置 (FAC-17916):** 4. 如果生成了 GitHub Actions 工作流，请务必提示词用户在他们的 GitHub 仓库中添加所需的密钥。分析生成的工作流和 config.yaml 来编译 EXACT 需要的密钥列表。将其作为检查清单呈现:

```
The QA workflow needs these GitHub repository secrets to work in CI:

  [ ] <SECRET_NAME> -- <what it's for>
      Get it from: <where to get it>
  ...

Add them at: https://github.com/<owner>/<repo>/settings/secrets/actions
```

根据生成的工作流和 config.yaml 动态填充此列表。列出工作流 `env:` 块中引用的所有密钥，并解释每个密钥的作用以及如何获取它们。不要在提示词中硬编码项目特定的密钥名称 -- 从生成的内容中发现它们。

5. 提醒他们任何其他手动设置的需求（例如，测试账户、API 访问权限、环境白名单）

---

# 重要指南

- 绝不能在生成的文件中存储真实凭据、密码、API 密钥或 token。只能记录其位置（env 变量名或密钥管理路径）。
- 协调器 SKILL.md 必须轻量级。应用模块包含详细的测试步骤。
- 每次完成问卷类别后，保存进度到 .install-progress.yaml 文件，以便用户在中断时可以恢复。
- 如果用户在任何时间点说“重新开始”，删除 .install-progress.yaml 并从阶段 2 重新开始。
- 根据问卷答案和代码库分析始终从头生成所有文件，即使这些文件已经存在也是如此。覆盖它们。用户可能已更改他们的答案或生成规则可能已被更新。
