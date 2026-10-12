"""B04 提升脚本：把某一次真实服务响应提升为该版本的 final.png / final.snapshot。

沿用 B03/B02 的字节指纹做法：final.png 的 md5 必须等于该请求原始响应副本的 md5，
final.snapshot 从该请求实际发送的 body 里按 HTTP 头/正文分隔符切出，
因此成品一定对应"真正渲染出这张图的那份 DSL"。

用法（总任务根）：python tmp/<run_id>/B04/promote.py --case case-01 --version v04
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
ap.add_argument("--name", default="final")
a = ap.parse_args()

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
tmp = root / "tmp" / rid / "B04"
out = root / "outputs" / rid / "B04" / a.case
want = "B04-%s-%s-" % (a.case, a.version)
norm = lambda s: s.replace("-", "")  # noqa: E731  兼容 case-01 / case01 两种写法

rec, fails = None, []
for line in (tmp / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    if not norm(r["request_id"]).startswith(norm(want)):
        continue
    if r["http_status"] == 200 and not r["error_summary"]:
        rec = r                      # 同版本多次尝试时取最后一次成功响应
    else:
        fails.append(r)
if rec is None:
    raise SystemExit("找不到该版本的 200 响应（失败尝试 %d 次：%s）" % (
        len(fails), fails[-1]["error_summary"] if fails else "无记录"))

md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()  # noqa: E731
raw = Path(rec["raw_copy_file"])
if md5(raw) != md5(Path(rec["out_file"])):
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
    "final_png_md5": md5(out / ("%s.png" % a.name)),
    "final_snapshot_bytes": (out / ("%s.snapshot" % a.name)).stat().st_size,
    "started_at": rec["started_at"], "server_timing": rec["server_timing"],
}, ensure_ascii=False, indent=2))
