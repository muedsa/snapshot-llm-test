# -*- coding: utf-8 -*-
"""Verify the rendered grid-scene PNG against the scene data, and measure the
REAL id-text bounding boxes from the image.

For every object G01-G64:
  - sample the body pixel (ring: on the band, since the centre is the hole)
    and compare with the expected colour,
  - scan the cell's body zone for the expected colour -> measured body bbox,
  - measure the dark id-label text bbox in the cell's id zone,
  - assert the id text never touches the body (ID must sit outside the body).

Writes tmp/run-20261011-01/A19/gen/grid-measure.json.
"""
import json
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A19/gen"

CELL = 200
COLOR_HEX = {"blue": "#2563EB", "orange": "#F59E0B",
             "green": "#16A34A", "purple": "#7C3AED"}
TEXT_RGB = (0x33, 0x41, 0x55)
TOL_BODY = 45      # colour-match tolerance for body pixels
TOL_TEXT = 50      # colour-match tolerance for the id label pixels
BBOX_TOL = 2       # measured vs constructed bbox tolerance (antialias edge)


def near(c, t, tol):
    return all(abs(c[i] - t[i]) < tol for i in range(3))


def hexrgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def main():
    raw = json.loads((GEN / "scene-raw.json").read_text(encoding="utf-8"))
    objs = raw["objects"]
    im = Image.open(GEN / "grid-scene-02.png").convert("RGB")
    px = im.load()
    assert im.size == (1600, 1600), im.size

    results = []
    fails = []
    for o in objs:
        r, c = o["row"], o["col"]
        cx, cy = o["center"]
        z = o["size"]
        col = hexrgb(COLOR_HEX[o["color"]])

        # --- body pixel sample
        if o["shape"] == "ring":
            sx, sy = cx + 3 * z // 8, cy        # on the band
        else:
            sx, sy = cx, cy
        sample = px[sx, sy]
        body_ok = near(sample, col, TOL_BODY)

        # --- measured body bbox inside the body zone (cell+40..cell+160)
        x0, y0 = (c - 1) * CELL + 40, (r - 1) * CELL + 40
        minx = miny = 10 ** 9
        maxx = maxy = -10 ** 9
        n = 0
        for y in range(y0, y0 + 120):
            for x in range(x0, x0 + 120):
                if near(px[x, y], col, TOL_BODY):
                    n += 1
                    minx, miny = min(minx, x), min(miny, y)
                    maxx, maxy = max(maxx, x), max(maxy, y)
        exp = o["body_bbox"]
        bbox_ok = (abs(minx - exp[0]) <= BBOX_TOL
                   and abs(miny - exp[1]) <= BBOX_TOL
                   and abs(maxx - (exp[2] - 1)) <= BBOX_TOL
                   and abs(maxy - (exp[3] - 1)) <= BBOX_TOL)

        # --- measured id text bbox in the id zone (cell+(0,0)..(58,40))
        tx0, ty0 = (c - 1) * CELL, (r - 1) * CELL
        tminx = tminy = 10 ** 9
        tmaxx = tmaxy = -10 ** 9
        tn = 0
        for y in range(ty0, ty0 + 40):
            for x in range(tx0, tx0 + 58):
                if near(px[x, y], TEXT_RGB, TOL_TEXT):
                    tn += 1
                    tminx, tminy = min(tminx, x), min(tminy, y)
                    tmaxx, tmaxy = max(tmaxx, x), max(tmaxy, y)
        text_ok = tn > 0
        # id text must stay outside the body
        separated = (tmaxx < exp[0] or tminx > exp[2]
                     or tmaxy < exp[1] or tminy > exp[3])

        rec = {
            "id": o["id"],
            "body_sample_rgb": list(sample),
            "body_color_ok": body_ok,
            "body_bbox_measured": [minx, miny, maxx + 1, maxy + 1],
            "body_bbox_constructed": exp,
            "body_bbox_ok": bbox_ok,
            "body_pixels": n,
            "id_text_box_measured": [tminx, tminy, tmaxx + 1, tmaxy + 1],
            "id_text_pixels": tn,
            "id_text_ok": text_ok,
            "id_outside_body": separated,
        }
        results.append(rec)
        if not (body_ok and bbox_ok and text_ok and separated):
            fails.append(rec)

    doc = {
        "png": "tmp/run-20261011-01/A19/gen/grid-scene-02.png",
        "checked_at_note": "对 A19-grid-02 渲染的实际像素测量",
        "tolerances": {
            "colour_match": TOL_BODY,
            "bbox_vs_constructed_px": BBOX_TOL,
        },
        "verified_objects": len(results) - len(fails),
        "failed_objects": len(fails),
        "results": results,
    }
    (GEN / "grid-measure.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("verified:", doc["verified_objects"], "/", len(results))
    if fails:
        for f in fails:
            print("FAIL", f["id"], "color_ok", f["body_color_ok"],
                  "bbox_ok", f["body_bbox_ok"],
                  "measured", f["body_bbox_measured"],
                  "constructed", f["body_bbox_constructed"],
                  "text_ok", f["id_text_ok"],
                  "sep", f["id_outside_body"])
    else:
        # sample stats for the report
        tw = [r["id_text_box_measured"][2] - r["id_text_box_measured"][0]
              for r in results]
        th = [r["id_text_box_measured"][3] - r["id_text_box_measured"][1]
              for r in results]
        print("id text width range:", min(tw), "-", max(tw),
              "| height range:", min(th), "-", max(th))
        print("ALL 64 objects verified: colour, body bbox, id label, "
              "id-outside-body")


if __name__ == "__main__":
    main()
