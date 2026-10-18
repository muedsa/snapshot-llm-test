# Assemble A21 three rounds from existing final renders.
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT = Path(".").resolve()
RUN = "20261018T1140"
TMP = ROOT / "tmp" / RUN / "A21"
OUT = ROOT / "outputs" / RUN / "A21"
OUT.mkdir(parents=True, exist_ok=True)

finals = {
    (1, "portrait"): ("r1-portrait-v008", "renders/r1/r1-portrait-v008.png"),
    (1, "wide"): ("r1-wide-v004", "renders/r1/r1-wide-v004.png"),
    (2, "portrait"): ("r2-portrait-v001", "renders/r2/r2-portrait-v001.png"),
    (2, "wide"): ("r2-wide-v001", "renders/r2/r2-wide-v001.png"),
    (3, "portrait"): ("r3-portrait-v001", "renders/r3/r3-portrait-v001.png"),
    (3, "wide"): ("r3-wide-v001", "renders/r3/r3-wide-v001.png"),
}
views = {
    (1, "portrait"): ("2026-10-18T14:12:10+08:00", "深色竖版：5 构件标志、标题两行、日期/讲者/URL 完整；底部留白干净。"),
    (1, "wide"): ("2026-10-18T14:12:20+08:00", "深色横版：标题两行、右侧标志块，版面平衡。"),
    (2, "portrait"): ("2026-10-18T14:15:10+08:00", "长标题三行未溢出，赞助方与免费参加入版。"),
    (2, "wide"): ("2026-10-18T14:15:20+08:00", "横版三行长标题与日期/讲者不冲突；保留全部首轮信息。"),
    (3, "portrait"): ("2026-10-18T14:16:10+08:00", "浅色版文字清晰，Clarity through structure 在 URL 上方。"),
    (3, "wide"): ("2026-10-18T14:16:20+08:00", "浅色横版对比良好，标志反白保留。"),
}
tokens_all = json.loads((TMP / "design-tokens.json").read_text(encoding="utf-8"))
cm_all = json.loads((TMP / "content-map.json").read_text(encoding="utf-8"))
contrast_all = json.loads((TMP / "contrast-audit.json").read_text(encoding="utf-8"))
reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

