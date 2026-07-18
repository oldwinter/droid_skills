# External Tool Dependencies

Some Droid skills depend on external CLI tools that are either bundled in the droid binary or must be installed separately.

## Bundled Tools (auto-resolved by droid)

These are npm dependencies embedded in the droid binary. Droid auto-resolves their paths at runtime.

| Tool | npm package | SubPath | Override Env Var |
|------|-------------|---------|------------------|
| **agent-browser** | `agent-browser@0.27.0` | `agent-browser/bin/agent-browser{platform}` | `FACTORY_AGENT_BROWSER_PATH` |
| **ripgrep (rg)** | `@vscode/ripgrep` | `@vscode/ripgrep/bin/rg` | `FACTORY_RIPGREP_PATH` |
| **keytar** | `keytar` (bundled) | `keytar/build/Release/keytar.node` | `FACTORY_KEYTAR_PATH` |
| **bun-pty** | `bun-pty@^0.4.8` | (Node module) | — |

### agent-browser

The `agent-browser` CLI drives Chrome/Chromium via CDP (Chrome DevTools Protocol). It runs in two modes:

**Desktop app (embedded pane):**
```bash
agent-browser --cdp "$AGENT_BROWSER_CDP" open <url>
```

**Headless (standalone):**
```bash
agent-browser open <url>
```

Key commands: `open`, `snapshot`, `click`, `type`, `eval`, `screenshot`, `errors`, `close`

See `automation/agent-browser.md` for full skill instructions.

## Install-on-Demand Tools

These are NOT bundled. Skills that need them include setup instructions.

### tuistory

A Playwright-like CLI framework for terminal UI testing.

**Install:**
```bash
which tuistory || (bun add -g tuistory || npm install -g tuistory)
```

**Skills that use it:**
- `automation/tuistory.md` — TUI testing skill
- `missions/tui-application-playbook.md` — TUI app mission playbook
- `qa/install-qa.md` — QA automation setup
- `wiki/wiki.md` — wiki generation Phase 3.5 (visual capture)

Key commands: `launch`, `snapshot`, `screenshot`, `type`, `press`, `click`, `wait-idle`, `close`

See `automation/tuistory.md` for full skill instructions.

## System Dependencies

These are expected to be available on the host system:

| Tool | Used by | Notes |
|------|---------|-------|
| `git` | Most skills | Standard on macOS/Linux |
| `curl` | install-qa, install-*, incident | Web requests |
| `bash` | Various skills | Shell scripting |
| `python3` | Various skills | Script execution |
| `node` | Various skills | JS runtime |
| `npm` / `bun` | Various skills | Package management |
| `gh` | install-code-review, install-wiki | GitHub CLI for PR creation |
| `xcodebuild` | install-qa (macOS) | Xcode build tool |

## Droid CLI Commands

Some skills invoke the `droid` CLI itself for sub-operations:

| Command | Used by |
|---------|---------|
| `droid wiki-read` | browse-wiki |
| `droid wiki-search` | browse-wiki |
| `droid wiki-upload` | wiki, install-wiki |
| `droid exec` | install-wiki, install-code-review, install-triage |
| `droid` | Various skills (self-referential) |

## Dep Resolution Mechanism

Droid uses a layered dependency resolution system:

1. **Per-dep env var override** — e.g., `FACTORY_AGENT_BROWSER_PATH`
2. **Global npm modules dir** — `FACTORY_NPM_MODULES_DIR`  
3. **Bundled in binary** — embedded via Bun's `bunfs` at compile time
4. **System PATH** — fallback to standard system resolution
