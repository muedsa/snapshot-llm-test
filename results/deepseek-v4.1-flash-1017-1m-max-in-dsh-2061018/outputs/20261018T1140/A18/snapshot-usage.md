# Snapshot 使用情况说明与踩坑记录

任务ID：A18
任务名称：守恒对象的三幕视觉叙事
本次运行ID：20261018T1140
完成状态：completed
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261018T1140/A18/`
临时目录：`tmp/20261018T1140/A18/`
路径基准：默认 suite_root；指标/日志相对总任务根，Markdown 本地链接相对本文件。

遵循[PATHS.md](../../../PATHS.md)。本报告中的图片/DSL 链接均相对本文件所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL / 图片 | 状态 |
|---|---|---|---|
| `three-act-story.png` | 1600×1000 三幕图 | three-act-story.snapshot | 通过 |
| `three-act-story.snapshot` | 最终完整 DSL | three-act-story.png | 通过 |
| `story-audit.json` | 逐幕15单元/3节点/接收关系/叙事证据 | — | 通过 |
| `rationale.md` | 281 字方向选择与感知说明 | — | 通过 |

- 两种 1600×1000 预览 A（三列并置）/B（三条横带）均真实渲染并查看；选 A：三幕在 400px 缩略仍同时可读，B 的第三幕退化为三组单色簇。
- 最终图为 1600×1000；三幕各 15 个 36px 圆（蓝/橙/灰各5，U01–U15 固定），三节点 N01 环/N02 方/N03 三角，外框均 72×72。
- 第一幕：15 条线全部指向 N01，三环半径 105/160/210，平均接收距离 158.3px，最小单元间距 97.1px，N02/N03 负载 0。
- 第二幕：同一 15 单元、同一 N01；三环缩到 60/105/150，平均距离 105.0px，最小间距 66.5px，并加三条同心排队弧；N02/N03 仍 0，体现同一系统过载而非增删单元。
- 第三幕：N01/N02/N03 各 5 个单元（5/5/5），颜色分别 3/2/2 种；最小单元间距 96.4px，单元到节点最小 85.99px；连线分 3 束各 5 条。
- 所有幕单元直径 36、颜色跨幕稳定；节点形状/基准 72 不变，无有限形变；线先画、圆后画，线不遮圆；单元间/单元节点间均无重叠。
- 图中文字仅总标题与三幕幕名；单元/节点无文字；无外部图像。
- 整图与 400×250 缩略均实际打开：400px 下三幕、中心聚拢、密集环、三分流仍可辨。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-18
AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md（已实际阅读）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应与 PNG | 7 次渲染 |
| https://snapshot.muedsa.com/reference/parser-tags/ | Container/Stack/Positioned/Transform/ClipPath | 连线、节点、单元 |
| https://snapshot.muedsa.com/guides/layout/ | 固定 1600×1000 与有界 Stack | 三面板 |

使用能力：稳定 ID 的 15 单元×3 幕、3 个不同形状节点、旋转连线矩形、同心排队弧、坐标/负载/重叠审计、400px 缩略检查；未使用 Image。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261018T1140/A18/requests.jsonl`；迭代记录：`tmp/20261018T1140/A18/iterations.jsonl`；看图记录：`tmp/20261018T1140/A18/views.jsonl`。

渲染请求 7 次；成功 5 次；失败 2 次；重试 1 次；DSL 版本 5 个；实际看图 5 次；完整视觉迭代 0 次；未完成视觉迭代 1 次。

| 请求ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看结果 |
|---|---|---|---|---|---|
['| A18-preview-02f93c5e7e | `tmp/20261018T1140/A18/dsl/preview-a-v001.snapshot` | 2026-10-18 13:30:19 +0800 · 300.58s | None · `None` | `None` | curl exit 28: curl: (28) Operation timed out after 300015 milliseconds with 0 bytes received |', '| A18-preview-58110966f0 | `tmp/20261018T1140/A18/dsl/preview-a-v002.snapshot` | 2026-10-18 13:42:09 +0800 · 10.49s | 200 · `image/png` | `tmp/20261018T1140/A18/previews/preview-a.png` | 已查看 |', '| A18-preview-c9cabc7cad | `tmp/20261018T1140/A18/dsl/preview-a-v003.snapshot` | 2026-10-18 13:42:31 +0800 · 7.58s | 200 · `image/png` | `tmp/20261018T1140/A18/previews/preview-a-v003.png` | 已查看 |', '| A18-preview-1271eb1bc4 | `tmp/20261018T1140/A18/dsl/preview-b-v003.snapshot` | 2026-10-18 13:42:48 +0800 · 14.73s | 200 · `image/png` | `tmp/20261018T1140/A18/previews/preview-b-v003.png` | 已查看 |', '| A18-final-06adfd58ed | `tmp/20261018T1140/A18/dsl/three-act-story-v004.snapshot` | 2026-10-18 13:43:19 +0800 · 43.32s | 200 · `image/png` | `tmp/20261018T1140/A18/renders/three-act-story-v004.png` | 已查看 |', '| A18-final-a5bd977457 | `tmp/20261018T1140/A18/dsl/three-act-story-v005.snapshot` | 2026-10-18 13:44:11 +0800 · 61.39s | None · `None` | `None` | curl exit 35: curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed |', '| A18-retry-b1ef3e0e07 | `tmp/20261018T1140/A18/dsl/three-act-story-v005.snapshot` | 2026-10-18 13:45:16 +0800 · 36.08s | 200 · `image/png` | `tmp/20261018T1140/A18/renders/three-act-story-v006.png` | 已查看 |']

