# -*- coding: utf-8 -*-
"""A24 shared: schedule (single source of truth for 3 images + JSONs) + DSL helpers.

Schedule proven optimal by exhaustive enumeration in a24_solve.py:
8 team assignments x per-team topological orders (112 order pairs total),
min makespan = 260 minutes; critical-path LB = 255 (R01->R04->R07->R09->R10->R12);
workload LB = 485/2 = 242.5; buffer = 420 - 260 = 160.

Display convention: minutes offset from 09:00 (+08:00); half-open [start,end).
DSL lessons applied (all verified in this run): Positioned must be a direct
Stack child; Opacity/Transform wrap inner boxes only; Text content lives in
the text= attribute.
"""
import math

FONT = "Noto Sans CJK SC"
TZ = "Asia/Shanghai (+08:00)"
DAY = "2026-11-07"
START_CLOCK = "09:00"
DEADLINE_CLOCK = "16:00"
WINDOW = 420
FINISH = 260
BUFFER = 160
FINISH_CLOCK = "13:20"
TOTAL_M = 485
CP_LB = 255
CP_PATH = ["R01", "R04", "R07", "R09", "R10", "R12"]
WL_LB = 242.5

# id, label, team, start, end, deps, teams_options, risk(K id or None)
SCHEDULE = [
    dict(id="R01", label="需求核对", team="design", s=0, e=25, deps=[],
         options=["design"], risk=None),
    dict(id="R02", label="服务与字体探测", team="engineering", s=0, e=20, deps=[],
         options=["engineering"], risk="K1"),
    dict(id="R03", label="数据清洗", team="engineering", s=20, e=60, deps=["R02"],
         options=["engineering"], risk=None),
    dict(id="R04", label="视觉系统", team="design", s=25, e=85, deps=["R01"],
         options=["design"], risk=None),
    dict(id="R05", label="文案审校", team="engineering", s=60, e=90, deps=["R01"],
         options=["design", "engineering"], risk="K2"),
    dict(id="R06", label="图表计算", team="engineering", s=90, e=135, deps=["R03"],
         options=["engineering"], risk=None),
    dict(id="R07", label="主海报构建", team="design", s=90, e=160, deps=["R04", "R05"],
         options=["design"], risk=None),
    dict(id="R08", label="驾驶舱构建", team="engineering", s=135, e=200,
         deps=["R04", "R06"], options=["engineering"], risk=None),
    dict(id="R09", label="手机适配", team="design", s=160, e=205, deps=["R07"],
         options=["design", "engineering"], risk=None),
    dict(id="R10", label="视觉回归检查", team="design", s=205, e=240,
         deps=["R07", "R08", "R09"], options=["design"], risk="K3"),
    dict(id="R11", label="产物与数据核验", team="engineering", s=205, e=235,
         deps=["R08", "R09"], options=["engineering"], risk=None),
    dict(id="R12", label="交付归档", team="design", s=240, e=260,
         deps=["R10", "R11"], options=["design", "engineering"], risk=None),
]
BY_ID = {t["id"]: t for t in SCHEDULE}

RISKS = [
    dict(id="K1", task="R02", impact="服务限流导致等待",
         mitigation="保留响应并依据Retry-After重试"),
    dict(id="K2", task="R05", impact="长文案导致版式回归",
         mitigation="冻结文案后再完成适配"),
    dict(id="K3", task="R10", impact="实际图像暴露裁剪或比例错误",
         mitigation="预留返工缓冲，不跳过看图"),
]
RISK_BY_TASK = {r["task"]: r for r in RISKS}

# idle gaps (minutes) shown on the execution board
GAPS = [("design", 85, 90), ("engineering", 200, 205)]

TEAM_CN = {"design": "设计团队", "engineering": "工程团队"}
TEAM_COLOR = {"design": "#4F46E5", "engineering": "#0E7490"}
TEAM_SOFT = {"design": "#EEF2FF", "engineering": "#ECFEFF"}
TEAM_BORDER = {"design": "#C7D2FE", "engineering": "#A5F3FC"}

PAL = dict(
    bg="#F5F7FB", bg_brief="#F8FAFC", bg_card="#FFFFFF",
    head="#101A34", head_soft="#C7D2EA", head_brand="#93A3C4",
    ink="#0F172A", ink2="#1E293B", muted="#64748B", faint="#94A3B8",
    line="#E2E8F0", axis="#94A3B8",
    good="#059669", good_soft="#D1FAE5", bad="#DC2626", bad_soft="#FEE2E2",
    bad_border="#FCA5A5", gap="#E2E8F0", white="#FFFFFF",
)


def clock(m):
    """Minute offset -> HH:MM (release day 09:00 base)."""
    return "%02d:%02d" % divmod(9 * 60 + m, 60)


