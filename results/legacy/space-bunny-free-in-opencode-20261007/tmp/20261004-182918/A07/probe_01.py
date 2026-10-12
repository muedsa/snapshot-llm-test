"""A07 probe: verify Transform matrix rotation direction, Container shape=CIRCLE + border,
and glyph coverage for check/cross marks. Rendered to temp preview only."""
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A07"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 900, 560


def rot_bar(x0, y0, x1, y1, color, w=10.0):
    """Horizontal bar rotated so it spans (x0,y0)->(x1,y1)."""
    L = math.hypot(x1 - x0, y1 - y0)
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    th = -math.degrees(math.atan2(y1 - y0, x1 - x0))
    a = round(math.cos(math.radians(th)), 6)
    b = round(-math.sin(math.radians(th)), 6)
    c = round(math.sin(math.radians(th)), 6)
    d = round(math.cos(math.radians(th)), 6)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (a, b, c, d)
    inner = D.el("Container", {"width": round(L, 2), "height": w, "color": color,
                                "borderRadius": w / 2.0})
    tr = D.el("Transform", {"matrix": m, "alignment": "CENTER"}, [inner])
    return D.el("Positioned", {"left": round(mx - L / 2.0, 2), "top": round(my - w / 2.0, 2),
                               "width": round(L, 2), "height": w}, [tr])


kids = [D.box(0, 0, W, H, color="#FFFFFFFF")]
# 1. rotation: 4 bars radiating from a hub
hub = (200, 200)
kids.append(D.box(hub[0] - 6, hub[1] - 6, 12, 12, color="#0F172AFF", extra={"shape": "CIRCLE"}))
targets = [(400, 200), (200, 420), (360, 40), (40, 360)]
for i, (tx, ty) in enumerate(targets):
    kids.append(rot_bar(hub[0], hub[1], tx, ty, ["#DC2626FF", "#2563EBFF", "#16A34AFF", "#CA8A04FF"][i]))
kids.append(D.text_el("hub (200,200)", x=140, y=440, w=200, h=30, size=20))
kids.append(D.text_el("0deg=E 90deg=S 135deg=SE 225deg=SW", x=140, y=474, w=420, h=30, size=20))

# 2. shape=CIRCLE with border
kids.append(D.box(470, 40, 40, 40, color="#FFFFFFFF", border="4 SOLID #0F172AFF", extra={"shape": "CIRCLE"}))
kids.append(D.box(530, 40, 40, 40, radius=20, color="#FFFFFFFF", border="4 SOLID #0F172AFF"))
kids.append(D.box(590, 40, 24, 24, color="#B45309FF", extra={"shape": "CIRCLE"}))
kids.append(D.text_el("shape=CIRCLE | radius | small dot", x=460, y=92, w=400, h=30, size=20))

# 3. glyph coverage
glyph_sets = [
    ("DejaVu Sans", "DJV: \u2713 \u2715 \u2717 \u25CF \u25B2 \u2022 \u2192 \u00D7"),
    ("Noto Sans CJK SC", "CJK: \u2713 \u2715 \u2717 \u25CF \u25B2 \u2022 \u2192 \u00D7"),
    ("Inter,Noto Sans CJK SC", "UI : \u2713 \u2715 \u2717 \u25CF \u25B2 \u2022 \u2192 \u00D7"),
]
yy = 160
for fam, s in glyph_sets:
    kids.append(D.text_el(s, x=460, y=yy, w=430, h=34, size=26, font=fam))
    yy += 44
kids.append(D.text_el("CJK probe: \u65e0\u969c\u788d \u7ad9\u53f7 \u6362\u4e58 \u533a\u95f4\u6570", x=60, y=505, w=420, h=34, size=26))

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
os.makedirs(os.path.join(TMP, "drafts"), exist_ok=True)
with open(os.path.join(TMP, "drafts", "probe-01.snapshot"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "probe-01.png", "probe-01.snapshot", final=False)
print("render ok=%s status=%s bytes=%s" % (r.get("ok"), r.get("status"), r.get("bytes")))
if not r.get("ok"):
    print(r.get("error"))
print("image:", r.get("image"))
for wn in D.warnings():
    print("WARN", wn)
