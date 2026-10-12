"""A16 · verify the corrected report from its own pixels.

The point of the task is that bar height must encode the value, so this measures every
bar in the rendered PNG and checks that height/value is one constant, that every bar
starts on the same zero line, and that all copy sits inside the canvas.
"""
from __future__ import annotations

import csv
import json
import os
import sys

from PIL import Image

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A16")
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A16")

C_REV = (0x24, 0x5C, 0xE4)
C_COST = (0xD9, 0x77, 0x06)
C_HI = (0x0E, 0x9F, 0x8F)
C_GREY = (0x94, 0xA3, 0xB8)
C_PAGE = (0xF3, 0xF6, 0xFB)


def near(c, ref, tol=26):
    return all(abs(a - b) <= tol for a, b in zip(c[:3], ref))


def runs_x(px, y, pred, minw=8, x0=0, x1=1280):
    out, start = [], None
    for x in range(x0, x1):
        ok = pred(px[x, y])
        if ok and start is None:
            start = x
        elif not ok and start is not None:
            if x - start >= minw:
                out.append([start, x - 1])
            start = None
    if start is not None and x1 - start >= minw:
        out.append([start, x1 - 1])
    return out


def vspan(px, x, pred, y0=0, y1=900):
    ys = [y for y in range(y0, y1) if pred(px[x, y])]
    return (min(ys), max(ys)) if ys else None


def main() -> None:
    png = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TMP, "png", "corrected-report.v2.png")
    im = Image.open(png).convert("RGB")
    W, H = im.size
    px = im.load()
    with open(os.path.join(ROOT, "tasks", "A16-visual-data-forensics", "inputs",
                           "source.csv"), encoding="utf-8-sig") as fh:
        src = {r["quarter"]: (int(r["revenue_wan"]), int(r["cost_wan"]))
               for r in csv.DictReader(fh)}

    res = {"file": png, "size": [W, H], "size_ok": [W, H] == [1280, 900]}

    # ---- main chart bars -----------------------------------------------------
    probe = 530
    rev_runs = runs_x(px, probe, lambda c: near(c, C_REV), 20, 150, 1220)
    cost_runs = runs_x(px, probe, lambda c: near(c, C_COST), 20, 150, 1220)
    res["revenue_bar_columns"] = rev_runs
    res["cost_bar_columns"] = cost_runs

    bars, ratios = [], []
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    for i, q in enumerate(quarters):
        for kind, rr, val in (("revenue", rev_runs, src[q][0]),
                              ("cost", cost_runs, src[q][1])):
            if i >= len(rr):
                res.setdefault("errors", []).append(f"missing {kind} bar {q}")
                continue
            x0, x1 = rr[i]
            sp = vspan(px, (x0 + x1) // 2,
                       lambda c, k=kind: near(c, C_REV if k == "revenue" else C_COST))
            bars.append(dict(quarter=q, series=kind, value=val, x0=x0, x1=x1,
                             top=sp[0], bottom=sp[1], height=sp[1] - sp[0] + 1,
                             px_per_unit=round((sp[1] - sp[0] + 1) / val, 5)))
            ratios.append((sp[1] - sp[0] + 1) / val)
    res["chart_bars"] = bars
    res["all_bars_share_zero_line"] = len({b["bottom"] for b in bars}) == 1
    res["zero_line_y"] = bars[0]["bottom"] if bars else None
    res["px_per_unit"] = dict(min=round(min(ratios), 5), max=round(max(ratios), 5),
                              spread=round(max(ratios) - min(ratios), 5))
    res["bar_heights_are_proportional"] = (max(ratios) - min(ratios)) < 0.02

    # ---- profit bars ---------------------------------------------------------
    probe2 = 790
    hi = runs_x(px, probe2, lambda c: near(c, C_HI), 20, 50, 760)
    gr = runs_x(px, probe2, lambda c: near(c, C_GREY), 20, 50, 760)
    allp = sorted(hi + gr)
    res["profit_bar_columns"] = allp
    pvals = [src[q][0] - src[q][1] for q in quarters]
    pbars, pratios = [], []
    for i, (x0, x1) in enumerate(allp):
        col = C_HI if near(px[(x0 + x1) // 2, probe2], C_HI) else C_GREY
        # restrict to the profit card: #94A3B8 is also the shared zero-line colour
        sp = vspan(px, (x0 + x1) // 2, lambda c, k=col: near(c, k), 660, 812)
        pbars.append(dict(quarter=quarters[i], value=pvals[i], top=sp[0], bottom=sp[1],
                          height=sp[1] - sp[0] + 1,
                          px_per_unit=round((sp[1] - sp[0] + 1) / pvals[i], 5)))
        pratios.append((sp[1] - sp[0] + 1) / pvals[i])
    res["profit_bars"] = pbars
    res["profit_px_per_unit"] = dict(min=round(min(pratios), 5), max=round(max(pratios), 5))
    # a colour match also catches the antialiased edge rows, so a ~2px constant offset is
    # expected: test the height against value*scale with that allowance instead of a ratio
    exp = (796 - 690) / 66
    res["profit_expected_px_per_unit"] = round(exp, 5)
    res["profit_height_errors_px"] = [round(b["height"] - b["value"] * exp, 2) for b in pbars]
    res["profit_heights_are_proportional"] = all(
        abs(b["height"] - b["value"] * exp) <= 2.5 for b in pbars)
    res["profit_bars_share_zero_line"] = (
        max(b["bottom"] for b in pbars) - min(b["bottom"] for b in pbars) <= 2)

    # ---- nothing may touch the canvas edge ----------------------------------
    body = [c for c in
            (lambda: [px[x, y] for y in range(0, H, 2) for x in range(0, W, 2)])()]
    edge_ink = 0
    for x in range(W):
        for y in (0, 1, H - 2, H - 1):
            if not near(px[x, y], C_PAGE, 12):
                edge_ink += 1
    for y in range(H):
        for x in (0, 1, W - 2, W - 1):
            if not near(px[x, y], C_PAGE, 12):
                edge_ink += 1
    res["ink_on_canvas_border"] = edge_ink
    res["nothing_touches_canvas_edge"] = edge_ink == 0

    print(json.dumps(res, ensure_ascii=False, indent=2))
    json.dump(res, open(os.path.join(TMP, "verify-corrected.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
