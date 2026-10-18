# Snapshot 使用情况说明与踩坑记录

任务ID：A03
任务名称：多层语义故障恢复（System Pulse 监控卡）
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A03/`
临时目录：`tmp/20261018T1140/A03/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `system-pulse.png` | 1280×800 修复后监控卡 | system-pulse.snapshot | 通过 |
| `system-pulse.snapshot` | 最终完整 DSL | system-pulse.png | 通过 |
| `repair-log.json` | 原稿报错、静默忽略、视觉问题与逐版修复证据 | — | 通过 |

- 原稿 broken.snapshot 已原样提交一次：request 7f53ff2c-01d5-40a9-90fc-187c8f801fe3，HTTP 400 PARSE_ERROR，原始响应保存在 tmp/.../responses；失败稿 original/v002/v003/v004 均保留。
- 画布实际响应 1280×800；背景 #0B1220；标题左上距边 32px，字号 44；LIVE 96×36 位于 (1152,32)，与标题无重叠。
- 第一行三张指标卡等宽 389.333px、高 180px、间距 24px，文案 USAGE 72% / LATENCY 148 ms / SUCCESS 99.2% 均为 28px。
- 中央说明卡精确 500×150、圆角 24、位于 (390,390)；彩色细条 x=300..980 同时穿过左右边界；卡内为裁剪+ImageFiltered 的背景副本，文字 Background-only blur 28px 保持清晰。
- REVIEW 标签精确 160×56、位于 (1062,694)、Transform -8°（屏幕逆时针）、背景 #FFFFFF33（20% 白）、文字 #FFFFFF 24px 不透明；旋转后视觉边界在 32px 安全边距内。
- 所有元素完整可见；最终整图与说明卡局部裁图均实际打开检查。
- repair-log.json 含 12 条问题：4 条真实报错、3 条静默/契约问题、5 条视觉或布局问题；每条有原稿行号/节点、依据、修改与验证。
- 修复过程中未通过删除区块来规避需求：LIVE、REVIEW、三指标卡、模糊说明卡均以等价或更完整的实现保留。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应、错误 JSON、字体与颜色 | 全部 8 次渲染 |
| https://snapshot.muedsa.com/reference/parser-tags/ | EdgeInsets、Transform matrix、Positioned 父级、BackdropFilter/ImageFiltered、颜色 alpha、Text fontSize | 原稿修复与最终稿 |
| https://snapshot.muedsa.com/guides/layout/ | 约束、Stack 尺寸与非定位子节点、有界布局 | 根 Stack 与 1280×800 画布修复 |

