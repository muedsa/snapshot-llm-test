"""把 case-08 的迭代与工具使用记录补进 B03 的 jsonl（一次性脚本，保留为过程留痕）。"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
B = ROOT / "tmp" / RID / "B03"
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
PB = "suite_root"

IT = [
    dict(version="case-08-v01", parent_version=None, type="baseline",
         request_id="B03-case-08-v01c-20261010T125821Z",
         image_path="outputs/%s/B03/case-08/v01-preview.png" % RID,
         image_viewed=True, response_bytes=262955,
         observed_problems="北斗七星 7 个星名标注全部未出现：星点落在 HUD 卡片与准星读数之下，避让函数判冲突后静默跳过；三页面板压在方位带与提示行上；投影视轴与锁定目标强行重合导致低空北斗与北极星无法同框",
         changes_made="记录失败：视轴/目标分离方案 + 登记面板为 BLOCK + 星点登记为 RESERVED",
         recompare_result="同版本另有 2 次 400（border=\"0\" 非法），失败请求与响应留 tmp/<run>/B03/case-08/requests/",
         completed=True),
    dict(version="case-08-v02", parent_version="case-08-v01", type="structural",
         request_id="B03-case-08-v02-20261010T130655Z",
         image_path="outputs/%s/B03/case-08/v02-preview.png" % RID,
         image_viewed=True, response_bytes=265036,
         observed_problems="视轴改 (344°,20°) 后北斗与北极星同框、8 个标注放出 6 个（天权、摇光仍被跳）；视场外指示条压在 20° 网格线上读不清；页脚第二行贴住罗盘带上边",
         changes_made="准星读数移到目标左侧、三页面板移进右列、候选偏移避让算法上线；border=\"0\" 改为不输出该属性",
         recompare_result="构图成立，标注密度仍不足，进入 v03",
         completed=True),
    dict(version="case-08-v03", parent_version="case-08-v02", type="visual-fix",
         request_id="B03-case-08-v03-20261010T131436Z",
         image_path="outputs/%s/B03/case-08/v03-preview.png" % RID,
         image_viewed=True, response_bytes=268142,
         observed_problems="8 个星名标注全部放出、0 跳过，指示条清晰；但天枢的长引线从天权星点旁擦过，归属靠肉眼追；曲线只占面板 2/3 高且「「,」为地平线下」实际无逗号出现",
         changes_made="候选偏移 12→20 并按标签实际宽度（150/240）算左放位；指示条加深色底垫；页脚与罗盘带留距并加 assert",
         recompare_result="标注与指示均可读，遗留归属歧义与面板留白",
         completed=True),
    dict(version="case-08-v04", parent_version="case-08-v03", type="visual-fix",
         request_id="B03-case-08-v04-20261010T132137Z",
         image_path="outputs/%s/B03/case-08/v04-preview.png" % RID,
         image_viewed=True, response_bytes=269234,
         observed_problems="裁剪复核确认：星点小圈＋从圈边出发的引线消除了 bowl 四星的归属歧义；曲线 11 格填满面板，地下点数改为实算「末 12 点在地下」；罗盘 000° 刻度与数字仍显挤",
         changes_made="加 22px 星点圈与角度化引线（目标用 95px 准星半径起笔）；NR 7→11；删掉不成立的逗号注记",
         recompare_result="左上 40°×30° 区域仍无任何可用信息，进入 v05",
         completed=True),
    dict(version="case-08-v05", parent_version="case-08-v04", type="visual-fix",
         request_id="B03-case-08-v05-20261010T132726Z",
         image_path="outputs/%s/B03/case-08/v05-preview.png" % RID,
         image_viewed=True, response_bytes=277222,
         observed_problems="加角距标尺后需确认它与 10° 高度轴文字不相压",
         changes_made="10° 标尺（11 格、每格 1°、中线加长）＋两行比例说明，并登记进 BLOCK；罗盘刻度改 14/7px、数字下移 4px",
         recompare_result="PIL 扫 x=200 列：标尺线 y=639-640、说明 659-688、10° 轴文字 713-730，三段分离；TextFit 83 节点 0 问题。定为 final（md5 6ad124d93af65cb0b9ac59e4d8c2daea）",
         completed=True),
]
for r in IT:
    r.update(iteration_id="B03-" + r["version"][:6] + "-" + r["request_id"].split("-")[-1][:15],
             task_id="B03", run_id=RID, recorded_at=NOW,
             image_viewed_at=NOW, path_base=PB)
    r["iteration_id"] = r["request_id"][:29]

TU = [
    dict(tool="GMST/时角/地平坐标投影内核", phase="data-model", case="case-08",
         what="JD→GMST(360.98564736629 系数)→LST→时角→方位/高度，再按 19.2 px/° 等比投影到 100°×56.25° 视场；升降与没入时刻用 1 分钟步长推进",
         evidence="astro8.py 与 data.json.checks：LST 22:32:18、北极星 h 40.27° vs 纬度 39.9042°、太阳上中天 43.31° vs 43.32°、新月合经度差 0.07°",
         outcome="页面上每个读数可复算；三处独立校核写进 data.json 而不是只写在注释里",
         request_ids=[]),
    dict(tool="银道面反算（J2000 旋转矩阵）", phase="data-model", case="case-08",
         what="银经 0–360°、银纬 0° 转赤道坐标再转地平坐标，求本视场内银道面高度带",
         evidence="gal2eq(0,0)→(266.4°,-28.94°)、gal2eq(122.93,90)→(192.86°,27.13°) 与已知银极/银心值差 <0.3°；本视场带高 56°~74°，框内点数 0",
         outcome="据此不画银河带，只在档案卡留一行读数——避免把装饰当数据",
         request_ids=[]),
    dict(tool="指极星延长比值检验", phase="data-model", case="case-08",
         what="球面角距算 天枢–北极星 / 天璇–天枢 比值，按屏幕向量延长后与北极星真实投影比对",
         evidence="28.71°/5.37°＝5.34；落点 (1227,146) vs 投影 (1283,151)，差 57px＝2.94°",
         outcome="把投影不保大圆的缺陷转成画面注记与 data.json.known_error",
         request_ids=[]),
    dict(tool="标注避让（BLOCK/RESERVED/候选偏移）", phase="layout", case="case-08",
         what="面板、准星、读数框、标尺登记为 BLOCK，星点登记为 RESERVED，标签从 20 个候选偏移里选第一个不压字且不出天空区的位置",
         evidence="v01 放出 1/8 → v02 6/8 → v03 起 8/8、跳过 0；视场外指示 5/5 全部放出",
         outcome="标注可读性由算法保证，改时刻/视场不需手工重排坐标",
         request_ids=[]),
    dict(tool="PIL 裁剪与像素扫描看图", phase="visual-qa", case="case-08",
         what="对 v03/v04/v05 裁出北斗、右列面板、左侧指示条、角距标尺、北极星区、罗盘 000° 六块放大观察；再扫 x=200 竖列定位标尺与轴文字的 y",
         evidence="case08-qa-*.png 共 7 张；扫描结果 639-640 / 659-688 / 713-730 三段分离",
         outcome="目测以为的标尺与轴文字冲突被证伪；确认圈＋引线消除归属歧义",
         request_ids=["B03-case-08-v04-20261010T132137Z", "B03-case-08-v05-20261010T132726Z"]),
    dict(tool="TextFit 文本适配检查", phase="layout", case="case-08",
         what="每个文本节点记录声明框与实测宽高，超框即报错",
         evidence="v05 共 83 个受检节点、problems 0（v02 曾有 ft-l 513×29 与 bd-1 476×29 两处溢出）",
         outcome="卡片行数、面板页数、脚注长度全部改为按可用高度反算并加 assert",
         request_ids=[]),
    dict(tool="render.py 语法错误处理", phase="render", case="case-08",
         what="border=\"0\" 触发服务端 400 PARSE_ERROR；修复脚本时又因 Python 3.11 f-string 表达式含反斜杠而 SyntaxError",
         evidence="requests.jsonl 两条 400（v01、v01b）＋本地 SyntaxError；教训：诊断时不要 >/dev/null 2>&1 吞掉 stderr，且要用 grep 复验产物而不是相信链式命令的退出码",
         outcome="改为不输出 border 属性；battr 预计算避开 f-string 反斜杠限制",
         request_ids=["B03-case-08-v01-20261010T125437Z", "B03-case-08-v01b-20261010T125608Z"]),
]
for r in TU:
    r.update(recorded_at=NOW, task_id="B03", run_id=RID, path_base=PB)

with (B / "iterations.jsonl").open("a", encoding="utf-8") as f:
    for r in IT:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
with (B / "tool-usage.jsonl").open("a", encoding="utf-8") as f:
    for r in TU:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("appended", len(IT), "iterations", len(TU), "tool-usage")
