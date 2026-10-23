# Snapshot 使用情况说明与踩坑记录（A21 · 跨三轮累计）

任务ID：A21
任务名称：staged-launch-change（预置连续三轮）
本次运行ID：r20261014T1536+0800-5f11da
状态：**完成**（round-01 / round-02 / round-03 三轮全部归档）
总任务清单位置：第 21 题（A01–A21 已完成，A22–A24、B01–B06 待执行）

输出目录：`outputs/r20261014T1536+0800-5f11da/A21/`
临时目录：`tmp/r20261014T1536+0800-5f11da/A21/`
路径基准：suite_root

遵循 [PATHS.md](../../../PATHS.md)。本文档的路径均为相对总任务根的相对路径；
Markdown 本地链接相对本文件所在位置（`outputs/<run_id>/A21/`）重新计算。

这是**题目根层的累计视图**。每轮的完整说明与指标分别在各轮的
`round-NN/snapshot-usage.md` 与 `round-NN/task-metrics.json` 里，本文档只汇总
跨轮结论、累计统计与三轮共同的经验；不重复轮次明细。

---

## 1. 三轮总览

| 轮次 | 需求主题 | 最终图 | 快照请求 | 成功/失败 | 看图 | 视觉迭代 | 质量门 |
|---|---|---|---|---|---|---|---|
| round-01 | 基线：两尺寸发布会主视觉，6 个品牌构件 | 2 | 9（含 3 条能力探针） | 6 / 3 | 14 | 1 | content-map 7/7 |
| round-02 | 主标题换成 27 字长句（≤3 行、≥48）；新增赞助方与报名状态牌 | 2 | 4 | 2 / 2 | 14 | 0 | content-map 9/9 |
| round-03 | 改浅色主题；普通文字对实际合成背景 ≥4.5:1；新增英语短句 | 2 | 4（含 2 条去文字辅助渲染） | 4 / 0 | 15 | 0 | content-map 9/9 + contrast-audit 23/23 |
| **合计** | | **6** | **17** | **12 / 5** | **43** | **1** | |

- 6 张最终图片是**三组独立作品**（每轮两图，均 1080×1350 与 1440×810 分别构图），
  不是同一张图的重复，也不是等比缩放。
- 请求耗时之和 **1417.469 s**，其中 1342.141 s 是 round-02 两次服务端读取超时
  的挂起（无产出）；扣掉后真正与渲染相关的时间为 **75.328 s**。
- 累计墙钟从 round-01 首条请求到 round-03 归档完成共 **57463.0 s**
  （2026-10-19T18:40:30 → 2026-10-20T10:38:13 +08:00）。这个数**不等于**三轮
  elapsed_seconds 之和（21194.4 s），因为三轮之间还有跨轮阅读、准备与归档时间；
  也**不等于**请求耗时之和，更不等于"设计时间"——里面含上下文压缩、平台停顿与
  归档返工。

逐轮详情：[round-01/snapshot-usage.md](round-01/snapshot-usage.md)、
[round-02/snapshot-usage.md](round-02/snapshot-usage.md)、
[round-03/snapshot-usage.md](round-03/snapshot-usage.md)。
结构化指标：[task-metrics.json](task-metrics.json) 与各轮的
[round-01/task-metrics.json](round-01/task-metrics.json)、
[round-02/task-metrics.json](round-02/task-metrics.json)、
[round-03/task-metrics.json](round-03/task-metrics.json)。

---

## 2. 三轮最终图片

| 轮次 | 竖版 1080×1350 | 横版 1440×810 |
|---|---|---|
| round-01 | [launch-portrait.png](round-01/launch-portrait.png) / [DSL](round-01/launch-portrait.snapshot) | [launch-wide.png](round-01/launch-wide.png) / [DSL](round-01/launch-wide.snapshot) |
| round-02 | [launch-portrait.png](round-02/launch-portrait.png) / [DSL](round-02/launch-portrait.snapshot) | [launch-wide.png](round-02/launch-wide.png) / [DSL](round-02/launch-wide.snapshot) |
| round-03 | [launch-portrait.png](round-03/launch-portrait.png) / [DSL](round-03/launch-portrait.snapshot) | [launch-wide.png](round-03/launch-wide.png) / [DSL](round-03/launch-wide.snapshot) |

每轮同尺寸的 DSL 与 PNG 配对齐全；PNG 是服务返回的原始字节，未经后处理。

---

## 3. 跨三轮的设计演进

**信息量逐轮增加，画布始终不变。** 三轮共同面对的问题是"内容变多、尺寸不变"：

