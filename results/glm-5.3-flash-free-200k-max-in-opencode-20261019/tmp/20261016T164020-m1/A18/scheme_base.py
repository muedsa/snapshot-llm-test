# -*- coding: utf-8 -*-
"""A18 三幕叙事生成器：scheme=alpha(引力场环) / beta(纵向车道队列)。
同一守恒对象集：15 单元(5蓝/5橙/5灰, d36, U01-U15) + 3 节点(N01-N03, 基准 72×72 圆角方/菱形/六边形)。
仅标题与幕名文字。方案均为 1600×1000。含最小间距校验。"""
import io, sys, json, math, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

exe_mode = sys.argv[1] if len(sys.argv) > 1 else "both"
OUTD = "outputs/20261016T164020-m1/A18"
TMPD = "tmp/20261016T164020-m1/A18"
os.makedirs(TMPD, exist_ok=True)
os.makedirs(OUTD, exist_ok=True)

INK = "#1B2440"; PANEL = "#FFFFFF"; BG = "#F7F6F2"
LINEC = "#C9D0DC"
UNIT = {"B": "#2F6FE0", "O": "#E8872E", "G": "#97A1AC"}
NODEC = "#2E3D57"
NAMES = ["幕一 · 集中", "幕二 · 过载", "幕三 · 重新分配"]
PANEL_X = [24.0, 549.333, 1074.667]
PW = 501.333
COLORS = ["B", "O", "G"]  # U_i -> COLORS[i%3]：各幕同色（身份守恒）

def node_shapes(cx, cy, scale=1.0):
    N01 = dict(id="N01", kind="rrect", w=int(round(72 * scale)), h=int(round(72 * scale)),
               r=round(20 * scale), cx=cx, cy=cy)
    N02 = dict(id="N02", kind="diamond", w=72, h=72, cx=cx, cy=cy)
    N03 = dict(id="N03", kind="hex", w=72, h=62, cx=cx, cy=cy)
    return [N01, N02, N03]

def draw_node(n):
    if n["kind"] == "rrect":
        w, h = n["w"], n["h"]
        x, y = n["cx"] - w / 2, n["cy"] - h / 2
        S.append(f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}" color="{NODEC}" borderRadius="{n["r"]}" /></Positioned>')
        return x, y, x + w, y + h
    if n["kind"] == "diamond":
        w, h = n["w"], n["h"]
        path = f"M{w/2} 0 L{w} {h/2} L{w/2} {h} L0 {h/2} Z"
    else:
        w, h = n["w"], n["h"]
        path = (f"M{w*8/72} 0 L{w*64/72} 0 L{w} {h/2} L{w*64/72} {h} "
                f"L{w*8/72} {h} L0 {h/2} Z")
    x, y = n["cx"] - w / 2, n["cy"] - h / 2
    S.append(f'<Positioned left="{x}" top="{y}"><SizedBox width="{w}" height="{h}">'
             f'<ClipPath path="{path}" clipBehavior="ANTI_ALIAS"><Container width="{w}" height="{h}" color="{NODEC}" /></ClipPath>'
             f'</SizedBox></Positioned>')
    return x, y, x + w, y + h

def draw_unit(idx, cx, cy, color_key):
    S.append(f'<Positioned left="{cx - 18}" top="{cy - 18}">'
             f'<Container width="36" height="36" color="{UNIT[color_key]}" borderRadius="18" /></Positioned>')
    return dict(id=f"U{idx + 1:02d}", color=COLORS[idx % 3], color_hex=UNIT[color_key], diameter=36,
                center=[cx, cy])

def line(x1, y1, x2, y2):
    S.append(f'<Positioned left="{x1}" top="{y1}"><Container width="{max(abs(x2 - x1), 1.5)}" '
             f'height="{max(abs(y2 - y1), 1.5)}" color="{LINEC}" /></Positioned>')

def vl(x, y0, y1):
    line(x, y0, x, y1)

def report_min(units):
    mm = 1e9; pair = None
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            d = math.hypot(units[i]["center"][0] - units[j]["center"][0],
                           units[i]["center"][1] - units[j]["center"][1])
            if d < mm:
                mm, pair = d, (units[i]["id"], units[j]["id"])
    return mm, pair

def build(scheme):
    global S
    S = []
    S.append(f'<Positioned left="0" top="0"><Container width="1600" height="1000" color="{BG}" /></Positioned>')
    S.append(f'<Positioned left="0" top="30" width="1600"><Text fontSize="36" color="{INK}" '
             f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" textAlign="CENTER">集中 → 过载 → 重新分配</Text></Positioned>')
    acts = []
    for ai in range(3):
        px = PANEL_X[ai]
        S.append(f'<Positioned left="{px}" top="122"><Container width="{PW}" height="854" color="{PANEL}" borderRadius="14" border="1 SOLID #E4E1D8" /></Positioned>')
        S.append(f'<Positioned left="{px}" top="146" width="{PW}"><Text fontSize="24" color="#47506B" '
                 f'fontFamily="Noto Sans CJK SC" fontStyle="BOLD" maxLines="1" overflow="CLIP" textAlign="CENTER">{NAMES[ai]}</Text></Positioned>')
        body = act_scheme(scheme, ai, px + PW / 2)
        acts.append(body)
    dsl = ('<Snapshot background="%s" type="png"><Stack><SizedBox width="1600" height="1000" />'
           % BG + "".join(S) + "</Stack></Snapshot>")
    return dsl, acts

def act_scheme(scheme, ai, cx0):
    raise NotImplementedError

# 下面 act_scheme 由两种方案实现文件补齐（见 scheme_alpha.py / scheme_beta.py）
