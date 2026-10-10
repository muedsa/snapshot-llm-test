# Snapshot 使用情况说明与踩坑记录

- 任务ID：**B02**
- 任务名称：为一个自选项目设计完整视觉生态（候鸟湾观鸟站 · 十个触点）
- 本次运行ID：`run-20261002-220723-mimo`
- 完成状态：**完成**
- 结束原因：需求满足并完成视觉自检（10 件主作品全部渲染成功、逐件实际看图、
  跨作品审查发现并修复两处星期错误、最终逐件复看通过）
- 输出目录：`outputs\run-20261002-220723-mimo\B02`
- 临时目录：`tmp\run-20261002-220723-mimo\B02`

---

## 1. 最终产物与需求完成情况

### 1.1 十件主作品

| 文件 | 用途 | 对应DSL或图片 | 尺寸 | 完成状态 |
|---|---|---|---|---|
| `case-01/final.snapshot` | 完整可复现DSL（46,474 B） | `case-01/final.png` | 1080×1620 | 完成 |
| `case-01/final.png` | 服务返回的最终图片（220,101 B） | `case-01/final.snapshot` | 1080×1620 | 完成 |
| `case-02/final.snapshot` | 完整可复现DSL（27,148 B） | `case-02/final.png` | 1920×720 | 完成 |
| `case-02/final.png` | 服务返回的最终图片（165,945 B） | `case-02/final.snapshot` | 1920×720 | 完成 |
| `case-03/final.snapshot` | 完整可复现DSL（15,167 B） | `case-03/final.png` | 900×1600 | 完成 |
| `case-03/final.png` | 服务返回的最终图片（154,699 B） | `case-03/final.snapshot` | 900×1600 | 完成 |
| `case-04/final.snapshot` | 完整可复现DSL（34,590 B） | `case-04/final.png` | 1920×1080 | 完成 |
| `case-04/final.png` | 服务返回的最终图片（222,559 B） | `case-04/final.snapshot` | 1920×1080 | 完成 |
| `case-05/final.snapshot` | 完整可复现DSL（14,897 B） | `case-05/final.png` | 1000×1400 | 完成 |
| `case-05/final.png` | 服务返回的最终图片（168,065 B） | `case-05/final.snapshot` | 1000×1400 | 完成 |
| `case-06/final.snapshot` | 完整可复现DSL（23,050 B） | `case-06/final.png` | 830×1170 | 完成 |
| `case-06/final.png` | 服务返回的最终图片（87,951 B） | `case-06/final.snapshot` | 830×1170 | 完成 |
| `case-07/final.snapshot` | 完整可复现DSL（9,145 B） | `case-07/final.png` | 1040×660 | 完成 |
| `case-07/final.png` | 服务返回的最终图片（72,427 B） | `case-07/final.snapshot` | 1040×660 | 完成 |
| `case-08/final.snapshot` | 完整可复现DSL（22,823 B） | `case-08/final.png` | 1748×760 | 完成 |
| `case-08/final.png` | 服务返回的最终图片（159,482 B） | `case-08/final.snapshot` | 1748×760 | 完成 |
| `case-09/final.snapshot` | 完整可复现DSL（37,103 B） | `case-09/final.png` | 1080×1080 | 完成 |
| `case-09/final.png` | 服务返回的最终图片（135,315 B） | `case-09/final.snapshot` | 1080×1080 | 完成 |
| `case-10/final.snapshot` | 完整可复现DSL（12,986 B） | `case-10/final.png` | 1080×1526 | 完成 |
| `case-10/final.png` | 服务返回的最终图片（191,282 B） | `case-10/final.snapshot` | 1080×1526 | 完成 |

每件另配 `case-NN/case.md`（场景 / 内容 / 视觉选择 / 实际自检 / 素材情况 /
自定完成标准）。`case-01..case-05/failures/` 内保留 7 份 400 错误响应原文字节。

**字节校验**：10 张最终 PNG 的文件字节数与 `requests.jsonl` 中**该用例最后一次
成功响应**的 `bytes` 字段逐一相等（220101 / 165945 / 154699 / 222559 / 168065 /
87951 / 72427 / 159482 / 135315 / 191282），说明交付图即服务原始响应字节、
未经任何后处理。PNG IHDR 尺寸与 DSL `<Container>` 宽高逐一相等。

### 1.2 输出根其余交付

| 文件 | 完成状态 |
|---|---|
| `project-brief.md` | 完成——说明解决了什么项目问题（四个真实痛点 → 十件作品） |
| `design-system.json` | 完成——13 个组件 + 实测字号分布 + 14 条跨作品不变量 + `reuse_findings.status = complete`（9 条复用结论，含 1 条反例） |
| `touchpoint-map.json` | 完成——10 个触点 × 8 个旅程阶段，含受众/时机/地点/观看距离/停留时长/交给下游的内容与独立性检查 |
| `portfolio.json` | 完成——逐件元数据、完成标准、看图证据、`final_collection_review`（10 项检查全 pass） |
| `portfolio.md` | 完成——策展逻辑与各作品用途 |
| `gallery.html` | 完成——本地画廊，相对链接、无远程脚本、点击按原尺寸查看，索引全部 10 张终版与其余 7 份文档 |
| `snapshot-usage.md` | 本文件 |
| `task-metrics.json` | 完成——墙钟、请求、迭代、看图、消耗 |

### 1.3 需求满足情况

| 题目要求 | 实际 | 结果 |
|---|---|---|
| 至少 10 件独立完整作品 | 10 件，10 种互不重复的画幅，10 个不同的主任务 | 满足 |
| 每件 `final.png` + `final.snapshot` + `case.md` | 各 10 份 | 满足 |
| 最终 PNG 为实际服务响应 | 10/10 字节数与响应 `bytes` 相等 | 满足 |
| 主体工作必须是 DSL | 10 件全部纯 DSL，无外部素材嵌入 | 满足 |
| `project-brief.md` / `design-system.json` / `touchpoint-map.json` | 三份均已交付 | 满足 |
| 每张成功响应实际打开观察 | `iterations.jsonl` 33 行 `viewed=true` 覆盖 10 件；另有终版补看 | 满足（见 §3.4 的取证说明） |
| 复用组件在不同密度/比例下有效 | `design-system.json` → `reuse_findings` 逐组件给出密度测试与实测参数 | 满足 |
| 跨作品一致性 | 14 条不变量逐条核对；审查中发现并修复 2 处星期错误 | 满足 |
| 标注虚构信息 | 全部数据标注「演示数据 DEMO」，`portfolio.json` 写明虚构 | 满足 |

