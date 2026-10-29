#!/usr/bin/env python3
"""B06 — ten redesigned everyday-information artifacts."""
import json, os, math
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN = SCRIPT.parents[2].name
OUT = SUITE / 'outputs' / RUN / 'B06'
TMP = SUITE / 'tmp' / RUN / 'B06'
D = json.loads((TMP / 'data.json').read_text(encoding='utf-8'))

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def T(txt, size, color="#1B1A17", bold=False, extra="", fam="Noto Sans CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'
def Tm(txt, size, color="#1B1A17", bold=False, extra=""):
    return T(txt, size, color, bold, extra, "Noto Sans Mono CJK SC")
def t(x, y, txt, size, color="#1B1A17", bold=False, extra="", w=None):
    wd = f' width="{w}"' if w else ""
    return f'<Positioned left="{x}" top="{y}"{wd}>' + T(txt, size, color, bold, extra) + '</Positioned>'
def tm(x, y, txt, size, color="#1B1A17", bold=False):
    return f'<Positioned left="{x}" top="{y}">' + Tm(txt, size, color, bold) + '</Positioned>'
def r(x, y, w, h, color, rad=0, border=None):
    b = f' border="{border}"' if border else ""
    return f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}"><Container width="{w}" height="{h}" color="{color}" borderRadius="{rad}"{b}/></Positioned>'
def card(x, y, w, h, color="#FFFDF8", rad=12, border="1 SOLID #D8CFC0"):
    return r(x, y, w, h, color, rad, border)
def line(x, y, w, color="#D8CFC0", h=1):
    return r(x, y, w, h, color)
def circle(x, y, d, color):
    return f'<Positioned left="{x}" top="{y}" width="{d}" height="{d}"><ClipOval><Container width="{d}" height="{d}" color="{color}"/></ClipOval></Positioned>'
