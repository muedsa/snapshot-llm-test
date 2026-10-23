"""A01 迭代留痕补记：把早期各轮（含失败请求）真实发生的视觉/语法修复补进
iterations.jsonl，与 requests.jsonl 逐条对齐。只记录真实发生的事，不造迭代。

启动基准：总任务根（cwd）。SNAPSHOT_RUN_ID / SNAPSHOT_TASK_ROOT 需已设置。
幂等：已存在的记录（同 kind+version+reason 首 24 字）跳过。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SNAPSHOT_TASK_ROOT", str(Path.cwd()))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))

import suite as S  # noqa: E402

HISTORY = [
    ("2026-10-14T17:18:09+08:00", "fail_http", "v1",
     "HTTP 403：Cloudflare WAF error 1010，User-Agent 为 Python-urllib/3.11 被拦。"
     "改用浏览器 UA 后同一 DSL 放行（200）。"),
    ("2026-10-14T17:30:24+08:00", "fail_parse", "v1",
     "PARSE_ERROR：Positioned 的父节点不是 Stack（Container > Positioned）→ "
     "renderBox.parentData must be StackParentData。"),
    ("2026-10-14T17:32:44+08:00", "fail_parse", "v1",
     "PARSE_ERROR：Positioned > Positioned 嵌套，同上。dsl.el() 增加 "
     "<Positioned left=0 top=0> 自动剥离。"),
    ("2026-10-14T17:37:18+08:00", "fail_parse", "v1",
     "PARSE_ERROR：ClipPath 的 viewBox 与 path 坐标空间不一致。"),
    ("2026-10-14T18:05:18+08:00", "baseline", "v1",
     "首次成功渲染（200 image/png）。基线版：4 KPI + 分组柱图 + 双小图 + 明细表 + 结论 + 双行脚注。"),
    ("2026-10-14T18:31:32+08:00", "visual_iter", "v2",
     "看图：KPI 主数值被裁掉末位字符（¥918,624 丢 4、11.15% 丢 %）。根因是 Positioned 的"
     " width 对 Text 是紧约束，而非字宽表偏差。"),
    ("2026-10-14T19:13:14+08:00", "visual_iter", "v3",
     "看图：转化率折线整体不可见。根因是 ClipPath 路径用了面板 body 坐标，被映射到 "
     "viewBox(0 0 534 56) 之外；改为盒内坐标。"),
    ("2026-10-14T19:33:47+08:00", "visual_iter", "v4",
     "看图：结论第 2 条尾部被裁（「…长靠流量，不靠效率。」丢失）。wrap_text 估算偏乐观、"
     "渲染器多折一行而盒高只留 1 行；加 safety=0.94。"),
    ("2026-10-14T19:43:58+08:00", "visual_iter", "v5",
     "复核：移除 panel/kpi/legend 单行文本的紧约束宽度，改由 Text 自定宽 + 构建期断言卡撞车。"),
    ("2026-10-14T20:00:14+08:00", "visual_iter", "v5",
     "看图：结论第 2 条行首是孤立的「：」（中文行首禁则）。随后补：KPI 强调条与内容层"
     "分居卡片两侧、wrap_text 改以原子为单位 + 行首/行末禁则 + 空格优先断行。"),
]


def main() -> None:
    path = Path(S.suite_root()) / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "A01" / "iterations.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    have = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                import json
                r = json.loads(line)
                have.add(f"{r.get('kind')}|{r.get('version')}|{str(r.get('reason', ''))[:24]}")
    n = 0
    for ts, kind, ver, reason in HISTORY:
        key = f"{kind}|{ver}|{reason[:24]}"
        if key in have:
            continue
        S.log_iteration("A01", {"ts": ts, "timezone": S.TZ_NAME, "kind": kind,
                                 "version": ver, "label": "A01 经营诊断驾驶舱",
                                 "reason": reason, "note": "backfill: 与 requests.jsonl 对齐"})
        n += 1
    print(f"backfilled {n} of {len(HISTORY)} -> {S.rel(path)}")


if __name__ == "__main__":
    main()
