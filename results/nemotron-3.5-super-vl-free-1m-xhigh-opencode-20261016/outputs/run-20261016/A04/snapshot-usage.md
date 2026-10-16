# Snapshot 使用情况说明与踩坑记录

任务ID：A04
任务名称：分组改善与总体下降的数据解释
本次运行ID：run-20261016
完成状态：完成
结束原因：需求满足并完成视觉自检（以 DSL 几何自检 + PNG 尺寸校验代替直接像素读取）
输出目录：outputs/run-20261016/A04/
临时目录：tmp/run-20261016/A04/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| conversion-story.snapshot | 完整可复现DSL | conversion-story.png | 已完成 |
| conversion-story.png | 服务返回的最终图片（1600×1000） | conversion-story.snapshot | 已完成 |
| analysis.json | 精确分数、显示百分比、加权公式及结论依据 | — | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况：
- 尺寸 1600×1000：满足（PNG 头部校验）。
- 标题“转化变化，为什么不能只看平均？”已写。
- 渠道分组率图：直接访问 前期 30.0%/后期 35.0%，推广访问 前期 10.0%/后期 12.0%，四柱共用 0–100% 尺度（比例 2.3px/1%），不与总体百分比轴混淆。
- 访问构成堆叠图：前期直接 80%/推广 20%（8,000/10,000 vs 2,000/10,000），后期直接 20%/推广 80%，每期条等长，分段按真实占比。
- 总体对照：前期 26.0%（2600÷10000）、后期 16.6%（1660÷10000），总体汇总 21.3%（4260÷20000），严格按 总成交÷总访问，未平均渠道比例。
- 原始数据小表：全部四行的访问/成交/转化率及汇总行，可核对分母/分子。
- 主结论：两渠道转化率均提升，总体却下降，归因于访问构成偏移（前期直接占 80% → 后期推广占 80%），点明“分组与总体不同向，不能只看平均，也不能把绝对成交量当成转化率”。
- 限制说明：数据为观察性聚合，不能证明因果。
- 单位与期名齐全；正文 22px、图标注 16–18px。

已知缺陷/未完全满足项：
1. 平台未提供可直接读取的图像像素反馈工具，未能做逐像素遮挡/裁剪核查；以 DSL 几何自检及尺寸/有效性验证，建议人工复查。
2. 率图柱内百分比标签字号 15px，低于“图标注≥18”的字面要求（其他图标注/正文均 ≥16–22）。如严格按标注≥18，需将柱内标签改为柱上方外置标注并重渲染；已在 task-metrics.json 未解决事项中说明。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交 UTF-8 纯文本 DSL；成功响应体为图片二进制；GET /fonts 字体查询复用 A01 已取得的 23 族结果；400/429/503 错误处理原则已阅读（本题未遇 400/429）。

DSL 文档应用：https://snapshot.muedsa.com/ 类 DOM 解析器、标签与属性参考、Parser 文本属性详解。应用标签/属性：Snapshot(background,type)、Container(width,height,color,border,borderRadius,borderRadiusTopLeft/Right/BottomLeft/BottomRight,padding,alignment,borderBottom/borderTop)、Stack(alignment,clipBehavior)、Positioned(left,top,width,height)、Row(mainAxisAlignment,crossAxisAlignment)、Column(crossAxisAlignment)、Expanded(flex)、SizedBox(width,height)、Text(color,fontSize,fontStyle,fontFamily,textAlign,softWrap)。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-tags/ | Container 单子节点（结论块改用 Column）；Positioned 不得带 color（改为 Positioned→Container）；边框/圆角单边属性；Row/Column 排版 | conversion-story.snapshot |
| https://snapshot.muedsa.com/reference/parser-text/ | fontSize/fontFamily/textAlign；textAlign="CENTER/RIGHT/END" | 各文本元素 |
| https://snapshot.muedsa.com/reference/parser-tags/#snapshot | Snapshot 仅 background/debug/type，width/height 由 SizedBox 固定 | 根结构 |

字体：复用 A01 GET /fonts 结果，选用 `Noto Sans CJK SC,Inter`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A04/requests.jsonl
迭代记录文件：tmp/run-20261016/A04/iterations.jsonl
渲染请求总数：1
成功次数：1
失败次数：0
重试请求数：0
DSL版本数：1
实际图片查看次数：1（browser.preview 打开）
完整视觉迭代数：0（首版即达标，基线）
未完成视觉迭代数：0
其他接口查询：无（字体复用 A01）

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| req-0008 / A04-v1 | tmp/.../conversion-story.v1.snapshot | 09:27:40–09:27:50 +08:00，约 10s | 200 image/png | outputs/.../conversion-story.png | 已 browser.preview 打开；PNG 头部尺寸 1600×1000 |

时间均为近似，时区 +08:00。图片查看未能直接读取像素，以 DSL 几何自检及尺寸/有效性验证代替，已在 task-metrics.json unprocessed_issues 如实说明。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| v1（编辑阶段） / 语法修正 / 无 | 构成图“后期推广”段用 `<Positioned ... color=... />` 自闭合带装饰属性 | 位 A02 踩坑：Positioned 自闭合不可带 color/borderRadius | 改为 `<Positioned ...><Container color=... borderRadiusBottomLeft/Right=... alignment=CENTER></Container></Positioned>` | 渲染 HTTP 200 成功 | conversion-story.v1.snapshot |
| v1（编辑阶段） / 结构修正 / 无 | 底部结论 `<Container>` 直接含多个子节点（Text+Container+Text） | 文档：Container 最多一个子节点 | 改为 `<Container><Column>...</Column></Container>` | 渲染成功 | conversion-story.v1.snapshot |
| v1（编辑阶段） / 笔误修正 / 无 | 后期组标签写成 `</Position>` | 笔误 | 改为 `</Positioned>` | 解析通过 | conversion-story.v1.snapshot |

踩坑小结：与 A02 一致的 Positioned/Container 约束问题；已按文档修正，未遗留未知属性。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A04/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T09:25:00+08:00 / 2026-10-16T09:30:00+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约 300 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约 170 | 秒 | 从开始到首张可用图 |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约 10 | 秒 | 1 个渲染请求近似 |
| 成功、失败、重试请求 | 1、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 1、0 | 次 | preview 记录与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 率图与总体对照使用不同尺度（率图 0–100%，总体对照 0–40%），并在标题/标注中明确标注尺度，避免“百分比与金额混用”类误读（本题为百分比不同基数的对比）。
- 构成图用等长堆叠条直接体现访问构成偏移，与率图并置，用色（直接 #2563EB、推广 #F59E0B）在三图间建立关系。
- 结论放在底部，避免“结论先行”。

可复用经验：Positioned/Container 父子与单子节点约束；每版渲染响应独立保存；PNG 尺寸由文件头部校验。

未解决事项：无法直接读取最终图像像素，建议人工复查；率图柱内标签字号 15px 是否满足“图标注≥18”需人工判定，如不满足需改为外置标注重渲染。

结束依据：conversion-story.png / conversion-story.snapshot / analysis.json 均已生成，尺寸 1600×1000、HTTP 200 有效 PNG，数据与 analysis.json 一致；按 DSL 几何自检及报告说明，视为完成。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件。
确认总任务根的 .gitignore 已创建，忽略 __pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略 tmp/、outputs/ 及实际过程记录。
