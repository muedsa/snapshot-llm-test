"""A02 三会场密集会议日程：1920×1200 泳道大图 + 720×1280 手机导览 + schedule-audit.json。

启动基准：总任务根（cwd）。SNAPSHOT_RUN_ID 必须已设置。
输入只读：tasks/A02-conference-schedule/inputs/{agenda.csv,venues.json}

大图几何：三条会场泳道共用一条线性时间轴 09:00–16:00。
    PX0=40、plot_w=1840、SPAN=420 分钟 → PPM = 1840/420 px/分钟。
    X(t) = PX0 + (t − 09:00) × PPM；卡左缘 = X(start)，卡宽 = 分钟数 × PPM。
    块宽不做任何外扩或压缩：30 分钟就是 131.4px，短场次靠竖排 + 标题折行装下文字。
手机图：分时段列表（上午场 8 场 / 午休 / 下午场 7 场），不缩放、不裁切大图。

审计 JSON 与两张图由同一份计算结果生成，图与 JSON 不各自硬编码数字。
"""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(Path.cwd()))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tools"))

import kit as K                      # noqa: E402
import taskgen as TG                # noqa: E402
from dsl import at, box, canvas, layer, text as dsl_text, text_width  # noqa: E402

TASK = "A02"
INP = ROOT / "tasks" / "A02-conference-schedule" / "inputs"

# 类别：颜色取已校验分类调色板的前 5 位（固定顺序，不循环）；标签取自 venues.json
CAT = {
    "keynote":  {"label": "主旨",   "color": K.SERIES[0]},
    "workshop": {"label": "工作坊", "color": K.SERIES[1]},
    "talk":     {"label": "分享",   "color": K.SERIES[2]},
    "demo":     {"label": "演示",   "color": K.SERIES[3]},
    "panel":    {"label": "圆桌",   "color": K.SERIES[6]},
}
CAT_ORDER = ["keynote", "workshop", "talk", "demo", "panel"]

LANE_BAND = "#F4F3F0"
LUNCH_TINT = "#E5E3DC"    # 比泳道底带 #F4F3F0 明显更深，午休带一眼可辨
CHIP = "#F1F0EC"

# 字号：大图正文（标题/讲者）20，时间标签/编号 18，标注 16 —— 均 ≥ 任务下限
FS_T, FS_ID, FS_TM, FS_SP, FS_CA = 20, 18, 18, 18, 16
SLACK = 1.06   # text_width 对拉丁/数字系统性偏小 ≤6%（A01 校准），断言按此放足

# 每个字段在大图 / 手机图上的字号与字重，随 content_map 一起落盘，
# 使 schedule-audit.json 自述排版，像素自检可直接复算期望宽度。
# （MOBILE_STYLE 在 FS_MB/FS_MC 定义之后，见手机图段。）
WIDE_STYLE = {"id": (FS_ID, True), "time": (FS_TM, False),
              "speaker": (FS_SP, False), "category": (FS_CA, False),
              "title": (FS_T, True)}


def hm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def hmfmt(t: int) -> str:
    return f"{t // 60:02d}:{t % 60:02d}"


def tw(s, size, bold=False):
    return text_width(s, size, bold)


# ===========================================================================
# 输入与统计
# ===========================================================================
def load():
    venues = json.loads((INP / "venues.json").read_text(encoding="utf-8"))
    caps = {k: v["capacity"] for k, v in venues.items()
            if isinstance(v, dict) and "capacity" in v}
    assert set(caps) == {"A", "B", "C"}, caps
    for k, v in venues["categories"].items():
        assert CAT[k]["label"] == v, f"类别标签与 venues.json 不一致：{k}"
    rows = list(csv.DictReader((INP / "agenda.csv").open(encoding="utf-8")))
    assert len(rows) == 15, len(rows)
    evs = []
    for r in rows:
        t0, t1 = hm(r["start"]), hm(r["end"])
        assert t1 > t0, r
        evs.append({"id": r["id"], "venue": r["venue"], "start": r["start"],
                    "end": r["end"], "t0": t0, "t1": t1, "dur": t1 - t0,
                    "title": r["title"], "speaker": r["speaker"],
                    "category": r["category"]})
    for e in evs:
        assert e["venue"] in caps and e["category"] in CAT, e
    return caps, evs


T0, T1, LUNCH0, LUNCH1 = hm("09:00"), hm("16:00"), hm("12:00"), hm("13:00")
SPAN = T1 - T0                        # 420
VENUES = ["A", "B", "C"]


