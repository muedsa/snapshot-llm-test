# -*- coding: utf-8 -*-
"""A21 round-02：在 round-01 版式上替换长标题(≤3行,≥48)，新增赞助方与参加方式。

品牌构件/主色/字体层级沿用 r01；装饰允许微移。竖图 1080×1350 / 横屏 1440×810。
长标题防碰撞：3 行固定行距的标题块后，副信息按级联 y 排布（最小间隙≥8px），
胶囊类构件贴底部，左簇区承担“免费参加”胶囊，不与文字块交叉。
"""
import os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RUN = "20261016T164020-m1"
D = f"outputs/{RUN}/A21/round-02"
os.makedirs(D, exist_ok=True)

FAM = "Noto Sans CJK SC"
FAM_L = "Inter"
BG1, BG2 = "#0B1220", "#0D1A31"
CY, VI, SKY = "#2EE6D0", "#7C6CFF", "#5AD7FF"
TXT, SUB = "#F4F7FC", "#A9B6CF"
GHOST_R1, GHOST_R2 = "#113850", "#0F1C4B"
GHOST_B = "#165261"
GHOST_RULE = "#1D7C81"
GHOST_DOT = "#2D466B"
NB = "\u00a0"

def txt(s, x, y, w, size, color, family=FAM, bold=False, align="START",
        ls=0, lines=1):
    st = (f'<Text fontSize="{size}" color="{color}" fontFamily="{family}"'
          f' textAlign="{align}"' + (' fontStyle="BOLD"' if bold else '')
          + (f' letterSpacing="{ls}"' if ls else '')
          + f' maxLines="{lines}"' + (' overflow="CLIP"' if lines == 1 else '')
          + f'>{s}</Text>')
    H = int(size * 1.45) + 2
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{H}">{st}</Positioned>'

def gradbar(x, y, w, h, r, c1, c2, rev=False):
    a, b = (c2, c1) if rev else (c1, c2)
    return (f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}"'
            f' borderRadius="{r}" gradientType="LINEAR" gradientColors="{a},{b}"'
            f' gradientBegin="CENTER_LEFT" gradientEnd="CENTER_RIGHT" /></Positioned>')

