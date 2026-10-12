"""A21 · 叠光 Layerlight 双尺寸发布物（按轮次参数化生成器）。

第 1 轮：1080x1350 竖海报 + 1440x810 横屏，同一主色/同一字体层级/同一个
6 构件品牌图形，分别构图，顶底留真实可用扩展区但不写占位文字。

能力依据（本任务实测，见 preview/probe-alpha-v02.png 像素核对）：
- 8 位 hex（#RRGGBBAA）按 alpha 正确合成 -> 叠光的半透明板用它；
- Transform 16 值矩阵 + alignment="CENTER" 绕自身中心旋转；
- Text letterSpacing 生效；
- Container 的 opacity 属性与 <Opacity value=...> 都被忽略（不透明渲染），故不使用。
"""
import json
import math
import os
import sys
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "_suite" / "scripts"))
from dslkit import Doc, TextFit  # noqa: E402

TMP = root / "tmp" / rid / "A21"
LAY = TMP / "layouts"

# ---------------- design tokens（两图共用同一份） ----------------
TOK = {
    "color": {"bg": "#0B1020", "primary": "#3D6BFF", "violet": "#7C5CFF",
              "cyan": "#22D3EE", "ink": "#FFFFFF", "muted": "#9FB3FF",
              "hairline": "#243056"},
    "alpha": {"plate": "5C", "plateStrong": "8C", "glow": "2E"},
    "font": {"display": "Noto Sans CJK SC", "latin": "Inter,Noto Sans CJK SC"},
    "scale": {"display": 96, "h2": 44, "body": 30, "meta": 26, "kicker": 28,
              "wordmark": 56, "wordmarkLatin": 30},
    "space": {"gutter": 88, "gutterWide": 72, "rail": 1.5},
    "minTitlePx": 56, "minOtherPx": 24,
    "tagline": "Clarity through structure",
}
A = TOK["alpha"]
S = TOK["scale"]

# 第 3 轮改浅色主题。文字色全部压深到能在实际合成底上达到 4.5:1，
# 但叠光板/光线仍沿用品牌三色的 alpha，保证品牌图形形态与观感同源。
# 浅色底（#F5F7FC）本身亮度 0.93，第 1/2 轮那套 alpha 压在上面几乎看不出来；
# 第 3 轮把装饰 alpha 提高、把描边基色从亮板青换成深品牌青，并把细线压深，
# 同时保持文字仍落在净空区（不新增文字与叠层的重叠）。
DARK_RIBBON = {"plate_1": "1A", "plate_2": "1A", "plate_3": "14", "ray": "1F"}
LIGHT_RIBBON = {"plate_1": "3A", "plate_2": "3A", "plate_3": "33", "ray": "4D"}
DARK = dict(TOK["color"])
LIGHT = {"bg": "#F5F7FC", "primary": "#1E40AF", "violet": "#5B3FD1",
         "cyan": "#0E7490", "ink": "#0D1428", "muted": "#4A5878",
         "hairline": "#B9C6DE",
         "p_primary": "#3D6BFF", "p_violet": "#7C5CFF", "p_cyan": "#22D3EE",
         "ring_mix": 0.35, "ring_base": "cyan", "ribbon": LIGHT_RIBBON}
DARK.update({"p_primary": "#3D6BFF", "p_violet": "#7C5CFF", "p_cyan": "#22D3EE",
             "ring_mix": 0.65, "ring_base": "p_cyan", "ribbon": DARK_RIBBON})
PALETTES = {1: DARK, 2: DARK, 3: LIGHT}
C = DARK


def use_palette(rnd):
    global C
    C = PALETTES[rnd]

REQUIRED = {
    1: ["让复杂信息变得清晰", "2026.11.07 19:30", "ONLINE LAUNCH",
        "讲者：林川 / 苏言", "layerlight.example.org"],
    2: ["当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
        "2026.11.07 19:30", "ONLINE LAUNCH", "讲者：林川 / 苏言",
        "layerlight.example.org", "Northstar Research / 云构工具",
        "免费参加 · 无需报名"],
    3: ["当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
        "2026.11.07 19:30", "ONLINE LAUNCH", "讲者：林川 / 苏言",
        "layerlight.example.org", "Northstar Research / 云构工具",
        "免费参加 · 无需报名", "Clarity through structure"],
}
# 第 2 轮起：主标题变长，标题行按语义在冒号处分断，最多 3 行、字号 >=48
TITLE_R02 = ["当所有信息都想成为标题：", "让复杂信息变得清晰的", "结构化方法"]

