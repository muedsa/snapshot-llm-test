# A21 · 真实需求变更：双尺寸发布物（三轮） — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A21/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A21/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

按预置需求连续执行三轮，每轮交付 1080×1350 竖版与 1440×810 横版各一张，并保存同名 DSL、design-tokens.json 与 content-map.json。第一轮深色主题、单行标题；第二轮把标题换成 24 字长句（竖版 2 行，≤3 行）并加入赞助方与参加方式；第三轮改浅色主题，逐条校验对比度（最差 5.02:1）并新增英语短句。旧轮全部保留。

| 文件 | 说明 |
|---|---|
| [round-01/launch-portrait.png](round-01/launch-portrait.png) | 第 1 轮竖版 |
| [round-02/launch-portrait.png](round-02/launch-portrait.png) | 第 2 轮竖版 |
| [round-03/launch-portrait.png](round-03/launch-portrait.png) | 第 3 轮竖版 |
| [round-01/launch-wide.png](round-01/launch-wide.png) | 第 1 轮横版 |
| [round-02/launch-wide.png](round-02/launch-wide.png) | 第 2 轮横版 |
| [round-03/launch-wide.png](round-03/launch-wide.png) | 第 3 轮横版 |
| [round-01/design-tokens.json](round-01/design-tokens.json) | 设计令牌 |
| [round-02/design-tokens.json](round-02/design-tokens.json) | 设计令牌 |
| [round-03/design-tokens.json](round-03/design-tokens.json) | 设计令牌 |
| [round-01/content-map.json](round-01/content-map.json) | 内容映射 |
| [round-02/content-map.json](round-02/content-map.json) | 内容映射 |
| [round-03/content-map.json](round-03/content-map.json) | 内容映射 |
| [round-03/contrast-audit.json](round-03/contrast-audit.json) | 对比度审计 |
| [task-metrics.json](task-metrics.json) | 三轮汇总指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 三轮各两张、尺寸 1080×1350 / 1440×810 | 六张 PNG 均按尺寸渲染 | 通过 |
| 必含文案（首轮） | 让复杂信息变得清晰 / 2026.11.07 19:30 / ONLINE LAUNCH / 讲者 / 网址 | 通过 |
| 主标题 ≥56、其余 ≥24（首轮） | 竖版 64、横版 56；其余 26–34 | 通过 |
| 同一主色与字体层级、3–6 构件品牌图形 | 三层圆角方 + 核心点，两尺寸复用同一函数 | 通过 |
| 分别构图、不用整图嵌入 | 竖/横两套版式，全部 DSL 绘制 | 通过 |
| 顶部/底部留扩展空间且不写待添加文字 | 竖版标题下方留空，无占位文字 | 通过 |
| 第二/三轮保留日期、讲者、ONLINE LAUNCH、网址 | content-map 逐条记录 | 通过 |
| 第二轮长标题 ≤3 行、≥48 | 竖版 54px 2 行、横版 48px 2 行 | 通过 |
| 第三轮浅色主题、全部文字 ≥4.5:1 | 最差 5.02:1 | 通过 |
| 第三轮新增英语短句 ≥24 | Clarity through structure，28px | 通过 |
| 赞助方不消失 | 第二、三轮均含联合呈现行 | 通过 |
| 逐轮 design-tokens / content-map / 报告 | 每轮各两份 JSON，任务根汇总报告与指标 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| round-01 竖版/横版 | 深色、单行标题、品牌三层方块；竖版下方保留扩展空间 | 通过 |
| round-02 竖版/横版 | 长标题折成 2 行不溢出；赞助方与参加方式填入预留空间 | 通过 |
| round-03 竖版/横版 | 浅色主题、对比度全部通过、英语短句在网址上方 | 通过 |

## 4. 设计与排版决策

- 三轮共用同一套版式函数，只替换文案与主题令牌，因此“同一主色、同一字体层级、同一品牌图形”是可验证的。
- 首轮故意在标题下留出约 400px：第二轮新增两行信息正好填进去，不需要压缩任何既有元素。
- 第三轮把深色换成浅色时，逐个文字计算对比度而不是只看主题色，最差项是最浅的强调色。

## 5. DSL 能力与文档应用

- 标题按词元折行后逐行绘制，避免渲染器二次折行；每行宽度预留 4% 余量。
- 品牌图形由三层圆角方 + 一个核心圆点组成，缩放只改参数，不改结构。
- 所有文字直接画在纯色底上，没有半透明叠层压在文字下，因此对比度即字色与底色的比值。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 首轮竖版中部留白偏大 | 第一轮内容少，预留了扩展空间 | 第二轮加入赞助方与参加方式后自然填补，属设计意图 |
| 长标题在竖版可能超 3 行 | 24 字 54px 折行不确定 | 按 900px 宽折行，实测 2 行；预留 3 行高度 |

## 三轮变化

- round-01：深色底 #0E1626，标题「让复杂信息变得清晰」64px 单行
- round-02：同主题，标题换 24 字长句（54px 2 行），新增赞助方与「免费参加 · 无需报名」
- round-03：浅色底 #F8F4EC，新增「Clarity through structure」，最差对比度 5.02:1（flag）
- 请求 6 次（成功 6），看图 6 次，墙钟 214.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A21/round-01/launch-portrait.png` | 第 1 轮竖版 |
| `outputs/20261103T152640-suite/A21/round-02/launch-portrait.png` | 第 2 轮竖版 |
| `outputs/20261103T152640-suite/A21/round-03/launch-portrait.png` | 第 3 轮竖版 |
| `outputs/20261103T152640-suite/A21/round-03/contrast-audit.json` | 对比度审计 |
| `tmp/20261103T152640-suite/A21/requests.jsonl` | 六次渲染请求 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
