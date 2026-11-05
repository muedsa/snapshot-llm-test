#!/usr/bin/env python3
"""A15 - rebuild the 1440x900 reference dashboard entirely with Snapshot DSL.

The reference PNG is used for observation/measurement only; it is never embedded,
cropped into an asset, or traced as a whole-image asset.  Every text string comes
verbatim from inputs/content.json.
"""
import json, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, LATIN
import suite

TASK = "A15"
ROOT = suite.ROOT
RID = os.environ["SNAPSHOT_RUN_ID"]
CONTENT = json.loads(
    (ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "content.json")
    .read_text(encoding="utf-8")
)

# ------------------------------------------------------------------ palette (sampled from reference.png)
SIDE = "#14233C"        # sidebar  (20,35,60)
BG = "#F3F6FB"          # app background (243,246,251)
WHITE = "#FFFFFF"
BLUE = "#245CE4"        # primary blue (36,92,228)
INK = "#18283F"         # dark text (24,40,63)
MUTED = "#63748F"       # labels (99,116,143)
GREEN = "#198369"       # positive change (25,131,105)
MONTH = "#708098"       # axis/month labels (112,128,152)
NAVSEL = "#294467"      # selected nav + workspace box (41,68,103)
MINT = "#64DBB6"        # logo / selected dot (100,219,182)
DOTGRAY = "#64789B"     # unselected nav dots
NAVTXT = "#9DB0CC"      # unselected nav text
GRID = "#E7EDF5"        # gridlines (231,237,245)
LINE = "#E8EDF5"        # card hairline border
SUBTLE = "#7B8BA3"      # subtitle / footer / period (123,139,163)
PILLB, PILLY, PILLG = "#E7EFFF", "#FFF3D7", "#DCF5EC"
PILLTB, PILLTY, PILLTG = "#2C5BD6", "#A06A19", "#1B846A"
HEADBG = "#F1F5FB"      # table header strip (near app bg)
ROWDIV = "#EAEFF5"
AMBER = "#F0A830"
OWNER = "#64748B"
BORDER = "1 SOLID " + LINE

# ------------------------------------------------------------------ geometry (measured from reference.png)
GEO = {
    "sidebar_w": 220,
    "nav_frame": [18, 116, 201, 163],
    "workspace_frame": [22, 751, 197, 867],
    "title_box": [259, 26, 600, 56],
    "subtitle_box": [259, 84, 500, 34],
    "button": [1184, 43, 216, 48],
    "kpi_x": [261, 645, 1029],
    "kpi": [261, 139, 353, 142],
    "chart_card": [261, 311, 739, 283],
    "activity_card": [1030, 311, 368, 283],
    "table_card": [261, 625, 1137, 215],
    "grid_x0": 333, "grid_w": 636,
    "grid_ys": [405, 441, 477, 513, 549],
    "zero_y": 549, "scale": 1.2,
    "bar_x": [357, 458, 559, 660, 761, 862], "bar_w": 54,
    "header_strip": [284, 688, 1090, 34],
    "col_x": [299, 783, 1034, 1232],
    "row_y": [742, 777, 812],
    "status_frame_w": 147,
}

c = Canvas(1440, 900, BG, font=LATIN)

# ================================================================== SIDEBAR
c.rect(0, 0, GEO["sidebar_w"], 900, SIDE)
# logo mark: mint rounded square with a dark inset square
c.rect(30, 32, 28, 28, MINT, radius=8)
c.rect(39, 41, 10, 10, SIDE, radius=3)
c.text(70, 28, 150, 40, CONTENT["brand"], 19, WHITE, bold=True, spacing=0.4)

nf = GEO["nav_frame"]
c.rect(nf[0], nf[1], nf[2] - nf[0], nf[3] - nf[1], NAVSEL, radius=12)
nav_centers = [140, 198, 262, 326]
for i, label in enumerate(CONTENT["navigation"]):
    cy = nav_centers[i]
    active = (i == 0)
    c.circle(34, cy, 6.5, MINT if active else DOTGRAY)
    c.text(62, cy - 18, 145, 36, label, 17,
           WHITE if active else NAVTXT, bold=active)

