#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""case-05 自适应信息亭界面设计稿（1920×1080，16:10 设计稿纸）。
鹭洲湿地公园触摸屏信息亭 V2 —— 同一信息架构在三种屏宽下的呈现。
主导手法：Flex 弹性布局（Row/Column/Expanded/Flexible/Spacer +
mainAxisAlignment=SPACE_BETWEEN/AROUND/EVENLY、crossAxisAlignment=STRETCH）
+ AspectRatio / FractionallySizedBox / ConstrainedBox 约束构件。
注意：Flex 子级内不能用 Positioned（parentData 必须是 StackParentData），
故磁贴/英雄区内部一律用 Stack+Positioned 或纯流式构件。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from b03_common import *  # noqa: F403
from b03_common import (T, positioned, assert_canvas, WARN,
                        INK, INK_DEEP, TEAL, PAPER, PAPER_DIM, ORANGE,
                        ORANGE_DEEP, INDIGO, REED, SKY, WHITE,
                        SERIF, SANS, MONO, INTER,
                        rect)

W, H = 1920, 1080
C_SCREEN = "#DCE9E4"   # 屏面
C_CARD = "#FFFFFF"     # 磁贴


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(s, size, color, style="NORMAL", family=SANS, spacing=None):
    sp = f' letterSpacing="{spacing}"' if spacing else ""
    st = f' fontStyle="{style}"' if style != "NORMAL" else ""
    return (f'<Text fontSize="{size}" color="{color}" '
            f'fontFamily="{family}"{st}{sp}>{esc(s)}</Text>')


def box(w, h, color, radius=0.0, child="", padding=None, align=None):
    br = f' borderRadius="{radius:.1f}"' if radius else ""
    pd = f' padding="{padding}"' if padding else ""
    al = f' alignment="{align}"' if align else ""
    return (f'<Container width="{w}" height="{h}" color="{color}"{br}{pd}'
            f'{al}>{child}</Container>')


def logo(size=40):
    return box(size, size, INK, size / 2, txt("鹭", int(size * 0.45),
              PAPER, "BOLD", SERIF), align="CENTER")


def chip_w(s, size=12):
    return (f'<Container borderRadius="12" color="#FFFFFFA8" '
            f'padding="(10,4)">{txt(s, size, INK)}</Container>')


def hero(flex, title, sub, tsize, ssize, hw, hh, tw):
    """英雄区：渐变天光 + 日 + 丘 + 底部 scrim + 标题（Stack+Positioned）。
    Positioned 只接受像素（百分比会 PARSE_ERROR），故 hw/hh 由调用方按
    flex 分配精算后传入；圆角裁剪用 ClipRRect（probe3 实证）。"""
    inner = (
        # 天光
        f'<Positioned left="0" top="0" width="{hw}" height="{hh}">'
        f'<Container width="{hw}" height="{hh}" gradientType="LINEAR" '
        f'gradientColors="#F2D3B3,#EFA479,#5E6B63" gradientStops="0,0.55,1" '
        f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>'
        f'</Positioned>'
        # 日（固定 px 圆：AspectRatio 仅在方形容器内实证）
        f'<Positioned left="{int(hw * 0.72)}" top="18" width="72" height="72">'
        f'<Container width="72" height="72" color="#FFF6E0" '
        f'shape="CIRCLE"/></Positioned>'
        # 丘（固定 px：负百分比 Positioned 未实证）
        f'<Positioned left="-70" top="{int(hh * 0.52)}" width="500" '
        f'height="150">'
        f'<Container width="500" height="150" color="#7C8A7E" '
        f'shape="CIRCLE"/></Positioned>'
        f'<Positioned left="{int(hw * 0.35)}" top="{int(hh * 0.58)}" '
        f'width="460" height="150">'
        f'<Container width="460" height="150" color="#66756B" '
        f'shape="CIRCLE"/></Positioned>'
        # 底部 scrim（FractionallySizedBox 演示）
        f'<FractionallySizedBox widthFactor="1" heightFactor="0.46" '
        f'alignment="BOTTOM_CENTER">'
        f'<Container color="#12203AA6"/>'
        f'</FractionallySizedBox>'
        # 标题块（固定 px）
        f'<Positioned left="28" top="{int(hh * 0.46)}" width="{tw}" '
        f'height="{int(hh * 0.5)}">'
        f'<Column crossAxisAlignment="START" mainAxisSize="MIN">'
        f'{txt(title, tsize, "#FFFFFF", "BOLD", SERIF)}'
        f'<SizedBox width="1" height="{int(tsize * 0.35)}"/>'
        f'{txt(sub, ssize, "#FFFFFFD9")}'
        f'</Column></Positioned>')
    return (f'<Expanded flex="{flex}"><ClipRRect borderRadius="14" '
            f'clipBehavior="ANTI_ALIAS">'
            f'<Stack alignment="TOP_LEFT" fit="EXPAND" '
            f'clipBehavior="HARD_EDGE">{inner}</Stack>'
            f'</ClipRRect></Expanded>')


