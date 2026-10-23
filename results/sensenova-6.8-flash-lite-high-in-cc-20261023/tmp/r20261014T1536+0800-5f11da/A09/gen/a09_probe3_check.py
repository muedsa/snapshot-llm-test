"""量出探针 3 的 6 格：省略 alignment 时矩阵是否直接作用在子盒左上角。"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a09_geom as G        # noqa: E402
import a09_pixels as PX     # noqa: E402

RID = "r20261014T1536+0800-5f11da"
TAG = os.environ.get("PROBE_TAG", "probe3")
PNG = Path("tmp") / RID / "A09" / "preview" / (TAG + "-transform.noalignment.png")
META = HERE.parent / (TAG + "-meta.json")

CELL_W, CELL_H = 300.0, 250.0
ORIGIN = (60.0, 70.0)
CX_OFF, CY_OFF = 150.0, 150.0
BOX = G.SIZE
WINDOW = 200.0


def cell_window(i: int):
    cx, cy = ORIGIN[0] + (i % 3) * CELL_W, ORIGIN[1] + (i // 3) * CELL_H
    bx, by = cx + CX_OFF - BOX / 2.0, cy + CY_OFF - BOX / 2.0
    return (int(bx + BOX / 2.0 - WINDOW / 2.0), int(by + BOX / 2.0 - WINDOW / 2.0),
            int(bx + BOX / 2.0 + WINDOW / 2.0), int(by + BOX / 2.0 + WINDOW / 2.0))


def main() -> None:
    meta = json.loads(META.read_text(encoding="utf-8"))
    W, H, px = PX.load(PNG)
    tally = {"PASS": 0, "PASS_AA": 0, "FAIL": 0, "NO_INK": 0}
    out = {"png": "tmp/%s/A09/preview/%s-transform.noalignment.png" % (RID, TAG),
           "png_size": [W, H], "tally": tally, "cells": []}
    for i, c in enumerate(meta["cells"]):
        m_full = tuple(c["affine"])
        rec = PX.compare(px, cell_window(i), tuple(c["box_origin"]), m_full,
                         f"{c['id']} {c['label']}", verbose=False)
        rec["with_alignment"] = c["with_alignment"]
        rec["matrix_str"] = c["matrix_str"]
        rec["verdict"] = (
            "NO_INK" if any(s["verdict"] == "NO_INK" for s in rec["shapes"]) else
            "FAIL" if any(s["verdict"] == "FAIL" for s in rec["shapes"]) else
            "PASS_AA" if any(s["verdict"] == "PASS_AA" for s in rec["shapes"]) else "PASS")
        tally[rec["verdict"]] += 1
        out["cells"].append(rec)

    dest = HERE.parent / (TAG + "-result.json")
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"PNG {W}x{H}   PASS={tally['PASS']} PASS_AA={tally['PASS_AA']} "
          f"FAIL={tally['FAIL']} NO_INK={tally['NO_INK']}")
    for rec in out["cells"]:
        print(f"\n--- {rec['label']}  box={rec['box_origin']}  "
              f"判定={rec['verdict']}  整体偏移估={rec['offset']}")
        for e in rec["shapes"]:
            print(f"    {e['shape']:6s} pred={e['predicted_bbox']}  "
                  f"got={e.get('measured_bbox')}  形心误差={e.get('centroid_err')}  "
                  f"{e['verdict']}")
    print("\n写入", dest)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
