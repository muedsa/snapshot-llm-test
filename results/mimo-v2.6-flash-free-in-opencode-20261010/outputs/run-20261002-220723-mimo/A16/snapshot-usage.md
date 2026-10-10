# A16 数据取证修正 — snapshot 使用记录

- run_id: `run-20261002-220723-mimo`
- 服务: `POST https://open-snapshot.muedsa.com/snapshot`，UTF-8 纯文本正文，`Content-Type: text/plain; charset=utf-8`
- 时间窗: 任务开始 `2026-10-03T20:35:47+08:00`，首个请求 `2026-10-03T13:03:41.778Z`，末个请求 `2026-10-04T06:22:03.298Z`
- 本题请求: **4 次**（渲染 **3** 次 + 文档 **1** 次），HTTP 200 **4** 次，**0 失败 / 0 重试 / 0 限流**，请求耗时合计 **16547.4 ms**
  （渲染 15130.0 ms，文档 1417.4 ms）
- 交付: `corrected-report.png` + `corrected-report.snapshot`（1280×900，原始服务字节）、`findings.json`、`corrected-data.json`、
  `snapshot-usage.md`、`task-metrics.json`

## 实际读取的资料

| 资料 | 来源 | 用途 |
| --- | --- | --- |
| `tasks/A16-visual-data-forensics/{TASK.md,AGENTS.md,task.json}` | 题库 | 取证口径、"图与源码都不是答案"、`正文≥22 / 标注≥18`、交付清单 |
| `inputs/source.csv` | 题库 | **唯一可信原始数据**：Q1 120/90、Q2 135/108、Q3 128/96、Q4 180/126 |
| `inputs/flawed-report.png` | 题库 | **仅供观察**：全尺寸打开 + 四个像素探针采样，未裁块、未描图、未嵌入 |
| `run-config.json`、`catalog.json` | 总根 | 服务地址覆盖子题默认值、task_order |
| `GET /fonts` 列表 | `tmp/.../A11/fonts-0001.txt`（套件共享请求，复用未重发） | 从**真实**列表中确认 `Inter`、`Noto Sans CJK SC` 确实存在 |
| DSL 参考字节 | `tmp/.../A15/doc-parser-tags.html`、`doc-container-widget.html`（同 run 已留存，复用未重发） | 经 `tmp/.../A16/doc-excerpts.md` 抽取本题真正用到的属性名 |

## 本题新增的真实文档请求（1 次）

| 请求 | 状态 | 耗时 | 字节 | 实际用于 |
| --- | --- | --- | --- | --- |
| `GET https://open-snapshot.muedsa.com/ai-guide.md` | 200 | 1417.4 ms | 3718 | 请求体是 UTF-8 **纯文本而非 JSON**、响应是 PNG 二进制、错误 JSON 形状（`code/message/requestId`）、`429` 要看 `Retry-After`、`fontFamily` 必须是逗号分隔且取自 `GET /fonts`、**不要臆造标签与属性** |

该文档在本题先用 harness 的 `webfetch` 实际读过一遍（`webfetch` 不暴露状态码/耗时/字节），随后重新抓取一次，
以便把源文件留存在 `tmp/.../A16/doc-ai-guide.md` 并记录可测字段；`requests.jsonl` 的 `note` 已如实写明这一点。
DSL 标签参考沿用同 run 已留存的字节，**按套件约定只复用、不重复计为新 HTTP 请求**，复用来源写在 `doc-excerpts.md` 开头。

## 用到的标签能力

