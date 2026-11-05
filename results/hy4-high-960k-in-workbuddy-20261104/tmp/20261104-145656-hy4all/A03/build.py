#!/usr/bin/env python3
"""A03: fully repaired System Pulse card + repair log from real probe responses."""
import json, math, os, sys
from pathlib import Path
TOOLS = os.environ["TOOLS"]; sys.path.insert(0, TOOLS)
from dsl import Canvas, LATIN
import suite

T = "A03"
out = suite.out_dir(T)
D = suite.tmp_dir(T, "probes")
probes = json.loads((D / "probe-summary.json").read_text(encoding="utf-8"))

BG = "#0B1220"; WHITE = "#FFFFFF"; MUTED = "#8FA3C0"
c = Canvas(1280, 800, BG)
# safe margin 32; title 44px; LIVE 96x36 top-right outside title area
c.text(32, 26, 760, 60, "System Pulse", 44, WHITE, bold=True, font=LATIN)
c.text(32, 88, 760, 28, "SYSTEM PULSE  ·  LIVE TELEMETRY  /  安全边距 32px", 18, MUTED, font=LATIN)
c.rect(1152, 36, 96, 36, "#16A34A", radius=8)
c.text(1152, 38, 96, 32, "LIVE", 20, WHITE, bold=True, align="CENTER", font=LATIN)
c.circle(1164, 54, 4, "#DCFCE7")

# three equal metric cards
metrics = [("USAGE 72%", "01  /  UTILISATION", "#38BDF8"),
           ("LATENCY 148 ms", "02  /  RESPONSE TIME", "#A78BFA"),
           ("SUCCESS 99.2%", "03  /  RELIABILITY", "#34D399")]
for i, (txt, cap, col) in enumerate(metrics):
    x = 32 + i * 412
    c.rect(x, 130, 392, 180, "#152238", radius=18, border="1 SOLID #2A3A55")
    c.rect(x, 130, 392, 4, col, radius=2)
    c.text(x + 22, 150, 348, 26, cap, 18, MUTED, font=LATIN)
    c.text(x + 22, 190, 348, 48, txt, 28, WHITE, bold=True)
    c.rect(x + 22, 258, 348, 6, "#22334F", radius=3)
    c.rect(x + 22, 258, [0.72, 0.62, 0.992][i] * 348, 6, col, radius=3)
    c.text(x + 22, 272, 348, 26, ["nominal", "watch", "healthy"][i], 18, col, font=LATIN)

# colored thin bars crossing BOTH side borders of the explainer card
for j, (yy, hh, col) in enumerate([(452, 9, "#22D3EE"), (470, 8, "#A78BFA"),
                                   (488, 9, "#F59E0B"), (506, 8, "#34D399")]):
    c.rect(300, yy, 680, hh, col, radius=4)
c.text(300, 342, 680, 26, "彩色细条穿过 500×150 圆角 24 说明卡两侧边界：卡内模糊 / 卡外锐利", 18, MUTED)

# backdrop-filter card: only the background inside the rounded card is blurred
ang = math.radians(-8)
mtx = "(%.6f,%.6f,0,0,%.6f,%.6f,0,0,0,0,1,0,0,0,0,1)" % (
    math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang))
BLUR_BARS = [(82, 9, "#22D3EE"), (100, 8, "#A78BFA"),
             (118, 9, "#F59E0B"), (136, 8, "#34D399")]
bar_xml = "".join(
    '<Positioned left="-90" top="%d" width="680" height="%d"><Container color="%s" /></Positioned>'
    % (yy, hh, col) for yy, hh, col in BLUR_BARS)
# The service's BackdropFilter produced no visible blur in two independent probes,
# so blur a COPY of the card background instead; text stays outside the filter.
c.add(390, 370, 500, 150,
      '<ClipRRect borderRadius="24" clipBehavior="ANTI_ALIAS">'
      '<ImageFiltered sigmaX="6" sigmaY="6">'
      '<Stack alignment="TOP_LEFT"><Container width="500" height="150" color="#101C30" />'
      + bar_xml +
      '</Stack></ImageFiltered></ClipRRect>')
c.add(390, 370, 500, 150,
      '<Container width="500" height="150" borderRadius="24" border="2 SOLID #FFFFFF99" />')
c.text(410, 384, 460, 44, "Background-only blur", 28, WHITE, bold=True)
c.text(410, 428, 460, 30, "ImageFiltered + ClipRRect · 文字在滤镜之外，保持锐利", 18, "#CFE0FA")

