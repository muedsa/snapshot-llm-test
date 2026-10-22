# -*- coding: utf-8 -*-
"""B04 case-11 · 全家福：特辑导读图 (1600x1000, 手机 0.4m).

user_goal: 一张图纵览八行星关键数并知道每件特辑讲什么。
technique: 综合信息带(按日距排序 8 列四数角标) + 导读指针网格(11 件)
           + 声明栏(来源/方法/口径)。
numeric_claims: 32 项角标逐项断言 == b04_data 表值(表值对硬编码期望 8x4，
                再回读展示串)；日距排序严格单调升序(断言)；11 指针与 plan
                cases 一一对应(标题照抄)；八行星=PLANETS 且不含月球/冥王星。
                圆点等大、不作大小编码(声明栏如实注明)。
plan_version: plan-v1 (case-11)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b04_common as C  # noqa: E402
import b04_data as D    # noqa: E402

W, H = 1600, 1000
BG = "#0B1026"
PANEL = "#131A33"
TRACK = "#182043"
TITLE = "#F2F6FF"
SUB = "#B9C6E8"
MUTED = "#93A4CC"
DIM = "#6E7FA8"
INNER = "#FF9E6D"
OUTER = "#7AA2F7"
ACC = "#5AC8FA"
CARD = "#141A35"

PLANETS = ["mercury", "venus", "earth", "mars",
           "jupiter", "saturn", "uranus", "neptune"]
GIANTS = ["jupiter", "saturn", "uranus", "neptune"]

# hardcoded expected table values (SRC-01) — assertion layer independent of
# the dicts themselves
EXP = {
    "mercury": (4879, 57.9, 88.0, 167),
    "venus": (12104, 108.2, 224.7, 464),
    "earth": (12756, 149.6, 365.2, 15),
    "mars": (6792, 228.0, 687.0, -65),
    "jupiter": (142984, 778.5, 4331, -110),
    "saturn": (120536, 1432.0, 10747, -140),
    "uranus": (51118, 2867.0, 30589, -195),
    "neptune": (49528, 4515.0, 59800, -200),
}

# titles verbatim from plan-v1.json cases[]
TITLES = [
    ("case-01", "行星有多大：直径比例尺"),
    ("case-02", "太阳系有多空：对数距离标尺"),
    ("case-03", "开普勒定律的指纹：T²∝a³"),
    ("case-04", "一天有多长：太阳日与自转"),
    ("case-05", "能跳多高：重力与逃逸速度"),
    ("case-06", "哪里最热：温度阶梯"),
    ("case-07", "卫星家族：谁的孩子多"),
    ("case-08", "地月系统：1/4 与 1/81"),
    ("case-09", "冥王星档案卡"),
    ("case-10", "环、磁场与密度分野"),
    ("case-11", "全家福：特辑导读图"),
]

METRICS = [("直径 km", "diam"), ("日距 10⁶km", "dist"),
           ("公转 天", "per"), ("均温 °C", "tmp")]


def numf(v):
    """Display floats like the table: integral -> no decimals, with commas."""
    if float(v) == int(v):
        return "{:,}".format(int(v))
    return "{:,}".format(v)


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"

    # -- assertion layer 1: table values == hardcoded expected (8 x 4 = 32)
    n = 0
    for b, (e_diam, e_dist, e_per, e_tmp) in EXP.items():
        assert D.DIAM_KM[b] == e_diam, b
        assert D.DIST_1E6[b] == e_dist, b
        assert D.ORPPER_D[b] == e_per, b
        assert D.TEMP_C[b] == e_tmp, b
        n += 4
    assert n == 32
    assert "moon" not in PLANETS and "pluto" not in PLANETS
    assert len(PLANETS) == 8

    # -- assertion layer 2: 日距 strictly monotone ascending (plan claim)
    ds = [D.DIST_1E6[b] for b in PLANETS]
    assert all(y > x for x, y in zip(ds, ds[1:])), ds

    # -- assertion layer 3: displayed strings parse back to the table value
    disp = {}
    for b in PLANETS:
        disp[b] = {"diam": numf(D.DIAM_KM[b]), "dist": numf(D.DIST_1E6[b]),
                   "per": numf(D.ORPPER_D[b]), "tmp": str(int(D.TEMP_C[b]))}
        assert float(disp[b]["diam"].replace(",", "")) == D.DIAM_KM[b]
        assert float(disp[b]["dist"].replace(",", "")) == D.DIST_1E6[b]
        assert float(disp[b]["per"].replace(",", "")) == D.ORPPER_D[b]
        assert int(disp[b]["tmp"]) == D.TEMP_C[b]

    # -- 11 pointers verbatim, split on full-width colon
    assert len(TITLES) == 11
    assert TITLES[-1] == ("case-11", "全家福：特辑导读图")
    cells = []
    for cid, t in TITLES:
        parts = t.split("：", 1)
        cells.append((cid, parts[0], parts[1] if len(parts) == 2 else ""))

    els = []
    # ---------------- header ----------------
    els.append(C.text(60, 30, 760, 24, "NASA 数据特辑 · 太阳系数据特辑 11/11",
                      14, MUTED, letter_space=3))
    els.append(C.text(60, 56, 900, 56, "全家福：特辑导读图", 42, TITLE,
                      bold=True))
    els.append(C.text(60, 118, 980, 60,
                      "按日距排序纵览八行星四数，并索引特辑 11 件导读",
                      17, SUB))
    els.append(C.text(1140, 54, 400, 24, "数据 · NASA NSSDCA 行星事实表",
                      14, MUTED, align="RIGHT"))
    els.append(C.text(1140, 80, 400, 24, "SRC-01 表值 · 逐项断言", 13, DIM,
                      align="RIGHT"))

    # ---------------- band: 8 planets sorted by 日距 ----------------
    els.append(C.text(60, 170, 700, 24,
                      "按日距排序的八行星带 · 每行星四数角标（表值 · 断言）",
                      16, SUB))
    els.append(C.box(1120, 164, 420, 30, PANEL, radius=8))
    els.append(C.box(1120, 164, 4, 30, ACC, radius=2))
    els.append(C.text(1132, 170, 396, 20,
                      "日距严格单调升序 57.9 → 4,515 ×10⁶ km（断言）", 12,
                      TITLE, align="CENTER"))

    colw = 1480.0 / 8.0
    for i, b in enumerate(PLANETS):
        cx = 60.0 + colw * (i + 0.5)
        col = OUTER if b in GIANTS else INNER
        els.append(C.circle(cx, 232, 13, col, border=TITLE, border_w=1))
        els.append(C.text(cx - 85, 254, 170, 24, D.ZH[b], 16, TITLE,
                          align="CENTER"))
        els.append(C.box(cx - 85, 286, 170, 160, PANEL, radius=8))
        for j, (lbl, key) in enumerate(METRICS):
            ry = 294.0 + j * 38.0
            els.append(C.text(cx - 77, ry + 6, 85, 16, lbl, 10, DIM))
            els.append(C.text(cx - 10, ry + 2, 87, 20, disp[b][key], 13,
                              TITLE, align="RIGHT"))

    # ---------------- 11 pointer cells ----------------
    els.append(C.text(60, 476, 700, 24, "11 件特辑导读 · 每件一眼", 16, SUB))
    els.append(C.text(1140, 478, 400, 20, "本图为 11/11 终章", 13, DIM,
                      align="RIGHT"))
    cw, gapx, gapy, ch = 359.0, 14.0, 10.0, 74.0
    row3_x = [60.0 + (1480.0 - (3 * cw + 2 * gapx)) / 2.0 + k * (cw + gapx)
              for k in range(3)]
    for idx, (cid, main_t, sub_t) in enumerate(cells):
        if idx < 8:
            x = 60.0 + (idx % 4) * (cw + gapx)
        else:
            x = row3_x[idx - 8]
        y = 506.0 + (idx // 4) * (ch + gapy)
        is_self = cid == "case-11"
        els.append(C.box(x, y, cw, ch, PANEL, radius=8,
                         border=ACC if is_self else None, border_w=1))
        els.append(C.box(x + 14, y + 23, 44, 28, TRACK, radius=6))
        els.append(C.text(x + 14, y + 27, 44, 20, "%02d" % (idx + 1), 14,
                          ACC, align="CENTER", bold=True))
        els.append(C.text(x + 70, y + 12, cw - 84, 24, main_t, 14, TITLE))
        if sub_t:
            els.append(C.text(x + 70, y + 40, cw - 84, 22, sub_t, 11, SUB))

    # ---------------- declaration ----------------
    els.append(C.box(60, 770, 1480, 116, CARD, radius=12))
    els.append(C.box(60, 770, 1480, 4, OUTER, radius=2))
    els.append(C.text(78, 782, 700, 20, "数据来源与方法声明", 13, OUTER))
    decl = [
        "数据：NASA NSSDCA 行星事实表与专题页 SRC-01–SRC-11；不可达页与"
        "抓取失败如实记录在 sources.json（未当成功源使用）。",
        "方法：本图 32 项角标逐项断言 == b04_data.py 表值，日距排序严格单调"
        "升序（断言）；圆点仅作等大标识，不作大小编码（比例见 01 件）。",
        "口径：日距 = 天文平均距离 ×10⁶ km；公转 = 恒星周期（天 · SRC-01 取整值，"
        "木星 4,331 vs 分表 4,332.589）；温度 = 表列表面均值 °C；系列差异（如"
        "密度 1,850/1,854）在各分件内如实注明。",
    ]
    ly = 806.0
    for s in decl:
        els.append(C.text(78, ly, 1444, 22, s, 12, SUB))
        ly += 24

    els.append(C.footnote(
        60, 930, 1480,
        "太阳系数据特辑 11/11 · 全部数值经 b04_data.py 断言校验 · 数据来源 "
        "NASA NSSDCA · 口径与差异见各分件与 sources.json", 12, DIM,
        align="CENTER"))

    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-11-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=BG)
    print("facts badges={} monotone={} titles={} cells={}".format(
        n, [D.DIST_1E6[b] for b in PLANETS], len(TITLES), len(cells)))


if __name__ == "__main__":
    main()
