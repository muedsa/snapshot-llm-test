# 全套 Snapshot 使用记录与总审查

- run_id：`run-20261002-220723-mimo`　profile：`all`　时区：UTC+08:00
- 起：2026-10-02T22:07:23+08:00　止：2026-10-09T12:18:46+08:00　总墙钟 569483 s（6.59 天）
- 服务：`https://open-snapshot.muedsa.com`（以总 run-config 为准，子题默认配置已被总地址覆盖）
- 结论：**30/30 题 completed**，124 张最终图片、118 件独立作品、B 轨 60 件独立完整作品全部交付并通过总审查

---

## 0. 本文的口径

本文只写**实际发生并可核对**的事：文档真的抓了哪些、研究真的拿到了什么、DSL 真的用了哪些标签、工具真的怎么串起来的、踩了哪些坑、最后审查到底查了什么。

凡是没拿到的（法条原文、国家标准、token 计量、费用），一律写"没拿到"，不填替代数字。

数据来源：`tmp/<task>/requests.jsonl`、`tmp/<task>/iterations.jsonl`、B 类另有 `tool-usage.jsonl`，以及 `outputs/<task>/**.snapshot` 的实际扫描。所有汇总数字由脚本从这些日志反查生成，没有手填。

---

## 1. 真实取得的文档与服务信息

全套共 **100 次 documentation 族请求、5 次字体查询**，归并为 **20 个不重复 URL**。

### 1.1 套件共享准备（只抓一次，后续复用）

| 请求 | 目标 | 结果 |
| --- | --- | --- |
| `shared-doc-0001` | `https://open-snapshot.muedsa.com/ai-guide.md` | 200 |
| `shared-doc-0002` | `https://snapshot.muedsa.com/` | 200 |
| `shared-doc-0003` | `https://snapshot.muedsa.com/reference/parser-tags/` | 200 |
| `shared-fonts-0001` | `GET /fonts` | 200，**27 个字体族** |
| `shared-render-0001/0002` | `POST /snapshot` 启动探针 | 200 / 200 |
| `shared-render-0000` | `POST /snapshot` BOM 探针 | 400（刻意验证编码边界） |

`tmp/<run>/_suite/requests.jsonl` 的这 7 行是**套件级**请求，不归属任何单题；同目录 `probe/requests.jsonl` 的 2 行是其中两次探针的重复登记（同 request id），汇总时只计一次。

后续题目**真实复用**这批本地副本，不再重复计为新的 HTTP 请求。

### 1.2 各题实际查阅的文档页面

不重复 URL 共 20 个，覆盖：

- **指南**：`guides/layout/`、`guides/media-text/`、`guides/painting/`、`guides/parser/`、`guides/rendering/`、`guides/testing/`
- **参考**：`reference/parser-tags/`、`reference/parser-errors/`、`reference/enums/`
- **部件**：`widgets/layout/container/`
- **接口**：`/openapi.yaml`
- **服务侧**：`/ai-guide.md`、`/fonts`

100 次请求里包含大量**重复抓取**：B 类每题会为自己落一份可检索的本地副本（B01 落了 8 份、B04/B05/B06 各自再落一份），这是刻意的——写 DSL 时要能 grep，而不是靠记忆。重复请求如实计入 `document_requests`，不去重掩盖工作量。

### 1.3 状态未记录的处理

有 **17 行**请求没有 HTTP 状态码（其中 1 行是 A10 的 `log_note` 说明行）。原因是取文工具在部分路径下不暴露状态码。按约定记 **null**——既不当作成功，也不当作失败。

---

## 2. 真实外部研究（108 次）

`type=research` 的外部资料抓取共 **108 次**，全部来自 B01–B06。真实结果：

| 结果 | 次数 | 含义 |
| --- | --- | --- |
| 200 | 88 | 拿到内容 |
| 状态未记录 | 12 | 取文超时（`The operation has timed out.`）或工具不暴露状态码 |
| 404 | 5 | 失效链接 |
| 412 | 2 | 站点反爬拦截（nmpa、nhc） |
| 403 | 1 | 拦截 |

### 2.1 检索方法的真实试探

B06 留下了最完整的一份方法试探记录：

