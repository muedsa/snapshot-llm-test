"""A13 生成器：两个几何方向预览 + 四张最终交付件 + 构件几何清单。

设计基线
--------
网格单位 u = 32 px，512 = 16u。标志活动区 14u = 448（32..480），四周留白 1u = 32 px。
纯单色相（teal）阶调，不设第二强调色——「叠光」的叠层靠同一色相的深浅表达，
不靠并置色相。徽章用最亮阶做实底，靠明度差而不是新色相获得能量。

黑版约束反过来限制了构图：**每个构件之间必须隔透明空隙**。黑版里只有"有/无覆盖"
两种状态，两个不透明构件一旦重叠就熔成一团，颜色版里靠色相分辨的结构会消失。
所以两个方向都做成构件互不重叠、负空间全部真透明的形态。

两个方向（都先出 512×512 透明预览，看图与 32 px 实测后再选）：
  A「环孔叠层」环 + 三条等距递减信息层，4 个构件
  B「同心叠光」外环 + 内环 + 中心光点，3 个构件

用法：
  SNAPSHOT_RUN_ID=<rid> python -I a13_pages.py previews     # 两个方向预览
  SNAPSHOT_RUN_ID=<rid> python -I a13_pages.py finals       # 四张最终交付件
  SNAPSHOT_RUN_ID=<rid> python -I a13_pages.py checks       # 只跑前置校验
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S  # noqa: E402
import snap_client as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A13"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)

# ---------------------------------------------------------------- 基础参数
U = 32                      # 网格单位
SYMBOL = 512                # 图标画布
LIVE = 14 * U               # 活动区边长 448
MARGIN = (SYMBOL - LIVE) // 2   # 四周留白 32

CJK = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
LATIN_EM = 0.47     # A12 实测：Noto Sans CJK SC 里 Latin 平均墨宽 0.47 em
MONO_EM = 0.60      # Noto Sans Mono CJK SC 实测非全宽：海报 URL 22 字 @24px 含
                    # 字距 2 实测墨宽 302 px → 单字 11.8 px ≈ 0.49 em；日期 19 字
                    # @28px 得 0.52 em。墨宽不含首末字侧空，真实步进更宽，取 0.60
                    # em 让折行估算偏保守（宁可误报超宽，不可漏报折行裁切）。
WRAP_SLACK = 0.92   # 墨宽估算超过盒宽 92% 即判折行风险（折行后会被裁）

BLACK = "#000000"

# 色板：单色相 teal 阶调 + 墨/纸
PAL = {
    "ink":      "#0B1220",   # 深墨蓝：海报底、正文
    "ink2":     "#131C2E",   # 海报底上的次级面
    "brand-900": "#0C3B37",
    "brand-700": "#134E4A",
    "brand-600": "#0F766E",
    "brand-400": "#2DD4BF",
    "brand-200": "#5EEAD4",
    "brand-100": "#99F0E4",
    "brand-50":  "#D7FBF5",
    "mint":     "#7CC7BD",
    "paper":    "#FFFFFF",
    "paper2":   "#F6F8FA",
    "rule":     "#E2E8F0",
    "rule2":    "#CBD5E1",
    "muted":    "#64748B",
    "faint":    "#94A3B8",
}

# 浅色语境（图标本体、横幅）：深→浅 = 光逐层累积
RAMP_LIGHT = ["brand-700", "brand-600", "brand-400", "brand-200"]
# 深色语境（海报）：全部提到亮部，保持相同明度阶梯
RAMP_DARK = ["brand-200", "brand-400", "brand-100", "brand-50"]

# 固定文案（题面原文，不得改写）
W_CJK = "叠光"
W_LAT = "Layerlight"
TAGLINE = "把复杂信息，组织成清晰画面"
DATE_ONLINE = "2026.11.07 · ONLINE"
BETA = "OPEN BETA"
URL = "layerlight.example.org"


def lh(size: int) -> int:
    """行高 = 1.45 × 字号（A12 实测饱和行距 1.40–1.44，取上界做安全预算）。"""
    return int(round(size * 1.45))


def est_w(text: str, size: int, mono: bool = False, ls: float = 0) -> float:
    """墨宽估算，只用于预判折行；真值以像素量测为准。"""
    w = 0.0
    for ch in text:
        if ch == " ":
            w += size * (0.5 if mono else 0.33)
        elif ord(ch) > 0x2E80:
            w += size * 1.0
        elif ch == "·":
            w += size * 0.67
        else:
            w += size * (MONO_EM if mono else LATIN_EM)
    return w + ls * (len(text) - 1)


# ---------------------------------------------------------------- 构件定义
# 坐标系：512 图标原生坐标，左上原点。motif 是"可独立辨认的几何母形"，
# 构件数按母形实例计（重复放置的母形分别计数；圆环内孔是负空间，不额外计）。
MARK_A = [
    {"id": "A-01", "motif": "annulus", "role": "孔径 / 光圈（叠层之后仍然清晰的那一点）",
     "shape": "CIRCLE", "x": 32, "y": 32, "w": 448, "h": 448,
     "stroke": 48, "tone": 0,
     "negative_space": "内孔半径 176（直径 352）见通透明；三条信息层的角点"
                       "最远落在半径 158.4，距孔壁 17.6，与环体互不重叠，"
                       "所以黑版里同样可辨",
     "dsl": "Container shape=\"CIRCLE\" border=\"48 SOLID <色>\""},
    {"id": "A-02", "motif": "pill", "role": "信息层 1（最长，最靠后）",
     "shape": "RRect", "x": 144, "y": 144, "w": 224, "h": 40, "radius": 20,
     "stroke": 0, "tone": 1,
     "negative_space": "左右端为半径 20 的半圆", "dsl": "Container borderRadius=20"},
    {"id": "A-03", "motif": "pill", "role": "信息层 2",
     "shape": "RRect", "x": 144, "y": 236, "w": 176, "h": 40, "radius": 20,
     "stroke": 0, "tone": 2,
     "negative_space": "与上下两层各隔 52 透明间隙",
     "dsl": "Container borderRadius=20"},
    {"id": "A-04", "motif": "pill", "role": "信息层 3（最短，最靠前）",
     "shape": "RRect", "x": 144, "y": 328, "w": 128, "h": 40, "radius": 20,
     "stroke": 0, "tone": 3,
     "negative_space": "左端与上层对齐，右端收回形成阶梯",
     "dsl": "Container borderRadius=20"},
]

MARK_B = [
    {"id": "B-01", "motif": "annulus", "role": "外环 / 外层层叠",
     "shape": "CIRCLE", "x": 32, "y": 32, "w": 448, "h": 448,
     "stroke": 44, "tone": 0,
     "negative_space": "内孔半径 180（直径 360）见透",
     "dsl": "Container shape=\"CIRCLE\" border=\"44 SOLID <色>\""},
    {"id": "B-02", "motif": "annulus", "role": "内环 / 内层层叠",
     "shape": "CIRCLE", "x": 128, "y": 128, "w": 256, "h": 256,
     "stroke": 44, "tone": 1,
     "negative_space": "与外环之间 52 宽环形负空间",
     "dsl": "Container shape=\"CIRCLE\" border=\"44 SOLID <色>\""},
    {"id": "B-03", "motif": "disc", "role": "中心光点 / 焦点",
     "shape": "CIRCLE", "x": 200, "y": 200, "w": 112, "h": 112,
     "stroke": 0, "tone": 2,
     "negative_space": "与内环之间 28 宽环形负空间",
     "dsl": "Container shape=\"CIRCLE\" color=<色>"},
]

MARKS = {"A": MARK_A, "B": MARK_B}
CHOSEN = "A"          # 预览看图 + 32 px 实测后的选择


# ---------------------------------------------------------------- DSL 组装
def ramp_for(mode: str) -> list[str]:
    """配色语境：light=浅底/图标本体，dark=深底/海报，black=纯黑版。

    返回 **CSS 颜色值**（hex），不是调色板键名——`color=` 与 `border=` 的
    颜色都必须是 CSS 格式，探针与 400 响应都验证过：
    PARSE_ERROR Attr [border] unsupported CSS color [brand-700]。
    """
    if mode == "black":
        return [BLACK] * 4
    return [PAL[k] for k in (RAMP_LIGHT if mode == "light" else RAMP_DARK)]


def ramp_keys(mode: str) -> list[str]:
    """调色板键名，供文档与 brand-system.json 使用。"""
    if mode == "black":
        return ["pure-black"] * 4
    return list(RAMP_LIGHT if mode == "light" else RAMP_DARK)


def mark_nodes(mark: list[dict], k: float, mode: str, x0: float = 0,
               y0: float = 0) -> list[str]:
    """按同一套几何规则把标志放到 (x0,y0)，整体缩放 k 倍。

    横幅与海报里的标志**不是**把 512 图标当图片贴进去，而是用同一份构件表
    重新生成几何，所以三处应用的尺寸/坐标都是这套参数的函数。
    """
    ramp = ramp_for(mode)
    out = []
    for c in mark:
        x, y, w, h = x0 + c["x"] * k, y0 + c["y"] * k, c["w"] * k, c["h"] * k
        col = ramp[c["tone"]]
        if c["motif"] == "annulus":
            body = (f'<Container width="{w:g}" height="{h:g}" shape="CIRCLE" '
                    f'border="{c["stroke"] * k:g} SOLID {col}" />')
        elif c["shape"] == "CIRCLE":
            body = (f'<Container width="{w:g}" height="{h:g}" shape="CIRCLE" '
                    f'color="{col}" />')
        else:
            body = (f'<Container width="{w:g}" height="{h:g}" '
                    f'borderRadius="{c["radius"] * k:g}" color="{col}" />')
        out.append(f'<Positioned left="{x:g}" top="{y:g}" width="{w:g}" '
                   f'height="{h:g}">{body}</Positioned>')
    return out


def text_node(x, y, w, h, text, size, *, family=CJK, color=PAL["ink"],
              style="", align="CENTER_LEFT", ls=0.0, tag=""):
    st = f' fontStyle="{style}"' if style else ""
    lsa = f' letterSpacing="{ls:g}"' if ls else ""
    n = (f'<Positioned left="{x:g}" top="{y:g}" width="{w:g}" height="{h:g}">'
         f'<Container width="{w:g}" height="{h:g}" alignment="{align}">'
         f'<Text fontFamily="{family}" fontSize="{size:g}" color="{color}"{st}'
         f'{lsa} text="{text}" /></Container></Positioned>')
    return n


def rect_node(x, y, w, h, *, color=None, border=None, radius=0.0):
    """矩形/圆角矩形/描边块，用于分隔线、徽章、色带。"""
    rd = f' borderRadius="{radius:g}"' if radius else ""
    bd = f' border="{border}"' if border else ""
    cd = f' color="{color}"' if color else ""
    return (f'<Positioned left="{x:g}" top="{y:g}" width="{w:g}" height="{h:g}">'
            f'<Container width="{w:g}" height="{h:g}"{rd}{bd}{cd} />'
            f'</Positioned>')


def snapshot(w, h, parts, *, background=None):
    bg = f' background="{background}"' if background else ""
    return ("\n".join([f'<Snapshot type="png"{bg}>',
                       f'<Container width="{w:g}" height="{h:g}">',
                       f'<Stack width="{w:g}" height="{h:g}">'] + parts +
                      ["</Stack>", "</Container>", "</Snapshot>"]) + "\n")


# ---------------------------------------------------------------- 各交付件
def build_symbol(mark_id: str, mode: str) -> tuple[str, float]:
    """512×512 透明图标。不写 background 也不铺白块——透明由画布本身给出。"""
    parts = mark_nodes(MARKS[mark_id], 1.0, mode)
    return snapshot(SYMBOL, SYMBOL, parts), 1.0


def build_banner(mark_id: str = CHOSEN, mode: str = "light") -> tuple[str, dict]:
    """1200×400 浅底品牌横幅：左标志 + 竖分隔线 + 两行字标 + 分隔线 + 标语。"""
    W, H, M = 1200, 400, 96
    k = 240.0 / SYMBOL
    mark = MARKS[mark_id]
    parts: list[str] = [rect_node(0, 0, W, H, color=PAL["paper"])]
    mark_x, mark_y = M, (H - 240) / 2          # 80
    parts += mark_nodes(mark, k, mode, mark_x, mark_y)

    rx = mark_x + 240 + 84                     # 420 竖分隔线
    parts.append(rect_node(rx, mark_y + 52, 2, 136, color=PAL["rule2"]))

    tx = rx + 40                               # 460 文本左缘
    tw = W - M - tx                            # 644 文本可用宽
    # 竖向：标题 72 / 字标 30 / 分隔线 / 标语 28，整体在 400 高内居中
    t_title, t_lat, t_tag = 72, 30, 28
    gap1, gap2 = 20, 36
    total = (lh(t_title) + gap1 + lh(t_lat) + gap2 + 1 + 26 + lh(t_tag))
    y0 = (H - total) / 2
    y_title, y_lat = y0, y0 + lh(t_title) + gap1
    y_rule = y_lat + lh(t_lat) + gap2
    y_tag = y_rule + 1 + 26
    parts.append(text_node(tx, y_title, tw, lh(t_title), W_CJK, t_title,
                           color=PAL["ink"], style="BOLD", ls=6, tag="banner-title"))
    parts.append(text_node(tx, y_lat, tw, lh(t_lat), W_LAT, t_lat,
                           family=MONO, color=PAL["brand-700"],
                           style="BOLD", ls=3, tag="banner-latin"))
    parts.append(rect_node(tx, y_rule, 640, 1, color=PAL["rule"]))
    parts.append(text_node(tx, y_tag, tw, lh(t_tag), TAGLINE, t_tag,
                           color=PAL["muted"], tag="banner-tagline"))
    meta = {"canvas": [W, H], "margin": M, "mark": {"x": mark_x, "y": mark_y,
             "size": 240, "scale": k}, "rule_x": rx, "text_x": tx, "text_w": tw,
            "text": {"title": [tx, y0, tw, lh(t_title), W_CJK],
                     "latin": [tx, y_lat, tw, lh(t_lat), W_LAT],
                     "tagline": [tx, y_tag, tw, lh(t_tag), TAGLINE]}}
    return snapshot(W, H, parts), meta


def build_poster(mark_id: str = CHOSEN) -> tuple[str, dict]:
    """1080×1350 深底发布海报：徽章 + 大标志 + 居中字标 + 标语 + 分隔 + 日期 + URL。

    构图与横幅不同：横幅是横向标志-文字锁定组合，海报是纵向居中英雄式构图，
    标志放到 480 并占据上中部，文字堆叠在下半部；不是横幅的放大。
    """
    W, H, M = 1080, 1350, 84
    k = 480.0 / SYMBOL
    mark = MARKS[mark_id]
    parts: list[str] = [rect_node(0, 0, W, H, color=PAL["ink"])]

    # 海报不放假装饰条。第一版在左下角放了三条呼应母形的阶调色带，实测它们从
    # x=0 起贴住画布左边缘（整体墨迹 bbox 左边为 0），底部只剩 38 px，读起来像
    # 被裁断的残片而不是签名，还把底部留白从 96 压到 38。母形呼应已经在 480 的
    # 大标志本体里完成，重复画一遍反而稀释。底部维持文字块的 96 px 留白。

    # 徽章：最亮阶做实底 + 深墨字，靠明度差获得能量而不引入第二色相
    bw, bh = 264, 56
    bx, by = W - M - bw, M
    parts.append(rect_node(bx, by, bw, bh, color=PAL["brand-200"], radius=bh / 2))
    parts.append(text_node(bx, by, bw, bh, BETA, 22, family=MONO,
                           color=PAL["ink"], style="BOLD", align="CENTER",
                           ls=3, tag="poster-beta"))

    mx = (W - 480) / 2
    my = 196
    parts += mark_nodes(mark, k, "dark", mx, my)

    cx, cw = M, W - 2 * M                      # 居中文字块 84..996
    s_title, s_lat, s_tag = 104, 34, 32
    s_date, s_url = 28, 24
    g1, g2, g3, g4 = 32, 44, 74, 26
    total = (lh(s_title) + g1 + lh(s_lat) + g2 + lh(s_tag) + g3 + 2 + g4
             + lh(s_date) + 22 + lh(s_url))
    band_top = my + 480 + 56                  # 标志下方留 56
    y0 = band_top + ((H - 96 - band_top) - total) / 2
    y_title = y0
    y_lat = y_title + lh(s_title) + g1
    y_tag = y_lat + lh(s_lat) + g2
    y_rule = y_tag + lh(s_tag) + g3
    y_date = y_rule + 2 + g4
    y_url = y_date + lh(s_date) + 22
    parts.append(text_node(cx, y_title, cw, lh(s_title), W_CJK, s_title,
                           color=PAL["paper"], style="BOLD", align="CENTER",
                           ls=8, tag="poster-title"))
    parts.append(text_node(cx, y_lat, cw, lh(s_lat), W_LAT, s_lat,
                           family=MONO, color=PAL["brand-200"],
                           style="BOLD", align="CENTER", ls=5, tag="poster-latin"))
    parts.append(text_node(cx, y_tag, cw, lh(s_tag), TAGLINE, s_tag,
                           color=PAL["brand-100"], align="CENTER",
                           tag="poster-tagline"))
    parts.append(rect_node((W - 160) / 2, y_rule, 160, 2,
                           color=PAL["brand-600"]))
    parts.append(text_node(cx, y_date, cw, lh(s_date), DATE_ONLINE, s_date,
                           family=MONO, color=PAL["brand-400"],
                           style="BOLD", align="CENTER", ls=2, tag="poster-date"))
    parts.append(text_node(cx, y_url, cw, lh(s_url), URL, s_url,
                           family=MONO, color=PAL["faint"], align="CENTER",
                           ls=2, tag="poster-url"))
    meta = {"canvas": [W, H], "margin": M,
            "badge": {"x": bx, "y": by, "w": bw, "h": bh},
            "mark": {"x": mx, "y": my, "size": 480, "scale": k},
            "text": {"beta": [bx, by, bw, bh, BETA],
                     "title": [cx, y_title, cw, lh(s_title), W_CJK],
                     "latin": [cx, y_lat, cw, lh(s_lat), W_LAT],
                     "tagline": [cx, y_tag, cw, lh(s_tag), TAGLINE],
                     "date": [cx, y_date, cw, lh(s_date), DATE_ONLINE],
                     "url": [cx, y_url, cw, lh(s_url), URL],
                     "rule": [(W - 160) / 2, y_rule, 160, 2]}}
    return snapshot(W, H, parts), meta


# ---------------------------------------------------------------- 前置校验
def check() -> list[str]:
    problems: list[str] = []

    for mid, mark in MARKS.items():
        if len(mark) > 6:
            problems.append(f"方向 {mid} 构件 {len(mark)} 个 > 6")
        for c in mark:
            x1, y1 = c["x"] + c["w"], c["y"] + c["h"]
            if c["x"] < MARGIN or c["y"] < MARGIN or x1 > SYMBOL - MARGIN \
                    or y1 > SYMBOL - MARGIN:
                problems.append(f"{c['id']} 越出活动区 32..480："
                                f"[{c['x']},{c['y']},{x1},{y1}]")
            if c["motif"] == "annulus":
                ccx, ccy = c["x"] + c["w"] / 2, c["y"] + c["h"] / 2
                inner_r = c["w"] / 2 - c["stroke"]
                outer_r = c["w"] / 2
                for o in mark:
                    if o is c:
                        continue
                    ocx, ocy = o["x"] + o["w"] / 2, o["y"] + o["h"] / 2
                    if o["shape"] == "CIRCLE" and abs(ocx - ccx) < 1 \
                            and abs(ocy - ccy) < 1:
                        # 同心圆族：比描边环带，内构件必须整段落在孔内、
                        # 外构件必须整段落在环外，比包围盒角点会误判
                        o_out = o["w"] / 2
                        o_in = o["w"] / 2 - o["stroke"] if o["stroke"] else 0
                        if not (o_out <= inner_r - 4 or o_in >= outer_r + 4):
                            problems.append(
                                f"{c['id']} 环带与同心 {o['id']} 相交"
                                f"（本环 {inner_r:g}..{outer_r:g}，"
                                f"对方 {o_in:g}..{o_out:g}）")
                    else:
                        # 矩形族：包围盒四个角都必须落在环孔内
                        worst = max(math.hypot(ox - ccx, oy - ccy)
                                    for ox in (o["x"], o["x"] + o["w"])
                                    for oy in (o["y"], o["y"] + o["h"]))
                        if worst > inner_r - 4:
                            problems.append(
                                f"{c['id']} 环孔与 {o['id']} 重叠风险"
                                f"（内半径 {inner_r:g}，最远角点 {worst:.1f}）")

        # 构件之间必须隔真实透明空隙：黑版里只有有/无覆盖两种状态，
        # 任何两个不透明构件一旦相交就会熔成一团。按包围盒判相交，
        # 允许 0.5 px 的浮点容差。含圆环的对由上面的半径/角点判据处理
        # （圆环内孔是空的，包围盒相交不等于实体相交）。
        for i in range(len(mark)):
            for j in range(i + 1, len(mark)):
                a, b = mark[i], mark[j]
                if a["motif"] == "annulus" or b["motif"] == "annulus":
                    continue
                ox = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
                oy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
                if ox > 0.5 and oy > 0.5:
                    problems.append(f"{a['id']} 与 {b['id']} 包围盒相交 "
                                    f"（x {ox:.1f} / y {oy:.1f} px）")

    # 文案完整性：题面要求的字样必须原样出现在对应 DSL 里。
    # 「叠光 Layerlight」由 CJK 行与 Latin 行两段构成，分别校验。
    dsls, metas = {}, {}
    for name, mk in (("brand-banner", build_banner), ("launch-poster", build_poster)):
        d, m = mk()
        dsls[name], metas[name] = d, m
    need = {"brand-banner": [W_CJK, W_LAT, TAGLINE],
            "launch-poster": [W_CJK, W_LAT, TAGLINE, DATE_ONLINE, BETA, URL]}
    for name, texts in need.items():
        for t in texts:
            if t not in dsls[name]:
                problems.append(f"{name} 缺文案「{t}」")

    # 折行与盒高：墨宽估算超过盒宽 92% 即判会被折行裁切
    for name, m in metas.items():
        cw = m["canvas"][0]
        for k_, box in m["text"].items():
            if len(box) != 5:      # "rule" 一类纯几何条目
                continue
            x, y, w, h, text = box
            size, family, ls = TYPO[name][k_]
            ew = est_w(text, size, family == MONO, ls)
            if ew > w * WRAP_SLACK:
                problems.append(f"{name} {k_}「{text}」墨宽≈{ew:.0f} 超盒宽 "
                                f"{w} 的 {WRAP_SLACK:.0%}（会被折行裁切）")
            if h < lh(size):
                problems.append(f"{name} {k_} 盒高 {h} < 行高 {lh(size)}")
            if x < m["margin"] - 1 or x + w > cw - m["margin"] + 1:
                problems.append(f"{name} {k_} 越出安全边距 {m['margin']}")
    return problems


TYPO = {
    "brand-banner": {"title": (72, CJK, 6), "latin": (30, MONO, 3),
                     "tagline": (28, CJK, 0)},
    "launch-poster": {"title": (104, CJK, 8), "latin": (34, MONO, 5),
                      "tagline": (32, CJK, 0), "date": (28, MONO, 2),
                      "url": (24, MONO, 2), "beta": (22, MONO, 3)},
}


def build(name: str) -> tuple[str, float, dict]:
    """统一入口：返回 (dsl, scale, meta)。"""
    sym = {"symbol-color": ("A", "light"), "symbol-black": ("A", "black"),
           "preview-a": ("A", "light"), "preview-b": ("B", "light")}
    if name in sym:
        mid, mode = sym[name]
        dsl, k = build_symbol(mid, mode)
        return (dsl, k, {"canvas": [SYMBOL, SYMBOL],
                         "mark": {"x": 0, "y": 0, "size": SYMBOL, "scale": k,
                                  "mode": mode}})
    if name == "brand-banner":
        dsl, meta = build_banner()
        return dsl, meta["mark"]["scale"], meta
    dsl, meta = build_poster()
    return dsl, meta["mark"]["scale"], meta


FINAL = {
    "symbol-color": ("透明彩色图标", "render"),
    "symbol-black": ("透明纯黑图标", "render"),
    "brand-banner": ("品牌横幅", "render"),
    "launch-poster": ("发布海报", "render"),
}


def render_all(names: list[str], to_out: bool) -> dict:
    rows = {}
    for name in names:
        dsl, k, meta = build(name)
        r = C.render(TASK, dsl, name, kind="render",
                     purpose=FINAL.get(name, ("预览", "render"))[0])
        rows[name] = {"request_id": r["request_id"], "status": r["status"],
                      "bytes": r["log"].get("response_bytes"),
                      "dsl_path": r["log"]["dsl_path"], "scale": k,
                      "meta": meta}
        print("  %-14s HTTP %-3s %7s B  rid=%s" % (
            name, r["status"], r["log"].get("response_bytes"), r["request_id"]))
        if r["status"] != 200:
            print("    错误：", r["log"].get("error"))
            continue
        if to_out:
            stem = name
            (OUT / (stem + ".png")).write_bytes(r["body"])
            (OUT / (stem + ".snapshot")).write_text(dsl, encoding="utf-8")
            print("    ->", S.rel(OUT / (stem + ".png")),
                  S.rel(OUT / (stem + ".snapshot")))
        else:
            p = TMP / "preview" / (name + ".png")
            p.write_bytes(r["body"])
            print("    ->", S.rel(p))
    return rows


def dump_geometry() -> Path:
    """构件几何清单：brand-system.json 直接消费这份数据。"""
    out = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "run_id": RID,
        "grid": {"unit_px": U, "symbol_canvas": SYMBOL, "live_area_px": LIVE,
                 "clear_space_px": MARGIN},
        "palette": PAL,
        "ramp_light_context": RAMP_LIGHT,
        "ramp_dark_context": RAMP_DARK,
        "chosen_direction": CHOSEN,
        "marks": {mid: [{"id": c["id"], "motif": c["motif"], "role": c["role"],
                         "shape": c["shape"],
                         "geometry_px_512": {"x": c["x"], "y": c["y"],
                                             "w": c["w"], "h": c["h"]},
                         "radius_px": c.get("radius"),
                         "stroke_px": c["stroke"],
                         "tone_index": c["tone"],
                         "negative_space": c["negative_space"],
                         "dsl_locator": c["dsl"]}
                        for c in mark]
                   for mid, mark in MARKS.items()},
        "applications": {
            "symbol": {"canvas_px": [SYMBOL, SYMBOL], "mark_x": 0, "mark_y": 0,
                       "mark_size_px": SYMBOL, "mark_scale": 1.0},
            "brand-banner": build_banner()[1],
            "launch-poster": build_poster()[1],
        },
        "text_runs": {n: build(n)[2]["text"] for n in ("brand-banner",
                                                        "launch-poster")},
    }
    p = TMP / "gen" / "mark-geometry.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    return p


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "checks"
    problems = check()
    print("前置校验问题：%d" % len(problems))
    for p in problems:
        print("  !", p)

    if mode == "checks":
        return 1 if problems else 0
    if problems:
        print("存在校验问题，中止渲染（如需强制：a13_pages.py <mode> force）")
        if len(sys.argv) < 3 or sys.argv[2] != "force":
            return 1

    rows = {}
    if mode == "previews":
        rows = render_all(["preview-a", "preview-b"], to_out=False)
    elif mode == "finals":
        rows = render_all(list(FINAL), to_out=True)
    g = dump_geometry()
    (TMP / "gen" / "render-rows.json").write_text(
        json.dumps({"mode": mode, "rows": rows,
                    "checks_problems": problems}, ensure_ascii=False, indent=2)
        + "\n", encoding="utf-8")
    print("几何清单", S.rel(g))
    bad = [n for n, r in rows.items() if r["status"] != 200]
    if bad:
        print("渲染失败：", ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
