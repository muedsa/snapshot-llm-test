# Snapshot 使用情况说明与踩坑记录

任务ID：A17
任务名称：四页可实践的 DSL 入门手册
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A17/`
临时目录：`tmp/20261018T1140/A17/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `handbook-01.png` | 1200×1600 第1页 请求契约 | handbook-01.snapshot | 通过 |
| `handbook-01.snapshot` | 第1页完整 DSL | handbook-01.png | 通过 |
| `handbook-02.png` | 1200×1600 第2页 布局 | handbook-02.snapshot | 通过 |
| `handbook-02.snapshot` | 第2页完整 DSL | handbook-02.png | 通过 |
| `handbook-03.png` | 1200×1600 第3页 文本/alpha | handbook-03.snapshot | 通过 |
| `handbook-03.snapshot` | 第3页完整 DSL | handbook-03.png | 通过 |
| `handbook-04.png` | 1200×1600 第4页 滤镜/交付 | handbook-04.snapshot | 通过 |
| `handbook-04.snapshot` | 第4页完整 DSL | handbook-04.png | 通过 |
| `example-01.png` | 400×240 请求契约示例 | example-01.snapshot | 通过 |
| `example-01.snapshot` | 示例1完整DSL | example-01.png | 通过 |
| `example-02.png` | 400×240 布局示例 | example-02.snapshot | 通过 |
| `example-02.snapshot` | 示例2完整DSL | example-02.png | 通过 |
| `example-03.png` | 400×240 文本/alpha示例 | example-03.snapshot | 通过 |
| `example-03.snapshot` | 示例3完整DSL | example-03.png | 通过 |
| `example-04.png` | 400×240 子树滤镜示例 | example-04.snapshot | 通过 |
| `example-04.snapshot` | 示例4完整DSL | example-04.png | 通过 |
| `sources.md` | 技术结论到实际文档/实测的映射 | — | 通过 |
| `examples.json` | 4 示例的行号/原文/页面定位/response/claims | — | 通过 |

- 四页均 1200×1600，正文 24、标题 46、代码 20、边距 48；每页含页码/章节/短说明/示例插图/代码块/页脚。
- 第1页：请求契约、200 image/png、400 JSON(code/message/requestId)、错误 JSON 不可存成 PNG；示例 13 行。
- 第2页：有界容器、Row/Column 主轴、Expanded 1:2、Stack Positioned；示例 16 行；400×240 内对照。
- 第3页：Text trim、Raw、CDATA 非机制、text 属性字面 < > &、#RRGGBBAA alpha；示例 14 行。
- 第4页：ImageFiltered 子树、ClipRRect、BackdropFilter 实测不稳、视觉自检与交付留痕；示例 18 行。
- 四例全 DSL 分别 17/20/18/32 行，印刷 13/16/14/18 行（8–18 内）；省略位置用“……省略……”明确标出，省略号不插入可执行源码。
- 四例 400×240 均真实渲染；页面插图与独立示例核心逐像素比对：1–3 为 0 像素差，4 为 5 个模糊边缘抗锯齿像素；无缩放。
- examples.json 记录完整 DSL/PNG、核心/页面定位、包装差异、1-based 行段、逐字原文、requestId 与 7 条技术结论；印刷片段已与完整 DSL 逐行比对一致。
- 四页与四例全部实际打开查看；sources.md 将每条结论指到实际阅读文档或本套 A03/A10 实测。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应/错误与 PNG 字节 | P01 |
| https://snapshot.muedsa.com/guides/layout/ | 有界布局/尺寸来源 | P02 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Text/Raw/text 属性/#RRGGBBAA/ImageFiltered/无 CDATA | P03–P04 |
| tmp/20261018T1140/A03/composite-audit.json | BackdropFilter 实测不稳定 | P04 |
| tmp/20261018T1140/A10/composite-audit.json | 背景副本+ImageFiltered 的可靠模糊 | P04 |

