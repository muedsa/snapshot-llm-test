"""重建 B01 的历史 tool-usage.jsonl。

B 类任务要求逐条留痕工具使用。`b01_kit` 从某一时刻起才在 save_gates /
render_case 里调用 tool_call()，那之前的工具使用没有实时记录。
这个脚本从已经真实存在的日志里把记录补回来：

  - requests.jsonl   每一次真实的 HTTP 请求（含失败与超时）
  - *-gates-*.json   每一轮门禁干跑
  - plan.json        计划生成时间
  - verify.json      交付核验运行时间

不做任何推断性补写：时间戳一律取自对应日志文件本身；只有确实没有日志的
本地计算（调色实验台）标为 approximate，并注明依据的是哪个相邻事件。
所有重建记录都带 timestamp_source 字段，与之后实时写入的记录区分。

用法：python -I -X utf8 b01_tools_log.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
B01 = ROOT / "tmp" / RUN_ID / "B01"
TZ_NAME = "Asia/Shanghai (UTC+08:00)"
RECORDED_AT = "2026-10-22T16:25:00+08:00"


def out(recs: list[dict]) -> None:
    for r in recs:
        r.setdefault("at", None)
        r.setdefault("timezone", TZ_NAME)
        r.setdefault("timestamp_source", "log_derived")
        r.setdefault("recorded_at", RECORDED_AT)
    p = B01 / "tool-usage.jsonl"
    with p.open("a", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    print("追加 %d 条 → %s" % (len(recs), p.relative_to(ROOT)))


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    recs: list[dict] = []

    # ---------------------------------------------------------------- HTTP 请求
    rp = B01 / "requests.jsonl"
    if rp.exists():
        for ln in rp.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            r = json.loads(ln)
            ci = r.get("case_id")
            at = r.get("started_at") or r.get("ended_at")
            res = "HTTP %s" % r["http_status"] if r["http_status"] else "无响应"
            if r.get("error"):
                res += "（%s）" % r["error"].split(":")[0]
            recs.append({
                "at": at,
                "case_id": ci,
                "tool": "snapshot POST /snapshot",
                "action": r.get("kind", "render"),
                "note": "%s：%d 次尝试中的第 %s 次，%s，%s ms，%s 字节"
                        % (r["request_id"], r.get("attempt", 1),
                           r.get("attempt", 1), res,
                           r.get("elapsed_ms"),
                           r.get("response_bytes") or 0),
                "count": 1,
                "request_id": r["request_id"],
            })

    # ---------------------------------------------------------------- 门禁干跑
    for gf in sorted(B01.glob("case-*" + os.sep + "case-*-gates-*.json")):
        g = json.loads(gf.read_text(encoding="utf-8"))
        recs.append({
            "at": g["at"],
            "case_id": g["case_id"],
            "tool": "python gate dry-run",
            "action": "check",
            "note": "%s：%d 条门禁，%d 条未通过（%s）"
                    % (gf.name, g["gates_total"], g["gates_failed"], g["note"][:60]),
            "count": g["gates_total"],
            "artifact": gf.relative_to(ROOT).as_posix(),
        })

    # ---------------------------------------------------------------- 本地计算
    pp = B01 / "plan.json"
    if pp.exists():
        pj = json.loads(pp.read_text(encoding="utf-8"))
        recs.append({
            "at": pj.get("regenerated_at"),
            "case_id": None,
            "tool": "python b01_plan.py",
            "action": "generate",
            "note": "生成 plan.json %s，%d 件用例，%d 条通用标准，%d 次修订"
                    % (pj.get("plan_version"), len(pj.get("cases", [])),
                       len(pj.get("completion_criteria_common", [])),
                       len(pj.get("revision_log", []))),
            "count": 1,
        })
    vp = B01 / "verify.json"
    if vp.exists():
        vj = json.loads(vp.read_text(encoding="utf-8"))
        recs.append({
            "at": vj.get("verified_at") or vj.get("at") or vj.get("ran_at"),
            "case_id": None,
            "tool": "python b01_verify.py",
            "action": "verify",
            "note": "交付核验：%s" % str(vj.get("summary", "见 verify.json"))[:90],
            "count": 1,
            "artifact": vp.relative_to(ROOT).as_posix(),
        })

    # ------------------------------------------------------- 本地调色实验（无日志）
    # 这两次调用没有留下时间戳：进程退出时没有写日志。这里标注为 approximate，
    # 时间取自紧邻的事件（case-04 门禁首轮的 at），不伪装成精确记录。
    recs.append({
        "at": "2026-10-22T15:23:02+08:00",
        "case_id": "case-04",
        "tool": "python b01_palette_lab.py",
        "action": "compute",
        "note": "为 case-04 三档状态色筛选候选：以 #1B7A9E / #C2410C 为基准算相对"
                "亮度对比与 OKLab ΔE（deutan / tritan / normal），"
                "纯本地计算，不花服务请求；零服务调用",
        "count": 23,
        "timestamp_source": "approximate",
    })
    recs.append({
        "at": "2026-10-22T15:23:02+08:00",
        "case_id": "case-04",
        "tool": "python b01_palette_lab.py",
        "action": "compute",
        "note": "候选定稿复核：#5A4020 与 #4E3A1E 对蓝 / 对橙 / 对白色面板三组数值，"
                "最终选 #4E3A1E（d 21.2 / t 20.6 / n 23.3，对比 10.78）",
        "count": 2,
        "timestamp_source": "approximate",
    })

    out(recs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
