"""A15 probe: is there ANY attribute spelling that changes glyph weight on the
Inter family?  Unknown attributes are silently ignored (DSL-HANDBOOK section 3),
so this must be measured, not assumed.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
from PIL import Image  # noqa: E402

snapkit.configure("A15", os.path.join(ROOT, "outputs", RUN, "A15"), TMP)

TEXT = "Workspace Overview"
SIZE = 33
TEXTW = 620

VARIANTS = [
    ("baseline-Inter", {}),
    ("fontWeight-700", {"fontWeight": "700"}),
    ("fontWeight-bold", {"fontWeight": "bold"}),
    ("fontWeight-BOLD", {"fontWeight": "BOLD"}),
    ("font-weight-700", {"font-weight": "700"}),
    ("weight-700", {"weight": "700"}),
    ("fontStyle-ITALIC", {"fontStyle": "ITALIC"}),
    ("fontWeight-600", {"fontWeight": "600"}),
    ("fontWeight-900", {"fontWeight": "900"}),
    ("family-InterBold", {"fontFamily": "Inter Bold"}),
    ("family-InterBold600", {"fontFamily": "Inter,Inter Bold"}),
    ("family-SemiBold", {"fontFamily": "Inter Semi Bold"}),
    ("family-ExtraBold", {"fontFamily": "Inter Extra Bold"}),
    ("family-Black", {"fontFamily": "Inter Black"}),
    ("family-Bold", {"fontFamily": "Inter Bold,Inter Semi Bold"}),
]

kids = []
for i, (name, extra) in enumerate(VARIANTS):
    y = 8 + i * 55
    e = dict(extra)
    if "fontFamily" in e:
        e["fontFamily"] = e["fontFamily"]
    else:
        e["fontFamily"] = "Inter"
    kids.append(D.box(20, y, 900, 50, color="#FFFFFFFF"))
    kids.append(D.text_el(TEXT, x=30, y=y + 2, w=TEXTW, h=48, color="#18283FFF",
                          size=SIZE, font=e.pop("fontFamily", "Inter"),
                          extra=e or None))

dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
r = snapkit.render(dsl, "weight-probe.png", "weight-probe.snapshot", final=False,
                   out_dir=os.path.join(TMP, "probes"))
print(r)
for w in D.warnings():
    print("WARN", w)
im = Image.open(r["image"]).convert("L")
px = im.load()
base = 255
print("variant                 density   inkW  inkH")
for i, (name, _) in enumerate(VARIANTS):
    y = 8 + i * 55
    d = 0
    minx = miny = maxx = maxy = None
    for yy in range(y, y + 50):
        for x in range(25, 940):
            dd = base - px[x, yy]
            if dd > 0:
                d += dd
                minx = x if minx is None else min(minx, x)
                maxx = x if maxx is None else max(maxx, x)
                miny = yy if miny is None else min(miny, yy)
                maxy = yy if maxy is None else max(maxy, yy)
    print("%-22s %8d %5d %5d" % (name, d, maxx - minx + 1, maxy - miny + 1))
