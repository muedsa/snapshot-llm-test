#!/usr/bin/env python
# 一次性补丁：重排 case10 的场地平面与右侧清单，消除 KPI 卡压图、百分比压数字、
# 以及要点溢出画布三个问题。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c10.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
head = s[:s.index("def case10():")]

new = '''def case10():
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
        ("A 主舞台前区", (120, 478, 280, 220), 4820, 5000),
        ("B 次舞台前区", (420, 478, 250, 220), 2610, 3000),
        ("C 电子舞台", (690, 478, 250, 220), 1980, 2400),
        ("D 美食市集", (450, 358, 220, 100), 1240, 2600),
        ("E 休息区", (120, 358, 300, 100), 860, 2200),
        ("F 商店排队", (700, 358, 240, 100), 640, 1600),
        ("G 北入口集散", (280, 718, 280, 96), 3100, 2400),
        ("H 南入口集散", (590, 718, 350, 96), 1420, 2600),
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
    b.append(txt("场地平面（示意）", 116, 356, 300, None, 18, DIM))
    for name, box, cnt, cap in zones:
        zx, zy, zw, zh = box
        r = cnt / cap
        col = zc(r)
        b.append(rect(zx, zy, zw, zh, col + "3A", 10, border=f'2 SOLID {col}'))
        b.append(txt(name, zx + 14, zy + 10, zw - 28, None, 20, col, W600))
        b.append(txt(f"{cnt:,} / {cap:,}", zx + 14, zy + 40, zw - 28, None, 21, INK,
                     W600))
        b.append(txt(f"{r:.0%}", zx + 14, zy + 68, zw - 28, None, 20, col))
    for lbl, ex, ey, dy in (("北入口", 470, 348, 12), ("南入口", 620, 830, -42)):
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
'''
p.write_text(head + new, encoding="utf-8")
print("case10 rewritten")