# Snapshot 使用情况说明与踩坑记录

任务ID：A23
任务名称：格式边界下的动画分镜交付
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A23/`
临时目录：`tmp/20261018T1140/A23/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `cover.png` | 1200×800 RGB 封面 | cover.snapshot | 通过 |
| `cover.snapshot` | 封面完整 DSL | cover.png | 通过 |
| `frame-01.png` | 600×600 透明关键帧1 | frame-01.snapshot | 通过 |
| `frame-01.snapshot` | 帧1完整 DSL | frame-01.png | 通过 |
| `frame-02.png` | 透明关键帧2 | frame-02.snapshot | 通过 |
| `frame-02.snapshot` | 帧2完整 DSL | frame-02.png | 通过 |
| `frame-03.png` | 透明关键帧3 | frame-03.snapshot | 通过 |
| `frame-03.snapshot` | 帧3完整 DSL | frame-03.png | 通过 |
| `frame-04.png` | 透明关键帧4 | frame-04.snapshot | 通过 |
| `frame-04.snapshot` | 帧4完整 DSL | frame-04.png | 通过 |
| `frame-05.png` | 透明关键帧5 | frame-05.snapshot | 通过 |
| `frame-05.snapshot` | 帧5完整 DSL | frame-05.png | 通过 |
| `frame-06.png` | 透明关键帧6（光圈） | frame-06.snapshot | 通过 |
| `frame-06.snapshot` | 帧6完整 DSL | frame-06.png | 通过 |
| `limitations.md` | SVG/CMYK/GIF/动画逐项判定与替代 | — | 通过 |
| `frame-data.json` | 6帧×12单元几何/轨迹/接缝 | — | 通过 |
| `timing.json` | 250ms/帧、1500ms循环、跳变接缝 | — | 通过 |

- 先按实际文档判定：服务只返回静态 PNG；不原生支持 SVG/CMYK/GIF/动画时间轴；limitations.md 逐项写明依据、替代和外部后续，不创建假格式文件。
- 封面 1200×800 RGB，文字“从结构到画面”可读；右侧 12 单元光圈，主色与字体层级统一；封面 DSL 无 Image。
- 6 帧均 600×600 透明 PNG；alpha 范围 0–255，四角 alpha=0；每帧 12 个单元，U01–U12 的颜色/形状/宽高/alpha 跨帧不变，只有位置与旋转变化。
- 6 帧从外圈半径 270px 逐步收拢到 190px；末帧形成 12 点光圈；单元不越出画布、不缩放、不变色、不渐隐；无文字。
- frame-data 记录 6×12 的实际中心/旋转/尺寸/颜色/alpha、相邻帧位移/角度与插值规则；timing 记录 0/250/500/750/1000/1250ms 与 1500ms 循环。
- 末帧→首帧是 250ms 跳变：最大平移 106.875px、最大旋转差 90°；timing/limitations 明确不声称无缝。
- 逐帧 1–6、封面与 3×2 接触表均实际查看；接触表只作辅助，不替代 6 张原图。
- 7 张指定 PNG 全部来自真实服务 200 image/png；封面无 alpha，6 帧真透明；没有合成 GIF/矢量化/CMYK。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 响应类型、PNG 字节、错误 | 全部 19 次渲染 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Container/Transform/颜色/无动画/SVG/CMYK/GIF 标签 | 封面与 6 帧 |
| https://snapshot.muedsa.com/guides/layout/ | 固定 600×600 与位置 | 6 帧 |

