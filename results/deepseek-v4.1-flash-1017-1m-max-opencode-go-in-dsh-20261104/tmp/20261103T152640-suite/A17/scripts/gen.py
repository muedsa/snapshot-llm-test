# -*- coding: utf-8 -*-
"""A17 v3: handbook pages + examples with correct Positioned wrappers."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A17"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)

BG = "#FBFAF7"
INK = "#12161C"
INK2 = "#39424F"
MUTED = "#6E7885"
ACCENT = "#C2410C"
CODE_BG = "#121A26"
CODE_INK = "#DCE6F2"
FONT = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
W, H = 1200, 1600

def cw(ch, size):
    o = ord(ch)
    if o >= 0x2E80:
        return 0.99 * size
    if ch.isdigit():
        return 0.585 * size
    if ch.isupper():
        return 0.675 * size
    if ch.islower():
        return 0.527 * size
    return 0.42 * size

def tokens(text):
    out, buf = [], ""
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch in "&<>+-/%.:"):
            buf += ch
        else:
            if buf:
                out.append(buf); buf = ""
            out.append(ch)
    if buf:
        out.append(buf)
    return out

def wrap(text, size, maxw):
    lines, cur = [], ""
    for tk in tokens(text):
        cand = cur + tk
        if cur and sum(cw(c, size) for c in cand) > maxw:
            lines.append(cur.rstrip())
            cur = "" if tk == " " else tk
        else:
            cur = cand
    if cur.strip():
        lines.append(cur.rstrip())
    return lines

def P(l, t, inner):
    return f'<Positioned left="{l}" top="{t}">{inner}</Positioned>'

def core1(dx, dy):
    x, y = dx, dy
    return [
        P(x + 20, y + 20, '<Container width="360" height="96" color="#16202E"/>'),
        P(x + 40, y + 38, '<Text fontSize="26">200 image/png</Text>'),
        P(x + 40, y + 76, '<Text fontSize="18">1812043 bytes 0.94 s</Text>'),
        P(x + 28, y + 46, '<Container width="10" height="10" color="#34D399"/>'),
        P(x + 20, y + 132, '<Container width="360" height="56" color="#16202E"/>'),
        P(x + 36, y + 148, '<Text fontSize="16">requestId 7f3c-9a21</Text>'),
    ]

def core2(dx, dy):
    x, y = dx, dy
    return [
        P(x + 20, y + 18, '<Container width="360" height="76" color="#16202E"/>'),
        P(x + 32, y + 30, '<Container width="104" height="52" color="#2563EB"/>'),
        P(x + 148, y + 30, '<Container width="104" height="52" color="#0F766E"/>'),
        P(x + 264, y + 30, '<Container width="104" height="52" color="#B45309"/>'),
        P(x + 20, y + 110, '<Container width="360" height="112" color="#16202E"/>'),
        P(x + 44, y + 130, '<Container width="120" height="72" color="#334155"/>'),
        P(x + 96, y + 150, '<Container width="120" height="72" color="#475569"/>'),
        P(x + 240, y + 150, '<Text fontSize="18">bounded</Text>'),
    ]

def core3(dx, dy):
    x, y = dx, dy
    return [
        P(x + 20, y + 14, '<Container width="360" height="56" color="#FFFFFF"/>'),
        P(x + 20, y + 14, '<Container width="196" height="56" color="#2563EB80"/>'),
        P(x + 232, y + 30, '<Text fontSize="18">50% blue</Text>'),
        P(x + 20, y + 84, '<Text fontSize="20"><![CDATA[A < B & C > D]]></Text>'),
        P(x + 20, y + 116, '<Text fontSize="20"><Raw>batch   07</Raw></Text>'),
        P(x + 318, y + 86, '<Container width="54" height="40" color="#FFFFFF33"/>'),
    ]

def core4(dx, dy):
    x, y = dx, dy
    out = []
    for lx in (20, 80, 140, 200, 260, 320):
        out.append(P(x + lx, y + 30, '<Container width="28" height="180" color="#0EA5E9"/>'))
    out.append(f'<Positioned left="{x+90}" top="{y+62}">')
    out.append('  <SizedBox width="220" height="116"><ImageFiltered sigmaX="6" sigmaY="6">')
    out.append('    <Container width="220" height="116" color="#2563EB" borderRadius="18"/>')
    out.append('  </ImageFiltered></SizedBox></Positioned>')
    out.append(P(x + 100, y + 104, '<Text fontSize="20">SHARP</Text>'))
    return out

CORES = {1: core1, 2: core2, 3: core3, 4: core4}

def example_lines(n):
    lines = ['<Snapshot background="#0B1220" type="png">',
             '  <Container width="400" height="240">',
             '    <Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">']
    for el in CORES[n](0, 0):
        lines.append("    " + el)
    lines += ["    </Stack>", "  </Container>", "</Snapshot>"]
    return lines

EXAMPLES = {n: example_lines(n) for n in range(1, 5)}
for n, lines in EXAMPLES.items():
    (OUT / f"example-0{n}.snapshot").write_text("\n".join(lines) + "\n", encoding="utf-8")

RANGES = {1: (4, 9), 2: (4, 11), 3: (4, 12), 4: (4, 16)}

PAGES = {
    1: dict(no="01", kicker="第一章 · 调用契约", title="一次请求，一张图",
            intro=["把 DSL 当作纯文本 POST 给服务：请求体是 UTF-8 文本，响应体是 PNG 原始字节。",
                   "成功只有一种形态：状态码 200 且 Content-Type 以 image/ 开头；其余一律按失败处理，先读 JSON 里的 code 与 diagnostic。",
                   "限流或维护返回 429/503 并带 Retry-After：按它等待再试，每次请求都写进日志。"],
            points=[("请求", "POST https://open-snapshot.muedsa.com/snapshot，body 为 UTF-8 纯文本"),
                    ("成功", "200 + image/png 原始字节，直接写文件"),
                    ("失败", "JSON {code, message, requestId, diagnostic}"),
                    ("重试", "429/503 读 Retry-After；网络错误退避重试")],
            tips=["用 curl 发一次请求，把响应字节直接写成 .png", "把 requestId 抄进日志，再回头用它找对应的图"], ex=1, fig="同一份 DSL 的真实渲染：400×240、6 个节点",
            notes=["响应字节数由服务决定，不要用本地 PNG 长度核对。",
                   "requestId 是唯一能把图片、日志与失败诊断串起来的字段。"]),
    2: dict(no="02", kicker="第二章 · 根尺寸与有界布局", title="先给边界，再谈排布",
            intro=["Snapshot 根没有 width/height：画布尺寸来自内容，要固定输出就先用 Container 写死宽高。",
                   "Row/Column 在主轴上默认无界；把 Expanded 放进无界主轴会直接报 Layout size is infinite。",
                   "Positioned 只在 Stack/IndexedStack 里生效，放进 Row 会得到 renderBox.parentData must be StackParentData。",
                   "注意：给 Container 写 left/top 不会生效——绝对定位属于 Positioned，不属于 Container。"],
            points=[("根尺寸", "由布局决定：<Container width height> 包住全部内容"),
                    ("Expanded", "只在有界主轴里合法，用来瓜分剩余空间"),
                    ("Positioned", "父节点必须是 Stack，坐标相对 Stack 左上角"),
                    ("排查", "先看错误里的 Layout size 与 parentData 关键词")],
            tips=["把 Expanded 放进无界 Column，抄下报错原文", "用 Stack + Positioned 复现两个方块的重叠"], ex=2, fig="三块等分来自有界 Row；重叠方块来自有界 Stack",
            notes=["不要用 HTML 的默认块级流来类比 Snapshot 的布局。",
                   "方格重叠靠 Positioned 的 left/top 叠加实现。"]),
    3: dict(no="03", kicker="第三章 · 文本与透明度", title="看不见的字符，最容易出错",
            intro=["Text 会裁掉首尾空白；要保留空白就用 Text 内的 Raw，或把整段包进 CDATA。",
                   "< 与 & 不是普通字符：必须走 CDATA，否则会被当成标签或实体，渲染出来就是另一段文字。",
                   "8 位十六进制是 #RRGGBBAA，末两位是 alpha：20% 白是 #FFFFFF33，#33FFFFFF 却是青白色。",
                   "富文本用同一个 Text 里嵌 Text 实现，各 span 天然共用一条基线（示例为控制行宽未印出，原理见下）。"],
            points=[("Raw", "Text 的子节点，保留首尾与连续空格"),
                    ("CDATA", "<![CDATA[A < B & C > D]]> 原样输出"),
                    ("富文本", "同一个 Text 内嵌 Text，共用基线"),
                    ("alpha", "#RRGGBBAA：33=20%、80≈50%、FF=100%")],
            tips=["把 #FFFFFF33 改成 #33FFFFFF，对比前后颜色", "用 Raw 保住两个连续空格，再删掉它试试"], ex=3, fig="CDATA、Raw 与两个不同 alpha 的叠色，来自同一份 DSL",
            notes=["把半透明当“变淡”容易忽略它仍在和白底混合。",
                   "每个 span 只能有一个颜色，斜杠要单独一段。"]),
    4: dict(no="04", kicker="第四章 · 滤镜与可复现交付", title="效果要能被验证",
            intro=["ImageFiltered 作用于整棵子树，BackdropFilter 在已有内容上叠一层模糊；想“只糊背景”就要把清晰内容画在裁剪外。",
                   "本例把蓝色面板放进 ImageFiltered 子树：面板边缘被糊成渐变，条纹仍是硬边；文字另画一层，所以保持锐利。",
                   "交付前必须打开最终 PNG 检查尺寸、层次与遮挡；失败响应、重试和每次迭代都留在日志里。"],
            points=[("ImageFiltered", "整棵子树一起糊，连文字也糊"),
                    ("SizedBox", "给滤镜子树一个确定尺寸，定位才稳定"),
                    ("自检", "渲染后打开原图，核对遮挡与裁切"),
                    ("可复现", "DSL、PNG、请求日志、迭代记录一并保存")],
            tips=["把 sigma 从 6 改成 0 与 20，比较面板边缘", "把 ImageFiltered 提到 Container 外，看文字是否一起糊"], ex=4, fig="条纹锐利、蓝色面板被 σ=6 模糊：同一份 DSL 的真实渲染",
            notes=["蓝色面板的四边被模糊成渐变，条纹仍是硬边。",
                   "想只糊背景，就把模糊副本放进裁剪内，文字另画一层。"]),
}

def page_dsl(n):
    cfg = PAGES[n]
    p: list[str] = []
    p.append(K.rect(0, 0, W, H, color=BG))
    p.append(K.rect(48, 44, W - 96, 4, color=ACCENT))
    p.append(K.text(48, 56, cfg["kicker"], size=22, color=ACCENT, bold=True, width=600))
    p.append(K.text(48, 92, cfg["title"], size=42, color=INK, bold=True, width=900))
    p.append(K.text(W - 168, 58, f"{cfg['no']} / 04", size=22, color=MUTED, width=120, align="RIGHT"))
    p.append(K.rect(48, 156, W - 96, 1, color="#E2DDD3"))
    y = 176
    for para in cfg["intro"]:
        lines = wrap(para, 24, 1096)
        for i, ln in enumerate(lines):
            p.append(K.text(48, y + i * 33, ln, size=24, color=INK2, width=1104))
        y += len(lines) * 33 + 6

    s, e = RANGES[cfg["ex"]]
    lines = EXAMPLES[cfg["ex"]][s - 1:e]
    p.append(K.text(48, y + 6, "示例代码（节选）", size=22, color=INK, bold=True, width=400))
    p.append(K.text(W - 508, y + 10, f"完整示例 example-0{cfg['ex']}.snapshot 第 {s}–{e} 行",
                    size=18, color=MUTED, width=460, align="RIGHT"))
    cy = y + 42
    block_h = 24 + len(lines) * 25
    p.append(K.rect(48, cy, 1104, block_h, color=CODE_BG, radius=12))
    p.append(K.rect(48, cy, 5, block_h, color=ACCENT, radius=2))
    for i, ln in enumerate(lines):
        p.append(K.text(58, cy + 12 + i * 25, ln, width=1090, size=20, color=CODE_INK, family=MONO))
    p.append(K.text(64, cy + block_h + 4, "…… 第 1–3 行是 Snapshot 根与 400×240 容器，此处省略 ……",
                    size=18, color=MUTED, width=1000))

    fy = cy + block_h + 40
    p.append(K.text(48, fy, "教学插图（同一份 DSL 的真实渲染，1:1）", size=22, color=INK, bold=True,
                    width=700))
    fx, fyy = 48, fy + 40
    p.append(K.rect(fx - 4, fyy - 4, 408, 248, color="#0B1220", radius=8))
    for el in CORES[cfg["ex"]](fx, fyy):
        p.append(el)
    ax = fx + 444
    p.append(K.text(ax, fyy + 2, cfg["fig"], size=20, color=INK2, width=610))
    for i, note in enumerate(cfg["notes"]):
        p.append(K.text(ax, fyy + 42 + i * 62, "· " + note, size=20, color=MUTED, width=610))

    py = fyy + 272
    p.append(K.rect(48, py, W - 96, 1, color="#E2DDD3"))
    p.append(K.text(48, py + 12, "要点", size=22, color=INK, bold=True, width=200))
    for i, (k, v) in enumerate(cfg["points"]):
        yy = py + 46 + i * 31
        p.append(K.text(48, yy, k, size=20, color=ACCENT, bold=True, width=176))
        p.append(K.text(232, yy, v, size=20, color=INK2, width=900))
    ty = py + 196
    p.append(K.rect(48, ty, W - 96, 132, color="#F3EEE4", radius=12))
    p.append(K.text(70, ty + 14, "试一试", size=22, color=ACCENT, bold=True, width=200))
    for i, tip in enumerate(cfg["tips"]):
        p.append(K.text(70, ty + 52 + i * 34, "· " + tip, size=20, color=INK2, width=1000))
    p.append(K.rect(48, H - 40, W - 96, 1, color="#E2DDD3"))
    p.append(K.text(48, H - 30, f"从文字到图片 · Snapshot 入门手册 · {cfg['no']}", size=18,
                    color=MUTED, width=700))
    p.append(K.text(W - 348, H - 30, "示例均可直接提交运行", size=18, color=MUTED, width=300,
                    align="RIGHT"))
    return K.document(W, H, p, background=BG)

logger = api.TaskLogger(TASK, TMP)
ONLY = os.environ.get("A17_ONLY", "1234")
for n in [int(c) for c in ONLY]:
    dsl = page_dsl(n)
    (OUT / f"handbook-0{n}.snapshot").write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(OUT / f"handbook-0{n}.snapshot", OUT / f"handbook-0{n}.png", f"handbook {n}")
    print(f"page{n}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s")
    for w in warn:
        print("   ", w)
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:900])
        raise SystemExit(1)

for n in [int(c) for c in ONLY]:
    rec = logger.render(OUT / f"example-0{n}.snapshot", OUT / f"example-0{n}.png", f"example {n}")
    ok = rec["http_status"] == 200
    print(f"example{n}: {rec['http_status']} {rec['response_bytes']}B",
          api.measure_png(OUT / f"example-0{n}.png") if ok else "")
    if not ok:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:900])
        raise SystemExit(1)

out = []
for n in range(1, 5):
    lines = EXAMPLES[n]
    s, e = RANGES[n]
    out.append({
        "page": n, "purpose": PAGES[n]["title"],
        "full_dsl": f"example-0{n}.snapshot", "rendered_png": f"example-0{n}.png", "size": [400, 240],
        "core_subtree": {
            "in_example": "Stack 下的 6–16 个子节点，坐标以 (0,0) 为原点",
            "in_handbook": "同一批子节点整体平移到教学页插图框内，尺寸、字号、相对坐标与滤镜参数不变",
            "outer_wrapper_difference": "示例：Snapshot + Container(400×240)；手册：只多一层插图外框与平移，不改变语义"},
        "printed_snippet": {"line_range_1based": [s, e], "line_count": e - s + 1,
                            "text": lines[s - 1:e], "omitted_lines": [1, 3],
                            "omitted_note": "…… 第 1–3 行是 Snapshot 根与 400×240 容器，此处省略 ……"},
        "total_lines": len(lines),
    })
api.write_json(OUT / "examples.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "protocol": {"method": "POST", "url": "https://open-snapshot.muedsa.com/snapshot",
                 "body": "UTF-8 plain text DSL", "success": "200 + image/png",
                 "failure": "JSON {code, message, requestId, diagnostic}"},
    "examples": out,
})
print("done")