**未满足项**：无。

---

## 2. 文档阅读与实际使用的能力

- 服务基地址：`https://open-snapshot.muedsa.com`（以总 `run-config.json` 为准，
  覆盖子题 run-config 的默认值）
- 接口：`POST /snapshot`，请求体 UTF-8 **纯文本**（不是 JSON），
  `Content-Type: text/plain; charset=utf-8`，无凭据
- 文档版本或访问日期：**AI 使用指南与框架文档在本 run 的 B01 阶段真实抓取并缓存**
  （`tmp/run-20261002-220723-mimo/B01/doc-ai-guide.md` 等）。B02 本身
  **未发起新的文档 HTTP 请求（document_requests = 0）**，直接复用同一 run 内
  已真实取得的缓存文件——这符合总约定「可复用已真实取得的结果」，
  并在 `tool-usage.jsonl` 的 `tu-10` 中登记，不重复计入请求消耗。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `doc-ai-guide.md`（B01 缓存，源自 `https://open-snapshot.muedsa.com/ai-guide.md`） | `POST /snapshot` 为纯文本体、非 JSON；非成功响应是含 `code`/`message`/`requestId` 的 JSON；`400 PARSE_ERROR` 按消息中的 position 修正 DSL 后再提交；成功响应是图片二进制，须先看 HTTP 状态与 Content-Type 再使用文件；`429`/部分 `503` 参考 `Retry-After`；默认不加 `?errorImage=png` 以免把错误写进图片 | `tmp/.../B01/doc-ai-guide.md`；`gen-b02-a.ps1` / `gen-b02-b.ps1` 的生成期校验；`_suite/render.ps1` 的状态检查与失败落盘 |
| `doc-parser-tags.txt`（B01 缓存，源自 `https://snapshot.muedsa.com/`） | `fontStyle` 是枚举、只接受大写 `BOLD`；`gradientBegin`/`gradientEnd` 取 `BoxAlignment` 枚举而非数值；`border` 形如 `"width style color"`；`<Positioned>` 只能是 `<Stack>` 的直接子元素；`Transform matrix` 需外层括号、无空格、16 个有限浮点数 | `lib-b02.ps1` 的 `T` / `Box` / `Circle` / `Transform` 封装；`patch-bold.ps1` |
| `doc-guides-layout.html` / `doc-guides-media-text.html` / `doc-guides-painting.html` / `doc-guides-widgets.html` / `doc-guides-concepts.html`（B01 缓存） | 布局与裁剪链、`SWEEP` 渐变的声明行为、文本 `maxLine` 与自动换行的边界 | 进度环方案选型（见 §4 的 SWEEP 反例）、`Fit`/`TW` 宽度校验 |

### 2.1 本次真正用到的 DSL 能力（只记录实际使用）

| 能力 | 具体用法 | 出现在 |
|---|---|---|
| 根节点与画布 | `<Snapshot type="png">` + 单个 `<Container width height color>` 决定画幅 | 10 件全部 |
| 绝对定位 | `<Stack>` 下的 `<Positioned left top width height>` 做三栏/网格分区（**Positioned 只作为 Stack 的直接子元素**） | case-01/02/03/04/05/07/08/09/10 |
| 变换 | `Transform matrix="(...)"` 16 元仿射：人字鸟阵斜段、装饰条斜置、`DialArc` 的 100 段旋转 | case-01/03/04/06/09/10 |
| 形状 | 圆角矩形（`borderRadius`）、圆（`C`）、`border="宽度 样式 颜色"` | 10 件全部 |
| 颜色 | `#RRGGBB` / `#RRGGBBAA`；半透明仅用于分隔线与遮罩 | 10 件全部 |
| 文本 | `fontFamily`、`fontSize`、`fontStyle="BOLD"`、`textAlign`、`maxLine` | 10 件全部 |
| 中文长句 | **手动断行**（`TLines` 逐行输出 `<Text>`），不使用自动换行，杜绝行首标点 | case-01/05/10 |
| 裁剪 | `<C>` 圆形裁剪链做进度环与环内留白 | case-01/09 |
| 图片 | — | **未使用**（纯 DSL，无 `<Image>`） |
| 滤镜 | — | **未使用**（B01 的能力探针已证实 `ColorFiltered` + `borderRadius` 组合会残留洋红角，本次直接避开） |
| 渐变 | 曾尝试 `SWEEP` 渐变表达进度比例 | **实测不生效，已弃用**（见 §4） |

### 2.2 字体

- **本题未发起 `/fonts` 查询（document_requests = 0）**；沿用本 run 内
  已真实取得的字体可用性结论，10 件统一 `fontFamily="Noto Sans CJK SC"`。
- 服务是确定性的：把已归档的 DSL 原样重发可复现完全相同的字节数（在
  `attempts/` 的重建过程中验证过一次，见 §4 的 case-05 归档）。
- 字号实测：从 10 份 `final.snapshot` 的 `fontSize` 属性直接统计，
  并集为 `12,13,14,15,16,17,18,19,20,21,22,23,24,26,30,33,34,35,36,44,46,50,52,74,84`，
  逐件数值写入 `design-system.json` → `typography.measured`。

---

## 3. 迭代过程、服务调用与图像检查

- 请求记录文件：`tmp/run-20261002-220723-mimo/B02/requests.jsonl`（**39 行，0 行坏 JSON**）
- 迭代记录文件：`tmp/run-20261002-220723-mimo/B02/iterations.jsonl`（**43 行，0 行坏 JSON**）
- 工具记录文件：`tmp/run-20261002-220723-mimo/B02/tool-usage.jsonl`（**14 行，0 行坏 JSON**）
- 渲染请求总数：**39**（38 条 `type=render` + 1 条 `type=render_transport_error`）
- 成功次数：**31**（HTTP 200）
- 失败次数：**8**（7 条 `400 PARSE_ERROR` + 1 条 DNS 传输失败，无 HTTP 交换）
- 重试请求数：**4**（`B02-c06-r1-retry` / `B02-c07-r1-retry` / `B02-c09-r1-retry` /
  `B02-c10-r1-retry`，是总请求的子集；均在 DNS 故障后的重试窗口发起，
  实际携带了更新后的 DSL，同时也是各用例视觉迭代的渲染，只计一次）
