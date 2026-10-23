"""A22 过程留痕：看图事件与迭代记录。

用法
    python -I -X utf8 a22_log.py views <round>          # 按 views-manifest 记看图事件
    python -I -X utf8 a22_log.py iter <round> <type> <parent> "<observed>" "<change>" "<rereview>"
    python -I -X utf8 a22_log.py note <round> <event_id> "<说明>"    # 给某条看图事件加批注
    python -I -X utf8 a22_log.py summary <round>        # 打印该轮已记录的条数

时间戳用本机当前时间并显式带 +08:00。所有写入只追加，不覆盖既有记录。
`note` 子命令不修改原事件字段（只增不改），把说明追加到该轮的 notes 列表里，
用于标注「这条事件指向的视图实际没能打开」这类事后确认。
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
SUITE_ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
TMP = SUITE_ROOT / "tmp" / RUN_ID / "A22"
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A22"
TZ = dt.timezone(dt.timedelta(hours=8))


def now() -> str:
    return dt.datetime.now(TZ).isoformat(timespec="seconds")


def rel(p: pathlib.Path) -> str:
    return str(p.relative_to(SUITE_ROOT)).replace("\\", "/")


def append_jsonl(path: pathlib.Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_jsonl(path: pathlib.Path) -> list:
    if not path.exists() or not path.stat().st_size:
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip()]


def cmd_views(rnd: int) -> int:
    man = TMP / "preview" / ("round-%02d" % rnd) / "views-manifest.json"
    if not man.exists():
        raise SystemExit("没有 views-manifest.json，请先跑 a22_build.py views %d" % rnd)
    doc = json.loads(man.read_text(encoding="utf-8"))
    png = OUT / ("round-%02d" % rnd) / "dashboard.png"
    p = TMP / "viewing-evidence.json"
    ev = {"rounds": {}}
    if p.exists() and p.stat().st_size:
        ev = json.loads(p.read_text(encoding="utf-8"))
    ev.setdefault("rounds", {})
    blk = ev["rounds"].setdefault(str(rnd), {"image_open_events": []})
    for v in doc["views"]:
        blk["image_open_events"].append({
            "event_id": "a22-r%02d-view-%s-%03d" % (rnd, v["name"],
                                                    len(blk["image_open_events"]) + 1),
            "round": rnd,
            "view": v["name"],
            "view_path": v.get("out"),
            "source_image": rel(png),
            "source_sha256": v.get("source_sha256"),
            "box": v.get("box"),
            "scale": v.get("scale"),
            "opened_at": now(),
            "opened_at_precision": "second",
            "tool": "Read（实际打开图像文件查看）",
        })
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    return len(blk["image_open_events"])


def cmd_iter(rnd: int, itype: str, parent: str, observed: str,
             change: str, rereview: str) -> int:
    rec = {
        "iteration_id": "a22-r%02d-%s-%s" % (rnd, itype, now().replace(":", "").split("+")[0][-6:]),
        "round": rnd,
        "type": itype,
        "parent": parent,
        "observed_problem": observed,
        "change": change,
        "rereview": rereview,
        "recorded_at": now(),
        "recorded_at_precision": "second",
    }
    append_jsonl(TMP / "iterations.jsonl", rec)
    return len(read_jsonl(TMP / "iterations.jsonl"))


def cmd_note(rnd: int, event_id: str, text: str) -> int:
    """给某条看图事件追加批注（不改原字段）。"""
    p = TMP / "viewing-evidence.json"
    ev = {"rounds": {}}
    if p.exists() and p.stat().st_size:
        ev = json.loads(p.read_text(encoding="utf-8"))
    blk = ev.setdefault("rounds", {}).setdefault(str(rnd), {})
    ids = [e.get("event_id") for e in blk.get("image_open_events", [])]
    if event_id not in ids:
        raise SystemExit("round-%02d 里没有事件 %s" % (rnd, event_id))
    blk.setdefault("notes", []).append({
        "ts": now(),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "about_event": event_id,
        "note": text,
    })
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n",
                 encoding="utf-8")
    return len(blk["notes"])


def cmd_summary(rnd: int) -> None:
    v = TMP / "viewing-evidence.json"
    it = TMP / "iterations.jsonl"
    n_view = 0
    if v.exists() and v.stat().st_size:
        doc = json.loads(v.read_text(encoding="utf-8"))
        blk = doc.get("rounds", {}).get(str(rnd), {})
        n_view = len(blk.get("image_open_events", []))
        n_note = len(blk.get("notes", []))
    else:
        n_note = 0
    n_iter = len(read_jsonl(it))
    print(json.dumps({"round": rnd, "viewing_events": n_view,
                      "viewing_notes": n_note,
                      "iterations_total": n_iter,
                      "iterations_for_round": sum(
                          1 for r in read_jsonl(it) if r.get("round") == rnd)},
                     ensure_ascii=False))


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    rnd = int(sys.argv[2])
    if cmd == "views":
        print("round-%02d 看图事件 %d 条" % (rnd, cmd_views(rnd)))
    elif cmd == "iter":
        print("迭代记录累计 %d 条" % cmd_iter(
            rnd, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]))
    elif cmd == "note":
        print("round-%02d 批注 %d 条" % (rnd, cmd_note(rnd, sys.argv[3], sys.argv[4])))
    elif cmd == "summary":
        cmd_summary(rnd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
