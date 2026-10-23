"""A02 迭代留痕补记：v4 那次渲染成功（两张 PNG 200，audit 已带 size/bold），
但脚本随后在读取 SNAPSHOT_ITER_REASON_FILE 时因文件不存在而抛错，
迭代记录未落盘。本脚本把那次真实发生的事补记进 iterations.jsonl。

只记录真实发生的事：v3 与 v4 的 DSL 逐字相同（tmp/dsl/*.v3.snapshot == *.v4.snapshot），
两张 PNG 字节数与 v3 完全一致（350942 / 217671），无视觉改动。
幂等：同 version+kind 已存在则跳过。

启动基准：总任务根（cwd）。SNAPSHOT_RUN_ID 需已设置。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(Path.cwd()))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import json  # noqa: E402
import suite as S  # noqa: E402

REASON = (
    "content_map 每条记录补 size/bold（WIDE_STYLE / MOBILE_STYLE），"
    "使 schedule-audit.json 自述排版、像素自检可独立复算期望宽度。"
    "无视觉改动：tmp/dsl/agenda-wide.v4.snapshot 与 v3 逐字相同、"
    "agenda-mobile.v4.snapshot 亦相同；两张 PNG 字节数与 v3 一致"
    "（350942 / 217671）。本次渲染 200，请求 ID 见 requests.jsonl。"
    "上一次运行时本脚本尚未写出 reason 文件，构建在读取 reason 时抛"
    " FileNotFoundError，PNG 与 audit 已落盘而迭代记录缺失，故补记。")


def main() -> None:
    path = (S.suite_root() / "tmp" / os.environ["SNAPSHOT_RUN_ID"]
            / "A02" / "iterations.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    have = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                have.add(f"{r.get('kind')}|{r.get('version')}")
    key = "audit-fix|v4"
    if key in have:
        print(f"skip (already present): {key}")
        return
    S.log_iteration("A02", {
        "kind": "audit-fix", "version": "v4", "parent": "v3",
        "label": "A02 全日日程（agenda-wide + agenda-mobile）",
        "reason": REASON,
        "images": [
            "outputs/r20261014T1536+0800-5f11da/A02/agenda-wide.png",
            "outputs/r20261014T1536+0800-5f11da/A02/agenda-mobile.png"],
        "note": "backfill: 渲染成功但脚本在读取 reason 文件时抛错，记录缺失"})
    print(f"backfilled {key} -> {path}")


if __name__ == "__main__":
    main()
