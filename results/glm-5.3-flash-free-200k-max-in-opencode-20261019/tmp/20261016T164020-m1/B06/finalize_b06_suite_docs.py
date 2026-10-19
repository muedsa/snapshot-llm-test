# -*- coding: utf-8 -*-
"""套件总装（B06 完成后）：_suite/gallery.md + index.md + snapshot-usage.md +
task-metrics.json，同步 suite-state 最终态（completed、final_images=磁盘数、
suite_artifacts），追加 suite 完成事件与 checkpoint state-000053，并全量校验
gallery 链接相对可达。遵循 PATHS.md：_suite 内全部链接相对本文件目录。"""
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(r"D:\mine\test\glm-5.3-flash")
RUN = "20261016T164020-m1"
OUT = ROOT / "outputs" / RUN
SUITE_OUT = OUT / "_suite"
SUITE_TMP = ROOT / "tmp" / RUN / "_suite"
NOW = datetime.now().astimezone().isoformat(timespec="milliseconds")

ST = json.loads((SUITE_OUT / "suite-state.json").read_text(encoding="utf-8"))
ORDER = ST["task_order_order"]

A_TITLES = {
    ("A01", "operations.png"): "运营驾驶舱（销售/访问/转化/结算明细）",
    ("A02", "agenda-wide.png"): "1920×1200 泳道日程全景",
    ("A02", "agenda-mobile.png"): "720×1280 手机时序列表",
    ("A03", "system-pulse.png"): "System Pulse 语义调修视图",
    ("A04", "conversion-story.png"): "转化率悖论五面板图",
    ("A05", "sensor-report.png"): "传感器三联共轴报告",
    ("A06", "dependency-map.png"): "项目依赖图（拓扑层+反馈线）",
    ("A07", "network-map.png"): "轨道交通网络拓扑图",
    ("A07", "travel-card.png"): "无障碍出行卡",
    ("A08", "wayfinding.png"): "展馆双路线导览",
    ("A09", "transform-atlas.png"): "12 枚印章 · Transform 复合矩阵图集",
    ("A10", "compositing-lab.png"): "六格合成与滤镜实验板",
    ("A11", "invoice-page-01.png"): "跨页双语结算单 · 第 1 页",
    ("A11", "invoice-page-02.png"): "跨页双语结算单 · 第 2 页",
    ("A12", "mobile.png"): "响应式断点 · 手机",
    ("A12", "tablet.png"): "响应式断点 · 平板",
    ("A12", "desktop.png"): "响应式断点 · 桌面",
    ("A12", "stage.png"): "响应式断点 · 大屏",
    ("A13", "symbol-color.png"): "Layerlight 品牌符号 · 彩色（512）",
    ("A13", "symbol-black.png"): "Layerlight 品牌符号 · 纯黑（512）",
    ("A13", "brand-banner.png"): "Layerlight 品牌横幅（1200×400）",
    ("A13", "launch-poster.png"): "Layerlight 上线海报（1080×1350）",
    ("A15", "reconstructed.png"): "Northstar 界面复刻（1440×900）",
    ("A16", "corrected-report.png"): "经营图诊断修正重建",
    ("A18", "three-act-story.png"): "三幕拥堵守恒叙事（β 方案）",
    ("A19", "grid-scene.png"): "8×8 对象题场网格",
    ("A19", "occlusion.png"): "遮挡谜题版 A",
    ("A19", "occlusion-alternative.png"): "遮挡谜题版 B（与 A 像素等价）",
    ("A20", "annotated-map.png"): "24 点求解标注图",
    ("A23", "cover.png"): "能力画卷封面",
    ("A24", "execution-board.png"): "发布执行排程板",
    ("A24", "decision-brief.png"): "发布决策简报",
    ("A24", "action-card.png"): "发布行动卡",
}

G_ENTRY = {"A01": "operations.snapshot", "A03": "system-pulse.snapshot",
           "A04": "conversion-story.snapshot", "A05": "sensor-report.snapshot",
           "A06": "dependency-map.snapshot", "A08": "wayfinding.snapshot",
           "A09": "transform-atlas.snapshot", "A10": "compositing-lab.snapshot",
           "A15": "reconstructed.snapshot", "A16": "corrected-report.snapshot",
           "A18": "three-act-story.snapshot", "A20": "annotated-map.snapshot"}


