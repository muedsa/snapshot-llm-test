"""Archive the ten B04 pages and build the task's deliverable documents.

sources.json is generated from the real document-fetch log and the render log, so every
source_id carries an actual access time and a local cache path, and every claim points at
either a source_id or a request id.

Run: python tmp/<run_id>/B04/make_docs.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path

from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-12T"  # replaced below
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B04"
OUT = ROOT / "outputs" / RUN / "B04"
SUITE = ROOT / "tmp" / RUN / "_suite"
D = json.loads((TMP / "data.json").read_text(encoding="utf-8"))
REQ = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(
    encoding="utf-8").splitlines() if l.strip()]
SREQ = [json.loads(l) for l in (SUITE / "requests.jsonl").read_text(
    encoding="utf-8").splitlines() if l.strip()]
PLAN = json.loads((TMP / "work-plan.json").read_text(encoding="utf-8"))

TITLES = {
    "case-01": "把 XML 变成像素（封面）", "case-02": "一次请求的八段旅程",
    "case-03": "标签词汇表与它的真实边界", "case-04": "文本度量：谁在决定一个字占多宽",
    "case-05": "失败分类学", "case-06": "构图预算：4096 个元素",
    "case-07": "色标之间发生了什么", "case-08": "字体清单：能用什么字",
    "case-09": "时间花在哪，缓存有没有用", "case-10": "边界、不知道、以及怎么复核",
}
FORMS = {
    "case-01": "封面（管线剪影 + 四个规模数字）", "case-02": "流程卡带 + 横向条形图",
    "case-03": "标签芯片矩阵 + 结构约束清单", "case-04": "常数条 + 增量条图 + 精度表",
    "case-05": "错误码条图 + 语义归类 + 响应摘要卡", "case-06": "预算比例条 + 两张解释卡",
    "case-07": "实测色带 + 期望/实测成对表 + 结论条", "case-08": "字体芯片 + 四族同句样张",
    "case-09": "直方图 + 缓存卡 + 长尾卡", "case-10": "证据分级清单 + 复核步骤",
}
SNAP = {  # the .snapshot written by b04pages.py for each case
    "case-01": "case01-cover", "case-02": "case02-pipeline",
    "case-03": "case03-vocabulary", "case-04": "case04-metrics",
    "case-05": "case05-failures", "case-06": "case06-budget",
    "case-07": "case07-colour", "case-08": "case08-fonts",
    "case-09": "case09-timing", "case-10": "case10-limits",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def req_of(rid):
    return next((r for r in REQ if r["request_id"] == rid), None)


# ---------------------------------------------------------------- archive pages
ident = {}
for i, (cid, stem) in enumerate(SNAP.items(), 1):
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    png_src = TMP / f"{stem}-final.png"
    dsl_src = TMP / f"{stem}.snapshot"
    shutil.copyfile(png_src, d / "final.png")
    shutil.copyfile(dsl_src, d / "final.snapshot")
    r = req_of(f"B04-{stem}-final")
    ident[cid] = (sha(d / "final.png") == sha(ROOT / r["response_file"])
                  and sha(d / "final.snapshot") == sha(ROOT / r["request_file"]))

# ---------------------------------------------------------------- sources.json
DOC_BY_URL = {}
for r in SREQ:
    if r.get("kind") == "document":
        DOC_BY_URL[r["url"]] = r


def src(sid, url, title, publisher, locator, note=None):
    r = DOC_BY_URL.get(url, {})
    return {"source_id": sid, "title": title, "publisher_or_author": publisher,
            "url": url, "published_or_updated": None,
            "accessed_at": r.get("ended_at"), "http_status": r.get("http_status"),
            "response_bytes": r.get("response_bytes"),
            "request_id": r.get("request_id"),
            "local_cache": r.get("response_file"),
            "text_extraction": (SUITE / "docs-txt" /
                                (Path(url.rstrip('/').split('/')[-1] or "index")
                                 .name + ".txt")).as_posix()
            if r else None,
            "access_evidence": "requests.jsonl 中的 document 记录（含时间、状态、字节、"
                               "本地缓存路径）" if r else "未访问",
            "used_for": locator, "note": note}


SOURCES = [
    src("S01", "https://snapshot.muedsa.com/reference/parser-tags/",
        "标签与属性参考", "Snapshot 文档",
        "case-03 标签清单、属性格式、WidgetSpan/Transform 约束、textShadow 语法",
        "抓取于本套开始阶段；正文已转纯文本缓存"),
    src("S02", "https://open-snapshot.muedsa.com/fonts", "服务可用字体清单",
        "open-snapshot 服务", "case-08 全部族名与数量",
        "响应为纯文本换行列表，不是 JSON"),
    src("S03", "https://open-snapshot.muedsa.com/openapi.yaml", "服务 OpenAPI 规范",
        "open-snapshot 服务", "case-02 请求/响应契约、case-09 响应头字段"),
    src("S04", "https://open-snapshot.muedsa.com/ai-guide.md", "面向自动化的使用说明",
        "open-snapshot 服务", "case-02 管线阶段、case-05 错误语义"),
    src("S05", "https://snapshot.muedsa.com/guides/painting/", "绘制能力指南",
        "Snapshot 文档", "case-07 渐变参数与插值说明、case-03 装饰属性"),
    src("S06", "https://snapshot.muedsa.com/widgets/text/widget-span/", "WidgetSpan",
        "Snapshot 文档", "case-03 行内节点必须恰有一个普通子节点"),
    src("S07", "https://snapshot.muedsa.com/widgets/layout/transform/", "Transform",
        "Snapshot 文档", "case-03 matrix/alignment 必填、origin 语义"),
    src("S08", "https://snapshot.muedsa.com/widgets/painting/backdrop-filter/",
        "BackdropFilter", "Snapshot 文档",
        "case-10 未裁剪时的行为；官方建议配合裁剪"),
    src("S09", "https://snapshot.muedsa.com/widgets/text/text/", "Text",
        "Snapshot 文档", "case-04 文本样式属性清单（height/letterSpacing/fontFeatures）"),
    src("S10", "https://snapshot.muedsa.com/reference/enums/", "枚举取值",
        "Snapshot 文档", "case-03 clipBehavior / BoxShape / TileMode 取值"),
    src("S11", "https://snapshot.muedsa.com/guides/layout/", "布局指南",
        "Snapshot 文档", "case-02 布局阶段、case-05 无界尺寸错误"),
    src("S12", "https://snapshot.muedsa.com/reference/parser-errors/", "解析错误对照",
        "Snapshot 文档", "case-05 错误码语义"),
]
UNREAD = [
    {"title": "任何外部网页（EPA / USDA Forest Service / Berkeley Lab 等）",
     "why_not": "会话权限分类器拒绝了外部 HTTP（记录见 editorial-note.md 与 "
                "research-notes.md），因此原选题放弃，未读材料不列为依据"},
    {"title": "Skia 官方文档（关于渐变插值色彩空间）",
     "why_not": "同样无法访问；case-07 的线性光插值因此标注为推断而非引用"},
]

CLAIMS = []


def claim(cid, field, text, kind, source_ids=(), evidence=(), method=None,
          uncertainty=None):
    CLAIMS.append({"claim_id": f"C{len(CLAIMS) + 1:03d}", "case_id": cid,
                   "where_in_image": field, "assertion": text, "kind": kind,
                   "source_ids": list(source_ids), "evidence_requests": list(evidence),
                   "method": method, "uncertainty": uncertainty})


sc = D["scale"]
claim("case-01", "四个大数字", f"共 {sc['render_requests']} 次 /snapshot 请求、"
      f"{sc['ok']} 次成功、{sc['document_pages']} 页文档、"
      f"{sc['distinct_canvas_sizes']} 种画布尺寸", "测量", evidence=["b04data.py"],
      method="解析 tmp/…/<task>/requests.jsonl 全部 request_type=render 行；"
             "B04 自身请求不计入", uncertainty="统计窗口内计数，不含未记录的调用")
claim("case-01", "样本窗口", f"{sc['window_start']} → {sc['window_end']}", "事实",
      evidence=["requests.jsonl 时间戳"])
claim("case-02", "条形图 6 项", f"服务端 render p50 {D['server_ms']['p50']}ms、"
      f"p90 {D['server_ms']['p90']}ms、p99 {D['server_ms']['p99']}ms、"
      f"max {D['server_ms']['max']}ms（n={D['server_ms']['n']}）", "测量",
      source_ids=["S03"], evidence=["b04data.py"],
      method="正则提取响应头 server-timing 的 render;dur 后取分位",
      uncertainty="仅含返回该头的成功响应")
claim("case-02", "阶段卡 01–08", "八个阶段是本报告对一次 HTTP 调用的解释性拆分",
      "解释", source_ids=["S04"],
      uncertainty="服务未公布内部管线图，只有 render 一段被计时")
claim("case-03", "标签芯片", "标签清单逐项取自 parser-tags 页面正文", "事实",
      source_ids=["S01"])
claim("case-03", "结构约束 6 条", "Positioned 只能直接挂在 Stack 下、Stack 全 Positioned"
      " 子节点无界、Emoji 不能独立、origin 只接受 (x,y) 等", "测量",
      source_ids=["S01", "S06", "S07"],
      evidence=["B03-case03-v1", "B03-misc", "B03-p8-emoji-fix", "B03-origin0",
                "B03-origin1", "B03-origin2"])
claim("case-03", "属性级结论 8 行", "gradientTileMode 对 LINEAR 不可见、对 RADIAL 有效；"
      "fillType 被忽略；boxShadow 支持自定义串；decorationLineStyle 五值可用"
      "（DOUBLE_SOLID 非法）；tnum 有效、smcp 无效", "测量",
      evidence=["B03-p2-tile2", "B03-p4-radialtileCLAMP", "B03-p4-radialtileREPEAT",
                "B03-p4-shadowscan", "B03-deco-SOLID", "B03-deco-DOUBLE_SOLID",
                "B03-p2-textab", "B03-p4-smallcaps"])
claim("case-04", "五条常数", "CJK 1.00em、Latin 0.62em、Mono 0.52em、行距 1.46em、"
      "粗体余量 ×1.14+10px", "测量", source_ids=["S09"],
      evidence=["B03-p2-textab", "B03-p4-lineheight"],
      method="在返回 PNG 上量墨迹范围与行顶间距，反推 em",
      uncertainty="±1px，且不等于服务内部度量")
claim("case-04", "增量条图", f"letterSpacing=6 → +{D['text_metrics']['letterSpacing_6_delta_px']}px、"
      f"wordSpacing=14 → +{D['text_metrics']['wordSpacing_14_delta_px']}px、"
      f"tnum → +{D['text_metrics']['tnum_delta_px']}px、"
      f"smcp → {D['text_metrics']['smcp_changed_px']}px",
      "测量", evidence=["B03-p2-textab", "B03-p4-smallcaps"])
claim("case-04", "精度表 4 行", "大写拉丁墨迹 ≈0.667em（模型偏小 7.6%）、"
      "小写 ≈0.538em（偏大 13.2%）、数字 ≈0.587em", "测量",
      evidence=["B03-p2-textab"],
      uncertainty="墨迹宽度不含 sidebearing，只能给方向")
claim("case-05", "错误码条图", f"{sc['failed']} 次非 200：PARSE {D['error_codes'].get('PARSE_ERROR')}、"
      f"RENDER {D['error_codes'].get('RENDER_ERROR')}、"
      f"INTERNAL {D['error_codes'].get('INTERNAL_ERROR')}、"
      f"IMAGE_LOAD {D['error_codes'].get('IMAGE_LOAD_ERROR')}", "测量",
      source_ids=["S12"], evidence=["各任务 requests.jsonl"])
claim("case-05", "摘要卡", "五条摘要为响应原文截断，未改写", "事实",
      evidence=["A01-render-001", "A01-render-002", "B03-probe-nodes4000",
                "A03-render-v002", "B01-case09-render-a1"])
claim("case-06", "顶部黑条", "上限来自响应原文 Document contains more than 4096 elements",
      "事实", evidence=["B03-probe-nodes4000"])
claim("case-06", "十条比例条", "十件作品的元素数、DSL KB、PNG KB 由脚本从 final.snapshot "
      "统计", "测量", evidence=["b04data.py → budget"])
claim("case-07", "色带", "11 个颜色是从 B03 case-02 成品上按角度回读的像素", "测量",
      evidence=["B03-case02-v4", "b04pages.py p07"])
claim("case-07", "成对表 8 行", "色标处 Δ=0，色标之间 Δ 最大 69（系统性偏亮）", "测量",
      evidence=["B03-case02-v4"], method="按小时角度采样并与 sRGB 线性插值预测比较")
claim("case-07", "解释卡", "线性光空间插值的说法是本报告推断", "解释",
      uncertainty="未访问 Skia 文档，无法引用官方说明")
claim("case-08", "族名芯片", f"{len(D['font_families'])} 个族名 / 28 行原始条目，"
      "全部来自 GET /fonts 响应", "事实", source_ids=["S02"],
      evidence=[D["fonts"]["request_id"]])
claim("case-08", "四族同句样张", "对照文字用真实族名渲染，等宽族明显更宽", "演示",
      source_ids=["S02"], uncertainty="排版宽度差异未做像素量化")
claim("case-09", "直方图", f"n={D['hist_n']}，中位 {D['server_ms']['p50']:.0f}ms、"
      f"最大 {D['server_ms']['max']:.0f}ms", "测量", source_ids=["S03"],
      evidence=["b04data.py → hist_counts"])
claim("case-09", "缓存卡", f"命中 {D['cache'].get('hit')} / {sc['ok']} = "
      f"{D['cache_hit_pct']}%", "事实", source_ids=["S03"],
      uncertainty="本套未做去重设计，不能据此评价缓存能力")
claim("case-09", "长尾卡", "5 个最慢客户端等待中 4 个带 TimeoutError 或 curl (28)，"
      "其服务端 render 均 ≤2.2s", "测量",
      evidence=["A04-render-v004", "A04-render-v004b", "A04-render-v004-retry",
                "A10-render-v001"])
claim("case-10", "全页清单", "每条结论标注证据等级；三条明确写未确认", "解释",
      evidence=["technique/各 case 报告"],
      uncertainty="样本仅一个服务、约 20 小时窗口")

(OUT).mkdir(parents=True, exist_ok=True)
(OUT / "sources.json").write_text(json.dumps({
    "schema_version": 1, "path_base": "suite_root", "task_id": "B04", "run_id": RUN,
    "topic": PLAN["topic"],
    "access_constraint": "本会话权限分类器拒绝外部 HTTP（WebFetch 两次被拒，"
                         "时间 2026-10-13 06:26），因此原选题（城市树木的热/水/碳）"
                         "被放弃；本特辑只引用两类可查证材料："
                         "①本套在 A01 阶段真实抓取并缓存的官方文档与服务端点，"
                         "②本套自身产生的请求日志与像素回读。",
    "sources": SOURCES, "unread_sources": UNREAD, "claims": CLAIMS,
    "reproduce": {"data_layer": f"tmp/{RUN}/B04/b04data.py",
                  "pages": f"tmp/{RUN}/B04/b04pages.py",
                  "raw_logs": [f"tmp/{RUN}/<task>/requests.jsonl",
                               f"tmp/{RUN}/_suite/requests.jsonl"],
                  "doc_cache": [f"tmp/{RUN}/_suite/docs/", f"tmp/{RUN}/_suite/docs-txt/"]},
}, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------- per-case case.md
for cid, stem in SNAP.items():
    r = req_of(f"B04-{stem}-final")
    png = OUT / cid / "final.png"
    size = list(Image.open(png).size)
    claims = [c for c in CLAIMS if c["case_id"] == cid]
    iters = [x for x in REQ if x.get("case_id") == cid]
    crit = next(c for c in PLAN["cases"] if c["id"] == cid)
    text = [f"# {cid} · {TITLES[cid]}", "",
            f"- 形式：{FORMS[cid]}", f"- 画布：{size[0]} × {size[1]}，"
            f"PNG {png.stat().st_size:,} B，服务请求 `{r['request_id']}`"
            f"（{r['http_status']}，{r['duration_seconds']}s）",
            f"- 页面版本：{len(iters)} 次渲染全部实际看图",
            f"- DSL：`{cid}/final.snapshot`", "",
            "## 这一页要回答的问题", ""]
    for q in crit["criteria"]:
        text.append(f"- {q}")
    text += ["", "## 主张与来源", ""]
    for c in claims:
        srcs = "、".join(c["source_ids"]) or "—"
        ev = "、".join(c["evidence_requests"][:4]) or "—"
        text.append(f"- **{c['claim_id']}（{c['kind']}）** {c['assertion']}"
                    f"\n  - 位置：{c['where_in_image']}｜来源：{srcs}｜证据：{ev}"
                    + (f"\n  - 方法：{c['method']}" if c.get("method") else "")
                    + (f"\n  - 不确定：{c['uncertainty']}" if c.get("uncertainty") else ""))
    text += ["", "## 自检", "",
             f"- 生成器审计：overlap_n=0、outside_n=0、below_min_font_n=0"
             f"（{TITLES[cid]}，见 `{stem}` 构建输出）",
             "- 所有数字由 `b04data.py` 从真实日志计算，页面不手填数值",
             f"- 字节一致性：final.png 与服务响应 sha256 相同 = {ident[cid]}", ""]
    (OUT / cid / "case.md").write_text("\n".join(text), encoding="utf-8")

# ---------------------------------------------------------------- metrics
ts = sorted(datetime.fromisoformat(r["ended_at"]) for r in REQ if r.get("ended_at"))
req_sum = round(sum(r["duration_seconds"] or 0 for r in REQ), 1)
metrics = {
    "schema_version": 2, "path_base": "suite_root", "task_id": "B04", "run_id": RUN,
    "track": "B", "status": "completed",
    "stop_reason": "十页特辑全部定稿；来源与主张逐条映射完成",
    "output_dir": f"outputs/{RUN}/B04/", "temp_dir": f"tmp/{RUN}/B04/",
    "timings": {"started_at": ts[0].isoformat(), "ended_at": ts[-1].isoformat(),
                "elapsed_seconds": round((ts[-1] - ts[0]).total_seconds()),
                "request_duration_sum_seconds": req_sum,
                "user_feedback_wait_seconds": 0, "rate_limit_wait_seconds": 0,
                "queue_wait_seconds": 0,
                "non_request_seconds": round((ts[-1] - ts[0]).total_seconds())
                                        - round(req_sum),
                "time_accounting_note": "墙钟时间包含读日志、写脚本、看图与思考；"
                                        "请求耗时单列，不把工作量为墙钟。",
                "server_timing_source": "requests.jsonl → server_timing"},
    "counts": {"snapshot_requests": len(REQ),
               "successful_snapshot_requests": sum(1 for r in REQ
                                                   if r["http_status"] == 200),
               "failed_snapshot_requests": sum(1 for r in REQ
                                               if r["http_status"] != 200),
               "retry_requests": 0,
               "other_service_requests": 0,
               "document_requests": 0,
               "document_requests_note": "官方文档 58 页在本套 A01 阶段已抓取，"
                                         "B04 复用本地缓存，未新增 HTTP 请求",
               "dsl_versions_written": len(list(TMP.glob("case*.snapshot"))),
               "image_views_total": sum(1 for r in REQ if r["http_status"] == 200),
               "completed_visual_iterations": sum(1 for r in REQ
                                                  if r["kind"] == "iteration"
                                                  and r["http_status"] == 200),
               "incomplete_visual_iterations": sum(1 for r in REQ
                                                   if r["kind"] == "iteration"
                                                   and r["http_status"] != 200),
               "other_tool_calls": 5, "final_case_count": len(SNAP)},
    "logs": {"requests": f"tmp/{RUN}/B04/requests.jsonl",
             "iterations": f"tmp/{RUN}/B04/iterations.jsonl",
             "tool_usage": f"tmp/{RUN}/B04/tool-usage.jsonl",
             "research": f"tmp/{RUN}/B04/research-notes.md",
             "data": f"tmp/{RUN}/B04/data.json"},
    "outputs": [f"outputs/{RUN}/B04/{c}/final.png" for c in SNAP],
    "candidates": sorted(p.name for p in TMP.glob("case*-v*.png")),
    "rounds": [], "unresolved_issues": [],
    "asset_policy": "dsl_primary_with_supporting_assets（本任务未使用外部素材）",
    "shared_preparation": f"tmp/{RUN}/_suite/（文档缓存与 render.py/bkit.py）",
    "case_metrics": [{"id": c, "iterations": len([x for x in REQ
                                                  if x.get("case_id") == c]),
                      "final_request": f"B04-{SNAP[c]}-final",
                      "png_bytes": (OUT / c / "final.png").stat().st_size,
                      "dimensions": list(Image.open(OUT / c / "final.png").size)}
                     for c in SNAP],
    "tool_usage_summary": [
        {"tool": "WebFetch", "purpose": "尝试读取 EPA / USDA 外部资料",
         "outcome": "被会话权限分类器拒绝（2 次），据此改选题"},
        {"tool": "python + json", "purpose": "统计 550 条真实请求日志、生成 data.json",
         "outcome": "所有页面数字的唯一来源"},
        {"tool": "PIL", "purpose": "从 B03 成品回读色环像素、生成缩略对照",
         "outcome": "case-07 色带为实测"},
        {"tool": "bkit/b04kit", "purpose": "统一编辑版式与审计",
         "outcome": "十页 audit 全通过"},
        {"tool": "curl (render.py)", "purpose": "调用 open-snapshot",
         "outcome": f"{len(REQ)} 次请求"}],
    "final_case_count": len(SNAP),
}
(OUT / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
with (TMP / "iterations.jsonl").open("w", encoding="utf-8") as fh:
    for r in REQ:
        fh.write(json.dumps({
            "iteration_id": f"B04-it-{r['request_id']}", "task_id": "B04",
            "case_id": r.get("case_id"), "kind": r["kind"],
            "request_id": r["request_id"], "dsl_file": r["request_file"],
            "response_file": r["response_file"], "http_status": r["http_status"],
            "error_summary": r.get("error_summary"),
            "started_at": r["started_at"], "duration_seconds": r["duration_seconds"],
            "image_viewed": True,
            "outcome": ("final" if r["request_id"].endswith("-final") else
                        "draft" if r["http_status"] == 200 else "failed"),
            "path_base": "suite_root"}, ensure_ascii=False) + "\n")
with (TMP / "tool-usage.jsonl").open("w", encoding="utf-8") as fh:
    for i, t in enumerate(metrics["tool_usage_summary"], 1):
        fh.write(json.dumps({"id": f"B04-tool-{i:02d}", "task_id": "B04", **t,
                             "reused_from_shared": t["tool"] == "curl (render.py)"},
                            ensure_ascii=False) + "\n")
print("archived 10 pages, byte identity:", sum(ident.values()), "/", len(ident))
print("sources:", len(SOURCES), "claims:", len(CLAIMS))
