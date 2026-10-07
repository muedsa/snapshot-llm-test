# -*- coding: utf-8 -*-
"""A13 probe 1: does the service produce a real alpha channel, and which
circle/rounded-rect spellings work?  One render, four panels, PIL-checked."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
os.makedirs(os.path.join(TMP, "probes"), exist_ok=True)
os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)

W, H = 900, 300
kids = []

# A: plain opaque rounded rect on a transparent background
kids.append(D.box(40, 40, 200, 200, color="#6366F1FF", radius=60))

# B: circle via ClipOval > ColoredBox
kids.append(D.el("Positioned", {"left": 300, "top": 40, "width": 200, "height": 200},
                 [D.el("ClipOval", {}, [D.el("ColoredBox", {"color": "#22D3EEFF"})])]))

# C: circle via Container shape=CIRCLE
kids.append(D.box(560, 40, 200, 200, color="#F472B6FF", extra={"shape": "CIRCLE"}))

# D: rounded rect with a LINEAR gradient
kids.append(D.box(790, 40, 70, 200, color=None, radius=30,
                  gradient={"gradientType": "LINEAR",
                            "gradientColors": "#4F46E5FF,#22D3EEFF",
                            "gradientStops": "0,1",
                            "gradientBegin": "TOP_CENTER",
                            "gradientEnd": "BOTTOM_CENTER"}))

# E: ClipRRect > Container (nested clip) - used later for the plate/lens hole trick
kids.append(D.el("Positioned", {"left": 40, "top": 250, "width": 60, "height": 40},
                 [D.el("ClipRRect", {"borderRadius": "20"},
                       [D.el("ColoredBox", {"color": "#FACC15FF"})])]))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#00000000")
with open(os.path.join(TMP, "drafts", "v01-probe-alpha.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)

r = snapkit.render(dsl, "probe-alpha.png", "probe-alpha.snapshot",
                   final=False, out_dir=os.path.join(TMP, "probes"))
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
for w in D.warnings():
    print("WARN", w)

if r.get("ok"):
    from PIL import Image
    im = Image.open(r["image"])
    print("mode", im.mode, "size", im.size)
    px = im.convert("RGBA").load()
    pts = {"corner(2,2)": (2, 2), "mid-gap(280,150)": (280, 150),
           "A-centre(140,140)": (140, 140), "B-centre(400,140)": (400, 140),
           "C-centre(660,140)": (660, 140), "D-centre(825,140)": (825, 140),
           "D-corner(800,45)": (800, 45), "E-clip(70,270)": (70, 270)}
    for k, (x, y) in pts.items():
        print("  %-20s -> %s" % (k, px[x, y]))
    a = im.convert("RGBA").split()[3]
    print("alpha min/max:", a.getextrema())