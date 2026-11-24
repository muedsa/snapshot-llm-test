from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B02"
INK = "#17243B"
BLUE = "#2855D9"
LIME = "#D8F275"
PAPER = "#F5F1E7"
ORANGE = "#F27B4B"
TEAL = "#1E7B70"
MUTED = "#68748A"
WHITE = "#FFFFFF"


def criteria(content: str, geometry: str, minimum: int = 22) -> list[dict]:
    return [
        {"id": "C1-content", "condition": content, "method": "逐件打开最终PNG，核对项目身份、关键内容与用户行动。"},
        {"id": "C2-system", "condition": "正确使用回环工坊的色彩、字阶、圆角、页眉/页脚与状态色规则。", "method": "对照design-system.json并查看最终图，检查跨触点一致性与适配。"},
        {"id": "C3-geometry", "condition": geometry, "method": "实际查看并核对生成坐标、比例、对齐与文本边界。"},
        {"id": "C4-provenance", "condition": "最终图为真实服务PNG，完整DSL与UTF-8请求及响应匹配。", "method": "核对请求日志、PNG字节哈希、DSL规范化哈希和尺寸。"},
    ]


def case_list() -> list[dict]:
    base = {"audience": "回环工坊的社区居民、维修求助者与志愿维修师", "use_context": "社区维修咖啡馆线上线下触点",
            "content_basis": "自拟社区维修项目；所有预约号、库存、排班与影响数据均为演示，不宣称真实部署。"}
    data = [
        ("case-01", "修好它，再陪你久一点｜招募海报", [1080, 1440], "社区公告栏与社交分享", "了解周六维修活动并带旧物到场。", "巨型环形维修符号与行动信息", "活动时间、地点、可维修品类与预约/到场规则完整。", "圆形符号、标题和底部信息分区不重叠。"),
        ("case-02", "能修什么｜服务菜单", [1200, 1600], "店内立牌与网站服务页", "判断自己的物品是否能修并选择服务。", "四行图标化服务目录", "小家电、自行车、衣物、家具四类服务及限制完整。", "图标、价格/时长和限制文字逐行对齐。"),
        ("case-03", "预约成功｜到店凭证", [1200, 900], "手机相册与工坊签到屏", "按时到店并出示预约号。", "蓝底双栏凭证与示意识别码", "日期、时段、预约号、物品与迟到规则完整。", "识别码与文字信息分区清楚，无裁切。"),
        ("case-04", "别忘了带旧物｜行前提醒", [720, 1280], "手机消息提醒", "完成到店前准备并找到入口。", "手机消息卡与三步清单", "提醒时间、地址、携带物品和改期入口完整。", "消息气泡与清单不重叠，底部操作可达。"),
        ("case-05", "A017｜现场排队票", [900, 1200], "现场取号机与纸质小票", "知道当前进度并等待叫号。", "撕口票根与巨大号码", "号码、当前叫号、预计等待和等待规则完整。", "票根分隔线、孔位与内容不冲突。"),
        ("case-06", "一起修｜年度会员卡", [1080, 720], "钱包实体卡与数字会员卡", "识别会员身份并了解权益。", "横版双色会员卡", "会员号、有效期、三项权益与项目标识完整。", "姓名、号码与权益区域互不遮挡。"),
        ("case-07", "周六班组｜志愿者排班", [1600, 1000], "志愿者后台与开工前看板", "确认岗位、交接对象与空档。", "时间网格排班与岗位色", "四个时段、岗位、志愿者和交接说明完整。", "网格时间与班次对齐；空档有明确标记。"),
        ("case-08", "配件够不够｜库存看板", [1600, 1000], "工坊备料台与管理后台", "识别低库存并决定补货。", "库存表、比例条与补货侧栏", "六类配件库存、安全线与补货量准确。", "比例条按上限归一；状态与数值一致。"),
        ("case-09", "让旧物继续｜年度影响报告", [1600, 1000], "社区年会投影与资助方简报", "理解维修规模、环境贡献与资助需求。", "大数字、月度柱图与环形图", "286件、412小时、1.8吨及月度数据一致。", "柱高按数值比例；环图与图例对应。"),
        ("case-10", "给旧物第二次机会｜筹款海报", [1080, 1350], "社区募捐页面与线下海报", "理解筹款用途并参与捐赠。", "橙底进度温度计与大字行动", "目标8640/12000元、72%与三项用途完整。", "进度比例与数字一致；行动按钮不遮挡文字。"),
    ]
    cases = []
    for cid, title, dims, context, goal, intent, content, geometry in data:
        cases.append(dict(base, id=cid, title=title, dimensions=dims, use_context=context, user_goal=goal,
                          visual_intent=intent, content_basis=base["content_basis"] + f" 本触点：{content}",
                          dsl_capabilities=["Positioned", "Stack", "Container", "Text", "圆角", "圆", "线", "透明度", "数据比例"],
                          criteria=criteria(content, geometry)))
    return cases


