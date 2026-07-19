---
name: install-code-review
description: >
  安装并配置 Factory Droid 以在 GitHub 或 GitLab 上自动审查代码。
  支持单仓库设置或跨数百个仓库的组织/团队级部署。
  当用户希望在其仓库中设置 Droid 审查时使用此功能。
user-invocable: true
---

# 安装代码审查

您正在为 GitHub 或 GitLab 上的自动代码审查安装 Factory Droid。

## 规则（必须严格按照这些执行，不允许有任何例外）

1. **绝不跳过步骤。** 按顺序执行。如果某一步失败，请停止并告诉用户如何修复。
2. **绝不自行假设。** 每个决策点都必须通过 AskUser 获取用户输入。不要擅自选择默认值，也不要跳过问题。
3. **绝不提交机密。** 工作流文件通过 `\${{ secrets.FACTORY_API_KEY }}`（GitHub）或 `$FACTORY_API_KEY`（GitLab）引用机密；绝不能把真实密钥写入文件。
4. **绝不转义工作流 YAML 中的 `\${{ ... }}`。** 按原样写表达式（`\${{ secrets.FACTORY_API_KEY }}`），不要写成 `\\${{ ... }}`。为避免 shell 展开，请使用步骤 8 中的 base64 原始输入，不要添加反斜杠。
5. **并行运行所有先决条件检查**（步骤 1）。
6. **使用列出的精确命令**。不要即兴使用替代命令。
7. **使用 AskUser** 对每一个问题进行提问。不要以纯文本形式询问问题。
8. **在执行任何创建、修改或删除资源的操作之前确认**。
9. **跟踪多仓库操作的进度**。显示正在处理哪个仓库。

## 步骤 0: 检测平台

检查 git 远程以检测平台：

```bash
git remote get-url origin 2>/dev/null
```

- 如果 URL 包含 `github.com` → **GitHub**。转到步骤 1（GitHub）。
- 如果 URL 包含 `gitlab.com` 或已知的 GitLab 实例 → **GitLab**。继续第 1 步（GitLab）。
- 如果没有远程仓库或模糊不清：使用 AskUser:
  ```
  1. [question] Which platform are you using?
  [topic] Platform
  [option] GitHub
  [option] GitLab
  ```

一旦确定了平台，请仅遵循该平台的步骤。不要混用 GitHub 和 GitLab 的步骤。

---

# GitHub 流程

## 第 1 步（GitHub）: 验证先决条件

并行运行所有四个命令。如果任何一个失败，请停止并显示修复方法。

| 检查         | 命令                                                                              | 在失败时                                                    |
| ------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| gh 已安装  | `gh --version`                                                                       | 告诉用户安装：`brew install gh` (macOS)               |
| 已认证 | `gh auth status`                                                                     | 告诉用户运行：`gh auth login`                             |
| 权限范围        | `gh auth status -t 2>&1` — 查看 "Token scopes" 中是否有 `repo`, `read:org`, `workflow` | 告诉用户运行：`gh auth refresh -s repo,read:org,workflow` |
| API 访问    | `gh api user --jq .login`                                                            | 告诉用户运行：`gh auth refresh`                           |

只有当所有四项都通过后才能继续。

## 第2 步（GitHub）：确定权限范围

使用 AskUser:

```
1. [question] What scope do you want to set up Droid for?
[topic] Scope
[option] Single repository
[option] Multiple repositories (org-wide)
```

- 如果 **单个仓库**：运行 `git remote get-url origin 2>/dev/null` 检测 `owner/repo`。如发现，请与用户确认。如未发现，则使用 AskUser 询问 `owner/repo`。然后转到第4 步。
- 如果 **多个仓库**：转到第3 步。

## 第3 步（GitHub）：组织级设置

### 3a. 识别组织

列出用户的组织：`gh api user/orgs --jq '.[].login'`

使用 AskUser 询问哪个组织。将命令输出中的组织作为选项包括进去。

验证它是否存在：`gh api /orgs/{org} --jq '.login'`

### 3b. 检查 GitHub App 安装

运行：`gh api /orgs/{org}/installations --jq '.installations[] | select(.app_slug == "factory-droid") | .id'`

- 如果输出为空（未返回任何 ID）：告诉用户确切的内容如下：
  > "Factory Droid GitHub 应用未安装在该组织中。请前往：https://app.factory.ai/settings/integrations/github/start 安装它——授予对‘所有仓库’的访问权限或选择特定的仓库。完成后告诉我。"
  > 然后等待。当用户确认后，重新运行该命令。如果仍然为空，则重复该消息。
- 如果返回了一个 ID：继续。

### 3c. 检查 FACTORY_API_KEY 组织秘密

运行：`gh secret list --org {org} 2>/dev/null | grep FACTORY_API_KEY`

- 如果未匹配到：告诉用户如下内容：
  > "FACTORY_API_KEY 没有设置为组织秘密。要进行设置，请按照以下步骤操作："
  > "1. 在 https://app.factory.ai/settings/api-keys" 生成一个密钥"
  > "2. 运行: `gh secret set FACTORY_API_KEY --org {org} --visibility all`"
  > 然后等待用户确认。重新检查。如果因 `admin:org` 范围的权限错误而失败，请先运行 `gh auth refresh -h github.com -s admin:org`。
- 如果已找到匹配项：继续执行。

### 3d. 选择目标仓库

运行: `gh repo list {org} --limit 1000 --json name,isArchived,isFork --jq '.[] | "\(.name) | archived:\(.isArchived) | fork:\(.isFork)"'`

使用 AskUser:

```
1. [question] Which repos should Droid be enabled on?
[topic] Repo-selection
[option] All repos
[option] Filter by pattern
[option] Let me select manually
```

如果为“所有仓库”或“按模式过滤”：统计已归档的仓库数量和分支仓库的数量。使用 AskUser:

```
1. [question] Found X archived repos. Exclude them?
[topic] Archived
[option] Yes, exclude archived repos
[option] No, include them

2. [question] Found Y forked repos. Forked repos cannot use required workflows (Option C). Include them?
[topic] Forks
[option] Yes, include forks
[option] No, exclude forks
```

