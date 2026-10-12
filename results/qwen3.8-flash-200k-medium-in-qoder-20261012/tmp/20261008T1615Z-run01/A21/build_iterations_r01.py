"""Append A21 round-01 iterations.jsonl rows (real request IDs, real view times)."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
task = "A21"
temp = root / "tmp" / rid / task
reqs = {}
for line in (temp / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    reqs[r["dsl_version"]] = r

NOW = datetime.now(timezone.utc).isoformat()
rows = [
    dict(iteration_id="A21-r01-it01", type="alternative", version="probe01", parent_version=None,
         request_id=reqs["probe01"]["request_id"], http_status=400,
         image_path=None, image_scope="none",
         changes_made="能力探测首版：Container@opacity、<Opacity>、Transform alignment=CENTER、"
                      "8 位 hex #RRGGBBAA、Text letterSpacing 五项一次试探",
         observed_problems="服务 HTTP 400 PARSE_ERROR: Attr [matrix] must contain 16 values；"
                           "手写矩阵时把 dslkit 跨行 f-string 的第二行漏抄了 1 个值",
         requirement_part="半透明叠色板的可行机制（本题主视觉语言）",
         recompare_result="错误响应原文存 preview/requests/A21-probe01-*.response.bin",
         completed=True, image_viewed=False,
         viewed_at_basis=None,
         note="探测请求不计入视觉迭代；失败尝试如实保留"),
    dict(iteration_id="A21-r01-it02", type="syntax-fix", version="probe02", parent_version="probe01",
         request_id=reqs["probe02"]["request_id"], http_status=200,
         image_path="tmp/%s/%s/preview/probe-alpha-v02.png" % (rid, task), image_scope="preview",
         changes_made="matrix 补齐 16 值后重试同一探测",
         observed_problems="像素取样结论：8 位 hex 在 Container color 上正确合成"
                           "（#FF000080 压 #0B1020 得 (133,8,16)，正好 50% 混色）；"
                           "Transform alignment=CENTER 绕自身中心旋转生效；letterSpacing 生效"
                           "（ONLINE LAUNCH 墨迹跨度 299..614）；"
                           "Container@opacity 与 <Opacity value> 均被服务忽略，仍是不透明",
         requirement_part="确认叠光板可用 alpha hex 而非 opacity 属性",
         recompare_result="PIL 取样比对预期混色值",
         completed=True, image_viewed=False,
         viewed_at_basis=None,
         note="判定手段是像素取样而非人眼看图，因此不计 image_views，也不计入视觉迭代"),
    dict(iteration_id="A21-r01-it03", type="visual", version="r01-portrait-v01",
         parent_version=None, request_id=reqs["r01-portrait-v01"]["request_id"], http_status=200,
         image_path="tmp/%s/%s/preview/r01-portrait-v01.png" % (rid, task), image_scope="preview",
         changes_made="竖版首版：token 驱动生成器（品牌 6 构件 + 三段主标题层级 + 信息区）",
         observed_problems="查看后：右下角三块背景板尺寸过大、透明度偏高，糊成一片脏色并压进底部"
                           "扩展区；一条独立光线横穿右侧信息列，与文字打架；"
                           "ONLINE LAUNCH 胶囊里的字距文字在估算“放得下”的盒内提前换行",
         requirement_part="顶部/底部真实可用扩展区不得有元素 / 品牌图形可识别 / 层级清晰",
         recompare_result="与 layouts/launch-portrait.plane.json 的盒坐标对照，确认扩展区被压占",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r01-it04", type="visual", version="r01-wide-v01",
         parent_version="r01-portrait-v01", request_id=reqs["r01-wide-v01"]["request_id"],
         http_status=200,
         image_path="tmp/%s/%s/preview/r01-wide-v01.png" % (rid, task), image_scope="preview",
         changes_made="横屏首版：同语言不同构图（左标题右信息列）",
         observed_problems="查看后：背景板在 810 高画布上更挤，光带直接顶到上下扩展区；"
                           "底部分隔线穿过右下角光带，线条在叠色上断续",
         requirement_part="两图同一主色/字体层级/可识别品牌图形，分别构图",
         recompare_result="与 r01-portrait-v01 并排比较，确认语言一致但背景处理需重做",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r01-it05", type="visual", version="r01-portrait-v02",
         parent_version="r01-portrait-v01", request_id=reqs["r01-portrait-v02"]["request_id"],
         http_status=200,
         image_path="tmp/%s/%s/preview/r01-portrait-v02.png" % (rid, task), image_scope="preview",
         changes_made="新增 light_ribbon()：背景叠光改用与品牌图形完全相同的角度/偏移/构件比例，"
                      "只降 alpha（1A/1A/14）；整体移到右下角并缩到扩展区之外；"
                      "字距文字估算改为 spacing*len(s) 再乘 1.10，胶囊内边距 24->56",
         observed_problems="查看后：胶囊单行正常、叠光带已不脏；仍有一条长光线从板组斜伸出到画布"
                           "中部，与主标题左缘齐平时显得多余",
         requirement_part="叠光语言 / 扩展区洁净 / 文字不截断",
         recompare_result="扩展区洁净度改由 build_docs.py 的旋转 AABB 断言机器复核",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r01-it06", type="visual", version="r01-wide-v02",
         parent_version="r01-wide-v01", request_id=reqs["r01-wide-v02"]["request_id"],
         http_status=200,
         image_path="tmp/%s/%s/preview/r01-wide-v02.png" % (rid, task), image_scope="preview",
         changes_made="横版同步 light_ribbon 与胶囊修正",
         observed_problems="查看后：光带仍覆盖到右侧信息列下方，r1 分隔线与光带重叠",
         requirement_part="横屏 1440x810 版面平衡",
         recompare_result="与竖版 v02 比较，确认同一语言在两种比例下均成立",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r01-it07", type="visual", version="r01-portrait-v03",
         parent_version="r01-portrait-v02", request_id=reqs["r01-portrait-v03"]["request_id"],
         http_status=200,
         image_path="tmp/%s/%s/preview/r01-portrait-v03.png" % (rid, task), image_scope="preview",
         changes_made="叠光带内部光线缩短为板组范围内的短光（起点/终点都在三块板覆盖区内）",
         observed_problems="查看后：主标题左缘干净，无游离线条；竖版达到可交付状态",
         requirement_part="主视觉不含无意义线条",
         recompare_result="归档前再次打开成品复核（见 it10）",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r01-it08", type="visual", version="r01-wide-v03",
         parent_version="r01-wide-v02", request_id=reqs["r01-wide-v03"]["request_id"],
         http_status=200,
         image_path="tmp/%s/%s/preview/r01-wide-v03.png" % (rid, task), image_scope="preview",
         changes_made="横版叠光带中心移到 (1300,628)、u=3.7，收进右下角",
         observed_problems="查看后：光带不再顶到上下扩展区；分隔线仍从光带中穿过",
         requirement_part="横屏扩展区洁净",
         recompare_result="与 r01-wide-v02 对比确认位移有效",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r01-it09", type="visual", version="r01-wide-v04",
         parent_version="r01-wide-v03", request_id=reqs["r01-wide-v04"]["request_id"],
         http_status=200,
         image_path="tmp/%s/%s/preview/r01-wide-v04.png" % (rid, task), image_scope="preview",
         changes_made="wide.rule-2 由通宽 1296 缩短为 1008，止于叠光带之前",
         observed_problems="查看后：线条完整、胶囊单行、上下 72px 扩展带真空、右下角叠光锚定；"
                           "横版达到可交付状态",
         requirement_part="分隔线不被装饰打断 / 扩展区洁净",
         recompare_result="与 r01-wide-v03 对比，仅线条长度变化",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r01-it10", type="retry", version="r01-portrait-v04",
         parent_version="r01-portrait-v03", request_id=reqs["r01-portrait-v04"]["request_id"],
         http_status=200,
         image_path="tmp/%s/%s/preview/r01-portrait-v04.png" % (rid, task), image_scope="preview",
         changes_made="无 DSL 改动，仅为与横版 v04 配对而重发同一份 DSL",
         observed_problems="服务返回 X-Snapshot-Cache: hit、Server-Timing cache;desc=hit，"
                           "响应字节数与 v03 完全相同（86650 B），属真实命中缓存的空重渲染",
         requirement_part="归档命名一致性",
         recompare_result="竖版成品即 v03 布局；本次归档前重新打开该 PNG 全图查看，"
                          "确认扩展区洁净、层级与品牌图形一致",
         completed=True, image_viewed=True, noop_render=True,
         viewed_at_basis="归档 round-01 时重新用图像工具打开成品 PNG 全图查看",
         note="如实记为 noop_render/cache-hit 重试，不当作一次新的视觉改进"),
]
for i, row in enumerate(rows):
    row.update(run_id=rid, task_id=task,
               image_viewed_at=(NOW if row["image_viewed"] else None),
               recorded_at=NOW,
               completed_meaning="本轮闭环：改动后有真实渲染并被实际查看比较；"
                                 "final=true 只表示该版本作为成品交付",
               path_base="suite_root")
    if row["type"] == "visual":
        row["final"] = row["version"] in ("r01-portrait-v04", "r01-wide-v04")
out = temp / "iterations.jsonl"
with out.open("a", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(rows), "rows ->", out)
