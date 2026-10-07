"""A14 step 1: calibration probe.

Renders every string the card system needs (titles, speakers, status words,
brand, date) as single un-wrapped lines with the exact font family/size the
cards will use, then measures the real ink bounding box of each row with PIL.

Purpose: line breaking and box sizing must be computed from measured advance
widths, not from a guess. Also calibrates the side-bearing correction using
CJK reference strings so `ink width` can be turned into `layout width`.

Output: <tmp>/probe/probe-widths.png (service response, raw bytes)
        <tmp>/probe/measured.json
"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A14"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

snapkit.configure(TASK, OUT, TMP)

CARDS = json.load(open(os.path.join(ROOT, "tasks", "A14-content-stress-batch",
                                    "inputs", "cards.json"), encoding="utf-8"))

TITLE_FONT = D.UI          # Inter,Noto Sans CJK SC
PROBE_SIZE_TITLE = 40
PROBE_SIZE_SPEAKER = 26
PROBE_SIZE_SMALL = 18
PROBE_SIZE_BRAND = 24

X0 = 40
ROW_H = 52
GAP = 62

rows = []          # (key, text, size, font, style)
y = 20


def add(key, text, size, font, style=None):
    global y
    rows.append({"key": key, "text": text, "size": size, "font": font,
                 "style": style, "y": y, "h": ROW_H})
    y += GAP


add("cal-cjk-1", "口", PROBE_SIZE_TITLE, TITLE_FONT)
add("cal-cjk-5", "口口口口口", PROBE_SIZE_TITLE, TITLE_FONT)
for c in CARDS:
    add("title-" + c["id"], c["title"], PROBE_SIZE_TITLE, TITLE_FONT)
for c in CARDS:
    add("speaker-" + c["id"], c["speaker"], PROBE_SIZE_SPEAKER, TITLE_FONT)
for s in ("开放", "满额", "候补", "取消", "本场取消"):
    add("status-" + s, s, PROBE_SIZE_SMALL, TITLE_FONT, "BOLD")
add("brand-bold", "Structure / Vision", PROBE_SIZE_BRAND, "Inter", "BOLD")
add("brand-reg", "Structure / Vision", PROBE_SIZE_BRAND, "Inter", None)
add("date-mono", "2026.11.07", 24, D.MONO, None)
add("index-mono", "01 / 08", 16, D.MONO, None)

W, H = 1200, y + 20
kids = []
for r in rows:
    kids.append(D.text_el(r["text"], x=X0, y=r["y"], w=1120, h=r["h"],
                          size=r["size"], font=r["font"], style=r["style"],
                          color="#111111FF", wrap=False, max_lines=None))
# baseline ruler marks every row top so geometry is verifiable in the probe image
for r in rows:
    kids.append(D.box(0, r["y"], 12, 2, color="#E11D48FF"))
dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
probe_dir = os.path.join(TMP, "probe")
os.makedirs(probe_dir, exist_ok=True)
res = snapkit.render(dsl, "probe-widths.png", "probe-widths.snapshot",
                     final=False, out_dir=probe_dir)
print("render ok=%s status=%s bytes=%s" % (res.get("ok"), res.get("status"),
                                           res.get("bytes")))
for w in D.warnings():
    print("WARN", w)

img = Image.open(res["image"]).convert("RGB")
px = img.load()
img_w, img_h = img.size
print("probe size", img.size)


def ink_bbox(x0, y0, x1, y1):
    minx, miny, maxx, maxy = None, None, None, None
    for yy in range(max(0, y0), min(img_h, y1)):
        for xx in range(max(0, x0), min(img_w, x1)):
            r, g, b = px[xx, yy]
            if (255 - r) > 24 or (255 - g) > 24 or (255 - b) > 24:
                if minx is None or xx < minx:
                    minx = xx
                if maxx is None or xx > maxx:
                    maxx = xx
                if miny is None or yy < miny:
                    miny = yy
                if maxy is None or yy > maxy:
                    maxy = yy
    return minx, miny, maxx, maxy


out = {"canvas": [W, H], "probe_size_title": PROBE_SIZE_TITLE,
       "probe_size_speaker": PROBE_SIZE_SPEAKER, "rows": []}
for r in rows:
    bb = ink_bbox(X0 - 5, r["y"] - 6, 1165, r["y"] + r["h"])
    rec = dict(r)
    rec["ink_bbox"] = list(bb) if bb and bb[0] is not None else None
    rec["ink_width"] = (bb[2] - bb[0] + 1) if bb and bb[0] is not None else None
    out["rows"].append(rec)
    print("%-18s size=%-3s ink_w=%-5s  %s" % (r["key"], r["size"], rec["ink_width"],
                                               r["text"]))

# side-bearing calibration: advance per CJK glyph from the two calibration rows
cal1 = next(r for r in out["rows"] if r["key"] == "cal-cjk-1")
cal5 = next(r for r in out["rows"] if r["key"] == "cal-cjk-5")
adv_per_cjk = (cal5["ink_width"] - cal1["ink_width"]) / 4.0
bear_sum = adv_per_cjk - cal1["ink_width"]
out["calibration"] = {
    "cjk_advance_at_40": round(adv_per_cjk, 3),
    "cjk_ink_at_40_single": cal1["ink_width"],
    "side_bearing_sum_at_40": round(bear_sum, 3),
    "formula": "layout_width(s, size) = (ink_width_40(s) + side_bearing_sum_at_40) * size/40",
}
print(json.dumps(out["calibration"], ensure_ascii=False, indent=2))

with open(os.path.join(probe_dir, "measured.json"), "w", encoding="utf-8",
          newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print("wrote", os.path.join(probe_dir, "measured.json"))