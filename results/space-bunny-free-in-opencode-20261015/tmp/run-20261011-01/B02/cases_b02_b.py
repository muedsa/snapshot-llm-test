#!/usr/bin/env python
# B02 触点作品 06–10：逾期提醒 / 维修台标签 / 开放日单张 / 归还检查单 / 志愿者排班板。
# 启动基准：总任务根 (suite_root)。用法：python cases_b02_b.py
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B02"))
from b02kit import (BG, CLAY, DIM, GREY, HAIR, INK, INK_BG, MOSS, NIGHT,
                    OCHRE, PAPER, PAPER2, STATUS, TOOL, W500, W600,
                    brand_footer, bullets, canvas, cat_badge, circle,
                    em_width, footer, header, label_strip, line_h,
                    status_chip, thick_divider)
from bsnap import rect, txt, wrap

FULL = "旧物仓 · 邻里共享"


# ═══════════════════════════ 06 逾期提醒 560×1200
def tp06():
    """锁屏上的一条推送：必须在两秒内让人知道「哪件、迟了几天、会怎样」。

    560×1200，接近手机竖屏宽度的窄条。这是全套里**最窄**的一件，
    用来检验同一套字号层级在窄容器下还站不站得住。
    """
    W, H = 560, 1200
    b = [rect(0, 0, W, H, "#0A0F0D")]
    b.append(txt("推送预览", 40, 36, 300, None, 20, DIM))
    # 推送卡
    b.append(rect(32, 80, 496, 156, NIGHT, 16, border="1 SOLID #2A3A34"))
    b.append(circle(68, 122, 28, CLAY))
    b.append(txt("旧", 68 - 14, 108, 28, None, 22, PAPER, W600, align="CENTER"))
    b.append(txt("旧物仓", 108, 98, 200, None, 20, PAPER, W600))
    b.append(txt("现在", 420, 100, 80, None, 17, DIM, align="END"))
    b.append(txt("「台锯」已逾期 3 天，今天是最后一天。", 108, 138, 400, None, 19,
                 PAPER))
    # 正文
    b.append(txt("旧物仓", 40, 286, 300, None, 28, CLAY, W600))
    b.append(txt("今天 20:00 前", 40, 336, 480, None, 40, PAPER, W600))
    b.append(txt("「台锯 A-10」逾期 3 天。", 40, 400, 480, None, 24, PAPER))
    b.append(txt("逾期每日扣 1 次信用额度；累计 3 次后暂停借阅。",
                 40, 440, 480, None, 22, "#C7CFC9"))
    b.append(txt("扣满 6 次需到站说明。", 40, 478, 480, None, 22, "#C7CFC9"))

    label_strip(b, 40, 540, 480, "A-10 台锯", "工具", "逾期")
    b.append(rect(40, 640, 480, 156, "#1D2F28", 12, border="1 SOLID #2A3A34"))
    b.append(txt("已逾期 3 天", 64, 658, 260, None, 24, CLAY, W600))
    b.append(txt("已扣信用额度", 64, 700, 260, None, 19, DIM))
    b.append(txt("3 / 6 次", 324, 690, 160, None, 30, CLAY, W600, align="END"))
    b.append(rect(64, 748, 400, 12, "#2A3A34", 6))
    b.append(rect(64, 748, 200, 12, CLAY, 6))

    for i, (label, col, sub) in enumerate(
            (("今天就还", MOSS, "免扣 1 次"), ("预约明天还", TOOL, "多等 1 天"),
             ("申请延期", OCHRE, "可续 14 天"))):
        y = 828 + i * 80
        b.append(rect(40, y, 480, 66, col + "22", 12, border=f'1 SOLID {col}'))
        b.append(txt(label, 64, y + 20, 240, None, 22, col, W600))
        b.append(txt(sub, 300, y + 22, 196, None, 19, PAPER, align="END"))
    b.append(rect(40, 1076, 480, 68, CLAY, 12))
    b.append(txt("扫码还", 40, 1096, 480, None, 24, "#0F1A16", W600,
                 align="CENTER"))
    brand_footer(b, 40, H - 56, 480, "推送稿；示例数据，非真实用户")
    return canvas(W, H, "".join(b), "#0A0F0D")


