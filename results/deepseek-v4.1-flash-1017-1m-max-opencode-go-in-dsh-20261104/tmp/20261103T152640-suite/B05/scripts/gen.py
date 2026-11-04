# -*- coding: utf-8 -*-
"""B05: product from zero - MediSort pill dispenser + family app."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "B05"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

INK, DIM, PAPER, CARD = "#14201C", "#5C6B62", "#F5F7F3", "#FFFFFF"
GREEN, AMBER, RED, SOFT = "#1F7A4D", "#B26A00", "#B3352E", "#E4EDE6"

def R(x, y, w, h, c, r=0, b=None):
    return K.rect(x, y, w, h, color=c, radius=r, border=b)

def T(x, y, s, w, size, c=INK, bold=False, align=None, label=None):
    return K.text(x, y, s, width=w, size=size, color=c, bold=bold, align=align, label=label)

def phone(status_bar=True, w=390, h=844, bg=PAPER):
    p = [R(0, 0, w, h, bg)]
    if status_bar:
        p.append(R(0, 0, w, 44, bg))
        p.append(T(20, 14, "9:41", 60, 15, INK, True))
        p.append(T(280, 14, "􀙇 􀖀 100%", 90, 13, INK, align="RIGHT"))
    return p

# 1 device idle
def c1():
    W, H = 800, 480
    p = [R(0, 0, W, H, "#EDF1EA")]
    p.append(R(0, 0, 8, H, GREEN))
    p.append(T(44, 40, "下一次用药", 400, 26, DIM))
    p.append(T(44, 84, "12:30", 420, 96, INK, True))
    p.append(T(44, 200, "钙片 1 片 · 随餐", 500, 28, INK))
    p.append(T(44, 244, "还有 1 小时 12 分", 500, 22, DIM))
    p.append(R(44, 300, 712, 2, "#C9D6CB"))
    p.append(T(44, 324, "今天 4 次 · 已完成 1 次", 500, 22, INK))
    p.append(T(44, 360, "08:00 完成 · 12:30 待服 · 19:00 · 21:00", 700, 20, DIM))
    p.append(R(600, 380, 156, 56, SOFT, 28))
    p.append(T(600, 396, "查看药格", 156, 20, GREEN, True, "CENTER"))
    return K.document(W, H, p, background="#EDF1EA")

# 2 device alert
def c2():
    W, H = 800, 480
    p = [R(0, 0, W, H, "#1F7A4D")]
    p.append(T(44, 40, "该吃药了", 500, 30, "#CDEBD9"))
    p.append(T(44, 84, "12:30", 420, 96, "#FFFFFF", True))
    p.append(T(44, 200, "钙片 1 片", 500, 40, "#FFFFFF", True))
    p.append(T(44, 260, "药格已亮起 · 请取出后放回", 600, 24, "#CDEBD9"))
    p.append(R(44, 330, 340, 84, "#FFFFFF", 16))
    p.append(T(44, 356, "已服用", 340, 30, GREEN, True, "CENTER"))
    p.append(R(416, 330, 340, 84, "#14563A", 16))
    p.append(T(416, 356, "稍后提醒（10 分钟）", 340, 26, "#FFFFFF", align="CENTER"))
    return K.document(W, H, p, background="#1F7A4D")

# 3 device confirmation
def c3():
    W, H = 800, 480
    p = [R(0, 0, W, H, "#EDF1EA")]
    p.append(R(0, 0, W, 8, GREEN))
    p.append(R(44, 60, 96, 96, GREEN, 48))
    p.append(T(44, 92, "✓", 96, 52, "#FFFFFF", True, "CENTER"))
    p.append(T(168, 72, "已记录 12:30 钙片", 560, 36, INK, True))
    p.append(T(168, 124, "今天第 2 次 · 连续 9 天按时", 560, 24, DIM))
    p.append(R(44, 200, 712, 2, "#C9D6CB"))
    p.append(T(44, 226, "下一次", 300, 22, DIM))
    p.append(T(44, 258, "19:00 二甲双胍 1 片", 600, 32, INK, True))
    p.append(T(44, 320, "家属已收到通知（女儿 张蕾）", 700, 22, DIM))
    p.append(R(44, 380, 712, 2, "#C9D6CB"))
    return K.document(W, H, p, background="#EDF1EA")

# 4 family home
def c4():
    W, H = 390, 844
    p = phone()
    p.append(T(20, 62, "张阿姨 · 今天", 300, 26, INK, True))
    p.append(T(20, 96, "10 月 18 日 周六", 300, 18, DIM))
    p.append(R(20, 132, 350, 132, CARD, 16, f"1 SOLID {SOFT}"))
    p.append(T(40, 150, "今天 2 / 4 次", 300, 22, DIM))
    p.append(T(40, 180, "下次 19:00", 200, 30, INK, True))
    p.append(T(40, 222, "二甲双胍 1 片 · 随餐", 300, 19, DIM))
    p.append(R(40, 250, 310, 1, SOFT))
    p.append(R(20, 284, 350, 96, CARD, 16, f"1 SOLID {SOFT}"))
    p.append(T(40, 300, "本周按时率", 200, 19, DIM))
    p.append(T(40, 326, "26 / 28", 160, 34, GREEN, True))
    p.append(T(206, 336, "92.9%", 140, 22, GREEN, True, "RIGHT"))
    p.append(T(20, 400, "今天的时间表", 300, 20, INK, True))
    rows = [("08:00", "氨氯地平 5mg ＋ 二甲双胍 500mg", "已完成", GREEN),
            ("12:30", "钙片 1 片", "已完成", GREEN),
            ("19:00", "二甲双胍 500mg", "待服", AMBER),
            ("21:00", "阿托伐他汀 20mg", "待服", DIM)]
    for i, (t, name, st, col) in enumerate(rows):
        y = 436 + i * 80
        p.append(R(20, y, 350, 68, CARD, 12, f"1 SOLID {SOFT}"))
        p.append(T(36, y + 12, t, 90, 20, INK, True))
        p.append(T(36, y + 38, name, 240, 15, DIM))
        p.append(T(300, y + 22, st, 56, 15, col, True, "RIGHT"))
    p.append(R(20, 764, 350, 56, GREEN, 28))
    p.append(T(20, 780, "给妈妈打电话", 350, 20, "#FFFFFF", True, "CENTER"))
    return K.document(W, H, p, background=PAPER)

# 5 schedule editor
def c5():
    W, H = 390, 844
    p = phone()
    p.append(T(20, 62, "用药时间表", 300, 26, INK, True))
    p.append(T(20, 100, "共 3 种药 · 每日 4 次", 340, 18, DIM))
    meds = [("氨氯地平", "5 mg · 每日 1 次", "08:00", GREEN),
            ("二甲双胍", "500 mg · 每日 2 次", "08:00 / 19:00", GREEN),
            ("阿托伐他汀", "20 mg · 每日 1 次", "21:00", GREEN),
            ("钙片", "1 片 · 每日 1 次", "12:30", AMBER)]
    for i, (name, dose, times, col) in enumerate(meds):
        y = 140 + i * 122
        p.append(R(20, y, 350, 108, CARD, 14, f"1 SOLID {SOFT}"))
        p.append(R(20, y, 5, 108, col, 2))
        p.append(T(38, y + 14, name, 200, 21, INK, True))
        p.append(T(38, y + 44, dose, 220, 16, DIM))
        p.append(T(38, y + 70, times, 260, 17, INK))
        p.append(T(300, y + 44, "编辑", 52, 16, GREEN, True, "RIGHT"))
    p.append(R(20, 648, 350, 56, SOFT, 28))
    p.append(T(20, 664, "＋ 添加药品", 350, 20, GREEN, True, "CENTER"))
    p.append(T(20, 728, "修改后需药师复核，通常 2 小时内生效。", 350, 15, DIM))
    p.append(T(20, 754, "当前版本 v3 · 10 月 12 日复核", 350, 15, DIM))
    return K.document(W, H, p, background=PAPER)

# 6 refill
def c6():
    W, H = 390, 844
    p = phone()
    p.append(T(20, 62, "补药提醒", 300, 26, INK, True))
    p.append(R(20, 104, 350, 120, "#FFF6E8", 16, f"1 SOLID {AMBER}"))
    p.append(T(40, 122, "阿托伐他汀只剩 6 天", 300, 21, AMBER, True))
    p.append(T(40, 154, "按当前用量，10 月 24 日用完", 300, 17, DIM))
    p.append(T(40, 184, "建议今天下单", 300, 17, AMBER))
    p.append(T(20, 256, "可选药房", 300, 20, INK, True))
    shops = [("社区药房（步行 6 分钟）", "次日达 · ￥38.5", GREEN),
             ("线上药房 · 已备案", "隔日达 · ￥32.0", DIM)]
    for i, (name, note, col) in enumerate(shops):
        y = 292 + i * 96
        p.append(R(20, y, 350, 84, CARD, 12, f"1 SOLID {SOFT}"))
        p.append(T(36, y + 14, name, 300, 18, INK, True))
        p.append(T(36, y + 44, note, 260, 16, DIM))
        p.append(R(296, y + 22, 58, 40, SOFT, 20))
        p.append(T(296, y + 32, "选择", 58, 15, GREEN, True, "CENTER"))
    p.append(R(20, 512, 350, 1, SOFT))
    p.append(T(20, 532, "处方有效期至 2026-12-31", 340, 16, DIM))
    p.append(T(20, 560, "下单前会再次核对剂量与相互作用。", 340, 15, DIM))
    p.append(R(20, 764, 350, 56, GREEN, 28))
    p.append(T(20, 780, "确认下单", 350, 20, "#FFFFFF", True, "CENTER"))
    return K.document(W, H, p, background=PAPER)

# 7 weekly report
def c7():
    W, H = 768, 1024
    p = [R(0, 0, W, H, PAPER)]
    p.append(T(48, 48, "用药周报", 400, 30, INK, True))
    p.append(T(48, 88, "张阿姨 · 10 月 12 日 – 10 月 18 日", 600, 18, DIM))
    p.append(R(48, 128, 672, 2, SOFT))
    kpis = [("按时率", "92.9%"), ("漏服", "2 次"), ("平均延迟", "14 分钟")]
    for i, (k, v) in enumerate(kpis):
        x = 48 + i * 230
        p.append(T(x, 152, k, 200, 18, DIM))
        p.append(T(x, 180, v, 200, 40, GREEN if i == 0 else INK, True))
    p.append(T(48, 256, "每天的完成情况", 400, 20, INK, True))
    days = ["一", "二", "三", "四", "五", "六", "日"]
    vals = [4, 4, 3, 4, 4, 3, 4]
    for i, v in enumerate(vals):
        x = 60 + i * 92
        h = v * 34
        p.append(R(x, 460 - h, 56, h, GREEN if v == 4 else AMBER, 8))
        p.append(T(x - 8, 472, days[i], 72, 18, DIM, align="CENTER"))
        p.append(T(x - 8, 496, f"{v}/4", 72, 16, INK, align="CENTER"))
    p.append(R(48, 540, 672, 1, SOFT))
    p.append(T(48, 566, "两次漏服都发生在晚上", 500, 20, INK, True))
    p.append(T(48, 600, "10 月 14 日 19:00 与 10 月 17 日 19:00 未记录服药。", 660, 17, DIM))
    p.append(T(48, 628, "建议把晚间药格移到餐桌旁。", 660, 17, GREEN))
    p.append(R(48, 700, 672, 1, SOFT))
    p.append(T(48, 726, "本周事件", 400, 20, INK, True))
    ev = [("10-15", "药师复核通过，新增钙片"), ("10-16", "补药提醒已发送"), ("10-18", "女儿查看 3 次")]
    for i, (d, t) in enumerate(ev):
        y = 762 + i * 44
        p.append(T(48, y, d, 90, 17, DIM))
        p.append(T(148, y, t, 560, 17, INK))
    p.append(T(48, 950, "数据仅来自设备记录，未做人工核对。", 660, 15, DIM))
    return K.document(W, H, p, background=PAPER)

# 8 onboarding pairing
def c8():
    W, H = 390, 844
    p = phone()
    p.append(T(20, 70, "连接药盒", 300, 26, INK, True))
    p.append(T(20, 108, "第 2 步，共 3 步", 300, 17, DIM))
    p.append(R(20, 152, 350, 300, CARD, 20, f"1 SOLID {SOFT}"))
    p.append(R(120, 200, 150, 150, SOFT, 20))
    p.append(T(120, 250, "◉", 150, 44, GREEN, align="CENTER"))
    p.append(T(20, 366, "正在搜索附近的药盒…", 350, 18, INK, align="CENTER"))
    p.append(T(20, 396, "请长按药盒顶部按钮 3 秒，指示灯变蓝", 350, 15, DIM, align="CENTER"))
    p.append(R(20, 480, 350, 96, CARD, 14, f"1 SOLID {SOFT}"))
    p.append(T(36, 496, "已找到", 120, 15, DIM))
    p.append(T(36, 520, "MediSort-0417", 260, 19, INK, True))
    p.append(T(36, 548, "信号良好 · 电量 82%", 260, 15, DIM))
    p.append(T(20, 610, "找不到？", 300, 18, GREEN, True))
    p.append(T(20, 640, "把药盒放在手机 1 米内，重新搜索。", 350, 15, DIM))
    p.append(T(20, 666, "仍失败可联系客服 400-000-0000。", 350, 15, DIM))
    p.append(R(20, 764, 350, 56, GREEN, 28))
    p.append(T(20, 780, "下一步：设置时间表", 350, 20, "#FFFFFF", True, "CENTER"))
    return K.document(W, H, p, background=PAPER)

# 9 pharmacist review
def c9():
    W, H = 1024, 768
    p = [R(0, 0, W, H, PAPER)]
    p.append(R(0, 0, W, 56, "#14332A"))
    p.append(T(32, 16, "药师复核 · 待处理 3 单", 600, 20, "#FFFFFF", True))
    p.append(T(760, 20, "李药师 · 在线", 232, 15, "#9FD4B7", align="RIGHT"))
    p.append(R(32, 84, 460, 300, CARD, 12, f"1 SOLID {SOFT}"))
    p.append(T(52, 100, "张阿姨（72 岁）", 300, 20, INK, True))
    p.append(T(52, 130, "当前 4 种药 · 每日 4 次", 340, 16, DIM))
    drugs = [("氨氯地平 5mg", "08:00"), ("二甲双胍 500mg", "08:00 / 19:00"),
             ("阿托伐他汀 20mg", "21:00"), ("钙片", "12:30")]
    for i, (d, t) in enumerate(drugs):
        y = 166 + i * 44
        p.append(T(52, y, d, 300, 17, INK))
        p.append(T(360, y, t, 110, 16, DIM, align="RIGHT"))
    p.append(R(520, 84, 472, 300, CARD, 12, f"1 SOLID {SOFT}"))
    p.append(T(540, 100, "相互作用检查", 300, 20, INK, True))
    hits = [("氨氯地平 × 阿托伐他汀", "轻微：可能升高他汀血药浓度", AMBER),
            ("钙片 × 二甲双胍", "无显著相互作用", GREEN),
            ("二甲双胍 × 阿托伐他汀", "无显著相互作用", GREEN)]
    for i, (pair, note, col) in enumerate(hits):
        y = 140 + i * 78
        p.append(R(540, y, 6, 60, col, 3))
        p.append(T(560, y + 4, pair, 400, 17, INK, True))
        p.append(T(560, y + 30, note, 400, 15, DIM))
    p.append(R(32, 404, 960, 200, CARD, 12, f"1 SOLID {SOFT}"))
    p.append(T(52, 420, "服药说明（发送给家属）", 400, 18, INK, True))
    p.append(T(52, 452, "阿托伐他汀请固定在晚间服用，避免与钙片同服；", 900, 17, INK))
    p.append(T(52, 482, "如出现肌肉酸痛请停药并联系社区医生。", 900, 17, INK))
    p.append(T(52, 520, "复核人：李药师　时间：2026-10-18 15:42", 900, 15, DIM))
    p.append(R(32, 630, 300, 64, GREEN, 10))
    p.append(T(32, 650, "通过并发送", 300, 20, "#FFFFFF", True, "CENTER"))
    p.append(R(352, 630, 300, 64, SOFT, 10))
    p.append(T(352, 650, "退回修改", 300, 20, INK, True, "CENTER"))
    return K.document(W, H, p, background=PAPER)

# 10 printable card
def c10():
    W, H = 559, 794
    p = [R(0, 0, W, H, "#FFFFFF")]
    p.append(R(0, 0, W, 6, GREEN))
    p.append(T(40, 32, "我的服药卡", 400, 26, INK, True))
    p.append(T(40, 68, "张阿姨 · 2026 年 10 月", 400, 15, DIM))
    p.append(R(40, 96, W - 80, 2, SOFT))
    rows = [("08:00", "氨氯地平 5mg\n二甲双胍 500mg", "早餐后"),
            ("12:30", "钙片 1 片", "午餐后"),
            ("19:00", "二甲双胍 500mg", "晚餐后"),
            ("21:00", "阿托伐他汀 20mg", "睡前")]
    for i, (t, drug, meal) in enumerate(rows):
        y = 116 + i * 130
        p.append(T(40, y, t, 110, 30, GREEN, True))
        p.append(T(150, y + 2, drug.split("\n")[0], 330, 17, INK))
        if "\n" in drug:
            p.append(T(150, y + 28, drug.split("\n")[1], 330, 17, INK))
        p.append(T(150, y + 56, meal, 300, 14, DIM))
        p.append(R(40, y + 100, W - 80, 1, SOFT))
    p.append(T(40, 660, "漏服时不要加倍补服；连续两次漏服请联系医生。", 480, 13, INK))
    p.append(T(40, 686, "药师：李药师　社区医院：0571-0000-0000", 480, 13, DIM))
    p.append(T(40, 712, "药盒客服：400-000-0000", 480, 13, DIM))
    p.append(R(40, 744, 60, 6, GREEN))
    return K.document(W, H, p, background="#FFFFFF")

CASES = [
    ("case-01", "药盒待机屏", c1, (800, 480), "device", "客厅", "说明下一次服药时间与今日进度"),
    ("case-02", "到点提醒", c2, (800, 480), "device", "客厅", "到点后用全屏提醒并提供两个选择"),
    ("case-03", "服药确认", c3, (800, 480), "device", "客厅", "完成后的即时反馈与下一次预告"),
    ("case-04", "家属端首页", c4, (390, 844), "app", "手机", "子女一眼看到妈妈今天的状态"),
    ("case-05", "时间表编辑", c5, (390, 844), "app", "手机", "调整剂量与时间并走药师复核"),
    ("case-06", "补药提醒", c6, (390, 844), "app", "手机", "快吃完了，给出可下单的药房"),
    ("case-07", "用药周报", c7, (768, 1024), "report", "平板", "一周按时率与两次漏服的规律"),
    ("case-08", "设备配对", c8, (390, 844), "app", "手机", "首次连接药盒的操作指引"),
    ("case-09", "药师复核", c9, (1024, 768), "pro", "桌面", "药师核对相互作用并发送说明"),
    ("case-10", "打印服药卡", c10, (559, 794), "print", "冰箱/随身", "不依赖手机的纸质备份"),
]

logger = api.TaskLogger(TASK, TMP)
ONLY = os.environ.get("B05_ONLY", "").split(",") if os.environ.get("B05_ONLY") else None
meta = []
for cid, title, fn, size, kind, place, need in CASES:
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
                 "place": place, "need": need, "png": f"{cid}/final.png",
                 "dsl": f"{cid}/final.snapshot", "bytes": rec["response_bytes"]})
if not ONLY:
    api.write_json(TMP / "cases.json", meta)
print("rendered", len(meta))
