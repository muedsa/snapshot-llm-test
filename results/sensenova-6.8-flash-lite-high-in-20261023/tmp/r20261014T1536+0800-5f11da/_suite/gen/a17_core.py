"""A17 共享构件：4 个核心示例子树、印刷片段、印刷代码块与外层包装构造器。

设计要点（全部来自实际文档阅读 + A17 六次语法探针实测）：
  * 核心示例子树 CORE1..CORE4 的根元素缩进为 0，便于与印刷片段逐字对齐；
  * 独立示例 = Snapshot 根 + 400x240 有界容器 + 核心子树；
  * 教学页     = 424x264 白底外框 + 12px 内缩 + 核心子树（同一字符串，逐字复用）；
  * 印刷代码块与要点列表都用 <Stack> + <Positioned> 逐行显式摆放，不用 Column：
    探针实测 Column 的直接 Row 子节点不会渲染，且会中断其后的兄弟；
  * 代码文本含字面 ]]> 时按「两段 CDATA 拆分」还原（req-a17-probe4-edc082 实测通过）。

A17 探针实测出的硬约束（均已用真实渲染复现）：
  req-a17-handbook-01..04  400 PARSE_ERROR「Tag Container only can have one child」
    -> <Container> 只能有一个子节点，多个元素必须包进 Column 或 Stack。
  req-a17-probe6-5091d8    V1/V2 Column 的直接 Row 子节点不渲染，且其后的兄弟
                           也不出现；V3 把 Row 包在显式尺寸 Container 里则三块齐全；
                           V4 裸 Stack 作 Column 子节点可渲染。
  req-a17-example-04 / probe6 V5  滤镜内的 Container 只有 height 没有 width 时，
    子树滤镜会撑满整块画布；补上显式 width 后恢复正常色块尺寸。
"""
from __future__ import annotations

# ---------------------------------------------------------------- 核心示例子树

# 第 1 页：请求（文本）/ 成功（二进制）/ 失败（JSON）三条分支的对照。
CORE1 = '''<Container width="400" height="240" color="#F8FAFC" padding="(16,14)">
    <Column width="368" height="212" mainAxisAlignment="SPACE_BETWEEN"
            crossAxisAlignment="STRETCH">
        <Container width="368" color="#0F172A" borderRadius="8" padding="(11,14)">
            <Text fontFamily="DejaVu Sans Mono" fontSize="12" color="#7DD3FC"
                  text="POST /snapshot  text/plain; charset=utf-8"/>
        </Container>
        <Container width="368" height="46">
            <Row width="368" height="46" crossAxisAlignment="STRETCH">
                <Expanded><Container width="178" height="46" color="#ECFDF5"
                        borderRadius="8" padding="(6,10)" alignment="CENTER">
                    <Text fontFamily="DejaVu Sans Mono" fontSize="12" color="#047857"
                          text="200 image/png"/></Container></Expanded>
                <SizedBox width="12"/>
                <Expanded><Container width="178" height="46" color="#FEF2F2"
                        borderRadius="8" padding="(6,10)" alignment="CENTER">
                    <Text fontFamily="DejaVu Sans Mono" fontSize="12" color="#B91C1C"
                          text="400 PARSE_ERROR"/></Container></Expanded>
            </Row>
        </Container>
        <Container width="368" color="#F1F5F9" borderRadius="8" padding="(11,14)">
            <Text fontFamily="DejaVu Sans Mono" fontSize="11" color="#334155">
                <![CDATA[{"code":"PARSE_ERROR","message":"..."}]]></Text>
        </Container>
    </Column>
</Container>'''

