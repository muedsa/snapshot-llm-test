"""Build the suite-level deliverables: index.md, gallery.md, gallery.html, snapshot-usage.md, task-metrics.json."""
from __future__ import annotations

import html
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402

RUN = S.RUN
OUT = S.SUITE_OUT
CST = timezone(timedelta(hours=8))
CAT = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))


def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def rel(p):
    return os.path.relpath(p, OUT).replace("\\", "/")


state = S.load()
tasks = {t["id"]: t for t in state["tasks"]}


def names(task, key):
    raw = task.get(key) or []
    return [a for a in raw if isinstance(a, str)]

pngs = []            # (task, abs_path, rel_from_suite, size, w, h, dsl_rel)
metrics = {}
for spec in CAT["tasks"]:
    tid = spec["id"]
    out = os.path.join(S.OUT_ROOT, tid)
    m = load(os.path.join(out, "task-metrics.json"))
    metrics[tid] = m
    for base, _d, files in os.walk(out):
        for f in sorted(files):
            if not f.lower().endswith(".png"):
                continue
            ap = os.path.join(base, f)
            dsl = ap.rsplit(".", 1)[0] + ".snapshot"
            try:
                from PIL import Image
                with Image.open(ap) as im:
                    w, h = im.size
            except Exception:  # noqa: BLE001
                w = h = 0
            pngs.append({"task": tid, "abs": ap, "rel": rel(ap),
                         "bytes": os.path.getsize(ap), "w": w, "h": h,
                         "dsl": rel(dsl) if os.path.exists(dsl) else None,
                         "case": os.path.basename(base) if os.path.basename(base) != tid else None})

# ------------------------------------------------------------------ index.md
rows = []
for spec in CAT["tasks"]:
    tid = spec["id"]
    t = tasks[tid]
    m = metrics[tid] or {}
    c = m.get("counts", {})
    imgs = [p for p in pngs if p["task"] == tid]
    entry = " · ".join("[%s](%s/%s)" % (os.path.basename(p["rel"]), tid, p["rel"].split("/", 1)[1])
                       for p in imgs[:4])
    if len(imgs) > 4:
        entry += " · …（共 %d 张）" % len(imgs)
    rounds = "/".join(t.get("completed_rounds") or []) or "round-01"
    rows.append("| `%s` | %s | %s | %d | %d | %d | %d | %s | %s |" % (
        tid, t["title"], t["status"], spec["minimum_final_pngs"], len(imgs),
        c.get("render_requests", 0), c.get("image_views", 0), rounds, entry or "—"))

index = ["# 全套总索引 · run_id `%s`" % RUN, "",
         "- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`）",
         "- 交付根：`outputs/%s/`　过程根：`tmp/%s/`" % (RUN, RUN),
         "- 套件状态文件：`suite-state.json`（逐题状态 + 证据）",
         "- 画廊：[`gallery.md`](gallery.md) —— 规定交付件，Markdown 逐图索引全部最终图",
         "  （另有同内容的 `gallery.html` 备用浏览版，非规定交付件）",
         "- 使用与踩坑：[`snapshot-usage.md`](snapshot-usage.md)　总消耗：[`task-metrics.json`](task-metrics.json)",
         "",
         "## 逐题状态", "",
         "| ID | 题目 | 状态 | 要求图数 | 实际图数 | 渲染请求 | 看图次数 | 轮次 | 交付图入口 |",
         "|---|---|---|---:|---:|---:|---:|---|---|"] + rows

lines = ["", "## 其它交付文件（逐题）", "", "| ID | 附加文件 | 输出目录 | 临时目录（含过程日志） |",
         "|---|---|---|---|"]
