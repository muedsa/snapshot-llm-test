# Snapshot 使用情况说明与踩坑记录

任务ID：A12
任务名称：Responsive System（响应式系统：同一内容在四个断点画布上的重排）
本次运行ID：run-20261002-220723-mimo
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：outputs\run-20261002-220723-mimo\A12
临时目录：tmp\run-20261002-220723-mimo\A12

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| mobile.snapshot | 完整可复现DSL（360×800） | mobile.png | 已交付，与 mobile-v3.snapshot SHA256 一致 |
| mobile.png | 服务返回的最终图片 360×800，72 662 B | mobile.snapshot | 已交付，原始服务字节，未后处理 |
| tablet.snapshot | 完整可复现DSL（768×1024） | tablet.png | 已交付，与 tablet-v3.snapshot SHA256 一致 |
| tablet.png | 服务返回的最终图片 768×1024，97 139 B | tablet.snapshot | 已交付，原始服务字节，未后处理 |
| desktop.snapshot | 完整可复现DSL（1440×900） | desktop.png | 已交付，与 desktop-v3.snapshot SHA256 一致 |
| desktop.png | 服务返回的最终图片 1440×900，120 059 B | desktop.snapshot | 已交付，原始服务字节，未后处理 |
| stage.snapshot | 完整可复现DSL（1920×1080） | stage.png | 已交付，与 stage-v3.snapshot SHA256 一致 |
| stage.png | 服务返回的最终图片 1920×1080，134 024 B | stage.snapshot | 已交付，原始服务字节，未后处理 |
| design-tokens.json | 四断点令牌表（栅格、字号、边距、间距、配色、组件） | gen.ps1 的单一令牌源 | 已交付 |
| content-map.json | 25 个输入字段在四张画布上的逐字段坐标区域与保留状态 | gen.ps1 写出 | 已交付 |
| responsive-audit.json | 92 项几何/内容/像素核对结果（92 PASS / 0 FAIL） | verify.ps1 对四图四DSL | 已交付 |
| snapshot-usage.md | 本报告 | — | 已交付 |
| task-metrics.json | 结构化指标 | — | 已交付 |

### 需求完成情况

- **四张画布尺寸**：360×800 / 768×1024 / 1440×900 / 1920×1080，四张 PNG 的 IHDR 由 `verify.ps1` P 组逐张读取校验，全部一致（P-4/4 PASS）。
- **每个 PNG 同名 .snapshot**：四对均已交付，交付副本与临时目录中实际被渲染的那一版逐字节 SHA256 相同。
- **输入字段全部保留、不缩写**：`inputs/content.json` 共 25 个字段（title、subtitle、date、time、location、cta、website + 6 张卡片 × id/title/detail）。C 组 4 张画布各核对 25/25，字段必须出现在该画布 DSL 的 CDATA 载荷内且不存在 `&lt;`/`&amp;` 等实体编码（C-4/4 PASS）。移动端标题因宽度被拆成两行 `Structure /` 与 `Vision`，核对方式是把两行按 `line1 + " " + line2` 重组后与原串逐一字符比较。
- **CTA 为纯文本**：`免费参加 · 扫码方式详见官网`，未放置二维码；`location` 等输入未被改动。
- **无 Image 标签、无 transform/scale**：N 组扫描 `<Image`、`transform=`、`scale=`、`rotate=`、`backgroundImage`、`clipPath` 六种 token，四份 DSL 全部为 clean（N-4/4 PASS）。所有断点差异都是**重新排版**得到的，不是裁剪或缩放得到的。
- **字号下限**：T 组 12 项全过——手机正文 ≥16、卡标题 ≥18，其余正文 ≥20、主标题 ≥40。min 实测：mobile 正文 16 / 卡标题 18 / 主标题 40；tablet 20 / 24 / 56；desktop 20 / 30 / 72；stage 24 / 34 / 88。
- **安全边距**：mobile 16、tablet 32、desktop 48、stage 56，均 ≥ 要求（L-4/4 PASS）；并且**实际墨迹包围盒**落在安全区内（M-4/4 PASS）。
- **无重叠文字**：O 组对每张画布内全部文本框做两两求交，0 重叠（O-4/4 PASS）；同时所有文本框在安全区内（B-4/4 PASS），标题不压右上角方块阵列（V-4/4 PASS），每张卡片的 index/title/detail 框都在自己的卡片矩形内（R-24/24 PASS）。
- **统一的色彩、形态与层级**：四张画布共用同一套核心装饰组件（accent-rule、2×2 方块阵列、hairline、meta-chip、card-tile + 左侧 4px 青色竖条、cta-pill、site-line）与同一配色，仅按断点**改变排列与尺寸**：手机 1×6 单列（chip 竖排、标题两行、index 与标题同行）、平板 2×3、桌面 3×2、舞台 6×1（index 移到标题上方单独一行）。
- **章节间隙与溢出**：G 组 12 项证明三个章节间隙（header→meta→cards→footer）内 0 墨迹；W 组 4 项证明位置 chip 下方 0 墨迹（这条正是用来抓 chip 换行溢出的）。
- **content-map.json**：每个输入字段在四张画布上都有 `boxes`（x/y/width/height/text）与 `retained: true`，坐标由 `gen.ps1` 在发射时写出，而不是事后量得。

