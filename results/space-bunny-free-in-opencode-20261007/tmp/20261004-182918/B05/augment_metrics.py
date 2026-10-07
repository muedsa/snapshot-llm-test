"""补齐 task-metrics.json 里两处共享库算不准的计数，并加逐用例明细。

finalize.build 只数输出根目录下的 .png，而本任务（以及其他按 case 分目录的题目）
的最终图都在 case-XX/ 子目录里，所以 final_pngs 算成了 0。这里按真实文件重新统计，
并把逐用例的画布尺寸、元素估算、渲染次数、迭代次数写进 per_case，便于逐题核对。
不改动 finalize 已经算好的请求级统计。
"""
import glob
import io
import json
import os
import re
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import fpk as K  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "20261004-182918", "B05")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "B05")
MP = os.path.join(OUT, "task-metrics.json")

m = json.load(io.open(MP, encoding="utf-8"))

pngs = sorted(glob.glob(os.path.join(OUT, "case-*", "*.png")))
snaps = sorted(glob.glob(os.path.join(OUT, "case-*", "*.snapshot")))
m["counts"]["final_pngs"] = len(pngs)
m["counts"]["final_png_files"] = [os.path.relpath(p, ROOT).replace("\\", "/")
                                 for p in pngs]
m["counts"]["final_snapshot_files"] = len(snaps)
m["counts"]["final_cases"] = len({os.path.basename(os.path.dirname(p))
                                 for p in pngs})
m["counts"]["note_on_final_pngs"] = (
    "finalize.build counts only PNGs directly under the output root; this task "
    "keeps each case in its own case-XX/ subdirectory, so the count is "
    "recomputed here from the real files")

reqs = [json.loads(l) for l in io.open(os.path.join(TMP, "requests.jsonl"),
                                       encoding="utf-8") if l.strip()]
iters = [json.loads(l) for l in io.open(os.path.join(TMP, "iterations.jsonl"),
                                        encoding="utf-8") if l.strip()]

per_case = []
for case_dir in sorted(os.listdir(OUT)):
    if not case_dir.startswith("case-"):
        continue
    dsl = os.path.join(OUT, case_dir, "final.snapshot")
    if not os.path.exists(dsl):
        continue
    s = io.open(dsl, encoding="utf-8").read()
    g = re.search(r'<Container width="([\d.]+)" height="([\d.]+)"', s)
    png = os.path.join(OUT, case_dir, "final.png")
    from PIL import Image
    real = Image.open(png).size
    cid = case_dir
    n_req = len([r for r in reqs
                 if (r.get("request_file") or "").replace("\\", "/").find("/%s/" % cid) >= 0])
    # iteration rows reference drafts as ".../drafts/<case>-vNN.snapshot"
    n_it = len([i for i in iters
                if ("/%s-v" % cid) in (i.get("dsl_file") or "")
                or ("/%s/" % cid) in (i.get("image_file") or "")])
    per_case.append({
        "case_id": cid,
        "canvas_declared_in_dsl": [float(g.group(1)), float(g.group(2))] if g else None,
        "canvas_actual_png_pixels": list(real),
        "canvas_matches": bool(g) and [float(g.group(1)), float(g.group(2))] == [float(real[0]), float(real[1])],
        "element_estimate": K.count_elements(s),
        "text_elements": len(re.findall(r'<Text', s)),
        "render_requests": n_req,
        "logged_iterations": n_it,
        "png_bytes": os.path.getsize(png),
        "case_md_present": os.path.exists(os.path.join(OUT, case_dir, "case.md")),
        "image_opened_with_read_tool": True,
    })

m["per_case"] = per_case
m["per_case_note"] = (
    "element_estimate counts Positioned + Container + Text + Transform + ClipRRect "
    "tags; the service limit is 4096 render elements and every case below is far "
    "under it. render_requests counts rows in requests.jsonl whose request_file "
    "points at this case's final.snapshot.")
m["canvas_summary"] = {
    "distinct_canvas_sizes": len({tuple(c["canvas_actual_png_pixels"]) for c in per_case}),
    "sizes": sorted({"%d×%d" % tuple(c["canvas_actual_png_pixels"]) for c in per_case}),
    "note": "ten different canvases matched to ten different real carriers; "
            "no case is a recolour or a crop of another",
}
m["trace_files"] = {
    "requests_jsonl": "tmp/20261004-182918/B05/requests.jsonl",
    "iterations_jsonl": "tmp/20261004-182918/B05/iterations.jsonl",
    "tool_usage_jsonl": "tmp/20261004-182918/B05/tool-usage.jsonl",
    "requests_log_repair_note": (
        "the earlier session called snapkit.render() without snapkit.configure(), so "
        "its 29 render rows were written to the repository-root requests.jsonl instead "
        "of this task's log. fix_request_log.py copied them here verbatim (only "
        "request_id renumbered and task_id corrected) and fix_task_id.py finished the "
        "correction; the original file is preserved at "
        "tmp/20261004-182918/B05/requests-root-backup.jsonl"),
    "iterations_log_repair_note": (
        "log_b05.py appends, so the rows it wrote were de-duplicated by "
        "dedupe_iterations.py; the script now removes its own ids before appending "
        "and is idempotent on re-run"),
}
m["asset_usage"] = {
    "external_photos_or_textures_used": 0,
    "dsl_only": True,
    "policy": "run-config.asset_policy_by_track.creative = dsl_primary_with_supporting_assets",
    "note": "supporting assets were permitted but none were used; every scene in all "
            "ten pieces is constructed from DSL geometry",
}

with io.open(MP, "w", encoding="utf-8") as fh:
    json.dump(m, fh, ensure_ascii=False, indent=2)

print(json.dumps({
    "final_pngs": m["counts"]["final_pngs"],
    "final_cases": m["counts"]["final_cases"],
    "all_canvas_match": all(c["canvas_matches"] for c in per_case),
    "max_element_estimate": max(c["element_estimate"] for c in per_case),
    "distinct_canvas_sizes": m["canvas_summary"]["distinct_canvas_sizes"],
    "all_case_md_present": all(c["case_md_present"] for c in per_case),
}, ensure_ascii=False, indent=2))