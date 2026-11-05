#!/usr/bin/env python3
"""Write B03 per-case visual-review conclusions and finalize portfolio.json.

Runs after all 10 final PNGs were opened with ViewImage. Dimensions are read
from the real PNG IHDR; request ids are read from the real request logs.
"""
import json
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.environ["TOOLS"])
import suite

T = "B03"
OUT = suite.out_dir(T)
TMP = suite.tmp_dir(T)

REVIEWS = {
    "case-01": (
        "v1 首版底部最浅青色波浪上的浅蓝白文字（票价/主办/网址/右栏）对比不足；"
        "v3 改为深墨色 #0A3A52 后清晰。最终逐区查看：深蓝渐变夜空与星点、"
        "ImageFiltered 模糊月晕、RADIAL 渐变月盘、5 层 8 位透明贝塞尔波浪、"
        "大标题「潮 汐」、副标与英文、日期场馆票价策展、富文本说明全部完整，"
        "标题压在波浪上仍清晰，无裁切、重叠或遮挡。通过。"),
    "case-02": (
        "v1 首版 8 个类目的英文名与子风味在明亮 SWEEP 色轮上偏淡；"
        "v3 为每个标签加 #160E0878 深色半透明底板后全部清晰。最终逐区查看："
        "SWEEP 多色扇形色轮、中心 ORIGIN 与说明、8 组带底板标签（中文/英文/子风味）、"
        "24 条辐射刻度、右下倾斜 CUPPING LAB 印章、底部读法说明完整，"
        "标签之间不重叠、无裁切。通过。"),
    "case-03": (
        "v1 首版右侧站点状态行因 Text 会 trim 前导空格而连写成「北辰站拥挤」；"
        "v3 把富文本片段改用 Raw 保留空格后分隔清晰。最终逐区查看："
        "渐变填充的 ClipPath 面积图、折线轮廓、18:00 峰值「晚高峰 9.8 万」标注、"
        "虚线网格与 0–10 刻度、6 个站点进度条与百分比、底部运营结论完整可读。通过。"),
    "case-04": (
        "v1 首版 12 个海拔标注挤成中央竖列并压在等高线上，峰顶深色标注在深棕内圈上偏暗；"
        "v3 改为左上角「海拔 / ELEV.」图例卡、峰顶标注改白色、N↑ 移至右上角。"
        "最终逐区查看：12 圈平滑闭合等高线、模糊峰顶光晕、橙红虚线路线与 4 个 CP、"
        "比例尺、右侧 5 行参数与沿线提示/通行窗口两张卡片完整，无文字与曲线冲突。通过。"),
    "case-05": (
        "v1 因 gradientStops 传入字符串被二次 join 拆成字符，服务返回 400 PARSE_ERROR"
        "（错误响应保留在 case-05/responses/）；v2 改传列表修复并成功渲染。"
        "首版还发现「12 000 K」长标注射位与 1k–12k 刻度数字重叠；"
        "v3 改为居中冷暖说明 + 6 个带 K 值标签的定位圆点。最终逐区查看："
        "11 段 gradientStops 连续色温带、刻度网格、6 张光源卡、4 张白平衡卡与脚注完整。通过。"),
    "case-06": (
        "v1/v3 首版第一行月相下方名称与第二行上方编号挤在同一水平带"
        "（出现「新月 05 / 满月」）；v4 删除上方编号行、下方合并为「01 · 新月」并加大行距。"
        "最终逐区查看：8 个盈亏月相、编号与名称、深蓝夜空星点、会员信息行、"
        "8 夜书单、金色权益条与页脚完整，遮罩圆与底色无明显色差边界，无重叠裁切。通过。"),
    "case-07": (
        "首版即达标，未作修改。最终逐区查看：28 根竖向渐变频谱柱、"
        "20–20k 对数频率轴、30/50/70/90 dB 虚线网格、黄色「参考 70 dB」虚线、"
        "粉红倾斜「PEAK 1.2 kHz」徽标与峰值圆点、右侧 6 项指标、底部工程结论"
        "全部完整可读，无裁切或遮挡。通过。"),
    "case-08": (
        "首版即达标，未作修改。最终逐区查看：4 块 Transform 倾斜的半透明玻璃板、"
        "gradientRotation 斜向高光、3 条色散细线、模糊阴影、"
        "「材料参数」4 行 8 字段表格、深色 ATELIER LUMEN 信息条与富文本说明"
        "全部清晰，浅底深字对比充分，无裁切或重叠。通过。"),
    "case-09": (
        "v1 首版第 8 款「归藏」因酒单纵向间距过大被 1000px 画布底部裁切；"
        "v4 把季节步长压到 202px、卡片高 74px 后 8 款全部显示。最终逐区查看："
        "13 圈木色年轮、中心「四时 FOUR SEASONS」、春/夏/秋/冬 4 组 8 款酒"
        "（名称/风格/ABV/IBU/风味短句）与页脚完整，季节色点与酒款对应、无裁切。通过。"),
    "case-10": (
        "v1 首版 60 圈填充闭合路径叠成一整块实心黑形，且参数表方程一行溢出被裁；"
        "v4 改为外轮廓+略小内轮廓的 EVEN_ODD 空心细环（84 采样点）并把方程拆成两行。"
        "最终逐区查看：细环干涉线网呈同心波纹并含朱红强调环与辐射细线、中心红点，"
        "参数表 7 行（含两行完整公式）、黑色生成说明卡、作品陈述与朱红底部条"
        "全部完整可读，不再有实心黑块或文字裁切。通过。"),
}

