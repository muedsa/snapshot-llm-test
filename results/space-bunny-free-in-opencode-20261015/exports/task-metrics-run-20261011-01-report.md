# Snapshot 总任务指标复核:`run-20261011-01` 的 task-metrics

- **数据来源**:[../outputs/run-20261011-01/_suite/task-metrics.json](../outputs/run-20261011-01/_suite/task-metrics.json)(`schema_version 1`,`path_base = suite_root`,`generated_at = 2026-10-15T09:24:35+08:00`)
- **范围**:本报告只分析这一个文件里的 `totals`、30 条 `per_task` 记录和两条说明字段。为解释 A21/A22 的空 `counts`,另读了这两题的题级与轮次级 task-metrics,仅用于第 5 节第 2 条;其他题目一律只引用本文件的数值。
- **复核方式**:逐项重加,脚本 [../tmp/run-20261011-01/_suite/scripts/analyze_suite_metrics.py](../tmp/run-20261011-01/_suite/scripts/analyze_suite_metrics.py)
- **一句话结论**:图片类指标(125/125)和看图次数(322)与明细自洽;`totals.requests = 518` 和 `totals.requests_ok = 390` 只累加了 8 行,漏掉另外 20 行的 398/323 次,实际应为 **916 / 713**。

## 1. 文件里其实有三套计数口径

`per_task` 的 30 行按 `counts` 的字段名分成三组,这直接决定了第 2 节的差额。

| 组 | 字段名风格 | 题目 | 行数 | 图片 |
| --- | --- | --- | --- | --- |
| S1 | `snapshot_requests` / `successful_snapshot_requests` / `failed_snapshot_requests` / `dsl_versions` / `completed_visual_iterations` | A01–A20 | 20 | 45 |
| S2 | `requests` / `requests_ok` / `requests_failed` / `renders` / `cases` / `visual_iteration_rounds` | A23、A24、B01–B06 | 8 | 71 |
| S0 | `counts` 为空对象 `{}` | A21、A22 | 2 | 9 |

S1 独有:`dsl_versions`、`retry_requests`、`other_service_requests`、`incomplete_visual_iterations`。
S2 独有:`renders`、`cases`、`distinct_images`(仅 A23)、`solver_runs`(仅 A24)、`web_retrievals*`(仅 B04)。
两组共有的只有 `image_views` 和 `requests` 类三个语义相同但名字不同的计数。

## 2. `totals` 复核:两项少计,三项自洽

| 指标 | 文件声明 | 明细重加(28 行有 counts 的) | 差额 | 判定 |
| --- | --- | --- | --- | --- |
| `images` | 125 | 125(30 行全部) | 0 | 一致 |
| `images_with_dsl` | 125 | 125 | 0 | 一致,且每题 `images == images_with_dsl` |
| `requests` | 518 | **916** = S1 398 + S2 518 | **−398** | 少计整 20 行 S1 |
| `requests_ok` | 390 | **713** = S1 323 + S2 390 | **−323** | 同上 |
| `image_views` | 322 | 322 = S1 217 + S2 105 | 0 | 一致(两组字段同名,所以被正确累加) |

差额来源可以精确复现,不是四舍五入或口径模糊:

- 518 = A23 31 + A24 12 + B01 82 + B02 33 + B03 247 + B04 37 + B05 40 + B06 36,即**只有 S2 这 8 行**。
- 390 = 25 + 12 + 57 + 33 + 156 + 37 + 34 + 36,同样只有 S2。
- 518 − 390 = 128,恰好等于 S2 的失败数之和 → 声明的失败口径也是 S2-only。
- `image_views` 因为 S1、S2 用了同一个键名而被两组合计,所以它"对得上",反而掩盖了前两项的漏加。

即 `totals` 是按 `requests`/`requests_ok` 这两个字面键名取的,遇到 S1 的 `snapshot_requests` 系列直接读成 0。成功率也因此失真:按声明值 75.3%,按实际 713/916 = **77.8%**。

## 3. 分组真实量(重加结果)

| 范围 | 图片 | 请求 | 成功 | 失败 | 成功率 | 看图 | 迭代 | 其他 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1(A01–A20) | 45 | 398 | 323 | 75 | 81.2% | 217 | 87 轮(未完成 1) | `dsl_versions` 270,`retry` 1 |
| S2(A23,A24,B01–B06) | 71 | 518 | 390 | 128 | 75.3% | 105 | 23 轮 | `renders` 71,`cases` 60 |
| **合计(28 行)** | 125* | **916** | **713** | **203** | **77.8%** | **322** | 不可直接相加 | — |
| A 类(A01–A24) | 65 | 441 | 360 | 81 | 81.6% | 228 | — | — |
| B 类(B01–B06) | 60 | 475 | 353 | 122 | 74.3% | 94 | 23 轮 | 60 件作品 |

