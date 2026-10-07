# 全套 Snapshot 使用与踩坑报告 · run_id `20261004-182918`

本文件记录 **30 题（A01–A24、B01–B06）** 全套执行中**真实**发生的文档应用、标签能力、跨题经验、
服务踩坑与总审查结果。凡是未确认的原因都标为「推测」；凡是平台/服务未提供的计量一律记 `null`，
**没有按字数、字节数或账户余额估算过任何数字**。

---

## 1. 真实使用的文档与接口

| 类型 | 来源 | 状态 |
|---|---|---|
| 服务使用指南 | `GET https://open-snapshot.muedsa.com/ai-guide.md` | 真实抓取，落盘 `tmp/20261004-182918/_suite/docs/ai-guide.md` |
| 接口定义 | `GET https://open-snapshot.muedsa.com/openapi.yaml` | 真实抓取，落盘 `_suite/docs/openapi.yaml` |
| 字体列表 | `GET https://open-snapshot.muedsa.com/fonts` | 真实抓取，落盘 `_suite/fonts-list.txt` |
| 标签与属性参考 | `https://snapshot.muedsa.com/reference/parser-tags/` | 真实读取 |
| 类 DOM 解析器 | `https://snapshot.muedsa.com/guides/parser/` | 真实读取 |
| 枚举速查 | `https://snapshot.muedsa.com/reference/enums/` | 真实读取（据此发现 `BorderStyle` 只有 `NONE`/`SOLID`） |
| 其它文档页 | 各题自抓（layout / widgets / painting / rendering 等） | 真实抓取，存于各题 `tmp/*/docs/` |

**渲染接口**：全部图片均由 `POST /snapshot` 返回的原始字节直接落盘，**没有任何本地绘图、后处理或再编码**。

**字体**（全部来自真实 `/fonts` 返回，未臆造）：
`Inter` 及字重族、`Inter Black`、`Noto Sans CJK SC/JP/KR/TC/HK`、`Noto Serif CJK SC/…`、
`Noto Sans Mono CJK SC/…`、`DejaVu Sans`、`DejaVu Sans Mono`、`DejaVu Serif`、`Noto Color Emoji`。
中西混排统一用 `fontFamily="Inter,Noto Sans CJK SC"`。

---

## 2. 全套沉淀下来的 DSL 语义坑（最重要的一节）

下面每一条都是**用真实服务响应或实际看图**验证出来的，不是照抄文档。手册固化在
`tmp/20261004-182918/_suite/DSL-HANDBOOK.md`。

### 2.1 会让服务报错的写法

| 写法 | 真实响应 |
|---|---|
| `<Positioned ... />` 空标签 | `400 RENDER_ERROR: ProxyWidget has no widget, can not create render box` |
| `<Positioned>` 放在 `Row` / `Column` / `Transform` / 普通 `Container` 里 | `400 RENDER_ERROR: renderBox.parentData must be StackParentData`（`Positioned` 只能是 `Stack`/`IndexedStack` 的直接子节点） |
| `<Positioned>` 塞多个子节点 | `400 PARSE_ERROR: Tag Positioned only can have one child` |
| `<Transform>` 不给 `matrix` | `400 PARSE_ERROR: Attr [matrix] must not be null` |
| `padding="24 32"` | `400 PARSE_ERROR: Attr [padding] value format error` |
| `border="2 DASHED #fff"` | `400 PARSE_ERROR: No enum constant BorderStyle.DASHED`（只有 `NONE`/`SOLID`） |
| 8 位色写成 10 位（`#38BDF866FF`） | `400 PARSE_ERROR: Attr [color]/[border] color must be #RGB/#RGBA/#RRGGBB/#RRGGBBAA` |
| `Container` 直接放多个子节点 | `400 PARSE_ERROR: Tag Container only can have one child` |
| `gradientBegin="CENTER_TOP"` / `alignment="null"` | `400 PARSE_ERROR`（枚举值非法） |
| 元素总数 > 4096 | `400 RENDER_ERROR: Document contains more than 4096 elements` |
| 嵌套 `Stack` 导致布局无界 | `400 RENDER_ERROR: Layout size is infinite`（或 `Layout size is empty`） |

