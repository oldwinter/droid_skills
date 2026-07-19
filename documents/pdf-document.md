---
name: pdf-document
description: 生成精美的 PDF 文档（报告、发票、简历、信件、传单、证书，任何“导出为 PDF”的交付物）。每当用户要求 PDF 或可打印的文档时使用。
---

# 创建 PDF 文档

当用户需要 PDF 时，请编写一份结构化的**文档规范**，由 Factory 按需渲染为真正的矢量 PDF。**不要**生成二进制 `.pdf`，**不要**编写 HTML，**不要**添加任何 PDF 库或 CDN。

规范是一个使用 [pdfmake](https://pdfmake.github.io/docs/) 的 `docDefinition`，并序列化为 JSON。它只包含数据（没有脚本、没有 DOM），因此可以安全生成。Factory 会验证规范并渲染清晰的矢量 PDF（文本可选中，分页真实），在 Web 和桌面端直接显示预览，并提供可用的 **下载 PDF** 按钮。

## 如何生成文档

1. 编写**一个**文件，其名称以 `.pdf.json` 结尾——例如 `report.pdf.json`、
   `invoice.pdf.json`、`resume.pdf.json`。用户只会将其视为 PDF 文件（例如 `report.pdf`）；`.json` 扩展名仅供内部使用。
2. 文件内容是一个 JSON 对象，即 pdfmake `docDefinition`。
3. **不要**再写入 `.pdf` 文件——PDF 会按需生成，
   不会持久化到工作区。

## 如何告知用户

将交付物称为 **PDF**（例如：“我已创建报告 PDF，请打开预览并下载。”）。不要提及 HTML、JSON、pdfmake 或规范格式。

## 规范规则（这些会被强制执行，请遵守）

- **顶级键**（仅限以下键）：`content`（必填）、`styles`、
  `defaultStyle`、`pageSize`、`pageOrientation`（`"portrait"` | `"landscape"`）、`pageMargins`、`header`、`footer`、`info`、`images`、`background`、`watermark`、`compress`、`language`。未知的顶级键会被拒绝。
- **字体**：仅可用 `"Roboto"`。不要设置任何其他 `font`。使用
  `bold`/`italics` 和 `fontSize` 来强调内容。
- **图片**：必须是 base64 `data:` URI（例如 `data:image/png;base64,…`，也支持 jpeg、
  gif、webp）。远程 URL 和文件路径会被拒绝。可以将 `image` 值内联为 data URI，也可以在顶级 `images` 映射中声明一次，再按名称引用。无法嵌入的图片应省略。
- `header`/`footer` 必须是静态内容（对象/字符串/数组），而不是
  函数——JSON 本来就无法包含函数。

## 可在 `content` 中使用的功能

- 带格式的文本：`{ "text": "Title", "style": "h1" }`，并可使用 `bold`、
  `italics`、`fontSize`、`color`、`alignment`、`margin: [l, t, r, b]`。
- 富文本片段：`{ "text": ["plain ", { "text": "bold", "bold": true }] }`。
- 列表：`{ "ul": [...] }` / `{ "ol": [...] }`。
- 分栏：`{ "columns": [ {...}, {...} ] }`（每列使用 `width`）。
- 表格：`{ "table": { "headerRows": 1, "widths": ["*", "auto"],
  "body": [[...], [...]] }, "layout": "lightHorizontalLines" }`。
- 间距辅助：`margin`、`{ "text": "", "margin": [0, 8] }`。
- 页面控制：在节点上使用 `pageBreak: "before"` / `"after"`。

## 最小示例 (`invoice.pdf.json`)

```json
{
  "pageSize": "A4",
  "pageMargins": [40, 50, 40, 50],
  "defaultStyle": { "font": "Roboto", "fontSize": 11 },
  "styles": {
    "h1": { "fontSize": 22, "bold": true, "margin": [0, 0, 0, 12] },
    "label": { "color": "#666666" }
  },
  "content": [
    { "text": "Invoice", "style": "h1" },
    {
      "columns": [
        { "text": [{ "text": "Billed to\n", "style": "label" }, "Acme Inc."] },
        {
          "text": [{ "text": "Invoice #\n", "style": "label" }, "INV-001"],
          "alignment": "right"
        }
      ],
      "margin": [0, 0, 0, 20]
    },
    {
      "table": {
        "headerRows": 1,
        "widths": ["*", "auto", "auto"],
        "body": [
          [
            { "text": "Description", "bold": true },
            { "text": "Qty", "bold": true },
            { "text": "Amount", "bold": true }
          ],
          ["Consulting", "10", "$1,000.00"],
          ["Support", "1", "$250.00"]
        ]
      },
      "layout": "lightHorizontalLines"
    },
    {
      "text": "Total: $1,250.00",
      "bold": true,
      "alignment": "right",
      "margin": [0, 16, 0, 0]
    }
  ]
}
```
