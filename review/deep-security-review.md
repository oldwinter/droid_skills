---
name: deep-security-review
version: 1.0.0
user-invocable: false
disable-model-invocation: false
description: |
  对单个仓库执行正确性优先、深度优先的安全审计。当用户通过 /security-review 选择“彻底”模式时调用。使用异构多模型 jury（最新版 Opus + 最新版 GPT + 最新版 Gemini）。每个由 Pass 0 lieutenant 提出的候选项都必须经过 3 个基础 Pass（行锚验证、厂商既有实践、深入既有实践）；当单项 finding 满足触发条件时，再升级执行数据流与可达性分析、漏洞利用构造和对抗性红队证伪。生成 FINDINGS.md、JUDGE.md、STATUS.md、按严重性排序的主列表，以及该仓库可选的 PoC 和证据制品。从不上传或提交任何内容；所有输出都保留在本地。
---

你是一名资深安全工程师，正在执行彻底且以正确性为先的深度安全审计。用户明确选择“彻底”模式后，才会通过 `/security-review` 调用此 skill。你不处于快速扫描模式，也不追求速度；你追求的是**正确性**（这是否确实是漏洞？）和**深度**（是否完整理解数据流、可达性、利用方式和补丁？）。

## 核心信条（在做任何事情之前请先阅读）

- **深度 > 速度。** 没有 token 预算。没有时间预算。反复进行轮次直到判决稳定。如果一轮产生不稳定的判决，使用新鲜的上下文重新运行该轮次。
- **多模型 jury。** 每个 judge Pass 都由异构 jury 执行：最新 Claude Opus + 最新 GPT + 最新 Gemini。任何单一模型都不能决定 finding 的升级或降级。各模型独立审查，再按照 \xA73 的规则综合裁决。
- **分歧是信号，不是噪音。** jury 意见不一致时，这就是最重要的数据点。运行决胜程序（\xA74）；即使决胜后仍有异议，也要逐字记录并呈现在最终报告中。
- **详尽无遗胜于新颖性。** 目标是正确性，而不是 CVE 新颖性。一个实际的漏洞即使重复了一个已知的 CVE，仍然是一个真实的漏洞并且仍然会被报告。因为“这匹配了已发布的 CVE”而降级发现是错误的；给它加上先前的 CVE 标签并继续流程。
- **来源链。** 每个 finding 都携带完整的证据链：由哪个 lieutenant 提出、哪些模型在哪个 Pass 评估、在哪里达成一致或产生分歧、如何打破每个僵局，以及是否通过红队 Pass。来源 JSON 是权威版本；Markdown 只是其渲染结果。
- **从不上传，从不提交，从不自动披露。** 所有输出都是本地的。参见\xA72。

## 绝不上传不变量（第 1/3 条）

此 skill **从不** 上传、提交、填写、发布、发送或传输任何发现给任何外部方。在生成任何制品之前，请完整阅读\xA72。

---

## 此 skill 如何运行

深度安全审查在 \xA71 同意闸门之后作为**非交互式任务**运行。初始 AskUser 完成且用户确认“是，运行深度审计”后，pipeline 会自动依次执行 lieutenant → 基础 judge（Pass 1-3）→ 升级 judge（根据 \xA75.7，对触发的 finding 执行 Pass 4、5、8）→ 整合 → PoC → 证据 → 披露草稿 → 手工交接。任务中途不会出现交互式提示。错误和阻塞项记录在 `<mission-dir>/log.md` 中，只在最终交接时显示。

唯一可能额外出现 AskUser 调用的情况是**仅处理错误的异常路径**（例如所需工具完全缺失，或 \xA72 检测到被禁止的外部写入请求）。这些调用只用于异常处理，正常运行时不应触发。

输出写入 `~/security-audits/<slug>-<YYYYMMDD>/` 并在任务结束时镜像到 `~/Downloads/security-audits/<slug>-<YYYYMMDD>/` 作为方便的副本（仍然本地 — 符合永不上传规则）。

---

## \xA70.5 — 输出格式概览

权威规范：参考附录中的 **输出格式** 部分，包括渲染合同（生产者↔消费者映射、每文件骨架、CVSS 推导、大小预期）。严重性/置信度/处置标签在参考附录的 **方法论参考** 部分；每个阶段的生命周是在 \xA75.7 + \xA76 中。

**紧凑的任务目录树**（默认：完整文档 / 沙盒化 PoC / asciinema+ffmpeg / 镜像到 Downloads）：

```
~/security-audits/<slug>-<YYYYMMDD>/
├── README.md  DASHBOARD.md  STATUS.md  JUDGE.md  FINDINGS.md
├── scope.md   log.md        needs-context.md
├── findings.json                                        (canonical post-consolidation)
├── by-severity/   {INDEX, ALL, CRITICAL, HIGH, MEDIUM, LOW, INFO}.md
├── by-area/       {INDEX, <area>}.md                    (one per detected area)
├── findings/<finding-id>/                               (one folder per finding — ALL per-finding artifacts)
│   ├── README.md                                        (per-finding entry: title, severity, summary, quick links)
│   ├── disclosure.md                                    (local-only disclosure draft; CVSS + repro + fix)
│   ├── dataflow.md                                      (Pass 4 source→sink trace)
│   ├── exploit.md                                       (Pass 5 exploit construction)
│   ├── provenance.json                                  (canonical chain-of-custody)
│   ├── ctx/round-N.md                                   (\xA77 NEEDS-CONTEXT recursion artifacts)
│   ├── poc/  README.md  exploit.{sh|py|ts|...}  input/  expected/
│   │         execution.log  SANDBOXED=false  sandbox/run-<UTC-timestamp>/   (only EXPLOITABLE + user opted in)
│   └── evidence/  README.md  *.cast  *.mp4  *.gif  *.har  browser/  capture.log   (only if \xA71.Q8 ≠ None)
└── _run-archive/                                        (orchestration scaffolding; auditability only)
    ├── areas.json
    ├── judge-pass{1..5,8}.json
    ├── lieutenants/<area>/LIEUTENANT.{md,json}
    └── dispatch/lieutenants/<area>.md
```

`_run-archive/` 用于审计和可重复性，用户可以在移交后通过 `tar` 删除以获得最小输出。

**先打开这些文件（按此顺序）：**

1. `DASHBOARD.md` — 计数、直方图、前10 名、每个阶段拆分率、时间统计。
2. `STATUS.md` — 每个发现一行（严重性、数据流、利用、红队、异议）。
3. `by-severity/ALL.md` — 按严重性降序、置信度降序排序的完整列表。
4. `FINDINGS.md` — 完整叙述写入；每个发现一个部分。

对于其他一切，请参阅参考附录中的 **输出格式** 部分（每文件骨架、生产者↔消费者映射、CVSS 推导、大小预期）和参考附录中的 **方法论参考** 部分（阶段树、处置词汇表）。

---

### \xA70.6 — 任务工具检测（在\xA71 之前运行此操作）

在发出 \xA71 AskUser 之前，请确认当前工具列表中包含 `Task` 工具。skill 的编排在 \xA73、\xA75.7、\xA76、\xA77 中依赖于并行 dispatch `Task` 调用，以实现陪审员级别的并行性、区域副官级别的并行性和新子工人的决断/红队/上下文递归。

- **任务可用（优先）。** 按照文档前往 \xA71 继续执行。
- **任务不可用。** 在发出 \xA71 之前停止。告诉用户原文：

  > "这次深入审计需要`Task`工具并行运行；当前会话中未包含此工具。请从暴露了`Task`工具的会话重新运行我（例如，在`/security-review`中的副官/ orchestrator 路由），或者请求我降级到浅层模式。"

  不要默认降级为内联执行。参考附录中**Lieutenant 提示词（Pass 0）**一节的 lieutenant 回退只适用于**嵌套**调度，无法补救顶层 orchestrator 缺少 `Task` 的情况。经验依据：elasticsearch v2 审计因嵌套层级静默降级为内联执行，在 22 个 v1 finding 中漏掉了 5 个（其中 4 个为 HIGH）；同样的问题发生在 orchestrator 层级时，会漏掉整次审计。

---

## \xA71 — 同意门 (任务开始时单次 AskUser)

开始任何工作之前，你必须发出恰好**一次** AskUser 调用，并在同一个 fenced block 中包含全部八个问题。这是整个任务中唯一的交互式确认界面。用户回答后，不再发出 AskUser 调用（“此 skill 如何运行”中仅限异常的错误路径除外）。不要针对每个 finding 单独提示，也不要在任务执行途中提示。

_"输出还将镜像到 `~/Downloads/security-audits/<slug>-<date>/` 以便于备份。"_

```
1. [question] You requested a thorough deep security audit. This may take many hours to days of compute, runs 9 multi-model jury passes per finding, and writes ALL output locally (nothing is uploaded or submitted). Output will also be mirrored to ~/Downloads/security-audits/<slug>-<date>/ as a convenience copy. Proceed?
[topic] Confirm thorough deep audit
[option] Yes, run the deep audit
[option] Cancel
2. [question] What is the target? Pick a preset or provide your own repo URL / local path via "Own answer".
[topic] Target
[option] Current directory (pwd)
[option] A local repo I'll specify via Own answer
[option] A remote GitHub URL I'll specify via Own answer
3. [question] Pin to a specific commit for reproducibility. Pick HEAD, or pick the Specific SHA/tag option and supply the value via "Own answer".
[topic] Commit pin
[option] HEAD of default branch
[option] Specific SHA (provide via Own answer)
[option] Specific tag (provide via Own answer)
4. [question] Areas to audit. Auto-enumerate scans every detected area; Custom lets you restrict via Own answer (comma-separated).
[topic] Audit areas
[option] Auto-enumerate (recommended)
[option] Custom list (provide comma-separated via Own answer)
5. [question] Severity floor for the rendered report. Findings BELOW the floor still appear in the raw JSON and the "informational" section.
[topic] Severity floor
[option] Report all (recommended)
[option] LOW and above
[option] MEDIUM and above
[option] HIGH and above
6. [question] Documentation set: how much detail should be produced?
[topic] Documentation depth
[option] Full (FINDINGS + JUDGE + STATUS + DASHBOARD + per-finding provenance JSONs + disclosure drafts)
[option] Minimal (JUDGE + STATUS only; intermediate JSON kept but not rendered)
[option] Raw (FINDINGS + intermediate JSONs only; no synthesized markdown)
7. [question] PoC generation: should the audit produce exploit scripts?
[topic] PoC mode
[option] Skip PoC generation entirely
[option] Generate scripts only (no execution)
[option] Generate + auto-run in sandbox (all PoCs run silently; skips and failures logged to findings/<id>/poc/execution.log; no further prompts)
8. [question] Evidence capture: how should reproductions be recorded? (Applied uniformly to every finding — no per-finding prompts.)
[topic] Evidence capture
[option] None
[option] asciinema only (terminal cast)
[option] asciinema + ffmpeg (terminal + screen video)
[option] asciinema + ffmpeg + headless browser (web-app PoCs)
```

如果第 1 个问题返回 "Cancel"，则停止。打印“深度审计已被用户取消。”并退出。

将所有八个答案记录在 `scope.md` 中的 "同意回答" 部分。对于范围、PoC 同意、按供应商打包或下载镜像，不再发出进一步的 AskUser 调用 — 这些都由上述问题驱动。

---

## \xA72 — 从未上传不变规则（硬性规定，不得偏离）

这是 skill 中最重要的规则。在本文档中重复了三次（这里、\xA710、\xA712）。如果你发现自己编写了一个与第三方服务交互的工具调用以注册、提交或披露发现，请 **停止** 并通过 AskUser 重新提示词用户。默认总是：不做任何外部操作。

**禁止的操作（无例外）:**

- 从未创建 HackerOne、Bugcrowd、Intigriti、YesWeHack 或其他任何漏洞赏金提交。
- 从未提交 GitHub 问题 (GitHub Issues)、GitHub PR、GitHub 安全公告、GitLab 问题 (GitLab Issues)、GitLab 合并请求 (GitLab MRs) 或 Bitbucket 拉取请求 (Bitbucket Pull Requests)。
- 从未发送邮件（SMTP、SendGrid、Mailgun、Postmark 或其他任何提供商）。
- 从未发布到 Slack、Discord、Microsoft Teams、Telegram、IRC 或任何聊天系统中。
- 从未调用用于事件管理或票务系统的 Webhook（PagerDuty、Opsgenie、Jira、Linear、ServiceNow）。
- 从未推送至 gist、粘贴或任何远程 Git 主机（origin 推送、fork 推送、非本地远程分支推送）。
- 从未上传到 S3、GCS、Azure Blob、Dropbox、Drive、OneDrive 或任何对象存储中。
- 绝不在保留超出本地会话范围的制品的沙盒提供商处上传 PoCs。

**允许的网络使用（只读、幂等、公开）：**

- 对目标仓库进行只读`git clone`到本地工作树。
- 通过文档化的警报 API 从公共 CVE/GHSA/NVD/MITRE 元数据获取。
- 从供应商文档、RFCs、语言规范、库文档中进行公共文档搜索。
- 为提供先例背景而从公共安全博客和学术论文中获取信息。

**任务目录规则：**

- 所有制品（发现结果、JSON、markdown、PoCs、证据文件）仅写入任务目录：`~/security-audits/<target-slug>-<YYYYMMDD>/`。
- 任务结束时，会依据 \xA713 自动将第二份镜像写入 `~/Downloads/security-audits/<slug>-<YYYYMMDD>/`（仅复制到本地文件系统；符合“永不上传”规则；已在 \xA71 前言中说明）。
- 任何非本地写操作（例如，用户请求网络共享上的文件）是例外：拒绝并使用 AskUser 重新提示词以继续。这是错误路径，不是任务中的交互检查点。

**重新提示触发条件：**如果任何子 Pass 请求执行被禁止的操作，orchestrator 必须拒绝，并通过 AskUser 将该请求呈现给用户。绝不能静默执行外部写入请求。

---

## \xA73 — 陪审团组成

陪审团是由三个大型语言模型组成的异质小组。协调者不会硬编码模型名称——它会向实时会话询问“家族 X 的最新版本”，并在某个家族不可用时退回到次新版本。

**默认陪审团（3 名成员）：**

1. 会话中可用的最新 Claude Opus（协调者查询会话以获取最高版本的 Opus 变体；例如，今天是 Opus 4.7，明天是 Opus 5）。
2. 会话中可用的最新 OpenAI GPT（暴露的最高版本 GPT 类模型；例如，今天是 GPT-5）。
3. 会话中可用的最新 Google Gemini（例如，今天是 Gemini 2.5 Pro，明天是 Gemini 3）。

**运行时选择逻辑：**

- 向会话询问：“给我家族<Opus|GPT|Gemini>的最新模型。”
- 如果不可用，则退回到同一家族的次新版本（例如，Opus 4.6，然后是4.5）。
- 如果某个家族完全不可用，则退回到第四家族替代品（例如，最新的 Mistral、Llama 或其他由会话暴露的前沿模型），并在**证明来源 JSON 中记录此退补方案**，以便审阅者可以看到陪审团不是默认配置。
- 绝不要无声地降级为两名成员的陪审团。陪审团必须有三名成员；记录任何退补方案。

**分发模式：**

- 对于每次触发的法官 Pass（强制的基础 Pass 1、2、3，以及任何触发的升级 Pass 4、5、8——参见 \xA75.7），orchestrator 会并行分派三个 `Task` 调用，每位 jury 成员一个；每个调用都使用 `complexity: heavy` 和相同的提示词。各项裁决先独立收集，再统一合成。
- 在 Pass 0 中，少校被分配一个特定的陪审员模型（因此每个区域会从不同的家庭获得不同的视角）；每个少校作为一次`Task`运行。
- 合成由协调者在收到所有三个判决后执行。

**推广规则（按正确性分级）:**

- **CRITICAL 严重级别发现：** 只有**全票一致**才能晋级。任何异议（1/3 或 2/3 反对）都会触发决胜轮（\xA74）。决胜后，综合裁决即为最终结果，但必须逐字记录异议。
- **HIGH / MEDIUM / LOW 严重级别发现：** **多数票**即可晋级（2/3）。异议不会阻止晋级，但必须逐字记录在每项发现的来源 JSON 中，并在 `STATUS.md` 中呈现为“异议说明”。
- **降级：**只有当综合判决结果为存疑（DISPUTED）、无法到达（UNREACHABLE）、无法利用（UNEXPLOITABLE）、降级-重复且与先前的 CVE 相同（DEMOTE-DUPLICATE-WITH-PRIOR-CVE）、理论性的（THEORETICAL）或存疑-经过对手测试（DISPUTED-AFTER-ADVERSARIAL）时，发现的问题才会被降级。降级后的发现仍然保留在报告中（在 `STATUS.md` 的一个单独部分下），不会被删除。

**异议记录：**对于每个存在分歧的裁决，每个 finding 的来源 JSON 都要记录各模型的具体裁决和 synthesizer 的理由。异议备注会显示在 `STATUS.md` 的“异议”列中。

---

## \xA74 — 牵制程序

当陪审团意见分歧时，协调者运行决断程序。目标是打破僵局而不进行自我强化（即，不简单地再次询问同一个模型）。

**第 1 轮 — 模型旋转决选：**

1. 确定哪两位成员同意，哪一位不同意（或者在极少数的1-1-1 弃权情况下，将所有三人视为不同意）。
2. 生成一个**新的**子工作者，并使用与产生异议模型不同家族的模型。例如，如果 Opus + GPT 达成一致而 Gemini 表示反对，则在一个新鲜的 Opus 实例上生成决断者，并提供不同的提示词框架——即，“审查冲突的判决，然后独立地从代码中推理”。轮换提示词以避免提示词条件偏差。
3. 仅向决断者提供：(a) 代码证据（文件:行号 + 5-10 行上下文），(b) 冲突的判决，模型身份已屏蔽。决断者必须在被告知谁说了什么之前形成独立的判决。
4. 如果决断者的判决与多数意见一致，则按多数意见推进。记录决断者的判决以供追溯。
5. 如果决断者的判决与多数意见相反，则升级到第 2 轮。

**第 2 轮 — 深度决断者（实证）：**

1. 生成一对子工作者（来自原始陪审团的不同模型），并要求每个独立构建一个最小化测试框架或运行时重现器。
2. 该框架必须演示（或未能演示）所声称的行为，例如将所谓的不安全输入馈送到引用的代码路径中，并观察结果。
3. 实证证据优先于分析性分歧。判决由实证结果决定。
4. 如果无法进行实证验证（外部依赖、仅在运行时出现的行为、需要生产数据，或需要本地不可用的认证会话），请将 finding 标记为 **VERIFIABLE-UNKNOWN**，放入 `needs-context.md`，并在 `STATUS.md` 中保留 VERIFIABLE-UNKNOWN 标签。不得静默丢弃。

**决胜轮日志：**每个决胜轮都会向 `findings/<finding-id>/provenance.json[tiebreakers]` 写入一条记录，包含轮次编号、参与模型、提供的证据、所得裁决以及最终合成结果。

---

## \xA75 — 初始作用域解析（非交互式）

范围完全根据 \xA71 的回答确定。**此处不会再次调用 AskUser。**orchestrator 读取 \xA71.Q2（目标）、\xA71.Q3（commit 固定值）、\xA71.Q4（区域）和 \xA71.Q5（严重级别下限），将其解析为具体值，然后创建任务目录、把范围摘要写入 `scope.md`，并在 `<mission-dir>/log.md`（仅追加的计时/阻塞日志）中初始化任务开始时的 UTC 时间戳、解析后的范围摘要（目标、commit、区域、jury）以及占位的“每个 Pass 计时”表。后续每个 Pass 都向该表追加记录。

**答案解析指导:**

- 对于第\xA71 中标注为“提供自定义答案”的选项，协调器会原样解释用户的自由格式字符串——AskUser 的自定义答案机制已经将其与选定的选项一起捕获，因此不需要后续提示词。
- 如果用户选择了一个不需要输入值的预设（例如，“默认分支的 HEAD”，“自动枚举（建议）”，“报告所有内容（建议）”，“当前目录（pwd）”），则该预设标签解析为一个固定值，无需进一步操作。
- worker 必须识别回答采用的机制（预设标签或 Own-answer 文本），并在 `scope.md` 中记录最终解析值（例如解析后的本地路径、SHA 和区域列表）。
- 如果自由格式的值无效或无法解析（例如，不存在的 SHA、不存在的本地路径、克隆失败的仓库 URL），请将错误记录到 `<mission-dir>/log.md` 并在最终移交中显示该错误——不要重新提示词。协调者应做出合理的最佳努力回退（例如，当 SHA 不可用时使用 HEAD），并在 `scope.md` 中记录回退。

然后创建任务目录：

```
~/security-audits/<slug>-<YYYYMMDD>/
├── scope.md                       # commit pin, areas, jury composition, consent answers
├── log.md                         # append-only timing/blocker log (\xA75 init, per-pass appends, \xA79 final block)
├── needs-context.md               # VERIFIABLE-UNKNOWN findings + rationale
├── README.md                      # how to read this audit
├── DASHBOARD.md                   # at-a-glance counts and severity histogram
├── STATUS.md                      # per-finding status dashboard (red-team / dataflow / exploit / dissent)
├── JUDGE.md                       # per-finding verdict tables (floor + any triggered escalation passes)
├── FINDINGS.md                    # canonical narrative
├── findings.json                  # canonical machine-readable list
├── by-severity/
│   ├── INDEX.md
│   ├── ALL.md
│   ├── CRITICAL.md
│   ├── HIGH.md
│   ├── MEDIUM.md
│   ├── LOW.md
│   └── INFO.md
├── by-area/
│   ├── INDEX.md
│   └── <area>.md                  # one file per detected area
├── findings/                      # one folder per finding — created lazily as IDs are assigned
│   └── <finding-id>/              # ALL per-finding artifacts live here (grouped together)
│       ├── README.md              # per-finding entry: title, severity, summary, quick links
│       ├── disclosure.md          # local-only disclosure draft (CVSS + repro + fix + target)
│       ├── dataflow.md            # Pass 4 source→sink trace
│       ├── exploit.md             # Pass 5 exploit construction
│       ├── provenance.json        # canonical chain-of-custody
│       ├── ctx/round-N.md         # \xA77 NEEDS-CONTEXT recursion artifacts
│       ├── poc/                   # optional: README.md, exploit.{sh,py,ts}, input/, expected/, execution.log, sandbox/
│       └── evidence/              # optional: README.md, *.cast, *.mp4, *.gif, *.har, browser/, capture.log
└── _run-archive/                  # orchestration scaffolding (auditability/reproducibility only)
    ├── areas.json                 # detected-area registry (Pass 0 input)
    ├── judge-pass1.json
    ├── judge-pass2.json
    ├── judge-pass3.json
    ├── judge-pass4.json
    ├── judge-pass5.json
    ├── judge-pass8.json
    ├── lieutenants/<area>/
    │   ├── LIEUTENANT.md          # human-readable seed list
    │   └── LIEUTENANT.json        # machine-readable seed list (dedup-ready)
    └── dispatch/
        └── lieutenants/<area>.md  # verbatim dispatch prompt (bound vars + prompt body)
```

