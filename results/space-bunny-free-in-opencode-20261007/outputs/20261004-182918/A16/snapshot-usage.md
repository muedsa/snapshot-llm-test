# A16 · 从错误图表恢复可信叙事 — snapshot-usage.md

- **状态**：completed（指定交付 1 张 1280×900 PNG + 同名 DSL，附加 JSON 2 份，报告与指标各 1 份）
- **输出目录**：`outputs/20261004-182918/A16/`
- **临时目录**：`tmp/20261004-182918/A16/`（脚本、逐版 DSL、预览图、放大裁图、文档、失败响应、requests.jsonl、iterations.jsonl）
- **run_id**：20261004-182918（沿用套件 run_id，未另建）
- **服务**：`POST https://open-snapshot.muedsa.com/snapshot`（snapkit.py 带浏览器 UA），全部图片为服务响应原始字节，无后处理
- **墙钟**：1132.0 s；其中请求耗时合计 27.31 s（6 次渲染 + 6 次文档/字体读取）；无用户反馈等待

## 1. 实际使用的服务文档与字体（均为本题真实抓取，HTTP 200）

| 资源 | 状态 | 落盘位置 | 实际用到什么 |
|---|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 200 | `tmp/.../A16/docs/ai-guide.md` | 确认请求体是 UTF-8 纯文本 DSL、响应体是图片二进制、`#RRGGBBAA` 透明度在最后两位、错误为含 `code/message/requestId` 的 JSON、`X-Request-Id` 可关联 |
| `https://open-snapshot.muedsa.com/fonts` | 200 | `tmp/.../A16/fonts-list.txt` | 27 个可用字体族；本题只用 `Inter` + `Noto Sans CJK SC` |
| `https://snapshot.muedsa.com/` | 200 | `docs/snapshot-docs-index.html` | 文档导航结构，确认参考页路径 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 200 | `docs/parser-tags.html`（另存纯文本 `parser-tags-plain.txt`） | 确认 `Text` 的 `fontSize/fontFamily/fontStyle(NORMAL·BOLD·ITALIC)/textAlign/softWrap/maxLines/letterSpacing/fontFeatures/baselineMode`，`Container` 的 `color/border/borderRadiusTopLeft…/boxShadow/gradient*`，`Stack` 的 `fit=EXPAND` 与 `Positioned` 定位 |
| `https://snapshot.muedsa.com/guides/widgets/` | 200 | `docs/guide-widgets.html` | 确认 `Positioned`/`Stack`/`ClipRRect`/`Container` 的用法与嵌套约束 |
| `https://snapshot.muedsa.com/guides/layout/` | 200 | `docs/guide-layout.html` | 确认绝对定位布局的约束行为 |

字体：`fontFamily="Inter,Noto Sans CJK SC"`（拉丁优先、缺字自动回退）。题库手册里的字体清单来自早前任务的真实 `GET /fonts`；本题**又独立抓取了一次**并落盘，未凭记忆臆造字体名。

## 2. 实际用到的标签与属性

`Snapshot`（`type`/`background`）→ `Container`（画布尺寸 + 卡片背景/柱体/圆点）→ `Stack fit="EXPAND"` → `Positioned`（全绝对定位）→ `Text`（`text`/`fontSize`/`fontFamily`/`fontStyle="BOLD"`/`color`/`textAlign="CENTER|RIGHT"`/`letterSpacing`/`fontFeatures="tnum=2"`）。
几何：`border`/`borderRadius`/`borderRadiusTopLeft`/`borderRadiusTopRight`/`boxShadow`；网格线与轴线用 1–2px 的 `Container` 拼接（DSL 无直线图元、无虚线边框）。

**本题踩到的 DSL 语义坑（都是真实失败/真实看图发现的）**

1. `Container` 只能有**一个**子节点。把多个 `Positioned` 直接放进卡片 `Container` → `400 PARSE_ERROR: Tag Container only can have one child`（失败响应留存于 `responses/resp-A16-req-006-*.txt`）。修法：卡片内容先包一层 `Stack`。
2. `Stack` 会把子节点坐标**重新基于自身原点**。把全画布 Stack 放进 `Positioned left=56 top=158` 的卡片里，卡片内所有绝对坐标被整体平移 (+56,+158) 并裁切——渲染“成功”但图是错的。修法：内容 Stack 放在 `(0,0)`、尺寸 `1280×900`，坐标始终使用整页坐标。
3. `textAlign` 依赖固定宽度文本框；`dsllib` 的 `est_width()` 会在放不下时给出 `D.warnings()`，必须逐条处理（v01 的页脚告警“需 2 行但框高只容 1 行”就是靠它发现的，随后把页脚文案缩短到单行）。
4. 1px 细线（网格线）在渲染后是**两行**混色（DSL `#E6EAF2` 叠白 → 实测 `(242,244,248)`），做像素复验时不能按原始色值匹配。
5. 圆角柱顶（`borderRadiusTopLeft/Right=8`）会让按“左边缘列”测柱高偏小；复验必须在柱的水平中心列取样，并按抗锯齿行的 alpha 覆盖率做亚像素还原。

