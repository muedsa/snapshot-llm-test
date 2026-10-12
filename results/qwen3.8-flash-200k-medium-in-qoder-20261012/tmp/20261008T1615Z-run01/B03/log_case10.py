"""把 case-10 的迭代与工具使用记录补进 B03 的 jsonl（一次性脚本，保留为过程留痕）。"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
B = ROOT / "tmp" / RID / "B03"
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
PB = "suite_root"


def it(v, parent, typ, req, nbytes, obs, chg, rec, viewed=True, scope="整幅成品 PNG"):
    return dict(version="case-10-v%s" % v, parent_version=parent, type=typ,
                request_id=req,
                image_path="outputs/%s/B03/case-10/v%s-preview.png" % (RID, v),
                image_viewed=viewed, image_view_scope=scope,
                response_bytes=nbytes, observed_problems=obs, changes_made=chg,
                recompare_result=rec, completed=True)


IT = [
    it(1, None, "baseline", "B03-case-10-v01-20261011T060242Z", 461948,
       "首版按设计没有实测值（全页「待测」）；看图两处缺陷：页眉 82px 描边「Aa」标记压在 "
       "v01·2026-10-11·1080×1920 版本号行上；§04 行高只有四栏，缺「不写 height」的默认档，"
       "无法证明 height 是乘字号还是乘默认行距",
       "标记上移到 y=16/高 86、版本行下移到 y=106；§04 增默认档成五栏并列；"
       "同时把 31 条测量带坐标写进 data.json 供扫描",
       "版式与留白成立（y_end 1864.5），但埋下位置键隐患 → v02"),
    it(2, "case-10-v01", "structural", "B03-case-10-v02-20261011T060735Z", 480298,
       "看图发现 §04 五栏的「实测行距」整体串了一栏：默认档显示待测、1.0 档显示 21、"
       "1.25 档显示 26……根因是测量带用位置键 h-0…h-4，插入默认列后键整体右移一位，"
       "把上一版 1.25 档的数读成了 1.0 档的数（页面结论因此失真）",
       "测量带键名改绑参数本身（h-def / h-1 / h-1.25 / h-1.5 / h-1.9）；"
       "case10_measure.py 加 --remap 做一次性键名迁移，把 v01 的四个值搬到新键上",
       "键名错位是这一页最致命的错误（数字错比没数字更坏），必须重排 §04 → v03"),
    it(3, "case-10-v02", "visual-fix", "B03-case-10-v03-20261011T061106Z", 499565,
       "§04 新加的两行说明文字压在五栏「行距 …｜预期 …」标题行上，整块重叠不可读；"
       "另外 v02 的实测行距（默认 20.8、1.0 16.8、1.25 20.8、1.5 25.8、1.9 31.8）"
       "显示默认档只有 1.22em，页面里 1.45em 的估算常数被实测推翻",
       "段落框改 valign=TOP 并按实际墨迹高度收拢（BLOCK 110.9→100.6），"
       "说明行移到标题行下方并压成一行；§01/§02/§05/§06 行距各收 1px 给说明行腾位",
       "§04 分块干净可读；QA 2× 裁图另暴露 §07 说明行与页脚横线相撞 → v04"),
    it(4, "case-10-v03", "visual-fix", "B03-case-10-v04-20261011T061302Z", 489997,
       "qa07-v04.png 放大后看到 §07 红色说明行的下沿正压在页脚横线上，横线又贴着方法注记；"
       "四条节末结论行与下一节的编号「02/03/05」之间只剩 2px 视觉空隙",
       "st-note 盒高 24→26、其后留距 24→32；w/ls/ws/fb 四条 note 各让 2px；"
       "§05 结论从「与已安装族都不等」升级为「3、4 两行实测同为 186px」这一更强证据",
       "留距正常；但本版生成时漏了测量文件 → v05 成为一次失误记录"),
    it(5, "case-10-v04", "process-error", "B03-case-10-v05-20261011T061435Z", 462449,
       "生成器输出 measured 0、TextFit 145 检（应为 161）：本版读不到 case10-measure-v05.json，"
       "整页实测列印成「待测」，等于把这一页的立身之本丢了。依闸门输出即判定不可用，"
       "未逐张看图（image_viewed=False，不伪造看图记录）",
       "补上流程：先扫上一版 PNG 产出本版测量文件，再生成本版 DSL；"
       "用 v05 的 PNG 与 v05 的 data.json 量出 case10-measure-v06.json",
       "本版保留为失误证据，不提升、不计入成品；数字与 v04 相同，说明测量口径稳定"),
    it(6, "case-10-v05", "gate-fix", "B03-case-10-v06-20261011T061503Z", 491907,
       "TextFit 提交前报警：fb-note 估算 2 行 957×28 超出盒子 968×24。2× 裁图看实际渲染并未裁切"
       "（估算偏保守），但本套件规定闸门带警不提交",
       "fb-note 文案收短（估算宽 957→887，回到单行），实测值全部印回",
       "闸门归零 → v07 复核"),
    it(7, "case-10-v06", "final", "B03-case-10-v07-20261011T061612Z", 490715,
       "全图复核：31 条实测全部印回、五栏行距与结论行分列清楚、§07 与页脚留距正常、"
       "底部留白 27px；TextFit 161 检 0 警；未发现新增缺陷",
       "无改动",
       "定为 final（md5 8c45a6f544868168be9addf23ab54f4e，promote.py 字节指纹校验通过）"),
]
for r in IT:
    r.update(recorded_at=NOW, task_id="B03", run_id=RID, path_base=PB,
             image_viewed_at=NOW if r["image_viewed"] else None)
    r["iteration_id"] = r["request_id"][:29]

TU = [
    dict(tool="open-snapshot 渲染服务", phase="render", case="case-10",
         what="7 个版本 7 次整幅 1080×1920 DSL 渲染，全部 HTTP 200，无失败响应、无重试",
         evidence="requests.jsonl 中 B03-case-10-v01…v07；server_timing render;dur 从 "
                  "4650.3ms（v01）降到 931.3ms（v07），响应体 461948–499565 字节",
         outcome="final.png 与服务端原始响应字节 md5 一致（8c45a6f544868168be9addf23ab54f4e）",
         request_ids=["B03-case-10-v01-20261011T060242Z",
                      "B03-case-10-v07-20261011T061612Z"]),
    dict(tool="PIL + numpy 成品像素扫描（case10_measure.py）", phase="review", case="case-10",
         what="按 data.json.bands 的 31 条坐标带扫描上一版 PNG：宽度取首末墨迹列之差、"
              "字重取墨迹面积占比、行高栏取相邻两行墨迹中心间距的中位数",
         evidence="case10-measure-v02…v07.json 六份（含 values 与逐带 meta：area_px、"
                  "row_groups、first_row_top）；背景取全图众数色，阈值「色距 > 40」写进 json",
         outcome="页面全部「实测」数字的唯一来源；量出 letterSpacing 严格线性（+1px×9 间隙）、"
                 "wordSpacing 仅作用于 2 个空格、height 乘字号（默认档 1.22em 而非 1.45em）、"
                 "fontFeatures 四组零差、STROKE 三档外框同为 129px",
         request_ids=[]),
    dict(tool="测量带键名迁移 --remap", phase="layout", case="case-10",
         what="§04 由四栏改五栏后，把上一版按位置编号的 h-0…h-3 迁到按参数命名的 h-def/h-1/…",
         evidence="case10_measure.py 的 --remap h-0=h-def,h-1=h-1,h-2=h-1.25,h-3=h-1.5,h-4=h-1.9 "
                  "与 case10-measure-v03.json",
         outcome="避免「数字串栏」这种比缺数更坏的错；此后所有测量带键名一律绑定参数值",
         request_ids=["B03-case-10-v02-20261011T060735Z"]),
    dict(tool="生成器内复现实验（case10_type_v03era.py）", phase="review", case="case-10",
         what="为取回被覆盖的 v03 版 data.json 坐标，临时还原 v03 时代的版式常量并重跑生成器",
         evidence="重跑得到的 case10-v03.snapshot 与渲染时留存的副本 md5 完全相同"
                  "（925b13bff02b822dd1c41ee21600bbad），先第一次差 2px（st-note 留距误改），"
                  "修正后一致",
         outcome="证明 DSL 生成是确定性的，可安全用于历史版本的坐标复原；测量因此仍指向真实那一版",
         request_ids=["B03-case-10-v03-20261011T061106Z"]),
    dict(tool="GET /fonts 字族清单（复用已缓存结果）", phase="research", case="case-10",
         what="27 个已安装族作为本页唯一可用字族；断言 Inter 各字重族在列、"
              "IBM Plex Mono / Courier New / Helvetica 不在列",
         evidence="tmp/<run>/_suite/docs/fonts.txt（2026-10-08 取得并缓存，本用例未重复请求）；"
                  "case10_type.py 开头三条 assert",
         outcome="回退实验（§05）因此可证伪；本页未使用任何未安装字族当作已安装来排版",
         request_ids=[]),
    dict(tool="TextFit 文本适配闸门", phase="layout", case="case-10",
         what="161 处文本发射前逐条估算宽高与行数，超框即记 problems",
         evidence="v06 报 1 条：fb-note 2line est 957x28 > box 968x24；改短后 v07 为 161 检 0 警",
         outcome="带警不提交：文案收短到估算宽 887 后才渲染下一版；"
                 "同时记录该闸门偏保守（实际渲染未裁切），估算余量按 SLACK=0.96 计",
         request_ids=["B03-case-10-v06-20261011T061503Z"]),
    dict(tool="运行时 assert 版式自校", phase="layout", case="case-10",
         what="字族数量与缺列断言、断言 y+72<=1920（页脚不越界）、测量带数量与实测数量对齐",
         evidence="首版排到 3351px、压缩后仍 2221px 两次触发 AssertionError，"
                  "遂把 §04 改五栏并列、节标题降到 36px、行步进 38–40px；"
                  "v05 的 measured 0 即由生成器打印暴露",
         outcome="溢出与丢数都在本地中断，不靠看图事后发现；最终 layout_y_end 1892.6",
         request_ids=["B03-case-10-v01-20261011T060242Z"]),
    dict(tool="DSL 排版属性：letterSpacing / wordSpacing / height / fontFeatures / foregroundMode",
         phase="dsl", case="case-10",
         what="四档字距、三档词距、五档行高、四组 OpenType 特性、三档描边各占独立测量带，"
              "同一文本只改一个属性以便归因",
         evidence="final.snapshot 里 Text 级属性计数：letterSpacing 3（ls=0 档不输出该属性）、"
                  "wordSpacing 2、height 7（§04 四档 + 两处 1.35 注记）、fontFeatures 3、"
                  "foregroundMode=\"STROKE\" 4（§07 三档 + 页眉 Aa 描边）、Text 161、Positioned 171",
         outcome="把「文档里写了」与「渲染器做了」分开陈述：前三类可复现，fontFeatures 明确标注不生效",
         request_ids=["B03-case-10-v07-20261011T061612Z"]),
    dict(tool="PIL 裁剪放大看图（QA）", phase="review", case="case-10",
         what="对 v04 裁 §01 / §04 / §07 三块、对 v06 裁 §05 结论行与 §07+页脚两块，放大 2× 观察",
         evidence="tmp/<run>/B03/qa{01,04,07}-v04.png 与 qa{05,07}-v06.png 共 5 张（仅观察用，不入成品）",
         outcome="发现全图看不出的 §07 说明行与页脚横线相撞；同时确认 TextFit 对 fb-note 的告警"
                 "属保守误报（实际未裁切）",
         request_ids=["B03-case-10-v04-20261011T061302Z",
                      "B03-case-10-v06-20261011T061503Z"]),
    dict(tool="promote.py 字节指纹提升", phase="promote", case="case-10",
         what="从 requests.jsonl 取该版本最后一次 200 响应，校验响应副本与 out_file 同 md5，"
              "再从请求 body 切出完整 DSL 写 final.snapshot",
         evidence="提升输出：request B03-case-10-v07-20261011T061612Z、"
                  "final_png_md5 8c45a6f544868168be9addf23ab54f4e、dsl_chars 44332",
         outcome="首次从 tmp 子目录运行因记录内路径以总根为基准而 FileNotFoundError，"
                 "改在总任务根运行后通过——path_base=suite_root 的既有约定",
         request_ids=["B03-case-10-v07-20261011T061612Z"]),
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