然后检查哪些仓库已经包含 Droid 工作流。对于每个选定的仓库运行: `gh api /repos/{org}/{repo}/contents/.github/workflows/ --jq '.[].name' 2>/dev/null`

统计已存在 `droid.yml` 或 `droid-review.yml` 的仓库数量。如果存在，请使用 AskUser.

```
1. [question] X repos already have Droid workflow files. What do you want to do?
[topic] Existing-workflows
[option] Skip repos that already have workflows
[option] Overwrite existing workflow files
```

## 步骤 4 (GitHub): 检查权限 (仅单仓库适用)

运行：`gh api /repos/{owner}/{repo} --jq '.permissions.admin'`

如果结果是 `false`，告诉用户：

> "你没有此仓库的管理员权限。你可以继续操作，但可能需要仓库管理员批准 GitHub App 安装、添加 FACTORY_API_KEY 密钥，并合并工作流 PR。"

使用 AskUser:

```
1. [question] Continue without admin permissions?
[topic] Permissions
[option] Yes, continue anyway
[option] No, cancel
```

## 步骤 5 (GitHub): GitHub 应用程序安装（仅单仓库）

运行：`gh api /repos/{owner}/{repo}/installation --jq '.id' 2>/dev/null`

如果为空或错误：告诉用户：

> "Factory Droid GitHub 应用未安装在该仓库中。请访问 https://app.factory.ai/settings/integrations/github/start 安装它。完成后告诉我。"

打开浏览器：`open https://app.factory.ai/settings/integrations/github/start 2>/dev/null`

等待用户确认。重新运行检查。如果仍未安装，则重复此步骤。

## 步骤 6 (GitHub): 工作流选择

使用 AskUser 以这些具体问题进行提问：

```
1. [question] Enable @droid tag responses? (Responds to @droid mentions in issues and PR comments)
[topic] Tag-responses
[option] Yes
[option] No

2. [question] Enable automatic code review on new PRs?
[topic] Auto-review
[option] Yes
[option] No

3. [question] Enable automatic security review on new PRs?
[topic] Security-review
[option] Yes
[option] No

4. [question] Review depth for automatic reviews?
[topic] Review-depth
[option] deep (thorough)
[option] shallow (fast, cost-effective)
```

至少启用一个标签响应或自动审查。如果用户同时禁用了两者，请告知他们：“必须启用至少一个工作流。请启用标签响应或自动审查。”

## 步骤 7 (GitHub): 选择分发策略 (仅多仓库适用)

首先，检查组织计划：`gh api /orgs/{org} --jq '.plan.name'`

使用 AskUser。如果计划是 `free`，仅显示选项 A 和 B。如果是 `team` 或 `enterprise` 计划，则显示所有三个：

```
1. [question] How should the workflow files be added to these repos?
[topic] Strategy
[option] Direct commit (fastest, commits to each repo's default branch)
[option] Open PRs (safest, opens a PR in each repo for review)
[option] Required workflows (zero per-repo files, enforced via org ruleset — requires Team/Enterprise)
```

如果计划是 `free` 且用户询问所需的工作流，请告诉他们：

> "必需的工作流需要 GitHub 团队或企业云版。你的组织在免费计划中。"

## 第 8 步（GitHub）: 执行

在执行之前，请使用 AskUser 确认：

```
1. [question] Ready to proceed? Here is what will happen: [describe exactly what will be created/modified, how many repos, which strategy]
[topic] Confirm
[option] Yes, go ahead
[option] No, cancel
```

**CRITICAL: 使用此模式仅编码工作流内容。** `echo|base64`、`printf|base64` 和在双引号 shell 字符串中嵌入 YAML 可能会损坏 `\${{ ... }}`。使用单引号的 Python 慢写，并使用原始字符串：

```bash
B64=$(python3 << 'PYEOF'
import base64
content = r"""<workflow YAML; keep \${{ ... }} literal, no backslashes>"""
print(base64.b64encode(content.encode()).decode())
PYEOF
)
```

验证后再提交（便携式）：`echo "$B64" | (base64 -d 2>/dev/null || base64 -D) | grep -F 'secrets.FACTORY_API_KEY'` 确保解码输出包含 **无** `\\${{` / `\$\{\{`。以 `gh api` 传递给 `-f content="$B64"`。

### 选项 A: 直接提交

对于每个选定的仓库：

1. 检查工作流文件是否已存在（尊重步骤3d 中的跳过/覆盖选择）。
2. 获取默认分支：`gh api /repos/{org}/{repo} --jq '.default_branch'`
3. 使用 Step 8 的 heredoc 编码每个工作流文件，然后:
   `gh api /repos/{org}/{repo}/contents/.github/workflows/{filename} -X PUT -f message="feat: Add {filename} workflow" -f content="$B64"` 如果覆盖，则首先获取 SHA（`--jq '.sha'`），并添加 `-f sha={existing_sha}`。
4. 打印：`✓ {repo}: committed {filenames}`
5. 发生错误时，打印：`✗ {repo}: {error message}` 并继续处理下一个仓库。

### 选项 B：创建 PR

对于每个选定的仓库：

1. 检查是否存在分支 `add-factory-workflows-*`（幂等性）：`gh api /repos/{org}/{repo}/git/refs --jq '.[].ref' 2>/dev/null | grep add-factory-workflows`
   如果找到，跳过并打印：`⊘ {repo}: PR branch already exists, skipping`
2. 获取默认分支：`gh api /repos/{org}/{repo} --jq '.default_branch'`
3. 获取最新 SHA：`gh api /repos/{org}/{repo}/git/refs/heads/{default_branch} --jq '.object.sha'`
4. 创建分支：`gh api /repos/{org}/{repo}/git/refs -f ref=refs/heads/add-factory-workflows-{timestamp} -f sha={sha}`
5. 使用 Step 8 的 heredoc 编码每个工作流文件，然后:
   `gh api /repos/{org}/{repo}/contents/.github/workflows/{filename} -X PUT -f message="feat: Add {filename} workflow" -f content="$B64" -f branch=add-factory-workflows-{timestamp}`
6. 创建 PR：`gh pr create --repo {org}/{repo} --head add-factory-workflows-{timestamp} --base {default_branch} --title "Enable Factory Droid automated code review" --body "{pr_body}"`
   PR 说明必须包含：添加了哪些工作流，链接到 https://app.factory.ai/settings/api-keys, https://docs.factory.ai
