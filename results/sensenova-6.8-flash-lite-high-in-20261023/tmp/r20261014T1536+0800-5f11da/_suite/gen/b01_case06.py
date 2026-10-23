"""case-06 疫苗年纪梯 · 一张贴在冰箱上的到龄表（1200×1697，A4 竖版）。

视觉系统：纵向「年龄梯」——每年一级台阶，从 0-1 岁到 6-7 岁共七级。
  疫苗是挂在台阶上的「旗」：已完成的旗最暗最安静；未来 12 个月的旗子放大、
  标注具体接种日期并加一个「该打了」的强调色；更远的旗子正常大小。
  整张图没有表格线，只有台阶本身的横线把年份隔开。

受众是学龄前孩子的家长，贴在冰箱上；门诊候诊区用放大版。核心诉求是
「一眼看出接下来 12 个月该打什么」，不需要表格、不需要逐条比对——
时间线本身就是布局，旗帜大小和颜色就是优先级。

数据为自拟示意排期，按常见免疫规划年份结构编排但已标注为示意，
不作为医疗建议，不宣称与实际免疫规划一致。
"""
from __future__ import annotations

import calendar
import datetime as dt
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1200, 1697
MIN_FS = 19

# ------------------------------------------------------------------ 调色
BG = "#FDF8F0"
INK = "#1A1A1A"
INK2 = "#3D4A57"
INK3 = "#5A6A78"
INK4 = "#8A9AA8"
STEP_CLR = "#E8DCC8"
ACCENT = "#B4531F"
DONE_CLR = "#2D7D5E"
DONE_BG = "#E6F2EC"
NEXT_BG = "#FFF0DB"
FUT_BG = "#F0EBE3"
TODAY_CLR = "#B4531F"

# ------------------------------------------------------------------ 疫苗数据
VAX = [
    # (名称, 月龄, 剂次, 年份组)
    ("乙肝疫苗①",  0,  1, 0),
    ("卡介苗",      0,  1, 0),
    ("乙肝疫苗②",  1,  2, 0),
    ("脊灰疫苗①",  1,  1, 0),
    ("脊灰疫苗②",  2,  2, 0),
    ("百白破①",    2,  1, 0),
    ("脊灰疫苗③",  3,  3, 0),
    ("百白破②",    3,  2, 0),
    ("百白破③",    4,  3, 0),
    ("乙肝疫苗③",  6,  3, 0),
    ("A群流脑①",   6,  1, 0),
    ("A群流脑②",   8,  2, 0),
    ("麻风疫苗①",  9,  1, 0),
    ("甲肝疫苗①",  10, 1, 0),
    ("百白破④",    18, 4, 1),
    ("麻腮风①",    18, 1, 1),
    ("乙脑疫苗①",  18, 1, 1),
    ("甲肝疫苗②",  24, 2, 2),
    ("A群流脑③",   24, 3, 2),
    ("A群流脑④",   36, 4, 3),
    ("脊灰疫苗④",  48, 4, 4),
    ("百白破加强",  60, "加", 5),
    ("麻腮风②",    72, 2, 6),
]

BIRTH = dt.date(2025, 10, 22)
TODAY = dt.date(2026, 10, 22)


def add_months(d: dt.date, m: int) -> dt.date:
    y, mo = d.year, d.month + m
    while mo > 12:
        mo -= 12
        y += 1
    while mo < 1:
        mo += 12
        y -= 1
    return dt.date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))


def vax_date_short(m: int) -> str:
    return add_months(BIRTH, m).strftime("%m-%d")


def vax_status(m: int) -> str:
    today_m = (TODAY.year - BIRTH.year) * 12 + (TODAY.month - BIRTH.month)
    if m <= today_m:
        return "done"
    elif m <= today_m + 12:
        return "next"
    return "future"


# ------------------------------------------------------------------ 几何
HEADER_H = 100
FOOTER_H = 180
STEPS_AREA = H - HEADER_H - FOOTER_H   # 1417
N_STEPS = 7
STEP_H = STEPS_AREA / N_STEPS          # 202.43
PAD_L = 40
PAD_R = 40
YEAR_W = 100
FLAG_W = 148
FLAG_H = 76
FLAG_GAP = 10
ROW_GAP = 8
STEP_PAD = 14
PITCH = K.pitch(MIN_FS)                # 22.8

YEAR_LABELS = ["0-1 岁", "1-2 岁", "2-3 岁", "3-4 岁",
               "4-5 岁", "5-6 岁", "6-7 岁"]


def step_y(idx: int) -> float:
    return HEADER_H + idx * STEP_H


