#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B04 · 用例元数据（供 b04_finish.py 生成 case.md / portfolio / metrics）。"""

RUN_ID = "run-20261013-174209"

# FINAL_VER：每件最终 DSL 版本；ALL_VER：全部版本链
FINAL_VER = {
    "case-01": "v04", "case-02": "v01", "case-03": "v02", "case-04": "v01",
    "case-05": "v01", "case-06": "v01", "case-07": "v01", "case-08": "v01",
    "case-09": "v01", "case-10": "v02", "case-11": "v02",
}
ALL_VER = {
    "case-01": ["v01", "v02", "v03", "v04"],
    "case-02": ["v01"], "case-03": ["v01", "v02"], "case-04": ["v01"],
    "case-05": ["v01"], "case-06": ["v01"], "case-07": ["v01"],
    "case-08": ["v01"], "case-09": ["v01"], "case-10": ["v01", "v02"],
    "case-11": ["v01", "v02"],
}

CASES = {
    "case-01": {
        "title": "特辑总览：三层十属垂直剖面",
        "canvas": "1920×1080（16:9）",
        "audience": "想「看懂天上那片云」的普通人；给孩子讲天的家长",
        "scenario": "特辑开篇总览——郊游/通勤时抬头对照的第一张图",
        "goal": "把 WMO 十属分类系统转化为一次从地面爬到对流层顶的垂直阅读",
        "technique": "分层天空渐变 + 高度轴 + 十枚云属芯片（各族插画）",
        "visual": "深蓝天空纵剖，高/中/低三族色带 + 积雨云塔贯穿三层",
        "basis": "S1 WMO ICA 表 6 三层高度；S4 CIMO 表 15-1 十属云底常用范围；"
                 "S3 WMO 2017 跨层例外；S5 NOAA 高中低分组",
        "criteria": [
            ("C-1", "十属全部在场且分层正确（高 3/中 3/低 4）",
             "met", "看图：高云族 Ci/Cc/Cs 三芯片（6–12 km）、中云族 Ac/As/Ns 三芯片（2–6 km 或地表–3 km）、低云族 St/Sc/Cu/Cb 四芯片（0.3–1.35 / 0.3–1.5 / 0.6–1.5 km），与 CIMO 表一致"),
            ("C-2", "每芯片云底高度为 CIMO 常用范围（温带）",
             "met", "像素核对：10 枚芯片云底数字与 notes §2.2 表逐行一致（Sc 0.3–1.35 km、Cu 0.3–1.5 km、Cb 0.6–1.5 km）"),
            ("C-3", "图标与文字不重叠、芯片内可读",
             "met", "v04 重构低云芯片为 130px 加高版式（图标区 y+8..y+58）后，实测积云团墨迹止于文字行上方"),
        ],
        "rounds": "v01 初版 → v02 层级标签移入色带左缘、芯片右移 → v03 修三处图标缺陷（晕圈越界/雨丝越线/积雨云砧顶压扁）→ v04 低云芯片加高重构",
        "views": ["z01-view.png v01 整图", "z01-right.png 积雨云塔", "z01-low.png 低云带",
                  "z01-high.png 高云芯片", "z01-b-high.png v02 高云芯片", "z01-b-low.png v02 低云芯片",
                  "z01-b-labels.png v02 层级标签", "z01-b-cu.png 积云/积雨云芯片",
                  "z01-b-cs.png 卷层云芯片", "z01-c-low.png v03 低云芯片",
                  "z01-c-mid.png v03 中云芯片", "z01-d-low.png v04 低云芯片",
                  "z01-d-full.png v04 整图"],
    },
    "case-02": {
        "title": "观测三步法：一指量天",
        "canvas": "1080×1440（3:4）",
        "audience": "初学者——第一次想认真认云的人",
        "scenario": "方法图：抬手一指判定云属的三步流程",
        "goal": "把「一指量天」（视宽判属）变成可执行的三步动作",
        "technique": "浅色判定流图 + 手指比例图示 + 分支卡片",
        "visual": "暖白纸面 + 赭朱强调 + 手势示意（小指/一指/三指）",
        "basis": "S5 NOAA JetStream 视宽判据（Cc <1°、Ac 1–5°、Sc >5°）；"
                 "S6 HKO 30° 地平规则；S4 CIMO 表（跨属核高度）",
        "criteria": [
            ("C-1", "三步流程完整且每步有来源判据",
             "met", "看图：①量视宽（小指 ＜1° → Cc 候选；一指 1–5° → Ac 候选；三指 ＞5° → Sc 候选）②看高度（对照 CIMO 云底范围）③核高度与云底；判据全部引自 NOAA/HKO"),
            ("C-2", "角度符号用全角，无实体泄漏",
             "met", "dsl：case-02 文本 ＜/＞ 均为全角 U+FF1C/U+FF1E，实体计数 0"),
        ],
        "rounds": "v01 首渲一次成功（含全角符号预防性修复）",
        "views": ["z02-view.png 整图"],
    },
    "case-03": {
        "title": "卷云 Cirrus (Ci) 图鉴页",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴读者——抬头见到丝缕状云想确认属名的人",
        "scenario": "图鉴页 1/10：高云族首属",
        "goal": "辨认卷云四质地（fibratus/uncinus/spissatus/intortus）并读其天气含义",
        "technique": "天空剖面 + 质地变体曲线 + 高度轴范围带",
        "visual": "暖纸面 + 天空蓝主图 + 赭朱数据条",
        "basis": "S2 WMO ICA 卷云页（定义逐字）；S4 CIMO 表（6–12 km/20 000–40 000 ft）；"
                 "S5 NOAA（染色与透明性）；S6 HKO（种 4/变种 4/附属 1）",
        "criteria": [
            ("C-1", "定义与种/变种清单逐字引自来源",
             "met", "图中 ICA 三栏：种 fibratus/uncinus/spissatus/castellanus、变种 intortus/radiatus/vertebratus/duplicatus、附属 mamma——与 HKO 电子书逐字一致；定义引 NOAA 原文"),
            ("C-2", "无无源表述",
             "met", "v02 剔除「钩指向上方风切变方向」等两条无来源 elaboration，改为 ICA 正式形态描述（uncinus）与 CIMO 表注"),
        ],
        "rounds": "v01 初版 → v02 数据纪律修复（剔除无源表述）",
        "views": ["z03-full.png 整图"],
    },
    "case-04": {
        "title": "卷积云 Cirrocumulus (Cc) 图鉴页",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴读者——见到颗粒/波纹状薄云想确认的人",
        "scenario": "图鉴页 2/10：高云族次属",
        "goal": "辨认卷积云的鱼鳞天排列，理解「视宽 ＜1°」这一硬判据",
        "technique": "嵌合颗粒阵列 + 1° 视宽标尺 + 高度轴范围带",
        "visual": "同族版式 + 高密度小颗粒阵列插画",
        "basis": "S2 WMO ICA 卷积云页；S4 CIMO 表（6–12 km）；S5 NOAA（视宽 ＜1°、寿命短）；"
                 "S6 HKO（种 4/变种 2/附属 2）",
        "criteria": [
            ("C-1", "视宽判据数值正确（＜1°）",
             "met", "数据卡与判别条均标 ＜1°（小指）；与 NOAA/HKO 一致"),
            ("C-2", "与 Ac/Sc 的视宽区分明示",
             "met", "30 秒判别条：＜1° → 卷积云；1–5° → 高积云；＞5° → 层积云"),
        ],
        "rounds": "v01 首渲一次成功（含全角符号预防性修复）",
        "views": ["z04-view.png 整图"],
    },
    "case-05": {
        "title": "卷层云 Cirrostratus (Cs) 图鉴页（含 22° 晕几何）",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴读者——见过日晕想知道那片云是什么的人",
        "scenario": "图鉴页 3/10：高云族末属 + 光学现象专页",
        "goal": "用 22° 晕反推卷层云在场，并解释晕的几何成因",
        "technique": "晕圈几何图解（太阳 + 22° 环 + 入射/折射路径）+ 高度轴范围带",
        "visual": "同族版式 + 日晕几何图示",
        "basis": "S2 WMO ICA 卷层云页（晕为在场证据）；S4 CIMO 表（6–12 km）；"
                 "S7 NWS/Meteo.es/Wikipedia 22° 晕（最小偏向角 22°，冰晶六棱柱折射）",
        "criteria": [
            ("C-1", "22° 晕角度与成因有三来源支撑",
             "met", "几何图标 22° 环 + 入射/折射光线；成因注记「六角冰晶最小偏向角约 22°」——NWS、Meteo.es、Wikipedia 三源一致"),
            ("C-2", "晕与霾/薄层云的区分有据",
             "met", "观测提示：「卷层云见晕、无色偏；霾带黄或褐色」（HKO）"),
        ],
        "rounds": "v01 首渲一次成功（含全角符号预防性修复）",
        "views": ["z05-view.png 整图"],
    },
    "case-06": {
        "title": "高积云 Altocumulus (Ac) 图鉴页",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴读者——见到成排云块/瓦片想确认的人",
        "scenario": "图鉴页 4/10：中云族首属",
        "goal": "辨认高积云的成排云块与华（corona）现象，理解 1–5° 判据",
        "technique": "成排圆块阵列 + 华环小图 + 高度轴范围带",
        "visual": "同族版式 + 规则云块阵列",
        "basis": "S2 WMO ICA 高积云页；S4 CIMO 表（2–6 km/6 500–20 000 ft，与 As 共用合并单元格）；"
                 "S5 NOAA（视宽 1–5°、corona 外红内蓝）；S6 HKO（种 4/变种 7/附属 2）",
        "criteria": [
            ("C-1", "视宽判据 1–5° 与 corona 描述有据",
             "met", "数据卡与 corona 小图注记均引自 NOAA；华环「外红内蓝」按 NOAA 原文"),
            ("C-2", "与 Cc/Sc 的区分规则完整",
             "met", "30 秒判别：＜1° 无阴影 → Cc；1–5° → Ac；＞5° 且高于地平 30° → Sc"),
        ],
        "rounds": "v01 首渲一次成功（含全角符号预防性修复）",
        "views": ["z06-view.png 整图"],
    },
    "case-07": {
        "title": "高层云 Altostratus (As) 图鉴页",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴 reader——日月隔毛玻璃可见的人",
        "scenario": "图鉴页 5/10：中云族次属",
        "goal": "辨认高层云的磨砂日面与无晕无影特征，区分 As/Ns",
        "technique": "磨砂玻璃日面示意 + 灰幕剖面 + 高度轴范围带",
        "visual": "同族版式 + 毛玻璃质感日面",
        "basis": "S2 WMO ICA 高层云页；S4 CIMO 表（2–6 km，可发展成雨层云注）；"
                 "S5 NOAA（毛玻璃日面、无晕无影）；S6 HKO（无种、变种 5、附属 5、夜间惯例）",
        "criteria": [
            ("C-1", "「无晕无影、日月轮廓可辨」判据有据",
             "met", "主图磨砂日面 + 观测提示均引 NOAA/HKO 原文"),
            ("C-2", "As/Ns 判别规则（日月轮廓 + 降水）完整",
             "met", "30 秒判别与数据卡：轮廓可辨 → As；蔽天且持续降水 → Ns"),
        ],
        "rounds": "v01 首渲一次成功",
        "views": ["z07-view.png 整图"],
    },
    "case-08": {
        "title": "雨层云 Nimbostratus (Ns) 图鉴页",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴读者——阴雨连绵时想知道云名的人",
        "scenario": "图鉴页 6/10：中云族末属",
        "goal": "辨认雨层云的连续降水幕与碎雨云，理解其贯穿三层的例外地位",
        "technique": "暗灰雨幕 + 连续降水幡阵列 + 蔽日示意 + 高度轴范围带",
        "visual": "同族版式 + 最暗主图（降水主题）",
        "basis": "S2 WMO ICA 雨层云页；S4 CIMO 表（地表–3 000 m/地表–10 000 ft，天气图视为中云）；"
                 "S5 NOAA（As 增厚而来、云底随降水降低）；S6 HKO（无种无变种、附属 3、以降水区分）",
        "criteria": [
            ("C-1", "云底高度与 CIMO 表一致（地表–3 km）",
             "met", "数据卡与范围带均地表–3 km/地表–10 000 ft；与 notes §2.2 一致"),
            ("C-2", "Ns/St 以降水区分的规则有据",
             "met", "数据卡与 30 秒判别均引 HKO「以是否产生降水区分」"),
        ],
        "rounds": "v01 首渲一次成功",
        "views": ["z08-view.png 整图"],
    },
    "case-09": {
        "title": "层积云 Stratocumulus (Sc) 图鉴页",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴读者——见到蜂窝状云块想确认的人",
        "scenario": "图鉴页 7/10：低云族次属",
        "goal": "辨认层积云的蜂窝排列与 30° 判别规则",
        "technique": "蜂窝嵌合阵列（暗底亮顶）+ 30° 仰角扇区图示 + 高度轴范围带",
        "visual": "同族版式 + 蜂窝 tessellation 插画",
        "basis": "S2 WMO ICA 层积云页；S4 CIMO 表（0.3–1.35 km/1 000–4 500 ft；更宽 0.3–2 km）；"
                 "S5 NOAA（视宽 ＞5°）；S6 HKO（30° 规则、种 4/变种 7/附属 3）",
        "criteria": [
            ("C-1", "云底高度与 CIMO 表一致（0.3–1.35 km）",
             "met", "数据卡：常用 0.3–1.35 km（1 000–4 500 ft）、更宽 0.3–2 km（1 000–6 500 ft）——与 notes §2.2 逐行一致"),
            ("C-2", "30° 判别图示准确",
             "met", "主图右上：地平线 + 30° 仰角扇区 + 云块位置，与 HKO 规则一致"),
        ],
        "rounds": "v01 首渲一次成功（含全角符号预防性修复）",
        "views": ["z09-view.png 整图"],
    },
    "case-10": {
        "title": "层云 Stratus (St) 图鉴页",
        "canvas": "1080×1350（4:5）",
        "audience": "图鉴读者——阴天灰幕想确认的人",
        "scenario": "图鉴页 8/10：低云族末属，与 Ns 配对",
        "goal": "辨认层云的均匀灰幕与透日轮廓，与雨层云以降水区分",
        "technique": "层云幕剖面（微起伏底边）+ 碎层云破片 + 透日轮廓 + 毛毛雨",
        "visual": "同族版式 + 均一灰层插画",
        "basis": "S2 WMO ICA 层云页；S4 CIMO 表（地表–600 m/地表–2 000 ft；更宽 地表–1 200 m/地表–4 000 ft）；"
                 "S5 NOAA（均匀底边、可辨日轮）；S6 HKO（种 2/变种 3/附属 1、雾被抬升成云）",
        "criteria": [
            ("C-1", "云底高度与 CIMO 表一致（地表–0.6 km）",
             "met", "v02 修正：v01 误植层积云 ft 上限（地表–2 km/0–6 500 ft）→ v02 改为地表–0.6 km/地表–2 000 ft、更宽 地表–1.2 km（地表–4 000 ft），与 notes §2.2 逐行一致"),
            ("C-2", "St/Ns 判别（以降水区分）有据",
             "met", "数据卡与 30 秒判别均引 HKO"),
        ],
        "rounds": "v01 初版 → v02 数据纪律修复（CIMO 高度误植）",
        "views": ["z10-view.png v01 整图", "z10-view-v02.png v02 整图"],
    },
    "case-11": {
        "title": "积云 → 积雨云 Cumulus/Cumulonimbus 图鉴页（对流塔）",
        "canvas": "1080×1920（9:16）",
        "audience": "图鉴读者——夏季看云长大的所有人",
        "scenario": "图鉴页 9/10（压轴）：对流发展全序列",
        "goal": "沿 humilis→mediocris→congestus→Cb 四阶段读懂对流塔演化与「云的工厂」",
        "technique": "四阶段发展序列 + 砧顶/塔身/降水幡/闪电插画 + 12 km 高度轴",
        "visual": "唯一 9:16 竖幅图鉴页；四阶段横向序列 + 发展箭头",
        "basis": "S2 WMO ICA 积云/积雨云页；S4 CIMO 表（Cu 300–1 500 m、Cb 600–1 500 m；更宽均 300–2 000 m）；"
                 "S5 NOAA（日对流生消、Cb 定义）；S6 HKO（Cu→Cb 演化标志、附属云全清单）",
        "criteria": [
            ("C-1", "四阶段序列与 HKO 演化标志一致",
             "met", "主图四阶段 + 数据卡「穹顶轮廓清晰（水滴）→ 顶部柔软纤维（冰晶）即 Cu→Cb」引 HKO 原文"),
            ("C-2", "Cu/Cb 云底高度与 CIMO 表一致",
             "met", "v02 修正：v01 误写 0.6–2 km → v02 改为 Cu 0.3–1.5 km（1 000–5 000 ft）/ Cb 0.6–1.5 km（2 000–5 000 ft），更宽 0.3–2 km；与 notes §2.2 逐行一致"),
            ("C-3", "附属云清单完整（ICA via HKO）",
             "met", "ICA 清单第三栏：Cu pileus；Cb incus/mamma/virga/praecipitatio/arcus/tuba/pannus/velum"),
        ],
        "rounds": "v01 初版 → v02 数据纪律修复（CIMO 高度误植）",
        "views": ["z11-view.png v01 整图", "z11-view-v02.png v02 整图"],
    },
}

# LAST_OK[(cid)] = (request_id, elapsed_s, dsl_bytes) 由 b04_finish.py 从 requests.jsonl 实取
