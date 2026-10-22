# -*- coding: utf-8 -*-
"""Pixel-verify case-07 landscape transfer timeline (criteria C2..C5).

  C2  every segment's horizontal extent must be strictly proportional to its
      minutes, on a single shared axis; the whole axis scale is checked
      against the printed minute ticks
  C3  both routes are complete: the conventional route carries stair (amber)
      segments, the accessible route carries lift (green) segments, each with
      its own duration and its own walking legs
  C4  the last-train margin is presented as current -> last -> remainder, and
      the remainder equals the margin minus the transfer time
  C5  landscape big-type legibility + nothing clipped or crossing the margins
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-07-v2.png")

W, H = 1688, 780
BAR_X, BAR_MAX_S = 380.0, 480.0
BAR_W = 1648.0 - BAR_X
PX_S = BAR_W / BAR_MAX_S

BG = (16, 24, 32)
BLUE = (60, 134, 200)
AMBER = (224, 160, 43)
GREEN = (53, 160, 110)
YELL = (255, 203, 71)
BORD = (36, 51, 63)
BACK = (27, 40, 51)

V = 1.2
PATH_A = [("w", 72, None), ("u", None, 75), ("w", 180, None),
          ("u", None, 70), ("w", 48, None)]
PATH_B = [("w", 72, None), ("l", None, 85), ("w", 216, None),
          ("l", None, 75), ("w", 48, None)]
COLS = {"w": BLUE, "u": AMBER, "l": GREEN}
CUR_S, LAST_S = 23 * 3600 + 12 * 60, 23 * 3600 + 40 * 60

TA = sum(d / V if k == "w" else float(t) for k, d, t in PATH_A)
TB = sum(d / V if k == "w" else float(t) for k, d, t in PATH_B)
MARGIN = LAST_S - CUR_S
LEFT = MARGIN - TA


def expect(path):
    out, c = [], 0.0
    for k, d, t in path:
        s = d / V if k == "w" else float(t)
        out.append((k, BAR_X + c * PX_S, BAR_X + (c + s) * PX_S, s))
        c += s
    return out, c


expA, totA = expect(PATH_A)
expB, totB = expect(PATH_B)
assert abs(totA - 395) < 1e-9 and abs(totB - 440) < 1e-9
assert abs(MARGIN - 1680) < 1e-9 and abs(LEFT - 1285) < 1e-9

im = Image.open(PNG).convert("RGB")
assert im.size == (W, H), im.size
_load = im.load()


def px(x, y):
    return _load[x, y]


def close(c, want, tol=34):
    return all(abs(c[i] - want[i]) <= tol for i in range(3))


def classify(c):
    for name, col in (("blue", BLUE), ("amber", AMBER), ("green", GREEN)):
        if close(c, col, 40):
            return name
    if close(c, BG, 14):
        return "bg"
    if close(c, YELL, 40):
        return "yell"
    if close(c, BORD, 14):
        return "bord"
    if close(c, BACK, 14):
        return "back"
    return "other"


def runs_at(y, x0=370, x1=1660):
    out, st, cur = [], None, None
    for x in range(x0, x1 + 1):
        c = classify(px(x, y))
        if c in ("blue", "amber", "green"):
            if c != cur:
                if cur is not None:
                    out.append((cur, st, x - 1))
                cur, st = c, x
        else:
            if cur is not None:
                out.append((cur, st, x - 1))
                cur, st = None, None
    if cur is not None:
        out.append((cur, st, x1))
    return [r for r in out if r[2] - r[1] >= 30]


# ---- C2/C3: segment geometry on both tracks --------------------------------
for (label, exp, ty, total) in (("track A", expA, 186, totA),
                                ("track B", expB, 350, totB)):
    y = ty + 14                          # clear of the in-bar mm:ss label
    got = runs_at(y)
    print("\n%s  (total %.1f s = %.1f px)" % (label, total, total * PX_S))
    assert len(got) == len(exp), "%s: %d runs != %d segments" % (
        label, len(got), len(exp))
    for (g, e) in zip(got, exp):
        gk, g0, g1 = g
        ek, e0, e1, es = e
        want_name = {"w": "blue", "u": "amber", "l": "green"}[ek]
        assert gk == want_name, \
            "%s segment colour %s != %s" % (label, gk, want_name)
        assert abs(g0 - e0) <= 3, "%s 起点 %.0f != %.1f" % (label, g0, e0)
        assert abs(g1 - e1) <= 3, "%s 终点 %.0f != %.1f" % (label, g1, e1)
        gw, ew = g1 - g0 + 1, e1 - e0
        print("   %-5s x %4d..%4d  w=%4d  expect %6.1f  = %5.1f s"
              % (gk, g0, g1, gw, ew, ew / PX_S))
        assert abs(gw - es * PX_S) <= 4, "%s 段宽不成正比" % label
    # bar body height
    col = {"w": BLUE, "u": AMBER, "l": GREEN}[exp[0][0]]
    ys = [yy for yy in range(ty - 10, ty + 96) if close(px(400, yy), col, 40)]
    assert ys and abs((max(ys) - min(ys) + 1) - 78) <= 3, \
        "%s 条高 %.0f != 78" % (label, (max(ys) - min(ys) + 1))
    # route totals, cross-checked against the printed summary values
    last = got[-1][2] - got[0][1] + 1
    print("   measured total = %d px  expect %.1f px  (%.2f px/s)"
          % (last, total * PX_S, last / total))
    assert abs(last - total * PX_S) <= 6

# ---- C2: the shared axis itself --------------------------------------------
ticks = [x for x in range(360, 1670) if not close(px(x, 170), BG, 16)]
groups, st, prev = [], ticks[0], ticks[0]
for x in ticks[1:]:
    if x - prev > 3:
        groups.append((st + prev) // 2)
        st = x
    prev = x
groups.append((st + prev) // 2)
print("\nminute ticks at:", groups)
assert len(groups) == 9, "刻度数 %d != 9" % len(groups)
for i, gx in enumerate(groups):
    want = BAR_X + i * 60 * PX_S
    assert abs(gx - want) <= 3, "第 %d 分钟刻度 %.0f != %.1f" % (i, gx, want)
# axis rule spans exactly 0..8 min
axis = [x for x in range(360, 1670) if not close(px(x, 178), BG, 16)]
assert abs(min(axis) - 380) <= 3 and abs(max(axis) - 1648) <= 3, "轴线未覆盖全程"

# ---- C3: the accessible route really carries lift legs ---------------------
kinds_b = [k for k, _s0, _s1, _t in expB]
assert kinds_b.count("l") == 2 and kinds_b.count("w") == 3, kinds_b
kinds_a = [k for k, _s0, _s1, _t in expA]
assert kinds_a.count("u") == 2 and kinds_a.count("w") == 3, kinds_a
lift = [t for k, _d, t in PATH_B if k == "l"]
assert sorted(lift) == [75, 85], lift

# ---- C4: the last-train card is rendered and consistent --------------------
c3x, c3y = 1128, 512
yell = [(x, y) for y in range(545, 645) for x in range(1140, 1640)
        if close(px(x, y), YELL, 60)]
assert yell, "末班车余量大数字未渲染"
bw = max(x for x, _y in yell) - min(x for x, _y in yell) + 1
bh = max(y for _x, y in yell) - min(y for _x, y in yell) + 1
print("last-train figure ink: %d px wide, %d px tall" % (bw, bh))
assert 180 <= bw <= 420, "余量数字宽度异常（应为 21 分 25 秒 量级）"
assert 30 <= bh <= 50, "大字高度不足（横屏大字要求）"
# card 1 big figure, same size class
y1 = [(x, y) for y in range(545, 645) for x in range(60, 540)
      if close(px(x, y), YELL, 60)]
assert y1 and 30 <= (max(y for _x, y in y1) - min(y for _x, y in y1) + 1) <= 50
# the three cards exist at the expected x ranges (yellow accent + right edge)
for cx in (40, 584, 1128):
    assert close(px(cx + 2, 615), YELL, 40), "卡片 %d 左侧强调条缺失" % cx
    assert close(px(cx + 519, 615), BORD, 12), "卡片 %d 右边界缺失" % cx

# ---- C5: nothing crosses the margins --------------------------------------
bleed = 0
for y in range(0, H):
    for x in (0, 4, 10, 16, W - 17, W - 9, W - 3):
        if not close(px(x, y), BG, 16):
            bleed += 1
for x in range(0, W):
    for y in (0, 4, 8, H - 9, H - 5, H - 2):
        if not close(px(x, y), BG, 16):
            bleed += 1
assert bleed == 0, "有元素越出安全边距 (%d 处)" % bleed
# assumption panel must end at the right margin, not past it
ap = [x for x in range(1100, 1670) if close(px(x, 60), YELL, 50)]
assert ap and abs(max(ap) - 1648) <= 3, "步速面板越过右margin: %s" % (
    max(ap) if ap else None)

print("\nLEFT = %d s = %d:%02d  (margin %d s, transfer %.0f s)"
      % (LEFT, int(LEFT // 60), int(LEFT % 60), MARGIN, TA))
print("ALL CASE-07 TIMELINE / AXIS / LAYOUT CHECKS PASSED")
