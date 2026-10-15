#!/usr/bin/env python
# B06 · 把十个日常信息难题重设计成十件作品。
# 每一件都在一个真实存在的生活场景里：先说清用户原本卡在哪，再重排信息结构。
# 启动基准：总任务根 (suite_root)。
# 用法：python tmp/run-20261011-01/B06/build_b06.py [all|1..10] [版本号]
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/B06"))
from b06kit import (ACCENTS, CARD, COOL, FAINT, HAIR, INKD, MUTE, PAPER, SHADE,  # noqa: E402
                    WARM, W400, W500, W600, barrow, canvas, dot_scale, footer, kicker,
                    line_h, masthead, pill, range_bar, rect, rule, section,
                    source_note, structbar, t, tighten_report, tighten_reset, tw, wrap, hw)
from bsnap import circle, segment  # noqa: E402

M = 56          # 统一左右外边距


def finish(b: list, w: int, y: int, bg: str, tail: int = 150) -> str:
    """画布高度由内容推出：最后一段内容 + tail，页脚再占用 tail 中的 110px。
    这样「正文压到页脚」与「图元出界」在生成阶段就不可能发生。"""
    h = int(y + tail)
    b.insert(0, rect(0, 0, w, h, bg))
    return canvas(w, h, "".join(b), bg)


def fit(s, size, max_w, floor=16.0, slack=0.97):
    while size > floor and tw(s, size) > max_w * slack:
        size -= 1
    return size