def header(c: list[str], w: int, eyebrow: str, title: str, subtitle: str = "", dark: bool = False, y: int = 44) -> None:
    color = WHITE if dark else INK
    c += [sk.label("回环工坊  /  LOOP WORKS", 56, y, w - 112, 34, 22, LIME if dark else BLUE, True),
          sk.label(title, 54, y + 60, w - 108, 78, 52, color, True)]
    if subtitle:
        c.append(sk.label(subtitle, 58, y + 148, w - 116, 44, 24, "#C7D3F5" if dark else MUTED))


def footer(c: list[str], w: int, code: str, dark: bool = False, y: int = 1310) -> None:
    c.append(sk.label(f"LOOP WORKS  ·  {code}  ·  演示项目", 56, y, w - 112, 30, 18, "#C7D3F5" if dark else MUTED, False, "RIGHT"))


def tag(c: list[str], x: int, y: int, w: int, text: str, fill: str = LIME, color: str = INK) -> None:
    c += [sk.box(x, y, w, 42, fill, 21), sk.label(text, x + 12, y + 7, w - 24, 28, 18, color, True, "CENTER")]


def poster() -> str:
    c = [sk.box(0, 0, 1080, 1440, BLUE), sk.label("回环工坊  /  LOOP WORKS", 64, 58, 952, 36, 24, LIME, True),
         sk.label("修好它，", 58, 142, 960, 112, 86, WHITE, True), sk.label("再陪你久一点。", 58, 260, 960, 112, 76, WHITE, True),
         sk.circle(540, 682, 246, LIME), sk.circle(540, 682, 168, BLUE), sk.circle(540, 682, 90, ORANGE),
         sk.box(516, 494, 48, 376, PAPER, 24), sk.box(352, 658, 376, 48, PAPER, 24),
         sk.box(504, 494, 72, 72, LIME, 36), sk.box(504, 798, 72, 72, LIME, 36),
         sk.label("REPAIR  ·  REUSE  ·  RETURN", 160, 976, 760, 36, 22, LIME, True, "CENTER"),
         sk.box(64, 1060, 952, 220, INK, 24), sk.label("每周六  10:00—16:00", 96, 1092, 880, 48, 32, WHITE, True),
         sk.label("梧桐路 18 号 · 社区中心一层", 96, 1150, 880, 38, 24, "#C7D3F5"),
         sk.label("小家电 / 自行车 / 衣物 / 家具", 96, 1200, 880, 34, 22, LIME),
         sk.label("免费诊断 · 配件按成本 · 请提前预约", 96, 1244, 880, 30, 20, WHITE),
         sk.label("社区活动信息为演示", 64, 1350, 952, 28, 18, "#C7D3F5", False, "CENTER")]
    return sk.snapshot(1080, 1440, c, BLUE)


def menu() -> str:
    c = [sk.box(0, 0, 1200, 1600, PAPER)]
    header(c, 1200, "", "你能修什么？", "先描述故障，再由维修师判断是否适合现场处理。")
    rows = [("01", "小家电", "电风扇 / 台灯 / 电水壶", "诊断免费 · 配件另计", BLUE),
            ("02", "自行车", "刹车 / 变速 / 轮胎", "基础保养 30 分钟起", TEAL),
            ("03", "衣物与织物", "开线 / 换扣 / 小面积织补", "简单修补 20 分钟起", ORANGE),
            ("04", "小家具", "松动连接 / 抽屉滑轨", "需拆装时先评估", INK)]
    for i, (num, name, examples, note, color) in enumerate(rows):
        y = 300 + i * 260
        c += [sk.box(56, y, 1088, 224, WHITE, 20), sk.circle(146, y + 80, 48, color),
              sk.label(num, 110, y + 60, 72, 40, 24, WHITE, True, "CENTER"),
              sk.label(name, 222, y + 30, 340, 48, 34, INK, True),
              sk.label(examples, 222, y + 94, 530, 38, 24, MUTED),
              sk.box(222, y + 154, 840, 2, "#E1E4E8"), sk.label(note, 222, y + 174, 840, 32, 22, color, True),
              sk.label("→", 1020, y + 82, 72, 48, 34, color, True, "CENTER")]
    c += [sk.box(56, 1372, 1088, 142, LIME, 18), sk.label("不接：燃气设备 / 医疗设备 / 高压电器", 84, 1400, 1032, 40, 26, INK, True),
          sk.label("无法现场修好的，我们会给出下一步建议。", 84, 1450, 1032, 34, 22, INK),
          sk.label("服务范围与价格为演示", 56, 1538, 1088, 28, 18, MUTED, False, "CENTER")]
    return sk.snapshot(1200, 1600, c, PAPER)


