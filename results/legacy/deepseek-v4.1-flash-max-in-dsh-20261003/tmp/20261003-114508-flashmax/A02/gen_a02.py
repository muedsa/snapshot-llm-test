"""A02 DSL generators: wide swimlane schedule (1920x1200) + mobile guide (720x1280)."""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A02"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
A = json.load(open(os.path.join(OUT, "schedule-audit.json"), encoding="utf-8"))
S = A["sessions"]
DAY0, DAY1 = 540, 960
CAT = A["totals"]["by_category"]

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, CARD, BG, NAVY = "#E2E8F0FF", "#FFFFFFFF", "#F1F5F9FF", "#0F172AFF"
TEAL, BLUE, AMBER, PURPLE, ROSE, SLATE = ("#0E9F8FFF", "#2563EBFF", "#D97706FF",
                                          "#7C3AEDFF", "#DB2777FF", "#475569FF")
CAT_STYLE = {
    "keynote": (ROSE, "#FFF1F2FF", "主旨"),
    "workshop": (AMBER, "#FFFBEBFF", "工作坊"),
    "talk": (TEAL, "#ECFDF5FF", "分享"),
    "demo": (PURPLE, "#F5F3FFFF", "演示"),
    "panel": (BLUE, "#EFF6FFFF", "圆桌"),
}


