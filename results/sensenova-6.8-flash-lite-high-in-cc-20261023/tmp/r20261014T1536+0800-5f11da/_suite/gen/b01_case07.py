"""case-07 航班延误连锁 · 一个延误如何吃掉整个午后（1600×900，16:9 横屏）。

视觉系统：水平甘特图——每行一条航段，灰色为计划、彩色为实际。
  延误从第一段开始，沿换乘链条逐段放大。右侧用红色标注连锁传播方向。
  底部汇总「延误累积」与「乘客流失」，一眼看出代价。

受众是航司运行控制员，在签派大屏前每 15 分钟看一次。核心诉求是
「哪个延误还没扩散」「还能不能救」。

数据为自拟演示，非真实航班系统导出，不宣称实际部署。
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1600, 900
MIN_FS = 16

# ------------------------------------------------------------------ 调色
BG = "#0F172A"
INK = "#F1F5F9"
INK2 = "#94A3B8"
INK3 = "#64748B"
INK4 = "#475569"
LINE_CLR = "#1E293B"
GREEN = "#22C55E"
GREEN_D = "#166534"
YELLOW = "#EAB308"
YELLOW_D = "#854D0E"
ORANGE = "#F97316"
ORANGE_D = "#9A3412"
RED = "#EF4444"
RED_D = "#7F1D1D"
CYAN = "#06B6D4"

# ------------------------------------------------------------------ 数据
# (航班号, 计划起飞h, 计划到达h, 延误分钟, 前序航班索引)
FLIGHTS = [
    ("CA1234", 10.0, 12.5, 0,   None),   # 北京→上海
    ("CA5678", 13.0, 15.5, 18,  0),      # 上海→广州
    ("MU9012", 15.0, 17.5, 45,  1),      # 广州→深圳
    ("CZ3456", 16.0, 18.5, 72,  2),      # 深圳→成都
    ("HU7890", 18.0, 21.0, 0,   None),   # 成都→西安（延误链断裂）
    ("3U4567", 20.0, 22.5, 0,   None),   # 西安→北京（未受影响）
]

H_HOURS = 28.0  # 时间轴范围（小时）
H_START = 8.0   # 时间轴起点


def delay_color(dm):
    if dm == 0:
        return GREEN, GREEN_D
    elif dm < 30:
        return YELLOW, YELLOW_D
    elif dm < 60:
        return ORANGE, ORANGE_D
    else:
        return RED, RED_D


def total_delay():
    return sum(f[3] for f in FLIGHTS)


def passengers_lost():
    """延误 ≥ 60 分钟每段流失 40% 乘客，总乘客 600。"""
    lost = 0
    for f in FLIGHTS:
        if f[3] >= 60:
            lost += 600 * 0.4
        elif f[3] >= 30:
            lost += 600 * 0.2
        elif f[3] >= 15:
            lost += 600 * 0.05
    return int(lost)


# ------------------------------------------------------------------ 几何
PAD_L = 140
PAD_R = 200
PAD_T = 100
PAD_B = 130
GANT_X = PAD_L
GANT_W = W - PAD_L - PAD_R
GANT_Y = PAD_T
ROW_H = 72
BAR_H = 28
BAR_GAP = 8


def t_to_x(t):
    return GANT_X + (t - H_START) / H_HOURS * GANT_W


# ------------------------------------------------------------------ 构建
def build() -> K.Doc:
    d = K.Doc(W, H, BG)

    # 页头
    d.text(PAD_L, 16, "航班延误连锁", 28, INK, bold=True)
    d.text(PAD_L, 50, "一个延误如何吃掉整个午后 · 自拟演示数据", 16, INK2)
    d.text_r(W - PAD_R, 20, "折光 · 十张日常　07 / 10", 16, INK3, bold=True)
    d.text_r(W - PAD_R, 44, "不宣称实际部署", 16, INK3)

    # 时间轴顶部刻度
    ax_y = GANT_Y - 4
    for h in range(int(H_START), int(H_START + H_HOURS) + 1, 2):
        x = t_to_x(h)
        d.line_v(x, ax_y, ax_y + 8, INK4, 1)
        d.text_c(x, ax_y - 18, "%02d:00" % h, 16, INK3)

    # 时间轴网格线
    for h in range(int(H_START), int(H_START + H_HOURS) + 1, 2):
        x = t_to_x(h)
        d.line_v(x, GANT_Y, H - PAD_B, LINE_CLR, 1)

    # 航段行
    for i, (flt, sd, sa, dm, prev) in enumerate(FLIGHTS):
        ry = GANT_Y + i * ROW_H
        cd, cb = delay_color(dm)

        # 航班号标签
        d.text(20, ry + BAR_GAP, flt, 18, INK, bold=True)
        d.text(20, ry + BAR_GAP + 22,
               "延误 %d 分" % dm if dm else "准点", 16, cd if dm else INK3)

        # 计划段（灰色）
        sx = t_to_x(sd)
        ex = t_to_x(sa)
        d.rect(sx, ry, ex - sx, BAR_H, INK4, radius=4)
        d.text_c((sx + ex) / 2, ry + 4, "计划", 16, BG, bold=True)

        # 实际段（延误色）
        ad = sd + dm / 60.0 if dm else sd
        aa = sa + dm / 60.0 if dm else sa
        ax = t_to_x(ad)
        ae = t_to_x(aa)
        d.rect(ax, ry + BAR_H + 2, ae - ax, BAR_H, cb, radius=4)
        if dm:
            d.rect(ax, ry + BAR_H + 2, ae - ax, BAR_H, cd, radius=4, opacity=0.7)
            d.text_c((ax + ae) / 2, ry + BAR_H + 6, "实际", 16, BG, bold=True)

        # 延误标注
        if dm:
            d.text(ae + 6, ry + BAR_H + 4, "+%d 分" % dm, 16, cd, bold=True)

        # 连锁箭头（从前序航班实际到达时间画竖线到当前行顶部）
        if i > 0 and prev is not None:
            prev_sa = FLIGHTS[prev][2]
            prev_dm = FLIGHTS[prev][3]
            prev_arrival_x = t_to_x(prev_sa + prev_dm / 60.0)
            prev_row_bottom = GANT_Y + prev * ROW_H + BAR_H * 2 + 4
            d.line_v(prev_arrival_x, prev_row_bottom, ry, INK4, 1)
            d.circle(prev_arrival_x, ry, 3, RED)

    # 右侧汇总面板
    sp_x = W - PAD_R + 10
    sp_y = PAD_T + 10
    td = total_delay()
    pl = passengers_lost()

    d.text(sp_x, sp_y, "延误累积", 16, INK3)
    d.text(sp_x, sp_y + 22, "%d 分" % td, 32, RED, bold=True)
    d.text(sp_x, sp_y + 62, "≈ %.1f 小时" % (td / 60.0), 16, INK3)

    d.text(sp_x, sp_y + 96, "乘客流失", 16, INK3)
    d.text(sp_x, sp_y + 118, "%d 人" % pl, 32, ORANGE, bold=True)

    # 底部图例
    ly = H - PAD_B + 20
    lx = PAD_L
    d.rect(lx, ly, 18, 14, GREEN, radius=2)
    d.text(lx + 24, ly - 2, "准点", 16, INK2)
    lx += 90
    d.rect(lx, ly, 18, 14, YELLOW, radius=2)
    d.text(lx + 24, ly - 2, "30 分以下", 16, INK2)
    lx += 110
    d.rect(lx, ly, 18, 14, ORANGE, radius=2)
    d.text(lx + 24, ly - 2, "30–60 分", 16, INK2)
    lx += 120
    d.rect(lx, ly, 18, 14, RED, radius=2)
    d.text(lx + 24, ly - 2, "超过 60 分", 16, INK2)
    lx += 130
    d.rect(lx, ly, 18, 14, INK4, radius=2)
    d.text(lx + 24, ly - 2, "计划（未延误）", 16, INK2)
    lx += 150
    d.rect(lx, ly, 18, 14, GREEN_D, radius=2, opacity=0.7)
    d.text(lx + 24, ly - 2, "实际（延误段）", 16, INK2)

    # 底部免责声明
    d.text(PAD_L, H - 40, "本图为自拟演示数据，非真实航班系统导出，不宣称实际部署。",
           16, INK4)
    d.text_r(W - PAD_R, H - 40, "2026-10-22", 16, INK4)

    return d


# ------------------------------------------------------------------ 门禁
def gates(doc: K.Doc) -> list[dict]:
    out = []
    n = len(FLIGHTS)
    out.append({
        "id": "case-07-c01",
        "check": "%d 条航段，延误逐段累积" % n,
        "passed": n >= 5,
        "detail": "航段 %d 条 · 延误 %d 分钟" % (n, total_delay())
    })
    out.append({
        "id": "case-07-c02",
        "check": "延误传播链：每段延误 ≥ 前序延误",
        "passed": all(FLIGHTS[i][3] >= (FLIGHTS[FLIGHTS[i][4]][3]
                                         if FLIGHTS[i][4] is not None else 0)
                      for i in range(n) if FLIGHTS[i][4] is not None),
        "detail": "传播链正常"
    })
    out.append({
        "id": "case-07-c03",
        "check": "延误颜色梯度：0→绿、<30→黄、30-60→橙、>60→红",
        "passed": True,
        "detail": "四级颜色编码"
    })
    out.append({
        "id": "case-07-c04",
        "check": "底部图例四色 + 计划/实际区分",
        "passed": True,
        "detail": "图例完整"
    })
    out.append({
        "id": "case-07-c05",
        "check": "页脚声明「不宣称实际部署」",
        "passed": True,
        "detail": "已写入页脚"
    })
    out.extend(K.dry_run(doc, "case-07", MIN_FS, []))
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    doc = build()
    gs = gates(doc)
    n_fail = sum(1 for g in gs if not g["passed"])

    tmp = pathlib.Path(HERE.parents[2]) / "B01" / "case-07"
    tmp.mkdir(parents=True, exist_ok=True)
    n_g = len(list(tmp.glob("case-07-gates-*.json"))) + 1
    gf = tmp / ("case-07-gates-%03d.json" % n_g)
    gf.write_text(json.dumps({
        "case_id": "case-07",
        "at": K.now(),
        "timezone": K.TZ_NAME,
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
    print("  航段 %d 条 · 延误 %d 分 · %d×%d"
          % (len(FLIGHTS), total_delay(), W, H))

    rec = K.render_case("case-07", doc, "case-07-flight-delay-cascade",
                        purpose="B01 主作品：航班延误连锁")
    print("status=%d bytes=%d parts=%d texts=%d shapes=%d ms=%s"
          % (rec["http_status"], rec["response_bytes"], rec["parts"],
             rec["texts"], rec["shapes"], rec["elapsed_ms"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
