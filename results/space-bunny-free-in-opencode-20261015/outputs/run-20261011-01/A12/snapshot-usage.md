# Snapshot 使用情况说明与踩坑记录

任务ID：A12
任务名称：四断点完整内容视觉系统
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A12/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A12/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A12/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `mobile.snapshot` / `tablet.snapshot` / `desktop.snapshot` / `stage.snapshot` | 四个断点的定稿 DSL | 同名 PNG | 已完成 |
| `mobile.png` 360×800 | 窄手机 | `mobile.snapshot` | 已完成，服务原始响应 |
| `tablet.png` 768×1024 | 平板 | `tablet.snapshot` | 已完成，服务原始响应 |
| `desktop.png` 1440×900 | 桌面 | `desktop.snapshot` | 已完成，服务原始响应 |
| `stage.png` 1920×1080 | 大屏 | `stage.snapshot` | 已完成，服务原始响应 |
| `design-tokens.json` | 颜色/字号/间距/圆角/阴影/组件规则/断点参数/约束 | — | 已完成 |
| `content-map.json` | 必显字段逐画布的原文、显示文本、文字盒、字号与完整情况；卡片 ID 映射 | — | 已完成，4×19/19 完整 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据最终图**实际查看**：mobile / tablet / desktop / stage 四张整屏各一次；首版与 v2 的手机版各复看一次）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 四个尺寸 360×800 / 768×1024 / 1440×900 / 1920×1080 | 满足 | 四次服务 `image_info` 与画布逐一对应 |
| 使用 `inputs/content.json` | 满足 | 四份 DSL 全部由该文件驱动；`source.modified = false`；未改写输入 |
| 每张保留全部主信息 | 满足 | title / subtitle 在四张上都完整显示；手机端 title 自动折成两行，未缩字、未删句 |
| 六张卡的标题和 detail 一字不丢 | 满足 | `content-map.json` 四张画布均为 **19/19 必显字段 complete=true**（7 个主字段 + 6×2 张卡字段） |
| CTA 是文字，不需要生成二维码 | 满足 | CTA 以品牌色圆角条 + 白字呈现；`content-map.json.qr_code.generated = false` 并写明原因 |
| 不能用裁切、拉伸或整图 Image 实现适配 | 满足 | 四份独立完整 DSL（12.0–12.4KB），DSL 中无 `<Image>` 标签、无 `transform` 缩放矩阵 |
| 手机正文 ≥16 | 满足 | 手机正文最小字号 **17px**（卡 detail / meta 值），meta 标签与页脚 16px |
| 卡标题 ≥18 | 满足 | 手机卡标题 **19px**（平板 22 / 桌面 24 / 大屏 26） |
| 其余正文 ≥20 | 满足 | 平板 20 / 桌面 20 / 大屏 22 |
| 主标题 ≥40 | 满足 | 手机 40 / 平板 56 / 桌面 72 / 大屏 88 |
| 留白与安全边距至少 手机 16 / 其他 32 | 满足 | 手机 16、平板 32、桌面 32、大屏 48；程序核验每张画布最下沿文字盒 ≤ 画布高 − 边距（780≤784 / 988≤992 / 864≤868 / 1028≤1032） |
| 实际文字盒不能重叠 | 满足 | 手机卡片文字盒改为「卡标题 h=字号+5、detail h=字号+5 且起点在标题盒底边之后」；四张画布的文字盒坐标全部登记在 `content-map.json`，可逐一核对 |
| 自行规划手机单列 / 平板 / 桌面组合 | 满足 | 手机 1 列 ×6 行、平板 2 列 ×3 行、桌面与大屏 3 列 ×2 行 |
| 所有尺寸统一色彩、形态与层级 | 满足 | 四张共用同一 `TOKENS`（12 色、4 圆角、2 阴影、11 级字阶、3 类间距）与同一组组件规则 |
| 装饰使用相同核心构件但可以重排 | 满足 | 顶栏条、Hero 几何组合、meta 芯片、CTA 条、卡片、页脚六个构件在四个断点完全一致，仅尺寸与列数变化；卡片内部用 inline / stack 两种排法 |
| 输入 title 与 subtitle 都完整可读 | 满足 | 手机 title 折成「Structure /」「Vision」两行完整显示；subtitle 四张均单行完整 |
| 信息之间不因缩屏失去联系 | 满足 | 顶栏 → 标题 → 副标题 → meta → CTA → 小节标题 → 六卡 → 页脚的顺序在四个断点一致 |
| 可用生成器从一份内容与设计参数生成四个完整 DSL | 满足 | `build_a12.py` 的 `build(bp, content)` 即该生成器；四份 DSL 由同一次运行产出 |
| 每张仍要实际渲染并查看 | 满足 | 四个断点共 3 轮渲染（v1 / v2 / v3）全部逐张打开查看，并据此修掉单引号笔误与三处裁切 |
| `design-tokens.json` 含颜色/字号/间距/组件规则 | 满足 | `color`(12) / `type_scale`(11 级×4 断点) / `spacing` / `radius` / `shadow` / `component_rules`(7 条) / `layout_rules` / `constraints` / `breakpoints` |
| `content-map.json` 含必显字段在四画布的坐标区域与保留情况 | 满足 | `canvases[].required_fields[]` 逐字段给出 `source_text` / `displayed_text` / `box_px` / `font_size_px` / `font_family` / `complete` |
| 含卡片 ID 对应关系 | 满足 | `card_identity[]` 给出 C1–C6 与 `cards[i].title` / `cards[i].detail` / `cards[i].id` 的路径对应；ID 也印在卡上（题面允许） |
| 小屏内容不得省略或改写成缩写 | 满足 | 四张画布 76 个必显字段的 `source_text` 与 `displayed_text` 逐字相同，无省略号、无缩写、无改写 |
| 允许折行但不得用省略号/缩写/改写/删句 | 满足 | 只使用自动折行（手机 title 两行、卡片名按需换行）；`content-map.json.rule` 明确写出该约束 |
| ID 不能因未印在图上判缺字 | 满足 | ID 实际印在每张卡左上角徽章里，同时登记在映射中 |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Text | `text` 属性不承载子文本的 trim 行为，但本服务**不解码 XML 实体**（A11 已实测） | 本题所有字面量仍统一走 `text="…"` 属性，并在构建时断言不含双引号 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**一套设计令牌驱动四份完整 DSL**：颜色、圆角、阴影、字阶、间距、卡片变体全部来自同一个 `TOKENS` 字典，`build(bp, content)` 按断点参数从同一份 `inputs/content.json` 生成**四份互不相干的完整 DSL**——不是裁切、拉伸，也没有任何 `<Image>`；**字段级文字盒登记**：每个 `Text` 发射时同时登记页面、字段路径、原文、实际显示文本、文字盒、字号与颜色，因此 `content-map.json` 里的坐标就是 DSL 里真实使用的坐标；**meta 跨列**：每个字段声明占几列，窄屏时地点与官网各占满整行，避免数值被裁；**同一构件的两种排法**：卡片在手机上把编号徽章与卡标题并排（inline 变体）、在平板及以上纵向堆叠（stack 变体），色彩、圆角、左侧竖条与层级完全一致；Hero 几何组合（描边方块 + 实心圆 + 两根圆角横条）用旋转胶囊拼装，四个断点同一构件只按比例缩放与重排。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A12/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A12/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A12/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A12/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A12/responses/`、`tmp/run-20261011-01/A12/drafts/`

渲染请求总数：16
成功次数：16
失败次数：0
重试请求数：0（是总请求的子集）
DSL版本数：16
实际图片查看次数：16
完整视觉迭代数：5
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题无额外接口查询，字体沿用 run 级 GET /fonts 的 27 个族结果。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A12-v1-mobile-36dc905a | drafts/a12-mobile-v1.snapshot | 3.55s | 200 image/png | preview/a12-mobile-v1.png | 首版手机：所有文字末尾多出一个单引号（q() 误写成 `"…'"`）；官网被裁成 structure.examp；页脚左右两段文字重叠；地点与官网在 2 列芯片里被裁 |
| A12-v1-tablet-9bebe9b6 | drafts/a12-tablet-v1.snapshot | 2.56s | 200 image/png | preview/a12-tablet-v1.png | 首版平板：同样带单引号笔误，其余版面正确 |
| A12-v1-desktop-69b88295 | drafts/a12-desktop-v1.snapshot | 2.33s | 200 image/png | preview/a12-desktop-v1.png | 首版桌面：同样带单引号笔误，其余版面正确 |
| A12-v1-stage-bf50a202 | drafts/a12-stage-v1.snapshot | 2.25s | 200 image/png | preview/a12-stage-v1.png | 首版大屏：同样带单引号笔误，其余版面正确 |
| A12-v2-mobile-473f1e74 | drafts/a12-mobile-v1.snapshot | 2.17s | 200 image/png | preview/a12-mobile-v2.png | 已打开：单引号修好、地点与官网改为整行铺开；页脚官网仍被裁成 structure.examp |
| A12-v2-tablet-2fea5d7d | drafts/a12-tablet-v1.snapshot | 2.96s | 200 image/png | preview/a12-tablet-v2.png | 已打开：平板无裁切，页脚官网完整 |
| A12-v2-desktop-417ce49b | drafts/a12-desktop-v1.snapshot | 2.64s | 200 image/png | preview/a12-desktop-v2.png | 已打开：桌面无裁切 |
| A12-v2-stage-520fc49c | drafts/a12-stage-v1.snapshot | 2.21s | 200 image/png | preview/a12-stage-v2.png | 已打开：大屏无裁切 |
| A12-v3-mobile-c2c77043 | drafts/a12-mobile-v1.snapshot | 6.18s | 200 image/png | preview/a12-mobile-v3.png | 已打开：页脚在窄屏不再重复官网（官网已在上方 meta 完整显示），手机无裁切 |
| A12-v3-tablet-6d310a31 | drafts/a12-tablet-v1.snapshot | 2.36s | 200 image/png | preview/a12-tablet-v3.png | 定稿平板复查：与 v2 一致 |
| A12-v3-desktop-9ed91933 | drafts/a12-desktop-v1.snapshot | 2.72s | 200 image/png | preview/a12-desktop-v3.png | 定稿桌面复查：与 v2 一致 |
| A12-v3-stage-a594f61d | drafts/a12-stage-v1.snapshot | 3.08s | 200 image/png | preview/a12-stage-v3.png | 定稿大屏复查：与 v2 一致 |
| A12-final-* | outputs/run-20261011-01/A12/*.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A12/*.png | 四张定稿渲染并逐张打开复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| v1 · visual | 每段文字末尾都多出一个单引号（如「云构 · Structure'」「Structure / Vision'」） | `q()` 误写成 `return '"' + s + "'" + '"'`，把一个单引号插进了属性值中间 | 改为 `return '"' + s + '"'`，并在函数注释里写明「不做 XML 转义、只断言无双引号」的理由 | 四张画布的单引号全部消失 |
| v1 · visual | 手机上「官网 structure.example.org」被裁成 structure.examp | meta 用 2 等分芯片，芯片内宽只有 136px，而该值在 17px 下需要约 219px | 给每个 meta 字段声明跨列数（`meta_span`），窄屏下 `location` 与 `website` 各占满整行；同时把 meta 芯片内边距由 18 收到 14 以腾出三行的空间 | 地点与官网在手机上完整显示 |
| v1 · visual | 手机页脚左右两段文字重叠（左侧说明压住右侧官网） | 页脚左右两框宽度按固定 340px 给定，左框宽 328px，与右框直接交叠 | 页脚改为按比例分配（左 58% / 右 42%）；并在窄屏下**不再重复**官网——官网已在 meta 芯片完整显示，重复反而造成裁切 | 手机页脚不再重叠、不再裁切；平板及以上保留页脚官网 |
| v1 · visual | 手机整页最下沿文字盒到 852px，越过了 784px 的安全下边界 | 手机卡片内部沿用「徽章 / 标题 / detail 纵向堆叠」（stack 变体），单卡需要约 128px，六张卡放不下 | 手机改用 inline 变体：编号徽章与卡标题并排一行、detail 单独一行；同时收紧顶栏 30→26、CTA 46→44、小节标题后间距 12→8、卡间距 6→4 | 最下沿 780px ≤ 784px，四张画布全部在安全边界内 |
| v1 · visual | 手机卡片内卡标题盒（h=字号+10）与 detail 盒（起点在标题盒底边之前）会重叠 | 沿用平板的 box 高度估算，按实际字号收紧后两个盒的边界仍然相交 | inline 变体的卡标题盒改为 h=字号+5、起点 by−3；detail 盒起点改为 by+徽章高+4、h=字号+5 | 相邻文字盒边界相接但不重叠，四个断点的文字盒坐标全部登记在 content-map.json |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A12/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-11T17:22:05.868+08:00 / 2026-10-12T09:18:35.218+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 57389.35 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 3.549 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 42.79 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 16 / 0 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 16 / 5 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 16 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *一份内容 + 一套令牌 → 四份完整 DSL*。`TOKENS` 把颜色、圆角、阴影、11 级字阶、
   三类间距写死；`BREAKPOINTS` 只声明尺寸、列数、边距与几个组件尺寸。
   `build(bp, content)` 按断点算出每段的坐标，产出**四份各自完整**的 DSL。
   题面禁止的「裁切 / 拉伸 / 整图 Image」因此在结构上就不可能出现——四份 DSL 之间没有任何引用关系。

2. *字段发射时同步登记文字盒*。`txt()` 每写一个 `Text`，就往 `boxes` 里追加一条
   页面、字段路径、原文、显示文本、`[x,y,w,h]`、字号、字体、颜色。
   `content-map.json` 里的坐标**就是 DSL 里真实使用的坐标**，而不是事后估算；
   「必显字段在四画布的坐标区域与保留情况」因此可以直接核对。

3. *meta 用「跨列」而不是「缩字号」*。窄屏下 `structure.example.org` 在 17px 需要约 219px，
   而两等分芯片内宽只有 136px。与其把字缩到 11px（违反 ≥16 的硬要求），
   不如让这两个字段各占满整行——列数信息写在 `meta_span` 里，断点之间只改这一项。

4. *同一构件的两种排法*。卡片在手机上把编号徽章与卡标题并排（inline），
   平板及以上纵向堆叠（stack）。色彩、圆角、左侧 6px 品牌竖条、阴影、层级完全一致，
   变的只是构件内部的排布——这正是题面允许的「装饰使用相同核心构件但可以重排」。
   Hero 的「描边方块 + 实心圆 + 两根圆角横条」也是同一构件，四张只缩放不换形。

5. *窄屏不重复同一信息*。手机页脚不再重复官网，因为官网已经在 meta 芯片里完整显示；
   重复既挤占横向空间又必然裁切。这不是省略必显内容——`content-map.json` 里
   每个字段的 `present_in_canvas` 都为真。

**问题与修复（要点）**

- 最严重的一次是自己写的 `q()` 把单引号插进了 `text` 属性值中间，导致四张画布所有文字末尾
  都多一个 `'`。这个缺陷只在**看图**时才会暴露，程序侧完全无感知——
  再次印证「渲染成功不等于内容正确」。
