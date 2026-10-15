# B04 · Snapshot DSL 应用记录

## 本题用到的文档

| 文档 | 用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 服务指南：渲染端点、尺寸约定、字体、错误处理 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 标签与属性总表 |
| *数据来源*：https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv · https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.txt | 两个真实公开数据集（见 [`sources.json`](sources.json)） |

## 视觉语言

十张共用一套**报刊式**版式，工具函数写在 `build_b04.py` 里：

- `masthead()` —— 眉题 + 大标题 + 导语 + 来源横线，四件套，每张图统一位置与字号。
- `footnote()` —— 脚注横线 + 文字，**按宽度折行**（见下）。
- `ramp()` —— 把气温距平映射到发散色带（冷 → 纸白 → 暖），线性分段插值、两端饱和。
- 纸白 `#F6F3EC` 打底，墨 `#16191F`，暖 `#C0392B`，冷 `#2C6E8F`，网格 `#D9D3C5`。

## 绘图手法

| 手段 | 用在哪 |
|---|---|
| `rect` 逐柱 / 逐格 | case 01 的 146 根柱、case 04 的 730 个色块、case 06 的计数块 |
| `polyline` | case 01 滑动平均、case 03 四条季线、case 05/07 的 CO₂ 曲线 |
| 发散色带 `ramp()` | case 01 柱色、case 02 条色、case 04 整个矩阵 |
| `circle` 空心描边点 | case 05 的 47 个年点、case 07 的 25 个月点 |
| 数字对齐 | 所有数值列都用定宽盒 + `textAlign` 左/右对齐成表 |

## 本题踩到的坑（都是 B03 记录的延续）

1. **脚注不会自动折行。** `bsnap.txt` 超出盒宽的部分被**静默裁掉仍返回 200**。
   case-05 的脚注原本写到「…不可」就断了；case-10 的三条说明各约 885px 而盒子只有
   836px，图上三条全都只剩半句。→ 把 `footnote()` 和 case-10 的条目都改成
   `bsnap.wrap` 折行，块高按折行后的**实际行数**算，不再写死。
2. **版面按算式估、结果要靠看。** 本题有五张图存在「纵向排到画布外」：
   case-02 汇总块 1108–1236 / 画布 1180；case-06 末行 918 / 画布 820
   （**后五行和整个汇总块都在画布外**，而标题却在说「从 0 到 5」）；
   case-08 表格 948 / 画布 920；case-09 汇总块 868 / 画布 860；
   case-07 块内末行 916 / 画布 940。渲染全部返回 200，**只有打开图才发现**。
3. **一处真正的数据错误**。case-07 的「同比 2025-07」用了 `CO2_RECENT[6]`，
   那是 2025-**01**（426.01），正确索引是 12（2025-07 = 424.09）。
   连带把「月均比一年前高 0.09 ppm」算错，正确值是 **+2.01 ppm**。
   → 修正后脚本里加了断言，固定这两处口径。
4. **后画的实心图元会盖住先画的文字**。case-08 的「全序列最高」原本写在
   for 循环里但没放进 `if`，导致**每一行都打**；case-03 的图例压在报头来源行上；
   case-02 的「基准期」标签跨过零线竖轴。

## 与 B03 的关系

B03 已经把「文字静默裁切」「滤镜只作用于子树」「后画盖先画」记成边界；
本题十张里出现了 **7 次**同类问题，说明这不是偶发，而是纯 DSL 的常态——
**每个字号都必须按 `char_em` 预算宽度，并且每张图都要真的打开看**。

## 资产政策

十张全部纯 DSL，**没有任何 `<Image>` 标签**、没有 base64、没有外部素材。

## 文件

- 十张：`case-01/` … `case-10/`（`final.png` + `final.snapshot` + `case.md`）
- 来源与抓取记录：[`sources.json`](sources.json) · 编辑手记与局限：[`editorial-note.md`](editorial-note.md)
- 大图：[`gallery.md`](gallery.md) · 索引：[`portfolio.md`](portfolio.md) · [`portfolio.json`](portfolio.json)
- 指标：`task-metrics.json`
- 过程证据：`tmp/run-20261011-01/B04/`（`data_b04.py`、`seasons_b04.py`、`build_b04.py`、
  `drafts/`、`preview/`、`responses/`、`requests.jsonl`、逐轮修正脚本）
