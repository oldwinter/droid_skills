---
name: install-triage
description: >
  搭建适用于任何公司的定时 Slack triage 自动化。
  创建 Python 工具层（run_triage.py）和 HEARTBEAT.md agent 循环，
  扫描已配置的 Slack 频道以发现可操作消息，与工单系统（Linear 或 Jira）
  中的现有条目去重，创建新工单并发布运行摘要。
  当用户希望部署自动 triage 机器人时使用。
user-invocable: true
---

# 安装 Triage

清除所有之前的计划和待办事项。你之前的任务已完成。你的新任务是为这位用户搭建一个定时的**问题处理自动化**。

triage 自动化按计划运行，扫描一组 Slack 频道，识别代表独立、可操作任务的消息，并与现有工单队列（Linear 或 Jira）去重。对于真正新增且可操作的任务，它会创建工单，并向 Slack 频道发布运行摘要。底层 Python 工具层只负责机械性的 I/O；部署后的自动化 agent 负责判断可操作性、路由和重复项。

**在开始之前，请从以下阶段创建待办事项列表。**

## 如何搭建

自动化脚本位于 `~/.factory/automations/<slug>/`（开发模式下为 `~/.factory-dev/automations/<slug>/`）。如果从自动化 UI 启动，创建提示词已经给出具体的自动化根目录和 slug，并预先写入 `memory/config.json` 和 `memory/state.json`。使用该根目录。否则，请向用户询问自动化名称，推导 kebab-case slug，并使用 `~/.factory/automations/<slug>/`。

以下路径均相对于**自动化根目录**。

## 阶段1 — 收集配置

自动化完全通过 `memory/config.json` 配置：

```json
{
  "name": "Triage",
  "scan_channels_description": "the eng on-call and support channels",
  "scan_channels": [{ "id": "C0123", "name": "engineering" }],
  "summary_channel_description": "#automation-triage",
  "summary_channel": { "id": "C0999", "name": "automation-triage" },
  "ticket_system": "linear",
  "default_destination_description": "Engineering",
  "default_destination": {
    "key": "ENG",
    "id": "<team id>",
    "name": "Engineering"
  },
  "ticket_guidance": "Routing rules, labels, default team/project...",
  "window_secs": 3900
}
```

`scan_channels`（一个数组的`{ "id": "C…", "name": "…" }`），`summary_channel`（单个`{ "id": "C…", "name": "…" }`），和`default_destination`是**运行时必需的** — `run_triage.py discover`读取`scan_channels`，发布总结时读取`summary_channel`，而`ticket-context`使用`default_destination`作为低置信度的备用（对于 Linear 团队，对于 Jira 项目；Jira 需要一个项目才能创建票务）。`*_description`字段是用户的白话描述；它们是解决实际值的提示，而不是替代品。

- **如果 `memory/config.json` 已经存在**（UI 流程），读取它并将其作为票据系统和指导的来源——不要重新询问这些内容。然而，UI **不** 解决频道或目的地：文件中有 `scan_channels_description`、`summary_channel_description` 和 `default_destination_description` 但可能没有解决的 `scan_channels` / `summary_channel` / `default_destination`。你必须：
  1. 将 `scan_channels_description` 和 `summary_channel_description` 转换为实际的 Slack 频道——列出可用的频道（使用 Slack 工具或让用户粘贴频道 id），并匹配它们到描述中。
  2. 将 `default_destination_description` 解决为一个真实的团队（Linear）/ 项目（Jira）——运行 `python3 run_triage.py ticket-context`（在写入密钥后）列出团队/项目，并进行匹配。
  3. 通过 `AskUser` 工具与用户确认解决后的扫描频道集、单一总结频道和默认目的地。
  4. 在完成前将它们写回 `memory/config.json` 作为 `scan_channels`、`summary_channel` 和 `default_destination`。总结频道可能是机器人尚未加入的频道——这没关系，`run_triage.py` 在首次发布时会自动加入它。
