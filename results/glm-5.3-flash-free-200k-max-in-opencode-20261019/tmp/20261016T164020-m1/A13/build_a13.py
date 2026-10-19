# -*- coding: utf-8 -*-
"""A13 终版：选择方向 A（叠层方片 + 圆孔负空间）。
四件最终图：symbol-color(512透明) / symbol-black(512透明 纯黑) / brand-banner(1200×400纸白) / launch-poster(1080×1350墨蓝)。
同一 mark() 几何生成器跨应用（同规则同比例，不嵌 PNG）。
方向 A 修订相对预览：顶层 α 45%→81%（孔内外对比增强）、孔半径 30→36。
"""
import io, sys, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A13")
os.makedirs(OUT, exist_ok=True)

C = {"blue": "#3D6FF2", "sky": "#7FB4FF", "ice": "#BCDCFF", "gold": "#F2C94C",
     "ink": "#0A162E", "ink2": "#13224A", "paper": "#F5F9FF", "sub": "#46608F",
     "line": "#D7E6FF", "darkline": "#30456F", "pale": "#9DBCE8"}
FAM = "Inter,Noto Sans CJK SC"
P0, R0, STEP0 = 220, 36, 48            # mark 母参数（512 母版）
HOLE0 = (110, 110, 36)                 # 孔心在顶层片内局部坐标、半径（512 母版）
A1, A2, A3 = "FF", "B8", "CF"          # 三层 alpha（彩版/黑版同构）
WARN = []

def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F: t += size * 1.0
        elif ch in "0123456789": t += size * 0.6
        elif ch == " ": t += size * 0.30
        elif ch.isupper(): t += size * 0.70
        else: t += size * 0.54
    return t

def fit(tag, s, size, box):
    w = estw(s, size)
    if w > box: WARN.append(f"{tag} estw {w:.0f}>{box}")

def rrect_path(x, y, w, h, r):
    return (f"M{x + r} {y} H{x + w - r} A{r} {r} 0 0 1 {x + w} {y + r} V{y + h - r} "
            f"A{r} {r} 0 0 1 {x + w - r} {y + h} H{x + r} A{r} {r} 0 0 1 {x} {y + h - r} "
            f"V{y + r} A{r} {r} 0 0 1 {x + r} {y} Z")

def hole_path(cx, cy, r):
    return f"M{cx + r} {cy} A{r} {r} 0 0 0 {cx - r} {cy} A{r} {r} 0 0 0 {cx + r} {cy} Z"

def mark_nodes(ox, oy, f, mode="color"):
    """叠光标志几何生成器：三片 220² r36 圆角方，步进 (+48,−48)，顶层片 EVEN_ODD 圆孔 r36 @片心。
    ox/oy = 512 母版坐标原点平移；f = 缩放。mode=color|black（黑版 RGB 恒 0，靠 alpha 分层）。"""
    if mode == "color":
        c1, c2, c3 = f'{C["blue"]}{A1}', f'{C["sky"]}{A2}', f'{C["ice"]}{A3}'
    else:
        c1 = c2 = c3 = None
        c1, c2, c3 = f"#000000{A1}", f"#000000{A2}", f"#000000{A3}"
    P, R, S_ = P0 * f, R0 * f, STEP0 * f
    hc, hu, hr = HOLE0[0] * f, HOLE0[1] * f, HOLE0[2] * f   # 孔心为顶层片局部坐标（片内居中）
    x3, y3 = (96 + 2 * STEP0) * f, 96 * f
    n = []
    n.append(f'<Positioned left="{ox + 96 * f}" top="{oy + (96 + 2 * STEP0) * f}"><Container width="{P}" height="{P}" borderRadius="{R}" color="{c1}" /></Positioned>')
    n.append(f'<Positioned left="{ox + (96 + STEP0) * f}" top="{oy + (96 + STEP0) * f}"><Container width="{P}" height="{P}" borderRadius="{R}" color="{c2}" /></Positioned>')
    pp = rrect_path(0, 0, P, P, R) + " " + hole_path(hc, hu, hr)
    n.append(f'<Positioned left="{ox + x3}" top="{oy + y3}"><SizedBox width="{P}" height="{P}"><ClipPath path="{pp}" fillRule="EVEN_ODD" clipBehavior="ANTI_ALIAS"><Container width="{P}" height="{P}" color="{c3}" /></ClipPath></SizedBox></Positioned>')
    return n

def T(x, y, s, size, color, bold=False, deco=False, deco_color=None):
    fit("T:" + s[:10], s, size, 2100)
    st = f' fontSize="{size}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: st += ' fontWeight="BOLD"'
    if deco: st += f' decoration="UNDERLINE" decorationColor="{deco_color or color}" decorationThickness="2"'
    return f'<Positioned left="{x}" top="{y}"><Text{st}>{s}</Text></Positioned>'

