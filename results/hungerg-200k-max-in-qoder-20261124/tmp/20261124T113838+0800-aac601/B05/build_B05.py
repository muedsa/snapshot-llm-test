from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B05"
run = sk.init_suite()[0]
plan = json.loads((BASE / "plan-v004.json").read_text(encoding="utf-8"))
product = json.loads((BASE / "product-data.json").read_text(encoding="utf-8"))
MEDS = product["medications"]
FONT = "Noto Sans CJK SC"
INK = "#173D39"
MUTED = "#687A73"
PAPER = "#F4F1E8"
WHITE = "#FFFEF8"
GREEN = "#246B5C"
MINT = "#DCEBE1"
LIME = "#D9E98F"
ORANGE = "#D96B43"
PALE_ORANGE = "#F7E0D3"
BLUE = "#4B7181"
PALE_BLUE = "#DFE9EB"
LINE = "#CBD5C9"
RED = "#A74435"


def text(value, size=20, color=INK, bold=False, align="LEFT", max_lines=None):
    attrs = [f'fontFamily="{FONT}"', f'fontSize="{size:g}"', f'color="{color}"',
             f'textAlign="{align}"', f'fontStyle="{"BOLD" if bold else "NORMAL"}"', 'softWrap="true"']
    if max_lines:
        attrs += [f'maxLines="{max_lines}"', 'overflow="ELLIPSIS"']
    return "<Text " + " ".join(attrs) + ">" + escape(str(value)) + "</Text>"


def lab(value, x, y, w, h, size=20, color=INK, bold=False, align="LEFT", max_lines=None):
    alignment = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}[align]
    return sk.positioned(x, y, w, h, f'<Container width="{w:g}" height="{h:g}" alignment="{alignment}">' + text(value, size, color, bold, align, max_lines) + "</Container>")


def pill(value, x, y, w, bg=MINT, fg=GREEN, size=14, h=30):
    return sk.box(x, y, w, h, bg, h/2) + lab(value, x+8, y, w-16, h, size, fg, True, "CENTER", 1)


def button(value, x, y, w, h=54, bg=GREEN, fg=WHITE, size=18):
    return sk.box(x, y, w, h, bg, 14) + lab(value, x+12, y, w-24, h, size, fg, True, "CENTER", 2)


def check(x, y, color=GREEN, size=22):
    return sk.circle(x+size/2, y+size/2, size/2, color) + lab("✓", x, y-1, size, size, size*0.66, WHITE, True, "CENTER")


def icon_circle(letter, x, y, bg=GREEN, fg=WHITE, size=36):
    return sk.circle(x+size/2, y+size/2, size/2, bg) + lab(letter, x, y, size, size, size*.42, fg, True, "CENTER")


def med_icon(med, x, y, scale=1):
    w, h = 46*scale, 28*scale
    if med["shape"] == "long":
        node = sk.box(x, y, w, h, med["color"], h/2)
        node += sk.box(x+w/2-1*scale, y, 2*scale, h, WHITE)
    elif med["shape"] == "capsule":
        node = sk.box(x, y, w, h, med["color"], h/2)
        node += sk.box(x+w/2-1*scale, y, 2*scale, h, WHITE)
    else:
        node = sk.circle(x+w/2, y+h/2, h/2, med["color"])
        node += sk.box(x+w*.37, y+h*.2, w*.26, max(1, 2*scale), WHITE)
    return node


def phone_status(width, dark=False):
    fg = WHITE if dark else INK
    return lab("9:41", 22, 10, 70, 28, 14, fg, True) + lab("演示设备 · 同频", width-154, 10, 130, 28, 12, fg, False, "RIGHT")


def phone_nav(active, width=390):
    items = ["今天", "清单", "联系", "我的"]
    nodes = [sk.box(0, 790, width, 54, WHITE)]
    for i, item in enumerate(items):
        x = i*width/4
        nodes.append(lab(item, x, 806, width/4, 24, 12, GREEN if i == active else MUTED, i == active, "CENTER"))
        if i == active:
            nodes.append(sk.box(x+width/8-10, 792, 20, 3, GREEN, 2))
    return "".join(nodes)


