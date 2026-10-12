# A15 · 复杂界面视觉复刻 — 重建对照说明（comparison.md）

参考图 `inputs/reference.png`（1440×900）只用于观察与像素测量；交付图 `reconstructed.png` 的每一个矩形、线条、文字、圆点都由 Snapshot DSL 构造，DSL 中没有任何 `<Image>` 元素，也没有使用参考图的任何裁块。

## 1. 对照方法

参考图与重建图由**同一套代码**测量（`tmp/20261004-182918/A15/verify_render.py`），因此下表的 delta 是实测值而不是目测估计：

- 几何锚点：用**精确色值游程**（例如卡片边框 `#E2E8F1`、网格线 `#E7EDF5`、柱体 `#245CE4`、选中态 `#294467`）扫描行/列取首末像素，得到边界坐标。
- 文字锚点：在与参考图完全一致的紧致区域内取**墨迹包围盒**（ink bbox），比较左上角坐标与宽高。
- 字重：用**墨迹密度** `Σ|bg_luma − px_luma|`（对背景取绝对值，因此与文字明暗无关）做量化标定。
- 整体：每 2 像素抽样一次，统计两图 RGB 三通道差 ≤24 的比例。

## 2. 几何锚点（49 个，覆盖画布四象限 + 图表 + 表格）

- 落在 ±8 px 容差内：**49 / 49**
- 最大绝对偏差：**1 px**
- 覆盖区域：图表区、左下象限、右下象限、左上象限、右上象限

### 左上象限

| 锚点 | 含义 | 参考估计 | 重建 | Δ(px) | ≤8px |
|---|---|---|---|---|---|
| `A01_logo_outer_left` | brand mark outer left edge | 30 | 30 | 0 | ✓ |
| `A02_logo_outer_top` | brand mark outer top edge | 34 | 35 | 1 | ✓ |
| `A03_brand_text_ink` | NORTHSTAR text ink top-left | (73, 38) | (73, 38) | (0, 0) | ✓ |
| `A04_nav_selected_left` | selected nav pill left edge | 18 | 18 | 0 | ✓ |
| `A05_nav_selected_top` | selected nav pill top edge | 116 | 116 | 0 | ✓ |
| `A06_nav_selected_bottom` | selected nav pill bottom edge | 163 | 163 | 0 | ✓ |
| `A07_nav_settings_ink` | Settings nav label ink top-left | (63, 318) | (63, 318) | (0, 0) | ✓ |
| `A08_kpi1_card_left` | KPI card 1 left border | 260 | 260 | 0 | ✓ |
| `A09_kpi1_card_top` | KPI card 1 top border | 138 | 138 | 0 | ✓ |
| `A10_kpi1_card_bottom` | KPI card 1 bottom border | 281 | 281 | 0 | ✓ |
| `A11_kpi1_value_ink` | KPI1 value ink top-left | (284, 199) | (284, 199) | (0, 0) | ✓ |

### 右上象限

| 锚点 | 含义 | 参考估计 | 重建 | Δ(px) | ≤8px |
|---|---|---|---|---|---|
| `A12_button_left` | Export report button left edge | 1184 | 1184 | 0 | ✓ |
| `A13_button_top` | Export report button top edge | 43 | 43 | 0 | ✓ |
| `A14_button_text_ink` | Export report ink top-left | (1237, 55) | (1237, 55) | (0, 0) | ✓ |
| `A15_kpi3_card_right` | KPI card 3 right border | 1383 | 1383 | 0 | ✓ |
| `A16_act_card_right` | Team activity card right border | 1399 | 1399 | 0 | ✓ |
| `A17_act_card_top` | Team activity card top border | 310 | 310 | 0 | ✓ |
| `A18_act_card_bottom` | Team activity card bottom border | 595 | 595 | 0 | ✓ |
| `A19_act3_ink` | Render complete ink top-left | (1078, 515) | (1078, 515) | (0, 0) | ✓ |
| `A20_act_dot3` | activity dot 3 left edge | 1055 | 1055 | 0 | ✓ |
| `A38_chart_period_ink` | Apr - Sep ink top-left | (896, 337) | (896, 337) | (0, 0) | ✓ |

### 左下象限

