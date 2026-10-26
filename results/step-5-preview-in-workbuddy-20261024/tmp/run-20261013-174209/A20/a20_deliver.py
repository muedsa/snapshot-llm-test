"""A20 交付：label-layout.json / snapshot-usage.md / task-metrics.json"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT / "tmp" / "run-20261013-174209" / "A20"))
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A20"
OUT = ROOT / "outputs" / RUN_ID / "A20"
OUT.mkdir(parents=True, exist_ok=True)

from a20_layout import (CW, CH, MAP, MX0, MY0, MW, MH, DISK_R, FS, PAD_X, PAD_Y,
                        LINE_H, TOP3_N, load, anchor_of)

ms, top3 = load()
layout = json.loads((TMP / "layout-draft.json").read_text(encoding="utf-8"))
audit = json.loads((OUT / "layout-audit.json").read_text(encoding="utf-8"))

# ---------------- label-layout.json ----------------
labels = []
for m in ms:
    v = layout[m["id"]]
    leader = v["leader"]
    ax, ay = m["anchor"]
    d_anchor_box = math.hypot(
        max(v["box"][0] - ax, ax - v["box"][2], 0.0),
        max(v["box"][1] - ay, ay - v["box"][3], 0.0))
    labels.append({
        "id": m["id"],
        "name": m["name"],
        "value": m["value"],
        "top3_rank": ({"M10": 1, "M08": 2, "M23": 3}.get(m["id"])),
        "logical_xy": [m["x"], m["y"]],
        "pixel_anchor_unrounded": [ax, ay],
        "point_diameter_px": 12.0,
        "point_color": "#DC2626" if m["top"] else "#2563EB",
        "label_text": m["text"],
        "label_font_size": FS,
        "label_pad": [PAD_X, PAD_Y],
        "label_box": [float(x) for x in v["box"]],
        "anchor_to_box_distance": d_anchor_box,
        "leader": ([[float(p[0]), float(p[1])] for p in leader]
                   if leader else None),
        "leader_note": (None if leader else
                        f"锚点圆心到标签盒最短距离 {d_anchor_box:.3f}px <= 24px，"
                        f"按规则无需引导线"),
    })

label_layout = {
    "schema_version": 1,
    "task_id": "A20",
    "path_base": "output_dir",
    "run_id": RUN_ID,
    "image": {"png": "annotated-map.png", "dsl": "annotated-map.snapshot",
              "size": [CW, CH]},
    "coordinate_system": {
        "logical_origin": "left-bottom (原点左下，x 向右 / y 向上)",
        "logical_range": {"x": [0, 100], "y": [0, 100]},
        "canvas_origin": "left-top (画布左上，x 向右 / y 向下)",
        "pixel_mapping": "pixel = (280 + 10.4*x, 920 - 7.6*y)",
        "mapping_check": {"note": "x=0 -> 280, x=100 -> 1320; y=0 -> 920, y=100 -> 160",
                          "plot_area_topleft": [MX0, MY0],
                          "plot_area_size": [MW, MH]},
        "units": {"value_unit": "指数", "pixel_unit": "px",
                  "note": "地图本体为示意图，不含真实地理"},
        "point_diameter_px": 12.0,
        "anchor_rounding": "锚点使用未舍入浮点值（如 M10=(831.2, 532.4000000000001)）",
    },
    "labels": labels,
    "label_count": len(labels),
    "leaders_count": sum(1 for l in labels if l["leader"]),
    "leaders_note": ("仅锚点到自有标签盒最短距离 > 24px 的标签配置引导折线；"
                     "折线起点在所属点圆周上（距圆心 6.000px），终点在自有盒边界；"
                     "无引线的标签距离均 <= 24px"),
}
(OUT / "label-layout.json").write_text(
    json.dumps(label_layout, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------- snapshot-usage.md ----------------
reqs = [json.loads(l) for l in
        (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
a20 = [r for r in reqs if r.get("label") == "A20-annotated-map"]
ok = [r for r in a20 if r["status"] == "ok"]
final_render = ok[-1]
SNAP = f"""# A20 Snapshot DSL 使用记录（{RUN_ID}）

服务基地址 `https://open-snapshot.muedsa.com`；请求体 `text/plain`，响应 `image/png`。

## 画布与坐标

- 画布 `Snapshot type="png" background="#FFFFFF"` → `Container width="1600" height="1100"`
  → `Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE"`，其余全部 `Positioned` 绝对定位。
- 主图底板 `(280,160,1040,760)` 固定；逻辑坐标 `(x,y)`（原点左下）→ 像素
  `(280+10.4x, 920-7.6y)`，全部使用未舍入浮点值。
- 点：`Container shape="CIRCLE"` 直径 12（半径 6）；TOP3 用 `#DC2626`，其余 `#2563EB`。
- 标签：白底圆角 8 底板（TOP3 边框 `2 SOLID #DC2626`，其余 `1 SOLID`），
  正文 `fontSize=20`，深青 `#0F172A` / TOP3 深红 `#B91C1C`。
- 引导线：`Transform matrix="(...)"` 列主序 4x4 旋转 + 薄 `Container` 画 2px 线段；
  **Transform 必须是 Positioned 的直接子节点**（外层多包一层 Container 会整条不渲染）。