## 3. 逐项自检表（TASK.md 硬指标 → 实际值 → 结论）

复验脚本 `verify_final.py` → `tmp/.../A16/verify-final.json`（16 项全部 PASS）。

| TASK.md 要求 | 实际值 | 结论 |
|---|---|---|
| 1280×900 | PNG 实测 1280×900，`IEND` 完整，PNG/RGBA | ✅ |
| 四季收入/成本分组柱图 | 4 组 × 2 根 = 8 根柱，组内收入在左、成本在右 | ✅ `bars_8_count` |
| 共同零起点 | 8 根柱底边全部在 y=529；最下方网格线解码为 **0.000 万元** | ✅ `all_bars_share_zero_baseline`、`zero_baseline` |
| 轴定义完整 | 刻度 0/50/100/150/200，实测解码 `{0:0.0, 50:50.0, 100:100.0, 150:150.0, 200:200.0}`，实测比例尺 1.420000 px/万元（= DSL 值） | ✅ `gridline_count/values/geometry` |
| 柱高对应数值（不能只改标签） | 8 根柱实测柱顶与 `530 − value×1.42` 的最大偏差 **0.56 px**（栅格噪声容差 0.6 px ≈ 0.42 万元）；逐根 `px/万元` 落在 1.4138–1.4245 | ✅ `bar_heights_match_csv`、`single_common_scale` |
| 利润明细 | 4 行（收入/成本/利润/利润率）× 5 列（Q1–Q4 + 全年）：120/135/128/180/563、90/108/96/126/420、30/27/32/54/143、25.0%/20.0%/25.0%/30.0%/25.4% | ✅ 数值全部由 CSV 现算 |
| 一条有数据依据的标题 | “季度复盘：Q4 利润 54 万元居首，占全年利润的 37.8%”（54=180−126，37.8%=54÷143） | ✅ 标题字符串由 `corrected-data.json` 计算生成 |
| 图例 | 蓝 `#2563EB`=收入、橙 `#F97316`=成本，实测色块 bbox 蓝 (1032,192)-(1049,209)、橙 (1126,192)-(1143,209)，蓝在左 | ✅ `legend_present`、`legend_order_revenue_first` |
| 单位“万元” | 面板标题“收入与成本对比（单位：万元）”“利润明细（单位：万元）”，页脚再写“纵轴 0–200 万元，刻度 50 万元” | ✅ |
| 全部季度 | Q1–Q4 在柱图、利润表、提示卡依据中均出现 | ✅ |
| 重点季度由数据论证 | 提示卡“重点观察 · Q4”，五条依据：收入 180 最高、成本 126 同步走高、利润 54 四季居首、利润率 30.0% 最高、占全年利润 37.8% | ✅ `corrected-data.json.key_quarter_argument` |
| 正文 ≥22 | 副标题 22、利润表数据 22、提示卡要点 22、面板标题 24/26、主标题 40 | ✅ |
| 标注 ≥18 | 轴刻度 18、柱顶数值 18、季度分组标签 20、图例 20、表头 18、页脚/眉标 18 | ✅（DSL 内 fontSize 仅 18/20/22/24/26/40） |
| 无外部图像 | DSL 中只出现 `Snapshot/Container/Positioned/Stack/Text`，无 `<Image>`、无 `dataUri` | ✅ |
| 保持“季度复盘”主题、风格允许改进 | 保留季度复盘框架（眉标 + 主标题 + 副标题 + 分组柱图 + 利润明细 + 重点观察） | ✅ |
| 附 findings.json | 10 条问题（位置/现象/源数据核对/影响/修正/最终查看结果）+ 5 条不确定项 + 原图像素测量 + 复验摘要 | ✅ |
| 附 corrected-data.json 的计算与轴定义 | `derived_fields`（利润/利润率/成本率/环比/全年口径）、`axis`（域、刻度、像素比例、柱宽、组距、组中心、系列顺序、配色）、`bar_geometry`（8 根柱的 x/y/高度） | ✅ |

## 4. 诊断与修复一览（详见 `findings.json`）

