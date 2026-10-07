# -*- coding: utf-8 -*-
"""A13 step 1: two genuinely different geometric directions, each rendered as a
512x512 transparent PNG and kept in the temp dir (task requires both previews)."""
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
PREVIEW = os.path.join(TMP, "preview")
DRAFTS = os.path.join(TMP, "drafts")
for p in (PREVIEW, DRAFTS):
    os.makedirs(p, exist_ok=True)

SIZE = 512
results = {}
for key in ("A", "B"):
    direction = L.DIRECTIONS[key]
    # centre the ink in the canvas and keep a 56px clearspace margin
    ox, oy, k = L.fitted(direction, SIZE / 2.0, SIZE / 2.0, SIZE - 2 * 56)
    parts = L.emit(direction, ox, oy, SIZE, L.color_colors(direction),
                   gradient=L.CORE_GRADIENT_COLOR)
    dsl = D.snapshot([D.stack(parts, SIZE, SIZE)], SIZE, SIZE, bg="#00000000")
    name = "direction-%s.png" % key
    with open(os.path.join(DRAFTS, "v02-dir-%s.snapshot" % key), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name, "direction-%s.snapshot" % key,
                       final=False, out_dir=PREVIEW)
    print("dir %s ok=%s status=%s bytes=%s ink=%s" % (
        key, r.get("ok"), r.get("status"), r.get("bytes"), L.ink_box(direction, ox, oy, k)))
    if not r.get("ok"):
        print(r.get("error"))
    results[key] = r.get("image")
    for w in D.warnings():
        print("WARN", w)
print(results)