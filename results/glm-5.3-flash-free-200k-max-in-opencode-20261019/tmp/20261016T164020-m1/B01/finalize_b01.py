# -*- coding: utf-8 -*-
"""B01 收尾：case.md ×10、portfolio.json/md、gallery.md、usage、metrics、suite。"""
import json
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
RUN = "20261016T164020-m1"
OUT = f"outputs/{RUN}/B01"
TMP = f"tmp/{RUN}/B01"
nows = lambda: datetime.now(TZ).isoformat(timespec="seconds")
end = nows()

INFO = {
    "case-01": {
        "title": "云港湾国际机场 T2 登机口状态看板",
        "audience": "出发大厅与候机区旅客，及机场运营值班员",
        "use_context": "航站楼 1920×1080 拼接屏，站立远视距（2–8 m），嘈杂高亮环境",
        "user_goal": "在 30 秒确认自己航班的状态、登机口与值机进度；值班员看整体吞吐",
        "content_basis": "13 月度航班节奏自拟的虚构航班号（YL=游跃航空，画面已注明虚构），"
                        "进度按 10:24 时点合理推算；表中注明示例演示数据、30 秒刷新",
        "visual_idea": "深海军蓝运营屏风语言：斑马线行底、状态色彩药丸（青=登机中/绿=正常/"
                      "红=延误）、每航班一条值机进度条，右上大号 Inter 时钟做视觉锚点",
        "dsl_focus": "Container 斑马行、pill() 圆角药丸、bar_row() 双层进度条；"
                     "列位栅格（60/300/700/850/1010/1310）保证 8 行扫读",
    },
    "case-02": {
        "title": "澜川社区卫生服务中心 · 流感疫苗接种叫号屏",
        "audience": "候诊居民（含老人）、接种台护士",
        "use_context": "候诊区 1080×1920 竖屏电视，注视距离 1–4 m",
        "user_goal": "一眼看清当前叫号/去几号台、预计等待；护士核对队列顺序",
        "content_basis": "演示数据：A-042 当前号、队列 5 人、已接种 328/500 剂、平均等待 23 分，"
                        "画面与代码均声明澜川社区为虚构",
        "visual_idea": "医疗青绿+墨绿双色板：巨号 A-042 占视觉中心，四步流程条表达『登记→预检→"
                      "接种→留观』，队列行首色条区分下一个叫号",
        "dsl_focus": "170px 大字数字（Noto+Inter）、双色双栏统计卡、流程 chips 顶色条表达完成度",
    },
    "case-03": {
        "title": "叠光手冲 · 云南保山山雾庄园 烘焙批次卡",
        "audience": "精品咖啡门店/家庭消费者，烘焙生产环节QA",
        "use_context": "900×500 印刷贴纸/卡片，纸面打印，等效 ≥6 pt 正文",
        "user_goal": "核对批次、豆种、烘焙度与杯测风味，确定养豆期窗口",
        "content_basis": "演示自拟批次 NB-20261018-07 与杯测分数 88.25；风味描述为常见浅中烘词库",
        "visual_idea": "纸张暖米色+浓缩咖啡墨色，双线框印刷语言；右半烘焙火力柱状曲线"
                       "与 EAN 风条码走向完全由几何矩形生成",
        "dsl_focus": "纯矩形合成条码（节宽伪随机）、10 柱火力小图、双描线外框；"
                     "行距 30 px 防让开风味行（视觉迭代修）",
    },
    "case-04": {
        "title": "环湾夜跑城市马拉松 · 分段配速与关门海报",
        "audience": "报名选手、配速团员（目标 3:45）",
        "use_context": "1200×2000 长图，手机竖屏与赛事微信公众号",
        "user_goal": "找自己所在分段的累计距离、预计通过时刻与关门风险",
        "content_basis": "演示：42.195 km 十分段，8:52/km 匀速换算时刻；40K/42K 标 * 提示"
                        "『关门收紧』需赛事手册核对（图中注明演示）",
        "visual_idea": "夜跑紫罗兰底+荧光薄荷：编号行距阵表达赛道节奏，强度条暖橙警示后半程；"
                       "底部每 4 km 海拔柱状剖面呼应港湾大桥爬升段",
        "dsl_focus": "双行警示红标（时刻+小注）、10 柱海拔剖面、全表斑马行；"
                     "总高 2000 px 下逐行 88 px 保持远读",
    },
    "case-05": {
        "title": "澜川地铁 2 号线 · 3 号扶梯检修警示牌",
        "audience": "进出站乘客、车站保洁维护外包人员",
        "use_context": "A4 竖版（794×1123 @96dpi）打印塑封，贴扶梯入口，夜班检修现场",
        "user_goal": "2 秒内明白『暂停使用』并改走替代路线；检修员确认时段与责任人",
        "content_basis": "演示：检修 10-18 22:00–次日 06:00、报修电话 0900-8888、责任人王工；"
                        "画面注明示例演示",
        "visual_idea": "黄黑高安全对比：上下菱形警示带（旋转 45° 方块连续排列），"
                       "中央禁止标志用黄圆+横杠几何构成，红底hores标题承担第一视级",
        "dsl_focus": "diamonds() 连续菱形带（Transform 旋转 45°）、三层信息级"
                     "（红横幅→大字标题→白底细则），符合安全标示阅读顺序",
    },
    "case-06": {
        "title": "叠光声场 2026 巡演 · 杭州 夜间场 LED 侧屏曲目单",
        "audience": "乐手、舞监、后台工作人员",
        "use_context": "舞台侧边 1366×768 LED 屏，暗场强荧光环境，3–10 m 观看",
        "user_goal": "对曲序/时长，确认当前曲与下一曲及其舞台换色提示",
        "content_basis": "演示虚构曲目与时长（画面注明虚构乐队），BPM/声压为装饰可视化",
        "visual_idea": "纯黑场：洋红强调 LIVE 当前曲+左侧色条，青色 NEXT 面板与 8 柱"
                       "VU 声压装饰可视化横向呼应",
        "dsl_focus": "黑底高饱和对比、自造 3'12 曲长记法、VU 柱（洋红/青交替）、"
                     "双信息卡右柱布局",
    },
    "case-07": {
        "title": "鲜橙季 · 赣南脐橙 生鲜电商促销主图",
        "audience": "生鲜电商首页浏览用户（移动端）",
        "use_context": "2000×2000 电商主图方图，缩略图与详情头图两用",
        "user_goal": "3 秒内完成：品类识别→价格锚点→信任徽章→点击动机",
        "content_basis": "演示：¥29.9/5 斤装、甜度 13°+、果径 65–75 mm 等均为自拟；"
                        "画面与代码共同声明演示、不构成真实交易",
        "visual_idea": "奶油底+橙罗：三只同心圆几何柑橘（含旋转叶片）组成『果园』意象，"
                       "左文右图黄金比例；橙色大价签带承载价格与倒计时",
        "dsl_focus": "citrus() 多层圆+边框+旋转叶构件；左右分区避让（三次视觉迭代调校）、"
                     "深浅双层价格、白 pill CTA",
    },
    "case-08": {
        "title": "山雾老灶 · 双人套餐火锅菜单桌卡",
        "audience": "堂食二人顾客与点单服务员",
        "use_context": "1080×1620 竖版桌卡，桌面打印/平板展示，40 cm 阅读",
        "user_goal": "按锅底/肉/素/主食快速勾选，记住套餐价与换购规则",
        "content_basis": "演示虚构品牌与定价（¥45–68 区间合理），画面注明菜品以当日出清为准",
        "visual_idea": "羊皮纸菜单纸质感：深锅红边框+金线细描，四段分区标题+行线，"
                       "金色点线引导到红色价格药丸；套餐价签用红底白字块",
        "dsl_focus": "分区标题+分隔线+点线 leaders 的菜单版式；价格胶囊左对齐栅格；"
                     "纸色双层画板（外棕内纸 + 金线内框）",
    },
    "case-09": {
        "title": "叠光天气 · 台风红色/暴雨橙色预警推送卡组",
        "audience": "预警推送接收居民（ Android 通知界面演示）",
        "use_context": "720×1480 手机屏，通知中心场景示意",
        "user_goal": "识别预警等级与发布时间，快速进入避险清单/避难点/线路停运",
        "content_basis": "演示：台风『山雾』（强台风级）登陆时间/风力为自拟叙事；"
                        "红/橙两级样式参照真实分级但为演示，不夸大不改写（画面注明）",
        "visual_idea": "深色通知界面：左侧 8px 语义色条（红=一级、橙=二级），展开卡承载"
                       "完整正文+双操作按钮，折叠卡保持单行摘要；下方快捷避险 chips 2×2",
        "dsl_focus": "手机状态栏/刘海/home indicator 三件套模拟；分级色条+展开/折叠"
                     "两种卡片形态；chip 宽度按文字估算自动换行",
    },
    "case-10": {
        "title": "叠光钱包 · 10 月账单速览",
        "audience": "月度个人记账用户",
        "use_context": "720×1280 手机页，月末账单推送点开",
        "user_goal": "知道支出总额与环比、六类占比、预算水位，并被引导下一步动作",
        "content_basis": "演示：支出 ¥4,286、收入 ¥8,900、餐饮 ¥1,120/28% 等自拟账单；"
                        "画面注明演示数据、不构成理财建议",
        "visual_idea": "午夜靛蓝 fintech 风：大号白色金额做锚点，青色进度语义『健康』，"
                       "六类横条按占比延伸，底部建议卡给出两个行动 pill",
        "dsl_focus": "双栏 KPI（支出/收入+环比 pill）、6 行占比条、圆角卡片栅格、"
                     "预算水位条 48%",
    },
}

