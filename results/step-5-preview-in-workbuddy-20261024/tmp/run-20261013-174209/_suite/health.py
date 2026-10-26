import sys
import time

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

dsl = '<Snapshot type="png" background="#FFFFFF"><Container width="100" height="50" color="#FF0000"/></Snapshot>'
t = time.time()
r = R.post_render(dsl, "https://open-snapshot.muedsa.com/snapshot", timeout=100)
print("health:", r.get("status"), r.get("content_type"), round(time.time() - t, 1), "s",
      (r.get("error") or "")[:120])