def brand(x, y, dark=False, compact=False):
    fg = WHITE if dark else INK
    nodes = icon_circle("同", x, y, LIME if dark else GREEN, INK if dark else WHITE, 32 if compact else 40)
    nodes += lab("同频", x+(42 if compact else 52), y-2, 92, 32 if compact else 40, 22 if compact else 28, fg, True)
    return nodes


def demo_footer(width, y, dark=False):
    fg = "#D5DFD5" if dark else MUTED
    return lab("虚构产品与演示数据 · 不构成医疗建议", 20, y, width-40, 22, 11, fg, False, "CENTER")


def case01():
    w, h = 390, 844
    n = [sk.box(0, 0, w, h, PAPER), phone_status(w), brand(22, 54, compact=True), pill("1 / 10", 302, 56, 66, MINT, GREEN, 12)]
    n += [lab("把药盒放进来", 22, 112, 346, 48, 30, INK, True),
          lab("先识别，再逐项确认。识别结果不是处方。", 22, 160, 346, 40, 15, MUTED)]
    n += [sk.box(22, 214, 346, 170, INK, 24),
          lab("药盒照片 · 演示", 42, 230, 200, 24, 13, LIME, True),
          pill("5 项待确认", 254, 228, 94, LIME, INK, 12)]
    for i, med in enumerate(MEDS):
        x = 44 + (i % 3)*105
        y = 274 + (i // 3)*48
        n += [sk.box(x, y, 88, 36, WHITE, 8), med_icon(med, x+10, y+6, .55),
              lab(f"药品 {i+1:02d}", x+37, y+2, 46, 31, 10, INK, True, "CENTER", 1)]
    n += [lab("识别出的药品", 22, 402, 250, 26, 14, MUTED, True), lab("左右滑动核对", 250, 402, 118, 26, 12, MUTED, False, "RIGHT")]
    for i, med in enumerate(MEDS):
        y = 438 + i*54
        n += [sk.box(22, y, 346, 47, WHITE, 12), med_icon(med, 34, y+11, .65),
              lab(f'{med["name"]}  {med["strength"]}', 82, y+3, 206, 23, 14, INK, True),
              lab(med["schedule"], 82, y+24, 230, 18, 11, MUTED), check(330, y+13, GREEN, 20)]
    n += [sk.box(22, 718, 346, 40, PALE_ORANGE, 12), lab("过敏记录：青霉素（演示）", 36, 718, 318, 40, 13, RED, True)]
    n += [button("确认这 5 项，建立清单", 22, 770, 346, 50), demo_footer(w, 828)]
    return sk.snapshot(w, h, n, PAPER)


def case02():
    w, h = 1440, 1000
    n = [sk.box(0, 0, w, h, "#EDF1EA"), brand(46, 36),
          lab("林建国 · 家庭清单", 930, 38, 280, 30, 18, INK, True, "RIGHT"),
          icon_circle("岚", 1246, 32, GREEN, WHITE, 40),
          lab("三份清单，先对齐", 46, 104, 860, 58, 40, INK, True),
          lab("差异不会自动覆盖。请医生或药师确认后，再更新家庭清单。", 46, 162, 1040, 34, 18, MUTED),
          pill("2 处待确认", 1190, 120, 200, PALE_ORANGE, RED, 16, 42)]
    cols = [
        (46, "门诊记录", "11月24日 10:20", BLUE, [("M01", "5 mg · 每日1片", False), ("M02", "40片 · 每日2片", True), ("M03", "已停用", True), ("M04", "20 mg · 每日1片", False), ("M05", "1000 IU · 每日1粒", False)]),
        (496, "家庭药盒", "11月24日 19:05", GREEN, [("M01", "22片 · 每日1片", False), ("M02", "32片 · 每日2片", True), ("M03", "18片 · 每晚1片", True), ("M04", "12片 · 每日1片", False), ("M05", "30粒 · 每日1粒", False)]),
        (946, "上次清单", "11月10日 18:30", "#89764D", [("M01", "5 mg · 每日1片", False), ("M02", "30片 · 每日2片", False), ("M03", "20 mg · 每晚1片", False), ("M04", "20 mg · 每日1片", False), ("M05", "未记录", False)]),
    ]
    for x, title, time, color, rows in cols:
        n += [sk.box(x, 230, 448, 594, WHITE, 20), sk.box(x, 230, 448, 7, color, 4),
              lab(title, x+24, 258, 250, 32, 23, INK, True), lab(time, x+24, 294, 340, 24, 13, MUTED)]
        for i, (mid, value, issue) in enumerate(rows):
            med = next(m for m in MEDS if m["id"] == mid)
            y = 340 + i*88
            if issue:
                n += [sk.box(x+16, y-8, 416, 76, PALE_ORANGE, 12)]
            n += [med_icon(med, x+28, y+5, .75), lab(med["name"], x+78, y, 190, 25, 17, INK, True),
                  lab(value, x+78, y+28, 280, 23, 14, RED if issue else MUTED, issue),
                  lab("待确认" if issue else "一致", x+304, y, 104, 28, 12, RED if issue else GREEN, True, "RIGHT")]
    n += [sk.box(46, 850, 1348, 94, INK, 18),
          lab("差异 01", 72, 866, 110, 22, 12, LIME, True), lab("Metformin 家中剩余 32片，门诊记录 40片", 72, 890, 700, 28, 17, WHITE, True),
          lab("差异 02", 802, 866, 110, 22, 12, LIME, True), lab("Atorvastatin：停用状态待确认", 802, 890, 420, 28, 17, WHITE, True),
          button("生成给医生的问题", 1150, 867, 218, 56, LIME, INK, 15),
          demo_footer(w, 966)]
    return sk.snapshot(w, h, n, "#EDF1EA")


def case03():
    w, h = 1200, 900
    n = [sk.box(0, 0, w, h, PAPER), brand(42, 34),
          lab("共享与权限", 42, 108, 700, 56, 38, INK, True),
          lab("父亲保留决定权；家人协助协调，不代替医生。", 42, 164, 900, 32, 18, MUTED),
          sk.box(42, 226, 620, 496, WHITE, 24),
          lab("一个家庭，三种角色", 70, 252, 500, 34, 23, INK, True)]
    n += [sk.line(334, 388, 370, 480, "#CBD5C9", 3), sk.line(202, 446, 202, 536, "#CBD5C9", 3),
          sk.line(334, 388, 502, 548, "#CBD5C9", 3)]
    roles = [(70, 330, "林建国 · 72岁", "本人", "查看、确认、随时撤销授权", GREEN),
             (370, 424, "林岚 · 女儿", "主要协调人", "录入、提醒、生成就诊摘要", BLUE),
             (70, 536, "门诊医生", "专业确认", "确认处方与剂量变更", "#89764D")]
    for x, y, name, role, ability, color in roles:
        n += [sk.box(x, y, 264, 116, "#F4F6EF", 16), icon_circle(role[0], x+16, y+16, color, WHITE, 40),
              lab(name, x+68, y+12, 182, 28, 17, INK, True), pill(role, x+68, y+44, 112, MINT, GREEN, 11, 24),
              lab(ability, x+16, y+80, 232, 26, 12, MUTED)]
    n += [sk.box(370, 548, 264, 126, INK, 16), lab("紧急联系人", 390, 564, 220, 28, 18, WHITE, True),
          lab("林澄 · 儿子\n仅在紧急卡片中显示", 390, 600, 220, 52, 14, "#DDE7DD")]
    n += [sk.box(700, 226, 458, 496, WHITE, 24), lab("林岚可以做什么", 728, 254, 390, 34, 23, INK, True)]
    perms = [("查看清单与库存", True), ("记录家属观察", True), ("接收异常提醒", True), ("修改处方或剂量", False), ("代替本人确认服药", False)]
    for i, (name, allowed) in enumerate(perms):
        y = 320 + i*62
        n += [lab(name, 730, y, 270, 38, 16, INK, allowed), check(1058, y+6, GREEN if allowed else "#A9B5AA", 24)]
        if not allowed:
            n += [lab("不可", 1090, y+4, 46, 30, 12, RED, True)]
    n += [button("保存授权设置", 728, 650, 402, 50, GREEN, WHITE, 16)]
    n += [sk.box(42, 748, 1116, 94, MINT, 18),
          check(66, 772, GREEN, 28), lab("2026-11-24 19:12 · 林建国确认共享", 110, 762, 680, 30, 17, INK, True),
          lab("授权范围：清单、库存与家属观察；不含自动改处方。", 110, 796, 790, 24, 14, MUTED),
          pill("可随时撤销", 958, 770, 170, WHITE, GREEN, 13, 34), demo_footer(w, 866)]
    return sk.snapshot(w, h, n, PAPER)


def case04():
    w, h = 390, 844
    n = [sk.box(0, 0, w, h, "#E7EFE2"), phone_status(w), brand(22, 52, compact=True),
          lab("林建国，早上好", 22, 116, 346, 46, 29, INK, True),
          lab("11月24日 · 周二", 22, 162, 250, 28, 15, MUTED),
          pill("大字模式", 278, 160, 90, WHITE, GREEN, 12, 30),
          sk.box(22, 212, 346, 88, INK, 20), lab("08:00", 42, 224, 110, 42, 28, LIME, True),
          lab("早晨的 4 项", 160, 224, 188, 32, 18, WHITE, True), lab("按已确认清单 · 未确认可稍后", 160, 258, 188, 24, 11, "#D9E3D8")]
    morning = [MEDS[0], MEDS[1], MEDS[3], MEDS[4]]
    for i, med in enumerate(morning):
        y = 314 + i*86
        n += [sk.box(22, y, 346, 78, WHITE, 16), med_icon(med, 42, y+27, 1),
              lab(med["name"], 112, y+9, 230, 26, 19, INK, True),
              lab(f'{med["strength"]} · 1{"粒" if med["shape"] == "capsule" else "片"}', 112, y+36, 230, 24, 14, MUTED)]
        if med["id"] == "M02":
            n += [pill("未确认", 292, y+42, 62, "#FFF1E6", RED, 11, 24)]
    n += [lab("完成后会记录时间，家属可看到。", 22, 664, 346, 26, 13, MUTED),
          button("我已服用", 22, 704, 208, 58, GREEN, WHITE, 20),
          button("稍后 / 求助", 242, 704, 126, 58, WHITE, GREEN, 16), phone_nav(0, w), demo_footer(w, 764)]
    return sk.snapshot(w, h, n, "#E7EFE2")


def case05():
    w, h = 390, 844
    n = [sk.box(0, 0, w, h, PAPER), phone_status(w), icon_circle("‹", 22, 58, WHITE, INK, 38),
          lab("漏服记录", 76, 58, 250, 38, 22, INK, True),
          sk.box(22, 122, 346, 116, PALE_ORANGE, 20),
          lab("先记录，不自动补服", 42, 138, 306, 34, 23, RED, True),
          lab("是否补服、何时补服，请遵循医嘱或询问药师。", 42, 178, 306, 44, 14, RED),
          lab("发生了什么", 22, 270, 346, 32, 20, INK, True),
          sk.box(22, 312, 346, 150, WHITE, 18), med_icon(MEDS[1], 42, 336, .8),
          lab("Metformin 500 mg", 108, 328, 236, 28, 18, INK, True), lab("08:00 项目 · 状态未确认", 108, 360, 236, 24, 14, RED, True),
          lab("09:40  林建国报告：可能忘记服用", 42, 408, 304, 26, 14, MUTED),
          lab("记录为：家属报告，不是医生诊断", 42, 438, 304, 20, 11, MUTED),
          sk.box(22, 488, 346, 106, WHITE, 18), icon_circle("!", 42, 512, RED, WHITE, 34),
          lab("不要自行加倍", 92, 502, 250, 28, 18, INK, True),
          lab("应用不会建议剂量，也不会自动标记为已服。", 92, 536, 246, 44, 14, MUTED),
          lab("下一步", 22, 620, 346, 30, 20, INK, True),
          button("联系药师", 22, 660, 164, 54, GREEN, WHITE, 17),
          button("通知林岚", 198, 660, 170, 54, WHITE, GREEN, 17),
          sk.box(22, 732, 346, 42, MINT, 12), check(36, 742, GREEN, 22),
          lab("保存后将同步到就诊摘要", 70, 732, 280, 42, 13, INK, True), demo_footer(w, 822)]
    return sk.snapshot(w, h, n, PAPER)


def case06():
    w, h = 1024, 768
    n = [sk.box(0, 0, w, h, "#EEF2EA"), brand(34, 28),
          lab("林建国 · 库存与补药", 34, 94, 650, 48, 34, INK, True),
          lab("今日盘点：Metformin 32 → 40片；按已记录频次估算。", 34, 142, 700, 30, 16, MUTED),
          pill("演示日期 11月24日", 792, 104, 198, WHITE, GREEN, 13, 36)]
    n += [sk.box(34, 202, 650, 488, WHITE, 20), lab("药品", 58, 222, 250, 28, 15, MUTED, True),
          lab("剩余 / 频次", 330, 222, 150, 28, 15, MUTED, True), lab("约可维持", 580, 222, 80, 28, 15, MUTED, True, "RIGHT")]
    for i, med in enumerate(MEDS):
        y = 274 + i*80
        urgent = med["id"] == "M02"
        if urgent:
            n += [sk.box(48, y-10, 622, 70, PALE_ORANGE, 12)]
        n += [med_icon(med, 60, y+2, .65), lab(f'{med["name"]} {med["strength"]}', 106, y-4, 220, 26, 15, INK, True),
              lab(f'{med["quantity"]}{"片" if med["shape"] != "capsule" else "粒"} / 每日{med["times_per_day"]}次', 330, y-4, 160, 26, 14, RED if urgent else MUTED, urgent),
              lab(f'{int(med["days_remaining"])} 天', 580, y-4, 70, 26, 15, RED if urgent else INK, True, "RIGHT"),
              sk.box(106, y+35, 544, 7, "#E7EBE3", 4),
              sk.box(106, y+35, 544*med["days_remaining"]/30, 7, ORANGE if urgent else GREEN, 4)]
    n += [sk.box(712, 202, 278, 236, INK, 20), lab("提前 14 天提醒", 734, 226, 234, 30, 20, LIME, True),
          lab("Metformin", 734, 274, 234, 28, 18, WHITE, True), lab("40片 ÷ 每日2片 = 20天", 734, 308, 234, 28, 14, "#DCE6DA"),
          lab("进入提醒范围", 734, 356, 234, 28, 16, WHITE, True), pill("待申请", 734, 392, 100, LIME, INK, 12, 28),
          sk.box(712, 458, 278, 232, WHITE, 20), lab("补药申请", 734, 480, 230, 28, 20, INK, True),
          lab("Metformin 500 mg · 40片", 734, 518, 230, 40, 14, MUTED),
          lab("榆树药店 · 待确认", 734, 564, 230, 28, 14, INK, True),
          button("提交给药店", 734, 620, 234, 48, GREEN, WHITE, 15),
          demo_footer(w, 724)]
    return sk.snapshot(w, h, n, "#EEF2EA")


def case07():
    w, h = 1440, 1000
    n = [sk.box(0, 0, w, h, "#F1EEE6"), brand(44, 32), pill("交接模式", 1160, 38, 220, MINT, GREEN, 14, 38),
          lab("今晚，换一个人接手", 44, 106, 900, 58, 40, INK, True),
          lab("19:30 林岚 → 林澄 · 只交接记录与跟进，不改变父亲的决定权。", 44, 166, 1100, 32, 18, MUTED)]
    n += [sk.box(44, 236, 790, 608, WHITE, 22), lab("接手清单", 72, 264, 500, 34, 24, INK, True),
          pill("3 项", 716, 264, 90, MINT, GREEN, 13, 30)]
    tasks = [
        ("21:00", "Atorvastatin 状态待确认", "停用待医生确认 · 已暂停自动提醒", "待确认", ORANGE),
        ("今天", "09:40 漏服记录跟进", "已联系药师 · 等待回复", "进行中", ORANGE),
        ("明天", "门诊问题摘要", "Metformin 数量、停用状态", "待携带", BLUE),
    ]
    for i, (time, title, detail, status, color) in enumerate(tasks):
        y = 328 + i*148
        n += [sk.box(72, y, 734, 124, "#F4F6F0", 16), pill(time, 90, y+18, 92, color, WHITE, 12, 28),
              lab(title, 202, y+14, 410, 30, 20, INK, True), lab(detail, 202, y+50, 480, 28, 15, MUTED),
              pill(status, 654, y+18, 128, WHITE, color, 12, 30),
              lab("负责人：林澄" if i == 0 else "负责人：林岚 → 林澄", 202, y+84, 480, 24, 13, color, True)]
    n += [button("林澄确认接手", 72, 784, 734, 44, GREEN, WHITE, 16)]
    n += [sk.box(866, 236, 530, 302, INK, 22), lab("交接时间线", 894, 264, 450, 32, 23, WHITE, True)]
    timeline = [("19:12", "林建国确认共享权限"), ("19:24", "林岚整理 3 项未完成"), ("19:30", "等待林澄确认接手")]
    for i, (time, event) in enumerate(timeline):
        y = 326 + i*62
        n += [sk.circle(902, y+12, 6, LIME), lab(time, 924, y-2, 76, 26, 14, LIME, True),
              lab(event, 1004, y-2, 356, 28, 15, WHITE)]
        if i < 2:
            n += [sk.box(899, y+20, 3, 43, "#54726A")]
    n += [sk.box(866, 562, 530, 282, WHITE, 22), lab("交接摘要", 894, 588, 450, 30, 22, INK, True),
          lab("• 5 项药品清单保持一致\n• 1 项漏服记录等待药师回复\n• 2 个问题将在门诊确认", 894, 632, 450, 108, 16, MUTED),
          lab("父亲可查看并撤回共享", 894, 772, 450, 28, 14, GREEN, True), demo_footer(w, 966)]
    return sk.snapshot(w, h, n, "#F1EEE6")


def case08():
    w, h = 430, 932
    n = [sk.box(0, 0, w, h, PAPER), phone_status(w), brand(22, 54, compact=True),
          lab("就诊摘要", 22, 116, 386, 46, 30, INK, True),
          lab("给医生看的 1 页 · 11月24日更新", 22, 162, 386, 28, 14, MUTED),
          sk.box(22, 210, 386, 88, INK, 18), lab("林建国 · 72岁", 42, 222, 260, 30, 21, WHITE, True),
          lab("过敏：青霉素（演示记录）", 42, 258, 320, 24, 14, LIME, True)]
    n += [lab("当前清单 · 5 项", 22, 322, 386, 30, 18, INK, True)]
    for i, med in enumerate(MEDS):
        y = 362 + i*60
        n += [sk.box(22, y, 386, 52, WHITE, 12), med_icon(med, 34, y+14, .58),
              lab(f'{med["name"]} {med["strength"]}', 78, y+3, 220, 23, 14, INK, True),
              lab("停用待医生确认" if med["id"] == "M03" else med["schedule"], 78, y+27, 300, 18, 10, RED if med["id"] == "M03" else MUTED, med["id"] == "M03")]
    n += [sk.box(22, 678, 386, 120, PALE_ORANGE, 16), lab("最近异常 · 09:40 家属报告", 40, 692, 350, 26, 16, RED, True),
          lab("Metformin 早晨项目未确认；是否补服尚待药师回复。", 40, 724, 350, 44, 14, INK),
          button("分享给本次门诊 · 24小时失效 · 可撤回", 22, 806, 386, 42, GREEN, WHITE, 12),
          lab("01  Metformin 家中数量为何不同？\n02  Atorvastatin 是否已停用？", 22, 856, 386, 52, 13, MUTED),
          demo_footer(w, 918)]
    return sk.snapshot(w, h, n, PAPER)


def case09():
    w, h = 390, 844
    n = [sk.box(0, 0, w, h, "#E8EEE6"), phone_status(w), brand(22, 52, compact=True),
          lab("取药后再核对", 22, 112, 346, 44, 28, INK, True),
          lab("榆树药店 · 演示取药凭证", 22, 158, 346, 26, 14, MUTED)]
    n += [sk.box(22, 206, 346, 220, WHITE, 20)]
    qx, qy, cell = 134, 228, 12
    pattern = ["11111110101", "10000010110", "10111010001", "10101011101", "10111010011", "10000010000", "11111110111", "10110000101", "11101011101", "10001010011", "11111110101"]
    for row, bits in enumerate(pattern):
        for col, bit in enumerate(bits):
            if bit == "1":
                n.append(sk.box(qx+col*cell, qy+row*cell, cell, cell, INK))
    n += [lab("CF-DEMO-024", 70, 372, 250, 24, 14, INK, True, "CENTER"), lab("演示码 · 不可用于真实交易", 70, 396, 250, 18, 10, MUTED, False, "CENTER")]
    n += [sk.box(22, 448, 346, 142, WHITE, 18), med_icon(MEDS[1], 42, 474, .85),
          lab("Metformin 500 mg", 108, 462, 236, 28, 19, INK, True), lab("申请数量：40片 · 已备妥（演示）", 108, 496, 236, 26, 13, MUTED),
          check(324, 472, GREEN, 28), lab("药袋数量已核对", 108, 540, 236, 24, 13, GREEN, True)]
    n += [sk.box(22, 612, 346, 104, PALE_ORANGE, 18), icon_circle("!", 42, 636, ORANGE, WHITE, 34),
          lab("标签字迹待药师核对", 92, 626, 252, 28, 18, RED, True),
          lab("先不更改服用方式，请药师现场确认。", 92, 660, 252, 40, 13, RED),
          button("请药师核对标签", 22, 740, 346, 52, GREEN, WHITE, 17), demo_footer(w, 822)]
    return sk.snapshot(w, h, n, "#E8EEE6")


def case10():
    w, h = 1180, 820
    n = [sk.box(0, 0, w, h, "#F2EFE6"), brand(36, 28),
          lab("本周只看需要处理的事", 36, 96, 840, 50, 35, INK, True),
          lab("11月18日—24日 · 不计算‘健康分’，不评价家人是否尽责。", 36, 150, 900, 30, 16, MUTED),
          pill("3 件待跟进", 952, 106, 192, PALE_ORANGE, RED, 14, 38)]
    cards = [
        (36, "01", "确认 Metformin 数量", "家中32片，门诊记录40片", "林岚 · 就诊时问", ORANGE),
        (424, "02", "等待药师回复", "09:40漏服记录已提交", "林澄 · 今天跟进", BLUE),
        (812, "03", "检查共享授权", "林建国可查看与撤销", "林建国 · 本周确认", GREEN),
    ]
    for x, num, title, detail, owner, color in cards:
        n += [sk.box(x, 222, 332, 226, WHITE, 20), icon_circle(num, x+22, 244, color, WHITE, 42),
              lab(title, x+22, 304, 288, 34, 20, INK, True), lab(detail, x+22, 346, 288, 38, 14, MUTED),
              lab(owner, x+22, 402, 288, 26, 13, color, True)]
    n += [sk.box(36, 480, 1108, 238, INK, 20), lab("这一周发生了什么", 64, 504, 700, 32, 22, WHITE, True)]
    events = [("周一", "建立 5 项清单", GREEN), ("周二", "发现 2 处差异", ORANGE), ("今天", "记录并联系药师", BLUE), ("明天", "复诊时确认", GREEN)]
    n += [sk.box(100, 602, 940, 4, "#5B756B")]
    for i, (day, event, color) in enumerate(events):
        x = 100 + i*310
        n += [sk.circle(x, 604, 11, color), lab(day, x-36, 550, 100, 28, 15, LIME, True),
              lab(event, x-36, 632, 176, 28, 15, WHITE)]
    n += [lab("记录来自家属操作，不代表服药结果或健康改善。", 64, 682, 900, 24, 12, "#D2DED3"), demo_footer(w, 760)]
    return sk.snapshot(w, h, n, "#F2EFE6")


BUILDERS = {f"B05-case-{i:02d}": fn for i, fn in enumerate(
    [case01, case02, case03, case04, case05, case06, case07, case08, case09, case10], 1)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--version", default="v001")
    args = parser.parse_args()
    selected = list(BUILDERS) if args.all else [args.case]
    for cid in selected:
        if cid not in BUILDERS:
            raise SystemExit(f"Unknown case: {cid}")
        case = next(c for c in plan["cases"] if c["id"] == cid)
        image, record = ck.render_case(TASK, case, BUILDERS[cid](), args.version)
        ck.record_view(TASK, case, image, args.version, "待视觉检查", "首次渲染；尚未作出通过判断。", "基线", False, "baseline")
        print(json.dumps({"case": cid, "version": args.version, "image": sk.rel(image), "request": record["request_id"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
