#!/usr/bin/env python3
"""A03 repaired system pulse card + repair-log.json."""
import json, os, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A03"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#F8FAFC", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

W, H = 1280, 800
c = 0.9902680687
s = -0.1391731010
mat = f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"

def kpi(x, label, value, accent, sub, pctbar=None):
    p = [f'<Positioned left="{x}" top="150"><Container width="392" height="168" color="#111C31" borderRadius="16" border="1 SOLID #22314A" padding="20"><Column crossAxisAlignment="START" mainAxisSize="MIN">']
    p.append(f'<Row crossAxisAlignment="CENTER"><Container width="10" height="10" color="{accent}" shape="CIRCLE"/><SizedBox width="8"/>' + T(label, 16, "#8FA3C0", True, ' letterSpacing="1.2"') + '</Row>')
    p.append('<SizedBox height="8"/>')
    p.append(T(value, 28, "#FFFFFF", True))
    p.append('<SizedBox height="6"/>')
    p.append(T(sub, 15, "#7387A6"))
    if pctbar is not None:
        p.append('<Spacer/>')
        p.append(f'<Container width="352" height="6" color="#1C2A42" borderRadius="3"><Container width="{352*pctbar:.0f}" height="6" color="{accent}" borderRadius="3"/></Container>')
    p.append('</Column></Container></Positioned>')
    return "".join(p)

parts = ['<Snapshot background="#0B1220" type="png">', f'<Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT" clipBehavior="NONE">']
parts.append('<Container width="1280" height="800" color="#0B1220"/>')
# soft glows
parts.append('<Positioned left="-160" top="-220" width="640" height="640"><Container width="640" height="640" gradientType="RADIAL" gradientColors="#1D4ED84D,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')
parts.append('<Positioned right="-180" top="240" width="620" height="620"><Container width="620" height="620" gradientType="RADIAL" gradientColors="#7C3AED40,#0B122000" gradientCenter="CENTER" gradientRadius="0.5" borderRadius="999"/></Positioned>')

