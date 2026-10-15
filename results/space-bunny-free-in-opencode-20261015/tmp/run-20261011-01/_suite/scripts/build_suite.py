#!/usr/bin/env python
# 全套总交付生成器 —— **只有在 30 题全部 completed 后才运行**。
# 生成 outputs/run-20261011-01/_suite/ 下 index.md、gallery.md、snapshot-usage.md、
# task-metrics.json；suite-state.json 由 suite_state.py artifacts 收尾。
#
# 设计要点：
#   · 不写死任何一张图的位置——按目录扫描 <task>/**/final.png，逐张建索引，
#     所以 A21/A22 的多轮、A 的多产物、B 的十件用例都能自动归组。
#   · Markdown 链接一律相对于本文档所在的 _suite/ 目录（如 ../A01/case-01/final.png），
#     整目录复制后仍可浏览，不依赖远程图片地址或机器绝对路径。
#   · 计数从文件系统与各题 task-metrics.json 现场统计，不手填。
#
# 启动基准：总任务根 (suite_root)。用法：python build_suite.py [--force]
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
RUN = "run-20261011-01"
OUT = f"outputs/{RUN}"
SUITE = f"{OUT}/_suite"
ORDER = ([f"A{i:02d}" for i in range(1, 25)]
         + [f"B{i:02d}" for i in range(1, 7)])
NAME = {}
for t in ORDER:
    d = ROOT / "tasks"
    hit = [x for x in d.iterdir() if x.name.startswith(t + "-")]
    NAME[t] = hit[0].name.split("-", 1)[1] if hit else t


def state() -> dict:
    p = ROOT / SUITE / "suite-state.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def status_of(st: dict, t: str) -> str:
    for row in st.get("tasks", []):
        if isinstance(row, dict) and row.get("id") == t:
            return row.get("status", "pending")
    return "pending"


def images_of(task: str) -> list[dict]:
    """扫出该题下的全部交付图，按目录分组，组内按路径排序。"""
    base = ROOT / OUT / task
    if not base.is_dir():
        return []
    groups: dict[str, list[dict]] = {}
    for png in sorted(base.rglob("*.png")):
        if png.name == "final.png":
            kind = "final"
        elif "contact" in png.name.lower():
            kind = "contact"
        else:
            kind = "other"
        dsl = png.with_suffix(".snapshot")
        groups.setdefault(png.parent.relative_to(base).as_posix(), []).append(
            {"png": png.relative_to(ROOT).as_posix(),
             "name": png.name,
             "dsl": dsl.relative_to(ROOT).as_posix() if dsl.exists() else None,
             "bytes": png.stat().st_size, "kind": kind})
    out = []
    for g in sorted(groups):
        out.append({"group": g, "items": groups[g]})
    return out


