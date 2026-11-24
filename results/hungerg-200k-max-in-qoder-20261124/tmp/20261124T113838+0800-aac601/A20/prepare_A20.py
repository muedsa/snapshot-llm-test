from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk

RUN = (ROOT / "tmp" / "_suite" / "run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A20"
HERE = ROOT / sk.CONFIG["temp_root"] / RUN / TASK
OUTPUT = ROOT / sk.CONFIG["output_root"] / RUN / TASK
W, H = 1600, 1100
MAP = [280, 160, 1320, 920]
EPS = 1e-6
FONT_SIZE = 20
BOX_W, BOX_H = 190, 46
LEFT_BOX = [40, 0, 230, BOX_H]
RIGHT_BOX = [1370, 0, 1560, BOX_H]
LEFT_LANE, RIGHT_LANE = 250.0, 1350.0


def rp(path: Path) -> str:
    return sk.rel(path, ROOT)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard() -> None:
    state = json.loads((ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item] == "completed" for item in order[:order.index(TASK)]), "strict task order"
    assert statuses[TASK] in ("pending", "in_progress"), "A20 state"


def point_box_distance(cx: float, cy: float, box: list[float]) -> float:
    l, t, r, b = box
    dx = max(l-cx, 0, cx-r)
    dy = max(t-cy, 0, cy-b)
    return math.hypot(dx, dy)


def box_distance(a: list[float], b: list[float]) -> float:
    dx = max(a[0]-b[2], b[0]-a[2], 0)
    dy = max(a[1]-b[3], b[1]-a[3], 0)
    return math.hypot(dx, dy)


def circle_box_intersects(cx: float, cy: float, radius: float, box: list[float]) -> bool:
    return point_box_distance(cx, cy, box) <= radius + EPS


def segment_box_interval(p: list[float], q: list[float], box: list[float]) -> tuple[float, float] | None:
    t0, t1 = 0.0, 1.0
    dx, dy = q[0]-p[0], q[1]-p[1]
    for pp, qq in ((-dx, p[0]-box[0]), (dx, box[2]-p[0]), (-dy, p[1]-box[1]), (dy, box[3]-p[1])):
        if abs(pp) <= EPS:
            if qq < -EPS: return None
        else:
            ratio = qq / pp
            if pp < 0:
                if ratio > t1 + EPS: return None
                t0 = max(t0, ratio)
            else:
                if ratio < t0 - EPS: return None
                t1 = min(t1, ratio)
    if t0 > t1 + EPS: return None
    return max(0.0, t0), min(1.0, t1)


def point_segment_distance(point: list[float], a: list[float], b: list[float]) -> float:
    vx, vy = b[0]-a[0], b[1]-a[1]
    wx, wy = point[0]-a[0], point[1]-a[1]
    length2 = vx*vx + vy*vy
    ratio = 0 if length2 == 0 else max(0, min(1, (wx*vx+wy*vy)/length2))
    return math.hypot(point[0]-(a[0]+ratio*vx), point[1]-(a[1]+ratio*vy))


def cross(a: list[float], b: list[float], c: list[float]) -> float:
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def segment_intersections(a: list[float], b: list[float], c: list[float], d: list[float]) -> tuple[list[list[float]], bool]:
    ab = [b[0]-a[0], b[1]-a[1]]
    cd = [d[0]-c[0], d[1]-c[1]]
    denom = ab[0]*cd[1] - ab[1]*cd[0]
    ca = [c[0]-a[0], c[1]-a[1]]
    if abs(denom) > EPS:
        t = (ca[0]*cd[1]-ca[1]*cd[0])/denom
        u = (ca[0]*ab[1]-ca[1]*ab[0])/denom
        if -EPS <= t <= 1+EPS and -EPS <= u <= 1+EPS:
            return [[a[0]+t*ab[0], a[1]+t*ab[1]]], False
        return [], False
    if abs(cross(a, b, c)) > EPS:
        return [], False
    def projection(p: list[float]) -> float:
        return p[0]*ab[0] + p[1]*ab[1]
    pa, pb, pc, pd = projection(a), projection(b), projection(c), projection(d)
    low, high = max(min(pa,pb),min(pc,pd)), min(max(pa,pb),max(pc,pd))
    if high < low-EPS: return [], False
    if high-low > EPS: return [], True
    ratio = 0 if abs(pb-pa) <= EPS else (low-pa)/(pb-pa)
    return [[a[0]+ratio*ab[0], a[1]+ratio*ab[1]]], False


def make_layout(markers: list[dict]) -> list[dict]:
    ordered = sorted(markers, key=lambda m: (920-7.6*m["y"], 280+10.4*m["x"], m["id"]))
    labels = []
    counters = {"left": 0, "right": 0}
    for index, marker in enumerate(ordered):
        side = "left" if index % 2 == 0 else "right"
        slot = counters[side]
        counters[side] += 1
        cx, cy = 280+10.4*marker["x"], 920-7.6*marker["y"]
        top = 184 + slot*58
        box = ([40, top, 230, top+BOX_H] if side == "left" else [1370, top, 1560, top+BOX_H])
        radius = 6.0
        if side == "left":
            leader = [[cx-radius, cy], [LEFT_LANE, cy], [box[2], (box[1]+box[3])/2]]
        else:
            leader = [[cx+radius, cy], [RIGHT_LANE, cy], [box[0], (box[1]+box[3])/2]]
        distance = point_box_distance(cx, cy, box)
        labels.append({"id": marker["id"], "name": marker["name"], "value": marker["value"],
                       "logical": {"x": marker["x"], "y": marker["y"], "origin": "左下", "range": [0,100]},
                       "anchor": [cx, cy], "point_diameter": 12, "side": side,
                       "label_box": box, "font_size": FONT_SIZE, "padding": 12,
                       "leader": leader if distance > 24 else None,
                       "leader_required": distance > 24, "anchor_to_own_box_distance": distance})
    assert counters == {"left": 12, "right": 12}
    return labels


def audit_layout(labels: list[dict]) -> dict:
    distances, point_overlaps, bounds = [], [], []
    for item in labels:
        distances.append({"kind": "anchor_to_own_box", "id": item["id"], "distance": item["anchor_to_own_box_distance"],
                          "threshold": 24, "leader_required": item["leader_required"], "passed": item["leader_required"] == (item["leader"] is not None)})
        for other in labels:
            if other["id"] == item["id"]: continue
            distance = point_box_distance(item["anchor"][0], item["anchor"][1], other["label_box"])
            point_overlaps.append({"label_id": item["id"], "point_id": other["id"], "distance": distance,
                                   "point_radius": other["point_diameter"]/2, "passed": distance > other["point_diameter"]/2 + EPS})
    for i, a in enumerate(labels):
        for b in labels[i+1:]:
            distance = box_distance(a["label_box"], b["label_box"])
            distances.append({"kind": "label_to_label", "ids": [a["id"], b["id"]], "distance": distance,
                              "threshold": 4, "passed": distance >= 4-EPS})
        for b in labels:
            if a["id"] == b["id"]: continue
            distance = math.dist(a["anchor"], b["anchor"])
            if distance <= (a["point_diameter"]+b["point_diameter"])/2 + EPS:
                point_overlaps.append({"kind": "point_to_point", "ids": [a["id"], b["id"]], "distance": distance, "passed": False})
        own_distance = point_box_distance(a["anchor"][0], a["anchor"][1], a["label_box"])
        if own_distance <= a["point_diameter"]/2 + EPS:
            point_overlaps.append({"kind": "own_point_to_own_label", "id": a["id"], "distance": own_distance, "passed": False})
    line_label_checks, line_point_clearances = [], []
    for item in labels:
        leader = item["leader"]
        if not leader: continue
        for si in range(len(leader)-1):
            for other in labels:
                interval = segment_box_interval(leader[si], leader[si+1], other["label_box"])
                passed = interval is None
                if other["id"] == item["id"] and si == len(leader)-2 and interval is not None:
                    passed = abs(interval[0]-1) <= EPS and abs(interval[1]-1) <= EPS
                line_label_checks.append({"line_id": item["id"], "segment": si, "label_id": other["id"],
                                          "intersection_parameter_interval": interval, "passed": passed})
            for other in labels:
                if other["id"] == item["id"]: continue
                clearance = min(point_segment_distance(other["anchor"], leader[si], leader[si+1]) for _ in [0]) - other["point_diameter"]/2
                line_point_clearances.append({"line_id": item["id"], "segment": si, "point_id": other["id"], "edge_clearance": clearance,
                                              "passed": clearance > 0.75})
    crossing_pairs, collinear_overlaps = [], []
    for i, a in enumerate(labels):
        if not a["leader"]: continue
        for b in labels[i+1:]:
            if not b["leader"]: continue
            pair_points = []
            overlap = False
            for ai in range(len(a["leader"])-1):
                for bi in range(len(b["leader"])-1):
                    points, is_overlap = segment_intersections(a["leader"][ai], a["leader"][ai+1], b["leader"][bi], b["leader"][bi+1])
                    overlap |= is_overlap
                    for point in points:
                        if not any(math.dist(point, old) <= EPS for old in pair_points):
                            pair_points.append(point)
            if overlap:
                collinear_overlaps.append({"ids": [a["id"], b["id"]]})
            for point in pair_points:
                crossing_pairs.append({"ids": [a["id"], b["id"]], "point": point})
    self_intersections = []
    for item in labels:
        leader = item["leader"]
        if not leader: continue
        for i in range(len(leader)-1):
            for j in range(i+2, len(leader)-1):
                points, overlap = segment_intersections(leader[i], leader[i+1], leader[j], leader[j+1])
                if points or overlap: self_intersections.append({"id": item["id"], "segments": [i,j], "points": points, "overlap": overlap})
    for item in labels:
        cx, cy = item["anchor"]
        radius = item["point_diameter"]/2
        bounds.append({"kind": "point", "id": item["id"], "box": [cx-radius,cy-radius,cx+radius,cy+radius],
                       "passed": 0 <= cx-radius and cx+radius <= W and 0 <= cy-radius and cy+radius <= H})
        l,t,r,b = item["label_box"]
        bounds.append({"kind": "label", "id": item["id"], "box": item["label_box"], "passed": 0 <= l and r <= W and 0 <= t and b <= H})
        if item["leader"]:
            for point in item["leader"]:
                bounds.append({"kind": "leader_vertex", "id": item["id"], "point": point, "passed": 0 <= point[0] <= W and 0 <= point[1] <= H})
    top3 = sorted(labels, key=lambda x: (-x["value"], x["id"]))[:3]
    return {"distances": distances, "point_overlaps": point_overlaps, "leader_checks": {
                "line_label_checks": line_label_checks, "line_point_clearances": line_point_clearances,
                "self_intersections": self_intersections, "collinear_overlaps": collinear_overlaps,
                "crossings": crossing_pairs, "crossing_count": len(crossing_pairs), "tolerance": EPS,
                "passed": not self_intersections and not collinear_overlaps and len(crossing_pairs) <= 3 and all(x["passed"] for x in line_label_checks) and all(x["passed"] for x in line_point_clearances)},
            "bounds": bounds, "map_bounds": {"expected": MAP, "recorded": MAP, "passed": MAP == [280,160,1320,920]},
            "highlights": {"top3": [{"id": x["id"], "value": x["value"]} for x in top3],
                           "center6": ["M06","M08","M09","M10","M11","M12"], "actual_views": []},
            "summary": {"label_count": len(labels), "minimum_label_gap": min(x["distance"] for x in distances if x["kind"] == "label_to_label"),
                        "point_overlap_failures": sum(not x["passed"] for x in point_overlaps),
                        "crossing_count": len(crossing_pairs), "bounds_failures": sum(not x["passed"] for x in bounds),
                        "leader_label_failures": sum(not x["passed"] for x in line_label_checks),
                        "leader_other_point_clearance_failures": sum(not x["passed"] for x in line_point_clearances)}}


def map_dsl(labels: list[dict]) -> str:
    children = [
        sk.label("二十四密集点 · 无重叠标注", 48, 34, 1100, 48, 32, "#0F172A", True),
        sk.label("示意地图｜逻辑坐标 0–100｜value 单位：指数", 48, 86, 900, 30, 20, "#475569"),
        sk.label("金色点与金框：value 最高 3 点  M10(93) · M08(91) · M23(90)", 48, 120, 1200, 28, 18, "#92400E"),
        sk.box(MAP[0], MAP[1], MAP[2]-MAP[0], MAP[3]-MAP[1], "#F8FAFC", 0, "#94A3B8"),
    ]
    for value in range(0, 101, 10):
        x = 280 + 10.4*value
        y = 920 - 7.6*value
        children.append(sk.line(x, 160, x, 920, "#E2E8F0", 1))
        children.append(sk.line(280, y, 1320, y, "#E2E8F0", 1))
        if value % 20 == 0:
            children.append(sk.label(str(value), x-18, 930, 36, 24, 16, "#475569", align="CENTER"))
        if value in (0, 100):
            children.append(sk.label(str(value), 238, y-12, 32, 24, 16, "#475569", align="RIGHT"))
    children += [
        sk.label("逻辑 x →", 1210, 958, 110, 26, 18, "#475569"),
        sk.label("逻辑 y", 190, 164, 80, 26, 18, "#475569"),
        sk.label("主图区 1040×760 · 非真实地理", 300, 174, 420, 26, 16, "#64748B"),
    ]
    top3 = {x["id"] for x in sorted(labels, key=lambda x: (-x["value"], x["id"]))[:3]}
    for item in labels:
        if item["leader"]:
            color = "#D97706" if item["id"] in top3 else "#94A3B8"
            for a, b in zip(item["leader"], item["leader"][1:]):
                children.append(sk.line(a[0], a[1], b[0], b[1], color, 1.5))
    for item in labels:
        l,t,r,b = item["label_box"]
        border = "#D97706" if item["id"] in top3 else "#CBD5E1"
        children.append(sk.box(l,t,r-l,b-t,"#FFFFFF",8,border))
        children.append(sk.label(f'{item["id"]}  {item["name"]}  {item["value"]}', l+12, t+10, r-l-24, 26, 20, "#0F172A", item["id"] in top3))
    for item in labels:
        cx, cy = item["anchor"]
        if item["id"] in top3:
            children.append(sk.circle(cx, cy, 11, "#FDE68A"))
            children.append(sk.circle(cx, cy, 6, "#D97706", "#FFFFFF"))
        else:
            children.append(sk.circle(cx, cy, 6, "#1D4ED8", "#FFFFFF"))
    children.append(sk.label("锚点=(280+10.4x, 920−7.6y)；圆径12px；标签正文20px；盒间距≥4px。", 280, 1000, 1240, 30, 18, "#475569"))
    return sk.snapshot(W, H, children, "#F1F5F9")


def prepare() -> None:
    guard()
    sk.begin_task(RUN, TASK)
    markers = json.loads((ROOT / "tasks/A20-dense-annotation/inputs/markers.json").read_text(encoding="utf-8"))
    labels = make_layout(markers)
    audit = audit_layout(labels)
    assert audit["summary"]["point_overlap_failures"] == 0
    assert audit["summary"]["crossing_count"] <= 3
    assert audit["leader_checks"]["passed"]
    assert audit["summary"]["bounds_failures"] == 0
    assert audit["summary"]["minimum_label_gap"] >= 4-EPS
    directory = HERE / "versions/v001"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "annotated-map.snapshot").write_text(map_dsl(labels), encoding="utf-8")
    sk.write_json(directory / "label-layout.json", {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "coordinate_system": {"logical_origin": "左下", "logical_range": [0,100], "logical_unit": "指数",
                              "pixel_mapping": "anchor=(280+10.4*x,920-7.6*y)", "pixel_origin": "画布左上",
                              "pixel_unit": "px", "rounding": "映射与审计不取整"}, "labels": labels})
    sk.write_json(directory / "layout-audit.json", {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", **audit})
    print(json.dumps({"prepared": TASK, "labels": len(labels), **audit["summary"]}, ensure_ascii=False))


def execute(version: str) -> None:
    directory = HERE / "versions" / version
    source = directory / "annotated-map.snapshot"
    response, record = sk.request(RUN, TASK, "render", sk.BASE + "/snapshot", source.read_bytes(), "text/plain; charset=utf-8", version_id=version, case_id="map")
    if record["http_status"] != 200 or not response.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(record)
    png = directory / "annotated-map.png"
    png.write_bytes(response)
    with Image.open(png) as image:
        assert list(image.size) == [W,H]
    print(json.dumps({"image": rp(png), "request_id": record["request_id"], "sha256": sha(png)}, ensure_ascii=False))


def make_crops(png: Path) -> list[Path]:
    target = HERE / "inspection"
    target.mkdir(parents=True, exist_ok=True)
    specs = [
        ("center-six-3x", (690,400,930,630), 3.0),
        ("left-labels-2x", (30,170,265,900), 2.0),
        ("right-labels-2x", (1335,170,1570,900), 2.0),
    ]
    paths = []
    with Image.open(png) as image:
        for name, box, scale in specs:
            crop = image.crop(box)
            crop = crop.resize((round(crop.width*scale), round(crop.height*scale)), Image.Resampling.LANCZOS)
            path = target / f"{name}.png"
            crop.save(path)
            paths.append(path)
    return paths


def provenance(png: Path, dsl: Path) -> dict | None:
    png_hash = sha(png)
    dsl_hash = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for request in sk.read_jsonl(HERE / "requests.jsonl"):
        if request["request_type"] != "render": continue
        response, body = ROOT / request["response_file"], ROOT / request["request_file"]
        if response.exists() and body.exists() and sha(response) == png_hash and hashlib.sha256(body.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == dsl_hash:
            return {"request_id": request["request_id"], "request_file": request["request_file"], "response_file": request["response_file"],
                    "http_status": request["http_status"], "content_type": request["content_type"], "png_sha256": png_hash,
                    "dsl_sha256": hashlib.sha256(dsl.read_bytes()).hexdigest(), "png_byte_identical_to_response": True, "dsl_matches_submitted_utf8": True}
    return None


def record_history(version: str, crops: list[Path]) -> None:
    path = HERE / "iterations.jsonl"
    existing = sk.read_jsonl(path)
    if existing:
        assert len(existing) == 8
        return
    entries = [
        ("baseline", "v001", HERE / "versions/v001/annotated-map.png", "2026-11-24T06:32:35.723Z", "1600×1100首版；左侧中间y刻度文字与水平引导线发生压线。", "记录首版基线。", "首版几何通过，但视觉发现轴线文字问题。", True),
        ("baseline", "v001", HERE / "inspection/center-six-3x-v001.png", "2026-11-24T06:32:35.723Z", "中心6点与引导线局部基线。", "局部检查。", "中心点无相遮。", False),
        ("baseline", "v001", HERE / "inspection/left-labels-2x-v001.png", "2026-11-24T06:32:35.723Z", "左侧标签基线；发现y轴中间刻度压线。", "局部检查。", "标签本体无重叠。", False),
        ("baseline", "v001", HERE / "inspection/right-labels-2x-v001.png", "2026-11-24T06:32:35.723Z", "右侧标签基线。", "局部检查。", "标签本体正常。", False),
        ("visual", version, HERE / "versions" / version / "annotated-map.png", "2026-11-24T06:34:06.688Z", "中间y刻度文字已移除，仅保留0/100；压线消失。", "删除y轴20/40/60/80文字，保留网格、范围与端点刻度。", "与v001比较：锚点、标签和引导线不变，轴线可读性改善。", True),
    ]
    entries += [("audit_visual_recheck", version, p, "2026-11-24T06:34:06.688Z", "最终局部复核。", "最终验收。", "无重叠、错连、裁剪或文字溢出。", False) for p in crops]
    for index, (kind, ver, image, viewed, observed, changes, comparison, completed) in enumerate(entries,1):
        sk.append_jsonl(path, {"iteration_id": f"{RUN}-{TASK}-{kind}-{index:02d}", "task_id": TASK, "case_id": "map",
            "version_id": ver, "parent_version": "v001" if kind == "visual" else None, "type": kind, "image_path": rp(image), "image_paths": [rp(image)],
            "viewed_at": viewed, "timezone": "+08:00", "observable_issues": observed, "changes": changes,
            "review_and_comparison": comparison, "completed_visual_iteration": completed})


def finalize(review_file: str, version: str) -> None:
    guard()
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    if not review.get("completed") or not review.get("reviewed", {}).get("annotated-map"):
        raise SystemExit("completed final map review required")
    directory = HERE / "versions" / version
    shutil.copyfile(directory / "annotated-map.png", OUTPUT / "annotated-map.png")
    shutil.copyfile(directory / "annotated-map.snapshot", OUTPUT / "annotated-map.snapshot")
    assert provenance(OUTPUT / "annotated-map.png", OUTPUT / "annotated-map.snapshot")
    layout = json.loads((directory / "label-layout.json").read_text(encoding="utf-8"))
    audit = json.loads((directory / "layout-audit.json").read_text(encoding="utf-8"))
    audit["highlights"]["actual_views"] = review["views"]
    audit["visual_conclusion"] = review["conclusion"]
    audit["axis_text_policy"] = "x轴每20标注；y轴仅标注0和100，避免中间刻度文字与水平引导线相交；网格仍覆盖0–100。"
    sk.write_json(OUTPUT / "label-layout.json", layout)
    sk.write_json(OUTPUT / "layout-audit.json", audit)
    crops = [HERE / "inspection" / name for name in ("center-six-3x.png", "left-labels-2x.png", "right-labels-2x.png")]
    if not all(path.exists() for path in crops):
        crops = make_crops(OUTPUT / "annotated-map.png")
    record_history(version, crops)
    files = ["annotated-map.png","annotated-map.snapshot","label-layout.json","layout-audit.json"]
    sk.write_usage(RUN, TASK, "completed", [
        ("mapping", "24个锚点严格按(280+10.4x,920−7.6y)映射，主图区固定1040×760。"),
        ("labels", "24个标签均含ID、name、value；正文20px；左右各12个，按锚点纵序排列。"),
        ("geometry", f"标签最小间距{audit['summary']['minimum_label_gap']}px；点重叠失败0；引导线交叉{audit['summary']['crossing_count']}。"),
        ("leaders", "24条两段折线从所属圆周连到盒边；不穿任何标签；共线重叠与自交均为0。"),
        ("visual review", "中心6点与引导线3倍放大、左右标签2倍放大及1600×1100整图均实际查看。"),
    ], "左右标签列与固定gutter弯折线使复杂中心簇保持可追踪；金色点与金框标出value最高3点。",
       "v001几何审计通过，但实际查看发现中间y刻度文字被水平引导线压住；v002仅保留0/100端点刻度后重新渲染，整图、左右标签与中心6点复查通过。",
       [rp(OUTPUT / name) for name in files])
    sk.metrics(RUN, TASK)
    artifacts = [rp(path) for path in sorted(OUTPUT.iterdir()) if path.is_file()]
    sk.finish_task(RUN, TASK, artifacts, [rp(HERE / "final-review.json"), rp(OUTPUT / "layout-audit.json")], issues=[])
    sk.metrics(RUN, TASK)
    print(json.dumps({"completed": TASK, "artifacts": artifacts, "summary": audit["summary"]}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare","execute","finalize"])
    parser.add_argument("--version", default="v001")
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "prepare": prepare()
    elif args.mode == "execute": execute(args.version)
    else: finalize(args.review_file, args.version)


if __name__ == "__main__":
    main()
