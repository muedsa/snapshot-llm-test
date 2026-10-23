"""case-01 急诊三十分钟 · 分诊降级倒计时（1920×1080 暗光墙面大屏）。

视觉系统：五级严重度阶梯 × 三档紧急状态仪表。
  行 = ESI 1..5（越靠上越紧急），行标签印出「ESI n」与允许等待分钟，
      所以严重度不靠颜色传达——行位置与印刷数字才是它的编码通道。
  仪表弧长 = 已等 ÷ 允许等待（走到尽头即超时），圆心 = 剩余分钟。
  仪表颜色只分三档紧急状态：现在行动 / 即将超时 / 相对稳定，
      三色 deutan/tritan/normal ΔE 全部 ≥20，且都带印刷文字标签。
护士不用读表：数一数还有几个红色环、哪一行最满。

数据全部自拟演示数据，非真实病人、不宣称实际部署。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1920, 1080
BG = "#0A0F1E"
PANEL = "#131B2F"
PANEL2 = "#1B2440"
TRACK = "#212C4A"
INK = "#F2F6FD"
INK2 = "#9AA8C4"
INK3 = "#7686A2"
ACCENT = "#7686A2"

# ESI 分级：(编号, 名称, 允许等待分钟)
ESI = [(1, "即刻处置", 5), (2, "高危观察", 10), (3, "急重症候", 30),
       (4, "可延迟处置", 60), (5, "非急重症", 120)]
ESI_LIMIT = {n: lim for n, _, lim in ESI}

# 三档紧急状态色（唯一承担颜色编码的角色）
NOW, NOW_TXT = "#F43F5E", "现在行动"
SOON, SOON_TXT = "#FBBF24", "即将超时"
OK, OK_TXT = "#60A5FA", "相对稳定"

# 自拟演示数据：(序号, 床号, 脱敏姓名, 年龄/性别, ESI, 已等分钟)
PTS = [
    (1, "床12", "王**", "男 47", 1, 4),
    (2, "床08", "李**", "女 29", 1, 7),
    (3, "床03", "张**", "男 63", 2, 8),
    (4, "床05", "刘**", "女 38", 2, 5),
    (5, "床11", "陈**", "男 19", 2, 3),
    (6, "床02", "赵**", "女 52", 3, 24),
    (7, "床06", "周**", "男 71", 3, 19),
    (8, "床09", "吴**", "女 8", 3, 12),
    (9, "床14", "郑**", "男 35", 3, 6),
    (10, "床01", "孙**", "女 66", 4, 22),
    (11, "床04", "朱**", "男 44", 4, 41),
    (12, "床10", "马**", "女 77", 4, 8),
    (13, "床07", "胡**", "男 58", 5, 33),
    (14, "床13", "林**", "女 25", 5, 61),
]

UP = -math.pi / 2
TWO_PI = 2 * math.pi
MIN_FS = 18


def state_of(rem: int) -> tuple:
    if rem <= 5:
        return NOW, NOW_TXT
    if rem <= 15:
        return SOON, SOON_TXT
    return OK, OK_TXT


def enrich() -> list:
    out = []
    for pid, bed, name, age, esi, waited in PTS:
        limit = ESI_LIMIT[esi]
        rem = limit - waited
        col, stxt = state_of(rem)
        out.append({"pid": pid, "bed": bed, "name": name, "age": age,
                    "esi": esi, "waited": waited, "limit": limit, "rem": rem,
                    "frac": min(1.0, waited / limit), "over": rem < 0,
                    "color": col, "stxt": stxt})
    return out


def build() -> tuple:
    d = K.Doc(W, H, BG)
    gates: list = []
    P = enrich()
    by_esi = {n: sorted([p for p in P if p["esi"] == n],
                        key=lambda q: q["rem"]) for n, *_ in ESI}
    overdue = sum(1 for p in P if p["over"])
    now_n = sum(1 for p in P if p["color"] == NOW)
    soon_n = sum(1 for p in P if p["color"] == SOON)
    crit = sum(1 for p in P if p["esi"] <= 2)

    # ------------------------------------------------ 顶栏
    d.rect(0, 0, W, 112, PANEL)
    d.rect(0, 110, W, 2, NOW)
    d.text(58, 24, "急诊分诊 · 30 分钟降级倒计时", 34, INK, bold=True)
    d.text(58, 70, "弧长 = 已等 ÷ 允许等待　|　圆心 = 剩余分钟　|　越靠上越紧急",
           18, INK2)

    for i, (label, val, col) in enumerate([
            ("在院", str(len(P)), INK), ("已超时", str(overdue), NOW),
            ("现在行动", str(now_n), NOW), ("ESI 1-2", str(crit), SOON)]):
        kx = 1112 + i * 190
        d.rect(kx, 26, 178, 74, PANEL2, radius=10)
        d.text_c(kx + 89, 34, val, 30, col, bold=True)
        d.text_c(kx + 89, 72, label, 18, INK2)

    # ------------------------------------------------ 状态图例
    lx, top, row_h, gap = 58, 162, 158, 13
    LADDER_W = 1082
    for i, (col, txt, rng) in enumerate([(NOW, NOW_TXT, "剩余 ≤ 5 分"),
                                         (SOON, SOON_TXT, "剩余 6-15 分"),
                                         (OK, OK_TXT, "剩余 ≥ 16 分")]):
        cx0 = 470 + i * 210
        d.rect(cx0, 128, 14, 14, col, radius=7)
        d.text(cx0 + 26, 126, txt, 18, INK, bold=True)
        d.text(cx0 + 106, 128, rng, 18, INK3)

    # ------------------------------------------------ 阶梯
    for i, (n, zh, limit) in enumerate(ESI):
        y = top + i * (row_h + gap)
        row = by_esi[n]
        d.rect(lx, y, LADDER_W, row_h, PANEL, radius=12)
        d.rect(lx, y, 300, row_h, PANEL2, radius=12)
        d.rect(lx + 288, y, 12, row_h, PANEL2, radius=6)
        d.rect(lx + 16, y + 16, 6, row_h - 32, ACCENT, radius=3)
        d.text(lx + 40, y + 16, "ESI %d" % n, 30, INK, bold=True)
        d.text(lx + 40, y + 58, zh, 22, INK2, bold=True)
        d.text(lx + 40, y + 92, "允许等待 %d 分钟" % limit, 18, INK3)
        d.text(lx + 40, y + 120, "在院 %d 人" % len(row), 18, INK3)

        gx = lx + 324
        for p in row:
            cx, cy = gx + 88, y + 54
            d.arc(cx, cy, 38, 48, UP, UP + TWO_PI - 0.02, TRACK, step=1)
            d.arc(cx, cy, 38, 48, UP, UP + TWO_PI * max(0.008, p["frac"]),
                  p["color"], step=1)
            if p["over"]:
                d.text_c(cx, cy - 14, "超时", 24, p["color"], bold=True)
            else:
                d.text_c(cx, cy - 14, "%d 分" % p["rem"], 24,
                         p["color"] if p["color"] != OK else INK, bold=True)
            d.text_c(cx, y + 112, "%s %s" % (p["bed"], p["name"]), 18, INK,
                     bold=True)
            d.text_c(cx, y + 136, "%s · 已等 %d 分" % (p["age"], p["waited"]),
                     18, INK3)
            gx += 176
        if not row:
            d.text(lx + 324, y + 62, "当前无在院患者", 18, INK3)

    # ------------------------------------------------ 右侧：本班次处置队列
    qx, qy, qw, qh = 1160, 162, 702, 842
    d.rect(qx, qy, qw, qh, PANEL, radius=14)
    d.rect(qx + 22, qy + 22, 6, 34, NOW, radius=3)
    d.text(qx + 44, qy + 20, "本班次处置队列", 26, INK, bold=True)
    d.text(qx + 44, qy + 58, "按剩余分钟升序 · 前 7 名", 18, INK3)
    d.rect(qx + 22, qy + 96, qw - 44, 2, "#222D4B")

    queue = sorted(P, key=lambda q: q["rem"])[:7]
    ry = qy + 112
    for i, p in enumerate(queue):
        d.rect(qx + 22, ry + 6, 40, 40, PANEL2, radius=20)
        d.text_c(qx + 42, ry + 14, "%d" % (i + 1), 20, INK2, bold=True)
        d.text(qx + 80, ry + 8, "%s %s" % (p["bed"], p["name"]), 22, INK,
               bold=True)
        d.text(qx + 80, ry + 40, "%s · ESI %d · 已等 %d 分"
               % (p["age"], p["esi"], p["waited"]), 18, INK3)
        if p["over"]:
            d.text_r(qx + qw - 22, ry + 18, "已超时", 22, p["color"],
                     bold=True)
        else:
            d.text_r(qx + qw - 22, ry + 18, "剩 %d 分" % p["rem"], 22,
                     p["color"], bold=True)
        if i < len(queue) - 1:
            d.rect(qx + 22, ry + 76, qw - 44, 1, "#1D2740")
        ry += 88

    d.rect(qx + 22, 892, qw - 44, 1, "#1D2740")
    _rem = sorted(p["rem"] for p in P)
    d.text(qx + 22, 910, "其余 %d 人处于相对稳定区间（剩余 %d-%d 分）"
           % (len(P) - len(queue), _rem[len(queue)], _rem[-1]), 18, INK2)
    d.text(qx + 22, 940, "处置顺序：先 ESI 1 已超时，再依次处理剩余 ≤ 5 分",
           18, INK3)
    d.text(qx + 22, 970, "队列为示意快照，实际以分诊系统为准", 18, INK3)

    # ------------------------------------------------ 底栏
    d.rect(0, H - 66, W, 66, PANEL)
    d.text(58, H - 48, "数据为自拟演示数据，非真实病人；分级阈值为常见 ESI 参考值，"
           "不构成临床建议。仪表按剩余时间着色，严重度看行位置与 ESI 编号。",
           18, INK3)
    d.text_r(W - 58, H - 48, "折光 · 十张日常　01 / 10", 18, INK3)
    d.text_r(W - 58, H - 22, "示意时刻 08:42 · 出图 2026-10-22", 18, INK3)

    # ------------------------------------------------ 专项门禁
    K.gate(gates, "case-01-06", "剩余分钟 = 允许 - 已等，逐人复算",
           all(p["rem"] == p["limit"] - p["waited"] for p in P),
           "; ".join("%s" % p["bed"] for p in P
                     if p["rem"] != p["limit"] - p["waited"]))
    K.gate(gates, "case-01-07", "仪表弧长比例 = min(1, 已等/允许)",
           all(abs(p["frac"] - min(1.0, p["waited"] / p["limit"])) < 1e-12
               for p in P), "")
    K.gate(gates, "case-01-08", "分级人数合计等于总人数 14",
           sum(len(v) for v in by_esi.values()) == len(P),
           {n: len(v) for n, v in by_esi.items()})
    K.gate(gates, "case-01-09", "KPI 与逐人数据复算一致（超时1/现在行动4/"
                                "即将超时3/ESI1-2 共5）",
           (overdue, now_n, soon_n, crit) == (1, 4, 3, 5),
           "overdue=%d now=%d soon=%d crit=%d" % (overdue, now_n, soon_n,
                                                  crit))
    K.gate(gates, "case-01-10", "紧急状态按剩余分钟阈值唯一确定",
           all(p["stxt"] == state_of(p["rem"])[1] for p in P), "")
    K.gate(gates, "case-01-11", "严重度不依赖颜色：每行都印出 ESI 编号与"
                                "允许等待分钟",
           all(("ESI %d" % n) in [t["text"] for t in d.texts] and
               ("允许等待 %d 分钟" % limit) in [t["text"] for t in d.texts]
               for n, zh, limit in ESI), "")
    K.gate(gates, "case-01-12", "三档紧急色与面板背景对比 ≥ 3.0",
           all(K.contrast(c, PANEL2) >= 3.0 for c in (NOW, SOON, OK)),
           " ".join("%.1f" % K.contrast(c, PANEL2) for c in (NOW, SOON, OK)))
    K.gate(gates, "case-01-13", "处置队列前 7 名按剩余分钟严格升序",
           all(queue[i]["rem"] <= queue[i + 1]["rem"]
               for i in range(len(queue) - 1)),
           " ".join(str(p["rem"]) for p in queue))
    K.gate(gates, "case-01-14", "队列恰好覆盖现在行动 + 即将超时全部患者",
           len(queue) == now_n + soon_n and all(p["rem"] <= 15 for p in queue),
           "queue=%d now+soon=%d" % (len(queue), now_n + soon_n))
    rem_all = sorted(p["rem"] for p in P)
    K.gate(gates, "case-01-15", "相对稳定区间端点与逐人数据一致",
           (rem_all[len(queue)], rem_all[-1]) == (18, 87),
           "start=%d end=%d" % (rem_all[len(queue)], rem_all[-1]))
    K.check_palette("case-01", [(NOW, SOON), (SOON, OK), (NOW, OK)], gates,
                    min_deutan=18.0, min_tritan=18.0, min_normal=25.0)
    gates = K.dry_run(d, "case-01", MIN_FS, gates)
    return d, gates, "第二版（最终交付）：加入右侧处置队列、修复实体转义、队列门禁"


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    doc, gates, note = build()
    K.assert_gates(gates, "case-01")
    print("gates=%s" % K.save_gates("case-01", gates, note))
    if "--dry" in sys.argv:
        return 0
    st = doc.stats()
    print("parts=%d texts=%d shapes=%d dsl=%d" % (st["parts"], st["texts"],
                                                   st["shapes"],
                                                   len(doc.build())))
    rec = K.render_case("case-01", doc, "case-01-er-triage",
                        "渲染 case-01 急诊分诊降级倒计时", attempt_note=note)
    print("status=%s bytes=%s parts=%d ms=%s"
          % (rec["http_status"], rec.get("png_bytes"), rec["parts"],
             rec.get("elapsed_ms")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
