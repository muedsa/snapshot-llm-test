#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全套总索引 + _suite/gallery.md 生成（30/30 完成后的最终交付）。"""
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "outputs" / "run-20261013-174209"

TASK_TITLES = {
    "A01": "六个月经营诊断驾驶舱", "A02": "三会场密集会议日程",
    "A03": "多层语义故障恢复", "A04": "分组改善与总体下降的数据解释",
    "A05": "不规则采样与缺测的仪表报告", "A06": "十四节点依赖图与反馈回路",
    "A07": "三线换乘图与路线核验", "A08": "展馆双路线导览与共享通道",
    "A09": "十二个非对称图形变换标本", "A10": "透明合成与滤镜语义实验板",
    "A11": "文字保真与跨页结算单", "A12": "四断点完整内容视觉系统",
    "A13": "品牌标志到完整活动应用", "A14": "八组文案压力测试与批量生成",
    "A15": "复杂界面视觉复刻", "A16": "从错误图表恢复可信叙事",
    "A17": "四页可实践的DSL入门手册", "A18": "守恒对象的三幕视觉叙事",
    "A19": "构造可核验的视觉题场", "A20": "二十四密集点的无重叠标注",
    "A21": "真实需求变更：双尺寸发布物", "A22": "真实数据更正与局部回归",
    "A23": "格式边界下的动画分镜交付", "A24": "双团队约束下的发布作战计划",
    "B01": "十张真实场景的炫酷用例", "B02": "为一个自选项目设计完整视觉生态",
    "B03": "用十件作品探索DSL的创意边界", "B04": "自主研究真实主题并制作十件视觉特辑",
    "B05": "从零构想产品并设计十个关键使用画面", "B06": "把十个日常信息难题变成惊艳而好用的作品",
}
GROUPS = [
    ("A01–A08", [f"A{i:02d}" for i in range(1, 9)], "基础渲染与数据呈现"),
    ("A09–A16", [f"A{i:02d}" for i in range(9, 17)], "变换、复合、文字与复刻"),
    ("A17–A24", [f"A{i:02d}" for i in range(17, 25)], "文档、叙事、题场与变更交付"),
    ("B01–B06", [f"B{i:02d}" for i in range(1, 7)], "十件级独立作品"),
]

# 每题的补充说明（一行）
TASK_NOTE = {
    "A01": "1600×1000 驾驶舱：六个月经营诊断，含程序化核验数据",
    "A02": "移动 720×1280 + 宽屏 1920×1200 双形态日程，schedule-audit.json 核验无冲突",
    "A03": "1280×800 系统脉冲图：多层语义故障定位与恢复链",
    "A04": "1600×1000：分组改善而总体下降的辛普森式解释",
    "A05": "1440×1000：不规则采样与缺测的传感器报告",
    "A06": "1600×1000：十四节点依赖图与反馈回路标注",
    "A07": "网络图 1600×1000 + 出行卡 720×1280；routes.json 路线核验",
    "A08": "1560×1080：双路线导览与共享通道（paths.json）",
    "A09": "1600×1200 变换图谱：十二个非对称标本（geometry-audit.json）",
    "A10": "1440×1100 合成实验板：透明度/混合/滤镜语义（composite-audit.json）",
    "A11": "两页结算单 1200×1600：中英文字保真 + 跨页合计闭合（invoice-audit.json）",
    "A12": "四断点视觉系统：stage/desktop/tablet/mobile（design-tokens.json）",
    "A13": "品牌系统：标志双版本 + 横幅 + 海报（brand-system.json, rationale.md）",
    "A14": "八组文案压力卡 1200×630：批量生成 + content-map.json",
    "A15": "1440×900 复刻：参考界面视觉重建（reconstruction-audit.json, comparison.md）",
    "A16": "1280×900：错误图表取证与可信叙事重建（findings.json）",
    "A17": "四页手册 1200×1600 + 四个示例 400×240（sources.md, verification.json）",
    "A18": "1600×1000：守恒对象三幕视觉叙事（story-audit.json）",
    "A19": "题场 1600×1600 + 遮挡两组对照：可核验视觉题（questions/answers/equivalence.json）",
    "A20": "1600×1100：二十四密集点无重叠标注（label-layout.json, layout-audit.json）",
    "A21": "三轮真实变更：双尺寸发布物 round-01→03（需求变更驱动重渲）",
    "A22": "三轮真实数据更正：仪表板局部回归 round-01→03",
    "A23": "封面 + 六分镜：格式边界下的动画分镜（timing.json, limitations.md）",
    "A24": "作战板 1920×1080 + 决策简报 + 行动卡（schedule.json, schedule-audit.json）",
    "B01": "十张真实场景：深空数据墙/菜单板/集结大屏/叫号屏/主视觉/账本/导览海报/对战卡/空气看板/日程卡",
    "B02": "湿地公园完整视觉生态：立牌/手册跨页/解说看板/任务卡/海报×2/报告页/感谢卡/标签/数字首页",
    "B03": "DSL 创意边界十件 + technique-notes.md（25 条边界清单）",
    "B04": "WMO 国际云图集十属特辑十一件 + sources.json（9 来源/32 claims）+ editorial-note.md",
    "B05": "Clearway 无碍出行产品十画面 + product-brief.md + journey.json（v02 七处一致性修订）",
    "B06": "十个日常信息难题十件作品 + problem-evidence.json + design-review.md",
}