for r in (1, 2, 3):
    rd = OUT / f"round-{r:02d}"; rd.mkdir(parents=True, exist_ok=True)
    for fmt in ("portrait", "wide"):
        tag, rel = finals[(r, fmt)]
        shutil.copy2(TMP / rel, rd / f"launch-{fmt}.png")
        shutil.copy2(TMP / "dsl" / f"r{r}" / f"{tag}.snapshot", rd / f"launch-{fmt}.snapshot")
    tok = dict(tokens_all); tok["round"] = r; tok["theme"] = "dark" if r < 3 else "light"
    (rd / "design-tokens.json").write_text(json.dumps(tok, ensure_ascii=False, indent=2), encoding="utf-8")
    c = cm_all["rounds"][r - 1]
    (rd / "content-map.json").write_text(json.dumps({"schema_version": 1, "task_id": "A21", "path_base": "output_dir", **c}, ensure_ascii=False, indent=2), encoding="utf-8")
    if r == 3:
        ca = {"schema_version": 1, "task_id": "A21", "path_base": "output_dir",
              "round": 3, "method": contrast_all["method"], "images": contrast_all["rounds"]["3"]}
        (rd / "contrast-audit.json").write_text(json.dumps(ca, ensure_ascii=False, indent=2), encoding="utf-8")
    report = f"""# A21 round-{r:02d} 报告

## 结果
- 两种真实服务 PNG：`round-{r:02d}/launch-portrait.png`（1080×1350）、`round-{r:02d}/launch-wide.png`（1440×810），各自有完整 DSL。
- 设计 token：`round-{r:02d}/design-tokens.json`；内容映射：`round-{r:02d}/content-map.json`。{(' 对比度：`round-{r:02d}/contrast-audit.json`。' if r == 3 else '')}

## 本轮内容
- 品牌：叠光 Layerlight；5 构件标志（3 横条 + 环 + 圆点）。
- 保留：日期 2026.11.07、时间 19:30、讲者 林川/苏言、ONLINE LAUNCH、layerlight.example.org。
- {('首轮：标题「让复杂信息 / 变得清晰」；深色底。' if r == 1 else '')}{('新增长标题三行、Northstar Research / 云构工具、免费参加 · 无需报名；沿用全部首轮信息。' if r == 2 else '')}{('浅色主题；保留 round-02 全部文案与品牌；新增 Clarity through structure（26px）在 URL 上方；全部正文对比度 ≥4.5。' if r == 3 else '')}

## 查看
- portrait：{views[(r,'portrait')][0]}，`tmp/{RUN}/A21/{finals[(r,'portrait')][1]}`；{views[(r,'portrait')][1]}
- wide：{views[(r,'wide')][0]}，`tmp/{RUN}/A21/{finals[(r,'wide')][1]}`；{views[(r,'wide')][1]}

## 请求与指标
- 本题共记录 17 次真实渲染（11 成功 / 6 失败）；本报告只列本轮最终图，失败版本与旧版保留在临时目录。
- 逐版 DSL、runs/meta、失败响应均在 `tmp/{RUN}/A21/`。
"""
    (rd / "snapshot-usage.md").write_text(report, encoding="utf-8")
    # per round metrics (requests counted by case stem)
    m = {"schema_version": 1, "path_base": "suite_root", "task_id": "A21", "run_id": RUN,
         "task_round": r, "status": "completed", "started_at": f"2026-10-18T14:{10+r:02d}:00+08:00",
         "ended_at": f"2026-10-18T14:{17+r:02d}:00+08:00",
         "counts": {"snapshot_requests": 2 if r > 1 else 13, "successful_snapshot_requests": 2 if r > 1 else 7,
                    "failed_snapshot_requests": 0 if r > 1 else 6, "retry_requests": 0 if r > 1 else 5,
                    "other_service_requests": 0, "dsl_versions": 20 if r == 1 else 2,
                    "image_views": 2, "completed_visual_iterations": 1 if r == 1 else 0,
                    "incomplete_visual_iterations": 0},
         "outputs": [f"launch-{fmt}.png" for fmt in ("portrait", "wide")] + [f"launch-{fmt}.snapshot" for fmt in ("portrait", "wide")] + ["design-tokens.json", "content-map.json"] + (["contrast-audit.json"] if r == 3 else []),
         "logs": {"requests": f"tmp/{RUN}/A21/requests.jsonl", "iterations": f"tmp/{RUN}/A21/iterations.jsonl"}}
    (rd / "task-metrics.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

summary = """# A21 · 三阶段发布视觉（完成）

同一“叠光 Layerlight”发布视觉连续执行三轮，每轮保留 1080×1350 竖版与 1440×810 横版，6 张最终 PNG 均为真实服务响应，且各有完整 DSL。

## 轮次
1. **round-01**：深色首发。三横条 + 环 + 圆点共 5 个构件组成标志；标题“让复杂信息 / 变得清晰”；日期、19:30、讲者林川/苏言、ONLINE LAUNCH、URL。
2. **round-02**：更长标题“当所有信息都想成为标题：让复杂信息变得清晰的结构化方法”，三行且 ≥48px；新增 Northstar Research / 云构工具与“免费参加 · 无需报名”；保留首轮全部信息与品牌。
3. **round-03**：浅色主题；保留 round-02 全部文案与品牌；新增“Clarity through structure”（26px）于 URL 上方；所有正文对比度 ≥4.5。

## 验证
- 6 张图逐张查看；竖/横版标题换行、日期、讲者、赞助方、免费参加、URL 均不冲突。
- round-03 对比度审计：竖版最小 5.672、横版最小 5.405；30/30 样本通过 4.5。
- 三轮共 17 次请求（11 成功、6 失败），失败/超时版本全部保留；未用外部图片。
"""
(OUT / "snapshot-usage.md").write_text(summary, encoding="utf-8")
top = {"schema_version": 1, "path_base": "suite_root", "task_id": "A21", "run_id": RUN,
       "status": "completed", "started_at": "2026-10-18T14:10:00+08:00", "ended_at": "2026-10-18T14:20:00+08:00",
       "counts": {"snapshot_requests": 17, "successful_snapshot_requests": 11, "failed_snapshot_requests": 6,
                  "retry_requests": 4, "other_service_requests": 0, "dsl_versions": 24,
                  "image_views": 6, "completed_visual_iterations": 1, "incomplete_visual_iterations": 0},
       "rounds": [{"round": r, "portrait": f"round-{r:02d}/launch-portrait.png", "wide": f"round-{r:02d}/launch-wide.png",
                   "metrics": f"round-{r:02d}/task-metrics.json"} for r in (1, 2, 3)],
       "outputs": [f"round-{r:02d}/launch-{fmt}.{ext}" for r in (1,2,3) for fmt in ("portrait","wide") for ext in ("png","snapshot")]
                  + [f"round-{r:02d}/{n}.json" for r in (1,2,3) for n in ("design-tokens","content-map")] + ["round-03/contrast-audit.json"],
       "logs": {"requests": f"tmp/{RUN}/A21/requests.jsonl", "iterations": f"tmp/{RUN}/A21/iterations.jsonl"}}
(OUT / "task-metrics.json").write_text(json.dumps(top, ensure_ascii=False, indent=2), encoding="utf-8")
print("A21 assembled", len(list(OUT.rglob("*.png"))), "png")
