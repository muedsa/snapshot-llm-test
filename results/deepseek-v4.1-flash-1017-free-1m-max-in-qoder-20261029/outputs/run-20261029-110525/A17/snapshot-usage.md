# Snapshot 使用情况说明与踩坑记录

- 任务ID：A17
- 任务名称：四页可实践的DSL入门手册
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A17/`
- 临时目录：`tmp/run-20261029-110525/A17/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `handbook-01.snapshot` | 教学页 DSL | `handbook-01.png` | 完成 |
| `handbook-01.png` | 1200×1600 教学页 | `handbook-01.snapshot` | 完成 |
| `example-01.snapshot` | 可运行示例 DSL | `example-01.png` | 完成 |
| `example-01.png` | 400×240 独立渲染 | `example-01.snapshot` | 完成 |
| `handbook-02.snapshot` | 教学页 DSL | `handbook-02.png` | 完成 |
| `handbook-02.png` | 1200×1600 教学页 | `handbook-02.snapshot` | 完成 |
| `example-02.snapshot` | 可运行示例 DSL | `example-02.png` | 完成 |
| `example-02.png` | 400×240 独立渲染 | `example-02.snapshot` | 完成 |
| `handbook-03.snapshot` | 教学页 DSL | `handbook-03.png` | 完成 |
| `handbook-03.png` | 1200×1600 教学页 | `handbook-03.snapshot` | 完成 |
| `example-03.snapshot` | 可运行示例 DSL | `example-03.png` | 完成 |
| `example-03.png` | 400×240 独立渲染 | `example-03.snapshot` | 完成 |
| `handbook-04.snapshot` | 教学页 DSL | `handbook-04.png` | 完成 |
| `handbook-04.png` | 1200×1600 教学页 | `handbook-04.snapshot` | 完成 |
| `example-04.snapshot` | 可运行示例 DSL | `example-04.png` | 完成 |
| `example-04.png` | 400×240 独立渲染 | `example-04.snapshot` | 完成 |
| `sources.md` | 文档来源映射 | `-` | 完成 |
| `examples.json` | 示例/片段/插图对应 | `-` | 完成 |

- 四张 1200×1600 教学页 — 证据：四页尺寸正确，页码/章节/边距 48
- 每页至少一个小型 DSL 示例（8–18 行）及实际插图 — 证据：15/18/18/18 行；插图 400×240 与示例同源
- 插图用同一 DSL 构件直接画，不嵌入预渲染图 — 证据：页面内为 Container/Text/滤镜构件；无 Image
- 四份完整示例 DSL 与独立 400×240 PNG — 证据：example-01..04 各自 200
- 印刷片段与独立运行一致 — 证据：examples.json 记录 1-based 范围与逐字文本；像素差 0–6
- 正文≥24、代码≥20、边距 48 — 证据：正文 24、代码 20、页边距 48
- sources.md 与 examples.json — 证据：两文件完整；每条技术结论指向文档与示例

