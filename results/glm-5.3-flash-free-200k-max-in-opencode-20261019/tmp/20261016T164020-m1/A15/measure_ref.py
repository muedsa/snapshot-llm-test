# -*- coding: utf-8 -*-
"""A15 参考图测量：从 inputs/reference.png（公开参考，无作者坐标）像素级估计锚点、采样色板。
输出 ref-measure.json（临时目录），供 DSL 构建与 reconstruction-audit.json 使用。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
REF = "tasks/A15-reference-reconstruction/inputs/reference.png"
STEPS = "tmp/20261016T164020-m1/A15/steps"
os.makedirs(STEPS, exist_ok=True)
im = Image.open(REF).convert("RGB")
px = im.load()
W, H = im.size
print("size", W, H)

def hexc(rgb):
    return "#%02X%02X%02X" % rgb

def sample(name, x, y):
    return {name: {"xy": [x, y], "hex": hexc(px[x, y])}}

def runs_on_row(y, x0, x1, pred, min_len=3):
    """返回一行中满足 pred 的连续段 [(start,end)]"""
    out = []
    s = None
    for x in range(x0, x1):
        ok = pred(*px[x, y])
        if ok and s is None:
            s = x
        elif not ok and s is not None:
            if x - s >= min_len:
                out.append((s, x - 1))
            s = None
    if s is not None and x1 - s >= min_len:
        out.append((s, x1 - 1))
    return out

def col_top_in_band(x, y0, y1, pred):
    for y in range(y0, y1):
        if pred(*px[x, y]):
            return y
    return None

def col_bottom_in_band(x, y0, y1, pred):
    r = None
    for y in range(y0, y1):
        if pred(*px[x, y]):
            r = y
    return r

M = {}
M.update(sample("bg_main", 700, 120))
M.update(sample("bg_sidebar", 110, 400))
M.update(sample("sidebar_active_pill", 110, 140))
M.update(sample("sidebar_card", 110, 800))
M.update(sample("card_white", 300, 200))
M.update(sample("btn_blue", 1290, 67))
M.update(sample("bar_blue", 383, 520))
M.update(sample("title_ink", 276, 52))
M.update(sample("sub_gray", 262, 92))
M.update(sample("kpi_change_green", 292, 252))
M.update(sample("status_inpro_bg", 1100, 742))
M.update(sample("status_review_bg", 1100, 778))
M.update(sample("status_done_bg", 1100, 812))
M.update(sample("table_header_bg", 700, 705))
M.update(sample("act_dot_amber", 1058, 403))
M.update(sample("act_dot_blue", 1058, 465))
M.update(sample("act_dot_green", 1058, 527))
M.update(sample("logo_teal", 44, 44))

BG = (0xF1, 0xF4, 0xF9)
def is_bg(r, g, b):
    return abs(r - BG[0]) < 7 and abs(g - BG[1]) < 7 and abs(b - BG[2]) < 7

def is_white(r, g, b):
    return r > 248 and g > 248 and b > 252

# 侧栏右边界（y=450 行，主bg 起点）
r = runs_on_row(450, 150, 320, is_bg, 2)
M["sidebar_right_edge"] = {"method": "row450 主bg首段起点", "x": r[0][0] if r else None, "runs": r[:2]}
# KPI 三卡:行 y=210 白色连续段
M["kpi_cards_row210"] = {"method": "row210 白色连续段", "runs": runs_on_row(210, 230, 1440, is_white, 8)}
# KPI 卡上/下缘:列 x=300 在 (100..320) 内非背景段
def seg_on_col(x, y0, y1, pred, min_len=5):
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
M["kpi1_col300"] = {"method": "col300 白色纵向段", "segs": seg_on_col(300, 100, 320, is_white, 8)}
# 图表卡:行 y=450 白段(260..1010)
M["chart_card_row450"] = {"method": "row450 白段(230..1015)", "runs": runs_on_row(450, 230, 1015, is_white, 8)}
# 活动卡:行 y=450 (1015..1440)
M["activity_card_row450"] = {"method": "row450 白段", "runs": runs_on_row(450, 1015, 1440, is_white, 8)}
# 表格卡:行 y=680 白段 + 列 x=700 白色纵向段(600..860)
M["table_card_row680"] = {"method": "row680 白段", "runs": runs_on_row(680, 230, 1440, is_white, 8)}
M["table_card_col700"] = {"method": "col700 白色纵段(600..880)", "segs": seg_on_col(700, 600, 880, is_white, 8)}
# 网格线:灰线行检测（x 340..960 内几乎整行近似 #E2E7F1）
def is_grid(r, g, b):
    return 205 <= r <= 238 and 210 <= g <= 242 and 225 <= b <= 252 and not is_white(r, g, b)
grid_rows = []
for y in range(390, 565):
    cnt = sum(1 for x in range(340, 960, 8) if is_grid(*px[x, y]))
    if cnt > 60:
        grid_rows.append(y)
# 合并相邻行
merged = []
for y in grid_rows:
    if merged and y - merged[-1][-1] <= 2:
        merged[-1].append(y)
    else:
        merged.append([y])
M["gridlines_y"] = {"method": "x340..960 整行灰线检测", "rows": [m[len(m) // 2] for m in merged], "raw_len": [len(m) for m in merged]}
# 网格线左端:行 y=零线（取最低网格线）向左找起点
gy = [m[len(m) // 2] for m in merged]
if gy:
    zy = max(gy)
    zx = None
    for x in range(300, 500):
        if is_grid(*px[x, zy]):
            zx = x
            break
    M["zero_line_left"] = {"method": f"行{zy} 向左首个灰像素", "y": zy, "x": zx}
# 柱形:行 y=520 蓝色段（6 段）
def is_blue(r, g, b):
    return 30 <= r <= 80 and 90 <= g <= 130 and 205 <= b <= 255
M["bars_row520"] = {"method": "row520 蓝色段", "runs": runs_on_row(520, 330, 1000, is_blue, 20)}
# 每柱顶部:对最后一柱中心列求最上蓝像素
if M["bars_row520"]["runs"]:
    last = M["bars_row520"]["runs"][-1]
    cx = (last[0] + last[1]) // 2
    top = col_top_in_band(cx, 390, 560, is_blue)
    M["last_bar_top"] = {"method": f"col{cx} 顶蓝像素", "x": cx, "y": top, "bar_span_x": last}
    # 各柱顶部行
    tops = [col_top_in_band((a + b) // 2, 390, 560, is_blue) for a, b in M["bars_row520"]["runs"]]
    M["bar_tops"] = tops
# 按钮盒:蓝像素包围盒 (1150..1430, 30..105)
bx0, by0, bx1, by1 = None, None, None, None
for y in range(30, 105):
    for x in range(1150, 1435):
        if is_blue(*px[x, y]):
            bx0 = x if bx0 is None else min(bx0, x)
            bx1 = x if bx1 is None else max(bx1, x)
            by0 = y if by0 is None else min(by0, y)
            by1 = y if by1 is None else max(by1, y)
M["button_box"] = {"method": "蓝像素包围盒", "box": [bx0, by0, bx1, by1]}
# 导航选中态 pill:侧栏浅色段 行 y=140 (0..219)
def is_pillbg(r, g, b):
    return 22 <= r <= 40 and 36 <= g <= 56 and 62 <= b <= 88
M["nav_active_row140"] = {"method": "row140 侧栏内亮色段", "runs": runs_on_row(140, 5, 219, is_pillbg, 10)}
M["nav_active_col100"] = {"method": "col100 亮色纵段(90..200)", "segs": seg_on_col(100, 90, 200, is_pillbg, 10)}
# 主标题字形框:暗墨(≈#16243C)包围盒 (240..640, 20..80)
def is_ink(r, g, b):
    return r < 70 and g < 80 and b < 100
tx0, ty0 = None, None
for y in range(20, 80):
    for x in range(240, 640):
        if is_ink(*px[x, y]):
            tx0 = x if tx0 is None else min(tx0, x)
            ty0 = y if ty0 is None else min(ty0, y)
M["title_glyph_tl"] = {"method": "暗墨包围盒左上", "xy": [tx0, ty0]}
# 表格 3 行状态 pill:每行浅色底包围盒
def pill_box(pred, y0, y1):
    x0, x1p, y0f, y1f = None, None, None, None
    for y in range(y0, y1):
        for x in range(1000, 1220):
            if pred(*px[x, y]):
                x0 = x if x0 is None else min(x0, x)
                x1p = x if x1p is None else max(x1p, x)
                y0f = y if y0f is None else min(y0f, y)
                y1f = y if y1f is None else max(y1f, y)
    return [x0, y0f, x1p, y1f]
def is_pale_blue(r, g, b):
    return 225 <= r <= 245 and 235 <= g <= 248 and 250 <= b <= 255
def is_pale_amber(r, g, b):
    return r > 245 and 235 <= g <= 248 and 195 <= b <= 230
def is_pale_green(r, g, b):
    return 200 <= r <= 230 and 235 <= g <= 250 and 215 <= b <= 240
M["pill_inprogress"] = {"method": "浅蓝包围盒(1000..1220,720..765)", "box": pill_box(is_pale_blue, 720, 765)}
M["pill_review"] = {"method": "浅琥珀包围盒(...760..800)", "box": pill_box(is_pale_amber, 760, 800)}
M["pill_done"] = {"method": "浅绿包围盒(...795..835)", "box": pill_box(is_pale_green, 795, 835)}
# 表头带:行 y=700 灰白带 x 范围
def is_head(r, g, b):
    return 235 <= r <= 244 and 238 <= g <= 246 and 244 <= b <= 250
M["table_header_row700"] = {"method": "row700 表头灰白段", "runs": runs_on_row(700, 260, 1400, is_head, 20)}
M["table_header_col290"] = {"method": "col290 表头纵段(670..740)", "segs": seg_on_col(290, 670, 740, is_head, 10)}
# 活动卡 y 上缘:col 1100 白段(300..620)
M["activity_card_col1100"] = {"method": "col1100 白段(300..620)", "segs": seg_on_col(1100, 290, 620, is_white, 8)}
# 时间轴文字行(论文):活动行文字 y 范围由暗墨包围盒估（1050..1250, 380..580）
def act_rows():
    rows = []
    cur = None
    for y in range(380, 580):
        ink = any(is_ink(*px[x, y]) for x in range(1070, 1260, 2))
        if ink and cur is None:
            cur = y
        elif not ink and cur is not None:
            if y - cur > 6:
                rows.append([cur, y - 1])
            cur = None
    return rows
M["activity_text_bands"] = {"method": "暗墨行带(1070..1260)", "bands": act_rows()}

json.dump(M, open(os.path.join(STEPS, "ref-measure.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in M.items():
    print(k, "=>", json.dumps(v, ensure_ascii=False))
