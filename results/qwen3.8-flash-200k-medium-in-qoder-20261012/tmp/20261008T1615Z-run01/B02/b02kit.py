"""B02 扳手屋 · 设计系统构件（在 _suite/scripts/dslkit.py 与 B01 通用构件之上）。

用法（各 case 生成脚本）：

    import os, sys
    from pathlib import Path
    root = Path(os.environ["SNAPSHOT_TASK_ROOT"]); rid = os.environ["SNAPSHOT_RUN_ID"]
    sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
    sys.path.insert(0, str(root / "tmp" / rid / "B01"))
    sys.path.insert(0, str(root / "tmp" / rid / "B02"))
    from dslkit import Doc, TextFit, n, minutes
    import b02kit as B

品牌层只实现 B01 探针（probe/caps*.png）真实验证过的构造：Container/Positioned/Text、
Transform 旋转、RADIAL/LINEAR/SWEEP 渐变、boxShadow、border、borderRadius、tnum。
面积/渐变填充一律用 mix() 预合成实色，避免 8 位 alpha 相邻矩形叠出竖纹（B01 踩坑）。
"""
import json
import math
import os
import random as _random
from pathlib import Path

from dslkit import Doc, TextFit, n  # noqa: F401
import b01kit as K  # 通用几何/文本构件（B01 探针验证过的构造）

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
DATA = json.loads((root / "tmp" / rid / "B02" / "data.json").read_text(encoding="utf-8"))

# ---------------- 品牌令牌 ----------------
P = {
    "paper": "#F2EBDD",     # 牛皮纸底
    "paper2": "#E9E0CE",    # 纸底第二档
    "ink": "#1B1E22",       # 主文字 / 主结构
    "ink2": "#4A5158",      # 次级文字
    "ink3": "#7C848C",      # 三级文字
    "orange": "#C8552B",    # 扳手屋主色
    "steel": "#2E5468",     # 钢青
    "brass": "#E0A526",     # 计量黄
    "green": "#3F7A55",     # 状态：可借
    "red": "#A6382F",       # 状态：逾期/禁止
    "greyblue": "#6E7F8D",  # 状态：维修中
    "dark": "#16181B",      # 深色版面底（触摸屏/门头夜间）
    "dark2": "#22262B",
    "white": "#FFFDF8",
}
TSCALE = (12, 14, 17, 22, 30, 44, 72, 120)
STATE_COLOR = {"在馆": P["green"], "在借": P["steel"], "维修中": P["greyblue"],
               "报废待处理": P["red"]}
FONT = "Inter,Noto Sans CJK SC"

mix = K.hexa  # 8 位 alpha 仍可用，但大面积填充用 blend()


