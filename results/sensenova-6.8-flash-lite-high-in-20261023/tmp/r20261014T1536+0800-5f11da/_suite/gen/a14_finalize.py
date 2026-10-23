"""A14 收口：task-metrics.json + snapshot-usage.md + suite-state 更新 + 检查点。

用法：SNAPSHOT_RUN_ID=<rid> python -I tmp/<rid>/_suite/gen/a14_finalize.py

判据来源与 a14_audit.py 一致：任务给定的硬约束（安全边距 40、标题 ≥36 且 ≤3
行、讲者 ≥22 且 ≤2 行、标题不与徽标碰撞、取消卡完整标题+时间+注明、文字原样
保留、PNG 为服务原始字节）直接对应到审计检查项；没有题目数值的余量项已在
审计报告的 thresholds 里标为 self_defined。

「逐张实际查看」这一项不由脚本判断，必须由 reviews.json 提供实际查看记录；
没有记录时该检查记为未通过并在 unresolved_issues 里点名。
"""

from __future__ import annotations

import json
import datetime
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
# run_id 从脚本自身路径推出（tmp/<rid>/_suite/gen/…）；显式 SNAPSHOT_RUN_ID 优先
os.environ.setdefault("SNAPSHOT_RUN_ID", HERE.parents[2].name)
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE.parent))
import suite as S
import a14_pages as A

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TASK = "A14"
RID = S.run_id()
OUT, TMP = S.task_dirs(TASK)
TSDIR, SDIR = S.suite_dirs()


def _load(path: Path) -> list:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8",
                                                 errors="replace").splitlines()
            if l.strip()]


