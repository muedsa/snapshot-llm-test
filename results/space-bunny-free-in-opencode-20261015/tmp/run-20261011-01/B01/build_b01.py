#!/usr/bin/env python
# B01 作品集生成器：十张体现实质不同任务的用例图。
# 每件都是独立的 DSL + 独立的内容，不复用同一张卡片换皮。
# 启动基准：总任务根 (suite_root)。用法：python build_b01.py [case_index|all] [ver]
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
from bsnap import (BG, DIM, INK, LINE, PANEL, PANEL2, SERIES, SUB, W500, W600,
                   bullets, canvas, circle, em_width, fmt, hbars, header, kpi_row,
                   line_h, nice_max, para, polyline, rect, txt, vbars, footer,
                   wrap, segment)

OUT = ROOT / "outputs/run-20261011-01/B01"
DRAFTS = ROOT / "tmp/run-20261011-01/B01/drafts"


# ══════════════════════════════════════════════ 01 末班车与换乘窗口
def case01():
    """城市夜间出行：末班车倒计时与换乘可行性。

    受众是夜里准备出发的乘客。真正要回答的是一句话：
    「我现在出发，能不能赶上最后一班车，在换乘截止前到得了？」
    所以视觉主体是一条**倒着数的时刻轴**：每一站往右就是越晚，
    乘客的当前位置用一条竖线钉在轴上，线右边还剩多少可换乘窗口一目了然。
    """
    W, H = 1440, 900
    b = [rect(0, 0, W, H, BG)]
    # 数据（自拟，模拟某市地铁 2 号线末班车班次）
    # 站名, 末班车发车分钟(23:00=0), 换乘窗口分钟, 换乘说明
    rows = [
        ("人民广场", 46, 8, "起点站"),
        ("南京西路", 53, 5, "2 号线 → 12 号线"),
        ("静安寺", 59, 4, "2 号线 → 7 号线"),
        ("徐家汇", 67, 6, "2 号线 → 9 号线"),
        ("龙华中路", 75, 3, "无换乘"),
        ("锦绣路", 82, 5, "2 号线 → 17 号线"),
        ("罗山路", 90, 7, "终点站"),
    ]
    X0, X1 = 560, 1388
    Y0 = 424               # 轴线：KPI 卡到 334，上面还要放小时标签与「现在」标记
    vmax = 96
    px = lambda m: X0 + (X1 - X0) * m / vmax          # noqa: E731
    now = 7

    b.extend(rect(0, 0, W, 4, SERIES[0], 0))
    y = header(b, 72, 48, W - 144, "案例 01 · 城市夜间出行",
               "末班车还有多久",
               "每一站的发车时刻、车上耗时与换乘窗口画在同一条时间轴上")
    kpi_row(b, 72, y + 16, W - 144, [
        ("当前时间", "23:07", SERIES[0], "距末班首站 39 分钟"),
        ("末班车到达终点", "00:30", SERIES[1], "罗山路"),
        ("最紧的换乘窗口", "3 分钟", SERIES[3], "龙华中路"),
        ("建议出发", "立即", SERIES[2], "可赶上全部 7 站"),
    ])

    b.append(txt("时间轴（分钟，23:00 = 0）", 72, 352, 400, None, 20, SUB))
    b.append(txt("现在 23:07", px(now) - 80, 352, 160, None, 20, SERIES[2], W600,
                 align="CENTER"))
    for m in range(0, vmax + 1, 12):
        major = m % 60 == 0
        b.append(rect(px(m), Y0 - 12, 1, 396, LINE if major else "#1B2740"))
        if m % 30 == 0:
            # 起点是 23:00，跨零点后小时要回绕——首版写成 9 + m//60，画出了「09:00」
            b.append(txt(f"{(23 + m // 60) % 24:02d}:{m % 60:02d}",
                         px(m) - 40, 384, 80, None, 20, DIM, align="CENTER"))
    b.append(rect(px(now), Y0 - 16, 3, 400, SERIES[2]))

    for i, (name, last, window, transfer) in enumerate(rows):
        ry = Y0 + i * 50
        tight = window <= 4
        b.append(txt(name, 72, ry + 2, 180, None, 22, INK, W600 if i == 0 else W500))
        b.append(txt(transfer, 244, ry + 5, 170, None, 18, DIM))
        # 换乘窗口放在左栏文字里，不画在时间轴上：
        # 首版把它画在时刻点右侧，和「末班 HH:MM」标签压在一起。
        b.append(txt(f"窗口 {window} 分", 424, ry + 5, 120, None, 18,
                     SERIES[3] if tight else SERIES[1]))
        # 可乘窗口：现在 → 末班车发车
        b.append(rect(px(now), ry, px(last) - px(now), 26, SERIES[0] + "33", 6))
        b.append(rect(px(now) - 2, ry - 3, 5, 32, SERIES[2], 3))
        b.append(rect(px(last) - 5, ry - 4, 11, 34, SERIES[0], 4))
        hh = 23 + (last // 60)
        mm = last % 60
        b.append(txt(f"末班 {hh:02d}:{mm:02d}", px(last) - 66, ry + 30, 132, None, 19,
                     SERIES[0], W600, align="CENTER"))
        if tight:
            b.append(circle(px(last) - 40, ry + 13, 13, SERIES[3]))

    footer(b, 72, H - 84, W - 144,
           "数据为自拟示例（模拟某市地铁 2 号线夜间班次），非实际运营数据；"
           "窗口按「同站换乘需在末班车到站后 N 分钟内完成」建模。")
    return canvas(W, H, "".join(b))

# ══════════════════════════════════════════════ 02 共享设备预约冲突
def case02():
    """科研共享设备预约：谁和谁撞了。

    受众是预约大型设备的实验室成员。真正要回答的是：
    「我提交的时段和别人冲突了吗？谁占了下一档？」
    视觉主体是**设备 × 时段的热力矩阵**：冲突格子用高饱和红并写上冲突编号，
    空档用暗色，一眼看出哪台设备在本周最抢手。
    """
    W, H = 1280, 1200
    b = [rect(0, 0, W, H, BG)]
    dev = ["共聚焦显微镜", "流式细胞仪", "冻干机", "PCR 阵列", "超高速离心机"]
    slots = ["周一 09–12", "周一 13–18", "周二 09–12", "周二 13–18",
             "周三 09–12", "周三 13–18", "周四 09–12", "周四 13–18"]
    # 0 空 / 1 已约 / 2 冲突（同一设备同一时段被两人同时预订）
    grid = [
        [1, 1, 1, 0, 1, 0, 0, 1],
        [0, 1, 2, 2, 1, 1, 1, 0],
        [1, 0, 1, 1, 0, 1, 1, 1],
        [1, 1, 0, 1, 1, 1, 2, 2],
        [0, 1, 1, 0, 0, 1, 1, 0],
    ]
    conflict_ids = {
        (1, 2): "C-118", (1, 3): "C-118", (3, 6): "C-131", (3, 7): "C-131",
    }
    b.extend(rect(0, 0, W, 4, SERIES[1], 0))
    y = header(b, 64, 52, W - 128, "案例 02 · 科研资源调度",
               "共享设备预约冲突",
               "5 台设备 × 8 个时段；红格表示同一时段被两人同时预订")

    kpi_row(b, 64, 208, W - 128, [
        ("本设备数", "5", SERIES[0]),
        ("预订总数", "25", SERIES[1]),
        ("冲突格数", "4", SERIES[3], "涉及 2 起事件"),
        ("空闲率", "26%", SERIES[2]),
    ])

    X0, X1 = 300, 1216
    Y0 = 388
    cw = (X1 - X0) / len(slots)
    ch = 86
    for j, s in enumerate(slots):
        b.append(txt(s, X0 + cw * j, Y0 - 34, cw, None, 19, SUB, align="CENTER"))
    for i, d in enumerate(dev):
        ry = Y0 + i * (ch + 12)
        b.append(txt(d, 64, ry + 24, 224, None, 22, INK))
        for j, s in enumerate(slots):
            v = grid[i][j]
            cx = X0 + cw * j
            col = {0: "#101A2C", 1: SERIES[0] + "44", 2: SERIES[3] + "66"}[v]
            b.append(rect(cx + 3, ry, cw - 6, ch, col, 8,
                          border=f'1 SOLID {SERIES[3]}' if v == 2 else None))
            if v == 1:
                b.append(txt("已约", cx + 3, ry + 30, cw - 6, None, 20, SERIES[0],
                             align="CENTER"))
            elif v == 2:
                cid = conflict_ids.get((i, j), "")
                b.append(txt("冲突", cx + 3, ry + 18, cw - 6, None, 22, SERIES[3],
                             W600, align="CENTER"))
                b.append(txt(cid, cx + 3, ry + 46, cw - 6, None, 18, "#FFD9E2",
                             align="CENTER"))
            else:
                b.append(txt("空闲", cx + 3, ry + 30, cw - 6, None, 20, DIM,
                             align="CENTER"))

    y = Y0 + len(dev) * (ch + 12) + 24
    b.append(txt("冲突明细", 64, y, 400, None, 28, INK, W600))
    y = bullets(b, [
        "C-118 · 流式细胞仪 · 周二 09–12 与 13–18 连续两格重叠；"
        "两位预约人分别为「李岚」与「周珩」，系统在周二 08:40 先后收到两条提交。",
        "C-131 · PCR 阵列 · 周四 13–18 重叠；预约人「陈禾」与「M. Ito」，"
        "两次提交间隔仅 3 分钟，第二次提交在事务并发窗口内通过了唯一性检查。",
    ], 64, y + 42, W - 128, 21)
    footer(b, 64, H - 108, W - 128,
           "数据为自拟示例（模拟某高校公共仪器平台一周排期）；"
           "冲突判定规则：同一设备、同一时段、两条及以上有效预订即为冲突。")
    return canvas(W, H, "".join(b))


# ══════════════════════════════════════════════ 03 咖啡烘焙曲线
def case03():
    """精品咖啡烘焙：把一次烘焙的温度与时间控制讲清楚。

    受众是准备自己烘豆的爱好者。他们要判断的是：
    「这一炉的火力够不够？发展时间落在合格区吗？」
    视觉主体是**豆温曲线 + 关键事件刻度**：转折点（回温点、转黄、一爆）用竖线钉在
    曲线上，下方用色带标出发展时间窗口与合格区。
    """
    W, H = 1440, 900
    b = [rect(0, 0, W, H, BG)]
    # 两炉对照：北纬 18° 水洗（浅焙）vs 哥伦比亚 曼特宁（深焙），同一台烘豆机
    t = [0, 1.5, 3, 4.5, 6, 7.5, 9, 10, 11, 11.5, 12, 13, 14]
    light = [198, 126, 168, 184, 190, 193, 196, 198, 199, 200, 200, 200, 200]
    dark = [204, 132, 174, 188, 196, 202, 206, 209, 210, 211, 211, 211, 211]
    events = [("回温点", 1.5, SERIES[2]), ("转黄", 7.5, SERIES[4]),
              ("一爆", 9.0, SERIES[3]), ("下豆", 11.5, SERIES[0])]
    dev_lo, dev_hi = 7.8, 10.2           # 发展时间合格窗口（分钟）

    b.extend(rect(0, 0, W, 4, SERIES[3], 0))
    y = header(b, 72, 48, W - 144, "案例 03 · 食品工艺控制",
               "一炉咖啡的 13 分钟",
               "豆温曲线、转黄与一爆时刻，以及发展时间是否落在合格窗口")

    y = kpi_row(b, 72, y + 16, W - 144, [
        ("入豆温", "198 / 204 °C", SERIES[2], "浅焙 / 深焙"),
        ("转折点", "1 分 30 秒", SERIES[4], "两炉同时"),
        ("一爆", "9 分 00 秒", SERIES[3], "浅焙深焙相近"),
        ("发展时间", "2 分 30 秒", SERIES[1], "合格 2.4–3.0 分"),
        ("下豆总时长", "11 分 30 秒", SERIES[0], "浅焙"),
    ])

    X0, X1 = 168, 1130
    Y0, Y1 = y + 84, 636
    tmax = 14.0
    tx = lambda m: X0 + (X1 - X0) * m / tmax                    # noqa: E731
    tlo, thi = 120, 215
    ty = lambda v: Y1 - (Y1 - Y0) * (v - tlo) / (thi - tlo)     # noqa: E731

    # 合格发展窗口色带（画在 x 轴上方的带子里）
    b.append(rect(tx(dev_lo), Y1 + 8, tx(dev_hi) - tx(dev_lo), 22,
                  SERIES[1] + "33", 6))
    b.append(txt("发展时间合格窗口 7.8–10.2 分", tx(dev_lo), Y1 + 11,
                 tx(dev_hi) - tx(dev_lo), None, 18, SERIES[1], align="CENTER"))

    for v in range(120, 220, 20):
        b.append(rect(X0 - 10, ty(v), X1 - X0 + 10, 1, LINE))
        b.append(txt(f"{v}°", X0 - 78, ty(v) - 13, 62, None, 19, DIM, align="END"))
    for m in range(0, 15, 2):
        b.append(rect(tx(m), Y0 - 8, 1, Y1 - Y0 + 16, LINE))
        b.append(txt(f"{m}′", tx(m) - 30, Y1 + 40, 60, None, 19, DIM,
                     align="CENTER"))

    # 曲线：两条实线（首版画成了一串圆点，改用旋转长条画线段）
    for series, col, dy in ((light, SERIES[0], 0), (dark, SERIES[1], 16)):
        pts = [(tx(m), ty(v) + dy) for m, v in zip(t, series)]
        b.append(polyline(pts, col, 4))
    # 图例（放在绘图区外的右侧，不随曲线循环重复画）
    LX = X1 + 40
    b.append(txt("豆温 °C", LX, Y0 - 10, 180, None, 19, SUB))
    for j, (nm, col) in enumerate((("浅焙 · 埃塞 北纬 18°", SERIES[0]),
                                  ("深焙 · 印尼 曼特宁", SERIES[1]))):
        ly = Y0 + 20 + j * 34
        b.append(segment(LX, ly + 10, LX + 34, ly + 10, col, 5))
        b.append(txt(nm, LX + 46, ly, 200, None, 20, col))

    for nm, m, col in events:
        b.append(rect(tx(m), Y0 - 8, 2, Y1 - Y0 + 16, col + "77"))
        b.append(txt(nm, tx(m) - 50, Y0 - 42, 100, None, 19, col, W600,
                     align="CENTER"))

    yb = Y1 + 92
    bullets(b, [
        "两炉的转折点几乎同时出现（1 分 30 秒），说明入豆量与滚筒热容匹配；",
        "深焙在 6 分钟后把豆温再拉高 6 °C，弥补了曼特宁密度大、吸热慢的差异；",
        "浅焙下豆比深焙早 0.5 分钟，发展时间 2 分 30 秒，落在合格窗口内。",
    ], 72, yb, 900, 20)
    footer(b, 72, H - 48, W - 144,
           "数据为自拟示例（按公开烘焙曲线的形态构造，非实测记录）；"
           "发展时间合格窗口 7.8–10.2 分钟取自常见浅中焙参数。")
    return canvas(W, H, "".join(b))


# ══════════════════════════════════════════════ 04 天台菜园灌溉决策
def case04():
    """城市天台菜园：今天要不要浇、浇哪几块。

    受众是周末才上楼的社区园艺者。他们要决定的是：
    「今天浇哪几块、跳过哪几块？理由是什么？」
    视觉主体是**每块地的含水量条 + 阈值带 + 一句话处置建议**，
    把「数据」直接翻译成「浇 / 跳过」。
    """
    W, H = 1280, 960
    b = [rect(0, 0, W, H, BG)]
    plots = [
        ("A1 番茄区", 31, "低于下限 4 个点"),
        ("A2 番茄区", 44, "在窗口内 · 偏干侧"),
        ("A3 叶菜区", 58, "在窗口内 · 偏湿侧"),
        ("B1 辣椒区", 22, "低于下限 13 个点"),
        ("B2 辣椒区", 39, "在窗口内 · 偏干侧"),
        ("B3 香草区", 67, "高于上限 7 个点"),
        ("C1 根菜区", 49, "在窗口内"),
        ("C2 育苗盘", 71, "高于上限 11 个点"),
    ]
    LO, HI = 35, 60          # 含水量阈值带 %
    X0, X1 = 320, 1064
    CW = X1 - X0
    Y0, PITCH = 388, 62

    b.extend(rect(0, 0, W, 4, SERIES[1], 0))
    y = header(b, 64, 48, W - 128, "案例 04 · 城市农业",
               "今天浇哪几块",
               "8 块地的土壤含水量与阈值带；低于下限才浇，窗口内不动")
    kpi_row(b, 64, y + 16, W - 128, [
        ("需浇地块", "2 / 8", SERIES[2], "A1 与 B1 低于下限"),
        ("今日预报降水", "12 mm", SERIES[0], "预计 21:00 前后"),
        ("平均含水量", "48%", SERIES[1], "8 块地算术平均"),
        ("建议用水", "19 L", SERIES[4], "按每块 9.5 L 计"),
    ])

    sc = lambda v: X0 + CW * v / 80.0                          # noqa: E731
    # 阈值带画在所有条子下面，作为一层底色
    b.append(rect(sc(LO), Y0 - 26, sc(HI) - sc(LO),
                  len(plots) * PITCH + 6, SERIES[1] + "16", 8))
    b.append(rect(sc(LO), Y0 - 26, 2, len(plots) * PITCH + 6, SERIES[1] + "77"))
    b.append(rect(sc(HI) - 2, Y0 - 26, 2, len(plots) * PITCH + 6, SERIES[1] + "77"))
    b.append(txt(f"阈值窗口 {LO}–{HI}%", sc(LO), Y0 - 58, sc(HI) - sc(LO), None, 19,
                 SERIES[1], align="CENTER"))
    for v in (0, 20, 40, 60, 80):
        b.append(txt(f"{v}%", sc(v) - 40, Y0 - 30, 80, None, 18, DIM,
                     align="CENTER"))

    for i, (name, v, note) in enumerate(plots):
        ry = Y0 + i * PITCH
        do = v < LO
        col = SERIES[2] if do else SERIES[1]
        b.append(txt(name, 64, ry + 8, 220, None, 22, INK))
        b.append(rect(X0, ry + 2, CW, 30, "#0E1727", 8))
        b.append(rect(X0, ry + 2, max(6.0, sc(v) - X0), 30, col + "4D", 8))
        b.append(rect(sc(v) - 3, ry - 2, 6, 38, col, 3))
        b.append(txt(f"{v}%", sc(v) + 14, ry + 5, 90, None, 21, col, W600))
        b.append(txt(note, X0, ry + 38, 460, None, 19, col))
        # 处置按钮放在条子右侧的固定列，不再挂在 X1 后面被画布切掉
        b.append(rect(1104, ry + 4, 128, 34, col + "2E", 8))
        b.append(txt("浇" if do else "跳过", 1104, ry + 10, 128, None, 21, col,
                     W600, align="CENTER"))

    footer(b, 64, H - 56, W - 128,
           "数据为自拟示例；含水量为体积含水率，下限 35%、上限 60%，"
           "降水取气象站日累计预报。实际灌溉还应考虑各块地的渗流与遮阴差异。")
    return canvas(W, H, "".join(b))

# ══════════════════════════════════════════════ 05 急诊分诊看板
def case05():
    """急诊分诊：按病情等级与等待时长给出处置队列。

    受众是值班护士与导医。真正要回答的是：
    「谁已经等太久了？下一步该叫谁？」
    视觉主体是**分诊等级条 + 每级的最长等待与目标线**，
    颜色直接对应分诊等级，超出目标等待的等级在底部汇总点名。
    """
    W, H = 1280, 960
    b = [rect(0, 0, W, H, BG)]
    # 等级, 颜色, 在诊人数, 最长等待分钟, 目标等待分钟, 目标文案, 超时人数
    levels = [
        ("I 级 濒危",   SERIES[3], 2, 3,  5,   "立即处置", 0),
        ("II 级 危急",  SERIES[2], 4, 9,  10,  "≤ 10 分钟", 0),
        ("III 级 紧急", "#4C8DFF", 9, 38, 30,  "≤ 30 分钟", 3),
        ("IV 级 次紧急", SERIES[5], 14, 74, 60, "≤ 60 分钟", 2),
        ("V 级 非紧急", SERIES[1], 18, 96, 120, "≤ 120 分钟", 0),
    ]
    total = sum(l[2] for l in levels)
    over_cnt = sum(l[6] for l in levels)
    over_n = sum(l[3] * l[2] for l in levels)
    avg = round(over_n / total)

    b.extend(rect(0, 0, W, 4, SERIES[3], 0))
    y = header(b, 64, 48, W - 128, "案例 05 · 医疗分诊",
               "急诊候诊 · 谁等最久",
               "按分诊等级统计在诊人数与最长等待；超出目标时长即在底部点名")
    kpi_row(b, 64, y + 16, W - 128, [
        ("在诊总人数", f"{total}", SERIES[0], "五个等级合计"),
        ("I + II 级", "6", SERIES[3], "濒危 2 · 危急 4"),
        ("超时人数", f"{over_cnt}", SERIES[3], "超出本级目标时长"),
        ("平均等待", f"{avg} 分钟", SERIES[5], "按人数加权"),
    ])

    Y0, BAR, PITCH = 396, 56, 78
    X0, X1 = 360, 1016
    for nm, col, cnt, worst, goal, glabel, ocnt in levels:
        ry = Y0 + levels.index((nm, col, cnt, worst, goal, glabel, ocnt)) * PITCH
        b.append(rect(64, ry, W - 128, BAR, PANEL, 10))
        b.append(rect(64, ry, 8, BAR, col, 4))
        b.append(txt(nm, 88, ry + 8, 200, None, 22, col, W600))
        b.append(txt(f"{cnt} 人" + (f" · 超时 {ocnt}" if ocnt else ""),
                     88, ry + 34, 220, None, 18, SERIES[3] if ocnt else SUB))
        b.append(rect(X0, ry + 20, X1 - X0, 16, "#0E1727", 8))
        b.append(rect(X0, ry + 20, (X1 - X0) * min(1.0, worst / 120.0), 16,
                      col + "66", 8))
        gx = X0 + (X1 - X0) * min(1.0, goal / 120.0)
        b.append(rect(gx, ry + 10, 3, 36, INK, 0))
        b.append(txt("目标", gx - 30, ry - 8, 60, None, 17, SUB, align="CENTER"))
        b.append(txt(f"最长等待 {worst} 分钟", X0, ry + 40, 300, None, 18, DIM))
        b.append(txt(f"目标 {glabel}", X1 - 60, ry + 18, 240, None, 19, SUB,
                     align="END"))

    ry = Y0 + len(levels) * PITCH + 6
    b.append(rect(64, ry, W - 128, 92, SERIES[3] + "1A", 12))
    b.append(rect(64, ry, 6, 92, SERIES[3], 3))
    b.append(txt("超时预警", 88, ry + 10, 300, None, 22, SERIES[3], W600))
    b.append(txt("III 级 紧急 3 人已等 38 分钟（目标 30）；"
                 "IV 级 次紧急 2 人已等 74 分钟（目标 60）",
                 88, ry + 40, W - 200, None, 20, INK))
    b.append(txt("处置：分诊护士复评这两级，按病情变化调整叫号顺序。",
                 88, ry + 64, W - 200, None, 20, SUB))
    footer(b, 64, H - 44, W - 128,
           "数据为自拟示例（模拟某市三甲急诊一个时段的候诊快照）；"
           "分诊等级用颜色区分，目标等待时长为院内分级诊疗常见参考值。")
    return canvas(W, H, "".join(b))

sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B01"))
from cases_b01_b import case06, case07, case08, case09, case10  # noqa: E402

CASES = [case01, case02, case03, case04, case05,
         case06, case07, case08, case09, case10]


def main() -> None:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    idx = range(len(CASES)) if which == "all" else [int(which) - 1]
    for i in idx:
        p = DRAFTS / f"case-{i + 1:02d}-{ver}.snapshot"
        p.write_text(CASES[i](), encoding="utf-8")
        print("->", p.name, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main()







