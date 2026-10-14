"""Append the A20 visual-review and iteration records actually made."""
import json
from datetime import datetime, timezone
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
LOG = RUN_DIR / "A20"

VIEWS = [
    ("A20-view-01", "v001", "v001-annotated-map.png", "full",
     "24 个标签全部就位、中心五点用右侧引导线；缺陷：左下说明文字横穿主图，压在 "
     "M01 北港 41 的标签上"),
    ("A20-view-02", "v002", "v002-zoom-centre.png", "zoom",
     "2.2× 放大指定中心 6 点 M06、M08、M09、M10、M11、M12：五点为 8px 红/蓝小圆，"
     "五条引导线各自从圆周出发连到右侧自己的标签盒边，线不穿任何标签文字，"
     "M06 的标签在左下 22.6px 处无需引导线"),
    ("A20-view-03", "v002", "v002-annotated-map.png", "full",
     "说明文字已移到主图下方；新缺陷：左上 y 轴标题两行与 value 前三图例标题重叠"),
    ("A20-view-04", "v003", "v003-zoom-topleft.png", "zoom",
     "1.5× 放大左上角：y 轴标题改为单行，图例从 MY+16 起排，二者不再重叠；"
     "y 轴刻度 100/80 与 M01、M03 标签互不接触"),
    ("A20-view-05", "v003", "v003-annotated-map.png", "full",
     "整图最终复核：24 个标签、5 条引导线、坐标轴与范围、单位“指数”、value 前三红圈红框"
     "全部到位；文字最小 20px；无遮挡、无裁切"),
]

ITERS = [
    ("v001", None, "baseline",
     ["v001-annotated-map.png", "v001-label-layout.json", "v001-layout-audit.json"],
     "首版按题面公式映射 24 点并解出无重叠标签布局；看图发现左下说明文字横穿主图压住 "
     "M01 标签。审计另暴露两处实现问题：贪心先占最上侧槽位导致引导线绕远，"
     "以及多名中心点共用一条垂直通道会正长度重合。",
     "候选槽改为按“到自身锚点的距离”排序；密集中心 M08–M12 先占右侧连续槽位"
     "（按锚点 y 单调分配），引导线改为直线段连接两条单调链，天然不交叉；"
     "通道回退时每条线独占 channel 并禁止与已放标签盒相交。",
     "layout-audit：最近标签盒间距 4.0px、非本点圆盘最小间隙 3.6px、"
     "引导线交叉 0（上限 3）、穿盒/自交/共线重合均为空"),
    ("v002", "v001", "visual",
     ["v002-annotated-map.png", "v002-zoom-centre.png"],
     "说明文字改到主图下方后，左上 y 轴标题两行与图例标题叠在一起。",
     "y 轴标题合并为一行放在主图上方，图例起点从 MY+8 下移到 MY+16。",
     "v003 放大左上角确认不再重叠"),
    ("v003", "v002", "visual",
     ["v003-annotated-map.png", "v003-zoom-topleft.png"],
     "整图与左上角、中心 6 点局部均实际查看：布局、层级、可读性达标；"
     "PNG 复核 24 个圆点直径与圆心（8/12px、中心误差 ≤2.5px）、"
     "24 个标签文字未越出标签盒。",
     "无进一步修改，定为交付版本。",
     "audit --ver v003 passed=true，problems=[]"),
]


def rec(fname, obj):
    obj.setdefault("ts", datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"))
    obj.setdefault("path_base", "suite_root")
    with (LOG / fname).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


for vid, ver, img, kind, note in VIEWS:
    rec("image-views.jsonl", {"view_id": vid, "task_id": "A20", "dsl_version": ver,
                              "image": f"tmp/{RUN_DIR.name}/A20/{img}", "kind": kind,
                              "note": note,
                              "tool": "Read (multimodal image view) + numpy pixel audit"})
for ver, parent, typ, arts, obs, chg, recheck in ITERS:
    rec("iterations.jsonl", {"version": ver, "parent": parent, "type": typ,
                             "artifacts": [f"tmp/{RUN_DIR.name}/A20/{x}" for x in arts],
                             "observed": obs, "change": chg, "recheck": recheck})
print("logged", len(VIEWS), "views", len(ITERS), "iterations")
