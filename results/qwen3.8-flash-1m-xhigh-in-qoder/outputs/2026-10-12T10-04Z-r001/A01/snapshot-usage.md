# A01 · 六个月经营诊断驾驶舱 — 使用与自检报告

- run_id：`2026-10-12T10-04Z-r001`（路径基准 `suite_root`，即本文件所在目录的上三级）
- 输出目录：`../../../outputs/2026-10-12T10-04Z-r001/A01/`
- 临时目录：`../../../tmp/2026-10-12T10-04Z-r001/A01/`

## 完成状态

completed。指定交付 `operations.png`（1600×1000，服务真实响应原始字节）与同名
`operations.snapshot`、附加 `computed-data.json` 均已就位。

## 需求逐项自检

| 要求 | 落实情况 | 证据 |
|---|---|---|
| 四张 KPI | 总净收入 91.86 万元、总经营利润 26.21 万元、总订单 3,045 笔、期间总体转化率 11.15% | [operations.png](operations.png) 第二行 |
| 净收入与经营利润分组柱图 | 6 组 × 2 柱，共用 0 起点与同一比例，纵轴 0–21 万元、步长 3 万元 | 主图卡片 |
| 访问量与转化率两个共享月份对齐的小图 | 两图使用同一 `si_l=1062`、`si_r=1528`、槽宽 77.67，逐月中心完全一致；生成脚本以断言保证 | `gen.py` 中 `side_chart()` 共用几何常量 |
| 六行明细表（月份/净收入/退款率/利润/转化率） | 6 行 + 合计行，金额整数元、比例两位小数 | 明细表卡片 |
| 有证据的管理结论 | 结论 + 3 条量化证据 + 建议框，全部数值来自 monthly.csv | 结论卡片 |
| 总体转化率用总订单/总访问 | 3,045 ÷ 27,300 = 11.15%，卡片副注明确标为“加权，非月均”；若误用月均为 11.19% | `computed-data.json` → `definitions` |
| 退款率 = 退款/退款前收入 | 逐月 5.00/5.00/8.00/5.00/8.00/4.00%，期间 5.79% | 明细表与 `monthly[]` |
| 柱图共用零起点与比例、负值处理 | 两列均为正值，`axes.grouped_bar_amount.note` 记录“无负值区间”，未虚构负轴 | `computed-data.json` |
| 百分比与金额不共用数轴 | 金额轴（万元）与百分比轴（%）分属不同卡片、各自独立刻度 | 主图 vs 转化率小图 |
| KPI 金额原值或万元换算 | 万元主值 + 元原值副注，两者可互相校验 | KPI 卡片 |
| 正文 ≥20、脚注 ≥16 | 明细表与 KPI 标签 20，结论标题 26、claim 20；刻度/脚注最小 16 | 见“实际问题”第 3 条修正记录 |
| 附 computed-data.json | 含逐月计算值、汇总、三条图轴定义与结论引用数值 | `computed-data.json` |

## 实际应用的文档与标签能力

先取回并通读 `https://open-snapshot.muedsa.com/ai-guide.md`、`/openapi.yaml` 与
`https://snapshot.muedsa.com/` 的 `/reference/parser-tags/`、`/guides/layout/`、
`/guides/rendering/`、`/guides/painting/`、`/guides/parser/`、`/reference/faq/`、
`/reference/enums/`（缓存于 `../../../tmp/2026-10-12T10-04Z-r001/_suite/docs/`）。

本图实际用到：

- `Snapshot background/type`：画布背景需显式设置，Parser 入口默认透明（`/guides/rendering/` 明确与 Kotlin 入口默认白色不同）。
- `Container`：`width/height`、`borderRadius`、`border="1 SOLID #223257"`、
  `gradientType/gradientColors/gradientStops/gradientBegin/gradientEnd`（卡片与柱体渐变）。
- `Stack` + `Positioned(left/top/right/bottom/width)`：整图绝对定位骨架。
- `Row/Column`：`crossAxisAlignment`、`mainAxisSize`、`textDirection`。
- `Text`：`fontSize/color/fontStyle/fontFamily/textAlign/softWrap/height/maxLines`。
- `Opacity`：背景光斑。
- 字体取自 `GET /fonts` 实际返回值：`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Inter`。

## 设计选择

1. **重点分层而非平均铺满**：视觉重量按 KPI（40px 数字）→ 主柱图（186px 高）→ 明细表 →
   结论递进；两个小图刻意压到 143px 高，只承担“逐月是否同步”的次要判断。
2. **万元轴 + 元原值**：柱顶用两位小数万元（11.97/3.77…）保证 40px 柱宽下可读，明细表保留
   整数元原值，页脚注明四舍五入规则，避免“同一数字两种精度”引起误读。
