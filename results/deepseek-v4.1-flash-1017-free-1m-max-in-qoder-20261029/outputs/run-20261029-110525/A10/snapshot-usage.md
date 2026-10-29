# Snapshot 使用情况说明与踩坑记录

- 任务ID：A10
- 任务名称：透明合成与滤镜语义实验板
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A10/`
- 临时目录：`tmp/run-20261029-110525/A10/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `compositing-lab.snapshot` | 1440×1100 DSL | `compositing-lab.png` | 完成 |
| `compositing-lab.png` | 最终图 | `compositing-lab.snapshot` | 完成 |
| `composite-audit.json` | 像素与滤镜审计 | `-` | 完成 |

- 六格 320×240、3×2、间距≥32、说明在区外 — 证据：格原点 (200/560/920, 190/470)，间距 40；下方说明卡
- ①②重叠处 RGB 理论/实际与 128/255 vs 0.5 解释 — 证据：①(127,63,191) 采样一致；②(128,128,255) 实测(126,126,255)，误差≤2
- ③④仅改变模糊层、共用参数 — 证据：pair_sharing 记录；③文字清晰、④文字糊
- ⑤⑥共享场景与参数、⑥圆裁 — 证据：⑤无圆裁、⑥ ClipOval (160,120) r100；黄色形状跨圆周
- 说明文字≥20 — 证据：说明条 20px
- ③–⑥视觉判断引用实际图 — 证据：visual_checks 五条，含坐标与观察

1440×1100 六格实验板，3×2、320×240 白底。①②对照 alpha 与组 opacity；③④共用条纹+卡片场景，仅改变模糊作用层；⑤⑥共用 MULTIPLY+sigma6 场景，⑥额外 ClipOval r100。理论 alpha 计算与最终 PNG 像素采样写入 composite-audit.json。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 文本请求、图片响应、错误处理 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Transform/Container/Stack/Text/滤镜/裁剪属性 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、文本换行 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A10/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A10/iterations.jsonl`
- 渲染请求总数：3；成功 3；失败 0；重试 0；DSL 版本 3
- 实际图片查看次数：2；完整视觉迭代：0；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `d11329eeedd0` | `outputs/run-20261029-110525/A10/compositing-lab.snapshot` | 2026-10-29T11:38:45+0800 / 10344ms | 200 / image/png | `outputs/run-20261029-110525/A10/compositing-lab.png` | 已查看 |
| `2949b8ef7025` | `outputs/run-20261029-110525/A10/compositing-lab.snapshot` | 2026-10-29T11:40:09+0800 / 5044ms | 200 / image/png | `outputs/run-20261029-110525/A10/compositing-lab.png` | 已查看 |
| `76e9b47090b9` | `outputs/run-20261029-110525/A10/compositing-lab.snapshot` | 2026-10-29T11:40:35+0800 / 3418ms | 200 / image/png | `outputs/run-20261029-110525/A10/compositing-lab.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A10-v1 / baseline / - | 滤镜输出越出格子并遮挡标签 |  | 每格 ClipRect 限制 320×240 | 通过 | `tmp/run-20261029-110525/A10/drafts/gen_a10_v2.py` |
| visual | ⑤⑥模糊外溢、遮住标签 | ImageFiltered 输出边界扩展 | 单元格 ClipRect | 标签与格子边界恢复 | `outputs/run-20261029-110525/A10/compositing-lab.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A10/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:38:45+0800 / 2026-10-29T11:50:41+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 716.9 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 10.3 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 18.81 | 秒 | 客户端计时 |
| 成功/失败/重试 | 3 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 2 / 0 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

alpha 128/255 与 group opacity 0.5 的差异可被像素验证；BackdropFilter 与 ImageFiltered 的作用层差异必须用同一场景对照。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
