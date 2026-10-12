"""A23 轨迹调参：在 6 个采样帧上搜索互不重叠的路径模型。

只做几何计算，不请求服务。所有坐标统一用"单元左上角"基准（与 gen_frames.py
一致；中心距与左上角距等价）。判定阈值随朝向变化：轴对齐 60px 方块中心距 60
即不相触，45° 菱形需要 60×√2≈84.9，因此要求 dmin ≥ 60 + 24.9×rot/45 + 4 余量。
"""
import itertools
import json
import math

FW = FH = 600.0
N = 12
SIZE = 60.0
RING_R = 250.0
PITCH, VPITCH = 72.0, 84.0
ROWS = [2, 4, 6]
FRAMES = 6
MARGIN = 4.0
ROT = 45.0


def targets():
    pts, top_y = [], (FH - ((len(ROWS) - 1) * VPITCH + SIZE)) / 2.0
    for ri, cnt in enumerate(ROWS):
        row_w = (cnt - 1) * PITCH + SIZE
        for ci in range(cnt):
            pts.append((FW / 2 - row_w / 2 + ci * PITCH, top_y + ri * VPITCH))
    return pts


def ring_angles():
    return [i * (360.0 / N) + 15 for i in range(N)]


def ring_starts():
    return [(FW / 2 + RING_R * math.cos(math.radians(a)) - SIZE / 2,
             FH / 2 + RING_R * math.sin(math.radians(a)) - SIZE / 2) for a in ring_angles()]


def smooth(t):
    return t * t * (3 - 2 * t)


def rot_of(t, settle):
    return ROT * (1.0 - smooth(min(1.0, t / settle)))


def pairings():
    """按格位极角排序的 12 种相位配对（把圆环第 i 点配到排序后第 (i+p)%12 格）。"""
    tg, cx, cy = targets(), FW / 2, FH / 2
    ang = [math.degrees(math.atan2(y + SIZE / 2 - cy, x + SIZE / 2 - cx)) % 360
           for x, y in tg]
    order = sorted(range(N), key=lambda i: ang[i])
    return {p: [tg[order[(i + p) % N]] for i in range(N)] for p in range(N)}


def pos(model, t, tg, settle, r_mid, stagger_max):
    st, out = ring_starts(), []
    lens = [math.dist(st[i], tg[i]) for i in range(N)]
    far = max(lens)
    for i in range(N):
        s = stagger_max * (1.0 - lens[i] / far)      # 行程短的晚出发
        u = max(0.0, min(1.0, (t - s) / max(0.2, 1.0 - s)))
        e = smooth(u)
        sx, sy = st[i]
        tx, ty = tg[i]
        if model == "linear":
            out.append((sx + (tx - sx) * e, sy + (ty - sy) * e))
        else:                                        # 两段：先收半径再入格
            mx = sx + (tx - sx) * 0.5
            my = sy + (ty - sy) * 0.5
            cx, cy = FW / 2 - SIZE / 2, FH / 2 - SIZE / 2
            dx, dy = mx - cx, my - cy
            d = math.hypot(dx, dy) or 1.0
            ix, iy = cx + dx / d * r_mid, cy + dy / d * r_mid
            if t <= 0.5:
                k = smooth(t / 0.5)
                out.append((sx + (ix - sx) * k, sy + (iy - sy) * k))
            else:
                k = smooth((t - 0.5) / 0.5)
                out.append((ix + (tx - ix) * k, iy + (ty - iy) * k))
    return out


def score(model, p, settle, r_mid, stagger_max):
    tg = pairings()[p]
    rows, ok = [], True
    for k in range(FRAMES):
        t = k / (FRAMES - 1)
        pts = pos(model, t, tg, settle, r_mid, stagger_max)
        rot = rot_of(t, settle)
        need = SIZE + 24.9 * rot / ROT + MARGIN
        dmin = min(math.dist(pts[i], pts[j])
                   for i in range(N) for j in range(i + 1, N))
        ext = (SIZE / 2) * (abs(math.cos(math.radians(rot)))
                            + abs(math.sin(math.radians(rot))))
        # pts 是左上角，旋转外接半径要从格心量起
        oob = sum(1 for x, y in pts if x + SIZE / 2 - ext < 0 or y + SIZE / 2 - ext < 0
                  or x + SIZE / 2 + ext > FW or y + SIZE / 2 + ext > FH)
        rows.append((round(dmin - need, 1), oob))
        if dmin < need or oob:
            ok = False
    return ok, min(r[0] for r in rows), rows


best = []
for model, p, settle, r_mid, sg in itertools.product(
        ("linear", "twophase"), range(N), (0.5, 1.0), (150.0, 175.0), (0.0, 0.15, 0.3)):
    if model == "linear" and r_mid != 150.0:
        continue                                     # r_mid 只作用于两段模型
    ok, margin, rows = score(model, p, settle, r_mid, sg)
    best.append((ok, margin, model, p, settle, r_mid if model == "twophase" else 0, sg, rows))
best.sort(key=lambda b: (not b[0], -b[1]))
for b in best[:10]:
    print("%-4s margin=%6.1f  %-9s phase=%2d settle=%.1f r_mid=%-5.1f stagger=%.2f  %s" % (
        "PASS" if b[0] else "fail", b[1], b[2], b[3], b[4], b[5], b[6],
        " ".join("%+.1f/%d" % (m, o) for m, o in b[7])))
print("通过配置数", sum(1 for b in best if b[0]), "/", len(best))
json.dump([[bool(x[0]), x[1], x[2], x[3], x[4], x[5], x[6]] for x in best],
          open("tmp/20261008T1615Z-run01/A23/tune_result.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
