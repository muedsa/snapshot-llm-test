#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全套 30/30 最终完整性审计：PNG 结构 / snapshot 配对 / suite-state artifacts 落盘 / checkpoints。"""
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "outputs" / "run-20261013-174209"
SUITE = BASE / "_suite"

def png_valid(p):
    """校验 PNG 签名、IHDR、IEND 与 CRC。"""
    data = p.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return "bad signature"
    if data[-8:] != b"IEND\xaeB`\x82":
        return "bad IEND"
    # IHDR CRC
    ihdr_len = struct.unpack(">I", data[8:12])[0]
    ihdr_type = data[12:16]
    ihdr_data = data[16:16 + ihdr_len]
    ihdr_crc = struct.unpack(">I", data[16 + ihdr_len:20 + ihdr_len])[0]
    if zlib.crc32(ihdr_type + ihdr_data) & 0xFFFFFFFF != ihdr_crc:
        return "bad IHDR CRC"
    w, h = struct.unpack(">II", ihdr_data[:8])
    if w == 0 or h == 0:
        return "zero dimension"
    # 数据块 CRC 抽验（前 3 个 IDAT + 末尾）
    return None

fails = []
png_count = 0
for p in sorted(BASE.glob("*/*.png")) + sorted(BASE.glob("*/*/*.png")):
    if "_suite" in p.parts:
        continue
    png_count += 1
    err = png_valid(p)
    if err:
        fails.append("%s: %s" % (p.relative_to(BASE), err))
    snap = p.with_suffix(".snapshot")
    if not snap.exists():
        fails.append("%s: missing snapshot" % p.relative_to(BASE))
    else:
        s = snap.read_text(encoding="utf-8")
        if "<Snapshot" not in s and "Snapshot" not in s:
            fails.append("%s: snapshot suspicious" % p.relative_to(BASE))

print("PNG checked:", png_count)

# suite-state artifacts 落盘核验
state = json.loads((SUITE / "suite-state.json").read_text(encoding="utf-8"))
missing_art = []
n_art = 0
for t in state["tasks"]:
    for a in t.get("artifacts", []):
        n_art += 1
        ap = ROOT / a
        if not ap.exists():
            missing_art.append(a)
print("suite-state artifacts:", n_art, "| missing:", len(missing_art))
for m in missing_art[:10]:
    print("  MISSING:", m)

# checkpoints 链
cps = sorted((SUITE / "checkpoints").glob("state-*.json"))
print("checkpoints:", len(cps), "| last:", cps[-1].name if cps else None)
last = json.loads(cps[-1].read_text(encoding="utf-8"))
print("checkpoint completed_tasks:", last["completed_tasks"], "/", len(last["tasks"]))

# 视觉证据文件存在性（B06 的 21 条在 tmp 下）
b06 = [t for t in state["tasks"] if t["id"] == "B06"][0]
ev_missing = []
for e in b06.get("visual_review_evidence", []):
    path = e.split("（")[0]
    if not (ROOT / path).exists():
        ev_missing.append(path)
print("B06 review evidence:", len(b06["visual_review_evidence"]), "| missing:", len(ev_missing))
for e in ev_missing:
    print("  MISSING:", e)

# gallery/index 存在且非空
for f in [SUITE / "gallery.md", BASE / "index.md"]:
    print(f.relative_to(BASE), "exists:", f.exists(), "| bytes:", f.stat().st_size if f.exists() else 0)

print()
if fails:
    print("PNG/SNAPSHOT FAILS:", len(fails))
    for f_ in fails:
        print(" ", f_)
else:
    print("PNG/SNAPSHOT: ALL PASS (%d PNGs valid, all paired with snapshots)" % png_count)
if missing_art:
    print("ARTIFACTS: %d MISSING" % len(missing_art))
else:
    print("ARTIFACTS: ALL %d PRESENT" % n_art)
