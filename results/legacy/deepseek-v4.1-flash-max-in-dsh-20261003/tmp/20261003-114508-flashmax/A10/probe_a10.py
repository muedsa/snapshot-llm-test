"""A10 probe: measure BackdropFilter / ImageFiltered / ColorFiltered semantics before
building the six-panel board. 900x480, one render.

Questions:
  Q1 does <ClipRRect> + <BackdropFilter sigma=6> blur only the rounded-card region, or
     does it smear the whole composited canvas (the suite briefing warned about sigma=1)?
  Q2 does <ImageFiltered sigma=6> blur only its own subtree, and does the text inside
     stay readable?
  Q3 does <ColorFiltered color="#F6B94A" blendMode="MULTIPLY"> stay inside the subtree
     paint bounds, and does it tint transparent gaps (documented as possible)?
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 900, 480
INK = "#0F172AFF"
CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"


def stripes(x, y, w, h, sw=14, color=INK):
    out = []
    i = 0
    while i * sw < w:
        out.append(f'<Positioned left="{x + i * sw}" top="{y}">'
                   f'<Container width="{min(sw, w - i * sw)}" height="{h}" color="{color}"/></Positioned>')
        i += 2
    return "".join(out)


def main() -> None:
    p = [f'<Snapshot background="#FFFFFFFF" type="png">',
         f'<Container width="{W}" height="{H}">',
         '<Stack alignment="TOP_LEFT" fit="EXPAND">']
    # ---- Q1: stripes across the full width, frosted card on the left, sharp text right
    p.append(f'<Positioned left="0" top="0"><Container width="{W}" height="240" color="#FFFFFFFF"/></Positioned>')
    p.append(stripes(0, 0, W, 240))
    p.append('<Positioned left="40" top="30"><ClipRRect borderRadius="20">'
             '<BackdropFilter sigmaX="6" sigmaY="6">'
             '<Container width="240" height="160" color="#FFFFFFB3"/>'
             '</BackdropFilter></ClipRRect></Positioned>')
    p.append('<Positioned left="60" top="90"><Text fontSize="24" color="#0F172AFF" '
             f'fontFamily="{MONO}" fontStyle="BOLD">SHARP / BLUR</Text></Positioned>')
    p.append('<Positioned left="320" top="30"><Container width="300" height="60" color="#FFFFFFCC" '
             'borderRadius="8"/></Positioned>')
    p.append('<Positioned left="332" top="42"><Text fontSize="24" color="#0F172AFF" '
             f'fontFamily="{CJK}">卡外文字应清晰 24px</Text></Positioned>')
    p.append('<Positioned left="332" top="120"><Container width="520" height="60" color="#FFFFFFCC" '
             'borderRadius="8"/></Positioned>')
    p.append('<Positioned left="344" top="132"><Text fontSize="24" color="#D92D20FF" '
             f'fontFamily="{CJK}">若这行也糊 → BackdropFilter 溢出裁剪</Text></Positioned>')
    # ---- Q2/Q3: white lower half, blurred text + multiplied content
    p.append(f'<Positioned left="0" top="240"><Container width="{W}" height="240" color="#FFFFFFFF"/></Positioned>')
    p.append('<Positioned left="40" top="270"><ImageFiltered sigmaX="6" sigmaY="6">'
             f'<Container width="240" height="60" color="#FFFFFFFF" alignment="CENTER_LEFT">'
             f'<Text fontSize="24" color="#0F172AFF" fontFamily="{MONO}">TEXT IN FILTER</Text>'
             '</Container></ImageFiltered></Positioned>')
    # multiplied group with a transparent gap, a dark rect and a shadow
    inner = ['<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">',
             '<Positioned left="24" top="20"><Container width="70" height="80" color="#1F2937FF" '
             'borderRadius="8" boxShadow="0 8 16 0 #0F172A40 NORMAL"/></Positioned>',
             '<Positioned left="110" top="20"><Container width="44" height="44" color="#2563EBFF" '
             'borderRadius="6"/></Positioned>',
             '<Positioned left="166" top="20"><Container width="44" height="44" color="#2563EBFF" '
             'borderRadius="6"/></Positioned>',
             '</Stack>']
    p.append('<Positioned left="330" top="270" width="240" height="160">'
             '<Container width="240" height="160" border="1 SOLID #E2E8F0FF">'
             '<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">'
             '<Positioned left="0" top="0">'
             '<ImageFiltered sigmaX="6" sigmaY="6">'
             '<ColorFiltered color="#F6B94AFF" blendMode="MULTIPLY">'
             + "".join(inner) +
             '</ColorFiltered></ImageFiltered></Positioned>'
             '</Stack></Container></Positioned>')
    p.append('<Positioned left="600" top="270"><Container width="260" height="60" color="#F8FAFCFF" '
             'borderRadius="8" border="1 SOLID #E2E8F0FF"/></Positioned>')
    p.append('<Positioned left="612" top="284"><Text fontSize="22" color="#475569FF" '
             f'fontFamily="{CJK}">⑤⑥测试区：MULTIPLY 是否出界</Text></Positioned>')
    p.append('</Stack></Container></Snapshot>')
    out = os.path.join(HERE, "probe-a10.snapshot")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(p) + "\n")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