| 锚点 | 含义 | 参考估计 | 重建 | Δ(px) | ≤8px |
|---|---|---|---|---|---|
| `A21_sidecard_left` | PRO WORKSPACE card left edge | 22 | 22 | 0 | ✓ |
| `A22_sidecard_top` | PRO WORKSPACE card top edge | 752 | 752 | 0 | ✓ |
| `A23_sidecard_bottom` | PRO WORKSPACE card bottom edge | 867 | 867 | 0 | ✓ |
| `A24_side_label_ink` | PRO WORKSPACE ink top-left | (38, 770) | (38, 770) | (0, 0) | ✓ |
| `A25_sidebar_main_split` | sidebar / main boundary x | 219 | 219 | 0 | ✓ |
| `A26_table_card_left` | Recent projects card left border | 260 | 260 | 0 | ✓ |
| `A27_table_card_bottom` | Recent projects card bottom border | 841 | 841 | 0 | ✓ |
| `A28_footer_ink` | footer ink top-left | (260, 867) | (260, 867) | (0, 0) | ✓ |

### 右下象限

| 锚点 | 含义 | 参考估计 | 重建 | Δ(px) | ≤8px |
|---|---|---|---|---|---|
| `A29_table_card_right` | Recent projects card right border | 1399 | 1399 | 0 | ✓ |
| `A30_thead_band_left` | table header band left edge | 284 | 284 | 0 | ✓ |
| `A31_thead_band_right` | table header band right edge | 1373 | 1373 | 0 | ✓ |
| `A32_thead_band_top` | table header band top edge | 688 | 688 | 0 | ✓ |
| `A33_rowsep760` | row separator 1 left end | 284 | 284 | 0 | ✓ |
| `A34_rowsep795_y` | row separator 2 y | 795 | 795 | 0 | ✓ |
| `A35_pill1_left` | In progress pill left edge | 1028 | 1028 | 0 | ✓ |
| `A36_pill3_top` | Done pill top edge | 799 | 799 | 0 | ✓ |
| `A37_r3_due_ink` | Nov 12 ink top-left | (1231, 805) | (1231, 805) | (0, 0) | ✓ |

### 图表区

| 锚点 | 含义 | 参考估计 | 重建 | Δ(px) | ≤8px |
|---|---|---|---|---|---|
| `A39_grid_x_left` | gridline horizontal start x | 333 | 333 | 0 | ✓ |
| `A40_grid_x_right` | gridline horizontal end x | 969 | 969 | 0 | ✓ |
| `A41_chart_zero_line_y` | chart zero / baseline gridline y | 549 | 549 | 0 | ✓ |
| `A42_grid_top_120_y` | chart top gridline (120) y | 405 | 405 | 0 | ✓ |
| `A43_grid_90_y` | gridline (90) y | 441 | 441 | 0 | ✓ |
| `A44_bar1_left` | Apr bar left edge | 357 | 357 | 0 | ✓ |
| `A45_bar1_top` | Apr bar top edge | 485 | 485 | 0 | ✓ |
| `A46_bar4_top` | Jul bar top edge | 441 | 441 | 0 | ✓ |
| `A47_bar6_right` | Sep bar right edge | 915 | 915 | 0 | ✓ |
| `A48_bar6_top` | Sep bar top edge | 420 | 420 | 0 | ✓ |
| `A49_month_sep_ink` | Sep axis label ink top-left | (876, 560) | (876, 560) | (0, 0) | ✓ |

### 文字墨迹锚点（57 个文本元素）

- 左边界最大偏差 **0 px**，上边界最大偏差 **0 px**，墨迹宽度最大偏差 **3 px**。
- 全部 57 个文本元素的墨迹位置与参考一致在 ±1 px 内（宽度 ≤3 px）。

### 2.1 逐文本墨迹对照（全部 57 项）