7. 打印：`✓ {repo}: PR opened — {pr_url}`
8. 发生错误时，打印：`✗ {repo}: {error message}` 并继续处理下一个仓库。

### 选项 C: 必要的工作流

1. 运行：`gh api /orgs/{org} --jq '.plan.name'` — 如果是 `free`，停止并告知用户这需要 Team/Enterprise 版本。
2. 使用 AskUser 询问中央仓库名称：
   ```
   1. [question] Name for the central workflows repo?
   [topic] Repo-name
   [option] droid-workflows
   ```
3. 检查仓库是否存在：`gh api /repos/{org}/{repo_name} --jq '.name' 2>/dev/null`
4. 如果未找到，创建它：`gh api /orgs/{org}/repos -f name={repo_name} -f visibility=public -f description="Reusable Droid workflows" -f auto_init=true`
5. 将可重用的工作流文件（来自下方的可重用工作流模板）提交到中央仓库，使用 GitHub Contents API。
6. 获取 repo ID: `gh api /repos/{org}/{repo_name} --jq '.id'`
7. 获取工作流 SHA: `gh api /repos/{org}/{repo_name}/contents/.github/workflows/{filename} --jq '.sha'`
8. 使用 AskUser 询问关于排除项:
   ```
   1. [question] Exclude any repos from the required workflow?
   [topic] Exclusions
   [option] No exclusions (apply to all repos)
   [option] Exclude specific repos
   ```
   如果排除，则询问 repo 名称/模式。
9. 创建组织规则集:
   ```
   gh api /orgs/{org}/rulesets -X POST --input - <<EOF
   {
     "name": "Require Droid Review",
     "target": "branch",
     "enforcement": "active",
     "conditions": {
       "ref_name": {
         "include": ["~DEFAULT_BRANCH"],
         "exclude": []
       },
       "repository_name": {
         "include": ["~ALL"],
         "exclude": ["{excluded_repos}"]
       }
     },
     "rules": [
       {
         "type": "workflows",
         "parameters": {
           "workflows": [
             {
               "repository_id": {repo_id},
               "path": ".github/workflows/droid-review-reusable.yml",
               "ref": "main",
               "sha": "{workflow_sha}"
             }
           ]
         }
       }
     ]
   }
   EOF
   ```
10. 如果 API 返回 403，请告诉用户: "组织规则集需要管理员权限。请请求组织管理员运行此操作，或者改用选项 A 或 B。"
11. 成功后打印: `✓ Ruleset "Require Droid Review" created. Applies to all repos`（或 `all repos except {excluded}`）。
12. 告诉用户: "稍后可在以下位置管理排除项: https://github.com/organizations/{org}/settings/rules"

### 单个 repo:

1. 获取默认分支: `gh api /repos/{owner}/{repo} --jq '.default_branch'`
2. 获取最新 SHA: `gh api /repos/{owner}/{repo}/git/refs/heads/{default_branch} --jq '.object.sha'`
3. 创建分支: `gh api /repos/{owner}/{repo}/git/refs -f ref=refs/heads/add-factory-workflows-{timestamp} -f sha={sha}`
   使用 `date +%s` 作为时间戳。
4. 使用 Step 8 的 heredoc 编码每个工作流文件，然后:
   `gh api /repos/{owner}/{repo}/contents/.github/workflows/{filename} -X PUT -f message="feat: Add {filename} workflow" -f content="$B64" -f branch=add-factory-workflows-{timestamp}` 验证（便携式）:`gh api /repos/{owner}/{repo}/contents/.github/workflows/{filename} --jq '.content' | (base64 -d 2>/dev/null || base64 -D) | tee /tmp/_droid_chk | grep -F 'secrets.FACTORY_API_KEY'` 然后 `! grep -F '\\${{' /tmp/_droid_chk` — 两者都必须成功。
5. 创建 PR:
   `gh pr create --repo {owner}/{repo} --head add-factory-workflows-{timestamp} --base {default_branch} --title "feat: Add Factory GitHub workflows" --body "{pr_body}"`
6. 打印 PR URL。

## Step 9 (GitHub): 总结

显示结果表格:

| 类别   | 数量 | 详情                                      |
| ---------- | ----- | -------------------------------------------- |
| 配置 | X     | 包含工作流提交或打开 PR 的仓库 |
| 已打开的 PRs | Y     | 指向前5 个 PR 的链接                         |
| 跳过了    | Z     | 已经配置，用户选择了跳过       |
| 失败     | W     | repo 名称+错误原因                   |

如果有任何仓库失败，请使用 AskUser:

```
1. [question] {W} repos failed. Retry with a different strategy?
[topic] Retry
[option] Retry failed repos with direct commit
[option] Retry failed repos with PRs
[option] Skip, I'll handle them manually
```

如果 FACTORY_API_KEY 未验证（单仓库流程跳过组织密钥检查），请提醒：

> "**重要: 添加您的 FACTORY_API_KEY**"
> "1. 在 https://app.factory.ai/settings/api-keys" 生成一个密钥"
> "2. 前往 repo 设置 > 秘密和变量 > 行动 > 新仓库秘密"
> "3. 名称: `FACTORY_API_KEY`，值: 您生成的密钥"

## 可重用的工作流模板

由选项 C 使用。将这些内容提交到中央仓库。

### droid-reusable.yml

```yaml
name: Droid Tag (Reusable)

on:
  workflow_call:
    secrets:
      factory_api_key:
        required: true

jobs:
  droid:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          fetch-depth: 1
      - name: Run Droid Exec
        uses: Factory-AI/droid-action@main
        with:
          factory_api_key: \${{ secrets.factory_api_key }}
```

### droid-review-reusable.yml

```yaml
name: Droid Auto Review (Reusable)

on:
  workflow_call:
    secrets:
      factory_api_key:
        required: true
    inputs:
      automatic_security_review:
        type: boolean
        default: false
      review_depth:
        type: string
        default: deep

jobs:
  droid-review:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          fetch-depth: 1
      - name: Run Droid Auto Review
        uses: Factory-AI/droid-action@main
        with:
          factory_api_key: \${{ secrets.factory_api_key }}
          automatic_review: true
          automatic_security_review: \${{ inputs.automatic_security_review }}
          review_depth: \${{ inputs.review_depth }}
```

