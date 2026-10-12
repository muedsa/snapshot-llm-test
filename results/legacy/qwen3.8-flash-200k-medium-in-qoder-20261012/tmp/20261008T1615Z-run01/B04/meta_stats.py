# -*- coding: utf-8 -*-
"""件-10 的统计底座：把本题整套留痕倒回成一张可核对的账。

输入全部是真实日志（requests.jsonl / iterations.jsonl / build-log.jsonl /
tool-usage.jsonl / research/*.json / outputs/…/case-NN/），输出
research/meta.json。不新造任何数字：每一项都写明它来自哪个文件。
"""
import collections
import hashlib
import io
import json, datetime
import os
import re
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
B = ROOT / "tmp" / RID / "B04"
O = ROOT / "outputs" / RID / "B04"
RES = B / "research"


def rd(p):
    return io.open(p, encoding="utf-8").read()


def jl(p):
    return [json.loads(l) for l in rd(p).rstrip("\n").split("\n") if l.strip()]


reqs = jl(B / "requests.jsonl")
iters = jl(B / "iterations.jsonl")
builds = jl(B / "build-log.jsonl")
tools = jl(B / "tool-usage.jsonl")

# ---------- 逐件 ----------
cases = []
for n in range(1, 10):
    cid = "case-%02d" % n
    ver = "case%02d" % n
    png = O / cid / "final.png"
    snp = O / cid / "final.snapshot"
    rb = [r for r in reqs if r.get("kind") == "render" and ver in str(r.get("request_id", ""))]
    # 迭代归属按 image_path 里的 case-NN 判定：case-01/02 早期 7 条记录的 version 字段
    # 没带 case 前缀（当时按“每题从 v01 起编号”记的），只按 version 会漏计。
    ib = [r for r in iters if ("/" + cid + "/") in str(r.get("image_path", ""))
          or str(r.get("version", "")).startswith(ver)]
    bb = [r for r in builds if r.get("case") == "%02d" % n]
    md5 = hashlib.md5(png.read_bytes()).hexdigest() if png.exists() else None
    # 成品尺寸从 DSL 头部读，不猜
    dims = None
    if snp.exists():
        m = re.search(r'width="(\d+)" height="(\d+)"', rd(snp))
        if m:
            dims = [int(m.group(1)), int(m.group(2))]
    if dims is None:
        dims = next((x.get("dimensions") for x in reversed(bb) if x.get("dimensions")), None)
    cases.append({
        "case": cid,
        "title": None,
        "dimensions": dims,
        "final_png_bytes": png.stat().st_size if png.exists() else None,
        "final_snapshot_bytes": snp.stat().st_size if snp.exists() else None,
        "final_png_md5": md5,
        "render_requests": len(rb),
        "render_ok": sum(1 for r in rb if r.get("http_status") == 200),
        "final_request_id": None,
        "iterations_logged": len(ib),
        "iteration_types": dict(collections.Counter(r.get("type") for r in ib)),
        "gate_checks": max([x["gate"]["checks"] for x in bb]) if bb else 0,
        "gate_blocked_attempts": sum(1 for x in bb if x.get("request_sent") is False
                                     or x["gate"]["warnings"]),
        "dsl_versions_kept": len(bb),
    })
    # 标题从 case.md 第一行取，保证与交付文档一致
    cm = O / cid / "case.md"
    if cm.exists():
        txt = rd(cm)
        m = re.match(r"^# 件 \d+ · (.+)$", txt.split("\n")[0].strip())
        if m:
            cases[-1]["title"] = m.group(1).strip()
        m2 = re.search(r"成品响应 `([A-Za-z0-9\-]+)`", txt)
        if m2:
            cases[-1]["final_request_id"] = m2.group(1)
        else:
            mv = re.search(r"\*\*(v[0-9a-z]+)\*\*", txt)
            cand = [r["request_id"] for r in rb
                    if mv and r["request_id"].startswith("B04-%s-%s-" % (ver, mv.group(1)))]
            cases[-1]["final_request_id"] = (cand[-1] if cand
                                             else (rb[-1]["request_id"] if rb else None))
            if not cand:
                cases[-1]["final_request_note"] = "按 case.md 加粗版本号回退匹配最后一次渲染"

# ---------- 来源账 ----------
docs = [r for r in reqs if r.get("kind") == "document"]
by_status = dict(collections.Counter(r.get("http_status") for r in docs))
hosts = dict(collections.Counter(str(r.get("url", "")).split("/")[2]
                                 if "://" in str(r.get("url", "")) else "?" for r in docs))
ok_urls = sorted({r["url"] for r in docs if r.get("http_status") == 200})
bad = [{"url": r.get("url"), "status": r.get("http_status"),
        "error": r.get("error_summary") or r.get("note")} for r in docs
        if r.get("http_status") != 200]

# ---------- 推算脚本 / 研究产物 ----------
derived = []
for p in sorted(RES.glob("*.json")):
    j = json.loads(rd(p))
    derived.append({"file": "research/" + p.name, "top_keys": len(j),
                    "generated_at": j.get("generated_at"),
                    "bytes": p.stat().st_size})
scripts = sorted(p.name for p in B.glob("derive*.py")) + sorted(
    p.name for p in B.glob("parse_*.py")) + sorted(p.name for p in B.glob("fetch_sources*.py"))

