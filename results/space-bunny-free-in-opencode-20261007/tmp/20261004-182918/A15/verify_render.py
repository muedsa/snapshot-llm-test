"""A15 verifier: measure reconstructed.png with exactly the same code used on
reference.png, then

  1. write text-offsets.json  -> the measured (dx, dy) ink offset per text element,
     so the next build places each glyph box exactly on the reference ink position;
  2. print a per-text delta table (reference ink vs reconstructed ink);
  3. print / write the 22 structural anchor deltas required by TASK.md.
"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
OUT = os.path.join(ROOT, "outputs", RUN, "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
sys.path.insert(0, TMP)
import spec_a15 as S  # noqa: E402


def rgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def ink_box(px, W, H, x0, x1, y0, y1, bg, tol):
    bgc = rgb(bg)
    minx = miny = maxx = maxy = None
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            if sum(abs(px[x, y][i] - bgc[i]) for i in range(3)) > tol:
                minx = x if minx is None else min(minx, x)
                maxx = x if maxx is None else max(maxx, x)
                miny = y if miny is None else min(miny, y)
                maxy = y if maxy is None else max(maxy, y)
    if minx is None:
        return None
    return {"bbox": [minx, miny, maxx, maxy], "w": maxx - minx + 1,
            "h": maxy - miny + 1}


def scan(path):
    im = Image.open(path).convert("RGB")
    px = im.load()
    out = {}
    for key, (x0, x1, y0, y1, bg, tol) in S.REGIONS.items():
        out[key] = ink_box(px, im.size[0], im.size[1], x0, x1, y0, y1, bg, tol)
    return out, im


def anchors(path):
    """Structural anchors located by exact-colour probes, so the identical routine
    measures both reference.png and reconstructed.png."""
    im = Image.open(path).convert("RGB")
    px = im.load()

    def run_h(y, color, x0, x1):
        """(first, last) x of an exactly-matching horizontal run."""
        c = rgb(color)
        xs = [x for x in range(x0, x1) if px[x, y] == c]
        return (min(xs), max(xs)) if xs else (None, None)

    def run_v(x, color, y0, y1):
        c = rgb(color)
        ys = [y for y in range(y0, y1) if px[x, y] == c]
        return (min(ys), max(ys)) if ys else (None, None)

    def ink_px(x, y):
        return px[x, y]

    R = {}
    R["A01_sidebar_right_edge"] = run_h(450, "#14233C", 0, 300)[1]
    R["A02_table_card_br"] = [run_h(700, "#E2E8F1", 230, 1440)[1],
                              run_v(700, "#E2E8F1", 610, 860)[1]]
    R["A03_kpi1_top_border_y"] = run_v(700, "#E2E8F1", 120, 300)[0]
    R["A04_kpi1_left_x"] = run_h(250, "#E2E8F1", 230, 1440)[0]
    R["A05_kpi3_right_x"] = run_h(250, "#E2E8F1", 230, 1440)[1]
    R["A06_chart_card_left_x"] = run_h(450, "#E2E8F1", 230, 1030)[0]
    R["A07_chart_card_right_x"] = run_h(450, "#E2E8F1", 995, 1035)[0]
    R["A08_chart_card_top_y"] = run_v(500, "#E2E8F1", 295, 610)[0]
    R["A09_chart_card_bottom_y"] = run_v(500, "#E2E8F1", 295, 610)[1]
    R["A10_act_card_left_x"] = run_h(450, "#E2E8F1", 1002, 1440)[0]
    R["A11_act_card_right_x"] = run_h(450, "#E2E8F1", 1002, 1440)[1]
    R["A12_zero_gridline_y"] = run_v(352, "#E7EDF5", 380, 570)[1]
    R["A13_grid_top_y"] = run_v(352, "#E7EDF5", 380, 570)[0]
    R["A14_grid_x_extent"] = list(run_h(549, "#E7EDF5", 280, 1000))
    R["A15_grid_y449"] = run_v(352, "#E7EDF5", 430, 460)[0]
    R["A16_bar1_left_x"] = run_h(520, "#245CE4", 300, 450)[0]
    R["A17_bar1_top_y"] = run_v(383, "#245CE4", 400, 560)[0]
    R["A18_bar4_top_y"] = run_v(686, "#245CE4", 400, 560)[0]
    R["A19_bar6_right_x"] = run_h(460, "#245CE4", 830, 1000)[1]
    R["A20_bar6_top_y"] = run_v(888, "#245CE4", 400, 560)[0]
    R["A21_table_card_top_y"] = run_v(700, "#E2E8F1", 610, 700)[0]
    R["A22_table_card_bottom_y"] = run_v(700, "#E2E8F1", 800, 870)[1]
    R["A23_thead_band_left_x"] = run_h(700, "#F3F6FB", 262, 1398)[0]
    R["A24_thead_band_right_x"] = run_h(700, "#F3F6FB", 262, 1398)[1]
    R["A25_thead_band_top_y"] = run_v(700, "#F3F6FB", 676, 724)[0]
    R["A26_thead_band_bottom_y"] = run_v(700, "#F3F6FB", 676, 724)[1]
    R["A27_rowsep760"] = list(run_h(760, "#EBEFF5", 262, 1398))
    R["A28_rowsep795_y"] = run_v(700, "#EBEFF5", 780, 810)[0]
    R["A29_pill1_left_x"] = run_h(742, "#E7EFFF", 1010, 1200)[0]
    R["A30_pill1_top_y"] = run_v(1100, "#E7EFFF", 720, 762)[0]
    R["A31_pill3_top_y"] = run_v(1100, "#DCF5EC", 780, 845)[0]
    R["A32_nav_pill_left_x"] = run_h(134, "#294467", 0, 219)[0]
    R["A33_nav_pill_bottom_y"] = run_v(60, "#294467", 100, 180)[1]
    R["A34_logo_left_x"] = run_h(46, "#64DBB6", 0, 80)[0]
    R["A35_logo_top_y"] = run_v(33, "#64DBB6", 20, 80)[0]
    R["A36_sidecard_left_x"] = run_h(800, "#233954", 0, 219)[0]
    R["A37_sidecard_top_y"] = run_v(100, "#233954", 730, 790)[0]
    R["A38_button_left_x"] = run_h(62, "#245CE4", 1150, 1440)[0]
    R["A39_button_top_y"] = run_v(1290, "#245CE4", 30, 110)[0]
    R["A40_act_dot1_left_x"] = run_h(401, "#EAAF40", 1040, 1075)[0]
    R["A41_act_dot3_left_x"] = run_h(521, "#168267", 1040, 1075)[0]
    R["A42_footer_band_bg"] = hx(px[1300, 890])
    R["A43_main_bg_right_margin"] = hx(px[1420, 500])
    R["A44_sidebar_bg"] = hx(px[110, 450])
    R["A45_card_fill"] = hx(px[700, 330])
    R["A46_card_border"] = hx(px[260, 450])
    R["A47_grid_color"] = hx(px[352, 549])
    R["A48_bar_color"] = hx(px[383, 520])
    R["A49_thead_bg"] = hx(px[700, 692])
    R["A50_rowsep_color"] = hx(px[700, 760])
    return R


def hx(c):
    return "#%02X%02X%02X" % c


ref_ink, _ = scan(REF)
ref_anchor = anchors(REF)

target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, "reconstructed.png")
got_ink, got_im = scan(target)
got_anchor = anchors(target)
layout = json.load(open(os.path.join(TMP, "layout.json"), encoding="utf-8"))["text_layout"]

offsets = {}
rows = []
for key, lay in layout.items():
    if key not in S.REGIONS:
        continue
    g = got_ink.get(key)
    if g is None:
        rows.append((key, lay["text"], None, None, None, None))
        continue
    dx = g["bbox"][0] - lay["box"][0]
    dy = g["bbox"][1] - lay["box"][1]
    offsets[key] = [dx, dy]
    r = ref_ink.get(key)
    rows.append((key, lay["text"],
                 r["bbox"][0] if r else None, g["bbox"][0],
                 r["bbox"][1] if r else None, g["bbox"][1],
                 r["w"] if r else None, g["w"], r["h"] if r else None, g["h"]))

json.dump(offsets, open(os.path.join(TMP, "text-offsets.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("== text ink deltas (ref vs reconstructed: left/top position, width/height size) ==")
print("%-14s %-28s %5s %5s %3s %5s %5s %3s %4s %4s %3s" %
      ("key", "text", "refL", "gotL", "dL", "refT", "gotT", "dT",
       "refW", "gotW", "dW"))
bad = 0
for row in rows:
    key, s, rl, gl, rt, gt = row[:6]
    rw, gw, rh, gh = row[6], row[7], row[8], row[9]
    if rl is None or gl is None:
        print("%-14s %-28s  MISSING" % (key, s[:28]))
        bad += 1
        continue
    dl, dt, dw = gl - rl, gt - rt, gw - rw
    flag = "" if (abs(dl) <= 3 and abs(dt) <= 3 and abs(dw) <= 4) else "  <<"
    if flag:
        bad += 1
    print("%-14s %-28s %5d %5d %3d %5d %5d %3d %4d %4d %3d%s" %
          (key, s[:28], rl, gl, dl, rt, gt, dt, rw, gw, dw, flag))
print("out-of-tolerance (pos>3px or width>4px):", bad)

print()
print("== structural anchors (exact-colour probes) ==")
worst = []
for key in sorted(ref_anchor):
    rv, gv = ref_anchor[key], got_anchor.get(key)
    if isinstance(rv, list) or isinstance(gv, list):
        if rv and gv and len(rv) == len(gv):
            d = [None if a is None or b is None else b - a for a, b in zip(rv, gv)]
        else:
            d = None
    elif isinstance(rv, str) and isinstance(gv, str):
        d = None
    elif rv is None or gv is None:
        d = None
    else:
        d = gv - rv
    ds = "" if d is None else str(d)
    if d is not None:
        worst += [abs(v) for v in (d if isinstance(d, list) else [d]) if v is not None]
    print("%-26s ref=%-14s got=%-14s delta=%-8s" % (key, rv, gv, ds))
print("max |anchor delta| =", max(worst) if worst else "n/a")

json.dump({"reference_anchor": ref_anchor, "reconstructed_anchor": got_anchor,
           "text_ink_delta": [
               {"key": r[0], "text": r[1], "ref_left": r[2], "got_left": r[3],
                "ref_top": r[4], "got_top": r[5],
                "d_left": None if r[2] is None or r[3] is None else r[3] - r[2],
                "d_top": None if r[4] is None or r[5] is None else r[5] - r[4],
                "ref_w": r[6], "got_w": r[7], "d_w": None if r[6] is None else r[7] - r[6],
                "ref_h": r[8], "got_h": r[9], "d_h": None if r[8] is None else r[9] - r[8]}
               for r in rows],
           "text_offsets": offsets},
          open(os.path.join(TMP, "verify.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nsize:", got_im.size)
