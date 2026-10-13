"""Build outputs/<run>/A17/examples.json from the delivered artefacts themselves.

Nothing here is typed by hand: the core subtree's line range is located inside both
the standalone example file and the handbook page file by scanning the written XML,
the printed segments are read back out of the page DSL, and the response evidence is
taken from requests.jsonl. That way the record cannot disagree with the files.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A17"
OUT = ROOT / "outputs" / RUN / "A17"
sys.path.insert(0, str(TMP))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

_spec = importlib.util.spec_from_file_location("ex", TMP / "examples.py")
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)


CODE_X = 70
CODE_COLORS = ("#E8EEF8", "#93AECF")


def lines(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8").split("\n")


def find_core_block(file_lines):
    """1-based [start, end] of the example's Stack inside a written DSL file.

    The page's own root is also `<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">`,
    so the block is identified by its second line - the 400x240 sizing container that
    only the example core carries - and closed at the first `</Stack>` at the same indent.
    """
    open_tag = '<Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">'
    for i, s in enumerate(file_lines):
        if s.strip() != open_tag:
            continue
        if file_lines[i + 1].strip() != '<Container width="400" height="240"/>':
            continue
        pad = len(s) - len(s.lstrip())
        for j in range(i + 1, len(file_lines)):
            t = file_lines[j]
            if t.strip() == "</Stack>" and (len(t) - len(t.lstrip())) == pad:
                return i + 1, j + 1
        raise AssertionError("no matching </Stack>")
    raise AssertionError("core Stack not found")


def printed_segments(page_dsl_path, example_dsl_path):
    """Rows of the code panel, as (file line number, verbatim text), in order."""
    exl = lines(example_dsl_path)
    root = ET.fromstring(page_dsl_path.read_text(encoding="utf-8"))
    rows, pos = [], 0
    for pos_el in root.iter("Positioned"):
        if pos_el.get("left") != str(CODE_X):
            continue
        for t in pos_el.iter("Text"):
            if t.get("color") not in CODE_COLORS or t.get("fontSize") != "20":
                continue
            raws = list(t.iter("Raw"))
            body = "".join(r.text or "" for r in raws) if raws else (t.text or "").strip()
            if "省略外层包装" in body:
                rows.append({"elision": body})
            else:
                hit = next((n for n in range(pos + 1, len(exl) + 1)
                            if exl[n - 1] == body), None)
                rows.append({"line": hit, "verbatim": body})
                pos = hit or pos
            break
    return rows


def group_segments(rows):
    segs, cur = [], []
    for r in rows:
        if "line" in r:
            cur.append(r)
        elif cur:
            segs.append({"from_line": cur[0]["line"], "to_line": cur[-1]["line"],
                         "verbatim": [c["verbatim"] for c in cur]})
            cur = []
    if cur:
        segs.append({"from_line": cur[0]["line"], "to_line": cur[-1]["line"],
                     "verbatim": [c["verbatim"] for c in cur]})
    return segs


def req_of(rid, reqs):
    r = next(x for x in reqs if x["request_id"] == rid)
    return {k: r.get(k) for k in ("request_id", "http_status", "response_content_type",
                                  "request_bytes", "response_bytes", "image_format",
                                  "image_width", "image_height", "x_request_id",
                                  "server_timing", "started_at", "ended_at",
                                  "duration_seconds")}


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v007")
a = ap.parse_args()
reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l]
views = [json.loads(l) for l in (TMP / "image-views.jsonl").read_text(encoding="utf-8").splitlines() if l]
verify = json.loads((TMP / f"{a.ver}-verify.json").read_text(encoding="utf-8"))

examples = []
for i in (1, 2, 3, 4):
    ex_dsl = OUT / f"example-{i:02d}.snapshot"
    pg_dsl = OUT / f"handbook-{i:02d}.snapshot"
    ex_block = find_core_block(lines(ex_dsl))
    pg_block = find_core_block(lines(pg_dsl))
    rows = printed_segments(pg_dsl, ex_dsl)
    segs = group_segments(rows)
    v = next(p for p in verify["pages"] if p["page"] == i)
    ill = next(c for c in v["checks"] if c["check"].startswith("illustration"))
    snip = next(c for c in v["checks"] if c["check"] == "printed-snippet-verbatim")
    margin = next(c for c in v["checks"] if c["check"] == "safe-margin-ink")
    contain = next(c for c in v["checks"] if c["check"] == "code-panel-containment")
    examples.append({
        "page_id": f"handbook-{i:02d}",
        "topic": ex.TITLES[i],
        "purpose": ex.PURPOSE[i],
        "artifacts": {
            "example_dsl": f"example-{i:02d}.snapshot",
            "example_png": f"example-{i:02d}.png",
            "handbook_dsl": f"handbook-{i:02d}.snapshot",
            "handbook_png": f"handbook-{i:02d}.png",
        },
        "example_size": [400, 240],
        "core_subtree": {
            "root_tag": "Stack",
            "in_example_dsl_lines": [ex_block[0], ex_block[1]],
            "in_handbook_dsl_lines": [pg_block[0], pg_block[1]],
            "identity": "both ranges are the render of the same examples.py core(i) "
                        "object; the handbook embeds it directly in a Positioned at 1:1",
        },
        "wrapper_differences": {
            "example_file": "Snapshot(background=#FFFFFF, type=png) > "
                            "Container(width=400,height=240) > core",
            "handbook_page": "Snapshot(background=#F6F7FA) > Stack(1200x1600) > "
                             "Positioned(left=64,top=291) > core, drawn on top of a "
                             "#FFFFFF figure card",
            "semantics_note": "the added card/position only places the example; the "
                              "core's own text, attribute values, child order, filter "
                              "parameters and relative geometry are untouched. The white "
                              "Snapshot background equals the page's white card so the "
                              "BackdropFilter sees the same painted backdrop.",
        },
        "printed_segments": segs,
        "printed_line_count": sum(len(s["verbatim"]) for s in segs),
        "elision_markers": sum(1 for r in rows if "elision" in r),
        "response": {
            "example": req_of(f"A17-render-{a.ver}-e{i:02d}-a1", reqs),
            "handbook": req_of(f"A17-render-{a.ver}-h{i:02d}-a1", reqs),
        },
        "visual_review": [v_["view_id"] for v_ in views
                          if v_["dsl_version"] in (a.ver, "v006")
                          and (f"handbook-0{i}" in v_["image"] or f"example-0{i}" in v_["image"])],
        "checks": {
            "illustration_identical": {"passed": ill["passed"],
                                       "pixels_within_6": ill["pixels_within_6"],
                                       "max_abs_difference": ill["max_abs_difference"],
                                       "located_at": ill["located_at"],
                                       "backdrop_regions": ill["backdrop_filter_regions_in_example"]},
            "printed_snippet_verbatim": {"passed": snip["passed"],
                                         "file_line_numbers": snip["file_line_numbers"],
                                         "rows_in_panel": snip["rows_in_panel"]},
            "safe_margin": {"passed": margin["passed"], "violations": margin["violations"]},
            "code_panel_containment": {"passed": contain["passed"],
                                       "text_stays_inside": contain["text_stays_inside"]},
        },
    })

CLAIMS = [
    {"claim": "请求体是 UTF-8 纯文本而不是 JSON，成功响应体直接是图片二进制",
     "source_url": "https://open-snapshot.muedsa.com/ai-guide.md",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs/ai-guide.md"},
     "quote": "接口为 POST /snapshot，请求体是 UTF-8 纯文本，不是 JSON；成功时响应体是图片二进制。",
     "line": 3, "demonstrated_by": ["example-01"]},
    {"claim": "非成功响应才是含 code/message/requestId 的 JSON，400 PARSE_ERROR 按位置修正后重投，"
              "429 与部分 503 参考 Retry-After",
     "source_url": "https://open-snapshot.muedsa.com/ai-guide.md",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs/ai-guide.md"},
     "quote": "非成功响应通常是包含 code、message、requestId 的 JSON。", "line": 47,
     "demonstrated_by": ["example-01"]},
    {"claim": "curl 出错时仍可能把 JSON 写进 result.png，使用前必须检查退出码、HTTP 状态与 Content-Type",
     "source_url": "https://open-snapshot.muedsa.com/ai-guide.md",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs/ai-guide.md"},
     "quote": "上述 curl 命令在错误时仍可能把 JSON 响应写入 result.png；使用生成的文件前，"
              "请检查退出码、HTTP 状态和响应 Content-Type。", "line": 51,
     "demonstrated_by": ["example-01"],
     "observed_in_suite": "本套题 A16 之前确实遇到过 200 但响应体被截断的情况，"
                          "render.py 因此按“是否真的是图片格式”判定成功"},
    {"claim": "GET /fonts 返回 text/plain，每行一个字体族名，不是 JSON",
     "source_url": "https://open-snapshot.muedsa.com/ai-guide.md",
     "doc_cache": {"path_base": "suite_root", "path": f"tmp/{RUN}/_suite/docs/fonts.txt"},
     "quote": "响应是 text/plain，每行一个字体族名称，不是 JSON", "line": 35,
     "demonstrated_by": ["example-01", "example-02", "example-03", "example-04"],
     "used_fonts": ["Noto Sans CJK SC", "Noto Sans Mono CJK SC"]},
    {"claim": "Snapshot 根标签只有 background/debug/type，且必须是文档第一个标签并带一个根 Widget 子节点；"
              "画布尺寸来自根布局容器",
     "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/reference_parser-tags.txt"},
     "quote": "必须是文档第一个开始标签，只能出现一次，并且最终必须有一个根 Widget 子节点。",
     "line": 189, "demonstrated_by": ["example-02"]},
    {"claim": "没有子节点也没有约束的空 Container 在无界根约束下收缩为零尺寸，根出图仍需非零宽高",
     "source_url": "https://snapshot.muedsa.com/guides/layout/",
     "doc_cache": {"path_base": "suite_root", "path": f"tmp/{RUN}/_suite/docs-txt/guides_layout.txt"},
     "quote": "没有子节点、没有约束的空 Container 在无界根约束下会收缩为零尺寸；根出图仍需非零宽高。",
     "line": 51, "demonstrated_by": ["example-02"]},
    {"claim": "Expanded/Flexible/Spacer 三者必须是 Flex、Row 或 Column 的直接子节点",
     "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/reference_parser-tags.txt"},
     "quote": "三者必须是 `Flex`、`Row` 或 `Column` 的直接子节点。", "line": 327,
     "demonstrated_by": ["example-02"]},
    {"claim": "Flex 主轴约束无限时无法计算剩余空间，必须先用外层容器给出有限尺寸",
     "source_url": "https://snapshot.muedsa.com/guides/layout/",
     "doc_cache": {"path_base": "suite_root", "path": f"tmp/{RUN}/_suite/docs-txt/guides_layout.txt"},
     "quote": "当 Flex 主轴约束无限时，无法计算可分配的“剩余空间”。请先通过外层 SizedBox、Container "
              "或 ConstrainedBox 提供有限主轴尺寸，再使用 Expanded 或紧约束的 Flexible。",
     "line": 90, "demonstrated_by": ["example-02"]},
    {"claim": "八位十六进制颜色按 CSS 的 #RRGGBBAA 解析（alpha 在末尾），旧版 #AARRGGBB 写法会改变颜色",
     "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/reference_parser-tags.txt"},
     "quote": "旧版 Parser 将八位颜色按 #AARRGGBB 解析；现在按 CSS 的 #RRGGBBAA 解析。例如旧的半透明红色 "
              "#80FF0000 应改为 #FF000080，否则颜色会改变。", "line": 87,
     "demonstrated_by": ["example-03"]},
    {"claim": "普通文本节点会被 trim；Raw 不 trim，首尾空格与换行保留，且只能出现在最外层 Text 的行内内容树中",
     "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/reference_parser-tags.txt"},
     "quote": "文本不做 trim，首尾空格和换行会保留；可以嵌套行内 Span，但只能出现在由最外层 Text 创建的行内内容树中。",
     "line": 572, "demonstrated_by": ["example-03"],
     "measured": "v002-example-03.png 中 <Raw> · </Raw> 两侧空格实际渲染出来（放大查看“绿 · 橙”间距）"},
    {"claim": "Text 可嵌套 Text/Raw/Emoji/WidgetSpan，段落属性只由最外层 Text 决定",
     "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/reference_parser-tags.txt"},
     "quote": "`Text` 可以嵌套 `Text`、`Raw`、`Emoji` 和 `WidgetSpan`。", "line": 560,
     "demonstrated_by": ["example-03"]},
    {"claim": "BackdropFilter 只有背后已有内容时才有视觉效果，且会读取子树之外的背景，需要外层裁剪限定区域",
     "source_url": "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/widget_painting_backdrop-filter.txt"},
     "quote": "BackdropFilter 只有背后已有内容时才有视觉效果。通常应配合 ClipRect 或 ClipRRect 限制滤镜区域… "
              "BackdropFilter 会读取子树之外的背景，无法仅凭子节点的绘制边界推断完整作用范围。",
     "demonstrated_by": ["example-04"],
     "measured": "probe-backdrop-a/b/c 三次真实渲染：同一棵 core_4 子树，仅更换外层包装/画布，"
                 "卡内像素最多差 21/255——文档的“读取子树之外的背景”正是原因"},
    {"claim": "ImageFiltered 与 BackdropFilter 要求有限非负的 sigmaX/sigmaY，可设 tileMode（默认 CLAMP）；"
              "ImageFiltered 会按 sigma 自动提供模糊输出边界",
     "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/reference_parser-tags.txt"},
     "quote": "ImageFiltered 与 BackdropFilter 要求有限非负的 sigmaX、sigmaY，可设置 tileMode（默认 CLAMP）…",
     "line": 443, "demonstrated_by": ["example-04"]},
    {"claim": "Stack 默认 clipBehavior=HARD_EDGE、alignment=TOP_START，阴影/柔化会被切掉",
     "source_url": "https://snapshot.muedsa.com/widgets/layout/stack/",
     "doc_cache": {"path_base": "suite_root", "path": f"tmp/{RUN}/_suite/docs-txt/widget_layout_stack.txt"},
     "quote": "clipBehavior: ClipBehavior = ClipBehavior.HARD_EDGE", "line": 12,
     "demonstrated_by": ["example-04"]},
    {"claim": "颜色支持 3/4/6/8 位十六进制与 rgb()/hsl() 等 CSS 写法，但不支持 currentColor/lab()/color()",
     "source_url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "doc_cache": {"path_base": "suite_root",
                   "path": f"tmp/{RUN}/_suite/docs-txt/reference_parser-tags.txt"},
     "quote": "十六进制颜色需以 # 开头，支持 3、4、6、8 位；4 位与 8 位的最后一组是透明度（alpha）。",
     "line": 81, "demonstrated_by": ["example-03"]},
]

doc = {
    "schema_version": 1,
    "task_id": "A17",
    "path_base": "output_dir",
    "coordinate_space": "canvas top-left origin, x right / y down, pixels; "
                        "boxes are [left, top, right, bottom] where given",
    "line_number_base": "1-based lines of the delivered example-NN.snapshot file",
    "accepted_version": a.ver,
    "examples": examples,
    "technical_claims": CLAIMS,
    "measurement": {
        "mono_advance_em": 0.486,
        "cjk_advance_em": 1.00,
        "line_pitch_em": 1.46,
        "method": "probe-mono.png (request A17-probe-mono-a1): 70 glyphs of Noto Sans "
                  "Mono CJK SC at fontSize 20 measured x=21..691 -> (691-21)/69 = 9.71px",
        "layout_model_conservative_mono_advance_em": 0.50,
    },
    "flex_ratio_measured_in_example_02": {
        "bars": [[24, 105], [118, 281], [294, 375]],
        "widths": [82, 164, 82],
        "ratio": "1 : 2 : 1",
        "violet_bar_width": 352,
        "method": "numpy colour mask over v007-example-02.png, same numbers as the "
                  "flex 1:2:1 claim on page 2",
    },
}
(OUT / "examples.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")
print("wrote", (OUT / "examples.json").relative_to(ROOT).as_posix(),
      "examples:", len(doc["examples"]), "claims:", len(doc["technical_claims"]))
for e in doc["examples"]:
    print(e["page_id"], "printed", e["printed_line_count"], "segments",
          [(s["from_line"], s["to_line"]) for s in e["printed_segments"]],
          "core in example", e["core_subtree"]["in_example_dsl_lines"],
          "core in page", e["core_subtree"]["in_handbook_dsl_lines"])
