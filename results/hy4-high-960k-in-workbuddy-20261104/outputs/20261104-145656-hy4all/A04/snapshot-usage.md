# Snapshot 使用情况说明与踩坑记录 — A04

任务ID：A04
任务名称：分组改善与总体下降的数据解释
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/20261104-145656-hy4all/A04/`
临时目录：`tmp/20261104-145656-hy4all/A04/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `conversion-story.png` | 1600×1000 转化率悖论信息图 | `conversion-story.snapshot` | 完成；服务真实 PNG |
| `analysis.json` | 四个分组精确分数/显示百分比、两期加权公式与构成、图轴定义、结论与因果限制 | — | 完成 |

展示两期×两渠道的四个精确分数：前期直接 2400/8000=30.00%、前期推广 200/2000=10.00%、后期直接 700/2000=35.00%、后期推广 960/8000=12.00%；总体前期 2600/10000=26.00%、后期 1660/10000=16.60%（总成交÷总访问，不平均渠道比例）。三图：① 共用 0–100% 尺度的渠道分组率柱图；② 每期等长 390px、分段按真实占比（80/20 → 20/80）的访问构成堆叠图；③ 总体 26.00%→16.60% 对照并给出加权公式与错误口径均值 20.00%→23.50% 的反例。底部小表列出全部原始分子/分母，深色卡给出由数据支持的主结论与“不能由该数据证明因果”的限制说明。正文≥22、图标注≥18。

**逐图自检证据**：实际打开 conversion-story.png 两次（v1、v2）。v1 发现率图轴单位与 100% 刻度相压、构成图 20% 窄分段标签被截断、表格首列渠道名被裁、结论正文末行压到限制小框、总体面板加权与错误口径均值间距不足；v2 删除轴单位标签、窄分段改用短百分比并补充颜色说明、首列缩短为“前期 直接”等、结论精简为三行、加权说明上移，重渲染并再次打开实际 PNG：三面板文字完整、构成图 80%/20% 分段清晰、6 行核对表对齐、结论与限制框分离、底部脚注完整。

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

Stack+固定画布绝对定位；Container 的 color/borderRadius/border 绘卡片与柱体；ClipPath 路径绘斜向趋势线（本题未用）；Text 的 fontSize/fontStyle/textAlign/maxLines/overflow 与 CDATA；渐变头部；c.bar/c.rect/c.text 组合三图。全部由 DSL 构造。


## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A04/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A04/iterations.jsonl`
渲染请求总数：2
成功次数：2
失败次数：0
重试请求数：0
DSL版本数：2
实际图片查看次数：2
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `conversion-story.png (v1)` 发现：轴单位与100%刻度重叠、20%窄分段标签截断、表格首列裁切、结论末行压限制框、加权说明与均值贴在一起。改动：生成首版基线并查看。复查：记录 5 项缺陷，进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `conversion-story.png (v2)` 发现：上述 5 项。改动：删除轴单位标签；窄分段显示 20% 并补颜色图例；表格首列缩短；结论精简为 3 行；加权说明上移 2px。复查：重渲染并再次查看，5 项缺陷全部消除，数值与 analysis.json 一致。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 轴单位与100%刻度重叠、20%窄分段标签截断、表格首列裁切、结论末行压限制框、加权说明与均值贴在一起 | 实际渲染图观察 | 生成首版基线并查看 | 记录 5 项缺陷，进入视觉迭代 |
| v2 / visual / v1 | 上述 5 项 | 实际渲染图观察；固定宽度标签未考虑窄分段与中文换行行数 | 删除轴单位标签；窄分段显示 20% 并补颜色图例；表格首列缩短；结论精简为 3 行；加权说明上移 2px | 重渲染并再次查看，5 项缺陷全部消除，数值与 analysis.json 一致 |

踩坑：堆叠图的窄分段（20%×390=78px）容不下“推广访问 20%”，需按实际像素宽度切换短标签；中文结论卡的 22px 文本按约 30 字/行估算，必须给限制框留足 120px 以上。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A04/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T15:45:52+08:00 → 2026-11-04T15:57:09+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 14.575 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 2 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 2 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

三图从左到右分别呈现“分组改善 → 构成转移 → 总体下降”，用相同的蓝/橙渠道配色把三图关联起来，结论放在右下而非图上方，避免结论先行；把错误口径（平均比例）并列展示以说明为何不能只看平均。

最终图逐项核对四个精确分数、两期加权式、0–100% 共用尺度、等长构成图与因果限制说明，全部可读且无遮挡，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
