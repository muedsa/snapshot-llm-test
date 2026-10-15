"""A20：把实际看图结论写进 layout-audit.json 的 highlights.visual_reviews。

只登记**真的打开看过**的图；每条给出裁切区域、放大倍数与观察到的现象。
"""
import json
import pathlib

DRAFTS = pathlib.Path("tmp/run-20261011-01/A20/drafts")
PREV = "tmp/run-20261011-01/A20/preview"

REVIEWS = [
    {"order": 1, "image": f"{PREV}/annotated-map-v2.png", "zoom": "1600×1100 原尺寸整屏",
     "region": "整图",
     "observed": "三列结构成立：左侧 15 个标签、中间主图 24 个点、右侧 9 个标签。"
                 "24 个点全部落在主图框内，无一越界；最高 3 点带橙色外圈且标签为橙字橙框。",
     "conclusion": "整体版式与密集中心表达通过"},
    {"order": 2, "image": f"{PREV}/center6-tight.png",
     "zoom": "裁切 (696,404)-(904,624) 后 4× LANCZOS",
     "region": "中心 6 点 M06/M08/M09/M10/M11/M12",
     "observed": "6 个 12px 圆盘彼此明显分离，无一接触或遮挡；"
                 "每条引导线都精确终止在各自圆盘边缘，未连错点；"
                 "M08(中庭 91) 与 M10(广场 93) 的橙色外圈在放大后仍清晰、不糊。",
     "conclusion": "密集中心点不互相遮挡；缩小点并非必要（最近圆心距 30.86px > 12px）"},
    {"order": 3, "image": f"{PREV}/center6-leaders.png",
     "zoom": "裁切 (360,396)-(1160,632) 后 2× LANCZOS",
     "region": "中心 6 点的左右引导线进入段",
     "observed": "左侧引入的水平段彼此平行、互不相交；右侧 M10/M11 的引入段同样平行；"
                 "线宽在 2× 下仍只有 4px，未压到任何圆盘。",
     "conclusion": "引导线不穿过其它标签、无错误连接"},
    {"order": 4, "image": f"{PREV}/m12-m14.png",
     "zoom": "裁切 (140,520)-(800,700) 后 2× LANCZOS",
     "region": "同 y 的 M12(48,45) 与 M14(26,45)",
     "observed": "两条末段分别落在 y=578 与 y=572，相隔 6px、平行不重合；"
                 "两条竖直段 x 相差 3px 且不接触，肉眼看不到交叉点。",
     "conclusion": "唯一一对同 y 点通过顶边引入 + 名次破平化解，无共线重合、无交叉"},
    {"order": 5, "image": f"{PREV}/left-column.png", "zoom": "裁切 (0,250)-(300,920) 原尺寸",
     "region": "左侧标签列",
     "observed": "15 个标签文字完整、无截断；标签盒之间留白均匀；"
                 "M08 的橙色高亮框与相邻标签有明显区分。",
     "conclusion": "标签正文 >=20px、无覆盖、无并排歧义"},
    {"order": 6, "image": f"{PREV}/annotated-map-v1.png", "zoom": "1600×1100 原尺寸整屏",
     "region": "整图（首版，已被 v2 取代）",
     "observed": "首版缺陷：x 轴标题与刻度数字「20」重叠；"
                 "M03/M15/M24 的引导线水平段正好穿过 y 轴「80」「40」「20」三个刻度数字。",
     "conclusion": "据此改为只在两端标 0/100，并把轴文字盒纳入程序化检查"},
]


def main() -> None:
    p = DRAFTS / "layout-audit-v2-raw.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["highlights"]["visual_reviews"] = REVIEWS
    d["highlights"]["view_order_note"] = (
        "题面要求「放大查看指定中心 6 点 M06/M08/M09/M10/M11/M12 及引导线，再查看整体」。"
        "实际执行顺序为：首版整屏(1) → v2 整屏(1) → 中心 6 点 4×(2) → 6 点引导线 2×(3) → "
        "M12/M14 破平处 2×(4) → 左标签列(5)，其中整屏复查在放大复查前后各做了一次。")
    d["highlights"]["whole_image_review"] = {
        "final_image": f"{PREV}/annotated-map-v2.png",
        "checked": "24 个点全部在主图框内；24 个标签全部完整可读；"
                   "最高 3 点标注与圆上橙圈一一对应；坐标轴、范围与单位均已标注。",
    }
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print("visual_reviews:", len(REVIEWS), "->", p.as_posix())


if __name__ == "__main__":
    main()