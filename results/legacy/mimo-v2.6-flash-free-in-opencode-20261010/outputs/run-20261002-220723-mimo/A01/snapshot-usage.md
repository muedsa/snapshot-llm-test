# A01 · 六个月经营诊断驾驶舱 — 使用报告

- run_id：`run-20261002-220723-mimo`
- 输出目录：`outputs/run-20261002-220723-mimo/A01/`
- 临时目录：`tmp/run-20261002-220723-mimo/A01/`
- 状态：completed（1 轮）

## 1. 实际阅读与应用的文档

| 来源 | 用途 | 记录 ID |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 确认 `POST /snapshot`、`Content-Type: text/plain; charset=utf-8`、`--data-binary`、错误 JSON 结构、`Retry-After` 处理、`/fonts` 用法 | `shared-doc-0001` |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签、颜色/EdgeInsets/对齐/圆角/边框/阴影格式、`Stack`+`Positioned`、`Transform.matrix` 列主序、`Text` 段落属性 | `shared-doc-0003` |
| https://snapshot.muedsa.com/ | 项目能力、类 DOM 解析器入口 | `shared-doc-0002` |
| `GET /fonts`（服务真实返回 27 个字体族） | 选定 `Inter` / `Inter Semi Bold` 与中文 `Noto Sans CJK SC` | `shared-fonts-0001` |

文档要点在本题的真实应用：

- 请求体是 UTF-8 **纯文本**而非 JSON；首次探测因 PowerShell `Set-Content -Encoding UTF8` 写入 BOM 被服务判为
  `400 PARSE_ERROR: Not Support RAWTEXT`。此后所有 DSL 一律用
  `New-Object System.Text.UTF8Encoding($false)` 写出，问题消失（失败响应保留在
  `tmp/.../_suite/probe/failures/`）。
- 颜色统一使用 CSS `#RRGGBB`；`borderRadius` 单角改用 `borderRadiusTopLeft/TopRight`，
  不使用文档未定义的 `"4 4 0 0"` 写法。
- 柱状图、折线图全部由 `Stack` + `Positioned` + `Container` 网格线/柱体构成，
  折线段用 `Transform` 列主序旋转矩阵（`(cos,sin,0,0,-sin,cos,0,0,0,0,1,0,tx,ty,0,1)`）实现，
  未使用任何外部图片；全图纯 DSL。
- `Text` 上显式写 `height="1.2"/"1.3"` 控制行高，避免 Noto CJK 默认行高撑破 KPI 卡与表格行。

## 2. 标签能力实际使用

`Snapshot`（background/type）、`Container`（width/height/padding/margin/color/border/borderRadius/
borderRadiusTopLeft/TopRight/alignment/gradient）、`Column`、`Row`（crossAxisAlignment=END/CENTER）、
`Expanded`、`SizedBox`、`Stack`（clipBehavior=NONE）、`Positioned`、`Align`、`Transform`、`Text`
（color/fontSize/fontFamily/height）。

## 3. 设计选择

- 1600×1000，深色驾驶舱；顶部标题与数据源徽标 → 4 张 KPI → 主区（分组柱图 + 六行明细表）
  → 底部（访问量小图 / 转化率折线小图 / 管理结论）。
- 视觉重点放在**分组柱图**与**四张 KPI**（字号最大、色彩最强），明细表与脚注为次级层级。
- 金额轴与百分比轴严格分离：柱图独占 `0–250,000 元`（步长 50,000、共用零起点），
  访问量图 `0–6,000 次`，转化率图 `10.00%–12.50%`，三者互不共用数轴。
- 退款率 8.00% 的两行（6 月、8 月）用红色标出，对应利润用琥珀色标出，支撑结论。

## 4. 数据与计算

唯一数据源 `inputs/monthly.csv`；计算结果写入 `computed-data.json`：
净收入＝退款前收入−退款，利润＝净收入−成本，退款率＝退款÷退款前收入，
月转化率＝订单÷访问，**总体转化率＝3,045÷27,300＝11.15%（非月比例平均，月均值为 11.19%）**。

## 5. 逐图自检（对照实际图像）

| 检查项 | 结果 |
|---|---|
| 4 张 KPI（总净收入 918,624 元 / 总经营利润 262,124 元 / 总订单 3,045 笔 / 总体转化率 11.15%） | ✅ 通过 |
| 六个月净收入与经营利润分组柱图，共用零起点与同一比例 | ✅ 通过 |
| 访问量与转化率两个共享月份对齐的小图（同为 4月–9月、同 x 位） | ✅ 通过 |
| 六行明细表：月份/净收入/退款率/利润/转化率 | ✅ 通过，金额整数、比例两位小数 |
| 一条有证据的管理结论（三条数值证据） | ✅ 通过 |
| 图表刻度、单位、图例、所有月份、表格内容完整可读 | ✅ 通过 |
| 正文 ≥20、脚注 ≥16 | ✅ 通过（正文 20/34，脚注 16） |
| 百分比与金额不共用混淆数轴 | ✅ 通过 |
| 最后一个月标签 2026-09 存在 | ✅ 通过 |

## 6. 实际问题、修复与验证

1. **渲染 400 PARSE_ERROR（BOM）** → 改用无 BOM UTF-8 写出 → 探针通过。
2. **v01 明细表月份列过窄**：`2026-04` 被折成 3 行并溢出行高。
   修复：列宽 100/120/92/116/116 → 116/116/88/112/112（合计仍为 544）。
   v02 实际看图确认 6 行月份、金额、比例全部单行对齐。
3. 其余未遇到错误；服务无 429/503。

## 7. 请求与迭代统计

- 渲染请求：2 次（A01-render-0001、A01-render-0002），全部 200，`Content-Type: image/png`。
- 失败请求：0（本题）；共享探测阶段失败 1 次（BOM），见 `_suite/requests.jsonl`。
- DSL 版本：2（v01 baseline、v02 visual）。
- 实际看图：2 次；完整视觉迭代：1 次（看 v01 → 改列宽 → 渲染 v02 → 对比）。
- 服务端渲染耗时：`render;dur=1102.5ms`、`render;dur=746.6ms`（`server-timing`）。

## 8. 文件

- 最终图：`outputs/run-20261002-220723-mimo/A01/operations.png`（服务原始 PNG 字节，324,302 B）
- 同名 DSL：`outputs/run-20261002-220723-mimo/A01/operations.snapshot`
- 数据：`outputs/run-20261002-220723-mimo/A01/computed-data.json`
- 指标：`outputs/run-20261002-220723-mimo/A01/task-metrics.json`
- 过程：`tmp/run-20261002-220723-mimo/A01/{v01,v02}.snapshot|.png`、`requests.jsonl`、`iterations.jsonl`

## 9. 未解决事项

无。