TF = TextFit()
PLANE = {}      # 每个版本的元素登记，供 content-map.json 使用


def fl(d, tag, x, y, w, h, s, color, size, align="START", valign="MIDDLE",
       spacing=0.0, style=None):
    """带放得下断言的文字；spacing 计入宽度估算。

    字距版式的换行余量比无字距时更紧：v01 的 ONLINE LAUNCH 胶囊按 len-1 个
    间隔估算，实际渲染仍在盒内提前折行，所以这里按 len 个间隔再加 10% 余量。
    """
    est = TF.w(s, size) + spacing * len(s)
    if spacing:
        est *= 1.10
    assert est <= w * TF.SLACK, "%s 文字超宽 %.0f > %.0f: %r" % (tag, est, w * TF.SLACK, s)
    assert size * 1.32 <= h, "%s 盒高不足 %.0f < %.0f" % (tag, h, size * 1.32)
    assert size >= (TOK["minTitlePx"] if "display" in tag else TOK["minOtherPx"]), \
        "%s 字号 %s 低于下限" % (tag, size)
    PLANE[tag] = {"text": s, "box_px": [x, y, w, h], "font_px": size,
                  "font_family": TOK["font"]["latin"], "color": color,
                  "align": align, "letter_spacing_px": spacing,
                  "est_width_px": round(est, 1)}
    d.label(x, y, w, h, s, color=color, size=size, align=align, valign=valign,
            style=style, spacing=spacing or None)


def rgba(hexcol, ahex):
    return hexcol + ahex


def mix(fg, bg, t):
    """把 fg 以 t 的不透明度压到 bg 上，得到等效实色（描边属性未验证支持 8 位 hex）。"""
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join("%02X" % round(f[i] * t + b[i] * (1 - t)) for i in range(3))


def plate(d, tag, cx, cy, w, h, deg, color, radius=14):
    """绕自身中心旋转的半透明板（品牌构件 1–3）。"""
    r = math.radians(deg)
    co, si = math.cos(r), math.sin(r)
    m = f"({co:.6f},{si:.6f},0,0,{-si:.6f},{co:.6f},0,0,0,0,1,0,0,0,0,1)"
    inner = (f'<Transform matrix="{m}" alignment="CENTER">'
             + d.box(w, h, color=color, radius=radius) + "</Transform>")
    PLANE[tag] = {"shape": "rotated-plate", "center_px": [round(cx, 1), round(cy, 1)],
                  "size_px": [w, h], "rotation_deg": deg, "fill": color,
                  "border_radius_px": radius}
    d.pos(cx - w / 2.0, cy - h / 2.0, w, h, inner)


def ray(d, tag, x1, y1, x2, y2, color, th=3):
    PLANE[tag] = {"shape": "ray", "from_px": [x1, y1], "to_px": [x2, y2],
                  "color": color, "thickness_px": th}
    d.line(x1, y1, x2, y2, th, color)


def brand_mark(d, tag, cx, cy, s):
    """6 构件品牌图形：3 块叠光板 + 1 个光源 + 2 道射线。两图完全同构，只缩放。"""
    u = s / 100.0
    plate(d, tag + ".plate-1", cx - 9 * u, cy + 6 * u, 62 * u, 26 * u, -22,
          rgba(C["p_primary"], A["plate"]), radius=13 * u)
    plate(d, tag + ".plate-2", cx + 3 * u, cy - 4 * u, 62 * u, 26 * u, -22,
          rgba(C["p_violet"], A["plate"]), radius=13 * u)
    plate(d, tag + ".plate-3", cx + 12 * u, cy - 16 * u, 62 * u, 26 * u, -22,
          rgba(C["p_cyan"], A["plateStrong"]), radius=13 * u)
    ray(d, tag + ".ray-1", cx - 46 * u, cy + 30 * u, cx + 40 * u, cy - 34 * u,
        rgba(C["p_cyan"], A["glow"]), th=max(2, 3 * u))
    ray(d, tag + ".ray-2", cx - 30 * u, cy + 40 * u, cx + 52 * u, cy - 20 * u,
        rgba(C["p_primary"], A["glow"]), th=max(2, 3 * u))
    d.dot(cx + 30 * u, cy - 30 * u, 16 * u, C["ink"])
    PLANE[tag + ".source"] = {"shape": "dot", "center_px": [round(cx + 30 * u, 1),
                                                            round(cy - 30 * u, 1)],
                              "diameter_px": round(16 * u, 1), "color": C["ink"]}
    return {"components": [tag + ".plate-1", tag + ".plate-2", tag + ".plate-3",
                           tag + ".source", tag + ".ray-1", tag + ".ray-2"]}