使用能力：透明 PNG 关键帧、稳定 ID 与属性守恒、位置/旋转轨迹、时序与跳变接缝记录、格式边界判定；未使用 Image。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A23/requests.jsonl`；迭代记录：`tmp/20261018T1140/A23/iterations.jsonl`；看图记录：`tmp/20261018T1140/A23/views.jsonl`。

渲染请求 19 次；成功 19 次；失败 0 次；重试 0 次；DSL 版本 3 个；实际看图 8 次；完整视觉迭代 0 次；未完成视觉迭代 2 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A23-baseline-e7aafe3f16 | `tmp/20261018T1140/A23/dsl/cover-v001.snapshot` | 2026-10-18 13:55:16 +0800 · 2.81s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/cover-v001.png` | 已查看 |', '| A23-baseline-67b3fed637 | `tmp/20261018T1140/A23/dsl/frame-01-v001.snapshot` | 2026-10-18 13:55:19 +0800 · 1.94s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-01-v001.png` | 已查看 |', '| A23-baseline-b960a2e504 | `tmp/20261018T1140/A23/dsl/frame-02-v001.snapshot` | 2026-10-18 13:55:21 +0800 · 3.91s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-02-v001.png` | 已查看 |', '| A23-baseline-7e05feba2b | `tmp/20261018T1140/A23/dsl/frame-03-v001.snapshot` | 2026-10-18 13:55:25 +0800 · 1.48s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-03-v001.png` | 已查看 |', '| A23-baseline-66c1819ac2 | `tmp/20261018T1140/A23/dsl/frame-04-v001.snapshot` | 2026-10-18 13:55:27 +0800 · 1.26s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-04-v001.png` | 已查看 |', '| A23-baseline-847af47818 | `tmp/20261018T1140/A23/dsl/frame-05-v001.snapshot` | 2026-10-18 13:55:29 +0800 · 1.81s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-05-v001.png` | 已查看 |', '| A23-baseline-798d8b2d98 | `tmp/20261018T1140/A23/dsl/frame-06-v001.snapshot` | 2026-10-18 13:55:31 +0800 · 2.54s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-06-v001.png` | 已查看 |', '| A23-visual-e408a2fa96 | `tmp/20261018T1140/A23/dsl/frame-01-v002.snapshot` | 2026-10-18 13:56:07 +0800 · 2.77s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-01-v002.png` | 已查看 |', '| A23-visual-53f2e2db4e | `tmp/20261018T1140/A23/dsl/frame-02-v002.snapshot` | 2026-10-18 13:56:10 +0800 · 2.4s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-02-v002.png` | 已查看 |', '| A23-visual-fdd1857fe0 | `tmp/20261018T1140/A23/dsl/frame-03-v002.snapshot` | 2026-10-18 13:56:13 +0800 · 4.78s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-03-v002.png` | 已查看 |', '| A23-visual-89d61c0716 | `tmp/20261018T1140/A23/dsl/frame-04-v002.snapshot` | 2026-10-18 13:56:18 +0800 · 2.05s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-04-v002.png` | 已查看 |', '| A23-visual-5dbefef674 | `tmp/20261018T1140/A23/dsl/frame-05-v002.snapshot` | 2026-10-18 13:56:21 +0800 · 2.07s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-05-v002.png` | 已查看 |', '| A23-visual-a04884abde | `tmp/20261018T1140/A23/dsl/frame-06-v002.snapshot` | 2026-10-18 13:56:23 +0800 · 1.41s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-06-v002.png` | 已查看 |', '| A23-final-2cc883791a | `tmp/20261018T1140/A23/dsl/frame-01-v003.snapshot` | 2026-10-18 13:56:36 +0800 · 1.6s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-01-v003.png` | 已查看 |', '| A23-final-1bf278e48c | `tmp/20261018T1140/A23/dsl/frame-02-v003.snapshot` | 2026-10-18 13:56:38 +0800 · 1.06s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-02-v003.png` | 已查看 |', '| A23-final-ac228ec53f | `tmp/20261018T1140/A23/dsl/frame-03-v003.snapshot` | 2026-10-18 13:56:39 +0800 · 1.22s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-03-v003.png` | 已查看 |', '| A23-final-0a2a2ee5da | `tmp/20261018T1140/A23/dsl/frame-04-v003.snapshot` | 2026-10-18 13:56:41 +0800 · 1.36s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-04-v003.png` | 已查看 |', '| A23-final-4de29cf7a2 | `tmp/20261018T1140/A23/dsl/frame-05-v003.snapshot` | 2026-10-18 13:56:43 +0800 · 1.36s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-05-v003.png` | 已查看 |', '| A23-final-7785036522 | `tmp/20261018T1140/A23/dsl/frame-06-v003.snapshot` | 2026-10-18 13:56:44 +0800 · 3.22s | 200 · `image/png` | `tmp/20261018T1140/A23/renders/frame-06-v003.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| cover-v001 | `tmp/20261018T1140/A23/renders/cover-v001.png` | 2026-10-18T13:55:50+08:00 | 封面：文字可读，12 单元光圈完整。 |
| f1-v003 | `tmp/20261018T1140/A23/renders/frame-01-v003.png` | 2026-10-18T13:56:50+08:00 | 外圈：12 单元均在画布内。 |
| f2-v003 | `tmp/20261018T1140/A23/renders/frame-02-v003.png` | 2026-10-18T13:56:53+08:00 | 第二帧：半径收拢。 |
| f3-v003 | `tmp/20261018T1140/A23/renders/frame-03-v003.png` | 2026-10-18T13:56:56+08:00 | 第三帧：无重叠。 |
| f4-v003 | `tmp/20261018T1140/A23/renders/frame-04-v003.png` | 2026-10-18T13:56:59+08:00 | 第四帧：继续收拢。 |
| f5-v003 | `tmp/20261018T1140/A23/renders/frame-05-v003.png` | 2026-10-18T13:57:02+08:00 | 第五帧：接近最终环。 |
| f6-v003 | `tmp/20261018T1140/A23/renders/frame-06-v003.png` | 2026-10-18T13:57:05+08:00 | 末帧：12 点光圈，可识别。 |
| contact | `tmp/20261018T1140/A23/renders/contact-sheet.png` | 2026-10-18T13:57:15+08:00 | 3×2 接触表：汇聚趋势清楚；仅辅助。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A23-IT-001 / visual / v001 | v001 用随机散点，frame 3 出现单元重叠，且 frame 1 的 300px 轨道让边缘单元越出 600 画布。 | 由实际图片或错误响应确认 | 改为同角度径向收拢，外圈 270px，内圈 190px，保留 12 个单元与旋转。 | v002/v003 六帧均 12 个单元、无越界、无重叠；末帧光圈清楚。 | `tmp/20261018T1140/A23/renders/frame-01-v003.png` |
| A23-IT-002 / visual / v002 | v002 之外圈仍略大，frame 1 边缘单元贴边风险。 | 由实际图片或错误响应确认 | 外圈 300→270；其余半径同步收紧；加入接缝旋转数据。 | v003 全部单元在 600×600 内；接缝 106.875px/90° 明确记录。 | `tmp/20261018T1140/A23/renders/contact-sheet.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 13:55:40 +0800 — 2026-10-18 13:57:39 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 119.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | -24.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 41.07 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 19 / 0 / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 8 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

封面用“结构汇聚成画面”的叙事：左侧文字，右侧 12 个形状/颜色单元组成光圈；6 帧从外圈 270px 收拢到 190px，保持单元属性不变，末帧成为可识别的 12 点光圈。接触表按 3×2 排列便于看汇聚。

可复用经验：透明帧必须从 alpha=0 角点和 extrema 验证；随机散点会在中间帧碰撞，改用同角度的径向收拢可保证全程 12 个单元不重叠/不越界。循环若首尾不同必须如实写跳变，不能因 loop=true 就称无缝；Transform 旋转要以自身中心放置。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留 19 次真实渲染、3 个 DSL 版本、6 帧、封面、接触表、frame-data/timing/limitations；根 .gitignore 已创建，仅忽略运行时缓存。
