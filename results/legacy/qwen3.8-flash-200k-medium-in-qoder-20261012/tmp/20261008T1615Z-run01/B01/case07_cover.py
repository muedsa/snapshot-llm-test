"""B01 case-07 · 深度报道杂志封面（1240×1750）。

受众：《暗礁》月刊订阅者在报刊亭/电子屏前停下的 3 秒。封面要在 3 秒里回答
「这期讲什么、值不值得买」，并把编辑部的真实信息（期号、定价、ISSN、条码、
篇数与字数）排在一起。全部统计量由下面那张目录表反算：篇数、总字数、最长篇、
通读分钟数、封面报道阅读时长、条码校验位，改目录表任一数字整张封面同步。
杂志名、文章标题、记者署名、ISSN/CN/邮发代号与条码号码均为虚构演示数据。
"""
import math
import os
import statistics
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from dslkit import Doc, TextFit, n  # noqa: E402
import b01kit as K  # noqa: E402

OUT = root / "tmp" / rid / "B01" / "case-07"
OUT.mkdir(parents=True, exist_ok=True)

# ==================== 数据 ====================
MAG = "暗礁"
LATIN = "REEF"
ISSUE_YEAR, ISSUE_MONTH = 2026, 11
NO = 148                       # 总第 148 期
PRICE = 28.00
ISSN = "1234-5670"
CN = "CN 31-2088/G2"
POST = "邮发代号 4-731"
CPM = 400                      # 成人中文默读速度 字/分钟

# (页码, 栏目, 标题, 作者, 字数)
TOC = [
    (14, "封面报道", "潮汐退去之后：一座渔港的十年账本", "沈知远", 21600),
    (46, "调查", "围塘、盐碱与一笔没结清的补偿款", "陆行舟", 9800),
    (58, "人物", "最后一个守灯塔的人", "周砚", 6400),
    (66, "数据", "三十年海岸线变迁：哪些村子从地图上消失了", "编辑部", 5200),
    (74, "现场", "休渔期的第一条船", "何见山", 3800),
    (80, "专栏", "海的账，谁来对", "林白", 2600),
    (86, "影像", "盐霜下的晒盐场（摄影组照）", "何见山", 1200),
    (94, "非虚构", "渔嫂的记账本", "沈知远", 7400),
    (104, "译作", "公海的悲剧：一篇 1968 年的报道", "陈遂 译", 6800),
    (112, "手记", "采访笔记：十二次往返大堤", "沈知远", 3100),
    (118, "书评", "当海洋史走进普通县城", "江晚", 2400),
    (124, "讣告", "老船长吴亚水（1943—2026）", "编辑部", 900),
]
N_ART = len(TOC)
TOTAL_WORDS = sum(t[4] for t in TOC)
LONGEST = max(TOC, key=lambda t: t[4])
SHORTEST = min(TOC, key=lambda t: t[4])
MEDIAN = statistics.median(t[4] for t in TOC)
READ_MIN = TOTAL_WORDS / float(CPM)
FEAT = TOC[0]
FEAT_MIN = FEAT[4] / float(CPM)
AVG_WORDS = TOTAL_WORDS / float(N_ART)

BAR_PREFIX = "977" + ISSN.replace("-", "") + "0"   # 977 + ISSN + 演示后缀


def ean13(d12):
    L = ["0001101", "0011001", "0010011", "0111101", "0100011",
         "0110001", "0101111", "0111011", "0110111", "0001011"]
    G = ["0100111", "0110011", "0011011", "0100001", "0011101",
         "0111001", "0000101", "0010001", "0001001", "0010111"]
    R = ["".join("1" if c == "0" else "0" for c in x) for x in L]
    PAR = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
           "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]
    ds = [int(c) for c in d12]
    chk = (10 - sum(ds[i] * (1 if i % 2 == 0 else 3) for i in range(12)) % 10) % 10
    digits = ds + [chk]
    bits = "101"
    for i in range(6):
        p = PAR[digits[0]][i]
        bits += (L, G)[p == "G"][digits[i + 1]]
    bits += "01010"
    for i in range(6, 12):
        bits += R[digits[i + 1]]
    bits += "101"
    return bits, chk


BAR_BITS, BAR_CHK = ean13(BAR_PREFIX)
BAR_TEXT = BAR_PREFIX + str(BAR_CHK)

