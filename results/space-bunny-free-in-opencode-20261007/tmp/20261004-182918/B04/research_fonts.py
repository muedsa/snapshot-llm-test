# B04: fetch the service's own /fonts list (host = the service base URL, per the AI guide).
import os, sys
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, state as S

TASK = "B04"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
st, path = snapkit.fetch_doc("https://open-snapshot.muedsa.com/fonts", "fonts-list.txt", "font_list")
print(st, path)
