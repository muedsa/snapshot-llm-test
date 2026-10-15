#!/usr/bin/env python
# B01 后五件（06–10）。与 build_b01.py 共用 bsnap 工具与画布规范。
# 启动基准：总任务根 (suite_root)。
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, W500, W600, bullets,
                   canvas, circle, footer, header, kpi_row, line_h, polyline,
                   rect, segment, txt)


# ══════════════════════════════════════════════ 06 代码评审负载
def case06():
    """代码评审负载：谁手上的 PR 太多、哪些会超 SLA。

    受众是某个开源项目的维护者。他们要回答：
    「这个 reviewer 该不该再加活？哪些 PR 已经要超 SLA 了？」
    视觉主体是**每个 reviewer 的评审槽位格**：按容量画格子，
    已占用的格子填色，临近/超 SLA 的人整行标红并列出具体 PR。
    """
    W, H = 1400, 960
    b = [rect(0, 0, W, H, BG)]
    # reviewer, 容量, 在评审数, 其中已超或临近 SLA
    revs = [
        ("R. Alvarez", 6, 6, 1), ("H. Nakamura", 5, 5, 0),
        ("J. Okafor", 6, 4, 0), ("陈曦", 5, 5, 2),
        ("D. Kowalski", 6, 3, 0), ("S. Bhatt", 4, 4, 1),
        ("M. Lindqvist", 6, 2, 0),
    ]
    risky = [
        ("#2841 feat(core): 分片重平衡", "陈曦", "已等 31 小时", "SLA 24 小时", True),
        ("#2859 fix(parser): 空文件不抛错", "陈曦", "已等 26 小时", "SLA 24 小时", True),
        ("#2833 docs: 迁移指南补图", "R. Alvarez", "已等 19 小时", "SLA 24 小时", False),
        ("#2861 chore: 锁文件升级", "S. Bhatt", "已等 22 小时", "SLA 12 小时", True),
    ]
    cap_total = sum(r[1] for r in revs)
    load = sum(r[2] for r in revs)

    b.extend(rect(0, 0, W, 4, SERIES[4], 0))
    y = header(b, 72, 48, W - 144, "案例 06 · 工程效能",
               "评审队列别压在人身上",
               "每个 reviewer 的容量、在评审数与超 SLA 的 PR")
    kpi_row(b, 72, y + 16, W - 144, [
        ("在评审 PR", f"{load}", SERIES[0], "七个 reviewer 合计"),
        ("总容量", f"{cap_total}", SERIES[1], "各人自报容量"),
        ("满载人数", f"{sum(1 for r in revs if r[2] >= r[1])}", SERIES[2], "占全员"),
        ("超 SLA 的 PR", f"{sum(1 for r in risky if r[4])}", SERIES[3], "需重新指派"),
    ])

    X0, X1 = 400, 1330
    Y0, PITCH = 390, 44
    slot = (X1 - X0) / 6
    for k in range(7):
        x = X0 + slot * k
        b.append(rect(x, Y0 - 18, 1, len(revs) * PITCH + 4, LINE))
        b.append(txt(str(k), x - 20, Y0 - 48, 40, None, 18, DIM, align="CENTER"))
    b.append(txt("评审槽位", X0 - 320, Y0 - 46, 300, None, 18, SUB, align="END"))

    for i, (name, cap, cur, flagged) in enumerate(revs):
        ry = Y0 + i * PITCH
        full = cur >= cap
        col = SERIES[3] if flagged else (SERIES[2] if full else SERIES[1])
        # 行距压到 44px 后姓名与副行必须并排，竖着放会压到下一行
        b.append(txt(name, 72, ry + 11, 226, None, 22, INK))
        b.append(txt(("满载 · " if full else "") + f"容量 {cap}", 302, ry + 15, 250,
                     None, 18, col if full else DIM))
        b.append(rect(X0, ry + 6, X1 - X0, 34, "#0E1727", 8))
        for k in range(6):
            occupied = k < cur
            within = k < cap
            b.append(rect(X0 + slot * k + 4, ry + 11, slot - 8, 24,
                          (col + ("66" if occupied else "18")) if within else "#0B1220",
                          5, border=f'1 SOLID {col}' if occupied and flagged
                          else (f'1 SOLID {col}66' if occupied else "1 SOLID #1B2740")))
        b.append(txt(f"{cur}", X1 + 16, ry + 9, 60, None, 24, col, W600))

    ry = Y0 + len(revs) * PITCH + 8
    b.append(txt("临近与超 SLA 的 PR", 72, ry, 500, None, 26, INK, W600))
    b.append(txt("按已等待时长排序", 820, ry + 4, 500, None, 18, DIM, align="END"))
    # 两列排布：首版四条 PR 竖着排，画布只有 900px，最后一条压到页脚上
    COLW = (W - 144 - 20) / 2
    for k, (pid, who, waited, sla, over_sla) in enumerate(risky):
        cx = 72 + (k % 2) * (COLW + 20)
        cy = ry + 46 + (k // 2) * 60
        col = SERIES[3] if over_sla else SERIES[2]
        b.append(rect(cx, cy, COLW, 54, PANEL, 10))
        b.append(rect(cx, cy, 6, 54, col, 3))
        b.append(txt(pid, cx + 18, cy + 8, COLW - 200, None, 20, INK))
        b.append(txt(f"{who} · {waited}", cx + 18, cy + 32, COLW - 200, None, 18, col))
        b.append(txt(("已超 " if over_sla else "临近 ") + sla, cx + COLW - 176, cy + 15,
                     158, None, 19, col, W600, align="END"))
    footer(b, 72, H - 40, W - 144,
           "数据为自拟示例；容量为各 reviewer 声明的可接 PR 数，"
           "SLA 取开源项目常见的首轮响应时限。")
    return canvas(W, H, "".join(b))


# ══════════════════════════════════════════════ 07 今夜星空可见性
def case07():
    """今夜星空：在这座城市，抬头能看到什么。

    受众是刚入门的观星者。他们要回答：
    「今晚这些亮星在哪个方位？城市光害会不会把矮星吃掉？」
    视觉主体是**方位角 × 高度角的直角星图**（而不是把地平线画成直线的极坐标图——
    那样星会跑到地平线以下，自相矛盾）：
    横轴是方位角 0°(北)→360°，纵轴是高度角 0°(地平线)→90°(天顶)，
    20° 以下画成被光害淹没的暗带，落进去的星只画空心点并标灰。
    """
    W, H = 1200, 1200
    b = [rect(0, 0, W, H, BG)]
    BORT = 20                     # 光害淹没高度角
    stars = [
        ("织女", 118, 62, 0.03, "天琴"), ("天津四", 92, 41, 2.45, "天琴"),
        ("牵牛", 92, 18, 0.77, "天鹰"), ("天津一", 108, 31, 2.90, "天琴"),
        ("河鼓二", 86, 9, 2.68, "天鹰"), ("北落师门", 232, 34, 1.16, "南鱼"),
        ("大陵五", 152, 58, 2.12, "英仙"), ("天大将军一", 166, 73, 2.02, "英仙"),
        ("毕宿五", 202, 21, 0.85, "金牛"), ("角宿一", 246, 52, 0.97, "室女"),
        ("心宿二", 281, 14, 1.06, "天蝎"), ("北极星", 0, 40, 1.98, "小熊"),
        ("五车二", 15, 29, 1.58, "大熊"), ("玉衡", 12, 55, 1.77, "大熊"),
        ("天枢", 28, 63, 2.37, "大熊"),
    ]
    conn = [("织女", "天津四"), ("天津四", "天津一"), ("天津四", "牵牛"),
            ("大陵五", "天大将军一"), ("五车二", "玉衡"), ("玉衡", "天枢"),
            ("玉衡", "五车二")]
    visible = [s for s in stars if s[2] > BORT]
    lost = [s for s in stars if s[2] <= BORT]
    look = {s[0]: s for s in stars}

    X0, X1 = 96, 1104
    YT, Y0 = 392, 790             # 天顶 90° ↔ 地平线 0°
    sx = lambda az: X0 + (X1 - X0) * az / 360.0                 # noqa: E731
    sy = lambda alt: Y0 - (Y0 - YT) * alt / 90.0                # noqa: E731

    b.extend(rect(0, 0, W, 4, SERIES[4], 0))
    y = header(b, 64, 48, W - 128, "案例 07 · 天文观测",
               "今夜，抬头能看到的",
               "北纬 31.2° · 城市 Bortle 6 · 22:40 本地时间 · 视宁度 3/5")
    y = kpi_row(b, 64, y + 16, W - 128, [
        ("可见亮星", f"{len(visible)} / {len(stars)}", SERIES[0], "高于 20° 光害线"),
        ("最亮星", "织女 0.03 等", SERIES[4], "天琴座 α"),
        ("今晚月亮", "盈凸 62%", SERIES[2], "22:12 落下"),
        ("暗空时段", "23:50 – 04:30", SERIES[1], "月光落下后"),
    ])

    # 被光害淹没的 0–20° 暗带
    b.append(rect(X0, sy(BORT), X1 - X0, Y0 - sy(BORT), "#0B1220", 0))
    b.append(rect(X0, sy(BORT) - 2, X1 - X0, 3, SERIES[3] + "88"))
    b.append(txt(f"{BORT}° 光害淹没线", X0 + 12, sy(BORT) + 16, 260, None, 19,
                 SERIES[3]))
    b.append(txt(f"线下 {len(lost)} 颗今晚看不见", X1 - 272, sy(BORT) + 16, 260,
                 None, 19, DIM, align="END"))
    # 高度角网格
    for alt in (0, 30, 60, 90):
        b.append(rect(X0, sy(alt), X1 - X0, 2 if alt == 0 else 1,
                      LINE if alt == 0 else "#1B2740"))
        b.append(txt(f"{alt}°", X0 - 62, sy(alt) - 14, 52, None, 19, DIM,
                     align="END"))
    b.append(txt("天顶", X0 + 10, YT - 6, 80, None, 18, DIM))
    # 方位角刻度
    for az in range(0, 361, 45):
        b.append(rect(sx(az), Y0, 1, 12, LINE))
        lbl = {0: "北 0°", 90: "东 90°", 180: "南 180°", 270: "西 270°",
               360: "北 360°"}.get(az, f"{az}°")
        b.append(txt(lbl, sx(az) - 60, Y0 + 16, 120, None, 19,
                     INK if az % 90 == 0 else DIM, align="CENTER"))
    b.append(rect(X0, Y0, X1 - X0, 2, LINE))

    # 星座连线
    for a, c in conn:
        if a in look and c in look and look[a][2] > BORT and look[c][2] > BORT:
            b.append(segment(sx(look[a][1]), sy(look[a][2]),
                             sx(look[c][1]), sy(look[c][2]), SERIES[4] + "77", 2))

    # 星点：半径随星等变小
    for nm, az, alt, mag, con in stars:
        x, yy = sx(az), sy(alt)
        if alt <= BORT:
            b.append(circle(x, yy, 9, None, border="2 SOLID #2E3D57"))
            continue
        r = max(3.0, 8.0 - mag * 3.2)
        b.append(circle(x, yy, r * 2.5, SERIES[0] + "2E"))
        b.append(circle(x, yy, r * 2, "#EAF2FF"))
        if mag < 1.6:
            b.append(txt(nm, x + r + 10, yy - 13, 150, None, 18, INK))

    b.append(txt("光害淹没带：此带内的星在城市天光下基本看不见，"
                 "上面画的是空心圈，只为对照位置", 96, Y0 + 62, W - 192, None, 19, DIM))
    bullets(b, [
        "织女—天津四—天津一连成夏季大三角，是今晚最值得先找的目标；",
        "心宿二、毕宿五、河鼓二落在 20° 以下，城市光害把它们吃掉了；",
        "月亮 22:12 落下，真正的暗空从 23:50 开始——这决定今晚先拍什么。",
    ], 64, Y0 + 110, W - 128, 20)
    footer(b, 64, H - 56, W - 128,
           "数据为自拟示例（按某夜实际星历近似构造），非实时星图；"
           "Bortle 6 的光害淹没高度角取 20°。")
    return canvas(W, H, "".join(b))


# ══════════════════════════════════════════════ 08 临期补货
def case08():
    """生鲜零售：哪些 SKU 该补、哪些该先报损。

    受众是门店的品类经理。他们要回答：
    「明天早上补什么货？哪几箱今天就得处理掉？」
    视觉主体是**双向条**：左边看缺货风险（库存 ÷ 安全库存），
    右边看过期风险（剩余保质期），最右一列写今天的处置。
    """
    W, H = 1400, 900
    b = [rect(0, 0, W, H, BG)]
    skus = [
        ("鲜牛奶 950ml", 0.42, 3, 46), ("鸡蛋 30 枚", 0.55, 9, 28),
        ("酸奶 100g × 4", 1.35, 12, 31), ("叶菜沙拉", 0.78, 2, 19),
        ("冷鲜鸡胸 500g", 0.61, 5, 22), ("面包 400g", 1.20, 6, 24),
        ("三文鱼刺身", 0.33, 1, 12), ("豆腐 400g", 1.55, 8, 17),
        ("蓝莓 125g", 0.88, 4, 20),
    ]
    actions, replenish, clear = [], 0, 0
    for name, ratio, days, vel in skus:
        if days <= 3 and ratio >= 1.0:
            act, col = "报损 / 折价", SERIES[3]
            clear += 1
        elif ratio < 0.7:
            act, col = "明日补货", SERIES[2]
            replenish += 1
        elif days <= 3:
            act, col = "优先出清", SERIES[4]
            clear += 1
        else:
            act, col = "维持", SERIES[1]
        actions.append((name, ratio, days, vel, act, col))

    b.extend(rect(0, 0, W, 4, SERIES[2], 0))
    y = header(b, 72, 48, W - 144, "案例 08 · 生鲜零售",
               "明早补什么，今天先动哪几箱",
               "左边看缺货风险，右边看过期风险，最右写今天的处置")
    kpi_row(b, 72, y + 16, W - 144, [
        ("在册 SKU", f"{len(skus)}", SERIES[0], "生鲜与冷藏"),
        ("明日需补货", f"{replenish}", SERIES[2], "低于安全库存 70%"),
        ("今日需出清", f"{clear}", SERIES[3], "临期 ≤ 3 天"),
        ("临期损失敞口", "¥ 412", SERIES[4], "按当前进价估算"),
    ])

    LX0, LX1 = 330, 700
    RX0, RX1 = 800, 1150
    Y0, PITCH = 412, 48
    rows_h = len(skus) * PITCH
    b.append(txt("← 缺货风险", LX0, Y0 - 66, LX1 - LX0, None, 20,
                 SERIES[2], align="CENTER"))
    b.append(txt("保质期 →", RX0, Y0 - 66, RX1 - RX0, None, 20, SERIES[3],
                 align="CENTER"))
    for v, lab, hi in ((0, "0", False), (0.7, "70% 安全线", True), (1.6, "160%", False)):
        x = LX0 + (LX1 - LX0) * v / 1.6
        b.append(rect(x, Y0 - 4, 1, rows_h + 10, SERIES[2] + "77" if hi else LINE))
        b.append(txt(lab, x - 70, Y0 - 32, 140, None, 18, SERIES[2] if hi else DIM,
                     align="CENTER"))
    for v, lab, hi in ((0, "0 天", False), (3, "3 天线", True), (14, "14 天", False)):
        x = RX0 + (RX1 - RX0) * v / 14
        b.append(rect(x, Y0 - 4, 1, rows_h + 10, SERIES[3] + "77" if hi else LINE))
        b.append(txt(lab, x - 60, Y0 - 32, 120, None, 18, SERIES[3] if hi else DIM,
                     align="CENTER"))

    for i, (name, ratio, days, vel, act, col) in enumerate(actions):
        ry = Y0 + i * PITCH
        b.append(txt(name, 72, ry + 12, 200, None, 21, INK))
        b.append(txt(f"日销 {vel}", 236, ry + 16, 84, None, 18, DIM, align="END"))
        w = (LX1 - LX0) * min(1.0, ratio / 1.6)
        b.append(rect(LX0, ry + 8, LX1 - LX0, 26, "#0E1727", 6))
        b.append(rect(LX1 - w, ry + 8, w, 26,
                      SERIES[3] if ratio < 0.7 else SERIES[1] + "55", 6))
        b.append(txt(f"{ratio:.2f}", LX1 - w - 92, ry + 11, 84, None, 19,
                     SERIES[3] if ratio < 0.7 else SUB, align="END"))
        w2 = (RX1 - RX0) * min(1.0, days / 14)
        b.append(rect(RX0, ry + 8, RX1 - RX0, 26, "#0E1727", 6))
        b.append(rect(RX0, ry + 8, w2, 26,
                      SERIES[3] + "66" if days <= 3 else SERIES[4] + "44", 6))
        b.append(txt(f"{days} 天", RX0 + w2 + 12, ry + 11, 90, None, 19,
                     SERIES[3] if days <= 3 else SUB))
        b.append(rect(1188, ry + 8, 168, 32, col + "2E", 8))
        b.append(txt(act, 1188, ry + 13, 168, None, 20, col, W600, align="CENTER"))

    footer(b, 72, H - 44, W - 144,
           "数据为自拟示例；安全库存由近 8 周日均销量 × 提前期估出，"
           "剩余保质期按先进先出推算。真实补货还要看在途库存与促销档期。")
    return canvas(W, H, "".join(b))


# ══════════════════════════════════════════════ 09 台风路径与港口停运
def case09():
    """台风路径：哪些港口要提前停、哪些可以等一等。

    受众是航运公司的值班调度。他们要回答：
    「未来 84 小时里，哪几个港的关闭窗口短到必须提前安排？」
    视觉主体是**上：路径概率带（横轴为预报时效）；下：每港一行的时窗条**。
    每个港口单独一行，而不是把所有港挤在同一根时间轴上——
    首版那样做，六条时窗叠成一条实心带，文字互相盖住，谁也读不出来。
    """
    W, H = 1400, 900
    b = [rect(0, 0, W, H, BG)]
    track = [(0, 452, "热带低压"), (12, 448, "热带风暴"), (24, 444, "强热带风暴"),
             (36, 441, "台风"), (48, 438, "强台风"), (60, 443, "台风"),
             (72, 449, "热带风暴"), (84, 454, "热带低压")]
    band = [(0, 30), (12, 48), (24, 68), (36, 84), (48, 92), (60, 84), (72, 60),
            (84, 36)]
    # 港口：x 位置, 名称, 警戒小时, 关港小时, 开港小时
    ports = [(300, "福州港", 18, 30, 66), (470, "温州港", 22, 34, 70),
             (640, "宁波舟山港", 26, 38, 70), (820, "上海洋山港", 30, 42, 70),
             (1010, "南通港", 34, 46, 70), (1190, "青岛港", 40, 52, 74)]
    SHORT = 32                      # 关闭窗口 ≤32 小时即视为「必须提前安排」
    must = [p for p in ports if p[4] - p[3] <= SHORT]
    first_close = min(p[3] for p in must)
    shortest = min(must, key=lambda p: p[4] - p[3])

    b.extend(rect(0, 0, W, 4, SERIES[3], 0))
    y = header(b, 72, 48, W - 144, "案例 09 · 航运调度",
               "哪几个港的关闭窗口短到要提前安排",
               "上：台风路径概率带；下：每个港口的警戒—关港—开港时窗")
    kpi_row(b, 72, y + 16, W - 144, [
        ("72 小时路径带", "±340 km", SERIES[0], "集合预报包络"),
        ("必须提前安排", f"{len(must)} 个港", SERIES[3], "关闭窗口 ≤ 32 小时"),
        ("最早关港", f"{first_close} 小时", SERIES[2], "宁波舟山港"),
        ("窗口最短", f"{shortest[4] - shortest[3]} 小时", SERIES[4], shortest[1]),
    ])

    X0, X1 = 150, 1300
    hx = lambda hr: X0 + (X1 - X0) * hr / 84.0                # noqa: E731
    # 概率带：以路径中心线为基准上下展开（首版以固定的带中心展开，
    # 导致上沿贴近顶部、下沿拖到 640，视觉重心整个偏了）
    top = [(hx(hr), _y - r * 1.00) for (hr, _y, _i), (_bh, r) in zip(track, band)]
    bot = [(hx(hr), _y + r * 1.00) for (hr, _y, _i), (_bh, r) in zip(track, band)]
    for i in range(len(top) - 1):
        b.append(rect(top[i][0], top[i][1], top[i + 1][0] - top[i][0],
                      bot[i][1] - top[i][1], SERIES[0] + "10", 0))
    b.append(polyline(top, SERIES[0] + "99", 3))
    b.append(polyline(bot, SERIES[0] + "99", 3))
    mid = [(hx(hr), _y) for hr, _y, _i in track]
    b.append(polyline(mid, SERIES[0], 4))
    for i, (hr, _y, inten) in enumerate(track):
        col = SERIES[3] if "台风" in inten else SERIES[5]
        b.append(circle(hx(hr), mid[i][1], 16, col))
        b.append(txt(f"+{hr}h {inten}", hx(hr) - 90, mid[i][1] - 38, 180, None, 18,
                     col, align="CENTER"))
    for hr in (0, 24, 48, 72, 84):
        b.append(rect(hx(hr), 336, 1, 206, "#1B2740"))
        b.append(txt(f"+{hr}h", hx(hr) - 40, 548, 80, None, 19, DIM,
                     align="CENTER"))

    PY, PITCH = 600, 42
    for i, (px, name, warn, close, open_) in enumerate(ports):
        ry = PY + i * PITCH
        urgent = (open_ - close) <= SHORT
        col = SERIES[3] if urgent else SERIES[1]
        b.append(txt(name, 72, ry + 4, 160, None, 20, INK))
        b.append(txt(f"警戒 {warn}h", 250, ry + 6, 130, None, 18, DIM,
                     align="END"))
        b.append(rect(hx(warn), ry + 4, hx(open_) - hx(warn), 22, col + "22", 6,
                      border=f'1 SOLID {col}88'))
        b.append(rect(hx(close), ry + 4, hx(open_) - hx(close), 22, col + "66", 6))
        b.append(txt(f"{close}–{open_}h 关闭", X1 - 230, ry + 6, 230, None, 19, col,
                     align="END"))
        for (hr, cx, _i), (_bh, r) in zip(track, band):
            if abs(cx - px) <= r:
                b.append(segment(px, ry - 8, px, ry + 2, SERIES[0] + "AA", 3))
                break
    footer(b, 72, H - 40, W - 144,
           "数据为自拟示例；路径带取集合预报 72 小时包络，关港窗口为港口防台规程示例值，"
           "不代表任何实际台风。")
    return canvas(W, H, "".join(b))

# ══════════════════════════════════════════════ 10 音乐节分区容量
def case10():
    """音乐节分区安全：哪块地已经不能进人。

    受众是舞台安全官。他们要回答：
    「现在哪个分区超过红线了？下一批人该往哪儿引导？」
    视觉主体是**场地分区图 + 右侧限流清单**：每块分区按「在场 ÷ 容量」着色，
    右侧只列出 ≥85% 的分区并给出处置动作。
    首版把平面图画在 y=288，而 KPI 卡到 334，地图顶栏直接压在卡片下沿；
    右侧列表宽 192px，百分比和「在场/容量」两行文字互相盖住——
    两处都改掉，地图下移、右侧加宽，数字分两行放。
    """
    W, H = 1280, 960
    b = [rect(0, 0, W, H, BG)]
    zones = [
        ("A 主舞台前区", (120, 500, 280, 200), 4820, 5000),
        ("B 次舞台前区", (420, 500, 250, 200), 2610, 3000),
        ("C 电子舞台", (690, 500, 250, 200), 1980, 2400),
        ("D 美食市集", (450, 384, 220, 100), 1240, 2600),
        ("E 休息区", (120, 384, 300, 100), 860, 2200),
        ("F 商店排队", (700, 384, 240, 100), 640, 1600),
        ("G 北入口集散", (280, 700, 280, 96), 3100, 2400),
        ("H 南入口集散", (590, 700, 350, 96), 1420, 2600),
    ]
    ratios = [(n, c / cap, c, cap, box) for n, box, c, cap in zones]
    over = [r for r in ratios if r[1] >= 1.0]
    warn = [r for r in ratios if 0.85 <= r[1] < 1.0]
    total = sum(r[2] for r in ratios)
    cap_total = sum(r[3] for r in ratios)

    def zc(r):
        return (SERIES[3] if r >= 1.0 else
                SERIES[2] if r >= 0.85 else
                SERIES[1] if r >= 0.5 else SERIES[0])

    b.extend(rect(0, 0, W, 4, SERIES[3], 0))
    y = header(b, 64, 48, W - 128, "案例 10 · 大型活动安全",
               "哪块地不能再进人",
               "场地分区图 · 按「在场人数 ÷ 区域容量」着色 · 21:10 快照")
    y = kpi_row(b, 64, y + 16, W - 128, [
        ("在场人数", f"{total:,}", SERIES[0], "八个分区合计"),
        ("总容量", f"{cap_total:,}", SERIES[1], "按场地核定值"),
        ("超限分区", f"{len(over)}", SERIES[3], "已达或超过红线"),
        ("待限分区", f"{len(warn)}", SERIES[2], "≥ 85% 需引导"),
    ])

    b.append(rect(100, 348, 864, 482, "#0C1424", 16, border="1 SOLID #1F2C48"))
    b.append(txt("场地平面（示意）", 700, 352, 248, None, 18, DIM, align="END"))
    for name, box, cnt, cap in zones:
        zx, zy, zw, zh = box
        r = cnt / cap
        col = zc(r)
        b.append(rect(zx, zy, zw, zh, col + "3A", 10, border=f'2 SOLID {col}'))
        b.append(txt(name, zx + 14, zy + 10, zw - 28, None, 20, col, W600))
        b.append(txt(f"{cnt:,} / {cap:,}", zx + 14, zy + 40, zw - 28, None, 21, INK,
                     W600))
        b.append(txt(f"{r:.0%}", zx + 14, zy + 68, zw - 28, None, 20, col))
    for lbl, ex, ey, dy in (("北入口", 470, 348, 4), ("南入口", 620, 830, -34)):
        b.append(rect(ex - 7, ey - 7, 14, 14, SERIES[4], 3))
        b.append(txt(lbl, ex - 60, ey + dy, 120, None, 19, SERIES[4], align="CENTER"))

    LX, LW = 984, 260
    b.append(txt("限流清单", LX, 352, LW, None, 26, INK, W600))
    b.append(txt("≥ 85% 的分区", LX, 386, LW, None, 18, DIM))
    yb = 420
    for r in sorted([x for x in ratios if x[1] >= 0.85], key=lambda z: -z[1]):
        col = SERIES[3] if r[1] >= 1.0 else SERIES[2]
        b.append(rect(LX, yb, LW, 80, PANEL, 10))
        b.append(rect(LX, yb, 6, 80, col, 3))
        # 第一行：名称 + 百分比（各占一半，互不重叠）
        b.append(txt(r[0], LX + 18, yb + 10, 150, None, 20, col, W600))
        b.append(txt(f"{r[1]:.0%}", LX + 168, yb + 10, 74, None, 20, col, W600,
                     align="END"))
        # 第二行：人数
        b.append(txt(f"{r[2]:,} / {r[3]:,}", LX + 18, yb + 42, LW - 36, None, 19, INK))
        yb += 88
    b.append(txt("处置", LX, yb + 4, LW, None, 24, INK, W600))
    bullets(b, [
        "A 主舞台前区 96%：停止放行，加密隔离带；",
        "G 北入口集散区 129%：下一批观众改导南入口；",
        "B / C 两区接近红线，广播每 15 分钟播一次分流。",
    ], LX, yb + 40, LW, 19, gap=6)
    footer(b, 64, H - 44, W - 128,
           "数据为自拟示例；区域容量按场地平面图与消防核定值构造，"
           "限流阈值取 85% 与 100%，不代表任何实际活动。")
    return canvas(W, H, "".join(b))