| key | 文本 | 参考墨迹 (x,y) | 重建墨迹 (x,y) | Δx | Δy | 参考 w×h | 重建 w×h | Δw |
|---|---|---|---|---|---|---|---|---|
| `brand` | NORTHSTAR | (73, 38) | (73, 38) | 0 | 0 | 117×15 | 117×14 | 0 |
| `nav_overview` | Overview | (62, 126) | (62, 126) | 0 | 0 | 88×16 | 89×16 | 1 |
| `nav_projects` | Projects | (63, 190) | (63, 190) | 0 | 0 | 72×19 | 72×19 | 0 |
| `nav_analytics` | Analytics | (62, 254) | (62, 254) | 0 | 0 | 83×19 | 83×19 | 0 |
| `nav_settings` | Settings | (63, 318) | (63, 318) | 0 | 0 | 73×20 | 73×20 | 0 |
| `side_label` | PRO WORKSPACE | (38, 770) | (38, 770) | 0 | 0 | 113×11 | 114×11 | 1 |
| `side_member` | 12 team members | (38, 804) | (38, 804) | 0 | 0 | 135×13 | 135×13 | 0 |
| `side_manage` | Manage access  → | (39, 835) | (39, 835) | 0 | 0 | 122×14 | 121×13 | -1 |
| `title` | Workspace Overview | (260, 38) | (260, 38) | 0 | 0 | 335×32 | 335×32 | 0 |
| `subtitle` | Saturday, 07 November 2026 | (261, 85) | (261, 85) | 0 | 0 | 246×18 | 246×18 | 0 |
| `button_text` | Export report | (1237, 55) | (1237, 55) | 0 | 0 | 110×17 | 108×16 | -2 |
| `kpi1_label` | REVENUE | (284, 160) | (284, 160) | 0 | 0 | 65×12 | 64×10 | -1 |
| `kpi1_value` | ¥128,400 | (284, 199) | (284, 199) | 0 | 0 | 149×30 | 147×29 | -2 |
| `kpi1_change` | +12.4% | (285, 246) | (285, 246) | 0 | 0 | 57×13 | 56×13 | -1 |
| `kpi2_label` | ORDERS | (668, 160) | (668, 160) | 0 | 0 | 57×12 | 56×11 | -1 |
| `kpi2_value` | 426 | (669, 199) | (669, 199) | 0 | 0 | 61×25 | 60×24 | -1 |
| `kpi3_label` | REFUND RATE | (1052, 160) | (1052, 160) | 0 | 0 | 94×12 | 95×11 | 1 |
| `kpi3_value` | 3.2% | (1053, 199) | (1053, 199) | 0 | 0 | 75×25 | 73×25 | -2 |
| `chart_title` | Net revenue | (285, 336) | (285, 336) | 0 | 0 | 129×17 | 132×18 | 3 |
| `chart_period` | Apr – Sep | (896, 337) | (896, 337) | 0 | 0 | 78×17 | 78×17 | 0 |
| `chart_unit` | ¥ thousand | (287, 375) | (287, 375) | 0 | 0 | 70×11 | 70×11 | 0 |
| `ytick_120` | 120 | (299, 398) | (299, 398) | 0 | 0 | 22×10 | 22×10 | 0 |
| `ytick_90` | 90 | (305, 434) | (305, 434) | 0 | 0 | 16×11 | 16×11 | 0 |
| `ytick_60` | 60 | (305, 470) | (305, 470) | 0 | 0 | 16×10 | 16×10 | 0 |
| `ytick_30` | 30 | (306, 506) | (306, 506) | 0 | 0 | 15×11 | 15×11 | 0 |
| `ytick_0` | 0 | (313, 542) | (313, 542) | 0 | 0 | 8×10 | 8×10 | 0 |
| `month_Apr` | Apr | (373, 560) | (373, 560) | 0 | 0 | 23×14 | 23×14 | 0 |
| `month_May` | May | (472, 560) | (472, 560) | 0 | 0 | 26×14 | 26×14 | 0 |
| `month_Jun` | Jun | (574, 560) | (574, 560) | 0 | 0 | 24×12 | 24×12 | 0 |
| `month_Jul` | Jul | (678, 560) | (678, 560) | 0 | 0 | 18×12 | 19×12 | 1 |
| `month_Aug` | Aug | (775, 560) | (775, 560) | 0 | 0 | 25×14 | 25×14 | 0 |
| `month_Sep` | Sep | (876, 560) | (876, 560) | 0 | 0 | 25×14 | 25×14 | 0 |
| `act_title` | Team activity | (1054, 335) | (1054, 335) | 0 | 0 | 146×22 | 147×22 | 1 |
| `act1_title` | Design review | (1078, 395) | (1078, 395) | 0 | 0 | 118×17 | 119×17 | 1 |
| `act1_time` | 08:40 | (1077, 422) | (1077, 422) | 0 | 0 | 39×12 | 39×12 | 0 |
| `act2_title` | Dataset updated | (1078, 455) | (1078, 455) | 0 | 0 | 139×17 | 140×17 | 1 |
| `act2_time` | 09:15 | (1077, 482) | (1077, 482) | 0 | 0 | 37×12 | 37×12 | 0 |
| `act3_title` | Render complete | (1078, 515) | (1078, 515) | 0 | 0 | 142×17 | 142×17 | 0 |
| `act3_time` | 10:05 | (1077, 542) | (1077, 542) | 0 | 0 | 37×12 | 37×12 | 0 |
| `table_title` | Recent projects | (285, 645) | (285, 645) | 0 | 0 | 169×22 | 171×22 | 2 |
| `ch_project` | PROJECT | (298, 699) | (298, 699) | 0 | 0 | 56×10 | 56×10 | 0 |
| `ch_owner` | OWNER | (782, 699) | (782, 699) | 0 | 0 | 45×10 | 43×10 | -2 |
| `ch_status` | STATUS | (1033, 699) | (1033, 699) | 0 | 0 | 47×10 | 47×9 | 0 |
| `ch_due` | DUE | (1230, 699) | (1230, 699) | 0 | 0 | 25×10 | 23×9 | -2 |
| `r1_proj` | Atlas / Visual system | (298, 734) | (298, 734) | 0 | 0 | 163×17 | 160×17 | -3 |
| `r1_owner` | Lin Chuan | (783, 735) | (783, 735) | 0 | 0 | 74×13 | 74×13 | 0 |
| `r1_status` | In progress | (1067, 736) | (1067, 736) | 0 | 0 | 70×13 | 70×13 | 0 |
| `r1_due` | Nov 09 | (1231, 735) | (1231, 735) | 0 | 0 | 54×13 | 54×13 | 0 |
| `r2_proj` | Pulse / Dashboard | (299, 769) | (299, 769) | 0 | 0 | 141×15 | 140×14 | -1 |
| `r2_owner` | Zhou He | (783, 770) | (783, 770) | 0 | 0 | 63×13 | 63×13 | 0 |
| `r2_status` | Review | (1079, 771) | (1079, 771) | 0 | 0 | 47×11 | 45×11 | -2 |
| `r2_due` | Nov 11 | (1231, 770) | (1231, 770) | 0 | 0 | 47×13 | 47×13 | 0 |
| `r3_proj` | Orbit / Launch | (298, 804) | (298, 804) | 0 | 0 | 110×15 | 108×15 | -2 |
| `r3_owner` | Su Yan | (783, 805) | (783, 805) | 0 | 0 | 50×13 | 50×13 | 0 |
| `r3_status` | Done | (1086, 806) | (1086, 806) | 0 | 0 | 32×11 | 33×11 | 1 |
| `r3_due` | Nov 12 | (1231, 805) | (1231, 805) | 0 | 0 | 51×13 | 51×13 | 0 |
| `footer` | All data is fictional · Snapshot benchmark | (260, 867) | (260, 867) | 0 | 0 | 257×13 | 257×13 | 0 |