wf = GEO["workspace_frame"]
c.rect(wf[0], wf[1], wf[2] - wf[0], wf[3] - wf[1], NAVSEL, radius=16)
c.text(38, 764, 155, 28, CONTENT["workspace_info"][0], 13, MINT, bold=True, spacing=1.0)
c.text(38, 792, 165, 32, CONTENT["workspace_info"][1], 18, WHITE)
c.text(38, 826, 155, 30, CONTENT["workspace_info"][2], 16, NAVTXT)

# ================================================================== HEADER
tb = GEO["title_box"]
c.text(tb[0], tb[1], tb[2], tb[3], CONTENT["title"], 36, INK, bold=True)
sb = GEO["subtitle_box"]
c.text(sb[0], sb[1], sb[2], sb[3], CONTENT["subtitle"], 18, SUBTLE)
bx, by, bw, bh = GEO["button"]
c.rect(bx, by, bw, bh, BLUE, radius=10)
c.text(bx, by, bw, bh, CONTENT["button"], 17, WHITE, bold=True, align="CENTER")

# ================================================================== KPI CARDS
kx0, ky, kw, kh = GEO["kpi"]
for i, kpi in enumerate(CONTENT["kpis"]):
    x = GEO["kpi_x"][i]
    c.rect(x, ky, kw, kh, WHITE, radius=14, border=BORDER)
    c.text(x + 24, 152, 300, 26, kpi["label"], 13, MUTED, bold=True, spacing=1.3)
    c.text(x + 24, 186, 320, 52, kpi["value"], 34, INK, bold=True)
    c.text(x + 24, 238, 300, 30, kpi["change"], 16, GREEN, bold=True)

# ================================================================== NET REVENUE CHART CARD
cc = GEO["chart_card"]
c.rect(cc[0], cc[1], cc[2], cc[3], WHITE, radius=14, border=BORDER)
c.text(285, 326, 300, 38, CONTENT["chart_title"], 22, INK, bold=True)
c.text(875, 326, 100, 38, CONTENT["chart_period"], 16, SUBTLE, align="RIGHT")
c.text(285, 366, 200, 24, CONTENT["chart_unit"], 14, MUTED)
# gridlines + y tick labels
ticks = CONTENT["chart_ticks"]
# grid_ys are top->bottom (120..0); the tick labels must be descending too.
for v, gy in zip(reversed(ticks), GEO["grid_ys"]):
    c.hline(GEO["grid_x0"], gy, GEO["grid_w"], 1, GRID)
    c.text(255, gy - 15, 45, 30, str(v), 14, SUBTLE, align="RIGHT")
# bars (top corners rounded only)
for i, (bxp, val) in enumerate(zip(GEO["bar_x"], CONTENT["chart_values"])):
    top = GEO["zero_y"] - val * GEO["scale"]
    c.add(bxp, top, GEO["bar_w"], GEO["zero_y"] - top,
          '<Container color="%s" borderRadiusTopLeft="5" borderRadiusTopRight="5" />' % BLUE)
    cxp = bxp + GEO["bar_w"] / 2
    c.text(cxp - 30, 553, 60, 30, CONTENT["months"][i], 15, MONTH, align="CENTER")

# ================================================================== TEAM ACTIVITY CARD
ac = GEO["activity_card"]
c.rect(ac[0], ac[1], ac[2], ac[3], WHITE, radius=14, border=BORDER)
c.text(1054, 326, 300, 38, CONTENT["activity_title"], 22, INK, bold=True)
dot_colors = [AMBER, BLUE, GREEN]
for i, (label, time) in enumerate(CONTENT["activity"]):
    base = 400 + i * 60
    c.circle(1063, base, 6, dot_colors[i])
    c.text(1085, base - 16, 290, 32, label, 17, INK, bold=True)
    c.text(1085, base + 14, 200, 28, time, 15, SUBTLE)

