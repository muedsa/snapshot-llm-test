# -*- coding: utf-8 -*-
"""B06 case-05 · 「0 手续费」的真实成本 — 分期现金流解剖

Problem: 结算页写「0 手续费 / 每期仅 89.33 元」，用户看不到真实的年化成本。
Redesign: 把 12 期现金流摊开：每期还款恒定，但剩余本金逐期下降，而手续费
始终按原始本金 1000 元计。于是同一笔 6.00 元手续费占当期余额的比例从
0.60% 涨到 7.20%，真实年化(IRR)被现金流直接求解出来。

数据边界: 本金 1000 元、12 期、每期名义费率 0.60% 均为自拟演示数据。
IRR 由二分法对真实现金流求根，不是估算、也不是 0.60%×12 的换算。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, emit, seg, text, tw_slot

W, H = 780, 1688
BG = "#0C1A22"
PANEL = "#112A35"
BORD = "#1E4557"
INK = "#E8F3FB"
MUT = "#6E93A8"
FAINT = "#4E6E88"
AMBER = "#F2A93B"
RED = "#FF6B4A"
TEAL = "#4FD1C5"
PRIN = "#2F6FA8"
L = 46
CW = W - 2 * L
CML, CMR = L + 24, L + CW - 24
INNER = CMR - CML

# ---------------- demo data -------------------------------------------------
PRINCIPAL, N, FEE_RATE = 1000.0, 12, 0.006      # 每期费率按原始本金计
FEE_EACH = PRINCIPAL * FEE_RATE                 # 6.00
PRIN_EACH = PRINCIPAL / N                       # 83.333...
PAY_EACH = PRIN_EACH + FEE_EACH                 # 89.333...
FEES_TOTAL = FEE_EACH * N                       # 72.00
TOTAL = PAY_EACH * N                            # 1072.00


def balance(t):
    """剩余本金（期初）：第 t 期开始时还欠多少。"""
    return PRINCIPAL - t * PRIN_EACH


def pv(r):
    return sum(PAY_EACH / (1.0 + r) ** t for t in range(1, N + 1))


# ---------------- IRR by bisection on the real cash flow (C1) --------------
lo, hi = 0.0, 1.0
assert pv(lo) > PRINCIPAL > pv(hi), "IRR 求根区间不成立"
for _ in range(300):
    mid = (lo + hi) / 2.0
    if pv(mid) > PRINCIPAL:
        lo = mid
    else:
        hi = mid
IRR_M = (lo + hi) / 2.0
IRR_A = (1.0 + IRR_M) ** N - 1.0
NOMINAL_A = FEE_RATE * N
GAP_PP = (IRR_A - NOMINAL_A) * 100.0

# ---------------- assertions ------------------------------------------------
# C1 nominal and actual both stated; IRR is solved, not converted
assert abs(pv(IRR_M) - PRINCIPAL) < 1e-9, "IRR 未收敛到现金流等式"
assert abs(IRR_M - 0.010877) < 5e-4, "月 IRR 异常: %.6f" % IRR_M
assert abs(NOMINAL_A - 0.072) < 1e-12
assert IRR_A > NOMINAL_A > 0, "实际年化应高于名义年化"
assert IRR_M > FEE_RATE, "月 IRR 应高于名义月费率"
assert 0.13 < IRR_A < 0.14, "实际年化 %.4f 超出预期区间" % IRR_A

# C2 cash flow every period, balance strictly decreasing
bals = [balance(t) for t in range(N)]
assert bals[0] == PRINCIPAL and abs(bals[-1] - PRIN_EACH) < 1e-9
assert all(bals[i] > bals[i + 1] for i in range(N - 1)), "余额未逐期递减"
assert all(abs(bals[i] - (PRINCIPAL - i * PRIN_EACH)) < 1e-9 for i in range(N))
assert abs(bals[1] - 916.67) < 0.01

# C3 total = principal + fees = sum of the periods
assert abs(TOTAL - (PRINCIPAL + FEES_TOTAL)) < 1e-9, "总还款分解不成立"
assert abs(sum(PAY_EACH for _ in range(N)) - TOTAL) < 1e-9
assert abs(FEES_TOTAL - FEE_EACH * N) < 1e-9 and abs(FEES_TOTAL - 72.0) < 1e-9
assert abs(TOTAL - 1072.0) < 1e-9
# the displayed 2-dp figures must still reconcile, with the tail absorbing it
disp_pay, disp_prin = round(PAY_EACH, 2), round(PRIN_EACH, 2)
assert abs(disp_pay * (N - 1) + round(TOTAL - disp_pay * (N - 1), 2)
           - TOTAL) < 1e-9
assert abs(disp_prin * (N - 1) + (PRINCIPAL - disp_prin * (N - 1))
           - PRINCIPAL) < 1e-9
TAIL_PAY = round(TOTAL - disp_pay * (N - 1), 2)
TAIL_PRIN = round(PRINCIPAL - disp_prin * (N - 1), 2)

# C4 lump-sum difference is explicit and comparable
DIFF = round(TOTAL - PRINCIPAL, 2)
assert abs(DIFF - 72.0) < 1e-9
assert abs(DIFF / PRINCIPAL * 100 - 7.20) < 1e-9

# the ratio the redesign is built on
r_first = FEE_EACH / bals[0]
r_last = FEE_EACH / bals[-1]
assert abs(r_first - FEE_RATE) < 1e-12
assert abs(r_last - 0.072) < 1e-12
assert abs(r_last / r_first - N) < 1e-9, "期末/期初费率比应恰为 12 倍"

print("IRR 月=%.6f 年化(复利)=%.4f%% 名义年化=%.2f%% 差=%.2fpp"
      % (IRR_M, IRR_A * 100, NOMINAL_A * 100, GAP_PP))
print("总还款=%.2f 本金=%.2f 手续费=%.2f 差额=%.2f 末期本金尾差=%.2f"
      % (TOTAL, PRINCIPAL, FEES_TOTAL, DIFF, TAIL_PRIN))

B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(text(L, 38, 240, 40, "09:42", 27, INK, bold=True, font="Inter"))
B.append(box(640, 44, 26, 17, INK, radius=3))
B.append(box(672, 40, 15, 24, INK, radius=2))
B.append(box(696, 38, 40, 28, INK, radius=6))
B.append(box(737, 45, 4, 14, INK, radius=2))
B.append(text(L, 90, 660, 54, "「0 手续费」的真实成本", 40, INK, bold=True))
B.append(text(L, 148, 640, 34, "12 期分期现金流解剖 · 演示数据", 22, MUT))

# ---------------- P1 rate ladder -------------------------------------------
PY, PH = 210, 270
B.append(box(L, PY, CW, PH, PANEL, radius=18, border=BORD, border_w=2))
B.append(text(CML, PY + 16, 560, 34, "同一笔分期的三个费率", 25, INK, bold=True))

SCALE1 = 40.0                      # px per percentage point
RATES = [
    ("名义月费率（按原始本金计）", FEE_RATE * 100, "0.60% / 月", "#3C6E86", 20),
    ("名义年化 = 月费率 × 12 期", NOMINAL_A * 100, "7.20% / 年", "#4FD1C5", 22),
    ("实际年化 IRR（现金流求解）", IRR_A * 100, "%.2f%% / 年" % (IRR_A * 100),
     AMBER, 30),
]
ry = PY + 58
for lab, v, val, col, vs in RATES:
    B.append(text(CML, ry, 420, 30, lab, 20, MUT))
    B.append(text(CMR - 220, ry - 4, 220, 36, val, vs, col, bold=True,
                  align="RIGHT", font="Inter"))
    B.append(box(CML, ry + 34, v * SCALE1, 18, col, radius=9))
    ry += 60
B.append(text(CML, ry - 4, INNER, 28,
              "实际年化比名义年化高 %.2f 个百分点" % GAP_PP, 19, AMBER, bold=True))
assert ry + 24 < PY + PH, "P1 越界"

# ---------------- P2 cash flow ---------------------------------------------
QY, QH = 494, 412
B.append(box(L, QY, CW, QH, PANEL, radius=18, border=BORD, border_w=2))
B.append(text(CML, QY + 12, 640, 34,
              "每期还的一样多，欠的一样少", 24, INK, bold=True))

PX0, PW_ = 118.0, 588.0
PITCH = PW_ / N                 # 49
CWD = 34.0


def cx(i):
    return PX0 + i * PITCH + (PITCH - CWD) / 2.0


AB_BOT, AB_MAX = QY + 196, 112.0          # 剩余本金 bars
BB_BOT, BB_MAX = QY + 372, 120.0          # 每期还款 bars
S_A = AB_MAX / PRINCIPAL
S_B = BB_MAX / PAY_EACH

B.append(text(CML, QY + 50, 300, 28, "剩余本金（期初，元）", 18, TEAL, bold=True))
for i in range(N):
    hgt = bals[i] * S_A
    # period 1 and period 12 are the two rows the ratio panel compares
    B.append(box(cx(i), AB_BOT - hgt, CWD, hgt,
                 TEAL if i in (0, N - 1) else "#2F7A80", radius=4))
B.append(seg(PX0, AB_BOT, PX0 + PW_, AB_BOT, 2, "#22505F"))

B.append(text(CML, QY + 214, 420, 28, "每期还款 89.33 元（本金 + 手续费）", 18, INK,
              bold=True))
for i in range(N):
    ph = PRIN_EACH * S_B
    fh = FEE_EACH * S_B
    B.append(box(cx(i), BB_BOT - ph, CWD, ph, PRIN, radius=3))
    B.append(box(cx(i), BB_BOT - ph - fh, CWD, fh, AMBER, radius=3))
B.append(seg(PX0, BB_BOT, PX0 + PW_, BB_BOT, 2, "#22505F"))

# x labels: only first / last, to keep the row readable
B.append(text(cx(0) - 20, BB_BOT + 8, 80, 24, "1 期", 16, MUT, align="CENTER"))
B.append(text(cx(N - 1) - 20, BB_BOT + 8, 80, 24, "12 期", 16, MUT,
              align="CENTER"))
B.append(text(550, QY + 214, 160, 28, "末期 89.37 补尾差", 15, FAINT, align="RIGHT"))
assert BB_BOT + 32 < QY + QH, "P2 越界"

# ---------------- P3 the ratio that explains it ----------------------------
RY, RH = 920, 220
B.append(box(L, RY, CW, RH, PANEL, radius=18, border=BORD, border_w=2))
B.append(text(CML, RY + 14, 640, 34, "同样的 6.00 元，占比差 12 倍", 24, INK,
              bold=True))
SCALE3 = 560.0 / (r_last * 100)
for k, (lab, bal, rr) in enumerate([
        ("第 1 期", bals[0], r_first), ("第 12 期", bals[-1], r_last)]):
    y = RY + 62 + k * 74
    B.append(text(CML, y, 400, 28, "%s · 剩余本金 %.2f 元" % (lab, bal), 19, MUT))
    B.append(text(CMR - 160, y - 4, 160, 34, "%.2f%%" % (rr * 100), 24,
                  TEAL if k == 0 else RED, bold=True, align="RIGHT", font="Inter"))
    B.append(box(CML, y + 32, rr * 100 * SCALE3, 16,
                 TEAL if k == 0 else RED, radius=8))
assert RY + 62 + 74 + 48 < RY + RH, "P3 越界"

# ---------------- P4 totals vs lump sum ------------------------------------
TY_, TH = 1154, 230
B.append(box(L, TY_, CW, TH, PANEL, radius=18, border=BORD, border_w=2))
B.append(text(CML, TY_ + 14, 640, 34, "总还款 = 本金 + 手续费", 24, INK, bold=True))
B.append(text(CML, TY_ + 52, 640, 28,
              "%.2f = %.2f + %.2f（6.00 × 12 期）" % (TOTAL, PRINCIPAL, FEES_TOTAL),
              19, MUT, font="Inter"))
SCALE4 = 560.0 / TOTAL
for k, (lab, val, col) in enumerate([("一次性付清", PRINCIPAL, "#3C6E86"),
                                     ("分期 12 期总还款", TOTAL, AMBER)]):
    y = TY_ + 88 + k * 60
    B.append(text(CML, y, 400, 28, lab, 19, MUT))
    B.append(text(CMR - 200, y - 4, 200, 34, "%.2f 元" % val, 22, col, bold=True,
                  align="RIGHT", font="Inter"))
    B.append(box(CML, y + 30, val * SCALE4, 16, col, radius=8))
B.append(text(CML, TY_ + 200, 640, 28,
              "差额 +%.2f 元（本金的 %.2f%%）" % (DIFF, DIFF / PRINCIPAL * 100),
              20, RED, bold=True))
assert TY_ + 228 <= TY_ + TH, "P4 越界"

# ---------------- P5 method / boundaries -----------------------------------
NY, NH = 1398, 222
B.append(box(L, NY, CW, NH, "#0E2A33", radius=18, border="#2F6E7E", border_w=2))
B.append(box(L, NY, 6, NH, "#2F6E7E", radius=3))
B.append(text(CML, NY + 12, 620, 32, "算法与边界", 23, "#7FD3C6", bold=True))
NOTES = [
    "· 实际年化由 12 期真实现金流二分法求解 IRR 得到：月 %.3f%%" % (IRR_M * 100),
    "· 年化 = (1+月IRR)^12 − 1 = %.2f%%；名义 %.2f%% 未随余额下降"
    % (IRR_A * 100, NOMINAL_A * 100),
    "· 每期名义费率 %.2f%% 按原始本金 1000 元计，故每期 6.00 元不变"
    % (FEE_RATE * 100),
    "· 演示边界：本金 1000 元、12 期、费率 0.60% 为自拟演示数据，",
    "  不指向任何真实商品或金融机构的分期方案",
]
for k, n in enumerate(NOTES):
    assert tw_slot(n, 19) <= INNER, "P5 line too wide: %s" % n
    B.append(text(CML, NY + 52 + k * 32, INNER, 30, n, 19, "#DDEBF3"))

foot = "演示数据 · 分期成本以实际合同与年化披露为准 · 0 手续费 ≠ 0 成本"
assert tw_slot(foot, 18) <= INNER, "footer too wide"
B.append(text(L, NY + NH + 12, CW, 40, foot, 18, FAINT))

end = NY + NH + 12 + 40
assert end <= H, "内容超出画布: %d > %d" % (end, H)
print("layout ends at %d / %d  (%d px spare)" % (end, H, H - end))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-05-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-05 %s written" % VER)
