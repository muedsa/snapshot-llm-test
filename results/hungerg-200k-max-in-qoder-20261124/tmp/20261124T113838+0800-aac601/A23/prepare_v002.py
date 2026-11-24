from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("a23", HERE / "prepare_A23.py")
a23 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a23)

failed = json.loads((HERE / "final-review-v001.json").read_text(encoding="utf-8"))
a23.record_views(failed, "v001")

directory = HERE / "v002"
directory.mkdir(parents=True, exist_ok=True)
(directory / "cover.snapshot").write_text(a23.cover_dsl(), encoding="utf-8")
for index in range(6):
    (directory / f"frame-{index+1:02d}.snapshot").write_text(a23.frame_dsl(index), encoding="utf-8")
a23.sk.write_json(directory / "frame-data.json", a23.frame_data("v002"))
a23.sk.write_json(directory / "timing.json", a23.timing_data())
print("prepared v002")
