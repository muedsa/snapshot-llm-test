# -*- coding: utf-8 -*-
"""A21 round-03：浅色主题（普通文字与实际合成背景对比≥4.5:1）。

保留 round-02 全部文案与品牌 4 构件（横带/渐变端色不变）；
新增网址上方英语句 "Clarity through structure"。
浅色场景色板：底 #F5F8FC→#E9EFF7 渐变；正文墨色 #0F1B2D/#2A3A54/#44536B；
品牌青文字改用深青墨 #0A6E62（浅底上的品牌青仍以装饰渐变保留原色）。
"""
import os, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
RUN = "20261016T164020-m1"
D = f"outputs/{RUN}/A21/round-03"
os.makedirs(D, exist_ok=True)

FAM = "Noto Sans CJK SC"
FAM_L = "Inter"
BG1, BG2 = "#F5F8FC", "#E9EFF7"
CY, VI, SKY = "#2EE6D0", "#7C6CFF", "#5AD7FF"          # 品牌装饰原色保留
INK, INK2, MUT = "#0F1B2D", "#2A3A54", "#44536B"
TEAL_INK = "#085F55"                                    # 品牌青的浅底文字色（加深以过幽灵环线上的 4.5:1）
CHIP_BG, CHIP_TX = "#0D2237", "#7FF3E6"
PILL_BG = "#FCFEFE"
SPONSOR_LABEL, SPONSOR_NAME = "#506681", "#44536B"
G_RING1, G_RING2, G_BEACON, G_RULE, G_DOT = "#CFE3EF", "#C7DCEE", "#D4E7F2", "#BFD6E4", "#C9D4E2"
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
             f' border="2 SOLID {G_RING1}" /></Positioned>')
            + (f'<Positioned left="{cx - r_in}" top="{cy - r_in}">'
               f'<Container width="{2 * r_in}" height="{2 * r_in}" borderRadius="{r_in}"'
               f' border="2 SOLID {G_RING2}" /></Positioned>'))

def beacon(x, y, ds=12):
    return ((f'<Positioned left="{x - 17}" top="{y - 17}">'
             f'<Container width="34" height="34" borderRadius="17" color="{G_BEACON}" /></Positioned>')
            + (f'<Positioned left="{x - ds // 2}" top="{y - ds // 2}">'
               f'<Container width="{ds}" height="{ds}" borderRadius="{ds // 2}"'
               ' color="#199CD9" /></Positioned>'))

def mesh(x0, y0, cols, rows, dx, dy):
    return "".join(
        f'<Positioned left="{x0 + c * dx}" top="{y0 + r * dy}">'
        f'<Container width="3" height="3" color="{G_DOT}" /></Positioned>'
        for r in range(rows) for c in range(cols))

def urlchip(x, y, w, h):
    ty = (h - 38) // 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Stack>'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' borderRadius="{h // 2}" color="{CHIP_BG}" /></Positioned>'
            f'<Positioned left="0" top="{ty}" width="{w}" height="{h - ty}">'
            f'<Text fontSize="30" color="{CHIP_TX}" fontFamily="{FAM_L}" textAlign="CENTER"'
            f' maxLines="1" overflow="CLIP">layerlight.example.org</Text></Positioned>'
            '</Stack></Positioned>')

def free_pill(x, y, w, h):
    ty = (h - 34) // 2
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Stack>'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' borderRadius="{h // 2}" color="{PILL_BG}" border="1 SOLID {G_RULE}" /></Positioned>'
            f'<Positioned left="0" top="{ty}" width="{w}" height="{h - ty}">'
            f'<Text fontSize="26" color="{TEAL_INK}" fontFamily="{FAM}" textAlign="CENTER"'
            f' maxLines="1" overflow="CLIP">免费参加{NB}·{NB}无需报名</Text></Positioned>'
            '</Stack></Positioned>')

def base(w, h, body):
    return ('<Snapshot background="' + BG1 + '" type="png"><Stack>'
            f'<SizedBox width="{w}" height="{h}" />'
            f'<Positioned left="0" top="0"><Container width="{w}" height="{h}"'
            f' gradientType="LINEAR" gradientColors="{BG1},{BG2}"'
            ' gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER" /></Positioned>'
            + body + '</Stack></Snapshot>\n')

def sponsor(x, y, w, al="START"):
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="40">'
            f'<Text fontSize="26" fontFamily="{FAM}" textAlign="{al}"'
            f' maxLines="1" overflow="CLIP">'
            f'<Raw color="{SPONSOR_LABEL}">赞助{NB}</Raw>'
            f'<Raw color="{SPONSOR_NAME}">Northstar{NB}Research{NB}/{NB}云构工具</Raw></Text>'
            f'</Positioned>')

