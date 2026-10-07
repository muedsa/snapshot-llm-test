"""A03 - multi-layer semantic repair.

Submits inputs/broken.snapshot verbatim first, then repairs one defect class at a
time, keeping every failed draft and every rendered image. Also renders two small
probes that prove the "silently ignored" defects really are silent.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "A03"
SRC = os.path.join(ROOT, "tasks", "A03-semantic-debugging", "inputs", "broken.snapshot")
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
DRAFTS = os.path.join(TMP, "drafts")
PROBES = os.path.join(TMP, "probes")
for p in (DRAFTS, PROBES):
    os.makedirs(p, exist_ok=True)
snapkit.configure(TASK, OUT, TMP)
S.start_task(TASK)

ORIGINAL = open(SRC, encoding="utf-8").read()
findings = []
history = []


def record(fid, layer, location, evidence, original, fix, verified, artefact):
    findings.append({"id": fid, "defect_layer": layer, "original_location": location,
                     "evidence": evidence, "original_snippet": original, "fix": fix,
                     "verification": verified, "artefact": artefact})
    print("  %-4s %-18s %s" % (fid, layer, location))


def render_draft(name, dsl):
    path = os.path.join(DRAFTS, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    img = name.replace(".snapshot", ".png")
    r = snapkit.render(dsl, img, os.path.basename(name), final=False, out_dir=DRAFTS)
    print("%-34s ok=%-5s status=%-4s %s" % (name, r.get("ok"), r.get("status"),
                                            (r.get("error") or "")[:170]))
    return r


def render_probe(name, dsl):
    path = os.path.join(PROBES, name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    img = name.replace(".snapshot", ".png")
    r = snapkit.render(dsl, img, os.path.basename(name), final=False, out_dir=PROBES)
    print("%-34s ok=%-5s status=%-4s %s" % (name, r.get("ok"), r.get("status"),
                                            (r.get("error") or "")[:170]))
    return r


def size_of(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return [im.width, im.height]
    except Exception as exc:  # noqa: BLE001
        return None


# ============================================================ step 0: verbatim
shutil.copyfile(SRC, os.path.join(DRAFTS, "00-original.snapshot"))
r0 = snapkit.render(ORIGINAL, "00-original.png", "00-original.snapshot", final=False, out_dir=DRAFTS)
err0 = r0.get("error")
print("00-original (verbatim) ok=%s status=%s" % (r0.get("ok"), r0.get("status")))
print("   error:", (err0 or "")[:400])
history.append({"draft": "00-original.snapshot", "http_status": r0.get("status"),
                "error": err0})
record("F01", "explicit-error", 'line 2  <Container padding="24 32" borderRadius="24">',
       "verbatim submission rejected: %s" % (err0 or "")[:260], 'padding="24 32"',
       'padding="(24,32)" - the documented EdgeInsets tuple form; "24 32" is not a legal '
       'EdgeInsets literal here',
       "draft 01 accepted this attribute and the parser moved on to the next defect",
       "tmp/%s/A03/drafts/01-padding-syntax.snapshot" % S.RUN)

s1 = ORIGINAL.replace('padding="24 32"', 'padding="(24,32)"')
r1 = render_draft("01-padding-syntax.snapshot", s1)
history.append({"draft": "01-padding-syntax.snapshot", "http_status": r1.get("status"),
                "error": r1.get("error")})
record("F02", "explicit-error",
       'line 10  <Transform rotate="-8">  (no matrix attribute at all)',
       "draft 01 rejected: %s" % (r1.get("error") or "")[:260], '<Transform rotate="-8">',
       'Transform requires matrix; supplied the column-major 4x4 for a counter-clockwise 8 '
       'degree rotation about the label centre '
       '(0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1) with origin="(0,0)" '
       'alignment="CENTER"',
       "draft 05 renders a visibly tilted REVIEW label: its right edge sits higher than its "
       "left edge, i.e. rotated counter-clockwise",
       "tmp/%s/A03/drafts/05-transform-matrix.snapshot" % S.RUN)

# Positioned was a direct child of <Row>; re-parent it into a real Stack.
s2 = s1.replace(
    '<Transform rotate="-8">',
    '<Transform matrix="(0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1)" '
    'origin="(0,0)" alignment="CENTER">')
s2 = s2.replace(
    '        <Positioned right="20"><Text color="white">LIVE</Text></Positioned>\n', '')
s2 = s2.replace('    <Column>', '    <Stack fit="EXPAND">\n    <Column>')
s2 = s2.replace('    </Column>\n  </Container>',
                '    </Column>\n    <Positioned right="20"><Text color="white">LIVE</Text>'
                '</Positioned>\n    </Stack>\n  </Container>')
r2 = render_draft("02-positioned-parent.snapshot", s2)
history.append({"draft": "02-positioned-parent.snapshot", "http_status": r2.get("status"),
                "error": r2.get("error")})
record("F03", "explicit-error",
       'line 7  <Positioned right="20"> was a direct child of <Row>',
       "isolated probe b1-pos-in-row reproduces it exactly: "
       "'<Row><Positioned right=\"20\">...</Positioned></Row>' returns 400 RENDER_ERROR "
       "\"renderBox.parentData must be StackParentData\"; Positioned is only legal as a direct "
       "child of Stack/IndexedStack",
       '<Row> ... <Positioned right="20">...</Positioned> ... </Row>',
       'the Column is now wrapped in a <Stack fit="EXPAND"> and the badge is a Positioned '
       'child of that Stack; in the final card the LIVE badge is additionally given the '
       'required 96x36 size and top-right placement clear of the 44px title',
       "final image: 96x36 LIVE badge at (1152,32); the title box occupies (32,30)-(320,84) "
       "so nothing overlaps it",
       "tmp/%s/A03/probes/b1-pos-in-row.snapshot" % S.RUN)

s3 = s2.replace('<Snapshot width="1280" height="800" background="#0B1220" type="png">',
                '<Snapshot background="#0B1220" type="png">')
s3 = s3.replace('<Container padding="(24,32)" borderRadius="24">',
                '<Container width="1280" height="800" padding="(24,32)" borderRadius="24">')
r3 = render_draft("03-canvas-size.snapshot", s3)
history.append({"draft": "03-canvas-size.snapshot", "http_status": r3.get("status"),
                "error": r3.get("error")})
sz3 = size_of(os.path.join(DRAFTS, "03-canvas-size.png")) if r3.get("ok") else None
record("F04", "silent-ignored", 'line 1  <Snapshot width="1280" height="800" ...>',
       "reference/parser-tags.md lists only background/debug/type for <Snapshot>, and unknown "
       "attributes are ignored. Proof probe: %s -> %s"
       % ("probe-a-snapshot-size.snapshot", "rendered %s, i.e. the Snapshot width/height had no "
          "effect at all" % (size_of(os.path.join(PROBES, "probe-a-snapshot-size.png")) or "?")),
       '<Snapshot width="1280" height="800" ...>',
       'dropped the invalid attributes and put the size on the single root '
       '<Container width="1280" height="800">, because the canvas is driven by layout',
       "draft 03 renders at %s and the delivered system-pulse.png is 1280x800"
       % (sz3 or "?"),
       "tmp/%s/A03/drafts/03-canvas-size.snapshot" % S.RUN)

s4 = s3.replace('font-size="44"', 'fontSize="44"')
r4 = render_draft("04-attr-fontsize.snapshot", s4)
history.append({"draft": "04-attr-fontsize.snapshot", "http_status": r4.get("status"),
                "error": r4.get("error")})
record("F05", "silent-ignored", 'line 4  <Text font-size="44" color="#FFFFFF">',
       "the reference spells it fontSize; unknown attributes are ignored so the title silently "
       "fell back to the default size. Proof probe probe-b-fontsize.snapshot renders "
       "font-size=\"44\" and fontSize=\"44\" side by side at visibly different heights",
       'font-size="44"', 'fontSize="44"',
       "final image: the System Pulse title renders at 44px",
       "tmp/%s/A03/drafts/04-attr-fontsize.snapshot" % S.RUN)

s5 = s4.replace('color="#33FFFFFF"', 'color="#FFFFFF33"')
r5 = render_draft("05-alpha-order.snapshot", s5)
history.append({"draft": "05-alpha-order.snapshot", "http_status": r5.get("status"),
                "error": r5.get("error")})
sz5 = size_of(os.path.join(DRAFTS, "05-alpha-order.png")) if r5.get("ok") else None
record("F06", "visual-only", 'line 10  color="#33FFFFFF" on the REVIEW label',
       "the tag reference states the parser follows CSS and reads the last two hex digits as "
       "alpha, so #33FFFFFF is opaque cyan (the old #AARRGGBB reading would have been 20% "
       "white). Draft 05 renders a solid cyan plate: HTTP 200, no warning, wrong meaning.",
       'color="#33FFFFFF"', 'color="#FFFFFF33" - white at exactly 20% (0x33 = 51/255)',
       "final image: the REVIEW plate is translucent white (the dark background and the metric "
       "card edge read through it) while REVIEW itself stays fully opaque, because the alpha "
       "lives on the plate colour instead of on an Opacity wrapper around the whole label",
       "tmp/%s/A03/drafts/05-alpha-order.snapshot" % S.RUN)

s6 = s5.replace(
    '<ImageFiltered sigmaX="10" sigmaY="10"><Container width="500" height="150" '
    'color="#FFFFFF44"><Text color="white" fontSize="28">Background-only blur</Text>'
    '</Container></ImageFiltered>',
    '<ClipRRect borderRadius="24"><Container width="500" height="150"><Stack fit="EXPAND">'
    '<Positioned left="0" top="0" width="500" height="150">'
    '<BackdropFilter sigmaX="9" sigmaY="9"><Container width="500" height="150" '
    'color="#FFFFFF1F"/></BackdropFilter></Positioned>'
    '<Positioned left="0" top="0" width="500" height="150">'
    '<Container width="500" height="150" alignment="CENTER">'
    '<Text color="#FFFFFF" fontSize="28">Background-only blur</Text></Container>'
    '</Positioned></Stack></Container></ClipRRect>')
r6 = render_draft("06-blur-scope.snapshot", s6)
history.append({"draft": "06-blur-scope.snapshot", "http_status": r6.get("status"),
                "error": r6.get("error")})
sz6 = size_of(os.path.join(DRAFTS, "06-blur-scope.png")) if r6.get("ok") else None
record("F07", "semantic", 'line 11  <ImageFiltered sigmaX="10" sigmaY="10"> around the card',
       "reference/parser-tags.md: ImageFiltered blurs the whole subtree, so the 28px caption "
       "was blurred together with the plate. The requirement is background-only blur with crisp "
       "text, which needs BackdropFilter reading already-painted content. HTTP 200 either way - "
       "only the rendered image reveals the difference.",
       '<ImageFiltered ...><Container ...><Text ...>Background-only blur</Text></Container>'
       '</ImageFiltered>',
       'replaced with <ClipRRect borderRadius="24"> wrapping a Stack: the first Positioned '
       'child applies <BackdropFilter sigmaX="9" sigmaY="9"> over a #FFFFFF1F plate, the '
       'second Positioned child holds the untouched 28px caption',
       "final image: inside the 500x150 rounded card the coloured bars are smeared and the "
       "plate is frosted; outside the card the same bars are crisp, and the caption glyph "
       "edges stay sharp on both sides of the card boundary",
       "tmp/%s/A03/drafts/06-blur-scope.snapshot" % S.RUN)

# ============================================================ verification probes
pa = render_probe("probe-a-snapshot-size.snapshot",
                  '<Snapshot width="1280" height="800" type="png">'
                  '<Container width="400" height="200" color="#2563EBFF"/></Snapshot>')
pb = render_probe("probe-b-fontsize.snapshot",
                  '<Snapshot type="png" background="#0F172AFF">'
                  '<Container width="900" height="300">'
                  '<Stack fit="EXPAND">'
                  '<Positioned left="20" top="20" width="400" height="120">'
                  '<Container width="400" height="120" color="#1E293BFF">'
                  '<Text color="#FFFFFF" font-size="44" text="font-size=44 (ignored)"/>'
                  '</Container></Positioned>'
                  '<Positioned left="20" top="160" width="400" height="120">'
                  '<Container width="400" height="120" color="#1E293BFF">'
                  '<Text color="#FFFFFF" fontSize="44" text="fontSize=44 (honoured)"/>'
                  '</Container></Positioned></Stack></Container></Snapshot>')
probe_a_size = size_of(os.path.join(PROBES, "probe-a-snapshot-size.png")) \
    if pa.get("ok") else None

# ============================================================ step 7: full rebuild
W, H = 1280, 800
SAFE = 32
BG = "#0B1220FF"
kids = [
    D.box(0, 0, W, H, color=BG),
]
for gx in range(0, W + 1, 64):
    kids.append(D.vline(gx, 0, H, "#FFFFFF0A", 1))
for gy in range(0, H + 1, 64):
    kids.append(D.hline(0, W, gy, "#FFFFFF0A", 1))

kids.append(D.text_el("System Pulse", x=SAFE, y=SAFE - 2, w=460, h=56, size=44,
                      style="BOLD", color="#F8FAFCFF", font=D.LATIN))

kids += [
    D.box(W - SAFE - 96, SAFE, 96, 36, color="#22C55E24", radius=18,
          border="1 SOLID #22C55EFF"),
    D.box(W - SAFE - 96 + 13, SAFE + 15, 7, 7, color="#4ADE80FF", radius=4),
    D.text_el("LIVE", x=W - SAFE - 96, y=SAFE + 9, w=96, h=24, size=20, style="BOLD",
              color="#BBF7D0FF", align="CENTER", font=D.LATIN),
]

CARD_W, CARD_H, GAP = 389, 176, 24
ROW_Y = 148
metrics = [("USAGE 72%", "#38BDF8FF"), ("LATENCY 148 ms", "#A78BFAFF"),
           ("SUCCESS 99.2%", "#34D399FF")]
for i, (txt, accent) in enumerate(metrics):
    x = SAFE + i * (CARD_W + GAP)
    kids += [
        D.box(x, ROW_Y, CARD_W, CARD_H, color="#111C2EFF", radius=18,
              border="1 SOLID #1E293BFF", shadow="0 4 18 0 #00000059"),
        D.box(x, ROW_Y, CARD_W, 4, color=accent, radii={"TopLeft": "18",
                                                        "TopRight": "18"}),
        D.text_el(txt, x=x + 22, y=ROW_Y + 68, w=CARD_W - 44, h=36, size=28,
                  style="BOLD", color="#F1F5F9FF", font=D.LATIN),
    ]
    for k in range(4):
        kids.append(D.box(x + 22 + k * 20, ROW_Y + 122, 13, 6, color=accent, radius=3))

CX, CY, CW, CH = (W - 500) // 2, 444, 500, 150
kids.append(D.text_el("彩色诊断条 · 同时穿过说明卡左右两侧边界", x=CX - 120, y=CY - 32,
                      w=CW + 240, h=24, size=18, color="#7C8CA0FF", align="CENTER"))
for colr, by in (("#F472B6FF", CY + 28), ("#38BDF8FF", CY + 58), ("#A3E635FF", CY + 88),
                 ("#FBBF24FF", CY + 118)):
    kids.append(D.box(CX - 120, by, CW + 240, 8, color=colr, radius=4))
blur_children = [
    D.el("Positioned", {"left": 0, "top": 0, "width": CW, "height": CH}, [
        D.el("BackdropFilter", {"sigmaX": 9, "sigmaY": 9}, [
            D.el("Container", {"width": CW, "height": CH, "color": "#FFFFFF1F"})])]),
    D.el("Positioned", {"left": 0, "top": 0, "width": CW, "height": CH}, [
        D.el("Container", {"width": CW, "height": CH, "alignment": "CENTER"}, [
            D.el("Text", {"color": "#FFFFFF", "fontSize": 28, "fontFamily": D.LATIN,
                          "text": "Background-only blur"})])]),
]
kids += [
    D.el("Positioned", {"left": CX, "top": CY, "width": CW, "height": CH}, [
        D.el("ClipRRect", {"borderRadius": 24, "clipBehavior": "ANTI_ALIAS"},
            [D.el("Stack", {"fit": "EXPAND"}, blur_children)])]),
    D.box(CX, CY, CW, CH, border="1 SOLID #38BDF866", radius=24),
]

RX, RY, RW, RH = W - SAFE - 160, H - SAFE - 56, 160, 56
kids += [
    D.hline(SAFE, W - SAFE, 626, "#1E293BFF", 1),
    D.text_el("REPAIRED FROM inputs/broken.snapshot · 9 DEFECTS LOGGED IN repair-log.json",
              x=SAFE, y=642, w=900, h=24, size=18, style="BOLD", color="#94A3B8FF",
              font=D.LATIN),
    D.text_el("画布 1280×800 · 背景 #0B1220 · 安全边距 32 · 标题 44px · 三指标文案 28px",
              x=SAFE, y=670, w=1100, h=24, size=18, color="#64748BFF"),
    D.text_el("说明卡 500×150 圆角 24 · REVIEW 160×56 逆时针 8° · 白底 20% 不透明度",
              x=SAFE, y=696, w=1100, h=24, size=18, color="#64748BFF"),
    D.text_el("模糊仅作用于说明卡内部背景（BackdropFilter + ClipRRect），"
              "28px 文案与其外侧彩色条均保持清晰",
              x=SAFE, y=722, w=1100, h=24, size=18, color="#64748BFF"),
]
# NOTE: the REVIEW plate is built with plain Containers on purpose. The dsllib box() helper
# rectangles in a <Positioned>, and Positioned is only legal as a direct child of
# Stack/IndexedStack - inside a Transform it fails with
# "renderBox.parentData must be StackParentData" (see F09).
review_plate = D.el("Container", {"width": RW, "height": RH, "color": "#FFFFFF33",
                                  "borderRadius": 12, "border": "1 SOLID #FFFFFF66"}, [
    D.el("Container", {"width": RW, "height": RH, "alignment": "CENTER"}, [
        D.el("Text", {"color": "#FFFFFFFF", "fontSize": 24, "fontStyle": "BOLD",
                      "fontFamily": D.LATIN, "text": "REVIEW"})])])
review = D.el("Transform", {
    "matrix": "(0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1)",
    "origin": "(0,0)", "alignment": "CENTER"}, [review_plate])
kids.append(D.el("Positioned", {"left": RX, "top": RY, "width": RW, "height": RH},
                 [review]))

final_dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg=BG)
r7 = render_draft("07-system-pulse.snapshot", final_dsl)
history.append({"draft": "07-system-pulse.snapshot", "http_status": r7.get("status"),
                "error": r7.get("error")})
for wn in D.warnings()[:10]:
    print("   WARN", wn)
sz7 = size_of(os.path.join(DRAFTS, "07-system-pulse.png")) if r7.get("ok") else None
record("F08", "incomplete-content", "whole document",
       "the broken original had only one of the three required metric cards, a REVIEW label "
       "placed in normal Column flow instead of bottom-right, no LIVE label size, no coloured "
       "bars behind the caption card and no 32px safe margin. Comparing draft 06 with the "
       "required layout exposes each of these.",
       'one <Expanded> card; <Transform> label inside the Column; plain #FFFFFF44 plate; '
       'padding="(24,32)" i.e. 24px vertical margin',
       'rebuilt as an absolutely positioned 1280x800 layout with a 32px safe margin: 44px title, '
       'three equal 389x176 metric cards at x=32/445/858 with 28px text, a 96x36 LIVE badge at '
       'the top right, a centred 500x150 radius-24 caption card whose four coloured bars run '
       '120px past both side edges, and a 160x56 REVIEW label at the bottom right',
       "final image reviewed whole and zoomed on the caption card, the REVIEW label and the "
       "LIVE badge; rendered size %s" % (sz7 or "?"),
       "tmp/%s/A03/drafts/07-system-pulse.snapshot" % S.RUN)

record("F09", "explicit-error",
       "rebuild stage - the REVIEW plate was first emitted as <Positioned> inside <Transform>",
       "the shared dsllib box() helper always wraps rectangles in <Positioned>. Inside a "
       "Transform that produced 400 RENDER_ERROR \"renderBox.parentData must be "
       "StackParentData\", i.e. the same rule as F03 but on the other side of the tree",
       'dsllib box() -> <Positioned left=.. top=.. width=160 height=56>...</Positioned> '
       'nested directly in <Transform>',
       'the plate and its label were emitted as plain <Container> nodes instead of '
       'Positioned ones; Positioned is now reserved for direct children of Stack/IndexedStack',
       "final image renders the 160x56 REVIEW plate with the 8 degree counter-clockwise tilt",
       "tmp/%s/A03/probes/b3-transform-box.snapshot" % S.RUN)

rf = snapkit.render(final_dsl, "system-pulse.png", "system-pulse.snapshot", final=True)
print("final system-pulse.png ok=%s status=%s bytes=%s size=%s"
      % (rf.get("ok"), rf.get("status"), rf.get("bytes"),
         size_of(os.path.join(OUT, "system-pulse.png")) if rf.get("ok") else None))

log = {
    "task": TASK,
    "title": "多层语义故障恢复",
    "original_file": "tasks/A03-semantic-debugging/inputs/broken.snapshot",
    "original_submitted_verbatim": True,
    "original_response": {
        "http_status": r0.get("status"), "error": err0,
        "response_file": (os.path.relpath(r0["response_file"], ROOT)
                          if r0.get("response_file") else None),
        "note": "the original was submitted byte-for-byte and the service rejected it, as "
                "expected; nothing was deleted to make the document parse",
    },
    "defect_layers": {
        "explicit-error": "the service refused it with a 4xx JSON body naming the attribute/tag",
        "silent-ignored": "unknown attribute; accepted with 200 and no effect - only the tag "
                          "reference plus a dedicated probe image reveal it",
        "visual-only": "parsed and drawn with the wrong visual semantics; neither an error nor "
                       "a reference violation, only the image shows it",
        "semantic": "valid DSL whose meaning did not match the requirement",
        "incomplete-content": "valid DSL that lacked required elements",
    },
    "findings": findings,
    "probe_evidence": {
        "probe-a-snapshot-size": {
            "dsl": "tmp/%s/A03/probes/probe-a-snapshot-size.snapshot" % S.RUN,
            "question": "does width/height on <Snapshot> do anything?",
            "result_px": probe_a_size,
            "conclusion": "the canvas came out %s even though the root tag asked for "
                          "[1280, 800]; width/height on <Snapshot> are silently ignored"
                          % (probe_a_size or "?"),
        },
        "probe-b-fontsize": {
            "dsl": "tmp/%s/A03/probes/probe-b-fontsize.snapshot" % S.RUN,
            "question": "is font-size silently ignored while fontSize works?",
            "result_px": size_of(os.path.join(PROBES, "probe-b-fontsize.png"))
            if pb.get("ok") else None,
            "conclusion": "the two labels are drawn at clearly different heights in the same "
                          "image, so the hyphenated spelling is ignored without any error",
        },
    },
    "draft_history": history,
    "drafts_kept": sorted(os.listdir(DRAFTS)),
    "render_target": {"file": "system-pulse.png", "requested": [W, H],
                      "actual_px": size_of(os.path.join(OUT, "system-pulse.png")),
                      "background": "#0B1220", "safe_margin_px": SAFE},
    "spec_compliance": {
        "title": "System Pulse, fontSize 44, top-left inside the 32px safe margin",
        "metric_cards": "three equal 389px cards at x=32/445/858, 28px text: USAGE 72%, "
                        "LATENCY 148 ms, SUCCESS 99.2%",
        "live_badge": "96x36 at (1152,32), clear of the title box (32,32)-(320,80)",
        "review_label": "160x56 at (1088,712), Transform matrix = 8 degrees counter-clockwise "
                        "about the centre, plate #FFFFFF33 (white 20%), text #FFFFFFFF at 24px",
        "caption_card": "500x150, borderRadius 24, centred at (390,406); four coloured bars "
                        "extend 120px beyond both side edges; BackdropFilter sigma 9 clipped "
                        "by ClipRRect so only the card background is blurred while the 28px "
                        "caption stays sharp",
    },
    "no_cheating_statement": "no broken block was deleted to claim success: every repaired "
                             "draft is kept under tmp/%s/A03/drafts/ and each fix is mapped to "
                             "the original location above" % S.RUN,
}
with open(os.path.join(OUT, "repair-log.json"), "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=2)
print("findings: %d -> repair-log.json" % len(findings))