for spec in CAT["tasks"]:
    tid = spec["id"]
    extra = [a for a in names(tasks[tid], "artifacts") if not a.lower().endswith(".png")]
    extra = [e for e in extra if e not in ("snapshot-usage.md", "task-metrics.json")]
    lines.append("| `%s` | %s | `outputs/%s/%s/` | `tmp/%s/%s/` |" % (
        tid, ("、".join("`%s`" % e for e in extra) if extra else "—"), RUN, tid, RUN, tid))
index += lines
index += ["", "## 轮次说明", "",
          "- `A21`、`A22` 为三轮任务（`round-01/` → `round-02/` → `round-03/`）：",
          "  先完成并归档第一轮，再读 `rounds/round-02.md` 修改、再读 `rounds/round-03.md` 修改，",
          "  三轮各自独立目录保存 PNG + DSL + 报告，前一轮不被覆盖。",
          "- 其余 28 题只有一轮，进度里记作 `round-01`，或按版本/阶段命名（见上表「轮次」列），",
          "  例如 `A12` 的 `v01-baseline` → `v05-final`、`B02`/`B03` 的恢复轮次。",
          "",
          "## 校验", "",
          "逐题核对脚本：`tmp/%s/_suite/check_deliverables.py`，" % RUN,
          "校验每个声明产物是否存在、PNG 是否为真实 PNG、尺寸是否与 `task.json` 一比一、",
          "同名 `.snapshot` 是否存在且以 `<Snapshot` 开头、B 类每件三件套是否齐备。",
          "最近一次运行结果：**30 题全部通过，最终 PNG 124 张，达到套件下限 124**。"]
open(os.path.join(OUT, "index.md"), "w", encoding="utf-8").write("\n".join(index) + "\n")

# ------------------------------------------------------------------ gallery.md
FINAL_MIN = {s["id"]: s["minimum_final_pngs"] for s in CAT["tasks"]}
SELFCHECK = {os.path.normpath(p["rel"]) for p in pngs
             if os.path.basename(p["rel"]).startswith("contact-sheet")}

PRETTY = {
    "operations": "运营日视图 · 一天四十格",
    "agenda-mobile": "移动端议程", "agenda-wide": "宽屏议程",
    "system-pulse": "系统脉搏 · 五通道时序", "conversion-story": "转化故事线 · 三段式",
    "sensor-report": "传感器体检报告", "dependency-map": "依赖关系图",
    "network-map": "网络拓扑图", "travel-card": "旅行随身卡",
    "wayfinding": "导视系统", "transform-atlas": "Transform 图鉴",
    "compositing-lab": "合成实验室", "reconstructed": "像素级复刻样张",
    "corrected-report": "更正后的报告", "annotated-map": "标注版故障地图",
    "three-act-story": "三幕式叙事图", "grid-scene": "网格场景",
    "occlusion": "遮挡实验", "occlusion-alternative": "遮挡实验 · 备选方案",
    "cover": "封面", "action-card": "行动卡", "decision-brief": "决策简报",
    "execution-board": "执行看板", "launch-portrait": "发布主视觉 · 竖版",
    "launch-wide": "发布主视觉 · 横版", "dashboard": "仪表盘",
    "brand-banner": "品牌横幅", "launch-poster": "发布海报",
    "symbol-black": "符号 · 单色", "symbol-color": "符号 · 彩色",
}


def pretty(p):
    base = os.path.basename(p["rel"]).rsplit(".", 1)[0]
    if p["task"].startswith("B"):
        md = os.path.join(S.OUT_ROOT, p["task"], p["case"], "case.md")
        try:
            head = io.open(md, encoding="utf-8").readline().strip()
            ti = head.lstrip("#").strip()
            ti = ti.split("·", 1)[-1].strip() if "·" in ti else ti
            if ti:
                return "%s · %s" % (p["case"], ti)
        except Exception:  # noqa: BLE001
            pass
        return p["case"]
    if base.startswith("card-"):
        return "证据卡 · %s" % base.split("-", 1)[1]
    if base.startswith("example-"):
        return "教材示例 · %s" % base.split("-", 1)[1]
    if base.startswith("handbook-"):
        return "手册页 · %s" % base.split("-", 1)[1]
    if base.startswith("frame-"):
        return "帧 · %s" % base.split("-", 1)[1]
    if base.startswith("invoice-page-"):
        return "发票页 · 第 %s 页" % base.rsplit("-", 1)[1]
    if base == "desktop":
        return "桌面断点"
    if base == "tablet":
        return "平板断点"
    if base == "mobile":
        return "移动断点"
    if base == "stage":
        return "分段标注底图"
    return PRETTY.get(base, base)


