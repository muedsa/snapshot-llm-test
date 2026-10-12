# A02 使用报告 · 三会场密集会议日程

状态：**completed**。基准目录：本文件位于 `outputs/<run_id>/A02/`，`path_base=suite_root`；
文中所有路径相对总任务根（由 `SNAPSHOT_TASK_ROOT` 给出，运行时为
`D:/mine/workspace/qwen-in-q`，记录时统一使用相对形式，遵循 `PATHS.md`）。

## 1. 交付物

| 文件 | 说明 |
|---|---|
| `outputs/<run_id>/A02/agenda-wide.png` | 1920×1200，服务真实响应，592,730 字节 |
| `outputs/<run_id>/A02/agenda-wide.snapshot` | 上图的完整 DSL，73,946 字节 |
| `outputs/<run_id>/A02/agenda-mobile.png` | 720×1280，服务真实响应，259,382 字节 |
| `outputs/<run_id>/A02/agenda-mobile.snapshot` | 上图的完整 DSL，31,596 字节 |
| `outputs/<run_id>/A02/schedule-audit.json` | 每场时长、各会场空档、冲突检查、两图内容映射 |
| `tmp/<run_id>/A02/generate_a02.py` | 读取 inputs 计算并生成 DSL 的脚本（当前版本） |
| `tmp/<run_id>/A02/v01..v04-*.snapshot` | 各版本 DSL 原件，未覆盖 |
| `tmp/<run_id>/A02/preview/` | 每次渲染的原始响应图（含被替换的版本） |
| `tmp/<run_id>/A02/zoom-*.snapshot` + `preview/zoom-*.png` | 1:1 局部检查用裁切 |
| `tmp/<run_id>/A02/requests/` | 每个请求的 body / response-headers / response.bin |
| `tmp/<run_id>/A02/requests.jsonl`、`iterations.jsonl` | 请求与迭代留痕 |
| `outputs/<run_id>/A02/task-metrics.json` | 汇总指标 |

最终 PNG 与已实际看过的预览图 SHA-256 相同（wide `4fc78876…`、mobile `c07510c6…`），
即交付图就是被视觉检查的那张，未做后处理。

## 2. 需求逐条自检

| 需求 | 实现 | 看图证据 |
|---|---|---|
| 三条会场泳道、09:00–16:00 共用线性轴 | 泳道 A/B/C 各 178px，轴 `LX=300→RX=1860`，`px/min = 1560/420 = 3.714` | v03-wide 全图 + zoom-lanes |
| 块位置与长度按真实起止比例 | 全部由 `tx(start)` 与 `dur*PX_PER_MIN` 计算，代码中无任何手工宽度 | 30 分钟块 111.4px、75 分钟块 278.6px，比例一致 |
| 空档保留 | 只画真实块；≥20 分钟空档在泳道空白处标出分钟数，跨午休空档按午休前后分段 | zoom-10am、v03-wide（B 泳道 “50 分”、C 泳道 “20 分”） |
| 12:00–13:00 午休跨三泳道、独立成带 | 单独 `#243450` 整高横带 + 四行说明，未与任何会议合并；audit 中 `sessions_overlapping_lunch` 为空数组 | v03-wide 中部 |
| 15 项编号/标题/讲者/起止/类别可读 | 块内显示编号、起止、标题、讲者（≥190px 时附时长）；类别以编号底色+竖色条+文字（宽度不足时省略文字）；全部 15 项在“编号索引”表中完整列出 | zoom-10am、zoom-s15、索引面板 |
| 短活动不靠拉伸时间解决 | 40 分钟仍为 148.6px（未画成 60 分钟）；短场改用两行起止 + 编号索引 | zoom-s15（S15 30 分钟 = 111.4px） |
| 正文 ≥20、时间标签 ≥18 | 标题 20、正文说明 18–20、时间 18/19；索引正文 18–19 | 1:1 裁切无缩放模糊 |
| 注明读图方法与会场容量 | 顶部三行“读图方法”；泳道卡 “容量 320/80/160 人” | v03-wide |
| 手机图为分时段列表，非缩小/裁切大图 | 720 宽单列列表，上午 8 场 / 午休 / 下午 7 场，独立 DSL | v04-mobile 全图 |
| 15 项保留编号、标题、会场、起止；注明讲者去向 | 每行含编号块、起止、会场、时长、类别、标题；顶部 “讲者详见完整日程” | v04-mobile + zoom-m-lunch |
| 手机正文 ≥18 | 最小字号 18 | 1:1 裁切 |
| `schedule-audit.json` | 每场时长与轴偏移、各会场空档（含午休标记）、冲突检查（同会场重叠=0，最大并行=3）、两图内容映射 | 文件本身 |
| 不捏造冲突、不调整输入时间 | 输入只读；冲突结论由代码比较得出（无重叠） | audit `conflict_check` |