class Doc:
    def __init__(self, w, h, bg=BG):
        self.p = [f'<Snapshot background="{bg}" type="png">',
                  f'<Container width="{w}" height="{h}">',
                  '<Stack alignment="TOP_LEFT" fit="EXPAND">']

    def box(self, x, y, w, h, color, radius=None, border=None, shadow=None):
        a = f'<Container width="{w}" height="{h}" color="{color}"'
        if radius:
            if isinstance(radius, (int, float)):
                a += f' borderRadius="{radius}"'
            else:
                side, val = radius
                if side == "top":
                    a += f' borderRadiusTopLeft="{val}" borderRadiusTopRight="{val}"'
                elif side == "bottom":
                    a += f' borderRadiusBottomLeft="{val}" borderRadiusBottomRight="{val}"'
                else:
                    a += (f' borderRadiusTopLeft="{val}" borderRadiusBottomLeft="{val}" '
                          f'borderRadiusTopRight="{val}" borderRadiusBottomRight="{val}"')
        if border:
            a += f' border="{border}"'
        if shadow:
            a += f' boxShadow="{shadow}"'
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def bar(self, x, y, w, h, color, tl=0, tr=0, bl=0, br=0):
        a = f'<Container width="{w}" height="{h}" color="{color}"'
        for name, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
            if v:
                a += f' borderRadius{name}="{v}"'
        self.p.append(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')
        return self

    def text(self, x, y, s, size, color, weight="NORMAL", family=CJ, w=None,
             align=None, spacing=None):
        a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
        if spacing:
            a += f' letterSpacing="{spacing}"'
        body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if w:
            self.p.append(f'<Positioned left="{x}" top="{y}" width="{w}">'
                          f'<Container alignment="{align or "CENTER_LEFT"}">'
                          f'<Text {a}>{body}</Text></Container></Positioned>')
        else:
            self.p.append(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')
        return self

    def seg(self, x0, y0, x1, y1, color, th):
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        m11, m12 = math.cos(ang), math.sin(ang)
        m21, m22 = -m12, m11
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        tx = mx - m11 * (length / 2) - m21 * (th / 2)
        ty = my - m12 * (length / 2) - m22 * (th / 2)
        mat = f"(1,0,0,0,0,1,0,0,0,0,1,0,{tx:.3f},{ty:.3f},0,1)"
        self.p.append(f'<Positioned left="0" top="0"><Transform matrix="{mat}">'
                      f'<Container width="{length:.2f}" height="{th}" color="{color}" '
                      f'borderRadius="{th/2}"/></Transform></Positioned>')
        return self

    def done(self):
        self.p += ['</Stack>', '</Container>', '</Snapshot>']
        return "\n".join(self.p) + "\n"


def fit(title: str, size: float, maxw: float) -> str:
    """Truncate a CJK/Latin mixed string to maxw px using the measured metrics."""
    def width(s: str) -> float:
        t = 0.0
        for ch in s:
            t += size * (1.0 if ord(ch) > 0x2E80 else 0.55)
        return t
    if width(title) <= maxw:
        return title
    out = ""
    for ch in title:
        if width(out + ch + "…") > maxw:
            break
        out += ch
    return out + "…"


# ==================================================================================
# WIDE 1920x1200
# ==================================================================================
W, H = 1920, 1200
PLOT_L, PLOT_W = 140, 1690
PPM = PLOT_W / (DAY1 - DAY0)
LANE_X, LANE_W = 40, 1804
LANE_Y0, LANE_H, LANE_GAP = 198, 72, 8
LANE_TOP, LANE_BOT = LANE_Y0, LANE_Y0 + 3 * LANE_H + 2 * LANE_GAP
BLOCK_INSET = 4


def xof(minute: int) -> float:
    return PLOT_L + (minute - DAY0) * PPM


d = Doc(W, H)
# ---- header ----
d.box(0, 0, W, 116, NAVY)
d.box(0, 0, 8, 116, TEAL)
d.text(44, 16, "Structure / Vision 2026 · 全日日程", 38, "#FFFFFFFF", "BOLD")
d.text(44, 68, "2026.11.07（星期六）· 云构中心 · A / B / C 会场 · 时间均为 Asia/Shanghai", 21, "#94A3B8FF")
d.text(1180, 18, "三会场 × 15 场活动", 21, "#5EEAD4FF", "BOLD", CJ, 696, "CENTER_RIGHT")
d.text(1180, 46, "09:00 — 16:00 · 共用线性时间轴 · 15 分钟刻度", 20, "#FFFFFFFF", "BOLD", MONO, 696, "CENTER_RIGHT")
d.text(1180, 80, "公共午休 12:00 — 13:00（跨三泳道，不与会议合并）", 20, "#FBBF24FF", "BOLD", CJ, 696, "CENTER_RIGHT")

# ---- how to read + legend (exactly one line each, so nothing wraps into the next row) ----
d.text(44, 110, "读图方法", 23, INK, "BOLD")
d.text(156, 114,
       "横轴 09:00—16:00 共 420 分钟；块左边缘 = 开始时间、块宽 = 时长，同一比例，输入时间未做任何调整；块内为编号，块上方一行是起止时间。",
       19, MUTED)
d.text(44, 140, "会场容量：A 320 人 · B 80 人 · C 160 人", 20, INK2, "BOLD")
lx = 470
for c in ("keynote", "workshop", "talk", "demo", "panel"):
    col, bgc, label = CAT_STYLE[c]
    d.bar(lx, 143, 15, 15, col, tl=4, tr=4, bl=4, br=4)
    d.text(lx + 22, 140, f"{label} ×{CAT[c]}", 20, INK2)
    lx += 112

# ---- timeline card ----
d.box(40, 166, 1804, 276, CARD, 16, f"1 SOLID {LINE}", "0 2 10 0 #0F172A14 NORMAL")
LX0, LX1 = round(xof(720)), round(xof(780))
d.text(1150, 452, "琥珀色横带 = 12:00 — 13:00 公共午休（跨三泳道，不并入任何会议）", 19, "#B45309FF", "BOLD", CJ, 694, "CENTER_RIGHT")

# time axis
for mm in range(DAY0, DAY1 + 1, 15):
    x = round(xof(mm))
    hour = (mm % 60 == 0)
    if hour:
        d.text(x - 40, 176, f"{mm//60:02d}:00", 19, INK, "BOLD", MONO, 80, "CENTER_LEFT")
    for lane in range(3):
        ly = LANE_Y0 + lane * (LANE_H + LANE_GAP)
        d.box(x, ly + 2, 1, LANE_H - 4, "#CBD5E1FF" if hour else "#EEF2F7FF")
# lane backgrounds + idle gaps
for i, v in enumerate(("A", "B", "C")):
    ly = LANE_Y0 + i * (LANE_H + LANE_GAP)
    d.box(LANE_X + 100, ly, LANE_W - 100, LANE_H, "#F8FAFCFF", 8)
    L = A["per_venue"][v]
    for g in L["gaps"]:
        gm0 = int(g["from"][:2]) * 60 + int(g["from"][3:])
        gm1 = int(g["to"][:2]) * 60 + int(g["to"][3:])
        if gm1 <= DAY0 or gm0 >= DAY1:
            continue
        gx0, gx1 = xof(max(gm0, DAY0)), xof(min(gm1, DAY1))
        d.box(round(gx0), ly + 2, round(gx1 - gx0), LANE_H - 4, "#E9EEF5FF", 5)
    d.text(LANE_X, ly + 8, f"{v} 会场", 25, INK, "BOLD")
    d.text(LANE_X, ly + 38, f"{L['capacity']} 人 · {L['session_count']} 场", 17, MUTED)

# lunch band across all lanes
lx0, lx1 = round(xof(720)), round(xof(780))
d.box(lx0, LANE_TOP + 2, lx1 - lx0, LANE_BOT - LANE_TOP - 4, "#FDE68A66")
d.seg(lx0, LANE_TOP + 2, lx1, LANE_TOP + 2, "#F59E0BFF", 4)

# session blocks
for s in S:
    i = {"A": 0, "B": 1, "C": 2}[s["venue"]]
    ly = LANE_Y0 + i * (LANE_H + LANE_GAP) + BLOCK_INSET
    bx0, bx1 = xof(s["start_min"]), xof(s["end_min"])
    bw = round(bx1 - bx0)
    col, bgc, label = CAT_STYLE[s["category"]]
    d.box(round(bx0), ly, bw, LANE_H - 2 * BLOCK_INSET, bgc, 6, f"2 SOLID {col}")
    d.bar(round(bx0), ly, 5, LANE_H - 2 * BLOCK_INSET, col, tl=6, bl=6)
    d.text(round(bx0) + 10, ly + 8, s["id"], 20, col, "BOLD", MONO)
    d.text(round(bx0) + 10, ly + 32, f"{s['start']}–{s['end']}", 18, INK, "BOLD", MONO)

# ---- index cards ----
d.text(44, 452, "活动索引 · 全部 15 项", 25, INK, "BOLD")
d.text(330, 459, "编号 · 标题 · 讲者 · 类别 · 起止时间与会场（短活动的文字空间由此解决）", 20, MUTED)
COLS, CW, CH, CGX, CGY = 5, 356, 202, 14, 12
GX0, GY0 = 40, 492
for idx, s in enumerate(S):
    r, c = divmod(idx, COLS)
    x = GX0 + c * (CW + CGX)
    y = GY0 + r * (CH + CGY)
    col, bgc, label = CAT_STYLE[s["category"]]
    d.box(x, y, CW, CH, CARD, 12, f"1 SOLID {LINE}", "0 2 6 0 #0F172A0F NORMAL")
    d.bar(x, y, CW, 5, col, tl=12, tr=12)
    d.text(x + 16, y + 18, s["id"], 24, col, "BOLD", MONO)
    d.text(x + 88, y + 18, label, 18, col, "BOLD", CJ, 100, "CENTER_LEFT")
    d.text(x + CW - 110, y + 18, f"{s['venue']} 会场", 18, MUTED, "BOLD", CJ, 94, "CENTER_RIGHT")
    d.text(x + 16, y + 56, fit(s["title"], 21, CW - 32), 21, INK, "BOLD")
    d.text(x + 16, y + 94, fit(s["speaker"], 19, CW - 32), 19, INK2)
    d.text(x + 16, y + 128, f"{s['start']} — {s['end']}", 20, INK, "BOLD", MONO)
    d.text(x + 16, y + 160, f"时长 {s['duration_min']} 分钟 · {label}", 18, MUTED)

# ---- footer ----
d.box(40, 1144, 1804, 36, NAVY, 10)
d.text(58, 1151, "15 场活动 · 总时长 %d 分钟 · 同会场无时间重叠 · 跨会场并行 %d 组（非冲突）· 输入时间未做任何调整"
       % (A["totals"]["total_session_minutes"], A["conflicts"]["cross_venue_overlap_count"]),
       19, "#E2E8F0FF")
d.text(1420, 1151, "Snapshot DSL · 1920×1200", 19, "#94A3B8FF", "NORMAL", MONO, 406, "CENTER_RIGHT")

wide = d.done()
open(os.path.join(TMP, "agenda-wide.snapshot"), "w", encoding="utf-8", newline="\n").write(wide)

# ==================================================================================
# MOBILE 720x1280 — segmented list, NOT a downscale of the wide image
# ==================================================================================
MW, MH = 720, 1280
m = Doc(MW, MH)
m.box(0, 0, MW, 150, NAVY)
m.box(0, 0, 6, 150, TEAL)
m.text(28, 20, "Structure / Vision 2026", 26, "#5EEAD4FF", "BOLD", MONO)
m.text(28, 56, "手机导览 · 分时段列表", 32, "#FFFFFFFF", "BOLD")
m.text(28, 104, "2026.11.07 · 云构中心 A / B / C 会场", 19, "#94A3B8FF")
m.text(28, 126, "时间均为 Asia/Shanghai · 讲者详见完整日程", 19, "#FBBF24FF", "BOLD")

morning = [s for s in S if s["end_min"] <= 720]
afternoon = [s for s in S if s["start_min"] >= 780]
y = 162
for band, items, note in (("上午 09:00 — 12:00", morning, f"{len(morning)} 场"),
                          (None, None, None)):
    if band is None:
        # lunch band
        m.box(24, y, MW - 48, 46, "#FDE68AFF", 10, "1 SOLID #F59E0BFF")
        m.text(40, y + 10, "12:00 — 13:00  公共午休", 22, "#92400EFF", "BOLD")
        m.text(MW - 200, y + 10, "不并入任何会议", 19, "#92400EFF", "NORMAL", CJ, 160, "CENTER_RIGHT")
        y += 58
        band, items, note = "下午 13:00 — 16:00", afternoon, f"{len(afternoon)} 场"
    m.box(24, y, MW - 48, 40, "#E2E8F0FF", 8)
    m.text(40, y + 10, band, 22, INK, "BOLD")
    m.text(MW - 180, y + 12, note, 19, MUTED, "NORMAL", MONO, 140, "CENTER_RIGHT")
    y += 48
    for s in items:
        col, bgc, label = CAT_STYLE[s["category"]]
        m.box(24, y, MW - 48, 50, bgc, 8, f"1 SOLID {col}")
        m.bar(24, y, 5, 50, col, tl=8, bl=8)
        m.text(40, y + 8, s["id"], 20, col, "BOLD", MONO)
        m.text(40, y + 28, f"{s['venue']} 会场", 18, INK2, "BOLD")
        m.text(126, y + 6, fit(s["title"], 19, 360), 19, INK, "BOLD")
        m.text(126, y + 28, f"{label} · {s['duration_min']} 分钟", 18, MUTED)
        m.text(MW - 186, y + 6, f"{s['start']}–{s['end']}", 19, INK, "BOLD", MONO, 146, "CENTER_RIGHT")
        m.text(MW - 186, y + 28, "讲者详见完整日程", 17, MUTED2, "NORMAL", CJ, 146, "CENTER_RIGHT")
        y += 56

m.box(24, y + 4, MW - 48, 92, "#0F172AFF", 12)
m.text(42, y + 14, "读图说明", 20, "#5EEAD4FF", "BOLD")
m.text(42, y + 40, "本页为重新排版的分时段列表，包含全部 15 项的编号、标题、", 18, "#E2E8F0FF")
m.text(42, y + 62, "会场与起止时间；讲者与类别详情见 1920×1200 完整日程。", 18, "#E2E8F0FF")

mobile = m.done()
open(os.path.join(TMP, "agenda-mobile.snapshot"), "w", encoding="utf-8", newline="\n").write(mobile)

print("wide", len(wide), "chars | mobile", len(mobile), "chars")
print("wide rows", LANE_Y0, LANE_BOT, "| cards end", GY0 + 3 * CH + 2 * CGY)
print("mobile list end y", y)
