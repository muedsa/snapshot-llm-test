# A01 snapshot-usage · 六个月经营诊断驾驶舱

- 任务状态：completed（2026-10-16，run_id 20261016T164020-m1）
- 输出目录：`outputs/20261016T164020-m1/A01/`（path_base=suite_root）
- 状态 / 指标：任务账 1 份、轮次 1 轮（round_count=1，未分轮）。
- 交付文件：
  - `operations.png` + `operations.snapshot`（1600×1000，PNG，服务真实响应）
  - `computed-data.json`（schema_version=1，含 months/totals/axes/conclusion/formulas）
  - `task-metrics.json`；过程留痕在 `tmp/20261016T164020-m1/A01/`（requests.jsonl、iterations.jsonl、renders/）

## 文档与规范的真实施行

- 先读 [https://open-snapshot.muedsa.com/ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md)（服务接口：POST /snapshot、UTF-8 纯文本请求体、响应为图片二进制、错误处理与 /fonts），再读 DSL 文档站（parser、parser-tags、parser-text、text-layout、painting、gradients、box-shadow、enums、faq 等，全部缓存于 `tmp/20261016T164020-m1/docs/`，原始响应与请求记录在 `tmp/20261016T164020-m1/_suite/shared-requests.jsonl`）。
- 通过 `GET /fonts` 实际取得字体族（`tmp/20261016T164020-m1/docs/fonts-list.txt`）：中文用 `Noto Sans CJK SC`，拉丁数字用 `Inter`；组合写法 `fontFamily="Inter,Noto Sans CJK SC"`，逗号后不加空格。
- 应用要点（真实生效）：
  - 画布由布局决定：根 `<Stack>` + 首个非定位 `<SizedBox width="1600" height="1000">` 定尺寸；`background="#0B1526"`。
  - Panel 内子元素一律相对面板原点定位（初版曾用画布绝对坐标导致整体平移，v01 报错复检后改用基准换算）。
  - 柱图矩形顶部圆角用 `borderRadiusTopLeft/Right`；纯色圆点用 `shape="CIRCLE"`。
  - 斜线段用 `Transform matrix`（列主序 16 值）+ `alignment="CENTER_LEFT"`，将其作为 `Positioned` 尺寸盒的子节点，几何先经 atan2 计算，点位与线段端点一致。
  - 文本 `maxLines="1" overflow="CLIP"`，居中/右对齐配合 `Positioned width` + `textAlign`。
  - 数字用 Inter、千分位分隔，合计口径百分比两位小数（11.15%），KPI 保留金额原值（918,624 元 / 262,124 元）。

## 数据与几何核验（实测计算后再落图）

- 净收入=收入−退款、利润=净收入−成本逐月复核（例：5 月 142,600−7,130−93,500=41,970）。
- 总体转化率 = 3,045 ÷ 27,300 = 11.152559…→ 11.15%（非月平均）；期间利润率 = 262,124 ÷ 918,624 = 28.53%。
- 退款率：4/5/7 月 5.00%，6/8 月 8.00%（8 月退款 15,048 元），9 月 4.00%。
- 柱图轴 0–24 万元（万元与利润同轴同比例、零起点），网格 0/6/12/18/24；访问量轴 0–6,000 次；转化率轴 0–12.5%（网格 0/5/10）。金额与百分比数轴分离。
- 所有坐标、刻度像素点位已在 `computed-data.json` `axes` 中记录映射公式。

## 逐图自检（真实查看渲染图）

- v01（基线）：面板内部使用画布坐标 → 主图内容整体错位、小图空白。
- v02：修正坐标基准后整体正确；遗留：“万元”轴单位与标题重叠、两张小图月份标签（2026-04…）相邻盒宽 68px 与组距 66.7px 几乎重合连成一串。
- v03：小图月份改“04月…09月”，单位下移；复核通过。
- v04（最终）：小图注记 16→18px；数值、样式、布局、文字可读性全部复检通过；与 v03 对比无新增问题。
- 每一版均以实际 PNG 打开检查（4 次看图），未以 XML/HTTP 成功替代视觉检查。

## 请求与迭代统计

- 渲染请求 5 次（v01–v04，v04 因补丁脚本路径错误多渲染一次，结果与 v03 相同；全部 HTTP 200，image/png）。
- DSL 版本 4 个；完整视觉迭代：v02、v03、v04 计 3 次；失败请求 0；429/网络故障 0。
- 明细见 `tmp/20261016T164020-m1/A01/requests.jsonl`、`iterations.jsonl`、`task-metrics.json`。

## 差旅字体/兼容性注记

- Inter,Noto Sans CJK SC 混排数字与 CJK 均正确渲染（“N” 徽标、KPI 数值中 “ 元” 回落 Noto）。
- 正文（表格/结论/KPI 标签）20px，脚注与图表注记 16–18px，柱值/点值标签 18px，两个小图月份 18px。

## 未解决事项

- 无。
