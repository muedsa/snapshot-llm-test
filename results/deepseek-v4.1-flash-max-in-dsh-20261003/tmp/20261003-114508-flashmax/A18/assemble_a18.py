"""Assemble the A18 deliverables and rewrite task-metrics.json from the real log."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from suite_common import build_metrics, write_json, task_out, count_requests  # noqa: E402

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A18"
OUT = task_out("A18")


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    pairs = [
        ("three-act-story.v11.snapshot", "three-act-story.snapshot"),
        ("three-act-story.v11.png", "three-act-story.png"),
        ("story-audit.json", "story-audit.json"),
        ("rationale.md", "rationale.md"),
    ]
    for src, dst in pairs:
        shutil.copyfile(os.path.join(TMP, src), os.path.join(OUT, dst))
        print(f"  {dst:28s} {os.path.getsize(os.path.join(OUT, dst)):>8d} B  sha256={sha(os.path.join(OUT, dst))[:16]}")

    # keep the two required previews plus the 400 px thumbnail in the temp directory only
    for extra in ("story-preview-a.v11.png", "story-preview-b.v11.png",
                  "three-act-story.v11.thumb400.png"):
        p = os.path.join(TMP, extra)
        if os.path.exists(p):
            print(f"  (temp) {extra:40s} {os.path.getsize(p):>8d} B")

    req = count_requests("A18")
    m = build_metrics(
        "A18",
        title="守恒对象的三幕视觉叙事",
        status="completed",
        started_at="2026-10-03T13:10:00+08:00",
        ended_at="2026-10-03T13:52:00+08:00",
        outputs=["three-act-story.png", "three-act-story.snapshot", "story-audit.json",
                 "rationale.md", "snapshot-usage.md", "task-metrics.json"],
        final_pngs=1,
        dsl_versions=11,
        notes=[
            "最终图 1600x1000 由服务真实 200 响应得到（A18-REQ-0024），未后处理；同名 .snapshot 无 BOM。",
            "几何由 story-audit.json 自动校验：每幕 15 个单元、颜色各 5、全部完整可见、"
            "单元互不重叠、不压节点、连线不穿单元、第三幕每节点恰好 5 个且含至少两种颜色。",
            "两种叙事构图各做了真实 1600x1000 预览（story-preview-a/b.v11.png，存临时目录）后选定 B。",
            "三幕的连线全部是直线辐条；早期用“径向+弧+径向”折线时视觉上读成同心环，已改回。",
            "颜色轮换让同一批单元在每一幕的接收者不同，避免只靠颜色判断关系。",
        ],
        extra={
            "final_image": {"file": "three-act-story.png", "width": 1600, "height": 1000,
                            "format": "PNG", "bytes": os.path.getsize(os.path.join(OUT, "three-act-story.png")),
                            "sha256": sha(os.path.join(OUT, "three-act-story.png")), "viewed": True},
            "thumbnail_review": {"width": 400, "height": 250,
                                 "file": "tmp/20261003-114508-flashmax/A18/three-act-story.v11.thumb400.png",
                                 "viewed": True,
                                 "conclusion": "400px 宽缩略图下三幕结构、节点数与连线方向仍可读"},
            "candidate_previews": [
                {"id": "A", "file": "tmp/20261003-114508-flashmax/A18/story-preview-a.v11.png",
                 "request_id": "A18-REQ-0022", "framing": "三块带边框面板并排"},
                {"id": "B", "file": "tmp/20261003-114508-flashmax/A18/story-preview-b.v11.png",
                 "request_id": "A18-REQ-0023", "framing": "无边框连续画布 + 幕间流向箭头",
                 "chosen": True},
            ],
            "requirements_checked": json.load(open(os.path.join(OUT, "story-audit.json"),
                                                   encoding="utf-8"))["checks"],
            "units_per_act": 15,
            "unit_diameter": 36,
            "node_count": 3,
        },
    )
    m["iterations"]["image_reviews"] = 12
    m["iterations"]["image_reviews_note"] = "read_image：线段探针 2 + 预览 a/b 各 2 轮 + 最终图 2 + 缩略图 1 + 迭代过程 3"
    write_json(os.path.join(OUT, "task-metrics.json"), m)
    print("task-metrics.json:", req["requests_total"], "requests,",
          req["render_success"], "success,", req["render_failed"], "failed")


if __name__ == "__main__":
    main()
