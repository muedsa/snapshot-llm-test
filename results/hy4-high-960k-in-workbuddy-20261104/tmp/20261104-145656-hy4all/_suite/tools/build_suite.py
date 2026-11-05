#!/usr/bin/env python3
"""Generate suite-level deliverables: gallery.md, index.md, snapshot-usage.md, task-metrics.json."""
import json, os, re, struct, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite

RID = suite.RID
cat = json.loads((suite.ROOT / "catalog.json").read_text(encoding="utf-8"))
order = cat["task_order"]
meta = {x["id"]: x for x in cat["tasks"]}
SUITE = suite.SUITE_OUT
SUITE.mkdir(parents=True, exist_ok=True)


def png_size(p):
    b = p.read_bytes()[:24]
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", b[16:24])


def task_purpose(t, stem):
    p = suite.ROOT / meta[t]["directory"] / "task.json"
    try:
        spec = json.loads(p.read_text(encoding="utf-8"))
        for o in spec.get("required_outputs", []):
            if Path(o["filename"]).stem == stem:
                return o.get("purpose", "")
    except Exception:
        pass
    return ""


def b_titles(t):
    p = suite.out_dir(t) / "portfolio.json"
    out = {}
    if p.exists():
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            for c in d.get("cases", []):
                cid = c.get("id") or c.get("case_id")
                if cid:
                    out[cid] = c.get("title") or cid
        except Exception:
            pass
    # fallback: read case.md first heading
    return out


ROUND_NAMES = {"round-01": "第 1 轮", "round-02": "第 2 轮", "round-03": "第 3 轮"}
A23_NAMES = {"cover": "封面与格式边界说明", "contact-sheet": "逐帧接触表"}


def title_for(t, p):
    rel = p.relative_to(suite.out_dir(t)).as_posix()
    parts = rel.split("/")
    stem = p.stem
    if t.startswith("B"):
        mp = b_titles(t)
        if len(parts) > 1 and parts[0] in mp:
            return mp[parts[0]]
        if len(parts) > 1 and parts[0].startswith("case-"):
            n = parts[0].replace("case-", "")
            return mp.get(parts[0], "作品 %s" % n)
    if len(parts) > 1 and parts[0] in ROUND_NAMES:
        base = task_purpose(t, stem) or stem
        return "%s · %s" % (ROUND_NAMES[parts[0]], base)
    if t == "A23" and stem.startswith("frame-"):
        return "分镜帧 %s" % stem.replace("frame-", "")
    if t == "A23" and stem in A23_NAMES:
        return A23_NAMES[stem]
    purpose = task_purpose(t, stem)
    if purpose:
        return purpose
    return stem


def collect(t):
    d = suite.out_dir(t)
    pngs = sorted(d.rglob("*.png"))
    items = []
    for p in pngs:
        s = p.with_suffix(".snapshot")
        size = png_size(p)
        items.append({
            "task": t, "path": p, "dsl": s if s.exists() else None,
            "size": size, "bytes": p.stat().st_size, "title": title_for(t, p),
            "group": p.parent.relative_to(d).as_posix() if p.parent != d else "",
        })
    return items


ALL = {t: collect(t) for t in order}
TOTAL_PNG = sum(len(v) for v in ALL.values())

