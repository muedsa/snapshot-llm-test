"""B02 收尾事实表：从真实日志与文件反查每题的版本数/请求数/看图数/定稿请求。

只读，不改任何交付物；输出 tmp/<run_id>/B02/facts.json 供 gallery/portfolio/metrics 生成用。
"""
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parents[3]
rid = "20261008T1615Z-run01"
temp = root / "tmp" / rid / "B02"
out = root / "outputs" / rid / "B02"


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


reqs = [json.loads(l) for l in (temp / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
iters = [json.loads(l) for l in (temp / "iterations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

# 只统计真实渲染请求（排除构件烟雾测试与字体/文档查询）
renders = [r for r in reqs if r.get("kind") == "render"]
by_case = {}
for r in renders:
    # 按响应文件所在目录归属，避免个别 request_id 漏写用例前缀时统计错位
    m = re.search(r"/(case-\d\d)[/.]", r.get("response_file") or "")
    if not m:
        continue
    by_case.setdefault(m.group(1), []).append(r)

cases = []
for i in range(1, 11):
    cid = "case-%02d" % i
    cd = out / cid
    arts = [a for a in ("final", "back") if (cd / (a + ".png")).exists()]
    size = None
    try:
        from PIL import Image
        size = list(Image.open(cd / (arts[0] + ".png")).size)
    except Exception:
        pass
    rs = by_case.get(cid, [])
    dig = md5(cd / (arts[0] + ".png"))
    fin = next((r for r in rs if r.get("raw_copy_file") and (root / r["raw_copy_file"]).exists()
                and md5(root / r["raw_copy_file"]) == dig), None)
    its = [x for x in iters if x.get("case_id") == cid]
    cm = (cd / "case.md").read_text(encoding="utf-8-sig")
    head = cm.splitlines()[0].lstrip("# ").strip()
    head = re.sub(r"^case-\d\d\s*·?\s*", "", head)
    title = head.split("·")[0].strip()
    cases.append({
        "id": cid,
        "title": title,
        "artifacts": arts,
        "dimensions": size,
        "png_bytes": (cd / (arts[0] + ".png")).stat().st_size,
        "png_md5": dig,
        "artifact_detail": [
            {"name": a,
             "bytes": (cd / (a + ".png")).stat().st_size,
             "md5": md5(cd / (a + ".png")),
             "size": list(Image.open(cd / (a + ".png")).size),
             "final_request_id": next((r["request_id"] for r in rs
                                       if r.get("raw_copy_file")
                                       and (root / r["raw_copy_file"]).exists()
                                       and md5(root / r["raw_copy_file"])
                                       == md5(cd / (a + ".png"))), None),
             "dsl_chars": len((cd / (a + ".snapshot")).read_text(encoding="utf-8"))}
            for a in arts],
        "dsl_chars": len((cd / (arts[0] + ".snapshot")).read_text(encoding="utf-8")),
        "final_request_id": fin["request_id"] if fin else None,
        "final_matched_by_md5": bool(fin),
        "server_render_ms": float(re.search(r"render;dur=([\d.]+)", fin["server_timing"]).group(1)) if fin else None,
        "requests": len(rs),
        "iterations_logged": len(its),
        "visual_iterations": len([x for x in its if x.get("kind") == "visual"]),
        "image_views": len([x for x in its if x.get("image_viewed_at")]),
        "content_fixes": len([x for x in its if x.get("kind") in ("content_fix", "syntax_fix")]),
        "versions": sorted({x["version"] for x in its if x.get("version") and x["version"] != "pre"}),
    })

facts = {
    "path_base": "suite_root",
    "run_id": rid, "task_id": "B02",
    "generated_at": datetime.utcnow().isoformat() + "+00:00",
    "total_render_requests": len(renders),
    "kit_smoke_requests": len([r for r in renders if "kit-smoke" in r["request_id"]]),
    "non_render_requests": len([r for r in reqs if r.get("kind") != "render"]),
    "failed_renders": [r["request_id"] for r in renders if r.get("http_status") != 200],
    "iteration_records": len(iters),
    "cases": cases,
}
(temp / "facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8")
for c in cases:
    print(c["id"], c["dimensions"], c["requests"], "it", c["iterations_logged"],
          "vis", c["visual_iterations"], "views", c["image_views"],
          "md5ok", c["final_matched_by_md5"], c["final_request_id"], "|", c["title"][:34])
print("renders", facts["total_render_requests"], "smoke", facts["kit_smoke_requests"],
      "non-render", facts["non_render_requests"], "failed", facts["failed_renders"])