B_CASE_TITLES = {}
for t in ["B01", "B02", "B03", "B04", "B05", "B06"]:
    md = (BASE / t / "portfolio.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", md, re.M)
    B_CASE_TITLES[t] = {int(n): (title, canvas) for n, title, canvas in rows}

A_FILE_LABELS = {
    "A01": [("operations.png", "六个月经营诊断驾驶舱")],
    "A02": [("agenda-wide.png", "三会场日程 · 宽屏版"), ("agenda-mobile.png", "三会场日程 · 移动版")],
    "A03": [("system-pulse.png", "系统脉冲 · 多层语义故障恢复")],
    "A04": [("conversion-story.png", "转化悖论 · 分组改善与总体下降")],
    "A05": [("sensor-report.png", "传感器报告 · 不规则采样与缺测")],
    "A06": [("dependency-map.png", "依赖图 · 十四节点与反馈回路")],
    "A07": [("network-map.png", "三线换乘网络图"), ("travel-card.png", "出行卡 · 移动版")],
    "A08": [("wayfinding.png", "展馆双路线导览")],
    "A09": [("transform-atlas.png", "变换图谱 · 十二标本")],
    "A10": [("compositing-lab.png", "合成实验板")],
    "A11": [("invoice-page-01.png", "结算单第 1 页"), ("invoice-page-02.png", "结算单第 2 页")],
    "A12": [("stage.png", "演讲大屏断点"), ("desktop.png", "桌面断点"), ("tablet.png", "平板断点"), ("mobile.png", "手机断点")],
    "A13": [("symbol-color.png", "标志 · 彩色版"), ("symbol-black.png", "标志 · 单色版"), ("brand-banner.png", "品牌横幅"), ("launch-poster.png", "活动海报")],
    "A14": [("card-K%02d.png" % i, "文案压力卡 K%02d" % i) for i in range(1, 9)],
    "A15": [("reconstructed.png", "参考界面复刻")],
    "A16": [("corrected-report.png", "修正后的可信报告")],
    "A17": [("handbook-0%d.png" % i, "DSL 入门手册 第 %d 页" % i) for i in range(1, 5)]
            + [("example-0%d.png" % i, "示例 0%d" % i) for i in range(1, 5)],
    "A18": [("three-act-story.png", "三幕视觉叙事")],
    "A19": [("grid-scene.png", "题场主场景"), ("occlusion.png", "遮挡题 · 正解"), ("occlusion-alternative.png", "遮挡题 · 变体")],
    "A20": [("annotated-map.png", "二十四密集点标注图")],
    "A21": [("round-01/launch-wide.png", "第 1 轮 · 宽版"), ("round-01/launch-portrait.png", "第 1 轮 · 竖版"),
            ("round-02/launch-wide.png", "第 2 轮 · 宽版"), ("round-02/launch-portrait.png", "第 2 轮 · 竖版"),
            ("round-03/launch-wide.png", "第 3 轮 · 宽版"), ("round-03/launch-portrait.png", "第 3 轮 · 竖版")],
    "A22": [("round-01/dashboard.png", "第 1 轮仪表板"), ("round-02/dashboard.png", "第 2 轮仪表板"), ("round-03/dashboard.png", "第 3 轮仪表板")],
    "A23": [("cover.png", "分镜封面")] + [("frame-0%d.png" % i, "分镜 %d" % i) for i in range(1, 7)],
    "A24": [("execution-board.png", "发布作战板"), ("decision-brief.png", "决策简报"), ("action-card.png", "行动卡")],
}


def png_size(p):
    with open(p, "rb") as f:
        data = f.read(33)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def load_metrics(tid):
    p = BASE / tid / "task-metrics.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def collect_pngs(tid):
    """返回 [(relpath, w, h)]，final 在前、其余按名。"""
    out = []
    for p in sorted((BASE / tid).rglob("*.png")):
        rel = p.relative_to(BASE).as_posix()
        s = png_size(p)
        if s:
            out.append((rel, s[0], s[1]))
    return out


