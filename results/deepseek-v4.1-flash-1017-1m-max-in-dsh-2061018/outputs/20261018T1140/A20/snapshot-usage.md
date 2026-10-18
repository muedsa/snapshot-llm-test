# Snapshot 使用情况说明与踩坑记录

任务ID：A20
任务名称：二十四密集点的无重叠标注
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A20/`
临时目录：`tmp/20261018T1140/A20/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `annotated-map.png` | 1600×1100 密集点地图与引导标注 | annotated-map.snapshot | 通过 |
| `annotated-map.snapshot` | 完整 DSL | annotated-map.png | 通过 |
| `label-layout.json` | 24 逻辑坐标/像素锚点/标签盒/折线 | — | 通过 |
| `layout-audit.json` | 标签交集/线穿标签/交叉/边界/中心6点 | — | 通过 |

- 1600×1100；主图区 [280,160,1320,920]；像素锚点 (280+10.4x, 920−7.6y)；24 点全部按输入映射，点径 12，未缩小、未删除。
- 24 个标签全部显示编号/name/value，正文 20px；标签盒两两最小间距 5.0px（≥4）；盒与任一非本点圆盘最小净距 18.2px（≥6）；无重叠/无覆盖。
- 5 条引导线；需引导的 M06 已连；线-标签内部 0、线穿圆盘 0、线线交叉 0（上限3）、共线 0、自交 0；线与标签终点正确。
- 坐标轴 0–100、单位“指数”、原点左下说明；value 前三 M10(93)、M08(91)、M23(90) 以金色环/标签标记；最高按 value 降序、ID 升序。
- 图例、几何审计摘要、24/24 标注与页脚均在图中；主图完整；所有目标/标签实际查看。
- 放大查看中心 6 点 M06/M08/M09/M10/M11/M12 及其引导线：标签不压点、线不穿标签、M06 线清晰连回。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应与字体 | 6 个 DSL 版本 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Container/Transform/Stack/Text | 点、标签、折线 |
| https://snapshot.muedsa.com/guides/layout/ | 绝对定位与固定画布 | 1600×1100 |

