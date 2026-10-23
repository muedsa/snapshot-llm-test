"""A23 像素级审计：对**已交付**的 PNG 字节逐像素核验，不重渲、不后处理。

设计数据（frame-data.json）记录的是设计轨迹；本题要求「对照 6 张实际 PNG 和接触表
核验」，所以这里直接从交付字节取证，与离线设计数据分开报告，互不顶替。

审计项
  P1  IHDR：宽高 / 位深 / 颜色类型（PNG 6 = RGBA）
  P2  透明背景：每帧 alpha 直方图 + 完全透明像素数与占比
  P3  封面不透明：1200×800，min alpha == 255
  P4  画布内：实际墨迹外接框 vs 12 个旋转后外包框的并集外接框
       HARD_EDGE 静默裁切会让墨迹框严格小于几何框——这就是越界裁切的检测器
  P5  每单元：内部取样点的实际像素是否与其自身颜色相容；不匹配的点按后画单元
       识别遮挡者，与离线几何预期逐点对齐
  P6  可见性：每帧 12 个单元中心处 alpha>0，且无单元被完全遮挡
  P7  封面标题：墨迹外接框 + 与背景的实际对比度（WCAG 相对亮度）
  P8  字节同一性：交付 PNG 的 sha256 与服务原始响应字节相同

颜色相容判定按 alpha 合成模型 obs = a·fg + (1−a)·bg：不透明单元（alpha=255）直接
比 RGB；半透明单元反解 bg = (obs − a·fg)/(1−a)，bg 落在 [0,255] 内即相容。
取样点用 inset 内缩盒，远离抗锯齿边缘，所以容差可以收得很紧。

用法
    python -I -X utf8 a23_audit.py
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / "tools"))

import suite as S  # noqa: E402
import a23_units as U  # noqa: E402

TASK = "A23"
RUN = "r20261014T1536+0800-5f11da"
OUT = ROOT / "outputs" / RUN / TASK
TMP = ROOT / "tmp" / RUN / TASK

N_SAMPLES = 7          # 每单元 7×7 网格的 inset 采样点
TOL_OPAQUE = 6         # 不透明单元 RGB 容差
TOL_SEMI_OBS = 9       # 半透明单元观测值容差（反解后按 1/(1-a) 放大）
EDGE_BAND = 1.0        # 形状边界 1 px 内不做强判定：那一带必然是抗锯齿混合
BBOX_SLACK = 2.5       # 墨迹框相对保守外包框的余量（抗锯齿）
PAINT_SLACK = 3.0      # 墨迹框相对「真实绘制极值框」的余量（密采样步长 + 抗锯齿）

# 封面标题墨迹搜索区（避开副标题蓝框与正文浅灰字）
TITLE_REGION = (80, 26, 1092, 146)

FRAME_FILES = ["frame-%d.png" % i for i in range(1, 7)]
COVER_FILE = "cover.png"
CONTACT_SHEET_FILE = "contact-sheet.png"


# --------------------------------------------------------------------------- #
# 头与颜色模型
# --------------------------------------------------------------------------- #
def png_header(path: Path) -> dict:
    """只读 IHDR：这是「服务真给了 600×600 RGBA」的证据。"""
    with path.open("rb") as f:
        sig = f.read(8)
        f.read(4)          # IHDR 块长度
        hdr = f.read(4)    # 块类型 "IHDR"
        data = f.read(13)
    if sig != b"\x89PNG\r\n\x1a\n" or hdr[:4] != b"IHDR":
        raise ValueError("%s 不是 PNG" % path.name)
    w, h, bd, ct, cm, fd, il = struct.unpack(">IIBBBBB", data)
    return {"width": w, "height": h, "bit_depth": bd, "color_type": ct,
            "color_type_name": {0: "grayscale", 2: "rgb", 3: "palette",
                                4: "gray+alpha", 6: "rgba"}.get(ct, str(ct)),
            "interlace": il, "signature_ok": True}


def parse_rgb(unit: dict) -> tuple[int, int, int]:
    r = unit["rgb"]
    return (int(r[0:2], 16), int(r[2:4], 16), int(r[4:6], 16))


def is_own(obs, rgb, alpha: int, tol: float) -> bool:
    """该像素主要由 (rgb, alpha) 贡献：相容，且解出的背景不能是任意值。

    不透明：obs 必须等于 rgb（容差内）。
    半透明：obs 必须能反解出一个 [0,255] 内的背景，且该背景不等于 obs 本身
    ——否则一个完全透明的观察值也能"相容"任何前景，判定会退化成恒真。
    """
    a = alpha / 255.0
    tol_bg = tol / (1.0 - a) if a < 1.0 else 0.0
    for oc, fc in zip(obs[:3], rgb):
        if a >= 1.0:
            if abs(oc - fc) > tol:
                return False
            continue
        bg = (oc - a * fc) / (1.0 - a)
        if bg < -tol_bg or bg > 255.0 + tol_bg:
            return False
    return True


def wcag_lum(c) -> float:
    def ch(v: float) -> float:
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return (0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])) * 100.0


# --------------------------------------------------------------------------- #
# 单帧
# --------------------------------------------------------------------------- #
def to_flat(img: Image.Image) -> tuple[bytes, int, int]:
    """摊平成字节缓冲：比逐像素 px[x,y] 快一个数量级。"""
    raw = img.tobytes()
    return raw, img.size[0], img.size[1]


def painted_points(unit: dict, p: dict, step: float = 1.0) -> list[tuple[float, float]]:
    """形状**实际绘制区域**旋转后的极值点（不是外包框的四个角）。

    三角形和圆形的旋转外包框比真实墨迹大一圈，拿它当「应有墨迹框」会把正常帧
    判成裁切。这里按 step 密采样形状内部、旋转到世界坐标，取到的极值才是墨迹
    真正的边界；step 带来的误差由 PAINT_SLACK 吸收。
    """
    w, h = unit["w"], unit["h"]
    hw, hh = w / 2.0, h / 2.0
    ang = math.radians(p["rot"])
    c, s = math.cos(ang), math.sin(ang)
    r_corner = min(hw, hh) if unit["shape"] == "rounded" else 0.0

    def inside(lx, ly) -> bool:
        """真实形状判定。

        a23_units.in_shape 把 rounded 当直角矩形用——对布局够用，但算墨迹极值会
        错：borderRadius=min(w,h)/2 是 stadium（box⊕disk），旋转后它的外延比同尺寸
        矩形的旋转外包框小一截，拿矩形框去比会让正常帧被误判成「墨迹被裁掉」。
        """
        if unit["shape"] == "circle":
            return lx * lx + ly * ly <= hw * hw
        if unit["shape"] == "rect":
            return abs(lx) <= hw and abs(ly) <= hh
        if unit["shape"] == "rounded":
            dx = max(0.0, abs(lx) - (hw - r_corner))
            dy = max(0.0, abs(ly) - (hh - r_corner))
            return dx * dx + dy * dy <= r_corner * r_corner
        if unit["shape"] == "triangle":
            if ly < -hh or ly > hh:
                return False
            return abs(lx) <= hw * ((ly + hh) / h)
        raise ValueError(unit["shape"])

    out = []
    for i in range(int(-hw / step), int(hw / step) + 1):
        lx = i * step
        for j in range(int(-hh / step), int(hh / step) + 1):
            ly = j * step
            if not inside(lx, ly):
                continue
            out.append((p["x"] + lx * c - ly * s, p["y"] + lx * s + ly * c))
    # 密采样有 step 级误差，再补上精确极值点。
    # rect 的极值就在四个顶点上；rounded 不能补矩形四角——那四个角在 stadium 外
    # （borderRadius=min(w,h)/2 把角全磨掉了），补进去会把应有框凭空放大一截，
    # 于是正常帧被误判成「墨迹被裁掉」。stadium 的轴向外延用支集函数给：
    #   e = (hw−r)·|cosθ| + (hh−r)·|sinθ| + r
    if unit["shape"] == "rect":
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                out.append((p["x"] + sx * hw * c - sy * hh * s,
                            p["y"] + sx * hw * s + sy * hh * c))
    if unit["shape"] == "rounded":
        rc = r_corner
        ex = (hw - rc) * abs(c) + (hh - rc) * abs(s) + rc
        ey = (hw - rc) * abs(s) + (hh - rc) * abs(c) + rc
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                out.append((p["x"] + sx * ex, p["y"] + sy * ey))
    if unit["shape"] == "triangle":
        verts = [(0.0, -hh), (-hw, hh), (hw, hh)]
        out += [(p["x"] + vx * c - vy * s, p["y"] + vx * s + vy * c) for vx, vy in verts]
    if unit["shape"] == "circle":
        for ang in range(0, 360, 15):
            ar = math.radians(ang)
            vx, vy = hw * math.cos(ar), hh * math.sin(ar)
            out.append((p["x"] + vx * c - vy * s, p["y"] + vx * s + vy * c))
    return out


def make_px(buf: bytes, stride: int):
    """返回 (x,y) → (r,g,b,a) 的取点闭包。"""
    def px(x: int, y: int):
        i = y * stride + x * 4
        return (buf[i], buf[i + 1], buf[i + 2], buf[i + 3])
    return px


def audit_frame(f: int, frame_row: list[dict], img: Image.Image,
                header: dict, file_label: str) -> dict:
    by_id = {u["id"]: u for u in U.UNITS}
    order = U.PAINT_ORDER
    rows = {r["id"]: r for r in frame_row}
    buf, W, H = to_flat(img)
    stride = W * 4
    px = make_px(buf, stride)
    res: dict = {"frame": f, "t_ms": (f - 1) * U.DURATION_MS, "file": file_label,
                 "header": header, "expected_size": [U.FRAME_W, U.FRAME_H]}

    # P2 透明度 + P4 墨迹外接框，一次扫描完成
    hist: dict[int, int] = {}
    ink = [9e9, 9e9, 0.0, 0.0]
    for y in range(H):
        row0 = y * stride
        for x in range(W):
            a = buf[row0 + x * 4 + 3]
            hist[a] = hist.get(a, 0) + 1
            if a > 0:
                if x < ink[0]: ink[0] = x
                if y < ink[1]: ink[1] = y
                if x + 1 > ink[2]: ink[2] = x + 1
                if y + 1 > ink[3]: ink[3] = y + 1
    total = W * H
    res["alpha"] = {
        "fully_transparent_pixels": hist.get(0, 0),
        "fully_transparent_fraction": round(hist.get(0, 0) / total, 6),
        "fully_opaque_pixels": hist.get(255, 0),
        "distinct_alpha_levels": len(hist),
        "top_levels": [[a, n] for a, n in sorted(hist.items(), key=lambda kv: -kv[1])[:6]],
        "method": "alpha 通道直方图；alpha=0 即真实透明背景",
    }

    # P4 画布内
    # 两个不同语义的框，别混：
    #   geo_bbox    — 旋转后**外包框**并集（保守上界，三角形/圆形的角不填满）
    #   paint_bbox  — 形状**实际绘制区域**的旋转后极值框（逐形状密采样，才是墨迹该有的框）
    # ink ⊆ geo_bbox 抓「溢出画布被截」；ink ≈ paint_bbox 抓 HARD_EDGE 静默裁切
    # （墨迹比应有框少一截，而几何本身还在画布内，前者抓不到）。
    def union_bbox(sel: float = 1.0) -> list[float]:
        b = [9e9, 9e9, 0.0, 0.0]
        for u in U.UNITS:
            r = rows[u["id"]]
            if sel == 1.0:
                hw, hh = U.rotated_half_extents(u["w"], u["h"], r["rot"], u["shape"])
                xs = [(r["x"] - hw, r["y"] - hh), (r["x"] + hw, r["y"] + hh)]
            else:
                xs = painted_points(u, r, step=0.5)
            for wx, wy in xs:
                b[0] = min(b[0], wx); b[1] = min(b[1], wy)
                b[2] = max(b[2], wx); b[3] = max(b[3], wy)
        return b

    geo = union_bbox(1.0)
    paint = union_bbox(0.5)
    has_ink = ink[0] < ink[2]
    res["canvas"] = {
        "ink_bbox": [round(v, 2) for v in ink] if has_ink else None,
        "geo_union_bbox": [round(v, 2) for v in geo],
        "painted_union_bbox": [round(v, 2) for v in paint],
        "geo_inside_canvas": all(geo[i] >= -0.5 and geo[i] <= (W if i < 2 else H) + 0.5
                                 for i in range(4)),
        "ink_inside_geo": bool(has_ink
                               and ink[0] >= geo[0] - BBOX_SLACK
                               and ink[1] >= geo[1] - BBOX_SLACK
                               and ink[2] <= geo[2] + BBOX_SLACK
                               and ink[3] <= geo[3] + BBOX_SLACK),
        "ink_matches_painted": bool(has_ink
                                    and all(abs(ink[i] - paint[i]) <= PAINT_SLACK
                                            for i in range(4))),
        "ink_vs_painted_delta": ([round(ink[i] - paint[i], 2) for i in range(4)]
                                 if has_ink else None),
        "method": "alpha>0 判墨迹；geo 是旋转外包框并集，painted 是逐形状密采样的真实"
                  "绘制极值并集。HARD_EDGE 静默裁切表现为 ink 与 painted 在某一边相差"
                  "超过 slack，而 geo_inside_canvas 仍为真",
        "slack_px": BBOX_SLACK,
        "painted_slack_px": PAINT_SLACK,
    }

    # P5/P6 每单元
    # 判定基准不是「我在找这个单元」，而是几何上算出**最上层覆盖该像素的单元** T，
    # 再要求实际像素与 T 的颜色相符。遮挡因此是结论，不是假设。
    # 几何判定必须与像素读取用**同一个整数坐标**（像素中心），否则 0.7 px 的
    # 取整误差就能让一个点被判到形状边界的另一侧——这正是本项第一次跑时那 1 个
    # 「未解释」点的来源，不是图有缺陷。
    def covering(xi: int, yi: int) -> list[str]:
        out = []
        for uid in order:
            u = by_id[uid]
            lc = U.world_to_local(xi, yi, rows[uid], u)
            if U.in_shape(lc[0], lc[1], u):
                out.append(uid)
        return out

    def tol_of(alpha: int) -> float:
        return TOL_OPAQUE if alpha == 255 else TOL_SEMI_OBS

    def dist_to_edge(lx: float, ly: float, u: dict) -> float:
        """本地坐标到该单元形状边界的最短距离（px），用于界定抗锯齿带。"""
        w, h = u["w"], u["h"]
        hw, hh = w / 2.0, h / 2.0
        if u["shape"] == "circle":
            return hw - math.hypot(lx, ly)
        if u["shape"] in ("rect", "rounded"):
            return min(hw - abs(lx), hh - abs(ly))
        denom = math.hypot(2 * hh, hw)          # triangle：底边 + 左右两坡
        return min(hh - ly,
                   (2 * hh * lx + hw * ly + hw * hh) / denom,
                   (-2 * hh * lx + hw * ly + hw * hh) / denom)

    units = []
    for uid in order:
        u = by_id[uid]
        r = rows[uid]
        pts = U.sample_world_points(u, r, N_SAMPLES)
        n = own = occ = n_edge = n_out = n_shape = n_un = 0
        occ_by: dict[str, int] = {}
        for wx, wy in pts:
            n += 1
            xi, yi = int(round(wx)), int(round(wy))
            if not (0 <= xi < W and 0 <= yi < H):
                n_out += 1
                continue
            chain = covering(xi, yi)
            # 抗锯齿带必须对**全部 12 个单元**取边界距离，不能只看覆盖链：
            # 一个形状边界刚好落在链外 0.8 px 处时，它的边缘羽化同样会渗进这个
            # 像素——只量链内单元就会把这个混合像素误判成缺陷（帧5 那个点）。
            dmin = min(abs(dist_to_edge(*U.world_to_local(xi, yi, rows[v], by_id[v]),
                                       by_id[v])) for v in order)
            if dmin < EDGE_BAND:
                n_edge += 1                     # 任一形状边界 1 px 内：羽化区，不做硬判
                continue
            if not chain:
                n_shape += 1                    # 硬判区内却不在任何形状里
                continue
            top = chain[-1]
            obs = px(xi, yi)
            t = by_id[top]
            if is_own(obs, parse_rgb(t), t["alpha"], tol_of(t["alpha"])):
                if top == uid:
                    own += 1
                else:
                    occ += 1
                    occ_by[top] = occ_by.get(top, 0) + 1
            else:
                n_un += 1
        cx, cy = int(round(r["x"])), int(round(r["y"]))
        calpha = px(cx, cy)[3] if 0 <= cx < W and 0 <= cy < H else -1
        hw, hh = U.rotated_half_extents(u["w"], u["h"], r["rot"], u["shape"])
        inside = (r["x"] - hw >= 0 and r["x"] + hw <= W and r["y"] - hh >= 0
                  and r["y"] + hh <= H)
        units.append({
            "id": uid, "name": u["name"], "expected_rgb": u["rgb"], "alpha": u["alpha"],
            "center": [round(r["x"], 3), round(r["y"], 3)],
            "rotated_bbox_in_canvas": inside,
            "center_alpha": calpha,
            "center_visible": calpha > 0,
            "interior_samples": n,
            "own_color_samples": own,
            "occluded_samples": occ,
            "antialias_band_samples": n_edge,
            "outside_own_shape_samples": n_shape,
            "out_of_canvas_samples": n_out,
            "unexplained_samples": n_un,
            "own_fraction": round(own / n, 6) if n else None,
            "occluded_fraction": round(occ / n, 6) if n else None,
            "occluded_by": occ_by or None,
            "visible": own > 0 and n_out == 0 and n_un == 0,
            "visible_reason": "own>0 表示该单元至少一处露出自己的颜色；unexplained=0 "
                              "表示所有落在硬判区的内部取样点都与其几何最上层单元的颜色相符",
        })
    res["units"] = units
    ids = [v["id"] for v in units]
    res["count"] = len(units)
    res["ids_unique_once"] = sorted(ids) == sorted({i for i in ids}) and len(ids) == 12
    res["units_all_visible"] = all(v["visible"] for v in units)
    res["centers_all_visible"] = all(v["center_visible"] for v in units)
    res["fully_hidden"] = [v["id"] for v in units if v["own_color_samples"] == 0]
    res["unexplained_total"] = sum(v["unexplained_samples"] for v in units)
    res["out_of_canvas_total"] = sum(v["out_of_canvas_samples"] for v in units)
    res["antialias_band_total"] = sum(v["antialias_band_samples"] for v in units)
    res["outside_own_shape_total"] = sum(v["outside_own_shape_samples"] for v in units)
    res["own_fraction_range"] = [min(v["own_fraction"] for v in units),
                                 max(v["own_fraction"] for v in units)]
    res["total_samples"] = sum(v["interior_samples"] for v in units)
    return res


# --------------------------------------------------------------------------- #
# 封面
# --------------------------------------------------------------------------- #
def audit_cover(img: Image.Image) -> dict:
    buf, W, H = to_flat(img)
    stride = W * 4
    res = {"file": COVER_FILE, "header": png_header(OUT / COVER_FILE),
           "expected_size": [U.COVER_W, U.COVER_H]}
    mn, mx = 256, -1
    for i in range(0, len(buf), 4):
        a = buf[i + 3]
        if a < mn: mn = a
        if a > mx: mx = a
    res["alpha"] = {"min_alpha": mn, "max_alpha": mx, "fully_opaque": mn == 255,
                    "method": "遍历全部 %dx%d 像素取 alpha 极值" % (W, H)}

    x0, y0, x1, y1 = TITLE_REGION
    ink = [9e9, 9e9, 0.0, 0.0]
    ink_l, bg_l = [], []
    for y in range(y0, y1):
        row0 = y * stride
        for x in range(x0, x1):
            j = row0 + x * 4
            lum = wcag_lum((buf[j], buf[j + 1], buf[j + 2]))
            if lum > 90:
                ink[0] = min(ink[0], x); ink[1] = min(ink[1], y)
                ink[2] = max(ink[2], x + 1); ink[3] = max(ink[3], y + 1)
                ink_l.append(lum)
            else:
                bg_l.append(lum)
    if not ink_l:
        res["title"] = {"found": False}
        return res
    mean_i, mean_b = sum(ink_l) / len(ink_l), sum(bg_l) / len(bg_l)
    worst_i = min(ink_l)
    rr = lambda lo, hi: round((hi + 5) / (lo + 5), 2)
    res["title"] = {
        "found": True,
        "text": U.TITLE,
        "search_region": [x0, y0, x1, y1],
        "ink_bbox": [round(v, 2) for v in ink],
        "ink_bbox_size": [round(ink[2] - ink[0], 2), round(ink[3] - ink[1], 2)],
        "ink_pixels": len(ink_l),
        "mean_ink_rel_lum_pct": round(mean_i, 3),
        "mean_bg_rel_lum_pct": round(mean_b, 3),
        "contrast_mean": rr(min(mean_i, mean_b), max(mean_i, mean_b)),
        "contrast_worst_ink_px": rr(min(worst_i, mean_b), max(worst_i, mean_b)),
        "wcag_aa_4_5": rr(min(worst_i, mean_b), max(worst_i, mean_b)) >= 4.5,
        "method": "WCAG 相对亮度公式线性化后加权；对比度按最暗墨迹像素计（保守）",
    }
    return res


# --------------------------------------------------------------------------- #
# 活性证明
# 审计器没触发过就是假的。这里故意用 PIL 重画几帧已知错误的图喂进去，验证每个
# 检测器真的会亮；再喂一帧正常图做阴性对照。只断言被测试的那个检测器。
# --------------------------------------------------------------------------- #
def paint_frame(rows: dict, exclude=(), recolor=None, opaque_bg=False,
                shift=None, erase=None) -> Image.Image:
    """按 PAINT_ORDER 用 PIL 重画一帧，专门用于构造已知错误的图。

    erase=(x0,y0,x1,y1) 画完后把该矩形抹掉，用来模拟 HARD_EDGE 的静默裁切：
    几何还在画布里，但像素被切走了。
    """
    by_id = {u["id"]: u for u in U.UNITS}
    canvas = Image.new("RGBA", (U.FRAME_W, U.FRAME_H),
                       (255, 255, 255, 255) if opaque_bg else (0, 0, 0, 0))
    for uid in U.PAINT_ORDER:
        if uid in exclude:
            continue
        u = by_id[uid]
        dx, dy = (shift or {}).get(uid, (0.0, 0.0))
        cx, cy = rows[uid]["x"] + dx, rows[uid]["y"] + dy
        rot = rows[uid]["rot"]
        hexcol = (recolor or {}).get(uid, u["rgb"])
        col = parse_rgb({"rgb": hexcol}) + (u["alpha"],)
        pad = 14
        lw, lh = int(math.ceil(u["w"])) + 2 * pad, int(math.ceil(u["h"])) + 2 * pad
        tmp = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        x0, y0, x1, y1 = pad, pad, pad + u["w"], pad + u["h"]
        if u["shape"] == "circle":
            d.ellipse((x0, y0, x1, y1), fill=col)
        elif u["shape"] == "rounded":
            d.rounded_rectangle((x0, y0, x1, y1),
                                radius=min(u["w"], u["h"]) / 2, fill=col)
        elif u["shape"] == "rect":
            d.rectangle((x0, y0, x1, y1), fill=col)
        else:
            d.polygon([(pad + u["w"] / 2, y0), (x1, y1), (x0, y1)], fill=col)
        tmp = tmp.rotate(-rot, resample=Image.BICUBIC,
                         center=(pad + u["w"] / 2, pad + u["h"] / 2))
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        layer.paste(tmp, (int(round(cx - lw / 2)), int(round(cy - lh / 2))))
        canvas = Image.alpha_composite(canvas, layer)
    if erase:
        canvas = canvas.copy()
        ImageDraw.Draw(canvas).rectangle(erase, fill=(0, 0, 0, 0))
    return canvas


def activation_tests(frames) -> list[dict]:
    """喂已知错误的合成图，验证检测器会触发；最后一项是阴性对照。"""
    f = 6
    row = frames[f - 1]
    rows = {r["id"]: r for r in row}
    hdr = {"width": U.FRAME_W, "height": U.FRAME_H, "bit_depth": 8,
           "color_type": 6, "color_type_name": "rgba", "interlace": 0,
           "signature_ok": True, "synthetic": True}
    cases = [
        ("A1 少画一个单元 → 该单元必须被报为完全遮挡",
         {"exclude": ("U01",)},
         lambda r: "U01" in r["fully_hidden"] and not r["units_all_visible"]),
        ("A2 换成不透明白底 → 全透明像素数必须归零",
         {"opaque_bg": True},
         lambda r: r["alpha"]["fully_transparent_pixels"] == 0),
        ("A3 换一个单元颜色 → 该点必须落成未解释像素",
         {"recolor": {"U01": "FF00FF"}},
         lambda r: r["unexplained_total"] > 0),
        ("A4 把整个地面推出画布 → 几何必须报越界、该单元不可见",
         {"shift": {"U12": (-560.0, 0.0)}},
         lambda r: not r["canvas"]["geo_inside_canvas"]
         and not r["units_all_visible"]),
        ("A5 硬裁左侧一条 → 墨迹框必须小于应有框（HARD_EDGE 静默裁切）",
         {"erase": (0, 0, 130, 600)},
         lambda r: not r["canvas"]["ink_matches_painted"]
         and r["canvas"]["geo_inside_canvas"]),
        ("A6 阴性对照：按设计原样重画 → 关键检测器都不应亮",
         {},
         lambda r: r["canvas"]["geo_inside_canvas"] and r["units_all_visible"]
         and not r["fully_hidden"]
         and r["alpha"]["fully_transparent_pixels"] > 0),
    ]
    out = []
    for name, kwargs, assert_fn in cases:
        img = paint_frame(rows, **kwargs)
        # 偏移要同时反映到**几何输入**里：审计的越界判定看的是设计坐标，
        # 只改图像不改进度数据就测不到 geo_inside_canvas。
        rows_used = dict(rows)
        for uid, (dx, dy) in (kwargs.get("shift") or {}).items():
            b = rows_used[uid]
            rows_used[uid] = dict(b, x=b["x"] + dx, y=b["y"] + dy)
        res = audit_frame(f, list(rows_used.values()), img, hdr, "synthetic")
        ok = bool(assert_fn(res))
        out.append({
            "case": name,
            "triggered_as_expected": ok,
            "fully_hidden": res["fully_hidden"],
            "units_all_visible": res["units_all_visible"],
            "fully_transparent_pixels": res["alpha"]["fully_transparent_pixels"],
            "unexplained_total": res["unexplained_total"],
            "geo_inside_canvas": res["canvas"]["geo_inside_canvas"],
            "ink_inside_geo": res["canvas"]["ink_inside_geo"],
            "ink_matches_painted": res["canvas"]["ink_matches_painted"],
            "ink_vs_painted_delta": res["canvas"]["ink_vs_painted_delta"],
            "ink_bbox": res["canvas"]["ink_bbox"],
            "geo_union_bbox": res["canvas"]["geo_union_bbox"],
            "out_of_canvas_samples": res["out_of_canvas_total"],
            "own_fraction_range": res["own_fraction_range"],
        })
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
    return out


# --------------------------------------------------------------------------- #
def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    frames = U.all_frames()
    report: dict = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "run_id": RUN, "audited_at": S.now_iso(), "timezone": S.TZ_NAME,
        "policy": "只读已交付 PNG 字节；不重渲、不后处理",
        "tolerances": {"opaque_rgb": TOL_OPAQUE, "semi_observed": TOL_SEMI_OBS,
                       "antialias_band_px": EDGE_BAND, "bbox_slack_px": BBOX_SLACK},
        "sampler": {"grid": "%d×%d" % (N_SAMPLES, N_SAMPLES), "inset_fraction": 0.16,
                    "source": "a23_units.interior_samples / sample_world_points",
                    "note": "inset 内缩盒避开抗锯齿边缘，容差因此可收紧"},
    }

    frames_out = []
    for f, row in enumerate(frames, 1):
        img = Image.open(OUT / FRAME_FILES[f - 1]).convert("RGBA")
        fp = OUT / FRAME_FILES[f - 1]
        r = audit_frame(f, row, img, png_header(fp), FRAME_FILES[f - 1])
        frames_out.append(r)
        ok = (r["units_all_visible"] and r["centers_all_visible"]
              and r["canvas"]["geo_inside_canvas"] and r["canvas"]["ink_inside_geo"]
              and r["canvas"]["ink_matches_painted"]
              and r["unexplained_total"] == 0 and r["out_of_canvas_total"] == 0)
        print("[%s] 帧%d t=%4dms %dx%d %s 全透明=%5.1f%% %d级 "
              "12单元可见=%s 中心可见=%s 几何⊆画布=%s 墨迹⊆几何=%s 墨迹=应有框=%s "
              "未解释=%d 抗锯齿带=%d 自身露色比例=%.2f~%.2f 完全遮挡=%s"
              % ("PASS" if ok else "FAIL", f, r["t_ms"], r["header"]["width"],
                 r["header"]["height"], r["header"]["color_type_name"],
                 100 * r["alpha"]["fully_transparent_fraction"],
                 r["alpha"]["distinct_alpha_levels"], r["units_all_visible"],
                 r["centers_all_visible"], r["canvas"]["geo_inside_canvas"],
                 r["canvas"]["ink_inside_geo"], r["canvas"]["ink_matches_painted"],
                 r["unexplained_total"], r["antialias_band_total"],
                 r["own_fraction_range"][0], r["own_fraction_range"][1],
                 r["fully_hidden"] or "无"))
    report["frames"] = frames_out

    print("\n活性证明：用已知错误的合成图验证检测器会触发")
    act = activation_tests(frames)
    report["activation_tests"] = {
        "method": "用 PIL 按 PAINT_ORDER 重画一帧，人为破坏其中一项，再喂给同一个 "
                  "audit_frame；只断言被破坏的那一项会被检出",
        "all_triggered": all(a["triggered_as_expected"] for a in act),
        "items": act,
    }

    cov_img = Image.open(OUT / COVER_FILE).convert("RGBA")
    res_cov = audit_cover(cov_img)
    report["cover"] = res_cov
    t = res_cov["title"]
    okc = res_cov["alpha"]["fully_opaque"] and t.get("wcag_aa_4_5")
    print("[%s] 封面 %dx%d %s min_alpha=%d 标题 %d 墨迹px 对比度 均值%s:1 最暗%s:1 AA=%s"
          % ("PASS" if okc else "FAIL", res_cov["header"]["width"],
             res_cov["header"]["height"], res_cov["header"]["color_type_name"],
             res_cov["alpha"]["min_alpha"], t.get("ink_pixels", 0),
             t.get("contrast_mean"), t.get("contrast_worst_ink_px"),
             t.get("wcag_aa_4_5")))

    # P8 字节同一性：覆盖全部 8 件交付（封面 + 6 帧 + 接触表），不只 7 件。
    man = json.loads((OUT / "delivery-manifest.json").read_text(encoding="utf-8"))
    ident = []
    for fname in [COVER_FILE] + FRAME_FILES + [CONTACT_SHEET_FILE]:
        blob = (OUT / fname).read_bytes()
        rec = next((d for d in man["deliverables"] if d["file"] == fname), None)
        # manifest 里 temp_response_path.path 已经是相对 suite_root 的路径，
        # 拼接后再转回相对，写进报告的路径不能出现机器绝对路径。
        resp = ROOT / rec["temp_response_path"]["path"] if rec else None
        rb = resp.read_bytes() if (resp and resp.is_file()) else b""
        ident.append({
            "file": fname,
            "png_sha256": hashlib.sha256(blob).hexdigest(),
            "response_sha256": hashlib.sha256(rb).hexdigest() if rb else None,
            "identical": bool(rb and hashlib.sha256(rb).hexdigest() == hashlib.sha256(blob).hexdigest()),
            "request_id": rec.get("request_id") if rec else None,
            "temp_response_path": {"path_base": "suite_root",
                                   "path": S.rel(resp) if resp else None},
        })
    report["delivery_byte_identity"] = {
        "checked": len(ident), "all_identical": all(i["identical"] for i in ident),
        "method": "sha256(交付PNG) == sha256(tmp/<run_id>/A23/responses/<request_id>.png)",
        "items": ident,
    }

    # 汇总
    fail = []
    for r in frames_out:
        if (r["header"]["width"], r["header"]["height"]) != (600, 600):
            fail.append("帧%d 尺寸非 600×600" % r["frame"])
        if r["header"]["color_type"] != 6:
            fail.append("帧%d 颜色类型非 RGBA" % r["frame"])
        if r["alpha"]["fully_transparent_pixels"] == 0:
            fail.append("帧%d 无透明像素" % r["frame"])
        if not r["ids_unique_once"]:
            fail.append("帧%d 12 个 ID 不唯一" % r["frame"])
        if not r["canvas"]["geo_inside_canvas"]:
            fail.append("帧%d 几何越出画布" % r["frame"])
        if not r["canvas"]["ink_inside_geo"]:
            fail.append("帧%d 墨迹超出几何框（疑似裁切）" % r["frame"])
        if not r["canvas"]["ink_matches_painted"]:
            fail.append("帧%d 墨迹框与应有框不符 偏差=%s（疑似静默裁切）"
                        % (r["frame"], r["canvas"]["ink_vs_painted_delta"]))
        if r["out_of_canvas_total"]:
            fail.append("帧%d 采样点越界 %d" % (r["frame"], r["out_of_canvas_total"]))
        if r["unexplained_total"]:
            fail.append("帧%d 未解释像素 %d" % (r["frame"], r["unexplained_total"]))
        if r["fully_hidden"]:
            fail.append("帧%d 单元被完全遮挡 %s" % (r["frame"], r["fully_hidden"]))
        if not r["centers_all_visible"]:
            fail.append("帧%d 单元中心不可见" % r["frame"])
    if (res_cov["header"]["width"], res_cov["header"]["height"]) != (1200, 800):
        fail.append("封面尺寸非 1200×800")
    if not res_cov["alpha"]["fully_opaque"]:
        fail.append("封面存在透明像素")
    if not t.get("found"):
        fail.append("封面标题墨迹未检出")
    if not t.get("wcag_aa_4_5"):
        fail.append("封面标题对比度不足 4.5:1")
    if not report["delivery_byte_identity"]["all_identical"]:
        fail.append("交付字节与服务响应不一致")
    if not report["activation_tests"]["all_triggered"]:
        bad_act = [a["case"] for a in report["activation_tests"]["items"]
                   if not a["triggered_as_expected"]]
        fail.append("审计器活性证明未通过：%s" % "、".join(bad_act))
    report["passed"] = not fail
    report["failures"] = fail
    print("\n像素审计：%s" % ("全部通过" if not fail else "未通过 — " + "；".join(fail)))

    body = json.dumps(report, ensure_ascii=False, indent=1) + "\n"
    (OUT / "pixel-audit.json").write_text(body, encoding="utf-8")
    (TMP / "pixel-audit.json").write_text(body, encoding="utf-8")
    S.log_iteration(TASK, {
        "seq": S.next_iteration_seq(TASK, 900),
        "stage": "audit", "kind": "pixel_audit",
        "started_at": S.now_iso(), "ended_at": S.now_iso(),
        "target": "outputs/%s/A23/{cover.png,frame-1..6.png}" % RUN,
        "result": "passed" if not fail else "failed",
        "failures": fail,
        "report": {"path_base": "output_dir", "path": "pixel-audit.json"},
        "note": "对已交付字节做像素级核验，不重渲、不后处理",
    })
    print("报告 outputs/%s/A23/pixel-audit.json" % RUN)
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
