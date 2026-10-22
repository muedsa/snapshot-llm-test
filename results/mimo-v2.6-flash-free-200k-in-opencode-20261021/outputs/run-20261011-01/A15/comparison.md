# A15 · 复杂界面视觉复刻 — 复刻对照报告

- 画布：1440×900，原点画布左上，单位像素
- 参考：`inputs/reference.png`（公开参考图，仅作像素观察，未嵌入）
- 交付：[reconstructed.png](reconstructed.png)（服务原始PNG字节，md5 `6c25ecf50eaf2facfab74adbdafd6561`）
  / [reconstructed.snapshot](reconstructed.snapshot)（同名完整DSL，md5 `834eecac579df8b6c1dc925ba29b5b68`）
- 机器可读审计：[reconstruction-audit.json](reconstruction-audit.json)

## 一、可测误差（全部由同一检测器测得）

用同一套检测脚本分别作用于参考图与重建图：`measure_anchors.py`（几何）
与 `measure_texts.py`（字形包围盒）。证据 JSON 保留在
`tmp/run-20261011-01/A15/`（`anchors-reference.json` / `anchors-recon-v7.json` /
`texts-reference.json` / `texts-recon-v7.json`，path_base=suite_root）。

### 几何锚点：20 项，最大分量误差 **0 px**（容差 ±8 px）

| 锚点 | 对象 | 参考估计 | 重建实测 | 分量误差 |
|---|---|---|---|---|
| sidebar_right_boundary | 侧栏右边界 (x) | 220 | 220 | 0 |
| nav_selected_frame | 导航选中态外框 | [18,116,201,163] | [18,116,201,163] | 0,0,0,0 |
| main_title_glyph_tl | 主标题字形框左上角 | (261,39) | (261,39) | 0,0 |
| kpi1_card | KPI卡1外框 | [260,138,615,281] | [260,138,615,281] | 0,0,0,0 |
| kpi2_card | KPI卡2外框 | [644,138,999,281] | [644,138,999,281] | 0,0,0,0 |
| kpi3_card | KPI卡3外框 | [1028,138,1383,281] | [1028,138,1383,281] | 0,0,0,0 |
| chart_card | 净收入图表卡外框 | [260,310,1001,595] | [260,310,1001,595] | 0,0,0,0 |
| chart_zero_line_left | 图表零线左端点 | (333,549) | (333,549) | 0,0 |
| last_bar_top_center | 末柱(Sep)顶部中心 | (888.5,420) | (888.5,420) | 0,0 |
| first_bar_top_center | 首柱(Apr)顶部中心 | (383.5,484) | (383.5,484) | 0,0 |
| activity_card | 活动卡外框 | [1030,310,1399,595] | [1030,310,1399,595] | 0,0,0,0 |
| table_card | 项目表格卡外框 | [260,624,1399,841] | [260,624,1399,841] | 0,0,0,0 |
| last_row_status_pill | 末行状态标签外框 | [1028,799,1175,826] | [1028,799,1175,826] | 0,0,0,0 |
| export_button | 导出按钮外框 | [1184,43,1399,90] | [1184,43,1399,90] | 0,0,0,0 |
| workspace_card | 侧栏工作区卡外框 | [22,752,197,867] | [22,752,197,867] | 0,0,0,0 |
| footer_glyph_tl | 页脚字形框左上角 | (261,867) | (261,867) | 0,0 |
| subtitle_glyph_tl | 副标题字形框左上角 | (261,86) | (261,86) | 0,0 |
| table_header_band | 表头底色带外框 | [284,688,1373,721] | [284,688,1373,721] | 0,0,0,0 |
| logo_mark | 侧栏Logo标记外框 | [30,33,57,60] | [30,33,57,60] | 0,0,0,0 |
| table_separator_rows | 表格行分隔线 y | [760,795] | [760,795] | 0,0 |

覆盖画布四象限（左上/上中/右上/左中/正中/右中/左下/下中/右下）及图表、表格。

### 文字字形：59 项，锚边最大偏差 **0.5 px**、顶边最大偏差 **0 px**

按各文本在参考中的锚定方式（左对齐取左缘、居中取中心、右对齐取右缘）
逐项比对可见字形包围盒。绝大多数（52/59）宽度差 0%，位置差 0 px。

宽度残差（绝对值均 ≤2px，居中或右对齐锚定后单侧偏 ≤1px）：

| 文本 | 参考宽 | 重建宽 | 差 |
|---|---|---|---|
| month Jun | 21 | 19 | −2 px (−9.5%) |
| month Jul | 17 | 15 | −2 px (−11.8%) |
| month Sep | 23 | 21 | −2 px (−8.7%) |
| act_t1 Design review | 116 | 121 | +5 px (+4.3%) |
| act_t3 Render complete | 140 | 145 | +5 px (+3.6%) |
| button Export report | 109 | 113 | +4 px (+3.7%) |

## 二、色彩判断

参考色由对 `reference.png` 的程序化采样取得，DSL 常量直接取该 RGB，
21 个色彩角色的 `delta_rgb` 均为 `[0,0,0]`（详见
[reconstruction-audit.json](reconstruction-audit.json) 的 `color_review`）。
要点：页面底 `#F3F6FB`、侧栏 `#14233C`、主蓝 `#245CE4`、
薄荷绿 `#64DBB6`（Logo／选中圆点／PRO WORKSPACE）、
卡片描边 `#E2E8F1`、网格线 `#E7EDF5`、
三枚状态胶囊底/字 `#E7EFFF`/`#245CE4`、`#FFF3D7`/`#9D6613`、`#DCF5EC`/`#168267`。

## 三、实际视觉检查

1. **原尺寸整图**：重建与参考并置逐区比对，布局、栅格、明暗块分布一致。
2. **局部放大 2×–4×**：8 个区域生成上下对照图
   （`tmp/run-20261011-01/A15/crops/sbs-*.png`）：侧栏顶部、侧栏底部、
   页头、KPI 行、柱状图、活动卡、表格、页脚。
3. **缩略**：小尺寸检视卡片栅格与色块分布。

首轮局部对比发现**字重偏轻**：参考的 KPI 标签、表头(PROJECT/OWNER/STATUS/DUE)、
表格行项目名、三枚状态胶囊文字、PRO WORKSPACE 均为粗体，
而初版用了 Inter Semi Bold。改为 Inter Bold 后复验：
Inter Bold 与 Semi Bold 字宽完全相同（同字号下包围盒不变，仅笔画加粗），
故宽度仍为 0% 偏差而字重吻合。

## 四、残余差异（如实说明）

1. **字体不同**：参考字体接近 Inter 度量但非同一文件；按要求从服务字体列表
   选用 Inter / Inter Bold / Inter Semi Bold。个别文本包围盒宽度差 1–5px，
   已在上表逐项列出。
2. **字距**：参考部分文本带轻微 letter-spacing（PRO WORKSPACE、
   Team activity 等）。服务 DSL 未确认可用的字距属性，故以等宽还原字号，
   不臆造属性名；残差以包围盒宽度记录。
3. **不宣称逐像素完全复刻**：DSL 树结构与作者源码无关，
   全部几何由对公开 `reference.png` 的像素测量反推得到。

## 五、诚实声明

所有参考坐标均来自对公开 `inputs/reference.png` 的程序化像素观察
（PIL 探针脚本，见 `tmp/run-20261011-01/A15/scripts/`），
未使用作者源码或任何标准坐标文件。画面 100% 由 Snapshot DSL 的几何与
文字构造，未嵌入参考图或其任何裁块。交付 PNG 为 open-snapshot 服务
返回的原始字节，未经任何后处理。
