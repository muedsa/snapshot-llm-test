from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as s  # noqa: E402

RUN_ID = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
OUTPUT, TEMP = s.task_dirs(RUN_ID, HERE.name)
TASK = HERE.name
FONT = s.FONT


def safe_label(value, x, y, width, height, size=20, color="#172033", bold=False, align="LEFT"):
    # Parser Text has no width/align attribute; Positioned supplies finite constraints.
    return s.positioned(x, y, width, height, s.text(value, size, color, bold, align))


s.label = safe_label


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jwrite(path: Path, value) -> None:
    s.write_json(path, value)


def next_version(unit: str) -> str:
    used = {p.stem for p in (TEMP / "candidates").glob(f"{unit}-v*.json")}
    number = 1
    while f"{unit}-v{number:03d}" in used:
        number += 1
    return f"{unit}-v{number:03d}"


def static_dsl(dsl: str, width: int, height: int) -> dict:
    root = ET.fromstring(dsl)
    assert root.tag == "Snapshot" and root.get("type") == "png"
    box = root.find("./Container/Stack")
    assert box is not None
    texts = list(root.iter("Text"))
    for node in texts:
        assert node.get("fontFamily") == FONT
        assert float(node.get("fontSize", "0")) > 0
        assert node.get("width") is None and node.get("align") is None, "Text width/align are not Parser attributes"
    boxes = []
    for node in root.iter("Positioned"):
        labels = list(node.iter("Text"))
        if not labels:
            continue
        x, y, w, h = (float(node.get("left", "0")), float(node.get("top", "0")),
                      float(node.get("width", "0")), float(node.get("height", "0")))
        assert 0 <= x and 0 <= y and x + w <= width and y + h <= height, ("text bounds", x, y, w, h)
        boxes.append((x, y, x + w, y + h, " | ".join(n.text or "" for n in labels)))
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert min(a[2], b[2]) - max(a[0], b[0]) <= 0.5 or min(a[3], b[3]) - max(a[1], b[1]) <= 0.5, \
                ("text box overlap", a[4], b[4])
    return {"width": width, "height": height, "text_nodes": len(texts), "text_boxes": len(boxes),
            "text_box_overlaps": 0, "xml_valid": True}


def png_check(path: Path, width: int, height: int, mode: str | None = None, transparent: bool = False) -> dict:
    from PIL import Image
    with Image.open(path) as image:
        image.load()
        assert image.format == "PNG", image.format
        assert image.size == (width, height), image.size
        if mode:
            assert image.mode == mode, image.mode
        result = {"format": image.format, "size": list(image.size), "mode": image.mode, "sha256": sha(path)}
        if transparent:
            assert "A" in image.mode, image.mode
            alpha = image.getchannel("A")
            lo, hi = alpha.getextrema()
            assert lo == 0 and hi == 255, (lo, hi)
            corners = [image.getpixel(p)[-1] for p in [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]]
            assert corners == [0, 0, 0, 0], corners
            result.update(alpha_extrema=[lo, hi], transparent_corners=corners)
        elif image.mode == "RGBA":
            assert image.getchannel("A").getextrema() == (255, 255)
        return result