| # | 原图问题 | 关键证据 | 修法 | 复验 |
|---|---|---|---|---|
| F01 | 标题称 Q3 利润最高 | 标题墨迹 (56,46)-(428,81)；CSV 利润 30/27/32/54 | 改为 Q4 54 万元、37.8% | 最终图标题与利润表一致 |
| F02 | 副标题称收入持续上升 | Q3 收入 128 < Q2 135（环比 −5.2%） | 改为全年合计 + Q3 回落 5.2% | 像素上 Q3 柱低于 Q2 柱 |
| F03 | 图例蓝=成本、橙=收入 | 蓝块 (877,183)-(896,202) 标“成本”，但蓝柱标签 120/135/128/180 = revenue_wan | 蓝=收入、橙=成本，顺序同柱序 | 按颜色像素定位色块与柱体复核 |
| F04 | 纵轴 100–200 截断，无 0 | 网格线 y=295…565，最低价签 100；8 根柱底边都在 565 | 0–200、刻度 50、零基线 2px 加粗 | 5 条网格线解码 0/50/100/150/200 |
| F05 | 柱高与标签、与刻度都不对应 | 按自带刻度反读得 140–190 万元；8 根柱隐含比例尺 1.222–1.531 px/万元；标签 128 的柱(196px)高于标签 135 的柱(170px) | 柱高 = value × 1.42，柱底统一 530 | 8 根柱偏差 ≤0.56 px，单一比例尺 |
| F06 | 组内视觉差与利润表矛盾 | 视觉差 39/36/69/80 px = 14.4/13.3/25.6/29.6 万元，利润表写 30/27/42/54 | 几何与表格同源 | Q4 柱顶差 = 54×1.42 = 76.7 px |
| F07 | 利润 Q3 算错（42） | 128 − 96 = 32 | 全部由 CSV 现算，并补全年列与利润率行 | 利润行 30/27/32/54/143 |
| F08 | 提示卡指向 Q3 | 同页利润表已写 Q4=54 > Q3=42 | 改为 Q4 并列五条可核对依据 | 五条依据全部可回算 |
| F09 | 柱顶数值字号过小 | 墨迹高 10–11px（≈14–15px） | 统一 18px + `tnum=2` | 标注区墨迹实测 |
| F10 | 缺全年口径与利润率 | 明细卡只有四个利润数字 | 4 行 × 5 列表格，全年列竖线分隔 | 墨迹未越出卡片 |
| U01–U05 | 单位位置、图例顺序、柱底 1px 差与柱距、配色取值、未标来源 | — | 作为**不确定项**单列，不当作数值错误 | 见 `findings.json.uncertain_items` |

## 5. 迭代过程（iterations.jsonl，6 版）

| 版本 | 类型 | 看图发现 | 改动 |
|---|---|---|---|
| v01 | baseline | 无图：400 `PARSE_ERROR Tag Container only can have one child` | 失败响应已留存 |
| v02 | syntax-fix | 卡片内容整体平移 +56/+158 并被裁切，图例被右边界切掉 | 定位为嵌套 Stack 重置原点 |
| v03 | visual | 版面正确，但利润率行显示 0.2%/0.3%；“万元”与“200”刻度上下相挤 | 比率 ×100；单位并入面板标题 |
| v04 | visual | 数值全对，但 18px 面板副标题与“正文≥22”有歧义 | 删除该副标题，移入页脚注记 |
| v05 | visual | 无重叠；放大后见利润表末行距卡片底仅 3px | 利润表整体上移 4px |
| v06 | visual（**最终**） | 整图 + 5 处放大均无重叠/截断；`verify_final.py` 16/16 PASS | 无 |

渲染 6 次（1 次失败、5 次成功、0 次重试），完整视觉迭代 4 次。`iterations.jsonl` 记录 5 次版本级查看（v02–v06）；用视觉工具实际打开图片共 **14 次**：参考原图 1 次 + 原图局部放大 2 次、预览版 4 次 + v05 局部放大 3 次、最终图 1 次 + 最终图局部放大 3 次。

> 留痕说明：`log_a16.py` 曾被误执行两次，第一次追加的 6 行迭代记录被第二次完整重复了一次。已用脚本内去重逻辑（按 `iteration_id` 只保留首次出现）把 `iterations.jsonl` 从 12 行还原为真实的 6 行，并以 `--metrics-only` 模式重建 `task-metrics.json`，因此指标里的 `image_views=5`、`completed_visual_iterations=4` 是去重后的真实值。

## 6. 未解决事项与如实说明

1. **像素复验的分辨率极限**：1 px = 0.70 万元。柱顶亚像素还原与 DSL 计算位置最大偏差 0.56 px，因此像素级复验只能保证 ±0.4 万元；此限制已写入 `findings.json.verification_summary.rasterisation_limit`，未按“精确到分位”宣称。
2. **原稿部分细节无法判定**：柱底蓝 563 / 橙 564 的 1px 差、64px 柱宽与 12px 组距、#245CE4/#E88E35 配色，均无证据判定是错误还是设计，已作为 U02–U04 记录。
3. **未提供的计量**：token、图像输入量、费用在服务响应与平台侧都没有可读指标，`task-metrics.json` 中一律 `null`，未按字数或文件大小估算。
4. **排队/限流等待**：服务响应未报告 queue 段，`rate_limit_or_queue_wait_seconds` 记为 `null`（不是 0）。
5. 本题只交付 1 张指定 PNG（`task.json` 只要求 1 张）；预览图与放大裁图都在临时目录，不计入交付。

## 7. 交付文件

| 文件 | 说明 |
|---|---|
| `corrected-report.png` | 1280×900，服务真实响应原始字节（`IEND` 完整，175164 bytes） |
| `corrected-report.snapshot` | 与最终 PNG 逐字节一致的完整 DSL（17766 bytes，297 行，无 `<Image>`） |
| `findings.json` | 10 条问题 + 5 条不确定项 + 原图测量 + 复验摘要 |
| `corrected-data.json` | 数据、计算口径、轴定义、8 根柱像素几何 |
| `snapshot-usage.md` | 本文件 |
| `task-metrics.json` | 请求/迭代/耗时/看图统计（由 `finalize.py` 生成） |