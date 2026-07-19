---
name: incident
description: 根因分析 (RCA) 作业手册。给定一个警报链接（或提示用户提供一个），识别警报类型，验证工具/认证，并通过深入研究逐步进行根本原因分析。将所学内容保存到事故指南中以供将来重用。
user-invocable: true
---

# 事故响应

**重要：**这是一个内置 skill，其内容已在上下文中。如果本文件末尾的可观测性工具参考表未完整显示，请询问用户涉及哪些可观测性工具，然后继续。当给出的告警链接需要认证或 FetchUrl 失败时，暂时**不要**要求用户粘贴告警文本，应先安装所需工具并完成认证。

## 如何使用

```
/incident <alert-link>
```

如果没有提供警报链接，请向用户提供一个。

## 工作流

### 步骤 0：检查现有指南

1. 使用 skill 工具调用 `incident-guidelines`
2. 如果找到了 skill，解析告警（步骤1），检查是否与指导原则中的已知告警类型匹配。
   - **找到匹配**：遵循该告警类型的文档工具/接口/认证/仓库。验证先决条件（步骤2），然后进行根本原因分析（步骤3）。
   - **未找到匹配**：按照不存在指导原则的情况进行完整发现（步骤1-3）
3. 如果找不到 skill（尚未存在），则按照不存在指导原则的情况进行完整发现（步骤1-3）

### 步骤1：获取并分类告警（工具优先）

1. 使用 FetchUrl 从提供的链接（通常是 Slack 消息）检索告警内容
2. 如果 FetchUrl 失败或链接需要认证，请根据 URL/域名推断平台，从可观测性工具参考中选择首选接口（CLI > API > MCP），并**在要求用户手动粘贴之前**进入步骤2 完成安装/认证。
3. 一旦获取到工具访问权限，通过工具/API 检索告警详情，然后解析告警以识别：
   - 哪些可观测性工具生成或引用了该告警
   - 错误消息、受影响组件、严重程度和解决状态
   - 任何运行 ID、作业名称、时间戳、服务名或响应者信息
4. 确定需要从可观测性工具参考表（文件末尾）中哪些工具进行调查
5. 只有在用户明确拒绝工具安装/授权或工具无法访问数据时，才请用户粘贴警报文本/详情。

### 步骤 2：验证先决条件（安装/授权后手动粘贴）

在提示用户之前，请参阅可观测性工具参考表以选择首选界面和授权方法。

**2.1 工具可用性（尚未进行授权）**

- 运行 `which <cli>` 或 `<cli> --version` 检查 CLIs 是否已安装
- 通过查找具有预期前缀的工具名称来检查当前会话中是否包含相关 MCP 工具（例如，对于 Sentry MCP 为 `sentry___*`，对于 Datadog MCP 为 `datadog___*`）
- 如果缺失，请询问用户是否要安装首选界面（根据表格列出首选项）
- 如果批准，则验证版本

**2.2 授权（在工具存在之后）**

- 使用 `echo "\${VAR:+set}"` 检查环境变量
- 运行可观测性工具参考表中的文档化测试命令
- 如果没有找到现有凭据，请仅使用 AskUser 提示词进行授权设置

> **警告：**如果任何必需的工具未安装或未认证，请告知用户在没有这些工具的情况下继续将导致 RCA 不准确或不完整。强烈建议在继续之前安装并完成认证。如果用户拒绝，继续但明确注明此限制。

**授权选择规则：**

- 如果一个工具具有多个接口（例如，命令行界面和 MCP），使用 AskUser 让用户选择。优先列出首选的接口（根据表格中的“首选？”列）。
- 当平台有单一的命令行界面时，倾向于使用 CLI。
- 对于认证，使用 AskUser 让用户选择他们的认证方法。优先列出持久化认证作为推荐的选择，然后是临时选项。如果有多个临时方法（例如，基于浏览器 vs. 设备码），请先列出设备码，因为它不需要本地浏览器。
- 不要请求长期令牌或 API 密钥。例外情况：OAuth 设备码或远程启动响应可能仅需粘贴一次以完成认证。如果响应包括访问/刷新令牌（或 JWT），则应中止并使用更安全的方法重新开始。使用 AskUser 让他们选择认证方法，然后给出设置说明作为助手消息，并通过运行测试命令验证认证。
- 如果需要 Slack：检查可观测性工具参考表中的认证方法。