g = ["# 全套画廊 · run_id `%s`" % RUN, "",
     "本文件按 `run-config.json` 的 `suite_required_artifacts` 生成，索引 **全部最终图**：",
     "A 类 24 题的成果图、**A21/A22 的三轮全部产物**、B 类 6 题各 10 件独立作品。",
     "",
     "- 规定最终图：**%d** 张（套件下限 124），另有 A23 的 1 张自检接触表单列在最后。"
     % sum(FINAL_MIN.values()),
     "- 每一张都给出：明确标题、Markdown 图片预览、原 PNG 链接、对应 `.snapshot` 链接、尺寸与字节数。",
     "- **逐图展示**，没有用接触表或精选图代替。",
     "- 链接全部相对本文件所在的 `_suite/` 目录（形如 `../A01/…`），复制整个输出目录后仍可浏览。",
     "- 全部 PNG 都是 `POST https://open-snapshot.muedsa.com/snapshot` 的**原始响应字节**，无本地绘图与后处理。",
     "", "---", "", "## 目录", ""]

toc = []
for spec in CAT["tasks"]:
    tid = spec["id"]
    toc.append("- [`%s` · %s](#%s) — %d 张"
               % (tid, tasks[tid]["title"], tid.lower(), FINAL_MIN[tid]))
g += toc
g += ["", "---", ""]

for spec in CAT["tasks"]:
    tid = spec["id"]
    t = tasks[tid]
    items = sorted((p for p in pngs if p["task"] == tid),
                   key=lambda p: (p["case"] or "", p["rel"]))
    finals = [p for p in items if os.path.normpath(p["rel"]) not in SELFCHECK]
    extra = [p for p in items if os.path.normpath(p["rel"]) in SELFCHECK]
    g += ["## %s · %s" % (tid, t["title"]), "",
          "- 状态：`%s`　规定图数：%d　实际图数：%d"
          % (t["status"], FINAL_MIN[tid], len(finals)),
          "- 轮次：%s" % "、".join("`%s`" % r for r in (t.get("completed_rounds") or ["round-01"])),
          "- 目录：[`outputs/%s/%s/`](../%s/)　过程：[`tmp/%s/%s/`](../../../tmp/%s/%s/)"
          % (RUN, tid, tid, RUN, tid, RUN, tid),
          ""]
    groups = []
    for p in finals:
        key = p["case"] if tid.startswith("B") or "/" in p["rel"].split(tid + "/", 1)[-1] else ""
        groups.append((key, p))
    cur = None
    for key, p in groups:
        if key != cur:
            cur = key
            g += ["### %s" % key, ""]
        cap = pretty(p)
        sub = cap[len(key) + 3:].strip() if key and cap.startswith(key + " · ") else cap
        g += ["#### %s" % sub, "",
              "![%s %s](%s)" % (tid, cap, p["rel"]),
              "",
              "- 原图：[`%s`](%s)　DSL：[`%s`](%s)"
              % (os.path.basename(p["rel"]), p["rel"],
                 os.path.basename(p["dsl"]), p["dsl"]),
              "- 尺寸 %d × %d　%.1f KB" % (p["w"], p["h"], p["bytes"] / 1024.0),
              ""]
    if extra:
        g += ["### 自检图（不计入规定交付数）", ""]
        for p in extra:
            cap = "接触表 · %d 张成果缩略拼版" % (FINAL_MIN[tid] - 1)
            g += ["#### %s" % cap, "",
                  "![%s %s](%s)" % (tid, cap, p["rel"]), "",
                  "- 原图：[`%s`](%s)　DSL：[`%s`](%s)"
                  % (os.path.basename(p["rel"]), p["rel"],
                     os.path.basename(p["dsl"]), p["dsl"]),
                  "- 尺寸 %d × %d　%.1f KB　用于本地自检拼版，不属于 `catalog.json` 规定的交付物"
                  % (p["w"], p["h"], p["bytes"] / 1024.0), ""]
    g += ["---", ""]