def booking() -> str:
    c = [sk.box(0, 0, 1200, 900, BLUE), sk.label("回环工坊  /  LOOP WORKS", 64, 48, 1072, 34, 22, LIME, True),
         sk.label("预约成功，周六见。", 60, 112, 1080, 72, 54, WHITE, True),
         sk.box(64, 224, 1072, 572, WHITE, 28), sk.box(64, 224, 300, 572, INK, 28),
         sk.label("A017", 92, 280, 244, 80, 64, LIME, True, "CENTER"), sk.label("预约号", 92, 368, 244, 32, 22, "#C7D3F5", False, "CENTER")]
    for row in range(9):
        for col in range(9):
            if (row * 7 + col * 11 + row * col) % 5 < 2:
                c.append(sk.box(102 + col * 22, 462 + row * 22, 16, 16, LIME if (row + col) % 3 == 0 else WHITE, 2))
    c.append(sk.label("示意识别码", 92, 704, 244, 30, 18, "#C7D3F5", False, "CENTER"))
    c += [sk.label("11月28日  周六", 416, 274, 650, 46, 34, INK, True),
          sk.label("10:30—11:00", 416, 338, 650, 52, 40, BLUE, True),
          sk.box(416, 414, 648, 2, "#DCE1EA"),
          sk.label("维修物品", 416, 446, 160, 32, 22, MUTED), sk.label("台灯不亮", 596, 446, 468, 36, 26, INK, True),
          sk.label("维修师", 416, 504, 160, 32, 22, MUTED), sk.label("林师傅 · 小家电岗", 596, 504, 468, 36, 26, INK),
          sk.label("地点", 416, 562, 160, 32, 22, MUTED), sk.label("梧桐路18号 · 社区中心一层", 596, 562, 468, 36, 24, INK),
          sk.box(416, 632, 648, 110, "#EEF2FF", 14), sk.label("请提前10分钟到店签到。", 440, 650, 600, 36, 24, BLUE, True),
          sk.label("迟到15分钟以上，请重新取号。", 440, 696, 600, 30, 20, MUTED),
          sk.label("演示预约凭证 · 非真实入场码", 64, 830, 1072, 30, 18, "#C7D3F5", False, "CENTER")]
    return sk.snapshot(1200, 900, c, BLUE)


def reminder() -> str:
    c = [sk.box(0, 0, 720, 1280, "#E9EDF5"), sk.box(0, 0, 720, 96, INK),
         sk.label("09:10", 42, 30, 180, 36, 24, WHITE, True), sk.label("回环工坊", 540, 30, 138, 36, 22, LIME, True, "RIGHT"),
         sk.label("别忘了带旧物", 48, 144, 624, 64, 44, INK, True), sk.label("你的维修预约在今天 10:30", 48, 218, 624, 38, 24, MUTED),
         sk.box(48, 294, 624, 270, WHITE, 26), sk.circle(114, 354, 34, LIME), sk.label("修", 90, 330, 48, 48, 26, INK, True, "CENTER"),
         sk.label("回环工坊", 172, 326, 430, 36, 26, INK, True), sk.label("09:10", 172, 370, 430, 30, 18, MUTED),
         sk.label("一会儿见！请带台灯和\n购买时的配件。", 84, 430, 552, 92, 30, INK)]
    c += [sk.label("到店前，确认三件事", 48, 620, 624, 44, 30, INK, True)]
    checks = ["带上待修物品与必要配件", "提前10分钟到社区中心签到", "如需改期，请及时释放名额"]
    for i, text in enumerate(checks):
        y = 696 + i * 96
        c += [sk.circle(76, y + 24, 22, BLUE), sk.label("✓", 60, y + 6, 32, 36, 22, WHITE, True, "CENTER"),
              sk.label(text, 120, y, 552, 52, 26, INK)]
    c += [sk.box(48, 1010, 624, 86, BLUE, 18), sk.label("查看预约与改期  →", 76, 1032, 568, 40, 28, WHITE, True, "CENTER"),
          sk.label("梧桐路18号 · 社区中心一层", 48, 1140, 624, 36, 22, MUTED, False, "CENTER"),
          sk.label("演示消息 · 非真实通知", 48, 1204, 624, 28, 18, MUTED, False, "CENTER")]
    return sk.snapshot(720, 1280, c, "#E9EDF5")


