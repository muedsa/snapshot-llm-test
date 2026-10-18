# Snapshot 使用情况说明与踩坑记录

任务ID：A13
任务名称：品牌标志到完整活动应用（叠光 / Layerlight）
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A13/`
临时目录：`tmp/20261018T1140/A13/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `symbol-color.png` | 512×512 透明彩色图标 | symbol-color.snapshot | 通过 |
| `symbol-color.snapshot` | 彩色图标完整 DSL | symbol-color.png | 通过 |
| `symbol-black.png` | 512×512 透明纯黑图标 | symbol-black.snapshot | 通过 |
| `symbol-black.snapshot` | 纯黑图标完整 DSL | symbol-black.png | 通过 |
| `brand-banner.png` | 1200×400 品牌横幅 | brand-banner.snapshot | 通过 |
| `brand-banner.snapshot` | 横幅完整 DSL | brand-banner.png | 通过 |
| `launch-poster.png` | 1080×1350 发布海报 | launch-poster.snapshot | 通过 |
| `launch-poster.snapshot` | 海报完整 DSL | launch-poster.png | 通过 |
| `brand-system.json` | 色彩/比例/5 构件/留白/应用映射/黑色审计 | — | 通过 |
| `rationale.md` | 224 字方向与选择说明 | — | 通过 |

- 先做 A/B 两个 512×512 透明预览并实际查看：A 为三条水平圆角条 + 珊瑚圆环 + 点；B 为两条对角梁 + 菱形 + 点；32px 同看后选 A（横条/圆环在小尺寸仍辨层数与孔径）。
- 彩色/纯黑图标均 512×512、透明背景；同一 logo_a 几何（3 条 + 1 环 + 1 点，共 5 个主要几何构件），未把文字整体当图标、无现成标志、无外部图片。
- 纯黑版所有 alpha>0 像素 R=G=B=0：56181 个像素，违规 0，alpha 范围 1–255；alpha=0 的 RGB 全为 0。
- 彩色与黑色 alpha 掩码最大差 1（203 个边缘像素，均为抗锯齿），几何一致；彩色图标外 alpha=0 区域 RGB 非零数 0。
- 32×32 检查用 Pillow 10.0.0 预乘 RGB + LANCZOS + 反预乘，实际 32px 浅底查看彩色/黑色轮廓；A 的 3 层与圆孔仍可读，B 的斜梁更易糊。
- 横幅 1200×400：同一几何以 0.5 缩放重绘，文字“叠光 Layerlight”“把复杂信息，组织成清晰画面”完整，含日期与品牌页脚。
- 海报 1080×1350：独立竖构图，0.62 缩放重绘同一几何，含“2026.11.07 · ONLINE”“OPEN BETA”“layerlight.example.org”及品牌/口号；非横幅放大。
- 图标留白：外接框到 512 画布边最小 56px；brand-system 记录 5 构件参数、环孔负空间与两应用几何映射；rationale 224 字 ≤300。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应、PNG/透明背景 | 全部 11 次渲染 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Container 圆角/边框、Transform、颜色 alpha、Text | 图标、横幅、海报 |
| https://snapshot.muedsa.com/guides/layout/ | 绝对定位与画布尺寸 | 四件应用 |

