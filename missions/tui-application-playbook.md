---
name: tui-application-playbook
description: 终端用户界面 (TUI) 应用程序任务手册。为执行 TUI 应用程序任务提供指导，包括执行、里程碑和验证策略
---

# TUI 应用程序任务手册

此手册将引导您完成执行终端用户界面 (TUI) 应用程序任务的过程。适用于具有交互式界面的 CLI 工具、终端仪表板、文本编辑器和其他在终端中呈现的项目

## 里程碑策略：垂直切片

将您的里程碑结构化为 **功能性的垂直切片**，而不是水平层

**良好的里程碑:**
- "navigation"（菜单系统、视图、快捷键 - 全栈）
- "data-display"（列表视图、详细视图、格式化 - 全栈）
- "editing"（输入处理、验证、持久化 - 全栈）

**不良里程碑：**
- "all-keybindings"（水平 - 无法单独测试）
- "rendering-layer"（水平 - 无法在没有数据/状态的情况下测试）

每个里程碑应使应用处于一个连贯且可测试的状态，用户可以完成有意义的操作流程。

## TUI 的工作类型

### tui-worker

- 实现 TUI 功能（视图、组件、输入处理、状态）
- **TDD: 先写测试（在任何实现之前）**
- **必须使用 tuistory 进行手动 TUI 验证：**
  - 启动应用，导航到相关视图，并验证渲染和交互
  - 使用 `tuistory snapshot --trim` 捕获终端输出并验证视觉正确性
  - 测试键盘交互 (`tuistory press <key>`), 输入处理 (`tuistory type "<text>"`)
  - 检查渲染伪影、对齐问题、溢出以及缺失状态
- **修复发现的问题：**
  - 自己工作中的问题（包括手动测试中发现的）→ 必须修复
  - 在其 skill 范围内的可管理现有问题 → 修复它们
  - 涉及较大范围或超出其 skill 的问题 → 报告给协调者
  - 将任何修复包含在 whatWasImplemented 中

### backend-worker

- 实现 TUI 消费的数据层、服务和业务逻辑
- **TDD: 先写测试（在任何实现之前）**
- 验证实际行为（而不仅仅是测试通过）
- **修复发现的问题：**
  - 自己工作中的问题（包括手动测试中发现的）→ 必须修复
  - 在其 skill 范围内的可管理现有问题 → 修复它们
  - 涉及较大范围或超出其 skill 的问题 → 报告给协调者
  - 将任何修复包含在 whatWasImplemented 中

## 质量执行流程

```text
1. Orchestrator creates implementation features grouped by milestone
2. Implementation workers build features (TDD + manual verification via tuistory)
3. When milestone X completes → system injects scrutiny and user-testing validators for the milestone
4. Failed validation surfaces bugs → orchestrator creates fix features
5. Repeat until milestone passes, then move to next milestone
```

### 示例 TUI 验证流程

```bash
# Launch the app
tuistory launch "node ./dist/cli.js" -s myapp --cols 120 --rows 40

# Wait for startup
tuistory -s myapp wait "Ready" --timeout 15000

# Navigate to the view under test
tuistory -s myapp press tab
tuistory -s myapp snapshot --trim   # verify navigation state

# Test a specific interaction
tuistory -s myapp type "search query"
tuistory -s myapp press enter
tuistory -s myapp wait "Results" --timeout 10000
tuistory -s myapp snapshot --trim   # verify results rendered correctly

# Clean up
tuistory -s myapp close
```

## 常见陷阱

1. **不构建状态管理而直接处理 UI** - 这会导致数据结构不符合渲染需求。应按垂直切片构建。

2. **忘记边缘状态** - worker 通常只实现正常路径。expectedBehavior 应包括空状态、错误状态、溢出/截断以及缩放处理。

3. **未测试键盘交互** - TUI 应用程序是通过键盘驱动的。每个视图都需要测试其快捷键，包括边缘情况（快速输入、冲突的快捷方式）。

4. **未使用 tuistory 验证视觉效果** - 单元测试无法捕获渲染问题。工作人员必须使用 tuistory 来验证布局、对齐和视觉状态。

5. **没有持久化的测试基础设施** - 每个工作人员的 TDD 会产生单元/集成测试，但考虑一下任务是否还需要专门用于共享测试脚本或使用 tuistory 的端到端测试套件的功能。
