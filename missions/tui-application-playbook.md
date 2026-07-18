---
name: tui-application-playbook
description: Playbook for terminal user interface (TUI) application missions. Provides guidance on execution, milestones, and verification strategies.
---

# TUI Application Playbook

This playbook guides you through executing a terminal user interface (TUI) application mission. Use this for CLI tools with interactive interfaces, terminal dashboards, text-based editors, and similar projects rendered in the terminal.

## Milestone Strategy: Vertical Slices

Structure your milestones as **vertical slices** of functionality, not horizontal layers.

**Good milestones:**
- "navigation" (menu system, views, keybindings - full stack)
- "data-display" (list views, detail views, formatting - full stack)
- "editing" (input handling, validation, persistence - full stack)

**Bad milestones:**
- "all-keybindings" (horizontal - can't test in isolation)
- "rendering-layer" (horizontal - can't test without data/state)

Each milestone should leave the app in a coherent, testable state where a user can complete a meaningful flow.

## Worker Types for TUI

### tui-worker

- Implements TUI features (views, components, input handling, state)
- **TDD: Write tests FIRST (before any implementation)**
- **MUST do manual TUI verification with tuistory:**
  - Launch the app, navigate to the relevant view, and verify rendering and interactions
  - Use `tuistory snapshot --trim` to capture terminal output and verify visual correctness
  - Test keyboard interactions (`tuistory press <key>`), input handling (`tuistory type "<text>"`)
  - Check for rendering artifacts, alignment issues, overflow, and missing states
- **Fix issues found:**
  - Issues with own work (including from manual testing) → must fix
  - Manageable existing issues under their skill → fix them
  - Large scope or outside their skill → report to orchestrator
  - Include any fixes in whatWasImplemented

### backend-worker

- Implements data layer, services, and business logic that the TUI consumes
- **TDD: Write tests FIRST (before any implementation)**
- Verifies actual behavior (not just tests passing)
- **Fix issues found:**
  - Issues with own work (including from manual testing) → must fix
  - Manageable existing issues under their skill → fix them
  - Large scope or outside their skill → report to orchestrator
  - Include any fixes in whatWasImplemented

## Quality Enforcement Flow

```text
1. Orchestrator creates implementation features grouped by milestone
2. Implementation workers build features (TDD + manual verification via tuistory)
3. When milestone X completes → system injects scrutiny and user-testing validators for the milestone
4. Failed validation surfaces bugs → orchestrator creates fix features
5. Repeat until milestone passes, then move to next milestone
```

### Example tuistory validation flow

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

## Common Pitfalls

1. **Building state management without UI** - Leads to data structures that don't match rendering needs. Build vertical slices instead.

2. **Forgetting edge states** - Workers often implement happy path only. expectedBehavior should include empty states, error states, overflow/truncation, and resize handling.

3. **Not testing keyboard interactions** - TUI apps are keyboard-driven. Every view needs its keybindings tested, including edge cases (rapid input, conflicting shortcuts).

4. **Not verifying visually with tuistory** - Unit tests can't catch rendering issues. Workers must use tuistory to verify layout, alignment, and visual state.

5. **No lasting test infrastructure** - Per-worker TDD produces unit/integration tests, but consider whether the mission also needs dedicated features for shared test fixtures or e2e test suites using tuistory.
`,HrB=`# Figma MCP Promotion

## Goal

Ensure users get the most out of Figma integration by encouraging MCP installation when Figma usage is detected, promoting Figma actions during conversation, and providing clear paths back to Figma after design-to-code workflows.

## Signal Detection

Detect Figma usage from any of these signals:
- **Figma URLs**: `figma.com/design/*`, `figma.com/file/*`, `figma.com/board/*`, `figma.com/proto/*`
- **Figma mentions**: User says "Figma", "figma design", "figma component", "figma file", "design handoff"
- **PNG with Figma metadata**: Images exported from Figma often contain software metadata identifying Figma as the source
- **Figma font agent**: Presence of the Figma font helper on the user's system (e.g., `~/Library/Application Support/Figma/` on macOS)

## When Figma MCP Is NOT Installed

If you detect a Figma signal but `figma___*` tools are not available:

1. Acknowledge the Figma context naturally within your response
2. Suggest installation with the exact command:
   ```
   droid mcp add figma https://mcp.figma.com/mcp --type http
   ```
3. Briefly explain the value: direct access to design context, component metadata, variables, and screenshots — no manual export needed
4. Do NOT block the user's current task — help them with whatever they asked, then suggest Figma MCP as an enhancement

Example response pattern:
> I can help you build this component. By the way, I noticed you're working with a Figma design — if you connect Figma MCP (`droid mcp add figma https://mcp.figma.com/mcp --type http`), I can pull design tokens, component structure, and screenshots directly from your Figma file.

## When Figma MCP IS Installed

### Conversational Promotion (suggest deeper usage)
After completing a Figma-related action, offer follow-up suggestions:
- "Would you like to share a Figma link so I can pull the exact design context?"
- "I can also fetch the variable definitions for this component — want me to check?"
- "Would you like me to get the design context for another node in this file?"

### Push-Back to Figma (surface links to Figma)
After any action that originated from a Figma node:
- Always include the source Figma URL as a clickable markdown link in your response
- Format: `[View in Figma](https://figma.com/design/{fileKey}/{fileName}?node-id={nodeId})`
- If the `generate_diagram` tool returns a FigJam URL, always display it as a markdown link

### Proactive Tool Usage
When you detect Figma context and tools are available:
- Use `figma___get_design_context` for design-to-code workflows (preferred over `get_screenshot` or `get_metadata`)
- Use `figma___get_variable_defs` when the user asks about design tokens or theming
- Use `figma___get_code_connect_map` to check if components are already mapped to code
- Suggest `figma___get_code_connect_suggestions` when implementing new components from Figma designs

## Do NOT
- Repeatedly suggest Figma MCP if the user has already declined or ignored the suggestion in the current session
- Block or delay the user's primary task to promote Figma
- Suggest Figma MCP when the conversation has no Figma signals
`,tmh,rmh,QHH,UHH,Bmh,jx;var b1T=F(()=>{b_();tmh=[{metadata:{name:"mission-planning",description:"Guides the orchestrator through the planning phase with the user."},systemPrompt:mtB,location:"builtin",filePath:"builtin:mission-planning",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:"define-mission-skills",description:"Guides the orchestrator through designing worker types and their skills."},systemPrompt:dtB,location:"builtin",filePath:"builtin:define-mission-skills",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:"refactoring-playbook",description:"Playbook for code modernization, architecture migrations, and large-scale refactoring. Provides guidance on characterization testing, strangler fig pattern, incremental migration, and behavior preservation."},systemPrompt:TrB,location:"builtin",filePath:"builtin:refactoring-playbook",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:"tui-application-playbook",description:"Playbook for terminal user interface (TUI) application missions. Provides guidance on vertical slice milestones, walking skeleton, TUI/backend workers, tuistory-based manual verification, and quality enforcement."},systemPrompt:RrB,location:"builtin",filePath:"builtin:tui-application-playbook",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}}],rmh=ptB,QHH={metadata:{name:"tuistory",description:"Automates terminal user interface (TUI) testing. Use when you need to launch, interact with, test, or debug terminal applications, capture TUI snapshots, or automate terminal inputs."},systemPrompt:xtB,location:"builtin",filePath:"builtin:tuistory",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},UHH={metadata:{name:"figma-mcp-helper",description:"Promote and assist with Figma MCP integration. ACTIVATE when the user shares a Figma URL (figma.com), mentions Figma designs or components, shares PNG images that may originate from Figma, or when Figma MCP tools are already connected and being used. Handles installation encouragement, conversational promotion, and push-back-to-Figma flows."},systemPrompt:HrB,location:"builtin",filePath:"builtin:figma-mcp-helper",lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},Bmh=[{metadata:{name:PHH,description:"Base procedures for all mission workers: startup, cleanup, and handoff."},systemPrompt:stB,location:"builtin",filePath:`builtin:${PHH}`,lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:LjT,description:"Scrutiny validation: runs validators, spawns review subagents, synthesizes results. Auto-injected by system when milestone completes."},systemPrompt:btB,location:"builtin",filePath:`builtin:${LjT}`,lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}},{metadata:{name:DjT,description:"User testing validation: determines testable assertions, sets up env, spawns flow validators, synthesizes results. Auto-injected by system when milestone completes."},systemPrompt:atB,location:"builtin",filePath:`builtin:${DjT}`,lastModified:0,validationResult:{valid:!0,errors:[],warnings:[]}}],jx=[LjT,DjT]});function ODA(T){if(T&&hrB.has(T))return"validation_worker";return"implementation_worker"}function t$R(T){let R=T.toLowerCase();if(R.includes("daemon_unreachable"))return"daemon_unreachable";if(R.includes("timed out waiting for factoryd"))return"daemon_rpc_timeout";if(R.includes("factoryd appears to be unavailable"))return"daemon_unavailable_during_run";if(R.includes("factoryd is not reachable"))return"daemon_not_reachable";if(R.includes("spawn error"))return"worker_spawn_error";if(R.includes("load session error"))return"worker_load_session_error";if(R.includes("resume error"))return"worker_resume_error";if(R.includes("inactivity"))return"worker_inactivity_timeout";if(R.includes("process exited"))return"worker_process_exit";if(R.includes("orphan_cleanup"))return"worker_orphan_cleanup";if(R.includes("killed by user"))return"worker_killed_by_user";if(R.includes("missing missionid"))return"missing_mission_id";if(R.includes("worker interrupted"))return"worker_interrupted";if(R.includes("timed out"))return"timeout";return"other"}function r$R(T){switch(T){case"daemon_unreachable":case"daemon_rpc_timeout":case"daemon_unavailable_during_run":case"daemon_not_reachable":return"daemon_connectivity";case"worker_spawn_error":case"worker_process_exit":return"worker_execution";case"worker_load_session_error":case"worker_resume_error":case"worker_orphan_cleanup":return"worker_session";case"worker_killed_by_user":case"worker_interrupted":return"user_action";case"missing_mission_id":return"mission_state";case"worker_inactivity_timeout":case"timeout":return"timeout";case"other":default:return"other"}}var hrB;var KHH=F(()=>{b1T();rZ();hrB=new Set(jx)});var Lmh={};Dh(Lmh,{setSecureFilePermissionsSync:()=>BW,setSecureFilePermissions:()=>px,setSecureDirectoryPermissionsSync:()=>xTT,ensureAllSecurePermissions:()=>irB});import*as _lT from"fs";import{promisify as nrB}from"util";async function px(T){try{await umh(T,fmh)}catch(R){tR(R,"[Security] Failed to set file permissions (async)",{path:T})}}async function _mh(T){try{await umh(T,Cmh)}catch(R){tR(R,"[Security] Failed to set directory permissions (async)",{path:T})}}function BW(T){try{if(_lT.chmodSync)_lT.chmodSync(T,fmh)}catch(R){tR(R,"[Security] Failed to set file permissions (sync)",{path:T})}}function xTT(T){try{if(_lT.chmodSync)_lT.chmodSync(T,Cmh)}catch(R){tR(R,"[Security] Failed to set directory permissions (sync)",{path:T})}}async function irB(){let{promises:T}=await import("fs"),R=await import("path"),{getFactoryDirName:H}=await Promise.resolve().then(() => (it(),ADh)),{getFactoryHome:A}=await Promise.resolve().then(() => (Mr(),jLh)),h=R.join(A(),H());try{await T.access(h)}catch{return}try{await _mh(h);let i=["sessions","updates","logs","droids"];for(let f of i){let C=R.join(h,f);try{await T.access(C),await _mh(C)}catch{}}let t=["auth.json","config.json","history.json","mcp.json","settings.json"];for(let f of t){let C=R.join(h,f);try{await T.access(C),await px(C)}catch{}}let B=R.join(h,"sessions");try{let f=await T.readdir(B);for(let C of f)if(C.endsWith(".jsonl")||C.endsWith(".settings.json")){let D=R.join(B,C);await px(D)}}catch{}let _=R.join(h,"droids");try{let f=await T.readdir(_);for(let C of f)if(C.endsWith(".json")){let D=R.join(_,C);await px(D)}}catch{}oT("[Security] File permissions secured on startup")}catch(i){tR(i,"[Security] Could not fully secure file permissions")}}var umh,fmh=384,Cmh=448;var ulT=F(()=>{JR();umh=_lT.chmod?nrB(_lT.chmod):async()=>{}});function wo(T){return T.toLowerCase().replace(/[^a-z0-9-]/g,"-").replace(/-+/g,"-").replace(/^-|-$/g,"")}import{readFileSync as trB}from"fs";import c1 from"fs/promises";import PC from"path";function Dmh(T){return T.trim().replace(/[^a-zA-Z0-9._-]+/g,"_").replace(/^_+|_+$/g,"").slice(0,120)}function rrB(T){return T.replace(/[:.]/g,"-")}async function a1T(T){try{return await c1.access(T),!0}catch{return!1}}async function oDA(T,R=new Set){let H;try{H=await c1.realpath(T)}catch{return[]}if(R.has(H))return[];R.add(H);let A;try{A=await c1.readdir(T,{withFileTypes:!0})}catch{return[]}return(await Promise.all(A.filter((i)=>i.isDirectory()||i.isSymbolicLink()).map(async(i)=>{let t=PC.join(T,i.name);if(await a1T(PC.join(t,lDA)))return[t];return oDA(t,R)}))).flat()}class IjT{baseSessionId;missionDir;progressLogCache=null;missionMetadataSyncTimer=null;constructor(T){this.baseSessionId=T,this.missionDir=PC.join(mX(),"missions",this.baseSessionId)}getMissionDir(){return this.missionDir}isCloudSessionSyncEnabled(){return CH().getSettings().general?.cloudSessionSync??!0}syncMissionMetadataToCloud(){if(!this.isCloudSessionSyncEnabled())return;if(this.missionMetadataSyncTimer)return;this.missionMetadataSyncTimer=setTimeout(()=>{this.missionMetadataSyncTimer=null,this.flushMissionMetadataToCloud()},BrB),this.missionMetadataSyncTimer.unref()}async flushPendingMissionMetadataSyncToCloud(){if(!this.missionMetadataSyncTimer)return;clearTimeout(this.missionMetadataSyncTimer),this.missionMetadataSyncTimer=null,await this.flushMissionMetadataToCloud()}async flushMissionMetadataToCloud(){if(!this.isCloudSessionSyncEnabled())return;let T=M2T({missionsDir:PC.dirname(this.missionDir),sessionId:this.baseSessionId});if(!T)return;await _v().syncMissionMetadata(this.baseSessionId,T)}async initializeMissionDir(){await c1.mkdir(this.missionDir,{recursive:!0})}async missionExists(){try{return await c1.access(this.missionDir),!0}catch{return!1}}get artifactLayoutMarkerPath(){return PC.join(this.missionDir,"canonical-artifact-layout.json")}async readCanonicalArtifactLayoutMarker(){try{let T=await c1.readFile(this.artifactLayoutMarkerPath,"utf-8");return JSON.parse(T)}catch{return null}}async writeArtifactLayoutMarker(T){await c1.writeFile(this.artifactLayoutMarkerPath,JSON.stringify(T,null,2))}async getPendingCanonicalArtifactLayoutNotice(){let T=await this.readCanonicalArtifactLayoutMarker();if(!T||T.canonicalNoticeShownAt)return null;return T}async markCanonicalArtifactLayoutNoticeShown(T=new Date().toISOString()){let R=await this.readCanonicalArtifactLayoutMarker();if(!R||R.canonicalNoticeShownAt)return;await this.writeArtifactLayoutMarker({...R,canonicalNoticeShownAt:T})}async ensureCanonicalArtifactLayout(){let T=await this.readState(),R=await this.readCanonicalArtifactLayoutMarker();if(T?.artifactLayoutVersion===qjT||R?.version===qjT){if(T&&T.artifactLayoutVersion!==qjT)await this.updateState({artifactLayoutVersion:qjT,legacyArtifactsHydratedAt:R?.hydratedAt});return{status:"canonical",importedPaths:[],ambiguousSkillNames:[]}}let H=await this.readFeatures();if(!H)return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let A=T?.workingDirectory??await this.readWorkingDirectory();if(!A)return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let h=PC.join(A,frB);if(!await a1T(h))return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let i=[...new Set(H.features.map((y)=>wo(y.skillName)).filter(Boolean))];if(!(await Promise.all(qmh.map(async(y)=>a1T(PC.join(h,y))))).some(Boolean)&&R===null)return{status:"skipped",importedPaths:[],ambiguousSkillNames:[]};let f=await this.findLegacySkillMatches(PC.join(h,"skills"),i),C=[];for(let y of qmh){let k=await this.copyLegacyArtifactIfMissing({sourcePath:PC.join(h,y),destinationPath:PC.join(this.missionDir,y),logicalPath:y});C.push(...k)}let D=[];for(let y of i){if(await this.hasMissionScopedSkill(y))continue;let k=f.get(y)??[];if(k.length===0)continue;if(k.length>1){D.push(y),$T("[MissionFileService] Legacy mission skill is ambiguous",{baseSessionId:this.baseSessionId,name:y,paths:k.map((G)=>G.skillDirPath)});continue}let[Q]=k,K=await this.copyLegacyArtifactIfMissing({sourcePath:Q.skillDirPath,destinationPath:PC.join(this.missionDir,"skills",Q.relativeDir),logicalPath:PC.join("skills",Q.relativeDir)});C.push(...K)}let $=!1,O=R?.hydratedAt??new Date().toISOString(),o={version:D.length===0?qjT:void 0,hydratedAt:O,importedPaths:[...new Set([...R?.importedPaths??[],...C])],ambiguousSkillNames:D,canonicalNoticeShownAt:R?.canonicalNoticeShownAt};if(await this.writeArtifactLayoutMarker(o),D.length===0){if(T)await this.updateState({artifactLayoutVersion:qjT,legacyArtifactsHydratedAt:O});$=!0}return oT("[MissionFileService] Checked legacy mission artifact layout",{baseSessionId:this.baseSessionId,cwd:A,paths:C,skillNames:D}),{status:"hydrated",importedPaths:C,ambiguousSkillNames:D,markedCanonical:$}}async findLegacySkillMatches(T,R){if(R.length===0||!await a1T(T))return new Map;let H=new Set(R),A=new Map,h=await oDA(T);for(let i of h){let t=await Cx(PC.join(i,lDA),"project");if(!t)continue;let B=wo(t.metadata.name);if(!H.has(B))continue;let _=PC.relative(T,i);if(_.startsWith("..")||PC.isAbsolute(_)||_==="")continue;let f=A.get(B)??[];f.push({skillDirPath:i,relativeDir:_}),A.set(B,f)}return A}async hasMissionScopedSkill(T){let R=PC.join(this.missionDir,"skills");if(!await a1T(R))return!1;let H=await oDA(R);for(let A of H){let h=await Cx(PC.join(A,lDA),"project");if(!h)continue;if(wo(h.metadata.name)===T)return!0}return!1}async copyLegacyArtifactIfMissing(T){if(!await a1T(T.sourcePath))return[];if((await c1.stat(T.sourcePath)).isDirectory())return this.copyDirectoryContentsIfMissing(T.sourcePath,T.destinationPath,T.logicalPath);return await this.copyFileIfMissing(T.sourcePath,T.destinationPath)?[T.logicalPath]:[]}async copyDirectoryContentsIfMissing(T,R,H){await c1.mkdir(R,{recursive:!0});let A=[],h=await c1.readdir(T,{withFileTypes:!0});for(let i of h){let t=PC.join(T,i.name),B=PC.join(R,i.name),_=PC.join(H,i.name);if(i.isDirectory()){A.push(...await this.copyDirectoryContentsIfMissing(t,B,_));continue}if(i.isSymbolicLink()){if((await c1.stat(t)).isDirectory())A.push(...await this.copyDirectoryContentsIfMissing(t,B,_));else if(await this.copyFileIfMissing(t,B))A.push(_);continue}if(await this.copyFileIfMissing(t,B))A.push(_)}return A}async copyFileIfMissing(T,R){if(await a1T(R))return!1;await c1.mkdir(PC.dirname(R),{recursive:!0}),await c1.copyFile(T,R);let H=await c1.stat(T);return await c1.chmod(R,H.mode),!0}get stateFilePath(){return PC.join(this.missionDir,"state.json")}async readState(){try{let T=await c1.readFile(this.stateFilePath,"utf-8");return JSON.parse(T)}catch(T){if(T.code!=="ENOENT")$T("[MissionFileService] Failed to read state.json",{baseSessionId:this.baseSessionId,filePath:this.stateFilePath,cause:T});return null}}async readStateOrThrow(){let T=await c1.readFile(this.stateFilePath,"utf-8");return JSON.parse(T)}async writeState(T){T.updatedAt=new Date().toISOString(),await c1.writeFile(this.stateFilePath,JSON.stringify(T,null,2)),this.syncMissionMetadataToCloud()}async createInitialState(T,R="initializing"){let H=new Date().toISOString(),A={missionId:`mis_${Lr().slice(0,8)}`,state:R,workingDirectory:T,createdAt:H,updatedAt:H};return await this.writeState(A),A}async ensurePlanningState(T){if(await this.initializeMissionDir(),await this.readState())return;await this.writeWorkingDirectory(T),await this.createInitialState(T,"planning")}async hasMissionArtifacts(){if((await Promise.all(urB.map((H)=>a1T(PC.join(this.missionDir,H))))).some(Boolean))return!0;if(!await this.missionExists())return!1;let R=await this.readState();return R===null||R.state!=="planning"}async updateState(T){let R=await this.readState();if(!R)throw new VT("Mission state not found for",{baseSessionId:this.baseSessionId});let H={...R,...T};if(await this.writeState(H),T.state!==void 0)kn.emit("project-notification",{notification:{type:"mission_state_changed",state:H.state,updatedAt:H.updatedAt}});return H}get featuresFilePath(){return PC.join(this.missionDir,"features.json")}static normalizeFeature(T){let R=T.milestone,H=typeof R==="number"||typeof R==="boolean"?String(R):typeof R==="string"?R:void 0;return{id:T.id||"",description:T.description||"",skillName:T.skillName||"",preconditions:Array.isArray(T.preconditions)?T.preconditions:[],expectedBehavior:Array.isArray(T.expectedBehavior)?T.expectedBehavior:typeof T.expectedBehavior==="string"?[T.expectedBehavior]:[],fulfills:Array.isArray(T.fulfills)?T.fulfills:void 0,milestone:H,status:T.status||"pending",workerSessionIds:T.workerSessionIds||[],currentWorkerSessionId:T.currentWorkerSessionId??null,completedWorkerSessionId:T.completedWorkerSessionId??null}}async readFeatures(){try{let T=await c1.readFile(this.featuresFilePath,"utf-8");return this.parseFeaturesContent(T)}catch(T){return this.handleReadFeaturesError(T),null}}readFeaturesSync(){try{let T=trB(this.featuresFilePath,"utf-8");return this.parseFeaturesContent(T)}catch(T){return this.handleReadFeaturesError(T),null}}parseFeaturesContent(T){let R=JSON.parse(T),H=Array.isArray(R)?R:R.features;if(!Array.isArray(H))return $T("[MissionFileService] Invalid features.json schema",{baseSessionId:this.baseSessionId,filePath:this.featuresFilePath}),null;return{features:H.map((A)=>IjT.normalizeFeature(A))}}handleReadFeaturesError(T){if(T.code!=="ENOENT")$T("[MissionFileService] Failed to read features.json",{baseSessionId:this.baseSessionId,filePath:this.featuresFilePath,cause:T})}async readFeaturesOrThrow(){let T=await c1.readFile(this.featuresFilePath,"utf-8"),R=JSON.parse(T),H=Array.isArray(R)?R:R.features;if(!Array.isArray(H))throw Error('Invalid features.json: expected { "features": [...] } or a bare array');return{features:H.map((A)=>IjT.normalizeFeature(A))}}async writeFeatures(T){await c1.writeFile(this.featuresFilePath,JSON.stringify(T,null,2)),this.syncMissionMetadataToCloud(),kn.emit("project-notification",{notification:{type:"mission_features_changed",features:T.features}})}async getFeature(T){let R=await this.readFeatures();if(!R)return null;return R.features.find((H)=>H.id===T)??null}getFeatureForWorkerSessionSync(T){let R=this.readFeaturesSync();if(!R)return null;return R.features.find((H)=>H.currentWorkerSessionId===T||(H.workerSessionIds??[]).includes(T))??null}async getInProgressFeature(){let T=await this.readFeatures();if(!T)return null;return T.features.find((R)=>R.status==="in_progress")??null}getInProgressFeatureSync(){let T=this.readFeaturesSync();if(!T)return null;return T.features.find((R)=>R.status==="in_progress")??null}async updateFeature(T,R){let H=await this.readFeatures();if(!H)return null;let A=H.features.findIndex((h)=>h.id===T);if(A===-1)return null;return H.features[A]={...H.features[A],...R},await this.writeFeatures(H),H.features[A]}async getNextPendingFeature(){let T=await this.readFeatures();if(!T)return null;return T.features.find((R)=>R.status==="pending")??null}async areAllFeaturesCompleted(){let T=await this.readFeatures();if(!T)return!1;return T.features.every((R)=>R.status==="completed"||R.status==="cancelled")}async addFeature(T){let R=await this.readFeatures();if(!R){await this.writeFeatures({features:[T]});return}R.features.push(T),await this.writeFeatures(R)}async insertFeatureAtTop(T){let R=await this.readFeatures();if(!R){await this.writeFeatures({features:[T]});return}R.features.unshift(T),await this.writeFeatures(R)}async moveFeatureToBottom(T){let R=await this.readFeatures();if(!R)return;let H=R.features.findIndex((h)=>h.id===T);if(H===-1)return;let[A]=R.features.splice(H,1);R.features.push(A),await this.writeFeatures(R)}async moveStrandedDoneFeaturesToBottom(){let T=await this.readFeatures();if(!T||T.features.length===0)return;let R=(B)=>B.status==="completed"||B.status==="cancelled",H=T.features,A=H.length;while(A>0&&R(H[A-1]))A--;let h=[],i=[];for(let B=0;B<A;B++)if(R(H[B]))h.push(H[B]);else i.push(H[B]);if(h.length===0)return;let t=H.slice(A);T.features=[...i,...t,...h],await this.writeFeatures(T)}async getMilestoneFeatures(T){let R=await this.readFeatures();if(!R)return[];return R.features.filter((H)=>H.milestone===T)}async getAllMilestones(){let T=await this.readFeatures();if(!T)return[];let R=new Set;for(let H of T.features)if(H.milestone)R.add(H.milestone);return Array.from(R)}async isMilestoneImplementationComplete(T){let R=await this.getMilestoneFeatures(T);if(R.length===0)return!1;let H=R.filter((A)=>!jx.includes(A.skillName));if(H.length===0)return!1;return H.every((A)=>A.status==="completed"||A.status==="cancelled")}async hasValidationPlannerRun(T){return(await this.readProgressLog()).some((H)=>H.type==="milestone_validation_triggered"&&H.milestone===T)}get progressLogPath(){return PC.join(this.missionDir,"progress_log.jsonl")}static updateDerivedWorkerStatesFromProgressEntry(T,R,H){if(T.type==="worker_started"){let{workerSessionId:A,timestamp:h}=T;if(H){let t=R[H];if(t&&!t.completedAt)R[H]={...t,completedAt:h}}let i=R[A];return R[A]={...i,startedAt:typeof i?.startedAt==="string"?i.startedAt:h},A}if(T.type==="worker_completed"){let{workerSessionId:A,timestamp:h,exitCode:i}=T,t=R[A];return R[A]={startedAt:t?.startedAt??h,completedAt:h,exitCode:i},H===A?void 0:H}if(T.type==="worker_failed"){let{workerSessionId:A,timestamp:h,exitCode:i}=T;if(A){let t=R[A];return R[A]={startedAt:t?.startedAt??h,completedAt:h,exitCode:i},H===A?void 0:H}}return H}async readProgressLogIncrementalOrThrow(){let T;try{let h=await c1.stat(this.progressLogPath);T={size:h.size,mtimeMs:h.mtimeMs}}catch(h){if(h.code==="ENOENT")return this.progressLogCache=null,{progressLog:[],derivedWorkerStates:{}};throw h}if(this.progressLogCache&&this.progressLogCache.size===T.size&&this.progressLogCache.mtimeMs===T.mtimeMs)return{progressLog:this.progressLogCache.entries,derivedWorkerStates:this.progressLogCache.derivedWorkerStates};let R=this.progressLogCache;if(!R||T.size<R.offset||T.size===R.size&&T.mtimeMs!==R.mtimeMs){let t=(await c1.readFile(this.progressLogPath,"utf-8")).trim().split(`
`).filter((f)=>f.trim()).map((f)=>JSON.parse(f)),B={},_;for(let f of t)_=IjT.updateDerivedWorkerStatesFromProgressEntry(f,B,_);return this.progressLogCache={size:T.size,mtimeMs:T.mtimeMs,offset:T.size,remainder:"",entries:t,derivedWorkerStates:B,activeWorkerSessionId:_},{progressLog:t,derivedWorkerStates:B}}let A=await c1.open(this.progressLogPath,"r");try{let h=R.offset,i=T.size-h;if(i<=0)return this.progressLogCache={...R,size:T.size,mtimeMs:T.mtimeMs,offset:T.size},{progressLog:this.progressLogCache.entries,derivedWorkerStates:this.progressLogCache.derivedWorkerStates};let t=Buffer.alloc(i);await A.read(t,0,i,h);let B=t.toString("utf-8"),f=(R.remainder+B).split(`
`),C=f.pop()??"",$=f.map((k)=>k.trim()).filter(Boolean).map((k)=>JSON.parse(k)),O=[...R.entries,...$],o={...R.derivedWorkerStates},y=R.activeWorkerSessionId;for(let k of $)y=IjT.updateDerivedWorkerStatesFromProgressEntry(k,o,y);return this.progressLogCache={...R,size:T.size,mtimeMs:T.mtimeMs,offset:T.size,remainder:C,entries:O,derivedWorkerStates:o,activeWorkerSessionId:y},{progressLog:O,derivedWorkerStates:o}}finally{await A.close()}}async readProgressLog(){try{let{progressLog:T}=await this.readProgressLogIncrementalOrThrow();return T}catch{return[]}}async readProgressLogOrThrow(){let{progressLog:T}=await this.readProgressLogIncrementalOrThrow();return T}async readProgressLogWithDerivedWorkerStatesOrThrow(){return this.readProgressLogIncrementalOrThrow()}async readProgressLogRaw(){try{return await c1.readFile(this.progressLogPath,"utf-8")}catch{return""}}async appendProgressLog(T){let R={...T,timestamp:T.timestamp||new Date().toISOString()},H=`${JSON.stringify(R)}