- DSL版本数：**38**（逐用例 7/3/3/8/3/2/3/2/3/4）
- 实际图片查看次数：**47**（拆分见 §3.4）
- 完整视觉迭代数：**20**
- 未完成视觉迭代数：**2**（`ite-B02-view-cache-v1`、`ite-B02-c04-v6-incomplete`，均因读图返回错误字节）
- 其他接口查询：**0**（本题未发起文档、字体或其它接口请求；复用 B01 缓存）

迭代类型分布：`baseline 10` / `visual 20` / `visual-incomplete 2` /
`syntax-fix 7` / `requirement-change 3` / `evidence-correction 1` = 43。

### 3.1 渲染请求全表

时间列为 UTC（`requests.jsonl` 的 `started_utc`），与日志中的含时区字段一致。

| 请求ID | 用例 | started (UTC) | 耗时 ms | 状态 | 响应字节 | 响应/错误文件 | 看图 |
|---|---|---|---|---|---|---|---|
| B02-c01-r1 | case-01 | 2026-10-05T09:53:13.098Z | 1918.3 | 400 | 238 | `case-01/failures/B02-c01-r1.body` | — |
| B02-c02-r1 | case-02 | 2026-10-05T09:53:15.114Z | 1973.4 | 400 | 213 | `case-02/failures/B02-c02-r1.body` | — |
| B02-c03-r1 | case-03 | 2026-10-05T09:53:17.106Z | 1675.7 | 400 | 238 | `case-03/failures/B02-c03-r1.body` | — |
| B02-c04-r1 | case-04 | 2026-10-05T09:53:18.801Z | 1780.5 | 400 | 238 | `case-04/failures/B02-c04-r1.body` | — |
| B02-c05-r1 | case-05 | 2026-10-05T09:53:20.603Z | 1721.1 | 400 | 238 | `case-05/failures/B02-c05-r1.body` | — |
| B02-c01-r2 | case-01 | 2026-10-05T09:56:32.545Z | 4390.1 | 200 | 211794 | `case-01/final.png` | 已看（基线） |
| B02-c02-r2 | case-02 | 2026-10-05T09:56:37.004Z | 3707.9 | 200 | 152262 | `case-02/final.png` | 已看（基线） |
| B02-c03-r2 | case-03 | 2026-10-05T09:56:40.729Z | 3390.0 | 200 | 148684 | `case-03/final.png` | 已看（基线） |
| B02-c04-r2 | case-04 | 2026-10-05T09:56:44.134Z | 3025.9 | 200 | 207041 | `case-04/final.png` | 已看（基线） |
| B02-c05-r2 | case-05 | 2026-10-05T09:56:47.174Z | 3105.4 | 200 | 165540 | `case-05/final.png` | 已看（基线） |
| B02-c02-r3 | case-02 | 2026-10-05T10:05:47.176Z | 3532.6 | 200 | 165945 | `case-02/final.png` | 已看 |
| B02-c03-r3 | case-03 | 2026-10-05T10:05:50.774Z | 3262.1 | 200 | 154699 | `case-03/final.png` | 已看 |
| B02-c04-r3 | case-04 | 2026-10-05T10:05:54.051Z | 1713.7 | 400 | 257 | `case-04/failures/B02-c04-r3.body` | — |
| B02-c01-r3 | case-01 | 2026-10-05T10:07:09.966Z | 1864.1 | 400 | 240 | `case-01/failures/B02-c01-r3.body` | — |
| B02-c04-r3 | case-04 | 2026-10-05T10:07:11.907Z | 3332.0 | 200 | 224113 | `case-04/final.png` | 已看 |
| B02-c01-r4 | case-01 | 2026-10-05T10:07:49.810Z | 4217.6 | 200 | 211954 | `case-01/final.png` | 已看 |
| B02-c01-r5 | case-01 | 2026-10-06T04:42:16.446Z | 9567.5 | 200 | 219178 | `case-01/final.png` | 已看 |
| B02-c06-r1 | case-06 | 2026-10-06T04:52:00.785Z | 4446.9 | 200 | 87801 | `case-06/final.png` | 已看（基线） |
| B02-c07-r1 | case-07 | 2026-10-06T04:52:05.299Z | 2442.7 | 200 | 72091 | `case-07/final.png` | 已看（基线） |
| B02-c08-r1 | case-08 | 2026-10-06T04:52:07.758Z | 4109.3 | 200 | 159975 | `case-08/final.png` | 已看（基线） |
| B02-c09-r1 | case-09 | 2026-10-06T04:52:11.884Z | 3361.4 | 200 | 136646 | `case-09/final.png` | 已看（基线） |
| B02-c10-r1 | case-10 | 2026-10-06T04:52:15.259Z | 4476.1 | 200 | 189124 | `case-10/final.png` | 已看（基线） |
| B02-c06-r1-retry | case-06 | 2026-10-06T04:55:56.433Z | 2561.4 | 200 | 87951 | `case-06/final.png` | 已看 |
| B02-c07-r1-retry | case-07 | 2026-10-06T04:55:59.057Z | 2233.8 | 200 | 72266 | `case-07/final.png` | 已看 |
| B02-c09-r1-retry | case-09 | 2026-10-06T04:56:01.307Z | 3621.8 | 200 | 135955 | `case-09/final.png` | 已看 |
| B02-c10-r1-retry | case-10 | 2026-10-06T04:56:04.945Z | 2788.5 | 200 | 189226 | `case-10/final.png` | 已看 |
| B02-c10-r3 | case-10 | 2026-10-06T04:58:08.040Z | 2862.8 | 200 | 189224 | `case-10/final.png` | 已看 |
| B02-c06-r2 | case-06 | （未采集） | null | 传输失败 | 0 | 无（`curl (6) Could not resolve host`） | — |
| B02-c01-r6 | case-01 | 2026-10-06T05:12:19.454Z | 4620.2 | 200 | 219680 | `case-01/final.png` | 已看 |
| B02-c04-r6 | case-04 | 2026-10-06T05:12:24.134Z | 4372.7 | 200 | 221595 | `case-04/final.png` | 已看 |
| B02-c07-r6 | case-07 | 2026-10-06T05:12:28.521Z | 2200.6 | 200 | 72427 | `case-07/final.png` | 已看 |
| B02-c09-r6 | case-09 | 2026-10-06T05:12:30.750Z | 3305.2 | 200 | 135315 | `case-09/final.png` | 已看 |
| B02-c10-r6 | case-10 | 2026-10-06T05:12:34.069Z | 3628.2 | 200 | 191282 | `case-10/final.png` | 已看 |
| B02-c04-r7 | case-04 | 2026-10-06T05:20:49.749Z | 3882.2 | 200 | 222262 | `case-04/final.png` | **未取得正确字节**（见 §3.4） |
| B02-c01-r7 | case-01 | 2026-10-06T05:35:52.881Z | 4786.8 | 200 | 220101 | `case-01/final.png` | 已看 |
| B02-c04-r8 | case-04 | 2026-10-06T05:35:57.727Z | 3103.2 | 200 | 222950 | `case-04/final.png` | 已看 |
| B02-c05-r3 | case-05 | 2026-10-06T06:16:17.635Z | 4574.0 | 200 | 168065 | `case-05/final.png` | 已看 |
| B02-c04-r9 | case-04 | 2026-10-06T06:38:49.516Z | 5193.4 | 200 | 222559 | `case-04/final.png` | 已看（终版） |
| B02-c08-r2 | case-08 | 2026-10-06T06:38:54.784Z | 5419.4 | 200 | 159482 | `case-08/final.png` | 已看（终版） |

