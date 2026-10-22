# -*- coding: utf-8 -*-
"""A15 text calibration comparator.

Compares reference vs reconstruction glyph boxes on the anchored edge
(left/center/right per texts-reference.json) plus vertical top, and writes
calib.json (absolute offsets from reference targets) for gen_a15.py.
Also reports per-text width deltas to spot font-size mismatches.

Usage:
  python compare_texts.py <ref.json> <recon.json> <calib_old.json> <calib_out.json>

calib_out = calib_old + measured_delta (cumulative: gen_a15.py positions
boxes at reference + calib, so each round's correction must build on the
offset already applied, otherwise equal-and-opposite oscillation occurs).
"""
import json
import pathlib
import sys


def anchor_val(box, anchor):
    if anchor == "left":
        return box[0]
    if anchor == "right":
        return box[2]
    return (box[0] + box[2]) / 2


def main():
    ref = json.loads(pathlib.Path(sys.argv[1]).read_text("utf-8"))
    rec = json.loads(pathlib.Path(sys.argv[2]).read_text("utf-8"))
    old_path = pathlib.Path(sys.argv[3])
    out = pathlib.Path(sys.argv[4])
    old = json.loads(old_path.read_text("utf-8")) if old_path.exists() else {}

    calib, rows, missing = {}, [], []
    for key, rv in ref.items():
        rb = rv["box"]
        ab = rec.get(key, {}).get("box")
        if rb is None or ab is None:
            missing.append(key)
            continue
        anchor = rv["anchor"]
        dx = anchor_val(rb, anchor) - anchor_val(ab, anchor)
        dy = rb[1] - ab[1]
        odx, ody = old.get(key, [0, 0])
        calib[key] = [round(odx + dx), round(ody + dy)]
        rw, aw = rb[2] - rb[0], ab[2] - ab[0]
        werr = (aw - rw) / rw if rw else 0
        rows.append((key, round(dx, 1), dy, rw, aw, round(werr * 100, 1)))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(calib, indent=1), encoding="utf-8")

    print(f"{'key':16s} {'dx':>6s} {'dy':>4s} {'ref_w':>6s} {'rec_w':>6s} "
          f"{'w%':>6s}")
    for r in sorted(rows, key=lambda t: -max(abs(t[1]), abs(t[2]))):
        flag = " <<" if max(abs(r[1]), abs(r[2])) > 2 or abs(r[5]) > 8 else ""
        print(f"{r[0]:16s} {r[1]:6.1f} {r[2]:4d} {r[3]:6d} {r[4]:6d} "
              f"{r[5]:6.1f}{flag}")
    if missing:
        print("MISSING:", missing)
    big = [r for r in rows if abs(r[5]) > 8]
    print(f"texts={len(rows)} missing={len(missing)} "
          f"|dx|max={max(abs(r[1]) for r in rows)} "
          f"|dy|max={max(abs(r[2]) for r in rows)} "
          f"width_off>8%={len(big)}")


if __name__ == "__main__":
    main()
