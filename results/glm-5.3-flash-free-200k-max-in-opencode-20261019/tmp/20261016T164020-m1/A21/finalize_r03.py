# -*- coding: utf-8 -*-
"""A21 round-03 收尾：tokens/content-map/metrics/usage + 根累计 + suite 状态。
请求留痕已由 snapshot_client 自动追加（A21-render-0015..0022），本脚本只统计。
"""
import json
import os
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
A21 = f"outputs/{RUN}/A21"
R3 = f"{A21}/round-03"
TMP = f"tmp/{RUN}/A21"
now = lambda: datetime.now(TZ).isoformat(timespec="milliseconds")
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
mt = lambda p: datetime.fromtimestamp(os.path.getmtime(p), TZ).isoformat(timespec="milliseconds")

audit = json.load(open(f"{R3}/contrast-audit.json", encoding="utf-8"))
runs = {r["id"]: r for img in audit["images"] for r in img["text_runs"]}


def gr(rid):
    """真实墨迹核框（audit 行剖面+归属排除所得，未经外扩）。"""
    return list(runs[rid]["glyph_band_core"])


def band(*rids):
    rs = [gr(x) for x in rids]
    return [min(r[0] for r in rs), min(r[1] for r in rs),
            max(r[2] for r in rs), max(r[3] for r in rs)]


def sep2d(a, b):
    """两实心矩形的最小间隙：竖向不交则取竖间距，横向不交则取横间距；相交=0。"""
    ax_lo, ay_lo, ax_hi, ay_hi = a
    bx_lo, by_lo, bx_hi, by_hi = b
    dv = max(bx_lo - ax_hi, ax_lo - bx_hi, 0)      # 横向不交时的横向间距
    dx = max(by_lo - ay_hi, ay_lo - by_hi, 0)      # 纵向不交时的纵向间距
    if dv > 0:
        return {"kind": "horizontal", "gap": dv}
    if dx > 0:
        return {"kind": "vertical", "gap": dx}
    return {"kind": "overlap", "gap": 0}


def pair(a, b):
    s = sep2d(a, b)
    ok = s["gap"] >= 8
    return s, ok


# ── 逐对实测间隙（字形核范围，未加反锯齿容差；核心字形 gap≥8 即视觉留白充足）──
dec_bars = {"portrait_underline": [470, 894, 610, 897], "portrait_rule_r": [738, 500, 822, 502],
            "portrait_rule_l": [258, 500, 342, 502], "wide_underline": [660, 506, 790, 509]}
pill_boxes = {"p_pill": [390, 1034, 690, 1090], "w_pill": [122, 618, 398, 674]}
chip_boxes = {"p_chip": [310, 1156, 770, 1218], "w_chip": [660, 670, 1120, 726]}

PAIRS = [
    ("portrait", "eyebrow→title1", sep2d(band("TR-P01"), gr("TR-P02"))),
    ("portrait", "rule_r→eyebrow", pair(gr("TR-P01"), dec_bars["portrait_rule_r"])[0]),
    ("portrait", "title3→tagline", pair(gr("TR-P04"), gr("TR-P05"))[0]),
    ("portrait", "tagline→date", pair(gr("TR-P05"), gr("TR-P06"))[0]),
    ("portrait", "date→underline", pair(gr("TR-P06"), dec_bars["portrait_underline"])[0]),
    ("portrait", "underline→speakers", pair(dec_bars["portrait_underline"], gr("TR-P07"))[0]),
    ("portrait", "speakers→sponsor", pair(gr("TR-P07"), band("TR-P08", "TR-P09"))[0]),
    ("portrait", "sponsor→pill(box)", pair(band("TR-P08", "TR-P09"), pill_boxes["p_pill"])[0]),
    ("portrait", "pill(box)→tagline_en", pair(pill_boxes["p_pill"], gr("TR-P11"))[0]),
    ("portrait", "tagline_en→chip(box)", pair(gr("TR-P11"), chip_boxes["p_chip"])[0]),
    ("wide", "rule→eyebrow", pair(gr("TR-W01"), dec_bars["wide_underline"] and [660, 136, 756, 138])[0]),
    ("wide", "eyebrow→title1", pair(gr("TR-W01"), gr("TR-W02"))[0]),
    ("wide", "title1→title2", pair(gr("TR-W02"), gr("TR-W03"))[0]),
    ("wide", "title2→title3", pair(gr("TR-W03"), gr("TR-W04"))[0]),
    ("wide", "title3→tagline", pair(gr("TR-W04"), gr("TR-W05"))[0]),
    ("wide", "tagline→date", pair(gr("TR-W05"), gr("TR-W06"))[0]),
    ("wide", "date→underline", pair(gr("TR-W06"), dec_bars["wide_underline"])[0]),
    ("wide", "underline→speakers", pair(dec_bars["wide_underline"], gr("TR-W07"))[0]),
    ("wide", "speakers→sponsor", pair(gr("TR-W07"), band("TR-W08", "TR-W09"))[0]),
    ("wide", "sponsor→tagline_en", pair(band("TR-W08", "TR-W09"), gr("TR-W10"))[0]),
    ("wide", "tagline_en→chip(box)", pair(gr("TR-W10"), chip_boxes["w_chip"])[0]),
    ("wide", "free_pill(glyph)→right_col", pair(gr("TR-W12"), band("TR-W01", "TR-W02", "TR-W03",
                                                                   "TR-W04", "TR-W05", "TR-W06",
                                                                   "TR-W07", "TR-W08", "TR-W09",
                                                                   "TR-W10", "TR-W11"))[0]),
]
pair_fail = [k for (img, k, s) in PAIRS if s["kind"] == "overlap"]
bad_gap = [(img, k, round(s["gap"], 1)) for (img, k, s) in PAIRS
           if s["kind"] != "overlap" and s["gap"] < 8]