| | round-01 | round-02 | round-03 |
|---|---|---|---|
| 标题 | 10 字，132/116 px | 27 字，66/52 px，≤3 行 | 同 round-02 |
| 信息栈 | 日期 / 讲者 / 网址 | + 赞助方、报名状态牌（5 行） | + 英语短句（6 行） |
| 主题 | 深底 + 发光 | 深底 + 发光 | 浅底，无发光阴影 |
| 品牌构件 | 6 | 6 | 6 |
| 文字下限 | ≥56 | 标题 ≥48、其余 ≥24 | 同 round-02，英语句 ≥24 |

三轮沉淀的三条主线：

1. **标题让出字号，不让出完整性和层级。** 27 字在 860 px 文本盒内、最多 3 行，
   只有 66/52 这一档能同时满足"不折行、不下限、仍高于日期"；次要文字按同比例下压，
   保持"标题 > 日期 > 讲者/网址"的层级不倒挂。全程不用 `transform` 压窄文字。
2. **新内容进信息栈与牌子族，不进品牌几何。** "免费参加 · 无需报名"是牌子族的
   新实例（用边框色区分语义），英语短句是普通文字——因此 6 个品牌构件的形态、
   层数、圆角比例、光带条数与递减关系三轮一字未变。
3. **装饰负责填空，而不是文字让位。** round-02 把发光球下移填补 3 行标题留下的
   右下空区；round-03 反过来让球体移到右列空区、把辉光收敛到与所有文字墨迹
   几何不相交——因为浅底上的文字对叠层极度敏感。

**三轮共用的能力基座**（round-01 用 3 条能力探针实测得到，后两轮直接复用，
不重复消耗请求）：`gradientType="LINEAR|RADIAL|SWEEP"` 与全部渐变参数、
`<Opacity>`、`boxShadow`、`shape="CIRCLE"`、`letterSpacing`、`height/maxLines/
softWrap`；以及三条负面结论——`gradientFocal` 会把径向渐变压平、
`shape="CIRCLE"` 与 `borderRadius` 互斥会 `PARSE_ERROR`、嵌套 `<Text>` 的前导
空白会被裁掉。

---

## 4. 跨三轮的对比度结论

只有 round-03 要求对比度审计，结论记录在
[round-03/contrast-audit.json](round-03/contrast-audit.json)：

| 项 | 值 |
|---|---|
| 阈值 | 4.5:1（未舍入判定，不因字号大而放宽） |
| 检查范围 | 2 图 × 23 段普通文字（竖版 12、横版 11） |
| 未检查项 | 0 |
| 全局最小对比度 | **4.8616**（未舍入 4.861573385783012） |
| 最差位置 | 竖版 `date` `#C2410C` 对页面底 `#F5F8FC`（横版同段 4.9098） |
| 带坐标样本 | 每图 6 处、共 12 处，含最差位置 |
| 背景来源 | 去文字辅助渲染在字形覆盖区的实际像素（同构造器、`Canvas.text(record_text=False)`） |

方法自洽性自检：交付图与去文字辅助图相减，墨迹阈值之外的逐通道最大差为 **12.0**
（即墨迹判定阈值本身），证明两图除文字外逐字节同源；round-03 的 12/11 段文字
全部无 `textShadow`，差值不会混入阴影。

---

## 5. 三轮共同的执行纪律

- **提交前必过无网络干跑门**（round-01 `a21_dryrun.py`、round-02
  `a21_dryrun_r2.py`、round-03 `a21_dryrun_r3.py`）：构造 DSL → 断言合法 →
  打印元素表 → 校验 advance 不超文本盒宽 → 校验墨迹与装饰净距 → 校验扩展空间与
  字号下限 → 校验标题行数 → 校验必需文案与需求原文逐字符一致 → 校验 `<Text>`
  无 `transform`。零服务请求就能抓到"静默丢字"这类不报错的缺陷——round-02 就是
  靠这条断言发现横版原本会丢掉"的结构化方法"。
- **交付后必做像素级审计**（`a21_audit.py`，产出 `content-map.json`）：
  墨迹检测用"单行字带窗口 + 列/行连续性"取真实墨迹 bbox，不用故意超大的文字盒；
  碰撞判交集面积、装饰判净距、尺寸读 PNG IHDR、占位词黑名单扫描。
- **必做实际看图**：三轮共 43 次实际打开，含整图 1:1 与语义裁切放大（header、
  title、info、orb、footer、whole），逐条记录在
  `tmp/<run>/A21/viewing-evidence.json`（round 1/2/3 块）。
- **不制造迭代**：round-02 与 round-03 首版即通过，`completed_visual_iterations`
  如实记 0；累计 1 次完整视觉迭代是 round-01 的 v1→v2 修复闭环
  （字标中英粘连、竖版右上空白、强调条与细线间距）。