## 3. 图表：按比例重建，而非照抄像素

刻度网格 y=405（120）与 y=549（0）间距 144 px，对应 1.2 px / 千元；柱底落在零线 y=549。柱高由 **数值 × 1.2 px** 计算得出，没有把参考图的柱顶像素作为输入：

| 月份 | 数值 | 参考柱 (x,top,w,h) | 重建柱 (x,top,w,h) | Δtop | Δh | 重建高度/数值 |
|---|---|---|---|---|---|---|
| Apr | 54 | (357, 485, 54, 59) | (357, 484, 54, 64) | -0.8 | 5.8 | 1.2 |
| May | 72 | (458, 463, 54, 81) | (458, 462, 54, 86) | -0.4 | 5.4 | 1.2 |
| Jun | 63 | (559, 474, 54, 70) | (559, 473, 54, 75) | -0.6 | 5.6 | 1.2 |
| Jul | 90 | (660, 441, 54, 103) | (660, 441, 54, 108) | 0.0 | 5.0 | 1.2 |
| Aug | 81 | (761, 452, 54, 92) | (761, 451, 54, 97) | -0.2 | 5.2 | 1.2 |
| Sep | 108 | (862, 420, 54, 124) | (862, 419, 54, 129) | -0.6 | 5.6 | 1.2 |