def f_num(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


# ════════════════════════════════════════════════════════════════════════
# case-01 · 超市购物小票 →「这张小票只回答三个问题」
# ════════════════════════════════════════════════════════════════════════
CATS = [("生鲜蔬果", 86.40, "17.4%"), ("肉禽水产", 134.20, "27.0%"),
        ("米面粮油", 52.60, "10.6%"), ("乳品鸡蛋", 61.80, "12.4%"),
        ("休闲零食", 73.50, "14.8%"), ("日用百货", 48.90, "9.8%"),
        ("调味速食", 39.20, "7.9%")]


def c01():
    W = 980
    acc = ACCENTS[1]
    b = []
    y = masthead(b, 1, W, "超市购物小票（热敏纸）",
                 "小票不是账单：「我花了多少」被埋在第 41 行",
                 "重设计目标：20 秒内答出三件事 —— 花了多少、花在哪、哪些能报销", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "41 行等权信息 · 商品与促销混排", 34),
                  [("第一层", "总额与差额"), ("第二层", "按类目归因"),
                   ("第三层", "大额·可报销·已省")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "结论先于流水", acc,
                "原版把合计放在第 41 行，新版放在第一屏第二行")
    y = kicker(b, M, y, W - M * 2,
               "本次实付 ¥454.20，比上次同店同类多 ¥23.60；其中 ¥38.70 可报销，"
               "3 笔大额占了商品金额的 46.9%。", acc, bg=CARD)
    y += 22

    ch = 196
    b.append(rect(M, y, W - M * 2, ch, CARD, 12))
    b.append(rect(M, y, 6, ch, acc, 3))
    b.append(t("本次实付", M + 28, y + 24, 320, 20, MUTE, W600))
    b.append(t("¥", M + 28, y + 62, 40, 40, MUTE, W600))
    b.append(t("454.20", M + 30 + tw("¥", 40), y + 46, 340, 82, INKD, W600))
    kx = M + 452
    for i, (lab, val, col) in enumerate([("商品金额 24 件", "¥496.60", INKD),
                                         ("优惠合计", "−¥42.40", COOL),
                                         ("上次同店同类", "¥430.60", MUTE)]):
        yy = y + 28 + i * 44
        b.append(t(lab, kx, yy, 210, 19, MUTE, W500))
        b.append(t(val, kx + 214, yy - 4, 178, 22, col, W600, align="END"))
        if i < 2:
            rule(b, kx, yy + 34, 392, "#EDE8DE")
    b.append(t("差额 +¥23.60（+5.5%）", kx, y + 28 + 3 * 44, 392, 19, acc, W600))
    y += ch + 30

    y = section(b, M, y, W - M * 2, "02", "¥496.60 花在哪", acc,
                "按类目归因 · 7 类 · 条长同一尺度")
    top = max(c[1] for c in CATS)
    palette = [COOL, acc, "#B8791B", "#2C6DBF", "#6B52C7", "#5C7A8A", "#9B8A6B"]
    for (name, amt, pct), col in zip(CATS, palette):
        b.append(t(name, M, y + 4, 176, 21, INKD, W600))
        bx, bw = M + 182, 452
        b.append(rect(bx, y + 10, bw, 16, SHADE, 8))
        b.append(rect(bx, y + 10, max(8.0, bw * amt / top), 16, col, 8))
        b.append(t(f"¥{amt:,.2f}", bx + bw + 18, y + 2, 150, 21, col, W600))
        b.append(t(pct, bx + bw + 178, y + 4, 90, 19, FAINT, W500, align="END"))
        y += 42
    y += 12

    y = section(b, M, y, W - M * 2, "03", "三件该做的事", acc,
                "每一件指向一个动作，而不是又一个数字")
    todo = [
        (COOL, "去开票", "¥38.70 可报销", "开票要求「明细小票」并写明品名数量",
         "A4 复印纸 24.90 · 中性笔 9.90 · 文件夹 3.90"),
        (WARM, "先决定要不要买", "¥212.90 = 46.9%", "3 笔单品 ≥ ¥60，占了近一半金额",
         "有机纯牛奶 79.90 · 黑猪里脊 68.00 · 冷萃 65.00"),
        (acc, "确认已省", "−¥42.40", "会员满 400 减 30 + 生鲜促销 12.40",
         "本单得 45 积分 · 下次把 ≥¥60 的三笔挪到月初"),
    ]
    for col, head, num, desc, detail in todo:
        bh = 86
        b.append(rect(M, y, W - M * 2, bh, CARD, 10))
        b.append(rect(M, y, 4, bh, col, 2))
        b.append(t(head, M + 22, y + 14, 400, 21, INKD, W600))
        b.append(t(num, M + 22, y + 46, 400, 22, col, W600))
        b.append(t(desc, M + 440, y + 16, 416, 18, MUTE, W500))
        b.append(t(detail, M + 440, y + 44, 416, 16, FAINT, W500))
        y += bh + 12
    y += 10
    y = source_note(b, M, y, W - M * 2, [
        "依据：商超票据须取得机打购物明细小票；自 2017-07-01 起发票须按实际销售情况如实开具具体品名，不得笼统开「食品」「日用品」。",
    ])
    fy = footer(b, M, y + 26, W - M * 2,
               "自拟示例：小票数据、品牌与门店均为演示用，非真实记录。本页只做信息重排，不构成任何消费建议。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-02 · 居民燃气缴费通知 →「这期为什么比上期多」
# ════════════════════════════════════════════════════════════════════════
GAS = [("去年同期 08 月", 152, "452.96", "4.90"),
       ("上期 09 月", 186, "557.88", "6.00"),
       ("本期 10 月", 231, "718.98", "7.70")]


def c02():
    W = 1480
    acc = ACCENTS[2]
    b = []
    y = masthead(b, 2, W, "居民燃气缴费通知",
                 "账单只给总额，不说是烧多了还是被阶梯价吃掉的",
                 "重设计目标：把金额差额拆成可核对的价格效应与用量效应", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "本期用量 + 金额 + 账期，共 3 个有效数字", 12),
                  [("结论", "差额归因一句话"), ("证据", "3 期用量 × 阶梯价"),
                   ("核对", "价格 + 用量 + 交互")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "多出来的 ¥161.10 去哪了", acc,
                "计量区间 2026-09-16 至 2026-10-15（30 天）")
    y = kicker(b, M, y, W - M * 2,
               "83.8%（¥134.97）来自多烧的 45 m³，16.2%（¥26.13）来自单价结构："
               "用量涨 24.2%，均价只涨 3.8%。", acc, bg=CARD)
    y += 26

    top_v, ch = 252.0, 462
    lw = 828
    b.append(rect(M, y, lw, ch, CARD, 12))
    b.append(t("天然气用量 · 三期对照", M + 26, y + 22, 420, 21, INKD, W600))
    b.append(t("单位 m³ · 三根柱同一尺度", M + 26, y + 52, 420, 17, FAINT, W500))
    # 同比 / 环比 / 均价放卡片右上角：柱区只占左侧 590px，右侧是空的，
    # 首版把这些注记放在柱顶上方，和柱子的数值标签叠在一起（看图发现）。
    for i, (lab, val, col) in enumerate([("同比", "↑52.0%", WARM), ("环比", "↑24.2%", acc)]):
        yy = y + 22 + i * 28
        b.append(t(lab, M + lw - 230, yy, 84, 18, FAINT, W500))
        b.append(t(val, M + lw - 26 - tw(val, 19), yy - 2, tw(val, 19) + 6, 19, col, W600))
    # 「均价」一行两行排：标签与数值各自独占一行，右上角那块只有 210px 宽，
    # 同一行放不下 "均价 /m³" 和 "2.98→3.00→3.11"。
    b.append(t("均价 /m³", M + lw - 230, y + 80, 210, 18, FAINT, W500))
    b.append(t("2.98 → 3.00 → 3.11", M + lw - 230, y + 102, 210, 18, MUTE, W600))
    base = y + 366
    for i, (lab, q, amt, per) in enumerate(GAS):
        cx = M + 52 + i * 210
        hgt = q / top_v * 200
        col = acc if i == 2 else "#C9C2B2"
        b.append(rect(cx, base - hgt, 190, hgt, col, 6))
        b.append(t(f"{q}", cx, base - hgt - 48, 190, 38, col if i == 2 else MUTE,
                   W600, align="CENTER"))
        b.append(t(lab, cx - 10, base + 14, 210, 18, MUTE, W500, align="CENTER"))
        b.append(t(f"¥{amt}", cx - 10, base + 40, 210, 21,
                   acc if i == 2 else MUTE, W600, align="CENTER"))
        b.append(t(f"日均 {per} m³", cx - 10, base + 66, 210, 17, FAINT, W500, align="CENTER"))
    b.append(rect(M + 26, base, lw - 52, 1, HAIR))

    rx, rw = M + lw + 24, W - M * 2 - lw - 24
    b.append(rect(rx, y, rw, ch, CARD, 12))
    b.append(rect(rx, y, rw, 4, acc, 2))
    b.append(t("本期比上期多", rx + 24, y + 22, rw - 48, 19, MUTE, W600))
    b.append(t("¥161.10", rx + 24, y + 44, rw - 48, 62, INKD, W600))
    b.append(t("上期 ¥557.88 → 本期 ¥718.98", rx + 24, y + 112, rw - 48, 18, MUTE, W500))
    py = y + 156
    for lab, amt, pct, col in [("用量效应", 134.97, 83.8, acc),
                               ("价格效应", 21.04, 13.1, "#B8791B"),
                               ("交互项", 5.09, 3.2, "#9BA2AE")]:
        b.append(t(lab, rx + 24, py, 170, 19, INKD, W600))
        bw = rw - 48
        b.append(rect(rx + 24, py + 28, bw, 12, SHADE, 6))
        b.append(rect(rx + 24, py + 28, max(5.0, bw * pct / 100.0), 12, col, 6))
        b.append(t(f"+¥{amt:,.2f}", rx + 24, py + 46, 200, 21, col, W600))
        b.append(t(f"{pct:.1f}%", rx + rw - 110, py + 46, 86, 21, col, W600, align="END"))
        py += 78
    rule(b, rx + 24, py + 2, rw - 48)
    b.append(t("合计 +¥161.10", rx + 24, py + 18, 220, 22, INKD, W600))
    b.append(t("核对 134.97 + 21.04 + 5.09 = 161.10", rx + 24, py + 50, rw - 48, 17,
               FAINT, W500))

    y += ch + 32
    y = section(b, M, y, W - M * 2, "02", "阶梯价：多烧的部分还多付了单价", acc,
                "计费规则：第一档 0–180 m³ @2.98 · 第二档 181–400 m³ @3.58")
    tx0, tw0 = M + 156, W - M * 2 - 156 - 200
    for i, (name, rng, q, price, col, amt) in enumerate(
            [("第一档", "0 – 180 m³", 180, 2.98, "#9FB59C", "536.40"),
             ("第二档", "181 – 231 m³", 51, 3.58, WARM, "182.58")]):
        yy = y + i * 86
        b.append(t(name, M, yy + 8, 150, 21, INKD, W600))
        b.append(t(rng, M, yy + 40, 200, 17, FAINT, W500))
        b.append(rect(tx0, yy + 16, max(60.0, tw0 * (q / 231.0)), 32, col, 6))
        b.append(t(f"{q} m³", tx0 + 14, yy + 20, 200, 22,
                   "#FFFFFF" if i else INKD, W600))
        b.append(t(f"@¥{price:.2f}", tx0 + tw0 + 16, yy + 20, 180, 21, INKD, W600))
        b.append(t(f"¥{amt}", tx0 + tw0 + 16, yy + 48, 180, 19, MUTE, W500))
    y += 86 * 2 + 8
    b.append(t("落在第二阶梯的 51 m³ 单价高 ¥0.60，仅这一项就多付 ¥30.60 —— "
               "原版账单从不显示这一行。", M + 156, y, W - M * 2 - 156, 21, acc, W600))
    y += 48
    y = source_note(b, M, y, W - M * 2, [
        "依据：阶梯计价的「用量 × 单价」效应分解，价格效应 =(P₁−P₀)×Q₀，用量效应 =P₀×(Q₁−Q₀)，交互项 =(P₁−P₀)×(Q₁−Q₀)，三项相加等于总差额。",
        "数据为自拟示例，燃气公司、门牌与账期均为演示用；用量、阶梯单价、分解结果均在本轮用脚本核算，与图中数字一致。",
    ])
    fy = footer(b, M, y + 26, W - M * 2,
           "自拟示例，非真实记录。本页只做信息重排，不构成缴费、计量或燃气安全建议。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-03 · 健康体检报告 →「结果按「下一步做什么」分三档」
# ════════════════════════════════════════════════════════════════════════
TIER1 = [("空腹血糖", "6.9", "mmol/L", 3.9, 6.1, 6.4, "↑ 0.5", "复诊时加做糖化血红蛋白", WARM),
         ("甘油三酯", "2.61", "mmol/L", 0.45, 1.70, 2.38, "↑ 0.23", "血脂门诊评估饮食与家族史", WARM)]
TIER2 = [("尿酸", "452", "µmol/L", 208, 428, 441, "↑ 11", "3 个月后复查，先忌高嘌呤", "#B8791B"),
         ("血红蛋白", "132", "g/L", 130, 175, 126, "↑ 6", "在下沿区间，3 个月后复查", "#B8791B"),
         ("腹部超声", "轻度脂肪肝", "影像所见", 0, 1, 0, "首次", "随体检建议随访，不需用药", "#B8791B")]
TIER3 = [("血压", "118/74", "mmHg", 0, 140, 122, "↓ 4", None, COOL),
         ("总胆固醇", "4.82", "mmol/L", 0, 5.18, 4.90, "持平", None, COOL),
         ("LDL-C", "2.94", "mmol/L", 0, 3.37, 3.02, "↓ 0.08", None, COOL),
         ("肌酐", "78", "µmol/L", 57, 97, 76, "↑ 2", None, COOL),
         ("白细胞", "6.1", "×10^9/L", 3.5, 9.5, 5.8, "↑ 0.3", None, COOL)]


def _lab_card(b, x, y, w, h, item, compact=False):
    """指标卡。首版把单位排在数值右边同一行，在 5 列紧凑排布下单位与数字重叠，
    且区间条下沿的 lo/hi 标签压到了「下一步」行（两处都是打开图才发现的）。
    现在：单位移到名称行右侧、数值独占整行、区间条下沿留出 78px 给标签与动作。"""
    name, val, unit, lo, hi, last, delta, action, col = item
    b.append(rect(x, y, w, h, CARD, 10))
    b.append(rect(x, y, w, 4, col, 2))
    inner = w - 32
    b.append(t(name, x + 16, y + 15, inner * 0.58, 19, MUTE, W600))
    b.append(t(unit, x + 16 + inner * 0.58, y + 16, inner * 0.42, 16, FAINT, W500,
               align="END"))
    vs = fit(val, 40 if compact else 44, inner)
    b.append(t(val, x + 16, y + 40, inner, vs, INKD, W600))
    ry = y + 40 + math.ceil(vs * 1.45) + 2
    if delta:
        b.append(t(delta, x + 16, ry, inner * 0.5, 19, col, W600))
    b.append(t(f"上次 {last}", x + 16 + inner * 0.5, ry, inner * 0.5, 18, FAINT, W500,
               align="END"))
    bar_y = y + h - (78 if action else 48)
    range_bar(b, x + 16, bar_y, inner, lo, hi, f"{lo:g}", f"{hi:g}", f_num(val), lo, hi, col)
    if action:
        b.append(t("下一步", x + 16, y + h - 32, 62, 17, col, W600))
        for i, ln in enumerate(hw(action, 17, inner - 70 - 8)[:2]):
            b.append(t(ln, x + 16 + 70, y + h - 32 + i * line_h(17), inner - 70, 17,
                       MUTE, W500))


def c03():
    W = 1240
    acc = ACCENTS[3]
    b = []
    y = masthead(b, 3, W, "健康体检报告（示例）",
                 "把「正常 / 异常」的二值标签，换成「下一步做什么」",
                 "重设计目标：读者打开第一屏就知道该先做哪一件事", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "28 项按科室平铺 · 标 ↑↓ · 无排序无动作", 22),
                  [("档一", "现在就和医生确认"), ("档二", "3 个月后复查"),
                   ("档三", "结果稳定")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "10 项结果 · 3 个动作档", acc,
                "分档依据：偏离幅度 + 较上次变化；不做诊断")
    cw = W - M * 2
    tiers = [("档一", "现在就和医生确认 · 2 项", WARM, TIER1, 2, 218, 0),
             ("档二", "3 个月后复查 · 3 项", "#B8791B", TIER2, 3, 218, 12),
             ("档三", "结果稳定 · 继续观察 · 5 项", COOL, TIER3, 5, 186, 14)]
    for tag, name, col, items, n, ch, gap in tiers:
        b.append(rect(M, y, 92, 40, col, 8))
        b.append(t(tag, M, y + 8, 92, 24, "#FFFFFF", W600, align="CENTER"))
        b.append(t(name, M + 108, y + 8, 560, 22, INKD, W600))
        b.append(t(f"{n} 项", M + cw - 120, y + 11, 120, 20, FAINT, W500, align="END"))
        y += 52
        cwx = (cw - (n - 1) * gap) / n
        for i, it in enumerate(items):
            _lab_card(b, M + i * (cwx + gap), y, cwx, ch, it, compact=(n == 5))
        y += ch + 26

    y = section(b, M, y, cw, "02", "为什么不只标一个红箭头", acc,
                "参考区间与「异常」不是一回事")
    y = kicker(b, M, y, cw,
               "参考区间通常取健康人群分布的中心 95%。按这一定义，每项都有 5% 的"
               "健康者会被标成异常；开 10 项检查时，全部落在区间内的概率只有约 60%。",
               acc, bg=CARD)
    y += 20
    for i in range(10):
        b.append(rect(M + i * 46, y, 38, 38, COOL, 6))
        b.append(t("95", M + i * 46, y + 9, 38, 20, "#FFFFFF", W600, align="CENTER"))
    b.append(t("10 项各自独立，各 95% 落在区间内", M + 490, y + 10, 500, 19, MUTE, W500))
    b.append(t("→ 至少一项被标「异常」是常态", M, y + 52, cw, 21, acc, W600))
    y += 92
    y = source_note(b, M, y, cw, [
        "依据：参考区间取分布中心 95% 时按定义约有 5% 健康个体落在区间外；各项独立时 n 项全部正常的概率为 0.95^n，n = 10 时约 0.60。",
        "「腹部超声」一行的区间刻度 0 / 1 为编码：0 = 本次未见异常，1 = 有异常所见；其余各行均为可连续比较的数值与单位。",
        "本图为信息结构重排示例，全部数值、单位、参考区间与上次结果均为自拟，不是任何真实体检报告，也不构成诊断、治疗或用药建议。",
    ])
    fy = footer(b, M, y + 26, cw, "自拟示例，非真实记录。任何健康问题请咨询执业医师。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-04 · 航空行程单 →「下一段该做什么」
# ════════════════════════════════════════════════════════════════════════
def c04():
    W = 1440
    acc = ACCENTS[4]
    b = []
    y = masthead(b, 4, W, "航空行程单 / 值机确认页",
                 "行程单按时间顺序平铺，读者真正要的只有一件事：下一段该做什么",
                 "重设计目标：把「现在」钉在时间轴上，其余一切围绕这一段排", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "5 段行程等权平铺 · 无当前态 · 无倒计时", 14),
                  [("现在", "一个游标"), ("下一段", "值机·安检·登机"),
                   ("再下一段", "中转与行李")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "今天 09:00–18:00 的时间轴", acc,
                "当前时刻 2026-10-14 09:36（周三）· 单位为小时")
    y = kicker(b, M, y, W - M * 2,
               "下一段 MU5105 上海虹桥 → 北京首都，11:20 起飞，登机口 C12。"
               "现在该做的三件事按截止时间排列，最紧的一件在 34 分钟后。", acc, bg=CARD)
    y += 26

    # ── 时间轴 ────────────────────────────────────────────────────────
    # 首版把「现在」游标标在 y-96，与顶部倒计时大字、段条全部叠在一起（看图发现）；
    # 现在给这张卡排一条固定的纵向栅格：标题 20 / 倒计时 52 / 游标 124 / 段条 172 / 轴线 228 / 刻度 240。
    ah = 292
    b.append(rect(M, y, W - M * 2, ah, CARD, 12))
    ax0, ax1 = M + 92, M + (W - M * 2) - 92
    span = ax1 - ax0
    per_h = span / 9.0

    def hx(hr: float) -> float:
        return ax0 + (hr - 9.0) * per_h

    ay = y + 230
    b.append(t("下一段 · 11:20 起飞 · 登机口 C12", ax0, y + 20, 900, 21, INKD, W600))
    b.append(t("距起飞 1 h 44", ax0, y + 50, 400, 36, acc, W600))
    b.append(t("托运 1 件 23.0 kg · 手提 1 件 7.4 kg · 座位 32K", ax1 - 600, y + 24, 600, 18,
               MUTE, W500, align="END"))
    b.append(t("本段里程 1,084 km · 经济舱 · 机型 737-800", ax1 - 600, y + 54, 600, 18,
               MUTE, W500, align="END"))
    b.append(rect(ax0, ay, span, 2, "#D8D2C6"))
    for hh in range(9, 19):
        xx = hx(float(hh))
        b.append(rect(xx, ay - 6, 1, 14, "#D8D2C6"))
        b.append(t(f"{hh:02d}:00", xx - 40, ay + 16, 80, 17, FAINT, W500, align="CENTER"))
    segs = [(9.6, 11.333, "值机与安检", "#9FB59C", "1 h 44"),
            (11.333, 13.0, "飞行 MU5105", acc, "1 h 40"),
            (13.0, 14.333, "中转安检", WARM, "1 h 20"),
            (14.333, 17.083, "飞行 MU0301", "#8E9BB0", "2 h 45")]
    for a, c, name, col, dur in segs:
        xa, xc = hx(a), hx(c)
        b.append(rect(xa + 3, ay - 58, xc - xa - 6, 54, col, 6))
        inner = fit(name, 19, xc - xa - 34, 13)
        b.append(t(name, xa + 17, ay - 42, xc - xa - 34, inner, "#FFFFFF", W600))
        b.append(t(dur, xa + 17, ay - 22, xc - xa - 34, 16, "#FFFFFF", W500))
    nowx = hx(9.6)
    b.append(rect(nowx - 2, y + 158, 4, 84, acc, 2))
    b.append(circle(nowx, y + 152, 14, acc))
    b.append(t("现在 09:36", nowx - 90, y + 112, 180, 19, acc, W600, align="CENTER"))
    y += ah + 32

    y = section(b, M, y, W - M * 2, "02", "三件该做的事（按截止时间排序）", acc,
                "倒计时以 09:36 为基准")
    acts = [("已完成", "值机 · B 区 12 号柜台", "10:35 截止", "已取登机牌，座位 32K", COOL),
            ("34 分钟后截止", "过安检 · 3 号安检口", "10:00 前到达", "预计排队 25 分钟 · 随身限 1 件", acc),
            ("起飞前 85 分钟", "登机 · C12 登机口", "10:35 开始登机", "登机口在 C 区尽头，步行 8 分钟", WARM)]
    aw = (W - M * 2 - 2 * 14) / 3
    for i, (badge, title, when, note, col) in enumerate(acts):
        ax = M + i * (aw + 14)
        b.append(rect(ax, y, aw, 160, CARD, 10))
        b.append(rect(ax, y, aw, 4, col, 2))
        b.append(t(badge, ax + 20, y + 18, aw - 40, 18, col, W600))
        b.append(t(title, ax + 20, y + 46, aw - 40, 22, INKD, W600))
        b.append(t(when, ax + 20, y + 78, aw - 40, 20, col, W600))
        b.append(t(note, ax + 20, y + 110, aw - 40, 17, FAINT, W500))
        yb = y + 160 + 10
    y = yb
    y = source_note(b, M, y, W - M * 2, [
        "数据为自拟示例：航班号、时刻、机型、航站楼、门牌与城市均为演示用，非真实行程；倒计时由 09:36 与各截止时刻在本轮用脚本核算。",
        "重设计只改变信息的读取顺序与层级，不改变任何行程字段本身；原行程单上的全部字段在本页都能找到对应位置。",
    ])
    fy = footer(b, M, y + 26, W - M * 2,
           "自拟示例，非真实记录。实际出行请以承运人官方通知为准，本页不构成行程建议。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-05 · 门诊收费票据 →「把 5 张票据合并成 1 笔账」
# ════════════════════════════════════════════════════════════════════════
BILLS = [("09:12", "门诊挂号费", "诊疗", "01-2345", 15.00, 12.00, 3.00),
         ("09:20", "血常规 + 生化 12 项", "检验", "01-2346", 186.50, 149.20, 37.30),
         ("09:35", "腹部超声", "检查", "01-2347", 120.00, 96.00, 24.00),
         ("10:02", "药品 3 种（详见处方）", "药品", "01-2348", 143.60, 0.00, 143.60),
         ("10:15", "输液处置（1 次）", "处置", "01-2349", 48.00, 38.40, 9.60)]
BILL_COLS = [("时间", 92), ("项目", 330), ("类别", 116), ("票据号", 130),
             ("金额", 166), ("医保统筹", 166), ("个人自付", 168)]


def c05():
    W = 1280
    acc = ACCENTS[5]
    b = []
    y = masthead(b, 5, W, "门诊收费票据（一式多张）",
                 "一次就诊散成 5 张票据，没有一张能回答「这次到底花了多少」",
                 "重设计目标：把 5 张票据合成 1 笔账，并标出可退项与办理时限", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "5 张独立票据 · 金额不跨票相加 · 退费信息分散", 17),
                  [("一层", "总额 / 医保 / 自付"), ("二层", "按时间线的 5 个项目"),
                   ("三层", "可退项与截止时限")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "这一笔账的三个总数", acc,
                "2026-10-14 门诊 · 自费比例 42.4%")
    y = kicker(b, M, y, W - M * 2,
               "本次合计 ¥513.10：医保统筹支付 ¥295.60，个人自付 ¥217.50，已全部支付。"
               "若放弃尚未出结果的检验，可退 ¥186.50，需在 10-15 17:00 前到 2 号窗口。",
               acc, bg=CARD)
    y += 24
    nums = [("本次合计", "513.10", "元", INKD), ("医保统筹", "295.60", "元 · 占 57.6%", acc),
            ("个人自付", "217.50", "元 · 占 42.4%", WARM), ("已支付", "513.10", "元 · 尚待支付 0.00", COOL)]
    nw = (W - M * 2 - 3 * 14) / 4
    for i, (lab, val, unit, col) in enumerate(nums):
        nx = M + i * (nw + 14)
        b.append(rect(nx, y, nw, 136, CARD, 12))
        b.append(rect(nx, y, nw, 4, col, 2))
        b.append(t(lab, nx + 20, y + 20, nw - 40, 19, MUTE, W600))
        # 单位首版排在数值右侧同一行，卡片只有 282px 宽时末位数字会被单位压住（看图发现）；
        # 现在单位换到数值下方一行，两者不可能重叠。
        b.append(t(val, nx + 20, y + 50, nw - 40, 42, col, W600))
        b.append(t(unit, nx + 20, y + 98, nw - 40, 18, FAINT, W500))
    y += 136 + 30

    y = section(b, M, y, W - M * 2, "02", "按发生时间排的 5 个项目", acc,
                "金额相加 = 513.10 · 医保 + 自付 = 合计")
    xs, acc_x = [], M
    for _, cwv in BILL_COLS:
        xs.append(acc_x)
        acc_x += cwv
    right_cols = {"金额", "医保统筹", "个人自付"}

    def _cell(yy, x0, cwv, name, v, size, col):
        """右对齐列的盒子必须留在列内：x0+6 起、宽 cwv-12，textAlign=END 在盒内靠右。"""
        if name in right_cols:
            return t(v, x0 + 6, yy, cwv - 12, size, col, W600, align="END")
        return t(v, x0, yy, cwv - 8, size, col, W600)

    b.append(rect(M, y, W - M * 2, 40, SHADE, 6))
    for (name, cwv), x0 in zip(BILL_COLS, xs):
        b.append(_cell(y + 10, x0, cwv, name, name, 18, MUTE))
    y += 40
    for time_, item, kind, no, amt, med, own in BILLS:
        highlight = no == "01-2346"
        b.append(rect(M, y, W - M * 2, 52, "#FBEFE9" if highlight else CARD, 6))
        if highlight:
            b.append(rect(xs[1] - 6, y + 10, 4, 32, WARM, 2))
        vals = [time_, item, kind, no, f"{amt:,.2f}", f"{med:,.2f}", f"{own:,.2f}"]
        cols = [MUTE, INKD, MUTE, FAINT, INKD, acc, WARM]
        for (name, cwv), x0, v, col in zip(BILL_COLS, xs, vals, cols):
            b.append(_cell(y + 15, x0, cwv, name, v, 19, col))
        y += 56
    tot = [f"{sum(r[4] for r in BILLS):,.2f}", f"{sum(r[5] for r in BILLS):,.2f}",
           f"{sum(r[6] for r in BILLS):,.2f}"]
    b.append(rect(M, y, W - M * 2, 48, "#E6E1D6", 6))
    b.append(t("合计（5 张票据）", xs[1], y + 13, 400, 20, INKD, W600))
    for (name, cwv), x0, v, col in zip(BILL_COLS[4:], xs[4:], tot, [INKD, acc, WARM]):
        b.append(_cell(y + 12, x0, cwv, name, v, 20, col))
    y += 48 + 30

    y = section(b, M, y, W - M * 2, "03", "还能反悔的一笔", acc, "原票据不写这件事")
    b.append(rect(M, y, W - M * 2, 128, "#FBEFE9", 10))
    b.append(rect(M, y, 5, 128, WARM, 3))
    b.append(t("可退 ¥186.50", M + 26, y + 18, 320, 32, WARM, W600))
    for i, ln in enumerate(hw(
            "票据 01-2346 · 血标本已于 09:20 采集，结果预计 10-16 出具；"
            "放弃本次检验即可全额退费（含医保统筹 ¥149.20）。", 17, 760)[:2]):
        b.append(t(ln, M + 26, y + 62 + i * line_h(17), 764, 17, MUTE, W500))
    b.append(t("截止", M + 830, y + 22, 100, 18, MUTE, W600))
    b.append(t("10-15 17:00", M + 830, y + 48, 300, 22, WARM, W600))
    b.append(t("地点 2 号退费窗口 · 需带身份证与医保卡", M + 830, y + 80, 310, 16, FAINT, W500))
    y += 128 + 24
    y = source_note(b, M, y, W - M * 2, [
        "数据为自拟示例：医院、科室、票据号、项目与金额均为演示用，非任何真实收费记录；合计、医保、自付在生成前用脚本逐项相加核对。",
        "重设计未改变任何票据字段，只把分散在 5 张票据上的同一笔账合并呈现，并新增「可退项 / 截止时限 / 办理地点」三项汇总。",
    ])
    fy = footer(b, M, y + 26, W - M * 2,
           "自拟示例，非真实记录。费用、医保与退费规则以医院与医保部门实际规定为准。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-06 · 快递电子面单 →「这张面单只回答：寄给谁、寄什么、我该做什么」
# ════════════════════════════════════════════════════════════════════════
FOLDED = ["承运商协议号", "加盟商网点号", "路由信息", "结算中心", "重量校验码",
          "电子面单 ID", "揽收网点", "操作员工号", "月结账号", "签名算法版本",
          "打印次数", "耗材批次", "面单尺寸规格", "重量体积换算系数", "路由版本",
          "时效产品代码", "附加服务代码", "条码校验位"]


def c06():
    W = 1440
    acc = ACCENTS[6]
    b = []
    y = masthead(b, 6, W, "快递电子面单 / 隐私面单",
                 "一张面单上二十多个字段，但寄件人只问三句、收件人只问一件",
                 "重设计目标：把 18 个字段折叠起来，正面只留两个人各自需要的东西", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "22 个等权字段 · 收寄同屏 · 无隐私状态", 22),
                  [("寄件人", "3 个核对问题"), ("收件人", "谁寄的 · 什么时候到"),
                   ("状态", "隐私面单已开启")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "一正一反，两个人的 30 秒", acc,
                "示例单号 SF 7182 0044 1290")
    y = kicker(b, M, y, W - M * 2,
               "寄件人要确认「电话、门牌、隐藏」三件事，收件人只想知道「谁寄的、"
               "什么时候到、要带什么」——其余 18 个字段在这一面全部折叠。", acc, bg=CARD)
    y += 26

    ph = 468
    lw = 720
    # ── 左：寄件人核对 ──────────────────────────────────────────────
    b.append(rect(M, y, lw, ph, CARD, 12))
    b.append(rect(M, y, lw, 4, acc, 2))
    b.append(t("寄件人核对区", M + 26, y + 22, 320, 21, INKD, W600))
    b.append(t("2 已确认 · 1 待确认", M + 384, y + 24, 300, 18,
               WARM, W600, align="END"))
    b.append(t("收件人", M + 26, y + 66, 160, 18, FAINT, W500))
    b.append(t("陈  越", M + 26, y + 90, 260, 38, INKD, W600))
    b.append(t("电话", M + 300, y + 66, 120, 18, FAINT, W500))
    b.append(t("138 **** 6721", M + 300, y + 90, 260, 26, INKD, W600))
    for i, ln in enumerate(hw("完整号码尾四位 8945；本面单与推送中只显示 138 **** 6721",
                               17, 380)[:2]):
        b.append(t(ln, M + 300, y + 122 + i * line_h(17), 384, 17, FAINT, W500))
    rule(b, M + 26, y + 160, lw - 52)
    asks = [("电话对吗？", "尾号 8945，请和买家再确认一次", "待确认", WARM),
            ("门牌对吗？", "珠江路 118 号 3 栋 1102 · 电话核对过", "已确认", COOL),
            ("隐藏手机号吗？", "隐私面单已开启，推送按隐藏后的号码发", "已确认", COOL)]
    for i, (q, detail, st, col) in enumerate(asks):
        yy = y + 178 + i * 70
        b.append(rect(M + 26, yy + 4, 4, 48, col, 2))
        b.append(t(q, M + 44, yy, 240, 21, INKD, W600))
        b.append(t(detail, M + 44, yy + 30, 470, 17, MUTE, W500))
        b.append(t(st, M + lw - 26 - 96, yy + 2, 96, 19, col, W600, align="END"))
    b.append(rect(M + 26, y + ph - 84, lw - 52, 66, SHADE, 8))
    b.append(t("备注", M + 44, y + ph - 72, 200, 19, INKD, W600))
    b.append(t("放前台，放不下打电话 · 不保价（货物价值 ¥0）", M + 44, y + ph - 44,
               lw - 110, 18, MUTE, W500))

    # ── 右：收件人 ──────────────────────────────────────────────────
    rx = M + lw + 24
    rw = W - M * 2 - lw - 24
    b.append(rect(rx, y, rw, ph, CARD, 12))
    b.append(rect(rx, y, rw, 4, acc, 2))
    b.append(t("收件人看到的一面", rx + 26, y + 22, 320, 21, INKD, W600))
    b.append(t("预计送达", rx + 26, y + 66, 200, 18, FAINT, W500))
    b.append(t("10-16 18:00 前", rx + 26, y + 90, rw - 52, 34, INKD, W600))
    b.append(rect(rx + 26, y + 140, rw - 52, 1, HAIR))
    rows = [("寄件人", "沈  川（示例小店）"), ("物品", "玻璃杯 × 1"),
            ("重量", "450 g"), ("保价", "未保价 · ¥0"), ("提醒", "易碎品，轻放")]
    for i, (k, v) in enumerate(rows):
        yy = y + 162 + i * 40
        b.append(t(k, rx + 26, yy, 120, 19, MUTE, W500))
        b.append(t(v, rx + 160, yy, rw - 186, 19, INKD, W600))
    b.append(rect(rx + 26, y + ph - 110, rw - 52, 92, "#EAF1FC", 8))
    b.append(t("隐私面单 · 已开启", rx + 44, y + ph - 96, rw - 88, 19, acc, W600))
    for i, ln in enumerate(hw("收件人手机号中 4 位、门牌号后 2 位已隐藏；"
                               "短信与微信推送同样按隐藏后的信息发送", 17, rw - 88)[:3]):
        b.append(t(ln, rx + 44, y + ph - 68 + i * line_h(17), rw - 88, 17, MUTE, W500))
    y += ph + 32

    y = section(b, M, y, W - M * 2, "02", "这一面折叠掉的 18 项", acc,
                "不是删掉，是收到「详情」里——发货与结算仍然需要它们")
    fx = M
    fx = pill(b, fx, y, f"已折叠 {len(FOLDED)} 项", INKD, SHADE, 18)
    y += 44
    cwid = (W - M * 2 - 5 * 10) / 6
    for i, name in enumerate(FOLDED):
        cx = M + (i % 6) * (cwid + 10)
        cy = y + (i // 6) * 36
        b.append(rect(cx, cy, cwid, 30, SHADE, 6))
        b.append(t(name, cx + 12, cy + 5, cwid - 24, 17, MUTE, W500))
    y += 36 * 3 + 14
    y = source_note(b, M, y, W - M * 2, [
        "依据：各快递公司自 2017 年起推出隐私面单，但据新华网、央广网等报道，推广四年后普及率不升反降，主要因为隐私面单多为增值服务而非默认选项；报道并称透过姓名、手机号与地址可还原大部分个人信息。",
        "数据为自拟示例：收寄件人、手机号、地址、单号、物品与时效均为演示用，非真实面单；《个人信息保护法》自 2021-11-01 起施行。",
    ])
    fy = footer(b, M, y + 26, W - M * 2,
           "自拟示例，非真实记录。隐私处理方式以承运人实际规则为准，本页不构成寄递或法律建议。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-07 · 餐厅菜单 →「按我现在的条件选」
# ════════════════════════════════════════════════════════════════════════
DISHES = [
    ("干煸四季豆", "32", "素", 12, 2, "2 人份", "花生"),
    ("番茄牛腩煲", "78", "荤", 45, 0, "2–3 人份", "—"),
    ("清蒸鲈鱼", "68", "荤", 20, 0, "2 人份", "鱼 · 贝类"),
    ("手撕包菜", "26", "素", 8, 1, "1–2 人份", "—"),
    ("蒜蓉西兰花", "28", "素", 10, 0, "2 人份", "蒜"),
    ("黑椒牛柳粒", "58", "荤", 15, 1, "2 人份", "奶"),
    ("酸汤肥牛米线", "32", "荤", 12, 3, "1 人份", "—"),
    ("桂花冰粉", "16", "素", 3, 0, "1–2 人份", "—"),
]


def c07():
    W = 1120
    acc = ACCENTS[7]
    b = []
    y = masthead(b, 7, W, "餐厅菜单（堂食单页）",
                 "菜单是从上到下的一长串，读的人却带着约束来：几个人、忌不忌口、多久要上",
                 "重设计目标：先给 4 个入口，再给每道菜标注决策维度", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "40 道菜纵向平铺 · 无分类 · 无维度标注", 26),
                  [("先选条件", "4 个入口"), ("再看菜", "辣度 · 用时 · 份量"),
                   ("最后提醒", "过敏原三字码")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "先说条件，再看菜", acc, "今日在售 8 道")
    # hero 数字：菜单原本没有任何一个"页面级"的数字，读的人要先数一遍有几道菜
    b.append(rect(M, y, 250, 116, CARD, 12))
    b.append(rect(M, y, 250, 4, acc, 2))
    b.append(t("8", M + 20, y + 24, 88, 56, INKD, W600))
    b.append(t("今日在售菜品", M + 20, y + 84, 200, 18, MUTE, W500))
    b.append(t("最快 3 分钟", M + 118, y + 22, 124, 19, acc, W600))
    b.append(t("上桌", M + 118, y + 48, 124, 18, FAINT, W500))
    entries = [("不吃辣", "辣度 0", "4 道", COOL), ("素食", "不含荤", "4 道", "#2F8A4B"),
               ("15 分钟内上", "用时 ≤ 15 分钟", "6 道", acc),
               ("两人分享", "标注 2 人份及以上", "5 道", "#6B52C7")]
    ex0 = M + 250 + 16
    ew = (W - M * 2 - 250 - 16 - 3 * 14) / 4
    for i, (name, sub, cnt, col) in enumerate(entries):
        ex = ex0 + i * (ew + 14)
        b.append(rect(ex, y, ew, 116, CARD, 12))
        b.append(rect(ex, y, ew, 4, col, 2))
        b.append(t(name, ex + 18, y + 20, ew - 36, 22, INKD, W600))
        b.append(t(sub, ex + 18, y + 50, ew - 36, 16, MUTE, W500))
        b.append(t(cnt, ex + 18, y + 76, ew - 36, 22, col, W600))
    y += 116 + 32

    y = section(b, M, y, W - M * 2, "02", "今日 8 道 · 每道标 4 个维度", acc,
                "辣度 ●○○○ · 用时为下单后上桌估计")
    cwid = (W - M * 2 - 18) / 2
    for i, (name, price, kind, mins, spice, serve, aller) in enumerate(DISHES):
        cx = M + (i % 2) * (cwid + 18)
        cy = y + (i // 2) * 132
        veg = kind == "素"
        col = "#2F8A4B" if veg else acc
        b.append(rect(cx, cy, cwid, 118, CARD, 10))
        b.append(rect(cx, cy, 4, 118, col, 2))
        b.append(t(name, cx + 22, cy + 16, cwid - 200, 22, INKD, W600))
        b.append(t(f"¥{price}", cx + cwid - 22 - 100, cy + 12, 100, 26, col, W600,
                   align="END"))
        b.append(t(kind, cx + 22, cy + 50, 60, 18, col, W600))
        b.append(t("辣度", cx + 92, cy + 51, 70, 17, FAINT, W500))
        dot_scale(b, cx + 156, cy + 60, 3, spice, "#C0502F")
        b.append(t(f"{mins} 分钟", cx + 268, cy + 50, 110, 18, MUTE, W500))
        b.append(t(serve, cx + 380, cy + 50, 110, 18, MUTE, W500))
        b.append(t(f"过敏原 {aller}", cx + 22, cy + 80, cwid - 44, 17, FAINT, W500))
    y += 132 * 4 + 10
    y = source_note(b, M, y, W - M * 2, [
        "数据为自拟示例：菜名、价格、用时、份量与过敏原均为演示用，非任何真实菜单；入口计数与 8 道菜的辣度、用时、份量字段在本轮用脚本逐条核对一致。",
        "重设计只改变信息的组织方式（先条件后菜品），不改动任何一道菜的名称、价格或配料。",
    ])
    fy = footer(b, M, y + 26, W - M * 2,
           "自拟示例，非真实记录。实际点单请以门店菜单与当厨供应为准，本页不构成饮食建议。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-08 · 药品说明书 →「现在能不能吃这一片」
# ════════════════════════════════════════════════════════════════════════
def c08():
    W = 1040
    acc = ACCENTS[8]
    b = []
    y = masthead(b, 8, W, "药品说明书 / 药盒侧面",
                 "说明书按法定章节排，患者要找的是「我现在能不能吃、吃几片、和别的药冲不冲」",
                 "重设计目标：把三个问题放到第一屏，并给出今天的服药时刻", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "23 个法定章节 · 术语密集 · 动作埋在末段", 23),
                  [("第一屏", "三个问题"), ("第二屏", "今天的服药时刻表"),
                   ("末屏", "三条必读警示")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "现在能不能吃这一片", acc,
                "示例通用名：对乙酰氨基酚缓释片 0.3 g × 12 片")
    y = kicker(b, M, y, W - M * 2,
               "可以。现在是 09:36，距 08:12 那次已过 10 小时 24 分，"
               "满足「间隔 ≥ 6 小时」；但这一片要等到 20:00 那次再吃。", acc, bg=CARD)
    y += 24
    qs = [("①", "现在能吃吗", "可以", "距上次 10 h 24 m · 要求 ≥ 6 h", COOL),
          ("②", "一次几片", "1 片", "0.3 g · 24 h 内不超过 4 片", acc),
          ("③", "和别的药冲吗", "先看成分", "复方感冒药常含相同成分", WARM)]
    qw = (W - M * 2 - 2 * 14) / 3
    for i, (no, q, ans, note, col) in enumerate(qs):
        qx = M + i * (qw + 14)
        b.append(rect(qx, y, qw, 154, CARD, 12))
        b.append(rect(qx, y, qw, 4, col, 2))
        b.append(t(no, qx + 20, y + 18, 40, 26, col, W600))
        b.append(t(q, qx + 64, y + 22, qw - 84, 22, MUTE, W600))
        b.append(t(ans, qx + 20, y + 58, qw - 40, 44, INKD, W600))
        b.append(t(note, qx + 20, y + 112, qw - 40, 17, MUTE, W500))
    y += 154 + 32

    y = section(b, M, y, W - M * 2, "02", "今天的服药时刻表", acc,
                "处方：每次 1 片，每 12 小时 1 次")
    th = 200
    b.append(rect(M, y, W - M * 2, th, CARD, 12))
    tx0, tx1 = M + 80, M + (W - M * 2) - 240
    span = tx1 - tx0

    def hx(hr: float) -> float:
        return tx0 + (hr - 6.0) / 18.0 * span

    ay = y + 100
    b.append(rect(tx0, ay, span, 2, "#D8D2C6"))
    for hh in range(6, 25, 2):
        xx = hx(float(hh))
        b.append(rect(xx, ay - 6, 1, 14, "#D8D2C6"))
        b.append(t(f"{hh:02d}:00", xx - 36, ay + 16, 72, 17, FAINT, W500, align="CENTER"))
    # 首版把服药标记按 26 小时跨度定位、刻度按 18 小时定位，两套比例尺，
    # 图上「已服 08:12」落在 08:00 刻度左边一点而对不上数——现在统一用 hx()。
    for hr, lab, col in [(8.2, "已服 08:12", COOL), (20.0, "待服 20:00", acc)]:
        xx = hx(hr)
        b.append(rect(xx - 2, y + 48, 4, 54, col, 2))
        b.append(circle(xx, y + 44, 13, col))
        b.append(t(lab, xx - 90, y + 18, 180, 19, col, W600, align="CENTER"))
    b.append(rect(tx1 + 6, y + 40, 3, 62, "#B6BECD", 2))
    b.append(t("次日 08:00", tx1 + 20, y + 26, 180, 18, MUTE, W500))
    b.append(t("下一轮第 1 次", tx1 + 20, y + 52, 180, 17, FAINT, W500))
    b.append(t("每次 1 片 · 两次间隔 12 h · 24 h 内不超过 4 片", M + 26, y + 148,
               W - M * 2 - 52, 19, MUTE, W500))
    y += th + 32

    y = section(b, M, y, W - M * 2, "03", "三条必须先看一眼的警示", acc,
                "原说明书里它们散在「禁忌」「注意事项」「不良反应」三节")
    warns = ["肝功能不全者禁用", "服药期间不得饮酒", "连用 3 天症状未缓解应就医"]
    for i, s in enumerate(warns):
        yy = y + i * 54
        b.append(rect(M, yy, W - M * 2, 46, "#FDF0EE", 8))
        b.append(rect(M, yy, 4, 46, WARM, 2))
        b.append(t(f"0{i + 1}", M + 20, yy + 11, 46, 20, WARM, W600))
        b.append(t(s, M + 74, yy + 11, W - M * 2 - 100, 21, INKD, W600))
    y += 54 * 3 + 16
    y = y = source_note(b, M, y, W - M * 2, [
        "依据：国家药监局 2023 年 10 月《药品说明书适老化及无障碍改革试点工作方案》提出说明书（简化版）（大字版）与电子版试点；中国药学会《中国家庭药箱调查》相关报道指出「不良反应」「药物相互作用」「禁忌」等栏目因术语密集成为最主要的阅读障碍。",
        "本图是信息结构的重排示例，不是任何真实药品说明书：通用名、规格、用法、时刻与警示均为演示用，不构成用药建议；实际用药请遵医嘱并以说明书为准。",
    ])
    fy = footer(b, M, y + 26, W - M * 2, "自拟示例，非真实记录。请遵医嘱用药。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-09 · 预包装食品营养标签 →「前三行才是你真正买的」
# ════════════════════════════════════════════════════════════════════════
NRV_TABLE = [("能量", "1980", "kJ"), ("蛋白质", "8.2", "g"), ("脂肪", "18.2", "g"),
             ("饱和脂肪", "7.4", "g"), ("碳水化合物", "68.6", "g"), ("糖", "24.6", "g"),
             ("钠", "480", "mg")]


def c09():
    W = 1000
    acc = ACCENTS[9]
    b = []
    y = masthead(b, 9, W, "预包装食品包装（正标 + 标签）",
                 "配料表按递减顺序排，但字号最小；消费者真正会看的是前三味和盐油糖",
                 "重设计目标：法定标示一字不动，另加一层「标准允许的补充说明」", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "一张 3 列小表 + 一行配料，字号最小、位置最边", 12),
                  [("法定区", "1+6 原样保留"), ("决策区", "前三位配料大字"),
                   ("对照区", "盐 / 油 / 糖 每包换算")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "前三位配料", acc, "示例产品：海盐苏打饼干 68 g / 包")
    top3 = ["小麦粉", "白砂糖", "植物油"]
    tw3 = (W - M * 2 - 2 * 14) / 3
    for i, ing in enumerate(top3):
        ix = M + i * (tw3 + 14)
        b.append(rect(ix, y, tw3, 132, CARD, 12))
        b.append(rect(ix, y, tw3, 4, acc, 2))
        b.append(t(f"第 {i + 1} 位", ix + 20, y + 20, tw3 - 40, 18, FAINT, W500))
        b.append(t(ing, ix + 20, y + 48, tw3 - 40, 42, INKD, W600))
        b.append(t(["占配料表首位", "甜味来源", "脂肪来源"][i], ix + 20, y + 98,
                   tw3 - 40, 18, MUTE, W500))
    y += 132 + 30

    y = section(b, M, y, W - M * 2, "02", "法定标示区：1 + 6（原样保留）", acc,
                "每 100 g · NRV% 一列留空，理由见下方来源说明")
    rows = ["项目", "每 100 g", "NRV%"]
    cols_x = [M + 20, M + 380, M + 600]
    cols_w = [340, 200, 220]
    b.append(rect(M, y, W - M * 2, 40, SHADE, 6))
    for i, name in enumerate(rows):
        al = "END" if i == 2 else None
        b.append(t(name, cols_x[i], y + 10, cols_w[i], 18, MUTE, W600, al))
    y += 40
    for name, val, unit in NRV_TABLE:
        b.append(rect(M, y, W - M * 2, 44, CARD, 4))
        b.append(t(name, cols_x[0], y + 12, cols_w[0], 20, INKD, W600))
        b.append(t(val, cols_x[1], y + 12, cols_w[1], 20, INKD, W600))
        b.append(t(unit, cols_x[1] + 84, y + 14, 90, 18, FAINT, W500))
        b.append(t("—", cols_x[2], y + 12, cols_w[2], 20, FAINT, W500, align="END"))
        y += 48
    b.append(rect(M, y, W - M * 2, 44, "#FBEFE9", 6))
    b.append(t("标准要求在表下方标示提示语：儿童青少年应避免摄入过量盐油糖",
               M + 18, y + 12, W - M * 2 - 36, 18, WARM, W600))
    y += 60

    y = section(b, M, y, W - M * 2, "03", "每包（68 g）换算后是什么", acc,
                "把「每 100 g」翻成手里这一包")
    packs = [("能量", "1346 kJ", "每包 68 g 折算", MUTE, None),
             ("盐", "0.82 g", "= 钠 326 mg × 2.5", acc, 0.164),
             ("糖", "16.7 g", "其中添加糖 8.2 g", WARM, 0.334),
             ("饱和脂肪", "5.03 g", "占本包能量 13.8%", WARM, 0.138)]
    pw = (W - M * 2 - 3 * 12) / 4
    for i, (name, val, note, col, ratio) in enumerate(packs):
        px = M + i * (pw + 12)
        b.append(rect(px, y, pw, 150, CARD, 12))
        b.append(rect(px, y, pw, 4, col, 2))
        b.append(t(name, px + 18, y + 18, pw - 36, 19, MUTE, W600))
        b.append(t(val, px + 18, y + 46, pw - 36, 34, INKD, W600))
        b.append(t(note, px + 18, y + 86, pw - 36, 17, FAINT, W500))
        if ratio is not None:
            b.append(rect(px + 18, y + 116, pw - 36, 10, SHADE, 5))
            b.append(rect(px + 18, y + 116, max(5.0, (pw - 36) * ratio), 10, col, 5))
            b.append(t(f"占每日参考 {ratio * 100:.1f}%", px + 18, y + 130, pw - 36, 15,
                       FAINT, W500))
        else:
            b.append(t("— 无单一上限基准", px + 18, y + 114, pw - 36, 15, FAINT, W500))
    y += 150 + 24
    facts = ["盐 0.82 g = 成人每日 5 g 食盐的 16.4%",
             "添加糖 8.2 g = 「每天 ≤ 50 g」的 16.3%",
             "饱和脂肪占本包能量 13.8%，高于「应 < 10%」",
             "钠 480 mg/100 g：高于低钠门槛 120 mg，低于高钠门槛 600 mg"]
    for i, s in enumerate(facts):
        yy = y + i * 32
        b.append(t("·", M, yy, 20, 18, acc, W600))
        b.append(t(s, M + 20, yy, W - M * 2 - 20, 18, MUTE, W500))
    y += 32 * 4 + 20
    y = source_note(b, M, y, W - M * 2, [
        "依据：GB 28050—2025 将强制标示由「1+4」扩为「1+6」（能量 + 蛋白质、脂肪、饱和脂肪、碳水化合物、糖、钠），并要求标示「儿童青少年应避免摄入过量盐油糖」；标准同时允许在规范标示营养成分表之后用图形、文字作补充说明（如以「盐」代「钠」、以「油」代「脂肪」）。",
        "对照值：盐 = 钠 × 2.5；《中国居民膳食指南（2022）》成人食盐 ≤5 g/天、添加糖 ≤50 g/天、饱和脂肪应 < 总能量的 10%；低钠门槛 ≤120 mg/100 g（GB 28050），高钠 >600 mg/100 g（中国营养学会）。能量按 GB 28050 系数核算：8.2×17 + 18.2×37 + 68.6×17 = 1979 ≈ 1980 kJ。",
        "NRV% 一列留空：2025 版已按 2023 版《中国居民膳食营养素参考摄入量》更新部分 NRV，本轮未逐项核实具体数值，故不臆造。数据整体为自拟示例，非真实产品。",
    ])
    fy = footer(b, M, y + 20, W - M * 2,
                "自拟示例，非真实产品标签。营养与健康问题请以产品实际标签和《中国居民膳食指南》为准。")
    return finish(b, W, fy, PAPER, tail=56)


# ════════════════════════════════════════════════════════════════════════
# case-10 · 家用电器说明书 →「按你要做的事重排」
# ════════════════════════════════════════════════════════════════════════
TASKS = [("更换滤芯", "约 2 分钟", "打开右侧仓门 → 抽出旧芯 → 装入新芯", "型号 KF-320B"),
         ("每周擦拭出风口", "约 3 分钟", "关机 → 微湿布单向擦拭 → 静置 30 秒", "断电后再擦"),
         ("清洁复合滤芯", "约 6 分钟", "清水冲洗 → 阴干 12 小时 → 装回", "不可用洗洁精"),
         ("更换灯珠模块", "约 10 分钟", "断电 → 拆下顶盖 → 拔插模块", "只在 02:00–06:00 通电"),
         ("重置运行计时", "约 30 秒", "长按机身键 5 秒 → 听到提示音", "换滤芯后无需手动"),
         ("处理「滤芯已用完」", "约 1 分钟", "取出旧芯 → 装新芯 → 自动归零", "报警会自动复位")]
CYCLES = [("复合滤芯清洗", "每 30 天", 41, 30, WARM), ("出风口擦拭", "每 7 天", 12, 7, WARM),
          ("机身除尘", "每 90 天", 34, 90, COOL),
          ("滤芯更换", "每 7200 小时", 5112, 7200, ACCENTS[10])]


def c10():
    W = 1440
    acc = ACCENTS[10]
    b = []
    y = masthead(b, 10, W, "家用电器说明书（空气净化器）",
                 "说明书按功能章节写，使用者按任务找：换滤芯、除垢、清洁各在哪一章",
                 "重设计目标：把说明书首页改成「你现在能做的 6 件事」", acc)
    y = structbar(b, M, y, W - M * 2, acc,
                  ("原结构", "9 章 34 节 · 按功能组织 · 任务要自己找", 26),
                  [("首页", "6 张任务卡"), ("状态", "滤芯寿命进度"),
                   ("周期", "保养日历")], h=146)
    y += 28
    y = section(b, M, y, W - M * 2, "01", "你现在能做的 6 件事", acc,
                "示例机型 K-320 · 每张卡只写一个动作")
    cwd = (W - M * 2 - 2 * 16) / 3
    for i, (name, dur, steps, warn) in enumerate(TASKS):
        cx = M + (i % 3) * (cwd + 16)
        cy = y + (i // 3) * 172
        b.append(rect(cx, cy, cwd, 156, CARD, 12))
        b.append(rect(cx, cy, cwd, 4, acc, 2))
        b.append(rect(cx + 22, cy + 22, 34, 34, acc, 8))
        b.append(t(str(i + 1), cx + 22, cy + 30, 34, 22, "#FFFFFF", W600, align="CENTER"))
        b.append(t(name, cx + 68, cy + 26, cwd - 200, 23, INKD, W600))
        b.append(t(dur, cx + cwd - 22 - 100, cy + 28, 100, 19, acc, W600, align="END"))
        for j, ln in enumerate(wrap(steps, 18, cwd - 44)[:2]):
            b.append(t(ln, cx + 22, cy + 74 + j * 28, cwd - 44, 18, MUTE, W500))
        b.append(rect(cx + 22, cy + 120, cwd - 44, 26, SHADE, 6))
        b.append(t(warn, cx + 34, cy + 124, cwd - 68, 17, MUTE, W500))
    y += 172 * 2 + 22

    y = section(b, M, y, W - M * 2, "02", "这三个数字说明它还好用", acc,
                "累计运行时长 5,112 h · 上次清洁 41 天前")
    stw = (W - M * 2 - 2 * 16) / 3
    states = [("滤芯已用", "71.0%", "5,112 / 7,200 小时", WARM),
              ("滤芯剩余", "2,088 h", "按 24 h/天计约 87 天", acc),
              ("距上次清洁", "41 天", "建议周期 30 天 · 已超 11 天", WARM)]
    for i, (lab, val, sub, col) in enumerate(states):
        sx = M + i * (stw + 16)
        b.append(rect(sx, y, stw, 128, CARD, 12))
        b.append(rect(sx, y, stw, 4, col, 2))
        b.append(t(lab, sx + 20, y + 18, stw - 40, 19, MUTE, W600))
        b.append(t(val, sx + 20, y + 46, stw - 40, 38, INKD, W600))
        b.append(t(sub, sx + 20, y + 92, stw - 40, 18, MUTE, W500))
    y += 128 + 30
    b.append(rect(M, y, W - M * 2, 34, SHADE, 8))
    b.append(rect(M + 4, y + 4, (W - M * 2 - 8) * 0.710, 26, acc, 6))
    b.append(t("滤芯寿命 0%", M + 14, y + 7, 160, 18, "#FFFFFF", W600))
    b.append(t("71.0%", M + (W - M * 2 - 8) * 0.710 - 70, y + 7, 70, 18, "#FFFFFF",
               W600, align="END"))
    b.append(t("100% = 7,200 小时", M + W - M * 2 - 190, y + 7, 180, 18, MUTE, W500,
               align="END"))
    y += 34 + 30

    y = section(b, M, y, W - M * 2, "03", "保养周期日历", acc, "超期项直接点名")
    for name, cyc, used, total, col in CYCLES:
        ratio = used / total
        over = ratio >= 1.0
        b.append(t(name, M, y + 4, 190, 20, INKD, W600))
        b.append(t(cyc, M + 196, y + 5, 150, 18, MUTE, W500))
        bx, bw = M + 360, W - M * 2 - 360 - 240 - 140
        b.append(rect(bx, y + 8, bw, 14, SHADE, 7))
        b.append(rect(bx, y + 8, max(6.0, bw * min(1.0, ratio)), 14, col, 7))
        b.append(t(f"已用 {used} / {total}", bx + bw + 18, y + 3, 220, 19, MUTE, W500))
        b.append(t("超期 11 天" if over else ("剩余正常" if ratio < 0.9 else "接近周期"),
                   M + W - M * 2 - 140, y + 3, 140, 19, col, W600, align="END"))
        y += 40
    y += 14
    y = source_note(b, M, y, W - M * 2, [
        "数据为自拟示例：机型、滤芯型号、运行时长、保养周期与任务步骤均为演示用，非任何真实产品说明书。",
        "重设计只改变说明书首页的组织方式（从「按功能分章」改为「按任务分卡」），任务步骤本身与原说明书一致，不新增操作。",
    ])
    fy = footer(b, M, y + 26, W - M * 2,
           "自拟示例，非真实记录。实际维护请以产品说明书与专业售后为准，断电后再操作。")
    return finish(b, W, fy, PAPER, tail=56)


CASES = {1: c01, 2: c02, 3: c03, 4: c04, 5: c05,
         6: c06, 7: c07, 8: c08, 9: c09, 10: c10}


def main():
    sel = sys.argv[1] if len(sys.argv) > 1 else "all"
    ver = sys.argv[2] if len(sys.argv) > 2 else "v1"
    out = ROOT / "tmp/run-20261011-01/B06/drafts"
    out.mkdir(parents=True, exist_ok=True)
    todo = sorted(CASES) if sel == "all" else [int(x) for x in sel.split(",")]
    for n in todo:
        tighten_reset()
        dsl = CASES[n]()
        p = out / f"b06-{n:02d}-{ver}.snapshot"
        p.write_text(dsl, encoding="utf-8")
        print(f"[{n:02d}] -> {p.name}  {len(dsl):,} chars")
        for ratio, where, spec in tighten_report(5):
            print(f"      余量 {ratio:.2f}  {spec}  {where}")


if __name__ == "__main__":
    main()