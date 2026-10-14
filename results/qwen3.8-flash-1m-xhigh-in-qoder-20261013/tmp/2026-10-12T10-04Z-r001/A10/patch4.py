"""A10 patch 4: ④ must blur the background too.

In v003 the ④ subtree held only the card fill, text and shape; the stripes were drawn
separately and stayed sharp, so the card interior showed hard-edged bands
(measured gradient 7.22, higher than ③'s blurred 1.13). The task asks ④ to blur
"背景、文字和前景整体", so the same stripes are now repeated inside the filtered
subtree at card-local phase, and ClipRRect keeps the effect inside the rounded region.
Captions are also shortened so none wraps to a single trailing glyph.
"""
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A10" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new, count)


rep('''def stripes(ox, oy, n=10, sw=16):
    """Sharp vertical colour bands that cross the card's left and right edges."""
    out = []
    cols = ["#E24C4C", "#2E7DD1", "#2FA36B", "#EAB53B", "#8E5AC8"]
    for i in range(n):
        x = i * (AW / n)
        out.append(Positioned(C(width=num(sw), height=num(AH), color=cols[i % 5]),
                              left=num(ox + x), top=num(oy)))
    return out''',
    '''STRIPE_N, STRIPE_W = 10, 16
STRIPE_COLS = ["#E24C4C", "#2E7DD1", "#2FA36B", "#EAB53B", "#8E5AC8"]


def stripes(dx, dy, n=STRIPE_N, sw=STRIPE_W):
    """The one shared stripe set; (dx, dy) offsets it in the caller's coordinates.

    Cell space gives the sharp full-cell bands; card-local space (dx=-CARD_X,
    dy=-CARD_Y) reproduces exactly the same phase inside a filtered subtree.
    """
    return [Positioned(C(width=num(sw), height=num(AH), color=STRIPE_COLS[i % 5]),
                       left=num(dx + i * (AW / n)), top=num(dy))
            for i in range(n)]''')

rep('''def card_front(ox, oy, word, *, blurred):
    """Card fill + text + foreground shape; identical in ③ and ④."""''',
    '''def card_front(ox, oy, word):
    """Card fill + text + foreground shape; identical in ③ and ④."""''')
rep('Positioned(C(width=num(CARD_W), height=num(CARD_H), color="#FFFFFFCC",\n                     borderRadius=num(CARD_R), border="2 SOLID #1B2A47"),\n                   left=num(ox + CARD_X), top=num(oy + CARD_Y)),',
    'Positioned(C(width=num(CARD_W), height=num(CARD_H), color="#FFFFFFCC",\n                     borderRadius=num(CARD_R), border="2 SOLID #1B2A47"),\n                   left=num(ox), top=num(oy)),')
rep('''            left=num(ox + CARD_X), top=num(oy + CARD_Y + 46), width=num(CARD_W)),
    ]


def scene_blur_background_only''',
    '''            left=num(ox), top=num(oy + 46), width=num(CARD_W)),
    ]


def scene_blur_background_only''')

rep('④ same scene, but card fill, text and shape all sit inside the blurred subtree."""',
    '④ background, card fill, text and shape all sit inside one blurred subtree."""')
rep('''        Positioned(
            ClipRRect(
                ImageFiltered(
                    Stack(C(width=num(CARD_W), height=num(CARD_H)),
                          *card_front(0, 0, "BLUR", blurred=True)),
                    sigmaX=num(SIGMA), sigmaY=num(SIGMA), tileMode="CLAMP"),
                borderRadius=num(CARD_R), clipBehavior="ANTI_ALIAS"),
            left=num(ox + CARD_X), top=num(oy + CARD_Y)),''',
    '''        Positioned(
            ClipRRect(
                ImageFiltered(
                    Stack(C(width=num(CARD_W), height=num(CARD_H)),
                          *stripes(-CARD_X, -CARD_Y),
                          *card_front(0, 0, "BLUR"),
                          alignment="TOP_LEFT", clipBehavior="NONE"),
                    sigmaX=num(SIGMA), sigmaY=num(SIGMA), tileMode="CLAMP"),
                borderRadius=num(CARD_R), clipBehavior="ANTI_ALIAS"),
            left=num(ox + CARD_X), top=num(oy + CARD_Y)),''')

# ③ keeps the same card-front construction, just outside the filter
rep('''        # text and foreground shape stay outside the filter subtree
        Positioned(
            Col(Text("SHARP", color="#0B1220", fontSize="24", fontStyle="BOLD",
                     fontFamily=FONT, textAlign="CENTER"),
                Container(height="6"),
                C(width="56", height="26", color="#16233C", borderRadius="6"),
                crossAxisAlignment="CENTER"),
            left=num(ox + CARD_X), top=num(oy + CARD_Y + 46), width=num(CARD_W)),''',
    '''        # text and foreground shape stay outside the filter subtree, drawn sharp
        *card_front(CARD_X, CARD_Y, "SHARP")[1:],''')

# ---------------------------------------------------------------- captions
rep('"ImageFiltered 把卡片、文字与形状一起糊"', '"ImageFiltered 连背景文字形状一起糊"')
rep('"MULTIPLY #F6B94A 后 sigma=6，可外溢"', '"MULTIPLY 后 sigma=6，间隙被填、边缘外溢"')
rep('"同样结果套上 r=100 圆裁，边界锐利"', '"同一结果套 r=100 圆裁，弧上锐利截断"')
rep('"BackdropFilter 只糊卡片覆盖处的条纹"', '"BackdropFilter 只糊卡下条纹，字仍锐利"')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched 4")
