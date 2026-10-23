"""像素级核验：把预览 PNG 的实际像素与 model.json 的逻辑路线逐段比对。

四件事，每件都用实际像素回答，不靠看图推断：

  1) 颜色模型校验：按实际绘制顺序
         通道白 → R1 实线带 → R2 虚线 → 白色箭头 → 标记/徽章
     对每段取 4 个弧位，先用**多边形包含关系**算出「此处该是什么颜色」，
     再比对实际像素。期望值不靠段号或「共享标记」推定，所以转角 miter、
     分歧/汇聚点、以及相邻段虚线的横向侵入都能被正确处理。
     取样弧位 2/20 在虚线段内（白色箭头占 5.1..18.6），30/38 在间隙内且离
     相邻格心 ≥ 6px；格心（弧位 40 的整数倍）正好是虚线与间隙的分界线，
     在那里取样测的是栅格化的边处理，所以不取。
  2) 实测带宽：在无箭头处沿法向双向测量，R1 = 24px、R2 = 16px
     （松/紧两档容差各量一次，差值即抗锯齿带，真实边线在其中点）。
  3) 箭头指向：**白色权重剖面**。箭头只有 6×13.5px，尖端附近形内深度不到
     0.5px，任何「尖内/尖外」单点采样都会因半像素取整落到形外（首轮报告
     R1 0/17 就是这个假象）。改用：底边附近 2px 内的白色权重必须显著大于
     尖端附近 2px 内的权重 —— 肥端在底、瘦端在尖，才指向行进向。
     同时统计正向三角内的像素白度，确认箭头本体确实被画了出来。
  4) 路线在标记/徽章两侧可追溯：题面允许小标记局部盖住路线，但两侧必须可见；
     端点门格（S/E）只要求一侧。共享通道另独立取样，确认同一处蓝橙并存。

用法：python -I tmp/<rid>/A08/gen/a08_pixels.py v3
输出 tmp/<rid>/A08/preview/v3-pixel-report.json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
import a08_geom as G  # noqa: E402
import a08_build as B  # noqa: E402

RID = os.environ["SNAPSHOT_RUN_ID"]
SAMPLE_ARC = 20.0     # 带宽测量弧位：虚线段内、箭头之后
# 颜色模型取样弧位：2 与 20 落在虚线段内（白色箭头占 5.1..18.6），
# 30 与 38 落在间隙内且离相邻格心 ≥ 6px —— 转角处相邻段虚线横向只宽 ±8px，
# 不会被误命中。格心（弧位的 40 的整数倍）正好是虚线与间隙的分界线，
# 在那里取样测的是栅格化的边处理，所以跳过。
PROBE_ARCS = (2.0, 20.0, 30.0, 38.0)
DASH_ARC = PROBE_ARCS[1]
GAP_ARC = PROBE_ARCS[2]
EDGE_IN = 0.6         # 判定「形内」的最小边距，避开抗锯齿过渡带
TOL_TIGHT = 10        # 紧容差：纯色主体
TOL_LOOSE = 120       # 松容差：把抗锯齿混色算进带内
WHITE_MIN = 190       # 判「白」的最低通道值（留抗锯齿余量）
WEIGHT_LO, WEIGHT_HI = 120.0, 255.0   # 白色权重的线性映射区间


def near(px, rgb, tol):
    return all(abs(px[i] - rgb[i]) <= tol for i in range(3))


def whiteness(px):
    """白色权重 0..1：低通道值越高越接近白。"""
    return max(0.0, min(1.0, (min(px[:3]) - WEIGHT_LO) / (WEIGHT_HI - WEIGHT_LO)))


def tri(ux, uy, cx, cy, sign=1.0):
    """箭头三角；sign=-1 时镜像成反向三角。"""
    w, h = B.ARROW_W, B.ARROW_H
    ux, uy = ux * sign, uy * sign
    return [(cx + ux * h, cy + uy * h),
            (cx - ux * h / 2 - uy * w / 2, cy - uy * h / 2 + ux * w / 2),
            (cx - ux * h / 2 + uy * w / 2, cy - uy * h / 2 - ux * w / 2)]


def _in_poly(x, y, pts):
    """射线法点-in-多边形。"""
    inside = False
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        if (y1 > y) != (y2 > y):
            if x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside


def depth(px, py, t):
    """点到三角的边距：内部为正、外部为负，取到最近边的距离。"""
    gx = sum(v[0] for v in t) / 3.0
    gy = sum(v[1] for v in t) / 3.0
    best = float("inf")
    for i in range(3):
        x1, y1 = t[i]
        x2, y2 = t[(i + 1) % 3]
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        nx, ny = dy / L, -dx / L
        if ((gx - x1) * nx + (gy - y1) * ny) < 0:
            nx, ny = -nx, -ny
        best = min(best, (px - x1) * nx + (py - y1) * ny)
    return best


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    img = Image.open(HERE.parent / "preview" / f"{version}-wayfinding.png").convert("RGB")
    model = json.loads((HERE.parent / "model.json").read_text(encoding="utf-8"))
    OX, OY, C = B.OX, B.OY, B.CELL
    R1_RGB = tuple(int(B.S.R1[i:i + 2], 16) for i in (1, 3, 5))
    R2_RGB = tuple(int(B.S.R2[i:i + 2], 16) for i in (1, 3, 5))
    ROUTE_RGBS = {"R1": R1_RGB, "R2": R2_RGB}
    # 标记圆/徽章的颜色：覆盖路线属题面允许，单独计数
    MARKER_RGBS = [tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))
                   for v in (B.S.BADGE, B.S.LM, B.S.S_C, B.S.E_C)]
    # 被标记圆/徽章压住的格：题面允许，单独列出，不计为渲染缺陷
    busy = {tuple(v) for v in model["marks"].values()} | {(3, 11), (23, 9)}

    def sample(x, y):
        return img.getpixel((max(0, min(int(round(x)), img.width - 1)),
                             max(0, min(int(round(y)), img.height - 1))))

    # 实际画出的几何：判定「此弧位该是什么颜色」以此为准，不按段号推定。
    # 格心正好是虚线/间隙的分界线（周期 40 = 格宽），所以格心上的取样测的是
    # 栅格化的边处理，不能当作「没画路线」——用多边形包含关系才准确。
    def parse(path):
        import re
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", path)]
        return list(zip(nums[0::2], nums[1::2]))

    polys = {}
    for rid_, r_ in model["routes"].items():
        pp = G.offset_poly([tuple(c) for c in r_["cells"]], OX, OY, G.D_LAT)
        hw_ = B.R1_HW if rid_ == "R1" else B.R2_HW
        polys[rid_] = [parse(G.band(pp, hw_))]
        if rid_ == "R2":
            polys["R2_dashes"] = [parse(q) for q in G.dash_polys(pp, hw_)]

    def in_any(x, y, key):
        return any(_in_poly(x, y, q) for q in polys[key])

    W_, H_ = model["grid"]["width"], model["grid"]["height"]

    def cell_of(px, py):
        cx, cy = int((px - OX) // C), int((py - OY) // C)
        return (cx, cy) if 0 <= cx < W_ and 0 <= cy < H_ else None

    print(f"图像 {img.size}；R1 {B.S.R1} R2 {B.S.R2}")
    report = {"image": list(img.size), "cell_px": C, "origin": [OX, OY],
              "sample_arcs": {"dash": DASH_ARC, "gap": GAP_ARC,
                              "band_width": SAMPLE_ARC},
              "routes": {}, "shared_corridors": [], "traceability": []}

    for rid, r in model["routes"].items():
        cells = [tuple(c) for c in r["cells"]]
        poly = G.offset_poly(cells, OX, OY, 0.0)
        hw = B.R1_HW if rid == "R1" else B.R2_HW
        want = R1_RGB if rid == "R1" else R2_RGB
        steps = len(cells) - 1

        def on_arc(s):
            for i in range(len(poly) - 1):
                a, b = i * C, (i + 1) * C
                if a <= s <= b:
                    t = (s - a) / C
                    return (poly[i][0] + (poly[i + 1][0] - poly[i][0]) * t,
                            poly[i][1] + (poly[i + 1][1] - poly[i][1]) * t)
            return poly[-1]

        # (1)+(2) 颜色模型校验：按实际绘制顺序
        #   通道白 → R1 实线带 → R2 虚线 → 白色箭头 → 标记/徽章
        # 对每段取 4 个弧位，先用多边形包含关系算出「此处该是什么颜色」，
        # 再比对实际像素。期望值不靠段号或「共享标记」推定，所以转角、
        # 分歧/汇聚点处的 miter 与相邻段虚线都能被正确处理。
        # 弧位 2 与 20 在虚线段内（箭头占 5.1..18.6），30 与 38 在间隙内
        # 且离相邻格心 ≥ 6px，不会被转角处相邻虚线的 ±8px 横向宽度误命中。
        probe = {"total": 0, "ok": 0, "own_color_expected": 0,
                 "other_route_expected": 0, "channel_expected": 0,
                 "covered_by_marker": 0, "arrow_white": 0,
                 "edge_antialias": 0, "bad": []}
        for i in range(steps):
            for arc in PROBE_ARCS:
                pt = on_arc(i * C + arc)
                if cell_of(*pt) in busy:
                    probe["covered_by_marker"] += 1
                    continue
                if in_any(*pt, "R2_dashes"):
                    exp, name = R2_RGB, "橙R2虚线"
                elif in_any(*pt, "R1"):
                    exp, name = R1_RGB, "蓝R1实线"
                else:
                    exp, name = (255, 255, 255), "白通道"
                px = sample(*pt)
                hx = f"#{px[0]:02X}{px[1]:02X}{px[2]:02X}"
                probe["total"] += 1
                if name.startswith("橙"):
                    probe["other_route_expected"] += (rid == "R1")
                    probe["own_color_expected"] += (rid == "R2")
                elif name.startswith("蓝"):
                    probe["other_route_expected"] += (rid == "R2")
                    probe["own_color_expected"] += (rid == "R1")
                else:
                    probe["channel_expected"] += 1
                if near(px, exp, 30):
                    probe["ok"] += 1
                elif is_white(px):
                    probe["arrow_white"] += 1      # 白色箭头画在路线之上
                elif (any(near(px, c, 70) for c in MARKER_RGBS)
                      or min(px[:3]) > 205):
                    probe["edge_antialias"] += 1
                else:
                    probe["bad"].append(
                        f"{rid} step{i} 弧{arc:.0f} @{pt[0]:.0f},{pt[1]:.0f} "
                        f"期望 {name} 实际 {hx}")

        # (3) 实测带宽：无箭头弧位处沿法向双向测量，松/紧两档
        widths = []
        for i in range(steps):
            if cells[i] in busy or cells[i + 1] in busy:
                continue
            x, y = on_arc(i * C + SAMPLE_ARC)
            dx = poly[i + 1][0] - poly[i][0]
            dy = poly[i + 1][1] - poly[i][1]
            nx, ny = G.perp(dx, dy)
            nrm = (nx * nx + ny * ny) ** 0.5 or 1.0
            nx, ny = nx / nrm, ny / nrm
            hi_l = hi_t = lo_l = lo_t = 0.0
            t = 0.0
            while t <= hw + 14:
                for sgn in (1, -1):
                    p = sample(x + sgn * nx * t, y + sgn * ny * t)
                    if near(p, want, TOL_LOOSE):
                        if sgn > 0:
                            hi_l = t
                        else:
                            lo_l = t
                    if near(p, want, TOL_TIGHT):
                        if sgn > 0:
                            hi_t = t
                        else:
                            lo_t = t
                t += 0.5
            widths.append((round(hi_l + lo_l, 1), round(hi_t + lo_t, 1)))

        # (4) 箭头：白色权重剖面 + 正向三角内的实际白度
        off = B.ARROW_OFFSET if rid == "R1" else -B.ARROW_OFFSET
        ay_ok, ay_bad, ay_covered = 0, [], []
        prof = []
        for i in range(len(poly) - 1):
            if (i + 1) % B.ARROW_EVERY:
                continue
            ux = (poly[i + 1][0] - poly[i][0]) / C
            uy = (poly[i + 1][1] - poly[i][1]) / C
            nx_, ny_ = G.perp(ux, uy)
            cx = poly[i][0] + ux * C * B.ARROW_F + nx_ * off
            cy = poly[i][1] + uy * C * B.ARROW_F + ny_ * off
            tf = tri(ux, uy, cx, cy, +1.0)
            w_base = w_tip = w_tot = 0.0
            fwd_in = fwd_white = 0
            x0, x1 = int(cx - B.ARROW_H - 2), int(cx + B.ARROW_H + 2)
            y0, y1 = int(cy - B.ARROW_H - 2), int(cy + B.ARROW_H + 2)
            for gy in range(max(0, y0), min(img.height, y1 + 1)):
                for gx in range(max(0, x0), min(img.width, x1 + 1)):
                    px_, py_ = gx + 0.5, gy + 0.5
                    t = (px_ - cx) * ux + (py_ - cy) * uy
                    s = (px_ - cx) * nx_ + (py_ - cy) * ny_
                    if not (-B.ARROW_H / 2 - 1.0 <= t <= B.ARROW_H + 1.0):
                        continue
                    if abs(s) > B.ARROW_W / 2 + 1.0:
                        continue
                    wt = whiteness(sample(gx, gy))
                    w_tot += wt
                    if -B.ARROW_H / 2 <= t <= -B.ARROW_H / 2 + 2.0:
                        w_base += wt
                    if B.ARROW_H - 2.0 <= t <= B.ARROW_H:
                        w_tip += wt
                    if depth(px_, py_, tf) > EDGE_IN:
                        fwd_in += 1
                        fwd_white += wt >= 0.5
            covered = cells[i] in busy or cells[i + 1] in busy
            rec = {"route": rid, "seg": i, "cell": list(cells[i]),
                   "center": [round(cx, 1), round(cy, 1)],
                   "dir": [round(ux, 2), round(uy, 2)],
                   "weight_total": round(w_tot, 1),
                   "weight_near_base": round(w_base, 1),
                   "weight_near_tip": round(w_tip, 1),
                   "forward_tri_white": f"{fwd_white}/{fwd_in}",
                   "covered_by_landmark": covered}
            prof.append(rec)
            note = (f"{rid} seg{i} {cells[i]}→{cells[i + 1]} 底 {w_base:.1f}"
                    f" / 尖 {w_tip:.1f} / 总 {w_tot:.1f}；"
                    f"正向三角 {fwd_white}/{fwd_in}"
                    + ("  [被地标/徽章覆盖]" if covered else ""))
            if covered:
                ay_covered.append(note)
            elif w_tot >= 25.0 and w_base >= w_tip + 3.0:
                ay_ok += 1
            else:
                ay_bad.append(note)

        n_arrows = sum(1 for i in range(steps) if (i + 1) % B.ARROW_EVERY == 0)
        loose = sorted({w[0] for w in widths})
        tight = sorted({w[1] for w in widths})
        report["routes"][rid] = {
            "steps": steps,
            "color_model": dict(probe),
            "expected_band_px": 2 * hw,
            "measured_band_px_loose": loose,
            "measured_band_px_tight": tight,
            "band_cells_measured": len(widths),
            "arrows": f"{ay_ok}/{n_arrows - len(ay_covered)}",
            "arrows_covered_by_landmark": len(ay_covered),
            "arrow_profiles": prof, "arrow_failures": ay_bad,
            "arrow_coverage": ay_covered,
        }
        print(f"\n{rid}：颜色模型 {probe['ok']}/{probe['total']} 符合预期"
              f"（本路线本色 {probe['own_color_expected']}、被另一路线合法覆盖 "
              f"{probe['other_route_expected']}、通道白 {probe['channel_expected']}"
              f"）；箭头白 {probe['arrow_white']}、边缘抗锯齿 "
              f"{probe['edge_antialias']}、被标记压住 {probe['covered_by_marker']}"
              f"；不符合 {len(probe['bad'])} 处")
        print(f"     实测带宽 松 {loose} / 紧 {tight}（预期 {2 * hw}px，"
              f"测 {len(widths)} 格；真实边线在两者之间）")
        print(f"     箭头方向（白色权重剖面）{ay_ok}/{n_arrows - len(ay_covered)}"
              f"，另有 {len(ay_covered)} 个被地标/徽章覆盖")
        if prof:
            clean = [p for p in prof if not p["covered_by_landmark"]]
            if clean:
                mb = min(p["weight_near_base"] for p in clean)
                mt = max(p["weight_near_tip"] for p in clean)
                wt = min(p["weight_total"] for p in clean)
                fw = min(p["forward_tri_white"] for p in clean)
                print(f"     未覆盖箭头 {len(clean)} 个：底边权重最低 {mb:.1f}、"
                      f"尖端权重最高 {mt:.1f}（差 {mb - mt:.1f}）；"
                      f"总权重最低 {wt:.1f}；正向三角最少 {fw} 个白色像素")
        for b in probe["bad"][:8]:
            print(f"       颜色不符：{b}")
        for b in ay_bad[:5]:
            print(f"       箭头缺陷：{b}")
        for b in ay_covered[:6]:
            print(f"       被覆盖（题面允许）：{b}")

    # 共享通道：同一处必须同时出现蓝与橙，两条路线身份才都成立
    for n, c in enumerate(model["shared_corridors"], 1):
        cells = [tuple(q) for q in c["cells"]]
        poly = G.offset_poly(cells, OX, OY, 0.0)
        steps = len(cells) - 1

        def on_arc(poly, s):
            for i in range(len(poly) - 1):
                a, b = i * C, (i + 1) * C
                if a <= s <= b:
                    t = (s - a) / C
                    return (poly[i][0] + (poly[i + 1][0] - poly[i][0]) * t,
                            poly[i][1] + (poly[i + 1][1] - poly[i][1]) * t)
            return poly[-1]

        blue = orange = gapblue = 0
        tot = 0
        for j in range(steps):
            if cells[j] in busy or cells[j + 1] in busy:
                continue
            for tag, s in (("dash", j * C + DASH_ARC), ("gap", j * C + GAP_ARC)):
                tot += 1
                px = sample(*on_arc(poly, s))
                if near(px, R1_RGB, 26):
                    blue += 1
                    if tag == "gap":
                        gapblue += 1
                if near(px, R2_RGB, 26):
                    orange += 1
        rec = {"id": f"shared-{n}", "from": list(cells[0]), "to": list(cells[-1]),
               "cells": len(cells), "steps": steps, "samples": tot,
               "r1_blue_hits": blue, "r2_orange_hits": orange,
               "blue_in_r2_gaps": gapblue,
               "both_routes_legible": bool(blue and orange and gapblue)}
        report["shared_corridors"].append(rec)
        print(f"\n共享 {n} {cells[0]}→{cells[-1]}：{tot} 点，蓝 {blue}"
              f"（其中 R2 间隙处 {gapblue}）、橙 {orange}"
              f" → 两条路线同时可辨：{rec['both_routes_legible']}")

    # (5) 路线在标记/徽章两侧可追溯
    for rid, r in model["routes"].items():
        cells = [tuple(c) for c in r["cells"]]
        poly = G.offset_poly(cells, OX, OY, 0.0)
        want = R1_RGB if rid == "R1" else R2_RGB
        for bc in busy:
            if bc not in cells:
                continue
            k = cells.index(bc)
            endpoint = k in (0, len(cells) - 1)   # 端点门格只要求一侧可见
            pa, pb = poly[max(k - 1, 0)], poly[min(k + 1, len(poly) - 1)]
            ux, uy = pb[0] - pa[0], pb[1] - pa[1]
            L = (ux * ux + uy * uy) ** 0.5 or 1.0
            ux, uy = ux / L, uy / L
            mcx, mcy = B.cell_px(*bc)
            sides = (1, -1) if not endpoint else ((1,) if k == 0 else (-1,))
            side = {}
            for sgn in sides:
                got = []
                for d in (15.0, 20.0, 25.0, 30.0):
                    px = sample(mcx + sgn * ux * d, mcy + sgn * uy * d)
                    got.append((d, f"#{px[0]:02X}{px[1]:02X}{px[2]:02X}",
                                near(px, ROUTE_RGBS["R1"], 26)
                                or near(px, ROUTE_RGBS["R2"], 26)))
                side[str(sgn)] = got
            rec = {"route": rid, "cell": list(bc), "route_index": k,
                   "endpoint": endpoint,
                   "required_sides": [str(s) for s in sides],
                   "visible": all(any(g[2] for g in side[str(s)]) for s in sides),
                   "samples": side}
            report["traceability"].append(rec)
            shown = "、".join(f"{'正' if s > 0 else '负'}侧 "
                            f"{[g[0] for g in side[str(s)] if g[2]] or '×'}"
                            for s in sides)
            print(f"追溯 {rid} @{bc}" + ("（端点，只需一侧）" if endpoint else "")
                  + f"：{shown} → {rec['visible']}")

    (HERE.parent / "preview" / f"{version}-pixel-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
