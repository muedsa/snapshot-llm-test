# Snapshot 使用情况说明与踩坑记录 — B06

任务ID：B06
任务名称：把十个日常信息难题变成惊艳而好用的作品
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：10 件独立完整作品全部达成需求，逐图看图与整体最终审查通过，已知缺陷已修复
输出目录：`outputs/20261104-145656-hy4all/B06/`
临时目录：`tmp/20261104-145656-hy4all/B06/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.png` | 一眼服药 · 24 小时服药环 1100×1100 独立完整作品 | `case-01/final.snapshot` | 完成；open-snapshot 真实响应 PNG，146625 字节，逐图 ViewImage 复查通过 |
| `case-02/final.png` | 同价尺 · 每 100g 统一标尺 1200×900 独立完整作品 | `case-02/final.snapshot` | 完成；open-snapshot 真实响应 PNG，139330 字节，逐图 ViewImage 复查通过 |
| `case-03/final.png` | 峰谷光带 · 24 小时用电账单 1400×900 独立完整作品 | `case-03/final.snapshot` | 完成；open-snapshot 真实响应 PNG，160970 字节，逐图 ViewImage 复查通过 |
| `case-04/final.png` | 三环限额 · 一包零食占多少 1000×1200 独立完整作品 | `case-04/final.snapshot` | 完成；open-snapshot 真实响应 PNG，123997 字节，逐图 ViewImage 复查通过 |
| `case-05/final.png` | 一条轨 · 把 8 条时间戳压成一条线 900×1400 独立完整作品 | `case-05/final.snapshot` | 完成；open-snapshot 真实响应 PNG，128142 字节，逐图 ViewImage 复查通过 |
| `case-06/final.png` | 末班钟 · 还能赶上哪班 1100×1100 独立完整作品 | `case-06/final.snapshot` | 完成；open-snapshot 真实响应 PNG，158451 字节，逐图 ViewImage 复查通过 |
| `case-07/final.png` | 四色树 · 垃圾分类决策树 1300×1000 独立完整作品 | `case-07/final.snapshot` | 完成；open-snapshot 真实响应 PNG，131379 字节，逐图 ViewImage 复查通过 |
| `case-08/final.png` | 穿衣带 · 一周天气决策列 1400×900 独立完整作品 | `case-08/final.snapshot` | 完成；open-snapshot 真实响应 PNG，103788 字节，逐图 ViewImage 复查通过 |
| `case-09/final.png` | 停车格 · 找车与计费一张卡 1100×1200 独立完整作品 | `case-09/final.snapshot` | 完成；open-snapshot 真实响应 PNG，179529 字节，逐图 ViewImage 复查通过 |
| `case-10/final.png` | 登机条 · 一眼看清 B27 1400×800 独立完整作品 | `case-10/final.snapshot` | 完成；open-snapshot 真实响应 PNG，126086 字节，逐图 ViewImage 复查通过 |
| `portfolio.json` | 10 件作品的元数据、完成标准与逐条检查结果 | — | 完成 |
| `portfolio.md` | 策展逻辑与逐件用途 | — | 完成 |
| `gallery.md` | 逐图 Markdown 预览、原 PNG 与对应 DSL 相对链接 | — | 完成 |
| `problem-evidence.json` | 每个问题的来源/假设、场景要求、重构选择与可观察/未验证效果区分 | — | 完成 |
| `design-review.md` | 逐件设计复核与整体最终审查 | — | 完成 |
| `plan.json` | 首次渲染前建立的作品计划与完成标准（位于临时目录） | — | 完成 |

B06 要求自主观察现实生活中信息难理解、难比较、难找到或难采取行动的场景，选择至少 10 个值得重新设计的问题，用 Snapshot 制作 10 件完整作品；每件说清用户原本卡在哪里、新作品如何让信息更容易被理解/使用，大胆重构信息同时保证关键内容完整、准确、能读，另交付 problem-evidence.json 与 design-review.md。本题选择服药、超市比价、电费峰谷、营养成分、快递轨迹、末班车、垃圾分类、一周天气、停车找车与计费、航班登机 10 个不同难题，分别用极坐标环、排序标尺、时间色带、同心仪表、垂直单轨、放射扇区、决策树、列网格、分区网格+阶梯、超大数字时间轴组织信息。全部数值为脚本计算的自拟演示数据并明确标注虚构，未做真实用户实验。全部由 Snapshot DSL 构造，无外部素材；所有最终 PNG 为服务真实响应。

