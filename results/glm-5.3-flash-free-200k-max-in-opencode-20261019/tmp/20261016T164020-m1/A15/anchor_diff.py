# -*- coding: utf-8 -*-
"""A15 锚点差分：同一扫描逻辑应用于 reference 与 reconstruction，计算分量误差。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
STEPS = "tmp/20261016T164020-m1/A15/steps"

def measure(path):
    im = Image.open(path).convert("RGB")
    px = im.load()
    M = {}
    BG = (0xF3, 0xF6, 0xFB)
    def is_bg(r, g, b):
        return abs(r - BG[0]) < 7 and abs(g - BG[1]) < 7 and abs(b - BG[2]) < 7
    def is_white(r, g, b):
        return r > 248 and g > 248 and b > 252
    def is_blue(r, g, b):
        return 30 <= r <= 80 and 90 <= g <= 130 and 205 <= b <= 255
    def is_ink(r, g, b):
        return r < 70 and g < 80 and b < 100
    def is_grid(r, g, b):
        return 200 <= r <= 240 and 205 <= g <= 244 and 220 <= b <= 253 and not is_white(r, g, b)

    out = []
    for x in range(150, 320):
        if is_bg(*px[x, 450]):
            out.append(x)
            break
    M["sidebar_right"] = out[0] if out else None

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
    s1 = seg_on_col(300, 100, 320, is_white, 8)
    M["kpi1_y"] = [s1[0][0], s1[0][1]] if s1 else None
    def runs_on_row(y, x0, x1, pred, min_len=8):
        out, s = [], None
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
    k = runs_on_row(210, 230, 1440, is_white)
    if k:
        M["kpi1_x"] = [k[0][0], [r for r in k if r[0] < 620][-1][1]]
        M["kpi2_x"] = [[r for r in k if 620 < r[0] < 1010][0][0], [r for r in k if 620 < r[0] < 1010][-1][1]]
        M["kpi3_x"] = [[r for r in k if r[0] > 1010][0][0], k[-1][1]]
    cc = runs_on_row(450, 230, 1015, is_white)
    if cc:
        M["chart_x"] = [cc[0][0], cc[-1][1]]
    sb = seg_on_col(300, 280, 620, is_white, 8)
    M["chart_y"] = [sb[0][0], sb[-1][1]] if sb else None
    aa = runs_on_row(450, 1015, 1440, is_white)
    if aa:
        M["activity_x"] = [aa[0][0], aa[-1][1]]
    ac = seg_on_col(1330, 280, 620, is_white, 8)
    M["activity_y"] = [ac[0][0], ac[-1][1]] if ac else None
    tb = runs_on_row(680, 230, 1440, is_white)
    if tb:
        M["table_x"] = [tb[0][0], tb[-1][1]]
    tc = seg_on_col(700, 600, 880, is_white, 8)
    if tc:
        M["table_y"] = [tc[0][0], tc[-1][1]]
    grid_rows = []
    for y in range(390, 565):
        cnt = sum(1 for x in range(340, 960, 8) if is_grid(*px[x, y]))
        if cnt > 55:
            grid_rows.append(y)
    merged = []
    for y in grid_rows:
        if merged and y - merged[-1][-1] <= 2:
            merged[-1].append(y)
        else:
            merged.append([y])
    M["gridlines"] = [m[len(m) // 2] for m in merged]
    gx = runs_on_row(M["gridlines"][-1] if merged else 549, 250, 1010, is_grid, 2)
    M["zero_x"] = gx[0][0] if gx else None
    import itertools
    brs = [r for r in runs_on_row(520, 330, 1000, is_blue, 20)]
    M["bars"] = brs
    if brs:
        cxm = (brs[-1][0] + brs[-1][1]) // 2
        for y in range(395, 555):
            if is_blue(*px[cxm, y]):
                M["bar6_top"] = [cxm, y]
                break
    bb = [None, None, None, None]
    for y in range(30, 105):
        for x in range(1150, 1435):
            if is_blue(*px[x, y]):
                bb[0] = x if bb[0] is None else min(bb[0], x)
                bb[1] = y if bb[1] is None else min(bb[1], y)
                bb[2] = x if bb[2] is None else max(bb[2], x)
                bb[3] = y if bb[3] is None else max(bb[3], y)
    M["button"] = bb
    tx0, ty0 = None, None
    for y in range(20, 85):
        for x in range(240, 660):
            if is_ink(*px[x, y]):
                tx0 = x if tx0 is None else min(tx0, x)
                ty0 = y if ty0 is None else min(ty0, y)
    M["title_tl"] = [tx0, ty0]
    def pill(pred, y0, y1):
        x0, x1p, y0f, y1f = None, None, None, None
        for y in range(y0, y1):
            for x in range(1005, 1220):
                r, g, b = px[x, y]
                if pred(r, g, b) and not is_ink(r, g, b):
                    x0 = x if x0 is None else min(x0, x)
                    x1p = x if x1p is None else max(x1p, x)
                    y0f = y if y0f is None else min(y0f, y)
                    y1f = y if y1f is None else max(y1f, y)
        return [x0, y0f, x1p, y1f]
    def is_pale_blue(r, g, b):
        return 222 <= r <= 246 and 234 <= g <= 250 and 249 <= b <= 255
    def is_pale_green(r, g, b):
        return 200 <= r <= 232 and 236 <= g <= 252 and 212 <= b <= 242
    M["pill_done"] = pill(is_pale_green, 795, 838)
    # 导航选中 pill（#294467 附近）
    def is_pillbg(r, g, b):
        return 30 <= r <= 55 and 55 <= g <= 82 and 88 <= b <= 118
    nave = runs_on_row(140, 2, 218, is_pillbg, 10)
    navc = seg_on_col(100, 80, 210, is_pillbg, 10)
    M["nav_x"] = [nave[0][0], nave[0][1]] if nave else None
    M["nav_y"] = [navc[0][0], navc[0][1]] if navc else None
    return M

ref = measure("tasks/A15-reference-reconstruction/inputs/reference.png")
mine = measure("outputs/20261016T164020-m1/A15/reconstructed.png")
json.dump({"ref": ref, "mine": mine}, open(os.path.join(STEPS, "anchor-diff.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in sorted(set(ref) | set(mine)):
    rv, mv = ref.get(k), mine.get(k)
    print(k, "REF", rv, "| MINE", mv)
