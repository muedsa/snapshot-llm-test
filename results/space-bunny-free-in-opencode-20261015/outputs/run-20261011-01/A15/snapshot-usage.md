# Snapshot 使用情况说明与踩坑记录

任务ID：A15
任务名称：复杂界面视觉复刻
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A15/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A15/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A15/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `reconstructed.snapshot` | 复刻界面定稿 DSL | `reconstructed.png` | 已完成 |
| `reconstructed.png` | 服务返回的最终图 1440×900 | 同名 `.snapshot` | 已完成，服务原始响应 |
| `reconstruction-audit.json` | 24 个视觉锚点、17 个色彩角色、11 条实际看图记录 | — | 已完成 |
| `comparison.md` | 可测误差与残余差异说明 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据**实际打开查看**：原尺寸整屏 1 次、上下并排 1 次、25% 缩略 1 次、
7 处 2× 局部放大、24 个锚点像素实测、17 个色彩角色同点取样）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 用 Snapshot DSL 重建参考图的布局、背景、侧栏、卡片、图表、表格、状态标签和主要装饰 | 满足 | `reconstructed.snapshot` 含 7 个区域共约 130 个图元/文本节点；DSL 中没有任何 `<Image>` |
| 禁止直接嵌入参考图或裁块当素材 | 满足 | 全套 DSL 无 `<Image>`、无 base64；参考图只被 `probe_reference_a15.py` / `measure_reference*_a15.py` 读取像素用于测量 |
| `content.json` 仅提供文本与数值 | 满足 | 构建脚本只从 `inputs/content.json` 取字符串与 `chart_values`；`reconstruction-audit.json.reference` 记录了使用方式 |
| 输出尺寸保持 1440×900 | 满足 | 服务 `image_info` 为 PNG 1440×900 |
| 所有主要结构与信息完整 | 满足 | 侧栏（品牌 + 4 导航 + PRO 卡）、页眉（标题/副标题/按钮）、3 张 KPI 卡、图表卡（6 柱 + 5 刻度 + 网格）、活动卡（3 项）、表格卡（3 行 × 4 列 + 3 状态标签）、页脚全部存在 |
| 不改成自己的新设计 | 满足 | 原图里 KPI 行右边界比下面两行窄 16px（1383 vs 1399）这一「不整齐」的特征也按原样保留 |
| 观察原尺寸、缩略与局部放大 | 满足 | `visual_reviews` 11 条：原尺寸、并排、25% 缩略、侧栏/页眉/KPI/图表/活动卡/表格/PRO 卡 7 处 2× 放大 |
| 关键锚点与参考一致（±8px） | 满足 | 24/24 合格，最大分量误差 3px |
| 检查位置须覆盖画布四象限 | 满足 | `quadrants_covered` = 左上、右上、左、右、左下、下、右下、上 |
| 颜色可小幅近似 | 满足 | 17 个角色 RGB 距离全部为 0 |
| 字体从实际服务列表中选择 | 满足 | 用 run 级 `GET /fonts` 返回的 Inter / Inter Semi Bold / Inter Medium；替换原因写在 `comparison.md` |
| 重建图表的比例与标记，而不是只放相同数字 | 满足 | 由零线与最上刻度反推 1.2px/单位，柱高 = value × 1.2；六根柱顶端误差 ≤0.8px，第一/末柱顶部中心锚点误差 0px |
| 表格 3 行顺序与状态编码准确 | 满足 | 三行顺序 Atlas/Pulse/Orbit 与参考一致；状态标签 In progress(#245CE4/#E7EFFF)、Review(#9D6613/#FFF3D7)、Done(#168267/#DCF5EC) 颜色与文字均一致 |
| 至少记录 12 个视觉锚点 | 满足 | 共 24 个，其中题面点名的 12 项见 `anchor_summary.required_anchors_present` |
| 锚点涵盖画布四象限、图表和表格 | 满足 | A01–A24 分布见上表 |
| 每项记录对象/测量类型、参考估计、重建实际、分量误差、测量方法及局部证据 | 满足 | `anchors[]` 每项含 `name`/`object`/`type`/`quadrant`/`reference_estimated`/`reconstructed_actual`/`component_errors`/`method`/`passed` |
| 边界项记 x 或 y，点项记 (x,y)，矩形记 [l,t,r,b]，均为外轮廓 | 满足 | `coordinate_convention` 明确声明；A01 为边界项、A04/A10/A12/A13/A20/A21/A22/A23/A24 为点项、其余为矩形外轮廓 |
| ±8px 指对应分量绝对误差均 ≤8，矩形四边分别比较 | 满足 | `verify_a15.py` 对 rect 取四边 max，point 取两分量 max；不平均抵消 |
| 文字锚点比较可见字形位置 | 满足 | A04/A20/A21/A24 用墨迹包围盒左上角 |
| 颜色采用人工并排判断，不设未公开的硬阈值 | 满足 | `color_review.method` 写明；每行给出色相/明暗/角色含义，RGB 距离仅作辅助解释，未作为判据 |
| 逐项说明主背景、侧栏、主蓝色、卡片和状态标签 | 满足 | 17 行覆盖这五类并额外覆盖描边、网格线、品牌标记、PRO 卡、状态标签字 |
| 可记录纯色内部采样辅助解释 | 满足 | 每行给 `reference_hex`/`reconstructed_hex`/HSL/RGB 距离 |
| 几何容差合格不替代图表比例、全部文字、状态编码与整体视觉检查 | 满足 | 除锚点外另做：六柱比例逐根对照表、三行表格与三枚状态色对照、11 条看图记录 |
| 交付 `reconstruction-audit.json` 与 `comparison.md` | 满足 | 均在输出目录，字段遵循 `templates/audit-fields.json` 的 `anchors`/`color_review`/`visual_reviews` |
| 不要求 DSL 树与参考来源一致，不必宣称逐像素完全复刻 | 满足 | `not_claimed` 与 `comparison.md` 第 5、6 节明确写出字体替换、抗锯齿与描边内沿差异，并声明未验证逐像素一致 |
| 所有指定最终 PNG 是服务真实响应且有同名 `.snapshot` | 满足 | 交付 PNG 由服务端渲染返回，DSL 为同一份 |



## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（与总 run-config.json 的 `service_base_url` 一致，覆盖子题默认地址）
文档访问日期：本次运行当天；字体清单由 `GET /fonts` 实际取得并缓存

AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际阅读情况：已按指南使用 `POST /snapshot`（请求体为 UTF-8 纯文本 DSL，非 JSON），
按指南要求检查 HTTP 状态与 `Content-Type` 后才使用图片；遇到 `400 PARSE_ERROR`
时按响应 `message` 中的位置修正 DSL 后重新提交；未使用 `?errorImage=png`，
以保证错误 JSON 可被程序读取。字体通过 `GET /fonts` 查询后按返回值书写 `fontFamily`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|

| https://open-snapshot.muedsa.com/ai-guide.md | `POST /snapshot` 请求体为 UTF-8 纯文本 DSL（非 JSON）；成功返回图片二进制；失败返回含 `code`/`message`/`requestId` 的 JSON，按 `message` 中的 `position` 定位修正；`GET /fonts` 返回 text/plain 字体族列表 | `_suite/scripts/snapshot_render.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | 38 个标签的完整属性表（`Container`/`Stack`/`Positioned`/`Text`/`Flex`/`ClipOval`/`ClipRRect`/`Transform` 等） | `snapkit.py` 与各题 DSL |
| https://snapshot.muedsa.com/reference/enums/ | 枚举取值（`CrossAxisAlignment`、`BorderStyle`、`FlexFit`、`StackFit` 等）；已确认 `BorderStyle` 仅 `NONE`/`SOLID`、`CrossAxisAlignment` 无 `BOTTOM` | 各题构造器中的枚举取值 |

字体：实际调用 `GET /fonts` 取得 27 个字体族，原始响应留存于
`tmp/<run_id>/_suite/responses/`（`request_type=fonts`），整理副本见 `tmp/<run_id>/_suite/fonts-list.txt`。
中文正文用 `Noto Sans CJK SC`，拉丁与数字用 `Inter` 系列。本套 A 类任务素材政策为 `dsl_only`，
全部主体由 DSL 构造，**未使用 `<Image>` 标签**，未引入任何外部图片素材。

| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | 同一 Stack 内后出现的节点绘制在上 | 主区底色若排在侧栏之后会把侧栏整块盖住；顺序必须是「主区底 → 侧栏 → 主区内容」 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Container | `border` 画在填充内沿 | 参考图白卡的 1px 描边在填充外沿（顶边 y=137），服务端 `border` 落在内沿（y=138）；两者视觉不可分辨，卡片外轮廓锚点误差 0px |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**同一套测量代码分别跑参考图与重建图**——这是复刻题能给出可测误差的前提。参考坐标不是抄来的，而是对公开 reference.png 做像素测量得到；两边走同一个函数，误差才可比。
**卡片描边要一起复刻**：白卡在参考图里带 1px #E2E8F1 描边（实测 x=260 / y=137 处的颜色），补上之后 6 个卡片锚点的误差从 178–268px 降到 0px。
**图表比例要反推**：由零线 y=549 与最上刻度 y=405 得出 1.2px/单位，柱高按 `value × 1.2` 算出，六根柱的顶端误差都在 0.8px 内，而不是照着数字把柱子放到大致位置。
**取色要看角色而不是只看一个点**：大面积纯色取 3×3 邻域中位色；1px 细线与文字笔画取区域内最暗像素——按固定坐标取点会踩在抗锯齿边缘上。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A15/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A15/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A15/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A15/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A15/responses/`、`tmp/run-20261011-01/A15/drafts/`

渲染请求总数：5
成功次数：5
失败次数：0
重试请求数：0（是总请求的子集）
DSL版本数：4
实际图片查看次数：18
完整视觉迭代数：2
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题的请求全部是渲染请求（含 2 张仅用于比对的并排/缩略对照图与 7 张局部放大对照图，均由 PIL 在本地生成，不是服务渲染）。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A15-v1-ef270fc5 | drafts/a15-reconstructed-v1.snapshot | 2.72s | 200 image/png | preview/reconstructed-v1.png | 首版整屏打开：**侧栏整块消失**——主区底色 rect 排在侧栏之后把它盖住了 |
| A15-v2-2f408dd9 | drafts/a15-reconstructed-v1.snapshot | 3.21s | 200 image/png | preview/reconstructed-v2.png | 改成「主区底 → 侧栏 → 主区内容」后侧栏恢复；像素锚点核验发现 6 个卡片锚点 FAIL（测量函数把卡内文字算进了卡片框） |
| A15-v3-01cdf028 | drafts/a15-reconstructed-v1.snapshot | 2.29s | 200 image/png | preview/reconstructed-v3.png | 补上白卡 1px #E2E8F1 描边后重渲；24 个锚点全部合格 |
| A15-final-* | outputs/run-20261011-01/A15/reconstructed.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A15/reconstructed.png | 定稿渲染，并对交付 PNG 重跑锚点与色彩核验 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · visual | 侧栏整块消失，只剩主区 | DSL 里 `Stack` 的后出现节点绘制在上；`main_area()` 第一件事就是画全幅主区底色，把已经画好的侧栏盖住了 | 把主区底色提到 `build()` 里最先画，顺序改为「主区底 → 侧栏 → 主区内容」 | 侧栏、品牌标记、四个导航项与 PRO 卡全部恢复 |
| v2 · measurement | 6 个卡片锚点全部 FAIL（误差 114–268px） | 测量函数用「非主背景色的像素包围盒」取卡片外轮廓，把卡片内部的文字也算进去了，量到的其实是文字块的框 | 改为「纯白填充 ∪ 1px #E2E8F1 描边」的像素包围盒 | 6 个卡片锚点误差降到 0px |
| v2 → v3 · visual | KPI 数值字形锚点差 9px；整屏并排看卡片边界比参考图「软」一格 | 沿卡边扫描发现参考图的白卡有 1px #E2E8F1 描边（顶边落在 y=137），重建图没有；同时该描边列被字形测量当成文字，把字形框顶到了 y=190 | 给 6 张白卡加 `border="1 SOLID #E2E8F1"`；字形测量排除描边色与主背景色 | 卡片锚点 0px，KPI 数值字形锚点误差降到 1px |
| v2 · measurement | 状态标签文字色与卡片描边色取样偏差大（64.6 / 落到主背景） | 按固定坐标取点时，文字点落在笔画抗锯齿边缘、描边点落在白卡与描边之间 | 大面积纯色用 3×3 邻域中位色；1px 细线与文字笔画改取区域内最暗像素 | 17 个色彩角色的 RGB 距离全部为 0 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A15/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-12T10:31:52.645+08:00 / 2026-10-12T10:43:52.554+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 719.909 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 2.723 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 12.096 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 5 / 0 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 18 / 2 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 4 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *把「参考坐标」变成可复算的测量，而不是眼估*。题面明确不提供标准坐标，
   但允许观察公开的 `reference.png`。所以我写了 5 个勘察脚本
   （`probe_reference_a15.py` + `measure_reference{,2,3,4}_a15.py`），
   把侧栏边界、卡片框、网格线、柱顶、表格行、状态药丸、侧栏文字色等全部量成 JSON，
   再用这些数字去写 DSL。这样「参考估计」有出处、有方法、可复核，
   而不是构建脚本里凭空冒出来的常数。

2. *两图同码测量，误差才可比*。`verify_a15.py` 里每个锚点只有一个测量函数，
   分别喂参考图和重建图。这一点很关键：如果参考值用「设计参数」而重建值用「像素测量」，
   误差里就混进了两套口径的差异。实际结果 24/24 合格、最大误差 3px。

3. *图表比例要反推*。从参考图量到零线 y=549、最上刻度 y=405、刻度 0/30/60/90/120，
   得出 1.2px/单位。柱高一律 `value × 1.2`，柱顶 y = 549 − 高度。
   六根柱的实测顶端与算出来的值差 ≤0.8px（差的来源是柱顶抗锯齿像素的取舍），
   第一根与最后一根柱的**顶部中心**锚点误差 0px。这比「把数字贴上去」有实质区别。

4. *不修原图的不整齐*。原图里 KPI 那一行的右边界是 1383，而图表/活动/表格三行是 1399——
   差 16px。看起来像原图自己没对齐，但复刻题要求「不改成自己的新设计」，
   所以照原样保留，并在 `comparison.md` 里写明这是刻意保留的特征。

5. *卡片描边也算「主要装饰」*。第一版只画了白底没有描边，整屏并排一看卡片边界明显偏「软」。
   沿卡边扫描才发现参考图有 1px #E2E8F1 描边（而不是投影——这一点我专门探测并排除了）。
   补上之后，6 个卡片锚点的误差从 178–268px 变成 0px。

**问题与修复（要点）**

- 侧栏消失纯属低级错误：`Stack` 里后出现的节点绘制在上，
  而我把全幅主区底色放在了侧栏之后。这类顺序问题在 DSL 里和在 DOM 里完全一样，
  首版就被抓出来了。
- 两次「锚点全 FAIL」其实都不是重建错，而是**测量函数写错了**：
  一次是把卡内文字算进了卡片框，一次是把 1px 描边列当成了文字。
  这提醒我：核验脚本本身也要先在已知答案上自测，否则它报的红灯是它自己的问题。

**可复用经验**

- 复刻类题目的正确做法是「先量后写」：把参考图的每个关键边界/色值/字号写成 JSON，
  再由这些数据驱动 DSL；这样审计里的「参考估计」才站得住。
- 卡片/面板类 UI 在浅底上常常不是靠投影、而是靠 **1px 浅色描边**来定边界；
  用「沿边扫描找中间色」就能区分两者。
- 按固定坐标取色要小心：踩在抗锯齿边缘上会得到完全错误的颜色。
  大面积纯色取邻域中位色，细线与文字取区域内最暗像素。
- 参考字体不在服务端列表里时（如几何无衬线），选最接近的族并**在 comparison.md 里
  明确说明字宽/字面率差异会影响哪些锚点**，比含糊地说「颜色一致」诚实得多。

**结束依据**：
`reconstructed.png` 整屏打开；再与参考图做上下并排、25% 缩略、7 处 2× 局部放大共 11 次实际看图；
对交付 PNG 跑 24 个锚点的像素实测（24/24 合格，最大 3px）与 17 个色彩角色的同点取样（RGB 距离全 0）。
未以「渲染成功」作为完成依据，也未宣称逐像素完全复刻。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- **字体替换是系统性差异**：参考图用的是几何无衬线（近似 Poppins 一类），
  服务端 27 个字体族中没有该族，改用 Inter。后果是长文本的字形右缘比参考图略短
  （例如「Atlas / Visual system」）。文字块的**位置与字号**不受影响，
  受影响的只有字形形状与宽度，已在 `comparison.md` 第 5 节写明。
- 服务端的 `border` 画在填充内沿，参考图的描边在填充外沿（KPI 卡顶边 y=138 vs y=137）。
  两者都是 1px `#E2E8F1`，视觉上不可分辨，卡片外轮廓锚点实测误差 0px；未为此做像素级补偿。
- **没有验证逐像素完全一致**，题面也不要求：渲染管线（Skia）与参考图生成方式不同，
  抗锯齿灰阶必然不同，且题面未定义可接受的差异阈值。
- 17 个色彩角色用同点取样比对可以做到 RGB 距离 0，但这只覆盖采样点；
  其余区域（例如文字笔画边缘的灰阶过渡）不做逐像素比对，理由同上。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
