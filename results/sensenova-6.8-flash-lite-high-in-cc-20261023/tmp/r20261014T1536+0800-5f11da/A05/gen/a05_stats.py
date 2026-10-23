"""汇总 A05 请求/留痕统计，供 task-metrics.json 与 usage 报告引用（不改任何交付件）。"""
import json, hashlib, re, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a05_io as IO
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

out, tmp = IO.dirs()
reqs = [json.loads(l) for l in (tmp / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print(f"请求总数 {len(reqs)}")
ok = [r for r in reqs if r["http_status"] == 200]
bad = [r for r in reqs if r["http_status"] != 200]
print(f"  200 {len(ok)}  非200 {len(bad)}")
from collections import Counter
print("  kind:", dict(Counter(r["kind"] for r in reqs)))
print("  status:", dict(Counter(r["http_status"] for r in reqs)))
print("  attempts 分布:", dict(Counter(r["attempts"] for r in reqs)))
el = [r["elapsed_ms"] for r in reqs]
print(f"  elapsed_ms 和 {sum(el):.0f}  min {min(el):.0f}  max {max(el):.0f}")
el_ok = [r["elapsed_ms"] for r in ok]
print(f"  200 的 elapsed_ms 和 {sum(el_ok):.0f}")
print(f"  首请求 {reqs[0]['started_at']}  末响应 {max(r['ended_at'] for r in reqs)}")
print(f"  ratelimit 范围 {min(int(r['ratelimit_remaining']) for r in reqs)}–{max(int(r['ratelimit_remaining']) for r in reqs)}")
print(f"  429/503 {sum(1 for r in reqs if r['http_status'] in (429,503))}  Retry-After 出现过 {any(r['retry_after'] for r in reqs)}")
rt = []
for r in reqs:
    m = re.search(r"render;dur=([\d.]+)", r["server_timing"] or "")
    rt.append(float(m.group(1)) if m else None)
print(f"  server render;dur 和 {sum(v for v in rt if v):.1f} ms（{sum(1 for v in rt if v)} 条含 render 段）")
print("  错误:")
for r in bad:
    print(f"    {r['request_id']} {r['http_status']} :: {r['error_summary'][:110]}")
print("  DSL 版本副本:")
for p in sorted((tmp / "dsl").glob("*.snapshot")):
    print(f"    {p.name}  {p.stat().st_size} B")

def sha(p):
    b = p.read_bytes()
    return hashlib.sha256(b).hexdigest()[:16], len(b)
print("\n交付件:")
for f in ("sensor-report.png", "sensor-report.snapshot", "normalized-data.json"):
    p = out / f
    print(f"  {f}: {sha(p)} bytes={len(p.read_bytes())}")
im = Image.open(out / "sensor-report.png")
print(f"  PNG mode={im.mode} size={im.size}")
dsl = (out / "sensor-report.snapshot").read_text(encoding="utf-8")
print(f"  DSL Positioned={dsl.count('<Positioned')}  节点={dsl.count('<')}  字节={len(dsl)}")
print("\n预览图:")
for p in sorted((tmp / "preview").glob("*.png")):
    print(f"  {p.name}  {p.stat().st_size} B")
