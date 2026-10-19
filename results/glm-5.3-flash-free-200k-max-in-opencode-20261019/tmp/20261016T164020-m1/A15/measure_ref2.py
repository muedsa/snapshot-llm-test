# -*- coding: utf-8 -*-
"""A15 补测：logo/导航/表头/文字带等第二组采样。追加到 ref-measure2.json。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
REF = "tasks/A15-reference-reconstruction/inputs/reference.png"
STEPS = "tmp/20261016T164020-m1/A15/steps"
im = Image.open(REF).convert("RGB")
px = im.load()

def hexc(rgb):
    return "#%02X%02X%02X" % rgb

M2 = {}
pts = {"logo_c": (44, 44), "logo_1": (36, 38), "logo_2": (52, 52), "logo_3": (44, 52),
       "pill_bg_r": (196, 128), "pill_bg_l": (26, 156), "pill_bg2": (180, 152),
       "navtext": (80, 205), "pill_mid": (100, 160),
       "btn_blue2": (1210, 55), "card_white2": (600, 160), "subgray": (270, 94),
       "table_h_1": (500, 700), "table_h_2": (500, 695), "table_h_3": (980, 710),
       "status_inpro_bg2": (1040, 742), "status_review_bg2": (1040, 777), "status_done_bg2": (1040, 812),
       "foot": (275, 872), "owner_gray": (800, 743), "due_gray": (1240, 812),
       "proj_ink": (310, 743), "month_gray": (383, 568), "axis_gray": (300, 405),
       "unit_gray": (286, 381), "period_gray": (960, 345), "act_time_gray": (1080, 428),
       "sidebar_text_gray": (66, 200), "sidebar_pro_teal": (44, 777),
       "rowsep": (700, 762), "grid_gray": (900, 477)}
for k, (x, y) in pts.items():
    M2[k] = {"xy": [x, y], "hex": hexc(px[x, y])}

# logo 区域 5×5 网格主色频次
from collections import Counter
c = Counter()
for yy in range(28, 58):
    for xx in range(28, 58):
        c[hexc(px[xx, yy])] += 1
M2["logo_palette_top"] = c.most_common(6)

def bands(y0, y1, x0, x1, pred, min_h=4, step=1):
    rows = []
    cur = None
    for y in range(y0, y1):
        ink = any(pred(*px[x, y]) for x in range(x0, x1, step))
        if ink and cur is None:
            cur = y
        elif not ink and cur is not None:
            if y - cur >= min_h:
                rows.append([cur, y - 1])
            cur = None
    if cur is not None:
        rows.append([cur, y1 - 1])
    return rows

dark = lambda r, g, b: (r < 90 and g < 95) or (r < 60 and g < 70 and b < 90)
light = lambda r, g, b: r > 200 and g > 200 and b > 200
teal = lambda r, g, b: r < 120 and g > 120 and b < 200 and g - r > 40

# 侧栏内浅色文字行带（0..220, 90..870）:白色/亮灰
M2["sidebar_text_bands"] = {"method": "亮色行带 x0..220", "bands": bands(90, 760, 24, 205, light, 4)}
M2["sidebar_bottom_bands"] = {"method": "底部面板文字行带 756..870", "bands": bands(756, 875, 24, 205, light, 3), "teal_bands": bands(760, 875, 24, 205, teal, 3)}
# 主区文字/元素行带:标题+副标题 (255..1060, 20..110)
M2["header_text_bands"] = {"method": "暗墨/灰行带 (255..1060,20..115)", "bands": bands(20, 115, 255, 1060, lambda r, g, b: r < 150 and not (r > 240), 4)}
# KPI 卡内文字带 (col 283..610, 139..281)
M2["kpi_text_bands"] = {"method": "暗墨带 kpi1", "bands": bands(141, 280, 283, 610, dark, 4)}
# 图表卡文字带 (283..980, 313..600)
M2["chart_text_bands"] = {"method": "暗墨带 chart(含柱)", "bands": bands(313, 600, 284, 980, dark, 4)}
# 月份标签带 (335..940, 552..585)
grayish = lambda r, g, b: 100 < r < 190 and 100 < g < 190 and 110 < b < 200
M2["month_bands"] = {"method": "灰行带", "bands": bands(550, 590, 345, 940, grayish, 3)}
# 表格文字带 (283..1375, 660..838)
M2["table_text_bands"] = {"method": "暗墨带 table", "bands": bands(655, 838, 300, 1375, dark, 3)}
# 状态文字(彩色)带STATUS 列 (1035..1170, 725..830)
M2["status_text_bands"] = {"method": "彩字行带", "bands": bands(725, 830, 1038, 1170, lambda r, g, b: abs(r - g) > 25 or abs(g - b) > 25, 3)}
# 表头带精确 x 范围:y=696(标签行上)颜色
M2["header_band_y700_full"] = [{"x": x, "hex": hexc(px[x, 700])} for x in (270, 282, 285, 320, 700, 1100, 1300, 1340, 1360, 1372, 1373, 1376)]
# 表头带 y 范围:col 500
def seg_on_col(x, y0, y1, pred, min_len=3):
    out, s = [], None
    for y in range(y0, y1):
        ok = pred(*px[x, y])
        if ok and s is None:
            s = y
        elif not ok and s is not None:
            if y - s >= min_len:
                out.append((s, y - 1))
            s = None
    if s is not None:
        out.append((s, y1 - 1))
    return out
M2["header_col500"] = {"method": "col500 近bg纵段(660..740)", "segs": seg_on_col(500, 660, 740, lambda r, g, b: 238 <= r <= 248 and 240 <= g <= 250 and 246 <= b <= 255, 3)}
# 行分隔线:col700 内 205..235 灰线
M2["rowsep_col700"] = {"method": "col700 灰线段(730..840)", "segs": seg_on_col(700, 730, 840, lambda r, g, b: 215 <= r <= 240 and 220 <= g <= 244 and 228 <= b <= 250, 1)}
# 侧栏底面板盒:col 200 与 row 800 扫描
M2["sidepanel_edges"] = {
    "row800_runs": None,
}
onedark = lambda r, g, b: r < 100 and g < 110 and b < 140
def runs_on_row(y, x0, x1, pred, min_len=3):
    out, s = [], None
    for x in range(x0, x1):
        ok = pred(*px[x, y])
        if ok and s is None:
            s = x
        elif not ok and s is not None:
            if x - s >= min_len:
                out.append((s, x - 1))
            s = None
    if s is not None:
        out.append((s, x1 - 1))
    return out
# 底面板比 bg_sidebar 亮: 0x1B..0x3A
panel = lambda r, g, b: 24 <= r <= 60 and 40 <= g <= 72 and 70 <= b <= 105
M2["sidepanel_row800"] = {"method": "row800 亮面板段", "runs": runs_on_row(800, 0, 220, panel, 10)}
M2["sidepanel_col110"] = {"method": "col110 亮面板纵段(700..890)", "segs": seg_on_col(110, 700, 890, panel, 10)}
# 活动点 y 中心:col 1058..1066 色点包围
for nm, pred in (("amber", lambda r, g, b: r > 190 and 130 < g < 200 and b < 120),
                 ("blue", lambda r, g, b: 30 <= r <= 80 and 90 <= g <= 130 and 205 <= b <= 255),
                 ("green", lambda r, g, b: r < 110 and g > 110 and b < 180)):
    x0, y0, x1, y1 = None, None, None, None
    for y in range(385, 570):
        for x in range(1048, 1070):
            if pred(*px[x, y]):
                x0 = x if x0 is None else min(x0, x)
                x1 = x if x1 is None else max(x1, x)
                y0 = y if y0 is None else min(y0, y)
                y1 = y if y1 is None else max(y1, y)
    M2["actdot_" + nm] = {"box": [x0, y0, x1, y1]}
json.dump(M2, open(os.path.join(STEPS, "ref-measure2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in M2.items():
    print(k, "=>", json.dumps(v, ensure_ascii=False))
