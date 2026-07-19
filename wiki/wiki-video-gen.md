---
name: wiki-video-gen
description: |
  为仓库 Wiki 生成带有 Factory 品牌标识的 HyperFrames 视频概述。
  在 Wiki 生成达到第3.6 阶段时使用，或者当用户要求一个带有叙述的仓库概述视频时使用。
user-invocable: true
---

# Wiki 视频生成

从`droid-wiki/`页面和实际仓库证据中生成精美的仓库概述视频。输出是一个带有清晰 TTS 解说、VTT 字幕、有用架构视觉效果并已准备好上传的 Factory 品牌 MP4 文件。

当此 skill 被 `wiki` skill 调用时，它是 Phase 3.6 的权威实现。`wiki` skill 应在此处委托生成视频，然后在 Phase 4 和 Phase 5 消费此 skill 的输出合同。

## 输出合约

对于仓库 `<repo>`，Wiki 目录 `<wikiDir>` 和标识符 `<slug>`：

- 工作目录: `<repo>/.factory/video/wiki/<slug>/`
- 标准上传文件: `<wikiDir>/video/overview.mp4`
- 标准字幕文件：`<wikiDir>/video/captions.en.vtt`
- 元数据移交：`<repo>/.factory/video/wiki/<slug>/videoOverview.json`
- 可选本地制品：
  - `<wikiDir>/video/overview-poster.png`
  - `<repo>/.factory/video/wiki/<slug>/index.html`
  - `<repo>/.factory/video/wiki/<slug>/assets/`

`wiki-upload` 必须能找到 `<wikiDir>/video/overview.mp4` 和 `<wikiDir>/video/captions.en.vtt`。MP4 只能包含视频流和音频流。字幕由 VTT sidecar 文件提供，并由 Factory Wiki 播放器启用。

元数据文件必须包含以下之一的形状：

```json
{
  "status": "ready",
  "sizeBytes": 12345678,
  "contentType": "video/mp4",
  "generatedAt": "2026-06-02T00:00:00.000Z",
  "durationSeconds": 360,
  "captionTracks": [
    {
      "language": "en",
      "label": "English",
      "sizeBytes": 12345,
      "contentType": "text/vtt"
    }
  ],
  "warnings": []
}
```

```json
{
  "status": "skipped",
  "warnings": ["Video generation skipped via prompt override"]
}
```

```json
{
  "status": "failed",
  "warnings": ["hyperframes doctor failed (exit 1): missing FFmpeg"]
}
```

如果之前使用了视频，不要创建新的 MP4。写入元数据时使用 `status: "ready"`，在 `warnings` 中包含之前的运行 ID 和差异理由，并告诉调用者向 `--copy-from-wiki-run-id <priorWikiRunId>` 传递 `droid wiki-upload`。

## 非谈判项

- 使用 **HyperFrames**，除非用户明确要求使用 Remotion。
- 不要全局安装工具。
- 不要修改仓库的 `package.json`、锁定文件、`.github/workflows` 或 CI 配置。
- 将所有临时工具保持在 `.factory/video/wiki/<slug>/` 下。
- 生成 `<wikiDir>/video/overview.mp4`；不要切换到 slug 化上传路径。
- 确保 MP4 文件在 Wiki 上传限制之下。目标大小 `<90 MB`；在超过`100 MB`之前硬性失败或重新压缩。
- 将所有视觉样式锚定至 Factory Brand System (`https://factory-brand-guide.vercel.app/`.)。
- 不要打包纯文本幻灯片、重复的居中文本卡片或通用的 `FACTORY` 文字品牌标识。
- 在 HyperFrames HTML 中不要渲染可见字幕。字幕必须以 WebVTT 侧边栏的形式生成，而不是嵌入到 MP4 文件中。
- 为每个准备好的视频生成 `<wikiDir>/video/captions.en.vtt`。
- 验证后再报告完成。
- 除非明确要求，否则不要上传至 Factory 云、提交、推送或清理生成的工作空间。由调用者处理上传。