def tile(glyph, label, sub, compact=False):
    """磁贴：图标圆 + 标签（+ 副标）。compact 为窄屏横排紧凑型。"""
    if compact:
        ic = box(28, 28, TEAL, 14, txt(glyph, 13, WHITE, "BOLD"),
                 align="CENTER")
        return (f'<Container borderRadius="10" color="{C_CARD}" '
                f'padding="(10,8)"><Row crossAxisAlignment="CENTER">'
                f'{ic}<SizedBox width="10" height="1"/>'
                f'{txt(label, 13, INK, "BOLD")}</Row></Container>')
    ic = box(34, 34, TEAL, 17, txt(glyph, 15, WHITE, "BOLD"),
             align="CENTER")
    return (f'<Container borderRadius="12" color="{C_CARD}" '
            f'padding="(12,10)"><Column crossAxisAlignment="CENTER" '
            f'mainAxisSize="MIN">'
            f'{ic}<SizedBox width="1" height="8"/>'
            f'{txt(label, 15, INK, "BOLD")}'
            f'<SizedBox width="1" height="3"/>'
            f'{txt(sub, 10, REED)}</Column></Container>')


def header(mode):
    """页眉：徽记 + 名称 + （宽/中屏）天气签。"""
    name_col = (f'<Column crossAxisAlignment="START" mainAxisSize="MIN">'
                f'{txt("鹭洲湿地公园", 19, INK, "BOLD", SERIF)}'
                f'<SizedBox width="1" height="3"/>'
                f'{txt("游客中心 · 触摸导览屏", 10, REED)}</Column>')
    if mode == "narrow":
        return (f'<Container padding="(12,10)"><Row '
                f'crossAxisAlignment="CENTER">{logo(34)}'
                f'<SizedBox width="10" height="1"/>{name_col}</Row>'
                f'</Container>')
    return (f'<Container padding="(12,10)"><Row '
            f'crossAxisAlignment="CENTER">{logo(40)}'
            f'<SizedBox width="10" height="1"/>{name_col}'
            f'<Expanded flex="1"><SizedBox width="1" height="1"/>'
            f'</Expanded>{chip_w("多云 18° · 09:50")}</Row></Container>')


def footer(mode):
    """页脚：联系方式。三种主轴分布策略的实证位。"""
    if mode == "wide":
        return (f'<Container padding="(12,8)"><Row '
                f'mainAxisAlignment="SPACE_BETWEEN" '
                f'crossAxisAlignment="CENTER">'
                f'{txt("咨询 0512-6688-0000", 11, REED)}'
                f'{txt("地铁 4 号线鹭洲站 B 口", 11, REED)}'
                f'{txt("V2.1", 10, REED, "NORMAL", MONO)}</Row></Container>')
    if mode == "mid":
        return (f'<Container padding="(12,8)"><Row '
                f'mainAxisAlignment="SPACE_AROUND" '
                f'crossAxisAlignment="CENTER">'
                f'{txt("0512-6688-0000", 11, REED)}'
                f'{txt("V2.1", 10, REED, "NORMAL", MONO)}</Row></Container>')
    return (f'<Container padding="(12,8)"><Column '
            f'mainAxisAlignment="SPACE_EVENLY" crossAxisAlignment="START">'
            f'{txt("咨询 0512-6688-0000", 10, REED)}'
            f'{txt("V2.1", 9, REED, "NORMAL", MONO)}</Column></Container>')


def tiles(mode):
    """磁贴区：宽屏一行四列 / 中屏 2×2 / 窄屏纵向列表。"""
    names = [("览", "湿地导览", "862 公顷"), ("动", "今日活动", "秋迁季 4 场"),
             ("行", "交通停车", "P1–P3 停车场"), ("询", "咨询电话", "08:30–17:00")]
    if mode == "wide":
        cells = "".join(
            f'<Expanded flex="1">{tile(g, l, s)}</Expanded>'
            f'<SizedBox width="10" height="1"/>' for g, l, s in names)
        return (f'<Expanded flex="3"><Row crossAxisAlignment="STRETCH">'
                f'{cells}</Row></Expanded>')
    if mode == "mid":
        r1 = "".join(f'<Expanded flex="1">{tile(g, l, s)}</Expanded>'
                     f'<SizedBox width="10" height="1"/>'
                     for g, l, s in names[:2])
        r2 = "".join(f'<Expanded flex="1">{tile(g, l, s)}</Expanded>'
                     f'<SizedBox width="10" height="1"/>'
                     for g, l, s in names[2:])
        return (f'<Expanded flex="3"><Column crossAxisAlignment="STRETCH" '
                f'mainAxisSize="MAX" mainAxisAlignment="SPACE_AROUND">'
                f'<Row crossAxisAlignment="STRETCH">{r1}</Row>'
                f'<Row crossAxisAlignment="STRETCH">{r2}</Row>'
                f'</Column></Expanded>')
    cells = "".join(f'<Expanded flex="1">{tile(g, l, "", True)}</Expanded>'
                    for g, l, _ in names)
    return (f'<Expanded flex="4"><Column crossAxisAlignment="STRETCH" '
            f'mainAxisSize="MAX" mainAxisAlignment="SPACE_EVENLY">'
            f'{cells}</Column></Expanded>')