图片查看记录：

| 版本 | 图片 | 查看时间 | 实际检查结果 |
|---|---|---|---|
| A-v003 | `tmp/20261018T1140/A18/previews/preview-a-v003.png` | 2026-10-18T13:42:40+08:00 | 三列并置：聚拢/拥挤/三分流清楚。 |
| B-v003 | `tmp/20261018T1140/A18/previews/preview-b-v003.png` | 2026-10-18T13:42:55+08:00 | 三条横带：网格化，第三幕单色簇，分配关系弱。 |
| v004 | `tmp/20261018T1140/A18/renders/three-act-story-v004.png` | 2026-10-18T13:44:30+08:00 | 图形正确，但幕名乱码。 |
| v006 | `tmp/20261018T1140/A18/renders/three-act-story-v006.png` | 2026-10-18T13:46:20+08:00 | 最终全图：中文幕名、三幕、15 单元/节点/连线。 |
| 400px | `tmp/20261018T1140/A18/previews/thumb-400.png` | 2026-10-18T13:46:40+08:00 | 400×250：三幕仍可辨，中心/密集/分流可读。 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| A18-IT-001 / alternative / — | 需要先比较三列并置与三条横带两种叙事构图。 | 由实际图片或错误响应确认 | A 三列同心环；B 三条横带规则网格。 | A 在缩略仍保留三幕关系；B 第三幕呈三组单色簇，选 A。 | `tmp/20261018T1140/A18/previews/preview-a-v003.png` |
| A18-IT-002 / visual / v002 | v002 的旋转连线全部堆在每个面板左上角，未连到单元/节点。 | 由实际图片或错误响应确认 | line 返回 Positioned(left=midX-len/2, top=midY-1) 包住 Transform，不再用 Pos(0,0)。 | v003 15 条线正确连到接收节点；预览 A 通过。 | `tmp/20261018T1140/A18/previews/preview-a-v003.png` |
| A18-IT-003 / retry / v004 | v004 用 PowerShell 替换中文幕名，文件被按错误编码读写，幕名显示为乱码。 | 由实际图片或错误响应确认 | 改用 Python UTF-8 读写，生成 v005 DSL。 | v006 幕名“第一幕/第二幕/第三幕”正确；图像其余不变。 | `tmp/20261018T1140/A18/renders/three-act-story-v006.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-18 13:30:00 +0800 — 2026-10-18 13:47:03 +0800 | 含时区 | 本任务墙钟记录 |
| 任务总耗时 | 1023.0 | 秒 | 开始到本报告完成 |
| 首次可用图耗时 | 729.0 | 秒 | 开始到首个 200 图片响应 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（null） | 秒 | 无 429/503 记录 |
| 已记录请求耗时之和 | 474.179 | 秒 | 请求日志之和，含重叠，不等于墙钟 |
| 成功、失败、重试请求 | 5 / 2 / 1 | 次 | `requests.jsonl` |
| 实际看图与完整视觉迭代 | 5 / 0 | 次 | `views.jsonl`、`iterations.jsonl` |

## 6. 设计选择、经验与未解决事项

三列并置保持三幕同时可比较：第一幕单元在宽环上向中心 N01 汇聚；第二幕同一 N01 与同一 15 单元被压到更近的三环，并出现排队弧；第三幕 N01/N02/N03 形成上/左下/右下三角，每节点 5 个单元。连线颜色随单元、但关系由端点与几何决定，不只靠颜色。

可复用经验：Transform 连线必须把旋转盒放在线段中点，否则所有线会堆到 Stack 左上；三面板各自都需要非定位 SizedBox，否则全 Positioned 会触发无限布局。过载不能靠删/缩单元，改用同一数量的更近环距+排队弧+更密集线束。

未解决事项：
- 无影响交付的已知缺陷。

临时目录保留 A/B 预览、7 次真实请求（2 次服务失败）、5 个 DSL 版本、全图与 400px 缩略；根 .gitignore 已创建，仅忽略运行时缓存。