def queue() -> str:
    c = [sk.box(0, 0, 900, 1200, PAPER), sk.label("回环工坊  /  LOOP WORKS", 64, 54, 772, 34, 22, BLUE, True),
         sk.label("现场排队票", 60, 124, 780, 64, 48, INK, True),
         sk.label("你的号码", 64, 252, 772, 34, 24, MUTED, False, "CENTER"), sk.label("A017", 64, 308, 772, 150, 132, BLUE, True, "CENTER"),
         sk.box(64, 510, 772, 210, INK, 22), sk.label("正在叫号", 96, 544, 300, 32, 22, "#C7D3F5"),
         sk.label("A013", 96, 590, 300, 64, 52, LIME, True), sk.label("预计等待", 520, 544, 260, 32, 22, "#C7D3F5"),
         sk.label("约 20 分钟", 520, 596, 260, 44, 30, WHITE, True)]
    for x in range(74, 840, 34):
        c.append(sk.circle(x, 784, 10, PAPER, "#C9CDD4"))
    c += [sk.label("等待时请留意", 64, 834, 772, 40, 28, INK, True),
          sk.label("01  不要远离取号区\n02  听到号码后到维修台登记\n03  过号请重新取号", 64, 894, 772, 154, 26, INK),
          sk.label("取号时间 10:02 · 演示票据", 64, 1110, 772, 32, 20, MUTED, False, "CENTER")]
    return sk.snapshot(900, 1200, c, PAPER)


def membership() -> str:
    c = [sk.box(0, 0, 1080, 720, "#E6EAF2"), sk.box(64, 86, 952, 548, INK, 32),
         sk.box(64, 86, 340, 548, LIME, 32), sk.label("LOOP", 96, 126, 276, 42, 28, INK, True),
         sk.label("一起修", 92, 196, 276, 86, 58, INK, True), sk.label("回环工坊", 96, 292, 276, 36, 24, INK),
         sk.circle(234, 472, 82, BLUE), sk.circle(234, 472, 48, LIME), sk.box(222, 390, 24, 164, PAPER, 12),
         sk.box(152, 460, 164, 24, PAPER, 12),
         sk.label("2027 年度会员", 456, 132, 500, 44, 30, WHITE, True),
         sk.label("周宁", 456, 204, 500, 60, 48, LIME, True),
         sk.label("MEMBER  /  LW-2027-0186", 456, 282, 500, 32, 20, "#C7D3F5"),
         sk.box(456, 344, 500, 2, "#41516E"),
         sk.label("全年工作坊优先预约\n免费参加每月工具课\n配件采购享 9 折", 456, 382, 500, 138, 26, WHITE),
         sk.label("有效期 2027.01—12", 456, 556, 500, 32, 22, LIME),
         sk.label("演示会员卡 · 非真实身份凭证", 64, 668, 952, 28, 18, MUTED, False, "CENTER")]
    return sk.snapshot(1080, 720, c, "#E6EAF2")


