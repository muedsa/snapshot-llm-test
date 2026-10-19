# -*- coding: utf-8 -*-
"""套件初始化：合并 SHARED 日志到 _suite，写入 suite-state.json 初始状态
与 docs-index.json、events.jsonl。启动基准：总任务根。"""
import json, os, sys, shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

RUN = sc.RUN_ID
suite_out = sc.suite_out()
suite_tmp = sc.suite_tmp()
sq_tmp = suite_tmp / "_suite"
sq_out = suite_out / "_suite"
sq_tmp.mkdir(parents=True, exist_ok=True)
sq_out.mkdir(parents=True, exist_ok=True)

# 1) 合并 SHARED 请求日志
old = suite_tmp / "SHARED" / "requests.jsonl"
merged = sq_tmp / "shared-requests.jsonl"
if old.exists():
    rows = [l for l in old.read_text(encoding="utf-8").splitlines() if l.strip()]
    if merged.exists():
        rows2 = [l for l in merged.read_text(encoding="utf-8").splitlines() if l.strip()]
        have = {json.loads(r)["id"] for r in rows2}
        rows = [l for l in rows if json.loads(l)["id"] not in have]
        rows2.extend(rows)
        rows = rows2
    merged.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    for r in rows:
        pass
    shutil.rmtree(suite_tmp / "SHARED", ignore_errors=True)
    print(f"merged shared-requests: {len(rows)} records -> {merged}")

# 2) docs-index.json：文档缓存清单（path_base=suite_root）
docs = sq_tmp / "docs-index.json"
docs_dir = sq_tmp / "docs"
idx = {
    "schema_version": 1,
    "path_base": "suite_root",
    "cache_dir": f"tmp/{RUN}/_suite/docs",
    "note": "已下载文档缓存；原请求保存在 tmp/<run_id>/_suite/renders 由 fetch_url 记录的 response_* 指向 docs/*.raw",
    "documents": [
        {"url": "https://open-snapshot.muedsa.com/ai-guide.md", "file": "tmp/20261016T164020-m1/_suite/docs/ai-guide.md",
         "title": "Open Snapshot AI 使用指南", "role": "服务接口规范"},
        {"url": "https://snapshot.muedsa.com/", "file": "tmp/20261016T164020-m1/_suite/docs/root-index.md",
         "title": "Snapshot 文档总览", "role": "导航"},
        {"url": "https://open-snapshot.muedsa.com/fonts", "file": "tmp/20261016T164020-m1/_suite/docs/fonts-list.txt",
         "title": "服务已安装字体(GET /fonts)", "role": "字体清单"},
    ],
    "docs_pages_fetched": sorted(p.name for p in (suite_tmp / "docs").glob("*.raw")),
    "families_used": ["Inter", "Noto Sans CJK SC", "Noto Serif CJK SC", "Noto Sans Mono CJK SC", "Noto Color Emoji"],
}
# 把指南保存为文档缓存
guide = sq_tmp / "docs" / "ai-guide.md"
if not guide.exists():
    import urllib.request
    st, ct, data2, rec = sc.fetch_url("SHARED", "document", "https://open-snapshot.muedsa.com/ai-guide.md",
                                      guide, timeout=60)
guide.write_text(open(guide, "rb").read().decode("utf-8"), encoding="utf-8") if False else None
docs.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")

# 3) suite-state.json 初始状态
state = {
    "schema_version": 1,
    "path_base": "suite_root",
    "suite_version": "1.0.0",
    "run_id": RUN,
    "profile": "all",
    "status": "in_progress",
    "started_at": "2026-10-16T16:40:20+08:00",
    "updated_at": sc.now_iso(),
    "current_task": "A01",
    "current_round": None,
    "current_case": None,
    "last_checkpoint": None,
    "task_order_order": ["A01","A02","A03","A04","A05","A06","A07","A08","A09","A10",
                          "A11","A12","A13","A14","A15","A16","A17","A18","A19","A20",
                          "A21","A22","A23","A24","B01","B02","B03","B04","B05","B06"],
    "tasks": [
        {"id": t, "status": "pending", "started_at": None, "ended_at": None,
         "output_dir": f"outputs/{RUN}/{t}/", "temp_dir": f"tmp/{RUN}/{t}/",
         "completed_rounds": [], "completed_cases": [], "artifacts": [],
         "visual_review_evidence": [], "unresolved_issues": [], "resume_notes": None}
        for t in ["A01","A02","A03","A04","A05","A06","A07","A08","A09","A10",
                  "A11","A12","A13","A14","A15","A16","A17","A18","A19","A20",
                  "A21","A22","A23","A24","B01","B02","B03","B04","B05","B06"]],
    "suite_artifacts": [],
}
sq_out.joinpath("suite-state.json").write_text(
    json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

# 4) events.jsonl 首条
ev = sq_tmp / "events.jsonl"
ev.write_text(json.dumps({
    "id": f"SUITE-ev-{sc.count_lines(ev)+1:06d}",
    "at": sc.now_iso(),
    "kind": "suite_start",
    "detail": {"run_id": RUN, "profile": "all", "service_base": sc.SERVICE_BASE,
               "gitignore": ".gitignore", "shared_docs_cached": idx["cache_dir"]},
}, ensure_ascii=False) + "\n", encoding="utf-8")

# 5) 第一次检查点
cp = sq_tmp / "checkpoints"
cp.mkdir(exist_ok=True)
cp.joinpath("state-000001.json").write_text(json.dumps({
    "checkpoint": 1, "at": sc.now_iso(), "note": "suites initialized; docs cached; A01 未开始",
    "current_task": "A01",
}, ensure_ascii=False), encoding="utf-8")

print("suite-state initialized at", sq_out / "suite-state.json")
print("events at", ev)