四页 1200×1600 手册，分别讲请求契约、根尺寸/有界布局、Raw/CDATA/富文本/alpha、滤镜与可复现交付。每页印刷一份 8–18 行真实示例，右侧放同一核心子树的 400×240 教学插图（1:1，不缩放、不换内容）；四份完整 DSL 单独渲染为 example-01..04。教学插图与独立示例的像素差为 0–6（仅边框/抗锯齿个别像素），examples.json 记录印刷行号、省略范围与核心子树。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应/错误 | handbook-01 |
| https://snapshot.muedsa.com/reference/parser-tags.md | 根尺寸/Expanded/Positioned/颜色/滤镜 | handbook-02..04 |
| https://snapshot.muedsa.com/guides/parser.md | CDATA/Raw/文本 | handbook-03 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A17/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A17/iterations.jsonl`
- 渲染请求总数：26；成功 24；失败 2；重试 2；DSL 版本 18
- 实际图片查看次数：8；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `40abc963650d` | `outputs/run-20261029-110525/A17/handbook-03.snapshot` | 2026-10-29T12:05:19+0800 / 7162ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-03.png` | 已查看 |
| `7c33ea3c57dd` | `outputs/run-20261029-110525/A17/handbook-01.snapshot` | 2026-10-29T12:05:19+0800 / 7777ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-01.png` | 已查看 |
| `cb9c0998c5be` | `outputs/run-20261029-110525/A17/handbook-02.snapshot` | 2026-10-29T12:05:19+0800 / 8362ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-02.png` | 已查看 |
| `ba376a0ad849` | `outputs/run-20261029-110525/A17/handbook-04.snapshot` | 2026-10-29T12:05:19+0800 / 9713ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-04.png` | 已查看 |
| `f6ef4036d5df` | `outputs/run-20261029-110525/A17/example-03.snapshot` | 2026-10-29T12:05:29+0800 / 1196ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-03.png` | 已查看 |
| `74f379a713e5` | `outputs/run-20261029-110525/A17/example-02.snapshot` | 2026-10-29T12:05:29+0800 / 1628ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-02.png` | 已查看 |
| `8eeae264bef1` | `outputs/run-20261029-110525/A17/example-04.snapshot` | 2026-10-29T12:05:29+0800 / 1639ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-04.png` | 已查看 |
| `72a91bb5120c` | `outputs/run-20261029-110525/A17/example-01.snapshot` | 2026-10-29T12:05:28+0800 / 2364ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-01.png` | 已查看 |
| `bb2116939845` | `outputs/run-20261029-110525/A17/handbook-02.snapshot` | 2026-10-29T12:05:45+0800 / 3885ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-02.png` | 已查看 |
| `17c2fff9cb34` | `outputs/run-20261029-110525/A17/handbook-01.snapshot` | 2026-10-29T12:05:45+0800 / 4289ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-01.png` | 已查看 |
| `37722a1408f6` | `outputs/run-20261029-110525/A17/handbook-03.snapshot` | 2026-10-29T12:05:45+0800 / 4839ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-03.png` | 已查看 |
| `daa39879faac` | `outputs/run-20261029-110525/A17/handbook-04.snapshot` | 2026-10-29T12:05:45+0800 / 4952ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-04.png` | 已查看 |
| `9c7040a50aa3` | `outputs/run-20261029-110525/A17/example-03.snapshot` | 2026-10-29T12:05:50+0800 / 1141ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-03.png` | 已查看 |
| `197b1cca158b` | `outputs/run-20261029-110525/A17/example-02.snapshot` | 2026-10-29T12:05:50+0800 / 1268ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-02.png` | 已查看 |
| `546290f35c2d` | `outputs/run-20261029-110525/A17/example-04.snapshot` | 2026-10-29T12:05:50+0800 / 1299ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-04.png` | 已查看 |
| `27bb73035026` | `outputs/run-20261029-110525/A17/example-01.snapshot` | 2026-10-29T12:05:50+0800 / 8520ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-01.png` | 已查看 |
| `7b5fa3719ddd` | `outputs/run-20261029-110525/A17/handbook-02.snapshot` | 2026-10-29T12:06:36+0800 / 1537ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-02.png` | 已查看 |
| `1e7f34bcd25b` | `outputs/run-20261029-110525/A17/handbook-01.snapshot` | 2026-10-29T12:06:36+0800 / 2485ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-01.png` | 已查看 |
| `e9aaae72ffbc` | `outputs/run-20261029-110525/A17/handbook-03.snapshot` | 2026-10-29T12:06:36+0800 / 2506ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-03.png` | 已查看 |
| `2bd407ecbd77` | `outputs/run-20261029-110525/A17/handbook-04.snapshot` | 2026-10-29T12:06:36+0800 / 75313ms | None / - | `outputs/run-20261029-110525/A17/handbook-04.png` | 失败响应已保留 |
| `0976cada4d11` | `outputs/run-20261029-110525/A17/handbook-04.snapshot` | 2026-10-29T12:07:53+0800 / 2389ms | 200 / image/png | `outputs/run-20261029-110525/A17/handbook-04.png` | 已查看 |
| `4d2b3147deb6` | `outputs/run-20261029-110525/A17/example-02.snapshot` | 2026-10-29T12:07:56+0800 / 885ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-02.png` | 已查看 |
| `bec668f49a63` | `outputs/run-20261029-110525/A17/example-01.snapshot` | 2026-10-29T12:07:56+0800 / 1177ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-01.png` | 已查看 |
| `765bd44b4264` | `outputs/run-20261029-110525/A17/example-04.snapshot` | 2026-10-29T12:07:56+0800 / 1805ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-04.png` | 已查看 |
| `6a2cd4bcdf64` | `outputs/run-20261029-110525/A17/example-03.snapshot` | 2026-10-29T12:07:56+0800 / 10698ms | None / - | `outputs/run-20261029-110525/A17/example-03.png` | 失败响应已保留 |
| `c94a1279196d` | `outputs/run-20261029-110525/A17/example-03.snapshot` | 2026-10-29T12:08:08+0800 / 1663ms | 200 / image/png | `outputs/run-20261029-110525/A17/example-03.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A17-v1 / baseline / - | 页1插图失去深色背景、页3出现实体、代码换行 |  | 核心容器显式背景、重写示例3、缩短示例4行 | 通过 | `tmp/run-20261029-110525/A17/drafts/gen_a17.py` |
| A17-v2 / visual / A17-v1 | 核对插图与示例 |  | 像素裁剪比对 | 差 0–6 | `outputs/run-20261029-110525/A17/handbook-03.snapshot` |
| visual | 教学插图背景丢失 | 核心 Container 透明，依赖 Snapshot 背景 | 给核心 Container 显式背景色 | 插图与示例像素一致 | `outputs/run-20261029-110525/A17/examples.json` |
| visual | 页3印刷出现 &lt; 实体 | T() 转义而 Parser 不解码 | 改写文案并重排 CDATA 示例 | 原字符显示 | `outputs/run-20261029-110525/A17/handbook-03.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A17/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T12:05:19+0800 / 2026-10-29T12:08:55+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 216.1 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 7.2 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 170.49 | 秒 | 客户端计时 |
| 成功/失败/重试 | 24 / 2 / 2 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 8 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

教学插图与独立示例必须同源同尺寸；本套用像素裁剪比对确认（最大差 6，仅 2 个像素），比只对函数名更可靠。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
