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
├── -home-<you>-code-work-myapp/
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
# 列出所有包含会话的项目文件夹
sessions_root="$HOME/.factory/sessions"
for project_dir in "$sessions_root"/*; do
  [[ -d "$project_dir" ]] && echo "$project_dir"
done

# 按字面名称片段选择项目；零匹配或多匹配都会失败
select_project_dir() {
  local needle=$1
  set -- "$sessions_root"/*"$needle"*
  if [[ "$#" -ne 1 || ! -d "$1" ]]; then
    echo "Expected exactly one project directory containing: $needle" >&2
    return 1
  fi
  echo "$1"
}

project_dir=$(select_project_dir "myapp") || exit 1
echo "$project_dir"
```

### 查看项目的最近会话

```bash
sessions_root="$HOME/.factory/sessions"
select_project_dir() {
  local needle=$1
  set -- "$sessions_root"/*"$needle"*
  if [[ "$#" -ne 1 || ! -d "$1" ]]; then
    echo "Expected exactly one project directory containing: $needle" >&2
    return 1
  fi
  echo "$1"
}
project_dir=$(select_project_dir "myapp") || exit 1

# List sessions by date for that project
ls -lt "$project_dir"/

# 获取最近 10 个会话的标题；NUL 分隔可保留路径中的空格
while IFS= read -r -d '' f; do
  echo "=== $f ==="
  head -1 "$f" | jq -r '.title // "Untitled"'
done < <(
  python3 - "$project_dir" <<'PY'
import os
import sys
from pathlib import Path

files = sorted(
    Path(sys.argv[1]).glob("*.jsonl"),
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)
for path in files[:10]:
    sys.stdout.buffer.write(os.fsencode(path))
    sys.stdout.buffer.write(bytes([0]))
PY
)
```

### 按内容搜索

```bash
sessions_root="$HOME/.factory/sessions"
select_project_dir() {
  local needle=$1
  set -- "$sessions_root"/*"$needle"*
  if [[ "$#" -ne 1 || ! -d "$1" ]]; then
    echo "Expected exactly one project directory containing: $needle" >&2
    return 1
  fi
  echo "$1"
}

# 搜索所有会话
rg "authentication" "$sessions_root"

# 搜索唯一匹配的项目文件夹
project_dir=$(select_project_dir "myapp") || exit 1
rg "bug fix" "$project_dir"

# 查看上下文中的匹配项
api_dir=$(select_project_dir "api") || exit 1
rg -C 2 "login" "$api_dir"
```

### 找到有关某个主题的项目会话

```bash
# 哪些项目的会话提到了 "redis"？从 sessions 根目录计算相对路径
sessions_root="$HOME/.factory/sessions"
rg -0 -l "redis" "$sessions_root" |
while IFS= read -r -d '' file; do
  relative=${file#"$sessions_root"/}
  echo "${relative%%/*}"
done | sort -u
```

## 阅读会话

一旦找到了会话文件：

```bash
sessions_root="$HOME/.factory/sessions"
select_project_dir() {
  local needle=$1
  set -- "$sessions_root"/*"$needle"*
  if [[ "$#" -ne 1 || ! -d "$1" ]]; then
    echo "Expected exactly one project directory containing: $needle" >&2
    return 1
  fi
  echo "$1"
}
project_dir=$(select_project_dir "myapp") || exit 1

# 选择一个真实的会话文件；未找到时立即停止
set -- "$project_dir"/*.jsonl
if [[ "$#" -eq 1 && ! -f "$1" ]]; then
  echo "No session files found in $project_dir" >&2
  exit 1
fi
session_file=$1
settings_file="${session_file%.jsonl}.settings.json"

# 元数据（标题、工作目录）
head -1 "$session_file" | jq .

# 会话统计（模型、token、时长）
if [[ -f "$settings_file" ]]; then
  jq . "$settings_file"
else
  echo "Settings file not found: $settings_file" >&2
fi

# 对话有多少行？
wc -l "$session_file"
```

用户消息带有 `"role": "user"`，助手响应带有 `"role": "assistant"`。工具调用显示了运行的命令和被修改的文件。

## 常见情况

**"我在这个项目中做了什么？"** 列出该项目的会话文件夹，检查日期，阅读对话文件。

**"找到我们修复登录 bug 的那个会话"** 在各个会话中搜索“login”或“auth”。找到后，阅读对话内容。

**"继续我之前的工作"** 找到相应的会话，阅读其中的内容，总结关键决策后再继续。

**"我使用 Droid 多久了？"** 设置文件中有 token 计数和活跃时间。如果需要，可以跨会话汇总。

## 提示

使用`rg`(ripgrep)代替 grep。它更快且能更好地处理嵌套文件夹。

项目路径中的斜杠会在所有支持的平台上被替换为短横线。例如，macOS 的 `/Users/me/code/app` 变为 `-Users-me-code-app`，Linux 的 `/home/me/code/app` 变为 `-home-me-code-app`。

会话标题并不总是有帮助的。有时需要阅读对话内容才能知道它是关于什么的。

会话可能包含敏感信息。在展示时要小心。
