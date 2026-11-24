from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
script = HERE / "prepare_A21.py"
spec = importlib.util.spec_from_file_location("a21", script)
a21 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a21)

review = json.loads((HERE / "round-03/final-review-v002.json").read_text(encoding="utf-8"))
existing = {item["iteration_id"] for item in a21.sk.read_jsonl(HERE / "iterations.jsonl")}
for kind, viewed in review["reviewed"].items():
    iteration_id = f"{a21.RUN}-A21-round-03-v002-{kind}"
    if iteration_id in existing:
        continue
    a21.sk.append_jsonl(HERE / "iterations.jsonl", {
        "iteration_id": iteration_id,
        "task_id": "A21",
        "case_id": kind,
        "version_id": "round-03-v002",
        "parent_version": "round-03-v001",
        "type": "visual",
        "image_path": viewed["image"],
        "image_paths": [viewed["image"]],
        "viewed_at": viewed["viewed_at"],
        "timezone": "+08:00",
        "observable_issues": viewed["observed"],
        "changes": "修正文字盒内缩与部分横版文字盒右坐标，但网址仍使用负宽度。",
        "review_and_comparison": review["conclusion"],
        "completed_visual_iteration": False,
    })

directory = HERE / "round-03/v003"
directory.mkdir(parents=True, exist_ok=True)
for kind in ("portrait", "wide"):
    dsl, _ = a21.build_dsl(3, kind)
    (directory / f"launch-{kind}.snapshot").write_text(dsl, encoding="utf-8")
    background, _ = a21.build_dsl(3, kind, False)
    (directory / f"background-{kind}.snapshot").write_text(background, encoding="utf-8")
a21.sk.write_json(directory / "design-tokens.json", a21.tokens(3))
a21.sk.write_json(directory / "content-map.json", a21.content_map(3))
print("prepared round-03 v003")