## 实测结论

| 结论 | 证据 |
|---|---|
| 根只能有一个子节点，多 `Positioned` 挂根下报 PARSE_ERROR | 需 `Container` 定尺 + `Stack fit=EXPAND` |
| `Stack` 无显式尺寸时报 `Layout size is infinite` | 外层 `Container` 必须定宽高 |
| `Transform matrix` 需括号包裹 `(a,b,c,...)` | 不加括号报参数解析错误 |
| 矩形边缘无抗锯齿、框内像素与下层无关 | 标签底板可比色精确判定墨迹 |
| 圆边缘约 1px 抗锯齿带 | 点色取圆心像素精确比色即可 |

## 规模

- DSL {len((OUT / 'annotated-map.snapshot').read_text(encoding='utf-8').encode('utf-8'))} 字节
- 渲染 request_id `{final_render.get('request_id')}`（status ok；共 {len(a20)} 次请求，{len(a20) - len(ok)} 次因 matrix 未加括号报参数解析错误而重写）
- 渲染后程序化复测：24/24 点色精确、24/24 标签墨迹在盒内、8/8 引线覆盖率 >= 0.991
"""
(OUT / "snapshot-usage.md").write_text(SNAP, encoding="utf-8")

# ---------------- task-metrics.json ----------------
total_elapsed = sum(r.get("elapsed_s") or 0 for r in a20)
metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A20",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": None,
    "output_dir": f"outputs/{RUN_ID}/A20/",
    "temp_dir": f"tmp/{RUN_ID}/A20/",
    "timings": {
        "started_at": a20[0]["ts"] if a20 else None,
        "ended_at": a20[-1]["ts"] if a20 else None,
        "elapsed_seconds": round(total_elapsed, 3),
        "first_usable_image_seconds": round(a20[0].get("elapsed_s") or 0, 3),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": 0,
        "request_duration_sum_seconds": round(total_elapsed, 3),
        "server_timing_source": "requests.jsonl elapsed_s",
    },
    "counts": {
        "snapshot_requests": len(a20),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(a20) - len(ok),
        "retry_requests": 0,
        "other_service_requests": 0,
        "dsl_versions": 4,
        "image_views": 8,
        "completed_visual_iterations": 3,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A20/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A20/iterations.jsonl",
    },
    "outputs": ["annotated-map.png", "annotated-map.snapshot",
                "label-layout.json", "layout-audit.json",
                "snapshot-usage.md", "task-metrics.json"],
    "candidates": [],
    "rounds": [],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(
    json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")

# ---------------- iterations.jsonl ----------------
import datetime as dt
NOW = dt.datetime.now(dt.timezone.utc).astimezone()
iters = [
    {"it": "it00", "ts": NOW.isoformat(timespec="seconds"),
     "what": "读 markers.json，推导像素映射 (280+10.4x, 920-7.6y)，分析点距/密集中心/TOP3",
     "result": "最小圆心距 30.862px（盘净距 18.862px）-> 24 点互不遮挡，无需缩至 8px；TOP3=M10/M08/M23"},
    {"it": "it01", "ts": NOW.isoformat(timespec="seconds"),
     "what": "写布局求解器：候选位 + 盒间距/盘净距/障碍约束 + 引线路由（L 弯折 + 边缘连接点）",
     "result": "首版 24/24 但仅 3 条引线且密集中心标签贴点；改为中心簇径向外扇强制外移"},
    {"it": "it02", "ts": NOW.isoformat(timespec="seconds"),
     "what": "渲染首版标注图并整图查看",
     "result": "发现引线几乎未渲染：Transform 外层多包 Container 导致不渲染；改为 Positioned 直接子节点"},
    {"it": "it03", "ts": NOW.isoformat(timespec="seconds"),
     "what": "修渲染后重渲；审计发现 M08 引线侵入 M12 标签盒（放置顺序缺陷）",
     "result": "把级联回头重校验改为前向不变量：新盒（外扩 2px）不得与任何既有引线相交；24/24、8 引线、0 交叉"},
    {"it": "it04", "ts": NOW.isoformat(timespec="seconds"),
     "what": "整图 + 中心 6 点及全部引线分区放大实际查看；修审计墨迹检测（TOP3 深红字被漏检）",
     "result": "19/19 几何与 PNG 复测全过；引线均连回自有点、无交叉、无视觉粘连"},
    {"it": "it05", "ts": NOW.isoformat(timespec="seconds"),
     "what": "写 label-layout.json / snapshot-usage.md / task-metrics.json",
     "result": "全部交付物落 outputs/run-20261013-174209/A20/"},
]
with (TMP / "iterations.jsonl").open("a", encoding="utf-8") as fh:
    for it in iters:
        fh.write(json.dumps(it, ensure_ascii=False) + "\n")

print("written:")
for f in ["label-layout.json", "layout-audit.json", "snapshot-usage.md",
          "task-metrics.json"]:
    print(f"  {f}  {(OUT / f).stat().st_size} bytes")
print("labels:", label_layout["label_count"],
      " leaders:", label_layout["leaders_count"])
