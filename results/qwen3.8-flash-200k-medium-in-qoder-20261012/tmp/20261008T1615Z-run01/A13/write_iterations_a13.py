"""A13 iterations.jsonl.

Every record is anchored to request ids that really exist in tmp/<run_id>/A13/requests.jsonl
(36 render requests, 28x200 + 8x500) so the log cannot claim an attempt that was never sent.
image_viewed is true only for rasters that were actually opened; the timestamps come from the
two viewing passes — the pre-compaction preview pass (16:46-17:02Z, which is what decided
direction, node colour and stroke) and this session's final pass (01:02-01:13Z, which
re-checked the 32px evidence and the delivered four).
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A13"
OUT = ROOT / "outputs" / RID / "A13"
reqs = [json.loads(l) for l in (TEMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()]
by_id = {r["request_id"]: r for r in reqs}
rows = []


def add(iid, version, parent, itype, req_part, problems, changes, result, completed,
        anchor=None, *, viewed=True, img=None, vat=None):
    """image_path defaults to the archived raw response for that request, which is the only
    place superseded versions still exist byte-for-byte; `img` overrides it with the live
    deliverable path when this version is still what outputs/<rid>/A13/ holds.

    `viewed` must be false when the request returned no raster (500/400) or when the image
    was archived but never opened — A12's log had to be corrected for exactly this.
    """
    rid_part = anchor or req_part
    rec = {"iteration_id": f"A13-{iid}", "task_id": "A13", "run_id": RID,
           "version": version, "parent_version": parent, "type": itype,
           "recorded_at": by_id[rid_part]["started_at"],
           "request_id": rid_part,
           "image_path": img or by_id[rid_part].get("response_file"),
           "image_viewed": viewed,
           "observed_problems": problems, "changes_made": changes,
           "recompare_result": result, "completed": completed, "path_base": "suite_root"}
    if viewed:
        rec["image_viewed_at"] = vat or by_id[rid_part]["ended_at"]
    rows.append(rec)


def find(sub):
    return next(k for k in by_id if sub in k)


# ---------------------------------------------------------------- direction previews
add("dir-01", "preview-A", None, "baseline", find("alt-A-512"),
    "方向 A「叠」首版：三个圆角框沿对角线平移，步距 0.17S、描边 0.060S；512 下轮廓干净。",
    "plan_a13.icon(direction='A') 用归一化比例出图，同一函数负责 512/32/横幅/海报。",
    "512 与 32 预览都成功（200），可作为候选。", False,
    img="tmp/%s/A13/preview/alt-A-512.png" % RID)
add("dir-02", "preview-B", None, "alternative", find("alt-B-512"),
    "方向 B「光」：正框＋45° 旋转框＋贯穿光束，与 A 的生成规则完全不同（角度 vs 平移）。",
    "rotated() 用 Transform matrix + alignment=CENTER 做真正的中心旋转。",
    "512 下角度感成立。", False, img="tmp/%s/A13/preview/alt-B-512.png" % RID)
add("dir-03", "preview-thumb", "preview-A", "visual", find("thumb-B-32"),
    "32px 缩略：B 读作禁止符号，斜束把中心负空间切成两半，与「叠加后仍清晰」相反；A 的三框在 32px 仍可数。",
    "放弃 B，A 成为唯一继续方向；缩略图只留在 tmp/preview，不进交付目录。",
    "方向确定：A。", True, img="tmp/%s/A13/preview/thumb-B-32.png" % RID)
# ---------------------------------------------------------------- node colour study
for k, (tag, note) in enumerate((("A2", "节点改红 #E5484D：与最上层红框同色，节点在 512 上被读成红框的一部分。"),
                                 ("A3", "去掉节点：中心负空间变成空洞，「光」的语义丢失。"),
                                 ("A4", "节点改蓝 #3E63DD：与最下层蓝框粘连，中心最暗。"),
                                 ("A5", "节点改琥珀 #F59E0B：三色之外的高亮，深色海报底上仍清晰。")),
                            start=1):
    add(f"node-{k:02d}", f"preview-{tag}", "preview-A", "alternative", find(f"alt-{tag}-512"),
        "墨色 #0F1724 节点在海报深色底上完全不可见（poster v01 暴露）。", note,
        "选定 A5 琥珀 #F59E0B 作为 node 色。" if tag == "A5" else "继续比较下一候选。",
        tag == "A5", img="tmp/%s/A13/preview/alt-%s-512.png" % (RID, tag))
# ---------------------------------------------------------------- small-size stroke
add("stroke-01", "check-32-base", "preview-A", "visual", find("v01-check-32-base"),
    "0.060S 描边在 32px 只有 1.9px，中间与上层框在交叠处粘连，四色中 amber 只剩 3.7px。",
    "原生 32px 渲染一张检查图（不入交付），并把大图描边提到 0.070S。",
    "32px 原生渲染四色齐全（check_a13 all_four_layers_survive_native_32_service_render）。",
    True, img="tmp/%s/A13/preview/check-32-base.png" % RID,
    vat="2026-10-09T01:03:08.419000+00:00")
add("stroke-02", "check-32-tuned", "check-32-base", "visual", find("v02-check-32-tuned"),
    "S<=48px 时 0.070S 仍偏细，需要一条可写进规范的小尺寸规则而不是临时加粗。",
    "同一几何、描边 0.085S 再渲一张 32px 对照。",
    "2.7px 描边下三框分离，四色齐全；规则写入 brand-system.json small_size_rule。", True,
    img="tmp/%s/A13/preview/check-32-tuned.png" % RID,
    vat="2026-10-09T01:02:57.519000+00:00")
add("stroke-03", "check-32-tuned", "check-32-base", "syntax-fix",
    find("v01-check-32-tuned"),
    "第一次尝试 0.085S 直接返回 HTTP 500 INTERNAL_ERROR，114 字节响应体没有任何线索。",
    "先按渲染失败重试一次，仍 500；确认不是偶发。",
    "两次 500 均归档（preview/requests/），转入受控实验。", False, viewed=False)
add("probe-01", "probes", "check-32-tuned", "syntax-fix", find("probe-p01"),
    "怀疑 borderRadius 与 border 宽度冲突：32px 下 radius=0.12*0.66*32=1.58 而 stroke=1.7。",
    "写 10 张最小探针 p01-p10，只改 radius/stroke 组合：1.58<1.7、1.0<1.7、1.6<1.7、1.9<2.0，"
    "以及 radius==stroke、radius>stroke 两组对照。",
    "6 张 500 / 4 张 200，边界确认：borderRadius < border 宽度即 500。", True,
    viewed=False)
add("probe-02", "probes", "probes", "requirement-change", find("probe-p10"),
    "服务不会给出提示，任何按比例算 radius 的生成器都可能在小画布上静默失败。",
    "plan_a13.frame() 加钳制 radius=max(radius, stroke)，并把结论写进 "
    "tmp/%s/_suite/notes/service-behaviour-from-a13.md 供后续题复用。" % RID,
    "check-32-tuned 重发返回 200（A13-v02-check-32-tuned）。", True, viewed=False)
# ---------------------------------------------------------------- finals
add("final-01", "v01", "probes", "baseline", find("v01-color"),
    "彩色图标 v01：透明底、4 构件、留白 0.30S。", "symbol(512,'color') 直接出图。",
    "200，6700 字节 RGBA。", True, img="outputs/%s/A13/symbol-color.png" % RID,
    vat="2026-10-09T01:03:27.331000+00:00")
add("final-02", "v01", "v01", "baseline", find("v01-black"),
    "纯黑图标必须与彩色版几何相同，且非透明像素 RGB 为 0。",
    "同一 icon() 调用 variant='black'，坐标一字不改，只换颜色。",
    "200；check_a13 的 geometry_identical_to_colour_symbol 与 painted_pixels_are_rgb_zero 通过。",
    True, img="outputs/%s/A13/symbol-black.png" % RID,
    vat="2026-10-09T01:03:13.235000+00:00")
add("final-03", "v01-banner", "v01", "baseline", find("v01-banner"),
    "横幅 v01：图标＋文字并排，右侧留白空着。",
    "ghost_layers() 把标志自身的对角位移以细线延伸到右边缘出血。",
    "200，但细线仍用 0.070S 时压出三条重带。", True)
add("final-04", "v01-poster", "v01", "baseline", find("v01-poster"),
    "海报 v01：五段文字沿页面散开、间距不均，82px 的 ghost 带直接穿过标题。",
    "ghost 降到 4px 细线；文字收进一块 night2 面板。",
    "200，构图问题记录在案，进入 v02。", True)
add("final-05", "v02-banner", "v01-banner", "visual", find("v02-banner"),
    "v01 横幅的 ghost 太重，与主标志抢注意力。",
    "ghost 描边固定 6px、透明度 0.22/0.18/0.14；Layerlight 加 1.5 字距。",
    "200，右侧出血读作结构而非装饰。", True)
add("final-06", "v02-poster", "v01-poster", "visual", find("v02-poster"),
    "散落的五行文字看起来像没排完。",
    "936x350 的 #151F33 圆角面板承载品牌行/标语/分隔线/日期/色条。",
    "200，但面板内间距仍不均。", True)
add("final-07", "v03-poster", "v02-poster", "visual", find("v03-poster"),
    "面板内基线节奏不一致，色条行贴住面板下沿。",
    "行距按 1.45em 盒重排，色条行下移。",
    "200；重排后 PNG 字节数与 v02 相同，用 server-timing（render;dur=256.1, miss）与 DSL 中 y=1146 确认确实重渲。",
    True)
add("final-08", "v04-poster", "v03-poster", "visual", find("v04-poster"),
    "色条与琥珀节点未在同一基线上。", "节点上移 6px 与三条色片共线。",
    "200，68069 字节；作为 v04 交付一版，随后被 v06 取代。", True,
    img="outputs/%s/A13/requests/A13-v04-poster-20261008T170130Z.response.bin" % RID,
    vat="2026-10-09T01:09:58.384000+00:00")
# ---------------------------------------------------------------- self-check round
add("audit-01", "check-v1", "v04", "requirement-change", find("v04-poster"),
    "写独立自检 check_a13.py：只读交付的 PNG/.snapshot，不预设任何坐标。首跑 46 项里 7 项失败。",
    "失败逐条查因：.body.txt 归档首行是 'POST <url>' 请求行，比对要先切出 DSL；"
    "海报的 mark 归一化被色条行的琥珀点污染，改为「填充块中心必须落在三框包围盒内」；"
    "banner/poster 的构件指纹与符号相差 0.001，是整数取整，比较改成 0.002 容差并写明理由；"
    "512→32 LANCZOS 缩小丢失 amber 被当成失败，实际是重采样属性，改为 measurement 如实记录；"
    "poster_has_its_own_composition 原来断言 <Opacity 数量更多，实测两图都是 3，改成比较两套互不重叠的色值。",
    "52 项全通过（含新增的留白与对比度检查）。", True, viewed=False)
add("audit-02", "v04-banner", "v02-banner", "visual", find("v03-banner"),
    "自检把留白规则扩展到应用图后暴露：横幅 v02 标志左边距 56px = 0.255S、到文字 64px = 0.291S，"
    "违反了自己写进规范的 0.30S。",
    "generate_a13.banner() 的边距改为 round(0.30*S)=66，文字列起点随之右移；"
    "check_a13 增加按 DSL 计算的 clear_space 与 WCAG 对比度检查。",
    "v04-banner 200（服务对同一 DSL 返回 cache hit，已在日志注明）；实测 left 0.300 / top 0.409 / bottom 0.409。",
    True, img="outputs/%s/A13/brand-banner.png" % RID,
    vat="2026-10-09T01:07:38.792000+00:00")
add("audit-03", "v05-poster", "v04-poster", "syntax-fix", find("v05-poster"),
    "想把 ghost 裁到标题之上，Stack clipBehavior=\"CLIP\" 返回 400 PARSE_ERROR："
    "No enum constant ...ClipBehavior.CLIP。",
    "抓 /widgets/painting/clip-rect/ 文档（shared-cliprect-20261009T011244Z）："
    "ClipRect 无尺寸参数、按自身布局边界裁剪、只接受一个子节点；非 NONE 的 clipBehavior 还需要 decoration。",
    "错误响应 277 字节如实归档，改用外层 Positioned 供尺寸 + 内层 ClipRect/Stack。", False,
    viewed=False)
add("audit-04", "v06-poster", "v05-poster", "visual", find("v06-poster"),
    "海报 v04 里 ghost 的下沿仍从 OPEN BETA 字面穿过，标题底不干净。",
    "ghost 组包进 ClipRect(0,0,1080,660)，细线在标题上方收束成竖向断口。",
    "200，62750 字节；看图确认标题落在纯色底上，52 项自检仍全通过。", True,
    img="outputs/%s/A13/launch-poster.png" % RID,
    vat="2026-10-09T01:13:23.048000+00:00")

with (TEMP / "iterations.jsonl").open("w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"records": len(rows),
                  "views": sum(1 for r in rows if r["image_viewed"]),
                  "completed_iterations": sum(1 for r in rows if r["completed"]),
                  "missing_requests": [r["request_id"] for r in rows
                                       if r["request_id"] not in by_id]},
                 ensure_ascii=False))