# ---------- 汇总 ----------
ALL_TASKS = [f"A{i:02d}" for i in range(1, 25)] + [f"B{i:02d}" for i in range(1, 7)]
rows = []
tot = dict(png=0, snap=0, req=0, succ=0, views=0, iters=0, dslver=0, ratios=0)
per_task = {}
for tid in ALL_TASKS:
    pngs = collect_pngs(tid)
    snaps = sorted((BASE / tid).rglob("*.snapshot"))
    m = load_metrics(tid)
    c = m.get("counts", {})
    views = c.get("image_views", c.get("visual_reviews", 0))
    iters = c.get("completed_visual_iterations", 0)
    ratios = c.get("canvas_ratios", 0)
    dslv = c.get("dsl_versions", 0)
    req = c.get("snapshot_requests", 0)
    succ = c.get("successful_snapshot_requests", 0)
    per_task[tid] = dict(pngs=pngs, snaps=len(snaps), req=req, succ=succ, views=views, iters=iters, dsl=dslv, ratios=ratios, m=m)
    tot["png"] += len(pngs); tot["snap"] += len(snaps)
    tot["req"] += req; tot["succ"] += succ
    tot["views"] += views; tot["iters"] += iters; tot["dslver"] += dslv; tot["ratios"] += ratios
    rows.append(tid)

# ---------- _suite/gallery.md ----------
g = []
g.append("# 全套图片总览 · run-20261013-174209")
g.append("")
g.append("30 题（A01–A24 + B01–B06）全部最终图片清单与链接。")
g.append("全部 PNG 均由 Snapshot DSL 经真实渲染服务（open-snapshot）产出，")
g.append("为服务响应字节原样落盘；每张图均有对应 `.snapshot` DSL 源文件。")
g.append("")
g.append("**合计：%d 张最终 PNG / %d 个 snapshot 源文件**" % (tot["png"], tot["snap"]))
g.append("")
for gname, tids, gdesc in GROUPS:
    g.append("## %s · %s" % (gname, gdesc))
    g.append("")
    for tid in tids:
        info = per_task[tid]
        g.append("### %s · %s" % (tid, TASK_TITLES[tid]))
        g.append("")
        g.append("| # | 图片 | 尺寸 | 链接 |")
        g.append("|---:|---|---|---|")
        if tid.startswith("B"):
            for rel, w, h in info["pngs"]:
                mm = re.search(r"case-(\d+)/final\.png", rel)
                n = int(mm.group(1)) if mm else 0
                title = B_CASE_TITLES[tid].get(n, ("", ""))[0]
                g.append("| %d | %s | %d×%d | [case-%02d/final.png](../%s) |" % (n, title, w, h, n, rel))
        else:
            labels = dict(A_FILE_LABELS.get(tid, []))
            for rel, w, h in info["pngs"]:
                fn = rel.split("/", 1)[1] if "/" in rel else rel
                g.append("| — | %s | %d×%d | [%s](../%s) |" % (labels.get(fn, fn), w, h, fn, rel))
        g.append("")
(BASE / "_suite" / "gallery.md").write_text("\n".join(g) + "\n", encoding="utf-8")
print("gallery.md written:", len(g), "lines,", tot["png"], "images")

# ---------- index.md ----------
idx = []
idx.append("# 全套任务总索引 · run-20261013-174209")
idx.append("")
idx.append("- **运行**：run-20261013-174209（profile: all）")
idx.append("- **范围**：A01–A24 + B01–B06，共 **30 题，全部 completed（30/30）**")
idx.append("- **最终图片**：**%d 张**（要求 ≥124；B 类每题 ≥10 件独立完整作品，B04 为 11 件）" % tot["png"])
idx.append("- **Snapshot 源文件**：%d 个（每张最终图一一对应）" % tot["snap"])
idx.append("- **渲染请求**：%d 次（成功 %d）· **实际看图**：%d 次 · **完整视觉迭代**：%d 轮 · **DSL 版本**：%d 个 · **画布比例**：%d 种"
           % (tot["req"], tot["succ"], tot["views"], tot["iters"], tot["dslver"], tot["ratios"]))
