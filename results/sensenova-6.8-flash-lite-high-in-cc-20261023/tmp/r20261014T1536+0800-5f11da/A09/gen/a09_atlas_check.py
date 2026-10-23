"""A09 最终图像素量测：对 12 格逐形状核对预测 bbox / 形心与 PNG 实测值。

判据：±1.5 px 通过；1.5–2.2 px 记 PASS_AA（反走样例外，仅限非整数像素的
旋转/缩放置栅）；超过 2.2 px 记 FAIL。
量测窗口取各格 200×200（舞台中心 ±100），完整覆盖该格变换后的全部主体，
且不含任何深色文字（INK #0F172A 与圆点色 #111111 距离仅 25.7）。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[3] / "tools"))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
import a09_geom as G        # noqa: E402
import a09_pixels as PX     # noqa: E402
import suite as S           # noqa: E402

RID = S.run_id()


def main() -> None:
    out_dir, tmp_dir = S.task_dirs("A09")
    png = out_dir / "transform-atlas.png"
    meta = json.loads((tmp_dir / "atlas-meta.json").read_text(encoding="utf-8"))
    W, H, px = PX.load(png)
    tally = {"PASS": 0, "PASS_AA": 0, "FAIL": 0, "NO_INK": 0}
    shape_tally = dict(tally)
    cells_out = []
    for c in meta["cells"]:
        m = tuple(c["affine"])
        rec = PX.compare(px, tuple(c["measure_window"]), tuple(c["box_origin"]),
                         m, c["id"] + " " + c["op_short"], verbose=False)
        rec["id"] = c["id"]
        rec["op_full"] = c["op_full"]
        rec["matrix_str"] = c["matrix_str"]
        rec["matrix_flat"] = c["matrix_flat"]
        rec["cell_center"] = c["cell_center"]
        rec["stamp_bbox_predicted_canvas"] = c["stamp_bbox_canvas"]
        rec["ops"] = c["ops"]
        rec["verdict"] = (
            "NO_INK" if any(s["verdict"] == "NO_INK" for s in rec["shapes"]) else
            "FAIL" if any(s["verdict"] == "FAIL" for s in rec["shapes"]) else
            "PASS_AA" if any(s["verdict"] == "PASS_AA" for s in rec["shapes"]) else "PASS")
        tally[rec["verdict"]] += 1
        for s in rec["shapes"]:
            shape_tally[s["verdict"]] = shape_tally.get(s["verdict"], 0) + 1
        cells_out.append(rec)

    dest = HERE.parent / "atlas-result.json"
    dest.write_text(json.dumps({
        "png": S.rel(png), "png_size": [W, H],
        "criterion": "bbox/形心误差 ≤1.5 px 判 PASS；1.5–2.2 px 判 PASS_AA"
                     "（反走样例外：仅 30° 旋转与非整数缩放的栅格化误差）；>2.2 px 判 FAIL",
        "tally_cells": tally, "tally_shapes": shape_tally,
        "cells": cells_out,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print("PNG %dx%d  cells: PASS=%d PASS_AA=%d FAIL=%d NO_INK=%d"
          % (W, H, tally["PASS"], tally["PASS_AA"], tally["FAIL"], tally["NO_INK"]))
    print("shapes:", shape_tally)
    worst = 0.0
    for rec in cells_out:
        print("\n--- %s  %s   判定=%s  整体偏移估=%s"
              % (rec["id"], rec["label"], rec["verdict"], rec["offset"]))
        print("    pred_canvas_bbox=%s" % rec["stamp_bbox_predicted_canvas"])
        for e in rec["shapes"]:
            ce = e.get("centroid_err") or [0, 0]
            worst = max(worst, max(abs(ce[0]), abs(ce[1])))
            print("    %-5s pred=%s got=%s 形心误差=%s %s"
                  % (e["shape"], e["predicted_bbox"], e.get("measured_bbox"),
                     ce, e["verdict"]))
    print("\n最大形心误差 %.4f px" % worst)
    print("写入", dest)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
