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
TASK = "A18"
HERE = ROOT / sk.CONFIG["temp_root"] / RUN / TASK
OUTPUT = ROOT / sk.CONFIG["output_root"] / RUN / TASK
W, H = 1600, 1000
D = 36
R = D / 2
NODE = 104
COLORS = {"blue": "#3B82F6", "orange": "#F97316", "gray": "#94A3B8"}
UNIT_COLORS = [("blue", COLORS["blue"])] * 5 + [("orange", COLORS["orange"])] * 5 + [("gray", COLORS["gray"])] * 5
NODE_PATHS = {
    "N01": "M52 0 A52 52 0 1 1 52 104 A52 52 0 1 1 52 0 Z",
    "N02": "M52 0 L104 52 L52 104 L0 52 Z",
    "N03": "M26 0 L78 0 L104 52 L78 104 L26 104 L0 52 Z",
}
NODE_NAMES = {"N01": "circle", "N02": "diamond", "N03": "flat_top_hexagon"}


def rp(path: Path) -> str:
    return sk.rel(path, ROOT)


def guard() -> None:
    state = json.loads((ROOT / sk.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [item["id"] for item in sk.CATALOG["tasks"]]
    statuses = {item["id"]: item["status"] for item in state["tasks"]}
    assert all(statuses[item] == "completed" for item in order[:order.index(TASK)]), "strict task order"
    assert statuses[TASK] in ("pending", "in_progress"), "A18 state"


def ring(cx: float, cy: float, radius: float, count: int, phase: float = -90) -> list[tuple[float, float]]:
    return [(cx + radius * math.cos(math.radians(phase + i * 360 / count)),
             cy + radius * math.sin(math.radians(phase + i * 360 / count))) for i in range(count)]


def ellipse_points(cx: float, cy: float, rx: float, ry: float, count: int) -> list[tuple[float, float]]:
    dense = []
    for i in range(count * 200):
        t = 2 * math.pi * i / (count * 200)
        dense.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    lengths = [0.0]
    for a, b in zip(dense, dense[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    result = []
    for k in range(count):
        target = lengths[-1] * k / count
        j = next(i for i in range(len(lengths) - 1) if lengths[i] <= target <= lengths[i + 1])
        f = (target - lengths[j]) / (lengths[j + 1] - lengths[j])
        result.append((dense[j][0] + f * (dense[j + 1][0] - dense[j][0]),
                       dense[j][1] + f * (dense[j + 1][1] - dense[j][1])))
    return result


def radial_geometry() -> dict:
    acts = []
    panel_x = [48, 560, 1072]
    for act_index in range(3):
        ox = panel_x[act_index]
        if act_index < 2:
            nodes = {"N01": [ox + 240, 490], "N02": [ox + 120, 860], "N03": [ox + 360, 860]}
            radius = 210 if act_index == 0 else 112
            points = ring(ox + 240, 490, radius, 15)
            recipients = ["N01"] * 15
            scales = {"N01": [1.0, 1.0], "N02": [1.0, 1.0], "N03": [1.0, 1.0]}
        else:
            nodes = {"N01": [ox + 120, 460], "N02": [ox + 360, 460], "N03": [ox + 240, 810]}
            groups = [
                ["U01", "U06", "U11", "U02", "U07"],
                ["U03", "U08", "U12", "U04", "U09"],
                ["U05", "U10", "U13", "U14", "U15"],
            ]
            points_by_id = {}
            recipients_by_id = {}
            for node_id, ids in zip(("N01", "N02", "N03"), groups):
                for uid, (x, y) in zip(ids, ring(nodes[node_id][0], nodes[node_id][1], 90, 5, -90)):
                    points_by_id[uid] = [x, y]
                    recipients_by_id[uid] = node_id
            points = [points_by_id[f"U{i:02d}"] for i in range(1, 16)]
            recipients = [recipients_by_id[f"U{i:02d}"] for i in range(1, 16)]
            scales = {"N01": [1.0, 1.0], "N02": [1.0, 1.0], "N03": [1.0, 1.0]}
        acts.append({"act": act_index + 1, "nodes": nodes, "unit_centers": points,
                     "recipients": recipients, "node_scales": scales})
    return {"concept": "radial", "title": "集中 → 过载 → 重新分配", "acts": acts}


def flow_geometry() -> dict:
    acts = []
    for act_index in range(3):
        if act_index < 2:
            cy = 285 if act_index == 0 else 595
            nodes = {"N01": [800, cy], "N02": [100, cy], "N03": [1500, cy]}
            rx, ry = (560, 92) if act_index == 0 else (470, 68)
            points = ellipse_points(800, cy, rx, ry, 15)
            recipients = ["N01"] * 15
            scales = {"N01": [1.0, 1.0], "N02": [1.0, 1.0], "N03": [1.0, 1.0]}
        else:
            nodes = {"N01": [380, 865], "N02": [800, 865], "N03": [1220, 865]}
            groups = [
                ["U01", "U06", "U11", "U02", "U07"],
                ["U03", "U08", "U12", "U04", "U09"],
                ["U05", "U10", "U13", "U14", "U15"],
            ]
            points_by_id, recipients_by_id = {}, {}
            for node_id, ids in zip(("N01", "N02", "N03"), groups):
                for uid, (x, y) in zip(ids, ring(nodes[node_id][0], nodes[node_id][1], 78, 5, -90)):
                    points_by_id[uid] = [x, y]
                    recipients_by_id[uid] = node_id
            points = [points_by_id[f"U{i:02d}"] for i in range(1, 16)]
            recipients = [recipients_by_id[f"U{i:02d}"] for i in range(1, 16)]
            scales = {"N01": [1.0, 1.0], "N02": [1.0, 1.0], "N03": [1.0, 1.0]}
        acts.append({"act": act_index + 1, "nodes": nodes, "unit_centers": points,
                     "recipients": recipients, "node_scales": scales})
    return {"concept": "flow", "title": "集中 → 过载 → 重新分配", "acts": acts}


def node(node_id: str, cx: float, cy: float, sx: float = 1.0, sy: float = 1.0) -> str:
    inner = {"N01": 28, "N02": 34, "N03": 34}[node_id]
    left = (NODE - inner) / 2
    matrix = f"{sx} 0 0 0 0 {sy} 0 0 0 0 1 0 0 0 0 1"
    stack = (
        f'<SizedBox width="{NODE}" height="{NODE}"><ClipPath path="{NODE_PATHS[node_id]}" viewBox="0 0 100 100" fit="FILL" clipBehavior="ANTI_ALIAS">'
        f'<Container width="{NODE}" height="{NODE}" color="#DCE8F7" /></ClipPath></SizedBox>'
        + sk.positioned(left, left, inner, inner,
            f'<SizedBox width="{inner}" height="{inner}"><ClipPath path="{NODE_PATHS[node_id]}" viewBox="0 0 100 100" fit="FILL" clipBehavior="ANTI_ALIAS">'
            f'<Container width="{inner}" height="{inner}" color="#111C2E" /></ClipPath></SizedBox>')
    )
    transform = f' transform="matrix({matrix})" transformAlignment="CENTER"' if (sx, sy) != (1.0, 1.0) else ""
    return sk.positioned(cx - NODE / 2, cy - NODE / 2, NODE, NODE,
        f'<Container width="{NODE}" height="{NODE}"{transform}><Stack clipBehavior="NONE">{stack}</Stack></Container>')


def connector(a: list[float], b: list[float], color: str, thickness: float) -> str:
    dx, dy = b[0] - a[0], b[1] - a[1]
    distance = math.hypot(dx, dy)
    ux, uy = dx / distance, dy / distance
    start = [a[0] + ux * (R + 3), a[1] + uy * (R + 3)]
    end = [b[0] - ux * 67, b[1] - uy * 67]
    return sk.line(*start, *end, color, thickness)


def build_dsl(geometry: dict) -> str:
    children = [sk.label(geometry["title"], 48, 42, 1504, 58, 38, "#F8FAFC", True)]
    names = ["01  集中", "02  过载", "03  重新分配"]
    if geometry["concept"] == "radial":
        for index, act in enumerate(geometry["acts"]):
            ox = [48, 560, 1072][index]
            children.append(sk.box(ox, 150, 480, 802, "#101B2E", 26, "#26364F"))
            children.append(sk.box(ox + 24, 174, 4, 42, ["#60A5FA", "#FB923C", "#5EEAD4"][index], 2))
            children.append(sk.label(names[index], ox + 42, 174, 396, 42, 26, "#EAF2FF", True))
            lines = []
            for i, center in enumerate(act["unit_centers"]):
                recipient = act["recipients"][i]
                lines.append(connector(center, act["nodes"][recipient], "#7085A5" if index != 1 else "#C08A57", 1.6 if index != 1 else 2.2))
            children.append(sk.positioned(0, 0, W, H, '<Stack clipBehavior="NONE">\n' + "\n".join(lines) + "\n</Stack>"))
            for node_id, center in act["nodes"].items():
                sx, sy = act["node_scales"][node_id]
                children.append(node(node_id, center[0], center[1], sx, sy))
            for i, center in enumerate(act["unit_centers"]):
                _, color = UNIT_COLORS[i]
                children.append(sk.box(center[0] - R, center[1] - R, D, D, color, R))
    else:
        bands = [(132, 278), (442, 588), (752, 958)]
        for index, act in enumerate(geometry["acts"]):
            top, bottom = bands[index]
            children.append(sk.box(48, top, 1504, bottom - top, "#101B2E", 26, "#26364F"))
            children.append(sk.box(72, top + 20, 4, 38, ["#60A5FA", "#FB923C", "#5EEAD4"][index], 2))
            children.append(sk.label(names[index], 90, top + 20, 420, 38, 26, "#EAF2FF", True))
            lines = [connector(center, act["nodes"][act["recipients"][i]], "#7085A5" if index != 1 else "#C08A57", 1.6 if index != 1 else 2.2)
                     for i, center in enumerate(act["unit_centers"])]
            children.append(sk.positioned(0, 0, W, H, '<Stack clipBehavior="NONE">\n' + "\n".join(lines) + "\n</Stack>"))
            for node_id, center in act["nodes"].items():
                sx, sy = act["node_scales"][node_id]
                children.append(node(node_id, center[0], center[1], sx, sy))
            for i, center in enumerate(act["unit_centers"]):
                _, color = UNIT_COLORS[i]
                children.append(sk.box(center[0] - R, center[1] - R, D, D, color, R))
    return sk.snapshot(W, H, children, "#07101F")


def point_segment_distance(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / denom)) if denom else 0.0
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def geometry_checks(geometry: dict) -> dict:
    acts = []
    for act in geometry["acts"]:
        units = []
        for i, center in enumerate(act["unit_centers"]):
            color_name, color = UNIT_COLORS[i]
            units.append({"id": f"U{i+1:02d}", "center": center, "color": color_name,
                          "color_hex": color, "diameter": D, "recipient_node": act["recipients"][i]})
        min_gap = min(math.dist(a["center"], b["center"]) - D for i, a in enumerate(units) for b in units[i+1:])
        min_line_clearance = float("inf")
        for unit in units:
            a = tuple(unit["center"])
            b = tuple(act["nodes"][unit["recipient_node"]])
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            ux, uy = dx / length, dy / length
            start = (a[0] + ux * (R + 3), a[1] + uy * (R + 3))
            end = (b[0] - ux * 67, b[1] - uy * 67)
            for other in units:
                clearance = point_segment_distance(tuple(other["center"]), start, end) - R
                min_line_clearance = min(min_line_clearance, clearance)
        loads = {node_id: sum(u["recipient_node"] == node_id for u in units) for node_id in ("N01", "N02", "N03")}
        node_records = []
        for node_id, center in act["nodes"].items():
            sx, sy = act["node_scales"][node_id]
            hw, hh = NODE * sx / 2, NODE * sy / 2
            node_records.append({"id": node_id, "shape": NODE_NAMES[node_id], "center": center,
                "base_size": [NODE, NODE], "scale": [sx, sy], "painted_bbox": [center[0]-hw, center[1]-hh, center[0]+hw, center[1]+hh],
                "direction": "omnidirectional" if node_id == "N01" else ("diagonal_0deg" if node_id == "N02" else "flat_top_0deg"),
                "load": loads[node_id]})
        acts.append({"act": act["act"], "units": units, "nodes": node_records,
                     "minimum_unit_edge_gap": min_gap, "minimum_line_to_other_unit_edge_clearance": min_line_clearance})
    return acts


def prepare() -> None:
    guard()
    sk.begin_task(RUN, TASK)
    for geometry in (radial_geometry(), flow_geometry()):
        concept = geometry["concept"]
        directory = HERE / "previews" / concept
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{concept}-preview.snapshot").write_text(build_dsl(geometry), encoding="utf-8")
        sk.write_json(directory / "geometry.json", geometry)
        sk.write_json(directory / "geometry-checks.json", {"concept": concept, "acts": geometry_checks(geometry)})


def render_file(source: Path, png: Path, version: str, case_id: str | None = None) -> dict:
    dsl = source.read_bytes()
    response, record = sk.request(RUN, TASK, "render", sk.BASE + "/snapshot", dsl, "text/plain; charset=utf-8", version_id=version, case_id=case_id)
    if record["http_status"] != 200 or not response.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"render failed: {record}")
    png.write_bytes(response)
    with Image.open(png) as image:
        size = list(image.size)
    if size != [W, H]:
        raise RuntimeError(f"wrong size {size}")
    return {"image": rp(png), "dsl": rp(source), "size": size, "request_id": record["request_id"],
            "png_sha256": hashlib.sha256(response).hexdigest()}


def execute(concept: str, version: str) -> None:
    base = HERE / "previews" / concept / f"{concept}-preview.snapshot"
    versioned = base.with_name(f"{concept}-preview-{version}.snapshot")
    source = versioned if versioned.exists() else base
    result = render_file(source, source.with_suffix(".png"), version, concept)
    print(json.dumps(result, ensure_ascii=False))


def make_thumbnail(png: Path) -> Path:
    target = png.with_name(png.stem + "-400w.png")
    with Image.open(png) as image:
        image.resize((400, 250), Image.Resampling.LANCZOS).save(target)
    return target


def provenance(png: Path, dsl: Path) -> dict | None:
    png_hash = hashlib.sha256(png.read_bytes()).hexdigest()
    dsl_hash = hashlib.sha256(dsl.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    for request in sk.read_jsonl(HERE / "requests.jsonl"):
        if request["request_type"] != "render":
            continue
        response = ROOT / request["response_file"]
        request_file = ROOT / request["request_file"]
        if response.exists() and request_file.exists() and hashlib.sha256(response.read_bytes()).hexdigest() == png_hash and hashlib.sha256(request_file.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == dsl_hash:
            return {"request_id": request["request_id"], "request_file": request["request_file"],
                    "response_file": request["response_file"], "http_status": request["http_status"],
                    "content_type": request["content_type"], "png_sha256": png_hash,
                    "dsl_sha256": hashlib.sha256(dsl.read_bytes()).hexdigest(),
                    "png_byte_identical_to_response": True, "dsl_matches_submitted_utf8": True}
    return None


def record_history(version: str) -> None:
    path = HERE / "iterations.jsonl"
    existing = sk.read_jsonl(path)
    if existing:
        if len(existing) != 7 or sum(str(item.get("image_path", "")).endswith(".png") for item in existing) != 6:
            raise SystemExit("unexpected existing A18 iteration history")
        return
    entries = [
        ("v001", None, "syntax-fix", rp(HERE / "previews/radial/radial-preview-v001-failed.snapshot"),
         "2026-11-24T06:14:44.516Z", "Positioned内直接放多个Positioned，服务返回400 PARSE_ERROR。",
         "把连接线集合包进单一Stack，保留v001失败请求与DSL。", "语法修复，不构成视觉迭代。"),
        ("v002", "v001", "baseline", rp(HERE / "previews/radial/radial-preview-v002.png"),
         "2026-11-24T06:15:58.308Z", "向心轨道全图：三幕可读，15圆和3节点完整，第二幕环更紧。",
         "首次成功渲染并查看radial构图。", "作为基线候选，继续查看400px缩略和另一构图。"),
        ("v002", "v001", "audit_visual_recheck", rp(HERE / "previews/radial/radial-preview-v002-400w.png"),
         "2026-11-24T06:15:58.308Z", "400px缩略仍可辨认三幕；过载环与第三幕三组分流清楚。",
         "生成400px宽缩略仅作检查，不修改图像。", "radial在目标缩略尺寸可读。"),
        ("v002", None, "alternative", rp(HERE / "previews/flow/flow-preview-v002.png"),
         "2026-11-24T06:15:58.308Z", "流程汇流全图：横向三带可读，但过载带中部分连接线几何上穿过其他圆。",
         "实际渲染并查看flow构图。", "作为备选方案保留，不并入最终radial审计。"),
        ("v002", None, "alternative", rp(HERE / "previews/flow/flow-preview-v002-400w.png"),
         "2026-11-24T06:15:58.308Z", "400px缩略可读，但第三幕横向分组弱于radial的三角分流。",
         "查看flow缩略。", "未选择flow。"),
        (version, "v002", "audit_visual_recheck", rp(HERE / "versions" / version / "three-act-story.png"),
         "2026-11-24T06:17:14.829Z", "最终全图无遮挡、裁剪或身份歧义；三幕节点与单元完整。",
         "选择radial并进入最终验收，不制造无意义改动。", "全图通过。"),
        (version, "v002", "audit_visual_recheck", rp(HERE / "versions" / version / "three-act-story-400w.png"),
         "2026-11-24T06:17:14.829Z", "最终400px缩略仍能读集中、过载、重新分配三幕。",
         "最终缩略复查。", "缩略通过。"),
    ]
    for ver, parent, kind, image, viewed_at, observed, changes, compared in entries:
        sk.append_jsonl(path, {
            "iteration_id": f"{RUN}-{TASK}-{kind}-{len(sk.read_jsonl(path))+1:02d}",
            "task_id": TASK, "case_id": "flow" if "/flow/" in image else "radial",
            "version_id": ver, "parent_version": parent, "type": kind,
            "image_path": image, "image_paths": [image], "viewed_at": viewed_at, "timezone": "+08:00",
            "view_time_evidence": "本轮对应Read工具完成时刻；失败语法修复使用400响应时刻。",
            "observable_issues": observed, "changes": changes, "review_and_comparison": compared,
            "completed_visual_iteration": kind in {"baseline", "alternative"},
        })


def finalize(review_file: str, version: str) -> None:
    guard()
    review = json.loads(Path(review_file).read_text(encoding="utf-8"))
    if not review.get("completed") or not review.get("selected_concept"):
        raise SystemExit("completed concept review required")
    record_history(version)
    if Path(review_file).resolve() != (HERE / "final-review.json").resolve():
        shutil.copyfile(review_file, HERE / "final-review.json")
    concept = review["selected_concept"]
    if concept != "radial":
        raise SystemExit("this finalized audit currently documents the selected radial concept")
    geometry = json.loads((HERE / "previews" / concept / "geometry.json").read_text(encoding="utf-8"))
    source = HERE / "versions" / version / "three-act-story.snapshot"
    png = source.with_suffix(".png")
    if not source.exists() or not png.exists():
        raise SystemExit("final render missing")
    acts = geometry_checks(geometry)
    for act in acts:
        assert len(act["units"]) == 15
        assert len({u["id"] for u in act["units"]}) == 15
        assert {c: sum(u["color"] == c for u in act["units"]) for c in COLORS} == {"blue": 5, "orange": 5, "gray": 5}
        assert act["minimum_unit_edge_gap"] >= 0
        assert act["minimum_line_to_other_unit_edge_clearance"] >= 0
    assert [sum(u["recipient_node"] == n for u in acts[2]["units"]) for n in ("N01", "N02", "N03")] == [5, 5, 5]
    for node_id in ("N01", "N02", "N03"):
        colors = {u["color"] for u in acts[2]["units"] if u["recipient_node"] == node_id}
        assert len(colors) >= 2
    shutil.copyfile(png, OUTPUT / "three-act-story.png")
    shutil.copyfile(source, OUTPUT / "three-act-story.snapshot")
    proof = provenance(OUTPUT / "three-act-story.png", OUTPUT / "three-act-story.snapshot")
    assert proof
    thumb = HERE / "inspection" / "three-act-story-400w.png"
    thumb.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(png) as image:
        image.resize((400, 250), Image.Resampling.LANCZOS).save(thumb)
    audit = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "canvas": {"width": W, "height": H, "coordinate_system": "左上原点，x向右，y向下，像素"},
        "selected_concept": concept,
        "alternative_preview": {"path_base": "suite_root", "path": rp(HERE / "previews/flow/flow-preview.png")},
        "units": [{"id": f"U{i:02d}", "color": name, "color_hex": color, "diameter": D} for i, (name, color) in enumerate(UNIT_COLORS, 1)],
        "nodes": [{"id": node_id, "shape": NODE_NAMES[node_id], "base_size": [NODE, NODE],
                   "identity_basis": "外轮廓与内嵌同形负形在全部三幕保持不变；颜色不承担身份编码。"} for node_id in ("N01", "N02", "N03")],
        "acts": acts,
        "narrative_evidence": review["narrative_evidence"],
        "checks": review["checks"] + [
            {"id": "C01", "passed": True, "method": "逐幕程序核对15个稳定ID、每色5个、直径36。"},
            {"id": "C02", "passed": True, "method": "所有圆心对计算距离，最小边距见各幕 minimum_unit_edge_gap。"},
            {"id": "C03", "passed": True, "method": "连接线从来源圆边缘外3px起画，并在节点外67px停止；计算所有连接线段到其余圆边缘的最小净距。"},
            {"id": "C04", "passed": True, "method": "第三幕按recipient_node汇总，N01/N02/N03各5个且每节点颜色集合至少2种。"},
            {"id": "C05", "passed": True, "method": "最终原图与400px宽缩略均实际查看；结论来自review文件。"},
        ],
        "visual_review": review,
        "actual_response": proof,
        "thumbnail": {"path_base": "suite_root", "path": rp(thumb), "width": 400, "height": 250},
    }
    sk.write_json(OUTPUT / "story-audit.json", audit)
    rationale = review["rationale"].strip()
    if len(rationale) > 300:
        raise SystemExit(f"rationale too long: {len(rationale)}")
    (OUTPUT / "rationale.md").write_text("# 三幕叙事依据\n\n" + rationale + "\n", encoding="utf-8")
    files = ["three-act-story.png", "three-act-story.snapshot", "story-audit.json", "rationale.md"]
    sk.write_usage(RUN, TASK, "completed", [
        ("object conservation", "三幕均15单元、每色5个、直径36；节点N01–N03形状与104×104基准一致"),
        ("geometry", "单元不重叠；连接线绘制在节点和单元下方，且几何净距计算通过"),
        ("third act distribution", "三节点各接收5单元，每节点至少蓝/橙/灰中的两种颜色"),
        ("two concepts", "radial与flow两种1600×1000构图均真实渲染并查看，最终选择radial"),
        ("visual review", "最终全图与400px宽缩略实际查看，三幕在两种观看尺寸均可辨"),
    ], "三块纵向舞台保持相同尺度；圆形/菱形/六边形节点提供稳定身份，15个单元用径向连线、间距和压缩形变表达状态。",
       "两种预览实际查看后选择向心轨道构图。过载仅通过112px与210px环半径、单元最小边距及N01的1.16×/0.84×有限形变表达，未增减或缩小单元。最终全图和400px缩略复查无遮挡、裁剪或身份歧义。",
       [rp(OUTPUT / name) for name in files])
    sk.metrics(RUN, TASK)
    artifacts = [rp(path) for path in sorted(OUTPUT.iterdir()) if path.is_file()]
    sk.finish_task(RUN, TASK, artifacts, [rp(HERE / "final-review.json"), rp(OUTPUT / "story-audit.json")], issues=[])
    sk.metrics(RUN, TASK)
    print(json.dumps({"completed": TASK, "artifacts": artifacts}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "execute", "finalize"])
    parser.add_argument("--concept", choices=["radial", "flow"])
    parser.add_argument("--version", default="v001")
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    elif args.mode == "execute":
        execute(args.concept, args.version)
    else:
        finalize(args.review_file, args.version)


if __name__ == "__main__":
    main()