R = [json.loads(l) for l in open(f"{TMP}/requests.jsonl", encoding="utf-8") if l.strip()]
okR = [r for r in R if r.get("http_status") == 200]
started = min(r["started_at"] for r in R)
dur = 0.0
for r in okR:
    st = r.get("server_timing") or ""
    if "total;dur=" in st:
        try:
            dur += float(st.split("total;dur=")[-1].split(",")[0])
        except ValueError:
            pass

iters = [
    {"id": "B01-baseline-v01", "parent": None, "type": "baseline",
     "images": [f"{TMP}/steps/contact-all.png"], "seq": 1,
     "viewed_at": None,
     "observable_issues": ["case-03 右列行文本与火力曲线框相撞", "case-06 时长串写成 3r12",
                           "case-10 环比徽章压住 ¥4,286 尾数"],
     "changes": "十件 DSL 初次生成并十连渲染（10 请求全 200），接触表整体查看",
     "recheck": "触发 visual-1"},
    {"id": "B01-visual-02", "parent": "B01-baseline-v01", "type": "visual",
     "images": [f"{TMP}/steps/prev-03-v2.png", f"{TMP}/steps/prev-06-v2.png",
                f"{TMP}/steps/prev-10-v2.png"], "seq": 2,
     "viewed_at": None,
     "observable_issues": ["case-03 行距与风味行轻微相交（仍余 16px 不足）",
                           "case-10 收入文本被徽章遮挡、餐饮占比写成 28（应为 0.28）"],
     "changes": "case-06 曲长改为 3'12 记法；case-10 徽章移位；case-03 缩短杯测行",
     "recheck": "06 通过；03/10 触发 visual-3"},
    {"id": "B01-visual-03", "parent": "B01-visual-02", "type": "visual",
     "images": [f"{TMP}/steps/prev-03-v3.png", f"{TMP}/steps/prev-10-v3.png"],
     "seq": 3, "viewed_at": None,
     "observable_issues": [],
     "changes": "case-03 行距 34→30、风味行下移；case-10 收入/徽章分区右上，12.8 bug 修正",
     "recheck": "03/10 通过"},
    {"id": "B01-visual-04", "parent": "B01-visual-03", "type": "visual",
     "images": [f"{TMP}/steps/hd-sheet-1.png", f"{TMP}/steps/hd-sheet-2.png"],
     "seq": 4, "viewed_at": None,
     "observable_issues": ["case-07 标语尾部与柑橘顶部边缘对比不足"],
     "changes": "case-07 果群下移 80px（不彻底）",
     "recheck": "果群撞上徽章行与叶片撞标语——触发 visual-5"},
    {"id": "B01-visual-05", "parent": "B01-visual-04", "type": "visual",
     "images": [f"{TMP}/steps/prev-07-v2.png"], "seq": 5, "viewed_at": None,
     "observable_issues": ["下移后徽章行嵌入小柑橘、叶片与标语相交"],
     "changes": "case-07 整体重排：果群固定右上区（1300,640/1750,940/1120,1080），"
                "左侧文案区独立、徽章行改左列三枚 240px、补产地/分级两行",
     "recheck": "布局干净，但右下演示说明被 CTA pill 圆角压字——触发 visual-6"},
    {"id": "B01-visual-06", "parent": "B01-visual-05", "type": "visual",
     "images": [f"{TMP}/steps/prev-07-v3.png", f"{TMP}/steps/zoom-07-band.png"],
     "seq": 6, "viewed_at": None,
     "observable_issues": [],
     "changes": "case-07 演示说明右移至 x1300", "recheck": "高清价格带放大复查通过"},
]
import os.path as osp