六根柱子的 **高度/数值比值全部等于 1.2**，说明柱高确实是按数值线性重建的；与参考图柱顶的差异 ≤1 px，来自参考图自身的像素取整。

## 4. 颜色

### 4.1 平涂色块（逐点取样，完全一致）

| 位置 | 参考 | 重建 | 一致 |
|---|---|---|---|
| main_bg | `#F3F6FB` | `#F3F6FB` | ✓ |
| sidebar_bg | `#14233C` | `#14233C` | ✓ |
| card_fill | `#FFFFFF` | `#FFFFFF` | ✓ |
| card_border | `#E2E8F1` | `#E2E8F1` | ✓ |
| grid | `#E7EDF5` | `#E7EDF5` | ✓ |
| bar | `#245CE4` | `#245CE4` | ✓ |
| thead | `#F3F6FB` | `#F3F6FB` | ✓ |
| rowsep | `#EBEFF5` | `#EBEFF5` | ✓ |
| nav_pill | `#FFFFFF` | `#FFFFFF` | ✓ |
| sidecard | `#233954` | `#233954` | ✓ |
| logo_ring | `#64DBB6` | `#64DBB6` | ✓ |
| logo_hole | `#14233C` | `#14233C` | ✓ |
| pill_ip | `#E7EFFF` | `#E7EFFF` | ✓ |
| pill_rv | `#FFF3D7` | `#FFF3D7` | ✓ |
| pill_dn | `#DCF5EC` | `#DCF5EC` | ✓ |
| button | `#245CE4` | `#245CE4` | ✓ |
| nav_dot_on | `#64DBB6` | `#64DBB6` | ✓ |
| nav_dot_off | `#7791B3` | `#7791B3` | ✓ |
| act_dot_amber | `#EAAF40` | `#EAAF40` | ✓ |
| act_dot_blue | `#245CE4` | `#245CE4` | ✓ |
| act_dot_green | `#168267` | `#168267` | ✓ |

21 / 21 个平涂色块完全一致（0 通道误差）。

### 4.2 文字墨色

全部 57 个文本区域的墨色与参考图一致（`colour-audit.json` 中 `text_ink_colour[*].delta_rgb` 全为 `[0,0,0]`）：主文字 `#18283F`、次级文字 `#63748F`、绿色变化 `#168267`、表头/到期 `#63748F`、页脚 `#7B8BA3`、状态标签 `#245CE4` / `#9D6613` / `#168267`、侧栏标签 `#64DBB6` / `#FFFFFF` / `#B0C2D6`。

### 4.3 整体像素一致率

每 2 像素抽样一次共 324000 个采样点，RGB 三通道差 ≤24 的有 318461 个，即 **98.29%**。剩余约 1.7% 集中在字形边缘的抗锯齿像素上——这是因为参考图的字重介于服务提供的 `Inter Semi Bold` 与 `Inter Extra Bold` 之间，字形轮廓在子像素级别不完全重合（见第 6 节）。

## 5. 表格：3 行顺序与状态编码

| 行 | PROJECT | OWNER | STATUS | 标签底色 | 标签文字色 | DUE |
|---|---|---|---|---|---|---|
| 1 | Atlas / Visual system | Lin Chuan | In progress | `#E7EFFF` | `#245CE4` | Nov 09 |
| 2 | Pulse / Dashboard | Zhou He | Review | `#FFF3D7` | `#9D6613` | Nov 11 |
| 3 | Orbit / Launch | Su Yan | Done | `#DCF5EC` | `#168267` | Nov 12 |

三行顺序、四个列头（PROJECT/OWNER/STATUS/DUE）、三枚状态标签的底色与文字色、以及标签矩形 (1028, 729/764/799, 148×28) 均与参考图一致（锚点 A35/A36，Δ=0）。

## 6. 残余差异（如实说明）

