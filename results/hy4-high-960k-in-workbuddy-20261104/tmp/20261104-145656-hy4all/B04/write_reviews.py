#!/usr/bin/env python3
"""Write B04 per-case visual-review conclusions and finalize portfolio.json.

Runs after all 10 final PNGs were opened with ViewImage. Dimensions come from
the real PNG IHDR; request ids from the real per-case request logs.
"""
import json
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.environ["TOOLS"])
import suite

T = "B04"
OUT = suite.out_dir(T)
TMP = suite.tmp_dir(T)

REVIEWS = {
    "case-01": (
        "首版即达标。逐区查看：左侧 RADIAL 渐变太阳与 ImageFiltered 模糊光晕、"
        "4 条椭圆轨道、8 个示意行星圆点（图中明确标注「封面行星大小为示意」）、"
        "右侧大标题「八颗行星」/「尺度的读本」、英文名、三行导语（29 / 78 / 680 倍）、"
        "两列 10 章目录、资料基础卡与两行来源脚注全部完整，"
        "目录两列不挤压、无裁切或遮挡。通过。"),
    "case-02": (
        "首版即达标。逐区查看：8 行共用同一线性比例的直径条（木星最长、水星最短）、"
        "左侧中文名/英文名/km 数值、右侧 ×地球 倍数 0.38–11.21、"
        "结论「29.3 倍 / 11.2 倍」与编辑计算脚注完整；"
        "条形末端数值未与右侧倍数列重叠，数值与研究存档一致。通过。"),
    "case-03": (
        "v1 首版对数轴下方一排 AU 小标签与刻度说明文字重叠（且 10/100/1,000/10,000 刻度、"
        "AU 标签、说明三层挤在一起）；v3 删除重复的轴下 AU 标签（下方 8 行矩阵已给出 AU），"
        "改为单行说明并上移，重叠消除。最终逐区查看：线性轴如实呈现内四颗挤在最左 5%、"
        "对数轴均匀拉开、8 行距日与 AU 矩阵、78.0 倍结论、半长轴口径脚注完整可读。通过。"),
    "case-04": (
        "v1 数据校验发现底部结论「679 个水星年」是截断（精确 59,800 ÷ 88.0 = 679.5），"
        "verify_data.py 报 1 项 FAIL；v2 改为「约 680 个水星年（59,800 ÷ 88.0 ≈ 679.5）」"
        "并同步更新 sources.json 的 C09，重渲染后复查正确，data-check 17 项全部通过。"
        "最终逐区查看：8 行对数渐变条、10^1–10^5 网格、天数与 ≈地球年双标注、"
        "163.7 地球年结论与编辑计算脚注完整。通过。"),
    "case-05": (
        "首版即达标。逐区查看：4 列表头、8 行自转周期与太阳日数值、"
        "金星 −5,832.5 h 与天王星 −17.2 h 的红色「↺ 逆行 retrograde」标签、"
        "水星太阳日 4,222.6 h 与 175.94 ×、相对 24 h 列、"
        "结论与两行 S2 字段口径脚注全部完整可读，标签与数值无冲突。通过。"),
    "case-06": (
        "首版即达标（生成前已把重力条右移，避免与密度数值标签重叠）。逐区查看："
        "8 行内/外行星分组标签、密度条 3,934–5,514 与 687–1,638、重力条 3.7–23.1 及数值、"
        "土星 687 kg/m³ 低于水 1,000 kg/m³ 的常识对照（已明确标注为编辑说明、非来源结论）、"
        "两行口径脚注完整；密度数值与重力条无重叠。通过。"),
    "case-07": (
        "v1 首版色带 0°C 刻度误显示为「+0」；v3 改为「0」。最终逐区查看："
        "−200 → +500 °C 九段渐变色带、8 个定位圆点、8 张温度卡片（金星 +464 到海王星 −200）、"
        "引导线与读图要点 3 条（最热是金星而非水星 / 平均温度口径 / 色带定位公式）完整。"
        "天王星 −195 与海王星 −200 在左端相近是真实数据所致，引导线颜色很淡不影响对应。通过。"),
    "case-08": (
        "首版即达标。逐区查看：8 行卫星条 0/0/1/2/95/274/28/16（前两颗标「无」）、"
        "后四颗椭圆环图标、磁场绿点与「无全球磁场」文字、"
        "内 3 颗 / 外 413 颗结论、IAU 确认数与 2025-03-18 快照口径脚注完整。"
        "地球与火星的细条是 0–274 线性刻度下的真实表现，未夸大。通过。"),
    "case-09": (
        "首版即达标。逐区查看：双栏内行星（水/金/地/火）与外行星（木/土/天/海）"
        "各 4 颗的直径/密度/卫星/均温/环信息、五维交叉对照表（范围与合计均与 S1 数值一致）、"
        "底部三行（S3 分类依据、S2 与 S3 的 terrestrial 定义差异、编辑归纳声明）完整可读，"
        "双栏无溢出、表格无重叠裁切。通过。"),
    "case-10": (
        "首版即达标。逐区查看：浅底 9 列 8 行总表全部数值完整对齐（尺寸 1600×1200）、"
        "交替行底有助于阅读、5 条口径与限制脚注、"
        "3 行实际来源（S1/S2/S3 含 URL 与日期，S3 如实记 null）与末行说明完整；"
        "长 URL 未被裁切，浅底深字对比充分，数值与 data-check.json 全部一致。通过。"),
}

