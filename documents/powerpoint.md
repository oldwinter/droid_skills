---
name: powerpoint
description: 生成精美的 PowerPoint 演示文稿（演示稿、幻灯片、路演材料，以及任何“导出为 PowerPoint”的交付物）。当用户要求 PowerPoint、幻灯片集或演示文稿时使用。
---

# 编写 PowerPoint 演示文稿

当用户需要 PowerPoint 时，请编写一组**HTML/CSS 幻灯片**，由 Factory 按需渲染为真正的 `.pptx` 文件。**不要**生成二进制 `.pptx`，**不要**编写脚本，**不要**添加任何演示文稿库或 CDN。

每张幻灯片都是一个使用内联 CSS 设置样式的 `<section class="slide">` 框架。内容是纯 HTML（无脚本、无远程资源），因此可以安全生成。Factory 会验证并渲染每张幻灯片，直接显示预览，并提供可用的 **下载 PowerPoint** 按钮（桌面应用支持下载）。

## 如何生成演示文稿

1. 编写**一个**文件，其名称以 `.pptx.html` 结尾——例如 `deck.pptx.html`,
   `pitch.pptx.html`, `quarterly-review.pptx.html`。用户只会看到 PowerPoint 文件（例如 `deck.pptx`）；`.html` 扩展名只是内部实现细节。
2. 该文件是一个 HTML 文档，每张幻灯片对应一个 `<section class="slide">`，
   并包含一个用于共享样式的 `<style>` 块。
3. **不要**再写入 `.pptx` 文件——PowerPoint 会按需生成，
   且不会持久化到工作区。

## 如何告知用户

将交付物称为 **PowerPoint**（例如：“我已创建演示文稿，请打开预览并下载。”）。不要提及 HTML、CSS 或幻灯片标记格式。

## 幻灯片规则（强制执行）

- 每张幻灯片都必须是 `<section class="slide">…</section>`。演示文稿至少要包含
  一个此类 section；没有 `class="slide"` 的 section 会被忽略。
- 每张幻灯片都按 **16:9、720\xD7405pt（960\xD7540px）的画框**设计。画框
  尺寸固定；不要覆盖 `.slide` 的宽度或高度，请在画框内安排内容。
- **不得包含脚本、事件处理器或远程资源。** `<script>`、`on*`
  handler、远程 `src`/`href`、CSS `@import` 和非 `data:` 的 `url(...)` 都会被移除。任何需要从网络获取的内容也会被删除。
- **图片**必须嵌入为 base64 `data:` URI
  （`data:image/png;base64,…`，也支持 jpeg、gif、webp）。远程 URL 和文件路径会被移除；无法嵌入的图片应直接省略。
- **字体**：使用 Web 安全字体族（例如 Arial、Helvetica、Georgia、
  "Times New Roman"、system-ui），或将字体嵌入为 `data:` URI。不要链接 Google Fonts 或任何远程样式表。

## 如何设计好的幻灯片

- 在 `<style>` 块中使用内联 CSS；类名和绝对定位
  在 `.slide` 中使用效果很好，适用于精确布局。
- 每张幻灯片只保留一个想法：标题、几条要点和辅助视觉效果。
- 使用大方的字体大小（标题 ~40px，正文 ~24px），以便幻灯片易于阅读。
- 使用背景颜色、强调栏和间距来构建视觉层次结构。

## 最小化示例 (`deck.pptx.html`)

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      .slide {
        font-family: Arial, Helvetica, sans-serif;
        color: #1a1a1a;
        padding: 56px 64px;
        background: #ffffff;
      }
      .slide h1 {
        font-size: 44px;
        margin: 0 0 24px;
      }
      .slide.title {
        background: #0b5cff;
        color: #ffffff;
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
      .slide ul {
        font-size: 24px;
        line-height: 1.6;
      }
      .accent {
        color: #0b5cff;
      }
    </style>
  </head>
  <body>
    <section class="slide title">
      <h1>Quarterly Review</h1>
      <p style="font-size: 24px; opacity: 0.85">Q3 2026 \xB7 Product</p>
    </section>
    <section class="slide">
      <h1>Highlights</h1>
      <ul>
        <li>Revenue up <span class="accent">32%</span> quarter over quarter</li>
        <li>Shipped 4 major features ahead of schedule</li>
        <li>NPS improved from 41 to 58</li>
      </ul>
    </section>
    <section class="slide">
      <h1>What's next</h1>
      <ul>
        <li>Expand to two new markets</li>
        <li>Launch the self-serve onboarding flow</li>
      </ul>
    </section>
  </body>
</html>
```
