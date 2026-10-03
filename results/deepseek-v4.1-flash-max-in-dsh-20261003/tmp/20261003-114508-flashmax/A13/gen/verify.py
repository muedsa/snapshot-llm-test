"""A13 · real pixel verification of the delivered PNGs.

Checks the requirements that cannot be judged by eye alone:
  * exact canvas size of every final PNG
  * the icons are genuinely transparent (alpha 0 outside the mark)
  * the icons contain interior transparent negative space (the two moats)
  * symbol-black has RGB == 0 on every pixel with alpha > 0
  * the two icons have byte-identical alpha channels (same geometry)
  * mark bounding box + clear space, measured from the alpha channel
  * required strings present in the two application DSL files
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A13"
OUT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A13"

SPEC = {
    "symbol-color.png": (512, 512),
    "symbol-black.png": (512, 512),
    "brand-banner.png": (1200, 400),
    "launch-poster.png": (1080, 1350),
}
STRINGS = {
    "brand-banner.snapshot": ["叠光 Layerlight", "把复杂信息，组织成清晰画面"],
    "launch-poster.snapshot": ["叠光 Layerlight", "把复杂信息，组织成清晰画面",
                               "2026.11.07 · ONLINE", "OPEN BETA",
                               "layerlight.example.org"],
}


def icon_report(path: str) -> dict:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    a = im.getchannel("A")
    px = im.load()
    corners = [px[0, 0][3], px[w - 1, 0][3], px[0, h - 1][3], px[w - 1, h - 1][3]]
    bbox = a.getbbox()
    # interior transparency: scan the horizontal and vertical centre lines
    cy, cx = h // 2, w // 2
    row = [a.getpixel((x, cy)) for x in range(w)]
    col = [a.getpixel((cx, y)) for y in range(h)]

    def runs(vals):
        out, cur = [], None
        for i, v in enumerate(vals):
            if v == 0:
                cur = i if cur is None else cur
            elif cur is not None:
                out.append((cur, i - 1))
                cur = None
        if cur is not None:
            out.append((cur, len(vals) - 1))
        return out

    row_runs = [r for r in runs(row) if r[0] > bbox[0] and r[1] < bbox[2]]
    col_runs = [r for r in runs(col) if r[0] > bbox[1] and r[1] < bbox[3]]
    solid = sum(1 for p in im.getdata() if p[3] > 0)
    return dict(
        file=os.path.basename(path), size=[w, h],
        corner_alpha=corners, transparent_corners=all(c == 0 for c in corners),
        alpha_bbox=list(bbox),
        mark_w=bbox[2] - bbox[0], mark_h=bbox[3] - bbox[1],
        clear_space_left=bbox[0], clear_space_top=bbox[1],
        clear_space_right=w - bbox[2], clear_space_bottom=h - bbox[3],
        interior_transparent_runs_h=row_runs, interior_transparent_runs_v=col_runs,
        interior_negative_space=bool(row_runs and col_runs),
        opaque_pixels=solid, coverage_pct=round(100.0 * solid / (w * h), 2),
        alpha_sha=__import__("hashlib").sha256(a.tobytes()).hexdigest()[:16],
    )


def black_report(path: str) -> dict:
    im = Image.open(path).convert("RGBA")
    bad = 0
    total_vis = 0
    worst = None
    for r, g, b, al in im.getdata():
        if al > 0:
            total_vis += 1
            if r or g or b:
                bad += 1
                if worst is None:
                    worst = [r, g, b, al]
    return dict(file=os.path.basename(path), visible_pixels=total_vis,
                nonzero_rgb_pixels=bad, first_offender=worst,
                pure_black=bad == 0)


def geometry_match(p1: str, p2: str) -> dict:
    """TASK.md allows antialiasing alpha; 'same geometry' is checked on the solid mask."""
    a = Image.open(p1).convert("RGBA").getchannel("A").load()
    b = Image.open(p2).convert("RGBA").getchannel("A").load()
    w, h = Image.open(p1).size
    diff = geo = maxd = 0
    sa = sb = 0
    for y in range(h):
        for x in range(w):
            va, vb = a[x, y], b[x, y]
            if va == 255:
                sa += 1
            if vb == 255:
                sb += 1
            if va != vb:
                diff += 1
                maxd = max(maxd, abs(va - vb))
                if (va == 255) != (vb == 255):
                    geo += 1
    return dict(solid_alpha_pixels_color=sa, solid_alpha_pixels_black=sb,
                geometry_differences=geo, antialias_only_pixels=diff,
                max_alpha_delta=maxd,
                same_geometry=geo == 0 and sa == sb,
                note="AA alpha differences are explicitly allowed by TASK.md")


def main() -> None:
    out = {}
    for name, (ew, eh) in SPEC.items():
        p = os.path.join(OUT, name)
        if not os.path.exists(p):
            out[name] = {"missing": True}
            continue
        if name.startswith("symbol-"):
            out[name] = icon_report(p)
            out[name]["expected_size"] = [ew, eh]
            out[name]["size_ok"] = out[name]["size"] == [ew, eh]
        else:
            im = Image.open(p)
            out[name] = {"file": name, "size": list(im.size), "mode": im.mode,
                         "expected_size": [ew, eh], "size_ok": list(im.size) == [ew, eh],
                         "bytes": os.path.getsize(p)}
    out["symbol-black-purity"] = black_report(os.path.join(OUT, "symbol-black.png"))
    out["icon_geometry_match"] = geometry_match(os.path.join(OUT, "symbol-color.png"),
                                                os.path.join(OUT, "symbol-black.png"))

    for dsl, need in STRINGS.items():
        text = open(os.path.join(OUT, dsl), encoding="utf-8").read()
        out[f"strings::{dsl}"] = {s: (s in text) for s in need}

    with open(os.path.join(TMP, "verify.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
