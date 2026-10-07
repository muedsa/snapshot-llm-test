# -*- coding: utf-8 -*-
"""A13 verification: prove every TASK.md hard requirement from the delivered files.

Checks
  1. file presence, PNG format, exact pixel size, RGBA
  2. colour vs mono: identical alpha mask (+-1), identical ink bbox and void bbox
  3. mono purity: every pixel with alpha>0 has R=G=B=0
  4. clearspace: transparent ring around the ink in both 512 symbols
  5. geometry consistency: every mark instance in the banner and the poster is
     measured from its own pixels and compared with the 512 symbol's ratios
  6. required copy present in the delivered .snapshot files
  7. no <Image> / no external asset anywhere in the delivered DSL
  8. component count of the mark
Writes tmp/<run>/A13/verify/report.json and prints a summary.
"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state as S  # noqa: E402
import layerlight as L  # noqa: E402

OUT = os.path.join(S.OUT_ROOT, "A13")
TMP = os.path.join(S.TMP_ROOT, "A13")
VDIR = os.path.join(TMP, "verify")
os.makedirs(VDIR, exist_ok=True)
MARK = L.MARK
REPORT = {}
FAIL = []


def check(name, ok, detail):
    REPORT[name] = {"pass": bool(ok), "detail": detail}
    print("%-46s %s  %s" % (name, "PASS" if ok else "FAIL", detail))
    if not ok:
        FAIL.append(name)


# ------------------------------------------------------------------ 1. files
WANT = {"symbol-color.png": (512, 512), "symbol-black.png": (512, 512),
        "brand-banner.png": (1200, 400), "launch-poster.png": (1080, 1350)}
files = {}
for fn, size in WANT.items():
    p = os.path.join(OUT, fn)
    ok = os.path.exists(p)
    info = {"exists": ok, "expected_size": list(size)}
    if ok:
        with open(p, "rb") as fh:
            magic = fh.read(8)
        info["png_magic"] = magic[:4] == b"\x89PNG"
        im = Image.open(p)
        info["actual_size"] = list(im.size)
        info["mode"] = im.mode
        info["bytes"] = os.path.getsize(p)
        ok = info["png_magic"] and list(im.size) == list(size)
        files[fn] = im.convert("RGBA")
    dsl = os.path.join(OUT, fn.replace(".png", ".snapshot"))
    info["dsl_exists"] = os.path.exists(dsl)
    info["dsl_bytes"] = os.path.getsize(dsl) if os.path.exists(dsl) else 0
    check("file %s %dx%d" % (fn, size[0], size[1]), ok and info["dsl_exists"], info)

# ------------------------------------------------------------------ 2/3. symbols
ac = files["symbol-color.png"].split()[3]
ab = files["symbol-black.png"].split()[3]
diff = maxdelta = 0
for y in range(512):
    for x in range(512):
        u, v = ac.getpixel((x, y)), ab.getpixel((x, y))
        if u != v:
            diff += 1
            maxdelta = max(maxdelta, abs(u - v))
check("colour/mono alpha mask identical", diff <= 200 and maxdelta <= 1,
      {"differing_px": diff, "max_delta": maxdelta, "tolerance": "delta<=1, <200px"})

pb = files["symbol-black.png"].load()
nonblack = [(x, y) for y in range(512) for x in range(512)
            if pb[x, y][3] > 0 and (pb[x, y][0] or pb[x, y][1] or pb[x, y][2])]
check("mono RGB == 0 wherever alpha>0", not nonblack,
      {"violations": len(nonblack), "sample": nonblack[:5]})


def enclosed_hole(is_mark, bb):
    """BBox-relative flood fill from the bbox border through background pixels.
    Whatever background is NOT reached is an enclosed hole (the mark's window).
    Returns (void_bbox_abs, hole_pixel_count) or (None, 0)."""
    x0, y0, x1, y1 = bb
    w, h = x1 - x0, y1 - y0
    seen = [[False] * w for _ in range(h)]
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if not is_mark(x0 + x, y0 + y) and not seen[y][x]:
                seen[y][x] = True
                stack.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if not is_mark(x0 + x, y0 + y) and not seen[y][x]:
                seen[y][x] = True
                stack.append((x, y))
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] \
                    and not is_mark(x0 + nx, y0 + ny):
                seen[ny][nx] = True
                stack.append((nx, ny))
    hole = [(x0 + x, y0 + y) for y in range(h) for x in range(w)
            if not seen[y][x] and not is_mark(x0 + x, y0 + y)]
    if not hole:
        return None, 0
    hb = (min(p[0] for p in hole), min(p[1] for p in hole),
          max(p[0] for p in hole) + 1, max(p[1] for p in hole) + 1)
    return hb, len(hole)


def mask_stats(alpha, thr=8):
    m = alpha.point(lambda v: 255 if v > thr else 0)
    bb = m.getbbox()
    px = alpha.load()
    hb, n = enclosed_hole(lambda x, y: px[x, y] > thr, bb)
    return bb, hb, n


bb_c, hb_c, nhole_c = mask_stats(ac)
bb_b, hb_b, nhole_b = mask_stats(ab)
check("symbols: same ink bbox", bb_c == bb_b,
      {"colour_ink_bbox": bb_c, "mono_ink_bbox": bb_b})
check("symbols: same void bbox", hb_c == hb_b,
      {"colour_void_bbox": hb_c, "mono_void_bbox": hb_b, "void_px": nhole_c})

INK = 398.22
want_clear = INK / 9.0
margins = {"left": bb_c[0], "top": bb_c[1], "right": 512 - bb_c[2], "bottom": 512 - bb_c[3]}
check("symbol clearspace >= ink/9 (%.1fpx)" % want_clear,
      min(margins.values()) >= want_clear - 1.0,
      {"ink_px": INK, "margins": margins, "required_min": round(want_clear, 2),
       "ratio": round(min(margins.values()) / INK, 4)})

# declared vs measured ratios on the 512 symbol
xs, ys, xe, ye = L.bbox(MARK)
plate = MARK["params"]["plate"]
offset = MARK["params"]["offset"]
core = plate - offset
k512 = INK / max(xe - xs, ye - ys)
meas = {"ink_w": bb_c[2] - bb_c[0], "ink_h": bb_c[3] - bb_c[1],
        "void_w": hb_c[2] - hb_c[0], "void_h": hb_c[3] - hb_c[1]}
ratios = {"void/ink": round((hb_c[2] - hb_c[0]) / meas["ink_w"], 4),
          "plate/ink": round(plate / max(xe - xs, ye - ys), 4),
          "offset/ink": round(offset / max(xe - xs, ye - ys), 4),
          "radius/plate": round(MARK["params"]["radius"] / plate, 4),
          "offset/plate": round(offset / plate, 4)}
check("512 symbol: void/ink ratio matches the grid model",
      abs(ratios["void/ink"] - core / max(xe - xs, ye - ys)) < 0.02,
      {"measured": ratios, "grid_px_per_unit": round(k512, 4),
       "expected_void_over_ink": round(core / max(xe - xs, ye - ys), 4)})


# ------------------------------------------------------------------ 5. instances
def instance(im, region, is_mark_px, label):
    px = im.load()
    x0, y0, x1, y1 = region
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if is_mark_px(px[x, y])]
    if not pts:
        check("instance %s" % label, False, "no mark pixels found")
        return None
    bb = (min(p[0] for p in pts), min(p[1] for p in pts),
          max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1)
    hb, nhole = enclosed_hole(lambda x, y: is_mark_px(px[x, y]), bb)
    ink_w, ink_h = bb[2] - bb[0], bb[3] - bb[1]
    out = {"ink_bbox": bb, "ink_w": ink_w, "ink_h": ink_h, "void_bbox": hb,
           "void_w": (hb[2] - hb[0]) if hb else 0,
           "void_h": (hb[3] - hb[1]) if hb else 0,
           "void_px": nhole,
           "void_over_ink": round(((hb[2] - hb[0]) / ink_w), 4) if hb else 0,
           "square_ink": abs(ink_w - ink_h) <= 1,
           "square_void": bool(hb) and abs((hb[2] - hb[0]) - (hb[3] - hb[1])) <= 1}
    return out


def nearest_rule(mark_colors, bg_color):
    """is_mark = at least as close to one of the mark inks as to the local ground.

    Ties (a 50/50 anti-aliased blend) count as material, which closes the AA
    corner pinholes that would otherwise let the flood fill leak out of the
    window through the two reflex corners of the staircase silhouette.
    """
    def d(c, t):
        return sum((a - b) ** 2 for a, b in zip(c[:3], t[:3]))
    return lambda c: min(d(c, m) for m in mark_colors) <= d(c, bg_color)


PAPER = (246, 247, 251)
INDIGO = (67, 56, 202)
CYAN = (34, 211, 238)

banner = files["brand-banner.png"]
poster = files["launch-poster.png"]


def bg_sample(im, region):
    px = im.load()
    return px[region[0] + 1, region[1] + 1][:3]


# region: (x0, y0, x1, y1) searched for the mark; mark inks; ground sampled from
# the region's own top-left pixel
INSTANCES = [
    ("banner left panel (mono on violet, ink 248)", banner, (0, 0, 520, 400), [PAPER]),
    ("poster hero (colour, ink 420)", poster, (200, 150, 880, 660), [INDIGO, CYAN]),
    ("poster top bar (mono on dark, ink 52)", poster, (84, 84, 160, 142), [PAPER]),
    ("poster footer card (mono on dark, ink 96)", poster, (118, 1138, 228, 1248), [PAPER]),
]
inst = {}
for label, im, region, inks in INSTANCES:
    rule = nearest_rule(inks, bg_sample(im, region))
    inst[label] = instance(im, region, rule, label)
    print("   %-46s %s" % (label, json.dumps(inst[label], ensure_ascii=False)))

ref_void = core / max(xe - xs, ye - ys)
bad = []
for label, v in inst.items():
    if not v or not v["void_bbox"]:
        bad.append((label, "no void"))
        continue
    if abs(v["void_over_ink"] - ref_void) > 0.02 or not v["square_ink"] \
            or not v["square_void"]:
        bad.append((label, v["void_over_ink"]))
check("all 4 application marks: same void/ink ratio as the 512 symbol",
      not bad, {"reference_void_over_ink": round(ref_void, 4), "failures": bad,
                "tolerance": "0.02 absolute on void/ink, ink and void both square",
                "instances": {k: (v or {}).get("void_over_ink") for k, v in inst.items()}})

# measured ink sizes must equal the declared ink sizes within 1px
DECL = {"banner left panel (mono on violet, ink 248)": 248.0,
        "poster hero (colour, ink 420)": 420.0,
        "poster top bar (mono on dark, ink 52)": 52.0,
        "poster footer card (mono on dark, ink 96)": 96.0}
mism = []
for label, v in inst.items():
    if v and abs(v["ink_w"] - DECL[label]) > 1.5:
        mism.append((label, v["ink_w"], DECL[label]))
check("declared ink sizes match the rendered pixels", not mism, {"mismatches": mism})

# clearspace actually respected around each instance
CLEAR = []
pb_ = banner.load()
banner_mark_bb = inst["banner left panel (mono on violet, ink 248)"]["ink_bbox"]
gap_l = banner_mark_bb[0]
gap_t = banner_mark_bb[1]
gap_b = 400 - banner_mark_bb[3]
gap_r = 520 - banner_mark_bb[2]
CLEAR.append(("banner mark to panel edges", min(gap_l, gap_t, gap_b, gap_r),
              248 / 9.0))
pp = poster.load()
hero = inst["poster hero (colour, ink 420)"]["ink_bbox"]
top_bar = inst["poster top bar (mono on dark, ink 52)"]["ink_bbox"]
card = inst["poster footer card (mono on dark, ink 96)"]["ink_bbox"]
CLEAR.append(("poster hero to rule/top bar", hero[1] - top_bar[3], 420 / 9.0))
CLEAR.append(("poster footer mark to card edge", min(card[0] - 84, 1266 - card[3]),
              96 / 9.0))
bad_clear = [(n, g, r) for n, g, r in CLEAR if g < r - 1.0]
check("application clearspace >= ink/9", not bad_clear,
      {"measured": [{"where": n, "gap_px": g, "required_px": round(r, 2)}
                    for n, g, r in CLEAR], "failures": bad_clear})

# ------------------------------------------------------------------ 6/7. DSL copy
def dsl_text(fn):
    with open(os.path.join(OUT, fn), encoding="utf-8") as fh:
        return fh.read()


banner_dsl = dsl_text("brand-banner.snapshot")
poster_dsl = dsl_text("launch-poster.snapshot")
COPY = [("brand-banner.snapshot", banner_dsl, ["叠光 Layerlight", "把复杂信息，组织成清晰画面"]),
        ("launch-poster.snapshot", poster_dsl,
         ["2026.11.07 · ONLINE", "OPEN BETA", "layerlight.example.org"])]
missing = []
for fn, text, need in COPY:
    for s in need:
        if s not in text:
            missing.append((fn, s))
check("required copy present in the delivered DSL", not missing,
      {"checked": [(f, n) for f, t, ns in COPY for n in ns], "missing": missing})

imgs = []
for fn in ("symbol-color.snapshot", "symbol-black.snapshot",
           "brand-banner.snapshot", "launch-poster.snapshot"):
    t = dsl_text(fn)
    if "<Image" in t or "dataUri" in t or "http://" in t or "https://" in t:
        imgs.append(fn)
check("no <Image> / external asset in any delivered DSL", not imgs,
      {"offenders": imgs, "tags_used": {
          "symbol-color.snapshot": sorted(set(
              __import__("re").findall(r"<([A-Za-z]+)", dsl_text("symbol-color.snapshot")))),
      }})

check("mark main components <= 6", len(MARK["components"]) <= 6,
      {"count": len(MARK["components"]),
       "roles": [c["role"] for c in MARK["components"]],
       "drawn_rects_per_variant": len(MARK["components"])})

# ------------------------------------------------------------------ report
REPORT["summary"] = {"failed_checks": FAIL, "all_passed": not FAIL,
                     "reference_void_over_ink": round(ref_void, 4)}
with open(os.path.join(VDIR, "report.json"), "w", encoding="utf-8") as fh:
    json.dump(REPORT, fh, ensure_ascii=False, indent=2)
print("\nwrote", os.path.join(VDIR, "report.json"))
print("ALL PASSED" if not FAIL else "FAILED: %s" % FAIL)