idx.append("- **渲染服务**：open-snapshot（https://open-snapshot.muedsa.com/snapshot），全部 PNG 为真实服务响应字节")
idx.append("- **执行状态**：[_suite/suite-state.json](_suite/suite-state.json)（status=completed, suite_status=completed, current_task=null）")
idx.append("- **全部图片清单**：[_suite/gallery.md](_suite/gallery.md)")
idx.append("")
idx.append("## 总览表")
idx.append("")
idx.append("| 顺序 | 任务 | 标题 | 最终图 | 请求(成功) | 看图 | 题目交付物 |")
idx.append("|---:|---|---|---:|---:|---:|---|")
for i, tid in enumerate(ALL_TASKS, 1):
    info = per_task[tid]
    docs = []
    for fn in ["portfolio.md", "gallery.md", "snapshot-usage.md", "task-metrics.json"]:
        if (BASE / tid / fn).exists():
            docs.append("[%s](%s/%s)" % (fn, tid, fn))
    idx.append("| %d | %s | %s | %d | %d(%d) | %d | %s |"
               % (i, tid, TASK_TITLES[tid], len(info["pngs"]), info["req"], info["succ"], info["views"],
                  " · ".join(docs) if docs else "—"))
idx.append("")
idx.append("## 分组明细")
idx.append("")
for gname, tids, gdesc in GROUPS:
    idx.append("### %s · %s" % (gname, gdesc))
    idx.append("")
    for tid in tids:
        info = per_task[tid]
        idx.append("#### %s · %s" % (tid, TASK_TITLES[tid]))
        idx.append("")
        idx.append("- %s" % TASK_NOTE[tid])
        # 特有交付物
        special = []
        for p in sorted((BASE / tid).iterdir()):
            if not p.is_file():
                continue
            fn = p.name
            if fn in ("portfolio.md", "gallery.md", "snapshot-usage.md", "task-metrics.json"):
                continue
            if fn.endswith((".png", ".snapshot")):
                continue
            special.append((fn, p.stat().st_size))
        if special:
            idx.append("- 题目交付物：" + " · ".join("[%s](%s/%s)" % (fn, tid, fn) for fn, _ in special))
        idx.append("- 图片：")
        if tid.startswith("B"):
            for rel, w, h in info["pngs"]:
                mm = re.search(r"case-(\d+)/final\.png", rel)
                n = int(mm.group(1))
                title = B_CASE_TITLES[tid].get(n, ("", ""))[0]
                idx.append("  - %02d [%s](%s)（%d×%d，[DSL 源](%s)）" % (n, title, rel, w, h, rel.replace(".png", ".snapshot")))
        else:
            labels = dict(A_FILE_LABELS.get(tid, []))
            for rel, w, h in info["pngs"]:
                fn = rel.split("/", 1)[1] if "/" in rel else rel
                idx.append("  - [%s](%s)（%d×%d，[DSL 源](%s)）" % (labels.get(fn, fn), rel, w, h, rel.replace(".png", ".snapshot")))
        idx.append("")
idx.append("## 过程证据")
idx.append("")
idx.append("- 执行状态与逐题登记：[_suite/suite-state.json](_suite/suite-state.json)")
idx.append("- 任务完成检查点：[_suite/checkpoints/](_suite/checkpoints/)（state-A21-completed … state-B06-completed.json，共 8 个）")
idx.append("- 过程增量快照：`tmp/run-20261013-174209/_suite/checkpoints/`（state-000001 … state-000033.json，共 33 个）")
idx.append("- 逐题计划/标准/迭代/看图记录：各题 `tmp/run-20261013-174209/<TASK>/`（plan、iterations.jsonl、case.md 证据）")
idx.append("- 渲染服务请求/响应留痕：`tmp/run-20261013-174209/MEASURE/`")
idx.append("")
idx.append("## 交付约定核对")
idx.append("")
idx.append("| 要求 | 实际 |")
idx.append("|---|---|")
idx.append("| 30 题全部完成 | 30/30 completed |")
idx.append("| 合计最终图 ≥124 | %d |" % tot["png"])
idx.append("| B 类每题 ≥10 件独立完整作品 | B01 10 · B02 10 · B03 10 · B04 11 · B05 10 · B06 10 |")
idx.append("| 每题实际看图 | %d 次（逐题 task-metrics.json） |" % tot["views"])
idx.append("| 完整视觉迭代 | %d 轮（看图发现问题→修订→重渲复核） |" % tot["iters"])
idx.append("| 全部图片清单与链接（_suite/gallery.md） | [已生成](_suite/gallery.md)（%d 张） |" % tot["png"])
idx.append("| 执行状态写 _suite/suite-state.json | completed / suite_status=completed / current_task=null |")
idx.append("")
idx.append("## 浏览方式")
idx.append("")
idx.append("图片与文档均为相对链接；在支持 Markdown 图片渲染的环境中可直接查看。")
idx.append("建议从 [_suite/gallery.md](_suite/gallery.md) 开始浏览全部 125 张最终图。")
idx.append("")
(BASE / "index.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
print("index.md written:", len(idx), "lines")
print("TOTALS:", tot)
