"""临时探针：修正矩阵并渲染，确认旋转矩阵约定。"""
from pathlib import Path
import sys

sys.path.insert(0, "tmp/run-20261013-174209/_suite")
import render as R  # noqa: E402

root = Path(".").resolve()
src = Path("tmp/run-20261013-174209/A01/probe-rot2.snapshot")
text = src.read_text(encoding="utf-8")
bad = "(0.5,0.8660254,0,0,-0.8660254,0.5,0,0,0,0,1,0,0,0,0,0,1)"
good = "(0.5,0.8660254,0,0,-0.8660254,0.5,0,0,0,0,1,0,0,0,0,1)"
assert bad in text
text = text.replace(bad, good)
dst = Path("tmp/run-20261013-174209/A01/probe-rot3.snapshot")
dst.write_text(text, encoding="utf-8")
res = R.render(
    root / dst,
    root / "tmp/run-20261013-174209/A01/probe-rot3.png",
    root,
    R.Log(root, "run-20261013-174209", "A01"),
    req_type="probe",
    label="rotation-convention-3",
)
print(res["record"]["status"], res["record"]["http_status"], res["record"].get("error"))