> 注：`B02-c04-r3` 出现两次（一次 400、一次 200），是请求编号复用的**日志缺陷**，
> 两条原始记录都保留未合并。第 6 列的 `响应字节` 是**该次**响应的字节数；
> `final.png` 的当前字节数只等于**该用例最后一次成功响应**的字节数（见 §1.1 校验）。

### 3.2 迭代全表（43 条）

| 迭代ID | 用例 | 版本→父版本 | 类型 | 请求ID | 查看 |
|---|---|---|---|---|---|
| ite-B02-c01-v1-syntaxfix | case-01 | v1 ← - | syntax-fix | B02-c01-r1 | 否 |
| ite-B02-c01-v2-baseline | case-01 | v2 ← v1 | baseline | B02-c01-r2 | 是 |
| ite-B02-c01-v3-syntaxfix | case-01 | v3 ← v2 | syntax-fix | B02-c01-r3 | 否 |
| ite-B02-c01-v4-visual | case-01 | v4 ← v3 | visual | B02-c01-r4 | 是 |
| ite-B02-c01-v5-visual | case-01 | v5 ← v4 | visual | B02-c01-r5 | 是 |
| ite-B02-c02-v1-syntaxfix | case-02 | v1 ← - | syntax-fix | B02-c02-r1 | 否 |
| ite-B02-c02-v2-baseline | case-02 | v2 ← v1 | baseline | B02-c02-r2 | 是 |
| ite-B02-c02-v3-visual | case-02 | v3 ← v2 | visual | B02-c02-r3 | 是 |
| ite-B02-c03-v1-syntaxfix | case-03 | v1 ← - | syntax-fix | B02-c03-r1 | 否 |
| ite-B02-c03-v2-baseline | case-03 | v2 ← v1 | baseline | B02-c03-r2 | 是 |
| ite-B02-c03-v3-visual | case-03 | v3 ← v2 | visual | B02-c03-r3 | 是 |
| ite-B02-c04-v1-syntaxfix | case-04 | v1 ← - | syntax-fix | B02-c04-r1 | 否 |
| ite-B02-c04-v2-baseline | case-04 | v2 ← v1 | baseline | B02-c04-r2 | 是 |
| ite-B02-c04-v3-syntaxfix | case-04 | v3 ← v2 | syntax-fix | B02-c04-r3 | 否 |
| ite-B02-c04-v4-visual | case-04 | v4 ← v3 | visual | B02-c04-r3 | 是 |
| ite-B02-c05-v1-syntaxfix | case-05 | v1 ← - | syntax-fix | B02-c05-r1 | 否 |
| ite-B02-c05-v2-baseline | case-05 | v2 ← v1 | baseline | B02-c05-r2 | 是 |
| ite-B02-c06-v1-baseline | case-06 | v1 ← - | baseline | B02-c06-r1 | 是 |
| ite-B02-c06-v2-visual | case-06 | v2 ← v1 | visual | B02-c06-r1-retry | 是 |
| ite-B02-c07-v1-baseline | case-07 | v1 ← - | baseline | B02-c07-r1 | 是 |
| ite-B02-c07-v2-visual | case-07 | v2 ← v1 | visual | B02-c07-r1-retry | 是 |
| ite-B02-c08-v1-baseline | case-08 | v1 ← - | baseline | B02-c08-r1 | 是 |
| ite-B02-c09-v1-baseline | case-09 | v1 ← - | baseline | B02-c09-r1 | 是 |
| ite-B02-c09-v2-visual | case-09 | v2 ← v1 | visual | B02-c09-r1-retry | 是 |
| ite-B02-c10-v1-baseline | case-10 | v1 ← - | baseline | B02-c10-r1 | 是 |
| ite-B02-c10-v2-visual | case-10 | v2 ← v1 | visual | B02-c10-r1-retry | 是 |
| ite-B02-c10-v3-visual | case-10 | v3 ← v2 | visual | B02-c10-r3 | 是 |
| ite-B02-view-cache-v1 | case-01 | - ← - | visual-incomplete | - | 否（读图返回错误字节） |
| ite-B02-consistency-audit | (shared) | - ← - | requirement-change | - | 否（脚本核对） |
| ite-B02-c01-v6-visual | case-01 | v6 ← v5 | visual | B02-c01-r6 | 是 |
| ite-B02-c04-v5-visual | case-04 | v5 ← v4 | visual | B02-c04-r6 | 是 |
| ite-B02-c04-v6-incomplete | case-04 | v6 ← v5 | visual-incomplete | B02-c04-r7 | 否（读图返回错误字节） |
| ite-B02-c07-v3-visual | case-07 | v3 ← v2 | visual | B02-c07-r6 | 是 |
| ite-B02-c09-v3-visual | case-09 | v3 ← v2 | visual | B02-c09-r6 | 是 |
| ite-B02-c10-v4-visual | case-10 | v4 ← v3 | visual | B02-c10-r6 | 是 |
| ite-B02-c01-v7-visual | case-01 | v7 ← v6 | visual | B02-c01-r7 | 是 |
| ite-B02-c04-v7-visual | case-04 | v7 ← v6 | visual | B02-c04-r8 | 是 |
| ite-B02-c05-v3-visual | case-05 | v3 ← v2 | visual | B02-c05-r3 | 是 |
| ite-B02-crosswork-elements | (shared) | - ← - | requirement-change | - | 是（看图核对） |
| ite-B02-read-evidence-correction | case-01,case-04 | - ← - | evidence-correction | - | 是 |
| ite-B02-crosswork-calendar | case-04,case-08 | - ← - | requirement-change | - | 是（看图核对） |
| ite-B02-c04-v8-visual | case-04 | v8 ← v7 | visual | B02-c04-r9 | 是（终版） |
| ite-B02-c08-v2-visual | case-08 | v2 ← v1 | visual | B02-c08-r2 | 是（终版） |

