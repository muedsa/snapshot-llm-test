# -*- coding: utf-8 -*-
"""A15 侧栏精测：Overview 加粗字芯、Projects 行字形盒与导航点色。"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
STEPS = "tmp/20261016T164020-m1/A15/steps"

def measure(path):
    im = Image.open(path).convert("RGB")
    px = im.load()
    out = {}
    def bbox(x0_, y0_, x1_, y1_, pred):
        bx0, by0, bx1, by1 = None, None, None, None
        n = 0
        for y in range(y0_, y1_):
            for x in range(x0_, x1_):
                if pred(*px[x, y]):
                    bx0 = x if bx0 is None else min(bx0, x)
                    bx1 = x if bx1 is None else max(bx1, x)
                    by0 = y if by0 is None else min(by0, y)
                    by1 = y if by1 is None else max(by1, y)
                    n += 1
        return [bx0, by0, bx1, by1, n]
    white = lambda r, g, b: r > 215 and g > 225 and b > 235
    out["overview_bbox"] = bbox(58, 115, 200, 162, white)
    grayish = lambda r, g, b: 110 <= r <= 200 and 125 <= g <= 215 and 150 <= b <= 230
    out["projects_bbox"] = bbox(58, 175, 215, 225, grayish)
    out["analytics_bbox"] = bbox(58, 238, 215, 290, grayish)
    out["northstar_bbox"] = bbox(60, 28, 215, 62, white)
    # 导航点:首行(Projects)y带内 x30..48 最亮点
    best = None
    for y in range(192, 212):
        for x in range(28, 50):
            r, g, b = px[x, y]
            if r + g + b > (px[10, 400][0] + px[10, 400][1] + px[10, 400][2]) + 60:
                best = (x, y, "#%02X%02X%02X" % (r, g, b))
    out["dot_sample_row_project"] = best
    # 点包围盒
    dd = bbox(28, 188, 52, 216, lambda r, g, b: r > 60 and g > 75 and b > 110)
    out["project_dot_bbox"] = dd
    # 选中点
    gd = bbox(28, 125, 52, 150, lambda r, g, b: g > 140 and g - r > 40)
    out["active_dot_bbox"] = gd
    return out

ref = measure("tasks/A15-reference-reconstruction/inputs/reference.png")
mine = measure("outputs/20261016T164020-m1/A15/reconstructed.png")
json.dump({"ref": ref, "mine": mine}, open(os.path.join(STEPS, "nav-diff.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in ref:
    print(k, "| REF", ref[k], "| MINE", mine[k])
