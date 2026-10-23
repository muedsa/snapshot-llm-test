"""A21 双尺寸版式构造：launch-portrait 1080x1350 与 launch-wide 1440x810。

两图共用同一套 token 与品牌构件，但分别构图：
  portrait —— 纵向结构：顶部品牌行；眉标 + 主标题两行居左；右中发光球作氛围锚点；
              主色强调条 → 细分隔线 → 信息栈（日期/讲者/网址牌）自上而下
  wide     —— 横向分栏：左栏品牌行 + 眉标 + 主标题两行，底部日期与讲者横排、
              网址牌收尾；右栏发光球大图占位
wide 的信息区是横排、portrait 是纵排，且主视觉在 portrait 位于右下、
在 wide 位于右侧整栏，两者不是同一布局的等比缩放。

字号：主标题 portrait 132 / wide 116（均 ≥56）；其余最小 28（均 ≥24）。
"""
from __future__ import annotations

from a21_core import C, Canvas, draw_mark, draw_orb


def default_text() -> dict:
    return {
        "brand_cn": "叠光",
        "brand_en": "Layerlight",
        "kicker": "ONLINE LAUNCH",
        "title_full": "让复杂信息变得清晰",
        "title_1": "让复杂信息",
        "title_2": "变得清晰",
        "date": "2026.11.07 19:30",
        "speakers": "讲者：林川 / 苏言",
        "url": "layerlight.example.org",
    }


def default_cfg() -> dict:
    return {
        "text": default_text(),
        "colors": dict(C),
        "title_size_portrait": 132,
        "title_size_wide": 116,
        "type": {"kicker_p": 32, "kicker_w": 30, "date_p": 56, "date_w": 44,
                 "speak_p": 34, "speak_w": 30, "url_p": 32, "url_w": 28,
                 "brand_p": 36, "brand_w": 30},
        "kicker_spacing": 8,
        "mark_size_portrait": 76,
        "mark_size_wide": 58,
        "orb_radius_portrait": 130,
        "orb_radius_wide": 190,
        "left": 96,
    }


def _wordmark(cv, left, mark_top, mark_size, box_h, size, text, col, gap):
    """品牌字标：中文主色 + 英文次要色，两段独立 <Text> 并排，垂直居中于标记。

    不用嵌套 Text span 混色：服务端会裁掉子 span 的前导空白，实测「叠光」与
    Layerlight 之间的空格丢失（render-01 已看图确认，36px 时「叠光」墨迹 224-291、
    Layerlight 墨迹自 298 起，只剩 6px 常规字距，视觉上无分隔）。拆成两段后
    间距由 left + size*len(cn) + gap 显式给出；CJK 全角字 advance 恰为 1em，
    故中文段宽取 size*len(cn)（36px 实测 advance 止于 294，与墨迹 291 相符）。
    """
    top = mark_top + (mark_size - box_h) // 2
    cn, en = text["brand_cn"], text["brand_en"]
    cv.text(left, top, size * len(cn), box_h, cn, size,
            color=col["primary"], role="brand_cn", line_h=1.0)
    cv.text(left + size * len(cn) + gap, top, 200, box_h, en, size,
            color=col["muted"], role="brand_en", line_h=1.0)


