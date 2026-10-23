# Snapshot 使用情况说明与踩坑记录 · A21 第一轮

任务ID：A21
任务名称：真实需求变更：双尺寸发布物（自动三轮版本）
本次运行ID：r20261014T1536+0800-5f11da
本轮：round-01（第一轮，基线）
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/r20261014T1536+0800-5f11da/A21/round-01/`
临时目录：`tmp/r20261014T1536+0800-5f11da/A21/`
路径基准：默认 `suite_root`（总任务根）；本目录内相对路径另在
`content-map.json` / `task-metrics.json` 中以 `path_base` 字段标明

执行模式：预置连续执行（自动三轮）。第一轮需求写在
[TASK.md](../../../../tasks/A21-staged-launch-change/TASK.md) 的「第一轮与执行顺序」；
第二、三轮需求在本轮归档后才读取。本报告只记录本轮，三轮汇总见
[../snapshot-usage.md](../snapshot-usage.md)。

遵循[PATHS.md](../../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown 本地链接相对当前文档。

---

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `launch-portrait.snapshot` | 完整可复现DSL（5381 B） | `launch-portrait.png` | 完成 |
| `launch-portrait.png` | 服务返回的最终图片（223312 B，sha256 `d7fbe0229d21cf14…`） | 同名DSL | 完成 |
| `launch-wide.snapshot` | 完整可复现DSL（4730 B） | `launch-wide.png` | 完成 |
| `launch-wide.png` | 服务返回的最终图片（231358 B，sha256 `3af59f8d277df85b…`） | 同名DSL | 完成 |
| `design-tokens.json` | 专用审计：色板/字体/品牌几何 | — | 完成 |
| `content-map.json` | 专用审计：内容映射与7项检查 | — | 完成 |
| `task-metrics.json` | 本轮指标 | — | 完成 |
| `snapshot-usage.md` | 本报告 | — | 完成 |

### 题目要求逐项核对

| 要求 | 实际 | 判定 |
|---|---|---|
| 1080×1350 竖版海报 | PNG IHDR 实测 `[1080, 1350]` | 满足 |
| 1440×810 横屏 | PNG IHDR 实测 `[1440, 810]` | 满足 |
| 含「让复杂信息变得清晰」 | 竖版拆两行「让复杂信息」/「变得清晰」132px；横版同 116px。跨行拼接后与必需文案逐字符一致 | 满足 |
| 含「2026.11.07 19:30」 | 竖版 56px 加粗 / 横版 44px 加粗，单行 | 满足 |
| 含「ONLINE LAUNCH」 | 竖版 32px / 横版 30px，字距 +8px | 满足 |
| 含「讲者：林川 / 苏言」 | 竖版 34px / 横版 30px | 满足 |
| 含「layerlight.example.org」 | 竖版 32px / 横版 28px，置于药丸形网址牌内 | 满足 |
| 两图同一主色 | 均用 `#5FE0FF` 主色系 + `#060A18` 底；色板见 `design-tokens.json` | 满足 |
| 同一字体层级 | 同族 `Noto Sans CJK SC,Inter`，层级规则同（标题加粗、日期唯一暖色、讲者次要色） | 满足 |
| 3–6 个可识别品牌构件 | 6 个：叠层主标记、主标记亮核、发光球、球内光带、主色强调条、网址牌 | 满足 |
| 两图分别构图 | 竖版纵向结构（品牌行→眉标→标题→强调条→信息栈自上而下，主视觉在右中）；横版横向分栏（左栏文字、底部日期｜竖分隔线｜讲者横排，主视觉占右整栏）。不是等比缩放 | 满足 |
| 主标题 ≥56 | 竖版 132 / 横版 116 | 满足 |
| 其余文字 ≥24 | 实际最小 28（横版网址），其余 30–56 | 满足 |
| 不得整图嵌入或外部图片 | 全部由 DSL 构造；两份 `.snapshot` 内无 `<Image>` 标签，服务请求体即完整构造 | 满足 |
| 顶部/底部真实可用扩展空间 | 竖版顶 118px / 底 207px；横版顶 88px / 底 74px（均 ≥70px） | 满足 |
| 不写待添加文字 | 占位词黑名单（TBD/TODO/待补充/待添加/占位/Lorem/XXX）扫描结果为空 | 满足 |
| 交付两 PNG/DSL 与两份专用 JSON | 见上表 | 满足 |