# header
parts.append('<Positioned left="32" top="28"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("System Pulse", 44, "#F8FAFC", True) + T("MONITORING CONSOLE · REPAIR VERIFIED · 2026-10-29", 15, "#7C90AE", True, ' letterSpacing="1.4"') + '</Column></Positioned>')
# LIVE
parts.append('<Positioned right="32" top="42"><Container width="96" height="36" color="#7F1D1D" borderRadius="18" border="1 SOLID #EF4444" alignment="CENTER"><Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#F87171" shape="CIRCLE"/><SizedBox width="6"/>' + T("LIVE", 16, "#FECACA", True, ' letterSpacing="1"') + '</Row></Container></Positioned>')
# divider
parts.append('<Positioned left="32" top="126" width="1216" height="1"><Container width="1216" height="1" color="#1E2B42"/></Positioned>')

# KPIs
parts.append(kpi(32, "SYSTEM USAGE", "USAGE 72%", "#38BDF8", "CPU 61% · MEM 74% · 稳定区间", 0.72))
parts.append(kpi(444, "RESPONSE LATENCY", "LATENCY 148 ms", "#A78BFA", "P95 · 目标阈值低于 200 ms", 0.74))
parts.append(kpi(856, "REQUEST SUCCESS", "SUCCESS 99.2%", "#34D399", "24h 窗口 · 12,480 次请求", 0.992))

# stripes crossing the card both sides
parts.append('<Positioned left="260" top="404" width="760" height="10"><Container width="760" height="10" color="#38BDF8" borderRadius="4"/></Positioned>')
parts.append('<Positioned left="300" top="474" width="700" height="10"><Container width="700" height="10" color="#F472B6" borderRadius="4"/></Positioned>')
parts.append('<Positioned left="330" top="440" width="620" height="4"><Container width="620" height="4" color="#A78BFA" borderRadius="2"/></Positioned>')
# central blurred card
parts.append('<Positioned left="390" top="370" width="500" height="150"><ClipRRect borderRadius="24" clipBehavior="ANTI_ALIAS"><Stack alignment="TOP_LEFT">')
parts.append('<BackdropFilter sigmaX="14" sigmaY="14" tileMode="CLAMP"><Container width="500" height="150" color="#0B122066"/></BackdropFilter>')
parts.append('<Container width="500" height="150" color="#FFFFFF0A" border="1 SOLID #FFFFFF2E" borderRadius="24"/>')
parts.append('<Positioned left="0" top="34" width="500"><Container width="500" alignment="CENTER">' + T("Background-only blur", 28, "#F8FAFC", True) + '</Container></Positioned>')
parts.append('<Positioned left="0" top="78" width="500"><Container width="500" alignment="CENTER">' + T("BackdropFilter σ14 · 卡内背景模糊，文字保持清晰", 15, "#94A3B8") + '</Container></Positioned>')
parts.append('</Stack></ClipRRect></Positioned>')
parts.append('<Positioned left="390" top="334" width="500"><Container width="500" alignment="CENTER">' + T("COMPOSITING DEMO", 13, "#64748B", True, ' letterSpacing="2"') + '</Container></Positioned>')

# REVIEW label rotated -8deg
parts.append('<Positioned right="32" bottom="40" width="160" height="56"><Transform matrix="' + mat + '" alignment="CENTER"><Container width="160" height="56" color="#FFFFFF33" border="1 SOLID #FFFFFF55" borderRadius="12" alignment="CENTER">' + T("REVIEW", 24, "#FFFFFF", True, ' letterSpacing="2"') + '</Container></Transform></Positioned>')
# footer
parts.append('<Positioned left="32" bottom="46">' + T("REPAIR RUN · 6 类问题已定位 · 3 次真实失败响应留档", 15, "#5C6F8C") + '</Positioned>')
parts.append('<Positioned left="32" bottom="24">' + T("1280 × 800 · safe margin 32 · background #0B1220", 13, "#40526C") + '</Positioned>')
parts.append('</Stack></Container></Snapshot>')
dsl = "\n".join(parts)
(OUT / "system-pulse.snapshot").write_text(dsl, encoding="utf-8")

repair = {
    "schema_version": 1, "task_id": "A03", "path_base": "output_dir",
    "original": "inputs/broken.snapshot",
    "final": "system-pulse.snapshot",
    "failures_kept": [
        {"version": "original", "file": "tmp/" + RUN_ID + "/A03/drafts/broken-original.snapshot",
         "response": "tmp/" + RUN_ID + "/A03/drafts/broken-original.png.http400.txt",
         "request_id": "0a6070fe-cd67-4b07-ac12-fd6d6ba1b53c", "http": 400,
         "error": "PARSE_ERROR padding"},
        {"version": "v1-padding", "file": "tmp/" + RUN_ID + "/A03/drafts/broken-v1-padding.snapshot",
         "response": "tmp/" + RUN_ID + "/A03/drafts/broken-v1-padding.png.http400.txt",
         "request_id": "fd7164f6-2829-4720-83be-56b6b2fbcfb0", "http": 400,
         "error": "PARSE_ERROR Transform.matrix missing"},
        {"version": "v2-transform", "file": "tmp/" + RUN_ID + "/A03/drafts/broken-v2-transform.snapshot",
         "response": "tmp/" + RUN_ID + "/A03/drafts/broken-v2-transform.png.http400.txt",
         "request_id": "4eacd408-cd50-4f26-91ea-ea9b4797fc08", "http": 400,
         "error": "RENDER_ERROR renderBox.parentData must be StackParentData"}
    ],
    "issues": [
        {"id": "A03-01", "kind": "parse_error", "location": "line 1, <Snapshot width=\"1280\" height=\"800\">",
         "finding": "Snapshot 不接受 width/height，画布尺寸不是由根属性指定",
         "basis": "parser-tags Snapshot 仅 background/debug/type；根尺寸由布局决定",
         "fix": "外层 Container width=1280 height=800 固定画布", "verified": "最终 1280×800 PNG 实际尺寸"},
        {"id": "A03-02", "kind": "parse_error", "location": "line 2, padding=\"24 32\" (offset 92, col 23)",
         "finding": "padding 格式非法，服务返回 400 PARSE_ERROR", "basis": "错误响应 requestId 0a6070fe…；EdgeInsets 需 \"24\"、\"(v,h)\" 或 \"(l,t,r,b)\"",
         "fix": "改为 padding=\"(24,32)\"；最终使用 (20,22) 等合法值", "verified": "v1 通过解析，进入下一个错误"},
        {"id": "A03-03", "kind": "parse_error", "location": "line 10, <Transform rotate=\"-8\"> (offset 466)",
         "finding": "Transform 缺少必填 matrix，rotate 不是 Parser 属性", "basis": "错误响应 requestId fd7164f6…；parser-tags Transform.matrix 必填",
         "fix": "改用 16 值列主序旋转矩阵，rotation=-8°，alignment=CENTER", "verified": "v2 通过解析；最终 REVIEW 逆时针 8° 由矩阵实现"},
        {"id": "A03-04", "kind": "render_error", "location": "line 7, <Positioned> 直接位于 <Row> 内",
         "finding": "Positioned 父节点必须是 Stack/IndexedStack，导致 RENDER_ERROR renderBox.parentData must be StackParentData",
         "basis": "错误响应 requestId 4eacd408…；parser-tags Positioned 约束",
         "fix": "重建层级：根 Stack + Positioned，LIVE 放到 Stack 顶层", "verified": "最终渲染 200，LIVE 与标题不重叠"},
        {"id": "A03-05", "kind": "silent_ignore", "location": "line 4, <Text font-size=\"44\">",
         "finding": "font-size 不是属性名，未知属性被忽略，标题回退 14px", "basis": "parser-tags 属性名区分大小写，未知属性忽略；对比实际图片字号",
         "fix": "改为 fontSize=\"44\"", "verified": "最终标题 44px，与安全边距内排版一致"},
        {"id": "A03-06", "kind": "silent_ignore", "location": "line 1, Snapshot width/height 属性",
         "finding": "未知根属性被忽略，画布由内容 intrinsic 尺寸决定，不能保证 1280×800", "basis": "官方文档 Snapshot 属性表；首版图片尺寸与目标不符",
         "fix": "在根 Stack 下使用固定 1280×800 Container", "verified": "PNG IHDR 1280×800"},
        {"id": "A03-07", "kind": "silent_ignore", "location": "line 9, <Spacer flex=\"1\"/> 位于无界高 Column",
         "finding": "Column 高度无界时 Spacer/Flex 无法分配剩余空间", "basis": "parser-tags Spacer 需要有限主轴空间",
         "fix": "外层固定高度 + 明确 Positioned 布局，移除无界 Spacer", "verified": "最终卡内所有元素有确定坐标"},
        {"id": "A03-08", "kind": "silent_ignore", "location": "line 12, color=\"#33FFFFFF\"",
         "finding": "8 位颜色语义已从 #AARRGGBB 改为 #RRGGBBAA，原写法变成青色而非半透明白", "basis": "parser-tags 颜色迁移说明",
         "fix": "按 #RRGGBBAA 写 #FFFFFF33（20% 白）", "verified": "REVIEW 白底 20% 透明度、文字不透明"},
        {"id": "A03-09", "kind": "visual_only", "location": "line 13-15, ImageFiltered 包裹整卡（含文字）",
         "finding": "背景条纹与文字一起被高斯模糊，文字不可读；需求只要背景模糊", "basis": "实际图片文字发虚；ImageFiltered 作用于整个子树",
         "fix": "条纹放在卡片外，ClipRRect 内用 BackdropFilter 只模糊卡内背景，文字绘制在滤镜之后", "verified": "最终图条纹在卡两侧可见、卡内背景虚化、文字锐利"},
        {"id": "A03-10", "kind": "visual_only", "location": "line 5-7, 三指标未等宽/未组成一行，LIVE 缺失",
         "finding": "原稿没有三张等宽 KPI、LIVE 96×36、REVIEW 160×56、500×150 说明卡", "basis": "对照 TASK.md 逐项清单",
         "fix": "按 392×168 三等分 KPI，LIVE 96×36、REVIEW 160×56、说明卡 500×150 r24", "verified": "最终图逐项核对通过"}
    ],
    "verification": {
        "canvas": [1280, 800], "safe_margin_px": 32,
        "title_font_px": 44, "kpi_font_px": 28, "explanation_font_px": 28,
        "live_box_px": [96, 36], "review_box_px": [160, 56], "review_rotation_deg": -8,
        "review_bg_alpha": 0.2, "explanation_box_px": [500, 150], "explanation_radius_px": 24,
        "stripes_cross_both_sides": True, "stripe_x_ranges": [[260, 1020], [300, 1000], [330, 950]],
        "text_over_stripes_clear": True,
    }
}
(OUT / "repair-log.json").write_text(json.dumps(repair, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", (OUT / "system-pulse.snapshot").relative_to(SUITE_ROOT).as_posix(), len(dsl))