def build_portrait(cfg: dict):
    """1080x1350 竖版海报。"""
    W, H, LX = 1080, 1350, cfg["left"]
    t, col = cfg["text"], cfg["colors"]
    ts = cfg["title_size_portrait"]
    ty = cfg["type"]
    cv = Canvas(W, H, col["bg_deep"])

    # ---- 氛围 wash：左下径向渐隐，压暗增层次，不覆盖任何文字墨迹 ----
    cv.box(-280, 720, 1000, 1000, shape="CIRCLE",
           gradient=("RADIAL", ["#12395F", "#05080F"], None),
           gradius=0.72, opacity=0.55, kind="ambient", role="ambient")

    # ---- 右上：线叠层角部水印（仅描边、无填充）----
    # 与左上实心主标记同构但只用描边，故读作「层」的纹理而非重复的 Logo；
    # 用于填补 render-01 中右上的大面积空白，并与左下的氛围 wash 形成对角重量。
    ws, wo = 300, 50
    for i, (lcol, lop) in enumerate((("#16385E", 0.45), ("#1E5688", 0.62),
                                    ("#2E7FB8", 0.80))):
        cv.box(828 + i * wo, -132 + i * wo, ws, ws, color=None,
               border="2 SOLID %s" % lcol, radius=int(round(ws * 0.30)),
               opacity=lop, kind="corner_sheet", role="corner-motif")

    # ---- 顶部品牌行 ----
    ms = cfg["mark_size_portrait"]
    m_top = 118
    draw_mark(cv, LX, m_top, ms)
    _wordmark(cv, LX + ms + 2 * int(ms * 0.17) + 26, m_top, ms, 52,
              ty["brand_p"], t, col, 14)

    # ---- 右中发光球（主视觉锚点）----
    ro = cfg["orb_radius_portrait"]
    draw_orb(cv, 884, 700, ro, halo=True, ring=True, bands=[
        {"w": int(ro * 1.62), "h": 14, "dy": -int(ro * 0.30), "opacity": 0.90},
        {"w": int(ro * 1.28), "h": 10, "dy": int(ro * 0.06), "opacity": 0.58},
        {"w": int(ro * 0.96), "h": 8, "dy": int(ro * 0.36), "opacity": 0.34},
    ])

    # ---- 眉标 ----
    ky = 302
    cv.box(LX, ky + 6, 6, 40, color=col["accent"], radius=3,
           kind="accent_bar", role="hairline-rule")
    cv.text(LX + 30, ky, 620, 52, t["kicker"], ty["kicker_p"],
            color=col["primary"], spacing=cfg["kicker_spacing"],
            role="kicker", line_h=1.0)

    # ---- 主标题两行 ----
    ty1 = 404
    ty2 = ty1 + int(ts * 1.30)
    for i, (top, val) in enumerate(((ty1, t["title_1"]), (ty2, t["title_2"])), 1):
        cv.text(LX, top, 860, int(ts * 1.2), val, ts, color=col["ink"],
                bold=True, line_h=1.0, role="title_line%d" % i,
                shadow="0 8 26 #5FE0FF2E")

    # ---- 主色强调条（标题与信息之间唯一的分隔；render-01 另有一条灰细线，
    #      与强调条仅隔 66px、长度不一，读起来像误留的笔画，故删除）----
    uy = ty2 + int(ts * 1.30) + 58
    cv.box(LX, uy, 156, 6, color=col["primary"], radius=3,
           kind="accent_bar", role="hairline-rule")

    # ---- 信息栈 ----
    dy = uy + 74
    cv.text(LX, dy, 720, int(ty["date_p"] * 1.25), t["date"], ty["date_p"],
            color=col["accent"], bold=True, role="date", line_h=1.0)
    sy = dy + int(ty["date_p"] * 1.96)
    cv.text(LX, sy, 720, int(ty["speak_p"] * 1.3), t["speakers"],
            ty["speak_p"], color=col["muted"], role="speakers", line_h=1.0)

    # ---- 网址牌 ----
    py = sy + 72
    ph = 84
    cv.box(LX, py, 632, ph, color=col["bg_panel"], radius=ph // 2,
           border="2 SOLID #24507A", kind="url_plate", role="url-plate")
    cv.box(LX + 26, py + 32, 20, 20, shape="CIRCLE", color=col["primary"],
           radius=10, kind="url_dot", role="light-core")
    cv.text(LX + 64, py + 20, 540, 44, t["url"], ty["url_p"],
            color=col["glow"], role="url", line_h=1.0)

    return cv


def build_wide(cfg: dict):
    """1440x810 横版。"""
    W, H, LX = 1440, 810, cfg["left"]
    t, col = cfg["text"], cfg["colors"]
    ts = cfg["title_size_wide"]
    ty = cfg["type"]
    cv = Canvas(W, H, col["bg_deep"])

    # ---- 氛围 wash ----
    cv.box(-320, -320, 1020, 1020, shape="CIRCLE",
           gradient=("RADIAL", ["#12395F", "#05080F"], None),
           gradius=0.70, opacity=0.42, kind="ambient", role="ambient")

    # ---- 右栏发光球大图（主视觉）----
    ro = cfg["orb_radius_wide"]
    draw_orb(cv, 1152, 404, ro, halo=True, ring=True, bands=[
        {"w": int(ro * 1.72), "h": 18, "dy": -int(ro * 0.30), "opacity": 0.92},
        {"w": int(ro * 1.40), "h": 12, "dy": int(ro * 0.08), "opacity": 0.58},
        {"w": int(ro * 1.04), "h": 10, "dy": int(ro * 0.42), "opacity": 0.34},
    ])

    # ---- 左栏品牌行 ----
    ms = cfg["mark_size_wide"]
    m_top = 88
    draw_mark(cv, LX, m_top, ms)
    _wordmark(cv, LX + ms + 2 * int(ms * 0.17) + 24, m_top, ms, 42,
              ty["brand_w"], t, col, 12)

    # ---- 眉标 ----
    ky = 200
    cv.box(LX, ky + 4, 5, 34, color=col["accent"], radius=2,
           kind="accent_bar", role="hairline-rule")
    cv.text(LX + 28, ky, 620, 44, t["kicker"], ty["kicker_w"],
            color=col["primary"], spacing=cfg["kicker_spacing"],
            role="kicker", line_h=1.0)

    # ---- 主标题两行 ----
    ty1 = 276
    ty2 = ty1 + int(ts * 1.30)
    for i, (top, val) in enumerate(((ty1, t["title_1"]), (ty2, t["title_2"])), 1):
        cv.text(LX, top, 860, int(ts * 1.2), val, ts, color=col["ink"],
                bold=True, line_h=1.0, role="title_line%d" % i,
                shadow="0 6 22 #5FE0FF2E")

    # ---- 底部信息横排：日期（左）｜竖分隔线｜讲者（右）----
    dy = ty2 + int(ts * 1.30) + 14
    cv.text(LX, dy, 500, int(ty["date_w"] * 1.25), t["date"], ty["date_w"],
            color=col["accent"], bold=True, role="date", line_h=1.0)
    cv.box(596, dy + 10, 2, int(ty["speak_w"] * 1.15), color=col["rule"],
           kind="rule", role="hairline-rule")
    cv.text(626, dy + 8, 420, int(ty["speak_w"] * 1.3), t["speakers"],
            ty["speak_w"], color=col["muted"], role="speakers", line_h=1.0)

    # ---- 网址牌 ----
    py = dy + int(ty["date_w"] * 1.96)
    ph = 60
    cv.box(LX, py, 552, ph, color=col["bg_panel"], radius=ph // 2,
           border="2 SOLID #24507A", kind="url_plate", role="url-plate")
    cv.box(LX + 24, py + 22, 16, 16, shape="CIRCLE", color=col["primary"],
           radius=8, kind="url_dot", role="light-core")
    cv.text(LX + 58, py + 12, 470, 36, t["url"], ty["url_w"],
            color=col["glow"], role="url", line_h=1.0)

    return cv


