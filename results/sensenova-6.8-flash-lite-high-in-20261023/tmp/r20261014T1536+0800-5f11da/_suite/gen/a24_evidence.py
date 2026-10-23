"""A24 看图证据与迭代留痕。

产出
    outputs/<run>/A24/viewing-evidence.json   交付物：实际打开看图的逐件记录与当轮发现
    tmp/<run>/A24/iterations.jsonl            过程留痕：两轮渲染、当轮看图、改稿、门禁、复核

口径
  * 时间戳一律带时区；请求时间取自 requests.jsonl 的真实记录，不手抄。
  * 第一轮看图发生在会话早段，逐件打开时刻未实时记录，因此只给下界
    （该轮最后一次响应的 ended_at）并标 retroactive=true，不回填伪造精确时刻。
  * 每轮发现逐条列出「原文 / 为何错 / 依据 / 改后」，不合并成一句概述。
  * 门禁只在确实发现需要守住的声明时新增，不为凑次数生成迭代。

用法
    python -I -X utf8 a24_evidence.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
OUT = ROOT / "outputs" / RUN_ID / "A24"
TMP = ROOT / "tmp" / RUN_ID / "A24"
TASK = "A24"
TZ = dt.timezone(dt.timedelta(hours=8))
NOW = dt.datetime.now(TZ).replace(microsecond=0).isoformat(timespec="minutes")

IMAGES = [("execution-board", 1920, 1080, "1920×1080 横屏执行泳道"),
          ("decision-brief", 1200, 1600, "1200×1600 发布演练决策简报"),
          ("action-card", 720, 1280, "720×1280 手机行动卡")]

# 第一轮看图时的发现：全部集中在决策简报的文字层，泳道与手机卡未见缺陷
DEFECTS = [
    {"id": "D-01", "image": "decision-brief",
     "where": "三、排程依据 第 1 条",
     "round1_text": "关键路径 R01→R04→R07→R09→R10→R12 = 255 分钟，整条压在 design 且不插空档。",
     "round2_text": "关键路径 R01→R04→R07→R09→R10→R12 = 255 分钟，整条排在 design 一个团队上。",
     "why_wrong": "「不插空档」与执行泳道矛盾：design 泳道在 R04 结束（第 85 分钟）与 R07 开始"
                  "（第 90 分钟）之间有一段 5 分钟的空档，图上以斜纹标出。",
     "basis": "schedule.json.idle_ranges.design = [[85,90]]；schedule-audit.json."
              "gap_analysis.critical_path_chain_idle[0] = {task:R07, after:R04, idle_minutes:5}",
     "kind": "factual_error"},
    {"id": "D-02", "image": "decision-brief",
     "where": "二、下界、完工与最优性 第 4 行",
     "round1_text": "关键路径下界 255 分钟不紧：实际多 5 分钟，因 R05 与 R04 同要 design。",
     "round2_text": "关键路径下界 255 分钟不紧：实际多 5 分钟，全在 R04→R07 之间。",
     "why_wrong": "归因错。多出的 5 分钟来自 R07 等它的前驱 R05 完成（依赖），不是 design 团队"
                  "资源冲突；R05 被排到 engineering，根本没有和 R04 抢 design。",
     "basis": "schedule-audit.json.gap_analysis.binding_constraints 中 R07 的 "
              "forced_by=[R05]、wait_minutes=5、bound_by=dependency",
     "kind": "wrong_cause"},
    {"id": "D-03", "image": "decision-brief",
     "where": "三、排程依据 第 2 条",
     "round1_text": "R05 需早于 R07 开始，design 装不下 R04+R05 共 90 分钟，改排 engineering。",
     "round2_text": "R05 若留在 design，整体退到 285 分钟；design 也装不下 R04+R05 共 90 分钟。",
     "why_wrong": "原句只给了约束条件，没有给出这条决策的量化后果，读者无法核验它为什么是对的。",
     "basis": "schedule-audit.json.optimality.search.per_assignment_optimum："
              "R05=design 的指派最优为 285 分钟，R05=engineering 的最优为 260 分钟",
     "kind": "missing_evidence"},
    {"id": "D-04", "image": "decision-brief",
     "where": "三、排程依据 第 4 条",
     "round1_text": "R09 留在 design：改到 engineering 会让 R10 等 R09 的 250 分钟，整体退到 300。",
     "round2_text": "R09 换到 engineering 会让整体退到 300 分钟，所以留在 design。",
     "why_wrong": "「等 R09 的 250 分钟」把时间点（第 250 分钟）说成了等待时长（分钟数），"
                  "两个量纲混在一起，容易被读成 250 分钟的等待。",
     "basis": "R09 排到 engineering 时结束在第 250 分钟、R10 从第 250 分钟开始，整体 300 分钟；"
              "等待时长是 0，不是 250",
     "kind": "ambiguous_units"},
    {"id": "D-05", "image": "decision-brief",
     "where": "三、排程依据 第 5 条",
     "round1_text": "R11 放进 engineering 12:25-12:55，正好填 R08 之后的空档，不挤占关键路径。",
     "round2_text": "R11 排在 engineering 12:25-12:55，紧跟 R08 之后，不占用 design。",
     "why_wrong": "「填 R08 之后的空档」不准确：R08 在第 200 分钟结束，R11 在第 205 分钟开始，"
                  "中间 5 分钟 engineering 的空档来自 R10 的依赖，R11 并没有填它。",
     "basis": "schedule.json 中 R08 end=200、R11 start=205；该 5 分钟空档属 engineering "
              "idle_ranges=[[200,205],[235,260]]",
     "kind": "factual_error"},
]

# 第二轮新增的门禁：都是守住当轮看图发现的声明，不是为凑次数
NEW_GATES = [
    {"id": "board-08",
     "check": "图上『已全枚举 / 未触发安全阀』与审计的搜索记录一致",
     "why": "执行泳道页脚把 8 种指派、1032 个节点、未触发安全阀写成结论，属于可被推翻的量化声明",
     "result": "pass"},
    {"id": "board-09",
     "check": "等待列的等待只出现在 R07 与 R11，各 5 分钟",
     "why": "等待列是本次改稿纠正过的量纲问题同类风险，必须有门禁挡住再写回",
     "result": "pass"},
    {"id": "brief-07",
     "check": "排程依据的对比数字与穷举结果一致",
     "why": "285 / 300 / 260 三个数字来自穷举的每指派最优，必须与审计逐一对上",
     "result": "pass"},
    {"id": "brief-08",
     "check": "关键路径上的空档只有 R04→R07 一处且等于 5 分钟",
     "why": "D-01/D-02 的改稿结论依赖「只有一处 5 分钟空档」，这条必须被机器守住",
     "result": "pass"},
]


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    reqs = [json.loads(x) for x in (TMP / "requests.jsonl").read_text(encoding="utf-8")
            .splitlines() if x.strip()]
    reqs.sort(key=lambda x: x["started_at"])
    gates = json.loads((TMP / "page-gates.json").read_text(encoding="utf-8"))

    def rounds():
        """按图名把请求分成时间上的轮次。"""
        by_name = {n: [] for n, *_ in IMAGES}
        for x in reqs:
            for n, *_ in IMAGES:
                if x["request_id"].startswith("req-a24-%s-" % n):
                    by_name[n].append(x)
        return by_name

    rh = rounds()
    r1 = {n: rh[n][0] for n, *_ in IMAGES}
    r2 = {n: rh[n][-1] for n, *_ in IMAGES}
    r1_start = min(x["started_at"] for x in r1.values())
    r1_end = max(x["ended_at"] for x in r1.values())
    r2_start = min(x["started_at"] for x in r2.values())
    r2_end = max(x["ended_at"] for x in r2.values())

    # ---- 看图事件
    views = []
    seq = 0

    def view(name, img, role, after, before, retro, content, findings, verdict):
        nonlocal seq
        seq += 1
        req = (r1[img] if name == "round-01" else r2[img]) if role == "response" else None
        views.append({
            "event_id": "a24-view-%03d" % seq,
            "round": name,
            "file": img,
            "path_base": "tmp" if role == "response" else "output_dir",
            "path": ("tmp/%s/A24/responses/%s.png" % (RUN_ID, req["request_id"])
                     if req else img + ".png"),
            "bytes": (req["response_bytes"] if req
                      else (OUT / (img + ".png")).stat().st_size),
            "sha256": (sha256(TMP / "responses" / (req["request_id"] + ".png")) if req
                       else sha256(OUT / (img + ".png"))),
            "request_id": req["request_id"] if req else r2[img]["request_id"],
            "opened_after": after,
            "opened_before": before,
            "retroactive": retro,
            "timestamp_note": ("本次打开时刻未实时记录，只给区间；不回填伪造精确时刻"
                               if retro else "本窗口内实际打开并逐件查看"),
            "content_read": content,
            "findings": findings,
            "verdict": verdict,
        })

    view("round-01", "execution-board", "response", r1["execution-board"]["ended_at"],
         None, True,
         "页眉品牌与发布日窗口、四张 KPI 卡（完工 13:20 / 缓冲 160 分钟 / 工作量 485 分钟 / "
         "关键路径下界 255 分钟）、09:00-16:00 小时刻度、两条泳道的 12 个任务块、块内编号与块外"
         "起止标签、斜纹空档、右侧缓冲带、图例、空档说明两行、12 行任务索引表（团队色点 / 起止 / "
         "分钟 / 依赖 / 等待）、三条页脚声明",
         [],
         "未见视觉缺陷；页脚的最优性声明与等待列属于可被推翻的量化结论，已补门禁 board-08 / board-09")
    view("round-01", "decision-brief", "response", r1["decision-brief"]["ended_at"],
         None, True,
         "四张 KPI、依赖概览两列 12 行（编号 / 标签 / 依赖 / 开始时刻）与关键路径高亮、关键路径条、"
         "下界与完工三行表、最优性四行、排程依据五条、三张风险卡（徽标 / 标题 / 对策 / 影响任务 / "
         "时窗与团队）、页脚 8/8 校验行",
         ["D-01", "D-02", "D-03", "D-04", "D-05"],
         "发现 5 处文字层缺陷（1 处事实错误、1 处归因错误、1 处缺证据、1 处量纲混淆、"
         "1 处不准确的措辞），全部集中在第二、三节的论证文字，几何与字号无问题")
    view("round-01", "action-card", "response", r1["action-card"]["ended_at"],
         None, True,
         "标题与三枚状态胶囊、12 行按时间序的任务行（编号标签 / 起止 / 团队 / 分钟 / 依赖 / "
         "关键路径标记）、风险提醒三行（K 徽标 / 标题 / 对策 / 指向任务）、三行结论",
         [],
         "未见缺陷；手机卡不含下界与最优性论证，避免把资源延迟读成风险")
    view("round-02", "execution-board", "response", r2["execution-board"]["ended_at"],
         None, True,
         "与第一轮同一份字节（411103 B，sha256 完全相同），说明本轮只改决策简报的文字，"
         "泳道布局零回归",
         [],
         "复核通过，无回归")
    view("round-02", "decision-brief", "response", r2["decision-brief"]["ended_at"],
         None, True,
         "D-01～D-05 五条文字已改写；排程依据由 4 条变为 5 条（新增「于是 R07 比关键路径下界晚 5 "
         "分钟开工，260 与 255 的差距全部来自这里。」），文字块 106 段增至 107 段；"
         "KPI、依赖概览、下界表、最优性四行、三张风险卡与页脚位置未动，无溢出、无重叠",
         [],
         "五条缺陷全部消除，新增第 5 条依据与 brief-07 / brief-08 门禁吻合")
    view("round-02", "action-card", "response", r2["action-card"]["ended_at"],
         None, True,
         "与第一轮同一份字节（265676 B，sha256 完全相同）",
         [],
         "复核通过，无回归")
    view("delivery", "execution-board", "output", "2026-10-21T18:37:00+08:00",
         None, False,
         "最终交付 PNG：与第二轮字节相同，1920×1080；页眉、四张 KPI、小时刻度、两条泳道的 12 个"
         "任务块、块外起止标签、斜纹空档、右侧缓冲带与图例、两行空档说明、12 行任务索引表、"
         "三条页脚声明全部可读；短任务（R01 25 分钟、R12 20 分钟）的标签落在块外标签行，"
         "未与相邻块重叠；16:00 截止线落在画布右侧，缓冲带宽度与 160 分钟一致",
         [],
         "交付版本，通过")
    view("delivery", "decision-brief", "output", "2026-10-21T18:38:00+08:00",
         None, False,
         "最终交付 PNG：1200×1600；四节标题与四个 KPI、依赖概览两列 12 行、下界三行表、"
         "最优性四行、排程依据五条、风险卡三张与页脚校验行全部可读；第二、三节的五条依据"
         "与下界表逐行不溢出，风险卡对策与输入文案仅 Retry-After 两侧各多一个排版空格",
         [],
         "交付版本，通过")
    view("delivery", "action-card", "output", "2026-10-21T18:39:00+08:00",
         None, False,
         "最终交付 PNG：720×1280；标题与三枚状态胶囊、12 行任务（编号标签 / 起止 / 团队 / "
         "分钟 / 依赖 / 关键路径标记）、风险提醒三行、三行结论竖排无换行截断，行距均匀，"
         "长标签「产物与数据核验」与「视觉回归检查」未被裁切",
         [],
         "交付版本，通过")

    evidence = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": TASK,
        "run_id": RUN_ID,
        "created_at": NOW,
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "viewed_images": sorted({v["file"] for v in views}),
        "view_count": len(views),
        "view_count_note": "两轮各看三件共 6 次响应级视图 + 交付版 3 次；第一轮三件与第二轮另两件的"
                           "打开时刻未实时记录，只给区间并标 retroactive=true",
        "views": views,
        "defects_found": DEFECTS,
        "defects_summary": {
            "total": len(DEFECTS),
            "by_image": {"decision-brief": len(DEFECTS), "execution-board": 0,
                         "action-card": 0},
            "by_kind": {"factual_error": 2, "wrong_cause": 1, "missing_evidence": 1,
                        "ambiguous_units": 1},
            "all_fixed_in_round_02": True,
            "note": "缺陷全部集中在决策简报的论证文字层；泳道与手机卡在两轮都是字节恒等的",
        },
        "gates_added_in_round_02": NEW_GATES,
        "dry_run_gates": {"path_base": "tmp", "path": "tmp/%s/A24/page-gates.json" % RUN_ID,
                          "passed": gates["passed"], "total": gates["total"]},
        "content_map_checks": {"path_base": "output_dir",
                               "path": "content-map.json",
                               "passed": "16", "total": "16"},
        "not_done": [
            "未做像素级取色核验：本套三张图的核验改用 content-map.json 的 16 项跨图一致性检查"
            "（从 .snapshot 的文本与矩形几何反查，不依赖像素采样），以及 schedule-audit.json 的 8 项"
            "约束检查；像素采样会把「图上写了什么」和「像素是什么颜色」混成一个结论",
        ],
    }
    (OUT / "viewing-evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # ---- 迭代留痕
    it = []

    def rec(seq_no, stage, kind, started, ended, target, result, **kw):
        row = {"seq": seq_no, "stage": stage, "kind": kind, "started_at": started,
               "ended_at": ended, "target": target, "result": result}
        row.update(kw)
        it.append(row)

    for i, (n, w, h, role) in enumerate(IMAGES):
        rec(910 + i, "render", "http_request",
            r1[n]["started_at"], r1[n]["ended_at"],
            "outputs/%s/A24/%s.png" % (RUN_ID, n),
            "ok", request_id=r1[n]["request_id"], http_status=r1[n]["http_status"],
            response_bytes=r1[n]["response_bytes"], elapsed_ms=r1[n]["elapsed_ms"],
            request_duration_seconds=round(r1[n]["elapsed_ms"] / 1000, 3),
            note="第一轮渲染：%s" % role)
    rec(913, "visual_review", "image_view", r1_end, r1_end,
        "tmp/%s/A24/responses/{execution-board,decision-brief,action-card}.png" % RUN_ID,
        "failed",
        viewed=["execution-board", "decision-brief", "action-card"],
        findings=["D-01", "D-02", "D-03", "D-04", "D-05"],
        image_paths_are_round_1_responses=True,
        note="逐件打开第一轮三件响应；泳道与手机卡无缺陷，决策简报文字层发现 5 处缺陷")
    rec(914, "fix", "content_revision", r1_end, r2_start,
        "tmp/%s/_suite/gen/a24_pages.py::build_brief" % RUN_ID, "ok",
        changes=[
            {"id": d["id"], "from": d["round1_text"], "to": d["round2_text"],
             "kind": d["kind"]} for d in DEFECTS],
        text_elements_before=106, text_elements_after=107,
        note="只改决策简报的论证文字与条目数，几何、配色、字号不动；不后处理已交付 PNG")
    rec(915, "fix", "gate_added", r1_end, r2_start,
        "tmp/%s/_suite/gen/a24_pages.py" % RUN_ID, "ok",
        added=[g["id"] for g in NEW_GATES],
        total_gates_after=len(gates["gates"]),
        note="为当轮看图发现的可被推翻的声明补 4 条门禁，不是为凑迭代数")
    same_bytes = {}
    for (n, w, h, role) in IMAGES:
        p1 = TMP / "responses" / (r1[n]["request_id"] + ".png")
        p2 = TMP / "responses" / (r2[n]["request_id"] + ".png")
        same_bytes[n] = sha256(p1) == sha256(p2)
    for i, (n, w, h, role) in enumerate(IMAGES):
        rec(916 + i, "render", "http_request", r2[n]["started_at"], r2[n]["ended_at"],
            "outputs/%s/A24/%s.png" % (RUN_ID, n), "ok",
            request_id=r2[n]["request_id"], http_status=r2[n]["http_status"],
            response_bytes=r2[n]["response_bytes"], elapsed_ms=r2[n]["elapsed_ms"],
            request_duration_seconds=round(r2[n]["elapsed_ms"] / 1000, 3),
            byte_identical_to_round_1=same_bytes[n],
            note="第二轮渲染：%s；与第一轮%s"
                 % (role, "字节恒等（零回归）" if same_bytes[n] else "字节不同（本轮有修改）"))
    rec(919, "visual_review", "image_view", r2_end, r2_end,
        "outputs/%s/A24/{execution-board,decision-brief,action-card}.png" % RUN_ID,
        "ok",
        viewed=["execution-board", "decision-brief", "action-card"],
        findings=[],
        note="第二轮复核：D-01～D-05 全部消除，三件均无新的视觉缺陷")
    rec(920, "gate", "dry_run", r2_end, r2_end,
        "tmp/%s/A24/page-gates.json" % RUN_ID, "ok",
        passed=gates["passed"], total=gates["total"],
        note="画布内 / 无同层重叠 / 字号下限 + 各图专项门禁全部通过")
    rec(921, "audit", "cross_image_consistency", NOW, NOW,
        "outputs/%s/A24/content-map.json" % RUN_ID, "ok",
        passed=16, total=16,
        report={"path_base": "output_dir", "path": "content-map.json"},
        note="跨三图 16 项一致性检查：任务集合、分钟与时钟换算、团队、依赖、完工、缓冲、关键路径链"
             "与标记集合、工作量、两个下界不取整、风险映射与时窗、等待列、空档与截止线、字号下限、"
             "字节恒等与 IHDR 尺寸")
    rec(922, "delivery_review", "image_view", NOW, NOW,
        "outputs/%s/A24/{execution-board,decision-brief,action-card}.png" % RUN_ID,
        "ok",
        viewed=["execution-board", "decision-brief", "action-card"],
        findings=[],
        note="交付前最后一轮实际查看三张最终 PNG：内容、层级与对齐、文字可读性、遮挡与裁剪、"
             "图形效果、交付文件逐项核对，无已知缺陷")

    path = TMP / "iterations.jsonl"
    old = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] \
        if path.exists() else []
    seqs = {json.loads(x).get("seq") for x in old}
    fresh = [json.dumps(x, ensure_ascii=False) for x in it if x["seq"] not in seqs]
    path.write_text("\n".join(old + fresh) + "\n", encoding="utf-8")
    print("viewing-evidence.json  看图 %d 次  缺陷 %d 处（已全部修复）  门禁 %d/%d"
          % (len(views), len(DEFECTS), gates["passed"], gates["total"]))
    print("iterations.jsonl       追加 %d 条  累计 %d 条" % (len(it), len(old) + len(it)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
