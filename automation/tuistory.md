---
name: tuistory
description: 自动化终端用户界面（TUI）测试。在需要启动、交互、测试或调试终端应用程序、捕获 TUI 快照或自动化终端输入时使用此功能。
---

# 使用 tuistory 进行 TUI 测试

tuistory 是一个类似于 Playwright 的框架，用于终端 UI。使用它进行确定性启动、按键输入、尺寸检查和证据捕获。

## 设置

确保 tuistory 可用：
```bash
which tuistory || (bun add -g tuistory || npm install -g tuistory)
tuistory --version
```

在使用高级标志之前，请检查已安装版本的命令界面:
```bash
tuistory --help
tuistory snapshot --help
tuistory screenshot --help
```

## 核心工作流（可靠路径）

1. 启动一个命名会话。
2. 等待空闲状态，然后快照。
3. 立即处理首次运行对话框。
4. 针对特定文本使用短而精确的等待。
5. 每次操作后进行快照。
6. 捕获屏幕截图作为视觉证明。
7. 完成时关闭会话。

```bash
tuistory launch "my-tui-command" -s app --cols 110 --rows 32
tuistory -s app wait-idle --timeout 8000
tuistory -s app snapshot --trim

# interact
tuistory -s app type "help"
tuistory -s app press enter
tuistory -s app wait "Usage" --timeout 8000
tuistory -s app snapshot --trim

# capture visual artifact
tuistory -s app screenshot --format png -o /tmp/app-usage.png

# cleanup
tuistory -s app close
```

## 关键输入规则（至关重要）

- 使用空格分隔的关键令牌，而不是引号组合键。
- 正确：`tuistory -s app press ctrl g`
- 错误：`tuistory -s app press "ctrl g"`
- 使用 `type` 用于文本和 `press` 用于控制/导航键。

常用按键：
```bash
tuistory -s app press enter
tuistory -s app press esc
tuistory -s app press ctrl c
tuistory -s app press ctrl g
```

## 等待策略（避免不稳定的长时间睡眠）

- 在触发重绘的交互后，优先使用 `wait-idle`。
- 对于异步里程碑，请优先使用 `wait <pattern>`。
- 保持超时限定且具上下文性（大多数互动步骤为 3s-20s）。
- 避免盲目长时间等待，除非绝对必要。

推荐的循环流程：
```bash
tuistory -s app press enter
tuistory -s app wait-idle --timeout 3000
tuistory -s app snapshot --trim
```

## Factory 特殊坑点（重要）

- 优先使用 `droid-dev` 进行本地 CLI 验证。在某些环境中，如果包装工具不可用，则 `bun run dev` 可能会失败。
- 确保守护进程 + CLI 部署环境匹配（例如 `NODE_ENV/NEXT_ENV/FACTORY_ENV/FACTORY_DEPLOYMENT_ENV=development`）。
- 启动提示词可能会阻塞流程（例如 VSCode 扩展安装）。早期检测并处理它们。
- 保持每个动作原子化：输入 -> 等待空闲/等待 -> 截图。

## Factory CLI PR 验证手册（已知良好）

在 factory-mono 中验证 CLI/TUI PR 时：

1. 确保开发守护进程正在运行且带有 dev 环境变量。
2. 使用命名会话和显式环境在启动命令中启动 CLI。
3. 立即截图并解决启动提示词（例如 VSCode 扩展提示词）。
4. 使用确定性的按键导航到目标 UI 状态。
5. 运行一个缩放矩阵并捕获文本快照和屏幕截图。
6. 如需，则修改本地测试固定文件以诱导错误/边界状态。

在重新启动重用的会话名称之前，清理过期会话：
```bash
tuistory -s prcheck close >/dev/null 2>&1 || true
tuistory sessions
```

示例模式：
```bash
# Start daemon separately (example)
NODE_ENV=development NEXT_ENV=development FACTORY_ENV=development FACTORY_DEPLOYMENT_ENV=development factoryd-dev

# Launch CLI test session (portable, explicit cwd/env)
tuistory launch "droid-dev --resume <session-id>"   -s prcheck   --cwd /path/to/apps/cli   --env NODE_ENV=development   --env NEXT_ENV=development   --env FACTORY_ENV=development   --env FACTORY_DEPLOYMENT_ENV=development   --cols 110 --rows 32

# Handle prompt and verify baseline
tuistory -s prcheck wait-idle --timeout 8000
tuistory -s prcheck snapshot --trim

# Open target view and verify
tuistory -s prcheck press ctrl g
tuistory -s prcheck wait "Mission Control" --timeout 10000
tuistory -s prcheck snapshot --trim

# Resize matrix
tuistory -s prcheck resize 90 28
tuistory -s prcheck wait-idle --timeout 3000
tuistory -s prcheck screenshot --format png -o /tmp/prcheck-90x28.png
tuistory -s prcheck resize 120 40
tuistory -s prcheck wait-idle --timeout 3000
tuistory -s prcheck screenshot --format png -o /tmp/prcheck-120x40.png
tuistory -s prcheck resize 70 22
tuistory -s prcheck wait-idle --timeout 3000
tuistory -s prcheck screenshot --format png -o /tmp/prcheck-70x22.png
```

注意：shell 样式的启动字符串（例如 `cd ... && ...`）可能有效，但 `--cwd` + `--env` 更清晰且更具移植性。

## 捕获制品

使用文本和图像制品：

```bash
tuistory -s app snapshot --trim > /tmp/state.txt
tuistory -s app screenshot --format png -o /tmp/state.png
```

为了制作一个轻量级演示视频，可以使用 ffmpeg 缝合屏幕截图：
```bash
# frames.txt format:
# file '/tmp/frame-01.png'
# duration 1.0
# ...
ffmpeg -y -f concat -safe 0 -i /tmp/frames.txt -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p" /tmp/demo.mp4
```

将制品保存在一个目录中以便你可以给用户提供单一路径。

## 故障排除

### 会话无法达到预期状态

- 立即捕获快照并检查当前 UI。
- 检查阻碍导航的模态/提示词文本。
- 使用增量操作：按键 -> 等待空闲 -> 捕获快照。

### 命令似乎没有执行任何操作

- 确认键语法（以空格分隔的和弦标记）。
- 通过 `tuistory sessions` 确认会话名称是否正确。
- 在重新尝试之前，使用 `snapshot` 重新检查当前活动命令。

### 渲染检查结果不明确

- 使用 `screenshot` 而不只是文本快照。
- 测试多种尺寸（小/中/大）并比较边框对齐方式。

## 命令参考（当前）

```bash
tuistory launch <command>
tuistory snapshot
tuistory screenshot
tuistory type <text>
tuistory press <key> [...keys]
tuistory click <pattern>
tuistory click-at <x> <y>
tuistory wait <pattern>
tuistory wait-idle
tuistory scroll <up|down> [lines]
tuistory resize <cols> <rows>
tuistory capture-frames <key> [...keys]
tuistory close
tuistory sessions
tuistory logfile
```