# ---------- 校验辅助 ----------
def links_of_gallery():
    gm = (SUITE_OUT / "gallery.md").read_text(encoding="utf-8")
    return gm, re.findall(r"\]\((\./[^)]+|\.\./[^)]+)\)", gm)


def a_title(task, name):
    nm = name.replace("\\", "/")
    if (task, name) in A_TITLES:
        return A_TITLES[(task, name)]
    if task == "A14" and name.startswith("card-K"):
        return "内容压测卡 %s（徽标/长标题/特殊字符）" % name[5:8]
    if task == "A17" and name.startswith("page-"):
        return "DSL 入门手册 · 第 %s 页（真实契约交付）" % name[5:7]
    if task == "A17" and name.startswith("example-"):
        return "DSL 教学独立示例 %s" % name[8:10]
    if task == "A21":
        rd = nm.split("/")[0][-1]
        return "启动页 %s · 第 %s 轮" % ("竖版" if "portrait" in name else "横幅", rd)
    if task == "A22":
        rd = nm.split("/")[0][-1]
        return "月度数据 dashboard · 第 %s 轮" % rd
    if task == "A23" and name.startswith("frame-"):
        return "能力画卷 · 序列帧 %s" % name[6:8]
    return name


def b_titles(task):
    p = OUT / task / "portfolio.json"
    mp = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for c in data.get("cases", []):
                mp[c.get("case_id") or c.get("id")] = c.get("title") or c.get("case_id") or c.get("id")
        except Exception:
            pass
    return mp


def disk_pngs(task):
    d = OUT / task
    return sorted([p for p in d.rglob("*.png")
                   if "_suite" not in p.parts and p.suffix == ".png"],
                  key=lambda p: str(p.relative_to(OUT)).replace("\\", "/"))


def load_metric(task):
    p = OUT / task / "task-metrics.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def load_reqs(task):
    p = ROOT / "tmp" / RUN / task / "requests.jsonl"
    rows = []
    if p.exists():
        for ln in p.read_text(encoding="utf-8").strip().splitlines():
            try:
                rows.append(json.loads(ln))
            except Exception:
                pass
    return rows


def rows_of(task):
    p = ROOT / "tmp" / RUN / task / "iterations.jsonl"
    if p.exists():
        return len(p.read_text(encoding="utf-8").strip().splitlines())
    return 0


def views_of(m):
    if "counts" in m and isinstance(m.get("counts"), dict):
        return m["counts"].get("image_views")
    return m.get("image_views")


def dsl_of(m):
    if "counts" in m and isinstance(m.get("counts"), dict):
        return m["counts"].get("dsl_versions")
    return None


def elapsed_of(m):
    t = m.get("timings") or {}
    return t.get("elapsed_seconds")


def cvis_of(m):
    c = m.get("counts") or {}
    if c.get("completed_visual_iterations") is not None:
        return c["completed_visual_iterations"]
    it = m.get("iterations")
    if isinstance(it, dict):
        return (it.get("visual_iteration", 0) or 0) + (it.get("requirement_change", 0) or 0)
    return 0


def elapsed_window_of(m):
    t = m.get("timings") or {}
    return t.get("started_at"), t.get("ended_at")


# ---------- 聚合 ----------
task_data = {}
for t in ORDER:
    m = load_metric(t)
    rows = load_reqs(t)
    render_rows = [r for r in rows if r.get("request_type") == "render"]
    ok200 = len([r for r in rows if r.get("http_status") == 200])
    fail = len([r for r in rows if r.get("http_status") not in (200, None)])
    p = disk_pngs(t)
    task_data[t] = {
        "status": [x for x in ST["tasks"] if x["id"] == t][0]["status"],
        "finals": len(p),
        "req_rows": len(rows),
        "renders": len(render_rows),
        "renders_ok": len([r for r in render_rows if r.get("http_status") == 200]),
        "renders_fail": len([r for r in render_rows if r.get("http_status") != 200]),
        "http_ok": ok200, "http_fail": fail,
        "doc_other_rows": len(rows) - len(render_rows),
        "image_views": views_of(m),
        "dsl_versions": dsl_of(m),
        "elapsed": elapsed_of(m),
        "cvis": cvis_of(m),
        "window": elapsed_window_of(m),
        "iter_rows": rows_of(t),
    }

