#!/usr/bin/env python
# B05 · case-05 … case-10。与 build_b05.py 共用 b05kit / b05data。
# 启动基准：总任务根 (suite_root)。
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B05"))
from bsnap import (W500, W600, canvas, circle, em_width, line_h, rect, segment,
                   txt, wrap)

import b05data as D
from b05kit import (BG, CW, DANGER, DIM, FROST, FOOTER_NOTE, HAIR, ICE, INK, INKD,
                    M, MUTED, NAV_TOP, PAPER, PAPER2, PANEL, PANEL2, PHONE_H,
                    PHONE_W, RULED, SAFE, SUB, SUBD, WARM, W500 as _w5, assert_fit,
                    appbar, band, bottom_note, btn, check_box, day_text, footer,
                    fridge_block, kv, navbar, note_card, para, patch_chip,
                    patch_disc, section, shelf_header, statusbar, group_label)


# ══════════════════════════════════════════════════════════════════
# case-05 · 录入一件新买的食材 —— 720×1600（2026-10-13 18:42）
# ══════════════════════════════════════════════════════════════════
def c05():
    """产品的主要功能页：陈可 18:42 买回小番茄，录进「冷藏下层」。

    页面末尾给出「存进去之后」的后果预览（在库 37→38、临期 4→5、下层 12→13），
    这是录入这类操作唯一值得预告的东西，也是 case-07 建议页的因果来源。
    """
    b = [rect(0, 0, PHONE_W, PHONE_H, BG)]
    statusbar(b, D.STAMP["c05"])
    appbar(b, 56, "记一笔", action="陈可", back=True)

    y = section(b, M, 124, CW, "这次买的是")
    # 照片位：没有真实照片，用几何占位并写明可以跳过
    b.append(rect(M, y + 6, CW, 112, PANEL, 12, border=f'1 SOLID {HAIR}'))
    b.append(circle(M + 56, y + 62, 52, PANEL2, border=f'2 SOLID {HAIR}'))
    b.append(rect(M + 46, y + 86, 20, 3, DIM, 2))
    b.append(rect(M + 54, y + 76, 3, 13, DIM, 2))
    b.append(txt("拍照这一步可以跳过", M + 104, y + 34, 420, None, 19, INK, W600))
    b.append(txt("App 不用照片也能算保质期，照片只在你翻记录时好看一点。",
                 M + 104, y + 62, CW - 128, None, 16, DIM))
    b.append(txt("＋ 选照片", M + 104, y + 86, 300, None, 16, FROST))
    y += 134

    def field(y, label, value, suffix=None, extra=None):
        b.append(txt(label, M, y, 300, None, 17, DIM))
        b.append(rect(M, y + 26, CW, 52, PANEL, 10))
        b.append(txt(value, M + 18, y + 40, 400, None, 20, INK, W600))
        if suffix:
            b.append(txt(suffix, M + CW - 210, y + 42, 192, None, 16, SUB,
                         align="END"))
        if extra:
            b.append(txt(extra, M + 18, y + 92, CW - 36, None, 16, DIM))
        return y + (118 if extra else 86)

    y = field(y, "名称", "小番茄", extra="也叫圣女果；App 会把它和「番茄」分开记")
    y = field(y, "数量", "400", suffix="克")
    b.append(txt("也可以填", M + 430, y - 34, 120, None, 15, DIM))
    y = field(y, "放在哪一层", "冷藏下层",
              extra="果蔬抽屉上层 · 贴片 2 就在这一层")

    chips = ["冷藏上层", "冷藏中层", "冷藏下层", "冷冻上层", "冷冻下层"]
    cwid = (CW - 4 * 8) / 5
    for i, nm in enumerate(chips):
        x = M + i * (cwid + 8)
        on = (nm == "冷藏下层")
        b.append(rect(x, y, cwid, 50, FROST + "26" if on else PANEL, 10,
                      border=f'1 SOLID {FROST if on else HAIR}'))
        b.append(txt(nm, x, y + 14, cwid, None, 16, FROST if on else SUB,
                     W600 if on else W500, align="CENTER"))
    y += 66

    y = field(y, "什么时候到期", "2026-10-16",
              extra="开封日 10-13 · 冷藏后建议 3 天内吃完")

    b.append(txt("这一份大约吃几次", M, y, 320, None, 17, DIM))
    mw = (CW - 3 * 8) / 4
    for i, nm in enumerate(["1 次", "2 次", "3 次", "4 次以上"]):
        x = M + i * (mw + 8)
        on = (nm == "3 次")
        b.append(rect(x, y + 26, mw, 46, FROST + "26" if on else PANEL, 10,
                      border=f'1 SOLID {FROST if on else HAIR}'))
        b.append(txt(nm, x, y + 38, mw, None, 16, FROST if on else SUB,
                     W600 if on else W500, align="CENTER"))
    y += 86

    b.append(txt("谁放进来的", M, y, 320, None, 17, DIM))
    for i, nm in enumerate(["林彦", "陈可"]):
        x = M + i * 170
        on = (nm == "陈可")
        b.append(rect(x, y + 26, 154, 46, FROST + "26" if on else PANEL, 10,
                      border=f'1 SOLID {FROST if on else HAIR}'))
        b.append(txt(nm, x, y + 38, 154, None, 17, FROST if on else SUB,
                     W600 if on else W500, align="CENTER"))
    b.append(txt("取走时会在成员动态里留一条", M + 360, y + 38, 304, None, 16, DIM))
    y += 86

    y = field(y, "备注（可不填）", D.FORM_DEFAULTS["note"])

    # 后果预览：录入页唯一需要预告的东西
    y = section(b, M, y + 4, CW, "存进去之后", right="本机预览")
    b.append(rect(M, y, CW, 132, PANEL, 12))
    deltas = [("在库件数", "37", "38 件"), ("3 天内到期", "4", "5 件"),
              ("冷藏下层", "12", "13 件")]
    for i, (k, a, c) in enumerate(deltas):
        yy = y + 18 + i * 36
        b.append(txt(k, M + 18, yy, 240, None, 17, SUB))
        b.append(txt(a, M + 300, yy, 90, None, 18, DIM, align="END"))
        b.append(txt("→", M + 400, yy - 1, 40, None, 18, DIM, align="CENTER"))
        b.append(txt(c, M + 446, yy, 160, None, 18, FROST, W600))
    y += 148

    btn(b, M, y, CW, 62, "存进 冷藏下层", fill=FROST, size=21)
    y += 74
    y = para(b, "存进去之后，这一件会出现在今晚的「先吃这些」里，并参与 3 天后的到期统计。",
             M, y, CW, 16, DIM)
    assert_fit(y, 1440, "c05 尾部")
    bottom_note(b)
    navbar(b, "冰箱")
    return canvas(PHONE_W, PHONE_H, "".join(b), BG)


