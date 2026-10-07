"""A17 examples: the four runnable 400x240 DSL documents.

Each entry is the SINGLE source of truth for two things:
  * `dsl`  - the complete document that is POSTed to /snapshot verbatim and
             written to example-0N.snapshot (rendered as example-0N.png)
  * `art`  - the page illustration, redrawn with page DSL primitives only
             (no <Image>), mirroring the example's geometry

The printed code on a handbook page is sliced verbatim out of `dsl`, so the
page can never show a different program than the one that was rendered.

Line width rule: the handbook code block prints at 20px DejaVu Sans Mono, whose
measured advance is exactly 0.600 em, so one character is 12.0px and the block
fits 83 characters.  No line of an example may exceed that.

Art item forms (coordinates live in the example's own 400x240 space; the page
builder scales them):
  {"t": "rect", "box": [x, y, w, h], "fill": "#RRGGBBAA", "radius": 0,
   "border": "1 SOLID #RRGGBBAA"}
  {"t": "text", "box": [x, y, w, h], "s": "...", "size": 18,
   "color": "#RRGGBBAA", "font": "mono"|"ui", "align": "RIGHT"|"CENTER"}
  {"t": "blur_backdrop", "box": [...], "radius": 14, "sigma": 7, "tint": "#..."}
  {"t": "blur_subtree",  "box": [...], "radius": 14, "sigma": 7,
   "plate": "#...", "inset": [x, y, w, h], "s": "...", "size": 18,
   "color": "#...", "font": "ui"}
"""
from __future__ import annotations

UI = "Inter,Noto Sans CJK SC"
MONO = "DejaVu Sans Mono"
MAX_COLS = 83


def _bars():
    cols = ["#7C3AEDFF", "#0EA5E9FF", "#F472B6FF", "#FACC15FF",
            "#34D399FF", "#FB923CFF", "#A78BFAFF", "#38BDF8FF"]
    out = []
    for i, c in enumerate(cols):
        out.append('      <Positioned left="%d" top="76" width="44" height="120">\n'
                   '        <Container color="%s" />\n'
                   '      </Positioned>' % (12 + i * 48, c))
    return "\n".join(out), cols


_BAR_DSL, BAR_COLS = _bars()

