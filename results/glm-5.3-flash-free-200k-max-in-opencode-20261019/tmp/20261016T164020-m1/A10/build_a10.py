# -*- coding: utf-8 -*-
"""A10 · 透明合成与滤镜语义实验板（1440×1100，六格 320×240）。
① 双 50%alpha 矩形 / ② Opacity(0.5) 组 / ③ 背景模糊卡 / ④ 子树模糊卡 / ⑤ MULTIPLY+子树模糊 / ⑥ 同⑤+圆形裁剪。
产出 compositing-lab.snapshot + composite-audit.json（panels/paired_scenes/samples/visual_checks）。
"""
import io, sys, json, os, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A10")
os.makedirs(OUT, exist_ok=True)

W, H = 1440, 1100
AW, AH = 320, 240
GX0 = (W - 3 * AW - 2 * 32) // 2          # 208
ROW0, ROW1 = 170, 530
ORIGINS = {1: (GX0, ROW0), 2: (GX0 + 352, ROW0), 3: (GX0 + 704, ROW0),
           4: (GX0, ROW1), 5: (GX0 + 352, ROW1), 6: (GX0 + 704, ROW1)}

BG = "#F4F7FB"; PAGE_F = "#0F172A"; SUB = "#55657F"; FAINT = "#94A3B8"; BORDER = "#E2E8F0"
FAM = "Inter,Noto Sans CJK SC"
SIGMA = 6

WARN = []
def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F: t += size * 1.0
        elif ch in "0123456789": t += size * 0.6
        elif ch == " ": t += size * 0.30
        elif ch.isupper(): t += size * 0.70
        elif ch in "·—（）()→=.,+×:/°#%": t += size * 0.5
        else: t += size * 0.54
    return t
def fit(tag, s, size, box):
    w = estw(s, size)
    if w > box: WARN.append(f"{tag} estw {w:.0f}>{box}: {s}")
def text(x, y, s, size, color, bold=False, align="START", box_w=None):
    sty = f' fontSize="{size}" color="{color}" fontFamily="{FAM}" maxLines="1" overflow="CLIP"'
    if bold: sty += ' fontWeight="BOLD"'
    if align != "START": sty += f' textAlign="{align}"'
    s = s.replace("&", "&amp;")
    if box_w is None:
        return f'<Positioned left="{x}" top="{y}"><Text{sty}>{s}</Text></Positioned>'
    return f'<Positioned left="{x}" top="{y}" width="{box_w}"><Text{sty}>{s}</Text></Positioned>'
def rect(x, y, w2, h2, color, radius=None, border=None, shadow=None):
    a = f'width="{w2}" height="{h2}"' + (f' color="{color}"' if color else "")
    if radius: a += f' borderRadius="{radius}"'
    if border: a += f' border="{border}"'
    if shadow: a += f' boxShadow="{shadow}"'
    return f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>'

def area_frame(px, py):
    return rect(px, py, AW, AH, "#FFFFFF", border=f"1 SOLID {BORDER}")

def stripes(extra=()):
    """全幅竖条纹：色 #5B7395 宽28 · 间距28（节距56）· 相位 x=0，跨卡片边"""
    out = [rect(k * 56, 0, 28, AH, "#5B7395") for k in range(6)]
    for e in extra: out.append(e)
    return out

def glass(px, py, label, front_color=FAM):
    """卡片共享前景：tint(白 35%) + 文字 + 前景形状（card 局部坐标，卡左上 = 区局部(40,40)）"""
    S = []
    S.append(rect(0, 0, 240, 160, "#FFFFFF59"))
    S.append(text(22, 54, label, 24, "#0B1220", bold=True))
    S.append(rect(22, 102, 120, 26, "#F6B94A", radius=6))
    S.append(rect(156, 102, 26, 26, "#334155"))
    return S

def card_pos(): return (40, 40, 240, 160)

S = [rect(0, 0, W, H, BG)]
# —— 标题带 ——
S.append(text(GX0, 34, "看到差异，才能说用对了", 36, PAGE_F, bold=True))
s_badge = "实验区 320×240 · 采样 局部(180,100)"
fit("badge", s_badge, 20, 460)
S.append(text(GX0 + 3 * AW + 2 * 32 - 460, 44, s_badge, 20, SUB, align="END", box_w=460))
s_sub = "①② 半透明来源不同（128/255 vs 组 0.5）· ③④ 背景模糊 vs 子树模糊 · ⑤⑥ MULTIPLY+子树模糊（⑥ 圆剪）"
fit("sub", s_sub, 20, 1000)
S.append(text(GX0, 96, s_sub, 20, SUB))
S.append(rect(GX0, 138, 3 * AW + 64, 1, BORDER))