### 2.2 **静默**失效（HTTP 200，但结果不对 —— 最危险的一类）

| 写法 | 静默后果 | 怎么发现的 |
|---|---|---|
| `<Snapshot width="1280" height="800">` | 完全无效，画布由布局决定。**探针实测：请求 1280×800，出图 400×200** | A03 用对照探针图证明 |
| `<Text font-size="44">` | 完全无效，正确拼写是 `fontSize`。**探针实测：同一张图里两种拼写字号肉眼不同** | A03 用对照探针图证明 |
| `Text` 同时给 `height` 与 `maxLines`，而 height < 换行后实际行高 | **整段文字完全不渲染**，无任何报错 | A01 结论卡三条证据整段空白，读回 DSL 才发现 |
| `Text` 在单行高度框里放不下 | 溢出部分被**静默丢弃**，不换行、不报错 | A01/A02/A04/A05 反复出现 |
| 8 位十六进制 | 按 CSS 读 `#RRGGBBAA`，旧 `#AARRGGBB` 读法已不适用。`#33FFFFFF` 是**不透明青色**不是 20% 白 | A03 修好后才看出来 |
| `colour=` 拼错、`fontWeight`/`font-weight`/`weight` | 全部静默忽略，HTTP 200 照常出图 | A15/A17 实测 |
| `colorBlendMode` 写成文档里没有的枚举 | HTTP 200 但滤镜不生效 | B03 探针 |

### 2.3 与直觉相反的行为

1. **`Stack` 默认 `clipBehavior="HARD_EDGE"`** —— 会裁掉越出子框的主体（A09 因此显式写 `clipBehavior="NONE"`）。
2. **`alignment="(0,0)"` 等价于 CENTER**，不是左上角；`Transform` 想绕左上角作用，得自己把 pivot 合进矩阵（A09）。
3. **嵌套 `Stack` 会重置坐标原点**，导致内部内容整体平移甚至被裁（A16 因此把内层 Stack 移到 `(0,0)`）。
4. **解析器不做 HTML 实体解码**：属性里写 `&lt;` 会画出字面量 `&lt;`（A11 全部改用 CDATA）。
5. **`Text` 的文本节点与 `text=` 属性都会 trim 首尾空格**；要保留必须用 `<Raw>`（A11）。
6. **`ImageFiltered` 模糊整棵子树**；只要背景模糊必须用 `BackdropFilter` + `ClipRRect`（A03）。
7. **`ColorFiltered` 的绘制边界包含子树阴影**，会撑大到不对称值（A10 用 2px 不透明边框钉死边界）。
8. **`fontFeatures="zero"` 会让 Inter 的数字 0 变成斜杠零**（A11 用它消除 O/0 歧义）。

### 2.4 服务能力边界（诚实记录）

| 能力 | 状态 |
|---|---|
| 动画 / GIF / APNG | **不支持**。`type` 只接受 `png`/`jpg`/`webp`；`gif`/`apng`/`svg` 被 `PARSE_ERROR` 拒绝（A23 实测） |
| `frames` / `loop` / `cmyk` / `path` 等属性 | 返回 200 但**静默忽略**——服务根本没有这个能力（A23 实测） |
| 矢量输出 / CMYK | 类 DOM DSL 做不到（A23、B03 如实说明） |
| ColorMatrix / 饱和度滤镜 | `ColorFiltered` 只能给 `color` + `blendMode`，其它滤镜需 Kotlin DSL（A10 如实说明） |
| 任意路径裁剪 | 只有 `ClipRect`/`ClipRRect`/`ClipOval`，没有任意 path（B03 如实说明） |
| 虚线边框 | `BorderStyle` 无 `DASHED`，只能手绘短矩形段（A02、A04） |
| 画线 / 多边形图元 | 只能由短矩形拼接，极陡线段在放大后有轻微阶梯（A01/A04/A05/A20） |

