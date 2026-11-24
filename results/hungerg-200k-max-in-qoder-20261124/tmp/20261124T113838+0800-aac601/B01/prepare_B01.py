from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as sk
import creativekit as ck

TASK = "B01"
FONT = sk.FONT


def criteria(content: str, geometry: str, minimum: int = 24) -> list[dict]:
    return [
        {"id": "C1-content", "condition": content, "method": "逐件实际查看最终PNG，核对标题、关键信息与行动入口。"},
        {"id": "C2-geometry", "condition": geometry, "method": "实际查看并结合生成参数/比例计算，检查遮挡、裁剪、对齐与数据几何。"},
        {"id": "C3-legibility", "condition": f"目标尺寸下正文不小于{minimum}px，层级清楚，长文案不被截断。", "method": "逐件完整查看；必要时接触表比较；记录真实观察。"},
        {"id": "C4-provenance", "condition": "最终图为真实服务PNG响应，完整DSL与请求匹配。", "method": "核对HTTP日志、响应字节SHA-256、DSL请求体与PNG尺寸。"},
    ]


def cases() -> list[dict]:
    return [
        {"id": "case-01", "title": "光的形状｜美术馆展览海报", "dimensions": [1080, 1440],
         "audience": "城市艺术爱好者与周末观展人群", "use_context": "美术馆入口灯箱、社交媒体竖版海报，1080×1440",
         "user_goal": "快速理解展览主题、时间与地点，并决定预约参观。", "content_basis": "自拟‘叠光美术馆’与演示展览信息；非实际客户作品。",
         "visual_intent": "以巨型橙色日轮、拱门和细小轨道线构成光的容器；深紫背景让标题与日期形成强烈入口。",
         "dsl_capabilities": ["Positioned", "Container", "Text", "圆角", "圆", "线", "透明度"],
         "criteria": criteria("主题、 dates、地点、票价与预约行动完整。", "圆形日轮、拱门和轨道不裁切标题；装饰位于安全区。")},
        {"id": "case-02", "title": "城市热岛｜社区降温决策看板", "dimensions": [1600, 1000],
         "audience": "街道办、社区规划师与公益组织", "use_context": "会议室大屏或打印A3横版，1600×1000",
         "user_goal": "识别最热社区、比较树冠与地表温度，确定优先降温区域。", "content_basis": "自拟城市与演示监测数据；温度单位为°C，仅用于展示决策逻辑。",
         "visual_intent": "抽象街区热力图与右侧诊断面板结合，用同心热斑和树冠缺口直接呈现空间问题。",
         "dsl_capabilities": ["Container", "Text", "圆", "半透明色", "线", "数据比例"], "criteria": criteria("最热社区、温度、树冠率、风险与行动建议一致。", "热斑半径按温度差比例计算；图例和地图边界不重叠。", 22)},
        {"id": "case-03", "title": "月度余额｜个人预算控制台", "dimensions": [1200, 1200],
         "audience": "第一次独立管理月预算的年轻上班族", "use_context": "手机相册、预算App分享卡，1200×1200",
         "user_goal": "一眼看懂本月收入、支出、结余与超支风险。", "content_basis": "虚构11月预算：收入12400，支出9760，结余2640；分类支出合计准确。",
         "visual_intent": "深色财务控制台以大号结余和环形余额读数为核心，分类横条把剩余可支配额落到行动。",
         "dsl_capabilities": ["Text", "圆环", "线性比例条", "圆角", "透明度"], "criteria": criteria("收入、支出、结余、五类支出和储蓄率准确。", "分类横条长度与金额成比例；圆环内外层级清楚。", 24)},
        {"id": "case-04", "title": "番茄罗勒｜20分钟晚餐教学单", "dimensions": [1080, 1440],
         "audience": "下班后希望快速做完两人晚餐的家庭烹饪者", "use_context": "厨房iPad竖屏或打印张贴，1080×1440",
         "user_goal": "按时间顺序完成两人份意面，并避免错过煮面与酱汁火候。", "content_basis": "自拟食谱与演示份量；食材与步骤为创作内容。",
         "visual_intent": "奶油纸色、番茄红与罗勒绿构成餐桌感；圆盘食材图和四步时间轴让操作顺序一眼可扫。",
         "dsl_capabilities": ["Text", "圆", "圆角", "线", "步骤编号"], "criteria": criteria("食材、四人步骤、时间与两人份信息完整。", "步骤编号与时间轴顺序一致；圆盘与食材不遮挡正文。", 26)},
        {"id": "case-05", "title": "港湾线｜城市通勤导览图", "dimensions": [1600, 1000],
         "audience": "首次到访港湾市的游客与通勤者", "use_context": "车站立柱、旅游App横屏，1600×1000",
         "user_goal": "选择机场快线或地铁线路，并找到换乘站与目的地。", "content_basis": "自拟港湾市交通网络；站名、线路和运营提示均为演示。",
         "visual_intent": "高纯度线路色、正交轨道和放大换乘节点构成清晰示意图；底部提供三种出行方案。",
         "dsl_capabilities": ["线", "圆", "Text", "图例", "换乘节点"], "criteria": criteria("三条线路、换乘站、机场快线和出行方案完整。", "轨道不穿越站名；换乘站位于线路真实交点。", 24)},
        {"id": "case-06", "title": "夜航｜独立电子专辑封面", "dimensions": [1200, 1200],
         "audience": "独立电子音乐听众与流媒体收藏者", "use_context": "流媒体专辑封面、实体唱片封套，1200×1200",
         "user_goal": "识别专辑与艺人，理解音乐氛围并找到完整曲目信息。", "content_basis": "自拟艺人‘渡线’与六首曲目；非真实发行。",
         "visual_intent": "酸性橙红底、黑色唱片与斜切几何构成夜晚速度感；超大中文字与小型目录形成唱片封套张力。",
         "dsl_capabilities": ["圆", "rotate", "Text", "边框", "高对比"], "criteria": criteria("艺人、专辑名、六首曲目与发行信息完整。", "唱片圆与斜切几何不遮挡标题；曲目列表可读。", 22)},
        {"id": "case-07", "title": "安全出口｜办公室疏散指引", "dimensions": [1600, 1000],
         "audience": "办公楼访客与物业安全管理员", "use_context": "楼层入口海报、疏散演练 briefing，1600×1000",
         "user_goal": "从当前位置找到两条安全出口，并理解集合点与禁乘电梯规则。", "content_basis": "虚构二层办公平面与疏散路线；非真实建筑合规文件。",
         "visual_intent": "建筑平面、绿色双向疏散路径和红色禁用设施并置，像一张可立即执行的现场地图。",
         "dsl_capabilities": ["矩形平面", "线", "圆", "Text", "路径箭头"], "criteria": criteria("两个出口、两条路线、集合点、当前位置和禁令完整。", "路线连续且不穿墙；房间标签与通道不重叠。", 24)},
        {"id": "case-08", "title": "内太阳系｜科普尺度图", "dimensions": [1600, 1000],
         "audience": "中学生与天文社团成员", "use_context": "课堂投影、科学墙报，1600×1000",
         "user_goal": "比较水星、金星、地球、火星的公转周期与相对轨道顺序。", "content_basis": "公转周期采用常用近似值88/225/365/687天；轨道与行星大小为示意，不按真实比例。",
         "visual_intent": "深空蓝黑背景上的同心轨道、发光色块与行星编号，把时间周期转成可比较的同心结构。",
         "dsl_capabilities": ["圆", "线", "Text", "数据标签", "示意比例"], "criteria": criteria("四行星顺序、周期、距日序号和图例准确。", "同心轨道不穿过标签；明确标注非真实比例。", 24)},
        {"id": "case-09", "title": "周末菜摊｜社区市集价格牌", "dimensions": [1080, 1440],
         "audience": "附近居民与周末市集采购者", "use_context": "摊位黑板、社区群竖版图片，1080×1440",
         "user_goal": "快速查看今日蔬菜价格、单位与售罄状态，决定购买清单。", "content_basis": "自拟‘青禾周末菜摊’和演示价格/库存；非真实商户。",
         "visual_intent": "森林绿黑板、粉笔白字、手绘太阳与蔬菜圆点，保留市集温度同时保证价格 scan 速度。",
         "dsl_capabilities": ["Text", "圆", "线", "价格表", "状态标签"], "criteria": criteria("六种蔬菜的价格、单位、库存状态与摊位时间完整。", "价格列对齐；售罄标记不遮盖品名。", 28)},
        {"id": "case-10", "title": "接口之前｜产品设计大会议程", "dimensions": [1080, 1440],
         "audience": "产品设计师、前端工程师与设计学生", "use_context": "会议预告长图、校园与社区海报，1080×1440",
         "user_goal": "选择适合自己角色的分会场，了解时间地点并完成报名。", "content_basis": "自拟‘接口之前’大会、讲者与议程；非实际活动。",
         "visual_intent": "钴蓝底、荧光黄网格与超大日期构成技术海报；三列议题和时间轴把密集议程变得可扫读。",
         "dsl_capabilities": ["Text", "网格", "圆角", "边框", "议程表"], "criteria": criteria("日期、地点、三场议题、讲者、时间和报名入口完整。", "时间轴与议题列对齐；长讲者名不截断。", 24)},
    ]