## 阶段0：解决输入参数

按以下顺序推断输入参数:

1. `repoRoot`: 当前 git 仓库根目录。
2. `wikiDir`: 显式用户/调用者值，否则为 `<repoRoot>/droid-wiki`。
3. `repoUrl`: 显式值，否则为 `git remote get-url origin`。
4. `slug`: 显式值，否则为小写的 repo-name slug。
5. `interactive`: 当前会话是否可以询问用户问题。
6. 提示词覆盖:
   - `skip video` 表示跳过而不调用 HyperFrames。
   - `regenerate the video` 表示即使允许重用也强制重新渲染。

如果 `wikiDir` 没有 markdown 页面且没有先前可播放的远程视频存在，则以 `status: "skipped"` 和警告信息跳过，解释说明没有可用源 Wiki 页面。

## 阶段1：增量重用决策

在渲染之前，检查是否有先前的 Wiki 运行生成了一个可播放的视频。

1. 列出先前的 Wiki 运行：
   ```bash
   droid wiki-read --repo-url <repoUrl> --json
   ```
2. 从最近的一个开始，检查每次运行：
   ```bash
   droid wiki-read --wiki-run-id <wikiRunId> --json
   ```
3. 一个运行是可播放的当 `videoOverview.status === "ready"` 且 `playbackUrl` 非空。

如果之前没有可播放的运行记录，无需发出分类行即可进行生成。

当存在先前可玩运行时，计算变更摘要：

```bash
git rev-list --count --since=<generatedAt> HEAD
git log --since=<generatedAt> --oneline --no-merges -10
git diff --shortstat <first-commit-since>^..HEAD -- . ':!*.lock' ':!package-lock.json' ':!*.generated.*'
```

分类代码差异：

- `major`: 10+次提交，或20+个文件更改，或总计500+行更改。
- `minor`: 低于所有主要阈值。
- `minor`: 本地 Wiki 页面缺失/不完整，但之前有可玩运行记录。

打印：

```text
Phase 3.6: Checking for prior playable video...
Phase 3.6: Found prior video from run <wikiRunId> (generated at <generatedAt>)
Phase 3.6: Changes since prior run: <N> commit(s), <M> file(s) changed, <I> insertion(s), <D> deletion(s)
Phase 3.6: Recent commits: <one-line summaries>
video diff classification: minor
```

对于 `minor`，除非提示词包含 `regenerate the video`，否则重用之前的视频。不要调用 `hyperframes render`。返回一个 `copyFromWikiRunId` 手工传递以进行上传，并写入一个警告包含字面分类，例如：

```text
Video diff classification: minor, changes are below regeneration thresholds (3 commits, 5 files, 120 lines)
```

对于 `major`，生成一个新的视频并包含一个警告，其中包含字面的分类信息。

## 阶段 2：交互式门控

在交互模式下，询问：`Generate video overview?`

- 如果用户拒绝，则跳过，并写入 `status: "skipped"` 和警告 `User declined video overview generation`。
- 如果用户接受，则继续。

在非交互模式下，除非提示词包含 `skip video`，否则总是尝试生成。

## 阶段 3：构建故事

使用 `droid-wiki/` 作为私有研究上下文。视频应描述 **仓库**，而不是 Wiki 或文档制品。除非仓库本身是文档产品，否则不要说“droid-Wiki”、“生成的 Wiki”、“Wiki 概览”或“此 Wiki”。

检查：

- `overview/index.md`
- `overview/architecture.md`
- `overview/getting-started.md`
- `by-the-numbers.md`
- 重要镜片索引页面
- 那些页面引用的源文件
- 来自 `<wikiDir>/images/` 的实际截图/资产

构建10-14 场景大纲。优先考虑：

1. repo 特定的钩子
2. 目的和用户价值
3. 二进制文件/应用程序/包
4. 启动或请求流程
5. 主要子系统
6. UI/API 接口
7. 贡献者热点
8. 总结

