# Snapshot 使用情况说明与踩坑记录

任务ID：A11
任务名称：文字保真与跨页结算单
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A11/`
临时目录：`tmp/20261018T1140/A11/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `invoice-page-01.png` | 1200×1600 结算与明细 | invoice-page-01.snapshot | 通过 |
| `invoice-page-01.snapshot` | 第 1 页完整 DSL | invoice-page-01.png | 通过 |
| `invoice-page-02.png` | 1200×1600 说明与原样文字 | invoice-page-02.snapshot | 通过 |
| `invoice-page-02.snapshot` | 第 2 页完整 DSL | invoice-page-02.png | 通过 |
| `invoice-audit.json` | 逐行金额、计税基数、舍入与 literal_lines 原样 | — | 通过 |
| `text-map.json` | 54 段文本的页面/像素盒/字体/字号与核对 | — | 通过 |

- 两页均 1200×1600；同一页眉显示 SN-2026-1107-008、2026-11-07、CNY，页码 1/2 与 2/2；安全边距 ≥48，正文 22–26px、脚注 ≥20px。
- 第 1 页四行 SKU/名称/数量/单价/行金额完整：805.50、478.80、1,160.00、1,680.00；金额列右对齐、等宽字体、两位小数。
- 小计 4,124.30；折扣 −180.00；税前 3,944.30；税 236.66（236.658 经 ROUND_HALF_UP 至分）；运费 35.00 不计税；应付 4,215.96。
- 计量使用 Decimal 定点：行金额乘后 quantize 0.01，税只在本步舍入，运费最后相加；invoice-audit 记录精确基数与顺序。
- 第 1 页表头、合计值、核验摘要均无裁切；SKU A<B&C>D 用 Text 的 text 属性原样显示，未变成实体。
- 第 2 页四条 notes 与四条 literal_lines 完整；literal 行使用 text 属性逐字符保真：批次行双空格、路径反斜杠、A < B & C > D、英文指令行均原样。
- PAID / 已结算 用同一外层 Text 的三个 span：PAID 绿色、斜线灰色、中文深色，同基线；状态不改应付。指令行仅排版。
- 两页整图与表格、合计、literal、PAID 局部图实际查看；text-map 54 段覆盖页眉、双方、四行、合计、四条 notes、四条 literal 与 PAID。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应、颜色与字体 | 全部 13 次渲染请求 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Text text 属性、嵌套 span/Raw、fontFamily、颜色 | literal 保真与 PAID 富文本 |
| https://snapshot.muedsa.com/guides/layout/ | 固定尺寸 Stack 与 Positioned | 两页页眉、表格、合计 |

