---
name: install-wiki
description: |
  安装 CI 行动以自动刷新 Factory Wiki 在每次推送至默认分支时。
  用于用户希望设置自动化 Wiki 生成、安装 Wiki CI 或配置 Wiki 刷新时。
user-invocable: true
---

# 安装 Wiki CI 动作

你正在设置一个 CI 行动，该行动将在代码推送到仓库的默认分支时自动刷新 Factory Wiki。

请严格按照以下步骤操作。不要跳过任何步骤。如果当前步骤失败，请勿进行下一步。

## 第 1 步：验证 Git 仓库

运行 `git rev-parse --is-inside-work-tree`，检查当前目录是否位于 git 仓库中。

如果不在 git 仓库中，请告知用户：

> ["\"此命令必须在 git 仓库内部运行。\"]

然后停止。不要继续。

## 步骤 2: 检测持续集成框架

检查仓库使用哪个持续集成框架：

1. 检查 `.github/workflows/` 目录是否存在（GitHub Actions）
2. 检查是否存在 `.gitlab-ci.yml` 文件 (GitLab CI)

如果未找到 NEITHER，请告诉用户：

> "未能检测到受支持的持续集成框架。当前支持：GitHub Actions, GitLab CI。请首先设置您的持续集成框架，然后再次运行此命令。"

然后停止。不要继续。

## 第3 步：检查是否存在现有的 Wiki CI 动作

搜索任何现有的 Wiki 刷新 CI 配置：

- **GitHub Actions**: 在 `.github/workflows/` 目录下的所有文件中搜索同时匹配 `droid` 和 `wiki` 的内容（例如，`droid exec` 与 `/wiki` 或 `wiki-upload`）。
- **GitLab CI**: 在 `.gitlab-ci.yml` 中搜索同时匹配 `droid` 和 `wiki` 的内容。

如果发现现有的 Wiki CI 动作，请告诉用户：

> “仓库中已经存在一个 Wiki 刷新 CI 行动：[filename]。无需更改。”

然后停止。不要继续。

## 第4 步：检测默认分支

运行 `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null` 获取默认分支。提取仅分支名称（例如，从 `main` 提取 `refs/remotes/origin/main`）。

如果失败，请退回到使用 `main` 或 `master` 检查是否存在 `git rev-parse --verify origin/main 2>/dev/null` 或 `git rev-parse --verify origin/master 2>/dev/null` 分支。

如果未找到，则默认为 `main`。

## 第5 步：创建持续集成配置

### 对于 GitHub Actions

在文件中创建 `.github/workflows/droid-wiki-refresh.yml`，内容如下（将 `DEFAULT_BRANCH` 替换为检测到的默认分支）：

```yaml
name: Droid Wiki Refresh

on:
  push:
    branches: [DEFAULT_BRANCH]

jobs:
  wiki-refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Factory Droid
        run: curl -fsSL https://app.factory.ai/cli | sh

      - name: Generate wiki
        run: droid exec --auto high "/wiki"
        env:
          FACTORY_API_KEY: \${{ secrets.FACTORY_API_KEY }}
```

### 对于 GitLab CI

在追加作业之前，阅读 `.gitlab-ci.yml` 并检查 `stages:` 列表。选择一个合适的现有阶段（例如，`deploy`, `after_script` 或列出的最后一个阶段）。如果不存在 `stages:` 关键字，则完全省略 `stage:` 字段，以便 GitLab 使用默认的 `test` 阶段。

在现有的 `.gitlab-ci.yml` 文件中追加以下作业（用检测到的默认分支替换 `DEFAULT_BRANCH`，用你上面找到的阶段替换 `DETECTED_STAGE`）：

```yaml
droid-wiki-refresh:
  stage: DETECTED_STAGE
  before_script:
    - curl -fsSL https://app.factory.ai/cli | sh
  script:
    - droid exec --auto high "/wiki"
  rules:
    - if: $CI_COMMIT_BRANCH == "DEFAULT_BRANCH"
  variables:
    FACTORY_API_KEY: $FACTORY_API_KEY
```

在创建/修改文件后，向用户展示创建的内容并提醒他们：

> "确保在 CI 设置中添加你的 `FACTORY_API_KEY` 作为秘密变量。"

## 第6 步：提出创建一个 PR

询问用户是否希望为此次变更创建 PR。如果用户同意：

1. 创建一个名为 `factory/install-wiki-ci` 的新分支
2. 暂存新的/修改的 CI 文件
3. 提交带有信息 `ci: add Droid Wiki refresh action`
4. 推送分支
5. 创建一个 PR，标题为 `ci: add Droid Wiki refresh action`，并在描述中解释更改内容
