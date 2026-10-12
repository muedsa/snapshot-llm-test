"""去重 tool-usage.jsonl。

log_tools.py 在修好 import 之后被运行了两次（第一次在写完全部 12 条之后
因缺少 import io 而在收尾的统计语句处失败），因此每个工具事件出现两份。
本脚本按 (tool, purpose, inputs) 去重，保留第一次出现的那条。
"""
import io
import json

DST = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B05\tool-usage.jsonl"

rows = []
with io.open(DST, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

seen, out, removed = set(), [], 0
for r in rows:
    k = (r["tool"], r["purpose"], json.dumps(r["inputs"], ensure_ascii=False))
    if k in seen:
        removed += 1
        continue
    seen.add(k)
    out.append(r)

out.sort(key=lambda r: r["ts"])

with io.open(DST, "w", encoding="utf-8") as fh:
    for r in out:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

print("kept %d unique tool events, removed %d duplicates" % (len(out), removed))