"""B05 修正留痕：把误写到仓库根 requests.jsonl 的渲染记录归并到本题目录。

实测：上一个执行阶段直接调用 snapkit.render() 而没有先 snapkit.configure()，
snapkit 的 TEMP_DIR 仍是 ""，于是 log_render_request 写到了 CWD 下的 requests.jsonl
（仓库根），而不是 tmp/20261004-182918/B05/。本题目录下的 requests.jsonl 因此只有
5 条文档/字体请求，缺全部渲染记录。

本脚本把根文件里 request_file 指向 B05 的渲染行原样搬进本题 requests.jsonl，
保持字段不变（这是真实记录，不是编造），然后把根文件里剩余的行留在原地。
"""
import io
import json
import os

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TASK_TMP = os.path.join(ROOT, "tmp", "20261004-182918", "B05")
ROOT_LOG = os.path.join(ROOT, "requests.jsonl")
DST = os.path.join(TASK_TMP, "requests.jsonl")

rows = []
with io.open(ROOT_LOG, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

moved, kept = [], []
for r in rows:
    rf = (r.get("request_file") or "").replace("\\", "/")
    resp = (r.get("response_file") or "").replace("\\", "/")
    if rf.find("/B05/") >= 0 or resp.find("/B05/") >= 0:
        moved.append(r)
    else:
        kept.append(r)

# renumber the moved rows so ids stay unique and monotonic within this task
moved.sort(key=lambda r: r["started_at"])
existing_max = 0
with io.open(DST, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        rid = json.loads(line)["request_id"]
        if rid.startswith("B05-req-"):
            existing_max = max(existing_max, int(rid.split("-")[-1]))

seq = existing_max
with io.open(DST, "a", encoding="utf-8") as out:
    for r in moved:
        seq += 1
        r = dict(r)
        r["request_id"] = "B05-req-%03d" % seq
        r["imported_from"] = ("the render log for this request was written to the repository-root "
                              "requests.jsonl because snapkit.configure() had not been called in the "
                              "earlier session; it is copied here verbatim with only request_id "
                              "renumbered, no field values altered")
        out.write(json.dumps(r, ensure_ascii=False) + "\n")

with io.open(ROOT_LOG, "w", encoding="utf-8") as out:
    for r in kept:
        out.write(json.dumps(r, ensure_ascii=False) + "\n")

print("moved %d render rows, kept %d in root, next id = B05-req-%03d"
      % (len(moved), len(kept), seq))