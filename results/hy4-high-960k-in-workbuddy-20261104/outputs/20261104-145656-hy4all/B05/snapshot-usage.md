# Snapshot 使用情况说明与踩坑记录 — B05

任务ID：B05
任务名称：从零构想产品并设计十个关键使用画面 · 「泊 / ANCHOR」城市暴雨安全同伴
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：10 件独立完整作品全部达成需求，逐图看图与整体最终审查通过，已知缺陷已修复
输出目录：`outputs/20261104-145656-hy4all/B05/`
临时目录：`tmp/20261104-145656-hy4all/B05/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.png` | 水位之上 · 品牌概念主视觉 1200×1200 独立完整作品 | `case-01/final.snapshot` | 完成；open-snapshot 真实响应 PNG，265081 字节，逐图 ViewImage 复查通过 |
| `case-02/final.png` | 此刻的城市 · 实时积水地图首页 760×1520 独立完整作品 | `case-02/final.snapshot` | 完成；open-snapshot 真实响应 PNG，196703 字节，逐图 ViewImage 复查通过 |
| `case-03/final.png` | 三条路，怎么走 · 出门决策卡 760×1460 独立完整作品 | `case-03/final.snapshot` | 完成；open-snapshot 真实响应 PNG，174546 字节，逐图 ViewImage 复查通过 |
| `case-04/final.png` | 前方 300 米 · 45 厘米 · 途中预警 700×1400 独立完整作品 | `case-04/final.snapshot` | 完成；open-snapshot 真实响应 PNG，112297 字节，逐图 ViewImage 复查通过 |
| `case-05/final.png` | 接单前的风险叠加 · 骑手横屏视图 1440×900 独立完整作品 | `case-05/final.snapshot` | 完成；open-snapshot 真实响应 PNG，163931 字节，逐图 ViewImage 复查通过 |
| `case-06/final.png` | 把水位告诉邻居 · 众包上报表单 800×1500 独立完整作品 | `case-06/final.snapshot` | 完成；open-snapshot 真实响应 PNG，139627 字节，逐图 ViewImage 复查通过 |
| `case-07/final.png` | 哪里能进去避一避 · 避险点列表 780×1480 独立完整作品 | `case-07/final.snapshot` | 完成；open-snapshot 真实响应 PNG，152411 字节，逐图 ViewImage 复查通过 |
| `case-08/final.png` | 梧桐里辖区监测 · 物业值班大屏 1600×1000 独立完整作品 | `case-08/final.snapshot` | 完成；open-snapshot 真实响应 PNG，176571 字节，逐图 ViewImage 复查通过 |
| `case-09/final.png` | 妈，我改走东门了 · 家庭平安屏 1200×900 独立完整作品 | `case-09/final.snapshot` | 完成；open-snapshot 真实响应 PNG，137521 字节，逐图 ViewImage 复查通过 |
| `case-10/final.png` | 这场雨，我们一起记下 · 雨后复盘 1200×1200 独立完整作品 | `case-10/final.snapshot` | 完成；open-snapshot 真实响应 PNG，179575 字节，逐图 ViewImage 复查通过 |
| `portfolio.json` | 10 件作品的元数据、完成标准与逐条检查结果 | — | 完成 |
| `portfolio.md` | 策展逻辑与逐件用途 | — | 完成 |
| `gallery.md` | 逐图 Markdown 预览、原 PNG 与对应 DSL 相对链接 | — | 完成 |
| `product-brief.md` | 用户问题、产品方案、十画面前后关系、假设与验证边界 | — | 完成 |
| `journey.json` | 结构化使用旅程、跨画面共用事实与验证边界 | — | 完成 |
| `plan.json` | 首次渲染前建立的作品计划与完成标准（位于临时目录） | — | 完成 |

B05 要求从零构想一款产品并交付至少 10 张独立完整的静态使用画面，让人理解它如何帮助真实用户；画面组合要支持可信使用过程，跨画面共用信息一致，内容具体可信，不按固定界面清单凑十页；另交付 product-brief.md 与 journey.json。本题构想「泊 / ANCHOR」——临江市众包积水安全同伴，10 张画面沿品牌认知→态势感知→路线决策→途中预警→骑手→上报→避险→物业→家庭→复盘展开，刻意采用不同画布尺寸、设备、配色与信息结构；共用同一组虚构事实并写入 journey.json。全部由 Snapshot DSL 构造，无外部素材；所有最终 PNG 为服务真实响应。

