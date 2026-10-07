import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A18"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

snapkit.configure(TASK, OUT, TMP)

W, H = 1000, 700
cx, cy = 500, 360
kids = []
kids.append(D.box(0, 0, W, H, color="#0B1220FF"))
kids.append(D.box(cx - 1, cy - 1, 2, 2, color="#FF0000FF"))


def seg_rot(x0, y0, x1, y1, t, color):
    """One element: rotated rect centred on the segment midpoint."""
    import math
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    phi = math.atan2(dy, dx)
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    m = "(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,0,0,0,1)" % (
        math.cos(phi), math.sin(phi), -math.sin(phi), math.cos(phi))
    return D.box(mx - L / 2.0, my - t / 2.0, L, t, color=color,
                 extra={"transform": m, "transformAlignment": "CENTER"})


# A: rotated Container transform, four spokes at known angles
for ang, col in ((0, "#38BDF8FF"), (90, "#F97316FF"), (180, "#34D399FF"), (270, "#F472B6FF")):
    import math
    a = math.radians(ang)
    kids.append(seg_rot(cx, cy, cx + 250 * math.cos(a), cy + 250 * math.sin(a), 6, col))
# B: same with <Transform> tag wrapper
import math
for ang, col in ((30, "#E2E8F0FF"), (210, "#E2E8F0FF")):
    a = math.radians(ang)
    x1, y1 = cx + 220 * math.cos(a), cy + 220 * math.sin(a)
    kids.append(seg_rot(cx, cy, x1, y1, 10, col))
# C: radial gradient glow
kids.append(D.box(cx - 140, cy - 140, 280, 280, radius=140,
                  gradient={"gradientType": "RADIAL",
                            "gradientColors": "#F9731699,#F9731600",
                            "gradientCenter": "CENTER", "gradientRadius": "0.5"}))
# D: thick border ring
kids.append(D.box(cx - 120, cy - 120, 240, 240, radius=120,
                  border="8 SOLID #38BDF866"))
# E: unit discs
for i, (dx, dy, col) in enumerate([(0, -100, "#2563EBFF"), (100, 0, "#F97316FF"),
                                   (0, 100, "#94A3B8FF"), (-100, 0, "#22C55EFF")]):
    kids.append(D.box(cx + dx - 18, cy + dy - 18, 36, 36, radius=18, color=col))
# F: text with mono + cjk
kids.append(D.text_el("MONO 15 = 5B + 5O + 5G", x=40, y=40, w=400, h=26,
                      size=20, color="#E2E8F0FF", font=D.MONO))
kids.append(D.text_el("第一幕 · 集中", x=40, y=80, w=400, h=32,
                      size=26, color="#F8FAFCFF", font=D.CJK))
kids.append(D.text_el("ABCDEFGHIJKLM", x=40, y=120, w=400, h=26,
                      size=20, color="#94A3B8FF", font=D.CJK,
                      extra={"fontFeatures": "tnum=2"}))
# G: dashed rule
kids.append(D.dashed(40, 460, 170, "#64748BFF", 2, 8, 6))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#0B1220FF")
os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)
with open(os.path.join(TMP, "drafts", "v00-probe.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "probe01.png", "probe01.snapshot", final=False)
print(json.dumps(r, ensure_ascii=False))
for w in D.warnings():
    print("WARN", w)