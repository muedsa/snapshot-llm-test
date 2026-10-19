# -*- coding: utf-8 -*-
"""A21 round-01：叠光 Layerlight 发布物（竖海报 1080x1350 / 横屏 1440x810）。

设计系统共享：深空底 + 青光主色(#2EE6D0)+紫光辅助(#7C6CFF)；
品牌构件4枚：layer-stack 三层渐变横带、halo-ring 光晕双环、beacon 信标点、mesh-dots 微光点阵。
竖图居中对称构图；横图左右分栏构图。顶/底各留真实无文字扩展区。
透明度装饰一律用对底色(#0B1220)预混后的实色（避免 Opacity/无界 Stack）。
"""
import os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RUN = "20261016T164020-m1"
D = f"outputs/{RUN}/A21/round-01"
os.makedirs(D, exist_ok=True)

FAM = "Noto Sans CJK SC"
FAM_L = "Inter"
BG1, BG2 = "#0B1220", "#0D1A31"
CY, VI, SKY = "#2EE6D0", "#7C6CFF", "#5AD7FF"
TXT, SUB = "#F4F7FC", "#A9B6CF"
GHOST_R1, GHOST_R2 = "#113850", "#0F1C4B"   # 18%青 / 12%紫 预混
GHOST_B = "#165261"                          # 30%青 信标晕
GHOST_RULE = "#1D7C81"                       # 50%青 短线
GHOST_DOT = "#2D466B"                        # 90%#2C4666 点阵

def txt(s, x, y, w, size, color, family=FAM, bold=False, align="START",
        ls=0, lines=1, h=None):
    st = (f'<Text fontSize="{size}" color="{color}" fontFamily="{family}"'
          f' textAlign="{align}"' + (' fontStyle="BOLD"' if bold else '')
          + (f' letterSpacing="{ls}"' if ls else '')
          + f' maxLines="{lines}"' + (' overflow="CLIP"' if lines == 1 else '')
          + f'>{s}</Text>')
    H = h or int(size * 1.45) + 2
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
    a = (f'<Positioned left="{cx - r_out}" top="{cy - r_out}">'
         f'<Container width="{2 * r_out}" height="{2 * r_out}" borderRadius="{r_out}"'
         f' border="2 SOLID {GHOST_R1}" /></Positioned>')
    b = (f'<Positioned left="{cx - r_in}" top="{cy - r_in}">'
         f'<Container width="{2 * r_in}" height="{2 * r_in}" borderRadius="{r_in}"'
         f' border="2 SOLID {GHOST_R2}" /></Positioned>')
    return a + b

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

def chip(x, y, w, h):
    ty = (h - 38) // 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Stack>'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' borderRadius="{h // 2}" color="#0F2334" border="1 SOLID {CY}" /></Positioned>'
            f'<Positioned left="0" top="{ty}" width="{w}" height="{h - ty}">'
            f'<Text fontSize="30" color="#7FF3E6" fontFamily="{FAM_L}" textAlign="CENTER"'
            ' maxLines="1" overflow="CLIP">layerlight.example.org</Text></Positioned>'
            '</Stack></Positioned>')

def base(w, h, body):
    return ('<Snapshot background="' + BG1 + '" type="png"><Stack>'
            f'<SizedBox width="{w}" height="{h}" />'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' gradientType="LINEAR" gradientColors="{BG1},{BG2}"'
            ' gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER" /></Positioned>'
            + body + '</Stack></Snapshot>\n')

# ── 竖海报 1080×1350：居中对称构图 ──
P = []
P.append(halo(540, 380, 240, 180))                       # 光晕双环
P.append(layer_mark(374, 322, 296, 24, 18, 36))          # 三层叠光横带
P.append(beacon(742, 470))                                # 信标点
P.append(mesh(108, 210, 5, 3, 46, 40))                    # 顶部左侧点阵
P.append(f'<Positioned left="258" top="500"><Container width="84" height="2" color="{GHOST_RULE}" /></Positioned>')
P.append(f'<Positioned left="738" top="500"><Container width="84" height="2" color="{GHOST_RULE}" /></Positioned>')
P.append(txt("ONLINE\u00a0LAUNCH", 240, 472, 600, 26, CY, FAM_L, bold=True,
             align="CENTER", ls=12, h=44))
P.append(txt("让复杂信息", 0, 548, 1080, 68, TXT, FAM, bold=True, align="CENTER", ls=4, h=92))
P.append(txt("变得清晰", 0, 642, 1080, 68, TXT, FAM, bold=True, align="CENTER", ls=4, h=92))
P.append(txt("叠光\u00a0Layerlight\u00a0发布活动", 0, 756, 1080, 30, SUB, FAM, align="CENTER", h=44))
P.append(txt("2026.11.07\u00a019:30", 0, 822, 1080, 46, TXT, FAM_L, bold=True,
             align="CENTER", ls=2, h=58))
P.append(gradbar(470, 886, 140, 3, 1.5, CY, VI))          # 日期下划线
P.append(txt("讲者：林川\u00a0/\u00a0苏言", 0, 916, 1080, 30, "#D7E0EE", FAM,
             align="CENTER", h=44))
P.append(chip(310, 1118, 460, 62))
portrait = base(1080, 1350, "".join(P))

# ── 横屏 1440×810：左右分栏构图 ──
W = []
W.append(halo(322, 344, 212, 158))                        # 左簇光晕
W.append(layer_mark(160, 252, 320, 26, 20, 44))           # 左簇叠光带
W.append(beacon(492, 428))                                # 左簇信标
W.append(mesh(120, 552, 5, 2, 48, 34))                    # 左下点阵
W.append(f'<Positioned left="660" top="122"><Container width="96" height="2" color="{CY}" /></Positioned>')
W.append(txt("ONLINE\u00a0LAUNCH", 660, 166, 660, 26, CY, FAM_L, bold=True, ls=12, h=44))
W.append(txt("让复杂信息变得清晰", 660, 218, 690, 60, TXT, FAM, bold=True, ls=3, h=84))
W.append(txt("叠光\u00a0Layerlight\u00a0发布活动", 660, 316, 690, 28, SUB, FAM, h=42))
W.append(txt("2026.11.07\u00a019:30", 660, 376, 690, 44, TXT, FAM_L, bold=True, ls=2, h=56))
W.append(gradbar(660, 440, 130, 3, 1.5, CY, VI))
W.append(txt("讲者：林川\u00a0/\u00a0苏言", 660, 460, 660, 28, "#D7E0EE", FAM, h=42))
W.append(chip(660, 524, 460, 60))
wide = base(1440, 810, "".join(W))

open(f"{D}/launch-portrait.snapshot", "w", encoding="utf-8", newline="\n").write(portrait)
open(f"{D}/launch-wide.snapshot", "w", encoding="utf-8", newline="\n").write(wide)
print("round-01 DSL written:", len(portrait), len(wide))
