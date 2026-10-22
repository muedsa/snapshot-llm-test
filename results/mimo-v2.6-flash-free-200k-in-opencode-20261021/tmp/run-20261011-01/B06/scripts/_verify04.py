# -*- coding: utf-8 -*-
"""Pixel-verify case-04 reference-interval strips (criteria C2 / C3).

For every item row the redesign claims:

  * the green band spans exactly the reference interval on a value-linear axis
  * the marker sits at the result's value-proportional position
  * a value outside the interval is NOT clamped back inside: it lands outside,
    and the coloured overshoot segment is proportional to the deviation
  * the printed lower/upper bound numerals sit under the band's own ends
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-04-v1.png")

ITEMS = [
    ("HGB", 130.0, 175.0, 118.0, 0, "low"),
    ("GLU", 3.9, 6.1, 5.8, 1, "ok"),
    ("TC", 2.8, 5.7, 5.9, 1, "high"),
    ("ALT", 9.0, 50.0, 46.0, 0, "ok"),
    ("UA", 208.0, 428.0, 486.0, 0, "high"),
    ("K", 3.5, 5.3, 3.3, 1, "low"),
    ("HbA1c", 4.0, 6.0, 5.6, 1, "ok"),
]
AXIS_PAD = 0.5
ROW0, PITCH = 464, 140
SX0, SW = 352.0, 470.0

BAND = (47, 143, 107)      # #2F8F6B
TRACK = (230, 227, 218)    # #E6E3DA
MARK = (27, 36, 32)        # #1B2420
LOWC = (37, 99, 235)       # #2563EB
HIGHC = (194, 65, 12)      # #C2410C

im = Image.open(PNG).convert("RGB")
assert im.size == (1240, 1754), im.size


def is_col(x, y, want, tol=34):
    p = im.getpixel((x, y))
    return all(abs(p[i] - want[i]) <= tol for i in range(3))


def run_at(y, want, x0=340, x1=860, tol=34, minlen=6):
    """longest contiguous run of `want` on row y"""
    best, st = None, None
    for x in range(x0, x1):
        if is_col(x, y, want, tol):
            if st is None:
                st = x
        else:
            if st is not None and (best is None or x - st > best[1] - best[0]):
                best = (st, x - 1)
            st = None
    if st is not None and (best is None or x1 - st > best[1] - best[0]):
        best = (st, x1 - 1)
    return best if best and best[1] - best[0] >= minlen else None


def span_at(y, want, x0=340, x1=860, tol=34, minlen=6):
    """outer extent of `want` on row y.

    The reference band is SPLIT by the marker whenever the result falls inside
    it, so the band's true extent is min..max of its pixels, not its longest
    contiguous run.
    """
    xs = [x for x in range(x0, x1) if is_col(x, y, want, tol)]
    if not xs or xs[-1] - xs[0] < minlen:
        return None
    return (xs[0], xs[-1])


def clusters(xs, gap=26):
    out, cur = [], [xs[0]]
    for v in xs[1:]:
        if v - cur[-1] > gap:
            out.append((cur[0], cur[-1]))
            cur = [v]
        else:
            cur.append(v)
    out.append((cur[0], cur[-1]))
    return out


def axis_of(lo, hi, res):
    span = hi - lo
    amin = max(0.0, lo - AXIS_PAD * span)
    amax = hi + AXIS_PAD * span
    pos = lambda v: (v - amin) / (amax - amin)
    return pos, SX0 + pos(lo) * SW, SX0 + pos(hi) * SW, SX0 + pos(res) * SW


worst = []
for i, (ab, lo, hi, res, dp, st) in enumerate(ITEMS):
    ry = ROW0 + i * PITCH
    ymid = ry + 69
    pos, e_lo, e_hi, e_res = axis_of(lo, hi, res)

    band = span_at(ymid, BAND)
    assert band, "%s: 绿色参考带未找到" % ab
    # ---- C2 band endpoints proportional to the interval bounds -----------
    assert abs(band[0] - e_lo) <= 4, "%s 带左缘 %d vs %.1f" % (ab, band[0], e_lo)
    assert abs(band[1] - e_hi) <= 4, "%s 带右缘 %d vs %.1f" % (ab, band[1], e_hi)

    # ---- C2 marker position --------------------------------------------
    mk = run_at(ymid, MARK, minlen=4)
    assert mk, "%s: 标记未找到" % ab
    mkx = (mk[0] + mk[1]) / 2.0
    assert abs(mkx - e_res) <= 5, "%s 标记 x=%.1f vs %.1f" % (ab, mkx, e_res)

    # ---- C3 overshoot: out-of-range results must land OUTSIDE the band ----
    over = None
    if st == "low":
        over = run_at(ymid, LOWC, x0=int(band[0]) - 260, x1=int(band[0]) + 6)
        assert over, "%s: 无偏低超出色段" % ab
        assert over[1] < band[0] + 6, "%s 低出段越入参考带" % ab
        assert abs((band[0] - over[0]) - (e_lo - e_res)) <= 6, \
            "%s 低出段长度 %.1f vs %.1f" % (ab, band[0] - over[0], e_lo - e_res)
    elif st == "high":
        over = run_at(ymid, HIGHC, x0=int(band[1]) - 6, x1=int(band[1]) + 300)
        assert over, "%s: 无偏高超出色段" % ab
        assert over[0] > band[1] - 6, "%s 高出段越入参考带" % ab
        assert abs((over[1] - band[1]) - (e_res - e_hi)) <= 6, \
            "%s 高出段长度 %.1f vs %.1f" % (ab, over[1] - band[1], e_res - e_hi)
    else:
        assert not run_at(ymid, LOWC) and not run_at(ymid, HIGHC), \
            "%s 正常项不应有超出色段" % ab

    # ---- printed bound numerals sit under the band's own ends ------------
    ly = ry + 100
    green = [x for x in range(340, 860) if is_col(x, ly, BAND, tol=40)]
    assert green, "%s: 界值数字未找到" % ab
    cl = clusters(green)
    assert len(cl) == 2, "%s 界值聚类异常: %s" % (ab, cl)
    llo, rhi = cl
    assert abs(llo[0] - e_lo) <= 8, "%s 下限数字左缘 %d vs %.1f" % (ab, llo[0], e_lo)
    assert abs(rhi[1] - e_hi) <= 8, "%s 上限数字右缘 %d vs %.1f" % (ab, rhi[1], e_hi)

    band_frac = (mkx - band[0]) / float(band[1] - band[0]) if band[1] > band[0] else 0
    val_frac = (res - lo) / float(hi - lo)
    print("  %-6s band %d..%d (exp %.1f..%.1f)  marker %.1f (exp %.1f)  "
          "over=%s  bounds %s..%s" %
          (ab, band[0], band[1], e_lo, e_hi, mkx, e_res,
           over if over else "none", llo, rhi))
    worst.append(abs(band_frac - val_frac))
    assert abs(band_frac - val_frac) < 0.02, \
        "%s 落点比例 %.4f vs %.4f" % (ab, band_frac, val_frac)

print("max |marker-proportion - value-proportion| = %.5f" % max(worst))
print("\nALL STRIP GEOMETRY CHECKS PASSED")
