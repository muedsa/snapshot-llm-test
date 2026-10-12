"""Build outputs/<run>/B04/sources.json from the real fetch log.

Run from the suite root:
  python tmp/<run_id>/B04/build_b04_sources.py

只有真实发出并记录在 requests.jsonl 里的抓取才算“访问过”。404／超时的页面一律标
accessed=false，绝不列为已读来源。各件引用由 final.snapshot 与 case.md 文本里实际
出现的文件名/主机名反查得到，不靠回忆。
"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
temp = root / "tmp" / rid / "B04"
out = root / "outputs" / rid / "B04"

jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
req = jl(temp / "requests.jsonl")
docs = [r for r in req if r["kind"] == "document"]
fonts = [r for r in req if r["kind"] == "fonts"]

TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
WS = re.compile(r"\s+")


def title_of(html_path):
    if not html_path or not (root / html_path).exists():
        return None
    t = TITLE.search((root / html_path).read_text(encoding="utf-8", errors="replace"))
    return WS.sub(" ", t.group(1)).strip() if t else None


# 每次 URL 的访问记录（同页重抓分别计次）
by_url = defaultdict(list)
for r in docs:
    by_url[r["url"]].append(r)


def slug(r):
    m = re.match(r"B04-doc-(.+)-\d{8}T\d{6}Z$", r["request_id"])
    return m.group(1) if m else None


def used_by(slug_, url):
    """在十件的成品 DSL 与 case.md 里实际搜这个来源名/URL。"""
    hits = []
    for i in range(1, 11):
        c = "case-%02d" % i
        texts = []
        for f in (out / c / "final.snapshot", out / c / "case.md"):
            if f.exists():
                texts.append(f.read_text(encoding="utf-8", errors="replace"))
        blob = "\n".join(texts)
        keys = [slug_, url, (url.split("//", 1)[-1] if "//" in url else url)]
        if any(k and k in blob for k in keys):
            hits.append(c)
    return hits


sources = []
for n, (url, rs) in enumerate(sorted(by_url.items(), key=lambda kv: min(x["started_at"] for x in kv[1])), 1):
    rs.sort(key=lambda x: x["started_at"])
    ok = [r for r in rs if r["http_status"] == 200]
    bad = [r for r in rs if r["http_status"] != 200]
    s = ok[0] if ok else rs[0]
    sl = slug(s)
    html_rel = None
    for r in ok:
        for key in ("response_file", "raw_html"):
            v = r.get(key)
            if v and str(v).endswith(".html") and (root / v).exists():
                html_rel = v
                break
        if html_rel:
            break
    sources.append({
        "id": "src-%02d" % n,
        "slug": sl,
        "title_in_page": title_of(html_rel),
        "url": url,
        "host": (url.split("//", 1)[1].split("/", 1)[0]) if "//" in url else None,
        "accessed": bool(ok),
        "access_count": len(rs),
        "ok_count": len(ok),
        "failed_count": len(bad),
        "first_accessed_at": rs[0]["started_at"],
        "last_accessed_at": (rs[-1]["ended_at"] or rs[-1]["started_at"]),
        "statuses": sorted({str(r["http_status"]) for r in rs}),
        "request_ids": [r["request_id"] for r in rs],
        "failure_notes": [str(r.get("error_summary"))[:160] for r in bad],
        "local_snapshot": (Path(html_rel).as_posix() if html_rel else None),
        "bytes_ok": (int(ok[0]["response_bytes"]) if ok else None),
        "used_by": used_by(sl, url),
        "how_cited": ("成品 DSL 或 case.md 中以文件名/URL 点名"
                      if used_by(sl, url) else "未见点名（仅作背景检索或抓取失败）"),
    })

# 抓取失败（404/超时）的页面单独成条，明确“不是已读来源”
failed_only = [s for s in sources if not s["accessed"]]

m = json.loads((out / "task-metrics.json").read_text(encoding="utf-8"))
meta = json.loads((temp / "research" / "meta.json").read_text(encoding="utf-8"))
inputs_per_case = meta["inputs_per_case"]

# 写出者由 grep 逐个确认（write_text/json.dump 目标路径），不是凭印象
WRITERS = {
    "catalog.json": ["b04_research.py", "parse_research.py"],
    "stats.json": ["b04_research.py", "parse_research.py"],
    "derived.json": ["derive.py"],
    "lunar.json": ["parse_lunar.py"],
    "seasons.json": ["derive_seasons.py"],
    "seasons-solar-only-v1.json": ["derive_seasons.py（v1 中间版，只含日食，留在原地不覆盖）"],
    "path-pages.json": ["parse_path.py"],
    "duration.json": ["derive_duration.py"],
    "geo.json": ["derive_geo.py"],
    "geo2.json": ["derive_geo2.py"],
    "speed.json": ["derive_speed.py"],
    "contacts.json": ["derive_contacts.py"],
    "meta.json": ["meta_stats.py"],
}
DESC = {
    "catalog.json": "224 行日食记录逐行解析（日期/类型/沙罗/月龄/γ/食分/食甚点经纬/最长时长/带宽），"
                    "解析失败的行留在 unparsed 字段里",
    "stats.json": "由 catalog.json 派生的类型计数、逐十年分布、时长与带宽极值、分箱",
    "derived.json": "本影长与触地门槛、月距余量、沙罗步长分布等可复算推算量",
    "lunar.json": "三种月份长度与 6585 天刻度（交点/近点/朔望）",
    "seasons.json": "食季窗口、季内间隔与季中心相隔（含日食与月食）",
    "seasons-solar-only-v1.json": "食季 v1（只含日食的中间版本），保留以说明口径变化",
    "path-pages.json": "两条食带（2024-04-08、2027-08-02）中央线逐点时刻与经纬、五接触时刻",
    "duration.json": "全食/环食时长分布、极值与逐分钟直方图计数",
    "geo.json": "224 个食甚点的经纬分箱与类型计数",
    "geo2.json": "中国经度带筛选、带宽盒与 |γ| 符号规则逐行核对",
    "speed.json": "两条食带逐点沿轨速度（经纬差/时刻差算弦速）与合成常数对照",
    "contacts.json": "五接触时刻、可裸眼窗口长度与占比、离轴曲线、ΔT 对照、时角互检",
    "meta.json": "件-10 的全部版面数字：共享输入关系边、自标分级计数、来源账、成品字节",
}


def users_of(fname):
    return sorted(c for c, lst in inputs_per_case.items() if fname in lst)


derived_files = []
for f in sorted(os.listdir(temp / "research")):
    if not f.endswith(".json"):
        continue
    if f == "meta-case10-frozen.json":
        continue
    derived_files.append({
        "file": "tmp/%s/B04/research/%s" % (rid, f),
        "made_by": ["tmp/%s/B04/%s" % (rid, w) for w in WRITERS.get(f, [])] or
                   ["（写出者未在本脚本中确认）"],
        "content": DESC.get(f, "（说明待补）"),
        "used_by": users_of(f) + (["case-10"] if f == "meta.json" else []),
        "note": "used_by 由 meta_stats.py 从各件生成器脚本里实际读的文件名反查得到（inputs_per_case），"
                "不是凭印象填" if f != "meta-case10-frozen.json" else "",
    })

sources_json = {

    "schema_version": 1,
    "path_base": "suite_root",
    "path_note": "本文件内所有 local_snapshot / file / log 路径均相对总任务根（suite_root），"
                 "不含盘符与用户目录；sources.json 本身位于 outputs/<run>/B04/",
    "task_id": "B04",
    "run_id": rid,
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "subject": "21 世纪日食（NASA GSFC 千年目录与逐食路径页）",
    "access_account": {
        "document_requests": m["counts"]["document_requests"],
        "distinct_urls": len(sources),
        "urls_accessed_ok": sum(1 for s in sources if s["accessed"]),
        "urls_never_read": len(failed_only),
        "http_200": m["counts"]["document_by_status"]["200"],
        "http_404": m["counts"]["document_by_status"]["404"],
        "timeout_or_transport": m["counts"]["document_by_status"]["timeout_or_transport"],
        "fonts_queries": m["counts"]["fonts_queries"],
        "counting_rule": "按 URL 逐条计：同一页重复抓取分别计次；“已读”只认 HTTP 200 的那一次，"
                         "404 与超时一律标 accessed=false 且不得列为来源",
        "log": "tmp/%s/B04/requests.jsonl" % rid,
        "html_cache_dir": "tmp/%s/B04/sources/" % rid,
    },
    "sources": sources,
    "never_read_pages": [
        {"id": s["id"], "url": s["url"], "statuses": s["statuses"],
         "reason": s["failure_notes"] or "非 200 响应，未取得正文",
         "note": "未读到正文，不作为任何一件作品的事实来源；只在件-10 的 D 区作为“失败的一半”如实列出"}
        for s in failed_only
    ],
    "per_case_source_map": {s2["id"]: s2["used_by"] for s2 in sources},
    "fonts_query": {
        "request_id": fonts[0]["request_id"] if fonts else None,
        "endpoint": fonts[0]["url"] if fonts else None,
        "purpose": "确认服务端可用水族，再决定 DSL fontFamily 写法",
        "result": "27 个字体族；正文/标题 Inter + Noto Sans SC 系，等宽数字用 Noto Sans Mono CJK SC，"
                  "引文用 Noto Serif CJK SC；实际字形由服务端渲染环境决定",
    },
    "derived_data_files": derived_files,
    "frozen_meta_for_case10": {
        "file": "tmp/%s/B04/research/meta-case10-frozen.json" % rid,
        "note": "件-10 交付时所读那份 meta.json 的原样冻结副本（10:14:22Z 落盘，DSL 上印的“快照 "
                "2026-10-11 10:05Z”即其首次扫描时刻；当时 generated_at 是脚本里手写字符串，后改为真实时钟）。"
                "本件交付后 meta.json 已增长到 http 86／渲染提交 45／迭代 46，与本副本不同属正常时差",
    },
    "demonstration_or_uncertain": [
        {"item": "件-01 的“本影尖端刚好触地”门槛带 374,805–387,328 km",
         "kind": "推算", "why": "由 fact sheet 的日/月半径与平均距离按相似三角形算出，NASA 页面未直接给出这个区间",
         "shown_as": "图上标注为推算，并列出所用常数"},
        {"item": "件-03 的三段沙罗阶梯时长与带宽",
         "kind": "来源结论 + 推算", "why": "日期/时长/带宽取自目录行；“成长—巅峰—退场”的分组命名是本辑编辑用语",
         "shown_as": "序列成员逐行给日期，可回表核对"},
        {"item": "件-05 的 ΔT 差 3.4 s",
         "kind": "已证实的差异", "why": "目录页 ΔT 74 s 与路径页 ΔT 70.6 s 是两个来源各自的原文值，不是本辑算出",
         "shown_as": "两条来路并列 + 刻度轴；未取其中其一"},
        {"item": "件-07 的沿轨速度剖面",
         "kind": "推算", "why": "由中央线逐点经纬差与时刻差算弦速，忽略测地线弯曲与高程；与手册常数合成值并列而非取代",
         "shown_as": "图上写明算法与假设"},
        {"item": "件-08 的“中国经度带 29 个／其中全食 7”",
         "kind": "推算（口径自选）", "why": "按 75°E–135°E 的经度框筛食甚点，是编辑定义的框，不是行政边界；目录经纬量化到度",
         "shown_as": "图上写明筛选框与量化精度限制"},
        {"item": "件-09 的可裸眼窗口占比",
         "kind": "已证实时刻 + 推算占比", "why": "接触时刻取路径页原文；(C3−C2)/(C5−C1) 由这些时刻相除；2021–2100 的“有几次给出窗口”受目录是否含中心线限制",
         "shown_as": "事实分层标注；目录未给接触时刻的年份如实写“未给出”"},
        {"item": "件-10 的“已证实 1／来源结论 1／推算 13／演示 0”",
         "kind": "自标覆盖率，不是真值率", "why": "统计的是各件成品 DSL 文本里自标词字符串出现次数；前八件大量使用目录原值时并未逐处打标",
         "shown_as": "B 区与已知限制里都写明这一点"},
        {"item": "本辑没有任何虚构演示数据",
         "kind": "声明", "why": "与 B01 的虚构品牌不同，B04 十件的数字全部来自抓取页面或由其派生；“演示”计数为 0 是实情而非漏标",
         "shown_as": "editorial-note.md 与件-10 F 区"},
    ],
    "attribution_rules": {
        "used_by": "对每件 final.snapshot 与 case.md 全文搜 slug／URL／路径文件名，命中才算引用；"
                   "因此件-02、件-03 出现 0 引用（早期只写“见 sources/ 目录”，没写文件名）——"
                   "这是真实的留痕缺陷，已在件-10 的 C 区标出并用 D 区整页清单补救",
        "与件-10 的口径差": "本文件的 used_by 认三种写法：doc slug（如 nasa-basics）、"
                            "完整 URL、HTML 文件名；件-10 C 区的“点名”数的是 DSL/case.md 里以 sources/、probe/、"
                            "research/ 开头的路径字符串出现次数（裸目录 “sources/” 也算一次）。"
                            "所以件-01 在这里是 0（没写过文件名）、在件-10 的表里是 1（写过裸目录），"
                            "两个数都对，只是粒度不同",
        "已证实": "页面原文直接给出的量",
        "来源结论": "页面给出的结论性说法（如“每世纪约 220–250 次”）",
        "推算": "本辑脚本由原文数据算出且写明算法",
        "演示": "编造数据（本题为 0）"
    },
    "unresolved": [
        "件-02、件-03 未点名来源文件（同上，已补救未改写历史报告）",
        "14 次抓取失败的 URL 始终未取得正文（404 10 次、超时/传输 4 次），本辑未把这些页面列为来源",
    ],
}
p = out / "sources.json"
p.write_text(json.dumps(sources_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(p.relative_to(root).as_posix(), len(sources), "urls;", len(failed_only), "never read")
print("used_by coverage:", {s["id"]: len(s["used_by"]) for s in sources if s["accessed"]})
