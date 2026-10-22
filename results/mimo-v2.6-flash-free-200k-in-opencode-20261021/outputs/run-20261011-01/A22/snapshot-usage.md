# A22 · 三轮累计使用报告（真实数据更正与局部回归）

## 完成状态
三轮全部完成并逐图真实看图。每轮独立子目录保留最终 PNG（服务原始字节）、同名 `.snapshot`、
`computed-data.json`、`layout-map.json`，第二/三轮另有 `change-audit.json`；任务根本报告与
`task-metrics.json` 汇总三轮，每轮另有自己的报告/指标。

| 轮次 | 内容 | 最终图 | 状态 |
|---|---|---|---|
| round-01 | 原始 CSV 六个月 1600×1000 驾驶舱（零起点共用柱图/六行表/主结论） | `round-01/dashboard.png` | completed |
| round-02 | 两处财务更正 + 负轴负柱重算（不变区域 0px 回归） | `round-02/dashboard.png` | completed |
| round-03 | 新增 2026-10 共 7 个月（KPI/图/表/结论全量重排，更正保持） | `round-03/dashboard.png` | completed |

## 实际文档/DSL/工具应用
- 服务基地址以总 run-config 为准（`https://open-snapshot.muedsa.com`）；请求体、编码、
  响应类型、字体确认依据 ai-guide/DSL 文档——**本 run 内 A01 起已真实取得并本地缓存，本题
  复用缓存、无新增文档 HTTP**（requests.jsonl 中 other_service_requests=0 如实反映）。
- DSL 全部由本题脚本程序生成（`a22_common.py` 构件 + `a22_gen.py` 计算排版）：Text 文字
  内容置于 `text=` 属性、`Positioned` 承载边界、`DecoratedBox`/`SizedBox` 构柱与网格，
  字体 `Noto Sans CJK SC`；无外部素材，纯 DSL 主体。
- 渲染经 `tmp/…/_suite/snap_render.py`（仅 429/503 重试）；复制经 `a22_copy.py`
  **md5 字节一致 + 1600×1000 PNG 头校验**；审计经 `a22_audit.py`（变更传播/保留/回归，
  只写入真实查看证据）。

## 计算与显示口径（三轮共同）
- 每月净收入 = gross_revenue − refund_amount；经营利润 = 净收入 − operating_cost；
  退款率 = refund/gross；月转化率 = orders/sessions；**总体转化率 = 总订单/总访问（加权）**。
- 汇总与柱高、轴比例均先用未舍入值计算，**最后一步**才格式化：金额整数千分位、百分比两位
  小数十进制四舍五入（Decimal ROUND_HALF_UP）。结论头条数字与 totals 断言一致（gen 内 assert）。
- 轴：净收入/利润共用零起点，r1 `[0,240000]`；r2/r3 因真实负利润扩展为
  `[-30000,240000]`（负轴只增不裁），零线 y=687.78，网格保留 0/60k/120k/180k/240k 主系列并
  新增 −30k。

## 三轮关键数值（全部实际计算核验）
| 指标 | r1（原始） | r2（更正后） | r3（7个月） |
|---|---|---|---|
| 总净收入 | 918,624 | 908,624（−10,000） | 1,121,424 |
| 总经营利润 | 262,124 | 182,124（−80,000） | 252,924 |
| 总订单 / 访问 | 3,045 / 27,300 | 3,045 / 27,300 | 3,685 / 33,200 |
| 总体转化率 | 11.15% | 11.15%（更正不涉 orders/sessions） | 11.10% |
| 负利润月 | 无 | 2026-09 = −5,632 | 2026-09 = −5,632 |
| 极值/要点 | 峰值 202,368/64,368；低点 27,914 | 08 退款率 13.32% | 10 月 212,800/70,800 最高 |