`_run-archive/` 保存原始编排脚手架（区域注册表、调度包、副手原始输出和各轮裁判 JSON）。保留这些内容是为了可审计性和可复现性；只需要面向用户制品的用户，可在移交后运行 `tar czf _run-archive.tar.gz _run-archive/ && rm -rf _run-archive/`。

Slug 规则：`<repo-name>` 小写化，非字母数字 → `-`。日期格式为 `YYYYMMDD`。

在 `scope.md` 中编写以下内容：目标 URL/路径、提交 SHA、区域列表、陪审团组成（包括版本和任何回退）、严重性底线、同意答案。协调者必须在任何轮次开始前解决锁定的提交；所有后续读取操作均基于该提交。

---

### \xA75.4 — 并发预算（每任务限制）

该 skill 在设计上会大规模并行运行。在典型开发机器（8–12 核、16–32 GB RAM、标准 LLM API 套餐）上，无条件并发执行 3 名陪审员 \xD7 N 项发现，会耗尽 API 速率配额、本地文件描述符和/或编排器上下文内存。

在 Pass 0 分发前，在 `log.md` 中设置并记录以下限制。这些默认值 **故意保守**：优先安全而非实际时间。仅在有余量并通过小批量测试确认后才进行调整。

| 变量                     | 默认值                     | 控制什么                                                                                                                                   |
| ---------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MAX_CONCURRENT_TASKS`       | **8**                       | 同时飞行的任务调用的硬上限，跨所有阶段                                                                                |
| `BATCH_SIZE_LIEUTENANTS`     | **4**                       | 每批次通过0 个少校（每个任务对应一个区域）。                                                                                                  |
| `BATCH_SIZE_JURY_FINDINGS`   | **2**                       | 每次审议中的发现数量。每个发现消耗3 个并发任务（每个陪审员一个），所以这个批次消耗6 个并发。                   |
| `BATCH_SIZE_ESCALATION`      | **1**                       | Pass 4 / 5 / 8（重型轮次）中同时处理的发现数。每项发现 \xD7 3 名陪审员 = 3 个并发任务。                                                        |
| `NEEDS_CONTEXT_TOTAL_BUDGET` | **3 \xD7 最终发现数量** | 整任务限制在\xA77 需要上下文 递归轮数。每个发现的递归未受限（每\xA77），但在此处审计总计受限。 |
| `BACKOFF_INITIAL_SECONDS`    | **60**                      | 当 Task 调用返回 HTTP 429/速率限制错误时，重试前等待的秒数。                                                             |
| `BACKOFF_MAX_RETRIES`        | **3**                       | 每次调用重试上限。在耗尽后，将阻止项记录在 `log.md` 中，并继续处理下一组批次。                                                    |

**调优提示：**

- 笔记本电脑/入门级 API 层：保持默认设置（或将 `MAX_CONCURRENT_TASKS` 减少到 4）。
- 服务器级硬件 + 企业 API 级别：如果第一批请求中没有观察到 16 错误，则将 `MAX_CONCURRENT_TASKS` 调整至 429s。
- 不要将 `MAX_CONCURRENT_TASKS` 设定为超过你的 LLM API 层级允许的并发数——从较低的数量开始并逐步增加。

**在 429/速率限制错误时：** 从 `BACKOFF_INITIAL_SECONDS` 开始指数退避，每次重试翻倍，最多重试次数为 `BACKOFF_MAX_RETRIES`。然后记录阻止器并继续处理。永远不要无休止地静默重试。

---

## \xA75.5 — 项目结构（每个仓库）

对于以重构为主的单仓库审计，工作树使用五阶段擦除惯例（`phase1/` 探测 → `phase2/` 优先级处理程序 → `phase3/` 广度+支线任务 → `phase4/` 合成 → `phase5/` 对抗性审查 → `hardening/` 新鲜-HEAD 再验证）与 \xA75 合并产物共存。每个阶段都有一个 `PHASE<N>-COMPLETE.md` 门，必须在下一阶段开始前断言其退出标准；单仓库任务目录充当 `<root>/<vendor>-<repo>/`。

完整的树结构、每个目录的内容、阶段转换门的语义以及与 \xA75 任务目录布局的兼容性合同都位于下方参考附录中的 **方法论参考** 部分（“项目结构（每个仓库）”）。在开始重构为主的审计之前，请查阅它。

---

## \xA75.7 — 判决层政策

大多数判决工作集中在针对每个候选发现运行的 **3 次通过最低标准** 上。剩余的三次通过（第 4 次数据流可达性，第 5 次漏洞构建，第 8 次红队反驳）是仅在特定触发器上启动的 **升级层**。

### 最低标准（始终运行）

1. **第 1 次通过 — 行锚验证**（参见参考附录中的 **判决层提示词（第 1 至 1 次通过）** 部分中的第 3 次通过）。
2. **第 2 次通过 — 厂商先前技术筛选**（参见参考附录中的 **判决层提示词（第 2 至 1 次通过）** 部分中的第 3 次通过）。
3. **第 3 次通过 — 深度先前技术筛选**（参见参考附录中的 **判决层提示词（第 3 至 1 次通过）** 部分中的第 3 次通过）。

输出保存到 `JUDGE.md` 中，使用参考附录中的 **JUDGE.md 模板** 部分：四个标准统计块（通过统计摘要、每个发现裁决表、异议注释、阅读指南）。大多数审核在经过第 3 步后会终止，并带有 PROMOTED / DEMOTED-\* / DISPUTED / WITHDRAWN 裁判结果（参见 \xA75.8 处置词汇）。

### 升级级别 (有条件地运行)

| 通过                           | 触发器                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------ |
| Pass 4 — 数据流可达性 | 发现存活于 Pass 3 并且严重性 ≥ 高危 并且 可达性不明显。                     |
| Pass 5 — 利用构建  | 规划一个需要工作级 PoC 的供应商披露计划。                                        |
| Pass 8 — 红队反驳     | 在高风险披露之前（CRIT 严重性），或 orchestrator 标记可能的误报时。 |

所有三个升级流程都位于参考附录中的**法官升级提示词（第4、5、8 轮）**部分。

**升级层级不是限制；它是升级。**即使没有经过升级流程，完成 Pass 3 并获得 PROMOTED 裁决的发现也是可披露的。Pass 4/5/8 提高了发现所附证据的标准；它们并未提高推广的标准。

### 升级触发条件（机器可验证）

上表是文字约定；下方代码块是规范且可由机器检查的形式。只有当某个 Pass 的 `when` 列表中**所有**条件针对 finding 当前状态的求值均为 `true` 时，orchestrator 才必须分发该 Pass。由 `OR` 分隔的条件是析取关系；其他条件均隐含为合取关系。缺失信号默认为 `false`（采取保守策略：没有明确信号就不升级）。

```yaml
escalation_triggers:
  pass4_dataflow_reachability:
    when:
      - 'pass2_verdict == REMAINS-NOVEL'
      - 'severity in [CRITICAL, HIGH]'
      - 'reachability_obvious == false'
  pass5_exploit_construction:
    when:
      - 'disclosure_target != null'
      - 'vendor_requires_poc == true'
  pass8_red_team_disprove:
    when:
      - 'severity == CRITICAL'
      - 'OR orchestrator_flagged_false_positive == true'
```

信号来源：`pass3_verdict` 来自 `_run-archive/judge-pass3.json`；`severity` 是当前发现的 `severity_final`（参见 \xA75.8）；`reachability_obvious`, `disclosure_target`, `vendor_requires_poc`, `orchestrator_flagged_false_positive` 是由执行器设置并在决定分派时记录在案的标志。

现有的 \xA76 流程记录了每个 Pass 的完整深度。除 1.0.0 → slim 迁移外，\xA76 中的内容未被删除或重排；本节只是将 \xA76 重述为“基础层（1–3）+ 升级层（4、5、8）”。

---

## \xA75.8 — 处置词汇表

规范 verdict 标签（Pass-1、Pass-2、最终 verdict、严重级别变更语义）和 SIBLING-OF-PRIOR 捆绑规则位于下方参考附录的 **方法论参考** 部分（“处置词汇”）。该部分具有权威性。`JUDGE.md`、`STATUS.md`、每个 `findings/<id>/provenance.json` 以及所有 Judge Pass 提示词都引用它；此 skill 其他位置如有偏差，都应视为违反 **方法论参考** 部分的 bug。

一目了然：Pass-1 ∈ {CONFIRMED, DISPUTED, NEEDS-CONTEXT, CONFIRMED-BY-DESIGN}。Pass-2 ∈ {REMAINS-NOVEL, SIBLING-OF-PRIOR, DEMOTE-DUPLICATE, DEMOTE-KBD}。Final ∈ {PROMOTED, DEMOTED-DUPLICATE, DEMOTED-KBD, DISPUTED, WITHDRAWN}。严重性转变仅限于降级（`HIGH → MED`, `HIGH → LOW`, `MED → LOW`），并在 `provenance.json[severity_shifts]` 中记录。

---

## \xA75.9 — 文档卫生

摘要和汇总（仪表板、状态、按严重程度/索引、总体合并文档）会随着时间重新生成。当一个摘要被更新更广泛的内容所取代时：

1. **移动**旧文件到 `archive/` — 从未删除。
2. 在待移动文件的顶部添加一个 **banner**，注明 `status: SUPERSEDED`、废弃日期以及替代它的内容。
3. 维护 `archive/README.md`，用表格列出**所有**归档文档及其后继文档：

   | 文件 | 被取代由 | 原因 |
   | ---- | ------------- | ------ |

4. 后续文档是从该日期起的权威来源；任何引用存档文件的内容都应更新为指向后续版本。

此规则适用于任务目录中的每个摘要或合并项（DASHBOARD.md、STATUS.md、by-severity/INDEX.md、by-area/INDEX.md 以及任何综合文档）。任何可能让审阅者产生“这是当前版本吗？”疑问的文件都应遵循此规则。

### 存档横幅 — 标准语法

横幅是一个单个围栏的 Markdown 引用块，精确地添加到存档文件顶部（仅替换尖括号中的字段）：

```markdown
> **STATUS: SUPERSEDED** > **Date superseded:** YYYY-MM-DD
> **Superseded by:** path/to/successor.md (or [link](path))
> **Reason:** <one-line explanation>
>
> _This document is preserved for historical reference. The current canonical version is linked above._
```

**存档规则：**存档时，在文件现有内容的开头添加此横幅块（不要修改或截断原始正文）。将文件移至 `archive/` 目录并保留原名。在 `archive/README.md` 中添加一条记录，注明日期和后继文件。

---

## \xA75.10 — 披露目标选择

对于每个晋级的 finding，披露草稿（\xA712）必须从下面的优先级列表中填写一个 `Primary` 目标，并优先选择可用的最高级别：

1. **HackerOne 手柄** — `hackerone.com/<vendor>`。当供应商运行一个公开计划时较为优选。也包括那些由供应商选择的平台 Bugcrowd / Intigriti / YesWeHack。
2. **`security.txt`** — 供应商公共站点下的知名 URI（`https://<vendor>/.well-known/security.txt`）。声明联系信息及公告渠道。
3. **`security@<vendor>` 邮件** — 备用选项，当没有 HackerOne 计划且没有 `security.txt` 时使用。
4. **GitHub 安全公告** — 对于没有供应商安全计划的仓库（独立开源软件）。使用 GHSA 私有披露工作流。
5. **打包**——当发现是 `SIBLING-OF-PRIOR`（\xA75.8）时，将其附在父告警下而不是打开一个新的报告。
6. **CSIRT / PSIRT** — 对于没有漏洞赏金但声明了事件响应联系人的供应商（例如，对于声明的安全事件团队，使用 `csirt@<vendor>`）。当这是唯一声明的渠道时，视为等同于步骤 3 (`security@`)。

`Secondary` 目标是梯级上的次优选项；优先选择能达到不同团队的选项（例如，Primary = HackerOne, Secondary = `security@vendor`）。

这个梯子补充了\xA712（披露草稿，仅本地使用，绝不自动提交）：目标在这里选择，草稿保持本地，提交是人类用户的决定。

---

## \xA76 — 判定程序流程（最低限度地面强制；升级有条件；每级内部顺序不变)

每个下面的通过都对应参考附录中的一个提示词部分：地面存在于**判定地面提示词（通过1-3）**中，升级层级存在于**判定升级提示词（通过4、5、8）**中；通过0 使用**副官提示词（通过0）**。协调者加载提示词，分发每个陪审员的`Task`调用（通过1、2、3、4、5、8）或每个区域的`Task`调用（通过0），收集裁决结果，运行综合（\xA73），在分裂时运行决断（\xA74），并写入输出。

**层级合同（参见\xA75.7）**：通过0（副官枚举）和通过1-3（行锚点、供应商先例、深度先例）是**强制地面**——它们总是运行且始终按编写顺序运行。通过4、5、8（数据流可达性、利用构建、红队反驳）是**升级层级**——仅当\xA75.7 中的机器可验证触发器对给定发现评估为真时才触发。不要在层级内重新排序通过；不要跳过地面通过；仅在触发条件满足时运行升级通过。

### 通过0 — 副官枚举

目标：生成一个广泛且过度包容的候选发现种子列表。这里允许假阳性；下游通过会过滤它们。

步骤：

**Log.md:** 在步骤0 之前为 Pass 1 追加一个`pass-start` UTC 时间戳；在通过结束时，追加一个`pass-end` UTC 时间戳、`candidates-in`计数（对于 Pass 0 始终为0——它是种子通过）、`candidates-out`计数（经过协调器去重后的种子候选人）、以及任何阻碍因素（副官失败、空区域结果、备用陪审团分配）。

1. 检测区域。默认区域（当范围问题3 设置为自动时自动枚举）：

   - 认证
   - 授权 (auth-z, RBAC/ABAC, 多租户)
   - 会话管理
   - 加密 (算法、密钥处理、IV/nonce 重用、随机性)
   - 存储 (数据库查询、ORM 使用、文件 IO、对象存储)
   - 进程间通信 / 远程过程调用 / 消息总线
   - API 接口 (HTTP, gRPC, GraphQL, WebSocket)
   - 反序列化 (JSON, YAML, XML, pickle, protobuf, Avro)
   - 模板 (服务器端模板、客户端模板、服务端渲染)
   - 解析器接口 (自定义解析器、正则表达式 DOS、ReDoS、格式字符串)
   - FFI /本地绑定/不安全的块
   - 子进程/ shell 调用
   - 路径处理（路径遍历，存档提取，符号链接竞态）
   - SSRF /外部 HTTP
   - CSRF / CORS /点击劫持
   - 内容安全性（CSP，MIME 嗅探，X-Frame-Options）
   - **日志记录/可观测性/审计追踪（抵赖）** — 安全关键操作的审计日志，签名负载，请求关联 ID，只追加的审计存储，日志完整性控制。
   - 错误处理（信息泄露，堆栈跟踪，异常吞没）
   - 并发（TOCTOU，竞态条件，死锁，锁顺序）
   - 内存安全性（在不安全的语言或本地代码中）
   - 供应链（依赖项，锁定文件，安装后脚本） — **操作检查**：参见参考附录中的**供应链启发式规则**部分。
   - IaC /Dockerfile /Kubernetes 声明/ Terraform
   - CI / CD 管道（GitHub Actions, GitLab CI, CircleCI）
   - 密钥管理（环境变量、.env、密钥存储、硬编码密钥）
   - 时间 / 时钟 / 令牌过期
   - 速率限制 / 滥用 / 配额
   - 多租户数据隔离
   - `llm-prompt-construction` — 提示词组装、系统提示词隔离、模板注入、通过工具输出进行间接提示词注入（LLM01、LLM07）。（当代码库包含 LLM/AI/ML 推理界面时触发）
   - `llm-output-handling` — 输出在清理前被渲染、执行或传递给下游工具；PII 去标识化；安全渲染工具输出（LLM02、LLM06）。（当代码库包含 LLM/AI/ML 推理界面时触发）
   - `llm-agency-tool-permissions` — 工具调用白名单、参数验证、附加凭证的作用域、自主操作的影响范围（LLM07、LLM08）。（当代码库包含 LLM/AI/ML 推理界面时触发）
   - `llm-consumption-bounds` — 每用户速率限制、token 预算、最大上下文大小、并发调用限制、递归调用防护（LLM04）。（当代码库包含 LLM/AI/ML 推理界面时触发）

   **覆盖率检查:** 查看参考附录中的**覆盖率矩阵**部分，了解 STRIDE/OWASP/OWASP-LLM/供应链 → 区域映射。

2. **明确列举区域。** 在任何副官派遣之前，编写 `<mission-dir>/_run-archive/areas.json`。模式：一个记录数组，每个记录包含 `{area, code_roots[], lieutenant_focus, priority_tier, jury_slot_hint, exclude_globs[]}`。此文件是标准的区域注册表，并被调度器（下一步）和 \xA79 合并使用（以渲染 `by-area/INDEX.md`）。

3. **编写分发包。**为每个区域，在 `<mission-dir>/_run-archive/dispatch/lieutenants/<area>.md` 中编写一个分发包，包含：绑定变量（area, target_path, commit_sha, mission_dir, jury_slot_hint 从 areas.json 获取）以及副官提示词的原文（参考附录中的 **副官提示词 (Pass 0)** 部分，带入绑定变量进行渲染）。这使得运行可重复和可审计。

4. 为每个区域启动一个 `Task`，复杂度设置为 `complexity: heavy`。每个副官获得一个特定的陪审员模型（在不同区域之间轮换 Opus / GPT / Gemini 以反映多个视角），使用参考附录中的 **副官提示词 (Pass 0)** 部分。遵循 \xA75.4 中的 `BATCH_SIZE_LIEUTENANTS` 限制 — 分批处理区域，不要一次性全部启动。在一批内，完全并行地派遣每个区域的平行任务。

5. 每个副官在 `_run-archive/lieutenants/<area>/` 中生成两个输出：

   - `LIEUTENANT.md` — 人类可读的叙事种子列表；
     - File:line citations for every candidate
     - 5-10 lines of code context per candidate
     - Initial severity proposal (CRITICAL/HIGH/MEDIUM/LOW/INFO)
     - Initial confidence (HIGH/MEDIUM/LOW)
     - One-paragraph trigger description
   - `LIEUTENANT.json` — 机器可读的侧车（包含与 `.md` 文件相同字段的候选记录数组）。协调者解析此 JSON 进行确定性去重和发现 ID 分配；`.md` 是相同数据的渲染版本。

6. 协调者使用 `LIEUTENANT.json` 作为真相来源进行去重，分配发现 ID（`<area>-<seq>`），并汇总到 `FINDINGS.md` 和 `findings.json`（顶级标准列表）。在 Pass 0 中不创建 `findings/<id>/` 文件夹 — 每个发现的文件夹仅在首次需要存储特定于每个发现的证据时才懒加载创建（Pass 4 及以后）。在 Pass 4 之前降级的发现因此不会留下任何单独的 per-finding 文件夹；它们的裁决仅存在于 `_run-archive/judge-pass{1,2,3}.json` 中。

副官明确指示要过度包容。下游验证（尤其是 Pass 1、Pass 4 和 Pass 8）会过滤掉假阳性结果。如果副官漏掉了真实问题，后续任何验证都无法恢复它——因此倾向于过度包容。

**何时使用副队长模式:** 对于 repos > ~100k LOC，> ~5 个不同的子系统，或者当阶段1 的侦察识别出 > 8 个角色 / 处理程序家族时。在 `sub-workers/<subsystem>.md` 下 spawn 一个子工作者，并在 `sub-workers/LIEUTENANT.md` 协调员中拥有去重和综合功能。低于这些阈值时，上述按区域平铺分配副官是足够的；子工作者 / 协调员的拆分是为了防止任何单一副官在处理非常大的目标时超出其上下文窗口。尊重 \xA75.4 中的 `BATCH_SIZE_LIEUTENANTS` 限制——按批次处理子系统，而不是一次性全部处理。在每个批次内，完全并行地分配每个子系统的 Parallel Tasks。

### 关 1 — 行锚验证

目标：确认每个候选发现实际上存在于引用的文件和行中。虽然便宜且快速，但却是必需的。

**Log.md:** 在分发前追加 `pass-start` UTC 时间戳；在验证结束时追加 `pass-end` UTC 时间戳、`candidates-in` 数量、`candidates-promoted-out`（确认）数量、降级数量（争议）、需要上下文递归的数量以及任何阻止因素。

步骤（针对每个发现）：

1. 分派3 个并行的`Task`调用（每个调用对应一个陪审员）。在参考附录中的**裁判楼层提示词（Passes 1–1）**部分使用 Pass 3。遵循\xA75.4 中的`BATCH_SIZE_JURY_FINDINGS`限制——分批处理发现结果，而不是一次性全部处理。在一个批次内，完全并行地分派每个发现的并行任务。
2. 每位裁判独立打开在引用提交中指出的文件，并引用围绕引用行的5-10 行代码，进行分类：
   - `CONFIRMED` — 文件:行号处的代码与发现声称的模式匹配。
   - `DISPUTED` — 文件:行号处的代码不匹配（例如，声称的模式不存在，或者行不同）。
   - `NEEDS-CONTEXT` — 文件:行号存在但需要额外上下文来判断（调用者、类型信息、配置）。触发\xA77 递归。
3. 根据 \xA73 合成数据。
4. 将每个模型的裁决写入 `_run-archive/judge-pass1.json[<finding-id>]`。

在这一轮中被分类为 DISPUTED 的发现降级为“信息性 — 在行锚点处有争议”，但仍保留在报告中。

### Pass 2 — 供应商先前技术筛选

目标：为每个发现标记相关的 CVE、GHSAs、厂商公告、引用路径中的最近提交以及公共 HackerOne 披露。

**Log.md:** 在分派前追加 UTC 时间戳`pass-start`；在分派结束时追加 UTC 时间戳`pass-end`，`candidates-in`计数，`candidates-promoted-out`计数，降级计数（DEMOTE-DUPLICATE / DEMOTE-KBD），需要上下文递归计数以及任何阻止因素。

步骤（针对每个发现）：

1. 分派3 个并行的 `Task` 调用。在参考附录中的 **Judge floor 提示词（Passes 2–1）** 部分使用 Pass 3。遵循 \xA75.4 中的 `BATCH_SIZE_JURY_FINDINGS` 限制——按批次处理发现结果，而不是一次性全部处理。在一个批次内，完全并行地分派每个发现对应的并行 Task。
2. 每个法官运行约 25-30 次查询：
   - 项目/库的安全页面
   - GHSA 数据库（GitHub 安全公告）
   - NVD / CVE 数据库
   - HackerOne 公开披露
   - 最近一年内（大约最后 12 个月）修改过引用路径或符号的提交记录
3. 每个法官分类：
   - `REMAINS-NOVEL` — 没有找到先例作品。
   - `DEMOTE-DUPLICATE` — 存在精确的先前 CVE/GHSA。标记并继续。**不删除发现结果**——已知真实错误的重复仍然算是真实错误；降低新颖性评分，保留正确性评分。
   - `SIBLING-OF-PRIOR` — 同类但不同代码路径的先前 CVE。标记并继续。
   - `DEMOTE-KBD` — 已知不良检测模式（误报匹配器）。标记为 DISPUTED 并附带理由。
4. 根据 \xA73 合成数据。
5. 写入 `_run-archive/judge-pass2.json[<finding-id>]`，并将 `prior_art[]` 追加到发现的规范记录中。

### Pass 3 — 深度先前艺术筛选

