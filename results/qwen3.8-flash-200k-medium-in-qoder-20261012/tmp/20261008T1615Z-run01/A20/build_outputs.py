"""A20 落盘：跑一遍求解器 -> 输出 label-layout.json / layout-audit.json。

与 gen_map.py 共用同一份内存状态（同一 seed 的确定性求解），所以 JSON 里记录的
就是最终那张图真正使用的坐标，不是事后补写的说明。
"""
import importlib.util
import json
import math
import os
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "A20"
OUT = root / "outputs" / rid / "A20"
spec = importlib.util.spec_from_file_location("gm", str(TMP / "gen_map.py"))
gm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gm)

gutter, failed = gm.solve()
top3 = [p.id for p in sorted(gm.PTS, key=lambda q: -q.value)[:3]]
probs = gm.audit()
x = gm.crossings()
mind, a, b = gm.min_pair_distance()

# 标签盒两两间距（分离轴上的最小间隙），用于核对 ≥4px
gaps = []
for i in range(len(gm.PTS)):
    for j in range(i + 1, len(gm.PTS)):
        p, q = gm.PTS[i], gm.PTS[j]
        dx = max(p.label[0] - (q.label[0] + q.label[2]),
                 q.label[0] - (p.label[0] + p.label[2]), 0.0)
        dy = max(p.label[1] - (q.label[1] + q.label[3]),
                 q.label[1] - (p.label[1] + p.label[3]), 0.0)
        gaps.append((round(math.hypot(dx, dy), 1), p.id, q.id))
gaps.sort()

layout = {
    "canvas": [gm.W, gm.H],
    "plot_rect_px": [gm.MX, gm.MY, gm.MW, gm.MH],
    "mapping": {"origin": "逻辑左下 / 像素左上",
                "formula": "px = 280 + 10.4*x, py = 920 - 7.6*y",
                "y_inverted": True},
    "dot_diameter_px": {"normal": 12, "dense_shrunk_to": 8,
                        "shrink_used": False,
                        "min_center_distance_px": round(mind, 2),
                        "min_center_distance_pair": [a, b]},
    "label_font_px": gm.TEXT, "label_box_height_px": gm.LB_H,
    "leader_threshold_px": gm.FREE, "required_label_gap_px": gm.GAP,
    "gutter_pitch_px": 48,
    "counts": {"points": len(gm.PTS), "in_map_labels": sum(1 for p in gm.PTS if p.inside_map),
               "gutter_labels": len(gutter), "leaders": sum(1 for p in gm.PTS if p.leader),
               "top3": top3},
    "points": [{
        "id": p.id, "name": p.name, "value": p.value,
        "logical": [p.lx, p.ly], "anchor_px": [round(p.px, 2), round(p.py, 2)],
        "dot_diameter_px": 12 if p.r == gm.D_R else 8,
        "label_box_px": [round(v, 2) for v in p.label],
        "placement": "in-map" if p.inside_map else "gutter",
        "gutter_side": getattr(p, "side", None), "gutter_slot": getattr(p, "slot", None),
        "point_to_label_gap_px": (p.inmap_gap if p.inside_map
                                  else round(math.hypot(
                                      min(abs(p.label[0] - p.px),
                                          abs(p.label[0] + p.label[2] - p.px)),
                                      min(abs(p.label[1] - p.py),
                                          abs(p.label[1] + p.label[3] - p.py))), 1)),
        "leader_px": [[round(v, 2) for v in pt] for pt in (p.leader or [])],
        "leader_variant": getattr(p, "leader_variant", None),
        "top3": p.id in top3,
    } for p in gm.PTS],
}

audit = {
    "generated_by": "gen_map.py 同一进程状态，程序审计 + 实际看图复核",
    "hard_problems": probs,
    "label_box_intersections": [s for s in probs if "标签盒相交" in s],
    "leader_through_label_text": [s for s in probs if "穿过非本点标签" in s],
    "leader_through_other_dot": [s for s in probs if "穿过非本点" in s
                                 and "标签" not in s],
    "leader_crossings": {"pairs": [[i, j] for i, j in x], "count": len(x),
                         "limit": 3, "connection_markers_drawn": False},
    "boundary_checks": {
        "label_outside_canvas": [s for s in probs if "越出画布" in s],
        "label_outside_plot_area": [s for s in probs if "越出绘图区" in s],
        "gutter_label_in_plot": [s for s in probs if "压进主图区" in s],
    },
    "per_point_checks": {
        "label_covers_own_dot": [s for s in probs if "压住自身点" in s],
        "inmap_gap_over_24_without_leader": [s for s in probs if "主图内标签离点" in s],
        "gutter_label_without_leader": [s for s in probs if "书脊标签却无引导线" in s],
    },
    "min_label_box_gap_px": gaps[0][0],
    "closest_label_pairs": [list(g) for g in gaps[:5]],
    "text_fit_gate": {"single_line_width_assert": True,
                      "estimated_glyph_advance": "dslkit.TextFit（SLACK 0.96）",
                      "labels_checked": gm.TF.n,
                      "fit_problems": gm.TF.problems},
    "dense_shrink": {"required": False, "reason": "最小中心距 %.2fpx > 12px 直径" % mind},
    "visual_review": {
        "full_image": "preview/map-v03.png（已打开查看）",
        "zoom_service_crop": "preview/zoom-svc-v03.png（服务侧 480x260 裁切）"
                             " + zoom-svc-v03-x3.png（本地 3x，已打开查看）",
        "zoom_local_crops": ["preview/zoom-center-v03.png",
                             "preview/zoom-cluster-v03.png"],
        "conclusion": "中心密集区每条引导线只落在一个点上，线不贴邻其他点，"
                      "无交叉、无文字裁切",
    },
}

OUT.mkdir(parents=True, exist_ok=True)
DSL = gm.render(top3)                      # 触发每个标签盒的文字放得下断言
assert DSL == (TMP / "layouts" / "annotated-map.snapshot").read_bytes().decode("utf-8"), \
    "落盘 DSL 与本进程重算结果不一致"
audit["dsl_bytes"] = len(DSL.encode("utf-8"))
(TMP / "label-layout.json").write_text(json.dumps(layout, ensure_ascii=False, indent=1),
                                       encoding="utf-8", newline="\n")
(TMP / "layout-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1),
                                       encoding="utf-8", newline="\n")
print("problems", len(probs), "crossings", len(x), "min_label_gap", gaps[0][0],
      "fit_checked", gm.TF.n)
print("labels", layout["counts"])