def rota() -> str:
    c = [sk.box(0, 0, 1600, 1000, "#F3F5F8")]
    header(c, 1600, "", "周六班组", "11月28日 · 社区中心一层 · 09:30 交接")
    x0, top, cellw, rowh = 260, 310, 230, 126
    for i, label in enumerate(["09:30—10:30", "10:30—12:00", "12:00—14:00", "14:00—16:00"]):
        c += [sk.label(label, 56, top + i * rowh + 42, 184, 32, 20, MUTED, True)]
    roles = ["维修台", "登记接待", "工具讲解", "安全巡视"]
    for j, role in enumerate(roles):
        c.append(sk.label(role, x0 + j * cellw, 264, cellw - 14, 34, 24, INK, True, "CENTER"))
    grid = [["林师傅", "陈可", "周远", "许阿姨"], ["林师傅", "陈可", "周远", "许阿姨"],
            ["何工", "小唐", "周远", "许阿姨"], ["何工", "小唐", "开放体验", "许阿姨"]]
    colors = [BLUE, TEAL, ORANGE, INK]
    for i in range(4):
        for j in range(4):
            x, y = x0 + j * cellw, top + i * rowh
            c += [sk.box(x, y, cellw - 14, rowh - 12, WHITE, 14), sk.box(x, y, 8, rowh - 12, colors[j], 4),
                  sk.label(grid[i][j], x + 22, y + 42, cellw - 50, 34, 24, INK, True)]
    c += [sk.box(1236, 232, 308, 598, INK, 22), sk.label("班次要点", 1268, 268, 244, 40, 28, LIME, True),
          sk.label("09:30  工具清点\n11:30  交接午餐\n14:00  儿童体验\n15:40  关闭电源", 1268, 340, 244, 190, 24, WHITE),
          sk.box(1268, 572, 244, 2, "#41516E"), sk.label("空档", 1268, 604, 244, 32, 22, "#C7D3F5"),
          sk.label("14:00—16:00\n工具讲解岗", 1268, 648, 244, 80, 26, LIME, True),
          sk.label("演示排班", 56, 920, 1488, 30, 20, MUTED)]
    return sk.snapshot(1600, 1000, c, "#F3F5F8")


def inventory() -> str:
    c = [sk.box(0, 0, 1600, 1000, PAPER)]
    header(c, 1600, "", "配件够不够？", "备料台库存 · 周六开工前更新")
    parts = [("USB-C 线材", 18, 30), ("台灯灯座", 4, 12), ("自行车内胎", 7, 20), ("拉链头", 3, 15),
             ("抽屉滑轨", 5, 10), ("常用保险丝", 24, 40)]
    c += [sk.label("配件", 76, 300, 340, 32, 22, MUTED, True), sk.label("当前 / 上限", 760, 300, 250, 32, 22, MUTED, True),
          sk.label("状态", 1040, 300, 180, 32, 22, MUTED, True)]
    for i, (name, stock, maximum) in enumerate(parts):
        y = 358 + i * 82
        status = "需补货" if stock <= maximum * 0.35 else "可用"
        c += [sk.label(name, 76, y, 330, 36, 26, INK, True), sk.box(430, y + 8, 300, 20, "#E0E3E7", 10),
              sk.box(430, y + 8, 300 * stock / maximum, 20, ORANGE if status == "需补货" else BLUE, 10),
              sk.label(f"{stock} / {maximum}", 760, y, 250, 36, 24, INK),
              sk.box(1040, y + 2, 126, 36, ORANGE if status == "需补货" else LIME, 18),
              sk.label(status, 1050, y + 7, 106, 26, 18, WHITE if status == "需补货" else INK, True, "CENTER")]
    c += [sk.box(1240, 270, 288, 588, INK, 22), sk.label("优先补货", 1272, 304, 224, 40, 28, LIME, True),
          sk.label("自行车内胎 13 件\n拉链头   12 件\n抽屉滑轨  5 件\n台灯灯座  8 件", 1272, 368, 224, 180, 24, WHITE),
          sk.box(1272, 580, 224, 2, "#41516E"), sk.label("补货规则", 1272, 610, 224, 32, 22, "#C7D3F5"),
          sk.label("不高于上限 35%\n进入本周补货单", 1272, 662, 224, 92, 26, LIME, True),
          sk.label("演示库存", 76, 912, 1452, 30, 20, MUTED)]
    return sk.snapshot(1600, 1000, c, PAPER)


