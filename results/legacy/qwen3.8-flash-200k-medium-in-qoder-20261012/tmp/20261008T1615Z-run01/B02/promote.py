"""B02 提升脚本：把某一次真实服务响应提升为该触点的 final.png / final.snapshot。

用字节指纹（md5）确认「成品图 = 该请求的原始响应字节」，DSL 从该请求的 body 文件里
按 HTTP 头/正文分隔符切出来，因此 final.snapshot 一定是真正渲染出这张图的那份 DSL。

用法：python tmp/<run_id>/B02/promote.py --case case-01 --version v04
"""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--case", required=True)
ap.add_argument("--version", required=True)
ap.add_argument("--key", default=None, help="请求 id 里的用例键，默认同 --case")
ap.add_argument("--name", default="final", help="输出文件基名，如 final / back")
a = ap.parse_args()

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
tmp = root / "tmp" / rid / "B02"
out = root / "outputs" / rid / "B02" / a.case
req_id = "B02-%s-%s-" % (a.key or a.case, a.version)

rec = None
for line in (tmp / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    if r["request_id"].startswith(req_id):
        rec = r
        break
if rec is None:
    raise SystemExit("找不到请求 %s*" % req_id)
if rec["http_status"] != 200 or rec["error_summary"]:
    raise SystemExit("该请求不是成功响应：%s" % rec["error_summary"])

raw = Path(rec["raw_copy_file"])
png = Path(rec["out_file"])
md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()  # noqa: E731
if md5(raw) != md5(png):
    raise SystemExit("响应副本与 out_file 字节不一致，拒绝提升")

body = Path(rec["request_file"]).read_bytes()
_, _, dsl = body.partition(b"\r\n\r\n")
if not dsl.startswith(b"<Snapshot") or not dsl.rstrip().endswith(b"</Snapshot>"):
    raise SystemExit("请求 body 里切出的不是完整 DSL")

out.mkdir(parents=True, exist_ok=True)
shutil.copy(str(raw), str(out / ("%s.png" % a.name)))
(out / ("%s.snapshot" % a.name)).write_bytes(dsl)
print(json.dumps({
    "case": a.case, "version": a.version, "request_id": rec["request_id"],
    "final_png_md5": md5(out / ("%s.png" % a.name)), "dsl_chars": len(dsl.decode("utf-8")),
    "started_at": rec["started_at"], "server_timing": rec["server_timing"],
    "dimensions": rec.get("dimensions"),
}, ensure_ascii=False, indent=2))