为每个场景记录场景目标、视觉原型、证据路径、屏幕上的标签以及叙述节奏，然后再编写`index.html`。至少六个场景必须使用基于证据的视觉效果而不是标题/正文内容。非平凡仓库视频不能仅是一系列带有头衔和段落的深色卡片。

使用真实 repo 事实、源路径、图表、指标和实时截图。如果截图为非 live app 证据，请诚实地标记它或改用基于源代码的卡片。

## 叙述规则

叙述应感觉像是一个引导式的漫步，而不是压缩的清单。

- 每个句子表达一个想法。
- 每个场景传达一个概念。
- 大多数口头句子保持在大约22 个字以内。
- 不要叙述长列表。
- 如果一个概念有多个项目，请说出类别并在视觉上展示细节。
- 每个句子最多使用2-3 个口头示例。
- 添加路标如“首先”，“接下来”，“关键点是”和“你可以记住这一点”。
- 以特定于仓库的引子开始，而不是陈词滥调。
- 如果视觉显示列表，请叙述其模式或为什么重要。
- 绝不要加快语速以达到目标时长。减慢速度或接受更长的视频。

当仓库需要时，目标为5-8 分钟。默认目标为5:30-6:30，但清晰度胜过严格的运行时间。

## 品牌规则

应用 Factory 品牌的默认设置，无需等待重新设计的提示词。将每个视觉决策锚定在`https://factory-brand-guide.vercel.app/`. Factory 品牌系统上。在具备浏览能力的会话中，在组合内容之前获取或检查该页面；在离线会话中，请使用下方的备用标记，并编写元数据警告，说明无法查阅实时品牌指南。

以品牌指南为准。截至 2026 年四月版指南：

- 视觉原则：工程化精准度、暗色优先、排版层次和技术可信度。
- 暗色优先画布：`#000000`。
- 主要强调色：Factory 橙色`#EE6018`，仅作为强调色使用。
- 表面与边框：`#161413`表面，`#342F2D`边框，`#9B8E87`灰色，`#948781`页脚灰色，`#FFFFFF`白色，`#F2F0F0`浅背景。
- 图表：橙色渐变`#FF9F2B -> #FF8B00 -> #F35E00`，次要描边`#CBC5C2`，最大半径2px，标签在条形图内侧。
- 排版：Geist Light 300 用于标题和正文，从不加粗；Geist Mono Regular 400 用于标签、元数据、说明文字、计数器和技术文本。
- 字体大小：H1 `56px+`，H2 `28px`，正文 `20px`，说明/标签 `14px`。
- 字间距：默认值为`-1%`。无斜体。除链接外无下划线。
- 几何形状：1px 边框、0-6px 圆角、4px 默认卡片圆角；技术卡片使用直角。
- 图表：深色圆角矩形，1px 边框，90 度连接器，橙色活动流程，单字标签，填充三角箭头，每条连接都有标签。
- 批准的纹理：半调/点阵，微妙的暗颗粒，旋转子/电路图案，ASCII 艺术。不要使用发光斑块、霓虹灯、合成波、渐变网状结构、表情符号、3D 渲染、 stock 照片或大面积橙色填充。
- 标志规则：使用官方白色锁-up 或在深色表面上使用白色旋转子。永远不要旋转、拉伸、重新着色或以橙色渲染标志。
- 语言：说 Factory 或机器人，不在正文中说 FactoryAI。避免“AI 驱动的”、“协作者”、“助手”、“帮手”、“魔法”和空洞的超级形容词。

从指南中获取的品牌资产应在网络访问可用时下载到`assets/brand/`中：

- `https://factory-brand-guide.vercel.app/logos/factory-lockup-white.svg`
- `https://factory-brand-guide.vercel.app/logos/rotor-white.svg`
- `https://factory-brand-guide.vercel.app/images/bg-halftone-rotor.jpg`
- `https://factory-brand-guide.vercel.app/images/bg-ascii.jpg`
- `https://factory-brand-guide.vercel.app/images/elements/halftone-dots.png`
- `https://factory-brand-guide.vercel.app/images/elements/texture-lava-figma.jpg`