# 第 2 页：有界容器里的 Row（Expanded 弹性 + 固定宽度）与 Stack（left/top、right/bottom）。
CORE2 = '''<Container width="400" height="240" color="#F8FAFC" padding="(14,12)">
    <Column width="372" height="216" mainAxisAlignment="SPACE_BETWEEN"
            crossAxisAlignment="STRETCH">
        <Text fontFamily="DejaVu Sans Mono" fontSize="10" color="#64748B"
              text="parent constraint 400 x 240, finite"/>
        <Container width="372" height="60">
            <Row width="372" height="60" crossAxisAlignment="STRETCH">
                <Expanded flex="2"><Container width="284" height="60"
                        color="#0EA5E9" borderRadius="8" alignment="CENTER">
                    <Text fontFamily="Inter" fontSize="11" color="#FFFFFF"
                          text="Expanded flex=2"/></Container></Expanded>
                <Container width="88" height="60" color="#F59E0B" borderRadius="8"
                        alignment="CENTER">
                    <Text fontFamily="Inter" fontSize="11" color="#FFFFFF"
                          text="fixed 88"/></Container>
            </Row>
        </Container>
        <Stack width="372" height="62">
            <Container width="372" height="62" color="#E2E8F0" borderRadius="8"/>
            <Positioned left="10" top="10" width="128" height="20">
                <Container width="128" height="20" color="#8B5CF6" borderRadius="6"
                       alignment="CENTER">
                    <Text fontFamily="Inter" fontSize="10" color="#FFFFFF"
                          text="left=10  top=10"/></Container>
            </Positioned>
            <Positioned right="10" bottom="10" width="116" height="20">
                <Container width="116" height="20" color="#EC4899" borderRadius="6"
                       alignment="CENTER">
                    <Text fontFamily="Inter" fontSize="10" color="#FFFFFF"
                          text="right=10 bottom=10"/></Container>
            </Positioned>
        </Stack>
    </Column>
</Container>'''

# 第 3 页：CDATA + 嵌套 Text 富文本、Raw 保空格、8 位尾部 alpha。
CORE3 = '''<Container width="400" height="240" color="#F8FAFC" padding="(14,10)">
    <Column width="372" height="220" mainAxisAlignment="SPACE_BETWEEN"
            crossAxisAlignment="STRETCH">
        <Container color="#0F172A" borderRadius="8" padding="(10,13)">
            <Text fontFamily="DejaVu Sans Mono" fontSize="11" color="#E2E8F0">
                <Text fontFamily="DejaVu Sans Mono" fontSize="10" color="#94A3B8"
                      text="CDATA + span: "/>
                <Text fontFamily="DejaVu Sans Mono" fontSize="11" color="#7DD3FC"
                      ><![CDATA[a < b && b > a]]></Text>
            </Text>
        </Container>
        <Container color="#F1F5F9" borderRadius="8" border="1 SOLID #CBD5E1"
                   padding="(10,13)">
            <Text fontFamily="DejaVu Sans Mono" fontSize="11" color="#334155"
                  decoration="UNDERLINE" decorationColor="#F59E0B">
                <Raw>   keep spaces   </Raw>
            </Text>
        </Container>
        <Container color="#1E293B" borderRadius="8" padding="(8,12)">
            <Row height="50" crossAxisAlignment="CENTER">
                <Expanded><Container height="50" color="#38BDF8" borderRadius="6"
                        alignment="CENTER">
                    <Text fontFamily="DejaVu Sans Mono" fontSize="9" color="#0F172A"
                          text="#38BDF8"/></Container></Expanded>
                <SizedBox width="14"/>
                <Expanded><Container height="50" color="#38BDF880" borderRadius="6"
                        alignment="CENTER">
                    <Text fontFamily="DejaVu Sans Mono" fontSize="9" color="#FFFFFF"
                          text="#38BDF880"/></Container></Expanded>
            </Row>
        </Container>
    </Column>
</Container>'''