# ── 竖海报 1080×1350（round-03 浅色）──────────────────────
P = []
P.append(halo(540, 380, 240, 180))
P.append(layer_mark(374, 322, 296, 24, 18, 36))
P.append(beacon(742, 470))
P.append(mesh(108, 210, 5, 3, 46, 40))
P.append(f'<Positioned left="258" top="500"><Container width="84" height="2" color="{G_RULE}" /></Positioned>')
P.append(f'<Positioned left="738" top="500"><Container width="84" height="2" color="{G_RULE}" /></Positioned>')
P.append(txt(f"ONLINE{NB}LAUNCH", 240, 472, 600, 26, TEAL_INK, FAM_L, bold=True,
             align="CENTER", ls=12))
P.append(txt("当所有信息都想成为标题：", 0, 524, 1080, 64, INK, FAM, bold=True,
             align="CENTER", ls=2))
P.append(txt("让复杂信息变得清晰的", 0, 602, 1080, 64, INK, FAM, bold=True,
             align="CENTER", ls=2))
P.append(txt("结构化方法", 0, 680, 1080, 64, INK, FAM, bold=True, align="CENTER", ls=2))
P.append(txt(f"叠光{NB}Layerlight{NB}发布活动", 0, 768, 1080, 30, MUT, FAM, align="CENTER"))
P.append(txt(f"2026.11.07{NB}19:30", 0, 828, 1080, 46, INK, FAM_L, bold=True,
             align="CENTER", ls=2))
P.append(gradbar(470, 894, 140, 3, 1.5, CY, VI))
P.append(txt(f"讲者：林川{NB}/{NB}苏言", 0, 918, 1080, 30, INK2, FAM, align="CENTER"))
P.append(sponsor(0, 986, 1080, "CENTER"))
P.append(free_pill(390, 1034, 300, 56))
P.append(txt("Clarity through structure", 0, 1108, 1080, 26, TEAL_INK, FAM_L,
             align="CENTER", ls=3))
P.append(urlchip(310, 1156, 460, 62))
portrait = base(1080, 1350, "".join(P))

# ── 横屏 1440×810（round-03 浅色）──────────────────────
W = []
W.append(halo(322, 344, 212, 158))
W.append(layer_mark(160, 252, 320, 26, 20, 44))
W.append(beacon(492, 428))
W.append(mesh(120, 552, 5, 2, 48, 34))
W.append(f'<Positioned left="660" top="136"><Container width="96" height="2" color="{CY}" /></Positioned>')
W.append(txt(f"ONLINE{NB}LAUNCH", 660, 150, 660, 26, TEAL_INK, FAM_L, bold=True, ls=12))
W.append(txt("当所有信息都想成为标题：", 660, 206, 690, 54, INK, FAM, bold=True, ls=2))
W.append(txt("让复杂信息变得清晰的", 660, 268, 690, 54, INK, FAM, bold=True, ls=2))
W.append(txt("结构化方法", 660, 330, 690, 54, INK, FAM, bold=True, ls=2))
W.append(txt(f"叠光{NB}Layerlight{NB}发布活动", 660, 398, 690, 28, MUT, FAM))
W.append(txt(f"2026.11.07{NB}19:30", 660, 442, 690, 44, INK, FAM_L, bold=True, ls=2))
W.append(gradbar(660, 506, 130, 3, 1.5, CY, VI))
W.append(txt(f"讲者：林川{NB}/{NB}苏言", 660, 520, 660, 28, INK2, FAM))
W.append(sponsor(660, 572, 690, "START"))
W.append(txt("Clarity through structure", 660, 624, 690, 26, TEAL_INK, FAM_L, ls=3))
W.append(urlchip(660, 670, 460, 56))
W.append(free_pill(122, 618, 276, 56))
wide = base(1440, 810, "".join(W))

open(f"{D}/launch-portrait.snapshot", "w", encoding="utf-8", newline="\n").write(portrait)
open(f"{D}/launch-wide.snapshot", "w", encoding="utf-8", newline="\n").write(wide)

# ── 去文字辅助版（背景审计用，仅存临时目录）──────────────
import re
def strip_text(s):
    # 先删“Positioned 仅含 Text”的整包装，再兜底删单独 Text
    s = re.sub(r'<Positioned\b[^>]*>\s*<Text\b[^>]*>.*?</Text>\s*</Positioned>', '', s, flags=re.S)
    s = re.sub(r'<Text\b[^>]*>.*?</Text>', '', s, flags=re.S)
    return s

TD = f"tmp/{RUN}/A21"
os.makedirs(f"{TD}/bg-data", exist_ok=True)
open(f"{TD}/bg-data/r03-portrait-bg.snapshot", "w", encoding="utf-8", newline="\n").write(strip_text(portrait))
open(f"{TD}/bg-data/r03-wide-bg.snapshot", "w", encoding="utf-8", newline="\n").write(strip_text(wide))
print("round-03 DSL written:", len(portrait), len(wide))
