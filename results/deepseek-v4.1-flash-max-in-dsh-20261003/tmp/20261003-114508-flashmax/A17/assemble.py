"""Assemble the A17 deliverables from the final per-artefact DSL versions.

Entity/limit facts re-verified for this revision (all measured against the live service):
  * `A &amp; B` renders five literal characters -> the parser does not decode entities
    (probe tmp/20261003-114508-flashmax/A17/entity-probe.png, request A17-REQ-0085)
  * no final DSL contains an entity sequence
  * element counts (regex `<[A-Za-z]`, the service counts elements per tag) stay far below
    the 4096 per-document cap; the largest page is ~620 elements
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "A17")
OUT = os.path.join(ROOT, "outputs", RUN, "A17")

FINAL = {name: "v9" for name in
         ("handbook-01", "handbook-02", "handbook-03", "handbook-04",
          "example-01", "example-02", "example-03", "example-04")}

PURPOSE = {
    "example-01": "第 1 页示例：最小调用契约。根 Container 定尺寸 + 渐变底 + Stack 居中文本，"
                  "证明“纯文本 DSL → PNG 字节”。",
    "example-02": "第 2 页示例：有界布局。根 Container 给约束，Stack 定位层里放 Row + 三个 Expanded，"
                  "并给出父约束数值与 Positioned 坐标。",
    "example-03": "第 3 页示例：原样文本与颜色。Raw + CDATA 让尖括号与标签字样原样进入图像，"
                  "实体写法不会被解码；渐变尾部 alpha=00 表示完全透明。",
    "example-04": "第 4 页示例：两种模糊。ImageFiltered 模糊自己的子树（白卡与字一起糊），"
                  "ClipRRect + BackdropFilter 只模糊背后已绘制的内容。",
}

PRINTED = {
    "example-01": [(1, 1), (2, 4), (5, 8), (9, 11)],
    "example-02": [(3, 7), (8, 9), (12, 13)],
    "example-03": [(2, 4), (11, 17)],
    "example-04": [(3, 5), (14, 16), (18, 19)],
}


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def dsl_path(name: str) -> str:
    return os.path.join(TMP, f"{name}.{FINAL[name]}.snapshot")


def png_path(name: str) -> str:
    return os.path.join(TMP, f"{name}.final.png")


def load_requests() -> list:
    recs = []
    with open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def build_examples_json(reqs: list) -> dict:
    by_dsl = {}
    for r in reqs:
        if r.get("request_kind") == "render" and r.get("success"):
            by_dsl.setdefault(os.path.basename(r["request_file"]), []).append(r)
    out = {
        "schema": "a17-examples/1",
        "run_id": RUN,
        "note": "printed_fragment 是 dsl_file 的逐行原文（line 为源文件行号），elided_lines 给出"
                "未印刷的行号区间；因此手册上印的代码与真实渲染用的是同一份文件。",
        "parser_facts": {
            "entities_decoded": False,
            "evidence": "tmp/20261003-114508-flashmax/A17/entity-probe.png (A17-REQ-0085): "
                        "A &amp; B 画出 5 个字面字符",
            "cdata_required_for_angle_brackets": True,
            "document_element_limit": 4096,
        },
        "examples": [],
    }
    for idx in range(1, 5):
        key = f"example-{idx:02d}"
        src_lines = open(dsl_path(key), encoding="utf-8").read().rstrip("\n").split("\n")
        printed, elided, prev = [], [], 0
        for a, b in PRINTED[key]:
            if a - 1 > prev:
                elided.append([prev + 1, a - 1])
            printed.extend(range(a, b + 1))
            prev = b
        if prev < len(src_lines):
            elided.append([prev + 1, len(src_lines)])
        rec = by_dsl.get(f"{key}.{FINAL[key]}.snapshot", [])
        dsl_text = "\n".join(src_lines)
        out["examples"].append({
            "id": key,
            "page": idx,
            "purpose": PURPOSE[key],
            "dsl_file": f"{key}.{FINAL[key]}.snapshot",
            "shipped_as": f"{key}.snapshot",
            "png_file": f"{key}.png",
            "dsl_full_lines": len(src_lines),
            "dsl_elements": len(re.findall(r"<[A-Za-z]", dsl_text)),
            "contains_entity_sequence": bool(re.search(r"&(?:lt|gt|amp|quot|apos);", dsl_text)),
            "printed_lines": len(printed),
            "printed_fragment": [{"line": n, "text": src_lines[n - 1]} for n in printed],
            "elided_lines": elided,
            "renders": [{"request_id": r["request_id"], "http_status": r["http_status"],
                         "response_bytes": r["response_bytes"],
                         "service_request_id": r.get("service_request_id"),
                         "started_at": r["started_at"],
                         "png_sha256": sha256(r["response_file"])} for r in rec],
            "final_png_sha256": sha256(png_path(key)),
            "final_png_bytes": os.path.getsize(png_path(key)),
            "last_render_request_id": rec[-1]["request_id"] if rec else None,
            "size": {"width": 400, "height": 240},
        })
    return out


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    reqs = load_requests()
    ex = build_examples_json(reqs)
    with open(os.path.join(OUT, "examples.json"), "w", encoding="utf-8") as fh:
        json.dump(ex, fh, ensure_ascii=False, indent=2)
    for name in FINAL:
        shutil.copyfile(dsl_path(name), os.path.join(OUT, f"{name}.snapshot"))
        shutil.copyfile(png_path(name), os.path.join(OUT, f"{name}.png"))
    print("copied 8 .snapshot + 8 .png; examples.json written")
    for e in ex["examples"]:
        print(f"  {e['id']}  full={e['dsl_full_lines']:2d}  printed={e['printed_lines']:2d}  "
              f"elements={e['dsl_elements']:3d}  entities={e['contains_entity_sequence']}  "
              f"png={e['final_png_bytes']}B  last={e['last_render_request_id']}")


if __name__ == "__main__":
    main()