当有网络访问时，头部必须使用官方标志资产，加上场景计数器或简洁的仓库标签。如果无法获取官方资产，则仅作为备用使用文本标签，并正确处理 Geist/Geist Mono 字体和元数据警告。

## 阶段 4：设置本地工具

在安装任何内容之前先创建工作区：

```bash
WORK="<repo>/.factory/video/wiki/<slug>"
mkdir -p "$WORK/assets" "$WORK/assets/brand" "$WORK/assets/fonts" "$WORK/out"
cd "$WORK"
```

不要修改仓库级别的 manifest 文件。当需要时，在`package.json`内部创建一个 workspace-local 的`.factory/video/wiki/<slug>/`是可以接受的。

优先使用隔离 Node 运行器来运行 HyperFrames：

```bash
npm exec --package=node@22 --package=hyperframes@0.4.44 -- hyperframes doctor
```

如果需要为 GSAP、FFmpeg 或浏览器设置安装本地依赖项，请仅在`$WORK`中安装它们：

```bash
npm init -y
npm install hyperframes@0.4.44 ffmpeg-static ffprobe-static gsap
```

HyperFrames 需要 Node 22+。如果系统中的 Node 较旧，则可以不全局安装 Node 而通过临时 Node 24 运行：

```bash
PATH="$PWD/node_modules/.bin:$PATH" npx -y -p node@24 node node_modules/hyperframes/dist/cli.js doctor
PATH="$PWD/node_modules/.bin:$PATH" npx -y -p node@24 node node_modules/hyperframes/dist/cli.js browser ensure
```

使用 `lint .` 和 `render .`，而不是 `lint ./index.html` 或 `render ./index.html`。

当网络访问可用时，在构建 `index.html` 之前将品牌指南资源下载到工作区中：

```bash
curl -fsSL https://factory-brand-guide.vercel.app/logos/factory-lockup-white.svg -o assets/brand/factory-lockup-white.svg
curl -fsSL https://factory-brand-guide.vercel.app/logos/rotor-white.svg -o assets/brand/rotor-white.svg
curl -fsSL https://factory-brand-guide.vercel.app/images/bg-halftone-rotor.jpg -o assets/brand/bg-halftone-rotor.jpg
curl -fsSL https://factory-brand-guide.vercel.app/images/bg-ascii.jpg -o assets/brand/bg-ascii.jpg
curl -fsSL https://factory-brand-guide.vercel.app/images/elements/halftone-dots.png -o assets/brand/halftone-dots.png
curl -fsSL https://factory-brand-guide.vercel.app/images/elements/texture-lava-figma.jpg -o assets/brand/texture-lava-figma.jpg
```

如果资源下载失败，请继续使用备用调色板并在 `videoOverview.json` 中写入警告。

## 阶段 5: 文本转语音和字幕

默认情况下，优先使用本地 TTS（例如 Kokoro），当可用时。不要默认使用云 TTS。仅在用户明确批准远程 TTS 备选方案或环境已为此准备时才允许使用 `edge-tts`。

首先编写 `script.txt`，然后将相同内容分割成 `scenes.json`。

字幕要求：

- 生成一个有效的 WebVTT 文件到 `assets/captions.en.vtt`，然后将其复制到 `<wikiDir>/video/captions.en.vtt` 中。
- 不要生成必需的 SRT 辅助文件，并且不要将字幕嵌入 MP4 中。
- 保持字幕片段简短：大约 5-7 个单词并且通常少于 42 个字符。
- 优先使用 HyperFrames 转录或 Whisper 的单词级时间戳。
- 如果原始文本丢失标点符号，请不要将其作为可见的字幕文本使用。
- 从原始脚本中重构可见提示文本，同时保留单词级别的时间戳。
- 规范化时间戳，使提示单调且不重叠。
- 以 `WEBVTT` 开始 VTT 文件，并验证所有提示时间戳使用 `HH:MM:SS.mmm --> HH:MM:SS.mmm` 格式。
- 尽可能检查至少三个字幕过渡。