# ══════════════════════════════════════════════════════════════════
# case-06 · 温度告警 —— 720×1600（2026-10-14 13:05）
# ══════════════════════════════════════════════════════════════════
def c06():
    """停电 38 分钟之后冷藏两层超阈，冷冻因蓄冷未受影响。

    这一屏回答四件事：哪一层、什么时候开始、超阈多久、现在该做什么。
    冷冻那一行明确写「正常」——告警页最容易出的错就是让人以为整台冰箱都坏了。
    """
    A = D.ALERT
    b = [rect(0, 0, PHONE_W, PHONE_H, BG)]
    statusbar(b, D.STAMP["c06"])
    appbar(b, 56, "告警", action="1 条未处理", back=True, action_color=DANGER)

    y = 120
    b.append(rect(M, y, CW, 254, PANEL, 14, border=f'1 SOLID {DANGER}55'))
    b.append(rect(M, y, CW, 4, DANGER, 2))
    b.append(txt("温度告警", M + 20, y + 20, 300, None, 20, DANGER, W600))
    b.append(rect(M + CW - 190, y + 18, 170, 32, DANGER + "2E", 16,
                  border=f'1 SOLID {DANGER}88'))
    b.append(txt(f"超阈 {A['over_minutes']} 分钟", M + CW - 190, y + 24, 170, None,
                 17, DANGER, W600, align="CENTER"))
    vt = f"{A['value']:.1f}"
    b.append(txt(vt, M + 20, y + 50, 200, None, 54, DANGER, W600))
    b.append(txt("℃", M + 24 + em_width(vt, 54), y + 74, 60, None, 22, DANGER))
    b.append(txt(f"贴片 {A['no']} · {A['shelf']}", M + 250, y + 58, 280, None,
                 19, INK, W600))
    b.append(txt("12:22 升到 6.0 ℃ 后开始累计，13:05 仍在上升",
                 M + 250, y + 88, 410, None, 16, DIM))
    b.append(rect(M + 20, y + 126, CW - 40, 1, HAIR))
    para(b, f"根因：{A['outage']} 停电，压缩机停转。复电后压缩机用了 22 分钟"
            "才重新启动。冷冻室有余冷，未受影响。",
         M + 20, y + 140, CW - 40, 16, SUB)
    y += 254

    reads = [(1, "冷藏中层", A["other"][1], "告警", 4.0),
             (2, "冷藏下层", A["value"], "告警", 5.0),
             (3, "冷冻室", A["other"][3], "正常", -18.0)]
    for i, (no, sh, t, st, tg) in enumerate(reads):
        patch_chip(b, M + i * 225, y + 18, no, sh, t, st, cw=214, ch=84, target=tg)
    y += 120

    # ── 24 小时曲线
    y = section(b, M, y, CW, "冷藏下层 · 过去 24 小时", right="阈值 6.0 ℃")
    PX0, PX1 = M + 8, M + CW - 8
    PY0, PY1 = y + 6, y + 190
    b.append(rect(PX0, PY0, PX1 - PX0, PY1 - PY0, PANEL, 10))
    span = D.CURVE_VMAX - D.CURVE_VMIN

    def cy(v):
        return PY1 - 14 - (v - D.CURVE_VMIN) / span * (PY1 - PY0 - 34)

    ty = cy(D.CURVE_THRESHOLD)
    xx = PX0 + 14
    while xx < PX1 - 14:                     # BorderStyle 无 DASHED，虚线只能手画
        b.append(rect(xx, ty, 12, 1, DANGER + "66"))
        xx += 22
    # 上移到 ty-40：事件标签改贴图表底部后这里也需要多留净空
    b.append(txt("6.0 ℃ 阈值", PX1 - 130, ty - 40, 118, None, 15, DANGER,
                 align="END"))
    n = len(D.CURVE_24H)
    step = (PX1 - PX0 - 40) / (n - 1)
    pts = [(PX0 + 20 + i * step, cy(v)) for i, v in enumerate(D.CURVE_24H)]
    for i in range(n - 1):
        c = DANGER if D.CURVE_24H[i + 1] >= D.CURVE_THRESHOLD else FROST
        b.append(segment(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, 3))
    for i in (0, n - 1):
        b.append(circle(pts[i][0], pts[i][1], 10, PANEL))
        b.append(circle(pts[i][0], pts[i][1], 6, INK))
    b.append(txt("4.0", PX0 + 8, PY1 - 32, 46, None, 14, DIM))
    for lab, idx in (("13:00", 0), ("19:00", 6), ("01:00", 12), ("07:00", 18),
                     ("13:00", 24)):
        b.append(txt(lab, pts[idx][0] - 30, PY1 - 28, 60, None, 14, DIM,
                     align="CENTER"))
    # 两条标记的 frac 只差 0.63 → 竖线相距约 16px，标签宽 130px 会完全叠在一起；
    # 且原排在 mx+6，第二条已贴近右端会出面板；还和「6.0 ℃ 阈值」(ty−22) 同高再叠一次。
    # → 标签改排竖线**左侧**并右对齐，纵向错开 20px，整体贴到图表底部
    #   （时间轴刻度之上），这样与阈值标签、曲线、竖线全部错开。
    for k, (frac, lab) in enumerate(((22.45, "11:27 停电"),
                                     (23.08, "12:05 复电"))):
        mx = PX0 + 20 + frac * step
        b.append(rect(mx, PY0 + 34, 1, PY1 - PY0 - 48, WARM + "88"))
        b.append(txt(lab, mx - 136, PY1 - 64 + k * 20, 130, None, 14, WARM,
                     align="END"))
    y = PY1 + 12

    # ── 受影响食材
    y = section(b, M, y, CW, "在该层停留超过 5.0 ℃ 最久的三件", right="13:05")
    for nm, qty, sh, days, mins in D.AFFECTED:
        col = band(days)
        b.append(rect(M, y, CW, 52, PANEL, 10))
        b.append(rect(M, y + 12, 4, 28, col, 2))
        b.append(txt(nm, M + 22, y + 14, 130, None, 19, INK, W600))
        b.append(txt(f"{qty} · {sh}", M + 160, y + 16, 210, None, 16, SUB))
        b.append(txt(mins, M + CW - 200, y + 15, 184, None, 17, col, W600,
                     align="END"))
        y += 60
    y = para(b, "叶菜最怕高温，这三件今晚吃掉比再放一天划算。", M, y + 2, CW, 16, DIM)
    y += 26

    # ── 现在可以做
    y = section(b, M, y, CW, "现在可以做")
    actions = [("把下层抽屉的叶菜挪到冷藏中层",
                "中层 6.4 ℃，比下层低 0.7 ℃，挪过去能多撑两天"),
               ("今天少开冷冻门两次",
                "过去 3 天冷藏下层平均开门 11 次，是平时的 2.4 倍"),
               ("不用整台丢弃食材",
                "按当前降温速度，16:02 前会回到 5.0 ℃ 以内")]
    for i, (t, d) in enumerate(actions):
        b.append(rect(M, y, CW, 76, PANEL, 10))
        b.append(circle(M + 34, y + 38, 30, FROST + "22", border=f'1 SOLID {FROST}77'))
        b.append(txt(str(i + 1), M + 19, y + 27, 30, None, 18, FROST, W600,
                     align="CENTER"))
        b.append(txt(t, M + 62, y + 13, CW - 90, None, 18, INK, W600))
        b.append(txt(d, M + 62, y + 41, CW - 90, None, 15, DIM))
        y += 84
    y += 6
    btn(b, M, y, 322, 58, "知道了", fill=None, outline=DANGER, size=19)
    b.append(rect(M + 342, y, 322, 58, PANEL2, 12, border=f'1 SOLID {HAIR}'))
    b.append(txt("转发给陈可", M + 342, y + 17, 322, None, 19, INK, W600,
                 align="CENTER"))
    y += 70
    assert_fit(y, 1440, "c06 尾部")
    bottom_note(b)
    navbar(b, "冰箱")
    return canvas(PHONE_W, PHONE_H, "".join(b), BG)


