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
`,HrB=`# Figma MCP 推广

## 目标

通过在检测到 Figma 使用时鼓励安装 MCP、在对话中推广 Figma 功能以及为设计到代码的工作流提供清晰的返回路径，确保用户最大限度地利用 Figma 的集成。

## 信号检测

从以下这些信号中检测 Figma 使用情况：
- **Figma URL**：`figma.com/design/*`、`figma.com/file/*`、`figma.com/board/*`、`figma.com/proto/*`
- **Figma 提到的内容**: 用户说 'Figma', 'figma design', 'figma component', 'figma file', '设计手稿'
- **带有 Figma 元数据的 PNG 图像**: 从 Figma 导出的图像通常包含标识 Figma 为源软件元数据
- **Figma 字体 agent**: 用户系统中存在 Figma 字体辅助程序（例如，在 macOS 中 `~/Library/Application Support/Figma/`）

## 当 Figma MCP 未安装时

如果你检测到 Figma 信号但 `figma___*` 工具不可用：

1. 自然地在响应中承认 Figma 上下文
2. 建议使用确切的命令进行安装：
   ```
   droid mcp add figma https://mcp.figma.com/mcp --type http
   ```
3. 简要解释其价值：直接访问设计上下文、组件元数据、变量和屏幕截图——无需手动导出
4. 不要阻拦用户的当前任务 — 在他们请求的帮助后提供帮助，然后建议使用 Figma MCP 作为增强功能

示例响应模式：
> 我可以帮你构建这个组件。顺便说一句，我发现你正在使用一个 Figma 设计 — 如果你连接 Figma MCP (`droid mcp add figma https://mcp.figma.com/mcp --type http`)，我可以直接从你的 Figma 文件中拉取设计令牌、组件结构和截图。

## 当 Figma MCP 已安装时

### 对话推广（建议更深入的使用）
在完成与 Figma 相关的操作后，提供后续建议：
- "你想要分享一个 Figma 链接以便我获取精确的设计上下文吗?"
- "我也可以拉取这个组件的变量定义 — 你想让我检查一下吗?"
- "你想要我为文件中的另一个节点获取设计上下文吗?"

### 反推到 Figma（展示链接到 Figma 的内容）
在任何源自 Figma 节点的操作之后：
- 始终在你的响应中包含来源的 Figma URL 作为可点击的 Markdown 链接
- 格式: `[View in Figma](https://figma.com/design/{fileKey}/{fileName}?node-id={nodeId})`
- 如果 `generate_diagram` 工具返回 FigJam URL，请始终以 Markdown 链接的形式显示它

### 主动使用工具
当你检测到 Figma 上下文并且可用的工具时:
- 使用 `figma___get_design_context` 用于设计到代码的工作流（优先于 `get_screenshot` 或 `get_metadata`）
- 当用户询问关于设计令牌或主题的信息时，使用 `figma___get_variable_defs`
- 使用 `figma___get_code_connect_map` 检查组件是否已映射到代码
- 在从 Figma 设计实现新组件时建议使用 `figma___get_code_connect_suggestions`