# ==================== 画布 ====================
W, H = 1240, 1750
PAPER = "#F2EEE5"
INK = "#12151C"
ACC = "#B4442C"
d = Doc(W, H, bg=PAPER, palette={"t0": INK, "t1": "#4A5262", "t2": "#8A90A0",
                                 "card": PAPER, "card2": "#E7E1D5",
                                 "border": "#CFC7B7", "row": "#E7E1D5",
                                 "red": ACC, "cyan": "#1E466E"})
P = d.P
tf = TextFit()
tag = "c7"
ART_H = 1100


def L(x, y, w, h, s, size, col=None, style=None, align="START", valign="MIDDLE",
      **kw):
    tf.check(tag, s, size, w, h)
    d.label(x, y, w, h, s, col or P["t0"], size, style, align=align,
            valign=valign, **kw)


def layer(x, y, w, h, draw, filt=None, clip=None):
    sd = Doc(w, h, palette=P)
    draw(sd, w, h)
    inner = ('<Container width="%s" height="%s"><Stack alignment="TOP_LEFT" '
             'clipBehavior="NONE">%s</Stack></Container>'
             % (n(w), n(h), "".join(sd.parts)))
    if clip:
        inner = '<ClipRRect borderRadius="%s" clipBehavior="ANTI_ALIAS">%s</ClipRRect>' % (clip, inner)
    if filt:
        inner = '<ColorFiltered color="%s" blendMode="%s">%s</ColorFiltered>' % (
            filt[0], filt[1], inner)
    d.pos(x, y, w, h, inner)


# ==================== 封面摄影（纯 DSL 构成 + 双色叠印） ====================
SUNFX, SUNFY = 0.70, 0.845          # 落日圆心（相对天空层）


def art_sky(sd, w, h):
    """灰度天空：渐变 + 低平云带 + 落日，交给 ColorFiltered 做暖色叠印。"""
    sd.pos(0, 0, w, h, sd.box(w, h, grad=(
        'gradientType="LINEAR" gradientColors="#1C1C1C,#565656,#B4B4B4" '
        'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"')))
    sx, sy = w * SUNFX, h * SUNFY
    # 落日：大范围柔光 + 日面 + 更亮的实心核心
    K.glow(sd, sx, sy, 176, "#FFFFFF", rings=11, a0=0.05)
    K.radial_disc(sd, sx - 58, sy - 58, 116,
                  ["#FFF6E4", "#FFFFFF", "#FFFFFF"], radius="0.5")
    sd.rect(sx - 36, sy - 36, 72, 72, "#FFFFFF", radius=36)
    # 低平云带：只出现在报头之下、地平线之上（方角、无描边，避免看起来像标尺）
    for fx, fy, fw, th, a in [(0.04, 0.555, 0.52, 13, 0.20),
                              (0.36, 0.615, 0.58, 10, 0.16),
                              (0.12, 0.685, 0.44, 9, 0.22),
                              (0.52, 0.745, 0.46, 12, 0.17),
                              (0.02, 0.805, 0.36, 8, 0.14),
                              (0.24, 0.500, 0.22, 6, 0.13)]:
        sd.rect(w * fx, h * fy, w * fw, th, K.hexa("#FFFFFF", a))
        sd.rect(w * fx + 30, h * fy + th, w * fw * 0.60, 2,
                K.hexa("#000000", 0.10))
    # 地平线雾带
    sd.rect(0, h * 0.885, w, h * 0.115, K.hexa("#FFFFFF", 0.16))
    # 远处岸线：低矮暗带、灯塔与两根电线杆
    sd.rect(0, h * 0.962, w * 0.40, 6, "#404040")
    sd.rect(w * 0.30, h * 0.938, 9, h * 0.024, "#3C3C3C")
    for fx in (0.08, 0.17):
        sd.rect(w * fx, h * 0.944, 3, h * 0.018, "#383838")
    # 三只海鸥：两条短斜线组成 v 形
    for gx, gy, gs in [(0.205, 0.575, 1.0), (0.255, 0.645, 0.72),
                       (0.165, 0.700, 0.55)]:
        x, y = w * gx, h * gy
        sd.line(x, y, x + 13 * gs, y - 7 * gs, 3 * gs, "#2A2A2A")
        sd.line(x + 13 * gs, y - 7 * gs, x + 26 * gs, y, 3 * gs, "#2A2A2A")