| 能力 | 本题用法 |
| --- | --- |
| `Snapshot` | 1280×900 根节点，`type="png"` |
| `Stack` + `Positioned` | 全部文本与矩形的绝对定位；`Stack` 持有 `Positioned`（遵守"Stack owns Positioned"） |
| `Container` | 三张卡片（1184×436 / 700×256 / 465×256）、8 根柱、5 条网格线、8 块数值标签白垫、图例色块、Q4 下划线、分隔线 |
| `Container` 圆角与描边 | 卡片 `r12` + 1px 描边、数值标签白垫 `r4`、下划线 `r2` |
| `Text` | `fontSize` **22 → 40**（最小值 22，同时满足"正文≥22"与"标注≥18"两种读法）、`fontFamily="Inter,Noto Sans CJK SC"`、`color`、`fontStyle` |
| 颜色 | 全部 `#RRGGBB`；服务返回 `image/png` |

**没有用到** `Image`、`Transform`（交付 DSL 中两者计数为 0），因此不存在外部素材、整图嵌入或整体缩放。

## 取证方法（不是"看一眼列坑"）

1. **先打开 `flawed-report.png`**，再用四个 `System.Drawing` 探针在同一张图上量出：
   图表卡 `x56 y157 w1168 h463`、利润卡 `x56 y651 w758 h170`、重点卡 `x843 y650 w382 h172 fill #FFF1D9`、
   网格线 `y=295/349/403/457/511/565`（标签 200..100，2.70 px/单位）、8 根柱底全部 `y=564`、
   蓝/橙柱高 `150/172/198/246` 与 `110/135/128/165` px、图例色块与文字位置、全部文字墨迹框。
2. **拿量到的现象逐条对 `source.csv`**：只有能被数据证伪的才写成 `finding`。
3. **不能证伪的一律进 `uncertain`**：配色、图例顺序、标签摆放——数据里没有样式字段，凭观感判错就是编。
4. **重算而非抄**：`gen.ps1` 从 CSV 现算利润、利润率、成本率、全年合计与柱高几何，
   并在发射前断言 `key_quarter == argmax(profit) == argmax(margin) == argmax(revenue) == argmin(cost_rate)`，数据一变就直接抛错。
5. **量真实服务返回的 PNG**（不是量 DSL）：`verify-render.ps1` 找网格线行，再按列**自底向上取连续段**，
   从而排除浮在柱顶上方的彩色数值标签。

## 8 条 finding 与 3 条 uncertain（严格分池）

| 池 | 数量 | ID | 判据 |
| --- | --- | --- | --- |
| 数值错误 | 2 | F01 利润明细 Q3=42（实为 32）、F02 标题"Q3利润最高"（实为 Q4 54） | 与 `source.csv` 计算结果直接冲突 |
| 被数据证伪的断言 | 3 | F03 副标题"收入持续上升"（Q3 环比 −7）、F04 重点卡论据、F07 图例颜色语义与柱上数据列相反 | 可复算反驳 |
| 几何/比例错误 | 2 | F05 轴截断在 100 且下界高于 90/96 两点、F06 八根柱 1.222~1.547 px/单位（26.6% 离散） | 像素测量 |
| 可追溯性缺口 | 1 | F08 结论层讲利润，主图区无利润编码 | 结论无法在图上自证 |
| **uncertain** | 3 | U01 配色、U02 图例顺序、U03 标签摆放与字号 | `confirmed_error=false`，**不并入数值错误计数** |

`2+3+2+1 = 8 = findings_total`，各归且仅归一类；每条都带 `image_location / phenomenon / source_check / impact / correction / final_view_result` 六字段。

## 视觉迭代（3 轮渲染，4 个靠看图发现的真实缺陷）

| 轮 | DSL | 结果 | 触发 → 改动 |
| --- | --- | --- | --- |
| r01 | v01 | 200 / 7020.6 ms | 首个可用图；几何检查已全绿 |
| — | — | — | **打开 v01** → 见下 3 项 |
| r02 | v02 | 200 / 4285.3 ms | 利润注解改写、重点卡正文 `left 795→811`、删除多余的 1184×1 细线 |
| — | — | — | **打开 v02** → 见下第 4 项 |
| r03 | v03 | 200 / 3824.1 ms | 加 8 块白色 `r4` 白垫 → **交付版** |

### 看图发现的缺陷（不是像素统计告诉我的）

