# Snapshot 使用情况说明与踩坑记录

任务ID：A19
任务名称：构造可核验的视觉题场
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A19/`
临时目录：`tmp/20261018T1140/A19/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `grid-scene.png` | 1600×1600 8×8、64对象网格 | grid-scene.snapshot | 通过 |
| `grid-scene.snapshot` | 网格完整 DSL | grid-scene.png | 通过 |
| `occlusion.png` | 800×800 遮挡 A | occlusion.snapshot | 通过 |
| `occlusion.snapshot` | 遮挡 A 完整 DSL | occlusion.png | 通过 |
| `occlusion-alternative.png` | 800×800 遮挡 B（隐藏内容不同） | occlusion-alternative.snapshot | 通过 |
| `occlusion-alternative.snapshot` | 遮挡 B 完整 DSL | occlusion-alternative.png | 通过 |
| `scene-data.json` | 64对象真实几何/频数/行检查 | — | 通过 |
| `questions.json` | 12网格题+2遮挡题，不含答案 | — | 通过 |
| `answers.json` | 14题答案/计算/容差/可见性 | — | 通过 |
| `equivalence.json` | A/B SHA-256 与逐像素四通道对比 | — | 通过 |

- 网格 1600×1600，8×8 格、每格 180px、原点 (80,80)；64 个对象 G01–G64 行优先编号，每格恰一主体，ID 在主体外。
- 颜色蓝/橙/绿/紫各16，形状圆/方/圆环/圆角方各16；尺寸 48/64/80 计数 32/16/16；16种颜色×形状组合全部出现；每种颜色与每种形状都出现三种尺寸；每行颜色/形状均≥3。
- 圆/方/圆环/圆角方按 48/64/80 绘制；圆按直径、方按边长；圆环外径=尺寸、内径=一半；无外部图。
- 64 个 ID 标签均在主体外（cell 内左上），全图与标签实际查看；对象颜色/形状/尺寸组合可辨。
- 遮挡 A/B 均 800×800；可见层（米白底、蓝圆、绿圆角方、不透明块 [120,200,680,620]）完全一致；隐藏 A 红圆+黄方，B 紫环+青圆角方，均完全在块内，无阴影/滤镜/虚线。
- 两遮挡 PNG 解码为 8 位未预乘 RGBA：尺寸相同、不同像素数 0、最大通道差 0；像素数组哈希相同；文件 SHA-256 也相同。
- 12 道网格题覆盖复合检索、严格中心关系、距离、排序、包围框、颜色/形状计数；Q08/Q09/Q11/Q12 为两步关系；2 道遮挡题，Q14 答案为“无法确定”。
- 所有题目写明左上原点、x向右/y向下、像素与边界/并列规则；questions.json 不含答案，answers.json 给出方法/容差/可见性依据。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应与 PNG | 5 次渲染 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Container 边框/圆角、Stack、Text | 网格与遮挡 |
| https://snapshot.muedsa.com/guides/layout/ | 固定画布与坐标 | 1600/800 |

使用能力：结构化 64 对象属性网格、四形状/三尺寸、稳定 ID、完全遮挡等价对、RGBA 逐像素等价、14 题问答数据；未使用 Image。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A19/requests.jsonl`；迭代记录：`tmp/20261018T1140/A19/iterations.jsonl`；看图记录：`tmp/20261018T1140/A19/views.jsonl`。

渲染请求 5 次；成功 5 次；失败 0 次；重试 0 次；DSL 版本 2 个；实际看图 3 次；完整视觉迭代 0 次；未完成视觉迭代 1 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A19-baseline-d895fe20bd | `tmp/20261018T1140/A19/dsl/grid-v001.snapshot` | 2026-10-18 13:47:43 +0800 · 10.23s | 200 · `image/png` | `tmp/20261018T1140/A19/renders/grid-v001.png` | 已查看 |', '| A19-baseline-55dd76ff79 | `tmp/20261018T1140/A19/dsl/occlusion-v001.snapshot` | 2026-10-18 13:47:54 +0800 · 2.45s | 200 · `image/png` | `tmp/20261018T1140/A19/renders/occlusion-v001.png` | 已查看 |', '| A19-baseline-bfac3df132 | `tmp/20261018T1140/A19/dsl/occlusion-alt-v001.snapshot` | 2026-10-18 13:47:56 +0800 · 1.57s | 200 · `image/png` | `tmp/20261018T1140/A19/renders/occlusion-alt-v001.png` | 已查看 |', '| A19-visual-c61ba24905 | `tmp/20261018T1140/A19/dsl/occlusion-v002.snapshot` | 2026-10-18 13:48:09 +0800 · 2.9s | 200 · `image/png` | `tmp/20261018T1140/A19/renders/occlusion-v002.png` | 已查看 |', '| A19-visual-f0c320a92f | `tmp/20261018T1140/A19/dsl/occlusion-alt-v002.snapshot` | 2026-10-18 13:48:12 +0800 · 1.63s | 200 · `image/png` | `tmp/20261018T1140/A19/renders/occlusion-alt-v002.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| grid-v001 | `tmp/20261018T1140/A19/renders/grid-v001.png` | 2026-10-18T13:48:20+08:00 | 8×8、64 ID/对象完整；形状尺寸可辨。 |
| occl-v002 | `tmp/20261018T1140/A19/renders/occlusion-v002.png` | 2026-10-18T13:49:30+08:00 | 可见蓝圆/绿圆角方；遮挡块完整。 |
| occl-alt-v002 | `tmp/20261018T1140/A19/renders/occlusion-alt-v002.png` | 2026-10-18T13:49:35+08:00 | 与 A 视觉完全相同；隐藏内容不可见。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A19-IT-001 / visual / v001 | v001 遮挡图右下绿色圆角方与遮挡块重叠 5px，可见前景被裁。 | 由实际图片或错误响应确认 | 绿色圆角方从 (615,615) 移到 (640,650)，完全离开遮挡块。 | v002 可见层完整，A/B 仍逐像素相同。 | `tmp/20261018T1140/A19/renders/occlusion-v002.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 13:47:30 +0800 — 2026-10-18 13:49:31 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 121.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 13.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 18.783 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 5 / 0 / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 3 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

网格用米白底与细格线，ID 置左上、主体居中；颜色/形状/尺寸三属性可逐格读。遮挡图用极简可见层与一整块深色不透明矩形，隐藏内容只存在于块后，A/B 视觉完全同图。

可复用经验：先固定 16 组合×4副本的尺寸序列，再洗牌并检查每行颜色/形状数，能同时满足覆盖与行约束。完全遮挡必须把隐藏对象画在遮挡块之前、完全落在块边界内且不加阴影；最终用 RGBA 数组而非文件哈希判定像素等价。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留两版遮挡、5 次真实渲染、scene/questions/answers/equivalence；根 .gitignore 已创建，仅忽略运行时缓存。