BUILDERS = {"portrait": build_portrait, "wide": build_wide}
SIZES = {"portrait": (1080, 1350), "wide": (1440, 810)}


# =====================================================================
# 第二轮：长标题 + 赞助方 + 报名状态
# 需求（rounds/round-02.md）：
#   主标题替换为「当所有信息都想成为标题：让复杂信息变得清晰的结构化方法」，
#   最多 3 行、字号 ≥48；新增「Northstar Research / 云构工具」与
#   「免费参加 · 无需报名」；日期、讲者、ONLINE LAUNCH、网址必须保留；
#   主色与 3–6 个品牌构件形态不变，允许移动和缩放装饰；两尺寸不变；
#   不得用变形压窄文字。
# 因此本轮的改动只落在：文案、字号、装饰的位移与缩放、信息区增行。
# 品牌构件仍是 6 个（牌子族多出「报名状态牌」一个实例，形态同源）。
# =====================================================================


def default_text_r2() -> dict:
    t = default_text()
    t["title_full"] = "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法"
    # 竖版 3 行、横版 2 行，两处分行都整句覆盖 title_full
    t["title_1"] = "当所有信息都想成为标题："
    t["title_2"] = "让复杂信息变得清晰"
    t["title_3"] = "的结构化方法"
    t["title_2w"] = "让复杂信息变得清晰的结构化方法"   # 横版第 2 行
    t["sponsors"] = "Northstar Research / 云构工具"
    t["badge"] = "免费参加 · 无需报名"
    return t


def default_cfg_r2() -> dict:
    c = default_cfg()
    c["text"] = default_text_r2()
    # 27 字进 3 行：竖版 66px（12 字行 792px，落在 860 的文本盒内不折行），
    # 横版 52px 两行（15 字行 780px，横版更宽故行更少）。两者都 ≥48。
    c["title_size_portrait"] = 66
    c["title_size_wide"] = 52
    # 标题变小后仍保持「主标题 > 日期 > 讲者/网址」的层级，故各档同比例下调
    c["type"].update({
        "kicker_p": 32, "kicker_w": 30,
        "date_p": 48, "date_w": 36,
        "speak_p": 30, "speak_w": 28,
        "url_p": 30, "url_w": 28,
        "brand_p": 36, "brand_w": 30,
        "spon_p": 30, "spon_w": 28,
        "badge_p": 30, "badge_w": 28,
    })
    c["mark_size_portrait"] = 72
    c["mark_size_wide"] = 52
    c["orb_radius_portrait"] = 165
    c["orb_radius_wide"] = 175
    return c


def _badge(cv, left, top, w, h, size, text, col):
    """报名状态牌：牌子族的新实例，形态与网址牌同源（圆角矩形 + 边框），
    区别只在边框用主色（网址牌用中性蓝），以区分「可访问地址」与「报名状态」。
    不新增品牌构件——与网址牌同属 plate 族。
    """
    cv.box(left, top, w, h, color=col["bg_panel"], radius=h // 2,
           border="2 SOLID %s" % col["primary"], kind="url_plate",
           role="url-plate")
    cv.text(left + 30, top + (h - 36) // 2, w - 60, 36, text, size,
            color=col["ink"], role="badge", line_h=1.0)