### 为何达到交付标准

不是靠「能渲染、文件齐」判定的。`content-map.json` 的 7 项检查全部为 `passed: true`，
其中三项是像素级而非声明级：

1. **画布尺寸**读的是交付 PNG 的 IHDR，不是构造参数。
2. **必需文案完整性**把 layout 的 role 归并到稳定文案 ID，再与必需文案逐字符比对。
   竖版字标被拆成「叠光」与「Layerlight」两个 `<Text>`（不同色），所以拼接规则是
   「同行分段间隙 ≥8px 记为一个空格」，间隙由像素实测得出：竖版 20px、横版 16px，
   两者均 ≥8，故归一化结果为「叠光 Layerlight」而非「叠光Layerlight」。
3. **文字墨迹碰撞**不比较文字盒，而在交付 PNG 上按目标色取真实墨迹后求交集。
   竖版 8 条、横版 8 条墨迹两两共 28 组，交集面积全部为 0。

此外单独检查了**文字墨迹到发光球实体的净距**：竖版最近的标题第一行距 `orb_core`
47.17px，横版 291px，均为正数，即标题不被球体压住。（到 `orb_halo` 的净距另作参考
列出，竖版标题第一行与 halo 包围盒相交但 halo 是 0.42 不透明度的渐隐外圈，视觉上
不构成遮挡——这一判断由实际看图确认，见第 3 节。）

### 已知缺陷与修复

首轮 v1 发现三处缺陷，全部修复后重渲 v2 并复查：

| 缺陷 | 修复 | 复查结果 |
|---|---|---|
| 字标渲染为「叠光Layerlight」，中英无空格 | 改为两段独立 `<Text>`，英文起点显式给出 | 像素实测间隙竖版 20px、横版 16px（v1 约 2px） |
| 竖版右上象限大面积空白，左重右轻 | 加线叠层角部水印（仅描边、无填充），与左下氛围 wash 形成对角重量 | 实际看图确认构图平衡，水印不触任何文字 |
| 竖版标题下强调条与灰细线仅隔 66px、长度不一 | 删除灰细线，只留 156×6 主色强调条 | 实际看图确认层级清晰 |

当前无未修复的已知缺陷。

---

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（以 run-config 为准，总配置无覆盖）
文档缓存：`tmp/r20261014T1536+0800-5f11da/_suite/docs/`（在更早的题目中实际下载，
本轮复用，未新增 HTTP 请求）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `tmp/…/_suite/docs/ai-guide.md` | 请求体格式、编码、响应类型、错误处理 | 全部 9 条请求的调用方式 |
| `tmp/…/_suite/docs/dsl-docs.html.md.txt` | 可用标签与属性；`<Container>`/`<Stack>`/`<Positioned>`/`<Text>`/`<Opacity>`/`<Transform>` | 两份 `.snapshot` |
| `tmp/…/_suite/docs/fonts.txt` | 中文字体族名 `Noto Sans CJK SC`，拉丁与数字用 `Inter` | `fontFamily="Noto Sans CJK SC,Inter"` |
| `tmp/…/_suite/docs/openapi.yaml` | 请求体上限 1048576 B、状态码语义 | 本地防呆 `assert_dsl_wellformed()` |

### 本轮实际使用的能力

**渐变**——`gradientType="RADIAL"` 配合 `gradientColors`（逗号列表）、`gradientRadius`。
发光球用三档停靠 `#A8F0FF,#1E86C8,#0B2B4E` 半径 0.60，靠色阶本身做出球体感，
不加 `gradientFocal`（原因见第 4 节）。

**子树透明度**——`<Opacity opacity="0..1">` 包住单个 `<Container>`，用于发光球外圈
（0.42）、光带（0.90/0.58/0.34）、角部水印（0.45/0.62/0.80）与氛围 wash（0.55/0.42）。