# 第 4 页：BackdropFilter 需要背后有已绘制内容，子树滤镜 ImageFiltered / ColorFiltered。
CORE4 = '''<Stack width="400" height="240" fit="EXPAND" clipBehavior="NONE">
    <Container width="400" height="240" color="#F8FAFC" padding="(14,12)">
        <Column width="372" height="216" mainAxisAlignment="SPACE_BETWEEN"
                crossAxisAlignment="STRETCH">
            <Text fontFamily="DejaVu Sans Mono" fontSize="10" color="#64748B"
                  text="backdrop filter needs painted content behind"/>
            <Stack width="372" height="108">
                <Container width="372" height="108" color="#FFFFFF" borderRadius="8"
                           border="1 SOLID #E2E8F0"/>
                <Positioned left="14" top="14" width="344" height="36">
                    <Row width="344" height="36" mainAxisAlignment="SPACE_BETWEEN">
                        <Container width="42" height="36" color="#FB923C"
                                   borderRadius="6"/>
                        <Container width="42" height="36" color="#38BDF8"
                                   borderRadius="6"/>
                        <Container width="42" height="36" color="#10B981"
                                   borderRadius="6"/>
                        <Container width="42" height="36" color="#EC4899"
                                   borderRadius="6"/>
                    </Row>
                </Positioned>
                <Positioned left="14" top="62" width="344" height="18">
                    <Container width="344" height="18" alignment="CENTER">
                        <Text fontFamily="DejaVu Sans Mono" fontSize="11"
                              color="#334155" text="AB CD EF GH IJ KL MN OP QR ST UV"/>
                    </Container>
                </Positioned>
                <Positioned left="104" top="6" width="196" height="96">
                    <ClipRRect borderRadius="12">
                        <BackdropFilter sigmaX="9" sigmaY="9" tileMode="CLAMP">
                            <Container width="196" height="96" color="#FFFFFF66"/>
                        </BackdropFilter>
                    </ClipRRect>
                </Positioned>
            </Stack>
            <Container width="372" height="64">
                <Row width="372" height="64" crossAxisAlignment="STRETCH">
                    <Expanded><ImageFiltered sigmaX="5" sigmaY="5" tileMode="CLAMP">
                        <Container width="128" height="56" color="#38BDF8"
                               borderRadius="8"/></ImageFiltered></Expanded>
                    <SizedBox width="12"/>
                    <Expanded><ColorFiltered color="#7C3AED" blendMode="MULTIPLY">
                        <Container width="128" height="56" color="#38BDF8"
                               borderRadius="8"/></ColorFiltered></Expanded>
                    <SizedBox width="12"/>
                    <Container width="92" height="56" color="#FFFFFF" borderRadius="8"
                           border="1 SOLID #E2E8F0" alignment="CENTER">
                        <Text fontFamily="Inter" fontSize="10" color="#334155"
                              text="sample interior"/></Container>
                </Row>
            </Container>
        </Column>
    </Container>
</Stack>'''

CORES = {1: CORE1, 2: CORE2, 3: CORE3, 4: CORE4}

# 独立 DSL 里核心子树之前的两行（Snapshot 根 + 400x240 有界容器），
# 印刷片段的行号按独立 DSL 文件换算时必须加上这个偏移。
CORE_LINE_OFFSET = 2

PAGES = 4