## 独立工作流文件模板

由选项 A、B 和单仓库流程使用。

### droid.yml

生成当@droid 标签响应被启用时:

```yaml
name: Droid Tag

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]
  pull_request:
    types: [opened, edited]

jobs:
  droid:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@droid')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@droid')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@droid')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@droid') || contains(github.event.issue.title, '@droid'))) ||
      (github.event_name == 'pull_request' && (contains(github.event.pull_request.body, '@droid') || contains(github.event.pull_request.title, '@droid')))
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          fetch-depth: 1
      - name: Run Droid Exec
        uses: Factory-AI/droid-action@main
        with:
          factory_api_key: \${{ secrets.FACTORY_API_KEY }}
```

### droid-review.yml

生成当自动代码审查被启用时。从这个基础开始:

```yaml
name: Droid Auto Review

on:
  pull_request:
    types: [opened, ready_for_review, reopened]

concurrency:
  group: \${{ github.workflow }}-\${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  droid-review:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          fetch-depth: 1
      - name: Run Droid Auto Review
        uses: Factory-AI/droid-action@main
        with:
          factory_api_key: \${{ secrets.FACTORY_API_KEY }}
          automatic_review: true
```

然后根据第6 步中的用户选择，在`with:`下添加这些行:

- 如果启用了安全审查: 添加 `automatic_security_review: true`
- 如果审查深度较浅: 添加 `review_depth: shallow`
- 如果审查深度较深: 不要添加 `review_depth`（深度是默认值）

## 错误处理 (GitHub)

| 错误                                | 原因                             | 修复                                                                           |
| ------------------------------------ | --------------------------------- | ----------------------------------------------------------------------------- |
| `HTTP 404` 在安装点 | 用户不是组织管理员          | 告诉用户询问组织管理员，或使用单仓库流程                        |
| `HTTP 403` 在设置密钥时             | 缺少 `admin:org` 范围         | 告诉用户：`gh auth refresh -h github.com -s admin:org`                       |
| `HTTP 403` 在规则集上               | 免费计划或非组织管理员        | 告诉用户升级计划或询问组织管理员                                    |
| `HTTP 422` 在文件创建时            | 文件已存在且没有 SHA   | 获取现有 SHA 并使用 `-f sha={sha}` 重试                            |
| 分支保护阻止推送        | 仓库有分支保护        | 建议打开 PR 而不是直接提交                                  |
| `startup_failure` 在工作流中        | 使用可重用的工作流 fork 仓库 | fork 仓库不能调用跨仓库的可重用工作流。请使用独立文件。 |

---

# GitLab 流程

## 步骤 1（GitLab）: 验证前提条件

并行运行这些检查。如果有任何失败，请停止并显示修复方法。

| 检查          | 命令                                               | 在失败时                                                                                 |
| -------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| glab 已安装 | `glab --version`                                      | 告诉用户安装：`brew install glab`（macOS）或参见 https://gitlab.com/gitlab-org/cli |
| 已认证  | `glab auth status`                                    | 告诉用户运行：`glab auth login`                                                        |
| API 访问     | `glab api user` 并从 JSON 响应中解析用户名 | 告诉用户运行：`glab auth login`并检查其连接                             |

**重要**：`glab api` 不支持 `--jq`。要从 API 响应中提取字段，请始终通过 python 管道：`glab api <endpoint> | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['field'])"`

只有当所有步骤都通过后才能继续。

## 第2 步（GitLab）：确定范围

使用 AskUser:

```
1. [question] What scope do you want to set up Droid for?
[topic] Scope
[option] Single project
[option] Multiple projects (group-wide)
```

- 如果**单个项目**：运行 `git remote get-url origin 2>/dev/null` 检测项目路径。解析 GitLab 项目路径（例如，`group/project`）。与用户确认后，转到第4 步（GitLab）。
- 如果**多个项目**：转到第3 步（GitLab）。

## 步骤 3（GitLab）: 组级设置

### 3a. 确定组

列出用户的组：`glab api groups -X GET -f min_access_level=30 | python3 -c "import sys,json; [print(g['full_path']) for g in json.load(sys.stdin)]"`

使用 AskUser 询问哪个组。将命令输出中的组作为选项包含进去。

为了对 API 进行 URL 编码（例如，`my-group/sub-group` → `my-group%2Fsub-group`），使用：`python3 -c "import urllib.parse; print(urllib.parse.quote('{group_path}', safe=''))"`

验证其是否存在：`glab api groups/{group_url_encoded} | python3 -c "import sys,json; print(json.load(sys.stdin)['full_path'])"`

### 3b. 检查 FACTORY_API_KEY 和 GITLAB_TOKEN CI/CD 变量

droid-review CI/CD 组件需要两个被遮掩的 CI/CD 变量：

| 变量          | 目的                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| `FACTORY_API_KEY` | 用于将 Droid CLI 验证到 Factory 的推理端点                                       |
| `GITLAB_TOKEN`    | 允许审查任务发布内联 MR 评论并使用 GitLab REST API 更新粘性跟踪笔记 |

必须在所有目标项目继承的级别设置为**遮罩、非受保护**的 CI/CD 变量。（非受保护是必需的，因为变量需要对合并请求管道可用，默认情况下这些管道运行于非受保护分支上）

> 注意：`CI_JOB_TOKEN` 有意不使用 — 它缺乏创建 MR 备注/讨论的权限。模板要求一个具有 `api` 范围的真实项目、组或个人访问令牌。

