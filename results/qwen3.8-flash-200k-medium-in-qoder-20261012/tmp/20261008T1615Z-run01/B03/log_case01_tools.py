"""B03 收尾核对：为 case-01 补写 tool-usage 记录。

case-01 当时只在 iterations.jsonl 与 case.md 里留痕，没有逐条工具记录（本题的
tool-usage 记录约定从 case-02 起才生效，case-08 之后才做到每件 5 条以上）。
这里补的不是「新使用」，而是把已经发生、且有文件可查的使用事件按同一 schema 登记，
因此每条 evidence 都指向可核对的 request_id、成品 DSL 标签计数或 tmp 下的 QA 裁图，
并把补记这件事本身写进 logged_via。不新增任何未发生过的操作。

用法（总任务根执行）：python tmp/<run>/B03/log_case01_tools.py
"""
import datetime
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
B = ROOT / "tmp" / RID / "B03"
PB = "suite_root"
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

REQ = {}
for line in (B / "requests.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(line)
    REQ[r["request_id"]] = r


def rid(prefix):
    hit = next(k for k in REQ if k.startswith(prefix))
    return hit


R = [
    dict(tool="open-snapshot 渲染服务", phase="render", case="case-01",
         what="5 个版本 v01–v05 各 1 次整幅 2400×1200 DSL 请求，全部 200，无失败响应",
         evidence="requests.jsonl 中 B03-case-01-v01…v05；定稿 v05 响应头 "
                  "Server-Timing render;dur=4636.6, total;dur=4972.7；"
                  "五张预览 outputs/%s/B03/case-01/vNN-preview.png" % RID,
         outcome="final.png（md5 %s）由 v05 原始响应字节提升，"
                 "final.snapshot 90 531 字符与该请求 body 分隔符后内容一致"
                 % hashlib.md5(
                     (ROOT / "outputs" / RID / "B03" / "case-01" / "final.png").read_bytes()
                 ).hexdigest(),
         request_ids=[rid("B03-case-01-v%02d" % i) for i in range(1, 6)]),
    dict(tool="ImageFiltered 三层高斯模糊（霓虹芯＋辉光）", phase="visual", case="case-01",
         what="招牌与灯管文字用「外晕 sigma 46 / 中晕 22 / 芯层」三层 ImageFiltered 叠出霓虹；"
              "地面倒影是渐变条整体套 ImageFiltered sigma=10",
         evidence="case-01/final.snapshot 内 <ImageFiltered 12 处；对比探针 %s"
                  "（同图先 textShadow 后 ImageFiltered）；文档缓存 tmp/%s/_suite/docs/"
                  "image-filtered.html.txt；v01 方板光晕见 tmp/%s/B03/case-01/qa-sign.png"
                  % (rid("B03-probe-20-if-neon"), RID, RID),
         outcome="辉光按字形外扩且不被文字排版矩形截断，v01 的方形光板缺陷在 v02 起消失",
         request_ids=[rid("B03-probe-20-if-neon"), rid("B03-case-01-v01")]),
    dict(tool="ClipOval 层叠 + RADIAL 渐变（月牙）", phase="layout", case="case-01",
         what="亮圆＋取色自同一天空分带插值的遮挡圆剪出月牙，环境光晕用两端透明的 "
              "RADIAL 渐变而非 boxShadow",
         evidence="final.snapshot 内 <ClipOval 2 处；探针 %s（RADIAL + focal 成立，probe 图 "
                  "probe/05-radial-focal.png）；v01 的 boxShadow 光晕即使配 borderRadius 仍呈方角，"
                  "该观察在 tmp/%s/B03/case-01/qa-moon.png 与 qa-sign.png 上直接看到"
                  % (rid("B03-probe-05-radial-focal"), RID),
         outcome="月牙形状与天空分带色一致，方角光晕改为圆形渐变；遮挡色由 sky_tone(y) 算出而非手填",
         request_ids=[rid("B03-probe-05-radial-focal")]),
    dict(tool="Container transform 2D 仿射斜切", phase="visual", case="case-01",
         what="雨棚用 b03kit.skew(x,y) 写进 transform（列主序 4×4）做斜切；透视矩阵项实测无视觉效果，"
              "因此全图只用 2D 仿射",
         evidence="final.snapshot 内 transform= 1 处；探针 %s（skew 成立）与 %s 系列"
                  "（perspective index 11 无变化）"
                  % (rid("B03-probe-02-skew"), rid("B03-probe-01-perspective")),
         outcome="雨棚斜边与招牌透视一致且不依赖不生效的矩阵项；该结论写进 case.md「已确认边界」",
         request_ids=[rid("B03-probe-02-skew"), rid("B03-probe-01-perspective")]),
    dict(tool="PIL 裁剪放大看图", phase="review", case="case-01",
         what="整幅看 5 次（v01–v05）后再裁局部 8 块放大观察：招牌、月牙、橱窗、右栏、标注、"
              "v04/v05 地面各两张",
         evidence="tmp/%s/B03/case-01/qa-{sign,moon,win,right,dims,v04-sign,v04-ground,"
                  "v05-ground}.png 共 8 张（PIL 裁剪，只作观察，不在 outputs 下）" % RID,
         outcome="量出 v01 页码行宽 130px 装不下 147px 的「41.0 m ／ 670 W」，v02 起 page_w=200/210；"
                 "v03 倒影硬边、v04 仍像一排柱子，v05 加宽 30–48px 后才是柔和拖尾",
         request_ids=[rid("B03-case-01-v04"), rid("B03-case-01-v05")]),
    dict(tool="TextFit 文本适配检查", phase="layout", case="case-01",
         what="每个文本节点经 b03kit.tlab 落位前先估算宽高，超框计入 problems",
         evidence="case01_board.py 第 106 行建 TextFit、第 325 行打印；定稿版重跑输出 "
                  "「v05 chars 90531 TextFit 25 problems 0」，重跑产物 md5 88bbc10d9a7fcc3b9f24ac8047c21a3f "
                  "与留痕 case01-v05.snapshot 全等（生成器确定性）",
         outcome="v01 的截断由看图发现、闸门在 v02 后保持 0 problems；估算器偏保守，"
                 "最终仍以看图为准",
         request_ids=[]),
]
for r in R:
    r.update(recorded_at=NOW, task_id="B03", run_id=RID, path_base=PB,
             logged_via="B03 closeout audit（按请求留痕/成品 DSL/QA 裁图补记，非使用时即时记录）")

with (B / "tool-usage.jsonl").open("a", encoding="utf-8") as f:
    for r in R:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("appended", len(R), "tool-usage records for case-01")
