"""A16 · compute the trustworthy numbers from source.csv and build the corrected report.

Every bar is drawn from the CSV value through one shared linear scale with a common zero
baseline. Nothing about the flawed PNG is reused except the findings it produced.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A16")
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from dslkit import Doc  # noqa: E402

W, H = 1280, 900
CJK = "Noto Sans CJK SC"
NUM = "Inter"

C_PAGE = "#F3F6FB"
C_CARD = "#FFFFFF"
C_BORDER = "#E2E8F1"
C_INK = "#0F172A"
C_BODY = "#3A4A63"
C_MUTED = "#63748F"
C_GRID = "#E2E8F1"
C_ZERO = "#94A3B8"
C_REV = "#245CE4"
C_COST = "#D97706"
C_HILITE = "#FFF7ED"
C_HILITE_BORDER = "#F5D8A8"
C_TEAL = "#0E9F8F"


def load() -> list:
    p = os.path.join(ROOT, "tasks", "A16-visual-data-forensics", "inputs", "source.csv")
    with open(p, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [dict(q=r["quarter"], rev=int(r["revenue_wan"]), cost=int(r["cost_wan"]))
            for r in rows]


def compute(rows: list) -> dict:
    for i, r in enumerate(rows):
        r["profit"] = r["rev"] - r["cost"]
        r["margin"] = r["profit"] / r["rev"]
        r["rev_qoq"] = None if i == 0 else (r["rev"] - rows[i - 1]["rev"]) / rows[i - 1]["rev"]
        r["cost_qoq"] = None if i == 0 else (r["cost"] - rows[i - 1]["cost"]) / rows[i - 1]["cost"]
        r["profit_qoq"] = None if i == 0 else (r["profit"] - rows[i - 1]["profit"]) / rows[i - 1]["profit"]
    tot_rev = sum(r["rev"] for r in rows)
    tot_cost = sum(r["cost"] for r in rows)
    tot_profit = sum(r["profit"] for r in rows)
    best = max(rows, key=lambda r: r["profit"])
    worst = min(rows, key=lambda r: r["profit"])
    best_margin = max(rows, key=lambda r: r["margin"])
    return dict(quarters=rows, total=dict(rev=tot_rev, cost=tot_cost, profit=tot_profit,
                                          margin=tot_profit / tot_rev),
                best_profit=best["q"], worst_profit=worst["q"],
                best_margin=best_margin["q"])


def esc(s: str) -> str:
    return f"<![CDATA[{s}]]>" if "<" in s else s


def T(d, x, y, s, size, color, weight="NORMAL", family=CJK, w=None,
      align="CENTER_LEFT", spacing=None):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    if spacing:
        a += f' letterSpacing="{spacing}"'
    body = esc(str(s))
    if w:
        d.raw(f'<Positioned left="{x}" top="{y}" width="{w}">'
              f'<Container alignment="{align}"><Text {a}>{body}</Text>'
              f'</Container></Positioned>')
    else:
        d.raw(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


def ty(ink_top, size, k=0.245):
    return round(ink_top - k * size)


def pct(v, nd=1):
    return f"{v * 100:.{nd}f}%"


def signed(v, nd=1):
    return f"{'+' if v >= 0 else '−'}{abs(v) * 100:.{nd}f}%"


# ------------------------------------------------------------------ geometry
CHART = dict(x=56, y=150, w=1168, h=450)
PLOT_L, PLOT_R = 170, 1192
AXIS_MAX, TICK = 200, 50
ZERO_Y, TOP_Y = 540, 250                     # 0 -> 540, 200 -> 250
PX_PER_UNIT = (ZERO_Y - TOP_Y) / AXIS_MAX    # 1.45
BAR_W, BAR_GAP = 76, 10
GROUP_W = (PLOT_R - PLOT_L) / 4

PROFIT = dict(x=56, y=620, w=700, h=210)
OBS = dict(x=772, y=620, w=452, h=210)
P_ZERO, P_MAX = 796, 66
P_PX_PER_UNIT = (P_ZERO - 690) / P_MAX        # 106 px for 60 万元


def build() -> tuple:
    rows = load()
    calc = compute(rows)
    d = Doc(W, H, background=C_PAGE)

    # ============================================================= header
    T(d, 56, ty(40, 32), "季度复盘：Q4 利润 54 万元居首，Q2 增收未增利", 32, C_INK, "BOLD")
    T(d, 56, ty(92, 22),
      "全年收入 563 万元 · 成本 420 万元 · 利润 143 万元 · 整体利润率 25.4%", 22, C_BODY)

    # ============================================================= chart card
    cx, cy, cw, ch = CHART["x"], CHART["y"], CHART["w"], CHART["h"]
    d.box(cx, cy, cw, ch, C_CARD, radius=14, border=f"1 SOLID {C_BORDER}")
    T(d, cx + 32, ty(178, 24), "收入与成本对比", 24, C_INK, "BOLD")
    T(d, cx + 32, ty(214, 18), "单位：万元　·　零起点共同基线", 18, C_MUTED)
    # legend (colours labelled the right way round, unlike the flawed version)
    d.box(1000, 182, 16, 16, C_REV, radius=3)
    T(d, 1024, ty(180, 20), "收入", 20, C_BODY)
    d.box(1110, 182, 16, 16, C_COST, radius=3)
    T(d, 1134, ty(180, 20), "成本", 20, C_BODY)

    # gridlines + tick labels
    for t in range(0, AXIS_MAX + 1, TICK):
        gy = round(ZERO_Y - t * PX_PER_UNIT)
        d.box(PLOT_L, gy, PLOT_R - PLOT_L, 2 if t == 0 else 1,
              C_ZERO if t == 0 else C_GRID)
        T(d, 0, ty(gy - 9, 18), str(t), 18, C_MUTED, family=NUM, w=PLOT_L - 16,
          align="CENTER_RIGHT")

    bars = []
    for i, r in enumerate(rows):
        centre = PLOT_L + GROUP_W * (i + 0.5)
        for j, (val, col, series) in enumerate(((r["rev"], C_REV, "revenue"),
                                                (r["cost"], C_COST, "cost"))):
            bx = round(centre - (BAR_W * 2 + BAR_GAP) / 2 + j * (BAR_W + BAR_GAP))
            bh = val * PX_PER_UNIT
            by = round(ZERO_Y - bh)
            d.box(bx, by, BAR_W, round(bh), col, radius=3)
            T(d, bx - 16, ty(by - 30, 20), str(val), 20, C_INK, "BOLD", family=NUM,
              w=BAR_W + 32, align="CENTER")
            bars.append(dict(quarter=r["q"], series=series, value=val, x=bx, w=BAR_W,
                             top=by, bottom=ZERO_Y, height=round(bh, 1)))
        T(d, round(centre - GROUP_W / 2), ty(556, 22), r["q"], 22, C_INK, "BOLD",
          w=round(GROUP_W), align="CENTER")

    # ============================================================= profit card
    px_, py_, pw_, ph_ = PROFIT["x"], PROFIT["y"], PROFIT["w"], PROFIT["h"]
    d.box(px_, py_, pw_, ph_, C_CARD, radius=14, border=f"1 SOLID {C_BORDER}")
    T(d, px_ + 32, ty(642, 24), "利润明细", 24, C_INK, "BOLD")
    T(d, px_ + 160, ty(646, 18), "（柱高=利润，单位：万元；标签=季度 · 利润率）", 18, C_MUTED)
    d.box(px_ + 32, P_ZERO + 1, pw_ - 64, 1, C_ZERO)
    profit_bars = []
    slot = (pw_ - 96) / 4
    for i, r in enumerate(rows):
        bx = round(px_ + 48 + slot * i + (slot - 96) / 2)
        bh = r["profit"] * P_PX_PER_UNIT
        by = round(P_ZERO - bh)
        col = C_TEAL if r["q"] == calc["best_profit"] else "#94A3B8"
        d.box(bx, by, 96, round(bh), col, radius=3)
        T(d, bx - 12, ty(by - 28, 20), str(r["profit"]), 20, C_INK, "BOLD", family=NUM,
          w=120, align="CENTER")
        T(d, bx - 12, ty(804, 18), f'{r["q"]} · {pct(r["margin"])}', 18, C_MUTED,
          w=120, align="CENTER")
        profit_bars.append(dict(quarter=r["q"], value=r["profit"], x=bx, w=96, top=by,
                                height=round(bh, 1), margin=r["margin"],
                                highlighted=r["q"] == calc["best_profit"]))

    # ============================================================= observation card
    ox, oy, ow, oh = OBS["x"], OBS["y"], OBS["w"], OBS["h"]
    d.box(ox, oy, ow, oh, C_HILITE, radius=14, border=f"1 SOLID {C_HILITE_BORDER}")
    T(d, ox + 32, ty(642, 24), "重点观察 · Q4", 24, "#B45309", "BOLD")
    for k, line in enumerate([
            "Q4 利润 54 万元、利润率 30.0%，",
            "两项均为四季最高。",
            "Q2 收入 +12.5%、成本 +20.0%，",
            "利润降至 27 万元，是唯一下滑季度。"]):
        T(d, ox + 32, ty(684 + k * 32, 22), line, 22, C_BODY)

    # ============================================================= footer
    T(d, 56, ty(858, 18),
      "数据来源 source.csv（四季收入/成本，单位万元）· 所有柱高按同一线性比例绘制，"
      "基线为 0 · 原图问题见 findings.json", 18, C_MUTED)

    plan = dict(canvas=[W, H], bars=bars, profit_bars=profit_bars,
                axis=dict(value_min=0, value_max=AXIS_MAX, tick_step=TICK,
                          zero_line_y=ZERO_Y, top_line_y=TOP_Y,
                          px_per_unit=PX_PER_UNIT,
                          plot_box=[PLOT_L, TOP_Y, PLOT_R, ZERO_Y],
                          bar_width=BAR_W, bar_gap=BAR_GAP,
                          group_width=GROUP_W),
                profit_axis=dict(value_min=0, value_max=P_MAX, zero_line_y=P_ZERO,
                                 px_per_unit=P_PX_PER_UNIT),
                calc=calc)
    return d.finish(), plan


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    text, plan = build()
    os.makedirs(os.path.join(TMP, "dsl"), exist_ok=True)
    p = os.path.join(TMP, "dsl", f"corrected-report.{version}.snapshot")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    json.dump(plan, open(os.path.join(TMP, f"plan.{version}.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    n = len(re.findall(r"<[A-Za-z]", text))
    print(f"wrote {p}: {len(text)} chars, {n} elements (cap 4096)")