def layer_mark(bx, by, bw, bh, step_x, step_y):
    return (gradbar(bx, by, bw, bh, bh // 2, CY, SKY)
            + gradbar(bx + step_x, by + step_y, bw, bh, bh // 2, "#45D2DF", VI)
            + gradbar(bx + 2 * step_x, by + 2 * step_y, bw, bh, bh // 2, VI, CY, rev=True))

def halo(cx, cy, r_out, r_in):
    return ((f'<Positioned left="{cx - r_out}" top="{cy - r_out}">'
             f'<Container width="{2 * r_out}" height="{2 * r_out}" borderRadius="{r_out}"'
             f' border="2 SOLID {GHOST_R1}" /></Positioned>')
            + (f'<Positioned left="{cx - r_in}" top="{cy - r_in}">'
               f'<Container width="{2 * r_in}" height="{2 * r_in}" borderRadius="{r_in}"'
               f' border="2 SOLID {GHOST_R2}" /></Positioned>'))

def beacon(x, y, ds=12):
    return ((f'<Positioned left="{x - 17}" top="{y - 17}">'
             f'<Container width="34" height="34" borderRadius="17" color="{GHOST_B}" /></Positioned>')
            + (f'<Positioned left="{x - ds // 2}" top="{y - ds // 2}">'
               f'<Container width="{ds}" height="{ds}" borderRadius="{ds // 2}"'
               ' color="#57FFE9" /></Positioned>'))

def mesh(x0, y0, cols, rows, dx, dy):
    return "".join(
        f'<Positioned left="{x0 + c * dx}" top="{y0 + r * dy}">'
        f'<Container width="3" height="3" color="{GHOST_DOT}" /></Positioned>'
        for r in range(rows) for c in range(cols))

def urlchip(x, y, w, h):
    ty = (h - 38) // 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Stack>'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' borderRadius="{h // 2}" color="#0F2334" border="1 SOLID {CY}" /></Positioned>'
            f'<Positioned left="0" top="{ty}" width="{w}" height="{h - ty}">'
            f'<Text fontSize="30" color="#7FF3E6" fontFamily="{FAM_L}" textAlign="CENTER"'
            f' maxLines="1" overflow="CLIP">layerlight.example.org</Text></Positioned>'
            '</Stack></Positioned>')

def free_pill(x, y, w, h):
    ty = (h - 34) // 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Stack>'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' borderRadius="{h // 2}" color="#0E2130" border="1 SOLID {GHOST_RULE}" /></Positioned>'
            f'<Positioned left="0" top="{ty}" width="{w}" height="{h - ty}">'
            f'<Text fontSize="26" color="#9FEFE6" fontFamily="{FAM}" textAlign="CENTER"'
            f' maxLines="1" overflow="CLIP">免费参加{NB}·{NB}无需报名</Text></Positioned>'
            '</Stack></Positioned>')

def base(w, h, body):
    return ('<Snapshot background="' + BG1 + '" type="png"><Stack>'
            f'<SizedBox width="{w}" height="{h}" />'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' gradientType="LINEAR" gradientColors="{BG1},{BG2}"'
            ' gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER" /></Positioned>'
            + body + '</Stack></Snapshot>\n')

SPONSOR_RICH = (f'<Raw color="{{SUB}}">赞助{NB}</Raw>'
                f'<Raw color="#9FB3CF">Northstar{NB}Research{NB}/{NB}云构工具</Raw>')

def sponsor(x, y, w, al="START"):
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="40">'
            f'<Text fontSize="26" fontFamily="{FAM}" textAlign="{al}"'
            f' maxLines="1" overflow="CLIP">'
            f'<Raw color="{SUB}">赞助{NB}</Raw>'
            f'<Raw color="#C9D4E4">Northstar{NB}Research{NB}/{NB}云构工具</Raw></Text>'
            f'</Positioned>')

# ── 竖海报 1080×1350（round-02）──────────────────────────────
P = []
P.append(halo(540, 380, 240, 180))
P.append(layer_mark(374, 322, 296, 24, 18, 36))
P.append(beacon(742, 470))
P.append(mesh(108, 210, 5, 3, 46, 40))
P.append(f'<Positioned left="258" top="500"><Container width="84" height="2" color="{GHOST_RULE}" /></Positioned>')
P.append(f'<Positioned left="738" top="500"><Container width="84" height="2" color="{GHOST_RULE}" /></Positioned>')
P.append(txt(f"ONLINE{NB}LAUNCH", 240, 472, 600, 26, CY, FAM_L, bold=True,
             align="CENTER", ls=12))
# 主标题 3 行（64px ≥48）
P.append(txt("当所有信息都想成为标题：", 0, 528, 1080, 64, TXT, FAM, bold=True,
             align="CENTER", ls=2))
P.append(txt("让复杂信息变得清晰的", 0, 608, 1080, 64, TXT, FAM, bold=True,
             align="CENTER", ls=2))
P.append(txt("结构化方法", 0, 688, 1080, 64, TXT, FAM, bold=True, align="CENTER", ls=2))
P.append(txt(f"叠光{NB}Layerlight{NB}发布活动", 0, 782, 1080, 30, SUB, FAM, align="CENTER"))
P.append(txt(f"2026.11.07{NB}19:30", 0, 836, 1080, 46, TXT, FAM_L, bold=True,
             align="CENTER", ls=2))
P.append(gradbar(470, 902, 140, 3, 1.5, CY, VI))
P.append(txt(f"讲者：林川{NB}/{NB}苏言", 0, 926, 1080, 30, "#D7E0EE", FAM, align="CENTER"))
P.append(sponsor(0, 990, 1080, "CENTER"))
P.append(free_pill(390, 1042, 300, 56))
P.append(urlchip(310, 1118, 460, 62))
portrait = base(1080, 1350, "".join(P))

# ── 横屏 1440×810（round-02）──────────────────────────────
W = []
W.append(halo(322, 344, 212, 158))
W.append(layer_mark(160, 252, 320, 26, 20, 44))
W.append(beacon(492, 428))
W.append(mesh(120, 552, 5, 2, 48, 34))
W.append(f'<Positioned left="660" top="150"><Container width="96" height="2" color="{CY}" /></Positioned>')
W.append(txt(f"ONLINE{NB}LAUNCH", 660, 164, 660, 26, CY, FAM_L, bold=True, ls=12))
W.append(txt("当所有信息都想成为标题：", 660, 222, 690, 54, TXT, FAM, bold=True, ls=2))
W.append(txt("让复杂信息变得清晰的", 660, 288, 690, 54, TXT, FAM, bold=True, ls=2))
W.append(txt("结构化方法", 660, 354, 690, 54, TXT, FAM, bold=True, ls=2))
W.append(txt(f"叠光{NB}Layerlight{NB}发布活动", 660, 432, 690, 28, SUB, FAM))
W.append(txt(f"2026.11.07{NB}19:30", 660, 476, 690, 44, TXT, FAM_L, bold=True, ls=2))
W.append(gradbar(660, 538, 130, 3, 1.5, CY, VI))
W.append(txt(f"讲者：林川{NB}/{NB}苏言", 660, 552, 660, 28, "#D7E0EE", FAM))
W.append(sponsor(660, 610, 690, "START"))
W.append(urlchip(660, 656, 460, 56))
W.append(free_pill(122, 618, 276, 56))
wide = base(1440, 810, "".join(W))

open(f"{D}/launch-portrait.snapshot", "w", encoding="utf-8", newline="\n").write(portrait)
open(f"{D}/launch-wide.snapshot", "w", encoding="utf-8", newline="\n").write(wide)
print("round-02 DSL written:", len(portrait), len(wide))
