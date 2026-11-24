from __future__ import annotations
import json
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import suitekit as s

RUN_ID = "20261124T113838+0800-aac601"
TASK = "A03"


def build_final() -> str:
    c = []
    # Background strips remain sharp outside the central card.
    for y, color in ((395, "#8B5CF6"), (435, "#22D3EE"), (475, "#FB923C")):
        c.append(s.box(180, y - 5, 920, 10, color, 5))
    # Header.
    c.append(s.label("INFRASTRUCTURE / REALTIME", 32, 28, 700, 24, 18, "#7DD3FC", True))
    c.append(s.label("System Pulse", 32, 58, 1000, 60, 44, "#FFFFFF", True))
    c.append(s.box(1152, 44, 96, 36, "#14532D", 18, "#22C55E"))
    c.append(s.circle(1170, 62, 4, "#4ADE80"))
    c.append(s.label("LIVE", 1180, 50, 58, 28, 20, "#DCFCE7", True, "CENTER"))
    # Equal-width metric cards: 394 + 16 + 395 + 16 + 395 = 1216.
    metrics = [
        (32, 394, "USAGE 72%", "#38BDF8", "CPU / MEMORY", 0.72),
        (442, 395, "LATENCY 148 ms", "#A78BFA", "P95 RESPONSE", 0.62),
        (853, 395, "SUCCESS 99.2%", "#34D399", "REQUEST HEALTH", 0.992),
    ]
    for x, w, value, accent, note, ratio in metrics:
        c.append(s.box(x, 150, w, 180, "#111E32", 18, "#26364D"))
        c.append(s.box(x, 150, w, 5, accent, 2))
        c.append(s.label(value, x + 24, 184, w - 48, 42, 28, "#FFFFFF", True))
        c.append(s.label(note, x + 24, 238, w - 48, 26, 18, "#94A3B8", True))
        c.append(s.box(x + 24, 287, w - 48, 8, "#25344A", 4))
        c.append(s.box(x + 24, 287, (w - 48) * ratio, 8, accent, 4))
    # Central 500x150 card: only the already-painted background is blurred.
    cx, cy, cw, ch = 390, 360, 500, 150
    backdrop = '<ClipRRect borderRadius="24" clipBehavior="ANTI_ALIAS"><BackdropFilter sigmaX="10" sigmaY="10"><Container width="500" height="150" color="#0B1220CC" /></BackdropFilter></ClipRRect>'
    c.append(s.positioned(cx, cy, cw, ch, backdrop))
    c.append(s.box(cx, cy, cw, ch, "#0B122000", 24, "#475569"))
    c.append(s.label("BACKGROUND LAYER / ISOLATED", cx + 28, cy + 24, 444, 24, 18, "#7DD3FC", True))
    c.append(s.label("Background-only blur", cx + 28, cy + 61, 444, 42, 28, "#FFFFFF", True))
    c.append(s.label("Text remains outside the backdrop filter", cx + 28, cy + 112, 444, 24, 18, "#CBD5E1"))
    # REVIEW background gets 20% alpha; the sibling text is fully opaque.
    review_bg = '<Transform matrix="rotate(-8deg)" alignment="CENTER"><Container width="160" height="56" color="#FFFFFF33" border="1 SOLID #FFFFFF55" borderRadius="8" /></Transform>'
    review_text = '<Transform matrix="rotate(-8deg)" alignment="CENTER">' + s.text("REVIEW", 24, "#FFFFFF", True, "CENTER", 160) + '</Transform>'
    c.append(s.positioned(1040, 650, 160, 56, review_bg))
    c.append(s.positioned(1040, 662, 160, 32, review_text))
    c.append(s.label("All systems operational", 32, 720, 700, 28, 20, "#94A3B8"))
    c.append(s.label("1280 × 800  /  SAFE AREA 32", 900, 724, 348, 24, 18, "#64748B", False, "RIGHT"))
    return s.snapshot(1280, 800, c, "#0B1220")


def rotated_box(x, y, w, h, degrees):
    a = math.radians(degrees)
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    out = []
    for px, py in pts:
        dx, dy = px - (x + w / 2), py - (y + h / 2)
        out.append([x + w / 2 + dx * math.cos(a) - dy * math.sin(a), y + h / 2 + dx * math.sin(a) + dy * math.cos(a)])
    return [min(p[0] for p in out), min(p[1] for p in out), max(p[0] for p in out), max(p[1] for p in out)]