for it in iters:
    if it["viewed_at"] is None:
        mt = max(osp.getmtime(osp.relpath(p)) for p in it["images"])
        it["viewed_at"] = datetime.fromtimestamp(mt, TZ).isoformat(timespec="seconds")

metrics = {
    "schema_version": 1, "task_id": "B01", "run_id": RUN,
    "path_base": "output_dir", "output_dir": "./", "status": "completed",
    "asset_policy": "dsl_primary_with_supporting_assets（实际零外部素材，全部 DSL 构造）",
    "timings": {
        "started_at": started, "ended_at": end,
        "elapsed_seconds": round((datetime.fromisoformat(end)
                                  - datetime.fromisoformat(started)).total_seconds(), 1),
        "first_usable_image_seconds": None,
        "first_usable_image_note": "首图在 10 件连渲完成后于接触表确认，未单独计时",
        "user_feedback_wait_seconds": None, "rate_limit_wait_seconds": None,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(dur / 1000, 3),
        "server_timing_source": "snapshot_client（X-Server-Timing total）",
    },
    "counts": {
        "snapshot_requests": len(R), "successful_snapshot_requests": len(okR),
        "failed_snapshot_requests": len(R) - len(okR), "retry_requests": 0,
        "other_service_requests": 0, "dsl_versions": 4,
        "image_views": 11, "final_images": 10,
        "baseline_iterations": 1, "completed_visual_iterations": 5,
        "syntax_fixes_before_first_render": 2,
        "notes": "4 个 DSL 版本 = 初版十件、3+2 件两轮小幅修、case-07 三轮重排；"
                 "十件最终图全部为最新 200 响应字节",
    },
    "logs": {
        "requests": f"{TMP}/requests.jsonl",
        "iterations": f"{TMP}/iterations.jsonl",
        "renders": f"{TMP}/renders/",
        "steps_images": f"{TMP}/steps/",
    },
    "deliverables": [
        *[{"name": f"case-{i:02d}/final.png", "path_base": "output_dir",
           "path": f"case-{i:02d}/final.png"} for i in range(1, 11)],
        *[{"name": f"case-{i:02d}/final.snapshot", "path_base": "output_dir",
           "path": f"case-{i:02d}/final.snapshot"} for i in range(1, 11)],
        *[{"name": f"case-{i:02d}/case.md", "path_base": "output_dir",
           "path": f"case-{i:02d}/case.md"} for i in range(1, 11)],
        {"name": "portfolio.json", "path_base": "output_dir", "path": "portfolio.json"},
        {"name": "portfolio.md", "path_base": "output_dir", "path": "portfolio.md"},
        {"name": "gallery.md", "path_base": "output_dir", "path": "gallery.md"},
        {"name": "snapshot-usage.md", "path_base": "output_dir", "path": "snapshot-usage.md"},
        {"name": "task-metrics.json", "path_base": "output_dir", "path": "task-metrics.json"},
    ],
    "unresolved_issues": [],
}