- **如果不存在**（独立 `/install-triage`），使用 `AskUser` 工具收集：

  1. 要扫描的 Slack 频道（将名称解析为频道 id — 列出频道或让用户粘贴 id），并确认解决后的集合与用户一起。
  2. 发布运行总结的 Slack 频道（解析为频道 id；机器人在首次加入时会自动加入）。
  3. 哪个票据系统 (`linear` 或 `jira`)。
  4. 默认目的地——当没有明确的所有者时，代码将路由到 Linear 团队 / Jira 项目票据（通过 `{key,id?,name}` 解析为 `ticket-context`）。
  5. 提交票据的指导：路由规则、应应用哪些标签/问题类型以及默认团队（Linear）或项目（Jira）。

  然后编写 `memory/config.json` 包含这些值（包括填充好的 `scan_channels`、`summary_channel` 和 `default_destination`）。`window_secs` 应该大致等于调度间隔加上一个小的重叠时间（例如，对于每小时调度，可以设置为 `3900`）。

## 阶段 2 — 密钥（切勿提交）

工具层从 `memory/secrets.json` 读取凭据。在写入任何密钥之前：

1. 在自动化根目录创建 `.gitignore` 包含：

   ```
   memory/secrets.json
   memory/*.db
   ```

2. 使用 `AskUser` 收集凭据并编写 `memory/secrets.json`：

   - 始终：`SLACK_BOT_TOKEN` — 具有读取扫描频道（`channels:history`, `groups:history`, `channels:read`, `channels:join`）和发布到总结频道权限（`chat:write`），以及如果需要截图则具有 `files:read` 权限的 Slack 机器人令牌。
   - 当 `ticket_system` 是 `linear` 时：`LINEAR_API_KEY`。
   - 当 `ticket_system` 为 `jira` 时：配置 `JIRA_BASE_URL`（例如 `https://acme.atlassian.net`）、`JIRA_EMAIL` 和 `JIRA_API_TOKEN`。

   绝不要将密钥值回显给用户、写入日志、报告或 `VISUAL.html` 中。

## 阶段 3 — 编写工具层

将以下文件原样写入自动化根目录的 `run_triage.py`。请勿修改它——它与具体公司无关，并会从 `memory/config.json` 和 `memory/secrets.json` 读取全部内容。写入后，请运行 `python3 run_triage.py --help`，确认帮助信息能够正常输出。

```python
{{RUN_TRIAGE_PY}}
```

## 阶段 4 — 编写 HEARTBEAT.md

在自动化根目录编写 `HEARTBEAT.md`。使用以下模板，然后 **用用户 `ticket_guidance` 中的 `config.json` 填充 "路由与归档指导" 部分**（复制它，并如果有助于具体化规则则扩展为具体的规则）。将 `schedule` 前置字段设置为自动化创建时的时间表（默认值 `0 * * * *`）。保持 agent 循环完整 — 它引用了工具层的 `ticket-*` 子命令，这些子命令抽象覆盖了 Linear 和 Jira。

