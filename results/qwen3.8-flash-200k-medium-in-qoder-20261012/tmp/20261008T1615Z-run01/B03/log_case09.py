"""把 case-09 的迭代与工具使用记录补进 B03 的 jsonl（一次性脚本，保留为过程留痕）。"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
B = ROOT / "tmp" / RID / "B03"
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
PB = "suite_root"


def it(v, parent, typ, req, nbytes, obs, chg, rec):
    return dict(version="case-09-v%s" % v, parent_version=parent, type=typ,
                request_id=req,
                image_path="outputs/%s/B03/case-09/v%s-preview.png" % (RID, v),
                image_viewed=True, response_bytes=nbytes,
                observed_problems=obs, changes_made=chg, recompare_result=rec,
                completed=True)


IT = [
    it(1, None, "baseline", "B03-case-09-v01-20261011T053632Z", 634310,
       "150px 描边「裁」与 kicker、主标题撞成一团；hl-sub 排到 x=1080 越出 1040 右边距；"
       "左栏开本表数字被拼贴底衬压住；A4/A5/A6 标签全部挤在同一个角；√2 作图太小且标注落在环带内",
       "记录失败项：报头重排、副题收宽、标签角位避让、作图放大",
       "全图可读但报头与右栏不可用，进入 v02"),
    it(2, "case-09-v01", "visual-fix", "B03-case-09-v02-20261011T053947Z", 627037,
       "报头与副题正常、标签分角放出；但 A1 窗口落在 A0 的**上半**，把 A0 标签整个盖住；"
       "本地断言 OY−DIAG >= yy+24 失败（742 vs 736）",
       "报头改 130px 描边＋文字右移；hl-sub 宽 496；作图圆心 OY = yy+DIAG+26",
       "风车顺序仍不成立 → 定位到 sub_rect() 的裁半语义写反（y += 0.0 if side=='下' else h）"),
    it(3, "case-09-v02", "structural", "B03-case-09-v03-20261011T054044Z", 704966,
       "裁半方向修正后拼贴读通（A0 上、A1 左下、A2 右下…）；但每块板仍按 ISO 表竖幅尺寸绘制，"
       "落进横幅槽时超出 164px，压住右栏「本辑要目」标题与要目前两行；A6 标签四角全撞，"
       "避让算法按设计抛 AssertionError: A6（没有静默丢标签）",
       "sub_rect() 改为 y += h if side=='下' else 0.0、x += w if side=='右' else 0.0；"
       "assert 允许长短边互换（容差 0.6px，差值来自标准表取整）",
       "溢出根因确认在绘制尺寸而非裁半逻辑，进入 v04"),
    it(4, "case-09-v03", "visual-fix", "B03-case-09-v04-20261011T054145Z", 655435,
       "wall() 按落位槽绘制后拼贴完整内嵌；新缺陷：A3 与 A4 标签同角相撞、A6 三个角相撞，"
       "仍触发 AssertionError",
       "标签候选扩为「角位 × 纵向微调（0/±22/±44/66）」并加一档单行紧凑标签（120×20 / 64×20）",
       "7 个标签全部放出且互不相交；√2 图放大后内容却不见了，进入 v05"),
    it(5, "case-09-v04", "visual-fix", "B03-case-09-v05-20261011T054442Z", 655328,
       "PIL 裁剪放大确认三处：① √2 图里正方形与红色对角线**完全看不见**——圆环的内圆是用底色"
       "填出来的，后画把先画的盖掉了；② 标签像贴纸压在正文上（A0 首行「纸是有秩序的」被切）；"
       "③ A5 深色板配深色标签对比不足",
       "圆环改为先画；标签先定位、正文让出标签所在横带（rows 按剩余带高重算并 assert rows>=1）；"
       "标签加 2px 纸色描边垫层；角位内缩 6→9px 给旋转留量",
       "作图恢复可读、标签不再压字；字数由 A0 552→504、A6 36→12，标签与 data.json 同步"),
    it(6, "case-09-v05", "visual-fix", "B03-case-09-v06-20261011T055028Z", 574091,
       "全图与中心群裁剪：标签带纸色描边后在深底上分离清楚，正文让带后无压字；"
       "像素级裁剪看到 √2 标签正好被圆环**下弧**穿过（交点处弧落在标签行内），读成「−2」",
       "√2 标签由「交点居中」改为「交点右侧弧外」（IX+10、宽 40、START 对齐）；"
       "docstring 字源字数 288→242 与实算 P_LEN 对齐",
       "标签与弧线分离，进入 v07 复核"),
    it(7, "case-09-v06", "visual-fix", "B03-case-09-v07-20261011T055152Z", 574085,
       "首试 B03-case-09-v07-20261011T055124Z 失败：curl (28) SSL/TLS connection timeout，"
       "http 0、无响应体（render.py 按 --retries 3 自动重试成功）；成品全图复核未见新增缺陷",
       "无改动，仅重试渲染",
       "七级窗口全部在拼贴框内、标签 7/7 放出、√2 三要素齐备、要目与条码区不与拼贴相接；"
       "定为 final（md5 db674fd69dabb439365c707a924ff333）"),
]
for r in IT:
    r.update(recorded_at=NOW, task_id="B03", run_id=RID, path_base=PB,
             image_viewed_at=NOW)
    r["iteration_id"] = r["request_id"][:29]

TU = [
    dict(tool="open-snapshot 渲染服务", phase="render", case="case-09",
         what="7 个版本 8 次请求（1 次 curl SSL 超时后重试成功），全部为整幅 1080×1440 DSL",
         evidence="requests.jsonl 中 B03-case-09-v01…v07；成品响应 574085 字节、"
                  "server_timing render;dur=833.9, total;dur=1013.9",
         outcome="final.png 与服务端原始响应字节 md5 一致（promote.py 用指纹校验）",
         request_ids=["B03-case-09-v07-20261011T055124Z",
                      "B03-case-09-v07-20261011T055152Z"]),
    dict(tool="ClipRRect / ClipOval 遮罩", phase="layout", case="case-09",
         what="七个窗口各套一层 ClipRRect（统一 borderRadius=6）；√2 圆环用 ClipOval 外套"
              "＋内嵌同心 Container 挖出 3px 环",
         evidence="final.snapshot 内 ClipRRect 7 处、ClipOval 1 处；未使用 Container 的 "
                  "clipBehavior（case-01/08 已证其对整幅子树会 400 或无效）",
         outcome="遮罩只裁子树、不改变坐标，因此窗口边界仍等于纸型边界，可逐级 assert",
         request_ids=[]),
    dict(tool="Container transform 旋转变换", phase="visual", case="case-09",
         what="七个窗口分别绕自身中心旋转 0/−1.2/+0.9/−0.7/+1.5/−1.0/+0.7 度，模拟套准偏差",
         evidence="final.snapshot 内 transform= 7 处（配 transformAlignment=\"CENTER\"）；"
                  "角度写入 data.json.iso216[*].rot",
         outcome="旋转使角位内缩从 6px 增到 9px，避免标签被转出板外；错位量成为可核对的设计参数",
         request_ids=["B03-case-09-v03-20261011T054044Z"]),
    dict(tool="foregroundMode STROKE 描边字", phase="visual", case="case-09",
         what="每三行正文改一次 STROKE（fg_w=1.0）与实心混排；报头「裁」用 3px 描边空心字",
         evidence="final.snapshot 内 STROKE 22 处；v01 看图时 150px 描边字与标题相撞，v02 改 130px",
         outcome="描边行在远看时形成灰度带，近看仍是同一字源，未引入额外素材",
         request_ids=["B03-case-09-v01-20261011T053632Z",
                      "B03-case-09-v02-20261011T053947Z"]),
    dict(tool="PIL 裁剪放大看图", phase="review", case="case-09",
         what="对 v05/v06 裁出中心标签群、A0 标签与首行、√2 作图、底部边界四块放大 1.4–2× 观察",
         evidence="tmp/<run>/B03/case09-qa-{cluster,a0tag,fig,bottom}-v05.png 与 "
                  "case09-qa-{cluster,a0tag,fig}-v06.png、case09-qa-fig-v07.png 共 8 张",
         outcome="发现并修掉两个全图看不出的缺陷：圆环内圆盖掉作图内容、√2 标签被下弧穿过；"
                 "裁剪图只用于观察，不作为成品",
         request_ids=["B03-case-09-v05-20261011T054442Z",
                      "B03-case-09-v06-20261011T055028Z"]),
    dict(tool="TextFit 文本适配检查", phase="layout", case="case-09",
         what="每个文本节点记录声明框与实测宽高，超框即计入 problems",
         evidence="v07 受检 83 项、problems 0（开发期曾有 con-3、con-5、bc-n 三处超框，本地报错未出图）",
         outcome="con-3 框高 40→50、条码单元 2.0→3.0px、注记文案改短，全部按可用高度反算",
         request_ids=[]),
    dict(tool="运行时 assert 结构校核", phase="layout", case="case-09",
         what="七级矩形与 ISO 216 标准表逐级比对、窗口必须落在拼贴框内、标签必须完整落在本级板内、"
              "rows>=1、右栏与要目区不越界",
         evidence="v03 触发 AssertionError: A6（标签放不下）而非静默丢标签；"
                  "v02 触发 OY−DIAG 断言（742 vs 736）",
         outcome="失败即中断不出图，迫使避让算法补档而不是删内容；两处断言都进了迭代表",
         request_ids=[]),
    dict(tool="render.py 失败与重试处理", phase="render", case="case-09",
         what="v07 首试 curl (28) SSL/TLS connection timeout（http 0、无响应体），脚本按 --retries 3 重试",
         evidence="requests.jsonl 两条 v07 记录：055124Z 失败、055152Z 200；"
                  "promote.py 原实现取首条同名记录，会误提失败响应，已改为取最后一次 200",
         outcome="提升脚本修正后 final.png 校验通过；失败记录保留不删",
         request_ids=["B03-case-09-v07-20261011T055124Z"]),
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
