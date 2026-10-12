# A14 · 八组文案压力测试与批量生成 — 使用说明

- 任务：`tasks/A14-content-stress-batch/`（TASK.md / AGENTS.md / task.json 已完整阅读）
- run_id：`20261008T1615Z-run01`
- 输出目录：`outputs/20261008T1615Z-run01/A14/`
- 临时目录：`tmp/20261008T1615Z-run01/A14/`
- 状态：completed（8/8 张为服务真实响应，逐张查看，batch-audit.json 170/170 通过）

## 交付清单

| 文件 | 字节 | served_by（渲染请求 ID） | 查看时间 |
|---|---|---|---|
| `card-K01.png` + `.snapshot` | 34291 | `A14-v02-K01-20261009T013218Z` | 2026-10-09T01:32:55Z |
| `card-K02.png` + `.snapshot` | 52811 | `A14-v02-K02-20261009T013220Z` | 2026-10-09T01:32:42Z |
| `card-K03.png` + `.snapshot` | 74693 | `A14-v02-K03-20261009T013222Z` | 2026-10-09T01:32:42Z |
| `card-K04.png` + `.snapshot` | 58726 | `A14-v02-K04-20261009T013224Z` | 2026-10-09T01:32:55Z |
| `card-K05.png` + `.snapshot` | 60730 | `A14-v02-K05-20261009T013226Z` | 2026-10-09T01:32:49Z |
| `card-K06.png` + `.snapshot` | 66336 | `A14-v02-K06-20261009T013228Z` | 2026-10-09T01:33:03Z |
| `card-K07.png` + `.snapshot` | 76636 | `A14-v02-K07-20261009T013230Z` | 2026-10-09T01:33:03Z |
| `card-K08.png` + `.snapshot` | 66797 | `A14-v02-K08-20261009T013232Z` | 2026-10-09T01:32:49Z |
| `batch-audit.json` | — | 逐卡 21 项断言 + 6 项批次断言 | — |

八张 `.snapshot` 与发送体逐字节一致（`requests/A14-v02-*.body.txt` 去掉 `POST` 头行后即为
DSL 本体）。v01 的原始响应字节保留在 `requests/A14-v01-*.response.bin`，并从那里复制到
`preview/v01/` 供回溯；交付路径上的 v01 PNG 已被 v02 覆盖，这一点在
`unresolved_issues` 中如实记录。

## 需求 ↔ 证据

| 需求 | 实现 | 证据 |
|---|---|---|
| 8 张 1200×630，文件名 card-K01…K08 | `Doc(1200, 630)` | 审计 `size-1200x630`、PNG 魔数 |
| 统一主色 | `#1B3A6B` 出现在八份 DSL | `batch.primary-colour-shared` |
| 统一标题区域 | 标题恒为 `x=264, w=896` 的左对齐块 | `layout.json` boxes |
| 日期 2026.11.07 / 品牌 Structure / Vision | 导轨 + 页脚 | `text-date` / `text-brand` |
| 状态体系：颜色 + 文字/符号 | 4 色 + 4 种 Container 几何（圆/方/菱/带斜杠圆环）+ 原文字 | `badge-colour-pixels`、`badge-symbol-*`、`status-*-distinct` |
| 标题 ≥36pt、≤3 行 | 72/60/48/40/36 档位，实渲 1–2 行 | `title-size-floor-36`、`title-lines-rendered` |
| 讲者 ≥22pt、长讲者两行 | 30/26/22 档位；K07 长讲者实渲 1 行 | `speaker-size-floor-22` |
| 取消卡保留完整标题与时间 + 注明「本场取消」 | K06 页脚红字，标题/时间原样 | `cancelled-*` 四项 |
| 安全边距 40 | 40px 边框带像素检查 | `safe-margin-40`（0 个非背景像素） |
| 标题不与徽标碰撞 | 徽标先定位，标题顶边从徽标行下方起算 | 生成器 `overlap()` 门 + 像素带 |
| 不靠全局缩小适配长标题 | 只切换字号档位/网格，画布恒 1200×630 | `batch.no-global-shrink` |
| 一套参数化规则、允许长度触发网格/换行 | `generate_a14.py` 单函数 `card()`，grid A/B + 字号档位由数据决定 | `layout.json`、`grids` |
| 接触表（可选） | `preview/contact-sheet-v02.png` 半尺寸 2×4，仅存临时目录 | 01:38:58Z 查看 |