**基线 10 次**（每用例首次成功响应后的看图）不计为改进迭代；
**20 次完整视觉迭代**都是「看旧图 → 改 DSL → 重渲染 → 看新图比较」；
**7 次语法修复**、**3 次需求变更**（跨作品一致性 / 日历复算）、
**1 次证据更正**、**2 次未完成视觉迭代**分别标识，父版本关系如表中
「版本→父版本」列，各用例统计互不重复。

### 3.3 看图时发现的真实问题（按迭代）

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| c01-v1 / syntax-fix / - | `400 PARSE_ERROR`：`Attr [fontStyle] value is invalid: Unexpected font style bold` | 服务端错误消息给出 position 2185；`doc-parser-tags.txt` 中 `fontStyle` 是枚举 | 生成库统一改成大写 `BOLD`，写 `patch-bold.ps1` 批量修复 | c02/c03/c04/c05 首版同样 400（同一个根因），一次批量修复后全部 200 | `case-01/failures/B02-c01-r1.body`、`patch-bold.ps1` |
| c01-v3 / syntax-fix / v2 | `400`：`Unexpected character '"' in input state [AFTER_ATTR_VALUE_QUOTED] at position 5107`（`gradientEndAngle="4.7123890""`） | 拼接时多写了一个引号，错误消息给出精确位置 | 修正字符串拼接 | 重渲染 200；但此后进度环的渐变问题才被发现（下一行） | `case-01/failures/B02-c01-r3.body` |
| c02-v1 / syntax-fix / - | `400`：`Attr [gradientBegin] value format error at position 264` | `doc-parser-tags.txt`：`gradientBegin/End` 取 `BoxAlignment` 枚举，不是 `"0,0"` | 改用枚举值 | 重渲染 200 | `case-02/failures/B02-c02-r1.body` |
| c04-v3 / syntax-fix / v2 | `400`：`Attr [color] unsupported CSS color [System.Object[] System.Object[] System.Object[]]` | PowerShell 把数组当字符串插值进了 `color` 属性（PS 拼接陷阱） | 给该处参数加显式字符串化与括号 | 重渲染 200 | `case-04/failures/B02-c04-r3.body` |
| c01-v4 / **visual** / v3 | **渲染成功但视觉不符**：进度环用 `SWEEP` 渐变表达 28% 进度，看图后弧段起止位置与 28% 明显对不上 | `measure-arc.ps1` / `measure-ring.ps1` 沿圆周逐 0.5° 采样：亮/暗弧的起止角与 `gradientStops`、`gradientStartAngle` 都对不上（起点被固定偏移 90°，停点被忽略） | 弃用渐变，改为 `DialArc`：圆周均分 100 段，先整圈画 OFF 色，再画前 28 段 ON 色覆盖 | `measure-ring.ps1` 复核：case-01 ON=203/720=**28.19%**、起点 0°；case-09 实测 78.47%、起点 0°，与参数 0.28/0.78 一致。剩余代价：DSL 体积 +8KB 左右 | `measure-arc.ps1`、`measure-ring.ps1`、`show-ring.ps1`、`lib-b02.ps1` |
| c06-v2 / **visual** / v1 | **渲染成功但视觉不符**：14 行记录表的分隔线几乎看不见，整张表读成一片 | `System.Drawing` 在 x=400 采样 y=545..865：线色只有 30% 不透明度、叠加 1px 在 `#F6F2E8` 纸面底色上对比不足 | 交替底色 `0x0A → 0x0D`、线色 `0x22 → 0x4D` | 采样复核 14 条线落在 555/593/631/…/859，与 38px 行高完全吻合；看图确认 14 行重新读成一张表 | `tool-usage.jsonl tu-09` |
| c01-v7 / **visual** / v6 | 跨作品一致性：海报写着「目标 132 种」，但 case-09 是「上一季 132 种 + 新增 11」 | `ite-B02-consistency-audit` + `ite-B02-crosswork-elements` 交叉比对 | 目标改为 **143**（132+11），进度环相应改为 16/57=28% | 重渲染并看图确认 143 与 28% 环同时出现 | `write-logs-b02-3.ps1` |
| c04-v5 / **visual** / v4 | 看板柱状图横轴是 `06..13`，但「在站观鸟人 21」是 17:42 的读数，末柱对不上；16 行数量之和需等于 412 | `ite-B02-crosswork-elements`：逐行求和 96+12+28+36+18+9+44+27+14+8+3+16+22+4+11+64=**412** | 横轴改为 `10..17`，高度改为 28/41/37/34/31/28/25/21（峰值 41 @11:00，末柱 21） | 重渲染并看图：末柱高度与「在站 21 人」齐平、峰值柱顶用强调色 | `write-logs-b02-3.ps1` |
| c05-v3 / **visual** / v2 | 手册封面的第 3 环节写「五要素：时间/种类/数量/**天气**/行为」，与记录表列头不一致 | `ite-B02-crosswork-elements` 逐列比对 case-06 表头 | `天气 → 备注`，对齐 case-06 的 `时间/种类/数量/行为/备注` | 重渲染 168065 B，看图确认五要素逐字一致 | `attempts/case-05.v2-final.*` |
| **crosswork-calendar / requirement-change** / - | **日历实算发现两处星期错误**：2026-10-05 实为**周一**（不是周日）；case-08 三场标着「周日」的活动落在 10-12/10-19/10-26，实际是**周一** | `[datetime]::ParseExact` 逐日复算（2026-10-06 = 周二 → 10-05 = 周一；10-10 六、10-11 日、10-15 四、10-17 六、10-18 日、10-22 四、10-24 六、10-25 日、10-31 六；9/20 与 11/15 都是周日、间隔 57 天） | case-04：表头 `周日 → 周一`、NEXT UP 第 4 条 `10/12 → 10/11`；case-08：三场周日活动移到真正的周日 `10-12→10-11`、`10-19→10-18`、`10-26→10-25`（星期标签保持「周日」） | 重渲染 `B02-c04-r9` / `B02-c08-r2`，`diff-weekday.ps1` 2px 全图差分：case-04 **44 个采样点**、包围盒 `x[1406..1484] × y[52..506]`（正好表头日期 + NEXT UP 第 4 条）；case-08 **115 个采样点**、包围盒 `x[696..710] × y[186..566]`（正好第 2/5/8 张卡的日期格），**其余区域零差异**；看图复核 9 组日期与星期 | `diff-weekday.ps1`、`crop-weekday.ps1`、`attempts/case-04.pre-weekdayfix.*`、`attempts/case-08.pre-weekdayfix.*` |
| read-evidence-correction / evidence-correction / - | `ite-B02-c01-v7-visual` 与 `ite-B02-c04-v7-visual` 的「查看」实际拿到的是**对方文件**的字节 | 读图工具按路径返回了别的文件的字节；用 PNG IHDR 尺寸 + 文件字节数与响应 `bytes` 比对判定 | 建立唯一命名的自标注副本（顶部 64px 标签条写明 case 编号/名称/尺寸），并用文件侧不可变证据交叉核对 | c01 用 `view/verify-case01-*.png` 复看正确；后续读图层自行恢复，10 件终版全部取得过与路径匹配的正确字节。剩余问题：读图工具的路径/内容错配本身未根治，已如实标注 | `mkjpegs*.ps1`、`view/`、`tool-usage.jsonl tu-07/tu-13` |