使用能力：十进制定点计费与 ROUND_HALF_UP、Text text 属性原样字符、嵌套 span 富文本、等宽金额对齐、中/日/拉丁字体回退、跨页重复页眉；未使用 Image。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A11/requests.jsonl`；迭代记录：`tmp/20261018T1140/A11/iterations.jsonl`；看图记录：`tmp/20261018T1140/A11/views.jsonl`。

渲染请求 13 次；成功 9 次；失败 4 次；重试 0 次；DSL 版本 7 个；实际看图 10 次；完整视觉迭代 0 次；未完成视觉迭代 3 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A11-test-8a0447953e | `tmp/20261018T1140/A11/scripts/literal-test.snapshot` | 2026-10-18 12:35:23 +0800 · 1.99s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/literal-test.png` | 已查看 |', '| A11-baseline-3dbf04c903 | `tmp/20261018T1140/A11/dsl/page1/v002.snapshot` | 2026-10-18 12:36:38 +0800 · 4.12s | 400 · `application/json` | `tmp/20261018T1140/A11/responses/page1-v002-A11-baseline-3dbf04c903.json` | http 400 non-image response |', '| A11-baseline-fb3c491dde | `tmp/20261018T1140/A11/dsl/page2/v002.snapshot` | 2026-10-18 12:36:42 +0800 · 4.08s | 400 · `application/json` | `tmp/20261018T1140/A11/responses/page2-v002-A11-baseline-fb3c491dde.json` | http 400 non-image response |', '| A11-baseline-51de6e65ec | `tmp/20261018T1140/A11/dsl/page1/v003.snapshot` | 2026-10-18 12:37:05 +0800 · 3.1s | 400 · `application/json` | `tmp/20261018T1140/A11/responses/page1-v003-A11-baseline-51de6e65ec.json` | http 400 non-image response |', '| A11-baseline-74773df308 | `tmp/20261018T1140/A11/dsl/page2/v003.snapshot` | 2026-10-18 12:37:08 +0800 · 3.11s | 400 · `application/json` | `tmp/20261018T1140/A11/responses/page2-v003-A11-baseline-74773df308.json` | http 400 non-image response |', '| A11-baseline-85992b5ee8 | `tmp/20261018T1140/A11/dsl/page1/v004.snapshot` | 2026-10-18 12:37:26 +0800 · 20.73s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page1/v004.png` | 已查看 |', '| A11-baseline-190018929d | `tmp/20261018T1140/A11/dsl/page2/v004.snapshot` | 2026-10-18 12:37:47 +0800 · 3.21s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page2/v004.png` | 已查看 |', '| A11-visual-fd44e71f63 | `tmp/20261018T1140/A11/dsl/page1/v005.snapshot` | 2026-10-18 12:38:22 +0800 · 4.3s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page1/v005.png` | 已查看 |', '| A11-visual-420597a51f | `tmp/20261018T1140/A11/dsl/page2/v005.snapshot` | 2026-10-18 12:38:26 +0800 · 2.6s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page2/v005.png` | 已查看 |', '| A11-visual-bb393c22de | `tmp/20261018T1140/A11/dsl/page1/v006.snapshot` | 2026-10-18 12:38:58 +0800 · 3.93s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page1/v006.png` | 已查看 |', '| A11-visual-478756f55b | `tmp/20261018T1140/A11/dsl/page2/v006.snapshot` | 2026-10-18 12:39:02 +0800 · 2.55s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page2/v006.png` | 已查看 |', '| A11-visual-b18ebd66aa | `tmp/20261018T1140/A11/dsl/page1/v007.snapshot` | 2026-10-18 12:39:32 +0800 · 2.75s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page1/v007.png` | 已查看 |', '| A11-visual-43a6eb66af | `tmp/20261018T1140/A11/dsl/page2/v007.snapshot` | 2026-10-18 12:39:35 +0800 · 4.14s | 200 · `image/png` | `tmp/20261018T1140/A11/renders/page2/v007.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| literal-test | `tmp/20261018T1140/A11/renders/literal-test.png` | 2026-10-18T12:35:30+08:00 | 验证 text 属性可原样显示 < & >，实体形式会显示成字面量。 |
| page1-v004 | `tmp/20261018T1140/A11/renders/page1/v004.png` | 2026-10-18T12:37:38+08:00 | 首版成功：表头/合计右侧裁切，PAID 无空格。 |
| page2-v004 | `tmp/20261018T1140/A11/renders/page2/v004.png` | 2026-10-18T12:37:55+08:00 | 四条 notes、literal 与 PAID 结构完整；PAID 空格缺失。 |
| crop | `tmp/20261018T1140/A11/renders/p1_table.png` | 2026-10-18T12:38:00+08:00 | 局部：表头 AMOUNT 被裁。 |
| crop | `tmp/20261018T1140/A11/renders/p1_totals.png` | 2026-10-18T12:38:02+08:00 | 局部：合计 4,215.96 贴边裁切。 |
| crop | `tmp/20261018T1140/A11/renders/p2_literal_v005.png` | 2026-10-18T12:38:32+08:00 | 局部：双空格、反斜杠、< & > 原样。 |
| crop | `tmp/20261018T1140/A11/renders/p2_paid_v006.png` | 2026-10-18T12:39:08+08:00 | 局部：PAID 绿、斜线灰、中文深色，空格已保留。 |
| page1-v007 | `tmp/20261018T1140/A11/renders/page1/v007.png` | 2026-10-18T12:39:40+08:00 | 最终第 1 页：表头/合计/摘要完整，字号达标。 |
| page2-v007 | `tmp/20261018T1140/A11/renders/page2/v007.png` | 2026-10-18T12:39:45+08:00 | 最终第 2 页：notes、literal、PAID、check 完整。 |
| crop | `tmp/20261018T1140/A11/renders/p2_paid_v007.png` | 2026-10-18T12:39:50+08:00 | 局部复查：PAID / 已结算 空格与颜色。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A11-IT-001 / syntax-fix / v001-v003 | 两页 v002/v003 均 400 RENDER_ERROR：Layout size is infinite。 | 由实际图片或错误响应确认 | 页眉 Stack 首部加入非定位 SizedBox(W,230)，并给页眉/说明行 Row 显式宽度。 | v004 两页 200，1200×1600。 | `tmp/20261018T1140/A11/responses/page1-v002-A11-baseline-3dbf04c903.json` |
| A11-IT-002 / visual / v004 | 表头 AMOUNT 被内边距裁切，合计 4,215.96 被 192px 值框裁切，PAID 空格被 trim。 | 由实际图片或错误响应确认 | 表头去水平内边距；合计值框 340/192→300/208；PAID 斜线用 Raw 保留空格。 | v005 表头与合计完整，PAID 显示空格。 | `tmp/20261018T1140/A11/renders/p2_paid_v005.png` |
| A11-IT-003 / visual / v005 | SKU 的 O/0 在无衬线等宽中仍易混，合计值贴近卡片右缘。 | 由实际图片或错误响应确认 | SKU 改 DejaVu Sans Mono；合计值框 232→208，右侧留 12px。 | v006 SKU 更易区分，合计不贴边。 | `tmp/20261018T1140/A11/renders/p1_table_v006.png` |
| A11-IT-004 / visual / v006 | 摘要标签 18px、合计脚注 18px，低于脚注 20px；摘要值 22px 低于正文 24px。 | 由实际图片或错误响应确认 | 标签/脚注提升到 20px，摘要值 24px，合计值右移留白。 | v007 字号层级满足要求，无裁切。 | `tmp/20261018T1140/A11/renders/page1/v007.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 12:35:40 +0800 — 2026-10-18 12:40:50 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 310.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | -17.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 60.635 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 9 / 4 / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 10 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

以米白纸张、深墨与墨绿作“正式结算单”：第 1 页上半部是买卖双方和发票元信息，中部是四行明细，右侧纵向合计，底部核验摘要；第 2 页用四张编号说明卡、深色等宽原样文字块和状态样张收束。金额与 SKU 用等宽字体，中文/日文按语言切换字体。

可复用经验：literal_lines 里的 <、>、& 必须走 Text 的 text 属性，内容节点会被当作标签；双空格在属性中保留。嵌套 span 里的普通空格可能被 trim，PAID 的斜线两侧应使用 Raw。页眉嵌套 Stack 若只有 Positioned 子节点也会触发 Layout size infinite，需要非定位 SizedBox。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留 13 次服务请求（4 次失败、1 次字符测试）、7 个 DSL 版本、两页 PNG 与 8 张局部证据；根 .gitignore 已创建，仅忽略运行时缓存。