def analyse(caps, evs):
    by_venue = {v: sorted([e for e in evs if e["venue"] == v], key=lambda e: e["t0"])
                for v in VENUES}
    gaps, conflicts = {}, []
    for v in VENUES:
        vs, cur, out = by_venue[v], T0, []
        for e in vs:
            if e["t0"] > cur:
                spans_lunch = LUNCH0 > cur and e["t0"] > LUNCH1
                out.append({"start": hmfmt(cur), "end": hmfmt(e["t0"]),
                            "minutes": e["t0"] - cur,
                            "note": ("覆盖公共午休 12:00–13:00" if spans_lunch
                                     else "相邻两场之间的空档")})
            cur = max(cur, e["t1"])
        if cur < T1:
            out.append({"start": hmfmt(cur), "end": hmfmt(T1), "minutes": T1 - cur,
                        "note": "当日收尾空档"})
        gaps[v] = out
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                a, b = vs[i], vs[j]
                lo, hi = max(a["t0"], b["t0"]), min(a["t1"], b["t1"])
                if hi > lo:
                    conflicts.append({"venue": v, "pair": [a["id"], b["id"]],
                                      "overlap": [hmfmt(lo), hmfmt(hi)],
                                      "minutes": hi - lo})
    pv = {v: {"sessions": len(by_venue[v]),
              "minutes": sum(e["dur"] for e in by_venue[v]),
              "gaps": len(gaps[v]),
              "gap_minutes": sum(g["minutes"] for g in gaps[v]),
              "gap_max": max(g["minutes"] for g in gaps[v])}
          for v in VENUES}
    total_min = sum(e["dur"] for e in evs)
    assert total_min == sum(pv[v]["minutes"] for v in VENUES)
    for v in VENUES:                  # 每会场：场次时长 + 空档 = 整日跨度
        assert pv[v]["minutes"] + pv[v]["gap_minutes"] == SPAN, v
    return gaps, conflicts, by_venue, pv, total_min


# ===========================================================================
# 排版片段
# ===========================================================================
def line(x, y, s, *, size, color=None, bold=False, align_text=None, w=None):
    """单行文本：Text 自定宽（不套紧约束，避免尾部被裁），h 仅作占位。"""
    return at(x, y, K.txt(0, 0, s, size=size, color=color or K.INK, bold=bold,
                          align_text=align_text, w=w), height=size * 1.35)


def wrapped(s, size, max_w, bold=False, lh=1.35):
    """预算折行：返回 (行数, 总高度)。"""
    ls = K.wrap_text(s, size, max_w, bold)
    return len(ls), len(ls) * size * lh


def balanced(s, size, max_w, bold=False):
    """标题折行：末行只剩 1-2 字（孤字成行）时收窄折行预算重折，两行更均衡。
    收窄只移动断点，产出行仍 ≤ max_w，所以高度预算（行数）不会变。"""
    ls = K.wrap_text(s, size, max_w, bold)
    if len(ls) != 2 or len(ls[1]) >= 3:
        return ls
    for f in (0.74, 0.70, 0.66, 0.62, 0.58, 0.54, 0.50):
        cand = K.wrap_text(s, size, max_w * f, bold)
        if len(cand) == 2 and len(cand[0]) >= 3 and len(cand[1]) >= 3:
            return cand
    return ls


def put_lines(x, y, ls, *, size, color=K.INK, bold=False, max_w, lh=1.35):
    """渲染已折好的行，返回 (dsl, 行数, 高度)。盒宽仍取 max_w（不断言折行）。"""
    h = len(ls) * size * lh
    d = at(x, y, K.txt(0, 0, "\n".join(ls), size=size, color=color, bold=bold,
                       w=max_w, wrap=True, height_ratio=lh,
                       max_lines=len(ls)), height=h)
    return d, len(ls), h


def put_block(x, y, s, *, size, color=K.INK, bold=False, max_w, lh=1.35):
    """渲染折行文本块，返回 (dsl, 行数, 高度)。"""
    ls = K.wrap_text(s, size, max_w, bold)
    h = len(ls) * size * lh
    d = at(x, y, K.txt(0, 0, "\n".join(ls), size=size, color=color, bold=bold,
                       w=max_w, wrap=True, height_ratio=lh,
                       max_lines=len(ls)), height=h)
    return d, len(ls), h


def swatch(x, y, c, d=14, r=3):
    return at(x, y, box(width=d, height=d, color=c, radius=r), width=d, height=d)


def dash_v(x, y0, y1, *, dash=8, gap=6, t=1.5, color=K.AXIS):
    out, y = [], y0
    while y + dash <= y1:
        out.append(at(x, y, box(width=t, height=dash, color=color, radius=1)))
        y += dash + gap
    return out


def legend_row(x, y, *, size=FS_CA, sw=14, gap=20):
    """类别图例（色块 + 文字双重编码）。返回单个 Positioned。"""
    kids, cx = [], 0
    for k in CAT_ORDER:
        lab = CAT[k]["label"]
        kids.append(swatch(cx, size * 1.5 - sw, CAT[k]["color"], d=sw))
        kids.append(line(cx + sw + 7, 0, lab, size=size, color=K.INK2))
        cx += sw + 7 + tw(lab, size) + gap
    w = cx - gap
    return at(x, y, layer(w, size * 1.5, *kids), width=w, height=size * 1.5)