\* 125 含 S0 的 9 张图,这 9 张图对应的请求与看图在文件里为 0。

## 4. 逐题明细

`请求/成功/失败/看图` 四列对 S0 记 `—`;`迭代` 列 S1 取 `completed_visual_iterations`、S2 取 `visual_iteration_rounds`(两者语义不同,见第 5 节)。

| 题 | 名称 | 图片 | 请求 | 成功 | 失败 | 看图 | 迭代 | DSL 版本 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | operations-dashboard | 1 | 10 | 6 | 4 | 5 | 3 | 6 |
| A02 | conference-schedule | 2 | 12 | 12 | 0 | 8 | 6 | 11 |
| A03 | semantic-debugging | 1 | 12 | 7 | 5 | 3 | 2 | 12 |
| A04 | conversion-paradox | 1 | 5 | 4 | 1 | 1 | 3 | 4 |
| A05 | irregular-sensors | 1 | 7 | 7 | 0 | 2 | 4 | 6 |
| A06 | dependency-graph | 1 | 39 | 12 | 27 | 1 | 3 | 12 |
| A07 | transit-topology | 2 | 32 | 29 | 3 | 15 | 7 | 13 |
| A08 | accessible-wayfinding | 1 | 11 | 6 | 5 | 10 | 3 | 5 |
| A09 | transform-atlas | 1 | 11 | 8 | 3 | 11 | 5 | 8 |
| A10 | compositing-lab | 1 | 8 | 8 | 0 | 11 | 3 | 6 |
| A11 | bilingual-invoice | 2 | 25 | 21 | 4 | 17 | 5 | 22 |
| A12 | responsive-system | 4 | 16 | 16 | 0 | 16 | 5 | 16 |
| A13 | brand-delivery | 4 | 34 | 28 | 6 | 16 | 7 | 29 |
| A14 | content-stress-batch | 8 | 67 | 66 | 1 | 24 | 13 | 49 |
| A15 | reference-reconstruction | 1 | 5 | 5 | 0 | 18 | 2 | 4 |
| A16 | visual-data-forensics | 1 | 3 | 3 | 0 | 15 | 2 | 3 |
| A17 | documentation-handbook | 8 | 72 | 67 | 5 | 21 | 5 | 41 |
| A18 | three-act-story | 1 | 11 | 6 | 5 | 9 | 3 | 11 |
| A19 | visual-puzzle-authoring | 3 | 14 | 9 | 5 | 8 | 1 | 8 |
| A20 | dense-annotation | 1 | 4 | 3 | 1 | 6 | 5 | 4 |
| **A21** | staged-launch-change | **6** | — | — | — | — | — | — |
| **A22** | staged-data-correction | **3** | — | — | — | — | — | — |
| A23 | capability-delivery | 8 | 31 | 25 | 6 | 8 | — | — |
| A24 | release-plan-capstone | 3 | 12 | 12 | 0 | 3 | — | — |
| B01 | ten-real-world-showcases | 10 | 82 | 57 | 25 | 16 | 6 | — |
| B02 | one-client-ten-touchpoints | 10 | 33 | 33 | 0 | 10 | 3 | — |
| B03 | dsl-creative-frontier | 10 | 247 | 156 | 91 | 26 | 4 | — |
| B04 | researched-visual-special | 10 | 37 | 37 | 0 | 18 | 4 | — |
| B05 | product-from-zero | 10 | 40 | 34 | 6 | 14 | 2 | — |
| B06 | everyday-information-reinvented | 10 | 36 | 36 | 0 | 10 | 4 | — |
| **合计** | 30 题 | **125** | **916** | **713** | **203** | **322** | 87 / 23 | 270 |

## 5. 数据质量问题清单