# 印刷片段：("range", (CORE 内 1-based 起, 止)) 或 ("ellipsis", 省略提示文本)。
# 范围可多段且保持原顺序；省略提示是独立行，不插入实际执行源码。
SEGMENTS = {
    1: [("ellipsis", "…… 省略 Snapshot 根与 400×240 有界容器（example-01.snapshot 第 1–2 行）……"),
        ("range", (1, 13)),
        ("ellipsis", "…… 省略第二个响应的对称写法与闭合标签（example-01.snapshot 第 16–22 行）……"),
        ("range", (21, 23)),
        ("ellipsis", "…… 省略容器与 Snapshot 的闭合标签（example-01.snapshot 第 26–30 行）……")],
    2: [("ellipsis", "…… 省略 Snapshot 根与 400×240 有界容器（example-02.snapshot 第 1–2 行）……"),
        ("range", (1, 8)),
        ("ellipsis", "…… 省略 Expanded 的收尾、fixed 子项与 Row 闭合（example-02.snapshot 第 11–19 行）……"),
        ("range", (18, 25)),
        ("ellipsis", "…… 省略 right/bottom 定位与闭合标签（example-02.snapshot 第 28–38 行）……")],
    3: [("ellipsis", "…… 省略 Snapshot 根、400×240 容器与第一个深色面板的外壳（example-03.snapshot 第 1–6 行）……"),
        ("range", (5, 11)),
        ("ellipsis", "…… 省略 Raw 所在容器的外壳（example-03.snapshot 第 14–17 行）……"),
        ("range", (16, 18)),
        ("ellipsis", "…… 省略不透明的第一个色块 #38BDF8（example-03.snapshot 第 21–26 行）……"),
        ("range", (25, 29)),
        ("ellipsis", "…… 省略 Row、容器与 Snapshot 的闭合标签（example-03.snapshot 第 32–37 行）……")],
    4: [("ellipsis", "…… 省略 Snapshot 根、400×240 容器与纹理层（example-04.snapshot 第 1–29 行）……"),
        ("range", (28, 44)),
        ("ellipsis", "…… 省略取样卡片与闭合标签（example-04.snapshot 第 47–58 行）……")],
}

CODE_FONT = "DejaVu Sans Mono"
CJK_FONT = "Noto Sans CJK SC,Inter"
MARGIN = 48
PAGE_W, PAGE_H = 1200, 1600
CONTENT_W = PAGE_W - 2 * MARGIN

IND_TITLE = 44
IND_SUBTITLE = 25
IND_SECTION = 19
IND_BODY = 24
IND_CODE = 20
IND_KICKER = 20


def core_file_range(core_lo: int, core_hi: int):
    """把核心子树内 1-based 行号换算成独立示例 DSL 文件里的行号。"""
    return core_lo + CORE_LINE_OFFSET, core_hi + CORE_LINE_OFFSET


def seg(page: int, ranges) -> str:
    """从核心子树按 1-based 行号区间（可多段、保序）取出逐字原文。"""
    lines = CORES[page].split("\n")
    out = []
    for lo, hi in ranges:
        assert 1 <= lo <= hi <= len(lines), (lo, hi, len(lines))
        out.append("\n".join(lines[lo - 1:hi]))
    return "\n".join(out)


def printed_ranges(page: int):
    """返回 (核心子树内行号区间列表, 实际印刷行数（不含省略提示行）)。"""
    ranges, n_printed = [], 0
    for kind, val in SEGMENTS[page]:
        if kind == "range":
            ranges.append(val)
            n_printed += val[1] - val[0] + 1
    return ranges, n_printed


def cdata_payload(text: str) -> str:
    """把可能含字面 ]]> 的代码文本拆成多段 CDATA，保证逐字还原。"""
    parts = text.split("]]>")
    out = [parts[0]]
    for p in parts[1:]:
        out.append("]]]]><![CDATA[>")
        out.append(p)
    return "".join(out)


def independent_dsl(page: int) -> str:
    """独立示例：Snapshot 根 + 400x240 有界容器 + 核心子树（核心子树逐字复用）。"""
    return ('<Snapshot type="png" background="#FFFFFF">\n'
            '<Container width="400" height="240">\n%s\n</Container>\n</Snapshot>\n'
            % CORES[page])


def illustration_frame(page: int, left: int, top: int) -> str:
    """教学页外框：424x264 白底圆角外框 + 12px 内缩，核心子树以 1:1 展示。"""
    return ('            <Positioned left="%d" top="%d" width="424" height="264">\n'
            '                <Container width="424" height="264" color="#FFFFFF"\n'
            '                       borderRadius="12" border="1 SOLID #CBD5E1">\n'
            '                    <Container width="400" height="240">\n%s\n'
            '                    </Container>\n'
            '                </Container>\n'
            '            </Positioned>' % (left, top, CORES[page]))