> **安全权衡——继续之前请向用户说明：**
>
> 一个具有 `GITLAB_TOKEN` 范围的遮罩、非受保护 `api` 可供 **每个合并请求管道** 使用，包括从分支或不太可信赖的贡献者处打开的 MR。管道可以从环境读取变量并窃取它；攻击者获取令牌后将获得该令牌的全部 API 权限，直到它被轮换。
>
> 推荐的缓解措施（按优先级递减顺序排列）：
>
> 1. **使用最小的工作范围**。优先选择项目访问令牌而非组访问令牌，再优先选择个人访问令牌。一个局限于单个项目范围内的令牌只能对该单一项目造成滥用；而组令牌可以对组中的每个项目造成滥用。
> 2. **使用专用的机器人账户或细粒度的令牌** 而不是长期绑定到真实用户的个人访问令牌。
> 3. **使用最小的角色**。`Developer` 对于审查工作（发布备注 + 读取 MR 数据）足够了。如果不需要，不要授予 `Maintainer`/`Owner` 角色。
> 4. **为 token 设置较短的过期时间**（GitLab 最长支持 1 年；若贡献者模式开放，应更早轮换）。
> 5. **对于接受来自不可信赖贡献者的分支-MR 的项目**，考虑：
>    - 禁用来自分支合并请求的管道运行（设置 > CI/CD > 通用管道 > “为分支合并请求运行管道”），并/或
>    - 仅在受保护分支上通过 `rules:` 覆盖运行 Droid 审查，并将变量标记为 Protected 而不是 non-protected（这也禁用了 MR 管道上的审查，因此这是一个权衡——用户必须做出选择）。
>
> 在确定组级非受保护之前，询问用户其贡献模型。如果他们不知道，默认使用 **per-project Project Access Tokens** 并在步骤 8 中明确显示权衡。

GitLab CI/CD 变量可以在层次结构的多个级别设置（顶级组、子组或项目）。询问用户希望在哪里设置它们：

```
1. [question] Where should the FACTORY_API_KEY and GITLAB_TOKEN CI/CD variables be set? Setting them at a higher level means all descendant projects inherit them automatically.
[topic] Variable-Scope
[option] Top-level group (all projects in the group inherit it)
[option] A specific subgroup (only projects in that subgroup inherit it)
[option] Per-project (I'll set it on each project individually)
```

然后检查所选级别的每个变量是否已经存在。运行 BOTH 检查（尽可能并行执行）：

对于组/子组：

- `glab api groups/{chosen_group_url_encoded}/variables/FACTORY_API_KEY | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('key','NOT_FOUND'))"`
- `glab api groups/{chosen_group_url_encoded}/variables/GITLAB_TOKEN | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('key','NOT_FOUND'))"`

对于项目：

- `glab api projects/{project_url_encoded}/variables/FACTORY_API_KEY | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('key','NOT_FOUND'))"`
- `glab api projects/{project_url_encoded}/variables/GITLAB_TOKEN | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('key','NOT_FOUND'))"`

对于每个缺失的变量，告诉用户如何设置它：

**如果 `FACTORY_API_KEY` 为 `NOT_FOUND`：**

> "FACTORY_API_KEY 在 {chosen_level} 没有设置为 CI/CD 变量。要进行设置："
> "1. 在 https://app.factory.ai/settings/api-keys" 生成一个密钥"
> "2. 前往 {chosen_level} 设置 > CI/CD > 变量"
> "3. 添加变量: Key=`FACTORY_API_KEY`，Value=你的密钥，勾选 '遮掩变量'，不勾选 '保护变量'"
> 或运行：`glab api {groups_or_projects}/{url_encoded}/variables -X POST -f key=FACTORY_API_KEY -f value=YOUR_KEY -f masked=true -f protected=false`
> 等待用户确认。重新检查。

**如果 `GITLAB_TOKEN` 为 `NOT_FOUND`:**

> "GITLAB_TOKEN 没有在 {chosen_level} 的 CI/CD 变量中设置。审查任务使用此令牌来发布合并请求评论并更新跟踪笔记。"
> ""
> "选择适用于 {chosen_level} 的最合适的令牌类型："
> " - **组访问令牌**（推荐用于全局配置）：{group_url}/-/settings/access_tokens — 创建一个名为 `droid-bot` 且角色为 `Developer`（或更高）和带有 `api` 权限的令牌。"
> " - **项目访问令牌**（单个项目配置）：{project_url}/-/settings/access_tokens — 同样的角色和权限。"
> " - **个人访问令牌**（备用选项，与用户绑定）：https://gitlab.com/-/user_settings/personal_access_tokens — `api` 权限。"
> ""
> "然后前往 {chosen_level} 设置 > CI/CD > 变量 并添加：Key=`GITLAB_TOKEN`，Value=该令牌，勾选‘遮掩变量’，取消勾选‘保护变量’。"
> 或一旦你有了令牌值，请运行：`glab api {groups_or_projects}/{url_encoded}/variables -X POST -f key=GITLAB_TOKEN -f value=YOUR_TOKEN -f masked=true -f protected=false`
> 等待用户确认。重新检查。

- 如果两者都找到了：继续进行。

### 3c. 选择目标项目

运行: `glab api groups/{group_url_encoded}/projects -X GET -f include_subgroups=true -f per_page=100 | python3 -c "import sys,json; [print(f"{p['path_with_namespace']} | archived:{p['archived']}") for p in json.load(sys.stdin)]"`

使用 AskUser:

```
1. [question] Which projects should Droid be enabled on?
[topic] Project-selection
[option] All projects
[option] Filter by pattern
[option] Let me select manually
```

统计归档项目数量。如有，请使用 AskUser 确认排除。

然后检查哪些项目已经有一个包含 droid 任务的 `.gitlab-ci.yml`。对于每个选定的项目，URL-编码项目路径并运行：`glab api "projects/{project_url_encoded}/repository/files/.gitlab-ci.yml/raw?ref={default_branch}" 2>&1`

如果响应包含 "droid"，说明项目已经有 droid 配置。统计此类项目；如果数量大于零，请使用 AskUser：

```
1. [question] X projects already have Droid CI configuration. What do you want to do?
[topic] Existing-config
[option] Skip projects that already have Droid config
[option] Overwrite existing configuration
```

## 步骤 4 (GitLab): 检查权限（仅单个项目）

运行: `glab api projects/{project_url_encoded} | python3 -c "import sys,json; d=json.load(sys.stdin); p=d.get('permissions',{}); a=p.get('project_access') or p.get('group_access') or {}; print(a.get('access_level',0))"`

如果访问级别小于40（维护人），告诉用户：

> "您需要至少具有 Maintainer 访问权限才能添加 CI/CD 配置。您可以继续操作，但需要有人具有 Maintainer 访问权限来合并 MR。"

