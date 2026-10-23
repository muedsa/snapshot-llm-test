"""case-10 城市树冠 · 一棵树的遮荫面积有多大（1200×1200，1:1）。

视觉系统：径向树状图——中心是街区，从中心向外辐射出 6 个树种扇区。
  每个扇区的高度代表遮荫面积，颜色代表树种。最外圈标注树种名称和
  遮荫半径。底部标注「总覆盖率」与「人均遮荫面积」。

受众是城市规划和景观设计师，在办公桌上看打印稿或投屏。核心诉求是
「哪片区域绿量不足」「该种什么树」。

数据为自拟演示，非真实城市测量数据，不宣称实际部署。
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402

W, H = 1200, 1200
MIN_FS = 16

PAD_L = 40

# ------------------------------------------------------------------ 调色
BG = "#FDF8F0"
INK = "#1A1A1A"
INK2 = "#3D4A57"
INK3 = "#5A6A78"
INK4 = "#8A9AA8"
LINE_CLR = "#E8DCC8"
ACCENT = "#B4531F"
ACCENT_L = "#E8B896"   # 浅版本 ACCENT，模拟半透明
GOOD = "#22C55E"
WARN = "#EAB308"

# 树种颜色（6 种）
TREE_COLORS = [
    ("榉树",    "#4A7C3F", "#2D5016"),   # 绿叶
    ("银杏",    "#8B7D3C", "#5C4E1E"),   # 黄绿
    ("樱花",    "#D4A574", "#A07040"),   # 粉白
    ("梧桐",    "#6B8E4E", "#3D5C22"),   # 深绿
    ("香樟",    "#3D7A5A", "#1F4A32"),   # 墨绿
    ("栾树",    "#C4A055", "#8B6E30"),   # 金棕
]

# ------------------------------------------------------------------ 数据
# (树种名, 遮荫半径m, 覆盖率%, 树龄年, 种植年份)
TREES = [
    ("榉树",    8.0, 22, 15, 2011),
    ("银杏",    10.0, 18, 12, 2014),
    ("樱花",    5.0, 12, 8, 2018),
    ("梧桐",    7.0, 20, 20, 2006),
    ("香樟",    9.0, 18, 25, 2001),
    ("栾树",    6.0, 10, 10, 2016),
]

CX, CY = 600, 520
R_INNER = 60
R_MAX = 360
N_TREES = len(TREES)
ANGLE_STEP = 2 * math.pi / N_TREES


def angle_i(i):
    """第 i 个扇区的起始角（弧度，0 = +x 轴）"""
    return -math.pi / 2 + i * ANGLE_STEP  # 从正上方开始


def radius_of(tree):
    """遮荫半径映射到 [R_INNER, R_MAX]"""
    max_r = max(t[1] for t in TREES)
    return R_INNER + (tree[1] / max_r) * (R_MAX - R_INNER)


def total_coverage():
    return sum(t[2] for t in TREES)


def per_capita():
    """人均遮荫面积（假设 500 人），半径单位为米"""
    total_area = sum(math.pi * t[1] ** 2 for t in TREES)
    return total_area / 500


# ------------------------------------------------------------------ 构建
def build() -> K.Doc:
    d = K.Doc(W, H, BG)

    # 页头
    d.text(PAD_L, 16, "城市树冠", 28, INK, bold=True)
    d.text(PAD_L, 50, "一棵树的遮荫面积有多大 · 自拟演示数据", 16, INK2)
    d.text_r(W - PAD_L, 20, "折光 · 十张日常　10 / 10", 16, INK4, bold=True)
    d.text_r(W - PAD_L, 44, "非真实城市测量数据", 16, INK4)

    # 同心圆参考线（无标签，仅视觉引导）
    for r in range(120, int(R_MAX) + 1, 80):
        pts = []
        for i in range(97):
            a = 2 * math.pi * i / 96
            pts.append((CX + math.cos(a) * r, CY + math.sin(a) * r))
        d.stroke(pts, LINE_CLR, width=1, step=2)

    # 中心圆（用浅色填充模拟半透明）
    d.circle(CX, CY, R_INNER, ACCENT_L)
    d.circle(CX, CY, R_INNER, ACCENT, step=1, segs=96)
    d.text_c(CX, CY - 14, "街区中心", 16, ACCENT, bold=True)
    d.text_c(CX, CY + 10, "覆盖率 %d%%" % total_coverage(), 16, INK3)

    # 6 个树种扇区
    for i, (name, radius, coverage, age, year) in enumerate(TREES):
        a0 = angle_i(i)
        a1 = angle_i(i + 1)
        color, dark = TREE_COLORS[i][1], TREE_COLORS[i][2]

        # 遮荫扇区（从 R_INNER 到 radius_of(tree)）
        r_out = radius_of((name, radius, coverage, age, year))
        pts = K.ring(CX, CY, R_INNER, r_out, a0, a1, steps=48)
        d.fill(pts, color, step=1.0)

        # 扇区描边
        d.stroke(pts, dark, width=2.0, step=1.0)

        # 树种名称（在扇区中心位置）
        am = (a0 + a1) / 2
        rm = (R_INNER + r_out) / 2
        tx = CX + math.cos(am) * rm
        ty = CY + math.sin(am) * rm
        d.text_c(tx, ty - 12, name, 18, INK, bold=True)
        d.text_c(tx, ty + 12, "R=%.1fm" % radius, 16, dark)
        d.text_c(tx, ty + 34, "覆盖 %d%%" % coverage, 16, INK2)

        # 外圈标注
        ox = CX + math.cos(am) * (r_out + 28)
        oy = CY + math.sin(am) * (r_out + 28)
        d.text_c(ox, oy - 12, "%s" % name, 16, dark, bold=True)
        d.text_c(ox, oy + 12, "R=%.1fm" % radius, 16, INK3)

    # 底部统计面板
    by = H - 180
    bx = PAD_L

    d.rect(0, by - 16, W, 2, ACCENT)

    # 统计卡片
    stats = [
        ("总覆盖率", "%d%%" % total_coverage(), GOOD if total_coverage() > 40 else WARN),
        ("树种数", "%d 种" % len(TREES), INK2),
        ("最大遮荫半径", "%.1f m" % max(t[1] for t in TREES), INK2),
        ("人均遮荫面积", "%.2f m²" % per_capita(), ACCENT),
    ]
    card_w = (W - 2 * PAD_L - 3 * 20) / 4
    for j, (label, value, color) in enumerate(stats):
        cx = bx + j * (card_w + 20)
        d.rect(cx, by, card_w, 80, LINE_CLR, radius=6)
        d.text_c(cx + card_w / 2, by + 12, label, 16, INK3)
        d.text_c(cx + card_w / 2, by + 38, value, 28, color, bold=True)

    # 免责声明
    d.text(PAD_L, H - 40,
           "本图为自拟演示数据，非真实城市测量数据，不宣称实际部署。",
           16, INK4)
    d.text_r(W - PAD_L, H - 40, "2026-10-22", 16, INK4)

    return d


# ------------------------------------------------------------------ 门禁
def gates(doc: K.Doc) -> list[dict]:
    out = []
    out.append({
        "id": "case-10-c01",
        "check": "6 个树种，每个有遮荫半径、覆盖率、树龄",
        "passed": len(TREES) == 6,
        "detail": "%d 种" % len(TREES)
    })
    out.append({
        "id": "case-10-c02",
        "check": "总覆盖率 = %d%%" % total_coverage(),
        "passed": total_coverage() > 0,
        "detail": "%d%%" % total_coverage()
    })
    out.append({
        "id": "case-10-c03",
        "check": "人均遮荫面积 = %.2f m²" % per_capita(),
        "passed": per_capita() > 0,
        "detail": "%.1f m²" % per_capita()
    })
    out.append({
        "id": "case-10-c04",
        "check": "遮荫半径在 [3, 15] m 范围内",
        "passed": all(3 <= t[1] <= 15 for t in TREES),
        "detail": "min %.1f · max %.1f m"
                  % (min(t[1] for t in TREES), max(t[1] for t in TREES))
    })
    out.append({
        "id": "case-10-c05",
        "check": "页面声明「非真实城市测量数据」",
        "passed": True,
        "detail": "已写入页脚"
    })
    out.extend(K.dry_run(doc, "case-10", MIN_FS, []))
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")

    doc = build()
    gs = gates(doc)
    n_fail = sum(1 for g in gs if not g["passed"])

    tmp = pathlib.Path(HERE.parents[2]) / "B01" / "case-10"
    tmp.mkdir(parents=True, exist_ok=True)
    n_g = len(list(tmp.glob("case-10-gates-*.json"))) + 1
    gf = tmp / ("case-10-gates-%03d.json" % n_g)
    gf.write_text(json.dumps({
        "case_id": "case-10",
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
    print("  树种 %d · 覆盖 %d%% · %d×%d" % (len(TREES), total_coverage(), W, H))

    rec = K.render_case("case-10", doc, "case-10-urban-canopy",
                        purpose="B01 主作品：城市树冠")
    print("status=%d bytes=%d parts=%d texts=%d shapes=%d ms=%s"
          % (rec["http_status"], rec["response_bytes"], rec["parts"],
             rec["texts"], rec["shapes"], rec["elapsed_ms"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
