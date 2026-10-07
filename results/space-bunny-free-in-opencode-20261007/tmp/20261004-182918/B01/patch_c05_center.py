# -*- coding: utf-8 -*-
"""One-off patch: replace every `one_line(cx, ..., align="CENTER")` in build_c05
with the new atelier.ctr() helper, which takes the real centre x.

Reason: `Text textAlign="CENTER"` centres inside its own BOX, so passing the
intended centre as the box left edge shifts every glyph right by w/2. That is
why the species names, month numbers and cell values were all off-centre.
"""
import io
import sys

PATH = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B01\build_c05.py"

PAIRS = [
    ('''    K.append(A.one_line((x0 + x1) / 2.0, GY0 - 28, nm, size=13, color="#10191A",
                        font=A.SEMI, pad=8, align="CENTER", w=x1 - x0))''',
     '''    K.append(A.ctr((x0 + x1) / 2.0, GY0 - 28, nm, w=x1 - x0, size=13,
                    color="#10191A", font=A.SEMI))'''),

    ('''    K.append(A.one_line(cx + CELL_W / 2.0, GY0, name, size=14,
                        color=BODY if name.endswith("月") else INK,
                        font=A.SEMI, pad=8, align="CENTER", w=CELL_W - 4))''',
     '''    K.append(A.ctr(cx + CELL_W / 2.0, GY0, name, w=CELL_W - 4, size=14,
                    color=INK, font=A.SEMI))'''),

    ('''            K.append(A.one_line(cx + CELL_W / 2.0, ry + 7, str(v), size=13,
                                color=fg, font=A.SEMI, pad=6,
                                align="CENTER", w=CELL_W - 6))''',
     '''            K.append(A.ctr(cx + CELL_W / 2.0, ry + 7, str(v), w=CELL_W - 6,
                            size=13, color=fg, font=A.SEMI))'''),

    ('''    K.append(A.one_line(M + 22, ry + 11, code, size=11,
                        color="#0E1614" if code == "R" else "#2A1C06",
                        font=A.BLACK, pad=4, align="CENTER", w=cw))''',
     '''    K.append(A.ctr(M + 22 + cw / 2.0, ry + 11, code, w=cw, size=11,
                    color="#0E1614" if code == "R" else "#2A1C06",
                    font=A.BLACK))'''),

    ('''    K.append(A.one_line(LGX + 20 + (LGW - 40) * (v / float(VMAX)), GY0 + 30,
                        str(v), size=10, color=MUTED, font=A.MONO, pad=6,
                        anchor="CENTER", w=30))''',
     '''    K.append(A.ctr(LGX + 20 + (LGW - 40) * (v / float(VMAX)), GY0 + 30,
                    str(v), w=30, size=10, color=MUTED, font=A.MONO))'''),

    ('''    K.append(A.one_line(cx + BW / 2.0, BY + 82, MONTHS[mth], size=13,
                        color=INK if inb else MUTED,
                        font=A.SEMI if inb else A.UI, pad=8,
                        align="CENTER", w=BW - 10))''',
     '''    K.append(A.ctr(cx + BW / 2.0, BY + 82, MONTHS[mth], w=BW - 10, size=13,
                    color=INK if inb else MUTED,
                    font=A.SEMI if inb else A.UI))'''),

    ('''        K.append(A.one_line(cx + BW / 2.0, BY + 42, str(scores[mth]), size=17,
                            color="#7FC8A4", font=A.BLACK, pad=8,
                            align="CENTER", w=BW - 10))''',
     '''        K.append(A.ctr(cx + BW / 2.0, BY + 42, str(scores[mth]), w=BW - 10,
                        size=17, color="#7FC8A4", font=A.BLACK))'''),
]


def main():
    s = io.open(PATH, encoding="utf-8").read()
    for old, new in PAIRS:
        if old not in s:
            print("MISS:", old.strip().splitlines()[0][:70])
            sys.exit(1)
        s = s.replace(old, new)
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(s)
    print("patched; remaining align=CENTER:", s.count('align="CENTER"'))


if __name__ == "__main__":
    main()