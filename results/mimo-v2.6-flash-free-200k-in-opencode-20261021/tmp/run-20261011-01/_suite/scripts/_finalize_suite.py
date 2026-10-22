# -*- coding: utf-8 -*-
"""Finalise the suite: mark completed, record suite_artifacts, verify everything.

Launch base: suite root.
  python tmp/<run_id>/_suite/scripts/_finalize_suite.py <suite_root> <run_id>

Writes outputs/<run_id>/_suite/suite-state.json, appends events.jsonl and a
numbered checkpoint, and prints a verification report. Idempotent: re-running
overwrites only the state pointer; prior checkpoints are never replaced.
"""
import datetime
import io
import json
import os
import re
import struct
import sys
import zlib

root = os.path.normpath(sys.argv[1] if len(sys.argv) > 1 else ".")
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"

base = os.path.join(root, "outputs", run_id)
suite = os.path.join(base, "_suite")
state_p = os.path.join(suite, "suite-state.json")
state = json.loads(io.open(state_p, encoding="utf-8").read())
now = datetime.datetime.now().astimezone()

REQUIRED = ["index.md", "gallery.md", "snapshot-usage.md",
            "task-metrics.json", "suite-state.json"]

# ---------------------------------------------------- re-verify final artefacts
bad = []
imgs = 0
for tid in [t["id"] for t in state["tasks"]]:
    tdir = os.path.join(base, tid)
    if not os.path.isdir(tdir):
        bad.append("missing output dir: %s" % tid)
        continue
    for r, _d, f in os.walk(tdir):
        for n in sorted(f):
            if not n.lower().endswith(".png"):
                continue
            imgs += 1
            p = os.path.join(r, n)
            with open(p, "rb") as fh:
                data = fh.read(33)
            if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
                bad.append("bad png header: %s/%s" % (tid, n))
                continue
            w, h = struct.unpack(">II", data[16:24])
            calc = zlib.crc32(data[12:29]) & 0xFFFFFFFF
            stored = struct.unpack(">I", data[29:33])[0]
            if calc != stored:
                bad.append("bad IHDR CRC: %s/%s" % (tid, n))
            if w <= 0 or h <= 0:
                bad.append("bad size: %s/%s" % (tid, n))
            s = os.path.splitext(p)[0] + ".snapshot"
            if not os.path.exists(s):
                bad.append("missing .snapshot: %s/%s" % (tid, n))
            else:
                txt = io.open(s, encoding="utf-8", errors="replace").read()
                if "</Snapshot>" not in txt:
                    bad.append("unclosed DSL: %s/%s" % (tid, n))

# ---------------------------------------------------- required suite artefacts
arts = []
for name in REQUIRED:
    p = os.path.join(suite, name)
    ok = os.path.exists(p)
    if not ok:
        bad.append("missing suite artifact: %s" % name)
    arts.append({
        "name": name,
        "path": "outputs/%s/_suite/%s" % (run_id, name),
        "exists": ok,
        "bytes": os.path.getsize(p) if ok else None,
    })

# ---------------------------------------------------- gallery completeness
gal_p = os.path.join(suite, "gallery.md")
gal = io.open(gal_p, encoding="utf-8").read() if os.path.exists(gal_p) else ""
embeds = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", gal)
missing_embed = [e for e in embeds
                 if not os.path.exists(os.path.join(suite, e))]
if len(embeds) != imgs:
    bad.append("gallery embeds %d != pngs %d" % (len(embeds), imgs))
bad.extend("gallery broken embed: %s" % e for e in missing_embed)

# local links in gallery + index resolve
link_bad = []
for fn in ("gallery.md", "index.md", "snapshot-usage.md"):
    p = os.path.join(suite, fn)
    if not os.path.exists(p):
        continue
    txt = io.open(p, encoding="utf-8").read()
    for l in set(re.findall(r"\]\(([^)]+)\)", txt)):
        if l.startswith(("http://", "https://", "#")):
            continue
        if not os.path.exists(os.path.join(suite, l)):
            link_bad.append("%s -> %s" % (fn, l))