# ============================================================== example 01
EX1 = """<Snapshot type="png" background="#0B1220FF">
  <Container width="400" height="240">
    <Stack fit="EXPAND">
      <Container width="400" height="52" color="#111C31FF" />
      <Positioned left="18" top="13" width="220" height="28">
        <Text fontSize="19" fontFamily="DejaVu Sans Mono"
              color="#E2E8F0FF" text="POST /snapshot" />
      </Positioned>
      <Positioned left="230" top="14" width="152" height="26">
        <Text fontSize="18" fontFamily="DejaVu Sans Mono"
              color="#34D399FF" text="200 image/png" textAlign="RIGHT" />
      </Positioned>
      <Positioned left="16" top="68" width="168" height="88">
        <Container color="#16233EFF" borderRadius="12"
                   border="1 SOLID #1E3A8AFF" />
      </Positioned>
      <Positioned left="30" top="80" width="140" height="20">
        <Text fontSize="14" fontFamily="DejaVu Sans Mono"
              color="#60A5FAFF" text="REQUEST" />
      </Positioned>
      <Positioned left="30" top="104" width="140" height="20">
        <Text fontSize="16" fontFamily="DejaVu Sans Mono"
              color="#E2E8F0FF" text="text/plain" />
      </Positioned>
      <Positioned left="30" top="126" width="142" height="20">
        <Text fontSize="15" fontFamily="DejaVu Sans Mono"
              color="#CBD5E1FF" text="utf-8 DSL body" />
      </Positioned>
      <Positioned left="188" top="98" width="32" height="28">
        <Text fontSize="26" fontFamily="Inter,Noto Sans CJK SC"
              color="#38BDF8FF" text="→" textAlign="CENTER" />
      </Positioned>
      <Positioned left="216" top="68" width="168" height="88">
        <Container color="#0E2A22FF" borderRadius="12"
                   border="1 SOLID #14532DFF" />
      </Positioned>
      <Positioned left="230" top="80" width="140" height="20">
        <Text fontSize="14" fontFamily="DejaVu Sans Mono"
              color="#34D399FF" text="RESPONSE" />
      </Positioned>
      <Positioned left="230" top="104" width="140" height="20">
        <Text fontSize="16" fontFamily="DejaVu Sans Mono"
              color="#E2E8F0FF" text="200 OK" />
      </Positioned>
      <Positioned left="230" top="126" width="144" height="20">
        <Text fontSize="15" fontFamily="DejaVu Sans Mono"
              color="#A7F3D0FF" text="PNG bytes" />
      </Positioned>
      <Positioned left="16" top="172" width="368" height="52">
        <Container color="#3A141AFF" borderRadius="12"
                   border="1 SOLID #7F1D1DFF" />
      </Positioned>
      <Positioned left="30" top="182" width="200" height="22">
        <Text fontSize="17" fontFamily="DejaVu Sans Mono"
              color="#FCA5A5FF" text="400 PARSE_ERROR" />
      </Positioned>
      <Positioned left="30" top="204" width="230" height="20">
        <Text fontSize="14" fontFamily="DejaVu Sans Mono"
              color="#FDA4AFFF" text="code message requestId" />
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

EX1_ART = [
    {"t": "rect", "box": [0, 0, 400, 240], "fill": "#0B1220FF"},
    {"t": "rect", "box": [0, 0, 400, 52], "fill": "#111C31FF"},
    {"t": "text", "box": [18, 11, 220, 30], "s": "POST /snapshot", "size": 19,
     "color": "#E2E8F0FF", "font": "mono"},
    {"t": "text", "box": [230, 12, 152, 28], "s": "200 image/png", "size": 18,
     "color": "#34D399FF", "font": "mono", "align": "RIGHT"},
    {"t": "rect", "box": [16, 68, 168, 88], "fill": "#16233EFF", "radius": 12,
     "border": "1 SOLID #1E3A8AFF"},
    {"t": "text", "box": [30, 79, 140, 20], "s": "REQUEST", "size": 14,
     "color": "#60A5FAFF", "font": "mono"},
    {"t": "text", "box": [30, 103, 140, 22], "s": "text/plain", "size": 16,
     "color": "#E2E8F0FF", "font": "mono"},
    {"t": "text", "box": [30, 125, 142, 22], "s": "utf-8 DSL body", "size": 15,
     "color": "#CBD5E1FF", "font": "mono"},
    {"t": "text", "box": [188, 96, 32, 30], "s": "→", "size": 26,
     "color": "#38BDF8FF", "font": "ui", "align": "CENTER"},
    {"t": "rect", "box": [216, 68, 168, 88], "fill": "#0E2A22FF", "radius": 12,
     "border": "1 SOLID #14532DFF"},
    {"t": "text", "box": [230, 79, 140, 20], "s": "RESPONSE", "size": 14,
     "color": "#34D399FF", "font": "mono"},
    {"t": "text", "box": [230, 103, 140, 22], "s": "200 OK", "size": 16,
     "color": "#E2E8F0FF", "font": "mono"},
    {"t": "text", "box": [230, 125, 144, 22], "s": "PNG bytes", "size": 15,
     "color": "#A7F3D0FF", "font": "mono"},
    {"t": "rect", "box": [16, 172, 368, 52], "fill": "#3A141AFF", "radius": 12,
     "border": "1 SOLID #7F1D1DFF"},
    {"t": "text", "box": [30, 181, 200, 22], "s": "400 PARSE_ERROR", "size": 17,
     "color": "#FCA5A5FF", "font": "mono"},
    {"t": "text", "box": [30, 203, 230, 20], "s": "code message requestId",
     "size": 14, "color": "#FDA4AFFF", "font": "mono"},
]

# ============================================================== example 02
EX2 = """<Snapshot type="png" background="#F8FAFCFF">
  <Container width="400" height="240">
    <Stack fit="EXPAND">
      <Positioned left="16" top="16" width="176" height="120">
        <Container color="#FFFFFFFF" borderRadius="12"
                   border="1 SOLID #CBD5E1FF">
          <Row>
            <Expanded flex="2">
              <Container color="#2563EBFF" borderRadius="8" />
            </Expanded>
            <Container width="14" color="#F1F5F9FF" />
            <Expanded flex="1">
              <Container color="#93C5FDFF" borderRadius="8" />
            </Expanded>
          </Row>
        </Container>
      </Positioned>
      <Positioned left="28" top="146" width="170" height="22">
        <Text fontSize="16" fontFamily="Inter,Noto Sans CJK SC"
              color="#334155FF" text="Row flex=2 : 1" />
      </Positioned>
      <Positioned left="208" top="16" width="176" height="120">
        <Container color="#0F172AFF" borderRadius="12">
          <Stack fit="EXPAND">
            <Positioned left="14" top="14" width="72" height="34">
              <Container color="#38BDF8FF" borderRadius="6" />
            </Positioned>
            <Positioned right="14" bottom="14" width="56" height="26">
              <Container color="#F472B6FF" borderRadius="6" />
            </Positioned>
          </Stack>
        </Container>
      </Positioned>
      <Positioned left="220" top="146" width="172" height="22">
        <Text fontSize="16" fontFamily="Inter,Noto Sans CJK SC"
              color="#334155FF" text="Stack + Positioned" />
      </Positioned>
      <Positioned left="16" top="184" width="368" height="42">
        <Container color="#E0F2FEFD" borderRadius="10"
                   border="1 SOLID #99F6E4FF" />
      </Positioned>
      <Positioned left="30" top="196" width="344" height="24">
        <Text fontSize="16" fontFamily="Inter,Noto Sans CJK SC"
              color="#0F766EFF" text="根尺寸 400x240 来自布局" />
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

