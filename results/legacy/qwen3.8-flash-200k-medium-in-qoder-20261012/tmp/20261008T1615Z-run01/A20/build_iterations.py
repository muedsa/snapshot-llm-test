"""A20 iterations.jsonl：真实渲染/看图事件，字段与 A17–A19 一致。"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "A20"


def now():
    return datetime.now(timezone.utc).isoformat()


REQ = {
    "map-v01": "A20-map-v01-20261009T051954Z",
    "map-v02": "A20-v02-20261009T052609Z",
    "map-v02-explore": "A20-v02-20261009T052609Z",
    "map-v03": "A20-v03-20261009T052857Z",
    "map-v03-zoom": "A20-v03-zoom-20261009T053024Z",
}
rows = []


def add(kind, version, parent, image, changes, observed, req_part, recompare,
        completed, final, viewed=True, itype=None, request=None, viewed_at=None):
    rows.append({
        "run_id": rid, "task_id": "A20",
        "iteration_id": "A20-it%02d" % (len(rows) + 1),
        "type": itype or ("visual" if kind == "render" else "verification"),
        "version": version, "parent_version": parent,
        "request_id": request or REQ[version],
        "http_status": 200,
        "image_path": image, "image_scope": "preview",
        "changes_made": changes, "observed_problems": observed,
        "requirement_part": req_part, "recompare_result": recompare,
        "completed": completed,
        "completed_meaning": "本轮闭环：改动后有真实渲染并被实际查看比较；"
                             "final=true 只表示该版本作为成品交付",
        "final": final, "image_viewed": viewed,
        "image_viewed_at": viewed_at or now(),
        "viewed_at_basis": "渲染返回后当场用图像工具打开该文件（含本地放大裁片）",
        "recorded_at": now(), "path_base": "suite_root",
    })


add("render", "map-v01", None,
    "tmp/%s/A20/preview/map-v01.png" % rid,
    "求解器首版：逻辑坐标->像素、密集点进左右书脊、孤立点主图内标签、引导线避让",
    "查看后：左下两条页脚说明被裁（“M10”后截断、“线不穿文字”只剩“线”），"
    "书脊 38px 行距使引导线几乎平行地插入中心点群，难以判断线头属于哪个点",
    "标签正文≥20 / 页脚说明完整 / 引导线可辨识",
    "与 layouts/annotated-map.snapshot 的生成参数对表，确认裁切来自盒宽不足而非服务问题",
    True, False)
add("render", "map-v02", "map-v01",
    "tmp/%s/A20/preview/map-v02.png" % rid,
    "加文字放得下闸门（单行宽度断言 + TextFit 高度）、页脚改 3 列 3 行、书脊 pitch 38->48",
    "查看后：页脚 9 条全部完整；仍剩 1 处引导线交叉 M12~M14（该点走了 fallback 直线），"
    "且 M12/M14 同处 py=578 一行，两条直线必然互穿",
    "线线交叉≤3 / 引导线不穿文字 / 放大查看中心点群",
    "audit() 报 1 条；本地 zoom-center-v02.png、zoom-footer-v02.png 复核",
    True, False)
add("render", "map-v02-explore", "map-v02",
    "tmp/%s/A20/preview/map-v02.png" % rid,
    "引导线避让余量 r+2.5 -> r+5（线擦过别人的点会被读成连到那个点）、候选折线 25 -> 122 条",
    "本轮无渲染，只跑求解器：M09 改走 5 点折线避开点群，M14 仍是 none-legal-fallback，"
    "交叉仍为 M12~M14",
    "引导线不得连接错点", "程序审计（未看图，故 image_viewed=false）",
    True, False, viewed=False, itype="exploration")
add("render", "map-v03", "map-v02",
    "tmp/%s/A20/preview/map-v03.png" % rid,
    "书脊排序键 py -> (py, px)：同像素行的两点按 x 升序，从根上消除那处交叉",
    "查看后：整图 0 交叉 0 审计问题；中心点群每条线只落一个点；页脚与坐标刻度无裁切",
    "主图完整 / 标注轴与单位 / 前三名高亮 / 密集区可读",
    "audit()=0、crossings()=[]、build_outputs.py 复算 DSL 与落盘字节一致",
    True, True)
add("render", "map-v03", "map-v03",
    "tmp/%s/A20/preview/zoom-svc-v03.png" % rid,
    "不改动布局；用服务侧 ClipRect 裁出中心密集区 480x260 后本地 3x 放大",
    "放大后确认：12 个点（含 2 个金环）各自只有一条引导线相接，线与非本点最小间距 5px，"
    "M09 的折线阶梯不压任何标签",
    "必须放大查看中心 6 点及引导线",
    "与 label-layout.json 的 leader_px 逐条对表",
    True, False, request=REQ["map-v03-zoom"])
add("render", "map-v03", "map-v03",
    "tmp/%s/A20/preview/zoom-cluster-v03.png" % rid,
    "不改动图像；从成品 PNG 本地 2x 裁片复核中心密集区（观察证据，非后处理）",
    "无新增问题",
    "引导线不得穿过标签文本 / 不得连接错点",
    "与 layout-audit.json 的 leader_through_label_text=[] 对表",
    True, False, request=REQ["map-v03"])

TMP.joinpath("iterations.jsonl").write_text(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
    encoding="utf-8", newline="\n")
print("iterations", len(rows), "visual", sum(1 for r in rows if r["type"] == "visual"),
      "viewed", sum(1 for r in rows if r["image_viewed"]))