def kiosk(x, y, w, h, mode, hero_flex=3, hero_title="秋迁季观鸟指南",
          hero_sub="287 种鸟类 · 最佳观测期 11–12 月", tsize=26, ssize=12,
          tw=560, hw=980, hh=250):
    """一台信息亭：实体框 + 屏面（返回两个 Positioned 节点）。"""
    frame = positioned(x, y, w, h,
                       box(w, h, INK, 18))
    sw, sh = w - 20, h - 20
    kids = [header(mode), '<SizedBox width="1" height="10"/>']
    if mode != "narrow":
        kids.append(hero(hero_flex, hero_title, hero_sub, tsize, ssize,
                         hw, hh, tw))
        kids.append('<SizedBox width="1" height="10"/>')
    kids.append(tiles(mode))
    kids.append('<SizedBox width="1" height="10"/>')
    kids.append(footer(mode))
    # 屏面直角（真实 kiosk 屏幕为直角；圆角仅外框，避免子级溢出圆角）
    screen = positioned(x + 10, y + 10, sw, sh,
                        box(sw, sh, C_SCREEN, 0,
                            f'<Column crossAxisAlignment="STRETCH" '
                            f'mainAxisSize="MAX">{"".join(kids)}</Column>'))
    return [frame, screen]


def space_demo_row(label, mode):
    dots = "".join(f'<Container width="12" height="12" color="{TEAL}" '
                   f'borderRadius="6"/>' for _ in range(4))
    return (f'<Row mainAxisAlignment="{mode}" crossAxisAlignment="CENTER">'
            f'{dots}</Row>')