- **Bing 多词中文查询被截断**——多词查询实际只按第一个词返回，等于没查。
- **可行配方**：`https://www.bing.com/search?format=rss&q=<1–2 个词>&setmkt=zh-CN`，配浏览器 UA 用 `curl.exe` 取。短词查询稳定返回。
- **gov.cn 政策检索接口**：请求返回 200，但 `totalCount=0`——**等于没查到**，不能因为 200 就当成"找到了"。
- **nmpa / nhc**：412 反爬页。
- **lite.duckduckgo**：请求失败，无状态码。

### 2.2 研究结论对画面的约束

因为**没有拿到任何法条、国家标准或服务标准的原文**，全套做了三条硬约束：

1. 画面与交付文档**不引用条款号**、**不写罚则金额**、**不写国标数字**、**不写机构背书**。
2. 唯一的外部线索是 Bing RSS 的二手摘要，一律标注为「检索摘要（来源，日期）」，例如「上海地铁末班车前 3 分钟停止售票（上海地铁检索摘要）」。
3. **全部数值标 DEMO**，不冒充真实数据。

B06 的十个案例里，01/03/04/05/06/07/09 有二手摘要支撑的场景依据，02/08/10 是自拟案例，`problem-evidence.json` 逐件标了 `source_type` 与 `assumptions`。

B04 的 `sources.json` + `editorial-note.md`、B05 的 `product-brief.md` + `journey.json` 同样遵守这条纪律：图表的分子/分母/单位/比率/时间范围都能对上，研究拿不到的部分明写没拿到。

---

## 3. DSL 的实际使用

对 **124 份最终交付的 `.snapshot`** 做全量标签扫描，实际用到 **24 种标签**：

| 标签 | 出现次数 | 用途 |
| --- | --- | --- |
| `Positioned` | 13241 | 绝对定位，全套排版的骨架 |
| `Container` | 8676 | 尺寸与底色 |
| `Text` | 5257 | 文本 |
| `Transform` | 1000 | 矩阵变换（旋转、错切、透视） |
| `Raw` | 335 | 原始 SVG/图片字节 |
| `SizedBox` | 321 | 间距 |
| `Stack` | 169 | 层叠 |
| `Snapshot` | 128 | 根节点 |
| `Opacity` | 127 | 透明度 |
| `Column` / `Row` | 79 / 68 | 流式布局 |
| `Align` / `Expanded` / `Spacer` | 24 / 21 / 3 | 布局微调 |
| `WidgetSpan` | 13 | 行内部件 |
| `ClipRect` / `ClipRRect` / `ClipOval` | 11 / 7 / 1 | 裁剪 |
| `ImageFiltered` / `ColorFiltered` | 10 / 5 | 滤镜 |
| `BackdropFilter` | 4 | 背景模糊（**每文档限 1 个**） |
| `SizedOverflowBox` | 2 | 溢出控制 |

字体实际使用 **12 种 `fontFamily` 组合**，主力是 `Noto Sans CJK SC`（2610 次）、`Noto Sans Mono CJK SC`（1028 次）、`Inter,Noto Sans CJK SC`（949 次）、`Inter Black`（137 次）。

### 3.1 逐题验证过并被反复复用的 DSL 边界

这些不是文档里抄来的，是**渲染返回 200 + 读图确认**之后才敢用的：

- 根节点 `<Snapshot type="png" background="...">` **不带** width/height；画幅由第一个内层 `<Container width height>` 决定。
- `border="N SOLID #COLOR"` 必须**带颜色**；8 位十六进制 = `#RRGGBBAA`。
- 无 polygon / path 标签；异形只能用矩形、圆角矩形、圆、以及 matrix 变换后的矩形拼。
- 变换矩阵外层加括号、16 个浮点、列主序；自定义渐变对齐只支持 `(-1,0)`。
- `Rotate(l,t,w,h,deg,inner)` 绕**矩形自身中心**旋转，顺时针为正。
- `ClipR(l,t,w,h,rad,inner)` 会包一层 `Positioned`+`ClipRRect`，**内部 Stack 的坐标相对 (l,t)**。
- `ClipRRect > Stack clipBehavior="NONE"` 经 A10 / B03 验证可用。
- 滤镜只有高斯一种；`BackdropFilter` **每文档恰好 1 个**。
- `LEFT_CENTER` → 实际枚举名是 `CENTER_LEFT`；`maxLines` 被忽略；盒阴影只接受 `ELEVATION_n` 或 `"dx dy spread #color"`。
- `Circ(l,t,d,c,b)` 参数顺序是**颜色在前、边框在后**；`TXW` 是 **10 个**参数。
- 构造函数签名必须严格：`Ts(id,l,t,w,h,s,fs,fam,c,a,bold,where)` 是 12 个参数（第 12 个实参会落到 `$bold` 上，表现为 `fontStyle="LEFT"`）；`Kicker(id,l,t,w,s,fs,fam)` **没有高度参数**（高度 = fs×1.8）。