def light_ribbon(d, tag, cx, cy, u):
    """背景叠光带：与品牌图形同一角度、同一相对位移，只是放大 4~6 倍。"""
    rb = C["ribbon"]
    plate(d, tag + ".plate-1", cx - 9 * u, cy + 6 * u, 62 * u, 26 * u, -22,
          rgba(C["p_primary"], rb["plate_1"]), radius=13 * u)
    plate(d, tag + ".plate-2", cx + 3 * u, cy - 4 * u, 62 * u, 26 * u, -22,
          rgba(C["p_violet"], rb["plate_2"]), radius=13 * u)
    plate(d, tag + ".plate-3", cx + 12 * u, cy - 16 * u, 62 * u, 26 * u, -22,
          rgba(C["p_cyan"], rb["plate_3"]), radius=13 * u)
    # 光线收在板组内部：v02 横版里它伸出板外，穿过右侧信息栏像一道划痕
    ray(d, tag + ".ray", cx - 26 * u, cy + 17 * u, cx + 28 * u, cy - 19 * u,
        rgba(C["p_cyan"], rb["ray"]), th=max(2, 1.6 * u))


def hairline(d, tag, x, y, w, color=None):
    PLANE[tag] = {"shape": "hairline", "box_px": [x, y, w, 1],
                  "color": color or C["hairline"]}
    d.rect(x, y, w, 1, color or C["hairline"])


def kicker(d, tag, x, y, s_size, spacing):
    """ONLINE LAUNCH 胶囊：描边环 + 字距文字，内部透明（A19 已验证无填充即真空）。"""
    est = (TF.w("ONLINE LAUNCH", s_size) + spacing * 13) * 1.10
    w = math.ceil(est / TF.SLACK) + 56
    h = 56
    d.pos(x, y, w, h, d.box(w, h, radius=h / 2,
                            border="1 SOLID " + mix(C[C["ring_base"]], C["bg"],
                                                    C["ring_mix"])))
    fl(d, tag, x + 28, y, w - 56, h, "ONLINE LAUNCH", C["cyan"], s_size,
       spacing=spacing)
    return [x, y, w, h]


# ---------------- 第 1 轮 竖版 1080x1350 ----------------
def build_portrait():
    W, H = 1080, 1350
    d = Doc(W, H, bg=C["bg"])
    # 顶部/底部真实可用扩展区：整条带内不含任何元素（design-tokens 里给出矩形）
    ext_top, ext_bottom = 104, 88
    # 背景叠光带：与品牌图形同角度同位移，只放大；不进入顶底扩展区
    light_ribbon(d, "bg", 950, 1140, 4.0)
    brand_mark(d, "mark", 88 + 66, ext_top + 66, 132)
    fl(d, "portrait.wordmark", 244, ext_top + 22, 320, 76, "叠光", C["ink"],
       S["wordmark"], style="BOLD")
    fl(d, "portrait.wordmark-latin", 244, ext_top + 104, 420, 40, "Layerlight",
       C["muted"], S["wordmarkLatin"], spacing=4)
    kicker(d, "portrait.kicker", 88, 336, S["kicker"], 6)
    fl(d, "portrait.display-1", 88, 452, 904, 128, "让复杂信息", C["ink"],
       S["display"], style="BOLD")
    fl(d, "portrait.display-2", 88, 588, 904, 128, "变得清晰", C["cyan"],
       S["display"], style="BOLD")
    hairline(d, "portrait.rule-1", 88, 760, 904)
    fl(d, "portrait.date-label", 88, 792, 300, 36, "发布时间", C["muted"], S["meta"])
    fl(d, "portrait.date", 88, 830, 700, 60, "2026.11.07 19:30", C["ink"], S["h2"],
       style="BOLD")
    fl(d, "portrait.speakers", 88, 908, 700, 44, "讲者：林川 / 苏言", C["muted"],
       S["body"])
    hairline(d, "portrait.rule-2", 88, 1170, 552)
    fl(d, "portrait.url-label", 88, 1190, 240, 40, "了解更多", C["muted"], S["meta"])
    fl(d, "portrait.url", 88, 1226, 700, 36, "layerlight.example.org", C["cyan"],
       S["meta"])
    return d.dsl(), W, H, {"ext_top": [0, 0, W, ext_top],
                           "ext_bottom": [0, H - ext_bottom, W, ext_bottom]}