使用 AskUser 确认继续。

## 步骤 5 (GitLab): 管道配置选择

使用 AskUser:

```
1. [question] Enable automatic code review on merge requests?
[topic] Auto-review
[option] Yes
[option] No

2. [question] Enable automatic security review on merge requests?
[topic] Security-review
[option] Yes
[option] No

3. [question] Review depth for automatic reviews?
[topic] Review-depth
[option] deep (thorough)
[option] shallow (fast, cost-effective)
```

至少必须启用自动审查功能。

## 步骤 6 (GitLab): 选择分发策略（仅组级可用）

首先，通过测试安全策略 API 来检查组是否有 Ultimate 阶段：`glab api "groups/{group_url_encoded}/security/policies" 2>&1`

- 如果 404：群组处于免费/高级套餐。仅显示选项 A 和 B。
- 如果返回200 或其他响应：终极层级。显示所有三个选项。

使用 AskUser。如果为免费/付费版，仅显示选项 A 和 B：

```
1. [question] How should the CI configuration be added to these projects?
[topic] Strategy
[option] Direct commit (fastest, commits to each project's default branch)
[option] Open merge requests (safest, opens an MR in each project for review)
```

如果为 Ultimate 级别，显示全部三项：

```
1. [question] How should the CI configuration be added to these projects?
[topic] Strategy
[option] Direct commit (fastest, commits to each project's default branch)
[option] Open merge requests (safest, opens an MR in each project for review)
[option] Pipeline Execution Policy (zero per-project files, enforced centrally — requires Ultimate)
```

如果用户询问关于 Pipeline 执行策略（Free/Premium），告诉他们：

> “流水线执行策略需要 GitLab 最终版。您所在的组处于较低的层级。您可以在 https://about.gitlab.com/free-trial/ 开始免费试用，或者使用选项 A/B。”

## 步骤 7 (GitLab): 执行

在执行之前，使用 AskUser 来确认将要发生什么。

**关键：为 `glab api` 编码内容**

`.gitlab-ci.yml` 内容包含 `$` 字符（如 `$FACTORY_API_KEY`, `$CI_PIPELINE_SOURCE` 等 CI 变量）。为了避免 shell 展开，务必使用 python 进行 base64 编码：

```bash
B64=$(python3 << 'PYEOF'
import base64
content = """<yaml content here>"""
print(base64.b64encode(content.encode()).decode())
PYEOF
)
```

然后使用 `-f encoding=base64 -f "content=$B64"` 传递给 API 。

**关键：创建文件时选择 POST 还是 PUT**

在提交文件之前，始终检查目标分支上是否已存在该文件：`glab api "projects/{encoded}/repository/files/.gitlab-ci.yml?ref={branch}" 2>&1`

- 如果返回文件元数据（HTTP 200）：使用 `-X PUT` 更新
- 如果返回404：使用 `-X POST` 创建

这适用于主分支和默认分支。一个项目可能已经有一个现有的`.gitlab-ci.yml`文件，该文件会被复制到新分支中。

### GitLab 单个项目：

1. 获取默认分支：
   `glab api projects/{project_url_encoded} | python3 -c "import sys,json; print(json.load(sys.stdin)['default_branch'])"`
2. 检查默认分支上是否已经存在`.gitlab-ci.yml`:
   `glab api "projects/{project_url_encoded}/repository/files/.gitlab-ci.yml?ref={default_branch}" 2>&1`
   - 如果存在：从默认分支读取原始内容并追加 Droid 任务
   - 如果未执行：使用以下完整的 GitLab CI 模板:
3. 创建新分支: `glab api projects/{project_url_encoded}/repository/branches -X POST -f branch=add-factory-droid-review -f ref={default_branch}`
4. 使用 Python 对内容进行 Base64 编码（参见上面的编码说明）。
5. 提交文件 — 由于分支是从默认分支创建的，可能已经包含该文件，请使用 PUT:
   `glab api "projects/{project_url_encoded}/repository/files/.gitlab-ci.yml" -X PUT -f branch=add-factory-droid-review -f "content=$B64" -f encoding=base64 -f "commit_message=ci: add Factory Droid review pipeline"` 如果 PUT 返回 404（文件在分支上不存在），请使用 POST 重试。
6. 通过 API 创建 MR:
   `glab api "projects/{project_url_encoded}/merge_requests" -X POST -f source_branch=add-factory-droid-review -f target_branch={default_branch} -f "title=Enable Factory Droid automated code review" -f "description={mr_body}"` 从响应中解析 `web_url`。
7. 打印 MR URL。

### GitLab 多项目 (MRs):

遍历选定的项目。对于每个项目:

1. 检查分支 `add-factory-droid-review` 是否已存在（幂等性）:
   `glab api "projects/{encoded}/repository/branches/add-factory-droid-review" 2>&1` 如果找到，请检查是否存在现有 MR: `glab api "projects/{encoded}/merge_requests?source_branch=add-factory-droid-review&state=opened" | python3 -c "import sys,json; mrs=json.load(sys.stdin); print(mrs[0]['web_url'] if mrs else 'NONE')"` 打印: `⊘ {project}: MR already exists: {mr_url}`（或如果不存在打开的 MR，则打印 `branch already exists, skipping`）
2. 遵循单项目步骤以上的内容。
3. 按项目跟踪成功/失败情况。

### GitLab 多项目（直接提交）:

遍历选定的项目。对于每个项目:

1. 检查默认分支上是否已存在 `.gitlab-ci.yml`。
2. 如果存在：读取内容，检查是否已包含 droid 配置（使用 grep 搜索 "droid"）。如果存在且用户选择了跳过，则跳过此项目。
3. 如果存在但没有 droid 配置: 将 droid 作业追加到现有内容中。
4. Base64 编码并使用 Repository Files API 在默认分支上提交（如果已存在则 PUT，否则 POST）。
5. 按项目跟踪成功/失败情况。

### GitLab 方案 C: 管道执行策略 (仅限 Ultimate 版本)

这会创建一个集中化的策略，在所有项目的管道中注入 droid 审查作业而无需修改任何项目的 `.gitlab-ci.yml`。这是 GitLab 中的 GitHub 必要工作流的等效物。