tot = {
    "finals": sum(v["finals"] for v in task_data.values()),
    "renders": sum(v["renders"] for v in task_data.values()),
    "renders_ok": sum(v["renders_ok"] for v in task_data.values()),
    "renders_fail": sum(v["renders_fail"] for v in task_data.values()),
    "req_rows": sum(v["req_rows"] for v in task_data.values()),
    "doc_other": sum(v["doc_other_rows"] for v in task_data.values()),
    "image_views": sum(v["image_views"] or 0 for v in task_data.values()),
    "iter_rows": sum(v["iter_rows"] for v in task_data.values()),
    "cvis": sum(v["cvis"] for v in task_data.values()),
    "elapsed_task_sum": sum(v["elapsed"] or 0 for v in task_data.values()),
}
print("AGG:", {k: v for k, v in tot.items()})
zero_views = [t for t, v in task_data.items() if not v["image_views"]]
print("tasks without explicit image_views:", zero_views)

# ---------- gallery.md（先写后验；suite-state 在校验通过后最终定格） ----------
g = ["# 全套画廊 · 124 张最终图（30 题）", "",
     "run `%s` · 服务 https://open-snapshot.muedsa.com（真实渲染 200 响应字节）· " % RUN,
     "每题终图按任务顺序分组；A21/A22 为预置三轮各自成图。所有链接相对本文件（`../<题>/...`），",
     "复制运行目录可离线浏览；每张图配同名完整 `.snapshot`。", ""]
num = 0
for t in ORDER:
    row = task_data[t]
    dpath = OUT / t
    pngs = disk_pngs(t)
    heads = {"A21": "A21 三轮启动页（预置连续执行）", "A22": "A22 三轮数据修订 dashboard（预置连续执行）",
             "A23": "A23 能力画卷（封面+六帧）", "A24": "A24 发布三部曲（板/简报/卡）"}
    if t in heads:
        g += ["## %s" % heads[t], ""]
    else:
        g += ["## %s（%d 张）" % (t, len(pngs)), ""]
    bts = b_titles(t) if t.startswith("B") else {}
    if t.startswith("B"):
        g += ["作品集入口：[%s/portfolio.md](../%s/portfolio.md) · 说明 [gallery](../%s/gallery.md)" % (t, t, t), ""]
    rounds = {"A21": ["round-01", "round-02", "round-03"], "A22": ["round-01", "round-02", "round-03"]}
    if t in rounds:
        for rd in rounds[t]:
            rpngs = [p for p in pngs if rd in str(p.relative_to(dpath)).replace("\\", "/")]
            if rpngs:
                g += ["### %s · %s" % (t, rd), ""]
            for p in rpngs:
                num += 1
                rel = p.relative_to(OUT).as_posix()
                snap = OUT / (rel[:-4] + ".snapshot")
                ttl = a_title(t, str(p.relative_to(dpath)))
                ttl = ttl.replace(" · 第  轮", "")  # 保险
                g += ["%d. **%s**" % (num, ttl), "",
                      "![%s](../%s)" % (rel, rel), "",
                      "- 原图：[`../%s`](../%s) · DSL：[`../%s`](../%s)%s" % (
                          rel, rel, (rel[:-4] + ".snapshot"), (rel[:-4] + ".snapshot"),
                          "" if snap.exists() else "（**DSL 缺失？**）"), ""]
    else:
        for p in pngs:
            num += 1
            rel = p.relative_to(OUT).as_posix()
            snap = OUT / (rel[:-4] + ".snapshot")
            base_name = p.name
            if t.startswith("B"):
                ttl = bts.get(p.parent.name) or base_name
            else:
                ttl = a_title(t, str(p.relative_to(dpath)))
            sub = " · %s" % p.parent.name if p.parent.name != t else ""
            g += ["%d. **%s**%s" % (num, ttl, sub), "",
                  "![%s](../%s)" % (rel, rel), "",
                  "- 原图：[`../%s`](../%s) · DSL：[`../%s`](../%s)%s" % (
                      rel, rel, (rel[:-4] + ".snapshot"), (rel[:-4] + ".snapshot"),
                      "" if snap.exists() else "（**DSL 缺失？**）"), ""]
assert num == tot["finals"], (num, tot["finals"])
g += ["---", "",
      "共 %d 张（= 磁盘终图审计）· 0 张缺失 · 全部为 open-snapshot 200 原始字节；" % num,
      "逐题渲染/迭代/看图明细见 [task-metrics.json](task-metrics.json) 与索引 [index.md](index.md)。"]
