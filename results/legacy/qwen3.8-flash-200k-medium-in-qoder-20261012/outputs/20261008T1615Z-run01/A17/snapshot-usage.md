# A17 · Snapshot 使用说明（四页可实践的 DSL 入门手册）

状态：**completed**。四页 1200×1600 手册 + 四个 400×240 可运行示例全部由
open-snapshot 真实渲染、逐张实际打开看过；`sources.md` 把每条技术结论落到
真实抓取过的文档行，`examples.json` 由 `requests.jsonl` 反推生成，不靠记忆。

## 1. 交付物

| 文件 | 尺寸 | 最终请求号 | 说明 |
|---|---|---|---|
| `handbook-01.png` + `.snapshot` | 1200×1600 | `A17-hb01-v06-20261009T035154Z` | 第1页：调用契约、输入/输出/错误响应 |
| `handbook-02.png` + `.snapshot` | 1200×1600 | `A17-hb02-v06-20261009T035203Z` | 第2页：根尺寸来自布局、有界 Flex/Expanded、Stack 定位 |
| `handbook-03.png` + `.snapshot` | 1200×1600 | `A17-hb03-v06-20261009T035209Z` | 第3页：Raw/CDATA/富文本与尾部 alpha |
| `handbook-04.png` + `.snapshot` | 1200×1600 | `A17-hb04-v09-20261009T040510Z` | 第4页：子树滤镜 vs 背景滤镜、视觉自检、可复现交付 |
| `example-01.png` + `.snapshot` | 400×240 | `A17-example01-v03-20261009T033226Z` | 第1页示例 |
| `example-02.png` + `.snapshot` | 400×240 | `A17-example02-v01-20261009T032145Z` | 第2页示例（v01 即定稿，未制造迭代） |
| `example-03.png` + `.snapshot` | 400×240 | `A17-example03-v02-20261009T032301Z` | 第3页示例 |
| `example-04.png` + `.snapshot` | 400×240 | `A17-example04-v02-20261009T035000Z` | 第4页示例 |
| `sources.md` | — | — | 53 条结论 → URL + 缓存文件:行 + 原文摘句 + 请求号 |
| `examples.json` | — | — | 4 例用途、印刷片段、真实响应、被取代版本 |

PNG 均为服务原始响应字节（`sha256` 与 `tmp/.../A17/preview/requests/*.response.bin`
逐一比对通过），未做任何后处理；`.snapshot` 是产生该图的完整 DSL。

## 2. 真实文档应用

本题实际抓取 7 次文档（`A17-parser-errors-*`×2、`positioned`、`expanded`、
`backdrop-filter`、`image-filtered`、`testing`），另复用 `_suite/docs/` 里
shared 阶段抓好的 8 份（ai-guide、openapi、container、painting、text、rich-text、
clip-rect、rendering）。手册里每条结论的来源与行号见 `sources.md`；其中
`fonts.txt` 是**套件开始前**的探测（响应头 `2026-10-08T08:14:01Z`），没有 per-task
日志，已在 `sources.md` 与 `examples.json` 里如实标注，不冒充本题新请求。

## 3. DSL 能力覆盖

`Snapshot`/`Container`/`SizedBox`/`Stack`/`Positioned`/`Row`/`Column`/`Expanded`/
`Text`/`Raw`/`RichText`/`TextSpan`/`ImageFiltered`/`BackdropFilter`/`ClipRect`/
`ClipRRect`/`DecoratedBox` 类边框与圆角、hex 尾部 alpha、CDATA 内联文本。
四页手册的插图全部由同页 DSL 构件直绘，未嵌入任何外部图片（A 类约束）。

## 4. 关键做法与踩坑（都是看图/看响应头得到的，不是推断）

1. **印刷代码必须与独立运行的是同一份字节。** 生成器直接从 `examples/*.snapshot`
   读行再排版，配合 `sha256` 校验，杜绝“手册写一套、运行另一套”。
2. **`Container` 矮于文字行盒会静默裁字形**，不报错、不告警。第1页流程卡的
   “image/png 字节”被裁后才在生成器里统一按 `ceil(fontSize×1.42)` 加高标签盒。
3. **`Text` trim 空白**：示例里的运算符 ` − ` 被挤成一团，改 `Raw` 才保留。
4. **印刷 `]]>` 会截断自己的 CDATA**，报 `Not Support RAWTEXT: ]]>`
   （`A17-hb01-v01-20261009T032843Z`，400），拆成两个 `Raw` 片段绕开。
5. **代码换行不能切 token**：按 `>` 之后 / 空格串之后 / 非标签起始 `<` 之前断行，
   续行带 `↳` 缩进，否则读者抄到错误的一行。
6. **字号下限与行距要一起调**：为躲裁字把代码降到 19px 会违反 TASK.md 的“代码≥20”，
   回退到 20 后靠行距 29 + 面板加高解决（v05→v06/v08）。
7. **`X-Snapshot-Cache` 不是“相同请求必命中”**：本题 35 次渲染 34 次 `miss`
   （第 35 次是 400，无该头），其中 `hb03-v01`/`hb03-v02` 请求体 sha256 完全相同、
   相隔 109 秒，两次都是 `miss`、都是 422199 字节。全套 237 次渲染只有 7 次 `hit`。
   手册第4页的措辞因此在 v09 从“命中渲染缓存”收敛为“可能命中缓存（取 hit/miss）”。
8. **一次无内容变化的重复请求**（上面第 7 条的 `hb03-v02`）如实记为 `retry`，
   不计作视觉迭代，也不删除。

## 5. 自检与统计

35 次渲染尝试：34 成功、1 次 400；35 条 `iterations.jsonl` 记录
（baseline 8 / visual 21 / requirement-change 4 / syntax-fix 1 / retry 1），
21 次完整视觉迭代都有“看旧图→改→重渲→看并比较”的闭环证据。
每张最终图都实际打开过，第4页定稿前另做了局部放大检查（`preview/crops/`）。

## 6. 剩余事项

- 示例图内文字最小 14px（400×240 画幅下 24px 正文放不下），这是**示例插图**而非
  手册正文；手册正文 24px、代码 20px、边距 48px 均按 TASK.md 执行。
- 缓存命中条件（TTL、是否按实例）文档未说明，本题只报告观测结果，不推断原因。

## 7. 路径

输出 `outputs/20261008T1615Z-run01/A17/`；过程留痕
`tmp/20261008T1615Z-run01/A17/`（`requests.jsonl`、`iterations.jsonl`、
`handbook/`、`examples/`、`preview/`（含 `requests/` 原始请求与响应字节、`crops/`）、
生成脚本 `gen_handbook.py`、`gen_examples.py`、`build_examples_json.py`、
`build_iterations.py`）。基准 `path_base=suite_root`，见 PATHS.md。
