# Snapshot 使用情况说明与踩坑记录 — A06

任务ID：A06
任务名称：十四节点依赖图与反馈回路
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261104-145656-hy4all/A06/`
临时目录：`tmp/20261104-145656-hy4all/A06/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `dependency-map.png` | 1600×1000 依赖与反馈解释图 | `dependency-map.snapshot` | 完成；服务真实 PNG |
| `graph-audit.json` | 拓扑层、每节点入/出邻居与像素盒、16 条先决边路径与箭头、最长先决路径 11 节点、2 条反馈边折线路径 | — | 完成 |

14 个节点编号与中文标签完整，节点字号 22px、注释 18px；16 条 solid_edges 一律由左层指向右层、箭头方向可辨；2 条 feedback_edges（N09→N08、N10→N08）用洋红虚线并配专用图例，明确不参与 DAG 排序；N04→N13 长距先决边经底部绕行避免横穿节点文字；交叉无连接点不构成新依赖；图内解释“失败后回到构建”与“检查发现问题后修复”；graph-audit.json 给出 11 个拓扑层、最长先决路径（11 节点，允许多解）与每条反馈边表示位置。

**逐图自检证据**：实际打开 dependency-map.png 两次（v1、v2）。v1 发现两条反馈边说明文字压在虚线上、反馈箭头贴到节点上沿存在被节点遮挡的风险；v2 把说明改为右侧白色圆角标签块（不遮虚线）、箭头终点上移 8px，重渲染并再次打开实际 PNG：14 节点标签完整、16 条实线箭头均向右、两条洋红虚线与图例清晰、N04→N13 底部绕行不压文字、L0–L10 层标签齐全、两块底部说明卡文字完整。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | 请求体/响应类型/错误处理/字体查询/限流 | render.py、requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/Border | 本题全部 .snapshot |
| reference/parser-text.md | fontFamily、fontSize、fontStyle、textAlign、CDATA 文本 | 本题全部文字元素 |
| guides/examples.md | 固定画布 + Stack/Column 布局范式 | 本题布局骨架 |

Stack+固定画布；Positioned 绝对定位节点与路径；ClipPath 多边形绘箭头与线段；dashed_line 绘制反馈虚线；Container 圆角边框绘节点盒；Text 的 fontSize/fontStyle/textAlign；渐变头部。节点最后绘制，确保连线不压节点文字。全部由 DSL 构造。


## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A06/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A06/iterations.jsonl`
渲染请求总数：2
成功次数：2
失败次数：0
重试请求数：0
DSL版本数：2
实际图片查看次数：2
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `dependency-map.png (v1)` 发现：两条反馈说明压在虚线上、箭头贴节点上沿。改动：生成首版基线并查看。复查：记录 2 项缺陷。
- **v2**（visual，父版本 v1）：查看 `dependency-map.png (v2)` 发现：上述 2 项。改动：说明改为右侧白色圆角标签块并避开虚线区域；反馈箭头终点上移 8px。复查：重渲染并查看，2 项消除，拓扑与绕行保持不变。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 两条反馈说明压在虚线上、箭头贴节点上沿 | 实际渲染图观察 | 生成首版基线并查看 | 记录 2 项缺陷 |
| v2 / visual / v1 | 上述 2 项 | 实际渲染图观察；标签无底色且虚线与其同高 | 说明改为右侧白色圆角标签块并避开虚线区域；反馈箭头终点上移 8px | 重渲染并查看，2 项消除，拓扑与绕行保持不变 |

踩坑：节点在连线之后绘制可避免线条压文字，但箭头终点若恰落在节点边界会被节点覆盖，需上移数像素；反馈边必须与实线用颜色+虚线双重区分，并显式标注不参与 DAG。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A06/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T15:45:52+08:00 → 2026-11-04T15:57:10+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 9.434 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 2 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 2 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

以最长前驱链计算 11 个拓扑层并从左到右排列，同层上下表示可并行；长距先决边走底部通道；反馈边走顶部双通道并以洋红虚线表示，配合右侧图例与底部解释卡把“返工”语义说清，避免读者把虚线误当作先决依赖。

最终图与 graph-audit.json 一致：14 节点、16 先决边、2 反馈边、11 个拓扑层、最长路径 11 节点；所有元素实际查看无遮挡，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
