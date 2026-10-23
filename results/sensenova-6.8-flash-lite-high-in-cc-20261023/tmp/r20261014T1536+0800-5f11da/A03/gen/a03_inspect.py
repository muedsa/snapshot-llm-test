"""A03 像素级自检：对渲染结果做可复算的几何与视觉核验。

不依赖肉眼判断，给出数值证据（写入 tmp/<rid>/A03/<name>-inspect.json）：

  size             画布尺寸是否 1280×800
  corner_pixels    四角像素是否等于背景 #0B1220
  content_bbox     全图非背景内容外接框 → 与安全边距 32 的余量
  title            标题外接框 → 44 号字高核验、右边界（与 LIVE 是否重叠）
  live             LIVE 标签外接框 → 96×36 核验、在安全区内
  metric_cards     三张指标卡外接框与宽度差（等宽核验）
  stripes          卡外细条锐度 vs 卡内模糊背景锐度 → 证明「只模糊卡内」
  text_band        说明卡文字带锐度 → 证明文字保持清晰
  review           REVIEW 外接框、旋转方向、四角到画布/安全区的余量
  review_fill      REVIEW 卡体取色的众数 → 验证白底 20% 不透明度

bbox 统一为 [left, top, right, bottom] 闭区间。
用法：python a03_inspect.py <png路径> <报告前缀> <输出目录>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

BG = np.array([0x0B, 0x12, 0x20], dtype=np.int16)
# LUM 必须是 float：dtype=int16 会把 0.299/0.587/0.114 截断成全 0，
# 使所有梯度恒为 0，把「卡外细条锐利、卡内模糊」误判成无差别。
LUM = np.array([0.299, 0.587, 0.114], dtype=np.float64)
TH = 12                       # 与背景判定为「内容」的最小通道差


def grad_mag(a: np.ndarray) -> float:
    """区域内灰度梯度模长均值：越大 = 边缘越锐利 / 细节越多。"""
    g = a.astype(np.float64) @ LUM.astype(np.float64)
    dy = np.abs(np.diff(g, axis=0))
    dx = np.abs(np.diff(g, axis=1))
    return float(np.concatenate([dy.ravel(), dx.ravel()]).mean())


def max_row_grad(a: np.ndarray) -> float:
    """区域内最强的水平边（相邻行灰度跳变最大值）—— 锐利横条会在这里留痕。"""
    g = a.astype(np.float64) @ LUM.astype(np.float64)
    return float(np.abs(np.diff(g, axis=0)).max())


def shift(bbox: list[int], x0: int, y0: int) -> list[int]:
    return [bbox[0] + x0, bbox[1] + y0, bbox[2] + x0, bbox[3] + y0]


def plain(o):
    """把 numpy 标量/数组递归转成 JSON 可序列化的纯 Python 类型。"""
    if isinstance(o, dict):
        return {k: plain(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [plain(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return [plain(v) for v in o.tolist()]
    return o


def card_geometry(img: np.ndarray, exp_x0: int, exp_x1: int,
                  exp_y0: int, exp_y1: int) -> dict:
    """说明卡的真实尺寸：分别用「上下边框行」和「左右边框列」定外接框。

    必须避开的三个坑：
      1) 细条里恰好有一条是 #38BDF8，与卡边框同色，且在卡外仍然锐利。
         所以用「卡外横向无亮蓝」限定行，才能从该行读左右边框列。
      2) 卡内被模糊后的蓝条混合色只有 (71,74,99)，不是亮蓝；卡外背景
         (11,18,32) 的 B-R 也只有 21。判据 B>R+40 且 B>140 只命中真正的边框。
      3) 卡有 borderRadius=24，最上/最下一行的边框被圆角截短（只到 413..866），
         宽度必须从未被圆角影响的中间行读。
    """
    rgb = img.astype(np.int16)
    blue = (rgb[:, :, 2] > rgb[:, :, 0] + 40) & (rgb[:, :, 2] > 140)
    ylo, xlo = exp_y0 - 2, exp_x0 - 40
    win = blue[ylo:exp_y1 + 3, xlo:exp_x1 + 41]

    inner = slice(exp_x0 + 5 - xlo, exp_x1 - 5 - xlo)     # 卡内横向范围
    rows = [a + ylo for a in range(win.shape[0])
            if win[a, inner].sum() > 300]                 # 上下边框行

    outer = np.zeros(win.shape[1], dtype=bool)
    outer[:exp_x0 - xlo] = True                           # x < 卡左边框
    outer[exp_x1 - xlo:] = True                           # x >= 卡右边框外侧
    xs_sel = np.zeros(win.shape[1], dtype=bool)
    gap_rows = []
    for a in range(win.shape[0]):
        if win[a, outer].sum() == 0:
            xs_sel |= win[a]
            gap_rows.append(a + ylo)

    if not rows or not xs_sel.any():
        return {"found": False, "reason": "未找到足够的边框行/列"}
    xcol = np.where(xs_sel)[0]
    x0, x1 = int(xcol.min()) + xlo, int(xcol.max()) + xlo
    y0, y1 = rows[0], rows[-1]
    w, h = x1 - x0 + 1, y1 - y0 + 1
    return {
        "found": True,
        "method": ("亮蓝掩膜 B>R+40 且 B>140；上下边框行=卡内横向大量亮蓝的行，"
                   "左右边框列=卡外横向无亮蓝的行上的亮蓝像素"),
        "top_bottom_border_rows": rows,
        "left_right_border_rows_used": [r for r in gap_rows
                                        if y0 - 3 <= r <= y1 + 3],
        "bbox": [x0, y0, x1, y1],
        "size": [w, h],
        "expected_bbox": [exp_x0, exp_y0, exp_x1 - 1, exp_y1 - 1],
        "expected_size": [exp_x1 - exp_x0, exp_y1 - exp_y0],
        "size_matches_500x150": (w == 500 and h == 150),
    }


def stripe_extent(img: np.ndarray, y0: int, y1: int,
                  card_x0: int, card_x1: int) -> dict:
    """彩色细条的实际横向跨度，及是否越过说明卡的左右边界。

    只统计颜色接近 5 条细条色（误差 ±12）的像素：模糊区内的混合色不在此列，
    所以测到的是「卡外仍然清晰可见的细条」的真实起止。
    """
    cols = [(0xF4, 0x72, 0xB6), (0x38, 0xBD, 0xF8), (0xA7, 0x8B, 0xFA),
            (0x34, 0xD3, 0x99), (0xFB, 0xBF, 0x24)]
    band = img[y0:y1, :].astype(np.int16)
    hit = np.zeros(band.shape[:2], dtype=bool)
    per_col = []
    for c in cols:
        d = np.abs(band - np.array(c, dtype=np.int16)).max(axis=2) <= 12
        n = int(d.sum())
        per_col.append({"color": "#%02X%02X%02X" % c, "pixels": n})
        hit |= d
    ys, xs = np.where(hit)
    out = {"per_color": per_col, "total_pixels": int(hit.sum())}
    if len(xs) == 0:
        out["extent_x"] = None
        out["crosses_both_card_edges"] = False
        out["reason"] = "未找到接近细条色的像素"
        return out
    out["extent_x"] = [int(xs.min()), int(xs.max())]
    out["card_edges_x"] = [card_x0, card_x1]
    out["overhang_left"] = card_x0 - out["extent_x"][0]
    out["overhang_right"] = out["extent_x"][1] - card_x1
    out["crosses_both_card_edges"] = bool(
        out["overhang_left"] > 8 and out["overhang_right"] > 8)
    return out


def main() -> None:
    png, tag = sys.argv[1], sys.argv[2]
    tmp = Path(sys.argv[3])
    profile = sys.argv[4] if len(sys.argv) > 4 else "v2"

    # 搜索带按版本布局取：v2 用最终设计的精确几何；v1 布局整体偏移 32px
    # （正是缺陷 V-1），所以用更宽的带，并且没有说明卡/细条可测。
    BANDS = {
        "v2": {"title": (28, 96, 20, 760), "live": (20, 110, 1100),
               "metrics": (116, 283), "review": (620, 792, 1020),
               "card": (390, 890, 446, 596), "stripes": True,
               "stripe_extent": (250, 1030)},
        "v1": {"title": (20, 140, 20, 800), "live": (20, 150, 1060),
               "metrics": (116, 340), "review": (600, 799, 900),
               "card": None, "stripes": False},
    }[profile]

    img = np.array(Image.open(png).convert("RGB"), dtype=np.int16)
    H, W = img.shape[:2]
    m = np.abs(img - BG).max(axis=2) > TH          # 内容掩膜

    rep: dict = {
        "image": png,
        "profile": profile,
        "size": [W, H],
        "size_ok_1280x800": (W, H) == (1280, 800),
        "corner_pixels": [img[0, 0].tolist(), img[0, -1].tolist(),
                          img[-1, 0].tolist(), img[-1, -1].tolist()],
    }

    cb = bbox_of(m)
    rep["content_bbox"] = cb
    if cb:
        clr = {"left": cb[0], "top": cb[1],
               "right": W - 1 - cb[2], "bottom": H - 1 - cb[3]}
        clr["min"] = min(clr.values())
        rep["safe_margin_clearance"] = clr
        rep["all_content_inside_safe_margin"] = clr["min"] >= 32

    # 标题
    ty0, ty1, tx0, tx1 = BANDS["title"]
    t = bbox_of(m[ty0:ty1, tx0:tx1])
    if t:
        b = shift(t, tx0, ty0)
        rep["title"] = {"bbox": b, "w": b[2] - b[0] + 1, "h": b[3] - b[1] + 1,
                        "right_edge": b[2]}

    # LIVE
    ly0, ly1, lx0 = BANDS["live"]
    l = bbox_of(m[ly0:ly1, lx0:W])
    if l:
        b = shift(l, lx0, ly0)
        rep["live"] = {"bbox": b, "w": b[2] - b[0] + 1, "h": b[3] - b[1] + 1,
                       "inside_safe_margin": (b[0] >= 32 and b[1] >= 32
                                              and b[2] <= 1247
                                              and b[3] <= 767)}

    # 三张指标卡（整行扫描连续段）
    my0, my1 = BANDS["metrics"]
    row = m[my0:my1, :]
    colsum = row.any(axis=0)
    runs, s = [], None
    for i, v in enumerate(colsum):
        if v and s is None:
            s = i
        elif not v and s is not None:
            runs.append((s, i - 1))
            s = None
    if s is not None:
        runs.append((s, len(colsum) - 1))
    runs = [r for r in runs if r[1] - r[0] > 40]
    cards = []
    for (x0, x1) in runs:
        bb = bbox_of(m[my0:my1, x0:x1 + 1])
        cards.append({"bbox": shift(bb, x0, my0), "w": x1 - x0 + 1})
    if cards:
        ws = [c["w"] for c in cards]
        gaps = [cards[i + 1]["bbox"][0] - cards[i]["bbox"][2] - 1
                for i in range(len(cards) - 1)]
        rep["metric_cards"] = {
            "count": len(cards), "cards": cards, "widths": ws,
            "max_width_delta": max(ws) - min(ws), "gaps": gaps,
            "expected_width": 384, "expected_gap": 32,
            "widths_match_384": all(abs(w - 384) <= 2 for w in ws),
            "gaps_match_32": all(abs(g - 32) <= 2 for g in gaps),
        }

    # 说明卡：卡外细条 vs 卡内模糊背景。
    # 判据 = 逐列纵向亮度剖面的最大单步跳变 max_step：
    #   1px 过渡（锐利细条）→ 相邻行亮度一次跳到 ~170；
    #   σ=10 高斯会把 10px 细条摊成 20+ px 斜坡 → 单步跳变掉到个位数。
    # 必须排除两类污染，否则结论不成立：
    #   1) 卡体 1px 亮蓝边框（y 上下各 1 行，亮度 156）——它在滤镜之后绘制，本来就锐利；
    #   2) 卡内文字笔画列——文字也在滤镜之后绘制，本来就锐利。
    # 两者都排除后，剩下的才是「卡内被模糊的背景」与「卡外未模糊的背景」的对比。
    if BANDS["stripes"]:
        cx0, cx1, cy0, cy1 = BANDS["card"]
        strip = BANDS.get("stripe_extent") or (250, 1030)
        rep["card_geometry_check"] = card_geometry(img, cx0, cx1, cy0, cy1)
        # 用实测卡体外接框定 y 区间（若与预期不符则以实测为准）
        cb = rep["card_geometry_check"].get("bbox")
        if cb:
            cx0, cy0, cx1, cy1 = cb

        ylo, yhi = cy0 + 2, cy1 - 2          # 严格卡在卡内，避开上下边框
        lum = img[ylo:yhi, :].astype(np.float64) @ LUM

        # 卡内近白像素 = 文字（卡内背景最亮处只有 ~100，远达不到 195）
        cardpx = img[ylo:yhi, cx0 + 2:cx1 - 1].astype(np.int16)
        near_white = cardpx.min(axis=2) > 195
        ty, tx = np.where(near_white)
        tbox = ([int(tx.min()) + cx0 + 2, int(ty.min()) + ylo,
                 int(tx.max()) + cx0 + 2, int(ty.max()) + ylo] if len(tx) else None)
        rep["card_text_bbox"] = tbox

        def clean_cols(a, b):
            """[a,b) 内不含文字笔画的列，等距取若干。"""
            cand = ([x for x in range(a, b) if x < tbox[0] - 3 or x > tbox[2] + 3]
                    if tbox else list(range(a, b)))
            if not cand:
                return []
            step = max(1, len(cand) // 5)
            return cand[::step][:5]

        def col_profile(x):
            d = np.abs(np.diff(lum[:, x]))
            return {"max_step": round(float(d.max()), 2),
                    "mean_step": round(float(d.mean()), 3)}

        groups = {
            "outside_left": clean_cols(strip[0] + 6, cx0 - 6),
            "outside_right": clean_cols(cx1 + 6, strip[1] - 6),
            "inside_left": clean_cols(cx0 + 6, (cx0 + cx1) // 2),
            "inside_right": clean_cols((cx0 + cx1) // 2, cx1 - 6),
        }
        prof = {k: {str(x): col_profile(x) for x in xs} for k, xs in groups.items()}
        out_max = float(np.mean([v["max_step"] for k, xs in prof.items()
                                 if k.startswith("outside")
                                 for v in xs.values()]))
        in_max = float(np.mean([v["max_step"] for k, xs in prof.items()
                                if k.startswith("inside")
                                for v in xs.values()]))
        rep["stripes"] = {
            "method": ("逐列纵向亮度剖面在卡内 y 区间内的最大单步跳变 max_step；"
                       "已排除卡体上下边框行与文字笔画列"),
            "profile_y_range": [ylo, yhi],
            "columns": prof,
            "outside_max_step_mean": round(out_max, 2),
            "inside_max_step_mean": round(in_max, 2),
            "outside_to_inside_ratio": (round(out_max / in_max, 2)
                                        if in_max else None),
            "verdict_outside_sharp": out_max > 60,
            "verdict_inside_soft": in_max < out_max / 3.0,
            "verdict_blur_confined_to_card": bool(
                out_max > 60 and in_max < out_max / 3.0),
        }
        rep["stripe_extent_check"] = stripe_extent(img, cy0, cy1, cx0, cx1)
        # 文字清晰度：文字笔画边缘的单步跳变应远大于卡内模糊背景
        if tbox:
            tb = (img[tbox[1]:tbox[3] + 1, tbox[0]:tbox[2] + 1]
                  .astype(np.float64) @ LUM)
            d = np.abs(np.diff(tb))
            rep["card_text_sharpness"] = {
                "bbox": tbox,
                "max_step": round(float(d.max()), 2),
                "mean_step": round(float(d.mean()), 3),
                "inside_backdrop_max_step": round(in_max, 2),
                "verdict_text_crisp": bool(d.max() > 120),
            }
    else:
        rep["stripes"] = None
        rep["stripes_reason"] = ("该版本没有说明卡与彩色细条结构，"
                                 "卡内/卡外模糊对比不适用")

    # REVIEW
    ry0, ry1, rx0 = BANDS["review"]
    sub = m[ry0:ry1, rx0:W]
    rb = bbox_of(sub)
    if rb:
        b = shift(rb, rx0, ry0)
        ys, xs = np.where(sub)
        cx = float(xs.mean()) + rx0
        x_top = int(xs[ys == ys.min()].mean()) + rx0
        x_bot = int(xs[ys == ys.max()].mean()) + rx0
        ccw = x_top > cx > x_bot
        rep["review"] = {
            "bbox": b, "w": b[2] - b[0] + 1, "h": b[3] - b[1] + 1,
            "expected_rotated_bbox_w_h": [167, 78],
            "centroid_x": round(cx, 1),
            "topmost_x": x_top, "bottommost_x": x_bot,
            "rotation": ("counterclockwise" if ccw
                         else ("clockwise" if (x_top < cx < x_bot)
                               else "unknown")),
            "canvas_clearance": {"left": b[0], "top": b[1],
                                 "right": W - 1 - b[2],
                                 "bottom": H - 1 - b[3]},
            "fully_visible": bool(b[0] >= 0 and b[1] >= 0
                                  and b[2] <= W - 1 and b[3] <= H - 1),
            "inside_safe_margin": bool(b[0] >= 32 and b[1] >= 32
                                       and b[2] <= 1247 and b[3] <= 767),
        }
        # 卡体取色：bbox 内的众数颜色（填充面积远大于文字笔画）
        patch = img[b[1] + 2:b[3] - 1, b[0] + 2:b[2] - 1].reshape(-1, 3)
        keys = (patch // 2) * 2
        flat = [tuple(k) for k in keys]
        cnt = {k: flat.count(k) for k in set(flat)}
        top = max(cnt.items(), key=lambda kv: kv[1])
        rep["review"]["fill_mode_color"] = list(top[0])
        rep["review"]["fill_mode_share"] = round(top[1] / len(flat), 4)
        rep["review"]["expected_fill_for_20pct_white"] = [
            int(round(0.8 * BG[c] + 0.2 * 255)) for c in range(3)]

    rep = plain(rep)
    (tmp / f"{tag}-inspect.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    keep = {k: rep.get(k) for k in
            ("size", "size_ok_1280x800", "content_bbox",
             "safe_margin_clearance", "all_content_inside_safe_margin")}
    print(json.dumps(keep, ensure_ascii=False, indent=1))
    print(json.dumps(rep.get("metric_cards", {}), ensure_ascii=False, indent=1))
    print(json.dumps(rep.get("review", {}), ensure_ascii=False, indent=1))
    print(json.dumps(rep.get("stripes", {}), ensure_ascii=False, indent=1))
    print(json.dumps(rep.get("stripe_extent_check", {}), ensure_ascii=False, indent=1))
    print(json.dumps(rep.get("card_text_sharpness", {}), ensure_ascii=False, indent=1))


def bbox_of(mask: np.ndarray) -> list[int] | None:
    """[left, top, right, bottom] 闭区间；无内容返回 None。"""
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


if __name__ == "__main__":
    main()