**逐图自检证据**：10 张最终 PNG 全部用 ViewImage 逐张打开：v1 全 10 张基线看图发现 4 张存在缺陷（case-01「12」刻度被底部条遮挡、case-02 单价数值压在色条上且结论口径不一致、case-06 底部说明中英混杂、case-07 根节点文字贴边与连线交叉），另 6 张首版即通过。v2 修复 4 张并逐张复查全部通过。渲染期间服务多次出现传输层/SSL 握手超时：v1 初渲 case-02 三次尝试失败、v2 重渲染 case-01/02 也曾失败，均按真实响应保留失败记录并重试补渲成功；所有 10 张最终 PNG 均为 200/image-png 成功响应。最终整体审查：10 张 PNG 文件头均为 89 50 4E 47，同名 .snapshot 完整自包含，附加文件齐全，gallery.md 逐图链接可离线访问，画面数值与 problem-evidence.json 一致，无已知缺陷。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | POST /snapshot 纯文本 UTF-8、image/png 响应、X-Request-Id/错误处理、/fonts | render.py、requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/ImageFiltered/渐变/边框/阴影 | 本题全部 .snapshot |
| reference/parser-text.md + media-text.md | fontFamily/fontSize/fontStyle/textAlign/letterSpacing/maxLines、CDATA、嵌套 Text 富文本、ImageFiltered 作用于子树 | 本题全部文字元素与能力探针 |
| guides/examples.md | 固定画布 + ClipPath SVG 路径票券范式 | 本题布局骨架与环形/扇区路径 |
| A03/A09 已完成题实现 + 能力探针 | Transform.matrix 列主序、ClipRRect+ImageFiltered、SWEEP/RADIAL 渐变、A 弧扇段真实生效 | tmp/20261104-145656-hy4all/_suite/probe/ |

使用 Snapshot 根节点 background + type=png；Stack + 固定尺寸 Container 画布 + Positioned 绝对定位；Container 的 color/borderRadius/border/boxShadow/gradientType(LINEAR/RADIAL/SWEEP)+gradientColors 构成卡片、渐变头部、光晕与7 列温度色带；ClipPath 的 SVG 路径（M/L/H/V/C/A/Z、多圆 EVEN_ODD 镂空、viewBox/fit/fillRule）实现同心环、仪表弧扇段、服药窗口弧、贝塞尔决策树连线、放射扇区与三角形指针；X.curve/X.polyline 采样三次贝塞尔与折线；ClipRRect + ImageFiltered（能力探针验证）、Opacity 半透明叠加、8 位 CSS #RRGGBBAA 颜色；Text 的 CDATA、fontFamily/fontSize/fontStyle/textAlign/letterSpacing/maxLines 与嵌套 Text 富文本；脚本化单价排序、百分比、时长计费、24 格色带与 7 列几何计算。所有主体、图表、文字、图标均由 DSL 构造，无外部素材。