---

## 3. 跨题可复用的工程做法

1. **整屏绝对定位**：一个 `Stack fit="EXPAND"`，每个元素都是 `Positioned` 给精确
   `left/top/width/height`。DSL 里的坐标 = 脚本算出的坐标，图表几何与审计 JSON 天然同源（A01–A24 全套采用）。
2. **文字溢出估算器**（`dsllib.est_width`，CJK 1.0em / 拉丁 0.55em）：在生成阶段就报出
   「这个框放不下」的告警。它偏保守会误报，但**每次漏报的静默截断都是真事故**，所以宁可多看。
3. **像素级复核脚本**：A14/A15/A16/A18/A20/B03 都写了独立脚本重新读 PNG、重新算数值再比对，
   多次抓到肉眼漏掉的缺陷（A24 的完成线被背景盖住、A18 的圆环内径、A15 的字重墨迹密度）。
4. **标签/引线自动布局**：A20 用「换列 + 列内相邻交换」的爬山搜索把引导线交叉压到 **0**，
   并把两两矩形相交检测写进审计 JSON —— **人眼看着不重叠不算数，程序测出相交就得改**。
5. **数据与图分离**：`computed-data.json` / `analysis.json` / `normalized-data.json` /
   `graph-audit.json` / `schedule-audit.json` / `repair-log.json` 等由生成脚本直接产出，
   所以「图上画的」与「报告里写的」不可能漂移。

---

## 4. 计量与消耗（如实）

**可测量的**（全部来自 `tmp/20261004-182918/<task>/requests.jsonl`）：

| 指标 | 数值 |
|---|---|
| 最终交付 PNG | **124**（套件下限 124；另有 1 张 A23 接触表自检图） |
| 渲染请求总数 | **2002** |
| 其中成功 / 失败 | 见 `_suite/task-metrics.json` 的 `counts` |
| 图像查看次数 | **422** |
| 完成的视觉迭代 | **232** |
| DSL 版本数 | 见 `counts.dsl_versions` |
| 请求耗时之和 | 见 `counts.sum_of_request_durations_seconds` |
| 墙钟合计 | 见 `elapsed_seconds`（**远大于请求耗时之和**，差额是本地设计与看图时间） |

**不可测量的**（一律 `null`，**未做任何估算**）：

- `input_tokens` / `output_tokens` / `image_input_usage` / `cost` / `currency`
  —— 服务没有计量端点，平台也没有回报逐请求数字。
- 限流/排队等待 —— 全部 200 响应的 `Server-Timing` 都没有 `queue` 段，
  无法区分「没排队」与「没告知」，所以记 `null` 而不是 `0`。

**成本与质量分开说**：本次没有任何计费或配额问题发生（无 401/413/429/503/504）；
质量上的成本体现在大量 `400` 与「HTTP 200 但图错」的返工上，已逐题写进各自的
`snapshot-usage.md` 问题表。

---

## 5. 轮次执行（A21 / A22）

- 两题均为 **3 轮**：`round-01/` → `round-02/` → `round-03/`，各自独立目录保存 PNG + DSL + 报告，
  **前一轮不被覆盖**。总计 6 + 3 = 9 张最终图。
- 每轮都是**归档后才读下一轮的预置需求文件**（`rounds/round-02.md`、`rounds/round-03.md`），
  在当前作品上修改，不是重做。
- A22 用程序证明了「局部回归」：两轮对比的主区域边界位移均为 **0.00px**，柱图绘图区、表格面板、
  全部表格列 x 锚点完全一致；只有柱与其标签随数据变化。
- **诚实声明**：这是**预置需求连续执行**（后续轮次的需求在根目录里一开始就存在、可提前读到），
  **不声称任何隐藏反馈盲测**。这一点在两题的报告里都写明了。

---

## 6. 总审查结果

