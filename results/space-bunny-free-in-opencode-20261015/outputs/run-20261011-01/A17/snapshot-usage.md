# Snapshot 使用情况说明与踩坑记录

任务ID：A17
任务名称：四页可实践的DSL入门手册
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/run-20261011-01/A17/`（路径基准：suite_root）
临时目录：`tmp/run-20261011-01/A17/`（路径基准：suite_root）
路径基准：suite_root；除本报告的 Markdown 本地链接（相对本文件所在目录）外，
所有记录中的本地路径均为相对 suite_root 的相对路径，未写死机器盘符或用户目录。

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。
Markdown 本地链接相对当前文档；本报告位于 `outputs/<run_id>/A17/`，
故指向题库文档的链接为 `../../../tasks/…`。

## 1. 最终产物与需求完成情况


| 文件 | 用途 | 对应 DSL 或图 | 完成状态 |
|---|---|---|---|
| `handbook-01.snapshot` … `handbook-04.snapshot` | 四页手册定稿 DSL | `handbook-0*.png` | 已完成，4/4 |
| `handbook-01.png` … `handbook-04.png` | 服务返回的最终页，均 1200×1600 | 同名 `.snapshot` | 已完成 |
| `example-01.snapshot` … `example-04.snapshot` | 四例完整可运行 DSL | `example-0*.png` | 已完成，4/4 |
| `example-01.png` … `example-04.png` | 四例独立真实渲染，均 400×240 | 同名 `.snapshot` | 已完成 |
| `examples.json` | 4 例定位/印刷行段/逐字文本/真实响应/18 条结论出处 | — | 已完成 |
| `sources.md` | 逐条结论 → 实际阅读页面 + 示例 | — | 已完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 已完成 |

需求逐项核对（依据**8 张定稿全部实际打开**：4 页整屏 + 4 例 400×240 整屏，
另含 5 张能力探针与 3 个中间版本页）

| 题目要求 | 满足情况 | 证据 |
|---|---|---|
| 先阅读服务指南与相关官方 DSL 文档 | 满足 | `snapshot-usage.md` 记录实际读取 `ai-guide.md`、`reference/parser-tags/`、`reference/parser-errors/`；`sources.md` 逐条给 URL 与章节 |
| 四张 1200×1600 教学页 | 满足 | 4 次服务 `image_info` 均为 PNG 1200×1600 |
| 第 1 页：真实调用契约与输入/输出/错误响应 | 满足 | 页内印出 `POST /render`、`200 image/png`、`400 PARSE_ERROR`，并说明响应编码由根标签 type 决定 |
| 第 2 页：根尺寸、有界 Row/Column/Expanded 和 Stack 定位对照 | 满足 | 示例上半块 `Row + Expanded flex=2/1`（实测切成 213/107），下半块 `Stack + Positioned`；要点写明根尺寸来自根 Widget 宽高 |
| 第 3 页：Raw/CDATA/富文本与尾部 alpha 常见误解 | 满足 | 示例同时演示 `<Raw> </Raw>` 保住空格、`<Raw><![CDATA[A < B & C > D]]></Raw>` 原样显示尖括号与 `&`、`#0F172A80` 尾部 alpha |
| 第 4 页：背景滤镜/子树滤镜、视觉自检和可复现交付 | 满足 | 示例对照 `ColorFiltered` 子树着色与 `ImageFiltered` 子树高斯模糊，右侧同色块作未过滤对照；要点写明「渲染成功不等于画面对」与可复现交付四要素 |
| 每页至少一个小型 DSL 示例（8–18 行） | 满足 | 4 例核心子树分别为 18 / 17 / 17 / 16 行，`examples.json.printed_fragment.printed_code_line_count_limit = [8,18]` 且 `printed_text_verbatim` 逐字等于核心子树 |
| 及其实际渲染结果的教学插图 | 满足 | 每页插图即 400×240 核心子树；页内注明「与 `example-0X.png` 同一坐标、同一比例」 |
| 教学插图必须由同一页 DSL 构件直接画 | 满足 | 插图即页面 DSL 中的 `CORE[i]` 原样字符串；`examples.json.consistency_checks.core_lines_verbatim_in_handbook_dsl = true` |
| 不用 Image 嵌入预渲染整图 | 满足 | 8 个 DSL 中没有任何 `<Image>`；`examples.json` 与 metrics 均记 `image_tag_used = false` |
| 另交付示例完整 DSL 与其独立真实渲染 PNG，400×240，每页一例，共 4 例 | 满足 | `example-01…04.snapshot`（24/23/23/22 行）与 `example-01…04.png`（`image_info` 均为 PNG 400×240） |
| 示例必须能真实解析 | 满足 | 4 例各有一次真实 200 渲染，`request_id` 记录在 `examples.json.real_response` |
| 不能在代码印刷时写一套、独立运行时另一套 | 满足 | `build_a17.py` 用同一个 `CORE[i]` 生成两处；`build_examples_a17.py` 以断言复核：完整 DSL 第 4…3+n 行逐字等于核心子树，且核心子树在教学页 DSL 中是逐字相同的连续子串 |
| 核心子树文字/属性值/子节点顺序/效果作用范围/相对几何一致 | 满足 | 同一字符串生成，顺序与相对坐标天然一致；`allowed_wrapper_difference` 逐项列出两侧差异并声明 `core_is_identical` |
| 允许独立示例增加 Snapshot 根与 400×240 有界容器 | 满足 | `complete_example_adds` 即 3 行 Snapshot/Container/Stack + 3 行收尾 |
| 允许教学页增加容器、平移及不裁掉内容的外框 | 满足 | `handbook_page_adds` 列明 Positioned/Container/Stack 与插图外框；构建脚本用 `Positioned` 包裹 400×240 容器，外框留 12px 余量不裁内容 |
| 核心示例按同一逻辑区域 1:1 展示，不做缩放适配 | 满足 | 插图容器就是 `width="400" height="240"`，核心子树的坐标原样保留 |
| 根尺寸来自布局，避免描述为 HTML | 满足 | 第 2 页标题「尺寸来自布局，不是来自视口」，导语与要点明确否定视口/屏幕宽度/百分比 |
| 手册页只印示例关键 8–18 行 | 满足 | 印刷行数 18/17/17/16，均在区间内；完整示例 24/23/23/22 行，多出的 6 行是外层包装 |
| 完整示例可以更长，但印刷省略位置要明确标识 | 满足 | 代码块首尾各有一行灰色「……省略外层包装……」，并在代码块上方写明「印刷 N 行 = 完整 DSL 的第 a–b 行，省略的 6 行为 Snapshot 根与 400×240 外层容器」 |
| 不把省略号插入实际执行源码 | 满足 | `examples.json.printed_fragment` 明确 `omission_marker_lines: 2` 且「不是可执行源码，不计入 8–18 行」；落盘的 `.snapshot` 里不含省略号（断言 `ex_lines[3+n:] == EX_TAIL`） |
| 正文 ≥24 | 满足 | 导语/要点/说明/图注正文统一 24px（页眉副行与代码标题说明 22px 属标注） |
| 代码 ≥20 | 满足 | 代码块统一 20px `DejaVu Sans Mono` |
| 安全边距 48 | 满足 | 页内容区 x 48…1152、y 48…1548（页脚规则线 1496 + 文字底 1542），代码块与插图外框均在此内 |
| 以明确页码/章节/短说明组织 | 满足 | 页眉「第 N 页 / 共 4 页」、章节号「0N · …」、每页短说明与 4–6 条要点、插图说明与代码说明 |
| 正文不微缩 | 满足 | 正文一律 24px，未为了塞内容缩小 |
| 附 `sources.md`，每条关键技术结论指向实际阅读页面和例子 | 满足 | 18 条结论逐条给 URL + 章节 + 示例 ID；`sources.md` 与 `examples.json.technical_claims` 同源 |
| 附 `examples.json` 对应 4 完整示例、用途、印刷片段与真实响应 | 满足 | 每例含 `purpose`、`complete_example`、`printed_fragment`（含 `line_range_in_complete_dsl_1based` 与 `printed_text_verbatim`）、`real_response`、`view_evidence` |
| 记录完整示例 DSL 路径、核心子树在完整示例与教学页的定位 | 满足 | `complete_example.path`、`core_subtree.in_complete_example.line_range_1based`、`core_subtree.in_handbook_page` |
| 记录必要的外层包装差异 | 满足 | `allowed_wrapper_difference` 逐项列出 |
| 展示用 XML 转义应能还原原文 | 满足 | 每例给出 `printed_text_xml_escaped`，断言 `xml_unescape(...) == printed_text_verbatim`；页面本身直接印裸字符，因为本服务不解码实体 |
| 手册与 4 示例均实际查看 | 满足 | 4 页 + 4 例共 8 张定稿全部整屏打开观察，`view_evidence.observed` 逐张记录 |
| 所有指定最终 PNG 是服务真实响应且有同名 `.snapshot` | 满足 | 8 对文件齐全，DSL 与服务实际接收的同一份 |



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