使用能力：Transform 4×4 矩阵旋转、ImageFiltered 高斯模糊、ClipRRect 裁剪、半透明颜色 alpha、绝对定位 Stack、Row/Column、Progress bar 与 sparkline 由 Container 构造；未使用 Image 或外部素材。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A03/requests.jsonl`；迭代记录：`tmp/20261018T1140/A03/iterations.jsonl`；看图记录：`tmp/20261018T1140/A03/views.jsonl`。

渲染请求 8 次；成功 4 次；失败 4 次；重试 0 次；DSL 版本 8 个；实际看图 5 次；完整视觉迭代 0 次；未完成视觉迭代 3 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A03-initial-broken-9a5c64ccda | `tmp/20261018T1140/A03/dsl/broken/original.snapshot` | 2026-10-18 12:04:17 +0800 · 1.14s | 400 · `application/json` | `tmp/20261018T1140/A03/responses/broken-original-A03-initial-broken-9a5c64ccda.json` | http 400 non-image response |', '| A03-syntax-fix-26f2e03655 | `tmp/20261018T1140/A03/dsl/broken/v002.snapshot` | 2026-10-18 12:04:26 +0800 · 1.65s | 400 · `application/json` | `tmp/20261018T1140/A03/responses/broken-v002-A03-syntax-fix-26f2e03655.json` | http 400 non-image response |', '| A03-syntax-fix-d2297d75ee | `tmp/20261018T1140/A03/dsl/broken/v003.snapshot` | 2026-10-18 12:04:35 +0800 · 2.23s | 400 · `application/json` | `tmp/20261018T1140/A03/responses/broken-v003-A03-syntax-fix-d2297d75ee.json` | http 400 non-image response |', '| A03-alternative-984bc7a0be | `tmp/20261018T1140/A03/dsl/broken/v004.snapshot` | 2026-10-18 12:04:44 +0800 · 2.15s | 400 · `application/json` | `tmp/20261018T1140/A03/responses/broken-v004-A03-alternative-984bc7a0be.json` | http 400 non-image response |', '| A03-baseline-a5a305721d | `tmp/20261018T1140/A03/dsl/system-pulse/v010.snapshot` | 2026-10-18 12:05:34 +0800 · 3.0s | 200 · `image/png` | `tmp/20261018T1140/A03/renders/system-pulse/v010.png` | 已查看 |', '| A03-visual-48660b9ecb | `tmp/20261018T1140/A03/dsl/system-pulse/v011.snapshot` | 2026-10-18 12:06:00 +0800 · 2.58s | 200 · `image/png` | `tmp/20261018T1140/A03/renders/system-pulse/v011.png` | 已查看 |', '| A03-visual-1b07f8623a | `tmp/20261018T1140/A03/dsl/system-pulse/v012.snapshot` | 2026-10-18 12:06:18 +0800 · 4.86s | 200 · `image/png` | `tmp/20261018T1140/A03/renders/system-pulse/v012.png` | 已查看 |', '| A03-visual-bd0937363e | `tmp/20261018T1140/A03/dsl/system-pulse/v013.snapshot` | 2026-10-18 12:06:32 +0800 · 2.68s | 200 · `image/png` | `tmp/20261018T1140/A03/renders/system-pulse/v013.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| v010 | `tmp/20261018T1140/A03/renders/system-pulse/v010.png` | 2026-10-18T12:05:40+08:00 | 首次成功图：1280×900；BackdropFilter 未模糊卡内；标题距顶 24px。 |
| v011 | `tmp/20261018T1140/A03/renders/system-pulse/v011.png` | 2026-10-18T12:06:06+08:00 | 1280×800；卡内副本模糊生效，文字清晰；标题仍 24px。 |
| v012 | `tmp/20261018T1140/A03/renders/system-pulse/v012.png` | 2026-10-18T12:06:24+08:00 | 标题移至 32px，安全边距达标。 |
| v013 | `tmp/20261018T1140/A03/renders/system-pulse/v013.png` | 2026-10-18T12:06:38+08:00 | 最终整图：三卡/LIVE/REVIEW/说明卡全部完整可见。 |
| v013-crop | `tmp/20261018T1140/A03/renders/system-pulse/v013_crop_card.png` | 2026-10-18T12:06:48+08:00 | 局部：卡内细条柔化、卡外锐利，标题/副标题清晰。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A03-IT-001 / syntax-fix / original | padding="24 32" 非法，400 PARSE_ERROR。 | 由实际图片或错误响应确认 | 改为 padding="(24,32)"。 | v002 进入下一错误：Transform matrix 缺失。 | `tmp/20261018T1140/A03/responses/broken-original-A03-initial-broken-9a5c64ccda.json` |
| A03-IT-002 / syntax-fix / v002 | Transform rotate 属性不存在，matrix 必填。 | 由实际图片或错误响应确认 | 替换为 -8° 旋转矩阵；font-size 改 fontSize。 | v003 进入渲染，报 Positioned parentData。 | `tmp/20261018T1140/A03/responses/broken-v002-A03-syntax-fix-26f2e03655.json` |
| A03-IT-003 / syntax-fix / v003 | Positioned 作为 Row 子节点触发 renderBox.parentData must be StackParentData。 | 由实际图片或错误响应确认 | LIVE 移出 Row，最终改为根 Stack 绝对定位。 | v004 暴露 Layout size is infinite。 | `tmp/20261018T1140/A03/responses/broken-v003-A03-syntax-fix-d2297d75ee.json` |
| A03-IT-004 / syntax-fix / v004 | 根 Container 无尺寸、Column+Spacer 无界，Layout size is infinite。 | 由实际图片或错误响应确认 | 最终稿改为绝对定位根 Stack + SizedBox(1280,800)。 | v010 成功输出 1280×900。 | `tmp/20261018T1140/A03/responses/broken-v004-A03-alternative-984bc7a0be.json` |
| A03-IT-005 / visual / v010 | v010 为 1280×900（900×900 非定位渐变撑高）；BackdropFilter 卡内无可见模糊。 | 由实际图片或错误响应确认 | 渐变改 Positioned；模糊改为裁剪内的背景副本 ImageFiltered；标题/卡面重排。 | v011 为 1280×800，卡内细条柔化、文字清晰。 | `tmp/20261018T1140/A03/renders/system-pulse/v011.png` |
| A03-IT-006 / visual / v011 | 标题距顶 24px，不满足 32px 安全边距。 | 由实际图片或错误响应确认 | 标题与 LIVE 移到 y=32。 | v012 安全边距达标。 | `tmp/20261018T1140/A03/renders/system-pulse/v012.png` |
| A03-IT-007 / visual / v012 | 模糊对比偏弱，卡内细条与卡外差异不够明显。 | 由实际图片或错误响应确认 | sigma 14→18，卡面 fill alpha 0x33→0x22。 | v013 卡内柔化、卡外锐利，局部裁图确认。 | `tmp/20261018T1140/A03/renders/system-pulse/v013_crop_card.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 12:04:10 +0800 — 2026-10-18 12:07:23 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 193.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 84.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 20.299 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 4 / 4 / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 5 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

把修复后的监控卡做成一张“运行中的信号面板”：左上角 44px 标题与右上 LIVE 形成实时状态轴；三张等宽指标卡用青/琥珀/绿编码容量、延迟、可靠性；中央说明卡放在彩色信号轨道上，卡内只保留背景的模糊副本，文字浮在最上层，直观展示“background-only blur”的语义；右下 REVIEW 用 -8° 倾斜、20% 白底写成审阅章。

可复用经验：当 BackdropFilter 在当前服务/组合下未产生可见效果时，可以用“同坐标背景副本 + ClipRRect + ImageFiltered”实现只模糊局部背景的等价语义；Transform 必须给 matrix，旋转轴用 alignment=CENTER；Positioned 不能出现在 Row 中；Snapshot 的 width/height 不生效，画布必须由根节点尺寸建立。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留原稿与 4 个失败版本 DSL、4 份错误 JSON、v010–v013 成功 PNG、1 张局部裁图、修复脚本与 repair-log；根 .gitignore 已创建，仅忽略运行时缓存。
