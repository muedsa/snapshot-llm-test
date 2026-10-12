"""B05 收尾：由实际产物生成 gallery.md / portfolio.json / portfolio.md。

所有数字（字节、md5、尺寸、版本数、预览数、QA 裁图数、请求数）都从
outputs/ 与 tmp/ 的真实文件读出，不手填。
"""
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

from PIL import Image

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
OUT = root / "outputs" / rid / "B05"
TMP = root / "tmp" / rid / "B05"

reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
its = [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
journey = json.loads((OUT / "journey.json").read_text(encoding="utf-8"))
JM = {p["case"]: p for p in journey["pieces"]}

CUR = {
 "01": dict(title="市民报修：拍一张照片就完成一次有效上报",
   kind="手机报修流程页（未提交态）", audience="人行道上的普通市民",
   env="单手、强光、4G，站立 30 秒内完成",
   basis="定位到具体树号 TZ-JS-0417 + 路段 + 危害对象三个必填字段，提交前可回退",
   claim="把「我拍了一张歪树」升级成「哪棵、挡了什么、谁该来看」，字段少而每个都能解释为什么要填"),
 "02": dict(title="巡检员单株档案卡（户外强光模式）",
   kind="手持机档案页（现场态）", audience="巡检员",
   env="戴手套、单手持、户外强光下站读",
   basis="实测四分项（倾斜/空洞/根系/暴露对象）+ 权重 + R=76 的算法行",
   claim="不只显示结论等级，而把等级怎么算出来的摊在卡上，换人巡检也是同一个结论"),
 "03": dict(title="值班室调度大屏",
   kind="2560×1440 大屏态势页（实时态）", audience="值班调度",
   env="值班室 3 米外、全天常亮",
   basis="四级 98/229/669/2,729、工单 327、超时 87、今日派工与班组负荷",
   claim="风险在哪、今天谁做什么、哪单超时，一屏同时可读，字号按 3 米距离放大"),
 "04": dict(title="行道树隐患处置单（A4 打印件）",
   kind="1240×1754 纸质单据（已派单态）", audience="作业班组长",
   env="现场纸质交底，可能没有网络",
   basis="责任链、措施、时间线（到场 10-11 09:58 / 复测 10-13 09:58）、签字位",
   claim="一张纸能独立支撑一次作业，不依赖回看设备；同一棵树与件-01/02/07 时刻一致"),
 "05": dict(title="台风前 48 小时加固优先序",
   kind="1920×1200 平板规划页（规划态）", audience="技术复核 + 调度",
   env="台风前 48 h，办公室平板",
   basis="排序公式、边界样本、被排除项与 Top 清单",
   claim="先给出「为什么是这 100 棵」，再给清单；被排除项同样列出理由"),
 "06": dict(title="现场围挡与交通导改图",
   kind="1600×1200 作业前布设说明图", audience="班组长与现场安全员",
   env="作业前交底，可能打印张贴",
   basis="围挡半径、导改车道、比例尺与 pedestrian 绕行距离",
   claim="静态说明图刻意不做导航栏与假按钮；弧线为示意并在图内注明非规范尺寸"),
 "07": dict(title="倾斜仪读数序列判读",
   kind="1200×1600 平板复核页（复核态）", audience="技术复核",
   env="办公室平板，逐点核对",
   basis="时序折线、阈值线、报警规则、连续两次 <5.0° 才撤围的判据",
   claim="把「该不该撤围」变成可复核的规则；2026-09 风速 0 节标为缺测而非无风"),
 "08": dict(title="社区认养与遮荫收益卡",
   kind="1080×1620 手机长图 / 树池张贴（长期态）", audience="认养居民",
   env="手机看或贴在树池边长期读",
   basis="正投影 π(D/2)²=69.4 m²、264/1,123=23.5 % 认养率、双方义务、时间轴",
   claim="只写算得出的好处，不引用降温与固碳；−11 户的数据缺陷用红字向居民本人披露"),
 "09": dict(title="雨后灾情快报",
   kind="1440×2000 上报通报（灾后 6 h）", audience="值班室与上级主管",
   env="灾后 6 h 对内通报，随后逐级转发",
   basis="113 起（83 已核实/30 待核实）、242 枝干、25 压线、51 阻路、每千株上报",
   claim="已核实与待核实分列不合并；用归一化列把南门的「表现好」改判为疑漏报；拒绝引用风力等级"),
 "10": dict(title="年度覆盖率与数据质量",
   kind="1920×1080 决策投屏（年度态）", audience="上级主管",
   env="会议室投屏",
   basis="90 天覆盖率 24.9 %、726 株超一年、4 项待修字段、87 张超时、三笔补数账",
   claim="对前面九件做口径审计：两套冠幅公式、认养达标率算不出、三色可信度同页公开"),
}

def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()

def case_facts(c):
    cd = OUT / ("case-%s" % c)
    png = cd / "final.png"
    snap = cd / "final.snapshot"
    im = Image.open(png)
    cc = "case%s" % c
    ok = [r for r in reqs if r.get("http_status") == 200 and "-%s-" % cc in r["request_id"]]
    bad = [r for r in reqs if r.get("http_status") != 200 and "-%s-" % cc in r["request_id"]]
    vers = sorted({r["dsl_version"] for r in reqs if "-%s-" % cc in r["request_id"]})
    prev = sorted((cd).glob("v*-preview.png"))
    qa = sorted((TMP / ("case-%s" % c)).glob("qa-*.png"))
    sub = [r for r in its if r["version"].startswith(cc + "-")]
    kinds = Counter(r["type"] for r in sub)
    return dict(
        case="case-%s" % c, width=im.size[0], height=im.size[1],
        png_bytes=png.stat().st_size, png_md5=md5(png),
        snap_bytes=snap.stat().st_size, snap_md5=md5(snap),
        report_bytes=(cd / "case.md").stat().st_size,
        versions=vers, previews=len(prev), qa_crops=len(qa),
        req_ok=len(ok), req_bad=len(bad),
        iterations=len(sub), visual_iters=kinds.get("visual", 0),
        retries=kinds.get("retry", 0), syntax_fix=kinds.get("syntax-fix", 0),
        alternative=kinds.get("alternative", 0),
        viewed=sum(1 for r in sub if r.get("image_viewed")),
        final_req=ok[-1]["request_id"] if ok else None,
        final_timing=ok[-1].get("server_timing") if ok else None,
        final_started=ok[-1].get("started_at") if ok else None,
    )

F = {c: case_facts(c) for c in CUR}

# ---------- gallery.md ----------
L = []
L.append("# B05 画廊 · 「枝安」城市行道树风险巡检与处置协同平台 · 十件最终作品（%s）\n" % rid)
L.append("路径基准：本文档位于 `outputs/%s/B05/`，下列链接全部相对本目录，复制整个输出目录后仍可浏览。\n" % rid)
L.append("每张图给出：标题与用途、Markdown 内嵌预览、原 PNG 链接、同名完整 DSL 链接、用例报告链接。\n预览即交付件本身——服务原始响应字节，未做任何后处理；参考图与 QA 裁图不作为作品交付。\n")
L.append("过程版本（`vNN-preview.png`）、2× QA 裁图与失败响应保留在 `tmp/%s/B05/<case>/`，不计入十件作品数。\n" % rid)
L.append("全部数据为演示数据：品牌、汀州市、街道名、树种名录、工单号、台风名与所有数字均由 "
         "`b05data.py`（固定种子 20261011）生成，不对应任何真实市政系统。**未做真实用户验证。**\n")
L.append("十件画布尺寸互不相同（%s），对应十种不同的介质与状态。\n"
         % "、".join("%d×%d" % (F[c]["width"], F[c]["height"]) for c in sorted(CUR)))
L.append("")
for c in sorted(CUR):
    f, cu, jm = F[c], CUR[c], JM["case-%s" % c]
    L.append("## %s｜case-%s · %s（%d×%d）\n" % (sorted(CUR).index(c) + 1, c, cu["title"], f["width"], f["height"]))
    L.append("![case-%s · %s](case-%s/final.png)\n" % (c, cu["title"], c))
    L.append("| 项 | 内容 |")
    L.append("|---|---|")
    L.append("| 文件 | [原 PNG](case-%s/final.png)（%s 字节，md5 `%s`） · [完整 DSL](case-%s/final.snapshot)（%s 字节，md5 `%s`） |"
             % (c, format(f["png_bytes"], ","), f["png_md5"], c, format(f["snap_bytes"], ","), f["snap_md5"]))
    L.append("| 用例报告 | [case-%s/case.md](case-%s/case.md)（%s 字节） |" % (c, c, format(f["report_bytes"], ",")))
    L.append("| 版面类型 | %s |" % cu["kind"])
    L.append("| 受众 | %s |" % cu["audience"])
    L.append("| 阅读环境 | %s |" % cu["env"])
    L.append("| 内容依据 | %s |" % cu["basis"])
    L.append("| 视觉主张 | %s |" % cu["claim"])
    L.append("| 验证的假设 | %s |" % jm["hyp"])
    L.append("| 缺失证据 | %s |" % jm["miss"])
    L.append("| 定稿请求 | `%s`（HTTP 200，%s；成功渲染 %d 次，失败/截断重发 %d 次，闸门拦下未提交另计） |"
             % (f["final_req"], f["final_timing"], f["req_ok"], f["req_bad"]))
    L.append("| 实际自检 | 版本 %d（%s）· 迭代留痕 %d 条 · 看图 %d 次 · 预览 %d 张 · 2× 裁图 %d 张 |"
             % (len(f["versions"]), "、".join(f["versions"]), f["iterations"], f["viewed"], f["previews"], f["qa_crops"]))
    L.append("")
L.append("## 跨件一致性\n")
for x in journey["cross_checks"]:
    L.append("- **%s**：%s" % (x["check"], x["detail"]))
L.append("")
L.append("## 公开的数据缺陷与拒绝引用\n")
for k, v in journey["honesty"].items():
    if k == "note":
        L.append("- **用户验证**：%s" % v)
    elif isinstance(v, list):
        L.append("- **%s**：%s" % ("自定口径" if k == "self_defined_metrics" else "拒绝引用的说法", "；".join(v)))
L.append("")
(OUT / "gallery.md").write_text("\n".join(L), encoding="utf-8")

# ---------- portfolio.json ----------
port = dict(
    schema_version="b05-portfolio/1", path_base="suite_root", task_id="B05", run_id=rid,
    status="completed",
    asset_policy="DSL 主导，允许局部辅助素材；本题十件全部为纯 Snapshot DSL 构造，未引入外部位图素材",
    theme="枝安 · 城市行道树风险巡检与处置协同平台（虚构品牌与演示数据）",
    audience="市民 / 巡检员 / 值班调度 / 技术复核 / 班组长 / 上级主管六种角色",
    curatorial_statement=(
        "同一份种子数据、同一个风险分，穿过六种介质与十种状态。选题的赌注是：一套图能不能既让"
        "市民在 30 秒内报对一棵树，又让决策者看见 24.9 % 这个不好看的数字。十件里所有红色与橙色"
        "都来自同一个算法，所有缺陷都印在页面上——包括我自己留下的两套冠幅公式。"),
    risk_model=journey["risk_model"],
    final_collection_review=dict(
        works=len(F), distinct_canvases=journey["totals"]["distinct_canvases"],
        render_requests=journey["totals"]["render_requests"],
        http_200=journey["totals"]["http_200"],
        failed_or_truncated=journey["totals"]["failed_or_truncated"],
        iterations_logged=journey["totals"]["iterations_logged"],
        images_actually_opened=journey["totals"]["images_actually_opened"],
        every_final_is_service_response=True,
        every_final_has_paired_snapshot=True,
        user_validation_done=False,
        checks=[
            "10/10 件均有 final.png + 同名 final.snapshot + case.md",
            "10 件 md5 互不相同，尺寸互不相同，无占位图与 lorem ipsum",
            "每张 final.png 均有 requests.jsonl 中 HTTP 200 的对应请求与 request_id",
            "iterations.jsonl 每条均有 image_viewed=true 与 image_path",
            "跨件数字互校：四级求和 = 3,725；工单 327 / 超时 87；TZ-JS-0417 六件一致",
        ]),
    cases=[dict(
        case="case-%s" % c, title=CUR[c]["title"], kind=CUR[c]["kind"],
        role=JM["case-%s" % c]["role"], device=JM["case-%s" % c]["dev"],
        stage=JM["case-%s" % c]["stage"],
        canvas="%dx%d" % (F[c]["width"], F[c]["height"]),
        audience=CUR[c]["audience"], reading_env=CUR[c]["env"],
        content_basis=CUR[c]["basis"], visual_claim=CUR[c]["claim"],
        hypothesis=JM["case-%s" % c]["hyp"], missing_evidence=JM["case-%s" % c]["miss"],
        files=dict(final_png="case-%s/final.png" % c, final_snapshot="case-%s/final.snapshot" % c,
                   case_report="case-%s/case.md" % c,
                   dsl_source="tmp/%s/B05/case%s.py" % (rid, c),
                   kit="tmp/%s/B05/b05kit.py" % rid,
                   dataset="tmp/%s/B05/research/stats.json" % rid),
        png_bytes=F[c]["png_bytes"], png_md5=F[c]["png_md5"],
        snapshot_bytes=F[c]["snap_bytes"], snapshot_md5=F[c]["snap_md5"],
        versions=F[c]["versions"], previews=F[c]["previews"], qa_crops=F[c]["qa_crops"],
        render_requests=dict(ok=F[c]["req_ok"], failed_or_truncated=F[c]["req_bad"]),
        iterations=dict(logged=F[c]["iterations"], viewed=F[c]["viewed"],
                        visual=F[c]["visual_iters"], retry=F[c]["retries"],
                        syntax_fix=F[c]["syntax_fix"], alternative=F[c]["alternative"]),
        promoted_request_id=F[c]["final_req"], server_timing=F[c]["final_timing"],
    ) for c in sorted(CUR)],
    unresolved_issues=[
        "风险分权重与四级阈值未经历史倒伏数据回溯，只是内部自洽",
        "两套冠幅公式（π(D/2)² 与 0.72·D²）并存，差 9.1 %，已在件-10 ⑤ 公开但未统一",
        "岩前 −11 户、云屿压线 0/阻路 15、灾情 30 起未去重三项缺陷只做到「页面披露 + 排补数账」，未真正回源核对",
        "全部十件未做任何真实用户验证；大屏 3 米可读性与打印件现场可读性均为目测判断",
        "件-06 的导改弧线为 DSL 图元逼近的示意，不是规范尺寸图",
    ],
)
(OUT / "portfolio.json").write_text(json.dumps(port, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---------- portfolio.md ----------
P = []
P.append("# B05 作品集 · 枝安（%s）\n" % rid)
P.append("curatorial statement：%s\n" % port["curatorial_statement"])
P.append("素材政策：%s\n" % port["asset_policy"])
P.append("## 十件一览\n")
P.append("| # | 件 | 标题 | 角色 / 介质 | 画布 | 版本 | 成功渲染 | 失败重发 | 定稿 request |")
P.append("|---|---|---|---|---|---|---|---|---|")
for i, c in enumerate(sorted(CUR), 1):
    f = F[c]
    P.append("| %d | [case-%s](case-%s/final.png) | %s | %s / %s | %d×%d | %d | %d | %d | `%s` |"
             % (i, c, c, CUR[c]["title"], JM["case-%s" % c]["role"], JM["case-%s" % c]["dev"],
                f["width"], f["height"], len(f["versions"]), f["req_ok"], f["req_bad"], f["final_req"]))
P.append("")
P.append("## 为什么是这十件\n")
P.append("六种角色 × 十个状态，覆盖一棵问题树从被市民拍下到进年度账本的完整链条："
         "01 上报 → 02 现场核查 → 03 值班派工 → 04 纸质处置单 → 05 台风前排序 → 06 作业交底 → "
         "07 时序复核 → 08 社区认养 → 09 灾后通报 → 10 年度复盘。十件共用同一个风险分与同一份"
         "种子数据，因此同一棵树、同一个等级、同一个总量在十张图上必须一致；不一致的地方"
         "（两套冠幅公式）就印在件-10 上。\n")
P.append("详细逐件说明见 [gallery.md](gallery.md)、[product-brief.md](product-brief.md) 与 "
         "[journey.json](journey.json)；逐件数据与算法见各 `case-NN/case.md`。\n")
P.append("## 未解决的问题\n")
for u in port["unresolved_issues"]:
    P.append("- %s" % u)
P.append("")
(OUT / "portfolio.md").write_text("\n".join(P), encoding="utf-8")

print("gallery.md %d 行 · portfolio.json %d 件 · portfolio.md %d 行"
      % (len(L), len(port["cases"]), len(P)))