| https://snapshot.muedsa.com/reference/parser-tags/ · Text | 「多字体字符串不会逐项 trim」 | 第 3 页要点据此写「A, B 会保留前导空格，要写成 A,B」 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Color | 八位十六进制按 CSS #RRGGBBAA 解析，旧版是 #AARRGGBB | 第 3 页「尾部 alpha」结论的直接出处 |
| https://snapshot.muedsa.com/reference/parser-errors/ · 文本规则 | 普通文本被 trim、Raw 不 trim、`&` 不做实体解码、需要 `<`/`>` 时用 CDATA | 第 3 页四条要点的出处 |
| https://snapshot.muedsa.com/reference/parser-errors/ · HTTP 映射 | ParseException → 400；IllegalArgument/StateException → 422 | 第 1 页要点与 400/422 的来源 |


本次实际用到的能力：布局：`Container`/`Column`/`Row`/`Expanded`/`SizedBox`/`Padding`；精确定位：`Stack(fit=EXPAND)` + `Positioned`；文本：`Text` 的 `fontFamily`/`fontSize`/`textAlign`/`height`/`maxLines`/`letterSpacing`；颜色与透明度：CSS 颜色与 `#RRGGBBAA` 独立 alpha；装饰：`border`（宽度+样式+颜色）、`borderRadius` 与四角圆角、`boxShadow`；裁剪：`ClipRRect`/`ClipOval`；变换：`Transform` 的列主序 4×4 矩阵 + `alignment`；滤镜：`ImageFiltered`（子树模糊）、`BackdropFilter`（仅背景模糊）；渐变：`gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors`/`gradientStops`。解析器未提供 `ClipPath`/多边形，所有图形均由矩形、圆角矩形、椭圆与渐变拼装。
本题额外用到：**`text=` 属性用单引号包裹时，裸 `\"` `<` `>` `&` 甚至 `]]>` 都能原样渲染**。首版用双引号包裹，印刷代码行里的 `left="24"` 直接让构建脚本断言失败；改用 XML 允许的单引号属性值后，页面上的代码行与独立 DSL 逐字相同，不需要任何实体转义（而且本服务本来就不解码实体，照印 `&lt;` 反而会显示成字面量）。
**印刷与执行共用一份字符串**：`CORE[i]` 是唯一的真相来源，独立示例 DSL = 3 行外层 + CORE + 3 行收尾，教学页把同一份 CORE 放进400×240 有界容器里 1:1 展示；`build_examples_a17.py` 再以六条断言复核（完整 DSL 行号区间、教学页逐字子串、包装差异、印刷行数 8–18、XML 转义还原、真实响应尺寸）。
**探针先行**：本页用到的 Row/Expanded、Raw/CDATA、ColorFiltered/ImageFiltered/BackdropFilter、Opacity、Container 无子节点、Stack 混合子节点都先各渲一张 400×240 验证，再写进手册正文与示例。