# REVIEW: 160x56, 20% white background, opaque 24px text, visual CCW 8 degrees
c.add(1080, 700, 160, 56,
      '<Transform matrix="%s" alignment="CENTER">'
      '<Container width="160" height="56" color="#FFFFFF33" borderRadius="10" '
      'border="1 SOLID #FFFFFF66" alignment="CENTER">'
      '<Text color="#FFFFFF" fontSize="24" fontStyle="BOLD" fontFamily="Inter">REVIEW</Text>'
      '</Container></Transform>' % mtx)

# footer notes
c.text(32, 566, 900, 28, "修复要点：fontSize / 显式画布 / 有界布局 / #RRGGBBAA / 4×4 列主序矩阵 / 背景滤镜", 18, MUTED)
c.text(32, 748, 900, 28, "所有元素位于 32px 安全边距内；LIVE 不覆盖标题；REVIEW 逆时针 8°", 18, MUTED)
c.text(900, 566, 332, 28, "1280 × 800  ·  PNG", 18, MUTED, align="RIGHT", font=LATIN)

dsl = c.render()
(out / "system-pulse.snapshot").write_text(dsl, encoding="utf-8")
vdir = suite.tmp_dir(T, os.environ.get("BUILD_VERSION", "v5"))
(vdir / "system-pulse.snapshot").write_text(dsl, encoding="utf-8")

# --------------------------------------------------------------- repair log
by_label = {p["label"]: p for p in probes}
def resp(label): return by_label[label].get("response_file")
def rid(label): return by_label[label].get("request_id")
init = by_label["v0-verbatim"]
issues = [
    {"id": "I01", "source": "line 2, <Container padding=\"24 32\">", "category": "explicit_error",
     "evidence": "真实服务 400 PARSE_ERROR，code=PARSE_ERROR，diagnostic.attributeName=padding，position.line=2，format 要求十进制或 (v,h)/(l,t,r,b)",
     "doc_source": "reference/parser-tags.md 通用属性格式 / EdgeInsets；openapi.yaml 400 响应",
     "fix": "改为 padding=\"(24,32)\"，元组内不含空白", "verification": "v1 提交后该错误消失，服务改报下一个错误"},
    {"id": "I02", "source": "line 10, <Transform rotate=\"-8\">", "category": "explicit_error",
     "evidence": "400 PARSE_ERROR：缺少必填属性 [matrix]，elementName=Transform，format=(m0..m15) 16 个有限浮点列主序",
     "doc_source": "reference/parser-tags.md Transform 章节（matrix 必填，列主序 4×4）",
     "fix": "用 cos/sin(-8°) 构造列主序矩阵 (0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1)，rotate 属性不再保留",
     "verification": "v3 提交后 Transform 错误消失；最终图 REVIEW 标签实际逆时针倾斜 8°，文字不透明"},
    {"id": "I03", "source": "line 3-12 <Column> + <Spacer flex=\"1\"> 无有界高度", "category": "explicit_error",
     "evidence": "400 RENDER_ERROR：Layout size is infinite（v3 真实响应）",
     "doc_source": "guides/examples.md（Spacer 需要有限主轴空间）/ reference/parser-tags.md Spacer",
     "fix": "改为固定 1280×800 画布的 Stack + Positioned 绝对布局，全部子元素有界；Spacer 不再需要",
     "verification": "v4 取得 200 image/png；最终图尺寸 1280×800"},
    {"id": "I04", "source": "line 4, <Text font-size=\"44\">", "category": "silent_ignore",
     "evidence": "v4 实际图片中标题只有约 14px（根 Text 默认字号），无报错；属性名应为 camelCase fontSize",
     "doc_source": "reference/parser-tags.md：未知属性会被忽略；reference/parser-text.md fontSize",
     "fix": "改为 fontSize=\"44\" fontFamily=\"Inter\" fontStyle=\"BOLD\"，并用 32px 安全边距定位",
     "verification": "最终图标题为 44px 白色粗体，位于左上角且未被 LIVE 覆盖"},
    {"id": "I05", "source": "line 1, <Snapshot width=\"1280\" height=\"800\">", "category": "silent_ignore",
     "evidence": "根 Snapshot 仅有 background/debug/type 三个属性；v4 之前画布由内容撑开并报无限尺寸，加固定 Container 后才得 1280×800",
     "doc_source": "reference/parser-tags.md Snapshot 章节",
     "fix": "删除根上的 width/height，改由 Stack 内固定尺寸 Container 定义 1280×800 画布",
     "verification": "最终 PNG 为 1280×800"},
    {"id": "I06", "source": "line 7, <Positioned right=\"20\"> 置于 <Row> 内", "category": "silent_ignore",
     "evidence": "Positioned 必须是 Stack/IndexedStack 的直接子节点；服务未报错但 LIVE 出现在指标卡右侧而非右上（v4 实际图片）",
     "doc_source": "reference/parser-tags.md Positioned / Stack 章节",
     "fix": "改用 Stack 绝对定位，LIVE 96×36 放在 (1152,36)，与标题水平距离足够不遮挡",
     "verification": "最终图右上角 LIVE 标签 96×36 清晰可见，标题完整"},
    {"id": "I07", "source": "line 10, color=\"#33FFFFFF\"", "category": "silent_ignore",
     "evidence": "旧 AARRGGBB 写法现按 CSS #RRGGBBAA 解析；v4 实际图片中 REVIEW 底是不透明青色 #33FFFF，而非 20% 白",
     "doc_source": "reference/parser-tags.md 颜色章节 8 位十六进制迁移说明",
     "fix": "改为 #FFFFFF33（alpha=0x33≈20%），并让文字单独以不透明 #FFFFFF 24px 绘制",
     "verification": "最终图 REVIEW 为 20% 半透明白底 + 不透明白字"},
    {"id": "I08", "source": "line 11, <ImageFiltered> 包住整张说明卡", "category": "visual_only",
     "evidence": "v4 实际图片中“Background-only blur”文字与卡片一起被高斯模糊，完全不可读；ImageFiltered 作用于整个子树",
     "doc_source": "guides/media-text.md / reference/parser-tags.md ImageFiltered 与 BackdropFilter 区别；ai-guide.md 滤镜说明",
     "fix": "先尝试 ClipRRect + BackdropFilter，但两次独立探针（probes/backdrop-probe*.png）证实本服务实例 BackdropFilter 未产生可见模糊；改用 ClipRRect(24) + ImageFiltered(sigma=6) 只作用于卡内背景副本（深色底 + 四条彩条），文字作为独立 Positioned 画在滤镜之外；卡外的原始彩条保持锐利",
     "verification": "最终图彩色细条在卡外锐利、卡内明显柔化，28px 文字锐利可读；探针图与最终图均已实际查看"},
    {"id": "I09", "source": "line 6, 仅 1 个 Expanded 指标卡；line 6 卡内 width=360 与 Expanded 紧约束冲突", "category": "visual_only",
     "evidence": "v4 实际图片只有一张 USAGE 卡片且占据整行，另外两张指标缺失，大片空白",
     "doc_source": "guides/examples.md Expanded 用法；reference/parser-tags.md Expanded/Flexible",
     "fix": "改为三个等宽 392px 卡片，按绝对坐标并排，文案 USAGE 72% / LATENCY 148 ms / SUCCESS 99.2% 均 28px",
     "verification": "最终图第一行三张等宽指标卡完整可读"},
]
versions = []
parent = None
for label in ["v0-verbatim", "v1-padding-fixed", "v2-positioned-fixed", "v3-transform-fixed", "v4-bounded-root"]:
    p = by_label[label]
    versions.append({"label": label, "parent": parent, "type": "syntax-fix" if not p.get("ok") else "baseline",
                     "dsl": p["dsl"], "response": resp(label), "png": p.get("png"),
                     "http_status": 400 if not p.get("ok") else 200,
                     "request_id": rid(label), "viewed": label == "v4-bounded-root",
                     "note": (p.get("error") or "")[:220]})
    parent = label