### 3.2 静态校验器

B06 的 `validate-b06.ps1` 把这些边界固化成检查项：无 `fontStyle`、`border` 形状、`color` 形状、`textAlign` 枚举、`boxShadow` 形状、`matrix` 必须 16 个数。最后一次运行 `files=37 problems=0`。

A08、A10、A14、A19 等题也各自有审计 JSON（`label-audit.json`、`composite-audit.json`、`wayfinding-audit.json` 等），做法一致：**先静态查，再渲染，再读图**。

---

## 4. 工具的实际使用

### 4.1 每题的固定链路

```
读题/TASK.md  →  研究(如需)  →  计算口径脚本  →  lib-<task>.ps1 共享绘图库
            →  gen-<task>-*.ps1 生成 DSL  →  render-<task>.ps1 POST /snapshot
            →  read 工具看图  →  改  →  重渲染  →  promote 到 outputs
            →  mk-iter / gen-case-md / mk-metrics 从 JSONL 反查生成交付
```

**渲染请求串行执行**，没有并发；全套 HTTP 请求耗时之和 2166.978 s（约 36 分钟），而总墙钟 569483 s——差额是读题、写生成器、读图、像素复核和写交付物，不是等待。

### 4.2 B 类的工具使用留痕

B01–B06 各有一份 `tool-usage.jsonl`，合计 **73 行**，每行含 `tool_id / tool / category / purpose / input / output / affected_cases / http_request_ids / double_counted / note`。

其中 `double_counted=false` + `note` 明确写出「HTTP 事件已在 requests.jsonl 计入，此处不重复累计」——**HTTP 次数只在 requests.jsonl 计一次**，工具日志只描述"用了什么工具做了什么"，不重复累计请求。

类别分布（节选）：生成程序 14、资料研究 4、图像观察 4、视觉检查 4、文档查阅 4、量测/放大 3、选题与规划 3、日志与指标 3、服务渲染 2、看图 2、探针 1、失败的工具尝试 1 等。

**"失败的工具尝试"** 也被如实记录——包括 `browser.preview` 与本地静态服务 + 浏览器标签页的尝试。

### 4.3 真实用过的辅助手段

| 手段 | 用途 |
| --- | --- |
| `System.Drawing` | PNG IHDR 尺寸读取、SHA256、**逐像素内区 MD5 比对**、局部放大裁切、出血复核、给视图副本画边框 |
| PowerShell 5.1 | 全套生成器、渲染器、校验器、日志与指标生成器（**不使用 Python / Node**） |
| `curl.exe` + Bing RSS | 外部研究（取文工具不可用时的替代路径） |
| PNG IHDR 头读取 | 逐张核对交付图片尺寸 |
| JSON 流式解析器 | 部分 `iterations.jsonl` 是多行序列化对象（A05/A06），按行 `ConvertFrom-Json` 会失败，需按花括号深度切分 |

### 4.4 不可用的工具

- **`browser.preview`**：本环境报 `browser.disconnected`，全程不可用。看图只能走 `read` 工具，这也是串图问题影响面更大的直接原因。
- **`websearch`**：被取消/不可用，外部研究改走 `curl.exe`。

---

## 5. 数据与口径纪律

B04 / B05 / B06 的所有数字都有唯一来源和唯一算法：

- **B06**：`calc-b06.ps1` 一次性算出十件作品的全部口径 → `calc-b06.json`（41312 B），生成器只读这个文件，不各自算一遍。
- **B05**：`calc-b05.ps1` → `calc-b05.json`，含加装电梯的时间线、分摊、路线。
- **B04**：图表保留正确的分子/分母/单位/比率/时间范围，`sources.json` 逐条记来源。