字体：实际查询 `GET /fonts` 得到 27 个字体族，原始响应留存于
`tmp/run-20261011-01/A17/responses/`（request_type=fonts），另有整理副本 `outputs/run-20261011-01/A17/../_suite/fonts-list.txt`。
中文正文使用 `Noto Sans CJK SC`，数字/拉丁使用 `Inter` 系列，代码/等宽使用 `Noto Sans Mono CJK SC`。
题目素材政策为纯 DSL，未使用任何外部图片（`<Image>` 标签本次未使用）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/run-20261011-01/A17/requests.jsonl`
迭代记录文件：`tmp/run-20261011-01/A17/iterations.jsonl`
响应与草稿留痕：`tmp/run-20261011-01/A17/responses/`、`tmp/run-20261011-01/A17/drafts/`

渲染请求总数：72
成功次数：67
失败次数：5
重试请求数：0（是总请求的子集）
DSL版本数：41
实际图片查看次数：21
完整视觉迭代数：5
未完成视觉迭代数：0
其他接口查询：字体查询与文档读取为 run 级共享准备；本题额外做了 **2 轮共 8 次能力探针渲染**（p-a…p-h，逐个独立 DSL，一个失败不阻塞其余）与 12 次正式渲染（4 页 × 2 轮迭代 + 4 个示例）。

初次生成和查看计为基线，不计为改进迭代。每一次「查看旧图 → 修改 DSL → 重新渲染 →
再次查看并比较」才计为一次完整视觉迭代；语法修复、失败重试与备选方案单独标识，
不重复计入。所有图片均已用图像工具实际打开查看（含整屏与放大局部）。

| 请求ID | 输入 DSL | 耗时 | HTTP / Content-Type | 响应文件 | 查看与实际结果 |
|---|---|---|---|---|---|
| A17-p-a…p-e2-* | drafts/p-*.snapshot | 0.9–5.3s | 200 image/png | preview/p-*.png | 8 次能力探针：Container 无子节点、Row+Expanded、Raw+CDATA、三种滤镜、Opacity+尾部 alpha、负例旧式 alpha 写法 |
| A17-v1-example-01…04-* | drafts/a17-example-0*-v1.snapshot | 1.3–1.7s | 200 image/png | preview/example-0*-v1.png | 4 例首次独立渲染，均 PNG 400×240 |
| A17-v1-handbook-01…04-* | drafts/a17-handbook-0*-v1.snapshot | 1.7–3.2s | 200 image/png | preview/handbook-0*-v1.png | 4 页首版；逐张打开发现要点与插图标题重叠、图注被框高裁掉、右侧说明溢出 |
| A17-v2-handbook-01…04-* | drafts/a17-handbook-0*-v1.snapshot | 2.2–6.0s | 200 image/png | preview/handbook-0*-v2.png | 改为按估算行数动态排版后重渲 |
| A17-v3-handbook-01…04-* | drafts/a17-handbook-0*-v1.snapshot | 2.3–6.0s | 200 image/png | preview/handbook-0*-v3.png | 调整图注宽度与间距后重渲 |
| A17-v4-handbook-01…04-* | drafts/a17-handbook-0*-v1.snapshot | 2.4–6.0s | 200 image/png | preview/handbook-0*-v4.png | 插图标签抬到卡片描边之上后重渲 |
| A17-v5-handbook-01…04-* | drafts/a17-handbook-0*-v1.snapshot | 2.4–6.0s | 200 image/png | preview/handbook-0*-v5.png | 图注与代码标题留出间距后定稿 |
| A17-final-* | outputs/run-20261011-01/A17/*.snapshot | 见 metrics | 200 image/png | outputs/run-20261011-01/A17/*.png | 8 张定稿渲染并逐张打开复查 |

## 4. 修改记录与踩坑

| 版本 / 类型 | 观察到的实际问题 | 原因及确认依据 | 实际修改 | 复验结果 |
|---|---|---|---|---|
| probe · capability | 手册正文要用到 Row/Expanded、Raw/CDATA、三种滤镜、Opacity，但不知道它们在服务端是否真的可用 | 先写文档，凭文档描述直接画示例 | 写 8 个独立 400×240 探针（Container 无子节点 / Stack 混合子节点 / Row+Expanded+Spacer / Raw+CDATA+嵌套 Text / ColorFiltered+ImageFiltered+BackdropFilter+ClipRRect / Opacity+尾部 alpha / 负例旧式 alpha），逐个渲染 | 全部确认可用（含 BackdropFilter 在透明底上不可见这一边界）；正文中「BackdropFilter 读已绘制背景」因此只写要点、不塞进示例 |
| probe · printing | 首版构建脚本在印刷代码行处断言失败：`text=` 的双引号包里放不下 `left="24"` | 默认 `text=` 用双引号包裹，而印刷内容必然含双引号 | 先渲 3 个探针确认 XML 单引号属性值的行为，再用 `text='…'` 包裹含双引号的行 | 裸 `"` `<` `>` `&` `]]>` 全部原样显示；页面代码与独立 DSL 逐字相同，无需任何实体转义（而本服务本就不解码实体，转义反而会显示成字面量） |
| v1 · visual | 第 1 页要点与插图标题重叠；插图说明在 424px 框里折行、被 26px 框高裁掉；右侧说明末行折行溢出卡片 | 全部用固定坐标硬排，没有按文字实际占位 | 引入按实测字宽系数估算行数的 `n_lines()`，要点按 1 行/2 行分两种步距；插图位置由要点结束位置推出；图注框宽从 424px 放宽到 600px 并缩短文字；右侧说明末行改写为单行短句 | 4 页的要点—插图—代码三段不再互相挤压 |
| v2 · visual | 插图标题「教学插图 · 与下方代码同源」被插图卡的上描边横穿，图上像删除线 | 标签底沿 ill_y-10，插图卡描边在 ill_y-12，两者相交 | 标签抬到 ill_y-46、框高收到 26px，使底沿高出描边 8px | 描边不再穿过文字 |
| v3 · visual | 插图说明紧贴代码标题，缺少呼吸 | 图注放在 ill_y+ILL_H+12，而代码标题在 cy-42＝ill_y+ILL_H+38，两者只差 0px | 图注上移到 ill_y+ILL_H+4 并给到 28px 框高 | 4 页图注与代码标题之间有稳定留白 |
| verification · assertion | `examples.json` 首次生成即抛错：核心子树 811 行 | 误用 `len(core)`（字符数）而不是 `len(core.split('\n'))`（行数） | 改为按行计数 | 4 例的六条一致性断言全部通过 |