def build_portrait_r2(cfg: dict):
    """1080x1350 竖版，第二轮：3 行长标题 + 赞助方 + 报名状态牌。

    竖版把 3 行标题放在左半，发光球移到底部右中填补右下的空区，
    角部水印仍留在右上，与标题首行不相交。
    """
    W, H, LX = 1080, 1350, cfg["left"]
    t, col = cfg["text"], cfg["colors"]
    ts = cfg["title_size_portrait"]
    ty = cfg["type"]
    cv = Canvas(W, H, col["bg_deep"])

    # ---- 氛围 wash：左下径向渐隐 ----
    cv.box(-300, 700, 1000, 1000, shape="CIRCLE",
           gradient=("RADIAL", ["#12395F", "#05080F"], None),
           gradius=0.72, opacity=0.55, kind="ambient", role="ambient")

    # ---- 右上：线叠层角部水印（仅描边、无填充），与第一轮同形，仅缩放 ----
    ws, wo = 288, 52
    for i, (lcol, lop) in enumerate((("#16385E", 0.45), ("#1E5688", 0.62),
                                     ("#2E7FB8", 0.80))):
        cv.box(846 + i * wo, -150 + i * wo, ws, ws, color=None,
               border="2 SOLID %s" % lcol, radius=int(round(ws * 0.30)),
               opacity=lop, kind="corner_sheet", role="corner-motif")

    # ---- 顶部品牌行 ----
    ms = cfg["mark_size_portrait"]
    m_top = 112
    draw_mark(cv, LX, m_top, ms)
    _wordmark(cv, LX + ms + 2 * int(ms * 0.17) + 26, m_top, ms, 52,
              ty["brand_p"], t, col, 14)

    # ---- 眉标 ----
    ky = 288
    cv.box(LX, ky + 6, 6, 40, color=col["accent"], radius=3,
           kind="accent_bar", role="hairline-rule")
    cv.text(LX + 30, ky, 640, 52, t["kicker"], ty["kicker_p"],
            color=col["primary"], spacing=cfg["kicker_spacing"],
            role="kicker", line_h=1.0)

    # ---- 主标题三行 ----
    step = int(ts * 1.30)
    ty1 = 350
    for i, key in enumerate(("title_1", "title_2", "title_3")):
        top = ty1 + i * step
        cv.text(LX, top, 860, int(ts * 1.2), t[key], ts, color=col["ink"],
                bold=True, line_h=1.0, role="title_line%d" % (i + 1),
                shadow="0 8 26 #5FE0FF2E")

    # ---- 主色强调条（标题与信息之间唯一的分隔，形态同第一轮）----
    uy = ty1 + 2 * step + int(ts * 1.30) + 56
    cv.box(LX, uy, 156, 6, color=col["primary"], radius=3,
           kind="accent_bar", role="hairline-rule")

    # ---- 信息栈：日期 / 讲者 / 网址牌 ----
    dy = uy + 76
    cv.text(LX, dy, 720, int(ty["date_p"] * 1.25), t["date"], ty["date_p"],
            color=col["accent"], bold=True, role="date", line_h=1.0)
    sy = dy + int(ty["date_p"] * 1.96)
    cv.text(LX, sy, 720, int(ty["speak_p"] * 1.3), t["speakers"],
            ty["speak_p"], color=col["muted"], role="speakers", line_h=1.0)

    py = sy + 70
    ph = 84
    cv.box(LX, py, 560, ph, color=col["bg_panel"], radius=ph // 2,
           border="2 SOLID #24507A", kind="url_plate", role="url-plate")
    cv.box(LX + 26, py + (ph - 20) // 2, 20, 20, shape="CIRCLE",
           color=col["primary"], radius=10, kind="url_dot", role="light-core")
    cv.text(LX + 64, py + 20, 480, 44, t["url"], ty["url_p"],
            color=col["glow"], role="url", line_h=1.0)

    # ---- 赞助方（新增）----
    sy2 = py + ph + 80
    cv.text(LX, sy2, 760, int(ty["spon_p"] * 1.3), t["sponsors"],
            ty["spon_p"], color=col["muted"], role="sponsors", line_h=1.0)

    # ---- 报名状态牌（新增）----
    _badge(cv, LX, sy2 + 70, 404, 62, ty["badge_p"], t["badge"], col)

    # ---- 右中偏下发光球（主视觉）：填补 3 行标题与底部信息之间的空区 ----
    ro = cfg["orb_radius_portrait"]
    draw_orb(cv, 905, 800, ro, halo=True, ring=True, bands=[
        {"w": int(ro * 1.62), "h": 14, "dy": -int(ro * 0.30), "opacity": 0.90},
        {"w": int(ro * 1.28), "h": 10, "dy": int(ro * 0.06), "opacity": 0.58},
        {"w": int(ro * 0.96), "h": 8, "dy": int(ro * 0.36), "opacity": 0.34},
    ])

    return cv