**仓库发现：**

- 如果警报类型在事件指南中被找到，请使用该处列出的仓库——除非看起来有问题，否则无需再次与用户确认。
- 如果这是一个新的警报类型（没有匹配的指南），你必须在提示用户之前搜索仓库。首先，在本地文件系统中搜索相关仓库，并使用 `gh repo list` / `glab project list` 发现组织中的仓库。只有在收集了候选者之后，通过 AskUser 向用户展示你的发现，请他们确认哪些是相关的并添加任何遗漏的仓库。在仓库列表被确认之前，不要展示任何根本原因分析（RCA）。
- 克隆任何尚未在文件系统上的仓库
- 对代码库进行深入搜索以理解 RCA 流程——首先阅读 repo(s) 中的 AGENTS.md 和 README 文件，然后从错误跟踪到仪器化、路由处理程序和依赖调用

### 步骤 3：调查并呈现 RCA

使用验证过的工具和仓库进行深入研究以确定根本原因。不要遵循固定的脚本——利用这些工具查询日志、指标、跟踪和代码来建立全面的理解。

向用户展示 RCA 包括：

- 具体的错误及其原因
- 为什么会发生（促成因素）
- 失败模式（间歇性 vs 一致，频率）
- 影响范围
- 建议的修复方案

与用户迭代直到他们对 RCA 满意为止。

### 步骤 4: 持久化指导方针

在用户确认 RCA 正确后，只有当调查产生了值得重用的有意义发现（例如，新的工具/认证/仓库映射、非显而易见的陷阱）时才继续持久化指导方针。如果是这样，请询问他们是否希望将警报类型映射保存为可重复使用的指导方针，以便未来此类警报可以进行 RCA 而无需从头开始重新发现。否则，跳过此步骤。

如果回答是:

1. 如果`incident-guidelines`skill 尚不存在，则使用 AskUser 询问是否在项目级别（仓库中的`.factory/skills/incident-guidelines/`，与队友共享）或用户级别（`~/.factory/skills/incident-guidelines/`，个人且跨项目）编写它
2. 创建或更新`incident-guidelines/SKILL.md`文件
3. 指导方针条目应简洁——列出警报类型名称、所需工具/接口/认证方法、仓库以及在调查过程中发现的任何通用陷阱
4. 不要包含内联 bash 脚本、硬编码的 API URL、账户 ID、步骤命令或特定于所调查警报的 RCA 发现
5. 陷阱应该是有助于未来相同警报类型的调查（例如，认证怪癖、工具特定的陷阱、非显而易见的配置要求，在哪个工具中查询哪个数据集/表）的事情
6. 不要在指导方针文件中包含敏感数据（API 密钥、令牌、秘密）

如果指导方针文件已经存在且警报匹配现有类型，则仅在此次 RCA 揭示了新的有意义陷阱或修正未被捕捉时提示词用户更新条目。否则，跳过任何新指导方针的持久化

incident-guidelinesskill 应具有以下 frontmatter:

```yaml
---
name: incident-guidelines
description: Learned alert type mappings from /incident runs. Maps alert types to required tools, interfaces, auth methods, repos, and gotchas for faster RCA on recurring alert patterns.
user-invocable: false
---
```

---

## 可观测性工具参考

这张表格是非详尽的可观测性工具参考。不要为列表中的每个工具安装接口——只需安装并验证特定警报所需的工具。表格是查找所需工具的接口和认证方法的指南。

首选顺序为 CLI > API > MCP。所有持久化认证方法都是无头的。

临时授权注解：

- `[headless]` = 仅终端，无需浏览器
- `[browser]` = 需要在本地机器上打开浏览器
- `[device-code]` = 在终端中打印 URL + 代码，无需本地浏览器。运行命令并展示输出给用户——其中包含他们可以在任何设备上完成认证的 URL 和代码。
- `[remote-bootstrap]` = 两步无头流程，需要持久化进程。每次调用都会生成一个唯一的 PKCE 状态，因此您必须保持原始进程存活——不要两次运行该命令或将其管道到新进程中。步骤如下：
  1. 编写一个 Python 脚本（仅使用标准库，无需 pip 安装）使用 `subprocess.Popen(stdin=subprocess.PIPE, stdout=subprocess.PIPE, env={...,'PYTHONUNBUFFERED':'1'})`
  2. 逐字符读取 stdout 使用 `p.stdout.read(1)` 直到提示词出现
  3. 从输出中提取启动命令并通过 AskUser 展示给用户——他们在有浏览器的机器上运行它并粘贴回输出
  4. 使用 `p.stdin.write(response + '\n'); p.stdin.flush()` 传递响应

