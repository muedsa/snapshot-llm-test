import os, json, datetime

RUN = "20261008T1615Z-run01"
ROOT = "outputs/" + RUN
SUITE = ROOT + "/_suite/"
F = json.load(open("tmp/%s/_suite/suite-facts.json" % RUN, encoding="utf-8"))
CAP_A = json.load(open("tmp/%s/_suite/captions-a.json" % RUN, encoding="utf-8"))
CAP_B = json.load(open("tmp/%s/_suite/caption-candidates.json" % RUN, encoding="utf-8"))
ORDER = F["tasks"] and [t for t in json.load(open("catalog.json", encoding="utf-8"))["task_order"]]
TASKS = F["tasks"]

B_EXTRA = {"B02/case-02/back.png": "会员卡 · 背面（与正面同批定稿，逐面各自实渲与看图）"}
CAP = {}
CAP.update(CAP_A)
for k, v in CAP_B.items():
    if k.startswith("B"):
        CAP[k] = v
CAP.update(B_EXTRA)

# ---- normalized per-task counts (documented aliases) ----
ALIAS = {
    "snapshot_requests": ["snapshot_requests", "http_requests_total", "render_submissions", "requests_total", "renders"],
    "successful_snapshot_requests": ["successful_snapshot_requests", "render_ok", "requests_success"],
    "failed_snapshot_requests": ["failed_snapshot_requests", "requests_failed", "render_transport_or_truncated"],
    "retry_requests": ["retry_requests", "retries"],
    "image_views": ["image_views", "images_viewed"],
    "completed_visual_iterations": ["completed_visual_iterations", "visual_iterations"],
    "incomplete_visual_iterations": ["incomplete_visual_iterations"],
    "dsl_versions": ["dsl_versions"],
    "document_requests": ["document_requests"],
    "other_service_requests": ["other_service_requests", "other_tool_calls", "tool_usage_records"],
}
SRC = {}


def norm(tid):
    c = TASKS[tid]["counts"]
    out = {}
    for key, names in ALIAS.items():
        for n in names:
            v = c.get(n)
            if isinstance(v, int):
                out[key] = v
                if v:
                    SRC.setdefault(key, []).append("%s:%s" % (tid, n))
                break
        out.setdefault(key, None)
    return out


N = {tid: norm(tid) for tid in ORDER}


def s(key):
    vals = [N[t][key] for t in ORDER if N[t][key] is not None]
    return sum(vals), len(vals)


def fmt(n):
    return "{:,}".format(n) if isinstance(n, int) else str(n)


# =============== gallery.md ===============
L = []
L.append("# 全套画廊 · %s（30 题 / %d 张最终图片）" % (RUN, F["totals"]["final_images"]))
L.append("")
L.append("路径基准：本文件位于 `outputs/%s/_suite/`。下面所有链接都相对本目录（`../A01/…`、`../B06/case-01/…`），"
         "复制整个 `outputs/%s/` 目录后仍可离线浏览；图片全部是本地文件，不依赖远程地址。" % (RUN, RUN))
L.append("")
L.append("- 每张最终图片给出：标题与用途、Markdown 内嵌预览、原 PNG 链接、同名完整 DSL（`.snapshot`）链接、单题/用例报告链接，"
         "以及字节数与 md5（用于验证 PNG 是服务原始响应字节、DSL 与请求体一致）。")
L.append("- 计数口径：只统计每题 `<task>/…png` 且同名 `.snapshot` 成对存在的最终图；"
         "过程版本（`vNN-preview.png`）、探针图（`probe-*.png`）、1:1/2× QA 裁图与放大图都不计入作品数，"
         "它们保留在各题输出目录与 `tmp/%s/<task>/` 下作为过程证据。" % RUN)
L.append("- A 轨（A01–A24）为纯 DSL 主体；B 轨（B01–B06）每题至少 10 件独立作品。A21/A22 的三轮、B 轨的每个开放用例都逐图列出。")
L.append("")
tot = 0
PREFERRED = {
    "A02": ["agenda-wide.png", "agenda-mobile.png"],
    "A07": ["network-map.png", "travel-card.png"],
    "A11": ["invoice-page-01.png", "invoice-page-02.png"],
    "A12": ["stage.png", "desktop.png", "tablet.png", "mobile.png"],
    "A13": ["symbol-color.png", "symbol-black.png", "brand-banner.png", "launch-poster.png"],
    "A17": ["handbook-01.png", "example-01.png", "handbook-02.png", "example-02.png",
            "handbook-03.png", "example-03.png", "handbook-04.png", "example-04.png"],
    "A19": ["grid-scene.png", "occlusion.png", "occlusion-alternative.png"],
}
for tid in ORDER:
    t = TASKS[tid]
    pref = PREFERRED.get(tid, [])
    t["images"] = sorted(t["images"], key=lambda im: (pref.index(os.path.basename(im["rel"]))
                                if os.path.basename(im["rel"]) in pref else 99, im["rel"]))
    imgs = t["images"]
    tot += len(imgs)
    L.append("## %s · %s（%d 张，题内要求 ≥%d 张）" % (tid, t["title"], len(imgs), t["minimum_final_pngs"]))
    L.append("")
    L.append("单题：[使用说明](../%s/snapshot-usage.md) · [指标](../%s/task-metrics.json)%s" % (
        tid, tid,
        " · [本题画廊](../%s/gallery.md)" % tid if "gallery.md" in t["closeout"] else ""))
    L.append("")
    for i, im in enumerate(imgs, 1):
        rel = im["rel"]
        cap = CAP.get(rel) or "%s · %s" % (t["title"], os.path.basename(rel))
        parts = rel.split("/")
        label = " · ".join(parts[1:]) if len(parts) > 1 else parts[0]
        L.append("### %s %s｜%s" % (tid, "%02d" % i, label))
        L.append("")
        L.append("**%s**" % cap)
        L.append("")
        href = "../" + rel
        L.append("![%s %s · %s](%s)" % (tid, label, cap, href))
        L.append("")
        links = "[原 PNG](%s)（%s B，md5 `%s`） · [完整 DSL](%s)（%s B，md5 `%s`）" % (
            href, fmt(im["png_bytes"]), im["png_md5"], "../" + im["snapshot"], fmt(im["snapshot_bytes"]), im["snapshot_md5"])
        report = "../%s/snapshot-usage.md" % tid
        if "/case-" in rel:
            report = "../%s/case-%s/case.md" % (tid, parts[1].split("-")[1])
        L.append("| 文件 | %s |" % links)
        L.append("| --- | --- |")
        L.append("| 画布 | %d×%d %s |" % (im["width"], im["height"], "RGBA" if im["rgba"] else "RGB"))
        L.append("| 报告 | [%s](%s) |" % (os.path.basename(report), report))
        L.append("")
    L.append("")
L.append("---")
L.append("")
L.append("## 逐图合计")
L.append("")
L.append("| 题目 | 最终图 | 题内最低 | 达标 |")
L.append("| --- | --- | --- | --- |")
for tid in ORDER:
    t = TASKS[tid]
    L.append("| %s %s | %d | %d | %s |" % (tid, t["title"], t["final_images"], t["minimum_final_pngs"],
                                           "是" if t["final_images"] >= (t["minimum_final_pngs"] or 1) else "否"))
L.append("| **合计** | **%d** | **%d** | **是** |" % (tot, sum(v for v in [TASKS[t]["minimum_final_pngs"] for t in ORDER] if v)))
L.append("")
assert tot == F["totals"]["final_images"]

open(SUITE + "gallery.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("gallery.md lines", len(L), "images", tot)