### 5.1 只靠读图才发现的三处数字矛盾

这三处**脚本一个都没发现**，全部是打开图片才看出来的：

1. **case-04**：标题与页脚硬编码 `+80.6%`，KPI 却是计算值 `+80.8%`——同一张图两个数。
2. **case-06**：KPI 写 `13.8%` / `7.2%`，标题却是 `13.84%` / `7.20%`，且图例里漏了 `%`。
3. **case-09**：档位卡把**分段增量** `3 / 6 / 8` 标成「累计」，而真实累计应是 `3 / 9 / 17`；比例条也按 `8/17` 而不是 `17/17` 画。

三处都已修复并重新读图确认。**这是全套最硬的一条经验：能算对不代表能画对，必须打开图片核对。**

### 5.2 逐像素复核抓到的日志错配

B06 收尾时对 29 份视图副本做了**逐像素内区 MD5 复核**，发现 `mk-iter-b06.ps1` 里 `case-01-r01` 与 `case-02-r01` 两条 `view=` 登记**互换**（一条登记了对方的文件）。修复后重新生成 `iterations.jsonl`、`case.md`、`portfolio`、`task-metrics`，复核结果 `rows=30 mismatches=0`。

结论：**人工登记的"我看了哪张图"必须事后用像素证据复核**，不能靠记忆。

---

## 6. 跨题经验与踩坑

### 6.1 读图工具会串图

`read` 工具按内容缓存，同一路径二次读取可能返回**之前读过的另一张图**。B05 发生 8 次、B06 发生 1 次，A14/A16/A17/A18 也有记录。

**对策**（已在 B 类固化为协议）：每次用**新 GUID 文件名**的副本 → 用 `System.Drawing` 改像素（画边框）→ 等待 5–7 秒 → 读取 → **必须同时核对画出来的边框和报头编号**。任一不符即作废重来。

配套坑：`Bitmap.Save()` 存回**同一个被打开的路径**会抛 `A generic error occurred in GDI+`——要写到新路径，或先 dispose 再重载。

被丢弃的重读多数没有单独日志，所以全套 `image_views = 505` 是**下界**，不是精确值。这个边界已写进 `task-metrics.json` 的 `image_views_note`。

### 6.2 PowerShell 5.1 坑清单

全套踩过并写成注释保留的：

- **变量大小写不敏感**：局部变量写成 `$L` 会被静默覆盖成位置参数 `$l`。B06 的 `Hatch6` 因此让两个裁剪框错位——**服务照样返回 200**，只有像素扫描能发现。
- **`int + string` 抛 `InvalidCastFromStringToInteger`**：PowerShell 会把右侧字符串转成 int。字符串字面量放前面，或用 `-f`。
- **`"$d.Value"` 不是属性访问**：必须写 `"$($d.Value)"`，否则展开成 `$d` 加字面量 `.Value`。
- **反引号在双引号串里是转义符**：写 markdown 代码段要用 `[char]96` + 辅助函数拼，不能直接写反引号。
- **`Measure-Object -Property <key>` 读不了 OrderedDictionary**；`Sort-Object <prop>` 也不会对 OrderedDictionary 的数值排序——统计一律用循环或 script-block 排序。
- **双引号串会静默展开 `$var`**：载荷含 `$` 时用单引号串或 `edit` 工具。
- **`Add-Content -Encoding UTF8` 在 PS 5.1 会写 BOM**：写 JSONL 用 `[IO.File]::AppendAllText`。
- **write/edit 工具写出的文件没有 BOM**：含中文的 `.ps1` 每次写入后必须重新 BOM 编码，否则中文变乱码。
- **`(if ...) {...}` 作为实参是语法错误**：先赋给变量。
- **`int` 与 `string` 之外**：`@(@('a','b'))` 会塌成一维；`A, B + C, D` 会按 `(A,B)+(C,D)` 分组。
- **`-like` 把 `[` `]` 当通配符**：改用 `.Contains()`。
- **不要给辅助函数起名 `H`**（会与 `$h` 冲突），不要在左侧参数 `$l` 旁边用 `$L`。

### 6.3 留痕纪律