1. **`totals.requests` / `requests_ok` 漏加 20 行**(第 2 节)。少计 398 次请求、323 次成功,影响最大的一项。
2. **A21、A22 的 `counts` 是空对象**,9 张定稿图在全套计数里没有任何请求、看图、迭代记录。这两题的轮次级文件其实有数据:A21 三轮为 9/4/22 次请求(成功 6/3/15、失败 3/1/7)共 35 次,A22 三轮各 2 次共 6 次,合计 **41 次请求、30 次成功** 未进入任何汇总;但轮次级的 `image_views` 全部记为 0,所以回填也不会改变 322 这个数——A21/A22 的看图证据链本身在题层就缺失。
3. **看图次数有三种字段名、两套基准。** 同一概念写作 `image_views_from_iterations_log`(A07、A08)、`image_views_from_iteration_log`(A09)、`image_views_raw`(A09–A20)。按"迭代日志里记到的"这一窄口径是 287 次,而字段值合计 322 次;差的 35 次是题级说明里单列的检查型看图(A07 12、A10 9、A13 9、A20 5)。12 张带 `image_views_detail` 的题逐条数与字段值全部吻合,不构成矛盾,但两种基准混在一个总数里,横向比较时会被误读。
4. **A01–A06 共 20 次看图没有任何逐条依据**,既无 `image_views_detail` 也无 `image_views_note`/`image_views_basis`,只有裸数字。
5. **`dsl_versions` 只覆盖 S1(270)**,且各题注明是"按 requests.jsonl 版本标签去重",与落盘 DSL 文件数不等(A09 8 版/1 个文件、A12 16/4、A14 49/10、A15 4/1、A11 22/14)。A23、A24、B01–B06 完全没有该字段,全套 DSL 版本总数无从统计。
6. **`retry_requests` 只有 S1 有**,全套合计 1(A08)。而 A08 自己的说明写:框架按 `is_retry` 标记计出的 `retry_requests_from_flag = 0`,这 1 次是人工补记的手工重试。S2 那 8 行没有重试字段,重试量不可统计。
7. **`other_service_requests` 全为 0,但 B04 记了 3 次 web 检索**;并且 B04 的检索三元组自身矛盾:`web_retrievals = 3`,而 `web_retrievals_ok = 2` + `web_retrievals_failed = 3` = 5。要么总数少计,要么把重试计进了 failed。
8. **A01 有 1 次未完成视觉迭代(`incomplete_visual_iterations = 1`)仍标 completed**,是全套唯一一处;文件里没有配套说明字段。
9. **迭代数不可合并**:S1 的 87 是"完成的视觉迭代版本数",S2 的 23 是"视觉迭代轮次",相加得 110 会掩盖两者差异。
10. **`aggregation_scope` 声明"shared 计数单列",但文件里没有 shared 行**,`totals` 也没有 shared 项 → 共享准备阶段(服务指南与 DSL 文档抓取、fonts 查询、smoke 渲染)完全不在本文件。
11. **`renders` 只 S2 有(71)**,与 S1 的 125 张图无法对齐,算不出统一的"每图渲染次数"。
12. 全部 30 行 `status = completed`,`completed = 30`、`task_count = 30` 三者一致,这一项无需修正。

## 6. 分布与集中度

- 请求量前 8 题(B03 247、B01 82、A17 72、A14 67、A06 39、A13 34、A07 32、A23 31)合计 604 次,占实际总量 916 的 **65.9%**;B03 一题占 27.0%。
- 203 次失败里,B03 91、A06 27、B01 25 三题占 **70.4%**;其余 17 题合计 60 次。
- **10 题零失败**:A02、A05、A10、A12、A15、A16、A24、B02、B04、B06。
- 成功率最低:A06 30.8%(12/39)、A08 54.5%、A18 54.5%、A03 58.3%、A01 60.0%、B03 63.2%、A19 64.3%、B01 69.5%。
- 单图请求成本(请求数 ÷ 定稿图数)最高:A06 39.0、B03 24.7、A07 16.0、A11 12.5;全套平均 7.3,A 类 6.8(441/65)、B 类 7.9(475/60)。
- 看图密度:A15 18.0 次/图、A16 15.0 次/图(两题各只交付 1 张图),属"少量渲染 + 大量像素核验";B 类合计 1.6 次/图(94/60),其中 B02 与 B06 各 1.0,即每张交付图只打开一次。
- A06 是唯一的极端组合:39 次请求、27 次失败,但只记录 1 次看图和 3 次视觉迭代,且交付 1 张图——请求消耗与看图证据严重不成比例,该题的看图依据需要单独核对。

## 7. 本文件不含的时间信息

文件里与时间有关的只有 `generated_at` 和一条 `wall_clock_note`。**没有任何每题起止、总墙钟、等待耗时或请求耗时**,所以无法从本文件核对耗时分布,也无法判断总墙钟与请求耗时是否被混记。

`wall_clock_note` 唯一给出的具体数值是:A12 的 `active_span` 含一次约 **15 小时 51 分的跨夜间隔**,该题已在自己的文件里标注过。这段时间是空档,不是工作时长,不能计入任何有效耗时统计。

## 8. 若要把这份文件改对

按第 2 节的重加结果,`totals` 应改为:`requests 916`、`requests_ok 713`(并可补 `requests_failed 203`)。这一步只需要在聚合脚本里对两套键名做别名归一(`snapshot_requests`→`requests` 等),不要改动任何一题的明细数字。

其余按影响排序:回填 A21/A22 的 41 次请求并把两套 `image_views` 基准分别标注;把 shared 计数作为独立一行加入;统一 `image_views_*` 命名或补上口径注释;修正 B04 的 web 检索三元组;为 A23/A24/B01–B06 补 `dsl_versions` 与重试字段。这些都不影响 125 张图片这一项。