def build_wide_r2(cfg: dict):
    """1440x810 横版，第二轮：2 行长标题 + 赞助方 + 报名状态牌。

    横版更宽，标题用 2 行即可容纳（15 字行 780px），因此竖排信息区能整体
    上移，把赞助方与报名状态牌做成底部两行；发光球占据右整栏。
    与竖版不是等比缩放——竖版 3 行标题、横版 2 行，球体在竖版位于右中偏下、
    在横版位于右侧整栏中部。
    """
    W, H, LX = 1440, 810, cfg["left"]
    t, col = cfg["text"], cfg["colors"]
    ts = cfg["title_size_wide"]
    ty = cfg["type"]
    cv = Canvas(W, H, col["bg_deep"])

    # ---- 氛围 wash：左下 ----
    cv.box(-300, 200, 1000, 1000, shape="CIRCLE",
           gradient=("RADIAL", ["#12395F", "#05080F"], None),
           gradius=0.72, opacity=0.42, kind="ambient", role="ambient")

    # ---- 右栏发光球大图（主视觉）----
    ro = cfg["orb_radius_wide"]
    draw_orb(cv, 1190, 400, ro, halo=True, ring=True, bands=[
        {"w": int(ro * 1.72), "h": 18, "dy": -int(ro * 0.30), "opacity": 0.92},
        {"w": int(ro * 1.40), "h": 12, "dy": int(ro * 0.08), "opacity": 0.58},
        {"w": int(ro * 1.04), "h": 10, "dy": int(ro * 0.42), "opacity": 0.34},
    ])

    # ---- 左栏品牌行 ----
    ms = cfg["mark_size_wide"]
    m_top = 74
    draw_mark(cv, LX, m_top, ms)
    _wordmark(cv, LX + ms + 2 * int(ms * 0.17) + 24, m_top, ms, 42,
              ty["brand_w"], t, col, 12)

    # ---- 眉标（横版强调条为竖条，形态同第一轮）----
    ky = 150
    cv.box(LX, ky + 4, 5, 34, color=col["accent"], radius=2,
           kind="accent_bar", role="hairline-rule")
    cv.text(LX + 28, ky, 620, 44, t["kicker"], ty["kicker_w"],
            color=col["primary"], spacing=cfg["kicker_spacing"],
            role="kicker", line_h=1.0)

    # ---- 主标题两行（横版更宽，第 2 行整句 15 字可容）----
    step = int(ts * 1.30)
    ty1 = 212
    for i, key in enumerate(("title_1", "title_2w")):
        top = ty1 + i * step
        cv.text(LX, top, 860, int(ts * 1.2), t[key], ts, color=col["ink"],
                bold=True, line_h=1.0, role="title_line%d" % (i + 1),
                shadow="0 6 22 #5FE0FF2E")

    # ---- 底部信息竖排：日期 / 讲者 / 网址牌 / 赞助方 / 报名状态牌 ----
    dy = ty1 + step + int(ts * 1.30) + 40
    cv.text(LX, dy, 500, int(ty["date_w"] * 1.25), t["date"], ty["date_w"],
            color=col["accent"], bold=True, role="date", line_h=1.0)
    sy = dy + int(ty["date_w"] * 1.90)
    cv.text(LX, sy, 460, int(ty["speak_w"] * 1.3), t["speakers"],
            ty["speak_w"], color=col["muted"], role="speakers", line_h=1.0)

    py = sy + 52
    ph = 52
    cv.box(LX, py, 540, ph, color=col["bg_panel"], radius=ph // 2,
           border="2 SOLID #24507A", kind="url_plate", role="url-plate")
    cv.box(LX + 24, py + (ph - 14) // 2, 14, 14, shape="CIRCLE",
           color=col["primary"], radius=7, kind="url_dot", role="light-core")
    cv.text(LX + 58, py + 11, 460, 30, t["url"], ty["url_w"],
            color=col["glow"], role="url", line_h=1.0)

    # ---- 赞助方（新增）----
    sy2 = py + ph + 46
    cv.text(LX, sy2, 700, int(ty["spon_w"] * 1.3), t["sponsors"],
            ty["spon_w"], color=col["muted"], role="sponsors", line_h=1.0)

    # ---- 报名状态牌（新增）----
    _badge(cv, LX, sy2 + 50, 400, 46, ty["badge_w"], t["badge"], col)

    return cv


BUILDERS_R2 = {"portrait": build_portrait_r2, "wide": build_wide_r2}
SIZES_R2 = dict(SIZES)