1. v01 利润注解写成「利润 − 收入与成本之差，取自 source.csv」——这不是定义。
2. v01 重点卡三行正文 `left=795`，而卡标题与利润卡注解都在 `left=811`，整块比自己的标题缩进少 16px。
3. v01 副标题下有一条 1184×1 细线，紧挨卡片边缘形成第二条通栏线，纯噪音。
4. v02 数值标签浮在柱外，网格线从数字中穿过——最明显是 Q1 成本标签 `90` 正好压在 y=376 的 100 网格线上。

### 测量发现、肉眼看不见的部分

- 三次测量（`verify-v01`、`verify-v03`、`probe-final`）**全部全绿，没有发现看图漏掉的缺陷**：
  5 条网格线 y=236/306/376/446/516 等距 70px、8 根柱底全部 y=515 贴 0 线、
  8 根柱 1.3958~1.4000 px/万元（离散 **0.30%**，对照原图 **26.6%**）、按轴读回最大误差 **0.29 万元**。
- 12 条文本行对卡片边最小留白：左 **26px**、右 **29px**、下 **15px**，无一触边或溢出。

## 实际遇到的问题与修复

1. **`mk-findings.ps1` 把裸函数调用当 `+` 的操作数** → `You must provide a value expression following the '+' operator`；
   改写为 `(F2 (...))`，随后 grep 全脚本确认没有其它裸操作数。
2. **`probe-final.ps1` 第一版报"找不到任何卡片"** —— 它在 `y=700` 做游程判定，而那一行正好穿过「全年合计」的字形，
   白色游程被每个汉字打断，永远达不到 200px 阈值。用调试计数（`nStart=34, found=0`）抓出来，
   改成在**无字形行**上取首尾匹配像素。**教训与 A15 相同：报"空集"的校验器先怀疑它根本没跑对。**
3. **行内 `powershell -Command` 被外层 shell 展开 `$b/$f/$w/$h` 两次** → `ScriptBlock should only be specified as a value of the Command parameter`；
   两次都改成先写 `.ps1` 再用 `-File` 执行。
4. **看图通道对 3 个从未打开过的裁剪路径返回旧帧**（每次都回一张之前的整页图）。
   `pnginfo.ps1` 证明磁盘上的裁剪本身是对的（1180×105 / 1170×80 / 660×340 / 590×340 / 730×270 / 480×270）。
   三次重试失败后**不再自称做过放大检查**，改为把 6 张裁剪交给独立子代理逐行转录并对照 `source.csv`；
   该子代理复现了同一故障，用字节不同的重编码绕开，最终报告"无重叠、无截断、无错位、无一个数字与源数据不符"。

**没有遇到任何 HTTP 错误**（4/4 全 200，`ratelimit_remaining` 始终 119），因此本题不存在重试、429 或 Retry-After；如实记录为 0 而非省略。

## 逐图自检（真实开图，本会话 8 次 + 独立复核 6 次）

| 视图 | 次数 | 看到什么 |
| --- | --- | --- |
| `flawed-report.png` 全尺寸 | 1 | 标题/副标题/图例/截断轴/Q3=42 与探针结果一致 |
| `corrected-report-v01.png` 全尺寸 | 1 | 结构正确 → 触发 3 项文字与对齐修正 |
| `corrected-report-v02.png` 全尺寸 | 1 | 数值被网格线穿过 → 触发白垫 |
| `corrected-report-v03.png` 全尺寸 | 1 | `90` 已把 100 网格线断开，标题、四季柱、图例、利润明细、Q4 重点卡齐备 |
| 3 个裁剪路径的开图事件 | 3 | **全部返回旧帧**，0 个可用画面；如实计为开图事件而非有效放大 |
| **交付文件 `outputs/.../corrected-report.png`** | **1** | 与 v03 同为 SHA-256 `F4AE7030…37332`，1280×900，逐字复核全部数字 |
| 独立子代理读 6 张裁剪 | 6 | 逐行转录 + 用 `source.csv` 验算，报告无缺陷 |

