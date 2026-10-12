"""Append A21 round-03 iterations.jsonl rows."""
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
    dict(iteration_id="A21-r03-it01", type="requirement-change", version="r03-portrait-v01",
         parent_version="r02-portrait-v02", request_id=reqs["r03-portrait-v01"]["request_id"],
         http_status=200, image_path=P + "r03-portrait-v01.png", image_scope="preview",
         changes_made="第 3 轮预置需求：换浅色主题（底 #F5F7FC、正文 #0D1428/#4A5878、"
                      "强调 #1E40AF/#0E7490），文案与版式坐标逐字沿用第 2 轮；"
                      "网址上方新增 “Clarity through structure”（30px ≥24）",
         observed_problems="查看后：文字全部可读、品牌图形形态与第 2 轮一致（光源点自动由白转深）；"
                           "但叠光带在浅色底上几乎看不见（alpha 1A/14 时合成后与底色亮度差只有 0.11），"
                           "ONLINE LAUNCH 胶囊的亮青描边和 #C9D3E8 细线也偏淡",
         requirement_part="改浅色主题且对比度 ≥4.5:1 / 保留第 2 轮全部文案与品牌图形 / 新增英语短句",
         recompare_result="contrast_audit.py：15 个文字元素最低 5.0:1、0 处不达标；"
                          "问题在装饰可见性，不在文字对比度",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r03-it02", type="requirement-change", version="r03-wide-v01",
         parent_version="r02-wide-v01", request_id=reqs["r03-wide-v01"]["request_id"],
         http_status=200, image_path=P + "r03-wide-v01.png", image_scope="preview",
         changes_made="横版同步浅色主题与新增短句（短句接在标题块之下、分隔线之上，"
                      "分隔带与底栏整体下移 12px）",
         observed_problems="查看后：与竖版同样的问题——右下叠光带、胶囊描边、细线在浅色底上过淡",
         requirement_part="两尺寸不变 / 不得只改两种颜色忽略实际叠层",
         recompare_result="contrast_audit.py 横版 15 个元素最低 5.0:1；装饰层单独核对",
         completed=True, image_viewed=True,
         viewed_at_basis="渲染返回后当场用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r03-it03", type="visual", version="r03-portrait-v02",
         parent_version="r03-portrait-v01", request_id=reqs["r03-portrait-v02"]["request_id"],
         http_status=200, image_path=P + "r03-portrait-v02.png", image_scope="preview",
         changes_made="浅色主题下把叠光带 alpha 由 1A/1A/14/1F 提到 3A/3A/33/4D，"
                      "胶囊描边改用品牌深青 mix(#0E7490,bg,0.35)，细线压深到 #B9C6DE；"
                      "文字颜色与坐标不动，因此对比度结论不受影响",
         observed_problems="查看后：叠光带、描边、细线三处都清晰可见，版面重心不再偏左上；"
                           "标题 3 行、赞助方、免费参加、时间、讲者、网址、新增短句全部完整",
         requirement_part="装饰可见性 / 保留品牌图形形态与主色相",
         recompare_result="ink_audit.py：0 墨迹重叠、同列最小间隙 21px、扩展带 0 非背景像素；"
                          "contrast_audit.py 的 decor_layers 用 PNG 实测反核 9 个半透明层，"
                          "最大通道差 14（容差 24）",
         completed=True, image_viewed=True, final=True,
         viewed_at_basis="归档 round-03 前用图像工具打开该 PNG 全图查看"),
    dict(iteration_id="A21-r03-it04", type="visual", version="r03-wide-v02",
         parent_version="r03-wide-v01", request_id=reqs["r03-wide-v02"]["request_id"],
         http_status=200, image_path=P + "r03-wide-v02.png", image_scope="preview",
         changes_made="横版同步装饰加强（同一套 palette 常量，两图不可能走偏）",
         observed_problems="查看后：右下叠光带与右侧信息列不相交，短句在分隔线之上完整可读",
         requirement_part="装饰可见性 / 新增信息不碰撞",
         recompare_result="ink_audit.py：0 重叠、同列最小间隙 20px、扩展带 0 非背景像素；"
                          "decor_layers 9 层实测最大通道差 23（容差 24）",
         completed=True, image_viewed=True, final=True,
         viewed_at_basis="归档 round-03 前用图像工具打开该 PNG 全图查看"),
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
