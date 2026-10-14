# A02 · 三会场密集会议日程 — 使用与自检报告

- run_id：`2026-10-12T10-04Z-r001`（基准 `suite_root`）
- 输出：`outputs/2026-10-12T10-04Z-r001/A02/`　临时：`tmp/2026-10-12T10-04Z-r001/A02/`

## 完成状态

completed。`agenda-wide.png`(1920×1200)、`agenda-mobile.png`(720×1280) 均为服务原始响应字节，
各带同名 `.snapshot`；附 `schedule-audit.json`。

## 需求逐项自检

| 要求 | 落实 | 证据 |
|---|---|---|
| 三条会场泳道，09:00–16:00 共用线性时间轴 | `x = 218 + (min−540) × 3.9667`，A/B/C 三条泳道同一 x 映射 | `schedule-audit.json → time_axis` |
| 位置与长度按实际起止比例 | 30 分钟的 S15 实宽 119px、35 分钟的 S06 实宽 139px、75 分钟的 S10 实宽 298px，比例恒等 | `zoom-v006-s15.png`、`zoom-v006-dense10.png` |
| 空档保留 | B 会场 11:10–12:00、C 会场 15:10–16:00、A 会场 15:00–15:30 等 19 段空档留白 | `venue_gaps` |
| 午休 12:00–13:00 跨三泳道且不与会议合并 | 独立琥珀带从 A 顶到轴基线，标签“公共午休 12:00 – 13:00”；`merged_with_session: false` | 大图带区 + `public_lunch` |
| 15 项编号/标题/讲者/起止/类别可读 | 块内：编号、起止、类别（宽块另有时长）；索引表：编号、起止、时长、会场、类别、标题、讲者 | `agenda-wide.png` 下半区 |
| 短活动用外侧说明/编号索引，不把 40 分钟画成 60 分钟 | 短块改为“编号+类别”同行、起止两行；标题与讲者由编号索引承载；块宽一律按分钟比例 | `zoom-v005/006-dense10.png` |
| 正文 ≥20、时间标签 ≥18 | 索引标题/正文 20–24，时间 18；读图说明 18；时长与脚注 16–18 | 全图 |
| 注明读图方法与会场容量 | 顶部“读图方法”条 + 每条泳道“容量 N 人 / M 场活动” | 大图 |
| 手机图改为分时段列表 | 上午 8 场 / 公共午休 / 下午 7 场，15 张卡片各含编号、起止、会场、类别、时长、标题 | `agenda-mobile.png` |
| 手机图讲者移出但须写明 | 头部“讲者详见完整日程”，底部“讲者名单见 1920×1200 完整日程编号索引” | 同上 |
| 不得缩小/裁切大图 | 手机图为独立 DSL（720×1280 另排），无 `<Image>`、无裁切；`content_map_note` 记录 | `agenda-mobile.snapshot` |
| 手机正文 ≥18 | 卡片两行 18/19，段标题 20，页脚 18 | 同上 |
| schedule-audit.json 四要素 | `events`(15，含分钟时长)、`venue_gaps`(19，含 public_lunch 分列)、`conflicts`([])、`content_map`(15，含两图文字与像素盒)、`time_axis` | 该文件 |
| 不捏造冲突、不调整输入时间 | 逐会场相邻区间相交判定得 0 冲突；跨会场 16 组并行单列为 informational 且 `is_conflict:false`；`layout_checks.input_times_modified: false` | `conflicts` / `cross_venue_parallel_informational` |

## 实际应用的文档与标签能力

沿用共享准备阶段缓存的 `/ai-guide.md`、`/openapi.yaml`、`/reference/parser-tags/` 等文档
（`tmp/<run_id>/_suite/docs/`），本题新增使用：

- `Container` 的 `gradientType/gradientColors/gradientStops/gradientBegin/gradientEnd` 做块面渐变；
  `boxShadow="0 6 18 0 #00000055 NORMAL"` 自定义阴影（8 位色为 RRGGBBAA）。
