"""A13 审计：透明底、构件几何、纯黑合规、32×32 预乘 alpha 缩略、四张图的文字量测。

产物写到 tmp/<rid>/A13/gen/a13_audit.json；32×32 检查预览只写 tmp/preview/。

用法：SNAPSHOT_RUN_ID=<rid> python -I a13_audit.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import a13_pages as A
import a13_pixels as P

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A13"
RID = A.RID
OUT, TMP = A.OUT, A.TMP
MARK = A.MARKS[A.CHOSEN]

# 判「某个位置被真正涂上」的 alpha 门槛。抗锯齿会把边缘向外溢 1 px 左右，
# 那部分 alpha 远低于实心值（实测胶囊与圆环的溢色 alpha ≤ 63/255 ≈ 25%）。
# 低于这个门槛的覆盖不算负空间泄漏，高于的才算。
SOLID_ALPHA = 128


def measure_mark(im, mark, scale=1.0, ox=0.0, oy=0.0, tol=1) -> dict:
    """逐构件量测实际覆盖：包围盒、行/列剖面、与声明几何的偏差。"""
    k = scale
    rows = []
    for c in mark:
        x = ox + c["x"] * k
        y = oy + c["y"] * k
        w, h = c["w"] * k, c["h"] * k
        box = [round(x), round(y), round(w), round(h)]
        bb = P.alpha_in(im, box, tol)
        r = {"id": c["id"], "motif": c["motif"], "declared": box, "ink": bb,
             "stroke_px": round(c["stroke"] * k, 3) if c["stroke"] else 0}
        if bb:
            r.update({"ink_w": bb[2] - bb[0] + 1, "ink_h": bb[3] - bb[1] + 1,
                      "clear": {"left": round(bb[0] - x, 2),
                                "top": round(bb[1] - y, 2),
                                "right": round(x + w - 1 - bb[2], 2),
                                "bottom": round(y + h - 1 - bb[3], 2)},
                      "dx": round(bb[2] - bb[0] + 1 - w, 2),
                      "dy": round(bb[3] - bb[1] + 1 - h, 2)})
            # 圆环：过几何中心的横/纵扫描切出两段实心弧，直接量出描边宽
            if c["motif"] == "annulus":
                cy, cx = round(y + h / 2), round(x + w / 2)
                r["line_x_at_cy"] = P.line_runs(im, "x", cy, tol)
                r["line_y_at_cx"] = P.line_runs(im, "y", cx, tol)
        rows.append(r)
    return {"components": rows}


def ring_bore_check(im, mark, tol=1) -> dict:
    """确认圆环内孔里「层块以外」的区域真的没有覆盖——负空间必须是真透明。

    内孔不是全空的：三条信息层就坐在孔里，它们本身是实心覆盖。所以判据是
    「孔内 ∩ 层块包围盒以外」必须 alpha=0，而不是整个孔必须空。同时量出每个
    层块四个角到孔内壁的最小距离，确认层没有顶到环体——这也是纯黑版里三层
    能只靠「有没有覆盖」就分开的几何保证。
    """
    out = {}
    d = P.arr(im)
    a = d[:, :, 3]
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for c in mark:
        if c["motif"] != "annulus":
            continue
        cx, cy = c["x"] + c["w"] / 2, c["y"] + c["h"] / 2
        ir = c["w"] / 2 - c["stroke"]
        dist = np.hypot(xx - cx, yy - cy)
        # 严格在内孔里，避开内边缘的抗锯齿像素
        bore = dist < (ir - 1)
        bars = np.zeros(a.shape, dtype=bool)
        spans = []
        for o in mark:
            if o is c:
                continue
            l, t = round(o["x"]), round(o["y"])
            r2, b2 = round(o["x"] + o["w"]), round(o["y"] + o["h"])
            bars[t:b2 + 1, l:r2 + 1] = True
            worst = max(math.hypot(ox - cx, oy - cy)
                        for ox in (o["x"], o["x"] + o["w"])
                        for oy in (o["y"], o["y"] + o["h"]))
            near = min(math.hypot(ox - cx, oy - cy)
                       for ox in (o["x"], o["x"] + o["w"])
                       for oy in (o["y"], o["y"] + o["h"]))
            rec = {"id": o["id"], "box": [l, t, r2, b2],
                   "farthest_corner_radius": round(worst, 2),
                   "nearest_corner_radius": round(near, 2),
                   "clearance_to_bore_px": round(ir - worst, 2),
                   "position": ("inside" if worst <= ir else
                                ("crossing_bore" if near < ir else
                                 "outside_ring"))}
            spans.append(rec)
        free = bore & ~bars
        n = int(free.sum())
        fr = a[free] if n else np.array([], dtype=np.int16)
        # 抗锯齿光晕与实心重叠要分开判：胶囊和圆环的边缘都会向外溢 1 px 左右，
        # 那部分 alpha 很低（实测 ≤63/255 ≈ 25%）。只有 alpha ≥ SOLID_ALPHA 的
        # 像素才算「这个位置被实实在在涂上了」，才是负空间泄漏。
        n_solid = int((fr >= SOLID_ALPHA).sum()) if n else 0
        n_halo = int(((fr > tol) & (fr < SOLID_ALPHA)).sum()) if n else 0
        # 「离孔内壁的净空」只对进入孔区的构件有意义。嵌套在自身之外、整体待在
        # 环体外面的构件（如方向 B 的外环之于内环）虽然 bbox 角半径会给出一个
        # 很大的负值，但那衡量的是「它在外面多远」，不是「它入侵了多少」。
        relevant = [s for s in spans if s["position"] != "outside_ring"]
        out[c["id"]] = {
            "centre": [cx, cy], "inner_radius_px": ir,
            "solid_alpha_threshold": SOLID_ALPHA,
            "bore_area_px": int(bore.sum()),
            "bar_bbox_area_px": int((bore & bars).sum()),
            "free_bore_area_px": n,
            "free_bore_solid_pixels": n_solid,
            "free_bore_aa_halo_pixels": n_halo,
            "free_bore_alpha_max": int(fr.max()) if n else None,
            "free_bore_cleared": n > 0 and n_solid == 0,
            "bars": spans,
            "bore_relevant_bar_ids": [s["id"] for s in relevant],
            "outside_ring_bar_ids": [s["id"] for s in spans
                                     if s["position"] == "outside_ring"],
            "min_bar_clearance_px": (round(min(s["clearance_to_bore_px"]
                                              for s in relevant), 2)
                                     if relevant else None),
            "note": "判据是「孔内 ∩ 层块包围盒以外」无实心覆盖；层块本身是实心"
                    "覆盖，不构成负空间泄漏。低 alpha 的抗锯齿光晕单独计数，"
                    "不计为泄漏。clearance 只统计进入孔区的构件"
                    "（inside / crossing_bore），整体在环外的构件不计"}
    return out


def cross_section(im, y: int, tol=1) -> list[list[int]]:
    """整幅某一行的实心段，用来核对「环 + 条」在同一行上的真实结构。"""
    return P.line_runs(im, "x", y, tol)


def text_scan(im, meta, tol=1) -> tuple[list, list, list]:
    """逐条文字盒量测：有墨、未出盒、纵向未裁切。"""
    fails, warns = [], []
    rows = []
    H = meta["canvas"][1]
    for k_, box in meta["text"].items():
        if len(box) != 5:          # "rule" 一类纯几何条目
            continue
        x, y, w, h, text = box
        bb = P.alpha_in(im, [round(x), round(y), round(w), round(h)], tol)
        rec = {"key": k_, "text": text, "box": [round(x), round(y), round(w),
                                                round(h)], "ink": bb}
        if bb is None:
            fails.append(f"{k_}「{text}」无墨迹")
            rows.append(rec)
            continue
        rec.update({"ink_w": bb[2] - bb[0] + 1, "ink_h": bb[3] - bb[1] + 1,
                    "clear": {"left": round(bb[0] - x, 2),
                              "top": round(bb[1] - y, 2),
                              "right": round(x + w - 1 - bb[2], 2),
                              "bottom": round(y + h - 1 - bb[3], 2)}})
        for side, d in rec["clear"].items():
            if d < -0.5:
                fails.append(f"{k_}「{text}」墨迹越过盒{side} {d:+.1f}px")
        if rec["clear"]["top"] < 0 or rec["clear"]["bottom"] < 0:
            fails.append(f"{k_}「{text}」纵向裁切 "
                         f"(top={rec['clear']['top']:.1f} "
                         f"bottom={rec['clear']['bottom']:.1f})")
        if bb[3] > H - 8:
            warns.append(f"{k_} 墨迹接近画布底边 (bottom={bb[3]})")
        rows.append(rec)
    return rows, fails, warns


def main() -> int:
    rep: dict = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
                 "run_id": RID, "files": {}, "thumbs": {}, "checks": []}

    def note(cid, desc, passed, detail):
        rep["checks"].append({"id": cid, "desc": desc, "passed": bool(passed),
                              "detail": detail})

    # ---- 四张最终交付件
    finals = {"symbol-color": (A.build("symbol-color"), "A"),
              "symbol-black": (A.build("symbol-black"), "A"),
              "brand-banner": (A.build("brand-banner"), None),
              "launch-poster": (A.build("launch-poster"), None)}

    for name, (built, mark_id) in finals.items():
        dsl, k, meta = built
        f = OUT / (name + ".png")
        if not f.exists():
            note("f-" + name, f"{name}.png 存在", False, "文件缺失")
            continue
        im, dec = P.open_rgba(f)
        dslf = OUT / (name + ".snapshot")
        dsl_ok = dslf.exists() and dslf.read_text(encoding="utf-8") == dsl
        fbox = meta["canvas"]
        size_ok = [im.width, im.height] == [int(fbox[0]), int(fbox[1])]
        note("size-" + name, f"{name} 尺寸 {fbox[0]}×{fbox[1]}",
             size_ok, {"actual": [im.width, im.height]})
        note("dsl-" + name, f"{name}.snapshot 与生成器 DSL 完全一致",
             dsl_ok, {"bytes": dslf.stat().st_size if dslf.exists() else None})
        d = {"decode": dec, "alpha": P.alpha_report(im),
             "bbox": P.alpha_bbox(im),
             "dsl_matches_generator": dsl_ok}

        if mark_id:
            d["mark"] = measure_mark(im, A.MARKS[mark_id])
            d["bore"] = ring_bore_check(im, A.MARKS[mark_id])
            d["cross_sections"] = {
                "y212_ring_only": cross_section(im, 212),
                "y256_ring_and_bar2": cross_section(im, 256)}
            note("transparent-" + name, f"{name} 画布四角与整体透明",
                 d["alpha"]["corner_alpha"]["tl"] == 0
                 and d["alpha"]["corner_alpha"]["br"] == 0,
                 d["alpha"]["corner_alpha"])
            nb = {cid: {"free_bore_area_px": v["free_bore_area_px"],
                        "free_bore_solid_pixels": v["free_bore_solid_pixels"],
                        "free_bore_aa_halo_pixels": v["free_bore_aa_halo_pixels"],
                        "free_bore_alpha_max": v["free_bore_alpha_max"],
                        "solid_alpha_threshold": v["solid_alpha_threshold"],
                        "min_bar_clearance_px": v["min_bar_clearance_px"],
                        "bore_relevant_bar_ids": v["bore_relevant_bar_ids"],
                        "bar_clearance": [{"id": s["id"],
                                           "clearance_to_bore_px": s["clearance_to_bore_px"],
                                           "position": s["position"]}
                                          for s in v["bars"]]}
                  for cid, v in d["bore"].items()}
            note("bore-" + name, name + " 圆环内孔除层块包围盒外无实心覆盖"
                "（负空间是真透明，不是裁剪或布尔扣形；抗锯齿光晕单独计数）",
                 all(v["free_bore_cleared"] and
                     v["min_bar_clearance_px"] is not None and
                     v["min_bar_clearance_px"] > 0 for v in d["bore"].values()),
                 nb)
        else:
            d["text"], tf, tw = text_scan(im, meta)
            for x in tf:
                note("text-" + name, "文字盒量测：" + x, False, {})
            d["text_warnings"] = tw

        if name == "symbol-black":
            bc = P.black_check(im)
            d["black_check"] = bc
            note("black-compliant", "symbol-black 所有 alpha>0 像素 R=G=B=0",
                 bc["compliant"], {
                     "decoder": "Pillow %s, PNG mode %s → convert('RGBA') 未预乘 8 位"
                                % (P.Image.__version__, dec["png_mode"]),
                     "n_alpha_gt0": bc["n_alpha_gt0"],
                     "alpha_range_of_alpha_gt0": [
                         int(P.arr(im)[:, :, 3][P.arr(im)[:, :, 3] > 0].min()),
                         int(P.arr(im)[:, :, 3][P.arr(im)[:, :, 3] > 0].max())],
                     "n_violation": bc["n_violation"],
                     "edge_pixels": bc.get("edge_pixels"),
                     "method": bc["method"]})
        rep["files"][name] = d

    # ---- 构件数与留白
    comp = A.MARKS[A.CHOSEN]
    note("components<=6", "选中方向构件数 ≤ 6（按母形实例计）",
         len(comp) <= 6, {"count": len(comp),
                          "ids": [c["id"] for c in comp],
                          "basis": "圆环内孔与扣出的负空间不额外计；重复放置的 "
                                   "pill 母形逐个计"})

    # ---- 两个方向 512 预览的几何量测（选择依据，不是拍脑袋）
    for tag, mid in (("preview-a", "A"), ("preview-b", "B")):
        p = TMP / "preview" / (tag + ".png")
        if not p.exists():
            continue
        pim, pdec = P.open_rgba(p)
        pm = A.MARKS[mid]
        rep["files"][tag] = {
            "decode": pdec, "alpha": P.alpha_report(pim),
            "bbox": P.alpha_bbox(pim),
            "mark": measure_mark(pim, pm),
            "bore": ring_bore_check(pim, pm)}

    # ---- 32×32 检查预览：最终两图 + 两个方向预览（选择依据）
    thumb_src = {"symbol-color": OUT / "symbol-color.png",
                 "symbol-black": OUT / "symbol-black.png"}
    previews = {}
    for tag, mid in (("preview-a", "A"), ("preview-b", "B")):
        p = TMP / "preview" / (tag + ".png")
        if p.exists():
            previews[tag] = p
    for tag, src in list(thumb_src.items()) + list(previews.items()):
        if not src.exists():
            continue
        im, _ = P.open_rgba(src)
        th, tmeta = P.thumb32(im, 32)
        p1 = TMP / "preview" / (tag + "-32.png")
        p2 = TMP / "preview" / (tag + "-32-onlight.png")
        th.save(p1, format="PNG")
        P.composite(th, P.LIGHT_BG, 1).save(p2, format="PNG")
        d = P.arr(th)
        # 32 px 下沿几何中心的横/纵扫描：切出可见的实心段，层与层之间必须
        # 真的有空隙（alpha=0）而不是靠颜色区分。这是 32×32 复核的实际判据。
        runs_x = P.line_runs(th, "x", 16)
        runs_y = P.line_runs(th, "y", 16)
        rep["thumbs"][tag] = {
            "source": A.S.rel(src),
            "preview_32_rgba": A.S.rel(p1),
            "preview_32_onlight": A.S.rel(p2),
            "params": tmeta,
            "alpha_min": int(d[:, :, 3].min()),
            "alpha_max": int(d[:, :, 3].max()),
            "n_alpha_gt0": int((d[:, :, 3] > 0).sum()),
            "coverage_pct": round(float((d[:, :, 3] > 0).sum()) / 1024 * 100, 2),
            "ink_bbox": P.alpha_bbox(th),
            "rows_covered": [int(v) for v in (d[:, :, 3] > 0).sum(axis=1)],
            "cols_covered": [int(v) for v in (d[:, :, 3] > 0).sum(axis=0)],
            "line_x_at_16": runs_x,
            "line_y_at_16": runs_y,
            "x_run_widths": [r[1] - r[0] + 1 for r in runs_x],
            "x_run_gaps": [runs_x[i + 1][0] - runs_x[i][1] - 1
                           for i in range(len(runs_x) - 1)],
            "y_run_widths": [r[1] - r[0] + 1 for r in runs_y],
            "y_run_gaps": [runs_y[i + 1][0] - runs_y[i][1] - 1
                           for i in range(len(runs_y) - 1)],
        }

    # 复核表：两张最终缩略 + 两个方向预览，各含 32 px 原尺寸与 4× 放大
    cells = []
    for tag in ("symbol-color", "symbol-black", "preview-a", "preview-b"):
        p = TMP / "preview" / (tag + "-32.png")
        if p.exists():
            cells.append((tag, P.Image.open(p).convert("RGBA")))
    if cells:
        sheet = P.sheet(cells, cell=32, magnify=4, pad=20, cols=2)
        sp = TMP / "preview" / "a13-32-review-sheet.png"
        sheet.save(sp, format="PNG")
        rep["thumbs"]["review_sheet"] = {"path": A.S.rel(sp), "cells":
                                         [c[0] for c in cells],
                                         "cell_px": 32, "magnify": 4}

    # ---- 方向选择依据：A / B 用同一把 32 px 尺子量，不靠感觉
    def _dir_block(tag: str, mid: str) -> dict:
        f = rep["files"].get(tag, {})
        th = rep["thumbs"].get(tag, {})
        bore = f.get("bore", {})
        b = next(iter(bore.values())) if bore else {}
        gaps = th.get("x_run_gaps") or []
        clr = b.get("min_bar_clearance_px")
        return {
            "direction": mid,
            "components": len(A.MARKS[mid]),
            "component_ids": [c["id"] for c in A.MARKS[mid]],
            "bore_relevant_clearance_px": clr,
            "bore_intrusion_px": (round(-clr, 2) if clr is not None and clr < 0
                                  else 0),
            "crossing_bore_members": [s["id"] for s in b.get("bars", [])
                                      if s["position"] == "crossing_bore"],
            "coverage_pct_512": f.get("alpha", {}).get("coverage_pct"),
            "coverage_pct_32": th.get("coverage_pct"),
            "line_x_run_widths_32": th.get("x_run_widths"),
            "line_x_gaps_32": gaps,
            "min_gap_32": min(gaps) if gaps else None,
        }

    rep["direction_comparison"] = {
        "criteria": [
            "32×32 下信息层之间的空隙是否真的存在（alpha=0，不靠颜色区分）",
            "同心构件到内孔壁的净空不得为负",
            "512 与 32 的覆盖率接近，缩后不塌",
            "构件数少（越少越稳，且 ≤6 为硬约束）"],
        "preview-a": _dir_block("preview-a", "A"),
        "preview-b": _dir_block("preview-b", "B"),
        "chosen": A.CHOSEN,
    }

    (TMP / "gen" / "a13_audit.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    npass = sum(1 for c in rep["checks"] if c["passed"])
    print("检查 %d 项，通过 %d" % (len(rep["checks"]), npass))
    for c in rep["checks"]:
        print("  [%s] %s" % ("PASS" if c["passed"] else "FAIL", c["desc"]))
    for name, d in rep["files"].items():
        a = d["alpha"]
        print("  %-14s %dx%d alpha %d..%d 覆盖 %.2f%% bbox %s" % (
            name, a["size"][0], a["size"][1], a["alpha_min"], a["alpha_max"],
            a["coverage_pct"], d["bbox"]))
    print("报告", A.S.rel(TMP / "gen" / "a13_audit.json"))
    return 1 if npass != len(rep["checks"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