# ═══════════════════════════ 07 维修台标签 1200×800
def tp07():
    """工作台上的一叠标签：修完贴回墙上，撕下来单张要看清「哪件、谁修、还要试什么」。

    1200×800，每张标签是独立一张、边缘带撕线。
    标签只在**维修台**这一个场景出现，因此字号比面向顾客的页面更大。
    """
    W, H = 1200, 800
    b = [rect(0, 0, W, H, PAPER)]
    b.append(txt(FULL, 56, 40, 400, None, 24, CLAY, W600))
    b.append(txt("维修台 · 挂签", 56, 80, 520, None, 44, NIGHT, W600))
    b.append(txt("修完贴回墙上；撕线以下可裁", 760, 52, 384, None, 19, DIM,
                 align="END"))
    tags = [
        ("A-13 切割机", "工具", "待修", "M. Ito", "换碳刷 + 校准护罩", "07-18"),
        ("A-04 热风枪", "工具", "待修", "周 珩", "电源线外皮破损，待换线", "07-17"),
        ("A-27 气罐", "露营", "待修", "李 岚", "阀门渗漏，送外修", "07-15"),
        ("A-32 婴儿推车", "育儿", "待修", "陈 禾", "后轮轴承异响", "07-20"),
    ]
    for i, (ident, cat, st, who, todo, due) in enumerate(tags):
        cx = 56 + (i % 2) * 552
        cy = 160 + (i // 2) * 296
        b.append(rect(cx, cy, 536, 268, PAPER2 + "CC", 12,
                      border="1 SOLID #D9CFBC"))
        b.append(rect(cx, cy, 536, 10, STATUS[st], 4))
        label_strip(b, cx + 0, cy + 10, 536, ident, cat, st, size=19)
        b.append(txt(ident.split(" ", 1)[1], cx + 24, cy + 78, 340, None, 30,
                     NIGHT, W600))
        b.append(txt("台面待办", cx + 24, cy + 126, 200, None, 18, DIM))
        b.append(txt(todo, cx + 24, cy + 154, 490, None, 21, NIGHT))
        b.append(rect(cx + 24, cy + 196, 488, 1, "#D9CFBC"))
        b.append(txt("接修人", cx + 24, cy + 208, 120, None, 18, DIM))
        b.append(txt(who, cx + 144, cy + 206, 180, None, 20, NIGHT, W600))
        b.append(txt("预计复通", cx + 340, cy + 208, 120, None, 18, DIM))
        b.append(txt(due, cx + 452, cy + 206, 70, None, 20, OCHRE, W600,
                     align="END"))
        # 撕线
        for k in range(28):
            b.append(rect(cx + 20 + k * 18, cy + 252, 10, 3, "#C9BEA8", 1))
    b.append(rect(56, H - 74, 1088, 1, "#D9CFBC"))
    b.append(txt("4 件在修，平均 1.6 天复通；积压超过 5 件需要加派人手",
                 56, H - 56, 700, None, 19, NIGHT))
    b.append(txt("示例数据", 940, H - 56, 204, None, 19, DIM, align="END"))
    return canvas(W, H, "".join(b), PAPER)


# ═══════════════════════════ 08 开放日单张 900×1200
def tp08():
    """贴在社区公告栏的 A3 单张：目标是**路过的陌生人**在 5 秒内决定要不要来看。

    900×1200。它的受众不是会员，是还没听说过的人，
    所以标题比说明重要，开门时间比规则重要。
    """
    W, H = 900, 1200
    b = [rect(0, 0, W, H, INK_BG)]
    b.append(rect(0, 0, W, 18, CLAY))
    b.append(txt(FULL, 56, 56, 400, None, 22, CLAY, W600))
    b.append(txt("开放日", 56, 100, 700, None, 96, PAPER, W600))
    b.append(txt("来试一次，不用先办卡", 56, 218, 700, None, 30, MOSS))
    b.append(rect(56, 282, 788, 1, HAIR))

    b.append(txt("7 月 19 日", 56, 314, 500, None, 44, CLAY, W600))
    b.append(txt("10:00 – 17:00 · 旧仓街 12 号", 56, 372, 700, None, 24, PAPER))

    prog = [("10:30", "电钻怎么选", TOOL), ("11:30", "露营装备清单", MOSS),
            ("13:30", "儿童推车怎么借", OCHRE), ("15:00", "修补工作坊", CLAY),
            ("16:30", "自由参观", "#9B6BFF")]
    y = 440
    for t, title, col in prog:
        b.append(rect(56, y, 6, 56, col, 3))
        b.append(circle(80, y + 28, 9, col))
        b.append(txt(t, 104, y + 6, 120, None, 24, col, W600))
        b.append(txt(title, 104, y + 34, 400, None, 20, PAPER))
        b.append(rect(56, y + 66, 788, 1, HAIR))
        y += 82
    b.append(txt("全天免费 · 不需预约 · 带旧物来可以折积分",
                 56, y + 20, 788, None, 24, MOSS))
    b.append(rect(56, y + 76, 788, 88, CLAY, 12))
    b.append(txt("扫码看本周在借榜", 56, y + 102, 788, None, 26, "#0F1A16", W600,
                 align="CENTER"))
    brand_footer(b, 56, H - 62, 788, "单张为设计稿；日期与场次为示例")
    return canvas(W, H, "".join(b), NIGHT)


# ═══════════════════════════ 09 归还检查单 1400×900
def tp09():
    """归还台上压着的清单：值班员逐项打勾，三项不合格就当场拒收。

    1400×900 横版，贴桌。复用同一套状态色：合格=苔绿，待清洁=赭黄，缺件=砖红。
    """
    W, H = 1400, 900
    b = [rect(0, 0, W, H, PAPER)]
    b.append(rect(0, 0, W, 168, INK_BG))
    b.append(txt(FULL, 56, 34, 420, None, 24, CLAY, W600))
    b.append(txt("归还检查单", 56, 74, 620, None, 50, PAPER, W600))
    b.append(txt("值班员逐项打勾 · 三项不合格当场拒收", 700, 96, 644, None, 21, MOSS,
                 align="END"))
    b.append(txt("单号 R-2026-0712-004", 700, 40, 644, None, 20, DIM,
                 align="END"))

    cols = ["检查项", "合格标准", "结果", "备注"]
    cx = [64, 420, 760, 980]
    for i, c in enumerate(cols):
        b.append(txt(c, cx[i], 204, 320, None, 22, DIM, W600))
    b.append(rect(64, 244, 1272, 2, NIGHT))
    rows = [
        ("外观", "无新增划痕与变形", "合格"),
        ("清洁", "无油污、无异味", "待清洁"),
        ("耗材", "锯片 / 电池 / 滤芯 齐全", "合格"),
        ("零件", "螺丝、卡扣、推杆 无缺失", "缺件"),
        ("功能", "空载运行 30 秒无异响", "待检"),
        ("附件", "说明书与原包装 随物归还", "合格"),
    ]
    y = 266
    for name, std, res in rows:
        col = {"合格": MOSS, "待清洁": OCHRE, "缺件": STATUS["缺件"],
               "待检": TOOL}[res]
        b.append(rect(64, y, 1272, 70, PAPER2 + "88", 8))
        b.append(txt(name, cx[0] + 18, y + 22, 320, None, 24, NIGHT, W600))
        b.append(txt(std, cx[1] + 18, y + 24, 320, None, 20, "#3B4A44"))
        b.append(rect(cx[2] - 6, y + 16, 130, 40, col + "2E", 20,
                      border=f'1 SOLID {col}'))
        b.append(txt(res, cx[2] - 6, y + 25, 130, None, 20, col, W600,
                     align="CENTER"))
        b.append(txt("", cx[3], y + 22, 300, None, 20, DIM))
        b.append(rect(cx[3], y + 34, 330, 2, "#C9BEA8"))
        y += 80
    b.append(rect(64, y + 8, 1272, 84, NIGHT, 12))
    b.append(txt("结论", 88, y + 26, 120, None, 22, CLAY, W600))
    b.append(txt("有 3 项不合格，本件当场拒收；已通知会员，顺延一天。",
                 208, y + 26, 900, None, 22, PAPER))
    b.append(txt("值班员签字", 88, y + 56, 160, None, 19, DIM))
    b.append(rect(248, y + 78, 260, 2, "#4A5A54"))
    brand_footer(b, 64, H - 62, 1272, "检查单为设计稿；示例数据，非真实记录")
    return canvas(W, H, "".join(b), PAPER)


# ═══════════════════════════ 10 志愿者排班板 1600×1000
def tp10():
    """志愿者看板上墙：一眼找到「我今天几点到哪个岗」，并知道谁同岗。

    1600×1000。横轴是时段、纵轴是岗位，用颜色区分班次类型；
    这是整套生态里唯一同时用到时间轴和颜色编码的一件。
    """
    W, H = 1600, 1000
    b = [rect(0, 0, W, H, PAPER)]
    b.append(rect(0, 0, W, 166, INK_BG))
    b.append(txt(FULL, 56, 32, 420, None, 24, CLAY, W600))
    b.append(txt("本周志愿者排班", 56, 72, 700, None, 48, PAPER, W600))
    b.append(txt("7 月 13 – 19 日", 1100, 46, 444, None, 26, MOSS, align="END"))
    b.append(txt("共 14 个班次 · 8 位志愿者", 1100, 96, 444, None, 20, DIM,
                 align="END"))
    SHIFT = {"开站": MOSS, "闭站": TOOL, "维修": OCHRE, "活动": CLAY}
    lx = 56
    for s, c in SHIFT.items():
        b.append(rect(lx, 140, 18, 18, c, 4))
        b.append(txt(s, lx + 28, 134, 90, None, 18, PAPER))
        lx += 130

    roles = ["柜台", "取还登记", "工具墙", "维修台", "开放日讲解"]
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    sched = [
        [("开站", "陈 禾", ""), ("闭站", "M. Ito", ""), ("开站", "周 珩", ""),
         ("闭站", "李 岚", ""), ("开站", "陈 禾", ""), ("活动", "全员", "09:30–17:00"),
         ("闭站", "M. Ito", "")],
        [("开站", "李 岚", ""), ("闭站", "陈 禾", ""), ("开站", "M. Ito", ""),
         ("维修", "周 珩", "13:00–18:00"), ("闭站", "李 岚", ""),
         ("活动", "全员", "09:30–17:00"), ("开站", "陈 禾", "")],
        [("闭站", "M. Ito", ""), ("开站", "周 珩", ""), ("闭站", "李 岚", ""),
         ("闭站", "陈 禾", ""), ("开站", "M. Ito", ""), ("活动", "全员", "09:30–17:00"),
         ("闭站", "周 珩", "")],
        [("开站", "陈 禾", ""), ("维修", "M. Ito", "14:00–20:00"),
         ("开站", "李 岚", ""), ("闭站", "周 珩", ""), ("闭站", "M. Ito", ""),
         ("活动", "全员", "09:30–17:00"), ("开站", "李 岚", "")],
        [("闭站", "周 珩", ""), ("开站", "陈 禾", ""), ("开站", "M. Ito", ""),
         ("闭站", "李 岚", ""), ("维修", "陈 禾", "13:00–18:00"),
         ("活动", "全员", "09:30–17:00"), ("闭站", "周 珩", "")],
    ]
    X0, X1 = 300, 1544
    Y0, RH = 234, 112
    dw = (X1 - X0) / 7
    for j, d in enumerate(days):
        b.append(txt(d, X0 + dw * j, 192, dw, None, 22, NIGHT, W600,
                     align="CENTER"))
        if j:
            b.append(rect(X0 + dw * j, Y0 - 8, 1, len(roles) * RH + 8, "#D9CFBC"))
    for i, role in enumerate(roles):
        ry = Y0 + i * RH
        b.append(txt(role, 56, ry + 30, 240, None, 24, NIGHT, W600))
        b.append(rect(56, ry + RH - 8, W - 112, 1, "#D9CFBC"))
        for j in range(7):
            sh, who, extra = sched[i][j]
            col = SHIFT[sh]
            x = X0 + dw * j + 6
            b.append(rect(x, ry + 6, dw - 12, RH - 22, col + "2E", 10,
                          border=f'1 SOLID {col}88'))
            b.append(txt(sh, x + 12, ry + 14, dw - 36, None, 19, col, W600))
            b.append(txt(who, x + 12, ry + 38, dw - 36, None, 20, NIGHT))
            if extra:
                b.append(txt(extra, x + 12, ry + 62, dw - 36, None, 16, DIM))
    b.append(rect(56, H - 96, W - 112, 1, "#D9CFBC"))
    b.append(txt("换班请提前 24 小时在群里说一声；缺岗由「闭站」班次的人顶。",
                 56, H - 78, 800, None, 19, NIGHT))
    b.append(txt("示例排班，非真实志愿者信息", 1000, H - 78, 544, None, 19, DIM,
                 align="END"))
    return canvas(W, H, "".join(b), PAPER)