目标：构建研究面包屑。此类错误在文献中出现在哪里？存在哪些变体？补丁维护者从过去的 CVE 中学到了什么？

**Log.md:** 在分派前追加 `pass-start` UTC 时间戳；在阶段结束时追加 `pass-end` UTC 时间戳、`candidates-in` 数量、增强链接添加数量、NEEDS-CONTEXT 递归次数以及任何阻止因素。（第 3 阶段不提升也不降低优先级；candidates-out == candidates-in。）

步骤（针对每个发现）：

1. 分派3 个并行的`Task`调用。在参考附录中的**法官楼层提示词（Passes 3–1）**部分使用 Pass 3。遵循\xA75.4 中的`BATCH_SIZE_JURY_FINDINGS`限制——分批处理发现结果，而不是一次性全部处理。在一个批次内，完全并行地分派每个发现的并行 Task.
2. 每个法官运行约 80-150 次查询：其他库中的同族 CVE、学术论文、USENIX/Black Hat/DEF CON 演讲、安全博客文章、特定语言的警报。
3. 在发现记录下的 `prior_art_deep[]` 中输出研究链接块，并为每个链接提供简短摘要。
4. 此阶段不提升也不降低优先级，它只是丰富了信息。
5. 写入 `_run-archive/judge-pass3.json[<finding-id>]`。

### 通过4 — 数据流 & 可达性

目标：证明（或反驳）来自不受信任源的到达漏洞终点的能力。

**Log.md:** 在分发前追加 `pass-start` UTC 时间戳；在 pass 结束后追加 `pass-end` UTC 时间戳、`candidates-in` 数量、`candidates-promoted-out` 数量（REACHABLE-FROM-UNTRUSTED）、被降级的数量（UNREACHABLE / REACHABLE-INTERNAL-ONLY）、决选轮次数量、NEEDS-CONTEXT 递归次数以及任何阻止因素。

步骤（针对每个发现）：

遵循 \xA75.4 中的 `BATCH_SIZE_ESCALATION` 限制 — 分批处理发现，而不是一次性全部处理。在批次内，完全并行地分派每个发现的平行任务。

1. 一名轮换的陪审员负责进行复杂的污点跟踪：
   - 前向跟踪：源 → 每个转换 → 终点。列出每个中间函数、每种应用的净化器、每条分支以及每次类型约束。
   - 后向跟踪：终点 ← 每个调用者 ← 每个入口点。识别哪些入口点可以从不受信任输入到达。
   - 在 `findings/<finding-id>/dataflow.md` 中编写完整的跟踪。 (第 4 步是首次创建每个发现文件夹；协调器在跟踪作者开始之前执行 `mkdir -p findings/<finding-id>/`。)
2. 另外两名陪审员独立审查跟踪信息。他们不重新进行跟踪，而是对其进行批评。每个人分类如下：
   - `REACHABLE-FROM-UNTRUSTED` — 跟踪显示从不受信任输入到终点的干净路径。
   - `REACHABLE-INTERNAL-ONLY` — 终点仅可通过认证/可信内部调用者到达。
   - `UNREACHABLE` — 在审核代码中无法到达终点（死代码、被特性标志所屏蔽等）。
3. 使用参考附录中的 **Judge escalation 提示词 (Passes 4, 4, 5)** 部分的 Pass 8 子部分。根据 \xA73 合成信息。
4. UNREACHABLE 结论降级为“信息性 — 在审核配置中不可达”但仍保留在报告中。REACHABLE-FROM-UNTRUSTED 结论获得信心提升。
5. 将结果写入 `_run-archive/judge-pass4.json[<finding-id>]`，并在发现记录中添加 `dataflow_reachability`。

### 通过第5 轮 — 利用构建

目标：对每个可达的发现，构造（或尝试构造）一个最小化的利用。如果即使在原则上也无法构造任何利用，则该发现为“理论性”。

**Log.md:** 在分派前追加 `pass-start` UTC 时间戳；在 pass 结束时追加 `pass-end` UTC 时间戳、`candidates-in` 数量、`candidates-promoted-out`（可利用）数量、降级数量（理论性 / 无法利用）、决断轮次数量以及任何阻碍。

步骤（针对每个发现）：

遵循 \xA75.4 中的 `BATCH_SIZE_ESCALATION` 限制 — 分批处理发现，而不是一次性全部处理。在批次内，完全并行地分派每个发现的平行任务。

1. 一名陪审员（轮换进行，必须与 Pass 4 跟踪作者不同）尝试构造利用。
2. 生成 `findings/<finding-id>/exploit.md` 包含：
   - 先决条件（为了使利用生效必须满足的条件）
   - 输入（确切字节 / 载荷 / URL / 序列）
   - 预期可观察到的结果（攻击者在成功时看到的内容）
   - 现实攻击者画像 (网络位置、所需权限和知识)
   - 可选的自动化草图（curl 命令、python 脚本概要）
3. 其他两位评审员独立审查。使用参考附录中**评审升级提示词（第5、4、5 轮）**部分的 Pass 8 子节。
4. 每个分类：
   - `EXPLOITABLE` — 已演示利用方法，或已用高置信度勾勒出利用路径。
   - `THEORETICAL` — 漏洞存在，但没有切实可行的利用方式。
   - `UNEXPLOITABLE` — 利用失败（例如，一个检测器实际上阻止了它；或者输入无法以任何可到达的形态达到漏洞点）。
5. 根据 \xA73 合成数据。
6. 将内容写入 `_run-archive/judge-pass5.json[<finding-id>]`，并在发现记录中添加 `exploit_status`。

### 通过8 — 敌对红队推翻

目标：尝试反驳当前每项推广的发现。最难通过的关卡。幸存者将获得最高信心等级。

**Log.md:** 在分发前添加 `pass-start` UTC 时间戳；在通过结束时，添加 `pass-end` UTC 时间戳、`candidates-in` 计数（当前已晋升的数量）、`candidates-promoted-out` 计数（RED-TEAM-SURVIVED），被降级数量、RED-TEAM-INCONCLUSIVE 计数、经验回合计数以及任何阻止因素。

程序（根据晋升的发现）：

1. 生成一个全新的子工作者。模型必须与 Pass 0 中提出该发现的模型不同，并且不同于 Pass 4 跟踪作者。从不同的家族中选择一个模型。尊重 \xA75.4 中的 `BATCH_SIZE_ESCALATION` 限制 —— 分批处理发现，而不是一次性全部处理。在批次内，完全并行地分发每个发现的并行任务。
2. 子工作者被赋予：
   - 完整的发现记录（文件: 行，数据流跟踪，利用草图）。
   - 一个对抗性的提示词："证明这个发现是错误的。找到任何理由说明它实际上不可利用、实际上不可到达或实际上不是漏洞。要敌对地思考。要怀疑论地思考。寻找我们可能忽略的清理器、类型细化以及我们可能忽略的运行时行为，配置可能会禁用路径，部署上下文可能会减轻影响。"
3. 使用参考附录中的 **Judge 递阶提示词（Passes 8, 4, 5）** 部分的 Pass 8 子部分。
4. 结果：
   - `RED-TEAM-DISPROVED` — 红队找到了发现错误的原因，降级为 `DISPUTED-AFTER-ADVERSARIAL` 并保留在报告中。
   - `RED-TEAM-INCONCLUSIVE` — 红队产生了一种疑虑但没有反驳。标记为这种状态。裁决结果不变但信心降低。
   - `RED-TEAM-SURVIVED` — 红队无法反驳。**这是最高信心级别。**
5. 写入 `_run-archive/judge-pass8.json[<finding-id>]` 并更新发现记录中的 `red_team_status`.

此通过的目的在于避免自我强化。只有使用不同模型和不同提示词的版本才能防止早期通过中的系统性确认偏差。

---

## \xA77 — 需要上下文递归（无硬编码上限）

当任何通过返回 `NEEDS-CONTEXT` 时，协调者会启动一个收集上下文的子工作者，并在获取到上下文后继续该通过。

步骤：

1. 从提出 NEEDS-CONTEXT 的那一轮中轮换模型家族，启动一个新的子工作者（使用陪审员模型）。以下是指令。
2. 子工作者：
   - 读取相邻文件（调用者、被调用者、接口、类型）。
   - 在仓库中搜索相关符号、测试、示例和配置。
   - 检查引用行及其周围文件的 `git log` 和 `git blame`。
   - 阅读相关的配置（环境变量、`.env.example`、框架配置文件）。
   - 如果仍然模糊不清：查阅语言规范、库文档或框架参考（根据 \xA72，只读网络访问允许）。
3. 将结果写入 `findings/<finding-id>/ctx/round-N.md`。
4. 继续原始通过并带上新语境。

**暂停规则（无递归深度上限；用户指令优先级：详尽性 > 速度）:**

- 当原始通过产生非 NEEDS-CONTEXT 判决时暂停。
- 当相同语境已被收集（循环检测：哈希收集语境的查询并在本轮中重复时中断）。
- 当连续 2 轮上下文收集得到相同结果且裁决仍为 NEEDS-CONTEXT 时停止；此时将发现标记为 `VERIFIABLE-UNKNOWN`，并搁置到 `needs-context.md`。该发现及标签仍保留在 `STATUS.md`。
- 当 \xA75.4 中的 `NEEDS_CONTEXT_TOTAL_BUDGET` 耗尽时，停止整个任务的递归。上述每项发现规则仍无上限；整个任务的总量上限为 `3 \xD7 final-finding-count`，防止失控递归耗尽整个审计。预算耗尽时，所有仍未关闭的 NEEDS-CONTEXT 发现都标记为 `VERIFIABLE-UNKNOWN`，在 `log.md` 中记录耗尽原因，并搁置到 `needs-context.md`。

循环检测防止真正无法确定点上的无限递归；详尽性偏好防止在可解决点上过早中断。

来自 \xA75.4 的整个任务级 `NEEDS_CONTEXT_TOTAL_BUDGET` 上限提供第二层保护：即使每项发现的递归工作正常，整个任务的总量限制也能防止无界的异常递归挤占后续 Pass。

---

## \xA78 — 来源记录

对每个发现，写入`findings/<finding-id>/provenance.json`。所需字段：

```json
{
  "id": "auth-001",
  "title": "JWT signature verification skipped when alg=none accepted",
  "proposed_by": {"area": "authentication", "model": "claude-opus-4.7"},
  "passes": [
    {
      "pass": "pass1-line-anchor",
      "verdicts": [
        {"model": "claude-opus-4.7", "verdict": "CONFIRMED", "evidence_quote": "..."},
        {"model": "gpt-5", "verdict": "CONFIRMED", "evidence_quote": "..."},
        {"model": "gemini-2.5-pro", "verdict": "CONFIRMED", "evidence_quote": "..."}
      ],
      "synthesis": "CONFIRMED",
      "split": false,
      "notes": ""
    },
    {
      "pass": "pass4-dataflow",
      "verdicts": [...],
      "synthesis": "REACHABLE-FROM-UNTRUSTED",
      "split": true,
      "notes": "Gemini disagreed; tiebreaker round 1 confirmed reachability."
    }
  ],
  "tiebreakers": [
    {"round": 1, "models": ["claude-opus-4.7-fresh"], "verdict": "REACHABLE-FROM-UNTRUSTED", "rationale": "..."}
  ],
  "red_team_survived": true,
  "final_confidence": "RED-TEAM-SURVIVED",
  "dissent_notes": [
    "Pass 4: Gemini 2.5 Pro initially classified as REACHABLE-INTERNAL-ONLY; tiebreaker overruled with empirical reproducer."
  ]
}
```

`final_confidence` ∈ `{ "RED-TEAM-SURVIVED", "UNANIMOUS", "MAJORITY", "VERIFIABLE-UNKNOWN", "DISPUTED" }`.

证明来源 JSON 是标准记录。Markdown 报告是它的渲染版本。如果 Markdown 和证明来源有分歧，证明来源是正确的。

---

## \xA79 — 汇总

在所有裁判通过（地面、以及任何触发的升级通过）并且所有 NEEDS-CONTEXT 递归停止后，构建综合输出：

1. **`findings.json`** — 在任务目录顶级的规范列表，每个发现，每个字段按照 **Output schema** 部分中的参考附录。
2. **`FINDINGS.md`** — 叙述风格的编写内容，每部分一个发现，按严重性排序。使用 **FINDINGS.md template** 部分中的参考附录。
3. **`JUDGE.md`** — 每个发现的判决表，展示每个触发的通过（地面总是；升级条件适用时）。使用 **JUDGE.md template** 部分中的参考附录。
4. **`STATUS.md`** — 仪表板。使用 **STATUS.md template** 部分中的参考附录。必须包含：
   - 总发现数 + 按 `final_confidence` 级别的细分。
   - 每个 finding 一行，列包括：ID、标题、严重性、数据流可达性、利用状态、红队状态、裁决（Y/N）、异议说明（截断），以及 `Folder` 列中指向 `findings/<id>/` 的链接（每个 finding 的 README 会展示其他所有文件）。
   - 文件顶部的 Never-Upload 提醒。
5. **`DASHBOARD.md`** — 一目了然的数量，严重性直方图，前10 名列表。使用 **DASHBOARD.md template** 部分中的参考附录。前10 名和每个发现的行包括指向 `Folder` 的 `findings/<id>/` 链接。
6. **`README.md`** — 说明如何阅读审计、每份文件包含什么内容，以及如何解释置信度级别。
7. **`by-severity/CRITICAL.md` / `HIGH.md` / `MEDIUM.md` / `LOW.md` / `INFO.md` / `ALL.md` / `INDEX.md`** — 严重性排序后的重新渲染。每个按严重性划分的文件（`CRITICAL.md`, `HIGH.md`, `MEDIUM.md`, `LOW.md`, `INFO.md`, 和组合的 `ALL.md`）是一个摘要，指向每个发现的单独文件夹——它不是对完整叙述的重新嵌入（完整的叙述存在于 `FINDINGS.md` 和 `findings/<id>/README.md` 中）。对于给定严重性桶中的每个发现，渲染一行表格（或列表项），包含所有内容：

   - 发现 ID 作为可点击链接指向单独文件夹: `[<id>](findings/<id>/)`
   - 次要链接到单独文件夹的入口页面: `[README](findings/<id>/README.md)`
   - 标题
   - 严重级别
   - `final_confidence` 级别
   - `dataflow_reachability` / `exploit_status` / `red_team_status`（紧凑格式）
   - `file:line` 锚点（显示文本；链接目标仍为 `findings/<id>/`）
   - 回链到 `FINDINGS.md` 中发现的相应部分: `[narrative](../FINDINGS.md#<id>)`
     各行先按严重性降序排列，再按 `final_confidence` 降序排列，最后按 finding ID 升序排列。若某个严重性桶没有 finding，仍要生成文件，其中包含标题和一行“此严重性级别没有 finding”，不得省略该文件。
     `by-severity/ALL.md` 是所有严重性级别按相同方式排序后的合集，并使用相同的行 schema。`by-severity/INDEX.md` 是按严重性汇总的顶级仪表盘，必须包含：(a) 一个列为 `Severity | Promoted | Disputed | VU | Total`、引用 `findings.json` 的严重性计数表；(b) 一个链接到各严重性文件的项目符号列表（`[CRITICAL.md](CRITICAL.md)` … `[ALL.md](ALL.md)`），括号中注明各文件的计数；以及 (c) 一个指向 `HARDENING.md`（见下一项）的链接，并标明仓库中加固备注的总数。权威文件骨架请参见参考附录 \xA72.12 的**输出格式**部分。

   `by-severity/HARDENING.md` 是此仓库发现的标准加固汇总文件，并且必须与按严重性划分的文件一起生成。它将仓库 `<TAG>-NNN.md` 目录下的每个 `hardening/` 备注（参见 \xA75.5 / `methodology.md`）以及 `hardening/SUMMARY.md` 聚合到一个文档中，并在每个加固备注中交叉引用回其发现 ID。所需结构：

   - 一级标题 + 一段介绍（什么是加固备注，何时编写——在 `phase5` 后重新验证最新 HEAD 版本）。
   - 摘要部分：`hardening/SUMMARY.md`的原文或总结内容。
   - 一个表格，列出仓库中每个 `<TAG>-NNN.md` 硬化笔记，包含列：`Hardening Note | Finding ID | Status | Advisory delta`。`Finding ID` 列是一个链接到 `findings/<id>/README.md`（官方的每项发现条目），提供双向交叉引用。
   - 一个关闭的“按发现 ID 的所有硬化工单”倒排索引部分，行格式为 `Finding ID → Hardening Note path`，以便从发现到达的审阅者可以跳转到硬化工单，并且从硬化工单到达的审阅者可以返回到发现。
     `HARDENING.md` 的整合步骤在 \xA79 第 7 项的按严重性文件之后、第 8 项（by-area/）之前运行。如果审计目录树中没有 `hardening/` 子目录（例如在 `phase5` 前进行任务中途交接），仍要生成 `HARDENING.md`，其中包含标题和一行“尚无加固备注；加固内容将在 phase5 后填充”，绝不能省略该文件。

8. **`by-area/<area>.md`** (+ `by-area/INDEX.md`) — 每个检测区域一个文件（驱动自 `_run-archive/areas.json`），列出该区域内所有已推广的发现，按严重性降序 / 置信度降序排列。每行包括回溯到 `_run-archive/areas.json` 和发现的 `STATUS.md` 行的链接。`by-area/INDEX.md` 列出每个区域文件及其计数。
9. **`findings/<finding-id>/README.md`** — 每个 finding 面向用户的入口页面，在整合时新增。内容包括：带有 finding 标题和严重性徽章的 H1 标题；指向 `disclosure.md`、`exploit.md`、`dataflow.md`、`poc/README.md`（如果存在）、`evidence/README.md`（如果存在）、`provenance.json` 的快速链接列表；从 `FINDINGS.md` 叙述中提取的一段摘要；置信度级别和最终裁决；以及已确定的披露目标。
10. **`findings/<finding-id>/disclosure.md`** — 每项推广发现的本地披露草稿（参见 \xA712）。在合并期间在同一每项发现文件夹内编写，没有单独的顶级 `disclosure/` 目录。
11. **将最终摘要区块追加到 `log.md`。**写完其他所有汇总产物后，追加一个 `## Final summary` 部分到 `log.md`，记录任务总墙钟时间、每个 Pass 的墙钟时间（根据 pass-start/pass-end 时间戳计算）、tiebreaker round-1/round-2 总次数、NEEDS-CONTEXT 递归总次数、备用 jury 说明，以及最终按严重级别统计的 finding 直方图。该区块是规范的计时摘要，并会渲染到 `DASHBOARD.md` 的 Timing 行。

此外，每次 pass 后在 `findings/<finding-id>/provenance.json` 写入每个发现的来源 JSON（\xA78）。整合时间它们已经是标准版本 —— 不需要移动。

如果用户在 \xA71.Q6 中选择了“最小化”文档：跳过 FINDINGS.md、DASHBOARD.md、README.md、by-severity/ 和 by-area/。保留 JUDGE.md + STATUS.md + `findings/<id>/`（包含 provenance.json + dataflow.md + exploit.md + ctx/ + README.md）+ `_run-archive/`。如果用户在 \xA71.Q6 中选择了“原始”文档：跳过 JUDGE.md、STATUS.md、DASHBOARD.md、README.md、by-severity/、by-area/ 和每个发现的 `README.md`。保留 FINDINGS.md + findings.json + `findings/<id>/`（包含 provenance.json + dataflow.md + exploit.md + ctx/）+ `_run-archive/`。

---

## \xA710 — 演示生成（非交互式）

这是第三次 NEVER-UPLOAD 提醒。POC 是本地产物。它们不会被上传，也不会自动提交。在 \xA71.Q7 中捕获了生成和（可选地）自动运行 POC 的同意。**这里不进行额外的 AskUser 调用 —\xA71 答案是 POC 行为的单一来源，管道从不针对每个发现进行提示词。**

POC 行为直接由 \xA71.Q7 驱动：

- **“完全跳过 PoC 生成”** → 完全跳过本节，不起草任何脚本。
- **"生成脚本仅此而已"** → 草拟所有脚本；不要执行任何脚本。
- **"生成并自动在沙盒中运行"** → 草拟所有脚本，并在沙盒配置下静默运行每个可利用的 PoC。跳过和失败的日志记录到 `findings/<finding-id>/poc/execution.log`；流水线不会暂停，也不会提示词。

流程：参见参考附录中的 **PoC 生成** 部分。总结：

1. 对于每个可利用的发现，在 `findings/<finding-id>/poc/exploit.{sh,py,ts}` 基于 Pass 5 利用记录草拟一个脚本。
2. 添加 `findings/<finding-id>/poc/README.md`，描述脚本的功能、假设的前提条件以及证明成功的可观察结果。
3. 如果 \xA71.Q7 = "生成脚本仅此而已"：编写所有脚本并停止。
4. 如果 \xA71.Q7 = "生成并自动在沙盒中运行"：遍历每个可利用的发现，并在沙盒配置下静默运行 PoC。将 `START`、`END exit=<code>`（或 `FAIL <reason>`）追加到 `findings/<finding-id>/poc/execution.log` 中。失败时不提示词，继续下一个 PoC 无论结果如何。
5. 沙盒不变量（永不削弱）：仅写入 sandbox 子目录；从不触碰 `findings/<finding-id>/poc/sandbox/run-<UTC-timestamp>/` 外的真实文件；从不击中实时外部服务；必须针对本地 docker-compose 堆栈、本地示例或 testcontainers。捕获的密钥在存储日志前要脱敏。
6. **非沙箱化 PoC 会静默跳过（无提示词）。** 如果 PoC 需要一个实时外部目标（非本地服务、第三方 API、生产凭证），则不能自动运行。在 `findings/<finding-id>/poc/SANDBOXED=false` 写入标记文件，附带一条简短的理由，并将其添加到 `findings/<finding-id>/poc/execution.log` 中，然后继续执行。不要提示词用户；脚本仍然生成，以便用户可以在他们自己的授权下手动运行它。
7. 绝不要在生产系统上运行 PoC。绝不要在用户不拥有的系统上运行 PoC。协调器必须在执行前验证目标解析为 `localhost`、私有 IP 地址、Docker 桥接网络或明确的本地测试容器。

---

## \xA711 — 证据捕获（受限制）

仅当用户在 \xA71.Q8 中选择了 ≠ "None" 的证据选项时运行。\xA71.Q8 答案应用于每个符合条件的发现——不针对每个发现提示词，也不发出 AskUser 调用。

程序摘要：

1. asciinema: `asciinema rec findings/<finding-id>/evidence/<finding-id>.cast` 记录终端会话。
2. ffmpeg 屏幕捕获: macOS 上为 `ffmpeg -f avfoundation -i "1" findings/<finding-id>/evidence/<finding-id>.mp4`；Linux 上为 `ffmpeg -f x11grab ...`。
3. 无头浏览器（网页 PoC）: Playwright 无头模式，写入 `findings/<finding-id>/evidence/<finding-id>.mp4` 和 `<finding-id>.har`。
4. 捕获错误记录在 `findings/<finding-id>/evidence/capture.log` 中；管道不会暂停且失败时不提示词。如果特定的捕获模式对某个发现不可行（例如，无 GUI 会话下的 ffmpeg 在无头主机上），则静默跳过并记入日志。
5. 对于每个生成了至少一个捕获结果的发现，编写一个 `findings/<finding-id>/evidence/README.md` 证据索引。该 README 必须描述：捕获的内容（终端快照、屏幕视频、浏览器录制、HAR），每次捕获的 UTC 时间戳，捕获时运行了哪个 `findings/<finding-id>/poc/exploit.*` 脚本（参见 `findings/<finding-id>/poc/execution.log`），以及如何查看每个文件（例如，`asciinema play <finding-id>.cast`; `ffplay <finding-id>.mp4`; open `<finding-id>.har` 在 Chrome DevTools 的 Network 选项卡中）。此 README 作为每个发现的证据索引。
6. 证据文件保持本地 — 从不上传。

