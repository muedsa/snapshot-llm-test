#!/usr/bin/env python
"""全套收尾：写 suite-state.json 的最终状态。

做四件事：
  1. suite_artifacts 记录五件总交付的实际路径
  2. status 置为 completed、记 ended_at
  3. 写 suite_reviews/notes：子代理速率限制这一真实事件（影响过过程）
  4. 复核：30 题是否都 completed、每张交付图是否都有同名 .snapshot

注意：suite_state.py artifacts 子命令在 PowerShell 下会因引号被吃掉而解析失败，
所以这里直接改文件，不走命令行。
启动基准：总任务根 (suite_root)。用法：python finalize_suite_state.py
"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
SUITE = ROOT / "outputs/run-20261011-01/_suite"
RUN = "run-20261011-01"
ORDER = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]

p = SUITE / "suite-state.json"
st = json.loads(p.read_text(encoding="utf-8"))

st["suite_artifacts"] = [
    f"outputs/{RUN}/_suite/index.md",
    f"outputs/{RUN}/_suite/gallery.md",
    f"outputs/{RUN}/_suite/snapshot-usage.md",
    f"outputs/{RUN}/_suite/task-metrics.json",
    f"outputs/{RUN}/_suite/suite-state.json",
]

tasks = st.get("tasks", [])
not_done = [t.get("id") for t in tasks if t.get("status") != "completed"]

# 图与 DSL 配对复核
out = ROOT / "outputs" / RUN
pngs = sorted(out.rglob("*.png"))
unpaired = [str(q.relative_to(ROOT).as_posix())
            for q in pngs if not q.with_suffix(".snapshot").exists()]

if not_done or unpaired:
    st["status"] = "partial"
    st["ended_at"] = None
    st["unresolved_issues"] = [
        f"未完成题目：{not_done}" if not_done else "",
        f"无同名 .snapshot 的图：{unpaired}" if unpaired else "",
    ]
    st["unresolved_issues"] = [x for x in st["unresolved_issues"] if x]
else:
    st["status"] = "completed"
    st["ended_at"] = datetime.datetime.now().astimezone().isoformat(
        timespec="seconds")
    st["suite_artifacts"] = st["suite_artifacts"]
    st["final_counts"] = {
        "tasks": len(tasks),
        "images": len(pngs),
        "images_with_dsl": len(pngs) - len(unpaired),
    }
    st["suite_reviews"] = [{
        "topic": "子代理速率限制对过程的影响",
        "observation":
            "B05 与 B06 两名子代理在完成大部分构建与渲染后撞上 Rate limit，"
            "没有交出文档。两者留下的产物是完整可用的："
            "B06 十张 final.png 与 .snapshot 已渲染完毕且版本到 v4；"
            "B05 十张 DSL 已构建但只渲染到第 4 张。",
        "resolution":
            "接手方式是先读两者的 plan-v1.md 与构建脚本，确认计划与数据口径，"
            "再续跑未完成的渲染与逐张看图，最后补齐 product-brief.md / journey.json / "
            "problem-evidence.json / design-review.md 等文档。"
            "结论：**过程留痕让中断可恢复**——若子代理只交最终图而不留 plan 与构建脚本，"
            "接手方无法判断数据口径是否自洽。",
        "impact_on_deliverables": "无。B05、B06 最终均为 completed，未降级。",
    }, {
        "topic": "交付树里的一处冗余文件",
        "observation":
            "B01 根目录曾有一份 final.png，与 case-01/final.png 字节完全相同，"
            "是交付脚本中途把渲染落到题目根目录留下的重复件，且无同名 .snapshot。",
        "resolution":
            "核对 SHA-256 确认字节相同后，移到 tmp/run-20261011-01/B01/stray/ "
            "保留（不删除，属过程证据），使交付树只含真实交付物。",
        "impact_on_deliverables": "交付图由 126 计为 125，且 125 张全部有同名 .snapshot。",
    }]
    st["unresolved_issues"] = [
        "B04 的 GISTEMP 方法学页与 ZonAnnual 分带数据抓取失败，"
        "因此全套未画不确定度带，也未做分纬度带对比；相关结论未出现在任何图上。",
        "B04 未做归因分析；分段升温斜率不足以支撑归因，图上已写明。",
        "B06 十件全部为自拟示例，未抓取真实品牌版式或官方规范；"
        "case-09 的 NRV% 一列留空并写明原因。",
    ]

p.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
print("status =", st["status"])
print("tasks  =", len(tasks), "not completed:", not_done)
print("images =", len(pngs), "unpaired:", unpaired)
print("ended_at =", st.get("ended_at"))
for a in st["suite_artifacts"]:
    print("  ", a, "->", "OK" if (ROOT / a).exists() else "MISSING")