"""去重 iterations.jsonl。

log_b05.py 被执行了两次（第一次在修正 requests.jsonl 之前），导致每条迭代记录
出现两份完全相同的行。本脚本按 iteration_id 去重，保留第一次出现的那条
（内容完全相同，仅顺序不同），并把被删的行数写入 note 字段说明。
"""
import io
import json

DST = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B05\iterations.jsonl"

rows = []
with io.open(DST, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

seen, out, removed = set(), [], 0
for r in rows:
    k = r["iteration_id"]
    if k in seen:
        removed += 1
        continue
    seen.add(k)
    out.append(r)

out.sort(key=lambda r: r["iteration_id"])
for r in out:
    r["note"] = ((r.get("note") or "") +
                 " | duplicate rows produced by re-running log_b05.py were removed"
                 ).strip(" |")

with io.open(DST, "w", encoding="utf-8") as fh:
    for r in out:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

print("kept %d unique iterations, removed %d duplicate rows" % (len(out), removed))