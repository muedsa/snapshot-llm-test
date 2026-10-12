"""A19 · 由 requests.jsonl 的真实条目生成 iterations.jsonl（一条渲染/一次看图一行）。"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "A19"
reqs = {json.loads(l)["dsl_version"]: json.loads(l)
        for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()}
now = datetime.now(timezone.utc).isoformat()

SPEC = [
    ("grid-v01", None, "baseline", "8x8 网格场景首次实际预览",
     "查看后：编号标签整体右移一格，G08 的标签落到格外、其余标签压在相邻主体上", True,
     "格内编号 / 64 对象交叉分布", "与生成器 scene-objects.json 逐格对表"),
    ("grid-v02", "grid-v01", "visual", "标签列改用 (col-1)*CELL+20，并在 validate() 增加"
     "标签框越界与标签压主体两类检查后重渲染",
     "查看后：64 个标签都落在自己格内、主体正下方，无越界无遮挡；圆环中孔真实透明", True,
     "格内编号 / 圆环内外径 / 每行≥3色≥3形", "与 grid-v01 并排比较同一格区"),
    ("occlusion", None, "baseline", "遮挡场景 A/B 与两个去板诊断图首次实际预览",
     "查看后：底部坐标原点说明被画布下沿裁掉，V9 标签与说明行距过近", True,
     "完整遮挡 / 只给可见部分", "与去板诊断图比较板内板外"),
    ("occlusion-alternative", "occlusion", "visual", "同一版式下的隐藏内容 B（11 个对象）",
     "查看后：可见部分与 A 完全一致，无法从图面分辨板下内容", False,
     "两份隐藏内容不同的完整 DSL", "与 occlusion 版逐像素比较（0 差异）"),
    ("occlusion-noplate", "occlusion", "exploration", "去掉遮挡板的 A 诊断渲染，仅留痕",
     "查看后：板内出现 5 个隐藏主体，证明隐藏内容真实存在", False,
     "证明隐藏内容不同", "与 occlusion-alternative-noplate 比较"),
    ("occlusion-alternative-noplate", "occlusion-alternative", "exploration",
     "去掉遮挡板的 B 诊断渲染，仅留痕",
     "查看后：板内是 11 个不同形状/颜色的对象，与 A 明显不同", False,
     "证明隐藏内容不同", "与 occlusion-noplate 比较（37248 像素差异）"),
    ("occlusion-v02", "occlusion", "visual", "底部说明上移到 y=756 并把 V9 上移 30 px 后重渲染",
     "查看后：说明文字完整可见，9 个可见对象与编号都在板外", True,
     "只给观众可见部分", "与 occlusion v01 比较同一区域"),
    ("occlusion-alternative-v02", "occlusion-alternative", "visual", "同步修正 B 版",
     "未单独打开图像：与 A 版 PNG 的 sha256 完全相同，等价性由逐像素比较确认", False,
     "像素等价证明", "逐像素比较：0 差异像素"),
    ("occlusion-noplate-v02", "occlusion-noplate", "visual", "同步修正去板诊断 A",
     "查看后：隐藏层 5 对象，差异像素完全落在板包围框内", True,
     "泄漏检查", "差异 bbox [249,250,543,543] ⊂ 板 [200,210,600,610]"),
    ("occlusion-alternative-noplate-v02", "occlusion-alternative-noplate", "visual",
     "同步修正去板诊断 B", "查看后：隐藏层 11 对象，与 A 差异 37248 像素", True,
     "泄漏检查", "差异 bbox 完全在板内"),
]
rows = []
rows = []
for i, (ver, parent, typ, change, observed, viewed, reqpart, recompare) in enumerate(SPEC, 1):
    r = reqs[ver]
    rows.append({
        "run_id": rid, "task_id": "A19", "iteration_id": "A19-it%02d" % i,
        "type": typ, "version": ver, "parent_version": parent,
        "request_id": r["request_id"], "http_status": r["http_status"],
        "image_path": r["out_file"], "image_scope": "preview",
        "changes_made": change, "observed_problems": observed,
        "requirement_part": reqpart, "recompare_result": recompare,
        "completed": True,
        "completed_meaning": "本轮闭环：改动后有真实渲染并被实际查看比较；final=true 只表示该版本作为成品交付",
        "final": ver in ("grid-v02", "occlusion-v02", "occlusion-alternative-v02"),
        "image_viewed": viewed,
        "image_viewed_at": r["ended_at"],
        "viewed_at_basis": "同一会话内渲染返回后立刻用图像工具打开该预览；时间戳沿用请求结束时刻",
        "recorded_at": now, "path_base": "suite_root",
    })
# 成品发布后对最终位图做的 4 次象限放大查看（同一次渲染、4 次真实看图事件）
for j, (quad, note) in enumerate([
        ("q-tl", "G01–G28 四行：标签与主体一一对应，颜色/形状/尺寸与 scene-objects.json 相符"),
        ("q-tr", "G05–G32 右半：圆环中孔为纯白背景，尺寸档位可辨"),
        ("q-bl", "G33–G60 左下：Q03/Q05/Q06/Q14 的基准对象 G28/G32/G42/G52 逐一核对"),
        ("q-br", "G37–G64 右下：Q01 的绿圆环 G38/G43/G54 与 Q11 的第5列蓝色对象核对")], 1):
    r = reqs["grid-v02"]
    rows.append({
        "run_id": rid, "task_id": "A19", "iteration_id": "A19-it%02d" % (len(rows) + 1),
        "type": "verification", "version": "grid-v02-qa%d" % j,
        "parent_version": "grid-v02", "request_id": r["request_id"],
        "http_status": r["http_status"],
        "image_path": "tmp/%s/A19/preview/qa/%s.png" % (rid, quad),
        "image_scope": "preview",
        "changes_made": "不改动图像；从已交付的 grid-scene.png 裁出象限做目视复核（观察证据，非后处理）",
        "observed_problems": "无；" + note,
        "requirement_part": "实际看图检查所有目标与标签 / 题目答案可仅凭可见图推出",
        "recompare_result": "与 scene-objects.json 及 verify_grid.py 的逐像素审计结果三方对表",
        "completed": True,
        "completed_meaning": "本轮闭环：改动后有真实渲染并被实际查看比较；final=true 只表示该版本作为成品交付",
        "final": False, "image_viewed": True, "image_viewed_at": now,
        "viewed_at_basis": "发布 outputs/grid-scene.png 之后当场用图像工具打开象限裁片查看",
        "recorded_at": now, "path_base": "suite_root",
    })

(TMP / "iterations.jsonl").write_text(
    "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8",
    newline="\n")
print(len(rows), "行；final:", [x["version"] for x in rows if x["final"]])
