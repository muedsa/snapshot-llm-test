"""A14 diagnostic probe 2: does gradientType actually produce a gradient?"""
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

snapkit.configure(TASK, OUT, TMP)
PDIR = os.path.join(TMP, "probe")

HEAD = ('<Snapshot type="png" background="#FFFFFF00">\n<Container width="1200" height="630">\n'
        '<Stack fit="EXPAND">\n')
TAIL = ('<Positioned left="40" top="300" width="400" height="60">'
        '<Text color="#14182EFF" fontSize="28" fontFamily="Inter" text="%s"/>'
        '</Positioned>\n</Stack>\n</Container>\n</Snapshot>')

CASES = {
    "F_no_begin_end":
        '<Positioned left="0" top="0" width="1200" height="630">'
        '<Container width="1200" height="630" gradientType="LINEAR" '
        'gradientColors="#3E49E6FF,#F7F5EFFF" /></Positioned>',
    "G_stops_only":
        '<Positioned left="0" top="0" width="1200" height="630">'
        '<Container width="1200" height="630" gradientType="LINEAR" '
        'gradientColors="#3E49E6FF,#F7F5EFFF" gradientStops="0.0,1.0" /></Positioned>',
    "H_begin_end_xy":
        '<Positioned left="0" top="0" width="1200" height="630">'
        '<Container width="1200" height="630" gradientType="LINEAR" '
        'gradientColors="#3E49E6FF,#F7F5EFFF" gradientBegin="Alignment.topLeft" '
        'gradientEnd="Alignment.bottomRight" /></Positioned>',
    "I_radial":
        '<Positioned left="0" top="0" width="1200" height="630">'
        '<Container width="1200" height="630" gradientType="RADIAL" '
        'gradientColors="#3E49E6FF,#F7F5EFFF" /></Positioned>',
}


def sample(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    pts = [(0, 0), (300, 150), (600, 315), (900, 480), (1199, 629)]
    return [(p, px[p]) for p in pts]


for k in sorted(CASES):
    dsl = HEAD + CASES[k] + "\n" + (TAIL % k) + "\n"
    r = snapkit.render(dsl, "grad-%s.png" % k, "grad-%s.snapshot" % k,
                       final=False, out_dir=PDIR)
    print("===", k, "ok=%s" % r.get("ok"), r.get("status"))
    if r.get("ok"):
        for p, c in sample(r["image"]):
            print("   ", p, c)
    else:
        print("   ", (r.get("error") or "")[:300])