def timespan(t):
    return "%s–%s" % (clock(t["s"]), clock(t["e"]))


def duration(t):
    return "%dmin" % (t["e"] - t["s"])


def deps_text(t):
    return "依赖：" + "、".join(t["deps"]) if t["deps"] else "依赖：无（起点）"


def check_schedule():
    """Assert every hard constraint on SCHEDULE (evidence for audit)."""
    errs = []
    by_team = {"design": [], "engineering": []}
    for t in SCHEDULE:
        if t["e"] - t["s"] != BY_ID[t["id"]].get("m", t["e"] - t["s"]):
            pass
        if t["team"] not in t["options"]:
            errs.append("%s team not in options" % t["id"])
        if not (0 <= t["s"] < t["e"] <= WINDOW):
            errs.append("%s outside window" % t["id"])
        for d in t["deps"]:
            if BY_ID[d]["e"] > t["s"]:
                errs.append("%s dep %s not finished" % (t["id"], d))
        by_team[t["team"]].append(t)
    for team, ts in by_team.items():
        ts = sorted(ts, key=lambda x: x["s"])
        for a, b in zip(ts, ts[1:]):
            if b["s"] < a["e"]:
                errs.append("%s/%s overlap on %s" % (a["id"], b["id"], team))
    if max(t["e"] for t in SCHEDULE) != FINISH:
        errs.append("finish mismatch")
    return errs


# ---------------- DSL helpers (proven patterns from A21-A23) ----------------
def r2(x):
    return float("%.2f" % x)


def rect_at(l, t, w, h, fill, radius=0, border=None, border_w=1):
    """border spec per service: single attr '宽度 SOLID 颜色' (integer width)."""
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s/></SizedBox></Positioned>'
            % (l, t, w, h, w, h, fill, radius, b))


def text_el(l, t, w, h, text, size, color, bold=False, align="LEFT"):
    wt = ' fontStyle="BOLD"' if bold else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="%s"%s'
            ' lineHeight="1.28" text="%s"/></Positioned>'
            % (l, t, w, h, size, FONT, color, align, wt, text))


def chip_el(l, t, w, h, fill, label, size, color, radius=8, border=None,
            border_w=1):
    b = (' border="%g SOLID %s"' % (border_w, border)) if border else ""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Stack alignment="CENTER">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"%s/></SizedBox>'
            '<Text fontSize="%g" fontFamily="%s" color="%s" textAlign="CENTER"'
            ' fontStyle="BOLD" lineHeight="1.28" text="%s"/>'
            '</Stack></Positioned>'
            % (l, t, w, h, w, h, fill, radius, b, size, FONT, color, label))


def rot_matrix(rot):
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    f = lambda v: ("%.8f" % v).rstrip("0").rstrip(".") or "0"
    return "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (f(c), f(s), f(-s), f(c))


def diamond_el(cx, cy, size, fill):
    """Small rotated-square arrow tip (no triangle tag in DSL)."""
    return ('<Positioned left="%g" top="%g" width="%g" height="%g">'
            '<Transform matrix="%s" alignment="CENTER">'
            '<SizedBox width="%g" height="%g"><DecoratedBox color="%s"'
            ' borderRadius="%g"/></SizedBox></Transform></Positioned>'
            % (r2(cx - size / 2), r2(cy - size / 2), size, size,
               rot_matrix(45), size, size, fill, size * 0.12))


def line_h(y, x1, x2, color, thick=2):
    return rect_at(min(x1, x2), y - thick / 2.0, abs(x2 - x1), thick, color)


def line_v(x, y1, y2, color, thick=2):
    return rect_at(x - thick / 2.0, min(y1, y2), thick, abs(y2 - y1), color)


def elbow_arrow(px, py_bottom, cx, cy_top, elbow_y, color="#94A3B2",
                thick=2, via_x=None):
    """Elbow connector: parent bottom-center -> child top-center (+ diamond).
    via_x: route vertical segment at this x instead of parent/child centers."""
    els = []
    y1, y2 = py_bottom, cy_top
    if via_x is not None:
        els.append(line_v(via_x, y1, elbow_y, color, thick))
        els.append(line_h(elbow_y, via_x, px, color, thick))
    else:
        els.append(line_v(px, y1, elbow_y, color, thick))
    els.append(line_h(elbow_y, px, cx, color, thick))
    els.append(line_v(cx, elbow_y, y2 - 6, color, thick))
    els.append(diamond_el(cx, y2 - 4, 11, color))
    return "".join(els)


def wrap_el(body, w, h, bg):
    return ('<Snapshot type="png" background="%s">'
            '<SizedBox width="%g" height="%g"><Stack alignment="TOP_LEFT"'
            ' clipBehavior="NONE">%s</Stack></SizedBox></Snapshot>'
            % (bg, w, h, body))