逐题核对脚本 `tmp/20261004-182918/_suite/check_deliverables.py`，检查：
每个声明产物是否存在 · PNG 是否为真实 PNG · 尺寸是否与 `task.json` 一比一 ·
同名 `.snapshot` 是否存在且以 `<Snapshot` 开头 · B 类每件 `final.png`+`final.snapshot`+`case.md`
是否齐备 · 规定的日志文件是否留存。

**结果：30 题全部通过（`tasks with problems: 0 / 30`），`delivered PNGs: 124`，达到套件下限。**

画廊 `outputs/20261004-182918/_suite/gallery.md`（`run-config.json` 的 `suite_required_artifacts` 规定的交付件）已校验：
125 张图全部逐图索引（124 张规定最终图 + 1 张 A23 自检接触表单列在末尾），
465 条链接中 310 个唯一目标**全部可达**、**0 远程引用**，
每一张都带明确标题、Markdown 图片预览、原 PNG 链接、对应 `.snapshot` 链接与尺寸字节数。
同目录另有同内容的 `gallery.html` 备用浏览版（非规定交付件，280 条相对链接、0 断链、0 `<script>`/`<link>`）。

**逐题画廊**：B01–B06 的 `task.json` `common_outputs` 同样要求 `gallery.md`，
因此六个 B 类任务的输出目录里各自有一份 `gallery.md`（10 件逐件展示，标题取自该题自己的
`portfolio.json` / `case.md`，每件含预览 + 原 PNG + `.snapshot` + `case.md` 链接 + 尺寸字节 + 入选理由
或实际看图审查记录，30 条链接全部可达）。校验时发现过一次真实偏差：初版只交付了
`gallery.html`，是 `check_deliverables.py` 报出 6 处 `MISSING gallery.md` 后补齐的。

---

## 7. 未解决事项（如实汇总）

1. **多次平台中断**：B01/B03/B05/B06 与 A20 的执行会话被平台中断过。
   这些题由后续会话接手完成，过程日志里如实记录了「哪个执行会话做了什么」，
   但被中断那一段的中间草稿有一部分无法逐字还原（各题 `snapshot-usage.md` 已逐条说明）。
2. **部分 B 类题目的迭代记录粒度偏粗**：A/B 类的 `iterations.jsonl` 记录的是
   「看图 → 发现 → 改 → 再看」的完整迭代；个别题目的渲染次数多于记录的迭代数，
   差额是探针渲染与能力验证（不构成完整视觉迭代），已在各题说明。
3. **B04 的四篇核心文献只拿到检索摘要、未抓到全文**，需要按全文复核其口径；该题已在报告中列出。
4. **像素级完全复刻做不到**：A15 明确没有宣称逐像素一致（抽样一致率 98.29%，
   残余差异集中在粗体抗锯齿边缘），字重粒度受服务限制。
5. **圆环内径、蒙版镂空**等服务没有对应图元的地方，A18/A19 用不透明底色挖出或裁剪近似，
   并在各自报告里标注了这是近似而非原生路径。

---

## 8. 套件目录

```
outputs/20261004-182918/
├─ _suite/            index.md · gallery.md（规定交付件）· gallery.html（备用浏览版）· snapshot-usage.md · task-metrics.json · suite-state.json
├─ A01 … A24          每题的 PNG + 同名 .snapshot + 题目要求的附加文件 + snapshot-usage.md + task-metrics.json
└─ B01 … B06          每题的 case-01…case-10/{final.png, final.snapshot, case.md} + 集合级文件

tmp/20261004-182918/
├─ _suite/            共享工具库（snapkit / dsllib / state / finalize / wrapup / crop）
│                     DSL-HANDBOOK.md · WORK-ORDER.md · 抓取的文档 · 探针 · 构建脚本
├─ _suite/checkpoints/  state-000001.json …（逐题归档快照）
├─ _suite/events.jsonl   套件级事件流
└─ A01 … B06          各题脚本、drafts/（编号草稿 DSL）、preview/、crops/（放大核对）、
                      responses/（失败响应原文）、requests.jsonl、iterations.jsonl、
                      B 类另有 tool-usage.jsonl
```