- **请求与交付件的对应由 sha256 证实**，不手抄：每轮
  `task-metrics.json` 的 `delivery_map` 用响应字节 sha256 与交付 PNG sha256
  逐一比对，三轮 6 对全部一致。

---

## 6. 请求与迭代统计（累计）

结构化指标：[task-metrics.json](task-metrics.json)

| 指标 | 值 | 说明 |
|---|---|---|
| 快照请求总数 | 17 | render 12 + render-aux 2 + probe 3 |
| 成功 / 失败 | 12 / 5 | round-01：6/3（含 1 条 400）；round-02：2/2（两次读取超时，无字节返回）；round-03：4/0 |
| 重试请求 | 2 | 均为 round-02 同一份 DSL 的原样重发 |
| 语法修复重交 | 3 | 均在 round-01（`shape="CIRCLE"` 与 `borderRadius` 互斥等 400） |
| DSL 版本数 | 10 | round-01 6（含探针版）、round-02 2、round-03 2 |
| 实际看图次数 | 43 | round 1/2/3 = 14/14/15；同一张图的不同视图不合并 |
| 完整视觉迭代 | 1 | round-01 v1→v2；round-02/03 首版即通过 |
| 迭代记录条数 | 8 | `tmp/<run>/A21/iterations.jsonl` |
| 请求耗时之和 | 1417.469 s | 含 round-02 的 1342.141 s 服务端挂起 |
| 扣挂起后的有效请求耗时 | 75.328 s | 占累计墙钟 0.13% |
| 限流等待 | 0 | 全程未出现 429/503 |
| 排队等待 | `null` | 服务端不可观测，未取得该数据 |
| 等待用户反馈 | 0 | 预置轮次模式，前一轮归档后直接读取下一轮需求 |

**请求口径说明（如实披露）**：round-01 的 3 条能力探针在 `requests.jsonl` 里的
`round` 字段为 `null`（驱动脚本在轮次字段落地之前就发出了它们）。累计计数按
`started_at`（18:40–18:43，落在 round-01 起点 18:39:48 之后）把它们归属 round-01，
与 round-01 `task-metrics.json` 的 9 条一致；该归属口径写在指标的
`snapshot_requests_attribution_note` 里。round-03 的 2 条去文字辅助渲染
（`kind: "render-aux"`）是真请求，计入总数，但**不产出交付件、不计入作品数、
不进 `delivery_map`**。

---

## 7. 跨三轮的经验与踩坑

**方法类。**
1. **CJK advance = 恰好 1 em**，让"这行装得下吗"变成整数算术
   （`fontSize × 字数 ≤ 文本盒宽`），是长标题排版的唯一可靠基准。
2. **审计别用文字盒判碰撞**——文字盒故意超大，且同色装饰会被同色阈值吃进来。
   用"单行字带窗口 + 列/行连续性"取真实墨迹 bbox，结果才可复算。
3. **交付前先跑无网络干跑门**，零请求就能抓到"静默丢字"这类不报错的缺陷。
4. **对比度的正确背景源是"去文字渲染"，不是 token**——同一份构造器关掉
   `<Text>` 输出，就得到逐像素真实的合成背景。
5. **给取样方法做自洽性自检**：交付图与辅助图相减，墨迹外的逐通道最大差应当
   等于墨迹判定阈值本身。这个数不对，整个审计都无效。
6. **配置值与实际渲染值必须同源**——round-03 的 `halo_scale` 一度配置写 2.7、
   构造器写死 2.75，靠"重建 DSL 与已交付字节逐字节比对"才确认是记录缺陷。
7. **JSONL 的写入格式要和读法一致**——追加一条多行 JSON 就把整个文件打碎了。
   追加前读一遍既有行的格式，写完回读逐行校验。

**服务与计时类。**
8. 服务端"接受连接但挂住不返回"和 429/503 是**两类故障**：内部重试只覆盖后者时，
   挂起时间会全额进墙钟，必须单列，否则"请求耗时"会被误读成"工作时间"。
9. **记录器要记录失败请求的真实起点**：异常路径下 `started_at` 容易写成结束时刻，
   落盘后只能靠 `elapsed_ms` 反推（round-02 就是这样校正的）。
10. **指标里的墙钟不能互相替代**：累计墙钟 ≠ 三轮 elapsed 之和 ≠ 请求耗时之和；
    每段都必须单列来源（设计/请求/服务挂起/归档尾段）。

**记录类（全部已披露、已留底）。**

