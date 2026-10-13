"""Append A21 round records (requests are already logged by render.py with a round tag)."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
ROOT = RUN_DIR.parents[1]
LOG = RUN_DIR / "A21"


def rec(fname, obj):
    obj.setdefault("ts", datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"))
    obj.setdefault("path_base", "suite_root")
    with (LOG / fname).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


VIEWS = [
    ("A21-r01-view-01", "round-01", "r01-portrait.png", "full",
     "竖版首版：构件 + 品牌名 + kicker/日期 + 96px 主标题 + 议程/讲者 + 分隔线 + 网址；"
     "底部 430px 色带太空，读起来像未收尾"),
    ("A21-r01-view-02", "round-01", "r01-wide.png", "full",
     "横版首版：左读右牌；品牌行 “叠光 Layerlight” 一度越过面板右界，"
     "改为叠光 46px + Layerlight 30px 两行后收进面板"),
    ("A21-r01-view-03", "round-01", "r01-portrait.png", "full",
     "底部预留带改为 270px 后重新渲染并查看：正文止于 883px，顶部 150px 与底部 270px "
     "都是干净的可用扩展区，无占位文字；两图共用同一五构件与同一色板"),
]

ITERS = [
    ("r01", "round-01", None, "baseline",
     ["r01-portrait.png", "r01-wide.png"],
     "两张首版渲染后看图：竖版底部色带过高显得空；横版品牌单行 46px 越过右面板边界"
     "（构建期自检已先报 outside=叠光 Layerlight）。",
     "品牌块统一改为 叠光 46px + Layerlight 30px + tagline 26px 三行；"
     "竖版底部预留带 430→270px。",
     "重新渲染并查看两图：outside/overlaps 均为空，最低字号 26（标题 96/88）"),
]

for vid, rnd, img, kind, note in VIEWS:
    rec("image-views.jsonl", {"view_id": vid, "task_id": "A21", "round": rnd,
                              "image": f"tmp/{RUN_DIR.name}/A21/{img}", "kind": kind,
                              "note": note, "dsl_version": "r01",
                              "tool": "Read (multimodal image view)"})
for ver, rnd, parent, typ, arts, obs, chg, recheck in ITERS:
    rec("iterations.jsonl", {"version": ver, "round": rnd, "parent": parent,
                             "type": typ,
                             "artifacts": [f"tmp/{RUN_DIR.name}/A21/{x}" for x in arts],
                             "observed": obs, "change": chg, "recheck": recheck})
print("logged", len(VIEWS), "views", len(ITERS), "iterations")