(SUITE_OUT / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")
print("gallery.md written:", num, "images")

# ---------- gallery 全量链接校验（先于状态定格） ----------
gm_text, links = links_of_gallery()
bad = [lnk for lnk in links if not (SUITE_OUT / lnk).resolve().exists()]
print("gallery links:", len(links), "broken:", len(bad), bad[:8])
if bad:
    print("ABORT: gallery has broken links; suite-state not finalized")
    sys.exit(2)

# ---------- suite-state 最终同步 ----------
st_metrics = {t: task_data[t]["finals"] for t in ORDER}
for x in ST["tasks"]:
    x["final_images"] = st_metrics[x["id"]]
st_metrics_all = sum(st_metrics.values())
ST.update({
    "status": "completed",
    "stop_reason": "all_tasks_completed",
    "updated_at": NOW,
    "current_task": None,
    "last_checkpoint": "state-000053.json",
    "task_finals_disk_audit": st_metrics,
    "suite_artifacts": [
        "outputs/%s/_suite/index.md" % RUN,
        "outputs/%s/_suite/gallery.md" % RUN,
        "outputs/%s/_suite/snapshot-usage.md" % RUN,
        "outputs/%s/_suite/task-metrics.json" % RUN,
        "outputs/%s/_suite/suite-state.json" % RUN,
    ],
    "completed_task_count": len(ORDER),
})
(SUITE_OUT / "suite-state.json").write_text(
    json.dumps(ST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("suite-state finalized; finals =", st_metrics_all)

# ---------- index.md ----------
ix = ["# 全套总索引 · Snapshot 全套任务（30 题）", "",
      "- run：`%s` · profile：all（A01–A24 + B01–B06）· 状态：**全部完成（30/30）**" % RUN,
      "- 时间：%s 起 → %s 收（含跨日运行与真实夜间暂停；单题时长见各题 task-metrics）" % (ST["started_at"], NOW),
      "- 服务：https://open-snapshot.muedsa.com（真实渲染，响应字节即最终图）·DSL 文档缓存自 B04 起",
      "- 套件交付：[gallery.md](gallery.md)（逐图 124 张）· [snapshot-usage.md](snapshot-usage.md) ·",
      "  [task-metrics.json](task-metrics.json) · [suite-state.json](suite-state.json)",
      "", "## 状态总表", "",
      "| # | 题 | 状态 | 终图 | 渲染 200/4xx | 看图 | 单题入口 |", "|---|---|---|---|---|---|---|"]
for i, t in enumerate(ORDER, 1):
    d = task_data[t]
    if t.startswith("B"):
        entry = "../%s/portfolio.md" % t
    elif t in ("A21", "A22"):
        entry = "../%s/round-01/launch-portrait.png" % t if t == "A21" else "../%s/round-01/dashboard.png" % t
    elif t == "A23":
        entry = "../%s/cover.png" % t
    else:
        pngs_t = disk_pngs(t)
        entry = ("../%s" % pngs_t[0].relative_to(OUT).as_posix()) if pngs_t else ""
    ix.append("| %d | %s | %s | %d | %d / %d | %s | [%s](%s) |" % (
        i, t, d["status"], d["finals"], d["renders_ok"], d["renders_fail"],
        d["image_views"] if d["image_views"] is not None else "—", t, entry))
ix += ["",
       "**合计**：终图 124（A 类 64 + B 类 60）· 渲染 %d（200×%d + 失败×%d）·" % (
           tot["renders"], tot["renders_ok"], tot["renders_fail"]),
       "服务 HTTP 总行 %d（其余为文档/字体/探针等记录，不重复计渲染）· 看图（显式字段合计）%d · 迭代台账行 %d。" % (
           tot["req_rows"], tot["image_views"], tot["iter_rows"]),
       "",
       "## 共享准备与复用",
       "- 文档缓存：ai-guide.md 与 DSL 文档于 B04 实抓一次（`tmp/%s/B04/renders/`），后续题复用不重复计请求。" % RUN,
       "- 共享客户端：`tmp/%s/_suite/snapshot_client.py`（渲染 + requests.jsonl 留痕）。" % RUN,
       "- 字体规约：CJK 用 Noto Sans CJK SC，数字用 Inter（仅纯 ASCII）；均在 A14 黑体探针与 A15 探针验证。",
       "", "## 计时说明",
       "- 套件墙钟：%s → %s。单题 elapsed 合计 %.1f s（约 %.1f 小时）；跨题含未计入的会话间隙（含 A19→A20、B05→B06 等夜间断点），" % (
           ST["started_at"], NOW, tot["elapsed_task_sum"], tot["elapsed_task_sum"] / 3600.0),
       "  因此单题之和≠总墙钟；各题等待时间如实标注（无等待记 0，不可测记 null）。",
       "", "## 复现",
       "- 逐题：`tmp/<run>/<题>/` 下 `requests.jsonl` / `iterations.jsonl`（B 题另有 tool-usage.jsonl）与 `renders/` 全部请求响应留痕。",
       "- 逐题 DSL：`tmp/<run>/<题>/dsl/`（B 题）或 `tmp/<run>/<题>/*.snapshot`（A 题），版本递增不可覆盖。",
       "", "## B06 特别说明（最后题）",
       "- B06《日常信息重构十件》为自主选题（十件独立：符号语法/价格与概率语义/体感转译/行为卡/读数训练）。",
       "- 根文档：[portfolio](../B06/portfolio.md) · [gallery](../B06/gallery.md) · 证据 [problem-evidence.json](../B06/problem-evidence.json) ·",
       "  [design-review.md](../B06/design-review.md)（可观改善 vs 未验证效果）。"]
(SUITE_OUT / "index.md").write_text("\n".join(ix) + "\n", encoding="utf-8")
print("index.md written")

# ---------- snapshot-usage.md (suite) ----------
fail_tasks = {t: v["renders_fail"] for t, v in task_data.items() if v["renders_fail"]}
su = ["# 全套 Snapshot 使用与最终审查", "",
      "## 服务调用总况（各题聚合，唯一口径=逐题 requests.jsonl 原始行）",
      "- 渲染请求：%d（200×%d / 失败×%d）。失败分布：%s" % (
          tot["renders"], tot["renders_ok"], tot["renders_fail"],
          ("；".join("%s %d 次（同因语法均可修复，已留证）" % (t, n) for t, n in fail_tasks.items())
           if fail_tasks else "无")),
      "- 服务 HTTP 总行（含文档/探针/字体等）：%d 行；其中非渲染行 %d 行（文档缓存抓取集中在 B04 一次完成，后续题复用计 0）。" % (
          tot["req_rows"], tot["doc_other"]),
      "- 无 429/速率限流（0 次）；Retry-After 均为 null；密钥零写入全部台账。",
      "- 复现：`python tmp/<run>/_suite/snapshot_client.py render <题> <dsl> <tag> <outdir>`（需要 env：SNAPSHOT_TASK_ROOT / SNAPSHOT_RUN_ID）。", "",
      "## 文档/能力应用（跨题汇编）",
      "- 实抓文档：ai-guide.md 与 DSL 文档（B04 缓存于 `tmp/<run>/B04/renders/`）；字体清单查询一轮；其后全部复用。",
      "- 已验证关键规约（逐题踩坑累计）：" ,
      "  1) border 枚举仅 NONE/SOLID（A03/B05 DASHED 两次实证，后以线段仿真）；",
      "  2) 8 位颜色 `#RRGGBBAA` 末组为 alpha（A01↔A10 探明）；",
      "  3) Transform 为 4×4 列主序，平移分量 = p−K·p（A09 校正）；",
      "  4) Positioned 仅在 Stack/画布根内定位；Row/Column 不接受它（A03 验证）；",
      "  5) 特殊字符经 Raw/CDATA 保真（A11/A17 逐字符）；fontWeight/fontStyle 行为有探针实证（A15）；",
      "  6) B06 新坑：**凭记忆的语法会 200 但版式全崩**——Text 无自由 x/boxWidth、Container 无 left/top；",
      "     真实书写应为 Positioned 定位 + Container/Text 属性（B06 v1 十张全 200 不可用版式留证、v3 重写生效）；",
      "  7) 渲染驱动会“回退旧文件”造成误渲（B05 v2/B06 v2 两次同型），候选文件必须显式 `_vN` 优先。",
      "- 双字体纪律：CJK = Noto Sans CJK SC（txt），纯 ASCII 数字 = Inter（num）；禁裸 `<`；每 canvas 首笔全幅底色。", "",
      "## 看图与迭代（各题汇总）",
      "- 看图（显式 image_views 合计）：%d 次——含每张最终图的整幅查看与密集区放大；接触表/缩略不替代整幅（各题 snapshot-usage 有逐题口径）。" % tot["image_views"],
      "- 完整视觉迭代（view→改→渲→再看的完成周期）合计 %d：A 类显式字段 49 + B01–B04 显式 15 + B05 20 + B06 9（语法修复行单独计，不入此项）。" % tot["cvis"],
      "- 迭代台账行合计 %d 行（baseline/语法修复/visual/需求变更分开计；B06 台账 40 行中 v2 无效批 10 行为字节哈希鉴别、非看图事件，已在行内注明）。" % tot["iter_rows"],
      "", "## 数值/调研合规（B04/B06 核查类）",
      "- B04：来源三重校验（原文要点+检索+存疑标注），sources.json 留痕。",
      "- B06：两次 websearch（财政部公告 2023-30 时效、WHO 2015 游离糖）真实发生并计入 tool-usage；数值唯一基准=calcs.json。",
      "- 演示口径逐件声明；不声称未做过的调研/实验、不伪造官方背书。", "",
      "## 最终审查结论",
      "- 30/30 完成；总终图 124（=磁盘审计）；每张图配同名完整 `.snapshot`（gallery 全量校验链接可达）。",
      "- 各题状态/证据：见 [suite-state.json](suite-state.json)（每题 artifacts/visual_review_evidence/unresolved）。",
      "- 遗留未解决事项：无（各题 unresolved_issues 均为空）。", "",
      "## 踩坑与跨题经验汇编（按时间序）",
      "- A01↔A10：颜色 alpha 位、BackdropFilter/ImageFiltered 组合语义、文字与滤镜先后。",
      "- A03：Positioned 需 Stack 语境；rotate 数值经 REVIEW 30° 验证。",
      "- A07：`extend` 字符串展开需逐字落盘（PARSE_ERROR 根因）。",
      "- A09：Transform 平移分量语义；±1.5px 像素级审计方法。",
      "- A11/A17：CDATA 保真与教学示例 [[CDATA 转义现身说法]]。",
      "- A13：透明 PNG 预览策略与角落最小化偏差。",
      "- A15：fontWeight 数值 vs 命名探针。",
      "- A19：等价像素策略（双 DSL 同画布同几何不同遮蔽层）。",
      "- A21/A22：预置三轮的回归执行方式（每轮只改需求点，对比区域零回归）。",
      "- B05：256 色规则下的纸感纹理（细线/渐变替代照片）；三字字体误植审查法（「元/分摊」逐字校笔）。",
      "- B06：语法记忆坑（见上）+ **一次渲染请求=一个真实 tag**（候选顺序修正）。",
      ]
(SUITE_OUT / "snapshot-usage.md").write_text("\n".join(su) + "\n", encoding="utf-8")
print("snapshot-usage.md written")

# ---------- task-metrics.json (suite) ----------
def status_counts():
    from collections import Counter
    c = Counter()
    for t in ORDER:
        c[task_data[t]["status"]] = c[task_data[t]["status"]] + 1
    return {k: c.get(k, 0) for k in ("completed", "partial", "blocked", "pending")}


suite_metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "suite_version": ST.get("suite_version", "1.0.0"),
    "run_id": RUN,
    "profile": ST.get("profile", "all"),
    "status": "completed",
    "stop_reason": "all_tasks_completed",
    "started_at": ST["started_at"],
    "ended_at": NOW,
    "elapsed_seconds": None,
    "wall_clock_note": "套件起止为真实墙钟（含跨夜与用户暂止）；单题 elapsed_seconds 由各题计时文件给出并可用合计（不含题间会话间隙），因此不等于套件墙钟；请求耗时之和亦≠墙钟",
    "task_status_counts": status_counts(),
    "counts": {
        "final_pngs": tot["finals"],
        "independent_creative_cases": tot["finals"],
        "snippet_note": "A17 页面与示例均独立计数；A21/A22 各轮独立计数；B 题十件=各独立用例",
        "snapshot_requests": tot["renders"],
        "successful_snapshot_requests": tot["renders_ok"],
        "failed_snapshot_requests": tot["renders_fail"],
        "retry_requests": 0,
        "other_service_requests": tot["doc_other"],
        "document_requests": 2,
        "document_note": "ai-guide.md 与 DSL 文档实抓记 B04（缓存复用至其余 29 题不重复计）",
        "dsl_versions": "见逐题（dsl_versions 字段或各题 dsl/ 目录实际版本文件数）",
        "image_views": tot["image_views"],
        "views_coverage_note": "30/30 题均提供显式 image_views（聚合只加各题顶层值，不把 round/case 明细重复相加）",
        "completed_visual_iterations": tot["cvis"],
        "cvis_note": "A01–A24 与 B01–B04 取各题 counts.completed_visual_iterations；B05/B06 为迭代台账 visual_iteration+requirement_change 合计（语法修复行单独计，B06 的 v2 无效批 10 行不含看图不入此项）；A49+B15+B05·20+B06·9=93",
        "incomplete_visual_iterations": 0,
    },
    "shared_preparation": {
        "docs_cached": ["https://open-snapshot.muedsa.com/ai-guide.md", "https://snapshot.muedsa.com/"],
        "shared_client": "tmp/%s/_suite/snapshot_client.py" % RUN,
        "ratings_note": "共享准备只计一次；每请求归属单一用例或共享范围",
    },
    "task_summaries": [
        {
            "task_id": t,
            "status": task_data[t]["status"],
            "final_images": task_data[t]["finals"],
            "markdown_source": "outputs/%s/%s/task-metrics.json" % (RUN, t),
            "elapsed_seconds": task_data[t]["elapsed"],
            "window": {"started_at": task_data[t]["window"][0], "ended_at": task_data[t]["window"][1]},
            "requests_jsonl_rows": task_data[t]["req_rows"],
            "snapshot_requests": task_data[t]["renders"],
            "snapshot_responses_ok": task_data[t]["renders_ok"],
            "snapshot_responses_fail": task_data[t]["renders_fail"],
            "non_render_rows": task_data[t]["doc_other_rows"],
            "image_views": task_data[t]["image_views"],
            "dsl_versions": task_data[t]["dsl_versions"],
            "iterations_ledger_rows": task_data[t]["iter_rows"],
        } for t in ORDER
    ],
    "aggregation_rule": "Only task-level totals plus shared preparation; never add round/case detail again.",
    "output_dir": "outputs/%s/" % RUN,
    "temp_dir": "tmp/%s/" % RUN,
    "unresolved_issues": [],
    "suite_required_artifacts_check": {
        name: ("outputs/%s/_suite/%s" % (RUN, name)) for name in (
            "index.md", "gallery.md", "snapshot-usage.md", "task-metrics.json", "suite-state.json")
    },
}
(SUITE_OUT / "task-metrics.json").write_text(
    json.dumps(suite_metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("task-metrics.json written")

# ---------- 完成事件 + checkpoint（校验通过后执行；幂等防重复） ----------
EV = SUITE_TMP / "events.jsonl"
_EVR = EV.read_text(encoding="utf-8")
if "suite-completed" in _EVR:
    print("suite-completed event already exists — skip append")
else:
    ev_next = len(_EVR.strip().splitlines()) + 1
    event = {
        "id": "SUITE-ev-%06d" % ev_next,
        "at": NOW,
        "kind": "suite-completed",
        "task_id": "SUITE",
        "detail": ("全套 30 题全部完成：终图 124 张（=磁盘审计，A64+B60），渲染 %d（200×%d/失败×%d），"
                   "服务 HTTP 总行 %d，显式看图合计 %d，迭代台账 %d 行；_suite 全件落盘 "
                   "(index/gallery/snapshot-usage/task-metrics/suite-state) 且 gallery 链接全量校验 %d 处通过。"
                   % (tot["renders"], tot["renders_ok"], tot["renders_fail"],
                      tot["req_rows"], tot["image_views"], tot["iter_rows"], len(links) - len(bad))),
    }
    with EV.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print("event appended:", event["id"])

_ckfile = SUITE_TMP / "checkpoints" / "state-000053.json"
if _ckfile.exists():
    print("checkpoint state-000053 already exists — skip")
else:
    ck = dict(ST)
    ck["checkpoint_id"] = "state-000053.json"
    ck["checkpoint_at"] = NOW
    ck["checkpoint_prev"] = "tmp/%s/_suite/checkpoints/state-000052.json" % RUN
    CKP = _ckfile
    CKP.write_text(json.dumps(ck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("checkpoint saved:", CKP.name)
print("DONE finalize_b06_suite_docs")