def Rc(x, y, w, h, color=None, radius=None, border=0, border_color=None):
    a = f'width="{w}" height="{h}"'
    if color: a += f' color="{color}"'
    if radius: a += f' borderRadius="{radius}"'
    if border: a += f' borderWidth="{border}" borderColor="{border_color}"'
    return f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>'

def snap(W, H, bg, body):
    b = f' background="{bg}"' if bg else ""
    return f'<Snapshot{b} type="png"><Stack><SizedBox width="{W}" height="{H}" />\n' + "\n".join(body) + "\n</Stack></Snapshot>"

def write(name, text):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(text)

# ---------- 1) symbol-color 512 透明 ----------
write("symbol-color.snapshot", snap(512, 512, None, mark_nodes(0, 0, 1, "color")))

# ---------- 2) symbol-black 512 透明（纯黑 #000000，alpha 分层 FF/B8/CF） ----------
write("symbol-black.snapshot", snap(512, 512, None, mark_nodes(0, 0, 1, "black")))

# ---------- 3) brand-banner 1200×400 纸白 ----------
MB = []                                    # 左标志 f=0.375 origin(48,104)
MB += mark_nodes(48, 104, 0.375, "color")
# 文案带：叠光 Layerlight 基线共享（CJK 56 / latin 44）
T_cjk_y, T_cjk_s = 140, 56
latin_s, latin_y = 44, T_cjk_y + T_cjk_s - 44
w_cjk = estw("叠光", T_cjk_s)              # 112
MB += [T(272, T_cjk_y, "叠光", T_cjk_s, C["ink"], bold=True),
       T(272 + w_cjk + 18, latin_y, "Layerlight", latin_s, C["ink"], bold=True)]
MB += [Rc(272, 224, 128, 8, C["gold"], radius=4),
       Rc(272, 224 + 14, 72, 8, C["sky"], radius=4)]
TB = []                                    # tagline + 副标语（双语说明）
fit("tagline", "把复杂信息，组织成清晰画面", 28, 1152 - 272)
MB.append(T(272, 262, "把复杂信息，组织成清晰画面", 28, C["sub"]))
TB.append(Rc(48, 344, 1104, 1, C["line"]))
TB.append(T(48, 358, "STRUCTURED VISUAL TOOLS · 信息叠加后仍然清晰", 18, C["sub"]))
# 右下角小型母体回声（同规则缩小 0.09，装饰不算新构件语言）
body = MB + TB
write("brand-banner.snapshot", snap(1200, 400, C["paper"], body))

# ---------- 4) launch-poster 1080×1350 墨蓝（独立构图） ----------
Z = []
Z += mark_nodes(410, 96, 260 / 512, "color")           # 大标志 260px 居中
pw = int(estw("OPEN BETA", 24) + 62)
Z += [Rc((1080 - pw) // 2, 396, pw, 48, C["gold"], radius=24),
      T((1080 - int(estw("OPEN BETA", 24))) // 2, 396 + 15, "OPEN BETA", 24, C["ink"], bold=True)]
title_y, title_s = 500, 104                              # 叠光（居中大字）
Z.append(T((1080 - int(estw("叠光", title_s))) // 2, title_y, "叠光", title_s, C["paper"], bold=True))
lw = estw("Layerlight", 56)                              # 纵向第二行，避免同轴碰撞
Z.append(T(int((1080 - lw) / 2), 630, "Layerlight", 56, C["paper"], bold=True))
tw = estw("把复杂信息，组织成清晰画面", 32)
Z.append(T(int((1080 - tw) / 2), 726, "把复杂信息，组织成清晰画面", 32, C["pale"]))
Z += [Rc(292, 790, 496, 1, C["darkline"])]
mw = int(estw("2026.11.07 · ONLINE", 28)) + 64
Z += [Rc((1080 - mw) // 2, 822, mw, 64, None, radius=32, border=2, border_color=C["darkline"]),
      T(int((1080 - int(estw("2026.11.07 · ONLINE", 28))) / 2), 822 + 17, "2026.11.07 · ONLINE", 28, C["paper"])]
ww = estw("layerlight.example.org", 26)
Z += [T(int((1080 - ww) / 2), 1188, "layerlight.example.org", 26, C["gold"], deco=True, deco_color=C["gold"]),
      Rc((1080 - 120) // 2, 1268, 120, 6, C["gold"], radius=3)]
write("launch-poster.snapshot", snap(1080, 1350, C["ink"], Z))

print("WARN", len(WARN))
for w in WARN: print(" -", w)
print("banner latin baseline:", latin_y, "poster asset widths:", int(estw("叠光", 104)), int(lw))