EX2_ART = [
    {"t": "rect", "box": [0, 0, 400, 240], "fill": "#F8FAFCFF"},
    {"t": "rect", "box": [16, 16, 176, 120], "fill": "#FFFFFFFF", "radius": 12,
     "border": "1 SOLID #CBD5E1FF"},
    # Row solved geometry, measured from example-02.png: the two Expanded
    # children fill the 176x120 Row (16..192 x 16..136) split 2:1 around the
    # 14px spacer.
    {"t": "rect", "box": [16, 16, 108, 120], "fill": "#2563EBFF", "radius": 12},
    {"t": "rect", "box": [124, 16, 14, 120], "fill": "#F1F5F9FF"},
    {"t": "rect", "box": [138, 16, 54, 120], "fill": "#93C5FDFF", "radius": 12},
    {"t": "text", "box": [28, 145, 170, 22], "s": "Row flex=2 : 1", "size": 16,
     "color": "#334155FF", "font": "ui"},
    {"t": "rect", "box": [208, 16, 176, 120], "fill": "#0F172AFF", "radius": 12},
    {"t": "rect", "box": [222, 30, 72, 34], "fill": "#38BDF8FF", "radius": 6},
    {"t": "rect", "box": [314, 96, 56, 26], "fill": "#F472B6FF", "radius": 6},
    {"t": "text", "box": [220, 145, 170, 22], "s": "Stack + Positioned", "size": 16,
     "color": "#334155FF", "font": "ui"},
    {"t": "rect", "box": [16, 184, 368, 42], "fill": "#E0F2FEFD", "radius": 10,
     "border": "1 SOLID #99F6E4FF"},
    {"t": "text", "box": [30, 194, 344, 26],
     "s": "根尺寸 400x240 来自布局", "size": 16,
     "color": "#0F766EFF", "font": "ui"},
]