def impact() -> str:
    c = [sk.box(0, 0, 1600, 1000, INK)]
    header(c, 1600, "", "让旧物继续", "2026 社区影响简报 · 演示汇总", True)
    stats = [("286", "件物品继续使用"), ("412", "小时志愿维修"), ("1.8 吨", "估算减少废弃物")]
    for i, (value, label) in enumerate(stats):
        x = 56 + i * 336
        c += [sk.box(x, 296, 312, 164, "#24344F", 18), sk.label(value, x + 24, 318, 264, 66, 50, LIME, True),
              sk.label(label, x + 24, 398, 264, 34, 20, "#C7D3F5")]
    c += [sk.label("月度维修量", 56, 530, 920, 38, 28, WHITE, True)]
    values = [18, 20, 22, 26, 24, 19, 28, 30, 27, 31, 24, 17]
    assert sum(values) == 286
    for i, value in enumerate(values):
        x = 72 + i * 80
        h = int(value * 4)
        c += [sk.box(x, 858 - h, 44, h, LIME if i == 9 else BLUE, 6),
              sk.label(str(value), x - 6, 812 - h, 56, 28, 16, WHITE, True, "CENTER"),
              sk.label(f"{i + 1}月", x - 6, 876, 56, 28, 16, "#C7D3F5", False, "CENTER")]
    c += [sk.circle(1220, 700, 156, BLUE), sk.circle(1220, 700, 104, INK),
          sk.label("68%", 1112, 670, 216, 62, 46, LIME, True, "CENTER"),
          sk.label("现场修好", 1112, 738, 216, 32, 22, WHITE, False, "CENTER"),
          sk.label("其余获得维修建议", 1030, 900, 380, 32, 22, "#C7D3F5", False, "CENTER"),
          sk.label("环境影响为演示估算，不等同于认证减排量。", 56, 944, 1488, 28, 18, "#C7D3F5")]
    return sk.snapshot(1600, 1000, c, INK)


def fundraiser() -> str:
    c = [sk.box(0, 0, 1080, 1350, ORANGE), sk.label("回环工坊  /  LOOP WORKS", 64, 54, 952, 34, 22, INK, True),
         sk.label("给旧物", 58, 142, 964, 112, 88, INK, True), sk.label("第二次机会。", 58, 266, 964, 112, 80, INK, True),
         sk.label("筹款目标", 64, 456, 360, 34, 24, INK), sk.label("¥8,640 / ¥12,000", 64, 504, 660, 64, 48, WHITE, True),
         sk.label("已完成 72%", 756, 516, 260, 40, 26, INK, True, "RIGHT"),
         sk.box(64, 604, 952, 34, "#F9D0B9", 17), sk.box(64, 604, int(952 * 0.72), 34, INK, 17),
         sk.box(64, 730, 952, 260, PAPER, 22), sk.label("这笔钱将用于", 96, 764, 888, 40, 28, INK, True),
         sk.label("01  购买公共维修工具\n02  补充安全防护用品\n03  支持免费社区工作坊", 96, 826, 888, 126, 28, INK),
         sk.box(64, 1060, 952, 116, INK, 20), sk.label("捐赠 ¥50，让一次维修发生  →", 92, 1094, 896, 48, 32, LIME, True, "CENTER"),
         sk.label("演示筹款信息 · 非真实捐款页面", 64, 1260, 952, 30, 18, INK, False, "CENTER")]
    return sk.snapshot(1080, 1350, c, ORANGE)


BUILDERS = {"case-01": poster, "case-02": menu, "case-03": booking, "case-04": reminder, "case-05": queue,
            "case-06": membership, "case-07": rota, "case-08": inventory, "case-09": impact, "case-10": fundraiser}