**逐图自检证据**：10 张最终 PNG 全部用 ViewImage 逐张打开：v1 全 10 张基线看图发现 6 张存在缺陷（case-01 仪表被建筑遮挡与刻度尺重叠、case-02 标签越界裁切与毛玻璃彩条压字、case-04 cm 压数字与指针标签重叠、case-07 缩略图文字挤压、case-08 柱顶数值与副标题重叠、case-10 半透明卡文字裁切），另 4 张首版即通过。v2 修复 6 张并逐张复查全部通过；case-01 又经 v3、v4 两轮把圆盘内四行文字收进仪表弧上方，最终 v4 复查确认四行文字清晰无重叠。最终整体审查：10 张 PNG 文件头均为89 50 4E 47，同名 .snapshot 完整自包含，附加文件齐全，gallery.md 逐图链接可离线访问，跨画面数值与 journey.json 一致，无已知缺陷。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | POST /snapshot 纯文本 UTF-8、image/png 响应、X-Request-Id/错误处理、/fonts | render.py、requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/ImageFiltered/渐变/边框/阴影 | 本题全部 .snapshot |
| reference/parser-text.md + media-text.md | fontFamily/fontSize/fontStyle/textAlign/letterSpacing/maxLines、CDATA、嵌套 Text 富文本、ImageFiltered 作用于子树 | 本题全部文字元素与毛玻璃浮层 |
| guides/examples.md | 固定画布 + ClipPath SVG 路径票券范式 | 本题布局骨架与环形/波浪路径 |
| A03/A09 已完成题实现 | Transform.matrix 列主序写法、ClipRRect+ImageFiltered 背景模糊 | tmp/20261104-145656-hy4all/A03、A09 |

使用 Snapshot 根节点 background + type=png；Stack + 固定尺寸 Container 画布 + Positioned 绝对定位全部元素；Container 的 color/borderRadius/border/boxShadow/gradientType(LINEAR/RADIAL/SWEEP)+gradientColors+gradientStops 构成卡片、渐变头部与光晕；ClipPath 的 SVG 路径（M/L/C/A/Z、多圆 EVEN_ODD 镂空、viewBox/fit/fillRule）实现同心水位环、仪表弧扇段、贝塞尔波浪、河道与三角形指针；Transform.matrix（列主序 16 浮点）用于能力探针的旋转验证；ClipRRect + ImageFiltered（sigmaX/sigmaY）实现毛玻璃浮层，文字置于滤镜之外保持锐利；Opacity 实现热力晕与半透明叠加；Text 的 CDATA、fontFamily/fontSize/fontStyle/textAlign/letterSpacing/maxLines 与嵌套 Text 富文本（能力探针验证）；8 位 CSS #RRGGBBAA 颜色；dashed_hline 警戒虚线、line/poly/polyline 折线与路径、ring_ticks 刻度、脚本化排序柱图与百分比计算。所有主体、图表、文字、图标均由 DSL 构造，无外部素材。