# =====================================================================
# 第三轮：浅色主题 + 全量对比度审计
# 需求（rounds/round-03.md）：改浅色主题，所有普通文字与实际合成背景的对比度
# ≥4.5:1；保留第二轮全部文案与品牌图形；在网址上方新增英语短句
# “Clarity through structure”（≥24）；两尺寸不变，中文长标题仍 ≤3 行、≥48；
# 不得让赞助方消失；不能只改两种颜色而忽略实际叠层。
# 因此本轮改动落在三处：整块调色板、品牌装饰的色带与辉光半径、
# 网址牌上方新增一行英语短句（信息栈整体重排，不删任何一条文案）。
# =====================================================================

# 浅色主题色板。每个文字色都按 round-03.md 给的 WCAG 公式对实际底面预核过：
#   ink   #0B1B33 对 #F5F8FC = 16.17，对纯白 #FFFFFF = 17.22
#   primary #0A6FA8 对 #F5F8FC = 4.82，对纯白 = 5.14
#   accent #C2410C 对 #F5F8FC = 4.86，对纯白 = 5.18
#   muted #4A5A72 对 #F5F8FC = 6.58，对纯白 = 7.01
# 取最严的对照关系（对纯白的最低值 5.14）仍 ≥4.5，故在浅底 wash 或牌子底
# 这类“比页面底更亮”的实际合成色上只会更好，不会跌破阈值。
LIGHT = {
    "bg_deep": "#F5F8FC",   # 页面底：比白略冷的浅蓝灰
    "bg_panel": "#FFFFFF",  # 牌子底面：纯白
    "rule": "#C9D6E5",
    "primary": "#0A6FA8",   # 主色：深青蓝（文字可读档）
    "primary_2": "#1E86C8",
    "primary_3": "#DCE9F4",
    "glow": "#EAFDFF",      # 亮核与光带仍用亮色：它们压在深板材/球体上
    "accent": "#C2410C",    # 暖色降暗保对比
    "ink": "#0B1B33",
    "muted": "#4A5A72",
}

# 浅底板材：比深底更饱和的三段蓝，保证亮核（glow）仍读得出边界
LIGHT_SHEETS = [
    ("#123A5C", "#2F6C96"),
    ("#17598B", "#3F95C8"),
    ("#1E86C8", "#7FC9EE"),
]

LIGHT_CORNER = [("#7FA9CB", 0.55), ("#5A92C0", 0.70), ("#3B7BAB", 0.85)]


def default_text_r3() -> dict:
    """第二轮文案全量保留，只新增一条网址上方的英语短句。"""
    t = default_text_r2()
    t["clarity_en"] = "Clarity through structure"
    return t


def default_cfg_r3() -> dict:
    c = default_cfg_r2()
    c["text"] = default_text_r3()
    c["colors"] = dict(LIGHT)
    c["sheets"] = LIGHT_SHEETS
    c["corner_stack"] = LIGHT_CORNER
    # 标题字号与行数照第二轮不动（竖版 66 三行 / 横版 52 两行），
    # 英语短句新增一档，两个尺寸都 ≥24。
    c["type"].update({"clarity_p": 28, "clarity_w": 26})
    # 装饰：发光球挪到标题与信息栈之外的右列，并把外辉光半径从第二轮的 3.4r
    # 收到 2.7r——这样在两个尺寸上，辉光的填充框与任何一个文字的墨迹都不相交，
    # “实际合成背景”就是页面底或牌子底，而不是球体或辉光叠层。
    # 球体本体仍是同一构件（径向渐变 + 外环 + 三条光带），只是位置与辉光收敛度不同。
    c["orb_radius_portrait"] = 150
    c["orb_radius_wide"] = 175
    c["orb_center_portrait"] = (890, 800)
    c["orb_center_wide"] = (1190, 400)
    c["halo_scale_portrait"] = 2.7
    c["halo_scale_wide"] = 2.75   # 横版画布更宽，右侧整栏可多放一圈辉光
    return c