## 阶段 6：HyperFrames 组合

在工作区创建 `hyperframes.json`, `meta.json`, 和 `index.html`。

组合要求：

- `data-composition-id="main"`
- `data-width="1280"`
- `data-height="720"`
- 精确的 `data-duration` 匹配视觉时间线
- 默认为 1280x720 和 24fps
- 当有用时使用 GSAP 时间线进行场景揭示/进度条
- 先渲染视觉效果；之后使用 FFmpeg 合并叙述，不包含字幕过滤器
- CSS `@font-face` 用于本地字体
- 精简可重用的 CSS 和标记以避免`file_too_large` lint 警告
- 除非必要，否则避免使用巨大的内联 SVG 路径

视觉要求：

- 从 Factory 壳开始：黑色画布，官方白色 Logo 或头部的 rotor 标志，顶部细边线，场景计数器，简洁的仓库/上下文标签，以及底部进度指示器。
- 在视频中至少构建五个不同的布局架构。使用系统地图、请求流图、模块网格、源路径条带、指标/图表、终端/代码片段、屏幕截图提示、贡献者热点和总结帧的混合组合。
- 限制单一卡片布局的重复使用，最多不超过两场。不要将每一场景都渲染为一个居中的表面，仅包含标题、段落和来源行。
- 使用仓库证据作为可见结构：真实的包名、源路径、命令名、API 名、测试名、图表、测量计数以及当可用时从`<wikiDir>/images/`获取的屏幕截图。
- 保持标题和指标为白色。橙色用于每个场景中的一个焦点强调：活动连接器、小标记、进度、图表填充或选定节点。
- 初始化进度条为空，并在整个时间线上进行动画处理。不要在第0 帧就显示满宽度的进度条。
- 使用 CSS 变量来定义品牌调色板和场景令牌。保持可重用组件紧凑，而不是重复标记。
- 当文件可用时，包含`@font-face`规则以使用本地 Geist/Geist Mono 字体。如果缺少本地字体文件，则使用`font-family: Geist, Inter, system-ui`和`Geist Mono, ui-monospace`，然后编写元数据警告。
- 不要在`.captions`中显示可见的`.caption`容器、`index.html`节点或字幕文本。字幕应位于`assets/captions.en.vtt`中，并由 Factory Wiki 播放器展示。
- 不要使用通用的文字品牌，如纯橙色的 `FACTORY` 单词。请使用官方的品牌组合/旋转器资产，或在无法获取资产时仅使用备用的单调文本标签。

## 阶段 7：渲染和复用

在渲染前运行 HyperFrames 医生。医生警告可能会被持久化且不会阻止。医生失败会跳过非交互模式下的渲染，并写入 `status: "failed"` 元数据。

首先渲染仅视觉的 MP4:

```bash
PATH="$PWD/node_modules/.bin:$PATH" npx -y -p node@24 node node_modules/hyperframes/dist/cli.js lint . --verbose
PATH="$PWD/node_modules/.bin:$PATH" npx -y -p node@24 node node_modules/hyperframes/dist/cli.js render . \
  -o out/<slug>-visual.mp4 \
  --fps 24 \
  --quality draft \
  --no-browser-gpu
```

然后复用叙述而不嵌入字幕:

```bash
./node_modules/.bin/ffmpeg -y \
  -i out/<slug>-visual.mp4 \
  -i assets/narration.mp3 \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -ar 48000 \
  -movflags +faststart \
  out/overview.mp4
```

如果第一次渲染/复用失败，请在修复原因后重试一次。如果重试失败，删除任何部分生成的 `<wikiDir>/video/overview.mp4`，写入 `status: "failed"` 元数据，并将控制权返回给调用者。整体 Wiki 生成应保持非致命状态。

从仅视觉的视频中创建海报:

```bash
./node_modules/.bin/ffmpeg -y -ss 00:00:08 -i out/<slug>-visual.mp4 \
  -frames:v 1 -update 1 -vf "scale=1280:720" out/overview-poster.png
```