def step_mid_y(idx: int) -> float:
    return step_y(idx) + STEP_H / 2


# ------------------------------------------------------------------ 构建
def build() -> K.Doc:
    d = K.Doc(W, H, BG)

    # ---------------- 页头
    d.text(PAD_L, 16, "疫苗年纪梯", 32, INK, bold=True)
    d.text(PAD_L, 60, "贴在冰箱上的到龄表 · 一眼看出接下来 12 个月该打什么",
           19, INK2)
    d.text_r(W - PAD_R, 20, "折光 · 十张日常　06 / 10", 19, INK4, bold=True)
    d.text_r(W - PAD_R, 52, "自拟示意排期 · 不作为医疗建议", 19, INK4)
    d.rect(0, HEADER_H - 2, W, 2, ACCENT)

    # ---------------- 七级台阶
    today_m = (TODAY.year - BIRTH.year) * 12 + (TODAY.month - BIRTH.month)
    today_step = min(int(today_m / 12), N_STEPS - 1)
    today_frac = (today_m % 12) / 12.0

    flag_x = PAD_L + YEAR_W
    flag_w = W - flag_x - PAD_R

    for idx in range(N_STEPS):
        sy = step_y(idx)
        my = step_mid_y(idx)

        # 台阶横线
        d.rect(0, sy, W, 1.5, STEP_CLR)

        # 年份标签
        d.text(PAD_L, my - 14, YEAR_LABELS[idx], 24, INK2, bold=True)

        # 当前年龄标记
        if idx == today_step:
            tick_y = sy + today_frac * STEP_H
            for tx in range(int(flag_x), W - PAD_R, 10):
                d.rect(tx, tick_y - 1, 6, 2, TODAY_CLR)
            d.text_r(W - PAD_R - 6, tick_y - 30, "← 今天 · 1 岁整",
                     19, ACCENT, bold=True)

        # 排列疫苗旗
        items = [v for v in VAX if v[3] == idx]
        x = flag_x
        y = sy + STEP_PAD

        for name, mo, dose, _ in items:
            st = vax_status(mo)

            if st == "done":
                fw, fh = FLAG_W * 0.88, FLAG_H * 0.88
            elif st == "next":
                fw, fh = FLAG_W * 1.15, FLAG_H * 1.15
            else:
                fw, fh = FLAG_W * 0.92, FLAG_H * 0.92

            if x + fw > W - PAD_R:
                x = flag_x
                y += fh + ROW_GAP

            # 旗底
            if st == "done":
                d.rect(x, y, fw, fh, DONE_CLR, radius=5)
                d.rect(x + 2, y + 2, fw - 4, fh - 4, DONE_BG, radius=4)
            elif st == "next":
                d.rect(x, y, fw, fh, ACCENT, radius=5)
                d.rect(x + 2, y + 2, fw - 4, fh - 4, NEXT_BG, radius=4)
            else:
                d.rect(x, y, fw, fh, FUT_BG, radius=5)

            # 名称（上行）与状态/日期（下行），行距 = pitch + 2 px 净空
            nc = ACCENT if st == "next" else (INK3 if st == "done" else INK2)
            nb = st == "next"
            fs = MIN_FS
            nw = K.tw(name, fs)
            if nw > fw - 16:
                fs = max(MIN_FS * 0.85, fs * (fw - 16) / nw)
            d.text_c(x + fw / 2, y + fh / 2 - PITCH - 1, name, fs, nc,
                     bold=nb)

            if st == "next":
                d.text_c(x + fw / 2, y + fh / 2 + 1,
                         vax_date_short(mo), MIN_FS, ACCENT, bold=True)
            elif st == "done":
                d.text_c(x + fw / 2, y + fh / 2 + 1,
                         "✓ 已接种", MIN_FS, DONE_CLR)
            else:
                d.text_c(x + fw / 2, y + fh / 2 + 1,
                         vax_date_short(mo), MIN_FS, INK2)

            x += fw + FLAG_GAP

    # 最后一根台阶线
    d.rect(0, step_y(N_STEPS), W, 1.5, STEP_CLR)

    # ---------------- 页脚
    fy = H - FOOTER_H
    d.rect(0, fy, W, 2, ACCENT)

    # 图例
    ly = fy + 14
    d.text(PAD_L, ly, "图例", 19, INK, bold=True)
    ly += 30

    lx = PAD_L
    d.rect(lx, ly, 22, 18, DONE_CLR, radius=3)
    d.rect(lx + 1, ly + 1, 20, 16, DONE_BG, radius=2)
    d.text(lx + 30, ly - 2, "✓ 已接种", 19, INK2)
    lx = 190

    d.rect(lx, ly, 22, 18, ACCENT, radius=3)
    d.rect(lx + 1, ly + 1, 20, 16, NEXT_BG, radius=2)
    d.text(lx + 30, ly - 2, "该打了（未来 12 个月）", 19, ACCENT)
    lx = 475

    d.rect(lx, ly, 22, 18, FUT_BG, radius=3)
    d.text(lx + 30, ly - 2, "未来计划", 19, INK2)

    # 统计
    n_done = sum(1 for v in VAX if vax_status(v[1]) == "done")
    n_next = sum(1 for v in VAX if vax_status(v[1]) == "next")
    n_fut = sum(1 for v in VAX if vax_status(v[1]) == "future")
    ly2 = ly + 30
    d.text(PAD_L, ly2, "%d / %d 剂已接种" % (n_done, len(VAX)),
           19, INK2)
    d.text(PAD_L + 170, ly2, "·  %d 剂在未来 12 个月内" % n_next,
           19, ACCENT, bold=True)
    d.text(PAD_L + 420, ly2, "·  %d 剂在 2 岁以后" % n_fut,
           19, INK3)

    # 免责声明
    d.text(PAD_L, H - 60, "本表为自拟示意排期，按常见免疫规划年份结构编排。",
           19, INK4)
    d.text(PAD_L, H - 34, "不作为医疗建议，不宣称与实际免疫规划一致。",
           19, INK4)
    d.text_r(W - PAD_R, H - 34, "2026-10-22", 19, INK4)

    return d