def build_portrait_r3(cfg: dict):
    """1080x1350 竖版，第三轮：浅色主题 + 网址上方新增英语短句。

    信息栈自上而下：强调条 → 日期 → 讲者 → 英语短句 → 网址牌 → 赞助方 →
    报名状态牌，六行都保留，赞助方仍在。发光球移到标题与信息之间的空区，
    并在信息栈之前绘制，保证牌子与文字永远压在最上层。
    """
    W, H, LX = 1080, 1350, cfg["left"]
    t, col = cfg["text"], cfg["colors"]
    ts = cfg["title_size_portrait"]
    ty = cfg["type"]
    cv = Canvas(W, H, col["bg_deep"])

    # ---- 氛围 wash：左下径向渐白（浅底上比页面底更亮，只会提高文字对比度）----
    cv.box(-300, 700, 1000, 1000, shape="CIRCLE",
           gradient=("RADIAL", ["#FFFFFF", col["bg_deep"]], None),
           gradius=0.72, opacity=0.55, kind="ambient", role="ambient")

    # ---- 右上：线叠层角部水印（仅描边、无填充），形态同第二轮，色带换浅底档 ----
    ws, wo = 288, 52
    for i, (lcol, lop) in enumerate(cfg["corner_stack"]):
        cv.box(846 + i * wo, -150 + i * wo, ws, ws, color=None,
               border="2 SOLID %s" % lcol, radius=int(round(ws * 0.30)),
               opacity=lop, kind="corner_sheet", role="corner-motif")

    # ---- 右中发光球：标题下方、信息栈上方的空区；先画，避免辉光压到牌子 ----
    ro = cfg["orb_radius_portrait"]
    ox, oy = cfg["orb_center_portrait"]
    draw_orb(cv, ox, oy, ro, halo=True, ring=True, bands=[
        {"w": int(ro * 1.62), "h": 14, "dy": -int(ro * 0.30), "opacity": 0.90},
        {"w": int(ro * 1.28), "h": 10, "dy": int(ro * 0.06), "opacity": 0.58},
        {"w": int(ro * 0.96), "h": 8, "dy": int(ro * 0.36), "opacity": 0.34},
    ], halo_scale=cfg["halo_scale_portrait"], halo_stops=["#BFE4F7", "#F5F8FC"],
        halo_opacity=0.50, ring_color=col["primary_2"], ring_pad=30,
        core_stops=["#5FCFF5", "#1E86C8", "#0B2E4E"], core_gradius=0.60,
        band_color=col["glow"])

    # ---- 顶部品牌行 ----
    ms = cfg["mark_size_portrait"]
    m_top = 112
    draw_mark(cv, LX, m_top, ms, sheets_palette=cfg["sheets"],
              core_color=col["glow"], core_shadow="0 6 16 #1E86C840")
    _wordmark(cv, LX + ms + 2 * int(ms * 0.17) + 26, m_top, ms, 52,
              ty["brand_p"], t, col, 14)

    # ---- 眉标 ----
    ky = 288
    cv.box(LX, ky + 6, 6, 40, color=col["accent"], radius=3,
           kind="accent_bar", role="hairline-rule")
    cv.text(LX + 30, ky, 640, 52, t["kicker"], ty["kicker_p"],
            color=col["primary"], spacing=cfg["kicker_spacing"],
            role="kicker", line_h=1.0)

    # ---- 主标题三行 ----
    step = int(ts * 1.30)
    ty1 = 350
    for i, key in enumerate(("title_1", "title_2", "title_3")):
        top = ty1 + i * step
        cv.text(LX, top, 860, int(ts * 1.2), t[key], ts, color=col["ink"],
                bold=True, line_h=1.0, role="title_line%d" % (i + 1))

    # ---- 主色强调条 ----
    uy = ty1 + 2 * step + int(ts * 1.30) + 56
    cv.box(LX, uy, 156, 6, color=col["primary"], radius=3,
           kind="accent_bar", role="hairline-rule")

    # ---- 信息栈：日期 / 讲者 / 英语短句 / 网址牌 ----
    dy = uy + 74
    cv.text(LX, dy, 720, int(ty["date_p"] * 1.25), t["date"], ty["date_p"],
            color=col["accent"], bold=True, role="date", line_h=1.0)
    sy = dy + int(ty["date_p"] * 1.96)
    cv.text(LX, sy, 720, int(ty["speak_p"] * 1.3), t["speakers"],
            ty["speak_p"], color=col["muted"], role="speakers", line_h=1.0)

    # ---- 英语短句（本轮新增，位于网址牌上方）----
    ey = sy + 60
    cv.text(LX, ey, 680, int(ty["clarity_p"] * 1.3), t["clarity_en"],
            ty["clarity_p"], color=col["primary"], spacing=0,
            role="clarity_en", line_h=1.0)

    py = ey + int(ty["clarity_p"] * 1.3) + 16
    ph = 84
    cv.box(LX, py, 560, ph, color=col["bg_panel"], radius=ph // 2,
           border="2 SOLID #C6D6E8", kind="url_plate", role="url-plate")
    cv.box(LX + 26, py + (ph - 20) // 2, 20, 20, shape="CIRCLE",
           color=col["primary"], radius=10, kind="url_dot", role="light-core")
    cv.text(LX + 64, py + 20, 480, 44, t["url"], ty["url_p"],
            color=col["primary"], role="url", line_h=1.0)

    # ---- 赞助方（第二轮文案，本轮保留）----
    sy2 = py + ph + 72
    cv.text(LX, sy2, 760, int(ty["spon_p"] * 1.3), t["sponsors"],
            ty["spon_p"], color=col["muted"], role="sponsors", line_h=1.0)

    # ---- 报名状态牌（第二轮文案，本轮保留）----
    _badge(cv, LX, sy2 + 70, 404, 62, ty["badge_p"], t["badge"], col)

    return cv


