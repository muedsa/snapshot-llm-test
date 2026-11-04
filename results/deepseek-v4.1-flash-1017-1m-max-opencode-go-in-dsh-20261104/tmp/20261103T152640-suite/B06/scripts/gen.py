# -*- coding: utf-8 -*-
"""B06: ten everyday information problems, redesigned."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B06"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

PAPER, INK, DIM, RULE = "#FBFAF6", "#161616", "#6B7280", "#DAD5C8"
ACC, RED, GREEN = "#C8452D", "#B3352E", "#1F7A4D"

def R(x, y, w, h, c, r=0, b=None):
    return K.rect(x, y, w, h, color=c, radius=r, border=b)

def T(x, y, s, w, size, c=INK, bold=False, align=None, label=None):
    return K.text(x, y, s, width=w, size=size, color=c, bold=bold, align=align, label=label)

def head(kicker, title, sub, W, accent=ACC):
    p = [R(0, 0, W, 8, accent)]
    p.append(T(64, 44, kicker, 700, 20, accent, True))
    p.append(T(64, 76, title, W - 128, 40, INK, True))
    if sub:
        p.append(T(64, 132, sub, W - 128, 20, DIM))
    p.append(R(64, 172, W - 128, 2, INK))
    return p

# 1 electricity bill
def c1():
    W, H = 1200, 1600
    p = head("问题 01 · 电费单看不懂", "这个月为什么比上个月贵 80 元", "阶梯电价 + 峰谷时段的拆解（示例数据）", W)
    p.append(T(64, 210, "总电费 268.40 元 · 用电 412 度", 900, 26, INK))
    tiers = [("第一档 0–180 度", 180, "0.52 元/度", 93.6, GREEN),
             ("第二档 181–300 度", 120, "0.57 元/度", 68.4, "#B26A00"),
             ("第三档 300 度以上", 112, "0.82 元/度", 91.8, RED)]
    for i, (name, deg, price, cost, col) in enumerate(tiers):
        y = 280 + i * 150
        p.append(R(64, y, W - 128, 130, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        p.append(R(64, y, 8, 130, col, 4))
        p.append(T(92, y + 20, name, 420, 22, INK, True))
        p.append(T(92, y + 56, f"{deg} 度 × {price}", 420, 19, DIM))
        p.append(T(760, y + 34, f"{cost:.1f} 元", 340, 34, col, True, "RIGHT"))
    p.append(R(64, 760, W - 128, 2, RULE))
    p.append(T(64, 790, "和上个月差在哪", 600, 24, INK, True))
    delta = [("多用了 46 度", "+24.0 元", "天气变冷，空调制热"),
             ("其中 32 度落在第三档", "+26.2 元", "跨档后单价从 0.57 涨到 0.82"),
             ("峰时段占比上升 6%", "+29.8 元", "19:00–21:00 用电集中")]
    for i, (what, money, why) in enumerate(delta):
        y = 836 + i * 110
        p.append(T(64, y, what, 380, 21, INK, True))
        p.append(T(470, y, money, 180, 21, RED, True))
        p.append(T(680, y, why, 460, 19, DIM))
        p.append(R(64, y + 72, W - 128, 1, RULE))
    p.append(T(64, 1200, "想省电，先看第三档的 112 度用在哪里。", 900, 22, INK, True))
    p.append(T(64, 1240, "把 19:00–21:00 的洗衣与热水器挪到 22:00 之后，按示例峰谷价差每月约省 26 元。", 1000, 19, DIM))
    p.append(T(64, 1300, "说明：电价与用量均为示例，不对应任何真实账单。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 2 train platform
def c2():
    W, H = 1600, 900
    p = head("问题 02 · 站台上不知道往哪走", "车厢位置图：你的 08 号车厢在第 3 个门", "G1234 · 16 节编组 · 站台 7（示例）", W)
    p.append(R(80, 240, 1440, 240, "#E8E4D8", 8))
    for i in range(16):
        x = 96 + i * 88
        col = ACC if (i + 1) == 8 else "#FFFFFF"
        p.append(R(x, 290, 76, 140, col, 6, f"1 SOLID {'#C8452D' if (i+1)==8 else '#B8B2A2'}"))
        p.append(T(x, 336, f"{i+1:02d}", 76, 30, "#FFFFFF" if (i + 1) == 8 else INK, True, "CENTER"))
        p.append(T(x, 380, "车", 76, 16, "#FFFFFF" if (i + 1) == 8 else DIM, align="CENTER"))
    p.append(T(80, 500, "检票口 A", 200, 18, DIM))
    p.append(R(80, 528, 60, 6, ACC))
    p.append(T(80, 552, "从 A 口下站台后右转 40 米", 500, 20, INK))
    p.append(T(760, 552, "08 号车厢位于站台中段，靠近检票口 A", 700, 20, DIM))
    p.append(R(80, 620, W - 160, 2, RULE))
    steps = [("1", "看站台屏确认 7 站台", "发车前 20 分钟"),
             ("2", "从 A 口下站台", "不要走 B 口，会多走 120 米"),
             ("3", "沿黄线向中段走", "地面有车厢号地贴"),
             ("4", "08 号车厢 3 号门", "上车后往左是 12–16 排")]
    for i, (n, what, note) in enumerate(steps):
        x = 80 + i * 370
        p.append(T(x, 660, n, 60, 34, ACC, True))
        p.append(T(x, 706, what, 330, 21, INK, True))
        p.append(T(x, 740, note, 330, 18, DIM))
    p.append(T(80, 830, "说明：编组、站台与时间均为示例；实际以当日站台屏为准。", 1000, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 3 nutrition label
def c3():
    W, H = 1080, 1350
    p = head("问题 03 · 营养成分表看不懂", "这碗面的钠，占了你一天的一半", "把「每 100 克」换算成「这一份」与「每日占比」", W)
    rows = [("钠", "2 140 mg", 107, "每日上限 2 000 mg", RED),
            ("脂肪", "18.6 g", 31, "每日参考 60 g", "#B26A00"),
            ("糖", "9.4 g", 19, "每日上限 50 g", "#B26A00"),
            ("蛋白质", "12.1 g", 24, "每日参考 50 g", GREEN)]
    for i, (name, amt, pct, base, col) in enumerate(rows):
        y = 220 + i * 170
        p.append(T(64, y, name, 200, 26, INK, True))
        p.append(T(240, y + 2, amt, 300, 24, INK))
        p.append(T(560, y + 4, f"{pct}%", 160, 30, col, True, "RIGHT"))
        p.append(R(64, y + 56, 952, 22, "#EDE9DE", 11))
        p.append(R(64, y + 56, int(952 * min(pct, 100) / 100), 22, col, 11))
        p.append(T(64, y + 88, base, 600, 17, DIM))
    p.append(R(64, 940, 952, 2, RULE))
    p.append(T(64, 966, "为什么换算很重要", 600, 22, INK, True))
    p.append(T(64, 1004, "包装标的是「每 100 克」，而这一碗是 105 克。", 950, 20, INK))
    p.append(T(64, 1038, "直接看每 100 克，会把钠低估 5%。", 950, 20, INK))
    p.append(T(64, 1090, "一餐吃掉 107% 的钠上限，意味着当天其余两餐要非常清淡。", 950, 19, DIM))
    p.append(T(64, 1220, "说明：数值为示例配方，每日参考值采用常见成人标准。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 4 rental contract
def c4():
    W, H = 1200, 1600
    p = head("问题 04 · 合同太长不敢签", "六条真正会影响你的条款", "把 12 页合同压成一页，按风险排序（示例）", W)
    rows = [("押金退还", "退租后 7 个工作日内退还，逾期按日 0.05% 计息", "有利", GREEN),
            ("维修责任", "非人为损坏由房东承担；24 小时内未修可自行维修并抵扣", "有利", GREEN),
            ("提前解约", "需提前 30 天书面通知，并支付 1 个月租金违约金", "注意", "#B26A00"),
            ("租金调整", "租期内不调整；续租涨幅不超过 5%", "有利", GREEN),
            ("转租", "未经书面同意不得转租，否则视为违约", "注意", "#B26A00"),
            ("设施清单", "附件二列 14 项，交房时逐项拍照留底", "必做", RED)]
    for i, (name, text, risk, col) in enumerate(rows):
        y = 210 + i * 190
        p.append(R(64, y, W - 128, 170, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        p.append(R(64, y, 8, 170, col, 4))
        p.append(T(92, y + 18, name, 300, 24, INK, True))
        p.append(T(92, y + 58, text, 700, 20, "#3A3A3A"))
        p.append(R(864, y + 18, 96, 34, col, 17))
        p.append(T(864, y + 25, risk, 96, 16, "#FFFFFF", True, "CENTER"))
    p.append(T(64, 1380, "读法：先看红标「必做」，再看两个「注意」，其余可以快读。", 1000, 20, INK, True))
    p.append(T(64, 1420, "说明：条款文本为示例，不构成法律意见。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 5 hospital route
def c5():
    W, H = 1400, 1000
    p = head("问题 05 · 挂号单不知道下一步去哪", "从进楼到看完，一共 5 个点", "门诊 3 层 · 预计 78 分钟（示例）", W)
    steps = [("1", "一层 大厅", "取号 / 建档", "自助机 A 区", 0, 8),
             ("2", "三层 分诊台", "测血压、扫码报到", "电梯到 3 层左转", 8, 20),
             ("3", "三层 12 诊室", "候诊叫号", "屏幕显示姓名后进入", 20, 45),
             ("4", "二层 检验科", "抽血、缴费", "电梯到 2 层，先缴费再抽血", 45, 65),
             ("5", "一层 药房", "取药、离院", "凭处方条码取药", 65, 78)]
    p.append(R(80, 220, 1240, 120, "#FFFFFF", 10, f"1 SOLID {RULE}"))
    for i, (n, place, what, note, t0, t1) in enumerate(steps):
        x = 100 + i * 244
        p.append(R(x, 244, 44, 44, ACC, 22))
        p.append(T(x, 252, n, 44, 22, "#FFFFFF", True, "CENTER"))
        p.append(T(x + 56, 250, place, 180, 20, INK, True))
        p.append(T(x + 56, 282, f"{t0}–{t1} 分", 160, 17, DIM))
    p.append(R(80, 380, W - 160, 2, RULE))
    for i, (n, place, what, note, t0, t1) in enumerate(steps):
        y = 410 + i * 100
        p.append(T(80, y, what, 420, 24, INK, True))
        p.append(T(80, y + 34, note, 520, 19, DIM))
        p.append(T(700, y + 6, place, 320, 20, DIM))
        p.append(T(1080, y + 6, f"{t1 - t0} 分钟", 200, 20, ACC, True, "RIGHT"))
    p.append(T(80, 930, "最容易走错：抽血在 2 层，但缴费在 3 层自助机也能做。", 1100, 19, INK))
    p.append(T(80, 962, "说明：楼层与时间为示例，不代表任何具体医院。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 6 parcel timeline
def c6():
    W, H = 1080, 1350
    p = head("问题 06 · 物流信息看不出还要多久", "包裹现在到哪了，还需要几天", "把 9 条流水压成 4 个阶段（示例）", W)
    stages = [("已揽收", "10-16 14:20", "杭州仓", "完成", GREEN),
              ("运输中", "10-17 08:05", "杭州 → 上海", "完成", GREEN),
              ("派送中", "10-18 09:12", "上海杨浦 · 王师傅", "进行中", ACC),
              ("已签收", "预计 10-18 18:00", "—", "待完成", DIM)]
    for i, (name, when, where, state, col) in enumerate(stages):
        y = 220 + i * 190
        p.append(R(64, y, 952, 160, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        p.append(R(64, y, 8, 160, col, 4))
        p.append(T(92, y + 20, name, 300, 26, INK, True))
        p.append(T(92, y + 60, when, 300, 19, DIM))
        p.append(T(92, y + 92, where, 500, 19, "#3A3A3A"))
        p.append(R(800, y + 18, 180, 34, col, 17))
        p.append(T(800, y + 25, state, 180, 16, "#FFFFFF", True, "CENTER"))
    p.append(R(64, 1000, 952, 2, RULE))
    p.append(T(64, 1026, "如果今天没收到", 600, 22, INK, True))
    p.append(T(64, 1062, "18:00 后仍未签收，可在 19:00 前申请改约次日。", 940, 20, INK))
    p.append(T(64, 1096, "同一单最多改约两次，第二次起收 2 元。", 940, 19, DIM))
    p.append(T(64, 1180, "说明：物流数据为示例，用于说明阶段化表达。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 7 waste sorting
def c7():
    W = H = 1080
    p = head("问题 07 · 站在桶前不知道扔哪", "三个问题，决定它进哪个桶", "把 64 类细则压成一条判断路径", W)
    qs = [("Q1", "它含有食物或厨余吗？", "是 → 湿垃圾（沥干后投放）", GREEN),
          ("Q2", "它能被回收再利用吗？", "是 → 可回收物（清空、压扁）", "#1D4ED8"),
          ("Q3", "它含药、电池、灯管吗？", "是 → 有害垃圾（单独密封）", RED)]
    for i, (q, text, ans, col) in enumerate(qs):
        y = 220 + i * 180
        p.append(R(64, y, 952, 150, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        p.append(R(64, y, 8, 150, col, 4))
        p.append(T(92, y + 16, q, 80, 22, col, True))
        p.append(T(92, y + 52, text, 500, 22, INK, True))
        p.append(T(92, y + 92, ans, 700, 19, DIM))
    p.append(R(64, 780, 952, 120, "#FFFFFF", 10, f"1 SOLID {RULE}"))
    p.append(T(92, 800, "以上都不是 → 干垃圾", 500, 24, INK, True))
    p.append(T(92, 840, "例如：陶瓷碎片、用过的纸巾、大骨头", 600, 19, DIM))
    p.append(T(64, 960, "不确定的时候，宁可扔干垃圾——湿垃圾里混入塑料会让整桶报废。", 950, 19, INK))
    p.append(T(64, 1010, "说明：分类口径以本地规定为准，此处为常见四分类的示例。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 8 laundry symbols
def c8():
    W, H = 1080, 1350
    p = head("问题 08 · 衣服上的符号看不懂", "五个符号，决定怎么洗", "把洗标翻译成一句话", W)
    items = [("水盆 + 40", "最高 40℃ 机洗", "常规程序，可脱水", "#1D4ED8"),
             ("三角", "可以漂白", "仅氧漂，不可氯漂", "#B26A00"),
             ("方块 + 圆", "可烘干", "低温烘干，取出即挂", "#1F7A4D"),
             ("熨斗 + 两点", "中温熨烫", "≤150℃，垫布", "#B26A00"),
             ("圆 + P", "可干洗", "石油溶剂干洗", "#6B7280")]
    for i, (sym, mean, note, col) in enumerate(items):
        y = 220 + i * 170
        p.append(R(64, y, 160, 150, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        p.append(T(64, y + 46, sym, 160, 22, col, True, "CENTER"))
        p.append(T(260, y + 24, mean, 500, 26, INK, True))
        p.append(T(260, y + 70, note, 600, 19, DIM))
    p.append(T(64, 1110, "洗标是上限，不是建议：能 40℃ 不代表必须 40℃。", 950, 20, INK))
    p.append(T(64, 1160, "说明：符号含义依照常见国际洗标，具体以衣物附标为准。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 9 parking sign
def c9():
    W, H = 900, 1200
    p = head("问题 09 · 这块牌子到底能不能停", "同一段路，三个时段三种规则", "把四行小字拆成时间轴（示例）", W)
    rows = [("07:00–09:00", "禁止停车", "早高峰", RED),
            ("09:00–17:00", "限停 2 小时", "收费 5 元/小时", "#B26A00"),
            ("17:00–19:00", "禁止停车", "晚高峰", RED),
            ("19:00–次日 07:00", "可停", "免费", GREEN)]
    for i, (t, rule, note, col) in enumerate(rows):
        y = 220 + i * 170
        p.append(R(64, y, 772, 150, "#FFFFFF", 10, f"1 SOLID {RULE}"))
        p.append(R(64, y, 10, 150, col, 5))
        p.append(T(96, y + 20, t, 400, 22, INK, True))
        p.append(T(96, y + 62, rule, 400, 30, col, True))
        p.append(T(96, y + 108, note, 400, 18, DIM))
    p.append(T(64, 940, "现在能不能停？先看手机时间落在哪一段。", 700, 20, INK, True))
    p.append(T(64, 990, "停在 16:50 最亏：两小时后正好撞上 17:00 的禁停。", 700, 19, DIM))
    p.append(T(64, 1060, "说明：时段与费率均为示例，实际以现场标志为准。", 700, 17, DIM))
    return K.document(W, H, p, background=PAPER)

# 10 health check report
def c10():
    W, H = 1080, 1500
    p = head("问题 10 · 体检报告全是箭头", "6 项关键指标里，只有 2 项要行动", "按「需要行动 / 观察 / 正常」重排；其余 6 项已折叠（示例）", W)
    groups = [("需要行动", RED, [("低密度脂蛋白", "4.2 mmol/L", "上限 3.4"),
                               ("空腹血糖", "6.4 mmol/L", "上限 6.1")]),
              ("继续观察", "#B26A00", [("尿酸", "428 μmol/L", "上限 420"),
                                     ("谷丙转氨酶", "48 U/L", "上限 40")]),
              ("正常范围", GREEN, [("血红蛋白", "132 g/L", "110–150"),
                                 ("总胆固醇", "4.6 mmol/L", "上限 5.2")])]
    y = 210
    for name, col, items in groups:
        p.append(R(64, y, 952, 44, col, 8))
        p.append(T(84, y + 8, name, 300, 20, "#FFFFFF", True))
        y += 56
        for label, val, ref in items:
            p.append(R(64, y, 952, 74, "#FFFFFF", 8, f"1 SOLID {RULE}"))
            p.append(T(88, y + 12, label, 300, 20, INK, True))
            p.append(T(88, y + 42, f"参考 {ref}", 300, 16, DIM))
            p.append(T(700, y + 20, val, 280, 22, col, True, "RIGHT"))
            y += 84
        y += 20
    p.append(T(64, 1010, "下一步：两个月后复查血脂与血糖，其余一年后常规体检。", 950, 20, INK, True))
    p.append(T(64, 1058, "报告上的箭头只是「偏离参考区间」，不等于「有病」。", 950, 19, DIM))
    p.append(T(64, 1150, "说明：数值为示例，不构成医疗建议。", 900, 17, DIM))
    return K.document(W, H, p, background=PAPER)

CASES = [
    ("case-01", "电费单：钱花在哪一档", c1, (1200, 1600), "账单", "把总额拆成三档与三条差异"),
    ("case-02", "站台：我的车厢在哪", c2, (1600, 900), "导视", "16 节编组平面图 + 4 步走法"),
    ("case-03", "营养表：一份占多少", c3, (1080, 1350), "标签", "每 100 克换算成整份与每日占比"),
    ("case-04", "合同：六条关键的", c4, (1200, 1600), "合同", "按风险排序，红黄绿三档"),
    ("case-05", "就诊：下一步去哪", c5, (1400, 1000), "流程", "五个点 + 每段耗时"),
    ("case-06", "物流：还要几天", c6, (1080, 1350), "状态", "九条流水压成四个阶段"),
    ("case-07", "垃圾：扔哪个桶", c7, (1080, 1080), "判别", "三个是非问题走到底"),
    ("case-08", "洗标：怎么洗", c8, (1080, 1350), "符号", "五个符号翻译成一句话"),
    ("case-09", "停车牌：现在能停吗", c9, (900, 1200), "规则", "四段时段 + 一句话结论"),
    ("case-10", "体检：先管哪两项", c10, (1080, 1500), "报告", "按行动优先级重排 12 项"),
]

logger = api.TaskLogger(TASK, TMP)
ONLY = os.environ.get("B06_ONLY", "").split(",") if os.environ.get("B06_ONLY") else None
meta = []
for cid, title, fn, size, kind, method in CASES:
    if ONLY and cid not in ONLY:
        continue
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    dsl = fn()
    (d / "final.snapshot").write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(d / "final.snapshot", d / "final.png", cid)
    ok = rec["http_status"] == 200 and api.measure_png(d / "final.png") == size
    print(f"{cid}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s ok={ok}")
    for w in warn:
        print("   ", w)
    meta.append({"case": cid, "title": title, "size": list(size), "kind": kind,
                 "method": method, "png": f"{cid}/final.png", "dsl": f"{cid}/final.snapshot",
                 "bytes": rec["response_bytes"]})
if not ONLY:
    api.write_json(TMP / "cases.json", meta)
print("rendered", len(meta))