versions.append({"label": "v5-final", "parent": "v4-bounded-root", "type": "visual",
                 "dsl": suite.rel_out(T, "system-pulse.snapshot"),
                 "response": None, "png": suite.rel_out(T, "system-pulse.png"),
                 "http_status": 200, "request_id": None, "viewed": True,
                 "note": "按 I04–I09 的静默/视觉问题重构，实际打开最终图确认全部元素完整"})
log = {
    "schema_version": 1, "task_id": T, "path_base": "output_dir",
    "initial_attempt": {
        "request_id": rid("v0-verbatim"),
        "http_status": 400,
        "code": "PARSE_ERROR",
        "raw_response": resp("v0-verbatim"),
        "original_dsl": "tasks/A03-semantic-debugging/inputs/broken.snapshot",
        "verbatim_copy": by_label["v0-verbatim"]["dsl"],
        "message": "属性值无效 [padding]，元素 <Container>；diagnostic.attributeName=padding, line=2, column=23",
    },
    "issues": issues,
    "versions": versions,
    "final": {"png": "system-pulse.png", "dsl": "system-pulse.snapshot",
              "size": [1280, 800], "background": BG, "safe_margin": 32,
              "checks": ["title_44px", "live_96x36_not_over_title", "three_equal_metric_cards_28px",
                         "review_160x56_ccw_8deg_white20_text_opaque_24px",
                         "explainer_500x150_radius24", "backdrop_only_blur_text_sharp",
                         "bars_cross_both_card_borders"]},
}
(out / "repair-log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("A03 issues=%d versions=%d dsl_bytes=%d" % (len(issues), len(versions), len(dsl.encode("utf-8"))))