未满足的要求：无。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com （`run-config.json` 覆盖子题默认值）
文档版本或访问日期：共享准备阶段取得的真实响应 `shared-doc-0001`（GET https://open-snapshot.muedsa.com/ai-guide.md，200，1400 ms）、`shared-doc-0002`（GET https://snapshot.muedsa.com/，200，900 ms）、`shared-doc-0003`（GET /reference/parser-tags/，200，1100 ms）、`shared-fonts-0001`（GET /fonts，200，1407 ms）。这四行在共享日志 `tmp/.../_suite/requests.jsonl` 中的 `started_utc`/`ended_utc` 均为 **null**（共享准备当时未记录时钟），因此本题不填写具体访问时刻——这是真实的留痕缺口，不作推测。A12 自身新增文档请求 0 次、字体请求 0 次。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

本次的实际应用（不是只贴链接）：请求体是 UTF-8 纯文本 DSL、`Content-Type: text/plain; charset=utf-8`、响应为 `image/png`；错误时先看状态码与响应体再判断是语法错误还是服务限流；字体必须先查 `/fonts` 才能写 `fontFamily`；429/503 按 `Retry-After` 重试（本题 12 次请求全部 200，未触发重试）。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求格式、响应检查、错误处理、字体查询流程 | `tmp/.../_suite/render.ps1`（POST + JSONL 留痕 + 429/503 重试） |
| https://snapshot.muedsa.com/ DSL 文档 | `Snapshot` / `Container` / `Stack` / `Positioned` / `Text` / `Raw` 语义，`borderRadius` 圆角，`height="1.0"` 行盒 | 四份 `*.snapshot` |
| GET /fonts（真实响应 448 B / 27 个字体族，本题 0 新请求，直接读既有文件） | 可用 `fontFamily` 列表、禁止逗号后空格 | `tmp/.../A11/fonts-0001.txt`，`verify.ps1` F 组 4 项 |

**字体**：本题 **0 次新增 HTTP 请求**。同一次运行中 `/fonts` 真实取得过两回，二者字节完全相同（SHA256 `CFA8A284DD8FE8E93167FDB9C8F1B10591571E5A9AE09538942DFC4B7E368569`，448 B，27 个字体族，已实测比对）：

- `shared-fonts-0001`（共享准备，GET /fonts，200，1407 ms）→ `$env:USERPROFILE\AppData\Local\Temp\fonts.txt`
- `A11-fonts-0001`（上一题自己发的，GET /fonts，200，1692 ms，2026-10-03T13:30:29+08:00）→ `tmp/run-20261002-220723-mimo/A11/fonts-0001.txt`

