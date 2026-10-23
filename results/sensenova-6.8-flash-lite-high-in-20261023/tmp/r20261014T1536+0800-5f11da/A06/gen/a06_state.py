"""A06 收尾：更新 suite-state.json、追加 events.jsonl、写 checkpoint 000033。

路径全部相对总任务根（path_base = suite_root）。
用法：python -I gen/a06_state.py
"""

from __future__ import annotations

import datetime
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a06_io as IO  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RID = "r20261014T1536+0800-5f11da"
SUITE_OUT = f"outputs/{RID}/_suite"
SUITE_TMP = f"tmp/{RID}/_suite"
A06_STARTED = "2026-10-15T06:23:45+08:00"   # = A05.ended_at
NEXT = "A07"


def main() -> None:
    root = IO.ROOT
    state_p = root / SUITE_OUT / "suite-state.json"
    events_p = root / SUITE_TMP / "events.jsonl"
    ck_dir = root / SUITE_TMP / "checkpoints"
    state = json.loads(state_p.read_text(encoding="utf-8"))
    metrics = json.loads(
        (root / f"outputs/{RID}/A06/task-metrics.json").read_text(encoding="utf-8"))
    ended = metrics["ended_at"]

    def find(tid: str) -> dict:
        return next(t for t in state["tasks"] if t["id"] == tid)

    a06 = find("A06")
    assert a06["status"] == "pending", a06["status"]
    a06.update({
        "status": "completed",
        "started_at": A06_STARTED,
        "ended_at": ended,
        "output_dir": f"outputs/{RID}/A06",
        "temp_dir": f"tmp/{RID}/A06",
        "completed_rounds": [],
        "completed_cases": [],
        "artifacts": [
            f"outputs/{RID}/A06/dependency-map.png",
            f"outputs/{RID}/A06/dependency-map.snapshot",
            f"outputs/{RID}/A06/graph-audit.json",
            f"outputs/{RID}/A06/snapshot-usage.md",
            f"outputs/{RID}/A06/task-metrics.json",
        ],
        "visual_review_evidence": [
            "最终 PNG 实际打开复核（1600x1000）：标题与两行副标题、11 行层号沟槽与节点数、"
            "14 个节点（编号 + 标签、阶段色 2px 边框）、16 条实线先决边与 16 个实心三角箭头、"
            "2 条橙色虚线反馈回环（x=195/265 分道）及其回环内侧短标签、左侧走廊 x=145 上的"
            "N04→N13 长期先决、右侧说明面板（节点样例、两种线型、交叉规则与实测结果、"
            "5 个阶段色块、两张反馈解释卡）、底部最长路径两解与规模行",
            "157 项像素断言全过 0 FAIL（tmp/r20261014T1536+0800-5f11da/A06/gen/"
            "final-inspect.txt），核验对象为最终产物而非预览；退出码 0；核验器期望几何从"
            "model.json 独立重推导，不复用构造器函数",
            "15 次看图（整幅 8：v1..v6 六个预览 + v5 二次复看 + 最终 PNG；裁图 7），"
            "另 2 次逐像素诊断；记录在 iterations.jsonl",
            "7 次请求全部 200 / 0 失败，attempts=1，无 429/503，无 Retry-After，"
            "RateLimit-Remaining 全程 118–119；请求耗时之和 29.313 s，"
            "服务端 render;dur 合计 9896.3 ms，墙钟 4629 s",
            "12 组要求 157 项断言：14 节点 / 16 先决边（覆盖 1.000、单段最长缺口 0px、"
            "层号单调递增）/ 2 反馈边（虚线 ≥3px 空档、反向、与实线色 0 像素重叠、"
            "excluded_from_dag_layering）/ 153 对边组合交叉 0 处 / 18 条边不侵入任何节点盒 / "
            "节点字号 22 与注释 18 / 面板内含 6px 留白 / graph-audit.json 字段齐备",
            "7 项问题（4 渲染缺陷 + 3 核验器自身缺陷 + 0 服务报错）全部修复后重渲染复查；"
            "v3「18 条边全部消失」与 v5「反馈卡越出面板 8px」两处均由整幅看图或逐像素实测"
            "发现，不是靠渲染成功判定",
            "交付前以 render 用途重新提交同一份 DSL 写入输出目录，对最终 PNG 重跑全部断言，"
            "并与 v6-preview 做 cmp 逐字节一致",
        ],
        "unresolved_issues": [
            "A06-U1 low 核验器 5 次运行中前 3 次（脚本语法错 / 路径解析错 / 色彩门槛与端帽错）"
            "未单独留档 .txt；根因、判定依据与修正记在 iterations.jsonl verify-1，"
            "核验器仍在 gen/ 下可重跑",
            "A06-U2 info 排队等待不可测记 null（服务无该字段）；看图只有真实下界"
            "viewed_not_before；路径覆盖判定以该色像素存在性为判据，抗锯齿边缘不计入长度",
            "A06-U3 info Transform 的 2×2 部分静默失效且无 Path/Line/Polyline 标签，"
            "斜线只能由轴对齐矩形拼合，箭头由 5 根缩窄矩形拼出；DSL 59619 B / 379 Positioned",
        ],
        "resume_notes": None,
    })

    a07 = find(NEXT)
    assert a07["status"] == "pending", a07["status"]
    a07.update({
        "status": "in_progress",
        "started_at": ended,
        "ended_at": None,
        "output_dir": f"outputs/{RID}/{NEXT}",
        "temp_dir": f"tmp/{RID}/{NEXT}",
    })

    state["current_task"] = NEXT
    state["current_round"] = None
    state["current_case"] = None
    state["updated_at"] = ended
    state["last_checkpoint"] = (
        f"{SUITE_TMP}/checkpoints/state-000033.json")

    state_p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")

    def ev(**kw) -> None:
        with events_p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(kw, ensure_ascii=False) + "\n")

    ev(ts=A06_STARTED, event="task_started", task_id="A06",
       status="in_progress", output_dir=f"outputs/{RID}/A06",
       temp_dir=f"tmp/{RID}/A06")
    ev(ts=ended, event="task_completed", task_id="A06", status="completed",
       ended_at=ended,
       checkpoint=f"{SUITE_TMP}/checkpoints/state-000033.json",
       artifacts=a06["artifacts"],
       snapshot_requests=metrics["counts"]["snapshot_requests"],
       successful=metrics["counts"]["successful_snapshot_requests"],
       failed=metrics["counts"]["failed_snapshot_requests"],
       image_views=metrics["counts"]["image_views"],
       visual_iterations=metrics["counts"]["completed_visual_iterations"],
       issues_found=metrics["counts"]["issues_found"],
       requirement_checks="157/157",
       elapsed_seconds=metrics["elapsed_seconds"])
    ev(ts=ended, event="task_started", task_id=NEXT,
       status="in_progress", output_dir=f"outputs/{RID}/{NEXT}",
       temp_dir=f"tmp/{RID}/{NEXT}")

    ck_dir.mkdir(parents=True, exist_ok=True)
    ck = ck_dir / "state-000033.json"
    assert not ck.exists(), f"已存在，不可覆盖：{ck.name}"
    shutil.copyfile(state_p, ck)

    print("suite-state.json 已更新：A06 completed → current_task", NEXT)
    print("events.jsonl 追加 3 条")
    print("checkpoint →", ck.relative_to(root))


if __name__ == "__main__":
    main()
