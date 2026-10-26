"""A15 复刻 vs 参考：全量锚点对比（v3 终版用）。"""
from __future__ import annotations
import json
from PIL import Image

REF = Image.open('tasks/A15-reference-reconstruction/inputs/reference.png').convert('RGB')
REC = Image.open('tmp/run-20261013-174209/A15/reconstructed-v4.png').convert('RGB')
rp, cp = REF.load(), REC.load()


def ink(px, x0, x1, y0, y1, t):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if px[x, y][0] < t]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def ink_pred(px, x0, x1, y0, y1, pred):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if pred(px[x, y])]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def card_bbox(px, x0, x1, y0, y1, border=(226, 232, 241)):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
           if abs(px[x, y][0] - border[0]) <= 8 and abs(px[x, y][1] - border[1]) <= 8
           and abs(px[x, y][2] - border[2]) <= 8]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def rect_by_color(px, pred, x0, x1, y0, y1):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if pred(px[x, y])]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def sidebar_right(px):
    xs = []
    for y in (100, 300, 500, 700, 850):
        for x in range(200, 240):
            if px[x, y][0] < 70 and px[x + 1, y][0] > 200:
                xs.append(x + 1)
                break
    xs.sort()
    return xs[len(xs) // 2]


def bar_top(px, cx):
    for y in range(380, 560):
        c = px[cx, y]
        if abs(c[0] - 36) <= 12 and abs(c[1] - 92) <= 14 and abs(c[2] - 228) <= 12:
            return y
    return None


A = {}


def measure(px):
    a = {}
    a["sidebar_right"] = sidebar_right(px)
    a["nav_sel"] = rect_by_color(px, lambda c: abs(c[0] - 41) <= 8 and abs(c[1] - 68) <= 8
                                 and abs(c[2] - 103) <= 8, 0, 219, 100, 200)
    a["title_tl"] = ink(px, 250, 700, 30, 80, 150)[:2]
    a["subtitle_tl"] = ink(px, 250, 700, 82, 105, 180)[:2]
    for i, (x0, x1) in enumerate(((250, 620), (640, 1000), (1020, 1390)), 1):
        a[f"kpi{i}"] = card_bbox(px, x0, x1, 120, 300)
    a["chart_card"] = card_bbox(px, 250, 1010, 290, 620)
    a["activity_card"] = card_bbox(px, 1020, 1400, 290, 620)
    a["table_card"] = card_bbox(px, 250, 1400, 600, 860)
    row = [x for x in range(325, 1000) if abs(px[x, 549][0] - 231) <= 6
           and abs(px[x, 549][2] - 245) <= 6]
    a["zero_line"] = (min(row), 549, max(row), 549)
    a["last_bar_top"] = (888, bar_top(px, 888))
    a["pill_done"] = rect_by_color(px, lambda c: abs(c[0] - 220) <= 10 and abs(c[1] - 245) <= 8
                                   and abs(c[2] - 236) <= 8, 1000, 1200, 780, 840)
    a["pill_progress"] = rect_by_color(px, lambda c: abs(c[0] - 231) <= 8 and abs(c[1] - 239) <= 8
                                       and abs(c[2] - 255) <= 8, 1000, 1200, 715, 765)
    a["pill_review"] = rect_by_color(px, lambda c: abs(c[0] - 255) <= 6 and abs(c[1] - 243) <= 8
                                     and abs(c[2] - 215) <= 10, 1000, 1200, 750, 800)
    a["button"] = rect_by_color(px, lambda c: abs(c[0] - 36) <= 12 and abs(c[1] - 92) <= 14
                                and abs(c[2] - 228) <= 12, 1150, 1430, 30, 100)
    a["pro_card"] = rect_by_color(px, lambda c: abs(c[0] - 35) <= 8 and abs(c[1] - 57) <= 8
                                  and abs(c[2] - 84) <= 8, 0, 219, 740, 880)
    a["head_band"] = rect_by_color(px, lambda c: abs(c[0] - 243) <= 4 and abs(c[1] - 246) <= 4
                                   and abs(c[2] - 251) <= 4, 262, 1398, 680, 730)
    for i, dy in enumerate((760, 795), 1):
        row = [x for x in range(270, 1395) if abs(px[x, dy][0] - 235) <= 8
               and abs(px[x, dy][2] - 245) <= 8]
        a[f"divider{i}"] = (min(row), dy, max(row), dy)
    for i, cx in enumerate((383, 484, 585, 686, 787, 888), 1):
        a[f"bar{i}_top"] = bar_top(px, cx)
    for m, (x0, x1) in {"Apr": (360, 410), "May": (460, 510), "Jun": (560, 610),
                        "Jul": (660, 715), "Aug": (765, 810), "Sep": (865, 915)}.items():
        b = ink(px, x0, x1, 555, 580, 210)
        a[f"month_{m}"] = ((b[0] + b[2]) / 2, b[1]) if b else None
    a["footer"] = ink(px, 260, 700, 860, 890, 190)
    # 文本锚点
    a["t_northstar"] = ink(px, 65, 200, 32, 58, 200)
    a["t_overview"] = ink_pred(px, 55, 200, 122, 145, lambda c: c[0] > 245 and c[1] > 245)
    a["t_projects"] = ink_pred(px, 55, 200, 186, 212, lambda c: 175 < c[0] < 218 and c[1] > 185)
    a["t_analytics"] = ink_pred(px, 55, 200, 250, 276, lambda c: 175 < c[0] < 218 and c[1] > 185)
    a["t_settings"] = ink_pred(px, 55, 200, 314, 342, lambda c: 175 < c[0] < 218 and c[1] > 185)
    a["t_prows"] = ink_pred(px, 30, 195, 762, 786, lambda c: abs(c[0] - 35) > 45 or abs(c[1] - 57) > 45)
    a["t_members"] = ink_pred(px, 30, 195, 795, 820, lambda c: abs(c[0] - 35) > 45 or abs(c[1] - 57) > 45)
    a["t_manage"] = ink_pred(px, 30, 195, 820, 855, lambda c: abs(c[0] - 35) > 45 or abs(c[1] - 57) > 45)
    a["t_button"] = ink_pred(px, 1200, 1390, 48, 86, lambda c: c[0] > 240 and c[1] > 240)
    a["t_k1_label"] = ink(px, 275, 400, 155, 176, 150)
    a["t_k1_value"] = ink(px, 275, 450, 195, 232, 150)
    a["t_k1_change"] = ink(px, 275, 400, 242, 262, 180)
    a["t_k2_label"] = ink(px, 660, 760, 155, 176, 150)
    a["t_k2_value"] = ink(px, 660, 760, 195, 232, 150)
    a["t_k3_label"] = ink(px, 1045, 1200, 155, 176, 150)
    a["t_k3_value"] = ink(px, 1045, 1200, 195, 232, 150)
    a["t_k3_change"] = ink(px, 1045, 1200, 242, 262, 180)
    a["t_chart_title"] = ink(px, 280, 500, 330, 358, 150)
    a["t_aprsep"] = ink(px, 880, 990, 330, 358, 180)
    a["t_unit"] = ink(px, 280, 370, 370, 392, 180)
    for lbl, (y0, y1) in {"120": (395, 410), "90": (432, 446), "60": (468, 482),
                          "30": (504, 518), "0": (540, 554)}.items():
        a[f"t_tick_{lbl}"] = ink(px, 290, 330, y0, y1, 180)
    a["t_act_title"] = ink(px, 1045, 1260, 330, 360, 150)
    for i, (y0, y1) in enumerate([(390, 415), (450, 475), (510, 535)], 1):
        a[f"t_act_name{i}"] = ink(px, 1070, 1260, y0, y1, 150)
        a[f"t_act_time{i}"] = ink(px, 1070, 1200, (418, 438), 180) if False else ink(px, 1070, 1200, y0 + 28, y1 + 28, 180)
    a["t_table_title"] = ink(px, 280, 500, 640, 670, 150)
    for lbl, (x0, x1) in {"PROJECT": (290, 400), "OWNER": (775, 850), "STATUS": (1025, 1110),
                          "DUE": (1225, 1290)}.items():
        a[f"t_hdr_{lbl}"] = ink(px, x0, x1, 695, 712, 150)
    for i, (y0, y1) in enumerate([(730, 755), (765, 790), (800, 825)], 1):
        a[f"t_proj{i}"] = ink(px, 295, 500, y0, y1, 150)
        a[f"t_owner{i}"] = ink(px, 775, 900, y0, y1, 150)
        a[f"t_due{i}"] = ink(px, 1225, 1300, y0, y1, 150)
    for i, (y0, y1) in enumerate([(732, 754), (767, 789), (802, 824)], 1):
        a[f"t_pill{i}"] = ink(px, 1060, 1145, y0, y1, 180)
    return a


A["ref"] = measure(rp)
A["rec"] = measure(cp)

print("== 全量锚点对比 ==")
bad = 0
for k in A["ref"]:
    rv, cv = A["ref"][k], A["rec"][k]
    if rv is None or cv is None:
        print(f"{k:18s} MISSING ref={rv} rec={cv}")
        bad += 1
        continue
    if isinstance(rv, (int, float)):
        e = cv - rv
        flag = "" if abs(e) <= 8 else "  <<<"
        if abs(e) > 8:
            bad += 1
        print(f"{k:18s} ref={rv} rec={cv} err={e:+}{flag}")
    elif isinstance(rv, tuple) and len(rv) == 2:
        e = (cv[0] - rv[0], cv[1] - rv[1])
        flag = "" if max(abs(e[0]), abs(e[1])) <= 8 else "  <<<"
        if max(abs(e[0]), abs(e[1])) > 8:
            bad += 1
        print(f"{k:18s} ref={rv} rec={cv} err={e}{flag}")
    else:
        errs = [cv[i] - rv[i] for i in range(len(rv))]
        flag = "" if max(abs(e) for e in errs) <= 8 else "  <<<"
        if max(abs(e) for e in errs) > 8:
            bad += 1
        print(f"{k:18s} ref={rv} rec={cv} err={['%+d' % e for e in errs]}{flag}")
print("超出 ±8 的锚点数:", bad)
json.dump(A, open('tmp/run-20261013-174209/A15/anchor-compare-v4.json', 'w'), indent=1)