DESC = {
    1: ("① 每矩形自带 50% 透明",
        "#FF000080/#0000FF80→128/255",
        "重叠理论 (127,127,191)"),
    2: ("② 相同两矩形 → Opacity(0.5) 组",
        "组内先不透明合成：重叠=纯蓝",
        "0.5 上白 → 理论 (128,128,255)"),
    3: ("③ 仅背景模糊（BackdropFilter）",
        "σ6 背景 + 玻璃 #FFFFFF59",
        "SHARP 与前景清晰，卡外锐利"),
    4: ("④ 子树模糊（ImageFiltered）",
        "白底+条纹+前景+文字 一起糊",
        "与 ③ 仅差模糊所作用的层"),
    5: ("⑤ MULTIPLY → 子树模糊 σ6",
        "白→琥珀、深块更暗（间隙同命色）",
        "无裁剪，效果铺满全实验区"),
    6: ("⑥ 同⑤效果，最外层加 ClipOval r100",
        "圆心(160,120)；圆内=滤色模糊",
        "圆外=同一基础场景锐利"),
}
def panel(n):
    px, py = ORIGINS[n]
    S = [area_frame(px, py)]
    # 区内容：Stack 裁剪由 Stack(hardEdge) 承担
    inner = []
    if n == 1:
        inner.append(rect(40, 40, 160, 120, "#FF000080"))
        inner.append(rect(120, 80, 160, 120, "#0000FF80"))
    elif n == 2:
        g = f'<Positioned left="{0}" top="{0}" width="{AW}" height="{AH}"><Opacity opacity="0.5">' \
            f'<Stack><SizedBox width="{AW}" height="{AH}" />' \
            + rect(40, 40, 160, 120, "#FF0000") + rect(120, 80, 160, 120, "#0000FF") \
            + "</Stack></Opacity></Positioned>"
        inner.append(g)
    elif n in (3, 4):
        inner += stripes()
        if n == 3:
            inner.append('<Positioned left="40" top="40" width="240" height="160">'
                         '<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
                         '<BackdropFilter sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack>'
                         + "".join(glass(0, 0, "SHARP"))
                         + "</Stack></BackdropFilter></ClipRRect></Positioned>")
        else:
            # 子树=白底 + 条纹复刻（同一相位）+ 同前景
            rep = [rect(0, 0, 240, 160, "#FFFFFF")]
            rep += [rect(k * 56 - 40, 0, 28, 160, "#5B7395") for k in range(1, 6)]
            rep += glass(0, 0, "BLUR")
            inner.append('<Positioned left="40" top="40" width="240" height="160">'
                         '<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">'
                         '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack>'
                         + "".join(rep)
                         + "</Stack></ImageFiltered></ClipRRect></Positioned>")
    else:
        scene = [rect(24, 24, 272, 200, "#8EC3F0"),
                 rect(52, 54, 84, 64, "#1B2B4B"),
                 rect(196, 128, 76, 56, "#22304A"),
                 rect(108, 96, 60, 40, "#F2C94C", shadow="0 6 14 0 #00000055 NORMAL")]
        if n == 5:
            inner.append(f'<Positioned left="0" top="0" width="{AW}" height="{AH}">'
                         '<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">'
                         '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">'
                         f'<Stack><SizedBox width="{AW}" height="{AH}" />'
                         + "".join(scene) + "</Stack></ImageFiltered></ColorFiltered></Positioned>")
        else:
            inner += scene                                # 圆外锐利基础场景
            # 圆内：白底替换 + 基础场景复刻（偏移 -60,-20）+ 同效果
            rep = [rect(0, 0, 200, 200, "#FFFFFF"),
                   rect(-36, 4, 272, 200, "#8EC3F0"),
                   rect(-8, 34, 84, 64, "#1B2B4B"),
                   rect(136, 108, 76, 56, "#22304A"),
                   rect(48, 76, 60, 40, "#F2C94C", shadow="0 6 14 0 #00000055 NORMAL")]
            inner.append('<Positioned left="60" top="20" width="200" height="200">'
                         '<ClipOval><ColorFiltered color="#F6B94A" blendMode="MULTIPLY">'
                         '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP"><Stack>'
                         + "".join(rep) + "</Stack></ImageFiltered></ColorFiltered></ClipOval></Positioned>")
    S.append(f'<Positioned left="{px}" top="{py}" width="{AW}" height="{AH}"><ClipRect><Stack>'
             + "".join(inner) + f"</Stack></ClipRect></Positioned>")
    # 区外侧：编号+三行说明
    S.append(text(px, py + AH + 12, DESC[n][0], 20, PAGE_F, bold=True))
    for li in (1, 2):
        fit("desc%d_%d" % (n, li), DESC[n][li], 20, 336)
        S.append(text(px, py + AH + 38 + 26 * (li - 1), DESC[n][li], 20, SUB))
    return S

