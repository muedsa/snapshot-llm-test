"""A20 · assemble the outputs and write task-metrics.json."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from suite_common import build_metrics, write_json, task_out, count_requests  # noqa: E402

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A20"
OUT = task_out("A20")


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    copies = [
        ("annotated-map.v1.snapshot", "annotated-map.snapshot"),
        ("annotated-map.final.png", "annotated-map.png"),
        ("label-layout.json", "label-layout.json"),
        ("layout-audit.json", "layout-audit.json"),
    ]
    for src, dst in copies:
        shutil.copyfile(os.path.join(TMP, src), os.path.join(OUT, dst))
        print(f"  {dst:26s} {os.path.getsize(os.path.join(OUT, dst)):>9d} B  {sha(os.path.join(OUT, dst))[:16]}")

    audit = json.load(open(os.path.join(OUT, "layout-audit.json"), encoding="utf-8"))
    layout = json.load(open(os.path.join(OUT, "label-layout.json"), encoding="utf-8"))
    req = count_requests("A20")
    far = [p["id"] for p in layout["points"] if p["leader"]["needs_leader"]]
    m = build_metrics(
        "A20",
        title="二十四密集点的无重叠标注",
        status="completed",
        started_at="2026-10-03T14:45:00+08:00",
        ended_at="2026-10-03T15:35:00+08:00",
        outputs=[c[1] for c in copies] + ["snapshot-usage.md", "task-metrics.json"],
        final_pngs=1,
        dsl_versions=1,
        notes=[
            "最终图 1600x1100 由服务真实 200 响应得到（A20-REQ-0003），未后处理；同名 .snapshot 无 BOM。",
            "锚点严格按 px = 280 + x/100*1040、py = 160 + (1-y/100)*760 映射，"
            "layout-audit.json 的 mapping_errors_over_0.01px 为空（最大误差 0）。",
            "24 个标签全部保留、无一删除；12px 圆点在本题中不需要缩小（最近两点距离 30.86px > 2×6px）"
            "，因此 dots_shrunk = 0，规则与判定一并记录。",
            "标签盒两两间隔 >= 4px、不覆盖任何点、引导线不穿标签文本、不与其它点相碰；"
            "线线交叉 1 处（上限 3），交叉处未画连接点。",
            "指数最高的 3 个点（M10 93 / M08 91 / M23 90）在图例与地图中同时标出。",
        ],
        extra={
            "final_image": {"file": "annotated-map.png", "width": 1600, "height": 1100,
                            "bytes": os.path.getsize(os.path.join(OUT, "annotated-map.png")),
                            "sha256": sha(os.path.join(OUT, "annotated-map.png")), "viewed": True},
            "local_zoom_review": {
                "file": "tmp/20261003-114508-flashmax/A20/zoom-centre.final.png",
                "region_px": [620, 420, 1100, 760], "scale": 3.0, "viewed": True,
                "conclusion": "中心密集区 6 个点（M08–M12、M18）与各自的引导线在 3× 放大下清晰可辨，"
                              "无压字、无错连"},
            "layout_audit": audit["checks"],
            "counts": audit["counts"],
            "crossings": audit["line_crossings"],
            "labels_needing_leader": far,
            "font_sizes": {"body": 20, "id": 20, "small": 18,
                           "note": "标签正文与编号均为 20px，满足 >=20 的要求；轴刻度 15px 属图表刻度而非标签正文"},
        },
    )
    m["iterations"]["image_reviews"] = 5
    m["iterations"]["image_reviews_note"] = ("read_image：annotated-map.v1.png、v2.png、final.png 各 1 次，"
                                             "中心密集区 3× 放大 2 次")
    write_json(os.path.join(OUT, "task-metrics.json"), m)
    print("task-metrics.json:", req["requests_total"], "requests",
          req["render_success"], "success", req["render_failed"], "failed")
    print("audit all_checks_pass:", audit["all_checks_pass"])


if __name__ == "__main__":
    main()
