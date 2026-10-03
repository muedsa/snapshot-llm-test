"""A14 · per-card pixel audit + contact sheet + batch-audit.json.

Measures the real rendered PNGs: canvas size, safe margin compliance, per-title-line
ink extents (to check the width model that drove the wrapping), badge/title separation,
and the presence of the status colour. Also builds a contact sheet from the eight real
service PNGs for a consistency check (a check aid only - it never replaces the eight).
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
TMP = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A14")
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A14")
PLAN = json.load(open(os.path.join(TMP, "card-plan.json"), encoding="utf-8"))

HEADER_H = 112
STATUS_BAR_H = 4
MARGIN = 40
SAFE_BOTTOM = 590
BADGE_TOP, BADGE_H = 140, 56
TITLE_TOP, TITLE_BOTTOM = 212, 494


def ink_bbox(im, x0, y0, x1, y1, bg=(255, 255, 255), tol=18):
    """Bounding box of pixels that differ from the background inside a region."""
    crop = im.crop((x0, y0, x1, y1)).convert("RGB")
    w, h = crop.size
    px = crop.load()
    left = top = right = bottom = None
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - bg[0]) > tol or abs(g - bg[1]) > tol or abs(b - bg[2]) > tol:
                if left is None or x < left:
                    left = x
                if right is None or x > right:
                    right = x
                if top is None:
                    top = y
                if bottom is None or y > bottom:
                    bottom = y
    if left is None:
        return None
    return [x0 + left, y0 + top, x0 + right, y0 + bottom]


def audit_card(plan: dict, png: str) -> dict:
    im = Image.open(png)
    w, h = im.size
    rgb = im.convert("RGB")

    # everything below the full-bleed header/status band must respect the 40px margin
    body = ink_bbox(rgb, 0, HEADER_H + STATUS_BAR_H + 1, w, h)
    margin_ok = bool(body) and body[0] >= MARGIN and body[2] <= w - MARGIN \
        and body[3] <= SAFE_BOTTOM

    lines = []
    for lg in plan["title_lines_geometry"]:
        size = plan["title_size"]
        band = ink_bbox(rgb, 0, int(lg["y"]), w, int(lg["y"] + size * 1.30))
        lines.append(dict(line=lg["line"], text=lg["text"], planned_y=lg["y"],
                          planned_x=lg["x"], est_w=lg["est_w"],
                          ink_bbox=band,
                          ink_w=(band[2] - band[0] + 1) if band else 0,
                          ink_x1=band[2] if band else None))
    title_zone = ink_bbox(rgb, 0, TITLE_TOP, w, TITLE_BOTTOM)
    badge = ink_bbox(rgb, 0, BADGE_TOP, w, BADGE_TOP + BADGE_H)
    status_px = rgb.getpixel((int(plan["badge"]["x"]) + 3,
                              BADGE_TOP + BADGE_H // 2))

    return dict(
        file=os.path.basename(png), size=[w, h], size_ok=[w, h] == [1200, 630],
        body_ink_bbox=body, safe_margin_40=margin_ok,
        title_ink_zone=title_zone,
        title_ink_within_zone=bool(title_zone) and title_zone[1] >= TITLE_TOP
        and title_zone[3] <= TITLE_BOTTOM,
        title_widest_line_ink=max((l["ink_w"] for l in lines), default=0),
        title_lines_measured=lines,
        badge_row_ink=badge,
        badge_and_title_do_not_overlap=bool(badge and title_zone)
        and badge[3] < title_zone[1],
        status_colour_sampled=str(status_px),
    )


def contact_sheet(paths: list, out: str) -> tuple:
    scale = 0.5
    cw, ch = int(1200 * scale), int(630 * scale)
    gap, pad, top = 24, 32, 76
    cols, rows = 2, 4
    W = pad * 2 + cols * cw + (cols - 1) * gap
    H = top + pad + rows * ch + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), (241, 245, 249))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sheet)
    dr.rectangle([0, 0, W, 56], fill=(15, 23, 42))
    dr.text((pad, 20), "A14 contact sheet - 8 cards, real 200 responses, 50% scale",
            fill=(248, 250, 252))
    for i, p in enumerate(paths):
        r, c = divmod(i, cols)
        x = pad + c * (cw + gap)
        y = top + r * (ch + gap)
        sheet.paste(Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS), (x, y))
        dr.rectangle([x - 1, y - 1, x + cw, y + ch], outline=(203, 213, 225))
    sheet.save(out)
    return sheet.size


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else "v6"
    results = []
    for plan in PLAN:
        png = os.path.join(TMP, "png", f"card-{plan['id']}.{src}.png")
        a = audit_card(plan, png)
        a["id"] = plan["id"]
        results.append(a)
        print(f"{plan['id']}: size_ok={a['size_ok']} margin40={a['safe_margin_40']} "
              f"title_in_zone={a['title_ink_within_zone']} "
              f"badge_clear={a['badge_and_title_do_not_overlap']} "
              f"widest_title_line={a['title_widest_line_ink']}px "
              f"body_x={a['body_ink_bbox'][0]}..{a['body_ink_bbox'][2]} "
              f"body_y_max={a['body_ink_bbox'][3]}")

    sheet = os.path.join(TMP, "png", f"contact-sheet.{src}.png")
    size = contact_sheet([os.path.join(TMP, "png", f"card-{p['id']}.{src}.png")
                          for p in PLAN], sheet)
    print("contact sheet", sheet, size)

    with open(os.path.join(TMP, f"pixel-audit.{src}.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print("all_ok =", all(r["size_ok"] and r["safe_margin_40"]
                          and r["title_ink_within_zone"]
                          and r["badge_and_title_do_not_overlap"] for r in results))


if __name__ == "__main__":
    main()