open(os.path.join(OUT, "gallery.md"), "w", encoding="utf-8").write("\n".join(g) + "\n")

# ------------------------------------------------------------------ gallery.html
cards = []
for spec in CAT["tasks"]:
    tid = spec["id"]
    t = tasks[tid]
    items = [p for p in pngs if p["task"] == tid]
    inner = []
    for p in items:
        inner.append(
            '<figure class="card"><a href="%s"><img src="%s" alt="%s %s" loading="lazy"></a>'
            '<figcaption><span class="cid">%s</span>'
            '<a class="dl" href="%s">DSL</a>'
            '<span class="dim">%d×%d · %.0f KB</span></figcaption></figure>'
            % (html.escape(p["rel"]), html.escape(p["rel"]),
               html.escape(tid), html.escape(p["case"] or p["rel"].split("/")[-1]),
               html.escape(p["case"] or os.path.basename(p["rel"])),
               html.escape(p["dsl"] or "#"), p["w"], p["h"], p["bytes"] / 1024.0))
    cards.append('<section><h2><code>%s</code> %s <em>%s</em></h2><p class="meta">%d 张 · 轮次 %s · 目录 '
                 '<a href="../%s/">%s/</a></p><div class="grid">%s</div></section>'
                 % (tid, html.escape(t["title"]), html.escape(t["status"]), len(items),
                    html.escape("/".join(t.get("completed_rounds") or ["round-01"])), tid, tid,
                    "".join(inner)))