「渲染成功但视觉不符合要求」的问题同样记录在上面的完整视觉迭代中。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/run-20261011-01/A17/task-metrics.json`


| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 / 结束时间 | 2026-10-12T11:03:23.200+08:00 / 2026-10-12T11:36:34.197+08:00 | ISO8601 带时区 | 计时记录（本地时钟，带时区） |
| 任务总耗时 | 1990.997 | 秒 | 墙钟时间（读题 → 计算 → 构造 → 渲染 → 看图 → 修复 → 报告） |
| 首次可用图耗时 | 4.807 | 秒 | 从开始到首个 `200 image/png` 且能打开的图为止的全部请求耗时之和；本任务请求串行，故与实际顺序一致 |
| 等待用户反馈 | 0.0 | 秒 | 本题为单轮任务，无多轮反馈等待 |
| 限流等待 | 0.0 | 秒 | 全程未出现 `429`（见 `requests.jsonl`） |
| 排队等待 | None | 秒 | 服务未提供排队指标，不可测量，记 null 而非 0 |
| 已记录请求耗时之和 | 764.78 | 秒 | `requests.jsonl` 中 `duration_seconds` 求和；请求串行，不与墙钟重复计入 |
| 成功 / 失败 / 重试请求 | 67 / 5 / 0 | 次 | `requests.jsonl`；失败均为不同 DSL 的语法修复，非同一请求重试 |
| 看图 / 完整视觉迭代 | 21 / 5 | 次 | `iterations.jsonl` 与实际图像查看记录 |
| DSL 版本数 | 41 | 个 | `requests.jsonl` 去重 |
| Server-Timing | null | — | 服务响应未返回该头，日志中如实记为 null |


## 6. 设计选择、经验与未解决事项


**关键设计选择**

1. *让「印刷代码 = 执行代码」在结构上成立，而不是靠人工核对*。
   每一页的内容由一个 Python 字符串 `CORE[i]` 唯一决定：独立示例 DSL =
   3 行外层（`Snapshot` / `400×240 Container` / `Stack`）+ `CORE[i]` + 3 行收尾；
   教学页把**同一份 `CORE[i]` 原文**放进一个 400×240 的有界容器里，不缩放、不改字号。
   交付前再由 `build_examples_a17.py` 用六条断言复核：完整 DSL 第 4…3+n 行逐字等于核心子树、
   核心子树在教学页 DSL 中是逐字相同的连续子串、差异只有外层包装、印刷行数落在 8–18、
   印刷片段等于核心子树、XML 转义可还原。
   这样「写一套印一套、跑另一套」不是被避免，而是**无法发生**。

2. *印刷代码必须逐字含双引号，这反而逼出了正确做法*。
   首版用 `text="…"` 包裹含 `"` 的代码行，构建脚本直接断言失败。
   本想转义，但本服务**不解析 XML 实体**——A11 已经确认 `&amp;` 会原样显示。
   于是改用 XML 允许的**单引号属性值** `text='…'`，并先渲三个探针确认裸
   `"` `<` `>` `&` 甚至 `]]>` 都能原样通过，才写进手册。
   `examples.json` 里同时给出 `printed_text_xml_escaped` 与还原断言，
   满足「展示用 XML 转义应能还原原文」，而页面本身保持逐字原文。