> 「渲染成功但视觉不符合要求」的问题共 3 类：进度环渐变（c01-v4）、
> 记录表分隔线对比度（c06-v2）、柱状图横轴口径（c04-v5），
> 全部由实际看图发现并修复。
> **从文档了解到但本次未触发**的注意事项：`429` 与 `Retry-After`（本题未遇到限流）、
> `413 REQUEST_TOO_LARGE`（最大 DSL 46,474 字符，远未触及）、
> `?errorImage=png` 的副作用（本题始终未加该参数）。

### 3.4 实际图片查看次数的拆分（重要取证说明）

`实际图片查看次数 = 47`，由三部分构成：

| 类别 | 次数 | 说明 |
|---|---|---|
| `iterations.jsonl` 中 `viewed=true` 的看图 | 33 | 覆盖 10 件作品；每条都有 `view_evidence` 字段说明看的是哪个文件 |
| 终版补看、复看与字节自检 | 12 | 含读图错配排查期的唯一命名副本复看、`tiny-red-*.png` 通道自检、以及终版 case-08 / case-04 / case-07 / case-09 的直接复看 |
| 未完成的查看（记为 `visual-incomplete`） | 2 | `ite-B02-view-cache-v1`、`ite-B02-c04-v6-incomplete` |
| **合计** | **47** | |

其中 **8 次返回的字节与请求路径不符**（读图工具层的路径/内容错配与图像层缓存卡住），
**39 次返回了与路径匹配的字节**。8 次错配全部单独留痕：
`ite-B02-view-cache-v1`、`ite-B02-c04-v6-incomplete`、
`ite-B02-read-evidence-correction`、`tool-usage.jsonl tu-13`。
**终版 10 张 PNG 全部取得过与路径匹配的正确字节并完成视觉判断。**

当直接看图失败时采用的替代证据（**明确不等同于视觉判断，只用于交叉核对**）：

1. PNG IHDR 实际尺寸 + 文件字节数 vs. 响应 `bytes`；
2. 自标注 JPEG 副本（顶部 64px 标签条写明 case 编号/名称/尺寸）；
3. `System.Drawing` 像素取样与差分（进度环 0.5° 中径取样、表格分隔线列采样、
   改动范围 2px 全图差分与包围盒）；
4. DSL 源文本（含日期、数字、地址的权威来源）。

**本地静态服务 + 浏览器标签页的绕行尝试失败**：`httpsrv.ps1` 起的 HttpListener
用 `Invoke-WebRequest` 自测 HTTP 200、字节数正确，但 `browser.tabs.open` 返回
`[browser.disconnected] No desktop browser is connected to this session`，
浏览器通道不可用。该尝试按失败如实记录在 `tool-usage.jsonl tu-14`，
**不计为成功的能力应用**。

---

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| 语法修复 ×7（c01-v1、c01-v3、c02-v1、c03-v1、c04-v1、c04-v3、c05-v1） | 7 次 `400 PARSE_ERROR` | 每次都读服务端 `message` + `position` 定位；见 §3.3 四类根因 | `fontStyle` 大写、`gradientBegin/End` 枚举、拼接多引号、PowerShell 数组插值 | 7 次失败响应原文字节全部保留在 `case-XX/failures/*.body`；修复后全部 200 | `case-0X/failures/`、`patch-bold.ps1` |
| c06 / 传输失败 | `B02-c06-r2`：`TRANSPORT_ERROR: curl (6) Could not resolve host: open-snapshot.muedsa.com` | DNS 解析失败，发生在任何 HTTP 交换之前，因此没有 wall-clock（`started_utc`/`ended_utc` 均为 null） | 同一窗口重发 4 个用例 | 4 条 `-retry` 全部 200；**失败行原样保留**，`duration_ms` 保持 `null` 而非填 0 | `requests.jsonl` 第 26 行 |
| 读图错配 | 连续多次按路径读取返回了别的文件的字节 | 用 IHDR 尺寸与响应字节数判定真正拿到的是 case-01 的海报 | 建立唯一命名自标注副本；随后读图层恢复 | 见 §3.4；剩余问题：错配本身未根治 | `view/`、`mkjpegs*.ps1`、`tool-usage.jsonl tu-13/tu-14` |
| 留痕缺口 | 早期被取代的 DSL/PNG 未进入 `attempts/` | 生成程序按用例就地覆盖 `final.snapshot`，早期版本未先归档 | 从 case-05 v2 起改为**先复制到 `attempts/` 再覆盖**；并对已丢失的 case-05 v2 DSL 用「还原生成程序行 → 重新生成 → 比对字节数 14,270 = 文档记录值」的方式重建 | `attempts/` 现有 7 个文件（case-05 v2/v3、case-04、case-08 改动前版本）；**早期版本无法再恢复**，如实标注为留痕缺口 | `attempts/`、`tool-usage.jsonl tu-11` |
| 日志编号 | `B02-c04-r3` 编号复用（一次 400、一次 200） | 手写生成脚本的编号规则缺陷 | **不合并、不删除**，两条原始记录都保留 | 读数时按行而非按 id 去重；不影响任何产物 | `requests.jsonl` |