使用能力：24 点标签非重叠布局、条件引导线、折线交叉几何审计、top3 规则、边界/点覆盖检查；未使用 Image。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A20/requests.jsonl`；迭代记录：`tmp/20261018T1140/A20/iterations.jsonl`；看图记录：`tmp/20261018T1140/A20/views.jsonl`。

渲染请求 12 次；成功 7 次；失败 5 次；重试 4 次；DSL 版本 6 个；实际看图 2 次；完整视觉迭代 0 次；未完成视觉迭代 0 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A20-baseline-63838d188d | `tmp/20261018T1140/A20/dsl/text-metrics-v001.snapshot` | 2026-10-18 13:53:44 +0800 · 2.34s | 400 · `application/json` | `tmp/20261018T1140/A20/responses/text-metrics-v001-A20-baseline-63838d188d.json` | http 400 non-image response |', '| A20-visual-168f9b2601 | `tmp/20261018T1140/A20/dsl/text-metrics-v002.snapshot` | 2026-10-18 13:54:04 +0800 · 1.71s | 200 · `image/png` | `tmp/20261018T1140/A20/renders/text-metrics-v002.png` | 已查看 |', '| A20-visual-29e84053f5 | `tmp/20261018T1140/A20/dsl/text-parts-v003.snapshot` | 2026-10-18 13:54:29 +0800 · 2.63s | 200 · `image/png` | `tmp/20261018T1140/A20/renders/text-parts-v003.png` | 已查看 |', '| A20-baseline-ad97f4c027 | `tmp/20261018T1140/A20/dsl/annotated-map-v001.snapshot` | 2026-10-18 13:58:37 +0800 · 44.54s | None · `None` | `None` | curl exit 35: curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed |', '| A20-retry-5416c40b23 | `tmp/20261018T1140/A20/dsl/annotated-map-v001.snapshot` | 2026-10-18 13:59:25 +0800 · 7.56s | 200 · `image/png` | `tmp/20261018T1140/A20/renders/annotated-map-v001.png` | 已查看 |', '| A20-visual-3b07479dff | `tmp/20261018T1140/A20/dsl/annotated-map-v003.snapshot` | 2026-10-18 14:02:55 +0800 · 181.65s | None · `None` | `None` | curl exit 35: curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed |', '| A20-retry-137b5fe55f | `tmp/20261018T1140/A20/dsl/annotated-map-v003.snapshot` | 2026-10-18 14:06:00 +0800 · 17.49s | 200 · `image/png` | `tmp/20261018T1140/A20/renders/annotated-map-v003.png` | 已查看 |', '| A20-visual-e652446e66 | `tmp/20261018T1140/A20/dsl/annotated-map-v004.snapshot` | 2026-10-18 14:06:43 +0800 · 26.15s | None · `None` | `None` | curl exit 56: curl: (56) Send failure: Connection was reset |', '| A20-retry-b6243cbf02 | `tmp/20261018T1140/A20/dsl/annotated-map-v004.snapshot` | 2026-10-18 14:07:13 +0800 · 90.08s | None · `None` | `None` | curl exit 28: curl: (28) Operation timed out after 90010 milliseconds with 72489 out of 229238 bytes received |', '| A20-retry-8f246ad616 | `tmp/20261018T1140/A20/dsl/annotated-map-v004.snapshot` | 2026-10-18 14:08:47 +0800 · 3.52s | 200 · `image/png` | `tmp/20261018T1140/A20/renders/annotated-map-v004.png` | 已查看 |', '| A20-visual-0016197505 | `tmp/20261018T1140/A20/dsl/annotated-map-v005.snapshot` | 2026-10-18 14:09:55 +0800 · 3.62s | 200 · `image/png` | `tmp/20261018T1140/A20/renders/annotated-map-v005.png` | 已查看 |', '| A20-visual-61eb80e88f | `tmp/20261018T1140/A20/dsl/annotated-map-v006.snapshot` | 2026-10-18 14:10:22 +0800 · 2.75s | 200 · `image/png` | `tmp/20261018T1140/A20/renders/annotated-map-v006.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| v006 | `tmp/20261018T1140/A20/renders/annotated-map-v006.png` | 2026-10-18T14:12:00+08:00 | 全图：24 标签、5 引导线、top3、轴/单位。 |
| v006-crop | `tmp/20261018T1140/A20/crops/v006-center.png` | 2026-10-18T14:12:20+08:00 | 中心 6 点放大：标签不压点，M06 线连回。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A20-IT-001 / alternative / v001 | 早期版本标签密集、引导线穿过标签/圆盘，交叉超限。 | 由实际图片或错误响应确认 | 重排 24 标签盒、限制 5 条引导线、按中心左右分侧；最终 v006 通过。 | 24/24 标签，min gap5.0，line crossings0，线穿标签0。 | `tmp/20261018T1140/A20/renders/annotated-map-v006.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 13:50:00 +0800 — 2026-10-18 14:14:03 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 1443.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 244.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 384.043 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 7 / 5 / 4 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 2 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

米白地图纸 + 深蓝观测点 + 白底标签，密集中心用左右错位与五条细引导线分流；top3 金色环和标签金色文字作为唯一强调色，保持地图本身不被解释文字压住。

可复用经验：标签盒间距与“盒到点圆盘净距”必须分开算；标签靠近点时可免除引导线，但任何 >24px 必须补线。中心 6 点用左右分侧并按 y 排序，才能做到 0 交叉；线必须画在标签与圆盘下层。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留 6 个 DSL 版本、完整 audit/label-layout、失败尝试与中心裁图；根 .gitignore 已创建，仅忽略运行时缓存。