def rel(path: str) -> str:
    """把 suite_root 相对路径转成相对 _suite/ 的 Markdown 链接。"""
    return "../" + path[len(OUT) + 1:].replace("\\", "/")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="即使未满 30/30 也生成（仅用于预览，不建议）")
    args = ap.parse_args()

    st = state()
    done = [t for t in ORDER if status_of(st, t) == "completed"]
    print(f"completed {len(done)}/30")
    if len(done) < 30 and not args.force:
        raise SystemExit("未满 30/30，拒绝生成总交付（如需预览加 --force）")

    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    per_task = []
    total_png = total_dsl = 0
    for t in ORDER:
        groups = images_of(t)
        n_png = sum(len(g["items"]) for g in groups)
        n_dsl = sum(1 for g in groups for it in g["items"] if it["dsl"])
        total_png += n_png
        total_dsl += n_dsl
        tm = ROOT / OUT / t / "task-metrics.json"
        counts = {}
        if tm.exists():
            counts = json.loads(tm.read_text(encoding="utf-8")).get("counts", {})
        per_task.append({
            "id": t, "name": NAME[t], "status": status_of(st, t),
            "images": n_png, "with_dsl": n_dsl,
            "png_with_dsl_pairs": sum(1 for g in groups for it in g["items"]
                                      if it["dsl"]),
            "groups": groups, "counts": counts,
            "entry": f"{OUT}/{t}/index.md" if (ROOT / OUT / t / "index.md").exists()
                     else f"{OUT}/{t}/",
        })

    # ── gallery.md ───────────────────────────────────────────────────
    g = [f"# 全套画廊 · {RUN}\n",
         f"> 生成时间：{now}　·　共 **{total_png}** 张交付图，"
         f"其中 **{total_dsl}** 张带同名 `.snapshot`\n",
         "全部为 open-snapshot 服务的真实响应。图片与 DSL 链接均相对于本文件所在的 "
         "`_suite/` 目录，整目录复制后仍可浏览。\n"]
    for row in per_task:
        if not row["groups"]:
            continue
        g.append(f"\n---\n\n## {row['id']} · {row['name']}"
                 f"　（{row['status']}，{row['images']} 张）\n")
        for grp in row["groups"]:
            title = grp["group"] if grp["group"] != "." else "（根目录）"
            g.append(f"### {title}\n")
            for it in grp["items"]:
                stem = it["png"][:-4]
                cap = it["name"].rsplit(".", 1)[0]
                if grp["group"] != ".":
                    cap = f"{grp['group']} · {cap}"
                g.append(f"**{cap}**\n")
                g.append(f"![{cap}]({rel(it['png'])})\n")
                line = f"- PNG：[`{stem}.png`]({rel(it['png'])})"
                if it["dsl"]:
                    line += f" · DSL：[`{stem}.snapshot`]({rel(it['dsl'])})"
                g.append(line + "\n")
    (ROOT / SUITE / "gallery.md").write_text("\n".join(g), encoding="utf-8")

    # ── index.md ─────────────────────────────────────────────────────
    i = [f"# 全套索引 · {RUN}\n", f"> 生成时间：{now}\n",
         f"**状态**：{len(done)}/30 题 completed　·　"
         f"**交付图**：{total_png} 张　·　**PNG+DSL 配对**：{total_dsl} 对\n",
         "路径基准：`path_base=suite_root`。本文件在 `outputs/run-20261011-01/_suite/`。\n",
         "| 题 | 名称 | 状态 | 图数 | 看图次数 | 产物入口 | 画廊 |",
         "|---|---|---|---|---|---|---|"]
    for row in per_task:
        i.append(f"| {row['id']} | {row['name']} | {row['status']} | "
                 f"{row['images']} | {row['counts'].get('image_views', '—')} | "
                 f"[`{row['id']}/`](../{row['id']}/) | "
                 f"[图](gallery.md#{row['id'].lower()}-·-{row['name']}) |")
    i.append(f"\n## 总览\n")
    i.append(f"- **总画廊**：[`gallery.md`](gallery.md)（逐图展示，含 PNG 与 `.snapshot` 链接）\n"
             f"- **DSL 与方法**：[`snapshot-usage.md`](snapshot-usage.md)\n"
             f"- **指标**：[`task-metrics.json`](task-metrics.json)\n"
             f"- **进度**：[`suite-state.json`](suite-state.json)\n")
    i.append(f"\n## 输出与临时目录\n")
    i.append(f"- 输出根：`{OUT}/`（各题一个子目录，外加 `_suite/`）\n"
             f"- 临时根：`tmp/{RUN}/`（`drafts/`、`preview/`、`responses/`、"
             f"`requests.jsonl`、各轮修正脚本等过程证据，全部保留）\n"
             f"- 共享准备与检查点：`tmp/{RUN}/_suite/`\n")
    (ROOT / SUITE / "index.md").write_text("\n".join(i), encoding="utf-8")

    # ── task-metrics.json（总汇总） ──────────────────────────────────
    req = sum(int(r["counts"].get("requests", 0)) for r in per_task)
    ok = sum(int(r["counts"].get("requests_ok", 0)) for r in per_task)
    views = sum(int(r["counts"].get("image_views", 0)) for r in per_task)
    mt = {
        "schema_version": 1, "suite_id": RUN, "path_base": "suite_root",
        "generated_at": now, "task_count": len(ORDER),
        "completed": len(done),
        "aggregation_scope": "只累计每题顶层 task-metrics.json 的 counts，"
                             "不把同题的 round/case 明细重复相加；"
                             "shared 计数单列。",
        "totals": {"images": total_png, "images_with_dsl": total_dsl,
                   "requests": req, "requests_ok": ok,
                   "image_views": views},
        "per_task": [{"id": r["id"], "name": r["name"], "status": r["status"],
                      "images": r["images"], "images_with_dsl": r["with_dsl"],
                      "counts": r["counts"]} for r in per_task],
        "wall_clock_note": "各题起止见其 task-metrics.json 的 timings；"
                           "A12 的 active_span 含一次跨夜间隔约 15h51m，已在该题标注。",
    }
    (ROOT / SUITE / "task-metrics.json").write_text(
        json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"-> _suite/index.md  _suite/gallery.md  _suite/task-metrics.json")
    print(f"   {total_png} images, {total_dsl} with .snapshot, "
          f"{req} requests, {views} image views")


if __name__ == "__main__":
    main()