**本次遇到的、已确认的踩坑**（真实发生）：

1. `fontStyle` 枚举只接受大写 `BOLD`（5 件首版因此 400）；
2. `gradientBegin`/`gradientEnd` 取 `BoxAlignment` 枚举而非坐标字符串；
3. **`SWEEP` 渐变的 `gradientStops` / `gradientStartAngle` 实测不生效**——
   这是本题最重要的能力边界发现，已在 `design-system.json` 里作为反例登记，
   进度表达一律改用确定性分段 `DialArc`；
4. PowerShell 字符串拼接陷阱：数组被插值进属性值（`color="System.Object[] ..."`）；
5. PowerShell 5.1 不支持 `Join-String`、`??`、三元运算符；`UTF8Encoding($false)`
   才能写出无 BOM；单引号字符串内用 `''` 转义；
6. `<Positioned>` 只能是 `<Stack>` 的直接子元素；`Transform matrix` 需外层括号、
   无空格、16 个有限浮点数；
7. 读图工具的路径/内容错配（见 §3.4）；
8. PS 5.1 的 `edit` 工具跨行匹配会因 CRLF 失败——单行替换可用，多行需拆开。

**本次未遇到**（未发生，不编造）：`429` 限流与 `Retry-After`、`401`、`413`、
`5xx`、坏 JSON 错误响应、字体查询失败。

---

## 5. 任务耗时与资源消耗

结构化指标文件：`outputs/run-20261002-220723-mimo/B02/task-metrics.json`

| 指标 | 实际值 | 单位或币种 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-05T17:39:27+08:00（UTC 2026-10-05T09:39:27.000Z） | ISO-8601 含时区 | `_suite/suite-state.json` 的 B02 `started_at` |
| 任务结束时间 | 2026-10-06T15:46:16.294+08:00（UTC 2026-10-06T07:46:16.294Z） | ISO-8601 含时区 | 本文件写完时的墙钟 |
| 任务总耗时（墙钟） | **79609.294** | 秒 | 结束 − 开始；含 2026-10-05T18:14 → 10-06T12:42 的长时间闲置窗口，故远大于请求耗时之和 |
| 首次可用图耗时 | **1029.943** | 秒 | 开始 → `B02-c01-r2` 结束（2026-10-05T09:56:36.943Z），首个 200 且可打开的用例图 |
| 等待用户反馈 | **0** | 秒 | 本题无等待用户反馈环节（自动连续执行） |
| 限流等待 | **0** | 秒 | 未出现 429/`Retry-After` |
| 排队等待 | **null** | 秒 | 服务未返回排队指标，不可测 |
| 已记录请求耗时之和 | **132.168** | 秒 | `requests.jsonl` 中 38 条有 `duration_ms` 的行求和；传输失败那条 `duration_ms` 为 `null` 未计入；**请求为串行，无重叠**；不等于墙钟 |
| 输入 / 输出 / 总 token | **null** | token | 平台未提供本任务的 token 计量，未知即 null，不以字符数估算 |
| 图像输入使用量 | **null** | 平台原始单位 | 同上；且未确认是否已含在输入 token 中，故不填、不相加 |
| 任务费用 | **null** | CNY/USD | 平台未提供计费数据 |
| 其他实际可取得指标 | 请求 39 / 成功 31 / 失败 8；迭代 43；工具记录 14；DSL 版本 38；最终用例 10；最终 PNG 10 | — | `requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl`、`task-metrics.json` |

> **统计范围说明**：墙钟含闲置窗口；请求耗时之和只覆盖 38 条有计时的请求；
> 逐用例耗时之和 = 132.168 s，与总墙钟 79609.294 s 不可互推。
> 文档访问 0 次（复用 B01 缓存），故不产生共享请求的重复累计；
> 每个渲染请求只归属一个用例，无共享渲染。

---

## 6. 设计选择、经验与未解决事项

### 6.1 关键设计选择（预览如何影响了选择）

1. **按「谁在什么环境要完成什么判断」分派媒介**，而不是按配色凑数。
   先写 `plan.md`（临时计划）把十件的任务、画幅、观看距离定下来，再开始生成；
   预览阶段就发现画幅必须全部不同，于是 10 种比例一次定死。
2. **同一套规则、不同的密度**。`lib-b02.ps1` 把 13 个组件做成函数，
   每个组件的 `density_test` 字段记录它在**最极端的两件**上是否成立
   （如 `SpeciesRow` 在 16 行/行高 40 与 6 行/行高 42 两端、
   `Chip` 在 2 字与 9 字两端）。预览中反复出现的问题是**字号下限**，
   最终定为 12（`typography.rule`）。
3. **比例必须能量出来**。进度环因为渐变不可靠改成 `DialArc` 后，
   看图不再作为比例的唯一证据，改用 `System.Drawing` 0.5° 取样：
   这一步把「看起来差不多」变成了「28.19% vs 28%」。
4. **跨作品数字用脚本核对，不用眼睛核对**。`ite-B02-consistency-audit`、
   `ite-B02-crosswork-elements`、`ite-B02-crosswork-calendar` 三条记录
   分别是品牌/数字初审、求和与口径、**日历复算**——最后一条抓出了两处
   星期错误，证明这类核对必须用计算而不是看图。
5. **改动范围用差分定位**。两次星期修正都做了 2px 全图差分，
   用包围盒证明「只改了该改的地方」，避免重新渲染引入回归。

### 6.2 可复用的经验

- 服务端 `PARSE_ERROR` 的 `position` + `near` 是最有效的定位手段，
  **先读错误再改代码**，本题 7 次语法修复全部一次命中。
- 对「比例/位置/密度」类主张，**像素量测优先于视觉判断**；
  对「文案/层级/可读性」类主张，**视觉判断优先于像素量测**，两者不能互换。
- 读图工具不可靠时，**唯一命名 + 自标注标签条**能立刻分辨拿到的是哪张图。
- 归档被取代产物必须**在覆盖之前**复制；一旦被生成程序覆盖就只能靠
  「还原生成程序 → 重新生成 → 比对字节数」重建，且仅在服务确定性成立时可行。
