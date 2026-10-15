#!/usr/bin/env python
# B05 · 「霜标 FrostMark」十件连续旅程界面。
# 用法：python build_b05.py [all|1..10] [ver]
# 启动基准：总任务根 (suite_root)。
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B05"))
from bsnap import W500, W600, canvas, circle, em_width, line_h, rect, segment, txt, wrap

import b05data as D
from b05kit import (BG, CW, DANGER, DIM, FROST, FOOTER_NOTE, HAIR, ICE, INK, INKD,
                    KRAFT, M, MUTED, NAV_TOP, PAPER, PAPER2, PANEL, PANEL2,
                    PHONE_H, PHONE_W, RULED, SAFE, SUB, SUBD, WARM, assert_fit,
                    appbar, band, bottom_note, btn, check_box, chevron, day_text,
                    footer, fridge_block, group_label, kv, navbar, note_card,
                    para, patch_chip, patch_disc, section, shelf_header, statusbar)

DRAFTS = ROOT / "tmp/run-20261011-01/B05/drafts"

FOOTER_NOTE_PAPER = "霜标 FrostMark · 开箱卡设计稿；配件清单与包装为自拟示例，非真实发货记录"


# ══════════════════════════════════════════════════════════════════
# case-01 · 开箱内衬卡（俯视）—— 1320×960
# ══════════════════════════════════════════════════════════════════
def c01():
    """硬件开箱：盒内五格 + 包装清单 + 三步贴法。

    这是整套里唯一一件「不是界面」的画面——它是用户第一次接触产品时
    手上真正拿到的那张卡。贴片实物用几何画，并在卡上写明「实物以收到为准」。
    """
    W, H = 1320, 960
    b = [rect(0, 0, W, H, KRAFT)]
    # 桌面：几道很淡的横向压痕，避免大面积纯色发闷
    for i in range(14):
        b.append(rect(0, 40 + i * 68, W, 1, "#D9CFBB"))

    # ── 标题区
    b.append(txt("FROSTMARK 霜标 · 开箱内衬卡", 48, 44, 700, None, 20, "#8A6A2F", W600))
    b.append(txt("贴在冰箱里最能代表整箱的位置", 48, 74, 900, None, 34, INKD, W600))
    b.append(txt("三枚贴片 + 一张说明卡。装好之后，App 才会开始替你盯着温度。",
                 48, 124, 900, None, 18, SUBD))

    # ── 盒托
    TX, TY, TW, TH = 48, 170, 780, 530
    b.append(rect(TX + 9, TY + 11, TW, TH, "#C9BEA6", 26))            # 盒体投影
    b.append(rect(TX, TY, TW, TH, PAPER, 26, border="1 SOLID #DCD3C0"))
    # 内衬五格
    wells = [("a", 72, 194, 404, 244), ("b", 492, 194, 178, 244), ("c", 686, 194, 118, 244),
             ("d", 72, 452, 452, 200), ("e", 540, 452, 264, 200)]
    for _k, x, y, w, h in wells:
        b.append(rect(x, y, w, h, PAPER2, 14, border="1 SOLID #E2DACA"))

    # 格 A：三枚贴片
    b.append(txt("霜标贴片 ×3", 92, 210, 300, None, 19, INKD, W600))
    b.append(txt("出厂已配对", 92, 236, 300, None, 15, SUBD))
    for i in range(3):
        patch_disc(b, 144 + i * 130, 334, 104, i + 1)
        b.append(txt(f"贴片 {i + 1}", 92 + i * 130, 394, 104, None, 16, SUBD,
                     align="CENTER"))
    # 格 B：磁吸底座
    b.append(txt("磁吸底座", 508, 210, 146, None, 17, INKD, W600))
    b.append(circle(581, 318, 96, "#E7EBF1", border="2 SOLID #C2CBD8"))
    b.append(circle(581, 318, 54, "#F7F9FC", border="1 SOLID #C2CBD8"))
    b.append(txt("×1", 508, 374, 146, None, 16, SUBD, align="CENTER"))
    # 格 C：镊子（两条细长条 + 尖端）
    b.append(txt("镊子", 700, 210, 90, None, 17, INKD, W600))
    b.append(segment(716, 252, 739, 392, "#9AA6B6", 5))
    b.append(segment(764, 252, 739, 392, "#9AA6B6", 5))
    b.append(circle(739, 396, 14, "#8D9AAD"))
    b.append(txt("×1", 700, 408, 90, None, 16, SUBD, align="CENTER"))
    # 格 D：说明卡
    b.append(txt("纸质说明卡", 92, 462, 300, None, 17, INKD, W600))
    b.append(rect(92, 494, 412, 144, "#FFFFFF", 8, border="1 SOLID #DCD3C0"))
    b.append(rect(92, 494, 412, 6, FROST, 3))
    b.append(txt("霜标 开箱说明 · 第 1 版", 110, 510, 380, None, 18, INKD, W600))
    for i, s in enumerate(["① 三枚贴片分别贴在哪一层", "② 撕开 3M 背贴，按压 10 秒",
                           "③ 指示点转常亮＝校准完成"]):
        b.append(txt(s, 110, 542 + i * 30, 380, None, 16, SUBD))
    # 格 E：备用背贴 ×6
    b.append(txt("备用 3M 背贴 ×6", 560, 462, 240, None, 17, INKD, W600))
    for i in range(6):
        b.append(rect(564 + (i % 3) * 76, 496 + (i // 3) * 76, 66, 66, "#FFFFFF", 8,
                      border="1 SOLID #D6CDBA"))
        b.append(rect(586 + (i % 3) * 76, 518 + (i // 3) * 76, 22, 22, "#D9E6E3", 6))

    # ── 右栏：包装内含 5 件
    RX, RW = 868, 404
    b.append(txt("包装内含 5 件", RX, 170, RW, None, 22, INKD, W600))
    b.append(rect(RX, 208, RW, 1, RULED))
    contents = [("霜标贴片", "×3", "已配对"), ("磁吸充电底座", "×1", ""),
                ("镊子", "×1", "换位置用"), ("纸质说明卡", "×1", ""),
                ("备用 3M 背贴", "×6", "一季一换")]
    for i, (nm, qty, note) in enumerate(contents):
        y = 218 + i * 54
        check_box(b, RX, y + 4)
        b.append(txt(nm, RX + 34, y + 2, 250, None, 18, INKD))
        if note:
            b.append(txt(note, RX + 34, y + 24, 220, None, 14, SUBD))
        b.append(txt(qty, RX + RW - 70, y + 3, 70, None, 18, SUBD, W600, align="END"))
    b.append(rect(RX, 508, RW, 1, RULED))
    b.append(txt("三枚贴片出厂满电", RX, 528, RW, None, 20, INKD, W600))
    for i in range(3):
        y = 564 + i * 26
        b.append(txt(f"贴片 {i + 1}", RX, y, 90, None, 16, SUBD))
        b.append(rect(RX + 78, y + 4, 258, 10, "#E2DACA", 5))
        b.append(rect(RX + 78, y + 4, 258, 10, SAFE, 5))
        # 「100%」共 4 个字符：3 个数字 + %，15px 下约 37px；盒宽必须给够，
        # 首版给了 38px 仍被服务端换行裁掉最后一个字符（图上只剩「100」）。
        b.append(txt("100%", RX + 344, y - 1, 60, None, 15, SAFE, align="END"))
    para(b, "标称续航 9 个月；App 会在剩余 15% 时提醒你取下来充电。",
         RX, 650, RW, 15, SUBD)

    # ── 底部三步
    steps = [("① 给贴片命名", "打开 App 蓝牙连上三枚贴片，逐枚起名字并选位置："
                             "冷藏中层、冷藏下层、冷冻室。"),
             ("② 撕背贴上墙", "贴片背面自带 3M 胶。撕开保护膜按 App 标的位置贴牢，"
                             "按压 10 秒再松手。"),
             ("③ 等 15 分钟校准", "指示点由慢闪转常亮即校准完成。校准完成前不要挪位置，"
                                "否则第一次读数会偏。")]
    for i, (t, d) in enumerate(steps):
        x = 48 + i * 416
        b.append(rect(x, 724, 392, 142, PAPER, 14, border="1 SOLID #DCD3C0"))
        b.append(rect(x, 724, 392, 4, [FROST, WARM, SAFE][i], 2))
        b.append(txt(t, x + 20, 740, 352, None, 21, INKD, W600))
        yy = para(b, d, x + 20, 776, 352, 17, SUBD)
        assert yy <= 724 + 142 - 6, f"c01 step{i + 1} 文字溢出"

    footer(b, 48, 890, 1224, FOOTER_NOTE_PAPER, color=SUBD, line_color="#CFC6B2")
    return canvas(W, H, "".join(b), KRAFT)


# ══════════════════════════════════════════════════════════════════
# case-02 · 首启：给三枚贴片命名 —— 720×1600（2026-08-30 10:12）
# ══════════════════════════════════════════════════════════════════
def c02():
    """装好硬件后的第一屏：蓝牙已连上，用户给三枚贴片起名字并选位置。

    这一屏解释了整个产品的「名字从哪来」——后面每一屏的温度读数、告警文案、
    数据筛选都用这里起的名字，是跨屏一致性的起点。
    """
    b = [rect(0, 0, PHONE_W, PHONE_H, BG)]
    statusbar(b, D.STAMP["c02"])

    y = appbar(b, 56, "霜标 FrostMark", action="第 2 步 / 共 3 步", back=False)
    # 进度条：3 段，已完成 2 段
    for i in range(3):
        b.append(rect(M + i * 224, y, 216, 6, FROST if i < 2 else PANEL2, 3))
    y += 26

    b.append(txt("给三枚贴片起名字", M, y, CW, None, 27, INK, W600))
    y += 40
    y = para(b, "蓝牙已连上三枚贴片。给每一枚起个你叫顺口的名字，"
                "之后 App 就用这个名字报温度。", M, y, CW, 17, SUB)

    # 三枚贴片的命名行
    names = [("1", "冷藏中层", "高度 1/3 处", 4.0),
             ("2", "冷藏下层", "果蔬抽屉上层", 5.0),
             ("3", "冷冻室", "冷冻层中部", -18.0)]
    y = 262
    for no, nm, where, target in names:
        b.append(rect(M, y, CW, 124, PANEL, 14))
        patch_disc(b, M + 50, y + 62, 76, no, shell="#1E2A40",
                   shell_bd="#33455F", inner="#16223A")
        # 名称输入框
        b.append(rect(130, y + 18, 262, 48, PANEL2, 10, border="1 SOLID #2C3E5C"))
        b.append(txt(nm, 146, y + 29, 232, None, 22, INK, W600))
        # 「目标 X ℃」：标签与数值首版都排在 y+78，互相压在一起（看图才发现）。
        # 现在标签在左、数值紧跟，位置说明右对齐到 404，三段互不相交。
        b.append(txt("目标", 146, y + 82, 46, None, 15, DIM))
        tv = f"{target:.1f} ℃".replace("-", "−")
        b.append(txt(tv, 196, y + 77, 110, None, 19, FROST, W600))
        b.append(txt(where, 290, y + 82, 114, None, 15, DIM, align="END"))
        # 右侧连接状态
        b.append(rect(414, y + 22, 108, 34, SAFE + "26", 17, border=f'1 SOLID {SAFE}88'))
        b.append(txt("已连接", 414, y + 29, 108, None, 17, SAFE, W600, align="CENTER"))
        b.append(txt("蓝牙 −48 dBm", 414, y + 70, 140, None, 15, DIM))
        b.append(txt("剩余 22 个月", 560, y + 70, 130, None, 15, DIM, align="END"))
        y += 136

    # 家庭成员
    y = section(b, M, 692, CW, "冰箱有几位？", right="稍后再说")
    b.append(txt("谁往里放东西就邀请谁。成员只能看到冰箱，App 不会读取通讯录。",
                 M, y - 6, CW, None, 16, DIM))
    y += 26
    members = [("林彦", "本人", "管理员 · 可改阈值", "已加入", SAFE),
               ("陈可", "伴侣", "可录入 · 可收提醒", "已接受邀请", FROST)]
    for nm, rel, right, st, col in members:
        b.append(rect(M, y, CW, 72, PANEL, 12))
        b.append(circle(M + 42, y + 36, 48, PANEL2, border=f'2 SOLID {col}66'))
        b.append(txt(nm[0], M + 18, y + 20, 48, None, 22, col, W600, align="CENTER"))
        b.append(txt(nm, M + 80, y + 14, 120, None, 20, INK, W600))
        b.append(txt(rel, M + 80, y + 42, 200, None, 15, DIM))
        b.append(txt(right, M + 300, y + 16, 190, None, 16, SUB))
        b.append(txt(st, M + CW - 150, y + 26, 134, None, 16, col, W600, align="END"))
        y += 84
    # 首版描边用了 HAIR，标签色也是 HAER → 图上「+ 邀请家人」几乎看不见。
    btn(b, M, y + 6, CW, 54, "+  邀请家人", fill=None, outline="#4A5F7E",
        size=19, radius=12)
    y += 72

    # 位置参考（与开箱卡、首页剖面上的 1/2/3 必须一致）
    y = section(b, M, 1016, CW, "贴在最能代表整箱的位置")
    where = [("冷藏中层", "高度 1/3 处", 1, 4.0),
             ("冷藏下层", "果蔬抽屉上层", 2, 5.0),
             ("冷冻室", "冷冻层中部", 3, -18.0)]
    y += 6
    for nm, desc, no, tg in where:
        b.append(rect(M, y, CW, 72, PANEL, 12))
        b.append(rect(M, y + 13, 4, 46, FROST if no < 3 else ICE, 2))
        b.append(txt(nm, M + 22, y + 13, 180, None, 20, INK, W600))
        b.append(txt(desc, M + 22, y + 41, 200, None, 16, DIM))
        b.append(rect(M + 248, y + 23, 25, 25, FROST + "2E", 13,
                      border=f'1 SOLID {FROST}77'))
        b.append(txt(str(no), M + 248, y + 28, 25, None, 16, FROST, W600,
                     align="CENTER"))
        b.append(txt("贴片", M + 282, y + 28, 60, None, 16, DIM))
        b.append(txt(f"目标 {tg:.1f} ℃".replace("-", "−"), M + CW - 190, y + 25,
                     174, None, 18, SUB, W600, align="END"))
        y += 82
    y = para(b, "首页、告警和数据页都用这三个名字显示层位，改名会同步到全部记录。",
             M, y + 4, CW, 17, DIM)
    assert_fit(y, 1360, "c02 位置参考")

    btn(b, M, 1372, CW, 64, "下一步：贴到冰箱上", fill=FROST, size=21)
    b.append(rect(0, 1460, PHONE_W, PHONE_H - 1460, PANEL, 0))
    b.append(rect(0, 1460, PHONE_W, 1, HAIR))
    b.append(txt("还没贴好？App 会等你 —— 三枚贴片全部到位后才开始记录温度。",
                 M, 1478, CW, None, 17, DIM))
    bottom_note(b)
    assert_fit(1372 + 64, 1460, "c02 主按钮")
    return canvas(PHONE_W, PHONE_H, "".join(b), BG)


# ══════════════════════════════════════════════════════════════════
# case-03 · 装机首日首页 —— 720×1600（2026-08-30 19:40）
# ══════════════════════════════════════════════════════════════════
def c03():
    """第 0 天的空冰箱：五个层位只有三个格子有东西。

    与 case-04 的满载首页刻意构成对照——同一个视图、同一套规则，
    差别只在「用户告诉 App 了多少」。
    """
    b = [rect(0, 0, PHONE_W, PHONE_H, BG)]
    statusbar(b, D.STAMP["c03"])
    appbar(b, 56, "冰箱", action="贴片 3/3 在线", back=False)

    temps = {"冷藏中层": (3.8, "正常"), "冷藏下层": (4.6, "正常"),
             "冷冻上层": (-19.4, "正常")}
    for i, (no, shelf, t, st) in enumerate(
            [(1, "冷藏中层", 3.8, "正常"), (2, "冷藏下层", 4.6, "正常"),
             (3, "冷冻室", -19.4, "正常")]):
        patch_chip(b, M + i * 225, 116, no, shelf, t, st, cw=214, ch=84)

    data = {"冷藏中层": [("鸡蛋", 14)], "冷藏下层": [("蓝莓", 5)],
            "冷冻下层": [("速冻饺子", 60)]}
    y = fridge_block(b, 16, 216, 688, data, temps)

    y = section(b, M, y + 18, CW, "今晚记下的 3 样", right="19:40 · 林彦")
    logged = [("鸡蛋", "8 枚", "冷藏中层", "保质期到 09-13"),
              ("蓝莓", "1 盒", "冷藏下层", "保质期到 09-04"),
              ("速冻饺子", "1 包", "冷冻下层", "保质期到 10-29")]
    for nm, qty, sh, exp in logged:
        b.append(rect(M, y, CW, 60, PANEL, 12))
        b.append(rect(M, y + 14, 4, 32, FROST, 2))
        b.append(txt(nm, M + 22, y + 16, 150, None, 20, INK, W600))
        b.append(txt(qty, M + 180, y + 19, 90, None, 17, SUB))
        b.append(txt(sh, M + 280, y + 20, 150, None, 17, SUB))
        b.append(txt(exp, M + CW - 230, y + 20, 214, None, 16, DIM, align="END"))
        y += 68

    y = para(b, "App 只知道你告诉它的事。空层位不会自己长出食材。", M, y + 6, CW, 17, DIM)
    y = note_card(b, M, y + 8, CW,
                  "三天后 App 会做第一件事：按你记的层位和到期日，"
                  "挑出最先到期的那几样，放进建议页。",
                  accent=WARM)
    btn(b, M, y + 14, CW, 56, "再记一笔", fill=None, outline=FROST, size=20)
    y += 84

    # 设置完成度：首启页唯一还欠的一件事，让用户知道下一步是什么
    b.append(rect(M, y, CW, 96, PANEL, 12))
    b.append(txt("设置完成度", M + 18, y + 16, 300, None, 18, INK, W600))
    b.append(txt("3 / 4 项", M + CW - 140, y + 17, 122, None, 17, FROST, W600,
                 align="END"))
    for i in range(4):
        b.append(rect(M + 18 + i * 160, y + 48, 152, 8, FROST if i < 3 else PANEL2, 4))
    b.append(txt("还差：让陈可也装上霜标，她录的东西你才看得到。",
                 M + 18, y + 66, CW - 36, None, 16, DIM))
    y += 96
    assert_fit(y, 1440, "c03 尾部")
    bottom_note(b)
    navbar(b, "冰箱")
    return canvas(PHONE_W, PHONE_H, "".join(b), BG)


# ══════════════════════════════════════════════════════════════════
# case-04 · 第 44 天首页 —— 720×1600（2026-10-13 16:20）
# ══════════════════════════════════════════════════════════════════
def c04():
    """用了 44 天之后的首页：37 件在库、4 件 3 天内到期、三枚贴片全部正常。"""
    b = [rect(0, 0, PHONE_W, PHONE_H, BG)]
    statusbar(b, D.STAMP["c04"])
    appbar(b, 56, "冰箱", action="林彦 +1", back=False)

    reads = [(1, "冷藏中层", 4.1, "正常", 4.0), (2, "冷藏下层", 4.9, "正常", 5.0),
             (3, "冷冻室", -18.6, "正常", -18.0)]
    for i, (no, sh, t, st, tg) in enumerate(reads):
        patch_chip(b, M + i * 225, 116, no, sh, t, st, cw=214, ch=84, target=tg)

    data = {sh: [(nm, d) for nm, _q, d in D.ITEMS[sh]] for sh in D.SHELVES}
    temps = {"冷藏中层": (4.1, "正常"), "冷藏下层": (4.9, "正常"),
             "冷冻上层": (-18.6, "正常")}
    y = fridge_block(b, 16, 216, 688, data, temps)

    # 临期清单：4 件，与 D.SOON_BEFORE 同源
    y = section(b, M, y + 16, CW, "3 天内到期 4 件",
                right=f"在库 {D.STOCK_BEFORE} 件")
    for nm, sh, qty, days in D.SOON_BEFORE:
        col = band(days)
        b.append(rect(M, y, CW, 58, PANEL, 12))
        b.append(rect(M, y + 14, 4, 30, col, 2))
        # 首版把「1 盒 · 冷藏上层」排在第二行（y+39），28px 行盒越过 58px 卡底，
        # 图上这行字挂在卡外。现在名称与规格同行，卡内三行变两行。
        b.append(txt(nm, M + 22, y + 17, 150, None, 20, INK, W600))
        b.append(txt(f"{qty} · {sh}", M + 182, y + 20, 250, None, 17, SUB))
        b.append(rect(M + CW - 128, y + 17, 112, 26, col + "26", 13))
        b.append(txt(day_text(days), M + CW - 128, y + 20, 112, None, 16, col,
                     W600, align="CENTER"))
        y += 66

    y = para(b, "剩饭 和 鸡胸肉 都在冷藏中层。今晚的「先吃这些」会把它们排在前两位。",
             M, y + 6, CW, 17, DIM)

    y = section(b, M, y + 14, CW, "家庭动态")
    b.append(rect(M, y, CW, 52, PANEL, 10))
    b.append(circle(M + 28, y + 26, 30, PANEL2, border=f"2 SOLID {FROST}66"))
    b.append(txt("可", M + 13, y + 15, 30, None, 17, FROST, W600, align="CENTER"))
    b.append(txt("陈可 16:02 拿走 酸奶 1 盒", M + 54, y + 14, 400, None, 17, INK))
    b.append(txt("冷藏中层", M + CW - 180, y + 15, 164, None, 15, DIM, align="END"))
    assert_fit(y + 52, 1440, "c04 尾部")
    bottom_note(b)
    navbar(b, "冰箱")
    return canvas(PHONE_W, PHONE_H, "".join(b), BG)


CASES = [c01, c02, c03, c04]

from cases_b05b import CASES_B
CASES = CASES + CASES_B

SIZES = [(1320, 960), (720, 1600), (720, 1600), (720, 1600), (720, 1600),
         (720, 1600), (1280, 900), (1280, 900), (720, 1600), (1120, 1400)]

def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    idx = range(len(CASES)) if which == "all" else [int(which) - 1]
    for i in idx:
        p = DRAFTS / f"b05-{i + 1:02d}-{ver}.snapshot"
        p.write_text(CASES[i](), encoding="utf-8")
        print(f"-> {p.name}  {SIZES[i][0]}x{SIZES[i][1]}  {p.stat().st_size}B")


if __name__ == "__main__":
    main()

