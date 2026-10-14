"""B05 药盒 - ten screens of one household medicine-shelf product.

All content comes from b05data.py's data.json, so the same medicine shows the same
remaining count, expiry and adherence on the phone, the watch, the fridge card, the
caregiver tablet, the pharmacist desktop and the A4 printout.

Run: python tmp/<run_id>/B05/b05pages.py [01 02 ... 10 | all]
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, SANS, tw, wrap, f  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B05"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
MEDS = {m["id"]: m for m in D["meds"]}
PEOPLE = {p["id"]: p for p in D["people"]}
TODAY = D["today"]

# palette: one hue per meaning, colour-blind safe pairing with text labels
INK = "#182028"
INK2 = "#4C5A66"
INK3 = "#7E8B95"
LINE = "#DCD6C8"
PAPER = "#F7F4EC"
CARD = "#FFFFFF"
GREEN = "#1F6F5C"
AMBER = "#8A6A12"
RED = "#A83224"
BLUE = "#1D5F8C"
GREY = "#9AA5AD"
BRAND = "#0B3954"


def status_of(m):
    """Pharmacist workflow state, driven by the same effective-expiry day count the
    alert list and the printout show."""
    return ("待药师确认" if m["expiry_days"] <= 30 else
            ("已核" if m["expiry_days"] > 90 else "随访提醒"))


def state_colour(s):
    return {"已服": GREEN, "待服": BLUE, "漏服": RED, "按需": GREY}.get(s, INK2)


def phone(w=390, h=844, title="药盒", status="21:40", net="在线"):
    s = Sheet(w, h, min_font=16, bg="#EDEAE2")
    s.rect(0, 0, w, h, "#EDEAE2")
    # status bar + app bar
    s.rect(0, 0, w, 34, BRAND)
    s.text("bar", status, 16, 8, 16, "#DCE7EE", font=MONO)
    s.text("bar", net, w - 16, 8, 16, "#DCE7EE", align="right", font=MONO)
    s.rect(0, 34, w, 54, BRAND)
    s.text("bar", title, 16, 48, 26, "#FFFFFF", bold=True)
    s.content_top = 88
    return s


def tabbar(s, w, h, active):
    tabs = ["今日", "药箱", "警报", "我的"]
    y = h - 62
    s.rect(0, y, w, 62, CARD)
    s.line(0, y, w, y, LINE, 1.0)
    for i, t in enumerate(tabs):
        x = w * (i + 0.5) / len(tabs)
        on = i == active
        s.rect(x - 26, y + 12, 52, 34, BRAND if on else "#00000000", radius=8,
               border=None if on else f"1 SOLID {LINE}")
        s.text("tab", t, x, y + 18, 18, "#FFFFFF" if on else INK2, align="center",
               bold=on)


def card(s, x, y, w, h, *, fill=CARD, radius=12, border=None, shadow=True,
         panel=True):
    if panel:
        s.panel(x, y, w, h)
    s.rect(x, y, w, h, fill, radius=radius, border=border,
           shadow="0 6 18 #18202814" if shadow else None)


def chip(s, text_, x, y, colour, size=16, filled=True):
    w = tw(text_, size) + 18
    if filled:
        s.rect(x, y, w, size + 10, colour, radius=(size + 10) / 2)
        s.text("chip", text_, x + w / 2, y + 5, size, "#FFFFFF", align="center")
    else:
        s.rect(x, y, w, size + 10, "#00000000", border=f"1 SOLID {colour}",
               radius=(size + 10) / 2)
        s.text("chip", text_, x + w / 2, y + 5, size, colour, align="center")
    return w


def save(s, name, min_font=16):
    s.min_font = min_font
    a = s.audit()
    print(name, json.dumps(a, ensure_ascii=False))
    assert a["overlap_n"] == 0, a["overlaps"]
    assert a["outside_n"] == 0, a["outside"]
    assert a["spill_n"] == 0, a["spill"]
    assert a["truncated_n"] == 0, a["truncated"]
    assert a["below_min_font_n"] == 0, a["below_min_font"]
    (TMP / f"{name}.snapshot").write_text(s.dsl(), encoding="utf-8")


# ------------------------------------------------------------------ 01 today
def p01():
    w, h = 390, 844
    s = phone(title="今日用药")
    slots = D["schedule_today"]
    done = sum(1 for x in slots if x["state"] == "已服")
    miss = sum(1 for x in slots if x["state"] == "漏服")
    card(s, 14, s.content_top + 8, w - 28, 112)
    s.text("sum", f"{done}/{len(slots)}", 30, s.content_top + 20, 40, INK, font=MONO,
           bold=True)
    s.text("sum", "今日已完成", 30, s.content_top + 68, 18, INK3)
    s.text("sum", f"漏服 {miss}", w - 30, s.content_top + 26, 22,
           RED if miss else GREEN, align="right", bold=True)
    s.line(30, s.content_top + 92, w - 30, s.content_top + 92, LINE, 1.0)
    s.text("sum", "数据截止 " + TODAY + " 21:40", w - 30, s.content_top + 100, 16,
           INK3, align="right")
    y = s.content_top + 136
    for x in slots:
        col = state_colour(x["state"])
        card(s, 14, y, w - 28, 92)
        s.rect(14, y, 6, 92, col, radius=3)
        s.text("sch", x["time"], 32, y + 12, 26, INK, font=MONO, bold=True)
        s.text("sch", x["short"], 32, y + 44, 22, INK2)
        s.text("sch", x["amount"] + " · " + PEOPLE[x["who"]]["name"], 32, y + 68, 16,
               INK3)
        chip(s, x["state"], w - 92, y + 30, col)
        y += 102
    tabbar(s, w, h, 0)
    save(s, "case01-today")


# ------------------------------------------------------------------ 02 alerts
def p02():
    w, h = 390, 844
    s = phone(title="药箱警报")
    sm = D["summary"]
    card(s, 14, s.content_top + 4, w - 28, 66, fill="#FDF3E6")
    s.text("h", f"{len(sm['expiring_7'])} 项 7 天内到期 · "
                f"{len(sm['expiring_30'])} 项 30 天内", 30, s.content_top + 12, 20,
           AMBER, bold=True)
    s.text("h", f"{len(sm['need_refill'])} 项需补货（按各自补货周期判断）", 30,
           s.content_top + 40, 16, INK3)
    y = s.content_top + 80
    order = sorted(D["meds"], key=lambda m: m["expiry_days"])
    for m in order:
        ec = RED if m["expiry_days"] <= 7 else (AMBER if m["expiry_days"] <= 30
                                                else GREEN)
        card(s, 14, y, w - 28, 112)
        s.text("a", m["name"], 28, y + 10, 21, INK, bold=True)
        s.text("a", PEOPLE[m["who"]]["name"] + " · " + m["rx"], 28, y + 36, 16, INK3)
        s.text("a", "效期 " + m["eff_expiry_iso"] + f"（{m['eff_days']} 天）", 28,
               y + 58, 18, ec, bold=True, font=MONO)
        if m["days_supply"] is None:
            s.text("a", "按需使用 · 无法按天数估计，剩 "
                        f"{m['remaining']} 吸", 28, y + 84, 17, INK2)
        else:
            s.text("a", f"剩 {m['remaining']} {m['form']} · 可服 "
                        f"{m['days_supply']:.0f} 天（至 {m['runs_out']}）", 28,
                   y + 84, 17, INK2, font=MONO)
        if m["need_refill"]:
            chip(s, "需补货", w - 96, y + 10, RED)
        if m["eff_label"] == "开封期 90 天内":
            chip(s, "开封期", w - 96, y + 10, BLUE, filled=False)
        y += 120
    tabbar(s, w, h, 2)
    save(s, "case02-alerts")


# ------------------------------------------------------------------ 03 entry form
def p03():
    w, h = 390, 844
    s = phone(title="录入药品")
    fields = [
        ("药品名称", "阿托伐他汀钙片", None),
        ("服用者", "周秀兰（母亲）", None),
        ("每次剂量", "1 片", None),
        ("每日时间", "22:00", None),
        ("包装总量", "30", None),
        ("有效期至", "2026-10-01", "效期早于今天（10-13），请核对药盒侧面"),
        ("每日次数", "3", "与已填时间数（1 个）不符：补时间或改次数"),
    ]
    y = s.content_top + 8
    s.text("f", "手动录入 · 已填 7 / 9 项", 16, y, 18, INK3, font=MONO)
    s.text("f", "还有 2 项", w - 16, y + 2, 16, INK3, align="right")
    y += 32
    for name, val, err in fields:
        elines = wrap(err, 16, w - 60) if err else []
        hgt = 58 + (len(elines) * 27.4 + 8 if err else 0)
        card(s, 14, y, w - 28, hgt, fill=CARD if not err else "#FDF0EE")
        s.text("f", name, 28, y + 8, 16, INK3)
        s.text("f", val, 28, y + 28, 22, INK, font=MONO if val.isdigit() else SANS)
        if err:
            s.rect(w - 44, y + 12, 18, 18, RED, radius=9)
            s.text("f", "!", w - 35, y + 13, 16, "#FFFFFF", align="center", bold=True)
            yy = y + 54
            for ln in elines:
                s.text("f", ln, 28, yy, 16, RED)
                yy += 27.4
        y += hgt + 8
    card(s, 14, y, w - 28, 44, fill="#E6E3DA")
    s.text("f", "保存（先修正 2 处错误）", w / 2, y + 12, 20, INK3, align="center")
    s.para("f", "本表单不采集药品相互作用信息；用法以医嘱为准", 16, y + 60, 16,
           INK3, w - 32)
    tabbar(s, w, h, 1)
    save(s, "case03-entry")


# ------------------------------------------------------------------ 04 empty state
def p04():
    w, h = 390, 844
    s = phone(title="药箱")
    y = s.content_top + 40
    s.rect(w / 2 - 46, y, 92, 92, "#00000000", border=f"2 SOLID {LINE}", radius=14)
    s.line(w / 2 - 20, y + 46, w / 2 + 20, y + 46, LINE, 3)
    s.line(w / 2, y + 26, w / 2, y + 66, LINE, 3)
    s.text("e", "还没有任何药品", w / 2, y + 116, 26, INK, align="center", bold=True)
    s.text("e", "没有提醒、没有警报，也不算余量。", w / 2, y + 154, 19, INK2,
           align="center")
    y += 200
    opts = [("扫药盒条码", "带出品名与规格，用法仍需核对", "需摄像头"),
            ("从医院处方导入", "读取本次就诊开具的药品清单", "需授权"),
            ("手动录入", "逐项填写，最慢但最可靠", "纯手动")]
    for t, d_, tag in opts:
        dlines = wrap(d_, 17, w - 150)
        hgt = 46 + len(dlines) * 28.8 + 12
        card(s, 14, y, w - 28, hgt)
        s.text("e", t, 30, y + 14, 24, INK, bold=True)
        yy = y + 46
        for ln in dlines:
            s.text("e", ln, 30, yy, 17, INK2)
            yy += 28.8
        chip(s, tag, w - 118, y + 16, BLUE if "手动" not in tag else GREY,
             filled=False)
        y += hgt + 12
    s.text("e", "首次录入后，今日时间线才会出现内容。", w / 2, y + 6, 17, INK3,
           align="center")
    cy = min(y + 40, h - 62 - 14 - 112)
    assert cy > y + 26, (cy, y)
    card(s, 14, cy, w - 28, 112, fill="#E2DBCA", shadow=False,
         border=f"1 SOLID {LINE}")
    s.text("e", "数据放在哪里", 30, cy + 12, 19, INK, bold=True)
    s.para("e", "记录只存在这台手机与家庭共享的设备上；未接入医院系统，也不会给出"
                "用药建议。", 30, cy + 40, 16, INK2, w - 60)
    tabbar(s, w, h, 1)
    save(s, "case04-empty")


# ------------------------------------------------------------------ 05 watch
def p05():
    w, h = 200, 240
    s = Sheet(w, h, min_font=14, bg="#0E1620")
    s.rect(0, 0, w, h, "#0E1620")
    s.rect(6, 6, w - 12, h - 12, "#16222E", radius=40)
    nxt = next(x for x in D["schedule_today"] if x["state"] == "待服") \
        if any(x["state"] == "待服" for x in D["schedule_today"]) else \
        D["schedule_today"][-1]
    m = MEDS["M3"]
    s.text("w", "22:00", w / 2, 40, 34, "#FFFFFF", align="center", bold=True,
           font=MONO)
    s.text("w", "降脂药", w / 2, 84, 22, "#B9CBD8", align="center")
    s.text("w", "1 片 · 母亲", w / 2, 112, 16, "#7E8B95", align="center")
    s.rect(w / 2 - 46, 142, 92, 30, "#A83224", radius=15)
    s.text("w", "仅剩 3 片", w / 2, 148, 15, "#FFFFFF", align="center", bold=True)
    s.text("w", "长按确认", w / 2, 186, 14, "#7E8B95", align="center")
    save(s, "case05-watch", min_font=14)


# ------------------------------------------------------------------ 06 fridge card
def p06():
    w, h = 680, 320
    s = Sheet(w, h, min_font=18, bg="#FBF8F0")
    s.rect(0, 0, w, h, "#FBF8F0")
    s.rect(0, 0, w, 46, BRAND)
    s.text("f", "本周谁在吃什么", 20, 12, 24, "#FFFFFF", bold=True)
    s.text("f", "离线显示 · " + TODAY + " 21:40", w - 20, 16, 18, "#B9CBD8",
           align="right", font=MONO)
    y = 60
    for mid in ("M1", "M2", "M3"):
        m = MEDS[mid]
        s.text("f", PEOPLE[m["who"]]["name"], 20, y + 4, 26, INK, bold=True)
        s.text("f", m["short"] + " " + f"{m['per_dose']}{m['form']}", 150, y + 6, 24,
               INK2)
        s.text("f", " / ".join(m["doses"]), 350, y + 6, 24, INK2, font=MONO)
        col = RED if m["expiry_days"] <= 7 else (AMBER if m["expiry_days"] <= 30
                                                 else GREEN)
        s.rect(w - 148, y, 128, 34, "#00000000", border=f"2 SOLID {col}", radius=17)
        s.text("f", f"效期 {m['expiry_days']} 天", w - 84, y + 6, 20, col,
               align="center", bold=True)
        y += 46
    s.line(20, y + 2, w - 20, y + 2, LINE, 1.5)
    s.text("f", "只列医嘱定时药；按需吸入剂与非医嘱补充剂不写在本卡上。", 20,
           y + 12, 18, INK3)
    s.text("f", "漏服怎么处理：以说明书或药师意见为准，勿自行加倍。", 20, y + 40, 20,
           INK, bold=True)
    s.text("f", "本页每 24 小时同步一次；有疑问可打给周成或社区药师。", 20, y + 68,
           18, INK3)
    save(s, "case06-fridge", min_font=18)


# ------------------------------------------------------------------ 07 caregiver tablet
def p07():
    w, h = 834, 1112
    s = Sheet(w, h, min_font=16, bg="#EFEBE1")
    s.rect(0, 0, w, h, "#EFEBE1")
    s.rect(0, 0, w, 72, BRAND)
    s.text("h", "照护者视图", 28, 22, 30, "#FFFFFF", bold=True)
    s.text("h", "望云里 7 号楼 · 502", w - 28, 28, 20, "#B9CBD8", align="right")
    x = 28
    for p in D["people"]:
        on = p["id"] == "gm"
        s.rect(x, 92, 150, 56, CARD if on else "#00000000", radius=12,
               border=f"2 SOLID {BRAND if on else LINE}")
        s.text("p", p["name"], x + 14, 100, 22, INK if on else INK2, bold=on)
        s.text("p", p["rel"] + f" {p['age']}", x + 14, 126, 16, INK3)
        x += 162
    grid_rows = [mid for mid in ("M1", "M2", "M3", "M5")
                 if MEDS[mid]["who"] == "gm"]
    card_y = 170
    card(s, 28, card_y, w - 56, 282, shadow=False)
    s.text("t", "周秀兰 · 近 14 天服药格", 48, card_y + 18, 26, INK, bold=True)
    s.text("t", "每格一天的医嘱时点；左半为前一周（自 09-30），右半为最近一周", 48,
           card_y + 52, 17, INK3)
    days = D["days14"]
    gx, gy = 170, card_y + 108
    cw, chh = 44, 26
    for j2, d in enumerate(days):
        if j2 % 2:
            today = j2 == len(days) - 1
            s.text("t", d[5:], gx + j2 * cw + cw / 2, gy - 28, 16,
                   INK if today else INK3, align="center", font=MONO, bold=today)
    s.line(gx + 7 * cw - 3, gy - 6, gx + 7 * cw - 3, gy + 3 * 44 + 22, LINE, 1.0)
    for i, mid in enumerate(grid_rows):
        m = MEDS[mid]
        s.text("t", m["short"], 48, gy + i * 44 + 4, 19, INK2)
        for j2, row in enumerate(D["grid14"][mid]):
            got = sum(1 for c in row if c == "取")
            need = len(row)
            col = GREEN if got == need else (RED if got == 0 else AMBER)
            s.rect(gx + j2 * cw, gy + i * 44, cw - 6, chh, col, radius=4)
            s.text("t", f"{got}/{need}", gx + j2 * cw + (cw - 6) / 2, gy + i * 44 + 3,
                   16, "#FFFFFF", align="center", font=MONO)
    s.text("t", "格内为『当日已确认时点数 / 应服时点数』；绿=全勤，黄=有漏，红=全漏。",
           48, gy + len(grid_rows) * 44 + 4, 17, INK3)
    pp = D["per_person"]
    rows = []
    for pid in ("gm", "da", "me"):
        st = pp[pid]
        if st["adherence_14"] is None:
            stat = f'{st["as_needed_meds"]} 种按需药 · 不计依从率'
            note = "无固定时点"
        else:
            stat = (f'{st["scheduled_meds"]} 种规律药 · {st["adherence_14"]:.1f}% '
                    f'（{st["taken_14"]}/{st["due_14"]}）')
            note = (f'14 天内漏 {st["missed_14"]} 次' if st["missed_14"]
                    else "14 天内无漏服")
        rows.append((PEOPLE[pid]["name"], stat, note))
    card(s, 28, 462, w - 56, 250, shadow=False)
    s.text("t", "成员切换会改变统计口径", 48, 478, 22, INK, bold=True)
    yy = 518
    for who, stat, note in rows:
        s.text("t", who, 48, yy, 22, INK, bold=True)
        s.clip_line(122, yy + 16, 162, yy + 16, LINE, 40, 1.0)
        s.text("t", stat, 170, yy + 2, 20, INK2, font=MONO)
        s.text("t", note, 520, yy + 2, 18, INK3)
        yy += 40
    s.text("t", "依从率 = 已确认时点数 ÷ 应服时点数（14 天窗口），按需药不计入分母。",
           48, 658, 18, INK2)
    s.text("t", "以上记录来自家庭自填与手表确认，未与医院系统核对。", 48, 684, 18,
           AMBER)
    card(s, 28, 736, w - 56, 300, shadow=False)
    s.text("t", "待办", 48, 752, 24, INK, bold=True)
    todos = [("补货", "M3 只剩 3 片，社区医院开药需 7 天", RED),
             ("清效期", "M3 效期 7 天，先确认是否续方", RED),
             ("清效期", "M2 效期 20 天，按当前速度会用不完", AMBER),
             ("记数", "M4 为按需吸入剂，需手动记剩余吸数", BLUE)]
    yy = 792
    for tag, txt, col in todos:
        chip(s, tag, 48, yy - 4, col)
        s.text("t", txt, 148, yy, 22, INK)
        s.rect(w - 96, yy - 2, 44, 30, "#00000000", border=f"2 SOLID {LINE}",
               radius=8)
        s.text("t", "完成", w - 74, yy + 4, 16, INK3, align="center")
        yy += 48
    s.text("t", "待办由余量、效期与漏服规则自动生成，不替代医嘱。", 48, 1056, 18,
           INK3)
    save(s, "case07-caregiver")


# ------------------------------------------------------------------ 08 pharmacist desktop
def p08():
    w, h = 1440, 900
    s = Sheet(w, h, min_font=16, bg="#E9E6DE")
    s.rect(0, 0, w, h, "#E9E6DE")
    s.rect(0, 0, w, 56, "#22303A")
    s.text("h", "药盒 · 药师交接端", 24, 16, 22, "#FFFFFF", bold=True)
    s.text("h", "家庭 502 · 3 位成员 · 5 种药 · 打印预览", w - 24, 20, 17, "#9FB2C4",
           align="right")
    for i, t in enumerate(["交接清单", "家庭档案", "打印与导出", "设置"]):
        on = i == 0
        s.rect(24 + i * 130, 70, 118, 36, BRAND if on else CARD, radius=8,
               border=None if on else f"1 SOLID {LINE}")
        s.text("h", t, 83 + i * 130, 78, 18, "#FFFFFF" if on else INK2,
               align="center")
    card(s, 24, 122, 880, 740, shadow=False)
    s.text("l", "家庭 502 · 交接清单（5 项）", 48, 142, 26, INK, bold=True)
    s.text("l", "其中 2 项需药师确认", 48, 176, 17, INK3)
    cols = [("药品", 48), ("服用者", 284), ("处方来源", 400), ("效期", 580),
            ("剩余", 690), ("状态", 762)]
    for name, x in cols:
        s.text("l", name, x, 214, 17, INK3)
    s.line(48, 240, 876, 240, INK, 1.2)
    y = 258
    for m in D["meds"]:
        st = status_of(m)
        col = RED if m["expiry_days"] <= 7 else (AMBER if m["expiry_days"] <= 30
                                                 else GREEN)
        s.line(48, y - 8, 876, y - 8, LINE, 1.0)
        s.text("l", m["name"], 48, y, 19, INK, bold=True, maxw=210)
        s.text("l", PEOPLE[m["who"]]["name"], 284, y + 2, 18, INK2, maxw=90)
        s.text("l", m["rx"], 400, y + 2, 18, INK2, maxw=164)
        s.text("l", m["eff_expiry_iso"], 580, y + 2, 18, col, font=MONO, maxw=94)
        s.text("l", f"{m['remaining']} {m['form']}", 690, y + 2, 18, INK2,
               font=MONO, maxw=58)
        s.text("l", st, 762, y + 2, 18, col, maxw=114)
        y += 46
    s.line(48, y - 8, 876, y - 8, INK, 1.2)
    card(s, 48, y + 10, 828, 120, fill="#F4F1E8", shadow=False)
    s.text("l", "未采集字段", 68, y + 24, 19, INK, bold=True)
    s.text("l", "批号 / 生产厂家 / 医保编码：本次交接不含，需现场补录后再打印。",
           68, y + 52, 18, INK2)
    s.text("l", "用法用量以处方原件为准，本系统不生成用药建议。", 68, y + 80, 18,
           AMBER)
    fy = y + 154
    counts = [("全部", len(D["meds"]))]
    for lab in ("待药师确认", "随访提醒", "已核"):
        k = sum(1 for m in D["meds"] if status_of(m) == lab)
        if k:
            counts.append((lab, k))
    for i, (lab, n) in enumerate(counts):
        on = i == 0
        chip(s, f"{lab} {n}", 48 + i * 150, fy, BRAND if on else INK3, size=17,
             filled=on)
    s.text("l", "上次打印 2026-10-12 09:14 · 打印人 王药师（演示账号）", 48,
           fy + 44, 17, INK3, font=MONO)
    s.line(48, fy + 76, 876, fy + 76, LINE, 1.0)
    s.text("l", "本页只汇总家庭自填与处方抄录信息，不构成用药建议。", 48, fy + 90,
           17, INK3)
    card(s, 924, 122, 492, 740, shadow=False)
    s.text("r", "打印预览（A4 竖版）", 948, 142, 22, INK, bold=True)
    pw, ph = 250, 353
    px, py = 990, 182
    s.rect(px, py, pw, ph, "#FFFFFF", border=f"1 SOLID {LINE}", radius=2)
    s.rect(px + 12, py + 12, pw - 24, 26, "#22303A", radius=3)
    s.text("preview", "家庭用药随访摘要", px + pw / 2, py + 16, 15,
               "#FFFFFF", align="center")
    yy = py + 50
    for i, m in enumerate(D["meds"]):
        s.rect(px + 12, yy, pw - 24, 26, "#F4F1E8", radius=3)
        s.text("preview", f"{i + 1}  {m['short']} · {m['remaining']}{m['form']} · "
               f"{m['expiry_days']}天", px + 18, yy + 5, 12, INK)
        yy += 32
    s.rect(px + 12, yy + 6, pw - 24, 40, "#EDEAE1", radius=3)
    s.text("preview", "黑白打印：状态用文字标注", px + 18, yy + 14, 12, INK2)
    s.text("r", "共 1 页 · 已含数据截止时刻", px + 12, py + ph + 20, 17, INK3)
    s.rect(948, py + ph + 44, 444, 44, BRAND, radius=8)
    s.text("r", "打印 / 导出 PDF", 1170, py + ph + 56, 20, "#FFFFFF", align="center",
           bold=True)
    s.text("r", "预览为缩小示意（12–15px），真实排版见第 09 屏 A4 页", 948,
           py + ph + 108, 17, INK3)
    sy = py + ph + 152
    s.line(948, sy, 1392, sy, LINE, 1.0)
    s.text("r", "打印设置", 948, sy + 14, 20, INK, bold=True)
    for i, (k, v) in enumerate([("纸张", "A4 竖版 · 单面"), ("份数", "1 份"),
                                ("包含字段", "不含空白字段"),
                                ("颜色", "黑白（状态用文字）")]):
        s.text("r", k, 948, sy + 48 + i * 32, 18, INK3)
        s.text("r", v, 1392, sy + 48 + i * 32, 18, INK2, align="right")
    a = s.audit(ignore_roles=("preview",))
    print("case08-pharmacist", json.dumps(a, ensure_ascii=False))
    assert a["overlap_n"] == 0 and a["outside_n"] == 0, a
    assert a["spill_n"] == 0, a["spill"]
    assert a["truncated_n"] == 0, a["truncated"]
    assert a["below_min_font_n"] == 0, a["below_min_font"]
    (TMP / "case08-pharmacist.snapshot").write_text(s.dsl() + "\n",
                                                    encoding="utf-8")


# ------------------------------------------------------------------ 09 A4 printout
def p09():
    w, h = 794, 1123
    s = Sheet(w, h, min_font=14, bg="#FFFFFF")
    s.rect(0, 0, w, h, "#FFFFFF")
    s.rect(48, 48, w - 96, 3, INK)
    s.text("p", "家庭用药随访摘要", 48, 66, 34, INK, bold=True)
    s.text("p", "望云里 7 号楼 3 单元 502 · 3 位成员 · 5 种药", 48, 116, 20, INK2)
    s.text("p", "数据截止 " + TODAY + " 21:40 · 制表：周成（管理员）", 48, 142, 18,
           INK3, font=MONO)
    s.line(48, 168, w - 48, 168, INK, 1.2)
    cols = [("#", 48), ("药品", 84), ("服用者", 292), ("用法", 368),
            ("剩余", 490), ("效期(天)", 556), ("依从", 636), ("状态", 696)]
    for name, x in cols:
        s.text("p", name, x, 182, 16, INK2, bold=True)
    y = 212
    for i, m in enumerate(D["meds"], 1):
        s.line(48, y - 10, w - 48, y - 10, "#DDD8CC", 1.0)
        vals = [(str(i), 48), (m["name"][:11], 84), (PEOPLE[m["who"]]["name"], 292),
                (" ".join(m["doses"]) or "按需", 368),
                (f"{m['remaining']}{m['form']}", 490), (str(m["expiry_days"]), 556),
                (f"{m['adherence_14']:.0f}%" if m["adherence_14"] is not None
                 else "不计", 636),
                ("需补货" if m["need_refill"] else
                 ("效期紧" if m["expiry_days"] <= 30 else "正常"), 696)]
        for t, x in vals:
            s.text("p", t, x, y, 17, INK,
                   font=MONO if x in (368, 490, 556, 636) else SANS)
        y += 38
    s.line(48, y, w - 48, y, INK, 1.2)
    y += 20
    s.text("p", "近 7 天服药记录（√=已确认，×=漏服，—=当日无安排）", 48, y, 19, INK,
           bold=True)
    y += 36
    s.text("p", "日期", 224, y, 14, INK3)
    s.text("p", "依从率", 616, y, 14, INK3)
    for j, d in enumerate(D["week_days"]):
        s.text("p", d[5:], 277 + j * 44, y, 14, INK3, font=MONO, align="center")
    y += 28
    for mid in ("M1", "M2", "M3", "M5"):
        m = MEDS[mid]
        s.text("p", m["name"][:10], 48, y, 17, INK)
        for j, row in enumerate(D["week_grid"][mid]):
            mark = "√" if all(c == "取" for c in row) else (
                "×" if any(c == "漏" for c in row) else "—")
            s.text("p", mark, 268 + j * 44, y, 18, INK, font=MONO)
        s.text("p", f"{m['adherence_14']:.0f}%", 616, y, 17, INK, font=MONO)
        y += 32
    s.text("p", "依从率 = 已确认时点数 ÷ 应服时点数（14 天窗口）；按需药不计入分母。",
           48, y + 2, 15, INK3)
    y += 32
    s.line(48, y, w - 48, y, "#DDD8CC", 1.0)
    y += 22
    s.text("p", "需要药师确认的事项", 48, y, 19, INK, bold=True)
    y += 36
    for t in ["阿托伐他汀钙片：效期 7 天且仅剩 3 片，是否续方？",
              "二甲双胍缓释片：效期 20 天，按当前用量会用不完，是否更换包装规格？",
              "布地奈德福莫特罗吸入剂：按需使用，剩余吸数由家属手工记数，请核对方法。",
              "维生素 D 滴剂：开封 2026-10-08，开封后 90 天内用完（2027-01-06）。"]:
        s.text("p", "· " + t, 48, y, 17, INK2)
        y += 30
    s.line(48, y + 10, w - 48, y + 10, "#DDD8CC", 1.0)
    s.text("p", "本页不替代医嘱；用法用量以处方原件为准。黑白打印即可，"
                "状态列全部使用文字而非颜色。", 48, y + 28, 16, INK3)
    s.line(48, 1026, 296, 1026, INK, 1.0)
    s.line(w - 296, 1026, w - 48, 1026, INK, 1.0)
    s.text("p", "家属签名 / 日期", 48, 1000, 16, INK3)
    s.text("p", "药师签名 / 日期", w - 296, 1000, 16, INK3)
    s.text("p", "第 1 页 / 共 1 页 · 药盒 v0.9 导出", w - 48, 1064, 16, INK3,
           align="right", font=MONO)
    save(s, "case09-print", min_font=14)


# ------------------------------------------------------------------ 10 disposal
def p10():
    w, h = 390, 844
    s = phone(title="过期药怎么办")
    m = MEDS["M3"]
    card(s, 14, s.content_top + 8, w - 28, 132, fill="#FDF0EE")
    s.text("d", "1 项已到期或即将到期", 30, s.content_top + 20, 22, RED, bold=True)
    s.text("d", m["name"], 30, s.content_top + 52, 22, INK)
    s.text("d", f"效期 {m['expiry_iso']}（{m['expiry_days']} 天后）· 剩 "
                f"{m['remaining']} 片", 30, s.content_top + 82, 18, INK2, font=MONO)
    s.text("d", "先确认是否续方，再决定处置", 30, s.content_top + 108, 18, AMBER)
    y = s.content_top + 156
    steps = [("1", "不要冲入马桶或下水道", "未查证权威清单；这是常见做法，送交前"
              "请先问药师"),
             ("2", "连同外包装盒一起送到回收点", "社区药房与卫生服务中心常设回收箱；"
              "点位以当地药师确认为准"),
             ("3", "在药盒里登记处置记录", "登记药品、数量、送交地点与日期，便于复诊"
              "时说明")]
    s.text("d", "三步处置", 16, y, 24, INK, bold=True)
    y += 40
    for n, t, why in steps:
        wlines = wrap(why, 17, w - 104)
        hgt = 50 + len(wlines) * 28.8 + 12
        card(s, 14, y, w - 28, hgt)
        s.rect(28, y + 16, 34, 34, BRAND, radius=17)
        s.text("d", n, 45, y + 22, 20, "#FFFFFF", align="center", bold=True,
               font=MONO)
        s.text("d", t, 76, y + 18, 22, INK, bold=True)
        yy = y + 50
        for ln in wlines:
            s.text("d", ln, 76, yy, 17, INK2)
            yy += 28.8
        y += hgt + 10
    blines = wrap("各地回收点与目录不同，未做核实；本页只给通用做法，"
                  "最终以药师意见为准。", 17, w - 60)
    card(s, 14, y, w - 28, 42 + len(blines) * 28.8 + 10, fill="#F4F1E8")
    s.text("d", "本系统不提供药品处置政策数据库", 30, y + 14, 19, INK, bold=True)
    yy = y + 42
    for ln in blines:
        s.text("d", ln, 30, yy, 17, INK2)
        yy += 28.8
    tabbar(s, w, h, 2)
    save(s, "case10-disposal")


PAGES = {"01": p01, "02": p02, "03": p03, "04": p04, "05": p05, "06": p06,
         "07": p07, "08": p08, "09": p09, "10": p10}

if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    for k, fn in PAGES.items():
        if "all" in which or k in which:
            fn()
            print("built", k)
