"""A14: append the audit/support iterations, then build task-metrics.json."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(ROOT / "tmp" / RID / "_suite" / "scripts"))
TEMP = ROOT / "tmp" / RID / "A14"
OUT = ROOT / "outputs" / RID / "A14"
IL = TEMP / "iterations.jsonl"
REQS = [json.loads(l) for l in (TEMP / "requests.jsonl").read_text(encoding="utf-8")
        .splitlines() if l.strip()]
LAST = {r["dsl_version"]: r for r in REQS}


def add(rec):
    """Append one iteration record unless its id is already on disk (rerun-safe)."""
    have = set()
    if IL.exists():
        have = {json.loads(l)["iteration_id"] for l in
                IL.read_text(encoding="utf-8").splitlines() if l.strip()}
    if rec["iteration_id"] in have:
        return
    with IL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def base(iid, version, cid, itype, **kw):
    r = LAST[f"{version}-{cid}"]
    rec = {"iteration_id": iid, "task_id": "A14", "version_id": f"{version}-{cid}",
           "type": itype, "viewed": False, "image_path": None,
           "image_viewed_at": None, "completed": False,
           "request_id": r["request_id"], "path_base": "suite_root"}
    rec.update(kw)
    add(rec)


base("A14-audit-01", "v02", "K01", "syntax-fix", parent="A14-visual-K01",
     requirement_part="batch-audit.json 的像素行数核对",
     observed_problems="check_a14.py 首跑 AttributeError：groups() 把当前组写成了整数",
     changes="groups() 改为统一用列表累积", result="脚本可运行，但仍有假阴性",
     completed=False)
base("A14-audit-02", "v02", "K03", "syntax-fix", parent="A14-audit-01",
     requirement_part="batch-audit.json 的像素行数核对",
     observed_problems="11 项失败：ink_rows 把三通道求和与单通道阈值比较（每行都算深色，"
                       "所有卡都报 1 行）；徽标符号断言用小写 'radius=\"'，DSL 实际是 "
                       "borderRadius（大写 R），永不匹配",
     changes="改用 mean(axis=2) < thr；断言串改 borderRadius；标题扫描带改为盒外扩 12px "
             "以检测越界", result="170/170 通过，八张实渲行数与计划一致", completed=False)
base("A14-audit-03", "v02", "K01", "alternative", parent="A14-audit-02",
     requirement_part="允许另做接触表检查一致性（不得替代八张原图）",
     observed_problems="无", changes="tmp/<rid>/A14/preview/contact-sheet-v02.png 半尺寸 2x4 "
             "拼版并查看：八张共用主色/导轨/页脚/条状母题，四种状态编码互不相同",
     result="已查看接触表；一致性确认仍以八张原图的逐张查看为准",
     completed=False, viewed=True,
     image_path="tmp/%s/A14/preview/contact-sheet-v02.png" % RID,
     image_viewed_at="2026-10-09T01:38:58+00:00")

# ---- metrics ------------------------------------------------------------------------
def iso(t):
    return datetime.fromisoformat(t)


stamps = [iso(r["started_at"]) for r in REQS] + [iso(r["ended_at"]) for r in REQS]
arts = []
for p in list(OUT.rglob("*")) + list(TEMP.rglob("*")):
    if p.is_file():
        arts.append(datetime.fromtimestamp(p.stat().st_mtime, timezone.utc))
t0, t1 = min(min(stamps), min(arts)), max(max(stamps), max(arts))
GAP = 300
seq = sorted(stamps)
gaps = [{"from": a.astimezone(timezone.utc).isoformat(),
         "to": b.astimezone(timezone.utc).isoformat(),
         "seconds": round((b - a).total_seconds(), 1)}
        for a, b in zip(seq, seq[1:]) if (b - a).total_seconds() > GAP]
idle = sum(g["seconds"] for g in gaps)
wall = (t1 - t0).total_seconds()
req_sec = round(sum(r["duration_seconds"] for r in REQS), 3)
iters = [json.loads(l) for l in IL.read_text(encoding="utf-8").splitlines() if l.strip()]
views = [i for i in iters if i.get("image_viewed_at")]
audit = json.loads((OUT / "batch-audit.json").read_text(encoding="utf-8"))
extra = {
    "started_at": t0.astimezone(timezone.utc).isoformat(),
    "ended_at": t1.astimezone(timezone.utc).isoformat(),
    "timings": {
        "wall_clock_seconds": round(wall, 1),
        "active_seconds": round(wall - idle, 1),
        "idle_gap_seconds": round(idle, 1),
        "idle_gaps": gaps,
        "request_seconds_total": req_sec,
        "first_image_seconds": round((iso(REQS[0]["ended_at"]) - t0).total_seconds(), 1),
        "method": "wall = first(artifact mtime, request) -> last(same); idle = gaps > "
                  "300 s between logged events; request sums overlap and are NOT the wall",
    },
    "counts": {
        "render_requests": len(REQS),
        "requests_total": len(REQS),
        "requests_success": sum(1 for r in REQS if r["http_status"] == 200),
        "requests_failed": sum(1 for r in REQS if r["http_status"] != 200),
        "retries": 0,
        "dsl_versions": 2,
        "image_views": len(views),
        "visual_iterations": sum(1 for i in iters if i["type"] == "visual"
                                 and i["completed"]),
        "iterations_logged": len(iters),
        "final_images": 8,
    },
    "counts_detail": {
        "audit_checks": f'{audit["checks_passed"]}/{audit["checks_total"]}',
        "audit_failed": [c["name"] for c in audit["checks"] if not c["ok"]],
        "cards_per_grid": {"A": 8, "B": 0},
        "title_sizes": {r["id"]: [r["title_size"], r["title_lines_planned"],
                                  r["title_ink_lines"]] for r in audit["cards"]},
        "statuses": {"开放": 4, "满额": 1, "候补": 2, "取消": 1},
        "service_errors": 0,
        "generator_problems": audit["problems_from_generator"],
    },
    "outputs": {
        "final_pngs": sorted(p.name for p in OUT.glob("card-*.png")),
        "final_dsls": sorted(p.name for p in OUT.glob("card-*.snapshot")),
        "served_by": {r["dsl_version"]: r["request_id"] for r in REQS
                      if r["dsl_version"].startswith("v02-")},
        "extra_files": ["batch-audit.json", "snapshot-usage.md", "task-metrics.json"],
    },
    "stop_reason": "all eight cards rendered, viewed and audited 170/170",
    "unresolved_issues": [
        "grid B 规则存在但本批 8 条数据在 36pt 下限内都能放进 grid A，从未触发；"
        "该分支只经过代码路径检查（bars_h/顶栏），没有对应的实渲样本",
        "v01 的八张 PNG 被 v02 就地覆盖，只有 requests/*.response.bin 与 "
        "preview/v01/*.png 保留了原始字节",
    ],
}
(TEMP / "metrics-extra.json").write_text(json.dumps(extra, ensure_ascii=False),
                                         encoding="utf-8")
cmd = [sys.executable, str(ROOT / "tmp" / RID / "_suite" / "scripts" / "build_metrics.py"),
       "--task", "A14", "--status", "completed",
       "--started", extra["started_at"],
       "--first-image", REQS[0]["ended_at"],
       "--stop-reason", extra["stop_reason"],
       "--unresolved", " ; ".join(extra["unresolved_issues"]),
       "--extra", str(TEMP / "metrics-extra.json")]
p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
print(p.returncode, p.stdout[-500:], p.stderr[-800:])
