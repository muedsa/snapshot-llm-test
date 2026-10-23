"""A15 生成器：参考图重建（1440×900 仪表盘）。

坐标、字号、颜色的来源
----------------------
题目没给设计源文件、也没给标准坐标，所以「参考估计值」不是读出来的，是**量出来**的：
对公开参考图 tasks/A15-reference-reconstruction/inputs/reference.png 做像素扫描，
a15_diag.py … a15_diag8.py（都保留在 tmp/<rid>/_suite/gen/）给出卡片边框、字形墨迹
框、网格线、柱体、胶囊、分隔线、圆角弧的位置与颜色。本文件顶部的常量表就是那份测量
的结论，每个常量注明它对应的扫描口径。a15_audit.py 用**同一套**扫描例程同时量参考图
与重建图，逐锚点算误差——两张图过同一把尺，误差才可比。

字号怎么定（两条独立口径互相校验）
----------------------------------
参考图是位图，字号只能由字形墨迹反推：

  * 字高 → 字号：按 Inter 的 cap height 0.727 em、ascender 0.734 em、
    descender −0.221 em 取该字符串实际跨越的字面高度；
  * 宽度 → 字号：用 ADV 步进表算步进宽度，减去首尾侧边距（≈0.04 em），再比墨宽。

墨迹框的阈值很关键。诊断 V 用固定 tol=40（≈1% 覆盖率）会把抗锯齿晕影也算成墨迹，
字高系统性偏大 3–6 px；诊断 VI 改用「ROI 内最大色差 × 0.5」（≈50% 覆盖率）得到真实
墨迹框，两口径随即一致。逐元素核对的结论：

  * NORTHSTAR（18.9/19.3）、PROJECT（12.3/12.4）、DUE（11.9/12.4）、Done（13.0/12.4）、
    Review（13.5/13.8）、Apr（13.0/13.7）、Sep（13.7/13.7）、副标题（17.8/17.5）、
    Net revenue（22.4/22.0）、Team activity（22.6/22.2）、Recent projects（22.2/22.2）、
    REVENUE（13.8/13.8）、ORDERS（13.8/13.8）、+12.4%（16.1/16.5）——两口径差 < 5%，
    说明服务用的就是 Inter 的宽度度量；
  * 主标题（35.9/41.3）、¥128,400（33.0/39.9）、表格行项目名（16.2/20.6）——字高口径
    系统性偏大 10–25%。凡含大写与升部混排的元素都有这个偏差，说明参考图字体的升部比
    Inter 相对更长。这类元素取**宽度口径**（宽度错了才会撞边或错位，字高差 10% 在
    1440 px 画布上只有 3–4 px）；不含升部的元素（全大写、纯小写）两口径本就一致。
  * 数字步进宽度实测为 0.60 em 而非 0.556 em：¥128,400 与 426 在 0.60 下两口径同落
    在 33 px，在 0.556 下相差 15%。ADV 表已按此修正。

因此字号按宽度口径定稿，字高残余偏差在 comparison.md 里如实记为字体度量差异，不伪装
成已吻合。

文字定位
--------
`text_at(left, ink_top, ...)` 按**目标墨迹左上角**定位：盒顶 = ink_top − EM_INK_TOP×字号。
所有 ink_top 都取自诊断 VI 的严格墨迹框（不是宽松口径），所以参考图与重建图量的是同
一个量。EM_INK_TOP = 0.32 先沿用 A14 在 Noto Sans CJK SC 上的实测值，随后用探针页
（13/22/36 px 三档，红线标出目标墨迹顶）实测确认 Inter BOLD 下也成立，误差 ±0.5 px。
渲染后仍由 a15_audit.py 的 glyph_boxes[*].ink_top_over_em 复核。文字盒在墨宽之外再留
PAD_X——实测盒窄于墨宽时服务会自动折行，而单行盒高会把第二行整行裁掉（A14 踩过的坑）。

文字色
------
不用「区域内最深/最饱和像素」，那会命中抗锯齿边缘、把文字色和底色混在一起
（例如把真色 #168267 量成 #0E7F67）。诊断 VIII 取 ROI 内 |像素−底色| 通道和最大处
——满覆盖率的文字体素差值最大，混色像素差值最小。量出来的是一套很干净的 token：
正文 #18283F、次级 #63748F、页脚 #7B8BA3，侧栏 #BECADD / #B8CADD，变化绿 #168267。
注意三个 KPI 变化（含 −0.8 pp）在参考图里**都是同一个绿**，表格标题也是 #18283F 而非
浅色——这两处最初的猜测是错的，已按实测改。

文本属性收原始字符，不做 XML 转义：A14 实测服务不解码实体，`&lt;` 会原样显示成字面
串（见 a14_pages.py 的 esc() 说明）。
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A15"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
CONTENT = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "content.json"
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"

W, H = 1440, 900          # 题目规定的画布

# ---------------------------------------------------------------- 颜色
# 文字色由诊断 VIII 的「核心像素」法量出（取与底色相差最大处，避开抗锯齿混色）；
# 填充色由诊断 VII/VIII 的中心像素量出。
BG = "#F3F6FB"            # 页背景 (243,246,251) @720,120
SIDEBAR = "#14233C"       # 侧栏 (20,35,60) @28,460
CARD = "#FFFFFF"          # 卡片 (255,255,255) @1360,200
BRD = "#E2E8F1"           # 卡片 1 px 边框 (226,232,241)
BLUE = "#245CE4"          # 主蓝：按钮填充 / 柱体 / 活动圆点2 (36,92,228)
GRID = "#E7EDF5"          # 网格线 @400,549
DIV = "#EBEFF5"           # 表格行分隔线 @900,760
NAVSEL = "#294467"        # 导航选中底 (41,68,103) @150,139
WSCARD = "#233954"        # 侧栏工作区卡 (35,57,84) @120,800

INK = "#18283F"           # 主墨色：标题 / KPI 数值 / 区块标题 / 活动条目 / 表格标题 / 行项目名
MUTED = "#63748F"         # 次级：副标题 / KPI 标签 / 单位 / 刻度 / 月标签 / 活动时间 / 表头 / 行负责人 / 行到期
TXT_LIGHT = "#7B8BA3"     # 页脚
GREEN_TX = "#168267"      # KPI 变化——三项同色（−0.8 pp 也是绿）/ 胶囊 Done 字 / 活动圆点3
MINT = "#64DBB6"          # logo 描边 / 选中圆点 / PRO WORKSPACE
NAV_TX_ON = "#FFFFFF"
NAV_TX_OFF = "#BECADD"    # 导航未选文字
WS_SUB = "#B8CADD"        # 工作区卡第三行
WHITE = "#FFFFFF"

# 胶囊：浅彩底 + 深彩字（诊断 VIII 实测：底色取填充中心像素，字色取核心像素）
PILL_BG_B, PILL_TX_B = "#E7EFFF", "#245CE4"   # In progress（蓝）
PILL_BG_A, PILL_TX_A = "#FFF3D7", "#9D6613"   # Review（琥珀）
PILL_BG_G, PILL_TX_G = "#DCF5EC", "#168267"   # Done（绿）
DOT_INACTIVE = "#7791B3"  # 未选中导航圆点 (119,145,179) @39,200
# 活动圆点（诊断 VII 逐行取中心色）
ACT_DOT_COLORS = ("#EAAF40", "#245CE4", "#168267")   # 琥珀 / 蓝 / 绿

# ---------------------------------------------------------------- 版式（28 px 栅格）
SIDEBAR_W = 220                       # 侧栏右边界 x=220（y=400..800 多处复核）
CONTENT_L, CONTENT_R = 260, 1399      # 内容栏左右缘
GRID_GAP = 28                         # 行间 / 列间统一间距

KPI_Y, KPI_H, KPI_W = 138, 144, 356   # KPI1 [260,138,615,281]
KPI_XS = (260, 644, 1028)             # 卡间 28；右侧余 16 px 是原稿的固有偏差
CARD2_Y, CARD2_H = 310, 286
CHART_X, CHART_W = 260, 742           # 图表卡 [260,310,1001,595]
ACT_X, ACT_W = 1030, 370              # 活动卡 [1030,310,1399,595]
TBL_Y, TBL_H = 624, 218               # 表格卡 [260,624,1399,841]
TBL_W = CONTENT_R - CONTENT_L + 1     # 1140：外轮廓含端点
CARD_R = 14                           # 卡片圆角

PAD_IN = 25                           # 卡片内容左内边距（260+25=285 = KPI 文字墨迹左缘）
# 各元素墨迹左缘实测（诊断 VI 严格阈值），不再统一套 PAD_IN：
T_X = 261.0                           # 主标题 / 副标题
CH_TITLE_X, UNIT_X = 286.0, 288.0     # 图表标题 / 单位（¥ 的左侧边距较大）
ACT_TITX = 1055.0                     # 活动卡区块标题
TBL_TITLE_X = 286.0                   # 表格标题

# 导出按钮：外框 [1184,43,1399,90]
BTN = (1184, 43, 216, 48)
# 导航选中底：[18,116,201,163]，左上角弧拟合 radius≈7
NAV_BOX = (18, 116, 184, 48)
NAV_BOX_R = 7.0
NAV_DOT_X = 39.5                      # 圆点中心 x（bbox 34..45）
NAV_DOT_D = 12.0                      # 圆点直径
# 圆点中心 y ≠ 底框中心（底框中心 140/204/268/332）：实测圆点 bbox
# (34,128,45,139)(34,192,45,203)(34,256,45,267)(34,320,45,331)，中心 133.5/197.5/261.5/325.5，
# 比底框中心高 6 px——参考图里圆点对齐的是文字墨迹，不是底框中线。
NAV_DOT_CY = (133.5, 197.5, 261.5, 325.5)
NAV_TXT_X = 62.5                      # 导航文字墨迹左缘（严格阈值实测 62..63）
NAV_INK_TY = (126, 191, 255, 319)     # 四项文字墨迹顶（严格阈值实测）
# 侧栏 logo：28×28 圆环，外缘 [30,33]-[57,60]，内孔 x 38..49 / y 41..52（12×12）。
# 诊断 X 把 x 26..62 / y 29..64 逐像素打成 ASCII 位图后确认是同心圆环：
# 外半径 14、内半径 6，描边厚 8 px（沿 y=46 中心线，左缘 30..37、右缘 50..57）。
# 首版误画成 44×28 的圆角矩形环，是因为只量了 mint 的整块 bbox 却把宽度当成 44。
LOGO = (30, 33, 28, 28)
LOGO_R = 14.0
LOGO_STROKE = 8.0
# 侧栏工作区卡：填充 [22,752,197,867]，左上角弧拟合 radius≈8
WS_BOX = (22, 752, 176, 116)
WS_BOX_R = 8.0
WS_TXT_X = 38.5                       # 三行文字墨迹左缘
WS_TAG_INK, WS_MAIN_INK, WS_SUB_INK = 770.0, 804.0, 836.0

# 图表绘图区：网格线 y=405(120) / 441(90) / 477(60) / 513(30) / 549(0)，x 333..969
GRID_X0, GRID_X1 = 333, 969
GRID_YS = (405, 441, 477, 513, 549)
Y_TICK_XR = 319.0                     # y 刻度墨迹右缘（"120" 与 "0" 同为 319）
ZERO_Y = 549
BAR_W = 54
BAR_CENTERS = (383.5, 484.5, 585.5, 686.5, 787.5, 888.5)   # 步进 101
BAR_TOP_R = 6                          # 柱顶圆角
MONTHS_Y = 561.0                       # 月标签墨迹顶（"Apr" 与 "Sep" 同为 561）

# 表格：表头带 [284,688,1373,721]，行分隔线同宽
# 宽度 1090 是实测来的：带与两条分隔线在参考图里都是从 x=284 到 x=1373，
# 比卡片内容区右缘（1398）短 25 px。首版按「贯到卡片右缘」画成 1116 宽，
# 审计窗口一旦收紧到卡片内部就把这个 25 px 露出来了。
TBAND = (284, 688, 1090, 34)
TBAND_R = 8
TBL_DIV_YS = (760, 795)                # 行分隔线
TBL_COL_X = (298.5, 782.5, 1034.0, 1231.0)   # 四列文字墨迹左缘
TBL_ROW_INK = (735.0, 770.0, 805.0)    # 三行文字墨迹顶
TBL_HDR_INK = 699.0                    # 表头文字墨迹顶
PILL_X, PILL_W, PILL_H = 1028, 148, 28
PILL_TY = (729, 764, 799)              # 三行胶囊顶（中心 742.5/777.5/812.5）

# 活动卡：条目标题墨迹顶与圆点中心（诊断 VII 逐行）
ACT_TXT_X = 1078.0
ACT_TY = (395.0, 456.0, 516.0)         # 条目标题墨迹顶
ACT_TIME_INK = (423.0, 483.5, 543.0)   # 三条时间墨迹顶（实测 423/543，中间按行距插值）
ACT_DOT_X = 1058.5                     # 圆点中心 x（bbox 1054..1063）
ACT_DOT_D = 10.0                       # 圆点直径
ACT_DOT_CY = (401.5, 461.5, 521.5)     # 圆点中心 y（步进 60）

# 页脚
FOOT_TXT = (260.0, 867.0)

# ---------------------------------------------------------------- 字号
# 严格墨迹框（诊断 VI）→ 宽度口径反推，括号为字高口径；两口径一致处即定稿。
SZ = {
    # 字号定稿方法：先用 ADV 步进表估一个初值，再用「本服务实际渲染墨宽 → 参考墨宽」
    # 反比缩放校准（size_new = size_prev × 参考墨宽 / 本服务渲染墨宽）。只用估测会把
    # 整段文字带偏 5–10 %，只有渲染出来的宽度才是同一把尺。括号是「上一版渲染墨宽 /
    # 参考墨宽」。三处以上互相印证的（如 sec 三处全 1.000、nav 三处全 1.000）就直接
    # 采信，不再动。
    "title": 36.0,        # 333/333
    "subtitle": 18.0,     # 17.5→241/246 → 17.8；17.8 渲染 243/246 → 18.0（第三轮）
    "btn": 15.0,
    "kpi_label": 14.0,    # 13.5→61/64 → 14.0（三卡取中：REFUND RATE 13.3、ORDERS 13.8）
    "kpi_value": 32.0,    # 33.0→152/147、61/59、76/73 → 32.0
    "kpi_delta": 16.0,    # 56/56、59/59
    "sec": 22.0,          # 128/128、144/144、167/167（三处全 1.000）
    "period": 17.0,       # 15.5→68/76 → 17.0（墨高 15 也印证，ascender+descender 口径）
    "unit": 13.2,         # 12.8→66/68 → 13.2
    "tick": 13.0,         # 21/20、6/6
    "month": 13.5,        # 21/22、23/24（差 1 px，不再动）
    "act_item": 17.0,     # 117/117、141/141
    "act_time": 14.0,     # 38/38、36/36
    "tbl_hdr": 12.5,      # 57/55、24/24
    "row_name": 16.2,     # 16.5→165/161、111/109 → 16.2
    "row_sub": 16.0,      # 73/73、54/54
    "pill": 13.0,         # 69/69、46/46、32/32（三处全 1.000）
    "footer": 13.4,       # 14.0→269/257 → 13.4
    "brand": 19.0,        # 116/116
    "nav": 19.0,          # 87/87、71/72、73/73
    "ws_tag": 13.0,       # 14.0→121/112 → 13.0
    "ws_main": 16.0,      # 15.0→125/134 → 16.0
    "ws_sub": 14.0,       # 14.5→125/122 → 14.0
}
LS = {"brand": 0.0, "ws_tag": 0.0}   # 追踪全大写：实测宽度已吻合 14 px / 19 px，不再补字距

# ---------------------------------------------------------------- 字体与度量
F = "Inter"
EXTRA = "Inter Extra Bold"             # 探针比对后决定是否用于标题 / KPI 数值

ADV = {}
for _c, _w in [("A", .722), ("B", .667), ("C", .667), ("D", .722), ("E", .611),
               ("F", .611), ("G", .722), ("H", .722), ("I", .278), ("J", .5),
               ("K", .667), ("L", .556), ("M", .833), ("N", .722), ("O", .722),
               ("P", .667), ("Q", .722), ("R", .722), ("S", .611), ("T", .611),
               ("U", .722), ("V", .667), ("W", .944), ("X", .667), ("Y", .611),
               ("Z", .611), ("a", .556), ("b", .611), ("c", .5), ("d", .611),
               ("e", .556), ("f", .333), ("g", .611), ("h", .611), ("i", .278),
               ("j", .333), ("k", .556), ("l", .278), ("m", .944), ("n", .611),
               ("o", .611), ("p", .611), ("q", .611), ("r", .389), ("s", .5),
               ("t", .389), ("u", .611), ("v", .556), ("w", .778), ("x", .556),
               ("y", .556), ("z", .5)]:
    ADV[_c] = _w
for _c in "0123456789":
    ADV[_c] = .60     # 数字步进 0.60 em（实测：¥128,400 与 426 两口径同落 33 px）
ADV.update({" ": .25, ",": .278, ".": .278, ":": .278, "/": .333, "-": .333,
            "+": .556, "%": .889, "¥": .611, "–": .556, "·": .333, "→": .611,
            "−": .556, "’": .333, "'": .222, "!": .333, "?": .556,
            ";": .333, "&": .833})

# 盒顶 → 墨迹顶（em）。沿用 A14 在 Noto Sans CJK SC 上的 0.32，随后用探针页
# 实测确认（build_probe 的三个 13/22/36 px 标定块，红线即目标墨迹顶）：Inter
# BOLD 下红线正好压在大写字母顶，三个字号都在 ±0.5 px 内，说明 0.32 对 Inter 也成立
# ——这是实测结论而非沿用假设。渲染后仍由 a15_audit.py 的 glyph_boxes[*].ink_top_over_em
# 复核（参考图给真值，重建图给服务实际行为）。
EM_INK_TOP = 0.32
PAD_X = 40.0         # 文字盒在墨宽之外多留的横向余量（防自动折行裁切）
BOLD_INFL = 1.02     # 粗体步进略宽


def esc(s: str) -> str:
    """原样返回，不做 XML 转义——A14 实测服务不解码实体。

    服务不解码实体，所以 `&`/`<`/`>` 不能转义成实体（会原样显示），`"` 也不能转成
    `&#34;`（同样原样显示）。这些字符在属性里只能靠**不用**来规避：探针页第一版把
    标签写成 `fontFamily="Inter"` 就报 PARSE_ERROR（AFTER_ATTR_VALUE_QUOTED）。
    因此这里对危险字符直接抛错，而不是静默产出一份能保存、渲染时报错的 DSL。
    """
    bad = ("\"", "<", ">", "&")
    hit = [c for c in bad if c in s]
    if hit:
        raise ValueError("文案含无法转义的 XML 危险字符 %s：%r" % (hit, s))
    return s


def lh(size: float) -> float:
    return size * 1.45


def est_w(s: str, size: float, ls: float = 0.0, bold: bool = False) -> float:
    """步进宽度估算（em → px）。盒宽用它 + PAD_X，宁大勿小。"""
    k = BOLD_INFL if bold else 1.0
    return sum(size * ADV.get(c, .6) * k + ls for c in s)


def text(x, y, w, h, s, size, *, color=INK, style="", ls=0.0, family=F,
         align="CENTER_LEFT"):
    st = ' fontStyle="%s"' % style if style else ""
    lsa = ' letterSpacing="%g"' % ls if ls else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Container width="%g" height="%g" alignment="%s">'
            '<Text fontFamily="%s" fontSize="%g" color="%s"%s%s '
            'text="%s" /></Container></Positioned>'
            % (x, y, w, h, w, h, align, family, size, color, st, lsa, esc(s)))


def text_at(left, ink_top, s, size, *, color=INK, style="", ls=0.0, family=F,
            dy=0.0):
    """墨迹左上角对齐 (left, ink_top) 的单行文字。

    dy 是该元素的实测修正（首版渲染后从 a15_audit.py 的 ink_offset 里回填）。
    """
    w = est_w(s, size, ls, bold=bool(style))
    return text(left, ink_top - EM_INK_TOP * size + dy, w + 2 * PAD_X, lh(size), s,
                size, color=color, style=style, ls=ls, family=family)


def text_cx(cx, ink_top, s, size, *, color=INK, style="", ls=0.0, family=F,
            dy=0.0):
    """水平居中于 cx、墨迹顶对齐 ink_top。盒心即 cx，估算误差不会传到锚点。"""
    w = est_w(s, size, ls, bold=bool(style))
    return text(cx - w / 2 - PAD_X, ink_top - EM_INK_TOP * size + dy,
                w + 2 * PAD_X, lh(size), s, size, color=color, style=style, ls=ls,
                family=family, align="CENTER")


def text_r(x_right, ink_top, s, size, *, color=INK, style="", ls=0.0, family=F,
           dy=0.0):
    """墨迹右缘对齐 x_right。

    盒心必须落在 `x_right − 墨宽/2`，文字在盒内水平居中，墨右缘才等于 x_right
    （估算误差只让盒左右等量偏移，误差被减半传导）。盒宽取 `墨宽 + PAD_X`——
    注意不能像 text_cx 那样两侧都留 PAD_X，否则盒心会漂到 x_right 上、整行右移
    半个墨宽（首版 chart_period 因此右移 38 px，audit 的 offset_vs_expected 抓到）。
    """
    w = est_w(s, size, ls, bold=bool(style))
    return text(x_right - w - PAD_X / 2, ink_top - EM_INK_TOP * size + dy,
                w + PAD_X, lh(size), s, size, color=color, style=style, ls=ls,
                family=family, align="CENTER")


def rect(x, y, w, h, *, color=None, border=None, radius=0.0, r_tl=None,
         r_tr=None, r_br=None, r_bl=None):
    """带填充/描边/圆角的盒。

    `border` 走 CSS border-box：描边在盒**内侧**画，外轮廓始终是 (x,y,w,h)。
    logo 圆环就是靠这个画出来的——28×28 盒、radius 14、8 px 描边 → 外圆 r=14、
    内圆 r=6，与参考图实测（外缘 30..57、内孔 x 38..49）一致。若描边居中画，
    外缘会变成 r=18、内孔 r=10，明显不符。
    """
    a = ""
    if radius:
        a += ' borderRadius="%g"' % radius
    for nm, v in (("borderRadiusTopLeft", r_tl), ("borderRadiusTopRight", r_tr),
                  ("borderRadiusBottomRight", r_br), ("borderRadiusBottomLeft", r_bl)):
        if v:
            a += ' %s="%g"' % (nm, v)
    if border:
        a += ' border="%s"' % border
    if color:
        a += ' color="%s"' % color
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Container width="%g" height="%g"%s />'
            '</Positioned>' % (x, y, w, h, w, h, a))


def circle(cx, cy, d, *, color=None, border=None):
    """圆心在 (cx, cy)、直径 d 的圆（点 / 圆环）。"""
    a = ' shape="CIRCLE"'
    if border:
        a += ' border="%s"' % border
    if color:
        a += ' color="%s"' % color
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Container width="%g" height="%g"%s />'
            '</Positioned>' % (cx - d / 2, cy - d / 2, d, d, d, d, a))


def snapshot(w, h, parts):
    return ('<Snapshot type="png">\n<Container width="%d" height="%d">\n'
            '<Stack width="%d" height="%d">\n' % (w, h, w, h)
            + "\n".join(parts) + "\n</Stack>\n</Container>\n</Snapshot>\n")


def card(x, y, w, h, *, radius=CARD_R, fill=CARD, border=BRD):
    return rect(x, y, w, h, color=fill, border="1 SOLID " + border, radius=radius)


# ---------------------------------------------------------------- 文案
def load_content() -> dict:
    return json.loads(CONTENT.read_text(encoding="utf-8"))


def build() -> tuple[str, dict]:
    """完整 DSL 与排版元数据。Stack 里后写的覆盖先写的，所以顺序就是绘制顺序。"""
    c = load_content()
    p: list[str] = []
    meta: dict = {}

    # ---- 铺底与侧栏
    p.append(rect(0, 0, W, H, color=BG))
    p.append(rect(0, 0, SIDEBAR_W, H, color=SIDEBAR))

    lx, ly, ld, ldh = LOGO
    p.append(rect(lx, ly, ld, ldh, color=SIDEBAR,
                  border="%g SOLID " % LOGO_STROKE + MINT, radius=LOGO_R))
    p.append(text_at(73.0, 38.0, c["brand"], SZ["brand"], style="BOLD",
                     color=NAV_TX_ON, ls=LS["brand"]))

    p.append(rect(NAV_BOX[0], NAV_BOX[1], NAV_BOX[2], NAV_BOX[3], color=NAVSEL,
                  radius=NAV_BOX_R))
    for i, label in enumerate(c["navigation"]):
        on = i == 0
        p.append(circle(NAV_DOT_X, NAV_DOT_CY[i], NAV_DOT_D,
                        color=(MINT if on else DOT_INACTIVE)))
        p.append(text_at(NAV_TXT_X, NAV_INK_TY[i], label, SZ["nav"],
                         style=("BOLD" if on else ""),
                         color=(NAV_TX_ON if on else NAV_TX_OFF)))

    wx, wy, ww, wh = WS_BOX
    p.append(rect(wx, wy, ww, wh, color=WSCARD, radius=WS_BOX_R))
    p.append(text_at(WS_TXT_X, WS_TAG_INK, c["workspace_info"][0], SZ["ws_tag"],
                     style="BOLD", color=MINT, ls=LS["ws_tag"]))
    p.append(text_at(WS_TXT_X, WS_MAIN_INK, c["workspace_info"][1], SZ["ws_main"],
                     color=WHITE))
    p.append(text_at(WS_TXT_X, WS_SUB_INK, c["workspace_info"][2], SZ["ws_sub"],
                     color=WS_SUB))

    # ---- 页头
    p.append(rect(BTN[0], BTN[1], BTN[2], BTN[3], color=BLUE, radius=10))
    p.append(text(BTN[0], BTN[1], BTN[2], BTN[3], c["button"], SZ["btn"],
                  color=WHITE, style="BOLD", align="CENTER"))
    p.append(text_at(T_X, 38.0, c["title"], SZ["title"], style="BOLD", color=INK))
    p.append(text_at(T_X, 85.0, c["subtitle"], SZ["subtitle"], color=MUTED))

    # ---- 三张 KPI 卡
    for i, k in enumerate(c["kpis"]):
        x0 = KPI_XS[i]
        p.append(card(x0, KPI_Y, KPI_W, KPI_H))
        p.append(text_at(x0 + PAD_IN, 161.0, k["label"], SZ["kpi_label"],
                         style="BOLD", color=MUTED))
        p.append(text_at(x0 + PAD_IN, 199.0, k["value"], SZ["kpi_value"],
                         style="BOLD", color=INK))
        p.append(text_at(x0 + PAD_IN, 246.0, k["change"], SZ["kpi_delta"],
                         style="BOLD", color=GREEN_TX))

    # ---- 净收入图表卡
    p.append(card(CHART_X, CARD2_Y, CHART_W, CARD2_H))
    p.append(text_at(CHART_X + PAD_IN, 336.0, c["chart_title"], SZ["sec"],
                     style="BOLD", color=INK))
    # "Apr – Sep" 墨迹右缘实测在 975（卡片右缘 1001 减去与左侧一致的 26 px 留白）
    p.append(text_r(975.0, 338.0, c["chart_period"], SZ["period"], color=MUTED))
    p.append(text_at(UNIT_X, 376.0, c["chart_unit"], SZ["unit"], color=MUTED))
    for gy in GRID_YS:
        p.append(rect(GRID_X0, gy, GRID_X1 - GRID_X0 + 1, 1, color=GRID))
    # y 轴刻度必须逆序配对：content.json 里 chart_ticks 升序给出（0,30,…,120），
    # 而 GRID_YS 是自上而下（405…549）。同序 zip 会把 0 画到最顶、120 画到最底，
    # 整条轴变成倒轴——首版就是这样，只有把参考与重建并排看图才发现。
    for tick, gy in zip(reversed(c["chart_ticks"]), GRID_YS):
        p.append(text_r(Y_TICK_XR, gy - 6.5, str(tick), SZ["tick"], color=MUTED))
    for i, (v, cx) in enumerate(zip(c["chart_values"], BAR_CENTERS)):
        h = math.ceil(v * 1.2)          # 每 30 单位 36 px = 1.2 px/单位，向上取整
        top = ZERO_Y - h                # 柱底停在 548，网格线 549 不被覆盖
        # 柱心是 .5 的半点，取整到整列后中心仍是 cx（54 为偶数宽）
        left = int(cx - BAR_W / 2 + 0.5)
        p.append(rect(left, top, BAR_W, h, color=BLUE,
                      r_tl=BAR_TOP_R, r_tr=BAR_TOP_R))
        p.append(text_cx(cx, MONTHS_Y, c["months"][i], SZ["month"], color=MUTED))

    # ---- 团队动态卡
    p.append(card(ACT_X, CARD2_Y, ACT_W, CARD2_H))
    p.append(text_at(ACT_TITX, 335.0, c["activity_title"], SZ["sec"],
                     style="BOLD", color=INK))
    for i, item in enumerate(c["activity"]):
        label, tm = item[0], item[1]
        p.append(circle(ACT_DOT_X, ACT_DOT_CY[i], ACT_DOT_D,
                        color=ACT_DOT_COLORS[i]))
        p.append(text_at(ACT_TXT_X, ACT_TY[i], label, SZ["act_item"],
                         style="BOLD", color=INK))
        p.append(text_at(ACT_TXT_X, ACT_TIME_INK[i], tm, SZ["act_time"],
                         color=MUTED))

    # ---- 最近项目表格卡
    p.append(card(CONTENT_L, TBL_Y, TBL_W, TBL_H))
    p.append(text_at(TBL_TITLE_X, 645.0, c["table_title"], SZ["sec"],
                     style="BOLD", color=INK))
    bx, by, bw, bh = TBAND
    p.append(rect(bx, by, bw, bh, color=BG, radius=TBAND_R))
    for label, x0 in zip(c["table_columns"], TBL_COL_X):
        p.append(text_at(x0, TBL_HDR_INK, label, SZ["tbl_hdr"], style="BOLD",
                         color=MUTED))
    for dy_ in TBL_DIV_YS:
        p.append(rect(bx, dy_, bw, 1, color=DIV))

    pill_styles = ((PILL_BG_B, PILL_TX_B), (PILL_BG_A, PILL_TX_A),
                   (PILL_BG_G, PILL_TX_G))
    for i, row in enumerate(c["rows"]):
        name, owner, status, due = row
        ink_top = TBL_ROW_INK[i]
        p.append(text_at(TBL_COL_X[0], ink_top, name, SZ["row_name"],
                         style="BOLD", color=INK))
        p.append(text_at(TBL_COL_X[1], ink_top, owner, SZ["row_sub"], color=MUTED))
        pG, pT = pill_styles[i]
        p.append(rect(PILL_X, PILL_TY[i], PILL_W, PILL_H, color=pG,
                      radius=PILL_H / 2))
        # alignment="CENTER" 按盒高居中；参考的胶囊文字比居中位置高 2 px，
        # 所以文字盒比胶囊盒矮 4 px（顶边不动），中心上移 2 px。三行一致。
        p.append(text(PILL_X, PILL_TY[i], PILL_W, PILL_H - 4, status, SZ["pill"],
                      color=pT, style="BOLD", align="CENTER"))
        p.append(text_at(TBL_COL_X[3], ink_top, due, SZ["row_sub"], color=MUTED))

    # ---- 页脚
    p.append(text_at(FOOT_TXT[0], FOOT_TXT[1], c["footer"], SZ["footer"],
                     color=TXT_LIGHT))

    meta = {
        "canvas": [W, H],
        "cards": {"kpi": [[x, KPI_Y, x + KPI_W - 1, KPI_Y + KPI_H - 1]
                          for x in KPI_XS],
                  "chart": [CHART_X, CARD2_Y, CHART_X + CHART_W - 1,
                            CARD2_Y + CARD2_H - 1],
                  "activity": [ACT_X, CARD2_Y, ACT_X + ACT_W - 1,
                               CARD2_Y + CARD2_H - 1],
                  "table": [CONTENT_L, TBL_Y, CONTENT_R, TBL_Y + TBL_H - 1]},
        "nav_box": [NAV_BOX[0], NAV_BOX[1], NAV_BOX[0] + NAV_BOX[2] - 1,
                    NAV_BOX[1] + NAV_BOX[3] - 1],
        "workspace_card": [WS_BOX[0], WS_BOX[1], WS_BOX[0] + WS_BOX[2] - 1,
                           WS_BOX[1] + WS_BOX[3] - 1],
        "header_band": [TBAND[0], TBAND[1], TBAND[0] + TBAND[2] - 1,
                        TBAND[1] + TBAND[3] - 1],
        "dividers": [[TBAND[0], dy_, TBAND[0] + TBAND[2] - 1, dy_]
                     for dy_ in TBL_DIV_YS],
        "logo_ring": [LOGO[0], LOGO[1], LOGO[0] + LOGO[2] - 1,
                      LOGO[1] + LOGO[3] - 1],
        "button": [BTN[0], BTN[1], BTN[0] + BTN[2] - 1, BTN[1] + BTN[3] - 1],
        "sidebar_right": SIDEBAR_W,
        "zero_line_left": [GRID_X0, ZERO_Y],
        "nav_text_ink_top": [float(v) for v in NAV_INK_TY],
        "activity_items": [{"ink_top": float(ACT_TY[i]),
                            "dot_cx": ACT_DOT_X, "dot_cy": float(ACT_DOT_CY[i]),
                            "dot_d": ACT_DOT_D} for i in range(3)],
        "bars": [{"value": v, "center_x": cx,
                  "left": int(cx - BAR_W / 2 + 0.5), "width": BAR_W,
                  "top": ZERO_Y - math.ceil(v * 1.2),
                  "height": math.ceil(v * 1.2)}
                 for v, cx in zip(c["chart_values"], BAR_CENTERS)],
        "pills": [[PILL_X, PILL_TY[i], PILL_X + PILL_W - 1,
                   PILL_TY[i] + PILL_H - 1] for i in range(3)],
        "gridlines": GRID_YS,
        "font_sizes": SZ,
        "em_ink_top": EM_INK_TOP,
    }
    return snapshot(W, H, p), meta


# ---------------------------------------------------------------- 探针
def build_probe() -> tuple[str, dict]:
    """探针页：确认不能靠假设的几件事。

    1. Inter 三个字重渲染差异（Regular / BOLD / Extra Bold）；
    2. 特殊字形 ¥ − – · → 是否缺字（豆腐块）；
    3. borderRadiusTopLeft/TopRight 是否生效（柱顶圆角）；
    4. shape="CIRCLE" + border 是否画成圆环（logo）；
    5. 「盒顶 → 墨迹顶」偏移：一行已知字符串，量出真实 EM_INK_TOP。
    """
    p = [rect(0, 0, W, H, color=CARD)]
    y = 56
    for fam, sty in ((F, ""), (F, "BOLD"), (EXTRA, "")):
        p.append(text_at(60, y, "fontFamily 『%s』   fontStyle 『%s』"
                     % (fam, sty or "none"), 15, color=MUTED))
        p.append(text_at(60, y + 30, "AB The quick 0123 ¥128,400", 34,
                     family=fam, style=sty, color=INK))
        p.append(rect(60, y + 76, 900, 1, color="#E11"))
        y += 104
    y += 8
    p.append(text_at(60, y, "特殊字形：¥128,400  −0.8 pp  Apr – Sep  "
                            "fictional · Snapshot  Manage access  →", 34,
                     style="BOLD", color=INK))
    y += 66
    # 柱顶圆角：三个不同 radius 的柱并排
    for i, r in enumerate((0.0, 3.0, 6.0)):
        p.append(rect(80 + i * 90, y + 60, 54, 120, color=BLUE,
                      r_tl=(r if r else None), r_tr=(r if r else None)))
        p.append(text_cx(80 + i * 90 + 27, y + 12, "radius %g" % r, 15,
                         color=MUTED))
    y += 190
    # 圆环：shape=CIRCLE + border
    p.append(circle(100, y + 24, 30, color=SIDEBAR, border="3 SOLID " + MINT))
    p.append(circle(150, y + 24, 12, color=MINT))
    p.append(text_at(200, y + 12, "shape=CIRCLE + border  /  solid dot", 18,
                     color=INK))
    y += 76
    # 墨迹顶偏移校准：同一字符串在三个字号下，红线下缘即目标墨迹顶
    for sz in (13.0, 22.0, 36.0):
        p.append(text_at(60, y, "Calibrate INKTOP 0123", sz, style="BOLD",
                         color=INK))
        p.append(rect(60, y - 1, 620, 1, color="#E11"))
        p.append(text_cx(780, y - 6, "box_top = %g   fontSize %g"
                         % (y - EM_INK_TOP * sz, sz), 14, color=MUTED))
        y += 56
    return snapshot(W, H, p), {"em_ink_top": EM_INK_TOP}


def checks() -> list[str]:
    """前置校验：不发请求，只查本文件自身的一致性。

    所有盒子一律按 (x, y, w, h) 记，外轮廓是 [x, y, x+w-1, y+h-1]。
    """
    probs: list[str] = []

    # 28 px 栅格与内容栏
    if min(KPI_XS) != CONTENT_L:
        probs.append("KPI 行左缘 %d ≠ 内容栏左缘 %d"
                     % (min(KPI_XS), CONTENT_L))
    if CONTENT_R - (KPI_XS[-1] + KPI_W - 1) != 16:
        probs.append("KPI 行右缘余量 %d ≠ 参考的 16 px"
                     % (CONTENT_R - (KPI_XS[-1] + KPI_W - 1)))
    for x0, x1 in zip(KPI_XS, KPI_XS[1:]):
        if x1 - (x0 + KPI_W) != GRID_GAP:
            probs.append("KPI 卡间距 %d ≠ %d" % (x1 - x0 - KPI_W, GRID_GAP))
    if ACT_X - (CHART_X + CHART_W) != GRID_GAP:
        probs.append("图表卡与活动卡间距 %d ≠ %d"
                     % (ACT_X - CHART_X - CHART_W, GRID_GAP))
    if CHART_X + CHART_W - 1 != 1001:
        probs.append("图表卡右缘 %d ≠ 参考 1001" % (CHART_X + CHART_W - 1))
    if ACT_X + ACT_W - 1 != CONTENT_R:
        probs.append("活动卡右缘 %d ≠ 内容栏右缘 %d"
                     % (ACT_X + ACT_W - 1, CONTENT_R))
    if CONTENT_L + TBL_W - 1 != CONTENT_R:
        probs.append("表格卡右缘 %d ≠ 内容栏右缘 %d"
                     % (CONTENT_L + TBL_W - 1, CONTENT_R))
    for y0, y1, tag in ((KPI_Y + KPI_H, CARD2_Y, "KPI 行 → 第二行"),
                        (CARD2_Y + CARD2_H, TBL_Y, "第二行 → 表格行")):
        if y1 - y0 != GRID_GAP:
            probs.append("%s 间距 %d ≠ %d" % (tag, y1 - y0, GRID_GAP))
    if (KPI_Y, KPI_H, CARD2_Y, CARD2_H, TBL_Y, TBL_H) != (138, 144, 310, 286,
                                                           624, 218):
        probs.append("行高与参考测量不一致")
    for x, y, w, h, tag in ((KPI_XS[0], KPI_Y, KPI_W, KPI_H, "KPI1"),
                            (CHART_X, CARD2_Y, CHART_W, CARD2_H, "图表卡"),
                            (ACT_X, CARD2_Y, ACT_W, CARD2_H, "活动卡"),
                            (CONTENT_L, TBL_Y, TBL_W, TBL_H, "表格卡")):
        if (x, y, x + w - 1, y + h - 1) not in (
                (260, 138, 615, 281), (644, 138, 999, 281),
                (260, 310, 1001, 595), (1030, 310, 1399, 595),
                (260, 624, 1399, 841)):
            probs.append("%s 外轮廓 [%d,%d,%d,%d] 不在参考测量集里"
                         % (tag, x, y, x + w - 1, y + h - 1))

    # 图表
    for gy in GRID_YS:
        if abs((ZERO_Y - gy) % 36) > 1e-6:
            probs.append("网格线 y=%d 不在 36 px 网格上" % gy)
    if GRID_YS != (405, 441, 477, 513, 549) or GRID_X0 != 333 or GRID_X1 != 969:
        probs.append("绘图区范围与参考测量不一致")
    for cx0, cx1 in zip(BAR_CENTERS, BAR_CENTERS[1:]):
        if abs((cx1 - cx0) - 101) > 1e-6:
            probs.append("柱心步进异常 %g" % (cx1 - cx0))
    for cx in BAR_CENTERS:
        if not (GRID_X0 < cx - BAR_W / 2 and cx + BAR_W / 2 < GRID_X1 + 1):
            probs.append("柱体越出绘图区：中心 %g" % cx)
    if BAR_CENTERS[-1] != 888.5:
        probs.append("最后一根柱心 %g ≠ 参考 888.5" % BAR_CENTERS[-1])

    # 内容数量
    c = load_content()
    if len(c["chart_values"]) != len(BAR_CENTERS) or len(c["months"]) != 6:
        probs.append("图表数据与柱心数量不匹配")
    if len(c["chart_ticks"]) != len(GRID_YS):
        probs.append("刻度数量与网格线数量不匹配")
    # y 轴方向守卫：GRID_YS 自上而下，刻度用 reversed(chart_ticks) 配对，
    # 所以内容里的 chart_ticks 必须是升序，最上一条网格线才对应最大刻度。
    if c["chart_ticks"] != sorted(c["chart_ticks"]):
        probs.append("chart_ticks 不是升序，y 轴方向会与参考相反：%s"
                     % c["chart_ticks"])
    if len(c["kpis"]) != 3 or len(c["activity"]) != 3 or len(c["rows"]) != 3:
        probs.append("KPI / 活动 / 表格行数异常")
    if len(c["navigation"]) != 4 or len(c["workspace_info"]) != 3 \
            or len(c["table_columns"]) != 4:
        probs.append("导航 / 工作区 / 表头数量异常")
    for r in c["rows"]:
        if len(r) != 4:
            probs.append("表格行字段数异常")

    # 文案必须逐字来自输入
    dsl, meta = build()
    for s in (c["title"], c["subtitle"], c["button"], c["footer"], c["brand"],
              c["chart_title"], c['chart_period'], c["chart_unit"],
              c["activity_title"], c["table_title"]):
        if 'text="%s"' % s not in dsl:
            probs.append("DSL 缺少文案 %r" % s)
    for k in c["kpis"]:
        for v in (k["label"], k["value"], k["change"]):
            if 'text="%s"' % v not in dsl:
                probs.append("DSL 缺少 KPI 文案 %r" % v)
    for a in c["activity"]:
        for v in a:
            if 'text="%s"' % v not in dsl:
                probs.append("DSL 缺少活动文案 %r" % v)
    for r in c["rows"]:
        for v in r:
            if 'text="%s"' % v not in dsl:
                probs.append("DSL 缺少表格文案 %r" % v)
    for n in c["navigation"]:
        if 'text="%s"' % n not in dsl:
            probs.append("DSL 缺少导航文案 %r" % n)
    for s in c["workspace_info"]:
        if 'text="%s"' % s not in dsl:
            probs.append("DSL 缺少工作区文案 %r" % s)
    for m in c["months"]:
        if 'text="%s"' % m not in dsl:
            probs.append("DSL 缺少月标签 %r" % m)

    # DSL 结构
    if dsl.count("<Positioned") != dsl.count("</Positioned>"):
        probs.append("Positioned 标签不闭合")
    for tag in ("<Snapshot", "<Stack", "¥", "−", "–", "·", "→"):
        if tag not in dsl:
            probs.append("DSL 缺少关键片段 %r" % tag)
    if "&lt;" in dsl or "&amp;" in dsl or "&gt;" in dsl:
        probs.append("DSL 里出现了 XML 实体（服务不解码，会原样显示）")
    if 'family="' in dsl and 'Inter' not in dsl:
        probs.append("DSL 未使用 Inter 字族")

    # 关键几何结论
    if meta["bars"][-1]["top"] != 419:
        probs.append("最后一根柱顶 %g ≠ 参考 419" % meta["bars"][-1]["top"])
    if meta["bars"][-1]["center_x"] != 888.5:
        probs.append("最后一根柱心 %g ≠ 参考 888.5" % meta["bars"][-1]["center_x"])
    if meta["zero_line_left"] != [333, 549]:
        probs.append("零线左端点 %s ≠ 参考 [333, 549]" % meta["zero_line_left"])
    if meta["nav_box"] != [18, 116, 201, 163]:
        probs.append("导航选中底 %s ≠ 参考 [18,116,201,163]" % meta["nav_box"])
    if meta["workspace_card"] != [22, 752, 197, 867]:
        probs.append("工作区卡 %s ≠ 参考填充 [22,752,197,867]"
                     % meta["workspace_card"])
    # 带与两条分隔线在参考图里同为 x 284..1373（比卡片内容右缘 1398 短 25 px）。
    # 首版画到卡片右缘，只在把审计窗口收紧到卡片内部后才发现。
    if meta["header_band"] != [284, 688, 1373, 721]:
        probs.append("表头带 %s ≠ 参考 [284,688,1373,721]" % meta["header_band"])
    if meta["dividers"] != [[284, 760, 1373, 760], [284, 795, 1373, 795]]:
        probs.append("行分隔线 %s ≠ 参考 y=760/795、x 284..1373"
                     % meta["dividers"])
    if meta["logo_ring"] != [30, 33, 57, 60]:
        probs.append("logo 圆环 %s ≠ 参考 [30,33,57,60]" % meta["logo_ring"])
    if meta["pills"][-1] != [1028, 799, 1175, 826]:
        probs.append("末行胶囊 %s ≠ 参考 [1028,799,1175,826]" % meta["pills"][-1])

    # 表头带与行分隔线不能越出表格卡，也不能压住文字
    if not (CONTENT_L < TBAND[0] and TBAND[0] + TBAND[2] - 1 <= CONTENT_R):
        probs.append("表头带越出表格卡左右缘")
    if TBAND[1] < TBL_Y or TBAND[1] + TBAND[3] - 1 > TBL_Y + TBL_H - 1:
        probs.append("表头带越出表格卡上下缘")
    for dy_ in TBL_DIV_YS:
        if TBL_HDR_INK + 20 > dy_ - 8 or dy_ > TBL_ROW_INK[-1] - 4:
            probs.append("行分隔线 y=%g 位置异常" % dy_)

    # 文字锚点必须在画布内且不越出内容栏（防越界与裁切）。
    # 页头文字（标题/副标题）在 KPI 行上方，页脚在表格卡下方，所以纵向只约束
    # 画布范围，横向约束内容栏；再单独要求页头不与 KPI 行重叠、页脚不与表格卡重叠。
    for x, y, tag in ((T_X, 38.0, "主标题"), (T_X, 85.0, "副标题"),
                      (286.0, 645.0, "表格标题"), (FOOT_TXT[0], FOOT_TXT[1], "页脚")):
        if not (CONTENT_L - 4 <= x <= CONTENT_R and 20 <= y <= H - 10):
            probs.append("%s 锚点 (%g,%g) 越出内容栏或画布" % (tag, x, y))
    for x, ink_top, size, y_max, tag in ((T_X, 38.0, SZ["title"], KPI_Y, "主标题"),
                                         (T_X, 85.0, SZ["subtitle"], KPI_Y, "副标题")):
        if ink_top + lh(size) > y_max:
            probs.append("%s 墨迹与 KPI 行重叠：底部 %g > %d"
                         % (tag, ink_top + lh(size), y_max))
    if FOOT_TXT[1] < TBL_Y + TBL_H:
        probs.append("页脚墨迹顶 %g 落在表格卡内" % FOOT_TXT[1])
    for i, x0 in enumerate(KPI_XS):
        if not (x0 + PAD_IN >= x0 + 20 and x0 + PAD_IN <= x0 + KPI_W - 40):
            probs.append("KPI%d 文字左内边距 %g 越界" % (i + 1, PAD_IN))
    return probs


def _write(dst: Path, body: bytes | str, text_mode: bool = False) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if text_mode:
        dst.write_text(body, encoding="utf-8")
    else:
        dst.write_bytes(body)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "checks"
    if mode == "checks":
        probs = checks()
        if not probs:
            print("checks: 全部通过")
        else:
            print("checks: %d 项未通过" % len(probs))
            for x in probs:
                print("  -", x)
        return 1 if probs else 0
    if mode == "probe":
        dsl, m = build_probe()
        r = C.render(TASK, dsl, "probe-typography", kind="render",
                     purpose="A15 探针：Inter 字重、特殊字形缺字、柱顶圆角、"
                             "shape=CIRCLE 描边、墨迹顶偏移校准")
        print("探针 HTTP", r["status"], "bytes", r["log"].get("response_bytes"),
              "rid", r["request_id"])
        if r["status"] != 200:
            print("错误：", r["log"].get("error"))
            return 1
        p = TMP / "preview" / "a15-probe.png"
        _write(p, r["body"])
        print("->", S.rel(p))
        (TMP / "gen").mkdir(parents=True, exist_ok=True)
        (TMP / "gen" / "probe.meta.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    if mode == "finals":
        OUT.mkdir(parents=True, exist_ok=True)
        (TMP / "gen").mkdir(parents=True, exist_ok=True)
        probs = checks()
        if probs:
            print("前置校验未通过，不渲染：")
            for x in probs:
                print("  -", x)
            return 1
        dsl, meta = build()
        r = C.render(TASK, dsl, "reconstructed", kind="render",
                     purpose="A15 最终交付：1440×900 参考图重建")
        print("渲染 HTTP", r["status"], "bytes", r["log"].get("response_bytes"),
              "rid", r["request_id"])
        if r["status"] != 200:
            print("错误：", r["log"].get("error"))
            return 1
        OUT.mkdir(parents=True, exist_ok=True)
        (TMP / "gen").mkdir(parents=True, exist_ok=True)
        (OUT / "reconstructed.png").write_bytes(r["body"])
        (OUT / "reconstructed.snapshot").write_text(dsl, encoding="utf-8")
        (TMP / "gen" / "layout.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("->", S.rel(OUT / "reconstructed.png"))
        print("->", S.rel(OUT / "reconstructed.snapshot"))
        print("->", S.rel(TMP / "gen" / "layout.json"))
        return 0
    print("用法: a15_pages.py [checks|probe|finals]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
