# -*- coding: utf-8 -*-
"""Append log-repair entries for the two iterations.jsonl lines whose
observation/action were truncated by a PowerShell redirection artifact
(original entries left untouched; reconstruction verified via token_diff.py
on drafts/case-02-v1/v2 and case-04-v1/v2 snapshots)."""
import datetime
import io
import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     ".."))

ENTRIES = [
    {
        "id": "B04-case-02-v2-visual_iteration-logrepair",
        "case_id": "case-02", "version": "v2", "parent_version": "v1",
        "type": "visual_iteration",
        "observation": "[日志修复补记] 原条目#2(2026-10-20T22:39:36)的 observation/action "
                       "被 PowerShell 参数中的 ASCII > 触发重定向截断(action 仅存 "
                       "'&gt;' 残片)。经 token_diff.py 对 drafts/case-02-v1/v2.snapshot "
                       "核对，四缺陷与 v2 改动完整恢复：(1) 正文 ASCII > 被服务 XML 转义"
                       "图上直出 &gt → 改『七处空隙均为正值』；(2) 小行星带分界标签压轴"
                       "(left746.3/top194) → 移 top172 与内外太阳系同排(left776.3,"
                       "width200)；(3) 冥王星数值标签 4436.8→7375.9 压轴端"
                       "(left1496 LEFT) → 移 left1350 右对齐收于轴内；(4) 空隙491.3 "
                       "标签偏左(821.3) → 移 901.3 居中于火星–木星空隙。",
        "action": "[日志修复补记] 原条目 action 丢失；token_diff 显示 6 处 replace "
                  "(三组位置+一组文字)与四缺陷一一对应。v2 于 req-0004 渲染并实看后"
                  "接受为 case-02 最终版(见原条目#2 与 drafts)。原条目未改动，本条"
                  "为追加修复记录。",
    },
    {
        "id": "B04-case-04-v2-visual_iteration-logrepair",
        "case_id": "case-04", "version": "v2", "parent_version": "v1",
        "type": "visual_iteration",
        "observation": "[日志修复补记] 原条目#5(2026-10-20T23:55:26)的 observation "
                       "在『水星标签4222.6』处被截断、action 仅存半句"
                       "('h从967起越过1010的右卡边界被卡片盖住；(3)其余无遮挡。')——"
                       "同一 PowerShell 重定向伪影。经 token_diff.py 对 "
                       "drafts/case-04-v1/v2.snapshot 核对完整恢复：缺陷(1) 金星卡两处"
                       "半角 >/< 被服务转义为 &gt;/&lt;；(2) 太阳日图 AX1=980 时水星"
                       "数值标签 4222.6 h 从 x967.3 起、右缘 1077 越过 1010 右卡边界被"
                       "盖住；(3) 其余无遮挡。",
        "action": "[日志修复补记] v2 改动(token_diff 109 处 replace)：AX1 980→930"
                  "(刻度 217.38/499.94/782.5→215.65/480.32/745，行底 930→924，条轨 "
                  "790→740，太阳日图十行条与标签按新比例全量重算，水星标签止于 "
                  "x918.6+字宽≈975＜1010)+金星卡两处改全角 ＞/＜；23:59 原条目#6 "
                  "记录 v2 复看接受为定版。本条为追加修复记录，原条目未改动。",
    },
]

for e in ENTRIES:
    e["ts"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    e["viewed"] = True
    e["repair_of"] = ("iterations.jsonl 原条目 observation/action 被截断，见 "
                      "tool-usage.jsonl seq 14")
    with io.open(os.path.join(BASE, "iterations.jsonl"), "a",
                 encoding="utf-8") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print("logged", e["id"])