## 变更传播与回归方法（round-02/03 change-audit.json）
- **changes**：逐字段 diff 上一轮 + 新增行；每条含原字段旧新值（对照原 CSV）、
  传播链 monthly→totals/KPI→柱像素高（含跨轮 span 重算：08 净 274.0→229.48px、
  09 利润 101.92→**−7.93px 移到零线下**）→表格单元格→结论全文（前后文本），并给
  KPI 卡/图槽/表行/结论区的实际坐标定位。
- **preserved**：未涉及字段与月份逐字段对照 CSV 原样；9 区域边界逐区域分量差
  （r2 vs r1、r3 vs r2 **全为 0px**，≤2px 要求）；region style 前后一致（字体/字号/颜色/卡样式）；
  输入 CSV 未修改；r3 另证两项更正**继续生效未恢复**（25048/208000 vs CSV 15048/138000）。
- **regression**：data（重算+断言+渲染文案一致）、axis（负范围/零线位置/负柱在零线下未裁切
  未画正）、layout（坐标差）、visual（真实打开整图与关键局部，带 viewed_at）、bar_heights
  （px=值/span×380 逐柱）。所有 passed 类字段均附方法与证据路径，无预填。

## 逐图视觉自检（全部真实查看）
- **r1**：整图 + 图表/表格两处放大——柱标签经 +10px 外移与净收入柱零相压；表 6×5 逐值与
  computed-data 一致；正文最小 22px；结论 3 行在卡内。
- **r2**：整图 + 负柱放大——红柱在零线下 7.93px 未裁切、`-5,632` 红标在柱下；首轮发现网格
  刻度跨轮错位 → 修正后重渲染对比确认（本轮唯一真实视觉迭代）。
- **r3**：整图 + 09/10 柱簇 + 表格放大——7 槽/7 行齐、更正值保持、`212,800/70,800` 标签分离、
  04 未省略、结论 3 行在卡内。
- 裁剪/放大图仅存临时目录（过程证据），最终 PNG 为服务原始字节、后处理零参与。

## 实际问题、修复与验证（如实记录）
1. **r2 网格刻度跨轮错位**（查看 r2 首版发现）：`range(-30000,…)` 生成 −30/30/90/150/210k，
   与 r1 的 0/60k/120k/180k/240k 错位。修复：axis_spec 改固定系列（r2/r3 = −30k/0/60k/…/240k，
   各刻度仍按真实值定位）；重渲染后实看对比确认（迭代 seq3）。
2. **audit 脚本字段键错误**（`KeyError: 'refund_amount'`，totals 实为 `*_sum`）：在交付
   change-audit 之前失败暴露 → 修正两处键名 → 重新生成并核验输出（3 处改动逐值检查：
   15048→25048、138000→208000、−5,632 柱从 101.92px 上方变 −7.93px 下方）。
3. **交付前完整性核验**：`verify` 交叉检查全部成品 md5 与报告记录一致、`.snapshot` 与临时
   DSL 字节相同、PNG 头合法（见 task-metrics 与各轮 copy-meta）。

## 过程统计（详见 task-metrics.json）
4 次渲染请求全部 200、0 失败 0 重试、请求耗时合计 14.429s；9 次看图事件（4 张不同 PNG）；
4 条迭代记录（3 baseline + 1 视觉迭代，r1/r3 首版即达标不制造凑数迭代）；三轮总墙钟
1,251.2s（含计算、排版、看图、审计与写作，远大于请求耗时之和——如实分列）。

## 文件路径（path_base=output_dir，相对本题输出根）
`round-01|02|03/{dashboard.png, dashboard.snapshot, computed-data.json, layout-map.json,
[change-audit.json], snapshot-usage.md, task-metrics.json}` + 本报告 +
`task-metrics.json`；过程：`tmp/run-20261011-01/A22/{requests.jsonl, iterations.jsonl,
scripts/, round-0X/（渲染原图、缩放证据、copy-meta.json、草稿DSL）}`（path_base=suite_root）。

## 未解决事项
无。三轮均满足要求、通过逐图视觉自检与回归核验。