def art_sea(sd, w, h):
    """灰度海面：从 y=0 起就是水，避免与天空层之间留缝。"""
    sd.pos(0, 0, w, h, sd.box(w, h, grad=(
        'gradientType="LINEAR" gradientColors="#5A5A5A,#424242,#2E2E2E" '
        'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"')))
    sd.line(0, 1, w, 1, 2, "#D0D0D0")
    sx = w * SUNFX
    for i in range(34):
        y = 10 + i * (h - 16) / 34.0
        wd = w * (0.07 + 0.46 * ((i * 37) % 23) / 23.0)
        xx = w * ((i * 61) % 41) / 41.0
        sd.rect(min(xx, w - wd), y, wd, 3 + (i % 3),
                K.hexa("#E8E8E8", 0.07 + 0.40 * (i % 5) / 5.0), radius=2)
    # 落日反光柱：逐段加宽、错开，模拟碎浪
    for i in range(24):
        y = 5 + i * (h * 0.66) / 24.0
        wd = 26 + i * 8.5
        off = (-1) ** i * (2 + (i % 4) * 3.5)
        sd.rect(sx - wd / 2 + off, y, wd, 5,
                K.hexa("#FFFFFF", 0.34 - i * 0.0125), radius=2)
    # 左侧栈桥：堤身 + 高低不齐的木桩 + 端头航标灯
    jd = w * 0.27
    for i, ph in enumerate((46, 58, 38, 52, 42, 62, 36)):
        x = 22 + i * (jd - 44) / 6.0
        sd.rect(x, h * 0.155 - ph, 8, ph + 26, "#262626")
    sd.rect(0, h * 0.155, jd, 16, "#202020")
    sd.rect(jd - 26, h * 0.155 - 74, 7, 74, "#1E1E1E")
    K.glow(sd, jd - 22.5, h * 0.155 - 78, 26, "#FFFFFF", rings=5, a0=0.10)
    sd.rect(jd - 28, h * 0.155 - 84, 12, 12, "#FFFFFF", radius=6)
    # 三条渔船：船体 + 驾驶舱 + 桅杆 + 索具 + 水线倒影
    for bx, by, sc in [(w * 0.355, h * 0.315, 1.0),
                       (w * 0.545, h * 0.115, 0.52),
                       (w * 0.135, h * 0.545, 0.78)]:
        sd.rect(bx, by, 148 * sc, 24 * sc, "#141414", radius=9 * sc)
        sd.rect(bx + 14 * sc, by + 18 * sc, 120 * sc, 8 * sc, "#0E0E0E",
                radius=4 * sc)
        sd.rect(bx + 86 * sc, by - 26 * sc, 40 * sc, 28 * sc, "#181818",
                radius=4 * sc)
        sd.line(bx + 44 * sc, by, bx + 40 * sc, by - 112 * sc, 5 * sc, "#141414")
        sd.line(bx + 40 * sc, by - 112 * sc, bx + 96 * sc, by - 26 * sc,
                3 * sc, "#1E1E1E")
        sd.line(bx + 40 * sc, by - 104 * sc, bx + 8 * sc, by, 3 * sc, "#1E1E1E")
        sd.rect(bx + 36 * sc, by - 116 * sc, 22 * sc, 5 * sc, "#141414")
        sd.rect(bx + 20 * sc, by + 30 * sc, 108 * sc, 6 * sc,
                K.hexa("#FFFFFF", 0.14), radius=3)


def art_thumb(sd, w, h):
    """封二影像组照预览：同一套灰度语言，缩成一张小照片。"""
    sd.rect(0, 0, w, h * 0.58, "#7E7E7E")
    sd.rect(0, h * 0.58, w, h * 0.42, "#454545")
    sd.line(0, h * 0.58, w, h * 0.58, 2, "#CFCFCF")
    sd.rect(w * 0.62 - 12, h * 0.36 - 12, 24, 24, "#FFFFFF", radius=12)
    K.glow(sd, w * 0.62, h * 0.36, 40, "#FFFFFF", rings=5, a0=0.05)
    for i in range(9):
        y = h * 0.62 + i * (h * 0.36) / 9.0
        wd = w * (0.16 + 0.30 * ((i * 7) % 5) / 4.0)
        sd.rect(w * 0.62 - wd / 2 + (i % 3) * 6, y, wd, 3,
                K.hexa("#FFFFFF", 0.26 - i * 0.02), radius=2)
    sd.rect(0, h * 0.50, w * 0.30, 9, "#242424")
    for i in range(4):
        x = 12 + i * 26
        sd.rect(x, h * 0.50 - 22 - (i % 2) * 9, 5, 31, "#2A2A2A")
    sd.rect(w * 0.44, h * 0.66, 46, 9, "#161616", radius=4)
    sd.line(w * 0.50, h * 0.66, w * 0.49, h * 0.44, 3, "#161616")