复制最终产物:

```bash
mkdir -p <wikiDir>/video
cp out/overview.mp4 <wikiDir>/video/overview.mp4
cp out/overview-poster.png <wikiDir>/video/overview-poster.png
cp assets/captions.en.vtt <wikiDir>/video/captions.en.vtt
```

默认情况下不要在 `<video>` 中嵌入 `overview/index.md` 标签。Factory 云渲染使用 `videoOverview` 元数据和上传的 MP4。只有当用户明确要求本地 Wiki 嵌入时才添加 markdown/HTML 嵌入。

## 验证关卡

在报告完成前运行适用的验证器:

```bash
PATH="$PWD/node_modules/.bin:$PATH" npx -y -p node@24 node node_modules/hyperframes/dist/cli.js lint . --verbose
./node_modules/.bin/ffmpeg -v error -i <wikiDir>/video/overview.mp4 -f null -
./node_modules/.bin/ffprobe -v error \
  -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,duration \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  <wikiDir>/video/overview.mp4
git -C <repo> status --short -- .github/workflows
```

还请验证:

- MP4 存在且大小 `>0`。
- MP4 的第 4-7 字节是 ASCII `ftyp`。
- 恰好包含一个视频流和一个音频流。
- 格式包含 `mp4`。
- 大小 `<100 MB`，最好 `<90 MB`。
- `<wikiDir>/video/captions.en.vtt` 存在且大小 `>0`，以 `WEBVTT` 开头，并且 cue 时间单调递增。
- 如果引用了可选的 sidecar/海报，则本地 Wiki 资产链接有效。
- 海报图片不含字幕行。

如果可以，请使用具备图像检查功能的 `Read` 工具检查海报。如果海报包含字幕或出现不自然的空白帧，请从约 6-10 秒处的稳定画面重新生成。

视觉质量门控:

- 渲染前检查 `index.html`。如果其中包含可见的 `.caption` 元素、重复的单卡场景结构、缺少品牌外壳、缺少官方/备用品牌处理，或缺少基于证据的图表/路径/指标，则判定失败并修订。
- 复用前至少检查视觉 MP4 中的一张海报或一帧画面。如果它看起来像通用文本演示文稿、左上角存在未格式化的字幕文本、使用橙色标题或大面积橙色填充、缺少 Factory 页眉，或显示已填满的进度条，则判定失败并修订。
- 对于包含超过10 个 Wiki 页面或超过10 个场景的非平凡仓库，通常一个时长少于4:30 的新视频过于压缩。除非源仓库确实很小，否则请使用较慢的叙述速度和更丰富的场景节奏进行重建。
- 验证 `assets/brand/` 是否包含下载的品牌指南资产（前提是网络访问可用）。如果资产不可用，请确认元数据警告解释了回退情况。

## 故障排除

- 如果 HyperFrames 接收到`./index.html`，请在项目目录`.`中重试。
- 如果医生无法找到 Chrome，请在工作区内部运行 `hyperframes browser ensure`。
- 如果 Node 版本太旧，请使用 `npx -y -p node@24 node ...`；不要全局安装 Node。
- 如果发现重复的媒体，请移除重复的 `<img>` 引用，并使用 CSS 背景或持久覆盖层。
- 如果代码检查警告文件过大，请减少重复的标记/资产并压缩生成的 HTML。
- 如果叙述感觉仓促，请降低 TTS 速率或将视频运行时间设为更长。
- 如果字幕太长或过于侵入，请将其拆分为较短的 WebVTT 提示。
- 如果字幕过早或过晚更改，请从单词级别的时间戳或更短的 TTS 片段重新构建。
- 如果字幕丢失标点符号，请从原始脚本中重构提示文本。
- 如果最终时长与音频相差几秒，请将视觉时长设为容器时长，但确保音频完整。

## 完成响应

保持最终响应简洁：

- MP4 路径。
- 时长、分辨率、帧率、大小。
- 视频是否新生成或重用。
- 验证结果。
- 任何写入`videoOverview.json`的警告信息。