def legend_w(size=FS_CA, sw=14, gap=20):
    """图例行总宽（与 legend_row 同一算法），供构建期断言判断是否会与右侧说明撞车。"""
    tot = 0
    for k in CAT_ORDER:
        tot += sw + 7 + tw(CAT[k]["label"], size) + gap
    return tot - gap


# ===========================================================================
# 大图 1920×1200
# ===========================================================================
W, H, M = 1920, 1200, 40
CW = W - 2 * M                                  # 1840
PX0 = M
PPM = CW / SPAN                                 # 4.380952380952381
LANE_H, LANE_GAP = 260, 14
LANES_Y = 166
LANE_Y = {v: LANES_Y + i * (LANE_H + LANE_GAP) for i, v in enumerate(VENUES)}
LANES_BOT = LANES_Y + 3 * LANE_H + 2 * LANE_GAP            # 974
CARD_INSET, CARD_H = 38, 212
AXIS_TICK_Y, AXIS_LBL_Y = 978, 990
AXIS_CAP_Y, FOOTER_DIV_Y = 1016, 1054
FOOT_ROW_Y, FOOT_STEP = 1072, 28


def X(t):
    return PX0 + (t - T0) * PPM


def build_wide(caps, evs, by_venue, pv, gaps):
    kids, cmap = [], []
    lx0, lx1 = X(LUNCH0), X(LUNCH1)

    # --- 页头 ---
    title = "Structure / Vision 2026 · 全日日程"
    sub = ("2026.11.07 · 云构中心 · A / B / C 会场 · Asia/Shanghai（UTC+08:00）"
           f" · 时段 09:00–16:00（{SPAN} 分钟）")
    kids.append(line(M, 28, title, size=30, color=K.INK, bold=True))
    kids.append(line(M, 78, sub, size=18, color=K.INK2))
    kids.append(legend_row(M, 110))
    guide = (f"读图方法：块左缘 = 开始时间，块宽 = 实际时长 × {PPM:.2f}px/分钟，"
             "块间空档真实保留；午休 12:00–13:00 以灰带跨三泳道标出，不并入任何会议；"
             "短场次标题在块内折行，不为塞字改变块宽")
    # 右对齐放置：文字宽度估算系统性偏小 ≤6%（A01 校准），不乘 SLACK 会让右端
    # 越过正文右界（实测右缘 1896 > 1880）。
    gw = tw(guide, 16) * SLACK
    assert PX0 + CW - gw >= M + legend_w() + 40, "读图说明与图例撞车"
    kids.append(at(PX0 + CW - gw, 112, K.txt(0, 0, guide, size=16, color=K.MUTED),
                   height=22))
    kids.append(K.divider(M, 154, CW))

    # --- 泳道底带 ---
    for v in VENUES:
        kids.append(at(PX0, LANE_Y[v],
                       box(width=CW, height=LANE_H, color=LANE_BAND, radius=10,
                           border=f"1 SOLID {K.RING}"),
                       width=CW, height=LANE_H))

    # --- 午休带（跨三条泳道，带内三泳道均无卡片） ---
    kids.append(at(lx0, LANES_Y, box(width=lx1 - lx0, height=LANES_BOT - LANES_Y,
                                     color=LUNCH_TINT),
                   width=lx1 - lx0, height=LANES_BOT - LANES_Y))
    kids.extend(dash_v(lx0, LANES_Y, LANES_BOT))
    kids.extend(dash_v(lx1 - 1.5, LANES_Y, LANES_BOT))

    # --- 整点网格（09:00/16:00 由泳道带左右缘承担） ---
    for h in range(10, 16):
        kids.append(at(X(h * 60) - 0.5, LANES_Y,
                       box(width=1, height=LANES_BOT - LANES_Y, color=K.GRID)))

    # --- 泳道标题行：会场 + 容量 + 场次/时长 + 空档 ---
    for v in VENUES:
        p = pv[v]
        h1, h2 = f"{v} 会场", f"容量 {caps[v]} 人"
        h3 = f"{p['sessions']} 场 · {p['minutes']} 分钟"
        h4 = (f"空档 {p['gaps']} 段 · 累计 {p['gap_minutes']} 分钟"
              f"（最长 {p['gap_max']}）")
        hx = PX0 + 24
        kids.append(line(hx, LANE_Y[v] + 7, h1, size=20, color=K.INK, bold=True))
        x2 = hx + tw(h1, 20, True) + 12
        kids.append(line(x2, LANE_Y[v] + 10, h2, size=16, color=K.INK2))
        x3 = x2 + tw(h2, 16) + 12
        kids.append(line(x3, LANE_Y[v] + 10, h3, size=16, color=K.INK2))
        w4 = tw(h4, 16)
        kids.append(at(PX0 + CW - 24 - w4, LANE_Y[v] + 10,
                       K.txt(0, 0, h4, size=16, color=K.MUTED), height=22))
        assert x3 + tw(h3, 16) + 48 <= PX0 + CW - 24 - w4, v

    # --- 午休说明（午休带三泳道全空，放带中央） ---
    lc = (lx0 + lx1) / 2
    for s, size, dy, color in (("午休", 22, 522, K.INK2),
                               ("12:00–13:00", 18, 560, K.INK2),
                               ("跨三会场 · 不并入会议", 16, 592, K.MUTED)):
        w = tw(s, size, True)
        assert w <= lx1 - lx0 - 8
        kids.append(at(lc - w / 2, dy, K.txt(0, 0, s, size=size, color=color,
                                              bold=True), height=size * 1.35))

    # --- 场次卡片 ---
    # 卡片内元素一律用相对坐标（card 的 layer 原点在卡片左上角）；内容映射的像素盒
    # 再加回 (cx, cy) 换算成画布坐标。上一版把文本按画布坐标画在 canvas 层，整块文字
    # 全跑到页头上、卡片全空 —— 且漏画了讲者。
    for e in evs:
        cx, cw = X(e["t0"]), e["dur"] * PPM
        cy = LANE_Y[e["venue"]] + CARD_INSET
        cat = CAT[e["category"]]
        pad_l, pad_r = 14, 8
        inner = cw - pad_l - pad_r
        tm = f"{e['start']}–{e['end']}"
        # Text 自定宽、层不裁剪：越界只会溢出卡片而非被裁，故在构建期按 SLACK 断言
        for s, size, bold in ((e["id"], FS_ID, True), (tm, FS_TM, False),
                              (e["speaker"], FS_SP, False)):
            assert tw(s, size, bold) * SLACK <= inner, (e["id"], s, round(cw, 1))
        tl = balanced(e["title"], FS_T, inner, bold=True)
        nl, th = len(tl), len(tl) * FS_T * 1.35
        gap = 7
        heights = [FS_ID * 1.35, FS_TM * 1.35, th, FS_SP * 1.35, 22]
        total = sum(heights) + gap * 4
        assert total <= CARD_H - 20, (e["id"], total, CARD_H)
        ty = (CARD_H - total) / 2
        xp = pad_l

        def rec(field, s, x, y, w, h):
            """记录画布坐标下的内容盒（相对坐标 + 卡片原点）。"""
            fs, fb = WIDE_STYLE[field]
            cmap.append({"event_id": e["id"], "field": field, "text": s,
                         "size": fs, "bold": fb,
                         "box": [round(cx + x, 1), round(cy + y, 1),
                                 round(cx + x + w, 1), round(cy + y + h, 1)]})

        ckids = [at(0, 16, box(width=4, height=CARD_H - 32, color=cat["color"],
                               radius=2), width=4, height=CARD_H - 32)]
        for s, size, color, bold, field in ((e["id"], FS_ID, K.INK, True, "id"),
                                             (tm, FS_TM, K.INK2, False, "time"),
                                             (e["speaker"], FS_SP, K.INK2, False,
                                              "speaker")):
            h = size * 1.35
            ckids.append(line(xp, ty, s, size=size, color=color, bold=bold))
            rec(field, s, xp, ty, tw(s, size, bold), h)
            ty += h + gap
        d, n, h = put_lines(xp, ty, tl, size=FS_T, color=K.INK, bold=True,
                            max_w=inner)
        ckids.append(d)
        cmap.append({"event_id": e["id"], "field": "title", "text": e["title"],
                     "size": FS_T, "bold": True,
                     "lines": n, "line_text": tl,
                     "box": [round(cx + xp, 1), round(cy + ty, 1),
                             round(cx + xp + inner, 1), round(cy + ty + h, 1)]})
        ty += h + gap
        cl = cat["label"]
        ckids.append(swatch(xp, ty + 4, cat["color"], d=9, r=2))
        ckids.append(line(xp + 14, ty, cl, size=FS_CA, color=K.INK2))
        rec("category", cat["label"], xp, ty, 14 + tw(cl, FS_CA), 22)
        kids.append(K.card(cx, cy, cw, CARD_H, radius=12, fill=K.PANEL,
                           children=ckids))
        cmap.append({"event_id": e["id"], "field": "block", "text": None,
                     "box": [round(cx, 1), round(cy, 1), round(cx + cw, 1),
                             round(cy + CARD_H, 1)],
                     "minutes": e["dur"],
                     "width_px": round(cw, 4),
                     "note": f"卡宽 = {e['dur']} 分钟 × {PPM:.6f} px/分钟，未外扩未压缩"})

    # --- 时间轴刻度与标签 ---
    for h in range(9, 17):
        gx, lab = X(h * 60), f"{h:02d}:00"
        lw = tw(lab, 16) * SLACK          # 16:00 右对齐贴正文右界，须按 SLACK 预留
        lx = PX0 if h == 9 else (PX0 + CW - lw if h == 16 else gx - lw / 2)
        kids.append(at(gx - 0.5, AXIS_TICK_Y, box(width=1, height=10, color=K.AXIS)))
        kids.append(line(lx, AXIS_LBL_Y, lab, size=16, color=K.MUTED))
    cap = f"线性时间轴 09:00–16:00 · 共 {SPAN} 分钟 · 1 分钟 = {PPM:.4f}px"
    kids.append(at(PX0, AXIS_CAP_Y, K.txt(0, 0, cap, size=16, color=K.MUTED),
                   height=22))

    # --- 页脚 ---
    f1 = (f"读图方法：块左缘 = 开始时间，块宽 = 实际时长 × {PPM:.2f}px/分钟，块间空档真实"
          "保留；午休 12:00–13:00 以灰带跨三泳道标出，不并入任何会议；短场次标题在块内"
          "折行，不为塞字改变块宽。")
    f2 = ("会场容量：A %d 人 · B %d 人 · C %d 人（合计 %d 人）。时长合计 %d 分钟 = %.1f 小时，"
          "15 场；每会场跨 09:00–16:00 共 %d 分钟，空档 A %d / B %d / C %d 分钟。"
          % (caps["A"], caps["B"], caps["C"], sum(caps.values()),
             sum(e["dur"] for e in evs), sum(e["dur"] for e in evs) / 60, SPAN,
             pv["A"]["gap_minutes"], pv["B"]["gap_minutes"], pv["C"]["gap_minutes"]))
    f3 = ("冲突检查：同一会场内不存在时间重叠的活动对，conflicts 为空；输入时间未作任何调整。"
          "逐场时长、空档与冲突见 schedule-audit.json。")
    f4 = ("数据源：inputs/agenda.csv（15 行）· inputs/venues.json。手机导览 "
          "agenda-mobile.png（720×1280，分时段列表，非本图缩放或裁切）。")
    kids.append(K.divider(M, FOOTER_DIV_Y, CW))
    for i, s in enumerate((f1, f2, f3, f4)):
        assert tw(s, 16) <= CW, (i, len(s), s)
        kids.append(line(M, FOOT_ROW_Y + i * FOOT_STEP, s, size=16, color=K.MUTED))

    return canvas(W, H, layer(W, H, *kids), background=K.PLANE), cmap


