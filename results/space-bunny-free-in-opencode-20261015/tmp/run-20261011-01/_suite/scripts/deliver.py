#!/usr/bin/env python
"""任务交付的一站式封装：定稿 → 渲染 → 审计 JSON → 迭代记录 → 指标 → 使用报告。

各题只需给出 `spec`（需求核对、请求/迭代记录、设计说明等），即可生成全部交付物。
路径基准：相对 suite_root（环境变量 SNAPSHOT_TASK_ROOT）。
"""

from __future__ import annotations

import json
import time
import sys
from pathlib import Path

sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import report_common as rc  # noqa: E402
import report_gen as rg  # noqa: E402
import suite_log as sl  # noqa: E402


def run(spec: dict) -> dict:
    """spec 字段：
      task_id, title, version, source_drafts {逻辑名: 草稿文件名},
      images [{name, draft_key}], audit_json {filename, draft_name, artifacts_extra},
      audit_fields_ok (bool), req_items, request_rows, change_rows, design_notes,
      unresolved, iterations [(version, kind, image_key|None, problems, changes, comparison)],
      started_at, candidates, extra_capabilities, extra_docs
    """
    tid = spec["task_id"]
    out_dir, temp_dir = ft.task_dirs(tid)
    ver = spec["version"]

    # ---- 1. 提升 DSL + 渲染最终图
    # 服务端会偶发「HTTP 200 但响应体为空」或超时（status=null）。这是可重试的传输层故障，
    # 不应让整份交付中断；每次重试都是一次真实请求，照实记入 requests.jsonl。
    results = {}
    failed = []
    for img in spec["images"]:
        dsl_name = img.get("dsl") or (img["name"].rsplit(".", 1)[0] + ".snapshot")
        src = f"{temp_dir}/drafts/{spec['source_drafts'][img['draft_key']]}"
        dsl_rel = ft.promote_dsl(tid, src, dsl_name)
        r = None
        for attempt in range(1, int(spec.get("render_attempts", 5)) + 1):
            r = ft.render_final(tid, f"final-{img['draft_key']}", dsl_rel, img["name"],
                                temp_dir, is_retry=attempt > 1)
            if r.get("ok"):
                break
            failed.append({"image": img["name"], "attempt": attempt,
                           "status": r.get("status"), "duration_seconds": r.get("duration_seconds"),
                           "response_file": r.get("response_file")})
            print(f"{tid} render attempt {attempt} failed for {img['name']}: "
                  f"status={r.get('status')} 保留响应 {r.get('response_file')}")
            time.sleep(min(20, 3 * attempt))
        if not r.get("ok"):
            raise SystemExit(f"{tid} render failed after retries: {r}")
        results[img["draft_key"]] = {"dsl": dsl_rel, "render": r,
                                     "size": ft.png_size(f"{out_dir}/{img['name']}")}
        print(f"{tid} {img['name']} -> {r['image_info']}")
    if failed:
        print(f"{tid} 渲染重试记录：{json.dumps(failed, ensure_ascii=False)}")

    # ---- 2. 审计 JSON
    outputs = []
    for img in spec["images"]:
        info = results[img["draft_key"]]
        outputs.append({"kind": "png", "path": f"{out_dir}/{img['name']}",
                        "dsl": info["dsl"], "required_by": "task.json required_outputs", **info["size"]})
        outputs.append({"kind": "dsl", "path": info["dsl"]})

    audit_rel = None
    audit_specs = spec.get("audit_json")
    if audit_specs:
        if isinstance(audit_specs, dict):        # 单个审计 JSON
            audit_specs = [audit_specs]
        for aj in audit_specs:                  # 可交付多个专用 JSON
            data = json.loads((ft.root() / f"{temp_dir}/drafts/{aj['draft_name']}")
                              .read_text(encoding="utf-8"))
            art = {}
            for img in spec["images"]:
                art[img["name"]] = {**results[img["draft_key"]]["size"],
                                    "dsl": img.get("dsl") or (img["name"].rsplit(".", 1)[0] + ".snapshot"),
                                    "image_info": results[img["draft_key"]]["render"].get("image_info")}
            data.setdefault("artifacts", {})
            data["artifacts"].update(art)
            data["artifacts"][aj["filename"]] = {
                "schema_version": 1, "task_id": tid, "path_base": "output_dir"}
            rel = ft.write_audit_json(tid, aj["filename"], data)
            outputs.append({"kind": "json", "path": rel})
            print(f"{tid} audit -> {rel}")

    outputs.append({"kind": "report", "path": f"{out_dir}/snapshot-usage.md"})
    outputs.append({"kind": "metrics", "path": f"{out_dir}/task-metrics.json"})

    # ---- 3. 迭代记录
    log_rel = f"{temp_dir}/iterations.jsonl"
    r = ft.root()
    if not sl.read_jsonl(r / log_rel) and spec.get("iterations"):
        for it in spec["iterations"]:
            if isinstance(it, dict):
                v, kind, img_key = it["version"], it.get("kind", "visual"), it.get("image_key")
                prob, chg, cmp_, comp = (it.get("problems"), it.get("changes"),
                                         it.get("comparison"), it.get("complete", True))
            else:  # (version, kind, image_key, problems, changes, comparison)
                v, kind, img_key, prob, chg, cmp_ = it
                comp = True
            img_rel = None
            if img_key and img_key in spec["source_drafts"]:
                img_rel = f"{temp_dir}/preview/{spec['source_drafts'][img_key].replace('.snapshot', '.png')}"
            elif img_key == "final":
                img_rel = f"{out_dir}/{spec['images'][0]['name']}"
            ft.log(tid, version=v, kind=kind, image=img_rel, problems=prob,
                   changes=chg, comparison=cmp_, complete=comp)
        print(f"{tid} iterations: {len(sl.read_jsonl(r / log_rel))}")

    # ---- 4. 指标
    m = ft.build_metrics(
        tid, started_at=spec["started_at"], ended_at=sl.now_iso(),
        status="completed", stop_reason=spec.get("stop_reason", "需求满足并完成逐图视觉自检"),
        feedback_wait=0.0, rate_limit_wait=0.0, queue_wait=None,
        outputs=outputs, candidates=spec.get("candidates"), round_label="round-01")
    recs = sl.read_jsonl(r / f"{temp_dir}/requests.jsonl")
    renders = [x for x in recs if x.get("request_type") == "render"]
    ok = next((x for x in renders if x.get("status") == 200), None)
    m["timings"]["first_usable_image_seconds"] = round(
        sum(float(x.get("duration_seconds") or 0) for x in renders[:renders.index(ok) + 1]), 3) if ok else None
    ft.write_metrics(tid, m)

    # ---- 5. 使用报告
    docs_rows = rc.DOCS_COMMON + (spec.get("extra_docs") or "")
    caps = rc.CAPS_COMMON + (("\n本题额外用到：" + spec["extra_capabilities"]) if spec.get("extra_capabilities") else "")
    md = rg.render(
        task_id=tid, title=spec["title"], run_id=ft.run_id(),
        status="完成", stop_reason=spec.get("stop_reason", "需求满足并完成逐图视觉自检"),
        out_dir=out_dir, temp_dir=temp_dir,
        req_items=spec["req_items"], docs_rows=docs_rows, capabilities=caps,
        counts={"other_queries": spec.get("other_queries",
                                          "字体查询与文档读取为 run 级共享准备；本题无额外接口查询")},
        request_rows=rc.req_table(spec["request_rows"]),
        change_rows=rc.iter_table(spec["change_rows"]),
        metrics_rows=rc.metrics_table(m),
        design_notes=spec["design_notes"], unresolved=spec["unresolved"],
        retention=rc.RETENTION_COMMON)
    print(ft.write_usage(tid, md))
    return {"outputs": outputs, "metrics": m}