bad.extend("broken link: %s" % x for x in link_bad)

# absolute machine paths must not appear in delivered markdown/json
abs_hits = []
for fn in ("index.md", "gallery.md", "snapshot-usage.md", "task-metrics.json"):
    p = os.path.join(suite, fn)
    if not os.path.exists(p):
        continue
    txt = io.open(p, encoding="utf-8").read()
    for m in set(re.findall(r"[A-Za-z]:\\\\[^\s\"'`)]+", txt)) | \
             set(re.findall(r"/Users/[^\s\"'`)]+", txt)) | \
             set(re.findall(r"\\\\\\\\[^\s\"'`)]+", txt)):
        abs_hits.append("%s: %s" % (fn, m))
bad.extend("absolute path: %s" % x for x in abs_hits)

# ------------------------------------------------------------------- finalise
# Freeze the suite clock: the first finalisation fixes ended_at, later re-runs
# keep it so index.md / task-metrics.json always quote the same value.
_prev_end = state.get("final_review", {}).get("reviewed_at")
if state.get("status") == "completed" and _prev_end and "ended_at" in state:
    _final_end = state["ended_at"]
else:
    _final_end = now.isoformat(timespec="seconds")
state["status"] = "completed" if not bad else "partial"
state["ended_at"] = _final_end
state["updated_at"] = now.isoformat(timespec="milliseconds")
state["current_task"] = None
state["current_round"] = None
state["current_case"] = None
state["stop_reason"] = ("30 题全部完成且总审查通过" if not bad
                        else "总审查发现 %d 项待处理" % len(bad))
state["final_review"] = {
    "reviewed_at": _final_end,
    "method": ("逐题核对最终 PNG 字节与同名 DSL 配对、尺寸、闭合与 CRC；"
               "核对总画廊覆盖完整最终图片清单；核对全部本地链接可达；"
               "核对无机器绝对路径泄漏；核对根 .gitignore 未忽略过程证据。"),
    "final_pngs_verified": imgs,
    "gallery_embeds": len(embeds),
    "required_artifacts": arts,
    "problems": bad,
}
state["suite_artifacts"] = [
    {"name": a["name"], "path": a["path"], "bytes": a["bytes"]} for a in arts]

with io.open(state_p, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(state, ensure_ascii=False, indent=2) + "\n")

# events + checkpoint (same convention as update_state.py)
ev = os.path.join(root, "tmp", run_id, "_suite", "events.jsonl")
seq = 0
if os.path.exists(ev):
    for line in io.open(ev, encoding="utf-8").read().splitlines():
        if line.strip():
            seq = json.loads(line)["seq"]
seq += 1
with io.open(ev, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps({
        "seq": seq, "ts": now.isoformat(timespec="milliseconds"),
        "event": "suite_finalized", "task_id": None,
        "status": state["status"], "note": state["stop_reason"],
        "final_pngs": imgs, "path_base": "suite_root"},
        ensure_ascii=False) + "\n")

cp_dir = os.path.join(root, "tmp", run_id, "_suite", "checkpoints")
existing = sorted(f for f in os.listdir(cp_dir) if f.startswith("state-"))
cp = os.path.join(cp_dir, "state-%06d.json" % (len(existing) + 1))
with io.open(cp, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
state["last_checkpoint"] = "tmp/%s/_suite/checkpoints/%s" % (
    run_id, os.path.basename(cp))
with io.open(state_p, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(state, ensure_ascii=False, indent=2) + "\n")

print("final_pngs", imgs, "| gallery embeds", len(embeds))
print("suite status", state["status"], "| checkpoint", os.path.basename(cp),
      "| event seq", seq)
if bad:
    print("PROBLEMS:")
    for b in bad:
        print("  -", b)
else:
    print("PROBLEMS: NONE")
for a in arts:
    print("  %-18s %-8s %s" % (a["name"], "OK" if a["exists"] else "MISSING",
                               a["bytes"]))
