# A17 Snapshot DSL 用法小结

run_id: run-20261013-174209 · 交付：4 张 1200x1600 教学页 + 4 个 400x240 独立示例

## 交付物

| 文件 | 尺寸 | 说明 |
| --- | --- | --- |
| handbook-01.png / .snapshot | 1200x1600 | 第 1 页 调用契约 |
| handbook-02.png / .snapshot | 1200x1600 | 第 2 页 Flex 与 Stack 对照 |
| handbook-03.png / .snapshot | 1200x1600 | 第 3 页 Raw / CDATA / 富文本 / 尾部 alpha |
| handbook-04.png / .snapshot | 1200x1600 | 第 4 页 三种滤镜与可复现自检 |
| example-01..04.png / .snapshot | 400x240 | 四个示例的完整 DSL 与独立真实渲染 |
| examples.json | — | 示例清单：完整 DSL 路径、core 定位、印刷行号与逐字原文、转义形式 |
| verification.json | — | 33 项一致性验证结果（全部通过） |
| sources.md | — | 每条技术结论对应的文档 URL 与原文依据 |

## 渲染方式

```
POST /snapshot
Content-Type: text/plain; charset=utf-8
<body> = .snapshot 文件全文</body>
```

根标签 `<Snapshot type="png" background="...">`；`type` 决定响应体格式（png/jpg/webp）。
`GET /fonts` 返回 text/plain，每行一个字体族（需带 `User-Agent: curl/8.5.0` 访问）。

## 本次用到的 DSL 结构

- **页面骨架**：`<Snapshot>` → 有界 `<Container width height>` → `<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">` → 一串 `<Positioned left top width height>`。绝对定位便于逐项核算坐标与预算。
- **代码块显示**：`<Text ...><Raw ...>code</Raw></Text>`。`Raw` 保留缩进空白，但只能作为最外层 `Text` 的行内子节点；放在 `Text` 外会直接 `PARSE_ERROR`。
- **含 `]]>` 的显示文本**：拆成多段 CDATA——`<![CDATA[a]]]]><![CDATA[>b]]>`，避免提前闭合。
- **教学插图**：外框 `<Container ... padding="32">` 内直接嵌入示例 core 子树，内容盒恰为 400x240，与独立示例 1:1（已用像素比对证明 0 差异）。
- **等宽字体**：`Noto Sans Mono CJK SC`；正文 `Noto Sans CJK SC`；数字标题 `Inter Semi Bold`。

## 版面自检手段

1. **换行预估 + 探针校准**：先用字符宽度模型估算换行，再用透明底批量墨迹探针（分块，单画布不超过 4096 高）实测每行宽度，按实测/预估比校准后重排。
2. **二次探针校验**：重排后再测一遍，任何一行超过可用宽度即报错列出（本次 0 条）。
3. **墨迹边界检查**：对成品 PNG 逐像素取非背景墨迹包围盒，确认左右不越 48px 安全边距、底部不越画布。
4. **一致性验证**：`a17_verify.py` 对落盘文件做 33 项检查——核心子树逐字节相同、印刷行与独立 DSL 行逐字相同、CDATA 往返一致、插图区域与独立示例 PNG 像素级 1:1（0/96000 像素差异）。

## 经验

- `ColorFiltered` 的作用范围是子树绘制边界：圆角矩形外的透明角也会被滤色，滤镜子块用方角可避免彩色角 artefacts。
- 服务存在间歇超时，渲染需带重试；每次尝试都如实记入 `requests.jsonl`。