def prepare(task_module, units: list[dict]) -> None:
    built = task_module.build_all()
    report = {"task_id": TASK, "run_id": RUN_ID, "path_base": "suite_root", "offline_only": True,
              "http_requests": 0, "suite_state_changes": 0, "final_output_writes": 0, "units": []}
    number = 1
    while (TEMP / f"preparation-{number:03d}.json").exists():
        number += 1
    destination = TEMP / f"preparation-{number:03d}"
    for unit in units:
        item = built[unit["id"]]
        dsl = item["dsl"]
        check = static_dsl(dsl, unit["width"], unit["height"])
        task_module.validate_static(unit["id"], item)
        path = destination / f'{unit["id"]}.snapshot'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dsl, encoding="utf-8")
        report["units"].append({"id": unit["id"], **check, "dsl": s.rel(path), "sha256": sha(path)})
    jwrite(TEMP / f"preparation-{number:03d}.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def execution_guard() -> None:
    state_path = OUTPUT.parent / "_suite/suite-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    order = [t["id"] for t in s.CATALOG["tasks"]]
    current = next(t for t in state["tasks"] if t["id"] == TASK)
    unfinished = [t["id"] for t in state["tasks"] if t["id"] in order[:order.index(TASK)] and t["status"] != "completed"]
    assert not unfinished, f"strict task order incomplete: {unfinished}"
    assert current["status"] == "in_progress", f'{TASK} must be in_progress, not {current["status"]}'


def begin() -> None:
    state_path = OUTPUT.parent / "_suite/suite-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    current = next(t for t in state["tasks"] if t["id"] == TASK)
    order = [t["id"] for t in s.CATALOG["tasks"]]
    earlier = order[:order.index(TASK)]
    unfinished = [t["id"] for t in state["tasks"] if t["id"] in earlier and t["status"] != "completed"]
    assert not unfinished, f"strict task order incomplete: {unfinished}"
    assert current["status"] == "pending", f'{TASK} is {current["status"]}; use existing checkpoint rather than restarting'
    s.begin_task(RUN_ID, TASK)


def render(task_module, unit_id: str, kind: str) -> Path:
    units = {u["id"]: u for u in task_module.UNITS}
    unit = units[unit_id]
    item = task_module.build_all()[unit_id]
    version = next_version(unit_id)
    image, record = s.render(RUN_ID, TASK, item["dsl"], unit_id, version, final=False, kind=kind, case_id=unit["case"])
    png_check(image, unit["width"], unit["height"], transparent=unit.get("transparent", False))
    dsl_path = TEMP / "versions" / version / f"{unit_id}.snapshot"
    manifest = {"task_id": TASK, "unit_id": unit_id, "case_id": unit["case"], "version_id": version,
                "image_path": s.rel(image), "dsl_path": s.rel(dsl_path), "sha256": sha(image),
                "request_id": record["request_id"], "rendered_at": s.iso(), "review": None}
    jwrite(TEMP / "candidates" / f"{version}.json", manifest)
    s.record_iteration(RUN_ID, TASK, version, image, kind, "待视觉检查：已取得服务PNG，尚未打开最终实际图片。",
                       "按生成器创建首版；等待逐图视觉检查。", "尚未进行视觉比较。", completed=False, case_id=unit["case"])
    print(image)
    return image


def review(unit_id: str, version: str, result: str, observation: str) -> None:
    path = TEMP / "candidates" / f"{version}.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["unit_id"] == unit_id
    assert result in {"pass", "fail"}
    assert observation.strip()
    review_path = TEMP / "reviews" / f"{version}.json"
    assert not review_path.exists(), "review evidence is immutable; render a new version to review again"
    value = {"viewed_at": s.iso(), "viewer": "HungerG", "visual_tool": "Read", "result": result,
             "observation": observation, "image_sha256": manifest["sha256"]}
    # Keep the render manifest immutable; visual reviews are separate append-only evidence.
    jwrite(TEMP / "reviews" / f"{version}.json", value)
    image = ROOT / manifest["image_path"]
    s.record_iteration(RUN_ID, TASK, version, image,
                       "baseline" if TASK in {"A23", "A24"} or manifest["case_id"] == "round-01" else "requirement-change",
                       observation, "实际查看后记录；通过则进入晋升，失败则保留候选并生成新版本。",
                       "依据当前PNG与需求逐项核对。", completed=result == "pass", case_id=manifest["case_id"])


def promote(task_module, unit_id: str, version: str | None = None) -> Path:
    units = {u["id"]: u for u in task_module.UNITS}
    unit = units[unit_id]
    if version is None:
        candidates = [json.loads(p.read_text(encoding="utf-8")) for p in (TEMP / "candidates").glob(f"{unit_id}-v*.json")]
        passed = []
        for candidate in candidates:
            review_path = TEMP / "reviews" / f'{candidate["version_id"]}.json'
            if review_path.exists():
                candidate["review"] = json.loads(review_path.read_text(encoding="utf-8"))
                if candidate["review"]["result"] == "pass":
                    passed.append(candidate)
        assert passed, f"no visually passed candidate for {unit_id}"
        manifest = max(passed, key=lambda c: c["version_id"])
    else:
        manifest = json.loads((TEMP / "candidates" / f"{version}.json").read_text(encoding="utf-8"))
        manifest["review"] = json.loads((TEMP / "reviews" / f"{version}.json").read_text(encoding="utf-8"))
    assert manifest["review"]["result"] == "pass", "visual review pass required"
    source = ROOT / manifest["image_path"]
    dsl_source = ROOT / manifest["dsl_path"]
    assert sha(source) == manifest["sha256"] == manifest["review"]["image_sha256"]
    png_check(source, unit["width"], unit["height"], transparent=unit.get("transparent", False))
    item = task_module.build_all()[unit_id]
    static_dsl(item["dsl"], unit["width"], unit["height"])
    assert sha(dsl_source) == sha_string(item["dsl"]), "candidate DSL differs from current generator"
    task_module.validate_static(unit_id, item)
    target = OUTPUT / unit["output"]
    unit_scope = f'{unit["case"]}/' if unit["case"].startswith("round-") else ""
    target.parent.mkdir(parents=True, exist_ok=True)
    final_meta = OUTPUT / unit_scope / "final-image-manifest.json"
    if final_meta.exists():
        records = json.loads(final_meta.read_text(encoding="utf-8")).get("images", [])
    else:
        records = []
    assert not any(x["output"] == unit["output"] for x in records), f"final already promoted: {unit['output']}"
    if target.exists():
        assert sha(target) == sha(source), f"refusing to overwrite different final: {target}"
    else:
        shutil.copyfile(source, target)
    dsl_target = target.with_suffix(".snapshot")
    if dsl_target.exists():
        assert sha(dsl_target) == sha(dsl_source), f"refusing to overwrite different DSL: {dsl_target}"
    else:
        shutil.copyfile(dsl_source, dsl_target)
    records.append({"output": unit["output"], "dsl": unit["output"].replace(".png", ".snapshot"),
                    "sha256": sha(source), "dsl_sha256": sha(dsl_source), "version_id": manifest["version_id"],
                    "request_id": manifest["request_id"], "review": manifest["review"]})
    jwrite(final_meta, {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "images": records})
    s.append_jsonl(TEMP / "promotions.jsonl", {"at": s.iso(), "unit_id": unit_id, "version_id": manifest["version_id"],
                                               "output": unit["output"], "sha256": sha(source), "review": manifest["review"]})
    return target


def sha_string(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def round_metrics(case_id: str) -> dict:
    requests = s.read_jsonl(TEMP / "requests.jsonl")
    iterations = s.read_jsonl(TEMP / "iterations.jsonl")
    if case_id != "all":
        requests = [x for x in requests if x.get("case_id") == case_id]
        iterations = [x for x in iterations if x.get("case_id") == case_id]
    renders = [r for r in requests if r["request_type"] == "render"]
    start = min((r["started_at"] for r in requests), default=None)
    end = max((r["ended_at"] for r in requests), default=None)
    elapsed = None
    if start and end:
        elapsed = round((s.dt.datetime.fromisoformat(end) - s.dt.datetime.fromisoformat(start)).total_seconds(), 3)
    return {"schema_version": 1, "path_base": "suite_root", "task_id": TASK, "run_id": RUN_ID,
            "case_id": case_id, "status": "archived", "output_dir": s.rel(OUTPUT), "temp_dir": s.rel(TEMP),
            "timings": {"started_at": start, "ended_at": end, "elapsed_seconds": elapsed,
                        "request_duration_sum_seconds": round(sum(r["elapsed_seconds"] for r in requests), 3),
                        "queue_wait_seconds": None, "user_feedback_wait_seconds": 0},
            "counts": {"snapshot_requests": len(renders), "successful_snapshot_requests": sum(r["http_status"] == 200 for r in renders),
                       "failed_snapshot_requests": sum(r["http_status"] != 200 for r in renders),
                       "retry_requests": sum(r["is_retry"] for r in renders), "other_service_requests": len(requests) - len(renders),
                       "dsl_versions": len({r["version_id"] for r in renders if r.get("version_id")}),
                       "image_views": sum(bool(r.get("image_path", "").endswith(".png")) and "待视觉检查" not in r.get("observable_issues", "") for r in iterations),
                       "completed_visual_iterations": sum(r["completed_visual_iteration"] for r in iterations)},
            "logs": {"requests": s.rel(TEMP / "requests.jsonl"), "iterations": s.rel(TEMP / "iterations.jsonl")},
        "aggregation_scope": "only request/iteration records whose case_id equals this round or case; all records for case_id=all; shared document requests excluded"}


def task_metrics() -> dict:
    result = s.metrics(RUN_ID, TASK)
    iterations = s.read_jsonl(TEMP / "iterations.jsonl")
    result["image_views"] = sum(bool(x.get("image_path", "").endswith(".png")) and "待视觉检查" not in x.get("observable_issues", "") for x in iterations)
    result["view_count_policy"] = "pending-render records are not image views; only recorded actual Read events count"
    jwrite(OUTPUT / "task-metrics.json", result)
    return result


def usage(task_module, status: str, scope: str, extra: str) -> None:
    output_dir = OUTPUT / scope if scope else OUTPUT
    metrics_path = output_dir / "task-metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    lines = [f"# {TASK} Snapshot 使用与自检报告", "", f"- 状态：{status}", f"- 运行 ID：`{RUN_ID}`",
             f"- 范围：{scope or '本题累计'}", f"- 输出根：`{s.rel(OUTPUT)}`（path_base=suite_root）",
             f"- 临时根：`{s.rel(TEMP)}`（path_base=suite_root）", f"- 服务基址：{s.BASE}", "",
             "## 文档与能力应用", "",
             "实际复用共享缓存的 AI 使用指南、OpenAPI、Parser 语法/标签/文本、布局、绘制、字体与错误文档；",
             "未在准备阶段发起HTTP。执行使用 UTF-8 text/plain POST /snapshot，以HTTP状态、Content-Type和真实PNG字节验收。",
             f"字体来自共享 `/fonts` 响应 `tmp/{RUN_ID}/_suite/shared/fonts.txt`，选择 `{FONT}`。",
             "A21/A22为预置需求连续执行模式，未来轮次可提前访问，不是隐藏反馈盲测。", "",
             "## 视觉检查与修改", "",
             "每张晋升PNG必须具有同版本候选manifest、实际Read查看记录、pass结论与图片SHA-256。",
             "初版待视觉检查保留在iterations.jsonl；失败候选不删除，修改后递增版本。",
             "脚本的静态/像素/数据检查不能替代实际打开图片。", "", extra, "",
             "## 指标与留痕", "", f"- 结构化指标：`{metrics_path.relative_to(output_dir).as_posix()}`",
             f"- 请求日志：`{s.rel(TEMP / 'requests.jsonl')}`", f"- 迭代日志：`{s.rel(TEMP / 'iterations.jsonl')}`",
             f"- 候选晋升：`{s.rel(TEMP / 'promotions.jsonl')}`", "",
             "请求/版本/查看次数及计时以指标文件为准；每轮仅聚合本case_id，任务根不重复累加轮次明细。",
             "排队耗时不可测记为null；预置轮次无人为反馈等待，记0。", "",
             "## 文件与路径", "", "所有最终PNG保留服务原始字节，并与完整同名.snapshot配对；旧轮与失败尝试不覆盖。",
             "本地记录使用suite_root或output_dir显式基准；脚本从自身位置解析总根，不写死机器盘符。",
             "总根.gitignore仅排除运行时缓存，不排除tmp/、outputs/或过程证据。", ""]
    (output_dir / "snapshot-usage.md").write_text("\n".join(lines), encoding="utf-8")


def parser(task_module, description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare", help="offline DSL/static validation; no HTTP, suite-state or final output")
    sub.add_parser("begin", help="execution only: verify strict order and begin task")
    r = sub.add_parser("render")
    r.add_argument("unit")
    r.add_argument("--kind", default="baseline")
    v = sub.add_parser("review")
    v.add_argument("unit"); v.add_argument("version"); v.add_argument("--result", choices=["pass", "fail"], required=True)
    v.add_argument("--observation", required=True)
    a = sub.add_parser("promote")
    a.add_argument("unit"); a.add_argument("--version")
    return p


def dispatch(task_module, description: str) -> None:
    args = parser(task_module, description).parse_args()
    if args.command == "prepare":
        prepare(task_module, task_module.UNITS)
    elif args.command == "begin":
        begin()
    else:
        execution_guard()
        if args.command == "render":
            render(task_module, args.unit, args.kind)
        elif args.command == "review":
            review(args.unit, args.version, args.result, args.observation)
        elif args.command == "promote":
            print(promote(task_module, args.unit, args.version))