- `requests.jsonl` 与 `iterations.jsonl` **只追加**，不改写。
- `checkpoints/state-0000NN.json` **只增不改**；`suite-state.json` 是允许更新的当前指针。
- `task-metrics.json` / `sources.json` **一律从 JSONL 反查程序生成**，不手写，避免与日志漂移。
- 每张最终图 = 服务返回的**原始字节** + 同名 `.snapshot`，**无任何后期处理**。
- 每次尝试都保留（草稿、失败响应、探针、脚本、资料），**不覆盖**已渲染过的尝试。全套 `.snapshot` 共 526 份（tmp 402 + outputs 124）。

---

## 7. 总审查结论

对全部 124 张最终图片执行了机器核验（脚本扫描，非抽样）：

| 检查项 | 结果 |
| --- | --- |
| PNG 魔数合法 | **124 / 124** |
| 存在同名 `.snapshot` | **124 / 124**，缺失 0 |
| IHDR 尺寸 == `.snapshot` 首个 `<Container>` 宽高 | **124 / 124**，不符 0 |
| 画廊相对链接可解析 | 157 条 href + 124 条 src，**无效 0**，外部/远程 **0** |
| 逐张读图并核对报头编号 | B 轨 60 件全部确认；A 轨 64 张在各自任务内确认 |
| 每题必备交付 | 30 份 `snapshot-usage.md` + 30 份 `task-metrics.json` 全部存在 |
| B 类额外交付 | B03 `technique-notes.md`、B04 `sources.json`+`editorial-note.md`、B05 `product-brief.md`+`journey.json`、B06 `problem-evidence.json`+`design-review.md` 全部存在 |
| B 轨独立完整作品 | **60 件**（B01–B06 各 10 件） |
| A21 / A22 预置轮次 | 各 3 轮产物全部保留（A21 6 张、A22 3 张） |
| 归档草稿 | 仅 2 张（A08、A10 的 `archive/*-v01.png`），明确标为草稿，不计入最终图片 |

**请求数核对**：render 435 + documentation 100 + fonts 5 + research 108 = 648 次 HTTP 尝试，另 1 行 `log_note` 非请求行。成功 559 / 失败 73 / 状态未记录 17。**0 次 429**，`ratelimit_remaining` 432 行有值，最低 15（出现在 A09，A01–A09 阶段普遍读到 15–19，A10 之后回到 100+，B 类稳定 110–119）。

---

## 8. 剩余事项与边界

1. **研究侧 3 类真实失败**：nmpa / nhc 各返回 412；ddg-lite 请求失败无状态码；gov.cn 政策检索返回 200 但 `totalCount=0`。因此全套没有法条、国家标准或服务标准原文，画面与文档一律不引用条款号、不写罚则金额、不写国标数字、不写机构背书。
2. **`image_views = 505` 是下界**：串图后被丢弃的重读多数未单独登记；22 题用申报值、8 题由迭代记录推得，逐题在 `image_views_source` 标注来源。
3. **token / 图像使用量 / 费用 = null**：平台未提供任何计量数据。按约定未知即填 null，**不以 DSL 字符数、渲染次数或账号剩余额度猜造**。真实可得的资源信号只有 HTTP 侧（次数、状态码、duration_ms、Server-Timing、ratelimit_remaining），已全部记入。
4. **17 行状态未记录**：取文工具不暴露状态码，记 null，不冒充成功也不冒充失败。
5. **30 题的 task-metrics 使用 4 种 schema**（A 类早期 v1、A13–A18 的 v1、A19–A23 的 v2、B 类 v2），字段名不统一。套件层对 `image_views` / `completed_visual_iterations` / `retry_requests` 采用「优先取申报值 + 逐题标注来源 + 给出覆盖率」的做法。
6. **A07 的 `ended_at` 漏写**：其关闭脚本未写入结束时刻。因全套串行执行，套件指标以下一题 A08 的 `started_at` 作为结束时刻给出**下界**，并在该题的 `wall_clock_source` 里标明。这是唯一一处需要推算的墙钟。
7. **`browser.preview` 全程不可用**：看图只能走 `read` 工具，串图问题的影响面比有预览时更大。
8. **排队等待不可测**：服务未返回排队指标，记 null；限流等待 0 是**实测**结论。

---

## 9. 可复用资产

下一套任务可直接取用（均已真实验证）：

