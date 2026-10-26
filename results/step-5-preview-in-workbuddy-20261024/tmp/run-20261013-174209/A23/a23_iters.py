#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 · 追加 iterations.jsonl（基线 + 完整视觉迭代 + 方案探索 + 重试）。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A23"
TZ = "+08:00"


def ts(hms, base="2026-10-20T"):
    return f"{base}{hms}{TZ}"


RECS = [
    # ---------------- 基线 ----------------
    {
        "version": "A23-v01-baseline", "parent": None, "type": "baseline",
        "images": [
            "tmp/run-20261013-174209/A23/preview/contact-sheet.png",
            "tmp/run-20261013-174209/A23/preview/frame-06-flat.png",
            "tmp/run-20261013-174209/A23/preview/f6_tip_top.png",
            "tmp/run-20261013-174209/A23/preview/f6_inner_ul.png",
            "tmp/run-20261013-174209/A23/preview/f6_center.png",
            "tmp/run-20261013-174209/A23/preview/cover-flat.png"],
        "viewed_at": [ts("19:58:12"), ts("19:58:40")],
        "observed_problems": [
            "五角星描边仅 16px、相对 418px 星体偏细，整体偏“线框”不够“结构”",
            "尖角因圆角 5px 略钝，顶端可见微小分叉",
            "封面标题被拆成“从结构 / 到画面”两行，题面要求“从结构到画面”可读，"
            "连续文案只出现在 19px 页脚，主标题不满足单行连续文案",
            "封面主视觉缩放 1.15，在直径 660 的光晕里显得过小、留白过多",
            "封面标题墨迹右缘 599 与星体左缘 604 只差 5px，间距过近"],
        "changes": "无（首版即基线）",
        "re_view_result": "确认为待改进基线；汇聚方向、单元数量、透明背景均正确",
        "iterations_completed": 0,
    },
    # ---------------- 方案探索：文字测量 ----------------
    {
        "version": "A23-alt01-measure-abandoned", "parent": "A23-v01-baseline",
        "type": "alternative",
        "images": ["tmp/run-20261013-174209/A23/requests.jsonl"],
        "viewed_at": [ts("19:32:00")],
        "observed_problems": [
            "原计划用逐条透明底文字渲染测量封面字宽（a23_measure.py），"
            "9 次 measure 请求中 7 次 60–188s 读超时失败、2 次成功"],
        "changes": "放弃逐条测量方案，改为从最终封面成图实测墨迹盒"
                   "（复测项 C02：在声明盒区域内统计深色墨迹的非透明像素范围）",
        "re_view_result": "改为从成图实测后无需额外请求即得到标题墨迹盒 "
                          "79–599 × 218–300，且可复用于每次封面重渲染",
        "iterations_completed": 0,
    },
    # ---------------- 重试层 ----------------
    {
        "version": "A23-retry01-outer-retry", "parent": "A23-v01-baseline",
        "type": "retry",
        "images": ["tmp/run-20261013-174209/A23/requests.jsonl"],
        "viewed_at": [ts("20:02:00")],
        "observed_problems": [
            "open-snapshot 出现间歇性 60–200s 读超时与 SSL 握手失败；"
            "render.py 内置重试只覆盖 429/503，不覆盖读超时",
            "前台批量渲染被 600s 工具超时中断，frame-01 连续两次失败"],
        "changes": "新增 a23_net.py：更长客户端超时（200s）+ 读超时外层重试，"
                   "每次尝试仍按约定记为一次独立请求；批量渲染改后台执行",
        "re_view_result": "后台重跑后 7/7 全部成功；失败尝试全部保留在 "
                          "requests.jsonl（15 条 error）",
        "iterations_completed": 0,
    },
    # ---------------- 视觉迭代 1 ----------------
    {
        "version": "A23-v02", "parent": "A23-v01-baseline", "type": "visual",
        "images": [
            "tmp/run-20261013-174209/A23/preview/contact-sheet.png",
            "tmp/run-20261013-174209/A23/preview/frame-06-flat.png",
            "tmp/run-20261013-174209/A23/preview/f6_tip2.png",
            "tmp/run-20261013-174209/A23/preview/f6_inner2.png",
            "tmp/run-20261013-174209/A23/preview/cover-flat.png"],
        "viewed_at": [ts("20:17:30"), ts("20:24:05")],
        "observed_problems": [
            "星形仍偏细（基线问题未完全解决）",
            "封面标题已改单行，但主视觉与光晕比例仍不理想",
            "尖角分叉仍在"],
        "changes": [
            "BAR_T 16 → 20（描边加粗，占星体尺度约 4.5%）",
            "BAR_RADIUS 5 → 3（尖角更锐）",
            "CORE_D 48 → 52（中心圆与加粗描边匹配）",
            "封面标题改为单行连续文案“从结构到画面”（88px 粗体），"
            "页脚保留同一连续文案；时间轴 chip 下移到 y=580",
            "HERO_SCALE 1.15 → 1.30，光晕 660 → 700，淡影 alpha 0.16 → 0.13"],
        "re_view_result": "星形明显加粗、结构感成立；封面标题成为单行连续文案；"
                          "尖角分叉减小但仍在 3x 放大下可见",
        "iterations_completed": 1,
    },
    # ---------------- 视觉迭代 2 ----------------
    {
        "version": "A23-v03", "parent": "A23-v02", "type": "visual",
        "images": [
            "tmp/run-20261013-174209/A23/preview/f6_tip2.png",
            "tmp/run-20261013-174209/A23/preview/cover-flat.png"],
        "viewed_at": [ts("20:25:40"), ts("20:46:30")],
        "observed_problems": [
            "3x 放大下星尖仍有约 3–5px 微小分叉（两端圆帽在尖角处不相交）",
            "封面标题墨迹右缘与星体左缘间距仍只有 5px"],
        "changes": [
            "BAR_OV 12 → 13（尖角实体深度 16.1px，两端外沿间距 15.3 < 厚度 20，"
            "保证尖角实体）",
            "BAR_RADIUS 3 → 2（进一步压缩圆帽造成的尖部分叉）",
            "HERO_SCALE 1.30 → 1.24、HERO_C 移到 (890,400)、光晕 700 → 740"],
        "re_view_result": "尖角实体且分叉基本消除；封面标题与主视觉间距拉到约 24px",
        "iterations_completed": 2,
    },
    # ---------------- 视觉迭代 3（仅封面） ----------------
    {
        "version": "A23-v04-cover", "parent": "A23-v03", "type": "visual",
        "images": ["tmp/run-20261013-174209/A23/preview/cover-flat.png"],
        "viewed_at": [ts("20:48:50")],
        "observed_problems": [
            "HERO_C 移到 (890,420) 后星形在光晕内偏下，光晕底部留白过多、"
            "整体下坠"],
        "changes": ["HERO_C y 400 → 420（仅封面）"],
        "re_view_result": "判定不改善，回退该方向并改按星形自身视觉中心对齐",
        "iterations_completed": 3,
    },
    # ---------------- 视觉迭代 4（仅封面） ----------------
    {
        "version": "A23-v05-cover", "parent": "A23-v04-cover", "type": "visual",
        "images": ["tmp/run-20261013-174209/A23/preview/cover-flat.png"],
        "viewed_at": [ts("20:50:10")],
        "observed_problems": [
            "五角星外接框的视觉中心在帧内 y≈280.5（顶点朝上的五角尾星"
            "底部两点更低），与画布中心 300 不重合，直接居中出现偏心"],
        "changes": [
            "HERO_C 改为 (890,438)（补偿星形视觉中心偏移 +19.5px/缩放）",
            "光晕 740 → 660，使星体四边留白约 72–80px 均衡"],
        "re_view_result": "星形在光晕内四边留白均衡，封面构图定稿；"
                          "随后全量复测 0 问题",
        "iterations_completed": 4,
    },
]


def main():
    path = TMP / "iterations.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        for r in RECS:
            r = dict(r)
            r.setdefault("task_id", "A23")
            r.setdefault("path_base", "suite_root")
            r.setdefault("run_id", RUN_ID)
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"appended {len(RECS)} iteration records -> {path}")


if __name__ == "__main__":
    main()
