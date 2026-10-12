"""B01 case-01..05 期间新确认的 DSL 能力与工具使用留痕（追加到既有证据文件）。

只记录有真实请求 ID 支撑的结论；recorded_at 为实际观察时刻（UTC）。
"""
import json
import os
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "B01"
NOW = "2026-10-10T01:33:00+00:00"

NEW = [
    {"cap": "Text fontStyle 枚举严格", "verdict": "constraint",
     "evidence": "400 PARSE_ERROR「Attr [fontStyle] value is invalid: Unexpected font "
                 "style None」（req B01-case-05-v07-20261010T011744Z, requestId "
                 "2dbc2e09-ffa7-4ce4-8d79-422337952c53）与同样报 "
                 "Unexpected font style REGULAR（req "
                 "B01-case-05-v08-20261010T011836Z, requestId "
                 "1f699fce-1aaa-42d2-8ba8-96ab68721863）；"
                 "改为不加粗时整个省略该属性后 200（req "
                 "B01-case-05-v09-20261010T011945Z）",
     "note": "已验证可用值只有 BOLD（以及缺省）；REGULAR/NORMAL/NONE 均非法。"
             "写通用文本工具函数时不要给 fontStyle 填默认值"},
    {"cap": "Container 作不透明标注贴片（radius + 内嵌 Text + align）",
     "verdict": "works",
     "evidence": "case-05 v06 起：地图上的城市名与路径时间全部改为 "
                 "Container(#050B15D0, radius=5, align=CENTER_LEFT/CENTER_RIGHT/CENTER) "
                 "内嵌 Text，压在路径线与不确定性锥上仍清晰可读"
                 "（req B01-case-05-v06-20261010T011416Z 起 200）",
     "note": "align 决定文字在贴片内的锚点，与外部 Positioned 的 TOP_LEFT 组合"
             "即可让贴片左/右边缘对齐锚点，省去手工量字宽"},
    {"cap": "Positioned 偏移 + 占位框做图内标注避让",
     "verdict": "works",
     "evidence": "case-05 v05 引入 PLACED 占位表：地理标注/图例/台风符号/登陆点先登记，"
                 "路径与城市标注按 12 个候选偏移搜索第一个不相交且不出图的位置，"
                 "超过 30 px 时补 1 px 引导线；v10→v12 修好登陆点簇叠字"
                 "（req B01-case-05-v10-20261010T012126Z → "
                 "B01-case-05-v12-20261010T012857Z）",
     "note": "占位框必须按可见墨迹尺寸登记，不能按容器宽度（180 px 的居中文本框"
             "会把可用空间全部吃掉，导致全部候选失败并回落到第一个）"},
    {"cap": "curl 传输失败（HTTP 0）与重试",
     "verdict": "environment",
     "evidence": "同一 DSL 三次请求失败：curl (56) Send failure: Connection was reset、"
                 "curl (28) SSL/TLS connection timeout（req "
                 "B01-case-05-v11-20261010T012557Z / 012629Z / 012657Z，均 http_status 0、"
                 "无响应体）；期间同内容的裁剪小图请求 200 成功（req "
                 "B01-case-05-zoom-landfall-v11-20261010T012723Z）",
     "note": "大 payload 链路抖动时先渲染裁剪区确认 DSL 无问题，再按新版本号重发；"
             "失败记录保留，不计入视觉迭代"},
]

TOOLS = [
    {"tool": "python 数值模型（无第三方库）",
     "purpose": "case-04：固定种子 20261009 生成 96 人次到达/分诊/占用事件流，"
                "反算等待、Esi 分布、最长候诊、床位占用；case-05：17 点路径表逐小时"
                "插值→登陆判定→7/10/12 级风圈覆盖→沿岸站增水衰减，全部显示数字同源",
     "input": "tmp/%s/B01/case04_triage.py, case05_typhoon.py" % rid,
     "output": "两图 .snapshot 与生成器 stdout 的一致性断言",
     "at": NOW, "affects": "B01 case-04 / case-05",
     "requests_ref": ["B01-case-04-v01-20261009T112601Z",
                      "B01-case-05-v12-20261010T012857Z"]},
    {"tool": "python + PIL 裁切放大（仅用于看图 QA）",
     "purpose": "把 1600x1200 成品的登陆点区域裁成 340x150 再 3x LANCZOS 放大，"
                "用来确认标注避让是否真的生效",
     "input": "tmp/%s/B01/case-05/z-landfall-v10.png, z-landfall-v11.png" % rid,
     "output": "tmp/%s/B01/case-05/z-landfall-v10-3x.png, z-landfall-v11-3x.png" % rid,
     "at": NOW, "affects": "B01 case-05 v11/v12 判定",
     "requests_ref": [],
     "note": "放大图只用于观察，不进入成品；成品保留服务原始 PNG 字节"},
    {"tool": "zoom.py + render.py 裁剪区渲染",
     "purpose": "用 ClipRect+Positioned 负偏移重建 DSL 局部，向服务请求 340x150 裁剪图，"
                "比整图 1600x1200 更快看清细节",
     "input": "tmp/%s/B01/case-05/case05.snapshot" % rid,
     "output": "tmp/%s/B01/case-05/z-landfall-v06/v10/v11.png" % rid,
     "at": NOW, "affects": "B01 case-05",
     "requests_ref": ["B01-case-05-zoom-landfall-v06-20261010T011532Z",
                      "B01-case-05-zoom-landfall-v10-20261010T012155Z",
                      "B01-case-05-zoom-landfall-v11-20261010T012723Z"]},
    {"tool": "grep 检索已缓存文档与历史 DSL",
     "purpose": "确认 fontStyle 的合法枚举（历史成品里只有 BOLD 出现过）",
     "input": "outputs/%s/**/*.snapshot 与 tmp/%s/_suite/docs" % (rid, rid),
     "output": "tmp/%s/B01/capability-findings.json 追加项" % rid,
     "at": NOW, "affects": "B01 case-05 v09 起",
     "requests_ref": [],
     "note": "复用已下载文档缓存，不新增 HTTP 请求"},
]

p = TMP / "capability-findings.json"
d = json.loads(p.read_text(encoding="utf-8"))
d["addenda"] = [{"recorded_at": NOW, "scope": "case-01..case-05", "findings": NEW}]
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

base = len([1 for _ in open(TMP / "tool-usage.jsonl", encoding="utf-8")])
with open(TMP / "tool-usage.jsonl", "a", encoding="utf-8") as f:
    for i, t in enumerate(TOOLS, base + 1):
        t["id"] = "B01-tool-%03d" % i
        t["path_base"] = "suite_root"
        f.write(json.dumps(t, ensure_ascii=False) + "\n")
print("findings", len(NEW), "tools", len(TOOLS), "tool-usage total", base + len(TOOLS))
