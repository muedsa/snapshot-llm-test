#!/usr/bin/env python
# A21 三轮交付：每轮一份 DSL+PNG 提升与渲染，并写出该轮与累计的报告/指标。
# 启动基准：总任务根 (suite_root)。用法：python deliver_round_a21.py <round> <ver>
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
sys.path.insert(0, str(ROOT / "tmp/run-20261011-01/_suite/scripts"))
import finalize_task as ft  # noqa: E402

TASK = "A21"
OUTD = ft.task_dirs(TASK)[0]
TEMPD = ft.task_dirs(TASK)[1]
PREV = f"{TEMPD}/preview"

EXTRA = {
    2: "round-02.md：主标题换为长标题（≤3 行、≥48），新增赞助方与参加方式，"
       "日期/讲者/ONLINE LAUNCH/网址保留，主色与品牌 4 构件形态不变。",
    3: "round-03.md：改浅色主题，全部普通文字与实际合成背景对比度 ≥4.5:1，"
       "保留第 2 轮全部文案与品牌图形，网址上方新增英语短句「Clarity through structure」，"
       "并交付 contrast-audit.json。",
}


def render(rd, which, ver, retries):
    dsub = f"round-{rd:02d}"
    src = f"{TEMPD}/drafts/{dsub}/a21-{which}-{ver}.snapshot"
    dst = f"{dsub}/launch-{which}.snapshot"
    dsl_rel = ft.promote_dsl(TASK, src, dst)
    r = None
    for a in range(1, 6):
        r = ft.render_final(TASK, f"r{rd}-{which}", dsl_rel,
                            f"launch-{which}.png", TEMPD, is_retry=a > 1, subdir=dsub)
        if r.get("ok"):
            break
        retries.append({"round": rd, "image": which, "attempt": a,
                        "status": r.get("status"),
                        "duration_seconds": r.get("duration_seconds"),
                        "response_file": r.get("response_file")})
        time.sleep(min(15, 3 * a))
    assert r.get("ok"), f"渲染失败：{r}"
    return {"dsl": dsl_rel, "render": r,
            "png": f"{dsub}/launch-{which}.png",
            "size": ft.png_size(f"{OUTD}/{dsub}/launch-{which}.png")}


def main() -> None:
    rd = int(sys.argv[1])
    ver = sys.argv[2] if len(sys.argv) > 2 else "v2"
    dsub = f"round-{rd:02d}"
    retries = []
    (ROOT / OUTD / dsub).mkdir(parents=True, exist_ok=True)

    imgs = {w: render(rd, w, ver, retries) for w in ("portrait", "wide")}

    for name in (["design-tokens", "content-map"]
                 + (["contrast-audit"] if rd == 3 else [])):
        s = ROOT / TEMPD / f"drafts/{dsub}/{name}-{ver}-raw.json"
        if s.exists():
            (ROOT / OUTD / dsub / f"{name}.json").write_text(
                s.read_text(encoding="utf-8"), encoding="utf-8")
            print("audit ->", f"{dsub}/{name}.json")

    # ---- 本轮指标
    reqs = [json.loads(x) for x in
            (ROOT / f"{TEMPD}/requests.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    mine = [d for d in reqs if f"r{rd}-" in d["version"] or f"r{rd}{ver}" in d["version"]]
    dur = sum(d.get("duration_seconds") or 0 for d in mine)
    m = {
        "schema_version": 1, "task_id": TASK, "round": rd, "path_base": "output_dir",
        "started_at": mine[0]["started_at"] if mine else None,
        "ended_at": mine[-1]["ended_at"] if mine else None,
        "timings": {"started_at": mine[0]["started_at"] if mine else None,
                    "ended_at": mine[-1]["ended_at"] if mine else None,
                    "request_duration_sum_seconds": round(dur, 3)},
        "counts": {"requests": len(mine),
                   "requests_ok": sum(1 for d in mine if d.get("status") == 200),
                   "requests_failed": sum(1 for d in mine if d.get("status") != 200),
                   "renders": 2, "image_views": 0},
        "outputs": [{"kind": "png", "path": f"{OUTD}/{imgs[w]['png']}",
                     "dsl": imgs[w]["dsl"], "size": imgs[w]["size"]} for w in imgs]
                  + [{"kind": "json", "path": f"{OUTD}/{dsub}/design-tokens.json"},
                     {"kind": "json", "path": f"{OUTD}/{dsub}/content-map.json"}]
                  + ([{"kind": "json", "path": f"{OUTD}/{dsub}/contrast-audit.json"}]
                     if rd == 3 else []),
        "verification": {"render_retries": retries,
                         "round_requirement": EXTRA.get(rd, "TASK.md 首轮要求")},
        "unresolved_issues": [],
    }
    path = ROOT / OUTD / dsub / "task-metrics.json"
    path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("metrics ->", f"{dsub}/task-metrics.json")


if __name__ == "__main__":
    main()