- **1 张交付 PNG 已用真实图像工具打开**，没有用接触表代替，也没有只看像素统计冒充看图。
- 所有观察图（`zoom-*-v03.png`、`view-A16-*`）都裁自**本作品自己的** PNG，只存 `tmp/` 作观察用，非交付物、不含输入像素。
- 输入图的局部检查走**像素探针**而非裁图，因为题目明令禁止裁块。
- 本题看图通道**确实出现旧帧**，因此没有拿模糊记忆当放大证据，而是交给独立复核并把双方开图次数分开统计。

## 修正后的几何（全部由数据推出）

- y 轴 `0..200`，刻度 `0/50/100/150/200`，**1.4 px/万元**，baseline `y=516`，绘图区顶 `y=236`，
  网格线 `y=236/306/376/446/516`（等距 70px）。
- 四组中心 `272/536/800/1064`，柱宽 74、组内间距 16，**8 根柱底全部 y=515**。
- 最小值 90 > 0，因此八根柱全部可被这根轴表示（原图的 100 起点做不到）。
- 重点季度由断言选出：`Q4 = {利润 54 最高, 利润率 30.0% 最高, 收入 180 最高, 成本率 70.0% 最低}`，
  全年 `563 / 420 / 143 / 25.4%`。

## 文件路径

| 用途 | 路径 |
| --- | --- |
| 最终图 + DSL | `outputs/run-20261002-220723-mimo/A16/corrected-report.png`、`corrected-report.snapshot` |
| 取证结论 | `outputs/run-20261002-220723-mimo/A16/findings.json` |
| 派生数据与坐标定义 | `outputs/run-20261002-220723-mimo/A16/corrected-data.json` |
| 使用记录 / 指标 | `outputs/run-20261002-220723-mimo/A16/snapshot-usage.md`、`task-metrics.json` |
| 请求 / 迭代日志 | `tmp/run-20261002-220723-mimo/A16/requests.jsonl`（4 行）、`iterations.jsonl`（16 行） |
| 生成与测量工具 | `tmp/run-20261002-220723-mimo/A16/{gen,verify-render,probe-final,zoom,pnginfo,check-dsl,check-findings,check-logs,mk-findings,mk-metrics,doc-excerpts,fetch-docs}.ps1` |
| 原图四个探针 | `tmp/run-20261002-220723-mimo/A16/probe-flawed{,-axis,-boxes,-callout}.ps1` 及其 `.json` |
| 各版 DSL 与渲染 | `tmp/run-20261002-220723-mimo/A16/corrected-report-v01..v03.snapshot`、`corrected-report-v01..v03.png` |
| 校验输出 | `tmp/run-20261002-220723-mimo/A16/verify-v01.json`、`verify-v03.json`、`probe-final.txt` |
| 观察图与独立复核脚本 | `tmp/run-20261002-220723-mimo/A16/zoom-*.png`、`view-A16-*`、`qa-*.{png,jpg,gif}`、`serve-qa.ps1`、`qa-bars.ps1`、`qa-text*.ps1` |
| 留存文档 | `tmp/run-20261002-220723-mimo/A16/doc-ai-guide.md`、`doc-excerpts.md` |

## 未解决事项

- **看图通道的旧帧故障没有根治**：本会话 3 次裁剪开图返回旧帧，已如实计为"开图事件 0 可用画面"，
  并改由独立复核完成放大检查；若下题仍复现，按同样方式处理，**不拿像素统计代替看图**。
- **输入图的全尺寸打开发生在证据收集阶段而非探针之前**：四条探针先跑、结论先由测量得出，
  `findings.json` 落盘前又对这张全尺寸图逐条复核了一遍；已写进 `task-metrics.json` 的 `open_issues`，不掩饰顺序。
- 无阻塞事项：4 次请求全部成功，全部 16 项校验通过，8 条 finding 与 3 条 uncertain 全部落盘。
