# A15 reconstruction comparison

Reference and final were actually viewed at original size, thumbnail size and 2× local crops. Detailed evidence is in `reconstruction-audit.json`.

## Anchor measurements

| Anchor | Reference | Measured final | Max component error | ≤8 px |
|---|---|---|---:|---|
| sidebar_right | `220` | `220` | 0 | True |
| selected_nav | `[18, 116, 202, 164]` | `[18, 116, 202, 164]` | 0 | True |
| title_glyph | `[261, 39]` | `[261, 39]` | 0 | True |
| kpi_revenue | `[260, 138, 616, 282]` | `[260, 138, 616, 282]` | 0 | True |
| kpi_orders | `[644, 138, 1000, 282]` | `[644, 138, 1000, 282]` | 0 | True |
| kpi_refund | `[1028, 138, 1384, 282]` | `[1028, 138, 1384, 282]` | 0 | True |
| chart_card | `[260, 310, 1002, 596]` | `[260, 310, 1002, 596]` | 0 | True |
| zero_left | `[333, 549]` | `[333, 549]` | 0 | True |
| last_bar_top | `[888.5, 420]` | `[888.5, 420]` | 0.0 | True |
| activity_card | `[1030, 310, 1400, 596]` | `[1030, 310, 1400, 596]` | 0 | True |
| projects_card | `[260, 624, 1400, 842]` | `[260, 624, 1400, 842]` | 0 | True |
| last_status | `[1028, 799, 1176, 827]` | `[1028, 799, 1175, 827]` | 1 | True |

## Chart proportions

| Month | ¥ thousand | Reference bbox | Final bbox | Height error |
|---|---:|---|---|---:|
| Apr | 54 | `[357, 485, 411, 549]` | `[357, 485, 411, 549]` | 0 |
| May | 72 | `[458, 463, 512, 549]` | `[458, 463, 512, 549]` | 0 |
| Jun | 63 | `[559, 474, 613, 549]` | `[559, 474, 613, 549]` | 0 |
| Jul | 90 | `[660, 441, 714, 549]` | `[660, 441, 714, 549]` | 0 |
| Aug | 81 | `[761, 452, 815, 549]` | `[761, 452, 815, 549]` | 0 |
| Sep | 108 | `[862, 420, 916, 549]` | `[862, 420, 916, 549]` | 0 |

Scale is 1.2 px per ¥ thousand. All six bar boxes, all five grid endpoints and the zero line match the measured reference exactly.

## Table badges

| Project | Status | Reference bbox | Final bbox | Max component error |
|---|---|---|---|---:|
| Atlas / Visual system | In progress | `[1028, 729, 1176, 757]` | `[1028, 729, 1175, 757]` | 1 |
| Pulse / Dashboard | Review | `[1028, 764, 1176, 792]` | `[1029, 764, 1175, 792]` | 1 |
| Orbit / Launch | Done | `[1028, 799, 1176, 827]` | `[1028, 799, 1175, 827]` | 1 |

## Color review

| Role | Visual judgment | Pure-color samples exact |
|---|---|---|
| main_background | 冷灰蓝背景，明度高、饱和度低；参考与重建的色相、明暗及承托卡片的角色一致。 | True |
| sidebar | 深蓝黑侧栏，低明高对比；参考与重建均为相同深蓝角色，导航与品牌标识清晰。 | True |
| primary_blue | 鲜明钴蓝主色，色相偏蓝、明度中等；柱图、选中点和主按钮的角色与参考一致。 | True |
| card | 中性白色卡片，与冷灰背景形成高明暗差；参考与重建在相同背景下均呈相同白灰层次。 | True |
| status_in_progress | 浅蓝紫状态底，低饱和、高明度；与蓝色文字配合表达进行中，色相和明暗一致。 | True |
| status_review | 浅暖黄状态底，低饱和、高明度；与棕黄文字配合表达待审，色相和明暗一致。 | True |
| status_done | 浅薄荷绿状态底，低饱和、高明度；与深绿文字配合表达完成，色相和明暗一致。 | True |

## Actual visual observation
已实际查看 1440×900 原图、720×450 缩略图、左右并排缩略图、七组同背景色卡，以及侧栏、标题/KPI、图表、活动、表格五处 2× 局部。侧栏右缘、选中导航、三张 KPI、图表卡、活动卡、项目卡、标题字形、零线、末柱顶部和末行标签均与参考对齐；六个柱体比例和五条网格准确，三行项目顺序与蓝/黄/绿状态编码完整。未发现文字缺失、遮挡、裁剪或图表越界。残余差异为字体字形/字距、边缘抗锯齿及状态标签可见右缘最多 1px。

## Changes
v001 修正图表坐标基准与品牌标志环；v002 校准图表为 1.2px/千单位并修正标题字形位置；v003 修正零线、网格、标签框与卡内布局；v004 将全部 Text 内容改用 Raw/CDATA，精确保留双空格、货币符号、Unicode 减号、间隔号与箭头，并完成原尺寸/缩略/局部回归。

## Residual differences
- 选用服务实际可用的 `Noto Sans CJK SC`；参考字体未公开，因此字形轮廓、字距、基线细节和文字边缘抗锯齿不宣称逐像素相同。
- 三个状态标签的可见纯色右缘存在 0–1 px 差异，远低于 ±8 px 容差；不影响状态编码。
- 卡片阴影和边框的亚像素抗锯齿可能存在细微差异；主要外框均按可见像素实测。
- 未发现内容缺失、图表比例错误、遮挡、裁剪或表格顺序/状态错误。

## Content and service provenance
All source strings are preserved literally through Raw/CDATA, including the double-space arrow, en dash, Unicode minus and middle dot. The final PNG is byte-identical to a successful service response and the final DSL matches the submitted UTF-8 request. No reference image or crop is embedded in the DSL.
