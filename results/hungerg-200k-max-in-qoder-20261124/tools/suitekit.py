from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
CONFIG = json.loads((ROOT / "run-config.json").read_text(encoding="utf-8"))
BASE = CONFIG["service_base_url"].rstrip("/")
TZ = dt.timezone(dt.timedelta(hours=8))
FONT = "Noto Sans CJK SC"


def now() -> dt.datetime:
    return dt.datetime.now(TZ)


def iso(value: dt.datetime | None = None) -> str:
    return (value or now()).isoformat(timespec="milliseconds")


def rel(path: Path, base: Path = ROOT) -> str:
    return path.resolve().relative_to(base.resolve()).as_posix()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".new")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl(path: Path, item: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")


def init_suite() -> tuple[str, Path, Path]:
    run_file = ROOT / "tmp" / "_suite" / "run-id.txt"
    if run_file.exists():
        run_id = run_file.read_text(encoding="utf-8").strip()
    else:
        run_id = now().strftime("%Y%m%dT%H%M%S%z") + "-" + uuid.uuid4().hex[:6]
        run_file.parent.mkdir(parents=True, exist_ok=True)
        run_file.write_text(run_id + "\n", encoding="utf-8")
    output = ROOT / CONFIG["output_root"] / run_id / "_suite"
    temp = ROOT / CONFIG["temp_root"] / run_id / "_suite"
    output.mkdir(parents=True, exist_ok=True)
    (temp / "checkpoints").mkdir(parents=True, exist_ok=True)
    gitignore = ROOT / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    required = (ROOT / "templates" / "gitignore-template.txt").read_text(encoding="utf-8").splitlines()
    rules = [line for line in required if line.strip() and not line.startswith("#")]
    missing = [rule for rule in rules if rule not in existing.splitlines()]
    if missing:
        prefix = existing.rstrip() + ("\n" if existing.strip() else "")
        gitignore.write_text(prefix + "# Suite runtime caches\n" + "\n".join(missing) + "\n", encoding="utf-8")
    state_path = output / "suite-state.json"
    if not state_path.exists():
        state = {
            "schema_version": 1,
            "path_base": "suite_root",
            "suite_version": CATALOG["suite_version"],
            "run_id": run_id,
            "profile": CONFIG["default_profile"],
            "status": "in_progress",
            "started_at": iso(),
            "updated_at": iso(),
            "current_task": None,
            "current_round": None,
            "current_case": None,
            "last_checkpoint": None,
            "tasks": [
                {
                    "id": task["id"], "status": "pending", "started_at": None, "ended_at": None,
                    "output_dir": f'{CONFIG["output_root"]}/{run_id}/{task["id"]}',
                    "temp_dir": f'{CONFIG["temp_root"]}/{run_id}/{task["id"]}',
                    "completed_rounds": [], "completed_cases": [], "artifacts": [],
                    "visual_review_evidence": [], "unresolved_issues": [], "resume_notes": None,
                }
                for task in CATALOG["tasks"]
            ],
            "suite_artifacts": [],
        }
        write_json(state_path, state)
        append_jsonl(temp / "events.jsonl", {"event_id": run_id + "-suite-start", "at": iso(), "event": "suite_start", "profile": "all"})
        checkpoint(run_id, "suite-start")
    return run_id, output, temp


def checkpoint(run_id: str, label: str) -> None:
    output = ROOT / CONFIG["output_root"] / run_id / "_suite"
    temp = ROOT / CONFIG["temp_root"] / run_id / "_suite"
    state = json.loads((output / "suite-state.json").read_text(encoding="utf-8"))
    state["updated_at"] = iso()
    files = sorted((temp / "checkpoints").glob("state-*.json"))
    number = int(files[-1].stem.split("-")[-1]) + 1 if files else 1
    name = f"state-{number:06d}.json"
    write_json(temp / "checkpoints" / name, state)
    state["last_checkpoint"] = f'{CONFIG["temp_root"]}/{run_id}/_suite/checkpoints/{name}'
    write_json(output / "suite-state.json", state)
    append_jsonl(temp / "events.jsonl", {"event_id": f"{run_id}-{label}-{number:06d}", "at": iso(), "event": label, "checkpoint": state["last_checkpoint"]})


def task_dirs(run_id: str, task_id: str) -> tuple[Path, Path]:
    return (ROOT / CONFIG["output_root"] / run_id / task_id,
            ROOT / CONFIG["temp_root"] / run_id / task_id)


def begin_task(run_id: str, task_id: str) -> None:
    output, temp = task_dirs(run_id, task_id)
    output.mkdir(parents=True, exist_ok=True)
    temp.mkdir(parents=True, exist_ok=True)
    state_path = ROOT / CONFIG["output_root"] / run_id / "_suite" / "suite-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    task = next(item for item in state["tasks"] if item["id"] == task_id)
    if task["status"] == "pending":
        task["status"] = "in_progress"
        task["started_at"] = iso()
    state["current_task"] = task_id
    state["current_round"] = None
    state["current_case"] = None
    write_json(state_path, state)
    checkpoint(run_id, f"{task_id}-start")


def finish_task(run_id: str, task_id: str, artifacts: list[str], reviews: list[str], issues: list[str] | None = None, rounds: list[str] | None = None, cases: list[str] | None = None) -> None:
    state_path = ROOT / CONFIG["output_root"] / run_id / "_suite" / "suite-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    task = next(item for item in state["tasks"] if item["id"] == task_id)
    task["status"] = "completed" if not issues else "partial"
    task["ended_at"] = iso()
    task["artifacts"] = artifacts
    task["visual_review_evidence"] = reviews
    task["unresolved_issues"] = issues or []
    if rounds:
        task["completed_rounds"] = rounds
    if cases:
        task["completed_cases"] = cases
    state["current_task"] = None
    write_json(state_path, state)
    checkpoint(run_id, f"{task_id}-finish")


def request(run_id: str, task_id: str, kind: str, url: str, body: bytes | None = None, content_type: str | None = None, attempt: int = 1, parent_id: str | None = None, version_id: str | None = None, case_id: str | None = None) -> tuple[bytes, dict]:
    output, temp = task_dirs(run_id, task_id)
    if task_id == "_shared":
        temp = ROOT / CONFIG["temp_root"] / run_id / "_suite" / "shared"
    request_id = f"{run_id}-{task_id}-{kind}-{uuid.uuid4().hex[:12]}"
    headers = {"X-Request-Id": request_id, "User-Agent": "HungerG-Snapshot-Suite/1.0"}
    if content_type:
        headers["Content-Type"] = content_type
    key = os.environ.get("SNAPSHOT_API_KEY")
    if key:
        headers["X-API-Key"] = key
    req = urllib.request.Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
    started = now()
    monotonic = time.monotonic()
    error = None
    response = b""
    status = None
    response_type = None
    response_headers = {}
    try:
        with urllib.request.urlopen(req, timeout=180) as result:
            status = result.status
            response_type = result.headers.get("Content-Type")
            response_headers = dict(result.headers.items())
            response = result.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        response_type = exc.headers.get("Content-Type")
        response_headers = dict(exc.headers.items())
        response = exc.read()
        error = f"HTTP {status}"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed = round(time.monotonic() - monotonic, 3)
    request_path = temp / f"{kind}-{started.strftime('%H%M%S%f')}-{attempt:02d}.request"
    response_path = request_path.with_suffix(".response")
    request_path.parent.mkdir(parents=True, exist_ok=True)
    if body is not None:
        request_path.write_bytes(body)
    else:
        request_path.write_text(f"GET {url}\n", encoding="utf-8")
    response_path.write_bytes(response)
    record = {
        "request_id": request_id, "task_id": task_id, "case_id": case_id, "request_type": kind,
        "attempt": attempt, "is_retry": attempt > 1, "parent_request_id": parent_id,
        "version_id": version_id, "started_at": iso(started), "ended_at": iso(),
        "timezone": "+08:00", "elapsed_seconds": elapsed, "method": req.method,
        "url": url, "path_base": "suite_root", "request_file": rel(request_path),
        "response_file": rel(response_path), "http_status": status,
        "content_type": response_type,
        "request_id_header": response_headers.get("X-Request-Id", request_id),
        "server_timing": response_headers.get("Server-Timing"),
        "snapshot_cache": response_headers.get("X-Snapshot-Cache"),
        "rate_limit_remaining": response_headers.get("X-RateLimit-Remaining"),
        "retry_after": response_headers.get("Retry-After"), "error": error,
    }
    if status in (429, 503):
        record["retry_after"] = exc.headers.get("Retry-After") if isinstance(exc, urllib.error.HTTPError) else None
    append_jsonl(temp / "requests.jsonl", record)
    return response, record


def fetch_document(run_id: str, name: str, url: str) -> tuple[Path, dict]:
    shared_temp = ROOT / CONFIG["temp_root"] / run_id / "_suite" / "shared"
    shared_temp.mkdir(parents=True, exist_ok=True)
    destination = shared_temp / name
    if not destination.exists():
        data, record = request(run_id, "_shared", "document", url)
        if record["http_status"] != 200:
            raise RuntimeError(f"Document fetch failed: {url}: {record}")
        destination.write_bytes(data)
    else:
        record = {"request_id": None, "http_status": 200, "cached": True, "response_file": rel(destination), "url": url}
    return destination, record


def prepare_docs(run_id: str) -> None:
    documents = {
        "ai-guide.md": CONFIG["service_guide_url"],
        "openapi.yaml": BASE + "/openapi.yaml",
        "llms.txt": CONFIG["dsl_documentation_url"] + "llms.txt",
        "parser.md": CONFIG["dsl_documentation_url"] + "guides/parser.md",
        "parser-tags.md": CONFIG["dsl_documentation_url"] + "reference/parser-tags.md",
        "parser-text.md": CONFIG["dsl_documentation_url"] + "reference/parser-text.md",
        "examples.md": CONFIG["dsl_documentation_url"] + "guides/examples.md",
        "fonts.md": CONFIG["dsl_documentation_url"] + "guides/fonts.md",
        "media-text.md": CONFIG["dsl_documentation_url"] + "guides/media-text.md",
        "painting.md": CONFIG["dsl_documentation_url"] + "guides/painting.md",
        "layout.md": CONFIG["dsl_documentation_url"] + "guides/layout.md",
        "parser-errors.md": CONFIG["dsl_documentation_url"] + "reference/parser-errors.md",
        "data-templates.md": CONFIG["dsl_documentation_url"] + "guides/data-templates.md",
    }
    for name, url in documents.items():
        fetch_document(run_id, name, url)
    fonts, record = request(run_id, "_shared", "fonts", BASE + "/fonts")
    if record["http_status"] != 200:
        raise RuntimeError(f"Font query failed: {record}")
    shared_temp = ROOT / CONFIG["temp_root"] / run_id / "_suite" / "shared"
    (shared_temp / "fonts.txt").write_bytes(fonts)
    checkpoint(run_id, "shared-docs-ready")


def render(run_id: str, task_id: str, dsl: str, stem: str, version: str = "v001", final: bool = False, kind: str = "baseline", max_retries: int = 4, case_id: str | None = None) -> tuple[Path, dict]:
    output, temp = task_dirs(run_id, task_id)
    version_dir = temp / "versions" / version
    version_dir.mkdir(parents=True, exist_ok=True)
    dsl_path = version_dir / f"{stem}.snapshot"
    dsl_path.write_text(dsl, encoding="utf-8")
    parent_id = None
    for attempt in range(1, max_retries + 1):
        data, record = request(run_id, task_id, "render", BASE + "/snapshot", dsl.encode("utf-8"),
                               "text/plain; charset=utf-8", attempt, parent_id, version, case_id)
        parent_id = record["request_id"]
        if record["http_status"] == 200 and (record["content_type"] or "").startswith("image/"):
            image = version_dir / f"{stem}-{attempt:02d}.png"
            image.write_bytes(data)
            if final:
                shutil.copyfile(image, output / f"{stem}.png")
                shutil.copyfile(dsl_path, output / f"{stem}.snapshot")
            record["image_path"] = rel(image)
            return image, record
        if record["http_status"] not in (429, 503) or attempt == max_retries:
            raise RuntimeError(f"Render failed: {json.dumps(record, ensure_ascii=False)}\n{data.decode('utf-8', errors='replace')}")
        delay = float(record.get("retry_after") or min(2 ** attempt, 20))
        time.sleep(delay)
    raise RuntimeError("unreachable")


def record_iteration(run_id: str, task_id: str, version: str, image: Path, kind: str, observed: str, changes: str, compared: str, completed: bool = True, case_id: str | None = None) -> None:
    _, temp = task_dirs(run_id, task_id)
    append_jsonl(temp / "iterations.jsonl", {
        "iteration_id": f"{run_id}-{task_id}-{uuid.uuid4().hex[:10]}",
        "task_id": task_id, "case_id": case_id,
        "version_id": version, "parent_version": None, "type": kind,
        "image_path": rel(image), "viewed_at": iso(), "timezone": "+08:00",
        "observable_issues": observed, "changes": changes,
        "review_and_comparison": compared, "completed_visual_iteration": completed,
    })


def metrics(run_id: str, task_id: str) -> dict:
    output, temp = task_dirs(run_id, task_id)
    requests = read_jsonl(temp / "requests.jsonl")
    iterations = read_jsonl(temp / "iterations.jsonl")
    renders = [item for item in requests if item["request_type"] == "render"]
    state_path = ROOT / CONFIG["output_root"] / run_id / "_suite" / "suite-state.json"
    task = next(item for item in json.loads(state_path.read_text(encoding="utf-8"))["tasks"] if item["id"] == task_id)
    pngs = sorted(output.rglob("*.png"))
    spec_path = next(ROOT / item["task_spec"] for item in CATALOG["tasks"] if item["id"] == task_id)
    task_spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if task_spec.get("required_outputs"):
        final_pngs = [output / item["filename"] for item in task_spec["required_outputs"] if (output / item["filename"]).is_file()]
    elif (output / "portfolio.json").is_file():
        portfolio = json.loads((output / "portfolio.json").read_text(encoding="utf-8"))
        final_pngs = [output / item["png"] for item in portfolio.get("cases", []) if item.get("png") and (output / item["png"]).is_file()]
    else:
        final_pngs = pngs
    visual_types = {"visual", "requirement-change"}
    unviewed_baselines = sum(
        item["type"] == "baseline"
        and not item.get("completed_visual_iteration")
        and "待视觉检查" not in item.get("observable_issues", "")
        for item in iterations
    )
    result = {
        "schema_version": 1, "path_base": "suite_root", "task_id": task_id, "run_id": run_id,
        "status": task["status"], "started_at": task["started_at"], "ended_at": task["ended_at"] or iso(),
        "wall_clock_seconds": None, "first_usable_image_seconds": None,
        "user_feedback_wait_seconds": 0, "queue_wait_seconds": None,
        "request_elapsed_seconds_sum": round(sum(item["elapsed_seconds"] for item in requests), 3),
        "snapshot_requests": len(renders), "successful_snapshot_requests": sum(item["http_status"] == 200 for item in renders),
        "failed_snapshot_requests": sum(item["http_status"] != 200 for item in renders),
        "retry_requests": sum(item["is_retry"] for item in renders),
        "other_service_requests": sum(item["request_type"] != "render" for item in requests),
        "document_requests": sum(item["request_type"] == "document" for item in requests),
        "dsl_versions": len({item["version_id"] for item in renders if item.get("version_id")}),
        "image_views": sum(str(item.get("image_path", "")).lower().endswith(".png") for item in iterations),
        "completed_visual_iterations": sum(
            item["type"] in visual_types
            and item["completed_visual_iteration"]
            and "待视觉检查" not in item.get("observable_issues", "")
            for item in iterations
        ),
        "incomplete_visual_iterations": sum(
            item["type"] in visual_types
            and not item["completed_visual_iteration"]
            and "待视觉检查" not in item.get("observable_issues", "")
            for item in iterations
        ),
        "unviewed_baselines": unviewed_baselines,
        "alternative_visual_iterations": sum(item["type"] == "alternative" and item["completed_visual_iteration"] for item in iterations),
        "syntax_or_retry_iterations": sum(item["type"] in {"syntax-fix", "retry"} for item in iterations),
        "final_visual_rechecks": sum(item["type"] == "audit_visual_recheck" for item in iterations),
        "final_pngs": len(final_pngs), "all_output_pngs": len(pngs), "output_dir": rel(output), "temp_dir": rel(temp),
        "logs": {"requests": rel(temp / "requests.jsonl"), "iterations": rel(temp / "iterations.jsonl")},
    }
    if task["started_at"]:
        end = dt.datetime.fromisoformat(task["ended_at"]) if task["ended_at"] else now()
        result["wall_clock_seconds"] = round((end - dt.datetime.fromisoformat(task["started_at"])).total_seconds(), 3)
    success = [item for item in renders if item["http_status"] == 200]
    if success and task["started_at"]:
        result["first_usable_image_seconds"] = round((dt.datetime.fromisoformat(success[0]["ended_at"]) - dt.datetime.fromisoformat(task["started_at"])).total_seconds(), 3)
    metric_path = output / "task-metrics.json"
    if metric_path.exists():
        previous = json.loads(metric_path.read_text(encoding="utf-8"))
        for key in ("case_metrics", "tool_usage_summary", "independent_creative_cases"):
            if key in previous:
                result[key] = previous[key]
    write_json(metric_path, result)
    return result


def audit_identity(task_id: str) -> dict:
    return {"schema_version": 1, "task_id": task_id, "path_base": "output_dir"}


def snapshot(width: int, height: int, children: list[str], background: str = "#F4F7FB") -> str:
    return f'<Snapshot type="png" background="{background}">\n<Container width="{width}" height="{height}">\n<Stack clipBehavior="NONE">\n' + "\n".join(children) + "\n</Stack>\n</Container>\n</Snapshot>\n"


def positioned(x: float, y: float, width: float | None = None, height: float | None = None, child: str = "") -> str:
    attrs = [f'left="{x:g}"', f'top="{y:g}"']
    if width is not None:
        attrs.append(f'width="{width:g}"')
    if height is not None:
        attrs.append(f'height="{height:g}"')
    return "<Positioned " + " ".join(attrs) + ">\n" + child + "\n</Positioned>"


def box(x: float, y: float, width: float, height: float, color: str, radius: float = 0, border: str | None = None, child: str = "") -> str:
    attrs = [f'width="{width:g}"', f'height="{height:g}"', f'color="{color}"']
    if radius:
        attrs.append(f'borderRadius="{radius:g}"')
    if border:
        attrs.append(f'border="1 SOLID {border}"' if not border.startswith("none") else f'border="{border}"')
    attrs.append('clipBehavior="ANTI_ALIAS"' if radius else 'clipBehavior="NONE"')
    container = "<Container " + " ".join(attrs) + ">\n" + child + "\n</Container>"
    return positioned(x, y, child=container)


def text(value: str, size: float = 20, color: str = "#172033", bold: bool = False, align: str = "LEFT", width: float | None = None, height: float | None = None, max_lines: int | None = None, family: str = FONT) -> str:
    attrs = [f'fontFamily="{family}"', f'fontSize="{size:g}"', f'color="{color}"',
             f'textAlign="{align}"', 'fontStyle="BOLD"' if bold else 'fontStyle="NORMAL"',
             'softWrap="true"']
    if width is not None:
        attrs.append(f'width="{width:g}"')
    if max_lines is not None:
        attrs.extend([f'maxLines="{max_lines}"', 'overflow="ELLIPSIS"'])
    safe = escape(str(value)).replace("]]>", "]]]]><![CDATA[>")
    return "<Text " + " ".join(attrs) + ">" + safe + "</Text>"


def label(value: str, x: float, y: float, width: float, height: float, size: float = 20, color: str = "#172033", bold: bool = False, align: str = "LEFT") -> str:
    return positioned(x, y, width, height, text(value, size, color, bold, align, width, height))


def line(x1: float, y1: float, x2: float, y2: float, color: str, thickness: float = 1) -> str:
    dx, dy = x2 - x1, y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    if not length:
        return box(x1, y1, thickness, thickness, color)
    angle = __import__("math").degrees(__import__("math").atan2(dy, dx))
    segment = (f'<Container width="{length:g}" height="{thickness:g}" color="{color}" '
               f'transform="rotate({angle:g}deg)" transformAlignment="CENTER_LEFT" />')
    return positioned(x1, y1, length, thickness, segment)


def circle(cx: float, cy: float, radius: float, color: str, border: str | None = None) -> str:
    return box(cx - radius, cy - radius, radius * 2, radius * 2, color, radius, border)


def write_usage(run_id: str, task_id: str, status: str, checks: list[tuple[str, str]], design: str, issues: str, files: list[str]) -> None:
    output, temp = task_dirs(run_id, task_id)
    doc_root = f'{CONFIG["temp_root"]}/{run_id}/_suite/shared'
    rows = "\n".join(f"| {name} | {result} |" for name, result in checks)
    content = f"""# {task_id} Snapshot 使用与自检报告

- 状态：{status}
- 运行 ID：`{run_id}`
- 输出根：`{rel(output)}`（path_base=suite_root）
- 临时根：`{rel(temp)}`（path_base=suite_root）
- 服务基址：{BASE}

## 文档与工具应用

实际读取服务指南、OpenAPI、Parser 语法、标签与文本属性、示例、字体、布局、绘制、错误处理与数据模板文档；原始响应缓存在 `{doc_root}/`。服务请求使用 UTF-8 纯文本 POST `/snapshot`，依据 HTTP 状态、Content-Type、X-Request-Id 与 Server-Timing 留痕。字体从真实 `/fonts` 响应选择 `{FONT}`。主体、图表、文字和几何均由完整 Snapshot DSL 构造。

## 视觉自检

| 检查项 | 结果与证据 |
|---|---|
{rows}

## 设计选择

{design}

## 问题、修改与验证

{issues}

## 交付文件

""" + "\n".join(f"- `{name}`" for name in files) + "\n"
    (output / "snapshot-usage.md").write_text(content, encoding="utf-8")