3. **转化率图配参考线**：0–15% 零基线柱图会显得几乎等高，因此叠加期间总体 11.15% 琥珀参考线，
   把“哪几个月低于总体”变成一眼可读的比较，而不是靠肉眼判断柱高差。
4. **结论可核验**：结论中每个数字（+60.0%、+69.1%、11.15%、8.00%、4.00%–5.00%、5.79%、
   173,052/161,120、49,120→41,052）都由脚本直接从 CSV 计算生成，不是手写文案。

## 实际问题与修复

| # | 现象（来自真实渲染） | 根因 | 修复 | 验证 |
|---|---|---|---|---|
| 1 | `400 PARSE_ERROR: Attr [borderRadius] value format error` | 文档只支持 `borderRadius="16"` 或四角单写属性，不支持 CSS 式 `"5,5,0,0"` | 改用 `borderRadiusTopLeft/borderRadiusTopRight` | `A01-render-002` 起不再报该错 |
| 2 | `400 RENDER_ERROR: Layout size is infinite` | 根 `Stack` 用 `fit="EXPAND"` 且全部子节点为 `Positioned`，在无界根约束下无尺寸 | 根改为固定 1600×1000 的 `Container`；每个 `Stack` 加一个非 Positioned 尺寸子节点；`Row/Column` 默认 `mainAxisSize="MIN"` | `A01-render-003` 成功出图 1600×1000 |
| 3 | 表格 2026-09 行与合计行被裁切、与页脚重叠；结论 4 条证据溢出卡片；页眉副标题被 KPI 卡遮住；主图“月份”轴标题落在卡片外 | 首版垂直预算（68/140/330/330）超出可用高度，且结论条目过多 | 重排为 76/132/302/384 并让表格与结论使用不同宽度切分（828 / 688）；结论精简为 3 条证据；删除越界轴标题，单位说明并入标题行 | `v005` 整图复查确认 |
| 4 | 小图月份标签压在卡片圆角边界外；刻度与柱顶数值 15px 低于 16px 下限 | 小图卡片仅 143px，内边距预算不足 | 绘图区改为 `y+40..y+114`，轴最大值调为 7,000 / 15%（配合步长 2,000 / 3% 只标 0,2000,4000,6000 与 0,6,12），标签统一提到 16px | `zoom-v006/007-side.png` 放大确认 |
| 5 | 结论卡片分隔线压在 claim 第二行“化率仅 11.15%。”上 | 证据区起点 `cy0+152` 小于 claim 两行的实际结束位置 | 顶部留白 20→14、块间距收紧、证据区起点下移到 `cy0+163`，建议框内边距 10→8 | `zoom-v008-conclusion.png` 确认已分离 |
| 6 | 页脚左句末尾“比”字丢失 | `Positioned` 宽度 900 小于文本实际宽度且未换行 | 左句宽度 900→1000、右句 560→480，两者之间保留 56px 间隙 | `v005` 起页脚完整 |
| 7 | 首次 `POST /snapshot` 返回 `403 error code: 1010` | 边缘节点按客户端签名拦截默认 `Python-urllib` UA | 渲染脚本显式设置 `User-Agent`（可用 `SNAPSHOT_USER_AGENT` 覆盖） | `SHARED-render-002` 起全部 200 |

## 未解决事项

- 无影响交付的已知缺陷。两点如实记录的次级观察：
  1. 转化率小图在零基线 0–15% 下柱高差异约 7px，主要靠数值标签与参考线传达；这是为满足
     “柱图共用零起点”与“百分比不共用混淆数轴”而做的取舍。
  2. `queue_wait_seconds` 记为 `null`：`Server-Timing` 只在发生槽位等待时返回 `queue` 段，
     本次响应仅见 `render/total`，无法据此断言“没有排队”，故不以 0 冒充。

## 文件清单

| 文件 | 说明 |
|---|---|
| `operations.png` | 1600×1000，服务原始响应字节（未后处理） |
| `operations.snapshot` | 与图片同名的完整 DSL |
| `computed-data.json` | 逐月计算值、汇总、三条图轴定义、结论引用数值 |
| `task-metrics.json` | 起止/墙钟、请求与迭代统计、看图次数 |
| `../../../tmp/<run_id>/A01/requests.jsonl` | 8 次渲染请求逐条留痕（含 2 次失败响应原文 `.resp`） |
| `../../../tmp/<run_id>/A01/iterations.jsonl` | v001→v008 版本链与逐次可观察问题 |
| `../../../tmp/<run_id>/A01/image-views.jsonl` | 9 次实际看图（整图与 1.6–2.0× 局部） |
| `../../../tmp/<run_id>/A01/v001..v008.snapshot/.png` | 全部尝试版本，未覆盖未清理 |
| `../../../tmp/<run_id>/A01/gen.py` | 数据计算 + DSL 生成脚本（相对 `SNAPSHOT_TASK_ROOT` 运行） |