```markdown
---
name: '<automation name>'
description: 'Scans Slack channels for actionable work, dedupes against the ticketing system, files tickets, posts a summary'
schedule: '0 * * * *'
templateId: triage
tags:
  - automations
---

# <automation name>

You are a triage agent. Every run you scan the configured Slack channels for
messages that represent distinct, actionable work items, check the ticketing
system for duplicates, file tickets when missing, route them per the guidance
below, and post a summary.

**You make the judgement calls.** The Python tool layer (`run_triage.py`) only
does mechanical I/O. Actionability, routing, and dedupe are your decisions.

## Tool layer

A single CLI at `run_triage.py` exposes the I/O primitives. Every subcommand
reads inputs from argv or stdin JSON and emits one JSON document on stdout. Run
`python3 run_triage.py --help` for the full list. The ones you use each run:

| Subcommand                                                                            | What it does                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `discover`                                                                            | pulls recent messages from the configured scan channels, drops excluded subtypes and already-processed `(channel_id, ts)` pairs, resolves permalinks, enriches attachment/block bodies. Returns candidates.                                         |
| `ticket-context`                                                                      | ticketing metadata for routing. Linear: teams + labels + fallback team. Jira: projects + issue types + labels.                                                                                                                                      |
| `ticket-search-permalink <url>`                                                       | hard-duplicate check for a Slack permalink.                                                                                                                                                                                                         |
| `ticket-search <query>`                                                               | semantic search of existing tickets (title/state/preview).                                                                                                                                                                                          |
| `ticket-create` (stdin JSON)                                                          | create a ticket. Linear keys: `{team_id, title, description, label_names?, slack_url?, sync_to_thread?}`. Jira keys: `{project_key, title, description, issue_type?, label_names?, slack_url?}`. Returns `{ticket:{id,identifier,url}, warnings?}`. |
| `ticket-link-slack` (stdin JSON `{issue_id, url, title?, sync_to_thread?}`)           | link an existing ticket to a Slack message (Linear native attachment / Jira remote link).                                                                                                                                                           |
| `attach-screenshots` (stdin JSON `{issue_id, files:[{url_private,name?,mimetype?}]}`) | download Slack files and attach them to the ticket.                                                                                                                                                                                                 |
| `slack-reply` (stdin JSON `{channel, ts, text}`)                                      | threaded reply.                                                                                                                                                                                                                                     |
| `slack-post` (stdin JSON `{channel, text}`)                                           | non-threaded message (run summary).                                                                                                                                                                                                                 |
| `resolve-summary-channel`                                                             | returns the configured summary channel id (joining it if needed).                                                                                                                                                                                   |
| `record-decision` (stdin JSON)                                                        | persist your decision. Required: `channel_id`, `ts`, `action` ∈ {`created`, `skipped_duplicate`, `skipped_not_actionable`, `skipped_bot_noise`}. Optional: `permalink`, `ticket_id`, `ticket_url`, `reason`, `confidence`, `route_key`.             |
| `finalize` (stdin JSON)                                                               | writes run metrics, the markdown report, the run-log line in `notes.md`, ages out old rows, regenerates `VISUAL.html`. Accepts `{scanned, evaluated, created, dup, na, tickets, skipped?, errors?, warnings?}`.                                     |

Credentials live in `memory/secrets.json`; the tool layer reads them itself.
Never log or echo their values.

## What counts as "actionable"

INCLUDE — file a ticket for:

- Bug reports with observable symptoms ("X is broken", "Y returns 500")
- Concrete requests ("we should add…", "can we change…", "would be nice if…")
- Customer escalations with a clear ask or reproduction
- Regressions ("this used to work", "since deploy X…")
- Specific design/performance feedback with a proposed change or impact

EXCLUDE — skip and `record-decision` with a reason:

- Status updates, FYIs, acknowledgements, venting without a request
- Already-resolved threads ("nvm fixed it")
- Jokes, social messages, emoji-only replies
- Replies/discussion on an existing thread (`thread_ts` set and ≠ `ts`)
- Open questions whose resolution is an _answer_, not a change ("do we
  support X?", "is there interest in Y?"). File only when the resolution is a
  change to code, config, or design.

Borderline test: **"Would a reasonable tech lead, reading this cold, say
'someone should look into this'?"** Politeness phrasing does not make a concrete
request non-actionable — read for the underlying ask. Bot-authored messages
(`bot_id` set) are NOT auto-skipped; many bots relay human content — read the
body and apply the same test.

## Routing & filing guidance

<!-- Fill this in from config.json `ticket_guidance`. Describe how to choose the
target team (Linear) or project (Jira), which labels / issue types to apply, the
default/fallback destination when confidence is low, and how aggressively to
dedupe. Track recurring channel→destination patterns in notes.md. -->

When confidence is low or a message is cross-cutting, route to the configured
default/fallback destination rather than guessing.

## Run flow

1. **Discover.** `python3 run_triage.py discover`. Read `memory/notes.md` first
   for tuning observations. If `candidates` is empty, skip to step 6.
2. **Pull ticket context.** `python3 run_triage.py ticket-context`. Cache it for
   this run (teams/projects, labels/issue types, fallback destination).
3. **For each candidate — judge, dedupe, file:**
   - **a. Actionable?** Apply the rubric. If not, `record-decision` with
     `skipped_not_actionable` (or `skipped_bot_noise`).
   - **b. Split bundled asks** into separate candidates.
   - **c. Synthesize** title (≤ 80 chars, paraphrased), a short prose
     description, and 3–6 dedupe keywords.
   - **d. Dedupe.** First `ticket-search-permalink "<permalink>"` (hard check);
     each hit carries `matched_via`. Then `ticket-search "<keywords>"` and read
     the hits — ask "would the owning team close my new ticket as a duplicate of
     one of these?". When uncertain, err toward filing.
   - **e. On a duplicate**, link the permalink to the existing ticket
     (`ticket-link-slack`) and post a threaded `slack-reply` pointing to it,
     then record `skipped_duplicate`.
   - **f. Route** per the guidance section; pick a confidence (high/medium/low).
   - **g. Create the ticket** with `ticket-create`. Pass the Slack permalink as
     `slack_url` (do not put it in the description). Apply labels / issue type
     per guidance. Fold any returned `warnings` into the run warnings — never
     roll back a filed ticket.
   - **h. Reply in Slack** (`slack-reply`, ≤ 3 lines) pointing at the new ticket
     and why it was actionable.
   - **i. Record** with `record-decision` `action: created`, including
     `ticket_id`, `ticket_url`, `confidence`, and `route_key`.
4. **Attachments.** If a candidate's `files` array is non-empty, call
   `attach-screenshots` right after the ticket is created.
5. **Run summary.** `resolve-summary-channel`, then `slack-post` a short summary
   to that channel. If zero tickets, say "No new tickets this window."
6. **Finalize.** Always run `finalize` (even with zero candidates) so the report,
   run log, and dashboard stay fresh. `evaluated` = candidates you looked at;
   `scanned` = `channels_scanned` from `discover`; merge `discover` warnings in.
7. **Tuning notes.** Append terse observations to `memory/notes.md` under a
   `## Tuning` section (false negatives, stable channel→destination mappings,
   channels with no actionable traffic).