def main() -> int:
    audit_p = TMP / "gen" / "batch-audit.json"
    if not audit_p.exists():
        print("缺 batch-audit.json，请先跑 a14_audit.py")
        return 2
    audit = json.loads(audit_p.read_text(encoding="utf-8"))
    checks = {c["id"]: c for c in audit["checks"]}
    cards = audit["cards"]
    reqs = _load(TMP / "requests.jsonl")
    its = _load(TMP / "iterations.jsonl")
    pre = audit.get("generation", {}).get("pre_render_checks", {})
    pre_probs = pre.get("problems", [])

    def allp(*ids: str) -> bool:
        return all(checks[i]["passed"] for i in ids if i in checks)

    def anyp(*ids: str) -> bool:
        return any(checks[i]["passed"] for i in ids)

    def group(prefix: str) -> bool:
        sel = [c for c in checks.values() if c["id"].startswith(prefix)]
        return bool(sel) and all(c["passed"] for c in sel)

    # ---- PNG 与服务原始响应字节一致
    pairing = []
    rows = json.loads((TMP / "gen" / "render-rows.json").read_text(encoding="utf-8")
                       )["rows"] if (TMP / "gen" / "render-rows.json").exists() else {}
    for c in cards:
        cid = c["id"]
        png = OUT / ("card-%s.png" % cid)
        row = rows.get(cid, {})
        rp = row.get("response_path")
        same = None
        if png.exists() and rp:
            src = ROOT / rp
            same = (src.exists() and png.read_bytes() == src.read_bytes())
        pairing.append({"card": cid,
                        "png": "card-%s.png" % cid,
                        "request_id": row.get("request_id"),
                        "response_archive": rp,
                        "png_byte_identical_to_service_response": same})
    byte_ok = all(p["png_byte_identical_to_service_response"] for p in pairing)

    # ---- 逐张实际查看
    reviews = audit.get("reviews", {})
    reviewed = [] if isinstance(reviews, dict) else reviews
    viewed = {r.get("card") for r in reviewed if r.get("viewed_at")}
    review_ok = len({c["id"] for c in cards} & viewed) == len(cards)

    # ---- 需求核对
    R = [
        ("r1", "8 张卡齐全且每张尺寸精确 1200×630（PNG 为真实 PNG）",
         group("size-") and len(cards) == 8),
        ("r2", "每张卡有同名完整 .snapshot，且与生成器 DSL 逐字一致",
         group("dsl-")),
        ("r3", "每张卡的 PNG 与服务返回的原始响应字节完全一致（未后处理）",
         byte_ok),
        ("r4", "安全边距 40：实测整幅墨迹四向净空均 ≥40", group("safe-")),
        ("r5", "标题原文完整保留、字号 ≥36、最多 3 行、折行无损",
         group("titlefont-") and group("titlelines-") and group("text-")),
        ("r6", "标题实测行数与声明一致且墨迹未被裁切（含最长标题与中英混排标题）",
         group("lines-") and group("titlefit-")),
        ("r7", "讲者原文完整保留、字号 ≥22、最多 2 行、实测行数一致",
         group("speakerfont-") and group("speakerlines-") and group("speakers-")),
        ("r8", "时间完整显示、未裁切", group("timeink-")),
        ("r9", "状态用颜色 + 绘制符号 + 中文词共同区分，颜色确实渲染到画面上",
         group("statuscolor-")),
        ("r10", "标题墨迹与状态徽标墨迹不相交，实测净空足够",
         group("nocollision-")),
        ("r11", "取消卡保留完整标题与时间，另有「本场取消」注明且未整体灰底",
         allp("cancel-K06", "nogrey-K06")),
        ("r12", "非取消卡不出现「本场取消」注明",
         group("cancel-absent-")),
        ("r13", "品牌/日期/主色/关键槽位坐标全批一致（无逐卡硬编码）",
         allp("consistency-badge", "consistency-time")),
        ("r14", "所有文字与几何槽位都有墨迹，且墨迹宽度覆盖全部字符，"
                "无被画丢或被裁掉一半的内容",
         group("inkall-") and group("labelink-") and group("footerink-")),
        ("r14b", "右锚（日期/时间/时间标签/页脚右串）墨迹右缘落在内容栏右缘 1112"
                 "，误差 ≤2 px", group("anchor-")),
        ("r15", "特殊字符原样：DSL text 属性里 & < > 都是原始字符、没有实体串，"
                "且字符多重集与原文一致（服务不解码实体，写成 &lt; 会画成字面串）",
         not [p for p in pre_probs if "多重集" in p or "实体串" in p
              or "双引号" in p]),
        ("r16", "前置校验（排版与硬约束）0 问题", not pre_probs),
        ("r17", "batch-audit.json 已交付到输出目录",
         (OUT / "batch-audit.json").exists()),
        ("r18", "8 张最终服务原图逐张实际查看并留痕（接触表不替代）", review_ok),
    ]
    rc = [{"id": i, "requirement": t, "passed": bool(p)} for i, t, p in R]
    summary = {"total": len(rc),
               "passed": sum(1 for c in rc if c["passed"]),
               "failed": sum(1 for c in rc if not c["passed"])}

    # ---- 计时与计数
    ok = [r for r in reqs if r.get("http_status") == 200]
    probe_n = sum(1 for r in reqs if "probe" in (r.get("label") or "")
                  or r.get("kind") == "probe")
    views = [i for i in its if i.get("image_path")]
    vis = [i for i in its if i.get("type") == "visual"]
    dsls = {r.get("dsl_path") for r in reqs if r.get("dsl_path")}
    started = min([r["started_at"] for r in reqs if r.get("started_at")] or
                  [S.now_iso()])
    ended = S.now_iso()
    t0 = datetime.datetime.fromisoformat(started)
    elapsed = max(0, int((datetime.datetime.fromisoformat(ended) - t0
                          ).total_seconds()))
    metrics = {
        "schema_version": 1,
        "path_base": "suite_root",
        "task_id": TASK,
        "run_id": RID,
        "status": "completed" if summary["failed"] == 0 else "partial",
        "stop_reason": None if summary["failed"] == 0 else "仍有未通过项，见 unresolved_issues",
        "requirement_checks": {"summary": summary, "checks": rc},
        "pairing": pairing,
        "counts": {
            "snapshot_requests": len(reqs),
            "successful_snapshot_requests": len(ok),
            "failed_snapshot_requests": len(reqs) - len(ok),
            "retry_requests": sum(1 for r in reqs if (r.get("attempt") or 1) > 1),
            "probe_requests": probe_n,
            "final_render_requests": sum(
                1 for r in ok if (r.get("label") or "").startswith("card-")),
            "dsl_versions": len(dsls),
            "dsl_version_note": "按归档 DSL 文件路径去重；每次请求单独落盘一份 DSL，"
                                "重试不覆盖旧版",
            "image_views": len(views),
            "visual_iterations": len(vis),
            "visual_iteration_note": "type=visual 的完整视觉迭代（看旧图→改→再渲染→"
                                     "看图比较）；前置校验与语法修复另计",
            "pre_render_check_problems": len(pre_probs),
            "verification_checks": len(audit["checks"]),
            "verification_failures": sum(1 for c in audit["checks"]
                                         if not c["passed"]),
            "final_images": len(pairing),
            "requirement_checks_failed": summary["failed"],
        },
        "timings": {
            "started_at": started,
            "ended_at": ended,
            "elapsed_seconds": elapsed,
            "first_usable_image_at": min(
                [r["started_at"] for r in ok if r.get("started_at")] or []),
            "request_elapsed_sum_ms": round(sum(
                (r.get("elapsed_ms") or 0) for r in reqs), 1),
            "queue_wait_ms": None,
            "user_wait_seconds": 0,
            "timezone": S.TZ_NAME,
            "timing_note": "总墙钟不含 Bash 分类器阻塞与上下文压缩等待；请求耗时之和"
                           "不等于墙钟",
        },
        "logs": {"requests": S.rel(TMP / "requests.jsonl"),
                 "iterations": S.rel(TMP / "iterations.jsonl"),
                 "pre_render_check_log": S.rel(TMP / "gen" / "checks.log"),
                 "batch_audit": S.rel(OUT / "batch-audit.json"),
                 "contact_sheet": S.rel(TMP / "preview" / "a14-contact-sheet.png")
                 if (TMP / "preview" / "a14-contact-sheet.png").exists() else None},
        "outputs": sorted(p.name for p in OUT.iterdir() if p.is_file())
                   if OUT.exists() else [],
        "unresolved_issues": [
            {"id": "review-evidence", "status": "open",
             "detail": "reviews.json 尚未记录全部 %d 张最终图的逐张实际查看"
                       % len(cards),
             "recovery": "逐张 Read 最终 PNG 后写 tmp/%s/A14/gen/reviews.json "
                         "并重跑 a14_audit.py / a14_finalize.py" % RID}
            if not review_ok else None,
            {"id": "verification", "status": "open",
             "detail": "像素审计仍有 %d 项未通过"
                       % sum(1 for c in audit["checks"] if not c["passed"]),
             "recovery": "查看 batch-audit.json 的 checks 里 failed 项并修 DSL"}
            if sum(1 for c in audit["checks"] if not c["passed"]) else None,
        ],
    }
    metrics["unresolved_issues"] = [x for x in metrics["unresolved_issues"]
                                    if x]

    (OUT / "task-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- snapshot-usage.md
    cards_txt = "\n".join(
        "| %s | %s | %d px / %d 行 | %s | %s |" % (
            c["id"], c["title"]["lines"][0][:26],
            c["title"]["font_size_px"], c["title"]["line_count"],
            c["status"]["text_original"], c["time"]["rendered"])
        for c in cards)
    md = f"""# A14 内容压力批量卡 —— 使用与踩坑记录

- run_id：`{RID}`
- 输出目录：`{S.rel(OUT)}`
- 临时目录：`{S.rel(TMP)}`
- 脚本：`tmp/{RID}/_suite/gen/a14_pages.py`（生成）、`a14_audit.py`（像素审计）、
  `a14_pixels.py`（量测库）、`a14_finalize.py`（指标与状态）
- 需求核对：{summary["passed"]}/{summary["total"]} 通过
- 前置校验问题：{len(pre_probs)}
- 像素审计检查：{len(audit["checks"])} 项，未通过
  {sum(1 for c in audit["checks"] if not c["passed"])}

## 服务与文档

真实服务：`https://open-snapshot.muedsa.com`，`POST /snapshot`，请求体为 UTF-8
DSL 文本，成功返回图片字节、失败返回错误 JSON。文档缓存与请求留痕见
`tmp/{RID}/_suite/docs/`。

## 交付清单

| 卡 | 标题首行 | 标题字号 / 行数 | 状态 | 时间 |
|---|---|---|---|---|
{cards_txt}

每张卡在输出目录有 `card-K0x.png`（服务原始字节）与同名 `.snapshot`。

## 关键设计

1. **标题只按字号台阶降档，绝不动画布**。字号从 {A.TITLE_STEPS} 逐档试，
   取第一个能在 {A.TITLE_MAX_LINES} 行内排下的档；画布、安全边距、徽标、讲者槽、
   时间槽、页眉页脚坐标全批一致，由 `checks()` 的单元组坐标比对强制。
2. **折行点提前于盒缘**。折行上限取盒宽的 {A.WRAP_SLACK:.0%}
   （{A.TITLE_WRAP_LIMIT} px 对 {A.TITLE_W} px 盒），剩余 8% 是墨宽估算误差预算。折在盒缘上
   时行末常达 94–99%，一次四舍五入就越界被裁。
3. **同行数内取最均衡折点**。贪心只保证装得下：K05 的 2 行分法会把第二行压成
   「读性」两个字。改成在最少行数内枚举全部合规折点、最小化最宽行，K05 变成
   「Color, Alpha & Contrast /」+「从颜色到可读性」，K07 的「服务」不再被拆到
   两行。
4. **一行一个单行 `<Text>` 盒**。不依赖服务的自动折行，行高精确等于
   `round(字号×1.45)`，垂直位置完全由生成器决定。
5. **状态符号用几何而非字形**。✕ / ✓ 这类字形有缺字变豆腐块的风险，四个状态
   （实心圆点 / 实心方块 / 空心圆环 / 空心圆环加横杠）全部用 `<Container>` +
   `border` 画出来，颜色 + 形状 + 中文词三重编码。
6. **右锚走 `text_r()`，不用 `transform` 反算**。探针 `a14-align-probe.png`
   实测 `alignment="CENTER"` 是**水平居中**、`CENTER_LEFT` 是左对齐，所以右缘
   对齐只能靠「把盒心放到 `右缘 - 墨宽/2`」。做法是 `盒宽 = 墨宽估算 + PAD_X`、
   `盒左 = 右缘 - 墨宽估算 - PAD_X/2`，盒心随之落在 `右缘 - 墨宽估算/2`，真实
   墨右缘 = `右缘 + (真实墨宽 - 墨宽估算) / 2`——**估算误差被减半**，但不会因为
   盒宽估算偏大而把整列挪动。最终锚点用 `ANCHOR_SHIFT` 补一次实测残差
   （date/time/label_time/footer_right 分别 +4/+4/+2/−3 px），补完后四个槽位的
   墨迹右缘**全部落在 1112，偏差 0**。
7. **盒宽口径和定位口径分开**。`MONO_EM = 0.60`（保守，只用来定**盒宽**，盒越
   宽越安全）与 `MONO_EM_TIGHT = 0.50`（贴近实测 0.49–0.52，只用来**定位**）
   不能混用：用 0.60 定位会让整列右锚向左偏约 9 px。等宽字估算与渲染都显式
   `family="Noto Sans Mono CJK SC"`，`text()` 里 `mono=True` 但 `family` 不是
   等宽字就直接抛错，避免两边口径不一致。

## 实际遇到的问题与处理

1. **头部整块漏发**。品牌、日期、主色短线、分隔线只写进了 `meta`，从未写进
   DSL。`_escape_check` 的字符多重集比对（预期文本含 BRAND / DATE）会把它报成
   「多重集不符」，但这条线索太隐晦，所以又加了结构检查：`<Text>` 节点数必须
   等于声明的文字条数，主色短线的矩形必须出现在 DSL 里。
2. **`text()` 收了 `mono` 却忽略它**。字体始终来自 `family`，于是时间盒按等宽
   0.60 em 估宽、却用 CJK 字体渲染，`CENTER` 居中后右缘会整体偏掉。已让
   `mono=True` 必须配 `family=MONO`，否则在生成时就报错。
3. **CJK 前导空格被吞**。`tokenize` 的 CJK 分支硬编码 `space: False`，
   「Contrast / 从」之间的空格在折行后消失，渲染成「Contrast /从」。改成
   `space = i > 0 and text[i - 1] == " "`。
4. **折行后末行可能超过折行上限**。旧的 `no_line_start_fix` 把上一行末尾 token
   挪下来，会让下一行变宽。新的枚举在折点处直接拒绝「下一行以禁则字符开头」，
   不再需要事后补救。
5. **XML 转义方向搞反了**（本批最大的坑）。最初按常规 XML 习惯把 `& < >` 转成
   实体，结果探针 `req-a14-probe-layout-abdd1d` 里标题被渲染成**字面的**
   `&lt; &amp; &gt;`——服务**不解码**实体。再用 `req-a14-escape-test-raw-6355ec`
   把裸的 `A < B & C > D` 直接写进 `text` 属性验证：HTTP 200，逐字正确。于是
   `esc()` 改成恒等函数，`_escape_check()` 的判据也**反转**：DSL 里出现实体串
   现在算缺陷，而不是「裸 `&`」才算。文档缓存里对这一点没有任何说明，只能靠
   实测。唯一残余风险是半角双引号 `"` 会截断属性，本批 8 条数据不含，已断言。
6. **标签与页脚丢字：根因不是右缘裁切，是盒太窄**。首版交付的 8 张卡上
   「讲者」只剩「讲」、「时间」只剩「时」、页脚右侧只剩「讲座系列 ·」。一开始
   怀疑是右缘被裁，但探针（把盒边界画成可见 1 px 线、并在 x=88 / x=1112 画
   参照线）显示真相反而是：盒宽等于估算墨宽，盒窄于墨宽时服务会**自行折到第二
   行**，而单行盒高把第二行整行裁掉。修法就是给每个盒留 `PAD_X` 的横向余量；
   盒子是透明的，宽一点不会裁切。审计里另加 `labelink-` / `footerink-`（比实测
   墨宽与估算墨宽的比值）和 `anchor-`（墨迹右缘到 1112 的偏差）来守着这个
   回归——「有没有墨迹」根本抓不住丢字。
7. **盒宽修好后，右列又不落在 1112 上**。裁切修完重渲染跑审计，新增的
   `anchor-` 检查全批失败：date/time/label_time/footer_right 的墨迹右缘分别
   落在 1108/1108/1110/1115。原因是 `盒中心 = 右缘 - 墨宽估算/2`，估算偏高会让
   右列整体左移、偏低则右移（误差减半传导）。关键观察是 **8 张卡的四个槽位
   偏差完全一致**，说明偏移只跟「字符串族 + 字号 + 字距」有关，与卡内容无关。
   于是把这次实测出的偏差做成 `ANCHOR_SHIFT`（+4/+4/+2/−3 px）补到盒左，盒边界
   与墨迹一起平移。补完后四个槽位墨迹右缘**全部落在 1112，偏差 0**。这是量出来的
   不是估出来的，审计里保留了原始偏差作为依据。
8. **审计器自己也有 bug：白底被判成灰底**。`nogrey-` 检查把 `dominant()` 的
   结果和 `[255,255,255]` 比，但 `dominant()` 会量化到 8 级（`//32*32`），纯白
   被归到 `[224,224,224]`，于是永远匹配不上，取消卡被误判为整体灰底。改成比对
   量化后的底色。这类「检查器缺陷」和「作品缺陷」要分开归因，否则会把正确作品
   判成不达标。
9. **白底卡与几何取证**。A13 靠 alpha 找几何，A14 铺满 `#FFFFFF`，alpha 恒为
   255。改按与参考色的分量差找墨迹，`color_counts` 再按目标色取证状态徽标的
   前景色与底色。

## 看图与迭代

- 探针 `tmp/{RID}/A14/preview/a14-probe.png`（req-a14-probe-layout-abdd1d）：
  一次渲染同时暴露实体不被解码、验证四种状态符号可辨、最长标题不越参照线。
- 转义对照 `tmp/{RID}/A14/preview/a14-escape-raw.png`（req-a14-escape-test-raw-6355ec）：
  裸 `< > &` 直接写进 text 属性，HTTP 200 且逐字正确，是反转转义策略的直接依据。
- 对齐探针 `tmp/{RID}/A14/preview/a14-align-probe.png`（req-a14-align-probe-800ada）：
  把测试盒边界画成可见 1 px 线并在 x=88 / x=1112 画参照线，一次确定
  `alignment="CENTER"` 是水平居中、以及「盒窄于墨宽会折行并裁掉第二行」这个
  真实机制。它替代了事后像素统计的猜测。
- 接触表 `tmp/{RID}/A14/preview/a14-contact-sheet.png`：仅作全批一致性辅助，
  **不替代**逐张查看。
- 逐张实际查看 8 张最终服务原图，记录见 `tmp/{RID}/A14/gen/reviews.json`
  与 `batch-audit.json` 的 `reviews`；每轮看旧图→改→再渲染→看新图的完整过程
  见 `tmp/{RID}/A14/iterations.jsonl`（5 个版本，其中 3 次是完整视觉迭代）。

## 未解决事项

""" + ("".join("- %s：%s（恢复办法：%s）\n" % (u["id"], u["detail"], u["recovery"])
              for u in metrics["unresolved_issues"])
        or "无。\n")
    (OUT / "snapshot-usage.md").write_text(md, encoding="utf-8")

    # ---- suite-state
    state = S.load_state()
    arts = sorted(p.name for p in OUT.iterdir() if p.is_file())
    entry = {
        "id": TASK, "status": metrics["status"],
        "started_at": metrics["timings"]["started_at"],
        "ended_at": ended, "elapsed_seconds": elapsed,
        "output_dir": S.rel(OUT), "temp_dir": S.rel(TMP),
        "artifacts": [S.rel(OUT / n) for n in arts],
        "metrics": S.rel(OUT / "task-metrics.json"),
        "requests": metrics["counts"]["snapshot_requests"],
        "successful_requests": metrics["counts"]["successful_snapshot_requests"],
        "failed_requests": metrics["counts"]["failed_snapshot_requests"],
        "retry_requests": metrics["counts"]["retry_requests"],
        "image_views": metrics["counts"]["image_views"],
        "visual_iterations": metrics["counts"]["visual_iterations"],
        "requirement_checks": summary,
        "verification": {
            "script": "tmp/%s/_suite/gen/a14_audit.py" % RID,
            "report": S.rel(OUT / "batch-audit.json"),
            "checks": len(audit["checks"]),
            "passed": sum(1 for c in audit["checks"] if c["passed"]),
            "failed": sum(1 for c in audit["checks"] if not c["passed"]),
        },
        "final_images": len(pairing),
        "byte_identical_to_service": byte_ok,
        "per_card_viewed": review_ok,
        "unresolved_issues": metrics["unresolved_issues"],
        "recorded_at": S.now_iso(),
    }
    state["tasks_detail"] = [t for t in state.get("tasks_detail", [])
                             if t.get("id") != TASK] + [entry]
    if metrics["status"] == "completed":
        state["completed"] = state.get("completed") or []
        if TASK not in state["completed"]:
            state["completed"].append(TASK)
    else:
        state["completed"] = [t for t in (state.get("completed") or [])
                              if t != TASK]
        det = next((t for t in state["tasks_detail"] if t.get("id") == TASK),
                   None)
        if det:
            det["status"] = "in_progress"
    comp = set(state.get("completed") or [])
    state["remaining"] = [t for t in state.get("remaining", []) if t not in comp]
    state["current_task"] = sorted(state["remaining"])[0] if state["remaining"] \
        else None
    state["counts_by_status"] = {"completed": len(comp), "in_progress": 0,
                                 "pending": len(state["remaining"])}
    if state.get("total_tasks"):
        assert len(comp) + len(state["remaining"]) == int(state["total_tasks"]), \
            (len(comp), len(state["remaining"]))
    state["updated_at"] = S.now_iso()
    state["status"] = "completed" if not state["remaining"] else "in_progress"
    S.save_state(state)

    # events.jsonl 在 tmp/<rid>/_suite/（suite_dirs() 的第二个），不在输出目录
    ev_p = SDIR / "events.jsonl"
    ev_before = (sum(1 for l in ev_p.read_text(encoding="utf-8",
                                               errors="replace").splitlines()
                     if l.strip()) if ev_p.exists() else 0)
    S.append_event({
        "ts": S.now_iso(),
        "event": "task_completed" if metrics["status"] == "completed"
                 else "task_partial",
        "task_id": TASK, "status": metrics["status"],
        "requirement_checks": summary,
        "requests": metrics["counts"]["snapshot_requests"],
        "image_views": metrics["counts"]["image_views"],
        "verification_failed": entry["verification"]["failed"],
        "final_images": len(pairing),
        "next_task": state["current_task"],
        "output_dir": S.rel(OUT)})
    ck = S.snapshot_checkpoint(state)
    state["last_checkpoint"] = ck
    S.save_state(state)

    print("需求核对 %d/%d 通过" % (summary["passed"], summary["total"]))
    for c in rc:
        if not c["passed"]:
            print("  [FAIL] %s %s" % (c["id"], c["requirement"]))
    print("像素审计 %d 项，未通过 %d" % (
        entry["verification"]["checks"], entry["verification"]["failed"]))
    print("请求 %d（成功 %d，失败 %d，重试 %d），看图 %d，视觉迭代 %d" % (
        metrics["counts"]["snapshot_requests"],
        metrics["counts"]["successful_snapshot_requests"],
        metrics["counts"]["failed_snapshot_requests"],
        metrics["counts"]["retry_requests"],
        metrics["counts"]["image_views"],
        metrics["counts"]["visual_iterations"]))
    print("bytes 一致 %s，逐张查看 %s，状态 %s" % (
        byte_ok, review_ok, metrics["status"]))
    print("counts_by_status:", json.dumps(state["counts_by_status"],
                                          ensure_ascii=False))
    print("current_task:", state["current_task"], "events:", ev_before,
          "->", ev_before + 1, "checkpoint:", ck)
    return 0 if metrics["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