HZ = 506
layer(0, 0, W, HZ + 16, art_sky, filt=("#C9863C", "MULTIPLY"))
layer(0, HZ, W, ART_H - HZ, art_sea, filt=("#1E466E", "MULTIPLY"))
# 压暗下部，保证封面文字可读（从封面主文案上方一点开始）
d.pos(0, HZ + 150, W, ART_H - HZ - 150, d.box(W, ART_H - HZ - 150, grad=(
    'gradientType="LINEAR" gradientColors="#08131F00,#08131F96,#08131FF0" '
    'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"')))
# 内页预览：ClipRRect 圆角裁切 + 同一条 ColorFiltered 双色链
layer(W - 76 - 240, HZ + 40, 240, 160, art_thumb, filt=("#2A5C8A", "MULTIPLY"),
      clip=12)
d.pos(W - 76 - 240, HZ + 40, 240, 160,
      d.box(240, 160, radius=12, border="1 SOLID #EADFCB"))
L(W - 76 - 240, HZ + 208, 240, 22, "封二 · 影像组照  P%d" % TOC[6][0], 14,
  "#D8C9AE", align="END", valign="TOP")

# ==================== 报头 ====================
L(76, 52, 400, 30, "%s 月刊 · %d 年 %d 月号" % (MAG, ISSUE_YEAR, ISSUE_MONTH),
  19, "#EADFCB", valign="TOP")
# 刊名用实心白 + 字距，104px 描边会让汉字笔画糊成一团（v02 视觉自检）
L(72, 82, 520, 118, MAG, 104, "#FFFFFF", "BOLD", valign="TOP", spacing=18)
d.rect(76, 206, 300, 3, K.hexa(ACC, 0.95))
L(76, 218, 520, 34, LATIN, 26, "#F0E4CE", "BOLD", valign="TOP", spacing=22)
rx = W - 76
for i, (s, sz, col) in enumerate([
        ("%d 期 · 总第 %d 期" % (ISSUE_MONTH, NO), 21, "#F0E4CE"),
        ("定价 ¥ %.2f · %s" % (PRICE, POST), 18, "#D8C9AE"),
        ("ISSN %s · %s" % (ISSN, CN), 18, "#D8C9AE")]):
    L(rx - 460, 60 + i * 34, 460, 30, s, sz, col, align="END", valign="TOP")

# ==================== 封面主文案 ====================
wy = ART_H - 372
kicker = "封面报道 · %s 字 · 通读约 %d 分钟" % (
    format(FEAT[4], ","), round(FEAT_MIN))
kw = 30 + tf.w(kicker, 19) + 30
d.pos(76, wy, kw, 38, d.box(kw, 38, color=K.hexa(ACC, 0.94), radius=19,
                            align="CENTER",
                            inner=K.T(kicker, d.font, color="#FFFFFF",
                                      fontSize=19, fontStyle="BOLD")))
tf.check(tag, kicker, 19, kw - 26, 38)
L(76, wy + 62, 1090, 96, "潮汐退去之后", 88, "#FFFFFF", "BOLD", valign="TOP")
L(76, wy + 168, 1090, 52, "一座渔港的十年账本", 42, "#F3D9A8", "BOLD",
  valign="TOP")
lead = ("我们带着三本台账回到 %s。十年里，这片海少了 %s 公顷滩涂、%d 个渔村，"
        "多出了 %s 万元的养殖补偿。数字都对得上，只有潮水不认账。") % (
    "青螺港", "1,840", 11, "4,700")
tf.check(tag, lead, 23, 1010, 78, lines=3)
d.pos(76, wy + 236, 1010, 78, d.box(1010, 78, align="TOP_LEFT",
                                    inner=K.T(lead, d.font, color="#DCE6F0",
                                              fontSize=23, height=1.55,
                                              maxLines=3)))
L(76, wy + 322, 1010, 26, "文 / 沈知远    图 / 何见山    编辑 / 江晚",
  19, "#9FB4C9", valign="TOP")

# ==================== 纸面区：本期要目 ====================
Y = ART_H + 36
d.rect(76, Y, W - 152, 2, INK)
L(76, Y + 16, 300, 30, "本期要目", 24, INK, "BOLD", valign="TOP")
L(W - 76 - 520, Y + 20, 520, 26,
  "%d 篇 · %s 字 · 通读约 %d 分钟" % (N_ART, format(TOTAL_WORDS, ","),
                                     round(READ_MIN)), 19, P["t1"], align="END",
  valign="TOP")