字体查询：中文统一 Noto Sans CJK SC，拉丁/数字用 Inter，等宽说明用 Noto Sans Mono CJK SC；字体清单缓存于 tmp/20261104-145656-hy4all/_suite/docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/B06/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/B06/iterations.jsonl`
渲染请求总数：26
成功次数：14
失败次数：12
重试请求数：9
DSL版本数：14
实际图片查看次数：14
完整视觉迭代数：4
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **case-01-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-01/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-01.snapshot）` 发现：24 小时环形服药时钟只显示 00/06/18，正下方「12」被底部注意事项条遮挡；其余元素完整清晰。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-02-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-02/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-02.snapshot）` 发现：5 行单价数值压在条形末端（¥4.70/100g 被切割难读）；底部「按每周买 3 袋算」文案与脚本 ×20 估算口径不一致。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-03-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-03/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-03.snapshot）` 发现：24 格用电色带、时间刻度、61% 占比环、三条建议卡与底部结论条全部完整可读，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-04-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-04/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-04.snapshot）` 发现：三层同心环比例正确、中心「钠偏高」判定与三行数值完整对齐，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-05-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-05/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-05.snapshot）` 发现：ETA 横幅、5 阶段单轨、当前高亮卡与结论卡完整可读，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-06-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-06/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-06.snapshot）` 发现：四个放射扇区、圆心与标签卡完整；唯一缺陷是底部说明中英混杂「自己 subtract 出等待时间」。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-07-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-07/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-07.snapshot）` 发现：根节点圆偏小使文字贴边；「三个都不是」长贝塞尔曲线横跨到最右灰桶并与另三条连线交叉。。改动：生成 v1 首版基线并逐张实际查看。复查：确认存在缺陷，进入视觉迭代。
- **case-08-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-08/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-08.snapshot）` 发现：7 列温度色带、降水条、决策 chip、周降雨色带与结论全部完整对齐，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-09-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-09/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-09.snapshot）` 发现：三区网格与 07 高亮、记忆卡、三段计费、¥18 大数字完整可读，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-10-v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/B06/case-10/final.png（v1 基线；DSL 备份 tmp/20261104-145656-hy4all/B06/v1/case-10.snapshot）` 发现：巨大 B27、水平时间轴、右侧面板、荧光绿两行结论与底部信息完整清晰，首版通过。。改动：生成 v1 首版基线并逐张实际查看。复查：首版即通过，未修改。
- **case-01-v2**（visual，父版本 case-01-v1）：查看 `outputs/20261104-145656-hy4all/B06/case-01/final.png（2）` 发现：v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed）。改动：环形与圆心整体上移（CY 600→555），让「12」刻度落在底部注意事项条上方。复查：v2 复查：00/06/12/18 四刻度齐全，三个服药弧段、中央 3、三张卡、胶囊与注意事项条全部完整清晰。
- **case-02-v2**（visual，父版本 case-02-v1）：查看 `outputs/20261104-145656-hy4all/B06/case-02/final.png（2）` 发现：v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed）。改动：条形收窄到独立绘图区、单价数值移到右侧专属列、「最划算」角标右移；结论文案改为与脚本计算一致的「按每月 20 份的单价差累计估算」。复查：v2 复查：5 个单价数值全部在条形外完整可读，金色高亮行与角标分离，排序正确，底部结论与 ¥16.50 清晰。
- **case-06-v2**（visual，父版本 case-06-v1）：查看 `outputs/20261104-145656-hy4all/B06/case-06/final.png（2）` 发现：v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed）。改动：底部说明「自己 subtract 出等待时间」改为通顺中文「自己算出等待时间」。复查：v2 复查：底部文案通顺完整，四扇区、圆心与四张标签卡仍完整无重叠。
- **case-07-v2**（visual，父版本 case-07-v1）：查看 `outputs/20261104-145656-hy4all/B06/case-07/final.png（2）` 发现：v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed）。改动：根节点圆半径 68→82 并缩小字号；删除交叉长曲线，灰桶改用「三个都不是 → 这里」局部标注 + 短竖线。复查：v2 复查：根节点文字完整落在圆内，三条问题→桶连线各自独立不交叉，四色桶与 6 个速查色块完整。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| case-01-v1 / baseline / — | 24 小时环形服药时钟只显示 00/06/18，正下方「12」被底部注意事项条遮挡；其余元素完整清晰。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-02-v1 / baseline / — | 5 行单价数值压在条形末端（¥4.70/100g 被切割难读）；底部「按每周买 3 袋算」文案与脚本 ×20 估算口径不一致。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-03-v1 / baseline / — | 24 格用电色带、时间刻度、61% 占比环、三条建议卡与底部结论条全部完整可读，首版通过。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-04-v1 / baseline / — | 三层同心环比例正确、中心「钠偏高」判定与三行数值完整对齐，首版通过。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-05-v1 / baseline / — | ETA 横幅、5 阶段单轨、当前高亮卡与结论卡完整可读，首版通过。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-06-v1 / baseline / — | 四个放射扇区、圆心与标签卡完整；唯一缺陷是底部说明中英混杂「自己 subtract 出等待时间」。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-07-v1 / baseline / — | 根节点圆偏小使文字贴边；「三个都不是」长贝塞尔曲线横跨到最右灰桶并与另三条连线交叉。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 确认存在缺陷，进入视觉迭代 |
| case-08-v1 / baseline / — | 7 列温度色带、降水条、决策 chip、周降雨色带与结论全部完整对齐，首版通过。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-09-v1 / baseline / — | 三区网格与 07 高亮、记忆卡、三段计费、¥18 大数字完整可读，首版通过。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-10-v1 / baseline / — | 巨大 B27、水平时间轴、右侧面板、荧光绿两行结论与底部信息完整清晰，首版通过。 | 实际打开 v1 渲染图逐项观察；环形刻度与底部条带、文字与条形、文案语言一致性的估计不足 | 生成 v1 首版基线并逐张实际查看 | 首版即通过，未修改 |
| case-01-v2 / visual / case-01-v1 | v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 环形与圆心整体上移（CY 600→555），让「12」刻度落在底部注意事项条上方 | v2 复查：00/06/12/18 四刻度齐全，三个服药弧段、中央 3、三张卡、胶囊与注意事项条全部完整清晰 |
| case-02-v2 / visual / case-02-v1 | v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 条形收窄到独立绘图区、单价数值移到右侧专属列、「最划算」角标右移；结论文案改为与脚本计算一致的「按每月 20 份的单价差累计估算」 | v2 复查：5 个单价数值全部在条形外完整可读，金色高亮行与角标分离，排序正确，底部结论与 ¥16.50 清晰 |
| case-06-v2 / visual / case-06-v1 | v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 底部说明「自己 subtract 出等待时间」改为通顺中文「自己算出等待时间」 | v2 复查：底部文案通顺完整，四扇区、圆心与四张标签卡仍完整无重叠 |
| case-07-v2 / visual / case-07-v1 | v1 实际渲染图中记录的缺陷（见同用例 baseline 的 observed） | 逐张 ViewImage 打开实际 PNG 后的视觉判断 | 根节点圆半径 68→82 并缩小字号；删除交叉长曲线，灰桶改用「三个都不是 → 这里」局部标注 + 短竖线 | v2 复查：根节点文字完整落在圆内，三条问题→桶连线各自独立不交叉，四色桶与 6 个速查色块完整 |

踩坑（均来自实际渲染图或真实服务响应）：① 极坐标刻度文字会被后续绘制的底部条带遮住——case-01 把环形整体上移；② 右对齐数值若与条形共享同一 x 区间会被色条切割——case-02 把数值移到条形右侧独立列；③ 文案必须与脚本计算口径一致，case-02 把「每周买 3 袋」改为「每月 20 份的单价差累计估算」；④ 长贝塞尔连线横跨整张图会与其余连线交叉——case-07 删除该线改用局部标注 + 短竖线；⑤ 根节点圆直径必须大于文字宽度，否则白字落在白底上不可见——case-07 放大圆并缩小字号；⑥ 服务出现多次 http_status=0 的传输层/SSL 握手超时（非 429/503，无 Retry-After），按真实响应重试后全部成功，失败响应与重试记录均保留在 tmp/20261104-145656-hy4all/B06/case-*/requests.jsonl 与 responses/；⑦ A03 已验证 BackdropFilter 在本服务实例不产生可见模糊，毛玻璃需用 ClipRRect + ImageFiltered 只模糊背景副本。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/B06/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T18:33:12+08:00 → 2026-11-04T19:35:01+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 2284.747 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 14 / 12 / 9 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 14 / 4 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

不按行业或媒介列清单，而从「用户原本卡在哪」选 10 个不同性质的障碍：看不懂（说明书/营养表）、比不了（单位价）、找不到重点（账单/轨迹/时刻表/航班屏）、记不住（分类规则/停车位）、难行动（天气/计费）。每件只用一种主导视觉组织，因此 10 张的构图、配色与信息结构互不相同：米白+药丸色、灰蓝+金、深蓝+紫青、白+红黄绿、白+靛蓝绿、深紫+青紫绿灰、白+四色、浅蓝+橙、深绿+米白金、深青+荧光绿。所有数值由脚本计算并在画面标注虚构演示，区分可观察的可读性改善与未经用户实验验证的效果。

最终 10 张实际图片已逐张打开检查（含 v2 视觉迭代复查）：内容、数据、几何、层级、对齐、可读性与裁切均满足题面要求；10 件作品独立完整且各自解决不同日常信息难题；据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
