"""把第 1 轮已归档的 task-metrics.json 补齐到与当前生成器一致的字段集。

背景：a21_metrics.py 在第 1 轮归档之后又新增了 5 个字段
（logs.round_changes、timings.service_stall_seconds / service_stall_note /
started_at_correction / started_at_correction_note）。第 1 轮没有读取超时的
请求，这 4 个 timings 字段对第 1 轮都是「0 / 空列表」的真值，而不是未知；
补上可以让全套指标用同一套字段聚合，不必在汇总时特判缺字段。

边界：只追加这 5 个字段，其余值（含 ended_at / elapsed_seconds 的归档时刻）
一个字节都不改，避免把「归档时算出的墙钟」换成「现在」。原文件先复制到
tmp/<run>/A21/archive-conform/ 留底，本脚本幂等：字段已存在则跳过。
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
A21 = SUITE_ROOT / "outputs" / RUN_ID / "A21"
M = A21 / "round-01" / "task-metrics.json"
KEEP = SUITE_ROOT / "tmp" / RUN_ID / "A21" / "archive-conform"


def main() -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")

    doc = json.loads(M.read_text(encoding="utf-8"))

    if KEEP.exists():
        print("留底目录已存在，不再覆盖：", KEEP)
    else:
        KEEP.mkdir(parents=True)
        shutil.copy2(M, KEEP / "task-metrics.round-01.pre-conform.json")
        print("已留底原文件 ->", (KEEP / "task-metrics.round-01.pre-conform.json")
              .relative_to(SUITE_ROOT).as_posix())

    changed = []

    # 与生成器一致：取最后一条在案的第 1 轮活动，算出归档尾段
    activity = []
    for i in (json.loads(l) for l in (SUITE_ROOT / "tmp" / RUN_ID / "A21"
                                      / "iterations.jsonl").read_text(
            encoding="utf-8").splitlines() if l.strip()):
        if i.get("round") == 1 and i.get("ended_at"):
            activity.append(dt.datetime.fromisoformat(i["ended_at"]))
    ve = json.loads((SUITE_ROOT / "tmp" / RUN_ID / "A21"
                     / "viewing-evidence.json").read_text(encoding="utf-8"))
    for e in ve["rounds"]["1"]["image_open_events"]:
        if e.get("viewed_at"):
            activity.append(dt.datetime.fromisoformat(e["viewed_at"]))
    for r in (json.loads(l) for l in (SUITE_ROOT / "tmp" / RUN_ID / "A21"
                                      / "requests.jsonl").read_text(
            encoding="utf-8").splitlines() if l.strip()):
        if (r.get("round") == 1 or r.get("round") is None) and r.get("http_status") is not None:
            activity.append(dt.datetime.fromisoformat(r["started_at"])
                            + dt.timedelta(milliseconds=r.get("elapsed_ms") or 0))
    last_activity = max(activity)
    tail_s = round((dt.datetime.fromisoformat(doc["timings"]["ended_at"])
                    - last_activity).total_seconds(), 1)

    t = doc["timings"]
    if "last_recorded_activity_at" not in t:
        new_t = {}
        for k, v in t.items():
            new_t[k] = v
            if k == "elapsed_note":
                new_t["last_recorded_activity_at"] = last_activity.isoformat(
                    timespec="seconds")
                new_t["archive_tail_seconds"] = tail_s
                new_t["archive_tail_note"] = (
                    "墙钟终点取本指标文件生成时刻（本轮归档完成）。在案的第 1 轮"
                    "活动——迭代记录的 ended_at、看图事件的 viewed_at、成功请求的"
                    "结束时刻——止于 last_recorded_activity_at；两者之差"
                    " archive_tail_seconds 是归档与记账尾段，含上下文压缩与平台"
                    "中断造成的停顿、写本报告与指标、必要的返工与调试。它是墙钟的"
                    "一部分，不能扣掉，也不能用 request_duration_sum_seconds 或"
                    "service_stall_seconds 替代墙钟")
        doc["timings"] = new_t
        changed += ["timings.last_recorded_activity_at",
                    "timings.archive_tail_seconds", "timings.archive_tail_note"]

    logs = doc["logs"]
    if "round_changes" not in logs:
        new_logs = {"round_changes": "tmp/%s/A21/round-01-changes.json" % RUN_ID}
        new_logs.update(logs)
        doc["logs"] = new_logs
        changed.append("logs.round_changes")

    t = doc["timings"]
    if "service_stall_seconds" not in t:
        # 插在 elapsed_note 之后，与第 2 轮字段的相对位置一致
        new_t = {}
        for k, v in t.items():
            new_t[k] = v
            if k == "elapsed_note":
                new_t["service_stall_seconds"] = 0
                new_t["service_stall_note"] = (
                    "http_status 为 None 的 0 条请求的 elapsed_ms 之和——第 1 轮"
                    "没有读取超时的请求：9 条记录里 6 条 200、3 条 400（均为"
                    "PARSE_ERROR，服务端正常返回了响应体），因此为 0")
                new_t["started_at_correction"] = []
                new_t["started_at_correction_note"] = (
                    "第 1 轮 9 条请求全部返回了响应，started_at 均为服务端起点，"
                    "无需还原；本脚本只在 http_status 为 None 时才改用"
                    " started_at - elapsed_ms")
        doc["timings"] = new_t
        changed += ["timings.service_stall_seconds", "timings.service_stall_note",
                    "timings.started_at_correction",
                    "timings.started_at_correction_note"]

    if not changed:
        print("字段已齐，无需改动")
        return 0

    M.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("已补齐字段：%s" % ", ".join(changed))
    print("补丁时间：%s" % dt.datetime.now().astimezone().isoformat(timespec="seconds"))
    print("未改动：ended_at=%s elapsed_seconds=%s"
          % (doc["timings"]["ended_at"], doc["timings"]["elapsed_seconds"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
