# Snapshot 使用情况说明与踩坑记录

- 任务ID：A13
- 任务名称：品牌标志到完整活动应用
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A13/`
- 临时目录：`tmp/run-20261029-110525/A13/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `symbol-color.snapshot` | 彩色图标 DSL | `symbol-color.png` | 完成 |
| `symbol-color.png` | 512 透明彩色 | `symbol-color.snapshot` | 完成 |
| `symbol-black.snapshot` | 纯黑图标 DSL | `symbol-black.png` | 完成 |
| `symbol-black.png` | 512 透明纯黑 | `symbol-black.snapshot` | 完成 |
| `brand-banner.snapshot` | 横幅 DSL | `brand-banner.png` | 完成 |
| `brand-banner.png` | 1200×400 横幅 | `brand-banner.snapshot` | 完成 |
| `launch-poster.snapshot` | 海报 DSL | `launch-poster.png` | 完成 |
| `launch-poster.png` | 1080×1350 海报 | `launch-poster.snapshot` | 完成 |
| `brand-system.json` | 品牌系统 | `-` | 完成 |
| `rationale.md` | 方向说明 | `-` | 完成 |

- 两个真正不同的预览并选择 — 证据：tmp previews A/B 均渲染查看；rationale 记录选择
- 彩色与纯黑 512 透明、几何相同、黑版 RGB=0 — 证据：两图同几何；黑版 alpha>0 像素 R=G=B=0，违规 0
- 图标≤6 主要构件、32×32 可识别 — 证据：4 构件；32px 预乘 Lanczos 预览与 4× 放大查看
- 横幅与海报指定文案、海报独立构图 — 证据：叠光/Layerlight/口号/日期/OPEN BETA/网址齐全
- 不能把图标 PNG 嵌进应用 — 证据：横幅与海报均由同一 icon 几何在 DSL 中重绘
- brand-system.json 与 rationale≤300 字 — 证据：两文件完整

先做两个 512×512 透明预览：A 三交叠圆环+中心点，B 三错位实心方片+负空间。实际查看后选 A；4 个主要构件（3 环+1 点），环宽 44、点 r34，32px 下仍保留三环轮廓。最终用同一几何生成彩色/纯黑图标、1200×400 横幅与 1080×1350 纵向海报；海报为独立构图，不是横幅缩放。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot、图片响应、错误处理 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Transform/ClipPath/border/圆角 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize/fontStyle/Raw/CDATA 与文本行高 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A13/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A13/iterations.jsonl`
- 渲染请求总数：13；成功 10；失败 3；重试 3；DSL 版本 7
- 实际图片查看次数：6；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `93d59485b641` | `tmp/run-20261029-110525/A13/previews/preview-b.snapshot` | 2026-10-29T11:51:36+0800 / 2099ms | 200 / image/png | `tmp/run-20261029-110525/A13/previews/preview-b.png` | 已查看 |
| `3be9184a354d` | `tmp/run-20261029-110525/A13/previews/preview-a.snapshot` | 2026-10-29T11:51:36+0800 / 65324ms | None / - | `tmp/run-20261029-110525/A13/previews/preview-a.png` | 失败响应已保留 |
| `d9618623b5ed` | `tmp/run-20261029-110525/A13/previews/preview-a.snapshot` | 2026-10-29T11:52:44+0800 / 5568ms | 200 / image/png | `tmp/run-20261029-110525/A13/previews/preview-a.png` | 已查看 |
| `7fe25244716c` | `outputs/run-20261029-110525/A13/symbol-black.snapshot` | 2026-10-29T11:52:59+0800 / 2742ms | 200 / image/png | `outputs/run-20261029-110525/A13/symbol-black.png` | 已查看 |
| `565904721e5f` | `outputs/run-20261029-110525/A13/brand-banner.snapshot` | 2026-10-29T11:52:59+0800 / 3101ms | 200 / image/png | `outputs/run-20261029-110525/A13/brand-banner.png` | 已查看 |
| `f6f3a183fc90` | `outputs/run-20261029-110525/A13/launch-poster.snapshot` | 2026-10-29T11:52:59+0800 / 4744ms | 200 / image/png | `outputs/run-20261029-110525/A13/launch-poster.png` | 已查看 |
| `f33ec9bd9b95` | `outputs/run-20261029-110525/A13/symbol-color.snapshot` | 2026-10-29T11:52:59+0800 / 5943ms | 200 / image/png | `outputs/run-20261029-110525/A13/symbol-color.png` | 已查看 |
| `9055de5214e1` | `outputs/run-20261029-110525/A13/brand-banner.snapshot` | 2026-10-29T11:53:28+0800 / 3499ms | 200 / image/png | `outputs/run-20261029-110525/A13/brand-banner.png` | 已查看 |
| `3196a7c7ebe3` | `outputs/run-20261029-110525/A13/symbol-color.snapshot` | 2026-10-29T11:53:28+0800 / 8233ms | 200 / image/png | `outputs/run-20261029-110525/A13/symbol-color.png` | 已查看 |
| `123cb945bcc1` | `outputs/run-20261029-110525/A13/symbol-black.snapshot` | 2026-10-29T11:53:28+0800 / 10678ms | None / - | `outputs/run-20261029-110525/A13/symbol-black.png` | 失败响应已保留 |
| `366853b9a004` | `outputs/run-20261029-110525/A13/symbol-black.snapshot` | 2026-10-29T11:53:41+0800 / 6631ms | 200 / image/png | `outputs/run-20261029-110525/A13/symbol-black.png` | 已查看 |
| `f48add6c21bd` | `outputs/run-20261029-110525/A13/launch-poster.snapshot` | 2026-10-29T11:53:28+0800 / 67222ms | None / - | `outputs/run-20261029-110525/A13/launch-poster.png` | 失败响应已保留 |
| `bdbd300bdb66` | `outputs/run-20261029-110525/A13/launch-poster.snapshot` | 2026-10-29T11:54:37+0800 / 5791ms | 200 / image/png | `outputs/run-20261029-110525/A13/launch-poster.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A13-v1 / baseline / - | 图标被 Positioning 约束裁切 |  | 按目标尺寸直接生成几何，不用 Transform 缩放 | 通过 | `tmp/run-20261029-110525/A13/drafts/gen_a13.py` |
| visual | 横幅/海报图标只显示四分之一 | Transform 子节点受 268 紧约束后再缩放 | icon 生成时按 size/512 缩放 | 图标完整 | `outputs/run-20261029-110525/A13/brand-banner.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A13/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:51:36+0800 / 2026-10-29T11:58:35+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 419.8 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 2.1 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 191.57 | 秒 | 客户端计时 |
| 成功/失败/重试 | 10 / 3 / 3 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 6 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

品牌几何用参数化 size 生成，避免对 512 图标做 Transform 缩放；32px 预览用预乘 Lanczos，黑版纯黑逐像素检查。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