字体查询：中文统一 Noto Sans CJK SC，拉丁/数字用 Inter，等宽说明用 Noto Sans Mono CJK SC；字体清单缓存于 tmp/20261104-145656-hy4all/_suite/docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/B05/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/B05/iterations.jsonl`
渲染请求总数：27
成功次数：20
失败次数：7
重试请求数：7
DSL版本数：18
实际图片查看次数：18
完整视觉迭代数：6
未完成视觉迭代数：2
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **case-01-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-01/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-01.snapshot）` 发现：中央「45」仪表被建筑剪影遮挡，数字与地点文字破碎；左侧竖向刻度尺文字互相重叠；「泊」与副标题贴连。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-02-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-02/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-02.snapshot）` 发现：「梧桐里东门」「光谷环岛」标签超出左右边界被裁切；毛玻璃浮层亮彩条横穿三行风险文字。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-03-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-03/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-03.snapshot）` 发现：三张路线卡、三列指标、迷你路径、推荐绿描边与角标、深色结论条、蓝色按钮全部完整、对齐、可读，无缺陷。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-04-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-04/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-04.snapshot）` 发现：「cm」压在巨大数字「5」上；「当前 45cm」指针标签与地点行重叠。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-05-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-05/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-05.snapshot）` 发现：骑手横屏分栏、风险晕、荧光绿绕行路线、2/3 大数字、风险时间窗色带、结论卡、3 行订单全部完整可读，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-06-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-06/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-06.snapshot）` 发现：取景框、0–60cm 标尺、水面波浪、12cm、滑杆指针、4 个多选标签、提交按钮全部清晰，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-07-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-07/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-07.snapshot）` 发现：方位缩略图右侧「最近的 / 6 分钟 / 梧桐里社区中心」两行文本塞进过矮盒子，挤压破碎重叠。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-08-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-08/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-08.snapshot）` 发现：KPI、排序柱图、分级表、处置流水均完整可读；仅 62cm 最高柱柱顶「62 cm」与图表副标题重叠。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-09-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-09/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-09.snapshot）` 发现：暖米家庭屏、肖像、平安绿标、竖时间轴、橙色大按钮、两张家人卡全部完整可读，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-10-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B05/case-10/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B05/v1/case-10.snapshot）` 发现：4 个 KPI、100% 采纳率环、双曲线与图例清晰；右下角半透明卡「帮助了 / 1,284 人」两行文字被裁掉下半。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-01-v2**（visual，父版本 case-01-v1）：查看 `outputs/20261104-145656-hy4all/B05/case-01/final.png（2）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：重排层级：仪表最后绘制并加深色圆盘垫底；删除左侧刻度尺；拉开「泊」与副标题间距。复查：v2 复查：45 完整清晰不再被遮挡、刻度尺重叠消失、标题间距正常；但发现圆盘底部「警戒水位 30cm」被橙色仪表弧压住。
- **case-01-v3**（visual，父版本 case-01-v2）：查看 `outputs/20261104-145656-hy4all/B05/case-01/final.png（3）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：删除被弧压住的「警戒水位 30cm」。复查：v3 复查：该行消失，但「江汉路地铁 B 口」仍贴近弧带。
- **case-01-v4**（visual，父版本 case-01-v3）：查看 `outputs/20261104-145656-hy4all/B05/case-01/final.png（4）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：把圆盘内四行文字整体收进弧带上方的可用区（y≤524）。复查：v4 复查：四行文字全部清晰、不重叠、不被弧或圆盘边缘裁切；整张海报所有元素完整可读，缺陷消除。
- **case-02-v2**（visual，父版本 case-02-v1）：查看 `outputs/20261104-145656-hy4all/B05/case-02/final.png（2）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：标签 x 坐标 clamp 到画面内、标签文字改白色；毛玻璃背景彩条改为左右边缘暗色柔光，文字区保持干净。复查：v2 复查：5 个标签全部完整在画面内，浮层三行文字锐利可读，标题/按钮/导航清晰。
- **case-04-v2**（visual，父版本 case-04-v1）：查看 `outputs/20261104-145656-hy4all/B05/case-04/final.png（2）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：「cm」移到数字右侧；标尺区整体下移，指针标签改为独立单行「45cm」并上移。复查：v2 复查：45 与 cm 分离清晰，指针标签不再压地点行，标尺三段/刻度/指针/两按钮完整可读。
- **case-07-v2**（visual，父版本 case-07-v1）：查看 `outputs/20261104-145656-hy4all/B05/case-07/final.png（2）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：方位缩略图右侧文字拆成三个独立单行并下调字号、给足盒高。复查：v2 复查：三行清晰不重叠，三张卡、容量条、剩余位置与物资标签完整。
- **case-08-v2**（visual，父版本 case-08-v1）：查看 `outputs/20261104-145656-hy4all/B05/case-08/final.png（2）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：删除与柱顶冲突的副标题，单位/排序说明移到右上角，30cm 虚线旁加独立标签。复查：v2 复查：62 cm 柱顶数值清晰，右上角说明与虚线标签不重叠，柱图/表格/流水完整。
- **case-10-v2**（visual，父版本 case-10-v1）：查看 `outputs/20261104-145656-hy4all/B05/case-10/final.png（2）` 发现：上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change）。改动：半透明卡内两行文字拆成三个独立单行并各自给足高度。复查：v2 复查：「你的 3 条上报 / 帮助了 / 1,284 人」三行完整显示，其余元素全部清晰。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| case-01-v1 / baseline / — | 中央「45」仪表被建筑剪影遮挡，数字与地点文字破碎；左侧竖向刻度尺文字互相重叠；「泊」与副标题贴连。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-02-v1 / baseline / — | 「梧桐里东门」「光谷环岛」标签超出左右边界被裁切；毛玻璃浮层亮彩条横穿三行风险文字。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-03-v1 / baseline / — | 三张路线卡、三列指标、迷你路径、推荐绿描边与角标、深色结论条、蓝色按钮全部完整、对齐、可读，无缺陷。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-04-v1 / baseline / — | 「cm」压在巨大数字「5」上；「当前 45cm」指针标签与地点行重叠。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-05-v1 / baseline / — | 骑手横屏分栏、风险晕、荧光绿绕行路线、2/3 大数字、风险时间窗色带、结论卡、3 行订单全部完整可读，首版通过。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-06-v1 / baseline / — | 取景框、0–60cm 标尺、水面波浪、12cm、滑杆指针、4 个多选标签、提交按钮全部清晰，首版通过。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-07-v1 / baseline / — | 方位缩略图右侧「最近的 / 6 分钟 / 梧桐里社区中心」两行文本塞进过矮盒子，挤压破碎重叠。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-08-v1 / baseline / — | KPI、排序柱图、分级表、处置流水均完整可读；仅 62cm 最高柱柱顶「62 cm」与图表副标题重叠。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-09-v1 / baseline / — | 暖米家庭屏、肖像、平安绿标、竖时间轴、橙色大按钮、两张家人卡全部完整可读，首版通过。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-10-v1 / baseline / — | 4 个 KPI、100% 采纳率环、双曲线与图例清晰；右下角半透明卡「帮助了 / 1,284 人」两行文字被裁掉下半。 | 实际打开 v1 渲染图逐项观察；多行文本盒高、绝对定位标签边界与绘制层级估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-01-v2 / visual / case-01-v1 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 重排层级：仪表最后绘制并加深色圆盘垫底；删除左侧刻度尺；拉开「泊」与副标题间距 | v2 复查：45 完整清晰不再被遮挡、刻度尺重叠消失、标题间距正常；但发现圆盘底部「警戒水位 30cm」被橙色仪表弧压住 |
| case-01-v3 / visual / case-01-v2 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 删除被弧压住的「警戒水位 30cm」 | v3 复查：该行消失，但「江汉路地铁 B 口」仍贴近弧带 |
| case-01-v4 / visual / case-01-v3 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 把圆盘内四行文字整体收进弧带上方的可用区（y≤524） | v4 复查：四行文字全部清晰、不重叠、不被弧或圆盘边缘裁切；整张海报所有元素完整可读，缺陷消除 |
| case-02-v2 / visual / case-02-v1 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 标签 x 坐标 clamp 到画面内、标签文字改白色；毛玻璃背景彩条改为左右边缘暗色柔光，文字区保持干净 | v2 复查：5 个标签全部完整在画面内，浮层三行文字锐利可读，标题/按钮/导航清晰 |
| case-04-v2 / visual / case-04-v1 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 「cm」移到数字右侧；标尺区整体下移，指针标签改为独立单行「45cm」并上移 | v2 复查：45 与 cm 分离清晰，指针标签不再压地点行，标尺三段/刻度/指针/两按钮完整可读 |
| case-07-v2 / visual / case-07-v1 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 方位缩略图右侧文字拆成三个独立单行并下调字号、给足盒高 | v2 复查：三行清晰不重叠，三张卡、容量条、剩余位置与物资标签完整 |
| case-08-v2 / visual / case-08-v1 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 删除与柱顶冲突的副标题，单位/排序说明移到右上角，30cm 虚线旁加独立标签 | v2 复查：62 cm 柱顶数值清晰，右上角说明与虚线标签不重叠，柱图/表格/流水完整 |
| case-10-v2 / visual / case-10-v1 | 上一版本实际渲染图中记录的缺陷（见 parent 版本的 observed 与本次 change） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 半透明卡内两行文字拆成三个独立单行并各自给足高度 | v2 复查：「你的 3 条上报 / 帮助了 / 1,284 人」三行完整显示，其余元素全部清晰 |