def blend(hex6, a, over):
    """把 hex6 以 alpha a 预合成到实色 over 上，返回实色。"""
    o = [int(hex6[i:i + 2], 16) for i in (1, 3, 5)]
    u = [int(over[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(int(round(o[i] * a + u[i] * (1 - a)))
                                   for i in range(3))


def lighten(hex6, a):
    return blend("#FFFFFF", a, hex6)


def darken(hex6, a):
    return blend(P["ink"], a, hex6)


def on_bg(hex6, dark):
    """同一令牌在深/浅底上都要可读：深底提亮，浅底压暗（烟雾测试踩坑）。"""
    return lighten(hex6, 0.34) if dark else darken(hex6, 0.16)


def doc_palette(dark=False):
    """把 dslkit 的默认（暗色）调色板整体换成扳手屋令牌，避免误用默认值。"""
    bg = P["dark"] if dark else P["paper"]
    return {
        "card": blend("#FFFFFF", 0.055, bg) if dark else P["white"],
        "card2": blend("#FFFFFF", 0.03, bg) if dark else P["paper2"],
        "border": blend("#FFFFFF", 0.16, bg) if dark else blend(P["ink"], 0.16, bg),
        "line": blend("#FFFFFF", 0.14, bg) if dark else blend(P["ink"], 0.12, bg),
        "grid": blend("#FFFFFF", 0.10, bg) if dark else blend(P["ink"], 0.10, bg),
        "axis": blend("#FFFFFF", 0.34, bg) if dark else blend(P["ink"], 0.34, bg),
        "row": blend("#FFFFFF", 0.035, bg) if dark else blend(P["ink"], 0.04, bg),
        "t0": blend("#FFFFFF", 0.94, bg) if dark else P["ink"],
        "t1": blend("#FFFFFF", 0.74, bg) if dark else P["ink2"],
        "t2": blend("#FFFFFF", 0.52, bg) if dark else P["ink3"],
        "bg": bg, "paper": bg,
        "orange": P["orange"], "brass": P["brass"], "steel": P["steel"],
        "green": P["green"], "red": P["red"], "greyblue": P["greyblue"],
        "amber": P["brass"], "cyan": P["steel"], "slate": P["greyblue"],
        "ink": P["ink"],
    }


def paper_doc(w, h, dark=False, noise=18, seed=7):
    """牛皮纸底（深色版面用于触摸屏/夜间门头）。

    噪点用确定性伪随机散布的小方格、预合成实色，不叠 alpha；第一版是固定取模的
    网格，放大后看起来像纱窗而不是纸（烟雾测试踩坑）。
    """
    bg = P["dark"] if dark else P["paper"]
    d = Doc(w, h, bg=bg, font=FONT, palette=doc_palette(dark))
    d.P["line"] = blend(P["ink"], 0.14, bg) if dark else blend(P["ink"], 0.12, bg)
    # 深色底上的纸纤维点必须更淡更小：0.045/1.4 倍在 1020x646 卡面上像斑驳墙皮
    tone = blend("#FFFFFF", 0.026, bg) if dark else blend(P["ink"], 0.030, bg)
    scales = (0.5, 0.8, 1.1) if dark else (0.6, 1.0, 1.4)
    if noise:
        rng = _random.Random(seed)
        n_ = min(400, int(w * h / (noise * noise * 2.2)))
        for _ in range(n_):
            s = noise * rng.choice(scales)
            d.rect(rng.randrange(0, max(1, w - int(s))),
                   rng.randrange(0, max(1, h - int(s))), int(s), int(s), tone)
    return d


def rotated_centered(d, cx, cy, w, h, deg, inner):
    """绕自身中心旋转：K.rotated 的 alignment 是 TOP_LEFT，直接把 x,y 当中心会让
    斜杆整体偏到螺母上方，读成一根独立的棍（烟雾测试踩坑）。"""
    co, si = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    K.rotated(d, cx - co * w / 2 + si * h / 2, cy - si * w / 2 - co * h / 2,
              w, h, deg, inner)


def hexagon(d, cx, cy, R, color, steps=None, rot=0.0, smooth=True):
    """尖顶正六边形：中间矩形 + 上下各 steps 条线性收缩的扫描条（无 path 图元）。

    steps 随半径增大，否则大标志上斜边呈明显锯齿（烟雾测试踩坑）；smooth 再沿 6 条
    理想边压一道同色粗线，盖住扫描条留下的台阶（case-01 的 235px 标志踩坑）。
    """
    hw = math.sqrt(3) * R / 2.0
    if steps is None:
        steps = max(9, min(72, int(R / 1.5)))

    def place(x, y, w, h, c):
        if rot:
            co, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            d.pos(cx - hw - 2, cy - R - 2, 2 * hw + 4, 2 * R + 4,
                  '<Transform matrix="(%0.4f,%0.4f,0,0,%0.4f,%0.4f,0,0,0,0,1,0,'
                  '0,0,0,1)" alignment="TOP_LEFT">'
                  % (co, si, -si, co)
                  + '<Container width="%s" height="%s"><Positioned left="%s" top="%s" '
                    'width="%s" height="%s"><Container width="%s" height="%s" '
                    'color="%s"/></Positioned></Container></Transform>'
                  % (2 * hw + 4, 2 * R + 4, x - (cx - hw - 2), y - (cy - R - 2),
                     w, h, w, h, c))
        else:
            d.rect(x, y, w, h, c)
    y0, y1 = int(round(cy - R / 2)), int(round(cy + R / 2))
    place(cx - hw, y0, 2 * hw, y1 - y0, color)
    # 扫描条按整数行铺满、宽度取该行的外沿值：分数高度的相邻条会被抗锯齿画出横纹
    for k in range(steps):
        w = 2 * hw * (1 - k / steps)
        ya = int(round(cy - R / 2 - (R / 2) * (k + 1) / steps))
        yb = int(round(cy - R / 2 - (R / 2) * k / steps))
        if yb > ya:
            place(cx - w / 2, ya, w, yb - ya, color)
        yc = int(round(cy + R / 2 + (R / 2) * k / steps))
        yd = int(round(cy + R / 2 + (R / 2) * (k + 1) / steps))
        if yd > yc:
            place(cx - w / 2, yc, w, yd - yc, color)
    if smooth and not rot:
        lt = max(1.6, 2.6 * hw / steps)
        v = hex_verts(cx, cy, R)
        for i in range(6):
            d.line(v[i][0], v[i][1], v[(i + 1) % 6][0], v[(i + 1) % 6][1], lt, color)


def hex_verts(cx, cy, R, rot=0.0):
    """尖顶正六边形顶点（屏幕坐标，y 向下）。"""
    return [(cx + R * math.cos(math.radians(a - rot)),
             cy - R * math.sin(math.radians(a - rot)))
            for a in (90, 30, -30, -90, -150, 150)]


def hex_outline(d, cx, cy, R, color, t=None):
    """六边形轮廓：6 条旋转粗线段（斜边是真正的直线，用于大尺寸标志）。"""
    t = t or R * 0.15
    v = hex_verts(cx, cy, R)
    for i in range(6):
        d.line(v[i][0], v[i][1], v[(i + 1) % 6][0], v[(i + 1) % 6][1], t, color,
               radius=t / 2)


def hex_chip(d, cx, cy, R, color, label="", size=None, ink=None, ring=False,
             bg=None, dark=False):
    """品牌母题：六角芯片。ring=True 时只留轮廓（低密度或次级状态）。"""
    if ring and dark:
        color = lighten(color, 0.22)
    if ring:
        hexagon(d, cx, cy, R, color)
        hexagon(d, cx, cy, R * 0.68, bg or d.P["bg"])
    else:
        hexagon(d, cx, cy, R, color)
    if label:
        # 环体只留 0.68R 的内孔，两字标签必须再降一档，否则字压到六角边框上
        f = 0.42 if (ring and len(label) >= 2) else (0.60 if len(label) >= 2 else 0.80)
        size = size or int(R * f)
        d.label(cx - R, cy - R * 0.62, 2 * R, R * 1.24, label,
                ink or (P["paper"] if not ring else on_bg(color, dark)),
                size, "BOLD", "CENTER", features="tnum")


def pill(d, x, y, w, h, text, color, size=14, dark=False, bold=True):
    """标签胶囊：六角多字放不下，用圆角条 + 左端一枚小六角保持母题一致。"""
    base = color if not dark else lighten(color, 0.24)
    fill = blend(base, 0.16, P["dark"]) if dark else blend(base, 0.13, P["white"])
    d.rect(x, y, w, h, fill, radius=h / 2)
    r = h * 0.30
    hex_chip(d, x + h * 0.52, y + h / 2, r, base, "", dark=dark)
    ink = blend(base, 0.30, P["white"]) if dark else darken(base, 0.55)
    d.label(x + h * 0.92, y, w - h * 1.1, h, text, ink, size,
            "BOLD" if bold else None, "START", features="tnum")
    return x + w


def barcode(d, x, y, w, h, s, color):
    """确定性条码：由会员号逐字符派生条宽，同一号码每次渲染结果一致。"""
    seq = []
    for ch in s:
        o = ord(ch)
        seq += [1 + o % 3, 1 + (o // 3) % 3, 1 + o % 2, 2]
    unit = w / float(sum(seq))
    cx = x
    for i, t in enumerate(seq):
        if i % 2 == 0:
            d.rect(cx, y, max(1.0, t * unit), h, color)
        cx += t * unit
    return cx


def qr_placeholder(d, x, y, size, seed_text, fg=None, bg=None, n=21):
    """虚构二维码占位：由字符串确定性生成的模块图，三个定位角。

    它不是可扫的二维码（没有编码规则），所以画面文字必须写明「占位/不指向真实地址」。
    """
    fg = fg or P["ink"]
    bg = bg or P["white"]
    d.rect(x, y, size, size, bg)
    u = size / float(n)
    h = 2166136261
    for ch in seed_text:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF

    def bit(i):
        v = (h ^ (i * 2654435761)) & 0xFFFFFFFF
        v = (v * 2246822519) & 0xFFFFFFFF
        return ((v >> 15) & 1) == 1

    def finder(r, c):
        return (r < 7 and c < 7) or (r < 7 and c >= n - 7) or (r >= n - 7 and c < 7)

    for r in range(n):
        for c in range(n):
            if finder(r, c) or not bit(r * n + c):
                continue
            d.rect(x + c * u, y + r * u, u + 0.4, u + 0.4, fg)
    for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):
        d.rect(x + fx * u, y + fy * u, 7 * u, 7 * u, fg)
        d.rect(x + (fx + 1) * u, y + (fy + 1) * u, 5 * u, 5 * u, bg)
        d.rect(x + (fx + 2) * u, y + (fy + 2) * u, 3 * u, 3 * u, fg)
    return x + size


def dash_line(d, x, y, w, color, seg=6, gap=6, h=2):
    cx = x
    while cx < x + w:
        d.rect(cx, y, min(seg, x + w - cx), h, color)
        cx += seg + gap
    return cx


def gradient_bands(d, w, h, c0, c1, band=20):
    """整幅竖向色带渐变：预合成实色、整数行铺满并向下压边 1px 防细缝。

    满幅手机底用 paper_doc 的方块噪点会读成压缩残骸而不是壁纸（case-05 v01 踩坑），
    这类版面改用渐变。
    """
    y = 0
    while y < h:
        b = min(band, h - y)
        d.rect(0, y, w, b + (1 if y + b < h else 0), K.lerp_colors([c0, c1], y / float(h)))
        y += b


def brand_mark(d, cx, cy, R, color=None, ink=None, bg=None, hole=0.42, deg=-34):
    """标志：六角螺母 + 斜穿中心的扳手柄（柄端带环头）。

    第一版在螺母上方加了两条「屋顶」斜板，R=22 时读成一堆碎条（烟雾测试踩坑），
    所以只保留两级结构：小尺寸下依然可辨。
    """
    color = color or P["orange"]
    ink = ink or P["ink"]
    bg = bg or d.P["bg"]
    hexagon(d, cx, cy, R, color)
    hexagon(d, cx, cy, R * hole, bg)
    if R >= 34:
        hex_outline(d, cx, cy, R * 0.74, bg, t=R * 0.05)
    t = max(5.0, R * 0.26)
    L = R * 2.15
    rotated_centered(d, cx, cy, L, t, deg,
                     d.box(L, t, radius=t / 2, color=ink))
    co, si = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    # 环头压在六角右上边上（第一版放在 1.27R 处，脱离螺母读成一把钥匙）
    ex, ey = cx + co * R * 0.99, cy + si * R * 0.99
    d.dot(ex, ey, R * 0.74, ink)
    if R >= 20:
        d.dot(ex, ey, R * 0.34, bg)


def ruler(d, x, y, w, frac, tone=None, h=14, ticks="full", label=None,
         lw=74, ls=17, track=None, dark=False):
    """刻度尺条（本项目所有比例数据的统一画法）。
    ticks: full=每 10% 一道刻线 + 半刻; compact=只留 50% 一道; micro=无刻线。"""
    tone = tone or P["orange"]
    bg = P["dark"] if dark else P["paper"]
    track = track or (blend(P["white"], 0.13, bg) if dark else blend(P["ink"], 0.12, bg))
    on_fill = blend(P["white"], 0.62, tone) if dark else blend(P["ink"], 0.42, tone)
    on_track = blend(P["white"], 0.20, bg) if dark else blend(P["ink"], 0.26, bg)
    d.rect(x, y, w, h, track, radius=h / 2)
    fw = max(h, w * frac)
    d.rect(x, y, fw, h, tone, radius=h / 2)
    if ticks == "full":
        for i in range(1, 10):
            th = h if i % 5 == 0 else h * 0.55
            d.rect(x + w * i / 10.0 - 0.7, y + (h - th) / 2, 1.4, th,
                   on_fill if w * i / 10 < fw else on_track)
    elif ticks == "compact":
        d.rect(x + w / 2 - 0.7, y + h * 0.22, 1.4, h * 0.56,
               on_fill if w / 2 < fw else on_track)
    if label is not None:
        ink = blend("#FFFFFF", 0.86, bg) if dark else P["ink"]
        d.label(x + w + 10, y - (ls - h) / 2, lw, ls * 1.2, label, ink, ls, "BOLD",
                "START", features="tnum")
    return x + w + 10 + lw


def card(d, x, y, w, h, title=None, sub=None, tone=None, radius=10, dark=False,
         border=True, pad=20):
    bg = blend("#FFFFFF", 0.055, P["dark"]) if dark else P["white"]
    d.pos(x, y, w, h, d.box(w, h, radius=radius, color=bg,
                            border="1 SOLID %s" % (blend(P["ink"], 0.16, bg)
                                                   if border else bg)))
    if title:
        d.label(x + pad, y + 14, w - 2 * pad, 30, title,
                tone or P["orange"], 20, "BOLD", "START", valign="TOP")
        if sub:
            d.label(x + pad, y + 40, w - 2 * pad, 24, sub,
                    blend("#FFFFFF", 0.7, P["dark"]) if dark else P["ink2"],
                    14, None, "START", valign="TOP")
    return d


def section_head(d, x, y, w, idx, title, sub=None, dark=False, size=22):
    """编号 + 六角 + 标题 + 细分隔线：所有信息密集触点共用的小标题。"""
    bg = P["dark"] if dark else P["paper"]
    hex_chip(d, x + 14, y + size * 0.62, 14, P["orange"], "%02d" % idx, size=11)
    d.label(x + 36, y, w - 36 - 120, size * 1.3, title,
            blend("#FFFFFF", 0.92, bg) if dark else P["ink"], size, "BOLD", "START")
    if sub:
        d.label(x + w - 118, y + size * 0.18, 118, size * 1.2, sub,
                blend("#FFFFFF", 0.55, bg) if dark else P["ink3"],
                12, None, "END", features="tnum")
    d.rect(x, y + size * 1.34, w, 1, blend(P["ink"], 0.18, bg))


def footer(d, x, y, w, variant="full", dark=False, note=None, align="START"):
    """识别锚点：三种压缩档，同一行内容在不同密度下退化。"""
    bg = P["dark"] if dark else P["paper"]
    ink = blend("#FFFFFF", 0.72, bg) if dark else P["ink2"]
    br = DATA["brand"]; ru = br["rules"]
    site = br["sites"][0].split("（")[0]
    fee = "个人年卡 ¥%d / 家庭年卡 ¥%d" % (ru["member_fee"]["个人年卡"],
                                            ru["member_fee"]["家庭年卡"])
    txt = {
        "full": "%s · %s · %s · 无押金 · 借出不再收费 · %s" % (
            br["name"], site, fee, ru["repair_by"]),
        "short": "%s · %s · 个人年卡 ¥%d · 无押金" % (br["name"], site,
                                                     ru["member_fee"]["个人年卡"]),
        "micro": "%s · %s" % (br["name"], site),
        "receipt": "%s · 逾期 ¥%g/件·天 · 电话 %s" % (
            ru["return_point"], ru["late_fee_per_day"], br["phone"]),
    }[variant]
    if note:
        txt = txt + " · " + note
    d.label(x, y, w, 22, txt, ink, 12 if variant != "receipt" else 13, None,
            align, valign="TOP")
    if variant == "full":
        d.label(x, y + 20, w, 20, "虚构演示品牌 · 全部数据由同一张馆藏/借阅表生成",
                blend(P["ink"], 0.45, bg) if not dark else blend("#FFFFFF", 0.4, bg),
                11, None, align, valign="TOP")


def stamp(d, x, y, w, h, text, color=None, deg=-8, size=20, dark=False, tf=None):
    """印章：旋转的圆角双线框 + 粗体文字（逾期/已完成/待保养）。

    框与文字分成同一中心的三层旋转图元：把 Stack/Positioned 塞进带 border 的
    Container 里，文字在真实渲染中整块消失（构件烟雾 v1/v3 两次踩坑）。
    """
    color = color or P["red"]
    bg = P["dark"] if dark else P["paper"]
    if tf is not None:
        tf.check("stamp", text, size, w - 20, h - 12)
    color = on_bg(color, dark)
    cx, cy = x + w / 2, y + h / 2
    rotated_centered(d, cx, cy, w, h, deg,
                     d.box(w, h, radius=8, border="3 SOLID %s" % color))
    rotated_centered(d, cx, cy, w - 14, h - 14, deg,
                     d.box(w - 14, h - 14, radius=4,
                           border="1 SOLID %s" % blend(color, 0.55, bg)))
    rotated_centered(d, cx, cy, w - 14, h - 14, deg,
                     d.box(w - 14, h - 14, align="CENTER",
                           inner=K.T(text, d.font, color=color, fontSize=size,
                                     fontStyle="BOLD", textAlign="CENTER")))


CAT_COLOR = {
    "EMT": P["orange"], "PNU": P["steel"], "HND": P["green"], "WOD": P["brass"],
    "MTL": P["red"], "GDN": P["greyblue"], "MSR": P["ink"],
    "CLN": blend(P["orange"], 0.45, P["paper"]), "LIF": blend(P["green"], 0.45, P["paper"]),
}


def cat_color(code, dark=False):
    """类目色在全套十个触点里必须一致（分区导视、触摸屏、年报共用）。"""
    c = CAT_COLOR[code]
    return lighten(c, 0.30) if dark else c


def tlab(d, tf, tag, x, y, w, h, s, size, color=None, style=None, align="START",
         valign="TOP", lines=1, features=None):
    """先过 TextFit 再落字：Snapshot 裁字不给省略号，只能事前把关（B01 标准沿用）。"""
    if tf is not None:
        tf.check(tag, s, size, w, h, lines=lines)
    kw = {"features": features} if features else {}
    d.label(x, y, w, h, s, color or d.P["t0"], size, style, align, valign=valign, **kw)


def pct(v):
    return "%.1f%%" % (v * 100)


def money(v):
    return "¥{:,.0f}".format(v) if float(v) == int(v) else "¥%.2f" % v


def date_cn(iso_s):
    y, m, dd = iso_s.split("-")
    return "%s年%d月%d日" % (y, int(m), int(dd))


def date_md(iso_s):
    _, m, dd = iso_s.split("-")
    return "%d月%d日" % (int(m), int(dd))


def tools_of(state=None, cat=None, limit=None):
    t = [x for x in DATA["tools"]
         if (state is None or x["state"] == state) and (cat is None or x["cat"] == cat)]
    return t[:limit] if limit else t


def summary():
    return DATA["summary"]
