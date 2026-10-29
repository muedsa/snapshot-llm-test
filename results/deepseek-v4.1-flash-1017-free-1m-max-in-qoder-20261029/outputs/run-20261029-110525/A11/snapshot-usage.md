# Snapshot 使用情况说明与踩坑记录

- 任务ID：A11
- 任务名称：文字保真与跨页结算单
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A11/`
- 临时目录：`tmp/run-20261029-110525/A11/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `invoice-page-01.snapshot` | 第 1 页 DSL | `invoice-page-01.png` | 完成 |
| `invoice-page-01.png` | 结算与明细 | `invoice-page-01.snapshot` | 完成 |
| `invoice-page-02.snapshot` | 第 2 页 DSL | `invoice-page-02.png` | 完成 |
| `invoice-page-02.png` | 说明与原样文字 | `invoice-page-02.snapshot` | 完成 |
| `invoice-audit.json` | 金额与字面审计 | `-` | 完成 |
| `text-map.json` | 段落位置与字体 | `-` | 完成 |

- 两页 1200×1600、编号/页眉/页码一致 — 证据：页码 01/02、02/02；编号一致
- 四行 SKU/名称/数量/单价/行金额与汇总 — 证据：805.50/478.80/1,160.00/1,680.00；小计 4,124.30
- 严格计税顺序与定点四舍五入 — 证据：折扣后 3,944.30；税 236.66；运费 35.00；应付 4,215.96
- 金额小数点列对齐 — 证据：所有金额两位小数、右对齐
- notes 与 literal_lines 逐字符保真 — 证据：CDATA；批次双空格、路径反斜杠、A<B&C>D 均原样
- PAID / 已结算富文本共基线、不改应付 — 证据：嵌套 Text + Raw 斜线；应付仍 4,215.96
- 正文≥24、脚注≥20、边距 48 — 证据：正文 24、说明 20、边距 48
- invoice-audit.json 与 text-map.json — 证据：两文件完整

两页 1200×1600 结算单。第 1 页展示双方、编号/日期/币种、四行明细、五步计税顺序与应付；金额用 Decimal 定点、ROUND_HALF_UP 至分，列右对齐。第 2 页四条 notes 与四条 literal_lines 用 CDATA 原样排版，保留双空格、反斜杠与尖括号；PAID / 已结算为嵌套 Text 富文本，斜线用 Raw 保留空格。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 文本请求、图片响应、错误处理 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Transform/Container/Stack/Text/滤镜/裁剪属性 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、文本换行 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A11/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A11/iterations.jsonl`
- 渲染请求总数：8；成功 7；失败 1；重试 1；DSL 版本 6
- 实际图片查看次数：4；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `5e73461bc683` | `outputs/run-20261029-110525/A11/invoice-page-02.snapshot` | 2026-10-29T11:41:41+0800 / 3585ms | 200 / image/png | `outputs/run-20261029-110525/A11/invoice-page-02.png` | 已查看 |
| `b52f5faede3a` | `outputs/run-20261029-110525/A11/invoice-page-01.snapshot` | 2026-10-29T11:41:41+0800 / 3769ms | 200 / image/png | `outputs/run-20261029-110525/A11/invoice-page-01.png` | 已查看 |
| `e0db49bea3a3` | `outputs/run-20261029-110525/A11/invoice-page-01.snapshot` | 2026-10-29T11:42:20+0800 / 3208ms | 200 / image/png | `outputs/run-20261029-110525/A11/invoice-page-01.png` | 已查看 |
| `da1bde547ebe` | `outputs/run-20261029-110525/A11/invoice-page-02.snapshot` | 2026-10-29T11:42:20+0800 / 65251ms | None / - | `outputs/run-20261029-110525/A11/invoice-page-02.png` | 失败响应已保留 |
| `3ff80c259411` | `outputs/run-20261029-110525/A11/invoice-page-02.snapshot` | 2026-10-29T11:43:28+0800 / 2611ms | 200 / image/png | `outputs/run-20261029-110525/A11/invoice-page-02.png` | 已查看 |
| `5b25bcfcd14b` | `outputs/run-20261029-110525/A11/invoice-page-02.snapshot` | 2026-10-29T11:43:49+0800 / 1527ms | 200 / image/png | `outputs/run-20261029-110525/A11/invoice-page-02.png` | 已查看 |
| `6d0d5b61459a` | `outputs/run-20261029-110525/A11/invoice-page-01.snapshot` | 2026-10-29T11:43:49+0800 / 2983ms | 200 / image/png | `outputs/run-20261029-110525/A11/invoice-page-01.png` | 已查看 |
| `3ad9b69bcf48` | `outputs/run-20261029-110525/A11/invoice-page-02.snapshot` | 2026-10-29T11:44:08+0800 / 3941ms | 200 / image/png | `outputs/run-20261029-110525/A11/invoice-page-02.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A11-v1 / baseline / - | 实体转义与金额换行 |  | CDATA SKU、金额宽度/字号 | 通过 | `tmp/run-20261029-110525/A11/drafts/gen_a11.py` |
| A11-v2 / visual / A11-v1 | &amp; 与斜线空格 |  | 改文案、Raw 斜线 | 通过 | `outputs/run-20261029-110525/A11/invoice-page-02.snapshot` |
| visual | SKU A<B&C>D 被转义为实体 | T() 对 &<> 做 HTML 转义而 Parser 不解码实体 | TRaw 使用 CDATA | 页面显示原字符 | `outputs/run-20261029-110525/A11/invoice-page-01.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A11/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:41:41+0800 / 2026-10-29T11:50:42+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 541.2 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 3.6 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 86.88 | 秒 | 客户端计时 |
| 成功/失败/重试 | 7 / 1 / 1 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 4 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

Parser 不做实体解码；含 <、& 的文本必须 CDATA。金额对齐用固定宽度右对齐+两位小数即可。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