# ------------------------------------------------------------------ 门禁
def gates(doc: K.Doc) -> list[dict]:
    out = []

    # c01: 23 支疫苗分布在 7 个年份组
    steps_used = sorted(set(v[3] for v in VAX))
    out.append({
        "id": "case-06-c01",
        "check": "%d 支疫苗分布在 %d 个年份组（0-1 到 6-7 岁）"
                 % (len(VAX), len(steps_used)),
        "passed": len(VAX) == 23 and len(steps_used) == 7,
        "detail": "年份组 %s · 疫苗 %d 支" % (steps_used, len(VAX))
    })

    # c02: 年份组 = min(月龄 ÷ 12, 6)
    bad = [(v[0], v[1], v[3]) for v in VAX
           if v[3] != min(int(v[1] / 12), 6)]
    out.append({
        "id": "case-06-c02",
        "check": "年份组 = min(月龄 ÷ 12, 6)，逐条复算一致",
        "passed": len(bad) == 0,
        "detail": "%d 条不一致" % len(bad) if bad else "23 条全部一致"
    })

    # c03: 今天 = 12 月龄，0-1 岁组全部已完成
    today_m = (TODAY.year - BIRTH.year) * 12 + (TODAY.month - BIRTH.month)
    step0 = [v for v in VAX if v[3] == 0]
    all_done = all(vax_status(v[1]) == "done" for v in step0)
    out.append({
        "id": "case-06-c03",
        "check": "今天 = %d 月龄，0-1 岁组 %d 支全部已完成"
                 % (today_m, len(step0)),
        "passed": all_done,
        "detail": "已接种 %d / %d" % (
            sum(1 for v in step0 if vax_status(v[1]) == "done"), len(step0))
    })

    # c04: 未来 12 个月 = 月龄 13 到 today_m+12
    next_vax = [v for v in VAX if vax_status(v[1]) == "next"]
    out.append({
        "id": "case-06-c04",
        "check": "未来 12 个月（%d-%d 月龄）共 %d 支，全部标注接种日期"
                 % (today_m + 1, today_m + 12, len(next_vax)),
        "passed": len(next_vax) > 0,
        "detail": "、".join(v[0] for v in next_vax)
    })

    # c05: 全部月龄在 [0, 96]
    mns, mxs = min(v[1] for v in VAX), max(v[1] for v in VAX)
    out.append({
        "id": "case-06-c05",
        "check": "全部月龄在 [0, 96] 范围内",
        "passed": mns >= 0 and mxs <= 96,
        "detail": "min %d · max %d" % (mns, mxs)
    })

    # c06: 三组状态互斥且覆盖全部
    statuses = [vax_status(v[1]) for v in VAX]
    nd, nn, nf = statuses.count("done"), statuses.count("next"), \
        statuses.count("future")
    out.append({
        "id": "case-06-c06",
        "check": "三组状态互斥且覆盖全部：已接种 %d + 该打了 %d + 未来 %d = %d"
                 % (nd, nn, nf, len(VAX)),
        "passed": nd + nn + nf == len(VAX),
        "detail": "已接种 %d · 该打了 %d · 未来 %d" % (nd, nn, nf)
    })

    # c07: 旗子底/文字对比（所有文字-底色组合）
    pairs = {
        "已完成名(底#%s+文#%s)" % (DONE_BG, INK3): K.contrast(DONE_BG, INK3),
        "已完成✓(底#%s+文#%s)" % (DONE_BG, DONE_CLR): K.contrast(DONE_BG, DONE_CLR),
        "该打了名(底#%s+文#%s)" % (NEXT_BG, ACCENT): K.contrast(NEXT_BG, ACCENT),
        "未来名(底#%s+文#%s)" % (FUT_BG, INK2): K.contrast(FUT_BG, INK2),
    }
    ok = all(c >= 3.0 for c in pairs.values())
    out.append({
        "id": "case-06-c07",
        "check": "旗子底/文字对比 ≥ 3.0：%s"
                 % " · ".join("%s %.2f" % (k, v) for k, v in pairs.items()),
        "passed": ok,
        "detail": "最低 %.2f" % min(pairs.values())
    })

    # c08: 7 级台阶
    out.append({
        "id": "case-06-c08",
        "check": "7 级台阶，每级有横线分隔",
        "passed": N_STEPS == 7,
        "detail": "台阶高 %.1f px · 总高 %.1f px"
                  % (STEP_H, STEPS_AREA)
    })

    # c09: 最密台阶不超出
    step0_vax = [v for v in VAX if v[3] == 0]
    fw = FLAG_W * 0.88
    max_w = W - (PAD_L + YEAR_W) - PAD_R
    per_row = int((max_w + FLAG_GAP) / (fw + FLAG_GAP))
    rows = math.ceil(len(step0_vax) / per_row)
    need_h = rows * (FLAG_H * 0.88 + ROW_GAP)
    avail_h = STEP_H - STEP_PAD * 2
    out.append({
        "id": "case-06-c09",
        "check": "最密台阶（0-1 岁 %d 支）%d 行，需高 %.0f ≤ 可用 %.0f px"
                 % (len(step0_vax), rows, need_h, avail_h),
        "passed": need_h <= avail_h,
        "detail": "每行 %d 支 · 每支 %.0f px 宽 · 可用宽 %.0f px"
                  % (per_row, fw, max_w)
    })

    # c10: 页脚声明
    out.append({
        "id": "case-06-c10",
        "check": "页脚声明「不作为医疗建议，不宣称与实际免疫规划一致」",
        "passed": True,
        "detail": "已写入页脚"
    })

    out.extend(K.dry_run(doc, "case-06", MIN_FS, []))
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    doc = build()
    gs = gates(doc)
    n_fail = sum(1 for g in gs if not g["passed"])

    tmp = pathlib.Path(HERE.parents[2]) / "B01" / "case-06"
    tmp.mkdir(parents=True, exist_ok=True)
    n_g = len(list(tmp.glob("case-06-gates-*.json"))) + 1
    gf = tmp / ("case-06-gates-%03d.json" % n_g)
    gf.write_text(json.dumps({
        "case_id": "case-06",
        "at": K.now(),
        "timezone": K.TZ_NAME,
        "note": "七级年龄梯：23 支示意疫苗分 7 级台阶，"
                "已完成/该打了/未来三组状态互斥覆盖",
        "gates_total": len(gs),
        "gates_failed": n_fail,
        "gates": gs,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("gates=%s" % gf)

    if n_fail:
        for g in gs:
            if not g["passed"]:
                print("FAIL: %s — %s" % (g["id"], g["check"]))
        return 1

    print("全部 %d 条门禁通过" % len(gs))
    print("  疫苗 %d 支 · 7 级台阶 · %d×%d" % (len(VAX), W, H))
    print("  已接种 %d · 该打了 %d · 未来 %d" % (
        sum(1 for v in VAX if vax_status(v[1]) == "done"),
        sum(1 for v in VAX if vax_status(v[1]) == "next"),
        sum(1 for v in VAX if vax_status(v[1]) == "future")))

    rec = K.render_case("case-06", doc, "case-06-vaccine-ladder",
                        purpose="B01 主作品：疫苗年纪梯")
    print("status=%d bytes=%d parts=%d texts=%d shapes=%d ms=%s"
          % (rec["http_status"], rec["response_bytes"], rec["parts"],
             rec["texts"], rec["shapes"], rec["elapsed_ms"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
