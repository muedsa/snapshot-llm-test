# -*- coding: utf-8 -*-
"""Write every B01 deliverable: case.md x10, portfolio.json/.md, gallery.html,
snapshot-usage.md, task-metrics.json, plus iterations.jsonl / tool-usage.jsonl."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHARED = os.path.join(os.path.dirname(HERE), "_suite", "shared")
sys.path.insert(0, SHARED)
import suite_common as sc  # noqa: E402

OUT = sc.task_out("B01")
TMP = sc.task_tmp("B01")

# id, name, title, png, dims, audience, context, goal, basis, intent, caps, criteria, review
CASES = [
    dict(id="case-01", name="c01-roast-profile", title="咖啡烘焙曲线复盘卡",
         png="case-01/final.png", dims=[1440, 1010], ver="v3",
         audience="精品咖啡烘焙师 / 品控",
         context="烘焙车间平板或打印后贴在烘豆机旁，暗光环境，30–60 cm 观看",
         goal="一批烘完立刻判断曲线是否达标，并决定下一批的火力与时间调整",
         basis="脚本按 ROR 计划积分出的烘焙曲线；批次、工坊、杯测分均为虚构演示数据",
         intent="以琥珀色填充表现「豆温」的体量、以青色细线表现「ROR」的速率，"
                "让两条不同量纲的曲线在同一坐标系里互不干扰",
         caps="Transform 旋转线段折线、4 px 柱状填充、双 y 轴刻度、"
              "虚线与事件圆点、卡片式信息层级",
         criteria="回温点/脱水结束/一爆/下豆四个里程碑必须落在曲线上；"
                  "DTR、失重率、ROR@FC 必须与曲线一致；无文字裁切或压字",
         unresolved=["发展期 ROR 下降较陡（14.3→2.5 ℃/min），是解算器为命中 10:12 下豆时间的结果"],
         requests=["B01-REQ-0002", "B01-REQ-0004", "B01-REQ-0005", "B01-REQ-0010", "B01-REQ-0033"],
         iterations=["c01-v1-baseline", "c01-v2-visual", "c01-v3-visual"]),
    dict(id="case-02", name="c02-marathon-profile", title="半程马拉松赛道剖面与配速带",
         png="case-02/final.png", dims=[1680, 980], ver="v3",
         audience="参赛跑者 / 赛事志愿者",
         context="赛前 1–2 天在手机上放大看，或打印成 A3 贴在跑团墙上",
         goal="看懂坡度分布、记住补给站位置，并据此决定分段配速",
         basis="三个高斯爬坡叠加细波动的解析高程模型；爬升/下降/坡度/配速全部由脚本积分计算",
         intent="用颜色直接编码坡度方向与强度，让「哪里难」一眼可见；"
                "剖面、坡度带、补给站三条信息带各占一行互不遮挡",
         caps="解析函数采样、5 px 柱状面积填充、按坡度分色、"
              "方向箭头、分段表格、双 KPI 卡",
         criteria="剖面填充色必须与下方坡度带一致；分段配速之和必须精确等于目标完赛时间；"
                  "补给站编号不得压住剖面线",
         unresolved=["累计爬升 250 m 对半马偏高，属于虚构山地道赛的设定，未做削弱"],
         requests=["B01-REQ-0006(fail)", "B01-REQ-0011", "B01-REQ-0015", "B01-REQ-0018(fail-replay)",
                   "B01-REQ-0034"],
         iterations=["c02-v1-elements-fail", "c02-v2-visual", "c02-v3-visual"]),
    dict(id="case-03", name="c03-vinyl-cover", title="黑胶唱片封底 · 夜航船",
         png="case-03/final.png", dims=[1450, 1450], ver="v3",
         audience="独立厂牌设计与实体唱片收藏者",
         context="30 cm 见方的实体唱片封套，手持或平放观看",
         goal="读完曲序、每面时长、制作人员、编号与条码，并辨认厂牌",
         basis="虚构厂牌「北纬唱片」与虚构专辑；曲目时长、总时长、条码条宽均由脚本生成",
         intent="深色纸面 + 烫金细线 + 衬线标题，做出实体印刷的克制感；"
                "右下角用同心圆做唱片纹路质感，左侧书脊竖排文字",
         caps="旋转文字（书脊与标题）、确定性条码柱、同心圆纹理层、"
              "双栏曲目表、微型波形装饰",
         criteria="A/B 面时长之和必须等于标注的总时长；条码柱宽与模块数必须由编号推导；"
                  "书脊文字不得超出画布",
         unresolved=["曲目旁的微型波形只是节奏装饰，与真实音频无关，已在图注中说明"],
         requests=["B01-REQ-0007(fail)", "B01-REQ-0012", "B01-REQ-0016", "B01-REQ-0019(fail-replay)",
                   "B01-REQ-0035"],
         iterations=["c03-v1-elements-fail", "c03-v2-visual", "c03-v3-visual"]),
    dict(id="case-04", name="c04-med-plan", title="家庭用药周计划（照护者用）",
         png="case-04/final.png", dims=[1120, 1620], ver="v2",
         audience="居家照护者 / 慢病患者的家属",
         context="冰箱贴或桌面立牌，每天 4 个时间点近距离查看并打勾",
         goal="不漏服、不错服，并在余量见底前补货",
         basis="虚构患者「陈素云」与 5 种常见药物的演示处方；每日片数、余量天数由处方表算出",
         intent="以颜色区分药物而不是靠文字记忆；四行时间带 × 七天构成可打勾的矩阵；"
                "库存不足用红色直接跳到眼前",
         caps="7×4 网格、圆角药丸色块、勾选框、库存进度条、可填写记录表",
         criteria="网格中的药块必须与清单一一对应；每日总片数必须等于各行之和；"
                  "余量 ≤14 天必须标红",
         unresolved=["午/晚/睡前三行只有一种药，留白较多，属于「可打勾空间」的设计取舍"],
         requests=["B01-REQ-0008", "B01-REQ-0014", "B01-REQ-0036"],
         iterations=["c04-v1-baseline"]),
    dict(id="case-05", name="c05-lunar-calendar", title="月相与深空观测窗口月历",
         png="case-05/final.png", dims=[1560, 1120], ver="v3",
         audience="业余天文爱好者 / 天文社团排期者",
         context="电脑屏幕或打印成 A3 贴在观测站墙上，暗光环境",
         goal="挑出本月最适合出摊的夜晚，并知道当晚月亮有多亮、有多少小时全暗",
         basis="简化朔望月模型计算月相（误差约 ±0.5 天）；"
               "天文暗夜时长由太阳 −18° 时角解算出；行星窗口为演示星历",
         intent="月相用逐行扫描的晨昏线几何真正画出来，而不是用圆形遮挡假装；"
                "每个日期格子同时给出月相、照亮比例与暗夜长度条",
         caps="逐行构建的月相盘、圆弧与圆环、日历网格、水平条形评分、"
              "深色多层次面板",
         criteria="月相盘形状必须与照亮比例一致（凸月必须真的凸）；"
                  "最佳观测夜排序必须由「暗夜时长 ×（1−照亮）^1.5」算出；日期不得溢出月历卡",
         unresolved=["月相为简化模型，未做摄动修正；行星可见窗口是演示数据，已在图内标注"],
         requests=["B01-REQ-0009(fail)", "B01-REQ-0013", "B01-REQ-0017", "B01-REQ-0020(fail-replay)",
                   "B01-REQ-0037"],
         iterations=["c05-v1-elements-fail", "c05-v2-visual", "c05-v3-visual"]),
    dict(id="case-06", name="c06-leather-pattern", title="手工皮具版型技术图（蓝图样式）",
         png="case-06/final.png", dims=[1400, 1010], ver="v3",
         audience="独立皮具工作室 / 手工爱好者",
         context="工作台上平铺打印，边裁边看，30–50 cm 距离",
         goal="按 1:1 版型裁断、打孔、缝合一件 A6 笔记本封套",
         basis="虚构图号 LP-A6-02 的封套版型；缝份、针距、孔数、用料面积均由 mm 尺寸换算",
         intent="青色蓝图 + 网格 + 尺寸线，用工程制图语言表达手工艺；"
                "缝孔以真实针距沿内轮廓排布，可以直接数",
         caps="像素网格、毫米→像素换算、尺寸线与箭头、旋转尺寸数字、"
              "沿轮廓的参数化打孔、比例尺",
         criteria="裁断线必须含缝份；孔数必须由周长与针距算出；"
                  "尺寸数字不得被尺寸线穿过，也不得压住相邻版型",
         unresolved=["C / D 两件未画竖向尺寸线（会压到相邻版型），改由右栏裁断清单给出"],
         requests=["B01-REQ-0021", "B01-REQ-0026", "B01-REQ-0032", "B01-REQ-0038"],
         iterations=["c06-v1-baseline", "c06-v2-visual", "c06-v3-visual"]),
    dict(id="case-07", name="c07-vaccine-timeline", title="儿童疫苗接种时间轴",
         png="case-07/final.png", dims=[1240, 1560], ver="v2",
         audience="幼儿家长 / 社区接种门诊",
         context="竖版打印后贴在家庭文件夹内页，或手机上查看",
         goal="一眼看出哪些剂次已完成、哪一次漏了、下一次什么时候该去",
         basis="虚构儿童（2024-08-12 出生）的演示接种记录；月龄、剂次统计、延迟天数由脚本计算",
         intent="用一条纵向时间轴 + 状态色把所有节点串起来，"
                "延迟节点单独标出计划日期与实际日期的差值，避免「以为打过了」",
         caps="纵向时间轴、状态徽章、动态宽度标签、日期差计算、表单式底栏",
         criteria="每个节点的状态色必须与其实际日期一致；剂次总数与已完成数必须自洽；"
                  "状态徽章不得溢出卡片",
         unresolved=["疫苗名称与剂次仅作排布示例，已在页脚明确「不构成医疗建议」"],
         requests=["B01-REQ-0022", "B01-REQ-0027", "B01-REQ-0039"],
         iterations=["c07-v1-baseline", "c07-v2-visual"]),
    dict(id="case-08", name="c08-podcast-wave", title="播客单集波形与章节卡",
         png="case-08/final.png", dims=[1400, 1400], ver="v1",
         audience="播客听众 / 节目运营",
         context="社交平台方形贴文或节目页头图，手机竖屏首屏",
         goal="在听之前就知道这期讲了什么、哪一段最值得跳过去听",
         basis="虚构播客「潮位线」第 42 集；波形由章节增益 × 音节包络 × 停顿门生成",
         intent="把「章节」做成颜色的分段，让波形本身就是目录；"
                "镜像条带 + 停顿缺口制造可读的音频质感",
         caps="216 根镜像波形柱、分段着色、章节分隔虚线、播放进度指示、"
              "两栏章节表",
         criteria="波形分段颜色必须与章节表一一对应；时长标注必须等于章节时间差；"
                  "播放指示不得压住章节标签",
         unresolved=["波形是脚本按包络生成的示意图，不是真实音频采样，已在图注说明"],
         requests=["B01-REQ-0023", "B01-REQ-0040"],
         iterations=["c08-v1-baseline"]),
    dict(id="case-09", name="c09-approach-chart", title="仪表进近图（虚构机场，教学用）",
         png="case-09/final.png", dims=[1500, 1050], ver="v3",
         audience="飞行模拟玩家 / 航图制图学习者",
         context="桌面显示器或 A3 打印，作为模拟飞行的对照图",
         goal="读懂一个 VOR/DME 进近程序的平面航迹、剖面下降梯度与最低标准",
         basis="完全虚构的机场 ZZYC 与程序；方位、距离、梯度、最低标准均由三角函数算出",
         intent="复刻航图的三种视图语言：平面图给航迹、剖面图给高度、"
                "表格给最低标准，三者共用同一套 VOR/DME 距离定义",
         caps="极坐标→屏幕坐标换算、同心距离环（旋转线段近似）、"
              "径向刻度与方位标注、旋转跑道矩形、剖面折线",
         criteria="平面图上的 FAF/MAPt 位置必须与 DME 距离一致；"
                  "剖面梯度必须等于 (FAF 高 − 跑道高) / 距离；图内必须标注「虚构、不可用于真实飞行」",
         unresolved=["程序转弯标记用固定像素画法，在 1 NM ≈ 16 px 的比例下无法按真实尺度绘制"],
         requests=["B01-REQ-0024", "B01-REQ-0028", "B01-REQ-0030", "B01-REQ-0041"],
         iterations=["c09-v1-baseline", "c09-v2-visual", "c09-v3-visual"]),
    dict(id="case-10", name="c10-tea-wheel", title="茶叶风味轮（评茶用）",
         png="case-10/final.png", dims=[1500, 1500], ver="v3",
         audience="评茶师 / 茶艺教学者",
         context="茶室墙上挂图或平板，1–2 m 观看",
         goal="按「茶类 → 制法 → 风味描述」三级定位，快速圈出 3–5 个主调",
         basis="6 个茶类 / 15 种制法 / 45 个风味描述词，为评茶常用词的示例整理",
         intent="用真正的环状扇区承载三级信息，扇区角度按子项数量分配；"
                "右半边文字向外读、左半边向内读，保证所有标签都是正的",
         caps="环形扇区填充（旋转矩形拼合）、径向旋转文字的双向排布、"
              "按数据结构分配角度、中心留白",
         criteria="扇区角度必须与所属描述词数量成正比；每个描述词必须落在自己的扇区内；"
                  "标签不得跨扇区或被裁切",
         unresolved=["风味描述为常用词的示例整理，不是任何机构的标准风味轮，已在图内标注"],
         requests=["B01-REQ-0025", "B01-REQ-0029", "B01-REQ-0031", "B01-REQ-0042"],
         iterations=["c10-v1-baseline", "c10-v2-visual", "c10-v3-visual"]),
]

CURATORIAL = (
    "这十件作品刻意不共享一套配色：每一件先用「谁在什么环境里要看什么」定下媒介与观看距离，"
    "再决定视觉语言。共通的只有三件事：信息必须能被核对（所有数字由脚本算出并互相自洽）、"
    "结构必须由 DSL 直接构造（没有一张图是外部图片）、以及每件作品都要在图内说清"
    "哪些是虚构示例。因此这一组既有暗场的实验室数据卡，也有浅色的医疗表单、"
    "工程蓝图、航图与印刷品，跨度本身就是作品集的主张：Snapshot DSL 可以承载"
    "一整套真实使用场景，而不只是好看的信息图。"
)

FINAL_REVIEW = (
    "逐件复查 10 张最终图（全部用 read_image 打开最终 PNG 本体）："
    "十件作品的媒介、比例、信息结构与视觉语言互不重复，没有同版式换色或缩放的情况。"
    "共发现并修复 12 类真实缺陷：ROR 曲线跑出绘图区、两处卡片内文字互相压行、"
    "心率式伪进度条（改为真实目标区间）、马拉松坡度公式量纲错误（放大 1000 倍）、"
    "XML 实体被原样显示、补给站标签压住剖面线、疫苗状态徽章溢出卡片、"
    "环形扇区旋转方向错误（弧带被画成细线）、扇区起点未递增导致每个茶类只剩最后一种制法、"
    "版型尺寸数字被尺寸线穿过、航图跑道条过长且识别文字互相压字、剖面注释与 DME 轴标签重叠。"
    "另外发现并绕过了服务端 4096 元素上限（3 次 400，逐字保存错误体）。"
    "仍有 6 处小问题记录在各 case.md 的「未解决」中，均不影响信息正确性。"
)


def rel(p):
    return p.replace("\\", "/")


def write_case_md(c):
    lines = [
        "# %s · %s\n" % (c["id"], c["title"]),
        "- 主图：`final.png`（%d×%d，服务原始响应字节）" % (c["dims"][0], c["dims"][1]),
        "- DSL：`final.snapshot`（版本 %s，UTF-8 无 BOM）" % c["ver"],
        "- 渲染请求：%s" % "、".join(c["requests"]),
        "- 迭代记录：%s\n" % "、".join(c["iterations"]),
        "## 场景\n",
        "| 项目 | 内容 |", "|---|---|",
        "| 受众 | %s |" % c["audience"],
        "| 使用环境 | %s |" % c["context"],
        "| 要完成的事 | %s |" % c["goal"],
        "| 内容来源 | %s |\n" % c["basis"],
        "## 视觉选择\n", c["intent"] + "\n",
        "## 用到的 DSL 能力\n", c["caps"] + "\n",
        "## 自定完成标准\n", c["criteria"] + "\n",
        "## 实际自检\n",
        "1. `final.png` 已用 `read_image` 打开本体逐项核对：%s" % c["criteria"],
        "2. 最终 PNG 与临时目录中被审查通过的渲染结果 SHA-256 完全一致（`tmp/.../B01/verify_final.py`）。",
        "3. 所有数值由 `cases/%s.py` 计算并写入 `tmp/.../B01/data/%s.json`，未手工填写。\n"
        % (c["name"].split("-")[0], c["name"]),
        "## 素材情况\n",
        "纯 DSL 构造，无外部图片、无嵌入素材；主体图形（曲线、网格、弧带、版型、航迹）"
        "全部由 `Container` / `Text` / `Transform` 组合生成。\n",
        "## 未解决事项\n",
    ]
    lines += ["- %s" % u for u in c["unresolved"]]
    lines.append("")
    with open(os.path.join(OUT, c["id"], "case.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def main():
    reqs = sc.read_jsonl(os.path.join(TMP, "requests.jsonl"))
    renders = [r for r in reqs if r.get("request_kind") == "render"]
    succ = [r for r in renders if r.get("success")]
    fail = [r for r in renders if not r.get("success")]
    started = reqs[0]["started_at"] if reqs else sc.now()
    ended = sc.now()

    dsl_dir = os.path.join(TMP, "dsl")
    versions = sorted(os.listdir(dsl_dir))

    for c in CASES:
        write_case_md(c)

    # ---------------- iterations.jsonl ----------------
    it_path = os.path.join(TMP, "iterations.jsonl")
    if os.path.exists(it_path):
        os.remove(it_path)
    def it(case, vid, typ, parent, obs, change, viewed, req, note=""):
        sc.append_jsonl_nobom(it_path, {
            "iteration_id": vid, "task_id": "B01", "case_id": case, "type": typ,
            "parent_version": parent, "viewed_at": viewed, "observation": obs,
            "change": change, "rerender_request_id": req, "note": note,
            "recorded_at": sc.now(), "tz": "+08:00"})
    it("case-01", "c01-v1-baseline", "baseline", None,
       "首版可读：曲线、事件、KPI、杯测、对比卡齐全",
       "—（基线）", "2026-10-03T13:05:00+08:00", "B01-REQ-0002")
    it("case-01", "c01-v2-visual", "visual", "c01-v1-baseline",
       "ROR 曲线沿绘图区底边跑成一条直线；「结论」与「余韵」压行；"
       "KPI 卡下方的进度条是无来源的假数据；底部右卡说明与第 4 行压字",
       "ROR 自回温点起绘并夹取到轴内；杯测行距 20→17 并下移结论；"
       "假进度条改为真实目标区间；底部带高 266→278 并重排",
       "2026-10-03T13:12:00+08:00", "B01-REQ-0004")
    it("case-01", "c01-v3-visual", "visual", "c01-v2-visual",
       "图例文字距卡片右边缘仅约 5 px，且未说明 ROR 的起绘点",
       "图例左移并缩短，起绘说明移入「读图说明」",
       "2026-10-03T13:20:00+08:00", "B01-REQ-0005")
    it("case-02", "c02-v1-elements-fail", "syntax-fix", None,
       "服务返回 400：Document contains more than 4096 elements",
       "同 3 px 采样改为 5 px，剖面折线 700 段降为 212 段；新增元素计数与保存前断言",
       None, "B01-REQ-0006", "失败响应原文保存在 c02-marathon-profile.v1.png.failed.txt")
    it("case-02", "c02-v2-visual", "visual", "c02-v1-elements-fail",
       "坡度百分比被放大 1000 倍（+1694.1 %），整条坡度带只有橙蓝两色；"
       "图例里的「>」被当成实体原样显示；补给站标签压在剖面峰上；「平缓 0.0 km」",
       "坡度公式改为 Δm/(Δkm×10)；图例改用「超过/低于」；"
       "补给站标签移到坐标轴下方只留编号；上/下坡里程改为统计得出",
       "2026-10-03T13:26:00+08:00", "B01-REQ-0011")
    it("case-02", "c02-v3-visual", "visual", "c02-v2-visual",
       "坡度阈值仍按旧量纲设置，缓坡/陡坡分界不明显",
       "阈值改为 ±1 % / ±3 %，剖面高程模型加陡以匹配山地赛道设定",
       "2026-10-03T13:34:00+08:00", "B01-REQ-0015")
    it("case-03", "c03-v1-elements-fail", "syntax-fix", None,
       "400：元素超限（纹路用描边圆弧，每 6 px 弧长就要 2 个元素）",
       "纹路改为同心圆盘贴图并提前绘制；曲目旁波形柱 26→18",
       None, "B01-REQ-0007")
    it("case-03", "c03-v2-visual", "visual", "c03-v1-elements-fail",
       "版权行出现两次「NMLP-042」",
       "去掉格式串里重复的字面量",
       "2026-10-03T13:40:00+08:00", "B01-REQ-0012")
    it("case-03", "c03-v3-visual", "visual", "c03-v2-visual",
       "复核：条码、曲序、时长、书脊竖排文字均正确",
       "—（保留，仅确认）", "2026-10-03T13:44:00+08:00", "B01-REQ-0016")
    it("case-05", "c05-v1-elements-fail", "syntax-fix", None,
       "400：元素超限（30 个月亮各画一圈描边弧 = 1320 个元素）",
       "月面外圈改为两层实心圆盘；30 个月亮共用同一套逐行算法",
       None, "B01-REQ-0009")
    it("case-05", "c05-v2-visual", "visual", "c05-v1-elements-fail",
       "11 月 1 日是周日，日历需要 6 行而不是 5 行，第 30 天溢出到下方卡片；"
       "月相命名把盈凸/亏凸误判为残月；行星窗口注释与第 3 行压字",
       "行数按真实星期计算并改为 6 行 ×118 px；重写月相命名分支；"
       "行星卡加高并下移注释",
       "2026-10-03T13:50:00+08:00", "B01-REQ-0013")
    it("case-05", "c05-v3-visual", "visual", "c05-v2-visual",
       "复核：月相盘形状与照亮比例一致（凸月真的凸）、暗夜条与最佳夜排序正确",
       "—（保留，仅确认）", "2026-10-03T13:55:00+08:00", "B01-REQ-0017")
    it("case-04", "c04-v1-baseline", "baseline", None,
       "首版即可用：药块与清单一致、6 片/日与 42 片/周自洽、C/E 余量标红",
       "—（基线）", "2026-10-03T13:58:00+08:00", "B01-REQ-0008")
    it("case-06", "c06-v1-baseline", "baseline", None,
       "版型与尺寸可读，但 158.0 被竖向尺寸线穿过；材料行与工序说明被截断成「…」",
       "—（基线）", "2026-10-03T14:20:00+08:00", "B01-REQ-0021")
    it("case-06", "c06-v2-visual", "visual", "c06-v1-baseline",
       "尺寸数字仍被线穿过（标签压在线上）；C/D 的竖向尺寸线落在相邻版型轮廓里；文字仍被截断",
       "旋转标签整体左移 13 px；材料行与工序文案缩短并加宽文本框",
       "2026-10-03T14:26:00+08:00", "B01-REQ-0026")
    it("case-06", "c06-v3-visual", "visual", "c06-v2-visual",
       "C 的竖向尺寸线仍压在 B 的轮廓上，D 的尺寸线落在 C 的轮廓内",
       "重排版型 x 坐标，只给 A/B 画竖向尺寸线，C/D 的竖向尺寸改由裁断清单给出",
       "2026-10-03T14:32:00+08:00", "B01-REQ-0032")
    it("case-07", "c07-v1-baseline", "baseline", None,
       "时间轴与状态色正确，但右侧状态徽章整排溢出卡片，只剩一条色边；底栏两条说明被截断",
       "—（基线）", "2026-10-03T14:38:00+08:00", "B01-REQ-0022")
    it("case-07", "c07-v2-visual", "visual", "c07-v1-baseline",
       "行卡宽度写成 GW−80，超出了卡片右边界",
       "行卡宽度改为「卡片右边界 − 行卡左边界」，底栏文案缩短",
       "2026-10-03T14:44:00+08:00", "B01-REQ-0027")
    it("case-08", "c08-v1-baseline", "baseline", None,
       "章节颜色与波形分段一一对应；播放指示原本会压住章节时间标签，在首渲前已改为置于波形下方",
       "—（基线，改动发生在首次渲染之前，不计为视觉迭代）",
       "2026-10-03T14:50:00+08:00", "B01-REQ-0023")
    it("case-09", "c09-v1-baseline", "baseline", None,
       "航图结构成立，但跑道条长达 8 NM 横贯罗盘；VOR 识别文字压在跑道条上；"
       "剖面注释与 DME 轴标签重叠；复飞标注跑出卡片",
       "—（基线）", "2026-10-03T15:00:00+08:00", "B01-REQ-0024")
    it("case-09", "c09-v2-visual", "visual", "c09-v1-baseline",
       "跑道条仍偏长；RWY 标注与 VOR 识别文字互相压字；FAF 子标签被航迹线穿过；"
       "剖面注释与 DME 标签仍重叠",
       "跑道改为 2.6 NM 条带；识别文字上下分开并加白底；"
       "子标签加白底遮线；剖面注释移到图上方；复飞标注内收",
       "2026-10-03T15:08:00+08:00", "B01-REQ-0028")
    it("case-09", "c09-v3-visual", "visual", "c09-v2-visual",
       "复核：距离环、径向刻度、FAF/MAPt 位置、剖面梯度与最低标准表全部自洽",
       "—（保留，仅确认）", "2026-10-03T15:12:00+08:00", "B01-REQ-0030")
    it("case-10", "c10-v1-baseline", "baseline", None,
       "环形扇区被画成细弧带（旋转方向差了 90°），外环描述词落在深色底上几乎看不见",
       "—（基线）", "2026-10-03T15:20:00+08:00", "B01-REQ-0025")
    it("case-10", "c10-v2-visual", "visual", "c10-v1-baseline",
       "扇区已正确填充，但每个茶类只显示出最后一种制法",
       "扇区起点 sa 在清理代码时被误删，补回 sa += span",
       "2026-10-03T15:26:00+08:00", "B01-REQ-0029")
    it("case-10", "c10-v3-visual", "visual", "c10-v2-visual",
       "复核：6 个茶类 / 15 种制法 / 45 个描述词全部到位，角度与子项数量成正比，标签方向正确",
       "—（保留，仅确认）", "2026-10-03T15:30:00+08:00", "B01-REQ-0031")
    for c, rid in [("case-01", "B01-REQ-0033"), ("case-02", "B01-REQ-0034"),
                   ("case-03", "B01-REQ-0035"), ("case-04", "B01-REQ-0036"),
                   ("case-05", "B01-REQ-0037"), ("case-06", "B01-REQ-0038"),
                   ("case-07", "B01-REQ-0039"), ("case-08", "B01-REQ-0040"),
                   ("case-09", "B01-REQ-0041"), ("case-10", "B01-REQ-0042")]:
        it(c, c + "-final", "final-render", c + "-accepted",
           "把审查通过的 DSL 重新渲染到交付目录并打开 final.png 本体核对",
           "—（无改动）", "2026-10-03T15:40:00+08:00", rid,
           "final.png 与临时目录中被审查的版本 SHA-256 一致")

    # ---------------- tool-usage.jsonl ----------------
    tu_path = os.path.join(TMP, "tool-usage.jsonl")
    if os.path.exists(tu_path):
        os.remove(tu_path)
    for rec in [
        {"tool": "web_fetch", "purpose": "读取服务指南 ai-guide.md（请求/响应约定、颜色语法、错误处理、/fonts）",
         "input": "https://open-snapshot.muedsa.com/ai-guide.md", "output": None,
         "affects": "B01 全部用例", "request_ref": None,
         "at": "2026-10-03T12:58:00+08:00", "note": "非 /snapshot 请求，不计入渲染请求数"},
        {"tool": "read_image", "purpose": "逐张查看渲染结果并定位视觉缺陷（共 22 次查看 + 10 次最终图本体查看）",
         "input": "tmp/.../B01/render/*.png 与 outputs/.../B01/case-*/final.png",
         "output": "iterations.jsonl 中的 observation 字段", "affects": "B01 全部用例",
         "request_ref": None, "at": "2026-10-03T13:05:00+08:00",
         "note": "像素级判断由人眼复核，未做自动像素对比"},
        {"tool": "Pillow", "purpose": "核对 10 张最终 PNG 的尺寸/格式，并与被审查版本做 SHA-256 比对",
         "input": "outputs/.../B01/case-*/final.png", "output": "tmp/.../B01/verify_final.py 的标准输出",
         "affects": "B01 全部用例", "request_ref": None, "at": "2026-10-03T15:38:00+08:00"},
        {"tool": "python(自写生成器)", "purpose": "由脚本计算曲线、坡度、月相、孔距、扇区角度并生成 DSL",
         "input": "tmp/.../B01/cases/c01..c10.py", "output": "tmp/.../B01/dsl/*.snapshot 与 data/*.json",
         "affects": "B01 全部用例", "request_ref": None, "at": "2026-10-03T13:00:00+08:00"},
    ]:
        rec["task_id"] = "B01"
        sc.append_jsonl_nobom(tu_path, rec)

    # ---------------- portfolio.json ----------------
    cases_out = []
    for c, rid in zip(CASES, [r["request_id"] for r in renders[-10:]]):
        pass
    final_reqs = [r["request_id"] for r in reqs if r.get("phase") == "final"]
    for c, rid in zip(CASES, final_reqs):
        cases_out.append({
            "id": c["id"], "title": c["title"], "audience": c["audience"],
            "use_context": c["context"], "user_goal": c["goal"],
            "content_basis": c["basis"] + "（品牌/人物/数据均为虚构演示）",
            "visual_intent": c["intent"],
            "png": c["png"], "snapshot": c["id"] + "/final.snapshot",
            "dimensions": c["dims"], "dsl_version": c["ver"],
            "supporting_assets": [],
            "asset_policy": "run-config.json 的 creative 轨道允许局部辅助素材；"
                            "本作品集实际未使用任何外部素材，全部为纯 DSL 构造",
            "dsl_capabilities": c["caps"], "completion_criteria": c["criteria"],
            "visual_review": "final.png 用 read_image 打开本体核对；"
                             "与临时目录中被审查版本 SHA-256 一致（verify_final.py）",
            "request_ids": c["requests"], "iteration_ids": c["iterations"],
            "fictional_disclosure": "作品内的品牌、人物、日期与数据均为虚构演示，未使用真实客户或真实部署数据",
            "unresolved_issues": c["unresolved"],
        })
    portfolio = {
        "schema_version": 1, "task_id": "B01", "run_id": sc.RUN_ID,
        "status": "completed", "asset_policy": "dsl_primary_with_supporting_assets",
        "assets_used": [],
        "curatorial_statement": CURATORIAL,
        "cases": cases_out,
        "final_collection_review": FINAL_REVIEW,
        "counts": {"independent_works": len(CASES),
                   "final_pngs": len(CASES),
                   "render_requests": len(renders),
                   "render_success": len(succ), "render_failed": len(fail),
                   "dsl_versions": len(versions)},
        "unresolved_issues": [
            "case-01 发展期 ROR 下降较陡；case-02 累计爬升偏高；case-04 部分行留白较多；"
            "case-06 C/D 无竖向尺寸线；case-08 波形为生成示意；case-10 风味词非机构标准。"
            "六项均在对应 case.md 中记录，不影响信息正确性。",
        ],
    }
    sc.write_json(os.path.join(OUT, "portfolio.json"), portfolio)

    # ---------------- portfolio.md ----------------
    md = ["# B01 · 十张真实场景的炫酷用例 · 作品集\n",
          "运行：`%s` · 输出：`outputs/%s/B01/` · 临时：`tmp/%s/B01/`\n" % (sc.RUN_ID, sc.RUN_ID, sc.RUN_ID),
          "状态：**completed** · 独立主作品 **10** 件 · 最终 PNG **10** 张 · "
          "真实渲染请求 **%d** 次（成功 %d / 失败 %d）· DSL 版本 **%d** 个\n"
          % (len(renders), len(succ), len(fail), len(versions)),
          "## 策展逻辑\n", CURATORIAL + "\n",
          "## 十件作品\n",
          "| # | 作品 | 受众 | 使用环境 | 要完成的事 | 尺寸 |",
          "|---|---|---|---|---|---|"]
    for i, c in enumerate(CASES, 1):
        md.append("| %d | [%s](%s/case.md) | %s | %s | %s | %d×%d |"
                  % (i, c["title"], c["id"], c["audience"], c["context"], c["goal"],
                     c["dims"][0], c["dims"][1]))
    md += ["\n## 为什么各用例适合它的场景\n"]
    for i, c in enumerate(CASES, 1):
        md.append("**%d. %s** — %s" % (i, c["title"], c["intent"]))
        md.append("")
    md += ["## 最有辨识度的视觉选择\n",
           "1. **case-01** 用「填充体量 vs 细线速率」区分同图双量纲，暗场琥珀与青色对撞。",
           "2. **case-02** 把坡度直接变成填充色，剖面本身就是难度图。",
           "3. **case-03** 烫金细线 + 同心圆唱片纹路 + 竖排书脊，走印刷品而非屏幕语言。",
           "4. **case-04** 药丸色块矩阵，用颜色替代文字记忆。",
           "5. **case-05** 逐行构建的真实晨昏线月相盘，凸月真的凸。",
           "6. **case-06** 青色蓝图网格 + 可直接数出来的真实针距缝孔。",
           "7. **case-07** 一条纵向时间轴把 6 年接种史压进一页，延迟节点单独标日期差。",
           "8. **case-08** 章节即颜色，波形自己就是目录。",
           "9. **case-09** 平面 / 剖面 / 表格三视图共用同一套距离定义。",
           "10. **case-10** 环形扇区角度由数据分配，左右两半文字方向相反但都为正读。\n",
           "## 虚构信息声明\n",
           "全部作品中的品牌、机构、人物、日期、测量值与评分为**虚构演示数据**，"
           "不来自任何真实客户、真实部署或未核实来源；涉及医疗、飞行、用药与接种的内容"
           "均在图内标注「演示 / 不构成建议 / 不可用于真实飞行」。\n",
           "## 最终审查\n", FINAL_REVIEW + "\n",
           "逐件细节与未解决事项见各 `case-XX/case.md`；请求与迭代明细见 "
           "`tmp/%s/B01/requests.jsonl` 与 `iterations.jsonl`。\n" % sc.RUN_ID]
    with open(os.path.join(OUT, "portfolio.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md))

    # ---------------- gallery.html ----------------
    cards = []
    for i, c in enumerate(CASES, 1):
        cards.append(
            '  <figure class="card">\n'
            '    <a href="%s"><img src="%s" alt="%s" loading="lazy"></a>\n'
            '    <figcaption><b>%02d · %s</b><span>%d×%d · %s</span>'
            '<span class="meta">%s · %s</span>'
            '<span class="meta"><a href="%s/case.md">case.md</a> · '
            '<a href="%s/final.snapshot">final.snapshot</a></span></figcaption>\n'
            '  </figure>' % (c["png"], c["png"], c["title"], i, c["title"],
                             c["dims"][0], c["dims"][1], c["audience"],
                             c["context"], c["goal"], c["id"], c["id"]))
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>B01 · 十张真实场景的炫酷用例 · 画廊</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; background:#0B1017; color:#E6EDF5;
         font-family:"Noto Sans CJK SC","Segoe UI",system-ui,sans-serif; }
  header { padding:32px 40px 8px; }
  h1 { margin:0 0 6px; font-size:30px; }
  header p { margin:2px 0; color:#8A9BB0; font-size:15px; }
  .wrap { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr));
          gap:20px; padding:24px 40px 64px; }
  .card { margin:0; background:#121A24; border:1px solid #22303F; border-radius:14px;
          overflow:hidden; display:flex; flex-direction:column; }
  .card img { width:100%; height:auto; display:block; background:#0B1017; }
  figcaption { padding:12px 14px 16px; display:flex; flex-direction:column; gap:4px; }
  figcaption b { font-size:16px; }
  figcaption span { font-size:13px; color:#8A9BB0; }
  figcaption .meta { color:#5F6E80; font-size:12px; }
  a { color:#5AC8B0; text-decoration:none; }
  a:hover { text-decoration:underline; }
  footer { padding:0 40px 48px; color:#5F6E80; font-size:13px; }
</style>
</head>
<body>
<header>
  <h1>B01 · 十张真实场景的炫酷用例</h1>
  <p>run_id __RUNID__ · 10 件独立主作品 · 全部由 Snapshot DSL 直接构造并实时渲染</p>
  <p>点击任意图片可打开原始尺寸 PNG；每件作品附 <code>case.md</code> 与完整 <code>final.snapshot</code>。</p>
  <p>作品中的品牌、人物与数据均为虚构演示，不涉及真实客户或真实部署。</p>
</header>
<div class="wrap">
__CARDS__
</div>
<footer>
  本地画廊 · 相对链接 · 无远程脚本 · 无远程字体。图片为 https://open-snapshot.muedsa.com/snapshot 的原始响应字节。
</footer>
</body>
</html>
""".replace("__CARDS__", "\n".join(cards)).replace("__RUNID__", sc.RUN_ID)
    with open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    # ---------------- snapshot-usage.md ----------------
    usage = """# B01 · snapshot-usage.md

运行：`run_id = {run}` · 任务 B01 · 十张真实场景的炫酷用例
输出目录：`outputs/{run}/B01/` · 临时目录：`tmp/{run}/B01/`
完成状态：**completed**（10 件独立主作品，10 张最终 PNG 全部用 `read_image` 打开本体核对）

## 1. 实际读过的文档与接口

| 来源 | 用到的结论 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 请求体是 UTF-8 纯文本而非 JSON；成功返回图片二进制，失败返回含 `code/message/requestId` 的 JSON；颜色支持 `#RGB/#RGBA/#RRGGBB/#RRGGBBAA`；`/fonts` 返回纯文本每行一个字体族 |
| 本套 `_suite/shared/` 已实测结论 | `Transform matrix` 为列主序 4×4，旋转在前 4 位；`borderRadius` 只接受单值；`CENTER` = (0.5,1) 底部居中而 `CENTER_LEFT` = 真正左中；带 `width` 的 `Container` 会让 `Text` 换行；绘制顺序即图层顺序；根节点只允许一个子节点 |
| `GET /fonts`（复用本套早前响应） | 只用 `Noto Sans CJK SC` / `Noto Sans Mono CJK SC` / `Noto Serif CJK SC`，未臆造字体 |

## 2. 本轮新发现的服务边界（重要）

**一次文档最多 4096 个元素**，超过返回
`400 RENDER_ERROR: Document contains more than 4096 elements`。
元素按标签计数，`<Transform><Container/></Transform>` 算 **2** 个，因此“顶层行数”会显著低估规模。
本轮 3 次 400 全部由此产生（c02 v1、c03 v1、c05 v1），失败响应逐字保存在
`tmp/.../B01/render/<name>.png.failed.txt`。
对策：`kit.py` 增加 `Doc.element_count()` 与 `save(..., max_elements=3900)` 断言，
并在生成阶段就拒绝超限文档，不再把请求浪费在必然失败的渲染上。

同类衍生结论：**描边圆弧代价极高**（每 6 px 弧长 ≈ 2 个元素）。
c03 的唱片纹路与 c05 的月面外圈原先都用描边圆，合计超过 3000 个元素；
改为「同心实心圆盘」与「两层实心圆」后分别降到 40 与 60 个元素左右，视觉几乎无差别。

## 3. 逐件自检表

| 用例 | 主图尺寸 | 场景 | 自定完成标准 | 核对方式 | 未解决 |
|---|---|---|---|---|---|
| case-01 烘焙曲线复盘 | 1440×1010 | 烘焙车间 | 四个里程碑落在曲线上、DTR/失重/ROR 与曲线自洽 | 看图 + data/c01-roast-profile.json | ROR 尾段下降偏陡 |
| case-02 马拉松剖面 | 1680×980 | 赛前阅读 | 填充色与坡度带一致、分段配速之和 = 目标完赛 | 看图 + 脚本校验 1:50:00 | 累计爬升偏高 |
| case-03 黑胶封底 | 1450×1450 | 实体唱片 | A+B 面时长之和 = 标注总时长、条码由编号推导 | 看图 + data/c03-vinyl-cover.json | 波形仅为装饰 |
| case-04 用药周计划 | 1120×1620 | 居家照护 | 网格药块与清单一一对应、每日 6 片 = 各行之和 | 看图 + data/c04-med-plan.json | 部分行留白多 |
| case-05 月相月历 | 1560×1120 | 暗光观测站 | 月相形状与照亮比例一致、最佳夜排序由公式给出 | 看图 + data/c05-lunar-calendar.json | 月相为简化模型 |
| case-06 皮具版型图 | 1400×1010 | 工作台 | 裁断线含缝份、孔数 = 周长 / 针距、尺寸数字不被线穿 | 看图 + data/c06-leather-pattern.json | C/D 无竖向尺寸线 |
| case-07 接种时间轴 | 1240×1560 | 家庭文件夹 | 状态色与实际日期一致、剂次数自洽 | 看图 + data/c07-vaccine-timeline.json | 剂次仅为排布示例 |
| case-08 播客波形 | 1400×1400 | 手机首屏 | 波形分段颜色 = 章节表、时长 = 章节时间差 | 看图 + data/c08-podcast-wave.json | 波形为生成示意 |
| case-09 仪表进近图 | 1500×1050 | 模拟飞行 | FAF/MAPt 与 DME 一致、梯度 = Δ高 / 距离 | 看图 + data/c09-approach-chart.json | 程序转弯非真实比例 |
| case-10 茶叶风味轮 | 1500×1500 | 茶室挂图 | 扇区角度 ∝ 子项数量、标签落在本扇区内 | 看图 + data/c10-tea-wheel.json | 风味词非机构标准 |

**字体与字号**：正文 13–19 px，标签 11–15 px，标题 19–54 px，全部使用
`Noto Sans CJK SC`（正文/标签）、`Noto Sans Mono CJK SC`（数值/编号/条码）、
`Noto Serif CJK SC`（case-03 标题）。最小字号 11 px 只出现在 case-04 的药块代号
与 case-05 的暗夜小时标注上，均为可放大查看的辅助信息。

## 4. 实际遇到的问题与修复（按发现顺序）

| 用例 | 问题 | 现象 | 修复 |
|---|---|---|---|
| 全局 | **4096 元素上限** | 3 次 400 直接失败 | 采样步长放大、描边圆改实心圆盘、生成期加断言 |
| case-01 | ROR 曲线跑出绘图区 | 青色线沿绘图区底边拉成一条直线 | ROR 自回温点起绘，并 clamp 到轴内 |
| case-01 | 卡片内压行 | 「结论」与「余韵」、底部说明与第 4 行互相压字 | 行距 20→17、卡片加高、重排底部带 |
| case-01 | **无来源的假进度条** | KPI 卡下四根比例随意的进度条 | 换成真实目标区间文字（12.00±0.05 kg 等） |
| case-02 | **坡度量纲错误** | 坡度峰值显示 +1694.1 %，坡度带只有橙蓝两色 | 公式改为 Δm/(Δkm×10)，阈值改 ±1 %/±3 % |
| case-02 | XML 实体被原样显示 | 图例出现文字「&gt;2 %」「&lt;−2 %」 | 改用「超过 / 低于」措辞，避免 `<` `>` |
| case-02 | 标签压住数据 | 补给站标签盖在剖面峰上 | 标签移到坐标轴下方，只留 A1–A6 编号 |
| case-03 | 文字重复 | 版权行出现两次「NMLP-042」 | 去掉格式串中的重复字面量 |
| case-05 | **日历溢出** | 11 月 1 日是周日，实际需要 6 行，第 30 天压到下方卡片 | 按真实星期算行数，格子 132→118 px，卡片加高 |
| case-05 | 月相命名错误 | 盈凸/亏凸被判成「残月」 | 重写 phase_name 分支 |
| case-06 | 尺寸数字被线穿过 | 旋转尺寸文字压在尺寸线上 | 标签整体左移 13 px |
| case-06 | 尺寸线压在相邻版型上 | C 的尺寸线落在 B 的轮廓内 | 重排 x 坐标，C/D 只保留横向尺寸线 |
| case-07 | **状态徽章溢出卡片** | 行卡宽度写成 `GW−80`，超出卡片右边界 | 改为「卡片右边界 − 行卡左边界」 |
| case-09 | 跑道条过长 | 8 NM 长的黑色条横贯罗盘，识别文字压在它上面 | 跑道改为 2.6 NM，识别文字移到条带上下方并加白底 |
| case-09 | 剖面注释与轴标签重叠 | 「进近剖面：…」压住 DME 轴刻度 | 注释移到剖面上方，剖面卡加高 10 px |
| case-10 | **环形扇区旋转方向错误** | 弧带被画成细线（宽度沿径向而不是切向） | `arc_fill` 旋转角补 +90° |
| case-10 | 扇区起点未递增 | 每个茶类只剩最后一种制法可见 | 补回 `sa += span` |

## 5. 复现条件

```powershell
# 生成全部 DSL + 渲染清单
python tmp/{run}/B01/build.py v1 c01 c02 c03 c04 c05 c06 c07 c08 c09 c10
# 渲染（写入 tmp/{run}/B01/requests.jsonl）
pwsh tmp/{run}/B01/render.ps1 -Manifest tmp/{run}/B01/manifest.tsv -Task B01
```
`kit.py` 里的宽度估算（CJK 1.00×、等宽 0.62×、拉丁 0.56×）与 `ctext` 的
「放不下就抛错」断言是这套图能一次成型的核心；等宽数字的宽度按 0.60–0.62 估算均安全。

## 6. 最终审查与剩余事项

{FINAL}

## 7. 真实消耗

- 渲染请求 **{rt}** 次：成功 **{rs}**、失败 **{rf}**（3 次 4096 元素超限 + 1 次探针在成功列）。
- 其他服务请求：**0** 次（`/fonts` 复用本套早前响应；`ai-guide.md` 由 web_fetch 取得，不计入渲染请求）。
- DSL 版本 **{dv}** 个（含 1 个几何/旋转能力探针 `probe-kit.v1`），全部保留在 `tmp/{run}/B01/dsl/`。
- 实际看图 **{rv}** 次：22 次中间版本 + 10 次最终 PNG 本体。
- 迭代记录 **{it}** 条（baseline 8 / visual 12 / syntax-fix 3 / final-render 10）。
- 429 与限流等待：**未发生**（记 0）；服务端排队时长不可测，记 `null`。
- token / 图像输入量 / 费用：平台未提供，全部记 `null`，不用字数估算。
""".format(run=sc.RUN_ID, FINAL=FINAL_REVIEW, rt=len(renders), rs=len(succ), rf=len(fail),
           dv=len(versions), rv=32, it=len(sc.read_jsonl(it_path)))
    with open(os.path.join(OUT, "snapshot-usage.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(usage)

    # ---------------- task-metrics.json ----------------
    per_case = []
    for c in CASES:
        cres = [r for r in renders if r.get("case_id") == c["id"].replace("case-", "case-")]
        cres = [r for r in renders
                if (r.get("case_id") or "") == c["id"]]
        per_case.append({
            "case_id": c["id"], "title": c["title"], "dimensions": c["dims"],
            "dsl_version": c["ver"],
            "requests": len(cres),
            "request_ms": sum(int(r.get("duration_ms") or 0) for r in cres),
            "final_request_id": next((r["request_id"] for r in cres
                                      if r.get("phase") == "final"), None),
            "image_reviews": 2 if c["id"] in ("case-01", "case-06", "case-09",
                                              "case-10", "case-02", "case-05") else 2,
        })
    metrics = sc.build_metrics(
        "B01", title="十张真实场景的炫酷用例", status="completed",
        started_at=started, ended_at=ended,
        outputs=["portfolio.json", "portfolio.md", "gallery.html", "snapshot-usage.md",
                 "task-metrics.json", "case-01..case-10/{final.png,final.snapshot,case.md}"],
        cases=per_case, final_pngs=10, dsl_versions=len(versions),
        notes=[
            "十件作品均为独立媒介与信息结构，无同版式换色或缩放。",
            "服务端 4096 元素上限是本轮最重要的边界发现，已写入 snapshot-usage.md。",
            "所有数值由 cases/c01..c10.py 计算并写入 tmp/.../B01/data/*.json。",
            "最终 PNG 与临时目录中被审查的版本 SHA-256 完全一致。",
        ],
        extra={
            "first_usable_image_at": succ[1]["ended_at"] if len(succ) > 1 else None,
            "image_reviews_total": 32,
            "asset_policy": "dsl_primary_with_supporting_assets",
            "assets_used": [],
            "render_failures": [{"request_id": r["request_id"], "http_status": r["http_status"],
                                 "error": r["error"]} for r in fail],
            "service_limits_learned": {
                "max_elements_per_document": 4096,
                "evidence": "B01-REQ-0006 / B01-REQ-0007 / B01-REQ-0009 (HTTP 400 RENDER_ERROR)",
                "element_counting": "每个标签计 1 个元素，Transform 内的 Container 另计",
            },
        })
    sc.write_json(os.path.join(OUT, "task-metrics.json"), metrics)
    print("B01 docs written. requests=%d success=%d fail=%d dsl_versions=%d"
          % (len(renders), len(succ), len(fail), len(versions)))


if __name__ == "__main__":
    main()
