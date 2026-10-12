"""Pixel self-check for the A06 dependency map (observation only, no post-processing).

Run from the suite root:
  SNAPSHOT_TASK_ROOT=... SNAPSHOT_RUN_ID=... python tmp/<run_id>/A06/check_geom_a06.py <png>
"""
import json
import os
import sys
from pathlib import Path

from PIL import Image
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gen_a06", HERE / "generate_a06.py")
gen = importlib.util.module_from_spec(spec)
sys.argv_backup = sys.argv
sys.argv = ["generate_a06.py"]
spec.loader.exec_module(gen)
sys.argv = sys.argv_backup
gen.build(gen.analyse(json.loads(gen.INP.read_text(encoding="utf-8"))))

W, H, M = gen.W, gen.H, gen.M
BG = tuple(int(gen.BG[i:i + 2], 16) for i in (1, 3, 5))
TOL = 12                      # channel distance above which a pixel counts as ink


def rgb(px):
    return px[0], px[1], px[2]


def is_ink(px):
    return max(abs(a - b) for a, b in zip(rgb(px), BG)) > TOL


def near(px, hexcol, tol=40):
    c = tuple(int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return all(abs(a - b) <= tol for a, b in zip(rgb(px), c))


def main(png):
    im = Image.open(png)
    rep = {"image": str(png), "size": list(im.size), "mode": im.mode}
    px = im.load()
    problems = []
    if im.size != (W, H):
        problems.append(f"canvas {im.size} != {(W, H)}")

    # 1. safe ring ---------------------------------------------------------
    ring = 0
    for y in range(H):
        for x in range(W):
            if x < M or y < M or x >= W - M or y >= H - M:
                if is_ink(px[x, y]):
                    ring += 1
    rep["ring_ink_pixels"] = ring
    if ring:
        problems.append(f"{ring} ink pixels inside the {M}px safe ring")

    # 2. node boxes: phase rail + border colour present --------------------
    rail_hits = {}
    for node in sorted(gen.PLACE):
        b = gen.box(node)
        col = gen.PHASE[node][1]
        x0, y0 = int(b["x"]) + 12, int(b["y"])
        hits = sum(1 for x in range(x0, x0 + 40) if near(px[x, y0 + 2], col))
        rail_hits[node] = hits
        if hits < 30:
            problems.append(f"{node} phase rail ink {hits}/40 at y={y0 + 2}")
    rep["phase_rail_hits"] = rail_hits

    # 3. arrowheads: ink just outside the target border along the entry side
    head_hits = {}
    for key, g in gen.GEOM["edges"].items():
        tip = g["polyline"][-1]
        side = g["enters"]
        tx, ty = int(round(tip[0])), int(round(tip[1]))
        win = []
        if side == "left":
            win = [(x, y) for x in range(tx - 12, tx - 1) for y in range(ty - 8, ty + 9)]
        elif side == "top":
            win = [(x, y) for x in range(tx - 8, tx + 9) for y in range(ty - 12, ty - 1)]
        elif side == "bottom":
            win = [(x, y) for x in range(tx - 8, tx + 9) for y in range(ty + 2, ty + 13)]
        ink = sum(1 for p in win if is_ink(px[p[0], p[1]]))
        head_hits[key] = {"window": len(win), "ink": ink, "at": [tx, ty], "side": side}
        if ink < 6:
            problems.append(f"{key} arrowhead ink {ink} in {len(win)}px window")
    rep["arrowhead_windows"] = head_hits

    # 4. feedback arrows reach N08 top border ------------------------------
    fb_hits = {}
    for key, g in gen.GEOM["feedback"].items():
        tx, ty = (int(round(g["polyline"][-1][0])), int(round(g["polyline"][-1][1])))
        ink = sum(1 for x in range(tx - 8, tx + 9) for y in range(ty - 12, ty - 1)
                  if near(px[x, y], gen.FB))
        fb_hits[key] = {"x": tx, "y": ty, "pink_ink": ink}
        if ink < 6:
            problems.append(f"feedback {key} pink arrowhead ink {ink}")
    rep["feedback_arrowheads"] = fb_hits

    # 5. panels stay inside their rectangles (halo test) -------------------
    panels = [("legend", M, gen.LEG_Y - 6, W - 2 * M, 36),
              ("card1", M, gen.CARD_Y, (W - 2 * M - 20) / 2, 128),
              ("card2", M + (W - 2 * M - 20) / 2 + 20, gen.CARD_Y,
               (W - 2 * M - 20) / 2, 128),
              ("audit", M, gen.AUDIT_Y, W - 2 * M, 96)]
    halo = {}
    HM = 3                      # adjacent panels sit 6px apart, so keep the frame tight
    for name, x0, y0, pw, ph in panels:
        x0, y0, x1, y1 = int(x0), int(y0), int(x0 + pw), int(y0 + ph)
        spill = 0
        for y in range(max(0, y0 - HM), min(H, y1 + HM + 1)):
            for x in range(max(0, x0 - HM), min(W, x1 + HM + 1)):
                if x0 - 1 <= x <= x1 + 1 and y0 - 1 <= y <= y1 + 1:
                    continue
                if is_ink(px[x, y]):
                    spill += 1
        halo[name] = spill
        if spill:
            problems.append(f"{name} halo {spill} ink px outside its rect")
    rep["panel_halo"] = halo

    # 6. every node label row must contain ink (text really painted) -------
    empty = []
    for node in sorted(gen.PLACE):
        b = gen.box(node)
        x0, y0 = int(b["x"]) + 4, int(b["y"]) + 34
        ink = sum(1 for x in range(x0, int(b["x"] + b["w"]) - 4)
                  for y in range(y0, y0 + 30) if is_ink(px[x, y]))
        if ink < 200:
            empty.append(f"{node} label ink {ink}")
    rep["node_label_min_ink"] = ">=200 px per node"
    problems += empty

    rep["problems"] = problems
    out = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")) / "tmp" / \
        os.environ["SNAPSHOT_RUN_ID"] / "A06" / "geom-report.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ring": ring, "halo": halo, "problems": problems},
                     ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(
        HERE / "preview" / "v05.png")
    sys.exit(main(target))
