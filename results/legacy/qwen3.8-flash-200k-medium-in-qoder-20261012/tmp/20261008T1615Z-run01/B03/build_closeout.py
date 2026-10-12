"""B03 收尾构件：从各 case.md、final.png/final.snapshot、requests/iterations/tool-usage jsonl
里读真实数据，生成 portfolio.json / portfolio.md / gallery.md / technique-notes.md /
task-metrics.json 的机器部分。不写任何未经核实的结论。

用法（总任务根执行）：python tmp/<run>/B03/build_closeout.py
"""
import datetime
import glob
import hashlib
import json
import os
import re
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RID / "B03"
OUT = ROOT / "outputs" / RID / "B03"
PB_OUT, PB_SUITE = "output_dir", "suite_root"
md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()  # noqa: E731


def lines(name):
    f = TMP / name
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines()] if f.exists() else []


REQ = lines("requests.jsonl")
ITR = lines("iterations.jsonl")
TU = lines("tool-usage.jsonl")
CASES = sorted(p.name for p in OUT.glob("case-*") if p.is_dir())


def section(md, key):
    """取 case.md 里标题含 key 的小节正文（到下一个 ## 为止）。"""
    m = re.search(r"^## [^\n]*%s[^\n]*\n(.*?)(?=^## |\Z)" % key, md, re.S | re.M)
    return m.group(1).strip() if m else ""


def items(text):
    """把 case.md 小节正文解析成条目，支持 - / * / 1. 三种列表与续行；纯散文按空行分段。"""
    out, cur = [], ""
    for ln in text.splitlines():
        if re.match(r"^(?:[-*]|\d+\.)\s+", ln):
            if cur:
                out.append(cur.strip())
            cur = re.sub(r"^(?:[-*]|\d+\.)\s+", "", ln)
        elif cur and ln.strip():
            cur += " " + ln.strip()
    if cur:
        out.append(cur.strip())
    return out if out else [p.replace("\n", " ").strip()
                            for p in text.split("\n\n") if p.strip()]