# ══════════════════════════════════════════════════════════════════
# 横屏平板共用顶栏（case-07 / case-08）
# ══════════════════════════════════════════════════════════════════
def tablet_top(b, w, active, time):
    b.append(rect(0, 0, w, 84, PANEL))
    b.append(rect(0, 84, w, 1, HAIR))
    b.append(circle(50, 42, 34, FROST + "2E", border=f'1 SOLID {FROST}88'))
    b.append(circle(50, 42, 12, FROST))
    b.append(txt("霜标 FrostMark", 78, 28, 260, None, 21, INK, W600))
    x = 380
    for nm in ["冰箱", "记录", "建议", "我的"]:
        on = (nm == active)
        b.append(txt(nm, x, 28, 96, None, 19, FROST if on else SUB,
                     W600 if on else W500))
        if on:
            b.append(rect(x, 60, 40, 3, FROST, 2))
        x += 108
    b.append(txt(time, w - 120, 28, 84, None, 19, SUB, W600, align="END"))


# ══════════════════════════════════════════════════════════════════
# case-07 · 建议页「先吃这些」 —— 1280×900（2026-10-14 19:20）
# ══════════════════════════════════════════════════════════════════
def c07():
    """录入小番茄之后的当晚建议页：5 件先吃 + 1 件别再买。

    五条建议严格按剩余天数升序，每条都带一个可执行动作；
    「别再买了」来自录入时记的采购次数，与 case-08 数据页的采购栏对得上。
    """
    W, H = 1280, 900
    b = [rect(0, 0, W, H, BG)]
    tablet_top(b, W, "建议", D.STAMP["c07"])

    LX, LW = 40, 736
    y = section(b, LX, 108, LW, "今晚先吃这些 · 5 件",
                right=f"在库 {D.STOCK_AFTER} 件")
    for nm, qty, sh, days, why, act in D.ADVICE:
        col = band(days)
        b.append(rect(LX, y, LW, 92, PANEL, 12))
        b.append(rect(LX, y, 5, 92, col, 3))
        b.append(txt(nm, LX + 22, y + 15, 190, None, 22, INK, W600))
        b.append(txt(f"{qty} · {sh}", LX + 22, y + 50, 190, None, 16, SUB))
        b.append(txt(why, LX + 232, y + 20, 236, None, 16, DIM))
        b.append(txt("为什么是它", LX + 232, y + 50, 236, None, 15, DIM))
        b.append(rect(LX + 480, y + 26, 92, 40, col + "26", 20,
                      border=f'1 SOLID {col}88'))
        b.append(txt(day_text(days), LX + 480, y + 37, 92, None, 17, col, W600,
                     align="CENTER"))
        b.append(rect(LX + 596, y + 26, 124, 40, FROST + "26", 20,
                      border=f'1 SOLID {FROST}88'))
        b.append(txt(act, LX + 596, y + 37, 124, None, 17, FROST, W600,
                     align="CENTER"))
        y += 100
    y += 8
    b.append(rect(LX, y, LW, 62, PANEL, 12))
    b.append(txt("排序规则：剩得少 × 已经开封 × 你常吃。吃完回来点一下，"
                 "App 会记住这次排序有多准。", LX + 18, y + 20, LW - 36, None, 16, DIM))
    y += 82
    assert_fit(y, 836, "c07 左栏")

    RX, RW = 812, 428
    nm, sub, _t3, spent, tip = D.DUP_CARD
    b.append(rect(RX, 108, RW, 176, PANEL, 12))
    b.append(rect(RX, 108, RW, 4, WARM, 2))
    b.append(txt("别再买了", RX + 20, 126, 240, None, 20, WARM, W600))
    b.append(txt(nm, RX + 20, 156, 240, None, 30, INK, W600))
    b.append(txt(sub, RX + 20, 196, 240, None, 16, WARM))
    b.append(txt(spent, RX + RW - 160, 158, 140, None, 23, INK, W600, align="END"))
    b.append(txt("本周已花", RX + RW - 160, 192, 140, None, 15, DIM, align="END"))
    b.append(txt(tip, RX + 20, 234, RW - 40, None, 16, SUB))

    tname, tcnt, tkinds, tamt = D.WEEK_BUY
    b.append(rect(RX, 300, RW, 158, PANEL, 12))
    b.append(txt(tname, RX + 20, 316, 240, None, 19, INK, W600))
    for i, (k, v) in enumerate((("采购次数", f"{tcnt} 次"), ("涉及品类", f"{tkinds} 类"),
                                ("合计", tamt))):
        xx = RX + 20 + i * 138
        b.append(txt(v, xx, 348, 132, None, 26, FROST if i == 2 else INK, W600))
        b.append(txt(k, xx, 384, 132, None, 15, DIM))
    b.append(rect(RX + 20, 418, RW - 40, 1, HAIR))
    b.append(txt("比上周少花 ¥38.2，主要来自重复买的叶菜。",
                 RX + 20, 428, RW - 40, None, 16, DIM))

    tname, t1, t2, t3 = D.TEMP_SUMMARY
    b.append(rect(RX, 474, RW, 150, PANEL, 12))
    b.append(txt(tname, RX + 20, 490, 240, None, 19, INK, W600))
    for i, (c, t) in enumerate(((DANGER, t1), (SAFE, t2), (SAFE, t3))):
        yy = 522 + i * 30
        b.append(circle(RX + 28, yy + 10, 9, c))
        b.append(txt(t, RX + 46, yy, RW - 80, None, 16, SUB))

    b.append(rect(RX, 640, RW, 186, PANEL, 12))
    b.append(txt("近 7 天建议采纳", RX + 20, 656, 300, None, 19, INK, W600))
    b.append(txt("采纳 12 / 给出 26 条", RX + RW - 210, 658, 190, None, 17, FROST,
                 W600, align="END"))
    adopt = [3, 2, 4, 1, 3, 2, 1]
    bx0, bw, bgp = RX + 20, 40, 12
    for i, v in enumerate(adopt):
        h = v * 15
        b.append(rect(bx0 + i * (bw + bgp), 792 - h, bw, h, FROST, 4))
    b.append(rect(bx0, 792, 7 * (bw + bgp) - bgp, 1, HAIR))
    b.append(txt("10-09    10-11    10-13    今天", RX + 20, 800, RW - 40,
                 None, 14, DIM))
    b.append(txt("最后一根是今天，未计入采纳", RX + 20, 802, RW - 40, None, 14,
                 DIM, align="END"))

    footer(b, 40, 836, 1200,
           "霜标 FrostMark · 建议页界面稿；食材与采购数据为自拟示例，非真实家庭记录")
    return canvas(W, H, "".join(b), BG)