# ---------------- 横版 1440x810 ----------------
def build_wide():
    W, H = 1440, 810
    d = Doc(W, H, bg=C["bg"])
    ext_top, ext_bottom = 72, 72
    light_ribbon(d, "bg", 1300, 628, 3.7)
    brand_mark(d, "mark", 72 + 54, ext_top + 54, 108)
    fl(d, "wide.wordmark", 200, ext_top + 10, 260, 78, "叠光", C["ink"],
       S["wordmark"], style="BOLD")
    fl(d, "wide.wordmark-latin", 200, ext_top + 90, 380, 42, "Layerlight", C["muted"],
       S["wordmarkLatin"], spacing=4)
    kicker(d, "wide.kicker", 1000, ext_top + 40, S["kicker"], 6)
    fl(d, "wide.display-1", 72, 250, 800, 128, "让复杂信息", C["ink"], S["display"], style="BOLD")
    fl(d, "wide.display-2", 72, 386, 800, 128, "变得清晰", C["cyan"], S["display"], style="BOLD")
    hairline(d, "wide.rule-1", 940, 300, 428)
    fl(d, "wide.date-label", 940, 326, 300, 40, "发布时间", C["muted"], S["meta"])
    fl(d, "wide.date", 940, 368, 428, 60, "2026.11.07 19:30", C["ink"], S["h2"],
       style="BOLD")
    fl(d, "wide.speakers", 940, 440, 428, 42, "讲者：林川 / 苏言", C["muted"], S["body"])
    hairline(d, "wide.rule-2", 72, 700, 1008)   # 不穿过右下角叠光带
    fl(d, "wide.url-label", 72, 638, 200, 40, "了解更多", C["muted"], S["meta"])
    fl(d, "wide.url", 280, 636, 620, 40, "layerlight.example.org", C["cyan"], S["meta"])
    return d.dsl(), W, H, {"ext_top": [0, 0, W, ext_top],
                           "ext_bottom": [0, H - ext_bottom, W, ext_bottom]}


def check_required(plane, name, rnd):
    joined = "".join(v["text"] for v in plane.values() if "text" in v)
    missing = [r for r in REQUIRED[rnd] if r not in joined
               and not (r == "让复杂信息变得清晰" and "让复杂信息" in joined
                        and "变得清晰" in joined)]
    assert not missing, "%s 缺必需文案 %s" % (name, missing)


def audit_layout(plane, canvas, max_title_lines=3, min_title_px=48):
    """长标题与新增信息的碰撞审计。

    量的是墨迹盒而不是排版盒：排版盒允许上下留白相碰（第 1 轮 url 与其标签的盒
    就有 4px 重叠），真正决定"看起来撞不撞"的是墨迹。墨迹盒按字号取保守高度、
    按 est_width_px 取宽度，两者都不小于真实墨迹，因此这里判"不重叠"是偏严的。
    """
    boxes = {}
    for k, v in plane.items():
        if "text" not in v:
            continue
        x, y, w, h = v["box_px"]
        size = v["font_px"]
        boxes[k] = (x, y + (h - size) / 2.0, v["est_width_px"], size)
    keys = sorted(boxes)
    is_title = lambda k: ".display-" in k
    overlaps, min_gap, min_pair = [], None, None
    for i, a in enumerate(keys):
        ax, ay, aw, ah = boxes[a]
        for b in keys[i + 1:]:
            bx, by, bw, bh = boxes[b]
            ox = min(ax + aw, bx + bw) - max(ax, bx)
            oy = min(ay + ah, by + bh) - max(ay, by)
            if ox > 1 and oy > 1:
                overlaps.append({"pair": [a, b], "overlap_px": [round(ox, 1), round(oy, 1)]})
            if ox > 1 and is_title(a) and is_title(b):   # 标题行盒按行距连续排布，另计
                continue
            if ox > 1:                      # 同列：量垂直净距
                gap = max(ay, by) - min(ay + ah, by + bh)
                if min_gap is None or gap < min_gap:
                    min_gap, min_pair = round(gap, 1), [a, b]
    titles = {k: v for k, v in plane.items() if "text" in v and "display" in k}
    sizes = {v["font_px"] for v in titles.values()}
    assert len(titles) <= max_title_lines, "标题行数 %s 超上限" % len(titles)
    assert min(sizes) >= min_title_px, "标题字号 %s 低于 %s" % (min(sizes), min_title_px)
    assert not overlaps, "文字盒重叠：%s" % overlaps
    return {
        "gap_basis": "墨迹盒（高=字号、宽=est_width_px，均不小于真实墨迹），非排版盒",
        "text_boxes": len(boxes),
        "text_box_overlaps": overlaps,
        "same_column_min_gap_px": min_gap,
        "same_column_min_gap_pair": min_pair,
        "title_lines": len(titles),
        "title_font_px": sorted(sizes),
        "title_line_breaks": [v["text"] for k, v in sorted(titles.items())],
        "title_ink_line_gap_px": (sorted(v["box_px"][1] for v in titles.values())[1]
                                  - sorted(v["box_px"][1] for v in titles.values())[0]
                                  - min(sizes)) if len(titles) > 1 else None,
        "canvas": list(canvas),
    }