- `Border` + `position` 默认背景装饰：午休标签用 `Border(border="1 SOLID #FDE68A", boxShadow="ELEVATION_4")`。
- `Row(mainAxisSize="MAX", mainAxisAlignment="CENTER")` 让“编号+类别”在窄块内水平居中。
- `Positioned(left, top, width)` 提供紧宽度约束，使 `Text` 的 `textAlign="CENTER"` 生效。
- 半透明色块 `#FBBF241A`（RRGGBBAA）绘制午休带底。

## 设计选择

1. **泳道给时间形状，索引给文字**：1920px 下 1 分钟只有 3.97px，任何“把标题塞进块里”的做法
   都必然拉长短块；因此块内只保留不可能说谎的字段（编号、起止、类别），标题与讲者交给编号索引。
2. **窄块改两行时间**：S06(139px)、S15(119px) 放不下 `10:15–10:50`（18px 约 118px），
   与其缩到 16px 违反“时间标签≥18”，不如把起止竖排，宽度保持真实。
3. **冲突与并行分开陈述**：题面要求“不捏造冲突”，故 `conflicts` 严格为空，
   同时把 16 组跨会场并行作为 informational 单列，避免读者把并行误读为冲突或把空数组误读为漏检。

## 实际问题与修复

| # | 现象 | 根因 | 修复 | 验证 |
|---|---|---|---|---|
| 1 | 生成期断言失败 `FOOT_Y+48=1242 > 1200` | 首版泳道 150px + 索引 5×82 超出画布 | 泳道/块/索引行整体压缩，页脚并为单行 | v002 起两图 200 OK |
| 2 | 大图 `16:00` 轴标签被右边界裁切 | `label` 用 `anchor="left_top"`，盒从刻度起算 | 改为 `center_top` 并以刻度为中心 | `zoom-v003-axis.png` |
| 3 | “时间轴（Asia/Shanghai）”与“编号索引”标题重叠 | 两者 y 区间相交且都靠左 | 说明改为右对齐并下移 2px | 同上 |
| 4 | 手机图 S15 标题压在页脚文字上 | 15×(56+6) 超出可用高度 | 卡片 56→54、间距 6→5、标题行上移 | `v003-mobile.png` |
| 5 | 短块缺类别文字 | 4 行文本在 96px 块内放不下 | 块高 104，短块改为“编号+类别”同行 + 起止两行 | `zoom-v006-dense10.png` |
| 6 | S06 编号被绘制两次、与类别重叠成乱码 | 独立编号标签在 if/else 之外无条件追加 | 把独立编号标签移入宽块分支 | v005→v006 对比 |

## 未解决事项

- 无影响交付的已知缺陷。次级观察：窄块（S06/S15）内不含标题，标题仅在编号索引中可读——
  这是题面“短活动通过外侧说明或编号索引解决文字空间”明确允许的方式，并已在读图方法中写明。
- `queue_wait_seconds` 记为 `null`：本次 `Server-Timing` 只返回 `render/total`，无 `queue` 段，
  不能据此断言未发生排队。

## 文件清单

| 路径 | 说明 |
|---|---|
| `agenda-wide.png` / `agenda-wide.snapshot` | 1920×1200 泳道日程（v006-wide 原始响应） |
| `agenda-mobile.png` / `agenda-mobile.snapshot` | 720×1280 分时段导览（v006-mobile 原始响应） |
| `schedule-audit.json` | 时长、空档、冲突、两图内容映射与时间轴映射 |
| `task-metrics.json` | 起止/墙钟、8 次渲染、10 次看图、6 条迭代 |
| `tmp/<run_id>/A02/requests.jsonl` | 渲染请求逐条留痕 |
| `tmp/<run_id>/A02/iterations.jsonl` | v001→v006 版本链 |
| `tmp/<run_id>/A02/image-views.jsonl` | 10 次实际看图（整图 + 1.5–2.2× 局部） |
| `tmp/<run_id>/A02/v001..v006-*.{snapshot,png}` | 全部尝试版本，未覆盖 |
| `tmp/<run_id>/A02/gen.py` | 数据计算 + 两图 DSL 生成脚本 |