- **绘图库**：`lib-b01.ps1` … `lib-b06.ps1`——`Ts` / `TXW` / `Circ` 构造函数、刊头/脚注/源标注、`Hand6` / `Wedge6` / `Arc6` / `Dial-Map` / `Ruler6` / `Pct100` / `Hatch6` / `Waterfall6` / `ColStack6` 等。
- **日志与指标**：`mk-iter` / `mk-toolusage` / `mk-portfolio` / `mk-metrics` 从 JSONL 反查生成交付的做法。
- **核验**：`validate-<task>.ps1` 静态校验 + `promote-<task>.ps1` 逐字节比对 + 逐像素内区 MD5 复核。
- **研究配方**：Bing RSS 短词查询 + `curl.exe`；以及"拿不到就如实写没拿到"的落地写法。

**同题成品不得重复计数为后题新增作品**——可复用的是构件和做法，不是成品。

---

## 10. 路径基准与忽略文件合规

本节对应总任务要求的三项变化：交付物由 `gallery.html` 改为 `gallery.md`、总任务根新增 `.gitignore`、
所有本地路径按 [PATHS.md](../../../PATHS.md) 使用有基准的相对路径。以下均为本轮实测结果，不是沿用旧结论。

### 10.1 总任务根 `.gitignore`

位置：总任务根 `.gitignore`（相对本文件 `../../../.gitignore`）。只有 Git 才读取它；当前目录并未
初始化 Git 仓库，但仍按要求创建。

实际采用的规则，与 `templates/gitignore-template.txt` 的缓存规则逐条一致：

