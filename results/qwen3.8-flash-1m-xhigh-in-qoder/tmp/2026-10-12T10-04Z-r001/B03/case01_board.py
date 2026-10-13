"""B03 case-01 门诊叫号屏 - frosted panels over a live colour field.

Real use: a 16:9 wall board in a hospital waiting area, refreshed every 30 s by the
triage desk. The frontier capability is BackdropFilter: the panels are glass, so the
department colour field behind them must stay legible as blur while the numbers stay
crisp. Every glass panel is clipped (bkit.Sheet.glass), because an unclipped
BackdropFilter re-composites the whole canvas opaquely (requests B03-p6-bottom-only /
B03-p6-clipped-backdrop).

Run: python tmp/<run_id>/B03/case01_board.py            (from the suite task root)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, SANS, tw, f  # noqa: E402
from snap import Node  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
OUT = ROOT / "outputs" / RUN / "B03" / "case-01"
W, H = 1600, 900

INK, INK2, INK3 = "#0E2233", "#2C4152", "#5B6E7C"
PAPER = "#F4F1E8"
ACCENT = "#B4432B"
OK = "#1F6F5C"
WARN = "#8A6A12"

# ------------------------------------------------------------------ queue model
ROOMS = [
    {"id": "A", "dept": "内科", "room": "3 诊室", "doctor": "周敏 主任医师",
     "now": "A 042", "issued": 58, "waiting": 7, "consult": 8, "band": "#0B3954",
     "state": "接诊中"},
    {"id": "B", "dept": "外科", "room": "5 诊室", "doctor": "李振宇 副主任医师",
     "now": "B 017", "issued": 24, "waiting": 4, "consult": 12, "band": "#12607A",
     "state": "接诊中"},
    {"id": "C", "dept": "儿科", "room": "1 诊室", "doctor": "陈曦 主治医师",
     "now": "C 096", "issued": 131, "waiting": 12, "consult": 7, "band": "#7A3B62",
     "state": "高峰"},
    {"id": "D", "dept": "骨科", "room": "2 诊室", "doctor": "赵弘 主任医师",
     "now": "D 008", "issued": 19, "waiting": 2, "consult": 15, "band": "#2F6B3A",
     "state": "接诊中"},
    {"id": "E", "dept": "眼科", "room": "4 诊室", "doctor": "孙嘉 主治医师",
     "now": "E 031", "issued": 44, "waiting": 5, "consult": 9, "band": "#8A5A12",
     "state": "接诊中"},
    {"id": "F", "dept": "口腔科", "room": "6 诊室", "doctor": "吴桐 副主任医师",
     "now": "F 000", "issued": 12, "waiting": 0, "consult": 20, "band": "#4A4A6A",
     "state": "暂停"},
]
for r in ROOMS:
    r["seen"] = r["issued"] - r["waiting"]
    r["queue_ahead"] = max(r["waiting"] - 1, 0)
    r["wait_min"] = r["queue_ahead"] * r["consult"] + int(r["consult"] * 0.5)
    r["next"] = chr(ord(r["id"])) + " " + f"{int(r['now'].split()[1]) + 1:03d}"
    r["paused"] = r["state"] == "暂停"
assert all(r["seen"] >= 0 and r["issued"] >= r["waiting"] for r in ROOMS)
assert ROOMS[5]["seen"] == 12 and ROOMS[5]["paused"]
AVG_WAIT = round(sum(r["wait_min"] * r["waiting"] for r in ROOMS)
                 / sum(r["waiting"] for r in ROOMS))
TOTAL_WAITING = sum(r["waiting"] for r in ROOMS)
assert TOTAL_WAITING == 30 and AVG_WAIT == 58, (TOTAL_WAITING, AVG_WAIT)
ER = {"lane": "急诊绿色通道", "free": 1, "total": 3, "ambulance": 2, "triage": "II 级 1 人"}
REFRESH = "14:32:10"


def mix(c0, c1, t):
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lum(hexcol):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(int(hexcol[1:3], 16)) + 0.7152 * ch(int(hexcol[3:5], 16)) \
        + 0.0722 * ch(int(hexcol[5:7], 16))


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)


# ------------------------------------------------------------------ build
s = Sheet(W, H, min_font=20, bg="#EFF3F2")

# colour field the glass will blur: one band per department, plus a warm floor wash
for i, r in enumerate(ROOMS):
    x = 40 + i * 260
    s.rect(x, 0, 260, H, mix(r["band"], "#FFFFFF", 0.74))
    s.rect(x, 0, 260, 240, mix(r["band"], "#FFFFFF", 0.52))
    s.text("bg", r["id"], x + 130, 250, 300, mix(r["band"], "#FFFFFF", 0.90),
           align="center", bold=True, font=MONO)  # lightened: see contrast note
s.rect(0, 620, W, 280, mix("#F4D9B0", "#FFFFFF", 0.35))
# fine vertical rules so the blur has structure to lose
for i in range(41):
    s.rect(20 + i * 39, 0, 2, H, "#0B395420")

# header
s.rect(0, 0, W, 132, mix("#0B3954", "#FFFFFF", 0.04))
s.text("hdr", "市第一人民医院 · 门诊候诊屏", 56, 34, 46, "#FFFFFF", bold=True)
s.text("hdr", f"数据由分诊台每 30 秒推送 · 更新 {REFRESH}", 56, 92, 24, "#BFD4E0")
s.rich("hdr", [("今日已接诊 ", {"raw": True}),
               ("2 486", {"font": MONO, "bold": True}),
               (" 人次", {"raw": True})], W - 56, 34, size=30, colour="#FFFFFF",
       features="tnum", height=1.2, align="right")
s.text("hdr", f"当前排队 {TOTAL_WAITING} 人 · 候诊者平均还需 {AVG_WAIT} 分钟",
       W - 56, 84, 24, "#BFD4E0", align="right")

CX, CY, CW, CH = 56, 172, 470, 286
GAP_X, GAP_Y = 30, 26
checks = []
for i, r in enumerate(ROOMS):
    col, row = i % 3, i // 3
    x = CX + col * (CW + GAP_X)
    y = CY + row * (CH + GAP_Y)
    tint = mix("#FFFFFF", r["band"], 0.06)
    s.glass(x, y, CW, CH, sigma=16, tint=tint + "CC", radius=22)
    s.rect(x, y, CW, CH, "#00000000", border=f"2 SOLID {mix(r['band'],'#FFFFFF',0.55)}",
           radius=22, shadow="0 18 40 #0B395440")
    s.rect(x + 22, y + 24, 6, CH - 48, r["band"], radius=3)
    L, RX = x + 44, x + CW - 24          # left column / right edge of right column
    CUT = x + 286                        # nothing on the right may start left of this
    s.text("card", f"{r['dept']} · {r['room']}", L, y + 26, 30, INK, bold=True)
    s.text("card", r["doctor"], L, y + 70, 22, INK2)
    s.text("card", r["now"], L, y + 108, 72, mix(r["band"], "#000000", 0.15),
           bold=True, font=MONO)
    s.text("card", "当前叫号", L, y + 196, 20, INK3)
    pill_col = {"接诊中": OK, "高峰": ACCENT, "暂停": WARN}[r["state"]]
    pw = tw(r["state"], 22) + 44
    assert RX - pw >= CUT, (r["id"], pw)
    s.rect(RX - pw, y + 26, pw, 40, "#00000000",
           border=f"2 SOLID {pill_col}", radius=20)
    s.text("card", r["state"], RX - pw / 2, y + 34, 22, pill_col,
           align="center", bold=True)
    s.text("card", f"候诊 {r['waiting']} 人", RX, y + 82, 28, INK, align="right",
           bold=True)
    if r["paused"]:
        s.text("card", "15:30 复诊", RX, y + 124, 28, WARN, align="right", bold=True)
        s.text("card", "请到分诊台登记", RX, y + 168, 20, INK2, align="right")
    else:
        s.text("card", f"预计 {r['wait_min']} 分钟", RX, y + 124, 28,
               mix(r["band"], "#000000", 0.2), align="right", bold=True)
        s.text("card", f"每人约 {r['consult']} 分钟", RX, y + 168, 20, INK2,
               align="right")
    # footer: progress seen / issued, plus the two queue facts that matter up close
    frac = r["seen"] / max(r["issued"], 1)
    s.rect(L, y + CH - 34, CW - 88, 10, "#0B395422", radius=5)
    s.rect(L, y + CH - 34, max((CW - 88) * frac, 6), 10, r["band"], radius=5)
    s.text("card", f"今日已过号 {r['issued'] - r['seen']} 人", L, y + CH - 66, 20,
           INK3)
    s.text("card", "下一位 —" if r["paused"] else f"下一位 {r['next']}",
           RX, y + CH - 66, 20, INK2, align="right")
    # the surface the glass actually sits on, for the contrast assertion
    surface = mix(mix(r["band"], "#FFFFFF", 0.79), "#FFFFFF", 0.20)
    checks.append((r["dept"], ratio(surface, INK), ratio(surface, INK2),
                   ratio(surface, mix(r["band"], "#000000", 0.15))))

# emergency rail under the cards
s.glass(56, 790, W - 112, 90, sigma=10, tint="#0B3954E6", radius=18)
s.text("er", ER["lane"], 84, 802, 32, "#FFFFFF", bold=True)
s.text("er", f"抢救室占用 {ER['free']}/{ER['total']} · 在途救护车 {ER['ambulance']} 台 "
             f"· 预检 {ER['triage']}", 84, 844, 22, "#C7DCE7")
s.text("er", "请留意叫号后 3 分钟内到诊，过号请到分诊台重新排序",
       W - 84, 800, 26, "#FFFFFF", align="right", bold=True)
s.text("er", "内科 / 外科 → 3F   儿科 → 2F 东区   骨科 / 眼科 / 口腔 → 4F",
       W - 84, 844, 22, "#C7DCE7", align="right")

audit = s.audit(ignore_roles=("bg",))
print(json.dumps(audit, ensure_ascii=False))
for dept, a, b, c in checks:
    print(f"contrast {dept}: ink {a} sub {b} number {c}")
    assert min(a, b, c) >= 4.5, f"{dept} contrast too low"
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]

dsl = s.dsl() + "\n"
OUT.mkdir(parents=True, exist_ok=True)
(TMP / "case01-board.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case01-data.json").write_text(json.dumps(
    {"rooms": ROOMS, "er": ER, "refresh": REFRESH, "contrasts": checks},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("nodes", len(s.nodes), "shapes", s.shapes, "bytes", len(dsl.encode("utf-8")))