def dotted(x, y, w, color="#B9B1A3"):
    return "".join(r(x + i * 8, y, 4, 2, color, 1) for i in range(int(w // 8)))
def page(w, h, bg="#F4EFE6"):
    return f'<Snapshot background="{bg}" type="png"><Container width="{w}" height="{h}"><Stack alignment="TOP_LEFT"><Container width="{w}" height="{h}" color="{bg}"/>'
def end(): return '</Stack></Container></Snapshot>'
def write(cid, w, h, body, bg="#F4EFE6"):
    d = OUT / f"case-{cid:02d}"; d.mkdir(parents=True, exist_ok=True)
    (d / 'final.snapshot').write_text(page(w, h, bg) + "".join(body) + end(), encoding='utf-8')

# ---------- 01 parking ----------
def c01():
    W, H = 620, 920
    INK = "#18231C"; METAL = "#E7E1D2"; LEAF = "#2F6B4F"; RED = "#B3402C"
    AMBER = "#C98A1E"; BLUE = "#1F4E79"; MUT = "#6C6A60"
    b = [r(0, 0, 620, 920, METAL, 0), r(0, 0, 620, 10, INK, 0), r(0, 910, 620, 10, INK, 0)]
    b.append(t(40, 36, "梧桐路 12–28 号", 17, INK, True))
    b.append(t(40, 62, "路侧停车 · 周二", 12, MUT))
    b.append(circle(522, 34, 58, BLUE))
    b.append(t(522, 46, "P", 30, "#FFFFFF", True, w=58, extra=' textAlign="CENTER"'))
    b.append(tm(40, 96, "14:20", 72, INK, True))
    b.append(t(300, 120, "周二", 18, MUT, True))
    b.append(t(300, 144, "现在", 11, MUT))
    b.append(t(40, 196, "可以停", 60, LEAF, True))
    b.append(t(40, 272, "最长到 16:20 驶离", 26, INK, True))
    b.append(t(40, 314, D['parking']['reason'], 13, MUT, w=540))
    # ruler
    x0, step = 40, 22.5
    for h in range(0, 25, 3):
        xx = x0 + h * step
        b.append(t(int(xx) - 6, 370, str(h), 10, MUT))
        b.append(r(int(xx), 390, 1, 8, "#A9A294"))
    b.append(line(x0, 400, 540, "#7C776B", 2))
    nowx = x0 + (14 + 20 / 60) * step
    b.append(r(int(nowx) - 1, 358, 3, 52, RED, 1))
    rules = [("清扫", [8], [10], "#B3402C", "周二 08:00–10:00 禁止停车"),
             ("装卸", [7], [9], "#C98A1E", "每日 07:00–09:00 货车装卸"),
             ("居民证", [0, 18], [8, 24], "#1F4E79", "18:00–次日 08:00 仅居民证"),
             ("限时", [9], [18], "#2F6B4F", "09:00–18:00 最长 2 小时")]
    for i, (lab, starts, ends, col, txt) in enumerate(rules):
        y = 430 + i * 66
        b.append(t(40, y, lab, 12, INK, True))
        b.append(t(100, y + 1, txt, 10, MUT))
        b.append(r(40, y + 22, 540, 10, "#D2CCBE", 5))
        for s, e in zip(starts, ends):
            w = (e - s) * step
            b.append(r(int(40 + s * step), y + 22, int(w), 10, col, 5))
            b.append(r(int(nowx) - 1, y + 19, 2, 16, RED, 1))
    b.append(card(40, 700, 540, 158, "#F6F2E7", 10, "1 SOLID #C9C2B3"))
    b.append(t(56, 714, "为什么", 10, MUT, True, ' letterSpacing="1"'))
    why = ["现在 14:20：不在清扫、装卸或居民证时段。", "限时 2 小时从 09:00 起算，因此最晚 16:20。", "18:00 后需要居民证；周日与法定节假日除外。"]
    for i, w in enumerate(why):
        b.append(t(56, 736 + i * 28, "— " + w, 12, INK))
    b.append(t(40, 876, "示例规则 · 以现场标志与当地规定为准", 9, MUT))
    return b

# ---------- 02 payslip ----------
def c02():
    W, H = 1240, 1754
    INK = "#1E1D1A"; PAPER = "#FBF7EF"; BLUE = "#245D8C"; RED = "#B23A2E"
    MUT = "#746E65"; GREEN = "#3F6B4F"; PALE = "#EDE6D8"
    b = [r(0, 0, W, H, PAPER, 0), line(80, 60, 1080, INK, 3)]
    b.append(t(80, 82, "工资单", 14, INK, True, ' letterSpacing="2"'))
    b.append(t(80, 106, "2026 年 9 月 · 演示", 10, MUT))
    b.append(t(900, 82, "林先生 / 编号 302-091", 10, MUT))
    b.append(t(80, 150, "实发", 12, MUT))
    b.append(tm(80, 170, "¥13,415", 64, INK, True))
    b.append(t(80, 248, "比上月少 ¥212", 14, RED, True))
    b.append(t(270, 250, "加班 +620 · 个税档位 −832", 11, MUT))
    # stacked bar
    b.append(t(80, 300, "应发 ¥18,000 的去向", 11, MUT, True, ' letterSpacing="1"'))
    b.append(r(80, 326, 1080, 88, "#EFE9DC", 8))
    segs = [(13415 / 18000 * 1080, GREEN, "实发 74.5%"), (1890 / 18000 * 1080, BLUE, ""),
            (2160 / 18000 * 1080, "#6C8FA8", ""), (535 / 18000 * 1080, RED, "")]
    xx = 80
    for w, col, lab in segs:
        b.append(r(int(xx), 326, int(w) + 1, 88, col, 6))
        if lab:
            b.append(t(int(xx) + 20, 356, lab, 16, "#FFFFFF", True))
        xx += w
    for i, (name, col) in enumerate([("实发 13,415", GREEN), ("社保 1,890", BLUE), ("公积金 2,160", "#4B728A"), ("个税 535", RED)]):
        x = 80 + i * 170
        b.append(circle(x, 433, 8, col))
        b.append(t(x + 14, 430, name, 10, col, True))
    # deduction cards
    b.append(t(80, 478, "钱去哪了", 11, MUT, True, ' letterSpacing="1"'))
    cards = [("社保", "¥1,890", "10.5%", "养老、医疗、失业等个人缴纳部分。", BLUE),
             ("公积金", "¥2,160", "12%", "进入个人公积金账户，可用于租房/购房。", "#4B728A"),
             ("个税", "¥535", "3.0%", "按累计预扣法计算；档位变化会直接影响到手。", RED)]
    for i, (name, val, pct, why, col) in enumerate(cards):
        x = 80 + i * 365
        b.append(card(x, 504, 340, 154, "#FFFDF8", 10))
        b.append(r(x, 504, 6, 154, col, 3))
        b.append(t(x + 22, 520, name, 11, MUT, True))
        b.append(tm(x + 22, 540, val, 28, INK, True))
        b.append(t(x + 190, 548, pct, 12, col, True))
        b.append(t(x + 22, 586, why, 9, MUT, w=296))
        b.append(t(x + 22, 624, "在工资单第 " + str(i + 1) + " 项核对", 9, col, True))
    # employer
    b.append(card(80, 690, 1080, 132, "#EAE3D5", 10, None))
    b.append(t(104, 706, "雇主实际付出", 11, MUT, True, ' letterSpacing="1"'))
    b.append(tm(104, 726, "¥22,320", 34, INK, True))
    b.append(t(360, 734, "= 应发 18,000 + 单位缴纳 4,320", 12, MUT))
    b.append(t(104, 780, "谈薪时看“应发”，算成本时看“雇主付出”；两者不是一回事。", 10, MUT))
    # month change
    b.append(t(80, 858, "为什么比上月少", 11, MUT, True, ' letterSpacing="1"'))
    b.append(card(80, 884, 1080, 168, "#FFFDF8", 10))
    changes = [("加班 8 小时", "+620", GREEN), ("专项附加扣除", "0", MUT), ("累计个税进入 10% 档", "−832", RED)]
    for i, (name, delta, col) in enumerate(changes):
        y = 902 + i * 44
        b.append(t(104, y, name, 12, INK))
        b.append(tm(980, y - 2, delta, 16, col, True))
        if i < 2:
            b.append(line(104, y + 28, 1010, "#EDE6D8"))
    # glossary
    b.append(t(80, 1090, "三个词看懂", 11, MUT, True, ' letterSpacing="1"'))
    gloss = [("应发", "扣款前的工资总额。"), ("缴费基数", "社保/公积金按这个数乘比例。"), ("专项附加扣除", "房租、赡养等可抵税额度。")]
    for i, (head, body) in enumerate(gloss):
        x = 80 + i * 365
        b.append(t(x, 1120, head, 16, INK, True))
        b.append(t(x, 1146, body, 10, MUT, w=320))
    b.append(card(80, 1230, 1080, 250, "#F1EADB", 12, None))
    b.append(t(104, 1250, "这张单子回答三个问题", 12, BLUE, True, ' letterSpacing="1"'))
    qs = ["到手多少？13,415。", "为什么少了？社保、公积金、个税，各自可核对。", "公司为我花了多少？22,320。"]
    for i, q in enumerate(qs):
        b.append(t(104, 1284 + i * 44, q, 16, INK, True))
    b.append(t(104, 1418, "对不上时：先查考勤与专项扣除，再向 HR 要缴费明细。", 9, MUT))
    b.append(line(80, 1560, 1080, "#D8CFC0"))
    b.append(t(80, 1580, "演示计算，不是税务或社保建议；比例与税率以当地当期规定为准。", 9, MUT))
    b.append(t(80, 1610, "工资单 · 2026-09 · 第 1 页 / 共 1 页", 9, MUT))
    return b

# ---------- 03 electricity ----------
def c03():
    W, H = 1200, 1500
    BG = "#0F1A1B"; INK = "#F1EBDD"; MUT = "#9DA99E"; AMBER = "#E0A32E"; GREEN = "#5FA37A"; RED = "#D9614A"
    b = [r(0, 0, W, H, BG, 0)]
    b.append(t(80, 70, "2026 年 9 月 · 家庭电费", 12, MUT, True, ' letterSpacing="2"'))
    b.append(t(80, 100, "你家的电，", 44, INK, True))
    b.append(t(80, 154, "什么时候最贵？", 44, INK, True))
    b.append(tm(80, 230, "¥173.34", 58, AMBER, True))
    b.append(t(80, 306, "320 kWh · 30 天 · 峰谷电价演示", 12, MUT))
    # legend
    b.append(circle(760, 240, 10, AMBER)); b.append(t(778, 236, "峰段 08:00–22:00", 11, MUT))
    b.append(circle(760, 266, 10, GREEN)); b.append(t(778, 262, "谷段 22:00–08:00", 11, MUT))
    # chart
    x0, step, bw = 90, 42, 34
    base = 840
    b.append(r(x0 + 8 * step, 360, 14 * step, 500, "#E0A32E14", 0))
    b.append(r(x0, 360, 8 * step, 500, "#5FA37A10", 0))
    b.append(r(x0 + 22 * step, 360, 2 * step, 500, "#5FA37A10", 0))
    for h, v in enumerate(D['electricity']['hourly']):
        hh = int(v / 30 * 300)
        col = AMBER if 8 <= h < 22 else GREEN
        b.append(r(x0 + h * step, base - hh, bw, hh, col, 3))
    b.append(line(x0, base, 24 * step, "#5B6660", 1))
    for h in range(0, 25, 3):
        b.append(t(x0 + h * step - 6, base + 14, str(h), 10, MUT))
    b.append(t(90, 890, "每小时用电量（kWh）· 最高 30", 10, MUT))
    # highlight 19
    hx = x0 + 19 * step
    b.append(circle(hx + 10, 480, 10, RED))
    b.append(t(hx - 60, 448, "19:00 · 30 kWh", 12, RED, True))
    b.append(r(hx + 15, 494, 1, 46, RED))
    # shift card
    b.append(card(80, 910, 1040, 128, "#1B2928", 12, "1 SOLID #384642"))
    b.append(t(104, 928, "把 2 度电从 19:00 挪到 23:00", 20, INK, True))
    b.append(t(104, 960, "洗衣服/洗碗改到 23:00 后，峰段少 60 kWh/月。", 11, MUT))
    b.append(tm(760, 930, "−¥18.60", 34, AMBER, True))
    b.append(t(760, 976, "每月 · 一年 ¥223.20", 11, MUT))
    # composition
    b.append(t(80, 1090, "账单由三块组成", 11, MUT, True, ' letterSpacing="1"'))
    total = 173.34
    w1 = 129.57 / total * 1040; w2 = 33.77 / total * 1040
    b.append(r(80, 1120, 1040, 28, "#2A3633", 6))
    b.append(r(80, 1120, int(w1), 28, AMBER, 6))
    b.append(r(80 + int(w1), 1120, int(w2), 28, GREEN, 6))
    rows = [("峰段电费", "¥129.57", "210 kWh × 0.617", AMBER), ("谷段电费", "¥33.77", "110 kWh × 0.307", GREEN), ("固定费用", "¥10.00", "按账单周期", "#8C9690")]
    for i, (name, val, calc, col) in enumerate(rows):
        x = 80 + i * 350
        b.append(circle(x, 1178, 8, col))
        b.append(t(x + 18, 1172, name, 11, INK, True))
        b.append(tm(x + 18, 1194, val, 18, INK, True))
        b.append(t(x + 110, 1199, calc, 9, MUT))
    b.append(t(80, 1270, "为什么晚上贵：18:00–21:00 是用电高峰，发电成本更高。", 13, INK))
    b.append(t(80, 1300, "把可延迟的家务挪到 23:00 后，比“少用”更容易执行。", 11, MUT))
    b.append(line(80, 1360, 1040, "#384642"))
    b.append(t(80, 1380, "演示电价与用电曲线；实际以当地供电公司账单为准。", 9, MUT))
    b.append(t(80, 1410, "余电 · 家庭账单重构 03 / 10", 9, "#6F7C75"))
    return b

# ---------- 04 prescription ----------
def c04():
    W, H = 1000, 700
    BG = "#FAF7F0"; INK = "#22201C"; MUT = "#746F66"; LEAF = "#3F6B4F"
    b = [r(0, 0, W, H, BG, 0)]
    b.append(t(40, 30, "一周药卡", 30, INK, True))
    b.append(t(40, 70, "林先生 · 58 岁 · 10/26–11/01", 11, MUT))
    b.append(t(760, 34, "按医生处方", 11, LEAF, True))
    b.append(t(760, 54, "不要自行调整剂量", 9, MUT))
    days = D['prescription']['days']
    x0 = 270
    for i, d in enumerate(days):
        b.append(t(x0 + i * 100, 108, "周" + d, 11, MUT, True, w=100, extra=' textAlign="CENTER"'))
    meds = D['prescription']['meds']
    for j, m in enumerate(meds):
        y = 140 + j * 94
        b.append(r(40, y, 210, 80, "#FFFFFF", 8, "1 SOLID #E4DCCD"))
        b.append(r(40, y, 6, 80, m['color'], 3))
        b.append(t(56, y + 10, m['name'], 14, INK, True))
        b.append(t(56, y + 32, m['dose'] + " · " + " / ".join(m['times']), 9, MUT))
        b.append(t(56, y + 50, ("随餐" if m['food'] == "随餐" else "不限"), 9, m['color'], True))
        for i in range(7):
            cx = x0 + i * 100
            b.append(r(cx, y, 92, 80, "#FFFFFF", 8, "1 SOLID #E4DCCD"))
            if len(m['times']) == 2:
                for k, lab in enumerate(["早", "晚"]):
                    xx = cx + 18 + k * 40
                    done = (i < 2 and k == 0) or (i == 0 and k == 1)
                    if done:
                        b.append(circle(xx, y + 40, 18, m['color']))
                        b.append(circle(xx + 6, y + 46, 6, "#FFFFFF"))
                    else:
                        b.append(f'<Positioned left="{xx}" top="{y+40}" width="18" height="18"><Container width="18" height="18" color="transparent" borderRadius="9" border="1.5 SOLID #C9C0B0"/></Positioned>')
                    b.append(t(xx - 2, y + 20, lab, 8, MUT))
            else:
                xx = cx + 37
                done = i < 2
                if done:
                    b.append(circle(xx, y + 30, 20, m['color']))
                    b.append(circle(xx + 7, y + 37, 6, "#FFFFFF"))
                else:
                    b.append(f'<Positioned left="{xx}" top="{y+30}" width="20" height="20"><Container width="20" height="20" color="transparent" borderRadius="10" border="1.5 SOLID #C9C0B0"/></Positioned>')
    b.append(t(40, 522, "实心 = 已服；空心 = 待服。橙色标签 = 随餐。", 10, MUT))
    b.append(card(40, 556, 920, 80, "#F0E9DA", 10, None))
    b.append(t(56, 570, "早 07:00 有两种药；具体顺序按医生或药师交代。", 11, INK))
    b.append(t(56, 594, "出门时拍一张，药盒丢了也能核对。", 9, MUT))
    b.append(t(40, 662, "处方示例，不构成用药建议；剂量与时间以医生处方为准。", 8, MUT))
    return b

# ---------- 05 train transfer ----------
def c05():
    W, H = 1080, 1920
    BG = "#0D1519"; INK = "#F4F1E8"; MUT = "#9BA8AB"; RED = "#E05038"; GREEN = "#5FA37A"; AMBER = "#F2C230"
    b = [r(0, 0, W, H, BG, 0)]
    b.append(t(80, 56, "杭州东站 · 换乘判断", 13, MUT, True, ' letterSpacing="2"'))
    b.append(t(760, 56, "14:32 · 实时演示", 11, MUT))
    b.append(t(80, 120, "赶不上", 110, RED, True))
    b.append(t(80, 280, "别跑，G1505 已停止检票。", 30, INK, True))
    b.append(t(80, 330, "到站 14:32，步行 6 分钟，最近一班 15:02。", 15, MUT))
    xline = 300
    b.append(r(xline, 430, 4, 620, "#334246", 2))
    nodes = [("G1505", "14:31 停止检票", "在你到站之前", RED, 460, "right"),
             ("G712", "14:32 到达", "8 站台", GREEN, 640, "left"),
             ("G1505", "14:36 开车 · 12 站台", "已经开走", RED, 820, "right"),
             ("步行", "步行 6 分钟", "14:38 才到 12 站台", AMBER, 1000, "left")]
    for code, main, sub, col, y, side in nodes:
        b.append(circle(xline - 14, y - 14, 32, col))
        b.append(circle(xline - 6, y - 6, 16, BG))
        if side == "right":
            b.append(t(360, y - 34, code, 12, MUT, True))
            b.append(t(360, y - 12, main, 26, INK, True))
            b.append(t(360, y + 24, sub, 12, MUT))
        else:
            b.append(t(80, y - 34, code, 12, MUT, True))
            b.append(t(80, y - 12, main, 26, INK, True))
            b.append(t(80, y + 24, sub, 12, MUT))
    b.append(card(80, 1140, 920, 250, "#152226", 16, "1 SOLID #334246"))
    b.append(t(108, 1160, "下一班", 11, AMBER, True, ' letterSpacing="2"'))
    b.append(tm(108, 1182, "15:02", 70, INK, True))
    b.append(t(360, 1188, "12 站台 · 同站台，不用换层", 16, INK, True))
    b.append(t(360, 1220, "还有 30 分钟；先在 12 站台等。", 13, MUT))
    b.append(r(108, 1300, 240, 54, AMBER, 10))
    b.append(t(108, 1314, "去 12 站台", 14, "#1B1A17", True, w=240, extra=' textAlign="CENTER"'))
    b.append(t(376, 1314, "改签窗口在 B1 层 · 演示指引", 11, MUT))
    b.append(t(80, 1450, "为什么赶不上", 11, MUT, True, ' letterSpacing="1"'))
    why = ["到站 14:32；G1505 停止检票 14:31。", "步行到 12 站台要 6 分钟，最快 14:38。", "下一班 15:02 同站台，不必出站。"]
    for i, w in enumerate(why):
        b.append(t(80, 1482 + i * 34, "— " + w, 15, INK))
    b.append(card(80, 1620, 920, 100, "#152226", 12, "1 SOLID #334246"))
    b.append(t(100, 1636, "如果你还是想跑", 11, MUT, True))
    b.append(t(100, 1660, "14:38 到站台时，检票已关闭 7 分钟；不要翻越或冲门。", 13, INK))
    b.append(t(80, 1800, "演示时刻与站台信息；以车站实时屏与工作人员指引为准。", 9, MUT))
    b.append(t(80, 1830, "换乘判断 05 / 10", 9, "#6F7E82"))
    return b

# ---------- 06 recall ----------
def c06():
    W, H = 800, 1100
    BG = "#F8F5EE"; INK = "#201E1A"; RED = "#B3261E"; MUT = "#6F6A60"; PALE = "#EFE8DB"
    b = [r(0, 0, W, H, BG, 0), r(0, 0, W, 14, RED, 0)]
    b.append(t(60, 50, "产品召回 · 演示", 12, RED, True, ' letterSpacing="2"'))
    b.append(t(60, 78, D['recall']['brand'], 13, MUT))
    b.append(t(60, 100, "原味酸奶 100g × 4", 34, INK, True))
    b.append(t(60, 152, "先看盒盖第二行，再决定要不要扔。", 15, INK))
    b.append(t(60, 202, "批号刻度", 10, MUT, True, ' letterSpacing="1"'))
    codes = D['recall']['batch_all']
    for i, code in enumerate(codes):
        col = i % 6
        row = i // 6
        x = 60 + col * 112
        y = 230 + row * 92
        affected = code in ['A7', 'A8', 'A9']
        if affected:
            b.append(r(x, y, 92, 72, RED, 8))
            b.append(tm(x, y + 20, code, 24, "#FFFFFF", True))
        else:
            b.append(r(x, y, 92, 72, "#FFFFFF", 8, "1 SOLID #D8CFC0"))
            b.append(tm(x, y + 20, code, 24, "#A39B8D"))
    b.append(t(60, 424, "A7–A9 受影响", 34, RED, True))
    b.append(t(60, 468, "如果你的盒盖批号在这三个里：", 13, MUT))
    steps = [("01", "停止食用", "不要尝味道，整盒放回冰箱。"),
             ("02", "拍下盒盖", "保留批号与购买小票。"),
             ("03", "带回门店退款", "截止 2026-11-30。")]
    for i, (num, head, body) in enumerate(steps):
        y = 520 + i * 128
        b.append(tm(60, y, num, 26, RED, True))
        b.append(t(120, y - 2, head, 22, INK, True))
        b.append(t(120, y + 34, body, 11, MUT, w=560))
        b.append(line(60, y + 96, 680, "#E6DED1"))
    b.append(card(60, 920, 680, 86, PALE, 10, None))
    b.append(t(78, 936, "原因：部分杯盖密封不良，可能出现胀包。", 12, INK))
    b.append(t(78, 962, "客服 400-000-0000（演示）· 门店原路退款。", 10, MUT))
    b.append(t(60, 1042, "虚构品牌与召回，用于演示批号定位与行动卡设计。", 9, MUT))
    return b

# ---------- 07 lease ----------
def c07():
    W, H = 1240, 1754
    BG = "#F6F1E6"; INK = "#1F2A2E"; MUT = "#6F6A60"; YEL = "#F2D06B"; RED = "#B23A2E"; GREEN = "#3F6B4F"
    b = [r(0, 0, W, H, BG, 0)]
    b.append(t(80, 66, "签字前，", 42, INK, True))
    b.append(t(80, 120, "先看这 5 行。", 42, INK, True))
    b.append(t(80, 186, "梧桐里 7 号楼 302（虚构）· 月租 ¥6,800 · 演示租约", 11, MUT))
    b.append(t(980, 72, "别急着签", 11, RED, True))
    for i, c in enumerate(D['lease']['clauses']):
        y = 250 + i * 160
        b.append(tm(80, y, f"0{i+1}", 16, RED, True))
        b.append(r(120, y + 2, 300, 26, YEL, 2))
        b.append(t(126, y, c['head'], 18, INK, True))
        b.append(t(120, y + 40, c['plain'], 12, INK, w=640))
        b.append(t(120, y + 74, "要问：" + c['ask'], 10, RED, w=640))
        if i < 4:
            b.append(line(80, y + 128, 680, "#DCD3C4"))
    b.append(card(820, 250, 340, 700, "#FFFDF8", 12))
    b.append(t(844, 270, "签字当天要付", 10, MUT, True, ' letterSpacing="1"'))
    b.append(tm(844, 292, "¥20,400", 34, INK, True))
    b.append(t(844, 340, "押二 13,600 + 首月 6,800", 10, MUT))
    b.append(line(844, 374, 292, "#E6DED1"))
    b.append(t(844, 394, "第二年月租", 10, MUT, True))
    b.append(tm(844, 416, "¥7,140", 26, RED, True))
    b.append(t(844, 454, "按每年 5% 上调", 9, MUT))
    b.append(line(844, 486, 292, "#E6DED1"))
    b.append(t(844, 506, "提前退租", 10, MUT, True))
    b.append(tm(844, 528, "−¥6,800", 26, RED, True))
    b.append(t(844, 566, "未满 1 年扣 1 个月", 9, MUT))
    b.append(line(844, 598, 292, "#E6DED1"))
    b.append(t(844, 618, "维修响应", 10, MUT, True))
    b.append(tm(844, 640, "48h", 26, GREEN, True))
    b.append(t(844, 678, "非人为损坏；超时怎么办？", 9, MUT))
    b.append(line(844, 710, 292, "#E6DED1"))
    b.append(t(844, 730, "通知期", 10, MUT, True))
    b.append(tm(844, 752, "30 天", 26, INK, True))
    b.append(t(844, 790, "书面通知，别口头", 9, MUT))
    b.append(card(80, 1090, 1080, 180, "#FFFDF8", 12))
    b.append(t(104, 1108, "带着这 5 个问题去签约", 11, MUT, True, ' letterSpacing="1"'))
    qs = ["押金退还条件写清了吗？", "转租成功还扣违约金吗？", "维修超时能否自行处理？", "涨幅是否封顶？", "转租书面同意多久答复？"]
    for i, q in enumerate(qs):
        x = 104 + (i % 3) * 350
        y = 1138 + (i // 3) * 44
        b.append(t(x, y, "— " + q, 11, INK))
    b.append(t(80, 1320, "把“口头承诺”写进补充条款；签字前拍照留档。", 14, RED, True))
    b.append(card(80, 1370, 1080, 240, "#EFE7D6", 12, None))
    b.append(t(104, 1390, "这张卡怎么算的", 11, MUT, True, ' letterSpacing="1"'))
    calc = ["入住现金 = 2 个月押金 + 3 个月租金 = 20,400。", "第二年 = 6,800 × 1.05 = 7,140。", "提前退租 = 1 个月租金 = 6,800。"]
    for i, c in enumerate(calc):
        b.append(t(104, 1422 + i * 38, c, 12, INK))
    b.append(t(104, 1540, "以上为虚构条款；不构成法律建议，签约前请核对合同原件。", 9, MUT))
    b.append(t(80, 1650, "租约重构 07 / 10", 9, MUT))
    return b

# ---------- 08 recycling ----------
def c08():
    W, H = 900, 1200
    BG = "#F3F0E7"; INK = "#1E241F"; MUT = "#6E6A60"
    bins = D['recycling']['bins']
    b = [r(0, 0, W, H, BG, 0)]
    b.append(t(40, 36, "这栋楼只分三类", 36, INK, True))
    b.append(t(40, 84, "梧桐里 7 号楼 · 演示规则 · 12 件常见物品", 11, MUT))
    for i, bn in enumerate(bins):
        x = 40 + i * 280
        b.append(card(x, 122, 250, 142, "#FFFDF8", 10))
        b.append(r(x, 122, 250, 10, bn['color'], 4))
        b.append(t(x + 18, 146, bn['name'], 22, bn['color'], True))
        b.append(t(x + 18, 180, bn['hint'], 10, MUT, w=214))
    b.append(t(40, 300, "12 件东西，投哪个桶？", 13, INK, True))
    b.append(t(700, 301, "红点 = 最容易错", 9, "#B3261E", True))
    colmap = {bn['name']: bn['color'] for bn in bins}
    for i, it in enumerate(D['recycling']['items']):
        col = i % 3
        row = i // 3
        x = 40 + col * 280
        y = 340 + row * 176
        b.append(card(x, y, 250, 154, "#FFFDF8", 10))
        b.append(r(x, y, 6, 154, colmap[it['bin']], 3))
        b.append(t(x + 20, y + 18, it['name'], 15, INK, True, w=210))
        b.append(r(x + 20, y + 58, 74, 24, colmap[it['bin']], 12))
        b.append(t(x + 20, y + 63, it['bin'], 9, "#FFFFFF", True, w=74, extra=' textAlign="CENTER"'))
        if it['tone'] == 'warn':
            b.append(circle(x + 218, y + 18, 10, "#B3261E"))
        if it['bin'] == '其他':
            b.append(t(x + 20, y + 98, "分不清时投这里，别混进可回收。", 9, MUT, w=210))
        elif it['bin'] == '有害':
            b.append(t(x + 20, y + 98, "单独投放，不要破袋。", 9, MUT, w=210))
        else:
            b.append(t(x + 20, y + 98, "干净、干燥才可回收。", 9, MUT, w=210))
    b.append(card(40, 1060, 820, 72, "#EDE7D8", 10, None))
    b.append(t(58, 1076, "最常错：外卖盒有油 → 其他；酸奶杯要洗净才可回收；电池、灯管、药品 → 有害。", 11, INK, w=790))
    b.append(t(40, 1150, "演示楼栋规则；各地分类不同，以当地规定为准。", 9, MUT))
    return b

# ---------- 09 nutrition ----------
def c09():
    W, H = 800, 1200
    BG = "#FFF8EE"; INK = "#1D1B18"; RED = "#D6452E"; GREEN = "#3F6B4F"; MUT = "#6F6A60"
    b = [r(0, 0, W, H, BG, 0)]
    b.append(t(60, 46, "货架卡 · 演示", 10, RED, True, ' letterSpacing="2"'))
    b.append(t(60, 76, "一袋 =", 30, INK, True))
    b.append(t(60, 118, "7.5 茶匙糖", 62, RED, True))
    b.append(t(60, 200, "100g 整袋，不是一份", 18, MUT))
    # pack
    b.append(r(60, 258, 250, 320, "#F1E6D2", 12, "2 SOLID #D8C8AE"))
    b.append(r(60, 258, 250, 26, RED, 8))
    b.append(t(80, 300, "每日坚果麦片", 16, INK, True, w=210))
    b.append(t(80, 330, "100g · 演示产品", 10, MUT))
    for i, (col, rr) in enumerate([("#8A6A3B", 22), ("#C49A5A", 16), ("#6E8A5A", 18)]):
        b.append(circle(90 + i * 52, 400, rr * 2, col))
    b.append(t(80, 500, "燕麦 · 坚果 · 果干", 10, MUT))
    # right numbers
    b.append(t(360, 270, "整袋糖", 11, MUT, True))
    b.append(tm(360, 290, "30g", 44, RED, True))
    b.append(t(360, 350, "一份 40g 含 12g", 12, INK))
    b.append(t(360, 374, "4g 糖 ≈ 1 茶匙", 11, MUT))
    b.append(line(360, 410, 380, "#E6DAC6"))
    b.append(t(360, 430, "蛋白质", 10, MUT, True))
    b.append(tm(360, 448, "20g", 26, GREEN, True))
    b.append(t(360, 486, "纤维", 10, MUT, True))
    b.append(tm(360, 504, "12.5g", 26, GREEN, True))
    b.append(t(540, 448, "整袋", 9, MUT))
    b.append(t(540, 504, "整袋", 9, MUT))
    # spoons
    b.append(t(60, 620, "换成茶匙：", 12, MUT, True))
    for i in range(8):
        x = 60 + i * 88
        if i < 7:
            b.append(f'<Positioned left="{x}" top="655" width="56" height="26"><ClipOval><Container width="56" height="26" color="{RED}"/></ClipOval></Positioned>')
            b.append(r(x + 50, 664, 34, 7, RED, 3))
        else:
            b.append(f'<Positioned left="{x}" top="655" width="26" height="26"><ClipOval><Container width="26" height="26" color="{RED}"/></ClipOval></Positioned>')
            b.append(r(x + 22, 664, 24, 7, RED, 3))
    b.append(t(60, 700, "7 满匙 + 半匙（8 个位置示意）", 10, MUT))
    # comparison table
    b.append(t(60, 760, "每份 vs 整袋", 11, MUT, True, ' letterSpacing="1"'))
    rows = [("糖", "12g", "30g"), ("蛋白质", "8g", "20g"), ("纤维", "5g", "12.5g")]
    b.append(t(300, 792, "每份 40g", 9, MUT))
    b.append(t(580, 792, "整袋 100g", 9, MUT))
    for i, (name, a, c) in enumerate(rows):
        y = 820 + i * 58
        b.append(line(60, y, 680, "#E6DAC6"))
        b.append(t(60, y + 14, name, 13, INK, True))
        b.append(tm(320, y + 12, a, 18, INK, True))
        b.append(tm(600, y + 12, c, 18, RED if name == "糖" else INK, True))
    b.append(line(60, 996, 680, "#E6DAC6"))
    b.append(t(60, 1020, "“无添加蔗糖”不等于低糖；先看整袋，再看配料表。", 13, INK, True, w=680))
    b.append(t(60, 1080, "演示营养数据；4g 糖 ≈ 1 茶匙；以实际包装标示为准。", 9, MUT))
    b.append(t(60, 1130, "营养标签重构 09 / 10", 9, MUT))
    return b

# ---------- 10 subscriptions ----------
def c10():
    W, H = 1080, 1350
    BG = "#F3EEE4"; INK = "#1D2A3A"; MUT = "#6C6A62"; RED = "#B23A2E"; AMBER = "#D9A441"; GREEN = "#3F6B4F"
    b = [r(0, 0, W, H, BG, 0)]
    b.append(t(80, 58, "订阅体检", 40, INK, True))
    b.append(t(80, 106, "2026 年 10 月 · 8 项自动续费 · 演示账单", 11, MUT))
    b.append(t(900, 64, "年化", 10, MUT, True, ' letterSpacing="2"'))
    b.append(tm(80, 142, "¥1,662", 56, INK, True))
    b.append(t(300, 164, "每年", 12, MUT))
    b.append(t(80, 210, "每月 ¥138.50 · 下一轮续费合计 ¥320", 14, MUT))
    b.append(t(80, 236, "年费按 12 个月摊；低使用项单独标出。", 10, MUT))
    # runway
    x0, x1, yline = 80, 1000, 470
    b.append(t(80, 320, "未来 5 周，钱会从哪里走", 11, MUT, True, ' letterSpacing="1"'))
    b.append(line(x0, yline, x1 - x0, "#CFC5B4", 2))
    for day in [1, 8, 15, 22, 29]:
        x = x0 + (day - 1) / 30 * (x1 - x0)
        b.append(r(int(x), yline - 8, 2, 16, "#8C867A"))
    items = D['subscriptions']['items']
    for i, it in enumerate(items):
        day = int(it['renew'].split('/')[1])
        if it['renew'].startswith('12'):
            x = 1030
        else:
            x = x0 + (day - 1) / 30 * (x1 - x0)
        amt = it['price']
        size = int(20 + (amt / 198) ** 0.5 * 40)
        col = RED if it.get('low') else (AMBER if it.get('annual_only') else GREEN)
        b.append(circle(int(x) - size // 2, yline - size // 2, size, col))
        fs = 9 if amt >= 100 else 8
        b.append(tm(int(x) - (8 if amt >= 100 else 4), yline - 5, str(amt), fs, "#FFFFFF", True))
        b.append(t(int(x) - 14, yline + 24, it['renew'], 8, MUT))
        if it.get('low'):
            b.append(t(int(x) - 16, yline - 48, it['name'], 9, RED, True))
        if it.get('annual_only'):
            b.append(t(int(x) - 30, yline - 50, "修图年费", 9, AMBER, True))
    b.append(t(80, 530, "气泡大小 = 金额；红 = 低使用，琥珀 = 年费。", 9, MUT))
    # low use card
    b.append(card(80, 570, 460, 190, "#FFFDF8", 12))
    b.append(t(104, 588, "低使用 2 项", 11, RED, True, ' letterSpacing="1"'))
    b.append(tm(104, 610, "¥58/月", 34, RED, True))
    b.append(t(104, 658, "健身 App ¥38 · 47 天未打开", 10, INK))
    b.append(t(104, 682, "新闻 ¥20 · 62 天未读", 10, INK))
    b.append(t(104, 714, "一年 ¥696；取消前先确认是否还要用。", 9, MUT))
    # annual card
    b.append(card(570, 570, 430, 190, "#1D2A3A", 12, None))
    b.append(t(594, 588, "如果两项都不再需要", 10, "#AEB9C4", True))
    b.append(tm(594, 610, "¥696", 38, "#FFFFFF", True))
    b.append(t(594, 660, "一年少支出", 10, "#AEB9C4"))
    b.append(t(594, 690, "相当于 27 个月视频会员", 10, "#FFFFFF"))
    b.append(t(594, 714, "或 3.5 个月房租（按 ¥200/月）", 9, "#AEB9C4"))
    # renewal list
    b.append(t(80, 800, "逐项续费", 11, MUT, True, ' letterSpacing="1"'))
    for i, it in enumerate(items):
        col = i % 2
        row = i // 2
        x = 80 + col * 500
        y = 830 + row * 58
        b.append(line(x, y, 460, "#E2D9C8"))
        b.append(tm(x, y + 12, it['renew'], 10, MUT))
        b.append(t(x + 56, y + 10, it['name'], 12, INK, True))
        b.append(tm(x + 360, y + 10, f"¥{it['price']}", 12, RED if it.get('low') else INK, True))
        b.append(t(x + 56, y + 30, it['use'], 8, RED if it.get('low') else MUT))
    # actions
    b.append(card(80, 1100, 920, 100, "#E9E1D2", 12, None))
    b.append(t(104, 1118, "今天可以做的 3 件事", 10, MUT, True, ' letterSpacing="1"'))
    acts = ["暂停健身 App（11/08 前）", "取消新闻（11/18 前）", "保留视频与云存储"]
    for i, a in enumerate(acts):
        b.append(t(104 + i * 300, 1146, f"{i+1}. {a}", 11, INK))
    b.append(t(104, 1176, "先处理本月续费，不用一次做完。", 9, MUT))
    b.append(t(80, 1260, "演示账单；金额与日期为虚构，年化按 12 个月计算。", 9, MUT))
    b.append(t(80, 1290, "订阅体检 10 / 10", 9, MUT))
    return b

CASES = [(1,620,920,c01),(2,1240,1754,c02),(3,1200,1500,c03),(4,1000,700,c04),
         (5,1080,1920,c05),(6,800,1100,c06),(7,1240,1754,c07),
         (8,900,1200,c08),(9,800,1200,c09),(10,1080,1350,c10)]
for cid, w, h, fn in CASES:
    write(cid, w, h, fn(), "#F4EFE6")
print('B06 wrote', len(CASES))
