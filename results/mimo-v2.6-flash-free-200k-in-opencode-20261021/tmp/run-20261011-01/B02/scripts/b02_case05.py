# -*- coding: utf-8 -*-
"""B02 case-05 · 志愿者排班表 (1400x1000, 手机查看/工具房打印).

user_goal: 看清本周各时段岗位缺口并认领。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b02_common as C  # noqa: E402

W, H = 1400, 1000

DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
SLOTS = ["07–10", "10–13", "13–16", "16–19"]
JOBS = ["浇水", "除草", "采收", "分拣"]
# grid[day*4+slot] = list of (job, people); day-major, 4 slots per day
GRID = [
    # 周一
    [("浇水", 1)], [("浇水", 1)], [("浇水", 1), ("除草", 2)], [("浇水", 1)],
    # 周二
    [("浇水", 1), ("采收", 2)], [("采收", 3), ("分拣", 2), ("除草", 2)],
    [("浇水", 1), ("分拣", 1)], [("除草", 1)],
    # 周三（07-10 除草缺 1 人：busy=2, need=3）
    [("除草", 2)], [("浇水", 1)], [("采收", 1)], [("浇水", 1), ("除草", 1)],
    # 周四（13-16 采收缺 2 人：busy=1, need=3）
    [("浇水", 1)], [("浇水", 1)], [("采收", 1)], [("浇水", 1)],
    # 周五
    [("浇水", 1), ("除草", 2)], [("浇水", 1)], [("采收", 2)], [("浇水", 1)],
    # 周六（市集日，最忙）
    [("采收", 3), ("分拣", 2), ("除草", 2)], [("采收", 3), ("分拣", 2)],
    [("采收", 2), ("分拣", 1), ("除草", 2)], [("浇水", 1), ("分拣", 1)],
    # 周日（10-13 分拣缺 2 人：busy=1, need=3）
    [("浇水", 1)], [("分拣", 1)], [("浇水", 1)], [("浇水", 1)],
]


def main():
    C.assert_facts()
    assert len(GRID) == 28
    total_p = sum(p for cell in GRID for _j, p in cell)
    els = []
    els.append(C.box(0, 0, W, H, C.PAPER))
    # header
    els.append(C.box(0, 0, W, 112, C.LEAFD))
    els.append(C.brand_header(48, 22, 520, color=C.PAPER, mark=C.SUN,
                              size=24, latin_size=11))
    els.append(C.text(48, 62, 620, 40, "志愿者排班 · 4 月第 3 周", 30, C.PAPER,
                      bold=True))
    els.append(C.chip(1040, 30, 312, 52, C.CLAY, "本周缺口 5 人次", 22,
                      "#FFFFFF", radius=26))

    # grid geometry
    gx, gy = 120, 172
    cwd, chd = 160, 156
    # column headers: days
    els.append(C.text(48, gy - 40, 64, 30, "时段", 18, C.MUTED))
    for d, day in enumerate(DAYS):
        els.append(C.text(gx + d * cwd, gy - 44, cwd, 34, day, 22, C.INK,
                          bold=True, align="CENTER"))
    # slot rows
    for s, slot in enumerate(SLOTS):
        ry = gy + s * chd
        els.append(C.text(44, ry + chd / 2 - 18, 68, 34, slot, 19, C.MUTED,
                          align="RIGHT"))
        for d in range(7):
            x = gx + d * cwd
            assigns = GRID[d * 4 + s]
            busy = sum(p for _j, p in assigns)
            # base cell
            els.append(C.box(x + 4, ry, cwd - 8, chd - 8, C.PAPER2,
                             radius=10, border=C.LINE))
            # saturday market cell emphasis
            if d == 5:
                els.append(C.box(x + 4, ry, cwd - 8, chd - 8, "#00000000",
                                 radius=10, border=C.LEAF, border_w=2))
            cy = ry + 8
            if not assigns:
                els.append(C.text(x + 12, cy, cwd - 24, 30, "空", 17, "#B9AE97",
                                  align="CENTER"))
            for job, p in assigns:
                jc = {"浇水": C.LEAF, "除草": C.SOIL, "采收": C.CLAY,
                      "分拣": C.LEAFD}[job]
                els.append(C.chip(x + 12, cy, 92, 30, jc, job, 16, "#FFFFFF",
                                  radius=8))
                els.append(C.text(x + 108, cy + 2, 36, 26, "%d人" % p, 15,
                                  C.MUTED))
                cy += 36
            # capacity bar: need 3, filled by busy
            need = 3
            els.append(C.box(x + 12, ry + chd - 40, cwd - 24, 12, "#E8DFC9",
                             radius=6))
            fillw = (cwd - 24) * min(busy, need) / float(need)
            barc = C.LEAF if busy >= need else (C.SUN if busy >= 2 else C.CLAY)
            els.append(C.box(x + 12, ry + chd - 40, fillw, 12, barc,
                             radius=6))
            els.append(C.text(x + 12, ry + chd - 26, cwd - 24, 24,
                              "%d/%d" % (busy, need), 14, C.MUTED,
                              align="CENTER"))

    # legend + gap list + contact
    ly = gy + 4 * chd + 18
    els.append(C.box(120, ly, 1240, 128, C.LEAFL, radius=14))
    els.append(C.text(148, ly + 16, 200, 30, "岗位图例", 20, C.LEAFD,
                      bold=True))
    lx = 148
    for job, jc in [("浇水", C.LEAF), ("除草", C.SOIL), ("采收", C.CLAY),
                    ("分拣", C.LEAFD)]:
        els.append(C.chip(lx, ly + 54, 88, 32, jc, job, 16, "#FFFFFF",
                          radius=8))
        lx += 100
    els.append(C.text(148, ly + 94, 560, 26,
                      "容量条：满编 3 人 · 绿=满 黄=2人 红=≤1人", 15, C.MUTED))
    # gap list
    els.append(C.text(560, ly + 16, 420, 30, "本周待认领缺口", 20, C.CLAY,
                      bold=True))
    gaps = ["周四 13–16 采收（差 2 人）", "周日 10–13 分拣（差 2 人）",
            "周三 07–10 除草（差 1 人）"]
    gy2 = ly + 50
    for g in gaps:
        els.append(C.circle(572, gy2 + 11, 4, C.CLAY))
        els.append(C.text(586, gy2, 400, 26, g, 16, C.INK))
        gy2 += 26
    # contact
    els.append(C.line_v(1000, ly + 16, ly + 112, C.LINE))
    els.append(C.text(1028, ly + 16, 310, 30, "认领方式", 20, C.LEAFD,
                      bold=True))
    els.append(C.text(1028, ly + 50, 316, 60,
                      "群内@排班员 小周 · 或工具房白板写名字\n"
                      "本周志愿合计 %d 人次 · 全园 %d 名志愿者" % (
                          total_p, C.FACTS["volunteers"]), 16, C.MUTED,
                      line_h=24))

    els.append(C.footnote(48, H - 40, 900,
                          "禾风里社区共耕花园 · 虚构演示排班；人员与时段均为示例"))
    els.append(C.footnote(900, H - 40, 452, "生成 4.15 · 排班员 小周",
                          align="RIGHT"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "drafts", "case-05-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H)


if __name__ == "__main__":
    main()