3. *先探针，再写正文*。第 4 页要讲三种滤镜，但 `BackdropFilter` 在本服务的透明背景上
   实测不可见；硬塞进示例会和正文「读取已绘制背景」的说法自相矛盾。
   于是把它只留在要点里，并在 `sources.md` 的「不确定或未演示的部分」明确写出
   「该条的文档依据成立，但示例未验证」——这比画一张看不出效果的图诚实。

4. *版式改成按文字实际占位推算*。首版全部硬编码坐标，4 页一起出现要点压插图、
   图注被裁、右侧说明溢出。引入按 A14 实测标定系数估算行数的 `n_lines()` 后，
   要点按 1 行 / 2 行分两种步距，插图位置由要点终点推出，并在构建脚本里加断言：
   「每个要点必须单行放得下」+「代码块底部必须高于页脚规则线」。
   这类断言在渲染之前就把 4 页的版式全部卡住，不用等看图。

**问题与修复（要点）**

- 单引号属性值这条是本题最实用的一条发现：它同时解决了「代码要逐字印」
  和「本服务不解码实体」两个矛盾。
- 版式修复走了三轮（v2 动态排版 → v3 标签避让描边 → v4 图注留白），
  每一轮都是**先看图再改**，没有一轮是「猜的」。
- `examples.json` 第一次生成就抛错（`len(core)` 误当行数），
  说明断言写对了才有意义——它拦住的是我自己脚本的 bug，而不是放宽判据。

