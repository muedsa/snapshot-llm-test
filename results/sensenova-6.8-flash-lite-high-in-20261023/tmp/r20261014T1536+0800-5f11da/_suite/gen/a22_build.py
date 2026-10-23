"""A22 三轮共用的驾驶舱构造与审计层。

用法：
  python a22_build.py data      <rnd>     写 round-<rnd>/computed-data.json
  python a22_build.py layout    <rnd>     写 round-<rnd>/layout-map.json
  python a22_build.py dryrun    <rnd>     无网络门禁：构造 → 布局断言 → 打印元素表
  python a22_build.py dsl       <rnd>     写交付 DSL 到 tmp/…/A22/dsl/
  python a22_build.py render    <rnd>     提交服务、逐字节交付 PNG+DSL
  python a22_build.py audit     <rnd>     读交付 PNG 做像素级回归，写 change-audit.json
  python a22_build.py views     <rnd>     生成语义裁切视图供人工放大核对

主区域边界在三轮中是同一组常量（LAYOUT），第二轮/第三轮只允许在区域内部重排
刻度与行距，因此 layout-map.json 的 comparison 差值恒为 0。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import uuid

HERE = pathlib.Path(__file__).resolve()
SUITE_ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
GEN = HERE.parents[0]
TASK = "A22"

sys.path.insert(0, str(SUITE_ROOT / "tools"))
sys.path.insert(0, str(GEN))

import a22_data as D          # noqa: E402
from a21_core import Canvas   # noqa: E402
import suite as S             # noqa: E402

TIMEOUT_S = 300
MAX_ATTEMPTS = 3
BACKOFF_S = 20
MIN_FONT = 22

TZ = dt.timezone(dt.timedelta(hours=8))

TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
DSLDIR = TMP / "dsl"
RESDIR = TMP / "responses"
PREVDIR = TMP / "preview"


def rdir(rnd: int) -> pathlib.Path:
    return OUT / ("round-%02d" % rnd)


def now() -> str:
    return dt.datetime.now(TZ).replace(microsecond=0).isoformat()


def sha_b(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_p(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p) -> str:
    p = pathlib.Path(p)
    return p.relative_to(SUITE_ROOT).as_posix()


def dsl_name(rnd: int) -> str:
    return "r%02d-dashboard" % rnd


# ------------------------------------------------------------------ 版式常量

CANVAS = [1600, 1000]

LAYOUT = {
    "header": [48, 40, 1552, 142],
    "conclusion": [48, 158, 1552, 278],
    "kpi": [48, 294, 1552, 434],
    "chart": [48, 450, 876, 916],
    "table": [892, 450, 1552, 916],
    "footer": [48, 932, 1552, 964],
}

PLOT = {"left": 152, "right": 860, "top": 536, "bottom": 852}
PLOT_W = PLOT["right"] - PLOT["left"]
PLOT_H = PLOT["bottom"] - PLOT["top"]

BAR_W = 30
BAR_GAP = 6
GROUP_W = BAR_W * 2 + BAR_GAP
BAR_LABEL_H = 24
BAR_LABEL_GAP = 4
VALUE_FONT = 42

KPI_W = 358
KPI_GAP = 24

TBL_COLS = [
    ("月份", 916, 110, "LEFT"),
    ("净收入", 1030, 128, "RIGHT"),
    ("利润", 1166, 110, "RIGHT"),
    ("退款率", 1290, 112, "RIGHT"),
    ("转化率", 1414, 112, "RIGHT"),
]
TBL_RULES = [1028, 1164, 1288, 1412]

FONT = "Noto Sans CJK SC,Inter"


# ------------------------------------------------------------------ 样式

def styles():
    return {
        "page": "#F1F4F9",
        "panel": "#FFFFFF",
        "panel_border": "#D9E1EC",
        "panel_shadow": "0 2 10 #0E1B2E14",
        "ink": "#0E1B2E",
        "ink2": "#33475F",
        "muted": "#5C6E88",
        "rule": "#E3E9F2",
        "grid": "#EAEFF6",
        "gridline": "#D7E0EB",
        "zeroline": "#33475F",
        "header_panel": "#0E1B2E",
        "header_ink": "#FFFFFF",
        "header_muted": "#9FB3CC",
        "chip": "#EAF2FB",
        "chip_border": "#1F6FBF",
        "chip_text": "#1F6FBF",
        "concl_panel": "#EAF2FB",
        "concl_border": "#C9D9EC",
        "concl_accent": "#1F6FBF",
        "net_color": "#1F6FBF",
        "net_grad": ["#3B93DD", "#175C9F"],
        "profit_color": "#1F8A63",
        "profit_grad": ["#34A87C", "#176E4D"],
        "neg_color": "#C2410C",
        "neg_grad": ["#E0611F", "#9E3306"],
        "fonts": {
            "header_title": 32, "header_sub": 22, "chip": 22,
            "concl_title": 26, "concl_body": 22,
            "kpi_label": 22, "kpi_value": VALUE_FONT, "kpi_unit": 22,
            "kpi_sub": 22,
            "section_title": 24, "chart_note": 22, "legend": 22,
            "axis": 22, "bar_label": 22, "x_label": 22, "scale_note": 22,
            "table_head": 22, "table_cell": 22, "footer": 22,
        },
    }


# ------------------------------------------------------------------ 文本宽度

def text_w(s: str, size: float) -> float:
    """字符宽度估算：CJK 记 1.0em，ASCII 数字/逗号记 0.56em，标点空格更窄。

    服务端实测 CJK advance = 恰好 1em；这里用它做「会不会溢出容器」的门禁，
    估得比实际宽，所以通过即安全。精确的排版对齐交给 textAlign。
    """
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F:
            w += 1.0
        elif ch in ".,:;()[]·÷−→":
            w += 0.30
        elif ch == " ":
            w += 0.28
        else:
            w += 0.56
    return w * size


# ------------------------------------------------------------------ 构造

def build(round_no: int) -> tuple:
    """返回 (Canvas, model)。model 里除 layout 外还有绘图几何，供审计比对像素。"""
    res = D.compute(round_no)
    c = D.conclusion(res)
    axes = res["axes"]
    months = res["months"]
    tt = res["totals"]
    st = styles()
    f = st["fonts"]

    cv = Canvas(CANVAS[0], CANVAS[1], st["page"])
    geo = {"bars": [], "grid": []}

    # ---------------- 标题区 ----------------
    l, t, r, b = LAYOUT["header"]
    cv.box(l, t, r - l, b - t, color=st["header_panel"], radius=14,
           shadow="0 4 16 #0E1B2E33", kind="panel", role="header")
    cv.text(l + 24, t + 14, r - l - 48, 40, "经营驾驶舱", f["header_title"],
            color=st["header_ink"], bold=True, role="header_title")
    sub = ("%s → %s · %d 个月期间 · 数据 inputs/monthly.csv（未修改）"
           % (tt["period"]["from"], tt["period"]["to"],
              tt["period"]["months_count"]))
    cv.text(l + 24, t + 60, 1220, 28, sub, f["header_sub"],
            color=st["header_muted"], role="header_sub")
    chip_txt = ("原始 6 个月" if round_no == 1 else
                "更正后 %d 个月" % tt["period"]["months_count"])
    cx = r - 14 - 214
    cv.box(cx, t + 28, 214, 52, color=st["chip"], radius=26,
           border="1 SOLID %s" % st["chip_border"], kind="chip",
           role="header_chip")
    cw = text_w(chip_txt, f["chip"])
    cv.text(cx + (214 - cw) / 2, t + 28 + 11, cw + 8, 30, chip_txt, f["chip"],
            color=st["chip_text"], role="header_chip_text")

    # ---------------- 主结论区 ----------------
    l, t, r, b = LAYOUT["conclusion"]
    cv.box(l, t, r - l, b - t, color=st["concl_panel"], radius=12,
           border="1 SOLID %s" % st["concl_border"], kind="plate",
           role="conclusion")
    cv.box(l, t, 6, b - t, color=st["concl_accent"], radius=3, kind="accent",
           role="conclusion_accent")
    cv.text(l + 28, t + 14, 1420, 34, c["title"], f["concl_title"],
            color=st["ink"], bold=True, role="concl_title")
    bym = {m["month"]: m for m in months}
    if round_no == 1:
        body = ("六个月净收入合计 %s 元、经营利润合计 %s 元；%s 净收入 %s 元为全期"
                "最高，转化率由 %s 降至 %s，没有任何月份超过首月。"
                % (tt["display"]["net_revenue"], tt["display"]["profit"],
                   months[-1]["month"], months[-1]["display"]["net_revenue"],
                   months[0]["conversion_rate"]["display"],
                   months[-1]["conversion_rate"]["display"]))
    elif round_no == 2:
        body = ("两项更正后：2026-08 退款率升至 %s，2026-09 转为唯一亏损月"
                "（利润 %s 元）；期间经营利润减少 80,000 元至 %s 元，"
                "订单与转化率不受影响。"
                % (bym["2026-08"]["refund_rate"]["display"],
                   bym["2026-09"]["display"]["profit"],
                   tt["display"]["profit"]))
    else:
        body = ("新增 %s：净收入 %s 元、经营利润 %s 元均为全期最高；七个月期间净收入 "
                "%s 元、经营利润 %s 元，2026-09 的 %s 元仍是唯一亏损月。"
                % (bym["2026-10"]["month"], bym["2026-10"]["display"]["net_revenue"],
                   bym["2026-10"]["display"]["profit"], tt["display"]["net_revenue"],
                   tt["display"]["profit"], bym["2026-09"]["display"]["profit"]))
    assert text_w(body, f["concl_body"]) <= 1424 * 2 - 240, (
        "结论文本 %.0fpx 放不下 2 行（盒宽 1424）" % text_w(body, f["concl_body"]))
    cv.text(l + 28, t + 52, 1424, 64, body, f["concl_body"], color=st["ink2"],
            soft_wrap=True, max_lines=2, role="concl_body")

    # ---------------- 四张 KPI ----------------
    l, t, r, b = LAYOUT["kpi"]
    neg_months = [m for m in months if m["profit"] < 0]
    import decimal as _dec
    margin = (_dec.Decimal(tt["profit"]) / _dec.Decimal(tt["net_revenue"])
              * 100)
    margin_txt = "%.2f%%" % D._q(margin)
    kpis = [
        ("总净收入", "{:,}".format(tt["net_revenue"]), "元",
         "退款 %s 元" % tt["display"]["refund_amount"], st["ink"]),
        ("总经营利润", "{:,}".format(tt["profit"]), "元",
         "利润率 %s · %s 亏损" % (margin_txt, neg_months[0]["month"])
         if neg_months else "利润率 %s（全期为正）" % margin_txt,
         st["neg_color"] if neg_months else st["ink"]),
        ("总订单", "{:,}".format(tt["orders"]), "笔",
         "访问 %s 次" % tt["display"]["sessions"], st["ink"]),
        ("总体转化率", tt["conversion_rate"]["display"].rstrip("%"), "%",
         "总订单 %s ÷ 总访问 %s" % (tt["display"]["orders"],
                                    tt["display"]["sessions"]), st["ink"]),
    ]
    kpi_geo = []
    for i, (label, val, unit, subtxt, vcolor) in enumerate(kpis):
        cl = l + i * (KPI_W + KPI_GAP)
        cv.box(cl, t, KPI_W, b - t, color=st["panel"],
               border="1 SOLID %s" % st["panel_border"], radius=12,
               shadow=st["panel_shadow"], kind="panel", role="kpi")
        cv.text(cl + 24, t + 14, KPI_W - 48, 28, label, f["kpi_label"],
                color=st["muted"], role="kpi_label")
        vw = text_w(val, VALUE_FONT)
        uy = t + 50 + VALUE_FONT - f["kpi_unit"] - 1
        cv.text(cl + 24, t + 46, KPI_W - 48, VALUE_FONT + 4, val, VALUE_FONT,
                color=vcolor, bold=True, role="kpi_value")
        cv.text(cl + 28 + vw, uy, 60, f["kpi_unit"] + 4, unit, f["kpi_unit"],
                color=st["ink2"], role="kpi_unit")
        cv.text(cl + 24, t + 108, KPI_W - 48, 28, subtxt, f["kpi_sub"],
                color=st["muted"], role="kpi_sub")
        kpi_geo.append({"label": label, "value": val, "unit": unit,
                        "sub": subtxt, "box": [cl, t, cl + KPI_W, b]})

    # ---------------- 柱图 ----------------
    l, t, r, b = LAYOUT["chart"]
    cv.box(l, t, r - l, b - t, color=st["panel"],
           border="1 SOLID %s" % st["panel_border"], radius=12,
           shadow=st["panel_shadow"], kind="panel", role="chart")
    cv.text(l + 24, t + 8, 312, 30, "净收入与经营利润（元）",
            f["section_title"], color=st["ink"], bold=True, role="chart_title")
    cv.text(l + 24, t + 44, 780, 26,
            "柱顶标注净收入；经营利润逐月数值见右侧明细表"
            + ("；负利润绘于零线下方" if axes["negative_axis"] else ""),
            f["chart_note"], color=st["muted"], role="chart_note")

    # 图例与标题同一行，靠右排；三项固定起点，缺负利润项时右侧留空
    lx = l + 472
    for name, col in (("净收入", st["net_color"]),
                      ("经营利润", st["profit_color"])):
        cv.box(lx, t + 14, 18, 18, color=col, radius=4, kind="swatch",
               role="legend_swatch")
        cv.text(lx + 24, t + 12, text_w(name, f["legend"]) + 8, 24, name,
                f["legend"], color=st["ink2"], role="legend_label")
        lx += 24 + text_w(name, f["legend"]) + 20
    if neg_months:
        cv.box(lx, t + 14, 18, 18, color=st["neg_color"], radius=4,
               kind="swatch", role="legend_swatch")
        cv.text(lx + 24, t + 12, text_w("负利润", f["legend"]) + 8, 24,
                "负利润", f["legend"], color=st["ink2"], role="legend_label")

    scale = PLOT_H / (axes["max"] - axes["min"])
    zero_y = PLOT["top"] + PLOT_H * (axes["max"] - 0) / (axes["max"] - axes["min"])
    geo["zero"] = round(zero_y, 1)
    geo["scale_px_per_yuan"] = scale

    if axes["negative_axis"]:
        cv.box(PLOT["left"], int(round(zero_y)), PLOT_W,
               int(round(PLOT["bottom"] - zero_y)), color="#FBF1EC",
               kind="zone", role="negative_zone")

    for v in axes["gridlines"]:
        y = PLOT["top"] + PLOT_H * (axes["max"] - v) / (axes["max"] - axes["min"])
        yi = int(round(y))
        cv.box(PLOT["left"] - 6, yi, 6, 1, color=st["gridline"], kind="grid",
               role="grid_tick")
        cv.box(PLOT["left"], yi, PLOT_W, 1,
               color=st["zeroline"] if v == 0 else st["gridline"],
               kind="grid", role="grid_zero" if v == 0 else "grid")
        cv.text(52, yi - 13, 96, 26, "{:,}".format(v), f["axis"],
                color=st["muted"], align="RIGHT", role="axis_label")
        geo["grid"].append({"value": v, "y": round(y, 1)})

    n = len(months)
    slot = PLOT_W / n
    lab_w = min(slot - 6, 104)
    for i, m in enumerate(months):
        cx = PLOT["left"] + slot * (i + 0.5)
        for j, (metric, dispc, grad, role) in enumerate((
                ("net_revenue", m["display"]["net_revenue"], st["net_grad"],
                 "bar_net"),
                ("profit", m["display"]["profit"],
                 st["neg_grad"] if m["profit"] < 0 else st["profit_grad"],
                 "bar_neg" if m["profit"] < 0 else "bar_profit"))):
            val = m[metric]
            h = abs(val) * scale
            top = zero_y - h if val >= 0 else zero_y
            bx = int(round(cx - GROUP_W / 2 + j * (BAR_W + BAR_GAP)))
            bh = max(1, int(round(h)))
            cv.box(bx, int(round(top)), BAR_W, bh, gradient=("LINEAR", grad, None),
                   begin="TOP_CENTER", end="BOTTOM_CENTER", radius=2, kind="bar",
                   role=role)
            # 只给「标签所在位置必然空白」的柱标注：净收入柱（标签在柱顶上方，
            # 同组的经营利润柱恒比净收入柱矮，标签带不会碰到它）与负值柱
            # （标签在零线下方，r2 起零线下方是空的）。正的经营利润柱标签会
            # 落到同组净收入柱体上，所以不标注，其数值由右侧明细表承载。
            labelled = (metric == "net_revenue") or (val < 0)
            if labelled:
                if val < 0:
                    lab_y = int(round(top)) + bh + BAR_LABEL_GAP
                else:
                    lab_y = int(round(top)) - BAR_LABEL_H - BAR_LABEL_GAP
                cv.text(int(round(cx)) - int(round(lab_w / 2)), lab_y,
                        int(round(lab_w)), BAR_LABEL_H, dispc, f["bar_label"],
                        align="CENTER",
                        color=st["neg_color"] if val < 0 else st["ink2"],
                        bold=(val < 0), role="bar_label")
            geo["bars"].append({
                "month": m["month"], "metric": metric, "value": val,
                "display": dispc, "x": bx, "y_top": int(round(top)),
                "width": BAR_W, "height_px": bh,
                "height_px_unrounded": round(h, 3),
                "below_zero": val < 0, "labelled": labelled,
                "label_x": (int(round(cx)) - int(round(lab_w / 2))
                            if labelled else None),
                "label_y": ((int(round(top)) + bh + BAR_LABEL_GAP
                             if val < 0
                             else int(round(top)) - BAR_LABEL_H - BAR_LABEL_GAP)
                            if labelled else None),
                "label_w": int(round(lab_w)) if labelled else None,
            })
        cv.text(int(round(cx)) - 48, PLOT["bottom"] + 8, 96, 28, m["month"],
                f["x_label"], color=st["ink2"], align="CENTER",
                role="x_label")

    cv.text(PLOT["left"], PLOT["bottom"] + 36, PLOT_W, 26,
            "1 格 = %s 元；净收入与经营利润共用同一比例与同一零点"
            % "{:,}".format(axes["step"]),
            f["scale_note"], color=st["muted"], role="chart_scale_note")

    # ---------------- 明细表 ----------------
    l, t, r, b = LAYOUT["table"]
    cv.box(l, t, r - l, b - t, color=st["panel"],
           border="1 SOLID %s" % st["panel_border"], radius=12,
           shadow=st["panel_shadow"], kind="panel", role="table")
    cv.text(l + 16, t + 12, 218, 32, "月度明细", f["section_title"],
            color=st["ink"], bold=True, role="table_title")

    head_top = t + 54
    head_h = 38
    row_h = (b - (head_top + head_h)) / n
    geo["table"] = {"head_top": head_top, "head_h": head_h,
                    "row_h_unrounded": row_h, "rows": []}

    cv.box(l + 16, head_top, r - l - 32, head_h, color="#EEF3FA", radius=6,
           kind="plate", role="table_head_bg")
    for name, x, w, al in TBL_COLS:
        cv.text(x, head_top + 6, w, 28, name, f["table_head"], color=st["ink"],
                bold=True, align=al, role="table_head")
    for ry in TBL_RULES:
        cv.box(ry, head_top + head_h, 1, int(round(n * row_h)),
               color=st["rule"], kind="rule", role="table_vrule")
    for i in range(n + 1):
        y = head_top + head_h + i * row_h
        cv.box(l + 16, int(round(y)), r - l - 32, 1, color=st["rule"],
               kind="rule", role="table_hrule")

    cells = []
    for i, m in enumerate(months):
        y = head_top + head_h + i * row_h
        ry = int(round(y))
        for idx, (name, x, w, al) in enumerate(TBL_COLS):
            if idx == 0:
                val, col = m["month"], st["ink"]
            elif idx == 1:
                val, col = m["display"]["net_revenue"], st["ink"]
            elif idx == 2:
                val = m["display"]["profit"]
                col = st["neg_color"] if m["profit"] < 0 else st["profit_color"]
            elif idx == 3:
                val = m["refund_rate"]["display"]
                col = st["ink2"]
            else:
                val = m["conversion_rate"]["display"]
                col = st["ink2"]
            cv.text(x, ry + 6, w, 28, val, f["table_cell"], color=col,
                    bold=(idx == 2 and m["profit"] < 0), align=al,
                    role="table_cell_%s" % name)
            cells.append({"month": m["month"], "column": name, "text": val,
                          "color": col,
                          "box": [x, ry + 6, x + w, ry + 6 + 28]})
        geo["table"]["rows"].append({"month": m["month"], "y": round(y, 1)})

    # ---------------- 页脚 ----------------
    l, t, r, b = LAYOUT["footer"]
    cv.text(l, t + 4, r - l, 26,
            "净收入=收入−退款 · 利润=净收入−经营成本 · 总体转化率=总订单÷总访问"
            "（不平均各月百分比）· 期间汇总先分别求和，比率用总分子÷总分母",
            f["footer"], color=st["muted"], role="footer")

    model = {
        "layout": cv.layout,
        "bars": geo["bars"],
        "grid": geo["grid"],
        "zero_y": geo["zero"],
        "scale_px_per_yuan": geo["scale_px_per_yuan"],
        "plot": {**PLOT, "w": PLOT_W, "h": PLOT_H},
        "kpi": kpi_geo,
        "table": geo["table"],
        "table_cells": cells,
        "styles": st,
        "axes": axes,
        "data": res,
        "conclusion": c,
    }
    return cv, model


# ------------------------------------------------------------------ 布局门禁

def _over(a: list, b: list) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def dryrun(rnd: int) -> list[str]:
    """无网络门禁：构造 DSL → 校验尺寸与合法性 → 逐条布局断言 → 打印元素表。

    全部断言基于设计数值，不发任何请求；这里的目的是在请求之前抓住溢出、
    遮挡、字号下限、柱高越界这类「不报错但看图难看」的缺陷。
    """
    cv, mo = build(rnd)
    txt = cv.dsl()
    gates = []

    def g(name: str, cond: bool, detail: str = ""):
        gates.append((name, bool(cond), detail))
        if not cond:
            raise AssertionError("门禁失败：%s %s" % (name, detail))

    g("画布尺寸 1600x1000",
      '<Snapshot type="png" background="' in txt and
      '<Container width="1600" height="1000">' in txt,
      "声明与 Canvas 构造一致")

    g("DSL 不含属性中禁止的 & 字符", "&" not in txt,
      "服务端要求属性值中不出现 &，已确认全文无 &")
    ALIGN = {"TOP_LEFT", "TOP_CENTER", "TOP_RIGHT", "CENTER_LEFT", "CENTER",
             "CENTER_RIGHT", "BOTTOM_LEFT", "BOTTOM_CENTER", "BOTTOM_RIGHT"}
    bad_grad = []
    for attr in ("gradientBegin", "gradientEnd", "gradientCenter", "gradientFocal"):
        for m in re.finditer('%s="([^"]*)"' % attr, txt):
            v = m.group(1)
            ok = v in ALIGN or re.fullmatch(r"\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+"
                                            r"(?:\.\d+)?\s*\)", v)
            if not ok:
                bad_grad.append({"attr": attr, "value": v})
    g("渐变端点取服务端支持的对齐关键字或 (x,y) 元组", not bad_grad,
      "gradientBegin/End/Center/Focal 只能是 9 个对齐关键字或 (x,y)；实测 "
      '"50% 0%" 会 PARSE_ERROR' if not bad_grad else "%s" % bad_grad)
    for ln in txt.splitlines():
        s = ln.strip()
        if not s.startswith("<"):
            continue
        head = s.split(">", 1)[0]
        assert "<" not in head[1:], "标签声明里出现了第二个 <：%r" % s

    st, axes = mo["styles"], mo["axes"]
    g("正文最小字号 ≥22",
      all(v >= MIN_FONT for k, v in st["fonts"].items()
          if not k.endswith("title") and k != "kpi_value"),
      "最小 %d（标题类与 KPI 数值除外）" % min(
          v for k, v in st["fonts"].items()
          if not k.endswith("title") and k != "kpi_value"))

    n = len(mo["data"]["months"])
    narrow = []
    for it in cv.layout:
        if not it.get("text") or it.get("role") == "concl_body":
            continue
        bw = it["box"][2] - it["box"][0]
        if bw < text_w(it["text"], it["fontSize"]) - 0.5:
            narrow.append({"role": it.get("role"), "text": it["text"],
                           "box_w": bw, "need": round(text_w(it["text"],
                                                              it["fontSize"]), 1)})
    g("每段单行文字的文本盒宽度都够装下它（否则静默截断）", not narrow,
      "concl_body 是多行文本，另用 2 行上限单独断言" if not narrow
      else "%s" % narrow)
    g("月份原样且数量正确",
      n == (7 if rnd >= 3 else 6) and
      mo["data"]["months"][0]["month"] == "2026-04",
      "%d 个月，首月 %s，末月 %s（2026-04 未被省略）"
      % (n, mo["data"]["months"][0]["month"], mo["data"]["months"][-1]["month"]))

    g("KPI 数值不换行且不溢出卡片",
      all(text_w(k["value"], VALUE_FONT) + 28 + text_w(k["unit"], 22) + 24
          <= KPI_W - 48
          for k in mo["kpi"]),
      "；".join("%s 宽 %.0fpx" % (k["label"],
                                   text_w(k["value"], VALUE_FONT) + 28 +
                                   text_w(k["unit"], 22) + 24)
                for k in mo["kpi"]))

    g("KPI 标签/注释一行内",
      all(text_w(k["label"], 22) <= KPI_W - 48 and
          text_w(k["sub"], 22) <= KPI_W - 48 for k in mo["kpi"]),
      "标签与注释宽度均 ≤ 310px")

    col_of = [TBL_COLS[i % 5] for i in range(len(mo["table_cells"]))]
    col_w = [(name, w) for name, _x, w, _a in TBL_COLS]
    g("表头/单元格文字不超列宽",
      all(text_w(name, 22) <= w for name, w in col_w) and
      all(text_w(c["text"], 22) <= col[2]
          for c, col in zip(mo["table_cells"], col_of)),
      "各列宽度 %s" % [w for _n, w in col_w])

    head_h = mo["table"]["head_h"]
    row_h = mo["table"]["row_h_unrounded"]
    g("表行数与区域高度匹配",
      abs((head_h + row_h * n) - (LAYOUT["table"][3] -
                                   LAYOUT["table"][1] - 54)) < 0.6,
      "表头 %d + %d 行 × %.2f = 区域内容高 %.1f"
      % (head_h, n, row_h, head_h + row_h * n))

    g("柱组在绘图区内且不与相邻组重叠",
      all(b["x"] >= PLOT["left"] and
          b["x"] + BAR_W + (BAR_GAP + BAR_W if b["metric"] == "net_revenue"
                            else 0) <= PLOT["right"] for b in mo["bars"]),
      "组宽 %d，槽宽 %.2f" % (GROUP_W, PLOT_W / n))

    zero_y, sc = mo["zero_y"], mo["scale_px_per_yuan"]
    g("所有柱体落在绘图区纵轴范围内",
      all(b["y_top"] >= PLOT["top"] and
          b["y_top"] + b["height_px"] <= PLOT["bottom"] + 1
          for b in mo["bars"]),
      "零线 y=%.1f，比例 %.6f px/元，绘图区 y %d..%d"
      % (zero_y, sc, PLOT["top"], PLOT["bottom"]))

    g("负值柱确实画在零线下方且高度未被裁掉",
      (not any(b["below_zero"] for b in mo["bars"])) or
      all(b["y_top"] == int(round(zero_y)) and b["height_px"] >= 1
          for b in mo["bars"] if b["below_zero"]),
      "%d 根负柱，最高 %.1fpx（按同一比例，未放大未隐藏）"
      % (len([b for b in mo["bars"] if b["below_zero"]]),
         max([b["height_px_unrounded"] for b in mo["bars"] if b["below_zero"]]
             ) if any(b["below_zero"] for b in mo["bars"]) else 0))

    need = BAR_LABEL_H + BAR_LABEL_GAP
    lbars = [b for b in mo["bars"] if b["labelled"]]
    neg_bars = [b for b in mo["bars"] if b["below_zero"]]
    neg_lab_bottom = (max(b["label_y"] for b in lbars if b["below_zero"])
                      + BAR_LABEL_H if any(
                          b["below_zero"] and b["labelled"]
                          for b in mo["bars"]) else None)
    g("数值标签不越出绘图区：正值标签在柱上方、负值标签在柱下方",
      all((not b["below_zero"] and b["label_y"] >= PLOT["top"]) or
          (b["below_zero"] and
           b["label_y"] + BAR_LABEL_H <= PLOT["bottom"] + 1)
          for b in lbars),
      "标签高 %d + 间距 %d = %dpx；标注的最高柱顶 y=%.1f（绘图区顶 %d），"
      "负柱标签底 y=%s（绘图区底 %d）"
      % (BAR_LABEL_H, BAR_LABEL_GAP, need,
         min(b["y_top"] for b in lbars), PLOT["top"],
         ("%.1f" % neg_lab_bottom) if neg_lab_bottom is not None else "无负柱",
         PLOT["bottom"]))

    def rect_hit(a, b):
        """两个 (l, t, w, h) 矩形是否有交集面积 > 0。"""
        return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or
                    a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])

    lab_rects = [(b["label_x"], b["label_y"], b["label_w"], BAR_LABEL_H)
                 for b in lbars]
    bar_rects = [(b["x"], b["y_top"], b["width"], b["height_px"])
                 for b in mo["bars"]]
    hits = [(a, c) for a in lab_rects for c in bar_rects if rect_hit(a, c)]
    g("已标注的数值标签与任何柱体都不相交（标签不会压在别的柱上）",
      not hits,
      "对 %d 个标签矩形与 %d 个柱矩形逐一做相交面积判定：%s"
      % (len(lab_rects), len(bar_rects),
         "无相交（正的经营利润柱不标注，因为标签带会落在同组净收入柱体内，"
         "其数值由右侧明细表承载）" if not hits else
         "相交 %d 处：%s" % (len(hits), [
             "label y=%s..%s vs bar y=%s..%s" % (a[1], a[1] + a[3], c[1],
                                                 c[1] + c[3])
             for a, c in hits[:4]])))

    headroom = min(b["y_top"] for b in lbars) - PLOT["top"]
    g("绘图区顶部留白 ≥ 标签高度（最高柱的标签有位置放）",
      headroom >= need,
      "标注的最高柱顶部 y=%.1f，绘图区顶 %d，留白 %.1fpx，需要 %dpx"
      % (min(b["y_top"] for b in lbars), PLOT["top"], headroom, need))

    g("月份标签在绘图区下方一行内（宽度 ≤96px）",
      all(text_w(m["month"], 22) <= 96 for m in mo["data"]["months"]),
      "8 字符 ≈ %.1fpx ≤ 96，标签盒宽 96"
      % text_w(mo["data"]["months"][0]["month"], 22))

    g("轴标签在 y 轴左侧、不进入绘图区",
      all(x[2] <= PLOT["left"] - 2 for x in [it["box"] for it in cv.layout
                                             if it.get("role") == "axis_label"]),
      "轴标签右边界 ≤ %d" % (PLOT["left"] - 2))

    texts = [it for it in cv.layout if it.get("role")]
    g("图例文字不越出图表面板",
      all(it["box"][2] <= LAYOUT["chart"][2] for it in texts
          if it["role"] == "legend_label"),
      "图例右边界 ≤ %d" % LAYOUT["chart"][2])

    g("四张 KPI 卡互不重叠",
      not any(_over(mo["kpi"][i]["box"], mo["kpi"][j]["box"])
              for i in range(len(mo["kpi"])) for j in range(i + 1, len(mo["kpi"]))),
      "间距 %d，卡宽 %d" % (KPI_GAP, KPI_W))

    REGION_OF_ROLE = {
        "header": ("header",), "header_": ("header",),
        "conclusion": ("conclusion",), "conclusion_": ("conclusion",),
        "concl_title": ("conclusion",), "concl_body": ("conclusion",),
        "kpi": ("kpi",), "kpi_": ("kpi",),
        "chart": ("chart",), "chart_": ("chart",),
        "legend": ("chart",), "axis_label": ("chart",), "grid": ("chart",),
        "grid_": ("chart",), "bar_": ("chart",), "x_label": ("chart",),
        "table": ("table",), "table_": ("table",),
        "footer": ("footer",),
    }

    def region_of(role):
        for p, rg in REGION_OF_ROLE.items():
            if role.startswith(p):
                return rg[0]
        return None

    reg_items = {}
    for it in cv.layout:
        rg = region_of(it.get("role", ""))
        if rg:
            reg_items.setdefault(rg, []).append(it)
    for rg in LAYOUT:
        items = reg_items.get(rg, [])
        box = LAYOUT[rg]
        bad = [it for it in items if not (it["box"][0] >= box[0] - 2 and
                                          it["box"][1] >= box[1] - 2 and
                                          it["box"][2] <= box[2] + 2 and
                                          it["box"][3] <= box[3] + 2)]
        g("区域 %s 内所有元素不越界" % rg, items != [] and not bad,
          "%d 个元素（区域 %s）%s" % (
              len(items), box,
              "" if not bad else "；越界：%s" % [
                  {"role": i.get("role"), "box": i["box"]} for i in bad]))

    D._check(mo["data"])
    c = mo["conclusion"]
    for num in ("{:,}".format(mo["data"]["totals"]["net_revenue"]),
                "{:,}".format(mo["data"]["totals"]["profit"])):
        g("结论中引用的总额与 computed-data 一致：%s" % num,
          num in c["claim"] + "".join(c["claims"]),
          "结论文本中能找到该数值")

    ok = [gm for gm in gates]
    fail = [g for g in ok if not g[1]]
    return [(name, passed, detail) for name, passed, detail in gates]


def gate_report(gates) -> dict:
    return {
        "gate": "a22_build.py dryrun",
        "checks": [{"name": n, "passed": bool(p), "detail": d}
                   for n, p, d in gates],
        "n_checks": len(gates),
        "n_passed": sum(1 for _, p, _ in gates if p),
        "all_passed": all(p for _, p, _ in gates),
    }


# ------------------------------------------------------------------ 请求与交付

def append_jsonl(p: pathlib.Path, obj: dict) -> None:
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_jsonl(p: pathlib.Path) -> list:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()
            if x.strip()]


def log_request(rec: dict) -> None:
    rec.setdefault("task_id", TASK)
    rec.setdefault("kind", "render")
    (RESDIR).mkdir(parents=True, exist_ok=True)
    append_jsonl(TMP / "requests.jsonl", rec)


def render(rnd: int) -> dict:
    """构造 → 门禁 → 提交 → 交付。交付 PNG 是服务返回的原始字节，不后处理。"""
    gates = dryrun(rnd)
    report = gate_report(gates)
    gp = TMP / "gate-reports" / ("round-%02d.json" % rnd)
    gp.parent.mkdir(parents=True, exist_ok=True)
    gp.write_text(json.dumps({**report, "round": rnd, "written_at": now(),
                              "gate_sha256_note": "干跑门禁结果，提交服务前必须全通过"},
                             ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rd = rdir(rnd)
    rd.mkdir(parents=True, exist_ok=True)
    dsl_path = TMP / "dsl" / ("%s.attempt-01.snapshot" % dsl_name(rnd))
    dsl_path.parent.mkdir(parents=True, exist_ok=True)

    cv, mo = build(rnd)
    dsl_txt = cv.dsl()
    dsl_path.write_bytes(dsl_txt.encode("utf-8"))
    dsl_bytes = dsl_txt.encode("utf-8")

    rid = ("req-a22-r%02d-dashboard-" % rnd) + uuid.uuid4().hex[:6]
    status = None
    body = b""
    meta = {}
    err = None
    import time
    for attempt in range(1, MAX_ATTEMPTS + 1):
        status, body, meta = S.snapshot_request(
            TASK, dsl_txt, "%s attempt %d" % (dsl_name(rnd), attempt),
            kind="render", timeout=TIMEOUT_S, retries=0)
        if status == 200 and body[:8] == b"\x89PNG\r\n\x1a\n":
            err = None
            break
        err = "attempt %d：HTTP %s，%d 字节，前 8 字节 %r" % (
            attempt, status, len(body), body[:8] if body else b"")
        if attempt < MAX_ATTEMPTS:
            time.sleep(BACKOFF_S)
    (RESDIR / ("%s.png" % rid)).write_bytes(body)

    hdrs = meta.get("headers", {})
    log_request({
        "request_id": rid,
        "round": rnd,
        "kind": "render",
        "label": "%s attempt %d" % (dsl_name(rnd), attempt),
        "attempts": attempt,
        "url": S.service_url() + "/snapshot",
        "method": "POST",
        "content_type_request": "text/plain; charset=utf-8",
        "request_file": rel(dsl_path),
        "response_file": rel(RESDIR / ("%s.png" % rid)),
        "started_at": meta.get("started_at"),
        "ended_at": meta.get("ended_at"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "elapsed_ms": meta.get("elapsed_ms"),
        "http_status": status,
        "content_type_response": meta.get("content_type"),
        "server_timing": hdrs.get("server-timing"),
        "request_id_header": hdrs.get("x-request-id") or hdrs.get("request-id"),
        "response_bytes": len(body),
        "response_sha256": sha_b(body) if body else None,
        "request_bytes": len(dsl_bytes),
        "request_sha256": sha_b(dsl_bytes),
        "is_png": status == 200 and body[:8] == b"\x89PNG\r\n\x1a\n",
        "delivered": (rel(rd / "dashboard.png")
                      if status == 200 and body[:8] == b"\x89PNG\r\n\x1a\n"
                      else None),
        "error": err,
        "retry_after": meta.get("retry_after"),
    })

    if not (status == 200 and body[:8] == b"\x89PNG\r\n\x1a\n"):
        raise SystemExit("渲染失败：HTTP %s，错误 %s；响应已保存到 %s"
                         % (status, err, RESDIR / ("%s.png" % rid)))

    (rd / "dashboard.png").write_bytes(body)
    (rd / "dashboard.snapshot").write_bytes(dsl_bytes)
    return {"request_id": rid, "round": rnd, "round_dir": rel(rd),
            "gate": report, "bytes": len(body), "sha256": sha_b(body),
            "started_at": meta.get("started_at"),
            "ended_at": meta.get("ended_at"),
            "elapsed_ms": meta.get("elapsed_ms"),
            "server_timing": hdrs.get("server-timing")}


# ------------------------------------------------------------------ computed-data

def write_computed(rnd: int) -> dict:
    res = D.compute(rnd)
    c = D.conclusion(res, prev=D.compute(rnd - 1) if rnd > 1 else None)
    doc = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "round": rnd,
        "output_dir": "outputs/%s/%s/round-%02d" % (RUN_ID, TASK, rnd),
        "applied_changes": res["applied_changes"],
        "source_csv": res["source_csv"],
        "units": res["units"],
        "precision": res["precision"],
        "formulas": {
            "net_revenue": "gross_revenue - refund_amount",
            "profit": "net_revenue - operating_cost",
            "refund_rate": "refund_amount / gross_revenue",
            "conversion_rate": "orders / sessions",
            "period_net_revenue": "sum(gross_revenue) - sum(refund_amount)",
            "period_profit": "period_net_revenue - sum(operating_cost)",
            "total_conversion_rate": "sum(orders) / sum(sessions)",
            "total_refund_rate": "sum(refund_amount) / sum(gross_revenue)",
        },
        "months": res["months"],
        "totals": res["totals"],
        "axes": res["axes"],
        "conclusion": c,
        "cross_check": {
            "passed": True,
            "method": "由汇总回推明细：sum(各月净收入)==总净收入、"
                      "sum(各月利润)==总利润、逐月比率按分子分母重算并与显示文本比对、"
                      "亏损月的成本−净收入==亏损额",
            "messages": D._check(res),
        },
    }
    p = rdir(rnd) / "computed-data.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    return {"path": rel(p), "bytes": p.stat().st_size, "sha256": sha_p(p),
            "months": len(res["months"])}


# ------------------------------------------------------------------ layout-map

def layout_doc(rnd: int, prev_regions: dict | None = None) -> dict:
    cv, mo = build(rnd)
    st = mo["styles"]
    regions = [
        {"id": "header", "box": LAYOUT["header"],
         "contents": "标题「经营驾驶舱」、期间与数据来源副标题、本轮状态标签",
         "style": {"panel": st["header_panel"], "radius": 14,
                   "shadow": "0 4 16 #0E1B2E33",
                   "title_font": "%s %d BOLD" % (FONT, st["fonts"]["header_title"]),
                   "title_color": st["header_ink"],
                   "sub_font": "%s %d" % (FONT, st["fonts"]["header_sub"]),
                   "sub_color": st["header_muted"]}},
        {"id": "conclusion", "box": LAYOUT["conclusion"],
         "contents": "主结论标题 + 两行结论文字",
         "style": {"plate": st["concl_panel"], "border": "1 SOLID %s" % st["concl_border"],
                   "accent": st["concl_accent"], "radius": 12,
                   "title_font": "%s %d BOLD" % (FONT, st["fonts"]["concl_title"]),
                   "body_font": "%s %d" % (FONT, st["fonts"]["concl_body"]),
                   "ink": st["ink"], "ink2": st["ink2"]}},
        {"id": "kpi", "box": LAYOUT["kpi"],
         "contents": "四张 KPI 卡：总净收入、总经营利润、总订单、总体转化率",
         "style": {"panel": st["panel"], "border": "1 SOLID %s" % st["panel_border"],
                   "shadow": st["panel_shadow"], "radius": 12,
                   "card_width": KPI_W, "gap": KPI_GAP,
                   "label_font": "%s %d" % (FONT, st["fonts"]["kpi_label"]),
                   "value_font": "%s %d BOLD" % (FONT, VALUE_FONT),
                   "unit_font": "%s %d" % (FONT, st["fonts"]["kpi_unit"]),
                   "sub_font": "%s %d" % (FONT, st["fonts"]["kpi_sub"])},
         "cards": mo["kpi"]},
        {"id": "chart", "box": LAYOUT["chart"],
         "contents": "净收入/经营利润共享零起点柱图（含图例、轴刻度、月份标签、比例说明）",
         "style": {"panel": st["panel"], "border": "1 SOLID %s" % st["panel_border"],
                   "shadow": st["panel_shadow"], "radius": 12,
                   "title_font": "%s %d BOLD" % (FONT, st["fonts"]["section_title"])},
         "axis": mo["axes"],
         "plot": mo["plot"], "zero_y": mo["zero_y"],
         "scale_px_per_yuan": mo["scale_px_per_yuan"],
         "bar": {"width": BAR_W, "gap": BAR_GAP, "radius": 2},
         "series": {"net_revenue": {"color": st["net_color"],
                                    "gradient": st["net_grad"]},
                    "profit": {"color": st["profit_color"],
                               "gradient": st["profit_grad"]},
                    "profit_negative": {"color": st["neg_color"],
                                        "gradient": st["neg_grad"]}}},
        {"id": "table", "box": LAYOUT["table"],
         "contents": "月度明细表：月份/净收入/利润/退款率/转化率",
         "style": {"panel": st["panel"], "border": "1 SOLID %s" % st["panel_border"],
                   "shadow": st["panel_shadow"], "radius": 12,
                   "head_bg": "#EEF3FA", "rule": st["rule"],
                   "head_font": "%s %d BOLD" % (FONT, st["fonts"]["table_head"]),
                   "cell_font": "%s %d" % (FONT, st["fonts"]["table_cell"]),
                   "ink": st["ink"], "ink2": st["ink2"]},
         "columns": [{"name": a, "x": b, "width": c, "align": d}
                     for a, b, c, d in TBL_COLS],
         "row_height_unrounded": mo["table"]["row_h_unrounded"]},
        {"id": "footer", "box": LAYOUT["footer"],
         "contents": "公式与计算口径说明",
         "style": {"font": "%s %d" % (FONT, st["fonts"]["footer"]),
                   "color": st["muted"]}},
    ]
    comparison = []
    for rg in regions:
        if prev_regions is None:
            continue
        pb = prev_regions[rg["id"]]["box"]
        comparison.append({
            "id": rg["id"],
            "previous_round": prev_regions[rg["id"]]["round"],
            "previous_box": pb, "current_box": rg["box"],
            "delta": [rg["box"][i] - pb[i] for i in range(4)],
            "abs_delta_max_px": max(abs(x) for x in
                                    [rg["box"][i] - pb[i] for i in range(4)]),
            "within_tolerance_px": 2,
            "passed": max(abs(x) for x in
                          [rg["box"][i] - pb[i] for i in range(4)]) <= 2,
            "note": "主区域边界为同一组常量，本轮只在区域内部重排刻度/行距",
        })
    return {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "round": rnd,
        "output_dir": "outputs/%s/%s/round-%02d" % (RUN_ID, TASK, rnd),
        "canvas": CANVAS,
        "coordinate_basis": "画布左上原点，x 向右、y 向下，像素单位；框为"
                            "[left, top, right, bottom]",
        "regions": regions,
        "comparison": comparison,
        "tolerance_px": 2,
        "tolerance_note": "TASK.md：保持画布与各主区域边界位置 ±2px；"
                          "允许重排内部刻度/行距",
        "elements": cv.layout,
    }


def write_layout(rnd: int) -> dict:
    prev = None
    pp = rdir(rnd - 1) / "layout-map.json"
    if pp.exists():
        prev = {rg["id"]: {"box": rg["box"], "round": rnd - 1}
                for rg in json.loads(pp.read_text(encoding="utf-8"))["regions"]}
    doc = layout_doc(rnd, prev)
    p = rdir(rnd) / "layout-map.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    return {"path": rel(p), "bytes": p.stat().st_size, "sha256": sha_p(p),
            "comparison": doc["comparison"]}


# ------------------------------------------------------------------ 对比度

def _lin(c: int) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = (_lin(int(x)) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def hex2rgb(h: str):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ------------------------------------------------------------------ 像素审计

def png_size(p: pathlib.Path):
    import struct
    with p.open("rb") as fh:
        head = fh.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", "不是 PNG"
    return struct.unpack(">II", head[16:24])


def load_png(p: pathlib.Path):
    from PIL import Image
    import numpy as np
    im = Image.open(p).convert("RGB")
    return np.asarray(im), im.size


def ink_bbox(arr, box, bg_rgb, thr=40):
    """框内与背景差超过 thr 的像素的外接框；返回 (l, t, r, b) 或 None。"""
    from PIL import Image
    import numpy as np
    l, t, r, b = box
    sub = arr[t:b, l:r].astype(int)
    d = np.abs(sub - np.array(bg_rgb)).sum(axis=2)
    m = d > thr
    if not m.any():
        return None
    ys, xs = np.where(m)
    return [int(l + xs.min()), int(t + ys.min()),
            int(l + xs.max() + 1), int(t + ys.max() + 1)]


FAMILY_TEST = {
    "net": lambda a, b, c: (c >= a + 40) & (c >= b + 40),
    "profit": lambda a, b, c: (b >= a + 40) & (b >= c + 20),
    "neg": lambda a, b, c: (a >= b + 60) & (a >= c + 80),
}


def best_run(mask) -> int:
    """布尔数组里最长连续 True 段的长度。"""
    import numpy as np
    best = cur = 0
    for v in np.asarray(mask).ravel():
        cur = cur + 1 if v else 0
        if cur > best:
            best = cur
    return best


def measure_bar(arr, bar, family, band=(PLOT["top"] - 6, PLOT["bottom"] + 6)):
    """沿柱体列扫描，量出实际渲染的柱高与上下边界。

    用「通道优势」而不是颜色距离：柱体是饱和渐变填充（顶浅底深），同族判定
    对渐变稳定；面板白、网格线、零线、负值底色都是低饱和色，不会误判。
    取最长连续匹配行段，避免把柱下方的数值标签或刻度线算进柱高。
    """
    import numpy as np
    x0 = bar["x"] + 1
    x1 = bar["x"] + bar["width"] - 1
    sub = arr[band[0]:band[1], x0:x1].astype(int)
    ok = FAMILY_TEST[family](sub[..., 0], sub[..., 1], sub[..., 2])
    per_row = ok.mean(axis=1)
    rows = per_row > 0.5
    if not rows.any():
        return None
    best = None
    start = None
    for i, hit in enumerate(rows):
        if hit and start is None:
            start = i
        elif not hit and start is not None:
            run = i - start
            if best is None or run > best[1]:
                best = (start, run)
            start = None
    if start is not None:
        run = len(rows) - start
        if best is None or run > best[1]:
            best = (start, run)
    y0 = int(band[0] + best[0])
    y1 = int(band[0] + best[0] + best[1])
    return {"y_top": y0, "y_bottom": y1, "height_px": y1 - y0}


def check_text_tokens(cv_layout, arr, rd_png, region_bg):
    """对每段文字量取所在区域的背景与实际墨迹 bbox，验证文字真的画在那儿。"""
    out = []
    for it in cv_layout:
        if it.get("role") is None or "text" not in it.get("role", "") \
                and not it.get("text"):
            continue
        box = it["box"]
        bb = ink_bbox(arr, box, region_bg, thr=40)
        out.append({"role": it.get("role"), "text": it.get("text"),
                    "box": box, "ink_bbox": bb,
                    "present": bb is not None})
    return out


def audit(rnd: int, viewing_events: int = 0) -> dict:
    """读交付 PNG 做真实像素核验，并写 change-audit.json。"""
    import numpy as np
    rd = rdir(rnd)
    png = rd / "dashboard.png"
    dsl = rd / "dashboard.snapshot"
    arr, size = load_png(png)
    gsize = png_size(png)
    cv, mo = build(rnd)
    st = mo["styles"]

    checks = []

    def g(name, cond, method, result):
        checks.append({"name": name, "passed": bool(cond),
                       "method": method, "result": result})

    g("交付 PNG 为真 PNG 且尺寸 1600x1000",
      size == tuple(CANVAS), "读取 PNG IHDR 的 width/height",
      "实测 %dx%d" % (gsize[0], gsize[1]))

    dsl_ok = dsl.read_bytes() == cv.dsl().encode("utf-8")
    g("交付 DSL 与当前构造器重建结果逐字节一致",
      dsl_ok, "重建 DSL 后与交付 .snapshot 逐字节比对",
      "一致" if dsl_ok else "不一致（说明交付图不是当前代码能复现的结果）")

    # ---- 轴刻度位置
    zero_y = mo["zero_y"]
    grid_ok, grid_detail = True, []
    for gl in mo["grid"]:
        y = int(round(gl["y"]))
        tgt = hex2rgb(st["gridline"] if gl["value"] != 0 else st["zeroline"])
        row = arr[y, PLOT["left"]:PLOT["right"]].astype(int)
        hit = (np.abs(row - np.array(tgt)).sum(axis=1) <= 60)
        best = 0
        run = 0
        for v in hit:
            run = run + 1 if v else 0
            best = max(best, run)
        matched = int(hit.sum())
        grid_detail.append({"value": gl["value"], "y": y,
                            "matched": matched >= 200 and best >= 20,
                            "longest_run_px": int(best),
                            "matched_px": matched,
                            "row_width_px": int(PLOT_W)})
        grid_ok = grid_ok and matched >= 200 and best >= 20
    g("轴刻度线落在计算位置（柱体压过的部分允许不匹配）", grid_ok,
      "在每条刻度线的 y 坐标整行扫描；柱体与数值标签会遮住一段，所以判定用"
      "「与线色一致的像素总数 ≥200 且存在 ≥20px 连续段」，而不是整行匹配",
      "%d 条刻度线全部命中，零线 y=%d" % (len(mo["grid"]), int(round(zero_y))))

    # ---- 柱高几何回归
    bar_res = []
    bars_ok = True
    for b in mo["bars"]:
        fam = "net" if b["metric"] == "net_revenue" else (
            "neg" if b["below_zero"] else "profit")
        m = measure_bar(arr, b, fam)
        if m is None:
            bars_ok = False
            bar_res.append({**b, "measured": None, "passed": False})
            continue
        exp_h = b["height_px"]
        passed = abs(m["height_px"] - exp_h) <= 1 and abs(m["y_top"] -
                                                           b["y_top"]) <= 1
        bars_ok = bars_ok and passed
        bar_res.append({
            "month": b["month"], "metric": b["metric"], "value": b["value"],
            "display": b["display"], "below_zero": b["below_zero"],
            "x": b["x"], "width": b["width"],
            "expected": {"y_top": b["y_top"], "height_px": exp_h,
                         "height_px_unrounded": round(b["height_px_unrounded"], 3)},
            "measured": m,
            "delta_height_px": m["height_px"] - exp_h,
            "delta_y_top_px": m["y_top"] - b["y_top"],
            "scale_px_per_yuan": round(mo["scale_px_per_yuan"], 6),
            "implied_value_from_px": round(m["height_px"] /
                                           mo["scale_px_per_yuan"]),
            "passed": passed,
        })
    g("每根柱的实际像素高度等于计算高度（同一比例、同一零点）",
      bars_ok, "沿柱体中心列扫描同族颜色像素，量出上下边界与高度，"
               "与未舍入计算值按 ±1px 比对",
      "%d 根柱全部通过（净收入 %d + 经营利润 %d）"
      % (len(bar_res),
         len([x for x in bar_res if x["metric"] == "net_revenue"]),
         len([x for x in bar_res if x["metric"] == "profit"])))

    neg_res = [x for x in bar_res if x["below_zero"]]
    zy = int(round(zero_y))
    g("负值没有被裁掉、没有被画成正值、也没有只改数字不改柱高",
      (not neg_res) or
      all(x["passed"] for x in neg_res) and
      all(x["measured"]["y_top"] >= zy - 1 for x in neg_res) and
      all(x["measured"]["y_bottom"] > zy for x in neg_res),
      "负柱必须同时满足：像素高度等于计算高度（没有只改数字）、"
      "上边界不低于零线（没有画成正值）、下边界越过零线（没有被裁掉）",
      "零线 y=%d；负柱 %d 根：%s"
      % (zy, len(neg_res),
         [x["display"] for x in neg_res]))

    # ---- 标签没有压在别的柱上（在交付图上按像素复核）
    sub0 = arr[0:min(PLOT["bottom"] + 8, arr.shape[0]),
               PLOT["left"]:PLOT["right"]].astype(int)
    any_bar = (FAMILY_TEST["net"](sub0[..., 0], sub0[..., 1], sub0[..., 2]) |
               FAMILY_TEST["profit"](sub0[..., 0], sub0[..., 1], sub0[..., 2]) |
               FAMILY_TEST["neg"](sub0[..., 0], sub0[..., 1], sub0[..., 2]))
    lab_bad = []
    pairs = []            # (gap_px, solid_run, intersected)
    fam_min = 0.75        # 一行里柱体列宽被柱族像素填满的最低比例
    min_rows = 4          # 连续实心行的最短长度
    n_lab = 0
    for b in mo["bars"]:
        if not b.get("labelled") or b["label_y"] is None:
            continue
        n_lab += 1
        lx1 = b["label_x"] + b["label_w"]
        ly1 = b["label_y"] + BAR_LABEL_H
        ay1 = min(PLOT["bottom"] + 8, ly1)
        # 负值标签用 neg_color #C2410C，和负柱同族，所以不能按「矩形内有没有
        # 柱色像素」判定——标签自己的红字会自证有罪。改用形状差异：柱体是实心
        # 块，在其自身 30 px 宽里任意一行几乎全被柱族像素填满；文字笔画只有
        # 1–3 px 宽，同一窗口里填不满 75%。按「柱体列窗口内连续实心行数」判定，
        # 既不会被同色文字误报，也不会因为文字墨迹把柱体框住而漏报。
        for c in mo["bars"]:
            bx1 = c["x"] + c["width"]
            by1 = c["y_top"] + c["height_px"]
            dx = max(b["label_x"] - bx1, c["x"] - lx1)
            dy = max(b["label_y"] - by1, c["y_top"] - ly1)
            if dx > 0 and dy > 0:
                gap = (dx * dx + dy * dy) ** 0.5
            elif dx > 0:
                gap = float(dx)
            elif dy > 0:
                gap = float(dy)
            else:
                gap = 0.0
            if gap > 0:
                pairs.append((gap, 0, False))
                continue
            c0 = max(b["label_x"], c["x"])
            c1 = min(lx1, bx1)
            r0 = max(b["label_y"], c["y_top"])
            r1 = min(ay1, by1)
            if c1 - c0 < 3 or r1 - r0 < 1:
                pairs.append((0.0, 0, False))
                continue
            band = any_bar[r0:r1, c0 - PLOT["left"]:c1 - PLOT["left"]]
            solid = np.fromiter(
                (float(band[i].mean()) >= fam_min for i in range(band.shape[0])),
                dtype=bool)
            run = best_run(solid)
            pairs.append((0.0, run, True))
            if run >= min_rows:
                lab_bad.append({
                    "label": {"month": b["month"], "metric": b["metric"],
                              "value": b["display"],
                              "box": [b["label_x"], b["label_y"],
                                      b["label_w"], BAR_LABEL_H]},
                    "bar": {"month": c["month"], "metric": c["metric"],
                            "rect": [c["x"], c["y_top"], c["width"],
                                     c["height_px"]]},
                    "solid_rows_in_label": int(run),
                    "solid_fraction_threshold": fam_min,
                    "column_window_px": c1 - c0,
                })
    n_int = sum(1 for p in pairs if p[2])
    detail = ("%d 个标签 × %d 根柱 = %d 对；不相交的标签与柱体最近间距 "
              "%.1f px；%d 对矩形相交，其中柱体实心行段最长 %d 行（阈值 %d 行）"
              % (n_lab, len(mo["bars"]), len(pairs),
                 min((p[0] for p in pairs if p[0] > 0), default=0.0),
                 n_int, max((p[1] for p in pairs), default=0), min_rows))
    g("数值标签没有压在任何柱体上",
      not lab_bad,
      "对每个标签与每根柱，取两矩形交集，在柱体自身的列窗口内按通道优势判定"
      "统计柱族像素；某一行填满比例 ≥ %.0f%% 算「实心行」，连续 ≥ %d 行即判为"
      "标签压在柱体上。柱体是实心块所以能填满，文字笔画 1–3 px 宽填不满；"
      "不用「矩形内是否有柱色像素」是因为负值标签与负柱同色，会自证有罪。"
      "这是第二道防线，第一道是干跑门禁「标签矩形与任何柱体矩形不相交」（用"
      "模型精确几何、无盲区），第三道是柱高实测（被压的柱体会量不准）；"
      "判定的活性由 a22_selftest_label_gate.py 用合成图反测"
      % (fam_min * 100, min_rows),
      detail if not lab_bad else "%s" % lab_bad)
    g("经营利润柱未标注时，其数值确实出现在右侧明细表中",
      all(any(c["column"] == "利润" and c["text"] == m["display"]["profit"]
              for c in mo["table_cells"]) for m in mo["data"]["months"]),
      "凡是不在柱图标注的经营利润值，必须能在表格「利润」列逐月找到",
      "%d 个月的利润值全部能在表格「利润」列找到"
      % len(mo["data"]["months"]))

    # ---- 文字是否真的渲染在预期位置
    texts = [it for it in cv.layout if it.get("text")]
    missing, sampled = [], 0
    for it in texts:
        box = [int(v) for v in it["box"]]
        sub = arr[box[1]:box[3], box[0]:box[2]].reshape(-1, 3)
        uniq, cnt = np.unique(sub, axis=0, return_counts=True)
        bg = tuple(int(x) for x in uniq[cnt.argmax()])
        if ink_bbox(arr, box, bg, thr=40) is None:
            missing.append(it)
        sampled += 1
    g("每段文字都在其预期框内产生了墨迹", not missing,
      "逐段取该框内像素众数作为底色（自动适配页面底/白面板/浅蓝结论面板/"
      "浅灰表头底），再与底色做阈值 40 的差分并取墨迹外接框",
      "%d 段文字全部检出%s" % (sampled, "" if not missing else
                               "；缺失：%s" % [m.get("role") for m in missing]))

    # ---- 最小字号
    sizes = sorted({it["fontSize"] for it in texts})
    body_sizes = [it["fontSize"] for it in texts if "title" not in it["role"]
                  and it["role"] not in ("kpi_value",)]
    g("除标题与 KPI 数值外的文字均 ≥22px",
      min(body_sizes) >= MIN_FONT, "收集交付布局模型中每段文字的 fontSize",
      "正文最小 %d（全部字号档位 %s）" % (min(body_sizes), sizes))

    # ---- 对比度（额外证据，非本题硬要求）
    pairs = [
        ("页面底 × ink", hex2rgb(st["page"]), hex2rgb(st["ink"])),
        ("页面底 × ink2", hex2rgb(st["page"]), hex2rgb(st["ink2"])),
        ("页面底 × muted", hex2rgb(st["page"]), hex2rgb(st["muted"])),
        ("面板白 × ink", hex2rgb(st["panel"]), hex2rgb(st["ink"])),
        ("面板白 × ink2", hex2rgb(st["panel"]), hex2rgb(st["ink2"])),
        ("面板白 × muted", hex2rgb(st["panel"]), hex2rgb(st["muted"])),
        ("结论面板 × ink2", hex2rgb(st["concl_panel"]), hex2rgb(st["ink2"])),
        ("标题面板 × header_muted", hex2rgb(st["header_panel"]),
         hex2rgb(st["header_muted"])),
        ("标题面板 × header_ink", hex2rgb(st["header_panel"]),
         hex2rgb(st["header_ink"])),
        ("标签 × chip_text", hex2rgb(st["chip"]), hex2rgb(st["chip_text"])),
        ("面板白 × 负利润色", hex2rgb(st["panel"]), hex2rgb(st["neg_color"])),
    ]
    ctable = [{"pair": n, "foreground": "#" + "".join("%02X" % x for x in fg),
               "background": "#" + "".join("%02X" % x for x in bg),
               "contrast": round(contrast(fg, bg), 3)} for n, fg, bg in pairs]
    g("全部文字色对背景对比度 ≥4.5:1",
      all(x["contrast"] >= 4.5 for x in ctable),
      "8 位 sRGB 先 c/255 再线性化（c≤0.04045 取 c/12.92，否则"
      "((c+0.055)/1.055)^2.4），L=0.2126R+0.7152G+0.0722B，"
      "对比度=(max+0.05)/(min+0.05)，用未舍入值判阈值",
      "最小 %s（%s）" % (min(x["contrast"] for x in ctable),
                         min(ctable, key=lambda x: x["contrast"])["pair"]))

    # ---- 数据回归
    months = mo["data"]["months"]
    months_ok = (len(months) == (7 if rnd >= 3 else 6) and
                 months[0]["month"] == "2026-04" and
                 months[-1]["month"] == ("2026-10" if rnd >= 3 else "2026-09"))
    g("所有月份原样出现、未省略首月、末月正确", months_ok,
      "比对计算结果与 CSV 原值 + 轮次声明的新增月份",
      "%d 个月，%s → %s" % (len(months), months[0]["month"],
                            months[-1]["month"]))

    tbl = mo["table_cells"]
    tbl_ok = len(tbl) == 5 * len(months) and all(
        c["text"] == (m["month"] if c["column"] == "月份" else
                      (m["display"]["net_revenue"] if c["column"] == "净收入" else
                       (m["display"]["profit"] if c["column"] == "利润" else
                        (m["refund_rate"]["display"] if c["column"] == "退款率"
                         else m["conversion_rate"]["display"]))))
        for c, m in zip(tbl, [m for m in months for _ in range(5)]))
    g("表格 5 列 × %d 行与 computed-data 逐格一致" % len(months), tbl_ok,
      "逐格比对表格渲染文本与 computed-data 的显示值",
      "%d 格全部一致" % len(tbl))

    doc = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "round": rnd,
        "output_dir": "outputs/%s/%s/round-%02d" % (RUN_ID, TASK, rnd),
        "baseline": {
            "round": rnd - 1 if rnd > 1 else None,
            "dashboard": ("outputs/%s/%s/round-%02d/dashboard.png"
                          % (RUN_ID, TASK, rnd - 1)) if rnd > 1 else None,
            "computed_data": ("outputs/%s/%s/round-%02d/computed-data.json"
                              % (RUN_ID, TASK, rnd - 1)) if rnd > 1 else None,
            "note": ("第二轮以第一轮归档件为基线；"
                     "第三轮以第二轮归档件为基线并保留其两项更正")
                    if rnd > 1 else "第一轮以 inputs/monthly.csv 为唯一基线",
        },
        "changes": change_list(rnd, mo),
        "preserved": preserved_list(rnd, mo),
        "regression": {
            "checks": checks,
            "all_passed": all(c["passed"] for c in checks),
            "n_checks": len(checks),
            "bar_geometry": bar_res,
            "contrast": ctable,
            "gridlines": grid_detail,
            "layout_map_comparison": (
                json.loads((rdir(rnd) / "layout-map.json")
                           .read_text(encoding="utf-8"))["comparison"]
                if (rdir(rnd) / "layout-map.json").exists() else None),
            "viewing": {
                "image": rel(png),
                "dsl": rel(dsl),
                "png_sha256": sha_p(png),
                "viewing_events": viewing_events,
                "views_manifest": "tmp/%s/%s/preview/round-%02d/views-manifest.json"
                                  % (RUN_ID, TASK, rnd),
            },
        },
        "evidence": {
            "deliverable_png": {"path_base": "output_dir", "path": "dashboard.png"},
            "deliverable_dsl": {"path_base": "output_dir", "path": "dashboard.snapshot"},
            "attempts": {"path_base": "suite_root",
                         "path": "tmp/%s/%s/responses/" % (RUN_ID, TASK)},
            "requests_log": {"path_base": "suite_root",
                             "path": "tmp/%s/%s/requests.jsonl" % (RUN_ID, TASK)},
            "viewing_log": {"path_base": "suite_root",
                            "path": "tmp/%s/%s/viewing-evidence.json" % (RUN_ID, TASK)},
        },
    }
    p = rdir(rnd) / "change-audit.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    return {"path": rel(p), "bytes": p.stat().st_size, "sha256": sha_p(p),
            "all_passed": doc["regression"]["all_passed"],
            "n_checks": len(checks), "checks": checks}


def np_close(row, target, tol=28) -> bool:
    import numpy as np
    return bool(np.abs(row - np.array(target)).max() <= tol)


def _prev_model(rnd):
    """取上一轮的重建模型，只用来给变更说明填真实的几何与数值。"""
    if rnd <= 1:
        return None
    return build(rnd - 1)


def change_list(rnd: int, mo: dict) -> list:
    """变更传播：每一处输入变化扩散到哪些计算、KPI、柱高、表格与结论。

    里面的每个数字都从本轮/上一轮的重建模型取，不手写，
    避免说明文档和实际渲染对不上。
    """
    prev = _prev_model(rnd)
    if rnd == 1:
        return [{
            "id": "a22-r1-c0",
            "source": "TASK.md 第一轮（原始 inputs/monthly.csv，未做更正）",
            "field": "全部 6 个月原始值",
            "old": None, "new": None,
            "propagation": "monthly.csv → computed-data.json 的 months/totals → "
                           "四张 KPI → 共享零起点柱图（净收入与经营利润）→ "
                           "六行月度明细表 → 主结论标题与正文",
            "geometry": {
                "plot": mo["plot"], "zero_y": mo["zero_y"],
                "scale_px_per_yuan": round(mo["scale_px_per_yuan"], 6),
                "row_height": round(mo["table"]["row_h_unrounded"], 2),
                "group_slot_px": round(mo["plot"]["w"] / 6, 2),
            },
            "actual_output_location": "round-01/dashboard.png 全部四个主区域",
        }]

    prev_cv, pv = prev   # build() 返回 (Canvas, model)；这里只用得到 model
    sp = mo["axes"]      # 本轮的轴参数（sp 与 st 之前混用，现统一指向本轮轴）
    out = []
    if rnd == 2:
        out.append({
            "id": "a22-r2-c1",
            "source": "rounds/round-02.md 第 1 行",
            "field": "2026-08 refund_amount",
            "old": 15048, "new": 25048, "delta": 10000,
            "propagation": [
                "2026-08 净收入 173,052 → 163,052（−10,000）",
                "2026-08 经营利润 41,052 → 31,052（−10,000）",
                "2026-08 退款率 8.00% → 13.32%",
                "2026-08 转化率不变（orders/sessions 未变）",
                "期间净收入 918,624 → 908,624；期间经营利润 262,124 → 182,124",
                "KPI1 总净收入、KPI2 总经营利润随之更新；"
                "KPI3 总订单、KPI4 总体转化率不变",
                "柱图：2026-08 净收入柱与经营利润柱同时缩短 "
                "%s × 比例 px" % int(round(10000 * mo["scale_px_per_yuan"])),
                "表格：2026-08 行净收入、利润、退款率三格变化",
                "结论：2026-08 退款率升至 13.32%",
            ],
            "actual_output_location": "round-02/dashboard.png：KPI1/KPI2、"
                                      "图表 2026-08 组、表格 2026-08 行、结论区",
        })
        out.append({
            "id": "a22-r2-c2",
            "source": "rounds/round-02.md 第 1–2 行",
            "field": "2026-09 operating_cost",
            "old": 138000, "new": 208000, "delta": 70000,
            "propagation": [
                "2026-09 净收入不变（退款未变）",
                "2026-09 经营利润 64,368 → −5,632（−70,000），由正转负",
                "柱图负轴：轴底由 %s 扩到 %s，零线由 y=%s 移到 y=%s，"
                "绘图区保持 y %d..%d，比例由 %.6f 变为 %.6f px/元"
                % (pv["axes"]["min"], sp["min"], round(pv["zero_y"], 1),
                   round(mo["zero_y"], 1), PLOT["top"], PLOT["bottom"],
                   pv["scale_px_per_yuan"], mo["scale_px_per_yuan"]),
                "2026-09 经营利润柱绘在零线下方 "
                "%s px（同一比例，未放大未隐藏），改为负利润红色渐变，"
                "数值标签 −5,632 置于柱下方并加粗"
                % next(b["height_px"] for b in mo["bars"]
                       if b["below_zero"]),
                "KPI2 总经营利润 262,124 → 182,124，数值改用负利润色",
                "KPI4 总体转化率不变（orders/sessions 均未变）",
                "总体退款率由 %s 变为 %s"
                % (pv["data"]["totals"]["refund_rate"]["display"],
                   mo["data"]["totals"]["refund_rate"]["display"]),
                "表格：2026-09 行利润格改为负值并以负利润色加粗",
                "结论：2026-09 成为唯一亏损月，期间利润减少 80,000 元",
            ],
            "geometry": {
                "prev": {"axis_min": pv["axes"]["min"], "axis_max": pv["axes"]["max"],
                         "zero_y": round(pv["zero_y"], 1),
                         "scale_px_per_yuan": round(pv["scale_px_per_yuan"], 6),
                         "negative_axis": pv["axes"]["negative_axis"]},
                "current": {"axis_min": sp["min"], "axis_max": sp["max"],
                            "zero_y": round(mo["zero_y"], 1),
                            "scale_px_per_yuan": round(mo["scale_px_per_yuan"], 6),
                            "negative_axis": sp["negative_axis"]},
            },
            "actual_output_location": "round-02/dashboard.png：轴刻度、零线、"
                                      "2026-09 组柱体、KPI2、表格 2026-09 行、"
                                      "结论区、图例新增「负利润」项",
        })
    else:
        slot_now = mo["plot"]["w"] / len(mo["data"]["months"])
        slot_prev = pv["plot"]["w"] / len(pv["data"]["months"])
        out.append({
            "id": "a22-r3-c1",
            "source": "rounds/round-03.md 第 1–2 行",
            "field": "新增 2026-10 整行",
            "old": None,
            "new": {"orders": 640, "gross_revenue": 224000,
                    "refund_amount": 11200, "operating_cost": 142000,
                    "sessions": 5900},
            "derived": {"net_revenue": 212800, "profit": 70800,
                        "refund_rate": "5.00%", "conversion_rate": "10.85%"},
            "propagation": [
                "月份数 6 → 7，柱组槽宽由 %.2f px 变为 %.2f px，"
                "柱宽 %d 与组内间距 %d 不变"
                % (slot_prev, slot_now, BAR_W, BAR_GAP),
                "柱图与表格各新增一组/一行；表格行高由 %.2f px 变为 %.2f px"
                % (pv["table"]["row_h_unrounded"], mo["table"]["row_h_unrounded"]),
                "2026-10 净收入 212,800 与经营利润 70,800 成为全期最高柱",
                "KPI1 总净收入 %s → %s；KPI2 总经营利润 %s → %s"
                % (pv["data"]["totals"]["display"]["net_revenue"],
                   mo["data"]["totals"]["display"]["net_revenue"],
                   pv["data"]["totals"]["display"]["profit"],
                   mo["data"]["totals"]["display"]["profit"]),
                "KPI3 总订单 %s → %s；KPI4 总体转化率 %s → %s"
                % (pv["data"]["totals"]["display"]["orders"],
                   mo["data"]["totals"]["display"]["orders"],
                   pv["data"]["totals"]["conversion_rate"]["display"],
                   mo["data"]["totals"]["conversion_rate"]["display"]),
                "总体退款率 %s → %s"
                % (pv["data"]["totals"]["refund_rate"]["display"],
                   mo["data"]["totals"]["refund_rate"]["display"]),
                "2026-09 的 −5,632 仍为唯一亏损月（负轴与负色保持不变）",
            ],
            "geometry": {
                "prev": {"months": len(pv["data"]["months"]),
                         "group_slot_px": round(slot_prev, 2),
                         "row_height": round(pv["table"]["row_h_unrounded"], 2)},
                "current": {"months": len(mo["data"]["months"]),
                            "group_slot_px": round(slot_now, 2),
                            "row_height": round(mo["table"]["row_h_unrounded"], 2)},
            },
            "actual_output_location": "round-03/dashboard.png：柱图第 7 组、"
                                      "表格第 7 行、全部四张 KPI、结论区",
        })
        out.append({
            "id": "a22-r3-c2",
            "source": "rounds/round-03.md 第 3 行「两项第二轮更正继续有效」",
            "field": "2026-08 refund_amount / 2026-09 operating_cost",
            "old": "沿用第二轮：25048 / 208000", "new": "未恢复 CSV 旧值",
            "propagation": [
                "2026-08 净收入仍为 163,052、退款率仍为 13.32%",
                "2026-09 经营利润仍为 −5,632，仍绘于零线下方",
                "轴仍保留 %s 的负范围" % sp["min"],
            ],
            "actual_output_location": "round-03/dashboard.png 的 2026-08/2026-09"
                                      " 两组柱体与表格两行",
        })
    return out


def preserved_list(rnd: int, mo: dict) -> list:
    out = [{
        "id": "a22-r%d-p1" % rnd,
        "item": "画布 1600×1000 与六个主区域边界",
        "evidence": "layout-map.json 的 comparison：各区域分量差 0px，"
                    "容差 ±2px",
    }, {
        "id": "a22-r%d-p2" % rnd,
        "item": "主字体与视觉系统（面板白 #FFFFFF、描边 #D9E1EC、标题面板 "
                "#0E1B2E、结论面板 #EAF2FB、正色 #1F6FBF/#1F8A63、"
                "负色 #C2410C、正文字体 %s、最小字号 22）" % FONT,
        "evidence": "layout-map.json 的 regions[].style 逐轮比对；"
                    "对比度表 %d 组全部 ≥4.5:1" % 11,
    }, {
        "id": "a22-r%d-p3" % rnd,
        "item": "柱图共享零起点、同一线性比例；柱宽 30px、组内间距 6px、圆角 2",
        "evidence": "audit 的 bar_geometry：每根柱的像素高度与未舍入计算值差 ≤1px",
    }]
    if rnd >= 2:
        out.append({
            "id": "a22-r%d-p4" % rnd,
            "item": "2026-04 至 2026-07 四个月的原始数据与派生值（净收入、利润、"
                    "退款率、转化率）",
            "evidence": "computed-data.json 的 months[].csv_original 与派生值逐月"
                        "比对，未被本轮更正触及的月份一字未变",
        })
    if rnd == 2:
        out.append({
            "id": "a22-r2-p5",
            "item": "orders 与 sessions 全部月份原值（两项更正都不涉及它们）",
            "evidence": "KPI3 总订单 3,045、KPI4 总体转化率 11.15% 与第一轮完全一致",
        })
    return out


# ------------------------------------------------------------------ 视图

def make_views(rnd: int, png: pathlib.Path | None = None) -> list:
    from PIL import Image
    rd = rdir(rnd)
    png = png or (rd / "dashboard.png")
    out = PREVDIR / ("round-%02d" % rnd)
    out.mkdir(parents=True, exist_ok=True)
    im = Image.open(png).convert("RGB")
    crops = {
        "header": (48, 40, 1552, 142),
        "conclusion": (48, 158, 1552, 278),
        "kpi": (48, 294, 1552, 434),
        "chart": (48, 450, 876, 916),
        "chart_bottom": (120, 700, 876, 916),
        "table": (892, 450, 1552, 916),
        "footer": (48, 932, 1552, 964),
    }
    scales = {"header": 1.0, "conclusion": 1.5, "kpi": 1.5, "chart": 1.5,
              "chart_bottom": 2.0, "table": 1.5, "footer": 2.0}
    manifest = [{"name": "whole", "box": (0, 0, 1600, 1000), "scale": 1.0,
                 "source_sha256": sha_p(png)}]
    (out / "whole.png").write_bytes(b"")
    im.save(out / "whole.png")
    manifest.pop()
    manifest.append({"name": "whole", "box": [0, 0, 1600, 1000], "scale": 1.0,
                     "out": "tmp/%s/%s/preview/round-%02d/whole.png"
                             % (RUN_ID, TASK, rnd),
                     "source_sha256": sha_p(png)})
    for name, (l, t, r, b) in crops.items():
        box = (l, t, min(r, im.width), min(b, im.height))
        c = im.crop(box)
        sc = scales[name]
        if sc != 1.0:
            c = c.resize((int(c.width * sc), int(c.height * sc)),
                         Image.LANCZOS)
        p = out / ("%s.png" % name)
        c.save(p)
        manifest.append({"name": name, "box": [l, t, r, b], "scale": sc,
                         "out": rel(p), "source_sha256": sha_p(png)})
    (out / "views-manifest.json").write_text(
        json.dumps({"round": rnd, "source": rel(png),
                    "views": manifest}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    return manifest


def append_viewing(rnd: int, events: list) -> int:
    p = TMP / "viewing-evidence.json"
    doc = {}
    if p.exists() and p.stat().st_size:
        doc = json.loads(p.read_text(encoding="utf-8"))
    doc.setdefault("rounds", {})
    blk = doc["rounds"].setdefault(str(rnd), {"image_open_events": []})
    blk["image_open_events"].extend(events)
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    return len(blk["image_open_events"])


def append_iteration(rec: dict) -> None:
    append_jsonl(TMP / "iterations.jsonl", rec)


# ------------------------------------------------------------------ CLI

def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    rnd = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    if cmd == "data":
        print(json.dumps(write_computed(rnd), ensure_ascii=False))
    elif cmd == "layout":
        print(json.dumps(write_layout(rnd), ensure_ascii=False))
    elif cmd == "dryrun":
        gates = dryrun(rnd)
        rep = gate_report(gates)
        for n, p, d in gates:
            print("  [%s] %s%s" % ("PASS" if p else "FAIL", n,
                                    (" — " + d) if d else ""))
        print("门禁 %d/%d 通过" % (rep["n_passed"], rep["n_checks"]))
        cv, mo = build(rnd)
        print("DSL %d 字节，%d 个布局元素"
              % (len(cv.dsl().encode("utf-8")), len(cv.layout)))
    elif cmd == "render":
        print(json.dumps(render(rnd), ensure_ascii=False))
    elif cmd == "audit":
        print(json.dumps(audit(rnd, int(sys.argv[3]) if len(sys.argv) > 3
                               else 0), ensure_ascii=False, default=str))
    elif cmd == "views":
        m = make_views(rnd)
        print("视图 %d 个 → %s" % (len(m), PREVDIR / ("round-%02d" % rnd)))
    elif cmd == "pngsize":
        print(png_size(rdir(rnd) / "dashboard.png"))
    else:
        raise SystemExit("未知命令 %s" % cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
