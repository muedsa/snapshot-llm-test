# Snapshot 使用情况说明与踩坑记录

任务ID：B04
任务名称：自主研究一个真实主题并制作十件视觉特辑（开放创作赛道 + 真实研究）
本次运行ID：20261003-114508-flashmax
完成状态：完成
结束原因：研究、十件作品、逐件视觉自检与整体审查均已完成
输出目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B04`
临时目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B04`

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01..case-10/final.png` | 10 件独立主作品，服务 200 响应原始字节 | 同名 `final.snapshot` | 完成 |
| `case-01..case-10/final.snapshot` | 每件完整自包含 DSL | 同名 `final.png` | 完成 |
| `case-01..case-10/case.md` | 读者问题/结构/数据来源/示例说明/自检 | 同目录图与 DSL | 完成 |
| `sources.json` | 6 个真实来源的 URL、访问时间、HTTP 状态、贡献内容、各作品引用；未能核实项目单列 | 10 件作品 | 完成 |
| `editorial-note.md` | 选题理由、读者问题、十件作品的叙述路线、编辑规则、虚构声明、局限 | 同上 | 完成 |
| `portfolio.json` / `portfolio.md` | 逐作品映射与策展说明 | 10 件作品 | 完成 |
| `gallery.html` | 本地画廊，索引全部 10 件，相对链接、无远程脚本 | 10 件 `final.png` | 完成 |
| `snapshot-usage.md` / `task-metrics.json` | 本文件与结构化指标 | — | 完成 |

题目要求「至少10件独立完整主作品」：实际交付 **10 件**，每件回答不同的读者问题，
使用不同的图表结构（截面注释图 / 柱状记录 + 条约轨 / 倒轴垂线图 / 日历条带矩阵 /
四格过程条 / 交替年表 / 案卷 / 配对主张账 / 成本收益账 / 不确定性账）。

## 2. 研究：实际读到的来源

| 编号 | 来源 | 实际用途 |
|---|---|---|
| S1 | [NASA Ozone Watch — Annual Records](https://ozonewatch.gsfc.nasa.gov/meteorology/annual_data.html) | 1979–2025 年逐年最大日臭氧洞面积、最小柱臭氧及其发生日期；这是全刊唯一的机器可读数据源，已转录为 `scripts/ozone.py` |
| S2 | [NASA Ozone Watch — What is the Ozone Hole?](https://ozonewatch.gsfc.nasa.gov/facts/hole_SH.html) | 220 DU 阈值的来历与定义；极涡、极地平流层云、催化破坏机理 |
| S3 | [NASA Ozone Watch — What is Ozone?](https://ozonewatch.gsfc.nasa.gov/facts/SH.html) | 90% 臭氧在 10–50 km、总质量约 30 亿吨、峰值约 32 km、UV 屏蔽比例 |
| S4 | [UNEP Ozone Secretariat — Facts and figures](https://ozone.unep.org/facts-and-figures-ozone-protection) | 198 个缔约方、99% 淘汰、恢复年份、135 Gt CO₂e、0.5–1 °C、UV 反事实、EPA 健康数字、多边基金、Kigali 数字 |
| S5 | [WMO/UNEP Scientific Assessment of Ozone Depletion 2022 — Executive Summary](https://www.csl.noaa.gov/assessments/ozone/2022/executivesummary/) | 各纬度带趋势与不确定度、恢复年份、CFC-11 延误 3 年/1 年、未解释排放清单、二氯甲烷、N₂O、SAI 风险、政策年表表 ES-1 |
| S6 | [UNEP Ozone Secretariat — Kigali Amendment overview](https://ozone.unep.org/kigali-amendment-overview) | Kigali 2016 通过、2019 生效、HFC 年增 >10%、2047 年降 80–85%、0.3–0.5 °C |

访问时间、HTTP 状态、各来源贡献与引用关系见 `sources.json`；两处来源不一致（Kigali
缔约方数：S4 记 2024-10 逾 160、S6 记 2026-02 逾 170）已在 `sources.json` 与作品脚注中
如实标注，作品采用较新的一处并给出日期。

## 3. 请求、迭代与看图

请求记录：`tmp/20261003-114508-flashmax/B04/requests.jsonl`（24 条，全部为渲染请求）
迭代记录：`tmp/20261003-114508-flashmax/B04/iterations.jsonl`（21 条）
看图台账：`tmp/20261003-114508-flashmax/B04/image-views.jsonl`（24 条逐张查看记录 + 1 次拼版总审）

- 渲染请求总数：**24**，成功 **24**，失败 **0**
- 本任务未出现 400/413 拒绝：`sk.guard()` 在本地按标签预检（最高一件 820 要素），
  四个已知上限（4096 要素 / 1 MiB / 4096 px 高 / 实体不解码）都在本地拦住
- DSL 版本数：34 个 `.snapshot`
- 实际看图次数：**24**（另加一次 10 件拼版总审）
- 完整视觉迭代数：案例内共 16 次「看图 → 改 DSL → 重渲染 → 再看」
- 已记录请求耗时之和：73.7 秒（含重叠，不等于墙钟）

## 4. 修改记录与踩坑（研究相关）

| 现象 | 原因与依据 | 处理 |
|---|---|---|
| 三件作品曾把「趋势线」画成锯齿栅栏 | 年度最小值序列本身年际跳动极大，46 点折线在本刊宽度下无法读 | case-03 改为从 220 DU 阈值垂下的「深度」条；case-02/04 保留柱与点阵编码 |
| 倒轴面积填充像天际线 | 倒置 y 轴上从顶部填充等于从「最好」值向下垂幕 | 去掉填充，改为折线 + 标记 + 五年均值 |
| 放射日历图彻底失败 | 弧线只落在同一象限、月份辐条像散线、示意剖面像毛毛虫 | 放弃该结构，改为「一年一行」的日历条带矩阵 |
| 数值单位与数字重叠（`~100ODSs`） | 单位位置由宽度估算推得，估算偏短 | 共享面板助手加大间隔 |
| 收益条标签出界 | 条形按同一比例尺绘制，最长条 + 标签超过画布 | 缩小比例尺并缩短标签；并注明「成本条在此比例尺下长 2 px，这正是要点」 |
| 固定长度横线暗示可比 | 摄氏度与十亿吨 CO₂e 单位不同，等长横线会制造来源并未做出的比较 | 去掉横线，改为「PUBLISHED ESTIMATE」标签并在正文解释 |
| 拉丁文按字符断行（`no t observed`、`harbo ur course`） | 早期 `wrap()` 逐字符换行，对 CJK 正确、对拉丁文错误 | 改为按空白分词、超长词才退化为字符断行；并回炉重渲染已交付的 4 件 B03 作品 |

## 5. 消耗

| 指标 | 实际值 | 来源 |
|---|---|---|
| 任务起止 | 2026-10-03T13:15:24+08:00 → 进行中 | suite-state.json |
| 已记录请求耗时之和 | 73.7 秒 | requests.jsonl（含重叠） |
| 限流/排队等待 | 0 / null | 未出现 429；排队不可测 |
| token / 图像输入 / 费用 | null | 平台未提供 |

## 6. 未解决事项

- 未取得 CFC-11 的测量级排放序列，因此该事件只按评估报告的表述与延误年数呈现，
  画面明确写出「本页不画曲线」及其原因。
- 北极仅在来源做对比处出现，未单独作图。
- Kigali 缔约方数在两份来源中不一致，已如实记录并采用较新值。

## 7. 诚实记录：一次自伤事故

在 B04 第一次渲染时，我把 B03 的构建脚本复制过来却没有重置 `SK_TASK`，导致那次调用
解析到 `tmp/.../B03/` 下的路径：它渲染的是 **B03 的 case-01 DSL**，把请求写进了 B03 的
日志，并覆盖了 B03 的两份草稿（`dsl/case-01.v1.snapshot` 与 `renders/case-01.v1.png`）。
该记录已按真实归属移回 B03（`B03-REQ-0088`，附说明），B03 的交付物未受影响且事后再次
通过校验。相关时间戳也曾被我写成估算值，现已全部按 `requests.jsonl` 与 `suite-state.json`
重算，并在 B03 的说明文件里更正。