1. **验证 Ultimate 版本**: 运行 `glab api "groups/{group_url_encoded}/security/policies" 2>&1`。如果返回 404，则停止并告知用户这需要 Ultimate 版本。

2. **检查现有安全策略项目**: 运行：
   `glab api graphql -f query='{ group(fullPath: "{group_path}") { securityPolicyProject { id name fullPath } } }' | python3 -c "import sys,json; d=json.load(sys.stdin); p=d['data']['group']['securityPolicyProject']; print(p['fullPath'] if p else 'NONE')"`

3. **创建或识别安全策略项目**:

   - 如果不存在安全策略项目，使用 AskUser 询问项目名称：
     ```
     1. [question] Name for the security policy project that will hold the Droid review policy?
     [topic] Policy-project
     [option] droid-security-policies
     ```
   - 创建项目: `glab api "groups/{group_url_encoded}/projects" -X POST -f "name={name}" -f visibility=private -f "description=Security policy project for Factory Droid review enforcement" -f auto_init=true`
   - 从响应中获取新的项目 ID。
   - 通过 GraphQL 将其链接为安全策略项目: `glab api graphql -f query='mutation { securityPolicyProjectAssign(input: { fullPath: "{group_path}" securityPolicyProjectId: "gid://gitlab/Project/{project_id}" }) { errors } }'`

4. **在安全策略项目中创建策略 CI/CD 配置文件**。
   创建一个名为 `droid-review-policy.yml` 的文件，其中包含公共 Droid 组件，并将注入的作业固定到 `.pipeline-policy-pre` 阶段：

   ```yaml
   include:
     - project: 'factory-components/droid-action'
       ref: main
       file: '/templates/droid-review.yml'
       inputs:
         droid_action_ref: main
         stage: '.pipeline-policy-pre'
         automatic_security_review: '{automatic_security_review}' # "true" or "false"
         review_depth: '{review_depth}' # "deep" or "shallow"
   ```

   备注：

   - 注入的任务从消费项目的 CI/CD 变量（在步骤 3b 中设置）继承 `FACTORY_API_KEY` 和 `GITLAB_TOKEN`，而不是从安全策略项目继承。确保这些变量存在于顶层组或每个项目级别，以便范围内的每个项目都能继承。
   - 一旦组件在 GitLab Catalog 上发布，请将 `ref:` 和 `droid_action_ref:` 固定到一个发布标签；使用 `main` 保持最新版本。

   使用 Repository Files API 对 `droid-review-policy.yml` 进行 Base64 编码并提交到安全策略项目（与其他选项的模式相同）。

5. 在安全策略项目中启用 **Pipeline Execution Policies 设置**：
   告诉用户：

   > "转到安全策略项目设置 > 通用 > 可见性、项目功能、权限，并启用 **管道执行策略**。这将授予管道用户访问政策配置的读取权限。完成后告诉我。"
   > 等待确认。

6. **创建管道执行策略**：
   在安全策略项目中创建一个文件 `.gitlab/security-policies/policy.yml`：

   ```yaml
   ---
   pipeline_execution_policy:
     - name: Factory Droid Code Review
       description: Enforces automated code review on all merge requests
       enabled: true
       pipeline_config_strategy: inject_policy
       content:
         include:
           - project: { security_policy_project_path }
             file: droid-review-policy.yml
       policy_scope:
         compliance_frameworks: []
   ```

   重要提示：`policy.yml` 的模式规则：

   - YAML 文档分隔符 `---` 在顶部是必需的。
   - 在 `pipeline_execution_policy:` 下列出的项目必须使用2 个空格缩进（不嵌套并在额外缩进的 `-` 下）。
   - `content` 必须包含一个 `include` 键和一个数组。请勿直接使用 `content.project`/`content.file`/`content.ref`。
   - 不要包含 `skip_ci` 或 `variables_override` 字段——它们是可选字段，格式不正确时会导致 schema 验证错误。
   - `policy_scope.compliance_frameworks: []` 表示 "适用于组中的所有项目"。

   Base64-编码并提交策略文件。

7. **验证**: 告诉用户：

   > "已创建管道执行策略。Droid 审查作业现在将被注入到组内所有合并请求管道中。无需对每个项目进行 `.gitlab-ci.yml` 的更改。"
   > "在以下位置管理策略：{security_policy_project_url}/-/security/policies"

8. 如果任何 API 调用返回 403，请告诉用户：
   > "您需要拥有组的访问权限才能创建安全策略。请让组的所有者运行此操作，或者使用选项 A 或 B 替代。"

## 第8 步（GitLab）：总结

显示结果表（格式与 GitHub 第9 步相同）。

如果步骤 3b 检测到缺少一个或两个必要 CI/CD 变量，请提醒用户：

> "**重要：审查流水线需要两个已掩码的 CI/CD 变量**"
>
> "**1. `FACTORY_API_KEY`** — 用于验证 Droid CLI。"
> " - 在 https://app.factory.ai/settings/api-keys" 生成"
> " - 在适当级别的设置 > CI/CD > 变量中添加（顶级组适用于所有项目，子组适用于部分项目，或单个项目）"
> " - Key=`FACTORY_API_KEY`，Value=你的密钥，勾选‘遮掩变量’，取消勾选‘保护变量’"
>
> "**2. `GITLAB_TOKEN`** — 允许作业发布 MR 评论并更新跟踪便签。"
> " - 在 {group_url}/-/settings/access_tokens 创建一个 **组级访问令牌**（适用于组级设置），在 {project_url}/-/settings/access_tokens 创建一个 **项目级访问令牌**，或在 https://gitlab.com/-/user_settings/personal_access_tokens." 处创建一个 **个人访问令牌**。"
> " - 角色：`Developer` 或更高。范围：`api`。"
> " - 在 FACTORY_API_KEY 同一级别添加：Key=`GITLAB_TOKEN`，Value=该令牌，勾选‘遮掩变量’，取消勾选‘保护变量’。"
>
> "如果没有这两个变量，流水线将在准备步骤中失败，提示 `Missing FACTORY_API_KEY` 或 `GitLab API 401: Unauthorized`。"

## GitLab CI 模板