# ══════════════════════════════════════════════════════════════════
# case-08 · 数据页 —— 1280×900（2026-10-15 09:00）
# ══════════════════════════════════════════════════════════════════
def c08():
    """44 天的账：239 件次录入 = 196 用完 + 6 丢弃 + 37 在库，页面上能自己核对。

    每周丢弃柱状图的七根柱之和必须等于 6，与 KPI 卡和结论文案一致。
    """
    W, H = 1280, 900
    b = [rect(0, 0, W, H, BG)]
    tablet_top(b, W, "记录", D.STAMP["c08"])
    b.append(txt("已连续记录 44 天 · 自 2026-08-30 起", 40, 102, 700, None, 17, DIM))

    kpis = [("累计录入", f"{D.TOTAL_LOGGED}", "件次", FROST, "手动录入 + 首日导入"),
            ("已吃掉", f"{D.TOTAL_USED}", "件", SAFE, "取走时标记为吃完"),
            ("丢弃", f"{D.TOTAL_DROPPED}", "件", DANGER, "记为坏掉或过期"),
            ("在库", f"{D.STOCK_BEFORE}", "件", ICE, "此刻冰箱里有的")]
    cw = (1200 - 3 * 14) / 4
    for i, (k, v, unit, col, note) in enumerate(kpis):
        x = 40 + i * (cw + 14)
        b.append(rect(x, 136, cw, 112, PANEL, 12))
        b.append(rect(x, 136, cw, 3, col, 2))
        b.append(txt(k, x + 18, 150, cw - 36, None, 17, SUB))
        b.append(txt(v, x + 18, 172, 150, None, 38, col, W600))
        b.append(txt(unit, x + 22 + em_width(v, 38), 190, 90, None, 17, col))
        b.append(txt(note, x + 18, 216, cw - 36, None, 15, DIM))
    b.append(txt(f"{D.TOTAL_USED} 用完 ＋ {D.TOTAL_DROPPED} 丢弃 ＋ "
                 f"{D.STOCK_BEFORE} 在库 ＝ {D.TOTAL_LOGGED}",
                 700, 262, 540, None, 16, DIM, align="END"))

    LX, LW = 40, 736
    y = section(b, LX, 288, LW, "每周丢弃件数", right="第 1–7 周 · 合计 6 件")
    PX0, PX1 = LX + 64, LX + LW - 24
    PY0, PY1 = y + 16, y + 250
    b.append(rect(LX, PY0 - 12, LW, PY1 - PY0 + 92, PANEL, 10))
    for k in range(3):
        gy = PY1 - (k / 2) * (PY1 - PY0 - 20)
        b.append(rect(PX0, gy, PX1 - PX0, 1, HAIR))
        b.append(txt(f"{k} 件", LX + 14, gy - 10, 44, None, 14, DIM, align="END"))
    n = len(D.WEEKLY_DROPPED)
    slot = (PX1 - PX0) / n
    bw = slot * 0.50
    for i, v in enumerate(D.WEEKLY_DROPPED):
        h = (v / 2) * (PY1 - PY0 - 20)
        bx = PX0 + slot * i + (slot - bw) / 2
        b.append(rect(bx, PY1 - h, bw, max(4, h), DANGER if v else HAIR, 6))
        if v:
            b.append(txt(str(v), bx - 10, PY1 - h - 26, bw + 20, None, 17, DANGER,
                         W600, align="CENTER"))
        else:
            b.append(txt("0", bx - 10, PY1 - 26, bw + 20, None, 15, DIM,
                         align="CENTER"))
        b.append(txt(f"第 {i + 1} 周", bx - 18, PY1 + 12, bw + 36, None, 15, DIM,
                     align="CENTER"))
        b.append(txt(D.WEEK_LABELS[i], bx - 18, PY1 + 34, bw + 36, None, 14, DIM,
                     align="CENTER"))
    b.append(txt("第 7 周还在进行中，10-14 那次温度告警不算丢弃",
                 LX + 20, PY1 + 62, LW - 40, None, 15, DIM))

    note_card(b, LX, PY1 + 96, LW,
              "44 天里丢掉 6 件，其中 4 件是叶菜，都在下层。下层本来就是最不稳的一层"
              "—— 贴片 2 在那里，它提示过 9 次偏高。",
              accent=WARM, size=17)

    RX, RW = 812, 428
    y2 = section(b, RX, 288, RW, "录入来源", right=f"合计 {D.TOTAL_LOGGED} 件次")
    tot = sum(v for _n2, v in D.SOURCE)
    for i, (nm, v) in enumerate(D.SOURCE):
        yy = y2 + i * 54
        b.append(txt(nm, RX, yy + 2, 220, None, 17, SUB))
        b.append(rect(RX, yy + 30, RW - 100, 12, PANEL2, 6))
        b.append(rect(RX, yy + 30, (RW - 100) * v / tot, 12, FROST, 6))
        b.append(txt(f"{v}", RX + RW - 92, yy, 92, None, 19, INK, W600, align="END"))
        b.append(txt(f"{v * 100 // tot}%", RX + RW - 92, yy + 28, 92, None, 15,
                     DIM, align="END"))

    y2 = section(b, RX, y2 + 186, RW, f"在库 {D.STOCK_BEFORE} 件的层位分布")
    mx = max(v for _s, v in D.SHELF_STOCK)
    for i, (sh, v) in enumerate(D.SHELF_STOCK):
        yy = y2 + i * 44
        b.append(txt(sh, RX, yy + 2, 150, None, 17, SUB))
        b.append(rect(RX + 150, yy + 6, RW - 240, 14, PANEL2, 7))
        b.append(rect(RX + 150, yy + 6, (RW - 240) * v / mx, 14,
                      ICE if D.GROUP_OF[sh] == "冷冻" else FROST, 7))
        b.append(txt(f"{v} 件", RX + RW - 80, yy + 1, 80, None, 17, INK, W600,
                     align="END"))
    b.append(rect(RX, y2 + 234, RW, 1, HAIR))
    b.append(txt("冷藏 27 件 · 冷冻 10 件 · 合计 37 件", RX, y2 + 248, RW, None,
                 16, DIM))
    note_card(b, RX, y2 + 296, RW,
              "陈可的录入占 55%，多是她下班顺路买菜时顺手记的。",
              accent=FROST, size=16)

    footer(b, 40, 836, 1200,
           "霜标 FrostMark · 数据页界面稿；全部计数为自拟示例，非真实家庭记录")
    return canvas(W, H, "".join(b), BG)