`verify.ps1` 的 F 组实际读取的是 `tmp/.../A11/fonts-0001.txt`，把它当作本题的字体真源。最终选用 `Noto Sans CJK SC` / `Noto Sans CJK JP`（正文与标题）与 `Noto Sans Mono CJK SC`（卡片序号 C1–C6、日期时间、URL）。F 组 4 项把每份 DSL 里出现的 `fontFamily` 逐个（按逗号拆开、trim 后）与该真实响应比对，全部命中，且检查了逗号后不能有空格（服务对该写法不兼容）。

**本题实际用到的 DSL 能力**：绝对定位 `Positioned`（left/top/width/height）+ `Text`（fontFamily/fontSize/color/textAlign/fontStyle/height）+ `Raw` CDATA 文本 + `Container`（color、borderRadius 圆角、borderWidth/borderColor 描边）+ `Stack` 装载。没有使用 Image、裁剪、变换、滤镜——这是本题的硬约束，不是没查到。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp\run-20261002-220723-mimo\A12\requests.jsonl
迭代记录文件：tmp\run-20261002-220723-mimo\A12\iterations.jsonl
渲染请求总数：12
成功次数：12
失败次数：0
重试请求数：0
DSL版本数：3
实际图片查看次数：8（v1 四张 + v3 四张）
完整视觉迭代数：1（L1：查看 v1 四图 → 修改 → 渲染 → 查看 v3 四图并比较）
未完成视觉迭代数：1（v2 四张已渲染但未开图，先被像素/几何核对（90/92）检查，随后被 v3 取代；已在 iterations.jsonl 中如实标注）
其他接口查询：本题 0 次新增；`/fonts` 复用共享准备阶段的既有真实响应（0 新请求）。

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A12-render-v1-mobile | tmp/.../A12/mobile-v1.snapshot | 2026-10-03T15:09:44+08:00 → 15:09:49+08:00，5338.9 ms | 200 image/png | tmp/.../A12/render-v1-mobile.png | 已查看（上限 15:20:45+08:00）：6 行单列，序号 13 px 偏小、日期时间 `2026.11.07·09:00–16:00` 无间隔 |
| A12-render-v1-tablet | tablet-v1.snapshot | 2026-10-03T15:09:49+08:00 → 15:09:51+08:00，2009.2 ms | 200 image/png | render-v1-tablet.png | 已查看：**位置 chip 溢出**，`云构中心 · ONLINE` 第二行掉到胶囊外 |
| A12-render-v1-desktop | desktop-v1.snapshot | 2026-10-03T15:09:51+08:00 → 15:09:55+08:00，3088.6 ms | 200 image/png | render-v1-desktop.png | 已查看：3×2 栅格，无可见缺陷 |
| A12-render-v1-stage | stage-v1.snapshot | 2026-10-03T15:09:55+08:00 → 15:09:58+08:00，2907 ms | 200 image/png | render-v1-stage.png | 已查看：6×1 单行，index 上置，无可见缺陷 |
| A12-render-v2-mobile | mobile-v2.snapshot | 2026-10-03T15:20:45+08:00 → 15:20:49+08:00，3585.8 ms | 200 image/png | render-v2-mobile.png | **未开图**（verify.ps1 数值核对 90/92 后被 v3 取代） |
| A12-render-v2-tablet | tablet-v2.snapshot | 2026-10-03T15:20:49+08:00 → 15:20:52+08:00，2938.8 ms | 200 image/png | render-v2-tablet.png | 未开图；W-tablet 像素带核对 0 墨迹已证明 chip 溢出被修掉 |
| A12-render-v2-desktop | desktop-v2.snapshot | 2026-10-03T15:20:52+08:00 → 15:20:55+08:00，2638.7 ms | 200 image/png | render-v2-desktop.png | 未开图 |
| A12-render-v2-stage | stage-v2.snapshot | 2026-10-03T15:20:55+08:00 → 15:20:58+08:00，2233.8 ms | 200 image/png | render-v2-stage.png | 未开图 |
| A12-render-v3-mobile | mobile-v3.snapshot | 2026-10-03T15:31:47+08:00 → 15:31:50+08:00，2639.9 ms | 200 image/png | render-v3-mobile.png | 已查看（终图）：通过 |
| A12-render-v3-tablet | tablet-v3.snapshot | 2026-10-03T15:31:50+08:00 → 15:31:53+08:00，2593.1 ms | 200 image/png | render-v3-tablet.png | 已查看（终图）：位置 chip 单行不溢出，通过 |
| A12-render-v3-desktop | desktop-v3.snapshot | 2026-10-03T15:31:53+08:00 → 15:31:57+08:00，4709.8 ms | 200 image/png | render-v3-desktop.png | 已查看（终图）：通过 |
| A12-render-v3-stage | stage-v3.snapshot | 2026-10-03T15:31:57+08:00 → 15:31:59+08:00，3274.8 ms | 200 image/png | render-v3-stage.png | 已查看（终图）：通过 |

