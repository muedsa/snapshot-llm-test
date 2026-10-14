"""A22 - the 1600x1000 cockpit, drawn from the computed numbers only.

One layout map drives all three rounds: the four region boundaries (header, conclusion,
KPI row, chart card, table card, footer) are constants here, so a later round can only
change what is *inside* them. Every bar height, tick, table cell and headline figure is
read from data.py's unrounded values; nothing is typed by hand.

Run:  python tmp/<run_id>/A22/dash.py --round 1 [--no-ink]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "A22"))

from snap import C, Node, Positioned, Snapshot, Stack, num  # noqa: E402
import data as D  # noqa: E402

SANS, MONO = "Noto Sans CJK SC", "Noto Sans Mono CJK SC"
CJK_EM, LATIN_EM, LINE_H = 1.0, 0.62, 1.46

P = {"bg": "#F4F6FB", "card": "#FFFFFF", "card_line": "#E1E7F2", "stripe": "#F8FAFD",
     "ink": "#14213D", "ink2": "#3A4A6B", "ink3": "#64748B",
     "net": "#1B4FBF", "profit": "#C97415", "loss": "#C97415",
     "grid": "#E6EBF5", "zero": "#94A3B8", "accent": "#1B4FBF", "chip": "#E7ECF8"}

# --- fixed region boundaries (x0, y0, x1, y1); rounds may not move these by >2px ---
REGIONS = {
    "header": (48, 40, 1552, 110),
    "conclusion": (48, 116, 1552, 238),
    "kpi_row": (48, 250, 1552, 370),
    "chart": (48, 386, 940, 922),
    "table": (964, 386, 1552, 922),
    "footer": (48, 938, 1552, 970),
}
KPI_W = 358
KPI_GAP = (1552 - 48 - 4 * KPI_W) / 3
PLOT = (148, 480, 916, 862)          # inside the chart card
TABLE_HEAD = (988, 462, 1528, 500)
TABLE_ROWS_Y = 504
ROW_H = 52
COLS = [("month", 96, "left"), ("net", 124, "right"), ("profit", 100, "right"),
        ("refund_rate", 110, "right"), ("conversion_rate", 110, "right")]
AXIS_STEP_WAN = 4
HEAD_W = 1552 - 48 - 26 - 24          # usable width inside the conclusion band


WIDE = {"%": 0.90}      # measured in Noto Sans CJK SC at 22px: 19px ink, i.e. 0.86em


def tw(t, size, mono=False):
    """Conservative advance width: measured CJK = 1.0em, proportional Latin = 0.62em
    (with the few glyphs measured wider listed in WIDE), monospaced Latin = 0.50em
    (the real figure is 0.486em)."""
    if mono:
        return sum(size * (CJK_EM if ord(c) > 0x2E80 else 0.52) for c in t)
    return sum(size * (CJK_EM if ord(c) > 0x2E80 else WIDE.get(c, LATIN_EM))
               for c in t)


def tokens(text):
    """Digits/punctuation runs stay atomic so a number never breaks across lines;
    CJK characters break individually."""
    out, cur = [], ""
    for ch in text:
        if ch.isascii() and not ch.isspace():
            cur += ch
        else:
            if cur:
                out.append(cur)
                cur = ""
            out.append(ch)
    if cur:
        out.append(cur)
    return out


def wrap(text, size, width):
    """Pack at "；" boundaries when they fit, so a headline never breaks in the middle
    of a clause; fall back to character-level packing for anything still too long."""
    parts = text.split("；")
    segs = [p + "；" for p in parts[:-1]] + [parts[-1]]
    rows, cur = [], ""
    for sg in segs:
        if tw(sg, size) > width:                      # clause alone is too long
            for ln in wrap_chars(sg, size, width):
                if cur and tw(cur, size) + tw(ln, size) <= width:
                    cur += ln
                else:
                    if cur:
                        rows.append(cur)
                    cur = ln
            continue
        if cur and tw(cur, size) + tw(sg, size) > width:
            rows.append(cur.rstrip())
            cur = sg
        else:
            cur += sg
    if cur.strip():
        rows.append(cur.rstrip())
    return rows


def wrap_chars(text, size, width):
    rows, cur = [], ""
    for tk in tokens(text):
        if cur and tw(cur, size) + tw(tk, size) > width:
            if not tk.strip():
                rows.append(cur.rstrip())
                cur = ""
                continue
            rows.append(cur.rstrip())
            cur = tk.lstrip()
        else:
            cur += tk
    if cur.strip():
        rows.append(cur.rstrip())
    return rows


class Sheet:
    def __init__(self, no_ink=False):
        self.no_ink = no_ink
        self.nodes = [C(width=1600, height=1000, color=P["bg"])]
        self.items = []

    def text(self, role, t, x, y, size, colour, *, font=SANS, bold=False, align="left",
             box_w=None):
        w = tw(t, size, mono=(font == MONO))
        if align == "right":
            x = x - w
        elif align == "center":
            x = x - w / 2
        h = size * 1.06
        if box_w is not None:
            w = box_w
        a = {"fontSize": num(size), "color": colour, "fontFamily": font}
        if bold:
            a["fontStyle"] = "BOLD"
        if not self.no_ink:
            self.nodes.append(Positioned(Node("Text", a, [], t), left=num(x),
                                         top=num(y), width=num(max(w, 1))))
        self.items.append({"role": role, "text": t, "box": [round(x, 2), round(y, 2),
                                                            round(x + w, 2),
                                                            round(y + h, 2)],
                           "font_size": size, "colour": colour, "font": font,
                           "bold": bold, "align": align})
        return y + size * LINE_H

    def rect(self, x, y, w, h, colour, *, radius=None, shape=None):
        a = {"width": num(w), "height": num(h), "color": colour}
        if radius is not None:
            a["borderRadius"] = num(radius)
        if shape:
            a["shape"] = shape
        self.nodes.append(Positioned(C(**a), left=num(x), top=num(y)))

    def card(self, key, *, title=None, subtitle=None):
        x0, y0, x1, y1 = REGIONS[key]
        self.rect(x0, y0, x1 - x0, y1 - y0, P["card"], radius=10)
        if title:
            self.text(f"{key}_title", title, x0 + 24, y0 + 18, 24, P["ink"], bold=True)
        if subtitle:
            self.text(f"{key}_sub", subtitle, x0 + 24, y0 + 48, 22, P["ink3"])

    def finish(self):
        return Snapshot(Stack(C(width=1600, height=1000), *self.nodes),
                        background=P["bg"], type="png")


def axis_range(d):
    vals = []
    for m in d["months"]:
        vals += [m["net_revenue"], m["operating_profit"]]
    hi_wan = max(vals) / 10000.0
    lo_wan = min(min(vals) / 10000.0, 0)
    step = AXIS_STEP_WAN
    hi = int(-(-hi_wan // step)) * step
    lo = int(lo_wan // step) * step
    if hi <= hi_wan:                       # never let a bar touch the top frame
        hi += step
    return lo, hi, step


def build(rnd, no_ink=False):
    d = D.compute(rnd)
    c = D.conclusions(rnd, d)
    s = Sheet(no_ink)
    t = d["totals"]

    # ---- header -------------------------------------------------------------
    s.text("title", "叠光经营驾驶舱", 48, 44, 34, P["ink"], bold=True)
    s.text("period", f"{t['summed_from'][0]} — {t['summed_from'][-1]} · "
                     f"{t['months']} 个月 · 金额单位：元（KPI 另标万元）",
           48, 86, 22, P["ink3"])
    s.text("stamp", "数据源 inputs/monthly.csv · 比率由分子/分母直接相除",
           1552, 86, 22, P["ink3"], align="right", font=MONO)

    # ---- conclusion band ----------------------------------------------------
    x0, y0, x1, y1 = REGIONS["conclusion"]
    s.rect(x0, y0, x1 - x0, y1 - y0, P["chip"], radius=10)
    s.rect(x0, y0, 6, y1 - y0, P["accent"], radius=3)
    head = wrap(c["headline"], 24, HEAD_W)
    assert len(head) <= 2, f"headline needs {len(head)} lines"
    y = y0 + 8
    for ln in head:
        s.text("conclusion_head", ln, x0 + 26, y, 24, P["ink"], bold=True)
        y += 24 * LINE_H
    sub = wrap(c["sub"], 22, HEAD_W)
    assert len(sub) == 1, f"sub-line wrapped to {len(sub)}"
    s.text("conclusion_sub", sub[0], x0 + 26, y + 2, 22, P["ink2"])

    # ---- KPI cards ----------------------------------------------------------
    kpis = [
        ("总净收入", t["display"]["net_revenue_wan"], "万元",
         f"{t['gross_revenue']:,} − {t['refund_amount']:,} 元"),
        ("总经营利润", t["display"]["operating_profit_wan"], "万元",
         f"占净收入 {t['display']['profit_share_pct']}%（先求和）"),
        ("总订单", t["display"]["orders"], "笔",
         f"同期访问 {t['display']['sessions']} 次"),
        ("总体转化率", t["display"]["overall_conversion_rate_pct"], "%",
         f"{t['orders']:,} / {t['sessions']:,}（笔/次）"),
    ]
    for i, (label, value, unit, sub) in enumerate(kpis):
        cx = 48 + i * (KPI_W + KPI_GAP)
        cy0, cy1 = REGIONS["kpi_row"][1], REGIONS["kpi_row"][3]
        s.rect(cx, cy0, KPI_W, cy1 - cy0, P["card"], radius=10)
        s.rect(cx, cy0, KPI_W, 4, P["accent"] if i < 2 else "#7C93B8", radius=2)
        s.text("kpi_label", label, cx + 20, cy0 + 14, 22, P["ink3"])
        s.text("kpi_value", value, cx + 20, cy0 + 42, 38, P["ink"], bold=True, font=MONO)
        s.text("kpi_unit", unit, cx + 20 + tw(value, 38, mono=True) + 8, cy0 + 54, 22,
               P["ink2"])
        s.text("kpi_sub", sub, cx + 20, cy0 + 92, 22, P["ink2"])
        assert tw(sub, 22) <= KPI_W - 36, f"KPI sub too wide: {sub}"

    # ---- chart --------------------------------------------------------------
    cx0, cy0, cx1, cy1 = REGIONS["chart"]
    lo, hi, step = axis_range(d)
    sub = (f"纵轴单位：万元 · 刻度步长 {AXIS_STEP_WAN} 万元 · "
           f"轴范围 {lo} ~ {hi} 万元")
    assert 72 + tw(sub, 22) <= cx1 - 24, f"chart subtitle too wide: {sub}"
    s.card("chart", title="月度净收入 / 经营利润（零起点柱图）", subtitle=sub)
    # legend, right aligned on the card title line
    lx = cx1 - 24 - tw("经营利润", 22)
    s.text("legend_profit", "经营利润", lx, cy0 + 20, 22, P["ink2"])
    s.rect(lx - 22, cy0 + 22, 16, 16, P["profit"], radius=3)
    lx2 = lx - 22 - 16 - tw("净收入", 22)
    s.text("legend_net", "净收入", lx2, cy0 + 20, 22, P["ink2"])
    s.rect(lx2 - 22, cy0 + 22, 16, 16, P["net"], radius=3)
    px0, py0, px1, py1 = PLOT
    span = hi - lo
    pw, ph = px1 - px0, py1 - py0

    def y_of(v_wan):
        return py1 - (v_wan - lo) / span * ph

    v = lo
    while v <= hi + 1e-9:
        yy = y_of(v)
        s.rect(px0, yy - 0.5, pw, 1, P["grid"] if v != 0 else P["zero"])
        s.text("axis_tick", f"{v:g}", px0 - 12, yy - 11, 22, P["ink3"],
               align="right", font=MONO)
        v += step
    zero_y = y_of(0)
    s.rect(px0 - 1, py0, 1, ph, P["zero"])
    s.rect(px0, zero_y - 1, pw, 2, P["zero"])

    n = len(d["months"])
    pitch = pw / n
    bar_w = min(46.0, pitch * 0.36)
    gap = 10.0
    labels = []
    for i, m in enumerate(d["months"]):
        gcx = px0 + pitch * (i + 0.5)
        for j, (key, colour) in enumerate((("net_revenue", P["net"]),
                                           ("operating_profit", P["profit"]))):
            val_wan = m[key] / 10000.0
            x = gcx - bar_w - gap / 2 + j * (bar_w + gap)
            yv = y_of(val_wan)
            top, hgt = (min(zero_y, yv), abs(zero_y - yv))
            s.rect(x, top, bar_w, max(hgt, 1), colour, radius=3)
            lab = m["display"][f"{key}_wan"]
            ly = (top - 30) if val_wan >= 0 else (top + hgt + 6)
            labels.append((m["month"], key, lab, x + bar_w / 2, ly))
        s.text("axis_month", m["month"], gcx, py1 + 12, 22, P["ink2"],
               align="center", font=MONO)
    for month, key, lab, cx, cy in labels:
        colour = P["net"] if key == "net_revenue" else P["profit"]
        s.text("bar_value", lab, cx, cy, 22, colour, align="center", font=MONO)

    # ---- table --------------------------------------------------------------
    tx0, ty0, tx1, ty1 = REGIONS["table"]
    s.card("table", title="月度明细", subtitle="净收入/利润单位：元 · 比率单位：%")
    hx0, hy0, hx1, hy1 = TABLE_HEAD
    heads = {"month": "月份", "net": "净收入", "profit": "利润",
             "refund_rate": "退款率", "conversion_rate": "转化率"}
    s.rect(hx0 - 12, hy0, (hx1 + 12) - (hx0 - 12), hy1 - hy0, P["chip"], radius=6)
    x = hx0
    for key, w, al in COLS:
        s.text("th", heads[key], x + (w - 8 if al == "right" else 4), hy0 + 8, 22,
               P["ink"], bold=True, align="right" if al == "right" else "left")
        x += w
    y = TABLE_ROWS_Y
    for i, m in enumerate(d["months"]):
        if i % 2:
            s.rect(hx0 - 12, y, (hx1 + 12) - (hx0 - 12), ROW_H, P["stripe"])
        vals = {"month": m["month"], "net": m["display"]["net_revenue_yuan"],
                "profit": m["display"]["operating_profit_yuan"],
                "refund_rate": m["display"]["refund_rate_pct"],
                "conversion_rate": m["display"]["conversion_rate_pct"]}
        x = hx0
        for key, w, al in COLS:
            colour = P["ink"]
            if key == "profit" and m["operating_profit"] < 0:
                colour = "#B3261E"
            s.text("td", vals[key], x + (w - 8 if al == "right" else 4), y + 13, 22,
                   colour, align="right" if al == "right" else "left",
                   font=SANS if key == "month" else MONO, bold=key == "month")
            x += w
        s.rect(hx0 - 12, y + ROW_H - 1, (hx1 + 12) - (hx0 - 12), 1, P["card_line"])
        y += ROW_H
    note = (f"合计：净收入 {t['display']['net_revenue_yuan']} · "
            f"利润 {t['display']['operating_profit_yuan']} 元")
    s.text("table_note", note, hx1, ty1 - 44, 22, P["ink2"], align="right")
    assert 976 + tw(note, 22) <= hx1, f"table note too wide: {note}"

    # ---- footer -------------------------------------------------------------
    fx0, fy0, fx1, fy1 = REGIONS["footer"]
    s.rect(fx0, fy0 - 8, fx1 - fx0, 1, P["card_line"])
    s.text("footer", "公式：净收入=收入−退款 · 利润=净收入−成本 · 退款率=退款/收入 · "
                     "转化率=订单/访问", fx0, fy0, 22, P["ink3"])
    s.text("footer_right", f"round-0{rnd} · 展示按十进制四舍五入（半值进位）",
           fx1, fy0, 22, P["ink3"], align="right")
    return s, d, c, {"axis": [lo, hi, step], "plot": list(PLOT),
                    "row_h": ROW_H, "months": n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument("--no-ink", action="store_true")
    a = ap.parse_args()
    TMP = ROOT / "tmp" / RUN / "A22"
    s, d, c, meta = build(a.round, a.no_ink)
    stem = f"r{a.round:02d}-dashboard" + ("-noink" if a.no_ink else "")
    (TMP / f"{stem}.snapshot").write_text(s.finish().render() + "\n", encoding="utf-8")
    if a.no_ink:
        print(json.dumps({"written": stem}, ensure_ascii=False))
        return 0
    json.dump({"items": s.items, "computed": d, "conclusion": c, "meta": meta},
              (TMP / f"r{a.round:02d}-built.json").open("w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ov = [(x["text"], y["text"]) for i, x in enumerate(s.items) for y in s.items[i + 1:]
          if not (x["box"][2] <= y["box"][0] or y["box"][2] <= x["box"][0]
                  or x["box"][3] <= y["box"][1] or y["box"][3] <= x["box"][1])]
    frame = (48, 40, 1552, 970)
    out = [i["text"] for i in s.items
           if i["box"][0] < frame[0] or i["box"][1] < frame[1]
           or i["box"][2] > frame[2] or i["box"][3] > frame[3]]
    print(json.dumps({"texts": len(s.items), "overlaps": ov[:12], "overlap_n": len(ov),
                      "outside_frame": out[:6],
                      "min_font": min(i["font_size"] for i in s.items),
                      "axis": meta["axis"], "months": meta["months"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