for n in (1, 2, 3, 4, 5, 6):
    S += panel(n)

# —— 底部说明带 ——
fy = ROW1 + AH + 98
S.append(rect(GX0, fy, 3 * AW + 64, 1, BORDER))
notes = [
    "共用③④：卡 240×160 圆角20 @(40,40) · 条纹 #5B7395 宽28 节距56 相位0 · 玻璃 #FFFFFF59",
    "③ 仅糊卡处既有背景（SHARP 清晰）· ④ 白底+条纹复刻+前景+文字整块糊 σ6",
    "共用⑤⑥：底景 #8EC3F0 (24,24) 272×200 · 深块 ×2 · #F2C94C 片 boxShadow 0 6 14 #00000055",
    "⑤⑥：ColorFiltered #F6B94A MULTIPLY → 子树模糊 σ6 CLAMP；⑥ 外加 r100 圆剪 @(160,120)，⑤ 无裁剪",
    "采样 ①(388,270) ②(740,270) · 未预乘 RGBA · 逐通道误差 ≤3 · 依据 docs 缓存 parser-tags/painting",
]
for i, s in enumerate(notes):
    fit("note%d" % (i + 1), s, 20, 1000)
    S.append(text(GX0, fy + 18 + i * 28, s, 20, SUB))

dsl = f'<Snapshot background="{BG}" type="png"><Stack><SizedBox width="{W}" height="{H}" />\n' + "\n".join(S) + "\n</Stack></Snapshot>"
open(os.path.join(OUT, "compositing-lab.snapshot"), "w", encoding="utf-8").write(dsl)

# ---------------- composite-audit.json ----------------
a = 128 / 255
g1 = (1 - a) * 255            # 红过白后 G=127
b1 = g1                        # B 同
r1 = a * 255 + (1 - a) * 255   # R255
exp1 = [math.floor(v + 0.5) for v in ((1 - a) * 255, (1 - a) * g1, a * 255 + (1 - a) * g1)]
# ② 组：重叠处=纯蓝(0,0,255)，整体 0.5 上白
e2 = [0.5 * 0 + 0.5 * 255, 0.5 * 0 + 0.5 * 255, 0.5 * 255 + 0.5 * 255]
exp2 = [math.floor(v + 0.5) for v in e2]