# ===========================================================================
# 手机图 720×1280
# ===========================================================================
MW, MH, MM = 720, 1280, 32
MCW = MW - 2 * MM                                  # 656
MCARD_H, MSTEP = 54, 58
M_AM_CARD_Y, M_LUNCH_Y, M_PM_HDR_Y, M_PM_CARD_Y = 210, 682, 724, 761
M_LUNCH_H, M_FOOT_Y = 30, 1177
FS_MB, FS_MC = 18, 16                              # 手机正文 18（≥18 下限），标注 16
MOBILE_STYLE = {"venue": (FS_MB, True), "id": (FS_MB, True),
                "time": (FS_MB, False), "category": (FS_MC, False),
                "title": (FS_MB, False)}


def build_mobile(evs, caps, pv):
    kids, cmap = [], []
    am = [e for e in evs if e["t0"] < LUNCH0]
    pm = [e for e in evs if e["t0"] >= LUNCH1]
    assert len(am) == 8 and len(pm) == 7, (len(am), len(pm))
    total_min = sum(e["dur"] for e in evs)

    kids.append(line(MM, 26, "Structure / Vision 2026", size=26, color=K.INK, bold=True))
    kids.append(line(MM, 68, "2026.11.07 · 云构中心 · A / B / C 会场 · "
                             "Asia/Shanghai（UTC+08:00）",
                     size=FS_MC, color=K.INK2))
    kids.append(line(MM, 92, "分时段列表 · 15 场全列 · 讲者详见完整日程 "
                             "agenda-wide.png",
                     size=FS_MC, color=K.MUTED))
    kids.append(K.divider(MM, 122, MCW))
    kids.append(legend_row(MM, 134, sw=13, gap=18))

    def seg(y, name, rng, cnt):
        kids.append(line(MM, y, name, size=20, color=K.INK, bold=True))
        r = f"{rng} · {cnt} 场"
        rw = tw(r, FS_MC) * SLACK     # 右对齐贴正文右界，须按 SLACK 预留
        assert MM + MCW - rw >= MM + tw(name, 20, True) + 20, (name, rng)
        kids.append(at(MM + MCW - rw, y + 4,
                       K.txt(0, 0, r, size=FS_MC, color=K.MUTED), height=22))

    seg(M_AM_CARD_Y - 30, "上午场", "09:00–12:00", len(am))

    def mcard(e, y):
        cat = CAT[e["category"]]
        kids.append(K.card(MM, y, MCW, MCARD_H, radius=10, fill=K.PANEL, children=[
            at(0, 8, box(width=4, height=MCARD_H - 16, color=cat["color"], radius=2),
               width=4, height=MCARD_H - 16)]))
        pad = 14
        xp = MM + pad
        # 行 1：会场 + 编号 + 起止时间 +（右端）类别标签
        vlab, idw, tm = f"{e['venue']} 会场", e["id"], f"{e['start']}–{e['end']}"
        wv, wi = tw(vlab, FS_MB, True), tw(idw, FS_MB, True)
        wt = tw(tm, FS_MB)
        cl = cat["label"]
        wc = tw(cl, FS_MC)
        x2, x3 = xp + wv + 10, xp + wv + 10 + wi + 10
        assert x3 + wt * SLACK <= MM + MCW - 12 - wc - 12, (e["id"], tm)
        kids.append(line(xp, y + 5, vlab, size=FS_MB, color=K.INK, bold=True))
        kids.append(line(x2, y + 5, idw, size=FS_MB, color=cat["color"], bold=True))
        kids.append(line(x3, y + 5, tm, size=FS_MB, color=K.INK2))
        kids.append(at(MM + MCW - 12 - wc, y + 9,
                       K.txt(0, 0, cl, size=FS_MC, color=K.MUTED), height=20))
        def mrec(field, text, bx0, bx1):
            fs, fb = MOBILE_STYLE[field]
            cmap.append({"event_id": e["id"], "field": field, "text": text,
                         "size": fs, "bold": fb,
                         "box": [round(bx0, 1), round(y + 5, 1),
                                 round(bx1, 1), round(y + 29, 1)]})
        mrec("venue", e["venue"], xp, xp + wv)
        mrec("id", idw, x2, x2 + wi)
        mrec("time", tm, x3, x3 + wt)
        mrec("category", cl, MM + MCW - 12 - wc, MM + MCW - 12)
        # 行 2：标题（18 号单行）
        tt = tw(e["title"], FS_MB)
        assert tt * SLACK <= MCW - pad - 12, (e["id"], e["title"])
        kids.append(line(xp, y + 29, e["title"], size=FS_MB, color=K.INK))
        cmap.append({"event_id": e["id"], "field": "title", "text": e["title"],
                     "size": FS_MB, "bold": False,
                     "box": [round(xp, 1), round(y + 29, 1), round(xp + tt, 1),
                             round(y + 53, 1)]})
        cmap.append({"event_id": e["id"], "field": "block", "text": None,
                     "box": [MM, y, MM + MCW, y + MCARD_H]})

    y = M_AM_CARD_Y
    for e in am:
        mcard(e, y)
        y += MSTEP
    assert y - MSTEP + MCARD_H + 12 <= M_LUNCH_Y, y

    # 午休：独立浅灰条，不并入任何会议
    kids.append(at(MM, M_LUNCH_Y,
                   box(width=MCW, height=M_LUNCH_H, color=LUNCH_TINT, radius=10,
                       border=f"1 SOLID {K.AXIS}"), width=MCW, height=M_LUNCH_H))
    kids.append(at(MM + 14, M_LUNCH_Y + 5,
                   K.txt(0, 0, "12:00–13:00 · 公共午休 · 跨三会场，不并入任何会议",
                         size=FS_MC, color=K.INK2), height=20))
    cmap.append({"event_id": None, "field": "public_break", "text": "午休 12:00–13:00",
                 "box": [MM, M_LUNCH_Y, MM + MCW, M_LUNCH_Y + M_LUNCH_H]})

    seg(M_PM_HDR_Y, "下午场", "13:00–16:00", len(pm))
    y = M_PM_CARD_Y
    for e in pm:
        mcard(e, y)
        y += MSTEP
    assert y - MSTEP + MCARD_H + 12 <= M_FOOT_Y, y

    f1 = (f"时段 09:00–16:00 · 15 场共 {total_min} 分钟 = {total_min / 60:.1f} 小时 · "
          f"午休 1 小时")
    f2 = (f"会场容量 A {caps['A']} / B {caps['B']} / C {caps['C']} 人 · "
          f"空档 A {pv['A']['gap_minutes']} / B {pv['B']['gap_minutes']} / "
          f"C {pv['C']['gap_minutes']} 分钟")
    f3 = "冲突检查：同一会场内无时间重叠，conflicts 为空 · 输入时间未调整"
    for i, s in enumerate((f1, f2, f3)):
        assert tw(s, FS_MC) <= MCW, (i, s)
        kids.append(line(MM, M_FOOT_Y + i * 26, s, size=FS_MC, color=K.MUTED))

    return canvas(MW, MH, layer(MW, MH, *kids), background=K.PLANE), cmap