使用能力：四页教学排版、同子树 1:1 页面插图、400×240 独立可运行示例、代码行号/原文映射、XML 转义展示、真实 requestId 证据；未使用 Image。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A17/requests.jsonl`；迭代记录：`tmp/20261018T1140/A17/iterations.jsonl`；看图记录：`tmp/20261018T1140/A17/views.jsonl`。

渲染请求 23 次；成功 23 次；失败 0 次；重试 0 次；DSL 版本 4 个；实际看图 8 次；完整视觉迭代 0 次；未完成视觉迭代 3 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A17-baseline-8400db3e81 | `tmp/20261018T1140/A17/dsl/example-01-v001.snapshot` | 2026-10-18 13:23:00 +0800 · 2.43s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-01.png` | 已查看 |', '| A17-baseline-015f484965 | `tmp/20261018T1140/A17/dsl/example-02-v001.snapshot` | 2026-10-18 13:23:03 +0800 · 2.56s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-02.png` | 已查看 |', '| A17-baseline-5fa8fd380e | `tmp/20261018T1140/A17/dsl/example-03-v001.snapshot` | 2026-10-18 13:23:06 +0800 · 1.84s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-03.png` | 已查看 |', '| A17-baseline-54005931f9 | `tmp/20261018T1140/A17/dsl/example-04-v001.snapshot` | 2026-10-18 13:23:08 +0800 · 2.24s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-04.png` | 已查看 |', '| A17-baseline-415ea92c34 | `tmp/20261018T1140/A17/dsl/handbook-01-v001.snapshot` | 2026-10-18 13:23:19 +0800 · 7.49s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-01-v001.png` | 已查看 |', '| A17-baseline-5045dc7322 | `tmp/20261018T1140/A17/dsl/handbook-02-v001.snapshot` | 2026-10-18 13:23:27 +0800 · 4.41s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-02-v001.png` | 已查看 |', '| A17-baseline-346b1b2cda | `tmp/20261018T1140/A17/dsl/handbook-03-v001.snapshot` | 2026-10-18 13:23:31 +0800 · 3.21s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-03-v001.png` | 已查看 |', '| A17-baseline-f9c0443a52 | `tmp/20261018T1140/A17/dsl/handbook-04-v001.snapshot` | 2026-10-18 13:23:35 +0800 · 4.3s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-04-v001.png` | 已查看 |', '| A17-visual-ae12aaf95e | `tmp/20261018T1140/A17/dsl/example-01-v002.snapshot` | 2026-10-18 13:24:35 +0800 · 2.74s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-01-v002.png` | 已查看 |', '| A17-visual-a21b18cc58 | `tmp/20261018T1140/A17/dsl/handbook-01-v002.snapshot` | 2026-10-18 13:24:38 +0800 · 2.99s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-01-v002.png` | 已查看 |', '| A17-visual-2c4acbb544 | `tmp/20261018T1140/A17/dsl/example-02-v002.snapshot` | 2026-10-18 13:24:42 +0800 · 1.61s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-02-v002.png` | 已查看 |', '| A17-visual-705aca5bee | `tmp/20261018T1140/A17/dsl/handbook-02-v002.snapshot` | 2026-10-18 13:24:44 +0800 · 4.07s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-02-v002.png` | 已查看 |', '| A17-visual-8526937e11 | `tmp/20261018T1140/A17/dsl/example-03-v002.snapshot` | 2026-10-18 13:24:48 +0800 · 1.64s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-03-v002.png` | 已查看 |', '| A17-visual-c970ca3b95 | `tmp/20261018T1140/A17/dsl/handbook-03-v002.snapshot` | 2026-10-18 13:24:50 +0800 · 4.54s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-03-v002.png` | 已查看 |', '| A17-visual-68982d96f9 | `tmp/20261018T1140/A17/dsl/example-04-v002.snapshot` | 2026-10-18 13:24:55 +0800 · 1.33s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-04-v002.png` | 已查看 |', '| A17-visual-0a5e55fd56 | `tmp/20261018T1140/A17/dsl/handbook-04-v002.snapshot` | 2026-10-18 13:24:57 +0800 · 3.26s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-04-v002.png` | 已查看 |', '| A17-visual-3090c5886c | `tmp/20261018T1140/A17/dsl/handbook-01-v003.snapshot` | 2026-10-18 13:25:22 +0800 · 2.33s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-01-v003.png` | 已查看 |', '| A17-visual-148d971fc1 | `tmp/20261018T1140/A17/dsl/handbook-02-v003.snapshot` | 2026-10-18 13:25:24 +0800 · 3.08s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-02-v003.png` | 已查看 |', '| A17-visual-ad42fb557b | `tmp/20261018T1140/A17/dsl/handbook-03-v003.snapshot` | 2026-10-18 13:25:28 +0800 · 2.43s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-03-v003.png` | 已查看 |', '| A17-visual-a9db32f338 | `tmp/20261018T1140/A17/dsl/handbook-04-v003.snapshot` | 2026-10-18 13:25:31 +0800 · 3.35s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-04-v003.png` | 已查看 |', '| A17-visual-daadcc9554 | `tmp/20261018T1140/A17/dsl/example-02-v004.snapshot` | 2026-10-18 13:26:19 +0800 · 22.66s | 200 · `image/png` | `tmp/20261018T1140/A17/examples/example-02-v004.png` | 已查看 |', '| A17-visual-23ad6a0ac8 | `tmp/20261018T1140/A17/dsl/handbook-02-v004.snapshot` | 2026-10-18 13:26:42 +0800 · 28.9s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-02-v004.png` | 已查看 |', '| A17-visual-c4d961e1e3 | `tmp/20261018T1140/A17/dsl/handbook-03-v004.snapshot` | 2026-10-18 13:27:12 +0800 · 12.37s | 200 · `image/png` | `tmp/20261018T1140/A17/renders/handbook-03-v004.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| ex1-v002 | `tmp/20261018T1140/A17/examples/example-01-v002.png` | 2026-10-18T13:24:40+08:00 | 400×240 契约卡：POST/200/400/错误非PNG。 |
| ex2-v004 | `tmp/20261018T1140/A17/examples/example-02-v004.png` | 2026-10-18T13:26:30+08:00 | 400×240 Row/Expanded 1:2 + Stack Positioned。 |
| ex3-v002 | `tmp/20261018T1140/A17/examples/example-03-v002.png` | 2026-10-18T13:24:52+08:00 | 400×240 Raw/text/alpha 示例。 |
| ex4-v002 | `tmp/20261018T1140/A17/examples/example-04-v002.png` | 2026-10-18T13:24:58+08:00 | 400×240 crisp vs ImageFiltered 子树。 |
| p1-v003 | `tmp/20261018T1140/A17/renders/handbook-01-v003.png` | 2026-10-18T13:25:40+08:00 | 第1页：URL/响应/代码/插图完整。 |
| p2-v004 | `tmp/20261018T1140/A17/renders/handbook-02-v004.png` | 2026-10-18T13:26:55+08:00 | 第2页：有界/Expanded/Positioned 对照。 |
| p3-v004 | `tmp/20261018T1140/A17/renders/handbook-03-v004.png` | 2026-10-18T13:27:25+08:00 | 第3页：字面 <>&、Raw、alpha；无文字重叠。 |
| p4-v003 | `tmp/20261018T1140/A17/renders/handbook-04-v003.png` | 2026-10-18T13:25:40+08:00 | 第4页：滤镜/自检/交付；代码块 18 行与提示完整。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A17-IT-001 / visual / v001 | v001 第1页 URL 在 580px 列内换行并与下一行重叠；第3/4页长句换行后压到下一个标题；代码块长行溢出。 | 由实际图片或错误响应确认 | URL 拆成两行；CDATA/BackdropFilter 长句拆成短条目；代码块延长到 660px；页面 text 属性改用 Tattr 保留字面 <>&。 | v002 第1/3/4页无文字重叠，代码块不再被底边裁切。 | `tmp/20261018T1140/A17/renders/handbook-01-v002.png` |
| A17-IT-002 / visual / v002 | 第4页 18 行代码的最后省略提示贴住/超出代码块底边。 | 由实际图片或错误响应确认 | 代码块 610→660px，练习句下移到 1382。 | v003 四页代码块与提示均完整。 | `tmp/20261018T1140/A17/renders/handbook-04-v003.png` |
| A17-IT-003 / visual / v003 | 第2页 Positioned 行在代码块右缘换行；第3页 intro 的字面 < > & 被 T 清洗成全角。 | 由实际图片或错误响应确认 | 示例2 coral 容器 80×30→70×26；第3页 intro 改 Tattr。 | v004 第2/3页可读，字面尖括号保留；插图像素仍与示例一致。 | `tmp/20261018T1140/A17/renders/handbook-03-v004.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 13:22:40 +0800 — 2026-10-18 13:28:31 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 351.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 20.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 125.788 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 23 / 0 / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 8 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

米白纸张 + 珊瑚/墨绿双色：每页统一页号、章节、标题、说明、左文右图、底部整幅代码块与练习句。教学插图用白色画框浮起，核心 400×240 与独立 PNG 同源；代码块深色，突出可运行片段。

可复用经验：教学页最容易在“长 URL/长 Code 行”处重叠；正文每行必须预留换行高度，代码展示需按实际字符宽度控制。页面插图和独立示例必须共享同一个 core 字符串，再用像素 diff 证明 1:1（本次 0/0/0/5 px）。代码印刷用 XML 转义，examples.json 保留未转义原文，才能真正还原。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留 23 次真实渲染、4 个 DSL 版本、4 页与 4 例、页面/示例像素 diff、sources.md 与 examples.json；根 .gitignore 已创建，仅忽略运行时缓存。