## 不要
- 如果用户已在当前会话中拒绝或忽略了建议，勿重复建议 Figma MCP
- 阻止或延迟用户的主任务以促进 Figma
- 当对话没有 Figma 信号时建议 Figma MCP
`,tmh,rmh,QHH,UHH,Bmh,jx;var b1T=F(()=>{b_();tmh=[{metadata:{name:"mission-planning",description:"Guides the orchestrator through the planning phase with the user."},systemPrompt:mtB,location:"builtin",filePath:"builtin:mission-planning",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:"define-mission-skills",description:"Guides the orchestrator through designing worker types and their skills."},systemPrompt:dtB,location:"builtin",filePath:"builtin:define-mission-skills",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:"refactoring-playbook",description:"Playbook for code modernization, architecture migrations, and large-scale refactoring. Provides guidance on characterization testing, strangler fig pattern, incremental migration, and behavior preservation."},systemPrompt:TrB,location:"builtin",filePath:"builtin:refactoring-playbook",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:"tui-application-playbook",description:"Playbook for terminal user interface (TUI) application missions. Provides guidance on vertical slice milestones, walking skeleton, TUI/backend workers, tuistory-based manual verification, and quality enforcement."},systemPrompt:RrB,location:"builtin",filePath:"builtin:tui-application-playbook",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}}],rmh=ptB,QHH={metadata:{name:"tuistory",description:"Automates terminal user interface (TUI) testing. Use when you need to launch, interact with, test, or debug terminal applications, capture TUI snapshots, or automate terminal inputs."},systemPrompt:xtB,location:"builtin",filePath:"builtin:tuistory",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},UHH={metadata:{name:"figma-mcp-helper",description:"Promote and assist with Figma MCP integration. ACTIVATE when the user shares a Figma URL (figma.com), mentions Figma designs or components, shares PNG images that may originate from Figma, or when Figma MCP tools are already connected and being used. Handles installation encouragement, conversational promotion, and push-back-to-Figma flows."},systemPrompt:HrB,location:"builtin",filePath:"builtin:figma-mcp-helper",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},Bmh=[{metadata:{name:PHH,description:"Base procedures for all mission workers: startup, cleanup, and handoff."},systemPrompt:stB,location:"builtin",filePath:`builtin:${PHH}`,lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:LjT,description:"Scrutiny validation: runs validators, spawns review subagents, synthesizes results. Auto-injected by system when milestone completes."},systemPrompt:btB,location:"builtin",filePath:`builtin:${LjT}`,lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:DjT,description:"User testing validation: determines testable assertions, sets up env, spawns flow validators, synthesizes results. Auto-injected by system when milestone completes."},systemPrompt:atB,location:"builtin",filePath:`builtin:${DjT}`,lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}}],jx=[LjT,DjT]});function ODA(T){if(T&&hrB.has(T))return"validation_worker";return"implementation_worker"}function t$R(T){let R=T.toLowerCase();if(R.includes("daemon_unreachable"))return"daemon_unreachable";if(R.includes("timed out waiting for factoryd"))return"daemon_rpc_timeout";if(R.includes("factoryd appears to be unavailable"))return"daemon_unavailable_during_run";if(R.includes("factoryd is not reachable"))return"daemon_not_reachable";if(R.includes("spawn error"))return"worker_spawn_error";if(R.includes("load session error"))return"worker_load_session_error";if(R.includes("resume error"))return"worker_resume_error";if(R.includes("inactivity"))return"worker_inactivity_timeout";if(R.includes("process exited"))return"worker_process_exit";if(R.includes("orphan_cleanup"))return"worker_orphan_cleanup";if(R.includes("killed by user"))return"worker_killed_by_user";if(R.includes("missing missionid"))return"missing_mission_id";if(R.includes("worker interrupted"))return"worker_interrupted";if(R.includes("timed out"))return"timeout";return"other"}function r$R(T){switch(T){case"daemon_unreachable":case"daemon_rpc_timeout":case"daemon_unavailable_during_run":case"daemon_not_reachable":return"daemon_connectivity";case"worker_spawn_error":case"worker_process_exit":return"worker_execution";case"worker_load_session_error":case"worker_resume_error":case"worker_orphan_cleanup":return"worker_session";case"worker_killed_by_user":case"worker_interrupted":return"user_action";case"missing_mission_id":return"mission_state";case"worker_inactivity_timeout":case"timeout":return"timeout";case"other":default:return"other"}}var hrB;var KHH=F(()=>{b1T();rZ();hrB=new Set(jx)});var Lmh={};Dh(Lmh,{setSecureFilePermissionsSync:()=>BW,setSecureFilePermissions:()=>px,setSecureDirectoryPermissionsSync:()=>xTT,ensureAllSecurePermissions:()=>irB});import*as _lT from"fs";import{promisify as nrB}from"util";async function px(T){try{await umh(T,fmh)}catch(R){tR(R,"[Security] Failed to set file permissions (async)",{path:T})}}async function _mh(T){try{await umh(T,Cmh)}catch(R){tR(R,"[Security] Failed to set directory permissions (async)",{path:T})}}function BW(T){try{if(_lT.chmodSync)_lT.chmodSync(T,fmh)}catch(R){tR(R,"[Security] Failed to set file permissions (sync)",{path:T})}}function xTT(T){try{if(_lT.chmodSync)_lT.chmodSync(T,Cmh)}catch(R){tR(R,"[Security] Failed to set directory permissions (sync)",{path:T})}}async function irB(){let{promises:T}=await import("fs"),R=await import("path"),{getFactoryDirName:H}=await Promise.resolve().then(() => (it(),ADh)),{getFactoryHome:A}=await Promise.resolve().then(() => (Mr(),jLh)),h=R.join(A(),H());try{await T.access(h)}catch{return}try{await _mh(h);let i=["sessions","updates","logs","droids"];for(let f of i){let C=R.join(h,f);try{await T.access(C),await _mh(C)}catch{}}let t=["auth.json","config.json","history.json","mcp.json","settings.json"];for(let f of t){let C=R.join(h,f);try{await T.access(C),await px(C)}catch{}}let B=R.join(h,"sessions");try{let f=await T.readdir(B);for(let C of f)if(C.endsWith(".jsonl")||C.endsWith(".settings.json")){let D=R.join(B,C);await px(D)}}catch{}let _=R.join(h,"droids");try{let f=await T.readdir(_);for(let C of f)if(C.endsWith(".json")){let D=R.join(_,C);await px(D)}}catch{}oT("[Security] File permissions secured on startup")}catch(i){tR(i,"[Security] Could not fully secure file permissions")}}var umh,fmh=384,Cmh=448;var ulT=F(()=>{JR();umh=_lT.chmod?nrB(_lT.chmod):async()=>{}});function wo(T){return T.toLowerCase().replace(/[^a-z0-9-]/g,"-").replace(/-+/g,"-").replace(/^-|-$/g,"")}import{readFileSync as trB}from"fs";import c1 from"fs/promises";import PC from"path";function Dmh(T){return T.trim().replace(/[^a-zA-Z0-9._-]+/g,"_").replace(/^_+|_+$/g,"").slice(0,120)}function rrB(T){return T.replace(/[:.]/g,"-")}async function a1T(T){try{return await c1.access(T),!0}catch{return!1}}async function oDA(T,R=new Set){let H;try{H=await c1.realpath(T)}catch{return[]}if(R.has(H))return[];R.add(H);let A;try{A=await c1.readdir(T,{withFileTypes:!0})}catch{return[]}return(await Promise.all(A.filter((i)=>i.isDirectory()||i.isSymbolicLink()).map(async(i)=>{let t=PC.join(T,i.name);if(await a1T(PC.join(t,lDA)))return[t];return oDA(t,R)}))).flat()}class IjT{baseSessionId;missionDir;progressLogCache=null;missionMetadataSyncTimer=null;constructor(T){this.baseSessionId=T,this.missionDir=PC.join(mX(),"missions",this.baseSessionId)}getMissionDir(){return this.missionDir}isCloudSessionSyncEnabled(){return CH().getSettings().general?.cloudSessionSync??!0}syncMissionMetadataToCloud(){if(!this.isCloudSessionSyncEnabled())return;if(this.missionMetadataSyncTimer)return;this.missionMetadataSyncTimer=setTimeout(()=>{this.missionMetadataSyncTimer=null,this.flushMissionMetadataToCloud()},BrB),this.missionMetadataSyncTimer.unref()}async flushPendingMissionMetadataSyncToCloud(){if(!this.missionMetadataSyncTimer)return;clearTimeout(this.missionMetadataSyncTimer),this.missionMetadataSyncTimer=null,await this.flushMissionMetadataToCloud()}async flushMissionMetadataToCloud(){if(!this.isCloudSessionSyncEnabled())return;let T=M2T({missionsDir:PC.dirname(this.missionDir),sessionId:this.baseSessionId});if(!T)return;await _v().syncMissionMetadata(this.baseSessionId,T)}async initializeMissionDir(){await c1.mkdir(this.missionDir,{recursive:!0})}async missionExists(){try{return await c1.access(this.missionDir),!0}catch{return!1}}get artifactLayoutMarkerPath(){return PC.join(this.missionDir,"canonical-artifact-layout.json")}async readCanonicalArtifactLayoutMarker(){try{let T=await c1.readFile(this.artifactLayoutMarkerPath,"utf-8");return JSON.parse(T)}catch{return null}}async writeArtifactLayoutMarker(T){await c1.writeFile(this.artifactLayoutMarkerPath,JSON.stringify(T,null,2))}async getPendingCanonicalArtifactLayoutNotice(){let T=await this.readCanonicalArtifactLayoutMarker();if(!T||T.canonicalNoticeShownAt)return null;return T}async markCanonicalArtifactLayoutNoticeShown(T=new Date().toISOString()){let R=await this.readCanonicalArtifactLayoutMarker();if(!R||R.canonicalNoticeShownAt)return;await this.writeArtifactLayoutMarker({...R,canonicalNoticeShownAt:T})}async ensureCanonicalArtifactLayout(){let T=await this.readState(),R=await this.readCanonicalArtifactLayoutMarker();if(T?.artifactLayoutVersion===qjT||R?.version===qjT){if(T&&T.artifactLayoutVersion!==qjT)await this.updateState({artifactLayoutVersion:qjT,legacyArtifactsHydratedAt:R?.hydratedAt});return{status:"canonical",importedPaths:[],ambiguousSkillNames:[]}}let H=await this.readFeatures();if(!H)return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let A=T?.workingDirectory??await this.readWorkingDirectory();if(!A)return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let h=PC.join(A,frB);if(!await a1T(h))return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let i=[...new Set(H.features.map((y)=>wo(y.skillName)).filter(Boolean))];if(!(await Promise.all(qmh.map(async(y)=>a1T(PC.join(h,y))))).some(Boolean)&&R===null)return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let f=await this.findLegacySkillMatches(PC.join(h,"skills"),i),C=[];for(let y of qmh){let k=await this.copyLegacyArtifactIfMissing({sourcePath:PC.join(h,y),destinationPath:PC.join(this.missionDir,y),logicalPath:y});C.push(...k)}let D=[];for(let y of i){if(await this.hasMissionScopedSkill(y))continue;let k=f.get(y)??[];if(k.length===0)continue;if(k.length>1){D.push(y),$T("[MissionFileService] Legacy mission skill is ambiguous",{baseSessionId:this.baseSessionId,name:y,paths:k.map((G)=>G.skillDirPath)});continue}let[Q]=k,K=await this.copyLegacyArtifactIfMissing({sourcePath:Q.skillDirPath,destinationPath:PC.join(this.missionDir,"skills",Q.relativeDir),logicalPath:PC.join("skills",Q.relativeDir)});C.push(...K)}let $=!1,O=R?.hydratedAt??new Date().toISOString(),o={version:D.length===0?qjT:void 0,hydratedAt:O,importedPaths:[...new Set([...R?.importedPaths??[],...C])],ambiguousSkillNames:D,canonicalNoticeShownAt:R?.canonicalNoticeShownAt};if(await this.writeArtifactLayoutMarker(o),D.length===0){if(T)await this.updateState({artifactLayoutVersion:qjT,legacyArtifactsHydratedAt:O});$=!0}return oT("[MissionFileService] Checked legacy mission artifact layout",{baseSessionId:this.baseSessionId,cwd:A,paths:C,skillNames:D}),{status:"hydrated",importedPaths:C,ambiguousSkillNames:D,markedCanonical:$}}async findLegacySkillMatches(T,R){if(R.length===0||!await a1T(T))return new Map;let H=new Set(R),A=new Map,h=await oDA(T);for(let i of h){let t=await Cx(PC.join(i,lDA),"project");if(!t)continue;let B=wo(t.metadata.name);if(!H.has(B))continue;let _=PC.relative(T,i);if(_.startsWith("..")||PC.isAbsolute(_)||_==="")continue;let f=A.get(B)??[];f.push({skillDirPath:i,relativeDir:_}),A.set(B,f)}return A}async hasMissionScopedSkill(T){let R=PC.join(this.missionDir,"skills");if(!await a1T(R))return!1;let H=await oDA(R);for(let A of H){let h=await Cx(PC.join(A,lDA),"project");if(!h)continue;if(wo(h.metadata.name)===T)return!0}return!1}async copyLegacyArtifactIfMissing(T){if(!await a1T(T.sourcePath))return[];if((await c1.stat(T.sourcePath)).isDirectory())return this.copyDirectoryContentsIfMissing(T.sourcePath,T.destinationPath,T.logicalPath);return await this.copyFileIfMissing(T.sourcePath,T.destinationPath)?[T.logicalPath]:[]}async copyDirectoryContentsIfMissing(T,R,H){await c1.mkdir(R,{recursive:!0});let A=[],h=await c1.readdir(T,{withFileTypes:!0});for(let i of h){let t=PC.join(T,i.name),B=PC.join(R,i.name),_=PC.join(H,i.name);if(i.isDirectory()){A.push(...await this.copyDirectoryContentsIfMissing(t,B,_));continue}if(i.isSymbolicLink()){if((await c1.stat(t)).isDirectory())A.push(...await this.copyDirectoryContentsIfMissing(t,B,_));else if(await this.copyFileIfMissing(t,B))A.push(_);continue}if(await this.copyFileIfMissing(t,B))A.push(_)}return A}async copyFileIfMissing(T,R){if(await a1T(R))return!1;await c1.mkdir(PC.dirname(R),{recursive:!0}),await c1.copyFile(T,R);let H=await c1.stat(T);return await c1.chmod(R,H.mode),!0}get stateFilePath(){return PC.join(this.missionDir,"state.json")}async readState(){try{let T=await c1.readFile(this.stateFilePath,"utf-8");return JSON.parse(T)}catch(T){if(T.code!=="ENOENT")$T("[MissionFileService] Failed to read state.json",{baseSessionId:this.baseSessionId,filePath:this.stateFilePath,cause:T});return null}}async readStateOrThrow(){let T=await c1.readFile(this.stateFilePath,"utf-8");return JSON.parse(T)}async writeState(T){T.updatedAt=new Date().toISOString(),await c1.writeFile(this.stateFilePath,JSON.stringify(T,null,2)),this.syncMissionMetadataToCloud()}async createInitialState(T,R="initializing"){let H=new Date().toISOString(),A={missionId:`mis_${Lr().slice(0,8)}`,state:R,workingDirectory:T,createdAt:H,updatedAt:H};return await this.writeState(A),A}async ensurePlanningState(T){if(await this.initializeMissionDir(),await this.readState())return;await this.writeWorkingDirectory(T),await this.createInitialState(T,"planning")}async hasMissionArtifacts(){if((await Promise.all(urB.map((H)=>a1T(PC.join(this.missionDir,H))))).some(Boolean))return!0;if(!await this.missionExists())return!1;let R=await this.readState();return R===null||R.state!=="planning"}async updateState(T){let R=await this.readState();if(!R)throw new VT("Mission state not found for",{baseSessionId:this.baseSessionId});let H={...R,...T};if(await this.writeState(H),T.state!==void 0)kn.emit("project-notification",{notification:{type:"mission_state_changed",state:H.state,updatedAt:H.updatedAt}});return H}get featuresFilePath(){return PC.join(this.missionDir,"features.json")}static normalizeFeature(T){let R=T.milestone,H=typeof R==="number"||typeof R==="boolean"?String(R):typeof R==="string"?R:void 0;return{id:T.id||"",description:T.description||"",skillName:T.skillName||"",preconditions:Array.isArray(T.preconditions)?T.preconditions:[],expectedBehavior:Array.isArray(T.expectedBehavior)?T.expectedBehavior:typeof T.expectedBehavior==="string"?[T.expectedBehavior]:[],fulfills:Array.isArray(T.fulfills)?T.fulfills:void 0,milestone:H,status:T.status||"pending",workerSessionIds:T.workerSessionIds||[],currentWorkerSessionId:T.currentWorkerSessionId??null,completedWorkerSessionId:T.completedWorkerSessionId??null}}async readFeatures(){try{let T=await c1.readFile(this.featuresFilePath,"utf-8");return this.parseFeaturesContent(T)}catch(T){return this.handleReadFeaturesError(T),null}}readFeaturesSync(){try{let T=trB(this.featuresFilePath,"utf-8");return this.parseFeaturesContent(T)}catch(T){return this.handleReadFeaturesError(T),null}}parseFeaturesContent(T){let R=JSON.parse(T),H=Array.isArray(R)?R:R.features;if(!Array.isArray(H))return $T("[MissionFileService] Invalid features.json schema",{baseSessionId:this.baseSessionId,filePath:this.featuresFilePath}),null;return{features:H.map((A)=>IjT.normalizeFeature(A))}}handleReadFeaturesError(T){if(T.code!=="ENOENT")$T("[MissionFileService] Failed to read features.json",{baseSessionId:this.baseSessionId,filePath:this.featuresFilePath,cause:T})}async readFeaturesOrThrow(){let T=await c1.readFile(this.featuresFilePath,"utf-8"),R=JSON.parse(T),H=Array.isArray(R)?R:R.features;if(!Array.isArray(H))throw Error('Invalid features.json: expected { "features": [...] } or a bare array');return{features:H.map((A)=>IjT.normalizeFeature(A))}}async writeFeatures(T){await c1.writeFile(this.featuresFilePath,JSON.stringify(T,null,2)),this.syncMissionMetadataToCloud(),kn.emit("project-notification",{notification:{type:"mission_features_changed",features:T.features}})}async getFeature(T){let R=await this.readFeatures();if(!R)return null;return R.features.find((H)=>H.id===T)??null}getFeatureForWorkerSessionSync(T){let R=this.readFeaturesSync();if(!R)return null;return R.features.find((H)=>H.currentWorkerSessionId===T||(H.workerSessionIds??[]).includes(T))??null}async getInProgressFeature(){let T=await this.readFeatures();if(!T)return null;return T.features.find((R)=>R.status==="in_progress")??null}getInProgressFeatureSync(){let T=this.readFeaturesSync();if(!T)return null;return T.features.find((R)=>R.status==="in_progress")??null}async updateFeature(T,R){let H=await this.readFeatures();if(!H)return null;let A=H.features.findIndex((h)=>h.id===T);if(A===-1)return null;return H.features[A]={...H.features[A],...R},await this.writeFeatures(H),H.features[A]}async getNextPendingFeature(){let T=await this.readFeatures();if(!T)return null;return T.features.find((R)=>R.status==="pending")??null}async areAllFeaturesCompleted(){let T=await this.readFeatures();if(!T)return!1;return T.features.every((R)=>R.status==="completed"||R.status==="cancelled")}async addFeature(T){let R=await this.readFeatures();if(!R){await this.writeFeatures({features:[T]});return}R.features.push(T),await this.writeFeatures(R)}async insertFeatureAtTop(T){let R=await this.readFeatures();if(!R){await this.writeFeatures({features:[T]});return}R.features.unshift(T),await this.writeFeatures(R)}async moveFeatureToBottom(T){let R=await this.readFeatures();if(!R)return;let H=R.features.findIndex((h)=>h.id===T);if(H===-1)return;let[A]=R.features.splice(H,1);R.features.push(A),await this.writeFeatures(R)}async moveStrandedDoneFeaturesToBottom(){let T=await this.readFeatures();if(!T||T.features.length===0)return;let R=(B)=>B.status==="completed"||B.status==="cancelled",H=T.features,A=H.length;while(A>0&&R(H[A-1]))A--;let h=[],i=[];for(let B=0;B<A;B++)if(R(H[B]))h.push(H[B]);else i.push(H[B]);if(h.length===0)return;let t=H.slice(A);T.features=[...i,...t,...h],await this.writeFeatures(T)}async getMilestoneFeatures(T){let R=await this.readFeatures();if(!R)return[];return R.features.filter((H)=>H.milestone===T)}async getAllMilestones(){let T=await this.readFeatures();if(!T)return[];let R=new Set;for(let H of T.features)if(H.milestone)R.add(H.milestone);return Array.from(R)}async isMilestoneImplementationComplete(T){let R=await this.getMilestoneFeatures(T);if(R.length===0)return!1;let H=R.filter((A)=>!jx.includes(A.skillName));if(H.length===0)return!1;return H.every((A)=>A.status==="completed"||A.status==="cancelled")}async hasValidationPlannerRun(T){return(await this.readProgressLog()).some((H)=>H.type==="milestone_validation_triggered"&&H.milestone===T)}get progressLogPath(){return PC.join(this.missionDir,"progress_log.jsonl")}static updateDerivedWorkerStatesFromProgressEntry(T,R,H){if(T.type==="worker_started"){let{workerSessionId:A,timestamp:h}=T;if(H){let t=R[H];if(t&&!t.completedAt)R[H]={...t,completedAt:h}}let i=R[A];return R[A]={...i,startedAt:typeof i?.startedAt==="string"?i.startedAt:h},A}if(T.type==="worker_completed"){let{workerSessionId:A,timestamp:h,exitCode:i}=T,t=R[A];return R[A]={startedAt:t?.startedAt??h,completedAt:h,exitCode:i},H===A?void 0:H}if(T.type==="worker_failed"){let{workerSessionId:A,timestamp:h,exitCode:i}=T;if(A){let t=R[A];return R[A]={startedAt:t?.startedAt??h,completedAt:h,exitCode:i},H===A?void 0:H}}return H}async readProgressLogIncrementalOrThrow(){let T;try{let h=await c1.stat(this.progressLogPath);T={size:h.size,mtimeMs:h.mtimeMs}}catch(h){if(h.code==="ENOENT")return this.progressLogCache=null,{progressLog:[],derivedWorkerStates:{}};throw h}if(this.progressLogCache&&this.progressLogCache.size===T.size&&this.progressLogCache.mtimeMs===T.mtimeMs)return{progressLog:this.progressLogCache.entries,derivedWorkerStates:this.progressLogCache.derivedWorkerStates};let R=this.progressLogCache;if(!R||T.size<R.offset||T.size===R.size&&T.mtimeMs!==R.mtimeMs){let t=(await c1.readFile(this.progressLogPath,"utf-8")).trim().split(`
`).filter((f)=>f.trim()).map((f)=>JSON.parse(f)),B={},_;for(let f of t)_=IjT.updateDerivedWorkerStatesFromProgressEntry(f,B,_);return this.progressLogCache={size:T.size,mtimeMs:T.mtimeMs,offset:T.size,remainder:"",entries:t,derivedWorkerStates:B,activeWorkerSessionId:_},{progressLog:t,derivedWorkerStates:B}}let A=await c1.open(this.progressLogPath,"r");try{let h=R.offset,i=T.size-h;if(i<=0)return this.progressLogCache={...R,size:T.size,mtimeMs:T.mtimeMs,offset:T.size},{progressLog:this.progressLogCache.entries,derivedWorkerStates:this.progressLogCache.derivedWorkerStates};let t=Buffer.alloc(i);await A.read(t,0,i,h);let B=t.toString("utf-8"),f=(R.remainder+B).split(`
`),C=f.pop()??"",$=f.map((k)=>k.trim()).filter(Boolean).map((k)=>JSON.parse(k)),O=[...R.entries,...$],o={...R.derivedWorkerStates},y=R.activeWorkerSessionId;for(let k of $)y=IjT.updateDerivedWorkerStatesFromProgressEntry(k,o,y);return this.progressLogCache={...R,size:T.size,mtimeMs:T.mtimeMs,offset:T.size,remainder:C,entries:O,derivedWorkerStates:o,activeWorkerSessionId:y},{progressLog:O,derivedWorkerStates:o}}finally{await A.close()}}async readProgressLog(){try{let{progressLog:T}=await this.readProgressLogIncrementalOrThrow();return T}catch{return[]}}async readProgressLogOrThrow(){let{progressLog:T}=await this.readProgressLogIncrementalOrThrow();return T}async readProgressLogWithDerivedWorkerStatesOrThrow(){return this.readProgressLogIncrementalOrThrow()}async readProgressLogRaw(){try{return await c1.readFile(this.progressLogPath,"utf-8")}catch{return""}}async appendProgressLog(T){let R={...T,timestamp:T.timestamp||new Date().toISOString()},H=`${JSON.stringify(R)}
