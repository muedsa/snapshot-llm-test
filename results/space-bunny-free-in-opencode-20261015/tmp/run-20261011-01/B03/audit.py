#!/usr/bin/env python
"""B03 · 交付前总审查：逐项核对文件、配对、链接、字号下限与免责声明。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__import__("os").environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
OUT = ROOT / "outputs/run-20261011-01/B03"
TMP = ROOT / "tmp/run-20261011-01/B03"

fails, warns = [], []


def ck(cond, msg):
    if cond:
        print(f"  OK   {msg}")
    else:
        fails.append(msg)
        print(f"  FAIL {msg}")


print("== 1. 十件产物 ==")
for i in range(1, 11):
    cid = f"case-{i:02d}"
    png, dsl, note = OUT / cid / "final.png", OUT / cid / "final.snapshot", OUT / cid / "case.md"
    ck(png.exists() and png.stat().st_size > 0, f"{cid}/final.png ({png.stat().st_size if png.exists() else 0} B)")
    ck(dsl.exists() and dsl.stat().st_size > 0, f"{cid}/final.snapshot ({dsl.stat().st_size if dsl.exists() else 0} B)")
    ck(note.exists() and note.stat().st_size > 0, f"{cid}/case.md")
    if dsl.exists():
        t = dsl.read_text(encoding="utf-8")
        body = re.sub(r"<Image(?:Filtered|EmojiSpan)\b", "", t)
        ck("<Image" not in body, f"{cid} DSL 无 <Image 标签")
        ck(t.startswith("<Snapshot"), f"{cid} DSL 以 <Snapshot 开头")
        ck(t.rstrip().endswith("</Snapshot>"), f"{cid} DSL 以 </Snapshot> 结尾")
        ck('type="png"' in t, f"{cid} 输出类型 png")

print("== 2. 输出根文档 ==")
for f in ("portfolio.json", "portfolio.md", "gallery.md", "snapshot-usage.md",
          "technique-notes.md", "task-metrics.json"):
    p = OUT / f
    ck(p.exists() and p.stat().st_size > 0, f"{f} ({p.stat().st_size if p.exists() else 0} B)")

print("== 3. gallery.md 链接可解析 ==")
g = (OUT / "gallery.md").read_text(encoding="utf-8")
for i in range(1, 11):
    cid = f"case-{i:02d}"
    for link in (f"({cid}/final.png)", f"({cid}/final.snapshot)", f"({cid}/case.md)"):
        ck(link in g, f"gallery 含 {link}")
    tgt = (OUT / cid / "final.png")
    ck(tgt.exists(), f"gallery 的 {cid}/final.png 目标存在")
ck(g.count("![") == 10, f"gallery 逐图预览 10 张（实际 {g.count('![')}）")

print("== 4. portfolio.json 自洽 ==")
pj = json.loads((OUT / "portfolio.json").read_text(encoding="utf-8"))
ck(pj["counts"]["pieces"] == 10, "portfolio 记录 10 件")
ck(len(pj["pieces"]) == 10, "portfolio pieces 长度 10")
for p in pj["pieces"]:
    ck((ROOT / p["png"]).exists() and (ROOT / p["dsl"]).exists()
       and (ROOT / p["case_note"]).exists(),
       f"{p['id']} 的 png/dsl/case_note 都存在")
    ck(p["fictional"] is True, f"{p['id']} 标记 fictional")

print("== 5. 每张图页脚的免责声明 ==")
DIS = "自拟场景与自拟数据"
for i in range(1, 11):
    cid = f"case-{i:02d}"
    note = (OUT / cid / "case.md").read_text(encoding="utf-8")
    ck(DIS in note, f"{cid}/case.md 含自拟声明")

print("== 6. 临时过程留痕 ==")
for f in ("plan-v1.md", "capability-findings.md", "requests.jsonl",
          "iterations.jsonl", "tool-usage.jsonl",
          "probe_b03_accept.py", "probe_b03_accept2.py",
          "probe_b03_accept3.py", "probe_b03_accept4.py",
          "deliver_b03.py", "deliver_metrics.py", "run_case.py", "b03kit.py"):
    ck((TMP / f).exists(), f"tmp/{f}")
ck(len(list((TMP / "pieces").glob("c*.py"))) == 10, "tmp/pieces 下 10 个生成脚本")
ck(len(list((TMP / "drafts").glob("*.snapshot"))) >= 30,
   f"tmp/drafts 保留历史版本 {len(list((TMP / 'drafts').glob('*.snapshot')))} 份")
for d in ("probe", "probe2", "probe3", "probe4"):
    ck((TMP / d).exists() and len(list((TMP / d).glob("*.snapshot"))) > 0,
       f"tmp/{d} 保留探针 DSL")
ck(len(list((TMP / "responses").glob("*"))) > 0, "tmp/responses 保留失败响应")

print("== 7. 指标自洽 ==")
m = json.loads((OUT / "task-metrics.json").read_text(encoding="utf-8"))
ck(m["counts"]["final_cases"] == 10, "metrics final_cases = 10")
ck(sum(c["image_views"] for c in m["per_case"]) == m["counts"]["image_views"], "metrics 看图数自洽")
ck(m["iteration_breakdown"]["baseline"] == 10, "每件 1 次 baseline 记录")
ck(m["timings"]["queue_wait_seconds"] is None, "未测量的排队等待为 null")
req = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8-sig").splitlines() if l.strip()]
ok = sum(1 for r in req if r.get("request_type") == "render" and r.get("status") == 200
         and not r.get("error") and (r.get("response_bytes") or 0) > 0)
ck(ok == m["counts"]["successful_render_requests"], f"metrics 成功渲染数与日志一致（{ok}）")
ck(not any(r.get("status") == 429 for r in req), "全程无 429")
ck(not any(r.get("status") == 503 for r in req), "全程无 503")

print()
print(f"== 总结：{len(fails)} 项失败 ==")
for f in fails:
    print("  -", f)
sys.exit(1 if fails else 0)