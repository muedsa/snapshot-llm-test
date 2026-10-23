"""A04 像素自检：对渲染结果做几何与颜色测量，逐项核验题面要求。

几何期望值在本脚本里**重新推导**（不复用 a04_build 的计算结果），
这样测量与被测对象相互独立：若构造器算错，这里会算出不同的期望值并判失败。

启动基准：总任务根（cwd）。用法：python a04_inspect.py <png相对路径>
输出：tmp/.../A04/inspect-<tag>.json
"""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image

import a04_io as IO

OUT, TMP = IO.dirs()
MODEL = json.loads((TMP / "model.json").read_text(encoding="utf-8"))

# ---------------- 从原始 CSV 重新推导期望值 ----------------
G = {(g["period"], g["channel"]): g for g in MODEL["groups"]}
P = {p["period"]: p for p in MODEL["periods"]}
P1, P2, C1N, C2N = "前期", "后期", "直接访问", "推广访问"
RATE = {(p, c): G[(p, c)]["rate_percent_exact"] for p in (P1, P2)
        for c in (C1N, C2N)}
SHARE = {}
for p in (P1, P2):
    for c in P[p]["composition"]:
        SHARE[(p, c["channel"])] = c["share_percent_display"]
VIS = {(p, c): G[(p, c)]["visits"] for p in (P1, P2) for c in (C1N, C2N)}
TOT = {p: P[p]["total_visits"] for p in (P1, P2)}
OV = {p: P[p]["overall_rate_percent_exact"] for p in (P1, P2)}

# 校验模型本身没算错：总体必须等于成交总数/访问总数
for p in (P1, P2):
    tc = P[p]["total_conversions"]
    tv = P[p]["total_visits"]
    assert Fraction(tc, tv) == Fraction(P[p]["overall_exact_fraction"]), p
    assert sum(VIS[(p, c)] for c in (C1N, C2N)) == tv, p

# ---------------- 版式常量（与 a04_build 独立书写） ----------------
CW, CH, MARGIN = 1600, 1000, 40
PX = 2.6                     # 每 1% 的像素
O1_X, O3_X = 256, 1230       # 率轴起点
CB_X, CB_W, BAR2_GAP = 584, 420, 2
C2_X, CP_W = 560, 500        # 图②面板左边缘与宽度（构成注的行界）
CH_Y, CH_H = 396, 340        # 三张图所在面板的顶边与高度
CON_Y_TOP, CON_H, BOX_A_W, BOX_B_X, BOX_B_W = 750, 210, 990, 1050, 510
BOX_A_RIGHT = MARGIN + BOX_A_W          # 1030
BOX_B_RIGHT = BOX_B_X + BOX_B_W         # 1560
PAD = 24                                # 面板内左边距
RUN_ID = "r20261014T1536+0800-5f11da"

CHART1_ROWS = [506, 538, 604, 636]          # 4 个分组条形顶边
CHART3_ROWS = [502, 592]                    # 2 条总体条形顶边
CHART2_ROWS = [532, 630]
BAR2_H = 62

BG = (0xF8, 0xFA, 0xFC)
WHITE = (0xFF, 0xFF, 0xFF)
INK = (0x0F, 0x17, 0x2A)
DIRECT, DIRECTL, DIRECTD = (0x25, 0x63, 0xEB), (0x93, 0xC5, 0xFD), (0x1E, 0x40, 0xAF)
PROMO, PROMOL, PROMOD = (0xDB, 0x27, 0x77), (0xF9, 0xA8, 0xD4), (0x9D, 0x17, 0x4D)
TOTAL, TOTALL = (0x0F, 0x76, 0x6E), (0x5E, 0xEA, 0xD4)

CHART1_EXPECT = [(P1, C1N, DIRECTL), (P2, C1N, DIRECTD),
                 (P1, C2N, PROMOL), (P2, C2N, PROMOD)]
CHART3_EXPECT = [(P1, TOTALL), (P2, TOTAL)]


def near(a, b, tol=24):
    return np.all(np.abs(np.array(a, np.int16) - np.array(b, np.int16)) <= tol,
                  axis=-1)


