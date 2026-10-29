#!/usr/bin/env python3
import json, os
from pathlib import Path
SCRIPT = Path(__file__).resolve(); SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4])); RUN = SCRIPT.parents[2].name
T = f"tmp/{RUN}"
def write(task, meta):
    p = SUITE_ROOT / "tmp" / RUN / task / "drafts" / "meta.json"; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"); print("meta", task)
docs = [
    {"url": "https://open-snapshot.muedsa.com/ai-guide.md", "knowledge": "POST /snapshot 文本请求、图片响应、错误 JSON、/fonts", "used_in": "渲染"},
    {"url": "https://snapshot.muedsa.com/reference/parser-tags.md", "knowledge": "Container/Stack/Positioned/Transform/Text 与属性限制", "used_in": "全部布局"},
    {"url": "https://snapshot.muedsa.com/reference/parser-text.md", "knowledge": "fontSize/fontStyle/maxLines 与文本换行", "used_in": "标签与注释"},
]
write("A06", {
    "task_id": "A06", "title": "十四节点依赖图与反馈回路", "status": "completed", "stop_reason": "需求满足并完成视觉自检",
    "design": "11 个拓扑层横向排布，同层并行节点上下堆叠；16 条先决边全部从左向右进入更高层，N04→N13 跨层先决用顶部绕行线。2 条反馈边用粉色虚线：N09→N08 从顶部绕回，N10→N08 从底部绕回，均配文字说明且不参与排序。下方三张说明卡给出先决、反馈、并行与最长路径，并加统计标签。",
    "requirements": [
        {"text": "14 节点编号与标签完整", "evidence": "N01–N14 全部出现，节点字号 22"},
        {"text": "16 条先决边方向可辨，不指向过去层", "evidence": "所有 solid 边 layer(to)>layer(from)，箭头从左到右"},
        {"text": "反馈边虚线+专用图例，不画成先决", "evidence": "2 条粉色虚线、图例与文字标注；graph-audit 标记 not_in_topological_sort"},
        {"text": "解释失败回构建与检查后修复", "evidence": "N09→N08、N10→N08 标签与说明卡"},
        {"text": "附 graph-audit.json 层/邻居/最长路径/反馈位置", "evidence": "graph-audit.json 完整"}
    ],
    "files": [{"file": "dependency-map.snapshot", "purpose": "1600×1000 DSL", "dsl": "dependency-map.png", "status": "完成"},
              {"file": "dependency-map.png", "purpose": "最终图", "dsl": "dependency-map.snapshot", "status": "完成"},
              {"file": "graph-audit.json", "purpose": "拓扑审计", "dsl": "-", "status": "完成"}],
    "reviews": [{"image": f"outputs/{RUN}/A06/dependency-map.png", "at": "2026-10-29T11:29:51+0800", "result": "节点/边/反馈/说明全部可读；说明卡略空"},
                {"image": f"outputs/{RUN}/A06/dependency-map.png", "at": "2026-10-29T11:30:07+0800", "result": "补统计标签后平衡，通过"}],
    "iterations": [{"id": "A06-v1", "type": "baseline", "parent": None, "dsl": f"{T}/A06/drafts/gen_a06.py", "image": f"outputs/{RUN}/A06/dependency-map.png", "at": "2026-10-29T11:29:51+0800", "problem": "说明卡空白偏多", "change": "补三组统计标签", "result": "通过"}],
    "issues": [{"type": "syntax", "problem": "图例把 Positioned 放进 Row 导致渲染失败", "cause": "seg() 返回 Stack 子节点用于 Row", "fix": "改用 Container 色条", "verify": "200 渲染", "evidence": "requests.jsonl"}],
    "notes": "分层依赖图用直线边更清晰；跨层边统一走顶部通道，避免穿越节点与文字。",
    "docs": docs,
})
write("A07", {
    "task_id": "A07", "title": "三线换乘图与路线核验", "status": "completed", "stop_reason": "需求满足并完成视觉自检",
    "design": "三条线路按 45°/90° 折线绘制，S04/S05/S08 为双线环换乘站；颜色加线路字母。16 站均可读，无障碍状态用绿点/空心灰点区分并在图例说明。路线按“边数最少、再换乘最少”计算：Q1 6 边 1 换乘（无障碍）、Q2 6 边 1 换乘但在无设施 S05 换乘（不可无障碍，给 6 边 2 换乘替代）、Q3 4 边 1 换乘（无障碍）。旅行卡逐站展示站序、线路段与换乘点。",
    "requirements": [
        {"text": "1600×1000 示意图 + 720×1280 旅行卡", "evidence": "两图尺寸正确，均服务真实响应"},
        {"text": "16 站名称/编号完整、线路折线 45°/90°、非地理声明", "evidence": "16 站标签齐全；页眉“非地理示意图”；线路段均为 45° 或 90°"},
        {"text": "共享站为换乘、交叉无站点不误导", "evidence": "S04/S05/S08 双环；页脚说明交叉无圆环不构成换乘"},
        {"text": "无障碍属性标注与图例", "evidence": "绿点/空心灰点；S03/S05/S09/S14 无设施"},
        {"text": "3 条查询最少边+最少换乘；无障碍替代", "evidence": "routes.json：6/6/4 边，换乘 1/1/1；Q2 替代 6 边 2 换乘"},
        {"text": "routes.json 站序、线路段、边数、换乘", "evidence": "routes.json 完整"}
    ],
    "files": [{"file": "network-map.snapshot", "purpose": "1600×1000 地图 DSL", "dsl": "network-map.png", "status": "完成"},
              {"file": "network-map.png", "purpose": "地图", "dsl": "network-map.snapshot", "status": "完成"},
              {"file": "travel-card.snapshot", "purpose": "720×1280 旅行卡 DSL", "dsl": "travel-card.png", "status": "完成"},
              {"file": "travel-card.png", "purpose": "旅行卡", "dsl": "travel-card.snapshot", "status": "完成"},
              {"file": "routes.json", "purpose": "路线与无障碍核验", "dsl": "-", "status": "完成"}],
    "reviews": [{"image": f"outputs/{RUN}/A07/network-map.png", "at": "2026-10-29T11:31:39+0800", "result": "站点标签被线穿过、S16/S12 标签重叠"},
                {"image": f"outputs/{RUN}/A07/travel-card.png", "at": "2026-10-29T11:32:56+0800", "result": "正文与无障碍说明重叠"},
                {"image": f"outputs/{RUN}/A07/network-map.png", "at": "2026-10-29T11:33:20+0800", "result": "标签底色、换乘子标签、S16 修正后通过"},
                {"image": f"outputs/{RUN}/A07/travel-card.png", "at": "2026-10-29T11:33:16+0800", "result": "卡片增高、正文 20 后全部可见；通过"}],
    "iterations": [{"id": "A07-map-v1", "type": "baseline", "parent": None, "dsl": f"{T}/A07/drafts/gen_a07.py", "image": f"outputs/{RUN}/A07/network-map.png", "at": "2026-10-29T11:31:39+0800", "problem": "标签与线重叠、S16/S12 冲突", "change": "标签底色、移动 S16、删换乘子标签", "result": "通过"},
                   {"id": "A07-card-v1", "type": "visual", "parent": None, "dsl": f"{T}/A07/drafts/gen_a07.py", "image": f"outputs/{RUN}/A07/travel-card.png", "at": "2026-10-29T11:32:56+0800", "problem": "正文重叠", "change": "卡片增高、固定段落位置", "result": "通过"}],
    "issues": [{"type": "syntax", "problem": "旅行卡分段文案色值未插值、缺少 f 前缀", "cause": "字符串拼接使用普通字符串", "fix": "改为 f-string 并预算 bgacc", "verify": "200", "evidence": "requests.jsonl"},
               {"type": "visual", "problem": "地图站名被线路穿过", "cause": "标签无底色且位于线路正上方", "fix": "加半透明底色、移动 S16", "verify": "最终图可读", "evidence": f"outputs/{RUN}/A07/network-map.png"}],
    "notes": "路线 tie-break 必须显式实现为 (边数, 换乘数) 字典序；无障碍约束只在换乘站生效，可乘车通过无设施站。",
    "docs": docs,
})
write("A08", {
    "task_id": "A08", "title": "展馆双路线导览与共享通道", "status": "completed", "stop_reason": "需求满足并完成视觉自检",
    "design": "按 floor.txt 逐格绘制 26×16 网格（单格 36px），墙/通道/门格分色。BFS 求 S→E 与 S→B→D→E，R1 35 步 70 米、R2 47 步 94 米；两段共享通道分别 9 条与 8 条格间边。共享段使用宽蓝实线底 + 窄橙虚线同中心线，箭头按 ±3.5px 偏移，两侧均可追踪；分岔/合流处加标签。S/E 与 A–D 名称进入图例，格心保留字母标记。",
    "requirements": [
        {"text": "1560×1080 双路线导览，26×16 网格与门洞", "evidence": "wayfinding.png 尺寸正确，所有格子/门洞可见"},
        {"text": "单格≥36px、格心坐标与比例尺", "evidence": "36px；1 格=2 米；边缘坐标刻度"},
        {"text": "R1 S→E 与 R2 S→B→D→E 步数/米数", "evidence": "R1 35 步/70m；R2 47 步/94m；分段 19/16/12"},
        {"text": "两条路线可独立追踪，共享段双向可辨", "evidence": "宽蓝底+窄橙虚线；入/离馆共享段各一"},
        {"text": "方向提示（箭头/分岔/合流/转弯）", "evidence": "双色箭头、分岔/合流标签"},
        {"text": "paths.json 格序列/共享段/审计依据", "evidence": "paths.json 与 BFS 复核一致"}
    ],
    "files": [{"file": "wayfinding.snapshot", "purpose": "1560×1080 DSL", "dsl": "wayfinding.png", "status": "完成"},
              {"file": "wayfinding.png", "purpose": "最终图", "dsl": "wayfinding.snapshot", "status": "完成"},
              {"file": "paths.json", "purpose": "路径与绘制审计", "dsl": "-", "status": "完成"}],
    "reviews": [{"image": f"outputs/{RUN}/A08/wayfinding.png", "at": "2026-10-29T11:34:45+0800", "result": "S/E 大标签压线、A–D 名称溢出、图例拥挤"},
                {"image": f"outputs/{RUN}/A08/wayfinding.png", "at": "2026-10-29T11:35:32+0800", "result": "侧栏重构、S/E 标签移除、名称 22px；通过"},
                {"image": f"outputs/{RUN}/A08/wayfinding.png", "at": "2026-10-29T11:35:49+0800", "result": "分岔/合流左移、S/E 名称入图例；最终通过"}],
    "iterations": [{"id": "A08-v1", "type": "baseline", "parent": None, "dsl": f"{T}/A08/drafts/gen_a08.py", "image": f"outputs/{RUN}/A08/wayfinding.png", "at": "2026-10-29T11:34:45+0800", "problem": "标签压线、名称溢出", "change": "移 S/E 标签入图例、A–D 名称 22px 两行", "result": "基本通过"},
                   {"id": "A08-v2", "type": "visual", "parent": "A08-v1", "dsl": f"outputs/{RUN}/A08/wayfinding.snapshot", "image": f"outputs/{RUN}/A08/wayfinding.png", "at": "2026-10-29T11:35:49+0800", "problem": "分岔/合流标签压住路线", "change": "左移标签、补 S/E 名称", "result": "通过"}],
    "issues": [{"type": "render_error", "problem": "图例共享段色块用 Stack 嵌套导致 ProxyWidget 错误", "cause": "Stack 作为行内单子节点组合方式不稳定", "fix": "改用单色条 + 文字说明", "verify": "200", "evidence": "requests.jsonl"},
               {"type": "visual", "problem": "S/E 大标签遮住路线", "cause": "标签放在门格旁且覆盖路线", "fix": "移除地图标签，名称入图例", "verify": "路线连续可追踪", "evidence": f"outputs/{RUN}/A08/wayfinding.png"}],
    "notes": "共享段用宽底+窄虚线是最稳妥的双身份画法；路径长度按格间边，不按像素偏移。",
    "docs": docs + [{"url": "https://snapshot.muedsa.com/reference/parser-tags.md", "knowledge": "Stack 子节点限制与 Transform 矩阵", "used_in": "路线与网格绘制"}],
})