# ============================================================== example 03
EX3 = """<Snapshot type="png" background="#111827FF">
  <Container width="400" height="240">
    <Stack fit="EXPAND">
      <Positioned left="18" top="16" width="364" height="30">
        <Text fontSize="20" fontFamily="DejaVu Sans Mono"
              color="#E5E7EBFF"><![CDATA[if (a < b && c > d) {]]></Text>
      </Positioned>
      <Positioned left="18" top="52" width="364" height="30">
        <Text fontSize="18" fontFamily="DejaVu Sans Mono"
              color="#94A3B8FF">
          <Raw><![CDATA[  前后空格保留  ]]></Raw>
        </Text>
      </Positioned>
      <Positioned left="18" top="88" width="364" height="32">
        <Text fontSize="20" fontFamily="Inter,Noto Sans CJK SC"
              color="#E5E7EBFF">
          <Text>限制条件：</Text>
          <Raw><![CDATA[ ]]></Raw>
          <Text color="#38BDF8FF" fontStyle="BOLD">Stack</Text>
          <Raw><![CDATA[ 与 ]]></Raw>
          <Text color="#F472B6FF" fontStyle="BOLD">Positioned</Text>
        </Text>
      </Positioned>
      <Positioned left="18" top="140" width="170" height="66">
        <Container color="#FF000080" borderRadius="10"
                   border="1 SOLID #FFFFFF66" />
      </Positioned>
      <Positioned left="212" top="140" width="170" height="66">
        <Container color="#80FF0000" borderRadius="10"
                   border="1 SOLID #FFFFFF66" />
      </Positioned>
      <Positioned left="18" top="206" width="170" height="24">
        <Text fontSize="16" fontFamily="DejaVu Sans Mono"
              color="#FCA5A5FF" text="#FF000080" textAlign="CENTER" />
      </Positioned>
      <Positioned left="212" top="206" width="170" height="24">
        <Text fontSize="16" fontFamily="DejaVu Sans Mono"
              color="#FCA5A5FF" text="#80FF0000" textAlign="CENTER" />
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
"""

# No backing panels: the page version uses exactly the example's own colours and
# boxes, so it is a true scale-up rather than a decorated redraw.  The inline
# rich-text run is re-laid-out by the page (each span is its own Text), so glyph
# x-positions inside that one line differ by a few px from the service's own
# inline layout; everything else lines up.
EX3_ART = [
    {"t": "rect", "box": [0, 0, 400, 240], "fill": "#111827FF"},
    {"t": "text", "box": [18, 14, 364, 32], "s": "if (a < b && c > d) {",
     "size": 20, "color": "#E5E7EBFF", "font": "mono"},
    {"t": "text", "box": [18, 50, 364, 32], "s": "  前后空格保留  ", "size": 18,
     "color": "#94A3B8FF", "font": "mono"},
    {"t": "text", "box": [18, 87, 130, 32], "s": "限制条件：", "size": 20,
     "color": "#E5E7EBFF", "font": "ui"},
    {"t": "text", "box": [156, 87, 80, 32], "s": "Stack", "size": 20,
     "color": "#38BDF8FF", "font": "ui"},
    {"t": "text", "box": [236, 87, 34, 32], "s": "与", "size": 20,
     "color": "#E5E7EBFF", "font": "ui"},
    {"t": "text", "box": [272, 87, 120, 32], "s": "Positioned", "size": 20,
     "color": "#F472B6FF", "font": "ui"},
    {"t": "rect", "box": [18, 140, 170, 66], "fill": "#FF000080", "radius": 10,
     "border": "1 SOLID #FFFFFF66"},
    {"t": "rect", "box": [212, 140, 170, 66], "fill": "#80FF0000", "radius": 10,
     "border": "1 SOLID #FFFFFF66"},
    {"t": "text", "box": [18, 205, 170, 24], "s": "#FF000080", "size": 16,
     "color": "#FCA5A5FF", "font": "mono", "align": "CENTER"},
    {"t": "text", "box": [212, 205, 170, 24], "s": "#80FF0000", "size": 16,
     "color": "#FCA5A5FF", "font": "mono", "align": "CENTER"},
]