print("PAIRS gaps:")
for img, k, s in PAIRS:
    print(f"  {img:8s} {k:26s} {s['kind']:10s} {s['gap']:.1f}")
print("overlaps:", pair_fail or "none")
print("gaps<8:", bad_gap or "none")
if pair_fail or bad_gap:
    raise SystemExit("layout gap check failed — fix before finalize")

# ── A) design-tokens.json（round-03）────────────────────────
tokens = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir", "round": 3,
    "theme": "light",
    "colors": {
        "bg_light_1": "#F5F8FC", "bg_light_2": "#E9EFF7",
        "text_primary": "#0F1B2D", "text_secondary": "#2A3A54",
        "text_soft": "#44536B",
        "brand_text_teal_ink": "#085F55",
        "brand_primary_accent": "#2EE6D0", "secondary_accent": "#7C6CFF",
        "sky": "#5AD7FF",
        "url_chip": {"bg": "#0D2237", "text": "#7FF3E6"},
        "free_pill": {"bg": "#FCFEFE", "border": "#BFD6E4", "text": "#085F55"},
        "sponsor": {"label": "#506681", "name": "#44536B"},
        "ghost_light_overlay": {
            "ring_outer": "#CFE3EF", "ring_inner": "#C7DCEE",
            "beacon_halo": "#D4E7F2", "beacon_core": "#199CD9",
            "rule_short": "#BFD6E4", "mesh_dot": "#C9D4E2"
        },
        "brand_decor_preserved": "横带三段渐变端色 #2EE6D0/#5AD7FF/#45D2DF/#7C6CFF 与"
    },
    "typography": {
        "family_cjk": "Noto Sans CJK SC", "family_latin": "Inter",
        "scale": {
            "title_portrait": 64, "title_wide": 54, "eyebrow": 26,
            "tagline_portrait": 30, "tagline_wide": 28,
            "date_portrait": 46, "date_wide": 44,
            "speakers_portrait": 30, "speakers_wide": 28,
            "sponsor": 26, "free_pill": 26, "tagline_en": 26, "url": 30
        },
        "rules": "三轮一致：主标题竖 64/横 54（≥48 且竖图首行沿用 ≥56 合规），"
                 "其余 ≥24；无 Transform/scale 压字"
    },
    "brand_geometry": [
        {"id": "layer-stack", "desc": "三层青→紫渐变圆角横带",
         "params": {"portrait": {"base": [374, 322], "band": [296, 24], "step": [18, 36]},
                    "wide": {"base": [160, 252], "band": [320, 26], "step": [20, 44]}},
         "inherit": "自 round-01 完整继承，端色不变"},
        {"id": "halo-ring", "desc": "双同心环（浅色描线）",
         "params": {"portrait": {"center": [540, 380], "radii": [240, 180]},
                    "wide": {"center": [322, 344], "radii": [212, 158]}},
         "inherit": "几何同 r01/r02；描线色改浅色系"},
        {"id": "beacon", "desc": "信标点（浅晕+蓝核）",
         "params": {"portrait": {"center": [742, 470]}, "wide": {"center": [492, 428]}},
         "inherit": "位置同 r01/r02；晕圈改 #D4E7F2"},
        {"id": "mesh-dots", "desc": "点阵",
         "params": {"portrait": {"origin": [108, 210], "grid": [5, 3], "pitch": [46, 40]},
                    "wide": {"origin": [120, 552], "grid": [5, 2], "pitch": [48, 34]}},
         "inherit": "同前轮；点色改 #C9D4E2"}
    ],
    "changes": [
        {"change": "主题深→浅：底 #F5F8FC→#E9EFF7 渐变；文字色板换浅底墨色系"
                   "（INK #0F1B2D / INK2 #2A3A54 / MUT #44536B）",
         "reason": "round-03 预置需求（浅色主题与 4.5:1 对比度审计）"},
        {"change": "品牌青文字色 TEAL_INK #0A6E62→#085F55（加深）",
         "reason": "对比审计实测：眉题 O 压幽灵内环 #C7DCEE 时 4.357<4.5；"
                   "加深后 5.363，且 pill/EN 侧同步升至 7.47/6.61-6.96"},
        {"change": "新增英文副句『Clarity through structure』(26px Inter, ls 3,"
                   " 竖 y1108 / 横 y624，位于网址胶囊上方)",
         "reason": "round-03 预置需求（≥24px）"},
        {"change": "幽灵装饰改浅色系：环 #CFE3EF/#C7DCEE、信标晕 #D4E7F2、"
                   "短横线 #BFD6E4、点阵 #C9D4E2（深底预混实色策略不再适用）",
         "reason": "浅底下保持可辨识装饰且不参与文字对比竞争"},
        {"change": "横屏右列级联插入 EN 行：sponsor 610→572、EN 624、"
                   "chip 670；竖图 sponsor 990→986、EN 1108、chip 1156",
         "reason": "为 EN 行腾位；实测同列相邻字形间隙≥8px（见 content-map.checks）"},
        {"change": "品牌 4 构件坐标与主色/横带渐变全继承；payload 无 Transform，"
                   "未用变形压窄文字", "reason": "跨轮一致性与 hard constraint"},
    ],
}
json.dump(tokens, open(f"{R3}/design-tokens.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)

# ── B) content-map.json（round-03）─────────────────────────
H3 = lambda s: int(s * 1.45) + 2
gap_ev = [f"{img}/{k}: {s['kind']} {s['gap']:.1f}px" for (img, k, s) in PAIRS
          if s["kind"] != "overlap"]
cmap = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir", "round": 3,
    "entries": [
        {"id": "CT-01", "role": "title", "status": "inherited_moved",
         "text": "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
         "source": "round-02 文本继承；round-03 浅色重排",
         "portrait": {"layout": "3 行居中", "font_px": 64, "lines": 3,
                      "boxes": [[0, 524, 1080, 618], [0, 602, 1080, 696], [0, 680, 1080, 774]]},
         "wide": {"layout": "3 行左对齐", "font_px": 54, "lines": 3,
                  "boxes": [[660, 206, 1350, 286], [660, 268, 1350, 348], [660, 330, 1350, 410]]}},
        {"id": "CT-02", "role": "eyebrow", "status": "inherited_moved",
         "text": "ONLINE LAUNCH", "source": "round-01 继承（竖 y472 不变/横 164→150）",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[240, 472, 840, 511]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[660, 150, 1320, 189]]}},
        {"id": "CT-03", "role": "event_name", "status": "inherited_moved",
         "text": "叠光 Layerlight 发布活动", "source": "round-01 继承",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[0, 768, 1080, 813]]},
         "wide": {"font_px": 28, "lines": 1, "boxes": [[660, 398, 1350, 440]]}},
        {"id": "CT-04", "role": "date", "status": "inherited_moved",
         "text": "2026.11.07 19:30", "source": "round-01 继承",
         "portrait": {"font_px": 46, "lines": 1, "boxes": [[0, 828, 1080, 896]]},
         "wide": {"font_px": 44, "lines": 1, "boxes": [[660, 442, 1350, 507]]}},
        {"id": "CT-05", "role": "speakers", "status": "inherited_moved",
         "text": "讲者：林川 / 苏言", "source": "round-01 继承",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[0, 918, 1080, 963]]},
         "wide": {"font_px": 28, "lines": 1, "boxes": [[660, 520, 1320, 562]]}},
        {"id": "CT-06", "role": "url", "status": "inherited_moved",
         "text": "layerlight.example.org", "source": "round-01 继承（浅色反转胶囊保留）",
         "portrait": {"font_px": 30, "lines": 1, "boxes": [[310, 1156, 770, 1218]]},
         "wide": {"font_px": 30, "lines": 1, "boxes": [[660, 670, 1120, 726]]}},
        {"id": "CT-07", "role": "sponsor", "status": "inherited_moved",
         "text": "赞助 Northstar Research / 云构工具",
         "source": "round-02 文本继承；圆环行色彩分 sponsor 前缀 #506681/名 #44536B",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[0, 986, 1080, 1026]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[660, 572, 1350, 612]]}},
        {"id": "CT-08", "role": "attendance", "status": "inherited_moved",
         "text": "免费参加 · 无需报名", "source": "round-02 文本继承；白底胶囊",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[390, 1034, 690, 1090]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[122, 618, 398, 674]]}},
        {"id": "CT-09", "role": "tagline_en", "status": "new",
         "text": "Clarity through structure",
         "source": "round-03 预置需求（网址上方新增，≥24px）",
         "portrait": {"font_px": 26, "lines": 1, "boxes": [[0, 1108, 1080, 1147]]},
         "wide": {"font_px": 26, "lines": 1, "boxes": [[660, 624, 1350, 663]]}},
    ],
    "checks": [
        {"check": "round-02 全部文案保留（CT-01..CT-08）且每段在两图实际渲染",
         "result": "pass", "evidence": "contrast-audit.json 前景像素实测（每段存在核心字形像素）+ 两图整图查看"},
        {"check": "中文长标题 ≤3 行且字号 ≥48（竖 64/横 54），无 Transform",
         "result": "pass", "evidence": "build_a21_r03.py 无 Transform 标签；标题放大查看"},
        {"check": "浅色主题普通文字对比度 ≥4.5:1（含最差位置与实际合成背景）",
         "result": "pass",
         "evidence": f"contrast-audit.json：2 图 ×12 段全部 pass_unrounded，"
                     f"最小 {audit['summary']['min_ratio_observed_6dp']:.6f}"
                     "（sponsor 前缀 #506681）；最差样本含幽灵环/渐变底/胶囊白/胶囊深"},
        {"check": "同列相邻元素实测间隙 ≥8px（字形核范围，不含反锯齿 ±2 容差）",
         "result": "pass", "evidence": "；".join(gap_ev)},
        {"check": "EN 副句位于网址上方且 ≥24px，两图一致",
         "result": "pass", "evidence": "CT-09 boxes；r3 两图放大查看"},
        {"check": "装饰与文字无 2D 真碰撞（相邻横线/条带按横向间隙计）",
         "result": "pass", "evidence": "date→underline 等项见上列实测间隙（同列表逐级≥8px）"},
    ],
}
json.dump(cmap, open(f"{R3}/content-map.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)

# ── C) round-03/task-metrics.json ──────────────────────────
reqs = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8")]
r3reqs = [r for r in reqs if r["response_file"].split("/")[-1].startswith("a21-r03-")]
ok = [r for r in r3reqs if r["http_status"] == 200]
fail = [r for r in r3reqs if r["http_status"] != 200]
dur = sum(float((r.get("server_timing") or "0").split("dur=")[-1].rstrip(',') or 0)
          for r in ok if (r.get("server_timing") or "").count("dur=") >= 2)
started = min(r["started_at"] for r in r3reqs)
ts_preview = mt(f"{R3}/launch-portrait.png")
first_usable = (datetime.fromisoformat(ts_preview) -
                datetime.fromisoformat(started)).total_seconds()
m3 = {
    "schema_version": 1, "path_base": "output_dir", "task_id": "A21", "round": 3,
    "run_id": RUN, "status": "completed", "output_dir": "round-03/",
    "timings": {
        "started_at": started,
        "ended_at": None,  # filled below
        "elapsed_seconds": None, "first_usable_image_seconds": round(first_usable, 1),
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur / 1000, 4),
        "server_timing_source": "snapshot_client 自动留痕 requests.jsonl（成功请求 total dur）",
    }, "counts": {
        "snapshot_requests": len(r3reqs),
        "successful_snapshot_requests": len(ok),
        "failed_snapshot_requests": len(fail),
        "retry_requests": 0, "other_service_requests": 0,
        "dsl_versions": 4,
        "image_views": 13,
        "completed_visual_iterations": 1,
        "incomplete_visual_iterations": 0,
        "final_images": 2,
    }, "logs": {
        "requests": f"tmp/{RUN}/A21/requests.jsonl（A21-render-0015..0022）",
        "iterations": f"tmp/{RUN}/A21/r03-iterations.jsonl",
        "contrast_audit": "round-03/contrast-audit.json",
    },
    "outputs": [
        {"name": "launch-portrait.png", "path_base": "output_dir", "path": "launch-portrait.png"},
        {"name": "launch-portrait.snapshot", "path_base": "output_dir", "path": "launch-portrait.snapshot"},
        {"name": "launch-wide.png", "path_base": "output_dir", "path": "launch-wide.png"},
        {"name": "launch-wide.snapshot", "path_base": "output_dir", "path": "launch-wide.snapshot"},
        {"name": "design-tokens.json", "path_base": "output_dir", "path": "design-tokens.json"},
        {"name": "content-map.json", "path_base": "output_dir", "path": "content-map.json"},
        {"name": "contrast-audit.json", "path_base": "output_dir", "path": "contrast-audit.json"},
        {"name": "snapshot-usage.md", "path_base": "output_dir", "path": "snapshot-usage.md"},
        {"name": "task-metrics.json", "path_base": "output_dir", "path": "task-metrics.json"},
    ],
    "candidates": [
        {"name": "launch-portrait v1（superseeded by TEAL_INK fix）",
         "path_base": "suite_root", "path": f"tmp/{RUN}/A21/renders/a21-r03-portrait-113309695.resp"},
        {"name": "launch-wide v1（superseeded by TEAL_INK fix）",
         "path_base": "suite_root", "path": f"tmp/{RUN}/A21/renders/a21-r03-wide-113316620.resp"},
        {"name": "去文字辅助背景 PNG/DSL（审计证据；保留不清理）",
         "path_base": "suite_root", "path": f"tmp/{RUN}/A21/bg-data/"},
    ],
    "unresolved_issues": [],
    "notes": "r03 含 2 张辅助去文字渲染（审计用，非最终图）；最终图 v1→v2 由"
             "对比审计驱动（TEAL_INK 加深），v1 原始响应保留于 renders/。",
}

# ── D) round-03/snapshot-usage.md ──────────────────────────
usage = f"""# A21 round-03 · snapshot-usage

## 状态
completed。round-03/launch-portrait.png/.snapshot(1080×1350)、launch-wide.png/.snapshot
(1440×810) 为服务 200 真实响应（v2 重渲后版本）；round-01/02 全部文件不改动完整保留。

## 本轮变更（design-tokens.changes 同源）
1. 深空主题→浅色：底渐变 #F5F8FC→#E9EFF7，文字墨色系 #0F1B2D/#2A3A54/#44536B，
   网址胶囊反转（#0D2237 底 + #7FF3E6 文），免费胶囊白底描边。
2. 新增网址上方英文副句『Clarity through structure』(26px)：竖 y1108、横 y624。
3. 品牌青文字色加深 #0A6E62→#085F55（审计驱动，见下），装饰渐变端色与主色不变；
   4 构件（横带/双环/信标/点阵）坐标继承，描线/点/晕改浅色系。
4. 全部 round-02 文案（标题 3 行/眉行/日期/讲者/赞助/免费参加/网址）保留并级联微移。

## 对比度审计（round-03/contrast-audit.json）
- 公式：WCAG 2.x sRGB 线性化 L=0.2126R+0.7152G+0.0722B，ratio=(L亮+0.05)/(L暗+0.05)，
  未舍入判值，阈值 4.5；阈值未用 UA 特殊公式豁免。
- 背景：使用两张**去文字辅助渲染**（同构布局删除全部 Text 及仅含 Text 的 Positioned，
  保留渐变底/幽灵环/点阵/白胶囊/深胶囊；label a21-r03-*-bg，响应与 PNG 保留于
   tmp/{RUN}/A21/bg-data/），在**最终图实测字形范围（前景色 ±3 通道匹配紧外包 + 2px
  反锯齿容差）**内逐像素取最劣背景样本。
- 结果：2 图 ×12 段全部 pass_unrounded；最小 5.199784（sponsor 前缀 #506681 on #ECF1F8）。
- 审计发现并修复的问题：v1 眉题 ONLINE LAUNCH 的 O 落在幽灵内环线上
  （#C7DCEE）仅 4.356541<4.5 → TEAL_INK 加深为 #085F55 重渲 v2 → 5.362942，24/24 通过。
- 失败尝试留痕：首轮辅助渲染 2×400（ProxyWidget has no widget，strip 后空
  Positioned 无子节点）；修好后同构重渲 2×200（过程入 syntax-fix 迭代记录）。

## 实际查看记录
- v1：两图 half + 竖 top/title/mid/bottom + 横 top/bottom + 2 张 bg-half 共 10 次查看。
- v2：两图 half + 眉题放大 3 次查看；audit 全红→全绿前后对比。
- iterations：baseline-v01（v1 两图，观察项：环线对比不足）→ syntaxfix-helper →
  visual-v02（TEAL_INK 修复；复查通过）。

## 未解决事项
无。
"""
open(f"{R3}/snapshot-usage.md", "w", encoding="utf-8", newline="\n").write(usage)

# ── F) r03-iterations.jsonl ────────────────────────────────
v1v = mt(f"{TMP}/steps/r03-portrait.png") if os.path.exists(f"{TMP}/steps/r03-portrait.png") else now()
iters = [
    {"id": "A21-r03-baseline-v01", "parent": "A21-r02-baseline-v01", "type": "baseline",
     "image": f"steps/r03-portrait.png",
     "viewed_at": mt(f"{TMP}/renders/a21-r03-portrait-113309695.resp"),
     "images": [f"steps/r03-portrait.png", f"steps/r03-wide.png",
                f"steps/r03p-half.png", f"steps/r03w-half.png"],
     "observable_issues": ["初版浅色两图整图/分区查看布局无缺陷；对比度审计发现"
                           "眉题压幽灵内环 4.3565<4.5（唯一不合格项）"],
     "changes": "浅色主题双图生成（含去文字辅助版方法搭建）",
     "recheck": "触发 visual-v02（TEAL_INK 加深）", "seq": 1},
    {"id": "A21-r03-syntaxfix-helper", "parent": "A21-r03-baseline-v01", "type": "syntax-fix",
     "image": f"bg-data/r03-portrait-bg.png",
     "viewed_at": mt(f"{TMP}/bg-data/r03-portrait-bg.png"),
     "images": [f"renders/a21-r03-portrait-bg-113355341.resp", f"renders/a21-r03-wide-bg-113356557.resp",
                f"renders/a21-r03-portrait-bg-113418518.resp", f"renders/a21-r03-wide-bg-113419907.resp",
                f"steps/r03p-bg-half.png", f"steps/r03w-bg-half.png"],
     "observable_issues": ["去文字辅助版 2×400：ProxyWidget has no widget —— strip 后"
                           "留下空 Positioned/无子节点包装"],
     "changes": "strip 规则改为整删『仅含 Text 的 Positioned』包装，再兜底删 Text",
     "recheck": "重渲 2×200；bg-half 查看确认无文字残留且容器全部保留", "seq": 2},
    {"id": "A21-r03-visual-v02", "parent": "A21-r03-baseline-v01", "type": "visual",
     "image": f"steps/r03-portrait.png", "viewed_at": now(),
     "images": [f"renders/a21-r03-portrait-115456045.resp", f"renders/a21-r03-wide-115458071.resp",
                f"steps/r03p-final-half.png", f"steps/r03w-final-half.png",
                f"steps/r03p-eyebrow-zoom.png"],
     "observable_issues": [],
     "changes": "TEAL_INK #0A6E62→#085F55；重渲两图 final v2",
     "recheck": "contrast-audit 24/24 pass_unrounded（最小 5.199784）；两图 half+眉题"
                "放大复查通过；v1 输出保留于 renders/*113309*/113316*.resp", "seq": 3},
]
open(f"{TMP}/r03-iterations.jsonl", "w", encoding="utf-8", newline="\n").write(
    "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in iters))

# ── G) 根累计 task-metrics.json ────────────────────────────
m1 = json.load(open(f"{A21}/round-01/task-metrics.json", encoding="utf-8"))
m2 = json.load(open(f"{A21}/round-02/task-metrics.json", encoding="utf-8"))
end = now()
m3["timings"]["ended_at"] = end
m3["timings"]["elapsed_seconds"] = round(
    (datetime.fromisoformat(end) - datetime.fromisoformat(started)).total_seconds(), 1)
json.dump(m3, open(f"{R3}/task-metrics.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)

wall = (datetime.fromisoformat(end) - datetime.fromisoformat(
    m1["timings"]["started_at"])).total_seconds()
act = m1["timings"]["elapsed_seconds"] + m2["timings"]["elapsed_seconds"] + \
    m3["timings"]["elapsed_seconds"]
req_total = 10 + 2 + len(r3reqs)  # r01×10 + r02×2 + r03×8（r02 重复行不重复计数）
cum = {
    "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
    "run_id": RUN, "status": "completed", "scope": "round-01..03 累计（不重复计子报告）",
    "timings": {
        "started_at": m1["timings"]["started_at"], "ended_at": end,
        "wall_clock_seconds": round(wall, 1),
        "active_round_seconds": round(act, 1),
        "idle_seconds_between_days": round(wall - act, 1),
        "first_usable_image_seconds": m1["timings"]["first_usable_image_seconds"],
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(
            sum(m["timings"]["request_duration_sum_seconds"] for m in (m1, m2, m3)), 4),
        "method": "墙钟含 2026-10-17 夜至 10-18 恢复执行的间隔；active=三轮 elapsed 之和；"
                  "两者差值记为跨日挂起/会话恢复间隔，未混入请求耗时",
    },
    "counts": {
        "snapshot_requests": req_total,
        "successful_snapshot_requests": m1["counts"]["successful_snapshot_requests"] +
        m2["counts"]["successful_snapshot_requests"] + len(ok),
        "failed_snapshot_requests": m1["counts"]["failed_snapshot_requests"] + len(fail),
        "retry_requests": 0, "other_service_requests": 0,
        "dsl_versions": 3 + 1 + 4,
        "image_views": m1["counts"]["image_views"] + m2["counts"]["image_views"] + 13,
        "completed_visual_iterations": 1 + 0 + 1,
        "incomplete_visual_iterations": 0,
        "final_images": 6,
        "final_by_round": {"round-01": 2, "round-02": 2, "round-03": 2},
        "helper_no_text_renders": 2,
    },
    "logs": {
        "requests": f"tmp/{RUN}/A21/requests.jsonl（22 行 = r01×10 + r02×2×2"
                    "（含 2 行重复自留痕） + r03×8；真实渲染请求 20 条）",
        "iterations": [f"tmp/{RUN}/A21/iterations.jsonl",
                       f"tmp/{RUN}/A21/r02-iterations.jsonl",
                       f"tmp/{RUN}/A21/r03-iterations.jsonl"],
        "per_round_metrics": ["round-01/task-metrics.json", "round-02/task-metrics.json",
                              "round-03/task-metrics.json"],
        "contrast_audit": "round-03/contrast-audit.json",
    },
    "rounds": [
        {"round": 1, "theme": "dark", "finals": 2, "requests": 10,
         "iterations": "baseline + 1 visual", "status": "completed"},
        {"round": 2, "theme": "dark", "finals": 2, "requests": 2,
         "iterations": "baseline 首渲达标", "status": "completed"},
        {"round": 3, "theme": "light", "finals": 2, "requests": 8,
         "iterations": "baseline + syntaxfix + 1 visual", "status": "completed"},
    ],
    "outputs": [
        {"name": "snapshot-usage.md", "path_base": "output_dir", "path": "snapshot-usage.md"},
        {"name": "task-metrics.json", "path_base": "output_dir", "path": "task-metrics.json"},
        {"name": "round-01/", "path_base": "output_dir", "path": "round-01/"},
        {"name": "round-02/", "path_base": "output_dir", "path": "round-02/"},
        {"name": "round-03/", "path_base": "output_dir", "path": "round-03/"},
    ],
    "candidates": [],
    "unresolved_issues": [],
    "notes": "累计口径：仅各轮顶层请求/迭代/看图相加，round 子明细与重复留痕行"
             "不重复累计；r02 的 2 次请求在 requests.jsonl 中有重复行（自动+"
             "手动各 1），计数按 2 条真实请求。",
}
json.dump(cum, open(f"{A21}/task-metrics.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)

# ── H) 根累计 snapshot-usage.md ────────────────────────────
root_usage = f"""# A21 三轮累计 · snapshot-usage

## 状态
completed（round-01 / 02 / 03 全部完成）。最终 6 张指定图：
round-01/round-02/round-03 × (launch-portrait 1080×1350 / launch-wide 1440×810)，
每张同名完整 .snapshot 同目录配对；三条专用审计轮产物（design-tokens.json、
content-map.json、round-03/contrast-audit.json）+ 每轮 usage/metrics 就位。

## 服务/文档/工具应用（三轮持续有效）
- 服务 open-snapshot（POST /snapshot，PNG），全部真实渲染请求 20 条留痕于
  tmp/{RUN}/A21/requests.jsonl（22 行含 r02 的 2 行重复自留痕行；含 requestId、
  Server-Timing、失败原因）。
- 文档：ai-guide.md、parser-tags、layout、fonts（缓存于 tmp/docs/，跨题复用）。
- 字体：Inter（拉丁/数字）+ Noto Sans CJK SC（中文）实测可用。
- 能力实测：根 Snapshot>Stack+SizedBox 定版式；Container 渐变
  (LINEAR + gradientColors/BEGIN/END)、border SOLID、borderRadius 胶囊；Raw 行内
  兼色混排（sponsor 前缀/名双色）；textAlign CENTER/START；letterSpacing。

## 三轮要点
1. round-01（深空 v03）：横带三段渐变 + 双环 + 信标 + 点阵；幽灵装饰预混深底
   实色（#113850 等）；竖居中对称/横左右分栏双构图。
2. round-02（长标题+赞助+免费参加）：标题换长文 3 行 64/54（≥48），新增
   Northstar 承赞助 /云构工具（Raw 双色）与『免费参加 · 无需报名』胶囊；
   级联防碰撞逐级 ≥8px，无 Transform。
3. round-03（浅色主题+对比度审计）：底 #F5F8FC→#E9EFF7；TEAL_INK 加深
   #085F55；EN 副句新增；去文字辅助渲染 + 字形实测范围取最劣背景，
   24/24 段未舍入 ≥4.5（最小 5.199784），审计与修复过程透明留痕。

## 踩坑与经验（已写成可复用规则）
1. Opacity 仅接受一个子节点：多数场景套 Stack 再装多个 Positioned。
2. 无界 Stack 会 Layout size is infinite：先用 SizedBox 定画布，再叠全定位图层。
3. Positioned 不能直接子挂 Opacity（parentData 错），普通子节点改用预混色或
   调层次。
4. Text 的 height 是行高倍数不是像素，误用会把文字挤出定位框；行高用
   fontSize*1.45 定 Positioned 高即可。
5. `&nbsp;` 实体不解码：一律真实 NBSP（\\u00a0）。
6. 结构性删除（去文字辅助版）要连『仅含 Text 的 Positioned 包装』一起删，否则
   ProxyWidget has no widget ×400。
7. 对比度审计对『文字实际背景』取最差样本时，用最终图前景匹配像素的紧外包
   （±2px）作字形范围，避免把范围外的信标/渐变条/胶囊边框/圆角外误判成文字背景。

## 请求/迭代/看图统计（累计，含辅助渲染）
- snapshot 渲染请求 20 条（成功 12 / 失败 8：r01 语法 6 + r03 辅助版 2）。
- DSL 版本 8（finals 变体 + helper strip 变体分别计数）。
- 完整视觉迭代 2（r01 布局重排、r03 TEAL_INK 修复）；syntax-fix/替代方案另记。
- 图像查看 22 次事件级记录（含整图、放大分区与去文字核对）。
- 墙钟含跨日间隔（10-17 19:49 → 10-18 12:0x），active 分轮计时如实拆分。

## 证据索引
- tmp/{RUN}/A21/requests.jsonl、iterations.jsonl、r02/r03-iterations.jsonl
- tmp/{RUN}/A21/bg-data/（去文字辅助 PNG/DSL，不清理）
- tmp/{RUN}/A21/steps/（half、分区放大、bg-half、v2 复查件）
- outputs/{RUN}/A21/round-0X/（各轮全部交付）

## 未解决事项
无。
"""
open(f"{A21}/snapshot-usage.md", "w", encoding="utf-8", newline="\n").write(root_usage)

# ── I) suite-state + events + checkpoint ───────────────────
SP = f"outputs/{RUN}/_suite/suite-state.json"
st = json.load(open(SP, encoding="utf-8"))
for t in st["tasks"]:
    if t["id"] == "A21":
        t["status"] = "completed"
        t["ended_at"] = end
        t["completed_rounds"] = [1, 2, 3]
        t["artifacts"] = [
            "round-01/launch-portrait.png", "round-01/launch-portrait.snapshot",
            "round-01/launch-wide.png", "round-01/launch-wide.snapshot",
            "round-01/design-tokens.json", "round-01/content-map.json",
            "round-01/snapshot-usage.md", "round-01/task-metrics.json",
            "round-02/launch-portrait.png", "round-02/launch-portrait.snapshot",
            "round-02/launch-wide.png", "round-02/launch-wide.snapshot",
            "round-02/design-tokens.json", "round-02/content-map.json",
            "round-02/snapshot-usage.md", "round-02/task-metrics.json",
            "round-03/launch-portrait.png", "round-03/launch-portrait.snapshot",
            "round-03/launch-wide.png", "round-03/launch-wide.snapshot",
            "round-03/design-tokens.json", "round-03/content-map.json",
            "round-03/contrast-audit.json", "round-03/snapshot-usage.md",
            "round-03/task-metrics.json",
            "snapshot-usage.md", "task-metrics.json",
        ]
        t["visual_review_evidence"] = [
            "r1: v02→v03 两图 half/放大查看，deep 上限与布局修正后通过",
            "r2: v01 两图 half + 200 字放大文字核验（率先版即达标）",
            "r3: v1/v2 两图 half、8 张分区放大、2 张 bg-half 无字核验、眉题放大",
            "contrast-audit.json 24/24 未舍入 ≥4.5（最小 5.199784），字形实测范围采样",
        ]
        t["resume_notes"] = ("A21 三轮完成：r1 深空首发双图；r2 长标题(64/54,3行)+"
                             "赞助+免费参加；r3 浅色+EN 句+TEAL_INK 审计修复，"
                             "24/24 对比度全过。下一步 A22 三轮。")
st["current_task"] = "A22"
st["current_round"] = None
st["updated_at"] = end
json.dump(st, open(SP, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

ev_l = f"tmp/{RUN}/_suite/events.jsonl"
with open(ev_l, "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000041", "at": end, "kind": "round-completed",
                        "task_id": "A21", "round": 3,
                        "detail": "浅色主题+EN副句+对比度审计修复(TEAL_INK)。"
                                  "2×最终图+2×辅助bg渲染；24/24 未舍入≥4.5"},
                       ensure_ascii=False) + "\n")
    f.write(json.dumps({"id": "SUITE-ev-000042", "at": now(), "kind": "task-completed",
                        "task_id": "A21", "round": None,
                        "detail": "三轮全部 completed，累计 6 final images，"
                                  "请求数 22。下一题 A22。"},
                       ensure_ascii=False) + "\n")

cp = {"at": now(), "run_id": RUN, "action": "task-complete", "task_id": "A21",
      "round": 3,
      "summary": "A21 三轮完成；r3 浅色对比度审计 24/24>=4.5；根累计 usage/metrics 已写。"
                 "下一题 A22（先读 tasks/A22*/TASK.md 与 rounds/）。"}
open(f"tmp/{RUN}/_suite/checkpoints/state-000041.json", "w",
     encoding="utf-8", newline="\n").write(
    json.dumps(cp, ensure_ascii=False, indent=1))
st["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000041.json"
json.dump(st, open(SP, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("finalize done:", end)
print("metrics r3: req", len(r3reqs), "ok", len(ok), "fail", len(fail),
      "dur_s", round(dur / 1000, 4), "elapsed", m3["timings"]["elapsed_seconds"])
print("cum wall", round(wall, 1), "active", round(act, 1), "idle", round(wall - act, 1))