请求耗时之和 37.9584 s（12 次，全部 200），来自 `requests.jsonl` 的 `duration_ms`。

**看图证据说明**：四张终图（v3）全部用视觉工具按路径逐张打开。查看时发现桌面/舞台两张横向图被查看器**以相反顺序呈现**，因此用像素行扫描确定文件与内容的对应关系：`render-v3-desktop.png`（1440×900）在 y=450 处恰有 3 个卡片底色（#132038）连续段，`render-v3-stage.png`（1920×1080）在 y=600 处恰有 6 个——与 design/content-map 中的栅格一致，四个文件本身没有错位，两套栅格内容也都已实际看过。

**看图发现并记录的真实问题**：
1. v1 平板位置 chip 换行溢出（见上表）——已修复，v3 通过肉眼与 W 组像素带双重确认。
2. v1 手机日期时间分隔符无间隔，读成一串——已修复（v2 起为 `2026.11.07 · 09:00–16:00`，直接比对 v1/v2/v3 三份 DSL 的 CDATA 确认）。
3. v3 四张图未再发现文字、遮挡、裁剪或层级问题，因此没有为了"凑迭代"而制造改动。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| v1 / baseline / — | 首版四图可用，但平板 chip 溢出、手机分隔符黏连 | 图片查看（肉眼直接可见） | 见下两行 | — | mobile/tablet/desktop/stage-v1.snapshot，render-v1-*.png |
| v1→v2 / 视觉 / v1 | 平板三等分 chip 导致位置 chip 仅 192 px，`云构中心 · ONLINE` 第二行掉出胶囊 | 肉眼查看 + 用 `EstTextW` 反推文字宽度约 200 px | chip 宽度按各自文案估算宽度（EstTextW×1.08 + 2×pad）计算，并加 chip 行总宽 `AssertFit` 守卫；新增单行守卫，任何单行元素会折行就直接抛错 | v2/v3 平板 W 组像素带 0 墨迹；v3 肉眼确认单行不溢出 | tablet-v1/v2/v3.snapshot，render-v1/v3-tablet.png |
| v1→v2 / 视觉 / v1 | 手机日期时间 `2026.11.07·09:00–16:00` 无间隔 | 肉眼查看 + 三版 DSL CDATA 逐版比对 | 分隔符两侧加空格 | v1 无空格、v2/v3 有空格（已实测确认） | mobile-v1/v2/v3.snapshot |
| v1→v2 / 视觉（补齐） / v1 | 手机网址下行会贴边 | 推断性风险，用 `ceil(0.3 × siteSize)` 预留下降部空间消除 | website 行下预留 ink pad | M 组手机墨迹包围盒落在安全区内 | mobile-v*.snapshot |
| v2→v3 / 备选参数（checker） / v2 | `verify.ps1` T1 两次失败：手机最小正文字号 13（卡片序号），平板 16，低于 16/20 下限 | 数值核对给出的实测最小值，不是肉眼问题 | 卡片序号字号 mobile 13→16、tablet 16→20（desktop 已 20、stage 已 24） | v3 由 90/92 → **92/92 PASS**；序号仍明显小于卡标题，层级未变 | gen.ps1 字号表，mobile/tablet-v3.snapshot |

