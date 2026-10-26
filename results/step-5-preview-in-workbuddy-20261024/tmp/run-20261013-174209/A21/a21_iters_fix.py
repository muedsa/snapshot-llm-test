#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加 A21 it07/it08 迭代记录（横版卡片净空缺陷的发现与修复）。"""
import json
import datetime

OUT = "outputs/run-20261013-174209/A21"
TMP = "tmp/run-20261013-174209/A21"


def now_iso():
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="milliseconds")


recs = [
    {"it": "it07", "round": 2, "ts": now_iso(), "type": "audit-defect",
     "parent": "it05",
     "images": [f"{OUT}/round-02/launch-portrait.png",
                f"{OUT}/round-02/launch-wide.png"],
     "observed": ("对比度审计交叉核对时发现横版缺陷：元信息卡第三行"
                  "“赞助方：Northstar Research / 云构工具”的字形墨迹越过卡片底边约 16px，"
                  "压在页面底色上（像素实测：横版卡片底边线在 y=730/731，而该行墨迹一直延伸到 "
                  "y≈740）。竖版卡高 196px 留足净空（墨迹距底边 21px），无此问题。"),
     "root_cause": ("横版 meta_card 卡高写死 164px（第一轮两行文字的尺寸），第二轮新增赞助方"
                    "一行后未重算卡高：20 + (34*1.5+14) + (28*1.5+14) + (26*1.5) = 180，"
                    "已超出 164-20=144 的可用高度。"),
     "change": ("a21_layout.py build_wide：卡高改为按行数计算 "
                "20 + sum(size*1.5 + 14) - 14 + 20，第二轮/第三轮横版为 200px（原 164px）；"
                "第一轮两行仍为 164px，构图不变。"),
     "result": "横版卡片向下增高 36px（567..767），右栏英雄徽标与网址随之下移 18px 并重新居中"},

    {"it": "it08", "round": 3, "ts": now_iso(), "type": "fix-reverify",
     "parent": "it07",
     "images": [f"{OUT}/round-02/launch-portrait.png",
                f"{OUT}/round-02/launch-wide.png",
                f"{OUT}/round-03/launch-portrait.png",
                f"{OUT}/round-03/launch-wide.png"],
     "observed": ("重渲染第二/第三轮横版后，赞助方一行完整落在卡片内；新增复测第 9 项 "
                  "card_text_clearance（卡内最低/最高一段文字墨迹到卡片上下边线的净距 >=8px，"
                  "且起点在卡内的文字段其声明盒不得越过卡片底边）。用旧卡高复现该缺陷时实测 "
                  "bottom clearance=1px 判定 FAIL，证明该检查项有效。"),
     "change": ("a21_verify.py 增加第 9 项 card_text_clearance；"
                "新增 a21_reports.py（从 requests.jsonl 汇总全部渲染尝试含失败重试，"
                "重写四份报告）、a21_retry.py / a21_retry_notext.py（读取超时重试）、"
                "a21_audit.py（不重新渲染、仅用最新辅助图重算对比度审计）。"),
     "result": ("三轮 6 张图 9 项复测全部 0 问题；round-03 对比度审计 24 段文字全部通过，"
                "最低 7.382:1（赞助方一行背景由卡片边线色 #D7DCEA 变为卡片本色 #FFFFFF，"
                "其最差对比度由 6.961 提升至 7.382）。"),
     "visual_review": ("第二/第三轮横版整图 + 元信息卡分区（2x 放大）+ 右栏英雄徽标分区"
                       "实际查看，确认赞助方不再压线、徽标 5 构件与网址位置协调。")},
]

with open(f"{TMP}/iterations.jsonl", "a", encoding="utf-8") as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("appended", [r["it"] for r in recs])
