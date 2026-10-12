"""case-10 迭代留痕追加脚本（一次性，保留为过程资料）。"""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
RID = "20261008T1615Z-run01"
recs = [
    dict(iteration_id=RID + "-case-10-content-fix", task_id="B02", case_id="case-10",
         version="pre", parent_version=None, kind="content_fix", render_request_id=None,
         image_viewed_at=None,
         observed="渲染前自查两处口径问题：占比刻度若按「最大类目归一」画，28.5% 的条会画满整格并标 28.5%；"
                  "「本区常借」若直接取类目 names[] 前四项，等于把台账里的登记顺序冒充成借阅排名。",
         changed="刻度改为按全馆 2946 次借阅 = 100% 的真实比例绘制并在说明行写明口径；"
                 "排名改为遍历 loans_2025 按机型合并计数取前四，标题改「本区最常借出（按 2025 年台账）」。",
         path_base="suite_root"),
    dict(iteration_id=RID + "-case-10-v01", task_id="B02", case_id="case-10",
         version="v01", parent_version="pre", kind="baseline",
         render_request_id="B02-case-10-v01-20261010T062653Z",
         image_viewed_at="2026-10-10T06:27:05+00:00",
         observed="整图可读，字母压倒性成立。三处问题：①「ZONE A」小字压在大字母脚上，像贴歪的标签；"
                  "②「96 件在架」用词不实——96 是在册件数，此刻在馆只有 81 件，吊牌把两者混为一谈；"
                  "③常借前四只印名字不印次数，且右侧留出大片空白，信息量低于同版其他块。",
         changed="见 v02：字母下方改独立铭牌；在册/在馆分列（在馆数由 tools[].state 现算）；"
                 "前四补「N 次」并加一行名次差说明；刻度标题与说明行去重。",
         path_base="suite_root"),
    dict(iteration_id=RID + "-case-10-v02", task_id="B02", case_id="case-10",
         version="v02", parent_version="v01", kind="visual",
         render_request_id="B02-case-10-v02-20261010T062938Z",
         image_viewed_at="2026-10-10T06:30:00+00:00",
         observed="铭牌、在册/在馆、次数列都到位。新问题：第一列的「80 次」右边界几乎顶到第二列色片，"
                  "2x 裁切看像同一行；字母底板用类目色 20% 混深灰，整块发闷成脏棕色。",
         changed="见 v03：名单元框 190→130、次数盒固定到 x+152..236，列间留白 88px；底板混色 0.20→0.10。",
         path_base="suite_root"),
    dict(iteration_id=RID + "-case-10-v03", task_id="B02", case_id="case-10",
         version="v03", parent_version="v02", kind="visual",
         render_request_id="B02-case-10-v03-20261010T063037Z",
         image_viewed_at="2026-10-10T06:31:10+00:00",
         observed="列间距与底板达标（880x860 裁切复核字母不碰铭牌）。对照 PLAN 的触点要求「货架编号、工坊/服务台/"
                  "归还口位置、我要去哪个区」，发现两块缺口：左卡副行写的是「本区为通道端点」这种元说明，"
                  "没给归还口；底部九区索引只有字母 + 件数，读者无法用它决定该去哪一区。",
         changed="见 v04：左卡副行改用 data.json 的 rules.return_point「归还口在服务台左侧」。",
         path_base="suite_root"),
    dict(iteration_id=RID + "-case-10-v04", task_id="B02", case_id="case-10",
         version="v04", parent_version="v03", kind="visual",
         render_request_id="B02-case-10-v04-20261010T063244Z",
         image_viewed_at="2026-10-10T06:33:15+00:00",
         observed="归还口信息到位（1320x230 裁切可辨）。九区索引仍缺类目名，索引条退化成装饰；"
                  "芯片高度 66 放不下三行。",
         changed="见 v05：芯片 66→78，字母 23px / 类目名 12px / 件数 11px 三行居中，"
                 "当前区保留色底 + 顶部 4px 色帽。",
         path_base="suite_root"),
    dict(iteration_id=RID + "-case-10-v05", task_id="B02", case_id="case-10",
         version="v05", parent_version="v04", kind="visual",
         render_request_id="B02-case-10-v05-20261010T063403Z",
         image_viewed_at="2026-10-10T06:34:20+00:00",
         observed="九区索引现在能独立回答「我要找的类目在哪个字母」；芯片底边 758 与页脚 762 不碰；"
                  "整图 1200x800、TextFit 54 条 0 溢出；字母、类目名、件数、相邻区方向、占比刻度、"
                  "归还口、九区索引全部到位。判定可用。",
         changed="提升为 final（md5 b4d7a16a86a91eedbd95b5efa038cbb2，DSL 32420 字符）。"
                 "共 5 次请求、4 轮完整视觉迭代 + 1 次渲染前口径修正。",
         path_base="suite_root"),
]
with (here / "iterations.jsonl").open("a", encoding="utf-8") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("appended", len(recs))