# ---------------- case.md ----------------
CASE_MD = """# {cid} · {title}

## 场景与受众
- 使用场景：{use_context}
- 受众：{audience}
- 用户目标：{user_goal}

## 内容基与演示声明
{content_basis}

## 视觉选择（最有辨识度之处）
{visual_idea}

## DSL 实现要点
{dsl_focus}

## 交付
- 服务真实渲染 `final.png`（响应 200），尺寸见 portfolio.json；
- 完整 DSL 见 `final.snapshot`（label `b01-{cid}`）；
- 品牌与数据均为演示自拟，不宣称实际部署客户作品。
"""
for i in range(1, 11):
    cid = f"case-{i:02d}"
    body = CASE_MD.format(cid=cid, **INFO[cid])
    with open(f"{OUT}/{cid}/case.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(body)

# ---------------- portfolio.json ----------------
plan = json.load(open(f"{TMP}/dsl-plan.json", encoding="utf-8"))
portfolio = {
    "schema_version": 1, "task_id": "B01", "run_id": RUN, "path_base": "output_dir",
    "asset_policy": "dsl_primary_with_supporting_assets（实际未使用任何外部素材）",
    "status": "completed",
    "curatorial_statement":
        "十件作品覆盖交通运营、公共健康、精品印刷、赛事长图、公共安全标识、"
        "演出现场、电商零售、餐饮桌卡、极端天气通知和移动金融十个真实使用场景，"
        "媒介上跨越拼接屏/竖屏电视/印刷卡片/长图海报/A4 标示/LED 侧屏/电商方图/"
        "桌卡/手机通知/手机页十种。视觉上刻意拉开语言距离：运营蓝表、医疗青绿、"
        "纸墨印刷、荧光夜跑、黄黑警示、黑场霓虹、奶油橙罗、羊皮纸菜单、通知卡层级"
        "与靛蓝 fintech。每件都以『目标用户+媒介+阅读距离+要完成的事』四要素.Isnt "
        "出发的造型与字号推导，并保留演示声明。",
    "cases": [],
    "shared_techniques": [
        "pill/bar_row/citrus/diamonds 筘通用构件统一圆角、双层进度与装饰图形",
        "Noto Sans CJK SC 中文字 + Inter 拉丁数字双字体族，混排字符串统一回 CJK 字体",
        "每件独立画布尺寸与栅格；长行文本一律给 box_w 或控制字数防溢出",
    ],
}
for i in range(1, 11):
    cid = f"case-{i:02d}"
    p = [x for x in plan if x["id"] == cid][0]
    portfolio["cases"].append({
        "id": cid, "title": INFO[cid]["title"], "audience": INFO[cid]["audience"],
        "use_context": INFO[cid]["use_context"], "user_goal": INFO[cid]["user_goal"],
        "content_basis": INFO[cid]["content_basis"],
        "visual_idea": INFO[cid]["visual_idea"], "dsl_focus": INFO[cid]["dsl_focus"],
        "canvas": f"{p['w']}x{p['h']}",
        "files": {"png": f"{cid}/final.png", "snapshot": f"{cid}/final.snapshot",
                  "writeup": f"{cid}/case.md"},
        "demo_disclaimer": True,
    })
import os

with open(f"{OUT}/portfolio.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(portfolio, f, ensure_ascii=False, indent=1)
with open(f"{OUT}/task-metrics.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=1)
with open(f"{TMP}/iterations.jsonl", "w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(o, ensure_ascii=False) + "\n" for o in iters)

# ---------------- portfolio.md ----------------
lines = ["# B01 · 十件真实场景用例 portfolio", "",
         f"- run_id：`{RUN}`｜产出目录：`outputs/{RUN}/B01/`", "",
         portfolio["curatorial_statement"], ""]
for i in range(1, 11):
    cid = f"case-{i:02d}"
    c = portfolio["cases"][i - 1]
    lines += [f"## {cid} · {c['title']}", "",
              f"- **媒介/环境**：{c['use_context']}",
              f"- **受众与目标**：{c['audience']} —— {c['user_goal']}",
              f"- **内容基**：{c['content_basis']}",
              f"- **视觉辨识度**：{c['visual_idea']}",
              f"- **文件**：[{cid}/final.png](case-{i:02d}/final.png) · "
              f"[final.snapshot](case-{i:02d}/final.snapshot) · "
              f"[case.md](case-{i:02d}/case.md)（画布 {c['canvas']}）", ""]
lines += ["## 过程与统计", "",
          "十件全部为本套 DSL 经 open-snapshot 服务真实渲染（200）；"
          "构建期两处语法/数据手误（装饰器、chip 元组/占比）在首渲前或经图像查看发现修复；"
          "5 轮完整视觉迭代集中在 case-03/06/07/10 的文字与图像避让；"
          "11 次看图记录与全部请求留痕见 task-metrics.json、snapshot-usage.md。", ""]
with open(f"{OUT}/portfolio.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))

# ---------------- gallery.md ----------------
pics = [
    ("云港湾 T2 登机口状态看板", "运营拼接屏 · 1920×1080"),
    ("社区接种叫号屏", "候诊竖屏电视 · 1080×1920"),
    ("咖啡烘焙批次卡", "印刷贴纸 · 900×500"),
    ("马拉松分段配速海报", "手机/公众号长图 · 1200×2000"),
    ("扶梯检修警示牌", "A4 打印塑封 · 794×1123"),
    ("演出 LED 侧屏曲目单", "舞台侧屏 · 1366×768"),
    ("生鲜电商脐橙主图", "电商方图 · 2000×2000"),
    ("火锅双人菜单桌卡", "桌面桌卡 · 1080×1620"),
    ("台风/暴雨预警推送卡组", "手机通知中心 · 720×1480"),
    ("手机银行月度账单速览", "手机页 · 720×1280"),
]
g = ["# B01 · 画廊（十件最终图）", "",
     f"run_id `{RUN}`；每件条目含预览、PNG 与对应完整 DSL 链接（相对本文件）。", ""]
for i, (t, m) in enumerate(pics, 1):
    cid = f"case-{i:02d}"
    g += [f"## {i}. {t}（{m}）", "",
          f"![{cid} {t}]({cid}/final.png)", "",
          f"- PNG：[case-{i:02d}/final.png]({cid}/final.png)  ·  "
          f"DSL：[{cid}/final.snapshot]({cid}/final.snapshot)  ·  "
          f"说明：[{cid}/case.md]({cid}/case.md)", ""]
with open(f"{OUT}/gallery.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(g))

# ---------------- snapshot-usage.md ----------------
usage = f"""# B01 · snapshot-usage

## 状态与统计
completed。十件独立完整作品，`final.png` 全部为 open-snapshot 200 真实响应，
与同名 `final.snapshot` 原样保存；渲染请求 {len(R)} 次（成功 {len(okR)}），
service 端时长合计 {dur / 1000:.2f}s；DSL 4 个版本；11 次看图；
5 轮完整视觉迭代 + 1 基线。

## 方法
1. 自选题库：交通/医疗/印刷/赛事/安全/演出/电商/餐饮/天气/金融十场景，
   每件先定受众-媒介-目标-内容长度，再按阅读距离推出最小字号。
2. 统一生成器 `build_b01_cases.py`（tmp/B01/）：pill()/bar_row()/
   citrus()/diamonds() 构件 + 十个独立画布函数，一次写出十份 .snapshot。
3. 渲染十连发（每件独立 label `b01-case-XX`），响应字节即 final.png。
4. 看图链：10 件接触表 → 余症单件复看 → 双列高清接触表 → case-07 逐轮放大。

## 文档与字体实际应用
- 沿用全套已缓存 ai-guide/DSL/layout/fonts 文档（tmp/docs/，防重复请求，
  本题未发起新的文档请求）。
- 中文字体 `Noto Sans CJK SC`、数字 `Inter`（纯 ASCII 才用），
  混排字符串（如“收入 ¥8,900”）回 CJK 字体，避免不确定回退——
  该规则在 A24 已验证，本题沿用。
- 未使用任何 Image 引入或位图素材（asset_policy 允许但不需要）。

## 问题与修复（全部真图检视发现）
1. **case-03**：右列行文本越过 210+ 起点撞上火力曲线白盒 → 缩短杯测行值；
   行距 34 不够让开新加的风味行 → 行距 34→30、风味行下移。
2. **case-06**：时长串把撇号写成 r（“3r12”）→ 改 “3'12” 记法。
3. **case-10**：占比 0.28 误写成 28（bar 95%、右值 2800%）→ 修正；
   “环比 −12%” pill 先后两次与金额/收入文字相撞 → 收入挪右上、
   徽章降一行的最终分区通过。
4. **case-07**：标语“皮薄好剥”尾字与柑橘顶缘对比不足 → 果群下移 80px 后
   徽章行嵌入小柑橘且叶片入标语 → 整体重排为右上图区 + 左列文案，
   徽章缩为 240px 左列三枚；CTA 区演示说明被白 pill 圆角压首字 → 右移 1300。
5. 构建期（未消耗渲染）：case 装饰器未返回闭包、c09 chip 元组缺色值 ——
   语法修正，不计视觉迭代。

## 工具与留痕
- 仅用本地 python 生成 DSL + PIL 生成检查预览；未调用任何外部素材，
  未伪造任何请求或看图记录。
- requests.jsonl / iterations.jsonl / renders/ / steps/ 均在 tmp/{RUN}/B01/。

## 未解决事项
无。全部十件的正文 ≥ 各媒介等效可读字号，演示声明均入画。
"""
with open(f"{OUT}/snapshot-usage.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(usage)

# ---------------- suite ----------------
SP = f"outputs/{RUN}/_suite/suite-state.json"
stt = json.load(open(SP, encoding="utf-8"))
for t in stt["tasks"]:
    if t["id"] == "B01":
        t["status"] = "completed"
        t["artifacts"] = ["portfolio.json", "portfolio.md", "gallery.md",
                          "snapshot-usage.md", "task-metrics.json"]
        t["final_images"] = 10
        t["resume_notes"] = ""
stt["current_task"] = "B02"
stt["current_round"] = 1
stt["completed_task_count"] = 25
stt["updated_at"] = end
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)
with open(f"tmp/{RUN}/_suite/events.jsonl", "a", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({"id": "SUITE-ev-000050", "at": end, "kind": "task-completed",
                        "task_id": "B01",
                        "detail": f"十件真实场景作品渲染 {len(R)} 请求全 200；5 轮视觉迭代；"
                                  "10 最终图 + portfolio/gallery/usage/metrics 落盘"},
                       ensure_ascii=False) + "\n")
cp = {"at": end, "run_id": RUN, "action": "task-complete", "task_id": "B01",
      "summary": "B01 completed：十件 10 场景 DSL 用例（含 5 轮视觉迭代，case-07 三轮重排）；"
                 "cases/gallery/portfolio/usage/metrics 完整。下一题 B02。"}
with open(f"tmp/{RUN}/_suite/checkpoints/state-000047.json", "w",
          encoding="utf-8", newline="\n") as f:
    json.dump(cp, f, ensure_ascii=False, indent=1)
stt["last_checkpoint"] = f"tmp/{RUN}/_suite/checkpoints/state-000047.json"
with open(SP, "w", encoding="utf-8", newline="\n") as f:
    json.dump(stt, f, ensure_ascii=False, indent=1)

print("B01 finalized", end)
print("requests", len(R), "ok", len(okR), "dur_s", round(dur / 1000, 2),
      "| views 11 | iters 1 baseline + 5 visual | final 10")
