"""Bisect helper: render each probe-05 section separately to find the 500.

The whole-probe render returned 500 INTERNAL_ERROR with no detail, so each
section is emitted into its own small canvas.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

SECTIONS = {
    "elev": ('<Container width="170" height="92" color="#F1F5F9FF" '
             'borderRadius="16" boxShadow="ELEVATION_%s" />'),
    "custom": ('<Container width="170" height="80" color="#F1F5F9FF" '
               'borderRadius="14" boxShadow="%s" />'),
    "radii": ('<Container width="190" height="120" color="#0EA5E9FF" %s />'),
    "align": '<Stack fit="LOOSE" alignment="%s" />',
    "idx": '<IndexedStack index="%s" fit="LOOSE" alignment="CENTER" />',
    "over": '%s',
    "flex": '%s',
}


def try_dsl(name, inner, w=400, h=260):
    dsl = D.snapshot([D.stack([D.el("Container", {"width": w, "height": h,
                                                  "color": "#0B1020FF"},
                                      [D.el("Positioned",
                                            {"left": 20, "top": 20,
                                             "width": w - 40,
                                             "height": h - 40},
                                            [D.el("Raw", {}, [D.cdata(inner)])
                                             if False else None] or
                                            [D.el("Container", {},
                                                  [inner_text(inner)])])])])],
                     w, h, bg="#0B1020FF")
    return P.probe(dsl, "bisect-" + name)


def inner_text(s):
    return D.el("Raw", {}, [D.cdata(s)])


CANDIDATES = []
for lv in [0, 1, 2, 4, 8, 16, 24]:
    CANDIDATES.append(("elev%d" % lv,
                       '<Container width="170" height="92" color="#F1F5F9FF" '
                       'borderRadius="16" boxShadow="ELEVATION_%d" />' % lv))
for i, sh in enumerate([
        "0 2 6 0 #00000033", "0 4 12 4 #00000044", "0 4 12 -4 #00000044",
        "8 8 20 0 #F43F5E66", "0 0 0 6 #38BDF866",
        "0 4 10 0 #00000055 NORMAL,0 1 2 0 #00000088",
        "0 4 10 0 #00000044 INNER", "0 4 10 0 #00000044 OUTER",
        "0 4 10 0 #00000044 SOLID"]):
    CANDIDATES.append(("shadow%d" % i,
                       '<Container width="170" height="80" color="#F1F5F9FF" '
                       'borderRadius="14" boxShadow="%s" />' % sh))
CANDIDATES += [
    ("radius4",
     '<Container width="190" height="120" color="#0EA5E9FF" '
     'borderRadiusTopLeft="60" borderRadiusTopRight="8" '
     'borderRadiusBottomLeft="8" borderRadiusBottomRight="60" />'),
    ("borders4",
     '<Container width="190" height="120" color="#111827FF" '
     'borderTop="8 SOLID #EF4444FF" borderBottom="8 SOLID #EF4444FF" />'),
    ("alignCustom",
     '<Stack fit="LOOSE" alignment="(0.8,-0.6)">'
     '<Container width="80" height="30" color="#F87171FF" />'
     '<Container width="120" height="30" color="#34D399FF" /></Stack>'),
    ("idxStack",
     '<IndexedStack index="1" fit="LOOSE" alignment="CENTER">'
     '<Container width="160" height="60" color="#F87171FF" />'
     '<Container width="160" height="60" color="#34D399FF" /></IndexedStack>'),
    ("overflowBox",
     '<OverflowBox alignment="TOP_RIGHT">'
     '<Container width="260" height="120" color="#F59E0BFF" /></OverflowBox>'),
    ("sizedOverflow",
     '<SizedOverflowBox width="160" height="100" alignment="BOTTOM_RIGHT">'
     '<Container width="260" height="120" color="#60A5FAFF" />'
     '</SizedOverflowBox>'),
    ("aspect2",
     '<AspectRatio aspectRatio="2.0">'
     '<Container color="#34D399FF" /></AspectRatio>'),
    ("frac",
     '<FractionallySizedBox widthFactor="0.5" heightFactor="0.25" '
     'alignment="CENTER"><Container width="120" height="40" '
     'color="#38BDF8FF" /></FractionallySizedBox>'),
    ("constrained",
     '<ConstrainedBox maxWidth="80"><Container width="200" height="60" '
     'color="#FB7185FF" /></ConstrainedBox>'),
    ("rowBaseline",
     '<Row crossAxisAlignment="BASELINE" textBaseline="ALPHABETIC">'
     '<Text text="big" fontSize="40" fontFamily="Inter" color="#F8FAFCFF" />'
     '<Text text="small" fontSize="16" fontFamily="Inter" color="#94A3B8FF" />'
     '</Row>'),
    ("rowRTL",
     '<Row textDirection="RTL">'
     '<Container width="80" height="40" color="#F87171FF" />'
     '<Container width="80" height="40" color="#FBBF24FF" /></Row>'),
    ("spacer", '<Row><Container width="60" height="40" color="#F87171FF" />'
               '<Spacer flex="1" />'
               '<Container width="60" height="40" color="#34D399FF" /></Row>'),
    ("mainAxisMin",
     '<Row mainAxisSize="MIN"><Container width="60" height="40" '
     'color="#F87171FF" /></Row>'),
]

for name, frag in CANDIDATES:
    w = 320
    h = 240
    body = D.el("Container", {"width": w, "height": h, "color": "#0B1020FF"},
                [D.el("Stack", {"fit": "LOOSE"}, [frag])])
    dsl = D.snapshot([D.stack([body], w, h)], w, h, bg="#0B1020FF")
    r = P.probe(dsl, "b05-" + name)
    print("%-14s %s %s" % (name, r.get("ok"), (r.get("error") or "")[:110]))