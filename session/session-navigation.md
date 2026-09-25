---
name: session-navigation
version: 1.1.0
description: |
  导航、搜索和管理 Droid 会话。使用此功能时，用户可以：
  - 列出最近的会话
  - 在会话历史中搜索特定主题或模式
  - 恢复之前的会话
  - 获取会话中完成工作的详细信息
  - 根据项目、日期或内容查找会话
---

# 会话导航

探索过去的 Droid 会话。也许你想从上次中断的地方继续，找到上周做的那件事，或者只是看看某个项目的最新进展。

## 会话存放位置

会话位于`~/.factory/sessions/`中，并按项目文件夹组织。每个项目都有自己的目录，路径中的斜杠会被替换为破折号：

```
~/.factory/sessions/
├── -Users-<you>-code-work-myapp/
│   ├── <uuid>.jsonl
│   └── <uuid>.settings.json
├── -Users-<you>-code-projects-api/
│   ├── <uuid>.jsonl
│   └── <uuid>.settings.json
└── ...
```

每个会话包含两个文件：

**对话**（`.jsonl`）：每行都是一个 JSON 对象。第一行包含元数据（会话 ID、标题、工作目录），其余各行记录用户消息、助手回复和工具调用。

**设置**（`.settings.json`）：会话统计信息，包括使用的模型、运行时长、token 数量和自主模式。

## 查找会话

### 列出项目文件夹

```bash
# See all project folders with sessions
ls ~/.factory/sessions/

# Find folders for a specific project (partial match)
ls ~/.factory/sessions/ | grep "myapp"
```

### 查看项目的最近会话

```bash
# List project folders first, then pick a name from that list
ls ~/.factory/sessions/
project=$(ls ~/.factory/sessions/ | grep "myapp" | head -1)

# List sessions by date for that project
ls -lt ~/.factory/sessions/"$project"/

# Get titles of recent sessions
for f in $(ls -t ~/.factory/sessions/"$project"/*.jsonl | head -10); do
  echo "=== $f ==="
  head -1 "$f" | jq -r '.title // "Untitled"'
done
```

### 按内容搜索

```bash
# Search across ALL sessions
rg "authentication" ~/.factory/sessions/

# Search within a project folder from the list above
ls ~/.factory/sessions/
project=$(ls ~/.factory/sessions/ | grep "myapp" | head -1)
rg "bug fix" ~/.factory/sessions/"$project"/

# See matches in context
api=$(ls ~/.factory/sessions/ | grep "api" | head -1)
rg -C 2 "login" ~/.factory/sessions/"$api"/
```

### 找到有关某个主题的项目会话

```bash
# Which projects have sessions mentioning "redis"?
rg -l "redis" ~/.factory/sessions/ | cut -d'/' -f1-5 | sort -u
```

## 阅读会话

一旦找到了会话文件：

```bash
ls ~/.factory/sessions/
project=$(ls ~/.factory/sessions/ | grep "myapp" | head -1)

# The metadata (title, working directory)
head -1 ~/.factory/sessions/"$project"/<uuid>.jsonl | jq .

# Session stats (model, tokens, duration)
cat ~/.factory/sessions/"$project"/<uuid>.settings.json | jq .

# How long was this conversation?
wc -l ~/.factory/sessions/"$project"/<uuid>.jsonl
```

用户消息带有 `"role": "user"`，助手响应带有 `"role": "assistant"`。工具调用显示了运行的命令和被修改的文件。

## 常见情况

**"我在这个项目中做了什么？"** 列出该项目的会话文件夹，检查日期，阅读对话文件。

**"找到我们修复登录 bug 的那个会话"** 在各个会话中搜索“login”或“auth”。找到后，阅读对话内容。

**"继续我之前的工作"** 找到相应的会话，阅读其中的内容，总结关键决策后再继续。

**"我使用 Droid 多久了？"** 设置文件中有 token 计数和活跃时间。如果需要，可以跨会话汇总。

## 提示

使用`rg`(ripgrep)代替 grep。它更快且能更好地处理嵌套文件夹。

项目路径中的斜杠被替换为短横线。`/Users/me/code/app`变为`-Users-me-code-app`。

会话标题并不总是有帮助的。有时需要阅读对话内容才能知道它是关于什么的。

会话可能包含敏感信息。在展示时要小心。
