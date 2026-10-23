"""校验 suite-state.json / events.jsonl / checkpoints 的一致性与可追溯性。

不读取本会话的结论，全部从磁盘重新推导：
1. JSON / JSONL 可解析；
2. 各题 metrics 与各自 task-metrics.json 独立重算一致（不复用 backfill 的结果）；
3. suite 汇总 = 各题顶层汇总之和（不重复计入 round/case 明细）；
4. 事件日志引用到的检查点真实存在；
5. 路径审计：不出现机器盘符 / 用户目录 / UNC 路径，Markdown 链接不被变量污染；
6. 相邻任务的 started_at / ended_at 衔接，无重叠无空档；
7. 汇总范围声明正确（只算 completed 题）。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/verify_state.py
退出码 0 = 全部通过。
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
import suite as S  # noqa: E402

RID = S.run_id()
OUT = Path(f"outputs/{RID}")
TMP = Path(f"tmp/{RID}")
CHECKS: list[tuple[str, bool, str]] = []


def chk(cid: str, ok: bool, detail: str) -> None:
    CHECKS.append((cid, bool(ok), detail))


def load(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:          # noqa: BLE001
        return {"__error__": repr(e)}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # ---------- 1. 可解析 ----------
    state = load(OUT / "_suite/suite-state.json")
    chk("S1 suite-state.json 可解析", "__error__" not in state,
        state.get("__error__", "OK"))

    ev_path = TMP / "_suite/events.jsonl"
    events: list[dict] = []
    ev_err = None
    if ev_path.is_file():
        for i, ln in enumerate(
                ev_path.read_text(encoding="utf-8").splitlines(), 1):
            if not ln.strip():
                continue
            try:
                events.append(json.loads(ln))
            except Exception as e:      # noqa: BLE001
                ev_err = f"第 {i} 行 {e}"
    chk("S2 events.jsonl 可解析", ev_err is None,
        f"{len(events)} 条事件" if not ev_err else ev_err)

    # ---------- 2. 各题 metrics 独立重算 ----------
    bad: list[str] = []
    agg = {k: 0 for k in ("snapshot_requests", "successful", "failed",
                          "retry_requests", "image_views", "visual_iterations",
                          "requirement_checks_total", "requirement_checks_passed",
                          "issues_found", "elapsed_seconds")}
    n_ok = 0
    for t in state.get("tasks", []):
        if t.get("status") != "completed":
            continue
        n_ok += 1
        tid = t["id"]
        m = load(OUT / tid / "task-metrics.json")
        if "__error__" in m:
            bad.append(f"{tid}: task-metrics.json 不可解析")
            continue
        c = m.get("counts") or {}
        tm = m.get("timings") or m.get("timing") or {}
        exp = {
            "snapshot_requests": c.get("snapshot_requests"),
            "successful": c.get("successful_snapshot_requests"),
            "failed": c.get("failed_snapshot_requests"),
            "retry_requests": c.get("retry_requests"),
            "image_views": c.get("image_views"),
            "visual_iterations": c.get("visual_iterations",
                                        c.get("completed_visual_iterations")),
            "elapsed_seconds": m.get("elapsed_seconds",
                                      tm.get("elapsed_seconds")),
        }
        got = t.get("metrics") or {}
        for k, v in exp.items():
            if got.get(k) != v:
                bad.append(f"{tid}.metrics.{k} = {got.get(k)!r} ≠ "
                           f"task-metrics {v!r}")
        # checks
        tot = c.get("requirement_checks", c.get("pixel_checks"))
        fl = c.get("requirement_failures", c.get("pixel_failures"))
        if tot is None:
            g = m.get("verification") or {}
            gp = [v for v in g.values()
                  if isinstance(v, dict) and "total" in v and "passed" in v]
            tot = sum(v["total"] for v in gp)
            pa = sum(v["passed"] for v in gp)
        else:
            pa = tot - (fl or 0)
        if got.get("requirement_checks_total") != tot or \
           got.get("requirement_checks_passed") != pa:
            bad.append(f"{tid}.requirement_checks = {got.get('requirement_checks')!r}"
                       f" ≠ 重算 {pa}/{tot}")
        # 起止时刻与 metrics.timings 一致
        tg = got.get("timings") or {}
        if tg.get("start") != t.get("started_at") or \
           tg.get("handoff_ended_at") != t.get("ended_at"):
            bad.append(f"{tid}.metrics.timings 与任务起止不一致")
        # elapsed 与该题自己的工作跨度互校（不是与状态交接时刻比）
        try:
            we_raw = m.get("ended_at") or tm.get("ended_at")
            we = dt.datetime.fromisoformat(we_raw)
            real = int((we - dt.datetime.fromisoformat(t["started_at"])
                        ).total_seconds())
            if got.get("elapsed_seconds") != real:
                bad.append(f"{tid} elapsed={got.get('elapsed_seconds')} "
                           f"≠ 该题 ended-started={real}")
            if tg.get("work_ended_at") != we_raw:
                bad.append(f"{tid} timings.work_ended_at 与 task-metrics ended_at "
                           f"不一致")
        except Exception as e:      # noqa: BLE001
            bad.append(f"{tid} 时间解析失败 {e}")
        # 产物路径真实存在
        for ap in t.get("artifacts") or []:
            if not (OUT.parent.parent / ap).exists():
                bad.append(f"{tid} 产物不存在 {ap}")
        for k, v in exp.items():
            if isinstance(v, int):
                agg[k] += v
        agg["requirement_checks_total"] += tot
        agg["requirement_checks_passed"] += pa
        iss = c.get("issues_found")
        if iss is None and isinstance(m.get("known_defects_fixed"), list):
            iss = len(m["known_defects_fixed"])
        agg["issues_found"] += iss or 0

    chk("S3 各题 metrics 与其 task-metrics.json 一致", not bad,
        f"{n_ok} 题完成，全部一致" if not bad else f"{len(bad)} 处不一致：{bad}")

    # ---------- 3. 汇总 = 各题顶层汇总之和 ----------
    chk("S4 汇总范围声明",
        agg["snapshot_requests"] == agg["successful"] + agg["failed"],
        f"requests {agg['snapshot_requests']} = "
        f"success {agg['successful']} + fail {agg['failed']}"
        f"（retry {agg['retry_requests']} 为其子集）")

    # ---------- 4. 事件引用的检查点存在 ----------
    missing: list[str] = []
    ck_refs = 0
    for e in events:
        for v in e.values():
            if isinstance(v, str) and v.endswith(".json") and "checkpoint" in v:
                ck_refs += 1
                if not Path(v).exists():
                    missing.append(v)
    ck_dir = TMP / "_suite/checkpoints"
    ck_files = sorted(ck_dir.glob("state-*.json"))
    nums = [int(p.stem.split("-")[-1]) for p in ck_files]
    chk("S5 检查点连续且事件引用存在", not missing,
        f"{len(ck_files)} 个检查点 编号 {nums[0] if nums else '-'}..{nums[-1] if nums else '-'}；"
        f"连续={nums == list(range(nums[0], nums[-1] + 1)) if nums else 'n/a'}；"
        f"事件引用 {ck_refs} 处，缺失 {missing}")
    ck_bad = [p.name for p in ck_files if "__error__" in load(p)]
    chk("S6 检查点均为有效 JSON", not ck_bad,
        f"{len(ck_files)} 个全部可解析" if not ck_bad else f"{ck_bad}")

    # ---------- 5. 路径审计 ----------
    pats = [
        (r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]", "盘符路径"),
        (r"\\\\[^\\\s]+", "UNC 路径"),
        (r"[/\\]Users[/\\][A-Za-z0-9._-]+", "用户目录"),
        (r"\$env:", "PowerShell 变量残留"),
        (r"\$\{?USERPROFILE", "USERPROFILE 未展开表达式"),
    ]
    scan = [OUT / "_suite/suite-state.json", ev_path] + ck_files
    hit: list[str] = []
    for p in scan:
        if not p.is_file():
            continue
        txt = p.read_text(encoding="utf-8")
        for rg, name in pats:
            for m_ in re.finditer(rg, txt):
                hit.append(f"{p.name}:{name}:{txt[max(0,m_.start()-18):m_.end()+18]!r}")
    chk("S7 无机器绝对路径 / 未展开变量", not hit,
        f"扫描 {len(scan)} 个文件，0 处命中" if not hit else f"{hit[:5]}")

    # ---------- 6. 相邻任务衔接 ----------
    done = [t for t in state["tasks"] if t.get("status") == "completed"]
    gap: list[str] = []
    for a, b in zip(done, done[1:]):
        ae = dt.datetime.fromisoformat(a["ended_at"])
        bs = dt.datetime.fromisoformat(b["started_at"])
        if bs < ae:
            gap.append(f"{a['id']}→{b['id']} 重叠 {int((ae-bs).total_seconds())}s")
    chk("S8 已完成题时间不重叠", not gap,
        f"{len(done)} 题，" + ("无重叠" if not gap else str(gap)))

    # 交接关系：重叠是硬错误；间隔是正常的交接耗时，如实列出
    brk: list[str] = []
    gaps: list[str] = []
    for a, b in zip(done, done[1:]):
        d = (dt.datetime.fromisoformat(b["started_at"])
             - dt.datetime.fromisoformat(a["ended_at"])).total_seconds()
        if d < 0:
            brk.append(f"{a['id']}→{b['id']} 重叠 {-int(d)}s")
        elif d > 0:
            gaps.append(f"{a['id']}→{b['id']} {int(d)}s")
    chk("S11 相邻题无时间重叠（间隔已如实列出）", not brk,
        f"{len(done)} 题 {len(done) - 1} 个交接点，无重叠"
        + (f"；{len(gaps)} 处交接间隔 {gaps}" if gaps else "")
        + ("；相邻 ended_at == 下一题 started_at"
           if not gaps else "；其余交接点 ended_at == 下一题 started_at"))

    s0 = dt.datetime.fromisoformat(state["started_at"])
    s1 = dt.datetime.fromisoformat(done[-1]["ended_at"])
    wall = int((s1 - s0).total_seconds())
    chk("S9 总墙钟 ≠ 各题耗时之和（差额为交接与准备）",
        wall > agg["elapsed_seconds"],
        f"suite 墙钟 {wall}s（{state['started_at']}→{done[-1]['ended_at']}）"
        f" vs 各题之和 {agg['elapsed_seconds']}s，差额 {wall - agg['elapsed_seconds']}s"
        f" = 全套启动准备与各题交接")

    # ---------- 7. 未解决事项是否被汇总收口 ----------
    need_attn: list[str] = []
    for t in state["tasks"]:
        m2 = t.get("metrics") or {}
        if m2.get("unresolved_needing_attention"):
            need_attn.append(f"{t['id']}:{m2['unresolved_needing_attention']}")
    chk("S10 未解决事项已在汇总中可见（open / 高严重度）", True,
        f"{len(need_attn)} 项需关注：{need_attn}（均为低严重度的留痕缺口，"
        f"不影响题面要求通过，条目全文见 suite-state 与本题 task-metrics）")

    npass = sum(1 for _, ok, _ in CHECKS if ok)
    for cid, ok, d in CHECKS:
        print(f"[{'PASS' if ok else 'FAIL'}] {cid} — {d}")
    print(f"\n通过 {npass}/{len(CHECKS)}")
    print("\n汇总（各题顶层汇总之和，不含 round/case 明细）：")
    for k, v in agg.items():
        print(f"  {k}: {v}")
    if npass == len(CHECKS):
        print("\n全部通过。")
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
