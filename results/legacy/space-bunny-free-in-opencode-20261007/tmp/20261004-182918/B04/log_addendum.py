"""B04: addendum — case-04 final visual iteration + the fifth crop check."""
import io
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "B04"))
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import olog  # noqa: E402

T = "tmp/%s/B04/" % RUN
O = "outputs/%s/B04/" % RUN

olog.log("case-04", "B04-iter-c04-4", "B04-iter-c04-3", "visual_iteration",
         T + "build_c04.py", O + "case-04/final.png", "2026-10-05T23:12+08:00",
         "最终定稿前的整体复核发现 DIC 条下方的三个标签虽然不再重叠，"
         "但「CO3^2-」右对齐到 0.90 宽、「CO2(aq)」右对齐到 1.0 宽，两者几乎首尾相接，"
         "读起来像一串「CO3^2-CO2(aq)」。用 crop.py 以 2× 放大 80,690–620,800 确认这一点。",
         "把「CO3^2-」右对齐位置从 0.76 宽改到 0.76-0.14=0.62 宽，与「CO2(aq)」拉开间距；"
         "重渲染后用同一放大图核对：HCO3- / CO3^2- / CO2(aq) 三个标签各自独立、"
         "互不相接，且仍分别对应各自色段。",
         True, "accepted", "定稿。本件自此共 4 次成功渲染、4 次看图（含 1 次局部放大）。")

olog.tool("PIL（局部放大核对）", "放大核对 DIC 堆叠条下方的三个标签是否首尾相接",
          "_suite/crop.py：case-04 DIC 条 80,690–620,800 2×",
          "tmp/%s/B04/crops/final-c04-dic.png" % RUN,
          "2026-10-05T23:10:00+08:00", ["case-04"],
          "这是本任务第 5 次局部放大核对。前四次分别用于确认 case-02 的填充条带、"
          "case-01 的阅读顺序条、case-03 的对数刻度、case-09 的底部面板。")

# patch case-meta.json so the regenerated case.md / portfolio pick up the v4 note
CM = os.path.join(ROOT, "tmp", RUN, "B04", "case-meta.json")
import json  # noqa: E402
meta = json.load(io.open(CM, encoding="utf-8"))
meta["case-04"]["review"] = (
    "打开 4 次（v1 右侧三面板宽度算出 −68px 直接 400 PARSE_ERROR；v2 重排为上排反应 + "
    "下排三面板；v3 修 DIC 标签互相压字并补一条明确标为「解读」的说明；v4 用 2× 放大图"
    "发现 CO3^2- 与 CO2(aq) 首尾相接，拉开间距后定稿）。"
    "最终版用 crop.py 以 2× 放大 DIC 条区域核对，三个标签各自独立"
    "（crops/final-c04-dic.png）。无 D.warnings() 输出。")
meta["case-04"]["iterations"] = ["B04-iter-c04-1", "B04-iter-c04-2",
                                 "B04-iter-c04-3", "B04-iter-c04-4"]
meta["case-04"]["left"] = ("反应式用 ASCII 记法（CO2、H2CO3、CO3^2-）而不是下标，"
                           "因为 DejaVu Sans Mono 的下标字符未在本任务验证过；"
                           "化学含义不受影响但排版不如真正下标紧凑。")
with io.open(CM, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(meta, fh, ensure_ascii=False, indent=1)
print("addendum logged; case-04 meta patched")
