"""case-10 v06 收尾回补的迭代记录追加（一次性）。"""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
RID = "20261008T1615Z-run01"
recs = [
    dict(iteration_id=RID + "-case-10-audit", task_id="B02", case_id="case-10",
         version="v05", parent_version="v05", kind="content_fix", render_request_id=None,
         image_viewed_at=None,
         observed="写 asset-sources.json 时对 11 份成品 DSL 做字符串核对：其余 10 份都带虚构演示声明，"
                  "只有 case-10 的页脚用 micro 档把声明省掉了，全套声明纪律在这里断掉。",
         changed="见 v06：页脚 micro 的 note 追加「本馆与全部数据为虚构演示内容」，"
                 "仍保持 12px 小字层级（3 米外不可读，走近才读），不影响主层级。",
         path_base="suite_root"),
    dict(iteration_id=RID + "-case-10-v06", task_id="B02", case_id="case-10",
         version="v06", parent_version="v05", kind="visual",
         render_request_id="B02-case-10-v06-20261010T065231Z",
         image_viewed_at="2026-10-10T06:53:05+00:00",
         observed="1440×90 页脚裁切：整行「扳手屋 · 白鹤岭馆 · 周二至周日 09:00–20:00 · "
                  "本馆与全部数据为虚构演示内容」完整渲染，未与上方索引芯片相碰；TextFit 54 条 0 溢出。",
         changed="重新提升为 final（1200x800，md5 13913232219c6a0ac627b5073ea28f2f，DSL 32437 字符）。"
                 "本题共 6 次渲染请求、4 轮完整视觉迭代、1 次渲染前口径修正、1 次收尾核对回补。",
         path_base="suite_root"),
]
with (here / "iterations.jsonl").open("a", encoding="utf-8") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("appended", len(recs))