# ---------------- 第 2 轮 竖版 1080x1350 ----------------
def build_portrait_r02(tagline=None):
    W, H = 1080, 1350
    d = Doc(W, H, bg=C["bg"])
    ext_top, ext_bottom = 104, 88
    # 叠光带仍缩在右下角：AABB 左界 818 让开文字列右界 788，下界 1253 让开底部扩展带
    light_ribbon(d, "bg", 980, 1140, 3.8)
    brand_mark(d, "mark", 88 + 66, ext_top + 66, 132)
    fl(d, "portrait.wordmark", 244, ext_top + 22, 320, 76, "叠光", C["ink"],
       S["wordmark"], style="BOLD")
    fl(d, "portrait.wordmark-latin", 244, ext_top + 104, 420, 40, "Layerlight",
       C["muted"], S["wordmarkLatin"], spacing=4)
    kicker(d, "portrait.kicker", 88, 320, S["kicker"], 6)
    # 长主标题：3 行 64px，按语义在冒号处分断，不做任何横向压窄
    for i, line in enumerate(TITLE_R02):
        fl(d, "portrait.display-%d" % (i + 1), 88, 410 + i * 94, 904, 94, line,
           C["cyan"] if i == 2 else C["ink"], 64, style="BOLD")
    hairline(d, "portrait.rule-1", 88, 716, 904)
    # 新增信息与标题分栏：左列时间，右列讲者与参与方式，两列互不相碰
    fl(d, "portrait.date-label", 88, 730, 300, 40, "发布时间", C["muted"], S["meta"])
    fl(d, "portrait.date", 88, 780, 420, 60, "2026.11.07 19:30", C["ink"], S["h2"],
       style="BOLD")
    fl(d, "portrait.speakers", 540, 730, 452, 44, "讲者：林川 / 苏言", C["muted"], S["body"])
    fl(d, "portrait.free", 540, 786, 452, 44, "免费参加 · 无需报名", C["cyan"], 28)
    hairline(d, "portrait.rule-2", 88, 872, 904)
    fl(d, "portrait.sponsor-label", 88, 884, 240, 40, "赞助方", C["muted"], S["meta"])
    fl(d, "portrait.sponsor", 88, 932, 700, 44, "Northstar Research / 云构工具",
       C["ink"], S["meta"])
    y_url_label, y_url = 1060, 1108
    if tagline:      # 第 3 轮新增英语短句，落在赞助方带与网址带之间
        fl(d, "portrait.tagline", 88, 1000, 700, 44, tagline, C["primary"], 30,
           spacing=1.5)
    fl(d, "portrait.url-label", 88, y_url_label, 240, 40, "了解更多", C["muted"], S["meta"])
    fl(d, "portrait.url", 88, y_url, 700, 40, "layerlight.example.org", C["cyan"],
       S["meta"])
    return d.dsl(), W, H, {"ext_top": [0, 0, W, ext_top],
                           "ext_bottom": [0, H - ext_bottom, W, ext_bottom]}


