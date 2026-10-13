"""A14 verification against the eight returned PNGs.

Checks, per card: the 40px safe margin is clean, the title actually rendered with the line
count the generator modelled, no title ink crosses the footer rule, the status badge uses
the status colour, and the four statuses really are four different encodings.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
OUT_DIR = ROOT / "outputs" / RUN / "A14"
TMP_DIR = ROOT / "tmp" / RUN / "A14"

W, H, M = 1200, 630, 40
DIVIDER_Y = 452
PAPER = np.array([247, 245, 240], dtype=np.int16)


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.int16)


def bands(ink, x0, x1, y0, y1, gap=4):
    sub = ink[y0:y1, x0:x1]
    rows = np.nonzero(sub.any(axis=1))[0]
    if not len(rows):
        return []
    out, st, prev = [], int(rows[0]), int(rows[0])
    for r in rows[1:]:
        if int(r) - prev > gap:
            out.append((st + y0, prev + y0))
            st = int(r)
        prev = int(r)
    out.append((st + y0, prev + y0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", required=True)
    a = ap.parse_args()
    audit = json.loads((OUT_DIR / "batch-audit.json").read_text(encoding="utf-8"))
    res, problems = {}, []

    badge_cols = {}
    for cid, card in audit["cards"].items():
        im = Image.open(TMP_DIR / f"{a.ver}-{cid}.png")
        im.load()
        assert im.size == (W, H), (cid, im.size)
        arr = np.asarray(im.convert("RGB"), dtype=np.int16)
        ink = np.abs(arr - PAPER).max(axis=2) > 40

        frame = np.zeros((H, W), dtype=bool)
        frame[:M, :] = True
        frame[H - M:, :] = True
        frame[:, :M] = True                # the status spine starts at x=40, on the margin
        frame[:, W - M:] = True
        dirty = int((ink & frame).sum())
        if dirty:
            ys, xs = np.nonzero(ink & frame)
            problems.append(f"[{cid}] margin ink {dirty}px e.g. ({int(xs[0])},{int(ys[0])})")

        # title band: dark ink in the title column between the kicker and the rule
        dark = arr.max(axis=2) < 110
        tb = bands(dark, 70, W - M, 190, DIVIDER_Y - 4)
        tb = [b for b in tb if b[1] - b[0] > card["title_size"] * 0.5]
        if len(tb) != card["title_lines"]:
            problems.append(f"[{cid}] title lines modelled={card['title_lines']} "
                            f"rendered={len(tb)} bands={tb}")
        if tb and tb[-1][1] > DIVIDER_Y - 2:
            problems.append(f"[{cid}] title crosses the rule at {DIVIDER_Y}: {tb[-1]}")

        # the badge's own ink is the most saturated pixel in the pill, not its tint
        bx, by = W - M - 250, 48
        patch = arr[by + 4:by + 48, bx + 8:bx + 244].reshape(-1, 3)
        sat = (patch.max(axis=1) - patch.min(axis=1)) + (255 - patch.max(axis=1))
        col = patch[sat.argmax()]
        badge_cols[cid] = [int(x) for x in col]
        st = audit["status_system"][card["status"]]
        if np.abs(col - rgb(st["colour"])).max() > 40:
            problems.append(f"[{cid}] badge ink {[int(x) for x in col]} "
                            f"!~ status colour {st['colour']}")

        res[cid] = {
            "png": f"tmp/{RUN}/A14/{a.ver}-{cid}.png",
            "margin_ink_px": dirty,
            "title_bands_rendered": [list(b) for b in tb],
            "title_lines_modelled": card["title_lines"],
            "title_lines_match": bool(len(tb) == card["title_lines"]),
            "title_size_modelled_px": card["title_size"],
            "badge_ink_rgb": [int(x) for x in col],
            "status": card["status"], "status_symbol": st["symbol"],
            "status_en": st["en"],
        }
        audit["cards"][cid]["image_viewed"] = {
            "viewed": True, "png": res[cid]["png"],
            "title_bands_rendered": res[cid]["title_bands_rendered"],
            "margin_ink_px": dirty}

    distinct = {cid: tuple(v) for cid, v in badge_cols.items()}
    by_status = {}
    for cid, v in audit["cards"].items():
        by_status.setdefault(v["status"], set()).add(tuple(res[cid]["badge_ink_rgb"]))
    enc = {s: {"colour": audit["status_system"][s]["colour"],
               "symbol": audit["status_system"][s]["symbol"],
               "en": audit["status_system"][s]["en"],
               "cards": [c for c in audit["cards"] if audit["cards"][c]["status"] == s],
               "badge_ink_rgb_observed": sorted(next(iter(v2)) for v2 in [by_status[s]])[0]
               if by_status[s] else None}
           for s, v2 in by_status.items()}
    audit["status_encodings_observed"] = enc
    audit["status_four_way_difference"] = {
        "distinct_colours": len({v["colour"] for v in enc.values()}),
        "distinct_symbols": len({v["symbol"] for v in enc.values()}),
        "distinct_wordings": len({v["en"] for v in enc.values()}),
        "all_four_differ": bool(len(enc) == 4 and len({v["colour"] for v in enc.values()}) == 4
                                and len({v["symbol"] for v in enc.values()}) == 4)}
    audit["rendered_verification"] = {
        "ver": a.ver, "problems": problems, "per_card": res,
        "method": "对每张返回 PNG 比较纸色底找墨迹；检查 40px 外框、标题实际行数条带、"
                  "标题是否越过分隔线，以及状态徽标墨色是否等于该状态的规定色"}
    (OUT_DIR / "batch-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # contact sheet: an extra consistency check, not a substitute for the eight originals
    sheet = Image.new("RGB", (2 * 600 + 30, 4 * 315 + 60), (255, 255, 255))
    for i, cid in enumerate(sorted(audit["cards"])):
        t = Image.open(TMP_DIR / f"{a.ver}-{cid}.png").convert("RGB").resize(
            (600, 315), Image.LANCZOS)
        sheet.paste(t, ((i % 2) * 610 + 10, (i // 2) * 325 + 10))
    sheet.save(TMP_DIR / f"{a.ver}-contact-sheet.png")

    print(json.dumps({"problems": problems,
                      "four_way": audit["status_four_way_difference"],
                      "lines_match_all": all(r["title_lines_match"] for r in res.values()),
                      "margin_clean_all": all(r["margin_ink_px"] == 0 for r in res.values())},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