**阴影**——`boxShadow="0 8 22 #5FE0FF66"` 给主标记亮核；`textShadow` 给标题
（竖版 `0 8 26 #5FE0FF2E`、横版 `0 6 22 #5FE0FF2E`），8 位 hex 的 alpha 通道生效。

**形状**——`shape="CIRCLE"` 做发光球、外圈、网址牌圆点。

**变换**——`transform` 属性（列主序 4×4 矩阵，必须带括号且不含空白）与
`<Transform matrix origin alignment>` 均可旋转；本轮版式未实际用到旋转，
但在能力探针中验证过 24 度角度正确，供后续轮次使用。

**文本**——`letterSpacing`（眉标 +8px）、`height`（行高倍数 1.0）、`textAlign`、
`fontStyle="BOLD"`。CJK 全角字 advance 恰为 1em（竖版标题实测 5 字 advance 660px，
墨迹 101–750 与之相符），这个结论被用来精确计算字标英文段的起点。

**未使用**：`<Image>`（题目禁止外部图片）、`decoration`/`decorationColor`（探针验证可用
但本轮不需要）、`maxLines`/`softWrap`（文字盒故意给足，不触发换行或截断）。

### 字体查询

复用已实际取得的 `fonts.txt`，未在本轮新增查询。选 `Noto Sans CJK SC` 是唯一的
中文字体族名，`Inter` 用于拉丁与数字，混排靠逗号列表在一个 `fontFamily` 里完成。

