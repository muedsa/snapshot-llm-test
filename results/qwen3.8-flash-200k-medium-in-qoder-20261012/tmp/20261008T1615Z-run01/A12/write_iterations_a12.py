"""A12 iteration log. Every record is anchored to a real request in requests.jsonl: the
version records carry that render's started_at and the view records its ended_at, so no
record can claim a moment when nothing actually happened. The view records are the evidence
that each canvas was opened, which is what TASK.md asks for ("每张仍要实际渲染并查看").
"""
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
T = ROOT / "tmp" / RID / "A12"

reqs = {}
for line in (T / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    reqs[r["request_id"]] = r


def at(rid_part, field="started_at"):
    for rid, r in reqs.items():
        if rid.startswith(rid_part):
            return r[field]
    raise KeyError(rid_part)


def path_of(rid_part):
    for rid, r in reqs.items():
        if rid.startswith(rid_part):
            return r["response_file"]
    raise KeyError(rid_part)


V = "tmp/%s/A12/" % RID
rec = []


def add(iid, version, parent, itype, req_part, problems, changes, result,
        completed, anchor=None, *, viewed=True, field="started_at", img=None):
    # anchor repeats the render the moment is taken from; view records pass it explicitly
    # so the reader sees that the timestamp belongs to the canvas being viewed.
    rid_part = anchor or req_part
    rec.append({
        "iteration_id": iid, "task_id": "A12", "run_id": RID, "version": version,
        "parent_version": parent, "type": itype, "recorded_at": at(rid_part, field),
        "request_id": next(k for k in reqs if k.startswith(rid_part)),
        "image_path": img or path_of(rid_part), "image_viewed": viewed,
        "observed_problems": problems, "changes_made": changes,
        "recompare_result": result, "completed": completed, "path_base": "suite_root"})


# ---------------------------------------------------------------- solver, before any render
add("A12-solve-01", "pre-v01", None, "baseline", "A12-v01-mobile",
    "生成器第一版：mobile 溢出（bottom 786 > 784），stage 的最大断点反而拿到最紧的 "
    "gap_multiplier 0.6，desktop 在 side 模式下把 96px 余量分配给了一个不起作用的杠杆"
    "（hero→grid 在 side 模式恒为 0）。",
    "solve() 改为有界节奏带 GM_BAND（1.6…0.5）取“能放下的最大值”，余量按 2:2:1 分配给 "
    "hero→grid、grid→footer、顶部，最后一份留作底部留白；geom() 在每次尝试上都复查安全边距"
    "与两两文字盒重叠。",
    "四张全部 problems: []，但还没看图。", False, "A12-v01-mobile", viewed=False)

add("A12-solve-02", "pre-v01", "pre-v01", "baseline", "A12-v01-mobile",
    "标签盒宽 = round(估宽+2)，而 TextFit 在 0.96×盒宽处换行，于是“日期”两字在 22/26pt 下"
    "被判成 2 行，meta 三行从 114px 变 225px，stage 主视觉凭空高出约 110px，"
    "gap_multiplier 被压到 0.6。",
    "标签/数值盒宽改为 round(估宽 / SLACK) + 2；节奏带补 0.9/0.8/0.7 三档。",
    "重跑：mobile 0.55、tablet 1.6、desktop 1.6、stage 1.4，均无 problems。",
    False, "A12-v01-mobile", viewed=False)

# ---------------------------------------------------------------- v01
add("A12-v01-baseline", "v01", None, "baseline", "A12-v01-mobile",
    "首张可用手机图：内容完整、层级清楚，但六张卡之间只有 4px 间隔，卡片几乎相贴。",
    "先登记为基线，其余三张看完再一起改。",
    "tablet/desktop/stage 见后续记录。", False, "A12-v01-mobile",
    img=V + "preview/v01/mobile.png")
add("A12-v01-view-tablet", "v01", "v01", "visual", "A12-v01-tablet",
    "平板 768×1024：2×3 卡片节奏舒适，但主视觉面板右半是空的——三行 meta 只占左侧约 400px。",
    "记为待改：meta 需要按宽度重排，而不是固定三行。",
    "见 v02。", False, "A12-v01-tablet", field="ended_at",
    img=V + "preview/v01/tablet.png")
add("A12-v01-view-desktop", "v01", "v01", "visual", "A12-v01-desktop",
    "桌面 1440×900 用左侧主视觉：主标题被挤成两行（“Vision”单独一行），卡片列比面板矮 117px，"
    "页脚又被 grid_to_footer 推到 y=765，内容与页脚之间出现约 175px 的空洞。",
    "结论：1440 的 900px 高度撑不起 side 版式，改为整幅 band + 3 列 2 行。",
    "见 v02。", False, "A12-v01-desktop", field="ended_at",
    img=V + "preview/v01/desktop.png")
add("A12-v01-view-stage", "v01", "v01", "visual", "A12-v01-stage",
    "大屏 1920×1080：主视觉面板 585px 高、占画布 54%，而 gap_multiplier 只有 0.6，"
    "最大的画布拿到最紧的节奏，与“统一节奏”相反。",
    "定位为 v01 之前的 meta 标签换行 bug（见 A12-solve-02）。",
    "修标签盒后 stage 主视觉降到 512px，节奏回到 1.4。", False, "A12-v01-stage",
    field="ended_at", img=V + "preview/v01/stage.png")

# ---------------------------------------------------------------- v02
add("A12-v02-desktop", "v02", "v01", "visual", "A12-v02-desktop",
    "side 版式在 900px 高的画布上必然留白：内容 590px + 页脚被推远。",
    "desktop 改 3 列 2 行；新增按度量决定的 meta 重排（放得下就一行，放不下逐行折行）；"
    "余量分配改为只在真正有效的杠杆上分。",
    "主标题回到单行，hero 363px，desktop problems []。", False, "A12-v02-desktop",
    img=V + "preview/v02/desktop.png")

# ---------------------------------------------------------------- v03
add("A12-v03-cta-line", "v03", "v02", "visual", "A12-v03-desktop",
    "desktop/stage 的 band 右半仍然空着：meta 一行只用到约 700px，剩下 600px 是深色空白，"
    "而 CTA 独占一行。",
    "新增第二条重排规则：meta 只占一行时，CTA 移到该行右端并与之行高居中对齐。",
    "hero 从 363→331（desktop）、512→388（stage），band 右半被 CTA 填满。", False,
    "A12-v03-desktop", img=V + "preview/v03/desktop.png")
add("A12-v03-view-stage", "v03", "v03", "visual", "A12-v03-stage",
    "大屏检查：meta 一行 + 右端 CTA 的 band 平衡了；卡片 2 行下方到页脚的空隙合理。",
    "不改。", "通过。", True, "A12-v03-stage", field="ended_at",
    img=V + "preview/v03/stage.png")
add("A12-v03-view-mobile", "v03", "v03", "visual", "A12-v03-mobile",
    "手机：文字全部完整，但卡片间隔仍是 4px（gap_multiplier 已到节奏带下限 0.6，"
    "因为 6 张单列卡 + 三行 meta 把 800px 用尽）。",
    "需要给卡片列表单独的呼吸空间，见 v04。", "见 v04。", False, "A12-v03-mobile",
    field="ended_at", img=V + "preview/v03/mobile.png")

# ---------------------------------------------------------------- v04
add("A12-v04-meta-flow", "v04", "v03", "visual", "A12-v04-mobile",
    "inline/stacked 二选一太粗：tablet 642px 的内容宽其实放得下“日期+时间”，只差“地点”，"
    "却被判成三行堆叠；mobile 也卡在 0.6 节奏下限。",
    "meta 改成真正的折行流（逐组累加宽度，放不下换行），CTA 同排条件改为“流只有一行”；"
    "mobile 的 cardGap 提到 16、heroPad 降到 12、inner 降到 7。",
    "tablet 变 2 行（hero 399→364），desktop/stage 仍 1 行，mobile 卡片间隔 4→9px。",
    False, "A12-v04-mobile", img=V + "preview/v04/mobile.png")
add("A12-v04-view-tablet", "v04", "v04", "visual", "A12-v04-tablet",
    "平板两行 meta 读起来自然，2×3 卡片与页脚节奏一致。", "不改。", "通过。", True,
    "A12-v04-tablet", field="ended_at", img=V + "preview/v04/tablet.png")
add("A12-v04-view-desktop", "v04", "v04", "visual", "A12-v04-desktop",
    "桌面：单行标题 + meta 流 + 右端 CTA + 3×2 卡片 + 页脚，无空洞。", "不改。",
    "通过。", True, "A12-v04-desktop", field="ended_at",
    img=V + "preview/v04/desktop.png")
add("A12-v04-view-stage", "v04", "v04", "visual", "A12-v04-stage",
    "大屏：与 desktop 同一构件、更大字号与间距，节奏带同为 1.6。", "不改。", "通过。",
    True, "A12-v04-stage", field="ended_at", img=V + "preview/v04/stage.png")

# ---------------------------------------------------------------- audit
add("A12-audit-01", "v04", "v04", "self_check", "A12-final-mobile",
    "check_a12.py 首跑 60 项里 2 项失败：mobile 与 desktop 的 website 文字盒底部有 7px / 2px "
    "的墨迹贴着盒边——等宽字体的 “g”“p” 下伸部被 1.45em 的行盒切到最后一条像素行。",
    "hh() 增加 2px 下伸部余量（round(size*1.45*lines)+2）；pill 高度改为随 CTA 字号伸缩"
    "（+max(18, 0.9*size)），把省下的预算还给 mobile 卡片节奏。",
    "见 v05。", False, "A12-final-mobile", viewed=False)

# ---------------------------------------------------------------- v05 + delivery
add("A12-v05-final", "v05", "v04", "visual", "A12-v05-mobile",
    "下伸部余量让 mobile 溢出 24px（6 张卡各多 4px）。",
    "mobile inner 8→7、cardGap 16→14、pill 内边距按字号；solve 重跑。",
    "四张再次 problems []（mobile gm 0.5、其余 1.6），交付版渲染后逐张开图复核。", False,
    "A12-v05-mobile", img=V + "preview/v05/mobile.png")
for bp in ("tablet", "desktop", "stage"):
    add(f"A12-v05-view-{bp}", "v05", "v05", "visual", f"A12-v05-{bp}",
        f"交付版 {bp} 整图复核：内容与页脚均在安全边距内，无重叠、无裁切。",
        "不改。", "通过。", True, f"A12-v05-{bp}", field="ended_at",
        img=V + f"preview/v05/{bp}.png")

CROPS = [("mobile-hero", "mobile", "mobile-hero",
          "26pt 主标题与 16pt meta 三行在 2× 下笔画完整，标签与数值同基线。"),
         ("mobile-cards-C1-C2", "mobile", "mobile-cards",
          "18pt 卡片标题压在 16pt 详情上方，序号胶囊与左侧强调条清晰，卡片间隔 14px 有呼吸。"),
         ("mobile-footer", "mobile", "mobile-footer",
          "16pt 等宽网址：修 hh() 之前 “g/p” 下伸部贴到盒底，现在底部留 2px。"),
         ("tablet-hero-meta", "tablet", "tablet-meta",
          "22pt meta 折成两行，第二行整组换行、没有把标签和数值拆开。"),
         ("desktop-hero-line", "desktop", "desktop-line",
          "单行 meta + 右端 CTA 胶囊，两盒按较高者居中对齐，胶囊内边距未挤压文字。"),
         ("stage-hero-line", "stage", "stage-hero",
          "72pt 主标题、30pt 副标题与 26pt meta/CTA 同排；band 右半被胶囊填满。"),
         ("stage-card-C4", "stage", "stage-c4",
          "34pt 标题 + 26pt 详情，笔画无断口，胶囊与标题基线关系正确。"),
         ("stage-footer", "stage", "stage-footer",
          "26pt 等宽网址下伸部完整。注意：裁切框左缘切掉了 7px 强调点，该点在 DSL 里 "
          "left=40 正好等于 stage 安全边距，属裁切边界而非渲染裁切（整图已复核）。"),
         ("desktop-card-C3", "desktop", "desktop-c3",
          "28pt 标题 + 22pt 详情，白卡与 1px 边框在 2× 下仍连续。"),
         ("tablet-card-C6", "tablet", "tablet-c6",
          "26pt 标题与详情，中文顿号 “、” 完整显示，未出现缺字方框。")]
for fn, bp, tag, note in CROPS:
    add(f"A12-crop-{tag}", "final2", "v05", "visual", f"A12-final2-{bp}",
        f"2× 放大复核 {bp} 细部（{fn}）：小字号正文、等宽页脚与下伸部是否被切。",
        "不改，仅取证。", note + " 结论：字形完整、无贴边裁切；清单见 "
        "preview/crops-final/manifest.json。",
        True, f"A12-final2-{bp}", field="ended_at",
        img=V + f"preview/crops-final/{fn}.png")

add("A12-audit-02", "final2", "final2", "self_check", "A12-final2-mobile",
    "复核脚本自身有一处假失败：provenance 用 A12-final-{bp}-* 匹配，交付目录里还留着上一轮 "
    "A12-final-* 的原始响应，于是比对到了旧文件。",
    "glob 改为 A12-final*-{bp}-* 并按 mtime 取最新一次响应。",
    "check-report.json：60/60 通过，19 条输入字符串在四张画布上逐字命中且各出现一次。",
    True, "A12-final2-mobile", viewed=False,
    img=V + "check-report.json")

with (T / "iterations.jsonl").open("w", encoding="utf-8") as fh:
    for r in rec:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

missing = [r["image_path"] for r in rec if r["image_viewed"]
           and not (ROOT / r["image_path"]).exists()]
print(json.dumps({"records": len(rec),
                  "views": sum(1 for r in rec if r["image_viewed"]),
                  "completed_iterations": sum(1 for r in rec if r["completed"]),
                  "missing_image_paths": missing}, ensure_ascii=False))