- PS 5.1 里 `ConvertTo-Json` 会把 `>` 转成 `>` 但保留 CJK，
  写 JSON 日志时直接写 UTF-8 文本更可控。

### 6.3 结束依据

**结束不是因为「达到了某个请求/迭代次数」**，而是因为逐条满足了以下条件
（全部有可核对的证据）：

1. 10 件作品齐全，每件都有 `final.png` + `final.snapshot` + `case.md`；
2. 10 张 PNG 字节数与对应成功响应的 `bytes` 逐一相等（未经后处理）；
3. 10 张 PNG 的 IHDR 尺寸与 DSL 宽高逐一相等；
4. **10 张终版全部用读图工具直接打开看过**，`iterations.jsonl` 33 行
   `viewed=true` 覆盖 10 件；
5. 每件的 4-5 条自定完成标准逐条对照实际图像给出结论（见 `case.md`）；
6. 跨作品 14 条不变量全部核对通过，审查中发现的 2 处星期错误已修复并复看；
7. `portfolio.json` → `final_collection_review` 的 10 项检查全部 `pass`；
8. 最终逐件复看未发现新的可见缺陷。

### 6.4 未解决事项 / 环境限制 / 未验证要求

1. **读图工具路径/内容错配**（8 次）——已用文件侧证据交叉核对并单独留痕，
   终版 10 张均取得过正确字节；错配根因未定位，属环境限制。
2. **浏览器通道不可用**（`[browser.disconnected] No desktop browser is connected`），
   本地 HttpListener 方案无法完成最后一步，已按失败记录。
3. **早期留痕缺口**：case-01..case-04 与 case-06..case-10 在各自第 2 版之前的
   被取代 DSL/PNG 未进入 `attempts/`（生成程序就地覆盖）；只有 `view/` 的
   自标注 JPEG 副本与 `iterations.jsonl` 的文字记录作为证据。
4. **`B02-c04-r3` 编号重复**：日志编号缺陷，两条记录均保留。
5. **token / 图像 / 费用**：平台未提供，全部为 `null`。
6. **未验证的要求**：`429`/`Retry-After` 路径、`/fonts.png` 可视化查字体、
   `?errorImage=png`——本题未触发，不做断言。

### 6.5 留痕材料保留情况

- 临时目录中的草稿、计划（`plan.md`）、生成程序（`gen-b02-a/b.ps1`、`lib-b02.ps1`）、
  量测与差分脚本、自标注副本、失败响应、`requests.jsonl` / `iterations.jsonl` /
  `tool-usage.jsonl` **全部保留，未删除或覆盖**；
- `attempts/` 保留 7 个被取代版本文件（case-05 v2/v3、case-04、case-08 改动前）；
- **无法取得的留痕材料**：见 §6.4 第 3 条（早期版本已被就地覆盖）；
- 交付与日志中**不含任何密钥**。

---

## 开放作品集补充

逐件的场景/内容/DSL能力/最终自检见 `portfolio.json`（含
`final_collection_review` 10 项检查）与各 `case-NN/case.md`。

### 整体策展审查
- 十件分派自 8 个旅程阶段（发现 / 了解×2 / 准备×2 / 到场 / 参与 / 归属 / 回看 / 持续），
  每件只有一个主任务，见 `touchpoint-map.json` → `stage_coverage`。
- 十种画幅全部不同、观看距离 0.25–6 m（24 倍跨度）、停留时长 1 s – 180 s。
- 「炫酷」的落点是**结构化图形系统真正承担信息任务**：确定性进度环的角度即比例、
  16 行物种表的算术自洽、9 张日程卡的星期与真实日历逐日吻合、
  看板末柱与「在站 21 人」的严格相等。

### 用例独立性
- 没有任何两件是同版式换色/换字或同一作品的缩放/裁切；
- 相邻的「了解」两件（地图 / 日程）分别回答空间与时间，信息结构不同；
- 相邻的「准备」两件（立牌 / 手册封面）分别是动作指导与目录页；
- 独立性检查脚本化字段见 `touchpoint-map.json` → `coverage_check`。

### 实际工具与局部素材贡献（`tool-usage.jsonl` 14 条，均 `double_counted=false`）
| 工具 | 真实用途 |
|---|---|
| `lib-b02.ps1` / `gen-b02-a/b.ps1` | 复用设计系统组件与生成期文本溢出校验（`Fit`/`TW`） |
| `patch-bold.ps1` | 批量修复 `fontStyle` 大小写 |
| `measure-arc/-ring/show-ring.ps1` | 进度环 0.5° 取样，证实 SWEEP 渐变失效并验证 DialArc |
| `zoom.ps1` | 局部 2× 放大核对小字号 |
| `mkjpegs*.ps1` | 自标注 JPEG 副本，规避读图错配 |
| `read`（读图工具） | 逐件看图 |
| `System.Drawing` 复核 | IHDR 尺寸、表格分隔线列采样 |
| B01 缓存文档 | 复用指南与标签参考 |
| `attempts/` 归档与 DSL 重建 | 覆盖前留存、确定性重建被取代版本 |
| 跨作品数值一致性核查 | 14 条不变量 + 求和验证 |
| 读图错配核查 | 文件侧不可变证据判定真正看到的作品 |
| 本地 HTTP + 浏览器（**失败**） | 未成功，如实记录 |

**局部素材贡献**：本题 **0 件外部素材**，10 件全部纯 DSL
（`design-system.json` → `imagery.external_assets = []`）；
程序化图形（人字鸟阵、折线/柱状图、滩涂等深线、水波纹、望远镜图解、
头肩剪影）全部由 DSL 图元拼装。

### 逐用例与共享准备的统计口径
- 每个渲染请求只归属一个用例，无共享渲染；
- 共享准备 = `lib-b02.ps1` 的组件库与 B01 缓存文档（文档请求 0 次），
  **不重复计入请求消耗**；
- 4 条 `requirement-change` / `evidence-correction` 迭代归属 `(shared)` 或跨用例行，
  在逐用例统计中**不重复计数**，只在总量 43 中出现一次；
- 逐用例与整体指标可互相核对：请求数 7+3+3+8+3+3+3+2+3+4 = 39，
  DSL 版本 7+3+3+8+3+2+3+2+3+4 = 38，
  逐用例请求耗时之和 = 132.168 s = 整体请求耗时。