# ---------- 迭代归属核对：任何一条都不能悄悄丢掉 ----------
attr = []
for r in iters:
    hit = ["case-%02d" % c for c in range(1, 10)
           if ("/case-%02d/" % c) in str(r.get("image_path", ""))
           or str(r.get("version", "")).startswith("case%02d" % c)]
    attr.append(hit)
unattributed = [r["iteration_id"] for h, r in zip(attr, iters) if not h]
prefixless = [r["iteration_id"] for r in iters
              if not str(r.get("version", "")).startswith("case")]

# ---------- 输入依赖：从生成器脚本本体里抠，不靠回忆 ----------
KIT = {"B.data()": ["stats.json", "catalog.json"], "B.ddata()": ["derived.json"]}
inputs = {}
for n in range(1, 10):
    txt = rd(B / ("case%02d.py" % n))
    js = set(re.findall(r'load\("([A-Za-z0-9_\-\.]+\.json)"\)', txt))
    js |= set(re.findall(r'"([a-z0-9\-]+\.json)"', txt))
    for fn, outs in KIT.items():
        if fn in txt:
            js |= set(outs)
    inputs["case-%02d" % n] = sorted(js)
edges = []
for a in range(1, 10):
    for b in range(a + 1, 10):
        sh = sorted(set(inputs["case-%02d" % a]) & set(inputs["case-%02d" % b]))
        if sh:
            edges.append({"from": "case-%02d" % a, "to": "case-%02d" % b,
                          "shared": sh, "w": len(sh)})

# ---------- 每件引用的来源文件：case.md 与成品图上的注带各算一次 ----------
PAT_SRC = r"(sources/[A-Za-z0-9\-\.]+|probe/[A-Za-z0-9\-\.]+|research/[A-Za-z0-9\-\.]+\.json)"
srcs = {}
img_srcs = {}
for n in range(1, 10):
    key = "case-%02d" % n
    cm = O / key / "case.md"
    srcs[key] = sorted(set(re.findall(PAT_SRC, rd(cm)))) if cm.exists() else []
    snp = O / key / "final.snapshot"
    img_srcs[key] = sorted(set(re.findall(PAT_SRC, rd(snp)))) if snp.exists() else []

# ---------- 成品图面上的自我标注次数（证据分级的可机读痕迹） ----------
KEYS = [u"推算", u"已证实", u"来源结论", u"原文", u"限制", u"演示"]
img_marks = {}
for n in range(1, 10):
    snp = O / ("case-%02d" % n) / "final.snapshot"
    t = rd(snp) if snp.exists() else ""
    img_marks["case-%02d" % n] = {k: t.count(k) for k in KEYS}

meta = {    "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
    "path_base": "suite_root",
    "run_id": RID,
    "sources_of_numbers": {
        "requests": "tmp/<run>/B04/requests.jsonl",
        "iterations": "tmp/<run>/B04/iterations.jsonl",
        "build_log": "tmp/<run>/B04/build-log.jsonl",
        "tool_usage": "tmp/<run>/B04/tool-usage.jsonl",
        "titles": "outputs/<run>/B04/case-NN/case.md 第一行",
        "dimensions": "final.snapshot 头部 width/height，退回 build-log.dimensions",
    },
    "cases": cases,
    "inputs_per_case": inputs,
    "shared_input_edges": edges,
    "sources_per_case": srcs,
    "sources_per_case_on_image": img_srcs,
    "image_marks": img_marks,
    "iteration_attribution": {
        "rule": "image_path 含 /case-NN/ 或 version 以 caseNN 开头",
        "unattributed": unattributed,
        "version_without_case_prefix": prefixless,
        "note": "case-01/02 的 7 条早期记录 version 只写 v01…v04（当时按每题独立编号），"
                "归属改由 image_path 判定；pre1/v03a/v04x 三条是语法修复与重试的补记。",
    },
    "totals": {
        "http_requests": len(reqs),
        "renders": sum(1 for r in reqs if r.get("kind") == "render"),
        "renders_ok": sum(1 for r in reqs if r.get("kind") == "render" and r.get("http_status") == 200),
        "renders_failed": sum(1 for r in reqs if r.get("kind") == "render" and r.get("http_status") != 200),
        "render_error_notes": [str(r.get("error_summary"))[:90] for r in reqs if r.get("kind") == "render" and r.get("http_status") != 200],
        "document_requests": len(docs),
        "document_by_status": by_status,
        "document_hosts": hosts,
        "distinct_ok_pages": len(ok_urls),
        "fonts_queries": sum(1 for r in reqs if r.get("kind") == "fonts"),
        "iterations": len(iters),
        "iteration_types": dict(collections.Counter(r.get("type") for r in iters)),
        "tool_usage_records": len(tools),
        "gate_blocked": sum(1 for x in builds if x.get("request_sent") is False
                            or x["gate"]["warnings"]),
        "final_png_bytes": sum(c["final_png_bytes"] or 0 for c in cases),
        "final_dsl_bytes": sum(c["final_snapshot_bytes"] or 0 for c in cases),
    },
    "ok_pages": ok_urls,
    "failed_pages": bad,
    "research_files": derived,
    "scripts": scripts,
}
out = RES / "meta.json"
io.open(out, "w", encoding="utf-8", newline="\n").write(json.dumps(meta, ensure_ascii=False, indent=1))
print("wrote", out.relative_to(ROOT))
for c in cases:
    print(c["case"], c["dimensions"], c["title"], "req", c["render_requests"],
          "it", c["iterations_logged"], "gate", c["gate_blocked_attempts"])
print(json.dumps(meta["totals"], ensure_ascii=False, indent=1))