# ══════════════════════════════════════════════════════════════════
# case-09 · 设置 —— 720×1600（2026-10-15 21:10）
# ══════════════════════════════════════════════════════════════════
def c09():
    """阈值、提醒、家庭权限、贴片电量四组设置，以及「改了会发生什么」。

    每条设置右侧都写清后果（改阈值会让告警更早或更晚触发），
    避免把装饰画成开关却解释不了作用。
    """
    S = D.SETTINGS
    b = [rect(0, 0, PHONE_W, PHONE_H, BG)]
    statusbar(b, D.STAMP["c09"])
    appbar(b, 56, "设置", back=True)

    def row(y, h, k, v, col=INK, kw=300, vw=340):
        b.append(rect(M, y, CW, h, PANEL, 10))
        b.append(txt(k, M + 18, y + (h - 22) // 2, kw, None, 17, SUB))
        b.append(txt(v, M + 18 + kw, y + (h - 22) // 2, CW - 36 - kw, None, 17,
                     col, W600, align="END"))
        return y + h + 8

    y = section(b, M, 120, CW, "温度告警", right="两名成员共用")
    y = row(y, 52, "冷藏超过多少度算告警", f"{S['cold_alert']:.1f} ℃", WARM)
    y = row(y, 52, "冷冻超过多少度算告警", f"{S['freeze_alert']:.1f} ℃".replace("-", "−"), ICE)
    y = row(y, 52, "要连续超阈多久才推送", f"{S['hold_min']} 分钟")
    y = row(y, 52, "免打扰时段", S["quiet"], DIM)
    y = para(b, "阈值调低会更早提醒，也更容易被打扰；冷冻调高到 −12.0 ℃ 之前，"
                "食物不会明显变质。", M, y, CW, 15, DIM)
    y += 16          # 原 26：与 assert_fit 抢 12px，此处收到 16

    y = section(b, M, y, CW, "提醒")
    y = row(y, 52, "剩 1 天", S["soon1"])
    y = row(y, 52, "剩 3 天", S["soon3"])
    y = row(y, 52, "温度告警发给谁", S["alert_to"], DIM)

    y += 10
    y = section(b, M, y, CW, "家庭成员", right="2 人")
    for nm, role, per, col in (("林彦", "本人", "管理员 · 可改全部阈值", SAFE),
                               ("陈可", "伴侣", "可录入 · 可收提醒", FROST)):
        b.append(rect(M, y, CW, 64, PANEL, 12))
        b.append(circle(M + 40, y + 32, 44, PANEL2, border=f'2 SOLID {col}66'))
        b.append(txt(nm[0], M + 18, y + 17, 44, None, 21, col, W600, align="CENTER"))
        b.append(txt(nm, M + 74, y + 12, 120, None, 19, INK, W600))
        b.append(txt(role, M + 74, y + 38, 120, None, 15, DIM))
        b.append(txt(per, M + 210, y + 20, 240, None, 16, SUB))
        b.append(txt("移除", M + CW - 100, y + 20, 84, None, 16, DANGER,
                     align="END"))
        y += 72
    btn(b, M, y + 4, CW, 50, "+  邀请家人", fill=None, outline="#4A5F7E", size=18)
    y += 70

    y = section(b, M, y, CW, "三枚贴片", right=f"固件 {S['firmware']}",
                right_color=DIM)
    for p in D.PATCHES:
        no, shelf = p["no"], p["shelf"]
        pct = D.BATTERY[no]
        col = SAFE if pct > 50 else WARM
        b.append(rect(M, y, CW, 62, PANEL, 12))
        patch_disc(b, M + 34, y + 31, 44, no, shell="#1E2A40",
                   shell_bd="#33455F", inner="#16223A")
        b.append(txt(shelf, M + 70, y + 10, 190, None, 19, INK, W600))
        b.append(txt("最后同步 21:08", M + 70, y + 36, 200, None, 15, DIM))
        b.append(rect(M + 330, y + 28, 200, 10, PANEL2, 5))
        b.append(rect(M + 330, y + 28, 200 * pct / 100, 10, col, 5))
        b.append(txt(f"{pct}%", M + 540, y + 12, 64, None, 17, col, W600,
                     align="END"))
        b.append(txt(f"约 {int(pct * 9 / 10)} 个月", M + 540, y + 36, 84, None,
                     14, DIM, align="END"))
        y += 70
    y = para(b, "贴片通过蓝牙直连手机，不经过服务器；关掉 App 就停止上传。",
             M, y, CW, 15, DIM)
    y += 14          # 原 26：与 assert_fit 抢 12px，此处收到 14

    y = section(b, M, y, CW, "数据与隐私")
    y = row(y, 52, "导出我的记录", "CSV · 2026-08 至今", FROST)
    y = row(y, 52, "删除这个冰箱", "会同时删除 239 条记录", DANGER)
    y = row(y, 52, "霜标 版本", f"{S['firmware']}（2026-09-28 更新）", DIM)
    assert_fit(y, 1440, "c09 尾部")
    bottom_note(b)
    navbar(b, "我的")
    return canvas(PHONE_W, PHONE_H, "".join(b), BG)


# ══════════════════════════════════════════════════════════════════
# case-10 · 我的冰箱档案 —— 1120×1400（2026-10-15 21:40）
# ══════════════════════════════════════════════════════════════════
def c10():
    """把 44 天积下来的东西汇总成一张可以打印、可以导出的档案页。

    这一件换成纸面质感：档案页值得用不同于 App 的颜色和密度，
    同时所有数字都来自同一份 journey 数据。
    """
    W, H = 1120, 1400
    b = [rect(0, 0, W, H, PAPER)]
    b.append(rect(0, 0, W, 14, FROST))
    for i in range(9):                        # 纸面淡横纹
        b.append(rect(0, 40 + i * 150, W, 1, "#F0EADC"))

    b.append(txt("霜标 FrostMark · 我的冰箱档案", 48, 56, 700, None, 22, "#2A6E68", W600))
    b.append(txt("导出时间 2026-10-15 21:40 · 已连续记录 44 天", 48, 88, 700, None,
                 17, SUBD))
    b.append(txt("档案页 · 可打印", W - 288, 60, 240, None, 17, SUBD, align="END"))
    b.append(rect(48, 128, 1024, 2, "#D9D1C0"))

    def card(x, y, w, h, title, accent="#5EE0D2", sub=None):
        b.append(rect(x, y, w, h, "#FFFFFF", 14, border="1 SOLID #E2DACA"))
        b.append(rect(x + 20, y + 20, 4, 22, accent, 2))
        b.append(txt(title, x + 32, y + 17, w - 52, None, 21, INKD, W600))
        if sub:
            b.append(txt(sub, x + 32, y + 46, w - 52, None, 15, SUBD))
            return y + 76
        return y + 54

    # ── 我的账户
    LX, LW = 48, 496
    y = card(LX, 156, LW, 300, "我的账户")
    b.append(circle(LX + 82, y + 56, 96, "#E4F3F0", border="2 SOLID #5EE0D2"))
    b.append(txt("林", LX + 34, y + 30, 96, None, 40, "#2A6E68", W600,
                 align="CENTER"))
    b.append(txt("林彦", LX + 150, y + 16, 200, None, 28, INKD, W600))
    b.append(txt("冰箱拥有者 · 成员 ID SH-0830", LX + 150, y + 52, 320, None, 16, SUBD))
    b.append(txt("加入 2026-08-30 · 管理员", LX + 150, y + 78, 320, None, 16, SUBD))
    b.append(rect(LX + 20, y + 122, LW - 40, 1, "#EDE6D8"))
    for i, (v, k, col) in enumerate((("86", "手动录入（件次）", "#2A6E68"),
                                     ("9", "发现已过期", "#B4522F"),
                                     ("14", "提醒被采纳", "#2A6E68"))):
        xx = LX + 20 + i * 152
        b.append(txt(v, xx, y + 140, 140, None, 34, col, W600))
        b.append(txt(k, xx, y + 186, 140, None, 15, SUBD))

    # ── 个人贡献
    RX, RW = 576, 496
    y2 = card(RX, 156, RW, 300, "我的贡献", sub="App 里 239 件次记录，有 36% 来自我")
    rows = [("手动录入", "86 件次", "36%"), ("首日批量导入", "21 件次", "9%"),
            ("标记为吃完", "112 件次", "47%"), ("发现并丢弃", "4 件", "2%")]
    for i, (k, v, p) in enumerate(rows):
        yy = y2 + i * 50
        b.append(txt(k, RX + 20, yy, 240, None, 17, SUBD))
        b.append(txt(v, RX + 230, yy, 150, None, 18, INKD, W600, align="END"))
        b.append(txt(p, RX + RW - 90, yy, 70, None, 16, "#2A6E68", W600,
                     align="END"))
        b.append(rect(RX + 20, yy + 30, RW - 40, 1, "#F0EADC"))
    for _i, _ln in enumerate(wrap("86 + 21 + 112 + 4 = 223，占 239 件次记录中的 93%（其余为陈可录入）。", 15, LW - 40)):
        b.append(txt(_ln, LX + 20, y + 204 + _i * 20, LW - 40, None, 15, SUB))

    # ── 冰箱档案
    y3 = card(LX, 480, LW, 470, "冰箱档案")
    b.append(txt(D.FRIDGE_MODEL, LX + 20, y3, 400, None, 26, INKD, W600))
    b.append(txt("三门 · 立式", LX + LW - 160, y3 + 6, 140, None, 16, SUBD,
                 align="END"))
    for i, (k, v) in enumerate((("总容积", f"{D.FRIDGE_LITERS} L"),
                                ("冷藏 / 冷冻", f"{D.COLD_L} L / {D.FREEZE_L} L"),
                                ("购入时间", f"{D.BOUGHT}（已用 5 年 7 个月）"))):
        yy = y3 + 46 + i * 40
        b.append(txt(k, LX + 20, yy, 180, None, 17, SUBD))
        b.append(txt(v, LX + 190, yy, 286, None, 18, INKD, W600))
    b.append(rect(LX + 20, y3 + 176, LW - 40, 1, "#EDE6D8"))
    b.append(txt(f"五个层位此刻共 {D.STOCK_BEFORE} 件", LX + 20, y3 + 190, 300, None,
                 17, INKD, W600))
    for i, (sh, v) in enumerate(D.SHELF_STOCK):
        yy = y3 + 226 + i * 42
        b.append(txt(sh, LX + 20, yy, 160, None, 17, SUBD))
        b.append(rect(LX + 170, yy + 4, 230, 14, "#F0EADC", 7))
        b.append(rect(LX + 170, yy + 4, 230 * v / 12, 14,
                      "#7C9CFF" if D.GROUP_OF[sh] == "冷冻" else "#5EE0D2", 7))
        b.append(txt(f"{v} 件", LX + LW - 90, yy, 70, None, 17, INKD, W600,
                     align="END"))
    # 原单行超宽被静默裁掉（停在「…上次同」）；这里补折行版本
    for _i, _ln in enumerate(wrap("贴片 1 / 2 / 3 全部在线 · 上次同步 21:08",
                                   15, LW - 40)):
        b.append(txt(_ln, LX + 20, y3 + 440 - 30 + _i * 20, LW - 40, None, 15, SUBD))

    # ── 采购渠道
    y4 = card(RX, 480, RW, 470, "44 天的采购习惯")
    b.append(txt("共采购 7 次 · 6 类食材 · ¥126.4", RX + 20, y4, 400, None, 17, SUBD))
    for i, (nm, pct) in enumerate(D.CHANNELS):
        yy = y4 + 42 + i * 66
        b.append(txt(nm, RX + 20, yy, 240, None, 18, INKD, W600))
        b.append(txt(f"{pct}%", RX + RW - 90, yy, 70, None, 18, "#2A6E68", W600,
                     align="END"))
        b.append(rect(RX + 20, yy + 30, RW - 40, 14, "#F0EADC", 7))
        b.append(rect(RX + 20, yy + 30, (RW - 40) * pct / 50, 14, "#5EE0D2", 7))
    b.append(rect(RX + 20, y4 + 248, RW - 40, 1, "#EDE6D8"))
    b.append(txt("丢掉的 6 件", RX + 20, y4 + 264, 240, None, 18, INKD, W600))
    for i, (k, v) in enumerate((("叶菜", "4 件"), ("牛奶", "1 件"), ("剩饭", "1 件"))):
        xx = RX + 20 + i * 152
        b.append(txt(v, xx, y4 + 296, 140, None, 26, "#B4522F", W600))
        b.append(txt(k, xx, y4 + 334, 140, None, 15, SUBD))
    b.append(txt("App 在第 3 周之后每周至少提示过一次「别再买了」。",
                 RX + 20, y4 + 374, RW - 40, None, 15, SUBD))

    # ── 家庭与饮食
    y5 = card(LX, 980, LW, 300, "家庭与饮食")
    for i, (nm, role, cnt) in enumerate(D.MEMBERS):
        yy = y5 + i * 58
        b.append(circle(LX + 44, yy + 26, 48, "#E4F3F0", border="2 SOLID #5EE0D2"))
        b.append(txt(nm[0], LX + 20, y5 + 12 + i * 58, 48, None, 22, "#2A6E68",
                     W600, align="CENTER"))
        b.append(txt(nm, LX + 82, yy + 2, 120, None, 19, INKD, W600))
        b.append(txt(role, LX + 82, yy + 28, 260, None, 15, SUBD))
        b.append(txt(f"{cnt} 件次", LX + LW - 160, yy + 10, 140, None, 18, INKD,
                     W600, align="END"))
    b.append(rect(LX + 20, y5 + 128, LW - 40, 1, "#EDE6D8"))
    for i, (k, v) in enumerate((("人数", "2 人"), ("餐次", "每天 2 餐"),
                                ("忌口", "不吃香菜"), ("采购频率", "每周 3.4 次"))):
        yy = y5 + 146 + (i % 2) * 48
        xx = LX + 20 + (i // 2) * 238
        b.append(txt(k, xx, yy, 100, None, 16, SUBD))
        b.append(txt(v, xx + 100, yy, 138, None, 18, INKD, W600))

    # ── 导出与隐私
    y6 = card(RX, 980, RW, 300, "导出与隐私")
    exports = [("2026 年 9 月家庭食材月报", "PDF · 1.2 MB"),
               ("原始记录（239 条）", "CSV · 34 KB")]
    for i, (k, v) in enumerate(exports):
        yy = y6 + i * 62
        b.append(rect(RX + 20, yy, RW - 40, 52, "#F7F4ED", 10))
        b.append(txt(k, RX + 36, yy + 8, 320, None, 17, INKD, W600))
        b.append(txt(v, RX + 36, yy + 30, 320, None, 15, SUBD))
        b.append(txt("导出", RX + RW - 96, yy + 15, 76, None, 17, "#2A6E68", W600,
                     align="END"))
    for _i, _ln in enumerate(wrap("贴片只通过蓝牙直连手机，不经过我们的服务器；删掉这个冰箱会同时删掉全部 239 条记录。", 15, LW - 40)):
        b.append(txt(_ln, RX + 20, y6 + 190 + _i * 20, RW - 40, None, 15, SUBD))

    footer(b, 48, 1330, 1024,
           "霜标 FrostMark · 档案页设计稿；型号、成员与全部计数为自拟示例，非真实家庭记录",
           color=SUBD, line_color="#D9D1C0", size=17)
    return canvas(W, H, "".join(b), PAPER)


CASES_B = [c05, c06, c07, c08, c09, c10]