def museum() -> str:
    c = [sk.box(0, 0, 1080, 1440, "#24172F"), sk.box(70, 66, 940, 1308, "#321E3E", 22),
         sk.label("叠光美术馆  /  DIEGUANG MUSEUM", 110, 100, 860, 40, 26, "#F6B37A", True),
         sk.label("光的形状", 108, 178, 860, 126, 92, "#FFF4E8", True),
         sk.label("THE SHAPE OF LIGHT", 114, 312, 860, 44, 28, "#D9B8D8"),
         sk.circle(540, 716, 272, "#F06A3B"), sk.circle(540, 716, 202, "#24172F"),
         sk.box(362, 650, 356, 452, "#F6B37A", 178), sk.box(398, 700, 284, 402, "#24172F", 142),
         sk.line(176, 602, 904, 602, "#8B668C", 2), sk.line(176, 1098, 904, 1098, "#8B668C", 2),
         sk.circle(804, 506, 26, "#F6D88A"), sk.circle(246, 918, 16, "#F6D88A"),
         sk.label("2026.12.05 — 2027.02.21", 110, 1150, 860, 48, 34, "#FFF4E8", True),
         sk.label("周二至周日 10:00—18:00  ·  叠光美术馆 2F", 110, 1210, 860, 40, 26, "#D9B8D8"),
         sk.box(110, 1282, 340, 62, "#F6B37A", 12), sk.label("预约参观  →", 134, 1294, 292, 38, 28, "#24172F", True),
         sk.label("学生票 ¥60 / 全票 ¥120", 486, 1298, 484, 36, 24, "#FFF4E8", False, "RIGHT")]
    return sk.snapshot(1080, 1440, c, "#24172F")