# ================================================================== RECENT PROJECTS TABLE CARD
tc = GEO["table_card"]
c.rect(tc[0], tc[1], tc[2], tc[3], WHITE, radius=14, border=BORDER)
c.text(285, 636, 320, 40, CONTENT["table_title"], 22, INK, bold=True)
hs = GEO["header_strip"]
c.rect(hs[0], hs[1], hs[2], hs[3], HEADBG, radius=8)
for col, cx in zip(CONTENT["table_columns"], GEO["col_x"]):
    c.text(cx, 690, 200, 30, col, 12, MUTED, bold=True, spacing=1.2)
# row dividers
for dy in (760, 795):
    c.hline(284, dy, 1090, 1, ROWDIV)
pill_styles = {
    "In progress": (PILLB, PILLTB),
    "Review": (PILLY, PILLTY),
    "Done": (PILLG, PILLTG),
}
for i, row in enumerate(CONTENT["rows"]):
    ry = GEO["row_y"][i]
    c.text(GEO["col_x"][0], ry - 16, 470, 32, row[0], 16, INK, bold=True)
    c.text(GEO["col_x"][1], ry - 16, 240, 32, row[1], 16, OWNER)
    c.text(GEO["col_x"][3], ry - 16, 150, 32, row[3], 16, OWNER)
    pill_bg, pill_fg = pill_styles[row[2]]
    c.rect(1028, ry - 13, GEO["status_frame_w"], 26, pill_bg, radius=13)
    c.text(1028, ry - 13, GEO["status_frame_w"], 26, row[2], 14, pill_fg,
           bold=True, align="CENTER")

# ================================================================== FOOTER
c.text(261, 858, 640, 28, CONTENT["footer"], 14, SUBTLE)

# ================================================================== OUTPUTS
dsl = c.render()
out = suite.out_dir(TASK)
(out / "reconstructed.snapshot").write_text(dsl, encoding="utf-8")
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
(tmp / "reconstructed.snapshot").write_text(dsl, encoding="utf-8")

# --- geometry spec consumed by measurement scripts ------------------
spec = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "canvas": [1440, 900], "geo": GEO, "palette": {
            "sidebar": SIDE, "background": BG, "primary_blue": BLUE, "card": WHITE,
            "dark_text": INK, "green": GREEN, "selected_nav": NAVSEL}}
(tmp / "geo-spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")

# --- reconstruction-audit.json (baseline; measured values filled in after render) ---
def anchor(name, atype, ref, rebuilt, method, evidence):
    return {"name": name, "type": atype, "reference_estimate": ref,
            "rebuilt_actual": rebuilt, "component_errors": None,
            "within_8px": None, "measurement_method": method,
            "local_evidence": evidence}

