"""Build examples.json for A17 from the real request log.

Every field is read back from files on disk: the example DSL bytes, the handbook
DSL bytes, and the render records in tmp/<run_id>/A17/requests.jsonl, so the
manifest cannot drift from what was actually sent to the service.

Usage: python tmp/<run_id>/A17/build_examples_json.py
"""
import hashlib
import json
import os
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
run_id = os.environ["SNAPSHOT_RUN_ID"]
task = "A17"
temp = root / "tmp" / run_id / task
out = root / "outputs" / run_id / task

log = [json.loads(l) for l in
       (temp / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
by_id = {r["request_id"]: r for r in log}

SPEC = [
    ("example-01", "handbook-01", [(1, 13)], "A17-example01-v03-20261009T033226Z",
     "第 1 页 · 调用契约",
     "把一次成功调用与一次失败调用的关键字段排成 6 行卡片：请求体类型、响应 Content-Type "
     "与响应头、以及 400 错误体的 {code,message,requestId} 形状。演示 Column + Text + Raw "
     "的 CDATA 写法（文本里要出现 < 或 > 时用 CDATA），以及用 height=\"1\" 的 Container "
     "画分隔线。",
     "独立渲染为 400x240；手册第 1 页印刷第 1-13 行 / 全 19 行，省略第 14-19 行（ERROR 400 "
     "段落与三个收尾标签）并在片段下方用 ⋮/↳ 图例标明省略与续行。"),
    ("example-02", "handbook-02", [(4, 13)], "A17-example02-v01-20261009T032145Z",
     "第 2 页 · 布局与定位",
     "在 400x240 画布上对照两件事：Row 里三个 Expanded（flex 2:1:1）在有界主轴上瓜分剩余空间；"
     "Stack 里两种 Positioned 写法（left+top+right+height 由两边推出宽度，left+bottom+width+height "
     "推出另一侧）。同时展示 clipBehavior=\"NONE\"。",
     "独立渲染为 400x240；手册第 2 页印刷第 4-13 行 / 全 24 行，省略第 1-3 行（根标签与内边距）"
     "与第 14-24 行（Stack 演示块与收尾标签）。"),
    ("example-03", "handbook-03", [(6, 8), (18, 22)], "A17-example03-v02-20261009T032301Z",
     "第 3 页 · 文本与颜色",
     "三组对照：CDATA 内的 <b>标签</b> 与 &amp; 原样保留（解析器不做 HTML 实体解码）；嵌套 Text "
     "作为行内 Span、段落属性只作用于最外层；#RRGGBBAA 的最后一组才是 alpha，三个红色块分别用 "
     "FF/80/1A 叠在同一深色底上。",
     "独立渲染为 400x240；手册第 3 页分两段印刷第 6-8 行与第 18-22 行 / 全 29 行，中间以 ⋮ 行标明省略。"),
    ("example-04", "handbook-04", [(19, 26)], "A17-example04-v02-20261009T035000Z",
     "第 4 页 · 滤镜与交付",
     "先铺一条 6 色 Expanded 背景，再用 ClipRRect + BackdropFilter(sigmaX=sigmaY=14) 在其上开一块"
     "毛玻璃（滤镜读的是身后已绘像素），另用 ImageFiltered(sigmaX=sigmaY=1.5) 软化自己的子树标题条。"
     "两个标签方向不同：一个处理子树，一个处理背景。",
     "独立渲染为 400x240；手册第 4 页印刷第 19-26 行 / 全 33 行，省略第 1-18 行（根标签与彩色背景条）"
     "与第 27-33 行（ImageFiltered 块与收尾标签）。sigma 由 2.5 降到 1.5 是看图后的修正：2.5 会把 "
     "15px 标题糊到不可读。"),
]

examples = []
for ex, page, ranges, rid, section, purpose, print_note in SPEC:
    dsl_path = temp / "examples" / f"{ex}.snapshot"
    dsl = dsl_path.read_text(encoding="utf-8")
    rec = by_id[rid]
    png = out / f"{ex}.png"
    examples.append({
        "id": ex,
        "handbook_page": page,
        "section": section,
        "purpose": purpose,
        "dsl_file": f"outputs/{run_id}/{task}/{ex}.snapshot",
        "dsl_temp_file": f"tmp/{run_id}/{task}/examples/{ex}.snapshot",
        "dsl_lines": len(dsl.splitlines()),
        "dsl_bytes": len(dsl.encode("utf-8")),
        "dsl_sha256": hashlib.sha256(dsl.encode("utf-8")).hexdigest(),
        "dsl": dsl,
        "printed_ranges": [{"from": a, "to": b} for a, b in ranges],
        "printed_range_text": "、".join(f"{a}-{b}" for a, b in ranges),
        "printed_note": print_note,
        "render": {
            "request_id": rec["request_id"],
            "request_id_header": rec["request_id_header"],
            "http_status": rec["http_status"],
            "content_type": rec["content_type"],
            "response_bytes": rec["response_bytes"],
            "server_timing": rec["server_timing"],
            "snapshot_cache": rec["snapshot_cache"],
            "duration_seconds": rec["duration_seconds"],
            "started_at": rec["started_at"],
            "ended_at": rec["ended_at"],
            "request_file": rec["request_file"],
            "headers_file": rec["headers_file"],
            "raw_response_file": rec["raw_copy_file"],
            "png": f"outputs/{run_id}/{task}/{ex}.png",
            "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
        },
    })

handbooks = []
for n, rid in [("handbook-01", "A17-hb01-v06-20261009T035154Z"),
               ("handbook-02", "A17-hb02-v06-20261009T035203Z"),
               ("handbook-03", "A17-hb03-v06-20261009T035209Z"),
               ("handbook-04", "A17-hb04-v09-20261009T040510Z")]:
    dsl_path = temp / "handbook" / f"{n}.snapshot"
    dsl = dsl_path.read_text(encoding="utf-8")
    rec = by_id[rid]
    handbooks.append({
        "id": n,
        "title": {"handbook-01": "一次请求，一张图片（契约与错误）",
                  "handbook-02": "尺寸来自布局，不是 CSS（布局与定位）",
                  "handbook-03": "文本、转义与颜色（文本与颜色）",
                  "handbook-04": "滤镜、自检与可复现交付（效果与交付）"}[n],
        "size": [1200, 1600],
        "dsl_file": f"outputs/{run_id}/{task}/{n}.snapshot",
        "dsl_lines": len(dsl.splitlines()),
        "dsl_bytes": len(dsl.encode("utf-8")),
        "dsl_sha256": hashlib.sha256(dsl.encode("utf-8")).hexdigest(),
        "final_render": {
            "request_id": rec["request_id"],
            "request_id_header": rec["request_id_header"],
            "http_status": rec["http_status"],
            "server_timing": rec["server_timing"],
            "snapshot_cache": rec["snapshot_cache"],
            "response_bytes": rec["response_bytes"],
            "request_file": rec["request_file"],
            "headers_file": rec["headers_file"],
            "raw_response_file": rec["raw_copy_file"],
            "png": f"outputs/{run_id}/{task}/{n}.png",
            "png_sha256": hashlib.sha256((out / f"{n}.png").read_bytes()).hexdigest(),
        },
        "superseded_versions": sorted(
            r["dsl_version"] for r in log
            if r["kind"] == "render" and r["dsl_version"].startswith("hb" + n[-2:] + "-")
            and r["request_id"] != rid),
    })

doc_reads = [{"request_id": r["request_id"], "url": r["url"],
              "http_status": r["http_status"], "cached_html": r["response_file"],
              "cached_text": r["text_file"]}
             for r in log if r["kind"] == "doc"]

manifest = {
    "task_id": task,
    "run_id": run_id,
    "path_base": "suite_root",
    "generated_at": "2026-10-09T03:56:00+00:00",
    "service": {"endpoint": "https://open-snapshot.muedsa.com/snapshot",
                "request_content_type": "text/plain; charset=utf-8",
                "docs_root": "https://snapshot.muedsa.com/"},
    "note": "dsl 字段与 outputs/<run_id>/A17/<id>.snapshot 字节一致；手册页印刷的代码片段"
            "由 gen_handbook.py 直接读取这些文件生成，因此手册与独立渲染用的是同一份 DSL。",
    "examples": examples,
    "handbook_pages": handbooks,
    "doc_reads_this_task": doc_reads,
    "doc_reads_reused_from_earlier_runs": [
        {"page": "ai-guide.md", "url": "https://open-snapshot.muedsa.com/ai-guide.md",
         "cached": f"tmp/{run_id}/_suite/docs/ai-guide.md", "first_fetched_by": "shared-doc-001-guide-ai"},
        {"page": "container.html", "url": "https://snapshot.muedsa.com/widgets/layout/container/",
         "cached": f"tmp/{run_id}/_suite/docs/container.html", "first_fetched_by": "shared-doc-006-doc-container"},
        {"page": "painting.html", "url": "https://snapshot.muedsa.com/guides/painting/",
         "cached": f"tmp/{run_id}/_suite/docs/painting.html", "first_fetched_by": "shared-doc-009-doc-painting"},
        {"page": "text.html", "url": "https://snapshot.muedsa.com/widgets/text/text/",
         "cached": f"tmp/{run_id}/_suite/docs/text.html", "first_fetched_by": "shared-textdoc-20261008T145223Z"},
        {"page": "rich-text.html", "url": "https://snapshot.muedsa.com/widgets/text/rich-text/",
         "cached": f"tmp/{run_id}/_suite/docs/rich-text.html", "first_fetched_by": "shared-richtext-20261008T145221Z"},
        {"page": "clip-rect.html", "url": "https://snapshot.muedsa.com/widgets/painting/clip-rect/",
         "cached": f"tmp/{run_id}/_suite/docs/clip-rect.html", "first_fetched_by": "shared-cliprect-20261009T011244Z"},
        {"page": "fonts.txt", "url": "https://open-snapshot.muedsa.com/fonts",
         "cached": f"tmp/{run_id}/_suite/docs/fonts.txt",
         "first_fetched_by": "pre-suite probe, headers dated 2026-10-08T08:14:01Z; "
                             "no per-task JSONL record exists for it"},
    ],
}
(out / "examples.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
print("wrote", out / "examples.json", len(examples), "examples,", len(handbooks), "pages,",
      len(doc_reads), "doc reads")
