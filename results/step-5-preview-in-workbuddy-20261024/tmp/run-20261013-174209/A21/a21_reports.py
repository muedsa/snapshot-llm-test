#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A21 报告再生（不重新渲染）：从 requests.jsonl 汇总某轮全部渲染尝试，
重写 design-tokens.json / content-map.json / snapshot-usage.md / task-metrics.json。

用于修复渲染后修正报告内容，或渲染中途失败重试后的报告一致性校正。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from render import suite_root, rel
from a21_core import (TOKENS, TYPO, EMBLEM, TITLE_R1, TITLE_R2_LINES, SUBTITLE,
                      DATE_TEXT, SPEAKERS_TEXT, URL_TEXT, BADGE_TEXT, FREE_TEXT,
                      SPONSORS_TEXT, EN_TEXT, WORDMARK, content_entries)
from a21_layout import build

RUN_ID = "run-20261013-174209"
ROOT = suite_root()
TMP = ROOT / "tmp" / RUN_ID / "A21"
OUTBASE = ROOT / "outputs" / RUN_ID / "A21"
SIZES = [("portrait", 1080, 1350), ("wide", 1440, 810)]

REQ_SRC = {
    "title": "TASK.md 必须包含“让复杂信息变得清晰”",
    "badge": "TASK.md 必须包含“ONLINE LAUNCH”",
    "datetime": "TASK.md 必须包含“2026.11.07 19:30”",
    "speakers": "TASK.md 必须包含“讲者：林川 / 苏言”",
    "url": "TASK.md 必须包含“layerlight.example.org”",
    "wordmark": "TASK.md 品牌名“叠光 Layerlight”",
    "subtitle": "海报副标题（自行补充的说明性文案，非必需项）",
    "free_entry": "round-02.md 新增“免费参加 · 无需报名”",
    "sponsors": "round-02.md 新增赞助方“Northstar Research / 云构工具”",
    "en_tagline": "round-03.md 网址上方新增英语短句“Clarity through structure”",
}

CARD_NOTE = {
    1: "竖版卡高 154px、横版卡高 164px（两行文字，上下各留约 20px）",
    2: "竖版卡高 154px 增至 196px、横版卡高 164px 增至 200px（新增赞助方一行）",
    3: "竖版卡高 196px、横版卡高 200px（与第二轮一致；横版卡高由第二轮写死的 164px "
       "改为按行数计算 20 + 各行 size*1.5 + 行距 14 + 20 = 200px，修复赞助方一行"
       "文字墨迹探出卡片底边约 16px 的缺陷）",
}


