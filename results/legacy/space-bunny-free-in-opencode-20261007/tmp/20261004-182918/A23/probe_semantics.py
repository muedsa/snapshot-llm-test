"""A23 step 2: verify Transform rotation-about-centre semantics and true transparency.

Both are load-bearing for the 6-frame build, so they get their own real-service probes.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import state as S  # noqa: E402
from PIL import Image  # noqa: E402

TASK = "A23"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)


def el(tag, a, kids=None, text=None):
    head = "<%s%s" % (tag, "".join(' %s="%s"' % (k, v) for k, v in a.items() if v is not None))
    if text is not None:
        head += ' text="%s"' % text
    if not kids:
        return head + " />"
    return head + ">\n" + "\n".join(kids) + "\n</%s>" % tag


def mat(deg):
    import math
    t = math.radians(deg)
    c, s = round(math.cos(t), 6), round(math.sin(t), 6)
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (c, -s, s, c)


# r1: capsule rotated 0/30/60/90 deg, each at a KNOWN cell centre, on an opaque board
kids = []
deg = 0
for i in range(4):
    cx, cy = 100 + i * 200, 100
    kids.append(el("Positioned", {"left": cx - 60, "top": cy - 20, "width": 120, "height": 40},
                   [el("Transform", {"matrix": mat(deg), "origin": "(0,0)", "alignment": "CENTER"},
                       [el("Container", {"width": 120, "height": 40, "color": "#E11D48FF",
                                         "borderRadius": "20"})])]))
    deg += 30
# reference outlines (unrotated) so rotation is measurable
for i in range(4):
    cx = 100 + i * 200
    kids.append(el("Positioned", {"left": cx - 60, "top": 80, "width": 120, "height": 40},
                   [el("Container", {"width": 120, "height": 40, "color": "#0F172A22"})]))

dsl = ('<Snapshot type="png" background="#FFFFFFFF">\n'
       + el("Container", {"width": 800, "height": 200},
           [el("Stack", {"fit": "EXPAND"}, kids)])
       + "\n</Snapshot>\n")
r = snapkit.render(dsl, "q1-rotation.png", "q1-rotation.snapshot", final=False)
print("q1-rotation:", r["ok"], r["status"], r.get("error"))

# measure bounding box of the rotated red capsules: proves rotation happens about the centre
im = Image.open(r["image"]).convert("RGB")
px = im.load()
W, H = im.size
for i in range(4):
    x0, x1 = i * 200, i * 200 + 200
    ys = [y for y in range(H) for x in range(x0, x1) if px[x, y][0] > 180 and px[x, y][1] < 90]
    xs = [x for y in range(H) for x in range(x0, x1) if px[x, y][0] > 180 and px[x, y][1] < 90]
    if ys:
        print("  cell %d deg=%-3d red-pixel bbox x[%d..%d] w=%d  y[%d..%d] h=%d  centroid=(%.1f, %.1f)"
              % (i, i * 30, min(xs), max(xs), max(xs) - min(xs) + 1,
                 min(ys), max(ys), max(ys) - min(ys) + 1,
                 (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2))
    else:
        print("  cell %d: no red pixels" % i)

# r2: transparency truth test -- default <Snapshot> background, opaque bar in the middle
dsl2 = ('<Snapshot>\n'
        + el("Container", {"width": 200, "height": 120},
            [el("Stack", {"fit": "EXPAND"},
                [el("Positioned", {"left": 70, "top": 40, "width": 60, "height": 40},
                    [el("Container", {"width": 60, "height": 40, "color": "#38BDF8FF"})])])])
        + "\n</Snapshot>\n")
r2 = snapkit.render(dsl2, "q2-transparent.png", "q2-transparent.snapshot", final=False)
print("q2-transparent:", r2["ok"], r2["status"], r2.get("error"))
im2 = Image.open(r2["image"])
print("  mode=%s size=%s format=%s" % (im2.mode, im2.size, im2.format))
rgba = im2.convert("RGBA")
print("  corner(2,2)=%s  bar(100,60)=%s  alpha-extremes=%s"
      % (rgba.getpixel((2, 2)), rgba.getpixel((100, 60)),
         (min(p[3] for p in rgba.getdata()), max(p[3] for p in rgba.getdata()))))

# r3: explicit #00000000 background must equal the default
dsl3 = dsl2.replace("<Snapshot>", '<Snapshot type="png" background="#00000000">')
r3 = snapkit.render(dsl3, "q3-transparent-explicit.png", "q3-transparent-explicit.snapshot", final=False)
print("q3-transparent-explicit:", r3["ok"], r3["status"], r3.get("error"))
im3 = Image.open(r3["image"]).convert("RGBA")
print("  corner=%s bar=%s  identical_bytes=%s"
      % (im3.getpixel((2, 2)), im3.getpixel((100, 60)),
         open(r2["image"], "rb").read() == open(r3["image"], "rb").read()))

# r4: CJK legibility at cover title size, real font families from /fonts
fams = open(os.path.join(TMP, "fonts-list.txt"), encoding="utf-8").read().split()
print("  /fonts families=%d  has Noto Sans CJK SC=%s" % (len(fams), "Noto Sans CJK SC" in fams))
rows = []
for i, fam in enumerate(["Noto Sans CJK SC", "Inter,Noto Sans CJK SC", "Noto Serif CJK SC"]):
    rows.append(el("Positioned", {"left": 20, "top": 16 + i * 60, "width": 660, "height": 52},
                   [el("Text", {"color": "#F8FAFCFF", "fontSize": "40", "fontFamily": fam},
                       text="从结构到画面 · 结构汇聚成图像")]))
r4 = snapkit.render('<Snapshot type="png" background="#0B1220FF">\n'
                    + el("Container", {"width": 700, "height": 200},
                        [el("Stack", {"fit": "EXPAND"}, rows)])
                    + "\n</Snapshot>\n",
                    "q4-cjk.png", "q4-cjk.snapshot", final=False)
print("q4-cjk:", r4["ok"], r4["status"], r4.get("error"))