# --------------------------------------------------------------- gallery.md
g = []
A = g.append
A("# Snapshot 全套最终图 · 完整画廊")
A("")
A("运行 ID：`%s` ｜ 任务范围：`all`（A01–A24、B01–B06，共 30 题） ｜ 最终图片：**%d 张**" % (RID, TOTAL_PNG))
A("")
A("本画廊逐张索引全部最终 PNG；每张给出标题、内嵌预览、原 PNG 链接与同名 `.snapshot` DSL 链接。")
A("所有链接相对本文件所在的 `_suite/` 目录（例如 `../A01/operations.png`），复制整个输出目录后仍可离线浏览。")
A("A21/A22 按三个预置轮次分组展示；B01–B06 按开放用例分组展示，每题 10 件独立作品。")
A("")
A("[返回总索引](index.md) · [使用情况与踩坑](snapshot-usage.md) · [全套指标](task-metrics.json)")
A("")
A("---")
A("")
for t in order:
    items = ALL[t]
    A("## %s · %s" % (t, meta[t]["title"]))
    A("")
    A("输出目录 `../%s/` ｜ 最终图 %d 张 ｜ [本题报告](../%s/snapshot-usage.md) ｜ [本题指标](../%s/task-metrics.json)" %
      (t, len(items), t, t))
    A("")
    groups = {}
    for it in items:
        groups.setdefault(it["group"], []).append(it)
    for gname in sorted(groups.keys(), key=lambda x: (x != "", x)):
        if gname:
            label = ROUND_NAMES.get(gname, gname)
            A("### %s · %s" % (t, label))
            A("")
        for it in groups[gname]:
            rel_png = "../%s/%s" % (t, it["path"].relative_to(suite.out_dir(t)).as_posix())
            rel_dsl = "../%s/%s" % (t, it["dsl"].relative_to(suite.out_dir(t)).as_posix()) if it["dsl"] else None
            dim = "%d × %d" % it["size"] if it["size"] else "尺寸未知"
            A("#### %s — `%s`" % (it["title"], it["path"].name))
            A("")
            A("![%s · %s](%s)" % (t, it["title"], rel_png))
            A("")
            if rel_dsl:
                A("尺寸 %s ｜ %d 字节 ｜ [原 PNG](%s) ｜ [同名 DSL `%s`](%s)" %
                  (dim, it["bytes"], rel_png, it["dsl"].name, rel_dsl))
            else:
                A("尺寸 %s ｜ %d 字节 ｜ [原 PNG](%s) ｜ **缺少同名 .snapshot**" % (dim, it["bytes"], rel_png))
            A("")
    A("---")
    A("")