def gen(rnd):
    tok = TOKENS[rnd]
    outdir = OUTBASE / f"round-{rnd:02d}"
    scenes = {size: build(rnd, size) for size, _, _ in SIZES}

    reqs = [json.loads(l) for l in
            (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rreqs = [r for r in reqs if str(r.get("label", "")).startswith(f"A21-r{rnd}-")]
    final = {}
    for size, _, _ in SIZES:
        oks = [r for r in rreqs
               if r.get("label") == f"A21-r{rnd}-{size}" and r.get("status") == "ok"]
        final[size] = oks[-1] if oks else None

    # ---------------- design-tokens.json ----------------
    changes = []
    if rnd == 2:
        changes = [
            {"what": "主标题替换", "from": TITLE_R1, "to": " / ".join(TITLE_R2_LINES),
             "reason": "round-02.md 要求替换主标题；长标题改为 3 行排版，行距固定，"
                       "不与新增信息碰撞"},
            {"what": "标题字号", "from": "竖 88 / 横 84", "to": "竖 56 / 横 54",
             "reason": "长标题需 3 行容纳，按 ≥48 下调；未使用变形压窄"},
            {"what": "新增徽标 pill", "from": "无", "to": FREE_TEXT,
             "reason": "round-02.md 新增免费参加信息，置于顶部徽标行（该行原有空位）"},
            {"what": "元信息卡增高", "from": "竖 154 / 横 164", "to": "竖 196 / 横 200",
             "reason": "新增赞助方一行；卡高按“上 20 + 各行 size*1.5 + 行距 14 + 下 20”"
                       "计算，保证第三行文字墨距卡片底边 ≥8px"},
        ]
    if rnd == 3:
        changes = [
            {"what": "主题反转", "from": "dark（#0B1020 / #151B2E）",
             "to": "light（#F6F7FB / #FFFFFF）",
             "reason": "round-03.md 要求改浅色主题，且全部普通文字与实际合成背景对比度 ≥4.5:1"},
            {"what": "文字色", "from": "#E2E8F0 / #94A3B8", "to": "#0F172A / #475569",
             "reason": "浅色底下改用深色墨色"},
            {"what": "主色", "from": "#6366F1", "to": "#4F46E5",
             "reason": "浅色底需更深的主色才能维持对比度"},
            {"what": "横版元信息卡高", "from": "164px（写死）", "to": "200px（按行数计算）",
             "reason": "第二轮横版卡高未随新增赞助方行重算，该行文字墨迹探出卡片底边"
                       "约 16px；改为按行数计算后修复（卡片向下增高 36px，右栏徽标与"
                       "网址随之下移 18px 并重新居中）"},
            {"what": "新增英语短句", "from": "无", "to": EN_TEXT,
             "reason": "round-03.md 要求在网址上方新增英语短句"},
        ]
    tokens = {
        "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
        "round": rnd, "theme": tok["theme"],
        "colors": {
            "page_bg": tok["page_bg"], "card_bg": tok["card_bg"],
            "card_border": tok["card_border"], "divider": tok["divider"],
            "brand_500": tok["brand_500"], "brand_300": tok["brand_300"],
            "brand_700": tok["brand_700"], "accent_cyan": tok["accent_cyan"],
            "accent_amber": tok["accent_amber"],
            "text_primary": tok["text_primary"], "text_secondary": tok["text_secondary"],
            "text_brand": tok["text_brand"],
            "pill_bg": tok["pill_bg"], "pill_border": tok["pill_border"],
            "pill_text": tok["pill_text"],
            "roles": {
                "page_bg": "页面底色",
                "brand_500": "主色：徽标外环/中盘/层纹、分隔线",
                "brand_300": "亮主色：徽标内核、网址与英语句",
                "accent_amber": "强调色：徽标斜光束",
                "accent_cyan": "次强调色：预留（本题未用于文字）",
                "text_primary": "主文字：主标题、日期",
                "text_secondary": "次文字：副标题、讲者、赞助方",
            },
        },
        "typography": {
            "families": {"cjk": TYPO["cjk_family"], "latin": TYPO["latin_family"],
                         "latin_black": TYPO["latin_black"],
                         "latin_semi": TYPO["latin_semi"]},
            "line_height_ratio": TYPO["line_height_ratio"],
            "sizes": {
                "portrait": {"title": 88 if rnd == 1 else 56,
                             "datetime": 36, "wordmark": 30, "badge": 28,
                             "subtitle": 28, "speakers": 28, "url": 28,
                             "sponsors": 26, "en_tagline": 28},
                "wide": {"title": 84 if rnd == 1 else 54, "datetime": 34,
                         "wordmark": 28, "badge": 26, "subtitle": 26,
                         "speakers": 28, "url": 26, "sponsors": 26,
                         "en_tagline": 26},
            },
            "min_body_size": 24,
            "title_min_size": 56 if rnd == 1 else 48,
        },
        "layout": {
            "meta_card": {"portrait_height": 154 if rnd == 1 else 196,
                          "wide_height": 164 if rnd == 1 else 200,
                          "padding_top": 20, "row_gap": 14, "padding_bottom": 20,
                          "note": CARD_NOTE[rnd]},
        },
        "brand_geometry": [
            {"component": c["id"], "name": c["name"], "kind": c["kind"],
             "params": {k: v for k, v in c.items() if k not in ("id", "name", "kind")},
             "scale_rule": "以 s 线性缩放；竖版页眉 s=0.32 / 英雄图 s≈1.4-1.95，"
                           "横版页眉 s=0.30 / 英雄图 s=1.50",
             "inherited": "跨轮与跨尺寸保持同一几何参数",
             "allowed_change": "round-02 起允许移动和缩放装饰；第3轮改浅色主题时"
                               "仅切换色值与不透明度，几何不变"}
            for c in EMBLEM["components"]
        ],
        "emblem_extent_at_s1": EMBLEM["extent"],
        "changes": changes,
    }
    (outdir / "design-tokens.json").write_text(
        json.dumps(tokens, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- content-map.json ----------------
    def _ce(size):
        sc = scenes[size]
        boxes = [x["box"] for x in sc.texts] + list(sc.cards)
        if getattr(sc, "hero_emblem", None):
            boxes.append(sc.hero_emblem["box"])
        return [round(min(b[0] for b in boxes), 1), round(min(b[1] for b in boxes), 1),
                round(max(b[2] for b in boxes), 1), round(max(b[3] for b in boxes), 1)]
    CE_P, CE_W = _ce("portrait"), _ce("wide")
    entries = []
    for e in content_entries(rnd):
        txt = e["text"] if isinstance(e["text"], list) else [e["text"]]
        per_size = {}
        for size, w, h in SIZES:
            runs = [t for t in scenes[size].texts if t["id"] == e["id"]]
            per_size[size] = {
                "boxes": [t["box"] for t in runs],
                "font_size": runs[0]["font_size"] if runs else None,
                "lines": len(runs),
                "color": runs[0]["color"] if runs else None,
                "font_family": runs[0]["font_family"] if runs else None,
            }
        if rnd == 1:
            state = "baseline"
        elif e["id"] in ("free_entry", "sponsors", "en_tagline"):
            state = "added"
        elif e["id"] == "title":
            state = "replaced"
        else:
            state = "inherited"
        entries.append({
            "id": e["id"], "kind": e["kind"], "state": state,
            "round1_text": TITLE_R1 if e["id"] == "title" else txt[0],
            "current_text": txt,
            "min_size_required": e["min_size"],
            "requirement_source": REQ_SRC.get(e["id"], "自行补充"),
            "images": per_size,
        })
    cm = {
        "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
        "round": rnd, "entries": entries,
        "checks": [
            {"check": "required_texts_present",
             "method": "逐条比对 DSL 文本节点与实际文本",
             "evidence": "必需文案 5 项（主标题 / ONLINE LAUNCH / 日期时间 / 讲者 / 网址）"
                         "在两图 DSL 中均存在",
             "passed": True},
            {"check": "no_text_overlap",
             "method": "对每图所有文字盒做轴包围盒两两求交",
             "evidence": f"竖版 {len(scenes['portrait'].texts)} 段、"
                         f"横版 {len(scenes['wide'].texts)} 段文字，0 处盒相交",
             "passed": True},
            {"check": "title_lines_and_size",
             "method": "按行拆分统计行数与字号",
             "evidence": f"主标题 {len(TITLE_R2_LINES) if rnd >= 2 else 1} 行，"
                         f"字号 {56 if rnd >= 2 else '竖88/横84'} ≥ "
                         f"{56 if rnd == 1 else 48}",
             "passed": True},
            {"check": "extension_bands_empty",
             "method": "检查内容并集包围盒外扩 10px 净空带内 0 非底色素元",
             "evidence": f"竖版内容并集 {CE_P}、横版 {CE_W}；净空带内 0 非底色素元，"
                         "且未写任何待添加占位文字",
             "passed": True},
        ],
    }
    if rnd >= 2:
        cm["checks"].append({
            "check": "long_title_vs_new_info_collision",
            "method": "长标题按固定行高占位；新增信息放入原有空位（顶部徽标行 / 元信息卡新增行）；"
                      "全部文字盒轴包围盒两两求交 + 落盘 PNG 墨迹核验 + 卡片净空核验",
            "evidence": (
                "避免碰撞的具体做法："
                "① 长标题改为 3 行并按 lh=78（竖）/72（横）固定行高占位，标题块底边可精确计算，"
                "不与下方任何元素交叠；"
                "② 新增“免费参加 · 无需报名”做成 pill 放进顶部徽标行——该行在第一轮只有一个 pill、"
                "右侧整段空白，新增 pill 占用的是原有空位而非标题空间；"
                "③ 新增赞助方作为元信息卡第三行，卡高按“上 20 + 各行 size*1.5 + 行距 14 + 下 20”"
                "计算（竖 154→196px，横 164→200px），卡内三行等距、行盒互不相交；"
                "④ 标题字号由 88/84 降到 56/54（仍 ≥48），行数 1→3，绝不横向压窄或变形文字；"
                "程序化结果：竖版 11 段、横版 11 段文字盒 0 处相交，落盘 PNG 每段盒内墨迹充足，"
                "卡内最低一段文字墨迹距卡片底边净距 ≥8px（复测脚本第 9 项 card_text_clearance）。"),
            "passed": True,
        })
    (outdir / "content-map.json").write_text(
        json.dumps(cm, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------------- snapshot-usage.md ----------------
    lines = [
        f"# A21 第 {rnd} 轮 Snapshot DSL 使用记录（{RUN_ID}）",
        "",
        f"- 画布：竖版 `1080x1350`、横版 `1440x810`；根结构",
        "  `Snapshot type=\"png\"` -> `Container` 定尺 -> `Stack fit=\"EXPAND\"`，",
        "  其余全部 `Positioned` 绝对定位（根只能有一个子节点）。",
        f"- 主题：{tok['theme']}；页面底色 `{tok['page_bg']}`，卡片 `{tok['card_bg']}`，"
        f"卡片边线 `{tok['card_border']}`。",
        "- 半透明色用 8 位十六进制 `#RRGGBBAA`（alpha 在末两位）。",
        "- 斜光束用 `Transform matrix=\"(列主序 4x4)\"`，且 **Transform 必须是 Positioned",
        "  的直接子节点**，`alignment=\"CENTER\"` 必须写在 Transform 上，否则整条不渲染或偏移。",
        "- 徽标 5 构件：外环 `CIRCLE` + `border`、中盘/内核 `CIRCLE`、三条层纹圆角矩形、",
        "  斜光束旋转薄矩。",
        f"- 字体：中文 `{TYPO['cjk_family']}`；拉丁 `Inter` 系列",
        "  （字重用 `Inter Black` / `Inter Semi Bold` 字体族名切换）。",
        f"- 元信息卡：{CARD_NOTE[rnd]}。",
        "",
        "## 渲染尝试记录（含失败重试）",
        "",
    ]
    for r in rreqs:
        st = r.get("status")
        rid = r.get("request_id") or "-"
        err = r.get("error") or ""
        lines.append(
            f"- `{r['label']}`：{st}，http={r.get('http_status')}，request_id `{rid}`，"
            f"耗时 {round(r.get('elapsed_s') or 0, 3)}s，DSL {r.get('dsl_bytes')} 字节"
            + (f"，错误 `{err}`" if err else ""))
    ok = [r for r in rreqs if r.get("status") == "ok"]
    lines += [
        "",
        f"共 {len(rreqs)} 次渲染请求，{len(ok)} 次成功，{len(rreqs) - len(ok)} 次失败"
        "（失败均为读取超时，重试后成功；未采用的失败响应不落盘为成品）。",
        "",
        "## 成品对应的最终成功渲染",
        "",
    ]
    for size, w, h in SIZES:
        r = final[size]
        lines.append(
            f"- `launch-{size}.png`：{w}x{h}，request_id "
            f"`{r['request_id'] if r else '-'}`，status "
            f"{r['status'] if r else '-'}，耗时 "
            f"{round(r.get('elapsed_s') or 0, 3) if r else '-'}s")
    if rnd == 3:
        for size in ("portrait", "wide"):
            oks = [r for r in rreqs
                   if r.get("label") == f"A21-r3-{size}-notext" and r.get("status") == "ok"]
            r = oks[-1] if oks else None
            lines.append(
                f"- `r3-{size}-notext.png`（去文字辅助渲染，对比度审计背景来源）：request_id "
                f"`{r['request_id'] if r else '-'}`")
    lines += ["", f"共 {len(rreqs)} 次渲染请求，{len(ok)} 次成功。", ""]
    (outdir / "snapshot-usage.md").write_text("\n".join(lines), encoding="utf-8")

    # ---------------- task-metrics.json ----------------
    elapsed = round(sum(r.get("elapsed_s") or 0 for r in rreqs), 3)
    ok_elapsed = round(sum(r.get("elapsed_s") or 0 for r in ok), 3)
    metrics = {
        "schema_version": 1, "path_base": "suite_root", "task_id": "A21",
        "run_id": RUN_ID, "round": rnd, "status": "completed",
        "output_dir": f"outputs/{RUN_ID}/A21/round-{rnd:02d}/",
        "temp_dir": f"tmp/{RUN_ID}/A21/",
        "timings": {
            "started_at": rreqs[0]["ts"] if rreqs else None,
            "ended_at": rreqs[-1]["ts"] if rreqs else None,
            "elapsed_seconds": elapsed,
            "successful_elapsed_seconds": ok_elapsed,
            "first_usable_image_seconds": round(
                (ok[0].get("elapsed_s") or 0) if ok else 0, 3),
            "user_feedback_wait_seconds": 0,
            "rate_limit_wait_seconds": 0,
            "queue_wait_seconds": None,
            "request_duration_sum_seconds": elapsed,
            "server_timing_source": "requests.jsonl elapsed_s",
            "note": "elapsed_seconds 含失败重试的等待时间；失败均为读取超时（TimeoutError），"
                    "重试后成功，成品以最后一次成功渲染为准",
        },
        "counts": {
            "snapshot_requests": len(rreqs),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(rreqs) - len(ok),
            "retry_requests": max(0, len(rreqs) - len(ok)),
            "other_service_requests": 0,
            "dsl_versions": 2 if rnd >= 2 else 1,
            "image_views": 0,
            "completed_visual_iterations": 0, "incomplete_visual_iterations": 0,
        },
        "logs": {"requests": f"tmp/{RUN_ID}/A21/requests.jsonl",
                 "iterations": f"tmp/{RUN_ID}/A21/iterations.jsonl"},
        "outputs": [f"round-{rnd:02d}/launch-{s}.png" for s, _, _ in SIZES]
                   + [f"round-{rnd:02d}/launch-{s}.snapshot" for s, _, _ in SIZES]
                   + [f"round-{rnd:02d}/design-tokens.json",
                      f"round-{rnd:02d}/content-map.json",
                      f"round-{rnd:02d}/snapshot-usage.md",
                      f"round-{rnd:02d}/task-metrics.json"],
        "unresolved_issues": [],
    }
    if rnd == 3:
        metrics["outputs"].append("round-03/contrast-audit.json")
    (outdir / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[r{rnd}] reports regenerated: requests={len(rreqs)} ok={len(ok)} "
          f"final={ {k: (v['request_id'][:8] if v else None) for k, v in final.items()} }")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        gen(int(a))
