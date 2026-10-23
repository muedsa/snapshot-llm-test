"""A01 自检：裁图放大查看 + 像素级几何核验（柱顶 / 网格 / 折线顶点 / 文字越界）。

启动基准：总任务根（cwd）。输出裁图到本题临时目录，供人工逐张查看。
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SUITE = Path.cwd()
sys.path.insert(0, str(SUITE / "tools"))
import verify as V  # noqa: E402

RID = "r20261014T1536+0800-5f11da"
PNG = SUITE / "outputs" / RID / "A01" / "operations.png"
TMP = SUITE / "tmp" / RID / "A01"

img = Image.open(PNG)
arr = V.load(PNG)
print(f"load ok {img.size} mode={img.mode}")

# --- 版面常量（与 a01_build.py 一致）--------------------------------------
M, GAP, LW, RW = 40, 24, 860, 636
Y_A, H_A = 262, 316
Y_B, H_B = 602, 304
GP_X, GP_Y, GP_W, GP_H = 76, 32, 744, 168
BAR_HI = 250000.0
BAR_TICKS = [0, 50000, 100000, 150000, 200000, 250000]
MX0, MPW, C1_P_Y, C1_H, C2_P_Y, C2_H = 62, 534, 22, 56, 142, 56
SES_HI, CVR_HI = 8000.0, 15.0
LW_BODY = (M + 20, Y_A + 20 + 22 * 1.45 + 10)        # (60, 323.9)
RW_BODY = (M + LW + GAP + 20, Y_A + 20 + 22 * 1.45 + 10)

NET, PROFIT, SESS, CVRC = "#2A78D6", "#EB6834", "#1BAF7A", "#6250D6"

# 图例色块（y 326-338）与 KPI 强调条（y 100-250）与柱/折线同色，须限定搜索区间，
# 否则 column_top/line_vertex 会取到图例或强调条的像素。
YMIN = 340


def col_top(color, x, ymin=YMIN):
    m = V.mask_of(arr, color)
    m[:ymin, :] = False
    v = V.column_top(m, x)
    return None if v is None else v


def vline_vertex(color, x, ymin=YMIN):
    m = V.mask_of(arr, color)
    m[:ymin, :] = False
    return V.line_vertex(m, x)

months = [
    ("2026-04", 119700, 37700, 3500, 12.00),
    ("2026-05", 135470, 41970, 4100, 11.22),
    ("2026-06", 126914, 27914, 4200, 10.60),
    ("2026-07", 161120, 49120, 4700, 11.28),
    ("2026-08", 173052, 41052, 5200, 10.96),
    ("2026-09", 202368, 64368, 5600, 11.07),
]

out = {"checks": [], "crops": []}


def chk(name, expected, actual, tol=2.0):
    r = V.report(name, expected, actual, tol)
    r["ok"] = bool(r["ok"])
    out["checks"].append(r)


def crop(name, box_, scale=2):
    p = TMP / "crops" / f"{name}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    im = img.crop(box_)
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(p)
    out["crops"].append(str(p.relative_to(SUITE)))


# --- 1. 分组柱图：12 根柱的顶沿 -------------------------------------------
slot = GP_W / len(months)
gw, bar_gap = 52, 6
grp_w = gw * 2 + bar_gap
for gi, (mo, net, prof, ses, cvr) in enumerate(months):
    gx = GP_X + gi * slot + (slot - grp_w) / 2
    for si, (v, col, tag) in enumerate(((net, NET, "net"), (prof, PROFIT, "profit"))):
        hgt = v / BAR_HI * GP_H
        exp_top = LW_BODY[1] + GP_Y + GP_H - hgt
        x = int(round(LW_BODY[0] + gx + si * (gw + bar_gap) + gw / 2))
        got = col_top(col, x)
        chk(f"柱 柱状{gi+1}-{tag} 顶沿", round(exp_top, 1), round(got, 1), 1.5)

# --- 2. 网格线与零基线 ----------------------------------------------------
# 1px 网格线画在浮点 y 上，栅格化会拆到相邻两行并抗锯齿变浅，按精确网格色逐行比对
# 必然误判；柱在网格之上绘制也会遮挡网格。故改在"无柱遮挡"的固定列上检查：
# 该行像素应为近灰（柱色与文字色饱和度高）且比面板底色深，y 容差 ±1px。
# x=261 落在第 0、1 组柱之间的 14px 空隙（组 0 利润柱止于 253，组 1 净收入柱起于 267），
# 也在网格线跨度 136..880 内。
GRID_C, AXIS_C = V.parse_hex("#E1E0D9"), V.parse_hex("#C3C2B7")
GAP_X = int(LW_BODY[0] + GP_X + 125)


def line_like(row, near, tol=80):
    """1px 线落在浮点 y 上时栅格化拆到相邻两行：最坏情况下该行只被覆盖 50%~70%，
    混白后 L1 距离可达 31~50，故容差取 80；同时要求近灰（柱色/文字色饱和度高被排除）。"""
    p = arr[row, GAP_X].astype(np.int16)
    if int(p.max() - p.min()) > 12:
        return False
    return int(np.abs(p - np.array(near)).sum()) <= tol


for t in BAR_TICKS:
    yy = LW_BODY[1] + GP_Y + GP_H - t / BAR_HI * GP_H
    near = AXIS_C if t == 0 else GRID_C
    hit_rows = [int(math.floor(yy)) + d for d in (-1, 0, 1)
                if 0 <= int(math.floor(yy)) + d < arr.shape[0]
                and line_like(int(math.floor(yy)) + d, near)]
    out["checks"].append({"check": f"网格 y={t} 存在且位置正确", "expected": 1,
                          "actual": len(hit_rows), "tol": 0,
                          "ok": bool(len(hit_rows) >= 1), "rows": hit_rows,
                          "expect_row": round(yy, 1), "col": GAP_X})

# --- 3. 访问量小图：6 根柱顶沿 --------------------------------------------
for gi, (mo, net, prof, ses, cvr) in enumerate(months):
    bh = ses / SES_HI * C1_H
    exp_top = RW_BODY[1] + C1_P_Y + C1_H - bh
    x = int(round(RW_BODY[0] + MX0 + gi * (MPW / 6) + (MPW / 6) / 2))
    got = col_top(SESS, x)
    chk(f"访问量 柱{gi+1} 顶沿", round(exp_top, 1), round(got, 1), 1.5)

# --- 4. 转化率折线：6 个顶点 ----------------------------------------------
for gi, (mo, net, prof, ses, cvr) in enumerate(months):
    y = C2_P_Y + C2_H - cvr / CVR_HI * C2_H
    x = int(round(RW_BODY[0] + MX0 + (gi + 0.5) * (MPW / 6)))
    got = vline_vertex(CVRC, x)
    chk(f"转化率 顶点{gi+1} y", round(RW_BODY[1] + y, 1), round(got, 1), 1.5)

# --- 5. 页面留白：上边距 28px 内无正文，正文底沿 ≤ 972 --------------------
BG = V.parse_hex("#F9F9F7")          # canvas background = PLANE
band_top = arr[0:28, 40:1560]
n_top = int((np.abs(band_top.astype(np.int16) - BG).sum(axis=2) > 40).sum())
out["checks"].append({"check": "上边距 0-28px 内无正文", "expected": 0,
                      "actual": n_top, "tol": 0, "ok": bool(n_top == 0)})
band_bot = arr[976:1000, 40:1560]
nb = int((np.abs(band_bot.astype(np.int16) - BG).sum(axis=2) > 40).sum())
rows_ink = np.where((np.abs(arr[900:1000, 40:1560].astype(np.int16) - BG).sum(axis=2) > 40).any(axis=1))[0]
bottom = int(rows_ink.max() + 900) if len(rows_ink) else 0
out["checks"].append({"check": "正文底沿 ≤ 972（下边距 ≥ 28）", "expected": 972,
                      "actual": bottom, "tol": 0, "ok": bool(nb == 0 and bottom <= 972)})
# 左右页边 40px 内无正文
for tag, sl in (("左边距", slice(0, 40)), ("右边距", slice(1560, 1600))):
    n = int((np.abs(arr[28:976, sl].astype(np.int16) - BG).sum(axis=2) > 40).sum())
    out["checks"].append({"check": f"{tag} 40px 内无正文", "expected": 0,
                          "actual": n, "tol": 0, "ok": n == 0})

# --- 6. 文字完整性：紧约束盒不能裁掉末位字符 ------------------------------
# 判定法（单向）：墨迹明显短于 text_width 估算 → 尾部被裁切
# （v2 里 "¥918,624" 丢失末位 "4"、"11.15%" 丢失 "%" 就是这种情况）；
# 墨迹略长于估算无害（文字自定宽，只是排版预算偏保守）。
# 另校验墨迹右沿不超过下一元素左沿（max_x），防贴字重叠。
# rect 须避开卡片右描边与左侧强调条，KPI3 的单位 "笔" 在其 rect 之外。
from dsl import text_width  # noqa: E402

WHITE = V.parse_hex("#FFFFFF")
TEXT_PROBES = [
    # (名称, 文本, 字号, 粗体, 墨迹搜索矩形, 允许的最右像素)
    ("KPI1 值", "¥918,624", 34, True, (63, 146, 401, 190), 401),
    ("KPI2 值", "¥262,124", 34, True, (448, 146, 786, 190), 786),
    ("KPI3 值", "3,045", 34, True, (834, 146, 933, 190), 933),
    ("KPI4 值", "11.15%", 34, True, (1221, 146, 1556, 190), 1556),
    ("KPI1 环比", "▲ 04→09 +69.1%", 16, True, (63, 194, 401, 220), 401),
    ("KPI4 环比", "▼ 04→09 −0.93pp", 16, True, (1221, 194, 1556, 220), 1556),
]
for name, s, size, bold, rect, max_x in TEXT_PROBES:
    rx0, ry0, rx1, ry1 = rect
    sub = arr[ry0:ry1, rx0:rx1]
    mk = np.abs(sub.astype(np.int16) - WHITE).sum(axis=2) > 42
    est = text_width(s, size, bold)
    if not mk.any():
        out["checks"].append({"check": f"文字完整 {name}", "expected": round(est, 1),
                              "actual": 0, "tol": 0, "ok": False})
        continue
    cols = np.where(mk.any(axis=0))[0]
    ix0, ix1 = int(cols.min() + rx0), int(cols.max() + rx0)
    cw = ix1 - ix0 + 1
    ratio = cw / est
    ok = bool(ratio >= 0.92 and ix1 <= max_x)
    out["checks"].append({"check": f"文字完整 {name}", "expected": round(est, 1),
                          "actual": cw, "tol": round(est * 0.08, 1), "ok": ok,
                          "ratio": round(ratio, 3), "ink": [ix0, ix1],
                          "max_x": max_x,
                          "note": "墨迹短于估算→疑似裁切" if ratio < 0.92 else
                                  ("墨迹越过下一元素" if ix1 > max_x else "完整")})

# --- 7. 裁图：逐区域查看（整幅 1x 便于通读，细节区 2x）---------------------
crop("k1_kpi_row", (36, 94, 810, 256), 1)
crop("k2_kpi_row", (800, 94, 1566, 256), 1)
crop("k3_chart_left", (40, 262, 900, 578), 1)
crop("k4_mini_right", (924, 262, 1560, 578), 1)
crop("k5_table", (40, 602, 900, 908), 1)
crop("k6_conclusion", (924, 602, 1560, 908), 1)
crop("k7_header", (36, 20, 1566, 100), 1)
crop("k8_footer", (36, 906, 1566, 1000), 1)
crop("z1_bars_m1_m2", (120, 330, 420, 560), 2)
crop("z2_mini_conversion", (940, 436, 1560, 580), 2)
crop("z3_kpi_values", (40, 138, 460, 220), 2)

rep_path = TMP / "inspect-report.json"
rep_path.write_text(json.dumps(out, ensure_ascii=False, indent=1,
                               default=lambda o: bool(o) if isinstance(o, (np.bool_, np.integer)) else float(o)),
                    encoding="utf-8")
fail = [c for c in out["checks"] if not c["ok"]]
# 控制台是 GBK，ensure_ascii=False 的 JSON 无法打印；摘要转成 ASCII 安全串输出。
def _a(s):
    return s.encode("ascii", "backslashreplace").decode("ascii")
print(f"report -> {rep_path.relative_to(SUITE)}")
print(f"FAIL {len(fail)} / {len(out['checks'])}")
for c in fail:
    print("  FAIL", _a(json.dumps(c, ensure_ascii=False,
                                  default=lambda o: bool(o) if isinstance(o, (np.bool_, np.integer)) else float(o))))
print("crops ->", *[str(Path(p).name) for p in out["crops"]], sep="\n  ")
