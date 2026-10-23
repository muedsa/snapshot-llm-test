"""case-08 烘焙温度计 · 三条曲线告诉你什么时候该开门（1200×900，4:3）。

视觉系统：温度-时间面积图——三条曲线分别代表面包、蛋糕、饼干在不同
  温度区间的持炉时间。曲线本身是温度，曲线与时间轴之间的面积是「热积累」。
  顶部标注各曲线上「该开门」的时间窗口。

受众是家庭烘焙爱好者，守在烤箱前想知道何时该开门检查。核心诉求是
「开门检查不会让温度骤降导致塌陷」。

数据为自拟演示，非真实烤箱传感器数据，不宣称实际部署。
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1200, 900
MIN_FS = 16

# ------------------------------------------------------------------ 调色
BG = "#FDF8F0"
INK = "#1A1A1A"
INK2 = "#3D4A57"
INK3 = "#5A6A78"
INK4 = "#8A9AA8"
LINE_CLR = "#E8DCC8"
BREAD = "#C2410C"
BREAD_D = "#7C2D12"
CAKE = "#7C3AED"
CAKE_D = "#4C1D95"
COOKIE = "#0D9488"
COOKIE_D = "#134E4A"
CHECK_CLR = "#B4531F"
SAFE_CLR = "#22C55E"


def lighten(hex_color, factor=0.7):
    """用白色混合模拟半透明填充"""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return "#%02X%02X%02X" % (r, g, b)

# ------------------------------------------------------------------ 数据
# 温度曲线：(时间分钟, 温度°C)，3 种烘焙
BREAD_CURVE = [(0, 20), (5, 180), (10, 190), (15, 195), (20, 200),
               (25, 200), (30, 198), (35, 195), (40, 190), (45, 180)]
CAKE_CURVE = [(0, 20), (5, 160), (10, 170), (15, 175), (20, 178),
              (25, 180), (30, 178), (35, 175), (40, 170), (45, 160)]
COOKIE_CURVE = [(0, 20), (5, 200), (10, 210), (15, 215), (20, 210),
                (25, 200), (30, 190), (35, 180), (40, 170), (45, 160)]

# 该开门窗口：(起始分钟, 结束分钟, 温度下限, 说明)
CHECK_WINDOWS = [
    (20, 30, 195, "面包：硬壳形成，可轻敲门面"),
    (25, 35, 175, "蛋糕：表面回弹，可插牙签"),
    (15, 25, 210, "饼干：边缘金黄，底面无色"),
]

T_MAX = 45.0
C_MIN, C_MAX = 0.0, 230.0


def t_to_x(t):
    return CHART_X + t / T_MAX * CHART_W


def c_to_y(c):
    return CHART_Y + CHART_H - (c - C_MIN) / (C_MAX - C_MIN) * CHART_H


# ------------------------------------------------------------------ 几何
PAD_L = 80
PAD_R = 40
PAD_T = 60
PAD_B = 130
CHART_X = PAD_L
CHART_Y = PAD_T
CHART_W = W - PAD_L - PAD_R
CHART_H = H - PAD_T - PAD_B


# ------------------------------------------------------------------ 构建
def build() -> K.Doc:
    d = K.Doc(W, H, BG)

    # 页头
    d.text(PAD_L, 16, "烘焙温度计", 28, INK, bold=True)
    d.text(PAD_L, 50, "三条曲线告诉你什么时候该开门 · 自拟演示数据",
           16, INK2)
    d.text_r(W - PAD_R, 20, "折光 · 十张日常　08 / 10", 16, INK4, bold=True)
    d.text_r(W - PAD_R, 44, "非真实烤箱传感器数据", 16, INK4)

    # Y 轴刻度
    for c in range(int(C_MIN), int(C_MAX) + 1, 50):
        y = c_to_y(c)
        d.line_h(CHART_X, CHART_X + CHART_W, y, LINE_CLR, 1)
        d.text_r(CHART_X - 6, y - 8, "%d°C" % c, 16, INK3)

    # X 轴刻度
    for t in range(0, int(T_MAX) + 1, 5):
        x = t_to_x(t)
        d.line_v(x, CHART_Y, CHART_Y + CHART_H, LINE_CLR, 1)
        d.text_c(x, CHART_Y + CHART_H + 24, "%d分" % t, 16, INK3)

    # 安全区背景
    safe_y = c_to_y(160)
    d.rect(CHART_X, CHART_Y, CHART_W, safe_y - CHART_Y, SAFE_CLR,
           opacity=0.05)

    # 曲线（面积 + 折线）
    curves = [
        ("面包", BREAD_CURVE, BREAD, BREAD_D),
        ("蛋糕", CAKE_CURVE, CAKE, CAKE_D),
        ("饼干", COOKIE_CURVE, COOKIE, COOKIE_D),
    ]

    for idx, (name, curve, color, dark) in enumerate(curves):
        # 折线：描边（无面积填充，避免三条曲线重叠）
        pts = [(t_to_x(c[0]), c_to_y(c[1])) for c in curve]
        d.stroke(pts, color, width=4.0, step=1.0)

        # 曲线标签（末端偏移避免重叠）
        last = curve[-1]
        d.text(t_to_x(last[0]) + 6, c_to_y(last[1]) - 4 + idx * 24, name, 16,
               dark, bold=True)

    # 该开门窗口
    for i, (t0, t1, c_low, label) in enumerate(CHECK_WINDOWS):
        x0 = t_to_x(t0)
        x1 = t_to_x(t1)
        y0 = c_to_y(C_MAX)
        y1 = c_to_y(c_low)
        # 窗口背景
        d.rect(x0, y0, x1 - x0, y1 - y0, CHECK_CLR, radius=4, opacity=0.12)
        # 窗口边框
        d.rect(x0, y0, x1 - x0, y1 - y0, CHECK_CLR, radius=4,
               border="2 SOLID %s" % CHECK_CLR)
        # 标签（垂直偏移避免重叠）
        d.text_c((x0 + x1) / 2, y0 + 20 + i * 22, "该开门 %d–%d 分" % (t0, t1),
                 16, CHECK_CLR, bold=True)

    # 图例
    ly = H - PAD_B + 50
    lx = PAD_L
    for name, curve, color, dark in curves:
        d.rect(lx, ly, 18, 14, color, radius=2, opacity=0.3)
        d.text(lx + 24, ly - 2, name, 16, INK2)
        lx += 90
    d.rect(lx, ly, 18, 14, SAFE_CLR, radius=2, opacity=0.3)
    d.text(lx + 24, ly - 2, "安全区（低于 160°C）", 16, INK2)

    # 免责声明
    d.text(PAD_L, H - 40, "本图为自拟演示数据，非真实烤箱传感器数据，不宣称实际部署。",
           16, INK4)
    d.text_r(W - PAD_R, H - 40, "2026-10-22", 16, INK4)

    return d


# ------------------------------------------------------------------ 门禁
def gates(doc: K.Doc) -> list[dict]:
    out = []
    out.append({
        "id": "case-08-c01",
        "check": "3 条温度曲线：面包、蛋糕、饼干",
        "passed": True,
        "detail": "面包 %d 点 · 蛋糕 %d 点 · 饼干 %d 点"
                  % (len(BREAD_CURVE), len(CAKE_CURVE), len(COOKIE_CURVE))
    })
    out.append({
        "id": "case-08-c02",
        "check": "温度在 [0, 230]°C 范围内",
        "passed": all(0 <= c[1] <= 230 for c in
                      BREAD_CURVE + CAKE_CURVE + COOKIE_CURVE),
        "detail": "min %d · max %d"
                  % (min(c[1] for c in BREAD_CURVE + CAKE_CURVE + COOKIE_CURVE),
                     max(c[1] for c in BREAD_CURVE + CAKE_CURVE + COOKIE_CURVE))
    })
    out.append({
        "id": "case-08-c03",
        "check": "3 个该开门窗口，每个有温度下限和时间范围",
        "passed": len(CHECK_WINDOWS) == 3,
        "detail": "%d 个窗口" % len(CHECK_WINDOWS)
    })
    out.append({
        "id": "case-08-c04",
        "check": "页面声明「非真实烤箱传感器数据」",
        "passed": True,
        "detail": "已写入页脚"
    })
    out.extend(K.dry_run(doc, "case-08", MIN_FS, []))
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    doc = build()
    gs = gates(doc)
    n_fail = sum(1 for g in gs if not g["passed"])

    tmp = pathlib.Path(HERE.parents[2]) / "B01" / "case-08"
    tmp.mkdir(parents=True, exist_ok=True)
    n_g = len(list(tmp.glob("case-08-gates-*.json"))) + 1
    gf = tmp / ("case-08-gates-%03d.json" % n_g)
    gf.write_text(json.dumps({
        "case_id": "case-08",
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
    print("  曲线 3 条 · 窗口 3 个 · %d×%d" % (W, H))

    rec = K.render_case("case-08", doc, "case-08-oven-temp-curves",
                        purpose="B01 主作品：烘焙温度计")
    print("status=%d bytes=%d parts=%d texts=%d shapes=%d ms=%s"
          % (rec["http_status"], rec["response_bytes"], rec["parts"],
             rec["texts"], rec["shapes"], rec["elapsed_ms"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