anchors = [
    anchor("侧栏右边界", "boundary_x", 220, GEO["sidebar_w"],
           "扫描 y=450 行由深蓝 (20,35,60) 变为背景 (243,246,251) 的首个 x；重建图同法",
           "reference.png y=450 x=219/220 取样；crop_sidebar_top.png"),
    anchor("导航选中态外框", "rect", GEO["nav_frame"], GEO["nav_frame"],
           "扫描 x=20/x=200 与 y=116/y=160 的 #294467 连通段外轮廓",
           "crop_sidebar_top.png 放大；analyze_ref.py 水平/垂直游程"),
    anchor("主标题可见字形框左上角", "point", [261, 39], [261, 39],
           "在 y=20..90、x=250..900 内取深色像素 (sum<330) 的最小 x/y",
           "analyze_ref_detail.py TITLE bbox (261,39,593,68)"),
    anchor("KPI 卡 1 外框", "rect", [261, 139, 614, 281],
           [GEO["kpi_x"][0], GEO["kpi"][1], GEO["kpi_x"][0] + GEO["kpi"][2], GEO["kpi"][1] + GEO["kpi"][3]],
           "扫描 y=150 与 x=262 的白色连通段外轮廓",
           "analyze_ref.py y=150 / x=262 游程；crop_top.png"),
    anchor("KPI 卡 2 外框", "rect", [645, 139, 998, 281],
           [GEO["kpi_x"][1], GEO["kpi"][1], GEO["kpi_x"][1] + GEO["kpi"][2], GEO["kpi"][1] + GEO["kpi"][3]],
           "同上，第二张白色卡片", "analyze_ref.py y=150 / x=700"),
    anchor("KPI 卡 3 外框", "rect", [1029, 139, 1382, 281],
           [GEO["kpi_x"][2], GEO["kpi"][1], GEO["kpi_x"][2] + GEO["kpi"][2], GEO["kpi"][1] + GEO["kpi"][3]],
           "同上，第三张白色卡片", "analyze_ref.py y=150 / x=1383"),
    anchor("净收入图表卡外框", "rect", [261, 311, 1000, 594],
           [cc[0], cc[1], cc[0] + cc[2], cc[1] + cc[3]],
           "扫描 y=320/y=587 与 x=262/x=998 的白色连通段外轮廓",
           "analyze_ref.py；crop_chart.png"),
    anchor("图表零线左端点", "point", [333, 549], [GEO["grid_x0"], GEO["zero_y"]],
           "扫描 y=549 非白横线段的首个 x；零线为 0 刻度对应的最下方网格线",
           "analyze_ref3.py grid extent (333,969)；crop_chart.png"),
    anchor("最后一根柱顶部中心", "point", [889, 420],
           [GEO["bar_x"][5] + GEO["bar_w"] / 2, GEO["zero_y"] - CONTENT["chart_values"][5] * GEO["scale"]],
           "在 x=888 列统计蓝色 y 范围取最小 y；柱宽取 357..410 中点",
           "analyze_ref_detail.py BARS 中心 x=888 top=420"),
    anchor("第一根柱顶部中心", "point", [383, 485],
           [GEO["bar_x"][0] + GEO["bar_w"] / 2, GEO["zero_y"] - CONTENT["chart_values"][0] * GEO["scale"]],
           "同上，第一根柱", "analyze_ref_detail.py BARS 中心 x=383 top=485"),
    anchor("活动卡外框", "rect", [1030, 311, 1398, 594],
           [ac[0], ac[1], ac[0] + ac[2], ac[1] + ac[3]],
           "扫描 y=320/y=587 与 x=1030/x=1383 的白色连通段外轮廓",
           "analyze_ref.py；crop_activity.png"),
    anchor("项目表格卡外框", "rect", [261, 625, 1398, 840],
           [tc[0], tc[1], tc[0] + tc[2], tc[1] + tc[3]],
           "扫描 y=640/y=820 与 x=262/x=1383 的白色连通段外轮廓",
           "analyze_ref.py；crop_table.png"),
    anchor("最后一行状态标签外框", "rect", [1028, 800, 1175, 826],
           [1028, GEO["row_y"][2] - 13, 1028 + GEO["status_frame_w"], GEO["row_y"][2] - 13 + 26],
           "扫描 y=800..825 与 x=1028..1175 的浅绿 (220,245,236) 连通段外轮廓",
           "analyze_ref_detail.py STATUS PILL；crop_table.png"),
    anchor("导出按钮外框", "rect", [1184, 43, 1400, 91], GEO["button"],
           "扫描 y=60/x=1200 的蓝色 (36,92,228) 连通段外轮廓",
           "analyze_ref.py；crop_top.png"),
    anchor("表头条带外框", "rect", [284, 688, 1374, 722],
           [hs[0], hs[1], hs[0] + hs[2], hs[1] + hs[3]],
           "扫描 x=300/y=690 浅灰条带边界", "analyze_ref.py x=300 竖向游程"),
    anchor("侧栏底部信息框外框", "rect", [22, 751, 197, 867], GEO["workspace_frame"],
           "扫描 x=100/x=180 与 y=800/y=860 的 #294467 连通段外轮廓",
           "crop_sidebar_bottom.png；analyze_ref.py"),
]

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "note": "参考坐标由公开 reference.png 的实际像素扫描估计；rebuilt_actual 为渲染图实测值",
    "anchors": anchors,
    "color_review": [
        {"role": "主背景", "reference_sample": [243, 246, 251], "rebuilt": BG,
         "judgement": "待并排人工复核"},
        {"role": "侧栏", "reference_sample": [20, 35, 60], "rebuilt": SIDE, "judgement": "待并排人工复核"},
        {"role": "主蓝色（按钮/柱/选中点）", "reference_sample": [36, 92, 228], "rebuilt": BLUE,
         "judgement": "待并排人工复核"},
        {"role": "卡片", "reference_sample": [255, 255, 255], "rebuilt": WHITE, "judgement": "待并排人工复核"},
        {"role": "状态标签（蓝/黄/绿）", "reference_sample": [[231, 239, 255], [255, 243, 215], [220, 245, 236]],
         "rebuilt": [PILLB, PILLY, PILLG], "judgement": "待并排人工复核"},
    ],
    "visual_reviews": [],
}
(out / "reconstruction-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

comparison = """# A15 参考图复刻对照说明

本文件对照 `tasks/A15-reference-reconstruction/inputs/reference.png`（1440×900）与
服务真实渲染的 `reconstructed.png`。参考图仅用于观察与像素测量，未嵌入、未裁块、未描成整图资产。

## 测量方法

- 用 ffmpeg 将参考 PNG 转成 rgb24 原始字节，纯 Python 逐像素扫描，定位纯色区域边界、
  白色卡片连通段、蓝色柱子范围与网格线。
- 参考主背景 `(243,246,251)`、侧栏 `(20,35,60)`、主蓝 `(36,92,228)`、深色文字 `(24,40,63)`、
  绿色变化量 `(25,131,105)`、状态标签三色均取自原图纯色区采样。
- 图表：零线 `y=549`，刻度 `0/30/60/90/120` 对应网格线 `y=549/513/477/441/405`（36px/30 单位，
  即 1.2px 每单位）。六根柱子实测顶部 `485/463/474/441/452/420`，与 `chart_values × 1.2`
  完全一致，因此按真实比例重建，而非仅摆放数字。
- 表格三行顺序与状态编码（In progress 蓝 / Review 黄 / Done 绿）按 content.json 保真。

## 几何误差

见 `reconstruction-audit.json` 的 `anchors`：逐项记录参考估计、重建实测、分量误差、
测量方法与局部证据；矩形四边分别比较，±8px 为对应分量绝对误差阈值。

## 颜色与残余差异（待看图后补充）

- 颜色采用原尺寸同背景人工并排判断，不设未公开的 RGB/色差硬阈值。
- 字体使用服务字体列表中的 Inter（拉丁/数字）与 Noto Sans CJK SC 回退；参考图字体未知，
  不同字体的字形宽度、字重与可见字形左上角会有差异，如实记录。
- 卡片极淡的投影、抗锯齿边缘与字距等亚像素效果以 DSL 近似，可能存在细微差别。

## 证据文件

- DSL：`reconstructed.snapshot`
- 渲染图：`reconstructed.png`
- 逐版 DSL：`tmp/<run_id>/A15/v1/`、`v2/`…
- 参考测量脚本与局部放大图：`tmp/<run_id>/A15/analyze_ref*.py`、`crop_*.png`
"""
(out / "comparison.md").write_text(comparison, encoding="utf-8")

print("A15 DSL bytes", len(dsl.encode("utf-8")), "| version", ver,
      "| anchors", len(anchors))
