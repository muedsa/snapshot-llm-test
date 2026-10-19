# -*- coding: utf-8 -*-
"""A15 v02 补测：nav pill 盒（row120/col30 避开文字）、标题字形全盒、PRO 颜色采样。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
STEPS = "tmp/20261016T164020-m1/A15/steps"

def measure(path):
    im = Image.open(path).convert("RGB")
    px = im.load()
    out = {}
    def is_pillbg(r, g, b):
        return 30 <= r <= 55 and 55 <= g <= 82 and 88 <= b <= 118
    def runs_on_row(y, x0, x1, pred, min_len=5):
        rr, s = [], None
        for x in range(x0, x1):
            ok = pred(*px[x, y])
            if ok and s is None:
                s = x
            elif not ok and s is not None:
                if x - s >= min_len:
                    rr.append((s, x - 1))
                s = None
        if s is not None and x1 - s >= min_len:
            rr.append((s, x1 - 1))
        return rr
    def seg_on_col(x, y0, y1, pred, min_len=5):
        rr, s = [], None
        for y in range(y0, y1):
            ok = pred(*px[x, y])
            if ok and s is None:
                s = y
            elif not ok and s is not None:
                if y - s >= min_len:
                    rr.append((s, y - 1))
                s = None
        if s is not None:
            rr.append((s, y1 - 1))
        return rr
    spills = runs_on_row(120, 5, 218, is_pillbg, 5)
    spv = seg_on_col(30, 80, 220, is_pillbg, 5)
    out["nav_pill_row120"] = spills
    out["nav_pill_col30"] = spv
    def is_ink(r, g, b):
        return r < 70 and g < 80 and b < 100
    tx0, tx1, ty0, ty1 = None, None, None, None
    for y in range(20, 85):
        for x in range(240, 700):
            if is_ink(*px[x, y]):
                tx0 = x if tx0 is None else min(tx0, x)
                tx1 = x if tx1 is None else max(tx1, x)
                ty0 = y if ty0 is None else min(ty0, y)
                ty1 = y if ty1 is None else max(ty1, y)
    out["title_bbox"] = [tx0, ty0, tx1, ty1]
    # 副标题字形盒
    def is_subink(r, g, b):
        return 100 <= r <= 170 and 105 <= g <= 175 and 120 <= b <= 200
    sx0, sx1, sy0, sy1 = None, None, None, None
    for y in range(78, 112):
        for x in range(250, 620):
            if is_subink(*px[x, y]):
                sx0 = x if sx0 is None else min(sx0, x)
                sx1 = x if sx1 is None else max(sx1, x)
                sy0 = y if sy0 is None else min(sy0, y)
                sy1 = y if sy1 is None else max(sy1, y)
    out["subtitle_bbox"] = [sx0, sy0, sx1, sy1]
    # PRO WORKSPACE 文字色（x40..160, 769..781 内 r<g 且 g>110 最高频）
    from collections import Counter
    cc = Counter()
    for yy in range(768, 782):
        for xx in range(40, 160):
            r, g, b = px[xx, yy]
            if g > 120 and g - r > 30:
                cc["#%02X%02X%02X" % (r, g, b)] += 1
    out["pro_teal_top"] = cc.most_common(4)
    # 活动点颜色(col 1054..1064 各带内主色)
    for nm, y0, y1 in ("amber", 395, 410), ("blue", 455, 470), ("green", 515, 530):
        c3 = Counter()
        for yy in range(y0, y1):
            for xx in range(1050, 1068):
                c3["#%02X%02X%02X" % px[xx, yy]] += 1
        out["dot_" + nm] = c3.most_common(3)
    # 关键小文字包围盒
    def bbox(x0_, y0_, x1_, y1_, pred):
        bx0, by0, bx1, by1 = None, None, None, None
        for y in range(y0_, y1_):
            for x in range(x0_, x1_):
                if pred(*px[x, y]):
                    bx0 = x if bx0 is None else min(bx0, x)
                    bx1 = x if bx1 is None else max(bx1, x)
                    by0 = y if by0 is None else min(by0, y)
                    by1 = y if by1 is None else max(by1, y)
        return [bx0, by0, bx1, by1]
    gr = lambda r, g, b: 100 <= r <= 175 and 105 <= g <= 180 and 120 <= b <= 205
    dk = lambda r, g, b: r < 70 and g < 80 and b < 100
    out["period_bbox"] = bbox(870, 328, 985, 360, gr)
    out["unit_bbox"] = bbox(280, 368, 380, 392, gr)
    out["kpi_label_bbox"] = bbox(280, 152, 400, 178, gr)
    out["kpi_change_bbox"] = bbox(280, 238, 380, 268, lambda r, g, b: r < 100 and g > 90 and g - r > 30 and b < 160)
    out["kpi_value_bbox"] = bbox(280, 188, 460, 240, dk)
    out["act_title1_bbox"] = bbox(1070, 388, 1230, 415, dk)
    out["act_time1_bbox"] = bbox(1070, 415, 1230, 442, gr)
    out["th_label_bbox"] = bbox(295, 694, 380, 716, lambda r, g, b: 80 <= r <= 120 and 90 <= g <= 130 and 120 <= b <= 165)
    out["row1_name_bbox"] = bbox(295, 728, 500, 756, dk)
    out["footer_bbox"] = bbox(255, 858, 560, 888, gr)
    out["month1_bbox"] = bbox(370, 556, 408, 580, gr)
    out["th_owner_bbox"] = bbox(760, 694, 850, 718, lambda r, g, b: 80 <= r <= 130 and 90 <= g <= 135 and 120 <= b <= 170)
    out["th_status_bbox"] = bbox(1015, 694, 1105, 718, lambda r, g, b: 80 <= r <= 130 and 90 <= g <= 135 and 120 <= b <= 170)
    out["th_due_bbox"] = bbox(1215, 694, 1285, 718, lambda r, g, b: 80 <= r <= 130 and 90 <= g <= 135 and 120 <= b <= 170)
    out["owner1_bbox"] = bbox(760, 726, 900, 758, lambda r, g, b: 120 <= r <= 200 and 130 <= g <= 210 and 140 <= b <= 220)
    out["due1_bbox"] = bbox(1215, 726, 1330, 758, lambda r, g, b: 120 <= r <= 200 and 130 <= g <= 210 and 140 <= b <= 220)
    out["pill_text_inpro"] = bbox(1040, 731, 1165, 754, lambda r, g, b: r < 120 and 120 <= g and b > 180)
    out["pill_text_review"] = bbox(1040, 766, 1165, 790, lambda r, g, b: 140 < r < 210 and 90 < g < 150 and b < 100)
    out["pill_text_done"] = bbox(1040, 800, 1165, 825, lambda r, g, b: r < 110 and g > 100 and g - r > 30)
    return out

ref = measure("tasks/A15-reference-reconstruction/inputs/reference.png")
mine = measure("outputs/20261016T164020-m1/A15/reconstructed.png")
json.dump({"ref": ref, "mine": mine}, open(os.path.join(STEPS, "sup-diff-v02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in ref:
    print(k, "| REF", ref[k], "| MINE", mine[k])
