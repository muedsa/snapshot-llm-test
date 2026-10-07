# -*- coding: utf-8 -*-
"""A13: build the 32x32 thumbnail check sheet from the DELIVERED symbol files.

Inspection preview only - it lives in the temp dir and is never a deliverable.
Left half: the service-rendered 32x32 (same emit() code path, rendered at 32px).
Right half: a LANCZOS downscale of the delivered 512 PNG.
"""
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsllib as D  # noqa: E402
import layerlight as L  # noqa: E402
import snapkit  # noqa: E402
import state as S  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
CHK = os.path.join(TMP, "preview", "final", "checksize")
os.makedirs(CHK, exist_ok=True)

CLEAR = 512.0 / 9.0
for nm, cols in (("color", L.MARK_ROLE_COLOR), ("black", L.mono_colors(L.MARK))):
    ink = 32 - 2 * (CLEAR / 512.0) * 32
    ox, oy, k = L.fitted(L.MARK, 16.0, 16.0, ink)
    dsl = D.snapshot([D.stack(L.emit(L.MARK, ox, oy, k, cols), 32, 32)], 32, 32,
                     bg="#00000000")
    fn = "thumb-%s-32x32.png" % nm
    r = snapkit.render(dsl, fn, fn.replace(".png", ".snapshot"), final=False, out_dir=CHK)
    print("%-24s ok=%s status=%s" % (fn, r.get("ok"), r.get("status")))

Z = 14
cols, labels = [], []
for tag, nm in (("rendered at 32px", "color"), ("delivered 512 -> 32px", "color"),
                ("rendered at 32px", "black"), ("delivered 512 -> 32px", "black")):
    if tag.startswith("rendered"):
        p = os.path.join(CHK, "thumb-%s-32x32.png" % nm)
    else:
        p = os.path.join(OUT, "symbol-%s.png" % nm)
    im = Image.open(p).convert("RGBA")
    if tag.startswith("delivered"):
        im = im.resize((32, 32), Image.LANCZOS)
    base = Image.new("RGB", (32, 32), (255, 255, 255))
    base.paste(im, (0, 0), im)
    cols.append(base.resize((32 * Z, 32 * Z), Image.NEAREST))
    labels.append("%s / %s" % (nm, tag))
sheet = Image.new("RGB", (32 * Z * 4 + 5 * 24, 32 * Z + 48), (233, 236, 243))
for i, c in enumerate(cols):
    sheet.paste(c, (24 + i * (32 * Z + 24), 24))
out = os.path.join(TMP, "preview", "final", "thumb32-check.png")
sheet.save(out)
with open(os.path.join(TMP, "preview", "final", "thumb32-check-labels.txt"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join("panel %d (left to right): %s" % (i + 1, lb)
                       for i, lb in enumerate(labels)) + "\n")
print("wrote", out, sheet.size)
print("panels:", labels)