| 工具                          | 接口                      | 首选？ | 持久认证 `[headless]`                                                                                                    | 临时认证                                                        |
| ----------------------------- | ------------------------------ | :--------: | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Slack（读取话题/消息） | Factory 集成 (FetchUrl) |    是     | 预配置在 https://app.factory.ai/settings/integrations. 使用 FetchUrl 获取 Slack 链接；仅在失败时提示词连接 | 无                                                                  |
| Sentry                        | CLI (`sentry`)                 |    是     | `SENTRY_AUTH_TOKEN`                                                                                                             | `sentry auth login` `[device-code]`                                   |
| Sentry                        | MCP (`sentry-mcp`)             |     否     | `SENTRY_AUTH_TOKEN` (stdio 传输)                                                                                           | MCP OAuth 2.0 `[browser]` (云传输)                           |
| Datadog                       | API                            |    是     | `DD-API-KEY` + `DD-APPLICATION-KEY` 头部                                                                                     | 无                                                                  |
| Datadog                       | MCP                            |     否     | `DD_API_KEY`+`DD_APP_KEY`                                                                                                       | MCP OAuth 2.0 `[browser]`                                             |
| AWS                           | CLI (`aws`)                    |    是     | `AWS_ACCESS_KEY_ID`+`AWS_SECRET_ACCESS_KEY`                                                                                     | `aws sso login` `[browser]` / `--no-browser` `[device-code]`          |
| GCP                           | CLI (`gcloud`/`bq`)            |    是     | `GOOGLE_APPLICATION_CREDENTIALS` (SA key JSON)                                                                                  | `gcloud auth login` `[browser]` / `--no-browser` `[remote-bootstrap]` |
| Grafana                       | API                            |    是     | `Authorization: Bearer <sa-token>`                                                                                              | 无                                                                  |
| Grafana                       | MCP (`mcp-grafana`)            |     否     | `GRAFANA_SERVICE_ACCOUNT_TOKEN` (+ `GRAFANA_URL`)                                                                               | 无                                                                  |
| Elasticsearch                 | API                            |    是     | `Authorization: ApiKey <base64>` 或 Basic Auth                                                                                  | 无                                                                  |
| Elasticsearch                 | MCP                            |     否     | `ES_API_KEY` / `ELASTICSEARCH_USERNAME`+`PASSWORD`                                                                              | 无                                                                  |
| PagerDuty                     | CLI (`pd`)                     |    是     | `pd auth:set --token <token>`                                                                                                   | `pd auth:web` `[browser]`                                             |
| PagerDuty                     | MCP                            |     否     | `PAGERDUTY_API_TOKEN`                                                                                                           | 无                                                                  |
| Prometheus                    | CLI (`promtool`)               |    是     | Bearer 令牌/基本认证通过`--http.config.file` YAML                                                                         | 无                                                                  |
| Splunk（本地部署）              | CLI (`splunk`)                 |    是     | Auth Token via `-token` 标志                                                                                                    | `splunk login` (user/pass 提示词) `[headless]`                        |
| Splunk (Cloud)                | API                            |    是     | `Authorization: Bearer <token>`                                                                                                 | 无                                                                  |
| Splunk (Cloud)                | MCP                            |     否     | `SPLUNK_TOKEN` + `SPLUNK_URL`                                                                                                   | 无                                                                  |
| New Relic                     | CLI (`newrelic`)               |    是     | 通过 `NEW_RELIC_API_KEY` 设置 `newrelic profile add`                                                                                  | 无                                                                  |
| New Relic                     | MCP                            |     否     | `NEW_RELIC_API_KEY` + `NEW_RELIC_ACCOUNT_ID`                                                                                    | 无                                                                  |
| Loki                          | CLI (`logcli`)                 |    是     | `LOKI_BEARER_TOKEN` / `LOKI_USERNAME`+`LOKI_PASSWORD`                                                                           | 无                                                                  |
| Dynatrace                     | API                            |    是     | `Authorization: Api-Token <token>`                                                                                              | 无                                                                  |
| Dynatrace                     | MCP                            |     否     | `DT_API_TOKEN` / `DT_CLIENT_ID`+`DT_CLIENT_SECRET`                                                                              | MCP OAuth `[browser]`                                                 |
| Axiom                         | CLI (`axiom`)                  |    是     | `AXIOM_TOKEN`                                                                                                                   | `axiom auth login` `[browser]`                                        |
| Axiom                         | MCP (`mcp.axiom.co`)           |     否     | `AXIOM_TOKEN`                                                                                                                   | 无                                                                  |
| Databricks                    | CLI (`databricks`)             |    是     | `DATABRICKS_TOKEN` / `DATABRICKS_CLIENT_ID`+`SECRET`                                                                            | `databricks auth login` `[browser]`                                   |
| Opsgenie                      | API                            |    是     | `Authorization: GenieKey <key>`                                                                                                 | 无                                                                  |
| 蜂窝                     | API                            |    是     | `X-Honeycomb-Team: <api-key>`                                                                                                   | 无                                                                  |
| 蜂窝                     | MCP                            |     否     | `HONEYCOMB_API_KEY`                                                                                                             | MCP OAuth 2.0 `[browser]`                                             |
| 雪崩                     | CLI (`snowsql`/`snow`)         |    是     | 密钥对（`private_key_path`） / `SNOWSQL_PWD`                                                                                   | `--authenticator externalbrowser` `[browser]`                         |
| Jaeger                        | API                            |    是     | 无内置认证（依赖反向代理）                                                                                      | 无                                                                  |
| Bugsnag                       | API                            |    是     | `Authorization: token <token>`                                                                                                  | 无                                                                  |
| Sumo Logic                    | API                            |    是     | HTTP Basic 认证（`accessId:accessKey`）                                                                                          | 无                                                                  |
| Rollbar                       | API                            |    是     | `X-Rollbar-Access-Token` 头部                                                                                                 | 无                                                                  |
| incident.io                   | API                            |    是     | `Authorization: Bearer <api-key>`                                                                                               | 无                                                                  |
| incident.io                   | MCP                            |     否     | `INCIDENT_IO_API_KEY`                                                                                                           | MCP OAuth 2.0 `[browser]`                                             |
| Rootly                        | API                            |    是     | `Authorization: Bearer <token>`                                                                                                 | 无                                                                  |
| Rootly                        | MCP                            |     否     | `ROOTLY_API_TOKEN`                                                                                                              | 无                                                                  |
| Betterstack                   | API                            |    是     | `Authorization: Bearer <token>`                                                                                                 | 无                                                                  |
| Betterstack                   | MCP                            |     否     | `BETTER_STACK_API_TOKEN`                                                                                                        | 无                                                                  |
| Papertrail                    | CLI (`papertrail`)             |    是     | `PAPERTRAIL_API_TOKEN`                                                                                                          | 无                                                                  |
| 胡狼蜂蜜                   | 命令行工具 (`hb`)                     |    是     | `HONEYBADGER_PERSONAL_AUTH_TOKEN` / `HONEYBADGER_API_KEY`                                                                       | 无                                                                  |
| 胡狼蜂蜜                   | MCP                            |     否     | `HONEYBADGER_PERSONAL_AUTH_TOKEN`                                                                                               | 无                                                                  |
| Zipkin                        | API                            |    是     | 无内置认证（依赖反向代理）                                                                                      | 无                                                                  |
| FireHydrant                   | API                            |    是     | `Authorization: Bearer <token>`                                                                                                 | 无                                                                  |
| Statuspage                    | API                            |    是     | `Authorization: OAuth <key>`                                                                                                    | 无                                                                  |
| Lightstep                     | API                            |    是     | `Authorization: Bearer <key>`                                                                                                   | 无                                                                  |
| VictorOps                     | API                            |    是     | `X-VO-Api-Key`+`X-VO-Api-Id`                                                                                                    | 无                                                                  |