使用能力：纯 DSL 几何标志（3 圆角条 + 圆环 + 圆点）、透明 PNG、同几何多尺度复用、纯黑 alpha 审计、预乘 Lanczos 32px 检查；未使用 Image。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A13/requests.jsonl`；迭代记录：`tmp/20261018T1140/A13/iterations.jsonl`；看图记录：`tmp/20261018T1140/A13/views.jsonl`。

渲染请求 11 次；成功 11 次；失败 0 次；重试 0 次；DSL 版本 4 个；实际看图 10 次；完整视觉迭代 0 次；未完成视觉迭代 2 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A13-preview-88823a55ca | `tmp/20261018T1140/A13/dsl/preview-a/v001.snapshot` | 2026-10-18 13:06:52 +0800 · 2.77s | 200 · `image/png` | `tmp/20261018T1140/A13/previews/preview-a.png` | 已查看 |', '| A13-preview-d8a894803b | `tmp/20261018T1140/A13/dsl/preview-b/v001.snapshot` | 2026-10-18 13:06:55 +0800 · 1.57s | 200 · `image/png` | `tmp/20261018T1140/A13/previews/preview-b.png` | 已查看 |', '| A13-final-1dc37752ba | `tmp/20261018T1140/A13/dsl/symbol-color/v002.snapshot` | 2026-10-18 13:07:06 +0800 · 1.14s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/symbol-color/v002.png` | 已查看 |', '| A13-final-eef1d8a962 | `tmp/20261018T1140/A13/dsl/symbol-black/v002.snapshot` | 2026-10-18 13:07:07 +0800 · 1.96s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/symbol-black/v002.png` | 已查看 |', '| A13-final-f53bf6319a | `tmp/20261018T1140/A13/dsl/banner/v002.snapshot` | 2026-10-18 13:07:10 +0800 · 1.77s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/banner/v002.png` | 已查看 |', '| A13-final-9031efd8a5 | `tmp/20261018T1140/A13/dsl/poster/v002.snapshot` | 2026-10-18 13:07:12 +0800 · 2.69s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/poster/v002.png` | 已查看 |', '| A13-visual-0f475383c3 | `tmp/20261018T1140/A13/dsl/symbol-black/v003.snapshot` | 2026-10-18 13:07:30 +0800 · 1.61s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/symbol-black/v003.png` | 已查看 |', '| A13-final-7ba3c32e8a | `tmp/20261018T1140/A13/dsl/symbol-color/v004.snapshot` | 2026-10-18 13:07:45 +0800 · 2.16s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/symbol-color/v004.png` | 已查看 |', '| A13-final-50720eba7a | `tmp/20261018T1140/A13/dsl/symbol-black/v004.snapshot` | 2026-10-18 13:07:47 +0800 · 1.98s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/symbol-black/v004.png` | 已查看 |', '| A13-final-353be2c945 | `tmp/20261018T1140/A13/dsl/banner/v004.snapshot` | 2026-10-18 13:07:50 +0800 · 3.05s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/banner/v004.png` | 已查看 |', '| A13-final-45bc6d941f | `tmp/20261018T1140/A13/dsl/poster/v004.snapshot` | 2026-10-18 13:07:53 +0800 · 1.77s | 200 · `image/png` | `tmp/20261018T1140/A13/renders/poster/v004.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| preview-a | `tmp/20261018T1140/A13/previews/preview-a.png` | 2026-10-18T13:06:58+08:00 | 方向 A：横条 + 圆环，层次清楚。 |
| preview-b | `tmp/20261018T1140/A13/previews/preview-b.png` | 2026-10-18T13:07:00+08:00 | 方向 B：对角棱镜，动势强但斜梁在 32px 偏细。 |
| color-32 | `tmp/20261018T1140/A13/previews/view-color-32.png` | 2026-10-18T13:08:20+08:00 | 实际 32px：三层与圆孔可辨。 |
| black-32 | `tmp/20261018T1140/A13/previews/view-black-32.png` | 2026-10-18T13:08:22+08:00 | 实际 32px：黑色剪影与圆孔可辨。 |
| a-32 | `tmp/20261018T1140/A13/previews/view-preview-a-32.png` | 2026-10-18T13:08:24+08:00 | A 的 32px 对比。 |
| b-32 | `tmp/20261018T1140/A13/previews/view-preview-b-32.png` | 2026-10-18T13:08:26+08:00 | B 的 32px 对比，斜梁糊化更明显。 |
| color-v004 | `tmp/20261018T1140/A13/renders/symbol-color/v004.png` | 2026-10-18T13:08:40+08:00 | 最终彩色图标，透明背景、5 构件。 |
| black-v003 | `tmp/20261018T1140/A13/renders/symbol-black/v003.png` | 2026-10-18T13:08:42+08:00 | 最终黑版视觉；后续 v004 字节相同。 |
| banner-v004 | `tmp/20261018T1140/A13/renders/banner/v004.png` | 2026-10-18T13:08:50+08:00 | 横幅文字、标志、日期完整。 |
| poster-v004 | `tmp/20261018T1140/A13/renders/poster/v004.png` | 2026-10-18T13:08:55+08:00 | 海报独立竖构图，品牌/口号/日期/OPEN BETA/网址完整。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A13-IT-001 / alternative / — | 两个几何方向需要先比较，不能直接定稿。 | 由实际图片或错误响应确认 | A：三条水平圆角条 + 圆环 + 点；B：两条 45° 梁 + 菱形 + 点。 | 两预览 512×512 实看；A 在 32px 仍保留层数与孔洞，B 斜梁变细，选 A。 | `tmp/20261018T1140/A13/previews/preview-a.png` |
| A13-IT-002 / visual / v002 | 黑色版三条 bar 用 92/85/90% alpha，浅底显示为灰，不符合“纯黑图标”的视觉预期。 | 由实际图片或错误响应确认 | 黑色版全部形状改 #000000FF，仅抗锯齿保留 alpha。 | v003 纯黑；灰色消失，RGB 违规 0。 | `tmp/20261018T1140/A13/renders/symbol-black/v003.png` |
| A13-IT-003 / visual / v003 | 彩色版 bar 仍为半透明，与黑色版的 alpha 掩码不完全一致。 | 由实际图片或错误响应确认 | 彩色 bar 也改不透明；重新生成横幅/海报以复用同一几何与不透明度。 | v004 两图标 alpha 差 ≤1（仅 AA），横幅/海报同步更新。 | `tmp/20261018T1140/A13/renders/symbol-color/v004.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 13:06:30 +0800 — 2026-10-18 13:08:54 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 144.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 22.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 22.481 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 11 / 0 / 0 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 10 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

标志用“信息层叠仍被清晰框定”作核心：三条错位横条代表叠加信息，珊瑚圆环作为取景/聚焦框，黑点在环心稳定视线。横幅沿用横向阅读；海报改为竖向舞台，标志放大置顶、标题与日期形成单独节奏，底部留白承载 OPEN BETA 与网址。

可复用经验：透明图标必须确认 alpha=0 区域 RGB 也为 0；黑色版若用半透明填充会在浅底变灰，应统一为不透明黑，仅让抗锯齿产生 alpha；32px 检查要用预乘 Lanczos，普通 RGBA resize 会产生黑边；圆环用 border 生成孔洞，负空间不另计构件。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留两方向预览、32px 彩色/黑色/方向对比、4 个 DSL 版本与全部渲染；根 .gitignore 已创建，仅忽略运行时缓存。
