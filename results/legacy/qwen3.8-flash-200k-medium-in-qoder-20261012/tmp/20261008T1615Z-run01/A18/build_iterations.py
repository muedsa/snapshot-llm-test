"""A18 iterations.jsonl：由 requests.jsonl + 每个版本实际看到的几何差异推导。"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RUN = os.environ["SNAPSHOT_RUN_ID"]
TMP = ROOT / "tmp" / RUN / "A18"

NOTE = {
    "storya-v01": ("baseline", "候选构图 alt-a（三栏矩形舞台）首次实际预览", True,
                   "查看后：连线只有短桩、方向不可读，但三幕横向阅读顺序成立"),
    "storyb-v01": ("baseline", "候选构图 alt-b（三圆盘舞台）首次实际预览", True,
                   "查看后：空闲节点落在圆盘之外，阅读顺序要来回跳，落选"),
    "storya2-v01": ("visual", "选定 alt-a 后完善：内容纵向居中、节点归位、加箭头、过载节点套橙色内环",
                    True, "查看后：箭头出现在圆心附近而不是节点上，说明线段被裁错了"),
    "storya2-v02": ("visual", "修正 connect() 的裁剪基准（原来从单元圆心量节点半宽，线段退化为 28px 短桩）",
                    True, "查看后：三幕的汇聚/挤压/分流第一次真正读得出来"),
    "storya3-v01": ("visual", "三幕共用同一组节点坐标，把“同一系统”变成可核对的几何事实",
                    True, "查看后：面板可直接横向对比；第 3 幕下方两簇贴住面板底边"),
    "storya3-v02": ("visual", "第 3 幕下方簇上移留白，连线细端加粗到 2.2px/alpha 8C 以过 400px 缩略关",
                    True, "只看 400px 缩略：三幕仍可分辨（疏星→密星→三小簇）"),
    "storya3-v03": ("visual", "第 3 幕三簇外扩到 R=110/140 试探更大箭头", False,
                    "生成器先报 4 处单元越界，未作为候选继续；渲染仅留作失败证据"),
    "storya3-v04": ("visual", "把越界簇收回：节点对收到 cx±105、扇形 R=105", True,
                    "查看后：第 1 幕环底单元与空闲节点距离过近，节点像被卷进环里"),
    "storya3-v05": ("visual", "节点对上移到 y=730 试错", True,
                    "查看后：反而更贴近第 1 幕的环，方向不成立"),
    "storya3-v06": ("visual", "节点对定在 cx±125 / y=765，第 3 幕扇形 R=95、span=120", True,
                    "全图与 400px 缩略都查看；发布为 three-act-story.png"),
}

renders = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
missing = [r["dsl_version"] for r in renders if r["dsl_version"] not in NOTE]
assert not missing, f"no note for {missing}"

rows = []
for i, r in enumerate(renders, 1):
    kind, change, viewed, outcome = NOTE[r["dsl_version"]]
    rows.append({
        "run_id": RUN,
        "task_id": "A18",
        "iteration_id": f"A18-it{i:02d}",
        "type": kind,
        "version": r["dsl_version"],
        "parent_version": renders[i - 2]["dsl_version"] if i > 1 else None,
        "request_id": r["request_id"],
        "http_status": r["http_status"],
        "image_path": r["out_file"],
        "image_scope": "preview",
        "changes_made": change,
        "observed_problems": outcome,
        "requirement_part": "三幕守恒几何 / 叙事可读性",
        "recompare_result": "与上一版本并排比较（同一生成器、同一画布）" if viewed else "生成器判定失败，未进入看图环节",
        "completed": True,
        "completed_meaning": "本轮闭环：改动后有真实渲染并被实际查看比较；final=true 才表示该版本作为成品交付",
        "final": r["dsl_version"] == "storya3-v06",
        "image_viewed": viewed,
        "image_viewed_at": r["ended_at"] if viewed else None,
        "viewed_at_basis": "同一会话内渲染返回后立刻用图像工具打开该预览；秒级时间戳沿用请求结束时刻",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "path_base": "suite_root",
    })
with (TMP / "iterations.jsonl").open("w", encoding="utf-8", newline="\n") as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print(len(rows), "iterations;",
      sum(1 for r in rows if r["image_viewed"]), "viewed;",
      json.dumps({k: sum(1 for r in rows if r["type"] == k) for k in {r["type"] for r in rows}}))