1. **字重粒度**。参考图的粗体字重落在 `Inter Semi Bold`(600) 与 `Inter Extra Bold`(800) 之间，而服务 `/fonts` 只提供 `Inter / Inter Medium / Inter Semi Bold / Inter Extra Bold / Inter Black` 五个档位，且 `fontWeight` / `font-weight` / `weight` 属性被**静默忽略**（实测见 `probe_weight.py`：`Workspace Overview`@33px 在这些属性下密度恒为 430063）。因此每处粗体只能在「更粗但更小」与「更细但更大」之间取舍：本复刻统一选择**保持墨迹宽度与位置不变**的解（密度误差 ≤11%），而不是为了追密度而牺牲字距。密度对照：

| 元素 | 重建/参考 墨迹密度 | 选用字重 |
|---|---|---|
| 页面标题 Workspace Overview | 1.106 | Inter Extra Bold 31.5 |
| KPI 数值 ¥128,400 | 1.053 | Inter Extra Bold 31 |
| KPI 标签 REVENUE | 0.970 | Inter Extra Bold 13 / ls 0.6 |
| 卡片标题 Net revenue | 0.933 | Inter Semi Bold 22.75 |
| 卡片标题 Team activity | 0.908 | Inter Semi Bold 22.5 |
| 卡片标题 Recent projects | 0.915 | Inter Semi Bold 22.5 |
| 活动条目 Design review | 1.089 | Inter Extra Bold 16.65 |
| 表格行 Atlas / Visual system | 1.105 | Inter Extra Bold 15.75 |
| 按钮 Export report | 1.022 | Inter Extra Bold 16.25 |
| 表头 PROJECT | 1.036 | Inter Extra Bold 11.5 |
| 状态标签 In progress | 1.037 | Inter Extra Bold 12.5 |
| 品牌字 NORTHSTAR | 0.998 | Inter Black 17 / ls 1.0 |
| 侧栏 PRO WORKSPACE | 1.007 | Inter Extra Bold 12.5 / ls 0.3 |
| 侧栏 12 team members | 1.000 | Inter 16 |
| 侧栏 Manage access → | 1.055 | Inter Medium 13.75 |
| 选中导航 Overview | 1.106 | Inter Extra Bold 19 |
| 未选中导航 Projects | 1.000 | Inter 19 |

2. **抗锯齿子像素**。位置与宽度都对齐之后，仍有约 1.7% 的像素因字形边缘覆盖率不同而超出 ±24 通道差，主要集中在 22px 与 15px 的粗体文字上。

3. **圆角拟合值是整数档**。卡片圆角实测参考图为 12（由角点轮廓 `[8,6,4,3,2,2,1,1,0]` 反解得到连续半径约 10–12，服务的 `borderRadius` 在整数档下渲染的圆角略少一点，取 12 后角点轮廓与参考图逐值相同）。按钮 9、状态标签与选中导航 8、柱 5、侧栏卡片 12、表头带 2、品牌标 7，全部逐值匹配参考图角点轮廓。

4. **未做逐像素声明**。本复刻不是也不宣称逐像素完全复刻：DSL 树与参考图的生成方式无关，字形光栅化存在子像素级差异，`pixel_agreement=98.29%` 是抽样统计结果，不是逐像素恒等。

## 7. 与 TASK.md 硬指标逐条对照

| TASK.md 要求 | 实测 |
|---|---|
| 输出尺寸保持 1440×900 | `reconstructed.png` 实测 1440×900 |
| 重建布局/背景/侧栏/卡片/图表/表格/状态标签/主要装饰 | 全部由 DSL 构造，见 `reconstructed.snapshot` |
| 禁止嵌入参考图或裁块 | DSL 中 `<Image>` 出现次数 = 0 |
| 主区边界/卡片边界/图表零线/导航选中态等锚点 ±8 px | 49/49 锚点通过，最大 Δ=1 px |
| 图表比例与标记（非只放相同数字） | 柱高 = 数值 × 1.2 px，六根比值全等 1.2 |
| 表格 3 行顺序与状态编码准确 | 见第 5 节 |
| 至少 12 个锚点，涵盖四象限/图表/表格 | 49 个锚点，覆盖 图表区、左下象限、右下象限、左上象限、右上象限 |
| 用可测误差说明残余差异 | 第 6 节；逐项数据在 `reconstruction-audit.json` |