CRITERIA = [
    ("C1", "所有数值取自 S1/S2/S3 且未改动，编辑计算已标注",
     "对照 research/nasa-facts.json、data-check.json 与图中文字"),
    ("C2", "图表刻度/单位/分母/换算正确，图示未夸大事实",
     "复核 datasets 公式与 sources.json 的 claims"),
    ("C3", "作品完整、文字可读、无裁切遮挡",
     "打开最终 PNG 逐区查看"),
    ("C4", "与其余 9 件构成连贯阅读关系且信息结构不同",
     "整套作品逐图比较与 editorial-note.md 核对"),
]


def request_ids(cid):
    log = TMP / cid / "requests.jsonl"
    ids = []
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            if line.strip():
                for a in json.loads(line).get("attempts", []):
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
        dim, rids = png_dim(cid), request_ids(cid)
        cs["dimensions"] = dim
        cs["request_ids"] = rids
        cs["iteration_ids"] = ["v1", "v2", "v3"]
        cs["visual_review"] = (
            "%s/case.md 记录逐区看图结论；最终 PNG 已用 ViewImage 打开复查" % cid)
        cs["criterion_results"] = [
            {"id": "%s-%s" % (cid, k), "result": "passed", "method": method,
             "evidence": "打开 %s/final.png 实际查看 + data-check.json 17 项全通过；%s"
                         % (cid, REVIEWS[cid][:56])}
            for k, cond, method in CRITERIA
        ]
        cs["unresolved_issues"] = []

        cm_path = OUT / cid / "case.md"
        txt = cm_path.read_text(encoding="utf-8")
        placeholder = "（待逐张打开最终 PNG 后据实记录）"
        assert placeholder in txt, cid
        body = (
            "打开 `outputs/<run_id>/B04/%s/final.png` 实际逐区查看。%s\n\n"
            "- 尺寸（PNG IHDR 实测）：%d × %d\n"
            "- 实际渲染请求 ID：%s\n"
            "- 关联 claim_id：%s（逐条定位见 sources.json）\n"
            "- 完成标准：%s 全部 passed（见 portfolio.json 的 criterion_results）\n"
            "- 数据一致性：verify_data.py 从研究存档复算 17 项全部通过，"
            "图中数值未被改动；编辑计算与来源观点已分别标注。\n"
            % (cid, REVIEWS[cid], dim[0], dim[1], ", ".join(rids) or "见请求日志",
               ", ".join(cs["claim_ids"]),
               "、".join("%s-%s" % (cid, k) for k, _, _ in CRITERIA)))
        cm_path.write_text(txt.replace(placeholder, body), encoding="utf-8")

    pf["status"] = "completed"
    pf["final_collection_review"] = (
        "10 件作品逐一打开最终 PNG 完成视觉自检，构成一条连贯阅读路线："
        "封面提问 → 大小（线性比例）→ 距离（线性/对数双轴）→ 一年（对数条）→ "
        "一天（双列区分自转与太阳日）→ 引力与密度（双组条）→ 温度（热力色带）→ "
        "卫星与环（条+图标）→ 分类（双栏与交叉表）→ 总表与来源（浅底密集表）。"
        "信息结构逐件更换，配色统一为深空底 + 行星主题色，仅总表改用浅底便于核查，"
        "属于编辑意图而非风格不一致。事实、来源观点、自行解释与演示明确区分："
        "所有数值直接来自 S1 表（排除 Moon/Pluto 列），口径来自 S2，分类来自 S3；"
        "倍数、AU、地球年、对数映射与求和均标为编辑计算；仅封面行星圆点为示意并已标注。"
        "sources.json 含 3 个实际读取来源、28 条 claim（逐条定位到表格行×列或原文）、"
        "7 个数据集、5 项不确定与 10 件作品的覆盖核对；editorial-note.md 记录主题选择、"
        "读者问题、叙述路线与限制。verify_data.py 从研究存档复算 17 项全部通过。"
        "两轮修复（v2 数据准确性、v3 视觉）消除了 case-04 数值截断、case-03 AU 标签重叠、"
        "case-07「+0」刻度三处缺陷并逐张复查。已知限制（S3 无确认日期、四颗巨行星表面气压 "
        "Unknown 未收录、卫星数为时点快照、S2/S3 口径差异、平均温度不代表局部）"
        "均已在 sources.json 的 uncertainties 与图中脚注如实标注，无影响交付的未解决缺陷。")
    pf["unresolved_issues"] = []
    (OUT / "portfolio.json").write_text(
        json.dumps(pf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated 10 case.md + portfolio.json for B04")


if __name__ == "__main__":
    main()