def system_documents() -> tuple[str, dict, dict]:
    brief = """# 回环工坊：一个社区维修咖啡馆的视觉生态

## 项目问题

社区居民有维修小家电、自行车、衣物和家具的需求，但常面临三类断点：不知道能否修、无法判断预约与等待进度、不知道活动如何持续运作。回环工坊以每周六开放的维修咖啡馆连接求助者与志愿维修师，采用免费诊断、配件按成本、会员支持与社区筹款相结合的虚构运作模式。

## 解决方案

十件触点覆盖从认知到参与的完整路径：招募海报解释项目，服务菜单帮助判断适配，预约凭证与提醒降低到店摩擦，排队票管理现场预期，会员卡承载持续关系；排班、库存、影响报告和筹款海报则服务于运营者、志愿者与资助者。它们共享“回环”环形符号、钴蓝/荧光黄绿/纸色的基础色，以及清晰的大字阶，但使用海报、目录、凭证、消息、票根、横卡、网格、数据板和筹款页等不同构图。

## 复用组件与适配

页眉统一使用“回环工坊 / LOOP WORKS”、圆角容器、状态色和演示声明。组件在手机提醒中压缩为单栏，在排班与库存中扩展为高密度网格，在年度报告中切换为深色数据场景。所有作品仍以完整自包含DSL构造，未嵌入外部素材。

## 内容与验证边界

项目、品牌、人物、预约号、排班、库存和影响数据均为演示，不宣称真实客户部署或环境认证。最终视觉以逐件打开服务原图和接触表整体审查验证；设计系统只记录实际用于这十件作品的规则。
"""
    design = {"schema_version": 1, "task_id": TASK, "project": "回环工坊 / LOOP WORKS", "path_base": "output_dir",
              "brand_idea": "修好、再用、回到社区；环形符号同时表达循环与协作。",
              "colors": {"ink": INK, "primary": BLUE, "accent": LIME, "paper": PAPER, "warning_action": ORANGE, "success": TEAL, "text_muted": MUTED},
              "type": {"family": sk.FONT, "display": "52–88px BOLD", "section": "28–40px BOLD", "body": "22–30px NORMAL", "meta": "18–20px"},
              "shape": {"card_radius": "14–32px", "pill_radius": "18–21px", "symbol": "同心圆与十字连接件"},
              "components": ["项目页眉", "演示页脚", "状态标签", "圆角信息卡", "数据比例条", "步骤清单", "服务行", "时间网格"],
              "applied_cases": {case["id"]: case["dsl_capabilities"] for case in case_list()},
              "component_stress_test": {"mobile": "case-04单栏消息与三步清单", "dense": "case-07排班网格与case-08库存表", "wide": "case-09数据报告", "print": "case-05票根与case-06会员卡"},
              "asset_policy": "pure_dsl", "supporting_assets": []}
    touch = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "project": "回环工坊",
             "journey": ["认知", "判断", "预约", "到店", "持续参与", "运营", "支持"],
             "touchpoints": [{"case_id": case["id"], "title": case["title"], "stage": stage, "audience": case["audience"],
                              "use_context": case["use_context"], "user_goal": case["user_goal"], "content_signal": case["visual_intent"]}
                             for case, stage in zip(case_list(), ["认知", "判断", "预约", "到店", "到店", "持续参与", "运营", "运营", "运营", "支持"])]}
    return brief, design, touch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["plan", "render", "docs", "finalize"])
    parser.add_argument("--case")
    parser.add_argument("--version", default="v001")
    parser.add_argument("--review-file")
    args = parser.parse_args()
    if args.mode == "plan":
        print(sk.rel(ck.prepare(TASK, case_list())))
    elif args.mode == "render":
        for case in case_list():
            if not args.case or case["id"] == args.case:
                image, record = ck.render_case(TASK, case, BUILDERS[case["id"]](), args.version)
                print(json.dumps({"case": case["id"], "image": sk.rel(image), "status": record["http_status"]}, ensure_ascii=False))
    elif args.mode == "docs":
        output, temp = ck.paths(TASK)
        output.mkdir(parents=True, exist_ok=True)
        temp.mkdir(parents=True, exist_ok=True)
        brief, design, touch = system_documents()
        (output / "project-brief.md").write_text(brief, encoding="utf-8")
        sk.write_json(output / "design-system.json", design)
        sk.write_json(output / "touchpoint-map.json", touch)
        sk.write_json(temp / "system-design-source.json", {"design_system": design, "touchpoint_map": touch})
        print("B02 project documents saved")
    else:
        portfolio = ck.finalize(TASK, ck.paths(TASK)[1] / "plan-v001.json", args.review_file,
            "回环工坊用同一品牌语言串联十个真实触点。视觉生态不是十张同版式换色海报，而是从公众认知、服务判断、预约到店、会员关系，到志愿者与物资运营、年度反馈和社区资助的完整系统。",
            "十张最终服务原图已逐件完整查看，并查看最终接触表。共享页眉、色彩、字阶和圆角规则在不同媒介中成立；手机单栏、票根、横卡、排班网格与高密度报告分别适配其观看任务。三件发现的数值或版式问题已修复并复查，最终集合无已知影响交付的缺陷。")
        state_path = ROOT / sk.CONFIG["output_root"] / sk.init_suite()[0] / "_suite/suite-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        entry = next(item for item in state["tasks"] if item["id"] == TASK)
        for name in ("project-brief.md", "design-system.json", "touchpoint-map.json"):
            path = ck.paths(TASK)[0] / name
            entry["artifacts"].append(sk.rel(path))
        sk.write_json(state_path, state)
        sk.checkpoint(sk.init_suite()[0], "B02-extra-artifacts-recorded")
        print(json.dumps({"completed": TASK, "cases": len(portfolio["cases"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
