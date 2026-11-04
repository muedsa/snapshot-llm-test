# A24 · 双团队约束下的发布作战计划 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A24/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A24/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

用 release.json 排出 12 个任务在 design/engineering 两个团队上的可行排程：全部任务完整执行其时长、依赖满足、同团队不并行，完工 260 分钟（13:20），缓冲 160 分钟。680×… 三张图（1920×1080 泳道图、1200×1600 决策简报、720×1280 手机卡）共用同一份 schedule.json。关键路径下界 255 分钟、资源下界 242.5 分钟；未做全局最优证明，只称可行且较优。

| 文件 | 说明 |
|---|---|
| [execution-board.png](execution-board.png) | 1920×1080 泳道执行图 |
| [execution-board.snapshot](execution-board.snapshot) | 对应 DSL |
| [decision-brief.png](decision-brief.png) | 1200×1600 决策简报 |
| [decision-brief.snapshot](decision-brief.snapshot) | 对应 DSL |
| [action-card.png](action-card.png) | 720×1280 手机行动卡 |
| [action-card.snapshot](action-card.snapshot) | 对应 DSL |
| [schedule.json](schedule.json) | 精确起止/团队/依赖 |
| [schedule-audit.json](schedule-audit.json) | 资源/依赖/下界/缓冲 |
| [content-map.json](content-map.json) | 三图文案与坐标 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 三张图与尺寸 | 1920×1080 / 1200×1600 / 720×1280 | 通过 |
| 任务完整时长、依赖先完成、同团队不并行 | audit.checks：durations_exact / dependencies_respected / no_team_overlap 全 true | 通过 |
| 不得改依赖、缩时、删检查环节 | 12 任务全部排入，时长为输入值 | 通过 |
| 全部 end ≤ 420 分钟 | 最大 end = 260 | 通过 |
| 求出尽量早的完工时间 | 枚举 3 个可选团队任务的 8 种组合取最小 makespan = 260 | 通过 |
| 关键路径时长与工作量下界 | CP 255 分钟；485/2 = 242.5 分钟 | 通过 |
| 不把未证明的方案称为最优 | audit.optimality 明写「未知、未提供证明」 | 通过 |
| 真实时间同尺度、块内可读 | 纵向时间轴 1 分钟 = 1.93px，块内 ID/标签/起止/时长/依赖 | 通过 |
| 依赖用编号索引而非满图交叉线 | 块内写「依赖 R04、R05」 | 通过 |
| 执行图有空档与截止线 | 空档用深色带并标分钟数，16:00 红线 | 通过 |
| 简报含依赖概览/总工时/完成时间/缓冲/三风险 | 12 行依赖表 + 4 KPI + 3 风险卡 + 排程依据 | 通过 |
| 手机卡按时间序给 12 任务与风险 | 12 行时间升序，团队/起止/风险 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| v1 执行图 | 泳道标题压住 R01/R02、短块文字溢出 | 位移标题、压缩块内文字 |
| v2 执行图 | 12 块全部可读，空档与 16:00 截止线清楚 | 通过 |
| 决策简报 | 依赖表 12 行、KPI、三风险、排程依据齐全 | 通过 |
| 手机行动卡 | 12 行按时间排序，团队与风险标注可读 | 通过 |

## 4. 设计与排版决策

- 时间纵向排布：420 分钟映射到 810px，最短 20 分钟的任务也有约 39px，足以放两行字。
- 把「依赖」写成块内的一行编号索引，避免 12 条交叉线盖住时间块。
- 空档用深色带 + 分钟数标出，读者能直接看出设计团队 10:25–10:30 的 5 分钟等待。

## 5. DSL 能力与文档应用

- 泳道与任务块用绝对定位的 Container，时间轴按 1 分钟 = 1.93px 统一换算，三图共用同一份 schedule.json。
- 块高按 max(46, 时长×比例) 兜底，保证 20 分钟的任务也能放两行文字。
- 三张图的数字全部来自同一 JSON，不存在手写数字。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 泳道标题与首块重叠 | 面板从 top 开始且标题在面板内 | 标题移到面板上方 top-46 |
| 短任务第二行溢出 | 25 分钟块高 48px 放不下三行 | 统一两行：20px 标签 + 15px 时间行 |
| 简报完成时间写成 14:20 | 手写字符串与计算结果不一致 | 改为 13:20 并与 schedule.json 对齐 |

## 排程结论

- 完工 260 分钟（13:20），缓冲 160 分钟
- 关键路径下界 255 分钟，资源下界 242.5 分钟，实际 260（差 5 分钟）
- 可选团队任务：R05→engineering（10:00–10:30）、R09→design（11:40–12:25）、R12→design（13:00–13:20）
- 请求 15 次（成功 15），看图 3 次，墙钟 636.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A24/execution-board.png` | 执行图 |
| `outputs/20261103T152640-suite/A24/decision-brief.png` | 简报 |
| `outputs/20261103T152640-suite/A24/action-card.png` | 行动卡 |
| `outputs/20261103T152640-suite/A24/schedule.json` | 排程 |
| `outputs/20261103T152640-suite/A24/schedule-audit.json` | 审计 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