## 3. 文档与 DSL 能力的实际应用

- 请求体仍是 `text/plain; charset=utf-8` 的原始 DSL；两次最终渲染均返回 `image/png`
  且带 `X-Request-Id` 与 `Server-Timing`（wide 最终 `render;dur=2747.2, total;dur=2960.7`，
  mobile 最终 `render;dur=415.9, total;dur=439.6`）。
- 复用 A01 已验证结论：`Stack clipBehavior="NONE"` + `Positioned` 绝对定位；
  `Container` 不设 width/height 于 `Expanded` 内；`Text` 会裁空白。
- 新增使用 `Transform.matrix` 旋转矩形绘制小时网格线（`dslkit.line()`），
  11 条网格线一次成功。
- 字体沿用 `Inter,Noto Sans CJK SC`（逗号连接、无空格），中英混排与 `·`、`–` 正常。
- 8 位十六进制色 `#0E183088`、`#38BDF866`（边框半透明）渲染正常。

## 4. 遇到的问题与修复

1. **v01 说明文字与时间轴标签重叠**：一段 110 字的 20px 说明在 1560px 盒内换行成 3 行，
   压住了 y=178 的整点标签。→ 改为每行不超过约 90 字的短句，并把轴下移到 y=176。
2. **v01 泳道卡“空档：…”列表被裁断**（`11:50–`、`14:15–` 截尾）：210px 宽、56px 高放不下
   5 段空档文字。→ 改为 “空档 5 段 · 155 分钟” 汇总，明细留在 `schedule-audit.json`。
3. **v01 窄块（S15 111px）文字被裁**：类别 “主旨” 只剩 “主”，`15:30–16:00` 被迫折行且
   讲者+时长溢出。→ 窄块（<150px）起止拆成 `15:30` / `– 16:00` 两行、标题下移；
   类别文字仅当 `块宽-78 ≥ 字数×18+4` 时才内嵌，其余由编号索引承载。
4. **v02 空档标注压在午休横带上**：B 泳道 11:10–13:00（110 分）、C 泳道 11:45–13:20（95 分）
   整体标注，文字落在午休带自身的说明上。→ 新增 `split_around_lunch()`，
   跨午休的空档按午休前后分段标注（B 显示 “50 分”，C 显示 “20 分”）。
5. **v02 泳道末行折行**：“首 09:00 开始 · 末 16:00 结束” 在 210px 内折行并贴卡片底。
   → 改为单行 “09:00 起 · 16:00 止”。
6. **v02 手机图底部溢出**：午休说明第二行被 46px 色带裁断，两行页脚贴到画布下沿被裁。
   → 行距 64→62、卡片 58→56、午休说明改单行，并在生成器加
   `assert y + 56 <= MH` 作为溢出保护（v04 通过）。

## 5. 统计与说明

- 渲染请求 13 次，全部 HTTP 200、全部返回 `image/png`：2 次基线（v01 wide/mobile）、
  4 次视觉迭代（v02 wide、v02 mobile、v03 wide、v04 mobile）、5 次 1:1 裁切检查
  （zoom-10am / s15 / lanes / m-lunch / m-foot）、2 次最终交付渲染。
  无 429/503，`Retry-After` 未触发，无失败响应，无重试。
- 服务端 `Server-Timing` 跨度较大：v02-wide 渲染 13.67s（该次为全图最重的一版），
  其余 0.21–2.96s；客户端总耗时（含 TLS 与传输）见 `task-metrics.json`。
- 完整视觉迭代：wide 2 轮（v01→v02→v03），mobile 2 轮（v01→v02→v04）。
- 实际打开图片 11 次：6 次作为基线/迭代查看记入 `iterations.jsonl`
  （`image_views=6`），另 5 次为 1:1 裁切检查（zoom-10am / s15 / lanes / m-lunch / m-foot），
  对应请求同样记入 `requests.jsonl`。
- 中途修正：`iterlog.py` 曾把 `--viewed <时间戳>` 当作布尔 false，导致 4 条 A02 记录
  `image_viewed=false`；已修脚本并用
  `tmp/<run_id>/_suite/scripts/fix_iteration_views.py` 回填（A01 的 5 条无需修正）。
  回填后的查看时间取记录写入时间，与实际看图时刻相差在 1–2 分钟内。
- `DSL_VERSION=v04` 运行生成器时同时写出了 `v04-wide.snapshot`（与 `v03-wide.snapshot`
  内容相同，因该轮只改手机图）；交付使用 `v03-wide`，重复文件保留在临时目录不删除。
- 未解决事项：无。可改进但本题未做：泳道卡 “155 分钟” 含与午休重叠的 60 分钟，
  若改为“不含午休”需拆成两行文字，当前宽度不足。
