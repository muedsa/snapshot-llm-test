# Snapshot 使用情况说明与踩坑记录

- 任务ID：A19
- 任务名称：构造可核验的视觉题场
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A19/`
- 临时目录：`tmp/run-20261029-110525/A19/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `grid-scene.snapshot` | 网格 DSL | `grid-scene.png` | 完成 |
| `grid-scene.png` | 1600×1600 题场 | `grid-scene.snapshot` | 完成 |
| `occlusion.snapshot` | 遮挡 A DSL | `occlusion.png` | 完成 |
| `occlusion.png` | 800×800 A | `occlusion.snapshot` | 完成 |
| `occlusion-alternative.snapshot` | 遮挡 B DSL | `occlusion-alternative.png` | 完成 |
| `occlusion-alternative.png` | 800×800 B | `occlusion-alternative.snapshot` | 完成 |
| `scene-data.json` | 种子/频数/几何 | `-` | 完成 |
| `questions.json` | 14 题 | `-` | 完成 |
| `answers.json` | 答案与方法 | `-` | 完成 |
| `equivalence.json` | 遮挡像素等价 | `-` | 完成 |

- 1600×1600、8×8、G01–G64、每格一个主体 — 证据：grid-scene.png；64 对象
- 4 色/4 形各 16、全组合覆盖、每色每形三尺寸 — 证据：scene-data.json 频数与组合
- 每行≥3 色≥3 形、圆环内径一半、编号外置 — 证据：scene-data rows；ring 厚度 0.25×外径
- 12 题覆盖复合/关系/距离/排序/包围框/计数，≥4 两步 — 证据：questions.json Q1–Q12
- 遮挡 A/B 可见相同、隐藏不同、不能虚线泄漏 — 证据：equivalence.json 像素差 0；隐藏位于不透明板内
- 2 道遮挡题，至少 1 题答案“无法确定” — 证据：OQ1 无法确定；OQ2 可见橙圆 1
- scene/questions/answers/equivalence 四 JSON — 证据：四文件完整

8×8 网格 64 对象，固定种子 0 的平衡分配：4 色×4 形各 16、16 组合全覆盖、每色/每形含 48/64/80、每行≥3 色≥3 形；圆环内径为外径一半。另做 800×800 遮挡 A/B：可见前景相同，隐藏内容不同且完全被不透明板覆盖，两 PNG 像素数组完全相同。12+2 题与答案/方法/坐标容差写入 JSON。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 渲染接口与错误 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform | 全部布局 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A19/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A19/iterations.jsonl`
- 渲染请求总数：5；成功 5；失败 0；重试 0；DSL 版本 5
- 实际图片查看次数：4；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `98b29164f42d` | `outputs/run-20261029-110525/A19/occlusion-alternative.snapshot` | 2026-10-29T12:12:05+0800 / 1649ms | 200 / image/png | `outputs/run-20261029-110525/A19/occlusion-alternative.png` | 已查看 |
| `c83f00bb2b12` | `outputs/run-20261029-110525/A19/occlusion.snapshot` | 2026-10-29T12:12:05+0800 / 1773ms | 200 / image/png | `outputs/run-20261029-110525/A19/occlusion.png` | 已查看 |
| `845a1b9d6891` | `outputs/run-20261029-110525/A19/grid-scene.snapshot` | 2026-10-29T12:12:05+0800 / 3765ms | 200 / image/png | `outputs/run-20261029-110525/A19/grid-scene.png` | 已查看 |
| `355b60e87ba7` | `outputs/run-20261029-110525/A19/grid-scene.snapshot` | 2026-10-29T12:12:29+0800 / 3066ms | 200 / image/png | `outputs/run-20261029-110525/A19/grid-scene.png` | 已查看 |
| `2dfc123af59b` | `outputs/run-20261029-110525/A19/grid-scene.snapshot` | 2026-10-29T12:12:44+0800 / 2841ms | 200 / image/png | `outputs/run-20261029-110525/A19/grid-scene.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A19-v1 / baseline / - | 形状偏移 160px |  | shape 坐标减网格原点 | 通过 | `tmp/run-20261029-110525/A19/drafts/gen_a19.py` |
| A19-v2 / visual / A19-v1 | 圆环内径不是一半 |  | 环厚 0.25×外径 | 通过 | `outputs/run-20261029-110525/A19/grid-scene.snapshot` |
| visual | 64 对象错位/空格 | 形状使用页面坐标放入网格 Stack | 减网格原点 | 64 格全部有对象 | `outputs/run-20261029-110525/A19/grid-scene.png` |
| visual | 圆环内径不为一半 | 环厚 18% | 25% 外径 | 内径=外径/2 | `outputs/run-20261029-110525/A19/grid-scene.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A19/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T12:12:05+0800 / 2026-10-29T12:15:28+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 203.3 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 1.6 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 13.09 | 秒 | 客户端计时 |
| 成功/失败/重试 | 5 / 0 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 4 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

遮挡等价要做到可见层与渲染参数完全一致、隐藏层不外溢；同字节 PNG 是更强证据但不是要求。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