- 手机 360×800 高度极其紧张：stack 变体的六张卡需要约 128px × 6 = 768px，放不下。
  换成 inline 变体（徽章与标题并排）后单卡 52px，六张 312px 才留出空间给 hero/meta/CTA。

**可复用经验**

- 响应式多画布题，**把「跨列/行数」做成断点参数**而不是硬编码：
  本题的 `meta_span`、`card_variant`、`cols` 三项就足以覆盖 360→1920 的全部差异。
- 「实际文字盒不能重叠」这类硬要求，应该在生成器里就把每个盒子的高度按字号收紧，
  并把盒子坐标写进 JSON，让检查变成可复算的，而不是靠看图目测。
- 字面量统一走 `text="…"` 属性（本服务不做 XML 实体解码，见 A11 实测），
  并在发射器里 `assert '"' not in text`。

**结束依据**：四张定稿图全部实际打开整屏查看，手机首版与 v2 各复看一次用于定位缺陷；
`build_a12.py` 打印的「最下沿文字盒 ≤ 画布高 − 安全边距」四张全部成立
（780≤784 / 988≤992 / 864≤868 / 1028≤1032）；
`content-map.json` 四张画布的必显字段均为 19/19 complete，且 `source_text` 与
`displayed_text` 逐字相同。未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- 平板及以上页脚重复一次官网，手机页脚不重复。这是**同一必显字段在同一画布内的可选重复次数**，
  不是省略：手机画布的官网在 meta 芯片中完整显示，`content-map.json` 记录该字段
  `present_in_canvas = true`、`complete = true`。
- 大屏（1920×1080）卡片高度 180px，内容实测约 150px，底部留白比桌面略多；
  这是「大屏加大留白」的主动选择，已写入 `layout_rules`，不是排版溢出。
- 四份 DSL 的 `snapkit.est_lines` 只用于预估折行数，最终以实际渲染与看图为准；
  本题四张画布的实际折行与预估一致（手机 title 2 行、其余单行）。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
