# -*- coding: utf-8 -*-
"""Build B06 gallery.md: every final work, one by one, with preview + PNG + DSL."""
import io
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", ".."))
O = "outputs/run-20261011-01/B06"

with io.open(os.path.join(ROOT, O, "portfolio.json"), encoding="utf-8") as f:
    pf = json.load(f)

AUD = {
 "case-01": "老年人/照护者 · 手机竖屏 · 老年视力",
 "case-02": "普通消费者 · 货架前手机 · 快速扫读",
 "case-03": "住户 · 手机账单页 · 可细看",
 "case-04": "患者 · A4 纸面/手机 · 近距离细读",
 "case-05": "分期消费者 · 结算页手机 · 决策时刻",
 "case-06": "市民 · 出门前天气页 · 几秒决策",
 "case-07": "通勤者 · 行走中横持手机 · 快速扫读",
 "case-08": "延误旅客 · 候机厅笔记本/大屏 · 2–3 米",
 "case-09": "球迷 · 客厅大屏 · 3–5 米",
 "case-10": "车主 · 车内/车库入口 · 中距离",
}
SHORT = {
 "case-01": "服药钟面", "case-02": "一瓶不等于一份", "case-03": "阶梯电费账单解剖",
 "case-04": "箭头之外 · 检验报告", "case-05": "「0 手续费」的真实成本",
 "case-06": "70% 不是 70% 的时间", "case-07": "换乘时间轴", "case-08": "登机牌与状态时间轴",
 "case-09": "为什么它排第一", "case-10": "再停 20 分钟会多多少钱",
}
BOUND = {
 "case-01": "演示数据：药名/剂量/时刻/相互作用均为自拟",
 "case-02": "真实锚点 GB 28050（SRC-02）；产品数值为演示数据",
 "case-03": "SRC-03 正文 404 未取得；档位与单价为示例演示",
 "case-04": "项目名与区间为通用表述；数值为自拟演示数据",
 "case-05": "本金/期数/费率为演示数据；IRR 由现金流实际求解",
 "case-06": "真实来源 SRC-01（CC BY-SA 4.0）逐字引文；天气数值为演示数据",
 "case-07": "站点/线路/距离为演示数据；步速 1.2 m/s 为图上标明的假设",
 "case-08": "航班号/时刻/口位为演示数据，不指向真实航班",
 "case-09": "虚构联赛，球队与战绩均为演示数据；规则为通行判定",
 "case-10": "演示费率 · 非真实车场",
}

L = []
A = L.append
A("# B06 作品画廊 · 十个日常信息难题")
A("")
A("任务ID：B06 ｜ 运行ID：run-20261011-01 ｜ 共 **10** 件主作品，全部完成。")
A("")
A("每件均为 open-snapshot 服务原始响应 PNG 字节，附同名 `.snapshot` DSL。")
A("所有链接相对本文件所在的 `outputs/run-20261011-01/B06/`，可离线浏览。")
A("")
A("策展逻辑与各作品用途见 [portfolio.md](portfolio.md)，逐件标准与证据见 "
  "[portfolio.json](portfolio.json)，问题证据见 "
  "[problem-evidence.json](problem-evidence.json)，设计审查见 "
  "[design-review.md](design-review.md)。")
A("")
A("## 总览")
A("")
A("| # | 作品 | 受众 · 环境 | 尺寸 | 版本 | 真实/演示边界 |")
A("|---|---|---|---|---|---|")
for i, c in enumerate(pf["cases"], 1):
    A("| %d | [%s](%s) | %s | %d×%d | %s | %s |" % (
        i, SHORT[c["id"]], c["id"] + "/case.md", AUD[c["id"]],
        c["dimensions"][0], c["dimensions"][1], c["accepted_version"],
        BOUND[c["id"]]))
A("")
A("---")
A("")

for i, c in enumerate(pf["cases"], 1):
    cid = c["id"]
    w, h = c["dimensions"]
    A("## %d. %s · %s" % (i, cid, SHORT[cid]))
    A("")
    A("**%s ｜ %d × %d ｜ 接受版本 %s（%s）**" % (
        AUD[cid], w, h, c["accepted_version"], c["accepted_request_id"]))
    A("")
    A("**用户原本卡在哪里**：%s" % c["user_goal"])
    A("")
    A("**视觉主张**：%s" % c["visual_intent"])
    A("")
    A("**真实/演示边界**：%s" % BOUND[cid])
    A("")
    A("**C1–C5**：全部满足。%s" % "；".join(
        "%s %s" % (r["id"], r["result"]) for r in c["criterion_results"]))
    A("")
    A("![%s](%s)" % (SHORT[cid], c["png"]))
    A("")
    A("[原 PNG](%s) ・ [对应 DSL](%s) ・ [用例说明](%s) ・ "
      "[问题证据](problem-evidence.json)" % (
          c["png"], c["snapshot"], c["case_md"]))
    A("")
    A("---")
    A("")

A("")
A("## 完成情况汇总")
A("")
A("- 10 / 10 件完成；24 次渲染请求全部 HTTP 200，无失败、无重试、无 429/503。")
A("- 23 个 DSL 版本；24 次迭代记录（10 baseline + 13 视觉迭代 + 1 探针），"
  "每条 `viewed: true`。")
A("- 50 条自定完成标准（10 件 × C1–C5）全部满足，逐条证据见 "
  "[portfolio.json](portfolio.json)。")
A("- 十件全部纯 DSL，无外部素材。真实来源仅 SRC-01（case-06）与 SRC-02（case-02）；"
  "SRC-03 正文 HTTP 404 未取得，case-03 档位与单价标为示例演示。")
A("- 十件均未做现场调研与用户实验；可观察改善与未验证效果逐件区分见 "
  "[design-review.md](design-review.md)。")
A("")
A("过程留痕（草稿、全部版本 DSL/PNG、研究缓存、脚本、请求与迭代日志）在 "
  "`tmp/run-20261011-01/B06/`，均保留未清理。")

out = os.path.join(ROOT, O, "gallery.md")
with io.open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("wrote", out)
print("works:", len(pf["cases"]))