踩坑（均来自实际渲染图观察）：① 多行文本塞进过矮盒子会被裁切/挤压——case-07 与 case-10 的两行文本必须拆成独立单行并给足高度；② 绝对定位标签未 clamp 会越出画布——case-02 两处标签被左右边界裁掉；③ 绘制顺序决定层级——case-01 中央仪表先画会被后画的城市建筑盖住，改为最后绘制并加深色圆盘垫底；④ 环形仪表弧在圆盘下半部会压住贴底文字——case-01 最终把文字收进弧带上方；⑤ ImageFiltered 作用于整个子树，A03 已验证 BackdropFilter 在本服务实例不产生可见模糊，毛玻璃须用 ClipRRect + ImageFiltered 只模糊背景副本，文字画在滤镜之外；⑥ 服务期间出现 7 次传输层失败（http_status=0），按真实响应重试后全部成功，失败响应与重试记录均保留在 tmp/20261104-145656-hy4all/B05/case-*/requests.jsonl 与 responses/。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/B05/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T17:57:00+08:00 → 2026-11-04T18:45:42+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 1470.816 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 20 / 7 / 7 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 18 / 6 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

品牌符号是「水位环」：同心圆环、刻度、水平水位线与波浪；10 张里这组词以不同形态出现（海报仪表盘、地图风险晕、预警标尺、表单滑杆、复盘采纳率环），语义一致而画面各异。配色按媒介切换：深蓝海报 / 深绿蓝地图 / 浅灰蓝决策 / 橙红预警 / 黄黑骑手 / 米白表单 / 青绿列表 / 深海军蓝驾驶舱 / 暖米家庭屏 / 白青数据海报，避免整套趋同。信息结构上分别用海报、沉浸式地图、卡片对比、单一大数字、横屏分栏、表单、状态列表、密集 dashboard、人物状态卡与数据海报组织，确保 10 件不是同一模板换文字。

最终 10 张实际图片已逐张打开检查（含多轮视觉迭代复查）：内容、数据、几何、层级、对齐、可读性与裁切均满足题面要求；10 件作品独立完整且共用信息自洽；据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