def heatmap() -> str:
    c = [sk.box(0, 0, 1600, 1000, "#F2F5F1"), sk.label("CLIMATE LAB  /  城市降温决策", 56, 36, 900, 36, 24, "#18705F", True),
         sk.label("热岛诊断：优先保护西岸树冠缺口", 56, 84, 1120, 60, 44, "#173D36", True),
         sk.label("演示监测 · 2026.08.18 15:00 · °C", 1120, 100, 424, 32, 22, "#587169", False, "RIGHT"),
         sk.box(56, 176, 1000, 744, "#FFFFFF", 18, "#D8E3DC")]
    blocks = [(96, 224, 250, 180, 31.2), (366, 224, 286, 180, 33.8), (672, 224, 334, 180, 35.6),
              (96, 424, 250, 202, 32.6), (366, 424, 286, 202, 36.4), (672, 424, 334, 202, 38.1),
              (96, 646, 250, 214, 33.1), (366, 646, 286, 214, 34.7), (672, 646, 334, 214, 36.9)]
    colors = ["#D7E9C8", "#F1DFA1", "#F4B36E", "#EA7457", "#C94E48"]
    for x, y, w, h, temp in blocks:
        index = min(4, int((temp - 31) // 1.6))
        c += [sk.box(x, y, w, h, colors[index], 10), sk.label(f"{temp:.1f}°", x + 18, y + 18, w - 36, 44, 32, "#FFFFFF" if index >= 3 else "#23473D", True)]
    c += [sk.circle(839, 525, 98, "#C94E4888"), sk.circle(839, 525, 66, "#C94E48AA"),
         sk.label("西岸", 755, 590, 168, 34, 24, "#FFFFFF", True, "CENTER")]
    c += [sk.label("31°", 72, 924, 70, 30, 20, "#587169"), sk.label("38°", 962, 924, 70, 30, 20, "#587169", False, "RIGHT")]
    for index, color in enumerate(colors):
        c.append(sk.box(160 + index * 120, 930, 112, 14, color, 3))
    c += [sk.box(1092, 176, 452, 744, "#173D36", 18), sk.label("优先行动", 1124, 210, 388, 40, 28, "#9DD7B9", True),
         sk.label("西岸社区", 1124, 270, 388, 54, 40, "#FFFFFF", True), sk.label("38.1°C  /  树冠率 12%", 1124, 334, 388, 36, 24, "#CBE4D9"),
         sk.box(1124, 402, 388, 2, "#42675D"), sk.label("与全市均值相比", 1124, 432, 388, 32, 22, "#9FBAB0"),
         sk.label("+4.3°C", 1124, 472, 388, 62, 48, "#F4B36E", True),
         sk.label("① 补植 180 株冠乔木\n② 增设 3 处遮阴棚\n③ 优先修复透水铺装", 1124, 566, 388, 174, 26, "#FFFFFF"),
         sk.box(1124, 794, 388, 86, "#E7F2C4", 12), sk.label("目标：两年内树冠率 ≥ 28%", 1144, 816, 348, 44, 24, "#173D36", True)]
    return sk.snapshot(1600, 1000, c, "#F2F5F1")


def budget() -> str:
    expenses = [("房租", 4200, "#8EA7FF"), ("餐饮", 1860, "#F3A45B"), ("交通", 720, "#60C6B0"), ("学习", 900, "#D883B5"), ("其他", 2080, "#8D99AD")]
    c = [sk.box(0, 0, 1200, 1200, "#111C2E"), sk.label("余额实验室  /  NOVEMBER", 64, 48, 1072, 38, 24, "#8EA7FF", True),
         sk.label("这个月，钱去了哪里？", 64, 104, 1072, 64, 48, "#F4F7FF", True),
         sk.circle(330, 410, 180, "#263651"), sk.circle(330, 410, 128, "#111C2E"),
         sk.label("可结余", 206, 342, 248, 34, 24, "#AAB8CF", False, "CENTER"),
         sk.label("¥2,640", 182, 386, 296, 64, 48, "#60C6B0", True, "CENTER"),
         sk.label("储蓄率 21.3%", 202, 460, 256, 34, 24, "#F4F7FF", False, "CENTER"),
         sk.label("收入 ¥12,400", 610, 278, 480, 44, 30, "#F4F7FF", True),
         sk.label("支出 ¥9,760", 610, 334, 480, 40, 28, "#F3A45B", True),
         sk.box(610, 402, 480, 2, "#3A4B65")]
    for index, (name, value, color) in enumerate(expenses):
        y = 442 + index * 68
        c += [sk.label(name, 610, y, 90, 32, 24, "#C9D4E5"), sk.box(710, y + 6, 280, 20, "#263651", 6),
              sk.box(710, y + 6, 280 * value / 4200, 20, color, 6), sk.label(f"¥{value:,}", 1004, y, 86, 32, 22, "#F4F7FF", True, "RIGHT")]
    c += [sk.box(64, 806, 1072, 272, "#1C2B43", 18), sk.label("本周可支配额", 96, 838, 420, 38, 26, "#8EA7FF", True),
         sk.label("¥600", 96, 890, 420, 72, 56, "#F4F7FF", True),
         sk.label("按剩余 4 周分配；已预留 ¥240 弹性支出。", 96, 980, 620, 36, 24, "#AAB8CF"),
         sk.box(756, 850, 336, 174, "#60C6B0", 16), sk.label("保持结余率", 780, 874, 288, 36, 24, "#12342F", True, "CENTER"),
         sk.label("≥ 20%", 780, 924, 288, 58, 42, "#12342F", True, "CENTER")]
    return sk.snapshot(1200, 1200, c, "#111C2E")


def recipe() -> str:
    c = [sk.box(0, 0, 1080, 1440, "#F7F0DF"), sk.label("下班后厨房  /  20 MIN DINNER", 64, 52, 952, 36, 24, "#B74732", True),
         sk.label("番茄罗勒意面", 62, 112, 950, 88, 66, "#283D32", True),
         sk.label("两人份 · 一口锅 · 20 分钟", 66, 214, 940, 40, 28, "#6E7E68"),
         sk.circle(540, 526, 242, "#FFFFFF", "#D7CDB8"), sk.circle(540, 526, 202, "#F3E7CE"),
         sk.circle(454, 478, 54, "#D9543F"), sk.circle(586, 454, 48, "#E47A4C"), sk.circle(632, 552, 58, "#C84435"),
         sk.circle(430, 596, 42, "#E47A4C"), sk.box(512, 540, 118, 24, "#E9C46A", 12),
         sk.box(490, 454, 34, 86, "#3F7A4D", 17), sk.box(570, 580, 74, 30, "#4B8B55", 15),
         sk.label("食材", 66, 830, 180, 40, 30, "#B74732", True),
         sk.label("意面 180g  ·  番茄 4 个  ·  罗勒 1 把\n蒜 2 瓣  ·  橄榄油 2 汤匙  ·  盐适量", 66, 882, 948, 90, 28, "#283D32")]
    steps = [("01", "0—8 分钟", "煮面：水沸后加盐，意面煮至弹牙。"),
             ("02", "8—13 分钟", "炒酱：蒜末、番茄块与橄榄油中小火收汁。"),
             ("03", "13—17 分钟", "合锅：加入意面与半碗面汤，翻拌挂汁。"),
             ("04", "17—20 分钟", "装盘：撕罗勒、磨黑胡椒，立即上桌。")]
    for index, (num, time, text) in enumerate(steps):
        y = 1012 + index * 88
        c += [sk.circle(94, y + 28, 28, "#B74732"), sk.label(num, 68, y + 10, 52, 36, 22, "#FFFFFF", True, "CENTER"),
              sk.label(time, 146, y, 188, 36, 24, "#B74732", True), sk.label(text, 346, y, 668, 60, 26, "#283D32")]
    return sk.snapshot(1080, 1440, c, "#F7F0DF")


def transit() -> str:
    c = [sk.box(0, 0, 1600, 1000, "#F8F7F2"), sk.label("HARBOR CITY  /  港湾市", 56, 40, 800, 36, 24, "#27364A", True),
         sk.label("一张图，找到你的目的地", 56, 90, 1100, 60, 46, "#172538", True),
         sk.label("机场快线 06:00—23:00\n地铁 05:30—00:30", 1150, 82, 390, 80, 20, "#667386", False, "RIGHT"),
         sk.box(56, 184, 1488, 554, "#FFFFFF", 18, "#DEE3E8")]
    blue, orange, green = "#246BCE", "#EE6B3A", "#16936F"
    c += [sk.line(154, 308, 1370, 308, blue, 14), sk.line(360, 264, 360, 638, orange, 14),
         sk.line(154, 520, 1180, 520, green, 14), sk.line(1180, 520, 1180, 308, green, 14),
         sk.line(154, 638, 1370, 638, blue, 14)]
    stations = [(154, 308, "西港"), (440, 308, "博物馆"), (360, 264, "机场"), (360, 308, "中央"),
                (360, 420, "市政厅"), (360, 520, " interchange"), (700, 308, "大学城"), (1000, 308, "东站"), (1370, 308, "海湾"),
                (154, 520, "花园"), (580, 520, "市场"), (840, 520, "科技园"), (1180, 520, "河东"),
                (154, 638, "南门"), (540, 638, "剧院"), (920, 638, "新城"), (1370, 638, "机场南")]
    for x, y, name in stations:
        c.append(sk.circle(x, y, 14, "#FFFFFF", "#27364A"))
        if name == "interchange":
            continue
        offset_x = -76 if x in (154, 360, 1180) else -54
        offset_y = -48 if y in (308, 638) else 22
        if x == 360 and y == 264:
            offset_y = -58
        if x == 360 and y == 308:
            offset_y = 24
        c.append(sk.label(name, x + offset_x, y + offset_y, 152, 34, 22, "#27364A", True, "CENTER"))
    c += [sk.circle(360, 420, 24, "#FFFFFF", "#EE6B3A"), sk.circle(360, 520, 24, "#FFFFFF", "#16936F"),
         sk.label("中央换乘", 400, 336, 180, 34, 24, "#EE6B3A", True),
         sk.label("绿线换乘", 398, 488, 180, 34, 24, "#16936F", True)]
    c += [sk.label("出行方案", 56, 780, 240, 40, 28, "#172538", True)]
    plans = [("机场 → 市中心", "机场快线直达中央，约 28 分钟", orange), ("中央 → 大学城", "蓝线向东 4 站，约 16 分钟", blue), ("中央 → 科技园", "绿线向东 3 站，约 12 分钟", green)]
    for index, (title, text, color) in enumerate(plans):
        x = 56 + index * 504
        c += [sk.box(x, 834, 480, 112, "#FFFFFF", 14, "#DEE3E8"), sk.box(x, 834, 10, 112, color, 5),
              sk.label(title, x + 28, 850, 424, 34, 26, color, True), sk.label(text, x + 28, 896, 424, 34, 22, "#667386")]
    return sk.snapshot(1600, 1000, c, "#F8F7F2")


def album() -> str:
    c = [sk.box(0, 0, 1200, 1200, "#F04E35"), sk.label("渡线  /  FERRYLINE", 64, 54, 760, 38, 24, "#241C1B", True),
         sk.label("夜航", 58, 118, 650, 150, 122, "#241C1B", True),
         sk.label("NIGHT FERRY", 68, 282, 620, 46, 30, "#FFE7C2", True),
         sk.circle(810, 596, 360, "#241C1B"), sk.circle(810, 596, 126, "#F04E35"), sk.circle(810, 596, 26, "#241C1B"),
         sk.circle(810, 596, 224, "#F04E3533"), sk.circle(810, 596, 286, "#F04E3522"),
         sk.box(608, 238, 410, 44, "#FFE7C2", 4), sk.box(1018, 822, 110, 280, "#FFE7C2", 4),
         sk.label("六首夜间航行", 66, 826, 440, 36, 24, "#241C1B", True)]
    tracks = ["01  离岸信号", "02  雾中灯塔", "03  潮汐电台", "04  无人甲板", "05  凌晨四点半", "06  返航"]
    for index, track in enumerate(tracks):
        c.append(sk.label(track, 66, 876 + index * 42, 460, 32, 22, "#241C1B"))
    c += [sk.label("STEREO  /  06 TRACKS  /  2026", 616, 1118, 520, 32, 20, "#241C1B", True, "RIGHT")]
    return sk.snapshot(1200, 1200, c, "#F04E35")


def evacuation() -> str:
    c = [sk.box(0, 0, 1600, 1000, "#EEF2EF"), sk.label("SAFE EXIT  /  楼层疏散指引", 56, 40, 900, 36, 24, "#24724E", True),
         sk.label("从当前位置，走两条路到安全出口", 56, 90, 1300, 60, 44, "#183C2C", True),
         sk.box(56, 184, 1090, 720, "#FFFFFF", 16, "#C9D5CD"),
         sk.label("二层办公平面 · 示意", 104, 206, 500, 34, 24, "#66786D"),
         sk.box(104, 300, 280, 210, "#E1E9E3", 8), sk.label("开放办公区", 138, 384, 212, 40, 28, "#183C2C", True, "CENTER"),
         sk.box(414, 300, 270, 210, "#E8EDF0", 8), sk.label("会议室", 454, 384, 190, 40, 28, "#183C2C", True, "CENTER"),
         sk.box(714, 300, 374, 210, "#F1E8DF", 8), sk.label("茶水 / 休息区", 770, 384, 262, 40, 28, "#183C2C", True, "CENTER"),
         sk.box(104, 650, 330, 178, "#E8EDF0", 8), sk.label("档案室", 154, 716, 230, 40, 28, "#183C2C", True, "CENTER"),
         sk.box(464, 650, 624, 178, "#E1E9E3", 8), sk.label("接待 / 打印区", 674, 716, 230, 40, 28, "#183C2C", True, "CENTER"),
         sk.box(104, 534, 984, 88, "#D5E7DB", 8), sk.label("主走廊", 502, 554, 188, 36, 24, "#24724E", True, "CENTER"),
         sk.circle(284, 468, 24, "#246BCE"), sk.label("你在这里", 320, 446, 180, 38, 24, "#246BCE", True),
         sk.line(284, 492, 284, 578, "#24724E", 12), sk.line(284, 578, 130, 578, "#24724E", 12), sk.line(130, 578, 130, 546, "#24724E", 12),
         sk.line(284, 578, 1058, 578, "#24724E", 12), sk.line(1058, 578, 1058, 546, "#24724E", 12),
         sk.box(92, 510, 76, 50, "#24724E", 6), sk.label("出口 A", 92, 470, 110, 34, 22, "#24724E", True),
         sk.box(1020, 510, 76, 50, "#24724E", 6), sk.label("出口 B", 1006, 470, 110, 34, 22, "#24724E", True),
         sk.box(1200, 184, 344, 720, "#183C2C", 16), sk.label("疏散三步", 1232, 220, 280, 40, 28, "#BEE5C9", True),
         sk.label("01  沿绿色路线撤离\n02  不乘电梯、不返回取物\n03  到东侧广场集合点", 1232, 300, 280, 224, 26, "#FFFFFF"),
         sk.box(1232, 574, 280, 112, "#E7F2C4", 12), sk.label("集合点", 1252, 590, 240, 32, 24, "#183C2C", True),
         sk.label("东侧广场 · 旗杆旁", 1252, 632, 240, 36, 22, "#183C2C"),
         sk.label("紧急联系：物业值班台", 1232, 744, 280, 64, 22, "#BEE5C9"),
         sk.label("本图为演示疏散逻辑，不替代现场标识与合规图纸。", 56, 934, 1488, 32, 22, "#66786D")]
    return sk.snapshot(1600, 1000, c, "#EEF2EF")


def solar() -> str:
    c = [sk.box(0, 0, 1600, 1000, "#091426"), sk.label("ORBIT NOTES  /  天文课堂", 56, 40, 800, 36, 24, "#78C7E8", True),
         sk.label("把公转周期放进同心轨道", 56, 92, 1100, 60, 44, "#F0F6FF", True),
         sk.label("轨道与行星大小为示意 · 非真实比例", 1100, 112, 444, 32, 22, "#8FA7C3", False, "RIGHT"),
         sk.circle(600, 548, 330, "#132844"), sk.circle(600, 548, 250, "#173553"), sk.circle(600, 548, 170, "#1B4064"),
         sk.circle(600, 548, 62, "#F6B94C"), sk.label("太阳", 548, 532, 104, 36, 24, "#5E3B10", True, "CENTER")]
    planets = [(0, -330, 28, "水星", "88 天", "#AEB8C8"), (1, -250, 38, "金星", "225 天", "#E7B56B"),
               (2, -170, 40, "地球", "365 天", "#4DA9D8"), (3, -250, 34, "火星", "687 天", "#D96F4A")]
    used = []
    for index, (orbit, offset, radius, name, period, color) in enumerate(planets):
        angle = math.radians(-55 + index * 42)
        x = 600 + offset * math.cos(angle)
        y = 548 + offset * math.sin(angle)
        c.append(sk.circle(x, y, radius, color))
        label_x = x + 44
        label_y = y - 34
        if label_x > 1070:
            label_x = x - 188
        c += [sk.label(name, label_x, label_y, 150, 34, 26, color, True), sk.label(period, label_x, label_y + 36, 150, 32, 22, "#C4D5E8")]
    c += [sk.box(1180, 230, 364, 570, "#101F35", 16, "#29415E"), sk.label("读图方法", 1212, 262, 300, 38, 28, "#78C7E8", True),
         sk.label("离太阳越近，轨道越小；\n数字是公转一周所需时间。\n\n88 ＜ 225 ＜ 365 ＜ 687", 1212, 330, 300, 260, 26, "#F0F6FF"),
         sk.box(1212, 654, 300, 100, "#F6B94C", 12), sk.label("地球：约 365 天", 1232, 684, 260, 40, 26, "#3E2B0D", True, "CENTER"),
         sk.label("数据为常用近似公转周期。", 56, 916, 1000, 34, 22, "#8FA7C3")]
    return sk.snapshot(1600, 1000, c, "#091426")


def market() -> str:
    c = [sk.box(0, 0, 1080, 1440, "#174D3C"), sk.box(46, 46, 988, 1348, "#174D3C", 18, "#8CB49B"),
         sk.label("青禾周末菜摊  /  QINGHE MARKET", 90, 86, 900, 36, 24, "#D6E7B2", True),
         sk.label("今天，吃点儿新鲜的", 88, 148, 904, 80, 54, "#FFF6DC", True),
         sk.circle(892, 190, 54, "#F2C96D"), sk.line(866, 260, 918, 260, "#F2C96D", 4),
         sk.label("11.07  SAT   /   08:00—13:00", 90, 258, 900, 36, 24, "#B8D2BA"),
         sk.box(90, 332, 900, 2, "#6F9C82")]
    produce = [("奶油生菜", "¥8", "/ 份", "现货", "#B9D98A"), ("沙地番茄", "¥12", "/ 斤", "现货", "#E97858"),
               ("紫皮洋葱", "¥6", "/ 斤", "现货", "#B79ACF"), ("水果黄瓜", "¥10", "/ 斤", "剩 3 斤", "#7FBF7A"),
               ("本地菠菜", "¥9", "/ 把", "售罄", "#75A887"), ("贝贝南瓜", "¥15", "/ 个", "现货", "#E4AD5B")]
    for index, (name, price, unit, status, color) in enumerate(produce):
        y = 374 + index * 126
        c += [sk.circle(126, y + 44, 30, color), sk.label(name, 184, y + 10, 330, 44, 32, "#FFF6DC", True),
              sk.label(price, 548, y, 190, 58, 44, "#F2C96D", True, "RIGHT"), sk.label(unit, 754, y + 16, 100, 36, 24, "#B8D2BA"),
              sk.box(866, y + 12, 108, 40, "#DDE9CF" if status == "现货" else "#E7B0A0" if status == "售罄" else "#F2C96D", 8),
              sk.label(status, 870, y + 18, 100, 30, 22, "#174D3C", True, "CENTER"), sk.box(184, y + 88, 790, 1, "#3E735B")]
    c += [sk.box(90, 1160, 900, 156, "#D6E7B2", 14), sk.label("自带布袋减 ¥2", 120, 1184, 500, 42, 30, "#174D3C", True),
         sk.label("蔬菜售罄以现场小黑板为准；不提供塑料袋。", 120, 1240, 840, 36, 24, "#174D3C"),
         sk.label("本地采摘 · 当日到货 · 演示价格", 90, 1340, 900, 30, 20, "#B8D2BA", False, "CENTER")]
    return sk.snapshot(1080, 1440, c, "#174D3C")


def conference() -> str:
    c = [sk.box(0, 0, 1080, 1440, "#1746D1"), sk.label("BEFORE THE API  /  产品设计大会", 56, 48, 968, 36, 24, "#DDFA69", True),
         sk.label("接口之前", 52, 112, 976, 128, 100, "#FFFFFF", True),
         sk.label("10.24", 54, 274, 600, 160, 132, "#DDFA69", True),
         sk.label("周六 09:30—17:30\n上海 · 西岸设计中心", 650, 306, 374, 100, 28, "#FFFFFF", True, "RIGHT")]
    for x in range(56, 1025, 72):
        c.append(sk.line(x, 492, x, 1230, "#3A61DA", 2))
    for y in range(492, 1231, 74):
        c.append(sk.line(56, y, 1024, y, "#3A61DA", 2))
    c += [sk.label("三条议题线，选择你的切入点", 56, 518, 968, 42, 28, "#DDFA69", True)]
    columns = [("设计系统", "#F4A7C0"), ("AI 交互", "#DDFA69"), ("前端实现", "#8ED9F2")]
    content = [("09:30", "从变量到共识", "林岚 · 设计负责人"), ("11:00", "组件的边界", "周屿 · 系统设计师"),
               ("14:00", "可访问性工作坊", "陈墨 · 研究顾问"), ("16:00", "圆桌：长期主义", "三位讲者共同参与")]
    for index, (title, color) in enumerate(columns):
        x = 56 + index * 328
        c += [sk.box(x, 584, 304, 62, color, 8), sk.label(title, x + 16, 598, 272, 36, 26, "#102D8B", True, "CENTER")]
        for row, (time, talk, speaker) in enumerate(content):
            y = 670 + row * 132
            if index == 2 and row == 2:
                talk, speaker = "DSL 渲染实战", "许放 · 前端工程师"
            if index == 1 and row == 2:
                talk, speaker = "人机协作原型", "唐可 · 产品设计师"
            c += [sk.label(time, x, y, 304, 32, 22, color, True), sk.label(talk, x, y + 36, 304, 36, 24, "#FFFFFF", True),
                  sk.label(speaker, x, y + 78, 304, 32, 20, "#C4D2FF")]
    c += [sk.box(56, 1240, 968, 112, "#DDFA69", 12), sk.label("早鸟票 ¥299  /  学生票 ¥99", 82, 1262, 620, 40, 28, "#102D8B", True),
         sk.label("立即报名  →", 742, 1266, 254, 36, 26, "#102D8B", True, "RIGHT"),
         sk.label("演示活动信息 · 非真实售票", 56, 1380, 968, 28, 20, "#C4D2FF", False, "CENTER")]
    return sk.snapshot(1080, 1440, c, "#1746D1")


BUILDERS = {"case-01": museum, "case-02": heatmap, "case-03": budget, "case-04": recipe, "case-05": transit,
            "case-06": album, "case-07": evacuation, "case-08": solar, "case-09": market, "case-10": conference}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["plan", "render", "finalize"])
    parser.add_argument("--case")
    parser.add_argument("--version", default="v001")
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "plan":
        path = ck.prepare(TASK, cases())
        print(sk.rel(path))
    elif args.mode == "render":
        selected = [case for case in cases() if not args.case or case["id"] == args.case]
        for case in selected:
            image, record = ck.render_case(TASK, case, BUILDERS[case["id"]](), args.version)
            print(json.dumps({"case": case["id"], "image": sk.rel(image), "status": record["http_status"]}, ensure_ascii=False))
    else:
        portfolio = ck.finalize(TASK, ck.paths(TASK)[1] / "plan-v001.json", args.review_file,
            "十件作品跨越文化传播、公共决策、个人财务、厨房操作、城市出行、音乐发行、安全疏散、科学教育、社区商业与会议策划。它们不共用一种卡片模板，而是分别用海报、地图、控制台、教学单、导览图、唱片封套、平面图、轨道图、价格牌和议程长图解决真实观看任务。所有品牌与演示数据均明确标注为虚构。",
            "十张最终服务原图已逐件完整查看，并生成接触表比较构图广度。展览海报、食谱、菜摊与议程采用竖版；热力图、交通图、疏散图与天文图采用横版；预算与专辑采用方版。各件的标题、关键数据/路径、行动入口、目标尺寸可读性、比例与素材声明均通过；未发现跨件复用同一版式仅换色的情况。")
        print(json.dumps({"completed": TASK, "cases": len(portfolio["cases"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
