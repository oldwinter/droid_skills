# 外部工具依赖

某些 Droid skill 依赖于外部 CLI 工具，这些工具要么被打包在 droid 二进制文件中，要么需要单独安装。

## 打包工具（由 droid 自动解析）

这些是嵌入在 droid 二进制文件中的 npm 依赖项。Droid 在运行时会自动解析它们的路径。

| 工具 | npm 包 | 子路径 | 覆盖环境变量 |
|------|-------------|---------|------------------|
| **agent-browser** | `agent-browser@0.27.0` | `agent-browser/bin/agent-browser{platform}` | `FACTORY_AGENT_BROWSER_PATH` |
| **ripgrep (rg)** | `@vscode/ripgrep` | `@vscode/ripgrep/bin/rg` | `FACTORY_RIPGREP_PATH` |
| **keytar** | `keytar` (打包) | `keytar/build/Release/keytar.node` | `FACTORY_KEYTAR_PATH` |
| **bun-pty** | `bun-pty@^0.4.8` | (Node 模块) | — |

### agent-browser

`agent-browser` CLI 通过 CDP（Chrome DevTools 协议）驱动 Chrome/Chromium。它支持两种运行模式：

**桌面应用（嵌入式面板）:**
```bash
agent-browser --cdp "$AGENT_BROWSER_CDP" open <url>
```

**无头模式（独立运行）:**
```bash
agent-browser open <url>
```

关键命令: `open`, `snapshot`, `click`, `type`, `eval`, `screenshot`, `errors`, `close`

请参见`automation/agent-browser.md`以获取完整的 skill 说明。

## 按需安装工具

这些不会被打包。需要它们的 skill 包括设置说明。

### tuistory

一个类似于 Playwright 的 CLI 框架，用于终端 UI 测试。

**安装:**
```bash
which tuistory || (bun add -g tuistory || npm install -g tuistory)
```

**使用它的 skill：**
- `automation/tuistory.md` — TUI 测试 skill
- `missions/tui-application-playbook.md` — TUI 应用任务手册
- `qa/install-qa.md` — 质量保证自动化设置
- `wiki/wiki.md` — Wiki 生成 Phase 3.5 (视觉捕获)

重要命令：`launch`, `snapshot`, `screenshot`, `type`, `press`, `click`, `wait-idle`, `close`

请参见 `automation/tuistory.md` 获取完整 skill 说明。

## 系统依赖项

这些预计会在主机系统上可用：

| 工具 | 由...使用 | 备注 |
|------|---------|-------|
| `git` | 大多数 skill | 标准在 macOS/Linux 上 |
| `curl` | install-qa, install-*, incident | 网络请求 |
| `bash` | 各种 skill | shell 脚本 |
| `python3` | 各种 skill | 脚本执行 |
| `node` | 各种 skill | JS 运行时 |
| `npm` / `bun` | 各种 skill | 包管理 |
| `gh` | install-code-review, install-wiki | GitHub CLI 用于 PR 创建 |
| `xcodebuild` | install-qa (macOS) | Xcode 构建工具 |

## Droid 命令行指令

一些 skill 调用`droid` CLI 本身进行子操作：

| 命令 | 由...使用 |
|---------|---------|
| `droid wiki-read` | browse-wiki |
| `droid wiki-search` | browse-wiki |
| `droid wiki-upload` | wiki, install-wiki |
| `droid exec` | install-wiki, install-code-review, install-triage |
| `droid` | 各种 skill（自指性） |

## 依赖解析机制

Droid 使用分层的依赖解析系统：

1. **Per-dep 环境变量覆盖** — 例如，`FACTORY_AGENT_BROWSER_PATH`
2. **全局 npm 模块目录** — `FACTORY_NPM_MODULES_DIR`
3. **内置在二进制文件中** — 通过 Bun 的 `bunfs` 在编译时嵌入
4. **系统 PATH** — 回退到标准系统的解析