# ============================================================== example 04
EX4 = """<Snapshot type="png" background="#020617FF">
  <Container width="400" height="240">
    <Stack fit="EXPAND">
      <Container width="400" height="44" color="#1E293BFF" />
      <Positioned left="18" top="11" width="364" height="26">
        <Text fontSize="19" fontFamily="Inter,Noto Sans CJK SC"
              color="#E2E8F0FF" text="两种模糊，作用范围不同" />
      </Positioned>
%s
      <Positioned left="12" top="50" width="176" height="22">
        <Text fontSize="15" fontFamily="DejaVu Sans Mono"
              color="#A78BFAFF" text="BackdropFilter" />
      </Positioned>
      <Positioned left="212" top="50" width="176" height="22">
        <Text fontSize="15" fontFamily="DejaVu Sans Mono"
              color="#67E8F9FF" text="ImageFiltered" />
      </Positioned>
      <Positioned left="12" top="76" width="176" height="120">
        <ClipRRect borderRadius="14" clipBehavior="ANTI_ALIAS">
          <Container width="176" height="120">
            <Stack fit="EXPAND">
              <Positioned left="0" top="0" width="176" height="120">
                <BackdropFilter sigmaX="7" sigmaY="7">
                  <Container width="176" height="120" color="#0F172AB8" />
                </BackdropFilter>
              </Positioned>
              <Positioned left="14" top="46" width="148" height="30">
                <Text fontSize="18" fontFamily="Inter,Noto Sans CJK SC"
                      color="#FFFFFFFF" text="文字清晰" />
              </Positioned>
            </Stack>
          </Container>
        </ClipRRect>
      </Positioned>
      <Positioned left="212" top="76" width="176" height="120">
        <ClipRRect borderRadius="14" clipBehavior="ANTI_ALIAS">
          <Container width="176" height="120">
            <Stack fit="EXPAND">
              <Positioned left="0" top="0" width="176" height="120">
                <ImageFiltered sigmaX="7" sigmaY="7">
                  <Container width="176" height="120">
                    <Stack fit="EXPAND">
                      <Positioned left="0" top="0" width="176" height="120">
                        <Container color="#0F172AB8" />
                      </Positioned>
                      <Positioned left="14" top="44" width="152" height="30">
                        <Text fontSize="18" fontFamily="Inter,Noto Sans CJK SC"
                              color="#FFFFFFFF" text="文字一起糊" />
                      </Positioned>
                    </Stack>
                  </Container>
                </ImageFiltered>
              </Positioned>
            </Stack>
          </Container>
        </ClipRRect>
      </Positioned>
      <Positioned left="12" top="202" width="376" height="30">
        <Container color="#0F172AE6" borderRadius="8"
                   border="1 SOLID #334155FF" />
      </Positioned>
      <Positioned left="24" top="207" width="352" height="24">
        <Text fontSize="16" fontFamily="Inter,Noto Sans CJK SC"
              color="#CBD5E1FF" text="交付：同名 .snapshot + 逐张看图" />
      </Positioned>
    </Stack>
  </Container>
</Snapshot>
""" % _BAR_DSL