# ---------------- 第 2 轮 横版 1440x810 ----------------
def build_wide_r02(tagline=None):
    W, H = 1440, 810
    d = Doc(W, H, bg=C["bg"])
    ext_top, ext_bottom = 72, 72
    light_ribbon(d, "bg", 1300, 628, 3.7)
    brand_mark(d, "mark", 72 + 54, ext_top + 54, 108)
    fl(d, "wide.wordmark", 200, ext_top + 10, 260, 78, "叠光", C["ink"],
       S["wordmark"], style="BOLD")
    fl(d, "wide.wordmark-latin", 200, ext_top + 90, 380, 42, "Layerlight", C["muted"],
       S["wordmarkLatin"], spacing=4)
    kw = math.ceil(((TF.w("ONLINE LAUNCH", S["kicker"]) + 6 * 13) * 1.10) / TF.SLACK) + 56
    kicker(d, "wide.kicker", W - 72 - kw, ext_top + 40, S["kicker"], 6)
    # 标题列右界 912，信息列左界 940：28px 的列间通道，长标题不可能碰到信息
    for i, line in enumerate(TITLE_R02):
        fl(d, "wide.display-%d" % (i + 1), 72, 236 + i * 94, 840, 94, line,
           C["cyan"] if i == 2 else C["ink"], 64, style="BOLD")
    hairline(d, "wide.rule-1", 940, 216, 428)
    fl(d, "wide.date-label", 940, 232, 300, 40, "发布时间", C["muted"], S["meta"])
    fl(d, "wide.date", 940, 282, 428, 60, "2026.11.07 19:30", C["ink"], S["h2"],
       style="BOLD")
    fl(d, "wide.speakers", 940, 354, 428, 44, "讲者：林川 / 苏言", C["muted"], S["body"])
    fl(d, "wide.free", 940, 410, 428, 44, "免费参加 · 无需报名", C["cyan"], 28)
    y_rule2, y_sponsor, y_url = 566, 588, 648
    if tagline:      # 第 3 轮：短句接在标题块之下，分隔带与底栏整体下移 12px
        fl(d, "wide.tagline", 72, 524, 840, 40, tagline, C["primary"], 30, spacing=1.5)
        y_rule2, y_sponsor, y_url = 578, 600, 660
    hairline(d, "wide.rule-2", 72, y_rule2, 1008)   # 止于右下叠光带之前
    fl(d, "wide.sponsor-label", 72, y_sponsor + 2, 200, 40, "赞助方", C["muted"], S["meta"])
    fl(d, "wide.sponsor", 280, y_sponsor, 700, 44, "Northstar Research / 云构工具",
       C["ink"], S["meta"])
    fl(d, "wide.url-label", 72, y_url + 2, 200, 40, "了解更多", C["muted"], S["meta"])
    fl(d, "wide.url", 280, y_url, 700, 44, "layerlight.example.org", C["cyan"], S["meta"])
    return d.dsl(), W, H, {"ext_top": [0, 0, W, ext_top],
                           "ext_bottom": [0, H - ext_bottom, W, ext_bottom]}


def build_portrait_r03():
    use_palette(3)
    return build_portrait_r02(tagline=TOK["tagline"])


def build_wide_r03():
    use_palette(3)
    return build_wide_r02(tagline=TOK["tagline"])


BUILDERS = {1: {"launch-portrait": build_portrait, "launch-wide": build_wide},
            2: {"launch-portrait": build_portrait_r02, "launch-wide": build_wide_r02},
            3: {"launch-portrait": build_portrait_r03, "launch-wide": build_wide_r03}}


if __name__ == "__main__":
    rnd = int(sys.argv[sys.argv.index("--round") + 1]) if "--round" in sys.argv else 1
    LAY = LAY / ("round-%02d" % rnd)
    LAY.mkdir(parents=True, exist_ok=True)
    for name, fn in BUILDERS[rnd].items():
        PLANE.clear()
        dsl, w, h, ext = fn()
        check_required(PLANE, name, rnd)
        audit = audit_layout(PLANE, (w, h))
        (LAY / (name + ".snapshot")).write_bytes(dsl.encode("utf-8"))
        (LAY / (name + ".plane.json")).write_text(
            json.dumps({"plane": PLANE, "canvas": [w, h], "extension_zones": ext,
                        "collision_audit": audit}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        print(name, w, h, "元素", len(PLANE), "DSL", len(dsl.encode("utf-8")), "B",
              "| 同列最小间隙", audit["same_column_min_gap_px"], audit["same_column_min_gap_pair"])

