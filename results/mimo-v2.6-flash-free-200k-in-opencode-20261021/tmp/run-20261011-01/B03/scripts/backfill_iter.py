# -*- coding: utf-8 -*-
"""B03 iteration journal backfill for probe + case-01 events (real events,
recorded after the fact; ts = recording time, render times live in
requests.jsonl)."""
import json
import os

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     ".."))

E = [
    ("shared", "probe-01", "probe-01", "probe_fix",
     "probe v1 400: SizedBox/Clip容器仅允许一个子元素——网格阵列直接挂入被拒(PARSE_ERROR给出位置)",
     "clip_*/blur/color_filter改为内部Stack聚合多元素, 并确立裁剪容器内局部坐标约定"),
    ("shared", "probe-01b", "probe-01", "probe",
     "probe-01b 200 首看: SWEEP扫描渐变✓ RADIAL focal偏移✓ BoxShape=CIRCLE边框环✓ ClipOval裁剪网格✓",
     "能力确认: case-03钟盘昼夜带/case-07对称窗花采用SWEEP与Clip"),
    ("shared", "probe-02", "probe-02", "probe_fix",
     "probe v1 400: decoration枚举仅NONE/UNDERLINE/OVERLINE/LINE_THROUGH(服务诊断枚举, 无DASHED)",
     "改用UNDERLINE+decorationLineStyle=DASHED验证虚线下划线"),
    ("shared", "probe-02b", "probe-02", "probe",
     "probe-02b 200 首看: textShadow红青色差重影✓ foregroundMode=STROKE描边字✓ decorationLineStyle=DASHED虚线✓ wordSpacing✓; smcp/tnum在Noto Sans CJK SC无可见效果(边界); 大标题因letterSpacing未计入宽度预算而换行截断",
     "text()宽度预算补计letter_space/word_space; smcp不用于作品(case-06只用色差/描边/字距); 色差手法进入case-06"),
    ("shared", "probe-03", "probe-03", "probe_fix",
     "probe v1 400: ImageFiltered同样单子元素规则(与probe-01同类根因)",
     "blur/color_filter签名改为(x,y,w,h,inner,..)显式区域+局部坐标"),
    ("shared", "probe-03b", "probe-03", "probe",
     "probe-03b 200 首看: ImageFiltered高斯模糊✓ ColorFiltered MULTIPLY混合✓ |dx|=|dy|精确45°段✓ 等距投影iso()✓ 程序化虚线dash_line✓",
     "能力确认: case-04/06用模糊, case-05用等距矩阵, case-09星点辉光用模糊, case-10刀模虚线用手造短划"),
    ("case-01", "v1", None, "syntax_fix",
     "生成失败(未发出请求): 环半径单调断言方向写反——半径随高程递减应为高处更小",
     "断言改为半径随高程严格单调(740<540<380)"),
    ("case-01", "v1", None, "syntax_fix",
     "v1 400: borderRadius不接受百分比写法, 仅接受圆半径或(水平半径,垂直半径)元组(服务diagnostic)",
     "ellipse()改用(rx,ry)元组形式实现椭圆等高线"),
    ("case-01", "v1b", "v1", "baseline",
     "v1b 200 首看: 等高线体系/两线折线/图例/指北/比例尺成立; 缺陷: 图例第4-5行文字重叠、'▲三角点'被绿线穿过、'1:5670'为杜撰比例、h01:56格式生硬",
     "图例加高至210并下移补给点行; 删三角点行(峰点已足够); 删杜撰比例改'虚构演示'; 用时改中文'1 小时 56 分'; 石阶数改为计算值402/0.175≈2,297级"),
    ("case-01", "v2", "v1b", "visual_iteration",
     "v2 200 复看: 图例✓ 三角点✓ 格式✓ 石阶数=计算值2,297✓; 缺陷: 备注列文字逼近表格卡右缘、'两线各穿越10条等高线'仅为假设未经计算",
     "备注列左移940并按列宽预算; 增加逐环3px采样断言: 两线各穿越全部10条环(通过)"),
    ("case-01", "v3", "v2", "visual_iteration",
     "v3 200 终看: 表格全部入卡(备注文字止于x≈1143<卡缘1152, 202.6px超列宽6.6px经看图确认无截断), 采样断言通过, 高程注记/补给点/山门/尺度全部可读",
     "定为交付版 final=case-01-v3"),
]

with open(os.path.join(BASE, "iterations.jsonl"), "a", encoding="utf-8") as f:
    for case, ver, parent, typ, obs, act in E:
        e = {
            "id": "B03-%s-%s-%s" % (case, ver, typ),
            "case_id": None if case == "shared" else case,
            "version": ver,
            "parent_version": parent,
            "type": typ,
            "ts": "2026-10-19T21:00:00+08:00",
            "note": "journal backfill after event; render ts authoritative in requests.jsonl",
            "observation": obs,
            "action": act,
            "viewed": True,
        }
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print("backfilled", len(E), "entries")
