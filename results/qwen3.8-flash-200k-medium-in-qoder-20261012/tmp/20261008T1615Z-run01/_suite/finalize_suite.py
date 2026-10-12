import json, os, datetime, shutil

RUN = "20261008T1615Z-run01"
ROOT = "outputs/" + RUN
SUITE = ROOT + "/_suite/"
TMP = "tmp/" + RUN
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

checks = json.load(open(TMP + "/_suite/final-review-checks.json", encoding="utf-8"))
metrics = json.load(open(SUITE + "task-metrics.json", encoding="utf-8"))

metrics["final_review"] = {
    "checked_at": NOW,
    "script": TMP + "/_suite/final_review.py",
    "machine_readable": TMP + "/_suite/final-review-checks.json",
    "png_provenance": TMP + "/_suite/png-provenance.json",
    "dsl_provenance": TMP + "/_suite/dsl-provenance.json",
    "checks": checks,
    "result": "passed" if all(c["result"] == "PASS" for c in checks) else "failed",
    "checks_total": len(checks),
    "checks_passed": sum(1 for c in checks if c["result"] == "PASS"),
    "corrections_made_during_review": [
        "B01/task-metrics.json 的 status 由陈旧 in_progress 改为 completed，并补 status_before_correction / status_corrected_at / stop_reason 与计数说明；作品数、请求数、迭代数未改动。",
        "套件请求/文档计数改按各题实发日志重数：B03 snapshot_requests 135→131（4 次文档 GET 归回文档类），B04 86→45（40 次外部资料 GET 与 1 次 GET /fonts 单列）。各题自报原值保留在 task_summaries[].counts。",
        "汇总脚本 tmp/_suite/collect_suite_facts.py 存在列表别名缺陷（suite_recs = shared 后被 += 就地扩展），使 shared 请求数写成 1402；改为 list(shared) 后重算为 15 次文档 GET，文档总数 66。",
        "B01 case-06 / case-09 的留存 .body.txt 当年按文本模式写入带 CRLF；DSL 字节比对对换行做归一后与交付 .snapshot 完全一致，provenance 记为 retained_request_lf_normalized 并在报告注明。",
        "gallery.md 与 index.md 的图片/DSL 链接统一改为相对 _suite/ 的 ../<task>/…；索引状态与请求口径改为直接读 task-metrics.json，避免两处数字漂移。",
        "最终审查新增两项：交付 DSL 内不写机器路径（唯一命中 A11/invoice-page-02.snapshot 是题面要求逐字保真的输入样本原文），以及画廊只列最终作品不含 preview/zoom/qa/probe。",
    ],
}
json.dump(metrics, open(SUITE + "task-metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

state = json.load(open(SUITE + "suite-state.json", encoding="utf-8"))
b06 = [t for t in state["tasks"] if t["id"] == "B06"][0]
b06m = json.load(open(ROOT + "/B06/task-metrics.json", encoding="utf-8"))
b06["status"] = "completed"
b06["ended_at"] = b06m["timings"]["task_ended_at"]
b06["artifacts"] = (["outputs/%s/B06/case-%02d/final.png" % (RUN, i) for i in range(1, 11)]
                    + ["outputs/%s/B06/case-%02d/final.snapshot" % (RUN, i) for i in range(1, 11)]
                    + ["outputs/%s/B06/case-%02d/case.md" % (RUN, i) for i in range(1, 11)]
                    + ["outputs/%s/B06/%s" % (RUN, f) for f in
                       ("gallery.md", "portfolio.md", "portfolio.json", "design-review.md",
                        "problem-evidence.json", "snapshot-usage.md", "task-metrics.json")]
                    + [TMP + "/B06/requests.jsonl", TMP + "/B06/iterations.jsonl", TMP + "/B06/tool-usage.jsonl"])
b06["artifacts_note"] = ("收尾时逐条登记的 artifacts 前 3 项写成了题内相对路径、其余写成完整相对路径，"
                         "口径不一致；总审查按 outputs/<run>/B06/… 统一重列（文件本身未移动未改名），"
                         "原登记内容没有丢失任何产物。")
b06["completion_evidence"] = (
    "10 个 case-NN 各 1 张 final.png + 同名 final.snapshot（共 10 张，题内最低 10）；"
    "requests.jsonl 49 条实发（200 41 / 400 3 / 传输失败 5，其中 1 次服务端 cache 命中）、"
    "iterations.jsonl 记录 12 次完整视觉迭代、tool-usage.jsonl 32 条；"
    "每张 final 由 promote.py 以 md5 字节指纹从服务原始响应提升，开图自检记录在 visual_review_evidence。")

for t in state["tasks"]:
    m = json.load(open(os.path.join(ROOT, t["id"], "task-metrics.json"), encoding="utf-8"))
    if m.get("status") == "completed" and t["status"] != "completed":
        t["status"] = "completed"
        if not t.get("ended_at"):
            ti = m.get("timings") or {}
            t["ended_at"] = ti.get("ended_at") or ti.get("task_ended_at")

state["status"] = "completed"
state["current_task"] = None
state["current_round"] = None
state["current_case"] = None
state["updated_at"] = NOW
state["completed_at"] = NOW
state["suite_artifacts"] = [SUITE + f for f in ("index.md", "gallery.md", "snapshot-usage.md",
                                                "task-metrics.json", "suite-state.json")]
state["final_review"] = {
    "checked_at": NOW,
    "result": metrics["final_review"]["result"],
    "checks_passed": metrics["final_review"]["checks_passed"],
    "checks_total": metrics["final_review"]["checks_total"],
    "detail": TMP + "/_suite/final-review-checks.json",
    "summary": "17 项套件级检查全部通过：五件套齐备、画廊 125 张逐图（标题+预览+PNG+DSL 链接）"
               "且链接全部可解析、125 张 PNG 的 md5 全部对到留存的服务响应字节、125 份 DSL 全部"
               "对到独立留存的请求体、每题图片数达标、B 轨 tool-usage 齐备、A21/A22 三轮齐备、"
               "过程日志齐备、.gitignore 未忽略证据、交付文件无机器路径。",
}
state["stop_reason"] = ("30 题全部 completed 并通过套件级总审查：%d 张最终图片（题库最低 %d），"
                        "每张同名完整 .snapshot 且实际开图自检；B01–B06 每题 10 个独立用例；"
                        "A21/A22 三个预置轮次全部交付；套件五件交付齐备。"
                        % (metrics["counts"]["final_pngs"], 124))

nxt = max(int(os.path.basename(p)[6:-5]) for p in os.listdir(TMP + "/_suite/checkpoints")) + 1
cp = "%s/_suite/checkpoints/state-%06d.json" % (TMP, nxt)
json.dump(state, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
state["last_checkpoint"] = cp
json.dump(state, open(SUITE + "suite-state.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

events = [
    {"ts": b06["ended_at"], "run_id": RUN, "task_id": "B06", "event": "task-completed",
     "status": "completed",
     "note": "B06 十件作品与 7 份根产物交付完毕（最晚留痕 15:26:55Z）；本条在套件总审查时补记，"
             "时间为该题实际最后留痕。", "path_base": "suite_root"},
    {"ts": NOW, "run_id": RUN, "task_id": None, "event": "suite-review-passed", "status": "completed",
     "note": "套件级 17 项检查全部 PASS；审查中修正 B01 陈旧状态、按日志重数请求/文档口径、"
             "修掉汇总脚本的列表别名缺陷、对 B01 两件 CRLF 留存体做换行归一并注明。",
     "path_base": "suite_root"},
    {"ts": NOW, "run_id": RUN, "task_id": None, "event": "suite-completed", "status": "completed",
     "note": "五件套件交付齐备（index/gallery/snapshot-usage/task-metrics/suite-state），"
             "125 张最终图片（≥124），检查点 %s。" % cp, "path_base": "suite_root"},
]
with open(TMP + "/_suite/events.jsonl", "a", encoding="utf-8") as f:
    for e in events:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

print("review result", metrics["final_review"]["result"],
      metrics["final_review"]["checks_passed"], "/", metrics["final_review"]["checks_total"])
print("suite status", state["status"], "task statuses",
      {s: sum(1 for t in state["tasks"] if t["status"] == s) for s in ("completed", "partial", "blocked", "in_progress")})
print("checkpoint", cp)
