"""B03 case-01：「夜航班」门头霓虹效果图 + 施工标注（2400×1200）。

受众：店主与招牌施工方；情境：夜间现场核对灯管颜色、字位与变压器回路。
手法：多层 textShadow 霓虹（探针 06b）、ClipOval 叠圆造月牙、仿射斜切雨棚（探针 02）、
RADIAL 焦点暖光（探针 05）、引导线点阵表格；右侧尺寸由左侧几何换算，不手填数字。
"""
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
for p in (ROOT / "tmp" / RID / "_suite" / "scripts", ROOT / "tmp" / RID / "B03"):
    sys.path.insert(0, str(p))
from dslkit import Doc, TextFit          # noqa: E402
import b03kit as K                        # noqa: E402

VER = os.environ.get("B03_VER", "v01")
W, H = 2400, 1200
M = 72
PX_TO_MM = 6                             # 出图换算：1 px = 6 mm


def mm(px):
    return round(px * PX_TO_MM)


def grp(v):
    return f"{v:,}".replace(",", " ")


def lerp(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_tone(y):
    """夜空分带渐变在 y 处的颜色，供月牙遮挡圆取色，避免叠色出现硬边。"""
    t = (y % (H / 6)) / (H / 6)
    return lerp("#07090E", "#0D1220", t / 0.5) if t < 0.5 else \
        lerp("#0D1220", "#080B12", (t - 0.5) / 0.5)


# ---------- 几何（右侧标注全部由此换算） ----------
CW = W - 2 * M
LW = 1480
RX = M + LW + 56
RW = W - M - RX
WX, WY, WW, WH = M, 168, LW, 876
GB = WY + WH                                    # 地面线

MAIN_SIZE, SUB_SIZE, HRS_SIZE = 190, 38, 30
WIN_W, WIN_H, WIN_Y = 300, 230, 672
WIN_XS = [WX + 96, WX + WW - 96 - WIN_W]
DW, DH = 250, 270
DX, DY = WX + (WW - DW) // 2, GB - DH
AW, AH = DW + 170, 74
AX, AY = DX - 85, DY - 38
MR, MX, MY = 52, 1352, 40                       # 月牙：屋顶上方的天空
SLOPE = 0.16

# 灯管长度：字高 × 每字笔画系数（CJK 约 7 倍字高，拉丁约 1.6 倍，空格 0.4）
def tube_metres(s, px_h):
    total = 0.0
    for c in s:
        if ord(c) >= 0x2E80:
            f = 7.0
        elif c == " ":
            f = 0.4
        elif c in "·–":
            f = 1.0
        elif c.isdigit() or c.isalpha():
            f = 1.6
        else:
            f = 0.5
        total += px_h * PX_TO_MM * f / 1000
    return round(total, 1)


T2_TEXT = "NIGHT FERRY · 精酿 黑胶 深夜食堂"
T1_LEN = tube_metres("夜航班", MAIN_SIZE)
T2_LEN = tube_metres(T2_TEXT, SUB_SIZE)
T3_LEN = round(math.pi * mm(2 * MR) * 1.15 / 1000, 1)
WIN_STRIP = round(2 * mm(WIN_W) / 1000, 1)

TUBES = [
    {"id": "T1", "name": "主标暖白", "hex": "#FFF3C4", "glow": "#E0A526",
     "model": "NEON-LED 8mm 2700K", "wpm": 18, "len": T1_LEN, "feed": "A"},
    {"id": "T2", "name": "副标琥珀", "hex": "#F6C87A", "glow": "#C8552B",
     "model": "NEON-LED 8mm 2200K", "wpm": 14, "len": T2_LEN, "feed": "A"},
    {"id": "T3", "name": "月牙冰蓝", "hex": "#BFE9FF", "glow": "#2E5468",
     "model": "FLEX 10mm 6500K", "wpm": 22, "len": T3_LEN, "feed": "B"},
]
FEED_LEN = {f: round(sum(t["len"] for t in TUBES if t["feed"] == f), 1)
            for f in ("A", "B")}
FEED_W = {f: round(sum(t["len"] * t["wpm"] for t in TUBES if t["feed"] == f))
          for f in ("A", "B")}
FEED_LEN["B"] = round(FEED_LEN["B"] + WIN_STRIP, 1)
FEED_W["B"] = round(FEED_W["B"] + WIN_STRIP * 14)
TRAFO = {"A": 450, "B": 150}
FEED_N = {f: max(1, math.ceil(FEED_W[f] * 1.2 / TRAFO[f])) for f in ("A", "B")}

d = Doc(W, H, bg="#07090E", font="Inter,Noto Sans CJK SC")
tf = TextFit()

# ---------- 夜空：分带渐变 + 环境光 + 星点 ----------
BAND = round(H / 6 + 1)
for i in range(6):
    d.pos(0, i * (H / 6), W, H / 6 + 1,
          f'<Container width="{W}" height="{BAND}" gradientType="LINEAR" '
          f'gradientColors="#07090E,#0D1220,#080B12" gradientStops="0,0.5,1" '
          f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>')
d.pos(0, 300, W, H - 300,
      f'<Container width="{W}" height="{H-300}" gradientType="RADIAL" '
      f'gradientColors="#C8552B26,#C8552B00" gradientCenter="BOTTOM_CENTER" '
      f'gradientRadius="0.72"/>')
STARS = [(118, 46, 3), (233, 96, 2), (356, 30, 2), (470, 118, 2), (598, 62, 3),
         (712, 132, 2), (838, 44, 2), (965, 104, 3), (1077, 58, 2), (1205, 126, 2),
         (1290, 34, 2), (1489, 54, 3), (1524, 120, 2), (430, 74, 2), (182, 128, 2)]
for sx, sy, sr in STARS:
    d.dot(sx, sy, sr, "#DFF3FF" if sr > 2 else "#8FA0B3")

# ---------- 立面：女儿墙压顶 + 砖墙 ----------
d.rect(WX - 10, WY - 18, WW + 20, 18, "#1B222C", radius=3)
d.pos(WX, WY, WW, WH,
      f'<Container width="{WW}" height="{WH}" borderRadius="6" gradientType="LINEAR" '
      f'gradientColors="#171C25,#10141B" gradientBegin="TOP_CENTER" '
      f'gradientEnd="BOTTOM_CENTER"/>')
for r in range(1, int(WH / 46)):
    y = WY + r * 46
    d.rect(WX, y, WW, 1, "#1D232E")
    off = 0 if r % 2 else 46
    for c in range(int(WW / 92)):
        x = WX + off + c * 92
        if x < WX + WW:
            d.rect(x, y - 46, 1, 46, "#1D232E")

# ---------- 霓虹主标 / 副标 / 营业时间 ----------
# 三层 ImageFiltered 模糊 + 芯层：辉光按字形外扩，不会被排版矩形裁成方板
MAIN_CY, SUB_CY, HRS_CY = 380, 552, 638
K.neon_if(d, WX, MAIN_CY - 230, WW, 460, "夜航班", MAIN_SIZE,
          core="#FFF6D8", glow=("#C8552B", "#E0A526", "#FFE9A8"),
          sigmas=(46, 22, 7), align="CENTER", font=d.font, tf=tf, tag="sign-main")
K.outline(d, tf, "sign-sub", WX + 180, SUB_CY - 60, WW - 360, 120,
           T2_TEXT, SUB_SIZE, "#F6C87A", align="CENTER", width=1.6)
K.neon_if(d, WX, HRS_CY - 70, WW, 140,
          "周二至周日 18:00 – 02:30 · 周一休整", HRS_SIZE,
          core="#EAF8FF", glow=("#2E5468", "#BFE9FF"), sigmas=(14, 5),
          style="NORMAL", align="CENTER", font=d.font, tf=tf, tag="sign-hours")

# 灯管分隔线：同一条矩形，一层模糊做辉光、一层实色做芯（ImageFiltered 复用）
DIV_Y, DIV_W = 700, 560
DIV_X = WX + (WW - DIV_W) // 2
for sig, col in ((9, "#E0A526"), (None, "#FFE9A8")):
    inner = f'<Container width="{DIV_W}" height="5" borderRadius="2.5" color="{col}"/>'
    d.pos(DIV_X, DIV_Y, DIV_W, 5,
          inner if sig is None else
          f'<ImageFiltered sigmaX="{sig}" sigmaY="{sig}">{inner}</ImageFiltered>')

# ---------- 月牙：亮圆 + 同色遮挡圆 + 外层辉光（ClipOval 层叠） ----------
# 辉光用 RADIAL 渐变而非 boxShadow：v01 的 boxShadow 光晕呈方角矩形，不跟随 borderRadius
GX, GY2 = MX + MR, MY + MR
GW = 2 * MR + 78
d.pos(MX, MY, MR * 2, MR * 2,
      f'<ClipOval clipBehavior="ANTI_ALIAS"><Container width="{MR*2}" height="{MR*2}" '
      f'gradientType="RADIAL" gradientColors="#DFF3FF,#8FD0F0,#2E5468" '
      f'gradientStops="0,0.66,1" gradientCenter="CENTER" gradientRadius="0.62"/>'
      f'</ClipOval>')
d.pos(MX + 30, MY - 10, MR * 2, MR * 2,
      f'<ClipOval clipBehavior="ANTI_ALIAS"><Container width="{MR*2}" height="{MR*2}" '
      f'color="{sky_tone(MY - 10 + MR)}"/></ClipOval>')
d.pos(GX - GW / 2, GY2 - GW / 2, GW, GW,
      f'<Container width="{GW}" height="{GW}" gradientType="RADIAL" '
      f'gradientColors="#BFE9FF4D,#BFE9FF1A,#BFE9FF00" gradientStops="0,0.42,1" '
      f'gradientCenter="CENTER" gradientRadius="0.5"/>')

# ---------- 窗：室内暖光（RADIAL 铺满窗洞）+ 吊灯与吧台 ----------
for i, gx in enumerate(WIN_XS):
    d.rect(gx, WIN_Y, WIN_W, WIN_H, "#0A0D12", radius=4)
    d.pos(gx, WIN_Y, WIN_W, WIN_H,
          f'<Container width="{WIN_W}" height="{WIN_H}" borderRadius="4" '
          f'gradientType="RADIAL" gradientColors="#F6C87A,#B07A2E,#241A12" '
          f'gradientStops="0,0.62,1" gradientCenter="CENTER" gradientRadius="1.0"/>')
    for k in (1, 2):
        px = gx + WIN_W * (0.32 if k == 1 else 0.68)
        d.line(px, WIN_Y + 10, px, WIN_Y + 52, 2, "#3A2E20")
        d.dot(px, WIN_Y + 58, 12, "#FFF3C4")
        d.pos(px - 26, WIN_Y + 32, 52, 52,
              f'<Container width="52" height="52" gradientType="RADIAL" '
              f'gradientColors="#FFE9A866,#FFE9A800" gradientStops="0,1" '
              f'gradientCenter="CENTER" gradientRadius="0.5"/>')
    d.rect(gx + 22, WIN_Y + WIN_H - 62, WIN_W - 44, 14, "#2A1D12", radius=2)
    d.rect(gx + WIN_W // 2 - 2, WIN_Y, 4, WIN_H, "#12161D")
    d.rect(gx, WIN_Y + WIN_H // 2, WIN_W, 4, "#12161D")
    d.rect(gx - 8, WIN_Y - 14, WIN_W + 16, 8, "#3A2E20", radius=2)
    d.rect(gx - 8, WIN_Y + WIN_H, WIN_W + 16, 9, "#1B222C", radius=2)
    K.tlab(d, tf, f"win{i}", gx - 8, WIN_Y + WIN_H + 14, WIN_W + 16, 26,
           "试听窗 · 周五至周日 20:00 起", 17, "#8FA0B3", align="CENTER")

# ---------- 门 + 雨棚（先门后棚，棚在门前出挑） ----------
d.rect(DX, DY, DW, DH, "#0B0E13", radius=4)
d.pos(DX, DY, DW, DH, f'<Container width="{DW}" height="{DH}" borderRadius="4" '
                      f'border="2 SOLID #3A2E20"/>')
d.rect(DX + 18, DY + 18, DW - 36, DH - 56, "#0E1319", radius=3)
d.rect(DX + DW - 26, DY + DH / 2 - 62, 8, 80, "#8A6A3A", radius=4)
K.tlab(d, tf, "door", DX, DY + 72, DW, 30, "推 · PULL", 20, "#6E7F8D", align="CENTER")
K.xform(d, AX, AY, AW, AH, K.skew(x=math.atan(SLOPE)),
        f'<Container width="{AW}" height="{AH}" gradientType="LINEAR" '
        f'gradientColors="#2A2118,#1B1E22" gradientBegin="TOP_CENTER" '
        f'gradientEnd="BOTTOM_CENTER" borderRadius="4"/>', align="TOP_LEFT")
for i in range(13):
    x = AX + 10 + i * ((AW - 20) / 12)
    d.line(x, AY + 5, x + SLOPE * (AH - 10), AY + AH - 5, 2, "#33291D")
# 雨棚前沿灯管：由粗到细三层叠色模拟辉光（斜切后与棚面同角）
for th, col in ((11, "#E0A52626"), (6, "#E0A52666"), (2, "#FFE9A8")):
    d.line(AX, AY + AH, AX + AW + SLOPE * AH, AY + AH, th, col)

# 壁灯：门两侧各一盏，暖光在墙上洗出光锥
for sx in (DX - 132, DX + DW + 132):
    d.rect(sx - 3, DY + 20, 6, 26, "#2A3140", radius=2)
    d.pos(sx - 60, DY + 34, 120, 120,
          f'<Container width="120" height="120" gradientType="RADIAL" '
          f'gradientColors="#F6C87A59,#F6C87A00" gradientStops="0,1" '
          f'gradientCenter="CENTER" gradientRadius="0.5"/>')
    d.pos(sx - 26, DY + 46, 52, 210,
          f'<Container width="52" height="210" gradientType="LINEAR" '
          f'gradientColors="#F6C87A00,#F6C87A4D,#F6C87A00" gradientStops="0,0.14,1" '
          f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>')
    d.rect(sx - 13, DY + 40, 26, 18, "#FFE9A8", radius=4)
    d.line(sx, DY + 58, sx, DY + 66, 2, "#8A6A3A")

# ---------- 地面：湿沥青 + 灯光水洼 ----------
d.rect(0, GB, W, H - GB, "#0A0C11")
d.rect(0, GB, W, 3, "#1B222C")
for cx, cw, col in [(DX + DW / 2, 520, "#F6C87A73"),
                    (WIN_XS[0] + WIN_W / 2, 330, "#F6C87A33"),
                    (WIN_XS[1] + WIN_W / 2, 330, "#F6C87A33")]:
    d.pos(cx - cw / 2, GB, cw, 96,
          f'<Container width="{cw}" height="96" gradientType="RADIAL" '
          f'gradientColors="{col},#00000000" gradientStops="0,1" '
          f'gradientCenter="TOP_CENTER" gradientRadius="0.8"/>')
# 湿沥青上的霓虹倒影：竖向渐变条再经 ImageFiltered 模糊，得到拖尾而非硬边柱
for rx, rw, rh, ra in ((560, 34, 66, "2E"), (720, 44, 74, "33"), (812, 48, 78, "3A"),
                       (980, 34, 68, "2E"), (400, 30, 56, "22"), (1320, 30, 58, "22")):
    strip = (f'<Container width="{rw}" height="{rh}" gradientType="LINEAR" '
             f'gradientColors="#FFE9A800,#FFE9A8{ra},#FFE9A800" gradientStops="0,0.2,1" '
             f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>')
    d.pos(rx - rw / 2, GB, rw, rh,
          f'<ImageFiltered sigmaX="10" sigmaY="10">{strip}</ImageFiltered>')

# ---------- 立面尺寸线（下方） ----------
GY = GB + 40
d.line(WX, GY, WX + WW, GY, 2, "#4A5568")
for gx in (WX, WX + WW):
    d.line(gx, GY - 12, gx, GY + 12, 2, "#4A5568")
K.tlab(d, tf, "dim-wall", WX, GY + 8, WW, 26,
       f"立面总宽 {grp(mm(WW))} mm（1 px = {PX_TO_MM} mm 折算）", 17, "#8FA0B3",
       align="CENTER")

# ---------- 右侧施工图例 ----------
K.tlab(d, tf, "rt-head", RX, M + 6, RW, 40, "施工标注 · 灯管与回路", 30, "#F2EBDD",
       style="BOLD")
d.rect(RX, M + 54, RW, 2, "#2A3140")

yy = M + 78
for t in TUBES:
    d.rect(RX, yy, 60, 60, t["hex"], radius=8)
    d.pos(RX, yy, 60, 60, f'<Container width="60" height="60" borderRadius="8" '
                          f'border="1 SOLID #3A4252"/>')
    K.tlab(d, tf, f"t{t['id']}h", RX + 78, yy - 2, RW - 78, 26,
           f"{t['id']} {t['name']} · {t['model']}", 20, "#F2EBDD", style="BOLD")
    K.tlab(d, tf, f"t{t['id']}p", RX + 78, yy + 26, RW - 78, 22,
           f"{t['wpm']} W/m　估算用量 {t['len']} m　{t['feed']} 回路", 17, "#8FA0B3")
    K.tlab(d, tf, f"t{t['id']}x", RX + 102, yy + 50, RW - 102, 20,
           f"色芯 {t['hex']} ／ 辉光 {t['glow']}", 16, "#8FA0B3")
    d.rect(RX + 78, yy + 52, 16, 16, t["glow"], radius=3)
    yy += 92

yy += 6
K.tlab(d, tf, "feed-head", RX, yy, RW, 30, "回路分配", 22, "#F2EBDD", style="BOLD")
yy += 40
FEEDS = [("A", "主标 + 副标", "门楣左侧检修口"),
         ("B", "月牙 + 窗檐灯带", "室内配电箱 B3")]
for code, scope, where in FEEDS:
    detail = (f"{FEED_N[code]} 台 × {TRAFO[code]} W（负载 {FEED_W[code]} W，余量 20%）"
              f" · {where}")
    d.rect(RX, yy, 34, 34, "#2E5468", radius=6)
    K.tlab(d, tf, f"fc{code}", RX, yy + 4, 34, 26, code, 20, "#F2EBDD",
           style="BOLD", align="CENTER")
    K.leader_dots(d, RX + 48, yy, RW - 48, scope,
                  f"{FEED_LEN[code]} m ／ {FEED_W[code]} W",
                  19, "#D8CFC0", "#4A5568", dot=3, pitch=11, title_w=280, page_w=200)
    K.tlab(d, tf, f"fn{code}", RX + 48, yy + 30, RW - 48, 22, detail, 16, "#8FA0B3")
    yy += 64

yy += 10
K.tlab(d, tf, "dim-head", RX, yy, RW, 30, "关键尺寸（由左图几何换算）", 22, "#F2EBDD",
       style="BOLD")
yy += 42
DIMS = [("主标字高", grp(mm(MAIN_SIZE))),
        ("主标底离地", grp(mm(GB - (MAIN_CY + MAIN_SIZE / 2)))),
        ("月牙外径", grp(mm(2 * MR))),
        ("雨棚 宽 × 出挑", f"{grp(mm(AW))} × {grp(mm(SLOPE * AH))}"),
        ("门洞净尺 宽×高", f"{grp(mm(DW))} × {grp(mm(DH))}"),
        ("窗洞净尺 宽×高", f"{grp(mm(WIN_W))} × {grp(mm(WIN_H))} × 2")]
for k, v in DIMS:
    K.leader_dots(d, RX, yy, RW, k, v, 19, "#D8CFC0", "#4A5568",
                  title_w=250, page_w=210)
    yy += 38

# ---------- 页脚 ----------
FY = H - 58
d.rect(M, FY - 14, CW, 1, "#2A3140")
K.tlab(d, tf, "foot", M, FY - 8, CW * 0.62, 26,
       "夜航班 NIGHT FERRY · 虚构演示品牌 · 效果图与施工标注同图出图，"
       "灯管长度按字高 × 笔画系数估算，灯位以现场复核为准", 17, "#8FA0B3")
K.tlab(d, tf, "ver", M + CW * 0.62, FY - 8, CW * 0.38, 26,
       f"B03 case-01 · {VER} · 2400×1200 · 2026-10-10", 17, "#6E7F8D", align="END")

dsl = d.dsl()
out = ROOT / "tmp" / RID / "B03" / f"case01-{VER}.snapshot"
out.write_text(dsl, encoding="utf-8")
print(VER, "chars", len(dsl), "TextFit", tf.n, "problems", len(tf.problems))
for p in tf.problems[:12]:
    print("  !", p)
print("lens", T1_LEN, T2_LEN, T3_LEN, "strip", WIN_STRIP,
      "feedW", FEED_W, "feedLen", FEED_LEN, "trafoN", FEED_N)