## 真实应用的文档与 DSL 能力

`<Snapshot>`/`<Container>`/`<Stack>`/`<Positioned>`/`<Text>`/`<Column>`/`<Row>`、
`textAlign`、`maxLines`、`letterSpacing`、`borderRadius`、`border="N SOLID #RRGGBB"`、
`<Transform matrix=…>`（菱形与斜杠）、`clipBehavior`。文字含 `<`、`>`、`&` 的 K04 用
`<![CDATA[…]]>` 包裹，实渲确认三个符号原样出现——Snapshot 解析器不做实体解码，把它当成
HTML 就会丢字。

## 设计选择

1. **导轨 + 主栏（grid A）**：编号、日期、时间、条状母题都在左导轨，主栏只放标题、讲者，
   使八张的标题区起点完全一致；条状母题按场次序号增长，让“批量”不等于“复制”。
2. **状态三重编码**：颜色 + 几何符号 + 原文字，色觉不可辨或灰度打印时仍可区分；
   「取消」额外在页脚以状态色加粗显示「本场取消」，而不是把整卡压成灰底。
3. **字号档位而非缩放**：`pick_size` 同时受行数与剩余高度约束，长标题降档，绝不缩画布。
4. **标题/讲者块垂直居中**：v01 顶部对齐使短标题下方留出 100–130px 空洞。

## 实际问题与修复

| # | 观察到的问题 | 原因 | 修复 | 验证 |
|---|---|---|---|---|
| 1 | v01 首版 `pick_size` 只看行数，72pt×3 行的标题盒穿过页脚线 | 缺高度预算 | 引入 `max_h = content_bottom - top - 22 - sp_h` | 生成器门 `stack bottom` 全绿 |
| 2 | K01/K02/K08 标题与讲者之间大片空洞（K02 计划 2 行实渲 1 行） | 共享 `TextFit` 用 1.02em + 0.96 slack，对 Noto CJK 保守约 6% | A14 本地 `Fit` 子类（CJK 1.00em、去 slack、粗体拉丁 0.60em）+ 标题盒 `CENTER_LEFT`；不改共享模块以免影响 A01–A13 | 八张实渲行数 = 计划行数 |
| 3 | grid B 的条状母题会压在标题上（y=148 vs 标题 158） | 竖向堆叠在顶栏无高度 | 同族横向变体 `bars_h` | 代码路径保留（本批未触发 grid B） |
| 4 | 审计脚本自身两处假阴性：所有卡都报“1 行”；徽标符号断言永不匹配 | 三通道求和与单通道阈值比较；`borderRadius` 的 R 大写，断言串写成小写 `radius="` | 改 `mean(axis=2) < thr`；断言串改 `borderRadius="` | 170/170 |
| 5 | `groups()` AttributeError | 当前组被写成整数 | 统一用列表累积 | 可运行 |

## 统计

- 渲染请求 16（v01 八张 + v02 八张），全部 HTTP 200，`server-timing: render;dur=…`
  均为真实渲染（无 cache hit）；失败 0、重试 0、限流未触发（remaining 119/120）。
- DSL 版本 2；图片查看 15 次（v01 六张、v02 八张、接触表 1 张）；
  完整视觉迭代 6 次（v01 查看→改→v02 查看比较，K03/K05 未看 v01 故不计）；
  另有 3 条审计/辅助记录。
- 耗时：墙钟 620.0s（首个日志事件 01:29:57Z → 最后 01:40:17Z），空闲间隔 0s，
  请求耗时合计 34.563s（重叠求和，不等于墙钟），首图 2.6s。
  墙钟自“首个落盘事件”起算，不含之前未落盘的读题与设计时间。

## 未解决事项

- grid B 分支从未被本批 8 条数据触发，只有代码路径检查，没有实渲样本。
- 交付路径上的 v01 PNG 被覆盖（原始字节已在 `requests/` 与 `preview/v01/` 保留）。
