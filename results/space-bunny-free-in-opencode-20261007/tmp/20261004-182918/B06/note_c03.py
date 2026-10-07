# -*- coding: utf-8 -*-
"""Append case-03's real visual-iteration records."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R  # noqa: E402

P = os.path.join(R.TMP, "preview", "case.png")
V = "2026-10-05T%s+08:00"
V1 = os.path.join(R.RESP, "resp-B06-req-007-e141c6-att1.txt") if False else None

R.note("case-03", "v01", "none", "baseline",
       os.path.join(R.DRAFTS, "case-03-v001.snapshot"), P, V % "21:40",
       "1500x1224，296 元素。门禁表、标识示意、三台机型卡、回本条都出来了，但看到 3 处硬伤："
       "(1) 右上『中国能效标识』示意里的 5 行字段，键名和值在同一 26px 盒子里上下压在一起，"
       "全部糊成一团灰条，完全读不出字段；(2) warnings 报出页脚第一行需要 2 行却只给 1 行，"
       "实测确认最后一行「本页不是选购建议…」被画布下边缘裁掉；"
       "(3) 三台机型卡与页脚之间有约 110px 空白，信息密度不均衡。",
       "本版留档作为基线；字段重叠与页脚裁切在下一版修", True)

R.note("case-03", "v02", "v01", "visual",
       os.path.join(R.DRAFTS, "case-03-v002.snapshot"), P, V % "21:52",
       "字段行从 5 条压 2 行改为 4 条、行距 31->38（键 11px 在上、值 12px 在下），示意标签可读；"
       "画布 1224->1268 后页脚仍差 6px 被裁，最后一行「本页不是选购建议」看不见；"
       "新增的『两种排序』对比条里，左上标签『按标价排序 · 大多数人这么选』直接压在第一个胶囊上。",
       "字段改为 4 行、行距 38；对比条的标签与注解给出显式 w=190 并把胶囊宽度 168->146、间距 22->18；"
       "画布改 1290、页脚四行改到 H-80/H-60/H-40/H-20",
       False)

R.note("case-03", "v03", "v02", "visual",
       os.path.join(R.DRAFTS, "case-03-v003.snapshot"), P, V % "22:00",
       "整图复查：0 warnings；对比条两张卡的标签/注解/胶囊三段互不重叠；页脚四行完整；"
       "标识示意 4 行字段清晰。同时核对了一遍算式，发现标题写错了——"
       "一级与三级价差 1,000 元，而 10 年电费差是 10,754-8,588 = 2,166 元，"
       "原文案『省下的电费值一千二』与数据不符。",
       "标题改为按实际算出的数字『多花 1,000 元买一级，10 年电费省回 2,166 元』；"
       "对比条胶囊改为单行『等级 + 金额』以适配 44px 高度", True)