## Memory layout

| Path                          | Purpose                                                                         | Mutability                               |
| ----------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------- |
| `memory/config.json`          | channels, summary channel, ticket system, guidance                              | read-only at runtime                     |
| `memory/triage.db`            | `processed_messages` (dedupe + audit, 14-day retention), `run_metrics`, `cache` | rewritten by tools                       |
| `memory/notes.md`             | tuning observations + run log                                                   | append-only by you                       |
| `memory/secrets.json`         | Slack + ticketing credentials                                                   | read-only, never committed               |
| `memory/state.json`           | automation `id` (for the backlink footer); `runCount`                           | `id` read-only; bump `runCount` each run |
| `reports/YYYY-MM-DD-HH-mm.md` | per-run report                                                                  | written by `finalize`                    |
| `VISUAL.html`                 | dashboard                                                                       | written by `finalize`                    |

## Operational guardrails

- Never log or echo any secret.
- One ticket per discrete issue. Split bundled Slack asks.
- `record-decision` is what marks a message handled — always call it for every
  candidate, including skips, or it will be re-evaluated next run.
- `finalize` must always run, even with zero candidates.
- If a subcommand returns non-zero or `{"ok": false}`, treat it as a hard error:
  collect it into `errors` for `finalize`, do not pretend success, and continue
  with the next candidate unless the failure is catastrophic (auth failure, no
  destinations available).
```

## 阶段 5 — 搭建状态、记忆和仪表盘

1. **`memory/state.json`** — 如果创建提示词指定了一个 UUID，它已经
   已编写；否则创建 `{ "id": "<uuid>", "runCount": 0 }`。`id` 是永久的，绝不能更改；每次运行时会增加 `runCount`。
2. **`memory/notes.md`** — 创建一个带有 `## Tuning` 标题和空内容的文件。
   `## Run log` 部分。
3. **`reports/`** — 创建空目录。
4. **`VISUAL.html`** — 编写一个自包含的“等待首次运行”占位符
   带有 `data-factory-visual-scaffold="true"` 的仪表板 `<body>`。`finalize` 子命令会在首次运行时用真实数据重新生成它，所以简单的品牌占位符即可。使用 Factory 醒目标记 `#EE6018` 和自动化名称作为 `<h1>`.

## 阶段 6 — 验证

- `python3 run_triage.py --help` 打印帮助信息且无错误。
- `memory/config.json` 和 `memory/secrets.json` 存在并能解析为 JSON。
- `.gitignore` 排除 `memory/secrets.json` 和 `memory/*.db`.
- `HEARTBEAT.md`, `run_triage.py`, `memory/state.json` 和 `VISUAL.html` 存在。

## 完成定义

自动化根目录包含 `HEARTBEAT.md`, `run_triage.py`, `VISUAL.html`, `.gitignore`, `memory/config.json`, `memory/state.json`, `memory/notes.md`, 以及一个空的 `reports/` 目录；秘密信息存储在 `memory/secrets.json`（被 .gitignore 排除）中；且 `run_triage.py --help` 能干净地运行。