def run_from(img, y, x0, color, tol=24):
    """从 (x0, y) 向右量同色连续像素长度，返回 (起点, 终点)。"""
    row = img[y]
    m = near(row, color, tol)
    x = x0
    while x < img.shape[1] and m[x]:
        x += 1
    return x0, x


def find_run(img, y, color, x_lo=0, x_hi=None, tol=24, min_len=4):
    """在 [x_lo, x_hi) 内找第一个长度 ≥ min_len 的同色连续段。"""
    row = img[y]
    m = near(row, color, tol)
    x_hi = x_hi or img.shape[1]
    x = x_lo
    while x < x_hi:
        if m[x]:
            x0 = x
            while x < x_hi and m[x]:
                x += 1
            if x - x0 >= min_len:
                return x0, x
        else:
            x += 1
    return None


def seg_extent(img, y0, y1, color, x_lo=0, x_hi=None, tol=24, min_px=60):
    """段在 [x_lo,x_hi)×[y0,y1) 内的最左/最右同色像素。

    不用单行连续段扫描：条内部有白色数值标签，会把单行 run 打断。
    取整块区域内同色像素的 min/max x，圆角只影响最左/最右的中部行，
    而中部的左右边缘是满宽的，所以量出来就是真实段宽。
    """
    x_hi = x_hi or img.shape[1]
    sub = img[y0:y1, x_lo:x_hi]
    m = near(sub, color, tol)
    ys, xs = np.where(m)
    if len(xs) < min_px:
        return None
    return int(x_lo + xs.min()), int(x_lo + xs.max())


def ink_bbox(img, box, ink_max=0x80, exclude=()):
    """区域内「比阈值暗」的像素外接框，用于量文字高度。

    exclude 传需要排除的装饰色（面板边框、网格线）：面板边框本身也是深色，
    不排除的话会把「文字贴到边框」误判成「文字越出边框」。
    """
    x0, y0, x1, y1 = box
    sub = img[y0:y1, x0:x1].astype(np.int16)
    lum = sub.max(axis=2)
    mask = lum <= ink_max
    for c in exclude:
        mask &= ~near(sub, np.array(c, np.int16), 45)
    if not mask.any():
        return None
    ys, xs = np.where(mask)
    return [int(x0 + xs.min()), int(y0 + ys.min()),
            int(x0 + xs.max()), int(y0 + ys.max())]


def _in_rounded(px, py, x0, y0, x1, y1, r):
    """像素中心是否落在圆角矩形 [x0,y0,x1,y1) 内（四角半径 r）。"""
    m = (px >= x0) & (px < x1) & (py >= y0) & (py < y1)
    for cx, cy, sx, sy in ((x0 + r, y0 + r, 1, 1), (x1 - r, y0 + r, -1, 1),
                           (x1 - r, y1 - r, -1, -1), (x0 + r, y1 - r, 1, -1)):
        in_sq = ((px - cx) * sx < 0) & ((py - cy) * sy < 0)
        d2 = (px - cx) ** 2 + (py - cy) ** 2
        m &= (~in_sq) | (d2 <= r * r)
    return m


def border_zone(px, py, x0, y0, x1, y1, r, stroke, halo=2.0):
    """圆角矩形描边的占位掩膜：外框内、内缩 stroke 后的圆角矩形外，再向两侧扩 halo。

    直线段上的描边是无抗锯齿的纯 stroke 环（实测 2px 边框恰好落在纯色两整行上）；
    但**圆角弧是斜线**，2px 描边在屏上展开约 2.8px，抗锯齿向内侧与外侧各扩 ~1.4px。
    只排除 [r-stroke, r] 环带会漏掉弧内侧那圈深色晕——实测它最深到 (77,153,147)，
    仍低于 0xC0 的墨迹阈值，于是整圈边框的晕被当成正文，外接框直接撑满面板。
    按几何排除（而不是按颜色阈值）在这里是唯一稳的做法：颜色法还得再切掉
    「边框色 × 面板白底」的中间灰，阈值根本调不干净。
    """
    return (_in_rounded(px, py, x0 - halo, y0 - halo, x1 + halo, y1 + halo,
                        r + halo)
            & ~_in_rounded(px, py, x0 + stroke + halo, y0 + stroke + halo,
                           x1 - stroke - halo, y1 - stroke - halo,
                           max(r - stroke - halo, 0.0)))