| 轮次 | ID | 内容 | 状态 |
|---|---|---|---|
| round-01 | a21-r1-u1 | 9 条请求记录无 `delivered` 字段 | 改由 sha256 比对得出对应关系 |
| round-01 | a21-r1-u2 | 交付 PNG 被同轮 v2 原地覆盖 | v1 字节保留在 `tmp/…/A21/responses/` |
| round-01 | a21-r1-u3 | 部分看图时间只到分钟级 | 逐条以 `viewed_at_precision` 标明 |
| round-02 | a21-r2-u1 | portrait 前两次请求读取超时共 1342.141 s | 记录原样保留，attempt 3 同 DSL 重发成功 |
| round-02 | a21-r2-u2 | 驱动脚本异常路径 `started_at` 记为结束时刻 | 指标脚本用 `elapsed_ms` 还原并逐条留证 |
| round-03 | a21-r3-u1 | changes.json 第一版不是合法 JSON | 坏版本留底，已修正 |
| round-03 | a21-r3-u2 | 修正版 changes.json 一度误写进交付目录 | 用 `mv` 移回临时目录，内容无独立留底（如实说明） |
| round-03 | a21-r3-u3 | 看图时间只到分钟级 | 15 条事件均标明精度 |
| round-03 | a21-r3-u4 | `halo_scale` 配置与实参一度不一致 | 已修，交付字节未变 |

另有两项**跨题遗留**（非本轮引入，如实保留、不补造）：
- 套级 `suite-state.json` 的 `tasks_detail` 只有 A09–A21 有逐题明细，
  A01–A08 只出现在 `completed` 清单里；A21 自 round-01 归档起已加入逐题明细。
- round-01 的 `design-tokens.json` 由更早一版生成器产出，缺 `diameter_*` /
  `center_*` 键，**因此不要用当前脚本重跑 `a21_audit.py 1`**（会写出不一致的
  token）。round-02 归档时曾向 `round-01/task-metrics.json` **追加**字段以对齐
  当前生成器（数值一个未改），原文件留底于
  `tmp/<run>/A21/archive-conform/`。

---

## 8. 交付清单与留痕确认

题目根层：
- `task-metrics.json`（本任务的跨三轮累计指标）
- `snapshot-usage.md`（本文件）

每轮子目录（各 8 个文件，round-03 另加 `contrast-audit.json` 共 9 个）：
`launch-portrait.png` / `.snapshot`、`launch-wide.png` / `.snapshot`、
`design-tokens.json`、`content-map.json`、`snapshot-usage.md`、`task-metrics.json`
（round-03 再加 `contrast-audit.json`）。

临时目录留痕（`tmp/r20261014T1536+0800-5f11da/A21/`）：三轮的 21 份 DSL（含 4 份
round-03 dryrun、4 份 notext）、`requests.jsonl`（17 条）、`iterations.jsonl`
（8 条，含 `iterations.pre-r03-normalize.jsonl` 留底）、`viewing-evidence.json`
（43 条事件）、三轮预览视图与 `views-manifest.json`、round-02/03 的变更说明
（含非法 JSON 留底）、2 张去文字辅助背景渲染、46 张对比度局部证据、
`archive-conform/` 下的 round-01 指标留底。生成脚本在
`tmp/r20261014T1536+0800-5f11da/_suite/gen/`（`a21_core.py`、`a21_layouts.py`、
`a21_round.py`、`a21_probe.py`、`a21_dryrun_r2/r3.py`、`a21_audit.py`、
`a21_r3_aux.py`、`a21_contrast.py`、`a21_viewlog_r2.py`、`a21_view_r03.py`、
`a21_iter_r03.py`、`a21_metrics.py`、`a21_metrics_r01_conform.py`、
`a21_state_r01/r02/r03.py`）。

套级归档：`tmp/<run>/_suite/events.jsonl` 追加了 round-03 的 `round_completed`
与 A21 的 `task_completed` 两条事件；检查点
`tmp/<run>/_suite/checkpoints/state-000057.json` 为 A21 归档后的新快照，
历史快照未覆盖。

交付目录不含草稿或响应正文；最终 PNG 是服务原始字节，未经后处理；未保存任何密钥。
总任务根的 `.gitignore` 只忽略 `__pycache__/`、`*.pyc`、`.pytest_cache/` 等运行时
缓存，不忽略 `tmp/`、`outputs/` 与过程证据；`__pycache__/` 不列为产物或自检证据。

**结束依据。** 三轮共 **27 个交付文件**已逐一核对存在：round-01 八个、round-02
八个、round-03 九个（多一个 `contrast-audit.json`），子目录内合计 25 个，加题目根层
的 `task-metrics.json` 与本报告共 27 个；三轮
`content-map.json` 的 7/7、9/9、9/9 项检查全部通过；round-03 的
`contrast-audit.json` 23 段全量对比度最小 4.8616、无未检查项；6 张最终图片各
打开多次并放大核对；交付映射由 sha256 逐一证实。A21 三轮需求全部满足，
本题已完成，不再追加请求或迭代。下一题按 catalog.json 顺序为 A22。