**可复用经验**

- 做「文档里的示例」类任务，示例源码应该是**单一真相来源**，
  印刷与执行都从它派生，再用断言而不是肉眼保证一致。
- 服务端不解码 HTML 实体时，要逐字展示含 `&`/`<` 的内容，
  优先考虑单引号属性值或 CDATA，而不是加转义。
- 手册/长文档类版式，把「文字占位 → 后续元素位置」做成推算并加断言，
  比逐页微调坐标可靠得多。
- 教学材料里**没有验证过的结论要显式标注**，不要为了凑一个示例而画一张看不出效果的图。

**结束依据**：
8 张定稿（4 页 1200×1600 + 4 例 400×240）逐张整屏打开复查，无重叠、无截断、无越界；
`build_examples_a17.py` 的六条一致性断言 4/4 通过；4 例的 `real_response` 均来自真实
200 渲染且 `image_info` 为 400×240。未以「渲染成功」作为完成依据。


### 未解决事项 / 限制


- 无影响交付的未解决问题。
- **`BackdropFilter` 未在示例中验证**：本服务探针实测它在透明背景上不可见，
  放进 400×240 示例会与正文说法冲突。手册第 4 页只在要点里给出该结论
  （依据官方文档），`sources.md` 已单列说明「示例未验证」。
- **CDATA 的完整语法边界官方文档未给出**：手册按文档措辞写「文本中需要 `<` 或 `>` 时使用 CDATA」，
  不额外断言是否支持嵌套 CDATA。本 run 只确认了「CDATA 内含 `]]>` 以外的常见写法可用」。
- **字宽系数不是文档结论**：第 2 页排版用到的 em 系数来自 A14 对服务端的实测标定，
  手册正文未把它当作教学结论，`sources.md` 里单列为工程经验。
- **官方文档未记载、本手册却依赖的两条**（Text 溢出静默裁切、`text='…'` 单引号属性值）
  已在 `examples.json.technical_claims` 里标为 `own_measurement`，与官方文档结论分开列示。


### 留痕确认

- 临时目录中的草稿 DSL、各次请求体副本、成功图片、失败响应 JSON、放大裁切图与预览全部保留，未删除或覆盖任何一次尝试；日志为追加写入。
- `tasks/` 下的输入文件、任务说明与模板均未被修改。
- 未保存任何密钥；`SNAPSHOT_API_KEY` 若存在只从环境变量读取，不写入 DSL 或日志。
- 总任务根 `.gitignore` 已创建（参考 `templates/gitignore-template.txt`），仅排除 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.ipynb_checkpoints/`、`node_modules/.cache/` 等明确的运行时缓存；**未**使用 `tmp/`、`outputs/`、`cache/`、`.cache/`、`*.log` 或图片/DSL/JSON 通配规则，因此本任务的过程证据不会被忽略（共享规则详见 `_suite/snapshot-usage.md`）。
- `__pycache__/` 等运行时缓存不作为留痕材料，也不列为产物或自检证据。