ry = Y + 58
for pg, col, title, author, words in TOC[:5]:
    mins = words / float(CPM)
    L(76, ry, 62, 26, "%03d" % pg, 20, ACC, "BOLD", valign="TOP")
    L(146, ry, 660, 26, title, 21, INK, valign="TOP")
    L(826, ry, 130, 26, col, 17, P["t2"], valign="TOP")
    L(966, ry, 198, 26, "%s 字 · %d 分钟" % (format(words, ","), round(mins)),
      17, P["t1"], align="END", valign="TOP")
    d.line(76, ry + 33, W - 76, ry + 33, 1, P["border"])
    ry += 42
L(76, ry + 1, W - 152, 22,
  "另含 %d 篇：%s" % (N_ART - 5,
   " / ".join(t[1] for t in TOC[5:])),
  16, P["t2"], valign="TOP")

# 篇幅分布：12 篇字数按目录顺序成柱，最长篇高亮（全部由 TOC 反算）
by = ry + 28
BH = 122
d.rect(76, by, W - 152, BH, "#E7E1D5", radius=10)
L(96, by + 8, 320, 20, "篇幅分布（%d 篇 · 按目录顺序）" % N_ART, 16, P["t2"],
  valign="TOP")
L(W - 96 - 560, by + 8, 560, 20,
  "最长 %s 字 · 中位 %s 字 · 最短 %s 字" % (format(LONGEST[4], ","),
                                          format(int(MEDIAN), ","),
                                          format(SHORTEST[4], ",")),
  16, P["t1"], align="END", valign="TOP")
base = by + BH - 20
maxh = base - (by + 34)
slot = (W - 152 - 40) / float(N_ART)
for i, t in enumerate(TOC):
    bh = max(3.0, maxh * t[4] / float(LONGEST[4]))
    x = 96 + i * slot
    d.rect(x, base - bh, slot - 9, bh,
           ACC if t is LONGEST else "#B7AB93", radius=2)
d.line(96, base + 0.5, W - 96, base + 0.5, 1, "#A79B82")
L(96, base + 4, 200, 18, "P%03d" % TOC[0][0], 14, P["t2"], valign="TOP")
L(W - 296, base + 4, 200, 18, "P%03d" % TOC[-1][0], 14, P["t2"], align="END",
  valign="TOP")

# ==================== 条码与页脚 ====================
FY = H - 150
d.rect(76, FY - 26, W - 152, 2, INK)
bw, gap = 2.6, 0.0
bx = W - 76 - int(len(BAR_BITS) * (bw + 0.9))
run = 0
i = 0
while i < len(BAR_BITS):
    c = BAR_BITS[i]
    j = i
    while j < len(BAR_BITS) and BAR_BITS[j] == c:
        j += 1
    if c == "1":
        d.rect(bx + run, FY, bw * (j - i), 74, INK)
    run += bw * (j - i) + 0.9
    i = j
L(bx, FY + 80, run, 24, BAR_TEXT, 19, INK, align="CENTER", valign="TOP")
L(76, FY - 2, 520, 26, "%s｜%s｜%s" % (MAG, ISSN, POST), 17, P["t1"],
  valign="TOP")
L(76, FY + 28, 560, 26, "出版：暗礁杂志社 · 定价 ¥ %.2f · 总编辑：林白" % PRICE,
  17, P["t1"], valign="TOP")
L(76, FY + 56, 620, 26, "条码为演示号码，按 EAN-13 标准表编码（校验位 %s）"
  % BAR_CHK, 15, P["t2"], valign="TOP")
L(76, FY + 84, 620, 26, "本刊全部内容为虚构演示数据，不指向任何真实刊物或人物",
  15, P["t2"], valign="TOP")

# 右侧竖排期号（放在压暗后的海面区，避开报头与云带）
K.place(d, W - 58, ART_H - 330, 26, 260,
        K.T("2 0 2 6 · 1 1", d.font, color="#8FA6BD", fontSize=20,
            fontStyle="BOLD", letterSpacing=2), align="TOP_CENTER")

dsl = d.dsl()
(OUT / "case07.snapshot").write_text(dsl, encoding="utf-8")
print("canvas %dx%d bytes %d textfit %d %s" % (W, H, len(dsl), tf.n, tf.problems[:5]))
print("arts %d words %s avg %.0f read %.1f min  longest %s" % (
    N_ART, format(TOTAL_WORDS, ","), AVG_WORDS, READ_MIN, LONGEST[2][:12]))
print("feat %s min %.1f  barcode %s chk %s bits %d" % (
    format(FEAT[4], ","), FEAT_MIN, BAR_TEXT, BAR_CHK, len(BAR_BITS)))