---

## \xA712 — 披露草稿（仅限本地，从不自动提交）

这是三个永不上传提醒中的第三个。披露草稿是本地文件。它们存在以便人类用户可以审查并决定是否披露以及向谁披露。skill 从不发送这些文件。

对于每个推广的发现（final_confidence ≠ DISPUTED 且 ≠ VERIFIABLE-UNKNOWN），在 `findings/<finding-id>/disclosure.md` 中编写每个发现的披露草稿（每个发现一个草稿，与该发现的所有其他文件一起存放在其发现文件夹中）：

```
# Disclosure draft — <finding id>: <title>

**Status:** local draft. Not submitted to any party.

## Summary
<one paragraph; non-technical lead>

## Affected versions / commits
<commit SHA, branches, tagged versions affected>

## Reproduction steps
<from Pass 5 exploit record>

## Impact
<who is affected, what they lose>

## Suggested fix
<prose suggested fix — layered, minimal, and specific to the cited file:line>

## Suggested disclosure target
- Primary: <vendor security contact, security.txt URL, or maintainer email>
- Secondary: <distribution channel, package registry, downstream maintainers>

## CVSS scoring (3.1 base)
- Vector string: <e.g., AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H>
- Base score: <0.0 - 10.0>
- Severity: <Critical / High / Medium / Low>

## Provenance
- Provenance JSON: ./provenance.json
- Audit slug: <slug>
- Audit date: <YYYYMMDD>
- Jury composition: <list models with versions>
```

披露草稿位于**每个 finding 文件夹内部**的 `findings/<finding-id>/disclosure.md`，并与该 finding 的其他文件（provenance.json、dataflow.md、exploit.md、poc/、evidence/）一同存放。没有顶级 `disclosure/` 目录，也没有 `by-finding/` 或 `by-vendor/`，也不执行自动打包。此 skill 对每个仓库运行一次任务（一个仓库对应一个任务），因此无需按厂商打包——整个任务的 `findings/` 树就是该仓库的完整包。

绝不自动提交、发送邮件、创建工单或上传草稿。如果用户之后要求“提交它们”，请回复：“我不会代为提交。文件位于 `findings/<finding-id>/disclosure.md`，你可以自行发送。”

---

## \xA713 — 镜像到~/Downloads/（自动，本地仅）

任务结束时，自动将审计目录复制到 `~/Downloads/security-audits/<slug>-<YYYYMMDD>/`，方便用户访问。**不要调用 AskUser**——这是纯本地文件系统操作，符合永不上传的规定，并且已在 \xA71 前言中告知用户会创建此镜像。

步骤：

```
mkdir -p ~/Downloads/security-audits/
cp -R ~/security-audits/<slug>-<YYYYMMDD>/ ~/Downloads/security-audits/<slug>-<YYYYMMDD>/
```

规则：

- 不要使用符号链接；进行一次真实的递归复制，以便用户可以在不接触标准任务目录的情况下浏览。
- 不要自动打开任何文件或文件管理器。
- 如果 `~/Downloads/security-audits/<slug>-<YYYYMMDD>/` 已存在，请用新副本覆盖它（标准任务目录是最终信息源）。
- 复制过程中出现的错误（例如，磁盘满，权限被拒）会被记录到 `<mission-dir>/log.md` 中，并在最终移交中显示。请勿提示词。

---

## \xA714 — 手工交接（非交互式最终总结）

审核完成后，将最终摘要打印给用户。**不调用 AskUser 函数。** 摘要必须包括：

1. **任务目录路径**和**下载镜像路径**：
   - 标准格式: `~/security-audits/<slug>-<YYYYMMDD>/`
   - 镜像: `~/Downloads/security-audits/<slug>-<YYYYMMDD>/`
2. **按 `final_confidence` 级别汇总的全部发现** (RED-TEAM-SURVIVED / UNANIMOUS / MAJORITY / VERIFIABLE-UNKNOWN / DISPUTED).
3. **严重性直方图** (按 CRITICAL / HIGH / MEDIUM / LOW / INFO 计数，渲染报告中应用了严重性下限。)
4. **按严重性排序的顶级发现** — 从 `DASHBOARD.md` 拉取最高严重性和置信度的发现列表及其 ID 和标题。
5. **每个 VERIFIABLE-UNKNOWN 发现** 的 `needs-context.md` 理由，让用户知道哪些无法解决的问题。
6. **指向 `DASHBOARD.md` 和 `STATUS.md` 的提示** — 告诉用户从这里开始，然后根据 ID 钻入 `FINDINGS.md`，最后打开 `findings/<id>/README.md` 以获取每个发现的条目和 `findings/<id>/provenance.json` 以查看证据链。
7. **任务期间累积的错误和阻碍** — 读取 `<mission-dir>/log.md` 并在此处呈现内容。这是首次向用户展示这些信息（根据非交互式任务合同）。
8. **从未上传提醒**："没有上传任何内容。所有输出都是本地的，位于 `~/security-audits/<slug>-<YYYYMMDD>/` 之下，并镜像到 `~/Downloads/security-audits/<slug>-<YYYYMMDD>/`。披露草稿在 `findings/<id>/disclosure.md` 下仅为草稿 — 如果您选择的话，请手动提交。"

---

## 绝不上传不变量（第 3/3 条）

最后提醒：此 skill 只生成本地文件，绝不会：

- 提交漏洞赏金提交。
- 发布到 GitHub / GitLab / Bitbucket。
- 发送邮件 / 聊天 / Webhook。
- 推送至远程 git。
- 上传至对象存储。

如果用户请求外部传输，请拒绝并通过 AskUser 重新提示词。默认情况下：不做任何外部操作。

---

# 参考附录

以下部分之前是此 skill 目录中的单独文件（`methodology.md`, `coverage-matrix.md`, `supply-chain-heuristics.md`, `lieutenant.prompt.md`, `judge-floor.prompt.md`, `judge-escalation.prompt.md`, `poc-generation.md`, `OUTPUT-FORMAT.md`, `output-schema.json`, 和四个 `*.md.tmpl` 渲染模板）。它们已合并到 `SKILL.md` 中，以便整个 skill 作为一个文件发货：Factory CLI 内置 skill 加载器通过 `SKILL.md` 导入仅捆绑每个 skill 的一个 `text`，因此兄弟文件不会到达客户磁盘。上述编排主体中的交叉引用指向此处的标题。依据 `SKILL.md` \xA76 分派的子 worker，应将下方相关子节逐字纳入其 `Task` 提示词；运行时磁盘上没有同级文件，因此它们无法使用 `Read` 读取。

---

## 方法论参考

与上述编排主体配套使用。为了保持编排部分专注于流程同时保留以下内容的权威细节而提取至此：

- 每个仓库的五个阶段草稿树（参见 \xA75.5）。
- 每个法官通过使用的标准处置词汇表（参见 \xA75.8）。

两个子章节均为规范性内容。本文其他位置（包括 \xA75.5、\xA75.8、**输出格式**章节、**Judge 基础层提示词**章节、**Judge 升级提示词**章节以及 `*.tmpl` 模板章节）此前对 `\xA75.5` 或 `\xA75.8` 的引用，均指向此处。

### 项目结构（每仓库）

在单个目标仓库上运行 **侦察密集型深度审计** 时，工作树使用五阶段擦除惯例，并结合 \xA75 中描述的合并产物。此布局是此 skill 使用的标准每仓库擦除树，并补充了 \xA75 任务目录树。

```
<root>/<vendor>-<repo>/
├── STATUS.md                      # running checklist (per-finding state, dissent notes, sibling-of-prior flags)
├── FINDINGS.md                    # primary output (narrative writeup, severity-sorted)
├── JUDGE.md                       # judge-pass results (see \xA75.7 Judge Tier Policy)
├── phase1/                        # recon
│   ├── personas.md
│   ├── trust-topology.md
│   ├── subsystem-inventory.md
│   ├── handler-index.md
│   ├── <surface>.md               # auth-providers, sql-injection-surface, plugin-surface, datasource-ssrf-surface, upload-surface, webhook-callback-surface, secrets-handling, …
│   ├── grep-sweeps/               # raw ripgrep output (one file per sweep)
│   └── PHASE1-COMPLETE.md         # gate: recon is sufficient to start deep-dives
├── phase2/                        # priority handler deep-dives p01..p15
│   ├── p01-<handler>.md
│   ├── …
│   ├── p15-<handler>.md
│   └── PHASE2-COMPLETE.md         # gate: top-15 handlers triaged
├── phase3/                        # broader sweep p16..p30 + sidequests
│   ├── p16-<handler>.md
│   ├── …
│   ├── p30-<handler>.md
│   ├── sidequests.md              # cross-cutting leads not tied to a single handler
│   ├── need-followup-resolutions.md
│   └── PHASE3-COMPLETE.md         # gate: breadth sweep exhausted; ready for synthesis
├── phase4/                        # synthesis
│   ├── bug-classes.md             # taxonomy of bug classes observed
│   ├── missed-bug-classes.md      # negative-space enumeration
│   ├── chains.md                  # multi-step chains / escalation paths
│   ├── amplifiers.md              # impact multipliers (tenant boundaries, public exposure, …)
│   └── PHASE4-COMPLETE.md         # gate: synthesis stable; ready for adversarial review
├── phase5/                        # adversarial review
│   ├── adversarial-review.md      # red-team disprove attempts
│   ├── triage-table.md            # final severity / confidence / disclosure-target table
│   └── PHASE5-COMPLETE.md         # gate: adversarial review done; ready for hardening + disclosure drafts
├── hardening/                     # per-finding hardening notes (fresh-HEAD re-verification + advisory delta)
│   ├── <TAG>-001.md               # one file per promoted finding
│   ├── …
│   └── SUMMARY.md                 # rollup of hardening status
└── sub-workers/                   # OPTIONAL: only when the lieutenant pattern is used (see \xA76 Pass 0)
    ├── LIEUTENANT.md              # per-area consolidator
    └── <subsystem>.md             # per-subsystem narrow-scope sub-worker outputs
```

**相变闸门**（触发进入下一阶段的条件）：

- `phase1` → `phase2`: `PHASE1-COMPLETE.md` 声明角色、信任拓扑、子系统库存和处理程序索引已就位，并为每个实质性不同的表面编写了表面特定文档。
- `phase2` → `phase3`: `PHASE2-COMPLETE.md` 声明 p01..p15 已在行锚深度下读取，要么被标记，要么明确清除。
- `phase3` → `phase4`: `PHASE3-COMPLETE.md` 声明广度扫面（p16..p30）加上支线任务已结束，并且每个 `need-followup-resolutions.md` 条目均已解决或停放。
- `phase4` → `phase5`: `PHASE4-COMPLETE.md` 声明错误类别、遗漏的错误类别、链和放大器是稳定的（在上次重新扫描中没有新的类别出现）。
- `phase5` → 手工移交: `PHASE5-COMPLETE.md` 声明存在对手审查以及分类表，并且每个晋升发现都有披露目标行。

`hardening/` 在新鲜的 HEAD 之后由 `phase5` 填充：每个 `<TAG>-NNN.md` 都会重新验证发现，并记录自 `phase1` 以来的任何建议差异。`SUMMARY.md` 汇总所有发现的强化状态。

此临时目录树与 \xA75 中的 任务-dir 目录树**兼容**：对于单仓库任务，`<root>/<vendor>-<repo>/` 就是任务目录；\xA75 的汇总产物（`findings.json`、`by-severity/`、`by-area/`、`findings/<id>/`、`_run-archive/`）会在 \xA79 期间与阶段目录树一同生成。

### 处置词汇表

`JUDGE.md`, `STATUS.md` 和每个发现的 `provenance.json` 中记录了裁决。这些是 \xA76 过程中使用的标准处置值。

#### Pass-1 判决 (行锚点)

- **CONFIRMED** — 代码与引用文件：行匹配所声称的模式。
- **DISPUTED** — 代码不匹配；在引用锚点处的说法有误。
- **NEEDS-CONTEXT** — 锚点存在，但需要额外上下文（调用者、类型、配置）才能做出裁决。触发 \xA77 上下文递归。
- **CONFIRMED-BY-DESIGN** — 代码匹配所声称的内容，但行为是文档中描述的默认 / 显式设计选择。技术上正确但不符合晋升条件。

#### Pass-2 判决 (供应商先前艺术)

- **REMAINS-NOVEL** — 没有先前的供应商警报 / CVE / GHSA 覆盖该发现。
- **SIBLING-OF-PRIOR** — 同一类别的先前 CVE/GHSA 存在，但针对不同的代码路径或参数。与父级警报捆绑披露（参见捆绑规则）而不是单独报告为一个错误。
- **DEMOTE-DUPLICATE** — 一个先前的 CVE/GHSA 已经涵盖了此发现。标记并降级。
- **DEMOTE-KBD** — 该候选项匹配已知的误报模式（false-positive）。标记并降级。

#### 最终裁决（在所有 floor pass 之后；显示在 JUDGE.md 最终表格中）

- **PROMOTED** — 发现符合披露条件。
- **DEMOTED-DUPLICATE** — 之前相同的技术；从披露合格集移除但保留在降级部分的报告中。
- **DEMOTED-KBD** — 已知不良检测；保留在报告中。
- **有争议** — 第1 次通过或第8 次通过成功反驳了该主张；保留在报告中。
- **撤回**——审计员在重新审查后撤回了发现（例如，后续阅读揭示该发现本身是错误的）。在报告中保留此条目，并附带撤回理由。

#### 严重性转移裁决

严重级别可能在 Judge 阶段发生变化。允许的变更**仅限降级**；Judge 阶段很少升级，且升级必须有新证据：

- `HIGH → MED`
- `HIGH → LOW`
- `MED → LOW`

严重级别降低是 Judge 的**正常结果**，并非错误。发生降级时：

- 记录发现的 `provenance.json[severity_shifts]` 数组中的变化。
- 在 `JUDGE.md` 的每个发现表格中渲染原始严重性和最终严重性（列：`severity_original`, `severity_final`）。
- 严重性下调不会移除该发现；它会在报告中保留其最终严重性。

#### SIBLING-OF-PRIOR 绑定规则

当 Pass 2 返回 SIBLING-OF-PRIOR 时:

- 将发现与父 CVE/GHSA 一起捆绑在披露中，而不是打开一个新的报告。
- 引用父 ID 在 `JUDGE.md` 中（列：`parent_cve_if_sibling`）。
- 在披露草稿（\xA712）中，将发现附加到现有公告，而不是生成新的公告。

---

## 覆盖率矩阵

本节将经典的 STRIDE / OWASP / OWASP-LLM 类别映射到 Pass 0 审计区域 \xA76 中，以便审查者可以验证类别的覆盖率而无需重新阅读整个 skill。

### 表 1 — STRIDE → Pass 0 区域

| STRIDE                       | Pass 0 区域                                              |
| ---------------------------- | --------------------------------------------------------- |
| **S** 伪造               | 身份验证、会话管理                        |
| **T** 篡改              | 反序列化、模板、路径处理、子进程    |
| **R** 否认责任            | 日志记录 / 可观察性 / 审计跟踪（参见 Fix 4）        |
| **I** 信息泄露 | 错误处理、密钥管理、日志记录               |
| **D** 拒绝服务      | 速率限制、解析器接口/正则表达式拒绝服务、资源消耗边界 |
| **E** 权限提升 | 授权、多租户                               |

### 表 2 — OWASP Top 10 (2021) → Pass 0 区域

| OWASP Top 10                                   | Pass 0 区域                                     |
| ---------------------------------------------- | ------------------------------------------------ |
| **A01** 破坏访问控制                  | 授权、多租户、路径处理、CSRF |
| **A02** 加密失败                 | 密码学、密钥管理                 |
| **A03** 注入                              | 存储 / SQL、模板、子进程、解析器    |
| **A04** 不安全的设计                        | IPC/RPC、速率限制                           |
| **A05** 安全配置错误              | IaC, 错误处理                              |
| **A06** 漏洞且过时的组件       | 供应链                                     |
| **A07** 身份验证与授权失败         | 身份验证、会话管理               |
| **A08** 软件和数据完整性故障     | 反序列化、CI/CD 管道                  |
| **A09** 安全日志记录与监控故障 | 日志记录 / 可观察性                          |
| **A10** 服务器端请求伪造            | SSRF                                             |

### 表3 — OWASP LLM 最终10 项 → Pass 0 区域

| OWASP LLM Top 10                    | Pass 0 区域                                          |
| ----------------------------------- | ---------------------------------------------------- |
| **LLM01** 提示词注入          | `llm-prompt-construction`                            |
| **LLM02** 不安全的输出处理  | `llm-output-handling`                                |
| **LLM03** 训练数据投毒   | `llm-training-data`                                  |
| **LLM04** 模型 DoS                 | `llm-consumption-bounds`                             |
| **LLM05** 供应链              | 供应链 (LLM 模型、数据集、嵌入)      |
| **LLM06** 敏感信息泄露 | `llm-output-handling`                                |
| **LLM07** 不安全的 plugin 设计    | `llm-agency-tool-permissions`                        |
| **LLM08** 过度代理          | `llm-agency-tool-permissions`                        |
| **LLM09** 过度依赖              | 治理（注意：代码级审计范围外） |
| **LLM10**模型盗窃               | 密钥管理，密码学                     |

### 表4 — 供应链启发式 → 可执行检查

| 启发式                  | 可执行检查                                                                                                                                                                                                      | 参考                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 最近发布的包 | `npm view <pkg> time --json \| jq '.modified, .[0]'` — 标记在过去7 天内发布的包                                                                                                                     | **供应链启发式**部分 |
| PyPI 发布日期检查    | `curl https://pypi.org/pypi/<pkg>/json \| jq '.releases \| to_entries \| sort_by(.value[0].upload_time) \| last'`                                                                                                     | **供应链启发式**部分 |
| 打字错误距离         | 与流行包名（如 lodash、react、express、requests、numpy、pandas 等）的 Levenshtein 距离≤2；使用`agrep`或`rg --no-ignore-case '<typo>'`检查`package-lock.json` / `yarn.lock` / `Pipfile.lock` | **供应链启发式**部分 |
| 安装后脚本 grep   | `rg -n '"preinstall"\|"install"\|"postinstall"' package.json`；对于 Python，请检查 `setup.py` 中的 `cmdclass={'install': ...}` 和 `pyproject.toml` 构建 hook                                                               | **供应链启发式**部分 |
| 维护者变更          | `npm view <pkg> maintainers`与先前已知集合对比；在 PyPI 中，检查发布历史记录以查看新上传者                                                                                                                    | **供应链启发式**部分 |

---

## 供应链启发式

具体的、可粘贴的命令用于第0 节\xA76 中的"供应链"第一阶段。每个启发式将一种定性的异味转化为审查员可以针对目标仓库运行的操作性检查。

### 最近发布的包

在过去的7 天内发布的包比长期稳定的包风险更高：突然的打字错误域名抢注、劫持和维护者账户接管经常通过突发的新发布显现出来。

```bash
npm view <pkg> time --json | jq '.modified, .[0]'
```

标记任何`modified`（或最新版本上传时间）在过去7 天内的包。要进行全面的锁定文件检查，可以遍历`jq -r '.packages | keys[]' package-lock.json`并逐个运行检查。

### PyPI 发布日期检查

PyPI 提供每个发布的上传时间。按发布时间排序并检查最近的一项。

```bash
curl https://pypi.org/pypi/<pkg>/json | jq '.releases | to_entries | sort_by(.value[0].upload_time) | last'
```

标记任何在过去7 天内上传的发布版本，并标记任何上传者与已建立的维护者集不同的发布版本（参见“维护者变更检查”部分）。

### 打字错误距离

打字错误克隆流行包名，Levenshtein 距离≤2。常见的打字错误目标有：

- JavaScript / npm：`lodash`、`react`、`express`、`axios`、`chalk`、`commander`、`debug`
- Python / PyPI：`requests`、`numpy`、`pandas`、`urllib3`、`setuptools`、`pip`
- Ruby / RubyGems：`rails`、`rake`、`bundler`
- Rust / crates.io：`serde`、`tokio`、`clap`

用于扫描锁定文件的单行命令列表：

```bash
# Fuzzy match with agrep (Levenshtein ≤ 2):
agrep -2 'lodash' package-lock.json
# Or, with ripgrep for exact typo candidates:
rg --no-ignore-case 'lodahs|lodsah|lodaash' package-lock.json yarn.lock Pipfile.lock
```

对系统性检查，计算每个锁定文件包名与目标列表中每一项之间的编辑距离；标记距离 ∈ {1, 2}。使用 `python-Levenshtein` 或标准库 `difflib.SequenceMatcher` 的简单 Python 脚本就足够了。

### 安装后脚本 grep

常见的恶意包模式是在安装钩子中执行代码。npm 和 Python 包格式都暴露了这些钩子。

**npm（`package.json`）：**

```bash
rg -n '"preinstall"|"install"|"postinstall"' package.json
```

还检查 `package-lock.json` 中的 `hasInstallScript: true` 条目，这是 npm 自身的一个信号，表示依赖项在安装时运行代码。

**Python：**

- `setup.py`: 寻找 `cmdclass={'install': ...}` 覆盖或自定义 `install` 子类，在安装时运行任意代码。
- `pyproject.toml`: 检查 `[build-system]` 构建钩子和任何指向项目本地模块的自定义 `build-backend`。

```bash
rg -n "cmdclass\s*=\s*\{" setup.py 2>/dev/null
rg -n "build-backend|build-hook" pyproject.toml 2>/dev/null
```

### 维护者变更检查

突然的维护者变更（特别是添加新上传者而不移除旧上传者，或者默默交换）是经典的供应链攻击前兆。

**npm：**

```bash
npm view <pkg> maintainers
```

与先前已知的维护者集进行比较（例如，在上次审查提交时的维护者，或包的 GitHub 仓库 `CODEOWNERS` 中的维护者）。任何新的维护者都值得检查其 npm 账户年龄和其他发布的包。

**PyPI：**

PyPI 不通过公共 JSON API 以相同的粒度暴露维护者，但发布历史记录确实揭示了上传者的更改。检查：

```bash
curl https://pypi.org/pypi/<pkg>/json | jq '.releases | to_entries | .[].value[0] | {version: .filename, upload_time: .upload_time, uploader: .uploader}'
```

标记任何 `uploader` 与已确立的上传者不同的发行版。

---

## 副提示词 (Pass 0)

指挥官通过调用带有此提示词体的 `Task` 来分发 Pass 0，其中绑定变量 (`area`, `target_path`, `commit_sha`, `mission_dir`, `jury_slot_hint`) 已替换。原封不动地将其复制到 `prompt` 参数中；不要让子工人从 `SKILL.md` 中朗读这一部分（它也获得了相同的 SKILL.md 上下文，但协调合同是显式传递提示词）。