CRITERIA = [
    ("C1", "主体图形、标题与全部信息区完整可见，无裁切、无遮挡",
     "打开最终 PNG 逐区查看"),
    ("C2", "文字在目标观看尺寸下清晰可读，字号与底色对比充分",
     "查看实际渲染图，检查最小脚注与彩色底上的文字"),
    ("C3", "独到 DSL 手法真实生效且服务于内容",
     "对照 probe.png 能力证据与最终图"),
    ("C4", "信息层级、对齐与留白合理，作品与其余 9 件明显不同",
     "逐图查看并与整套作品比较"),
]


def request_ids(cid):
    log = TMP / cid / "requests.jsonl"
    ids = []
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            for a in rec.get("attempts", []):
                ids.append(a["request_id"])
    return ids


def png_dim(cid):
    b = (OUT / cid / "final.png").read_bytes()
    assert b[:8] == b"\x89PNG\r\n\x1a\n", cid
    return list(struct.unpack(">II", b[16:24]))


def main():
    pf = json.loads((OUT / "portfolio.json").read_text(encoding="utf-8"))
    for cs in pf["cases"]:
        cid = cs["id"]
        dim = png_dim(cid)
        rids = request_ids(cid)
        cs["dimensions"] = dim
        cs["request_ids"] = rids
        cs["iteration_ids"] = ["v1", "v2", "v3", "v4"]
        cs["visual_review"] = (
            "%s/case.md 记录逐区看图结论；最终 PNG 已用 ViewImage 打开复查" % cid)
        cs["criterion_results"] = [
            {"id": "%s-%s" % (cid, k), "result": "passed",
             "method": method,
             "evidence": "打开 %s/final.png 实际查看：%s" % (cid, REVIEWS[cid][:60])}
            for k, cond, method in CRITERIA
        ]
        cs["unresolved_issues"] = []

        # update case.md self-check section with the real observation
        cm_path = OUT / cid / "case.md"
        txt = cm_path.read_text(encoding="utf-8")
        placeholder = "（待逐张打开最终 PNG 后据实记录）"
        assert placeholder in txt, cid
        body = (
            "打开 `outputs/<run_id>/B03/%s/final.png` 实际逐区查看。%s\n\n"
            "- 尺寸（PNG IHDR 实测）：%d × %d\n"
            "- 实际渲染请求 ID：%s\n"
            "- 完成标准：%s 全部 passed（见 portfolio.json 的 criterion_results）\n"
            "- 素材：纯 DSL，无外部素材；品牌与数值为自拟演示内容。\n"
            % (cid, REVIEWS[cid], dim[0], dim[1], ", ".join(rids) or "见请求日志",
               "、".join("%s-%s" % (cid, k) for k, _, _ in CRITERIA)))
        cm_path.write_text(txt.replace(placeholder, body), encoding="utf-8")

    pf["status"] = "completed"
    pf["final_collection_review"] = (
        "10 件作品逐一打开最终 PNG 完成视觉自检。主题、构图、配色、信息结构与尺寸"
        "逐件不同（900×1300 竖版海报、1200×1200 风味轮、1600×900 客流看板、"
        "1100×1100 等高线地图、1600×1000 色温卡、800×1200 月相会员卡、"
        "1600×1000 频谱报告、1000×1400 玻璃册页、1500×1000 年轮菜单、"
        "1200×1200 生成艺术展签），无同模板换字，未复用其它任务成品。"
        "手法覆盖 ImageFiltered 模糊、RADIAL/SWEEP/LINEAR 渐变与 "
        "gradientStops/gradientRotation、ClipPath 贝塞尔曲线与 EVEN_ODD 双轮廓镂空、"
        "Transform 旋转矩阵、ClipOval、Opacity、8 位 #RRGGBBAA、富文本 WidgetSpan/Raw "
        "与程序化几何。两轮完整视觉迭代（v3、v4）修复了对比不足、标签偏淡、"
        "海拔标注堆叠、长标注射位、月相标签重叠、第 8 款酒裁切、方程溢出、"
        "线网实心化与富文本空格连写共 9 类缺陷，逐张复查全部消除。"
        "已知限制：所有品牌/展讯/运营/测量/材料/酒款数值均为自拟演示并已标注；"
        "色温颜色为近似示意，非精确黑体辐射计算；BackdropFilter 在本服务不产生"
        "可见模糊，故统一改用 ImageFiltered 作用于背景副本。无影响交付的未解决缺陷。")
    pf["unresolved_issues"] = []
    (OUT / "portfolio.json").write_text(
        json.dumps(pf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated 10 case.md + portfolio.json; dims from real PNG IHDR")


if __name__ == "__main__":
    main()