def build_wide_r3(cfg: dict):
    """1440x810 横版，第三轮：浅色主题 + 网址上方新增英语短句。

    横版标题仍为 2 行（15 字行 780px），空出的纵向余量让底部信息栈能在
    新增一行后仍保持 ≥70 的下边距；发光球占右侧整栏中部。
    """
    W, H, LX = 1440, 810, cfg["left"]
    t, col = cfg["text"], cfg["colors"]
    ts = cfg["title_size_wide"]
    ty = cfg["type"]
    cv = Canvas(W, H, col["bg_deep"])

    # ---- 氛围 wash：左上径向渐白 ----
    cv.box(-300, -320, 1000, 1000, shape="CIRCLE",
           gradient=("RADIAL", ["#FFFFFF", col["bg_deep"]], None),
           gradius=0.72, opacity=0.42, kind="ambient", role="ambient")

    # ---- 右栏发光球（主视觉），先画 ----
    ro = cfg["orb_radius_wide"]
    ox, oy = cfg["orb_center_wide"]
    draw_orb(cv, ox, oy, ro, halo=True, ring=True, bands=[
        {"w": int(ro * 1.72), "h": 18, "dy": -int(ro * 0.30), "opacity": 0.92},
        {"w": int(ro * 1.40), "h": 12, "dy": int(ro * 0.08), "opacity": 0.58},
        {"w": int(ro * 1.04), "h": 10, "dy": int(ro * 0.42), "opacity": 0.34},
    ], halo_scale=cfg["halo_scale_wide"], halo_stops=["#BFE4F7", "#F5F8FC"],
        halo_opacity=0.50, ring_color=col["primary_2"], ring_pad=30,
        core_stops=["#5FCFF5", "#1E86C8", "#0B2E4E"], core_gradius=0.60,
        band_color=col["glow"])

    # ---- 左栏品牌行 ----
    ms = cfg["mark_size_wide"]
    m_top = 74
    draw_mark(cv, LX, m_top, ms, sheets_palette=cfg["sheets"],
              core_color=col["glow"], core_shadow="0 6 16 #1E86C840")
    _wordmark(cv, LX + ms + 2 * int(ms * 0.17) + 24, m_top, ms, 42,
              ty["brand_w"], t, col, 12)

    # ---- 眉标 ----
    ky = 150
    cv.box(LX, ky + 4, 5, 34, color=col["accent"], radius=2,
           kind="accent_bar", role="hairline-rule")
    cv.text(LX + 28, ky, 620, 44, t["kicker"], ty["kicker_w"],
            color=col["primary"], spacing=cfg["kicker_spacing"],
            role="kicker", line_h=1.0)

    # ---- 主标题两行 ----
    step = int(ts * 1.30)
    ty1 = 212
    for i, key in enumerate(("title_1", "title_2w")):
        top = ty1 + i * step
        cv.text(LX, top, 860, int(ts * 1.2), t[key], ts, color=col["ink"],
                bold=True, line_h=1.0, role="title_line%d" % (i + 1))

    # ---- 底部信息竖排：日期 / 讲者 / 英语短句 / 网址牌 / 赞助方 / 报名状态牌 ----
    dy = ty1 + step + int(ts * 1.30) + 28
    cv.text(LX, dy, 500, int(ty["date_w"] * 1.25), t["date"], ty["date_w"],
            color=col["accent"], bold=True, role="date", line_h=1.0)
    sy = dy + int(ty["date_w"] * 1.82)
    cv.text(LX, sy, 460, int(ty["speak_w"] * 1.3), t["speakers"],
            ty["speak_w"], color=col["muted"], role="speakers", line_h=1.0)

    ey = sy + 34
    cv.text(LX, ey, 680, int(ty["clarity_w"] * 1.3), t["clarity_en"],
            ty["clarity_w"], color=col["primary"], spacing=0,
            role="clarity_en", line_h=1.0)

    py = ey + int(ty["clarity_w"] * 1.3) + 10
    ph = 52
    cv.box(LX, py, 540, ph, color=col["bg_panel"], radius=ph // 2,
           border="2 SOLID #C6D6E8", kind="url_plate", role="url-plate")
    cv.box(LX + 24, py + (ph - 14) // 2, 14, 14, shape="CIRCLE",
           color=col["primary"], radius=7, kind="url_dot", role="light-core")
    cv.text(LX + 58, py + 11, 460, 30, t["url"], ty["url_w"],
            color=col["primary"], role="url", line_h=1.0)

    sy2 = py + ph + 38
    cv.text(LX, sy2, 700, int(ty["spon_w"] * 1.3), t["sponsors"],
            ty["spon_w"], color=col["muted"], role="sponsors", line_h=1.0)

    _badge(cv, LX, sy2 + 42, 400, 46, ty["badge_w"], t["badge"], col)

    return cv


BUILDERS_R3 = {"portrait": build_portrait_r3, "wide": build_wide_r3}
SIZES_R3 = dict(SIZES)