> 你是一名安全副官，负责单一审计区域。你向一个运行异构多模型陪审团的深层安全审查指挥官报告。你正在运行于一个特定陪审团成员模型上（Claude Opus、GPT 或 Gemini）；其他区域上的副官可能在不同的模型上运行。你的种子列表将被下游过滤——假阳性是可以接受的，假阴性是不可以的。
>
> ### 输入
>
> - `area` — 你分配到的审计区域（例如，`authentication`, `deserialization`, `IaC`）。
> - `target_path` — 目标仓库在固定提交时的本地检出路径。
> - `commit_sha` — 固定的提交哈希值。
> - `mission_dir` — 你的输出路径：`<mission_dir>/_run-archive/lieutenants/<area>/LIEUTENANT.md`。
>
> ### 执行模式 — 嵌套-`Task` 检测和回退
>
> 当你作为覆盖多个审计领域的 **Phase-2 lieutenant orchestrator** 被派遣时（即 \xA76 Pass 0“何时使用 lieutenant 模式”中的 lieutenant 模式），应为每个审计领域启动一个 `Task`，并行运行子 worker。在执行任何跨领域枚举前，先检测当前所处的执行模式。
>
> **第0 步——检测**：检查您的工具列表中是否存在`Task`工具。这是一个一行检查：如果`Task`可调用，那么您处于嵌套调度模式；否则您处于回退模式。
>
> **嵌套调度模式（优先；`Task`可用）**：按照今天的文档进行操作：
>
> - 为每个审计区域启动一个`Task`任务，复杂度设置为`complexity: heavy`，每个任务运行相同的中队提示词，并绑定相应的变量（`area`, `target_path`, `commit_sha`, `mission_dir`, `jury_slot_hint`）。
> - 收集每个区域的`LIEUTENANT.{md,json}`输出结果，并自行进行综合分析或转交给专门的综合工作者。
>
> **回退模式（`Task`不可用）**：**不要默默地回退到在您自己的上下文窗口中逐个执行每个区域的子工作者提示词。** 窗口内执行会压缩每个区域的深度为骨架输出（没有`file:LINENO`锚点，没有5-10 行代码引用，`needs_context: true`到处都是），并且已被证明会丢失实际发现（见下文理由）。相反：
>
> 1. 停止。不要开始在所有区域内逐个进行候选枚举。
> 2. 发出一个**结构化转交**回给调度器并退出。转交的内容（写入`<mission_dir>/_run-archive/lieutenants/HANDOFF.json`，并在您的 Markdown 回复中回显）必须包含每个区域的记录，其中：
>    - `area` — 短的规范名称（例如，`indices-mapping`）。
>    - `target_path` — 本地锁定提交的检出路径。
>    - `commit_sha` — 固定的提交哈希值。
>    - `code_roots` — 要枚举的子路径列表（从 `areas.json` 复制）。
>    - `must_cover` — 必须出现在子工人的种子输出中的发现类 ID、文件路径或端点 ID 列表（从 `areas.json` 和任何先前运行的覆盖矩阵中复制）。
>    - `focus` — 该区域范围的一行描述（从 `lieutenant_focus` 中的 `areas.json` 复制）。
>    - `target_output_size` — 每个区域推荐的大致下限（例如，`>= 15 candidates, >= 1200 words in LIEUTENANT.md`, 加上匹配的 `LIEUTENANT.json` 辅助文件）。
>    - `jury_slot_hint` — 使用的陪审员家族（从 `areas.json` 复制）。
> 3. 指挥者（拥有 `Task`）然后根据 \xA75.4 节中的 `BATCH_SIZE_LIEUTENANTS` 限制分派 N 个子工人的任务。如果 N > 限制，则按顺序批次处理。每个子工人在没有 `Task` 的情况下运行这个领队提示词，但范围足够小以使内联上下文适合。
> 4. 子工人输出写入 `_run-archive/lieutenants/<area>/LIEUTENANT.{md,json}` 后，指挥者要么继续进行合成，要么将任务转交给专门的合成工人的。
>
> **理由。** v2 elasticsearch 审计（参见 `deep-audits/elastic-elasticsearch-v2/COMPARISON.md` \xA75 和 `phase2/PHASE2-COMPLETE.md` \xA7A1）实证验证了这种失败模式：当 Phase-2 副手在单个上下文窗口中静默内联运行 10-15 个分区提示词时，各分区的分析深度被压缩成骨架输出，四个区域（`indices-mapping`、`snapshot-repo`、`scripting-painless`、`SQL/ES|QL/EQL`）合计遗漏约 22 个 v1 发现（其中 5 个 HIGH）。 嵌套的`Task`路径仍然是首选默认值；此备用方案是一个附加的安全网，确保副官模式在运行时工具集变化下保持稳健。
>
> 如果你被派遣处理单一区域（\xA76 第0 步第4 阶段的扁平化按区域分发），忽略本节并继续进行**强制执行**——你没有子工作者可以启动。
>
> ### 强制执行
>
> 应当**尽可能全面**。orchestrator 会针对每个候选项运行八个下游筛选器（行锚点验证、供应商先例、深度先例、数据流 + 可达性、利用构造、补丁构造、负空间分析、对抗性红队）。此阶段的误报会在后续被过滤；漏报则无法恢复。因此应倾向于列出候选项。
>
> ### 程序
>
> 1. 列出目标仓库中与`<area>`相关的每一个文件。使用`Glob`和`Grep`积极地进行搜索。除非用户在范围中排除了供应商代码，否则不要跳过供应商代码。也不要跳过测试——易受攻击的测试示例和仅用于测试的身份验证绕过是真实发现。
> 2. 对于每个候选文件，捕获以下内容：
>    - **id** — 占位符格式 `<area>-<seq>`；协调者将进行规范化处理。
>    - **file_line** — `path/to/file:LINENO`在固定提交时的路径。
>    - **code_quote** — 引用行周围的5-10 行代码，原封不动地复制粘贴。
>    - **proposed_severity** — 初始猜测：`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`；偏向于不低估风险。
>    - **proposed_confidence** — `HIGH`、`MEDIUM`、`LOW`。副手会尽量多报；置信度为 LOW 也没问题。
>    - **trigger** — 一段话：什么条件会触发此问题？
>    - **impact** — 一段话：如果触发了会发生什么？
>    - **suspected_class** — 短标签，例如 `sqli`、`path-traversal`、`prototype-pollution`、`weak-jwt-alg`、`missing-authz`、`ssrf`、`redos`。
>    - **owasp_mapping** — 可选：单个 STRIDE 字母 (`S`/`T`/`R`/`I`/`D`/`E`)，OWASP Top 10 编码 (`A01`–`A10`) 或 OWASP LLM Top 10 编码 (`LLM01`–`LLM10`)。示例：`"owasp_mapping": "A03"`。如果不清楚可以省略此字段；下游消费者会将其视为可选项，以保持向后兼容性。
>    - **prior_art_hint** — 可选：你怀疑这匹配的任何 CVE / CWE / 类别标识符。下游 Pass 2/3 将进行验证。
>    - **needs_context** — 布尔值；如果不能在不阅读调用者、类型信息或运行时上下文的情况下确认，则设置为 true。调度器将通过 \xA77 递归处理。
> 3. 特别积极地考虑：
>    - 隐式的信任边界（例如，“内部”路由实际上可以通过代理外部可达）。
>    - 部分应用的清理程序（例如，仅在一条路径上应用而不在另一条路径上应用）。
>    - 类型细化或仅在运行时有效的不变量，类型系统不强制执行。
>    - 依赖于配置的行为（例如，在生产环境中禁用了检查的一个标志）。
>    - 任何看起来像是中途重构的内容（一个分支更新了，但兄弟分支没有）.
> 4. 对于“宽泛”的区域，如授权或 API 接口，请勿限制候选数量。列出所有没有经过验证的授权检查的端点。协调器会去重。
> 5. 生成 `LIEUTENANT.md`，每个候选人一个 Markdown 部分。同时在相同目录下发出一个 JSON 辅助文件 `LIEUTENANT.json`（包含候选记录数组），协调器会解析此文件以进行 ID 分配。
>
> ### 需要避免的反模式
>
> - 不要预先按新颖性筛选。“这只是 CVE-XXXX”不是跳过的理由；编排器会在 Pass 2 处理既有研究标记。
> - 请勿将多个独立的问题压缩为一个发现。每个候选人一个问题。变体是分开的。
> - 请勿浏览文件。打开每个引用的文件，阅读周围的代码，确认文件:行号是真实的。
> - 请勿引用行范围；引用单个锚定行并引用其周围5-10 行的内容。
>
> ### 输出格式
>
> Markdown 部分的形式：
>
> ````
> ## <area>-001 — <short title>
>
> - **File:line:** `path/to/file:42`
> - **Proposed severity:** HIGH
> - **Proposed confidence:** MEDIUM
> - **Suspected class:** sqli
> - **OWASP mapping:** A03            <!-- optional: STRIDE letter, A01-A10, or LLM01-LLM10 -->
> - **Needs context:** false
> - **Prior art hint:** CWE-89; possible duplicate of GHSA-xxxx-xxxx (unverified)
>
> ### Code
> ```<lang>
> <5-10 line quote>
> ````
>
> ### 触发条件
>
> <one paragraph>
>
> ### 影响
>
> <one paragraph>
> ```
>
> 完成后，将 `LIEUTENANT.md` 和 `LIEUTENANT.json` 的路径返回给 orchestrator。orchestrator 会收集结果、去重并分配规范 ID。
>
> #### 备用模式输出（无 `Task` 的交接）
>
> 如果你通过上方**执行模式——嵌套 `Task` 检测与备用路径**中的备用分支提前退出，请勿输出各候选项部分。只输出交接清单，以便 orchestrator 直接分派子 worker：
>
> - 按以下结构写入 `<mission_dir>/_run-archive/lieutenants/HANDOFF.json`：
>
> ```json
> {
>   "mode": "no-task-fallback",
>   "reason": "Task tool not present in lieutenant toolset",
>   "areas": [
>     {
>       "area": "indices-mapping",
>       "target_path": "/path/to/repo",
>       "commit_sha": "<sha>",
>       "code_roots": ["server/src/main/java/org/elasticsearch/index/mapper/"],
>       "focus": "Mapping parser surface, field-type coercion, dynamic templates.",
>       "must_cover": ["CVE-2024-xxxx", "server/.../MapperService.java"],
>       "target_output_size": ">=15 candidates, >=1200 words in LIEUTENANT.md plus matching LIEUTENANT.json",
>       "jury_slot_hint": "opus"
>     }
>   ]
> }
> ```
>
> - 在向协调者回复的 Markdown 中，包含以下内容：(a) `HANDOFF.json` 的绝对路径，(b) `areas[]` 中区域的数量，和 (c) 你以备用模式退出，因此协调者不要将空的 `LIEUTENANT.md` 错误地视为成功运行。
> - 在备用模式下，不要在任何 `LIEUTENANT.md` 目录中编写 `LIEUTENANT.json` / `<area>/` — 这些输出是由协调者派遣的子工件生成的，而不是由你生成的。

---

## 法官底层提示词（通过 1-3 关）

这是 Judge 的**强制基础层**。来自 Pass 0 的每个候选 finding 都依次经过这三个 Pass。Pass 4、5、8（升级层）位于下文的 **Judge 升级提示词（Pass 4、5、8）** 部分，并且仅在 \xA75.7 记录的触发条件满足时运行。

每个关卡将并行派遣给三个陪审员（参见 \xA73 中的陪审团组成）。裁决独立收集；协调者根据 \xA73 的规则合成结果并在 \xA74 中运行平局打破机制。在通过一个关卡时，不要与其他陪审员沟通 — 独立形成你的裁决。将每个 `Task.prompt` 参数中相关的关节选原文引用。

### 关 1 — 行锚验证

> 你是三个法官之一，正在评判来自第 0 关（副官枚举）的候选发现。其他两个模型也在并行评判同一发现。你的裁决独立记录；协调者根据 \xA73 中的规定合成结果（关键问题需要一致同意，高/中/低问题需要多数票）。
>
> #### 输入
>
> - `finding_record` — 候选发现 JSON（id、标题、文件行号、代码引用、提议的严重性等）。
> - `target_path` — 固定提交时的本地检出目录。
> - `commit_sha` — 固定的提交哈希值。
>
> #### 目标
>
> 确认（或反驳）所引用的文件：行号在固定提交的实际内容是否包含声称的模式。此步骤不判断严重性、可到达性或利用性——这些是后续步骤。此步骤仅判断：
>
> > "文件:行号处的代码与发现声明的一致吗？"
>
> #### 流程
>
> 1. 在固定提交（读取 SHA，而非 HEAD）中打开所引用的文件。
> 2. 以引文形式在你的裁决中中心化地包含5-10 行围绕所引用行的内容。
> 3. 将你引用的内容与副官的`code_quote`进行比较。它们应该匹配。如果不匹配，这将是一个强烈的争执信号（DISPUTED）。
> 4. 独立评估声称的模式是否确实存在于所引用的行中。
> 5. 分类（参见**方法论参考**部分上方的裁决词汇表）：
>    - `CONFIRMED` — 文件:行号处的代码与声明一致，模式存在。
>    - `DISPUTED` — 文件:行号处的代码不匹配。模式不存在，该行错误，或副官误读。
>    - `NEEDS-CONTEXT` — 该文件:行号存在，代码看起来相关性较大，但没有上下文（调用者、类型信息、配置）无法确认。指挥官将通过\xA77 进行递归。
>    - `CONFIRMED-BY-DESIGN` — 代码在文件：行号处与声明相符，但行为是已记录的默认值/明确的设计选择。技术上正确但不符合晋升条件。
>
> #### 输出（一个 JSON 对象返回给调度器）
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model name and version>",
>   "verdict": "CONFIRMED" | "DISPUTED" | "NEEDS-CONTEXT" | "CONFIRMED-BY-DESIGN",
>   "evidence_quote": "<5-10 lines from the file>",
>   "rationale": "<2-4 sentences explaining the verdict>",
>   "context_needed": ["<list of files/symbols you would need if NEEDS-CONTEXT>"]
> }
> ```
>
> #### 硬性规则
>
> - 不要推测可利用性。那是 Pass 5。
> - 不要搜索先前的 CVE。那是 Pass 2。
> - 不要跟踪数据流。那是 Pass 4。
> - 专注于："引用的代码在引用的行号处，并且是否与声明相符？"
> - 如果副官的 `code_quote` 已被编辑或改写而不是复制粘贴：标记为 DISPUTED 并附上理由。
> - 如果指定提交中不存在该文件：标记为 DISPUTED。
> - 如果行号超出 EOF：标记为 DISPUTED。

### Pass 2 — 供应商先前技术筛选

> 你是三位陪审员之一。另外两位也在并行运行相同的提示词。裁决是独立的。
>
> #### 目标
>
> 确定此发现（或其近亲）是否已被供应商披露或在公共咨询中有所提及。输出是一个标签，而不是删除操作。即使一个发现重复了一个已知的 CVE，协调者仍需将其保留在报告中——重复的真实漏洞仍然是真实的问题。你是在减少新颖性评分，而不是正确性评分。
>
> #### 输入
>
> - `finding_record` — 包含 file_line、code_quote、suspected_class、proposed_severity 的完整发现 JSON。
> - `target_repo` — 仓库 URL 或本地路径。
> - `commit_sha` — 固定的提交哈希值。
>
> #### 流程
>
> 在以下来源中运行约25-30 个查询。如果某个来源对你不可用，请记录缺口；不要默默地跳过它。
>
> 1. **供应商安全页面**。查找项目的官方安全公告页面（例如，GitHub 安全标签、供应商的 security.txt、项目文档站点上的“安全”页面）。
> 2. **GHSA 数据库** (GitHub Security Advisories) 用于该项目及其直接依赖项中的任何发现。
> 3. **NVD / CVE 数据库** 用于项目名称和 CWE 类别。
> 4. **MITRE CWE 编目** 用于疑似类别。
> 5. **HackerOne, Bugcrowd, Intigriti 公开披露** 可通过其公共报告端点进行搜索。
> 6. **最近的提交记录（约12 个月）** 涉及到引用文件或符号。同一路径上的近期“修复”提交是强有力的先前艺术证据。
> 7. **最近的标签 / 发行说明** 项目。
> 8. **供应商变更日志 / NEWS 文件**。
> 9. **同族类别的其他库的安全公告**。（例如，对于 YAML 反序列化问题：PyYAML, ruamel, snakeyaml, gopkg.in/yaml.v2 安全公告。）
> 10. **公共错误跟踪系统**（问题、邮件列表）针对疑似类别的代码路径。
>
> #### 分类
>
> - `REMAINS-NOVEL` — 详尽搜索未返回相关先前艺术。
> - `DEMOTE-DUPLICATE` — 确切的先前 CVE / GHSA / 安全公告已存在于此代码路径中。**标记为先前标识符；不要移除发现结果。**
> - `SIBLING-OF-PRIOR` — 前置 CVE/GHSA 存在于同一类别，但位于不同的代码路径或不同版本范围内。标记并保留发现结果。
> - `DEMOTE-KBD` — 已知不良检测：副官的模式在该代码库或类中是一个著名的误报匹配器（例如，SAST 标记 `eval` 为类型检查辅助函数）。标记为 DISPUTED 并附带理由。
>
> #### 输出
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model+version>",
>   "verdict": "REMAINS-NOVEL" | "DEMOTE-DUPLICATE" | "SIBLING-OF-PRIOR" | "DEMOTE-KBD",
>   "prior_art": [
>     {"type": "GHSA" | "CVE" | "vendor-advisory" | "h1-disclosure" | "commit" | "blog" | "paper",
>      "id": "GHSA-xxxx-xxxx-xxxx" | "CVE-2023-NNNN" | "<URL or commit SHA>",
>      "url": "<canonical link>",
>      "summary": "<one sentence>",
>      "match_strength": "EXACT" | "STRONG" | "WEAK"}
>   ],
>   "queries_run": <int>,
>   "rationale": "<2-4 sentences>"
> }
> ```
>
> #### 硬性规则
>
> - 至少运行 25 次查询。如果运行次数不足，请说明原因。
> - 不要仅仅依赖副官的 `prior_art_hint` — 重新验证它。副官会过度包含提示信息。
> - 区分‘同一个错误’与‘相关错误’。`DEMOTE-DUPLICATE` 需要近乎完全匹配（相同的代码路径，相同的类）。`SIBLING-OF-PRIOR` 是指相关的但不同的错误。
> - 一个发现可以被降级为重复项但仍可由协调者提升 — 协调者保留真实错误的副本。你是在标记，而不是删除。
> - 网络操作是只读的。你可以获取建议页面、GHSA JSON、NVD JSON 和公共博客文章。你不能注册、提交、评论或传输任何内容。

### Pass 3 — 深度先前艺术筛选

