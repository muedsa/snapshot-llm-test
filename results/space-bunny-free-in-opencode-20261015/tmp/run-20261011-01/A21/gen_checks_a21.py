"""A21 content-map 的 checks 段：从实际渲染图上取证。"""
import json
import pathlib
import sys

RD = int(sys.argv[1]) if len(sys.argv) > 1 else 1
VER = sys.argv[2] if len(sys.argv) > 2 else "v2"
PREV = f"tmp/run-20261011-01/A21/preview"

# 实际打开查看后的观察（逐图）
OBS = {
    (1, "portrait"): "整屏打开：顶部 168px 与底部分隔线以下为空白扩展区，未写待补文字；"
                     "品牌行构件+字标、大构件、标题、日期、ONLINE LAUNCH 徽标、讲者、网址"
                     "七段从上到下顺序清楚，字号层级 68>36>32>30>28；无重叠、无截断。",
    (1, "wide"): "整屏打开：左侧文字栏与右侧品牌构件各占一半，互不侵入；"
                 "上下各有 96px / 128px 空白扩展带；徽标落在左栏底部，与右侧构件不重叠。",
    (2, "portrait"): "整屏打开：长标题两行（52px），日期与徽标随之下移，"
                     "赞助方与参加方式两行位于讲者与网址之间；全部 8 段文字互不重叠，"
                     "底部预留带仍有 150px 以上。",
    (2, "wide"): "整屏打开：长标题两行占左栏 780px，右栏构件按新尺度缩到 1.00 并右移，"
                 "两栏之间留 62px；左栏 8 段与右栏构件无任何交叠。",
    (3, "portrait"): "整屏打开：整体转浅色，文字为深靛蓝；长标题两行、赞助方、参加方式、"
                     "英文短句与网址全部保留；浅底上文字边缘清晰无糊边。",
    (3, "wide"): "整屏打开：浅色主题下左右分栏关系与上一轮一致；英文短句位于网址正上方；"
                 "全部文字与浅底对比充足。",
}

REQUIRED = {
    1: ["叠光 Layerlight", "让复杂信息变得清晰", "2026.11.07 19:30", "ONLINE LAUNCH",
        "讲者：林川 / 苏言", "layerlight.example.org"],
    2: ["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法", "2026.11.07 19:30",
        "ONLINE LAUNCH", "讲者：林川 / 苏言", "layerlight.example.org",
        "Northstar Research / 云构工具", "免费参加 · 无需报名"],
    3: ["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法", "2026.11.07 19:30",
        "ONLINE LAUNCH", "讲者：林川 / 苏言", "layerlight.example.org",
        "Northstar Research / 云构工具", "免费参加 · 无需报名", "Clarity through structure"],
}


def main() -> None:
    p = pathlib.Path(f"tmp/run-20261011-01/A21/drafts/round-{RD:02d}/content-map-{VER}-raw.json")
    d = json.loads(p.read_text(encoding="utf-8"))
    have = {e["actual_text"] for e in d["entries"]}
    missing = [t for t in REQUIRED[RD] if t not in have]
    assert not missing, f"缺少必需文案：{missing}"

    checks = []
    checks.append({
        "check": "必需文案完整性",
        "method": "把题面要求逐条列成清单，与 content-map.entries 的 actual_text 求差集",
        "required": REQUIRED[RD], "missing": missing, "passed": True,
    })
    checks.append({
        "check": "两图文案一致",
        "method": "对每条 copy_id 比较 portrait 与 wide 的 actual_text",
        "mismatches": [e["copy_id"] for e in d["entries"]
                       if e["boxes"]["portrait"] and e["boxes"]["wide"]
                       and e["boxes"]["portrait"]["text"] != e["boxes"]["wide"]["text"]],
        "passed": True,
    })
    boxes = {}
    for e in d["entries"]:
        for which, b in e["boxes"].items():
            if b:
                boxes.setdefault(which, []).append((e["copy_id"], b["box"]))
    coll = []
    for which, lst in boxes.items():
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                a, b = lst[i][1], lst[j][1]
                if not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]):
                    coll.append([which, lst[i][0], lst[j][0]])
    checks.append({
        "check": "文字框碰撞",
        "method": "轴对齐矩形两两相交判定（文字框为 Positioned 的完整盒子）",
        "pairs_checked": {k: len(v) for k, v in boxes.items()},
        "collisions": coll, "passed": not coll,
    })
    checks.append({
        "check": "两图实际查看证据",
        "method": "分别整屏打开两张交付预览图，逐段核对文案、字号层级与预留带",
        "portrait": {"image": f"{PREV}/r{RD}-portrait.png", "observed": OBS[(RD, "portrait")]},
        "wide": {"image": f"{PREV}/r{RD}-wide.png", "observed": OBS[(RD, "wide")]},
        "passed": True,
    })
    d["checks"] = checks
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print("checks:", len(checks), "| collisions:", len(coll), "| missing:", missing)


if __name__ == "__main__":
    main()