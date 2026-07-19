---
name: excel
description: 生成精美的 Excel 表格（报告、预算、数据导出，任何“导出为 Excel”的交付物）。每当用户要求 Excel 文件、电子表格或 .xlsx 交付物时都使用此功能。
---

# 编写 Excel 电子表格

当用户需要 Excel 文件时，请编写一份**JSON 工作簿规范**，由 Factory 按需渲染为真正的 `.xlsx` 文件。**不要**生成二进制 `.xlsx`，**不要**编写脚本，**不要**添加任何电子表格库。

规范是纯数据（没有脚本，没有远程资源），这使生成更加安全。Factory 会验证它，在其中显示为一个包含工作表标签的电子表格网格，并提供一个可用的 **下载 Excel** 按钮。

## 如何生成工作簿

1. 编写**一个**文件，其名称以 `.xlsx.json` 结尾——例如 `budget.xlsx.json`、
   `q3-report.xlsx.json`。用户只会将其视为 Excel 文件（例如 `budget.xlsx`）；`.json` 扩展名仅供内部使用。
2. 该文件是一个符合以下 schema 的 JSON 文档。
3. **不要**再写入 `.xlsx` 文件——Excel 文件会按需生成，
   且不会持久化到工作区。

## 告诉用户的内容

将其视为一个 **Excel 文件**（“我已经创建了你的预算表格——打开它预览并下载”）。不要提及 JSON 或规范格式。

## 工作簿规范（以下规则会强制执行）

顶层是 `{ "sheets": [...] }`，包含1 到20 张表格。每张表格：

```jsonc
{
  "name": "Budget",          // required; unique, ≤31 chars, no : \ / ? * [ ]
  "rows": [[...], [...]],    // required; array of rows, each an array of cells
  "columns": [{ "width": 18 }, {}], // optional; widths in Excel character units (1–255)
  "merges": ["A1:C1"],       // optional; A1-style ranges, must not overlap
  "freezeRows": 1,           // optional; header rows kept frozen when scrolling
  "conditionalFormats": [...] // optional; live formatting rules, see below
}
```

每个单元格要么是一个普通的值（例如，`"text"`，`123.45`，`true` 或 `null` 表示空单元格），要么是一个对象：

```jsonc
{
  "value": 1250.5, // string | number | boolean (null = empty cell, styling kept)
  "type": "date", // only with a string ISO value ("2026-06-10" or "2026-06-10T14:30", treated as UTC)
  "formula": "SUM(B2:B9)", // Excel formula WITHOUT the leading "=" (do not combine with "value")
  "result": 10040, // precomputed formula result, shown in the preview
  "numFmt": "$#,##0.00", // Excel number format ("0.0%", "#,##0", "$#,##0.00", ...)
  "bold": true,
  "italic": false,
  "color": "#1A1A2E", // font color, #RRGGBB
  "fill": "#EEF2FF", // background fill, #RRGGBB
  "align": "center", // "left" | "center" | "right"
}
```

### 条件格式化

每个工作表可以包含一个 `conditionalFormats` 数组（不超过 50 项，每项不超过 10 条规则）。每一项针对一个 A1 样式的单元格或范围，并按优先级列出规则——当规则冲突时，较早的规则优先。规则在下载的文件中保持**有效**：Excel 会在用户编辑值时重新评估这些规则。

```jsonc
"conditionalFormats": [
  { "ref": "B2:B13", "rules": [
    // numeric comparison; operator: "equal" | "greaterThan" | "lessThan" | "between"
    // (1 number in "values", or 2 for "between")
    { "type": "cellIs", "operator": "greaterThan", "values": [100], "style": { "fill": "#FFC7CE", "color": "#9C0006", "bold": true } },
    // 2- or 3-color heatmap across the range (min → mid → max)
    { "type": "colorScale", "colors": ["#F8696B", "#FFEB84", "#63BE7B"] },
    // in-cell bar sized to the value, like a mini bar chart
    { "type": "dataBar", "color": "#638EC6" },
    // text matching; operator: "containsText" | "containsBlanks" | "notContainsBlanks"
    // ("text" required for containsText, ≤256 chars, forbidden for the blank operators)
    { "type": "containsText", "operator": "containsText", "text": "OK", "style": { "fill": "#C6EFCE" } },
    // top/bottom N items, or N percent with "percent": true
    { "type": "top10", "rank": 10, "percent": false, "bottom": false, "style": { "bold": true } },
    // above (or below, with "aboveAverage": false) the range's average
    { "type": "aboveAverage", "aboveAverage": true, "style": { "fill": "#FFEB9C" } },
    // any Excel formula (no leading "="); evaluated by Excel in the download,
    // not shown in the inline preview — prefer the typed rules above
    { "type": "expression", "formula": "MOD(ROW(),2)=0", "style": { "fill": "#F2F2F2" } }
  ] }
]
```

`style` 接受 `fill`, `color`（两者都是 `#RRGGBB` 格式），`bold`, 和 `italic`.

当格式用于编码**数据**时，例如阈值（`cellIs`）、热图（`colorScale`）、单元格内数据条（`dataBar`）和离群值（`top10`、`aboveAverage`），应优先使用条件格式而不是手工设置静态填充。这样，值发生变化时工作簿会自动更新。仅对标题行等固定结构使用静态 `fill`/`bold`。

限制：每个工作表最多 10,000 行，每行最多 256 列，总计最多 200,000 个单元格。图表、数据透视表和图片**不**受支持，请改用额外的数据工作表呈现此类分析。

## 如何设计好的电子表格

- 给每张表一个加粗的填充标题行，并设置 '`"freezeRows": 1`'。
- 设置 `columns` 的宽度以便内容可读（文本约 12–30，数字约 10–14）。
- 使用 `numFmt` 格式化货币、百分比和大数字——绝不要直接嵌入格式化后的值。
  格式化为字符串（将 `1250.5` 写作 `"$#,##0.00"`，而不是 `"$1,250.50"`）。
- 使用公式计算总计和派生值，并始终包含 `result` ，以便
  预览会显示计算结果。
- 使用 `conditionalFormats` 使关键数字突出显示——标记超过
  预算使用 `cellIs`，热图化一个指标列使用 `colorScale`，为数量级列添加 `dataBar`。
- 将不相关的数据分布在多个工作表中，而不是一个拥挤的工作表。

## 最小示例 (`budget.xlsx.json`)

```json
{
  "sheets": [
    {
      "name": "Budget",
      "freezeRows": 1,
      "columns": [{ "width": 24 }, { "width": 14 }, { "width": 14 }],
      "rows": [
        [
          { "value": "Item", "bold": true, "fill": "#EEF2FF" },
          {
            "value": "Quantity",
            "bold": true,
            "fill": "#EEF2FF",
            "align": "right"
          },
          { "value": "Cost", "bold": true, "fill": "#EEF2FF", "align": "right" }
        ],
        ["Laptops", 4, { "value": 5196, "numFmt": "$#,##0.00" }],
        ["Monitors", 8, { "value": 2392, "numFmt": "$#,##0.00" }],
        [
          { "value": "Total", "bold": true },
          null,
          {
            "formula": "SUM(C2:C3)",
            "result": 7588,
            "numFmt": "$#,##0.00",
            "bold": true
          }
        ]
      ]
    }
  ]
}
```