```gitignore
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

**必要补充：无。** 本套只使用 PowerShell 5.1、System.Drawing 与 curl.exe，都不产生语言级运行时
缓存目录，因此没有追加规则；文件内已写明"换用 Node/Java/Python 工具时按模板逐条补加"，而不是整体
排除目录或扩展名。`.gitignore` 中的非注释规则行恰好就是上面 6 条。

**明确没有排除的东西**（过程证据必须保留）：`outputs/`、`tmp/`、`cache/`、`.cache/`、`*.log`，
以及任何图片 / DSL / JSON 通配。机器核验：命中"排除过程证据"的规则 **0 条**；`outputs/`、`tmp/`
只出现在注释行里，内容正是"不得在此排除"的说明。

### 10.2 路径基准与 `path_base`

| 记录类别 | 基准 | 声明位置与覆盖 |
| --- | --- | --- |
| 配置 | 配置文件所在目录 | `run-config.json` 位于总任务根 |
| 指标 / 状态 / 检查点 | 总任务根 | `path_base: "suite_root"`：`suite-state.json`、套件 `task-metrics.json`、37/37 份检查点 |
| 含本地路径的 JSON 记录 | 总任务根 | 130/130 份声明 `path_base: "suite_root"`（另有 6 份 A 轨 `task-metrics.json` 本身不含任何本地路径字段，无需声明） |
| 请求 / 迭代 / 工具日志 | 总任务根 | 67/67 份含本地路径的 JSONL 逐行声明 `path_base: "suite_root"`，共 1109 条记录 |
| 单题交付文件 | 本题输出根 | `path_base: "output_dir"`：B01–B06 的 `portfolio.json` 6/6 |
| 文档内链接 | 文档自身 | `index.md` 与 `gallery.md` 全部用 `../<task>/…`，失效链接 0 |

本轮为满足该要求实际做的改动（脚本 `tmp/<run>/_suite/norm-paths-1..4.ps1`，报告
`tmp/<run>/_suite/path-normalization.json`）：

1. **记录与报告**：按扫描结果（不按假设）处理 470 个自撰文件，在 29 个文件中删除 661 处
   写死的总任务根前缀（含盘符的单反斜杠写法、JSON 转义写法与正斜杠写法三种），路径变为套件根
   相对；3 处写死的用户目录前缀改写为未展开的 `$env:USERPROFILE` 表达式。逐文件的命中计数见
   `path-normalization.json`（该报告只记录相对路径与计数，本身不含机器路径）。
2. **日志**：给 124 份 JSON 记录与 67 份 JSONL 日志共 1109 个顶层对象，在对象首字节之后插入
   `path_base` 声明。**不重新序列化任何值**——浮点位数、键序、以及 A05/A06 多行流的物理行数
   （均为 18 行）都保持原样；插入前后的 JSON / JSONL 解析结果逐份比对，失败集合与改动前完全重合。
3. **脚本**：235 个 `.ps1` 里的机器根改为规范允许的写法——
   `if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }`，
   既可从总任务根启动，也可从任意工作目录启动。每个改写后的文件都用 PowerShell 语言解析器
   重新解析确认可编译。唯一解析失败的 `A11/verify-attempt-01-broken.ps1` 是**改动前就损坏的失败
   尝试**（32 处解析错误）；变换前后错误集合逐条相同（差异 0），确认未新增损伤后才保留该改动。

**如实说明的两处例外**：

- `A11/invoice-page-02.snapshot` 内的 `C:\work\cards\v2` 是**题面指定的内容数据**，属作品正文，
  按"保留服务原始字节"的约定不改写。
- 抓取来的原始响应与文档缓存共 1310 个 `.png` / `.snapshot` / `.html` 文件保持原始字节，不做路径
  改写；`.snapshot` 同时是当时的渲染请求原文，改动一个字节就不再是那次请求。

**关于历史检查点**：37 份 `checkpoints/state-*.json` 属"不可覆盖的编号快照"。本轮只在每份顶层
**新增**了一个 `path_base` 声明字段，其记录的状态、时刻、产物、证据与编号一律未改动——注入逻辑的设计
是仅在每个顶层对象的 `{` 之后插入固定字符串，不触碰其它字节。这是"补声明"而非"覆盖历史"，
在此如实记录，供后续审查判断。

### 10.3 交付物的机器核验（同一次运行内实测）

脚本 `tmp/<run>/_suite/verify-suite-2.ps1`，结果写入 `tmp/<run>/_suite/verify-report.json`：

| 项 | 实测 |
| --- | --- |
| `run-config.suite_required_artifacts` | 5/5 存在（`index.md`、`gallery.md`、`snapshot-usage.md`、`task-metrics.json`、`suite-state.json`） |
| `gallery.md` 图片预览 / 显式标题 | 124 / 124，与最终图片数一致 |
| `gallery.md` 链接集合 | PNG 124 条、`.snapshot` 124 条，与磁盘双向相等（缺失 0、多余 0） |
| `gallery.md` 失效 / 远程 / 机器路径链接 | 0 / 0 / 0（目录锚点 30 个另计，不是文件路径） |
| 分组 | 30 个题目小节 + 60 个 `case-NN` + 6 个 `round-NN` |
| `index.md` 失效链接 / 是否链接 `gallery.md` | 0 / 已链接 |
| 最终图片 | 124 张全部通过 PNG 魔数 + 同名 `.snapshot` 配对 + IHDR 等于 DSL 首个 `Container` 宽高 |
| B 轨 case 目录 | 60/60（`final.png` + `final.snapshot` + `case.md` 齐全） |
| A21 / A22 预置轮次 | 各 3 轮，PNG 与 `.snapshot` 数量相等 |
| 机器盘符 / 用户名命中 | 记录与脚本 0 处 |
| `path_base` 覆盖 | 检查点 37/37、含本地路径的 JSON 130/130、日志 67/67、portfolio 6/6 = `output_dir`，缺声明的行 0 |
| `.gitignore` | 存在，模板 6 条规则齐备，排除过程证据的规则 0 条 |
| `suite-state.suite_artifacts` | 6 条，磁盘全部存在 |
| 指标与磁盘一致性 | 最终图片 124、`.snapshot` 124、独立作品 118、completed 30/30，一致 |

`gallery.html` 仍在 `_suite/` 下，但**不在** `suite_required_artifacts` 内，只作为附加的 HTML 翻看版；
`index.md` 先链接 `gallery.md`，再在附加区提到它。它在 `suite-state.suite_artifacts` 里以
`required_by_suite_config: false` 标注，不会被误当成交付要求。

### 10.4 本节的边界

- 总任务根没有 `.git`，`.gitignore` 只能做文本层面核验（规则行逐条比对模板），无法用
  `git check-ignore` 实测。按 AGENTS.md"无需初始化仓库"的要求，不为此新建仓库。
- §8 记录的其余边界（排队等待不可测等）不受本次改动影响，结论不变。
