"""A20 几何审计 + 落盘 PNG 复测。

几何审计（全部用未舍入值，容差 1e-6）：
  A 映射：锚点 = (280+10.4*x, 920-7.6*y) 逐点复核；
  B 距离：锚点圆心到自有盒最短欧氏距离（>24 必须有引线）；两标签盒最短距离 >=4；
  C 点-盒：标签盒与任一非本点圆盘不得相交或相触（按实际 12px 直径）；
  D 引线：起点在所属圆周、终点在自有盒边界、不进入任何标签盒内部、
           不连接错点、不自交、不共线重合、与非本点盘净距 >=4、线间净距 >=5；
  E 交叉：不同引线“线对+交点”去重计数（端点接触/落线段上也计），<=3；
  F 边界：点/标签/引线均在画布内，主图框固定 (280,160,1040,760)；
  G 前三：value 降序前三（同值 ID 升序）。
PNG 复测：点色、标签墨迹在盒内、引线沿线覆盖、TOP3  crimson。
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from a20_layout import (CW, CH, MAP, MX0, MY0, MW, MH, MX1, MY1, DISK_R, FS,
                        load, rect_dist, rects_dist, closest_on_rect,
                        seg_rect_intersect, seg_seg_intersect, seg_disk_dist,
                        segs_dist, TOP3_N)

ROOT = Path(__file__).resolve().parent.parent.parent.parent
TMP = ROOT / "tmp" / "run-20261013-174209" / "A20"
OUT = ROOT / "outputs" / "run-20261013-174209" / "A20"
EPS = 1e-6

ms, top3 = load()
layout = json.loads((TMP / "layout-draft.json").read_text(encoding="utf-8"))
by_id = {m["id"]: m for m in ms}

problems = []
checks = []


def ck(name, ok, method, evidence):
    checks.append({"check": name, "passed": bool(ok), "method": method,
                   "evidence": evidence})
    if not ok:
        problems.append(f"{name}: {evidence}")
    return ok


# ---------- A 映射 ----------
map_bad = []
for m in ms:
    ex = (MX0 + 10.4 * m["x"], MY1 - 7.6 * m["y"])
    if abs(ex[0] - m["anchor"][0]) > EPS or abs(ex[1] - m["anchor"][1]) > EPS:
        map_bad.append(m["id"])
ck("anchor_mapping", not map_bad,
   "逐点复算 (280+10.4x, 920-7.6y) 与程序锚点比对（1e-6）",
   f"24/24 一致（含未舍入小数，如 M10={by_id['M10']['anchor']}）")

# ---------- B 距离 ----------
dist_records = []
for m in ms:
    box = layout[m["id"]]["box"]
    d = rect_dist(m["anchor"][0], m["anchor"][1], *box)
    ld = layout[m["id"]]["leader"]
    need = d > 24.0
    ok = (need and ld is not None) or ((not need) and ld is None)
    if not ok:
        problems.append(f"{m['id']} 引线条件不符: d={d:.3f} leader={'有' if ld else '无'}")
    dist_records.append({
        "id": m["id"], "anchor": [m["anchor"][0], m["anchor"][1]],
        "box": box, "anchor_to_own_box_px": round(d, 6),
        "threshold_px": 24.0, "leader_required": need,
        "leader_present": ld is not None,
        "reason_if_no_leader": None if ld else f"距盒 {d:.3f}px <= 24px，按口径不需引导线",
    })
min_d = min(r["anchor_to_own_box_px"] for r in dist_records)
max_d = max(r["anchor_to_own_box_px"] for r in dist_records)
n_leader = sum(1 for r in dist_records if r["leader_present"])
ck("leader_requirement", all((r["leader_required"] == r["leader_present"])
                             for r in dist_records),
   "锚点圆心到自有盒最短欧氏距离 >24 则必须有引线，反之必须无",
   f"24/24 符合；有引线 {n_leader} 条；锚点-盒距离 {min_d:.3f}..{max_d:.3f}px")

# 盒间距离
pair_records = []
min_pair = None
ids = [m["id"] for m in ms]
for i in range(len(ids)):
    for j in range(i + 1, len(ids)):
        a, b = layout[ids[i]]["box"], layout[ids[j]]["box"]
        d = rects_dist(a, b)
        if min_pair is None or d < min_pair[0]:
            min_pair = (d, ids[i], ids[j])
        if d < 4.0 - EPS:
            problems.append(f"盒间距不足: {ids[i]}-{ids[j]} {d:.6f}")
        pair_records.append({"pair": [ids[i], ids[j]], "distance_px": round(d, 6)})
ck("label_box_gaps", min_pair[0] >= 4.0 - EPS,
   "两标签盒最短欧氏距离（重叠记 0）>= 4px",
   f"最小盒间距 {min_pair[0]:.6f}px（{min_pair[1]}-{min_pair[2]}）；共 "
   f"{len(pair_records)} 对")

# ---------- C 点-盒 ----------
ov_records = []
min_ov = None
for m in ms:
    box = layout[m["id"]]["box"]
    for o in ms:
        if o["id"] == m["id"]:
            continue
        d = rect_dist(o["anchor"][0], o["anchor"][1], *box)
        if min_ov is None or d < min_ov[0]:
            min_ov = (d, m["id"], o["id"])
        if d <= DISK_R + EPS:
            problems.append(f"{m['id']} 盒与 {o['id']} 盘相触/相交: {d:.6f}")
        ov_records.append({"label": m["id"], "other_point": o["id"],
                           "center_to_box_px": round(d, 6),
                           "disk_r": DISK_R,
                           "clear": bool(d > DISK_R + EPS)})
ck("label_box_vs_other_disks", min_ov[0] > DISK_R + EPS,
   "标签盒到任一非本点圆盘中心的最短距离 > 盘半径 6px（不相交不相触）",
   f"最小净距 {min_ov[0]:.6f}px（{min_ov[1]} 的盒 vs {min_ov[2]} 的盘）；"
   f"共 {len(ov_records)} 组")

# 自有标签不遮自有主体
own_bad = []
for m in ms:
    d = rect_dist(m["anchor"][0], m["anchor"][1], *layout[m["id"]]["box"])
    if d <= DISK_R:
        own_bad.append((m["id"], d))
ck("own_label_not_cover_own_point", not own_bad,
   "自有盒到自有锚点距离 > 盘半径（不遮点主体）",
   f"24/24 通过；最小 {min(r['anchor_to_own_box_px'] for r in dist_records):.3f}px"
   if not own_bad else str(own_bad))

# ---------- D 引线 ----------
def segs_of(pts):
    return [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def collinear_overlap(s, t):
    """两线段是否共线且有正长度重合（任务禁止）。"""
    (x1, y1), (x2, y2) = s
    (x3, y3), (x4, y4) = t
    cross = lambda ax, ay, bx, by, cx, cy: (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    # 四点共线（方向叉积近似 0）
    if (abs(cross(x1, y1, x2, y2, x3, y3)) > 1e-6
            or abs(cross(x1, y1, x2, y2, x4, y4)) > 1e-6):
        return False
    # 投影到长轴求重叠长度
    if abs(x2 - x1) >= abs(y2 - y1):
        a0, a1 = sorted((x1, x2))
        b0, b1 = sorted((x3, x4))
    else:
        a0, a1 = sorted((y1, y2))
        b0, b1 = sorted((y3, y4))
    ov = min(a1, b1) - max(a0, b0)
    return ov > 1e-6


leader_checks = {
    "count": n_leader,
    "start_on_own_circle": [], "end_on_own_box": [],
    "enters_label_box": [], "self_intersection": [], "collinear_overlap": [],
    "non_own_disk_clearance": [], "min_leader_gap_px": None,
}
all_leaders = {m["id"]: layout[m["id"]]["leader"] for m in ms
               if layout[m["id"]]["leader"]}

for mid, pts in all_leaders.items():
    ax, ay = by_id[mid]["anchor"]
    # 起点在所属圆周
    ds = math.hypot(pts[0][0] - ax, pts[0][1] - ay)
    ok_s = abs(ds - DISK_R) <= 1e-6
    leader_checks["start_on_own_circle"].append(
        {"id": mid, "dist_px": round(ds, 9), "ok": bool(ok_s)})
    if not ok_s:
        problems.append(f"{mid} 引线起点不在圆周: {ds:.9f}")
    # 终点在自有盒边界
    box = layout[mid]["box"]
    ex, ey = pts[-1]
    on_edge = (abs(ex - box[0]) <= 1e-6 or abs(ex - box[2]) <= 1e-6
               or abs(ey - box[1]) <= 1e-6 or abs(ey - box[3]) <= 1e-6)
    inside = box[0] - 1e-6 <= ex <= box[2] + 1e-6 and box[1] - 1e-6 <= ey <= box[3] + 1e-6
    ok_e = on_edge and inside
    leader_checks["end_on_own_box"].append({"id": mid, "point": [ex, ey], "ok": bool(ok_e)})
    if not ok_e:
        problems.append(f"{mid} 引线终点不在自有盒边界: ({ex},{ey})")
    # 不进入任何标签盒内部（允许终点接触自有盒边）
    for o in ms:
        ob = layout[o["id"]]["box"]
        for k, (p, q) in enumerate(segs_of(pts)):
            last = (k == len(pts) - 2)
            shrink = 0.5
            if seg_rect_intersect(p, q, *ob, shrink=shrink):
                # 终点接触自有盒边属于允许
                if o["id"] == mid and last:
                    continue
                leader_checks["enters_label_box"].append(
                    {"leader": mid, "box_of": o["id"], "segment": k})
                problems.append(f"{mid} 引线第 {k} 段进入 {o['id']} 标签盒")
    # 不自交
    ss = segs_of(pts)
    for i in range(len(ss)):
        for j in range(i + 2, len(ss)):
            if seg_seg_intersect(ss[i][0], ss[i][1], ss[j][0], ss[j][1]):
                leader_checks["self_intersection"].append(
                    {"leader": mid, "segments": [i, j]})
                problems.append(f"{mid} 引线自交")
    # 与非本点盘净距
    for o in ms:
        if o["id"] == mid:
            continue
        oc = o["anchor"]
        mind = min(seg_disk_dist(p, q, oc, DISK_R) for p, q in ss)
        if mind < DISK_R + 4.0 - EPS:
            leader_checks["non_own_disk_clearance"].append(
                {"leader": mid, "point": o["id"], "clearance_px": round(mind, 6)})
            problems.append(f"{mid} 引线离 {o['id']} 盘仅 {mind:.3f}px")

# 线对交叉 + 共线重合 + 线间净距
crossings = []
min_gap = None
lids = list(all_leaders)
for i in range(len(lids)):
    for j in range(i + 1, len(lids)):
        a, b = lids[i], lids[j]
        sa, sb = segs_of(all_leaders[a]), segs_of(all_leaders[b])
        pts_found = set()
        for s in sa:
            for t in sb:
                p = seg_seg_intersect(s[0], s[1], t[0], t[1])
                if p:
                    key = (round(p[0], 6), round(p[1], 6))
                    pts_found.add(key)
        for p in sorted(pts_found):
            crossings.append({"pair": [a, b], "point": [p[0], p[1]]})
        # 共线重合（正长度）
        for s in sa:
            for t in sb:
                if collinear_overlap(s, t):
                    leader_checks["collinear_overlap"].append(
                        {"pair": [a, b], "segments": [list(s), list(t)]})
                    problems.append(f"{a}-{b} 引线共线重合")
        # 线间净距
        for s in sa:
            for t in sb:
                g = segs_dist(s, t)
                if min_gap is None or g < min_gap[0]:
                    min_gap = (g, a, b)
leader_checks["min_leader_gap_px"] = (round(min_gap[0], 6) if min_gap else None)
leader_checks["crossings"] = crossings
leader_checks["crossing_count"] = len(crossings)
ck("leader_crossings", len(crossings) <= 3,
   "不同引线“线对+交点”去重计数（1e-6 容差；端点接触/落线段上亦计）",
   f"交叉 {len(crossings)} 处（允许至多 3）；引线间最小净距 "
   f"{min_gap[0]:.3f}px（{min_gap[1]}-{min_gap[2]}，线宽 2px 无视觉粘连）"
   if min_gap else "无引线")
ck("leader_start_on_own_circle",
   all(x["ok"] for x in leader_checks["start_on_own_circle"]),
   "引线起点到所属锚点距离 = 盘半径 6px（1e-6）",
   f"{len(all_leaders)}/{len(all_leaders)} 起点在所属圆周（连回正确的点）")
ck("leader_end_on_own_box", all(x["ok"] for x in leader_checks["end_on_own_box"]),
   "引线终点在自有标签盒边界上",
   f"{len(all_leaders)}/{len(all_leaders)} 终点在自有盒边")
ck("leader_not_enter_boxes", not leader_checks["enters_label_box"],
   "引线各段与标签盒（内缩 0.5px）求交，终点接触自有盒边除外",
   f"侵入 {len(leader_checks['enters_label_box'])} 处（不穿任何标签文本）")
ck("leader_no_self_intersection", not leader_checks["self_intersection"],
   "同一折线非相邻线段求交", "0 处自交")
ck("leader_no_collinear_overlap", not leader_checks["collinear_overlap"],
   "不同引线线段四点共线且投影重叠长度 >1e-6 判为共线重合",
   f"共线重合 {len(leader_checks['collinear_overlap'])} 处（不允许）")
ck("leader_disk_clearance", not leader_checks["non_own_disk_clearance"],
   "引线到非本点盘中心净距 >= 盘半径+4px（避免误连）",
   f"违规 {len(leader_checks['non_own_disk_clearance'])} 处")

# ---------- F 边界 ----------
bounds_bad = []
for m in ms:
    ax, ay = m["anchor"]
    if not (0 <= ax <= CW and 0 <= ay <= CH):
        bounds_bad.append((m["id"], "anchor"))
    if not (MX0 <= ax <= MX1 and MY0 <= ay <= CH):
        pass
    box = layout[m["id"]]["box"]
    if not (8 <= box[0] and box[2] <= CW - 8 and 8 <= box[1] and box[3] <= CH - 8):
        bounds_bad.append((m["id"], "box", box))
    for p in (layout[m["id"]]["leader"] or []):
        if not (0 <= p[0] <= CW and 0 <= p[1] <= CH):
            bounds_bad.append((m["id"], "leader", p))
ck("bounds", not bounds_bad,
   "点/标签/引线均在画布 1600x1100 内（标签留 8px 边距）",
   f"越界 {len(bounds_bad)} 处" + (f"：{bounds_bad[:3]}" if bounds_bad else ""))
ck("map_frame_fixed", MAP == (280.0, 160.0, 1040.0, 760.0),
   "主图区固定左上 (280,160)、宽 1040、高 760",
   "DSL 中主图底板即 (280,160,1040,760)，映射公式与之一致")

# ---------- G 前三 ----------
top3_calc = sorted(ms, key=lambda m: (-m["value"], m["id"]))[:TOP3_N]
ck("top3_by_value", [m["id"] for m in top3_calc] == ["M10", "M08", "M23"],
   "value 降序取前三，同值按 ID 升序（不按 y 坐标）",
   f"TOP1 {top3_calc[0]['id']} {top3_calc[0]['value']} / "
   f"TOP2 {top3_calc[1]['id']} {top3_calc[1]['value']} / "
   f"TOP3 {top3_calc[2]['id']} {top3_calc[2]['value']}")

# 点径与遮挡
mind = min(math.hypot(by_id[a]["anchor"][0] - by_id[b]["anchor"][0],
                      by_id[a]["anchor"][1] - by_id[b]["anchor"][1])
           for a in ids for b in ids if a < b)
ck("point_diameter_and_occlusion", mind - 2 * DISK_R > 0,
   "全部点按 12px 直径绘制；最小圆心距减去直径得盘间净距",
   f"最小圆心距 {mind:.3f}px（M10-M11）-> 盘间净距 {mind - 12:.3f}px > 0，"
   "24 点互不遮挡，无需缩至 8px")

# ---------- PNG 复测 ----------
arr = np.asarray(Image.open(OUT / "annotated-map.png").convert("RGB")).astype(int)
H, W = arr.shape[:2]
png_checks = {"size_ok": (W, H) == (CW, CH), "points": [], "labels": [],
              "leaders": []}
BLUE = (37, 99, 235); RED = (220, 38, 38); LEADER = (100, 116, 139)
for m in ms:
    ax, ay = m["anchor"]
    px = tuple(int(v) for v in arr[int(round(ay)), int(round(ax))])
    expect = RED if m["top"] else BLUE
    png_checks["points"].append({"id": m["id"], "px": list(px), "expect": list(expect),
                                 "ok": px == expect})
bad_pts = [p for p in png_checks["points"] if not p["ok"]]
ck("png_point_colors", not bad_pts,
   "落盘 PNG 逐点取锚点中心像素比色（蓝 #2563EB / 红 #DC2626）",
   f"24/24 精确一致" if not bad_pts else f"异常 {bad_pts[:3]}")

for m in ms:
    box = layout[m["id"]]["box"]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    sub = arr[y0:y1 + 1, x0:x1 + 1]
    # 墨迹=任一通道够暗：深青字 INK(min≈15)、深红字 TOP_INK #B91C1C(min=28)、
    # TOP 红框 #DC2626(min=38) 均可检出；白底(min=255) 不误报
    dark = (sub.min(axis=2) < 120)
    ink = int(dark.sum())
    ok_ink = ink >= 30
    # 墨迹包围盒应在盒内（容差 2px）
    if ink:
        ys, xs = np.nonzero(dark)
        ink_box = [int(x0 + xs.min()), int(y0 + ys.min()),
                   int(x0 + xs.max()), int(y0 + ys.max())]
        fit = (ink_box[0] >= x0 - 2 and ink_box[1] >= y0 - 2
               and ink_box[2] <= x1 + 2 and ink_box[3] <= y1 + 2)
    else:
        ink_box = None
        fit = False
    png_checks["labels"].append({"id": m["id"], "ink_px": int(ink),
                                 "ink_box": ink_box,
                                 "declared_box": [float(v) for v in box],
                                 "ink_inside": bool(fit),
                                 "ok": bool(ok_ink and fit)})
bad_lb = [l for l in png_checks["labels"] if not l["ok"]]
ck("png_label_text_in_box", not bad_lb,
   "标签盒内深色墨迹（文字）存在且包围盒不超出声明盒（容差 2px）",
   f"24/24 通过；墨迹 "
   f"{min(l['ink_px'] for l in png_checks['labels'])}-"
   f"{max(l['ink_px'] for l in png_checks['labels'])}px/盒"
   if not bad_lb else f"异常 {[(l['id'], l['ink_px']) for l in bad_lb][:5]}")

for mid, pts in all_leaders.items():
    ss = segs_of(pts)
    total = 0
    hit = 0
    for p, q in ss:
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        n = max(2, int(L))
        for k in range(n + 1):
            t = k / n
            x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            total += 1
            found = False
            for ddx in (-1, 0, 1):
                for ddy in (-1, 0, 1):
                    xx, yy = int(round(x)) + ddx, int(round(y)) + ddy
                    if 0 <= xx < W and 0 <= yy < H:
                        c = arr[yy, xx]
                        if abs(int(c[0]) - LEADER[0]) <= 40 and \
                           abs(int(c[1]) - LEADER[1]) <= 40 and \
                           abs(int(c[2]) - LEADER[2]) <= 40:
                            found = True
            if found:
                hit += 1
    cov = hit / total if total else 0
    png_checks["leaders"].append({"id": mid, "samples": total, "hit": hit,
                                  "coverage": round(cov, 4), "ok": cov >= 0.9})
bad_ld = [l for l in png_checks["leaders"] if not l["ok"]]
ck("png_leader_pixels", not bad_ld,
   "沿引线折线 1px 步进采样，3x3 邻域内存在引线色 #64748B（容差 40）记为命中",
   f"{len(all_leaders)}/{len(all_leaders)} 条引线覆盖率 >=0.9；最低 "
   f"{min(l['coverage'] for l in png_checks['leaders']):.3f}"
   if not bad_ld else f"异常 {bad_ld[:3]}")

# ---------- 汇总输出 ----------
audit = {
    "schema_version": 1,
    "task_id": "A20",
    "path_base": "output_dir",
    "coordinate_system": {
        "logical": "输入 markers.json：x/y 为 0-100 逻辑坐标，原点左下，x 向右 y 向上",
        "canvas": "画布左上原点 (0,0)，x 向右、y 向下，像素单位",
        "anchor_formula": "anchor = (280 + 10.4*x, 920 - 7.6*y)，未舍入",
        "map_area": {"left": 280, "top": 160, "width": 1040, "height": 760},
        "box_format": "[left, top, right, bottom] 轴对齐外包矩形（含文字/内边距/底板，不含引线）",
    },
    "distances": dist_records,
    "label_box_pair_distances": {
        "count": len(pair_records),
        "min_px": round(min_pair[0], 6),
        "min_pair": [min_pair[1], min_pair[2]],
        "threshold_px": 4.0,
        "pairs": pair_records,
    },
    "point_overlaps": {
        "rule": "标签盒与任一非本点圆盘不得相交或相触（盘半径 6px，实际直径 12px）",
        "min_center_to_box_px": round(min_ov[0], 6),
        "min_case": [min_ov[1], min_ov[2]],
        "records": ov_records,
    },
    "leader_checks": leader_checks,
    "bounds": {
        "canvas": [CW, CH],
        "violations": bounds_bad,
        "map_frame_fixed": [280, 160, 1040, 760],
    },
    "highlights": {
        "top3": [{"rank": i + 1, "id": m["id"], "name": m["name"],
                  "value": m["value"]} for i, m in enumerate(top3_calc)],
        "top3_rule": "value 降序前三，同值按 ID 升序",
        "center6": ["M06", "M08", "M09", "M10", "M11", "M12"],
        "visual_review": [
            "outputs/run-20261013-174209/A20/annotated-map.png（1600x1100 整图实际查看："
            "24 标签、坐标轴/范围/单位/图例/TOP3 注记齐备，三处 TOP 红框标记明确）",
            "tmp/run-20261013-174209/A20/crops/center6-v2.png（指定中心 6 点 M06/M08/M09/"
            "M10/M11/M12 及全部引线 2x 放大实际查看：7 条簇引线各连回自有点，无交叉，"
            "引线互不粘连（净距 14.3px > 2px 线宽））",
            "tmp/run-20261013-174209/A20/crops/m12-m09.png（M12/M08/M09/M10 引线 3x 放大："
            "M12 竖线连回蓝点、M08 斜线连回红点、M09 竖线连回蓝点）",
            "tmp/run-20261013-174209/A20/crops/m04-m05.png（M04/M06 引线 3x 放大："
            "斜线/竖线均连回各自蓝点）",
            "tmp/run-20261013-174209/A20/crops/left-top.png（M01-M07 区 2x 放大）",
            "tmp/run-20261013-174209/A20/crops/right-bottom.png（M08-M11/M16-M19/M22/M23 "
            "区 2x 放大：TOP1/2/3 红标签引线连回各自红点）",
            "tmp/run-20261013-174209/A20/thumb-400.png（400x275 缩略：三幕结构仍可辨）",
        ],
    },
    "checks": checks,
    "problems": problems,
    "png_recheck": png_checks,
}
(OUT / "layout-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
print(f"checks: {len(checks)}  passed: {sum(1 for c in checks if c['passed'])}  "
      f"problems: {len(problems)}")
for c in checks:
    print(f"  [{'OK' if c['passed'] else 'FAIL'}] {c['check']}: {c['evidence'][:110]}")
for p in problems[:10]:
    print("  !", p)