audit = {
    "schema_version": 1, "task_id": "A10", "path_base": "output_dir",
    "canvas": {"size": [W, H], "background": BG},
    "coordinate_system": {
        "unit": "px", "origin": "画布左上，x 右/y 下",
        "panels_local": "每格 320×240 实验区局部原点=该区左上外边界；镜头像素=decode PNG[(ox+lx),(oy+ly)]（0 基）",
        "sample_point_local": [180, 100],
    },
    "panels": [
        {"panel": n, "origin_canvas": list(ORIGINS[n]), "size": [AW, AH],
         "sample_local": [180, 100], "sample_canvas": [ORIGINS[n][0] + 180, ORIGINS[n][1] + 100],
         "scene": {"red_rect_local": [40, 40, 160, 120], "blue_rect_local": [120, 80, 160, 120], "blue_on_top": True} if n in (1, 2) else
                  ({"stripe_color": "#5B7395", "stripe_width": 28, "pitch": 56, "phase": "x=0",
                    "card_local": [40, 40, 240, 160], "card_radius": 20, "label": "SHARP" if n == 3 else "BLUR",
                    "front": ["#F6B94A 120×26 r6", "#334155 26×26"], "glass": "#FFFFFF59"}
                   if n in (3, 4) else
                   {"top_rect": "#8EC3F0 24,24 272×200", "dark_rects": ["#1B2B4B 52,54 84×64", "#22304A 196,128 76×56"],
                    "chip": "#F2C94C 108,96 60×40", "chip_shadow": "0 6 14 0 #00000055 NORMAL", "transparent_gaps": "未绘制区域（间隙）"}),
         "effect_node": {"1": "双 Container 颜色 #FF000080/#0000FF80（CSS #RRGGBBAA，末二位 alpha=0x80）",
                          "2": "<Opacity opacity=0.5> 包裹完全不透明 #FF0000/#0000FF（Stack 320×240）",
                          "3": "<ClipRRect r20><BackdropFilter sigmaX=6 sigmaY=6 tileMode=CLAMP>",
                          "4": "<ClipRRect r20><ImageFiltered sigmaX=6 sigmaY=6 tileMode=CLAMP>（子树含白底+条纹复刻+玻璃+文字+前景）",
                          "5": "<ColorFiltered color=#F6B94A blendMode=MULTIPLY><ImageFiltered 6,6>",
                          "6": "<ClipOval 200×200@局部(60,20)> 包裹 <ColorFiltered #F6B94A MULTIPLY><ImageFiltered 6,6>（子树=白底+场景复刻偏移(-60,-20)）"}[str(n)]}
        for n in range(1, 7)
    ],
    "paired_scenes": [
        {"pair": "P34", "shared": {"stripes": "#5B7395 宽14 节距28 相位x=0 全幅", "card": "240×160 r20 @区局部(40,40)",
                                    "glass_tint": "#FFFFFF59（白 alpha 0x59）", "text": "24px bold #0B1220（SHARP/BLUR）",
                                    "front_shapes": ["#F6B94A 120×26 r6 @(22,102)", "#334155 26×26 @(156,102)"],
                                    "sigma": 6, "tileMode": "CLAMP"},
         "unique_diff": "③ 仅对卡覆盖处的既有背景做 BackdropFilter，文字/前景保持清晰；④ 相同范围的背景+文字+前景整体子树 ImageFiltered",
         "clip_geometry": "两者均为 ClipRRect borderRadius=20 @区局部(40,40,240×160)；卡外条纹共用同一相位保持锐利"},
        {"pair": "P56", "shared": {"scene": ["#8EC3F0 (24,24) 272×200", "#1B2B4B (52,54) 84×64", "#22304A (196,128) 76×56",
                                             "#F2C94C (108,96) 60×40 boxShadow 0 6 14 0 #3A000000 NORMAL"],
                                    "transparent_gaps": "形状之间未绘制区域", "color_filter": "#F6B94A MULTIPLY",
                                    "blur": "sigmaX=sigmaY=6 tileMode=CLAMP"},
         "unique_diff": "⑤ 无裁剪（整区滤色+模糊），⑥ 最外层加 ClipOval",
         "clip_geometry": "圆心=区局部(160,120)，半径100 → ClipOval 盒 局部(60,20,200×200)；跨圆周证据：#8EC3F0 矩形同时覆盖圆内/外，圆周处与圆外锐利同色但明显模糊差异",
         "rim_crossing": "圆周与 #8EC3F0 相交于 y≈30..214 多处（例如 y=30 时 x≈116/204），圆周内琥珀色调+模糊、圆外原色锐利"},
    ],
    "alpha_models": {
        "panel1": {"alpha": "128/255 = 0.5019607843…（每矩形各自携带）", "order": "蓝 over 红 over 白；source-over、sRGB 0–255；中间不取整",
                   "steps": [
                       {"op": "红(255,0,0) over 白", "rgb": [255, round((1 - a) * 255, 6), round((1 - a) * 255, 6)]},
                       {"op": "蓝(0,0,255) over 上一步", "rgb": [round((1 - a) * 255, 6), round((1 - a) * ((1 - a) * 255), 6),
                                                                  round(a * 255 + (1 - a) * ((1 - a) * 255), 6)]}],
                   "expected_rgb": exp1,
                   "formula": {"R": "红 R=255 未被红衰减；蓝 R=0 → (1−a)·255 = 127",
                                "G": "(1−a)·[(1−a)·255] = (127/255)²·255 = 63.2549…（红残余 G=127 再被蓝衰减一次）",
                                "B": "a·255 + (1−a)·127 = 191.2549…"},
                   "rounding": "floor(v+0.5)",
                   "note": "逐矩形 alpha 的要害：红在半透明蓝下仍按 (1−a) 权重参与，红残余（G=127）再衰减一次 → G=63；与②组透明度的 128 差 65，语义差别一目了然。"},
        "panel2": {"alpha": "0.5（组层透明度，非逐矩形）", "order": "组内：不透明蓝完全盖住红 → 组层重叠(0,0,255)；组层 over 白 · 0.5",
                   "expected_rgb": exp2, "formula": {"R": "0.5·0+0.5·255 = 127.5", "G": "127.5", "B": "0.5·255+0.5·255 = 255"},
                   "rounding": "floor(v+0.5)",
                   "note": "② 与①的本质差别：组透明度先完全不透明地合成子树（遮挡两次不再衰减）再整体乘 0.5；重叠处显示纯蓝的 50% 版本，B=255 而 ① B=191。若运行时把组 alpha 量化（实测有效 α≈129/255），会向 (126,126,255) 偏 2，仍在每通道 ≤3 容差内；红/蓝单区实测 (255,126,126)/(126,126,255) 与该量化一致（推测为 Skia 层 alpha 量化，未查源码确认）。"},
    },
    "samples": [],
    "visual_checks": [],
}
open(os.path.join(OUT, "composite-audit.json"), "w", encoding="utf-8").write(json.dumps(audit, ensure_ascii=False, indent=1))
print("audit written; exp1", exp1, "exp2", exp2)
print("WARN", len(WARN))
for w in WARN: print(" -", w)
