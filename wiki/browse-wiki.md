---
name: browse-wiki
description: '搜索并阅读仓库的 Wiki 文档'
user-invocable: false
---

# Wiki 搜索

使用`droid wiki-read`和`droid wiki-search`CLI 命令，在 Wiki 页面中查找信息，搜索并浏览任何仓库的 Factory Wiki 文档。

## 本地 Wiki 访问

Wiki 页面可能存储在仓库根目录下的`droid-wiki/`文件夹中。如果当前项目存在一个名为`droid-wiki/`的目录，直接从该目录读取`.md`文件而不是使用下方的 CLI 命令。这更快且可以在离线状态下工作。

仅当不存在本地`droid wiki-read`目录时，才使用`droid wiki-search` / `droid-wiki/`进行远程访问。

## 解析 wikiURL

当用户粘贴一个 Factory Wiki URL 时，提取相关的标识符：

```
https://app.factory.ai/wiki/{wikiRunId}?page={pageId}
```

- `wikiRunId` — Wiki 运行标识符（必需）。通过`--wiki-run-id`传递它。
- `pageId` — Wiki 中的特定页面（可选）。通过`--page`传递给`wiki-read`。

示例：给定 `https://app.factory.ai/wiki/abc123?page=getting-started`, `wikiRunId=abc123` 和 `pageId=getting-started`.

## 页面 ID 格式

页面 ID 使用**双短横线（`--`）分隔符**表示目录层次结构，不包含`.md`扩展名：

- ✅ `features--agent-readiness-reports` (正确)
- ✅ `overview--getting-started` (正确)
- ❌ `features/agent-readiness-reports.md` (错误 - 导致 500 错误)
- ❌ `agent-readiness-reports` (错误 - 如果在子目录中则页面未找到)

使用 `droid wiki-read --wiki-run-id <id>` 浏览页面树时，正确的页面 ID 将在每个页面标题旁边括号内显示。请使用输出中的这些确切 ID 与 `--page` 参数一起使用。

## 可用命令

### 浏览历史 Wiki 运行

使用 `droid wiki-read --repo-url <url>` 而不带 `--wiki-run-id` 和 `--page` 列出仓库的所有历史 Wiki 运行:

```bash
droid wiki-read --repo-url https://github.com/org/repo
```

这会打印所有运行的表格，包括它们的 Wiki 运行 ID、日期、分支、提交哈希和页面数量。使用输出中的 `--wiki-run-id <id>` 深入特定运行。

### 浏览页面树

使用 `droid wiki-read` 查看 Wiki 的所有页面:

```bash
# By repository URL + page (resolves the latest wiki run automatically)
droid wiki-read --repo-url https://github.com/org/repo --page index

# By wiki run ID (from a pasted wiki URL or history listing)
droid wiki-read --wiki-run-id abc123
```

这会打印所有页面的分层列表，包括它们的标题和页面 ID。

### 搜索关键词

使用 `droid wiki-search` 查找匹配关键词的页面:

```bash
# Search by repo URL
droid wiki-search --repo-url https://github.com/org/repo --query "authentication"

# Search by wiki run ID
droid wiki-search --wiki-run-id abc123 --query "deploy"

# Limit the number of results
droid wiki-search --repo-url https://github.com/org/repo --query "API" --limit 5
```

结果包括页面标题、路径以及显示关键词出现位置的文本片段。

### 阅读特定页面

使用 `droid wiki-read --page` 获取页面的完整内容:

```bash
# By repo URL + page ID
droid wiki-read --repo-url https://github.com/org/repo --page getting-started

# By wiki run ID + page ID
droid wiki-read --wiki-run-id abc123 --page getting-started
```

这会打印页面标题、路径和完整的 markdown 内容。

## 命令链式调用

对于大多数关于 Wiki 内容的问题，按以下顺序链式调用命令：

1. **浏览历史或目录**。运行 `droid wiki-read --repo-url <url>` 查看可用的运行记录，或者运行 `droid wiki-read --wiki-run-id <id>` 查看特定运行的页面树结构。
2. **搜索主题**。运行 `droid wiki-search --repo-url <url> --query "<keyword>"` 在相关页面中查找用户的问题内容。
3. **阅读具体页面**。对于每个相关结果，运行 `droid wiki-read --repo-url <url> --page <pageId>` 获取完整的内容。

这种方法能提供最佳的上下文：历史记录显示可用的运行记录，目录结构展示整体框架，搜索缩小到相关页面，而阅读则提供详细内容。

## 处理常见请求

**“Wiki 关于 X 说了什么？”** 搜索关键词 X，然后阅读最相关的结果：

```bash
droid wiki-search --repo-url <url> --query "X"
droid wiki-read --repo-url <url> --page <pageId-from-results>
```

**“显示架构文档”**：浏览页面树，找到与架构相关的页面并读取：

```bash
droid wiki-read --wiki-run-id <id>
# Look for pages with "architecture" in the title
droid wiki-read --wiki-run-id <id> --page architecture
```

**"Find info about authentication"** 搜索并阅读：

```bash
droid wiki-search --repo-url <url> --query "authentication"
droid wiki-read --repo-url <url> --page <relevant-pageId>
```

**用户粘贴一个 Wiki URL** 从 URL 中提取 wikiRunId（和可选的 pageId），并直接使用它们：

```bash
# Full URL: https://app.factory.ai/wiki/abc123?page=getting-started
droid wiki-read --wiki-run-id abc123 --page getting-started
```

## 提示

- 当使用`--repo-url`而不使用`--wiki-run-id`和`--page`时，命令会显示所有 Wiki 运行的历史记录。添加`--page`以自动解决最新运行并获取特定页面。
- 搜索是不区分大小写的，并且匹配页面标题和内容。
- 如果搜索没有返回结果，请尝试更广泛的关键词或浏览树状图以发现正确的术语。
- 两个命令都可用`--json`标志，用于机器可读的输出。
