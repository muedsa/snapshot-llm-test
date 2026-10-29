# Snapshot 使用情况说明与踩坑记录

- 任务ID：A23
- 任务名称：格式边界下的动画分镜交付
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A23/`
- 临时目录：`tmp/run-20261029-110525/A23/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `cover.snapshot` | 封面 DSL | `cover.png` | 完成 |
| `cover.png` | 1200×800 封面 | `cover.snapshot` | 完成 |
| `frame-01.snapshot` | 帧1 DSL | `frame-01.png` | 完成 |
| `frame-02.snapshot` | 帧2 DSL | `frame-02.png` | 完成 |
| `frame-03.snapshot` | 帧3 DSL | `frame-03.png` | 完成 |
| `frame-04.snapshot` | 帧4 DSL | `frame-04.png` | 完成 |
| `frame-05.snapshot` | 帧5 DSL | `frame-05.png` | 完成 |
| `frame-06.snapshot` | 帧6 DSL | `frame-06.png` | 完成 |
| `frame-01.png` | 600×600 透明帧1 | `frame-01.snapshot` | 完成 |
| `frame-02.png` | 600×600 透明帧2 | `frame-02.snapshot` | 完成 |
| `frame-03.png` | 600×600 透明帧3 | `frame-03.snapshot` | 完成 |
| `frame-04.png` | 600×600 透明帧4 | `frame-04.snapshot` | 完成 |
| `frame-05.png` | 600×600 透明帧5 | `frame-05.snapshot` | 完成 |
| `frame-06.png` | 600×600 透明帧6 | `frame-06.snapshot` | 完成 |
| `limitations.md` | 格式边界 | `-` | 完成 |
| `frame-data.json` | 逐帧/轨迹/接缝 | `-` | 完成 |
| `timing.json` | 帧时序 | `-` | 完成 |

- 判定格式支持并写 limitations — 证据：limitations.md 四项请求/依据/替代/后续
- 1200×800 封面文字可读 — 证据：“从结构到画面”64px，实图可读
- 6 张透明 PNG、12 单元每帧、属性守恒 — 证据：frame-data.json；角 alpha=0；尺寸/颜色/alpha 不变
- 轨迹连续、末帧成可识别三角 — 证据：径向 smoothstep；6 帧间距 105→60，未重叠
- 250ms/帧、循环 1500ms、帧序 — 证据：timing.json
- 循环接缝说明 — 证据：seam max 135.2px；标注跳变，不称无缝

先依据指南确认服务只输出静态 png/jpg/webp，无 SVG/CMYK/GIF 参数。按授权交付 1200×800 RGB 封面与 6 张 600×600 透明关键帧：12 个单元（4 圆/4 方/4 环）属性跨帧守恒，沿各自径向轨迹从 1.75× 大三角汇聚到最终三角；250ms/帧、1500ms 循环，末帧→首帧为跳变并在 timing/frame-data/limitations 中明确。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 渲染接口/type 仅 png/jpg/webp | A23/A24 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform | 全部布局 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A23/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A23/iterations.jsonl`
- 渲染请求总数：15；成功 14；失败 1；重试 1；DSL 版本 12
- 实际图片查看次数：8；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `fc59c441d8fc` | `outputs/run-20261029-110525/A23/frame-01.snapshot` | 2026-10-29T12:20:50+0800 / 1086ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-01.png` | 已查看 |
| `625a4dbffc56` | `outputs/run-20261029-110525/A23/frame-02.snapshot` | 2026-10-29T12:20:50+0800 / 1285ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-02.png` | 已查看 |
| `09f53993ebff` | `outputs/run-20261029-110525/A23/frame-03.snapshot` | 2026-10-29T12:20:50+0800 / 2323ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-03.png` | 已查看 |
| `3cdcf836ba71` | `outputs/run-20261029-110525/A23/cover.snapshot` | 2026-10-29T12:20:50+0800 / 2808ms | 200 / image/png | `outputs/run-20261029-110525/A23/cover.png` | 已查看 |
| `8d62dff82e5b` | `outputs/run-20261029-110525/A23/frame-04.snapshot` | 2026-10-29T12:20:51+0800 / 1698ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-04.png` | 已查看 |
| `581d2533dad8` | `outputs/run-20261029-110525/A23/frame-06.snapshot` | 2026-10-29T12:20:52+0800 / 1417ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-06.png` | 已查看 |
| `5d9f18af73df` | `outputs/run-20261029-110525/A23/frame-05.snapshot` | 2026-10-29T12:20:51+0800 / 3697ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-05.png` | 已查看 |
| `6b84ca27b78e` | `outputs/run-20261029-110525/A23/frame-05.snapshot` | 2026-10-29T12:21:13+0800 / 946ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-05.png` | 已查看 |
| `727c36ad16be` | `outputs/run-20261029-110525/A23/cover.snapshot` | 2026-10-29T12:21:13+0800 / 1349ms | 200 / image/png | `outputs/run-20261029-110525/A23/cover.png` | 已查看 |
| `490641892392` | `outputs/run-20261029-110525/A23/frame-04.snapshot` | 2026-10-29T12:21:13+0800 / 1749ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-04.png` | 已查看 |
| `b09bef17ba08` | `outputs/run-20261029-110525/A23/frame-03.snapshot` | 2026-10-29T12:21:13+0800 / 1957ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-03.png` | 已查看 |
| `c240f292f4af` | `outputs/run-20261029-110525/A23/frame-06.snapshot` | 2026-10-29T12:21:14+0800 / 1165ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-06.png` | 已查看 |
| `675f94521cef` | `outputs/run-20261029-110525/A23/frame-01.snapshot` | 2026-10-29T12:21:13+0800 / 3810ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-01.png` | 已查看 |
| `faa9aea2bff5` | `outputs/run-20261029-110525/A23/frame-02.snapshot` | 2026-10-29T12:21:13+0800 / 10708ms | None / - | `outputs/run-20261029-110525/A23/frame-02.png` | 失败响应已保留 |
| `d0d35d795f24` | `outputs/run-20261029-110525/A23/frame-02.snapshot` | 2026-10-29T12:21:26+0800 / 2211ms | 200 / image/png | `outputs/run-20261029-110525/A23/frame-02.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A23-v1 / baseline / - | 线性路径中段碰撞 |  | 改径向缩放轨迹 | 通过 | `tmp/run-20261029-110525/A23/drafts/gen_a23.py` |
| visual | 帧中段单元重叠 | 分散点到终点直线路径交叉 | 终点三角形按 1.75× 径向放大作为起点 | 最小中心距 60px；全部可见 | `outputs/run-20261029-110525/A23/frame-data.json` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A23/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T12:20:50+0800 / 2026-10-29T12:25:45+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 295.1 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 1.1 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 38.21 | 秒 | 客户端计时 |
| 成功/失败/重试 | 14 / 1 / 1 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 8 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

动画格式不支持时按授权改为关键帧+timing；循环接缝必须如实标注，不能用 loop 掩饰跳变。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