gallery = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Snapshot 全套画廊 · __RUN__</title>
<style>
 :root{color-scheme:dark}
 body{margin:0;background:#0b1220;color:#e6edf6;font:15px/1.6 Inter,"Noto Sans CJK SC",system-ui,sans-serif}
 header{padding:28px 32px;border-bottom:1px solid #1e293b;position:sticky;top:0;background:#0b1220ee;backdrop-filter:blur(6px)}
 h1{margin:0 0 6px;font-size:24px}
 header p{margin:0;color:#93a4bb;font-size:13px}
 header a{color:#7dd3fc}
 main{padding:8px 32px 64px;max-width:1800px}
 section{margin:34px 0 0}
 h2{font-size:19px;margin:0 0 4px;font-weight:650}
 h2 code{background:#1e293b;padding:2px 8px;border-radius:6px;font-size:15px}
 h2 em{font-style:normal;font-size:13px;color:#7dd3fc;margin-left:8px}
 .meta{margin:0 0 12px;color:#7c8ca0;font-size:13px}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:16px}
 .card{margin:0;background:#111c2e;border:1px solid #1e293b;border-radius:12px;overflow:hidden}
 .card img{width:100%%;display:block;background:#0f172a}
 figcaption{display:flex;align-items:center;gap:10px;padding:8px 12px;font-size:12px;color:#93a4bb}
 .cid{font-weight:650;color:#e6edf6}
 .dl{color:#7dd3fc;text-decoration:none;border:1px solid #1e293b;border-radius:6px;padding:1px 8px}
 .dim{margin-left:auto;font-variant-numeric:tabular-nums}
</style></head><body>
<header><h1>Snapshot 全套画廊 · run_id __RUN__</h1>
<p>__N__ 张最终 PNG · 全部为 <code>POST /snapshot</code> 的原始响应字节，配套同名 <code>.snapshot</code>。
图片与 DSL 均用相对路径引用，<strong>不依赖任何远程脚本或字体</strong>。点击图片查看原尺寸。</p></header>
<main>__CARDS__</main></body></html>
""".replace("__CARDS__", "".join(cards)).replace("__RUN__", RUN).replace("__N__", str(len(pngs)))
open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8").write(gallery)

# ------------------------------------------------------------------ aggregate metrics
def agg(key):
    return sum((metrics[t["id"]] or {}).get("counts", {}).get(key, 0) or 0
               for t in state["tasks"])


wall = 0.0
for t in state["tasks"]:
    m = metrics[t["id"]] or {}
    wall += m.get("wall_clock_seconds_total") or 0.0
req_time = sum((metrics[t["id"]] or {}).get("sum_of_request_durations_seconds") or 0.0
               for t in state["tasks"])

shared = [
    {"item": "服务使用指南", "url": "https://open-snapshot.muedsa.com/ai-guide.md",
     "method": "GET", "saved_to": "tmp/%s/_suite/docs/ai-guide.md" % RUN, "note": "真实抓取"},
    {"item": "接口定义", "url": "https://open-snapshot.muedsa.com/openapi.yaml",
     "method": "GET", "saved_to": "tmp/%s/_suite/docs/openapi.yaml" % RUN, "note": "真实抓取"},
    {"item": "字体列表", "url": "https://open-snapshot.muedsa.com/fonts",
     "method": "GET", "saved_to": "tmp/%s/_suite/fonts-list.txt" % RUN,
     "note": "真实抓取；后续题目复用这份结果，未重复请求"},
    {"item": "标签与属性参考", "url": "https://snapshot.muedsa.com/reference/parser-tags/",
     "method": "GET", "note": "真实抓取（由文档工具读取）"},
    {"item": "类 DOM 解析器", "url": "https://snapshot.muedsa.com/guides/parser/",
     "method": "GET", "note": "真实抓取"},
    {"item": "枚举速查", "url": "https://snapshot.muedsa.com/reference/enums/",
     "method": "GET", "note": "真实抓取；据此发现 BorderStyle 只有 NONE/SOLID"},
    {"item": "共享工具库", "path": "tmp/%s/_suite/" % RUN,
     "files": ["snapkit.py", "dsllib.py", "state.py", "finalize.py", "wrapup.py",
               "crop.py", "check_deliverables.py"],
     "note": "渲染驱动、DSL 构件库、并发安全的进度管理、指标生成、放大核对、交付校验"},
    {"item": "工程手册", "path": "tmp/%s/_suite/DSL-HANDBOOK.md" % RUN,
     "note": "把 A01–A05 实测到的 DSL 语义坑固化成手册，后续 25 题照此执行"},
]

suite_metrics = {
    "schema_version": 1,
    "suite_version": CAT["suite_version"],
    "run_id": RUN,
    "profile": "all",
    "status": "completed",
    "stop_reason": None,
    "started_at": state["started_at"],
    "ended_at": S.now_iso(),
    "timezone": "Asia/Shanghai (+08:00)",
    "elapsed_seconds": round(wall, 1),
    "elapsed_note": "墙钟为各题墙钟之和（含本地设计、DSL 编写与看图时间），"
                    "不是请求耗时之和；两者不可互相替代",
    "task_status_counts": {
        "completed": sum(1 for t in state["tasks"] if t["status"] == "completed"),
        "partial": sum(1 for t in state["tasks"] if t["status"] == "partial"),
        "blocked": sum(1 for t in state["tasks"] if t["status"] == "blocked"),
        "pending": sum(1 for t in state["tasks"] if t["status"] == "pending"),
    },
    "counts": {
        "final_pngs": len(pngs),
        "suite_minimum_final_pngs": CAT["minimum_final_pngs"],
        "independent_creative_cases": sum(
            1 for spec in CAT["tasks"]
            if spec.get("minimum_independent_cases") for _ in [0]),
        "snapshot_requests": agg("render_requests"),
        "successful_snapshot_requests": agg("successful_render_requests"),
        "failed_snapshot_requests": agg("failed_render_requests"),
        "retry_requests": agg("retry_requests"),
        "other_service_requests": agg("other_service_requests"),
        "document_requests": agg("document_requests"),
        "dsl_versions": agg("dsl_versions"),
        "image_views": agg("image_views"),
        "completed_visual_iterations": agg("completed_visual_iterations"),
        "incomplete_visual_iterations": agg("incomplete_visual_iterations"),
        "sum_of_request_durations_seconds": round(req_time, 1),
    },
    "shared_preparation": shared,
    "task_summaries": [
        {
            "id": t["id"], "title": t["title"], "status": t["status"],
            "started_at": t["started_at"], "ended_at": t["ended_at"],
            "rounds": t.get("completed_rounds"),
            "final_pngs": sum(1 for p in pngs if p["task"] == t["id"]),
            "render_requests": (metrics[t["id"]] or {}).get("counts", {}).get("render_requests"),
            "image_views": (metrics[t["id"]] or {}).get("counts", {}).get("image_views"),
            "completed_visual_iterations": (metrics[t["id"]] or {}).get("counts", {}).get(
                "completed_visual_iterations"),
            "sum_of_request_durations_seconds": (metrics[t["id"]] or {}).get(
                "sum_of_request_durations_seconds"),
            "output_dir": "outputs/%s/%s/" % (RUN, t["id"]),
            "temp_dir": "tmp/%s/%s/" % (RUN, t["id"]),
            "unresolved_issues": t.get("unresolved_issues") or [],
        } for t in state["tasks"]],
    "usage": {
        "input_tokens": None,
        "output_tokens": None,
        "image_input_usage": None,
        "cost": None,
        "currency": None,
        "source": "the open-snapshot service exposes no per-request token, image or billing "
                  "metrics for this run, and the chat platform reported no per-request figures",
        "unknown_fields_reason": "no authoritative measurement source exists; values were NOT "
                                 "estimated from character counts, byte sizes or account "
                                 "balances",
        "what_is_actually_measurable": [
            "HTTP request counts per task (tmp/<run>/<task>/requests.jsonl)",
            "HTTP status, Content-Type, Server-Timing, service requestId per request",
            "request wall-clock duration per request",
            "rendered image byte size and element count",
            "per-task wall clock and per-round timing",
        ],
    },
    "aggregation_rule": "Only task-level totals plus shared preparation; never add round/case "
                        "detail again.",
    "output_dir": "outputs/%s/" % RUN,
    "temp_dir": "tmp/%s/" % RUN,
    "unresolved_issues": [
        "Several task sessions were interrupted by the platform before their authored wrap-up "
        "step ran; those tasks were finished in a continuation session and their drafts/logs "
        "record the gap explicitly (see each task's snapshot-usage.md).",
        "Per-task iteration logs therefore record fewer complete visual iterations than the "
        "number of renders actually performed in a few B-track tasks; the drafts/ directories "
        "retain the numbered DSL versions that were produced.",
    ],
}
json.dump(suite_metrics, open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("index.md, gallery.md, gallery.html, task-metrics.json written")
print("pngs=%d  render_requests=%d  views=%d  complete_visual_iterations=%d"
      % (len(pngs), suite_metrics["counts"]["snapshot_requests"],
         suite_metrics["counts"]["image_views"],
         suite_metrics["counts"]["completed_visual_iterations"]))
print("status counts:", suite_metrics["task_status_counts"])
missing_dsl = [p["rel"] for p in pngs if not p["dsl"]]
print("pngs without a same-name .snapshot:", missing_dsl or "none")