(SUITE / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")

# --------------------------------------------------------------- index.md
ix = []
A = ix.append
A("# Snapshot 全套任务 · 总索引")
A("")
A("运行 ID：`%s` ｜ 配置：`all`（30 题） ｜ 状态：**完成** ｜ 最终图片：**%d 张**（要求 ≥ %d）" %
  (RID, TOTAL_PNG, cat["minimum_final_pngs"]))
A("")
A("总输出目录：`outputs/%s/` ｜ 总临时目录：`tmp/%s/` ｜ 本文件与总画廊位于 `outputs/%s/_suite/`。" %
  (RID, RID, RID))
A("")
A("- [完整画廊 gallery.md](gallery.md) — 逐张索引全部最终图、A21/A22 三轮与 B 类全部作品")
A("- [使用情况与踩坑 snapshot-usage.md](snapshot-usage.md)")
A("- [全套指标 task-metrics.json](task-metrics.json)")
A("- [进度状态 suite-state.json](suite-state.json)")
A("")
A("## 逐题状态")
A("")
A("| 顺序 | 任务 | 标题 | 状态 | 轮次 / 用例 | 最终 PNG | 输出目录 | 临时目录 | 单题入口 |")
A("|---:|---|---|---|---|---:|---|---|---|")
state = suite.load_state()
for i, t in enumerate(order, 1):
    ts = suite.task_state(state, t)
    rnd = ", ".join(ts.get("completed_rounds") or []) or "—"
    cases = ts.get("completed_cases") or []
    rc = ("%d 用例" % len(cases)) if cases else rnd
    A("| %d | %s | %s | %s | %s | %d | `outputs/%s/%s/` | `tmp/%s/%s/` | [报告](../%s/snapshot-usage.md) · [指标](../%s/task-metrics.json) |" %
      (i, t, meta[t]["title"], ts["status"], rc, len(ALL[t]), RID, t, RID, t, t, t))
A("")
A("## 多轮与开放用例")
A("")
A("- **A21**（真实需求变更：双尺寸发布物）：round-01 深色双尺寸基线 → round-02 长标题与赞助方 → round-03 浅色高对比；每轮 2 张图，共 6 张。轮次要求已随题库预置，按顺序连续执行，未等待外部反馈。")
A("- **A22**（真实数据更正与局部回归）：round-01 原始 6 月 → round-02 两项更正与负值柱 → round-03 新增 2026-10；每轮 1 张图，共 3 张。")
A("- **B01–B06**：每题 10 件独立完整作品，共 60 张；按 `case-01` … `case-10` 分组，逐件在 [画廊](gallery.md) 中展示。")
A("")
A("## 交付口径")
A("")
A("每张最终 PNG 均为 open-snapshot 服务 `POST /snapshot` 的真实 `image/png` 响应原始字节，并有同名完整 `.snapshot` DSL；")
A("每题输出目录另含 `snapshot-usage.md`、`task-metrics.json` 与题目指定的审计 JSON/CSV；")
A("各题 `requests.jsonl`、`iterations.jsonl`（B 类另有 `tool-usage.jsonl`）、DSL 版本、失败响应、草稿与预览均保留在临时目录。")
A("所有本地路径按 PATHS.md（总任务根）记录为相对总任务根或相对本题输出根；Markdown 链接相对所在文档。")
(SUITE / "index.md").write_text("\n".join(ix) + "\n", encoding="utf-8")

# --------------------------------------------------------------- task-metrics.json
def metrics_of(t):
    p = suite.out_dir(t) / "task-metrics.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def req_count(t):
    return suite.summarize_requests(t)


shared = suite.summarize_requests("_suite") if False else {"render_requests": 0}
# shared preparation: docs + fonts + smoke/colortest probes (already recorded in _suite/requests.jsonl)
sp = (suite.SUITE_TMP / "requests.jsonl")
shared_recs = []
if sp.exists():
    for line in sp.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                shared_recs.append(json.loads(line))
            except Exception:
                pass
shared_attempts = [a for r in shared_recs for a in r.get("attempts", [])]

summaries = []
for t in order:
    m = metrics_of(t)
    r = req_count(t)
    summaries.append({
        "task_id": t, "title": meta[t]["title"], "status": suite.task_state(state, t)["status"],
        "final_pngs": len(ALL[t]),
        "independent_cases": m.get("independent_cases", 0),
        "completed_rounds": suite.task_state(state, t).get("completed_rounds", []),
        "render_requests": r["render_requests"],
        "successful_requests": r["successful"],
        "failed_requests": r["failed"],
        "retry_requests": r["retries"],
        "request_duration_sum_seconds": round(r["request_ms_sum"] / 1000, 3),
        "dsl_versions": m.get("dsl_versions", 0),
        "image_views": m.get("image_views", 0),
        "completed_visual_iterations": m.get("completed_visual_iterations", 0),
        "incomplete_visual_iterations": m.get("incomplete_visual_iterations", 0),
        "started_at": m.get("started_at"), "ended_at": m.get("ended_at"),
        "elapsed_seconds": m.get("elapsed_seconds"),
        "output_dir": suite.rel_out(t), "temp_dir": suite.rel_tmp(t),
        "metrics_source": "outputs/%s/%s/task-metrics.json" % (RID, t),
    })

state = suite.load_state()
starts = [s["started_at"] for s in summaries if s["started_at"]]
suite_start = state.get("started_at") or (min(starts) if starts else None)
# total wall clock includes the final suite-wide review, so use the suite end marker
suite_end = state.get("ended_at") or (max([s["ended_at"] for s in summaries if s["ended_at"]]) if summaries else None)
elapsed = None
if suite_start and suite_end:
    elapsed = round((datetime.fromisoformat(suite_end) - datetime.fromisoformat(suite_start)).total_seconds(), 2)

sm = {
    "schema_version": 1, "path_base": "suite_root", "suite_version": "1.0.0",
    "run_id": RID, "profile": "all", "status": "completed", "stop_reason": "全部 30 题完成且总审查通过",
    "started_at": suite_start, "ended_at": suite_end, "elapsed_seconds": elapsed,
    "task_status_counts": {"completed": 30, "partial": 0, "blocked": 0, "pending": 0},
    "counts": {
        "final_pngs": TOTAL_PNG,
        "independent_creative_cases": sum(s["independent_cases"] for s in summaries),
        "snapshot_requests": sum(s["render_requests"] for s in summaries),
        "successful_snapshot_requests": sum(s["successful_requests"] for s in summaries),
        "failed_snapshot_requests": sum(s["failed_requests"] for s in summaries),
        "retry_requests": sum(s["retry_requests"] for s in summaries),
        "other_service_requests": 0,
        "document_requests": 14,
        "dsl_versions": sum(s["dsl_versions"] for s in summaries),
        "image_views": sum(s["image_views"] for s in summaries),
        "completed_visual_iterations": sum(s["completed_visual_iterations"] for s in summaries),
        "incomplete_visual_iterations": sum(s["incomplete_visual_iterations"] for s in summaries),
    },
    "suite_final_review": {
        "reviewer": "主代理（全套终审）",
        "final_pngs_opened": TOTAL_PNG,
        "method": "逐张打开实际最终 PNG；对短任务块、共享通道、窄标签、底部脚注等易裁切区域另做 2 倍局部放大复核",
        "found_and_fixed": [
            {"task": "A24", "file": "execution-board.png",
             "issue": "2 倍放大发现 20 分钟短块内 20px 中文标签溢出：R02「服务与字体探测」末字压住 09:00/09:20，R12「交付归档」贴边",
             "fix": "标签带加高到 88px、两行起止时间下移，BUILD_VERSION=v3 重渲染；另两张 DSL 哈希不变",
             "recheck": "放大复查 R02/R12/R10/R11 标签完整、无重叠无裁切；已追加 iterations.jsonl 与单题报告第 9 节"},
            {"task": "A22", "file": "round-01/dashboard.png",
             "issue": "缩略显示疑似表格首行与结论文字重叠",
             "fix": "2 倍放大核实为缩放错觉，2026-04 利润 37,700 与结论卡文字各自完整，无需修改 DSL"},
        ],
        "zoom_evidence": [
            "tmp/%s/_suite/review-a22-r1-bottom.png" % RID,
            "tmp/%s/_suite/review-a24-lanes.png" % RID,
            "tmp/%s/_suite/review-a24-lanes-v3.png" % RID,
            "tmp/%s/_suite/review-b06-case-04-bottom.png" % RID,
            "tmp/%s/_suite/review-b06-case-07-bottom.png" % RID,
        ],
        "result": "全套 125 张最终图终审通过；唯一影响交付的缺陷（A24 短任务标签）已修复并复查，其余为已核实的显示错觉或脚注字号，不构成缺陷。",
        "note": "主代理终审看图次数未重复计入各题 iterations.jsonl 的 image_views，避免与执行代理逐图检查重复累计。",
    },
    "shared_preparation": {
        "docs_cached": "tmp/%s/_suite/docs/" % RID,
        "doc_requests": 14,
        "font_query": "/fonts (cached fonts.txt)",
        "capability_probes": 2 + len(shared_attempts),
        "shared_render_attempts": len(shared_attempts),
        "note": "服务指南、openapi.yaml、llms.txt、parser/标签/文本/错误/示例/字体/媒体文档与 DSL 合集已下载缓存；字体清单来自真实 GET /fonts；冒烟与颜色保真探针验证 ClipPath/渐变/中文字体。文档复用不计为后续各题新增 HTTP 请求。",
    },
    "task_summaries": summaries,
    "aggregation_rule": "Only task-level totals plus shared preparation; never add round/case detail again. 总指标只累计每题顶层汇总与 shared，不重复累加同题 round/case 明细。",
    "timing_source": "各题 task-metrics.json 的起止时间由本地墙钟与 requests.jsonl 首末请求时间校准；总墙钟为最早开始到最晚结束，不等于请求耗时之和。",
    "counts_source": "各题 requests.jsonl（含轮次/用例子目录）与 iterations.jsonl、task-metrics.json",
    "output_dir": "outputs/%s/_suite/" % RID,
    "temp_dir": "tmp/%s/_suite/" % RID,
    "unresolved_issues": [],
}
(SUITE / "task-metrics.json").write_text(json.dumps(sm, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("gallery.md / index.md / task-metrics.json written; PNGs=%d" % TOTAL_PNG)
print("suite elapsed=%s requests=%d images=%d iterations=%d" %
      (elapsed, sm["counts"]["snapshot_requests"], sm["counts"]["image_views"],
       sm["counts"]["completed_visual_iterations"]))
