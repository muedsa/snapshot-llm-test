#!/usr/bin/env python
# B02 触点作品 01–05：门头招牌 / 会员卡 / 借还规则 / 工具墙目录 / App 物品详情。
# 启动基准：总任务根 (suite_root)。用法：python cases_b02_a.py
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

BRAND = "旧物仓"
FULL = "旧物仓 · 邻里共享"


# ═══════════════════════════ 01 门头招牌 1600×600
def tp01():
    """街角门头：5–8 米外站着的人，五秒内要知道「这是什么、能不能进、几点开」。

    远观环境，字号按观看距离放大到 96px；不做任何细节，只做三件事：
    名字、品类、开门时间。品类用色点带出，和 App 里的分类徽标同一套颜色。
    """
    W, H = 1600, 600
    b = [rect(0, 0, W, H, INK_BG)]
    b.append(rect(0, 0, 560, H, CLAY))
    b.append(txt(BRAND, 72, 148, 420, None, 96, PAPER, W600))
    b.append(txt("邻里共享物品站", 76, 268, 420, None, 30, PAPER + "CC"))
    b.append(rect(72, 330, 130, 6, PAPER, 3))
    b.append(txt("借一件 · 用完还回来", 72, 360, 420, None, 26, PAPER + "AA"))

    b.append(txt("全场 412 件在册", 640, 96, 700, None, 34, PAPER, W600))
    b.append(txt("工具 · 厨具 · 露营 · 育儿 · 清洁 · 图书", 640, 146, 900, None, 24,
                 MOSS))
    b.append(circle(648, 196, 14, TOOL))
    b.append(circle(690, 196, 14, CLAY))
    b.append(circle(732, 196, 14, MOSS))
    b.append(circle(774, 196, 14, OCHRE))
    b.append(circle(816, 196, 14, "#7C8DA0"))
    b.append(circle(858, 196, 14, "#9B6BFF"))
    b.append(txt("色点 = 物品分类，与 App 内徽标同一套", 890, 182, 560, None, 19, DIM))

    b.append(rect(640, 246, 880, 1, HAIR))
    b.append(txt("开放时间", 640, 274, 300, None, 24, DIM))
    hours = [("周二 – 周四", "18:00 – 21:00"), ("周五", "18:00 – 22:00"),
             ("周六 – 周日", "10:00 – 17:00"), ("周一", "闭站")]
    for i, (d, h) in enumerate(hours):
        x = 640 + (i % 2) * 450
        y = 316 + (i // 2) * 54
        b.append(txt(d, x, y, 240, None, 24, PAPER, W600))
        b.append(txt(h, x + 250, y, 190, None, 24, CLAY if h != "闭站" else GREY,
                     align="END"))
    b.append(rect(640, 448, 880, 76, MOSS + "22", 12, border=f'1 SOLID {MOSS}'))
    b.append(txt("凭会员卡免费借，无需押金；", 664, 464, 460, None, 24, MOSS))
    b.append(txt("首次到站现场办卡，只需身份证。", 664, 494, 560, None, 24, PAPER))
    brand_footer(b, 72, H - 78, W - 144,
                 "门头效果图；示例数据，非真实运营记录")
    return canvas(W, H, "".join(b), NIGHT)


# ═══════════════════════════ 02 会员卡 1050×600
def tp02():
    """口袋里的卡：掏出来的那一秒要看到「我是谁、有效期到什么时候、怎么用」。

    1050×600 的银行卡比例，85.6×54mm 印刷。三面都印齐，
    背面是给店员看的取件规则；信息密度比门头高一档，字号下限仍是 18px。
    """
    W, H = 1050, 600
    b = [rect(0, 0, W, H, NIGHT)]
    # 正面
    b.append(rect(0, 0, W, 330, INK_BG))
    b.append(rect(0, 330, W, 2, CLAY))
    b.append(txt(FULL, 56, 48, 600, None, 26, CLAY, W600))
    b.append(txt("借阅证", 56, 96, 300, None, 44, PAPER, W600))
    b.append(txt("NO. 2026-0731-0412", 700, 100, 294, None, 20, DIM, align="END"))
    b.append(txt("持卡人", 56, 196, 120, None, 18, DIM))
    b.append(txt("陈 屿", 56, 220, 320, None, 34, PAPER, W600))
    b.append(txt("有效至 2027-06-30", 700, 196, 294, None, 20, PAPER,
                 W600, align="END"))
    b.append(txt("会员等级 · 长期会员", 700, 226, 294, None, 18, MOSS,
                 align="END"))
    for i in range(3):
        b.append(rect(640 + i * 26, 282, 18, 18, "#2A3A34", 4))
    b.append(txt("在借 2 件 · 信用额度 6 件", 56, 278, 460, None, 20, MOSS))
    # 背面
    b.append(txt("取件与归还", 56, 366, 400, None, 24, PAPER, W600))
    rules = [
        ("借期", "最长 14 天，可续一次"),
        ("逾期", "第 15 天起每日扣 1 次信用额度"),
        ("损坏", "按修补成本折算，柜台当场结算"),
        ("查询", "扫码查看在借清单与到期日"),
    ]
    for i, (k, v) in enumerate(rules):
        x = 56 + (i % 2) * 480
        y = 408 + (i // 2) * 52
        b.append(circle(x + 5, y + 16, 8, CLAY))
        b.append(txt(k, x + 24, y + 4, 90, None, 20, CLAY, W600))
        b.append(txt(v, x + 118, y + 4, 340, None, 20, PAPER))
    brand_footer(b, 56, H - 44, W - 112, "卡面为设计稿；示例数据，非真实持卡人")
    return canvas(W, H, "".join(b), NIGHT)


# ═══════════════════════════ 03 借还规则 A4 1240×1754
def tp03():
    """柜台立牌：站着翻阅，单页讲清六条规则，别让人问第三遍。

    A4 竖版，贴在前台。规则用编号 + 大字标题 + 一行解释，
    最后一块放「逾期怎么算」的时间条——这是最常被问的一条。
    """
    W, H = 1240, 1754
    b = [rect(0, 0, W, H, PAPER)]
    b.append(rect(0, 0, W, 210, INK_BG))
    b.append(txt(FULL, 64, 40, 600, None, 26, CLAY, W600))
    b.append(txt("借还规则", 64, 86, 600, None, 64, PAPER, W600))
    b.append(txt("前台立牌 · 六条看完就能借", 64, 160, 600, None, 24, MOSS))
    b.append(txt("2026 年 7 月版", 900, 46, 276, None, 20, DIM, align="END"))
    b.append(txt("旧物仓", 900, 140, 276, None, 40, PAPER, W600, align="END"))

    rules = [
        ("01", "借期最长 14 天", "到期前可在 App 或柜台续借一次，续借后再顺延 14 天。", TOOL),
        ("02", "一次最多 6 件", "其中大型工具不超过 2 件；露营装备需同时借出租赁炉具。", MOSS),
        ("03", "无押金，但要押信用", "首次办卡即获得 6 件信用额度，逾期会逐日占用。", CLAY),
        ("04", "坏了不用赔新的", "按修补成本折算；柜台当场结算，小额直接抵扣信用额度。", OCHRE),
        ("05", "不外借、不转卖", "物品所有权归旧物仓，遗失按重置价从信用额度扣除。", "#7C8DA0"),
        ("06", "还回来要过检查台", "清洁、耗材、零件三项目视；不合格可拒收并顺延一天。", "#9B6BFF"),
    ]
    y = 268
    for num, title, desc, col in rules:
        b.append(rect(64, y, 1112, 150, PAPER2 + "AA", 12))
        b.append(rect(64, y, 8, 150, col, 4))
        b.append(txt(num, 96, y + 22, 90, None, 40, col, W600))
        b.append(txt(title, 196, y + 26, 520, None, 30, NIGHT, W600))
        b.append(txt(desc, 196, y + 76, 940, None, 21, "#3B4A44"))
        y += 168

    b.append(rect(64, y, 1112, 200, NIGHT, 12))
    b.append(txt("逾期怎么算", 96, y + 20, 400, None, 28, CLAY, W600))
    marks = [("第 1–14 天", "正常", MOSS), ("第 15 天", "扣 1 次额度", OCHRE),
             ("第 16–30 天", "每日扣 1 次", CLAY), ("超 30 天", "暂停借阅", "#B4574E")]
    bx, bw = 96, 1000 / 4
    for i, (d, e, col) in enumerate(marks):
        x = bx + i * bw
        b.append(rect(x, y + 78, bw - 10, 64, col + "2E", 8,
                      border=f'1 SOLID {col}'))
        b.append(txt(d, x, y + 86, bw - 10, None, 19, col, W600, align="CENTER"))
        b.append(txt(e, x, y + 114, bw - 10, None, 18, PAPER, align="CENTER"))
    b.append(txt("额度扣满后需到站说明情况并补办，柜台会协助恢复。",
                 96, y + 156, 1000, None, 19, DIM))
    brand_footer(b, 64, H - 66, 1112, "规则文本为示例；实际条款以站点公示为准")
    return canvas(W, H, "".join(b), PAPER)


# ═══════════════════════════ 04 工具墙目录 A2 1400×1980
def tp04():
    """站在工具墙前 1.5 米扫一眼：这一面墙上有什么、哪几件状态不对。

    这是整套生态里**密度最高**的一件，用来检验组件在高密度下是否还成立。
    4 列 × 9 行 = 36 格，每格只放：缩略占位 + 名称 + 状态点 + 编号。
    标签条、状态点、圆角半径全部沿用同一套规则。
    """
    W, H = 1400, 1980
    b = [rect(0, 0, W, H, PAPER)]
    b.append(rect(0, 0, W, 176, INK_BG))
    b.append(txt(FULL, 56, 34, 520, None, 24, CLAY, W600))
    b.append(txt("工具墙 · A 面", 56, 74, 700, None, 52, PAPER, W600))
    b.append(txt("36 格 · 30 件可借", 940, 48, 404, None, 28, MOSS, align="END"))
    b.append(txt("扫码查价与在借状态", 940, 96, 404, None, 20, DIM, align="END"))
    # 状态图例（与 App 同色）
    lx = 56
    for s, c in STATUS.items():
        b.append(circle(lx + 7, 148, 11, c))
        b.append(txt(s, lx + 22, 138, 120, None, 18, PAPER))
        lx += 132

    items = []
    names = ["电钻", "角磨机", "曲线锯", "热风枪", "工具箱", "螺丝套装", "万用表",
             "激光水平仪", "冲击钻", "台锯", "手推刨", "砂磨机", "切割机",
             "内六角组", "套筒组", "钳子组", "卷尺", "水平尺", "美工刀", "电钻夹头",
             "梯子 2m", "梯子 3m", "伸缩梯", "搬运车", "手推独轮车", "捆扎带",
             "露营炉", "气罐", "睡袋", "帐篷", "天幕", "折叠桌椅", "保温箱",
             "儿童自行车", "婴儿推车", "安全座椅", "学步车", "围栏"]
    cats = ["工具", "工具", "工具", "工具", "工具", "工具", "工具", "工具",
            "工具", "工具", "工具", "工具", "工具", "工具", "工具", "工具",
            "工具", "工具", "工具", "工具", "工具", "工具", "工具", "工具",
            "工具", "工具", "露营", "露营", "露营", "露营", "露营", "露营",
            "露营", "育儿", "育儿", "育儿", "育儿", "育儿"]
    sts = ["可借", "已借出", "可借", "待修", "可借", "逾期", "可借", "缺件",
           "可借", "已借出", "可借", "可借", "待修", "可借", "可借", "逾期",
           "可借", "可借", "缺件", "可借", "可借", "已借出", "可借", "可借",
           "逾期", "可借", "可借", "待修", "可借", "已借出", "可借", "可借",
           "缺件", "可借", "可借", "逾期", "可借"]
    for i, (n, c, s) in enumerate(zip(names, cats, sts)):
        items.append((f"A-{i + 1:02d}", n, c, s))

    COLS, GX, GY = 4, 40, 28
    CW = (W - 2 * GX - (COLS - 1) * GY) / COLS
    RH = 160
    y0 = 216
    for i, (ident, name, cat, st) in enumerate(items):
        cx = GX + (i % COLS) * (CW + GY)
        cy = y0 + (i // COLS) * (RH + 14)
        col = STATUS[st]
        b.append(rect(cx, cy, CW, RH, PAPER2 + "AA", 10,
                      border=f'2 SOLID {col}' if st != "可借" else "1 SOLID #D9CFBC"))
        # 缩略占位：用几何块表示，不画照片（DSL 内无 <Image>）
        b.append(rect(cx + 12, cy + 12, CW - 24, 88, INK_BG + "AA", 8))
        b.append(circle(cx + CW / 2, cy + 56, 34, col + "55"))
        b.append(circle(cx + CW / 2, cy + 56, 18, col + "AA"))
        b.append(txt(name, cx + 12, cy + 104, CW - 24, None, 22, NIGHT, W600))
        b.append(txt(cat, cx + 12, cy + 132, 90, None, 17, DIM))
        b.append(txt(ident, cx + 100, cy + 132, CW - 170, None, 16, "#A79C88"))
        b.append(circle(cx + CW - 92, cy + 52, 11, col))
        b.append(txt(st, cx + CW - 72, cy + 43, 60, None, 16, col, W600,
                     align="END"))
    yb = y0 + 9 * (RH + 14) + 10
    b.append(rect(GX, yb, W - 2 * GX, 68, NIGHT, 12))
    b.append(txt("墙上 6 件状态异常：", GX + 24, yb + 14, 300, None, 20, PAPER, W600))
    abnormal = [it[0] for it in items if it[3] != "可借"]
    b.append(txt("、".join(abnormal), GX + 24, yb + 40, 940, None, 19, CLAY))
    b.append(txt("到站找值班员", W - GX - 240, yb + 22, 216, None, 19, MOSS,
                 align="END"))
    brand_footer(b, GX, H - 62, W - 2 * GX, "目录为设计稿；示例数据，非真实库存")
    return canvas(W, H, "".join(b), PAPER)


# ═══════════════════════════ 05 App 物品详情 720×1560
def tp05():
    """手机单手握持：拇指可达范围 420px 内放「借 / 还 / 问」三个动作。

    720×1560（9:19.5）。顶部实物大图位 → 关键参数 → 状态与到期 →
    三个动作按钮 → 同类推荐。底部安全区留 96px。
    """
    W, H = 720, 1560
    b = [rect(0, 0, W, H, INK_BG)]
    b.append(rect(0, 0, W, 108, NIGHT))
    b.append(txt("‹ 工具墙 A 面", 40, 34, 240, None, 22, DIM))
    b.append(txt("物品详情", 280, 30, 340, None, 26, PAPER, W600, align="CENTER"))
    b.append(txt("···", 640, 34, 44, None, 24, DIM, align="END"))

    b.append(rect(0, 108, W, 560, NIGHT + "FF"))
    b.append(circle(360, 360, 200, "#1D2F28"))
    b.append(circle(360, 360, 120, TOOL + "44"))
    b.append(circle(360, 360, 52, TOOL))
    b.append(rect(232, 584, 256, 44, NIGHT + "AA", 22, border="1 SOLID #2A3A34"))
    b.append(txt("无实物照片 · 图为占位", 232, 595, 256, None, 17, DIM,
                 align="CENTER"))

    label_strip(b, 40, 700, 640, "A-10 台锯", "工具", "可借")
    b.append(txt("台锯", 40, 768, 400, None, 40, PAPER, W600))
    b.append(txt("T-2026-0188", 40, 824, 300, None, 19, DIM))
    b.append(txt("押金 · 无", 470, 824, 210, None, 19, DIM, align="END"))

    b.append(rect(40, 880, 640, 1, HAIR))
    b.append(txt("参数", 40, 900, 200, None, 22, CLAY, W600))
    specs = [("锯片直径", "185 mm"), ("额定功率", "1200 W"), ("切割深度 90°", "45 mm"),
             ("重量", "4.6 kg"), ("电压", "220 V"), ("附件", "台锯片 1、推杆 1")]
    for i, (k, v) in enumerate(specs):
        x = 40 + (i % 2) * 330
        y = 944 + (i // 2) * 46
        b.append(txt(k, x, y, 126, None, 19, DIM))
        b.append(txt(v, x + 132, y, 188, None, 19, PAPER, align="END"))

    b.append(rect(40, 1096, 640, 132, MOSS + "1E", 12, border=f'1 SOLID {MOSS}'))
    b.append(txt("当前可借", 64, 1114, 260, None, 20, MOSS))
    b.append(txt("上次归还后已清洁检查", 64, 1152, 420, None, 19, PAPER))
    b.append(txt("借出后 14 天内到期", 64, 1182, 420, None, 19, PAPER))

    acts = [("借这件", MOSS, 40), ("看说明", TOOL, 264), ("问值班员", CLAY, 488)]
    for label, col, x in acts:
        b.append(rect(x, 1256, 200, 76, col, 14))
        b.append(txt(label, x, 1280, 200, None, 24, "#0F1A16", W600,
                     align="CENTER"))

    b.append(txt("同类还有", 40, 1372, 300, None, 22, CLAY, W600))
    for i, (n, st) in enumerate((("手推刨", "可借"), ("切割机", "待修"),
                                 ("砂磨机", "可借"))):
        x = 40 + i * 216
        b.append(rect(x, 1410, 200, 84, NIGHT, 10, border="1 SOLID #2A3A34"))
        b.append(circle(x + 30, 1452, 22, STATUS[st] + "66"))
        b.append(txt(n, x + 58, 1436, 132, None, 19, PAPER))
        b.append(txt(st, x + 58, 1464, 132, None, 17, STATUS[st]))
    brand_footer(b, 40, H - 66, 640, "界面稿；示例数据，非真实库存")
    return canvas(W, H, "".join(b), NIGHT)