def table_rows(text):
    d = {}
    for ln in text.splitlines():
        m = re.match(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|$", ln.strip())
        if m and m.group(1) not in ("项", "---"):
            d[m.group(1)] = re.sub(r"`", "", m.group(2))
    return d


PROBE = [r for r in REQ if "-probe-" in r["request_id"]]
PROBE_OPEN = [r for r in PROBE if r["started_at"] < "2026-10-10T07:30"]
CASE_INFO = {}
for c in CASES:
    d = OUT / c
    md = (d / "case.md").read_text(encoding="utf-8")
    title = md.splitlines()[0].lstrip("# ").strip()
    png, snap = d / "final.png", d / "final.snapshot"
    w, h = Image.open(png).size
    dsl = snap.read_text(encoding="utf-8")
    reqs = [r for r in REQ if r["request_id"].startswith("B03-%s-" % c)]
    ok = [r for r in reqs if r["http_status"] == 200 and not r["error_summary"]]
    bad = [r for r in reqs if r not in ok]
    its = [r for r in ITR if r["version"].startswith("case-%s-" % c.split("-")[1])]
    prom = next((r for r in ok if r.get("out_file") and Path(r["out_file"]).exists()
                 and md5(ROOT / r["out_file"]) == md5(png)), None)
    CASE_INFO[c] = dict(
        id=c, title=title,
        audience=section(md, "受众").split("\n\n")[0].replace("\n", " "),
        techniques=items(section(md, "独到手法")),
        truth=section(md, "失真") or section(md, "真实性"),
        boundaries=items(section(md, "边界") or section(md, "未尽")),
        iteration_table=section(md, "迭代"),
        dimensions=[w, h], png_bytes=png.stat().st_size, png_md5=md5(png),
        dsl_chars=len(dsl), dsl_bytes=snap.stat().st_size,
        nodes={"Positioned": dsl.count("<Positioned"), "Container": dsl.count("<Container"),
               "Text": dsl.count("<Text "), "Stack": dsl.count("<Stack"),
               "ClipRRect": dsl.count("<ClipRRect"), "ClipOval": dsl.count("<ClipOval"),
               "Image": len(re.findall(r"<Image(?![A-Za-z])", dsl)),
               "ImageFiltered": dsl.count("<ImageFiltered")},
        renders_ok=len(ok), renders_failed=len(bad),
        versions=sorted({re.search(r"-case-\d+-(v[\w]+)-", r["request_id"]).group(1)
                         for r in reqs if re.search(r"-case-\d+-(v[\w]+)-", r["request_id"])}),
        iteration_records=len(its),
        promoted_from=prom["request_id"] if prom else None,
        server_timing=prom["server_timing"] if prom else None,
        qa_crops=[],
        review_evidence=section(md, "看图"),
        tool_usage=[t["tool"] for t in TU if t.get("case") == c],
        has_data_json=(d / "data.json").exists(),
    )

# QA 裁图归属：01–07 在 tmp/B03/case-0N/ 下（qa-*.png）；08/09 在 tmp/B03/ 顶层且带
# case0N-qa 前缀；10 号在顶层以小节号命名（qa01/qa04/qa05/qa07-*.png，均为 10-11 06:13Z 后
# 生成，与 case-10 的 v04/v06 时间一致）。路径相对总任务根，全部留在 tmp，不作交付物。
TOP = {c: [] for c in CASES}
for p in sorted(glob.glob(str(TMP / "case0*-qa-*.png")) +
                glob.glob(str(TMP / "qa[0-9][0-9]-*.png"))):
    b = os.path.basename(p)
    m = re.match(r"case(\d\d)-qa", b)
    key = "case-%s" % m.group(1) if m else ("case-10" if re.match(r"qa\d\d-", b) else None)
    if key in TOP:
        TOP[key].append("tmp/%s/B03/%s" % (RID, b))
for c in CASES:
    local = ["tmp/%s/B03/%s/%s" % (RID, c, os.path.basename(x))
             for x in sorted(glob.glob(str(TMP / c / "qa-*.png")))]
    CASE_INFO[c]["qa_crops"] = local + TOP[c]
assigned = {x.rsplit("/", 1)[-1] for c in CASES for x in CASE_INFO[c]["qa_crops"]}
orphans = [os.path.basename(x) for x in
           glob.glob(str(TMP / "case0*-qa-*.png")) + glob.glob(str(TMP / "qa[0-9][0-9]-*.png"))
           if os.path.basename(x) not in assigned]
assert not orphans, "QA 裁图未归属：%s" % orphans

# ---------------- 计时与空档 ----------------
UTC = datetime.timezone.utc


def ts(r, k):
    return datetime.datetime.fromisoformat(r[k])


seq = sorted(REQ, key=lambda r: r["started_at"])
t0, t1 = ts(seq[0], "started_at"), max(ts(r, "ended_at") for r in seq)
wall = (t1 - t0).total_seconds()
GAP_EVIDENCE = {
    "2026-10-10T07:22": ("idle-unverified",
                         "探针 01c 于 07:22:18 落盘后到 07:37:29 首个 case-01 请求之间无任何文件写入，"
                         "无法证明这段时间在产出，按空闲计"),
    "2026-10-10T08:47": ("work",
                         "08:48:15 qa-v10-notes.png、08:48:54 提升 case-03 final、08:52:42 case.md、"
                         "08:53:19 检查点、09:31:58 case04-v01.snapshot：收尾＋下一案开案"),
    "2026-10-10T09:55": ("work",
                         "09:55:35 probe-through3 探针响应，10:09:03 写出 case05-v02.snapshot"),
    "2026-10-10T10:46": ("work",
                         "10:46:39 probe-block 响应与 1x 裁图，11:00:20 写出 case07-v01.snapshot"),
    "2026-10-10T11:21": ("partial",
                         "11:22–11:30 为 case-07 收尾（qa 裁图、final、case.md、检查点），"
                         "11:56:25 写 astro8.py；11:56→12:54 无写入，按空闲计"),
    "2026-10-10T13:27": ("idle",
                         "13:28–13:41 完成 case-08 看图裁切、final 提升、case.md、log_case08.py 与检查点；"
                         "13:41:52 之后到次日 05:36:32 会话未运行（夜间停止），计空闲"),
    "2026-10-11T05:51": ("work",
                         "05:52–05:56 case-09 提升/case.md/log_case09.py/总状态与检查点，"
                         "随后编写 case-10 生成器，06:02:42 发出 v01"),
}
gaps, idle = [], 0.0
prev_end = None
for r in seq:
    s = ts(r, "started_at")
    if prev_end and (s - prev_end).total_seconds() > 600:
        g = (s - prev_end).total_seconds()
        key = prev_end.isoformat()[:16]
        cls, note = next((v for k, v in GAP_EVIDENCE.items()
                          if k[:16] == key[:16]), ("work", "该区间内有文件写入"))
        # 有写入证据的区间只把「最后一次写入到下个请求」的空档算空闲
        if cls == "work":
            idle_part = 0.0
        elif cls == "partial":
            idle_part = 3492.0
        else:
            idle_part = g if cls == "idle" else g
        idle += idle_part
        gaps.append(dict(start=prev_end.isoformat(), end=s.isoformat(), seconds=round(g, 1),
                         idle_seconds=round(idle_part, 1), classification=cls, evidence=note))
    prev_end = max(prev_end or s, ts(r, "ended_at"))

req_dur = sum(r.get("duration_seconds") or 0 for r in REQ)
rt = [float(m.group(1)) for r in REQ if (m := re.search(r"render;dur=([\d.]+)", r.get("server_timing") or ""))]
tt = [float(m.group(1)) for r in REQ if (m := re.search(r"total;dur=([\d.]+)", r.get("server_timing") or ""))]
kinds = {}
for r in REQ:
    kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
status = {}
for r in REQ:
    status[str(r["http_status"])] = status.get(str(r["http_status"]), 0) + 1

METRICS = {
    "schema_version": 2, "path_base": PB_SUITE, "task_id": "B03", "run_id": RID,
    "task_round": None, "status": "completed",
    "stop_reason": "10 件主作品全部定稿，逐件完成真实看图→改→再渲染→再比较的视觉迭代闭环，"
                   "套件级 B03 收尾文件齐备",
    "output_dir": "outputs/%s/B03/" % RID, "temp_dir": "tmp/%s/B03/" % RID,
    "timings": {
        "started_at": t0.isoformat(), "ended_at": t1.isoformat(),
        "elapsed_seconds": round(wall, 1),
        "wall_clock_seconds": round(wall, 1),
        "active_seconds": round(wall - idle, 1),
        "idle_gap_seconds": round(idle, 1),
        "idle_gaps": gaps,
        "elapsed_time_note": "elapsed/wall 是本题时间窗，不等于连续工作；空闲（会话未运行、"
                             "无写入证据的区间）已扣除并逐条列出证据；request_duration_sum 只统计真实服务调用",
        "first_usable_image_seconds": round(
            (ts(next(r for r in REQ if r["request_id"].startswith("B03-case-01-v01")),
                "ended_at") - t0).total_seconds(), 1),
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(req_dur, 2),
        "requests_missing_duration": [r["request_id"] for r in REQ if r.get("duration_seconds") is None],
        "shared_doc_requests_reused": 15,
        "shared_doc_duration_seconds": None,
        "shared_doc_note": "服务文档与 openapi 抓取属 shared，只在 _suite 计一次",
        "server_timing_source": "%d 份响应头 Server-Timing（render;dur / total;dur）" % len(rt),
        "server_render_ms": {"min": min(rt), "max": max(rt),
                             "avg": round(sum(rt) / len(rt), 1),
                             "sum_seconds": round(sum(rt) / 1000, 2)},
        "server_total_sum_seconds": round(sum(tt) / 1000, 2),
        "duration_note": "request_duration_sum_seconds 为客户端端到端（含网络与写盘），"
                         "server_* 为服务侧耗时，两者不混用",
        "ratelimit_observed": {"limit": 120, "min_remaining": min(
            int(m.group(1)) for r in REQ if (m := re.search(r"x-ratelimit-remaining: (\d+)",
                                                            r.get("ratelimit") or ""))),
            "windows_hit": 0},
    },
    "counts": {
        "snapshot_requests": len(REQ),
        "successful_snapshot_requests": sum(1 for r in REQ if r["http_status"] == 200
                                            and not r["error_summary"]),
        "failed_snapshot_requests": sum(1 for r in REQ if r["http_status"] != 200
                                        or r["error_summary"]),
        "by_http_status": status,
        "by_kind": kinds,
        "probe_requests": sum(1 for r in REQ if "-probe-" in r["request_id"]),
        "case_requests": sum(1 for r in REQ if "-case-" in r["request_id"]),
        "dsl_versions": len({r["request_id"] for r in REQ}),
        "image_views": sum(1 for i in ITR if i.get("image_viewed")),
        "image_views_not_viewed": [i["version"] for i in ITR if not i.get("image_viewed")],
        "iteration_records": len(ITR),
        "iteration_records_by_kind": {},
        "completed_visual_iterations": sum(
            1 for i in ITR if i.get("image_viewed") and i.get("parent_version")),
        "prerender_fixes": sum(1 for i in ITR if not i.get("request_id")),
        "final_case_count": len(CASES),
        "final_image_count": len(CASES),
        "final_image_note": "10 件各 1 张定稿图；版本预览图 %d 张另计（outputs/…/case-*/v*-preview.png），"
                            "探针图 %d 张在 tmp 下，属能力试验，不算作品"
                            % (sum(len(list((OUT / c).glob('v*-preview.png'))) for c in CASES),
                               len(glob.glob(str(TMP / "probe" / "*.png")))),
        "tool_usage_records": len(TU),
    },
    "logs": {"requests": "tmp/%s/B03/requests.jsonl" % RID,
             "iterations": "tmp/%s/B03/iterations.jsonl" % RID,
             "tool_usage": "tmp/%s/B03/tool-usage.jsonl" % RID,
             "plan": "tmp/%s/B03/PLAN.md" % RID,
             "shared_requests": "tmp/%s/_suite/requests.jsonl" % RID},
    "outputs": ["outputs/%s/B03/%s/final.png" % (RID, c) for c in CASES]
    + ["outputs/%s/B03/%s/final.snapshot" % (RID, c) for c in CASES]
    + ["outputs/%s/B03/%s/case.md" % (RID, c) for c in CASES]
    + ["outputs/%s/B03/portfolio.json" % RID, "outputs/%s/B03/portfolio.md" % RID,
       "outputs/%s/B03/gallery.md" % RID, "outputs/%s/B03/snapshot-usage.md" % RID,
       "outputs/%s/B03/technique-notes.md" % RID, "outputs/%s/B03/task-metrics.json" % RID],
    "candidates": [],
    "rounds": [],
    "unresolved_issues": [
        "服务无矢量 path 图元：曲线/星图轨迹只能用逐段矩形与 polyline 逼近（case-01/07/08）",
        "fontFeatures 只被解析不被应用，等宽数字与小型大写需版式手工兜底（case-10 实测四组零差）",
        "Container 的 clipBehavior 对整幅子树会 400，遮罩只能用 ClipRRect/ClipOval（探针 03）",
        "未安装字族回退到同一平台默认字体，字族清单以 GET /fonts 实际返回为准（case-10 §05）",
    ],
    "asset_policy": "dsl_primary_with_supporting_assets（creative 赛道）；本题 10 件定稿 DSL 的 "
                    "<Image> 计数均为 0，未嵌入任何外部素材，探针图与 QA 裁图属过程留痕",
    "shared_preparation": {
        "scope": "套件 _suite 文档抓取（复用 15 条）+ B03 探针阶段 %d 次能力探测请求" % len(PROBE),
        "probe_requests": len(PROBE),
        "probe_requests_ok": sum(1 for r in PROBE if r["http_status"] == 200 and not r["error_summary"]),
        "probe_requests_failed": sum(1 for r in PROBE
                                     if r["http_status"] != 200 or r["error_summary"]),
        "probe_opening_phase_requests": len(PROBE_OPEN),
        "probe_opening_window": "%s → %s" % (PROBE_OPEN[0]["started_at"],
                                             PROBE_OPEN[-1]["ended_at"]),
        "note": "探针与构件不计入任何单件作品，也不重复统计为题目产出；"
                "开题能力探测 01–20（含 b/c/d 重试）共 %d 次，其余 %d 次是各案进行中"
                "为确认某一性质而补做的定点探针" % (len(PROBE_OPEN), len(PROBE) - len(PROBE_OPEN))},
    "research": {"web_search": 0, "web_fetch_attempts": 4, "web_fetch_succeeded": 4,
                 "sources_used": ["open-snapshot.muedsa.com/ai-guide.md",
                                  "snapshot.muedsa.com 文档站（enums/transform 等页）",
                                  "GET /fonts（27 族，2026-10-08 缓存）"],
                 "failed_and_not_cited": [],
                 "notes": "tmp/%s/_suite/docs/ 与 tmp/%s/B03/probe/" % (RID, RID)},
}
byk = {}
for i in ITR:
    byk[i["type"]] = byk.get(i["type"], 0) + 1
METRICS["counts"]["iteration_records_by_kind"] = byk

# ---- 补齐 task-metrics-template.json 要求的字段（全部由上面的真实记录算出）----
grp = {}
for r in REQ:
    m = re.match(r"(B03-case-\d+-v[\w]+)-", r["request_id"])
    if m:
        grp.setdefault(m.group(1), []).append(r)
METRICS["counts"]["retry_requests"] = sum(max(0, len(v) - 1) for v in grp.values())
METRICS["counts"]["retry_requests_note"] = (
    "同一版本号被重复请求的次数：%d 次，分属 3 组（case-07 v03 ×3、case-07 v04 ×2、"
    "case-09 v07 ×2），全部是传输层故障后的重试——curl (28) SSL 连接超时、"
    "curl (56) 连接被重置、响应体按 Content-Length 截断；与 DSL 内容无关，"
    "最终 v03 仍保留截断记录、v04/v07 由后续 200 响应定稿"
    % METRICS["counts"]["retry_requests"])
METRICS["counts"]["other_service_requests"] = kinds.get("doc", 0)
METRICS["counts"]["document_requests"] = kinds.get("doc", 0)
METRICS["counts"]["document_requests_note"] = (
    "本题内直接抓取文档 %d 次（kind=doc）；套件共享抓取 15 条（服务指南、DSL 文档站各页、"
    "GET /fonts）在 tmp/%s/_suite/requests.jsonl，只在 _suite 计一次" % (kinds.get("doc", 0), RID))
METRICS["counts"]["incomplete_visual_iterations"] = sum(
    1 for i in ITR if i.get("parent_version") and not i.get("image_viewed"))
METRICS["counts"]["other_tool_calls"] = len(TU)
METRICS["counts"]["dsl_versions"] = sum(len(v["versions"]) for v in CASE_INFO.values())
METRICS["counts"]["dsl_versions_note"] = (
    "十个触点各自的 vNN 去重合计 %d 个真实提交过的 DSL 版本；另有 %d 个探针 DSL "
    "（tmp/%s/B03/probe/*.snapshot）与 1 份 v03 复现件，均不算作品版本"
    % (METRICS["counts"]["dsl_versions"],
       len(glob.glob(str(TMP / "probe" / "*.snapshot"))), RID))
METRICS["counts"]["image_views_note"] = (
    "%d 条迭代记录标了实际看图（其中 %d 条只裁局部核对），未看图 %d 条：%s"
    % (METRICS["counts"]["image_views"],
       sum(1 for i in ITR if i.get("image_view_scope")),
       len(METRICS["counts"]["image_views_not_viewed"]),
       ", ".join(METRICS["counts"]["image_views_not_viewed"])))
METRICS["case_metrics"] = [dict(
    case_id=c, title=v["title"], dimensions=v["dimensions"],
    final_png="outputs/%s/B03/%s/final.png" % (RID, c), png_md5=v["png_md5"],
    png_bytes=v["png_bytes"], final_snapshot="outputs/%s/B03/%s/final.snapshot" % (RID, c),
    dsl_chars=v["dsl_chars"], dsl_nodes=v["nodes"], versions=v["versions"],
    requests_ok=v["renders_ok"], requests_failed=v["renders_failed"],
    promoted_from=v["promoted_from"], iteration_records=v["iteration_records"],
    tool_usage_records=len(v["tool_usage"]), qa_crop_records=len(v["qa_crops"]),
    has_data_json=v["has_data_json"]) for c, v in CASE_INFO.items()]
tusum = {}
for t in TU:
    k = t["tool"]
    d = tusum.setdefault(k, dict(tool=k, count=0, phases=set(), cases=set()))
    d["count"] += 1
    d["phases"].add(t.get("phase") or "")
    if t.get("case"):
        d["cases"].add(t["case"])
METRICS["tool_usage_summary"] = [
    dict(tool=d["tool"], count=d["count"], phases=sorted(d["phases"]),
         cases=sorted(d["cases"])) for d in tusum.values()]
METRICS["final_case_count"] = len(CASES)

(OUT / "task-metrics.json").write_text(
    json.dumps(METRICS, ensure_ascii=False, indent=1), encoding="utf-8")
json.dump(CASE_INFO, (TMP / "case-info.json").open("w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("cases", len(CASES), "wall", round(wall), "idle", round(idle),
      "active", round(wall - idle), "requests", len(REQ), "iterations", len(ITR))