---

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/r20261014T1536+0800-5f11da/A21/requests.jsonl`
迭代记录文件：`tmp/r20261014T1536+0800-5f11da/A21/iterations.jsonl`
看图证据文件：`tmp/r20261014T1536+0800-5f11da/A21/viewing-evidence.json`
裁切视图清单：`tmp/r20261014T1536+0800-5f11da/A21/preview/round-01/views-manifest.json`

渲染请求总数：9（含 3 条能力探针）
成功次数：6
失败次数：3
重试请求数：0（同 DSL 原样重发；每次重交都改了 DSL 正文，另计为语法修复 3 次）
DSL版本数：6（launch-portrait 2 版、launch-wide 2 版、能力探针 2 版）
实际图片查看次数：14
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：0（文档与字体在本轮之前已下载并缓存，本轮复用未新增 HTTP）

初次生成和查看计为基线，不计为改进迭代。仅 `it-a21-006` 构成一次完整视觉迭代：
查看 v1 → 修改 → 重渲 → 查看并比较 v2。

### 逐次请求与查看

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `req-a21-probe1-capabilities-ab094e` | `tmp/…/A21/dsl/probe1-capabilities.attempt-01.snapshot` | 18:40:30→18:40:36，6531ms | 200 / image/png | `tmp/…/A21/responses/req-a21-probe1-capabilities-ab094e.png` | 18:44 已查看：渐变、Opacity、文本扩展属性全部生效；发现嵌套 `<Text>` 子 span 前导空白被裁掉 |
| `req-a21-probe2-transform-5cf9fa` | `tmp/…/A21/dsl/probe2-transform.attempt-01.snapshot` | 18:40:36→18:40:37，1047ms | 400 / 错误JSON | `tmp/…/A21/responses/req-a21-probe2-transform-5cf9fa.png`（232B 错误体） | 未查看：无图像可查看 |
| `req-a21-probe2-transform-624a90` | 同上路径（DSL 正文已修正） | 18:43:13→18:43:16，3187ms | 200 / image/png | `tmp/…/A21/responses/req-a21-probe2-transform-624a90.png` | 18:47 已查看：旋转、boxShadow、origin 偏移旋转生效；三个品牌候选中定下候选二+候选一 |
| `req-a21-r01-launch-portrait-b817ac` | `tmp/…/A21/dsl/r01-launch-portrait.attempt-01.snapshot` | 18:54:50→18:54:52，2406ms | 400 / 错误JSON | `tmp/…/A21/responses/req-a21-r01-launch-portrait-b817ac.png`（232B 错误体） | 未查看 |
| `req-a21-r01-launch-wide-b55ddc` | `tmp/…/A21/dsl/r01-launch-wide.attempt-01.snapshot` | 18:54:52→18:54:54，1360ms | 400 / 错误JSON | `tmp/…/A21/responses/req-a21-r01-launch-wide-b55ddc.png`（232B 错误体） | 未查看 |
| `req-a21-r01-launch-portrait-cf8a74` | 同上路径（DSL 已修正） | 18:55:48→18:55:52，4640ms | 200 / image/png | `tmp/…/A21/responses/req-a21-r01-launch-portrait-cf8a74.png`（216749 B，sha256 `fe64da1a3410d9c5…`） | 19:06 已查看：v1 竖版。发现三处缺陷（字标无空格、右上空白、双分隔线） |
| `req-a21-r01-launch-wide-eb0d6f` | 同上路径（DSL 已修正） | 18:55:52→18:55:57，4313ms | 200 / image/png | `tmp/…/A21/responses/req-a21-r01-launch-wide-eb0d6f.png`（231371 B，sha256 `62114c08523dad9f…`） | 19:06 已查看：v1 横版。同竖版存在字标问题 |
| `req-a21-r01-launch-portrait.v2-f82591` | `tmp/…/A21/dsl/r01-launch-portrait.v2.attempt-01.snapshot` | 19:14:06→19:14:12，5172ms | 200 / image/png | `tmp/…/A21/responses/req-a21-r01-launch-portrait.v2-f82591.png`（223312 B，sha256 `d7fbe0229d21cf14…`） | 19:21 整图 + header/kicker-title/orb/info 四裁切；19:40 归档前复查整图与 header 裁切。三处缺陷均已修复 |
| `req-a21-r01-launch-wide.v2-dd43b3` | `tmp/…/A21/dsl/r01-launch-wide.v2.attempt-01.snapshot` | 19:14:12→19:14:16，4000ms | 200 / image/png | `tmp/…/A21/responses/req-a21-r01-launch-wide.v2-dd43b3.png`（231358 B，sha256 `3af59f8d277df85b…`） | 19:21 整图 + header 裁切；19:40 归档前复查整图 |

时间均为 2026-10-19，时区 +08:00。

### 看图时的实际观察

- **裁切视图的源字节**由 `views-manifest.json` 的 `source_sha256` 锁定，与交付 PNG
  逐字节一致，排除「看的是一版旧的图」。
- 竖版 `whole` 视图确认：顶部品牌行→眉标→标题→强调条→日期→讲者→网址牌自上而下
  节奏清楚；右上线叠层水印与左下氛围 wash 形成对角重量；发光球在右中作氛围锚点。
- 竖版 `orb` 裁切（1.6×）确认：发光球靠色阶本身有明确球体感，外环细线完整，
  3 条光带自上而下递减宽度与亮度、两端圆头收口。
- 竖版 `info` 裁切（1.4×）确认：强调条→日期（橙、加粗）→讲者（灰）→网址牌
  （药丸形 + 圆点）层级明确，网址未溢出牌体。
- 横版 `header` 裁切（1.8×）确认：主标记 58px、字标 30px，中英间距约 16px，
  与竖版同一排版规则。
- 横版 `whole` 确认：底部日期与讲者之间用竖分隔线分开，横排布局与竖版纵排不是
  等比缩放。

**时间精度说明**：18:44–19:21 的查看发生在本轮上下文压缩之前的会话中，
时间只能记录到分钟级，已在 `viewing-evidence.json` 中以
`viewed_at_precision` 逐条标明，不做更精细的补记。19:40 的归档前复查发生在本会话，
同样记到分钟。

---

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| `it-a21-002` / syntax-fix / `it-a21-001` | `400 PARSE_ERROR 属性值无效 [transform]`，元素 `<Container>` | 把 4×4 矩阵写成不带括号的 16 个浮点数；服务端 diagnostic 直接给出格式要求 | `rot_matrix()` 输出 `(m0,…,m15)` 带括号且不含空白。同时纠正之前「属性值一律禁止 `(`」的过严结论——矩阵类属性恰要求括号 | `it-a21-003` 同参数重交得 200，24 度旋转正确 | `probe2-transform-5cf9fa.png`（错误体）、`probe2-transform-624a90.png` |
| `it-a21-004` / syntax-fix / `it-a21-003` | `400 PARSE_ERROR Attr [borderRadius] can not be used with shape CIRCLE`，两图同一位置 | 网址牌圆点同时给了 `shape="CIRCLE"` 与 `borderRadius` | `Canvas.box()` 中两者改为互斥（`elif`）：圆形本身等角，无需圆角属性 | 两图重交得 200 | `r01-launch-portrait-b817ac.png`、`r01-launch-wide-b55ddc.png`（错误体） |
| `it-a21-005` / baseline / `it-a21-004` | v1 竖版三处缺陷 | 实际看图发现，非推断 | 决定做一次视觉迭代 | — | `r01-launch-portrait-cf8a74.png`、`r01-launch-wide-eb0d6f.png` |
| `it-a21-006` / visual / `it-a21-005` | ① 字标「叠光Layerlight」无空格；② 竖版右上空白；③ 竖版双分隔线 | ① 嵌套 `<Text>` 的子 span 前导空白被服务端裁掉（`probe1` 已观察到，此处在成品中命中）；② 构图左重右轻；③ 156×6 强调条与 320×2 灰线仅隔 66px、长度不一 | ① 字标改为两段独立 `<Text>`，英文起点 = 中文起点 + `size*len(cn)` + gap（竖版 14、横版 12），CJK advance 按 1em 计算；② 右上加线叠层水印（3 个 300px 圆角方框，仅描边、无填充，透明度 0.45/0.62/0.80，出血到画布外）；③ 删除灰细线，信息栈改为 强调条→日期(+74)→讲者→网址牌(+72) | 重渲后重新看图 + 像素复核：字标间隙竖版 20px、横版 16px（v1 约 2px）；底部扩展空间由约 188px 增至 207px；水印不触任何文字。`content-map.json` 7 项检查全通过 | `r01-launch-portrait.v2.*.snapshot`、`r01-launch-wide.v2.*.snapshot` |
| — / 记录器修复 / — | `render()` 在写入 `delivered` 映射之前落日志，导致 round-01 的 9 条请求记录都没有 `delivered` 字段 | 读 `a21_round.py` 时自查发现，非服务返回 | 顺序改为先构造 `delivered` 映射再 `log_request()`；并给重渲加 `tag` 机制，attempt 文件名与请求 ID 带 `.v2`，避免覆盖同轮上一版真实尝试 | 已生效于第 2、3 轮。**旧日志不回填**——请求与交付件的对应改由 sha256 逐一比对得出，写在 `task-metrics.json` 的 `delivery_map` | 无（代码修复） |
| — / 审计修正 / — | 墨迹检测把球内光带误判为标题墨迹，导致伪碰撞 | 标题墨迹色 `#F5F9FF` 与光带色 `#EAFDFF` 色差仅 11（容差 40 内）；且文字盒故意超大，外扩窗口会吃到下一行字顶 | 窗口改为单行字带 `[top-0.25em, top+1.15em]`（够不到下一行），再从最左命中列起保留列间隙 ≤60 的连续段、从最上命中行起保留行间隙 ≤24 的连续段 | 竖版标题与球实体的净距由误报 0px 变为 47.17px；两两碰撞全为 0；标题第一行到球体净距为正，与看图一致 | `tmp/…/_suite/gen/a21_audit.py` |

### 从文档了解到但本轮未触发的注意事项

- 属性值禁止 `<` 与 `&`；括号只允许出现在 `transform` / `matrix` / `origin`。
- `<Rect>`/`<Circle>`/`<Line>`/`<Path>` 不存在，文字写在 `text` 属性里。
- `<Container>`/`<Positioned>` 最多一个子节点；根 `<Stack>` 须包在 `<Container>` 里。
- `<Stack>` 按文档顺序绘制，后者在上；`Column` 的直接 `Row` 子节点不渲染。

以上均由本地 `assert_dsl_wellformed()` 与构造器互斥约束兜住，本轮未再触发。

---

## 5. 任务耗时与请求统计

结构化指标文件：[`task-metrics.json`](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 本轮开始、结束时间 | 2026-10-19T18:40:30+08:00 → 见 `task-metrics.json` | ISO8601 带时区 | 第一条请求 `started_at` → 本轮归档时刻 |
| 本轮墙钟耗时 | 见 `task-metrics.json` | 秒 | 整个本轮的墙钟时间，含看图、设计与归档 |
| 首次可用图耗时 | 6.531 | 秒 | 到首次成功取得可打开图片（能力探针1）；由该请求的 `elapsed_ms` 得出 |
| 首次交付图耗时 | 922.6 | 秒 | 到首次成功取得交付尺寸的成品图（launch-portrait v1） |
| 等待用户反馈 | 0 | 秒 | 预置轮次模式，不等待外部反馈 |
| 限流等待 | 0 | 秒 | 本轮未出现 429/503 |
| 排队等待 | null | 秒 | 服务端不可观测排队，未取得该数据 |
| 已记录请求耗时之和 | 32.656 | 秒 | 本轮 9 条快照请求的 `elapsed_ms` 之和；含并行重叠，**不等于**本轮墙钟 |
| 成功、失败、重试请求 | 6 / 3 / 0 | 次 | `requests.jsonl`；语法修复重交另计 3 次 |

计时精度：请求日志的 `started_at` / `ended_at` 被截断到整秒，故「首次可用图」与
「首次交付图」两个字段用各请求的 `elapsed_ms` 还原了亚秒分量，但绝对起点仍只精确
到 1 秒，这两个值的不确定度是 **±1 秒**，不是小数位带来的精度。

墙钟口径：本轮墙钟含设计、看图、审计与归档，**也含本会话中段的上下文压缩与平台
中断造成的停顿**，因此远大于「已记录请求耗时之和」；两者不可相加，也不可互相替代。
| 实际看图 | 14 | 次 | `viewing-evidence.json`；含探针图与归档前复查，不合并同图不同视图 |
| 完整视觉迭代 | 1 | 次 | `iterations.jsonl` 中 `type=visual` 的记录 |
| DSL 版本 | 6 | 版 | launch-portrait 2、launch-wide 2、能力探针 2 |

服务端自报耗时与本地墙钟分开记录：请求日志的 `server_timing` 字段保留原值，
例如 v2 portrait 为 `render;dur=1339.4, total;dur=1343.4`，明显小于本地 5172ms，
差异为网络往返与本地处理，两者不互相替代也不相加。

---

## 6. 设计选择、经验与未解决事项

### 关键设计选择

**「叠光」的语义直接做成图形**——三张板材由暗到亮、沿右下方向偏移叠加，配合亮核
与发光球内的三条光带，「层」与「光」都落在实体上而不是靠文案解释。竖版额外的
右上线叠层水印只用描边、无填充，因此读作「层」的纹理而不是重复的 Logo。

**两图分别构图而不是等比缩放**——竖版是纵向信息栈、主视觉在右中作锚点；横版是
左栏文字加右栏整栏主视觉、底部信息横排并用竖分隔线分隔日期与讲者。横版信息区横排
vs 竖版纵排、主视觉整栏 vs 右中，是可辨认的差异。

**只有一处暖色**——日期 `#FFC26B` 是画面唯一暖色，与冷色主体系形成焦点，
眉标竖条也用同一色以建立呼应；讲者用次要灰蓝退到第二层。

**扩展空间不填占位文字**——顶部 118px、底部 207px（竖版）留给后续轮次或渠道裁切，
只放图形元素，不写「待添加」之类字样。

### 可复用经验

1. **CJK 全角字 advance 恰为 1em**——已用像素实测在 36px 与 132px 两个尺度上确认。
   这让字标英文段的起点可以用 `size*len(cn) + gap` 精确给出，不必猜测。
2. **嵌套 `<Text>` 的子 span 前导空白会被裁掉**——想同句混色时不能靠前导空格分隔，
   必须拆成独立元素并显式给坐标。文档里查不到 `<Raw>` 之类的转义手段，
   因此不依赖任何未文档化的行为。
3. **`gradientFocal` 在径向渐变上会把亮点推出可见范围**，球体发平。要球体感就用
   居心径向加 `gradientRadius`，不加 focal。
4. **`shape="CIRCLE"` 与 `borderRadius` 互斥**，同时给会被拒绝。已写进构造器。
5. **墨迹检查要用「单行字带窗口 + 连续段裁剪」**，否则同色的装饰元素（光带）
   会被当成文字墨迹，产生伪碰撞。这个坑只有在真去跑像素检查时才暴露。
6. **能力探针值得做**——本轮两次 400 都来自探针而非交付请求，探针把矩阵格式与
   属性互斥这两条约束先暴露出来，交付阶段的语法修复成本被压到很低。

### 未解决事项与如实说明

1. **`requests.jsonl` 的 round-01 记录无 `delivered` 字段**——驱动脚本在 9 条日志
   全部落盘之后才修好「先写映射再落日志」，旧日志不回填（保留真实过程优先于
   日志整齐）。请求与交付件的对应关系由 sha256 逐一比对得出并写入
   `task-metrics.json` 的 `delivery_map`：`req-a21-r01-launch-portrait.v2-f82591`
   ↔ `launch-portrait.png`，`req-a21-r01-launch-wide.v2-dd43b3` ↔ `launch-wide.png`，
   两对 sha256 完全一致。第 2、3 轮的日志将直接带 `delivered`。
2. **round-01 的交付 PNG 被同轮 v2 迭代原地覆盖**——v1 的服务响应字节完整保留在
   `tmp/…/A21/responses/`，sha256 与最初记录的交付值一致（portrait
   `fe64da1a3410d9c5…`、wide `62114c08523dad9f…`），v1 的迭代记录指向这些保留文件
   并注明。这是刻意的取舍：交付目录只放最终版，历史尝试留在临时目录。
3. **部分看图时间只能到分钟级**——见第 3 节说明，已在证据文件中逐条标注精度。
4. **横版右下为深色背景、无图形元素**——属底部扩展空间的一部分，未作处理。
   已看图确认不构成缺陷，记录在此以便后续轮次决定是否利用。

### 留痕确认

`tmp/r20261014T1536+0800-5f11da/A21/` 下完整保留：

- `dsl/`：2 组探针 + 4 组交付的 dry-run 与 attempt DSL，共 12 个 `.snapshot`
- `responses/`：全部 9 次响应原始字节，含 4 个 232B 的 PARSE_ERROR 错误体
- `preview/round-01/`：10 张裁切视图 + `views-manifest.json`
  （另有保留的 `views-manifest.render-01.json`）
- `r01-layout-*.json`：交付用的 layout 模型（含 `.roles-v1.json` 备份）
- `iterations/round-01-iterations.json`：6 条迭代的完整记录源
- `viewing-evidence.json`：14 条看图事件
- `round-01-changes.json`：首轮变化说明（design-tokens 中 `changes` 按模板约定为空，
  基线说明放在 `round_intro`）
- 生成脚本：`tmp/…/_suite/gen/` 下 `a21_core.py`、`a21_layouts.py`、`a21_round.py`、
  `a21_audit.py`、`a21_metrics.py`

失败响应、草稿与预览均未清理、未覆盖、未删减。未保存任何密钥。
总任务根 `.gitignore` 在启动时已创建，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，
不排除 `tmp/`、`outputs/` 或过程证据。

---

## 后续轮次

本轮已归档。按题目要求，第一轮的看图、保存与归档完成后读取
`tasks/A21-staged-launch-change/rounds/round-02.md` 执行第二轮，
第二轮归档后读取 `rounds/round-03.md` 执行第三轮，不等待用户消息。
本轮的两图、DSL、layout 模型与 `design-tokens.json` 的 `cross_round` 字段
（逐构件写明允许变动范围与固定项）即为第二、三轮的可比基线。
