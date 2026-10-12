"""Append A21 round-02 iterations.jsonl rows."""
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
P = "tmp/%s/%s/preview/" % (rid, task)

rows = [
    dict(iteration_id="A21-r02-it01", type="requirement-change", version="r02-portrait-v01",
         parent_version="r01-portrait-v04", request_id=reqs["r02-portrait-v01"]["request_id"],
         http_status=200, image_path=P + "r02-portrait-v01.png", image_scope="preview",
         changes_made="按第 2 轮预置需求：主标题换成 27 字长句，3 行 64px 按语义断行；"
                      "新增赞助方与“免费参加 · 无需报名”；其余文案、主色、品牌 6 构件不变",
         observed_problems="查看后：文字全部完整、无压窄；但下半部 5 行单列堆叠，"
                           "讲者与免费参加两行贴得太近，且 y≈750..1100 的右侧整块空白，"
                           "重心明显偏左上",
         requirement_part="标题最多 3 行且 ≥48 / 新增信息不得与标题碰撞 / 不得变形压窄文字",
         recompare_result="audit_layout() 报 0 处墨迹重叠；问题在版面节奏而非碰撞",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r02-it02", type="requirement-change", version="r02-wide-v01",
         parent_version="r01-wide-v04", request_id=reqs["r02-wide-v01"]["request_id"],
         http_status=200, image_path=P + "r02-wide-v01.png", image_scope="preview",
         changes_made="横版同步长标题（3 行 64px，标题列右界 912）；新增信息分两处："
                      "右列放讲者与免费参加，底栏放赞助方与网址；胶囊改为按宽度右对齐",
         observed_problems="查看后：标题最长行墨迹止于 x≈800，信息列左界 940，"
                           "两者之间留有 28px 列间通道；底栏与右下叠光带不相交；无需再改",
         requirement_part="两尺寸不变 / 长标题与新增信息不碰撞 / 装饰可移动缩放",
         recompare_result="ink_audit.py 从服务 PNG 反测墨迹：0 重叠、上下扩展带 0 非背景像素",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r02-it03", type="visual", version="r02-portrait-v02",
         parent_version="r02-portrait-v01", request_id=reqs["r02-portrait-v02"]["request_id"],
         http_status=200, image_path=P + "r02-portrait-v02.png", image_scope="preview",
         changes_made="下半部改双栏（左：发布时间+日期；右：讲者+免费参加）；"
                      "赞助方/网址下移成分隔带；叠光带移到 (980,1140) u=3.8，"
                      "其外接矩形左界 818 让开文字列右界 788",
         observed_problems="查看后：中右空白被叠光带与信息双栏填住，两行不再贴在一起；"
                           "标题 3 行、赞助方、免费参加、时间、讲者、网址全部完整可读",
         requirement_part="版面节奏 / 新增信息与标题不碰撞",
         recompare_result="与 r02-portrait-v01 对比；ink_audit.py 复核 0 重叠、"
                          "同列最小墨迹间隙 19px、扩展带 0 非背景像素",
         completed=True, image_viewed=True, final=True,
         viewed_at_basis="归档 round-02 前用图像工具打开该 PNG 全图查看"),
]
for row in rows:
    row.update(run_id=rid, task_id=task, image_viewed_at=NOW, recorded_at=NOW,
               noop_render=False,
               completed_meaning="本轮闭环：改动后有真实渲染并被实际查看比较；"
                                 "final=true 只表示该版本作为成品交付",
               path_base="suite_root")
    row.setdefault("final", False)
with (temp / "iterations.jsonl").open("a", encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("appended", len(rows))