def dsl() -> str:
    n = []
    n.append(rect(0, 0, W, H, PAPER))

    # ================= 稿纸抬头 =================
    T("信息亭界面 · 自适应设计稿", 60, 30, 800, 40, 30, INK, "LEFT",
      "BOLD", SERIF, nodes=n)
    T("同一信息架构 · 三种屏宽（1000 / 480 / 260）· Flex 弹性布局与约束构件",
      60, 76, 900, 20, 13, REED, "LEFT", "NORMAL", SANS, nodes=n)
    T("鹭洲湿地公园 · 触摸屏信息亭 V2 · 2026-11", 1020, 40, 840, 22, 14,
      TEAL, "RIGHT", "NORMAL", SANS, nodes=n)
    n.append(rect(60, 108, 1800, 2, INK))

    # ================= 三台信息亭 =================
    caps = [("① 宽屏 1000 · 页脚 SPACE_BETWEEN · hero 3 : 磁贴 3", 60, 1000),
            ("② 中屏 480 · 磁贴 SPACE_AROUND · 2×2", 1090, 480),
            ("③ 窄屏 260 · 列表 SPACE_EVENLY · 纵排", 1600, 260)]
    for cap, cx, cw in caps:
        T(cap, cx, 120, cw, 20, 13, INK, "LEFT", "NORMAL", MONO, nodes=n)
    n += kiosk(60, 148, 1000, 640, "wide")
    n += kiosk(1090, 148, 480, 640, "mid", hero_flex=2,
               hero_title="秋迁季观鸟指南", hero_sub="287 种鸟类",
               tsize=20, ssize=11, tw=300, hw=460, hh=200)
    n += kiosk(1600, 148, 260, 640, "narrow")

    # ================= 注释区 =================
    # A. Flex 策略
    n.append(rect(60, 828, 660, 190, WHITE, 12))
    n.append(rect(60, 828, 660, 190, "transparent").replace(
        'color="transparent"', 'color="transparent" border="1 SOLID #3E7C7455"'))
    T("Flex 策略", 84, 846, 300, 24, 16, INK, "LEFT", "BOLD", SANS,
      nodes=n)
    notes = [
        "主轴分布：宽屏 SPACE_BETWEEN · 中屏 SPACE_AROUND · 窄屏 SPACE_EVENLY",
        "弹性份额：磁贴 Expanded flex=1 均分；宽屏英雄区 flex=3 : 磁贴 flex=3",
        "交叉轴 STRETCH：同行磁贴等高；容器 Column crossAxisAlignment=STRETCH",
        "窄屏纵排： Expanded flex=1 + SPACE_EVENLY 自动平分剩余高度",
    ]
    for i, s in enumerate(notes):
        T(s, 84, 880 + i * 30, 620, 22, 12, REED, "LEFT", "NORMAL", SANS,
          nodes=n)

    # B. SPACE_* 演示
    n.append(rect(760, 828, 500, 190, WHITE, 12))
    n.append(rect(760, 828, 500, 190, "transparent").replace(
        'color="transparent"', 'color="transparent" border="1 SOLID #3E7C7455"'))
    T("主轴分布策略对比", 784, 846, 300, 24, 16, INK, "LEFT", "BOLD", SANS,
      nodes=n)
    demos = [("SPACE_BETWEEN", "SPACE_BETWEEN"),
             ("SPACE_AROUND", "SPACE_AROUND"),
             ("SPACE_EVENLY", "SPACE_EVENLY")]
    for i, (lab, mode) in enumerate(demos):
        dy = 884 + i * 40
        T(lab, 784, dy + 4, 150, 20, 11, INK, "LEFT", "NORMAL", MONO,
          nodes=n)
        n.append(positioned(944, dy, 292, 28, space_demo_row(lab, mode)))

    # C. 约束构件
    n.append(rect(1300, 828, 560, 190, WHITE, 12))
    n.append(rect(1300, 828, 560, 190, "transparent").replace(
        'color="transparent"', 'color="transparent" border="1 SOLID #3E7C7455"'))
    T("约束构件", 1324, 846, 300, 24, 16, INK, "LEFT", "BOLD", SANS,
      nodes=n)
    # AspectRatio 2.5（容器 150×60 恰好满足 2.5：紧约束下按比例缩放）
    n.append(positioned(1324, 884, 150, 60,
                        f'<AspectRatio aspectRatio="2.5">'
                        f'<Container '
                        f'gradientType="LINEAR" gradientColors="#3E7C74,'
                        f'#2B4C7E" gradientBegin="CENTER_LEFT" '
                        f'gradientEnd="CENTER_RIGHT"/></AspectRatio>'))
    T("AspectRatio 2.5", 1324, 950, 220, 18, 10, REED, "CENTER", "NORMAL",
      MONO, nodes=n)
    # FractionallySizedBox（参照盒 + 55%×60% 子盒）
    n.append(positioned(1580, 884, 220, 60,
                        f'<Container width="220" height="60" '
                        f'color="{SKY}" borderRadius="6">'
                        f'<FractionallySizedBox widthFactor="0.55" '
                        f'heightFactor="0.6" alignment="CENTER">'
                        f'<Container '
                        f'color="{ORANGE}" borderRadius="4"/>'
                        f'</FractionallySizedBox></Container>'))
    T("FractionallySizedBox .55×.6", 1580, 950, 220, 18, 10, REED,
      "CENTER", "NORMAL", MONO, nodes=n)
    # ConstrainedBox（Align 松约束父级 + minHeight 40，probe5 实证：
    # 紧约束父级下 maxWidth/minHeight 失效，Align 下 minHeight 把 20 抬到 40）
    n.append(positioned(1324, 972, 476, 40,
                        f'<Align alignment="CENTER_LEFT">'
                        f'<ConstrainedBox minHeight="40">'
                        f'<Container width="240" height="20" '
                        f'color="{TEAL}" borderRadius="6">'
                        f'{txt("ConstrainedBox minHeight 40（20 → 40）", 11, WHITE)}'
                        f'</Container></ConstrainedBox></Align>'))

    # ================= 稿纸页脚 =================
    n.append(rect(60, 1040, 1800, 1, "#1E3B2F33"))
    T("设计稿 · 非运行界面 · 构件行为以 open-snapshot 渲染实证为准", 60,
      1054, 900, 20, 11, REED, "LEFT", "NORMAL", SANS, nodes=n)
    T("鹭洲湿地公园管理处 · 信息亭 V2 · 3 / 3", 1020, 1054, 840, 20, 11,
      REED, "RIGHT", "NORMAL", SANS, nodes=n)

    out = snapshot(W, H, n, PAPER)
    probs = assert_canvas(out, W, H)
    for p in probs + WARN:
        print("WARN:", p)
    return out


if __name__ == "__main__":
    s = dsl()
    out = Path(__file__).resolve().parent / "case-05-v01.snapshot"
    out.write_text(s, encoding="utf-8")
    print("wrote", out, len(s), "B")
