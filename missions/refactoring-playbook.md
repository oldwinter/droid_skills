---
name: refactoring-playbook
description: 代码现代化、架构迁移和大规模重构的 操作手册
---

# 重构与迁移手册

此手册指导涉及代码现代化、架构迁移、依赖升级或大规模重构的任务。核心挑战：**在改变实现的同时保持行为不变**。

## 关键原则：更改前先进行测试

没有测试的重构只是希望改变代码而已。在修改任何代码之前:
- 如果已存在测试: 确保它们通过并且覆盖你要改变的行为
- 如果没有测试: 先添加描述性测试以捕获当前行为

## 里程碑策略：逐步安全转换

围绕安全转换阶段构建里程碑:

- **characterization** - 添加测试以捕获当前行为（如果缺失）
- **scaffold** - 并行设置新模式/基础设施与旧的代码（绞杀者榕树）
- **migrate-batch-N** - 逐步迁移组件，每批完成后测试通过
- **cutover** - 切换到新的实现，移除旧代码
- **cleanup** - 移除框架，打磨

每个批次是一个里程碑。永远不要‘一次性上线’ - 始终是小而可验证的步骤，在每次提交后测试通过才能继续下一步。

## Worker 类型

重构任务使用协调共享状态的工人，这些状态位于 `{missionDir}/library/` 中。

### characterization-worker

在进行任何更改之前为现有行为添加测试。

1. 阅读 `migration-plan.md` 以了解将要迁移的内容
2. 识别缺乏测试覆盖的代码路径
3. 编写描述当前行为（而非理想行为）的特性测试
4. 更新 `migration-status.md`，记录测试覆盖率状态

这些测试必须在当前代码上通过。这些测试将成为迁移的安全网。

### scaffold-worker

设置新的基础设施与旧的共存（绞杀者榕树模式）。

1. 阅读 `migration-plan.md` 以了解目标架构/模式
2. 在现有代码旁边创建新模块/基础设施
3. 设置适配器/门面，使旧代码可以逐渐切换到新版本
4. 更新 `migration-status.md` 以记录骨架状态

旧测试仍然必须通过。 新的基础设施应该是可测试的但尚未使用

### migration-worker

从旧实现迁移到新实现的具体组件

1. 阅读 `migration-status.md` 以找到下一个要迁移的组件
2. 一次仅迁移一个组件/模块（保持范围较小）
3. 更新调用点以使用新实现
4. 运行完整测试套件 - 在完成之前必须通过
5. 更新 `migration-status.md`，标记组件为迁移完成

每次迁移都应是一个原子 commit。如果测试失败，请修复或回滚，绝不能留下损坏的代码。

### verification-worker

确保迁移后行为得以保留。

1. 阅读 `migration-status.md` 以了解发生了什么变化
2. 运行完整的测试套件，包括特性测试
3. 手动验证迁移后的功能
4. 比较旧版本与新版本在边缘情况下的行为差异
5. 记录任何发现的行为差异

## 信息流

```text
characterization-worker ──writes──▶ migration-status.md (test coverage)
                                            │
                                            ▼ reads
scaffold-worker ──writes──▶ migration-status.md (scaffold ready)
                                            │
                                            ▼ reads
migration-worker ──writes──▶ migration-status.md (component X migrated)
                                            │
                                            ▼ reads
verification-worker ──writes──▶ migration-status.md (batch verified)
```

每个工人：
1. 在开始前阅读 migration-plan.md 和 migration-status.md
2. 确保所有测试通过后再标记工作完成
3. 在完成后更新 migration-status.md

## orchestrator 设置

在开始迁移之前创建:

1. **`{missionDir}/library/migration-plan.md`**:
   - 当前状态（现在存在什么）
   - 目标状态（我们要迁移到哪里）
   - 范围（包括什么，明确排除什么）
   - 方法（绞杀者植物藤、并行运行等）
   - 风险区域（复杂逻辑、外部依赖项）

2. **`{missionDir}/library/migration-status.md`**:
   - 组件列表及其状态（待处理、进行中、已迁移、验证过）
   - 测试覆盖率状态
   - 骨架状态
   - 发现的问题/阻碍

3. **`{missionDir}/services.yaml`** - 确保 `test` 命令运行完整套件

## 功能结构

### 特征阶段
```
characterize-<area>  (characterization-worker) - Add tests for <area>
```

### 搭建阶段
```
scaffold-<component> (scaffold-worker) - Set up new <component> alongside old
```

### 迁移批次
```
migrate-<component>  (migration-worker) - Migrate <component> to new implementation
verify-batch-N       (verification-worker) - Verify batch N preserves behavior
```

### 切换与清理
```
cutover-<area>       (migration-worker) - Remove old <area>, switch fully to new
cleanup-<area>       (migration-worker) - Remove adapters, polish
```

## 示例工作 skill: migration-worker

```markdown
---
name: migration-worker
description: Migrate components from old to new implementation incrementally.
---

# Migration Worker

## Procedure

1. **Read status** - Check `migration-plan.md` and `migration-status.md`. Identify your assigned component. Return to orchestrator if scaffold not ready.

2. **Understand the component** - Read current implementation. Identify all call sites. Note edge cases and error handling.

3. **Migrate incrementally**:
   - Update component to use new patterns/infrastructure
   - Update call sites one at a time
   - Run tests after each change
   - Keep changes in atomic commits

4. **Verify** - Run full test suite. All tests must pass.

5. **Update status** in `migration-status.md`:
   ```
   ## UserService
   
   **状态:** 已迁移 **提交:** abc123 **更改:** 从类迁移到函数式，现在使用新的数据层 **调用站点更新:** 12 **测试:** 所有47 个测试都通过
   ```

## Example Handoff

{
  "salientSummary": "Migrated UserService to the functional pattern and updated 12 call sites; ran `npm test` (47 passing) and updated `{missionDir}/library/migration-status.md` with the MIGRATED status + commit.",
  "whatWasImplemented": "Migrated UserService from class-based to functional pattern. Updated 12 call sites. All 47 existing tests pass.",
  "verification": {
    "commandsRun": [
      {"command": "npm test", "exitCode": 0, "observation": "47 tests pass"},
      {"command": "grep 'Status: MIGRATED' {missionDir}/library/migration-status.md", "exitCode": 0, "observation": "Status updated"}
    ]
  }
}

## Return to Orchestrator When

- Scaffold not ready for this component
- Tests fail and fix is non-trivial
- Migration reveals architectural issue requiring plan change
- Component has undocumented dependencies
```

## 常见陷阱

1. **在迁移期间改变行为** - 重构只改变结构，不改变行为。行为变化应作为单独的功能处理。
2. **大爆炸迁移** - 每个提交都应使测试通过。不要批量处理多个组件。
3. **跳过特性化** - 在没有捕获当前行为的测试的情况下，无法验证保留情况。
4. **不完整的调用站点更新** - 使用 grep/find-references 确保所有使用都被更新。
5. **未更新迁移状态** - 下一个工人需要知道已完成的工作。
6. **混用重构与功能** - 保持它们分开。先重构，然后添加功能。

## 何时停止

- **完成** - 所有组件已迁移、验证并通过且旧代码已被移除
- **阻塞** - 发现需要架构决策的问题
- **范围变更** - 用户决定调整要迁移的内容
