# -*- coding: utf-8 -*-
"""Pixel-verify case-05 installment cash-flow geometry (criteria C2..C5).

  C2  the balance bars must strictly decrease and be proportional to the
      outstanding principal of each period; every payment column must be the
      same height with the same principal/fee split
  C3  the total bar must equal principal + fees (1000 + 72 = 1072)
  C4  the lump-sum and installment totals must be directly comparable, i.e.
      their bar widths must have the ratio 1000 : 1072
  C5  every geometric bar must be proportional to the number printed beside it
      (rate ladder, ratio panel, totals panel)
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "..", "drafts", "case-05-v2.png")

W, H = 780, 1688
CML = 70
PRINCIPAL, N, FEE_RATE = 1000.0, 12, 0.006
FEE_EACH = PRINCIPAL * FEE_RATE                 # 6.00
PRIN_EACH = PRINCIPAL / N                       # 83.333...
PAY_EACH = PRIN_EACH + FEE_EACH                 # 89.333...
TOTAL = PAY_EACH * N                            # 1072.00
bals = [PRINCIPAL - t * PRIN_EACH for t in range(N)]


def solve_irr():
    def pv(r):
        return sum(PAY_EACH / (1.0 + r) ** t for t in range(1, N + 1))
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2.0
        if pv(mid) > PRINCIPAL:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


IRR_M = solve_irr()
IRR_A = (1.0 + IRR_M) ** N - 1.0
NOMINAL_A = FEE_RATE * N

# panel geometry, mirrored from case05.py
PY = 210
QY = 494
RY = 920
TY_ = 1154
AB_BOT = QY + 196                      # 690
BB_BOT = QY + 372                      # 866
AB_MAX, BB_MAX = 112.0, 120.0
S_A = AB_MAX / PRINCIPAL
S_B = BB_MAX / PAY_EACH
SCALE1 = 40.0                          # px per percentage point
SCALE3 = 560.0 / (FEE_EACH / bals[-1] * 100)
SCALE4 = 560.0 / TOTAL
PITCH = 588.0 / N


def cx(i):
    return 118.0 + i * PITCH + (PITCH - 34.0) / 2.0


BG_PANEL = (17, 42, 53)

im = Image.open(PNG).convert("RGB")
assert im.size == (W, H), im.size


def px(x, y):
    return im.getpixel((int(x), int(y)))


def close(c, want, tol=30):
    return all(abs(c[i] - want[i]) <= tol for i in range(3))


def hrun(y, want, x0, x1, tol=30, minlen=4):
    xs = [x for x in range(x0, x1) if close(px(x, y), want, tol)]
    if not xs or xs[-1] - xs[0] < minlen:
        return None
    # longest contiguous run (bars are single-colour)
    best, st = None, None
    for x in range(x0, x1):
        if close(px(x, y), want, tol):
            if st is None:
                st = x
        else:
            if st is not None and (best is None or x - st > best[1] - best[0]):
                best = (st, x - 1)
            st = None
    if st is not None and (best is None or x1 - st > best[1] - best[0]):
        best = (st, x1 - 1)
    return best if best and best[1] - best[0] >= minlen else None


# ---- C5: rate ladder bars proportional to the printed rates ----------------
RATES = [("月", FEE_RATE * 100, (60, 110, 134), 302),
         ("年", NOMINAL_A * 100, (79, 209, 197), 362),
         ("年", IRR_A * 100, (242, 169, 59), 422)]
got = []
for i, (u, v, col, y) in enumerate(RATES):
    r = hrun(y + 9, col, CML, 730)
    assert r, "rate bar %d not found at y=%d" % (i, y)
    got.append(r[1] - r[0] + 1)
    exp = v * SCALE1
    print("  rate %-3s %-7s w=%3d  expect %.1f  (px/pp 40)" % (u, "%.2f%%" % v,
                                                               r[1] - r[0] + 1, exp))
    assert abs((r[1] - r[0] + 1) - exp) <= 4, "rate bar %d not proportional" % i
print("    nominal/month = %.2f (expect 12.00)  IRR/nominal = %.4f (expect %.4f)"
      % (got[1] / float(got[0]), got[2] / float(got[1]), IRR_A / NOMINAL_A))
assert abs(got[1] / float(got[0]) - 12.0) < 0.15
assert abs(got[2] / float(got[1]) - IRR_A / NOMINAL_A) < 0.03

# ---- C2: balance bars strictly decreasing, proportional to balance ---------
heights = []
for i in range(N):
    x = cx(i) + 17.0
    top = None
    for y in range(574, AB_BOT + 2):        # 574 = below the sub-chart caption
        r, g, b = px(x, y)
        if g >= 100 and b >= 90 and r < 150:
            top = y
            break
    assert top is not None, "balance bar %d missing" % (i + 1)
    heights.append(AB_BOT - top)
    exp = bals[i] * S_A
    assert abs(heights[-1] - exp) <= 4, "balance bar %d h=%d expect %.1f" % (
        i + 1, heights[-1], exp)
assert all(heights[i] > heights[i + 1] for i in range(N - 1)), "余额未逐期递减"
print("  balance heights:", heights)
# zero-intercept least-squares fit: heights == k * balance
kb = sum(bals)
slope = (sum(heights[i] * bals[i] for i in range(N)) /
         sum(b * b for b in bals))
intercept = sum(heights) / float(N) - slope * kb / float(N)
print("    proportional fit: k=%.6f (expect %.6f)  intercept=%.2f px"
      % (slope, S_A, intercept))
assert abs(slope - S_A) < 0.01, "余额柱与金额不成正比"
assert abs(intercept) < 4.0, "余额柱存在非零截距"
assert abs(heights[0] / float(heights[6]) - bals[0] / bals[6]) < 0.12

# ---- C2: payment columns identical, principal/fee split constant -----------
pcols, fcols = [], []
for i in range(N):
    x = cx(i) + 17.0
    # the fee cap sits ABOVE the principal column, so find amber first
    ftop = next((y for y in range(700, BB_BOT)
                 if close(px(x, y), (242, 169, 59), 34)), None)
    assert ftop is not None, "payment column %d: fee cap missing" % i
    ptop = next((y for y in range(ftop, BB_BOT)
                 if close(px(x, y), (47, 111, 168), 34)), None)
    assert ptop is not None, "payment column %d: principal missing" % i
    pcols.append(BB_BOT - ptop)
    fcols.append(ptop - ftop)
    assert ftop < ptop, "fee must sit above principal"
exp_p, exp_f = PRIN_EACH * S_B, FEE_EACH * S_B
print("  payment cols: principal h=%d (expect %.1f)  fee h=%d (expect %.1f)"
      % (pcols[0], exp_p, fcols[0], exp_f))
assert max(pcols) - min(pcols) <= 3, "每期本金高度不一致"
assert max(fcols) - min(fcols) <= 3, "每期手续费高度不一致"
assert abs(pcols[0] - exp_p) <= 4 and abs(fcols[0] - exp_f) <= 4
assert abs((pcols[0] + fcols[0]) - BB_MAX) <= 4
tot = [pcols[i] + fcols[i] for i in range(N)]
assert max(tot) - min(tot) <= 3, "每期还款不等高"

# ---- C5: ratio panel (0.60% vs 7.20%) -------------------------------------
r0 = hrun(1022, (79, 209, 197), CML, 730, tol=40)
r1b = hrun(1096, (255, 107, 74), CML, 730, tol=40)
assert r0 and r1b, "ratio panel bars not found"
w1, w2 = r0[1] - r0[0] + 1, r1b[1] - r1b[0] + 1
print("  ratio bars: %.2f%% w=%d (expect %.1f)   7.20%% w=%d (expect %.1f)"
      % (FEE_EACH / bals[0] * 100, w1, 0.6 * SCALE3, w2, 7.2 * SCALE3))
assert abs(w1 - 0.6 * SCALE3) <= 5 and abs(w2 - 7.2 * SCALE3) <= 5
assert abs(w2 / float(w1) - 12.0) < 0.4, "占比条非 12 倍"

# ---- C3/C4: totals bars, 1000 : 1072 --------------------------------------
a = hrun(1280, (60, 110, 134), CML, 730, tol=26)
b = hrun(1340, (242, 169, 59), CML, 730, tol=30)
assert a and b, "totals bars not found"
wa, wb = a[1] - a[0] + 1, b[1] - b[0] + 1
print("  totals: lump-sum w=%d (expect %.1f)   installment w=%d (expect %.1f)"
      % (wa, PRINCIPAL * SCALE4, wb, TOTAL * SCALE4))
assert abs(wa - PRINCIPAL * SCALE4) <= 5
assert abs(wb - TOTAL * SCALE4) <= 5
assert abs(wb / float(wa) - TOTAL / PRINCIPAL) < 0.006, "C4 两期口径不可比"
# C3 decomposition, in bar terms
assert abs(wb - wa - FEE_EACH * N * SCALE4) < 6, "C3 手续费段不成比例"

# ---- C3: numeric reconciliation ------------------------------------------
assert abs(TOTAL - (PRINCIPAL + FEE_EACH * N)) < 1e-9
assert abs(TOTAL - 1072.0) < 1e-9
assert abs((TOTAL - PRINCIPAL) / PRINCIPAL * 100 - 7.20) < 1e-9
pv_at_irr = sum(PAY_EACH / (1.0 + IRR_M) ** t for t in range(1, N + 1))
assert abs(pv_at_irr - PRINCIPAL) < 1e-9, "IRR 与现金流不符"

print("\nIRR monthly %.6f%%  effective annual %.4f%%  nominal %.2f%%"
      % (IRR_M * 100, IRR_A * 100, NOMINAL_A * 100))
print("ALL CASE-05 GEOMETRY / RECONCILIATION CHECKS PASSED")