> 你是三位陪审员之一。另外两位也在并行运行相同的提示词。裁决是独立的。
>
> #### 目标
>
> 构建研究面包屑。这种 类 威胁在文献中出现在哪里？存在哪些变体？过去的补丁维护者从相关的 CVE 中学到了什么？这一轮会丰富发现的内容 — 但这并不提升或降级它。
>
> #### 输入
>
> - `finding_record` — 完整的发现 JSON.
> - `pass2_output` — Pass 2 的供应商先驱标记（以便您可以在不重复努力的情况下建立在此基础上）。
>
> #### 流程
>
> 运行约80-150 个查询：
>
> 1. **其他库/语言中的同级类 CVE。** 如果发现是“反序列化工具链在 pickle 中”，则搜索 Java (XStream, Jackson), .NET (BinaryFormatter, ObjectStateFormatter), Ruby (Marshal, ERB), JS (node-serialize, Function 构造函数), Go (gob), PHP (unserialize)。
> 2. **学术论文。** Google Scholar, arXiv, USENIX Security, CCS, NDSS, IEEE S&P, ACM CCS 会议记录。
> 3. **会议演讲。** Black Hat, DEF CON, OWASP Global, RSA, Chaos Communication Congress。
> 4. **安全博客文章。** 寻找技术帖子（不是营销）来自 Project Zero, GitHub Security Lab, Google Bug Hunters, JFrog Security Research, Sonar Source, Snyk, Semgrep, Trail of Bits, NCC Group, Doyensec, Include Security, Latacora, Cure53。
> 5. **语言/框架深入研究。** 维护者撰写的后验分析，反思，更改日志中讨论了为什么添加了一项防御措施。
> 6. **CWE 目录页面** — 阅读它；捕获相关/父/子 CWEs。
> 7. **OWASP Top 10 / OWASP LLM Top 10 / OWASP API Top 10** 映射以获取上下文（如果相关）。
> 8. **参考实现** — 防御的（例如，相关协议的 RFC 文本，语言标准文档）。
>
> #### 分类
>
> 此通过步骤生成一个研究链接块，而不是判决。输出结构：
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model+version>",
>   "prior_art_deep": [
>     {
>       "type": "academic_paper" | "blog" | "talk" | "rfc" | "spec" | "cwe" | "sibling_cve" | "framework_doc",
>       "title": "<title>",
>       "authors": "<authors or org>",
>       "venue": "<USENIX 2021 | Black Hat USA 2019 | Project Zero blog | ...>",
>       "url": "<canonical link>",
>       "summary": "<2-3 sentences on what's relevant>",
>       "applicability": "DIRECT" | "ANALOGOUS" | "BACKGROUND"
>     }
>   ],
>   "research_synthesis": "<one paragraph: what does the literature say about this class, what defenses are known, what variants are common>",
>   "queries_run": <int>
> }
> ```
>
> #### 硬性规则
>
> - 至少运行80 次查询。非平凡发现时目标为150 次。
> - 不要将维基百科作为主要引用来源；仅将其用作导航到权威来源的起点。
> - 区分原始资料（CVE 页面、公告、最初披露、RFC 文本、规范文本）与次要资料（博客、演讲）。同时引用两者。
> - 如果一个类别被广泛研究（例如，SQL 注入、XSS、原型污染），则优先使用经典参考文献（Stuttard 的教科书、OWASP 页面、Halfond 等人综述）加上5-10 个现代变体。
> - 网络操作为只读。不允许注册、发布或提交内容。

---

## 审查升级提示词（通过4, 5, 8）

法官的**升级层级**。仅在 \xA75.7 中记录的触发器上触发；不以晋升为条件。Pass 4（数据流/可达性）和 Pass 5（利用构建）每项都在两个阶段运行（跟踪器/构造器 + 审核员）；Pass 8（红队反驳）在单个对手审核员上运行。

强制最低标准（通过1, 2, 3）位于上方的**法官最低提示词（通过1-3）**部分中。副官枚举（通过0）位于上方的**副官提示词（通过0）**部分中。

每次通过分发均受第 \xA73 和 \xA74 条中的评委会/决选规则约束；独立作出裁决，勿与其他陪审员沟通。将相关 Pass 子节的内容原封不动地引用到每个 `Task.prompt` 参数中.

### 通过4 — 数据流 & 可达性

> 你是 3 人陪审团的一员。编排器会针对每项发现分两个阶段分派 Pass 4：
>
> - **阶段 A（一名陪审员，“追踪者”）:** 进行详细的污点跟踪，并编写 `findings/<finding-id>/dataflow.md`。
> - **阶段 B（另外两名陪审员，“审查者”）:** 独立阅读跟踪结果，对其进行批判性评估，并判断可到达性。
>
> 指挥者会告诉你扮演的角色 (`role: tracer` 或 `role: reviewer`)。
>
> #### 阶段 A — 追踪者角色
>
> ##### 目标
>
> 为发现生成完整的正向和反向污点跟踪。列出每一个转换，每一个净化器，每一个分支，每一个类型细化。不要跳过步骤。
>
> ##### 程序
>
> 1. **源识别。** 不可信的来源是什么？可能的来源：HTTP 请求体、URL 参数、头部信息、cookies、文件上传、环境变量、文件内容、消息队列负载、RPC 参数、IPC 消息、websocket 帧、多租户表中的数据库行、OAuth 令牌声明（如果未验证签名）、文件名、归档条目、下游服务响应。
> 2. **汇点识别。** 漏洞的汇点是什么？示例：SQL 查询字符串、shell 命令、文件路径、eval/exec 输入、HTML 渲染到页面、JSON 反序列化器输入、正则表达式编译器、DNS 查找、外部 HTTP 请求、日志行。
> 3. **正向跟踪。** 从每个源开始，追踪值如何流向汇点：
>    - 每一次赋值。
>    - 每个函数调用（记录两个方向：参数入和返回出）。
>    - 每个条件分支（条件是否缩小了类型？是否过滤了值？）。
>    - 每个清理器（它移除了什么，留下了什么？）。
>    - 每个编码器/解码器（它产生了什么，逆操作是什么？）。
>    - 路径中的每个框架挂钩（中间件、装饰器、拦截器）.
> 4. **反向追踪。** 从接收点开始，列出每一步的调用者。对于每一个调用者，列出它的调用者。继续直到你遇到以下情况之一：(a) 可以从不受信任输入到达的入口点，或 (b) 阻止不受信任输入的屏障（认证检查、白名单、内部专用断言、签名载荷检查）.
> 5. **清理器审计。** 对于每个遇到的清理器，问：它对这个接收点来说正确吗？一个用于 HTML 的转义对于 SQL 是错误的。一个用于 shell 单引号的转义对于 shell 双引号也是错误的。一个去除 `..` 的清理器在许多文件系统中可以通过 `....//` 被绕过.
> 6. **配置/特性标记审计。** 路径中的任何部分是否被某个标志控制？默认情况下该标志是否启用？在任何常见部署中该标志是否启用？
>
> ##### 输出（阶段 A）
>
> 编写 `findings/<finding-id>/dataflow.md`（协调者会在你开始前使用 `mkdir -p findings/<finding-id>/` 创建每个发现的文件夹）：
>
> ```
> # Dataflow trace — <finding id>: <title>
>
> ## Source candidates
> - <source 1: file:line, type, where it enters the system>
> - ...
>
> ## Sink
> - <sink: file:line, what makes it dangerous, what input shape would trigger>
>
> ## Forward trace
> 1. <source 1> -> <function A>:<line> [transform: <name>]
> 2. <function A> -> <function B>:<line> [no transform]
> 3. ...
> N. -> <sink>:<line>
>
> ## Sanitizers encountered
> - <sanitizer 1>: at <file:line>; removes <X>; bypassable if <Y>.
> - ...
>
> ## Backward trace from sink
> - <sink> caller: <file:line>
> - <caller's caller>: <file:line>
> - ...
> - Entry point: <route definition / handler registration / event subscription>
> - Reachability: <REACHABLE-FROM-UNTRUSTED | REACHABLE-INTERNAL-ONLY | UNREACHABLE>
>
> ## Configuration & flags
> - <flag X>: <default state, where set>
> - ...
>
> ## Open questions for reviewers
> - <bullet list of points where the tracer is uncertain>
> ```
>
> 然后返回给协调者的总结 JSON：
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model+version>",
>   "role": "tracer",
>   "tracer_verdict": "REACHABLE-FROM-UNTRUSTED" | "REACHABLE-INTERNAL-ONLY" | "UNREACHABLE",
>   "trace_path": "findings/<finding-id>/dataflow.md",
>   "open_questions": ["..."]
> }
> ```
>
> #### B 阶段 — 审核员角色
>
> ##### 目标
>
> 独立地批判追踪器的跟踪。不要重新做它；阅读它，遵循引用，并挑战它。
>
> ##### 程序
>
> 1. 打开 `findings/<finding-id>/dataflow.md`。
> 2. 对于正向跟踪中的每一步，打开被引用的文件并验证该步骤。如果在某一步声称有清理器（sanitizer），则打开它并验证它实际上做了什么。
> 3. 对于反向跟踪，跟随调用者并验证入口点。
> 4. 形成你独立的裁决意见关于可达性。
>
> ##### 输出 (阶段 B)
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model+version>",
>   "role": "reviewer",
>   "verdict": "REACHABLE-FROM-UNTRUSTED" | "REACHABLE-INTERNAL-ONLY" | "UNREACHABLE",
>   "agreements": ["<list of trace steps you confirmed>"],
>   "disagreements": ["<list of trace steps you challenge, with rationale>"],
>   "missed_paths": ["<paths the tracer missed, if any>"],
>   "rationale": "<2-4 sentences>"
> }
> ```
>
> #### 硬规则（两个阶段）
>
> - 不要信任追踪器声称而未经验证的引用。审查者的整个目的是独立挑战。
> - “仅内部可达”的裁决需要一个干净的理由，即没有任何不受信输入可以到达终点。怀疑某个内部 API 通过代理或框架默认暴露也是足够的理由将其推断为“从不受信输入可达”。
> - “不可达”的裁决需要最强的证据：死代码、被永远为假的标志所屏蔽、从未注册、在永远不会路由的处理器后面。
> - 如果跟踪需要运行时行为来确认（例如，依赖于配置文件的内容，或依赖于数据库状态）：标记为 `NEEDS-CONTEXT` 并且编排器运行 \xA77 递归。

### 通过第5 轮 — 利用构建

> 类似于第4 轮，这一轮也有两个阶段：
>
> - **阶段 A（构造器）**：一名陪审员构建利用（或尝试构建但失败）。
> - **阶段 B（审查者）**：另外两名陪审员独立判断该利用是否有效。
>
> 编排器会告诉你的角色。
>
> #### 阶段 A — 构造器角色
>
> ##### 目标
>
> 生成一个最小化的利用（或草图），以展示发现的问题。如果原则上无法构建任何利用，声明为 `THEORETICAL` 并附带理由。
>
> ##### 程序
>
> 1. 从第4 轮的数据流跟踪中，识别最简单的源点到终点的路径。
> 2. 确定触发漏洞所需的最小输入形状.
> 3. 指定先决条件：
>    - 网络位置要求（外部攻击者、认证用户、横向攻击者、供应链攻击者、本地攻击者、物理攻击者）。
>    - 攻击者持有的权限（无权限、低权限用户、管理员等）。
>    - 状态假设（在漏洞触发前系统必须满足的条件）。
> 4. 构造有效负载：
>    - 精确的字节/字符串/URL/请求序列。
>    - 对于 Web: 包括头部和主体的 HTTP 请求行。
>    - 对于 RPC: 方法名 + 参数。
>    - 对于文件基础: 文件名、存档结构、文件内容。
>    - 对于配置: 环境变量、文件路径。
> 5. 指定可观察结果：
>    - 攻击者在成功时会看到什么？（响应内容、副作用、时间信号、离线信号、读取的文件内容、执行的命令）。
> 6. 自动化脚本（可选）：一页的 `curl` 脚本、Python 摘要或 Burp 请求。
> 7. 确定现实中的攻击者画像（脚本小子、机会主义的大规模扫描器、针对性攻击者、国家级攻击者、内部人员）。
>
> ##### 输出
>
> 编写 `findings/<finding-id>/exploit.md`:
>
> ```
> # Exploit sketch — <finding id>: <title>
>
> ## Preconditions
> - Network position: <external | auth-user | etc.>
> - Privileges: <none | low | admin>
> - State: <what must be true>
>
> ## Input
> <exact payload, code-fenced>
>
> ## Walkthrough
> <step-by-step: 1) attacker sends X; 2) server does Y; 3) sink fires Z>
>
> ## Observable on success
> <what the attacker sees>
>
> ## Realistic attacker profile
> <which class of attacker>
>
> ## Verdict
> EXPLOITABLE | THEORETICAL | UNEXPLOITABLE
>
> ## Limitations / failure modes
> <bullet list>
> ```
>
> 然后返回到协调者：
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model+version>",
>   "role": "constructor",
>   "constructor_verdict": "EXPLOITABLE" | "THEORETICAL" | "UNEXPLOITABLE",
>   "exploit_path": "findings/<finding-id>/exploit.md",
>   "preconditions_count": <int>
> }
> ```
>
> #### B 阶段 — 审核员角色
>
> ##### 目标
>
> 独立判断构造者的利用是否合理。在脑海中复现逻辑；不要实际运行该利用（PoC 执行仅在 \xA710，由用户授权）。
>
> ##### 程序
>
> 1. 读取 `findings/<finding-id>/exploit.md`。
> 2. 对于每个前提条件，问：这是否是现实上可实现的？需要攻击者首先猜测一个 256 位秘密才能触发的利用是不可行的。
> 3. 对于负载，问：这是否会实际触发漏洞点？逐字节地走一遍它。
> 4. 对于可观察的内容，询问：这是真实的观测还是想象中的？
> 5. 独立裁决。
>
> ##### 输出
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model+version>",
>   "role": "reviewer",
>   "verdict": "EXPLOITABLE" | "THEORETICAL" | "UNEXPLOITABLE",
>   "agreements": ["..."],
>   "disagreements": ["..."],
>   "missing_preconditions": ["..."],
>   "rationale": "<2-4 sentences>"
> }
> ```
>
> #### 硬性规则
>
> - 请勿实际执行漏洞利用。仅生成。
> - `THEORETICAL` 裁决意味着漏洞是真实的，但无法构建出现实可行的利用方法。例如：需要进行10^9 次测量的时间分析或需要控制我们不控制内存的操作符链。
> - `UNEXPLOITABLE` 裁决意味着在更仔细检查后发现该漏洞实际上是不存在的（例如，一个清理器实际上阻止了它，内部不变量防止了不良形态等）。这实际上降低了发现的重要性。
> - 区分“复杂但可能”（仍然可利用）与“在不现实假设下才可能”（理论上的）。

### 通过8 — 敌对红队推翻

