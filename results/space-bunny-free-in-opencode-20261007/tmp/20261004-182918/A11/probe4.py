"""A11 probe 4: measurement rig so that space counts can be proven from pixels.

Rows are laid out one per line with a clean reference glyph 'X' after a variable
number of spaces. Measuring ink-run edges gives the rendered space advance, and
then the real literal line can be checked against an integral number of spaces.
"""
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A11")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A11")
snapkit.configure("A11", OUT, TMP)

W, H = 1200, 1260
UI = "Inter,Noto Sans CJK SC"
kids = []
y = 20
ROWS = []


def put(text, size, font=UI, x=20):
    global y
    kids.append(D.el("Positioned", {"left": x, "top": y, "width": 1150},
                     [D.el("Text", {"color": "#111827FF", "fontSize": size,
                                    "fontFamily": font}, [D.cdata(text)])]))
    ROWS.append((text, y, size, font))
    y += int(size * 1.55) + 12


for n in range(4):
    put("X" + " " * n + "X", 56)
put("XX", 56)
y += 10
for n in range(4):
    put("批次：" + " " * n + "X", 56)
put("批次：  A  07", 56)
put("批次：  A  07", 30)
put("Path: C:\\work\\cards\\v2", 30, "DejaVu Sans Mono,Noto Sans Mono CJK SC")
put("O0-I1-B8", 30, "Inter")

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
with open(os.path.join(TMP, "drafts", "probe-v04.snapshot"), "w",
          encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "probe-04.png", "probe-04.snapshot", final=False,
                   out_dir=os.path.join(TMP, "preview"))
print("render", r)
with open(os.path.join(TMP, "probe04-rows.json"), "w", encoding="utf-8") as fh:
    json.dump(ROWS, fh, ensure_ascii=False, indent=1)
for i, (t, yy, s, f) in enumerate(ROWS):
    print(i, repr(t), "top=", yy, "size=", s, "font=", f,
          "band=", (yy + 3, yy + 3 + int(s * 1.05)))
print("WARN", D.warnings())