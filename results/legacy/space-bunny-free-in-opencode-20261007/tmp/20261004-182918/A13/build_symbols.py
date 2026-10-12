# -*- coding: utf-8 -*-
"""A13 step 2 driver (refined mark):
  python build_symbols.py <tag> <radius> <offset> <plate> <origin> [mode] [--final]
  mode = void | solid     (void = final negative-space mark, solid = pre-refinement)
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import layerlight as L  # noqa: E402

TASK = "A13"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

a = [v for v in sys.argv[1:] if not v.startswith("--")]
tag = a[0]
radius = float(a[1]) if len(a) > 1 else 60.0
offset = float(a[2]) if len(a) > 2 else 150.0
plate = float(a[3]) if len(a) > 3 else 300.0
origin = float(a[4]) if len(a) > 4 else 6.0
mode = a[5] if len(a) > 5 else "void"
sharp_void = ("round" not in (a[6] if len(a) > 6 else "sharp"))
FINAL = "--final" in sys.argv

DIR = OUT if FINAL else os.path.join(TMP, "preview", tag)
os.makedirs(DIR, exist_ok=True)

if mode == "void":
    mark = L.build_mark(plate=plate, radius=radius, offset=offset, origin=origin,
                        sharp_void=sharp_void)
    colors = L.MARK_ROLE_COLOR
else:
    mark = L.build_dir_a(plate=plate, radius=radius, offset=offset, origin=origin)
    colors = L.ROLE_COLOR["A"]

CLEAR = 512.0 / 9.0   # clearspace = 1/9 of the grid on every side


def symbol(size, cols):
    ink = size - 2 * (CLEAR / 512.0) * size
    ox, oy, k = L.fitted(mark, size / 2.0, size / 2.0, ink)
    parts = L.emit(mark, ox, oy, k, cols, gradient=None)
    return D.snapshot([D.stack(parts, size, size)], size, size, bg="#00000000"), (ox, oy, k)


print("mode", mode, "params", mark.get("params"), "final", FINAL)
if "void" in mark:
    print("void", mark["void"])

for name, cols in (("symbol-color.png", colors), ("symbol-black.png", L.mono_colors(mark))):
    dsl, geom = symbol(512, cols)
    with open(os.path.join(TMP, "drafts", "%s-%s" % (tag, name.replace(".png", ".snapshot"))),
              "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name, name.replace(".png", ".snapshot"), final=FINAL, out_dir=DIR)
    print("%-18s ok=%s status=%s bytes=%s ink=%s" % (
        name, r.get("ok"), r.get("status"), r.get("bytes"), L.ink_box(mark, *geom)))
    if not r.get("ok"):
        print(r.get("error"))

if not FINAL:
    for size in (32, 48, 64):
        for nm, cols in (("color", colors), ("black", L.mono_colors(mark))):
            dsl, geom = symbol(size, cols)
            nm2 = "check-%s-%dx%d.png" % (nm, size, size)
            r = snapkit.render(dsl, nm2, nm2.replace(".png", ".snapshot"), final=False,
                               out_dir=os.path.join(TMP, "preview", tag, "checksize"))
            print("%-22s ok=%s status=%s" % (nm2, r.get("ok"), r.get("status")))
            if not r.get("ok"):
                print(r.get("error"))

for w in D.warnings():
    print("WARN", w)