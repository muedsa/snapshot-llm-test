"""把归并进来的渲染行的 task_id 从 _suite 改成 B05，并保留原始 id 作为字段。

这些行的 request_id 已由 fix_request_log.py 重编为 B05-req-NNN，
原始 id 记录在 original_request_id，来源说明记录在 imported_from。
其余字段（时间、状态、耗时、文件路径、requestId、错误）一律不动。
"""
import io
import json

DST = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B05\requests.jsonl"

out = []
n = 0
with io.open(DST, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("task_id") == "_suite":
            r["original_request_id"] = r["request_id"]
            r["original_task_id"] = "_suite"
            r["task_id"] = "B05"
            n += 1
        out.append(r)

with io.open(DST, "w", encoding="utf-8") as fh:
    for r in out:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

ids = [r["request_id"] for r in out]
print("fixed %d rows; total %d; unique ids %s" % (n, len(out), len(ids) == len(set(ids))))