"""Append the A19 visual-review and iteration records actually made."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
LOG = RUN_DIR / "A19"

VIEWS = [
    ("A19-view-01", "v001", "tmp/<run>/A19/v001-grid-scene.png", "full",
     "1600×1600 八乘八格：64 个主体各占一格、编号在主体下方外侧；四色四形三尺寸交叉出现，"
     "网格线浅灰不抢主体"),
    ("A19-view-02", "v001", "tmp/<run>/A19/v001-occlusion.png", "full",
     "800×800 A 版：浅色面板 + 8 个完整可见对象 + 中央深色不透明遮挡板，遮挡板上方有 "
     "OCCLUDED REGION 文字；无任何虚线/缺口/阴影泄漏"),
    ("A19-view-03", "v002", "tmp/<run>/A19/v002-occlusion-alternative.png", "full",
     "B 版与 A 版看起来一模一样（隐藏层 5 个对象被完全盖住），符合等价要求"),
    ("A19-view-04", "v002", "tmp/<run>/A19/v002-grid-scene.png", "full",
     "定稿整图复核：每行都能看出至少三种颜色与三种形状，主体未压格线"),
    ("A19-view-05", "v002", "tmp/<run>/A19/v002-zoom-rings.png", "zoom",
     "1.3× 放大第 5 行左三格与第 6 行左三格：G33/G35 圆角方、G34/G43 圆环（内孔为白底、"
     "内径为外径一半）、G41 直角方、G42 实心圆；48/64/80 三档大小肉眼可分，"
     "编号文字都在主体框之外且清晰可读"),
]

ITERS = [
    ("v001", None, "baseline",
     ["tmp/<run>/A19/v001-grid-scene.png", "tmp/<run>/A19/v001-occlusion.png",
      "tmp/<run>/A19/v001-occlusion-alternative.png"],
     "首版全部约束一次满足（颜色/形状各 16、16 组合齐、每色每形三尺寸齐、每行≥3 色 3 形）；"
     "两遮挡版文件哈希相同。像素自检发现分类器把直角方误读为圆角方（只看单个角点），"
     "圆环的颜色被读成橙色（取中心像素，而中心是孔）；B 版隐藏对象最小内缩只有 12 px。",
     "分类器改为“填充率 + 5×5 角窗占用 + 中心是否为底色”，颜色改用组件像素中位数；"
     "B 版隐藏对象重新排布使内缩≥24 px。",
     "verify --ver v002：64 个主体尺寸/形状/颜色/中心全部与计划一致，problems=[]；"
     "遮挡比较不同像素 0、最大通道差 0、隐藏足迹覆盖率 100%"),
    ("v002", "v001", "visual",
     ["tmp/<run>/A19/v002-grid-scene.png", "tmp/<run>/A19/v002-occlusion.png",
      "tmp/<run>/A19/v002-occlusion-alternative.png",
      "tmp/<run>/A19/v002-zoom-rings.png"],
     "整图与 1.3× 局部实际查看：主体不压线、编号在外、圆环内孔干净；"
     "两遮挡版视觉不可区分。",
     "无进一步修改，定为交付版本；据此生成 scene-data / questions / answers / equivalence。",
     "verify --ver v002 全绿；questions 18 题（14 网格 + 4 遮挡，8 题两步）"),
]


def rec(fname, obj):
    obj.setdefault("ts", datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"))
    obj.setdefault("path_base", "suite_root")
    with (LOG / fname).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


for vid, ver, img, kind, note in VIEWS:
    rec("image-views.jsonl", {"view_id": vid, "task_id": "A19", "dsl_version": ver,
                              "image": img.replace("<run>", RUN_DIR.name), "kind": kind,
                              "note": note,
                              "tool": "Read (multimodal image view) + numpy pixel audit"})
for ver, parent, typ, arts, obs, chg, recheck in ITERS:
    rec("iterations.jsonl", {"version": ver, "parent": parent, "type": typ,
                             "artifacts": [x.replace("<run>", RUN_DIR.name) for x in arts],
                             "observed": obs, "change": chg, "recheck": recheck})
print("logged", len(VIEWS), "views", len(ITERS), "iterations")