**本题遇到并已确认的踩坑（踩在脚本侧，不是服务侧）**：
- **PowerShell 变量大小写不敏感**：`verify.ps1` 初版里 `$M`（边距）被正则循环变量 `$m` 覆盖、`$MAP` 被局部 `$map` 覆盖、`$W/$H` 被 IHDR 解析出的 `$w/$h` 覆盖、`$EXPECT` 被 `$exp` 覆盖、`$SEG` 被 `$segs` 覆盖，直接把核对结果打成一堆假失败/假通过。重写时给每个名字做了**大小写意义上的唯一化**（`$margin`/`$cm`/`$cvsW`/`$EXP`/`$SEGS`…），并在文件头注释里点明。
- **`ConvertFrom-Json` 的数组不展开**：`@(ReadAllLines(...) -join "`n" | ConvertFrom-Json)` 得到的是"含 1 个数组元素"的数组，`foreach` 拿到的 `$sg` 是整个数组，`$sg.bp` 走成员枚举拼成一个巨串，最终报 `Collection was of a fixed size`。改为 `ReadAllText(... ) | ConvertFrom-Json` 后正常。
- **PSCustomObject 不能用字符串下标**：`$f.canvases[$bp]` 返回 null，要用动态成员访问 `$f.canvases.$bp`。
- **`System.Drawing` 需要显式加载**：脚本里 `Add-Type -AssemblyName System.Drawing` 必须写，否则 `New-Object System.Drawing.Bitmap` 报 TypeNotFound。
- **字体列表逗号后不能有空格**（服务端不接受），F 组检查已把这一条固化成断言。

**服务侧问题**：未发生。12 次渲染全部 200，0 失败 0 重试，没有出现 429/503，也没有解析错误（三版 DSL 解析错误 0）。

**从文档了解到、但本次未触发的注意事项**：`Stack` 默认 `clipBehavior="HARD_EDGE"` 会裁掉越界内容——本题因"不裁剪、靠重排"的约束，反而把它当成了溢出检测器的反面参照（若 chip 文本掉出容器，肉眼与像素带检查都会立刻暴露）；HTML 实体不解码，因此所有文本一律走 `Raw` + CDATA。

## 5. 任务耗时与资源消耗

结构化指标文件：outputs\run-20261002-220723-mimo\A12\task-metrics.json

| 指标 | 实际值 | 单位或币种 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-03T14:49:37+08:00 | 含时区 | `tmp/.../_suite/events.jsonl` seq 22（A12 task_started） |
| 任务结束时间 | 2026-10-03T15:44:21+08:00 | 含时区 | 交付本报告与 task-metrics.json 时的本机时钟 |
| 任务总耗时（墙钟） | 3284.1 | 秒 | 自开始到交付的墙钟，**不等于**请求耗时之和 |
| 首次可用图耗时 | 1212.4 | 秒 | 到 v1 手机图渲染响应完成（15:09:49+08:00） |
| 等待用户反馈 | 0 | 秒 | 本题为单题自动执行，未发生 |
| 限流等待 | 0 | 秒 | 12 次请求均一次成功，未触发 429/503 |
| 排队等待 | null | 秒 | 服务端未返回可测排队时长，按约定记 null |
| 已记录请求耗时之和 | 37.9584 | 秒 | `requests.jsonl` 12 行 `duration_ms` 求和（v1 13.3437 + v2 11.3971 + v3 13.2176）；与 Server-Timing 同源，不与墙钟相加 |
| 服务端 Server-Timing | 12/12 行有值 | ms | 响应头 `Server-Timing: render;dur=…, total;dur=…` |
| 输入、输出、总 token | null | token | 平台未在本运行中提供 token 计量，不以字符数估算 |
| 图像输入使用量 | null | 平台原始单位 | 同上，无重复相加问题 |
| 任务费用 | null | — | 平台未提供计费数据 |
| 其他实际可取得指标 | 渲染响应字节 1 269 076；终图 4 张共 423 884 B（终 DSL 4 份共 33 645 B） | 字节 | `requests.jsonl` 的 `bytes` 字段 / 交付文件大小（SHA256 已逐个与 task-metrics.json 比对一致） |