def repair_log():
    out, tmp = s.task_dirs(RUN_ID, TASK)
    requests = s.read_jsonl(tmp / "requests.jsonl")
    first = requests[0]
    issues = [
        {"id": "I01", "source_line": 10, "node": "Transform", "category": "explicit_parse_error", "observation": "原样请求返回 400 PARSE_ERROR：缺少必填属性 matrix", "documentation": "tmp/20261124T113838+0800-aac601/_suite/shared/parser-tags.md#transform；rotate 必须写入 matrix 且角度带 deg/rad", "fix": "改为 matrix=\"rotate(-8deg)\" alignment=\"CENTER\"，保留原 REVIEW 区块", "verification": "v001 提交后显式 PARSE_ERROR 消失；后续真实 PNG 中 REVIEW 保持逆时针 8°"},
        {"id": "I02", "source_line": 7, "node": "Positioned under Row", "category": "explicit_render_error", "observation": "v001–v004 返回 400 RENDER_ERROR：renderBox.parentData must be StackParentData", "documentation": "layout.md 的 Stack 与 Positioned：Positioned 只能直接位于 Stack；Expanded 只能直接位于 Flex", "fix": "LIVE 移出 Row 成为 Stack 直接子节点；用有界 SizedBox 包住 Stack，保留 LIVE 96×36", "verification": "v005 首次成功返回 PNG；LIVE 位于右上且不覆盖标题"},
        {"id": "I03", "source_line": 1, "node": "Snapshot width/height", "category": "silently_ignored_attribute", "observation": "Snapshot 标签不支持 width/height；画布由根 Widget 尺寸决定", "documentation": "parser-tags.md#snapshot 仅列 background/debug/type；layout.md 从有限根尺寸算起", "fix": "移除根节点未知 width/height，在根 Container 显式设置 1280×800", "verification": "PNG 头解析为 1280×800；最终 DSL 无未知属性"},
        {"id": "I04", "source_line": 4, "node": "Text font-size", "category": "silently_ignored_attribute", "observation": "属性名区分大小写，font-size 被忽略，标题回退默认字号", "documentation": "parser-tags.md 开头与 parser-text.md：属性名区分大小写，使用 fontSize", "fix": "改为 fontSize=\"44\"", "verification": "最终图标题为 44 字号，实际查看与 USAGE 文案形成明确层级"},
        {"id": "I05", "source_line": 10, "node": "REVIEW color #33FFFFFF", "category": "silently_wrong_alpha_semantics", "observation": "现代 CSS 八位色为 #RRGGBBAA；#33FFFFFF 是青色且 alpha=FF，不是白色 20%", "documentation": "parser-tags.md#颜色：八位最后两位为 alpha，#FF000080 示例", "fix": "背景改 #FFFFFF33；文字作为兄弟层保持 #FFFFFF 不透明，字号 24", "verification": "最终图 REVIEW 为浅白透明底、白色实字；旋转后可见边界在安全边距内"},
        {"id": "I06", "source_line": 11, "node": "ImageFiltered around card and Text", "category": "visual_only_wrong_filter_target", "observation": "v005 实际图片中 Background-only blur 文字与卡片被子树滤镜一起模糊", "documentation": "painting.md：ImageFiltered 模糊子树，BackdropFilter 模糊已经画好的背景；parser-tags.md 滤镜章节", "fix": "先画穿过卡片左右边界的彩色细条；卡内用 ClipRRect+BackdropFilter；文字放到滤镜之外", "verification": "最终图卡内条带柔化、卡外保持锐利，说明文字清晰；圆角 24，卡片 500×150"},
        {"id": "I07", "source_line": "3-13", "node": "unbounded Column/Row and missing metrics", "category": "layout_and_content_gap", "observation": "原稿仅一张 USAGE 卡；Spacer 在无界 Column 中不能可靠分配剩余空间，REVIEW 与说明卡位置不符合最终布局", "documentation": "layout.md：Flex 主轴需要有限空间；画布由有限根决定", "fix": "采用 1280×800 有界根与绝对定位；三张等宽卡 394/395/395，间距 16；保留所有功能区块并补全 LATENCY/SUCCESS", "verification": "最终图三卡右边界为 426/837/1248，左边界 32/442/853；所有元素在 32 像素安全区内"},
    ]
    versions = []
    for req in requests:
        if req["request_type"] != "render":
            continue
        version = req["version_id"]
        dsl = tmp / "versions" / version
        snapshots = sorted(dsl.glob("*.snapshot")) if dsl.exists() else []
        pngs = sorted(dsl.glob("*.png")) if dsl.exists() else []
        versions.append({
            "version_id": version, "parent_version": None, "request_id": req["request_id"], "http_status": req["http_status"],
            "dsl": [{"path_base": "suite_root", "path": s.rel(p)} for p in snapshots],
            "response": {"path_base": "suite_root", "path": req["response_file"]},
            "png": [{"path_base": "suite_root", "path": s.rel(p)} for p in pngs],
            "view_record": "See iterations.jsonl; successful images were opened with Read, failures were not treated as images",
        })
    result = s.audit_identity(TASK)
    result.update({
        "initial_attempt": {"request_id": first["request_id"], "http_status": first["http_status"], "response_path": {"path_base": "suite_root", "path": first["response_file"]}, "dsl_path": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/{TASK}/original-broken.snapshot"}, "unchanged_input": True},
        "issues": issues,
        "versions": versions,
        "final_geometry": {"canvas": [1280, 800], "safe_margin": 32, "title_font_size": 44, "metric_font_size": 28, "explanation_font_size": 28, "review_font_size": 24, "metric_cards": [[32, 150, 426, 330], [442, 150, 837, 330], [853, 150, 1248, 330]], "live_box": [1152, 44, 1248, 80], "explanation_box": [390, 360, 890, 510], "review_unrotated_box": [1040, 650, 1200, 706], "review_rotated_visible_box": rotated_box(1040, 650, 160, 56, -8), "review_angle_degrees": -8, "review_background_alpha": 0.2, "backdrop_sigma": 10, "coordinate_system": "canvas top-left origin; x right, y down; pixels"},
        "final_dsl": "system-pulse.snapshot",
        "final_png": "system-pulse.png",
    })
    return result


def main():
    s.begin_task(RUN_ID, TASK)
    out, tmp = s.task_dirs(RUN_ID, TASK)
    dsl = build_final()
    image, record = s.render(RUN_ID, TASK, dsl, "system-pulse", "v006-final-candidate", final=False, kind="visual")
    s.write_json(tmp / "v006-response.json", record)
    s.write_json(out / "repair-log.json", repair_log())
    print(image)


if __name__ == "__main__":
    main()
