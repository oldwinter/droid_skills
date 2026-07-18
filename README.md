# Droid Built-in Addins

Extracted from the `droid` CLI binary (`/opt/homebrew/bin/droid`, Mach-O arm64).

Total: **23 extracted skills** across 9 categories.

## Category Breakdown

### automation/
Browser, terminal, and desktop automation skills.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `agent-browser.md` | 19 KB | 500 | Automates browsers & Electron apps (VS Code, Slack, Discord, Figma, Notion, Spotify) via Chrome DevTools Protocol |
| `tuistory.md` | 14 KB | 293 | Playwright-like framework for TUI testing — deterministic launch, key input, resize checks, evidence capture |
| `figma-mcp-helper.md` | 26 KB | 57 | Promotes Figma MCP integration — detects Figma URLs/images and guides installation |

### documents/
Office document generation skills.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `excel.md` | 7 KB | 156 | Produce polished Excel spreadsheets (.xlsx) |
| `pdf-document.md` | 4 KB | 106 | Produce polished PDF documents (reports, invoices, resumes, letters) |
| `powerpoint.md` | 4 KB | 114 | Produce polished PowerPoint presentations (decks, pitch decks) |

### incident/
Incident response and RCA skills.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `incident.md` | 24 KB | 180 | RCA runbook for alerts — identifies alert type, verifies tooling/auth, walks through root cause analysis |

### installers/
CI/CD setup and installation skills.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `install-code-review.md` | 51 KB | 1025 | Install automated code review on GitHub/GitLab (single repo or org-wide) |
| `install-triage.md` | 21 KB | 267 | Scaffold scheduled Slack triage automation bot |
| `install-wiki.md` | 4 KB | 118 | Install CI action that auto-refreshes wiki on every push |

### missions/
Factory Missions orchestration skills (planning, worker definition, playbooks).

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `mission-planning.md` | 116 KB | 1153 | Guides the orchestrator through the planning phase with the user |
| `define-mission-skills.md` | 93 KB | 856 | Guides the orchestrator through designing worker types and their skills |
| `refactoring-playbook.md` | 37 KB | 351 | Playbook for code modernization, architecture migrations, large-scale refactoring |
| `tui-application-playbook.md` | 30 KB | 148 | Playbook for TUI application missions — CLI tools with interactive interfaces |

### qa/
Quality assurance setup and automation.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `install-qa.md` | 43 KB | 771 | Set up automated QA testing with modular sub-skills, CI workflow, and report template |

### review/
Code review and analysis skills.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `review.md` | 17 KB | 298 | Review code changes and identify high-confidence, actionable bugs |
| `security-review.md` | 27 KB | 365 | Security-focused code review using STRIDE, OWASP Top 10, OWASP LLM Top 10, supply chain analysis |
| `deep-security-review.md` | 187 KB | 2754 | Correctness-first, depth-first security audit with heterogeneous multi-model jury, 3-pass floor, conditional escalation tier |
| `simplify.md` | 4 KB | 53 | Review changed code for reuse, quality, and efficiency, then fix issues found |

### session/
Session management and navigation.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `session-navigation.md` | 4 KB | 122 | Navigate, search, and manage Droid sessions — list, search history, resume, get details |

### wiki/
AutoWiki generation, browsing, and video skills.

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `wiki.md` | 79 KB | 1410 | Generate comprehensive codebase documentation (full generation pipeline with sub-agent delegation) |
| `wiki-video-gen.md` | 22 KB | 430 | Generate Factory-branded HyperFrames video overviews for repository wikis |
| `browse-wiki.md` | 6 KB | 148 | Search and read wiki documentation — `droid wiki-read` / `droid wiki-search` commands |

---

## External Dependencies

Some skills depend on external CLI tools. See **[dependencies.md](dependencies.md)** for the full list including bundled tools (`agent-browser`, `ripgrep`) and install-on-demand tools (`tuistory`).

The `tools/` directory contains the LLM function-calling schema for `agent_browser` — the only built-in tool stored in Anthropic-style JSON function definition format. Core tools (Read, Edit, Execute, etc.) are defined programmatically in TypeScript, not as embedded JSON.

---

## Not Extractable (Programmatic / Background)

These are mentioned in system reminders as available skills but are **not stored as standalone YAML skill definitions** in the binary. They may be defined programmatically, bundled within other skills, or generated dynamically.

### droid-control workflow skills (not invoked directly)

These are background skills that support the `droid-control` automation skill:

- `droid-control` — Control terminal TUIs and web/Electron apps for testing, demos, QA, and computer-use tasks
- `capture` — Recording lifecycle for terminal and browser sessions
- `verify` — Deliverable verification against commitments
- `droid-cli` — Droid CLI target patterns, shortcuts, modes, and launch helpers
- `compose` — Video assembly via Remotion — title cards, layout, transitions, effects
- `pty-capture` — Capture ground-truth byte sequences from real terminal emulators
- `desktop-control` — Desktop-control driver mechanics for native GUI app automation via trycua cua-driver
- `showcase` — Visual polish for videos via Remotion-powered window chrome, animations, branded backgrounds
- `true-input` — True-input driver mechanics for real terminal emulator automation via headless Wayland compositor

### Other non-extractable skills

- `handoff` — Compact the current conversation into a handoff document for another agent to pick up
- `grill-with-docs` — Grilling session that challenges your plan against the existing domain model

### Custom droids (sub-agents)

These are custom droid configurations stored in `.factory/droids/` or `~/.factory/droids/`, not built into the binary:

- `worker` — General-purpose worker droid for delegating tasks
- `scrutiny-feature-reviewer` — Code review for a single feature during mission validation
- `user-testing-flow-validator` — Test validation contract assertions through designated contract surfaces

---

## Extraction Method

Skills were extracted from the `droid` binary by:

1. **Template-literal format** (16 skills): `var <X>=`---\nname: <name>\n...`;var <NEXT>`
   - Found by searching for `var <X>=`---` byte pattern
   - Boundaries determined by next variable assignment in JS bundle

2. **Escaped string format** (1 skill): `var _si="---\nname: browse-wiki\n...";var Bsi=...`
   - Found by searching for `"---\nname: browse-wiki`

3. **JSON metadata + variable reference** (6 skills): `{metadata:{name:"<name>",description:"..."},systemPrompt:<VAR>}`
   - Resolved the `<VAR>` reference to its template-literal assignment elsewhere in the bundle