未知项原因说明：token、图像输入与费用三项在本次运行的可得数据源中均未出现，按约定记 `null` 并在此说明，不用账号剩余额度或文本长度反推。

## 6. 设计选择、经验与未解决事项

**关键设计选择**
1. **一份内容 + 一份令牌 → 四份 DSL**：`gen.ps1 -Ver N` 是唯一真源，四张画布不是手写的四份稿子。这样"同一核心组件、只改排列"才可证——design-tokens.json 里四个断点共享同一套 color/component 定义，只有栅格、字号、边距、间距是分断点的。
2. **分区布局 + 差额吸收**：页面分 header / meta / cards / footer 四段，剩余高度按 1 : gapWeight2 : 1 的权重灌进三个段间空隙（手机 18/28/17、平板 51/61/51、桌面 52/62/51、舞台 90/117/90），使 `bottom_slack` 恰好等于网址行的下降部预留——边距是**构造出来**的，不是事后量出来的。
3. **把断点差异表达为"重排"而非"缩放"**：手机把 meta chip 竖排、标题拆两行；舞台把 index 从标题行移到标题上方。这既满足"无 transform/scale/Image"的硬约束，也让 6×1 这种极端栅格仍然可读。
4. **守卫先于渲染**：`EstTextW` ×1.08 估算 + `AssertFit` 在生成阶段就抛错，把"渲染出来才发现换行"提前成"生成时就失败"。v1 的 chip 溢出正是缺这层守卫的代价。
5. **核对脚本独立于生成脚本**：`verify.ps1` 只读交付物（DSL + PNG + content-map + segments），不回写，92 项分组 P/N/C/F/T/L/M/B/O/V/R/G/W，最终 92/92。

**预览如何影响了选择**：v1 平板图是唯一一次"必须看图才能发现"的问题——chip 宽度的算术在纸面上是对的（三等分），但没有考虑文字本身需要 200 px。看到图之后，方案从"均分"改成"按内容分配"，并顺手加了单行守卫，把这一类问题从"看图发现"变成"生成时发现"。

**可复用经验**
- 断点系统里，**宽度预算表**（每个单行元素的估算宽度必须 ≤ 可用宽度）比像素复查更省事；像素检查留作最后一道闸。
- 核对脚本要从生成脚本里独立出来，并且脚本内所有变量名做到**大小写唯一**，否则 PowerShell 会静默地把核对结果改写。
- 四图/多图任务里，肉眼"看起来对"和文件名对不对是两件事，最好用像素行扫描再钉一次文件↔内容的对应关系（本题 desktop/stage 确实被查看器颠倒呈现过）。

**未解决事项 / 未经验证的要求**
- 排队等待时长服务端未提供，指标中记 `null`，未做估计。
- v2 四张图未用视觉工具打开（已在 iterations.jsonl 标注为未完成迭代）；其结论由像素与几何核对支撑，若需要完全对齐"每个版本都开图"的口径，可直接查看 `tmp/.../A12/render-v2-*.png`，文件均未删除。
- 极端更小的视口（如 320 px 宽）不在本题输入范围内，未做验证。

**结束依据**：四张终图全部真实渲染、全部开图查看并通过；92/92 结构化核对全过；25 个输入字段在四张画布上逐字保留；无 Image/transform/scale；字号、边距、无重叠、无溢出均有机检与目视双重证据。达到迭代次数不是完成依据——本题在**最后一次查看没有再发现可改的缺陷**时才收工。

**留痕保留**：`tmp/.../A12/` 中保留 v1/v2/v3 三版 DSL、12 张渲染响应 PNG、gen.ps1、verify.ps1、requests.jsonl、iterations.jsonl、segments-v1/v2/v3.json、design-tokens/content-map 三版；无失败响应文件（0 次失败）；未删除或覆盖任何旧版本；未保存任何密钥。