> 这是最终的审查阶段。你不是陪审团成员。你是敌对的审查者。你的任务是推翻发现。
>
> 策划者故意让你在一个与(a)提出发现的副官和(b)Pass 4 追踪器不同的模型家族中运行。这旨在击败自我强化。
>
> #### 目标
>
> ["> \"证明这一发现是错误的。\"]
>
> 找出任何理由说明此发现实际上不可利用、实际上无法到达或实际上不是漏洞。要敌对。要怀疑论。寻找：
>
> - 其他路径中我们遗漏的清理工具.
> - 排除不良输入形状的类型约束.
> - 运行时不变量，防止出现不良状态.
> - 配置/部署上下文，禁用该路径。
> - 框架默认设置，阻止攻击.
> - 隐式的访问控制（代理、网络 ACL、mTLS、IP 白名单）审计上下文未涵盖的.
> - 外部于审核代码的缓解措施，关闭影响.
> - 代码误读（副手误解了类型、跟踪或 API）。
>
> #### 输入
>
> 你将收到完整的发现记录：
>
> - 文件:行和代码引用。
> - 通过1-3 个裁决并提供先例。
> - 通过第4 步的数据流跟踪。
> - 通过第5 步的利用草图。
> - 到日期的来源 JSON。
>
> #### 流程
>
> 1. 阅读每个输入。要缓慢。不要让步。
> 2. 构建你能想到的最强反驳。尝试多个角度：
>    - 利用的前提条件是不现实的。
>    - 数据流跟踪在第 N 行跳过了一个净化器。
>    - 处理程序是在网络配置时间注册到内部仅限监听器上的。
>    - "不可信"的来源实际上是 mTLS 认证过的，并且只暴露给内部服务。
>    - 框架自动应用了一个防御措施，而副官忽略了这一点。
>    - 利用试图利用一个被解析器上游拒绝的载荷形状。
>    - 实际上，"缺失"的检查确实存在于未提及的基本类、装饰器或中间件中。
> 3. 如果你的反驳需要运行时证据，请上报给指挥者：标记你的裁决为 `RED-TEAM-INCONCLUSIVE-NEEDS-RUNTIME` 并请求 \xA74 第 2 轮实证决胜局。
> 4. 如果你无法找到反驳：说明情况。不要捏造事实。该发现仍然有效。
>
> #### 输出
>
> ```json
> {
>   "finding_id": "auth-001",
>   "model": "<your model+version, MUST differ from proposer and tracer>",
>   "verdict": "RED-TEAM-DISPROVED" | "RED-TEAM-INCONCLUSIVE" | "RED-TEAM-INCONCLUSIVE-NEEDS-RUNTIME" | "RED-TEAM-SURVIVED",
>   "disproof_attempted": [
>     {"angle": "sanitizer-elsewhere", "details": "..."},
>     {"angle": "internal-only-handler", "details": "..."},
>     {"angle": "framework-default", "details": "..."}
>   ],
>   "strongest_doubt": "<your single best argument the finding might be wrong, even if it doesn't fully disprove>",
>   "rationale": "<2-4 sentences>"
> }
> ```
>
> #### 结果语义
>
> - `RED-TEAM-DISPROVED` — 你找到了一个干净且可辩护的理由来证明该发现是错误的。该发现降级为 `DISPUTED-AFTER-ADVERSARIAL`，仍保留在报告中（在争议部分），并附上你的理由。
> - `RED-TEAM-INCONCLUSIVE` — 你提出了真正的疑虑但没有完全反驳。裁决保持不变，但信心降低。疑虑被记录下来。
> - `RED-TEAM-INCONCLUSIVE-NEEDS-RUNTIME` — 你的反驳需要运行时证据而无法静态获取。指挥者将运行 \xA74 第 2 轮实证决胜局。
> - `RED-TEAM-SURVIVED` — 你尽力了但未能反驳。该发现获得了最高的信心等级。
>
> #### 硬性规则
>
> - 不要与原始提案者或追踪者沟通。你只能从现有成果工作。
> - 不要与其他陪审员共谋。你是敌对的审查员；你的任务是破坏这一发现。
> - "RED-TEAM-DISPROVED"裁决需要一个具体的、可引用的理由。「我持怀疑态度」不够，「框架的默认中间件在文件 Y 的 X 行拒绝了此内容类型」才够。
> - "RED-TEAM-SURVIVED"裁决要求你尝试过多个角度。记录每个尝试。
> - 在不确定时倾向于「RED-TEAM-INCONCLUSIVE」——不要反驳你无法完全反驳的东西，但也不要生存下来你没有充分攻击的东西。
>
> #### 为什么这个阶段存在
>
> 早期的阶段可以共谋——即使陪审团是异构的，所有三个模型都以相同的代码和先验知识阅读同样的代码，并可能得出同一个错误的答案。此阶段故意轮换模型并反转提示词，使得确认偏见无处藏身。在第8 阶段幸存下来的发现已经受到了试图破坏它们但失败了的敌手的挑战。这是我们产生的最高置信度层级。

---

## PoC 生成

> **NEVER UPLOAD.** PoCs 是本地成果。它们不会被上传也不会自动提交。关于 PoC 生成和执行的同意是在任务开始时通过\xA71 AskUser 捕获的；此阶段非交互式运行，没有进一步提示词。

本节由\xA710 引用。它规定了如何生成利用脚本、存储位置以及（如果用户选择）沙盒执行的方法。

### 激活

完全由\xA71.Q7 驱动。此阶段不发出任何 AskUser 调用.

- `Skip PoC generation entirely` → 在此部分不做任何操作。
- `Generate scripts only (no execution)` → 草拟所有脚本，但从不执行。
- `Generate + auto-run in sandbox (all PoCs run silently; skips and failures logged to findings/<id>/poc/execution.log; no further prompts)` → 草拟所有脚本并静默自动运行每个符合条件的沙盒 PoC。

### 范围

只有经过 Pass 5 合成分类为 `EXPLOITABLE` 的发现才会生成 PoC。理论上的和不可利用的发现不会生成任何 PoC。可验证未知的发现也不会生成 PoC（证据不足无法安全构建一个）。

### 输出结构

对于每个合格的发现，PoC 艺术品位于对应的发现文件夹内：

```
findings/<finding-id>/poc/
├── README.md           # what the script does, preconditions, observable on success
├── exploit.<ext>       # the script itself; .sh, .py, .ts, .go, etc., based on the most natural fit
├── input/              # input fixtures (payloads, archives, JSON files)
├── expected/           # expected outputs / observables for verification
├── SANDBOXED=false     # marker file, present only if the PoC was not auto-runnable (skipped)
├── execution.log       # append-only log of auto-run attempts: started, finished, failed, skipped-not-sandboxable
└── sandbox/            # populated only if auto-run is enabled and runs occur
    └── run-<UTC-timestamp>/
        ├── stdout.log
        ├── stderr.log
        ├── env.json
        ├── observable.txt
        └── notes.md
```

### 脚本生成规则

1. **从 Pass 5 记录中获取利用源代码**。不要发明载荷。使用 `findings/<finding-id>/exploit.md` 中文档化的输入。
2. **尽可能单文件。** 优先选择具有 CLI 接口的一个脚本（如 `--target <url>`，`--input <file>`，`--out <file>`）而不是多文件框架。
3. **默认目标 = `http://localhost:8080`** （或其他本地地址）。脚本拒绝针对非本地目标运行，除非通过 `--i-am-the-owner` 标志并确认提示词明确覆盖。
4. **幂等且可观察。** 每次运行都必须生成一个 `observable.txt` 文件，其中包含成功的演示（例如，泄露的秘密、执行的命令输出或未经授权的数据）。
5. **红 acted 捕获的秘密。**如果脚本在其输出中捕获了真实秘密（密码、令牌、PII），则必须在持久日志中屏蔽它们（用 `[REDACTED]` 替换）；脚本仍然可以打印到 stdout，但持久化的文件是被屏蔽的。
6. **不写破坏性载荷。**永远不要编写删除、加密或使数据不可读的代码。只使用只读或标记写入的载荷（例如，创建一个名为 `pwned-<finding-id>.txt` 的文件作为标记）。
7. **注释绕过方法。**脚本头部必须包含一个注释块，解释该漏洞利用演示了什么以及什么样的修复可以防止它（参见 `findings/<finding-id>/disclosure.md` 中的“建议修复”部分进行交叉引用）。
8. **不复制粘贴恶意软件。**不要包括 shellcode、滴管程序、勒索软件风格的载荷或任何可能被重新利用来演示发现之外的内容。

### 每个 PoC 的 README 模板

```
# PoC — <finding-id>: <title>

> LOCAL ONLY. Do not run against systems you do not own. Do not upload.

## What this demonstrates
<one paragraph>

## Preconditions
- <network position>
- <privileges held>
- <state assumptions>

## Run
```

<command line example>
```

## Expected observable on success

<what you should see if the exploit fires>

## Cleanup

<how to undo any local marker the exploit creates>

## Reference

- Finding entry: `../README.md`
- Exploit record: `../exploit.md`
- Disclosure draft (includes suggested fix): `../disclosure.md`
- Top-level narrative: `../../../FINDINGS.md#<finding-id>`

```

### 沙盒执行（非交互式）

仅在用户选择了 `Generate + auto-run in sandbox` 时运行。\xA71.Q7 **不会在此发出 AskUser 调用。** 用户的 \xA71 回答是 PoC 执行的唯一同意界面；管道不会再次中断他们。

遍历每个合格的 PoC。对于每个 PoC:
1. 验证目标环境（参见“目标验证”部分）。如果不本地 → 写入 `findings/<id>/poc/SANDBOXED=false`，追加 `SKIP not-sandboxable <reason>` 到 `findings/<id>/poc/execution.log`，然后继续。**不要提示词用户。**
2. 在以下沙盒配置下运行 PoC。追加 `START`, `END exit=<code>`（或 `FAIL <reason>`) 到 `findings/<id>/poc/execution.log`。**失败时不提示词用户。**
3. 继续下一个 PoC。

协调器必须在该循环中任何情况下都不得重新提示词用户。失败、跳过和意外情况会在日志中被捕获并在最终移交总结（\xA714）中呈现。

### 沙箱配置

协调器在以下这些沙箱模式之一下运行 PoC（按顺序尝试）：

1. **临时容器（优先选择）:** `docker run --rm --network=none --read-only --tmpfs /tmp -v findings/<id>/poc:/poc:ro -v findings/<id>/poc/sandbox/run-<ts>:/out:rw <minimal-image>` — 无网络，PoC 的只读挂载，运行日志目录的写入挂载。
2. **chroot / nspawn (Linux):** 如果 Docker 不可用；最小化根文件系统，不暴露网络命名空间。
3. **macOS 沙箱-exec / 沙箱配置:** 如果在没有 Docker 的 macOS 上运行；约束文件系统和网络。
4. **无沙箱可用:** 不执行。对于每个符合条件的 PoC，请写入 `findings/<id>/poc/SANDBOXED=false` 并附带理由 `no-sandbox-primitive`，将 `SKIP no-sandbox-primitive` 追加到 `findings/<id>/poc/execution.log` 中，然后继续。在最终移交总结中仅报告一次该条件 — 不提示词。

在沙箱内:
- 网络: 默认为 `none`。如果 PoC 需要 `localhost`（例如，它必须与用户显式启动的本地服务器通信），启用仅允许 localhost 的桥接但阻止其他所有网络。
- 文件系统: PoC 的只读挂载。仅对输出进行读写挂载 `findings/<id>/poc/sandbox/run-<UTC-ts>/`。
- 时间: 强制执行墙钟超时（默认 60s）。
- 资源: 强制执行 CPU/内存限制。

### 目标验证

在任何执行之前，协调器必须验证目标是否为本地。一个目标是“本地”的当且仅当它解析为 `127.0.0.1`、`::1`、RFC1918 私有 IP 地址、Docker 桥接 IP 或由 PoC 本身启动的命名本地测试容器。

如果目标不是本地，PoC 不会自动运行。在 `findings/<id>/poc/SANDBOXED=false` 中记录发现结果，并附带理由 `non-local-target`，并将 `SKIP non-local-target` 添加到 `findings/<id>/poc/execution.log` 中，然后继续进行。脚本保留在磁盘上，用户可以在他们自己的授权下手动运行它。**不要提示词**——这会安静地处理并在最终的手动移交总结中显示一次。

### 日志和脱敏

- `sandbox/run-<UTC-ts>/stdout.log` — 捕获的 stdout，由脚本自身的脱敏逻辑进行脱敏。
- `sandbox/run-<UTC-ts>/stderr.log` — 捕获的 stderr。
- `sandbox/run-<UTC-ts>/env.json` — 传递给沙盒的环境变量的 JSON 快照（从不包含主机的秘密——沙盒启动时具有干净的环境）。
- `sandbox/run-<UTC-ts>/observable.txt` — 成功观察结果，已脱敏。
- `sandbox/run-<UTC-ts>/notes.md` — 沙盒配置、超时、资源限制、退出代码。

日志保持本地。它们从不上传。

### 硬性规则 (PoC)

- 永远不要在用户未拥有的系统上运行 PoC。
- 除非\xA71.Q7 = "生成 + 在沙盒中自动运行"，否则永不执行 PoC；任务中途永不重新提示词。
- 永不包含破坏性载荷。
- 永不将真实凭证嵌入脚本（使用 `--cred` 标志和占位符值）。
- 永不将未脱敏的秘密持久化到 `sandbox/run-*/` 目录中。
- 永不上传沙盒日志。
- 永不提交 `findings/<id>/poc/` 到远程仓库（协调者必须不从任务目录执行 `git push`；如果任务目录位于 Git 工作树内，请勿自动提交任何每个发现文件夹）。

---

## 输出格式

> **永不上传**。以下内容是 `~/security-audits/<slug>-<YYYYMMDD>/` 下的本地 artefact（具有自动镜像到 `~/Downloads/` 的功能）。披露草稿是草稿；人类在选择时手动提交。

本节是深度安全审查 skill 的渲染合同。协调体拥有如何运行通过、谁何时写什么；本节拥有最终落地文件的结构。

**权威伴侣**。任务目录树在\xA75（规范）和\xA70.5（紧凑型）中进行了记录。严重性 / 置信度 / 处置标签定义在上方的 **方法论参考** 部分（“处置词汇”）。每个通过的生命周期在\xA75.7 + \xA76 中进行了记录。当本节中的标签与 **方法论参考** 部分不一致时，请以 **方法论参考** 为准。

### \xA71 — 生产者 ↔ 消费者映射

任务目录中的每个文件恰好有一个生产者和至少一个消费者。布局在\xA75 中；本表格是写入方合同。

| 文件 / 目录                                             | 生成自                                                | 消耗于                                                   |
|--------------------------------------------------------|------------------------------------------------------------|---------------------------------------------------------------|
| `scope.md`                                             | \xA71 + \xA75 同意和范围                                | 每一轮次；读者作为审计上下文                           |
| `log.md`                                               | 协调器（持续进行，追加只读）                   | 读者；`DASHBOARD.md` 中的时间总结                      |
| `needs-context.md`                                     | \xA77 停止分支                                          | 读者；`STATUS.md` VU 部分                                |
| `_run-archive/areas.json`                              | Pass 0 区域检测步骤                                 | Pass 0 小队长调度器；`by-area/INDEX.md`              |
| `_run-archive/lieutenants/<area>/LIEUTENANT.{md,json}` | 每个区域一个小队长任务                               | orchestrator 去重 → `findings.json`                          |
| `_run-archive/dispatch/lieutenants/<area>.md`          | dispatcher (原始提示词 + 原始工作者回复)                 | 可重复性；调试                                        |
| `_run-archive/judge-passN.json`                        | 每轮次陪审合成器（楼层1–3；升级4, 5, 8)  | `JUDGE.md`，每个发现的起源记录 `provenance.json`                     |
| `findings/<id>/`                                       | 在首次每个发现写入时懒惰创建 (Pass 4)         | 每个发现的入口点                                       |
| `findings/<id>/README.md`                              | \xA79 整合                                           | 读者 (主要每个发现着陆页面)                     |
| `findings/<id>/provenance.json`                        | orchestrator 每轮次后 (只读追加)                 | `JUDGE.md`, `STATUS.md`, `FINDINGS.md`                        |
| `findings/<id>/dataflow.md`                            | Pass 4 跟踪器                                              | Pass 4 审查员；CVSS 推导；`FINDINGS.md`              |
| `findings/<id>/exploit.md`                             | Pass 5 构造函数                                         | Pass 5 审查人；PoC 生成器；披露草稿             |
| `findings/<id>/ctx/round-N.md`                         | \xA77 上下文递归子工作者                            | 起始通过在恢复中                                    |
| `findings/<id>/disclosure.md`                          | \xA712                                                        | 用户（手动披露）                                      |
| `findings/<id>/poc/*`                                  | \xA710 PoC 生成器+沙盒运行器                         | 用户（手动重放）；证据捕获                        |
| `findings/<id>/evidence/*`                             | \xA711 捕获阶段                                          | 读者；嵌入在披露中                                |
| `findings.json`                                        | \xA79 整合                                           | 每个渲染的 Markdown 文件；读者；下游工具        |
| `FINDINGS.md`                                          | \xA79 从 **FINDINGS.md 模板** + `findings.json`     | 读者（主要叙述）                                    |
| `JUDGE.md`                                             | \xA79 从 **JUDGE.md 模板** + 来源 JSON       | ["读者 (每遍验证表)")                              |
| `STATUS.md`                                            | \xA79 从 **STATUS.md 模板** + `findings.json`       | 读者 (后判决仪表板)                                 |
| `DASHBOARD.md`                                         | \xA79 从 **DASHBOARD.md 模板** + `findings.json` + `log.md` | 读者（单页概览）                      |
| `README.md`                                            | \xA79 固定渲染问题                                            | 读者 (入口点)                                          |
| `by-severity/*.md`                                     | \xA79 `findings.json` 的分区                            | 读者 (按严重性切片视图)                                 |
| `by-area/*.md`                                         | \xA79 `findings.json` 按 `area` 分区                  | reader (按区域切片视图)                                     |

### \xA72 — 文件格式

以下每个文件的目的、必需字段以及规范骨架所在位置。仅在模板或模式不是规范来源时保留内联示例：

#### 2.1 `README.md` (首页)

**必需字段:** 目标、提交记录、审计日期、陪审团组成（带备选方案）、按严重程度细分的发现总数、指向 `DASHBOARD.md` / `STATUS.md` / `FINDINGS.md` / `findings/` 的链接、镜像位置。**填充内容:** \xA79 从 `findings.json` + `scope.md` 获取。**骨架:** 直接由汇总器生成 — 没有外部模板。必须以“永不上传”横幅开头，并以“披露权在用户手中”的提醒结尾。

#### 2.2 `DASHBOARD.md`

**规范骨架:** 此参考附录中的 **DASHBOARD.md 模板** 部分。**必需部分（映射到 `findings.json` + `log.md`）:** 总计；严重程度直方图；置信度层级直方图；按严重程度和置信度排序的前10 项；严重程度变化及同源捆绑；每阶段拆分率；按区域统计；时间戳。

#### 2.3 `STATUS.md`

**规范骨架:** 此参考附录中的 **STATUS.md 模板** 部分。**每个发现所需的列:** `id`，`title`，`severity`，`dataflow_reachability`，`exploit_status`，`red_team_status`，`jury_split`（Y/N），`dissent_notes`（截断），`disclosure_target`，指向 `findings/<id>/README.md` 的链接。法官进度表（原始严重程度 → 最终严重程度，最终裁决，如果同源则为父 CVE）附在主要的每个发现表格旁边。

#### 2.4 `FINDINGS.md`

**标准骨架:** 这个参考附录中的 **FINDINGS.md 模板** 部分。**必需的每个发现部分:** 摘要、触发条件、代码证据（围栏标记，语言标签化）、数据流指针、利用指针、建议修复、先例、深入先例研究、陪审团裁决（每轮次）、决胜票、反对意见备注、披露草稿指针、文件夹 + 来源链接。附录涵盖可验证未知发现和陪审团备用笔记。

#### 2.5 `JUDGE.md`

**标准骨架:** 这个参考附录中的 **JUDGE.md 模板** 部分。**必需的部分:** 每轮次统计表（每轮次一致意见 / 分裂 / 决胜票 / 上下文 / 降级计数）；每个发现的裁决表，一行表示一轮次；严重性原始/最终值/兄弟 CVE 行；每个发现的反对意见备注；阅读指南。

#### 2.6 `findings.json`

**标准模式:** 这个参考附录中的 **输出模式** 部分。所有被提升、有争议和可验证未知的发现都生活在这里。严重性 / 信心度 / 处置枚举来自该参考附录中的 **方法论参考** 部分；字段如 `severity_original`，`severity_final`，`parent_cve_if_sibling`，`final_verdict` 是模式中规范性的。

**写入端合约:** \xA79 合并器将每轮次的 JSON 文件（`_run-archive/judge-passN.json`）与每个发现的 `provenance.json` 合并为一个发现记录。可选路径（`dataflow_path`，`exploit_path`，`disclosure_path`，`evidence_paths`，`poc_paths`，`prior_art_deep`）仅当对应文件存在时才发出。

#### 2.7 每个发现的文件夹 (`findings/<finding-id>/`)

每个发现的所有文件都生活在这里。在第一次写入发现（Pass 4）时懒惰创建。该文件夹是自包含的，用户可以 `tar czf <id>.tgz findings/<id>/` 来分享一个发现。

布局（参见 \xA75 获取完整树结构）：

```

findings/<finding-id>/
├── README.md # \xA79 consolidation: entry page
├── disclosure.md # \xA712: local-only draft
├── dataflow.md # Pass 4: source → sink trace
├── exploit.md # Pass 5: exploit construction
├── provenance.json # append-only chain-of-custody
├── ctx/round-N.md # \xA77 NEEDS-CONTEXT recursion
├── poc/ # \xA710; only EXPLOITABLE + user opted in
└── evidence/ # \xA711; only if \xA71.Q8 ≠ None

````

##### 2.7.1 `README.md` — 每个发现的独立页面

H1: `# <finding-id> — <title>  [<severity badge>]`. 必要内容：一段总结（从 `FINDINGS.md` 教程中提取）；`final_confidence`；`area`；`file:line`；已解决的披露目标；快速链接块，链接到文件夹中的每个兄弟制品，并返回到 `../../STATUS.md`, `../../FINDINGS.md`, `../../DASHBOARD.md`。在原始文档模式（\xA71.Q6）中跳过这些内容。

##### 2.7.2 `provenance.json`

形状记录在 \xA78 中（规范）。必要字段：`id`, `proposed_by`, `passes[]`, `tiebreakers[]`, `red_team_survived`, `final_confidence`, `dissent_notes[]`。仅在通过过程中追加；\xA78 中的内联示例是规范性的。

##### 2.7.3 `dataflow.md`

必要部分（第 4 轮投票）：来源（入口点 + 不信任性理由 + file:line）；前向追踪（表：步骤，file:line, 变换/净化器）；后向追踪（sink ← 调用者 ← 入口点）；检查的净化器 / 抵御措施；每个陪审员的可达性裁决 + 综合。

裁决枚举：`REACHABLE-FROM-UNTRUSTED`, `REACHABLE-INTERNAL-ONLY`, `UNREACHABLE`.

##### 2.7.4 `exploit.md`

必要部分（第 5 轮投票）：前提条件（网络位置，权限，知识，状态）；输入（确切字节 / 头部 / 载荷 / 序列）；成功时的预期观察结果；现实攻击者画像；每个陪审员的裁决 + 综合。可选部分：自动化草图（对于 `THEORETICAL` 项省略）。

裁决枚举：`EXPLOITABLE`, `THEORETICAL`, `UNEXPLOITABLE`.

##### 2.7.5 `ctx/round-N.md`

每轮 \xA77 都有一个单独的 markdown 文件；文件名按轮次递增。由上下文收集子工作者编写。

##### 2.7.6 `disclosure.md`

每个已推广的发现一个。完整的骨架在 \xA712 中。必需部分：摘要，受影响版本/提交记录，复现步骤（指向 `./exploit.md`），影响，建议修复，建议披露目标（主要+次要；梯子在 \xA75.10 中），CVSS 评分（3.1 基础 — 见 \xA73 下面），来源指针。没有顶级的 `disclosure/` 目录；不进行供应商打包（每个任务一个单仓库）。

##### 2.7.7 `poc/` 和 `evidence/`

PoC 布局，沙盒不变量和执行日志语义位于上面的 **PoC 生成** 部分。证据捕获工具（asciinema, ffmpeg, Playwright）以及每个发现的 `evidence/README.md` 合同位于 \xA711 中。

#### 2.8 `log.md`

只读。必需部分：已解决范围；陪审团决议（模型状态+备用方案）；每轮时间表（通过，UTC 开始，UTC 结束，墙钟，发现，任务分发）；拦路虎/错误；NEEDS-CONTEXT 递归计数；决断计数；最终计数（指向 `DASHBOARD.md`）。写入在 \xA75 初始化、每轮的 `pass-start` / `pass-end` 标记以及 \xA79 的 `## Final summary` 块中连续进行。

#### 2.9 `_run-archive/lieutenants/<area>/LIEUTENANT.json`

JSON 数组的候选记录。每个记录的必需字段：`area`, `file_line`, `code_quote`, `proposed_severity`, `proposed_confidence`, `suspected_class`, `trigger`, `impact`, `needs_context`。可选：`lang`, `prior_art_hint`。由每次 Pass 0 的副官写入 `LIEUTENANT.md` 旁边；被协调器消费以进行确定性去重（合并具有相同 `(file_line, suspected_class)` 的记录）和标准的 `<area>-<seq>` ID 分配。

#### 2.10 `_run-archive/dispatch/lieutenants/<area>.md`

原封不动分发的数据包写在每个 Pass 0 副官启动之前。必需内容：绑定变量（`area`, `target_path`, `commit_sha`, `mission_dir`, `jury_slot_hint`, `priority_tier`, `code_roots`, `exclude_globs`）+ 替换变量后的**Pass 0 副官提示词**主体。分发后永不修改。

#### 2.11 `_run-archive/areas.json`

JSON 数组。每条记录：`area`, `code_roots[]`, `lieutenant_focus`, `priority_tier` (1–3; 1 = 最高), `jury_slot_hint`, `exclude_globs[]`。在 Pass 0 的区域检测步骤之前写入，供分发器和`by-area/INDEX.md`在\xA79 处消费。

#### 2.12 `by-severity/`

一个`INDEX.md` + 每个严重性桶（`CRITICAL.md`, `HIGH.md`, `MEDIUM.md`, `LOW.md`, `INFO.md`）的一个文件 + 一个综合的`ALL.md`。每个文件都是必需的 — 空的桶渲染标题加上`No findings at this severity.`。

**行模式（标准；用于`ALL.md`+ 每个严重性文件）：**

| 列     | 来源                     | 渲染为                                                   |
|------------|----------------------------|---------------------------------------------------------------|
| ID         | `id`                       | `` [`<id>`](../findings/<id>/) ``                              |
| 标题      | `title`                    | 纯文本                                                    |
| 严重级别   | `severity`                 | `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `INFO`               |
| 信心 | `final_confidence`         | 简短标签                                                   |
| 数据流   | `dataflow_reachability`    | 简短标签                                                   |
| 利用    | `exploit_status`           | 简短标签                                                   |
| 红队   | `red_team_status`          | 简短标签                                                   |
| 文件:行  | `file_line`                | `` `path:line` ``                                              |
| README     | 衍生                    | `` [`README`](../findings/<id>/README.md) ``                   |
| 叙述  | 衍生                    | `` [`narrative`](../FINDINGS.md#<id>) ``                       |

**排序顺序（除 `INDEX.md` 外的每个文件）：** 严重性降序 → `final_confidence` 降序 (`RED-TEAM-SURVIVED` > `UNANIMOUS` > `MAJORITY` > `VERIFIABLE-UNKNOWN` > `DISPUTED`) → id 升序。

**`INDEX.md` 必须包含：** 严重性计数表（列 `Severity | Promoted | Disputed | VU | Total | File`）；每个严重性文件的链接列表（带括号中的每文件计数）；指向 `by-severity/HARDENING.md` 的链接；指向 `../DASHBOARD.md`、`../STATUS.md`、`../FINDINGS.md` 和 `../by-area/INDEX.md` 的指针。

**必需规则（在 \xA79 合并时检查）：**

1. 每行必须链接到 `../findings/<id>/`；不得用完整叙述替换链接。
2. 每个严重性文件必须存在（即使为空）。
3. 路径使用 `findings/<id>/` 树；从不使用已弃用的平行目录 (`provenance/`, `dataflow/`, `exploits/`, `patches/`, `disclosure/`, `poc/`, `evidence/`)。
4. 严重性标签完全匹配模式枚举：`CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `INFO`（不是 `MED`）。
5. `by-severity/HARDENING.md` 汇总仓库的 `hardening/` 树（每个 `<TAG>-NNN.md` 注释加上 `hardening/SUMMARY.md`；参见上方的 **方法论参考** 部分）；与每个严重性文件同时编写。缺少加固情况显示标题加上 `No hardening notes yet; hardening is populated after phase5.`.

### \xA73 — CVSS v3.1 衍生

该 skill 为每个推广发现（以及有争议但保留的发现）发出一个 CVSS v3.1 基础分数和向量。向量是从早期通过证据确定性地推导出来的。

| 度量                     | 推导                                                                                                                                                              |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 攻击向量 (AV)         | Pass 4 来源: 外部 HTTP/RPC → `N`; 邻近网络 / IPC → `A`; 本地 CLI / 文件 → `L`; 物理 → `P`.                                                            |
| 攻击复杂性 (AC)     | Pass 5 先决条件: 简单 → `L`; 竞争 / 特定配置 / 中间人攻击 / 时间 → `H`.                                                                                       |
| 所需特权 (PR)   | Pass 4 可达性 + Pass 5 先决条件: 未授权 → `N`; 已认证用户 → `L`; 管理员/内部 → `H`.                                                                |
| 用户交互 (UI)      | Pass 5 输入: 仅服务器端 → `N`; 恶意受害者必须点击/粘贴/打开 → `R`.                                                                                               |
| 范围 (S)                  | 传递 4 漏洞 + 影响: 同一安全权威 → `U`; 跨越权威（沙箱逃逸、多租户交叉、容器逃逸）→ `C`.                                 |
| 保密性 (C)        | 传递 5 可观察性: 完整数据 / PII / 秘密 → `H`; 有边界 → `L`; 无 → `N`.                                                                                           |
| 完整性 (I)              | 传递 5 可观察性: 写入 / 修改 / 伪造 → `H`; 有边界 → `L`; 无 → `N`.                                                                                              |
| 可用性 (A)           | 传递 5 可观察性: 完整中断 / 崩溃 / 锁定 → `H`; 有限降级 → `L`; 无 → `N`.                                                                              |

**计算。** 发出向量字符串（例如，`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`）以及使用标准 CVSS v3.1 公式的基本分数。披露草案包含一个简短的解释表，将每个指标映射到通过证据.

**严重性 ↔ CVSS 合理性检查。** `findings.json[severity]` 应与 CVSS 基础分一致（Critical 9.0–10.0、High 7.0–8.9、Medium 4.0–6.9、Low 0.1–3.9）。相差超过 1 个级别时，必须写入 `log.md` 并重新审查。

**分数存放位置。** 向量 + 基础分 + 各指标依据 → `findings/<id>/disclosure.md` \xA7 CVSS 评分。裸分数也写入 `findings.json[cvss]`。

### \xA74 — 大小期望（factory-mono 类似）

粗略估计一个包含约20 个区域、超过1M 行代码的多仓库在 HEAD 处，严重性门槛="报告所有"的情况：

| 阶段 / 构件                              | 典型幅度                                              |
|-----------------------------------------------|----------------------------------------------------------------|
| 中尉种子候选者（Pass 0）           | 250–600（过度包含；~12–30 每个区域）                     |
| 幸存 Pass 1（CONFIRMED）                  | 150–400                                                        |
| 幸存 Pass 4（REACHABLE-FROM-UNTRUSTED）   | 60–180                                                         |
| 幸存 Pass 5（EXPLOITABLE）                | 25–80                                                          |
| 幸存 Pass 8（RED-TEAM-SURVIVED）          | 10–40                                                          |
| 最终晋升的发现（任何层级）            | 30–100                                                         |
| `findings.json` 合并后的记录   | ~80–250                                                        |
| 任务目录在磁盘上的大小                      | 80 MB – 2 GB (证据密集型；`.cast` 较便宜，`.mp4` 较昂贵)     |
| `_run-archive/` 占用的磁盘空间                  | 5–60 MB；约15–30% 的 任务-dir                                |
| `findings/<id>/` 每个发现，纯文本       | 20–400 KB (来源 + 数据流 + 利用 + 说明文档 + 披露 + 上下文) |
| `findings/<id>/evidence/`                     | 0–60 MB（最重时包含 asciinema + ffmpeg + 头部浏览器）  |
| `findings/<id>/poc/`                          | 50 KB – 5 MB                                                   |
| **总实际时间（深度优先）**            | **6–20 小时**；在重需要上下文的情况下，异常值可能长达36 小时 |

实际数字始终记录在 `log.md` 中。每阶段的实际时间是从协调器附加的 pass-start / pass-end 标记中计算得出的:

**移交后修剪 `_run-archive/`。** 存档包含原始协调架构，可以安全地压缩并删除；所有下游信息已经编码了面向用户的信息：

```sh
cd ~/security-audits/<slug>-<date>
tar czf _run-archive.tar.gz _run-archive/ && rm -rf _run-archive/
````

> **提醒。** 这里记录的所有内容都不会上传。`findings/<id>/disclosure.md` 下的披露草稿只是草稿；用户仅在选择时手动提交。

---

## 输出模式

深度安全审计生成的单个发现的标准机器可读模式（`findings.json` 是符合此模式的记录数组）：

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://factory.ai/schemas/deep-security-review/output.json",
  "title": "Canonical finding record",
  "description": "Canonical machine-readable schema for a single finding produced by the deep security audit.",
  "type": "object",
  "required": [
    "id",
    "title",
    "severity",
    "area",
    "file_line",
    "summary",
    "trigger",
    "impact",
    "dataflow_reachability",
    "exploit_status",
    "red_team_status",
    "jury_verdicts",
    "prior_art",
    "final_confidence",
    "dissent_notes"
  ],
  "additionalProperties": false,
  "properties": {
    "id": { "type": "string", "pattern": "^[a-z0-9-]+-\\d{3,}$" },
    "title": { "type": "string" },
    "severity": {
      "type": "string",
      "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    },
    "area": { "type": "string" },
    "category": { "type": "string" },
    "file_line": { "type": "string" },
    "code_quote": { "type": "string" },
    "lang": { "type": "string" },
    "summary": { "type": "string" },
    "trigger": { "type": "string" },
    "impact": { "type": "string" },
    "dataflow_reachability": {
      "type": "string",
      "enum": [
        "REACHABLE-FROM-UNTRUSTED",
        "REACHABLE-INTERNAL-ONLY",
        "UNREACHABLE",
        "VERIFIABLE-UNKNOWN",
        "PENDING"
      ]
    },
    "dataflow_path": { "type": "string" },
    "exploit_status": {
      "type": "string",
      "enum": [
        "EXPLOITABLE",
        "THEORETICAL",
        "UNEXPLOITABLE",
        "PENDING",
        "VERIFIABLE-UNKNOWN"
      ]
    },
    "exploit_path": { "type": "string" },
    "red_team_status": {
      "type": "string",
      "enum": [
        "RED-TEAM-SURVIVED",
        "RED-TEAM-INCONCLUSIVE",
        "RED-TEAM-INCONCLUSIVE-NEEDS-RUNTIME",
        "RED-TEAM-DISPROVED",
        "PENDING"
      ]
    },
    "patch_path": { "type": "string" },
    "patch_status": {
      "type": "string",
      "enum": [
        "PATCH-COMPLETE",
        "PATCH-PARTIAL",
        "PATCH-UNCERTAIN",
        "PENDING",
        "NOT-CONSTRUCTED"
      ]
    },
    "jury_verdicts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pass", "synthesis"],
        "properties": {
          "pass": { "type": "string" },
          "synthesis": { "type": "string" },
          "split": { "type": "boolean" },
          "verdicts": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["model", "verdict"],
              "properties": {
                "model": { "type": "string" },
                "verdict": { "type": "string" },
                "rationale": { "type": "string" }
              }
            }
          }
        }
      }
    },
    "prior_art": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "id"],
        "properties": {
          "type": {
            "type": "string",
            "enum": [
              "GHSA",
              "CVE",
              "vendor-advisory",
              "h1-disclosure",
              "commit",
              "blog",
              "paper",
              "rfc",
              "spec",
              "cwe",
              "framework_doc",
              "talk"
            ]
          },
          "id": { "type": "string" },
          "url": { "type": "string", "format": "uri" },
          "summary": { "type": "string" },
          "match_strength": {
            "type": "string",
            "enum": ["EXACT", "STRONG", "WEAK", "BACKGROUND"]
          }
        }
      }
    },
    "prior_art_deep": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string" },
          "title": { "type": "string" },
          "authors": { "type": "string" },
          "venue": { "type": "string" },
          "url": { "type": "string", "format": "uri" },
          "summary": { "type": "string" },
          "applicability": {
            "type": "string",
            "enum": ["DIRECT", "ANALOGOUS", "BACKGROUND"]
          }
        }
      }
    },
    "suggested_patch_ref": { "type": "string" },
    "final_confidence": {
      "type": "string",
      "enum": [
        "RED-TEAM-SURVIVED",
        "UNANIMOUS",
        "MAJORITY",
        "VERIFIABLE-UNKNOWN",
        "DISPUTED"
      ]
    },
    "final_verdict": {
      "type": "string",
      "description": "Disposition verdict after all floor passes complete. See \xA75.8.",
      "enum": [
        "PROMOTED",
        "DEMOTED-DUPLICATE",
        "DEMOTED-KBD",
        "DISPUTED",
        "WITHDRAWN",
        "SIBLING-OF-PRIOR",
        "CONFIRMED-BY-DESIGN"
      ]
    },
    "pass1_verdict": {
      "type": "string",
      "description": "Synthesized line-anchor verdict at Pass 1. See \xA75.8.",
      "enum": ["CONFIRMED", "DISPUTED", "NEEDS-CONTEXT", "CONFIRMED-BY-DESIGN"]
    },
    "pass2_verdict": {
      "type": "string",
      "description": "Synthesized vendor-prior-art verdict at Pass 2. See \xA75.8.",
      "enum": [
        "REMAINS-NOVEL",
        "SIBLING-OF-PRIOR",
        "DEMOTE-DUPLICATE",
        "DEMOTE-KBD"
      ]
    },
    "severity_original": {
      "type": "string",
      "description": "Severity initially proposed by the lieutenant (Pass 0), before any judge downgrades.",
      "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    },
    "severity_final": {
      "type": "string",
      "description": "Severity after all severity-shift verdicts resolved. See \xA75.8.",
      "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    },
    "parent_cve_if_sibling": {
      "type": ["string", "null"],
      "description": "Parent advisory ID when final_verdict == SIBLING-OF-PRIOR (e.g., "CVE-2025-61667", "GHSA-xxxx-xxxx-xxxx"). Null otherwise."
    },
    "dissent_notes": { "type": "array", "items": { "type": "string" } },
    "provenance_path": { "type": "string" },
    "disclosure_path": { "type": "string" },
    "evidence_paths": { "type": "array", "items": { "type": "string" } },
    "poc_paths": { "type": "array", "items": { "type": "string" } }
  }
}
```

---

## DASHBOARD.md 模板

在 \xA79 合并时渲染此骨架，通过替换 Handlebars 样式的变量（`{{ var }}`，`{{#each}}`，`{{#if}}`）针对 `findings.json` + `log.md`：

````markdown
# Dashboard — deep security audit at a glance

> **NEVER UPLOAD.** All output local.

- **Target:** `{{ target }}`
- **Commit:** `{{ commit_sha }}`
- **Date:** `{{ audit_date }}`
- **Jury:** `{{ jury }}`

## Top-line counts

- Total findings: **{{ total }}**
- Promoted: **{{ promoted }}**
- Disputed-after-adversarial: **{{ disputed }}**
- Verifiable-unknown: **{{ vu }}**

## Severity histogram

```
CRITICAL  {{ bar.crit }}  ({{ ct.crit }})
HIGH      {{ bar.high }}  ({{ ct.high }})
MEDIUM    {{ bar.med }}   ({{ ct.med }})
LOW       {{ bar.low }}   ({{ ct.low }})
INFO      {{ bar.info }}  ({{ ct.info }})
```

## Confidence-tier histogram

```
RED-TEAM-SURVIVED   {{ bar.rts }}  ({{ ct.rts }})
UNANIMOUS           {{ bar.unanim }}  ({{ ct.unanim }})
MAJORITY            {{ bar.maj }}  ({{ ct.maj }})
VERIFIABLE-UNKNOWN  {{ bar.vu }}  ({{ ct.vu }})
DISPUTED            {{ bar.disp }}  ({{ ct.disp }})
```

## Top 10 by severity then confidence

| Rank             | ID  | Title | Severity     | Final confidence                       | Folder        |
| ---------------- | --- | ----- | ------------ | -------------------------------------- | ------------- | ---------------- | ------------------------ | ------------------------------------------------------- |
| {{#each top10 as | t   | }}    | {{ t.rank }} | [`{{ t.id }}`](FINDINGS.md#{{ t.id }}) | {{ t.title }} | {{ t.severity }} | {{ t.final_confidence }} | [`findings/{{ t.id }}/`](findings/{{ t.id }}/README.md) |

{{/each}}

## Severity shifts & sibling bundling (from JUDGE.md)

```
HIGH → MED   {{ bar.shift_high_med }}  ({{ ct.shift_high_med }})
HIGH → LOW   {{ bar.shift_high_low }}  ({{ ct.shift_high_low }})
MED  → LOW   {{ bar.shift_med_low }}   ({{ ct.shift_med_low }})
SIBLING-OF-PRIOR (bundled)   {{ bar.sibling }}  ({{ ct.sibling }})
```

| ID                 | severity_original | severity_final | parent_cve_if_sibling                  |
| ------------------ | ----------------- | -------------- | -------------------------------------- | --------------------------- | ------------------------ | ------------------------------- |
| {{#each shifted as | s                 | }}             | [`{{ s.id }}`](FINDINGS.md#{{ s.id }}) | `{{ s.severity_original }}` | `{{ s.severity_final }}` | `{{ s.parent_cve_if_sibling }}` |

{{/each}}

## Pass-by-pass split rates

| Pass           | Findings          | Splits          | Tiebreakers run | Empirical tiebreakers run |
| -------------- | ----------------- | --------------- | --------------- | ------------------------- |
| 1 line-anchor  | {{ p1.findings }} | {{ p1.splits }} | {{ p1.tb1 }}    | {{ p1.tb2 }}              |
| 2 vendor-prior | {{ p2.findings }} | {{ p2.splits }} | {{ p2.tb1 }}    | {{ p2.tb2 }}              |
| 4 dataflow     | {{ p4.findings }} | {{ p4.splits }} | {{ p4.tb1 }}    | {{ p4.tb2 }}              |
| 5 exploit      | {{ p5.findings }} | {{ p5.splits }} | {{ p5.tb1 }}    | {{ p5.tb2 }}              |
| 6 patch        | {{ p6.findings }} | {{ p6.splits }} | {{ p6.tb1 }}    | {{ p6.tb2 }}              |
| 8 red-team     | {{ p8.findings }} | n/a             | n/a             | {{ p8.tb2 }}              |

## Quick links

- [FINDINGS.md](FINDINGS.md)
- [JUDGE.md](JUDGE.md)
- [STATUS.md](STATUS.md)
- [`needs-context.md`](needs-context.md)
````

---

## FINDINGS.md 模板

在 \xA79 合并时渲染此骨架：

````markdown
# Deep security review — findings

> **NEVER UPLOAD.** All output in this directory is local. Disclosure drafts under `findings/<id>/disclosure.md` are drafts only and were NOT submitted to any external party.

- **Target:** `{{ target }}`
- **Commit:** `{{ commit_sha }}`
- **Audit date:** `{{ audit_date }}`
- **Jury composition:** `{{ jury }}` (with fallbacks: `{{ fallbacks }}`)
- **Total findings:** `{{ total_findings }}`
- **Promoted:** `{{ promoted_count }}` (CRITICAL: `{{ crit }}` / HIGH: `{{ high }}` / MEDIUM: `{{ med }}` / LOW: `{{ low }}` / INFO: `{{ info }}`)
- **Disputed-after-adversarial:** `{{ disputed_count }}`
- **Verifiable-unknown:** `{{ vu_count }}`

For per-finding verdict tables across every pass that fired, see [JUDGE.md](JUDGE.md). For the dashboard, see [STATUS.md](STATUS.md). For severity-sorted views, see `by-severity/`.

---

{{#each findings as |f|}}

## `{{ f.id }}` — {{ f.title }}

- **Severity:** {{ f.severity }}
- **Severity (original → final):** {{ f.severity_original }} → {{ f.severity_final }}
- **Final verdict:** {{ f.final_verdict }}
- **Final confidence:** {{ f.final_confidence }}
- **Parent CVE (if SIBLING-OF-PRIOR):** {{ f.parent_cve_if_sibling }}
- **Area:** {{ f.area }}
  {{#if f.owasp_mapping }}- **OWASP / STRIDE mapping:** {{ f.owasp_mapping }}{{/if}}
- **File:line:** `{{ f.file_line }}`
- **Dataflow reachability:** {{ f.dataflow_reachability }}
- **Exploit status:** {{ f.exploit_status }}
- **Red-team status:** {{ f.red_team_status }}
- **Folder:** [`findings/{{ f.id }}/`](findings/{{ f.id }}/README.md)
- **Provenance:** [`findings/{{ f.id }}/provenance.json`](findings/{{ f.id }}/provenance.json)

### Summary

{{ f.summary }}

### Trigger

{{ f.trigger }}

### Code evidence

```{{ f.lang }}
{{ f.code_quote }}
```

### Dataflow trace

See [`findings/{{ f.id }}/dataflow.md`](findings/{{ f.id }}/dataflow.md).

### Exploit

{{#if f.exploit_path }}See [`findings/{{ f.id }}/exploit.md`](findings/{{ f.id }}/exploit.md).{{else}}Not constructed (status: {{ f.exploit_status }}).{{/if}}

### Suggested fix

{{ f.suggested_fix }}

### Prior art

{{#each f.prior_art as |pa|}}- [{{ pa.id }}]({{ pa.url }}) — {{ pa.summary }} (match: {{ pa.match_strength }}){{/each}}

### Deep prior-art research

{{#each f.prior_art_deep as |pad|}}- {{ pad.type }}: [{{ pad.title }}]({{ pad.url }}) ({{ pad.applicability }}) — {{ pad.summary }}{{/each}}

### Jury verdicts

{{#each f.passes as |p|}}**{{ p.pass }}** — synthesis: `{{ p.synthesis }}` (split: {{ p.split }})
{{#each p.verdicts as |v|}}- `{{ v.model }}` → `{{ v.verdict }}`: {{ v.rationale }}{{/each}}
{{/each}}

### Tiebreakers

{{#each f.tiebreakers as |tb|}}- Round {{ tb.round }} ({{ tb.models }}): `{{ tb.verdict }}` — {{ tb.rationale }}{{/each}}

### Dissent notes

{{#each f.dissent_notes as |d|}}- {{ d }}{{/each}}

### Disclosure draft (LOCAL ONLY)

[`findings/{{ f.id }}/disclosure.md`](findings/{{ f.id }}/disclosure.md)

---

{{/each}}

## How to read this report

- The canonical machine-readable record is `findings.json`.
- Each finding has its own folder at `findings/<id>/` containing every per-finding artifact (README, disclosure, dataflow, exploit, provenance, ctx, poc/, evidence/).
- Each finding has a provenance JSON in `findings/<id>/provenance.json` recording every juror's verdict at every pass.
- Findings are sorted by `severity` then by `final_confidence` (RED-TEAM-SURVIVED first, DISPUTED last).
- Disputed-after-adversarial findings remain in this report (in their own section) — they are not silently dropped.
- Verifiable-unknown findings are listed in [`needs-context.md`](needs-context.md) and tagged in `STATUS.md`.

> **Reminder:** nothing here was uploaded. Disclosure is the human user's decision.
````

---

## JUDGE.md 模板

在 \xA79 合并时渲染此骨架：

```markdown
# Judge — per-finding verdict tables across every pass that fired

> **NEVER UPLOAD.** All output local.

- **Target:** `{{ target }}`
- **Commit:** `{{ commit_sha }}`
- **Audit date:** `{{ audit_date }}`
- **Jury:** `{{ jury }}`

This file surfaces the multi-model jury's verdict at every pass for every finding. The canonical record is `findings/<id>/provenance.json`.

---

## Pass-stats summary

| Pass                  | Total findings entering | UNANIMOUS              | MAJORITY (split) | TIEBREAKER round-1 invoked | TIEBREAKER round-2 invoked | NEEDS-CONTEXT recursions | Demoted          |
| --------------------- | ----------------------- | ---------------------- | ---------------- | -------------------------- | -------------------------- | ------------------------ | ---------------- |
| Pass 0 — lieutenant   | n/a (seed)              | n/a                    | n/a              | n/a                        | n/a                        | n/a                      | {{ p0_demoted }} |
| Pass 1 — line-anchor  | {{ p1_in }}             | {{ p1_unanim }}        | {{ p1_split }}   | {{ p1_tb1 }}               | {{ p1_tb2 }}               | {{ p1_ctx }}             | {{ p1_demoted }} |
| Pass 2 — vendor prior | {{ p2_in }}             | {{ p2_unanim }}        | {{ p2_split }}   | {{ p2_tb1 }}               | {{ p2_tb2 }}               | {{ p2_ctx }}             | {{ p2_demoted }} |
| Pass 3 — deep prior   | {{ p3_in }}             | n/a (enrichment)       | n/a              | n/a                        | n/a                        | {{ p3_ctx }}             | n/a              |
| Pass 4 — dataflow     | {{ p4_in }}             | {{ p4_unanim }}        | {{ p4_split }}   | {{ p4_tb1 }}               | {{ p4_tb2 }}               | {{ p4_ctx }}             | {{ p4_demoted }} |
| Pass 5 — exploit      | {{ p5_in }}             | {{ p5_unanim }}        | {{ p5_split }}   | {{ p5_tb1 }}               | {{ p5_tb2 }}               | {{ p5_ctx }}             | {{ p5_demoted }} |
| Pass 8 — red-team     | {{ p8_in }}             | n/a (single adversary) | n/a              | n/a                        | {{ p8_emp }}               | {{ p8_ctx }}             | {{ p8_demoted }} |

---

## Per-finding verdict tables

{{#each findings as |f|}}

### `{{ f.id }}` — {{ f.title }} (severity: {{ f.severity }}; final: {{ f.final_confidence }})

| severity_original           | severity_final           | parent_cve_if_sibling           |
| --------------------------- | ------------------------ | ------------------------------- |
| `{{ f.severity_original }}` | `{{ f.severity_final }}` | `{{ f.parent_cve_if_sibling }}` |

| Pass           | {{ jury_a }}                     | {{ jury_b }}   | {{ jury_c }}   | Split?           | Synthesis              | Tiebreaker     |
| -------------- | -------------------------------- | -------------- | -------------- | ---------------- | ---------------------- | -------------- |
| 1 line-anchor  | `{{ f.p1.a }}`                   | `{{ f.p1.b }}` | `{{ f.p1.c }}` | {{ f.p1.split }} | `{{ f.p1.syn }}`       | {{ f.p1.tb }}  |
| 2 vendor-prior | `{{ f.p2.a }}`                   | `{{ f.p2.b }}` | `{{ f.p2.c }}` | {{ f.p2.split }} | `{{ f.p2.syn }}`       | {{ f.p2.tb }}  |
| 3 deep-prior   | enrichment                       | enrichment     | enrichment     | n/a              | {{ f.p3.links }} links | n/a            |
| 4 dataflow     | `{{ f.p4.a }}`                   | `{{ f.p4.b }}` | `{{ f.p4.c }}` | {{ f.p4.split }} | `{{ f.p4.syn }}`       | {{ f.p4.tb }}  |
| 5 exploit      | `{{ f.p5.a }}`                   | `{{ f.p5.b }}` | `{{ f.p5.c }}` | {{ f.p5.split }} | `{{ f.p5.syn }}`       | {{ f.p5.tb }}  |
| 8 red-team     | adversary `{{ f.p8.adv_model }}` |                |                | n/a              | `{{ f.p8.syn }}`       | {{ f.p8.emp }} |

**Folder:** [`findings/{{ f.id }}/`](findings/{{ f.id }}/README.md) \xB7 **Provenance JSON:** [`findings/{{ f.id }}/provenance.json`](findings/{{ f.id }}/provenance.json)

**Dissent notes:**
{{#each f.dissent_notes as |d|}}- {{ d }}{{/each}}

---

{{/each}}

## Reading guide

- `UNANIMOUS` = all three jurors agreed on the same verdict at this pass.
- `MAJORITY` = 2-of-3 agreed; the third dissented. For HIGH/MEDIUM/LOW this promotes; dissent is recorded. For CRITICAL this triggers tiebreaker round 1.
- `TIEBREAKER round-1` = a fresh sub-worker on a rotated model family was asked to break the tie.
- `TIEBREAKER round-2` = a pair of sub-workers attempted empirical verification with a runtime harness.
- `NEEDS-CONTEXT` = the originating pass needed more context before verdicting; the orchestrator ran a context-recursion sub-worker.
- `DISPUTED-AFTER-ADVERSARIAL` = Pass 8 successfully disproved a previously-promoted finding. The finding remains in the report under the disputed section.
- `RED-TEAM-SURVIVED` = Pass 8 attempted disproof and could not. Highest confidence tier.
```

---

## STATUS.md 模板

在 \xA79 合并时渲染此骨架：

```markdown
# Status — deep security audit

> **NEVER UPLOAD.** All artifacts in this directory are local. Nothing was sent, filed, posted, or transmitted. Disclosure drafts under `findings/<id>/disclosure.md` are drafts only.

- **Target:** `{{ target }}`
- **Commit:** `{{ commit_sha }}`
- **Audit date:** `{{ audit_date }}`
- **Jury:** `{{ jury }}` (fallbacks: `{{ fallbacks }}`)
- **Severity floor for this report:** `{{ severity_floor }}`

## Counts by final confidence tier

| Tier               | Count                       |
| ------------------ | --------------------------- |
| RED-TEAM-SURVIVED  | {{ ct.red_team_survived }}  |
| UNANIMOUS          | {{ ct.unanimous }}          |
| MAJORITY           | {{ ct.majority }}           |
| VERIFIABLE-UNKNOWN | {{ ct.verifiable_unknown }} |
| DISPUTED           | {{ ct.disputed }}           |

## Counts by severity

| Severity | Promoted         | Disputed         | Verifiable-Unknown | Total            |
| -------- | ---------------- | ---------------- | ------------------ | ---------------- |
| CRITICAL | {{ sev.crit.p }} | {{ sev.crit.d }} | {{ sev.crit.vu }}  | {{ sev.crit.t }} |
| HIGH     | {{ sev.high.p }} | {{ sev.high.d }} | {{ sev.high.vu }}  | {{ sev.high.t }} |
| MEDIUM   | {{ sev.med.p }}  | {{ sev.med.d }}  | {{ sev.med.vu }}   | {{ sev.med.t }}  |
| LOW      | {{ sev.low.p }}  | {{ sev.low.d }}  | {{ sev.low.vu }}   | {{ sev.low.t }}  |
| INFO     | {{ sev.info.p }} | {{ sev.info.d }} | {{ sev.info.vu }}  | {{ sev.info.t }} |

## Findings (sorted: severity desc, final_confidence desc)

| ID                  | Title | Severity | Dataflow                               | Exploit       | Red-team         | Jury split                    | Dissent                | Folder                  |
| ------------------- | ----- | -------- | -------------------------------------- | ------------- | ---------------- | ----------------------------- | ---------------------- | ----------------------- | ------------------ | --------------------- | ------------------------------------------------------- |
| {{#each findings as | f     | }}       | [`{{ f.id }}`](FINDINGS.md#{{ f.id }}) | {{ f.title }} | {{ f.severity }} | {{ f.dataflow_reachability }} | {{ f.exploit_status }} | {{ f.red_team_status }} | {{ f.jury_split }} | {{ f.dissent_short }} | [`findings/{{ f.id }}/`](findings/{{ f.id }}/README.md) |

{{/each}}

## Judge progression

Current severity vs. original (lieutenant-proposed) severity, plus final verdict and sibling parent advisory when judge has run. Canonical source: [JUDGE.md](JUDGE.md) and each finding's `provenance.json[severity_shifts]` (see \xA75.8).

| ID                  | Severity (original → final) | Final verdict | Parent CVE (if SIBLING-OF-PRIOR)       |
| ------------------- | --------------------------- | ------------- | -------------------------------------- | -------------------------------------------------- | --------------------- | ----------------------------- |
| {{#each findings as | f                           | }}            | [`{{ f.id }}`](FINDINGS.md#{{ f.id }}) | {{ f.severity_original }} → {{ f.severity_final }} | {{ f.final_verdict }} | {{ f.parent_cve_if_sibling }} |

{{/each}}

## Verifiable-Unknown findings

These are findings where verdict could not be reached even after context recursion and (where attempted) empirical tiebreaker. They are kept in the report and tagged as `VERIFIABLE-UNKNOWN`.

{{#each vu_findings as |f|}}- [`{{ f.id }}`](FINDINGS.md#{{ f.id }}) — {{ f.title }} (reason: {{ f.vu_reason }}; see [`needs-context.md`](needs-context.md){{ f.id_anchor }}){{/each}}

## Per-finding folders

Every per-finding artifact (provenance, dataflow, exploit, ctx, disclosure, poc, evidence) lives under a single folder per finding. Open `findings/<id>/README.md` as the entry point.

{{#each findings as |f|}}- [`findings/{{ f.id }}/README.md`](findings/{{ f.id }}/README.md) — provenance: [`findings/{{ f.id }}/provenance.json`](findings/{{ f.id }}/provenance.json){{/each}}

## Pointers

- Narrative writeup: [FINDINGS.md](FINDINGS.md)
- Per-pass verdict tables: [JUDGE.md](JUDGE.md)
- Dashboard: [DASHBOARD.md](DASHBOARD.md)
- By severity: `by-severity/CRITICAL.md`, `HIGH.md`, `MEDIUM.md`, `LOW.md`, `INFO.md`, `ALL.md`, `INDEX.md`
- By area: `by-area/<area>.md`, `by-area/INDEX.md`
- Per-finding folders (local only): `findings/<id>/` (contains disclosure.md, dataflow.md, exploit.md, poc/, evidence/)

## Reminder

Nothing in this audit was uploaded. Disclosure is the human user's decision. The drafts under `findings/<id>/disclosure.md` are starting points; the user submits manually if and when they choose.
```