# Page version of the same scene: the busy bar field is redrawn as rects, the
# left tile uses a real <BackdropFilter>, the right tile a real
# <ImageFiltered>, so the illustration is the phenomenon, not a picture of it.
EX4_ART = [
    {"t": "rect", "box": [0, 0, 400, 240], "fill": "#020617FF"},
    {"t": "rect", "box": [0, 0, 400, 44], "fill": "#1E293BFF"},
    {"t": "text", "box": [18, 10, 364, 26], "s": "两种模糊，作用范围不同",
     "size": 19, "color": "#E2E8F0FF", "font": "ui"},
] + [{"t": "rect", "box": [12 + i * 48, 76, 44, 120], "fill": c}
     for i, c in enumerate(BAR_COLS)] + [
    {"t": "text", "box": [12, 49, 176, 22], "s": "BackdropFilter", "size": 15,
     "color": "#A78BFAFF", "font": "mono"},
    {"t": "text", "box": [212, 49, 176, 22], "s": "ImageFiltered", "size": 15,
     "color": "#67E8F9FF", "font": "mono"},
    {"t": "blur_backdrop", "box": [12, 76, 176, 120], "radius": 14, "sigma": 7,
     "tint": "#0F172AB8"},
    {"t": "text", "box": [26, 122, 148, 30], "s": "文字清晰", "size": 18,
     "color": "#FFFFFFFF", "font": "ui"},
    {"t": "blur_subtree", "box": [212, 76, 176, 120], "radius": 14, "sigma": 7,
     "plate": "#0F172AB8", "inset": [14, 44, 152, 30], "s": "文字一起糊",
     "size": 18, "color": "#FFFFFFFF", "font": "ui"},
    {"t": "rect", "box": [12, 202, 376, 30], "fill": "#0F172AE6", "radius": 8,
     "border": "1 SOLID #334155FF"},
    {"t": "text", "box": [24, 206, 352, 24], "s": "交付：同名 .snapshot + 逐张看图",
     "size": 16, "color": "#CBD5E1FF", "font": "ui"},
]

EXAMPLES = [
    {"n": 1, "page": 1, "w": 400, "h": 240, "bg": "#0B1220FF",
     "title": "调用契约：请求、响应、错误",
     "purpose": "一次成功渲染与一次失败响应的并排对照",
     "dsl": EX1, "art": EX1_ART, "windows": [(1, 8), (38, 43)]},
    {"n": 2, "page": 2, "w": 400, "h": 240, "bg": "#F8FAFCFF",
     "title": "根尺寸来自布局：Row 与 Stack 对照",
     "purpose": "左：有限主轴下的 Row + Expanded；右：Stack + Positioned",
     "dsl": EX2, "art": EX2_ART, "windows": [(4, 13), (37, 41)]},
    {"n": 3, "page": 3, "w": 400, "h": 240, "bg": "#111827FF",
     "title": "文本三坑与尾部 alpha",
     "purpose": "CDATA 尖括号、Raw 空白、行内富文本、八位色尾部透明度",
     "dsl": EX3, "art": EX3_ART, "windows": [(1, 10), (24, 27)]},
    {"n": 4, "page": 4, "w": 400, "h": 240, "bg": "#020617FF",
     "title": "滤镜作用范围与交付自检",
     "purpose": "BackdropFilter 只糊背景，ImageFiltered 连文字一起糊",
     "dsl": EX4, "art": EX4_ART, "windows": [(45, 52), (62, 68)]},
]


def check():
    for e in EXAMPLES:
        lines = e["dsl"].rstrip("\n").split("\n")
        worst = max(lines, key=len)
        n_code = 0
        for a, b in e["windows"]:
            n_code += b - a + 1
        print("example-%02d lines=%-3d longest=%-3d %s | printed=%d in %s"
              % (e["n"], len(lines), len(worst), worst.strip()[:44], n_code,
                 e["windows"]))
        assert len(worst) <= MAX_COLS, "example-%02d line too long: %r" % (e["n"], worst)
        assert 8 <= n_code <= 18, "example-%02d prints %d code lines" % (e["n"], n_code)


if __name__ == "__main__":
    check()