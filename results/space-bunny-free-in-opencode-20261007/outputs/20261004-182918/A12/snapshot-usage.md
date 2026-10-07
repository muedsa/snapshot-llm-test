# Snapshot 使用情况说明与踩坑记录

任务ID：A12
任务名称：四断点完整内容视觉系统
本次运行ID：20261004-182918
完成状态：完成
结束原因：需求满足并完成视觉自检（四张最终图全部逐张打开查看，并用像素级校核脚本复核）
输出目录：`D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\A12\`
临时目录：`D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A12\`

---

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `mobile.png` (360×800, 89470 B) | 窄手机版 | `mobile.snapshot` (20634 B) | 完成 |
| `tablet.png` (768×1024, 113680 B) | 平板版 | `tablet.snapshot` (23504 B) | 完成 |
| `desktop.png` (1440×900, 149352 B) | 桌面版 | `desktop.snapshot` (38614 B) | 完成 |
| `stage.png` (1920×1080, 158200 B) | 大屏版 | `stage.snapshot` (62319 B) | 完成 |
| `design-tokens.json` (5855 B) | 颜色/字阶/间距/组件规则 | — | 完成 |
| `content-map.json` (77 KB) | 每字段在四画布的坐标区域与保留情况 | — | 完成 |

四张 PNG 均为服务 `POST /snapshot` 返回的原始字节，未经任何后处理（`snapkit.render` 直接把响应体写入文件）。四张尺寸经 PIL 复核：360×800 / 768×1024 / 1440×900 / 1920×1080，全部 RGBA PNG。

### TASK.md 逐条硬指标自检

| 硬指标 | 实际值 | 结论 |
|---|---|---|
| 四个尺寸 360×800 / 768×1024 / 1440×900 / 1920×1080 | 全部一致 | 满足 |
| 每张保留全部主信息、网站及六张卡的标题和 detail，一字不丢 | 25 个输入字段（7 主字段 + 6×(id/title/detail)）全部以原文绘制；78 个内容字段逐一像素复核通过 | 满足 |
| CTA 是文字，不需要二维码 | CTA 以按钮内文字呈现；`images_embedded = 0` | 满足 |
| 不用裁切、拉伸或整图 Image 适配 | DSL 中 `<Image>` 标签数为 0；四份 DSL 各自独立计算全部坐标 | 满足 |
| 手机正文 ≥16 | 正文/卡 detail/元信息/标签/官网均为 16，卡标题 18 | 满足 |
| 卡标题 ≥18 | 手机 18 | 满足 |
| 其余正文 ≥20 | 平板/桌面/大屏正文最小 20 | 满足 |
| 主标题 ≥40 | 平板 48 / 桌面 72 / 大屏 96 | 满足 |
| 留白安全边距 ≥ 手机16 / 其他32 | 实测左/右/上/下边距：mobile 20/20/32/20.3；tablet 40/40/52/110.9；desktop 48/66/72/49.7；stage 72/72/84/360.7 | 满足 |
| 实际文字盒不能重叠 | 生成器对 78 个文字盒做墨迹带（ink band）两两相交检测，0 命中；交付后另用 PNG 复核 | 满足 |
| 手机单列 / 平板 / 桌面组合自行规划 | 1列×6行 / 2列×3行 / 3列×2行 / 6列×1行，四种不同网格 | 满足 |
| 各尺寸统一色彩、形态与层级 | 同一 11 色色板、同一字阶角色、同一圆角/描边、同一套构件；仅字号与位置按断点缩放 | 满足 |
| 装饰使用相同核心构件但可重排 | accent tick / 网格 / 序号 chip / ghost 序号 / L 形角标 / 六节点轨 / 圆环 在四档全部出现，仅位置数量变化 | 满足 |
| title 与 subtitle 都完整可读，信息不因缩屏失去联系 | title 在手机/平板为单行、桌面/大屏为两行，文字内容完全一致；日期/时间/地点始终同处一块 meta 面板，CTA 与官网始终同行或紧邻 | 满足 |
| 生成器从一份内容与设计参数生成四个完整 DSL，每张实际渲染并查看 | `build_a12.py` 单入口生成四份 DSL；四张均单独 POST 渲染并用 read 工具打开查看（另加局部放大） | 满足 |
| 交付 design-tokens.json 与 content-map.json | 两份均已生成，含颜色/字号/间距/组件规则与每字段坐标区域、保留状态 | 满足 |
| 小屏内容不得省略或改写成缩写 | 手机端 19 个内容字段与平板完全同集，无省略、无缩写 | 满足 |
| 所有指定最终 PNG 为服务真实响应且有同名 .snapshot | 4/4 | 满足 |

补充说明（设计chrome，非输入内容）：画面上另加了 `日期/时间/地点/官网/六个环节` 五个字段标签，用于说明日期时间地点三列的含义。它们只是标签，输入字段值本身在四张图上均按原文完整绘制，未替换任何输入文字。

---

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（`run-config.json` 的 `service_base_url`）
文档访问日期：2026-10-04 ~ 2026-10-05 (+08:00)

| 实际阅读/使用的来源 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `_suite/docs/ai-guide.md`（本题库 A01 阶段真实抓取，本次复用并重读） | `POST /snapshot` 请求体为 UTF-8 纯文本 DSL、响应体为图片字节；成功响应 Content-Type 为 `image/*`；失败为含 `code/message/requestId` 的 JSON；429/503 参考 `Retry-After`；`X-Request-Id` 可关联日志 | `snapkit.render()` 全部实现 |
| `_suite/docs/openapi.yaml`（同上，复用） | 接口与错误码语义 | `_suite/snapkit.py` |
| `_suite/fonts-list.txt`（本题库真实 `GET /fonts` 结果，本次复用） | 可用字族：`Inter`、`DejaVu Sans Mono`、`Noto Sans CJK SC` 等，未臆造字体名 | `dsllib.UI / LATIN / MONO` |
| `https://snapshot.muedsa.com/` DSL 文档（经 DSL-HANDBOOK.md 落实的实测结论） | 标签 `Snapshot/Container/Stack/Positioned/Text`；属性 `color/borderRadius/border/boxShadow/width/height/left/top/fontSize/fontFamily/fontStyle/textAlign/letterSpacing`；8 位色按 `#RRGGBBAA` | 四份 `.snapshot` |

本次实际用到的能力：绝对定位布局（`Stack fit="EXPAND"` + 全部 `Positioned` 显式坐标）、圆角矩形与描边面板、`border` 描边圆环、纯色/半透明填充（`#RRGGBBAA` 叠加）、`borderRadius` 圆角、用短矩形拼接的虚线（水平与竖向两种）、多字体族混排（Inter / Inter+Noto CJK SC / DejaVu Sans Mono）、`fontStyle="BOLD"`、`letterSpacing`、`textAlign`（CENTER/RIGHT）、嵌套 `Stack(fit="EXPAND")` 承载容器内文字。**未使用**：`<Image>`、任何外部素材、渐变、滤镜、变换矩阵——本题不需要。

### 探针（真实请求，用于把"猜测"换成"实测"）

| 探针 | 请求数 | 得到的可复用结论 | 留存 |
|---|---|---|---|
| `probe_fonts.py` | 17 | 12 条关键字符串在 100 px 下的墨迹宽度，首次暴露共享库 `est_width` 对等宽字体低估 7% | `probe/`、`font-metrics.json` |
| `probe_fonts2.py` | 22 | 20 字长串测得等宽 0.5935 em/字符（模型用 0.55）；同一批串的小比例探测还给出了最低落字高度 | `probe2/`、`font-metrics-2.json` |
| `probe_glyphband.py` | 64 | CJK 墨迹带高 ≈0.94 em、盒内起点 ≈0.31 em；等宽/拉丁墨迹带 ≈0.97/0.87 em 且偏上 | `probe3/`、`glyph-band.json` |
| `probe_fonts4.py` | 86 | 逐字号（16~96）复测，证明 100 px 指标不能线性外推到 20 px | `probe4/`、`font-metrics-4.json` |
| `probe_textalign.py` | 14 | 枚举 `textAlign` 取值：小写值报 `PARSE_ERROR`（skia `Alignment`），大写值合法 | `probe5/`、`textalign-probe.json` |
| `probe_textalign2.py` | 6 | 用正常字符串复测：LEFT/CENTER/RIGHT/START/END 均真实生效，JUSTIFY 表现为 LEFT | `probe6/`、`textalign-probe2.json` |
| `probe_metrics.py` | 104 | 枚举生成器真正用到的全部 104 组 (文本, 字族, 字号)，逐条实测墨迹宽度并回写 `measured-metrics.json`，之后所有文本框宽度改用实测值 | `probe-metrics/`、`measured-metrics.json` |

字体选择：`Inter`（拉丁标题）、`Inter,Noto Sans CJK SC`（中西混排正文）、`DejaVu Sans Mono`（日期/时间/网址/序号），全部来自真实 `GET /fonts` 结果，未使用未安装字体。

---

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp\20261004-182918\A12\requests.jsonl`（追加式，含每次请求 ID、类型、起止时间、耗时、HTTP 状态、Content-Type、请求/响应文件路径、错误摘要、服务端 requestId、Server-Timing）
迭代记录文件：`tmp\20261004-182918\A12\iterations.jsonl`
结构化指标：`outputs\20261004-182918\A12\task-metrics.json`

- 渲染请求总数：**590**（其中 4 次为最终交付图，586 次为探针与开发迭代）
- 成功次数：**569**
- 失败次数：**21**（全部为开发过程中的真实错误响应，见第 4 节）
- 重试请求数：**0**（未遇到 429/503；唯一一次网络超时 `A12-req-033` 由脚本自动重发并成功，未按限流重试计数）
- DSL 版本数：四份交付 `.snapshot` + `drafts/` 下逐次留存的草稿
- 实际图片查看次数：**4 张交付图各完整打开 1 次（共 4 次）+ 局部放大 7 次 + 探针图若干**
- 完整视觉迭代数：**5 轮**（v01 基线 → v02 → v03 → v04 → v05 定稿，逐轮"看图→改脚本→重渲染→再看"）
- 未完成视觉迭代数：**0**
- 其他接口查询：0（字体列表与 AI 指南为复用本题库 A01 的真实抓取结果，本次未重复请求）

### 交付图的实际渲染记录

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A12-req-587 | `outputs/.../mobile.snapshot` | 2026-10-05T00:08:27.209+08:00 起，2050.9 ms | 200 `image/png`（Server-Timing `render;dur=149.1, total;dur=154.4`） | `outputs/.../mobile.png` | 已查看：19 个字段齐全，CTA 居中、chip 数字居中、ghost 序号与角标不压字 |
| A12-req-588 | `outputs/.../tablet.snapshot` | 2026-10-05T00:08:29.270+08:00 起，2206.0 ms | 200 `image/png`（`render;dur=301.5, total;dur=319.4`） | `outputs/.../tablet.png` | 已查看：2列×3行，竖向虚线轨可见，元信息三列完整 |
| A12-req-589 | `outputs/.../desktop.snapshot` | 2026-10-05T00:08:31.487+08:00 起，2336.5 ms | 200 `image/png`（`render;dur=302.6, total;dur=330.1`） | `outputs/.../desktop.png` | 已查看：左栏 hero + 右 3列×2行，官网右对齐页脚 |
| A12-req-590 | `outputs/.../stage.snapshot` | 2026-10-05T00:08:33.836+08:00 起，2146.3 ms | 200 `image/png`（`render;dur=394.8, total;dur=779.3`） | `outputs/.../stage.png` | 已查看：6 卡单行流水线，gold 轨 + accent 轨夹住卡片行 |

### 逐轮看图发现的问题（均为实际观察，非推测）

| 轮次 | 打开的图 | 实际看到的问题 |
|---|---|---|
| v01 | mobile/tablet/desktop/stage | 主标题与副标题**完全消失**；CTA 按钮空白；序号 chip 空白 |
| v02 | mobile/tablet/desktop/stage | 主标题与副标题已出现；桌面/大屏 `云构中心 · ONLINE` 被截断成 `云构中心 ·`；卡片内虚线压住标题基线；桌面左栏出现一个只有虚线轨的空面板 |
| v03 | mobile/desktop | `云构中心 · ONLINE` 仍被截断；桌面官网与 ghost 序号没有按 RIGHT 对齐；ghost 序号"01"只显示出"0" |
| v04 | desktop | 截断问题仍在（定位为字体族与宽度模型不匹配） |
| v05 | mobile/tablet/desktop/stage | 全部字段完整、对齐正确、边距达标（定稿） |

---

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A12-v01 / syntax-fix / 无 | `400 PARSE_ERROR: Attr [color] color must be #RGB/#RGBA/#RRGGBB/#RRGGBBAA`，位置指向 `#FF7A3DFF33` | 我把已是 8 位的 `ACC_A="#FF7A3DFF"` 再拼 `"33"`，得到 10 位十六进制 | 引入 6 位基色 `ACC6="#FF7A3D"`，所有半透明色改为 `ACC6+"33"/"4D"` | v01 四张全部返回 200 | `requests.jsonl` A12-req-001/002 |
| A12-v01 / syntax-fix / 无 | `400 PARSE_ERROR: Unexpected character '\n' in input state [TAG_OPEN]`，错误片段里标签名被逐字符换行显示 | 生成器里 `kids += comp_ring(...)`，而 `comp_ring` 返回**字符串**，`+=` 把字符串逐字符摊进了列表 | `comp_ring` 改为返回 list | 解析错误消失 | A12-req-003/004；`drafts/desktop-v01.snapshot` |
| A12-v01 / syntax-fix / 无 | `400 RENDER_ERROR: renderBox.parentData must be StackParentData` | 序号 chip 与 CTA 按钮用 `Container > Positioned` 嵌文字；`Positioned` 只能是 `Stack/IndexedStack` 的直接子节点（手册第 2 节） | 两处改为 `Container > Stack(fit="EXPAND") > Positioned > Text` | 四张 200，全部出图 | A12-req-009~012 |
| A12-v01 / visual / 无 | 主标题、副标题、CTA 文字、chip 数字**完全没有渲染**，画面顶部整片空白 | `hero()` 只返回底部 y 值，调用方写成 `y = hero(...)`，**没有把 hero 生成的小部件并入 kids**；CTA/chip 文字则因为 `Positioned` 用了画布绝对坐标，被叠加了父容器偏移后落到画布外 | 1) `hero()` 改为向传入的 kids 追加并返回底部 y；2) `Rec.t` 新增 `origin` 参数，嵌套文字按**父容器相对坐标**输出，记录仍用画布坐标 | v02 四张标题、副标题、CTA、chip 全部出现 | `peek.py`（在 DSL 中 grep `Structure` 无命中，确认为生成器漏加而非服务丢弃） |
| A12-v02 / visual / 无 | 桌面与大屏 `云构中心 · ONLINE` 只显示到 `云构中心 ·`，"ONLINE" 被裁掉 | 文本框宽度按共享库 `est_width`（拉丁 0.55 em/字符）估算；`probe_fonts2.py` 实测等宽与拉丁均被低估，`probe_fonts4.py` 证明 100 px 指标不能线性外推到 20 px。框太窄 → 服务换行 → 第二行被盒高裁掉，**不报错** | 建立"每串每字号实测"表（`probe_metrics.py`，104 组），文本框宽度改用 `max(模型, 实测)×1.05`；同时给 `Rec.t` 加 `TEXT_TOO_NARROW` 断言 | v04 桌面/大屏 `云构中心 · ONLINE` 完整显示 | `probe/`、`probe4/`、`probe-metrics/`、`measured-metrics.json` |
| A12-v03 / visual / 无 | 同样的截断在桌面**仍然存在**，而手机/平板正常 | grep 定稿 DSL 发现 `地点` 那一列实际写的是 `fontFamily="DejaVu Sans Mono"`：该字体没有 CJK 字形，走回退后实际宽度与按 UI 字体算出的框宽不符 | `meta()` 按字段分别指定 `D.MONO if mono else D.UI`；并加 `FONT_MODEL_MISMATCH` 断言，防止宽度模型与实际字族再次脱节 | 桌面/大屏截断消失 | `peek.py`、`probe_site.py` |
| A12-v02 / visual / 无 | 卡片内那条强调虚线**横穿标题基线** | 虚线 y 用了 `dy - div/2 + 4`，而 `dy` 又是"标题块底部 + 偏移"，两条路径叠加后正好落在标题墨迹底部 | 虚线改为固定画在标题块下方 26 px 处（`y + head + 26`），detail 用 `dy + div`；div 由 60 收到 46 | v02 起虚线稳定位于标题与 detail 之间 | `crops/s-card1.png`（4× 放大确认压字） |
| A12-v03 / visual / 无 | 桌面页脚网址、ghost 序号"01"都没有按 `textAlign="RIGHT"` 对齐（ghost 只显示到"0"是因为框太窄而非对齐） | `Rec.t` 把 `align` 当成自己簿记用的参数吃掉，**没有转发给 `D.text_el`**，因此四张图里其实一个 `textAlign` 都没生效。`probe_textalign2.py` 证明该枚举本身是好的（LEFT/CENTER/RIGHT/START/END 均生效，JUSTIFY 等同 LEFT） | `Rec.t` 末尾显式 `align=align` 转发 | v05：CTA 文字居中、chip 数字居中、ghost 序号右对齐、桌面网址右对齐 | `crops/m-card1-ghost.png`、`peek_site.py` |
| A12-v02 / visual / 无 | 手机卡片右侧 ghost 序号与 L 形角标几乎贴死（4× 放大只剩约 1 px） | ghost 右内边距与角标内边距相同 | 手机档 ghost 额外内缩 10 px | 放大后两者间有清晰间隙 | `crops/m-card1-ghost.png` |
| A12-v02 / visual / 无 | 桌面左栏出现一个只有虚线轨的空面板，且"六个环节"在同一张图上出现两次 | 面板没有承载内容；标签重复 | 桌面改为：去掉空面板，左栏底部改成"环形纹样 + 六节点轨 + 细线 + 右对齐网址"的页脚区；"六个环节"只在卡片区上方出现一次 | 桌面左栏从 500 px 一直填到 850 px，无重复标签 | — |
| A12-v02 / syntax-fix / 无 | 平板两列之间计划中的连接虚线**没有出现** | `dsllib.dashed()` 只生成水平短矩形，竖线传进去等于画了一条零高度线段 | 新增 `comp_dashed_v()` 竖向虚线构件 | 平板中缝出现完整竖向虚线轨 | — |
| — / measurement | `probe_glyphband.py` 中 fs≤21 全部报"空白" | 探针自身画布高度写成 `fs*4.0` 而文字盒顶边固定在 y=80，fs<33 时文字整体落在画布外 | 修正探针画布高度，仅采信 fs≥30 的数据 | 得到可用的墨迹带模型（带顶 0.15 em、带高 1.15 em） | `glyph-band.json` |
| — / measurement | `probe_metrics.py` 首版把 chip 数字测成 132 px、ghost 序号测成 194 px | 探针把文字画在与文字同色的背景上（或未合成 alpha），掩膜选中了整块背景 | 探针改用中灰底 + "与背景不同即墨迹"判据，天然兼容 alpha | 104 组数据全部合理（如 `'01'`@16 = 18 px） | `probe-metrics/` |

**区分说明**：上表中"已知但本次未触发"的注意事项——`<Positioned>` 多子节点、`padding="24 32"`、`border="2 DASHED"`、`<Transform>` 缺 matrix、根布局无穷大——来自 DSL-HANDBOOK 中 A01–A05 的实测记录，本题未触发。

---

## 5. 任务耗时与资源消耗

结构化指标文件：`outputs\20261004-182918\A12\task-metrics.json`

| 指标 | 实际值 | 单位或币种 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-04T22:39:54.246+08:00 ~ 2026-10-05T00:08:35.983+08:00 | ISO8601 (+08:00) | `requests.jsonl` 首末记录 |
| 任务总耗时 | 5321.7 | 秒 | 墙钟，含本地设计/DSL 编写与全部探针 |
| 首次可用图耗时 | 约 1370 | 秒 | 从首个请求到第一张可打开的有效 PNG（A12-req-010 之后的 mobile 成功响应） |
| 等待用户反馈 | 0 | 秒 | 未请求也未收到交互反馈；视觉迭代全部由自查驱动 |
| 限流等待、排队等待 | 未发生 / 不可测 | 秒 | 590 次响应中 569 次带 `Server-Timing`，均只有 `render` 与 `total` 段，没有排队段；限流等待记 0，排队等待记未知 |
| 已记录请求耗时之和 | 967.5 | 秒 | `requests.jsonl` 全部请求耗时累加（含探针），**远小于**墙钟，不等于任务总耗时 |
| 输入、输出、总token | null | token | 服务与平台均未提供任何 token 用量接口 |
| 图像输入使用量 | null | 平台原始单位 | 平台未提供 |
| 任务费用 | null | 币种 | 平台未提供真实计费数据 |
| 其他实际可取得指标 | 服务端 `Server-Timing`：最终四张分别为 `total` 154.4 / 319.4 / 330.1 / 779.3 ms | 毫秒 | 响应头 `Server-Timing`，与客户端耗时口径不同 |
| 本地像素级校核 | 78 个内容字段、0 失败 | 个 | `verify_png.py` → `verify-png.json` |

未知的结构化数值一律 `null`，未按字符数、请求次数或账号额度做任何估算。

---

## 6. 设计选择、经验与未解决事项

### 关键设计选择

- **一套构件，四种排布**。六个环节卡在四个断点上是同一段生成代码（`step_card`）：序号 chip + 卡标题 + 卡 detail + 虚线强调 + ghost 序号 + 四角 L 形角标。变的只有网格位置（1×6 / 2×3 / 3×2 / 6×1）、字号与 ghost 序号的位置（手机垂直居中右置，其余右下）。大屏刻意用 6 列单行，把"六个环节"读成一条流水线，并在上下各夹一条六节点轨。
- **断点差异体现在版式而非缩放**。手机单列定义列表式元信息；平板 CTA 与官网同行、卡片 2×3 并加中缝竖轨；桌面改成"左栏 hero + 右侧 3×2 卡片"，主标题断成两行；大屏是分栏 hero 带 + 单行流水线。四者没有一处是同一张图缩放。
- **宽度不靠估**。先用探针把每个字符串在每个实际字号下的墨迹宽度实测出来（104 组），生成器用 `max(模型, 实测) × 1.05` 定框；交付后再用 `verify_png.py` 按精确 RGB 逐字段量交付 PNG 的实际墨迹宽度并与预期比对，把"静默截断"这种无报错失败变成可判定的硬指标（本次 78/78 通过）。
- **文字盒按墨迹带而非盒高做防重叠判定**。墨迹带由探针实测得到（盒内顶 0.15 em、高 1.15 em），比用盒高判定更贴近"实际文字盒不能重叠"的字面要求。

### 可复用的经验

1. `Positioned` 只能挂在 `Stack/IndexedStack` 下；容器内放字必须 `Container > Stack(fit="EXPAND") > Positioned > Text`。
2. `Positioned` 的坐标是**相对父 Stack** 的。嵌套时用画布绝对坐标会被叠加父容器偏移而落到画布外，表现就是"文字凭空消失"，不报错。
3. `dsllib.dashed()` 只能画水平虚线；竖虚线要自己铺短矩形。
4. 半透明色必须从 **6 位基色**拼 alpha，拼到已带 alpha 的 8 位色上会得到 10 位并报 `PARSE_ERROR`。
5. `textAlign` 枚举是大写 `LEFT/CENTER/RIGHT/START/END/JUSTIFY`；小写会报 skia `Alignment` 错误；`JUSTIFY` 实际表现为 `LEFT`。
6. 静默截断的真实机制是"框太窄 → 换行 → 第二行被盒高裁掉"，**不需要 `maxLines`** 也会发生。只看 HTTP 200 和 DSL 文本完全发现不了，必须量像素。
7. 共享库的 `est_width` 对 CJK 保守，但对 Inter 小写与 DejaVu Sans Mono **偏小 5%~15%**；而 100 px 下的指标不能线性外推到 20 px。做严肃排版前值得先跑一遍逐字号实测。
8. 生成器里 `list += "字符串"` 会把字符串逐字符摊进列表，DSL 会长得极像"标签名被换行"的解析错误。返回集合的函数一律返回 list。
9. 探针自身的画布尺寸、对照底色、掩膜判据都要先验证，否则量出来的是探针的 bug 而不是字体的度量。

### 未解决事项与如实说明

- **未遇到**：429 限流、503、认证失败、持续环境阻塞。开发期出现 1 次客户端读超时（`A12-req-033`），脚本自动重发即成功，未产生内容缺失。
- **未验证**：`maxLines` 与过小盒高的联合截断行为本次未触发（本次所有文本框高度都取 1.55×字号、宽度都宽于实测墨迹，因此不依赖该行为）；`ImageFiltered/BackdropFilter`、`gradientType`、`Transform matrix`、`<Image>` 均为本题不需要，未使用也未验证。
- **一个未解释的观察**：`probe_textalign.py` 用 `"WWWWWWWWWW"`（10 个重复 W）做对照时，服务返回的图里出现了约 19 个 W，字符数与 DSL 中的字符串不符；换用正常字符串后（`probe_textalign2.py`）行为正常。DSL 里确实只有 1 个 `Text` 节点、文本为 10 个 W。该现象仅出现在这个退化字符串上，未在本任务任何交付内容中复现，原因未确认，标记为**未确认**。
- **口径说明**：文字墨迹宽度用"与背景明显不同的像素"判定，因此在交付画布上比灰底探针少 2~3 px（两端各约 1 px 抗锯齿边缘被精确色匹配排除）。校核脚本据此设 4 px 容差——真实换行截断会丢掉整个词（几十 px），二者不会混淆。
- 临时目录中的全部草稿（`drafts/`）、探针请求与响应（`probe*/`）、失败响应（`responses/`）、度量表、裁切放大图（`crops/`）、请求日志与迭代日志均已保留，未删除任何尝试，未保存任何密钥。

### 结束依据

四张最终 PNG 均由服务真实响应产生并逐张打开查看；`content-map.json` 中 78 个内容字段全部标记 `verbatim`、`abbreviated: false`、`truncated: false`、`wrapped: false`；`verify-png.json` 复核 `all_ok = true`、四张尺寸正确、安全边距达标、墨迹带无重叠；生成器自检 0 问题。达成依据是逐条核对上表硬指标，而非渲染次数或迭代次数。