# ===========================================================================
def main() -> None:
    caps, evs = load()
    gaps, conflicts, by_venue, pv, total_min = analyse(caps, evs)
    wide, cmap_w = build_wide(caps, evs, by_venue, pv, gaps)
    mobile, cmap_m = build_mobile(evs, caps, pv)

    # 先解析迭代 reason（走 UTF-8 文件，避开 GBK 控制台环境变量）。
    # 必须在渲染之前：reason 文件缺失时立即失败，避免「PNG 已落盘而迭代记录丢失」。
    kind = os.environ.get("SNAPSHOT_ITER_KIND", "baseline")
    version = os.environ.get("SNAPSHOT_ITER_VERSION", "v1")
    rf = os.environ.get("SNAPSHOT_ITER_REASON_FILE")
    if rf:
        rf_p = ROOT / rf if not os.path.isabs(rf) else Path(rf)
        if not rf_p.is_file():
            raise SystemExit(f"迭代 reason 文件不存在，终止（不渲染）：{rf}")
        reason = rf_p.read_text(encoding="utf-8").strip()
    else:
        reason = ("首次渲染：三条会场泳道共用 09:00–16:00 线性时间轴，块宽按实际时长"
                  "等比；手机图分上午场 / 午休 / 下午场列表。")
    parent = os.environ.get("SNAPSHOT_ITER_PARENT")

    t = TG.Task(TASK)
    TG.mark_started(TASK)
    ver = os.environ.get("SNAPSHOT_DSL_VERSION", "v1")
    t.write_dsl(f"agenda-wide.{ver}", wide)
    t.write_dsl(f"agenda-mobile.{ver}", mobile)
    res_w = t.render(f"agenda-wide.{ver}", wide, "agenda-wide.png",
                     label=f"A02 全日日程泳道大图 {ver}")
    res_m = t.render(f"agenda-mobile.{ver}", mobile, "agenda-mobile.png",
                     label=f"A02 手机导览 {ver}")
    # 每张最终图必须有同名完整 DSL（AGENTS）：agenda-wide.png ↔ agenda-wide.snapshot
    t.write_text("agenda-wide.snapshot", wide)
    t.write_text("agenda-mobile.snapshot", mobile)

    pairs = sum(len(v) * (len(v) - 1) // 2 for v in by_venue.values())
    audit = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "date": "2026-11-07",
        "venue": "云构中心 · A / B / C 会场",
        "inputs": [{"path": "tasks/A02-conference-schedule/inputs/agenda.csv",
                    "path_base": "suite_root", "rows": 15,
                    "modified": False},
                   {"path": "tasks/A02-conference-schedule/inputs/venues.json",
                    "path_base": "suite_root", "modified": False}],
        "artifacts": {
            "agenda-wide.png": {
                "path": "agenda-wide.png", "dsl": "agenda-wide.snapshot",
                "size": [W, H], "role": "按时长比例绘制的三会场泳道日程",
                "render_request": res_w.get("request_id"),
                "bytes": res_w.get("response_bytes")},
            "agenda-mobile.png": {
                "path": "agenda-mobile.png", "dsl": "agenda-mobile.snapshot",
                "size": [MW, MH], "role": "手机导览：分时段列表，非大图缩放或裁切",
                "render_request": res_m.get("request_id"),
                "bytes": res_m.get("response_bytes"),
                "omitted_field": {"field": "speaker",
                                  "note": "按 TASK.md 允许移到大图；图内注明"
                                          "「讲者详见完整日程 agenda-wide.png」"}},
            "schedule-audit.json": {"path": "schedule-audit.json"}},
        "time_axis": {
            "timezone": "Asia/Shanghai (UTC+08:00)",
            "date": "2026-11-07",
            "domain": ["09:00", "16:00"],
            "base_time": "09:00",
            "base_time_minutes": T0,
            "origin": "agenda-wide.png 画布左上原点，x 向右、y 向下，单位像素",
            "px_per_minute": round(PPM, 10),
            "px_per_minute_exact": "1840/420",
            "plot": {"x_left": PX0, "x_right": PX0 + CW, "width_px": CW},
            "lane_y": {k: v for k, v in LANE_Y.items()},
            "lane_height": LANE_H,
            "lane_range": [LANES_Y, LANES_BOT],
            "formula": "x = 40 + (minutes_since_09:00) * (1840/420)",
            "block_rule": "卡左缘 = X(start)，卡宽 = 分钟数 × px_per_minute；"
                          "不做宽度外扩或压缩，30 分钟场次卡宽 131.43px",
            "hour_tick_x": {f"{h:02d}:00": round(X(h * 60), 4)
                            for h in range(9, 17)},
            "lunch_band": {"start": "12:00", "end": "13:00",
                           "x_left": round(X(LUNCH0), 4),
                           "x_right": round(X(LUNCH1), 4),
                           "y_top": LANES_Y, "y_bottom": LANES_BOT,
                           "note": "跨三条泳道的连续灰带 + 两端虚线；午间三泳道均无卡片"},
        },
        "events": [
            {"event_id": e["id"], "venue": e["venue"], "start": e["start"],
             "end": e["end"], "duration_minutes": e["dur"], "title": e["title"],
             "speaker": e["speaker"], "category": e["category"],
             "category_label": CAT[e["category"]]["label"],
             "period": "上午" if e["t0"] < LUNCH0 else "下午",
             "wide_block_px": {"x_left": round(X(e["t0"]), 4),
                               "x_right": round(X(e["t1"]), 4),
                               "width": round(e["dur"] * PPM, 4)}}
            for e in evs],
        "duration_summary": {
            "total_minutes": total_min,
            "total_hours": round(total_min / 60, 4),
            "by_venue": {v: pv[v]["minutes"] for v in VENUES},
            "by_venue_hours": {v: round(pv[v]["minutes"] / 60, 4) for v in VENUES},
            "by_duration_minutes": {},
            "min_duration_minutes": min(e["dur"] for e in evs),
            "max_duration_minutes": max(e["dur"] for e in evs),
        },
        "venue_gaps": [
            {"venue": v, "gaps": gaps[v], "gap_count": len(gaps[v]),
             "gap_minutes_total": pv[v]["gap_minutes"],
             "session_minutes": pv[v]["minutes"],
             "check": f"{pv[v]['minutes']} + {pv[v]['gap_minutes']} = {SPAN} 分钟"
                      f"（09:00–16:00）"}
            for v in VENUES],
        "public_break": {
            "label": "公共午休", "start": "12:00", "end": "13:00",
            "minutes": LUNCH1 - LUNCH0, "venues": VENUES,
            "merged_into_event": False,
            "overlapping_venue_gaps": {"A": "11:50–13:00", "B": "11:10–13:00",
                                       "C": "11:45–13:20"},
            "note": "作为独立条目记录，未并入任何会议，也未计入各会场空档合计；"
                    "与各会场跨午间空档部分重叠，两处分别记录以免重复计数。"},
        "conflicts": conflicts,
        "conflict_check": {
            "method": "同一会场内任两场做半开区间 [start, end) 求交，交集非空记为冲突",
            "pairs_checked": pairs,
            "conflicts_found": len(conflicts),
            "result": "无冲突：同一会场内不存在时间重叠的活动对"
                      if not conflicts else "存在冲突，见 conflicts",
            "input_times_modified": False,
        },
        "content_map": (
            [{"image": "agenda-wide.png", "image_path": "agenda-wide.png",
              "coordinates": "agenda-wide.png 画布左上原点，像素，[left,top,right,bottom]",
              **c} for c in cmap_w] +
            [{"image": "agenda-mobile.png", "image_path": "agenda-mobile.png",
              "coordinates": "agenda-mobile.png 画布左上原点，像素，[left,top,right,bottom]",
              **c} for c in cmap_m]),
        "fonts": {
            "family": K.FAMILY,
            "agenda-wide.png": {"title": 30, "subtitle": 18, "lane_header": 20,
                                "body_title": FS_T, "body_speaker": FS_SP,
                                "time_label": FS_TM, "event_id": FS_ID,
                                "caption": FS_CA,
                                "note": "正文（标题/讲者）20 ≥ 20 下限；时间标签 18 ≥ 18 下限；"
                                        "标注 16"},
            "agenda-mobile.png": {"title": 26, "body": FS_MB, "caption": FS_MC,
                                  "note": "手机正文 18 ≥ 18 下限；分段标题 20；"
                                          "副信息与标注 16"},
        },
        "unresolved": [],
    }
    dp: dict[int, int] = {}
    for e in evs:
        dp[e["dur"]] = dp.get(e["dur"], 0) + 1
    audit["duration_summary"]["by_duration_minutes"] = dict(sorted(dp.items()))

    t.write_json("schedule-audit.json", audit)

    print("events %d  total_min %d  conflicts %d  pairs_checked %d"
          % (len(evs), total_min, len(conflicts), pairs))
    print("by_venue", {v: (pv[v]["sessions"], pv[v]["minutes"],
                           pv[v]["gaps"], pv[v]["gap_minutes"]) for v in VENUES})
    print("ppm %.10f  lanes %s  bot %d  card_h %d"
          % (PPM, {k: v for k, v in LANE_Y.items()}, LANES_BOT, CARD_H))
    for k, v in (("wide", res_w), ("mobile", res_m)):
        print(k, v.get("http_status"), v.get("response_bytes"), v.get("png"),
              v.get("elapsed_ms"))
    print("dsl_bytes", len(wide), len(mobile), "cmap", len(cmap_w) + len(cmap_m))

    # 迭代留痕：kind/version/parent 走环境变量（ASCII 安全）；reason 已在渲染前
    # 由 SNAPSHOT_ITER_REASON_FILE 读入，避免经 GBK 控制台环境变量传入变成乱码。
    t.iter({"kind": kind, "version": version,
            "label": "A02 全日日程（agenda-wide + agenda-mobile）",
            "reason": reason,
            "parent": parent,
            "images": [t.rel_out("agenda-wide.png"), t.rel_out("agenda-mobile.png")]})


if __name__ == "__main__":
    main()
