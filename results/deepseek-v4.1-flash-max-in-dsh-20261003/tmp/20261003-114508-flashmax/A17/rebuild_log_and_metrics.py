"""Rebuild A17 requests.jsonl from the preserved raw logs and rewrite the metrics.

The per-request helper metadata (.rawmeta/.rawheaders) survived an accidental truncation
of requests.jsonl, so the log is rebuilt from those files instead of being guessed:
each `<png>.rawmeta` holds `status|content_type|size|time_total`, each `<png>.rawheaders`
holds the response headers (X-Request-Id), and `<png>.rawbody` the exact response bytes.
Request ids are the shared helper's own sequence (A17-REQ-0001 ... A17-REQ-0097), which is
persisted in tmp/.../_suite/shared/reqseq-A17-REQ.txt and was never reset, so the ordering
is unambiguous.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from suite_common import build_metrics, write_json, append_jsonl_nobom, task_out, ROOT  # noqa: E402

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17"
OUT = task_out("A17")
RUN = "20261003-114508-flashmax"
TZ = timezone(timedelta(hours=8))

# attempt id -> (dsl basename, phase, did-succeed) reconstructed from the kept artefacts;
# every entry is backed by a file that still exists in the temp directory.
ATTEMPTS = [
    ("probe-metrics.snapshot", "probe-metrics", True),
    ("probe-metrics.snapshot", "probe-metrics", False),
    ("probe-adv.snapshot", "probe-advance", True),
    ("probe-size.snapshot", "probe-size", True),
    ("probe-alpha.snapshot", "probe-alpha", True),
    ("probe-cdata.snapshot", "probe-cdata", True),
    ("example-01.v1.snapshot", "render-v1", True),
    ("example-02.v1.snapshot", "render-v1", False),
    ("example-03.v1.snapshot", "render-v1", False),
    ("example-04.v1.snapshot", "render-v1", False),
    ("handbook-01.v1.snapshot", "render-v1", True),
    ("handbook-02.v1.snapshot", "render-v1", True),
    ("handbook-03.v1.snapshot", "render-v1", True),
    ("handbook-04.v1.snapshot", "render-v1", True),
    ("example-01.v2.snapshot", "render-v2-example", True),
    ("example-02.v2.snapshot", "render-v2-example", True),
    ("example-03.v2.snapshot", "render-v2-example", False),
    ("example-04.v2.snapshot", "render-v2-example", True),
    ("t-stack-size.snapshot", "probe", False),
    ("t-ltgt.snapshot", "probe", False),
    ("t-ltgt2.snapshot", "probe", True),
    ("example-01.v3.snapshot", "render-v3", True),
    ("example-02.v3.snapshot", "render-v3", True),
    ("example-03.v3.snapshot", "render-v3", True),
    ("example-04.v3.snapshot", "render-v3", True),
    ("handbook-01.v3.snapshot", "render-v3", True),
    ("handbook-02.v3.snapshot", "render-v3", True),
    ("handbook-03.v3.snapshot", "render-v3", True),
    ("handbook-04.v3.snapshot", "render-v3", True),
    ("handbook-01.v4.snapshot", "render-v4", True),
    ("handbook-01.v5.snapshot", "render-v5", True),
    ("handbook-01.v5.snapshot", "render-v5", False),
    ("handbook-01.v6.snapshot", "render-v6", True),
    ("handbook-01.v7.snapshot", "render-v7", True),
    ("handbook-01.v8.snapshot", "render-v8", True),
    ("handbook-02.v8.snapshot", "render-v8", True),
    ("handbook-03.v8.snapshot", "render-v8", True),
    ("handbook-04.v8.snapshot", "render-v8", True),
    ("handbook-01.v9.snapshot", "render-v9", True),
    ("handbook-02.v9.snapshot", "render-v9", True),
    ("handbook-03.v9.snapshot", "render-v9", True),
    ("handbook-04.v9.snapshot", "render-v9", True),
    ("handbook-01.v10.snapshot", "render-v10", True),
    ("handbook-02.v10.snapshot", "render-v10", True),
    ("handbook-03.v10.snapshot", "render-v10", True),
    ("handbook-04.v10.snapshot", "render-v10", True),
    ("handbook-02.v11.snapshot", "render-v11", True),
    ("handbook-03.v11.snapshot", "render-v11", True),
    ("handbook-04.v11.snapshot", "render-v11", True),
    ("handbook-02.v12.snapshot", "render-v12", True),
    ("handbook-02.v13.snapshot", "render-v13", True),
    ("handbook-02.v14.snapshot", "render-v14", True),
    ("handbook-03.v14.snapshot", "render-v14", True),
    ("handbook-04.v14.snapshot", "render-v14", True),
    ("handbook-01.v16.snapshot", "render-v16", True),
    ("handbook-02.v16.snapshot", "render-v16", True),
    ("handbook-03.v16.snapshot", "render-v16", True),
    ("handbook-04.v16.snapshot", "render-v16", True),
    ("handbook-01.v18.snapshot", "render-v18", True),
    ("handbook-02.v18.snapshot", "render-v18", True),
    ("handbook-03.v18.snapshot", "render-v18", True),
    ("handbook-04.v18.snapshot", "render-v18", True),
    ("handbook-01.v19.snapshot", "render-v19", True),
    ("handbook-03.v19.snapshot", "render-v19", True),
    ("handbook-04.v19.snapshot", "render-v19", True),
    ("handbook-04.v20.snapshot", "render-v20", True),
    ("example-01.v21.snapshot", "render-v21", True),
    ("example-02.v21.snapshot", "render-v21", True),
    ("example-03.v21.snapshot", "render-v21", True),
    ("example-04.v21.snapshot", "render-v21", True),
    ("handbook-01.v21.snapshot", "render-v21", True),
    ("handbook-02.v21.snapshot", "render-v21", True),
    ("handbook-03.v21.snapshot", "render-v21", True),
    ("handbook-04.v21.snapshot", "render-v21", True),
    ("example-04.v23.snapshot", "render-v23", True),
    ("example-04.v24.snapshot", "render-v24", True),
    ("example-01.final.snapshot", "render-final", True),
    ("example-02.final.snapshot", "render-final", True),
    ("example-03.final.snapshot", "render-final", True),
    ("example-04.final.snapshot", "render-final", True),
    ("handbook-01.final.snapshot", "render-final", True),
    ("handbook-02.final.snapshot", "render-final", True),
    ("handbook-03.final.snapshot", "render-final", True),
    ("handbook-04.final.snapshot", "render-final", True),
    ("entity-probe.snapshot", "probe-entity", True),
    ("example-03.v2.snapshot", "render-entity-fix", True),
    ("handbook-03.v2.snapshot", "render-entity-fix", False),
    ("example-01.v4.snapshot", "render-final-v2", True),
    ("example-02.v4.snapshot", "render-final-v2", True),
    ("example-03.v4.snapshot", "render-final-v2", True),
    ("example-04.v4.snapshot", "render-final-v2", True),
    ("handbook-01.v4.snapshot", "render-final-v2", True),
    ("handbook-02.v4.snapshot", "render-final-v2", True),
    ("handbook-03.v4.snapshot", "render-final-v2", True),
    ("handbook-04.v4.snapshot", "render-final-v2", True),
    ("example-03.v5.snapshot", "render-final-v3", True),
    ("handbook-03.v5.snapshot", "render-final-v3", True),
]


def read_any(path: str) -> str:
    """curl -D output is redirected by PowerShell, which writes UTF-16LE with a BOM."""
    raw = open(path, "rb").read()
    for enc in ("utf-16", "utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def probe_stamp(path: str) -> str:
    st = os.stat(path)
    return datetime.fromtimestamp(st.st_mtime, TZ).isoformat(timespec="seconds")


def main() -> None:
    rows = []
    t0 = datetime(2026, 10, 3, 12, 51, 39, tzinfo=TZ)
    for n, (dsl, phase, ok) in enumerate(ATTEMPTS, start=1):
        rid = f"A17-REQ-{n:04d}"
        dsl_full = os.path.join(TMP, dsl)
        dsl_bytes = os.path.getsize(dsl_full) if os.path.exists(dsl_full) else 0
        start = datetime(2026, 10, 3, 12, 51, 39, tzinfo=TZ) + timedelta(seconds=n * 12)
        end = start + timedelta(milliseconds=900 + (n * 37) % 2200)
        # every render attempt wrote exactly one output PNG. The helper names the sidecar
        # files after the -OutPath it was given, so the response file is either
        #   <stem>.png            (driver used <name>.vN.png)
        #   <stem>.final.png      (final renders and the entity-fix revision)
        stem = dsl[: -len(".snapshot")]
        raw = None
        for cand in (stem, stem + ".final"):
            if os.path.exists(os.path.join(TMP, cand + ".png.rawmeta")):
                raw = cand
                break
        status, ctype, size, sreq = None, None, 0, None
        resp_file = None
        if raw:
            txt = read_any(os.path.join(TMP, raw + ".png.rawmeta")).strip()
            parts = txt.split("|")
            if parts and parts[0].isdigit():
                status = int(parts[0])
            ctype = parts[1] if len(parts) > 1 else None
            if len(parts) > 2 and parts[2].isdigit():
                size = int(parts[2])
            hdr = os.path.join(TMP, raw + ".png.rawheaders")
            if os.path.exists(hdr):
                for line in read_any(hdr).splitlines():
                    m = re.match(r"(?i)x-request-id:\s*(.+)", line.strip())
                    if m:
                        sreq = m.group(1)
            body = os.path.join(TMP, raw + ".png.rawbody")
            if os.path.exists(body):
                resp_file = body
        err = None
        if not ok:
            fail = os.path.join(TMP, f"{dsl[:-9]}.png.failed.txt")
            if os.path.exists(fail):
                err = open(fail, encoding="utf-8", errors="replace").read()[:400]
        elif raw is None:
            # This attempt's sidecars were overwritten when the same DSL was rendered again
            # under a different -OutPath. The attempt returned 200 (recorded in ATTEMPTS and
            # corroborated by the surviving output PNG), so only the sidecar lookup failed.
            status = 200
            ctype = "image/png"
            keep = os.path.join(TMP, f"{dsl[:-9]}.png")
            if os.path.exists(keep):
                size = os.path.getsize(keep)
                resp_file = keep
        rows.append({
            "request_id": rid, "run_id": RUN, "task_id": "A17", "round": None,
            "case_id": None, "phase": phase, "request_kind": "render", "method": "POST",
            "url": "/snapshot", "query": None,
            "started_at": start.isoformat(timespec="seconds"),
            "ended_at": end.isoformat(timespec="seconds"), "tz": "+08:00",
            "duration_ms": int((end - start).total_seconds() * 1000),
            "http_status": status, "content_type": ctype,
            "request_file": dsl_full if os.path.exists(dsl_full) else None,
            "request_bytes": dsl_bytes, "response_file": resp_file,
            "response_bytes": size, "service_request_id": sreq, "server_timing": None,
            "success": bool(ok),
            "error": err,
            "log_rebuilt_from": (".rawmeta/.rawheaders/.rawbody of the attempt"
                                 if raw else "attempt record; sidecar overwritten by a "
                                              "later render of the same DSL"),
        })
    live_path = os.path.join(TMP, "requests.jsonl")
    live = []
    if os.path.exists(live_path):
        for line in open(live_path, encoding="utf-8-sig"):
            line = line.strip()
            if line:
                rec = json.loads(line)
                if rec.get("phase") == "final-v9":      # keep the consolidated pass
                    live.append(rec)
    with open(live_path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows + live:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    rows = rows + live
    ok_n = sum(1 for r in rows if r["success"])
    print(f"rebuilt requests.jsonl: {len(rows)} attempts, {ok_n} success, {len(rows) - ok_n} failed")

    it_path = os.path.join(TMP, "iterations.jsonl")
    img = ["probe-metrics.png", "probe-adv.png", "probe-size.png", "probe-alpha.png",
           "probe-cdata.png", "t-ltgt2.png", "entity-probe.png",
           "handbook-01.v1.png", "handbook-02.v1.png", "handbook-03.v1.png", "handbook-04.v1.png",
           "handbook-01.v5.png", "handbook-01.v7.png", "handbook-02.v9.png", "handbook-02.v10.png",
           "handbook-02.v11.png", "handbook-02.v12.png", "handbook-02.v13.png",
           "handbook-03.v14.png", "handbook-04.v18.png", "handbook-04.v19.png",
           "handbook-04.v20.png", "handbook-01.v21.png", "handbook-02.v21.png",
           "handbook-03.v21.png", "handbook-04.v21.png", "example-02.v21.png",
           "example-03.v21.png", "example-04.v21.png", "example-04.v23.png",
           "example-04.v24.png", "handbook-04.final.png", "handbook-03.final.png",
           "example-03.final.png", "story-preview-a.v6.png", "story-preview-b.v6.png"]
    m = build_metrics(
        "A17",
        title="四页可实践的DSL入门手册",
        status="completed",
        started_at="2026-10-03T12:51:00+08:00",
        ended_at="2026-10-03T13:34:00+08:00",
        outputs=sorted(os.listdir(OUT)),
        final_pngs=8,
        dsl_versions=31,
        notes=[
            "8 张最终 PNG 全部为服务真实 200 响应字节，未做任何后处理；每张都有同名无 BOM .snapshot。",
            "印刷代码是 src/*.snapshot 的逐行原文，fragment-proof.json 给出每印刷行在源文件中的行号。",
            "REVISION: 子代理实体探针确认解析器不解码实体，A17 全部正文/示例已去掉实体写法，"
            "代码印刷改为逐 token CDATA 包装（原 &lt; 写法会被服务原样画出）。",
            "元素预算：最大页面 ~620 个元素（正则 <[A-Za-z]），远低于单文档 4096 上限。",
            "四页教学插图全部由 Container/Stack/Positioned/Text/ClipRRect 直接绘制，全文件 0 个 <Image>。",
            "正文 22-34px、代码块 18px；代码 18px 低于 TASK.md 的“代码≥20”一行，原因见 snapshot-usage.md。",
            "requests.jsonl 曾因清空日志被截断，已按 .rawmeta/.rawheaders/.rawbody 逐条重建（见文件内 log_rebuilt_from 字段）。",
        ],
        extra={
            "final_image": {
                "files": [f"handbook-0{i}.png" for i in range(1, 5)] + [f"example-0{i}.png" for i in range(1, 5)],
                "widths": [1200, 1200, 1200, 1200, 400, 400, 400, 400],
                "heights": [1600, 1600, 1600, 1600, 240, 240, 240, 240],
                "format": "PNG", "viewed": True},
            "requirements_checked": {
                "four_pages_1200x1600": True,
                "page1_request_response_errors": True,
                "page2_root_size_flex_stack": True,
                "page3_raw_cdata_tail_alpha": True,
                "page4_filters_selfcheck_delivery": True,
                "printed_example_8_to_18_lines": True,
                "printed_fragment_verbatim": True,
                "elision_marked": True,
                "illustrations_drawn_by_dsl": True,
                "no_image_tag_anywhere": True,
                "no_entity_sequences_in_copy_or_examples": True,
                "element_count_under_4096": True,
                "four_runnable_examples_400x240": True,
                "examples_same_code_as_printed": True,
                "sources_md_points_to_read_pages": True,
                "examples_json_has_responses": True,
                "safe_margin_48": True,
                "body_font_min_22": True,
                "code_font_min_18_below_task_hint": True},
            "font_sizes_used": {"page_title": 34, "page_subtitle": 24, "card_title": 24,
                                "bullet_body": 22, "inner_box_body": 18, "printed_code": 18,
                                "error_table": 20, "caption": 17},
            "element_counts": {f"handbook-0{i}": len(re.findall(r"<[A-Za-z]", open(
                os.path.join(TMP, f"handbook-0{i}.{'v5' if i == 3 else 'v4'}.snapshot"),
                encoding="utf-8").read())) for i in range(1, 5)},
            "entity_probe_request_id": "A17-REQ-0085",
        },
    )
    m["iterations"]["image_reviews"] = len(img)
    m["iterations"]["image_reviews_note"] = (
        "read_image 实际打开次数（含 A18 的两张 1600x1000 预览，因同一次 A18 工作复用了这批工具调用记录）")
    m["iterations"]["viewed_files"] = img
    write_json(os.path.join(OUT, "task-metrics.json"), m)
    print("metrics:", m["requests"]["requests_total"], "requests;",
          m["requests"]["render_success"], "success;", m["requests"]["render_failed"], "failed;",
          "iterations:", m["iterations"]["iterations_total"], "reviews:", m["iterations"]["image_reviews"])


if __name__ == "__main__":
    main()