def ink_of(img, x0, y0, x1, y1, zones, halo=2.0):
    """区域内非装饰墨迹的外接框。

    zones 为 [(rect_x0, rect_y0, rect_x1, rect_y1, 圆角半径, 描边宽度), ...]，
    按几何从掩膜里剔除描边及其抗锯齿晕，只留正文墨迹。
    """
    sub = img[y0:y1, x0:x1].astype(np.int16)
    h, w = sub.shape[0], sub.shape[1]
    px = (x0 + np.arange(w, dtype=np.float32) + 0.5)[None, :]
    py = (y0 + np.arange(h, dtype=np.float32) + 0.5)[:, None]
    m = sub.max(axis=2) <= 0xC0
    for zx0, zy0, zx1, zy1, zr, zw in zones:
        m &= ~border_zone(px, py, zx0, zy0, zx1, zy1, zr, zw, halo)
    if not m.any():
        return None
    ys, xs = np.where(m)
    return [int(x0 + xs.min()), int(y0 + ys.min()),
            int(x0 + xs.max()), int(y0 + ys.max())]


def main(png_rel: str, tag: str) -> int:
    src = IO.ROOT / png_rel
    img = np.asarray(Image.open(src).convert("RGB"))
    h, w = img.shape[:2]
    R = {"schema_version": 1, "task_id": "A04", "path_base": "output_dir",
         "timezone": "Asia/Shanghai (UTC+08:00)",
         "png": png_rel, "size": [int(w), int(h)], "checks": []}

    def chk(name, passed, expected, actual, note=""):
        R["checks"].append({"name": name, "passed": bool(passed),
                            "expected": expected, "actual": actual,
                            "note": note})

    # --- 1 画布尺寸 ---
    chk("canvas_size_1600x1000", (w, h) == (CW, CH), [CW, CH], [w, h])

    # --- 2 背景与四角 ---
    corners = {"tl": img[3, 3], "tr": img[3, w - 4],
               "bl": img[h - 4, 3], "br": img[h - 4, w - 4]}
    # 必须转成原生 int：numpy uint8 不能被 json 序列化
    ok = all(tuple(c) == BG for c in corners.values())
    chk("page_background_F8FAFC", ok, list(BG),
        [[int(v) for v in c] for c in corners.values()])

    # --- 3 安全边距：外 36px 内不应出现前景（白面板/深色文字） ---
    band = np.concatenate([
        img[:36, :].reshape(-1, 3), img[h - 36:, :].reshape(-1, 3),
        img[:, :36].reshape(-1, 3), img[:, w - 36:].reshape(-1, 3)])
    n_fg = int((~np.all(band == np.array(BG), axis=1)).sum())
    chk("safe_margin_36px_no_content", n_fg == 0, 0, n_fg,
        "内容区 x/y ∈ [40,1560]/[40,960]，外 36px 应为纯页面底色")

    # --- 4 图① 四条分组的长度与标签一致 ---
    got1, exp1 = [], []
    for y_top, (p, c, col) in zip(CHART1_ROWS, CHART1_EXPECT):
        y = y_top + 13
        seg = find_run(img, y, col, x_lo=200, x_hi=560)
        got1.append(None if not seg else seg[1] - seg[0])
        exp1.append(RATE[(p, c)] * PX)
        if seg:
            print(f"  图① {p} {c}: 量得 {seg[1]-seg[0]:.0f}px "
                  f"(期望 {RATE[(p,c)]*PX:.1f}px) 起点 x={seg[0]}")
    tol_len = 1.6
    ok = all(g is not None and abs(g - e) <= tol_len for g, e in zip(got1, exp1))
    chk("chart1_bar_lengths_match_rates", ok,
        [round(e, 1) for e in exp1],
        [None if g is None else round(g, 1) for g in got1],
        f"容差 ±{tol_len}px（圆角与抗锯齿）")

    # --- 5 图③ 两条总体的长度 ---
    got3, exp3 = [], []
    for y_top, (p, col) in zip(CHART3_ROWS, CHART3_EXPECT):
        y = y_top + 17
        seg = find_run(img, y, col, x_lo=1150, x_hi=1560)
        got3.append(None if not seg else seg[1] - seg[0])
        exp3.append(OV[p] * PX)
        if seg:
            print(f"  图③ {p}: 量得 {seg[1]-seg[0]:.0f}px "
                  f"(期望 {OV[p]*PX:.1f}px) 起点 x={seg[0]}")
    ok = all(g is not None and abs(g - e) <= tol_len for g, e in zip(got3, exp3))
    chk("chart3_bar_lengths_match_overall", ok,
        [round(e, 1) for e in exp3],
        [None if g is None else round(g, 1) for g in got3])

    # --- 6 图①与图③同一 0–100% 尺度：每 1% 的像素必须一致 ---
    def px_per_pct(lengths, pcts):
        return [g / p for g, p in zip(lengths, pcts) if g is not None]

    k1 = px_per_pct(got1, [RATE[k] for k in [(P1, C1N), (P2, C1N),
                                             (P1, C2N), (P2, C2N)]])
    k3 = px_per_pct(got3, [OV[P1], OV[P2]])
    m1 = float(np.mean(k1)) if k1 else float("nan")
    m3 = float(np.mean(k3)) if k3 else float("nan")
    delta = abs(m1 - m3)
    chk("same_0_100pct_scale_chart1_vs_chart3",
        m1 and m3 and delta <= 0.06, f"两图 px/1% 差 ≤ 0.06，均为 {PX}",
        {"chart1_px_per_pct": round(m1, 4), "chart3_px_per_pct": round(m3, 4),
         "abs_diff": round(delta, 4)})

    # --- 7 构成图两期等长，分段按真实占比 ---
    seg_info = {}
    for i, p in enumerate((P1, P2)):
        y0, y1 = CHART2_ROWS[i], CHART2_ROWS[i] + BAR2_H
        d_seg = seg_extent(img, y0, y1, DIRECT, x_lo=560, x_hi=1060)
        p_seg = seg_extent(img, y0, y1, PROMO, x_lo=560, x_hi=1060)
        seg_info[p] = {"direct": d_seg, "promo": p_seg}
        if d_seg and p_seg:
            total = p_seg[1] - d_seg[0]
            dw = d_seg[1] - d_seg[0]
            pw = p_seg[1] - p_seg[0]
            print(f"  构成 {p}: 总长 {total}px 直接 {dw}px 推广 {pw}px")
            seg_info[p]["total"] = total
            seg_info[p]["direct_w"] = dw
            seg_info[p]["promo_w"] = pw
            seg_info[p]["boundary_x"] = d_seg[1]

    t1 = seg_info.get(P1, {}).get("total")
    t2 = seg_info.get(P2, {}).get("total")
    chk("composition_bars_equal_length",
        t1 is not None and t2 is not None and abs(t1 - t2) <= 2.0,
        f"两条总长相同（{CB_W}px = 各期 {TOT[P1]:,} 次）",
        {"前期": t1, "后期": t2,
         "abs_diff": None if (t1 is None or t2 is None) else abs(t1 - t2)})

    # 分段比例应等于真实访问占比
    ratio_ok, ratio_detail = True, {}
    for p in (P1, P2):
        s = seg_info.get(p, {})
        dw, pw = s.get("direct_w"), s.get("promo_w")
        if not dw or not pw:
            ratio_ok = False
            continue
        total = dw + pw
        r_direct = dw / total * 100
        ratio_detail[p] = {"measured_direct_pct": round(r_direct, 2),
                           "expected_direct_pct": SHARE[(p, C1N)],
                           "measured_boundary_x": s.get("boundary_x"),
                           "expected_boundary_x": round(
                               CB_X + VIS[(p, C1N)] / TOT[p] * (CB_W - BAR2_GAP), 1)}
        if abs(r_direct - SHARE[(p, C1N)]) > 1.2:
            ratio_ok = False
    chk("composition_segments_match_true_share", ratio_ok,
        "分段占比 = 访问数占比（容差 1.2pp）", ratio_detail)

    # --- 8 文字高度：正文明显大于图标注，且图标注不小于 18 号比例 ---
    # ink_max 必须 ≥ 0xC0：刻度是 INK3 #64748B（最高通道 139），用默认 0x80 会量不到
    t_title = ink_bbox(img, (40, 40, 900, 96), ink_max=0xC0)              # 38 号标题
    t_body = ink_bbox(img, (64, CON_Y_TOP + 52, 1000, CON_Y_TOP + 86),
                      ink_max=0xC0)                                       # 22 号正文第1行
    t_tick = ink_bbox(img, (O1_X - 28, 666, O1_X + 28, 696), ink_max=0xC0)  # 18 号刻度
    t_val = ink_bbox(img, (342, 506, 400, 532), ink_max=0xC0)             # 18 号数值

    def hh(b):
        return None if not b else b[3] - b[1]

    r_ratio = None
    if hh(t_title) and hh(t_body):
        r_ratio = round(hh(t_title) / hh(t_body), 3)
    chk("font_size_hierarchy_22_body_vs_18_annotation",
        hh(t_tick) is not None and hh(t_body) is not None
        and hh(t_body) >= hh(t_tick) + 2,
        "正文(22) 墨迹高度 ≥ 图标注(18) + 2px",
        {"title_h": hh(t_title), "body_h": hh(t_body),
         "tick_h": hh(t_tick), "value_h": hh(t_val),
         "title_over_body": r_ratio,
         "expect_title_over_body": round(38 / 22, 3)},
        "标题38/正文22 ≈ 1.727")

    # --- 9 结论与限制区存在且互不重叠 ---
    boxA = img[CON_Y_TOP:CON_Y_TOP + CON_H, MARGIN:MARGIN + BOX_A_W]
    boxB = img[CON_Y_TOP:CON_Y_TOP + CON_H, BOX_B_X:BOX_B_X + BOX_B_W]
    inkA = int((boxA.astype(np.int16).max(axis=2) <= 0x80).sum())
    inkB = int((boxB.astype(np.int16).max(axis=2) <= 0x80).sum())
    chk("conclusion_and_limitation_both_present",
        inkA > 400 and inkB > 200, "两框均有正文墨迹",
        {"boxA_ink_px": inkA, "boxB_ink_px": inkB})

    # --- 10 数值口径交叉核对：图③标称值 = 成交总数/访问总数 ---
    fracs = []
    for p in (P1, P2):
        f = Fraction(P[p]["total_conversions"], P[p]["total_visits"])
        fracs.append({"period": p,
                      "numerator": P[p]["total_conversions"],
                      "denominator": P[p]["total_visits"],
                      "value_pct": round(float(f * 100), 2),
                      "model_pct": round(OV[p], 2),
                      "match": abs(float(f * 100) - OV[p]) < 1e-9})
    chk("overall_is_total_over_total",
        all(x["match"] for x in fracs),
        "总体率 = 成交总数 ÷ 访问总数（未取渠道平均）", fracs)

    # --- 11 未加权平均渠道比例与本图总体口径不同向（说明禁止算法的后果） ---
    naive = {}
    for p in (P1, P2):
        r = sum(RATE[(p, c)] for c in (C1N, C2N)) / 2
        naive[p] = round(r, 2)
    naive_delta = round(naive[P2] - naive[P1], 2)
    true_delta = round(OV[P2] - OV[P1], 2)
    chk("prohibited_mean_would_be_wrong_direction",
        naive_delta * true_delta < 0 or naive_delta == 0,
        f"未加权平均 Δ={naive_delta:+.2f}pp 与真实 Δ={true_delta:+.2f}pp 方向相反",
        {"naive_mean_pct": naive, "naive_delta_pp": naive_delta,
         "true_delta_pp": true_delta})

    # --- 12 文字不越出各自面板，四边留足余量 ---
    # 面板描边按几何排除（见 border_zone），不靠颜色阈值：边框与底色会混出中间灰，
    # 亮度/颜色法都切不干净，会把边框当成正文墨迹、误判「文字压到边框」。
    # 查询窗取整个面板外框（含描边），再验证墨迹落在描边内侧并留 CLEAR 余量。
    CON_LY = [CON_Y_TOP + 54 + 28 * i for i in range(5)]
    CON_BOT = CON_Y_TOP + CON_H                 # 960
    PANELS = [
        (MARGIN, CON_Y_TOP, BOX_A_RIGHT, CON_BOT, 16, 2),    # 主结论框（青，2px）
        (BOX_B_X, CON_Y_TOP, BOX_B_RIGHT, CON_BOT, 16, 2),   # 限制框（红，2px）
        (C2_X, CH_Y, C2_X + CP_W, CH_Y + CH_H, 16, 1),       # 图②面板（灰，1px）
    ]
    # 构成注：18 号图标注，紧贴图②面板下缘（702 = BAR2_Y[1] + BAR2_H + 10）
    NOTE_Y = CH_Y + CH_H - 34
    HALO = 2.0                                  # 圆角弧的抗锯齿晕，两侧各 2px
    # 余量从面板**外缘**量起，必须同时覆盖描边、圆角晕与正文净空
    PAD_MIN = 2 + HALO + 4                     # 8px
    # (名称, 查询窗 [x0,y0,x1,y1), 所属面板 zone 的下标；None 表示图②面板)
    ITEMS = [
        ("主结论框", PANELS[0][:4], 0),
        ("限制框", PANELS[1][:4], 1),
        ("图②构成注", (CB_X - 8, NOTE_Y - 8, C2_X + CP_W, NOTE_Y + 34), 2),
    ]
    detail, over = {}, []
    for name, win, zi in ITEMS:
        z0 = PANELS[zi]
        zx0, zy0, zx1, zy1 = win
        b = ink_of(img, zx0, zy0, zx1, zy1, [z0], HALO)
        if b is None:
            over.append(f"{name}:未测到墨迹")
            detail[name] = {"ink_bbox": None}
            continue
        cl = {"左": b[0] - z0[0], "上": b[1] - z0[1],
              "右": z0[2] - b[2], "下": z0[3] - b[3]}
        detail[name] = {"ink_bbox": b, "clearance_px": cl,
                        "width": b[2] - b[0]}
        for k, v in cl.items():
            if v < PAD_MIN:
                over.append(f"{name}:{k}侧余量 {v}px（< {PAD_MIN}px）")
    chk("no_text_overflows_panels", not over,
        f"文字距面板外缘 ≥ {PAD_MIN}px（描边 + 圆角抗锯齿晕 + 正文净空），"
        "无文字越出任何面板",
        {"violations": over or "无", "detail": detail})

    # --- 13 结论两框的行与行之间有可测的密度低谷 ---
    # 像素检查器无法把一条墨迹归属到某一行（要归属就得有字体度量），所以不逐行量
    # 外接框，改量**每行的墨迹像素数**：若相邻两行的字形在竖直方向相触，中间就不会
    # 出现低谷。查询窗取 y 790–953 × 各框正文列，两侧边框（x 40–41 / 1028–1029、
    # 1050–1051 / 1558–1559）与上下边框都落在窗外，无需再做描边排除。
    P_TOP, P_BOT = 790, 954
    profs = {}
    for box_name, tx, zx1 in (("结论框A", MARGIN + PAD, BOX_A_RIGHT - 6),
                              ("限制框B", BOX_B_X + PAD, BOX_B_RIGHT - 6)):
        cnt = [int((img[y, tx - 8:zx1].astype(np.int16).max(axis=1) <= 0xC0).sum())
               for y in range(P_TOP, P_BOT)]
        peak = max(cnt) if cnt else 0
        gaps = []
        for i in range(len(CON_LY) - 1):
            b = CON_LY[i + 1]
            seg = [c for y, c in zip(range(P_TOP, P_BOT), cnt) if b - 4 <= y < b + 4]
            gaps.append({"boundary_y": b,
                         "min_count": min(seg) if seg else None,
                         "peak": int(peak)})
        profs[box_name] = {"window_y": [P_TOP, P_BOT], "window_x": [tx - 8, zx1],
                           "ink_count_per_row": cnt, "inter_line_gaps": gaps,
                           "all_gaps_below_half_peak": bool(cnt) and peak > 0 and all(
                               g["min_count"] is not None
                               and g["min_count"] * 2 <= peak for g in gaps)}
    gap_ok = all(p["all_gaps_below_half_peak"] for p in profs.values())
    chk("inter_line_ink_separation", gap_ok,
        "每对相邻结论行之间都存在墨迹密度低谷（< 峰值的一半）",
        {k: {"window_y": v["window_y"], "window_x": v["window_x"],
             "gaps": v["inter_line_gaps"],
             "ok": v["all_gaps_below_half_peak"]} for k, v in profs.items()},
        "峰值 = 该行字形最密的一行的墨迹像素数；低谷取行盒边界 ±4px 内的最小值")

    # --- 14 字号合规：DSL 中所有字号 ≥ 18，且结论区正文行都是 22 号 ---
    # 字号下限是题面要求，最直接的核对方式是读最终 .snapshot 的 fontSize 属性；
    # 琥珀色那行单独按墨迹宽度反推字号，因为它是唯一曾被写成 20 号的正文行
    # （20 号实测墨迹宽 719px，22 号应约 791px），光看 DSL 会漏掉构造器写错的场景。
    # 正式版与 PNG 同名同目录；预览版在 dsl/ 下按版本命名
    dsl_p = (src.with_suffix(".snapshot")
             if src.with_suffix(".snapshot").exists()
             else TMP / "dsl" / f"{IO.DSL_NAME}.{tag}.snapshot")
    dsz = ([int(x) for x in
            re.findall(r'fontSize="(\d+)"', dsl_p.read_text(encoding="utf-8"))]
           if dsl_p.exists() else [])
    AMBER_C = np.array((0xB4, 0x53, 0x09), np.int16)
    s5 = img[CON_LY[4] - 4:CON_LY[4] + 38, MARGIN + PAD - 8:BOX_A_RIGHT - 6]
    m5 = np.all(np.abs(s5.astype(np.int16) - AMBER_C) <= 24, axis=-1)
    yy, xx = np.where(m5)
    aw = int(xx.max() - xx.min() + 1) if len(xx) else 0
    ah = int(yy.max() - yy.min() + 1) if len(yy) else 0
    ok14 = bool(dsz) and min(dsz) >= 18 and 775 <= aw <= 805 and ah >= 22
    chk("font_sizes_meet_task_minimums", ok14,
        "所有 fontSize ≥ 18（图标注下限）；结论区最后一行与其余正文同为 22 号",
        {"dsl_path": str(dsl_p.relative_to(IO.ROOT)) if dsl_p.exists() else None,
         "dsl_font_sizes": sorted(set(dsz)), "min_font_size": min(dsz) if dsz else None,
         "amber_conclusion_line": {"width_px": aw, "ink_height_px": ah,
                                   "expect_width_at_22px": "775–805（20 号实测 719）"},
         "measured_ink_heights": {"title_38": hh(t_title), "body_22": hh(t_body),
                                  "tick_18": hh(t_tick), "value_18": hh(t_val)}},
        "字号取自最终 .snapshot 的 fontSize 属性；琥珀色分解行的墨迹宽度反向验证其字号")

    passed = sum(1 for c in R["checks"] if c["passed"])
    R["summary"] = {"total": len(R["checks"]), "passed": passed,
                    "failed": len(R["checks"]) - passed}
    dst = TMP / f"inspect-{tag}.json"
    dst.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"\n{passed}/{len(R['checks'])} 项通过 → {dst.relative_to(IO.ROOT)}")
    for c in R["checks"]:
        if not c["passed"]:
            print("  ✗", c["name"], c["actual"])
    return 0 if passed == len(R["checks"]) else 1


if __name__ == "__main__":
    png = sys.argv[1] if len(sys.argv) > 1 else \
        f"tmp/{RUN_ID}/A04/preview/v1.png"
    tg = sys.argv[2] if len(sys.argv) > 2 else "v1"
    sys.exit(main(png, tg))
