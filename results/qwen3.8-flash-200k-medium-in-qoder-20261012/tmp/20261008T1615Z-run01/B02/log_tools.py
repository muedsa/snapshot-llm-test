import json, os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
p = root / "tmp" / rid / "B02" / "tool-usage.jsonl"

now = datetime.now(timezone.utc).isoformat()
recs = [
    dict(tool="python（_suite/scripts/render.py）",
         purpose="把每个 case 的 DSL 作为一次真实服务请求渲染成 PNG，并逐条落 requests.jsonl",
         input="--task B02 --version case-NN-vNN --kind baseline|visual --in <dsl> --out <png> --seq-dir tmp/<run>/B02/case-NN",
         output="tmp/20261008T1615Z-run01/B02/requests.jsonl（48 条，其中本题 40 条 + 构件烟雾 8 条）、tmp/<run>/B02/case-NN/*.png 与同名 .snapshot、requests/ 原始响应",
         affects="B02 全部触点的成图与留痕",
         requests_ref=["B02-case-10-v06-20261010T065231Z", "B02-case-01-v05-20261010T045643Z"]),
    dict(tool="python + hashlib（promote.py）",
         purpose="定稿晋升：用 md5(原始响应字节)==md5(交付 PNG) 证明交付图未被后处理，并核对同名 DSL 完整",
         input="python tmp/<run>/B02/promote.py --case case-NN --version vNN（10 个用例各一次，case-10 因页脚口径修正晋升过两次）",
         output="outputs/20261008T1615Z-run01/B02/case-NN/{final.png,final.snapshot}；10/10 md5 匹配记录在 tmp/<run>/B02/facts.json 的 matched 字段",
         affects="gallery.md / portfolio.json 里每张图的「定稿请求」与 md5 列",
         requests_ref=[]),
    dict(tool="python + PIL 裁切放大（逐案视觉自检）",
         purpose="对 1200x800 / 1400x900 成图切局部放大图，判断实际可读性而不是凭 DSL 源码想象",
         input="case-08 顶栏色带与状态列、case-09 顶部结论区、case-10 类目磁贴与前四名列表、整图 RGB 抽样",
         output="tmp/<run>/B02/case-08/qa-v0{1,2}-{band,state}.png、case-09/qa-v0{3,4}-top.png、case-10/qa-v03-tile.png、qa-v03-top4.png、qa-v04-adj.png、qa-v06-footer.png、qa-full-rgb.png（共 11 张，仅观察用，非交付物）",
         affects="case-08 v02、case-09 v04、case-10 v02→v06 的具体修改项",
         requests_ref=["B02-case-08-v02-20261010T061021Z", "B02-case-10-v06-20261010T065231Z"]),
    dict(tool="python（b02data.py 重跑 + 断言）",
         purpose="返工期间数据被重生成过一次，重跑后逐项复核总数字未变，避免图上的数与 data.json 脱钩",
         input="random.Random(20261010) 固定种子重跑 tmp/<run>/B02/b02data.py",
         output="tmp/<run>/B02/data.json（412 件、9 类目、2946 条借阅、1860 名会员、逾期 364 条 12.4%、续费 593 次 20.1%）",
         affects="所有触点的数字口径；复核结论写入 snapshot-usage.md 第 4 节",
         requests_ref=[]),
    dict(tool="python（TextFit 检查器）",
         purpose="渲染前用度量估算判断每段文案是否会溢出容器，替代「渲染出来再看」",
         input="tmp/<run>/B02/*_board.py 中的 b02kit.tlab 调用，每张定稿 DSL 的文本标记逐条度量（case-10 定稿为 54 条文本 / 0 条溢出）",
         output="各 board 脚本运行时的 problems 列表；problems 非空时先改字号或容器再请求渲染",
         affects="每案 iterations.jsonl 中 kind=content_fix|syntax_fix 的 10 条渲染前修正",
         requests_ref=[]),
    dict(tool="python（collect_b02.py）",
         purpose="从 requests.jsonl/iterations.jsonl/成图反查每题事实清单，收尾数字不靠记忆手填",
         input="按 response_file 路径归案 + final.png md5 反查定稿请求 + PIL 读尺寸 + 解析 case.md 标题",
         output="tmp/<run>/B02/facts.json（48 次渲染、0 次失败、10/10 md5 匹配、25 轮完整视觉迭代、37 次看图）",
         affects="task-metrics.json、gallery.md、portfolio.json 的全部统计数字",
         requests_ref=[]),
    dict(tool="python（字符串核对，素材审计）",
         purpose="逐个定稿 DSL 统计 <Image> / backgroundImage 出现次数，用可复核的计数支撑「0 内嵌素材」",
         input="11 张 final.snapshot 全文计数；并核对三份抓取来源与四份仅搜索来源",
         output="outputs/20261008T1615Z-run01/B02/asset-sources.json（每文件计数均为 0；en.wikipedia.org 抓取失败故未被引用）",
         affects="asset-sources.json、snapshot-usage.md 第 5 节；审计过程发现 case-10 缺虚构声明，触发 v06 重渲染",
         requests_ref=["B02-case-10-v06-20261010T065231Z"]),
    dict(tool="python（build_closeout.py）",
         purpose="由 facts.json 生成画廊与作品集，保证图片链接、md5、迭代统计与实际文件一致",
         input="tmp/<run>/B02/facts.json + 手写文案字典（受众/使用情境/用户目标/依据/视觉意图/能力/验收）",
         output="outputs/20261008T1615Z-run01/B02/{gallery.md,portfolio.json,portfolio.md}",
         affects="B02 收尾交付物",
         requests_ref=[]),
]
with p.open("a", encoding="utf-8") as f:
    for i, r in enumerate(recs, start=5):
        r["at"] = now
        r["id"] = "B02-tool-%03d" % i
        r["path_base"] = "suite_root"
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(p.read_text(encoding="utf-8").count("\n"))
