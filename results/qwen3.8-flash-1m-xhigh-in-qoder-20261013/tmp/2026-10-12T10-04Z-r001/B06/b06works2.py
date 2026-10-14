"""B06 works 06-10: warning tiers, a deposit decision tree, insurance gaps,
hospital wayfinding and a household utilities comparison.

Run: python tmp/<run_id>/B06/b06works2.py [06 07 ... | all]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, SANS, SERIF, tw, wrap, f  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B06"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))

INK = "#17212B"
INK2 = "#4A5866"
INK3 = "#7C8894"
LINE = "#D6D0C2"
PAPER = "#F4F1E8"
WHITE = "#FFFFFF"
GREEN = "#1F6F5C"
AMBER = "#8A6A12"
RED = "#A83224"
BLUE = "#1D5F8C"
GREY = "#A7B0B7"
NAVY = "#0B2F4A"


def save(s, name, min_font):
    s.min_font = min_font
    a = s.audit()
    print(name, json.dumps(a, ensure_ascii=False))
    assert a["overlap_n"] == 0, a["overlaps"]
    assert a["outside_n"] == 0, a["outside"]
    assert a["spill_n"] == 0, a["spill"]
    assert a["truncated_n"] == 0, a["truncated"]
    assert a["below_min_font_n"] == 0, a["below_min_font"]
    (TMP / f"{name}.snapshot").write_text(s.dsl(), encoding="utf-8")


def lines(s, role, text, x, y, size, colour, width, step=None):
    """Wrap to `width` and return the y after the last line."""
    step = step or size * 1.46 + 4
    for ln in wrap(text, size, width):
        s.text(role, ln, x, y, size, colour)
        y += step
    return y


# ------------------------------------------------------------------ 06 暴雨预警
def w06():
    w, h = 800, 1130
    s = Sheet(w, h, min_font=18, bg="#F2EFE6")
    s.rect(0, 0, w, h, "#F2EFE6")
    wn = D["warnings"]
    s.rect(0, 0, w, 150, "#1E2A33")
    s.text("h", "暴雨预警：颜色之后要做什么", 32, 26, 34, WHITE, bold=True)
    s.text("h", wn["issued"], 32, 74, 20, "#B9CBD8", font=MONO)
    s.text("h", f"当前生效：{wn['active']}", 32, 104, 24, "#E8A0A0", bold=True)
    # progression strip
    cols = {"Ⅳ 蓝色": "#1D5F8C", "Ⅲ 黄色": "#B47B1F", "Ⅱ 橙色": "#A83224",
            "Ⅰ 红色": "#5E1A14"}
    sy = 168
    for i2, t2 in enumerate(wn["tiers"]):
        x = 32 + i2 * 186
        on = t2["level"] == wn["active"]
        s.rect(x, sy, 176, 40, cols[t2["level"]], radius=8)
        s.text("p", t2["level"], x + 88, sy + 9, 21, WHITE, align="center", bold=on)
        if i2:
            s.text("p", "→", x - 12, sy + 8, 22, INK3)
    s.text("p", "级别递增 →", 32, sy + 48, 18, INK3)
    s.text("p", "红框＝现在这一级", 768, sy + 48, 18, INK3, align="right")
    cw, chh = 372, 396
    for i2, t2 in enumerate(wn["tiers"]):
        x = 32 + (i2 % 2) * (cw + 12)
        y = 244 + (i2 // 2) * (chh + 10)
        on = t2["level"] == wn["active"]
        s.rect(x, y, cw, chh, WHITE, radius=12,
               border=f"{3 if on else 1} SOLID {cols[t2['level']] if on else LINE}")
        s.panel(x, y, cw, chh)
        s.rect(x, y, cw, 48, cols[t2["level"]], radius=0)
        s.text("c", t2["level"], x + 16, y + 12, 24, WHITE, bold=True)
        if on:
            s.text("c", "当前生效", x + cw - 16, y + 15, 20, "#FFE1B0", align="right",
                   bold=True)
        yy = y + 62
        s.text("c", "触发标准", x + 16, yy, 18, INK3, bold=True)
        yy = lines(s, "c", t2["signal"], x + 16, yy + 24, 20, INK, cw - 32) + 6
        s.text("c", "谁受影响", x + 16, yy, 18, INK3, bold=True)
        yy = lines(s, "c", t2["who"], x + 16, yy + 24, 20, INK2, cw - 32) + 6
        s.text("c", "该做什么", x + 16, yy, 18, INK3, bold=True)
        yy += 24
        for a in t2["actions"]:
            yy = lines(s, "c", "· " + a, x + 16, yy, 20, INK, cw - 32)
        yy += 6
        for lab, val in (("停课", t2["school"]), ("停工", t2["work"]),
                         ("解除", t2["cancel"])):
            s.text("c", lab, x + 16, yy, 18, INK3)
            yy = lines(s, "c", val, x + 84, yy, 18, INK2, cw - 100) + 2
    lines(s, "f", "本页不预测雨情，只把每一级对应的行动摊开。阈值取自公开预警体系的"
                  "一般结构（示例编制）；停课、停工与转移以当地通知为准。", 32, 1052,
          18, INK2, w - 64)
    save(s, "case06-warnings", 18)


# ------------------------------------------------------------------ 07 押金决策树
def w07():
    w, h = 1200, 620
    s = Sheet(w, h, min_font=16, bg="#EEF1F3")
    s.rect(0, 0, w, h, "#EEF1F3")
    dp = D["deposit"]
    s.text("h", "退租时，押金能拿回多少", 40, 22, 36, INK, bold=True)
    s.text("h", f"押金 {dp['bond']:,.0f} 元 · 月租 {dp['rent']:,.0f} 元 · "
                "「是」往下走，「否」从右边掉出去", 40, 70, 20, INK2)
    nx, nw = 40, 430
    stub_x, stub_w = 490, 210
    y = 112
    for idx, n in enumerate(dp["nodes"]):
        qlines = wrap(n["q"], 20, nw - 60)
        hh = 16 + len(qlines) * 29 + 26
        s.rect(nx, y, nw, hh, WHITE, radius=10, border=f"1 SOLID {BLUE}")
        s.panel(nx, y, nw, hh)
        s.text("n", n["id"], nx + 14, y + 12, 20, BLUE, bold=True, font=MONO)
        yy = y + 12
        for ln in qlines:
            s.text("n", ln, nx + 46, yy, 20, INK, bold=True)
            yy += 29
        s.text("n", "合同" + n["clause"], nx + 46, yy + 1, 17, INK3)
        if idx < len(dp["nodes"]) - 1:
            s.line(nx + 60, y + hh, nx + 60, y + hh + 18, GREEN, 3.0)
            s.text("n", "是", nx + 20, y + hh + 1, 18, GREEN, bold=True)
        # 否 branch stub: the outcome this answer actually produces
        fee = n["no_fee"]
        s.line(nx + nw, y + hh / 2, stub_x, y + hh / 2, RED, 2.0)
        s.rect(stub_x, y + hh / 2 - 26, stub_w, 52, "#F7EAE8", radius=8,
               border=f"1 SOLID {RED}")
        s.panel(stub_x, y + hh / 2 - 26, stub_w, 52)
        s.text("n", ("否 → 扣 " + f"{fee:,.0f} 元") if fee else "否 → 不扣费",
               stub_x + 14, y + hh / 2 - 16, 19, RED if fee else GREEN, bold=True)
        s.text("n", n["no_outcome"], stub_x + 14, y + hh / 2 + 6, 16, INK2)
        y += hh + 18
    lx, lw = 720, 440
    s.text("l", "三条常见路径", lx, 100, 22, INK, bold=True)
    ly = 134
    for p in dp["paths"]:
        fee = sum(a for _, a in p["fees"])
        hh = 96 + (26 if p["fees"] else 0)
        s.rect(lx, ly, lw, hh, WHITE, radius=12,
               border=f"2 SOLID {GREEN if fee == 0 else (RED if fee >= 1900 else AMBER)}")
        s.panel(lx, ly, lw, hh)
        s.text("l", p["name"], lx + 18, ly + 12, 21, INK, bold=True)
        s.text("l", f"走法：{' → '.join(p['walk'])}", lx + 18, ly + 40, 16, INK2,
               font=MONO)
        s.text("l", "退回", lx + 18, ly + 64, 18, INK3)
        s.text("l", f"{p['back']:,.0f} 元", lx + 62, ly + 58, 26,
               GREEN if fee == 0 else INK, font=MONO, bold=True)
        s.text("l", f"扣 {fee:,.0f}", lx + lw - 18, ly + 64, 18,
               RED if fee else INK3, align="right", font=MONO)
        if p["fees"]:
            s.text("l", "＋ ".join(f"{lab} {amt:,.0f}" for lab, amt in p["fees"]),
                   lx + 18, ly + 90, 16, RED, font=MONO)
        ly += hh + 14
    s.text("f", "示例合同（条款号自拟）。本图只把条款摆在一起，不构成裁决；"
                "实际扣款需与出租方逐条核对。", 40, h - 40, 18, INK3)
    save(s, "case07-deposit", 16)


# ------------------------------------------------------------------ 08 车险场景
def hatch_rect(s, x, y, w, h, colour, step=14, weight=3):
    """45-degree hatching, each stroke clipped to the rectangle it fills."""
    if w <= 0 or h <= 0:
        return
    for c in range(int(x + y), int(x + w + y + h) + step, step):
        ax = max(x, c - (y + h))
        bx = min(x + w, c - y)
        if bx - ax < 1:
            continue
        s.line(ax, c - ax, bx, c - bx, colour, weight)


def w08():
    w, h = 1000, 1400
    s = Sheet(w, h, min_font=16, bg="#FBF9F3")
    s.rect(0, 0, w, h, "#FBF9F3")
    car = D["car"]
    s.rect(0, 0, w, 156, "#2A2118")
    s.text("h", "这三种事故，你要自己掏多少钱", 36, 24, 34, "#F5EFE2", bold=True)
    s.text("h", "保额高不等于都赔：把「不赔的部分」画出来", 36, 70, 21, "#C8B99A")
    s.text("h", f"三场景合计自掏 {car['total_out']:,.0f} 元 · 三条横条同一比例",
           36, 100, 20, "#E0A0A0", font=MONO)
    s.text("h", "读法：绿色 = 保险承担；斜纹 = 保单不覆盖，要自己掏。", 36, 128, 18,
           "#9C8E75")
    y = 176
    scale = 520.0 / max(sc["loss"] for sc in car["scenarios"])
    for sc in car["scenarios"]:
        s.rect(36, y, w - 72, 300, WHITE, radius=14, border=f"1 SOLID {LINE}")
        s.panel(36, y, w - 72, 300)
        s.text("s", sc["id"], 60, y + 18, 22, INK3, font=MONO, bold=True)
        s.text("s", sc["title"], 100, y + 18, 26, INK, bold=True, maxw=700)
        bw = sc["loss"] * scale
        paid = sc["paid"] * scale
        s.rect(60, y + 74, max(bw, 3), 46, "#F0E2DF", radius=4)
        s.rect(60, y + 74, max(paid, 3), 46, "#1F6F5C", radius=4)
        hatch_rect(s, 60 + paid, y + 74, bw - paid, 46, "#A83224")
        s.rect(60, y + 74, max(bw, 3), 46, "#00000000", border=f"1 SOLID {LINE}",
               radius=4)
        s.rect(60, y + 136, 14, 14, "#1F6F5C", radius=3)
        s.text("s", "保险赔付", 82, y + 132, 18, INK2)
        s.text("s", f"{sc['paid']:,.0f} 元", 60, y + 154, 22, INK, font=MONO, bold=True)
        s.rect(300, y + 136, 14, 14, "#F0E2DF", border=f"1 SOLID {RED}", radius=3)
        s.text("s", "自己掏（保单不覆盖）", 322, y + 132, 18, INK2)
        s.text("s", f"{sc['out']:,.0f} 元", 300, y + 154, 22, RED, font=MONO,
               bold=True)
        s.text("s", f"损失合计 {sc['loss']:,.0f} 元", w - 72, y + 154, 20, INK2,
               align="right", font=MONO)
        s.line(60, y + 196, w - 72, y + 196, LINE, 1.0)
        s.text("s", "缺口来自", 60, y + 210, 18, INK3)
        s.text("s", sc["gap_from"], 148, y + 210, 20, INK, maxw=680)
        s.text("s", "条款 " + sc["clause"], w - 72, y + 212, 18, INK3, align="right")
        s.text("s", f"横条总长 = 损失 {sc['loss']:,.0f} 元；其中斜纹 "
                    f"{100 * sc['out'] / sc['loss']:.0f}% 由你自己承担", 60, y + 248,
               17, INK3)
        y += 320
    s.rect(36, y, w - 72, 120, "#F2EDE2", radius=12)
    s.panel(36, y, w - 72, 120)
    s.text("s", "保单要点（示例）", 56, y + 12, 20, INK, bold=True)
    for i, (k, v) in enumerate(car["policy"].items()):
        col = 56 + (i % 3) * 300
        row = y + 42 + (i // 3) * 30
        s.text("s", f"{k} {v if isinstance(v, str) else f'{v:,.0f}'}", col, row, 17,
               INK2, maxw=290)
    s.text("s", "示例保单与金额，不指向任何真实产品；投保前请逐条读条款。", 36,
           h - 40, 18, INK3)
    save(s, "case08-insurance", 16)


# ------------------------------------------------------------------ 09 门诊楼层
def w09():
    w, h = 900, 1600
    s = Sheet(w, h, min_font=18, bg="#F5F2EA")
    s.rect(0, 0, w, h, "#F5F2EA")
    hp = D["hospital"]
    s.rect(0, 0, w, 128, "#1B3A4B")
    s.text("h", "门诊大楼：你要去的科在哪", 32, 26, 38, WHITE, bold=True)
    s.text("h", "左边按楼层看，右边按科室查；示例医院布局", 32, 78, 24, "#A8C7D6")
    floors = sorted(hp["floors"], key=lambda fl: -fl["floor"])
    fx, fw, fh = 32, 470, 188
    y = 152
    for fl in floors:
        s.rect(fx, y, fw, fh - 14, WHITE, radius=10, border=f"1 SOLID {LINE}")
        s.panel(fx, y, fw, fh - 14)
        s.text("f", f"{fl['floor']} 层", fx + 16, y + 14, 30, INK, bold=True,
               font=MONO)
        east, west = fl["zones"]["东区"], fl["zones"]["西区"]
        total = len(east) + len(west)
        ew = (fw - 32) * len(east) / total
        s.rect(fx + 16, y + 62, ew - 5, 96, "#DCE7EE", radius=8)
        s.rect(fx + 16 + ew, y + 62, fw - 32 - ew, 96, "#EFE6D8", radius=8)
        for i, d in enumerate(east):
            dw = (ew - 5 - 8 * (len(east) - 1)) / len(east)
            s.text("f", d, fx + 16 + i * (dw + 8) + dw / 2, y + 80,
                   dept_size(d, dw), INK, align="center", maxw=dw - 4)
        for i, d in enumerate(west):
            dw = (fw - 32 - ew - 8 * (len(west) - 1)) / len(west)
            s.text("f", d, fx + 16 + ew + i * (dw + 8) + dw / 2, y + 80,
                   dept_size(d, dw), INK, align="center", maxw=dw - 4)
        s.text("f", "东区", fx + 16, y + 128, 18, BLUE)
        s.text("f", "西区", fx + 16 + ew + 6, y + 128, 18, AMBER)
        y += fh
    gy = y - 14
    s.rect(fx, gy, fw, 44, "#1B3A4B", radius=8)
    s.text("f", "1 层入口 · 东门在右侧", fx + fw / 2, gy + 10, 22, WHITE,
           align="center")
    tgt = hp["target"]
    ty = 152 + (6 - tgt["floor"]) * fh + 96
    # the route runs in the gutter between the two columns, never over a label
    gx2 = fx + fw + 22
    s.line(gx2, gy + 22, gx2, ty, RED, 5.0)
    s.line(gx2, ty, fx + fw - 2, ty, RED, 5.0)
    s.dot(gx2, gy + 22, 8, RED, ring=WHITE, ring_w=2)
    # mark the destination block itself
    fl3 = next(f2 for f2 in hp["floors"] if f2["floor"] == tgt["floor"])
    band = fw - 32
    ew3 = band * len(fl3["zones"]["东区"]) / (len(fl3["zones"]["东区"])
                                             + len(fl3["zones"]["西区"]))
    dw3 = (ew3 - 5 - 8) / len(fl3["zones"]["东区"])
    bx = fx + 16
    s.rect(bx - 4, 152 + (6 - tgt["floor"]) * fh + 58, dw3 + 8, 104, "#00000000",
           border=f"3 SOLID {RED}", radius=10)
    s.dot(bx + dw3 / 2, 152 + (6 - tgt["floor"]) * fh + 132, 7, RED, ring=WHITE,
          ring_w=2)
    s.text("r", f"红线示例：1 层东门 → {tgt['floor']} 层"
                f"{tgt['zone']} {tgt['dept']}（红框）", 32, gy + 58, 21, RED, bold=True)
    s.text("r", hp["lift_note"], 32, gy + 88, 20, INK2)
    ix = 540
    s.rect(ix, 152, w - ix - 32, gy + 44 - 152, WHITE, radius=12,
           border=f"1 SOLID {LINE}")
    s.panel(ix, 152, w - ix - 32, gy + 44 - 152)
    s.text("i", "按科室查楼层", ix + 20, 170, 26, INK, bold=True)
    s.text("i", "与左图同一份数据", ix + 20, 208, 18, INK3)
    iy = 244
    for name, fl, zone in hp["index"]:
        s.text("i", name, ix + 20, iy, 20, INK, maxw=180)
        s.text("i", f"{fl} 层 · {zone}", ix + 300, iy, 20, INK2, align="right",
               font=MONO)
        s.line(ix + 20, iy + 30, ix + 300, iy + 30, "#EFEADC", 1.0)
        iy += 48
    s.text("f", "示例布局与科室分布；实际就诊请以医院当日指引为准。", 32, h - 44, 20,
           INK3)
    save(s, "case09-wayfinding", 18)


def dept_size(name, dw):
    """Largest label size that still fits the block it sits in."""
    for size in (20, 19, 18):
        if tw(name, size) <= dw - 4:
            return size
    raise ValueError(f"{name} will not fit a {dw:.0f}px block")


def ew_mid(hp):
    """x offset of the 3F east-zone centre inside a floor band."""
    fl = next(f2 for f2 in hp["floors"] if f2["floor"] == 3)
    east, west = fl["zones"]["东区"], fl["zones"]["西区"]
    band = 470 - 32
    ew = band * len(east) / (len(east) + len(west))
    return ew / 2


# ------------------------------------------------------------------ 10 家庭水电煤
def w10():
    w, h = 1200, 900
    s = Sheet(w, h, min_font=16, bg="#FFFFFF")
    s.rect(0, 0, w, h, "#FFFFFF")
    ut = D["utilities"]
    s.text("h", "水、电、燃气：终于能放在一张表里比", 40, 28, 34, INK, bold=True)
    s.text("h", f"三种单位、三种计费方式，先统一成「元 / {ut['people']} 人 · 月」",
           40, 78, 20, INK2)
    s.text("h", f"全年合计 {ut['total_year']:,.0f} 元 · 每人每月 "
                f"{ut['total_per_person_month']:g} 元", 40, 104, 20, INK3, font=MONO)
    y = 148
    maxv = max(i["yuan_per_person_month"] for i in ut["items"])
    for it in ut["items"]:
        s.rect(40, y, w - 80, 172, "#FAF8F2", radius=12)
        s.panel(40, y, w - 80, 172)
        s.text("u", it["name"], 64, y + 18, 28, INK, bold=True)
        s.text("u", f"{it['yuan_per_person_month']:g} 元 / 人 · 月", 64, y + 56, 20,
               INK2, font=MONO)
        bw = it["yuan_per_person_month"] / maxv * 300
        s.rect(64, y + 90, bw, 30, BLUE if it["name"] == "电" else
               (AMBER if it["name"] == "燃气" else GREEN), radius=4)
        s.text("u", f"份额 {it['share_pct']:g}%", 64 + bw + 12, y + 96, 18, INK3)
        # 12-month sparkline
        sx, sy = 560, y + 40
        peak = max(it["monthly"])
        for k, v in enumerate(it["monthly"]):
            bh = v / peak * 90
            s.rect(sx + k * 24, sy + 90 - bh, 18, bh, "#CFD8DE")
        s.text("u", "12 个月支出（元）", sx, sy + 100, 17, INK3)
        s.text("u", f"最高 {peak:,.0f}", sx + 190, sy + 100, 17, INK2, font=MONO)
        # unit reality check + trend
        s.text("u", "原始单位", 900, y + 18, 18, INK3)
        s.text("u", f"{it['year_qty']:,} {it['unit']} / 年", 900, y + 42, 20, INK,
               font=MONO)
        s.text("u", f"单价 {it['yuan_per_unit']:g} 元 / {it['unit']}", 900, y + 70, 18,
               INK2, font=MONO)
        s.text("u", f"全年 {it['year_cost']:,.0f} 元", 900, y + 98, 18, INK2,
               font=MONO)
        up = it["yoy_pct"] > 0
        s.rect(900, y + 128, 180, 34, "#F5E4E1" if up else "#E3EFE9", radius=8)
        s.text("u", f"同比 {'+' if up else ''}{it['yoy_pct']:g}% · "
                    f"{'涨' if up else '降'}", 990, y + 134, 18,
               RED if up else GREEN, align="center", bold=True)
        y += 186
    s.line(40, y - 8, w - 40, y - 8, LINE, 1.0)
    s.text("u", "可行动项", 40, y + 6, 22, INK, bold=True)
    verbs = {"电": "若来自空调或采暖，先看这两个月的时段与温度设置；",
             "燃气": "采暖季占比高，核对壁挂炉设定温度与使用习惯；",
             "自来水": "用量集中在两三个月，先排查渗漏与浇灌用水。"}
    for i, it in enumerate(ut["items"]):
        p1, p2 = it["peaks"]
        s.text("u", f"· {it['name']}：{p1['month']} 与 {p2['month']} 高出月均 "
                    f"{p1['over_mean']:g} / {p2['over_mean']:g} 元，"
                    f"前 4 个月占全年 {it['top4_share']:g}%；{verbs[it['name']]}",
               40, y + 38 + i * 26, 18, INK2, maxw=w - 90)
    s.text("u", "示例抄表数据（自拟 12 个月），同比来自同一样本的上一年版本；单价与"
                "用量不代表任何真实账户。", 40, h - 62, 18, INK3)
    s.text("u", "月度柱形按本项最高月归一，只用于看分布，不用于跨项比较。", 40,
           h - 34, 18, INK3)
    save(s, "case10-utilities", 16)


WORKS = {"06": w06, "07": w07, "08": w08, "09": w09, "10": w10}

if __name__ == "__main__":
    which = sys.argv[1:] or ["all"]
    for k, fn in WORKS.items():
        if "all" in which or k in which:
            fn()
            print("built", k)
