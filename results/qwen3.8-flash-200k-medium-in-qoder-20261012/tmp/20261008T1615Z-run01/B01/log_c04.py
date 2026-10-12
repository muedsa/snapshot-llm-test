import json, io, os, sys
from pathlib import Path
root = Path(os.environ["SNAPSHOT_TASK_ROOT"]); rid = os.environ["SNAPSHOT_RUN_ID"]
sys.path.insert(0, str(root / "tmp" / rid / "B01"))
from promote import iter_log

reqs = {}
for line in io.open(root / "tmp" / rid / "B01" / "requests.jsonl", encoding="utf-8"):
    r = json.loads(line)
    v = r.get("version") or ""
    if v.startswith("case-04"):
        reqs[v.split("-")[-1]] = r.get("request_id") or r.get("request_id_header")
print(reqs)

Q = chr(0x201c), chr(0x201d)
data = [
    ("v01", None,
     "首版渲染：整屏结构成立，但右侧三张卡的右对齐数值超出卡片边界被裁；ESI 条形与「最久」列重叠；"
     "图例压在副标题上；长等待气泡互相叠字；提示条写「抢救室 3/6 满员」与实际占用不符。",
     "右列数值标签锚点改为卡片内边；w_max 360→300 并把「最久」移到 LX+590；图例下移到 MY+86/100、"
     "绘图区 PY=MY+150；气泡仅保留 wait>=200 并交错；告警文案改为按 OCC 最大占用率实时推导。"),
    ("v02", "v01",
     "复核告警与右列锚点修正效果，检查候诊人数是否足以撑起时间轴。",
     "演示队列扩到 96 人次到院 / 34 人在院候诊；等待时长改用 dur() 显示 h/m，避免与时刻 hhmm 混淆。"),
    ("v03", "v02",
     "时间轴「急诊内科」行多条气泡落在同一 x 区间叠成一片不可读；其余分区已基本干净。",
     "气泡重写为按等待时长倒序、每行最多 2 条、同行 190px 内互斥，并加深色小底板与引导线；本轮先做整图复核。"),
    ("v04", "v03",
     "气泡不再重叠，只剩 2 条可读标注；但左侧床位 waffle 固定 8 列，抢救室 6 床画成 8 格"
     "（5/6 显示成 5/8），骨科行为空却无任何说明。",
     "waffle 增加 total 参数并按真实容量取列数（min(8,cap)）；时间轴无候诊患者的分区补"
     "「当前无候诊患者（空床 N）」注记。"),
    ("v05", "v04",
     "格数与容量一致（6/14/12/8/6/10）、空分区有说明、三列信息密度与配色统一，"
     "未发现裁切或叠字；文本自检 12 项 0 问题。",
     "接受为 case-04 终稿，提升为 outputs/<run>/B01/case-04/final.png + final.snapshot。"),
]
for v, parent, obs, chg in data:
    iter_log("case-04", "case-04-" + v, ("case-04-" + parent) if parent else None,
             reqs.get(v), "visual-iteration" if parent else "first-render", obs, chg)
