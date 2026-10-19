# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = 'tmp/20261016T164020-m1/A06/build_a06.py'
t = open(p, encoding='utf-8').read()
old = '''    fit("节点" + nid, lab, 22, NW - 28)
    S.append(text(cx - NW/2 + 22, cy + 4, lab, 22, INK, family=FAM_MIX, bold=True))'''
new = '''    fit("节点" + nid, lab, 22, NW - 28)
    S.append(text(cx - NW/2 + 22, cy + 4, lab, 22, INK, family=FAM_MIX, bold=True))

# =====================================================================
# 先决边（实线 + 箭头；弯折绕行避免压字）
# =====================================================================
EDGE_COL = "#6B7A93"
EDGE_PX = []

def port_r(nid):
    b = NODE_BOX[nid]
    return (b[2], (b[1] + b[3]) / 2)

def port_l(nid):
    b = NODE_BOX[nid]
    return (b[0], (b[1] + b[3]) / 2)

def port_t(nid):
    b = NODE_BOX[nid]
    return ((b[0] + b[2]) / 2, b[1])

def port_b(nid):
    b = NODE_BOX[nid]
    return ((b[0] + b[2]) / 2, b[3])

def seg_pts(points, color, thick=3.0):
    out = []
    for i in range(len(points) - 1):
        q = quad(points[i], points[i + 1], color, thick)
        if q:
            out.append(q)
    return out

# 每条边布局：straight = 右中→左中；up/down = 右中→拱形→左中；top/bottom = 出 ports 绕行
BEND_EDGES = {
    ("N04", "N13"): "bottom",
    ("N03", "N06"): "up",
}
for (a, b), mode in [(e, BEND_EDGES.get(e, "straight")) for e in SOLID]:
    if mode == "straight":
        p1, p2 = port_r(a), port_l(b)
        pts = [p1, p2]
        d = "R"
        tip = p2
    elif mode == "up":
        # 右中→上拱→左中（从上排跨到不同层）
        p1, p2 = port_r(a), port_l(b)
        midy = min(p1[1], p2[1]) - 64
        pts = [p1, (p1[0] + (p2[0]-p1[0]) * 0.5, p1[1]), (p1[0] + (p2[0]-p1[0]) * 0.5, midy),
               (p1[0] + (p2[0]-p1[0]) * 0.5, p2[1]), p2]
        d = "R"
        tip = p2
    elif mode == "down":
        p1, p2 = port_r(a), port_l(b)
        midy = max(p1[1], p2[1]) + 64
        pts = [p1, ((p1[0]+p2[0])/2, p1[1]), ((p1[0]+p2[0])/2, midy),
               ((p1[0]+p2[0])/2, p2[1]), p2]
        d = "R"
        tip = p2
    elif mode == "bottom":
        # 从底缘出，走卡底通道再上入目标底缘或右缘
        p1 = port_b(a)
        p2 = port_l(b)
        channel = GY + GH - 24      # 卡底通道 y
        p1c = (p1[0], p1[1] + 16)
        pts = [p1, p1c, (p1c[0], channel), (p2[0] - 26, channel), (p2[0] - 26, p2[1]), p2]
        d = "R"
        tip = p2
    for q in seg_pts(pts, EDGE_COL):
        S.append(q)
    S.append(arrowhead(tip[0] + 9 if d == "R" else tip[0], tip[1], d, EDGE_COL))
    EDGE_PX.append({"from": a, "to": b, "polyline": [[round(x,2), round(y,2)] for x, y in pts],
                    "arrow": [round(tip[0], 2), round(tip[1], 2)]})'''
assert t.count(old) == 1
open(p, 'w', encoding='utf-8').write(t.replace(old, new))
print('patched3')