Droid 审查流水线发布为一个可重用的 GitLab CI/CD 组件，在 gitlab.com 上的 `factory-components/droid-action`（公共 droid-action 仓库的镜像）。消费项目只需 `include:` 该模板 — 他们不需要脚本化 `droid exec`，安装 CLI，或自行维护审查流水线。"

该模板提供了完整的两阶段审查（候选人生成 + 验证器），内联 MR 评论，带有遥测信息的粘性跟踪便签，以及可选的并行安全审查子 agent —— 所有这些都通过输入进行配置。"

### 完整 .gitlab-ci.yml (用于新文件)

在创建新的 `.gitlab-ci.yml` 时生成此内容：

```yaml
include:
  - project: 'factory-components/droid-action'
    ref: main
    file: '/templates/droid-review.yml'
    inputs:
      droid_action_ref: main
      automatic_security_review: '{automatic_security_review}' # "true" or "false"
      review_depth: '{review_depth}' # "deep" or "shallow"
```

将 `{automatic_security_review}` 替换为 `"true"` 或 `"false"`，根据第 5 步的答案；将 `{review_depth}` 替换为 `"deep"` 或 `"shallow"`。

备注：

- 组件锁定 `factory-components/droid-action` 在 `main` 分支上。在生产环境中，请锁定到标签（例如 `v0.1.0`）或提交 SHA，以使流水线可重复。`ref:` 包含指令和 `droid_action_ref:` 输入参数应匹配。
- 作业默认为 `stage: test`。这适用于没有自定义 `stages:` 列表的项目（GitLab 的隐式默认排序包括 `test`）。对于缺少 `stages:` 的自定义 `test` 列表的项目，请参阅附录片段中的 stages-check 指导。
- `FACTORY_API_KEY` 和 `GITLAB_TOKEN` CI/CD 变量会自动继承（模板从作业环境引用它们的名字）。请勿添加显式的 `variables:` 覆盖块——显式重新解析可能会在某些项目中破坏继承。

### 附录片段（用于现有的 .gitlab-ci.yml）

当追加到现有文件时：

1. 读取现有文件内容。
2. 检查它是否已经有 `include:` 块。如果有，将新条目添加到现有 `include:` 下。如果没有，请添加一个顶级的 `include:` 块。
3. **检查现有的 `stages:` 列表（如果存在）**。组件的作业默认为 `stage: test`，因此作业需要 `test` 作为有效的阶段：
   - 如果不存在顶级 `stages:` 关键字 → 不需要更改（GitLab 使用隐式默认值包括 `test`）。
   - 如果 `stages:` 存在且已包含 `test` → 不需要更改。
   - 如果 `stages:` 存在但不包含 `test`，请选择一个选项：
     - **选项 A（推荐）：**将 `- test` 追加到现有 `stages:` 列表。这是改动最小的方案，并能让 Droid 作业与项目现有阶段保持隔离。
     - **选项 B：**不修改 `stages:`，而是在 Component include 中添加 `stage: "<existing-stage>"` 输入（例如，可设置为 `stage: "build"`；如果项目已有 `- build`，它应位于 `stages:` 列表中）。当用户明确希望 Droid 作业在流水线 UI 中与现有阶段归组时使用此方案。
   - 在修改文件之前，请问用户他们更偏好哪个选项，默认选择选项 A。
4. 追加：

   ```yaml
   include:
     - project: 'factory-components/droid-action'
       ref: main
       file: '/templates/droid-review.yml'
       inputs:
         droid_action_ref: main
         automatic_security_review: '{automatic_security_review}'
         review_depth: '{review_depth}'
         # Add `stage: "<existing-stage>"` here if you picked Option B above.
   ```

不要覆盖现有文件内容 — 先读取它，然后合并。

## 错误处理 (GitLab)

| 错误                                 | 原因                                                          | 修复                                                                                                                         |
| ------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `glab: command not found`             | glab CLI 未安装                                         | 告诉用户：`brew install glab` 或访问 https://gitlab.com/gitlab-org/cli                                                   |
| `401 Unauthorized`                    | 未认证                                              | 告诉用户：`glab auth login`                                                                                                |
| 项目文件上返回 `403 Forbidden`      | 权限不足                                       | 用户需要至少 Maintainer 访问权限                                                                                       |
| 安全策略上返回 `403 Forbidden`  | 不是组 Owner                                                | 用户需要 Owner 访问权限以执行 Pipeline 执行策略                                                                     |
| 组变量上返回 `404`              | 变量不存在                                         | 引导用户在组 CI/CD 设置中创建它                                                                             |
| 安全策略 API 上返回 `404`        | 不在 Ultimate 版本中                                           | 告诉用户：Pipeline 执行策略需要 GitLab Ultimate                                                              |
| 文件创建返回`400`                  | 文件已存在                                            | 使用 PUT 而不是 POST 来更新                                                                                           |
| 分支已存在                 | 上次运行未完成                                   | 删除分支或跳过项目                                                                                       |
| `chosen stage X missing from stages:` | 自定义的`stage:`输入不在项目的`stages:`列表中出现 | 要么移除`stage:`输入（默认为`test`），要么将选定阶段添加到项目的`stages:`列表中               |
| `Missing FACTORY_API_KEY`             | CI/CD 变量未设置或未继承                        | 验证 FACTORY_API_KEY 已被遮蔽且在项目继承的级别上非受保护状态（步骤3b）                             |
| `GitLab API 401: Unauthorized`        | GITLAB_TOKEN 缺失、过期或权限不足           | 重新颁发具有`api`范围的项目/组/个人访问令牌并重新设置 CI/CD 变量（步骤3b）                     |
| `include: project: ... 401` 或 `404`  | factory-components/droid-action 不可从 runner 访问     | 确认消费项目的 CI/CD 环境可以访问 gitlab.com（无出站阻塞），并且包含`ref:`。 |

---

## 语言

用户使用哪种语言编写，就用同一种语言回复。如果用户用日语书写，则用日语回复；如果用户用韩语书写，则用韩语回复。这适用于所有消息、AskUser 问题、错误指导和总结。唯一必须保持英文的是：git 提交信息、分支名称、PR 标题/正文（这些是技术产物），以及 YAML 内容本身。
