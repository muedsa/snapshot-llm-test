"""A17 compare: page-02 illustration vs example-02.png, pixel for pixel.

The page illustration is the example geometry scaled by K, so after cropping
the art band out of the page and dividing by K the two images should match on
every pixel of the shared region.  This is the mechanical check behind the
claim "the teaching illustration is the same construct, redrawn".
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, TASK := "A17")
TMP = os.path.join(ROOT, "tmp", RUN, "A17")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import build_pages as BP  # noqa: E402
import hb  # noqa: E402
import examples as X  # noqa: E402

K = BP.K
report = {}
for spec in BP.PAGES:
    ex = [e for e in X.EXAMPLES if e["n"] == spec["ex"]][0]
    p, _, _, _ = BP.build(spec)
    # rebuild the page DSL to recover the art origin without rendering again
    dsltxt = p.dsl()
    ax = hb.MARGIN + 20
    # panel y = the last <Positioned top=...> before the art background rect
    art_top = None
    for m in dsltxt.split("\n"):
        pass
    # the art band is anchored at panel_y + PANEL_HEAD - 10; panel_y is the
    # y recorded just before illustration_panel(), which equals the first
    # rect of the panel.  Recover it from the emitted markup.
    import re
    panel_rects = re.findall(
        r'<Positioned left="48" top="([\d.]+)" width="([\d.]+)" height="([\d.]+)">\n'
        r'  <Container width="[\d.]+" height="[\d.]+" color="#FFFFFFFF" '
        r'borderRadius="16"', dsltxt)
    if not panel_rects:
        report["page%d" % spec["index"]] = {"error": "panel rect not found"}
        continue
    panel_y = float(panel_rects[0][0])
    ay = panel_y + BP.PANEL_HEAD - 10
    page = Image.open(os.path.join(OUT, "handbook-%02d.png" % spec["index"])).convert("RGB")
    band = page.crop((int(round(ax)), int(round(ay)),
                      int(round(ax + 400 * K)), int(round(ay + 240 * K))))
    exi = Image.open(os.path.join(OUT, "example-%02d.png" % spec["ex"])).convert("RGB")
    # downscale the band back to 400x240 and compare
    back = band.resize(exi.size, Image.LANCZOS)
    a = np.asarray(back).astype(int)
    b = np.asarray(exi).astype(int)
    diff = np.abs(a - b).sum(axis=2)
    report["page%d" % spec["index"]] = {
        "example": spec["ex"],
        "panel_y": panel_y,
        "art_origin": [ax, ay],
        "band_size": list(band.size),
        "mean_abs_diff_per_px": round(float(diff.mean()), 2),
        "max_abs_diff": int(diff.max()),
        "pct_pixels_within_12": round(float((diff <= 12).mean() * 100), 2),
        "note": "the page version also adds panel chrome and, for page 4, a "
                "larger sigma-free redraw, so a small residual is expected; a "
                "large one would mean the geometry drifted",
    }
    band.save(os.path.join(TMP, "crops", "art-p%d.png" % spec["index"]))
    back.save(os.path.join(TMP, "crops", "art-p%d-downscaled.png" % spec["index"]))

json.dump(report, open(os.path.join(TMP, "probe", "art-compare.json"), "w",
                       encoding="utf-8"), ensure_ascii=False, indent=2)
for k, v in report.items():
    print(k, json.dumps(v, ensure_ascii=False))